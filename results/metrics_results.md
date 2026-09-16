# Dynamical Metrics — Male vs Female (2000ms, w_syn=0.1, seeded)

| Metric | Female BANC | Male MCNS | Interpretation |
|---|---|---|---|
| Neurons fired | 2.7% | 36.3% | male ~13x more active |
| Mean firing rate | 8.1 Hz | 106.5 Hz | male ~13x |
| **Branching ratio (σ)** | 0.9997 | 1.0000 | **both at criticality** |
| **CV of ISI** | 1.01 | 2.99 | male much more bursty/irregular |
| **Transfer entropy** | 0.0005 | 0.0221 | **male 44x more information flow** |
| **Participation ratio (dim)** | 6.08 | 1.28 | male lower-dimensional (more synchronized) |

## Key findings

1. **Both brains sit at criticality** (branching ratio σ ≈ 1.0). This is a known
   property of the fly connectome (rich-club, near-critical) and validates the
   model — it reproduces the expected critical regime for BOTH sexes.

2. **The male brain has 44x higher transfer entropy** (0.022 vs 0.0005). This is
   the most interesting result: the male CNS propagates information between
   neurons far more effectively than the female. This is a *qualitative* difference
   in information processing, not just a magnitude difference in activity.

3. **The male brain is lower-dimensional** (participation ratio 1.28 vs 6.08).
   Male activity is more synchronized/correlated (fewer independent modes), while
   female activity is more distributed across independent dimensions.

4. **The male brain is more bursty** (CV of ISI 2.99 vs 1.01). Male firing is
   irregular/bursty; female firing is near-Poisson (CV≈1).

## Synthesis
The male CNS is not merely "more active" — it is a *qualitatively different*
dynamical system: critical (like the female) but with higher information flow,
lower dimensionality, and burstier firing. This is consistent with the male CNS
having ~2x connection density and a wiring topology optimized for propagating
activity (e.g., courtship song circuits, aggression circuits).

## Caveats
- Avalanche size/duration is degenerate (male = 1 continuous avalanche at 1ms bins;
  activity never drops to zero). Need threshold-based avalanche definition or
  shorter bins, OR drop avalanche in favor of branching ratio (cleaner).
- Transfer entropy is a simplified binned estimate (200 random pairs, 2ms bins).
  Should be validated against a proper TE estimator (e.g., JIDT).
- Participation ratio subsampled to 5000 neurons (memory bound).
- Single w_syn point; should confirm metrics are stable across the critical regime.
