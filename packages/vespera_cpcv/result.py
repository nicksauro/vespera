"""Result dataclasses — Beckett shape spec T002-backtest-result-shape.md §1.

6 frozen dataclasses:
    TradeRecord       — one round-trip in a fold
    FoldMetadata      — CPCV path identity (groups, sessions, purge/embargo)
    AggregateMetrics  — per-fold summary scalars
    DeterminismStamp  — R15 reproducibility audit
    FoldDiagnostics   — lookahead audit, force-exit count, etc.
    BacktestResult    — top-level: one fold's complete artifact

Plus a ``content_sha256()`` method on BacktestResult for byte-identical
determinism checks (AC12).

All fields are frozen / immutable — pass tuples, not lists; frozensets,
not sets.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import date, datetime
from typing import Any

# AC14 contract — ``Fill`` is the canonical entry/exit record shared with
# the live broker. Reuse, do NOT duplicate.
from packages.t002_eod_unwind.adapters.exec_backtest import Fill
from packages.t002_eod_unwind.core.signal_rule import Direction


# ---------------------------------------------------------------
# 1.1 — TradeRecord
# ---------------------------------------------------------------
@dataclass(frozen=True)
class TradeRecord:
    """One round-trip in the fold. AC14 contract — entry+exit are the same
    ``Fill`` type used by live broker (``packages/...adapters/exec_*.py``).

    T002.6 F2-T1 — additive fields per Mira Gate 4b spec §15.3 (Phase F2 IC
    pipeline wiring; Beckett consumer audit §T0c additive frozen-dataclass
    extension; semver minor bump). Fields are populated by the
    ``make_backtest_fn`` closure at trade-record time:

    - ``predictor_signal_per_trade`` — signed value
      ``-intraday_flow_direction`` per §15.1 sign convention (predictor for
      C1 + C2 IC computation). FADE strategy: positive flow → SHORT
      (predictor = -1); negative flow → LONG (predictor = +1).
    - ``forward_return_at_1755_pts`` — forward return in WDO points from
      entry to 17:55:00 BRT close, signed by trade direction (label for C1
      IC). ``None`` when exit was vertical at 17:55 itself (degenerate
      label — zero forward window) or when the close-at-17:55 reference
      price is unavailable (synthetic walk Phase E — IC compute deferred).

    Back-compat: defaults preserve existing callsites (``test_result_dataclasses``
    + any cached pickled artifacts whose mathematical content is unchanged).
    Round 1 N7 cached artifacts MUST be regenerated for IC computation per
    F2-T4 Beckett N7-prime re-run mandate (Mira spec §15.3 / §15.11).
    """

    session_date: date
    trial_id: str
    entry_window_brt: str  # "16:55" | "17:10" | "17:25" | "17:40"
    direction: Direction
    entry_fill: Fill
    exit_fill: Fill
    pnl_rs: float
    slippage_rs_signed: float
    fees_rs: float
    duration_seconds: int
    forced_exit: bool
    flags: frozenset[str]
    # T002.6 F2-T1 additive fields (Mira spec §15.3 — predictor + label).
    # Default 0.0 / None preserve back-compat for existing callsites that
    # do not yet emit per-event predictor/label (synthetic Phase E + legacy
    # test fixtures); the real Phase F closure populates them per §15.1.
    predictor_signal_per_trade: float = 0.0
    forward_return_at_1755_pts: float | None = None


# ---------------------------------------------------------------
# 1.2 — FoldMetadata
# ---------------------------------------------------------------
@dataclass(frozen=True)
class FoldMetadata:
    """Identifies WHICH path in {0..n_paths-1}, WHICH groups train/test,
    WHICH days were purged/embargoed.
    """

    path_index: int
    n_groups_total: int
    k_test_groups: int
    train_group_ids: tuple[int, ...]
    test_group_ids: tuple[int, ...]
    train_session_dates: tuple[date, ...]
    test_session_dates: tuple[date, ...]
    purged_session_dates: tuple[date, ...]
    embargo_session_dates: tuple[date, ...]
    embargo_sessions_param: int
    purge_formula_id: str


# ---------------------------------------------------------------
# 1.3 — AggregateMetrics
# ---------------------------------------------------------------
@dataclass(frozen=True)
class AggregateMetrics:
    """Per-fold summary. Computed by ``vespera_metrics.compute_fold_metrics``."""

    n_trades: int
    n_long: int
    n_short: int
    n_flat_signals: int
    pnl_rs_total: float
    pnl_rs_per_contract_avg: float
    sharpe_daily: float | None
    sortino_daily: float | None
    hit_rate: float | None
    profit_factor: float | None
    max_drawdown_rs: float
    max_drawdown_pct: float
    ulcer_index: float | None
    avg_slippage_signed_ticks: float
    fill_rate: float
    rejection_rate: float


# ---------------------------------------------------------------
# 1.4 — DeterminismStamp
# ---------------------------------------------------------------
@dataclass(frozen=True)
class DeterminismStamp:
    """R15 + reproducibility checklist."""

    seed: int
    simulator_version: str
    dataset_sha256: str
    spec_sha256: str
    spec_version: str
    engine_config_sha256: str
    rollover_calendar_sha256: str | None
    cost_atlas_sha256: str | None
    cpcv_config_sha256: str
    python_version: str
    numpy_version: str
    pandas_version: str
    run_id: str
    timestamp_brt: datetime  # BRT-naive (R2)


# ---------------------------------------------------------------
# 1.5 — FoldDiagnostics
# ---------------------------------------------------------------
@dataclass(frozen=True)
class FoldDiagnostics:
    """Audit + sanity."""

    lookahead_audit_pass: bool
    holdout_lock_passed: bool
    holdout_unlock_used: bool
    force_exit_count: int
    triple_barrier_exit_count: int
    embargo_overlap_warnings: tuple[str, ...]
    n_signals_total: int
    n_signals_non_flat: int


# ---------------------------------------------------------------
# 1.6 — BacktestResult (top-level)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class BacktestResult:
    """Output of ONE fold in ``CPCVEngine.run()``. Frozen — must be byte
    identical across re-runs given the same ``DeterminismStamp`` + fold
    inputs (AC12).

    Persisted at: ``docs/backtest/runs/{run_id}/folds/path_{path_index:02d}.json``
    """

    fold: FoldMetadata
    trades: tuple[TradeRecord, ...]
    metrics: AggregateMetrics
    determinism: DeterminismStamp
    diagnostics: FoldDiagnostics

    def content_sha256(self) -> str:
        """SHA-256 of (fold, trades, metrics, diagnostics) — EXCLUDING
        ``determinism`` (which carries a wall-clock ``timestamp_brt`` that
        legitimately varies between re-runs).

        Two re-runs of the same fold with the same dataset + spec + seed
        MUST produce the same hash. This is the AC12 invariant.
        """
        payload = {
            "fold": _frozen_to_jsonable(self.fold),
            "trades": [_frozen_to_jsonable(t) for t in self.trades],
            "metrics": _frozen_to_jsonable(self.metrics),
            "diagnostics": _frozen_to_jsonable(self.diagnostics),
        }
        canonical = json.dumps(payload, sort_keys=True, default=_default_json)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------
# JSON serialization helpers (private)
# ---------------------------------------------------------------
def _default_json(obj: Any) -> Any:
    """Fallback JSON encoder for non-standard types in result tree."""
    if isinstance(obj, datetime):
        # BRT-naive (R2) — no tz suffix; isoformat keeps microseconds if present
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, frozenset):
        return sorted(obj)
    if isinstance(obj, Direction):
        return obj.value
    if isinstance(obj, Fill):
        return _frozen_to_jsonable(obj)
    raise TypeError(f"Cannot serialize {type(obj).__name__} for content_sha256")


def _frozen_to_jsonable(obj: Any) -> dict[str, Any]:
    """Recursively convert a frozen dataclass tree to a JSON-able dict."""
    raw = asdict(obj)
    return _normalize(raw)


def _normalize(obj: Any) -> Any:
    """Walk and convert types not natively JSON-able."""
    if isinstance(obj, dict):
        return {k: _normalize(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_normalize(v) for v in obj]
    if isinstance(obj, frozenset):
        return sorted(_normalize(v) for v in obj)
    if isinstance(obj, set):
        return sorted(_normalize(v) for v in obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Direction):
        return obj.value
    return obj


__all__ = [
    "AggregateMetrics",
    "BacktestResult",
    "DeterminismStamp",
    "FoldDiagnostics",
    "FoldMetadata",
    "TradeRecord",
]
