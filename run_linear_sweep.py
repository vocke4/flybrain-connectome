"""
Linear w_syn sweep — run BOTH real networks at a given w_syn under LINEAR weights.

This uses weight_sensitivity.py (same code path as the weight-rule sensitivity
table) so the linear baseline numbers are internally consistent.

Usage:
    python run_linear_sweep.py <w_syn>
"""

import sys
import json
import subprocess
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def run_one(name, w_syn):
    cmd = [sys.executable, os.path.join(HERE, "weight_sensitivity.py"), name,
           "--transform", "linear", "--w-syn", str(w_syn),
           "--duration", "2000"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    for line in p.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    return {"error": True, "stderr": p.stderr[-1000:]}


if __name__ == "__main__":
    w_syn = float(sys.argv[1])
    f = run_one("banc_female", w_syn)
    m = run_one("mcns_male", w_syn)
    print("SUMMARY " + json.dumps({
        "w_syn": w_syn,
        "female_pct_fired": f.get("pct_fired"),
        "male_pct_fired": m.get("pct_fired"),
        "female_error": f.get("error", False),
        "male_error": m.get("error", False),
    }))
