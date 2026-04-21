"""Tests for signal_rule (layer 4).

AC1: pure. AC2: baseline T1 spec fidelity. AC3: T2-T5 variants. AC4: edge cases.
AC5: reason strings deterministic.
"""

from __future__ import annotations

from datetime import datetime

import pytest

from packages.t002_eod_unwind.core.feature_computer import (
    Features,
    PercentileBands,
)
from packages.t002_eod_unwind.core.signal_rule import (
    Direction,
    TrialParams,
    compute_signal,
)


@pytest.fixture
def atr_bands() -> PercentileBands:
    return PercentileBands(p20=0.5, p60=1.0, p80=1.5)


@pytest.fixture
def t1(atr_bands: PercentileBands) -> TrialParams:
    # T1 baseline uses magnitude > P60 threshold
    return TrialParams(trial_id="T1", magnitude_threshold=0.6, apply_regime_filter=True)


def _feats(
    *,
    direction: int,
    magnitude: float,
    atr_ratio: float,
    hh: int = 17,
    mm: int = 10,
    flags: frozenset[str] = frozenset(),
) -> Features:
    return Features(
        entry_ts=datetime(2024, 3, 15, hh, mm, 0),
        intraday_flow_direction=direction,
        intraday_flow_magnitude=magnitude,
        atr_day_ratio=atr_ratio,
        flags=flags,
    )


def test_t1_fade_short_when_flow_up(t1: TrialParams, atr_bands: PercentileBands) -> None:
    """magnitude > P60 AND atr_ratio in [P20,P80] AND flow>0 ⇒ SHORT (fade)."""
    feats = _feats(direction=1, magnitude=0.8, atr_ratio=1.0)
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.SHORT
    assert sig.reason == "entered_fade_short"


def test_t1_fade_long_when_flow_down(t1: TrialParams, atr_bands: PercentileBands) -> None:
    feats = _feats(direction=-1, magnitude=0.8, atr_ratio=1.0)
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.LONG
    assert sig.reason == "entered_fade_long"


def test_t1_flat_magnitude_below_threshold(
    t1: TrialParams, atr_bands: PercentileBands
) -> None:
    feats = _feats(direction=1, magnitude=0.5, atr_ratio=1.0)
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.FLAT
    assert sig.reason == "magnitude_below_threshold"


def test_t1_flat_atr_outside_regime_low(
    t1: TrialParams, atr_bands: PercentileBands
) -> None:
    feats = _feats(direction=1, magnitude=0.8, atr_ratio=0.3)  # below P20=0.5
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.FLAT
    assert sig.reason == "atr_ratio_outside_regime"


def test_t1_flat_atr_outside_regime_high(
    t1: TrialParams, atr_bands: PercentileBands
) -> None:
    feats = _feats(direction=-1, magnitude=0.8, atr_ratio=2.0)  # above P80=1.5
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.FLAT
    assert sig.reason == "atr_ratio_outside_regime"


def test_flow_flat_returns_flat(t1: TrialParams, atr_bands: PercentileBands) -> None:
    """AC4: direction=0 cannot be faded."""
    feats = _feats(direction=0, magnitude=0.8, atr_ratio=1.0)
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.FLAT
    assert sig.reason == "flow_flat"


def test_atr_undefined_flag_returns_flat(
    t1: TrialParams, atr_bands: PercentileBands
) -> None:
    """AC4: regime_atr_undefined propagates from feature computer."""
    feats = _feats(
        direction=1, magnitude=float("inf"), atr_ratio=float("inf"),
        flags=frozenset({"regime_atr_undefined"}),
    )
    sig = compute_signal(feats, atr_bands, t1)
    assert sig.direction == Direction.FLAT
    assert sig.reason == "atr_undefined"


def test_t4_ignores_regime_filter(atr_bands: PercentileBands) -> None:
    """T4 variant: sem regime filter. atr_ratio fora de [P20,P80] ainda entra."""
    t4 = TrialParams(
        trial_id="T4", magnitude_threshold=0.6, apply_regime_filter=False
    )
    feats = _feats(direction=1, magnitude=0.8, atr_ratio=3.0)  # way above P80
    sig = compute_signal(feats, atr_bands, t4)
    assert sig.direction == Direction.SHORT


def test_t5_restricts_entry_windows(atr_bands: PercentileBands) -> None:
    """T5 variant: apenas janela 17:25."""
    t5 = TrialParams(
        trial_id="T5",
        magnitude_threshold=0.6,
        apply_regime_filter=True,
        allowed_entry_windows=frozenset({"17:25"}),
    )
    # entry at 17:10 ⇒ blocked
    feats_wrong = _feats(direction=1, magnitude=0.8, atr_ratio=1.0, hh=17, mm=10)
    sig_wrong = compute_signal(feats_wrong, atr_bands, t5)
    assert sig_wrong.direction == Direction.FLAT
    assert sig_wrong.reason == "window_not_in_trial"
    # entry at 17:25 ⇒ entra
    feats_ok = _feats(direction=1, magnitude=0.8, atr_ratio=1.0, hh=17, mm=25)
    sig_ok = compute_signal(feats_ok, atr_bands, t5)
    assert sig_ok.direction == Direction.SHORT


def test_t2_vs_t3_threshold_difference(atr_bands: PercentileBands) -> None:
    """T2 uses P50 (lower threshold) — entra; T3 P70 — bloqueia."""
    t2 = TrialParams(trial_id="T2", magnitude_threshold=0.5)
    t3 = TrialParams(trial_id="T3", magnitude_threshold=0.7)
    feats = _feats(direction=1, magnitude=0.65, atr_ratio=1.0)
    assert compute_signal(feats, atr_bands, t2).direction == Direction.SHORT
    assert compute_signal(feats, atr_bands, t3).direction == Direction.FLAT


def test_determinism_same_input_same_output(
    t1: TrialParams, atr_bands: PercentileBands
) -> None:
    feats = _feats(direction=-1, magnitude=0.9, atr_ratio=0.95)
    outputs = [compute_signal(feats, atr_bands, t1) for _ in range(5)]
    assert all(o == outputs[0] for o in outputs)
