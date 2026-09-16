"""Aggregate ssot_results.jsonl into the SSOT synthesis report.

Dedupes on (tag, source, weight_seed, sim_seed) — LAST timestamp wins (the
male DES sims were double-fired by the lane wait-loop and finish_missing.sh;
re-runs intentionally overwrite earlier bad records).

Writes results/ssot_synthesis.md with per-condition mean ± SD and the
headline ratio / log-gap decomposition. Idempotent.
"""

import json
import os
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SSOT = os.path.join(HERE, "results", "ssot", "ssot_results.jsonl")
OUT = os.path.join(HERE, "results", "ssot_synthesis.md")

METRICS = ("pct_fired", "rate_all_Hz", "branching_ratio", "cv_isi")


def load_dedup():
    best = {}
    with open(SSOT) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            k = (r["tag"], r["source"], r["weight_seed"], r["sim_seed"])
            if k not in best or r["ts"] > best[k]["ts"]:
                best[k] = r
    return list(best.values())


def msd(vals):
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], float)
    if len(v) == 0:
        return None
    return float(v.mean()), float(v.std(ddof=1)) if len(v) > 1 else 0.0


def fmt(m, digits=2):
    if m is None:
        return "—"
    return f"{m[0]:.{digits}f} ± {m[1]:.{digits}f}"


def main():
    recs = load_dedup()
    groups = defaultdict(list)
    for r in recs:
        groups[(r["tag"], r["source"])].append(r)

    print(f"unique records: {len(recs)}, conditions: {len(groups)}")

    lines = [
        "# SSOT Synthesis (auto-generated from results/ssot/ssot_results.jsonl)",
        "",
        f"{len(recs)} unique records, {len(groups)} conditions; dual-seed "
        "(weight_seed × sim_seed); mean ± SD across seed-pairs; ddof=1.",
        "Dedup: last-timestamp-wins per (tag, source, weight_seed, sim_seed).",
        "",
        "| condition | source | n | % fired | rate all (Hz) | branching | CV-ISI |",
        "|---|---|---|---|---|---|---|",
    ]
    for (tag, src), g in sorted(groups.items()):
        cells = [tag, src, str(len(g))]
        for m in METRICS:
            m_ = msd([r.get(m) for r in g])
            cells.append(fmt(m_, 3 if m == "branching_ratio" else 2))
        lines.append("| " + " | ".join(cells) + " | ")

    # --- headline decomposition ------------------------------------------
    def cond(sex, tag):
        for (t, s), g in groups.items():
            if t == tag and ((sex == "M") == s.startswith("mcns")):
                return g
        return None

    def ratio_cis(gf, gm, field="pct_fired"):
        """Delta-method CI on male/female ratio via seed-pair bootstrap."""
        rng = np.random.default_rng(0)
        f = np.array([r[field] for r in gf if r.get(field) is not None])
        m = np.array([r[field] for r in gm if r.get(field) is not None])
        stats = []
        for _ in range(10000):
            fs = f[rng.integers(0, len(f), len(f))]
            ms = m[rng.integers(0, len(m), len(m))]
            if fs.mean() > 0:
                stats.append(ms.mean() / fs.mean())
        stats = np.array(stats)
        return (f"{np.mean(f):.2f}±{np.std(f, ddof=1):.2f}",
                f"{np.mean(m):.2f}±{np.std(m, ddof=1):.2f}",
                f"{np.mean(m)/np.mean(f):.2f} "
                f"[{np.percentile(stats, 2.5):.2f}, {np.percentile(stats, 97.5):.2f}]")

    lines += ["", "## Headline decomposition (σ=1.6, w_syn=0.1)", ""]
    f_real, m_real = cond("F", "anchor_ln_s1.6_w0.1"), cond("M", "anchor_ln_s1.6_w0.1")
    f_des = [g for (t, s), g in groups.items() if t.startswith("des_s") and s.startswith("banc_female_des")]
    m_des = [g for (t, s), g in groups.items() if t.startswith("des_s") and s.startswith("mcns_male_des")]
    fr, mr, rr = ratio_cis(f_real, m_real)
    lines.append(f"- Real: female {fr}, male {mr} → ratio {rr}")
    fdes_all = [r for g in f_des for r in g]
    mdes_all = [r for g in m_des for r in g]
    fr2, mr2, rr2 = ratio_cis(fdes_all, mdes_all)
    lines.append(f"- DES rewired: female {fr2}, male {mr2} → ratio {rr2}")
    import math
    lf, lm = math.log(float(fr.split("±")[0])), math.log(float(mr.split("±")[0]))
    ld_f, ld_m = math.log(float(fr2.split("±")[0])), math.log(float(mr2.split("±")[0]))
    gap_real = lm - lf
    gap_des = ld_m - ld_f
    share_wiring = 1 - gap_des / gap_real
    lines.append(f"- log-gap real {gap_real:.3f}, DES {gap_des:.3f} → "
                 f"specific-wiring share {share_wiring*100:.0f}%, "
                 f"degree/density share {(1-share_wiring)*100:.0f}%")

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {OUT}")
    for ln in lines[-4:]:
        print(ln)


if __name__ == "__main__":
    main()