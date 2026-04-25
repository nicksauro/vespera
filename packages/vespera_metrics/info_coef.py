"""Information Coefficient (Spearman) and bootstrap CI.

Refs:
- AFML Ch.8 §8.4.1 p.121 (IC Spearman as rank correlation).
- Efron, B. (1979) "Bootstrap Methods: Another Look at the Jackknife"
  Ann. Statist. 7(1):1-26 (percentile bootstrap).

Pure functions; bootstrap uses np.random.default_rng(seed) — PCG64.
"""
from __future__ import annotations

from typing import Callable, Tuple

import numpy as np
from scipy import stats


def ic_spearman(predictions: np.ndarray, labels: np.ndarray) -> float:
    """Spearman rank correlation between predictions and labels.

    Edge cases (per spec §2.3):
    - len < 2 → ValueError
    - mismatched shapes → ValueError
    - NaN in inputs → ValueError (clean upstream)
    - zero-variance input → 0.0 (rank correlation degenerate, not NaN)
    """
    p = np.asarray(predictions, dtype=float)
    lab = np.asarray(labels, dtype=float)

    if p.shape != lab.shape:
        raise ValueError(
            f"predictions and labels must have same shape; got {p.shape} vs {lab.shape}"
        )
    if p.ndim != 1:
        raise ValueError("predictions and labels must be 1-dim")
    if p.size < 2:
        raise ValueError("IC undefined for n < 2")
    if np.isnan(p).any() or np.isnan(lab).any():
        raise ValueError("NaN in predictions/labels — clean upstream")

    if np.std(p) == 0.0 or np.std(lab) == 0.0:
        return 0.0

    # Compute ranks once to detect exact monotonic (anti-)alignment without
    # relying on scipy's Pearson-on-ranks float arithmetic (which drifts to
    # 0.9999...9 even for perfectly aligned rank vectors). Spec §2.4 T1/T2
    # require exact 1.0 / -1.0 (tolerance 0) for these cases.
    rp = stats.rankdata(p)
    rl = stats.rankdata(lab)
    if np.array_equal(rp, rl):
        return 1.0
    if np.array_equal(rp, rl[::-1]) and np.array_equal(rp[::-1], rl):
        # Reversed-rank shortcut only valid when ranks are also exactly mirrored.
        # Use simpler check below for robustness.
        pass

    rho, _ = stats.spearmanr(p, lab)
    if np.isnan(rho):
        # scipy returns nan only for degenerate inputs we already filtered.
        return 0.0
    rho_f = float(rho)

    # Snap to exact ±1.0 when scipy's float-drift produces 0.9999...9.
    # Conservative tolerance: only snap if within 1e-12 of an extreme.
    if abs(rho_f - 1.0) < 1e-12:
        return 1.0
    if abs(rho_f + 1.0) < 1e-12:
        return -1.0
    return rho_f


def bootstrap_ci(
    sample: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
    n_resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float]:
    """Percentile bootstrap CI (Efron 1979) — deterministic via PCG64.

    Edge cases (per spec §3.4):
    - len(sample) < 2 → ValueError
    - confidence ∉ (0, 1) → ValueError
    - var == 0 → returns (sample[0], sample[0]) exact (no resampling needed)
    """
    s = np.asarray(sample, dtype=float)
    if s.ndim != 1:
        raise ValueError("sample must be 1-dim")
    if s.size < 2:
        raise ValueError("bootstrap_ci requires len(sample) >= 2")
    if not (0.0 < confidence < 1.0):
        raise ValueError("confidence must be in (0, 1)")
    if np.isnan(s).any():
        raise ValueError("NaN in sample — clean upstream")

    if np.var(s) == 0.0:
        # Degenerate: every resample returns the same value → CI collapses.
        return float(s[0]), float(s[0])

    rng = np.random.default_rng(np.random.PCG64(seed))
    n = s.size
    # Vectorised resampling: shape (n_resamples, n)
    idx = rng.integers(0, n, size=(n_resamples, n))
    resamples = s[idx]
    stats_arr = np.apply_along_axis(statistic, 1, resamples)

    alpha = 1.0 - confidence
    lo = float(np.percentile(stats_arr, 100.0 * alpha / 2.0))
    hi = float(np.percentile(stats_arr, 100.0 * (1.0 - alpha / 2.0)))
    return lo, hi
