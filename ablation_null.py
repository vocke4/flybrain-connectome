"""
Size-matched random ablation null for dimorphic silencing.

For each sex, build K control connectomes where a RANDOM k neurons are silenced
(k = that sex's dimorphic count, edges fully disconnected — identical procedure
to localize.py which keeps edges whose pre AND post are both non-dimorphic).

Outputs normalized/<source>_abl<seed>.npz files.

Usage:
  venv/bin/python ablation_null.py <source> <dim_count> [--k-seeds 5]
"""

import numpy as np
import os
import argparse

HERE = os.path.dirname(os.path.abspath(__file__))
NORM = os.path.join(HERE, "normalized")


def load_edgelist(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("dim_count", type=int)
    ap.add_argument("--k-seeds", type=int, default=5)
    args = ap.parse_args()

    d = np.load(os.path.join(NORM, f"{args.source}.npz"))
    pre, post, weight, sign = (d["pre_idx"], d["post_idx"], d["weight"], d["sign"])
    n = int(d["n_neurons"])
    print(f"[{args.source}] E={len(pre)} n={n} k={args.dim_count} k_seeds={args.k_seeds}")

    for seed in range(args.k_seeds):
        rng = np.random.default_rng(1000 + seed)
        rm = rng.choice(n, size=args.dim_count, replace=False)
        rm_set = np.zeros(n, dtype=bool)
        rm_set[rm] = True
        keep = ~(rm_set[pre] | rm_set[post])
        out = os.path.join(NORM, f"{args.source}_abl{seed}.npz")
        np.savez_compressed(out,
                            pre_idx=pre[keep].astype(np.int32),
                            post_idx=post[keep].astype(np.int32),
                            weight=weight[keep].astype(np.float32),
                            sign=sign[keep].astype(np.int8),
                            n_neurons=np.int32(n))
        print(f"  saved {out} (kept {int(keep.sum())} of {len(pre)} edges)")


if __name__ == "__main__":
    main()