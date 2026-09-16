"""
Degree-preserving double-edge-swap configuration model.

Fixes the reviewer/PRD critique of null_model.py: the post-target permutation
preserves out-degree exactly but randomizes the in-degree SEQUENCE, so a null
collapse could reflect destruction of in-degree hubs, not "specific wiring."

Double-edge swap: pick two random directed edges (a->b, c->d), swap targets to
(a->d, c->b). Preserves out-degree AND in-degree of every node exactly.
Validation: reject self-loops and duplicate edges; retry with fresh random picks.

Mixing: Q x E successful swaps, Q=10 default (PRD spec).

Usage:
  venv/bin/python double_edge_swap.py <source> [--q 10] [--seed 0]
  writes normalized/<source>_des_<seed>.npz
"""

import numpy as np
import os
import sys
import argparse

NORM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "normalized")


def load_edgelist(name):
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    return d["pre_idx"].astype(np.int64), d["post_idx"].astype(np.int64), \
        d["weight"], d["sign"], int(d["n_neurons"])


def double_edge_swap(pre, post, n_swaps, seed, max_attempts_factor=50):
    """In-place double-edge swaps with validation. Returns new (pre, post).

    Edge set is stored as int64 keys (pre * 2**32 + post) for memory:
    24.4M edges -> ~1 GB as int64 vs ~4 GB as Python tuples.
    """
    rng = np.random.default_rng(seed)
    pre = pre.copy()
    post = post.copy()
    E = len(pre)
    SHIFT = np.int64(1) << np.int64(32)
    keys = pre * SHIFT + post
    edge_set = set(keys.tolist())
    done = 0
    attempts = 0
    max_attempts = n_swaps * max_attempts_factor

    while done < n_swaps and attempts < max_attempts:
        attempts += 1
        i1, i2 = rng.integers(0, E, size=2)
        if i1 == i2:
            continue
        a, b = int(pre[i1]), int(post[i1])
        c, d = int(pre[i2]), int(post[i2])
        if a == c and b == d:
            continue
        # new edges (a->d) and (c->b)
        if a == d or c == b:            # self-loops
            continue
        k1, k2 = a * int(SHIFT) + d, c * int(SHIFT) + b
        if k1 in edge_set or k2 in edge_set:  # duplicates
            continue
        if k1 == a * int(SHIFT) + b or k1 == c * int(SHIFT) + d:
            continue  # would need to keep an original edge alive
        if k2 == a * int(SHIFT) + b or k2 == c * int(SHIFT) + d:
            continue
        # commit
        edge_set.discard(a * int(SHIFT) + b)
        edge_set.discard(c * int(SHIFT) + d)
        edge_set.add(k1)
        edge_set.add(k2)
        post[i1] = d
        post[i2] = b
        done += 1

    return pre, post, done, attempts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--q", type=float, default=10.0, help="mixing parameter")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    pre, post, weight, sign, n = load_edgelist(args.source)
    E = len(pre)
    n_swaps = int(args.q * E)
    print(f"[{args.source}] E={E} n_swaps={n_swaps} (Q={args.q})")

    # verify degree preservation capability up front
    pre2, post2, done, attempts = double_edge_swap(pre, post, n_swaps, args.seed)
    print(f"[{args.source}] swaps done={done} attempts={attempts} "
          f"({100.0*done/attempts:.1f}% acceptance)")

    # verify degree sequences preserved exactly
    in0 = np.bincount(post, minlength=n)
    in2 = np.bincount(post2, minlength=n)
    out0 = np.bincount(pre, minlength=n)
    out2 = np.bincount(pre2, minlength=n)
    assert (in0 == in2).all(), "IN-DEGREE NOT PRESERVED"
    assert (out0 == out2).all(), "OUT-DEGREE NOT PRESERVED"
    print(f"[{args.source}] degree sequences verified identical")

    out = os.path.join(NORM, f"{args.source}_des_{args.seed}.npz")
    np.savez_compressed(out,
                        pre_idx=pre2.astype(np.int32), post_idx=post2.astype(np.int32),
                        weight=weight, sign=sign, n_neurons=np.int32(n))
    print(f"saved {out}")


if __name__ == "__main__":
    main()