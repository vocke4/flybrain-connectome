"""
Proper rate-matched TE control: match PER-NEURON firing rate, not total spikes.

The male has 13x more active neurons AND 13x higher per-neuron rate. The crude
total-spike subsample dilutes male spikes across 13x more neurons, collapsing TE
to zero. The correct control matches each neuron's firing rate to the female's
mean per-neuron rate, then compares TE.

Usage:
    python te_control2.py
"""

import numpy as np
import os
from collections import Counter

RUNS = os.path.join(os.path.dirname(__file__), "runs")


def load_spikes(name):
    d = np.load(os.path.join(RUNS, f"{name}_spikes.npz"))
    return d["spike_t"], d["spike_i"], int(d["n_neurons"]), float(d["duration_ms"])


def binned_te(x, y, n_bins):
    bx = np.zeros(n_bins, dtype=int)
    by = np.zeros(n_bins, dtype=int)
    bx[list(x)] = 1
    by[list(y)] = 1
    n = n_bins
    y_t = by[1:]; y_t1 = by[:-1]; x_t1 = bx[:-1]
    joint = Counter(zip(y_t, y_t1, x_t1))
    cond = Counter(zip(y_t1, x_t1))
    marg = Counter(zip(y_t, y_t1))
    p_yt1 = Counter(y_t1)
    total = len(y_t)
    te = 0.0
    for (yt, yt1, xt1), c in joint.items():
        p_joint = c / total
        p_cond = cond[(yt1, xt1)] / total
        p_marg = marg[(yt, yt1)] / total
        p_yt1v = p_yt1[yt1] / total
        if p_joint > 0 and p_cond > 0 and p_marg > 0 and p_yt1v > 0:
            p1 = p_joint / p_cond
            p2 = p_marg / p_yt1v
            if p1 > 0 and p2 > 0:
                te += p_joint * np.log(p1 / p2)
    return te


def per_neuron_rate_match(spike_t, spike_i, target_rate, duration_ms, seed=0):
    """Subsample each neuron's spikes to target_rate (per-neuron)."""
    rng = np.random.default_rng(seed)
    keep_t = []
    keep_i = []
    for i in np.unique(spike_i):
        t = spike_t[spike_i == i]
        n_target = int(target_rate * duration_ms / 1000.0)
        if len(t) > n_target:
            idx = rng.choice(len(t), size=n_target, replace=False)
            t = t[idx]
        keep_t.append(t)
        keep_i.append(np.full(len(t), i))
    return np.concatenate(keep_t), np.concatenate(keep_i)


def mean_te(spike_t, spike_i, n_neurons, duration_ms, bin_ms=2.0, n_pairs=200, seed=0):
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]
    active = np.unique(spike_i)
    if len(active) < 2:
        return np.nan
    rng = np.random.default_rng(seed)
    te_vals = []
    for _ in range(n_pairs):
        x, y = rng.choice(active, size=2, replace=False)
        tx = set(bins[spike_i == x])
        ty = set(bins[spike_i == y])
        te = binned_te(tx, ty, n_bins)
        if not np.isnan(te):
            te_vals.append(te)
    return np.mean(te_vals) if te_vals else np.nan


if __name__ == "__main__":
    ft, fi, fn, fd = load_spikes("banc_female")
    mt, mi, mn, md = load_spikes("mcns_male")

    # per-neuron rates
    fc = Counter(fi); mc = Counter(mi)
    female_per_neuron = np.mean(list(fc.values())) / (fd/1000.0)
    male_per_neuron = np.mean(list(mc.values())) / (md/1000.0)
    print(f"female: {len(np.unique(fi))} active neurons, {female_per_neuron:.1f} Hz/neuron")
    print(f"male:   {len(np.unique(mi))} active neurons, {male_per_neuron:.1f} Hz/neuron")

    # Baseline TE
    te_f = mean_te(ft, fi, fn, fd)
    te_m = mean_te(mt, mi, mn, md)
    print(f"\nBaseline TE: female={te_f:.5f}, male={te_m:.5f}, ratio={te_m/te_f:.1f}x")

    # Per-neuron rate-matched male -> female's per-neuron rate
    mt_rm, mi_rm = per_neuron_rate_match(mt, mi, female_per_neuron, md)
    te_m_rm = mean_te(mt_rm, mi_rm, mn, md)
    print(f"\nPer-neuron rate-matched male ({female_per_neuron:.1f} Hz/neuron):")
    print(f"  TE = {te_m_rm:.5f}, ratio vs female = {te_m_rm/te_f:.1f}x")

    # Also: match female UP to male's per-neuron rate is impossible (can't add spikes),
    # but we can compare at a common LOW per-neuron rate
    common = min(female_per_neuron, male_per_neuron) * 0.5
    ft_c, fi_c = per_neuron_rate_match(ft, fi, common, fd)
    mt_c, mi_c = per_neuron_rate_match(mt, mi, common, md)
    te_f_c = mean_te(ft_c, fi_c, fn, fd)
    te_m_c = mean_te(mt_c, mi_c, mn, md)
    print(f"\nCommon per-neuron rate ({common:.1f} Hz): female={te_f_c:.5f}, male={te_m_c:.5f}, ratio={te_m_c/te_f_c:.1f}x")

    print("\n=== CONCLUSION ===")
    if te_m_rm > te_f * 1.5:
        print("Per-neuron rate-matched male TE still >1.5x female -> wiring property.")
    else:
        print("Per-neuron rate-matched male TE ~= female -> TE difference was a rate artifact.")
