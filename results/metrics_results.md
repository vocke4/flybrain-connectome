# Dynamical Metrics — Male vs Female (2000ms, w_syn=0.1, seeded)

Baseline metrics for the two connectomes embedded in the identical LIF model (linear
weights, w_syn = 0.1, 2000 ms). Headline real-network conditions are sampled over three
(weight, simulation) seed-pairs of the append-only SSOT ledger; aggregated values in
`results/ssot_synthesis.md`. Higher-order metrics (transfer entropy, participation ratio,
CV of ISI) are evaluated raw and under per-neuron rate matching
(paper/preprint.md §3.8).

| Metric | Female BANC | Male MCNS | Interpretation |
|---|---|---|---|
| Recruitment (% fired) | 1.35 ± 0.29% | 35.20 ± 0.68% | 26.1× [21.9, 33.7] near the linear threshold |
| Population rate (Hz, all neurons) | 0.07 ± 0.04 | 15.50 ± 3.85 | large rate gap; rate-scaled metrics inherit it (§3.8) |
| **Branching ratio m** | 0.999 ± 0.000 | 1.001 ± 0.002 | pinned at the Poisson ceiling — no criticality information (§3.5) |
| **CV of ISI** | 1.04 ± 0.22 | 2.74 ± 0.47 | rate-dependent; reverses sign across weight rules (§3.8) |
| **Transfer entropy** | 0.0005 | 0.0221 | raw M/F ≈44×; 0.9× under per-neuron rate matching (§3.8) |
| **Participation ratio (dim)** | 6.08 | 1.28 | raw contrast reverses under thinning; no defensible dimensionality claim (§3.8) |

## Key findings

1. **The recruitment gap is the primary sex difference.** At the linear anchor the male
   recruits 35.20 ± 0.68% of neurons vs 1.35 ± 0.29% in the female — a **26.1× ratio
   (95% CI 21.9–33.7)** over three seed-pairs. The magnitude is regime-dependent
   (14.5–17.1× under mean-matched lognormal weights; 1.75× [1.74, 1.78] at the
   literature-matched σ = 1.6 anchor; 1.0× at the log1p/sqrt drive floor;
   paper/preprint.md §3.4), and the male reaches equal recruitment at ~3–3.5× lower
   w_syn (§3.5).

2. **The raw ≈44× transfer-entropy ratio collapses to 0.9× under per-neuron rate
   matching** (male subsampled to the female's per-neuron rate: 0.00047 vs 0.00051).
   The apparent information-flow advantage is a firing-rate artifact; under this control
   the sexes are not distinguishable in information flow (paper/preprint.md §3.8;
   `results/te_rate_matched_correction.md`).

3. **The participation-ratio contrast supports no dimensionality claim in either
   direction.** Raw PR reads 1.28 (male) vs 6.08 (female), suggesting a more
   synchronized male; under rate matching the male reads 43.1 vs 6.1. Both readings are
   thinning artifacts: spike thinning decorrelates neurons and inflates PR in both
   sexes (the female's own PR inflates 6.08 → 19.5 when thinned to a common 2 Hz rate).
   A matched-rate simulation would be required for any claim (paper/preprint.md §3.8;
   `results/rate_matched_correction.md`).

4. **The CV-of-ISI comparison reverses sign across weight rules.** Linear weights:
   male 2.74 ± 0.47 vs female 1.04 ± 0.22. At the σ = 1.6 anchor the ordering flips:
   female 2.68 ± 0.12 vs male 1.48 ± 0.03. A single-regime CV comparison is
   uninterpretable without rate context (paper/preprint.md §3.8).

5. **The branching ratio carries no criticality information at these drive densities.**
   m = 0.98–1.00 sits on the Poisson ceiling: the mean-ratio estimator is bounded by
   1 − exp(−λ) ≥ 0.99923 at λ ≥ 7.17 spikes/ms, so it cannot distinguish regimes. Under
   quiescence-referenced avalanche statistics neither the real networks nor their nulls
   show a clean power law, and no criticality claim is made (paper/preprint.md §3.5).

## Synthesis
The robust sex difference is position on a shared recruitment curve: the male CNS
reaches any given recruitment level at ~3–3.5× lower synaptic weight scale. At the
saturated σ = 1.6 anchor the log-gap decomposes into 58% specific wiring and 42%
degree/density structure (paper/preprint.md §3.3), consistent with the male's ~2×
connection density (mean 4.81 vs 3.10 synapses/edge, §2.1) spread across the whole
connectome. The higher-order metric contrasts (TE, PR, CV of ISI) are rate-confounded
under one-sided post-hoc thinning and are not used as sex-difference evidence
(paper/preprint.md §3.8).

## Caveats
- Transfer entropy is a simplified binned estimate (200 random pairs, 2 ms bins).
  Validation against a proper TE estimator (e.g., JIDT) remains open.
- Participation ratio subsampled to 5000 neurons (memory bound).
- The metric probes were run at a single w_syn operating point; any TE/PR/CV claim
  would require a matched-rate simulation rather than post-hoc thinning (§3.8).
- Avalanche size/duration is degenerate under this drive protocol (activity never
  drops to zero); quiescence-referenced avalanche statistics (§3.5) are the referenced
  protocol, and under them neither real networks nor nulls show a clean power law.

Full aggregated values: `results/ssot_synthesis.md`; rate-matching controls:
`results/rate_matched_correction.md`, `results/te_rate_matched_correction.md`;
interpretation: `paper/preprint.md` §3.5, §3.8.