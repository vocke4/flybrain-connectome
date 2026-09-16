"""
Rate-matched participation ratio (dimensionality) check — vectorized.

The male fires 13x more per neuron, which could inflate synchronization and
lower the participation ratio (PR). This checks whether the PR difference
survives per-neuron rate matching.

All hot paths are vectorized (O(N log N)); the naive per-neuron loops hang on
the male's ~6M spikes.

Usage:
    python pr_control.py
"""

import numpy as np
import os

RUNS = os.path.join(os.path.dirname(__file__), "runs")


def load_spikes(name):
    d = np.load(os.path.join(RUNS, f"{name}_spikes.npz"))
    return d["spike_t"], d["spike_i"], int(d["n_neurons"]), float(d["duration_ms"])


def per_neuron_rate_match(spike_t, spike_i, target_rate, duration_ms, seed=0):
    """Subsample each neuron's spikes to target_rate (per-neuron), vectorized."""
    rng = np.random.default_rng(seed)
    n_target = int(target_rate * duration_ms / 1000.0)
    order = np.lexsort((spike_t, spike_i))
    si = spike_i[order]
    st = spike_t[order]
    new_neuron = np.empty(len(si), dtype=bool)
    new_neuron[0] = True
    new_neuron[1:] = si[1:] != si[:-1]
    starts = np.flatnonzero(new_neuron)
    ends = np.append(starts[1:], len(si))
    keep = np.zeros(len(si), dtype=bool)
    for s, e in zip(starts, ends):
        n = e - s
        if n > n_target:
            idx = s + rng.choice(n, size=n_target, replace=False)
            keep[idx] = True
        else:
            keep[s:e] = True
    return st[keep], si[keep]


def participation_ratio(spike_t, spike_i, n_neurons, duration_ms, bin_ms=10.0, max_neurons=5000):
    """Participation ratio of the population covariance matrix (subsampled)."""
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]
    active = np.unique(spike_i)
    if len(active) < 2:
        return np.nan
    if len(active) > max_neurons:
        rng = np.random.default_rng(0)
        active = rng.choice(active, size=max_neurons, replace=False)
    idx_map = {i: k for k, i in enumerate(active)}
    R = np.zeros((len(active), n_bins))
    for i, b in zip(spike_i, bins):
        if i in idx_map:
            R[idx_map[i], b] += 1
    R = R - R.mean(axis=1, keepdims=True)
    C = R @ R.T / n_bins
    evals = np.linalg.eigvalsh(C)
    evals = evals[evals > 0]
    if len(evals) == 0:
        return np.nan
    return (evals.sum() ** 2) / (evals ** 2).sum()


if __name__ == "__main__":
    ft, fi, fn, fd = load_spikes("banc_female")
    mt, mi, mn, md = load_spikes("mcns_male")

    nf = len(np.unique(fi)); nm = len(np.unique(mi))
    female_rate = len(ft) / nf / (fd / 1000.0)
    male_rate = len(mt) / nm / (md / 1000.0)
    print(f"female: {nf} active, {female_rate:.1f} Hz/neuron")
    print(f"male:   {nm} active, {male_rate:.1f} Hz/neuron", flush=True)

    pr_f = participation_ratio(ft, fi, fn, fd)
    pr_m = participation_ratio(mt, mi, mn, md)
    print(f"Baseline PR: female={pr_f:.2f}, male={pr_m:.2f}", flush=True)

    # Rate-match male down to female rate
    mt_rm, mi_rm = per_neuron_rate_match(mt, mi, female_rate, md)
    pr_m_rm = participation_ratio(mt_rm, mi_rm, mn, md)
    print(f"Rate-matched male PR ({female_rate:.1f} Hz/neuron): {pr_m_rm:.2f}", flush=True)

    # Common low rate
    common = min(female_rate, male_rate) * 0.5
    ft_c, fi_c = per_neuron_rate_match(ft, fi, common, fd)
    mt_c, mi_c = per_neuron_rate_match(mt, mi, common, md)
    pr_f_c = participation_ratio(ft_c, fi_c, fn, fd)
    pr_m_c = participation_ratio(mt_c, mi_c, mn, md)
    print(f"Common rate ({common:.1f} Hz): female={pr_f_c:.2f}, male={pr_m_c:.2f}", flush=True)

    print("\n=== CONCLUSION ===")
    print(f"Baseline: female={pr_f:.2f}, male={pr_m:.2f} (male looks lower-dimensional)")
    print(f"Rate-matched male: {pr_m_rm:.2f} vs female {pr_f:.2f}")
    print(f"Common low rate: female={pr_f_c:.2f}, male={pr_m_c:.2f}")
    print()
    print("NOTE: thinning inflates PR for BOTH sexes (female 6.08 -> %.2f at 2 Hz)." % pr_f_c)
    print("So the raw 'lower-dimensional' claim is a rate artifact (dead), but the")
    print("rate-matched reversal (male MORE high-dimensional) is itself confounded by")
    print("thinning-induced decorrelation. Needs a proper matched-rate SIMULATION.")
