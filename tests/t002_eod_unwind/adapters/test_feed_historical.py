"""Tests for HistoricalTradesReplay."""

from __future__ import annotations

from datetime import date, datetime

import pytest

from packages.t002_eod_unwind.adapters.feed_historical import (
    HistoricalTradesReplay,
    TradeEvent,
)
from packages.t002_eod_unwind.core.session_state import Trade
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData


@pytest.fixture
def empty_calendar() -> CalendarData:
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def test_emits_trade_events_in_order(empty_calendar: CalendarData) -> None:
    trades = [
        Trade(ts=datetime(2024, 3, 15, 10, 0), price=5200.0, qty=1),
        Trade(ts=datetime(2024, 3, 15, 10, 1), price=5201.0, qty=2),
    ]
    replay = HistoricalTradesReplay(trades, empty_calendar)
    events = list(replay)
    assert len(events) == 2
    assert isinstance(events[0], TradeEvent)
    assert events[0].price == 5200.0
    assert events[1].qty == 2


def test_skips_copom_days() -> None:
    cal = CalendarData(
        version="test",
        copom_meetings=frozenset({date(2024, 3, 15)}),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )
    trades = [
        Trade(ts=datetime(2024, 3, 14, 10, 0), price=5200.0, qty=1),  # ok
        Trade(ts=datetime(2024, 3, 15, 10, 0), price=5210.0, qty=1),  # Copom — skip
        Trade(ts=datetime(2024, 3, 18, 10, 0), price=5220.0, qty=1),  # ok (Mon)
    ]
    events = list(HistoricalTradesReplay(trades, cal))
    dates = {e.ts.date() for e in events}
    assert date(2024, 3, 15) not in dates
    assert date(2024, 3, 14) in dates
    assert date(2024, 3, 18) in dates


def test_out_of_order_raises(empty_calendar: CalendarData) -> None:
    trades = [
        Trade(ts=datetime(2024, 3, 15, 10, 1), price=5200.0, qty=1),
        Trade(ts=datetime(2024, 3, 15, 10, 0), price=5201.0, qty=1),
    ]
    with pytest.raises(ValueError, match="ascending ts"):
        list(HistoricalTradesReplay(trades, empty_calendar))


def test_schema_matches_trade_event(empty_calendar: CalendarData) -> None:
    """AC6: TradeEvent has the same shape as live feed will produce."""
    trades = [Trade(ts=datetime(2024, 3, 15, 10, 0), price=5200.0, qty=1)]
    ev = next(iter(HistoricalTradesReplay(trades, empty_calendar)))
    assert set(ev.__dataclass_fields__.keys()) == {"ts", "price", "qty"}
