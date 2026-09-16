"""
Normalize all three Drosophila connectomes into a common edge-list format.

Canonical format (per connectome, saved as .npz):
    pre_idx  : int32[N_edges]  0-based neuron index
    post_idx : int32[N_edges]  0-based neuron index
    weight   : float32[N_edges]  synapse count (or raw weight)
    sign     : int8[N_edges]    +1 excitatory, -1 inhibitory
    n_neurons: int

Sign mapping (standard fly convention, Shiu et al. / Pospisil et al.):
    Excitatory (+1): acetylcholine, glutamate, dopamine, octopamine, tyramine
    Inhibitory (-1): gaba, histamine, serotonin, glycine
    Unclear/NaN     : dropped (documented as a limitation)
"""

import numpy as np
import pyarrow.feather as feather
import pyarrow.parquet as pq
import pandas as pd
import os

DATA = os.path.join(os.path.dirname(__file__), "data")
OUT = os.path.join(os.path.dirname(__file__), "normalized")
os.makedirs(OUT, exist_ok=True)

EXCITATORY = {"acetylcholine", "glutamate", "dopamine", "octopamine", "tyramine"}
INHIBITORY = {"gaba", "histamine", "serotonin", "glycine"}


def nt_to_sign(nt):
    """Map a neurotransmitter label (possibly comma-separated) to +1/-1/None."""
    if nt is None or (isinstance(nt, float) and np.isnan(nt)):
        return None
    parts = [p.strip().lower() for p in str(nt).split(",")]
    exc = any(p in EXCITATORY for p in parts)
    inh = any(p in INHIBITORY for p in parts)
    if exc and not inh:
        return 1
    if inh and not exc:
        return -1
    return None  # mixed or unknown


def save_edgelist(name, pre_idx, post_idx, weight, sign, n_neurons):
    path = os.path.join(OUT, f"{name}.npz")
    np.savez_compressed(
        path,
        pre_idx=pre_idx.astype(np.int32),
        post_idx=post_idx.astype(np.int32),
        weight=weight.astype(np.float32),
        sign=sign.astype(np.int8),
        n_neurons=np.int32(n_neurons),
    )
    n_exc = int((sign == 1).sum())
    n_inh = int((sign == -1).sum())
    print(f"[{name}] neurons={n_neurons} edges={len(pre_idx)} "
          f"exc={n_exc} inh={n_inh} -> {path}")
    return path


# ---------------------------------------------------------------------------
# 1. Female BANC (CNS)
# ---------------------------------------------------------------------------
def normalize_banc():
    el = feather.read_table(os.path.join(DATA, "female", "banc_888_edgelist_simple_v3.feather"))
    meta = feather.read_table(
        os.path.join(DATA, "female", "banc_888_meta.feather"),
        columns=["banc_888_id", "neurotransmitter_predicted", "neurotransmitter_verified"],
    ).to_pandas()

    pre = el["pre"].to_numpy()
    post = el["post"].to_numpy()
    count = el["count"].to_numpy()

    # Build id -> sign map (prefer verified, fall back to predicted)
    sign_map = {}
    for _, row in meta.iterrows():
        bid = row["banc_888_id"]
        nt = row["neurotransmitter_verified"]
        if nt is None or (isinstance(nt, float) and np.isnan(nt)):
            nt = row["neurotransmitter_predicted"]
        s = nt_to_sign(nt)
        if s is not None:
            sign_map[bid] = s

    # Map string ids to integer indices
    all_ids = np.unique(np.concatenate([pre, post]))
    id_to_idx = {i: k for k, i in enumerate(all_ids)}
    pre_idx = np.array([id_to_idx[i] for i in pre], dtype=np.int32)
    post_idx = np.array([id_to_idx[i] for i in post], dtype=np.int32)

    # Sign per edge (from presynaptic neuron)
    sign = np.array([sign_map.get(i, 0) for i in pre], dtype=np.int8)

    # Drop edges with unknown sign
    keep = sign != 0
    pre_idx, post_idx, count, sign = pre_idx[keep], post_idx[keep], count[keep], sign[keep]

    save_edgelist("banc_female", pre_idx, post_idx, count, sign, len(all_ids))


# ---------------------------------------------------------------------------
# 2. Male MCNS (CNS)
# ---------------------------------------------------------------------------
def normalize_mcns():
    ann = feather.read_table(
        os.path.join(DATA, "male", "body-annotations-male-cns-v1.0-minconf-0.5.feather"),
        columns=["bodyId"],
    ).to_pandas()
    nt = feather.read_table(
        os.path.join(DATA, "male", "body-neurotransmitters-male-cns-v1.0.feather"),
        columns=["body", "consensus_nt"],
    ).to_pandas()

    annotated = set(ann["bodyId"].tolist())
    sign_map = {}
    for _, row in nt.iterrows():
        s = nt_to_sign(row["consensus_nt"])
        if s is not None:
            sign_map[row["body"]] = s

    # Stream weights in chunks to avoid loading 1GB at once
    wf = feather.read_table(
        os.path.join(DATA, "male", "connectome-weights-male-cns-v1.0-minconf-0.5.feather")
    )
    pre = wf["body_pre"].to_numpy()
    post = wf["body_post"].to_numpy()
    w = wf["weight"].to_numpy()

    # Filter to annotated neurons (both endpoints)
    pre_set = set(np.unique(pre))
    post_set = set(np.unique(post))
    valid = annotated & pre_set & post_set
    valid = {i for i in valid if i in sign_map}  # also need a sign
    valid_sorted = sorted(valid)
    id_to_idx = {i: k for k, i in enumerate(valid_sorted)}

    mask = np.array([(p in id_to_idx) and (q in id_to_idx) for p, q in zip(pre, post)], dtype=bool)
    pre_idx = np.array([id_to_idx[p] for p in pre[mask]], dtype=np.int32)
    post_idx = np.array([id_to_idx[q] for q in post[mask]], dtype=np.int32)
    w_f = w[mask]
    sign = np.array([sign_map[p] for p in pre[mask]], dtype=np.int8)

    save_edgelist("mcns_male", pre_idx, post_idx, w_f, sign, len(valid_sorted))


# ---------------------------------------------------------------------------
# 3. Female FAFB (brain-only, secondary reference)
# ---------------------------------------------------------------------------
def normalize_fafb():
    t = pq.read_table(
        os.path.join(os.path.dirname(__file__), "fly-brain", "data", "2025_Connectivity_783.parquet"),
        columns=["Presynaptic_Index", "Postsynaptic_Index", "Connectivity", "Excitatory"],
    )
    pre = t["Presynaptic_Index"].to_numpy()
    post = t["Postsynaptic_Index"].to_numpy()
    conn = t["Connectivity"].to_numpy()
    exc = t["Excitatory"].to_numpy()

    n = int(max(pre.max(), post.max())) + 1
    sign = np.where(exc == 1, 1, -1).astype(np.int8)
    save_edgelist("fafb_female", pre, post, conn, sign, n)


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "banc"):
        normalize_banc()
    if which in ("all", "mcns"):
        normalize_mcns()
    if which in ("all", "fafb"):
        normalize_fafb()
