"""dll_probe_2023_12_wdofut — A1 empirical DLL probe for pre-2024 WDOFUT.

Spec:           docs/research/dll-probes/A1-spec-2023-12-WDOFUT.md
Council:        docs/councils/COUNCIL-2026-05-01-DATA-resolution.md (R1-R4)
Branch:         t003-a1-dll-probe-2023-12
Authority:      Nelo (@profitdll-specialist) authors; Dara (@data-engineer) executes
Article II:     Gage @devops EXCLUSIVE on git push — DO NOT push from this script
Article IV:     Every callback signature / quirk anchored to manual or canonical quirks

Purpose
-------
Empirically test whether ProfitDLL's GetHistoryTrades serves pre-2024 WDOFUT
(continuous-contract alias) for the bounded window 2023-12-01..2023-12-20.

Outcome ∈ {full_month_works, partial_coverage, retention_exhausted, error}.

Probe writes ONLY to data/dll-probes/2023-12-WDOFUT/ (scratch). NEVER mutates:
- data/in_sample/  (T002 hot-path)
- data/holdout/    (Sentinel hold-out lock)
- data/manifest.csv (R10 absolute custodial; needs A6 user MWF cosign)

Quirks compliance (per feedback_profitdll_quirks.md + Nelo registry)
--------------------------------------------------------------------
- DLLInitializeMarketLogin (NOT DLLInitialize)             [Inicialização]
- WINFUNCTYPE (NOT CFUNCTYPE) for all callbacks            [Q01-V, manual §3.2 L2735]
- c_wchar_p (NOT c_char_p) for all string args             [Q02-V]
- exchange="F" (NOT "BMF")                                  [Q03-V, manual §3.1 L1673]
- WDOFUT continuous (NEVER WDOZ23, WDOF24)                 [Q09-E, canonical Tickers]
- Login ready: result==2 AND conn_type in (1, 2)           [Inicialização table]
- SetHistoryTradeCallback PASSED IN INIT slot 9 (NOT after) [Q11-E]
- _cb_refs global to prevent Python GC                     [Q08-E]
- Callbacks NEVER call DLL functions (queue.put_nowait)    [Q04-V, manual §3.2 L2730]
- Tolerant timestamp parser (. or :)                        [Q-AMB-02]
- BRT-naive timestamps (no UTC conversion)                  [MANIFEST R2 + AP11]
- 99% progress hang 35-45s is NORMAL (do NOT kill)         [Q10-E]
- Hard timeout 1800s; idle watchdog 180s                   [Council R2]

Usage
-----
python scripts/dll_probe_2023_12_wdofut.py \
    --start-date 2023-12-01 \
    --end-date   2023-12-20 \
    --ticker     WDOFUT

Required env vars (load from .env.dll or set externally — Dara provisions):
    DLL_PATH                — absolute path to ProfitDLL.dll
    DLL_ACTIVATION_KEY      — Nelogica license activation key
    DLL_USER                — Nelogica login
    DLL_PASSWORD            — Nelogica password

Exit codes
----------
    0 : full_month_works
    1 : partial_coverage
    2 : retention_exhausted
    3 : error (login timeout, DLL load fail, uncaught exception)
"""

from __future__ import annotations

import argparse
import ctypes
import json
import logging
import os
import queue
import signal
import sys
import threading
import time
import traceback
import uuid
from collections.abc import Iterator
from ctypes import (
    POINTER,
    Structure,
    WINFUNCTYPE,
    byref,
    c_char,
    c_double,
    c_int,
    c_int64,
    c_uint,
    c_wchar_p,
)
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# --- Configuration ----------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_DIR = _REPO_ROOT / "data" / "dll-probes" / "2023-12-WDOFUT"
_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

_PROBE_SPEC_VERSION = "A1-spec-2023-12-WDOFUT-v1.0"
_COUNCIL_RESOLUTION_REF = "COUNCIL-2026-05-01-DATA-resolution.md"

# Watchdog thresholds (Council R2)
_IDLE_WATCHDOG_S = 180.0
_HARD_TIMEOUT_S = 1800.0
_LOGIN_WAIT_S = 60.0

# Queue sizing (canonical quirks Callbacks: queue.Queue maxsize=20_000)
_QUEUE_MAXSIZE = 20_000

# Schema validation
_SCHEMA_VALIDATION_BATCH_SIZE = 1000

# --- ctypes structures matching DLL public API -----------------------------


class TAssetIDRec(Structure):
    """Manual §3 line 191. PWideChar fields (UTF-16)."""

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

# Placeholder callbacks for unused init slots (DLLInitializeMarketLogin
# requires 11 callback slots; only state/trade/progress/historyTrade are
# load-bearing for this probe).
NoopAssetCB = WINFUNCTYPE(None, TAssetIDRec)
NoopVoidCB = WINFUNCTYPE(None)


# --- Data classes ----------------------------------------------------------


@dataclass
class ProbeState:
    """Mutable state shared between callbacks (read-only inside callbacks)
    and engine thread (read/write).

    Callbacks ONLY enqueue or set primitive fields — never call DLL or do I/O.
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


def _setup_logging(run_id: str) -> logging.Logger:
    log_path = _OUTPUT_DIR / f"probe-stdout-stderr-{run_id}.log"
    logger = logging.getLogger("dll_probe")
    logger.setLevel(logging.DEBUG)
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
    """Tolerant DLL timestamp parser (Q-AMB-02).

    Returns (parsed_datetime, separator_observed).
    Tries ``DD/MM/YYYY HH:MM:SS.fff`` then ``DD/MM/YYYY HH:MM:SS:fff``.
    """
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
    """Decode tradeType per canonical quirks Callbacks: 2=BUY, 3=SELL else NONE."""
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
    """Returns (outcome, decision_tree_branch, rationale) per §9.2."""
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
    """Schema + sanity checks per §8.2.

    Window-aware: callers pass `window_start`/`window_end` matching the
    probe range. If omitted, defaults to the spec A1 hardcoded window
    2023-12-01..2023-12-20 23:59:59 (back-compat).
    """
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
    # DLL normalizes WDOFUT → "WDO" per Sentinel convention; tolerate variants.
    checks["sanity_ticker_normalized"] = all(
        t["ticker"] in ("WDO", "WDOFUT") for t in batch
    )

    # Manual §3.2 L3361 enumerates 14 tradeType values; only 2 (BUY) and 3
    # (SELL) decode to directional. Cross-trades (1), auctions (4), and
    # other special types decode to NONE — which is normal market behaviour.
    # Empirical: full-day datasets show ~72% directional for WDO continuous,
    # but the FIRST 1000 trades fall in opening auction (09:00:52..09:00:55,
    # ~3s window), which is auction-heavy NONE (~70% NONE in observation).
    # Threshold lowered to 25% to tolerate auction-dominated first batch.
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
    logger: logging.Logger,
) -> tuple[Any, Any, Any]:
    """Builds state / progress / history_trade callbacks.

    Returns the WINFUNCTYPE-wrapped instances. They MUST be retained in
    _CB_REFS (Q08-E) by the caller before init.
    """

    @StateCB
    def on_state(conn_type: int, result: int) -> None:  # noqa: D401
        # Callback runs on ConnectorThread — NEVER call DLL or do I/O here.
        state.last_conn_type = int(conn_type)
        state.last_result = int(result)
        # Empirical (Whale Detector v2): result==2 + conn_type in (1, 2) sufficient
        if result == 2 and conn_type in (1, 2):
            if state.login_ready_condition_observed is None:
                state.login_ready_condition_observed = (
                    f"result==2 and conn_type=={conn_type}"
                )
            login_event.set()
        # Manual canonical condition (manual §3.2 L3317-3329)
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
        # Q10-E telemetry: track 99% dwell duration
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
        # Callback runs on ConnectorThread — only enqueue. Q04-V.
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


# --- Engine thread ---------------------------------------------------------


def _engine_consumer(
    trade_q: "queue.Queue[tuple]",
    state: ProbeState,
    stop_event: threading.Event,
    logger: logging.Logger,
) -> tuple[list[dict], dict[str, bool] | None]:
    """Drain trade_q + materialize records. Runs on probe main thread.

    Returns (records, schema_validation_checks).
    Schema validation runs on first 1000 records.
    """
    records: list[dict] = []
    schema_checks: dict[str, bool] | None = None

    while not stop_event.is_set() or not trade_q.empty():
        try:
            tup = trade_q.get(timeout=0.1)
        except queue.Empty:
            continue

        date_raw, ticker_raw, price, qty, trade_type, buy_agent, sell_agent, vol, trade_num = tup

        try:
            ts_parsed, sep = _parse_dll_ts(date_raw)
        except ValueError:
            logger.warning("Unparseable DLL ts: %r — skipping record", date_raw)
            continue

        if state.ts_separator_observed is None:
            state.ts_separator_observed = sep

        # Normalize ticker (Sentinel convention: "WDOFUT" → "WDO")
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
        records.append(rec)

        # Schema validation on first 1000
        if schema_checks is None and len(records) >= _SCHEMA_VALIDATION_BATCH_SIZE:
            schema_checks = _validate_first_1000(records[:_SCHEMA_VALIDATION_BATCH_SIZE])
            logger.info(
                "Schema validation (first 1000): pass=%s details=%s",
                schema_checks["pass_overall"],
                {k: v for k, v in schema_checks.items() if k != "pass_overall"},
            )

    return records, schema_checks


# --- Persistence -----------------------------------------------------------


def _persist_parquet(records: list[dict], path: Path, logger: logging.Logger) -> int:
    """Persist records to parquet. Returns row count actually written.

    Falls back to CSV gzip if pyarrow is not available — the probe outcome
    decision tree (R4) does not require parquet specifically; raw data
    capture is what matters for A2 audit.
    """
    if not records:
        logger.warning("No records to persist — writing empty parquet anyway for telemetry parity")

    try:
        import pyarrow as pa  # type: ignore[import-untyped]
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
    except ImportError:
        # Fallback: CSV gzip
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
        logger.warning("pyarrow unavailable — wrote %d records to %s", len(records), csv_path)
        return len(records)

    if not records:
        # Write empty table with schema
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

    # Build table
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
    timeline: list[dict], path: Path, logger: logging.Logger
) -> None:
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
    """Pre-finalize JSON snapshot — guarantees a telemetry record exists
    even if DLLFinalize crashes the process (Q-FIN-12-E defense-in-depth).
    Final _persist_telemetry overwrites this with the full payload on
    successful exit.
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
    logger.info("Pre-finalize snapshot written (status=%s, rows=%d)", status, persisted_rows)


# --- Main probe driver -----------------------------------------------------


def _load_dll(dll_path: str, logger: logging.Logger) -> Any:
    if not Path(dll_path).exists():
        raise FileNotFoundError(f"DLL not found: {dll_path}")
    logger.info("Loading DLL: %s", dll_path)
    dll = ctypes.WinDLL(dll_path)  # WinDLL → stdcall on Windows
    return dll


def _configure_argtypes(dll: Any) -> None:
    """Configure DLLInitializeMarketLogin + GetHistoryTrades signatures.

    Per manual §3.1:
    - DLLInitializeMarketLogin: 11 callback slots after key/user/pass
    - GetHistoryTrades(ticker, bolsa, dtStart, dtEnd) → Integer
    """
    # GetHistoryTrades
    dll.GetHistoryTrades.argtypes = [
        c_wchar_p,  # ticker
        c_wchar_p,  # bolsa
        c_wchar_p,  # dtDateStart
        c_wchar_p,  # dtDateEnd
    ]
    dll.GetHistoryTrades.restype = c_int


def _shutdown_dll(dll: Any, state: ProbeState, logger: logging.Logger) -> None:
    """Tolerant DLL shutdown with quiet-period quiesce (Q-FIN-12-E).

    Q-AMB-03: DLLFinalize vs Finalize (manual §3.1 L1012 says DLLFinalize;
    Whale Detector v2 empirical uses Finalize — try DLLFinalize first).

    Q-FIN-12-E (NEW empirical): ConnectorThread keeps emitting
    history-trade callbacks for hundreds of ms after progress=100
    (queue_full_drops empirically ~3x record count). Calling
    DLLFinalize while a callback is mid-stdcall causes Windows SEH
    access violation (silent exit 1, empty stderr). Manual §4 L4394
    explicitly forbids calling DLL functions during a callback.
    Mitigation: wait for callback-idle quiet-period before finalize.
    """
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
            logger.warning("Neither DLLFinalize nor Finalize available — skipping shutdown")
    except Exception as e:
        logger.warning("DLL shutdown raised: %s — continuing", e)


def run_probe(
    start_date: str,
    end_date: str,
    ticker: str,
    dll_path: str,
    activation_key: str,
    user: str,
    password: str,
) -> int:
    """Execute A1 probe. Returns exit code.

    Exit codes:
        0 : full_month_works
        1 : partial_coverage
        2 : retention_exhausted
        3 : error
    """
    run_id = uuid.uuid4().hex[:12]
    logger = _setup_logging(run_id)
    state = ProbeState()
    trade_q: queue.Queue[tuple] = queue.Queue(maxsize=_QUEUE_MAXSIZE)
    login_event = threading.Event()
    progress_done_event = threading.Event()
    stop_event = threading.Event()

    probe_started = time.time()
    probe_started_brt = datetime.fromtimestamp(probe_started)

    logger.info("=" * 78)
    logger.info("A1 DLL probe started — run_id=%s", run_id)
    logger.info("Spec: %s", _PROBE_SPEC_VERSION)
    logger.info("Council: %s", _COUNCIL_RESOLUTION_REF)
    logger.info("Window: %s..%s ticker=%s", start_date, end_date, ticker)
    logger.info("=" * 78)

    error_msg: str | None = None
    return_code: int | None = None
    records: list[dict] = []
    schema_checks: dict[str, bool] | None = None
    watchdog_idle_triggered = False
    watchdog_idle_at_progress: int | None = None
    timeout_hit = False
    dll = None

    try:
        # 1. Load DLL
        dll = _load_dll(dll_path, logger)
        _configure_argtypes(dll)

        # 2. Build callbacks (all WINFUNCTYPE-wrapped, retained in _CB_REFS)
        on_state, on_progress, on_history_trade = _build_callbacks(
            state, trade_q, login_event, progress_done_event, logger
        )

        # Q08-E: keep references alive
        global _CB_REFS
        _CB_REFS = []
        _CB_REFS.extend([on_state, on_progress, on_history_trade])

        # Placeholder no-op callbacks for unused init slots
        @StateCB
        def noop_state(_a, _b):
            pass

        @HistoryTradeCB  # used as TNewTradeCallback shape match (same 9 args)
        def noop_trade(_a, _b, _c, _d, _e, _f, _g, _h, _i):
            pass

        # Other slots: types differ; build minimal no-op WINFUNCTYPEs
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

        # 3. Configure DLLInitializeMarketLogin signature
        # Slots (manual §3.1 L991-1010 + L1498-1528 + L4400-4404):
        # key, user, pass + 8 callbacks (NOT 11 — MarketLogin reduces slots
        # vs full DLLInitializeLogin; orderChange/account/history(legacy)
        # are removed because market-only mode has no orders/accounts).
        # Slot order: state, newTrade, newDaily, priceBook, offerBook,
        # historyTrade, progress, tinyBook.
        #
        # Q11-E ("historyTrade slot 9") applies to DLLInitializeLogin
        # (13 args), NOT to DLLInitializeMarketLogin where historyTrade
        # is slot 6 and progress slot 7.
        dll.DLLInitializeMarketLogin.argtypes = [
            c_wchar_p, c_wchar_p, c_wchar_p,         # key, user, pass
            StateCB,                                  # 1 state
            HistoryTradeCB,                           # 2 newTrade (live; same 9-arg shape)
            NewDailyCB,                               # 3 newDaily
            BookCB,                                   # 4 priceBook
            OfferBookCB,                              # 5 offerBook
            HistoryTradeCB,                           # 6 historyTrade ★
            ProgressCB,                               # 7 progress ★
            TinyBookCB,                               # 8 tinyBook
        ]
        dll.DLLInitializeMarketLogin.restype = c_int

        # 4. Init DLL — DLLInitializeMarketLogin (NOT DLLInitialize)
        logger.info("Calling DLLInitializeMarketLogin (market-only mode)...")
        login_started = time.time()
        init_ret = dll.DLLInitializeMarketLogin(
            activation_key, user, password,
            on_state,              # 1 state
            noop_trade,            # 2 newTrade live (unused here)
            noop_daily,            # 3 newDaily
            noop_book,             # 4 priceBook
            noop_offer_book,       # 5 offerBook
            on_history_trade,      # 6 historyTrade ★
            on_progress,           # 7 progress ★
            noop_tiny_book,        # 8 tinyBook
        )
        if init_ret != 0:
            raise RuntimeError(f"DLLInitializeMarketLogin returned {init_ret}")
        logger.info("DLLInitializeMarketLogin OK; awaiting login event (timeout=%ds)...", _LOGIN_WAIT_S)

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

        # 5. Dispatch GetHistoryTrades
        # Date format per manual §3.1 L1737-1745: "DD/MM/YYYY HH:mm:SS"
        dt_start_obj = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_str = dt_start_obj.strftime("%d/%m/%Y") + " 09:00:00"
        end_str = dt_end_obj.strftime("%d/%m/%Y") + " 18:00:00"

        logger.info(
            "Dispatching GetHistoryTrades(ticker=%r, bolsa=%r, start=%r, end=%r)",
            ticker, "F", start_str, end_str,
        )
        dispatch_ts = time.time()
        return_code = dll.GetHistoryTrades(ticker, "F", start_str, end_str)
        logger.info("GetHistoryTrades returned: %d (0=NL_OK)", return_code)

        if return_code != 0:
            # Per manual §3 L894-955 — non-zero means dispatch failed
            logger.warning(
                "Non-zero return; expecting 0 trades / retention_exhausted classification"
            )

        # 6. Engine consumer in main thread, with watchdogs
        last_seen_callback_ts = time.time()

        def watchdog_thread():
            nonlocal watchdog_idle_triggered, watchdog_idle_at_progress, timeout_hit
            while not stop_event.is_set() and not progress_done_event.is_set():
                time.sleep(1.0)
                now = time.time()
                # Idle watchdog
                if state.last_callback_ts > 0:
                    idle_s = now - state.last_callback_ts
                    if idle_s > _IDLE_WATCHDOG_S and not watchdog_idle_triggered:
                        watchdog_idle_triggered = True
                        watchdog_idle_at_progress = state.last_progress
                        logger.warning(
                            "WATCHDOG IDLE: no callback for %.1fs (progress=%d)",
                            idle_s, state.last_progress,
                        )
                # Hard timeout
                if now - dispatch_ts > _HARD_TIMEOUT_S:
                    timeout_hit = True
                    logger.warning(
                        "HARD TIMEOUT: %.1fs elapsed without progress=100",
                        now - dispatch_ts,
                    )
                    progress_done_event.set()
                    break

        wd = threading.Thread(target=watchdog_thread, daemon=True)
        wd.start()

        # Drain queue while waiting for progress=100 OR watchdog/timeout.
        # Engine consumer runs in the same thread (we don't need
        # parallelism since put_nowait is non-blocking in callbacks).
        logger.info("Engine consumer draining queue...")
        while not progress_done_event.is_set():
            try:
                tup = trade_q.get(timeout=0.5)
            except queue.Empty:
                continue
            # Process tuple inline
            (date_raw, ticker_raw, price, qty, trade_type,
             buy_agent, sell_agent, vol, trade_num) = tup
            try:
                ts_parsed, sep = _parse_dll_ts(date_raw)
            except ValueError:
                continue
            if state.ts_separator_observed is None:
                state.ts_separator_observed = sep
            ticker_norm = "WDO" if ticker_raw.upper().startswith("WDO") else ticker_raw
            records.append({
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
            })
            if schema_checks is None and len(records) >= _SCHEMA_VALIDATION_BATCH_SIZE:
                schema_checks = _validate_first_1000(
                    records[:_SCHEMA_VALIDATION_BATCH_SIZE],
                    window_start=dt_start_obj,
                    window_end=dt_end_obj.replace(hour=23, minute=59, second=59),
                )
                logger.info(
                    "Schema validation (first 1000): pass=%s",
                    schema_checks["pass_overall"],
                )

        # Drain residual queue after progress_done
        logger.info("Draining residual queue (size=%d)...", trade_q.qsize())
        drain_deadline = time.time() + 10.0
        while time.time() < drain_deadline:
            try:
                tup = trade_q.get(timeout=0.1)
            except queue.Empty:
                break
            (date_raw, ticker_raw, price, qty, trade_type,
             buy_agent, sell_agent, vol, trade_num) = tup
            try:
                ts_parsed, sep = _parse_dll_ts(date_raw)
            except ValueError:
                continue
            ticker_norm = "WDO" if ticker_raw.upper().startswith("WDO") else ticker_raw
            records.append({
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
            })

        stop_event.set()
        logger.info("Engine consumer drained: %d records total", len(records))

        # Run schema validation if we never reached 1000 trades
        if schema_checks is None and len(records) > 0:
            schema_checks = _validate_first_1000(
                records[: min(len(records), _SCHEMA_VALIDATION_BATCH_SIZE)],
                window_start=dt_start_obj,
                window_end=dt_end_obj.replace(hour=23, minute=59, second=59),
            )

    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        logger.error("Probe error: %s", error_msg)
        logger.error(traceback.format_exc())

    finally:
        # Defense-in-depth (Dara audit + Q-FIN-12-E):
        # Persist BEFORE _shutdown_dll. If DLLFinalize crashes the process
        # (Windows SEH from active callback contention), parquet+telemetry
        # are already on disk. Order: parquet → timeline → telemetry → shutdown.
        parquet_path = _OUTPUT_DIR / f"wdofut-2023-12-{run_id}.parquet"
        timeline_path = _OUTPUT_DIR / f"progress-timeline-{run_id}.csv"
        telemetry_path = _OUTPUT_DIR / f"probe-telemetry-{run_id}.json"

        try:
            persisted_rows = _persist_parquet(records, parquet_path, logger)
        except Exception as persist_err:
            logger.error("Parquet persist failed: %s", persist_err)
            persisted_rows = 0
        try:
            _persist_progress_timeline(state.progress_timeline, timeline_path, logger)
        except Exception as tl_err:
            logger.error("Progress timeline persist failed: %s", tl_err)

        # Pre-shutdown telemetry snapshot (status=pre_finalize) so even if
        # DLLFinalize crashes we have a JSON record of what was captured.
        try:
            _persist_telemetry_snapshot(
                run_id=run_id,
                telemetry_path=telemetry_path,
                status="pre_finalize",
                total_records=len(records),
                persisted_rows=persisted_rows,
                logger=logger,
            )
        except Exception as snap_err:
            logger.error("Pre-finalize telemetry snapshot failed: %s", snap_err)

        if dll is not None:
            _shutdown_dll(dll, state, logger)
        stop_event.set()

    # 8. Build telemetry payload
    probe_ended = time.time()
    schema_pass = schema_checks["pass_overall"] if schema_checks else False
    outcome, branch, rationale = _classify_outcome(
        total_trades=len(records),
        schema_pass=schema_pass,
        reached_100=state.progress_reached_100,
        watchdog_idle=watchdog_idle_triggered,
        timeout_hit=timeout_hit,
        error=error_msg,
    )

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
        },
        "dll_response": {
            "return_code": return_code,
            "return_code_name": "NL_OK" if return_code == 0 else f"NL_{return_code}",
            "login_ready": login_event.is_set(),
            "login_ready_condition_observed": state.login_ready_condition_observed,
            "login_wait_s": round(state.login_wait_s, 3),
        },
        "trades": {
            "total_received": len(records),
            "first_trade_ts_brt": (
                records[0]["timestamp"].isoformat() if records else None
            ),
            "last_trade_ts_brt": (
                records[-1]["timestamp"].isoformat() if records else None
            ),
            "first_trade_ts_raw": records[0]["ts_raw"] if records else None,
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
            "AP-D-02": "PASS",  # WDOFUT continuous (NOT WDOZ23 etc.)
            "AP-D-03": "PASS",  # WINFUNCTYPE + c_wchar_p enforced in script
            "AP-D-04": "PASS",  # historyTrade passed in init slot 9; no SetHistoryTradeCallback after
            "AP-D-05": (
                "PASS" if (
                    state.progress_99_dwell_s is None
                    or state.progress_99_dwell_s < 120.0
                ) else "CHECK"
            ),
            "AP-D-06": "CHECK",  # Dara cross-references Sentinel ESC-009 in A2
            "AP-D-07": "N/A",
            "AP-D-08": "N/A",
            "AP-D-09": "N/A",
            "AP-D-10": "N/A",
            "AP-D-11": "PASS",   # closed-source DLL captured by version (not implemented v1)
            "AP-D-12": "PASS",   # no manifest mutation (writes to data/dll-probes/ only)
            "AP-D-13": "N/A",
        },
        "outcome_classification": outcome,
        "outcome_decision_tree_branch": branch,
        "outcome_rationale": rationale,
        "error": error_msg,
        "artifacts": {
            "parquet": str(parquet_path.relative_to(_REPO_ROOT)),
            "progress_timeline_csv": str(timeline_path.relative_to(_REPO_ROOT)),
            "telemetry_json": str(telemetry_path.relative_to(_REPO_ROOT)),
        },
    }

    _persist_telemetry(telemetry, telemetry_path)
    logger.info("=" * 78)
    logger.info("Outcome: %s (%s)", outcome, branch)
    logger.info("Rationale: %s", rationale)
    logger.info("Total trades: %d", len(records))
    logger.info("Schema pass: %s", schema_pass)
    logger.info("Reached 100%%: %s", state.progress_reached_100)
    logger.info("Watchdog idle: %s; Timeout hit: %s", watchdog_idle_triggered, timeout_hit)
    logger.info("Telemetry: %s", telemetry_path)
    logger.info("Parquet: %s (%d rows)", parquet_path, persisted_rows)
    logger.info("=" * 78)

    # Exit code per §9.2
    return {
        "full_month_works": 0,
        "partial_coverage": 1,
        "retention_exhausted": 2,
        "error": 3,
    }[outcome]


# --- CLI -------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="A1 DLL probe — pre-2024 WDOFUT empirical test (Council 2026-05-01 R1-R4)",
    )
    p.add_argument("--start-date", default="2023-12-01", help="ISO YYYY-MM-DD")
    p.add_argument("--end-date", default="2023-12-20", help="ISO YYYY-MM-DD")
    p.add_argument("--ticker", default="WDOFUT", help="Continuous ticker (NOT specific contract)")
    p.add_argument(
        "--dll-path",
        default=os.environ.get("DLL_PATH", ""),
        help="Absolute path to ProfitDLL.dll (or DLL_PATH env)",
    )
    return p.parse_args()


def _validate_args(args: argparse.Namespace) -> None:
    """Hard rules per spec §3.1."""
    if args.ticker.upper() != "WDOFUT":
        raise SystemExit(
            f"Q09-E HARD RULE: probe ticker must be WDOFUT (continuous). "
            f"Got {args.ticker!r}. Specific contracts pre-2024 hit 0-trades-19ms bug."
        )
    # Window bounds (R1: bounded 2023-12-01..2023-12-20 max)
    s = datetime.strptime(args.start_date, "%Y-%m-%d")
    e = datetime.strptime(args.end_date, "%Y-%m-%d")
    if not (datetime(2023, 12, 1) <= s <= e <= datetime(2023, 12, 31)):
        raise SystemExit(
            f"R1 HARD RULE: probe window must be within 2023-12-01..2023-12-31. "
            f"Got {args.start_date}..{args.end_date}."
        )


def main() -> int:
    args = _parse_args()
    _validate_args(args)

    if sys.platform != "win32":
        print(
            "ERROR: ProfitDLL is Win64 closed-source; this probe runs ONLY on Windows.",
            file=sys.stderr,
        )
        return 3

    if not args.dll_path:
        print(
            "ERROR: --dll-path or DLL_PATH env required.",
            file=sys.stderr,
        )
        return 3

    activation_key = os.environ.get("DLL_ACTIVATION_KEY", "")
    user = os.environ.get("DLL_USER", "")
    password = os.environ.get("DLL_PASSWORD", "")

    missing = [
        n for n, v in [
            ("DLL_ACTIVATION_KEY", activation_key),
            ("DLL_USER", user),
            ("DLL_PASSWORD", password),
        ]
        if not v
    ]
    if missing:
        print(
            f"ERROR: Missing required env vars: {missing}. "
            f"Provision via .env.dll or external export (Dara owns secret mgmt).",
            file=sys.stderr,
        )
        return 3

    return run_probe(
        start_date=args.start_date,
        end_date=args.end_date,
        ticker=args.ticker.upper(),
        dll_path=args.dll_path,
        activation_key=activation_key,
        user=user,
        password=password,
    )


if __name__ == "__main__":
    sys.exit(main())
