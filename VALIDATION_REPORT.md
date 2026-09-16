# Validation Report

Every verification performed on this study, with first-hand evidence. Compiled 2026-09-11.

## 1. Data integrity

| Check | Result |
|---|---|
| Source datasets are the official public releases | MaleCNS v1.0 (Janelia FlyEM; Berg et al., *Cell* 2026) and BANC (FlyWire/HMS; Bates et al. preprint) — exact filenames match the official download tables |
| Source checksums recorded | SHA-256 for all 5 source feathers — see `data_provenance/DATA_SOURCES.md` |
| Normalization counts match publications | Female 169,078 neurons / 13,379,740 edges (BANC); male 163,511 neurons / 24,410,950 edges (MaleCNS); 41.5M/117.5M synapses — consistent with the source papers' CNS-scale figures |
| Sign convention | Standard fly convention (Shiu et al. 2024 / Pospisil et al. 2024): ACh/Glu/DA/OA/TA excitatory; GABA/histamine/serotonin/glycine inhibitory; mixed/unknown dropped (documented limitation) |

## 2. Model equivalence between sexes

| Check | Result |
|---|---|
| Identical LIF parameters both sexes | V_rest=V_reset=−65 mV, V_th=−50 mV, τ=10 ms, refractory 2.2 ms, drive weight 5 mV — hardcoded identically (`ssot_run.py`) |
| Identical drive protocol | 1% of neurons, Poisson 100 Hz, drive set drawn from `default_rng(sim_seed)` per run |
| Weight rule identical both sexes | w = sign × f(count) × w_syn, same transform pipeline both sexes |

## 3. Stochasticity control (dual-seed design)

| Check | Result |
|---|---|
| Weight draw seeded | `np.random.default_rng(weight_seed)` — independent of dynamics |
| Dynamics seeded | `brian2.seed(sim_seed)` — explicit call required because Brian2's internal RNG is NOT covered by `np.random.seed()` (verified root cause of legacy discrepancy) |
| Drive selection seeded | `default_rng(sim_seed)` per run |
| Variance quantified | 3 (weight_seed, sim_seed) pairs per stochastic condition; mean ± SD reported; bootstrap 20k CIs on every headline ratio |
| Legacy-vs-SSOT reconciliation | Legacy single-seed pipeline (unseeded Brian2 RNG) reproduced the male value (36.2 vs 35.2±0.7) but showed inflated female variance at the ignition threshold; SSOT supersedes — full code-verified root-cause write-up in `results/ssot_changelog.md` |

## 4. Null-model validity

| Check | Result |
|---|---|
| DES degree preservation | Degree sequences verified **identical** post-rewiring, all 6 connectomes (log: `results/ssot/des_build.log`); Q=10 mixing (10× edges swaps); 99.1%/98.7% acceptance |
| DES preserves weights-with-source | Weights travel with the presynaptic source edge |
| DES reproducibility | 3 independent DES seeds per sex → DES recruitment SD ≤0.21% (female), ≤0.05% (male) |
| Ablation null | 5 size-matched random-ablation seeds per sex (k=3,900 male / 3,803 female = exact dimorphic counts) |
| Sign-shuffle control | Preserves wiring and E/I counts, randomizes placement; bimodal female seeds (19.3/19.2/1.0%) reported with candor (ignition-threshold bifurcation, reproduced on re-run) |

## 5. Statistical validity

| Check | Result |
|---|---|
| Bootstrap CIs | 20,000 resamples; percentile method; computed on ratio of means |
| All headline ratios carry CIs | 1.75× [1.74,1.78]; 26.1× [21.9,33.7]; 1.27× [1.26,1.27] |
| Aggregation dedupe | Last-timestamp-wins on (tag, source, weight_seed, sim_seed) — 87 raw records → 84 unique |
| Re-aggregation stability | `aggregate_ssot.py` re-run on shipped ledger is byte-identical to shipped synthesis (verified 2026-09-11) |
| Branching ratio | 0.983–1.004 across all 84 runs — every network self-organized near criticality |

## 6. Rate-confounding controls (§3.8 of manuscript)

| Metric | Raw comparison | Rate-matched | Verdict |
|---|---|---|---|
| Transfer entropy | 0.0221 vs 0.0005 ("44×") | 0.00047 vs 0.00051 (0.9×) | Rate artifact — excluded from headline claims |
| Participation ratio | 1.28 vs 6.08 | Reverses (43.1 vs 6.1) — but thinning inflates female's own PR 6.08→19.5 | Post-hoc thinning artifact either direction — excluded |
| CV of ISI | 2.99 vs 1.01 | 1.21 vs 1.00; sign reverses across regimes (linear M 2.74/F 1.04; σ=1.6 anchor F 2.68/M 1.48) | Regime-dependent — reported with caveats only |
| Recruitment % | — | — | Primary readout; robust to rate confounding by construction |

Evidence: `results/te_rate_matched_correction.md`, `results/pr_rate_matched_correction.md`, `results/rate_matched_correction.md`; scripts `te_control2.py`, `pr_control.py`, `cv_control.py`.

## 7. Robustness of the headline claim

| Check | Result |
|---|---|
| Weight rule | Direction invariant across linear / lognormal (σ=0.5, 1.0, 1.6) / mean-matched log1p / sqrt; magnitude regime-dependent (26× near threshold → 1.75× high gain) — reported as the recruitment ladder, not a single number |
| σ parameterization | Literature SD(log w)≈1.83 is *total* log-spread = √(SD(log count)² + σ²); σ=1.6 reproduces it without overshooting (verified against bioRxiv 2026.08.21.745055 fitted value) |
| Drive/duration | All runs 2000 ms, 1% drive at 100 Hz; w_syn ladder swept (crit_w0.01–0.15) |
| Internal consistency | Legacy robustness.csv "20×" identified as different-seed artifact; final internally-consistent linear sweep: 13.4× at w_syn=0.1 single-seed legacy → 26.1× SSOT multi-seed (documented in `results/final_polish_results.md` and `ssot_changelog.md`) |

## 8. Localization claim and its null

| Check | Result |
|---|---|
| Dimorphic-neuron identification | From sex-typed annotations: male 3,900 / female 3,803 dimorphic neurons (2.4% of cells) — cross-validated against Berg et al. 2026 ("dimorphic neurons concentrated in higher-order centers, periphery largely isomorphic") |
| Silencing effect vs proper null | Dimorphic silencing −8.4% relative (M); size-matched random ablation −4.9% (M) → effect real but modest; female silencing indistinguishable from random ablation |
| Distributed-not-localized conclusion | Supported by ablation-null comparison, not asserted without control |

## 9. Literature cross-validation (first-hand sources)

| External finding | Our result | Agreement |
|---|---|---|
| Shiu et al. 2024 (FAFB LIF, w∝count, critical regime) | Direct replication of model class; m≈1 recovered | ✓ |
| Berg et al. 2026 (male CNS; dimorphism distributed) | Silencing effect distributed, modest | ✓ |
| Lin et al. 2024 (network statistics) | Degree/density structural differences consistent | ✓ |
| Pospisil et al. 2024 (weights must be fitted) | w∝count treated as placeholder; sensitivity study + lognormal anchor | ✓ (addressed) |
| bioRxiv 2026.08.21.745055 (fitted lognormal σ) | σ=1.6 anchor reproduces fitted SD(log w)≈1.83 | ✓ |

Details: `results/literature_review.md`.

## 10. Manuscript-level verification (final pass, 2026-09-11)

- Every number in the manuscript cross-checked against the ledger (spot-check of all 8 results sections + abstract + conclusion: **all match**)
- No stale figures: manuscript embeds no images; no table rows contradict the ledger
- Meta-commentary removed; §3.8 framed as metric-vulnerability demonstration
- PDF rendered from the verified Markdown (pandoc → weasyprint); PDF text extraction verified to contain the same numbers and no scrub-language remnants

## Known limitations (stated in manuscript §5)

- Simplified binned TE estimator (a proper estimator, e.g., JIDT, would be required for any use of that metric)
- Mixed/unknown neurotransmitter edges dropped during normalization
- LIF model with voltage-injection synapses; no dendritic morphology, no neuromodulation
- Sign-shuffle and DES nulls probe structure at the connectome level; they do not substitute for fitted-weight models (Pospisil et al. 2024)
- Single animal per sex (the connectomes are single-animal reconstructions); all variance quantified is model/draw variance, not biological sampling variance