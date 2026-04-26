"""T5 — tests for ``make_backtest_fn`` (AC2 of Story T002.0f).

Coverage:
    test_returns_callable_signature       — AC2 returned closure shape
    test_closure_independence_no_globals  — AC2 no module-level state mutation
    test_per_fold_p126_rebuild_changes_hash — AC2 different P126 ⇒ different hash
    test_closure_purity_2_calls_same_inputs — AC2 deterministic
    test_costs_anchored_in_hash           — AC2 costs participate in hash
    test_calendar_anchored_in_hash        — AC2 calendar participates in hash
"""

from __future__ import annotations

from datetime import date, datetime
from typing import cast

import pandas as pd

from packages.t002_eod_unwind.adapters.exec_backtest import BacktestCosts
from packages.t002_eod_unwind.cpcv_harness import (
    _PLACEHOLDER_STAMP,
    make_backtest_fn,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    PercentileBands,
    Percentiles126dState,
)
from packages.vespera_cpcv import BacktestResult, CPCVSplit
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


def _make_p126(magnitude_p20: float = 1.0, atr_p20: float = 2.0) -> Percentiles126dState:
    bands = PercentileBands(p20=magnitude_p20, p60=magnitude_p20 + 1, p80=magnitude_p20 + 2)
    atr_bands = PercentileBands(p20=atr_p20, p60=atr_p20 + 1, p80=atr_p20 + 2)
    return Percentiles126dState(
        as_of_date=date(2024, 7, 1),
        magnitude=bands,
        atr_day_ratio=atr_bands,
        window_days=tuple(),
        computed_at_brt=datetime(2024, 7, 1, 0, 0),
    )


def _make_synthetic_split(path_id: int = 0) -> CPCVSplit:
    """Build a CPCVSplit with empty events DataFrames (closure stub doesn't trade)."""
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


# =====================================================================
# AC2 — closure shape + signature
# =====================================================================
def test_returns_callable_with_correct_signature() -> None:
    """Per AC2 — make_backtest_fn returns Callable[[df, df, CPCVSplit], BacktestResult]."""
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    assert callable(fn)
    split = _make_synthetic_split()
    out = fn(split.train_events, split.test_events, split)
    assert isinstance(out, BacktestResult)
    assert out.fold.path_index == 0
    # Determinism stamp is the placeholder — runner.run will replace it.
    assert out.determinism is _PLACEHOLDER_STAMP


# =====================================================================
# AC2 — closure independence (no global state mutation)
# =====================================================================
def test_closure_independence_no_globals() -> None:
    """Per AC2 — invoking the closure must not mutate any module-level state.

    We snapshot a hash of the module's mutable-looking attribute (the
    placeholder stamp) before and after invocation; they must match.
    """
    import packages.t002_eod_unwind.cpcv_harness as harness_mod

    snapshot_before = (
        harness_mod._PLACEHOLDER_STAMP.seed,
        harness_mod._PLACEHOLDER_STAMP.run_id,
        harness_mod._PLACEHOLDER_STAMP.simulator_version,
    )

    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    split = _make_synthetic_split()
    for _ in range(5):
        fn(split.train_events, split.test_events, split)

    snapshot_after = (
        harness_mod._PLACEHOLDER_STAMP.seed,
        harness_mod._PLACEHOLDER_STAMP.run_id,
        harness_mod._PLACEHOLDER_STAMP.simulator_version,
    )
    assert snapshot_before == snapshot_after


def test_two_closures_independent() -> None:
    """Per AC2 — two closures with different inputs produce different results."""
    p126_a = _make_p126(magnitude_p20=1.0)
    p126_b = _make_p126(magnitude_p20=99.0)
    fn_a = make_backtest_fn(BacktestCosts(), _make_calendar(), p126_a)
    fn_b = make_backtest_fn(BacktestCosts(), _make_calendar(), p126_b)
    split = _make_synthetic_split()

    res_a = fn_a(split.train_events, split.test_events, split)
    res_b = fn_b(split.train_events, split.test_events, split)

    # Different P126 ⇒ different content_sha256() (P126 is anchored in hash).
    assert res_a.content_sha256() != res_b.content_sha256()


# =====================================================================
# AC2 — per-fold P126 rebuild is observable
# =====================================================================
def test_per_fold_p126_rebuild_changes_hash() -> None:
    """Per AC2 + Nova T0 endorsement — passing 2 different P126 states
    yields 2 distinct ``BacktestResult.content_sha256()`` values.

    This is the empirical anti-leak test: per-train-fold rebuild MUST be
    observable downstream. If the closure ignored ``percentiles_state``,
    both hashes would match — a leak vector.
    """
    state_train_fold_1 = _make_p126(magnitude_p20=1.5, atr_p20=2.5)
    state_train_fold_2 = _make_p126(magnitude_p20=3.5, atr_p20=4.5)

    fn1 = make_backtest_fn(BacktestCosts(), _make_calendar(), state_train_fold_1)
    fn2 = make_backtest_fn(BacktestCosts(), _make_calendar(), state_train_fold_2)
    split = _make_synthetic_split()

    h1 = fn1(split.train_events, split.test_events, split).content_sha256()
    h2 = fn2(split.train_events, split.test_events, split).content_sha256()
    assert h1 != h2, (
        "P126 rebuild not observable in result hash — closure may be "
        "ignoring percentiles_state (leak vector!)"
    )


# =====================================================================
# AC2 — purity (same inputs ⇒ same outputs)
# =====================================================================
def test_closure_purity_two_calls_same_inputs() -> None:
    """Per AC2 — the closure is pure: identical inputs ⇒ identical hash."""
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    split = _make_synthetic_split()
    h1 = fn(split.train_events, split.test_events, split).content_sha256()
    h2 = fn(split.train_events, split.test_events, split).content_sha256()
    assert h1 == h2


def test_costs_anchored_in_hash() -> None:
    """Per AC2 — different costs ⇒ different result hash."""
    cal = _make_calendar()
    p126 = _make_p126()
    cheap = BacktestCosts(brokerage_per_contract_side_rs=0.10)
    expensive = BacktestCosts(brokerage_per_contract_side_rs=5.00)

    split = _make_synthetic_split()
    h_cheap = make_backtest_fn(cheap, cal, p126)(
        split.train_events, split.test_events, split
    ).content_sha256()
    h_expensive = make_backtest_fn(expensive, cal, p126)(
        split.train_events, split.test_events, split
    ).content_sha256()
    assert h_cheap != h_expensive


def test_calendar_anchored_in_hash() -> None:
    """Per AC2 — calendar participation: different validity for the test
    session ⇒ different result hash.

    Validates that the closure consults the calendar (not just captures
    it as dead reference).
    """
    p126 = _make_p126()
    costs = BacktestCosts()
    split = _make_synthetic_split()
    test_session = split.test_events["session"].iloc[0]
    test_session_date = cast(date, test_session)

    cal_valid = _make_calendar()
    cal_invalid = CalendarData(
        version="t",
        copom_meetings=frozenset(),
        br_holidays=frozenset({test_session_date}),  # mark test session as holiday
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )

    h_valid = make_backtest_fn(costs, cal_valid, p126)(
        split.train_events, split.test_events, split
    ).content_sha256()
    h_invalid = make_backtest_fn(costs, cal_invalid, p126)(
        split.train_events, split.test_events, split
    ).content_sha256()
    assert h_valid != h_invalid


# =====================================================================
# Sanity — bench against tests/cpcv conventions
# =====================================================================
def test_result_metrics_n_flat_signals_equals_test_events() -> None:
    """Per closure stub contract — n_flat_signals counts test events."""
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    split = _make_synthetic_split()
    out = fn(split.train_events, split.test_events, split)
    assert out.metrics.n_flat_signals == len(split.test_events)


def test_calendar_module_namespace_unchanged() -> None:
    """Sanity guard — ensure pytest import order didn't shadow the module."""
    import packages.t002_eod_unwind.cpcv_harness as h
    assert hasattr(h, "make_backtest_fn")
    assert hasattr(h, "build_events_dataframe")
    assert hasattr(h, "run_5_trial_fanout")


# Ensure pytest collects this file and imports resolve.
def test_module_imports_clean() -> None:
    import packages.t002_eod_unwind.cpcv_harness  # noqa: F401
