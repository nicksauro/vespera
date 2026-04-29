"""T002.1.bis — per-fold P126 isolation + D-1 anti-leak invariants.

Per Mira spec §3.4 + §4.2 + Aria T0b APPROVE_OPTION_B + Beckett T0c
``§3 D-1 invariant + per-fold isolation`` verification path.

Covers:
  test_per_fold_p126_rebuild_no_leakage         — fold k's P126 only sees
                                                   train slice (no test
                                                   data contamination)
  test_shifted_by_1_invariant_per_fold          — D-1 enforced by builder
                                                   (m.day < as_of_date)
  test_distinct_p126_per_fold                   — at least 2 folds see
                                                   distinct as_of_date
                                                   ⇒ distinct P126 instance
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import pytest

from packages.t002_eod_unwind.cpcv_harness import (
    _build_daily_metrics_from_train_events,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    DailyMetrics,
    Percentiles126dBuilder,
)


def _make_calendar() -> CalendarData:
    """Calendar that accepts every day as valid sample (no holidays)."""
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _build_train_events(sessions: list[date]) -> pd.DataFrame:
    """Build a minimal train events DataFrame with strategy columns."""
    rows = []
    for s in sessions:
        rows.append(
            {
                "t_start": pd.Timestamp(datetime(s.year, s.month, s.day, 16, 55)),
                "t_end": pd.Timestamp(datetime(s.year, s.month, s.day, 17, 55)),
                "session": s,
                "trial_id": "T1",
                "entry_window": "16:55",
            }
        )
    return pd.DataFrame(rows).reset_index(drop=True)


# =====================================================================
# Test 1 — per-fold P126 only sees training events (no test contamination)
# =====================================================================
def test_per_fold_p126_rebuild_no_leakage() -> None:
    """Per Mira spec §3.1 + §4.2 — fold k's P126 builder consumes ONLY
    fold k's train slice; rebuild must NEVER see test-set days.

    We verify by building DailyMetrics from the train slice + asserting
    that no day in the resulting metrics list belongs to the test
    sessions.
    """
    train_sessions = [date(2024, 1, 1) + timedelta(days=i) for i in range(20)]
    test_sessions = [date(2024, 2, 1) + timedelta(days=i) for i in range(5)]

    train_events = _build_train_events(train_sessions)
    metrics = _build_daily_metrics_from_train_events(train_events, seed_anchor=0)

    # Every metric.day must be in train_sessions, NEVER in test_sessions.
    metric_days = {m.day for m in metrics}
    train_set = set(train_sessions)
    test_set = set(test_sessions)
    assert metric_days <= train_set, (
        "_build_daily_metrics emitted days outside train slice"
    )
    assert metric_days.isdisjoint(test_set), (
        "_build_daily_metrics LEAKED test session days into train metrics"
    )


# =====================================================================
# Test 2 — D-1 invariant: P126 builder rejects same-day or future days
# =====================================================================
def test_shifted_by_1_invariant_per_fold() -> None:
    """Per Mira spec §3.4 + percentiles_126d_builder.py:131-136 —
    ``_select_window`` filters ``m.day < as_of_date``. This is the D-1
    anti-leak invariant: bands are computed over days STRICTLY BEFORE
    the entry session.

    We verify with a minimal DailyMetrics list where as_of_date equals
    the latest day in metrics — that latest day MUST be excluded from
    the window.
    """
    cal = _make_calendar()
    builder = Percentiles126dBuilder(cal)

    # 200 weekday-only metrics across consecutive business days;
    # as_of_date = the day immediately after the latest entry.
    metrics: list[DailyMetrics] = []
    cur = date(2024, 1, 1)
    while len(metrics) < 200:
        if cur.weekday() < 5:  # Monday..Friday
            metrics.append(
                DailyMetrics(
                    day=cur,
                    magnitude=1.0 + 0.01 * len(metrics),
                    atr_day_ratio=0.5 + 0.005 * len(metrics),
                )
            )
        cur += timedelta(days=1)

    last_day = metrics[-1].day
    # as_of_date == last_day → must EXCLUDE last_day per D-1 invariant.
    window = builder._select_window(metrics, last_day)
    assert all(m.day < last_day for m in window), (
        "D-1 invariant violated: window contains as_of_date or later days"
    )
    # Window is the last 126 valid (weekday) days STRICTLY before last_day.
    assert len(window) == 126
    assert window[-1].day < last_day


# =====================================================================
# Test 3 — distinct P126 per fold (different as_of_date ⇒ distinct state)
# =====================================================================
def test_distinct_p126_per_fold() -> None:
    """Per Aria §I.5 + Mira §3.1 — across folds with different
    ``as_of_date`` values, the rebuilt ``Percentiles126dState`` instances
    differ structurally (at least the ``as_of_date`` field).
    """
    cal = _make_calendar()
    builder = Percentiles126dBuilder(cal)
    # 300 weekday-only metrics so 126d windows are satisfied for both
    # as_of_date values below.
    metrics: list[DailyMetrics] = []
    cur = date(2024, 1, 1)
    while len(metrics) < 300:
        if cur.weekday() < 5:
            metrics.append(
                DailyMetrics(
                    day=cur,
                    magnitude=1.0 + 0.01 * len(metrics),
                    atr_day_ratio=0.5 + 0.005 * len(metrics),
                )
            )
        cur += timedelta(days=1)

    as_of_a = date(2024, 12, 16)
    as_of_b = date(2025, 1, 16)

    state_a = builder.build(metrics, as_of_date=as_of_a, now_brt=datetime.now())
    state_b = builder.build(metrics, as_of_date=as_of_b, now_brt=datetime.now())

    assert state_a.as_of_date == as_of_a
    assert state_b.as_of_date == as_of_b
    assert state_a.as_of_date != state_b.as_of_date
    # Window contents shifted ⇒ band values likely differ (deterministic mix).
    assert state_a.window_days != state_b.window_days


# =====================================================================
# Test 4 — fold-local seed anchor produces distinct metrics across folds
# =====================================================================
def test_seed_anchor_distinguishes_folds() -> None:
    """Per ``_build_daily_metrics_from_train_events`` ``seed_anchor`` —
    the same train slice with different ``seed_anchor`` values (path_id)
    yields different per-day magnitudes / ATR ratios. This is essential
    for cross-fold isolation: each CPCV path gets its own fold-local
    P126 even when train slices overlap.
    """
    train_sessions = [date(2024, 1, 1) + timedelta(days=i) for i in range(10)]
    train_events = _build_train_events(train_sessions)

    metrics_path_0 = _build_daily_metrics_from_train_events(
        train_events, seed_anchor=0
    )
    metrics_path_42 = _build_daily_metrics_from_train_events(
        train_events, seed_anchor=42
    )

    # Same days, but at least some metric values differ.
    days_0 = [m.day for m in metrics_path_0]
    days_42 = [m.day for m in metrics_path_42]
    assert days_0 == days_42  # same train slice → same days

    mags_0 = [m.magnitude for m in metrics_path_0]
    mags_42 = [m.magnitude for m in metrics_path_42]
    assert mags_0 != mags_42, (
        "seed_anchor doesn't differentiate folds — cross-fold isolation broken"
    )


# =====================================================================
# Test 5 — _build_daily_metrics_from_train_events fail-closed on bad input
# =====================================================================
def test_build_daily_metrics_rejects_missing_session_column() -> None:
    """Defensive — caller must pass a DataFrame with a ``session`` column."""
    bad_df = pd.DataFrame({"foo": [1, 2, 3]})
    with pytest.raises(ValueError, match="session"):
        _build_daily_metrics_from_train_events(bad_df)
