"""
Build retry scripts for jobs that crashed on the searchsorted IndexError.

Reads queue_female.sh / queue_male.sh, extracts ssot_run.py commands, checks
each (tag, source, weight_seed, sim_seed) against ssot_results.jsonl, and
emits retry_<sex>.sh containing only missing jobs. Male des_* jobs are
excluded (owned by the still-running male lane).
"""

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SSOT = os.path.join(HERE, "results", "ssot", "ssot_results.jsonl")

done = set()
with open(SSOT) as f:
    for line in f:
        r = json.loads(line)
        done.add((r["tag"], r["source"], r["weight_seed"], r["sim_seed"]))

ARG = re.compile(r"--(\S+)\s+(\S+)")


def extract(path):
    cmds = []
    with open(path) as f:
        for line in f:
            if "ssot_run.py" not in line:
                continue
            a = dict(ARG.findall(line))
            cmds.append((line.strip(), a))
    return cmds


for sex in ("female", "male"):
    retry = []
    for cmd, a in extract(os.path.join(HERE, f"queue_{sex}.sh")):
        tag, src = a.get("tag"), a.get("source")
        ws, ss = int(a.get("weight-seed", 0)), int(a.get("sim-seed", 42))
        if (tag, src, ws, ss) in done:
            continue
        if sex == "male" and tag.startswith("des_"):
            continue  # owned by the live male lane
        retry.append(cmd)
    out = os.path.join(HERE, f"retry_{sex}.sh")
    with open(out, "w") as f:
        f.write("#!/bin/bash\ncd " + HERE + "\n")
        for cmd in retry:
            f.write(cmd + f" >> results/ssot/lane_{sex}.log 2>&1 || echo 'RETRY FAILED' >> results/ssot/lane_{sex}.log\n")
    os.chmod(out, 0o755)
    print(f"{out}: {len(retry)} jobs to retry")