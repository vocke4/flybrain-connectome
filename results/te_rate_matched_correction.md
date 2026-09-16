# Transfer Entropy Rate-Matched Control — CRITICAL CORRECTION

## The problem
The male brain fires 53.2 Hz/neuron vs female 4.1 Hz/neuron (13x). Transfer
entropy is naturally inflated by firing rate, so the "44x" headline number was
suspected to be partly a rate artifact.

## The test
Rate-match the male's per-neuron firing rate down to the female's (4.1 Hz/neuron),
then recompute TE. If TE is still higher, it's a wiring property; if it collapses,
it was a rate artifact.

## Result
| Condition | Female TE | Male TE | Ratio |
|---|---|---|---|
| Baseline (raw) | 0.00051 | 0.02213 | 43.2x |
| Per-neuron rate-matched | 0.00051 | 0.00047 | **0.9x** |
| Common low rate (2 Hz) | 0.00038 | 0.00024 | 0.6x |

## Conclusion: the 44x transfer entropy was a RATE ARTIFACT.

When the male's firing rate is matched to the female's, the transfer entropy
difference vanishes (0.9x, i.e., slightly LOWER than female). The "44x more
information flow" claim is NOT supported. It was an artifact of the male firing
13x more per neuron.

## What this means for the paper

The transfer entropy claim must be REMOVED or heavily caveated. The surviving,
defensible findings are:

1. **Activity difference (~20x)** — SURVIVES rewiring (both → 1%), so it's a
   wiring property, not size. SOLID.
2. **Burstiness (CV of ISI 2.99 vs 1.01)** — CV is normalized by mean, so it's
   rate-independent. The male fires more burstily. LIKELY SOLID (should verify).
3. **Both at criticality (σ ≈ 1.0)** — SOLID, validates model.

The transfer entropy and participation ratio claims need re-examination:
- TE: DEAD (rate artifact, confirmed).
- Participation ratio: lower dimensionality in male could ALSO be a rate artifact
  (higher rate → more synchronized → lower PR). Needs a rate-matched check.

## Lesson
This is exactly why the rigor pass matters. The "44x information flow" was the
most exciting number, and it was wrong. Better to catch it now than in review.
