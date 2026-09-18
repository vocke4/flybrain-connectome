# Reproduction Guide

This document describes, end to end, how every result in the manuscript was produced
and how to reproduce it from the first-hand public sources. Run all commands from the
package root (the directory containing this file and the pipeline scripts:
`normalize.py`, `double_edge_swap.py`, `ssot_run.py`, `aggregate_ssot.py`, `model.py`, …).

---

## 0. Environment

- Python **3.12** (tested on 3.12.9, macOS arm64; any platform with Brian2 works)
- Dependencies (`pip install`):

```
Brian2==2.10.1
Cython==3.1.3
numpy==2.5.3
pandas==3.0.5
pyarrow==25.0.1
sympy==1.14.0
matplotlib==3.11.1
```

- Brian2 codegen target: `cython` (set in code; requires a working C compiler on first run)
- A full run of the ledger queue takes ≈0.5 h total wall time (median 12 s/job on one machine; jobs are independent and trivially parallelizable across two lanes).

## 1. Obtain the first-hand connectomes (public, versioned)

Create `data/female/` and `data/male/` and download:

| File | Size | SHA-256 (first 64 hex) |
|---|---|---|
| `data/female/banc_888_edgelist_simple_v3.feather` | 382 MB | `8c296e946f3c69a8c7222f30ad75fa8a98eeb189124fec6df829c9125f4be64b` |
| `data/female/banc_888_meta.feather` | 15 MB | `86ccf5df0c67419f8c5f43e93a7ed38d23a080e9f7fde26737290252f3780098` |
| `data/male/connectome-weights-male-cns-v1.0-minconf-0.5.feather` | ~1.1 GB | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |
| `data/male/body-neurotransmitters-male-cns-v1.0.feather` | — | `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621` |
| `data/male/body-annotations-male-cns-v1.0-minconf-0.5.feather` | — | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |

**Download locations (first-hand sources):**

- **Female (BANC)** — "Brain And Nerve Cord" connectome of an adult female *Drosophila melanogaster* (FlyWire / Harvard Medical School; described in the bioRxiv preprint "Distributed control circuits across a brain-and-cord connectome", Bates et al.): <https://flywire.ai/banc_access> and <https://github.com/htem/BANC-project>
- **Male (MaleCNS)** — male CNS connectome v1.0 (Janelia FlyEM / Drosophila Connectomics Group Cambridge; described in Berg et al., *Cell* 2026): <https://male-cns.janelia.org/download/>

Verify checksums after download:

```bash
shasum -a 256 data/female/*.feather data/male/*.feather
```

## 2. Normalize the connectomes

```bash
python normalize.py
```

Produces `normalized/{banc_female,mcns_male}.npz` edge lists
(`pre_idx, post_idx, weight=synapse count, sign=±1, n_neurons`).
Sign convention: excitatory = acetylcholine/glutamate/dopamine/octopamine/tyramine;
inhibitory = GABA/histamine/serotonin/glycine; mixed/unknown dropped
(documented limitation).

**Expected:** female 169,078 neurons / 13,379,740 edges; male 163,511 neurons /
24,410,950 edges (117.5M / 41.5M synapses respectively).

## 3. Generate the null/derived connectomes

```bash
# Degree-preserving double-edge-swap nulls (Q=10, 3 seeds × 2 sexes).
# Verifies degree sequences identical after swapping; logs to results/ssot/des_build.log
python double_edge_swap.py banc_female --q 10 --seed 0   # repeat --seed 1 2
python double_edge_swap.py mcns_male   --q 10 --seed 0   # repeat --seed 1 2

# Size-matched random ablation nulls (5 seeds × 2 sexes; k = dimorphic count)
python ablation_null.py banc_female 3803 --k-seeds 5
python ablation_null.py mcns_male   3900 --k-seeds 5

# Sign-shuffle control (preserves all wiring and sign counts)
python null_model.py banc_female --seed 0
python null_model.py mcns_male   --seed 0
```

**Validation built in:** the DES script asserts degree sequences are identical after
rewiring (see `results/ssot/des_build.log`: 133,797,400 swaps female / 244,109,500
male, ~99% acceptance, "degree sequences verified identical" ×6).

## 4. Run the dual-seed experiment queue

The queue generator enumerates the 42-condition × 2-sex core queue with the exact seed pairs
used in the paper — (weight_seed, sim_seed) = (0,42), (1,43), (2,44) for stochastic
transforms; weight_seed=0 with 3 sim seeds for deterministic transforms. The shipped
ledger contains the phase-0 supplement (stages A–D: 6/12/20/8 records) alongside the
core queue, for 133 records → 130 unique runs / 46 (tag, sex) families:

```bash
python gen_queue.py               # writes queue_female.sh / queue_male.sh (relative-path commands)
bash queue_female.sh              # or run the two lanes in parallel
bash queue_male.sh
```

Each job appends one JSON record to `results/ssot/ssot_results.jsonl` with full
provenance: `{tag, source, transform, sigma, w_syn, weight_seed, sim_seed,
n_neurons, n_edges, pct_fired, rate_all_Hz, rate_fired_Hz, branching_ratio,
cv_isi, participation_ratio, wall_s, ts}`.

**Seed semantics (critical):**
- `--weight-seed` seeds the lognormal weight *draw* (`np.random.default_rng(weight_seed)`)
- `--sim-seed` seeds the *dynamics*: `brian2.seed(sim_seed)` + drive-neuron selection
  (`default_rng(sim_seed)`) + Poisson drive
- `brian2.seed(sim_seed)` is required explicitly: Brian2's internal RNG is NOT
  covered by `np.random.seed()`, so both calls are made in every run.

To reproduce any single condition directly:

```bash
python ssot_run.py --source banc_female --tag anchor_ln_s1.6_w0.1 \
    --transform lognormal --sigma 1.6 --w-syn 0.1 \
    --weight-seed 0 --sim-seed 42 --duration 2000
```

Add `--save-spikes` to save spike trains (needed for §3.8 rate-matching controls).

**Spike-train runs for the §3.8 controls** (as in the manuscript):
run `model.py` for both sexes at the linear baseline, which saves
`runs/{banc_female,mcns_male}_spikes.npz`:

```bash
python model.py banc_female --duration 2000
python model.py mcns_male   --duration 2000
```

## 5. Rate-matching controls (§3.8)

```bash
python te_control2.py    # per-neuron rate-matched transfer entropy
python pr_control.py     # per-neuron rate-matched participation ratio
python cv_control.py     # rate-matched CV of ISI
```

Expected outcomes (match manuscript §3.8):
- TE: raw 0.0221 vs 0.0005 ("44×") → 0.9× under per-neuron rate matching (0.00047 vs 0.00051)
- PR: raw 1.28 vs 6.08 → reversed under rate matching (43.1 vs 6.1), but the reversal
  is itself a spike-thinning decorrelation artifact (female PR inflates 6.08→19.5
  under thinning); dimensionality from post-hoc thinning is not defensible either way
- CV of ISI: raw 2.99 vs 1.01; sign reverses across regimes (no archived matched-rate CV control is shipped, so no rate-matched CV claim is made)


## 5b. Ledger supplement and companion probe ledgers

The shipped `results/ssot/ssot_results.jsonl` contains the dual-seed core queue
**plus** the phase-0 supplement (62 runs): the σ = 1.83 overshoot probe (6 runs),
DES nulls at 3 build × 3 sim seeds (18), ablation nulls at 5 build × 3 sim seeds (30),
and the 3-seed w_syn-equivalence cells (8). Idempotent re-run:

```bash
python phase0_runs.py        # skips any (tag, source, weight_seed, sim_seed) already present
```

Table 3b (the DES decomposition across anchors, w_syn = 0.04 → 0.10) re-runs via:

```bash
bash run_b2.sh               # real + DES at w_syn = 0.04 (3 DES build seeds each)
bash run_b2b.sh              # anchor map at w_syn = 0.05/0.06/0.07/0.08
```

Both drivers append to `results/crit_probe/anchor2_ledger.jsonl` (log:
`results/crit_probe/reanchor_des.log`). `PYTHON=...` overrides the interpreter
(`phase0_runs.py` uses `PYTHON` or `./venv/bin/python`; the two shell drivers use
`PYTHON` or `./venv/bin/python`).

The quiescence-referenced criticality probe ledger (`results/crit_probe/crit_probe_results.jsonl`)
comes from `crit_probe.py` at the package root; see the paper's §3.5 for
why its verdict is "estimator saturates — no criticality claim".

## 6. Aggregate and verify

```bash
python aggregate_ssot.py
```

Deduplicates the ledger (last-timestamp-wins per `(tag, source, weight_seed, sim_seed)`),
computes mean ± SD over seed-pairs, and bootstrap 95% CIs (10,000 resamples) for ratios.
Writes `results/ssot_synthesis.md`.

**Canonical numbers to check against** (all in `results/ssot_synthesis.md`,
aggregated from the shipped 133-record ledger):

| Quantity | Value |
|---|---|
| Anchor σ=1.6 recruitment | F 45.04±0.49% / M 79.03±0.16% → **1.75× [1.74, 1.78]** |
| σ=1.83 overshoot probe | F 55.17±1.05% / M 80.93±0.13% → **1.47× [1.44, 1.50]** (3 seed-pairs) |
| Linear w_syn=0.1 | F 1.35±0.29% / M 35.20±0.68% → **26.1× [21.9, 33.7]** |
| Mean-matched σ sweep | σ=0.5: 17.1×, σ=1.0: 16.5×, σ=1.6: 14.5× |
| DES rewired | F 72.11±0.21% / M 91.46±0.03% → **1.27× [1.26, 1.27]** |
| Log-gap decomposition | real 0.562 / DES 0.238 → **58% specific wiring / 42% degree-density** (log-ratio scale; 57.7% [56.9, 58.5] bootstrapped; 43/57 on the linear scale) |
| w_syn-equivalence | male matches female recruitment at **~3–3.5× lower w_syn** (pair 1 3.0× by grid; pair 2 ≈3.5× interpolated) |
| Dimorphic silencing | M −8.4% rel (35.20→32.23±0.45); ablation null −6.3% (32.98±1.41, n=15); Welch t = 1.67, p ≈ 0.12 |
| Branching ratio | 0.980–1.004 in all 130 unique runs; Poisson ceiling 1 − exp(−λ) ≥ 0.99923 (λ ≥ 7.17) — no criticality claim |
| Per-active rate | F 154.1±35.4 / M 231.8±2.8 Hz |

Determinism: re-running the queue with the same seeds reproduces the ledger modulo
wall-clock fields; `aggregate_ssot.py` output is byte-stable for a given ledger.

## 7. Remaining analyses

```bash
python localize.py               # dimorphic-neuron identification + localization (§2.8)
python robustness.py             # drive/w_syn robustness sweeps
```

## 8. Notes on compute

- Single 2 s simulation: 5–91 s wall (median 12 s), ~1–3 GB RAM per job
- The full ledger queue: ≈0.5 h total wall time single-lane; ~15 min two-lane
- No GPU required; Brian2 cython codegen compiles on first call
- The DES null generation is the longest step (133.8M/244.1M swaps; ~5–10 min per connectome)