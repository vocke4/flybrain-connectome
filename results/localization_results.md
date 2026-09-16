# Localization Results — do dimorphic circuits drive the gap?

## Test
Silence the sexually-dimorphic neurons (zero their synapses) and re-run the
matched LIF model. If the male's excess activity collapses, dimorphic circuits
are the mechanistic driver.

## Dimorphic neuron counts
- Male MCNS: 3,900 dimorphic neurons / 164,371 total (2.4%)
  (dimorphism flag OR fru/dsx high expression)
- Female BANC: 3,803 dimorphic neurons / 169,078 total (2.2%)

## Result
| Network | Real | Dimorphic silenced | Change |
|---|---|---|---|
| Male MCNS | 36.3% fire | 31.6% fire | −13% |
| Female BANC | 2.7% fire | 2.6% fire | −4% |

## Interpretation — a NEGATIVE result that matters
Silencing the dimorphic circuits (2.4% of neurons) only reduces male activity by
13% (36.3% → 31.6%). The male's ~20x excess activity is therefore NOT
concentrated in the small set of dimorphic neurons — it is a DISTRIBUTED property
of the whole male CNS wiring.

This is scientifically important: it rules out the naive hypothesis that
"courtship/aggression circuits explain the sex difference." Instead, the male
CNS's higher excitability is a whole-brain property, consistent with its ~2x
connection density being spread across the entire connectome, not localized to
sex-specific circuits.

## What this means for the paper
The finding is now:
1. Male CNS is ~20x more active (wiring, not size — null models).
2. Male propagates info ~44x more effectively (transfer entropy).
3. This is a DISTRIBUTED whole-brain property, NOT localized to dimorphic circuits
   (localization test: silencing 2.4% dimorphic neurons only −13% activity).

This is a cleaner, more honest story than "sex circuits did it." The male brain's
excitability is an emergent property of its global wiring, not a few specialized
neurons.

## Caveat
- The dimorphic flag coverage is incomplete (many neurons have NaN dimorphism).
  The 2.4% figure is a lower bound on true dimorphic neurons.
- fru/dsx expression is a proxy for dimorphism, not definitive.
