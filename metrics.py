"""
Dynamical metrics for the male-vs-female comparison.

Each metric is computed from a spike record (runs/<name>_spikes.npz) and is
independent of the others, so they can be computed in parallel.

Metrics:
  1. avalanche.py      — avalanche size/duration distributions (criticality)
  2. lyapunov.py       — edge-of-chaos / perturbation growth
  3. transfer_entropy.py — information flow between regions
  4. dimensionality.py — population activity dimensionality (participation ratio)

Usage:
    python metrics.py <name> [--metric all|avalanche|lyapunov|te|dim]
"""

import numpy as np
import os
import argparse

RUNS = os.path.join(os.path.dirname(__file__), "runs")
OUT = os.path.join(os.path.dirname(__file__), "metrics")
os.makedirs(OUT, exist_ok=True)


def load_spikes(name):
    d = np.load(os.path.join(RUNS, f"{name}_spikes.npz"))
    return d["spike_t"], d["spike_i"], int(d["n_neurons"]), float(d["duration_ms"])


# ---------------------------------------------------------------------------
# 1. Avalanche analysis (criticality)
# ---------------------------------------------------------------------------
def avalanche(spike_t, spike_i, n_neurons, duration_ms, bin_ms=1.0):
    """Avalanche size/duration via binning population activity."""
    n_bins = int(duration_ms / bin_ms)
    # population activity per bin
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]
    activity = np.bincount(bins, minlength=n_bins)

    # avalanche = contiguous run of non-zero activity
    sizes = []
    durations = []
    current_size = 0
    current_dur = 0
    for a in activity:
        if a > 0:
            current_size += a
            current_dur += 1
        else:
            if current_dur > 0:
                sizes.append(current_size)
                durations.append(current_dur)
                current_size = 0
                current_dur = 0
    if current_dur > 0:
        sizes.append(current_size)
        durations.append(current_dur)

    sizes = np.array(sizes)
    durations = np.array(durations)

    # power-law exponent via MLE (Clauset et al.) on sizes
    def pl_exponent(x, xmin=1):
        x = x[x >= xmin]
        if len(x) < 10:
            return np.nan
        return 1 + len(x) / np.sum(np.log(x / xmin))

    alpha_size = pl_exponent(sizes)
    alpha_dur = pl_exponent(durations)

    return {
        "n_avalanches": len(sizes),
        "mean_size": sizes.mean() if len(sizes) else 0,
        "max_size": sizes.max() if len(sizes) else 0,
        "mean_duration": durations.mean() if len(durations) else 0,
        "alpha_size": alpha_size,
        "alpha_dur": alpha_dur,
        "sizes": sizes,
        "durations": durations,
    }


# ---------------------------------------------------------------------------
# 2. Edge-of-chaos (perturbation growth / Lyapunov-like)
# ---------------------------------------------------------------------------
def lyapunov(spike_t, spike_i, n_neurons, duration_ms):
    """Approximate sensitivity: rate of divergence of spike-train distance.

    Uses the inter-spike-interval (ISI) coefficient of variation as a proxy for
    irregularity, plus a simple perturbation-growth estimate via the branching
    ratio (sigma) — the standard criticality measure for spiking networks.
    """
    # Branching ratio: average number of spikes in next bin per spike in current bin
    bin_ms = 1.0
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]
    activity = np.bincount(bins, minlength=n_bins).astype(float)

    # sigma = <A(t+1)> / <A(t)> conditioned on A(t)>0
    if len(activity) < 2:
        return {"branching_ratio": np.nan, "cv_isi": np.nan}

    a_t = activity[:-1]
    a_t1 = activity[1:]
    mask = a_t > 0
    if mask.sum() < 10:
        return {"branching_ratio": np.nan, "cv_isi": np.nan}

    sigma = a_t1[mask].mean() / a_t[mask].mean()

    # ISI CV (irregularity) — vectorized (O(N log N), not O(N^2)).
    # The naive per-neuron loop hangs on the male's ~6M spikes.
    order = np.lexsort((spike_t, spike_i))
    si = spike_i[order]
    st = spike_t[order]
    new_neuron = np.empty(len(si), dtype=bool)
    new_neuron[0] = True
    new_neuron[1:] = si[1:] != si[:-1]
    isi = np.diff(st)
    cross = new_neuron[1:]  # spike starts a new neuron -> previous diff invalid
    isi = isi[~cross]
    if len(isi) >= 10:
        cv = isi.std() / isi.mean()
    else:
        cv = np.nan

    return {"branching_ratio": sigma, "cv_isi": cv}


# ---------------------------------------------------------------------------
# 3. Transfer entropy (information flow) — simplified
# ---------------------------------------------------------------------------
def transfer_entropy(spike_t, spike_i, n_neurons, duration_ms, n_pairs=200):
    """Pairwise transfer entropy between random neuron pairs (binned).

    TE(X->Y) = sum p(y_t, y_{t-1}, x_{t-1}) log [p(y_t | y_{t-1}, x_{t-1}) / p(y_t | y_{t-1})]
    Simplified to a binned estimate over random pairs.
    """
    bin_ms = 2.0
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]

    # Build sparse activity matrix (neurons x time)
    # Use a dict of sets for efficiency
    rng = np.random.default_rng(0)
    active_neurons = np.unique(spike_i)
    if len(active_neurons) < 2:
        return {"mean_te": np.nan, "n_pairs": 0}

    # sample pairs
    pairs = []
    for _ in range(n_pairs):
        x, y = rng.choice(active_neurons, size=2, replace=False)
        pairs.append((x, y))

    # Build binary spike trains for sampled neurons
    te_values = []
    for x, y in pairs:
        tx = set(bins[spike_i == x])
        ty = set(bins[spike_i == y])
        # binned binary series
        bx = np.zeros(n_bins, dtype=int)
        by = np.zeros(n_bins, dtype=int)
        bx[list(tx)] = 1
        by[list(ty)] = 1
        te = _te_binary(bx, by)
        if not np.isnan(te):
            te_values.append(te)

    return {"mean_te": np.mean(te_values) if te_values else np.nan,
            "n_pairs": len(te_values)}


def _te_binary(x, y):
    """Transfer entropy from x to y for binary series."""
    n = len(x)
    if n < 4:
        return np.nan
    # y_t, y_{t-1}, x_{t-1}
    y_t = y[1:]
    y_t1 = y[:-1]
    x_t1 = x[:-1]

    # joint counts
    from collections import Counter
    joint = Counter(zip(y_t, y_t1, x_t1))
    cond = Counter(zip(y_t1, x_t1))
    marg = Counter(zip(y_t, y_t1))

    total = len(y_t)
    te = 0.0
    for (yt, yt1, xt1), c in joint.items():
        p_joint = c / total
        p_cond = cond[(yt1, xt1)] / total
        p_marg = marg[(yt, yt1)] / total
        p_yt1 = sum(1 for (a, b) in zip(y_t, y_t1) if b == yt1) / total
        if p_joint > 0 and p_cond > 0 and p_marg > 0 and p_yt1 > 0:
            # p(y_t | y_{t-1}, x_{t-1}) = p_joint / p_cond
            # p(y_t | y_{t-1}) = p_marg / p_yt1
            p1 = p_joint / p_cond
            p2 = p_marg / p_yt1
            if p1 > 0 and p2 > 0:
                te += p_joint * np.log(p1 / p2)
    return te


# ---------------------------------------------------------------------------
# 4. Population dimensionality (participation ratio)
# ---------------------------------------------------------------------------
def dimensionality(spike_t, spike_i, n_neurons, duration_ms, bin_ms=10.0, max_neurons=5000):
    """Participation ratio of the population covariance matrix (subsampled)."""
    n_bins = int(duration_ms / bin_ms)
    bins = np.floor(spike_t / bin_ms).astype(int)
    bins = bins[bins < n_bins]

    active = np.unique(spike_i)
    if len(active) < 2:
        return {"participation_ratio": np.nan, "n_active": len(active)}

    # Subsample active neurons to bound the covariance matrix size
    if len(active) > max_neurons:
        rng = np.random.default_rng(0)
        active = rng.choice(active, size=max_neurons, replace=False)

    # Build rate matrix for active neurons
    idx_map = {i: k for k, i in enumerate(active)}
    R = np.zeros((len(active), n_bins))
    for i, b in zip(spike_i, bins):
        if i in idx_map:
            R[idx_map[i], b] += 1

    # covariance
    R = R - R.mean(axis=1, keepdims=True)
    C = R @ R.T / n_bins
    evals = np.linalg.eigvalsh(C)
    evals = evals[evals > 0]
    if len(evals) == 0:
        return {"participation_ratio": np.nan, "n_active": len(active)}
    pr = (evals.sum() ** 2) / (evals ** 2).sum()
    return {"participation_ratio": pr, "n_active": len(active)}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--metric", default="all")
    args = ap.parse_args()

    spike_t, spike_i, n, dur = load_spikes(args.name)
    print(f"[{args.name}] spikes={len(spike_t)} neurons={n} duration={dur}ms")

    results = {}
    if args.metric in ("all", "avalanche"):
        results["avalanche"] = avalanche(spike_t, spike_i, n, dur)
    if args.metric in ("all", "lyapunov"):
        results["lyapunov"] = lyapunov(spike_t, spike_i, n, dur)
    if args.metric in ("all", "te"):
        results["transfer_entropy"] = transfer_entropy(spike_t, spike_i, n, dur)
    if args.metric in ("all", "dim"):
        results["dimensionality"] = dimensionality(spike_t, spike_i, n, dur)

    # print summary (drop large arrays)
    for k, v in results.items():
        summary = {kk: vv for kk, vv in v.items() if not isinstance(vv, np.ndarray)}
        print(f"  {k}: {summary}")

    # save
    np.savez_compressed(
        os.path.join(OUT, f"{args.name}_metrics.npz"),
        **{k: v for k, v in results.items()},
    )
