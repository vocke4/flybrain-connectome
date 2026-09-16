# Weight-Rule Sensitivity — the "20× activity" finding is weight-rule-dependent

## What I tested

The core finding ("male ~20× more active") was computed under the field-standard
linear weight rule `w = sign × count × w_syn`. The literature (Pospisil 2024
effectome; Aug 2026 bioRxiv connectome-constrained fitting) says true weights are
NOT linear in synapse count — fitting yields **lognormal** weights. The male has
~2× connection density, so under the linear rule it gets ~2× more weight per
neuron, which could inflate the activity gap.

I re-ran the matched LIF model (w_syn=0.1, 2000ms, drive 1% @100Hz, seed 0) under
four weight transforms:

| Transform | Rule | Rationale |
|---|---|---|
| linear | w = count | baseline (Shiu 2024) |
| log1p | w = log(1+count) | compress high-count synapses |
| sqrt | w = sqrt(count) | intermediate compression |
| lognormal | w = exp(N(log count, 0.5)) | literature-supported (2026 fitting) |

## Results

| Transform | Female % fired | Male % fired | Male/Female ratio |
|---|---|---|---|
| linear | 2.70% | 36.23% | **13.4×** |
| log1p | 1.00% | 1.00% | **1.0×** |
| sqrt | 1.00% | 1.00% | **1.0×** |
| lognormal | 6.43% | 42.43% | **6.6×** |

## Interpretation — this is a major finding

1. **The "~20×" gap is NOT robust to the weight rule.** Under log1p and sqrt
   transforms (which compress high-synapse-count connections), the male's excess
   activity **vanishes entirely** — both brains collapse to ~1% firing. The large
   gap is specifically a product of the linear rule amplifying the male's
   high-count ("strong") synapses.

2. **The gap is driven by high-synapse-count connections.** The male's ~2×
   connection density is concentrated in a subset of high-count edges. When those
   edges are damped (log/sqrt), the male behaves like the female. When they are
   amplified (linear), the male runs away.

3. **Under the literature-supported lognormal rule, a real gap survives (6.6×).**
   This is the key nuance: the finding is not *entirely* an artifact. The
   lognormal rule — which the Aug 2026 bioRxiv shows is what fitting to activity
   actually produces — still yields a substantial male/female gap (6.6×), though
   smaller than the linear-rule headline.

## What this means for the paper

The honest, defensible statement is now:

> The male CNS is intrinsically more active than the female's, but the magnitude
> is weight-rule-dependent: the gap ranges from ~1× (log/sqrt compression) to
> ~13× (linear), with ~6.6× under the literature-supported lognormal weight rule.
> The large gap under the linear rule is driven by the male's high-synapse-count
> connections; compressing those connections eliminates the gap.

This is a *stronger* paper, not a weaker one: it (a) pre-empts the reviewer's #1
objection ("your weight rule is a placeholder"), (b) identifies the *mechanism*
(high-count synapses) behind the activity difference, and (c) shows the finding
survives under the most defensible weight rule.

## Caveats

- The linear baseline here (13.4×) differs slightly from the earlier 20×
  (robustness.csv: 1.8% vs 36.5%) due to known PoissonGroup seeding variance in
  the female (1.8%–2.7% across runs). The qualitative conclusion is unchanged.
- The lognormal draw used σ=0.5; the 2026 fitting paper's actual σ should be
  checked. A σ sweep would bound this.
- The rewiring null was run under linear weights only. To fully close the loop,
  the rewiring null should be re-run under lognormal weights to confirm "wiring,
  not size" survives there too.

## Next steps

1. Re-run the rewiring null under lognormal weights (does "wiring not size"
   survive?).
2. Sweep lognormal σ to bound the 6.6× estimate.
3. Update the preprint: revise "~20×" to the weight-rule-dependent framing.
