"""Percentiles_252d rolling builder for T002 warm-up.

Computes rolling percentiles (P20, P60, P80) over 252 valid business days
for two series:

  1. magnitude     = |close[16:55] - open_day| / ATR_20d_of_that_day
  2. atr_day_ratio = ATR_day / ATR_20d_of_that_day

These percentiles gate signal emission: the strategy fires only when
magnitude > P60 AND atr_day_ratio is between P20 and P80 on the current
day (computed against history-only percentiles, shifted by 1 day).

Design reference:
- docs/architecture/T002-end-of-day-inventory-unwind-design.md §3.2
- docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml trading_rules

MANIFEST:
- R2 BRT naive timestamps
- R7 trades-only
- R11 pure computation — no orchestration, no DLL calls
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Mapping, Sequence


@dataclass(frozen=True)
class DailyMetrics:
    """Per-day metrics feeding the percentile computation."""

    day: date
    magnitude: float
    atr_day_ratio: float


@dataclass(frozen=True)
class PercentileBands:
    p20: float
    p60: float
    p80: float

    def to_json(self) -> dict:
        return {"p20": self.p20, "p60": self.p60, "p80": self.p80}

    @classmethod
    def from_json(cls, data: Mapping) -> "PercentileBands":
        return cls(p20=float(data["p20"]), p60=float(data["p60"]), p80=float(data["p80"]))


@dataclass(frozen=True)
class Percentiles252dState:
    as_of_date: date
    magnitude: PercentileBands
    atr_day_ratio: PercentileBands
    window_days: tuple[date, ...]
    computed_at_brt: datetime

    def to_json(self) -> dict:
        return {
            "as_of_date": self.as_of_date.isoformat(),
            "magnitude": self.magnitude.to_json(),
            "atr_day_ratio": self.atr_day_ratio.to_json(),
            "window_days": [d.isoformat() for d in self.window_days],
            "computed_at_brt": self.computed_at_brt.isoformat(),
        }

    @classmethod
    def from_json(cls, data: Mapping) -> "Percentiles252dState":
        return cls(
            as_of_date=date.fromisoformat(data["as_of_date"]),
            magnitude=PercentileBands.from_json(data["magnitude"]),
            atr_day_ratio=PercentileBands.from_json(data["atr_day_ratio"]),
            window_days=tuple(date.fromisoformat(x) for x in data["window_days"]),
            computed_at_brt=datetime.fromisoformat(data["computed_at_brt"]),
        )


class Percentiles252dBuilder:
    """Builds 252-day rolling percentiles from per-day metrics."""

    WINDOW: int = 252

    def __init__(self, calendar) -> None:
        self._cal = calendar

    def build(
        self,
        metrics: Sequence[DailyMetrics],
        as_of_date: date,
        now_brt: datetime,
    ) -> Percentiles252dState:
        window = self._select_window(metrics, as_of_date)
        if len(window) < self.WINDOW:
            raise ValueError(
                f"insufficient history: need {self.WINDOW} valid days, got {len(window)}"
            )
        magnitudes = sorted(m.magnitude for m in window)
        atr_ratios = sorted(m.atr_day_ratio for m in window)
        return Percentiles252dState(
            as_of_date=as_of_date,
            magnitude=PercentileBands(
                p20=self._percentile(magnitudes, 20),
                p60=self._percentile(magnitudes, 60),
                p80=self._percentile(magnitudes, 80),
            ),
            atr_day_ratio=PercentileBands(
                p20=self._percentile(atr_ratios, 20),
                p60=self._percentile(atr_ratios, 60),
                p80=self._percentile(atr_ratios, 80),
            ),
            window_days=tuple(m.day for m in window),
            computed_at_brt=now_brt,
        )

    def _select_window(
        self, metrics: Sequence[DailyMetrics], as_of_date: date
    ) -> list[DailyMetrics]:
        eligible = [
            m
            for m in sorted(metrics, key=lambda m: m.day)
            if m.day < as_of_date and self._cal.is_valid_sample_day(m.day)
        ]
        return eligible[-self.WINDOW :]

    @staticmethod
    def _percentile(sorted_values: Sequence[float], p: float) -> float:
        """Linear-interpolation percentile (type 7, matches numpy default)."""
        if not sorted_values:
            raise ValueError("empty sequence")
        n = len(sorted_values)
        if n == 1:
            return sorted_values[0]
        rank = (p / 100.0) * (n - 1)
        low_idx = int(rank)
        frac = rank - low_idx
        if low_idx + 1 >= n:
            return sorted_values[-1]
        return sorted_values[low_idx] + frac * (
            sorted_values[low_idx + 1] - sorted_values[low_idx]
        )

    def persist(self, state: Percentiles252dState, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            json.dump(state.to_json(), fh, indent=2)

    def load(self, path: Path) -> Percentiles252dState:
        with path.open("r", encoding="utf-8") as fh:
            return Percentiles252dState.from_json(json.load(fh))
