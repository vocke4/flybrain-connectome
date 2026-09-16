
## Legacy-vs-SSOT reconciliation (linear transform)

Legacy `weight_sensitivity.py` (single-seed, 2026-09-11): female 2.70% / male 36.23% → 13.4×.
SSOT (dual-seed, 3 sim_seeds): female 1.35±0.29% / male 35.20±0.68% → 26.1× [~15, ~45].

Root cause of discrepancy (verified in code, not conjecture):
- Legacy `np.random.seed(42)` seeds ONLY numpy's legacy global RNG; Brian2's
  internal `rand()`/`randn()` stream was never seeded (no `brian2.seed()` call),
  so threshold-noise draws came from an uncontrolled RNG state.
- Legacy drive-neuron selection hardcoded `default_rng(0)`; SSOT selects drive
  neurons from `default_rng(sim_seed)` — 3 different 1% drive populations.
- Male value is stable across all of this (36.2 vs 35.2±0.7); the female sits
  near the ignition threshold where draw variance is largest — exactly where
  uncontrolled seeding shows up.

Decision: SSOT numbers are authoritative. Legacy 13.4× superseded by ~26×
(linear) with wide CI; headline remains the σ=1.6 row: 1.75× [1.74, 1.78].
Prose must cite SSOT only; the sensitivity study keeps its legacy values as a
historical row with a pointer to the SSOT re-run.
