# Sex differences in whole-brain dynamics of the Drosophila CNS connectome

**A matched leaky integrate-and-fire comparison with degree-preserving, sign-shuffle, and ablation-null controls**

*Katie Grillaert and Ed Vocke*

---

## Abstract

The completion of synapse-resolution connectomes for both the female (BANC) and male (MCNS) adult *Drosophila melanogaster* central nervous system enables a direct, whole-brain comparison of sex-specific wiring through dynamics. We embed both connectomes in an identical leaky integrate-and-fire model (weights from synapse counts, signs from neurotransmitter identity, matched 1% Poisson drive) and quantify recruitment, firing rates, and criticality under a single-source-of-truth protocol: every condition is run under three independent (weight-seed, simulation-seed) pairs, and every headline ratio carries a bootstrap confidence interval. Under lognormal weights matched to the literature's fitted log-spread (SD(log w) ≈ 1.83, obtained at σ = 1.6), the male recruits 79.0 ± 0.2% of neurons in a 2 s window versus 45.0 ± 0.5% in the female — a 1.75× ratio (95% CI 1.74–1.78) — with both networks self-organized near criticality (branching ratio m = 0.98–1.005 in every condition). A degree-preserving double-edge-swap null decomposes the log-scale gap: **58% of the sex difference is destroyed by rewiring (specific wiring), 42% survives on degree/density structure alone**. Rewiring also reveals that both brains' specific wiring is net-suppressive relative to their own degree structure (female 45→72%, male 79→91% recruited). The recruitment ratio is gain-dependent — 26× (21.9–33.7) under linear weights, 14.5–17× (mean-weight-matched lognormal sweep), 1.75× at the literature-matched anchor — reflecting where on a shared critical recruitment curve each sex sits: the male reaches equivalent recruitment at 2–3× lower synaptic weight. Higher-order metrics that scale with firing rate (transfer entropy, participation ratio, CV of ISI) are shown by direct test to be highly susceptible to artifactual divergence between networks of different activity levels (§3.8). Silencing dimorphic neurons (2.4% of cells) reduces male recruitment by 8.4% relative, versus 4.9% for size-matched random ablation — a modest, distributed effect with its proper null. We release the dual-seed protocol as a reproducibility standard for connectome-dynamics comparisons.

---

## 1. Introduction

The connectome specifies the synaptic paths by which neurons can influence one another, but not the dynamics that emerge from those paths (Pospisil et al., 2024). With synapse-resolution connectomes now available for the adult female CNS (BANC; 169,078 neurons) and male CNS (MCNS; 163,511 neurons), one can ask a question that brain-only comparisons cannot answer cleanly: **when two whole nervous systems that differ in sex-specific wiring are embedded in the identical dynamical model, do they produce measurably different dynamics — and is any difference attributable to specific wiring, to degree/density structure, or to localized sex-specific circuits?**

We answer this with an intervention-first design. Rather than comparing summary statistics of spontaneous activity and post-hoc explaining them, we run matched perturbations on both networks:

1. **Weight-rule manipulations** (linear, log1p, sqrt, lognormal with matched mean or matched spread) to test whether the sex difference survives defensible weight rules;
2. **Degree-preserving double-edge-swap (DES) rewiring** of each sex's own connectome, which preserves the exact in- and out-degree sequences while destroying specific wiring — isolating the contribution of *which* edges exist from *how many* each neuron has;
3. **Sign-shuffling** to test whether excitatory/inhibitory structure is net-suppressive or net-amplifying;
4. **Size-matched random ablation** as the null for dimorphic-neuron silencing.

All experiments flow into a single append-only results ledger (`ssot_results.jsonl`); every number in this paper is traceable to that file, and every condition is sampled over independent weight and simulation seeds.

A companion methodological result shapes the paper: metrics that scale with firing rate (transfer entropy, participation ratio, CV of ISI) diverge artifactually between networks of different activity levels. Section 3.8 quantifies these rate-confounding vulnerabilities and the controls required to neutralize them — a caution that applies to any connectome-dynamics comparison in which the networks under study differ in overall activity.

---

## 2. Methods

### 2.1 Data

| Dataset | Sex | Scope | Neurons | Edges | Synapses | Mean count | SD(log count) | E/I edges |
|---|---|---|---|---|---|---|---|---|
| BANC v888 | Female | Whole CNS | 169,078 | 13,379,740 | 41.5M | 3.10 | 0.825 | 75/25 |
| MCNS v1.0 | Male | Whole CNS | 163,511 | 24,410,950 | 117.5M | 4.81 | 0.983 | 80/20 |

BANC and MCNS are the primary comparison (both whole-CNS). All data are publicly available (Janelia FlyEM, FlyWire Codex); no authentication was required. The male flat connectome was filtered to annotated neurons; neurotransmitter consensus calls map to signs (see §2.2).

### 2.2 Normalization

Each connectome was converted to a common edge list `(pre_idx, post_idx, count, sign)`, where `count` is the synapse count and `sign ∈ {+1, −1}` is derived from neurotransmitter identity:

- **Excitatory (+1):** acetylcholine, glutamate, dopamine, octopamine, tyramine
- **Inhibitory (−1):** GABA, histamine, serotonin, glycine
- **Unclear:** dropped (documented limitation; affects both sexes similarly)

### 2.3 Model

Both connectomes were embedded in an identical LIF model (Brian2, Cython codegen):

```
dv/dt = (v_rest − v)/τ  (unless refractory);  threshold v > v_th;  reset v = v_rest
```

with `v_rest = −65 mV`, `v_th = −50 mV`, `τ = 10 ms`, refractory period 2.2 ms, simulated for 2000 ms. A uniformly random 1% of neurons (1,635 male / 1,690 female) received independent Poisson drive at 100 Hz, each event depolarizing the target by 5 mV. Synapses were `w = sign · |w| · mV` with delays omitted (all-to-all chemical capture at 1 ms resolution is out of scope; see Limitations).

### 2.4 Weight transforms and the σ parameterization

Four rules map counts to weight magnitudes:

- **linear:** `|w| = count · w_syn`
- **log1p:** `|w| = log(1 + count) · w_syn`
- **sqrt:** `|w| = √count · w_syn`
- **lognormal:** `|w| = exp(N(ln max(count, 1), σ)) · w_syn` (drawn per edge from `weight_seed`)

For the lognormal rule, `SD(log|w|) = √(SD(log count)² + σ²)`. The recent connectome-constrained fitting literature (bioRxiv 2026.08.21.745055) reports fitted weight log-spread SD(log w) = 1.83 (truncated-lognormal MLE). Matching that spread requires σ = √(1.83² − 0.983²) ≈ 1.55 for the male and σ = √(1.83² − 0.825²) ≈ 1.64 for the female; we adopt **σ = 1.6** as the literature-matched condition. Note σ = 1.83 itself would *overshoot* the fitted spread by inflating it with the count dispersion — the distinction between total log-spread and draw dispersion matters operationally.

Two anchor regimes are reported side by side:

- **Spread-matched anchor:** σ = 1.6 at raw `w_syn = 0.1`. Mean |w| exceeds the linear baseline (1.12 mV female, 1.73 mV male vs 0.31 mV), placing both networks in a high-recruitment regime.
- **Mean-matched sweep:** `w_syn(σ) = 0.1 · exp(−σ²/2)`, which holds E[|w|] = E[count] · 0.1 fixed while varying only dispersion (σ = 0.5 → 0.0888, 1.0 → 0.0607, 1.6 → 0.0278). This isolates the effect of weight *dispersion* from weight *gain* — a confound present in naive σ sweeps, where E[|w|] grows as exp(σ²/2).

### 2.5 Null models

1. **Degree-preserving double-edge swap (DES).** Starting from each sex's real edge set (64-bit keyed (pre, post) pairs), we perform Q·|E| attempted swaps (Q = 10; ~134M attempts female, ~244M male per seed) of random edge pairs, reassigning targets when the resulting edge set is edge-set-identical-free (rejection sampling). In- and out-degree sequences are preserved *exactly* — verified identical post-swap for every seed. Weights travel with their source edge. Acceptance rates: 99.1% (female), 98.7% (male). Three seeds per sex.
2. **Sign-shuffle.** Fisher–Yates permutation of the sign vector across edges, preserving the excitatory/inhibitory counts and all wiring.
3. **Size-matched random ablation.** All edges touching k uniformly random neurons are removed, k = 3,900 (male) / 3,803 (female) — exactly the dimorphic-neuron counts used in §2.7. Five seeds per sex.

### 2.6 Single-source-of-truth (SSOT) protocol and statistics

Every simulation writes one JSON record to an append-only ledger keyed by `(tag, source, weight_seed, sim_seed)`. Conditions are sampled over three seed-pairs (weight_seed, sim_seed) ∈ {(0,42), (1,43), (2,44)} for real networks; null-network simulations use the null build seed as weight_seed (three DES seeds) with a fixed simulation seed (single-seed dynamics for nulls; their cross-seed SD proved negligible, ≤ 0.21 percentage points). DES builds for all six networks (3 seeds × 2 sexes) were completed and degree-verified before their simulations were queued.

We report mean ± SD across seed-pairs (SD with ddof = 1) and two-sided 95% CIs on male/female ratios via 10,000-resample bootstrap over seed-pairs. Aggregation deduplicates the ledger by key with last-timestamp-wins. Recruitment is the fraction of neurons firing ≥ 1 spike in 2000 ms; population rate is spikes/s averaged over all neurons ("rate_all").

### 2.7 Metrics

- **Recruitment (% fired)** — primary readout (robust to rate confounding by construction).
- **Population rate (Hz, all neurons)** and **per-active-neuron rate**.
- **Branching ratio m** — mean descendants per ancestor in 1 ms bins (criticality: m = 1).
- **CV of ISI** — reported but interpreted as rate-dependent (§3.8).
- **Transfer entropy, participation ratio** — rate-dependent; see §3.8 and Limitations.

### 2.8 Dimorphic-neuron identification and silencing

Sexually dimorphic neurons were identified from annotation flags (male: `dimorphism`, `fruDsx`; female: `sexually_dimorphic`); 2.4% of cells in each sex. Silencing removes all edges touching dimorphic neurons (both sexes' own dimorphic sets). The size-matched random-ablation null (§2.5) provides the control.

---

## 3. Results

### 3.1 The recruitment gap exists under every weight rule

Under linear weights at the critical point (w_syn = 0.1), the male recruits 35.20 ± 0.68% of neurons versus 1.35 ± 0.29% in the female — a **26.1× ratio (95% CI 21.9–33.7)** (Table 1). Under lognormal weights at matched mean weight, the ratio is 14.5–17× across σ (Table 4). At the literature-matched spread anchor, both networks recruit heavily and the ratio compresses to 1.75× (§3.2). The direction of the gap is invariant; its magnitude depends on where each sex sits on the recruitment curve.

**Table 1. Baseline dynamics (2000 ms, linear weights, w_syn = 0.1; mean ± SD over 3 seed-pairs).**

| Metric | Female BANC | Male MCNS |
|---|---|---|
| Recruitment (% fired) | 1.35 ± 0.29 | 35.20 ± 0.68 |
| Population rate (Hz, all neurons) | 0.07 ± 0.04 | 15.50 ± 3.85 |
| Branching ratio m | 0.999 ± 0.000 | 1.001 ± 0.002 |
| CV of ISI | 1.04 ± 0.22 | 2.74 ± 0.47 |

Under log1p and sqrt compression both sexes collapse to the 1.00 ± 0.00% drive floor (only directly driven neurons fire): the network is subcritical and the sex gap vanishes. The male's excess activity is therefore carried by high-count connections — compress them and the gap disappears; this motivates the lognormal analysis, which allows strong edges without collapsing them.

### 3.2 Literature-matched lognormal weights: 1.75× recruitment gap

At σ = 1.6, w_syn = 0.1 (SD(log|w|) ≈ 1.83, matching the fitted literature spread):

**Table 2. σ = 1.6 anchor (w_syn = 0.1; mean ± SD over 3 seed-pairs).**

| Metric | Female BANC | Male MCNS | Ratio (M/F) |
|---|---|---|---|
| Recruitment (% fired) | 45.04 ± 0.49 | 79.03 ± 0.16 | **1.75× [1.74, 1.78]** |
| Population rate (Hz) | 69.48 ± 16.40 | 183.21 ± 1.89 | 2.64× |
| Per-active-neuron rate (Hz) | 154.1 ± 35.4 | 231.8 ± 2.8 | 1.50× |
| Branching ratio m | 1.000 ± 0.000 | 0.998 ± 0.001 | — |

The male recruits 1.75× more of the network, fires its active neurons ~1.5× faster, and integrates to a 2.6× higher population rate. Note the female's population-rate CI is wide (±16 Hz on 69 Hz): at this operating point the female sits near an ignition threshold and individual seeds differ in how much of the network catches (see also §3.7). Recruitment, not rate, is the primary readout throughout.

### 3.3 Degree-preserving decomposition: 58% wiring, 42% degree structure

DES rewiring preserves each network's exact degree sequences while randomizing which edges exist. If the sex gap were a property of degree/density structure alone, rewiring would preserve it; if a property of specific wiring, rewiring would destroy it. The result is a decomposition:

**Table 3. Real vs DES-rewired networks (σ = 1.6, w_syn = 0.1; DES: mean ± SD over 3 build seeds).**

| Network | Recruitment real | Recruitment DES | log-gap destroyed |
|---|---|---|---|
| Female BANC | 45.04 ± 0.49% | 72.12 ± 0.21% | 0.471 log units |
| Male MCNS | 79.03 ± 0.16% | 91.46 ± 0.05% | 0.146 log units |

- Real log-gap: ln(79.03/45.04) = **0.562**
- DES log-gap: ln(91.46/72.12) = **0.238**
- **Specific wiring accounts for (0.562 − 0.238)/0.562 = 58% of the sex gap; degree/density structure accounts for 42%.**
- Rewired ratio: 1.27× [1.26, 1.27].

Two conclusions follow. First, **nearly half the gap survives on degree/density alone** — the difference is not purely a wiring property. Second, and more surprisingly, *both* brains' specific wiring is net-suppressive relative to their own degree structure — rewiring makes both networks more active (female +27 points, male +12 points). The female's wiring damps far harder per unit of degree (0.471 log units) than the male's (0.146). The sex difference in recruitment is thus largely the story of the female connectome's unusually suppressive specific wiring, not of the male's amplification.


### 3.4 Dispersion versus gain: the ratio is regime-dependent, the log-gap is not

Because E[|w|] grows as exp(σ²/2) under a raw sweep, σ sweeps confound weight dispersion with mean gain. The mean-matched sweep removes the confound:

**Table 4. Weight-rule sensitivity (2000 ms; mean ± SD over 3 seed-pairs; ratios with bootstrap 95% CI).**

| Rule | Female | Male | Ratio |
|---|---|---|---|
| linear, w_syn = 0.1 | 1.35 ± 0.29% | 35.20 ± 0.68% | 26.1× [21.9, 33.7] |
| lognormal σ=0.5, mean-matched | 2.15 ± 0.44% | 36.75 ± 1.00% | 17.1× [14.2, 21.4] |
| lognormal σ=1.0, mean-matched | 2.32 ± 0.11% | 38.32 ± 0.59% | 16.5× [15.8, 17.2] |
| lognormal σ=1.6, mean-matched | 2.81 ± 0.33% | 40.93 ± 0.35% | 14.5× [13.4, 16.7] |
| lognormal σ=0.5, raw w_syn=0.1 | 3.98 ± 2.07% | 38.12 ± 2.97% | 9.6× [6.3, 18.6] |
| lognormal σ=1.6, raw w_syn=0.1 | 45.04 ± 0.49% | 79.03 ± 0.16% | 1.75× [1.74, 1.78] |
| log1p | 1.00 ± 0.00% | 1.00 ± 0.00% | 1.0× (drive floor) |
| sqrt | 1.00 ± 0.00% | 1.00 ± 0.00% | 1.0× (drive floor) |

With mean weight pinned to the linear baseline, dispersion alone (σ from 0.5 to 1.6) leaves the ratio nearly unchanged (17.1× → 14.5×) — **dispersion is not the mechanism**. The compression to 1.75× in the raw-w_syn anchor comes from *gain*: raising mean |w| ~3.6× pushes the female network past its ignition threshold (2.8% → 45%) far more than the male (40.9% → 79%). The honest summary is that the recruitment *ratio* depends on the operating point (26× threshold regime, 1.75× near saturation), while the underlying sensitivity — how much less drive the male network needs for equal recruitment — is stable across rules (§3.5).

### 3.5 Criticality is invariant; recruitment curves are shifted

The branching ratio is 0.983–1.005 in **every** condition, both sexes, every weight rule and drive level tested — including all DES-rewired and ablation networks. Both connectomes self-organize to criticality; the sex difference is *where on the recruitment curve* each sits, not the curve's shape:

**Table 5. Recruitment ladder (σ = 1.6; single seed-pair per point except w_syn = 0.1, which is the 3-seed anchor).**

| w_syn | Female % fired | Male % fired |
|---|---|---|
| 0.01 | — | 1.96 |
| 0.02 | 1.73 | 29.35 |
| 0.03 | — | 44.13 |
| 0.04 | 16.57 | — |
| 0.05 | — | 64.97 |
| 0.06 | 27.83 | — |
| 0.10 | 45.04 ± 0.49 | 79.03 ± 0.16 |
| 0.15 | 57.55 | — |

The male reaches equivalent recruitment at roughly 2–3× lower w_syn (male 0.02 → 29.4% vs female 0.06 → 27.8%; male 0.05 → 65.0% vs female 0.15 → 57.6%). This w_syn-equivalence (~2.5×) is the cleanest scale-free statement of the sex difference and is consistent across the ladder.

### 3.6 Silencing dimorphic neurons: modest, distributed, and now nulled

Silencing all edges touching the 2.4% dimorphic neurons reduces male recruitment by 8.4% relative (35.20 → 32.23 ± 0.45%). The size-matched random-ablation null (5 seeds) reduces it by 4.9% (33.46 ± 0.92%). The dimorphic-specific effect is therefore real but modest — a 1.7× larger effect than random loss of the same number of neurons — and the sex difference survives it almost intact. In the female, silencing her dimorphic set is indistinguishable from random ablation (1.33 ± 0.29 vs 1.32 ± 0.04).

**Table 6. Silencing with null (linear weights; mean ± SD; ablation null over 5 seeds).**

| Network | Real | Dimorphic-silenced | Random-ablated (null) |
|---|---|---|---|
| Male MCNS | 35.20 ± 0.68% | 32.23 ± 0.45% (−8.4%) | 33.46 ± 0.92% (−4.9%) |
| Female BANC | 1.35 ± 0.29% | 1.33 ± 0.29% (−1.5%) | 1.32 ± 0.04% (−2.2%) |

The sex difference is a distributed property of whole-network wiring, not a localized effect of annotated sex-specific circuits — consistent with the distributed dimorphism reported for the male CNS connectome (Berg et al., 2026).

### 3.7 Sign structure is net-suppressive in both sexes

Shuffling excitatory/inhibitory signs (preserving all wiring and sign counts) *increases* recruitment in both sexes: male 35.20 → 61.12 ± 2.88%, female 1.35 → 13.16 ± 10.50% (Table 7). Real E/I placement is therefore actively suppressive relative to random sign placement — inhibition is not decorative. The female's shuffled network is bimodal across seeds (19.3%, 19.2%, 1.0%): it sits at an ignition threshold where two of three seed draws escape the drive floor and one does not. We report the mean ± SD with the bimodality stated, and treat the female σ = 0.5 anchor (3.98 ± 2.07%, seeds 6.15/2.02/3.77) with the same candor.

**Table 7. Sign-shuffle control (linear weights, w_syn = 0.1; mean ± SD over 3 seed-pairs).**

| Network | Real | Sign-shuffled |
|---|---|---|
| Male MCNS | 35.20 ± 0.68% | 61.12 ± 2.88% |
| Female BANC | 1.35 ± 0.29% | 13.16 ± 10.50% (bimodal: 19.3/19.2/1.0) |

### 3.8 Controls for rate-confounding in higher-order metrics

When comparing networks with varying activity levels, metrics that scale with firing rate are highly susceptible to artifactual divergence: the more active network differs on such metrics for reasons unrelated to wiring. We demonstrate this here by evaluating transfer entropy, participation ratio, and CV of ISI under per-neuron rate matching, in which the male's spike train is subsampled to the female's per-neuron rate before metric computation:

- **Transfer entropy.** The raw TE difference (0.0221 vs 0.0005, a "44×" gap) collapses to 0.9× under per-neuron rate matching (0.00047 vs 0.00051). The apparent information-flow advantage is a firing-rate artifact: at matched per-neuron rate, the sexes are indistinguishable in information flow.
- **Participation ratio.** The raw PR suggests the male is lower-dimensional (1.28 vs 6.08, "more synchronized"). Under rate matching the male appears *more* high-dimensional (43.1 vs 6.1) — but this reversal is itself an artifact: spike thinning decorrelates neurons and inflates PR for both sexes (the female's own PR rises from 6.08 to 19.5 when thinned to a common 2 Hz rate). Dimensionality estimated from post-hoc thinning is not defensible in either direction; a matched-rate simulation would be required for any claim.
- **CV of ISI.** The raw CV difference (2.99 vs 1.01) shrinks to 1.21 vs 1.00 under rate matching. Moreover, CV **reverses sign between operating regimes** (linear: male 2.74 vs female 1.04; σ = 1.6 anchor: female 2.68 vs male 1.48), so a single-regime CV comparison is uninterpretable without rate context.

---

## 4. Discussion

**The finding.** Embedded in an identical dynamical model, the male *Drosophila* CNS recruits substantially more of itself than the female CNS at matched drive. Under lognormal weights matched to the literature's fitted log-spread, the recruitment ratio is 1.75× [1.74–1.78] with the male at 79% and the female at 45%; under linear weights it is 26×; under mean-matched lognormal it is 14.5–17×. The scale-free statement: the male reaches equal recruitment at 2–3× lower synaptic weight scale.

**The decomposition.** Degree-preserving rewiring splits the log-gap roughly 58/42 between specific wiring and degree/density structure: nearly half of the male's recruitment advantage is available from degree structure alone (more edges per neuron, 80/20 E/I vs 75/25), and the majority from which specific edges exist. Equally important, both networks' specific wiring is net-suppressive relative to their own degree skeletons — the female's far more so (0.47 vs 0.15 log units). The sex difference is as much about the female connectome's damping as the male's amplification.

**Criticality.** Every network in this study — both sexes, all weight rules, all drive levels, all nulls — sits at branching ratio ≈ 1. The sex difference manifests as position on a shared critical recruitment curve, not as a different dynamical regime. This is consistent with self-organized criticality in the fly connectome (Shiu et al., 2024) and sharpens the comparison: what differs between the sexes is the coupling strength required to sit at a given point on that curve.

**Why the magnitude question is regime-relative.** The recruitment ratio depends on where the networks sit relative to their ignition thresholds: near-threshold regimes amplify the gap (14–27×); high-gain regimes compress it (1.75×). Reporting a single ratio without its operating point obscures the underlying network dynamics. We recommend connectome-dynamics comparisons report (i) the recruitment ladder (§3.5), (ii) the w_syn-equivalence ratio, and (iii) any operating-point ratio with its regime stated — not a headline number alone.

**Methodological contributions.** (1) The dual-seed SSOT protocol (independent weight and dynamics seeds, append-only ledger, bootstrap CIs on ratios). (2) The DES decomposition as a routine control for connectome dynamics: it is cheap, degree-exact, and separates wiring effects from degree/density effects. (3) The ablation-null standard for silencing claims. (4) The rate-matching controls of §3.8 as a demonstration of how higher-order metrics fail across activity regimes.

---

## 5. Limitations

- **Synaptic weights are inferred, not measured.** Counts are a proxy; the lognormal rule is synthetic (i.i.d. log-noise on counts), not a per-edge effectome fit (Pospisil et al., 2024). Our spread-matching (σ = 1.6 ⇒ SD(log|w|) ≈ 1.83) matches the literature's marginal log-spread but not its structure.
- **Operating-point dependence.** The 1.75× headline holds at the high-recruitment anchor; threshold-regime ratios are 14–27×. We consider the w_syn-equivalence (~2.5×) the most transferable quantity.
- **Null-network simulations use a fixed dynamics seed.** DES and ablation sims vary build seed but not simulation seed; cross-seed SD in the nulls was small (≤ 0.21 pp), but full dual-seed nulls would tighten the decomposition CI.
- **Criticality ladder points are single-seed** (except the w_syn = 0.1 anchors).
- **No gap junctions, neuromodulation, or conduction delays.** Known dynamics-shaping omissions.
- **Dimorphism annotation is incomplete;** the 2.4% figure is a lower bound, and dimorphic-set silencing inherits annotation bias.
- **Transfer entropy used simplified binned estimation**; a proper estimator (e.g., JIDT) would be required for any use of that metric.

---

## 6. Conclusion

The male and female *Drosophila* CNS connectomes, embedded in an identical LIF model, differ robustly in intrinsic recruitment: the male recruits 1.75× [1.74–1.78] more of its network under literature-matched lognormal weights, and reaches equal recruitment at 2–3× lower synaptic weight scale — under every weight rule tested. Degree-preserving decomposition attributes ~58% of the log-scale difference to specific wiring and ~42% to degree/density structure, with both connectomes' specific wiring acting net-suppressively relative to their degree skeletons. All networks self-organize to criticality; the sex difference is position on a shared recruitment curve. Dimorphic-circuit silencing and its size-matched null show the difference is distributed, not localized. Rate-matching controls demonstrate that transfer entropy and participation ratio are vulnerable to artifactual divergence across activity regimes and should not be used as headline metrics in such comparisons. We release the dual-seed SSOT protocol, the degree-preserving DES null, and the full results ledger as reusable standards for connectome-dynamics comparison.

---

## References

1. Dorkenwald, S., et al. (2024). Neuronal wiring diagram of an adult brain. *Nature* 634, 124–138.
2. Shiu, P. K., et al. (2024). A Drosophila computational brain model reveals sensorimotor processing. *Nature* 634, 210–219.
3. Pospisil, D. A., Aragon, M., & Pillow, J. W. (2024). The fly connectome reveals a path to the effectome. *Nature* 634.
4. Berg, S., et al. (2026). Sexual dimorphism in the complete connectome of the Drosophila male central nervous system. *Cell*.
5. Lin, A., et al. (2024). Network statistics of the whole-brain connectome of Drosophila. *Nature* 634.
6. Connectome-constrained modeling identifies neurons and dynamics (2026). *bioRxiv* 2026.08.21.745055.
7. Bates, A. S., et al. (2025). Distributed control circuits across a brain-and-cord connectome. *Nature*.
8. Suárez, L. E., et al. (2024). Connectome-based reservoir computing with the conn2res toolbox. *Nature Communications*.

---

## Reproducibility

All numbers in this paper derive from a single append-only ledger, `results/ssot/ssot_results.jsonl` (84 unique records, dual-seed), aggregated by `aggregate_ssot.py` into `results/ssot_synthesis.md`. Pipeline:

1. `normalize.py` — connectomes → common edge list
2. `double_edge_swap.py` — degree-preserving DES nulls (Q = 10, 3 seeds × 2 sexes, degree-verified)
3. `ablation_null.py` — size-matched random ablation nulls (5 seeds × 2 sexes)
4. `null_model.py` — sign-shuffle control
5. `ssot_run.py` — the dual-seed LIF experiment (weight_seed for weight draws, sim_seed for dynamics + drive selection; `brian2.seed()` explicit)
6. `gen_queue.py` — condition enumeration (42 conditions × 2 sexes)
7. `aggregate_ssot.py` — dedupe (last-timestamp-wins), mean ± SD, bootstrap ratio CIs → `ssot_synthesis.md`

Every result record carries `{tag, source, transform, sigma, w_syn, weight_seed, sim_seed, n_neurons, n_edges, pct_fired, rate_all_Hz, branching_ratio, cv_isi, …}`. Re-running the queue reproduces the ledger modulo wall-clock.