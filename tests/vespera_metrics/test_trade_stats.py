"""Tests for vespera_metrics.trade_stats — sortino, hit_rate, profit_factor.

Toy T13 (no-downside), T14 (alternating), T18 (PF/HR) per spec §7.4 + §10.3.
Story T002.0d AC8.
Edge cases §7.3, §10.2, §12 EC2.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from packages.vespera_metrics.trade_stats import (
    hit_rate,
    profit_factor,
    sortino_ratio,
)


# ---------------------------------------------------------------------------
# T13 — no downside → +inf
# ---------------------------------------------------------------------------
def test_T13_sortino_no_downside_inf():
    returns = np.array([0.01] * 252)
    s = sortino_ratio(returns, freq="daily")
    assert math.isinf(s) and s > 0


# ---------------------------------------------------------------------------
# T14 — Sortino alternating (AC8, spec §7.4)
# ---------------------------------------------------------------------------
def test_T14_sortino_alternating():
    returns = np.array([0.01, -0.005] * 126)
    s = sortino_ratio(returns, freq="daily", target=0.0)
    # Recompute from spec formula: mean(DD²) over ALL 252 periods.
    mean_r = float(np.mean(returns))
    dd = np.minimum(returns - 0.0, 0.0)
    downside_dev = math.sqrt(float(np.mean(dd ** 2)))
    expected = mean_r / downside_dev * math.sqrt(252)
    assert math.isclose(s, expected, rel_tol=1e-12)
    # Spec §7.4 reference ≈ 11.225, tolerance 1e-3.
    assert math.isclose(s, 11.225, abs_tol=1e-3)


# ---------------------------------------------------------------------------
# T18 — profit factor + hit rate (spec §10.3)
# ---------------------------------------------------------------------------
def test_T18_profit_factor_hit_rate():
    trades = np.array([10, -5, 20, -15, 8, -3, 12], dtype=float)
    pf = profit_factor(trades)
    hr = hit_rate(trades)
    assert math.isclose(pf, 50.0 / 23.0, rel_tol=1e-12)
    assert math.isclose(hr, 4.0 / 7.0, rel_tol=1e-12)


# ---------------------------------------------------------------------------
# Sortino edge cases (spec §7.3)
# ---------------------------------------------------------------------------
def test_sortino_n_lt_2_raises():
    with pytest.raises(ValueError, match=">= 2"):
        sortino_ratio(np.array([0.01]))


def test_sortino_unknown_freq_raises():
    with pytest.raises(ValueError, match="freq"):
        sortino_ratio(np.array([0.01, 0.02]), freq="weekly")


def test_sortino_at_target_zero():
    """No downside AND mean == target → 0.0 (NOT NaN)."""
    returns = np.array([0.0] * 252)
    s = sortino_ratio(returns, freq="daily", target=0.0)
    assert s == 0.0


def test_sortino_below_target_only_neg_inf():
    """All returns < target, std_downside == |mean - target|."""
    returns = np.array([-0.001] * 252)
    s = sortino_ratio(returns, freq="daily", target=0.0)
    # downside_dev > 0 → finite negative.
    assert math.isfinite(s) and s < 0


def test_sortino_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        sortino_ratio(np.array([0.01, np.nan, 0.02]))


# ---------------------------------------------------------------------------
# Hit rate / profit factor edge cases (spec §10.2)
# ---------------------------------------------------------------------------
def test_hit_rate_empty_raises():
    with pytest.raises(ValueError, match="no trades"):
        hit_rate(np.array([]))


def test_hit_rate_all_positive():
    assert hit_rate(np.array([1.0, 2.0, 3.0])) == 1.0


def test_hit_rate_all_zero():
    assert hit_rate(np.array([0.0, 0.0, 0.0])) == 0.0


def test_hit_rate_all_negative():
    assert hit_rate(np.array([-1.0, -2.0, -3.0])) == 0.0


def test_profit_factor_empty_raises():
    with pytest.raises(ValueError, match="no trades"):
        profit_factor(np.array([]))


def test_profit_factor_all_positive_inf():
    pf = profit_factor(np.array([1.0, 2.0, 3.0]))
    assert math.isinf(pf) and pf > 0


def test_profit_factor_all_zero_one():
    """Convention: 0/0 → 1.0."""
    pf = profit_factor(np.array([0.0, 0.0, 0.0]))
    assert pf == 1.0


def test_profit_factor_all_negative_zero():
    pf = profit_factor(np.array([-1.0, -2.0, -3.0]))
    assert pf == 0.0


def test_profit_factor_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        profit_factor(np.array([1.0, np.nan, -1.0]))
