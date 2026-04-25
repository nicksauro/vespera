"""Contract tests — Hold-out lock fail-closed guard.

Story: T002.0a (AC7, AC8.1)
Spec ref: docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml L93-94
Module under test: scripts/_holdout_lock.py

Gate behavior (what this guards)
--------------------------------
The pre-registered hold-out window is ``[2025-07-01, 2026-04-21]``. Any
materialization / adapter call whose requested window intersects this range
MUST raise ``HoldoutLockError`` unless ``VESPERA_UNLOCK_HOLDOUT=1`` is in
the environment.

This is the single mechanism enforcing R1 (hold-out virgin) at the data-
access layer. A bug here means silent leakage. The cases below are the
4 minima the story calls for:

  1. locked-in-range         — fully inside hold-out, no flag -> ERROR
  2. locked-cross-boundary   — straddles boundary, no flag   -> ERROR
  3. unlocked-with-flag      — same window, flag=1           -> OK
  4. unlocked-pre-holdout    — fully before hold-out, no flag -> OK
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

# Ensure scripts/ is importable.
_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _holdout_lock import (  # noqa: E402
    HOLDOUT_END_INCLUSIVE,
    HOLDOUT_START,
    HoldoutLockError,
    assert_holdout_safe,
    is_unlock_enabled,
)


# ---------------------------------------------------------------------------
# Case 1: locked-in-range (fully inside hold-out, no flag) -> ERROR
# ---------------------------------------------------------------------------

def test_locked_in_range_rejects_without_flag():
    """Window fully inside hold-out, no unlock -> HoldoutLockError."""
    env: dict[str, str] = {}  # no VESPERA_UNLOCK_HOLDOUT
    with pytest.raises(HoldoutLockError) as exc:
        assert_holdout_safe(date(2025, 7, 1), date(2025, 7, 15), env=env)

    msg = str(exc.value).lower()
    assert "hold-out" in msg
    assert "vespera_unlock_holdout" in msg


def test_locked_flag_zero_still_rejects():
    """VESPERA_UNLOCK_HOLDOUT='0' is explicitly fail-closed."""
    env = {"VESPERA_UNLOCK_HOLDOUT": "0"}
    with pytest.raises(HoldoutLockError):
        assert_holdout_safe(date(2025, 10, 1), date(2025, 10, 31), env=env)


# ---------------------------------------------------------------------------
# Case 2: locked-cross-boundary (straddles start/end) -> ERROR
# ---------------------------------------------------------------------------

def test_locked_cross_start_boundary_rejects():
    """In-sample end into hold-out start -> ERROR (1-day overlap)."""
    env: dict[str, str] = {}
    with pytest.raises(HoldoutLockError):
        assert_holdout_safe(date(2025, 6, 15), date(2025, 7, 1), env=env)


def test_locked_cross_end_boundary_rejects():
    """Window covering the last day of hold-out -> ERROR."""
    env: dict[str, str] = {}
    with pytest.raises(HoldoutLockError):
        assert_holdout_safe(date(2026, 4, 21), date(2026, 5, 10), env=env)


def test_locked_spans_entire_holdout_rejects():
    """Window strictly containing the whole hold-out -> ERROR."""
    env: dict[str, str] = {}
    with pytest.raises(HoldoutLockError):
        assert_holdout_safe(date(2024, 1, 1), date(2026, 12, 31), env=env)


# ---------------------------------------------------------------------------
# Case 3: unlocked-with-flag (same locked window, flag=1) -> OK
# ---------------------------------------------------------------------------

def test_unlocked_with_flag_allows_in_range():
    """VESPERA_UNLOCK_HOLDOUT=1 allows window inside hold-out."""
    env = {"VESPERA_UNLOCK_HOLDOUT": "1"}
    # Should not raise.
    assert_holdout_safe(date(2025, 7, 1), date(2025, 7, 15), env=env)


def test_unlocked_flag_allows_boundary_cross():
    env = {"VESPERA_UNLOCK_HOLDOUT": "1"}
    assert_holdout_safe(date(2025, 6, 15), date(2025, 7, 1), env=env)


# ---------------------------------------------------------------------------
# Case 4: unlocked-pre-holdout (fully before, no flag) -> OK
# ---------------------------------------------------------------------------

def test_pre_holdout_window_allowed_without_flag():
    """Window entirely before 2025-07-01 never needs unlock."""
    env: dict[str, str] = {}
    # Spec in-sample: 2024-07-01 .. 2025-06-30. Warmup: 2024-01-02 .. 2024-06-30.
    assert_holdout_safe(date(2024, 1, 2), date(2024, 6, 30), env=env)
    assert_holdout_safe(date(2024, 7, 1), date(2025, 6, 30), env=env)
    # Day-before-boundary (2025-06-30) is the strictest pre-holdout edge.
    assert_holdout_safe(date(2025, 6, 30), date(2025, 6, 30), env=env)


def test_post_holdout_window_allowed_without_flag():
    """Window entirely after 2026-04-21 never needs unlock."""
    env: dict[str, str] = {}
    assert_holdout_safe(date(2026, 4, 22), date(2026, 5, 30), env=env)


# ---------------------------------------------------------------------------
# Sanity: bounds match spec v0.2.0 L93-94 literally.
# ---------------------------------------------------------------------------

def test_bounds_match_preregistration():
    assert HOLDOUT_START == date(2025, 7, 1)
    assert HOLDOUT_END_INCLUSIVE == date(2026, 4, 21)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_invalid_window_start_after_end_raises_value_error():
    with pytest.raises(ValueError):
        assert_holdout_safe(date(2025, 1, 15), date(2025, 1, 1), env={})


def test_iso_string_inputs_accepted():
    """Strings in ISO-8601 naive form are accepted."""
    env: dict[str, str] = {}
    assert_holdout_safe("2024-03-01", "2024-03-15", env=env)
    with pytest.raises(HoldoutLockError):
        assert_holdout_safe("2025-07-05", "2025-07-10", env=env)


def test_tz_aware_datetime_rejected():
    """R2: tz-aware datetimes are rejected."""
    from datetime import datetime, timezone
    env: dict[str, str] = {}
    aware = datetime(2024, 3, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        assert_holdout_safe(aware, date(2024, 3, 15), env=env)


# ---------------------------------------------------------------------------
# is_unlock_enabled
# ---------------------------------------------------------------------------

def test_is_unlock_enabled_true_only_for_exact_one():
    assert is_unlock_enabled(env={"VESPERA_UNLOCK_HOLDOUT": "1"}) is True
    assert is_unlock_enabled(env={"VESPERA_UNLOCK_HOLDOUT": "0"}) is False
    assert is_unlock_enabled(env={"VESPERA_UNLOCK_HOLDOUT": ""}) is False
    assert is_unlock_enabled(env={"VESPERA_UNLOCK_HOLDOUT": "true"}) is False
    assert is_unlock_enabled(env={}) is False


# ---------------------------------------------------------------------------
# Ordering contract: guard MUST fire before any DB connection attempt.
# Riven CONDITION: prove `HoldoutLockError` raises BEFORE I/O
# ---------------------------------------------------------------------------

def test_materialize_raises_before_db_connect(monkeypatch):
    """HoldoutLockError must be raised BEFORE psycopg2.connect is called.

    We patch ``_connect`` with a sentinel that flips a flag. If the guard
    fires in the correct order, the sentinel is NEVER invoked.
    """
    import materialize_parquet as mp  # noqa: E402

    connect_called = {"flag": False}

    def fake_connect(_env):
        connect_called["flag"] = True
        raise AssertionError(
            "_connect was called before the hold-out guard rejected the window"
        )

    monkeypatch.setattr(mp, "_connect", fake_connect)
    # Also patch _load_env_vespera so we never touch the filesystem.
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    args = mp.parse_args([
        "--start-date", "2025-08-01",
        "--end-date", "2025-08-15",
        "--ticker", "WDO",
    ])
    with pytest.raises(HoldoutLockError):
        mp.run(args)

    assert connect_called["flag"] is False, (
        "_connect should not have been invoked — guard must run first"
    )
