"""
Weight-rule sensitivity check.

The core finding ("male ~20x more active") was computed under the field-standard
linear weight rule w = sign * count * w_syn. The literature (Pospisil 2024
effectome; Aug 2026 bioRxiv connectome-constrained fitting) says true weights are
NOT linear in synapse count — fitting yields lognormal weights. The male has ~2x
connection density, so under the linear rule it gets ~2x more weight per neuron,
which could drive the activity gap.

This script re-runs the matched LIF model under alternative weight transforms and
reports whether the male/female activity RATIO survives.

Transforms:
  linear    w = sign * count * w_syn            (baseline, current)
  log1p     w = sign * log1p(count) * w_syn     (compresses high-count synapses)
  sqrt      w = sign * sqrt(count) * w_syn      (intermediate compression)
  lognormal w = sign * exp(N(log(count), s)) * w_syn  (stochastic, s=0.5)

Usage:
    python weight_sensitivity.py <name> --transform linear|log1p|sqrt|lognormal \
        [--duration 2000] [--w-syn 0.1] [--seed 0]
"""

import numpy as np
import os
import time
import argparse
import json

from brian2 import (
    NeuronGroup, Synapses, PoissonGroup, SpikeMonitor, Network,
    run, ms, mV, Hz, prefs,
)

prefs.codegen.target = "cython"

NORM = os.path.join(os.path.dirname(__file__), "normalized")
OUT = os.path.join(os.path.dirname(__file__), "runs")
os.makedirs(OUT, exist_ok=True)

V_REST = -65 * mV
V_TH = -50 * mV
V_RESET = -65 * mV
TAU = 10 * ms
REFRACTORY = 2.2 * ms
DRIVE_WEIGHT = 5 * mV


def load_edgelist(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"])


def transform_weight(count, sign, transform, w_syn, seed=0, sigma=0.5):
    """Apply a weight transform. Returns signed weight in mV units."""
    count = count.astype(np.float64)
    if transform == "linear":
        w = count
    elif transform == "log1p":
        w = np.log1p(count)
    elif transform == "sqrt":
        w = np.sqrt(count)
    elif transform == "lognormal":
        rng = np.random.default_rng(seed)
        # lognormal draw centered on log(count), sigma configurable
        w = np.exp(rng.normal(np.log(np.maximum(count, 1.0)), sigma))
    else:
        raise ValueError(f"unknown transform {transform}")
    return (sign * w * w_syn).astype(np.float32)


def build_and_run(name, transform, duration_ms=2000, w_syn=0.1, seed=0, sigma=0.5):
    pre_idx, post_idx, count, sign, n = load_edgelist(name)
    w = transform_weight(count, sign, transform, w_syn, seed, sigma)
    print(f"[{name}/{transform}] neurons={n} edges={len(pre_idx)} "
          f"mean|w|={np.abs(w).mean():.4f} mV", flush=True)

    G = NeuronGroup(
        n,
        "dv/dt = (v_rest - v)/tau : volt (unless refractory)",
        threshold="v > v_th",
        reset="v = v_reset",
        refractory=REFRACTORY,
        method="exact",
        namespace={"v_rest": V_REST, "v_th": V_TH, "v_reset": V_RESET, "tau": TAU},
    )
    G.v = V_REST

    S = Synapses(G, G, "w : 1", on_pre="v_post += w*mV")
    t0 = time.time()
    S.connect(i=pre_idx, j=post_idx)
    S.w = w
    print(f"[{name}/{transform}] connected {len(S)} synapses in {time.time()-t0:.1f}s", flush=True)

    n_drive = int(n * 0.01)
    rng = np.random.default_rng(0)
    drive_ids = rng.choice(n, size=n_drive, replace=False)
    P = PoissonGroup(n_drive, 100 * Hz)
    D = Synapses(P, G, "drive_w : volt", on_pre="v_post += drive_w")
    D.connect(i=np.arange(n_drive), j=drive_ids)
    D.drive_w = DRIVE_WEIGHT

    M = SpikeMonitor(G)
    net = Network(G, S, P, D, M)
    np.random.seed(42)

    t0 = time.time()
    net.run(duration_ms * ms)
    wall = time.time() - t0
    print(f"[{name}/{transform}] ran {duration_ms}ms in {wall:.1f}s", flush=True)

    n_spikes = M.num_spikes
    n_fired = len(np.unique(M.i))
    pct = 100 * n_fired / n
    print(f"[{name}/{transform}] spikes={n_spikes} fired={n_fired}/{n} ({pct:.1f}%)", flush=True)

    out = os.path.join(OUT, f"{name}_{transform}_spikes.npz")
    np.savez_compressed(out, spike_t=M.t / ms, spike_i=M.i,
                        n_neurons=n, duration_ms=duration_ms)
    return {"name": name, "transform": transform, "n_spikes": int(n_spikes),
            "n_fired": int(n_fired), "pct_fired": float(pct), "n_neurons": int(n)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--transform", default="linear")
    ap.add_argument("--duration", type=float, default=2000)
    ap.add_argument("--w-syn", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--sigma", type=float, default=0.5)
    args = ap.parse_args()
    r = build_and_run(args.name, args.transform, args.duration, args.w_syn, args.seed, args.sigma)
    print("RESULT " + json.dumps(r))
