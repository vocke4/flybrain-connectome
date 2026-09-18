# Transfer Entropy Rate-Matched Control

## The setup
At the linear anchor the male brain fires far faster per neuron than the female.
Transfer entropy scales with firing rate, so the raw TE ratio is suspected to be
rate-driven.

## The test
Rate-match the male's per-neuron firing rate down to the female's per-neuron rate by
subsampling, then recompute TE. If TE remains higher, it is a wiring property; if it
collapses, it is a rate artifact.

## Result
| Condition | Female TE | Male TE | Ratio |
|---|---|---|---|
| Baseline (raw) | 0.00051 | 0.0221 | ≈44× |
| Per-neuron rate-matched | 0.00051 | 0.00047 | **0.9×** |

## Conclusion
The raw TE ratio male/female ≈44× collapses to 0.9× under per-neuron rate matching
(paper §3.8): the apparent information-flow advantage is a firing-rate artifact, and
under this control the sexes are not distinguishable in information flow. One-sided
thinning can itself impose or erase structure (the participation-ratio case
demonstrates this; `results/rate_matched_correction.md`), so the rate-matched reading
is a negative control, not a positive claim: a matched-rate simulation would be
required for any positive TE claim.

## Where TE fits in the evidence
Transfer entropy is not used as sex-difference evidence. The primary readout is
recruitment, which is robust to rate confounding by construction:

- **Recruitment:** 26.1× [21.9, 33.7] in the linear threshold regime (35.20 ± 0.68% vs
  1.35 ± 0.29%); 1.75× [1.74, 1.78] at the literature-matched σ = 1.6 lognormal anchor
  (45.04 ± 0.49% vs 79.03 ± 0.16%); 1.0× at the log1p/sqrt drive floor (paper §3.4,
  Table 4).
- **Scale-free form:** the male reaches equal recruitment at ~3–3.5× lower w_syn
  (paper §3.5, Table 5).
- **Decomposition at the saturated anchor:** 58% specific wiring / 42% degree/density
  under degree-preserving DES rewiring (paper §3.3).
- **Branching ratio:** 0.98–1.00 is pinned at the Poisson ceiling
  1 − exp(−λ) ≥ 0.99923 at these drive densities (λ ≥ 7.17 spikes/ms), so it carries no
  criticality information; under quiescence-referenced avalanche statistics neither
  real networks nor nulls show a clean power law, and no criticality claim is made
  (paper §3.5).
- **CV of ISI:** reverses sign across weight rules (linear: male 2.74 vs female 1.04;
  σ = 1.6 anchor: female 2.68 vs male 1.48), so it likewise carries no interpretable
  single-regime comparison without rate context (paper §3.8).

## Methodological lesson
The raw ≈44× TE contrast was the most rate-sensitive headline number, and the
per-neuron rate-matching control neutralizes it. Metrics that scale with firing rate
diverge artifactually between networks of different activity levels; recruitment is
the readout that does not (paper §3.8; Suárez et al., 2024).

## Next steps
1. A matched-rate simulation (both sexes driven to a common per-neuron rate) would
   enable defensible TE comparisons; post-hoc thinning does not.
2. Validate the binned TE estimator (200 random pairs, 2 ms bins) against a proper
   estimator (e.g., JIDT) before any matched-rate claim.

Full aggregated values: `results/ssot_synthesis.md`; companion analyses:
`results/rate_matched_correction.md`, `results/pr_rate_matched_correction.md`;
interpretation: `paper/preprint.md` §3.8.