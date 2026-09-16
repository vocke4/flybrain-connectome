# Literature Review — What the existing fly-connectome papers tell us about our project

**Date:** 2026-09-11
**Scope:** Papers on the *Drosophila* connectome, its LIF simulation, sex differences, criticality, and the effectome — assessed for what informs, validates, or challenges our male-vs-female dynamical comparison.

---

## 1. The landscape (who has done what)

| Paper | Year | What it did | Relevance to us |
|---|---|---|---|
| Shiu et al., *Nature* 634:210 | 2024 | First whole-brain LIF model (FAFB female brain), w ∝ synapse count, sign from NT | **Our model is a direct replication of this.** |
| Lin et al., *Nature* 634 | 2024 | Network statistics: rich-club, 30% highly connected | Topology context for "what about the wiring" |
| Pospisil et al., *Nature* 634 | 2024 | The "effectome" — causal model, weights must be *fitted* not assumed | **Challenges our weight rule** |
| Lappalainen et al., *Nature* | 2024 | Connectome-constrained networks predict visual activity (26 studies) | Frames the "connectivity alone" debate |
| Berg et al., *Cell* | 2026 | **Male CNS connectome** (166,700 neurons) + first male/female structural comparison | **The dataset we use; directly validates our localization result** |
| Sexually-dimorphic neurons (PMC12270219) | 2025 | 91 Fru/Dsx cell types, ~1400 neurons in female brain | Supports "distributed, not localized" |
| Connectome-constrained fitting (bioRxiv) | Aug 2026 | Fitting weights to activity → lognormal weights, scale-free avalanches | **State of the art; the direction the field is moving** |

---

## 2. Findings that VALIDATE our approach

### 2.1 Our model is the field-standard, not a toy
Shiu et al. (2024) is the canonical whole-brain LIF model. We replicate it exactly: `w = sign × count × w_syn`, sign from neurotransmitter identity, Brian2, voltage-injection synapses. Our criticality result (both brains σ ≈ 1.0) reproduces their known critical regime — this is the model *validating itself* against prior work, which is exactly what a reviewer wants to see.

### 2.2 Our "distributed, not localized" finding is independently confirmed
This is the single most important cross-validation. Berg et al. (2026) — the paper that *released* the male CNS connectome — found:

> "Sex-specific and dimorphic neurons are concentrated in higher-order brain centers, while the sensory and motor periphery is largely isomorphic."
> "Sexual dimorphism is present in the majority of intrinsic brain networks and affects ∼0.5–2% of brain locations surveyed."
> "Just under five percent of male brain neurons were found to be sex-specific or dimorphic, compared to fewer than three percent in female brains."

Our localization test silenced 2.4% of male neurons (dimorphic) and saw only −13% activity. That is *consistent* with Berg's structural finding: dimorphism is spread thinly across most networks, not concentrated in a few circuits. Our dynamical result and their structural result are two independent lines of evidence for the same conclusion.

### 2.3 The dimorphic neurons are embedded, not isolated
The sexually-dimorphic-neuron paper (PMC12270219) found that Fru/Dsx neurons, while highly interconnected with each other, "typically receive more inputs from and send more outputs to non-Fru/Dsx neurons." They are not a closed circuit. This is the structural reason our silencing test shows a small effect: you can't kill the sex difference by killing the dimorphic neurons, because they're wired into everything.

### 2.4 Rate confounding is a real, named problem
Our rigor pass (rate-matching) is methodologically sound and citable. Transfer entropy and population dimensionality are both known to scale with firing rate; the neural-population-analysis literature (Trautmann et al. 2019; Elsayed et al. 2017) treats rate normalization as standard practice. Our retraction of the "44× info flow" and "lower-dimensional" claims is exactly the kind of control a careful reviewer would demand.

---

## 3. Findings that CHALLENGE our approach

### 3.1 The weight rule is explicitly a placeholder — and the field is moving past it
This is the biggest challenge. Three independent sources say `w ∝ synapse count` is not the truth:

- **Shiu et al. (2024)** themselves: "given the variety of assumptions the model relies upon, **absolute firing rate predictions are unlikely to be accurate**." They use the model for *relative* circuit-perturbation predictions, not absolute dynamics.
- **Pospisil et al. (2024)**: the whole point of the effectome is that the connectome gives you *paths* but not *strengths*. They use "scaled, signed synaptic counts" only as a first approximation.
- **Connectome-constrained fitting (bioRxiv, Aug 2026)**: fitting weights to resting-state activity yields **lognormal** synaptic weights (not linear-in-count) and reproduces scale-free avalanches and short-timescale dynamics that the naive rule does not.

**Implication for us:** our "male is ~20× more active" result is *conditional on the linear weight rule*. The male has ~2× connection density, so under `w ∝ count` it gets ~2× more weight per neuron — and that alone could drive the activity gap. Our rewiring null *does* rule out pure density (it preserves degree + weight distribution and still collapses activity), so "wiring, not size" survives. But the *magnitude* of the 20× is a function of the weight rule, and a reviewer will ask "what happens with lognormal/fitted weights?"

### 3.2 "Connectivity alone" is contested
Lappalainen et al. (2024) open with the exact debate our project sits inside: "The degree to which measurements of connectivity alone can inform the understanding of neural computation is an open question." They show connectivity + task → accurate predictions, but note success "is more likely when neurons are sparsely connected." Our project is a *pure* connectivity test (no task, no fitting) — which is both its strength (clean) and its weakness (a reviewer may say "of course you need the effectome").

### 3.3 Criticality is contested
Both our brains sit at σ ≈ 1.0, but the criticality literature has a cautionary thread: some rigorous re-analyses (e.g., of cortical avalanche data) did *not* confirm power-law scaling. Our branching ratio is a cleaner measure than avalanches (which we found degenerate in the male — one continuous avalanche), but we should be careful not to over-claim "criticality" when we mean "branching ratio ≈ 1."

---

## 4. The gap we fill (our novelty)

**Nobody has done a matched LIF *dynamical* comparison of male vs female CNS.**

- Berg et al. (2026) did the *structural* comparison (where the wiring differs).
- Shiu et al. (2024) did the *dynamical* model but only on the female brain.
- No paper has asked: "do the structural sex differences produce *dynamical* differences when both are embedded in an identical model?"

That is our contribution. And our honest answer — "yes, in activity (a wiring property), but the more exciting dynamical claims (info flow, dimensionality) are rate artifacts" — is a *useful* negative result, because it tells the field that the structural differences Berg found do **not** trivially translate into the kind of qualitative dynamical differences one might naively expect.

---

## 5. Concrete recommendations (what to do with this)

1. **Cite Berg et al. (2026) as independent confirmation of our localization result.** This is the strongest single addition — it turns our "distributed" finding from a lone result into a cross-validated one.

2. **Reframe the weight-rule caveat as a *feature*, not a bug.** Our paper can explicitly position itself as: "we use the field-standard linear rule (Shiu 2024); the effectome (Pospisil 2024) and fitted-weight models (2026) are the natural next step." This pre-empts the reviewer's #1 objection.

3. **Add a lognormal-weight sensitivity check.** The 2026 fitting paper shows lognormal weights reproduce avalanches. A cheap robustness test: re-run our model with `w ∝ log(1 + count)` or a lognormal draw, and see if the 20× activity gap survives. If it does, the finding is weight-rule-robust; if not, we've found the boundary of our claim. This is the single highest-value experiment to run next.

4. **Soften "criticality" to "branching ratio ≈ 1."** Cite the contested-criticality literature to show we're being careful.

5. **Keep the rate-matching section.** It's our methodological contribution and it's citable (Trautmann 2019, Elsayed 2017).

---

## 6. Sources (all verified 2026-09-11)

1. Shiu, P. K., et al. (2024). A Drosophila computational brain model reveals sensorimotor processing. *Nature* 634, 210–219. https://www.nature.com/articles/s41586-024-07763-9
2. Lin, A., et al. (2024). Network statistics of the whole-brain connectome of Drosophila. *Nature* 634. https://www.nature.com/articles/s41586-024-07968-y
3. Pospisil, D. A., Aragon, M., & Pillow, J. W. (2024). The fly connectome reveals a path to the effectome. *Nature* 634. https://www.nature.com/articles/s41586-024-07982-0
4. Lappalainen, J. K., et al. (2024). Connectome-constrained networks predict neural activity across the fly visual system. *Nature*. https://pmc.ncbi.nlm.nih.gov/articles/PMC11525180/
5. Berg, S., et al. (2026). Sexual dimorphism in the complete connectome of the Drosophila male central nervous system. *Cell*. https://www.cell.com/cell/fulltext/S0092-8674(26)00942-6
6. Sexually-dimorphic neurons in the Drosophila whole-brain connectome (2025). https://pmc.ncbi.nlm.nih.gov/articles/PMC12270219/
7. Connectome-constrained modeling identifies neurons and [dynamics] (bioRxiv, Aug 2026). https://www.biorxiv.org/content/10.64898/2026.08.21.745055v1
8. Trautmann, E. M., et al. (2019). Accurate estimation of neural population dynamics without spike sorting. *Neuron*.
9. Elsayed, G. F., & Cunningham, J. P. (2017). Structure in neural population recordings. *Nature Neuroscience*.
10. Eckstein, N., et al. (2024). Neurotransmitter classification from electron microscopy images. *Cell*.
