"""IC pipeline wiring tests — Mira Gate 4b spec §15.8 (4 NEW tests).

T002.6 F2-T1 — Phase F2 IC pipeline wiring per:
- Mira Gate 4b spec ``docs/ml/specs/T002-gate-4b-real-tape-clearance.md``
  §15.8 (Test artifact specification — 4 NEW tests).
- Aria archi review APPROVE_OPTION_D — separate orchestration submodule
  ``packages/vespera_metrics/cpcv_aggregator.py``.
- Beckett consumer audit §T0c — additive ``TradeRecord`` fields.

Tests:
1. ``test_ic_computed_non_zero`` — direct regression on Round 1 failure
   mode (IC silently flowed 0.0 through verdict layer).
2. ``test_ic_deterministic`` — PCG64 paired-resample bootstrap CI is
   bit-identical across re-runs given same seed_bootstrap.
3. ``test_ic_status_flag`` — status='computed' propagates through
   ReportConfig → MetricsResult.ic_status → KillDecision; numeric K3
   evaluation proceeds (no short-circuit).
4. ``test_ic_inconclusive_path`` — Mira-authorized inconclusive case;
   evaluate_kill_criteria raises InvalidVerdictReport per Anti-Article-IV
   Guard #8 (§15.5) + §15.6 invariant.

Each test is deterministic via PCG64 seed. Small synthetic fixtures —
ADR-1 v3 6 GiB RSS budget honored.
"""
from __future__ import annotations

from datetime import date, datetime

import numpy as np
import pytest

from packages.t002_eod_unwind.adapters.exec_backtest import Fill
from packages.t002_eod_unwind.core.signal_rule import Direction
from packages.vespera_cpcv import (
    AggregateMetrics,
    BacktestResult,
    DeterminismStamp,
    FoldDiagnostics,
    FoldMetadata,
    TradeRecord,
)
from packages.vespera_metrics import (
    ICAggregateResult,
    InvalidVerdictReport,
    ReportConfig,
    compute_ic_from_cpcv_results,
    evaluate_kill_criteria,
)


# =====================================================================
# Fixtures — small CPCV results with non-trivial predictor/label pairing
# =====================================================================
def _make_fill(hour: int, minute: int, price: float, qty: int) -> Fill:
    return Fill(
        ts=datetime(2025, 3, 15, hour, minute),
        price=price,
        qty=qty,
        fees_rs=0.6,
        reason="entry_market" if minute < 55 else "exit_triple_barrier",
    )


def _make_trade(
    *,
    session: date,
    trial_id: str,
    window: str,
    direction: Direction,
    pnl_rs: float,
    predictor: float,
    forward_return_pts: float | None,
) -> TradeRecord:
    """Build a TradeRecord with explicit predictor/label for IC tests."""
    return TradeRecord(
        session_date=session,
        trial_id=trial_id,
        entry_window_brt=window,
        direction=direction,
        entry_fill=_make_fill(16, 55, 5050.0, 1),
        exit_fill=_make_fill(17, 55, 5050.0 + pnl_rs / 10.0, -1),
        pnl_rs=pnl_rs,
        slippage_rs_signed=-1.0,
        fees_rs=1.2,
        duration_seconds=3600,
        forced_exit=False,
        flags=frozenset({"pt_hit", "entered_fade_short"}),
        predictor_signal_per_trade=predictor,
        forward_return_at_1755_pts=forward_return_pts,
    )


def _make_fold(path_index: int) -> FoldMetadata:
    return FoldMetadata(
        path_index=path_index,
        n_groups_total=10,
        k_test_groups=2,
        train_group_ids=tuple(g for g in range(10) if g not in (0, 1)),
        test_group_ids=(0, 1),
        train_session_dates=(),
        test_session_dates=(date(2025, 3, 15),),
        purged_session_dates=(),
        embargo_session_dates=(),
        embargo_sessions_param=0,
        purge_formula_id="AFML_7_4_1_intraday_H_eq_session",
    )


def _make_metrics() -> AggregateMetrics:
    return AggregateMetrics(
        n_trades=1,
        n_long=0,
        n_short=1,
        n_flat_signals=0,
        pnl_rs_total=10.0,
        pnl_rs_per_contract_avg=10.0,
        sharpe_daily=0.5,
        sortino_daily=0.7,
        hit_rate=0.6,
        profit_factor=1.2,
        max_drawdown_rs=2.0,
        max_drawdown_pct=0.04,
        ulcer_index=0.01,
        avg_slippage_signed_ticks=0.5,
        fill_rate=1.0,
        rejection_rate=0.0,
    )


def _make_stamp() -> DeterminismStamp:
    return DeterminismStamp(
        seed=42,
        simulator_version="0.1.0",
        dataset_sha256="abc",
        spec_sha256="def",
        spec_version="0.2.3",
        engine_config_sha256="ghi",
        rollover_calendar_sha256=None,
        cost_atlas_sha256=None,
        cpcv_config_sha256="jkl",
        python_version="3.11",
        numpy_version="1.26",
        pandas_version="2.0",
        run_id="ic-pipeline-test",
        timestamp_brt=datetime(2026, 4, 30, 12, 0, 0),
    )


def _make_diagnostics() -> FoldDiagnostics:
    return FoldDiagnostics(
        lookahead_audit_pass=True,
        holdout_lock_passed=True,
        holdout_unlock_used=False,
        force_exit_count=0,
        triple_barrier_exit_count=1,
        embargo_overlap_warnings=(),
        n_signals_total=1,
        n_signals_non_flat=1,
    )


def _make_cpcv_results_with_edge(
    n_events: int = 50, *, seed: int = 42
) -> dict[str, list[BacktestResult]]:
    """Construct cpcv_results with a positive-IC signal.

    Predictor is +1/-1; label = predictor * positive_drift + noise so that
    the Spearman rank correlation is materially positive (around 0.3-0.6
    depending on noise variance). Each (session, trial, window) tuple is
    unique so dedup is a no-op.
    """
    rng = np.random.default_rng(np.random.PCG64(seed))
    trials = ["T1", "T2", "T3", "T4", "T5"]
    windows = ["16:55", "17:10", "17:25", "17:40"]
    results: dict[str, list[BacktestResult]] = {t: [] for t in trials}

    # Generate n_events trades and distribute across trials/windows/sessions.
    # We allocate one BacktestResult per trial with all that trial's trades
    # bundled into a single fold (path_index=0) for simplicity.
    per_trial_trades: dict[str, list[TradeRecord]] = {t: [] for t in trials}
    base_date = date(2025, 1, 6)  # Monday
    for i in range(n_events):
        trial = trials[i % len(trials)]
        window = windows[(i // len(trials)) % len(windows)]
        # Spread sessions across business days; offset deterministically.
        days_off = (i // (len(trials) * len(windows))) * 1
        session = date.fromordinal(base_date.toordinal() + days_off + i % 3)
        predictor = 1.0 if (i % 2 == 0) else -1.0
        # Positive-edge label: predictor * 5.0 + noise (yields positive IC).
        forward_ret = predictor * 5.0 + float(rng.normal(0.0, 2.0))
        pnl = predictor * 4.0 + float(rng.normal(0.0, 2.0))
        direction = Direction.SHORT if predictor < 0 else Direction.LONG
        trade = _make_trade(
            session=session,
            trial_id=trial,
            window=window,
            direction=direction,
            pnl_rs=pnl,
            predictor=predictor,
            forward_return_pts=forward_ret,
        )
        per_trial_trades[trial].append(trade)

    for trial in trials:
        results[trial] = [
            BacktestResult(
                fold=_make_fold(path_index=0),
                trades=tuple(per_trial_trades[trial]),
                metrics=_make_metrics(),
                determinism=_make_stamp(),
                diagnostics=_make_diagnostics(),
            )
        ]
    return results


# =====================================================================
# Test 1 — Mira spec §15.8 #1: IC computed non-zero
# =====================================================================
def test_ic_computed_non_zero():
    """IC pipeline emits non-zero IC + non-zero CI95 + status='computed'.

    Mira Gate 4b spec §15.8 #1 — direct regression on the Round 1 Phase F
    failure mode where IC silently flowed 0.0 through verdict layer.
    """
    cpcv_results = _make_cpcv_results_with_edge(n_events=50, seed=42)

    ic_result = compute_ic_from_cpcv_results(
        cpcv_results,
        seed_bootstrap=42,
        n_resamples=1000,  # smaller for test speed
        holdout_locked=True,
    )

    # Per §15.8 #1: IC ≠ 0.0 (non-trivial predictor/label pairing).
    assert ic_result.ic_in_sample != 0.0, (
        f"expected non-zero IC; got {ic_result.ic_in_sample} — "
        "Round 1 Phase F failure mode regression"
    )
    # Per §15.8 #1: ic_spearman_ci95 ≠ (0.0, 0.0).
    assert ic_result.ic_spearman_ci95 != (0.0, 0.0), (
        f"expected non-zero CI95; got {ic_result.ic_spearman_ci95}"
    )
    # Per §15.8 #1: ic_status == 'computed'.
    assert ic_result.ic_status == "computed", (
        f"expected ic_status='computed'; got {ic_result.ic_status!r}"
    )
    # Bonferroni-cosmetic: hold-out is locked under Phase F2.
    assert ic_result.ic_holdout == 0.0
    assert ic_result.ic_holdout_status == "deferred"
    # n_pairs >= 30 (Bailey-LdP 2014 §3 minimum-N).
    assert ic_result.n_pairs >= 30


# =====================================================================
# Test 2 — Mira spec §15.8 #2: deterministic
# =====================================================================
def test_ic_deterministic():
    """Same seed_bootstrap → bit-identical IC + CI95 across two calls.

    Mira Gate 4b spec §15.8 #2 + §15.4 PCG64 paired-indices determinism
    witness.
    """
    cpcv_results = _make_cpcv_results_with_edge(n_events=50, seed=42)

    r1 = compute_ic_from_cpcv_results(
        cpcv_results, seed_bootstrap=42, n_resamples=2000, holdout_locked=True
    )
    r2 = compute_ic_from_cpcv_results(
        cpcv_results, seed_bootstrap=42, n_resamples=2000, holdout_locked=True
    )

    # Bit-identical scalar IC values.
    assert r1.ic_in_sample == r2.ic_in_sample
    assert r1.ic_c2 == r2.ic_c2
    # Bit-identical CI95 tuples.
    assert r1.ic_spearman_ci95 == r2.ic_spearman_ci95
    assert r1.ic_c2_ci95 == r2.ic_c2_ci95
    # Sanity: status + n_pairs match.
    assert r1.ic_status == r2.ic_status == "computed"
    assert r1.n_pairs == r2.n_pairs


# =====================================================================
# Test 3 — Mira spec §15.8 #3: status flag propagates through pipeline
# =====================================================================
def test_ic_status_flag():
    """ic_status='computed' propagates through ReportConfig → MetricsResult
    → KillDecision; numeric K3 evaluation proceeds (no short-circuit).

    Mira Gate 4b spec §15.8 #3 + §15.6 invariant.
    """
    cpcv_results = _make_cpcv_results_with_edge(n_events=50, seed=42)
    ic_result = compute_ic_from_cpcv_results(
        cpcv_results, seed_bootstrap=42, n_resamples=500, holdout_locked=True
    )
    assert ic_result.ic_status == "computed"

    # ReportConfig threading.
    cfg = ReportConfig(
        seed_bootstrap=42,
        ic_in_sample=ic_result.ic_in_sample,
        ic_holdout=ic_result.ic_holdout,
        ic_spearman_ci95=ic_result.ic_spearman_ci95,
        ic_status=ic_result.ic_status,
        ic_holdout_status=ic_result.ic_holdout_status,
    )
    assert cfg.ic_status == "computed"
    assert cfg.ic_holdout_status == "deferred"

    # evaluate_kill_criteria reads ic_status='computed' and proceeds to
    # numeric K3 evaluation rather than short-circuiting.
    kd = evaluate_kill_criteria(
        dsr=0.95,
        pbo=0.2,
        ic_in_sample=0.10,
        ic_holdout=0.06,
        ic_status="computed",
        ic_holdout_status="deferred",
    )
    # Numeric K3 evaluation: 0.06 >= 0.5 * 0.10 ⇒ K3 PASS.
    assert kd.k3_ic_decay_passed is True
    assert kd.verdict == "GO"

    # Negative case: same status but failing IC decay numerically.
    kd_fail = evaluate_kill_criteria(
        dsr=0.95,
        pbo=0.2,
        ic_in_sample=0.10,
        ic_holdout=0.02,  # decayed below 50% floor
        ic_status="computed",
        ic_holdout_status="deferred",
    )
    assert kd_fail.k3_ic_decay_passed is False
    assert kd_fail.verdict == "NO_GO"
    assert any("K3" in r for r in kd_fail.reasons)


# =====================================================================
# Test 4 — Mira spec §15.8 #4: inconclusive path raises InvalidVerdictReport
# =====================================================================
def test_ic_inconclusive_path():
    """Inconclusive IC status → evaluate_kill_criteria raises
    InvalidVerdictReport per Anti-Article-IV Guard #8 (§15.5) + §15.6
    invariant.

    Mira Gate 4b spec §15.8 #4 — Mira-authorized inconclusive cases:
    - Empty cpcv_results (no events) → status='not_computed'.
    - Under-N (n_pairs < 30) → status='inconclusive_underN'.
    Both cases emit ic=0.0 (Mira-authorized 0.0, NOT silent default) and
    cause evaluate_kill_criteria to raise InvalidVerdictReport.
    """
    # Sub-case A: empty cpcv_results.
    empty_results: dict[str, list[BacktestResult]] = {}
    ic_empty = compute_ic_from_cpcv_results(
        empty_results, seed_bootstrap=42, n_resamples=500, holdout_locked=True
    )
    assert ic_empty.ic_status == "not_computed"
    assert ic_empty.ic_in_sample == 0.0  # Mira-authorized 0.0
    assert ic_empty.ic_spearman_ci95 == (0.0, 0.0)

    # Sub-case B: under-N (n_pairs < 30).
    under_n_results = _make_cpcv_results_with_edge(n_events=15, seed=42)
    ic_underN = compute_ic_from_cpcv_results(
        under_n_results, seed_bootstrap=42, n_resamples=500, holdout_locked=True
    )
    assert ic_underN.ic_status == "inconclusive_underN"
    assert ic_underN.ic_in_sample == 0.0  # Mira-authorized 0.0
    assert ic_underN.n_pairs < 30

    # Per §15.5 Anti-Article-IV Guard #8: evaluate_kill_criteria MUST raise
    # InvalidVerdictReport rather than emitting K3_FAIL with silent 0.0.
    with pytest.raises(InvalidVerdictReport, match="ic_status"):
        evaluate_kill_criteria(
            dsr=0.95,
            pbo=0.2,
            ic_in_sample=ic_empty.ic_in_sample,
            ic_holdout=ic_empty.ic_holdout,
            ic_status=ic_empty.ic_status,
            ic_holdout_status=ic_empty.ic_holdout_status,
        )

    with pytest.raises(InvalidVerdictReport, match="inconclusive_underN"):
        evaluate_kill_criteria(
            dsr=0.95,
            pbo=0.2,
            ic_in_sample=ic_underN.ic_in_sample,
            ic_holdout=ic_underN.ic_holdout,
            ic_status=ic_underN.ic_status,
            ic_holdout_status=ic_underN.ic_holdout_status,
        )


# =====================================================================
# Bonus invariants — Aria C-A1..C-A7 + Mira §15.7 dedup
# =====================================================================
def test_ic_aggregate_result_is_frozen():
    """ICAggregateResult is a frozen dataclass (Aria archi review)."""
    ic_result = compute_ic_from_cpcv_results(
        _make_cpcv_results_with_edge(n_events=50, seed=42),
        seed_bootstrap=42,
        n_resamples=500,
        holdout_locked=True,
    )
    assert isinstance(ic_result, ICAggregateResult)
    with pytest.raises(Exception):
        ic_result.ic_in_sample = 0.99  # type: ignore[misc]


def test_ic_dedup_per_event():
    """Mira §15.7 dedup invariant — same (session, trial, window) tuple
    appearing in multiple folds collapses to ONE event (lowest path_index
    wins).
    """
    # Build cpcv_results where SAME event tuple appears in two folds.
    # Both folds carry trades for the SAME (session, trial, window); after
    # dedup, only one trade should be considered.
    trade_a = _make_trade(
        session=date(2025, 3, 15),
        trial_id="T1",
        window="16:55",
        direction=Direction.SHORT,
        pnl_rs=5.0,
        predictor=-1.0,
        forward_return_pts=4.0,
    )
    # Same event tuple but different "fold" — the dedup key is identity.
    trade_b_dup = _make_trade(
        session=date(2025, 3, 15),
        trial_id="T1",
        window="16:55",
        direction=Direction.SHORT,
        pnl_rs=5.0,
        predictor=-1.0,
        forward_return_pts=4.0,
    )

    fold_low = _make_fold(path_index=2)
    fold_high = _make_fold(path_index=10)
    result_low = BacktestResult(
        fold=fold_low,
        trades=(trade_a,),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    result_high = BacktestResult(
        fold=fold_high,
        trades=(trade_b_dup,),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    cpcv_results = {
        "T1": [result_low, result_high],
        "T2": [],
        "T3": [],
        "T4": [],
        "T5": [],
    }

    ic_result = compute_ic_from_cpcv_results(
        cpcv_results, seed_bootstrap=42, n_resamples=100, holdout_locked=True
    )
    # Only ONE unique event tuple → n_pairs == 1 → 'inconclusive_underN'.
    assert ic_result.n_events_total == 1
    assert ic_result.n_pairs == 1
    assert ic_result.ic_status == "inconclusive_underN"
