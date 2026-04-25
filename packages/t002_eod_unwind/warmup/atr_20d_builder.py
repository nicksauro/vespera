"""ATR_20d rolling builder for T002 warm-up.

Aggregates trades into daily OHLC, computes true range per day, then
rolling 20-day average. Persists state to disk for fast startup.

Design reference:
- docs/architecture/T002-end-of-day-inventory-unwind-design.md §3.1
- docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml feature_set[1]

MANIFEST:
- R2: all timestamps BRT-naive
- R5: GetHistoryTrades must be called in a worker thread; this module is
  pure computation and does NOT call the DLL — the caller (session
  bootstrap) supplies the trades iterable.
- R7: trades-only (no book dependency)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Sequence


@dataclass(frozen=True)
class Trade:
    """Minimal trade record. BRT-naive timestamp (R2)."""

    ts: datetime
    price: float
    qty: int


@dataclass(frozen=True)
class DailyOHLC:
    """Single-session OHLC derived from trades."""

    day: date
    open: float
    high: float
    low: float
    close: float
    volume_contracts: int


@dataclass(frozen=True)
class ATR20dState:
    """Persisted ATR_20d computation, keyed by as_of_date.

    `atr` is the rolling 20-day average true range ending at the last
    business day <= as_of_date that was a valid sample day.

    `window_days` contains the exact sequence of days used — needed for
    reproducibility and audit.
    """

    as_of_date: date
    atr: float
    window_days: tuple[date, ...]
    computed_at_brt: datetime

    def to_json(self) -> dict:
        return {
            "as_of_date": self.as_of_date.isoformat(),
            "atr": self.atr,
            "window_days": [d.isoformat() for d in self.window_days],
            "computed_at_brt": self.computed_at_brt.isoformat(),
        }

    @classmethod
    def from_json(cls, data: dict) -> "ATR20dState":
        return cls(
            as_of_date=date.fromisoformat(data["as_of_date"]),
            atr=float(data["atr"]),
            window_days=tuple(date.fromisoformat(x) for x in data["window_days"]),
            computed_at_brt=datetime.fromisoformat(data["computed_at_brt"]),
        )


class ATR20dBuilder:
    """Builds 20-day rolling ATR from trade history.

    Design contract:
    - Caller passes a trades iterable already fetched (ProfitDLL via worker
      thread — not our concern). Pure computation here.
    - Output covers the 20 most recent valid-sample days <= as_of_date - 1.
      Current day is NEVER included (avoids look-ahead).
    - prev_close fallback: when aggregating the oldest day in the window,
      use that day's open as prev_close (true-range reduces to high-low).
      This is a well-known edge; it affects <=1 day out of 20 and is
      conservative.
    """

    WINDOW: int = 20

    def __init__(self, calendar) -> None:
        self._cal = calendar

    def build(
        self,
        trades: Iterable[Trade],
        as_of_date: date,
        now_brt: datetime,
    ) -> ATR20dState:
        daily = self._aggregate_daily(trades)
        window = self._select_window(daily, as_of_date)
        if len(window) < self.WINDOW:
            raise ValueError(
                f"insufficient history: need {self.WINDOW} valid days, got {len(window)}"
            )
        atr = self._compute_atr(window)
        return ATR20dState(
            as_of_date=as_of_date,
            atr=atr,
            window_days=tuple(ohlc.day for ohlc in window),
            computed_at_brt=now_brt,
        )

    def _aggregate_daily(self, trades: Iterable[Trade]) -> list[DailyOHLC]:
        buckets: dict[date, list[Trade]] = {}
        for tr in trades:
            buckets.setdefault(tr.ts.date(), []).append(tr)
        days: list[DailyOHLC] = []
        for day, trs in sorted(buckets.items()):
            trs_sorted = sorted(trs, key=lambda t: t.ts)
            prices = [t.price for t in trs_sorted]
            days.append(
                DailyOHLC(
                    day=day,
                    open=prices[0],
                    high=max(prices),
                    low=min(prices),
                    close=prices[-1],
                    volume_contracts=sum(t.qty for t in trs_sorted),
                )
            )
        return days

    def _select_window(
        self, daily: Sequence[DailyOHLC], as_of_date: date
    ) -> list[DailyOHLC]:
        eligible = [
            d
            for d in daily
            if d.day < as_of_date and self._cal.is_valid_sample_day(d.day)
        ]
        return eligible[-self.WINDOW :]

    def _compute_atr(self, window: Sequence[DailyOHLC]) -> float:
        true_ranges: list[float] = []
        for i, day in enumerate(window):
            if i == 0:
                true_ranges.append(day.high - day.low)
            else:
                prev_close = window[i - 1].close
                tr = max(
                    day.high - day.low,
                    abs(day.high - prev_close),
                    abs(day.low - prev_close),
                )
                true_ranges.append(tr)
        return sum(true_ranges) / len(true_ranges)

    def persist(self, state: ATR20dState, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(state.to_json(), fh, indent=2)

    def load(self, path: Path) -> ATR20dState:
        with path.open("r", encoding="utf-8") as fh:
            return ATR20dState.from_json(json.load(fh))
