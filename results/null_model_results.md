# Null-Model Results (2000ms, w_syn=0.1, drive 1% @100Hz)

Two degree-preserving nulls probe what carries the sex gap: **DES rewiring**
(double-edge-swap; preserves each network's exact in/out-degree sequences while
randomizing which edges exist) and **sign-shuffling** (preserves all wiring and E/I
counts while randomizing signs). Real-network and null conditions are sampled over
independent (weight, simulation) seed-pairs in the append-only SSOT ledger
(`results/ssot/ssot_results.jsonl`; aggregated in `results/ssot_synthesis.md`).

## Results at the linear anchor (w_syn = 0.1)

| Network | Recruitment real | Recruitment DES-rewired | Recruitment sign-shuffled |
|---|---|---|---|
| **Female BANC** | 1.35 ± 0.29% | 1.0% (n=1) | 13.16 ± 10.50% |
| **Male MCNS** | 35.20 ± 0.68% | 1.1% (n=1) | 61.12 ± 2.88% |

(Recruitment = % neurons firing ≥1 spike in 2000 ms; n=1 cells are single-seed for
that cell. Population rates: female 0.07 ± 0.04 Hz real / 4.50 ± 3.87 Hz
sign-shuffled; male 15.50 ± 3.85 Hz real / 27.23 ± 3.03 Hz sign-shuffled.)

## Findings

1. **Sign structure is net-suppressive in both sexes.** Shuffling excitatory/inhibitory
   signs (preserving all wiring and sign counts) *increases* recruitment in both:
   female 1.35 → 13.16 ± 10.50%, male 35.20 → 61.12 ± 2.88% (paper Table 7). The real
   connectomes' sign arrangement is tuned to damp activity relative to chance — a
   classic E/I-balance result; inhibition is not decorative. The female's shuffled
   network is bimodal across seeds (19.3%, 19.2%, 1.0%): it sits at an ignition
   threshold where two of three seed draws escape the drive floor and one does not.

2. **DES rewiring at the saturated σ = 1.6 anchor raises both networks, so specific
   wiring reads net-suppressive there.** Under the literature-matched lognormal rule
   (σ = 1.6, w_syn = 0.1; DES: 3 build × 3 simulation seeds, n = 9 per sex):

   **Table 3 (paper §3.3). Real vs DES-rewired networks (σ = 1.6, w_syn = 0.1).**

   | Network | Recruitment real | Recruitment DES | log-gap destroyed |
   |---|---|---|---|
   | Female BANC | 45.04 ± 0.49% | 72.11 ± 0.21% | 0.471 log units |
   | Male MCNS | 79.03 ± 0.16% | 91.46 ± 0.03% | 0.146 log units |

   - Real log-gap: ln(79.03/45.04) = **0.562**; DES log-gap: ln(91.46/72.11) = **0.238**.
   - **Specific wiring accounts for (0.562 − 0.238)/0.562 = 58% of the sex gap;
     degree/density structure accounts for 42%** (log-ratio scale; bootstrapped over
     seed-pairs and DES builds: 57.7% [56.9, 58.5]; on the linear percentage-point
     scale the split reads 43/57). Rewired ratio: 1.27× [1.27, 1.27].
   - Two-fifths of the gap survives on degree/density alone, so the difference is not
     purely a wiring property — and both brains' specific wiring damps relative to
     their own degree structure at this operating point (female +27 points under
     rewiring, male +12).

3. **The decomposition is operating-point-dependent, and the share inverts near
   threshold.** Re-simulating the same DES edge sets across w_syn, the specific-wiring
   share slides from −233% (w_syn = 0.04) through +30% (0.06) to +58% (0.10) (paper
   Table 3b). The DES female sits on a knife-edge transition (1.44% at w = 0.04 rising
   to 46.15% at w = 0.06, a 33× jump for a 1.5× weight change); the extreme negative
   shares at w_syn = 0.04–0.05 are single-seed readings on that knife-edge — the sign
   inversion is plausible but indicative only, not seed-replicated.

4. **The recruitment magnitude is regime-dependent.** At the linear anchor the
   M/F ratio is 26.1× [21.9, 33.7]; under mean-matched lognormal weights 14.5–17.1×;
   at the σ = 1.6 anchor 1.75× [1.74, 1.78]; at the log1p/sqrt drive floor 1.0×
   (paper §3.4, Table 4). The scale-free statement is the recruitment ladder: the male
   reaches equal recruitment at ~3–3.5× lower w_syn (paper §3.5).

## Interpretation
The sex difference is carried jointly by which edges exist and how many each neuron
has: at the saturated anchor, 58% of the log-gap is specific-wiring and 42%
degree/density, with the male's ~2× connection density (mean 4.81 vs 3.10
synapses/edge) supplying the degree component. Both networks' real sign arrangements
are net-suppressive relative to chance. The female's specific wiring damps harder per
unit of degree (0.471 vs 0.146 log units) at the anchor — an anchor-specific,
scale-dependent observation, not a general property.

## Caveats
- **E/I confound in the DES null:** DES rewiring permutes which edges exist and thereby
  remixes each network's excitatory/inhibitory composition, which §3.7 shows is itself
  suppressively organized; wiring specificity and E/I arrangement are confounded in
  this null, and the female's suppressive-wiring reading is bounded by it
  (paper §3.3, §3.7).
- DES preserves in- and out-degree sequences *exactly* (verified post-swap for every
  seed; acceptance rates 99.1% female, 98.7% male). The n=1 linear-regime rewired cells
  above predate the 3-build-seed DES design and are single-seed for that cell.
- w_syn = 0.1 is one point in parameter space; the share inversion near threshold is
  single-seed (Table 3b). Drive is uniform random 1%; drive-location sensitivity
  (sensory vs motor) remains untested.
- Amine sign conventions are a coarse modeling choice; the sign-structure conclusion is
  conditional on them (paper §2.2, Limitations).

Current aggregated values: `results/ssot_synthesis.md`; interpretation:
`paper/preprint.md` §3.3, §3.4, §3.7 (Tables 3, 3b, 7).