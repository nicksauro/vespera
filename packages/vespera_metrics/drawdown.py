"""Maximum drawdown, MAR ratio, and Ulcer Index.

Refs:
- Calmar/MAR — Young (1991); Schwager *Market Wizards* (1989).
- Ulcer Index — Martin, P. (1989) tangotools.com/ui/ui.htm.
"""
from __future__ import annotations

import math

import numpy as np


def max_drawdown(equity: np.ndarray) -> float:
    """Maximum drawdown of an equity curve.

    Returns a NEGATIVE float (or 0.0 for monotonically non-decreasing equity).

    Edge cases (per spec §8.3):
        equity[0] <= 0       → ValueError
        constant or strictly increasing → 0.0
        NaN                  → ValueError
    """
    e = np.asarray(equity, dtype=float)
    if e.ndim != 1:
        raise ValueError("equity must be 1-dim")
    if e.size < 1:
        raise ValueError("equity must be non-empty")
    if np.isnan(e).any():
        raise ValueError("NaN in equity — clean upstream")
    if e[0] <= 0:
        raise ValueError("equity series must start positive")

    peak = np.maximum.accumulate(e)
    dd = (e - peak) / peak
    return float(np.min(dd))


def mar_ratio(cagr: float, max_dd: float) -> float:
    """MAR / Calmar ratio.

    Sign convention (per spec §8.3):
        max_dd < 0:  MAR = cagr / abs(max_dd)        (sign of MAR = sign of cagr)
        max_dd == 0 and cagr > 0:  MAR = +inf
        max_dd == 0 and cagr < 0:  MAR = -inf
        max_dd == 0 and cagr == 0: MAR = 0.0         (NOT NaN)
        max_dd > 0: ValueError                       (drawdown is non-positive)
    """
    if math.isnan(cagr) or math.isnan(max_dd):
        raise ValueError("NaN in cagr or max_dd")
    if max_dd > 0:
        raise ValueError("max_dd must be <= 0 (drawdown convention)")

    if max_dd == 0.0:
        if cagr > 0:
            return math.inf
        if cagr < 0:
            return -math.inf
        return 0.0

    return cagr / abs(max_dd)


def ulcer_index(equity: np.ndarray) -> float:
    """Ulcer Index (Martin 1989).

    Formula (spec §9.2):
        peak_t = max(equity[0..t])
        ret_dd_pct_t = 100 × (equity_t - peak_t) / peak_t
        UI = sqrt( mean( ret_dd_pct_t² ) )
    """
    e = np.asarray(equity, dtype=float)
    if e.ndim != 1:
        raise ValueError("equity must be 1-dim")
    if e.size < 1:
        raise ValueError("equity must be non-empty")
    if np.isnan(e).any():
        raise ValueError("NaN in equity — clean upstream")
    if e[0] <= 0:
        raise ValueError("equity series must start positive")

    peak = np.maximum.accumulate(e)
    ret_dd_pct = 100.0 * (e - peak) / peak
    return float(math.sqrt(np.mean(ret_dd_pct ** 2)))
