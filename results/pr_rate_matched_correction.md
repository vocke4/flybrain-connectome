# Participation Ratio Rate-Matched Control — CONFIRMED (vectorized re-run)

## Result (re-verified 2026-09-11, vectorized, no OOM)

| Condition | Female | Male |
|---|---|---|
| Baseline (raw) | 6.08 | 1.28 (looks "lower-dimensional") |
| Per-neuron rate-matched (4.1 Hz/neuron) | 6.08 | **43.10** |
| Common low rate (2.0 Hz) | 19.52 | 56.32 |

## Interpretation

1. **The raw "male is lower-dimensional" claim is DEAD.** It was a rate artifact:
   the male fires 13x more per neuron, saturating population activity into a
   single shared mode (PR 1.28). When slowed to the female's rate, the male is
   actually MORE high-dimensional (43 vs 6).

2. **BUT the reversal is itself confounded.** Spike thinning decorrelates neurons
   and inflates PR for BOTH sexes — note the female's own PR jumps from 6.08 to
   19.52 when thinned to 2 Hz. So the "43 vs 6" reversal is not a clean wiring
   result either; it's partly a thinning artifact.

3. **The honest conclusion:** dimensionality is NOT a defensible finding in either
   direction from post-hoc thinning. The only way to settle it is a proper
   matched-rate SIMULATION (re-run the male model at a matched drive rate so it
   fires at the female's rate naturally, no thinning).

## What this means for the paper

- PR claim: RETRACTED (both the "lower-dimensional" claim AND the "reversal" are
  confounded). Dimensionality is left to future work with a matched-rate sim.
- This is consistent with the preprint's current framing: PR is listed as
  "artifact (reversed)" but flagged as requiring a proper matched-rate simulation.
