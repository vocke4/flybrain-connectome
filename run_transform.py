"""
Wrapper: run BOTH networks for one weight transform, print a clean JSON summary.

This is the single command each orchestration subagent runs. It keeps the
subagent's job to "run one command, read one JSON line" — no multi-step
process management for a flash model.

Usage:
    python run_transform.py <transform> [--duration 2000] [--w-syn 0.1]
"""

import json
import sys
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def run_one(name, transform, duration, w_syn):
    cmd = [sys.executable, os.path.join(HERE, "weight_sensitivity.py"),
           name, "--transform", transform, "--duration", str(duration),
           "--w-syn", str(w_syn)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    # find the RESULT line
    result = None
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            result = json.loads(line[len("RESULT "):])
    if result is None:
        return {"name": name, "error": True,
                "stdout_tail": p.stdout[-2000:], "stderr_tail": p.stderr[-2000:]}
    return result


if __name__ == "__main__":
    transform = sys.argv[1]
    duration = 2000
    w_syn = 0.1
    if "--duration" in sys.argv:
        duration = float(sys.argv[sys.argv.index("--duration") + 1])
    if "--w-syn" in sys.argv:
        w_syn = float(sys.argv[sys.argv.index("--w-syn") + 1])

    female = run_one("banc_female", transform, duration, w_syn)
    male = run_one("mcns_male", transform, duration, w_syn)

    summary = {
        "transform": transform,
        "female_pct_fired": female.get("pct_fired"),
        "male_pct_fired": male.get("pct_fired"),
        "female_n_spikes": female.get("n_spikes"),
        "male_n_spikes": male.get("n_spikes"),
        "female_error": female.get("error", False),
        "male_error": male.get("error", False),
    }
    if female.get("error"):
        summary["female_stderr"] = female.get("stderr_tail", "")[-500:]
    if male.get("error"):
        summary["male_stderr"] = male.get("stderr_tail", "")[-500:]

    print("SUMMARY " + json.dumps(summary))
