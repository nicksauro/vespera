"""Tests for vespera_metrics.report.evaluate_kill_criteria — K1/K2/K3 wiring.

Story T002.0d AC14: K1 (DSR>0), K2 (PBO<0.4), K3 (IC_holdout >= 0.5*IC_in_sample).
Mapping per thesis L126-146.
"""
from __future__ import annotations


from packages.vespera_metrics.report import evaluate_kill_criteria


def test_all_pass_GO():
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.2, ic_in_sample=0.10, ic_holdout=0.08
    )
    assert kd.verdict == "GO"
    assert kd.k1_dsr_passed is True
    assert kd.k2_pbo_passed is True
    assert kd.k3_ic_decay_passed is True
    assert kd.reasons == ()


def test_K1_dsr_zero_kills():
    kd = evaluate_kill_criteria(
        dsr=0.0, pbo=0.2, ic_in_sample=0.10, ic_holdout=0.08
    )
    assert kd.verdict == "NO_GO"
    assert kd.k1_dsr_passed is False
    assert any("K1" in r for r in kd.reasons)


def test_K1_dsr_negative_kills():
    kd = evaluate_kill_criteria(
        dsr=-0.1, pbo=0.2, ic_in_sample=0.10, ic_holdout=0.08
    )
    assert kd.verdict == "NO_GO"
    assert kd.k1_dsr_passed is False


def test_K2_pbo_at_ceiling_kills():
    """PBO == 0.4 is NOT strictly less than 0.4 → fails."""
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.4, ic_in_sample=0.10, ic_holdout=0.08
    )
    assert kd.verdict == "NO_GO"
    assert kd.k2_pbo_passed is False
    assert any("K2" in r for r in kd.reasons)


def test_K2_pbo_above_ceiling_kills():
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.5, ic_in_sample=0.10, ic_holdout=0.08
    )
    assert kd.verdict == "NO_GO"
    assert kd.k2_pbo_passed is False


def test_K3_ic_decay_below_floor_kills():
    """IC_holdout = 0.04, IC_in_sample = 0.10 → ratio 0.4 < 0.5 floor."""
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.2, ic_in_sample=0.10, ic_holdout=0.04
    )
    assert kd.verdict == "NO_GO"
    assert kd.k3_ic_decay_passed is False
    assert any("K3" in r for r in kd.reasons)


def test_K3_ic_in_sample_non_positive_kills():
    """No edge in-sample → can't pass decay test by construction."""
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.2, ic_in_sample=0.0, ic_holdout=0.0
    )
    assert kd.verdict == "NO_GO"
    assert kd.k3_ic_decay_passed is False


def test_K3_at_exact_floor_passes():
    """IC_holdout == 0.5 × IC_in_sample → PASS (>=)."""
    kd = evaluate_kill_criteria(
        dsr=0.95, pbo=0.2, ic_in_sample=0.10, ic_holdout=0.05
    )
    assert kd.k3_ic_decay_passed is True


def test_thresholds_overrides():
    """Allow custom thresholds (e.g. tightening for production)."""
    kd = evaluate_kill_criteria(
        dsr=0.5,
        pbo=0.3,
        ic_in_sample=0.10,
        ic_holdout=0.08,
        thresholds={"dsr_floor": 0.7, "pbo_ceiling": 0.2},
    )
    assert kd.verdict == "NO_GO"
    assert kd.k1_dsr_passed is False  # 0.5 < 0.7
    assert kd.k2_pbo_passed is False  # 0.3 >= 0.2
