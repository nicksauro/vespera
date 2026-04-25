"""Tests for FeatureComputer.

AC3: pure, deterministic.
AC4: direction ∈ {-1, 0, 1}.
AC5: ATR_20d == 0 ⇒ magnitude=inf and flag regime_atr_undefined (no crash).
AC10: parity with spec YAML formulas.
"""

from __future__ import annotations

import math
from datetime import datetime

import pytest

from packages.t002_eod_unwind.core.feature_computer import (
    PercentileBands,
    compute_features,
)
from packages.t002_eod_unwind.core.session_state import (
    SessionSnapshot,
    SessionState,
    Trade,
)


@pytest.fixture
def bands() -> PercentileBands:
    return PercentileBands(p20=0.3, p60=0.6, p80=0.9)


def _snap(
    open_day: float,
    close: float,
    high: float,
    low: float,
    as_of: datetime = datetime(2024, 3, 15, 16, 55, 0),
) -> SessionSnapshot:
    return SessionSnapshot(
        as_of_ts=as_of,
        open_day=open_day,
        close_at_ts=close,
        session_high=high,
        session_low=low,
    )


def test_formula_parity_with_spec_positive_flow(bands: PercentileBands) -> None:
    """Spec: magnitude = |close - open_day| / ATR_20d; direction = sign(close - open_day).

    close=5250, open_day=5200, ATR_20d=25 ⇒ magnitude = 50/25 = 2.0, direction=+1
    high=5260, low=5190 ⇒ ATR_day = 70 ⇒ atr_day_ratio = 70/25 = 2.8.
    """
    snap = _snap(open_day=5200.0, close=5250.0, high=5260.0, low=5190.0)
    feats = compute_features(snap, atr_20d=25.0, magnitude_bands=bands, atr_ratio_bands=bands)
    assert feats.intraday_flow_direction == 1
    assert feats.intraday_flow_magnitude == pytest.approx(2.0)
    assert feats.atr_day_ratio == pytest.approx(70.0 / 25.0)
    assert feats.flags == frozenset()


def test_direction_negative_when_close_below_open(bands: PercentileBands) -> None:
    snap = _snap(open_day=5200.0, close=5180.0, high=5210.0, low=5175.0)
    feats = compute_features(snap, atr_20d=25.0, magnitude_bands=bands, atr_ratio_bands=bands)
    assert feats.intraday_flow_direction == -1
    assert feats.intraday_flow_magnitude == pytest.approx(20.0 / 25.0)


def test_direction_zero_when_close_equals_open(bands: PercentileBands) -> None:
    """AC4: close == open_day ⇒ direction = 0 exact."""
    snap = _snap(open_day=5200.0, close=5200.0, high=5210.0, low=5190.0)
    feats = compute_features(snap, atr_20d=20.0, magnitude_bands=bands, atr_ratio_bands=bands)
    assert feats.intraday_flow_direction == 0
    assert feats.intraday_flow_magnitude == pytest.approx(0.0)


def test_atr_20d_zero_sets_flag_and_inf(bands: PercentileBands) -> None:
    """AC5: edge — never crashes, flags regime_atr_undefined."""
    snap = _snap(open_day=5200.0, close=5250.0, high=5260.0, low=5190.0)
    feats = compute_features(snap, atr_20d=0.0, magnitude_bands=bands, atr_ratio_bands=bands)
    assert math.isinf(feats.intraday_flow_magnitude)
    assert math.isinf(feats.atr_day_ratio)
    assert "regime_atr_undefined" in feats.flags
    # direction still defined
    assert feats.intraday_flow_direction == 1


def test_atr_20d_negative_defensive_guard(bands: PercentileBands) -> None:
    """Defensive: negative ATR is impossible but we flag rather than crash."""
    snap = _snap(open_day=5200.0, close=5250.0, high=5260.0, low=5190.0)
    feats = compute_features(snap, atr_20d=-1.0, magnitude_bands=bands, atr_ratio_bands=bands)
    assert "regime_atr_undefined" in feats.flags
    assert math.isinf(feats.intraday_flow_magnitude)


def test_pure_determinism(bands: PercentileBands) -> None:
    """AC3: same input → same output across multiple invocations."""
    snap = _snap(open_day=5200.0, close=5237.5, high=5245.0, low=5195.0)
    out1 = compute_features(snap, atr_20d=22.5, magnitude_bands=bands, atr_ratio_bands=bands)
    out2 = compute_features(snap, atr_20d=22.5, magnitude_bands=bands, atr_ratio_bands=bands)
    out3 = compute_features(snap, atr_20d=22.5, magnitude_bands=bands, atr_ratio_bands=bands)
    assert out1 == out2 == out3


def test_features_frozen(bands: PercentileBands) -> None:
    snap = _snap(open_day=5200.0, close=5210.0, high=5220.0, low=5195.0)
    feats = compute_features(snap, atr_20d=25.0, magnitude_bands=bands, atr_ratio_bands=bands)
    with pytest.raises(Exception):
        feats.intraday_flow_direction = 99  # type: ignore[misc]


def test_integration_session_state_to_features(bands: PercentileBands) -> None:
    """End-to-end: push trades → snapshot → compute_features. Parity check."""
    state = SessionState()
    d = datetime(2024, 3, 15, 9, 30, 0)
    state.on_trade(Trade(ts=d, price=5200.0, qty=1))  # open_day
    state.on_trade(Trade(ts=d.replace(hour=10), price=5230.0, qty=1))  # high so far
    state.on_trade(Trade(ts=d.replace(hour=11), price=5190.0, qty=1))  # low so far
    state.on_trade(Trade(ts=d.replace(hour=16, minute=55), price=5220.0, qty=1))
    snap = state.snapshot_at(d.replace(hour=16, minute=55))

    feats = compute_features(snap, atr_20d=20.0, magnitude_bands=bands, atr_ratio_bands=bands)
    # diff = 5220 - 5200 = 20 → magnitude = 20/20 = 1.0
    assert feats.intraday_flow_direction == 1
    assert feats.intraday_flow_magnitude == pytest.approx(1.0)
    # ATR_day = 5230 - 5190 = 40 → ratio = 40/20 = 2.0
    assert feats.atr_day_ratio == pytest.approx(2.0)
