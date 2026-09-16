"""
Localization: do sexually-dimorphic circuits drive the male/female dynamical gap?

Test: silence the dimorphic neurons (zero their incoming+outgoing synapses) and
re-run the matched LIF model. If the male's excess activity collapses toward the
female's level, the dimorphic circuits are the mechanistic driver.

Dimorphic definition:
  Male MCNS:  dimorphism in {male-specific, sexually dimorphic, potentially *}
              OR fruDsx in {fru_high, dsx_high, coexpress_high}
  Female BANC: sexually_dimorphic in {dimorphic, female-specific, male-specific}

Usage:
    python localize.py
"""

import numpy as np
import os
import subprocess
import pyarrow.feather as feather

HERE = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(HERE, "venv", "bin", "python")
NORM = os.path.join(HERE, "normalized")
DATA = os.path.join(HERE, "data")


def male_dimorphic_indices():
    """Return normalized indices of dimorphic male neurons."""
    ann = feather.read_table(
        os.path.join(DATA, "male", "body-annotations-male-cns-v1.0-minconf-0.5.feather"),
        columns=["bodyId", "dimorphism", "fruDsx"],
    ).to_pandas()
    nt = feather.read_table(
        os.path.join(DATA, "male", "body-neurotransmitters-male-cns-v1.0.feather"),
        columns=["body", "consensus_nt"],
    ).to_pandas()

    dim = set()
    for _, row in ann.iterrows():
        d = row["dimorphism"]
        f = row["fruDsx"]
        if isinstance(d, str) and d in ("male-specific", "sexually dimorphic",
                                        "potentially sexually dimorphic", "potentially male-specific"):
            dim.add(row["bodyId"])
        elif isinstance(f, str) and f in ("fru_high", "dsx_high", "coexpress_high"):
            dim.add(row["bodyId"])

    # Reconstruct the valid set (same as normalize.py)
    sign_map = {}
    for _, row in nt.iterrows():
        s = row["consensus_nt"]
        if isinstance(s, str):
            sl = s.lower()
            exc = any(x in sl for x in ("acetylcholine", "glutamate", "dopamine", "octopamine", "tyramine"))
            inh = any(x in sl for x in ("gaba", "histamine", "serotonin", "glycine"))
            if exc and not inh:
                sign_map[row["body"]] = 1
            elif inh and not exc:
                sign_map[row["body"]] = -1

    # valid = annotated AND has sign
    annotated = set(ann["bodyId"].tolist())
    valid = sorted(annotated & set(sign_map.keys()))
    id_to_idx = {i: k for k, i in enumerate(valid)}

    dim_idx = sorted(id_to_idx[i] for i in dim if i in id_to_idx)
    return dim_idx, len(valid)


def female_dimorphic_indices():
    """Return normalized indices of dimorphic female neurons."""
    meta = feather.read_table(
        os.path.join(DATA, "female", "banc_888_meta.feather"),
        columns=["banc_888_id", "sexually_dimorphic"],
    ).to_pandas()

    # Reconstruct female index mapping (same as normalize.py)
    el = feather.read_table(
        os.path.join(DATA, "female", "banc_888_edgelist_simple_v3.feather"),
        columns=["pre", "post"],
    )
    all_ids = np.unique(np.concatenate([el["pre"].to_numpy(), el["post"].to_numpy()]))
    id_to_idx = {i: k for k, i in enumerate(all_ids)}

    dim = set()
    for _, row in meta.iterrows():
        sd = row["sexually_dimorphic"]
        if isinstance(sd, str) and sd in ("dimorphic", "female-specific", "male-specific"):
            dim.add(row["banc_888_id"])

    dim_idx = sorted(id_to_idx[i] for i in dim if i in id_to_idx)
    return dim_idx, len(all_ids)


def silence_and_run(name, dim_idx, n_neurons, out_name):
    """Build a silenced edgelist (zero synapses to/from dimorphic neurons) and run."""
    d = np.load(os.path.join(NORM, f"{name}.npz"))
    pre, post, weight, sign = d["pre_idx"], d["post_idx"], d["weight"], d["sign"]

    dim_set = set(dim_idx)
    mask = np.array([(p not in dim_set) and (q not in dim_set) for p, q in zip(pre, post)], dtype=bool)
    pre_s, post_s, weight_s, sign_s = pre[mask], post[mask], weight[mask], sign[mask]

    np.savez_compressed(
        os.path.join(NORM, f"{out_name}.npz"),
        pre_idx=pre_s.astype(np.int32), post_idx=post_s.astype(np.int32),
        weight=weight_s.astype(np.float32), sign=sign_s.astype(np.int8),
        n_neurons=np.int32(n_neurons),
    )
    r = subprocess.run(
        [PY, "model.py", out_name, "--duration", "2000", "--w-syn", "0.1"],
        capture_output=True, text=True, cwd=HERE,
    )
    out = r.stdout + r.stderr
    fired_pct = None
    for line in out.splitlines():
        if "neurons_fired=" in line:
            fired_pct = float(line.split("(")[1].split("%")[0])
    return fired_pct, len(pre_s)


if __name__ == "__main__":
    print("=== Localization: silence dimorphic circuits ===")

    # Male
    dim_m, n_m = male_dimorphic_indices()
    print(f"male: {len(dim_m)} dimorphic neurons / {n_m} total ({100*len(dim_m)/n_m:.1f}%)")
    pct_m, edges_m = silence_and_run("mcns_male", dim_m, n_m, "mcns_male_nodimorph")
    print(f"male silenced: {pct_m}% fire (was 36.3%)")

    # Female
    dim_f, n_f = female_dimorphic_indices()
    print(f"female: {len(dim_f)} dimorphic neurons / {n_f} total ({100*len(dim_f)/n_f:.1f}%)")
    pct_f, edges_f = silence_and_run("banc_female", dim_f, n_f, "banc_female_nodimorph")
    print(f"female silenced: {pct_f}% fire (was 2.7%)")
