"""Hold-out lock guard test — AC12 of story T002.0c.

If ``events`` contains any timestamp in the pre-registered hold-out window
``[2025-07-01, 2026-04-21]`` and ``VESPERA_UNLOCK_HOLDOUT != 1``,
``CPCVEngine.generate_splits`` MUST raise ``HoldoutLockError`` BEFORE
yielding any split (i.e. before any partition / purge / embargo work).

This test exercises the engine's outer-window check (Beckett §3.2),
NOT the inner ``_holdout_lock`` module (which has its own contract tests
in ``tests/contracts/test_holdout_lock.py``).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import pytest

from packages.vespera_cpcv import CPCVConfig, CPCVEngine, HoldoutLockError


def _build_events_starting(base: date, n: int = 12) -> pd.DataFrame:
    """Build n events spaced 7 days apart starting at ``base``."""
    rows = []
    for i in range(n):
        d = base + timedelta(days=i * 7)
        rows.append(
            {
                "t_start": datetime.combine(d, datetime.min.time()).replace(hour=16, minute=55),
                "t_end": datetime.combine(d, datetime.min.time()).replace(hour=17, minute=55),
                "session": d,
            }
        )
    return pd.DataFrame(rows)


def test_holdout_guard_raises_when_window_inside_holdout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Events entirely inside the hold-out window MUST raise."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    events = _build_events_starting(date(2025, 8, 1))
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)

    with pytest.raises(HoldoutLockError):
        # Calling list() forces iteration — but the guard fires BEFORE
        # any yield, so we should get the error immediately.
        list(engine.generate_splits(events))


def test_holdout_guard_raises_when_window_crosses_into_holdout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Events that cross from in-sample INTO the hold-out window MUST raise."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    # Window starts in 2025-06 (in-sample) but extends into 2025-08+ (hold-out).
    events = _build_events_starting(date(2025, 6, 1), n=12)
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)

    with pytest.raises(HoldoutLockError):
        list(engine.generate_splits(events))


def test_holdout_guard_passes_when_strictly_in_sample(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """In-sample window (2024-07 to 2025-06) MUST pass without unlock."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    events = _build_events_starting(date(2024, 7, 1), n=12)
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(events))
    assert len(splits) == 15  # C(6, 2)


def test_holdout_guard_passes_with_explicit_unlock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With ``VESPERA_UNLOCK_HOLDOUT=1`` the guard must allow hold-out events."""
    monkeypatch.setenv("VESPERA_UNLOCK_HOLDOUT", "1")

    events = _build_events_starting(date(2025, 8, 1))
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(events))
    assert len(splits) == 15


def test_holdout_guard_fires_before_iteration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The guard must raise on FIRST contact with the iterator, not lazily.

    AC12: 'lança HoldoutLockError antes de retornar qualquer split'.
    """
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    events = _build_events_starting(date(2025, 9, 1))
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)

    iterator = engine.generate_splits(events)
    # First call to next() must raise — no split materialized.
    with pytest.raises(HoldoutLockError):
        next(iterator)
