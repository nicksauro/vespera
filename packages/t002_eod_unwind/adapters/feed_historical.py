"""HistoricalTradesReplay — layer 1 backtest adapter.

Consumes an iterable of `Trade(ts, price, qty)` and yields `TradeEvent`
with identical schema to the live feed contract. Filters out days that
are NOT valid_sample_day per the calendar (Copom, holidays, rollover
window D-3..D-1).

AC6: schema parity with live feed. AC7: pre-session filter via calendar.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime

from ..core.session_state import Trade
from ..warmup.calendar_loader import CalendarData


@dataclass(frozen=True)
class TradeEvent:
    """Public schema — same for backtest and live (AC6)."""

    ts: datetime
    price: float
    qty: int


class HistoricalTradesReplay:
    """Replay historical trades as `TradeEvent` stream.

    Caller provides trades already sorted by ts ascending. A day that is
    NOT `calendar.is_valid_sample_day` is skipped entirely (all its
    trades discarded — the backtest runner never sees them).
    """

    def __init__(self, trades: Iterable[Trade], calendar: CalendarData) -> None:
        self._trades = trades
        self._calendar = calendar

    def __iter__(self) -> Iterator[TradeEvent]:
        last_ts: datetime | None = None
        for t in self._trades:
            if last_ts is not None and t.ts < last_ts:
                raise ValueError(
                    f"HistoricalTradesReplay requires ascending ts — got "
                    f"{t.ts} after {last_ts}"
                )
            last_ts = t.ts
            if not self._calendar.is_valid_sample_day(t.ts.date()):
                continue
            yield TradeEvent(ts=t.ts, price=t.price, qty=t.qty)
