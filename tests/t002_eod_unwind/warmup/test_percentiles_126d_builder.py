"""Tests for Percentiles_126d_builder.

AC3: P20/P60/P80 computed correctly over 126-day window.
AC12: deterministic with known synthetic percentiles (126-day fixture).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    DailyMetrics,
    Percentiles126dBuilder,
    Percentiles126dState,
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
    metrics: list[DailyMetrics] = []
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
    """With values [0/126, 1/126, ..., 125/126], percentiles approximate linear values."""
    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(126, date(2024, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))
    # Linear interpolation on 126 values: P20 ≈ 0.198 (rank 0.2*125=25, value 25/126=0.1984)
    assert state.magnitude.p20 == pytest.approx(0.1984, abs=0.01)
    assert state.magnitude.p60 == pytest.approx(0.5952, abs=0.01)
    assert state.magnitude.p80 == pytest.approx(0.7937, abs=0.01)
    assert len(state.window_days) == 126


def test_returns_percentiles126dstate(empty_calendar: CalendarData) -> None:
    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(130, date(2024, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))
    assert isinstance(state, Percentiles126dState)


def test_percentiles_excludes_current_day(empty_calendar: CalendarData) -> None:
    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(130, date(2024, 1, 2))
    as_of = metrics[-1].day  # last day itself
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))
    assert as_of not in state.window_days


def test_insufficient_history_raises(empty_calendar: CalendarData) -> None:
    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(50, date(2024, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    with pytest.raises(ValueError, match="insufficient history"):
        builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))


def test_copom_days_excluded() -> None:
    """A Copom day feeds no metric, reducing window size."""
    copom_day = date(2024, 3, 20)
    cal = CalendarData(
        version="test",
        copom_meetings=frozenset({copom_day}),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )
    builder = Percentiles126dBuilder(cal)
    metrics = _linspace_metrics(130, date(2024, 1, 2))
    # Insert the copom day with a wild outlier
    outlier = DailyMetrics(day=copom_day, magnitude=999.0, atr_day_ratio=999.0)
    metrics_with_copom = sorted(metrics + [outlier], key=lambda m: m.day)
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(
        metrics_with_copom, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0)
    )
    assert copom_day not in state.window_days
    # outlier excluded → P80 stays moderate, not near 999
    assert state.magnitude.p80 < 1.0


def test_rollover_window_excluded() -> None:
    """D-3..D-1 of WDO expiration must be excluded from sample."""
    expiration = date(2024, 4, 1)  # Monday
    cal = CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset({expiration}),
        pre_long_weekends_br_with_us_open=frozenset(),
    )
    builder = Percentiles126dBuilder(cal)
    metrics = _linspace_metrics(140, date(2023, 10, 2))
    # Insert outliers in rollover window (D-3..D-1)
    rollover_outliers = [
        DailyMetrics(day=expiration - timedelta(days=k), magnitude=999.0, atr_day_ratio=999.0)
        for k in range(1, 4)
    ]
    metrics_w_rollover = sorted(metrics + rollover_outliers, key=lambda m: m.day)
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(
        metrics_w_rollover, as_of_date=as_of, now_brt=datetime(2024, 5, 1, 9, 0)
    )
    for k in range(1, 4):
        assert (expiration - timedelta(days=k)) not in state.window_days
    assert state.magnitude.p80 < 1.0


def test_persist_and_load_roundtrip(
    empty_calendar: CalendarData, tmp_path: Path
) -> None:
    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(130, date(2024, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))
    path = tmp_path / "pct.json"
    builder.persist(state, path)
    loaded = builder.load(path)
    assert loaded == state


def test_persist_writes_expected_schema(
    empty_calendar: CalendarData, tmp_path: Path
) -> None:
    """AC4: state file has as_of_date + computed_at_brt + bands + window_days."""
    import json as _json

    builder = Percentiles126dBuilder(empty_calendar)
    metrics = _linspace_metrics(130, date(2024, 1, 2))
    as_of = metrics[-1].day + timedelta(days=3)
    state = builder.build(metrics, as_of_date=as_of, now_brt=datetime(2024, 7, 1, 9, 0))
    path = tmp_path / "pct.json"
    builder.persist(state, path)
    payload = _json.loads(path.read_text(encoding="utf-8"))
    assert "as_of_date" in payload
    assert "computed_at_brt" in payload
    assert "magnitude" in payload and {"p20", "p60", "p80"} <= set(payload["magnitude"])
    assert "atr_day_ratio" in payload and {"p20", "p60", "p80"} <= set(payload["atr_day_ratio"])
    assert "window_days" in payload
    assert len(payload["window_days"]) == 126
