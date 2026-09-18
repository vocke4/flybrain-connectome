# Weight-Rule Sensitivity — the recruitment gap is regime-quantified across weight rules

## What was tested

The recruitment gap is measured under the field-standard linear weight rule
`w = sign × count × w_syn` and under transforms suggested by the literature (Pospisil
2024 effectome; Aug 2026 bioRxiv connectome-constrained fitting): true weights are NOT
linear in synapse count — fitting yields **lognormal** weights. The male has ~2×
connection density, so under the linear rule it gets ~2× more weight per neuron,
which could inflate the activity gap.

The matched LIF model (w_syn = 0.1, 2000 ms, drive 1% @100 Hz) runs under four weight
transforms; headline conditions are sampled over three (weight, simulation) seed-pairs
of the append-only SSOT ledger (paper §2.4, §3.4):

| Transform | Rule | Rationale |
|---|---|---|
| linear | w = count | baseline (Shiu 2024) |
| log1p | w = log(1+count) | compress high-count synapses |
| sqrt | w = sqrt(count) | intermediate compression |
| lognormal | w = exp(N(log count, σ)) · w_syn | literature-supported (2026 fitting) |

## Results (2000 ms; mean ± SD over 3 seed-pairs; ratios with bootstrap 95% CI; paper Table 4)

| Rule | Female % fired | Male % fired | M/F ratio |
|---|---|---|---|
| linear, w_syn = 0.1 | 1.35 ± 0.29% | 35.20 ± 0.68% | **26.1× [21.9, 33.7]** |
| lognormal σ=0.5, mean-matched | 2.15 ± 0.44% | 36.75 ± 1.00% | 17.1× [14.2, 21.4] |
| lognormal σ=1.0, mean-matched | 2.32 ± 0.11% | 38.32 ± 0.59% | 16.5× [15.8, 17.2] |
| lognormal σ=1.6, mean-matched | 2.81 ± 0.33% | 40.93 ± 0.35% | 14.5× [13.4, 16.7] |
| lognormal σ=0.5, raw w_syn=0.1 | 3.98 ± 2.07% | 38.12 ± 2.97% | 9.6× [6.3, 18.6] |
| lognormal σ=1.6, raw w_syn=0.1 | 45.04 ± 0.49% | 79.03 ± 0.16% | **1.75× [1.74, 1.78]** |
| log1p | 1.00 ± 0.00% | 1.00 ± 0.00% | 1.0× (drive floor) |
| sqrt | 1.00 ± 0.00% | 1.00 ± 0.00% | 1.0× (drive floor) |

## Interpretation

1. **The gap's magnitude is regime-dependent, and the regime is stated per number.**
   Under log1p and sqrt transforms (which compress high-synapse-count connections),
   both brains collapse to the 1.00 ± 0.00% drive floor and the gap vanishes. In the
   linear threshold regime the ratio peaks at **26.1× (95% CI 21.9–33.7)**; at the
   saturated literature-matched anchor (σ = 1.6, raw w_syn = 0.1) it compresses to
   **1.75× [1.74, 1.78]**.

2. **The gap is driven by high-synapse-count connections.** The male's ~2× connection
   density is concentrated in a subset of high-count edges. When those edges are damped
   (log1p/sqrt), the male behaves like the female; when they are amplified (linear),
   the male runs away. The compression to 1.75× at the σ = 1.6 anchor comes from
   *gain*: raising mean |w| ~3.6× pushes the female past her ignition threshold
   (2.81% → 45.04%) far more than the male (40.93% → 79.03%).

3. **Dispersion is not the mechanism.** With mean weight pinned to the linear baseline,
   dispersion alone (σ from 0.5 to 1.6) leaves the ratio nearly unchanged
   (17.1× → 14.5×; paper §3.4).

4. **The scale-free statement is the recruitment ladder.** The male reaches equal
   recruitment at ~3–3.5× lower w_syn (3.0× on the first matched ladder pair, ≈3.5×
   interpolated on the second; paper §3.5, Table 5). At the saturated σ = 1.6 anchor
   the log-gap splits 58% specific wiring / 42% degree/density under degree-preserving
   DES rewiring (paper §3.3).

## What this means for the paper

The study result (paper §3.4):

> The male CNS is intrinsically more active than the female's; the magnitude is
> regime-dependent — 26.1× [21.9, 33.7] in the linear threshold regime, 14.5–17.1×
> under mean-matched lognormal weights, 1.75× [1.74, 1.78] at the literature-matched
> σ = 1.6 anchor, and 1.0× at the log1p/sqrt drive floor. The underlying sensitivity —
> how much less drive the male network needs for equal recruitment — is stable across
> rules (~3–3.5× lower w_syn).

This is a *stronger* paper, not a weaker one: it (a) pre-empts the reviewer's #1
objection ("your weight rule is a placeholder"), (b) identifies the *mechanism*
(high-count synapses) behind the activity difference, (c) shows the finding survives
under the most defensible weight rule with its operating point stated, and (d)
reports the per-regime ratio with the w_syn-equivalence ladder as the scale-free
companion (paper §3.5).

## Caveats
- Four ladder cells (male w_syn 0.01, 0.03; female 0.02, 0.04) are single-seed (n=1)
  for that cell (paper §2.6, Table 5).
- σ = 1.6 is the literature-matched anchor (SD(log|w|) ≈ 1.83, matching the fitted
  spread); σ = 1.83 as a draw dispersion would overshoot the fitted total spread
  (SD(log|w|) ≈ 2.0), and the 3-seed probe there compresses the ratio further to
  1.47× [1.44, 1.50] (paper §2.4).
- With three seed-pairs, bootstrap CIs are within-cell spread indicators rather than
  resolved sampling distributions (paper §2.6).

Full aggregated values: `results/ssot_synthesis.md`; interpretation:
`paper/preprint.md` §2.4, §3.4, §3.5 (Tables 4, 5).