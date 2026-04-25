"""Tests for SessionState.

AC1: O(1) mutation per trade; open_day fixed by first trade >= 09:30 BRT.
AC2: snapshot_at(ts) returns close <= ts — anti-leakage.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from packages.t002_eod_unwind.core.session_state import (
    SessionState,
    Trade,
)


def _ts(h: int, m: int, s: int = 0, d: date = date(2024, 3, 15)) -> datetime:
    return datetime(d.year, d.month, d.day, h, m, s)


def test_open_day_set_by_first_trade_at_or_after_session_open() -> None:
    state = SessionState()
    # pre-open trade (defensive — shouldn't happen) — must NOT set open_day
    state.on_trade(Trade(ts=_ts(9, 15), price=5200.0, qty=1))
    assert state.open_day is None
    # first post-open trade sets it
    state.on_trade(Trade(ts=_ts(9, 30), price=5210.0, qty=2))
    assert state.open_day == 5210.0
    # subsequent trades never overwrite
    state.on_trade(Trade(ts=_ts(9, 35), price=5215.0, qty=1))
    assert state.open_day == 5210.0


def test_session_high_low_and_last_track_monotonically() -> None:
    state = SessionState()
    state.on_trade(Trade(ts=_ts(9, 30), price=5200.0, qty=1))
    state.on_trade(Trade(ts=_ts(10, 0), price=5220.0, qty=1))
    state.on_trade(Trade(ts=_ts(11, 0), price=5180.0, qty=1))
    state.on_trade(Trade(ts=_ts(12, 0), price=5190.0, qty=1))
    assert state.session_high == 5220.0
    assert state.session_low == 5180.0
    assert state.last_price == 5190.0
    assert state.last_ts == _ts(12, 0)


def test_out_of_order_trade_raises() -> None:
    state = SessionState()
    state.on_trade(Trade(ts=_ts(10, 0), price=5200.0, qty=1))
    with pytest.raises(ValueError, match="out-of-order"):
        state.on_trade(Trade(ts=_ts(9, 59), price=5201.0, qty=1))


def test_snapshot_at_returns_last_price_leq_ts() -> None:
    """AC2: snapshot never sees a future price."""
    state = SessionState()
    state.on_trade(Trade(ts=_ts(9, 30), price=5200.0, qty=1))
    state.on_trade(Trade(ts=_ts(16, 54, 59), price=5250.0, qty=1))
    # caller wants snapshot at 16:55:00 exactly, last trade is at 16:54:59
    snap = state.snapshot_at(_ts(16, 55, 0))
    assert snap.close_at_ts == 5250.0
    assert snap.open_day == 5200.0
    assert snap.as_of_ts == _ts(16, 55, 0)


def test_snapshot_at_rejects_ts_before_last_ts() -> None:
    """Defensive: caller must buffer correctly — pushing trade at 17:00 then
    asking for snapshot_at 16:55 is a bug that WOULD leak future info."""
    state = SessionState()
    state.on_trade(Trade(ts=_ts(9, 30), price=5200.0, qty=1))
    state.on_trade(Trade(ts=_ts(17, 0), price=5260.0, qty=1))
    with pytest.raises(ValueError, match="anti-leakage"):
        state.snapshot_at(_ts(16, 55))


def test_snapshot_before_any_trade_raises() -> None:
    state = SessionState()
    with pytest.raises(ValueError, match="before any trade"):
        state.snapshot_at(_ts(16, 55))


def test_snapshot_before_session_open_raises() -> None:
    """State has trades pre-open but no post-open trade — open_day still None."""
    state = SessionState()
    state.on_trade(Trade(ts=_ts(9, 15), price=5200.0, qty=1))
    with pytest.raises(ValueError, match="before session open"):
        state.snapshot_at(_ts(9, 20))


def test_snapshot_is_frozen_dataclass() -> None:
    state = SessionState()
    state.on_trade(Trade(ts=_ts(9, 30), price=5200.0, qty=1))
    snap = state.snapshot_at(_ts(9, 30))
    with pytest.raises(Exception):  # FrozenInstanceError
        snap.close_at_ts = 0.0  # type: ignore[misc]


def test_brt_naive_throughout() -> None:
    """R2: all timestamps are naive — no tzinfo anywhere."""
    state = SessionState()
    t = Trade(ts=_ts(9, 30), price=5200.0, qty=1)
    assert t.ts.tzinfo is None
    state.on_trade(t)
    snap = state.snapshot_at(_ts(10, 0))
    assert snap.as_of_ts.tzinfo is None
