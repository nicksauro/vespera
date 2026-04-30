"""Materialize hold-out monthly parquets from Sentinel daily files.

Story: T002.7-prep
Epic:  EPIC-T002.7 (Phase G OOS validation)
Owner: Dara (@data-engineer)
Council: ESC-012 R4 — hold-out window 2025-07-01..2026-04-21 (Mira spec §15.13)

Purpose
-------
Aggregate daily trade parquets from ``D:/sentinel_data/historical/`` into
monthly partitioned parquets under ``data/holdout/year=YYYY/month=MM/`` —
mirror layout of ``data/in_sample/`` so Phase G OOS code can dispatch on
``--phase`` cleanly.

Source: ``D:/sentinel_data/historical/WDO_YYYYMMDD.parquet`` (10 columns,
us-precision, large_string types). Daily files are CONCATENATED per month
and projected onto the canonical 7-column schema:

    timestamp  : timestamp[ns]  (BRT-naive)
    ticker     : string
    price      : float64
    qty        : int32
    aggressor  : string
    buy_agent  : string  (nullable)
    sell_agent : string  (nullable)

Output layout
-------------
    data/holdout/year=YYYY/month=MM/wdo-YYYY-MM.parquet
    data/manifest.csv  (append-only; phase=hold_out rows)

Hold-out unlock
---------------
Materialization is data-engineering preparation — it makes raw bytes
available on disk under the canonical layout. The actual statistical
unlock happens at runtime in ``compute_ic_from_cpcv_results
(holdout_locked=False)`` per spec §15.13. To honor the
``_holdout_lock.assert_holdout_safe`` guard contract (R1 hold-out virgin),
this script requires ``VESPERA_UNLOCK_HOLDOUT=1`` — the operator MUST
set it explicitly with justification in their session record.

Determinism
-----------
Per-month: daily files are sorted by filename (YYYYMMDD), concatenated,
sorted by (ticker, timestamp), written via ``pq.write_table`` with the
same knobs as ``materialize_parquet.py`` (snappy, row_group=100k,
v2.6, store_schema=True).

Reuses helpers from ``materialize_parquet.py`` so behavior matches:
``_build_parquet_schema``, ``_write_parquet``, ``_sha256_file``,
``classify_phase``, ``_resolve_manifest_target``, ``_guard_canonical_write``,
``_append_manifest``, ``MANIFEST_PATH``, ``MANIFEST_COLUMNS``, ``REPO_ROOT``.

CLI
---
    python scripts/materialize_holdout_parquet.py \
        --start-date 2025-07-01 \
        --end-date 2026-04-21 \
        --ticker WDO \
        --source-dir D:/sentinel_data/historical \
        --output-dir data/holdout/

Bypassing manifest:
    --no-manifest         (no manifest write)
    --manifest-path PATH  (scratch manifest)
"""

from __future__ import annotations

import argparse
import gc
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _holdout_lock import (  # noqa: E402
    HoldoutLockError,
    assert_holdout_safe,
)
from materialize_parquet import (  # noqa: E402
    MANIFEST_COLUMNS,
    MANIFEST_PATH,
    REPO_ROOT,
    MonthWindow,
    _append_manifest,
    _emit_launch_banner,
    _emit_scratch_output_warning,
    _guard_canonical_write,
    _resolve_manifest_target,
    _sha256_file,
    _write_parquet,
    classify_phase,
    iter_month_windows,
)

DEFAULT_SOURCE_DIR = Path("D:/sentinel_data/historical")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "data" / "holdout"

# Daily filename pattern: WDO_YYYYMMDD.parquet
_DAILY_RE = re.compile(r"^([A-Z]{1,8})_([0-9]{8})\.parquet$")


@dataclass(frozen=True)
class Args:
    start_date: date
    end_date: date
    ticker: str
    source_dir: Path
    output_dir: Path
    dry_run: bool
    no_manifest: bool
    manifest_path: Path | None


def _parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="materialize_holdout_parquet",
        description=(
            "Aggregate Sentinel daily parquets into monthly hold-out "
            "partitions matching the in-sample schema. Requires "
            "VESPERA_UNLOCK_HOLDOUT=1."
        ),
    )
    parser.add_argument(
        "--start-date", "--start",
        dest="start_date", type=_parse_date, required=True,
    )
    parser.add_argument(
        "--end-date", "--end",
        dest="end_date", type=_parse_date, required=True,
    )
    parser.add_argument(
        "--ticker", type=str, required=True,
    )
    parser.add_argument(
        "--source-dir",
        type=Path, default=DEFAULT_SOURCE_DIR,
        help=f"Daily parquet root (default: {DEFAULT_SOURCE_DIR}).",
    )
    parser.add_argument(
        "--output-dir", "--out",
        dest="output_dir", type=Path, default=DEFAULT_OUTPUT_DIR,
        help=f"Monthly output root (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Plan-only: list daily files per month and exit.",
    )
    manifest_group = parser.add_mutually_exclusive_group()
    manifest_group.add_argument(
        "--no-manifest", action="store_true",
    )
    manifest_group.add_argument(
        "--manifest-path", dest="manifest_path", type=Path, default=None,
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
    manifest_path = ns.manifest_path
    if manifest_path is not None:
        try:
            resolved_override = Path(manifest_path).resolve()
        except (OSError, RuntimeError):
            resolved_override = Path(manifest_path)
        if resolved_override == MANIFEST_PATH.resolve():
            parser.error(
                "--manifest-path must not point at the canonical "
                "data/manifest.csv; use the cosign flow."
            )
    return Args(
        start_date=ns.start_date,
        end_date=ns.end_date,
        ticker=ticker,
        source_dir=ns.source_dir,
        output_dir=ns.output_dir,
        dry_run=bool(ns.dry_run),
        no_manifest=bool(ns.no_manifest),
        manifest_path=manifest_path,
    )


def _list_daily_files(
    source_dir: Path, ticker: str, start: date, end_inclusive: date,
) -> list[tuple[date, Path]]:
    """Return [(date, path)] for all daily files in [start, end_inclusive].

    Files are matched by ``{TICKER}_{YYYYMMDD}.parquet`` exact regex.
    Sorted ascending by date.
    """
    if not source_dir.exists():
        raise FileNotFoundError(f"source dir does not exist: {source_dir}")
    out: list[tuple[date, Path]] = []
    for entry in source_dir.iterdir():
        if not entry.is_file():
            continue
        m = _DAILY_RE.match(entry.name)
        if not m:
            continue
        if m.group(1) != ticker:
            continue
        try:
            d = datetime.strptime(m.group(2), "%Y%m%d").date()
        except ValueError:
            continue
        if d < start or d > end_inclusive:
            continue
        out.append((d, entry))
    out.sort(key=lambda x: x[0])
    return out


def _month_output_path(output_dir: Path, ticker: str, mw: MonthWindow) -> Path:
    return (
        output_dir
        / f"year={mw.year:04d}"
        / f"month={mw.month:02d}"
        / f"{ticker.lower()}-{mw.label}.parquet"
    )


def _read_and_normalize_daily(path: Path, ticker: str):
    """Read a single daily parquet and project onto the canonical 7-col schema.

    Source columns: timestamp, ticker, price, vol, qty, buy_agent, sell_agent,
                    aggressor, trade_type, trade_number  (us-precision, large_string)
    Target columns: timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent
                    (ns-precision, string, R2 BRT-naive)
    """
    import pandas as pd  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    pf = pq.ParquetFile(path)
    # Read only the columns we need — saves IO/RAM.
    df = pf.read(
        columns=[
            "timestamp", "ticker", "price", "qty",
            "aggressor", "buy_agent", "sell_agent",
        ],
    ).to_pandas()
    if df.empty:
        return df

    # Strict typing — mirror materialize_parquet._fetch_month_dataframe.
    df["timestamp"] = pd.to_datetime(df["timestamp"])  # us -> ns coercion
    if getattr(df["timestamp"].dt, "tz", None) is not None:
        raise RuntimeError(
            f"timestamp column tz-aware in {path}; violates R2"
        )
    df["ticker"] = df["ticker"].astype(str)
    df["price"] = df["price"].astype("float64")
    df["qty"] = df["qty"].astype("int32")
    df["aggressor"] = df["aggressor"].astype(str)
    df["buy_agent"] = df["buy_agent"].astype("string")
    df["sell_agent"] = df["sell_agent"].astype("string")

    # Defensive: filter to requested ticker (in case file mixes tickers).
    df = df.loc[df["ticker"] == ticker].reset_index(drop=True)
    return df


def _aggregate_month(
    daily_files: list[tuple[date, Path]],
    ticker: str,
    mw: MonthWindow,
):
    """Concatenate daily files for one month, sorted by (ticker, timestamp).

    Filters each daily file to ``[mw.start, mw.end_inclusive]`` so a month
    partition with a clipped start/end (e.g. 2025-07-01 first day) yields
    the right rows even if the daily file spans extra dates (it never does
    with WDO_YYYYMMDD.parquet, but be defensive).
    """
    import pandas as pd  # type: ignore[import-untyped]

    relevant = [
        (d, p) for (d, p) in daily_files
        if mw.start <= d <= mw.end_inclusive
    ]
    if not relevant:
        return pd.DataFrame(columns=[
            "timestamp", "ticker", "price", "qty",
            "aggressor", "buy_agent", "sell_agent",
        ])

    frames = []
    for _, p in relevant:
        frames.append(_read_and_normalize_daily(p, ticker))

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    if df.empty:
        return df
    # Stable sort on (ticker, timestamp) — matches materialize_parquet.
    df = df.sort_values(
        by=["ticker", "timestamp"], kind="mergesort",
    ).reset_index(drop=True)
    return df


def run(args: Args) -> int:
    # 1. Hold-out guard — REQUIRES VESPERA_UNLOCK_HOLDOUT=1.
    assert_holdout_safe(args.start_date, args.end_date)

    # Resolve manifest target + emit banners.
    target = _resolve_manifest_target(args)
    _emit_scratch_output_warning(args, target)
    _emit_launch_banner(args, target)

    months = iter_month_windows(args.start_date, args.end_date)
    daily_files = _list_daily_files(
        args.source_dir, args.ticker, args.start_date, args.end_date,
    )
    if not daily_files:
        print(
            f"[holdout] WARNING: no daily files matching "
            f"{args.ticker}_YYYYMMDD.parquet in {args.source_dir} "
            f"for window [{args.start_date}, {args.end_date}]",
            file=sys.stderr,
        )

    if args.dry_run:
        print(
            f"[dry-run] ticker={args.ticker} window="
            f"{args.start_date.isoformat()}..{args.end_date.isoformat()} "
            f"months={len(months)} daily_files={len(daily_files)}"
        )
        for mw in months:
            relevant = [d for (d, _) in daily_files
                        if mw.start <= d <= mw.end_inclusive]
            out = _month_output_path(args.output_dir, args.ticker, mw)
            print(
                f"[dry-run]   -> {mw.label} "
                f"[{mw.start} .. {mw.end_inclusive}] "
                f"daily={len(relevant)} -> {out}"
            )
        return 0

    # Fail-fast custodial guard BEFORE any write.
    if target is not None:
        _guard_canonical_write(target)

    generated_at = datetime.now().isoformat(timespec="seconds")

    import pandas as pd  # type: ignore[import-untyped]

    total_flushed = 0
    for mw in months:
        out_path = _month_output_path(args.output_dir, args.ticker, mw)
        relevant_daily_count = sum(
            1 for (d, _) in daily_files if mw.start <= d <= mw.end_inclusive
        )
        print(
            f"[holdout] {mw.label} [{mw.start} .. {mw.end_inclusive}] "
            f"daily_files={relevant_daily_count} -> {out_path}"
        )
        df = _aggregate_month(daily_files, args.ticker, mw)
        if df.empty:
            print(
                f"[holdout]   WARNING: no rows for {mw.label}; skipping file."
            )
            del df
            gc.collect()
            continue

        _write_parquet(df, out_path)
        digest = _sha256_file(out_path)

        rel_path = Path(
            os.path.relpath(out_path, REPO_ROOT)
        ).as_posix()
        start_ts = pd.Timestamp(df["timestamp"].iloc[0]).isoformat()
        end_ts = pd.Timestamp(df["timestamp"].iloc[-1]).isoformat()
        phase = classify_phase(mw.start, mw.end_inclusive)
        if phase != "hold_out":
            raise RuntimeError(
                f"phase classifier returned {phase!r} for window "
                f"[{mw.start}, {mw.end_inclusive}]; expected hold_out"
            )
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
        if target is None:
            print(
                f"[manifest-suppressed] month={mw.label} "
                f"reason=--no-manifest",
                file=sys.stderr,
            )
        else:
            _append_manifest([month_row], target=target)
            total_flushed += 1
            print(
                f"[manifest] flushed {mw.label} ({total_flushed} total)"
            )
        print(
            f"[holdout]   rows={len(df)} phase={phase} sha256={digest}"
        )

        del df
        gc.collect()

    # End-of-run summary.
    if target is None:
        print(
            "[holdout] run complete; 0 month(s) flushed (--no-manifest)",
            file=sys.stderr,
        )
    elif target.resolve() != MANIFEST_PATH.resolve():
        print(
            f"[holdout] run complete; {total_flushed} month(s) "
            f"flushed -> {target}",
            file=sys.stderr,
        )
    else:
        if total_flushed:
            print(
                f"[holdout] run complete; {total_flushed} month(s) "
                f"flushed -> {MANIFEST_PATH}"
            )
        else:
            print("[holdout] no rows appended (all months empty)")
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
