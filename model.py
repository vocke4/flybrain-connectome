"""
Matched LIF whole-brain model builder (Brian2).

Voltage-injection synapse (fast, memory-light), signed weight = sign * count * w_syn.
Identical parameters for both sexes so any dynamical difference is attributable
to wiring, not model choice.

Tuned regime (w_syn=0.1): subcritical-to-critical, ~3% neurons fire, mean ~3.6 Hz,
with genuine recurrent propagation. This is the comparable regime for the
male-vs-female comparison.

Usage:
    python model.py <name> [--duration 1000] [--drive-frac 0.01] [--drive-rate 100] [--w-syn 0.1]
"""

import numpy as np
import os
import time
import argparse

from brian2 import (
    NeuronGroup, Synapses, PoissonGroup, SpikeMonitor, Network,
    run, ms, mV, Hz, prefs,
)

prefs.codegen.target = "cython"

NORM = os.path.join(os.path.dirname(__file__), "normalized")
OUT = os.path.join(os.path.dirname(__file__), "runs")
os.makedirs(OUT, exist_ok=True)

# Matched LIF parameters (identical across sexes)
V_REST = -65 * mV
V_TH = -50 * mV
V_RESET = -65 * mV
TAU = 10 * ms
REFRACTORY = 2.2 * ms
DRIVE_WEIGHT = 5 * mV  # per Poisson spike


def load_edgelist(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"])


def build_and_run(name, duration_ms=1000, drive_frac=0.01, drive_rate=100.0, w_syn=0.1):
    pre_idx, post_idx, count, sign, n = load_edgelist(name)
    print(f"[{name}] neurons={n} edges={len(pre_idx)}")

    w = (sign * count * w_syn).astype(np.float32)
    print(f"[{name}] w range=[{w.min():.2f},{w.max():.2f}] mV, mean|w|={np.abs(w).mean():.3f}")

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
    print(f"[{name}] connected {len(S)} synapses in {time.time()-t0:.1f}s")

    n_drive = int(n * drive_frac)
    rng = np.random.default_rng(0)
    drive_ids = rng.choice(n, size=n_drive, replace=False)
    P = PoissonGroup(n_drive, drive_rate * Hz)
    D = Synapses(P, G, "drive_w : volt", on_pre="v_post += drive_w")
    D.connect(i=np.arange(n_drive), j=drive_ids)
    D.drive_w = DRIVE_WEIGHT

    M = SpikeMonitor(G)
    net = Network(G, S, P, D, M)

    # Seed numpy for reproducible Poisson spiking
    np.random.seed(42)

    t0 = time.time()
    net.run(duration_ms * ms)
    wall = time.time() - t0
    print(f"[{name}] ran {duration_ms}ms in {wall:.1f}s wall ({duration_ms/wall:.0f}x realtime)")

    n_spikes = M.num_spikes
    n_fired = len(np.unique(M.i))
    print(f"[{name}] spikes={n_spikes} neurons_fired={n_fired}/{n} ({100*n_fired/n:.1f}%)")

    if n_spikes > 0:
        from collections import Counter
        c = Counter(M.i)
        rates = np.array(list(c.values()))
        print(f"[{name}] mean rate={rates.mean():.2f} Hz, max={rates.max()}, "
              f"median={np.median(rates)}, >1spike={(rates>1).sum()}")

    np.savez_compressed(
        os.path.join(OUT, f"{name}_spikes.npz"),
        spike_t=M.t / ms,
        spike_i=M.i,
        n_neurons=n,
        duration_ms=duration_ms,
    )
    return n_spikes, n_fired


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--duration", type=float, default=1000)
    ap.add_argument("--drive-frac", type=float, default=0.01)
    ap.add_argument("--drive-rate", type=float, default=100.0)
    ap.add_argument("--w-syn", type=float, default=0.1)
    args = ap.parse_args()
    build_and_run(args.name, args.duration, args.drive_frac, args.drive_rate, args.w_syn)
