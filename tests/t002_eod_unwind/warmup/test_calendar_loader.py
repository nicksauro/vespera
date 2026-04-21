"""Tests for calendar_loader.

AC7: calendar is single source for Copom/holidays/expirations.
AC8: BRT-naive (no tz conversion anywhere).
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from packages.t002_eod_unwind.warmup.calendar_loader import (
    CalendarData,
    CalendarLoader,
)


@pytest.fixture
def calendar_yaml(tmp_path: Path) -> Path:
    content = """
version: "test"
copom_meetings:
  - "2024-01-31"
  - "2024-03-20"
br_holidays:
  - "2024-01-01"
  - "2024-02-12"
wdo_expirations:
  - "2024-02-01"
  - "2024-03-01"
pre_long_weekends_br_with_us_open:
  - "2024-02-09"
"""
    p = tmp_path / "cal.yaml"
    p.write_text(content, encoding="utf-8")
    return p


def test_load_returns_calendar_data(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    assert isinstance(cal, CalendarData)
    assert cal.version == "test"
    assert date(2024, 1, 31) in cal.copom_meetings
    assert date(2024, 1, 1) in cal.br_holidays
    assert date(2024, 2, 1) in cal.wdo_expirations


def test_is_copom_day_positive(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    assert cal.is_copom_day(date(2024, 1, 31)) is True
    assert cal.is_copom_day(date(2024, 1, 30)) is False


def test_is_br_holiday(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    assert cal.is_br_holiday(date(2024, 1, 1)) is True
    assert cal.is_br_holiday(date(2024, 1, 2)) is False


def test_rollover_window_covers_d3_d2_d1(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    # WDO expiration 2024-02-01 → rollover: 2024-01-29, 30, 31
    assert cal.is_rollover_window(date(2024, 1, 29)) is True
    assert cal.is_rollover_window(date(2024, 1, 30)) is True
    assert cal.is_rollover_window(date(2024, 1, 31)) is True
    # expiration day itself is NOT in rollover window
    assert cal.is_rollover_window(date(2024, 2, 1)) is False
    # D-4 is NOT
    assert cal.is_rollover_window(date(2024, 1, 28)) is False


def test_is_business_day_excludes_weekend(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    # 2024-01-06 was a Saturday
    assert cal.is_business_day(date(2024, 1, 6)) is False
    # 2024-01-02 was a Tuesday (not in holidays fixture)
    assert cal.is_business_day(date(2024, 1, 2)) is True


def test_is_valid_sample_day_combines_all_filters(calendar_yaml: Path) -> None:
    cal = CalendarLoader.load(calendar_yaml)
    # 2024-01-31 is Copom → invalid AND rollover window for 2024-02-01 expiration
    assert cal.is_valid_sample_day(date(2024, 1, 31)) is False
    # 2024-01-01 is holiday
    assert cal.is_valid_sample_day(date(2024, 1, 1)) is False
    # 2024-01-06 is Saturday
    assert cal.is_valid_sample_day(date(2024, 1, 6)) is False
    # 2024-01-03 is Wednesday, no holiday, not copom, not rollover
    assert cal.is_valid_sample_day(date(2024, 1, 3)) is True


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        CalendarLoader.load(tmp_path / "does-not-exist.yaml")


def test_missing_required_key_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("version: test\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required key"):
        CalendarLoader.load(bad)


def test_invalid_date_format_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        "copom_meetings: ['not-a-date']\n"
        "br_holidays: []\n"
        "wdo_expirations: []\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        CalendarLoader.load(bad)


def test_loads_real_project_calendar() -> None:
    """AC7 smoke: production calendar file parses without error."""
    project_root = Path(__file__).resolve().parents[3]
    cal_path = project_root / "config" / "calendar" / "2024-2027.yaml"
    if not cal_path.exists():
        pytest.skip("project calendar not yet installed")
    cal = CalendarLoader.load(cal_path)
    assert date(2024, 1, 31) in cal.copom_meetings
    assert date(2026, 1, 1) in cal.br_holidays
