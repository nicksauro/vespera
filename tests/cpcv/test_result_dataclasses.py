"""Result dataclass tests — frozen invariants + content_sha256 determinism (AC12).

3 runs of the same fold inputs MUST produce byte-identical
``content_sha256()`` (excluding the per-run wall-clock timestamp in
``DeterminismStamp``).
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date, datetime

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


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def _make_fill(ts_hour: int, price: float, qty: int) -> Fill:
    return Fill(
        ts=datetime(2024, 7, 1, ts_hour, 55),
        price=price,
        qty=qty,
        fees_rs=0.6,
        reason="entry_market" if ts_hour == 16 else "exit_hard_stop",
    )


def _make_trade() -> TradeRecord:
    return TradeRecord(
        session_date=date(2024, 7, 1),
        trial_id="T1",
        entry_window_brt="16:55",
        direction=Direction.LONG,
        entry_fill=_make_fill(16, 5050.0, 1),
        exit_fill=_make_fill(17, 5055.0, -1),
        pnl_rs=49.4,
        slippage_rs_signed=-2.0,
        fees_rs=1.2,
        duration_seconds=3600,
        forced_exit=True,
        flags=frozenset({"forced_exit_no_post_liquidity"}),
    )


def _make_fold(path_index: int = 0) -> FoldMetadata:
    return FoldMetadata(
        path_index=path_index,
        n_groups_total=10,
        k_test_groups=2,
        train_group_ids=(2, 3, 4, 5, 6, 7, 8, 9),
        test_group_ids=(0, 1),
        train_session_dates=(date(2024, 8, 1), date(2024, 8, 2)),
        test_session_dates=(date(2024, 7, 1), date(2024, 7, 2)),
        purged_session_dates=(),
        embargo_session_dates=(date(2024, 7, 3),),
        embargo_sessions_param=1,
        purge_formula_id="AFML_7_4_1_intraday_H_eq_session",
    )


def _make_metrics() -> AggregateMetrics:
    return AggregateMetrics(
        n_trades=1,
        n_long=1,
        n_short=0,
        n_flat_signals=0,
        pnl_rs_total=49.4,
        pnl_rs_per_contract_avg=49.4,
        sharpe_daily=None,
        sortino_daily=None,
        hit_rate=1.0,
        profit_factor=None,
        max_drawdown_rs=0.0,
        max_drawdown_pct=0.0,
        ulcer_index=None,
        avg_slippage_signed_ticks=-2.0,
        fill_rate=1.0,
        rejection_rate=0.0,
    )


def _make_stamp(ts: datetime | None = None) -> DeterminismStamp:
    return DeterminismStamp(
        seed=42,
        simulator_version="0.1.0",
        dataset_sha256="abc123",
        spec_sha256="def456",
        spec_version="0.2.0",
        engine_config_sha256="789xyz",
        rollover_calendar_sha256=None,
        cost_atlas_sha256=None,
        cpcv_config_sha256="cfg-hash",
        python_version="3.14.3",
        numpy_version="2.3.3",
        pandas_version="2.3.3",
        run_id="test-run-id",
        timestamp_brt=ts or datetime(2024, 7, 1, 12, 0, 0),
    )


def _make_diagnostics() -> FoldDiagnostics:
    return FoldDiagnostics(
        lookahead_audit_pass=True,
        holdout_lock_passed=True,
        holdout_unlock_used=False,
        force_exit_count=1,
        triple_barrier_exit_count=0,
        embargo_overlap_warnings=(),
        n_signals_total=4,
        n_signals_non_flat=1,
    )


# ---------------------------------------------------------------
# Frozen-ness
# ---------------------------------------------------------------
def test_trade_record_is_frozen() -> None:
    t = _make_trade()
    with pytest.raises(FrozenInstanceError):
        t.pnl_rs = 999.0  # type: ignore[misc]


def test_fold_metadata_is_frozen() -> None:
    f = _make_fold()
    with pytest.raises(FrozenInstanceError):
        f.path_index = 99  # type: ignore[misc]


def test_aggregate_metrics_is_frozen() -> None:
    m = _make_metrics()
    with pytest.raises(FrozenInstanceError):
        m.n_trades = 999  # type: ignore[misc]


def test_determinism_stamp_is_frozen() -> None:
    s = _make_stamp()
    with pytest.raises(FrozenInstanceError):
        s.seed = 999  # type: ignore[misc]


def test_fold_diagnostics_is_frozen() -> None:
    d = _make_diagnostics()
    with pytest.raises(FrozenInstanceError):
        d.force_exit_count = 999  # type: ignore[misc]


def test_backtest_result_is_frozen() -> None:
    r = BacktestResult(
        fold=_make_fold(),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    with pytest.raises(FrozenInstanceError):
        r.trades = ()  # type: ignore[misc]


# ---------------------------------------------------------------
# content_sha256 — AC12 byte-identical determinism (3 runs)
# ---------------------------------------------------------------
def test_content_sha256_stable_across_three_constructions() -> None:
    """3 independent constructions of the same logical result MUST hash equal."""
    hashes = []
    for _ in range(3):
        r = BacktestResult(
            fold=_make_fold(),
            trades=(_make_trade(),),
            metrics=_make_metrics(),
            determinism=_make_stamp(),
            diagnostics=_make_diagnostics(),
        )
        hashes.append(r.content_sha256())
    assert len(set(hashes)) == 1, f"3 runs produced different hashes: {hashes}"


def test_content_sha256_excludes_determinism_timestamp() -> None:
    """Two results identical EXCEPT for ``DeterminismStamp.timestamp_brt``
    must produce the same ``content_sha256`` — the timestamp is not part
    of the canonical content (it's a per-run wall-clock).
    """
    r1 = BacktestResult(
        fold=_make_fold(),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(datetime(2024, 7, 1, 9, 0)),
        diagnostics=_make_diagnostics(),
    )
    r2 = BacktestResult(
        fold=_make_fold(),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(datetime(2024, 7, 1, 21, 30)),  # different time
        diagnostics=_make_diagnostics(),
    )
    assert r1.content_sha256() == r2.content_sha256()


def test_content_sha256_changes_when_pnl_changes() -> None:
    """Sanity: if a real piece of content changes, the hash MUST differ."""
    r1 = BacktestResult(
        fold=_make_fold(),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    altered_metrics = AggregateMetrics(
        n_trades=1,
        n_long=1,
        n_short=0,
        n_flat_signals=0,
        pnl_rs_total=999.99,  # changed
        pnl_rs_per_contract_avg=999.99,
        sharpe_daily=None,
        sortino_daily=None,
        hit_rate=1.0,
        profit_factor=None,
        max_drawdown_rs=0.0,
        max_drawdown_pct=0.0,
        ulcer_index=None,
        avg_slippage_signed_ticks=-2.0,
        fill_rate=1.0,
        rejection_rate=0.0,
    )
    r2 = BacktestResult(
        fold=_make_fold(),
        trades=(_make_trade(),),
        metrics=altered_metrics,
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    assert r1.content_sha256() != r2.content_sha256()


def test_content_sha256_changes_when_path_index_changes() -> None:
    r1 = BacktestResult(
        fold=_make_fold(path_index=0),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    r2 = BacktestResult(
        fold=_make_fold(path_index=1),
        trades=(_make_trade(),),
        metrics=_make_metrics(),
        determinism=_make_stamp(),
        diagnostics=_make_diagnostics(),
    )
    assert r1.content_sha256() != r2.content_sha256()


# ---------------------------------------------------------------
# Trade contract parity (AC14)
# ---------------------------------------------------------------
def test_trade_uses_same_fill_type_as_live_broker() -> None:
    """AC14: TradeRecord.entry_fill / exit_fill MUST be the same Fill type
    used by the live broker (re-exported from exec_backtest).
    """
    t = _make_trade()
    assert isinstance(t.entry_fill, Fill)
    assert isinstance(t.exit_fill, Fill)
