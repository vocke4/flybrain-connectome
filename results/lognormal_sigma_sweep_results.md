# Lognormal σ sweep + DES null — dispersion is not the mechanism; the anchor is σ = 1.6

## 1. σ = 0.5 raw anchor and DES null under lognormal weights

Degree-preserving double-edge-swap (DES) rewiring — preserving each network's exact
in/out-degree sequences while randomizing which edges exist — is tested under the
lognormal rule (σ = 0.5, raw w_syn = 0.1, three seed-pairs for the real networks):

| Network | % fired (lognormal σ=0.5, raw w_syn=0.1) |
|---|---|
| Female real | 3.98 ± 2.07% |
| Male real | 38.12 ± 2.97% |

At the saturated σ = 1.6 anchor the DES null raises both networks (female
45.04 ± 0.49% → 72.11 ± 0.21%; male 79.03 ± 0.16% → 91.46 ± 0.03%; 3 build × 3
simulation seeds, n = 9 per sex), so specific wiring reads net-suppressive there: it
destroys 58% of the log-scale gap, with the share inverting near threshold (from
−233% at w_syn = 0.04 through +30% at 0.06 to +58% at the anchor; paper §3.3, §3.4,
Table 3b). The female's σ = 0.5 raw anchor (3.98 ± 2.07%; seeds 6.15/2.02/3.77) is
itself threshold-bimodal across seeds and is reported with that spread stated.

## 2. Mean-matched σ sweep (dispersion isolated from gain)

A raw σ sweep confounds dispersion with mean gain (E[|w|] grows as exp(σ²/2)). The
mean-matched sweep sets w_syn(σ) = 0.1 · exp(−σ²/2), holding E[|w|] fixed while
varying only dispersion (three seed-pairs per row; paper §3.4, Table 4):

| σ | Female | Male | Ratio |
|---|---|---|---|
| 0.5 (mean-matched) | 2.15 ± 0.44% | 36.75 ± 1.00% | 17.1× [14.2, 21.4] |
| 1.0 (mean-matched) | 2.32 ± 0.11% | 38.32 ± 0.59% | 16.5× [15.8, 17.2] |
| 1.6 (mean-matched) | 2.81 ± 0.33% | 40.93 ± 0.35% | 14.5× [13.4, 16.7] |

With mean weight pinned to the linear baseline, dispersion alone (σ from 0.5 to 1.6)
leaves the ratio nearly unchanged (17.1× → 14.5×): **dispersion is not the mechanism**.

## 3. The raw anchors: literature-matched σ = 1.6 and the σ = 1.83 overshoot probe

At raw w_syn = 0.1 the ratio compresses because of *gain*, not dispersion: raising
mean |w| ~3.6× pushes the female network past its ignition threshold far more than the
male (paper §3.4, Table 4):

| Rule (raw w_syn = 0.1) | Female | Male | Ratio |
|---|---|---|---|
| lognormal σ = 0.5 | 3.98 ± 2.07% | 38.12 ± 2.97% | 9.6× [6.3, 18.6] |
| lognormal σ = 1.6 (literature-matched anchor) | 45.04 ± 0.49% | 79.03 ± 0.16% | **1.75× [1.74, 1.78]** |
| lognormal σ = 1.83 (overshoot probe) | 55.17 ± 1.05% | 80.93 ± 0.13% | 1.47× [1.44, 1.50] |

**σ = 1.6 is the literature-matched anchor.** The connectome-constrained fitting
literature (bioRxiv 2026.08.21.745055) reports fitted weight log-spread
SD(log w) = 1.83; matching that spread requires σ ≈ 1.54 (male) / 1.64 (female), so
σ = 1.6 reproduces the fitted total log-spread at w_syn = 0.1 (SD(log|w|) ≈ 1.83;
paper §2.4).

**σ = 1.83 is the overshoot probe, not the anchor:** σ is the per-edge *draw*
dispersion, and setting it to 1.83 inflates the total spread to SD(log|w|) ≈ 2.0,
overshooting the fitted value by stacking draw dispersion on top of count dispersion.
The 3-seed probe confirms the expected reading: the ratio compresses further to
1.47× [1.44, 1.50] (male 80.93 ± 0.13%, female 55.17 ± 1.05%), confirming the anchor
choice is not innocuous; σ = 1.6 is retained (paper §2.4).

## 4. What this means for the paper

The finding is robust and quantified per regime:

1. **Mechanism identified:** the gap is carried by the male's high-synapse-count
   connections (log1p/sqrt compression collapses both sexes to the 1.00 ± 0.00% drive
   floor; the linear rule amplifies high-count synapses — paper §3.1).
2. **Dispersion is not the mechanism:** under mean-matched lognormal weights the ratio
   barely moves across σ (17.1× → 14.5×). The compression to 1.75× at the σ = 1.6
   anchor comes from mean gain, which pushes the female past ignition
   (2.81% mean-matched → 45.04% raw) far more than the male (40.93% → 79.03%).
3. **The honest headline:** the recruitment *ratio* depends on the operating point
   (26.1× [21.9, 33.7] in the linear threshold regime; 14.5–17.1× mean-matched;
   1.75× [1.74, 1.78] at the literature-matched anchor; 1.47× at the σ = 1.83
   overshoot probe), while the underlying sensitivity — how much less drive the male
   network needs for equal recruitment — is stable across rules (~3–3.5× on the
   w_syn-equivalence ladder; paper §3.5).

The honest summary (paper §3.4):

> The male CNS is intrinsically more active than the female's. The magnitude is
> regime-dependent — 26× in the linear threshold regime, 14.5–17× under mean-matched
> lognormal weights, 1.75× at the literature-matched σ = 1.6 anchor — because the
> female sits closer to her ignition threshold; the male reaches equal recruitment at
> ~3–3.5× lower w_syn. Dispersion alone does not move the ratio; gain does.

## 5. Caveats
- Four ladder cells (male w_syn 0.01, 0.03; female 0.02, 0.04) are single-seed (n=1)
  for that cell (paper §2.6, Table 5).
- The DES decomposition is measured at the saturated anchor only; its share inverts
  near threshold (Table 3b), and the w_syn = 0.04–0.05 DES cells are single-seed
  readings on the female's knife-edge transition.
- DES rewiring remixes E/I composition (itself suppressively organized), confounding
  wiring specificity with E/I arrangement in this null (paper §3.3, §3.7).
- With three seed-pairs, bootstrap CIs are within-cell spread indicators rather than
  resolved sampling distributions (paper §2.6).

Full aggregated values: `results/ssot_synthesis.md`; interpretation:
`paper/preprint.md` §2.4, §3.4, §3.5 (Tables 2, 4, 5, 3b).