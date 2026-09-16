"""
Rewiring null under lognormal weights.

The original "wiring, not size" claim was established under LINEAR weights:
rewiring collapses both brains to ~1%. This re-tests it under the
literature-supported LOGNORMAL weight rule: does degree-preserving rewiring
still collapse the male/female gap?

Usage:
    python run_rewired_lognormal.py
"""

import sys
import json
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def run_one(name):
    cmd = [sys.executable, os.path.join(HERE, "weight_sensitivity.py"), name,
           "--transform", "lognormal", "--sigma", "0.5",
           "--duration", "2000", "--w-syn", "0.1"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"error": True, "stderr": p.stderr[-1000:]}


if __name__ == "__main__":
    f = run_one("banc_female_rewired")
    m = run_one("mcns_male_rewired")
    print("SUMMARY " + json.dumps({
        "female_rewired_pct_fired": f.get("pct_fired"),
        "male_rewired_pct_fired": m.get("pct_fired"),
        "female_error": f.get("error", False),
        "male_error": m.get("error", False),
    }))
