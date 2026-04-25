"""Tests for vespera_metrics.sharpe — Sharpe ratio + path distribution.

Toy T7, T8 + edge cases per spec §4 + §12 (EC1, EC2, EC5).
Story T002.0d AC7.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from packages.vespera_metrics.sharpe import sharpe_distribution, sharpe_ratio


# ---------------------------------------------------------------------------
# T7 — constant positive returns → +inf (AC7 part 1)
# ---------------------------------------------------------------------------
def test_T7_constant_positive_inf():
    returns = np.array([0.01] * 252)
    sr = sharpe_ratio(returns, freq="daily")
    assert math.isinf(sr) and sr > 0


# ---------------------------------------------------------------------------
# T8 — alternating returns (AC7 part 2)
# ---------------------------------------------------------------------------
def test_T8_alternating():
    returns = np.array([0.01, -0.005] * 126)
    sr = sharpe_ratio(returns, freq="daily")
    # Reference computation per spec §4.4 T8: SR_annual ≈ 5.281, tol 1e-3.
    mean = float(np.mean(returns))
    std = float(np.std(returns, ddof=1))
    expected = mean / std * math.sqrt(252)
    assert math.isclose(sr, expected, rel_tol=1e-12)
    assert math.isclose(sr, 5.281, abs_tol=1e-3)


# ---------------------------------------------------------------------------
# Edge cases (spec §4.3, §12 EC1, EC2)
# ---------------------------------------------------------------------------
def test_sharpe_constant_eq_rf_zero():
    """std==0 and mean==rf → 0.0 (NOT NaN)."""
    returns = np.array([0.0] * 252)
    sr = sharpe_ratio(returns, freq="daily", rf=0.0)
    assert sr == 0.0


def test_sharpe_constant_below_rf_neg_inf():
    returns = np.array([-0.001] * 252)
    sr = sharpe_ratio(returns, freq="daily", rf=0.0)
    assert math.isinf(sr) and sr < 0


def test_sharpe_n_lt_2_raises():
    with pytest.raises(ValueError, match=">= 2"):
        sharpe_ratio(np.array([0.01]))


def test_sharpe_unknown_freq_raises():
    with pytest.raises(ValueError, match="freq"):
        sharpe_ratio(np.array([0.01, 0.02]), freq="weekly")


def test_sharpe_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        sharpe_ratio(np.array([0.01, np.nan, 0.02]))


# ---------------------------------------------------------------------------
# Sharpe distribution (per-path)
# ---------------------------------------------------------------------------
def test_sharpe_distribution_shape():
    rng = np.random.default_rng(0)
    paths = [rng.normal(0.001, 0.01, size=252) for _ in range(45)]
    dist = sharpe_distribution(paths, freq="daily")
    assert dist.shape == (45,)
    assert dist.dtype == np.float64
    # All finite for non-degenerate paths.
    assert np.all(np.isfinite(dist))


def test_sharpe_distribution_empty_raises():
    with pytest.raises(ValueError, match="at least one"):
        sharpe_distribution([])
