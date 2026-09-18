"""
Generate lane scripts (queue_female.sh / queue_male.sh) for the SSOT re-run.

Every job = one ssot_run.py invocation, appended to results/ssot/ssot_results.jsonl.
Seeds: (weight_seed, sim_seed) paired as (0,42),(1,43),(2,44) for stochastic
transforms; deterministic transforms use weight_seed=0 with 3 sim seeds.

Job groups (PRD mapping):
  anchor_ln_s1.6  — headline σ=1.6 multi-seed        (PRD: Verify Headline Data)
  anchor_linear   — linear w0.1 multi-seed           (SSOT baseline)
  ctrl_abl        — size-matched random ablation     (PRD: Upgrade Silencing)
  ctrl_nodimorph  — dimorphic silencing, multi-seed  (same)
  ctrl_signshuffle— missing sign-shuffle control     (PRD: Report Missing Control)
  anchor_ln_s0.5  — reconciles 6.6x vs 6.9x          (SSOT)
  mm_ln_*         — mean-weight-matched σ sweep      (PRD: Isolate Variance)
  mm_log1p/mm_sqrt— drive-normalized floor rules     (PRD: Normalize Drive)
  crit_w*         — criticality-matching coarse sweep(PRD: Match Criticality)
  des_s*          — double-edge-swap null at σ=1.6   (PRD: Fix Null Model)
"""

import numpy as np
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NORM = os.path.join(HERE, "normalized")
OUT = os.path.join(HERE, "results", "ssot")
os.makedirs(OUT, exist_ok=True)

PY = os.path.join(HERE, "venv", "bin", "python")
SEEDS = [(0, 42), (1, 43), (2, 44)]


def load(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["weight"].astype(np.float64), int(d["n_neurons"])


def mean_matched_wsyn(count, transform, base=0.1):
    t = {"log1p": np.log1p(count), "sqrt": np.sqrt(count)}[transform]
    return base * count.mean() / t.mean()


def jobs_for(source, sex, des_prefix):
    count, n = load(source)
    J = []

    def add(tag, src, transform, w_syn, wseed, simseed, sigma=0.5):
        J.append(f"{PY} ssot_run.py --source {src} --tag {tag} "
                 f"--transform {transform} --sigma {sigma} --w-syn {w_syn} "
                 f"--weight-seed {wseed} --sim-seed {simseed} --duration 2000")

    # 1. Headline anchor: lognormal sigma=1.6 at w_syn=0.1
    for ws, ss in SEEDS:
        add("anchor_ln_s1.6_w0.1", source, "lognormal", 0.1, ws, ss, sigma=1.6)
    # 2. Linear anchor
    for _, ss in SEEDS:
        add("anchor_linear_w0.1", source, "linear", 0.1, 0, ss)
    # 3. Random ablation nulls (k = dimorphic count; male 3900, female 3803)
    k = 3900 if sex == "male" else 3803
    for s in range(5):
        add(f"ctrl_abl{k}_s{s}", f"{source}_abl{s}", "linear", 0.1, 0, 42)
    # 4. Dimorphic silencing, multi-seed
    for _, ss in SEEDS:
        add("ctrl_nodimorph", f"{source}_nodimorph", "linear", 0.1, 0, ss)
    # 5. Sign-shuffle control
    for _, ss in SEEDS:
        add("ctrl_signshuffle", f"{source}_signshuffled", "linear", 0.1, 0, ss)
    # 6. sigma=0.5 anchor (reconciles 6.6x vs 6.9x)
    for ws, ss in SEEDS:
        add("anchor_ln_s0.5_w0.1", source, "lognormal", 0.1, ws, ss, sigma=0.5)
    # 7. Mean-weight-matched lognormal sweep (holds E[w] fixed)
    for sigma in (0.5, 1.0, 1.6):
        w = 0.1 * float(np.exp(-sigma * sigma / 2.0))
        for ws, ss in SEEDS:
            add(f"mm_ln_s{sigma}", source, "lognormal", round(w, 5), ws, ss, sigma=sigma)
    # 8. Drive-normalized log1p / sqrt (fixes floor-effect comparison)
    for tr in ("log1p", "sqrt"):
        w = mean_matched_wsyn(count, tr)
        for _, ss in SEEDS:
            add(f"mm_{tr}", source, tr, round(w, 5), 0, ss)
    # 9. Criticality-matching coarse sweep at sigma=1.6 (seed 0)
    grid = {"female": [0.02, 0.04, 0.06, 0.15], "male": [0.01, 0.02, 0.03, 0.05]}[sex]
    for w in grid:
        add(f"crit_w{w}", source, "lognormal", w, 0, 42, sigma=1.6)
    # 10. Double-edge-swap null at headline sigma=1.6 (wait for DES build)
    J.append("i=0; while [ ! -f normalized/" + des_prefix + "_des_2.npz ] && [ $i -lt 75 ]"
             "; do sleep 60; i=$((i+1)); done")
    for s in range(3):
        add(f"des_s{s}_ln_s1.6", f"{des_prefix}_des_{s}", "lognormal", 0.1, s, 42, sigma=1.6)
    return J


def write_lane(sex, source, des_prefix):
    lines = ["#!/bin/bash",
             f"cd {HERE}",
             f"echo '=== lane {sex} start '$(date)' ===' >> results/ssot/lane_{sex}.log"]
    for j in jobs_for(source, sex, des_prefix):
        lines.append(f"echo '[{sex}] '$(date '+%H:%M:%S')' START ' $(echo {j} | "
                     f"grep -o 'tag [a-z0-9._]*') >> results/ssot/lane_{sex}.log")
        lines.append(j + " >> results/ssot/lane_{sex}.log 2>&1 || echo 'JOB FAILED' "
                     ">> results/ssot/lane_{sex}.log".replace("{sex}", sex))
        lines.append(f"echo '[{sex}] '$(date '+%H:%M:%S')' END' >> results/ssot/lane_{sex}.log")
    lines.append(f"echo '=== lane {sex} done '$(date)' ===' >> results/ssot/lane_{sex}.log")
    path = os.path.join(HERE, f"queue_{sex}.sh")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    os.chmod(path, 0o755)
    n_jobs = sum(1 for l in lines if "ssot_run.py" in l)
    print(f"{path}: {n_jobs} jobs")


if __name__ == "__main__":
    write_lane("female", "banc_female", "banc_female")
    write_lane("male", "mcns_male", "mcns_male")