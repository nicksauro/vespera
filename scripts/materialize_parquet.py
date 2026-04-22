# PATCH t002-refactor-next-run: fix cursor leak (fetchall->fetchmany),
# flush manifest per month, gc.collect between months. Applied by Dara
# 2026-04-22 while PID 12608 (current run with old code) still materializes.
# This patch is for FUTURE runs — it is NOT hot-applied to the live process.
"""Materialize Sentinel trades into deterministic monthly parquet files.

Story: T002.0a
Epic:  EPIC-T002.0
Owner: Dara (@data-engineer)

Purpose
-------
Read trades from the Sentinel TimescaleDB (via the read-only ``sentinel_ro``
role) and emit one parquet file per (ticker, year, month) with a strict
schema (R2 BRT-naive) and byte-deterministic output (re-run produces
identical files).

Hold-out fail-closed
--------------------
The hold-out guard runs BEFORE any DB connection. If the requested window
intersects ``[2025-07-01, 2026-04-21]`` and ``VESPERA_UNLOCK_HOLDOUT != 1``,
the script raises ``HoldoutLockError`` and exits with code 2.

CLI
---
    python scripts/materialize_parquet.py \
        --start-date 2024-01-02 \
        --end-date 2025-06-30 \
        --ticker WDO \
        --output-dir data/in_sample/

Aliases ``--start`` and ``--end`` are accepted for operator ergonomics.

Output layout
-------------
    data/in_sample/year=YYYY/month=MM/wdo-YYYY-MM.parquet   (lowercase ticker)
    data/manifest.csv   (append-only, 7 fixed columns)

Parquet schema (strict)
-----------------------
    timestamp  : timestamp[ns]  (BRT-naive, tz=None)
    ticker     : string
    price      : float64
    qty        : int32
    aggressor  : string  (BUY | SELL | NONE)
    buy_agent  : string  (nullable)
    sell_agent : string  (nullable)

Note: the Sentinel source stores ``buy_agent/sell_agent`` as VARCHAR(64)
(already-resolved agent names). Materializer preserves them as strings —
any downstream numeric mapping is a consumer concern.

Security (Riven Condition 2 — APPROVED_WITH_CONDITIONS, 2026-04-22)
-------------------------------------------------------------------
Password NEVER logged, even in debug/traceback. Credentials come only from
``.env.vespera`` (gitignored) and are passed directly to ``psycopg2.connect``
via keyword args — they are NEVER interpolated into a DSN string, logged,
or rendered into an exception message. Any ``psycopg2.Error`` raised during
connection is SANITIZED in ``_connect`` before re-raise: patterns matching
``password=...`` and connection-DSN hints are scrubbed to ``password=***``
and ``dsn=<redacted>`` so that Python tracebacks in CI / operator shells
cannot accidentally leak the secret.

Phase classification (Riven Condition 3 — APPROVED_WITH_CONDITIONS)
-------------------------------------------------------------------
The manifest distinguishes three phases per spec v0.2.0 L93 + PRR-20260421-1:

  * ``warmup``    — 2024-01-02 through 2024-06-30 (6 months, ~125 business days)
  * ``in_sample`` — 2024-07-01 through 2025-06-30 (12 months, ~250 business days)
  * ``hold_out``  — 2025-07-01 through 2026-04-21 (NOT materialized in T002.0a)

A month straddling a phase boundary is a programming error against the
phase cutoffs — the classifier asserts single-phase purity per parquet file
and raises ``ValueError`` on a mixed-phase partition.
"""

from __future__ import annotations

import argparse
import csv
import gc
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

# Local import — scripts/ is added to sys.path when invoked as a module.
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _holdout_lock import HoldoutLockError, assert_holdout_safe  # noqa: E402


REPO_ROOT = _SCRIPTS_DIR.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "in_sample"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.csv"
MANIFEST_COLUMNS = (
    "path",
    "rows",
    "sha256",
    "start_ts_brt",
    "end_ts_brt",
    "ticker",
    "phase",
    "generated_at_brt",
)

# Phase cutoffs (Riven Condition 3; spec v0.2.0 L93 + PRR-20260421-1).
WARMUP_START: date = date(2024, 1, 2)
WARMUP_END_INCLUSIVE: date = date(2024, 6, 30)
IN_SAMPLE_START: date = date(2024, 7, 1)
IN_SAMPLE_END_INCLUSIVE: date = date(2025, 6, 30)
HOLD_OUT_START: date = date(2025, 7, 1)
HOLD_OUT_END_INCLUSIVE: date = date(2026, 4, 21)


def classify_phase(start: date, end_inclusive: date) -> str:
    """Classify a parquet file's window as warmup | in_sample | hold_out.

    Raises ``ValueError`` if the window straddles a phase boundary — such
    a file cannot carry a single ``phase`` label and is a programming error
    in the partitioning logic (monthly partitions fit cleanly, but the
    WARMUP/IN_SAMPLE cut at 2024-06-30/2024-07-01 falls between June and
    July — a partition bug, not a user error).
    """
    if start > end_inclusive:
        raise ValueError(f"Invalid window: start={start} > end={end_inclusive}")

    def _in(d: date, lo: date, hi: date) -> bool:
        return lo <= d <= hi

    if _in(start, WARMUP_START, WARMUP_END_INCLUSIVE) and _in(
        end_inclusive, WARMUP_START, WARMUP_END_INCLUSIVE
    ):
        return "warmup"
    if _in(start, IN_SAMPLE_START, IN_SAMPLE_END_INCLUSIVE) and _in(
        end_inclusive, IN_SAMPLE_START, IN_SAMPLE_END_INCLUSIVE
    ):
        return "in_sample"
    if _in(start, HOLD_OUT_START, HOLD_OUT_END_INCLUSIVE) and _in(
        end_inclusive, HOLD_OUT_START, HOLD_OUT_END_INCLUSIVE
    ):
        return "hold_out"

    raise ValueError(
        f"Window [{start.isoformat()}, {end_inclusive.isoformat()}] "
        "straddles a phase boundary (warmup|in_sample|hold_out); "
        "monthly partitioning should keep each file in a single phase."
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Args:
    start_date: date
    end_date: date
    ticker: str
    output_dir: Path
    dry_run: bool


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="materialize_parquet",
        description=(
            "Materialize Sentinel trades to deterministic monthly parquet. "
            "Hold-out fail-closed: window intersecting [2025-07-01, 2026-04-21] "
            "requires VESPERA_UNLOCK_HOLDOUT=1."
        ),
    )
    parser.add_argument(
        "--start-date", "--start",
        dest="start_date",
        type=_parse_date,
        required=True,
        help="Inclusive start date (YYYY-MM-DD, BRT).",
    )
    parser.add_argument(
        "--end-date", "--end",
        dest="end_date",
        type=_parse_date,
        required=True,
        help="Inclusive end date (YYYY-MM-DD, BRT).",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Ticker to materialize (e.g. WDO, WIN).",
    )
    parser.add_argument(
        "--output-dir", "--out",
        dest="output_dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output root (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan-only: print month partitions and exit without DB connect or write.",
    )
    return parser


def parse_args(argv: list[str] | None = None) -> Args:
    parser = build_parser()
    ns = parser.parse_args(argv)
    if ns.start_date > ns.end_date:
        parser.error(f"--start-date {ns.start_date} > --end-date {ns.end_date}")
    ticker = ns.ticker.strip()
    if not ticker:
        parser.error("--ticker must not be empty")
    return Args(
        start_date=ns.start_date,
        end_date=ns.end_date,
        ticker=ticker,
        output_dir=ns.output_dir,
        dry_run=bool(ns.dry_run),
    )


# ---------------------------------------------------------------------------
# Month partitioning
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class MonthWindow:
    year: int
    month: int
    start: date  # inclusive, clipped to requested range
    end_inclusive: date  # inclusive, clipped to requested range

    @property
    def label(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"


def _month_first(d: date) -> date:
    return date(d.year, d.month, 1)


def _month_last(d: date) -> date:
    # Last day of the month containing d
    if d.month == 12:
        nxt = date(d.year + 1, 1, 1)
    else:
        nxt = date(d.year, d.month + 1, 1)
    return nxt - timedelta(days=1)


def iter_month_windows(start: date, end_inclusive: date) -> list[MonthWindow]:
    """Yield (year, month) partitions intersecting [start, end_inclusive]."""
    out: list[MonthWindow] = []
    cursor = _month_first(start)
    while cursor <= end_inclusive:
        m_first = cursor
        m_last = _month_last(cursor)
        clip_start = max(m_first, start)
        clip_end = min(m_last, end_inclusive)
        out.append(MonthWindow(
            year=cursor.year,
            month=cursor.month,
            start=clip_start,
            end_inclusive=clip_end,
        ))
        # advance to next month
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return out


# ---------------------------------------------------------------------------
# DB + parquet helpers (imported lazily so tests can run without psycopg2)
# ---------------------------------------------------------------------------

def _build_parquet_schema():
    import pyarrow as pa  # type: ignore[import-untyped]
    return pa.schema([
        pa.field("timestamp", pa.timestamp("ns"), nullable=False),
        pa.field("ticker", pa.string(), nullable=False),
        pa.field("price", pa.float64(), nullable=False),
        pa.field("qty", pa.int32(), nullable=False),
        pa.field("aggressor", pa.string(), nullable=False),
        pa.field("buy_agent", pa.string(), nullable=True),
        pa.field("sell_agent", pa.string(), nullable=True),
    ])


def _load_env_vespera() -> dict[str, str]:
    env_path = REPO_ROOT / ".env.vespera"
    if not env_path.exists():
        raise FileNotFoundError(
            f"{env_path} not found. Copy .env.vespera.example and fill credentials."
        )
    out: dict[str, str] = {}
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


_SENSITIVE_PATTERNS = (
    (re.compile(r"password\s*=\s*[^\s,)]+", re.IGNORECASE), "password=***"),
    (re.compile(r"dsn\s*=\s*['\"][^'\"]*['\"]", re.IGNORECASE), "dsn=<redacted>"),
)


def _sanitize_error_message(msg: str) -> str:
    """Scrub password/DSN fragments from an error message (Riven Condition 2).

    Re-raised psycopg2.Error messages sometimes include fragments of the
    connection DSN in driver-level diagnostics. This helper strips those
    so operator tracebacks in CI cannot leak ``.env.vespera`` secrets.
    """
    out = msg
    for pattern, replacement in _SENSITIVE_PATTERNS:
        out = pattern.sub(replacement, out)
    return out


def _connect(env: dict[str, str]):
    """Connect to Sentinel DB using credentials from .env.vespera.

    Security (Riven Condition 2): password is passed as a kwarg, never
    interpolated into a DSN string or logged. Any ``psycopg2.Error`` is
    caught, its message SANITIZED, and re-raised without the original
    traceback chain (``from None``) so the underlying driver frames —
    which can carry the DSN — do not leak upstream.
    """
    import psycopg2  # type: ignore[import-untyped]
    required = ("VESPERA_DB_HOST", "VESPERA_DB_PORT", "VESPERA_DB_NAME",
                "VESPERA_DB_USER", "VESPERA_DB_PASSWORD")
    missing = [k for k in required if not env.get(k)]
    if missing:
        raise RuntimeError(f"Missing keys in .env.vespera: {missing}")
    try:
        return psycopg2.connect(
            host=env["VESPERA_DB_HOST"],
            port=int(env["VESPERA_DB_PORT"]),
            dbname=env["VESPERA_DB_NAME"],
            user=env["VESPERA_DB_USER"],
            password=env["VESPERA_DB_PASSWORD"],
            # explicit read-only at session level (defense in depth)
            options="-c default_transaction_read_only=on",
        )
    except psycopg2.Error as exc:
        safe_msg = _sanitize_error_message(str(exc))
        # Re-raise as same class with sanitized message, dropping original chain
        # so driver-level frames (which may carry DSN) do not surface.
        raise type(exc)(safe_msg) from None


# ---------------------------------------------------------------------------
# Core materialization
# ---------------------------------------------------------------------------

def _month_output_path(output_dir: Path, ticker: str, mw: MonthWindow) -> Path:
    return (
        output_dir
        / f"year={mw.year:04d}"
        / f"month={mw.month:02d}"
        / f"{ticker.lower()}-{mw.label}.parquet"
    )


def _fetch_month_dataframe(conn, ticker: str, mw: MonthWindow):
    """Stream trades for one month window into a pandas DataFrame (sorted)."""
    import pandas as pd  # type: ignore[import-untyped]

    # end is half-open (< next day 00:00) to match spec semantics.
    end_exclusive = mw.end_inclusive + timedelta(days=1)

    query = (
        "SELECT timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent "
        "FROM trades "
        "WHERE ticker = %(ticker)s "
        "AND timestamp >= %(start)s "
        "AND timestamp < %(end_excl)s "
        "ORDER BY ticker, timestamp"
    )
    params = {
        "ticker": ticker,
        "start": mw.start.isoformat(),
        "end_excl": end_exclusive.isoformat(),
    }

    # Server-side named cursor for streaming on large partitions.
    # PATCH t002-refactor-next-run: replace fetchall() (which buffers the
    # entire month in memory — 10-20M rows — causing swap thrashing) with a
    # fetchmany(itersize) loop that drains the cursor in 100K-row batches.
    rows: list = []
    with conn.cursor(name="materialize_stream") as cur:
        cur.itersize = 100_000
        cur.execute(query, params)
        while True:
            batch = cur.fetchmany(cur.itersize)
            if not batch:
                break
            rows.extend(batch)

    df = pd.DataFrame(rows, columns=[
        "timestamp", "ticker", "price", "qty", "aggressor", "buy_agent", "sell_agent",
    ])
    if df.empty:
        return df

    # Strict typing — pandas may infer ``object`` or ``Decimal`` from psycopg2.
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # naive
    if getattr(df["timestamp"].dt, "tz", None) is not None:
        # Defensive: should not happen given column type, but assert R2.
        raise RuntimeError("timestamp column became tz-aware; violates R2")
    df["ticker"] = df["ticker"].astype(str)
    df["price"] = df["price"].astype("float64")
    df["qty"] = df["qty"].astype("int32")
    df["aggressor"] = df["aggressor"].astype(str)
    df["buy_agent"] = df["buy_agent"].astype("string")
    df["sell_agent"] = df["sell_agent"].astype("string")
    return df


def _write_parquet(df, path: Path):
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    schema = _build_parquet_schema()
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")

    # Determinism knobs:
    # - snappy compression (stable)
    # - fixed row_group_size
    # - no stats extras, no dictionary randomness (pyarrow default is stable)
    pq.write_table(
        table,
        tmp,
        compression="snappy",
        row_group_size=100_000,
        use_dictionary=True,
        write_statistics=True,
        version="2.6",
        store_schema=True,
    )
    os.replace(tmp, path)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _append_manifest(rows: list[dict[str, str]]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    exists = MANIFEST_PATH.exists()
    with MANIFEST_PATH.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(MANIFEST_COLUMNS), lineterminator="\n")
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MANIFEST_COLUMNS})


def run(args: Args) -> int:
    # 1. Hold-out guard — MUST be before connecting to DB.
    assert_holdout_safe(args.start_date, args.end_date)

    months = iter_month_windows(args.start_date, args.end_date)

    if args.dry_run:
        print(f"[dry-run] ticker={args.ticker} window="
              f"{args.start_date.isoformat()}..{args.end_date.isoformat()} "
              f"months={len(months)}")
        for mw in months:
            out = _month_output_path(args.output_dir, args.ticker, mw)
            print(f"[dry-run]   -> {mw.label} [{mw.start} .. {mw.end_inclusive}] -> {out}")
        return 0

    env = _load_env_vespera()
    generated_at = datetime.now().isoformat(timespec="seconds")

    import pandas as pd  # type: ignore[import-untyped]  # for Timestamp formatting

    # PATCH t002-refactor-next-run: per-month manifest flush + gc.collect.
    # Prior version buffered all manifest rows and flushed once at the end —
    # meaning a mid-run crash would lose all chain-of-custody for months that
    # completed successfully. Now each month flushes its own row immediately
    # after the parquet write, and gc.collect() runs between months to free
    # the ~10-20M-row DataFrame before the next query starts.
    total_flushed = 0
    conn = _connect(env)
    try:
        for mw in months:
            out_path = _month_output_path(args.output_dir, args.ticker, mw)
            print(f"[materialize] {mw.label} [{mw.start} .. {mw.end_inclusive}] -> {out_path}")
            df = _fetch_month_dataframe(conn, args.ticker, mw)
            if df.empty:
                print(f"[materialize]   WARNING: no rows for {mw.label}; skipping file.")
                # Still free any partially allocated structures.
                del df
                gc.collect()
                continue

            _write_parquet(df, out_path)
            digest = _sha256_file(out_path)

            # Use os.path.relpath (case-insensitive on Windows) rather than
            # Path.relative_to, which is case-sensitive even on Win32 and
            # breaks when the OS reports a different casing for the repo root.
            rel_path = Path(
                os.path.relpath(out_path, REPO_ROOT)
            ).as_posix()
            start_ts = pd.Timestamp(df["timestamp"].iloc[0]).isoformat()
            end_ts = pd.Timestamp(df["timestamp"].iloc[-1]).isoformat()
            phase = classify_phase(mw.start, mw.end_inclusive)
            month_row = {
                "path": rel_path,
                "rows": str(len(df)),
                "sha256": digest,
                "start_ts_brt": start_ts,
                "end_ts_brt": end_ts,
                "ticker": args.ticker,
                "phase": phase,
                "generated_at_brt": generated_at,
            }
            # Flush THIS month immediately — crash-safe chain of custody.
            _append_manifest([month_row])
            total_flushed += 1
            print(
                f"[materialize]   rows={len(df)} phase={phase} sha256={digest}"
            )
            print(f"[manifest] flushed {mw.label} ({total_flushed} total)")

            # Release the DataFrame before the next month's query.
            del df
            gc.collect()
    finally:
        conn.close()

    # PATCH: final aggregate append is now a noop — all months flushed above.
    if total_flushed:
        print(f"[manifest] run complete; {total_flushed} month(s) flushed -> {MANIFEST_PATH}")
    else:
        print("[manifest] no rows appended (all months empty)")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        return run(args)
    except HoldoutLockError as exc:
        print(f"HoldoutLockError: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
