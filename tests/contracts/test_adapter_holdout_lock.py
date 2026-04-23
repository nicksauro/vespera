"""Contract tests — Hold-out lock applies to BOTH adapters (T002.0b AC11/AC12).

Story: T002.0b
Spec ref: docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml L93-94

What this proves
----------------
Both ``feed_timescale.load_trades`` and ``feed_parquet.load_trades`` MUST:

  1. Raise ``HoldoutLockError`` when the requested window intersects the
     pre-registered hold-out ``[2025-07-01, 2026-04-21]`` and the unlock
     flag is NOT set.
  2. Raise the lock error BEFORE any I/O — no ``psycopg2.connect`` for
     timescale, no ``ParquetFile`` open for parquet. This is a strict
     ordering requirement (R1 + R15(d) — no silent side-effect if the
     retry layer reconnects past the guard).
  3. With ``VESPERA_UNLOCK_HOLDOUT=1`` set via ``monkeypatch.setenv``,
     return an iterable (possibly empty). No raise.

Why 4 cases
-----------
Per story T4 spec: 2 adapters × 2 states (locked, unlocked) = 4 cases.
Additional sentinel tests below verify the ordering precondition for each
adapter (guard BEFORE I/O).
"""

from __future__ import annotations

from datetime import datetime

import pytest

from packages.t002_eod_unwind.adapters import (
    feed_parquet,
    feed_timescale,
)
from packages.t002_eod_unwind.adapters._holdout_lock import HoldoutLockError


# Windows for the 4 cases. Intersect the hold-out range deliberately.
_LOCKED_START = datetime(2025, 7, 1)
_LOCKED_END = datetime(2025, 7, 2)


# ---------------------------------------------------------------------------
# Case 1: feed_timescale — locked (no flag)  -> HoldoutLockError, no connect
# ---------------------------------------------------------------------------

def test_feed_timescale_locked_raises_before_connect(monkeypatch):
    """AC11/AC12: lock raise before psycopg2.connect, without unlock flag."""
    # Guard: ensure flag is NOT set.
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    # Sentinel: any call to psycopg2.connect is a bug — the guard must have
    # already raised by the time we reach here.
    connect_called = {"n": 0}

    def sentinel_connect(*args, **kwargs):
        connect_called["n"] += 1
        raise AssertionError(
            "feed_timescale called psycopg2.connect BEFORE the hold-out "
            "guard rejected the window — AC11 violation"
        )

    import psycopg2  # type: ignore[import-untyped]
    monkeypatch.setattr(psycopg2, "connect", sentinel_connect)

    with pytest.raises(HoldoutLockError):
        # Materialize the iterable — load_trades runs the guard eagerly,
        # but we list() just in case an implementation delays the guard
        # to first iteration (would also be a violation).
        list(feed_timescale.load_trades(_LOCKED_START, _LOCKED_END, "WDO"))

    assert connect_called["n"] == 0, (
        f"psycopg2.connect was invoked {connect_called['n']} time(s) — "
        "guard must run first"
    )


# ---------------------------------------------------------------------------
# Case 2: feed_parquet — locked (no flag)    -> HoldoutLockError, no open
# ---------------------------------------------------------------------------

def test_feed_parquet_locked_raises_before_open(monkeypatch):
    """AC11/AC12: lock raise before ParquetFile open, without unlock flag."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    open_called = {"n": 0}

    class SentinelParquetFile:
        def __init__(self, *args, **kwargs):
            open_called["n"] += 1
            raise AssertionError(
                "feed_parquet opened a ParquetFile BEFORE the hold-out "
                "guard rejected the window — AC11 violation"
            )

    import pyarrow.parquet as pq  # type: ignore[import-untyped]
    monkeypatch.setattr(pq, "ParquetFile", SentinelParquetFile)

    with pytest.raises(HoldoutLockError):
        list(feed_parquet.load_trades(_LOCKED_START, _LOCKED_END, "WDO"))

    assert open_called["n"] == 0, (
        f"ParquetFile was opened {open_called['n']} time(s) — "
        "guard must run first"
    )


# ---------------------------------------------------------------------------
# Case 3: feed_timescale — unlocked (flag=1) -> no HoldoutLockError
# ---------------------------------------------------------------------------

def test_feed_timescale_unlocked_does_not_raise_lock(monkeypatch):
    """VESPERA_UNLOCK_HOLDOUT=1 allows the hold-out window without error.

    We still short-circuit before an actual DB connect by patching
    psycopg2.connect with a stub that returns a sentinel connection. The
    point is that the hold-out guard does NOT fire.
    """
    monkeypatch.setenv("VESPERA_UNLOCK_HOLDOUT", "1")

    class _StubCursor:
        def __init__(self):
            self.itersize = 0

        def execute(self, *a, **kw):
            return None

        def close(self):
            return None

        def __iter__(self):
            return iter([])  # empty result set — still valid per AC2

    class _StubConn:
        def cursor(self, *args, **kwargs):
            return _StubCursor()

        def close(self):
            return None

    import psycopg2  # type: ignore[import-untyped]
    monkeypatch.setattr(psycopg2, "connect", lambda *a, **kw: _StubConn())

    # Should NOT raise HoldoutLockError. Empty iterable is acceptable.
    result = list(feed_timescale.load_trades(_LOCKED_START, _LOCKED_END, "WDO"))
    assert result == []


# ---------------------------------------------------------------------------
# Case 4: feed_parquet — unlocked (flag=1)   -> no HoldoutLockError
# ---------------------------------------------------------------------------

def test_feed_parquet_unlocked_does_not_raise_lock(monkeypatch):
    """VESPERA_UNLOCK_HOLDOUT=1 allows the hold-out window without error.

    Since no hold-out parquet exists yet (T002.0a hasn't materialized past
    2025-03), we simply assert that calling load_trades with the flag set
    does NOT raise HoldoutLockError and returns an iterable we can consume.
    The iterable may be empty (manifest has no hold-out files) — that's OK
    per AC2.
    """
    monkeypatch.setenv("VESPERA_UNLOCK_HOLDOUT", "1")

    # Exhaust the iterable; should NOT raise HoldoutLockError.
    try:
        result = list(feed_parquet.load_trades(_LOCKED_START, _LOCKED_END, "WDO"))
    except HoldoutLockError:
        pytest.fail(
            "feed_parquet raised HoldoutLockError despite VESPERA_UNLOCK_HOLDOUT=1"
        )
    # No hold-out parquets in the manifest yet; empty iterable is correct.
    assert result == []


# ---------------------------------------------------------------------------
# Additional: whitelist enforcement (AC2 cross-cutting)
# ---------------------------------------------------------------------------

def test_feed_timescale_rejects_unknown_ticker():
    with pytest.raises(ValueError):
        list(feed_timescale.load_trades(
            datetime(2024, 3, 4), datetime(2024, 3, 5), "PETR4",
        ))


def test_feed_parquet_rejects_unknown_ticker():
    with pytest.raises(ValueError):
        list(feed_parquet.load_trades(
            datetime(2024, 3, 4), datetime(2024, 3, 5), "PETR4",
        ))


# ---------------------------------------------------------------------------
# Additional: tz-aware rejection (AC6, AC10 — BRT naive)
# ---------------------------------------------------------------------------

def test_feed_timescale_rejects_tz_aware_input():
    from datetime import timezone
    aware = datetime(2024, 3, 4, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        list(feed_timescale.load_trades(aware, datetime(2024, 3, 5), "WDO"))


def test_feed_parquet_rejects_tz_aware_input():
    from datetime import timezone
    aware = datetime(2024, 3, 4, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        list(feed_parquet.load_trades(aware, datetime(2024, 3, 5), "WDO"))
