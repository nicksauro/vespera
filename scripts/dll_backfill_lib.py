"""dll_backfill_lib — shared primitives for DLL backfill orchestrator (Phase 2A).

Source of truth:    scripts/dll_probe_2023_12_wdofut.py (Council 2026-05-01 R1-R4
                    canonical artifact, Phase-1 fixes applied; NEVER mutated).
Spec:               docs/research/dll-probes/A1-spec-2023-12-WDOFUT.md (probe shape)
Council:            COUNCIL-2026-05-01-DATA-resolution.md (R1-R4 + R10 + AP-D-*)
Authority:          Dara (@data-engineer) implementation; Nelo (@profitdll-specialist)
                    primitives author. Article IV: every primitive below traces to
                    the canonical probe — no invention.

Purpose
-------
Phase 2A deliverable: extract probe primitives into a shared library that supports
multi-chunk backfill orchestration, AND introduce ``IncrementalParquetSink`` for
streaming persistence (RAM-bounded ~50 MB peak vs probe single-shot ~2 GB peak
for ~5M rows).

This module is consumed by ``dll_backfill_smoke.py`` (Phase 2A validator) and
the future Phase 2B/2C orchestrator drivers. The canonical probe remains
intact — if you need to extend the probe family, extend HERE, not in the
council artifact.

Constraints (non-negotiable)
----------------------------
- Q-FIN-12-E (DLL quiesce): ``_shutdown_dll`` retains the 2.0s callback-idle
  quiet-period before DLLFinalize (defends against Windows SEH).
- Q-RANGE-13-E (5d max chunk): NOT enforced here — chunk caller decides; smoke
  uses 5d. Orchestrator wrappers will enforce.
- Q08-E: ``_CB_REFS`` global keepalive preserved. Caller must extend it.
- Q04-V: callbacks NEVER call DLL; they only queue or set primitives.
- Q01-V / Q02-V: WINFUNCTYPE + c_wchar_p preserved across all callbacks.
- Q03-V: exchange="F" hardcoded inside ``run_chunk`` (NOT "BMF").
- Q09-E: continuous tickers only — chunk caller is responsible for ticker hygiene.
- R10: writes ONLY to ``output_dir`` argument — never to ``data/manifest.csv``.

Diff vs probe (run_probe → run_chunk)
-------------------------------------
1. ``output_dir`` is a parameter (was hardcoded ``_OUTPUT_DIR``).
2. ``hard_timeout_s`` and ``idle_watchdog_s`` are parameters (were module
   constants).
3. ``sink_factory`` is a parameter:
     - ``None`` → reproduces single-shot ``_persist_parquet`` behaviour
       (back-compat with the probe; default).
     - ``Callable[[Path], IncrementalParquetSink]`` → uses streaming sink
       to keep RAM bounded for 5d chunks.
4. Logging path is rooted in ``output_dir``.
5. Schema validation window comes from the chunk dates (probe already
   parameterized this in Phase-1 fixes).
6. Telemetry artifact paths and "anti_patterns_audit" remain identical to the
   probe payload (so downstream parsers are unchanged).
"""

from __future__ import annotations

import ctypes
import json
import logging
import os
import queue
import sys
import threading
import time
import traceback
import uuid
from ctypes import (
    Structure,
    WINFUNCTYPE,
    c_char,
    c_double,
    c_int,
    c_int64,
    c_uint,
    c_wchar_p,
)
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

# --- Module-level constants (probe-faithful) -------------------------------

_PROBE_SPEC_VERSION = "A1-spec-2023-12-WDOFUT-v1.0"
_COUNCIL_RESOLUTION_REF = "COUNCIL-2026-05-01-DATA-resolution.md"

_LOGIN_WAIT_S = 60.0
_QUEUE_MAXSIZE = 20_000
_SCHEMA_VALIDATION_BATCH_SIZE = 1000


# --- ctypes structures matching DLL public API -----------------------------


class TAssetIDRec(Structure):
    """Manual §3 line 191. PWideChar fields (UTF-16). Probe lines 114-122."""

    _fields_ = [
        ("pwcTicker", c_wchar_p),
        ("pwcBolsa", c_wchar_p),
        ("nFeed", c_int),  # 0=Nelogica, 255=Outro
    ]


# --- Callback type aliases (WINFUNCTYPE per Q01-V + manual §3.2 L2735) -----

StateCB = WINFUNCTYPE(None, c_int, c_int)

ProgressCB = WINFUNCTYPE(None, TAssetIDRec, c_int)

# THistoryTradeCallback per manual §3.2 line 3730
HistoryTradeCB = WINFUNCTYPE(
    None,
    TAssetIDRec,    # rAssetID
    c_wchar_p,      # pwcDate (raw string per §6.1)
    c_uint,         # nTradeNumber
    c_double,       # dPrice
    c_double,       # dVol (financial volume R$ — Q07-V)
    c_int,          # nQtd (contracts)
    c_int,          # nBuyAgent (numeric agent_id)
    c_int,          # nSellAgent
    c_int,          # nTradeType (2=BUY, 3=SELL else NONE)
)

NoopAssetCB = WINFUNCTYPE(None, TAssetIDRec)
NoopVoidCB = WINFUNCTYPE(None)


# --- Data classes ----------------------------------------------------------


@dataclass
class ProbeState:
    """Mutable state shared between callbacks and engine thread.

    Replicates the probe's ``ProbeState`` (lines 154-174). Callbacks ONLY
    enqueue or set primitive fields — never call DLL or do I/O.
    """

    last_conn_type: int = -1
    last_result: int = -1
    last_progress: int = 0
    last_progress_ts: float = 0.0
    progress_99_started_ts: float | None = None
    progress_99_dwell_s: float | None = None
    last_callback_ts: float = 0.0
    queue_full_drops: int = 0
    login_ready_condition_observed: str | None = None
    login_wait_s: float = 0.0
    progress_timeline: list[dict] = field(default_factory=list)
    progress_reached_100: bool = False
    ts_separator_observed: str | None = None


# --- Module-global callback ref keepalive (Q08-E — prevents Python GC) -----

_CB_REFS: list = []


# --- Helpers ---------------------------------------------------------------


def _setup_logging(run_id: str, output_dir: Path) -> logging.Logger:
    """Probe lines 185-200, generalized — ``output_dir`` replaces ``_OUTPUT_DIR``.

    Creates a per-chunk logger isolated by ``run_id`` so concurrent chunks (if
    ever orchestrated in parallel; not a smoke concern) do not collide.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / f"probe-stdout-stderr-{run_id}.log"
    logger_name = f"dll_backfill.{run_id}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    # Prevent propagation to root (no duplicated console output if root has handlers)
    logger.propagate = False
    # Idempotency: reset handlers on re-init (caller may use same run_id rare)
    logger.handlers.clear()
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def _parse_dll_ts(raw: str) -> tuple[datetime, str]:
    """Tolerant DLL timestamp parser (Q-AMB-02). Probe lines 203-218."""
    s = raw[:23]
    for fmt, sep in (
        ("%d/%m/%Y %H:%M:%S.%f", "."),
        ("%d/%m/%Y %H:%M:%S:%f", ":"),
    ):
        try:
            return datetime.strptime(s, fmt), sep
        except ValueError:
            continue
    raise ValueError(f"DLL ts unrecognized: {raw!r}")


def _decode_aggressor(trade_type: int) -> str:
    """Decode tradeType per canonical quirks. Probe lines 221-227."""
    if trade_type == 2:
        return "BUY"
    if trade_type == 3:
        return "SELL"
    return "NONE"


def _classify_outcome(
    total_trades: int,
    schema_pass: bool,
    reached_100: bool,
    watchdog_idle: bool,
    timeout_hit: bool,
    error: str | None,
) -> tuple[str, str, str]:
    """Returns (outcome, decision_tree_branch, rationale). Probe lines 230-267."""
    if error is not None:
        return ("error", "out_of_R4", f"uncaught error: {error}")
    if total_trades == 0:
        return (
            "retention_exhausted",
            "R4(c)",
            "0 trades received — pre-2024 retention floor confirmed",
        )
    if (
        total_trades >= 1_000_000
        and schema_pass
        and reached_100
        and not watchdog_idle
        and not timeout_hit
    ):
        return (
            "full_month_works",
            "R4(a)",
            f"{total_trades:,} trades + schema OK + reached 100 + no watchdog",
        )
    return (
        "partial_coverage",
        "R4(b)",
        (
            f"trades={total_trades:,} schema_pass={schema_pass} "
            f"reached_100={reached_100} watchdog_idle={watchdog_idle} "
            f"timeout_hit={timeout_hit}"
        ),
    )


def _validate_first_1000(
    batch: list[dict],
    window_start: datetime | None = None,
    window_end: datetime | None = None,
) -> dict[str, bool]:
    """Schema + sanity checks (probe lines 270-324, window-aware)."""
    if window_start is None:
        window_start = datetime(2023, 12, 1, 0, 0)
    if window_end is None:
        window_end = datetime(2023, 12, 20, 23, 59, 59)

    checks: dict[str, bool] = {}

    checks["dtype_timestamp"] = all(
        isinstance(t["timestamp"], datetime) and t["timestamp"].tzinfo is None
        for t in batch
    )
    checks["dtype_price_double"] = all(isinstance(t["price"], float) for t in batch)
    checks["dtype_qty_int"] = all(isinstance(t["qty"], int) for t in batch)
    checks["dtype_aggressor_str"] = all(
        t["aggressor"] in ("BUY", "SELL", "NONE") for t in batch
    )
    checks["sanity_price_positive"] = all(t["price"] > 0 for t in batch)
    checks["sanity_qty_positive"] = all(t["qty"] > 0 for t in batch)
    checks["sanity_ticker_normalized"] = all(
        t["ticker"] in ("WDO", "WDOFUT") for t in batch
    )

    n_directional = sum(1 for t in batch if t["aggressor"] in ("BUY", "SELL"))
    checks["sanity_aggressor_distribution"] = n_directional >= 0.25 * len(batch)

    ts_list = [t["timestamp"] for t in batch]
    checks["sanity_ts_monotonic_nondec"] = all(
        ts_list[i] <= ts_list[i + 1] for i in range(len(ts_list) - 1)
    )

    checks["sanity_in_window"] = all(
        window_start <= t["timestamp"] <= window_end for t in batch
    )

    checks["pass_overall"] = all(checks.values())
    return checks


# --- Build callbacks ------------------------------------------------------


def _build_callbacks(
    state: ProbeState,
    trade_q: "queue.Queue[tuple]",
    login_event: threading.Event,
    progress_done_event: threading.Event,
    logger: logging.Logger,  # noqa: ARG001 — kept for parity with probe signature
) -> tuple[Any, Any, Any]:
    """Builds state / progress / history_trade callbacks.

    Probe lines 327-415, identical semantics. Returns the WINFUNCTYPE-wrapped
    instances. They MUST be retained in the module-global ``_CB_REFS`` (Q08-E)
    by the caller before init.
    """

    @StateCB
    def on_state(conn_type: int, result: int) -> None:  # noqa: D401
        state.last_conn_type = int(conn_type)
        state.last_result = int(result)
        if result == 2 and conn_type in (1, 2):
            if state.login_ready_condition_observed is None:
                state.login_ready_condition_observed = (
                    f"result==2 and conn_type=={conn_type}"
                )
            login_event.set()
        if result == 4 and conn_type == 2:
            if state.login_ready_condition_observed is None:
                state.login_ready_condition_observed = "result==4 and conn_type==2"
            login_event.set()

    @ProgressCB
    def on_progress(asset_id: TAssetIDRec, progress: int) -> None:  # noqa: ARG001
        now = time.time()
        state.last_callback_ts = now
        delta_s = (now - state.last_progress_ts) if state.last_progress_ts else 0.0
        state.last_progress = int(progress)
        state.last_progress_ts = now
        try:
            state.progress_timeline.append({
                "ts_unix": now,
                "ts_brt": datetime.fromtimestamp(now).isoformat(),
                "progress": int(progress),
                "delta_s": round(delta_s, 3),
            })
        except Exception:
            pass  # NEVER raise from a callback
        if int(progress) == 99 and state.progress_99_started_ts is None:
            state.progress_99_started_ts = now
        if int(progress) == 100:
            if state.progress_99_started_ts is not None:
                state.progress_99_dwell_s = now - state.progress_99_started_ts
            state.progress_reached_100 = True
            progress_done_event.set()

    @HistoryTradeCB
    def on_history_trade(
        asset: TAssetIDRec,
        date_raw: c_wchar_p,
        trade_num: int,
        price: float,
        vol: float,
        qty: int,
        buy_agent: int,
        sell_agent: int,
        trade_type: int,
    ) -> None:
        state.last_callback_ts = time.time()
        try:
            trade_q.put_nowait((
                str(date_raw) if date_raw is not None else "",
                str(asset.pwcTicker) if asset.pwcTicker is not None else "",
                float(price),
                int(qty),
                int(trade_type),
                int(buy_agent),
                int(sell_agent),
                float(vol),
                int(trade_num),
            ))
        except queue.Full:
            state.queue_full_drops += 1

    return on_state, on_progress, on_history_trade


# --- Persistence (probe single-shot, kept for back-compat) -----------------


def _persist_parquet_single_shot(
    records: list[dict], path: Path, logger: logging.Logger
) -> int:
    """Single-shot parquet writer (probe behaviour, lines 484-553).

    Used when ``run_chunk`` is invoked with ``sink_factory=None`` (probe-equivalent
    mode). For 5d chunks this peaks ~2 GB RAM — use ``IncrementalParquetSink``
    via ``sink_factory`` for production multi-chunk runs.
    """
    if not records:
        logger.warning(
            "No records to persist — writing empty parquet anyway for telemetry parity"
        )

    try:
        import pyarrow as pa  # type: ignore[import-untyped]
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
    except ImportError:
        import csv
        import gzip

        csv_path = path.with_suffix(".csv.gz")
        with gzip.open(csv_path, "wt", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(
                fh,
                fieldnames=[
                    "timestamp", "ts_raw", "ticker", "price", "qty",
                    "aggressor", "buy_agent", "sell_agent", "vol_brl",
                    "trade_number",
                ],
            )
            writer.writeheader()
            for rec in records:
                writer.writerow({
                    **rec,
                    "timestamp": rec["timestamp"].isoformat() if rec["timestamp"] else "",
                })
        logger.warning(
            "pyarrow unavailable — wrote %d records to %s", len(records), csv_path
        )
        return len(records)

    if not records:
        schema = pa.schema([
            ("timestamp", pa.timestamp("ns")),
            ("ts_raw", pa.string()),
            ("ticker", pa.string()),
            ("price", pa.float64()),
            ("qty", pa.int64()),
            ("aggressor", pa.string()),
            ("buy_agent", pa.int64()),
            ("sell_agent", pa.int64()),
            ("vol_brl", pa.float64()),
            ("trade_number", pa.int64()),
        ])
        empty = pa.table({n: [] for n in schema.names}, schema=schema)
        pq.write_table(empty, path)
        return 0

    table = pa.table({
        "timestamp": [r["timestamp"] for r in records],
        "ts_raw": [r["ts_raw"] for r in records],
        "ticker": [r["ticker"] for r in records],
        "price": [r["price"] for r in records],
        "qty": [r["qty"] for r in records],
        "aggressor": [r["aggressor"] for r in records],
        "buy_agent": [r["buy_agent"] for r in records],
        "sell_agent": [r["sell_agent"] for r in records],
        "vol_brl": [r["vol_brl"] for r in records],
        "trade_number": [r["trade_number"] for r in records],
    })
    pq.write_table(table, path, compression="snappy")
    return len(records)


def _persist_progress_timeline(
    timeline: list[dict], path: Path, logger: logging.Logger  # noqa: ARG001
) -> None:
    """Probe lines 556-569."""
    import csv as _csv

    with path.open("w", encoding="utf-8", newline="") as fh:
        if not timeline:
            fh.write("ts_unix,ts_brt,progress,delta_s\n")
            return
        writer = _csv.DictWriter(
            fh, fieldnames=["ts_unix", "ts_brt", "progress", "delta_s"]
        )
        writer.writeheader()
        writer.writerows(timeline)


def _persist_telemetry(payload: dict, path: Path) -> None:
    """Probe lines 572-574."""
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, default=str, ensure_ascii=False)


def _persist_telemetry_snapshot(
    run_id: str,
    telemetry_path: Path,
    status: str,
    total_records: int,
    persisted_rows: int,
    logger: logging.Logger,
) -> None:
    """Pre-finalize JSON snapshot (probe lines 577-600).

    Defense-in-depth: guarantees a telemetry record exists even if DLLFinalize
    crashes (Q-FIN-12-E). Final ``_persist_telemetry`` overwrites this with the
    full payload on successful exit.
    """
    snapshot = {
        "probe_run_id": run_id,
        "probe_spec_version": _PROBE_SPEC_VERSION,
        "status": status,
        "total_records": total_records,
        "persisted_rows": persisted_rows,
        "snapshot_ts_brt": datetime.now().isoformat(),
    }
    with telemetry_path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, default=str, ensure_ascii=False)
    logger.info(
        "Pre-finalize snapshot written (status=%s, rows=%d)", status, persisted_rows
    )


# --- DLL load / configure / shutdown ---------------------------------------


def _load_dll(dll_path: str, logger: logging.Logger) -> Any:
    """Probe lines 606-611."""
    if not Path(dll_path).exists():
        raise FileNotFoundError(f"DLL not found: {dll_path}")
    logger.info("Loading DLL: %s", dll_path)
    dll = ctypes.WinDLL(dll_path)  # WinDLL → stdcall on Windows
    return dll


def _configure_argtypes(dll: Any) -> None:
    """Probe lines 614-628. Configures GetHistoryTrades signature.

    DLLInitializeMarketLogin argtypes are configured INSIDE ``run_chunk``
    because they reference the no-op shim closures built per-call.
    """
    dll.GetHistoryTrades.argtypes = [
        c_wchar_p,  # ticker
        c_wchar_p,  # bolsa
        c_wchar_p,  # dtDateStart
        c_wchar_p,  # dtDateEnd
    ]
    dll.GetHistoryTrades.restype = c_int


def _shutdown_dll(dll: Any, state: ProbeState, logger: logging.Logger) -> None:
    """Tolerant DLL shutdown with quiet-period quiesce. Q-FIN-12-E. Probe lines 631-674."""
    QUIET_PERIOD_S = 2.0
    MAX_QUIESCE_S = 30.0
    deadline = time.time() + MAX_QUIESCE_S
    while time.time() < deadline:
        if state.last_callback_ts > 0:
            idle = time.time() - state.last_callback_ts
            if idle >= QUIET_PERIOD_S:
                logger.info(
                    "DLL quiesced (idle=%.2fs since last cb) — calling DLLFinalize",
                    idle,
                )
                break
        time.sleep(0.25)
    else:
        logger.warning(
            "DLL did not quiesce within %.0fs — calling DLLFinalize anyway",
            MAX_QUIESCE_S,
        )

    try:
        dll.DLLFinalize()
        logger.info("dll.DLLFinalize() succeeded")
    except AttributeError:
        try:
            dll.Finalize()
            logger.info("dll.Finalize() succeeded (DLLFinalize unavailable)")
        except AttributeError:
            logger.warning(
                "Neither DLLFinalize nor Finalize available — skipping shutdown"
            )
    except Exception as e:
        logger.warning("DLL shutdown raised: %s — continuing", e)


# --- IncrementalParquetSink (Phase 2A primitive) ---------------------------


class IncrementalParquetSink:
    """Streaming parquet writer with JSONL sidecar for crash-of-last-resort recovery.

    DEPRECATED for bulk historical backfill — squad audit 2026-05-02 (Nelo + Beckett)
    identified throughput regression 8.5k → 2.5k trd/s due to json.dumps
    per-record overhead, leading to trade_q overflow and silent data loss
    (violates "all data captured" user mandate).

    Use single-shot mode (sink_factory=None) for bulk backfill instead.
    Phase-1 fix (persist-before-shutdown_dll + Q-FIN-12-E quiesce) provides
    sufficient durability without sink streaming.

    Sink class retained for future use cases:
      - Live/streaming pipeline (low callback rate, RPO critical)
      - Window > 5M trades where peak RAM > 1GB becomes a problem

    For those, the perf fix path is:
      1. Replace json.dumps with orjson (5-10x faster)
      2. Or move _flush to background thread

    Q-FIN-12-E defense-in-depth: even if DLLFinalize/process crashes,
    JSONL sidecar has every record fsync'd-batch-cadence; a recovery tool
    rebuilds the parquet from JSONL.

    Replaces ``_persist_parquet_single_shot`` (~2 GB RAM peak for 5M rows)
    with batched streaming (~50 MB RAM peak).

    Schema (explicit, NOT inferred — replicates probe records dict shape):

        timestamp     : datetime[ns]
        ts_raw        : string
        ticker        : string
        price         : float64
        qty           : int64
        aggressor     : string
        buy_agent     : int64
        sell_agent    : int64
        vol_brl       : float64
        trade_number  : int64

    Lifecycle::

        sink = IncrementalParquetSink(parquet_path, jsonl_path, logger)
        for rec in records: sink.append(rec)   # ~50k buffer flush + JSONL line
        n = sink.close()                        # final flush, fsync, atomic replace

    NOT a context manager — sink is stateful and the caller controls quiesce
    ordering relative to ``_shutdown_dll``.
    """

    BATCH_SIZE = 50_000
    FSYNC_EVERY_N_BATCHES = 10

    # Schema declared upfront — matches probe records dict shape (lines 455-466).
    @staticmethod
    def _build_schema():
        import pyarrow as pa  # type: ignore[import-untyped]
        return pa.schema([
            ("timestamp", pa.timestamp("ns")),
            ("ts_raw", pa.string()),
            ("ticker", pa.string()),
            ("price", pa.float64()),
            ("qty", pa.int64()),
            ("aggressor", pa.string()),
            ("buy_agent", pa.int64()),
            ("sell_agent", pa.int64()),
            ("vol_brl", pa.float64()),
            ("trade_number", pa.int64()),
        ])

    def __init__(
        self,
        parquet_path: Path,
        jsonl_path: Path,
        logger: logging.Logger,
    ) -> None:
        # Lazy pyarrow import so the module loads on systems without pyarrow
        # (e.g. spec-only checks); ``IncrementalParquetSink.__init__`` raises
        # an explicit ImportError if pyarrow is missing.
        try:
            import pyarrow as pa  # type: ignore[import-untyped]
            import pyarrow.parquet as pq  # type: ignore[import-untyped]
        except ImportError as e:
            raise ImportError(
                "IncrementalParquetSink requires pyarrow. Install via "
                "`pip install pyarrow`."
            ) from e

        self._pa = pa
        self._pq = pq
        self.parquet_path = parquet_path
        self.jsonl_path = jsonl_path
        self.logger = logger

        # Atomic write: stage at .parquet.tmp, replace on close()
        self._tmp_path = parquet_path.with_suffix(parquet_path.suffix + ".tmp")
        parquet_path.parent.mkdir(parents=True, exist_ok=True)
        jsonl_path.parent.mkdir(parents=True, exist_ok=True)

        self._schema = self._build_schema()
        self._writer = pq.ParquetWriter(
            str(self._tmp_path), self._schema, compression="snappy"
        )

        # JSONL sidecar — line-buffered text, fsync cadence below
        self._jsonl_fh = jsonl_path.open("w", encoding="utf-8")

        self._buffer: list[dict] = []
        self._jsonl_buffer: list[str] = []
        self._batches_written = 0
        self._rows_persisted = 0
        self._closed = False

    def append(self, rec: dict) -> None:
        """Append one trade record. JSON line buffered in-memory; both
        parquet and JSONL flush together every ``BATCH_SIZE`` records
        (single bulk write — eliminates per-record fh.write overhead
        that bottlenecked the consumer thread in v1).
        """
        if self._closed:
            raise RuntimeError("IncrementalParquetSink.append after close()")

        # Buffer JSONL line in memory. Bulk written to disk in _flush()
        # via single fh.write() call. Durability: every 50k records the
        # batch hits disk; fsync every 10 batches (= 500k records).
        ts = rec["timestamp"]
        ts_iso = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
        line = json.dumps({
            "timestamp": ts_iso,
            "ts_raw": rec["ts_raw"],
            "ticker": rec["ticker"],
            "price": rec["price"],
            "qty": rec["qty"],
            "aggressor": rec["aggressor"],
            "buy_agent": rec["buy_agent"],
            "sell_agent": rec["sell_agent"],
            "vol_brl": rec["vol_brl"],
            "trade_number": rec["trade_number"],
        }, ensure_ascii=False)
        self._jsonl_buffer.append(line)

        self._buffer.append(rec)
        if len(self._buffer) >= self.BATCH_SIZE:
            self._flush()

    def _flush(self) -> None:
        """Write current buffer as one parquet row group + bulk-write JSONL
        + maybe fsync."""
        if not self._buffer:
            return
        pa = self._pa
        batch = self._buffer
        table = pa.table({
            "timestamp": [r["timestamp"] for r in batch],
            "ts_raw": [r["ts_raw"] for r in batch],
            "ticker": [r["ticker"] for r in batch],
            "price": [r["price"] for r in batch],
            "qty": [r["qty"] for r in batch],
            "aggressor": [r["aggressor"] for r in batch],
            "buy_agent": [r["buy_agent"] for r in batch],
            "sell_agent": [r["sell_agent"] for r in batch],
            "vol_brl": [r["vol_brl"] for r in batch],
            "trade_number": [r["trade_number"] for r in batch],
        }, schema=self._schema)
        self._writer.write_table(table)

        # Bulk JSONL write — one fh.write call for the whole batch.
        if self._jsonl_buffer:
            self._jsonl_fh.write("\n".join(self._jsonl_buffer) + "\n")
            self._jsonl_buffer.clear()

        self._rows_persisted += len(batch)
        self._batches_written += 1
        self._buffer = []

        # JSONL fsync cadence: every N batches keeps recovery RPO tight
        # without paying fsync per record (which would cost ~5x throughput).
        if self._batches_written % self.FSYNC_EVERY_N_BATCHES == 0:
            try:
                self._jsonl_fh.flush()
                os.fsync(self._jsonl_fh.fileno())
            except OSError as e:
                # Don't bring down the whole chunk for a fsync hiccup; log and continue.
                self.logger.warning("JSONL fsync failed (continuing): %s", e)

    def close(self) -> int:
        """Flush remaining buffer, close writer + JSONL, atomically replace
        the parquet at its final path. Returns persisted_rows.

        Idempotent. Tolerant: writer.close failure does not prevent JSONL
        close, and vice-versa — every cleanup step runs in its own try/except
        so a single failure cannot leak file handles.
        """
        if self._closed:
            return self._rows_persisted
        self._closed = True

        # Final flush of any buffered records
        try:
            self._flush()
        except Exception as e:
            self.logger.error("IncrementalParquetSink final flush failed: %s", e)

        # Close parquet writer (forces row-group footer + flushes to .tmp)
        try:
            self._writer.close()
        except Exception as e:
            self.logger.error("ParquetWriter close failed: %s", e)

        # Atomic replace — only after writer.close() succeeded enough to
        # close the file handle. If .tmp does not exist, skip rename.
        try:
            if self._tmp_path.exists():
                os.replace(self._tmp_path, self.parquet_path)
        except Exception as e:
            self.logger.error(
                "Atomic replace %s -> %s failed: %s",
                self._tmp_path, self.parquet_path, e,
            )

        # JSONL: always fsync + close at end (RPO guarantee)
        try:
            self._jsonl_fh.flush()
            try:
                os.fsync(self._jsonl_fh.fileno())
            except OSError as fe:
                self.logger.warning("JSONL final fsync failed: %s", fe)
            self._jsonl_fh.close()
        except Exception as e:
            self.logger.error("JSONL close failed: %s", e)

        return self._rows_persisted


SinkFactory = Callable[[Path], IncrementalParquetSink]


# --- Engine consumer (sink-aware) ------------------------------------------


def _drain_into_sink(
    trade_q: "queue.Queue[tuple]",
    state: ProbeState,
    sink: IncrementalParquetSink | None,
    records_buf: list[dict],
    schema_check_window: tuple[datetime, datetime],
    schema_checks_state: dict[str, Any],
    logger: logging.Logger,
    poll_timeout: float,
) -> None:
    """Pop one tuple from queue and route to either ``sink`` (streaming) or
    ``records_buf`` (single-shot, probe-equivalent).

    Wrapped so both the active drain loop AND the post-progress residual drain
    use the same code path. ``schema_checks_state`` is a mutable dict carrying
    the boolean ``done`` flag and the resulting checks; it lets first-1000
    validation work uniformly across modes.
    """
    try:
        tup = trade_q.get(timeout=poll_timeout)
    except queue.Empty:
        return

    (
        date_raw, ticker_raw, price, qty, trade_type,
        buy_agent, sell_agent, vol, trade_num,
    ) = tup

    try:
        ts_parsed, sep = _parse_dll_ts(date_raw)
    except ValueError:
        logger.warning("Unparseable DLL ts: %r — skipping record", date_raw)
        return

    if state.ts_separator_observed is None:
        state.ts_separator_observed = sep

    ticker_norm = "WDO" if ticker_raw.upper().startswith("WDO") else ticker_raw

    rec = {
        "timestamp": ts_parsed,
        "ts_raw": date_raw,
        "ticker": ticker_norm,
        "price": float(price),
        "qty": int(qty),
        "aggressor": _decode_aggressor(int(trade_type)),
        "buy_agent": int(buy_agent),
        "sell_agent": int(sell_agent),
        "vol_brl": float(vol),
        "trade_number": int(trade_num),
    }

    if sink is not None:
        # Streaming mode: feed sink immediately. We still keep a SHORT prefix
        # (first 1000) in records_buf for schema validation only.
        sink.append(rec)
        schema_checks_state["total_routed"] = schema_checks_state.get("total_routed", 0) + 1
        if not schema_checks_state["done"] and len(records_buf) < _SCHEMA_VALIDATION_BATCH_SIZE:
            records_buf.append(rec)
    else:
        records_buf.append(rec)

    # Schema validation trigger (uniform across modes)
    if not schema_checks_state["done"] and len(records_buf) >= _SCHEMA_VALIDATION_BATCH_SIZE:
        ws, we = schema_check_window
        schema_checks_state["checks"] = _validate_first_1000(
            records_buf[:_SCHEMA_VALIDATION_BATCH_SIZE],
            window_start=ws,
            window_end=we,
        )
        schema_checks_state["done"] = True
        logger.info(
            "Schema validation (first 1000): pass=%s",
            schema_checks_state["checks"]["pass_overall"],
        )


# --- Main backfill driver: run_chunk ---------------------------------------


def run_chunk(
    start_date: str,
    end_date: str,
    ticker: str,
    dll_path: str,
    activation_key: str,
    user: str,
    password: str,
    output_dir: Path,
    hard_timeout_s: float,
    idle_watchdog_s: float,
    sink_factory: SinkFactory | None = None,
) -> dict:
    """Execute one chunk of the backfill.

    Returns a result dict::

        {
            "exit_code": int (0=full, 1=partial, 2=retention_exhausted, 3=error),
            "outcome": str,
            "outcome_branch": str,
            "outcome_rationale": str,
            "run_id": str,
            "parquet_path": Path,
            "jsonl_path": Path | None,
            "telemetry_path": Path,
            "timeline_path": Path,
            "log_path": Path,
            "persisted_rows": int,
            "telemetry": dict,        # full payload (probe-faithful)
        }

    Diff vs ``run_probe``:
      - ``output_dir`` parameter (probe used module-global ``_OUTPUT_DIR``).
      - ``hard_timeout_s`` / ``idle_watchdog_s`` parameters (probe used module
        constants).
      - ``sink_factory`` parameter — when provided, switches to streaming
        sink + JSONL sidecar; when ``None``, falls back to ``run_probe``'s
        single-shot ``_persist_parquet_single_shot``.
      - Returns a dict (run_probe returns int). Caller maps ``exit_code`` for
        process-exit semantics.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex[:12]
    logger = _setup_logging(run_id, output_dir)
    state = ProbeState()
    trade_q: queue.Queue[tuple] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
    login_event = threading.Event()
    progress_done_event = threading.Event()
    stop_event = threading.Event()

    probe_started = time.time()
    probe_started_brt = datetime.fromtimestamp(probe_started)

    log_path = output_dir / f"probe-stdout-stderr-{run_id}.log"
    parquet_path = output_dir / f"wdofut-{start_date}_{end_date}-{run_id}.parquet"
    jsonl_path = parquet_path.with_suffix(".jsonl")
    timeline_path = output_dir / f"progress-timeline-{run_id}.csv"
    telemetry_path = output_dir / f"probe-telemetry-{run_id}.json"

    logger.info("=" * 78)
    logger.info("DLL backfill chunk started — run_id=%s", run_id)
    logger.info("Spec: %s", _PROBE_SPEC_VERSION)
    logger.info("Council: %s", _COUNCIL_RESOLUTION_REF)
    logger.info("Window: %s..%s ticker=%s", start_date, end_date, ticker)
    logger.info("Output dir: %s", output_dir)
    logger.info(
        "Hard timeout=%.1fs / idle watchdog=%.1fs / sink=%s",
        hard_timeout_s, idle_watchdog_s,
        "IncrementalParquetSink" if sink_factory else "single-shot",
    )
    logger.info("=" * 78)

    error_msg: str | None = None
    return_code: int | None = None
    records: list[dict] = []  # in single-shot mode: ALL records; in sink mode: first <=1000 for schema only
    schema_checks: dict[str, bool] | None = None
    watchdog_idle_triggered = False
    watchdog_idle_at_progress: int | None = None
    timeout_hit = False
    dll = None
    sink: IncrementalParquetSink | None = None
    persisted_rows = 0

    try:
        # 1. Load DLL
        dll = _load_dll(dll_path, logger)
        _configure_argtypes(dll)

        # 2. Build callbacks
        on_state, on_progress, on_history_trade = _build_callbacks(
            state, trade_q, login_event, progress_done_event, logger
        )

        # Q08-E: keep references alive
        global _CB_REFS
        _CB_REFS = []
        _CB_REFS.extend([on_state, on_progress, on_history_trade])

        # No-op shims for unused init slots (probe lines 736-790, identical)
        @StateCB
        def noop_state(_a, _b):
            pass

        @HistoryTradeCB
        def noop_trade(_a, _b, _c, _d, _e, _f, _g, _h, _i):
            pass

        NewDailyCB = WINFUNCTYPE(
            None,
            TAssetIDRec, c_wchar_p,
            c_double, c_double, c_double, c_double, c_double,
            c_double, c_double, c_double,
            c_double, c_double,
            c_int, c_int,
            c_int, c_int, c_int, c_int, c_int,
        )

        @NewDailyCB
        def noop_daily(*_a):
            pass

        BookCB = WINFUNCTYPE(
            None,
            TAssetIDRec, c_int, c_int, c_int, c_int, c_int,
            c_double, ctypes.c_void_p, ctypes.c_void_p,
        )

        @BookCB
        def noop_book(*_a):
            pass

        OfferBookCB = WINFUNCTYPE(
            None,
            TAssetIDRec, c_int, c_int, c_int, c_int, c_int, c_int64,
            c_double, c_char, c_char, c_char, c_char, c_char,
            c_wchar_p, ctypes.c_void_p, ctypes.c_void_p,
        )

        @OfferBookCB
        def noop_offer_book(*_a):
            pass

        TinyBookCB = WINFUNCTYPE(None, TAssetIDRec, c_double, c_int, c_int)

        @TinyBookCB
        def noop_tiny_book(*_a):
            pass

        _CB_REFS.extend([
            noop_state, noop_trade, noop_daily, noop_book, noop_offer_book,
            noop_tiny_book,
        ])

        # 3. Configure DLLInitializeMarketLogin signature (probe lines 803-814)
        dll.DLLInitializeMarketLogin.argtypes = [
            c_wchar_p, c_wchar_p, c_wchar_p,
            StateCB,
            HistoryTradeCB,
            NewDailyCB,
            BookCB,
            OfferBookCB,
            HistoryTradeCB,
            ProgressCB,
            TinyBookCB,
        ]
        dll.DLLInitializeMarketLogin.restype = c_int

        # 4. Init DLL — DLLInitializeMarketLogin (probe lines 817-843)
        logger.info("Calling DLLInitializeMarketLogin (market-only mode)...")
        login_started = time.time()
        init_ret = dll.DLLInitializeMarketLogin(
            activation_key, user, password,
            on_state,              # 1 state
            noop_trade,            # 2 newTrade live (unused here)
            noop_daily,            # 3 newDaily
            noop_book,             # 4 priceBook
            noop_offer_book,       # 5 offerBook
            on_history_trade,      # 6 historyTrade
            on_progress,           # 7 progress
            noop_tiny_book,        # 8 tinyBook
        )
        if init_ret != 0:
            raise RuntimeError(f"DLLInitializeMarketLogin returned {init_ret}")
        logger.info(
            "DLLInitializeMarketLogin OK; awaiting login event (timeout=%ds)...",
            _LOGIN_WAIT_S,
        )

        if not login_event.wait(timeout=_LOGIN_WAIT_S):
            raise TimeoutError(
                f"Login did not become ready within {_LOGIN_WAIT_S}s "
                f"(last conn_type={state.last_conn_type}, result={state.last_result})"
            )
        state.login_wait_s = time.time() - login_started
        logger.info(
            "Login ready after %.1fs (condition: %s)",
            state.login_wait_s, state.login_ready_condition_observed,
        )

        # 5. Construct sink (if factory provided) — AFTER login confirmed,
        # so we don't open a parquet writer for a doomed chunk.
        if sink_factory is not None:
            sink = sink_factory(parquet_path)
            logger.info(
                "IncrementalParquetSink ready: parquet=%s jsonl=%s",
                parquet_path.name, jsonl_path.name,
            )

        # 6. Dispatch GetHistoryTrades (probe lines 846-864)
        dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_str = dt_start_obj.strftime("%d/%m/%Y") + " 09:00:00"
        end_str = dt_end_obj.strftime("%d/%m/%Y") + " 18:00:00"
        schema_window = (
            dt_start_obj,
            dt_end_obj.replace(hour=23, minute=59, second=59),
        )

        logger.info(
            "Dispatching GetHistoryTrades(ticker=%r, bolsa=%r, start=%r, end=%r)",
            ticker, "F", start_str, end_str,
        )
        dispatch_ts = time.time()
        return_code = dll.GetHistoryTrades(ticker, "F", start_str, end_str)
        logger.info("GetHistoryTrades returned: %d (0=NL_OK)", return_code)

        if return_code != 0:
            logger.warning(
                "Non-zero return; expecting 0 trades / retention_exhausted classification"
            )

        # 7. Watchdog (probe lines 869-892, parameterized timeouts)
        def watchdog_thread():
            nonlocal watchdog_idle_triggered, watchdog_idle_at_progress, timeout_hit
            while not stop_event.is_set() and not progress_done_event.is_set():
                time.sleep(1.0)
                now = time.time()
                if state.last_callback_ts > 0:
                    idle_s = now - state.last_callback_ts
                    if idle_s > idle_watchdog_s and not watchdog_idle_triggered:
                        watchdog_idle_triggered = True
                        watchdog_idle_at_progress = state.last_progress
                        logger.warning(
                            "WATCHDOG IDLE: no callback for %.1fs (progress=%d)",
                            idle_s, state.last_progress,
                        )
                if now - dispatch_ts > hard_timeout_s:
                    timeout_hit = True
                    logger.warning(
                        "HARD TIMEOUT: %.1fs elapsed without progress=100",
                        now - dispatch_ts,
                    )
                    progress_done_event.set()
                    break

        wd = threading.Thread(target=watchdog_thread, daemon=True)
        wd.start()

        # 8. Drain loop (probe lines 901-937)
        schema_state: dict[str, Any] = {"done": False, "checks": None}
        logger.info("Engine consumer draining queue...")
        while not progress_done_event.is_set():
            _drain_into_sink(
                trade_q, state, sink, records, schema_window, schema_state,
                logger, poll_timeout=0.5,
            )

        # 9. Residual drain (probe lines 940-965)
        logger.info("Draining residual queue (size=%d)...", trade_q.qsize())
        drain_deadline = time.time() + 10.0
        while time.time() < drain_deadline:
            before = trade_q.qsize()
            _drain_into_sink(
                trade_q, state, sink, records, schema_window, schema_state,
                logger, poll_timeout=0.1,
            )
            if before == 0 and trade_q.empty():
                break

        stop_event.set()
        schema_checks = schema_state["checks"]

        if sink is not None:
            total_routed = schema_state.get("total_routed", 0)
            logger.info(
                "Engine consumer drained: %d records routed to sink", total_routed
            )
        else:
            logger.info("Engine consumer drained: %d records total", len(records))

        # Schema validation if we never reached 1000 trades
        if schema_checks is None and records:
            ws, we = schema_window
            schema_checks = _validate_first_1000(
                records[: min(len(records), _SCHEMA_VALIDATION_BATCH_SIZE)],
                window_start=ws,
                window_end=we,
            )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error("Chunk error: %s", error_msg)
        logger.error(traceback.format_exc())

    finally:
        # Defense-in-depth (Q-FIN-12-E): persist BEFORE _shutdown_dll.
        # Order: parquet/sink → timeline → telemetry snapshot → shutdown_dll.
        try:
            if sink is not None:
                persisted_rows = sink.close()
            else:
                persisted_rows = _persist_parquet_single_shot(
                    records, parquet_path, logger
                )
        except Exception as persist_err:
            logger.error("Parquet persist failed: %s", persist_err)
            persisted_rows = 0

        try:
            _persist_progress_timeline(state.progress_timeline, timeline_path, logger)
        except Exception as tl_err:
            logger.error("Progress timeline persist failed: %s", tl_err)

        # Determine "total" for snapshot: in sink mode we don't keep all records
        # in memory, so use sink's persisted_rows; in single-shot use len(records).
        total_for_snapshot = persisted_rows if sink is not None else len(records)
        try:
            _persist_telemetry_snapshot(
                run_id=run_id,
                telemetry_path=telemetry_path,
                status="pre_finalize",
                total_records=total_for_snapshot,
                persisted_rows=persisted_rows,
                logger=logger,
            )
        except Exception as snap_err:
            logger.error("Pre-finalize telemetry snapshot failed: %s", snap_err)

        if dll is not None:
            _shutdown_dll(dll, state, logger)
        stop_event.set()

    # 10. Build telemetry payload (probe lines 1020-1115, schema unchanged)
    probe_ended = time.time()
    schema_pass = schema_checks["pass_overall"] if schema_checks else False

    # In sink mode total = persisted_rows; in single-shot total = len(records).
    if sink is not None:
        total_records = persisted_rows
    else:
        total_records = len(records)

    outcome, branch, rationale = _classify_outcome(
        total_trades=total_records,
        schema_pass=schema_pass,
        reached_100=state.progress_reached_100,
        watchdog_idle=watchdog_idle_triggered,
        timeout_hit=timeout_hit,
        error=error_msg,
    )

    # First/last trade timestamps:
    #   single-shot: read from records[0] / records[-1].
    #   sink mode: records only holds first <=1000 — so "first" is exact, but
    #              "last" is approximate. For Phase 2A smoke this is acceptable;
    #              Phase 2B can re-read parquet head/tail if exact bounds matter.
    first_ts_brt = records[0]["timestamp"].isoformat() if records else None
    first_ts_raw = records[0]["ts_raw"] if records else None
    if sink is not None:
        last_ts_brt = None
        last_note = "sink_mode_last_ts_not_buffered"
    else:
        last_ts_brt = records[-1]["timestamp"].isoformat() if records else None
        last_note = None

    telemetry = {
        "probe_run_id": run_id,
        "probe_spec_version": _PROBE_SPEC_VERSION,
        "council_resolution_ref": _COUNCIL_RESOLUTION_REF,
        "start_ts_brt": probe_started_brt.isoformat(),
        "end_ts_brt": datetime.fromtimestamp(probe_ended).isoformat(),
        "wall_clock_duration_s": round(probe_ended - probe_started, 3),
        "request": {
            "function": "GetHistoryTrades",
            "ticker": ticker,
            "exchange": "F",
            "start_str": start_date,
            "end_str": end_date,
            "hard_timeout_s": hard_timeout_s,
            "idle_watchdog_s": idle_watchdog_s,
            "sink_mode": "IncrementalParquetSink" if sink is not None else "single_shot",
        },
        "dll_response": {
            "return_code": return_code,
            "return_code_name": "NL_OK" if return_code == 0 else f"NL_{return_code}",
            "login_ready": login_event.is_set(),
            "login_ready_condition_observed": state.login_ready_condition_observed,
            "login_wait_s": round(state.login_wait_s, 3),
        },
        "trades": {
            "total_received": total_records,
            "first_trade_ts_brt": first_ts_brt,
            "last_trade_ts_brt": last_ts_brt,
            "last_trade_ts_brt_note": last_note,
            "first_trade_ts_raw": first_ts_raw,
            "ts_separator_observed": state.ts_separator_observed,
            "queue_full_drops": state.queue_full_drops,
            "persisted_rows": persisted_rows,
        },
        "progress": {
            "timeline_event_count": len(state.progress_timeline),
            "progress_99_dwell_s": (
                round(state.progress_99_dwell_s, 3)
                if state.progress_99_dwell_s is not None else None
            ),
            "reached_100": state.progress_reached_100,
            "last_progress_seen": state.last_progress,
        },
        "schema_validation": {
            "first_1000_complete": (schema_checks is not None),
            "checks": schema_checks if schema_checks else {},
        },
        "watchdogs": {
            "watchdog_idle_triggered": watchdog_idle_triggered,
            "watchdog_idle_at_progress": watchdog_idle_at_progress,
            "timeout_hit": timeout_hit,
        },
        "anti_patterns_audit": {
            "AP-D-01": (
                "PASS" if outcome != "retention_exhausted" else "FAIL_DETECTED"
            ),
            "AP-D-02": "PASS",
            "AP-D-03": "PASS",
            "AP-D-04": "PASS",
            "AP-D-05": (
                "PASS" if (
                    state.progress_99_dwell_s is None
                    or state.progress_99_dwell_s < 120.0
                ) else "CHECK"
            ),
            "AP-D-06": "CHECK",
            "AP-D-07": "N/A",
            "AP-D-08": "N/A",
            "AP-D-09": "N/A",
            "AP-D-10": "N/A",
            "AP-D-11": "PASS",
            "AP-D-12": "PASS",
            "AP-D-13": "N/A",
        },
        "outcome_classification": outcome,
        "outcome_decision_tree_branch": branch,
        "outcome_rationale": rationale,
        "error": error_msg,
        "artifacts": {
            "parquet": str(parquet_path),
            "jsonl_sidecar": str(jsonl_path) if sink is not None else None,
            "progress_timeline_csv": str(timeline_path),
            "telemetry_json": str(telemetry_path),
            "log": str(log_path),
        },
    }

    _persist_telemetry(telemetry, telemetry_path)
    logger.info("=" * 78)
    logger.info("Outcome: %s (%s)", outcome, branch)
    logger.info("Rationale: %s", rationale)
    logger.info("Total trades: %d", total_records)
    logger.info("Persisted rows: %d", persisted_rows)
    logger.info("Schema pass: %s", schema_pass)
    logger.info("Reached 100%%: %s", state.progress_reached_100)
    logger.info(
        "Watchdog idle: %s; Timeout hit: %s",
        watchdog_idle_triggered, timeout_hit,
    )
    logger.info("Telemetry: %s", telemetry_path)
    logger.info("Parquet: %s (%d rows)", parquet_path, persisted_rows)
    if sink is not None:
        logger.info("JSONL sidecar: %s", jsonl_path)
    logger.info("=" * 78)

    exit_code = {
        "full_month_works": 0,
        "partial_coverage": 1,
        "retention_exhausted": 2,
        "error": 3,
    }[outcome]

    return {
        "exit_code": exit_code,
        "outcome": outcome,
        "outcome_branch": branch,
        "outcome_rationale": rationale,
        "run_id": run_id,
        "parquet_path": parquet_path,
        "jsonl_path": jsonl_path if sink is not None else None,
        "telemetry_path": telemetry_path,
        "timeline_path": timeline_path,
        "log_path": log_path,
        "persisted_rows": persisted_rows,
        "telemetry": telemetry,
    }
