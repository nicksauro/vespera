"""Sortino ratio, hit rate, profit factor.

Refs:
- Sortino & van der Meer (1991); AFML Ch.14 §14.2.
"""
from __future__ import annotations

import math

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


def sortino_ratio(
    returns: np.ndarray,
    freq: str = "daily",
    target: float = 0.0,
) -> float:
    """Annualised Sortino ratio.

    Formula (spec §7.2):
        DD_t = min(returns_t - target, 0)
        downside_dev = sqrt( mean(DD_t²) )            # mean over ALL periods
        Sortino = (mean(returns) - target) / downside_dev × sqrt(periods)

    Edge cases (per spec §7.3):
        len < 2                    → ValueError
        no downside, mean > target → +inf
        no downside, mean == target→ 0.0
    """
    r = np.asarray(returns, dtype=float)
    if r.ndim != 1:
        raise ValueError("returns must be 1-dim")
    if r.size < 2:
        raise ValueError("sortino_ratio requires len(returns) >= 2")
    if np.isnan(r).any():
        raise ValueError("NaN in returns — clean upstream")

    periods = _periods(freq)
    mean_r = float(np.mean(r))
    diff = r - target
    dd = np.minimum(diff, 0.0)
    # Detect "no downside" exactly to avoid float drift producing tiny
    # downside_dev when all returns equal the target.
    if np.all(dd == 0.0):
        downside_dev = 0.0
    else:
        downside_dev = math.sqrt(float(np.mean(dd ** 2)))

    if downside_dev == 0.0:
        delta = mean_r - target
        if delta > 0:
            return math.inf
        if delta < 0:
            return -math.inf
        return 0.0

    sortino_per = (mean_r - target) / downside_dev
    return sortino_per * math.sqrt(periods)


def hit_rate(trades_pnl: np.ndarray) -> float:
    """Fraction of trades with strictly positive PnL.

    Edge cases (per spec §10.2):
        len == 0      → ValueError
        all positive  → 1.0
        all zero      → 0.0
        all negative  → 0.0
    """
    t = np.asarray(trades_pnl, dtype=float)
    if t.ndim != 1:
        raise ValueError("trades_pnl must be 1-dim")
    if t.size == 0:
        raise ValueError("no trades")
    if np.isnan(t).any():
        raise ValueError("NaN in trades_pnl — clean upstream")

    return float(np.sum(t > 0)) / t.size


def profit_factor(trades_pnl: np.ndarray) -> float:
    """sum(wins) / abs(sum(losses)).

    Edge cases (per spec §10.2):
        len == 0          → ValueError
        all positive       → +inf
        all zero           → 1.0  (convention 0/0 → 1)
        all negative       → 0.0
    """
    t = np.asarray(trades_pnl, dtype=float)
    if t.ndim != 1:
        raise ValueError("trades_pnl must be 1-dim")
    if t.size == 0:
        raise ValueError("no trades")
    if np.isnan(t).any():
        raise ValueError("NaN in trades_pnl — clean upstream")

    wins = float(np.sum(t[t > 0]))
    losses = float(abs(np.sum(t[t < 0])))

    if wins == 0.0 and losses == 0.0:
        return 1.0
    if losses == 0.0:
        return math.inf
    return wins / losses
