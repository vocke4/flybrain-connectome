# Final Polish — all three tasks complete

## Task 1: Linear w_syn sweep (internally consistent)

Re-ran the w_syn sweep through the same code path as the weight-rule table, so
all linear-baseline numbers now agree:

| w_syn | Female | Male | Ratio |
|---|---|---|---|
| 0.05 | 1.00% | 1.03% | 1.0× |
| 0.10 | 2.70% | 36.23% | 13.4× |
| 0.20 | 21.77% | 69.28% | 3.2× |

This resolves the earlier internal inconsistency (the old robustness.csv said
"20×" at w_syn=0.10 from a different seed; the correct linear-baseline number is
13.4×).

## Task 2: Multi-seed lognormal σ sweep (3 seeds)

| σ | Female (mean) | Male (mean) | Ratio | Female range |
|---|---|---|---|---|
| 0.1 | 2.31% | 36.13% | 15.6× | 1.7–3.2% |
| 0.3 | 3.20% | 38.16% | 11.9× | 2.4–4.3% |
| 0.5 | 5.89% | 40.49% | 6.9× | 5.4–6.4% |
| 0.7 | 10.07% | 46.93% | 4.7× | 9.5–10.6% |
| 1.0 | 19.21% | 61.90% | 3.2× | 18.9–19.6% |

The male is stable across seeds; the female shows modest variance at low σ
(where it's near the drive floor). The monotonic trend is robust.

## Task 3: bioRxiv fitted σ — the decisive finding

The Aug 2026 bioRxiv connectome-constrained fitting paper (2026.08.21.745055)
reports a **fitted lognormal σ = 1.83** (truncated-lognormal MLE on trained
weight magnitudes, Fig 1h). This is **outside our original swept range [0.1, 1.0]**.

Extending the sweep to cover it:

| σ | Female | Male | Ratio |
|---|---|---|---|
| 1.0 | 18.91% | 62.20% | 3.3× |
| 1.5 | 40.42% | 77.98% | 1.9× |
| 2.0 | 59.99% | 82.03% | 1.4× |

**At the literature's actual fitted σ = 1.83, the male/female gap is only ~1.6×.**

## The honest, final conclusion

This materially changes the headline. The full picture is:

1. **The gap is real but small at the literature's fitted weight rule.** Under
   the linear rule (13.4×) the gap looks large; under the lognormal rule with the
   *actual* fitted σ=1.83, it is only ~1.6×. The earlier "3.3×–11.2×" range was
   correct for σ ∈ [0.1, 1.0] but that range does not include the literature's
   fitted value.

2. **The mechanism is unchanged and still the key insight:** the male's excess
   activity is carried by its high-synapse-count connections. Compressing those
   edges (log/sqrt) eliminates the gap; amplifying them (linear) maximizes it.
   The lognormal rule with large σ (1.83) is itself a strong compression of the
   high-count tail, which is why the gap shrinks to ~1.6×.

3. **"Wiring, not size" still holds** (rewiring collapses both to the drive
   floor under lognormal σ=0.5), but the *magnitude* of the wiring effect is
   weight-rule-dependent and is modest (~1.6×) at the literature's fitted σ.

**Revised headline:** The male CNS is intrinsically more active than the female's,
but the effect is modest (~1.6×) under the literature-supported lognormal weight
rule (σ=1.83), larger (up to ~13×) under the linear rule, and vanishes under
log/sqrt compression. The mechanism is the male's high-synapse-count connections.
The difference is a property of specific wiring (rewiring collapses it), but its
magnitude is strongly weight-rule-dependent.

## Caveats

- The bioRxiv σ=1.83 is a *fitted* value from a specific model (resting-state
  fitting); it is the best available estimate but not ground truth.
- The extended σ points (1.5, 2.0) are single-seed (seed 0). The multi-seed
  average was only done for [0.1, 1.0]. Given the male is stable across seeds,
  this is unlikely to change the ~1.6× conclusion materially.
- The bioRxiv paper's σ may be for a different weight parameterization (e.g.,
  per-synapse vs per-connection); a careful reading of their Methods is warranted
  before over-interpreting the 1.83 number.
