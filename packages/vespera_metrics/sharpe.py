"""Sharpe Ratio and Sharpe distribution over CPCV paths.

Ref: Sharpe, W.F. (1966) J. of Business; AFML Ch.14 §14.2.

Annualisation: SR_annual = SR × sqrt(periods_per_year), where
- daily   = 252
- hourly  = 252 * 8
- minute  = 252 * 8 * 60
"""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np


_FREQ_PERIODS = {
    "daily": 252,
    "hourly": 252 * 8,
    "minute": 252 * 8 * 60,
}


def _periods(freq: str) -> int:
    if freq not in _FREQ_PERIODS:
        raise ValueError(
            f"freq must be one of {sorted(_FREQ_PERIODS)}; got {freq!r}"
        )
    return _FREQ_PERIODS[freq]


def sharpe_ratio(
    returns: np.ndarray,
    freq: str = "daily",
    rf: float = 0.0,
) -> float:
    """Annualised Sharpe ratio.

    Edge cases (per spec §4.3):
    - len < 2 → ValueError
    - std == 0 and mean > rf → +inf
    - std == 0 and mean == rf → 0.0
    - std == 0 and mean < rf → -inf
    - unknown freq → ValueError
    """
    r = np.asarray(returns, dtype=float)
    if r.ndim != 1:
        raise ValueError("returns must be 1-dim")
    if r.size < 2:
        raise ValueError("sharpe_ratio requires len(returns) >= 2")
    if np.isnan(r).any():
        raise ValueError("NaN in returns — clean upstream")

    periods = _periods(freq)

    mean = float(np.mean(r))
    # Detect constant returns at the array level (avoids float-drift in
    # np.std producing ~1e-19 for arrays like [-0.001]*252 instead of 0).
    is_constant = bool(np.all(r == r[0]))
    std = 0.0 if is_constant else float(np.std(r, ddof=1))

    if std == 0.0:
        diff = mean - rf
        if diff > 0:
            return math.inf
        if diff < 0:
            return -math.inf
        return 0.0

    sr_per_period = (mean - rf) / std
    return sr_per_period * math.sqrt(periods)


def sharpe_distribution(
    paths_returns: Iterable[np.ndarray],
    freq: str = "daily",
    rf: float = 0.0,
) -> np.ndarray:
    """Sharpe ratio per CPCV path.

    Returns 1-D ndarray with one Sharpe per path. For T002 CPCV(N=10, k=2),
    expected len == 45.
    """
    paths = list(paths_returns)
    if len(paths) == 0:
        raise ValueError("paths_returns must contain at least one path")

    out = np.empty(len(paths), dtype=float)
    for i, path in enumerate(paths):
        out[i] = sharpe_ratio(path, freq=freq, rf=rf)
    return out
