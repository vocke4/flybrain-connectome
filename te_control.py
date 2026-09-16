"""
Rate-matched transfer entropy control.

The male brain fires ~106 Hz vs female ~8 Hz. Transfer entropy is naturally
inflated by firing rate, so the "44x" could be partly a rate artifact. This
script does a rate-matched control:

  1. Subsample male spikes to match the female firing rate (rate-matched).
  2. Recompute TE on the rate-matched male.
  3. If TE is STILL higher, the difference is a wiring property, not a rate artifact.

Also computes a proper binned TE estimator (Schreiber 2000) in pure numpy.

Usage:
    python te_control.py
"""

import numpy as np
import os

RUNS = os.path.join(os.path.dirname(__file__), "runs")


def load_spikes(name):
    d = np.load(os.path.join(RUNS, f"{name}_spikes.npz"))
    return d["spike_t"], d["spike_i"], int(d["n_neurons"]), float(d["duration_ms"])


def binned_te(x, y, n_bins):
    """Schreiber (2000) transfer entropy from x to y, binned binary series."""
    bx = np.zeros(n_bins, dtype=int)
    by = np.zeros(n_bins, dtype=int)
    bx[list(x)] = 1
    by[list(y)] = 1
    n = n_bins
    if n < 4:
        return np.nan

    y_t = by[1:]
    y_t1 = by[:-1]
    x_t1 = bx[:-1]

    # joint distribution p(y_t, y_{t-1}, x_{t-1})
    from collections import Counter
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
            p1 = p_joint / p_cond  # p(y_t | y_{t-1}, x_{t-1})
            p2 = p_marg / p_yt1v   # p(y_t | y_{t-1})
            if p1 > 0 and p2 > 0:
                te += p_joint * np.log(p1 / p2)
    return te


def mean_te(spike_t, spike_i, n_neurons, duration_ms, bin_ms=2.0, n_pairs=200, seed=0):
    """Mean pairwise TE over random pairs."""
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


def rate_match(spike_t, spike_i, target_rate, duration_ms):
    """Subsample spikes to match a target firing rate."""
    n_neurons = len(np.unique(spike_i))
    current_rate = len(spike_t) / (duration_ms / 1000.0)
    if current_rate <= target_rate:
        return spike_t, spike_i  # already at or below target

    keep_frac = target_rate / current_rate
    rng = np.random.default_rng(0)
    keep = rng.random(len(spike_t)) < keep_frac
    return spike_t[keep], spike_i[keep]


if __name__ == "__main__":
    # Load both
    ft, fi, fn, fd = load_spikes("banc_female")
    mt, mi, mn, md = load_spikes("mcns_male")

    female_rate = len(ft) / (fd / 1000.0)
    male_rate = len(mt) / (md / 1000.0)
    print(f"female: {len(ft)} spikes, {female_rate:.1f} Hz")
    print(f"male:   {len(mt)} spikes, {male_rate:.1f} Hz")

    # Baseline TE
    te_f = mean_te(ft, fi, fn, fd)
    te_m = mean_te(mt, mi, mn, md)
    print(f"\nBaseline TE: female={te_f:.5f}, male={te_m:.5f}, ratio={te_m/te_f:.1f}x")

    # Rate-matched male (subsample to female rate)
    mt_rm, mi_rm = rate_match(mt, mi, female_rate, md)
    male_rate_rm = len(mt_rm) / (md / 1000.0)
    te_m_rm = mean_te(mt_rm, mi_rm, mn, md)
    print(f"\nRate-matched male: {len(mt_rm)} spikes, {male_rate_rm:.1f} Hz")
    print(f"Rate-matched TE: male={te_m_rm:.5f}, ratio vs female={te_m_rm/te_f:.1f}x")

    # Also rate-match female UP is impossible (can't add spikes), so instead
    # downsample BOTH to a common low rate for a fair comparison
    common_rate = min(female_rate, male_rate) * 0.5
    ft_c, fi_c = rate_match(ft, fi, common_rate, fd)
    mt_c, mi_c = rate_match(mt, mi, common_rate, md)
    te_f_c = mean_te(ft_c, fi_c, fn, fd)
    te_m_c = mean_te(mt_c, mi_c, mn, md)
    print(f"\nCommon-rate ({common_rate:.1f} Hz) TE: female={te_f_c:.5f}, male={te_m_c:.5f}, ratio={te_m_c/te_f_c:.1f}x")

    print("\n=== CONCLUSION ===")
    if te_m_rm > te_f * 1.5:
        print("Rate-matched male TE still >1.5x female -> wiring property, not rate artifact.")
    else:
        print("Rate-matched male TE ~= female -> the 44x was largely a rate artifact.")
