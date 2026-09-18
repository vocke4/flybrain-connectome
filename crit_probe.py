#!/usr/bin/env python3
"""Experiment A: a QUIESCENCE-REFERENCED criticality test for the flybrain runs.

The Sept-11 "criticality" metric (mean(A[t+1]|A[t]>0)/mean(A[t]|A[t]>0) at 1 ms)
is degenerate on a continuously-driven network: bins are essentially never empty,
so the estimator returns ~1 by construction (see README_CRITICALITY_AUDIT.md).

This script fixes the *protocol*, not the arithmetic:
  * low total drive-event rate -> real quiescent bins and true avalanches
  * avalanche size/duration distributions with a Clauset-style discrete power-law
    MLE + KS goodness-of-fit, and the classic critical exponents
  * the SAME runs are also scored with the old estimator, so the two can be
    compared directly on identical spike trains

Run real, DES-rewired and sign-shuffled networks at matched drive on a w_syn
ladder. If real networks are near a critical point they should show power-law
avalanche statistics at some w; if the estimator is a tautology, real and nulls
will look the same at every w.

Usage:
  venv/bin/python crit_probe.py \
      --source banc_female --tag A_banc_female_w0.10 \
      --transform linear --w-syn 0.10 --drive-frac 0.001 --drive-rate 1.0 \
      --weight-seed 0 --sim-seed 42 --duration 120000 --save-spikes
"""
import argparse
import json
import os
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
NORM = os.path.join(HERE, "normalized")
RUNS = os.path.join(HERE, "runs")
OUT_DIR = os.path.join(HERE, "results", "crit_probe")
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(RUNS, exist_ok=True)

V_REST, V_TH, V_RESET = -65.0, -50.0, -65.0
TAU_MS, REFRACTORY_MS = 10.0, 2.2

from brian2 import (NeuronGroup, Synapses, PoissonGroup, SpikeMonitor, Network,
                    run, ms, mV, Hz, prefs, seed as brian2_seed)
prefs.codegen.target = "cython"


def load_edgelist(source):
    d = np.load(os.path.join(NORM, f"{source}.npz"))
    return (d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"]))


def transform_weight(count, sign, transform, w_syn, weight_seed, sigma):
    count = count.astype(np.float64)
    if transform == "linear":
        w = count
    elif transform == "log1p":
        w = np.log1p(count)
    elif transform == "sqrt":
        w = np.sqrt(count)
    elif transform == "lognormal":
        rng = np.random.default_rng(weight_seed)
        w = np.exp(rng.normal(np.log(np.maximum(count, 1.0)), sigma))
    else:
        raise ValueError(transform)
    return (sign * w * w_syn).astype(np.float32)


# ---------------------------------------------------------------- estimators
def old_branching(spike_t, duration_ms, bin_ms=1.0):
    """The Sept-11 estimator, verbatim."""
    n_bins = int(duration_ms / bin_ms)
    b = np.floor(spike_t / bin_ms).astype(np.int64)
    b = b[b < n_bins]
    act = np.bincount(b, minlength=n_bins).astype(float)
    a_t, a_t1 = act[:-1], act[1:]
    m = a_t > 0
    if m.sum() < 10:
        return np.nan, act
    return float(a_t1[m].mean() / a_t[m].mean()), act


def avalanche_stats(act):
    """Avalanches = maximal runs of non-empty bins (separated by empty bins)."""
    active = act > 0
    idx = np.flatnonzero(active)
    if len(idx) == 0:
        return dict(n_avalanches=0, sizes=np.array([]), durations=np.array([]))
    breaks = np.flatnonzero(np.diff(idx) > 1)
    starts = np.concatenate(([0], breaks + 1))
    ends = np.concatenate((breaks, [len(idx) - 1]))
    counts_at_active = act[idx]
    # note: reduceat sums between consecutive start positions
    sizes = np.add.reduceat(counts_at_active, starts)
    # subtract everything after each avalanche's end is handled by construction:
    # reduceat sums from starts[k] to starts[k+1]-1, which is exactly the run.
    durations = (ends - starts + 1).astype(int)
    return dict(n_avalanches=len(sizes), sizes=sizes.astype(float),
                durations=durations)


def pl_fit_discrete(sizes, xmin=None):
    """Clauset-style discrete power-law MLE + KS distance.

    Returns (alpha, xmin, n_tail, ks). If xmin is None, scan candidates and
    keep the one minimising KS (standard recipe, restricted to xmin>=2).
    """
    sizes = np.asarray(sizes, dtype=float)
    sizes = sizes[sizes >= 2]
    if len(sizes) < 50:
        return None
    cands = np.unique(np.floor(np.logspace(np.log10(2), np.log10(sizes.max() or 2), 15)).astype(int))
    cands = cands[cands >= 2]
    best = None
    for xm in cands:
        tail = sizes[sizes >= xm]
        if len(tail) < 50:
            continue
        alpha = 1.0 + len(tail) / np.sum(np.log(tail / (xm - 0.5)))
        if not np.isfinite(alpha) or alpha <= 1:
            continue
        # KS distance against the fitted CDF
        ts = np.sort(tail)
        cdf_emp = np.arange(1, len(ts) + 1) / len(ts)
        # discrete power-law CDF via zeta-normalised survival approximation
        xs = np.arange(xm, ts.max() + 1)
        pmf = xs.astype(float) ** (-alpha)
        pmf /= pmf.sum()
        cdf_fit = np.cumsum(pmf)
        idxs = np.clip((ts - xm).astype(np.int64), 0, len(cdf_fit) - 1)
        cdf_at = cdf_fit[idxs]
        ks = np.abs(cdf_emp - cdf_at).max()
        if best is None or ks < best[3]:
            best = (alpha, xm, len(tail), ks)
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--transform", default="linear")
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--w-syn", type=float, default=0.1)
    ap.add_argument("--drive-frac", type=float, default=0.001)
    ap.add_argument("--drive-rate", type=float, default=1.0)
    ap.add_argument("--drive-weight", type=float, default=5.0)
    ap.add_argument("--weight-seed", type=int, default=0)
    ap.add_argument("--sim-seed", type=int, default=42)
    ap.add_argument("--duration", type=float, default=120000)
    ap.add_argument("--bin-ms", type=float, default=1.0)
    ap.add_argument("--save-spikes", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    pre, post, count, sign, n = load_edgelist(args.source)
    w = transform_weight(count, sign, args.transform, args.w_syn,
                         args.weight_seed, args.sigma)

    G = NeuronGroup(
        n, "dv/dt = (v_rest - v)/tau : volt (unless refractory)",
        threshold="v > v_th", reset="v = v_reset",
        refractory=REFRACTORY_MS * ms, method="exact",
        namespace={"v_rest": V_REST * mV, "v_th": V_TH * mV,
                   "v_reset": V_RESET * mV, "tau": TAU_MS * ms})
    G.v = V_REST * mV
    S = Synapses(G, G, "w : 1", on_pre="v_post += w*mV")
    S.connect(i=pre, j=post)
    S.w = w

    n_drive = max(1, int(round(n * args.drive_frac)))
    drive_ids = np.random.default_rng(args.sim_seed).choice(n, size=n_drive, replace=False)
    P = PoissonGroup(n_drive, args.drive_rate * Hz)
    D = Synapses(P, G, "drive_w : volt", on_pre="v_post += drive_w")
    D.connect(i=np.arange(n_drive), j=drive_ids)
    D.drive_w = args.drive_weight * mV

    net = Network(G, S, P, D)
    np.random.seed(args.sim_seed)
    brian2_seed(args.sim_seed)

    # settle for 10% of duration (transient), then attach the monitor and record
    transient = min(0.1 * args.duration, 20000.0)
    if transient > 0:
        net.run(transient * ms)
    M2 = SpikeMonitor(G)
    net.add(M2)
    net.run((args.duration - transient) * ms)
    rec_dur = args.duration - transient
    wall = time.time() - t0

    spike_t = np.asarray(M2.t / ms, dtype=np.float64)
    spike_i = np.asarray(M2.i, dtype=np.int64)
    n_spikes = len(spike_t)

    old_br, act = old_branching(spike_t, rec_dur, args.bin_ms)
    n_bins = len(act)
    zero_bins = int((act == 0).sum())
    av = avalanche_stats(act)
    fit_size = pl_fit_discrete(av["sizes"])
    fit_dur = pl_fit_discrete(av["durations"])

    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tag": args.tag, "source": args.source,
        "sex": ("male" if args.source.startswith("mcns") else "female"),
        "transform": args.transform, "sigma": args.sigma,
        "w_syn": args.w_syn, "weight_seed": args.weight_seed,
        "sim_seed": args.sim_seed, "duration_ms": rec_dur,
        "drive_frac": args.drive_frac, "drive_rate_Hz": args.drive_rate,
        "n_drive": n_drive, "drive_weight_mV": args.drive_weight,
        "total_drive_events_per_s": n_drive * args.drive_rate,
        "n_neurons": n, "n_edges": int(len(pre)),
        "pct_fired": round(100.0 * len(np.unique(spike_i)) / n, 3),
        "n_spikes": int(n_spikes),
        "rate_all_Hz": round(n_spikes * 1000.0 / rec_dur / n, 5),
        "zero_bins": zero_bins, "n_bins": n_bins,
        "zero_frac": round(zero_bins / n_bins, 4),
        "old_branching_ratio": None if np.isnan(old_br) else round(old_br, 5),
        "n_avalanches": int(av["n_avalanches"]),
        "max_avalanche_size": (int(av["sizes"].max()) if av["n_avalanches"] else 0),
        "mean_avalanche_size": (round(float(av["sizes"].mean()), 2) if av["n_avalanches"] else 0),
        "alpha_size": (float(round(fit_size[0], 3)) if fit_size else None),
        "xmin_size": (int(fit_size[1]) if fit_size else None),
        "n_tail_size": (int(fit_size[2]) if fit_size else None),
        "ks_size": (float(round(fit_size[3], 4)) if fit_size else None),
        "alpha_duration": (float(round(fit_dur[0], 3)) if fit_dur else None),
        "ks_duration": (float(round(fit_dur[3], 4)) if fit_dur else None),
        "wall_s": round(wall, 1),
    }

    if args.save_spikes:
        np.savez_compressed(
            os.path.join(RUNS, f"crit_{args.tag}_spikes.npz"),
            spike_t=spike_t.astype(np.float32), spike_i=spike_i.astype(np.int32),
            n_neurons=np.int32(n), duration_ms=np.float64(rec_dur))

    with open(os.path.join(OUT_DIR, "crit_probe_results.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("RESULT " + json.dumps(rec))


if __name__ == "__main__":
    main()
