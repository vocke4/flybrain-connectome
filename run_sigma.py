"""
Lognormal sigma sweep — run BOTH real networks at a given lognormal sigma and seed.

Usage:
    python run_sigma.py <sigma> [--seed 0]
"""

import sys
import json
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def run_one(name, sigma, seed):
    cmd = [sys.executable, os.path.join(HERE, "weight_sensitivity.py"), name,
           "--transform", "lognormal", "--sigma", str(sigma),
           "--seed", str(seed),
           "--duration", "2000", "--w-syn", "0.1"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"error": True, "stderr": p.stderr[-1000:]}


if __name__ == "__main__":
    sigma = float(sys.argv[1])
    seed = 0
    if "--seed" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--seed") + 1])
    f = run_one("banc_female", sigma, seed)
    m = run_one("mcns_male", sigma, seed)
    print("SUMMARY " + json.dumps({
        "sigma": sigma,
        "seed": seed,
        "female_pct_fired": f.get("pct_fired"),
        "male_pct_fired": m.get("pct_fired"),
        "female_error": f.get("error", False),
        "male_error": m.get("error", False),
    }))
