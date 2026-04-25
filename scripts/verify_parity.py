"""Parity gate — re-materialize a single month into SCRATCH and compare sha256
to the on-disk canonical parquet.

Story: T002.0a — squad gates G1 (Mar 2024) and G3 (Sep 2024)
Owner: Dex (@dev)

Purpose
-------
Ensure the refactored ``scripts/materialize_parquet.py`` (PATCH
t002-refactor-next-run, commit f971bb5) produces byte-identical parquet
output to the previously-materialized files on disk. A byte-identical
re-materialization proves that the 3 patches (cursor streaming, per-month
manifest flush, gc.collect) did NOT change the serialized output — only
the run-time memory/crash-safety behavior.

Behavior
--------
1. Accept ``--month YYYY-MM`` (e.g. ``2024-03``).
2. Re-materialize that month into a SCRATCH directory
   (``data/_scratch/parity/year=YYYY/month=MM/``) using the SAME
   ``_fetch_month_dataframe`` + ``_write_parquet`` code paths as
   ``materialize_parquet.py``. NO re-implementation — functions are imported.
3. Compute sha256 of the scratch file and of the on-disk
   ``data/in_sample/year=YYYY/month=MM/<ticker>-YYYY-MM.parquet``.
4. Print PASS (exit 0) if the two hashes match, FAIL (exit 1) otherwise.

Guardrails
----------
* NEVER touches ``data/in_sample/`` (read-only).
* NEVER touches ``data/manifest.csv`` (read-only).
* Scratch dir is created fresh per invocation and is safe to delete.
"""

from __future__ import annotations

import argparse
import gc
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _holdout_lock import assert_holdout_safe  # noqa: E402
from materialize_parquet import (  # noqa: E402
    MonthWindow,
    _connect,
    _fetch_month_dataframe,
    _load_env_vespera,
    _month_last,
    _sha256_file,
    _write_parquet,
)

REPO_ROOT = _SCRIPTS_DIR.parent
IN_SAMPLE_DIR = REPO_ROOT / "data" / "in_sample"
SCRATCH_DIR = REPO_ROOT / "data" / "_scratch" / "parity"

# Q-10: ticker whitelist (mirrors packages/t002_eod_unwind/adapters/*.py)
_ALLOWED_TICKERS: frozenset[str] = frozenset({"WDO", "WIN"})


def _parse_month_arg(value: str) -> tuple[int, int]:
    parts = value.split("-")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM, got {value!r}")
    try:
        y = int(parts[0])
        m = int(parts[1])
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid YYYY-MM: {value!r}: {exc}")
    if not (2020 <= y <= 2030 and 1 <= m <= 12):
        raise argparse.ArgumentTypeError(f"out of range YYYY-MM: {value!r}")
    return y, m


def _canonical_path(year: int, month: int, ticker: str) -> Path:
    return (
        IN_SAMPLE_DIR
        / f"year={year:04d}"
        / f"month={month:02d}"
        / f"{ticker.lower()}-{year:04d}-{month:02d}.parquet"
    )


def _scratch_path(year: int, month: int, ticker: str) -> Path:
    return (
        SCRATCH_DIR
        / f"year={year:04d}"
        / f"month={month:02d}"
        / f"{ticker.lower()}-{year:04d}-{month:02d}.parquet"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify_parity",
        description=(
            "Re-materialize one month into a scratch dir and sha256-compare "
            "against the canonical in_sample parquet. Used for squad gates "
            "G1 (Mar 2024) and G3 (Sep 2024)."
        ),
    )
    parser.add_argument(
        "--month",
        type=_parse_month_arg,
        required=True,
        help="Month to re-materialize (YYYY-MM, e.g. 2024-03).",
    )
    parser.add_argument(
        "--ticker",
        type=str,
        default="WDO",
        help="Ticker to query (default: WDO).",
    )
    ns = parser.parse_args(argv)

    year, month = ns.month
    ticker = ns.ticker.strip()

    # Q-10: ticker whitelist — fail BEFORE any I/O
    if ticker not in _ALLOWED_TICKERS:
        raise ValueError(
            f"ticker must be one of {sorted(_ALLOWED_TICKERS)}; got {ticker!r}"
        )

    # Q-02: hold-out guard — fail BEFORE any I/O (parity with feed_parquet.py:365,
    # feed_timescale.py:197). Month is evaluated inclusive-end (YYYY-MM-01 .. last day of month).
    m_first_guard = date(year, month, 1)
    m_last_guard = _month_last(m_first_guard)
    # Propagate HoldoutLockError with exit 2 per ADR-2 exit-code map
    from _holdout_lock import HoldoutLockError  # noqa: E402
    try:
        assert_holdout_safe(m_first_guard, m_last_guard)
    except HoldoutLockError as exc:
        print(f"HoldoutLockError: {exc}", file=sys.stderr)
        return 2

    canonical = _canonical_path(year, month, ticker)
    if not canonical.exists():
        print(
            f"FATAL: canonical parquet not found: {canonical}",
            file=sys.stderr,
        )
        return 1

    scratch = _scratch_path(year, month, ticker)
    scratch.parent.mkdir(parents=True, exist_ok=True)
    # Start fresh — delete any prior scratch file for this month.
    if scratch.exists():
        scratch.unlink()

    # Build the MonthWindow matching exactly what materialize_parquet.run()
    # would construct when invoked with --start-date YYYY-MM-01 --end-date YYYY-MM-last.
    # Clip semantics: when --start <= month_first and --end >= month_last,
    # MonthWindow.start == month_first and MonthWindow.end_inclusive == month_last.
    m_first = date(year, month, 1)
    m_last = _month_last(m_first)
    mw = MonthWindow(year=year, month=month, start=m_first, end_inclusive=m_last)

    print(f"[parity] month={mw.label} window=[{mw.start} .. {mw.end_inclusive}]")
    print(f"[parity] canonical={canonical}")
    print(f"[parity] scratch={scratch}")

    env = _load_env_vespera()
    conn = _connect(env)
    try:
        df = _fetch_month_dataframe(conn, ticker, mw)
        if df.empty:
            print(
                f"FATAL: no rows returned for {mw.label} — cannot compare",
                file=sys.stderr,
            )
            return 1
        print(f"[parity] fetched rows={len(df)}")
        _write_parquet(df, scratch)
        # Release DataFrame before hashing (parity with materialize loop).
        del df
        gc.collect()
    finally:
        conn.close()

    canonical_sha = _sha256_file(canonical)
    scratch_sha = _sha256_file(scratch)

    print(f"[parity] canonical sha256 = {canonical_sha}")
    print(f"[parity] scratch   sha256 = {scratch_sha}")

    if canonical_sha == scratch_sha:
        print(f"[parity] PASS — {mw.label} byte-identical")
        return 0
    print(f"[parity] FAIL — {mw.label} hashes diverge", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
