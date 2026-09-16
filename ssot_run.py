"""
SSOT unified runner: one script for every condition, one JSONL output.

Every run appends one JSON line to results/ssot/ssot_results.jsonl with:
  full parameter provenance (source npz, transform, sigma, w_syn, weight_seed,
  sim_seed) + inline metrics (pct_fired, rate stats, branching ratio, CV-ISI,
  participation ratio) + wall time.

Seed semantics (fixes the reviewer's "no uncertainty quantification"):
  --weight-seed  seeds the lognormal weight DRAW (stochastic transform)
  --sim-seed     seeds the DYNAMICS (Poisson drive + network simulation;
                 previously hardcoded np.random.seed(42) everywhere)
Total variance = weight draw + dynamics together.

Usage:
  venv/bin/python ssot_run.py --source mcns_male --tag real_sigma1.6 \
      --transform lognormal --sigma 1.6 --w-syn 0.1 \
      --weight-seed 0 --sim-seed 42 [--save-spikes] [--duration 2000]
"""

import numpy as np
import os
import json
import time
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
NORM = os.path.join(HERE, "normalized")
RUNS = os.path.join(HERE, "runs")
SSOT_DIR = os.path.join(HERE, "results", "ssot")
os.makedirs(RUNS, exist_ok=True)
os.makedirs(SSOT_DIR, exist_ok=True)
SSOT_FILE = os.path.join(SSOT_DIR, "ssot_results.jsonl")

V_REST, V_TH, V_RESET = -65.0, -50.0, -65.0  # mV
TAU_MS, REFRACTORY_MS, DRIVE_WEIGHT_MV = 10.0, 2.2, 5.0

from brian2 import (
    NeuronGroup, Synapses, PoissonGroup, SpikeMonitor, Network,
    run, ms, mV, Hz, prefs, seed as brian2_seed,
)
prefs.codegen.target = "cython"


def load_edgelist(source):
    d = np.load(os.path.join(NORM, f"{source}.npz"))
    return (d["pre_idx"], d["post_idx"], d["weight"], d["sign"],
            int(d["n_neurons"]))


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
        raise ValueError(f"unknown transform {transform}")
    return (sign * w * w_syn).astype(np.float32)


# --- vectorized metrics (import-free, no O(N^2) traps) ----------------------
def branching_and_cv(spike_t, spike_i, duration_ms, bin_ms=1.0):
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(np.int64)
    bins = bins[bins < n_bins]
    act = np.bincount(bins, minlength=n_bins).astype(float)
    a_t, a_t1 = act[:-1], act[1:]
    mask = a_t > 0
    if mask.sum() < 10:
        return np.nan, np.nan
    br = a_t1[mask].mean() / a_t[mask].mean()
    order = np.lexsort((spike_t, spike_i))
    si, st = spike_i[order], spike_t[order]
    new_neuron = np.empty(len(si), dtype=bool)
    new_neuron[0] = True
    new_neuron[1:] = si[1:] != si[:-1]
    isi = np.diff(st)[~new_neuron[1:]]
    cv = isi.std() / isi.mean() if len(isi) >= 10 else np.nan
    return float(br), float(cv)


def participation_ratio(spike_t, spike_i, n_neurons, duration_ms,
                        bin_ms=10.0, max_neurons=5000):
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(np.int64)
    ok = bins < n_bins
    bins, si = bins[ok], spike_i[ok]
    active = np.unique(si)
    if len(active) < 2:
        return np.nan
    if len(active) > max_neurons:
        rng = np.random.default_rng(0)
        active = np.sort(rng.choice(active, size=max_neurons, replace=False))
    idx = np.searchsorted(active, si)
    # searchsorted returns insertion position for missing values, which can be
    # len(active) (out of bounds) for ids above the subsample max — clip first.
    idx = np.minimum(idx, len(active) - 1)
    valid = active[idx] == si
    idx, bins = idx[valid], bins[valid]
    na = len(active)
    flat = idx * n_bins + bins
    R = np.bincount(flat, minlength=na * n_bins).astype(np.float64).reshape(na, n_bins)
    R -= R.mean(axis=1, keepdims=True)
    C = (R @ R.T) / n_bins
    evals = np.linalg.eigvalsh(C)
    evals = evals[evals > 0]
    if len(evals) == 0:
        return np.nan
    return float((evals.sum() ** 2) / (evals ** 2).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="npz base name in normalized/")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--transform", default="linear")
    ap.add_argument("--sigma", type=float, default=0.5)
    ap.add_argument("--w-syn", type=float, default=0.1)
    ap.add_argument("--weight-seed", type=int, default=0)
    ap.add_argument("--sim-seed", type=int, default=42)
    ap.add_argument("--duration", type=float, default=2000)
    ap.add_argument("--save-spikes", action="store_true")
    ap.add_argument("--notes", default="")
    args = ap.parse_args()

    t0 = time.time()
    pre, post, count, sign, n = load_edgelist(args.source)
    w = transform_weight(count, sign, args.transform, args.w_syn,
                         args.weight_seed, args.sigma)
    mean_abs_w = float(np.abs(w).mean())

    G = NeuronGroup(
        n,
        "dv/dt = (v_rest - v)/tau : volt (unless refractory)",
        threshold="v > v_th", reset="v = v_reset",
        refractory=REFRACTORY_MS * ms, method="exact",
        namespace={"v_rest": V_REST * mV, "v_th": V_TH * mV,
                   "v_reset": V_RESET * mV, "tau": TAU_MS * ms},
    )
    G.v = V_REST * mV
    S = Synapses(G, G, "w : 1", on_pre="v_post += w*mV")
    S.connect(i=pre, j=post)
    S.w = w

    n_drive = int(n * 0.01)
    # Drive neuron selection is part of the input realization -> varies with
    # sim_seed (weight_seed governs network construction only).
    drive_ids = np.random.default_rng(args.sim_seed).choice(n, size=n_drive, replace=False)
    P = PoissonGroup(n_drive, 100 * Hz)
    D = Synapses(P, G, "drive_w : volt", on_pre="v_post += drive_w")
    D.connect(i=np.arange(n_drive), j=drive_ids)
    D.drive_w = DRIVE_WEIGHT_MV * mV

    M = SpikeMonitor(G)
    net = Network(G, S, P, D, M)

    # Seed the DYNAMICS. brian2.seed() reseeds the RNG used by rand() in
    # codegen (np.random.seed alone does NOT cover Brian2's internal RNG).
    np.random.seed(args.sim_seed)
    brian2_seed(args.sim_seed)
    net.run(args.duration * ms)
    wall = time.time() - t0

    spike_t = np.asarray(M.t / ms, dtype=np.float64)
    spike_i = np.asarray(M.i, dtype=np.int64)
    n_spikes = len(spike_t)
    fired = np.unique(spike_i)
    pct = 100.0 * len(fired) / n

    br, cv = branching_and_cv(spike_t, spike_i, args.duration)
    pr = participation_ratio(spike_t, spike_i, n, args.duration)
    rate_fired = n_spikes * 1000.0 / args.duration / max(len(fired), 1)   # Hz per firing neuron
    rate_all = n_spikes * 1000.0 / args.duration / n                     # Hz averaged over ALL neurons

    if args.save_spikes:
        np.savez_compressed(
            os.path.join(RUNS, f"ssot_{args.tag}_{args.source}_w{args.weight_seed}s{args.sim_seed}_spikes.npz"),
            spike_t=spike_t.astype(np.float32), spike_i=spike_i.astype(np.int32),
            n_neurons=np.int32(n), duration_ms=np.float64(args.duration))

    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tag": args.tag, "source": args.source,
        "sex": ("male" if args.source.startswith("mcns") else "female"),
        "transform": args.transform, "sigma": args.sigma,
        "w_syn": args.w_syn, "weight_seed": args.weight_seed,
        "sim_seed": args.sim_seed, "duration_ms": args.duration,
        "drive_frac": 0.01, "drive_rate_Hz": 100, "drive_weight_mV": DRIVE_WEIGHT_MV,
        "n_neurons": n, "n_edges": int(len(pre)),
        "mean_abs_w_mV": mean_abs_w,
        "pct_fired": round(float(pct), 3),
        "n_spikes": int(n_spikes),
        "rate_fired_Hz": round(float(rate_fired), 3),
        "rate_all_Hz": round(float(rate_all), 4),
        "branching_ratio": None if np.isnan(br) else round(br, 4),
        "cv_isi": None if np.isnan(cv) else round(cv, 3),
        "participation_ratio": None if np.isnan(pr) else round(pr, 2),
        "wall_s": round(wall, 1),
        "notes": args.notes,
    }
    with open(SSOT_FILE, "a") as f:
        f.write(json.dumps(rec) + "\n")
    print("RESULT " + json.dumps(rec))


if __name__ == "__main__":
    main()