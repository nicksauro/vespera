"""T002.1.bis — tests for ``backtest_fn_factory`` per-fold rebuild pattern.

Per Aria T0b architectural review (`docs/architecture/T002.1.bis-aria-archi-review.md`)
APPROVE_OPTION_B + Mira spec §6.1. Verifies:

  test_factory_invoked_once_per_fold              — factory called n_paths times
  test_factory_each_fold_distinct_p126_as_of_date — fold-local state per Aria §I.5
  test_engine_run_rejects_both_backtest_fn_and_factory — ValueError on both args
  test_engine_run_rejects_neither                 — ValueError on no args
  test_back_compat_static_backtest_fn             — legacy single closure path

These complement the 6 existing AC2 tests in ``test_make_backtest_fn.py`` —
those continue passing untouched (Aria §I.6 back-compat invariant).
"""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd
import pytest

from packages.t002_eod_unwind.adapters.exec_backtest import BacktestCosts
from packages.t002_eod_unwind.cpcv_harness import make_backtest_fn
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    PercentileBands,
    Percentiles126dState,
)
from packages.vespera_cpcv import BacktestRunner, CPCVConfig, CPCVSplit
from packages.vespera_cpcv.purge import CPCVTestBlock


# =====================================================================
# Fixtures
# =====================================================================
def _make_calendar() -> CalendarData:
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _make_p126(
    as_of_date: date = date(2024, 7, 1),
    magnitude_p20: float = 1.0,
    atr_p20: float = 2.0,
) -> Percentiles126dState:
    return Percentiles126dState(
        as_of_date=as_of_date,
        magnitude=PercentileBands(
            p20=magnitude_p20, p60=magnitude_p20 + 1, p80=magnitude_p20 + 2
        ),
        atr_day_ratio=PercentileBands(
            p20=atr_p20, p60=atr_p20 + 1, p80=atr_p20 + 2
        ),
        window_days=tuple(),
        computed_at_brt=datetime(2024, 7, 1, 0, 0),
    )


def _make_synthetic_split(path_id: int = 0) -> CPCVSplit:
    sessions = [date(2024, 7, 1), date(2024, 7, 2), date(2024, 7, 3)]
    train_df = pd.DataFrame(
        {
            "t_start": [pd.Timestamp(d) for d in sessions[:2]],
            "t_end": [pd.Timestamp(d) for d in sessions[:2]],
            "session": sessions[:2],
        }
    )
    test_df = pd.DataFrame(
        {
            "t_start": [pd.Timestamp(sessions[2])],
            "t_end": [pd.Timestamp(sessions[2])],
            "session": [sessions[2]],
        }
    )
    empty = pd.DataFrame(columns=["t_start", "t_end", "session"])
    return CPCVSplit(
        path_id=path_id,
        group_ids_test=(0,),
        group_ids_train=(1, 2),
        train_events=train_df,
        test_events=test_df,
        purged_events=empty,
        embargoed_events=empty,
        test_blocks=(
            CPCVTestBlock(
                group_ids=(0,),
                window_start=pd.Timestamp(sessions[2]).to_pydatetime(),
                window_end=pd.Timestamp(sessions[2]).to_pydatetime(),
                last_session=sessions[2],
            ),
        ),
    )


def _build_dummy_events(n_sessions: int = 12) -> pd.DataFrame:
    """Build an events DataFrame with the strategy column shape so the
    engine can partition it into n_groups=10, k=2 ⇒ 45 paths.
    """
    sessions = [
        date(2024, 7, 1) + pd.Timedelta(days=i).to_pytimedelta()
        for i in range(n_sessions)
    ]
    rows = []
    for s in sessions:
        for w in ("16:55", "17:10", "17:25", "17:40"):
            hh, mm = (int(x) for x in w.split(":"))
            t_start = pd.Timestamp(datetime(s.year, s.month, s.day, hh, mm))
            t_end = pd.Timestamp(datetime(s.year, s.month, s.day, 17, 55))
            rows.append(
                {
                    "t_start": t_start,
                    "t_end": t_end,
                    "session": s,
                    "trial_id": "T1",
                    "entry_window": w,
                }
            )
    return pd.DataFrame(rows).sort_values("t_start", kind="stable").reset_index(drop=True)


def _make_runner() -> BacktestRunner:
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    return BacktestRunner(
        config=cfg,
        spec_version="0.2.0",
        simulator_version="harness-test",
    )


# =====================================================================
# Test 1 — factory invoked once per fold
# =====================================================================
def test_factory_invoked_once_per_fold() -> None:
    """Per Aria §I.1 — engine calls factory once per CPCVSplit (45 calls
    for n_groups=10, k=2). NO factory call when ``backtest_fn`` (legacy
    static path) is provided.
    """
    calls: list[tuple[int, int]] = []

    def factory(split: CPCVSplit, train_events: pd.DataFrame):
        calls.append((split.path_id, len(train_events)))
        return make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())

    events = _build_dummy_events(n_sessions=12)
    runner = _make_runner()
    out = runner.run(events, backtest_fn_factory=factory)

    assert len(out) == 45, f"expected 45 fold results, got {len(out)}"
    assert len(calls) == 45, f"factory called {len(calls)} times, expected 45"
    # Each path_id 0..44 invoked exactly once.
    invoked_path_ids = sorted(p for p, _ in calls)
    assert invoked_path_ids == list(range(45))


# =====================================================================
# Test 2 — fold-local P126 state has distinct as_of_date per fold
# =====================================================================
def test_factory_each_fold_distinct_p126_as_of_date() -> None:
    """Per Aria §I.5 + Mira §3.4 — factory should produce a closure
    bound to a fold-local ``Percentiles126dState`` whose ``as_of_date``
    derives from the fold's TEST slice, NOT a global constant.

    Verified by injecting a factory that picks ``as_of_date`` from
    ``min(test_events.session)`` and asserting that the produced
    ``BacktestResult.content_sha256()`` differs across folds (fold-local
    state DOES propagate into the fold result hash via the P126 anchor
    in ``avg_slippage_signed_ticks``).
    """
    seen_as_of_dates: list[date] = []

    def factory(split: CPCVSplit, train_events: pd.DataFrame):
        as_of = min(split.test_events["session"])
        seen_as_of_dates.append(as_of)
        # Use as_of-derived magnitude_p20 to make P126 distinct per fold.
        magnitude_p20 = float(as_of.toordinal() % 5 + 1)
        return make_backtest_fn(
            BacktestCosts(),
            _make_calendar(),
            _make_p126(as_of_date=as_of, magnitude_p20=magnitude_p20),
        )

    events = _build_dummy_events(n_sessions=12)
    runner = _make_runner()
    results = runner.run(events, backtest_fn_factory=factory)

    # At least 2 distinct as_of_date values across the 45 folds (CPCV
    # partition guarantees test sets span the in-sample range).
    assert len(set(seen_as_of_dates)) >= 2, (
        f"expected fold-local as_of_date diversity; got "
        f"{len(set(seen_as_of_dates))} distinct values across 45 folds"
    )
    # Fold-local distinctness should propagate into per-fold metrics —
    # at least 2 distinct content_sha256() values across the 45 folds.
    hashes = {r.content_sha256() for r in results}
    assert len(hashes) >= 2, (
        f"expected per-fold hash diversity; got {len(hashes)} distinct "
        f"content_sha256() values (factory state may not be reaching closure)"
    )


# =====================================================================
# Test 3 — engine.run rejects both backtest_fn and factory
# =====================================================================
def test_engine_run_rejects_both_backtest_fn_and_factory() -> None:
    """Per Aria §I.1 — mutually-exclusive contract."""
    events = _build_dummy_events(n_sessions=12)
    runner = _make_runner()
    bf = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())

    def factory(split, train_events):
        return bf

    with pytest.raises(ValueError, match="EXACTLY ONE"):
        runner.run(events, backtest_fn=bf, backtest_fn_factory=factory)


# =====================================================================
# Test 4 — engine.run rejects neither
# =====================================================================
def test_engine_run_rejects_neither() -> None:
    """Per Aria §I.1 — at least one of backtest_fn / factory required."""
    events = _build_dummy_events(n_sessions=12)
    runner = _make_runner()
    with pytest.raises(ValueError, match="EXACTLY ONE"):
        runner.run(events)  # neither


# =====================================================================
# Test 5 — back-compat: static backtest_fn path still works (Aria §I.6)
# =====================================================================
def test_back_compat_static_backtest_fn() -> None:
    """Per Aria §I.6 — existing ``runner.run(events, backtest_fn=...)``
    callers (T002.0f stub path) continue working unchanged. Factory
    is opt-in.
    """
    events = _build_dummy_events(n_sessions=12)
    runner = _make_runner()
    bf = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    out = runner.run(events, backtest_fn=bf)
    assert len(out) == 45
    # All results share the runner's uniform DeterminismStamp.
    seeds = {r.determinism.seed for r in out}
    assert len(seeds) == 1


# =====================================================================
# Test 6 — run_5_trial_fanout factory plumbing
# =====================================================================
def test_run_5_trial_fanout_factory_plumbing() -> None:
    """Per Aria §I.3 — ``run_5_trial_fanout`` accepts ``backtest_fn_factory``
    and forwards verbatim to ``runner.run`` per trial.
    """
    from packages.t002_eod_unwind.cpcv_harness import run_5_trial_fanout

    invoke_count = {"n": 0}

    def factory(split, train_events):
        invoke_count["n"] += 1
        return make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())

    # Build a full 5-trial events DataFrame (T1..T5 × 4 windows × n_sessions).
    sessions = [
        date(2024, 7, 1) + pd.Timedelta(days=i).to_pytimedelta()
        for i in range(12)
    ]
    rows = []
    for s in sessions:
        for w in ("16:55", "17:10", "17:25", "17:40"):
            hh, mm = (int(x) for x in w.split(":"))
            t_start = pd.Timestamp(datetime(s.year, s.month, s.day, hh, mm))
            t_end = pd.Timestamp(datetime(s.year, s.month, s.day, 17, 55))
            for trial in ("T1", "T2", "T3", "T4", "T5"):
                rows.append(
                    {
                        "t_start": t_start,
                        "t_end": t_end,
                        "session": s,
                        "trial_id": trial,
                        "entry_window": w,
                    }
                )
    events = (
        pd.DataFrame(rows).sort_values("t_start", kind="stable").reset_index(drop=True)
    )
    runner = _make_runner()
    out = run_5_trial_fanout(events, runner=runner, backtest_fn_factory=factory)
    assert set(out.keys()) == {"T1", "T2", "T3", "T4", "T5"}
    # 5 trials × 45 folds = 225 total factory invocations.
    assert invoke_count["n"] == 225, (
        f"expected 225 factory invocations (5 × 45), got {invoke_count['n']}"
    )


# =====================================================================
# Test 7 — run_5_trial_fanout mutual-exclusivity guard
# =====================================================================
def test_run_5_trial_fanout_rejects_both_paths() -> None:
    """Per Aria §I.3 + Mira §6.4 — fanout must reject both
    backtest_fn AND factory simultaneously.
    """
    from packages.t002_eod_unwind.cpcv_harness import run_5_trial_fanout

    sessions = [
        date(2024, 7, 1) + pd.Timedelta(days=i).to_pytimedelta()
        for i in range(12)
    ]
    rows = []
    for s in sessions:
        for w in ("16:55", "17:10", "17:25", "17:40"):
            hh, mm = (int(x) for x in w.split(":"))
            t_start = pd.Timestamp(datetime(s.year, s.month, s.day, hh, mm))
            t_end = pd.Timestamp(datetime(s.year, s.month, s.day, 17, 55))
            for trial in ("T1", "T2", "T3", "T4", "T5"):
                rows.append(
                    {
                        "t_start": t_start,
                        "t_end": t_end,
                        "session": s,
                        "trial_id": trial,
                        "entry_window": w,
                    }
                )
    events = (
        pd.DataFrame(rows).sort_values("t_start", kind="stable").reset_index(drop=True)
    )
    runner = _make_runner()
    bf = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())

    def factory(split, train_events):
        return bf

    with pytest.raises(ValueError, match="EXACTLY ONE"):
        run_5_trial_fanout(
            events,
            backtest_fn=bf,
            runner=runner,
            backtest_fn_factory=factory,
        )
