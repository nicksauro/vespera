"""Unit tests — feed_cache adapter (ADR-4 §9.1).

Story:  T002.0a (pre-cache layer, Option B)
Spec:   docs/architecture/pre-cache-layer-spec.md §9

Test enumeration vs §9:
  T1  test_feed_cache_rejects_unknown_ticker
  T2  test_feed_cache_rejects_tz_aware_input
  T3  test_feed_cache_holdout_locked_raises_before_open
      test_feed_cache_holdout_unlocked_does_not_raise_lock
  T4  test_feed_cache_sha256_mismatch_raises
  T5  test_feed_cache_missing_manifest_raises_filenotfound
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

import pytest

from packages.t002_eod_unwind.adapters import feed_cache
from packages.t002_eod_unwind.adapters._holdout_lock import HoldoutLockError


_LOCKED_START = datetime(2025, 7, 1)
_LOCKED_END = datetime(2025, 7, 2)


# ---------------------------------------------------------------------------
# T1 — unknown ticker rejection
# ---------------------------------------------------------------------------

def test_feed_cache_rejects_unknown_ticker():
    with pytest.raises(ValueError):
        list(feed_cache.load_trades(
            datetime(2024, 3, 4), datetime(2024, 3, 5), "PETR4",
        ))


# ---------------------------------------------------------------------------
# T2 — tz-aware inputs rejection
# ---------------------------------------------------------------------------

def test_feed_cache_rejects_tz_aware_input():
    aware = datetime(2024, 3, 4, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        list(feed_cache.load_trades(aware, datetime(2024, 3, 5), "WDO"))


def test_feed_cache_rejects_tz_aware_end():
    aware_end = datetime(2024, 3, 5, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        list(feed_cache.load_trades(datetime(2024, 3, 4), aware_end, "WDO"))


# ---------------------------------------------------------------------------
# T3 — hold-out guard fires BEFORE any parquet open (AC11 parity)
# ---------------------------------------------------------------------------

def test_feed_cache_holdout_locked_raises_before_open(monkeypatch):
    """ADR-4 §8.2: guard fires BEFORE ParquetFile construction."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    open_called = {"n": 0}

    class SentinelParquetFile:
        def __init__(self, *args, **kwargs):
            open_called["n"] += 1
            raise AssertionError(
                "feed_cache opened a ParquetFile BEFORE the hold-out "
                "guard rejected the window — AC11 violation"
            )

    import pyarrow.parquet as pq  # type: ignore[import-untyped]
    monkeypatch.setattr(pq, "ParquetFile", SentinelParquetFile)

    with pytest.raises(HoldoutLockError):
        list(feed_cache.load_trades(_LOCKED_START, _LOCKED_END, "WDO"))

    assert open_called["n"] == 0, (
        f"ParquetFile was opened {open_called['n']} time(s) — "
        "guard must run first"
    )


def test_feed_cache_holdout_unlocked_does_not_raise_lock(
    monkeypatch, tmp_path,
):
    """With VESPERA_UNLOCK_HOLDOUT=1 the guard yields control; manifest
    absence then produces FileNotFoundError — NOT HoldoutLockError."""
    monkeypatch.setenv("VESPERA_UNLOCK_HOLDOUT", "1")
    # Point the adapter at an empty tmp manifest path.
    empty_manifest = tmp_path / "cache-manifest.csv"
    try:
        list(feed_cache.load_trades(
            _LOCKED_START, _LOCKED_END, "WDO",
            manifest_path=empty_manifest,
        ))
    except HoldoutLockError:
        pytest.fail(
            "feed_cache raised HoldoutLockError despite VESPERA_UNLOCK_HOLDOUT=1"
        )
    except FileNotFoundError:
        # Expected: no manifest at the tmp path.
        pass


# ---------------------------------------------------------------------------
# T4 — sha256 mismatch raises
# ---------------------------------------------------------------------------

def _write_tiny_cache_parquet(path: Path, ts: datetime) -> tuple[str, int]:
    """Write a 1-row cache parquet with the canonical 7-column schema.
    Returns (sha256, rows)."""
    import pandas as pd  # type: ignore[import-untyped]
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    from scripts.materialize_parquet import _build_parquet_schema, _sha256_file

    df = pd.DataFrame({
        "timestamp": [ts],
        "ticker": ["WDO"],
        "price": [5000.0],
        "qty": [1],
        "aggressor": ["BUY"],
        "buy_agent": ["A"],
        "sell_agent": ["B"],
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["qty"] = df["qty"].astype("int32")
    df["buy_agent"] = df["buy_agent"].astype("string")
    df["sell_agent"] = df["sell_agent"].astype("string")
    schema = _build_parquet_schema()
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        table, path, compression="snappy", row_group_size=100_000,
        use_dictionary=True, write_statistics=True, version="2.6",
        store_schema=True,
    )
    return _sha256_file(path), len(df)


def _write_cache_manifest(
    path: Path, parquet_path: Path, rows: int, sha256_val: str,
    start_ts: datetime, end_ts: datetime, ticker: str = "WDO",
) -> None:
    import os as _os
    from scripts.materialize_parquet import MANIFEST_COLUMNS, REPO_ROOT

    path.parent.mkdir(parents=True, exist_ok=True)
    rel = Path(_os.path.relpath(parquet_path, REPO_ROOT)).as_posix()
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(MANIFEST_COLUMNS), lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow({
            "path": rel,
            "rows": str(rows),
            "sha256": sha256_val,
            "start_ts_brt": start_ts.isoformat(),
            "end_ts_brt": end_ts.isoformat(),
            "ticker": ticker,
            "phase": "in_sample",
            "generated_at_brt": datetime.now().isoformat(timespec="seconds"),
        })


def test_feed_cache_sha256_mismatch_raises(tmp_path, monkeypatch):
    """A corrupted cache parquet surfaces as ValueError on read."""
    # Build a legit tiny cache under tmp_path rooted at REPO_ROOT-style layout.
    # The adapter relies on paths in the manifest being relative to REPO_ROOT,
    # so we trick it: monkeypatch REPO_ROOT to tmp_path.
    monkeypatch.setattr(feed_cache, "_REPO_ROOT", tmp_path)
    parquet = tmp_path / "data" / "cache" / "raw_trades" / "ticker=WDO" / \
              "year=2024" / "month=08" / "wdo-2024-08.parquet"
    ts = datetime(2024, 8, 1, 10, 0, 0)
    sha, rows = _write_tiny_cache_parquet(parquet, ts)

    # Manifest with CORRECT sha, then corrupt the file on disk (byte flip).
    manifest_path = tmp_path / "data" / "cache" / "cache-manifest.csv"
    # The adapter's _REPO_ROOT patch means the manifest row's relative path
    # must be relative to tmp_path for _REPO_ROOT / raw["path"] to resolve.
    # Use the real REPO_ROOT relpath logic (parquet lives under tmp_path /
    # data/cache/...) — manifest has that relative path.
    rel = parquet.relative_to(tmp_path).as_posix()

    with manifest_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "path", "rows", "sha256", "start_ts_brt", "end_ts_brt",
                "ticker", "phase", "generated_at_brt",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerow({
            "path": rel,
            "rows": str(rows),
            "sha256": sha,
            "start_ts_brt": ts.isoformat(),
            "end_ts_brt": ts.isoformat(),
            "ticker": "WDO",
            "phase": "in_sample",
            "generated_at_brt": datetime.now().isoformat(timespec="seconds"),
        })

    # Corrupt: append a spurious byte.
    with parquet.open("ab") as fh:
        fh.write(b"\x00")

    # Reset integrity cache to force recomputation.
    from packages.t002_eod_unwind.adapters import feed_parquet as fp
    fp._INTEGRITY_CACHE.clear()

    with pytest.raises(ValueError, match="sha256 mismatch"):
        list(feed_cache.load_trades(
            datetime(2024, 8, 1), datetime(2024, 8, 2), "WDO",
            manifest_path=manifest_path,
        ))


# ---------------------------------------------------------------------------
# T5 — missing manifest raises FileNotFoundError (before any parquet work)
# ---------------------------------------------------------------------------

def test_feed_cache_missing_manifest_raises_filenotfound(tmp_path):
    bogus = tmp_path / "does-not-exist" / "cache-manifest.csv"
    with pytest.raises(FileNotFoundError):
        list(feed_cache.load_trades(
            datetime(2024, 8, 1), datetime(2024, 8, 2), "WDO",
            manifest_path=bogus,
        ))


# ---------------------------------------------------------------------------
# Constitutional — schema parity with canonical (§9.5 / T16)
# ---------------------------------------------------------------------------

def test_cache_schema_identical_to_canonical():
    """Cache parquet schema MUST be the canonical _build_parquet_schema."""
    from scripts.materialize_parquet import _build_parquet_schema
    schema = _build_parquet_schema()
    names = [f.name for f in schema]
    assert names == [
        "timestamp", "ticker", "price", "qty",
        "aggressor", "buy_agent", "sell_agent",
    ], "Cache schema MUST mirror canonical (Article IV — No Invention)"
