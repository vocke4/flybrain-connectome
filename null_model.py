"""
Null models for each connectome.

1. Configuration-model rewiring: permute the post-synaptic targets of all edges.
   Preserves out-degree exactly, in-degree in expectation, and the full
   weight/sign distribution. Destroys the specific wiring. Fast (one permutation).

2. Sign-shuffle: keep wiring, randomize excitatory/inhibitory sign.

Usage:
    python null_model.py <name> [--seed 0]
"""

import numpy as np
import os
import argparse

NORM = os.path.join(os.path.dirname(__file__), "normalized")
OUT = NORM


def load_edgelist(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["pre_idx"], d["post_idx"], d["weight"], d["sign"], int(d["n_neurons"])


def save(name_out, pre, post, weight, sign, n):
    np.savez_compressed(
        os.path.join(OUT, f"{name_out}.npz"),
        pre_idx=pre.astype(np.int32),
        post_idx=post.astype(np.int32),
        weight=weight.astype(np.float32),
        sign=sign.astype(np.int8),
        n_neurons=np.int32(n),
    )
    print(f"  saved {name_out}.npz")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    pre, post, weight, sign, n = load_edgelist(args.name)
    print(f"[{args.name}] edges={len(pre)} neurons={n}")

    # 1. Configuration model: permute post targets
    rng = np.random.default_rng(args.seed)
    perm = rng.permutation(len(post))
    post_r = post[perm]
    save(f"{args.name}_rewired", pre, post_r, weight, sign, n)

    # 2. Sign shuffle
    rng2 = np.random.default_rng(args.seed + 1)
    sign_s = sign.copy()
    rng2.shuffle(sign_s)
    save(f"{args.name}_signshuffled", pre, post, weight, sign_s, n)
