#!/usr/bin/env python3
"""PHASE 0 driver — settle the load-bearing numbers before any text edits.

Adds new seed-pairs / anchors to the canonical ledger (append-only, per §2.6).
Idempotent: skips any (tag, source, weight_seed, sim_seed) already present.

Stage A  sigma=1.83 anchor           6 runs  — resolves the 1.6x-vs-1.75x citation split
Stage B  DES nulls 3 build x 3 sim  18 runs  — makes the seed-pair claim TRUE
Stage C  ablation nulls 5 x 3 sim   30 runs  — fixes the "<=0.21pp" error with real SDs
Stage D  equivalence pairs 3-seed    8 runs  — 2.5x -> 3.0x with error bars
                                      ----
                                      62 runs
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE  # script lives at the package/repo root
LEDGER = os.path.join(REPO, "results", "ssot", "ssot_results.jsonl")
PY = os.environ.get("PYTHON", os.path.join(REPO, "venv", "bin", "python"))
LOG = os.path.join(HERE, "phase0_runs.log")


def existing_keys():
    keys = set()
    if os.path.exists(LEDGER):
        for line in open(LEDGER):
            if line.strip():
                r = json.loads(line)
                keys.add((r["tag"], r["source"], r["weight_seed"], r["sim_seed"]))
    return keys


def job(tag, source, transform, sigma, w_syn, ws, ss):
    return dict(tag=tag, source=source, transform=transform, sigma=sigma,
                w_syn=w_syn, weight_seed=ws, sim_seed=ss)


def build_plan():
    plan = []
    # A: sigma = 1.83 anchor, 2 sexes x 3 pairs
    for src in ("banc_female", "mcns_male"):
        for ws, ss in ((0, 42), (1, 43), (2, 44)):
            plan.append(job("anchor_ln_s1.83_w0.1", src, "lognormal", 1.83, 0.1, ws, ss))
    # B: DES 3 build seeds x 3 sim seeds
    for k in (0, 1, 2):
        for src in (f"banc_female_des_{k}", f"mcns_male_des_{k}"):
            for ss in (42, 43, 44):
                plan.append(job(f"des_s{k}_ln_s1.6", src, "lognormal", 1.6, 0.1, k, ss))
    # C: ablation 5 build seeds x 3 sim seeds
    for j in range(5):
        for src, tag in ((f"banc_female_abl{j}", f"ctrl_abl3803_s{j}"),
                         (f"mcns_male_abl{j}", f"ctrl_abl3900_s{j}")):
            for ss in (42, 43, 44):
                plan.append(job(tag, src, "linear", 0.5, 0.1, 0, ss))
    # D: equivalence pairs, seeds (1,43) and (2,44)
    for src, w, tag in (("mcns_male", 0.02, "crit_w0.02"), ("banc_female", 0.06, "crit_w0.06"),
                        ("mcns_male", 0.05, "crit_w0.05"), ("banc_female", 0.15, "crit_w0.15")):
        for ws, ss in ((1, 43), (2, 44)):
            plan.append(job(tag, src, "lognormal", 1.6, w, ws, ss))
    return plan


def main():
    plan = build_plan()
    have = existing_keys()
    todo = [j for j in plan if (j["tag"], j["source"], j["weight_seed"], j["sim_seed"]) not in have]
    print(f"plan={len(plan)}  already-present={len(plan)-len(todo)}  to-run={len(todo)}")
    with open(LOG, "a") as lf:
        lf.write(f"\n=== PHASE0 START {time.strftime('%Y-%m-%dT%H:%M:%S')} "
                 f"todo={len(todo)}/{len(plan)} ===\n")
    done = 0
    for j in todo:
        cmd = [PY, os.path.join(REPO, "ssot_run.py"),
               "--source", j["source"], "--tag", j["tag"],
               "--transform", j["transform"], "--sigma", str(j["sigma"]),
               "--w-syn", str(j["w_syn"]), "--weight-seed", str(j["weight_seed"]),
               "--sim-seed", str(j["sim_seed"])]
        t0 = time.time()
        with open(LOG, "a") as lf:
            lf.write(f"[{time.strftime('%H:%M:%S')}] RUN {j['tag']} {j['source']} "
                     f"ws={j['weight_seed']} ss={j['sim_seed']} "
                     f"sigma={j['sigma']} w={j['w_syn']} -> ")
        p = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t0
        ok = p.returncode == 0
        with open(LOG, "a") as lf:
            lf.write(("OK" if ok else f"FAIL rc={p.returncode}") + f" {dt:.1f}s\n")
            if not ok:
                lf.write((p.stderr or "")[-500:] + "\n")
        done += 1
        if done % 5 == 0 or not ok:
            print(f"  {done}/{len(todo)} done  ({j['tag']} {j['source']} ss={j['sim_seed']})  {dt:.0f}s", flush=True)
    with open(LOG, "a") as lf:
        lf.write(f"=== PHASE0 END {time.strftime('%Y-%m-%dT%H:%M:%S')} ran={done} ===\n")
    print(f"PHASE0 COMPLETE ran={done}")


if __name__ == "__main__":
    main()
