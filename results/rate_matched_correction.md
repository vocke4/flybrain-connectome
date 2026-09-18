# Rate-Matched Controls

## What was tested
At the linear anchor the male fires far faster per neuron than the female; any
information or dimensionality measure scaled by firing rate is confounded by that rate
difference. The male's per-neuron firing rate was subsampled down to the female's
before recomputing the metric (paper §3.8).

## Results

### Transfer entropy — rate artifact
| Condition | Female | Male | Ratio |
|---|---|---|---|
| Baseline | 0.00051 | 0.0221 | ≈44× |
| Rate-matched | 0.00051 | 0.00047 | 0.9× |

The raw ≈44× transfer-entropy ratio collapses to 0.9× under per-neuron rate matching
(paper §3.8; `results/te_rate_matched_correction.md`). The apparent information-flow
advantage is a firing-rate artifact: under this control the sexes are not
distinguishable in information flow.

### Participation ratio (dimensionality) — thinning artifact, no defensible claim in either direction
| Condition | Female | Male |
|---|---|---|
| Baseline | 6.08 | 1.28 (raw reading: "more synchronized") |
| Rate-matched (male thinned) | 6.08 | 43.1 (male reads MORE high-dimensional) |

The raw PR contrast reverses under thinning, but the reversal is itself an artifact:
spike thinning decorrelates neurons and inflates PR for both sexes. The female's own
PR inflates **6.08 → 19.5** when thinned to a common 2 Hz rate
(`results/pr_rate_matched_correction.md`). Dimensionality estimated from post-hoc
thinning is not defensible in either direction; a matched-rate simulation would be
required for any claim (paper §3.8).

### CV of ISI — rate-dependent and regime-dependent
The raw CV contrast at the linear anchor (male 2.74 ± 0.47 vs female 1.04 ± 0.22) is
rate-driven. A rate-matched CV comparison would require an archived matched-rate
control, which is not shipped, so no rate-matched CV claim is made. Moreover, CV
**reverses sign across weight rules**: linear weights give male 2.74 vs female 1.04,
while the σ = 1.6 anchor gives female 2.68 ± 0.12 vs male 1.48 ± 0.03 — a
single-regime CV comparison is uninterpretable without rate context (paper §3.8).

## Findings that stand

1. **The recruitment difference** — 26.1× [21.9, 33.7] in the linear threshold regime
   (35.20 ± 0.68% vs 1.35 ± 0.29%); 1.75× [1.74, 1.78] at the literature-matched σ = 1.6
   lognormal anchor — survives degree-preserving rewiring's decomposition as 58%
   specific wiring / 42% degree/density at the anchor (paper §3.3, §3.4). It is a
   distributed wiring property, not size and not localized dimorphic circuits
   (paper §3.6).
2. **Recruitment, not any rate-scaled metric, is the primary readout.** The branching
   ratio prints 0.98–1.00 but is pinned at the Poisson ceiling 1 − exp(−λ) ≥ 0.99923 at
   these drive densities (λ ≥ 7.17 spikes/ms), carrying no criticality information;
   under quiescence-referenced avalanche statistics neither real networks nor nulls
   show a clean power law, and no criticality claim is made (paper §3.5).

## The finding

The male CNS recruits substantially more of itself than the female at matched drive,
at ~3–3.5× lower w_syn for equal recruitment, and this is a distributed property of
whole-network wiring (58% specific wiring / 42% degree/density at the σ = 1.6 anchor).
The higher-order metric contrasts (TE, PR) are one-sided-thinning artifacts and are
not used as sex-difference evidence; CV of ISI reverses sign across weight rules and
carries no interpretable single-regime comparison (paper §3.8).

## Methodological lesson
Metrics that scale with firing rate (transfer entropy, participation ratio, CV of ISI)
diverge artifactually between networks of different activity levels; per-neuron rate
matching is the control, and one-sided thinning can itself impose or erase structure
(the PR case). This caution applies to any connectome-dynamics comparison in which
the networks under study differ in overall activity (paper §3.8; Suárez et al., 2024).

## Next steps
1. A matched-rate simulation (drive adjusted so both sexes fire at a common
   per-neuron rate) would enable defensible TE/PR/CV comparisons; post-hoc thinning
   does not.
2. The σ = 1.6 anchor provides the higher-activity regime where per-neuron rates are
   closer (154.1 vs 231.8 Hz for active neurons; paper Table 2), a natural operating
   point for matched-rate probes.

Full aggregated values: `results/ssot_synthesis.md`; companion analyses:
`results/te_rate_matched_correction.md`, `results/pr_rate_matched_correction.md`;
interpretation: `paper/preprint.md` §3.8.