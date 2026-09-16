# Lognormal σ sweep + rewiring null — the finding is robust

## 1. Rewiring null under lognormal weights

The original "wiring, not size" claim was established under LINEAR weights. We
re-tested it under the literature-supported LOGNORMAL rule (σ=0.5):

| Network | % fired (lognormal σ=0.5) |
|---|---|
| Female real | 6.43% |
| Male real | 42.43% |
| Female rewired | 1.05% |
| Male rewired | 1.58% |

**Result: "wiring, not size" survives the lognormal rule.** Degree-preserving
rewiring collapses both brains to ~1–1.6% (the drive floor), while the real
networks show a 6.6× gap. The male's excess activity is a property of its
specific wiring under *both* weight rules — not an artifact of the linear rule.

## 2. Lognormal σ sweep

The male/female ratio is monotonic in σ, but a substantial gap survives across
the entire plausible range:

| σ | Female | Male | Ratio |
|---|---|---|---|
| 0.1 | 3.24% | 36.46% | 11.2× |
| 0.3 | 4.34% | 39.08% | 9.0× |
| 0.5 | 6.43% | 42.43% | 6.6× |
| 0.7 | 10.59% | 48.22% | 4.6× |
| 1.0 | 18.91% | 62.20% | 3.3× |

**Result: the gap is bounded at 3.3×–11.2× across σ ∈ [0.1, 1.0].** As σ grows,
both brains become more active (larger weights → more propagation), and the
*ratio* shrinks because the female catches up — but the male is always 3–11×
more active. There is no σ at which the gap disappears.

## 3. What this means for the paper

The finding is now **robust in two independent ways**:

1. **Mechanism identified:** the gap is carried by the male's high-synapse-count
   connections (log/sqrt compression kills it; linear amplifies it).
2. **Robust under the defensible weight rule:** under lognormal weights (the
   literature-supported rule), the gap is 3.3×–11.2× depending on σ, and
   "wiring, not size" holds (rewiring collapses both).

The honest headline is now:

> The male CNS is intrinsically more active than the female's. The magnitude is
> weight-rule-dependent (1×–13× across transforms), but under the
> literature-supported lognormal rule the gap is 3.3×–11.2× across σ ∈ [0.1, 1.0],
> and degree-preserving rewiring collapses both sexes to the drive floor —
> confirming the difference is a property of specific wiring, not size.

## 4. Caveats

- The lognormal σ used by the Aug 2026 bioRxiv fitting paper should be checked
  against our range; if their fitted σ is outside [0.1, 1.0], we should extend
  the sweep.
- Single seed per σ (seed=0). A multi-seed average would tighten the estimates,
  but the monotonic trend is already clear.
- The rewiring null used the existing rewired networks (seed 0). Multi-seed
  rewiring under lognormal would strengthen it further.
