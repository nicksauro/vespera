"""Unit tests — materialize_parquet.py --source={sentinel,cache} dispatch.

Story:  T002.0a (ADR-4 pre-cache layer)
Spec:   docs/architecture/pre-cache-layer-spec.md §9.4

Test enumeration vs spec:
  T14  test_materialize_source_cache_does_not_connect_postgres
  T15  test_materialize_source_sentinel_unchanged
  +    test_materialize_source_flag_defaults_to_sentinel
  +    test_materialize_source_cache_routes_through_feed_cache
  +    test_materialize_source_cache_with_manifest_path_canonical_blocked
  +    test_materialize_source_sentinel_rejects_cache_flags
"""

from __future__ import annotations

import csv
import sys
from datetime import date, datetime
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import materialize_parquet as mp  # noqa: E402


def _base_argv(*extra: str) -> list[str]:
    return [
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        *extra,
    ]


# ---------------------------------------------------------------------------
# Default: --source=sentinel preserved (non-breaking, T15)
# ---------------------------------------------------------------------------

def test_materialize_source_flag_defaults_to_sentinel():
    args = mp.parse_args(_base_argv())
    assert args.source == "sentinel"
    assert args.cache_dir is None
    assert args.cache_manifest is None


def test_materialize_source_sentinel_unchanged(tmp_path):
    """Explicit --source=sentinel keeps defaults and does not need cache flags."""
    args = mp.parse_args(_base_argv("--source", "sentinel"))
    assert args.source == "sentinel"
    assert args.cache_dir is None


def test_materialize_source_sentinel_rejects_cache_flags(tmp_path):
    with pytest.raises(SystemExit):
        mp.parse_args(_base_argv(
            "--source", "sentinel",
            "--cache-dir", str(tmp_path / "c"),
        ))
    with pytest.raises(SystemExit):
        mp.parse_args(_base_argv(
            "--source", "sentinel",
            "--cache-manifest", str(tmp_path / "m.csv"),
        ))


# ---------------------------------------------------------------------------
# --source=cache (T14)
# ---------------------------------------------------------------------------

def test_materialize_source_cache_does_not_connect_postgres(
    tmp_path, monkeypatch, capsys,
):
    """T14 — a --source=cache dry-run does NOT invoke psycopg2.connect."""
    import psycopg2  # type: ignore[import-untyped]

    def sentinel_connect(*a, **kw):
        raise AssertionError(
            "materialize_parquet called psycopg2.connect despite --source=cache"
        )
    monkeypatch.setattr(psycopg2, "connect", sentinel_connect)
    monkeypatch.setattr(mp, "_connect", sentinel_connect)

    # Point cache to tmp so the default (data/cache/...) is NOT used.
    cache_dir = tmp_path / "cache" / "raw_trades"
    cache_manifest = tmp_path / "cache" / "cache-manifest.csv"

    args = mp.parse_args(_base_argv(
        "--source", "cache",
        "--cache-dir", str(cache_dir),
        "--cache-manifest", str(cache_manifest),
        "--dry-run",
    ))
    assert args.source == "cache"
    assert args.cache_dir == cache_dir
    assert args.cache_manifest == cache_manifest

    rc = mp.run(args)
    assert rc == 0


def test_materialize_source_cache_routes_through_feed_cache(
    tmp_path, monkeypatch,
):
    """--source=cache routes run() to _fetch_month_from_cache (no DB)."""
    import pandas as pd
    import numpy as np

    # Build one tiny cache parquet + manifest.
    cache_dir = tmp_path / "cache" / "raw_trades"
    manifest_path = tmp_path / "cache" / "cache-manifest.csv"
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({
        "timestamp": pd.to_datetime([datetime(2024, 8, 1, 10, 0, 0)] * 3),
        "ticker": ["WDO"] * 3,
        "price": np.array([5000.0, 5001.0, 5002.0], dtype="float64"),
        "qty": np.array([1, 2, 3], dtype="int32"),
        "aggressor": ["BUY", "SELL", "BUY"],
        "buy_agent": pd.array(["A", "B", "C"], dtype="string"),
        "sell_agent": pd.array(["X", "Y", "Z"], dtype="string"),
    })
    mp._write_parquet(df, parquet_path)
    sha = mp._sha256_file(parquet_path)

    import os as _os
    rel = Path(_os.path.relpath(parquet_path, mp.REPO_ROOT)).as_posix()
    with manifest_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh, fieldnames=list(mp.MANIFEST_COLUMNS), lineterminator="\n",
        )
        w.writeheader()
        w.writerow({
            "path": rel, "rows": "3", "sha256": sha,
            "start_ts_brt": "2024-08-01T10:00:00",
            "end_ts_brt": "2024-08-01T10:00:00",
            "ticker": "WDO", "phase": "in_sample",
            "generated_at_brt": "2026-04-23T12:00:00",
        })

    # Output scratch manifest (avoid canonical).
    out_dir = tmp_path / "out"
    out_manifest = tmp_path / "out-manifest.csv"

    # Block DB path: this proves --source=cache is on the cache branch.
    def no_db(*a, **kw):
        raise AssertionError("cache branch leaked through to _connect")
    monkeypatch.setattr(mp, "_connect", no_db)
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    args = mp.Args(
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        ticker="WDO",
        output_dir=out_dir,
        dry_run=False,
        no_manifest=False,
        manifest_path=out_manifest,
        source="cache",
        cache_dir=cache_dir,
        cache_manifest=manifest_path,
    )
    rc = mp.run(args)
    assert rc == 0
    # Scratch manifest should have one row.
    rows = list(csv.DictReader(out_manifest.open()))
    assert len(rows) == 1


def test_materialize_source_cache_with_manifest_path_canonical_blocked():
    """MWF-20260422-1 still in force: --manifest-path=<canonical> rejected
    even under --source=cache."""
    with pytest.raises(SystemExit):
        mp.parse_args(_base_argv(
            "--source", "cache",
            "--cache-dir", "/tmp/cache",
            "--cache-manifest", "/tmp/cache-manifest.csv",
            "--manifest-path", str(mp.MANIFEST_PATH),
        ))


def test_materialize_source_cache_manifest_cannot_alias_canonical(tmp_path):
    """--cache-manifest pointing at canonical data/manifest.csv is rejected."""
    with pytest.raises(SystemExit):
        mp.parse_args(_base_argv(
            "--source", "cache",
            "--cache-dir", str(tmp_path / "c"),
            "--cache-manifest", str(mp.MANIFEST_PATH),
        ))
