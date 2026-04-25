# T002 — `BacktestResult` Shape Specification

**Author:** Beckett (The Simulator) — backtester
**Date BRT:** 2026-04-25
**Status:** DRAFT — handshake-pending with Mira (purge formula → `vespera_metrics` interface)
**Spec ref:** `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml`
**Consumes from:** `packages/t002_eod_unwind/adapters/exec_backtest.py` (`BacktestBroker`, `Fill`, `pnl_contracts`)
**Consumed by:** `CPCVEngine.run(events, backtest_fn) -> list[BacktestResult]` and downstream `vespera_metrics`
**Constitutional gates:** AC9 (17:55 hard stop), AC11 (manual PnL parity), AC12 (determinism), AC14 (Trade contract parity backtest↔live), MANIFEST R1 (hold-out virgin), R2 (BRT-naive), R15 (preregistration revisions).

---

## 0. TL;DR — for the impatient

A `BacktestResult` is the **complete, byte-reproducible artifact of running one CPCV path** (= one fold in {0, 1, …, 44}). It carries:

1. **Fold identity** (which fold, which trained groups, which test groups, which embargo).
2. **Trade ledger** (every entry/exit/PnL/slippage/fees event, in order).
3. **Aggregate metrics** computed by `vespera_metrics` over that ledger.
4. **Determinism stamps** (seed, dataset hash, sim version, spec hash, engine-config hash) — required by Beckett `reproducibility_checklist`.
5. **Diagnostics** (lookahead audit, force-exit count, embargo overlap warnings).

`CPCVEngine.run(events, backtest_fn)` returns `list[BacktestResult]` of length `n_paths` (45 for default CPCV N=10/k=2). `vespera_metrics.aggregate_paths([...])` then ingests the list to compute DSR, PBO, IC_spearman, etc.

---

## 1. The `BacktestResult` dataclass

**Location proposed:** `packages/t002_eod_unwind/backtest/result.py` (new module — Dex implements after handshake closes; do NOT create until then).

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal

from packages.t002_eod_unwind.adapters.exec_backtest import Fill
from packages.t002_eod_unwind.core.signal_rule import Direction


# ---------------------------------------------------------------
# 1.1 — TradeRecord (trade-level row)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class TradeRecord:
    """One round-trip in the fold. AC14 contract — entry+exit must come
    from the same Fill type used by live broker (`packages/...adapters/exec_*.py`).
    """
    session_date: date              # BRT-naive — the trading day
    trial_id: str                   # "T1".."T5" — Bonferroni cell
    entry_window_brt: str           # "16:55" | "17:10" | "17:25" | "17:40"
    direction: Direction            # LONG / SHORT (FLAT trades excluded from ledger)
    entry_fill: Fill                # AC14 — same type as live
    exit_fill: Fill                 # forced at 17:55 (AC9) OR triple-barrier (Fase E)
    pnl_rs: float                   # net of fees (matches `pnl_contracts(...)`)
    slippage_rs_signed: float       # signed cost of slippage on round-trip (entry+exit)
    fees_rs: float                  # entry.fees + exit.fees
    duration_seconds: int           # exit_fill.ts - entry_fill.ts
    forced_exit: bool               # True if exit_fill.reason == "exit_hard_stop"
    flags: frozenset[str]           # e.g. "rollover_week", "pre_copom", "high_vol"


# ---------------------------------------------------------------
# 1.2 — FoldMetadata (CPCV path identity)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class FoldMetadata:
    """Identifies WHICH path in {0..n_paths-1}, WHICH groups train/test,
    WHICH days were purged/embargoed. Required by vespera_metrics for PBO
    reconstruction (rank IS vs OOS by path).
    """
    path_index: int                 # 0..44 for default N=10/k=2
    n_groups_total: int             # 10 (default)
    k_test_groups: int              # 2 (default)
    train_group_ids: tuple[int, ...]
    test_group_ids: tuple[int, ...]
    train_session_dates: tuple[date, ...]   # post-purge, post-embargo
    test_session_dates: tuple[date, ...]
    purged_session_dates: tuple[date, ...]  # samples whose label horizon overlapped test
    embargo_session_dates: tuple[date, ...] # buffer sessions removed (default = 1)
    embargo_sessions_param: int     # spec.cv_scheme.embargo_sessions
    purge_formula_id: str           # PENDING — see §7. Mira owns the formula tag.


# ---------------------------------------------------------------
# 1.3 — AggregateMetrics (per-fold summary)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class AggregateMetrics:
    """Fold-level scalars. Computed by `vespera_metrics.compute_fold_metrics(trades)`.
    These feed into cross-path aggregates (DSR, PBO) downstream.
    """
    n_trades: int                   # may be 0 — see §6 edge cases
    n_long: int
    n_short: int
    n_flat_signals: int             # signals fired but direction=FLAT (no trade)
    pnl_rs_total: float
    pnl_rs_per_contract_avg: float
    sharpe_daily: float | None      # None if n_trades < 2
    sortino_daily: float | None
    hit_rate: float | None          # n_winning / n_trades
    profit_factor: float | None     # gross_wins / abs(gross_losses)
    max_drawdown_rs: float
    max_drawdown_pct: float
    ulcer_index: float | None
    avg_slippage_signed_ticks: float
    fill_rate: float                # n_trades_filled / n_signals_non_flat
    rejection_rate: float           # for backtest = 0.0 unless impact-rejection triggered


# ---------------------------------------------------------------
# 1.4 — DeterminismStamp (R15 + reproducibility_checklist)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class DeterminismStamp:
    seed: int                                  # default 42
    simulator_version: str                     # semver, e.g. "0.3.1"
    dataset_sha256: str                        # parquet bundle hash (DAY-level concat)
    spec_sha256: str                           # mira spec yaml hash (file content)
    spec_version: str                          # e.g. "0.2.0"
    engine_config_sha256: str                  # docs/backtest/engine-config.yaml hash
    rollover_calendar_sha256: str | None       # Nova calendar (None if not loaded)
    cost_atlas_sha256: str | None              # docs/backtest/nova-cost-atlas.yaml hash
    cpcv_config_sha256: str                    # hash of {N, k, embargo, purge_formula_id}
    python_version: str                        # e.g. "3.11.7"
    numpy_version: str
    pandas_version: str
    run_id: str                                # uuid4 — folder name under docs/backtest/runs/
    timestamp_brt: datetime                    # BRT-naive (R2) — when run started


# ---------------------------------------------------------------
# 1.5 — Diagnostics (audit + sanity)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class FoldDiagnostics:
    lookahead_audit_pass: bool                 # True if no fill ts < signal ts
    holdout_lock_passed: bool                  # always True in non-final runs (False if forced unlock used)
    holdout_unlock_used: bool                  # VESPERA_UNLOCK_HOLDOUT=1 was set
    force_exit_count: int                      # n trades closed by AC9 hard stop
    triple_barrier_exit_count: int             # 0 in v0.2.0 — Fase E only
    embargo_overlap_warnings: tuple[str, ...]  # human-readable, e.g. "PRR-rollover D-1 leaked to test"
    n_signals_total: int                       # incl. FLAT
    n_signals_non_flat: int


# ---------------------------------------------------------------
# 1.6 — BacktestResult (top-level)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class BacktestResult:
    """Output of ONE fold in CPCVEngine.run(). Frozen — must be byte-identical
    across re-runs given (DeterminismStamp, fold inputs).

    Persisted at: docs/backtest/runs/{run_id}/folds/path_{path_index:02d}.json
    """
    fold: FoldMetadata
    trades: tuple[TradeRecord, ...]            # ordered by entry_fill.ts
    metrics: AggregateMetrics
    determinism: DeterminismStamp
    diagnostics: FoldDiagnostics
    # serialization helpers (NOT fields, methods Dex implements):
    # def to_json(self) -> dict: ...
    # @classmethod from_json(cls, raw: dict) -> BacktestResult: ...
    # def content_sha256(self) -> str: ...   # for cross-run determinism check
```

---

## 2. Interface with the existing `BacktestBroker`

### 2.1 — What `BacktestBroker` produces today

`packages/t002_eod_unwind/adapters/exec_backtest.py` provides:

- `Fill(ts, price, qty, fees_rs, reason)` — frozen dataclass.
- `BacktestBroker.execute(...) -> Fill` — entry market order with deterministic slippage (`Roll_spread_half + 1 tick`).
- `BacktestBroker.force_exit(...) -> Fill` — AC9 hard stop fill.
- `pnl_contracts(entry, exit_) -> float` — net R$ PnL.

This is **per-trade**. It has **no awareness** of folds, paths, or aggregate metrics. That is correct — broker stays single-purpose.

### 2.2 — Gap analysis (broker → BacktestResult)

| Need | Source today | Gap |
|---|---|---|
| Per-trade entry/exit fills | `BacktestBroker.execute / force_exit` | NONE — direct reuse |
| `pnl_rs` net of fees | `pnl_contracts(entry, exit)` | NONE — direct reuse |
| `slippage_rs_signed` per round-trip | NOT exposed (computed implicitly inside `_slippage()`) | **Refactor needed:** expose `slip_points_signed` on `Fill` OR derive from `(entry.price - mid_at_entry) + (mid_at_exit - exit.price)` recorded by caller |
| `forced_exit` flag | `Fill.reason == "exit_hard_stop"` | NONE — already encoded |
| `duration_seconds` | `entry.ts`, `exit_.ts` | NONE — caller computes |
| Aggregate metrics (sharpe, etc.) | NOT in broker scope | by design — `vespera_metrics` owns this |
| Determinism stamp | NOT in broker scope | by design — `BacktestRunner` (Dex implements after handshake) injects |

### 2.3 — Required minor refactor on `BacktestBroker`

Two options. **Beckett recommendation: Option B (additive, non-breaking).**

**Option A** — extend `Fill` with `mid_price_ref: float | None` and `slip_points: float | None`. Pro: self-contained record. Con: changes `Fill` shape — breaks AC14 parity with live `Fill` unless live also carries those fields.

**Option B** *(recommended)* — keep `Fill` immutable. Have `BacktestRunner` (the loop one level above broker) record `mid_at_entry` / `mid_at_exit` in the `TradeRecord` it builds. Slippage is then `entry.price - mid_at_entry - (exit.price - mid_at_exit) * sign(qty)`. This preserves AC14 (live `Fill` shape unchanged) and confines broker concerns to broker.

**No code changes to `exec_backtest.py` itself** for this story. Dex only writes the new `BacktestRunner` + `result.py` after Beckett↔Mira handshake closes (§7).

---

## 3. Interface with `CPCVEngine`

### 3.1 — Signature

```python
def CPCVEngine.run(
    self,
    events: Iterable[SessionEvent],          # Dara/Nova-prepared, sorted by ts BRT-naive
    backtest_fn: Callable[[FoldInputs], BacktestResult],
) -> list[BacktestResult]:
    ...
```

Where `FoldInputs` carries everything `backtest_fn` needs to be deterministic *for that path*:

```python
@dataclass(frozen=True)
class FoldInputs:
    fold: FoldMetadata                # pre-computed by CPCVEngine
    train_events: tuple[SessionEvent, ...]
    test_events: tuple[SessionEvent, ...]
    determinism: DeterminismStamp     # injected from runner — copied into each result
    spec_snapshot: SpecSnapshot       # frozen view of Mira spec at run start
```

### 3.2 — Contract guarantees

- **Length:** `len(result) == spec.cv_scheme.n_paths` (45 for default).
- **Order:** results sorted by `result.fold.path_index` ascending.
- **Determinism:** for the same `(events, spec, seed, sim_version)`, the function returns a list whose elements are pairwise byte-equal across re-runs (AC12). This is checked by `content_sha256()` per fold.
- **No I/O in backtest_fn:** results are returned in-memory; `CPCVEngine` is the one that persists `docs/backtest/runs/{run_id}/folds/path_*.json`.
- **Hold-out gate:** `CPCVEngine` calls `assert_holdout_safe(...)` before iterating events, on the OUTER window (`min(event.ts).date()`, `max(event.ts).date()`). Per-fold gate is **not needed** because the outer window already covers all sub-windows.

### 3.3 — `backtest_fn` responsibilities

For each `FoldInputs`, `backtest_fn`:

1. Trains the model on `train_events` (T002 v0.2.0: trains the percentile bands P60/P20/P80 over `train_events` — model is non-parametric).
2. Replays `test_events` through `BacktestBroker` + signal logic exactly as in `tests/t002_eod_unwind/integration/test_backtest_one_day.py::_run_day`.
3. Collects `TradeRecord`s, computes `AggregateMetrics` via `vespera_metrics`, stamps `DeterminismStamp`, writes `FoldDiagnostics`.
4. Returns one `BacktestResult`.

---

## 4. Interface with `vespera_metrics`

Mira is specifying this module in parallel. Beckett's commitment: **`BacktestResult` carries every input `vespera_metrics` needs for the metrics in `spec.metrics_required`.**

| Metric (spec L160-172) | Source field on `BacktestResult` | Aggregation level |
|---|---|---|
| `IC_spearman` | `metrics.pnl_rs_per_contract_avg` per fold + spec label values from `events` | cross-path (n=45) |
| `DSR` | `metrics.sharpe_daily` per fold + `n_trials` from spec L126 | cross-path + N_trials |
| `PBO` | `metrics.sharpe_daily` per fold + `fold.path_index` + IS-rank table | cross-path |
| `sharpe_distribution_45paths` | `metrics.sharpe_daily` per fold | cross-path |
| `sortino` | `metrics.sortino_daily` per fold | cross-path mean/median |
| `MAR` | `metrics.pnl_rs_total / abs(metrics.max_drawdown_rs)` | per fold then aggregate |
| `max_drawdown` | `metrics.max_drawdown_rs`, `metrics.max_drawdown_pct` | distribution |
| `hit_rate` | `metrics.hit_rate` | distribution |
| `profit_factor` | `metrics.profit_factor` | distribution |
| `ulcer_index` | `metrics.ulcer_index` | distribution |
| `bootstrap_ci_ic_10k` | per-trade `pnl_rs` from `trades` ledger | bootstrap over all paths |
| stress-regime breakdowns (spec §stress_regimes) | `trades[i].flags` | filter then re-aggregate |

**Two-layer split:**

- **Beckett (per-fold, deterministic):** computes `AggregateMetrics` scalars from the `trades` tuple. These are simple closed-form aggregations — no statistical inference.
- **Mira / `vespera_metrics` (cross-fold, statistical):** consumes `list[BacktestResult]` to produce DSR (needs `N_trials`), PBO (needs IS-vs-OOS rank table), bootstrap CI, deflated metrics. **This requires Mira's purge formula closed (§7).**

---

## 5. Determinism contract

Mandatory invariants enforced by `BacktestResult`:

1. **Seed propagation:** `DeterminismStamp.seed` is set at runner construction, propagated to every randomness source (numpy, python `random`, any sampler in `vespera_metrics`). T002 v0.2.0 has no stochastic model component (percentile bands are deterministic), so `seed` only affects bootstrap CI in `vespera_metrics`.
2. **Dataset hash:** SHA-256 over the *concatenation* of parquet bytes for all trading days in `[in_sample.start, hold_out_virgin.end]`, computed at runner start. Mismatch ⇒ refuse to run.
3. **Spec hash:** SHA-256 of the spec yaml *file content* (not normalized — yaml whitespace counts). Logged also as `spec_version` for human readability. Mismatch with previous run ⇒ R15 revision required.
4. **Engine-config hash:** SHA-256 of `docs/backtest/engine-config.yaml` (when wired — currently `BacktestCosts` is hardcoded; track as `[TO-VERIFY]` until engine-config is loaded).
5. **Sim version stamp:** `simulator_version` is a semver string baked into the `BacktestRunner` module. Bump on any logic change (broker, signal, runner). CPCV re-run from scratch is mandatory on minor bumps that touch fill/cost logic.
6. **No lookahead:** `FoldDiagnostics.lookahead_audit_pass` is computed by walking `trades` in order and asserting `entry_fill.ts >= signal_ts` for every record. False ⇒ run rejected.
7. **Re-run check:** `BacktestResult.content_sha256()` of (`fold` + `trades` + `metrics` excluding `determinism`) must be identical across re-runs given the same `DeterminismStamp`. AC12 test enforces this for 3 runs.

---

## 6. Edge cases

| Case | Handling |
|---|---|
| **Empty fold** (test_events spans 0 sessions due to embargo) | Return `BacktestResult` with `trades=()`, `metrics.n_trades=0`, `metrics.sharpe_daily=None`. `vespera_metrics` must accept `None` and treat as missing observation (NOT zero). |
| **Zero trades in fold** (all signals FLAT — magnitude/regime filters reject every day) | Same as above — `trades=()` but `metrics.n_flat_signals = n_eligible_days`. Still a valid path; counts toward distribution. |
| **Single-trade fold** | `metrics.sharpe_daily=None` (need ≥2 obs). `vespera_metrics` skips this fold for sharpe-distribution but counts it for `hit_rate` / `pnl_total`. |
| **Embargo overlap with rollover D-3..D-1** | Spec §universe excludes those days at sample-construction time. If `FoldMetadata.test_session_dates` contains any rollover date, `FoldDiagnostics.embargo_overlap_warnings` records it and the run is **flagged but not failed**. Mira reviews. |
| **Hold-out leakage** | `assert_holdout_safe` raises BEFORE any I/O. If `VESPERA_UNLOCK_HOLDOUT=1` is set (Fase E final run only), `DeterminismStamp` records `holdout_unlock_used=True` for audit. |
| **Force-exit at 17:55 with no liquidity** (no trade observed in [17:55, 17:55+ε]) | Per `fill_rules_trades_only`, broker walks subsequent trades pessimistically. If session has no trades after 17:55 timestamp (synthetic/sparse data), broker uses `state.last_price`. This is the documented behavior (`test_backtest_one_day.py` confirms). `TradeRecord.flags` records `"forced_exit_no_post_liquidity"`. |
| **Triple-barrier label (Fase E)** | Out of scope for v0.2.0. `TradeRecord` shape is forward-compatible — `exit_fill.reason` is an open string; runner sets `"exit_triple_barrier_pt"` / `"exit_triple_barrier_sl"` / `"exit_triple_barrier_timeout"` in Fase E. |
| **Spec breaking-field revision mid-batch** | Per R15: each `BacktestResult.determinism.spec_version` is checked against the running spec at result-collection time. Mismatch ⇒ batch invalidated, full CPCV re-run required. No partial reuse. |

---

## 7. Handshake status — what's pending before Dex builds

**Beckett's side: COMPLETE.** Shape above is final from broker / fold / determinism / diagnostics perspective.

**Pending on Mira:**

1. **Purge formula** — needed to fill `FoldMetadata.purge_formula_id` and to determine which `train_session_dates` are dropped. Mira's CV scheme (spec L148-154) says `purging: true` but doesn't pin the formula. Default Lopez de Prado AFML §7.4.1: drop train samples whose label horizon `[t, t+H]` overlaps any `test_session_dates`. T002 horizon `H = entry_ts → 17:55` (intraday only) means purge is tight (same-day overlap only — minimal impact). **Beckett requests Mira confirm: same-day-only purge, formula tag `"AFML_7_4_1_intraday_H_eq_session"`.** This impacts effective sample size per fold.
2. **`vespera_metrics` signature** — Mira owns. Beckett needs the function name(s) so `BacktestRunner` can call them. Provisional: `vespera_metrics.compute_fold_metrics(trades: tuple[TradeRecord, ...]) -> AggregateMetrics` and `vespera_metrics.aggregate_paths(results: list[BacktestResult], spec: SpecSnapshot) -> CrossPathReport`.
3. **`SpecSnapshot` shape** — Mira's domain. Frozen view of yaml fields needed by metrics (n_trials.total, cv_scheme params, label horizon). Beckett only forwards.
4. **`SessionEvent` schema** — Dara/Nova have the parquet shape (Beckett persona §historical_data_reality). Confirm whether `CPCVEngine` works on raw `Trade` events or on pre-grouped session aggregates. **Beckett recommendation:** keep raw `Trade` events; grouping into sessions happens inside `backtest_fn` (matches the live loop contract from `test_backtest_one_day.py::_run_day`).

**Once Mira confirms (1) and (2):** Beckett signs off, Pax validates the story, Dex implements `result.py` + `BacktestRunner` + `CPCVEngine.run`. Quinn QA gates. Gage pushes.

**Until then:** this document is the locked contract. Any change to `BacktestResult` fields after Pax sign-off triggers a new revision (R15) and CPCV re-run from scratch.

— Beckett, reencenando o passado 🎞️
