"""
Robustness check: multi-seed rewiring + w_syn sweep.

Answers two reviewer questions:
  1. Is the male/female activity gap robust across the critical regime (w_syn sweep)?
  2. Is the rewired-null collapse robust across rewiring seeds (not a lucky permutation)?

Outputs a CSV summary to results/robustness.csv.

Usage:
    python robustness.py
"""

import numpy as np
import os
import subprocess
import sys
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(HERE, "venv", "bin", "python")
NORM = os.path.join(HERE, "normalized")
OUT = os.path.join(HERE, "runs")
os.makedirs(OUT, exist_ok=True)

W_SYN_SWEEP = [0.05, 0.1, 0.2]
SEEDS = [0, 1, 2, 3, 4]
DURATION = 2000


def run_model(name, w_syn, duration=DURATION):
    """Run model.py and parse the summary line."""
    r = subprocess.run(
        [PY, "model.py", name, "--duration", str(duration), "--w-syn", str(w_syn)],
        capture_output=True, text=True, cwd=HERE,
    )
    out = r.stdout + r.stderr
    # parse "spikes=... neurons_fired=.../... (...%)"
    fired_pct = None
    mean_rate = None
    for line in out.splitlines():
        if "neurons_fired=" in line:
            # e.g. "spikes=36402 neurons_fired=4119/169078 (2.4%)"
            pct = line.split("(")[1].split("%")[0]
            fired_pct = float(pct)
        if "mean rate=" in line:
            mean_rate = float(line.split("mean rate=")[1].split(" Hz")[0])
    return fired_pct, mean_rate


def main():
    rows = []
    header = ["network", "w_syn", "seed", "fired_pct", "mean_rate"]

    # w_syn sweep on real networks
    for name in ["banc_female", "mcns_male"]:
        for w_syn in W_SYN_SWEEP:
            pct, rate = run_model(name, w_syn)
            rows.append([name, w_syn, "real", pct, rate])
            print(f"{name} w_syn={w_syn}: {pct}% fire, {rate} Hz", flush=True)

    # multi-seed rewiring
    for name in ["banc_female", "mcns_male"]:
        d = np.load(os.path.join(NORM, f"{name}.npz"))
        pre, post, weight, sign, n = (d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"]))
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            perm = rng.permutation(len(post))
            post_r = post[perm]
            tmp = f"{name}_rewired_s{seed}"
            np.savez_compressed(
                os.path.join(NORM, f"{tmp}.npz"),
                pre_idx=pre.astype(np.int32), post_idx=post_r.astype(np.int32),
                weight=weight.astype(np.float32), sign=sign.astype(np.int8),
                n_neurons=np.int32(n),
            )
            pct, rate = run_model(tmp, 0.1)
            rows.append([name, 0.1, f"rewired_s{seed}", pct, rate])
            print(f"{name} rewired seed={seed}: {pct}% fire, {rate} Hz", flush=True)
            os.remove(os.path.join(NORM, f"{tmp}.npz"))

    with open(os.path.join(HERE, "results", "robustness.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("saved results/robustness.csv")


if __name__ == "__main__":
    main()
