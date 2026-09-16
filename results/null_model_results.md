# Null-Model Results (2000ms, w_syn=0.1, drive 1% @100Hz)

| Network | Neurons fired | Mean rate | Total spikes |
|---|---|---|---|
| **Female BANC (real)** | 2.4% | 8.8 Hz | 36k |
| Female BANC (rewired) | 1.0% | 8.8 Hz | 15k |
| Female BANC (sign-shuffled) | 19.1% | 51.3 Hz | 1.66M |
| **Male MCNS (real)** | 36.1% | 101 Hz | 5.98M |
| Male MCNS (rewired) | 1.1% | 8.8 Hz | 16k |
| Male MCNS (sign-shuffled) | 59.8% | 75.7 Hz | 7.40M |

## Three findings

1. **Wiring, not size, drives activity.** Rewiring (configuration model: preserves
   degree + weight/sign distribution, destroys specific connections) collapses BOTH
   brains to the same low-activity state (~1% fire, 8.8 Hz). The male's 36% activity
   is therefore NOT a size/degree artifact — it is a property of its specific wiring.

2. **The male brain is intrinsically ~15x more active than the female** (36.1% vs
   2.4% neurons firing), and this difference vanishes under rewiring (both → ~1%).
   This is the core sex-difference signal.

3. **E/I balance suppresses runaway activity in both.** Sign-shuffling (keeps wiring,
   randomizes excitatory/inhibitory) INCREASES activity in both (female 2.4%→19%,
   male 36%→60%). The real connectomes' sign arrangement is tuned to damp activity
   relative to chance — a classic excitatory/inhibitory balance result.

## Interpretation
The male CNS connectome's specific wiring produces intrinsically higher excitability
than the female's, independent of size. This is consistent with the male CNS having
~2x the connection density (mean 4.81 vs 3.10 synapses/edge) AND a wiring topology
that propagates activity more effectively. The rewired-null result rules out the
"it's just bigger" objection.

## Caveats (to address before claiming)
- Configuration model preserves out-degree exactly but in-degree only in expectation.
- Single seed; need multiple rewiring seeds for a distribution, not a point estimate.
- w_syn=0.1 is one point in parameter space; need a sweep to show robustness.
- Drive is uniform random 1%; should test sensitivity to drive location (sensory vs motor).
