"""Build the local raw-trades pre-cache from the Sentinel TimescaleDB (ADR-4).

Story:  T002.0a (pre-cache layer, Option B)
Epic:   EPIC-T002.0
Owner:  Dex (@dev)
Spec:   docs/architecture/pre-cache-layer-spec.md §5, §7, §10

Purpose
-------
Pre-materialize an immutable, sha256-verified local mirror of raw Sentinel
trades at ``data/cache/raw_trades/ticker=<T>/year=<Y>/month=<MM>/`` so that
downstream baseline-run workloads can execute with the Sentinel container
STOPPED (per RA-20260426-1 Option B quiesce). Schema is 1:1 with canonical
``data/in_sample/**`` — no new columns, no renames (Article IV — No Invention).

Hold-out fail-closed
--------------------
The hold-out guard runs BEFORE any DB connection or file I/O. If the
requested window intersects ``[2025-07-01, 2026-04-21]`` and
``VESPERA_UNLOCK_HOLDOUT != 1``, the script raises ``HoldoutLockError``
and exits with code 2 (same contract as ``materialize_parquet.py``).

Canonical paths are STRUCTURALLY untouchable
--------------------------------------------
- ``--cache-dir`` must NOT resolve under ``data/in_sample/``.
- ``--cache-manifest`` must NOT equal canonical ``data/manifest.csv``.
argparse fails-closed on either violation.

Reuses (no reinvention — Article IV, ADR-4 §5.4)
------------------------------------------------
From ``scripts/materialize_parquet.py`` verbatim:
  - ``_parse_date``, ``_month_first``, ``_month_last``, ``iter_month_windows``,
    ``MonthWindow``
  - ``_build_parquet_schema``
  - ``_load_env_vespera``, ``_sanitize_error_message``, ``_connect``
  - ``_fetch_month_dataframe``
  - ``_write_parquet``
  - ``_sha256_file``
  - ``classify_phase``, ``MANIFEST_COLUMNS``

CLI
---
    python scripts/build_raw_trades_cache.py \
        --ticker WDO \
        --start-date 2024-08-01 \
        --end-date 2024-08-31

Exit codes (ADR-4 §10.4)
------------------------
  0 success
  1 generic error (sanitized message)
  2 HoldoutLockError
 11 reserved for hard DB errors (mirrors canonical materializer convention)
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

# ADR-4 §5.4 — reuse helpers verbatim from the canonical materializer.
import materialize_parquet as mp  # noqa: E402
from _holdout_lock import HoldoutLockError, assert_holdout_safe  # noqa: E402

REPO_ROOT = _SCRIPTS_DIR.parent
DEFAULT_CACHE_DIR = REPO_ROOT / "data" / "cache" / "raw_trades"
DEFAULT_CACHE_MANIFEST = REPO_ROOT / "data" / "cache" / "cache-manifest.csv"
_ALLOWED_TICKERS = frozenset({"WDO", "WIN"})


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BuildArgs:
    ticker: str                 # {"WDO", "WIN"}
    start_date: date            # BRT, inclusive
    end_date: date              # BRT, inclusive
    cache_dir: Path             # default: data/cache/raw_trades
    cache_manifest: Path        # default: data/cache/cache-manifest.csv
    resume: bool                # default True
    dry_run: bool               # default False
    force_rebuild: bool         # default False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_raw_trades_cache",
        description=(
            "Build the local pre-cache of raw Sentinel trades (ADR-4 Option B). "
            "Hold-out fail-closed: window intersecting [2025-07-01, 2026-04-21] "
            "requires VESPERA_UNLOCK_HOLDOUT=1."
        ),
    )
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Ticker whitelist: WDO or WIN.",
    )
    parser.add_argument(
        "--start-date", "--start",
        dest="start_date",
        type=mp._parse_date,
        required=True,
        help="Inclusive start date (YYYY-MM-DD, BRT).",
    )
    parser.add_argument(
        "--end-date", "--end",
        dest="end_date",
        type=mp._parse_date,
        required=True,
        help="Inclusive end date (YYYY-MM-DD, BRT).",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help=(
            f"Cache root (default: {DEFAULT_CACHE_DIR}). MUST NOT resolve "
            "under data/in_sample/."
        ),
    )
    parser.add_argument(
        "--cache-manifest",
        type=Path,
        default=DEFAULT_CACHE_MANIFEST,
        help=(
            f"Cache manifest path (default: {DEFAULT_CACHE_MANIFEST}). MUST "
            "NOT equal the canonical data/manifest.csv."
        ),
    )
    # Aliases expected by the dispatch prompt (--output-dir is rejected as
    # cache-dir cannot alias in_sample, but accept it as alias for ergonomics):
    parser.add_argument(
        "--output-dir",
        dest="cache_dir",
        type=Path,
        default=argparse.SUPPRESS,
        help="Alias for --cache-dir.",
    )
    resume_group = parser.add_mutually_exclusive_group()
    resume_group.add_argument(
        "--resume",
        dest="resume",
        action="store_true",
        default=True,
        help="Skip months already in manifest with valid sha256 (default).",
    )
    resume_group.add_argument(
        "--no-resume",
        dest="resume",
        action="store_false",
        help="Disable resume (re-process every month, keeping existing files).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan-only: print partitions and exit without DB connect or write.",
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help=(
            "Wipe target chunks + manifest entries for the window before "
            "re-building."
        ),
    )
    return parser


def _reject_canonical_aliases(
    parser: argparse.ArgumentParser,
    cache_dir: Path,
    cache_manifest: Path,
) -> None:
    """Fail-closed: cache paths MUST NOT alias canonical paths (ADR-4 §5.2).

    ``cache_dir`` cannot resolve under ``data/in_sample/`` and
    ``cache_manifest`` cannot equal canonical ``data/manifest.csv``.
    """
    in_sample = (REPO_ROOT / "data" / "in_sample").resolve()
    try:
        cd_resolved = cache_dir.resolve()
    except (OSError, RuntimeError):
        cd_resolved = Path(cache_dir)
    try:
        cd_resolved.relative_to(in_sample)
        parser.error(
            "--cache-dir must not resolve under data/in_sample/ (ADR-4 §5.2)."
        )
    except ValueError:
        pass  # outside in_sample — OK.

    try:
        cm_resolved = cache_manifest.resolve()
    except (OSError, RuntimeError):
        cm_resolved = Path(cache_manifest)
    if cm_resolved == mp.MANIFEST_PATH.resolve():
        parser.error(
            "--cache-manifest must not equal the canonical data/manifest.csv "
            "(ADR-4 §5.2)."
        )


def parse_args(argv: list[str] | None = None) -> BuildArgs:
    parser = build_parser()
    ns = parser.parse_args(argv)
    ticker = ns.ticker.strip().upper()
    if ticker not in _ALLOWED_TICKERS:
        parser.error(
            f"--ticker must be one of {sorted(_ALLOWED_TICKERS)}; got {ns.ticker!r}"
        )
    if ns.start_date > ns.end_date:
        parser.error(f"--start-date {ns.start_date} > --end-date {ns.end_date}")
    _reject_canonical_aliases(parser, ns.cache_dir, ns.cache_manifest)
    return BuildArgs(
        ticker=ticker,
        start_date=ns.start_date,
        end_date=ns.end_date,
        cache_dir=ns.cache_dir,
        cache_manifest=ns.cache_manifest,
        resume=bool(ns.resume),
        dry_run=bool(ns.dry_run),
        force_rebuild=bool(ns.force_rebuild),
    )


# ---------------------------------------------------------------------------
# Cache layout (ADR-4 §3)
# ---------------------------------------------------------------------------

def _cache_output_path(
    cache_dir: Path, ticker: str, mw: mp.MonthWindow,
) -> Path:
    return (
        cache_dir
        / f"ticker={ticker}"
        / f"year={mw.year:04d}"
        / f"month={mw.month:02d}"
        / f"{ticker.lower()}-{mw.label}.parquet"
    )


def _ckpt_path(out_path: Path) -> Path:
    return out_path.with_suffix(out_path.suffix + ".ckpt")


def _tmp_path(out_path: Path) -> Path:
    return out_path.with_suffix(out_path.suffix + ".tmp")


def _cleanup_partial(out_path: Path) -> None:
    """Unlink ``.tmp`` and ``.ckpt`` sentinels if present (ADR-4 §5.4)."""
    for p in (_tmp_path(out_path), _ckpt_path(out_path)):
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Cache manifest (ADR-4 §7 — mirror of canonical manifest format)
# ---------------------------------------------------------------------------

def _read_cache_manifest(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    """Return ``{(path, ticker): row}`` for resume lookups.

    Empty manifest (missing file) returns an empty dict — the build will
    create the manifest on first flush.
    """
    out: dict[tuple[str, str], dict[str, str]] = {}
    if not path.exists():
        return out
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(
            ln for ln in fh if not ln.lstrip().startswith("#")
        )
        for raw in reader:
            key = (raw["path"].strip(), raw["ticker"].strip())
            out[key] = raw
    return out


def _append_cache_manifest_row(
    path: Path, row: dict[str, str],
) -> None:
    """Atomically append one row to the cache manifest (ADR-4 §5.4)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(mp.MANIFEST_COLUMNS), lineterminator="\n",
        )
        if not exists:
            writer.writeheader()
        writer.writerow({k: row.get(k, "") for k in mp.MANIFEST_COLUMNS})


def _remove_cache_manifest_row(
    path: Path, rel_path: str, ticker: str,
) -> None:
    """Remove any manifest row matching (path, ticker) — used by --force-rebuild.

    Re-writes the manifest atomically via ``.tmp`` + ``os.replace`` so a
    mid-rewrite crash cannot leave a truncated file.
    """
    if not path.exists():
        return
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(
            ln for ln in fh if not ln.lstrip().startswith("#")
        )
        for raw in reader:
            if raw["path"].strip() == rel_path and raw["ticker"].strip() == ticker:
                continue  # drop
            rows.append(raw)

    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(mp.MANIFEST_COLUMNS), lineterminator="\n",
        )
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in mp.MANIFEST_COLUMNS})
    os.replace(tmp, path)


# ---------------------------------------------------------------------------
# Build loop (ADR-4 §5.3)
# ---------------------------------------------------------------------------

def _relpath_posix(path: Path) -> str:
    return Path(os.path.relpath(path, REPO_ROOT)).as_posix()


# ---------------------------------------------------------------------------
# Streaming month -> parquet helper (ADR-4 §13.1 Amendment 20260424-1)
# ---------------------------------------------------------------------------

def _stream_month_to_parquet(
    conn, ticker: str, mw: mp.MonthWindow, out_tmp: Path, schema,
) -> tuple[int, datetime | None, datetime | None]:
    """Stream one month window to ``out_tmp`` without accumulating in memory.

    Per ADR-4 §13.1 Amendment 20260424-1: replaces the build-script-scoped
    delegation to ``mp._fetch_month_dataframe`` + ``mp._write_parquet`` (which
    accumulates every 100K fetchmany batch into a single ``rows`` list before
    building a DataFrame + Arrow Table). Observed pilot thrash (~11.8 GiB peak
    WS on 16 GiB host) violated CAP_v3 = 8.4 GiB.

    This helper:
      - Opens the same server-side cursor as ``_fetch_month_dataframe``
        (``name="cache_stream"``, ``itersize=100_000``, identical query/params).
      - Opens a ``pyarrow.parquet.ParquetWriter`` on ``out_tmp`` with the SAME
        determinism knobs as ``mp._write_parquet``:
            compression='snappy', version='2.6', use_dictionary=True,
            write_statistics=True, store_schema=True
      - Per ``fetchmany(100_000)`` batch: build a pyarrow Table with explicit
        per-column typed arrays (mirrors ``_fetch_month_dataframe`` strict
        coercions verbatim — timestamp[ns], float64, int32, nullable strings)
        and calls ``writer.write_table(batch_table)``. PyArrow emits one row
        group per ``write_table`` call — 100K-row batches produce 100K-row
        row groups, matching ``row_group_size=100_000`` in canonical path.
      - Drops the batch + Arrow Table before the next fetch — no inter-batch
        retention.
      - Empty-month short-circuit: if the first ``fetchmany`` returns ``[]``,
        returns ``(0, None, None)`` WITHOUT opening the ParquetWriter, so no
        ``.tmp`` file is created (matches existing ``_cleanup_partial`` path).

    Atomic rename + sha256 are performed by the caller (``os.replace(tmp,
    out_path)`` + ``mp._sha256_file``) — identical to the existing flow.

    Parameters
    ----------
    conn
        Live psycopg2 connection.
    ticker
        Whitelisted ticker (caller validates).
    mw
        ``mp.MonthWindow`` partition.
    out_tmp
        Path to write the ``.tmp`` parquet to. Caller renames on success.
    schema
        Arrow schema (``mp._build_parquet_schema()``).

    Returns
    -------
    tuple[int, datetime | None, datetime | None]
        ``(row_count, first_ts, last_ts)``. ``first_ts``/``last_ts`` are
        ``None`` when ``row_count == 0``. Timestamps are already ``datetime``
        objects coming out of psycopg2.
    """
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    # end is half-open (< next day 00:00) — matches _fetch_month_dataframe.
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

    row_count = 0
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    writer: pq.ParquetWriter | None = None

    # Field positions (mirror SELECT order).
    I_TS, I_TICK, I_PRICE, I_QTY, I_AGG, I_BUY, I_SELL = 0, 1, 2, 3, 4, 5, 6

    out_tmp.parent.mkdir(parents=True, exist_ok=True)

    try:
        with conn.cursor(name="cache_stream") as cur:
            cur.itersize = 100_000
            cur.execute(query, params)
            while True:
                batch = cur.fetchmany(cur.itersize)
                if not batch:
                    break

                # Per-column strict coercions — mirror
                # _fetch_month_dataframe:532-541 verbatim but expressed as
                # pyarrow arrays with explicit types (avoid pandas on hot
                # path; also avoids Decimal->float64 inference surprises).
                ts_col = [row[I_TS] for row in batch]
                tick_col = [str(row[I_TICK]) for row in batch]
                price_col = [float(row[I_PRICE]) for row in batch]
                qty_col = [int(row[I_QTY]) for row in batch]
                agg_col = [str(row[I_AGG]) for row in batch]
                buy_col = [
                    None if row[I_BUY] is None else str(row[I_BUY])
                    for row in batch
                ]
                sell_col = [
                    None if row[I_SELL] is None else str(row[I_SELL])
                    for row in batch
                ]

                table = pa.Table.from_arrays(
                    [
                        pa.array(ts_col, type=pa.timestamp("ns")),
                        pa.array(tick_col, type=pa.string()),
                        pa.array(price_col, type=pa.float64()),
                        pa.array(qty_col, type=pa.int32()),
                        pa.array(agg_col, type=pa.string()),
                        pa.array(buy_col, type=pa.string()),
                        pa.array(sell_col, type=pa.string()),
                    ],
                    schema=schema,
                )

                if writer is None:
                    # Only open the writer once we have real data — preserves
                    # the empty-month short-circuit (no orphan .tmp on disk).
                    writer = pq.ParquetWriter(
                        out_tmp,
                        schema,
                        compression="snappy",
                        version="2.6",
                        use_dictionary=True,
                        write_statistics=True,
                    )
                    first_ts = ts_col[0]

                writer.write_table(table)
                last_ts = ts_col[-1]
                row_count += len(batch)

                # Drop references so the next fetchmany runs with a clean
                # working set — no accumulation (ADR-4 §13.1 memory cap).
                del ts_col, tick_col, price_col, qty_col
                del agg_col, buy_col, sell_col
                del table, batch
    finally:
        if writer is not None:
            writer.close()

    return row_count, first_ts, last_ts


def run(args: BuildArgs) -> int:
    # 1. Hold-out guard — MUST be before any I/O (ADR-4 §8.1).
    assert_holdout_safe(args.start_date, args.end_date)

    months = mp.iter_month_windows(args.start_date, args.end_date)

    if args.dry_run:
        print(
            f"[cache-dry-run] ticker={args.ticker} window="
            f"{args.start_date.isoformat()}..{args.end_date.isoformat()} "
            f"months={len(months)}"
        )
        for mw in months:
            out = _cache_output_path(args.cache_dir, args.ticker, mw)
            print(
                f"[cache-dry-run]   -> {mw.label} "
                f"[{mw.start} .. {mw.end_inclusive}] -> {out}"
            )
        return 0

    generated_at = datetime.now().isoformat(timespec="seconds")

    # Arrow schema is built once — shared across all month writers.
    schema = mp._build_parquet_schema()

    # Manifest state (read for resume/force-rebuild).
    manifest_state = _read_cache_manifest(args.cache_manifest)

    # DB connection is opened lazily — only when the first non-skipped month
    # needs a fetch. This keeps resume runs DB-free (ADR-4 §5.3 step 7.2).
    conn = None
    env: dict[str, str] | None = None

    def _ensure_conn():
        nonlocal conn, env
        if conn is None:
            env = mp._load_env_vespera()
            conn = mp._connect(env)
        return conn

    total_flushed = 0
    total_skipped = 0
    try:
        for mw in months:
            out_path = _cache_output_path(args.cache_dir, args.ticker, mw)
            rel_path = _relpath_posix(out_path)
            key = (rel_path, args.ticker)

            # --- force-rebuild: wipe chunk + manifest row BEFORE resume check
            if args.force_rebuild:
                _cleanup_partial(out_path)
                try:
                    out_path.unlink(missing_ok=True)
                except Exception:
                    pass
                _remove_cache_manifest_row(
                    args.cache_manifest, rel_path, args.ticker,
                )
                # Reload manifest state after mutation.
                manifest_state = _read_cache_manifest(args.cache_manifest)

            # --- resume: skip month if chunk+manifest match
            if args.resume and key in manifest_state:
                mrow = manifest_state[key]
                expected_sha = mrow.get("sha256", "").strip().lower()
                if out_path.exists() and expected_sha:
                    disk_sha = mp._sha256_file(out_path)
                    if disk_sha == expected_sha:
                        print(
                            f"[cache] skip {mw.label} (resume: sha matches)"
                        )
                        total_skipped += 1
                        continue

            # --- partial cleanup (crash recovery)
            _cleanup_partial(out_path)

            # --- checkpoint sentinel (JSON marker; informational only —
            # deterministic atomicity is ensured by os.replace of the parquet
            # itself, not by this file).
            ckpt = _ckpt_path(out_path)
            ckpt.parent.mkdir(parents=True, exist_ok=True)
            ckpt.write_text(
                json.dumps({
                    "status": "in_progress",
                    "started_at": datetime.now().isoformat(timespec="seconds"),
                    "month": mw.label,
                    "ticker": args.ticker,
                }),
                encoding="utf-8",
            )

            print(
                f"[cache] build {args.ticker} {mw.label} "
                f"[{mw.start} .. {mw.end_inclusive}] -> {out_path}"
            )
            _ensure_conn()

            # ADR-4 §13.1 Amendment 20260424-1 — streaming parquet writer.
            # Replaces prior `mp._fetch_month_dataframe` + `mp._write_parquet`
            # pair that accumulated the whole month in memory (pilot thrash
            # at ~11.8 GiB peak WS). Helper writes batches directly to the
            # ``.tmp`` file via ``pq.ParquetWriter``; caller handles the
            # atomic rename + sha256.
            out_tmp = _tmp_path(out_path)
            try:
                row_count, first_ts, last_ts = _stream_month_to_parquet(
                    conn, args.ticker, mw, out_tmp, schema,
                )
            except Exception:
                # Ensure no stale .tmp survives on error; caller retries via
                # resume / force-rebuild on next invocation.
                _cleanup_partial(out_path)
                raise

            if row_count == 0:
                print(
                    f"[cache]   WARNING: no rows for {mw.label}; "
                    "skipping file and manifest flush."
                )
                _cleanup_partial(out_path)
                gc.collect()
                continue

            # --- atomic rename (.tmp -> final) — matches _write_parquet step
            os.replace(out_tmp, out_path)
            digest = mp._sha256_file(out_path)

            # first_ts / last_ts are datetime objects from psycopg2 — no need
            # to re-read the parquet.
            start_ts = first_ts.isoformat() if first_ts is not None else ""
            end_ts = last_ts.isoformat() if last_ts is not None else ""
            # Phase classifier fires on straddle — defense in depth (ADR-4 §8.3).
            phase = mp.classify_phase(mw.start, mw.end_inclusive)
            row = {
                "path": rel_path,
                "rows": str(row_count),
                "sha256": digest,
                "start_ts_brt": start_ts,
                "end_ts_brt": end_ts,
                "ticker": args.ticker,
                "phase": phase,
                "generated_at_brt": generated_at,
            }
            _append_cache_manifest_row(args.cache_manifest, row)
            total_flushed += 1
            print(
                f"[cache]   rows={row_count} phase={phase} sha256={digest} "
                f"flushed ({total_flushed} total)"
            )

            # --- clear checkpoint only after manifest row flushed
            try:
                ckpt.unlink(missing_ok=True)
            except Exception:
                pass

            gc.collect()
    finally:
        if conn is not None:
            conn.close()

    print(
        f"[cache] run complete; built={total_flushed} skipped={total_skipped} "
        f"-> {args.cache_manifest}",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        return run(args)
    except HoldoutLockError as exc:
        print(f"HoldoutLockError: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        safe = mp._sanitize_error_message(str(exc))
        print(f"ERROR: {safe}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
