# Robustness Results

## w_syn sweep (real networks, 2000 ms, σ = 1.6 lognormal)

Recruitment ladder across w_syn at the literature-matched lognormal rule
(paper §3.5, Table 5). Headline cells are 3-seed (mean ± SD over the three
(weight, simulation) seed-pairs); four low-w_syn cells are single-seed (n=1) for
that cell. The ratio is regime-dependent: 1.0× at the drive floor, maximal near the
ignition threshold, compressing toward 1× as both sexes saturate (paper §3.4).

| w_syn | Female BANC | Male MCNS | Notes |
|---|---|---|---|
| 0.01 | n/a | 1.96% (n=1) | single-seed cell |
| 0.02 | 1.73% (n=1) | 29.13 ± 0.50% | male 3.0× lower w_syn at equal recruitment (29.13 vs 28.08, within 1.1 pp) |
| 0.03 | n/a | 44.13% (n=1) | single-seed cell |
| 0.04 | 16.57% (n=1) | n/a | single-seed cell |
| 0.05 | n/a | 64.91 ± 0.06% | |
| 0.06 | 28.08 ± 0.22% | n/a | |
| 0.10 (anchor) | 45.04 ± 0.49% | 79.03 ± 0.16% | ratio 1.75× [1.74, 1.78] |
| 0.15 | 58.04 ± 0.48% | n/a | |

The male reaches equivalent recruitment at ~3–3.5× lower w_syn: 3.0× on the first
matched ladder pair (male 0.02 → 29.13 ± 0.50% vs female 0.06 → 28.08 ± 0.22%), and
≈3.5× interpolated on the second (male 0.05 → 64.91 ± 0.06%; the female ladder puts
her at 64.91% near w_syn ≈ 0.18). This w_syn-equivalence is the cleanest scale-free
statement of the sex difference.

## Linear anchor (w_syn = 0.1, three seed-pairs)

| Network | % fired | Population rate (Hz) | Branching | CV of ISI |
|---|---|---|---|---|
| Female BANC | 1.35 ± 0.29% | 0.07 ± 0.04 | 0.999 ± 0.000 | 1.04 ± 0.22 |
| Male MCNS | 35.20 ± 0.68% | 15.50 ± 3.85 | 1.001 ± 0.002 | 2.74 ± 0.47 |

Linear-rule ratio: **26.1× (95% CI 21.9–33.7)**. The ratio is regime-dependent across
weight rules — 14.5–17.1× under mean-matched lognormal weights, 1.75× [1.74, 1.78] at
the σ = 1.6 anchor, 1.0× at the log1p/sqrt drive floor (paper §3.4, Table 4) — while
the direction is invariant (43/43 matched male ≥ female pairs in the ledger).

## DES-rewired null (w_syn = 0.1)

At the σ = 1.6 anchor, degree-preserving double-edge-swap rewiring raises both
networks (female 45.04 → 72.11 ± 0.21%, male 79.03 → 91.46 ± 0.03%; 3 build × 3
simulation seeds, n = 9 per sex), splitting the log-gap 58% specific wiring / 42%
degree/density (paper §3.3, Table 3). The share is operating-point-dependent: it runs
from −233% (w_syn = 0.04) through +30% (0.06) to +58% (0.10), with the sign inverting
near threshold (paper Table 3b).

## Conclusion
The core finding is robust across the parameter space in direction, and quantified in
magnitude per regime: the male CNS recruits more of itself than the female at matched
drive under every weight rule tested, reaching equal recruitment at ~3–3.5× lower
w_syn. The gap is monotone in w_syn within each rule and not a single-point artifact;
its magnitude is a function of operating point (26.1× [21.9, 33.7] in the linear
threshold regime; 1.75× near saturation), reported per-regime in paper §3.4.

## Remaining caveats
- Four ladder cells (male w_syn 0.01, 0.03; female 0.02, 0.04) are single-seed (n=1).
- Drive is uniform random 1%; sensitivity to drive location (sensory vs motor) is
  untested.
- The higher-order metrics (avalanche/TE/dimensionality) are rate-confounded under
  post-hoc thinning and carry no sex-difference evidence here (paper §3.8); the
  branching estimator carries no criticality information at these drive densities
  (paper §3.5).

Full aggregated values: `results/ssot_synthesis.md`; interpretation:
`paper/preprint.md` §3.4, §3.5 (Tables 4, 5, 3b).