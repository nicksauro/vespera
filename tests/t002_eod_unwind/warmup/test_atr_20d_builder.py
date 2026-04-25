"""Tests for ATR_20d_builder.

AC1: output struct with correct fields.
AC12: deterministic — synthetic fixtures produce known ATR within 0.01.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from packages.t002_eod_unwind.warmup.atr_20d_builder import (
    ATR20dBuilder,
    ATR20dState,
    Trade,
)
from packages.t002_eod_unwind.warmup.calendar_loader import (
    CalendarData,
)


@pytest.fixture
def empty_calendar() -> CalendarData:
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _make_day_trades(d: date, open_p: float, high: float, low: float, close: float) -> list[Trade]:
    """Produce trades such that aggregation yields the requested OHLC."""
    ts_base = datetime(d.year, d.month, d.day, 10, 0, 0)
    return [
        Trade(ts=ts_base, price=open_p, qty=1),
        Trade(ts=ts_base + timedelta(minutes=1), price=high, qty=1),
        Trade(ts=ts_base + timedelta(minutes=2), price=low, qty=1),
        Trade(ts=ts_base + timedelta(minutes=3), price=close, qty=1),
    ]


def test_atr_constant_range_equals_range(empty_calendar: CalendarData) -> None:
    """20 days with identical OHLC: ATR == high-low == constant."""
    builder = ATR20dBuilder(empty_calendar)
    # 20 business days ending on a Friday
    days = [date(2024, 1, 2) + timedelta(days=i) for i in range(30)]
    days = [d for d in days if d.weekday() < 5][:20]
    trades: list[Trade] = []
    for d in days:
        trades.extend(_make_day_trades(d, 5000.0, 5010.0, 4990.0, 5005.0))
    as_of = days[-1] + timedelta(days=1)
    while as_of.weekday() >= 5:
        as_of += timedelta(days=1)
    state = builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 2, 15, 9, 0))
    assert isinstance(state, ATR20dState)
    assert state.atr == pytest.approx(20.0, abs=0.01)
    assert len(state.window_days) == 20


def test_atr_uses_true_range_with_gap(empty_calendar: CalendarData) -> None:
    """Gap between days lifts true range above high-low."""
    builder = ATR20dBuilder(empty_calendar)
    # 20 days, each range=10, consecutive closes drift up by 50 → TR=60 for days 2..20
    days_all = [date(2024, 1, 2) + timedelta(days=i) for i in range(40)]
    days = [d for d in days_all if d.weekday() < 5][:20]
    trades: list[Trade] = []
    base = 5000.0
    for i, d in enumerate(days):
        mid = base + i * 50.0
        trades.extend(_make_day_trades(d, mid, mid + 5, mid - 5, mid))
    as_of = days[-1] + timedelta(days=3)
    state = builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 2, 15, 9, 0))
    # day 0: TR=10; days 1..19: TR=max(10, |high-prev_close|, |low-prev_close|)
    # prev_close drifts by 50, so TR = |mid+5 - (prev_mid)| = 55
    # Mean = (10 + 55*19)/20 = 52.75
    assert state.atr == pytest.approx(52.75, abs=0.01)


def test_atr_excludes_copom_and_rollover() -> None:
    cal = CalendarData(
        version="test",
        copom_meetings=frozenset({date(2024, 1, 31)}),
        br_holidays=frozenset(),
        wdo_expirations=frozenset({date(2024, 2, 1)}),  # rollover: 1/29, 1/30, 1/31
        pre_long_weekends_br_with_us_open=frozenset(),
    )
    builder = ATR20dBuilder(cal)
    # 25 business days to have enough after exclusions
    trades: list[Trade] = []
    all_days = [date(2024, 1, 2) + timedelta(days=i) for i in range(45)]
    bdays = [d for d in all_days if d.weekday() < 5][:25]
    for d in bdays:
        trades.extend(_make_day_trades(d, 5000.0, 5010.0, 4990.0, 5005.0))
    as_of = bdays[-1] + timedelta(days=3)
    state = builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 3, 1, 9, 0))
    excluded = {date(2024, 1, 29), date(2024, 1, 30), date(2024, 1, 31)}
    for d in excluded:
        assert d not in state.window_days


def test_atr_insufficient_history_raises(empty_calendar: CalendarData) -> None:
    builder = ATR20dBuilder(empty_calendar)
    # only 10 days
    days = [date(2024, 1, 2) + timedelta(days=i) for i in range(20)]
    days = [d for d in days if d.weekday() < 5][:10]
    trades: list[Trade] = []
    for d in days:
        trades.extend(_make_day_trades(d, 5000.0, 5010.0, 4990.0, 5005.0))
    as_of = days[-1] + timedelta(days=3)
    with pytest.raises(ValueError, match="insufficient history"):
        builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 2, 1, 9, 0))


def test_atr_never_includes_current_day(empty_calendar: CalendarData) -> None:
    """No look-ahead: as_of_date itself must not appear in window."""
    builder = ATR20dBuilder(empty_calendar)
    days = [date(2024, 1, 2) + timedelta(days=i) for i in range(50)]
    days = [d for d in days if d.weekday() < 5][:21]
    trades: list[Trade] = []
    for d in days:
        trades.extend(_make_day_trades(d, 5000.0, 5010.0, 4990.0, 5005.0))
    as_of = days[-1]  # last day
    state = builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 3, 1, 9, 0))
    assert as_of not in state.window_days


def test_persist_and_load_roundtrip(empty_calendar: CalendarData, tmp_path: Path) -> None:
    builder = ATR20dBuilder(empty_calendar)
    days = [date(2024, 1, 2) + timedelta(days=i) for i in range(35)]
    days = [d for d in days if d.weekday() < 5][:20]
    trades: list[Trade] = []
    for d in days:
        trades.extend(_make_day_trades(d, 5000.0, 5010.0, 4990.0, 5005.0))
    as_of = days[-1] + timedelta(days=3)
    state = builder.build(trades, as_of_date=as_of, now_brt=datetime(2024, 3, 1, 9, 0))
    path = tmp_path / "atr.json"
    builder.persist(state, path)
    loaded = builder.load(path)
    assert loaded == state
