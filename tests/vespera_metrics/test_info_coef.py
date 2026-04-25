"""Tests for vespera_metrics.info_coef — IC Spearman + bootstrap CI.

Toy benchmarks T1-T6 + edge cases per spec §2-§3 + §12.
Story T002.0d: AC5 (perfect rank), AC6 (zero-var bootstrap), AC11 (determinism).
"""
from __future__ import annotations

import math

import numpy as np
import pytest
from scipy import stats as scistats

from packages.vespera_metrics.info_coef import bootstrap_ci, ic_spearman


# ---------------------------------------------------------------------------
# T1 — perfect rank (AC5)
# ---------------------------------------------------------------------------
def test_T1_perfect_rank():
    pred = np.array([1, 2, 3, 4, 5], dtype=float)
    lab = np.array([1.1, 1.9, 3.2, 3.8, 5.5])
    ic = ic_spearman(pred, lab)
    assert ic == 1.0


# ---------------------------------------------------------------------------
# T2 — anti-correlation
# ---------------------------------------------------------------------------
def test_T2_anti_correlation():
    pred = np.array([1, 2, 3, 4, 5], dtype=float)
    lab = np.array([5, 4, 3, 2, 1], dtype=float)
    ic = ic_spearman(pred, lab)
    assert ic == -1.0


# ---------------------------------------------------------------------------
# T3 — tied ranks (scipy reference)
# ---------------------------------------------------------------------------
def test_T3_tied_ranks():
    pred = np.array([1, 1, 2, 2, 3], dtype=float)
    lab = np.array([10, 20, 30, 40, 50], dtype=float)
    expected = float(scistats.spearmanr(pred, lab).statistic)
    ic = ic_spearman(pred, lab)
    # Spec lists ≈ 0.9486832980505138; tolerance 1e-12.
    assert math.isclose(ic, expected, abs_tol=1e-12)
    assert math.isclose(ic, 0.9486832980505138, abs_tol=1e-12)


# ---------------------------------------------------------------------------
# T4 — zero variance returns 0.0 (NOT NaN)
# ---------------------------------------------------------------------------
def test_T4_zero_variance():
    pred = np.array([3, 3, 3, 3, 3], dtype=float)
    lab = np.array([1, 2, 3, 4, 5], dtype=float)
    ic = ic_spearman(pred, lab)
    assert ic == 0.0


# ---------------------------------------------------------------------------
# Edge cases (spec §2.3, §12 EC4)
# ---------------------------------------------------------------------------
def test_ic_n_lt_2_raises():
    with pytest.raises(ValueError, match="n < 2"):
        ic_spearman(np.array([1.0]), np.array([2.0]))


def test_ic_mismatched_shapes_raises():
    with pytest.raises(ValueError, match="same shape"):
        ic_spearman(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0]))


def test_ic_nan_raises():
    pred = np.array([1.0, 2.0, np.nan, 4.0, 5.0])
    lab = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    with pytest.raises(ValueError, match="NaN"):
        ic_spearman(pred, lab)


# ---------------------------------------------------------------------------
# T5 — bootstrap CI zero variance (AC6)
# ---------------------------------------------------------------------------
def test_T5_bootstrap_zero_var():
    sample = np.array([0.1] * 1000)
    lo, hi = bootstrap_ci(sample, n_resamples=10_000, confidence=0.95, seed=42)
    assert math.isclose(lo, 0.1, abs_tol=1e-10)
    assert math.isclose(hi, 0.1, abs_tol=1e-10)


# ---------------------------------------------------------------------------
# AC11 — bootstrap determinism (same seed → byte-exact)
# ---------------------------------------------------------------------------
def test_bootstrap_determinism():
    sample = np.random.default_rng(0).normal(0, 1, size=200)
    lo1, hi1 = bootstrap_ci(sample, seed=42)
    lo2, hi2 = bootstrap_ci(sample, seed=42)
    assert lo1 == lo2
    assert hi1 == hi2


def test_bootstrap_different_seeds_differ():
    sample = np.random.default_rng(0).normal(0, 1, size=200)
    res1 = bootstrap_ci(sample, seed=42)
    res2 = bootstrap_ci(sample, seed=43)
    assert res1 != res2


# ---------------------------------------------------------------------------
# Edge cases for bootstrap_ci (spec §3.4, §12 EC8)
# ---------------------------------------------------------------------------
def test_bootstrap_size_lt_2_raises():
    with pytest.raises(ValueError, match=">= 2"):
        bootstrap_ci(np.array([1.0]))


def test_bootstrap_invalid_confidence_raises():
    sample = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="confidence"):
        bootstrap_ci(sample, confidence=1.5)
    with pytest.raises(ValueError, match="confidence"):
        bootstrap_ci(sample, confidence=0.0)


def test_bootstrap_nan_raises():
    sample = np.array([1.0, 2.0, np.nan])
    with pytest.raises(ValueError, match="NaN"):
        bootstrap_ci(sample)


def test_bootstrap_ci_bounds_order():
    """Sanity: lo <= hi for a reasonable sample."""
    sample = np.random.default_rng(7).normal(0, 1, size=500)
    lo, hi = bootstrap_ci(sample, seed=42)
    assert lo <= hi
