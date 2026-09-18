# Localization Results — do dimorphic circuits drive the gap?

## Test
Silence all edges touching the sexually-dimorphic neurons and re-run the matched LIF
model. If the male's excess activity collapses, dimorphic circuits are the mechanistic
driver. The size-matched random-ablation null (all edges touching k uniformly random
neurons removed, k = 3,900 male / 3,803 female; 5 build × 3 simulation seeds, n = 15
per sex) provides the control.

## Dimorphic neuron counts
- Male MCNS: 3,900 dimorphic neurons / 164,371 total (2.4%)
  (dimorphism flag OR fru/dsx high expression)
- Female BANC: 3,803 dimorphic neurons / 169,078 total (2.2%)

## Result (linear weights, w_syn = 0.1; mean ± SD over 3 seed-pairs)

**Table 6 (paper §3.6). Silencing with null (linear weights; ablation null over
5 build × 3 simulation seeds).**

| Network | Real | Dimorphic-silenced | Random-ablated (null, n = 15) |
|---|---|---|---|
| Male MCNS | 35.20 ± 0.68% | 32.23 ± 0.45% (−8.4%) | 32.98 ± 1.41% (−6.3%) |
| Female BANC | 1.35 ± 0.29% | 1.33 ± 0.29% (−1.5%) | 1.31 ± 0.23% (−2.7%) |

The male's dimorphic-silenced recruitment sits 0.75 pp below the ablation null, but
with the null's measured spread the two are statistically indistinguishable
(Welch t = 1.67, p ≈ 0.12).

## Interpretation — a NEGATIVE result that matters
Silencing all edges touching the 2.4% dimorphic neurons reduces male recruitment by
8.4% relative (35.20 → 32.23 ± 0.45%), and the size-matched random-ablation null
reduces it by 6.3% (32.98 ± 1.41%, n = 15). Dimorphic silencing does not measurably
exceed random neuron loss in either sex: the dimorphic-specific effect is modest at
best, and the male's excess activity is a DISTRIBUTED property of whole-network
wiring, not a localized effect of annotated sex-specific circuits.

This rules out the naive hypothesis that "courtship/aggression circuits explain the
sex difference." The male CNS's higher excitability is a whole-brain property,
consistent with its ~2× connection density (mean 4.81 vs 3.10 synapses/edge) being
spread across the entire connectome, not localized to sex-specific circuits,
consistent with the distributed dimorphism reported for the male CNS connectome
(Berg et al., 2026).

## What this means for the paper
The finding stands as:
1. The recruitment gap is a weight-rule-quantified, distributed property: 26.1×
   [21.9, 33.7] in the linear threshold regime, 1.75× [1.74, 1.78] at the
   literature-matched σ = 1.6 lognormal anchor (paper §3.4).
2. At the saturated anchor the log-gap splits 58% specific wiring / 42% degree/density
   under degree-preserving DES rewiring (paper §3.3).
3. Dimorphic silencing does not measurably exceed the size-matched random-ablation
   null in either sex (Welch t = 1.67, p ≈ 0.12): the sex difference is distributed,
   not localized (paper §3.6).

## Caveat
- The dimorphic flag coverage is incomplete (many neurons have NaN dimorphism).
  The 2.4% figure is a lower bound on true dimorphic neurons.
- fru/dsx expression is a proxy for dimorphism, not definitive.
- Higher-order metric contrasts (e.g., transfer entropy) are rate-confounded under
  post-hoc thinning and carry no sex-difference evidence (paper §3.8).

Full aggregated values: `results/ssot_synthesis.md`; interpretation:
`paper/preprint.md` §3.6 (Table 6).