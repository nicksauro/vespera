"""T4 — tests for ``build_events_dataframe`` (AC1 of Story T002.0f).

Coverage:
    test_columns_and_dtypes              — AC1 canonical columns + dtypes
    test_warmup_gate_fires               — AC1 RuntimeError when gate not READY
    test_invalid_session_skipped         — AC1 holiday/weekend dropped (not raised)
    test_index_monotonic_increasing      — AC1 engine invariant on returned index
    test_trial_filter_subset             — AC1 trials param subset validated
    test_unknown_trial_rejected          — AC1 ValueError on bad trial id
    test_end_before_start_rejected       — AC1 ValueError on inverted window
    test_empty_window_after_calendar     — AC1 ValueError when no valid sessions

Synthetic fixtures only — no parquet IO. Real warmup state files are
mocked via injected ``WarmUpGate`` instances pointing at tmp_path JSON
files (matching ``WarmUpGate.check`` schema).
"""

from __future__ import annotations

import json
from datetime import date, time
from pathlib import Path

import pandas as pd
import pytest

from packages.t002_eod_unwind.cpcv_harness import (
    ENTRY_WINDOWS_BRT,
    TRIALS_DEFAULT,
    build_events_dataframe,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.gate import WarmUpGate


# =====================================================================
# Fixtures
# =====================================================================
def _make_calendar(
    holidays: frozenset[date] = frozenset(),
    copom: frozenset[date] = frozenset(),
    expirations: frozenset[date] = frozenset(),
) -> CalendarData:
    """Build a minimal CalendarData with optional exclusions."""
    return CalendarData(
        version="test-fixture",
        copom_meetings=copom,
        br_holidays=holidays,
        wdo_expirations=expirations,
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _write_warmup_state(
    tmp_path: Path,
    as_of: date,
    *,
    atr_valid: bool = True,
    pct_valid: bool = True,
) -> tuple[Path, Path]:
    """Write atr_20d.json + percentiles_126d.json with the given as_of_date."""
    atr_path = tmp_path / "atr_20d.json"
    pct_path = tmp_path / "percentiles_126d.json"
    atr_payload = {"as_of_date": as_of.isoformat() if atr_valid else "1900-01-01"}
    pct_payload = {"as_of_date": as_of.isoformat() if pct_valid else "1900-01-01"}
    atr_path.write_text(json.dumps(atr_payload), encoding="utf-8")
    pct_path.write_text(json.dumps(pct_payload), encoding="utf-8")
    return atr_path, pct_path


def _make_ready_gate(tmp_path: Path, as_of: date) -> WarmUpGate:
    atr, pct = _write_warmup_state(tmp_path, as_of)
    return WarmUpGate(atr, pct)


# =====================================================================
# AC1 — columns + dtypes
# =====================================================================
def test_columns_and_dtypes(tmp_path: Path) -> None:
    """Per AC1 — canonical columns, BRT-naive timestamps, str trial_id."""
    start = date(2024, 7, 1)  # Monday — valid sample day
    end = date(2024, 7, 5)    # Friday — 5 business days
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)

    # Canonical column order (AC1).
    assert list(df.columns) == ["t_start", "t_end", "session", "trial_id", "entry_window"]
    # Per AC1 — t_start, t_end pd.Timestamp BRT-naive (R2: no tz attached).
    assert df["t_start"].dtype.kind == "M", f"t_start should be datetime64, got {df['t_start'].dtype}"
    assert df["t_end"].dtype.kind == "M"
    assert df["t_start"].dt.tz is None
    assert df["t_end"].dt.tz is None
    # session: python date objects (object dtype in pandas).
    first_session = df["session"].iloc[0]
    assert isinstance(first_session, date)
    # trial_id + entry_window are strings.
    assert df["trial_id"].iloc[0] in TRIALS_DEFAULT
    assert df["entry_window"].iloc[0] in ENTRY_WINDOWS_BRT
    # 5 business days × 4 windows × 5 trials = 100 rows.
    assert len(df) == 5 * len(ENTRY_WINDOWS_BRT) * len(TRIALS_DEFAULT)


# =====================================================================
# AC1 — warmup gate fires
# =====================================================================
def test_warmup_gate_fires_when_not_ready(tmp_path: Path) -> None:
    """Per AC1 + Pax gap #1 — gate not READY ⇒ RuntimeError."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 5)
    cal = _make_calendar()
    # Stale state files: as_of != start.
    atr, pct = _write_warmup_state(tmp_path, start, atr_valid=False, pct_valid=False)
    stale_gate = WarmUpGate(atr, pct)

    with pytest.raises(RuntimeError, match="warmup not satisfied"):
        build_events_dataframe(
            start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=stale_gate
        )


def test_warmup_gate_fires_when_files_missing(tmp_path: Path) -> None:
    """Per AC1 — missing state files ⇒ WARM_UP_IN_PROGRESS ⇒ RuntimeError."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 5)
    cal = _make_calendar()
    # Point at non-existent files.
    missing_gate = WarmUpGate(tmp_path / "nope_atr.json", tmp_path / "nope_pct.json")

    with pytest.raises(RuntimeError, match="WARM_UP_IN_PROGRESS"):
        build_events_dataframe(
            start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=missing_gate
        )


# =====================================================================
# AC1 — invalid sessions skipped (not raised)
# =====================================================================
def test_invalid_session_skipped(tmp_path: Path) -> None:
    """Per AC1 + Nova T0 handshake — holidays/weekends are SKIPPED, not raised.

    Window 2024-07-01 (Mon) .. 2024-07-07 (Sun) = 5 business days; weekends
    auto-skipped via ``is_business_day``. We additionally insert 2024-07-03
    (Wed) as a fake holiday to verify holiday-day exclusion.
    """
    start = date(2024, 7, 1)
    end = date(2024, 7, 7)
    cal = _make_calendar(holidays=frozenset({date(2024, 7, 3)}))
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)

    sessions = sorted(set(df["session"]))
    # Expected: Mon 2024-07-01, Tue 2024-07-02, Thu 2024-07-04, Fri 2024-07-05.
    # Excluded: Wed 2024-07-03 (holiday), Sat-Sun 2024-07-06/07 (weekends).
    assert sessions == [
        date(2024, 7, 1),
        date(2024, 7, 2),
        date(2024, 7, 4),
        date(2024, 7, 5),
    ], f"got {sessions}"
    # Skipping is silent — no exception raised.


def test_rollover_window_skipped(tmp_path: Path) -> None:
    """Per AC1 + Nova T0 — rollover window D-3..D-1 before WDO expiration is skipped."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 8)
    # WDO expiration on 2024-07-05 (Fri) ⇒ rollover D-1=07-04, D-2=07-03, D-3=07-02.
    cal = _make_calendar(expirations=frozenset({date(2024, 7, 5)}))
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)

    sessions = sorted(set(df["session"]))
    # Mon 07-01 (valid), 07-02/03/04 (rollover), 07-05 (expiration day = valid),
    # weekends skipped, Mon 07-08 (valid).
    assert date(2024, 7, 1) in sessions
    assert date(2024, 7, 2) not in sessions
    assert date(2024, 7, 3) not in sessions
    assert date(2024, 7, 4) not in sessions


# =====================================================================
# AC1 — engine invariant: monotonic-increasing index
# =====================================================================
def test_index_monotonic_increasing(tmp_path: Path) -> None:
    """Per AC1 — engine ``_validate_events`` requires monotonic index."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 12)
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)

    assert df.index.is_monotonic_increasing
    # And the underlying t_start is sorted ascending.
    assert df["t_start"].is_monotonic_increasing
    # entry_window 16:55 must precede 17:40 within each session.
    first_day = df[df["session"] == date(2024, 7, 1)].sort_values("t_start")
    windows_seen = list(first_day["entry_window"].drop_duplicates())
    assert windows_seen == ["16:55", "17:10", "17:25", "17:40"]


# =====================================================================
# AC1 — trial subset + validation
# =====================================================================
def test_trial_filter_subset(tmp_path: Path) -> None:
    """Per AC1 — passing a subset of TRIALS_DEFAULT yields only that subset."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 5)
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(
        start, end, ("T1", "T3"), calendar=cal, warmup_gate=gate
    )

    assert sorted(df["trial_id"].unique()) == ["T1", "T3"]
    # 5 days × 4 windows × 2 trials = 40 rows.
    assert len(df) == 5 * 4 * 2


def test_unknown_trial_rejected(tmp_path: Path) -> None:
    """Per AC1 — Article IV: unknown trial id ⇒ ValueError (no silent accept)."""
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, date(2024, 7, 1))
    with pytest.raises(ValueError, match="unknown trial ids"):
        build_events_dataframe(
            date(2024, 7, 1),
            date(2024, 7, 5),
            ("T1", "T99"),  # T99 invented
            calendar=cal,
            warmup_gate=gate,
        )


def test_empty_trials_rejected(tmp_path: Path) -> None:
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, date(2024, 7, 1))
    with pytest.raises(ValueError, match="trials tuple must be non-empty"):
        build_events_dataframe(
            date(2024, 7, 1), date(2024, 7, 5), (), calendar=cal, warmup_gate=gate
        )


def test_end_before_start_rejected(tmp_path: Path) -> None:
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, date(2024, 7, 1))
    with pytest.raises(ValueError, match="in_sample_end .* < in_sample_start"):
        build_events_dataframe(
            date(2024, 7, 5), date(2024, 7, 1), TRIALS_DEFAULT, calendar=cal, warmup_gate=gate
        )


def test_empty_window_after_calendar_rejected(tmp_path: Path) -> None:
    """All days excluded ⇒ no events ⇒ ValueError (CPCV cannot run on empty)."""
    # Only weekends in window.
    start = date(2024, 7, 6)  # Saturday
    end = date(2024, 7, 7)    # Sunday
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)
    with pytest.raises(ValueError, match="no valid sessions"):
        build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)


# =====================================================================
# AC1 — entry window times are correct
# =====================================================================
def test_entry_window_times_match_spec(tmp_path: Path) -> None:
    """Per spec §trading_rules — entry windows 16:55, 17:10, 17:25, 17:40; exit 17:55."""
    start = date(2024, 7, 1)
    end = date(2024, 7, 1)
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)

    df = build_events_dataframe(start, end, ("T1",), calendar=cal, warmup_gate=gate)

    rows = df.sort_values("t_start").reset_index(drop=True)
    assert len(rows) == 4
    expected_starts = [
        pd.Timestamp(2024, 7, 1, 16, 55),
        pd.Timestamp(2024, 7, 1, 17, 10),
        pd.Timestamp(2024, 7, 1, 17, 25),
        pd.Timestamp(2024, 7, 1, 17, 40),
    ]
    for actual, expected in zip(rows["t_start"], expected_starts):
        assert actual == expected
    # All t_end == 17:55 hard stop.
    assert (rows["t_end"] == pd.Timestamp(2024, 7, 1, 17, 55)).all()
    # Sanity: time(17, 55) is the canonical EXIT_DEADLINE_BRT.
    assert rows["t_end"].iloc[0].time() == time(17, 55)
