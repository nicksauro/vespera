"""Vespera CPCV — Purged Combinatorial Cross-Validation engine.

Story: T002.0c — implements AFML Ch.12 §12.4 CPCV with §7.4.1 purging
and §7.4.2 embargo.

Public API:
    CPCVConfig         — frozen config dataclass (n_groups, k, embargo, seed, purge_formula_id)
    CPCVEngine         — engine with generate_splits() + run() entrypoints
    CPCVSplit          — one fold's train/test partition (frozen)
    BacktestRunner     — orchestrator: adapter → engine → broker → metrics_callback

Result dataclasses (Beckett shape spec, T002-backtest-result-shape.md §1):
    TradeRecord
    FoldMetadata
    AggregateMetrics
    DeterminismStamp
    FoldDiagnostics
    BacktestResult

Exceptions:
    HoldoutLockError   — re-export from packages.t002_eod_unwind.adapters._holdout_lock
"""

from __future__ import annotations

from packages.t002_eod_unwind.adapters._holdout_lock import (
    HoldoutLockError,
    assert_holdout_safe,
)

from .config import CPCVConfig
from .engine import CPCVEngine, CPCVSplit
from .result import (
    AggregateMetrics,
    BacktestResult,
    DeterminismStamp,
    FoldDiagnostics,
    FoldMetadata,
    TradeRecord,
)
from .runner import BacktestRunner

__all__ = [
    "AggregateMetrics",
    "BacktestResult",
    "BacktestRunner",
    "CPCVConfig",
    "CPCVEngine",
    "CPCVSplit",
    "DeterminismStamp",
    "FoldDiagnostics",
    "FoldMetadata",
    "HoldoutLockError",
    "TradeRecord",
    "assert_holdout_safe",
]
