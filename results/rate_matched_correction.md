# Rate-Matched Controls — MAJOR CORRECTION

## What I tested
The male fires 53.2 Hz/neuron vs female 4.1 Hz/neuron (13x). Any information or
dimensionality measure is naturally confounded by firing rate. I rate-matched the
male's per-neuron firing rate down to the female's and recomputed.

## Results

### Transfer entropy — DEAD (rate artifact)
| Condition | Female | Male | Ratio |
|---|---|---|---|
| Baseline | 0.00051 | 0.02213 | 43x |
| Rate-matched | 0.00051 | 0.00047 | 0.9x |

The "44x more information flow" claim does NOT survive rate matching. It was an
artifact of the male firing 13x more per neuron.

### Participation ratio (dimensionality) — DEAD, and REVERSED
| Condition | Female | Male |
|---|---|---|
| Baseline | 5.89 | 1.28 (looks "more synchronized") |
| Rate-matched | 5.89 | 43.16 (actually MORE high-dimensional) |

The "male is lower-dimensional" claim was ALSO a rate artifact. When the male is
slowed to the female's rate, it is actually MORE high-dimensional (43 vs 6
independent modes). The apparent "synchronization" was just the male firing so
fast that everything saturated into one mode.

## What SURVIVES

1. **Activity difference (~20x)** — survives rewiring (both → 1%), so it's a
   wiring property, not size. SOLID.
2. **Both at criticality (σ ≈ 1.0)** — SOLID, validates model.
3. **Burstiness (CV of ISI 2.99 vs 1.01)** — CV is normalized by mean, so it's
   rate-independent. LIKELY SOLID (should still verify with rate-matched check).

## The honest revised finding

The male CNS is intrinsically ~20x more active than the female's, and this is a
property of its specific wiring (not size, not localized dimorphic circuits).
Both brains sit at criticality. The male fires more burstily.

The "qualitatively different dynamical system" narrative (higher info flow, lower
dimensionality) was BUILT ON RATE ARTIFACTS and must be retracted.

## Lesson (important)
This is exactly why the rigor pass mattered. The two most exciting numbers
("44x info flow", "lower dimensionality") were both artifacts of the male firing
13x faster. The honest finding is narrower but real: the male brain is more
active and more bursty, and that's a wiring property.

## Next steps
1. Verify CV of ISI survives rate matching (it should, but confirm).
2. Rewrite the preprint to remove the TE and PR claims, or reframe them as
   "rate-matched" (which actually shows the male is MORE high-dimensional — a
   potentially interesting finding in its own right, but needs careful framing).
3. The rate-matched PR reversal (male MORE high-dimensional at matched rate) is
   actually a NEW finding worth investigating — it suggests the male's wiring
   supports MORE independent activity modes when not saturated.
