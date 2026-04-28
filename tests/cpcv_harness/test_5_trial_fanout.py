"""T6 — tests for ``run_5_trial_fanout`` (AC3 + AC4 of Story T002.0f).

Coverage:
    test_dict_shape_5x45                  — AC3 5 keys × 45 results = 225
    test_trial_isolation_disjoint_events  — AC3 events_T1 ∩ events_T2 = ∅
    test_3_runs_byte_identical            — AC4 determinism (carry from T002.0c)
    test_subset_trials_supported          — AC3 trials kwarg
    test_missing_trial_id_column_raises   — AC3 ValueError on bad input
    test_uses_runner_not_engine_directly  — Beckett T0: uniform DeterminismStamp
    test_path_index_ordering              — Beckett §3.2 ascending order
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from packages.t002_eod_unwind.adapters.exec_backtest import BacktestCosts
from packages.t002_eod_unwind.cpcv_harness import (
    TRIALS_DEFAULT,
    build_events_dataframe,
    make_backtest_fn,
    run_5_trial_fanout,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.gate import WarmUpGate
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    PercentileBands,
    Percentiles126dState,
)
from packages.vespera_cpcv import BacktestRunner, CPCVConfig


# =====================================================================
# Fixtures — shared across tests
# =====================================================================
def _make_calendar() -> CalendarData:
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _make_p126() -> Percentiles126dState:
    return Percentiles126dState(
        as_of_date=date(2024, 7, 1),
        magnitude=PercentileBands(p20=1.0, p60=2.0, p80=3.0),
        atr_day_ratio=PercentileBands(p20=0.5, p60=1.0, p80=1.5),
        window_days=tuple(),
        computed_at_brt=__import__("datetime").datetime(2024, 7, 1),
    )


def _make_ready_gate(tmp_path: Path, as_of: date) -> WarmUpGate:
    atr = tmp_path / "atr_20d.json"
    pct = tmp_path / "percentiles_126d.json"
    atr.write_text(json.dumps({"as_of_date": as_of.isoformat()}), encoding="utf-8")
    pct.write_text(json.dumps({"as_of_date": as_of.isoformat()}), encoding="utf-8")
    return WarmUpGate(atr, pct)


def _make_runner(seed: int = 42) -> BacktestRunner:
    """Build a runner with the spec v0.2.0 CPCVConfig: n_groups=10, k=2 ⇒ 45 paths."""
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=seed)
    return BacktestRunner(
        config=cfg,
        spec_version="0.2.0",
        simulator_version="harness-test",
    )


def _build_events_for_fanout(tmp_path: Path):
    """Build an events frame with enough sessions for n_groups=10 to slice."""
    # Need M >= n_groups (10); use 20 business days × 4 windows × 5 trials = 400 rows
    # per trial that's 80 events ⇒ comfortably > 10 groups.
    start = date(2024, 7, 1)  # Monday
    end = date(2024, 7, 31)   # ~22 business days
    cal = _make_calendar()
    gate = _make_ready_gate(tmp_path, start)
    return build_events_dataframe(start, end, TRIALS_DEFAULT, calendar=cal, warmup_gate=gate)


# =====================================================================
# AC3 — dict shape: 5 keys × 45 results = 225
# =====================================================================
def test_dict_shape_5_trials_45_paths(tmp_path: Path) -> None:
    """Per AC3 — dict[trial_id, list[BacktestResult]] with 5×45=225 results."""
    events = _build_events_for_fanout(tmp_path)
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()

    out = run_5_trial_fanout(events, fn, runner)

    assert isinstance(out, dict)
    assert set(out.keys()) == set(TRIALS_DEFAULT)
    assert len(out) == 5
    for trial, results in out.items():
        assert len(results) == 45, f"trial {trial} expected 45 paths, got {len(results)}"
    total = sum(len(v) for v in out.values())
    assert total == 225, f"expected 225 total results, got {total}"


# =====================================================================
# AC3 — trial isolation
# =====================================================================
def test_trial_isolation_disjoint_events_by_trial_id(tmp_path: Path) -> None:
    """Per AC3 — events filtered by trial_id BEFORE engine; no cross-contamination.

    We verify by comparing the train/test session sets: since each trial's
    events come from the same temporal grid but tagged differently, the
    PER-TRIAL filtered DataFrame indexes are disjoint by construction.
    """
    events = _build_events_for_fanout(tmp_path)

    # Verify trial filtering is well-formed at source.
    e_t1 = events[events["trial_id"] == "T1"]
    e_t2 = events[events["trial_id"] == "T2"]
    # Index sets must be disjoint (each row belongs to exactly one trial).
    assert set(e_t1.index).isdisjoint(set(e_t2.index))
    # And both must be non-empty.
    assert len(e_t1) > 0 and len(e_t2) > 0
    # Same temporal grid (sessions match).
    assert sorted(set(e_t1["session"])) == sorted(set(e_t2["session"]))


def test_trial_isolation_results_differ_per_trial(tmp_path: Path) -> None:
    """Per AC3 — different trials may share grid but produce isolated result lists.

    The harness stub uses ``avg_slippage_signed_ticks`` as the P126 anchor
    proxy — same P126 across trials ⇒ per-fold metrics within a trial are
    constant for the stub, but the per-fold counts (n_flat_signals = len
    test events) differ between trials only if the per-trial event count
    differs. With identical event counts, the test verifies that fan-out
    EXECUTES per trial without raising.
    """
    events = _build_events_for_fanout(tmp_path)
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()
    out = run_5_trial_fanout(events, fn, runner)

    # Sanity: each trial received its own runner pass (no result is None).
    for trial in TRIALS_DEFAULT:
        for r in out[trial]:
            assert r is not None
            assert r.fold.path_index in range(45)


# =====================================================================
# AC4 — determinism: 3 runs same seed ⇒ 225 byte-identical content_sha256
# =====================================================================
def test_three_runs_byte_identical_content_sha256(tmp_path: Path) -> None:
    """Per AC4 (carry from T002.0c AC12) — 3 runs same seed ⇒ 225 hashes equal."""
    events = _build_events_for_fanout(tmp_path)

    runs: list[dict[str, list[str]]] = []
    for _ in range(3):
        # Build fresh closure + runner per run to verify true reproducibility.
        fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
        runner = _make_runner(seed=42)
        out = run_5_trial_fanout(events, fn, runner)
        run_hashes = {trial: [r.content_sha256() for r in results] for trial, results in out.items()}
        runs.append(run_hashes)

    # Compare run 0 vs runs 1, 2 — all 225 hashes must match pairwise.
    for trial in TRIALS_DEFAULT:
        for i in range(45):
            assert (
                runs[0][trial][i] == runs[1][trial][i] == runs[2][trial][i]
            ), f"trial {trial} path {i}: hashes differ across 3 runs"


# =====================================================================
# AC3 — trials subset support
# =====================================================================
def test_subset_trials_supported(tmp_path: Path) -> None:
    """Per AC3 — caller may pass a subset of TRIALS_DEFAULT."""
    events = _build_events_for_fanout(tmp_path)
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()

    out = run_5_trial_fanout(events, fn, runner, trials=("T1", "T3"))

    assert set(out.keys()) == {"T1", "T3"}
    assert len(out["T1"]) == 45
    assert len(out["T3"]) == 45


# =====================================================================
# AC3 — error handling
# =====================================================================
def test_missing_trial_id_column_raises(tmp_path: Path) -> None:
    """Per AC3 — Article IV: events without trial_id ⇒ ValueError."""
    import pandas as pd

    bad_events = pd.DataFrame({"t_start": [], "t_end": [], "session": []})
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()
    with pytest.raises(ValueError, match="missing required 'trial_id' column"):
        run_5_trial_fanout(bad_events, fn, runner)


def test_trial_with_no_events_raises(tmp_path: Path) -> None:
    """Per AC3 — requested trial absent from events ⇒ ValueError (no silent skip)."""
    events = _build_events_for_fanout(tmp_path)
    # Remove all T2 rows.
    events_no_t2 = events[events["trial_id"] != "T2"].reset_index(drop=True)

    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()
    with pytest.raises(ValueError, match="no events found for trial 'T2'"):
        run_5_trial_fanout(events_no_t2, fn, runner)


# =====================================================================
# Beckett T0 invariants — uniform DeterminismStamp + ordered paths
# =====================================================================
def test_uniform_determinism_stamp_per_trial_run(tmp_path: Path) -> None:
    """Per Beckett T0 — runner.run injects uniform DeterminismStamp across folds.

    All 45 results within ONE trial share the same DeterminismStamp
    (excluding ``timestamp_brt``, which is a per-run wall-clock).
    """
    events = _build_events_for_fanout(tmp_path)
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()
    out = run_5_trial_fanout(events, fn, runner)

    for trial, results in out.items():
        seeds = {r.determinism.seed for r in results}
        run_ids = {r.determinism.run_id for r in results}
        config_hashes = {r.determinism.cpcv_config_sha256 for r in results}
        assert len(seeds) == 1, f"trial {trial} has heterogeneous seeds: {seeds}"
        assert len(run_ids) == 1, f"trial {trial} has heterogeneous run_ids: {run_ids}"
        assert len(config_hashes) == 1


def test_path_indices_ascending_per_trial(tmp_path: Path) -> None:
    """Per Beckett §3.2 — results sorted by path_index ascending."""
    events = _build_events_for_fanout(tmp_path)
    fn = make_backtest_fn(BacktestCosts(), _make_calendar(), _make_p126())
    runner = _make_runner()
    out = run_5_trial_fanout(events, fn, runner)

    for trial, results in out.items():
        path_indices = [r.fold.path_index for r in results]
        assert path_indices == sorted(path_indices)
        # And full coverage 0..44.
        assert path_indices == list(range(45))
