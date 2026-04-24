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

# T002.4 / ADR-4 §14.5.2 B1 — child-side peak telemetry emission constants.
# The structured line is parsed by scripts/run_materialize_with_ceiling.py at
# child exit (ADR-2 telemetry contract extension, non-breaking per AC-I).
TELEMETRY_CHILD_PEAK_TAG = "TELEMETRY_CHILD_PEAK_EXIT"

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
    # MWF-20260422-1 §3.2 — manifest write-mode controls.
    no_manifest: bool
    manifest_path: Path | None  # None => canonical; else scratch
    # ADR-4 §10.3 — data-source dispatch (pre-cache layer, Option B).
    # Defaults preserve backward compat for call-sites that construct Args
    # directly without passing the new fields (e.g. existing unit tests).
    source: str = "sentinel"  # "sentinel" (default) | "cache"
    cache_dir: Path | None = None   # only set when --source=cache
    cache_manifest: Path | None = None  # only set when --source=cache


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
    # MWF-20260422-1 §3.1 — mutually exclusive manifest write-mode flags.
    manifest_group = parser.add_mutually_exclusive_group()
    manifest_group.add_argument(
        "--no-manifest",
        action="store_true",
        help=(
            "Do not append to any manifest. No manifest file is created or mutated. "
            "Use for throwaway/scratch runs (e.g. baseline-run). Mutually exclusive "
            "with --manifest-path."
        ),
    )
    manifest_group.add_argument(
        "--manifest-path",
        dest="manifest_path",
        type=Path,
        default=None,
        help=(
            "Override manifest target to PATH (scratch manifest). PATH MUST NOT "
            "equal the canonical data/manifest.csv — that target requires "
            "VESPERA_MANIFEST_COSIGN. Mutually exclusive with --no-manifest."
        ),
    )
    # ADR-4 §10.3 — pre-cache layer dispatch. Default `sentinel` preserves
    # all existing behavior byte-for-byte (non-breaking change).
    parser.add_argument(
        "--source",
        choices=("sentinel", "cache"),
        default="sentinel",
        help=(
            "Raw-trade data source. 'sentinel' (default): read from the "
            "Sentinel TimescaleDB via psycopg2 (existing behavior). 'cache': "
            "read from the local pre-cache layer at --cache-dir (no DB "
            "connection). See docs/architecture/pre-cache-layer-spec.md."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help=(
            "Cache root (required when --source=cache). Default layout: "
            "data/cache/raw_trades/ticker=<T>/year=<Y>/month=<M>/."
        ),
    )
    parser.add_argument(
        "--cache-manifest",
        type=Path,
        default=None,
        help=(
            "Cache manifest path (required when --source=cache). Default: "
            "data/cache/cache-manifest.csv."
        ),
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
    # MWF-20260422-1 §3.2 — reject --manifest-path that resolves to canonical.
    manifest_path = ns.manifest_path
    if manifest_path is not None:
        try:
            resolved_override = Path(manifest_path).resolve()
        except (OSError, RuntimeError):
            resolved_override = Path(manifest_path)
        if resolved_override == MANIFEST_PATH.resolve():
            parser.error(
                "--manifest-path must not point at the canonical data/manifest.csv; "
                "use the cosign flow instead."
            )
    # ADR-4 §10.3 — validate --source dispatch consistency.
    source = ns.source
    cache_dir = ns.cache_dir
    cache_manifest = ns.cache_manifest
    if source == "cache":
        # Apply cache defaults when the operator did not specify them.
        if cache_dir is None:
            cache_dir = REPO_ROOT / "data" / "cache" / "raw_trades"
        if cache_manifest is None:
            cache_manifest = REPO_ROOT / "data" / "cache" / "cache-manifest.csv"
        # Cache-manifest MUST NOT alias the canonical manifest (defense in
        # depth; Article IV + ADR-4 §7.3).
        try:
            resolved_cm = Path(cache_manifest).resolve()
        except (OSError, RuntimeError):
            resolved_cm = Path(cache_manifest)
        if resolved_cm == MANIFEST_PATH.resolve():
            parser.error(
                "--cache-manifest must not point at the canonical "
                "data/manifest.csv (ADR-4 §7.3)."
            )
    else:  # source == "sentinel"
        if cache_dir is not None or cache_manifest is not None:
            parser.error(
                "--cache-dir/--cache-manifest are only valid with --source=cache."
            )
    return Args(
        start_date=ns.start_date,
        end_date=ns.end_date,
        ticker=ticker,
        output_dir=ns.output_dir,
        dry_run=bool(ns.dry_run),
        no_manifest=bool(ns.no_manifest),
        manifest_path=manifest_path,
        source=source,
        cache_dir=cache_dir,
        cache_manifest=cache_manifest,
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


def _fetch_month_from_cache(
    cache_dir: Path, cache_manifest: Path, ticker: str, mw: "MonthWindow",
):
    """Read one month window from the local pre-cache layer (ADR-4 §6.3).

    Returns a DataFrame with the same 7-column schema as the sentinel
    source (``_build_parquet_schema``), filtered to ``[mw.start, mw.end+1d)``.

    Integrity (sha256) is verified on read against the cache-manifest row.
    """
    import csv as _csv

    import pandas as pd  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    if not cache_manifest.exists():
        raise FileNotFoundError(
            f"cache manifest {cache_manifest} not found; run "
            "scripts/build_raw_trades_cache.py first."
        )

    # Build expected on-disk path.
    expected_path = (
        cache_dir
        / f"ticker={ticker}"
        / f"year={mw.year:04d}"
        / f"month={mw.month:02d}"
        / f"{ticker.lower()}-{mw.label}.parquet"
    )

    # Locate manifest row for this ticker + month. Match on relative path
    # OR resolved absolute path (cache-manifest stores the relative posix).
    expected_rel = Path(
        os.path.relpath(expected_path, REPO_ROOT)
    ).as_posix()

    expected_sha: str | None = None
    with cache_manifest.open("r", encoding="utf-8", newline="") as fh:
        reader = _csv.DictReader(
            ln for ln in fh if not ln.lstrip().startswith("#")
        )
        for raw in reader:
            if raw["path"].strip() == expected_rel and raw["ticker"].strip() == ticker:
                expected_sha = raw["sha256"].strip().lower()
                break
    if expected_sha is None:
        raise FileNotFoundError(
            f"cache-manifest has no row for {expected_rel} (ticker={ticker})"
        )

    # Integrity: sha256(file) must match manifest entry (ADR-4 §7.2).
    actual_sha = _sha256_file(expected_path)
    if actual_sha != expected_sha:
        raise ValueError(
            f"cache sha256 mismatch for {expected_path}: "
            f"manifest={expected_sha} disk={actual_sha}"
        )

    # Read the parquet and filter to the month window (pandas path for
    # symmetry with the DB-fetch sibling — the cache pilot is 1-2 GiB, fits
    # comfortably, and we match schema types immediately below).
    end_exclusive = datetime(mw.end_inclusive.year, mw.end_inclusive.month,
                             mw.end_inclusive.day) + timedelta(days=1)
    start_ts = datetime(mw.start.year, mw.start.month, mw.start.day)

    pf = pq.ParquetFile(expected_path)
    df = pf.read().to_pandas()
    # Filter to window [start, end_exclusive). Ticker already implicit in path.
    mask = (df["timestamp"] >= start_ts) & (df["timestamp"] < end_exclusive)
    df = df.loc[mask].reset_index(drop=True)
    if df.empty:
        return df
    # Strict typing — mirrors _fetch_month_dataframe so downstream code is
    # identical regardless of source.
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if getattr(df["timestamp"].dt, "tz", None) is not None:
        raise RuntimeError("cache parquet timestamp is tz-aware; violates R2")
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


# MWF-20260422-1 §3.3 — env-var names + regexes used by the custodial guard.
_COSIGN_ENV = "VESPERA_MANIFEST_COSIGN"
_EXPECTED_SHA_ENV = "VESPERA_MANIFEST_EXPECTED_SHA256"
_COSIGN_RE = re.compile(r"^MC-\d{8}-\d+$")
_EXPECTED_SHA_RE = re.compile(r"^([0-9a-f]{64}|CREATE)$")

# MWF-20260422-1 §4.2 — scratch-output warning scope (prefix match on resolved abs path).
_SCRATCH_OUTPUT_PREFIXES: tuple[Path, ...] = (
    (REPO_ROOT / "data" / "baseline-run").resolve(),
    (REPO_ROOT / "data" / "_scratch").resolve(),
    (REPO_ROOT / "data" / "scratch").resolve(),
)


def _resolve_manifest_target(args: Args) -> Path | None:
    """Return the manifest path to write to, or ``None`` when suppressed.

    Per MWF-20260422-1 §4 pseudo-code:
    - ``--no-manifest``      -> None (all manifest IO suppressed)
    - ``--manifest-path X``  -> X   (scratch target, no custodial gate)
    - default                -> MANIFEST_PATH (canonical, requires cosign)
    """
    if args.no_manifest:
        return None
    if args.manifest_path is not None:
        return args.manifest_path
    return MANIFEST_PATH


def _guard_canonical_write(target: Path) -> None:
    """Fail-closed gate for writes to the canonical ``data/manifest.csv``.

    Per MWF-20260422-1 Decision 2 (dual cosign + hash pin). Non-canonical
    targets bypass all checks — operators can freely write to scratch paths.
    """
    # MWF-20260422-1 §4 — scratch writes have no gate.
    if target.resolve() != MANIFEST_PATH.resolve():
        return

    # MWF-20260422-1 §4 — env cosign required.
    cosign = os.environ.get(_COSIGN_ENV, "")
    if not _COSIGN_RE.match(cosign):
        raise RuntimeError(
            "Refusing to write to canonical data/manifest.csv without "
            "VESPERA_MANIFEST_COSIGN=MC-YYYYMMDD-N. This write requires "
            "R10 ex-ante sign-off in docs/MANIFEST_CHANGES.md. See "
            "docs/architecture/manifest-write-flag-spec.md."
        )

    # MWF-20260422-1 §4 — hash-pin required.
    expected = os.environ.get(_EXPECTED_SHA_ENV, "")
    if not _EXPECTED_SHA_RE.match(expected):
        raise RuntimeError(
            "Refusing to write to canonical data/manifest.csv without "
            "VESPERA_MANIFEST_EXPECTED_SHA256=<64hex>|CREATE."
        )

    # MWF-20260422-1 §4 — bootstrap branch: file MUST NOT exist when CREATE.
    if expected == "CREATE":
        if MANIFEST_PATH.exists():
            raise RuntimeError(
                "VESPERA_MANIFEST_EXPECTED_SHA256=CREATE but "
                f"{MANIFEST_PATH} already exists. Pass the current sha256 "
                "or delete the file if re-bootstrapping."
            )
        return

    # MWF-20260422-1 §4 — ordinary append: sha256 must match live file.
    actual = _sha256_file(MANIFEST_PATH)
    if actual != expected:
        raise RuntimeError(
            f"Refusing canonical manifest write: expected sha256={expected} "
            f"but current file is sha256={actual}. The manifest has drifted "
            "since the R10 sign-off was recorded; re-run audit and update "
            "VESPERA_MANIFEST_EXPECTED_SHA256."
        )


def _append_manifest(rows: list[dict[str, str]], *, target: Path) -> None:
    """Append rows to ``target`` manifest CSV.

    Per MWF-20260422-1 §4 contract: caller MUST have already resolved
    ``target`` via ``_resolve_manifest_target`` (so ``target`` is never
    ``None`` here) AND passed ``_guard_canonical_write(target)`` for the
    canonical path. This function itself no longer hardcodes ``MANIFEST_PATH``.
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    exists = target.exists()
    with target.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(MANIFEST_COLUMNS), lineterminator="\n",
        )
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MANIFEST_COLUMNS})


def _output_dir_is_scratch(output_dir: Path) -> bool:
    """True iff ``output_dir`` resolves under a known scratch prefix.

    Per MWF-20260422-1 §4.2 — prefix match on resolved absolute path.
    """
    try:
        resolved = output_dir.resolve()
    except (OSError, RuntimeError):
        return False
    for prefix in _SCRATCH_OUTPUT_PREFIXES:
        try:
            resolved.relative_to(prefix)
            return True
        except ValueError:
            continue
    return False


def _emit_launch_banner(args: Args, target: Path | None) -> None:
    """Print the per-mode launch banner to stderr.

    Per MWF-20260422-1 Decision 4, Banner 1.
    """
    if target is None:
        print(
            "[manifest-mode] NO-MANIFEST (--no-manifest active; no manifest "
            "file will be written)",
            file=sys.stderr,
        )
        return
    if target.resolve() != MANIFEST_PATH.resolve():
        print(
            f"[manifest-mode] SCRATCH path={target.resolve()} "
            "(--manifest-path active)",
            file=sys.stderr,
        )
        return
    cosign_val = os.environ.get(_COSIGN_ENV) or "NOT_SET"
    print(
        f"[manifest-mode] CANONICAL path={MANIFEST_PATH} cosign={cosign_val}",
        file=sys.stderr,
    )


def _emit_scratch_output_warning(args: Args, target: Path | None) -> None:
    """Print Decision 3 warning when output-dir is scratch but target is canonical.

    Per MWF-20260422-1 §4.2 — soft warning, does NOT exit.
    """
    if target is None:
        return
    if target.resolve() != MANIFEST_PATH.resolve():
        return
    if not _output_dir_is_scratch(args.output_dir):
        return
    try:
        resolved_out = args.output_dir.resolve()
    except (OSError, RuntimeError):
        resolved_out = args.output_dir
    print(
        f"[warn] --output-dir points to a scratch location ({resolved_out}) "
        f"but the manifest target is the CANONICAL path ({MANIFEST_PATH}). "
        "This will require VESPERA_MANIFEST_COSIGN=MC-... to proceed. If "
        "this is a throwaway run, pass --no-manifest or --manifest-path <scratch>.",
        file=sys.stderr,
    )


def run(args: Args) -> int:
    # 1. Hold-out guard — MUST be before connecting to DB.
    assert_holdout_safe(args.start_date, args.end_date)

    # MWF-20260422-1 §4.1 — resolve target + banners BEFORE any DB work.
    target = _resolve_manifest_target(args)
    # Decision 3 warning first, so operators see it alongside the banner.
    _emit_scratch_output_warning(args, target)
    _emit_launch_banner(args, target)

    months = iter_month_windows(args.start_date, args.end_date)

    # MWF-20260422-1 §6 — --dry-run semantics unchanged; it never writes or
    # connects, so we skip the custodial guard (which would otherwise abort
    # pre-flight dry-runs with canonical target but no cosign set).
    if args.dry_run:
        print(f"[dry-run] ticker={args.ticker} window="
              f"{args.start_date.isoformat()}..{args.end_date.isoformat()} "
              f"months={len(months)}")
        for mw in months:
            out = _month_output_path(args.output_dir, args.ticker, mw)
            print(f"[dry-run]   -> {mw.label} [{mw.start} .. {mw.end_inclusive}] -> {out}")
        return 0

    # Fail-fast custodial guard BEFORE DB connect.
    if target is not None:
        _guard_canonical_write(target)

    # ADR-4 §6.3 dispatch. Default --source=sentinel preserves existing
    # behavior byte-identically; --source=cache skips DB entirely.
    is_cache_source = args.source == "cache"

    if not is_cache_source:
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
    conn = None if is_cache_source else _connect(env)
    try:
        for mw in months:
            out_path = _month_output_path(args.output_dir, args.ticker, mw)
            print(f"[materialize] {mw.label} [{mw.start} .. {mw.end_inclusive}] -> {out_path}")
            if is_cache_source:
                df = _fetch_month_from_cache(
                    args.cache_dir, args.cache_manifest, args.ticker, mw,
                )
            else:
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
            # MWF-20260422-1 §4.1 — per-month manifest dispatch:
            #   - target is None => --no-manifest active, emit suppression banner.
            #   - else           => flush immediately to resolved target.
            if target is None:
                print(
                    f"[manifest-suppressed] month={mw.label} reason=--no-manifest",
                    file=sys.stderr,
                )
            else:
                _append_manifest([month_row], target=target)
                total_flushed += 1
                print(f"[manifest] flushed {mw.label} ({total_flushed} total)")
            print(
                f"[materialize]   rows={len(df)} phase={phase} sha256={digest}"
            )

            # Release the DataFrame before the next month's query.
            del df
            gc.collect()
    finally:
        if conn is not None:
            conn.close()

    # MWF-20260422-1 Decision 4, Banner 3 — end-of-run summary per mode.
    if target is None:
        print(
            "[manifest] run complete; 0 month(s) flushed (--no-manifest active)",
            file=sys.stderr,
        )
    elif target.resolve() != MANIFEST_PATH.resolve():
        print(
            f"[manifest] run complete; {total_flushed} month(s) flushed -> {target}",
            file=sys.stderr,
        )
    else:
        # Canonical path — keep existing stdout semantics (unchanged behavior).
        if total_flushed:
            print(
                f"[manifest] run complete; {total_flushed} month(s) "
                f"flushed -> {MANIFEST_PATH}"
            )
        else:
            print("[manifest] no rows appended (all months empty)")
    return 0


def _collect_child_peak_memory() -> tuple[int | None, int | None, str | None]:
    """Collect this process's peak commit + peak working-set via psutil.

    Returns (peak_pagefile_bytes, peak_wset_bytes, error_message). psutil is
    the primary source; if the psutil field is unavailable (shouldn't happen
    on Windows under the current pin ``psutil>=5.9,<8``, but defensive per
    AC-C), fall back to ``ctypes.windll.psapi.GetProcessMemoryInfo``.

    On any collection error the function returns ``(None, None, "<reason>")``
    so the caller can emit a structured line with null values rather than
    suppressing the event entirely (AC-A: EVERY successful exit emits).
    """
    # Primary: psutil (pinned 7.2.2 — peak_wset + peak_pagefile available on Win).
    try:
        import psutil  # local import keeps the module importable on hosts
                      # without psutil during argparse-only unit tests.
        proc = psutil.Process()
        mem = proc.memory_info()
        peak_pagefile = getattr(mem, "peak_pagefile", None)
        peak_wset = getattr(mem, "peak_wset", None)
        if peak_pagefile is not None and peak_wset is not None:
            return int(peak_pagefile), int(peak_wset), None
    except Exception as exc:  # noqa: BLE001 — defensive fallback
        psutil_error = f"psutil_error:{type(exc).__name__}:{exc}"
    else:
        psutil_error = "psutil_missing_peak_fields"

    # Fallback: ctypes GetProcessMemoryInfo (AC-C). Windows-only; on non-Win
    # hosts the fallback reports the psutil error unchanged.
    if sys.platform != "win32":
        return None, None, psutil_error
    try:
        import ctypes
        from ctypes import wintypes

        class _PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
                ("PrivateUsage", ctypes.c_size_t),
            ]

        counters = _PROCESS_MEMORY_COUNTERS_EX()
        counters.cb = ctypes.sizeof(_PROCESS_MEMORY_COUNTERS_EX)
        # Use psapi.GetProcessMemoryInfo with the current process handle.
        psapi = ctypes.WinDLL("psapi.dll")
        kernel32 = ctypes.WinDLL("kernel32.dll")
        handle = kernel32.GetCurrentProcess()
        rc = psapi.GetProcessMemoryInfo(
            handle, ctypes.byref(counters), counters.cb,
        )
        if not rc:
            err = ctypes.GetLastError()
            return None, None, f"{psutil_error};ctypes_rc=0_err={err}"
        return int(counters.PeakPagefileUsage), int(counters.PeakWorkingSetSize), None
    except Exception as exc:  # noqa: BLE001 — defensive fallback
        return None, None, f"{psutil_error};ctypes_error:{type(exc).__name__}:{exc}"


def _emit_child_peak_telemetry() -> None:
    """Emit the single ``TELEMETRY_CHILD_PEAK_EXIT`` line on stdout.

    Per ADR-4 §14.5.2 B1 + T002.4 AC-A. Line format (space-separated k=v):

        TELEMETRY_CHILD_PEAK_EXIT commit=<int> wset=<int> pid=<int> timestamp_brt=<iso>

    On collection failure the payload carries ``commit=0 wset=0`` plus a
    trailing ``error=<reason>`` field — wrapper treats that as a structured
    miss (not a crash) per AC-K(iii).
    """
    peak_pagefile, peak_wset, err = _collect_child_peak_memory()
    pid = os.getpid()
    ts = datetime.now().isoformat(timespec="seconds")  # BRT-naive (R2).
    if peak_pagefile is None or peak_wset is None:
        line = (
            f"{TELEMETRY_CHILD_PEAK_TAG} commit=0 wset=0 "
            f"pid={pid} timestamp_brt={ts} error={err or 'unknown'}"
        )
    else:
        line = (
            f"{TELEMETRY_CHILD_PEAK_TAG} commit={peak_pagefile} "
            f"wset={peak_wset} pid={pid} timestamp_brt={ts}"
        )
    # Use print (not sys.stderr) so the parent wrapper can parse the line from
    # the captured child-log (wrapper redirects child stdout -> {run_id}.log
    # with stderr merged; either stream would work but stdout matches the ADR-2
    # "structured stdout line" contract in §14.5.2 B1).
    print(line, flush=True)


def main(argv: list[str] | None = None) -> int:
    # T002.4 / ADR-4 §14.5.2 B1 — wrap the existing dispatch so that EVERY
    # exit path (success, HoldoutLockError, generic Exception) emits exactly
    # one TELEMETRY_CHILD_PEAK_EXIT line just before returning (AC-A).
    try:
        try:
            args = parse_args(argv)
            return run(args)
        except HoldoutLockError as exc:
            print(f"HoldoutLockError: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    finally:
        # Emitting in the outer ``finally`` guarantees the line is written
        # regardless of which inner branch ran (AC-A). Swallow any unexpected
        # emission error to avoid masking the real return value (AC-K(iii)
        # fallback semantics — the wrapper treats "missing" as a warning, not
        # a crash).
        try:
            _emit_child_peak_telemetry()
        except Exception as exc:  # noqa: BLE001
            print(
                f"{TELEMETRY_CHILD_PEAK_TAG} commit=0 wset=0 "
                f"pid={os.getpid()} timestamp_brt=unknown "
                f"error=emit_failed:{type(exc).__name__}:{exc}",
                flush=True,
            )


if __name__ == "__main__":
    raise SystemExit(main())
