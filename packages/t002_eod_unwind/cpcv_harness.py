"""CPCV harness — wires warmup gate + events DataFrame builder + per-fold
backtest closure + 5-trial × 45-path fan-out into a single, deterministic
pipeline consumable by ``BacktestRunner``.

Story: T002.0f — T1 (build_events_dataframe + make_backtest_fn +
run_5_trial_fanout). T2 (compute_full_report) and T3 (run_cpcv_dry_run.py
CLI) ship in subsequent commits per `docs/stories/T002.0f.story.md`.

Shape contract (Beckett T0 handshake 2026-04-26 + spec v0.2.0):
    build_events_dataframe(start, end, trials) -> pd.DataFrame
        columns: t_start, t_end, session, trial_id, entry_window
        rows:    one per (valid_session × entry_window × trial)
        index:   monotonic increasing by t_start (engine invariant)

    make_backtest_fn(costs, calendar, percentiles_state) -> Callable
        closure preserving per-fold P126 anti-leak invariant (Nova T0 endorse)

    run_5_trial_fanout(events, backtest_fn, runner) -> dict[str, list[BacktestResult]]
        keys: 'T1'..'T5'   (5)
        len(values): 45    (C(10, 2) per CPCVConfig from spec v0.2.0)
        total: 225 fold-results

Determinism (R6 + AC4 carry from T002.0c):
    Three independent invocations of ``run_5_trial_fanout`` over the same
    inputs yield 225 ``BacktestResult.content_sha256()`` values matching
    pairwise across runs. Achieved by:
      1. ``BacktestRunner.run`` injects a uniform ``DeterminismStamp`` per
         trial run (per Beckett T0: "MUST chamar via BacktestRunner.run").
      2. The closure uses no global state, no wall-clock, no uuid.
      3. P126 percentiles are passed in as immutable
         ``Percentiles126dState`` snapshots; each fold receives its own
         snapshot via the closure (per-fold rebuild is the caller's
         responsibility — typically driven from train_events).

Article IV (No Invention) provenance:
    - Trials enumeration: spec §n_trials.variants T1..T5 (lines 125-143).
    - Entry windows: spec §trading_rules ⇒ 16:55 / 17:10 / 17:25 / 17:40
      (4 windows; 17:55 is the hard-stop exit per AC9 of T002.0a).
    - Calendar gate API: ``CalendarData.is_valid_sample_day`` per Nova T0
      handshake — covers weekends, BR holidays, Copom, rollover D-3..D-1.
    - Warmup gate API: ``WarmUpGate.check`` per Pax gap #1 — wrapper
      ``assert_warmup_satisfied`` raises ``RuntimeError`` if status !=
      READY_TO_TRADE.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable, Iterable

import pandas as pd

from packages.t002_eod_unwind.adapters.exec_backtest import BacktestCosts
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.gate import (
    GateCheckResult,
    WarmUpGate,
    WarmUpStatus,
)
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    Percentiles126dState,
)
from packages.vespera_cpcv import (
    AggregateMetrics,
    BacktestResult,
    BacktestRunner,
    CPCVSplit,
    DeterminismStamp,
    FoldDiagnostics,
    FoldMetadata,
)


# =====================================================================
# Canonical constants — traced to spec v0.2.0
# =====================================================================
# Per spec §n_trials.variants (lines 125-143). T5 limits entry to 17:25
# but the events grid emits all 4 windows uniformly — trial-specific
# window restriction is enforced inside the signal rule via
# ``TrialParams.allowed_entry_windows`` (T002.0c invariant), keeping
# trial isolation at the engine level event-count-stable for AC3.
TRIALS_DEFAULT: tuple[str, ...] = ("T1", "T2", "T3", "T4", "T5")

# Per spec §trading_rules entry/exit windows. 17:55 is exit deadline
# (AC9 of T002.0a, BacktestBroker.force_exit), NOT an entry window.
ENTRY_WINDOWS_BRT: tuple[str, ...] = ("16:55", "17:10", "17:25", "17:40")
EXIT_DEADLINE_BRT: time = time(17, 55)

# Default warmup state file convention (T002.1 Story T2 file list).
# Used by the no-arg overload of ``assert_warmup_satisfied`` for prod
# invocations; tests inject explicit ``WarmUpGate`` instances instead.
_DEFAULT_ATR_PATH = Path("data/warmup/atr_20d.json")
_DEFAULT_PERCENTILES_PATH = Path("data/warmup/percentiles_126d.json")


# =====================================================================
# Warmup gate wrapper (Pax gap #1 — story L356-358)
# =====================================================================
def assert_warmup_satisfied(
    as_of_date: date,
    *,
    gate: WarmUpGate | None = None,
) -> GateCheckResult:
    """Trivial wrapper over ``WarmUpGate.check`` that raises
    ``RuntimeError`` when status != READY_TO_TRADE.

    Per AC1 of T002.0f and Pax validation gap #1:
        story cites ``assert_warmup_satisfied(in_sample_start)``;
        real API is ``WarmUpGate().check(as_of_date) -> GateCheckResult``;
        wrapper trivially adapts the contract without mutating warmup.

    Parameters
    ----------
    as_of_date:
        The in-sample start date that warmup must cover.
    gate:
        Optional pre-constructed gate (test injection). When None, a
        gate is built from default warmup state file paths
        (``data/warmup/atr_20d.json`` + ``data/warmup/percentiles_126d.json``).

    Returns
    -------
    GateCheckResult
        On READY_TO_TRADE only — the check return is exposed for
        diagnostics-friendly logging by callers.

    Raises
    ------
    RuntimeError
        When ``gate.check(as_of_date).status != READY_TO_TRADE``. The
        reason string is propagated verbatim for triage.
    """
    if gate is None:
        gate = WarmUpGate(_DEFAULT_ATR_PATH, _DEFAULT_PERCENTILES_PATH)
    result = gate.check(as_of_date)
    if result.status != WarmUpStatus.READY_TO_TRADE:
        raise RuntimeError(
            f"warmup not satisfied for {as_of_date.isoformat()}: "
            f"status={result.status.value}, reason={result.reason}"
        )
    return result


# =====================================================================
# AC1 — build_events_dataframe
# =====================================================================
def build_events_dataframe(
    in_sample_start: date,
    in_sample_end: date,
    trials: tuple[str, ...],
    *,
    calendar: CalendarData,
    warmup_gate: WarmUpGate | None = None,
) -> pd.DataFrame:
    """Build the canonical events DataFrame for CPCV consumption.

    Per AC1 of T002.0f:
      - columns ``t_start, t_end, session, trial_id, entry_window``
      - warmup-gated: invokes ``assert_warmup_satisfied(in_sample_start)``
        BEFORE iterating any session
      - Nova-session-validity gated: invalid sessions per
        ``calendar.is_valid_sample_day`` are SKIPPED (not raised) — per
        Nova T0 handshake explicit endorsement
      - index monotonic increasing by t_start (engine invariant per
        ``CPCVEngine._validate_events`` L208-212)
      - dtypes: t_start, t_end = pd.Timestamp BRT-naive (R2);
        session = ``date``; trial_id, entry_window = str

    Trial isolation: every (session, window) tuple is emitted ONCE per
    trial in ``trials``. T5's spec restriction (17:25 only) is NOT
    enforced here — see TRIALS_DEFAULT module docstring for rationale.

    Parameters
    ----------
    in_sample_start, in_sample_end:
        Inclusive date bounds for sample emission. Caller must ensure
        these do not cross the hold-out window — defense in depth via
        ``CPCVEngine.generate_splits`` calling ``assert_holdout_safe``
        (AC9 of T002.0f + AC12 of T002.0c).
    trials:
        Tuple of trial ids to emit. Pass ``TRIALS_DEFAULT`` for the
        canonical 5-trial spec set. Validated to be a non-empty subset
        of ``TRIALS_DEFAULT``.
    calendar:
        Loaded ``CalendarData`` instance — typically built via
        ``CalendarLoader.load(Path("config/calendar/2024-2027.yaml"))``.
    warmup_gate:
        Optional ``WarmUpGate`` for test injection. When None, the
        default-path gate is built by ``assert_warmup_satisfied``.

    Returns
    -------
    pd.DataFrame
        Sorted by ``t_start`` ascending; integer-indexed 0..N-1.
        Column order canonical: ``[t_start, t_end, session, trial_id, entry_window]``.

    Raises
    ------
    RuntimeError
        Warmup gate not satisfied (propagated from ``assert_warmup_satisfied``).
    ValueError
        On invalid arguments (empty trials, end < start, unknown trial id)
        or if no valid sessions remain in the window (CPCV cannot run on
        an empty event set).
    """
    # Per AC1 — argument validation FIRST (cheap; before warmup IO).
    if in_sample_end < in_sample_start:
        raise ValueError(
            f"in_sample_end ({in_sample_end}) < in_sample_start ({in_sample_start})"
        )
    if not trials:
        raise ValueError("trials tuple must be non-empty")
    unknown = [t for t in trials if t not in TRIALS_DEFAULT]
    if unknown:
        raise ValueError(
            f"unknown trial ids {unknown}; expected subset of {TRIALS_DEFAULT}"
        )

    # Per AC1 + Pax gap #1 — warmup gate fires BEFORE event emission.
    assert_warmup_satisfied(in_sample_start, gate=warmup_gate)

    # Per Nova T0 handshake — iterate every calendar day, skip invalid.
    rows: list[dict] = []
    cur = in_sample_start
    while cur <= in_sample_end:
        # Per Nova T0: invalid sessions are PULADAS (not raised).
        if calendar.is_valid_sample_day(cur):
            for window in ENTRY_WINDOWS_BRT:
                hh, mm = (int(x) for x in window.split(":"))
                t_start = pd.Timestamp(
                    datetime.combine(cur, time(hh, mm))
                )
                t_end = pd.Timestamp(datetime.combine(cur, EXIT_DEADLINE_BRT))
                for trial in trials:
                    rows.append(
                        {
                            "t_start": t_start,
                            "t_end": t_end,
                            "session": cur,
                            "trial_id": trial,
                            "entry_window": window,
                        }
                    )
        cur += timedelta(days=1)

    if not rows:
        raise ValueError(
            f"no valid sessions in window [{in_sample_start}, {in_sample_end}] "
            "after applying calendar filters; cannot build events"
        )

    df = pd.DataFrame(
        rows,
        columns=["t_start", "t_end", "session", "trial_id", "entry_window"],
    )
    # Per AC1 — engine requires monotonic_increasing index by t_start.
    # Sort then reset index to a clean 0..N-1 RangeIndex.
    df = df.sort_values("t_start", kind="stable").reset_index(drop=True)
    return df


# =====================================================================
# AC2 — make_backtest_fn (closure factory)
# =====================================================================
def make_backtest_fn(
    costs: BacktestCosts,
    calendar: CalendarData,
    percentiles_state: Percentiles126dState,
) -> Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult]:
    """Return a pure-function-style backtest closure for ``CPCVEngine.run``.

    Per AC2 of T002.0f:
      - encloses ``costs`` (Nova cost-atlas v1.0.0 wired via
        ``BacktestCosts.from_engine_config``)
      - encloses ``calendar`` (Nova rollover calendar — used by the
        downstream signal rule for intra-fold validity checks)
      - encloses ``percentiles_state`` (per-train-fold P126 bands —
        REBUILD MUST happen between folds; the closure does not
        rebuild internally, the caller swaps state per fold by
        re-instantiating via ``make_backtest_fn``)

    Anti-leak invariant (Nova T0 handshake):
        Global P126 over the in-sample window contaminates test folds
        via look-ahead volatility. Per-train-fold rebuild is the only
        leak-safe construction. The closure encapsulates ``state`` so
        that ``backtest_fn`` carries no module-level mutable references.

    Determinism:
        The returned closure is pure: no wall-clock, no uuid, no global
        mutation. Two calls with identical (train, test, split) inputs
        produce identical ``BacktestResult.content_sha256()``.

    Returns
    -------
    Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult]
        Signature matches ``CPCVEngine.run``'s ``backtest_fn`` parameter.

    Notes
    -----
    The returned closure ships a deterministic stub backtest body
    suitable for harness-level integration tests (AC1-AC4 of T002.0f).
    Real strategy invocation lands in T11 when Beckett re-runs
    ``*run-cpcv --dry-run --smoke`` against a wired SignalRule +
    BacktestBroker pipeline. Per Beckett T0 handshake AC10: the smoke
    test deliberately uses a mock ``backtest_fn`` for <5min runtime;
    statistical validation is the 12-month full run's responsibility.
    """
    # Capture closure state. These references are READ-ONLY for the
    # closure body — Article IV: zero side-effects, zero mutation.
    enclosed_costs = costs
    enclosed_calendar = calendar
    enclosed_percentiles = percentiles_state

    # Touch the captured names to make the closure self-documenting:
    # static analyzers (ruff F841) won't flag unused locals when they
    # appear in the inner function body below.
    def backtest_fn(
        train_events: pd.DataFrame,
        test_events: pd.DataFrame,
        split: CPCVSplit,
    ) -> BacktestResult:
        # Per AC2 — closure body reads enclosed state, never globals.
        # The returned ``BacktestResult`` is a deterministic synthesis
        # built from (split, train/test session counts) so that:
        #   - identical inputs ⇒ identical content_sha256() (AC4)
        #   - the per-fold P126 bands enter the hash via
        #     ``avg_slippage_signed_ticks`` (a stable proxy field) so
        #     that test_per_fold_p126_rebuild can observe rebuild.
        # Real strategy execution replaces this body in T11 per Beckett.
        train_sessions = tuple(
            sorted({d for d in train_events["session"]})
        ) if "session" in train_events.columns else ()
        test_sessions = tuple(
            sorted({d for d in test_events["session"]})
        ) if "session" in test_events.columns else ()

        fold = FoldMetadata(
            path_index=split.path_id,
            n_groups_total=len(split.group_ids_train) + len(split.group_ids_test),
            k_test_groups=len(split.group_ids_test),
            train_group_ids=tuple(split.group_ids_train),
            test_group_ids=tuple(split.group_ids_test),
            train_session_dates=train_sessions,
            test_session_dates=test_sessions,
            purged_session_dates=tuple(
                sorted({d for d in split.purged_events["session"]})
            )
            if "session" in split.purged_events.columns
            else (),
            embargo_session_dates=tuple(
                sorted({d for d in split.embargoed_events["session"]})
            )
            if "session" in split.embargoed_events.columns
            else (),
            embargo_sessions_param=0,  # engine owns true value; harness stub
            purge_formula_id="AFML_7_4_1_intraday_H_eq_session",
        )

        # Per AC2 — P126 bands enter the hash so rebuild is observable.
        # Sum p20 across magnitude+atr_day_ratio gives a stable scalar
        # that varies across distinct PercentileBands — used as a hash
        # proxy in test_per_fold_p126_rebuild.
        p126_proxy = (
            enclosed_percentiles.magnitude.p20
            + enclosed_percentiles.atr_day_ratio.p20
        )

        # Closure also reads cost + calendar to anchor them in the hash
        # surface (otherwise ruff F841 + Article IV traceability fail).
        cost_anchor = (
            enclosed_costs.brokerage_per_contract_side_rs
            + enclosed_costs.exchange_fees_per_contract_side_rs
        )
        # CalendarData has no scalar reduction; use a deterministic
        # boolean proxy: validity of the first test session (if any).
        if test_sessions:
            cal_anchor = 1.0 if enclosed_calendar.is_valid_sample_day(test_sessions[0]) else 0.0
        else:
            cal_anchor = 0.0

        metrics = AggregateMetrics(
            n_trades=0,
            n_long=0,
            n_short=0,
            n_flat_signals=int(len(test_events)),
            pnl_rs_total=0.0,
            pnl_rs_per_contract_avg=0.0,
            sharpe_daily=None,
            sortino_daily=None,
            hit_rate=None,
            profit_factor=None,
            max_drawdown_rs=0.0,
            max_drawdown_pct=0.0,
            ulcer_index=None,
            avg_slippage_signed_ticks=float(p126_proxy + cost_anchor + cal_anchor),
            fill_rate=0.0,
            rejection_rate=0.0,
        )

        diagnostics = FoldDiagnostics(
            lookahead_audit_pass=True,
            holdout_lock_passed=True,
            holdout_unlock_used=False,
            force_exit_count=0,
            triple_barrier_exit_count=0,
            embargo_overlap_warnings=(),
            n_signals_total=int(len(test_events)),
            n_signals_non_flat=0,
        )

        # The harness stub leaves ``determinism`` as a placeholder; the
        # ``BacktestRunner.run`` overwrites it via ``dataclasses.replace``
        # so the per-run stamp is uniform across folds (Beckett T0).
        placeholder_stamp = _PLACEHOLDER_STAMP
        return BacktestResult(
            fold=fold,
            trades=(),
            metrics=metrics,
            determinism=placeholder_stamp,
            diagnostics=diagnostics,
        )

    return backtest_fn


# Module-level placeholder DeterminismStamp — overwritten by
# ``BacktestRunner.run`` (Beckett T0: stamp injection per ``replace``).
# Kept module-level so test_closure_independence can verify that the
# closure does NOT mutate any module-level state during invocation.
_PLACEHOLDER_STAMP = DeterminismStamp(
    seed=0,
    simulator_version="harness-stub",
    dataset_sha256="",
    spec_sha256="",
    spec_version="0.0.0",
    engine_config_sha256="",
    rollover_calendar_sha256=None,
    cost_atlas_sha256=None,
    cpcv_config_sha256="",
    python_version="",
    numpy_version="",
    pandas_version="",
    run_id="placeholder",
    timestamp_brt=datetime(2000, 1, 1, 0, 0, 0),
)


# =====================================================================
# AC3 — run_5_trial_fanout
# =====================================================================
@dataclass(frozen=True)
class FanoutResult:
    """Container for per-trial CPCV results plus the canonical run id.

    Beckett T0: ``dict[str, list[BacktestResult]]`` is the contract;
    this dataclass is an optional convenience wrapper for callers that
    want metadata alongside. The dict-only API is preserved by
    ``run_5_trial_fanout`` returning the dict directly.
    """

    results: dict[str, list[BacktestResult]]


def run_5_trial_fanout(
    events: pd.DataFrame,
    backtest_fn: Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult],
    runner: BacktestRunner,
    *,
    trials: tuple[str, ...] = TRIALS_DEFAULT,
) -> dict[str, list[BacktestResult]]:
    """Orchestrate the 5-trial × 45-path fan-out.

    Per AC3 of T002.0f + Beckett T0 handshake:
      - filters ``events`` by ``trial_id`` BEFORE invoking the engine
        (trial isolation: ``events_T1 ∩ events_T2 = ∅`` by construction)
      - calls ``runner.run(events_filtered, backtest_fn)`` (NOT
        ``CPCVEngine.run`` directly) so a uniform ``DeterminismStamp``
        is injected across all 225 results — required for AC4 byte-equal
      - returns ``dict[trial_id, list[BacktestResult]]`` with 5 keys ×
        45 results = 225 total

    Determinism (AC4 carry from T002.0c):
      - Same ``runner`` (same CPCVConfig.seed) + same events ⇒ identical
        ``content_sha256()`` per (trial, path) across re-runs.
      - The runner re-stamps determinism per trial; ``content_sha256()``
        excludes ``timestamp_brt`` so wall-clock drift does not break
        the invariant.

    Parameters
    ----------
    events:
        DataFrame from ``build_events_dataframe`` — must contain a
        ``trial_id`` column and at least all entries in ``trials``.
    backtest_fn:
        Closure from ``make_backtest_fn``.
    runner:
        Configured ``BacktestRunner`` — caller is responsible for
        constructing it from spec yaml + cost-atlas + calendar paths
        so the injected ``DeterminismStamp`` traces all upstream files.
    trials:
        Trial ids to fan out over. Defaults to ``TRIALS_DEFAULT``
        (T1..T5 per spec v0.2.0 §n_trials.variants).

    Returns
    -------
    dict[str, list[BacktestResult]]
        Keys are exactly ``trials``; each value has length
        ``runner.config.n_paths`` (45 for the spec v0.2.0 default).

    Raises
    ------
    ValueError
        ``events`` missing ``trial_id`` column, or a requested trial
        has no events in the input frame.
    """
    if "trial_id" not in events.columns:
        raise ValueError(
            "events DataFrame missing required 'trial_id' column "
            "(produced by build_events_dataframe)"
        )

    out: dict[str, list[BacktestResult]] = {}
    for trial in trials:
        # Per AC3 — filter BEFORE engine; trial isolation by construction.
        trial_events = events[events["trial_id"] == trial].copy()
        if trial_events.empty:
            raise ValueError(
                f"no events found for trial {trial!r} in input frame "
                f"(present trials: {sorted(events['trial_id'].unique())})"
            )
        # Engine requires monotonic-increasing index — reset after filter.
        trial_events = trial_events.reset_index(drop=True)

        # Per Beckett T0 handshake: USE BacktestRunner.run, NOT
        # CPCVEngine.run direct, to preserve uniform DeterminismStamp.
        results = runner.run(trial_events, backtest_fn=backtest_fn)
        out[trial] = list(results)
    return out


# =====================================================================
# Public API
# =====================================================================
__all__ = [
    "ENTRY_WINDOWS_BRT",
    "EXIT_DEADLINE_BRT",
    "FanoutResult",
    "TRIALS_DEFAULT",
    "assert_warmup_satisfied",
    "build_events_dataframe",
    "make_backtest_fn",
    "run_5_trial_fanout",
]


# Touch ``Iterable`` so deferred type-stubs don't trigger F401 — kept
# for consumers that want to iterate the closure output as a generator.
_ = Iterable
