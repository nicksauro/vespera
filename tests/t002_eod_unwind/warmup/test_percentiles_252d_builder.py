"""Tests for Percentiles_252d_builder.

AC3: P20/P60/P80 computed correctly.
AC12: deterministic with known synthetic percentiles.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_252d_builder import (
    DailyMetrics,
    Percentiles252dBuilder,
    Percentiles252dState,
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


def _linspace_metrics(n: int, start_day: date) -> list[DailyMetrics]:
    """Produce n DailyMetrics with magnitude/atr_ratio = i/n."""
    metrics = []
    d = start_day
    i = 0
    while len(metrics) < n:
        if d.weekday() < 5:
            metrics.append(
                DailyMetrics(day=d, magnitude=i / n, atr_day_ratio=i / n)
            )
            i += 1
        d += timedelta(days=1)
    return metrics


def test_p20_p60_p80_on_uniform_distribution(empty_calendar: CalendarData) -> None:
    """With values [0/252, 1/252, ..., 251/252], percentiles approximate linear values."""
    builder = Percentiles252dBuilder(empty_calendar)
    metrics = _linspace_metrics(252, date(2023, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 1, 1, 9, 0))
    # Linear interpolation on 252 values: P20 ≈ 0.199
    assert state.magnitude.p20 == pytest.approx(0.199, abs=0.01)
    assert state.magnitude.p60 == pytest.approx(0.597, abs=0.01)
    assert state.magnitude.p80 == pytest.approx(0.796, abs=0.01)
    assert len(state.window_days) == 252


def test_percentiles_excludes_current_day(empty_calendar: CalendarData) -> None:
    builder = Percentiles252dBuilder(empty_calendar)
    metrics = _linspace_metrics(260, date(2023, 1, 2))
    as_of = metrics[-1].day  # last day itself
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 1, 1, 9, 0))
    assert as_of not in state.window_days


def test_insufficient_history_raises(empty_calendar: CalendarData) -> None:
    builder = Percentiles252dBuilder(empty_calendar)
    metrics = _linspace_metrics(100, date(2023, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    with pytest.raises(ValueError, match="insufficient history"):
        builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 1, 1, 9, 0))


def test_copom_days_excluded() -> None:
    """A Copom day feeds no metric, reducing window size."""
    copom_day = date(2023, 6, 21)
    cal = CalendarData(
        version="test",
        copom_meetings=frozenset({copom_day}),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )
    builder = Percentiles252dBuilder(cal)
    metrics = _linspace_metrics(260, date(2022, 6, 1))
    # Insert the copom day with a wild outlier
    outlier = DailyMetrics(day=copom_day, magnitude=999.0, atr_day_ratio=999.0)
    metrics_with_copom = sorted(metrics + [outlier], key=lambda m: m.day)
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(
        metrics_with_copom, as_of_date=as_of, now_brt=datetime(2024, 1, 1, 9, 0)
    )
    assert copom_day not in state.window_days
    # outlier excluded → P80 stays moderate, not near 999
    assert state.magnitude.p80 < 1.0


def test_persist_and_load_roundtrip(
    empty_calendar: CalendarData, tmp_path: Path
) -> None:
    builder = Percentiles252dBuilder(empty_calendar)
    metrics = _linspace_metrics(260, date(2023, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 1, 1, 9, 0))
    path = tmp_path / "pct.json"
    builder.persist(state, path)
    loaded = builder.load(path)
    assert loaded == state
