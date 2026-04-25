"""Tests for vespera_metrics.drawdown — max_drawdown, mar_ratio, ulcer_index.

Toy T15, T16, T17 per spec §8-§9.
Story T002.0d AC9 (MAR sign), AC10 (Ulcer T17=5.0 exato).
Edge cases §8.3, §9, §12 EC3.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from packages.vespera_metrics.drawdown import (
    max_drawdown,
    mar_ratio,
    ulcer_index,
)


# ---------------------------------------------------------------------------
# T15 — simple drawdown (spec §8.4)
# ---------------------------------------------------------------------------
def test_T15_simple_drawdown():
    equity = np.array([100, 110, 120, 90, 100, 130], dtype=float)
    md = max_drawdown(equity)
    assert math.isclose(md, -0.25, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# T16 — MAR negative sign (AC9, spec §8.4)
# ---------------------------------------------------------------------------
def test_T16_mar_negative_sign():
    mar = mar_ratio(cagr=-0.10, max_dd=-0.30)
    assert math.isclose(mar, -1.0 / 3.0, abs_tol=1e-12)
    assert mar < 0


# ---------------------------------------------------------------------------
# T17 — Ulcer Index Martin canonical example = 5.0 (AC10, spec §9.3)
# ---------------------------------------------------------------------------
def test_T17_ulcer_martin_canonical():
    equity = np.array([100, 95, 90, 100, 110], dtype=float)
    ui = ulcer_index(equity)
    assert math.isclose(ui, 5.0, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# Drawdown edge cases (spec §8.3, §12 EC3)
# ---------------------------------------------------------------------------
def test_drawdown_strictly_increasing():
    equity = np.array([100, 105, 110, 115, 120], dtype=float)
    md = max_drawdown(equity)
    assert md == 0.0


def test_drawdown_constant():
    equity = np.array([100.0] * 10)
    md = max_drawdown(equity)
    assert md == 0.0


def test_drawdown_initial_non_positive_raises():
    with pytest.raises(ValueError, match="must start positive"):
        max_drawdown(np.array([0.0, 1.0, 2.0]))
    with pytest.raises(ValueError, match="must start positive"):
        max_drawdown(np.array([-1.0, 1.0, 2.0]))


def test_drawdown_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        max_drawdown(np.array([100.0, np.nan, 110.0]))


# ---------------------------------------------------------------------------
# MAR sign matrix (AC9 explicit) — spec §8.3
# ---------------------------------------------------------------------------
def test_mar_positive_cagr_negative_dd():
    assert mar_ratio(0.10, -0.20) == 0.5


def test_mar_zero_dd_positive_cagr_inf():
    assert mar_ratio(0.10, 0.0) == math.inf


def test_mar_zero_dd_negative_cagr_neg_inf():
    assert mar_ratio(-0.10, 0.0) == -math.inf


def test_mar_zero_zero_returns_zero_not_nan():
    """Both zero → MAR = 0 (NOT NaN). Spec §8.3 explicit."""
    val = mar_ratio(0.0, 0.0)
    assert val == 0.0
    assert not math.isnan(val)


def test_mar_positive_dd_raises():
    """max_dd is the most-negative drawdown — positive value is invalid."""
    with pytest.raises(ValueError, match="<= 0"):
        mar_ratio(0.10, 0.05)


def test_mar_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        mar_ratio(math.nan, -0.1)
    with pytest.raises(ValueError, match="NaN"):
        mar_ratio(0.1, math.nan)


# ---------------------------------------------------------------------------
# Ulcer edge cases
# ---------------------------------------------------------------------------
def test_ulcer_strictly_increasing_zero():
    equity = np.array([100, 110, 120, 130], dtype=float)
    assert ulcer_index(equity) == 0.0


def test_ulcer_initial_non_positive_raises():
    with pytest.raises(ValueError, match="must start positive"):
        ulcer_index(np.array([0.0, 1.0, 2.0]))


def test_ulcer_nan_raises():
    with pytest.raises(ValueError, match="NaN"):
        ulcer_index(np.array([100.0, np.nan, 90.0]))
