"""
Rate-matched CV-of-ISI (burstiness) check — vectorized (fast).

CV of ISI is nominally rate-independent, but thinning changes the ISI
distribution, so we verify empirically with a vectorized implementation.

Usage:
    python cv_control.py
"""

import numpy as np
import os

RUNS = os.path.join(os.path.dirname(__file__), "runs")


def load_spikes(name):
    d = np.load(os.path.join(RUNS, f"{name}_spikes.npz"))
    return d["spike_t"], d["spike_i"], int(d["n_neurons"]), float(d["duration_ms"])


def cv_isi(spike_t, spike_i):
    """Population CV of ISI, vectorized via argsort grouping."""
    order = np.argsort(spike_i, kind="stable")
    si = spike_i[order]
    st = spike_t[order]
    # boundaries between neurons
    new_neuron = np.empty(len(si), dtype=bool)
    new_neuron[0] = True
    new_neuron[1:] = si[1:] != si[:-1]
    # within-neuron sort by time
    # (argsort by neuron only; need per-neuron time sort -> do a second pass)
    # Simpler: sort by (neuron, time) lexicographically
    order2 = np.lexsort((spike_t, spike_i))
    si2 = spike_i[order2]
    st2 = spike_t[order2]
    new_neuron2 = np.empty(len(si2), dtype=bool)
    new_neuron2[0] = True
    new_neuron2[1:] = si2[1:] != si2[:-1]
    # ISI = diff of times within same neuron (exclude cross-neuron diffs)
    isi = np.diff(st2)
    cross = new_neuron2[1:]  # this spike starts a new neuron -> previous diff invalid
    isi = isi[~cross]
    if len(isi) < 10:
        return np.nan, len(isi)
    return isi.std() / isi.mean(), len(isi)


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


if __name__ == "__main__":
    ft, fi, fn, fd = load_spikes("banc_female")
    mt, mi, mn, md = load_spikes("mcns_male")

    # per-neuron rates
    nf = len(np.unique(fi)); nm = len(np.unique(mi))
    female_per_neuron = len(ft) / nf / (fd / 1000.0)
    male_per_neuron = len(mt) / nm / (md / 1000.0)

    cv_f, n_f = cv_isi(ft, fi)
    cv_m, n_m = cv_isi(mt, mi)
    print(f"female: {female_per_neuron:.1f} Hz/neuron, CV_ISI={cv_f:.3f} (n_isi={n_f})")
    print(f"male:   {male_per_neuron:.1f} Hz/neuron, CV_ISI={cv_m:.3f} (n_isi={n_m})")

    mt_rm, mi_rm = per_neuron_rate_match(mt, mi, female_per_neuron, md)
    cv_m_rm, n_m_rm = cv_isi(mt_rm, mi_rm)
    print(f"\nRate-matched male ({female_per_neuron:.1f} Hz/neuron): CV_ISI={cv_m_rm:.3f} (n_isi={n_m_rm})")

    common = min(female_per_neuron, male_per_neuron) * 0.5
    ft_c, fi_c = per_neuron_rate_match(ft, fi, common, fd)
    mt_c, mi_c = per_neuron_rate_match(mt, mi, common, md)
    cv_f_c, _ = cv_isi(ft_c, fi_c)
    cv_m_c, _ = cv_isi(mt_c, mi_c)
    print(f"Common rate ({common:.1f} Hz): female CV={cv_f_c:.3f}, male CV={cv_m_c:.3f}")

    print("\n=== CONCLUSION ===")
    if cv_m_rm > 1.5:
        print("Rate-matched male CV still >1.5 -> burstiness is a genuine wiring property.")
    elif cv_m_rm > 1.2:
        print("Rate-matched male CV 1.2-1.5 -> burstiness PARTIALLY survives (weakened by thinning).")
    else:
        print("Rate-matched male CV ~=1 -> burstiness was largely a rate artifact.")
