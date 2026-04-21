"""Calendar loader for T002 warm-up.

Reads config/calendar/*.yaml and exposes date-membership queries used by
ATR_20d and percentile builders to exclude Copom days, holidays, and
rollover windows (D-3..D-1 before each WDO expiration).

Design reference: docs/architecture/T002-end-of-day-inventory-unwind-design.md §7
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import yaml


@dataclass(frozen=True)
class CalendarData:
    """Immutable view of parsed calendar YAML.

    All dates are BRT-naive (MANIFEST R2).
    """

    version: str
    copom_meetings: frozenset[date]
    br_holidays: frozenset[date]
    wdo_expirations: frozenset[date]
    pre_long_weekends_br_with_us_open: frozenset[date]
    rollover_exclusion_days: int = 3  # D-3..D-1 before expiration
    _rollover_window: frozenset[date] = field(default_factory=frozenset, init=False)

    def __post_init__(self) -> None:
        rollover: set[date] = set()
        for exp in self.wdo_expirations:
            for offset in range(1, self.rollover_exclusion_days + 1):
                rollover.add(exp - timedelta(days=offset))
        object.__setattr__(self, "_rollover_window", frozenset(rollover))

    def is_copom_day(self, d: date) -> bool:
        return d in self.copom_meetings

    def is_br_holiday(self, d: date) -> bool:
        return d in self.br_holidays

    def is_wdo_expiration(self, d: date) -> bool:
        return d in self.wdo_expirations

    def is_rollover_window(self, d: date) -> bool:
        """True if d is in D-3..D-1 of any WDO expiration."""
        return d in self._rollover_window

    def is_business_day(self, d: date) -> bool:
        """True if d is NOT weekend and NOT a BR holiday."""
        return d.weekday() < 5 and d not in self.br_holidays

    def is_valid_sample_day(self, d: date) -> bool:
        """True if d should be included in T002 sample.

        Excludes: weekends, BR holidays, Copom days, rollover windows.
        """
        if not self.is_business_day(d):
            return False
        if self.is_copom_day(d):
            return False
        if self.is_rollover_window(d):
            return False
        return True


class CalendarLoader:
    """Loads calendar YAML and produces an immutable CalendarData.

    Usage:
        cal = CalendarLoader.load(Path("config/calendar/2024-2027.yaml"))
        if cal.is_valid_sample_day(date(2024, 3, 20)):
            ...
    """

    REQUIRED_KEYS: tuple[str, ...] = (
        "copom_meetings",
        "br_holidays",
        "wdo_expirations",
    )

    @staticmethod
    def load(path: Path) -> CalendarData:
        if not path.exists():
            raise FileNotFoundError(f"Calendar file not found: {path}")
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
        if not isinstance(raw, dict):
            raise ValueError(f"Calendar YAML root must be a mapping: {path}")
        for key in CalendarLoader.REQUIRED_KEYS:
            if key not in raw:
                raise ValueError(f"Calendar YAML missing required key '{key}': {path}")
        return CalendarData(
            version=str(raw.get("version", "unknown")),
            copom_meetings=CalendarLoader._parse_dates(raw["copom_meetings"]),
            br_holidays=CalendarLoader._parse_dates(raw["br_holidays"]),
            wdo_expirations=CalendarLoader._parse_dates(raw["wdo_expirations"]),
            pre_long_weekends_br_with_us_open=CalendarLoader._parse_dates(
                raw.get("pre_long_weekends_br_with_us_open", [])
            ),
        )

    @staticmethod
    def _parse_dates(items: Iterable) -> frozenset[date]:
        result: set[date] = set()
        for item in items:
            if isinstance(item, date):
                result.add(item)
            elif isinstance(item, str):
                result.add(date.fromisoformat(item))
            else:
                raise ValueError(f"Invalid date entry: {item!r}")
        return frozenset(result)
