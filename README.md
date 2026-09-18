# Validation & Reproducibility Package

**Manuscript:** *Sex differences in whole-brain dynamics of the Drosophila CNS connectome: a matched leaky integrate-and-fire comparison with degree-preserving, sign-shuffle, and ablation-null controls*

**Authors:** Katie Grillaert and Ed Vocke

**Package date:** 2026-09-18. Every number in the manuscript derives from the
single-source-of-truth (SSOT) ledger in this package.

---

## Contents

| Path | What it is |
|---|---|
| `manuscript/preprint.md` | Final manuscript (canonical text, Markdown) |
| `manuscript/preprint_v3.pdf` | Final manuscript (PDF render, 2026-09-18) |
| `results/ssot/ssot_results.jsonl` | **SSOT ledger** — 133 records → 130 unique dual-seed runs, 46 (tag, sex) families. Single source of truth for every number in the paper |
| `results/ssot/des_build.log` | Degree-preservation verification log for all 6 DES null connectomes |
| `results/crit_probe/` | Criticality-probe and w_syn-ladder ledgers (§3.5) |
| `phase0_runs.py` + `run_b2.sh` / `run_b2b.sh` / `crit_probe.py` | Ledger-supplement and probe drivers (σ=1.83 probe, DES 3×3, ablation 5×3, ladder equivalents, DES-decomposition anchor map, quiescence-referenced criticality probe; append-only, idempotent) |
| `results/ssot_synthesis.md` | Aggregate statistics (mean ± SD over 3 seed-pairs, bootstrap 95% CIs) |
| `results/localization_results.md` | Dimorphic-neuron localization analysis with size-matched ablation null |
| `results/metrics_results.md` | Raw metric comparison (pre-control) |
| `results/null_model_results.md` | Sign-shuffle control |
| `results/rate_matched_correction.md` | CV-of-ISI rate-confounding control |
| `results/te_rate_matched_correction.md` | Transfer-entropy rate-confounding control |
| `results/pr_rate_matched_correction.md` | Participation-ratio rate-confounding control |
| `results/robustness_results.md` + `robustness.csv` | Drive/w_syn robustness sweeps (SSOT values) |
| `results/lognormal_sigma_sweep_results.md` | σ-sweep (weight-dispersion) results |
| `results/weight_sensitivity_results.md` | Weight-rule sensitivity study (dual-seed SSOT values) |
| `results/literature_review.md` | Literature cross-validation (Shiu 2024, Berg 2026, Lin 2024, Pospisil 2024, bioRxiv 2026.08.21.745055) |
| Pipeline scripts (package root: `normalize.py`, `double_edge_swap.py`, `ssot_run.py`, `aggregate_ssot.py`, …) | Full pipeline (Python; see `REPRODUCING.md`) |
| `data_provenance/DATA_SOURCES.md` | First-hand source datasets, checksums, download locations |
| `REPRODUCING.md` | **Step-by-step reproduction guide** |
| `VALIDATION_REPORT.md` | Summary of every validation/verification performed |
| `MANIFEST.sha256` | SHA-256 checksums of all files in this package |

## Data availability (summary)

Raw connectomes are **not redistributed** here (≈1.4 GB, public, versioned by their
original projects). Exact filenames, SHA-256 checksums, and download locations are in
`data_provenance/DATA_SOURCES.md`. The manuscript's headline claims can be re-verified
directly from the ledger + synthesis without downloading data; full re-simulation
requires the public connectomes.