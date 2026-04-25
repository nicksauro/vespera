"""Tests for vespera_metrics.pbo — Probability of Backtest Overfitting (CSCV).

Toy benchmarks T11, T12, T13 per spec §6.5-§6.7.
Story T002.0d AC4 (updated reference per Mira spec §6.5: PBO=0.8333 instead
of 1.0 trivial; T12 retained as sanity for trivial 2×N case).
Edge cases §6.3, §12 EC7.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from packages.vespera_metrics.pbo import probability_backtest_overfitting


# ---------------------------------------------------------------------------
# T11 — anti-correlation 4×4 (spec §6.5)
#
# DEX FLAG TO MIRA (Article IV escalation, AC0 gate): the PBO impl computes
# 1.0 on this matrix, NOT 5/6 ≈ 0.8333 as the §6.5 walkthrough table claims.
#
# Reproduction: the §6.5 manual table for partition s=3 (IS={0,3}, OOS={1,2})
# states "var 0 (IS mean=5.25 vs var1=5.0, var2=5.0, var3=5.0; argmax → var 0)".
# Actual IS means for {0,3}:
#   var0 = (cv[0,0]+cv[0,3])/2 = (10+0.5)/2 = 5.25
#   var1 = (cv[1,0]+cv[1,3])/2 = (8+2)/2    = 5.0
#   var2 = (cv[2,0]+cv[2,3])/2 = (3+8)/2    = 5.5    ← spec table says 5.0
#   var3 = (cv[3,0]+cv[3,3])/2 = (1+10)/2   = 5.5    ← spec table says 5.0
# argmax → var 2 (lowest index among tie 5.5/5.5), NOT var 0.
# OOS means in {1,2}: var2=(2+7)/2=4.5 → rank=1 → λ=log(1/4)<0 → overfit.
# Therefore all 6 partitions overfit → PBO = 6/6 = 1.0.
#
# Mira's hand-arithmetic in the §6.5 table for s=3 is incorrect; the formula
# itself (§6.2) is canonical and Article IV-clean. Per story T002.0d:
# "Se diverge, levanta para Mira ANTES de marcar AC verde."
# This test asserts the formula-faithful result (1.0) while documenting the
# discrepancy for Mira's re-computation in next spec revision.
# ---------------------------------------------------------------------------
def test_T11_anti_correlation_4x4():
    cv = np.array(
        [
            [10.0, 9.0, 1.0, 0.5],
            [8.0, 7.0, 3.0, 2.0],
            [3.0, 2.0, 7.0, 8.0],
            [1.0, 0.5, 9.0, 10.0],
        ]
    )
    pbo = probability_backtest_overfitting(cv)
    # Formula-faithful expected: all partitions overfit on this perfectly
    # anti-correlated 4×4 → PBO = 1.0. (Spec walkthrough has arithmetic
    # error in s=3 row; flagged to Mira for v0.2.1 metrics-spec revision.)
    assert math.isclose(pbo, 1.0, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# T12 — degenerate 2×N matrix → PBO = 1.0 (spec §6.6)
# ---------------------------------------------------------------------------
def test_T12_degenerate_2xN_anti_corr_pbo_one():
    cv = np.array(
        [
            [10.0, 9.0, 1.0, 0.5],
            [1.0, 0.5, 9.0, 10.0],
        ]
    )
    pbo = probability_backtest_overfitting(cv)
    assert math.isclose(pbo, 1.0, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# T13 — pure noise → PBO ≈ 0.5 (spec §6.7, tolerance ±0.15)
# ---------------------------------------------------------------------------
def test_T13_noise_pbo_near_half():
    rng = np.random.default_rng(42)
    cv = rng.normal(0, 1, size=(4, 8))
    pbo = probability_backtest_overfitting(cv)
    assert abs(pbo - 0.5) <= 0.15


# ---------------------------------------------------------------------------
# Edge cases (spec §6.3, §12 EC7)
# ---------------------------------------------------------------------------
def test_pbo_T_lt_2_raises():
    with pytest.raises(ValueError, match=">= 2 strategy variants"):
        probability_backtest_overfitting(np.array([[1.0, 2.0, 3.0, 4.0]]))


def test_pbo_N_odd_raises():
    cv = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    with pytest.raises(ValueError, match="N even"):
        probability_backtest_overfitting(cv)


def test_pbo_N_lt_2_raises():
    cv = np.array([[1.0], [2.0]])
    with pytest.raises(ValueError, match="N even"):
        probability_backtest_overfitting(cv)


def test_pbo_nan_raises():
    cv = np.array([[1.0, 2.0, 3.0, 4.0], [np.nan, 2.0, 3.0, 4.0]])
    with pytest.raises(ValueError, match="NaN"):
        probability_backtest_overfitting(cv)


def test_pbo_all_identical_returns_half():
    """All-identical variants → no signal → PBO = 0.5 by convention."""
    cv = np.tile(np.array([1.0, 2.0, 3.0, 4.0]), (3, 1))
    pbo = probability_backtest_overfitting(cv)
    assert pbo == 0.5
