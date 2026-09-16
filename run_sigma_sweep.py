"""
Multi-seed lognormal sigma sweep — run BOTH real networks across 5 sigma values
at a given seed, print one JSON summary.

Usage:
    python run_sigma_sweep.py <seed>
"""

import sys
import json
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SIGMAS = [0.1, 0.3, 0.5, 0.7, 1.0]


def run_one(name, sigma, seed):
    cmd = [sys.executable, os.path.join(HERE, "weight_sensitivity.py"), name,
           "--transform", "lognormal", "--sigma", str(sigma),
           "--seed", str(seed), "--duration", "2000", "--w-syn", "0.1"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"error": True, "stderr": p.stderr[-1000:]}


if __name__ == "__main__":
    seed = int(sys.argv[1])
    out = {"seed": seed, "sigmas": {}}
    for sigma in SIGMAS:
        f = run_one("banc_female", sigma, seed)
        m = run_one("mcns_male", sigma, seed)
        out["sigmas"][str(sigma)] = {
            "female_pct_fired": f.get("pct_fired"),
            "male_pct_fired": m.get("pct_fired"),
            "female_error": f.get("error", False),
            "male_error": m.get("error", False),
        }
    print("SUMMARY " + json.dumps(out))
