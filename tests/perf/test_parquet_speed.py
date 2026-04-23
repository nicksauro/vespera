"""Performance test — feed_parquet cold-start budget (T002.0b AC13 cold).

Story: T002.0b (T6a)
Epic:  EPIC-T002.0

Budget
------
Cold read of one WDO session (~500k-850k trades) MUST complete in ≤ 10s
on dev hardware. "Cold" means the integrity cache is cleared before each
measurement so sha256 verification is paid fresh (worst case).

The budget is the gate-of-viability for CPCV 45 paths × ~250 sessions:
if one cold session takes > 10s, the hot loop amortization (AC13b) has no
runway.

Regimes (T6 in story)
---------------------
- baseline:  2024-03-04 (typical session)
- high_vol:  2024-05-02 (FOMC adjacent)
- low_vol:   2024-07-05 (pós-feriado EUA 4-jul)

Currently only baseline is live (2024-03 parquet exists). high_vol and
low_vol are skipped until T002.0a completes full materialization. Beckett
signs AC13(b) with the three-regime measurement later; T6(b) is blocked
on T002.0a per the story.
"""

from __future__ import annotations

import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]

_COLD_BUDGET_SEC = 10.0


def _parquet_for(day: datetime) -> Path:
    return (
        _REPO
        / "data"
        / "in_sample"
        / f"year={day.year:04d}"
        / f"month={day.month:02d}"
        / f"wdo-{day.year:04d}-{day.month:02d}.parquet"
    )


def _measure_cold(day: datetime) -> tuple[float, int]:
    """Drop the integrity cache, time one full session read, return (dt, n_trades)."""
    from packages.t002_eod_unwind.adapters import feed_parquet

    feed_parquet._reset_integrity_cache()

    start = day
    end = day + timedelta(days=1)

    t0 = time.perf_counter()
    n = 0
    for _ in feed_parquet.load_trades(start, end, "WDO"):
        n += 1
    dt = time.perf_counter() - t0
    return dt, n


@pytest.mark.skipif(
    not _parquet_for(datetime(2024, 3, 4)).exists(),
    reason="2024-03 parquet not materialized",
)
def test_cold_baseline_under_budget():
    """baseline regime (2024-03-04): cold read ≤ 10s."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dt, n = _measure_cold(datetime(2024, 3, 4))

    print(f"\n[perf] cold baseline 2024-03-04: {n} trades in {dt:.2f}s")
    assert n > 0, "baseline must return trades"
    assert dt <= _COLD_BUDGET_SEC, (
        f"cold baseline 2024-03-04 took {dt:.2f}s > {_COLD_BUDGET_SEC}s budget"
    )


@pytest.mark.skipif(
    not _parquet_for(datetime(2024, 5, 2)).exists(),
    reason="2024-05 parquet not materialized",
)
def test_cold_high_vol_under_budget():
    """high_vol regime (2024-05-02, FOMC-adjacent): cold read ≤ 10s."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dt, n = _measure_cold(datetime(2024, 5, 2))

    print(f"\n[perf] cold high_vol 2024-05-02: {n} trades in {dt:.2f}s")
    assert n > 0, "high_vol must return trades"
    assert dt <= _COLD_BUDGET_SEC, (
        f"cold high_vol 2024-05-02 took {dt:.2f}s > {_COLD_BUDGET_SEC}s budget"
    )


@pytest.mark.skipif(
    not _parquet_for(datetime(2024, 7, 5)).exists(),
    reason="2024-07 parquet not materialized",
)
def test_cold_low_vol_under_budget():
    """low_vol regime (2024-07-05, post-US-July4th): cold read ≤ 10s."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        dt, n = _measure_cold(datetime(2024, 7, 5))

    print(f"\n[perf] cold low_vol 2024-07-05: {n} trades in {dt:.2f}s")
    assert n > 0, "low_vol must return trades"
    assert dt <= _COLD_BUDGET_SEC, (
        f"cold low_vol 2024-07-05 took {dt:.2f}s > {_COLD_BUDGET_SEC}s budget"
    )


# ---------------------------------------------------------------------------
# T6(b) hot-loop — BLOCKED on T002.0a full materialization.
# ---------------------------------------------------------------------------

@pytest.mark.skip(
    reason="Blocked by T002.0a full materialization (needs ~250 in-sample sessions)"
)
def test_hot_loop_cpcv_1path_250_sessions_under_budget():
    """AC13(b) — 1 path × ~250 sessions ≤ 4.5 min. Blocked on T002.0a.

    Will be unblocked once PID 12608 finishes materializing all in-sample
    months (2024-07 through 2025-06). Beckett assigns the measurement and
    signs on the story with 3-regime numbers.
    """
    raise NotImplementedError("Unblocked when full in-sample parquet is ready")
