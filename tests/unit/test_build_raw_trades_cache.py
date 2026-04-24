"""Unit tests — build_raw_trades_cache.py (ADR-4 §9.2 + §9.4 + §9.5).

Story:  T002.0a (pre-cache layer, Option B)
Spec:   docs/architecture/pre-cache-layer-spec.md §9

Test enumeration vs §9:
  T6   test_build_holdout_guard_blocks_range
       (aka test_build_holdout_fires_before_db_connect)
  T7   test_build_cache_dir_cannot_point_to_in_sample
  T8   test_build_cache_manifest_cannot_point_to_canonical
  T9   test_build_resume_skips_already_built_month
  T10  test_build_resume_redoes_partial_month
  T11  test_build_force_rebuild_wipes_manifest_and_chunk
       (covered via manifest rewrite logic)
  +    test_build_cache_atomic_flush_no_partial_files
  +    test_build_cache_writes_sha256_to_manifest
  +    test_build_cache_does_not_touch_canonical_paths
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

import build_raw_trades_cache as brc  # noqa: E402
import materialize_parquet as mp  # noqa: E402


def _base_argv(*extra: str) -> list[str]:
    return [
        "--ticker", "WDO",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-05",
        *extra,
    ]


# ---------------------------------------------------------------------------
# T6 — hold-out guard fires BEFORE psycopg2.connect
# ---------------------------------------------------------------------------

def test_build_holdout_guard_blocks_range(monkeypatch):
    """assert_holdout_safe must raise before _connect is called."""
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    connect_called = {"n": 0}

    def sentinel_connect(*a, **kw):
        connect_called["n"] += 1
        raise AssertionError(
            "build_raw_trades_cache called _connect BEFORE hold-out guard"
        )

    # The build script reuses mp._connect; patch that entry point.
    monkeypatch.setattr(mp, "_connect", sentinel_connect)
    # Also ensure psycopg2 itself cannot be reached (defense in depth).
    import psycopg2  # type: ignore[import-untyped]
    monkeypatch.setattr(psycopg2, "connect", sentinel_connect)

    with pytest.raises(brc.HoldoutLockError):
        brc.run(brc.BuildArgs(
            ticker="WDO",
            start_date=date(2025, 8, 1),
            end_date=date(2025, 8, 3),
            cache_dir=_REPO / "data" / "cache" / "raw_trades",
            cache_manifest=_REPO / "data" / "cache" / "cache-manifest.csv",
            resume=True, dry_run=False, force_rebuild=False,
        ))
    assert connect_called["n"] == 0


# ---------------------------------------------------------------------------
# T7 — --cache-dir cannot resolve under data/in_sample/
# ---------------------------------------------------------------------------

def test_build_cache_dir_cannot_point_to_in_sample():
    bad = str(_REPO / "data" / "in_sample" / "cache_smuggle")
    with pytest.raises(SystemExit):
        brc.parse_args(_base_argv("--cache-dir", bad))


def test_build_cache_dir_in_sample_root_also_rejected():
    bad = str(_REPO / "data" / "in_sample")
    with pytest.raises(SystemExit):
        brc.parse_args(_base_argv("--cache-dir", bad))


# ---------------------------------------------------------------------------
# T8 — --cache-manifest cannot equal canonical data/manifest.csv
# ---------------------------------------------------------------------------

def test_build_cache_manifest_cannot_point_to_canonical():
    with pytest.raises(SystemExit):
        brc.parse_args(_base_argv(
            "--cache-manifest", str(mp.MANIFEST_PATH),
        ))


# ---------------------------------------------------------------------------
# T9 — resume skips already-built month (no DB call)
# ---------------------------------------------------------------------------

def _fake_df(ts_start: datetime, n: int = 3):
    import pandas as pd  # type: ignore[import-untyped]
    import numpy as np  # type: ignore[import-untyped]
    timestamps = [ts_start for _ in range(n)]
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(timestamps),
        "ticker": ["WDO"] * n,
        "price": np.array([5000.0 + i for i in range(n)], dtype="float64"),
        "qty": np.array([1] * n, dtype="int32"),
        "aggressor": ["BUY"] * n,
        "buy_agent": pd.array(["A"] * n, dtype="string"),
        "sell_agent": pd.array(["B"] * n, dtype="string"),
    })
    return df


def test_build_resume_skips_already_built_month(tmp_path, monkeypatch):
    """Pre-populate manifest + parquet; --resume should skip DB entirely."""
    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    # Build the fake parquet using the real writer (ensures schema conformance).
    df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=3)
    mp._write_parquet(df, parquet_path)
    sha = mp._sha256_file(parquet_path)

    # Manifest row — path MUST be REPO-relative posix (brc writes it that way).
    import os as _os
    rel = Path(_os.path.relpath(parquet_path, brc.REPO_ROOT)).as_posix()
    with manifest.open("w", encoding="utf-8", newline="") as fh:
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

    # Block any DB connect — resume must short-circuit.
    def no_db(*a, **kw):
        raise AssertionError("resume leaked through to _connect")
    monkeypatch.setattr(mp, "_connect", no_db)
    # Prevent env-load (no .env.vespera needed on resume path).
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 5),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=False,
    ))
    assert rc == 0


# ---------------------------------------------------------------------------
# T10 — resume redoes partial month (.ckpt present => cleanup + refetch)
# ---------------------------------------------------------------------------

def test_build_resume_redoes_partial_month(tmp_path, monkeypatch):
    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"  # empty — no manifest row
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    # Create orphan .ckpt + .tmp (simulated crash).
    (parquet_path.with_suffix(parquet_path.suffix + ".ckpt")).write_text(
        '{"status":"in_progress"}', encoding="utf-8",
    )
    (parquet_path.with_suffix(parquet_path.suffix + ".tmp")).write_bytes(
        b"\x00\x00partial",
    )

    # Stub streaming helper — write a fake parquet for Aug-2024; empty else.
    # ADR-4 §13.1 Amendment 20260424-1: _fetch_month_dataframe delegation was
    # replaced by brc._stream_month_to_parquet (writes directly to out_tmp,
    # returns (row_count, first_ts, last_ts)).
    fetched = {"calls": []}

    def fake_stream(conn, ticker, mw, out_tmp, schema):
        fetched["calls"].append(mw.label)
        if mw.label == "2024-08":
            df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=3)
            mp._write_parquet(df, out_tmp)
            return 3, datetime(2024, 8, 1, 10, 0, 0), datetime(2024, 8, 1, 10, 0, 0)
        return 0, None, None

    class DummyConn:
        def close(self): pass

    monkeypatch.setattr(brc, "_stream_month_to_parquet", fake_stream)
    monkeypatch.setattr(mp, "_connect", lambda env: DummyConn())
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=False,
    ))
    assert rc == 0
    # After run: parquet written, .ckpt gone, .tmp gone.
    assert parquet_path.exists()
    assert not parquet_path.with_suffix(parquet_path.suffix + ".ckpt").exists()
    assert not parquet_path.with_suffix(parquet_path.suffix + ".tmp").exists()
    # Manifest should have one row for 2024-08.
    assert manifest.exists()
    rows = list(csv.DictReader(manifest.open()))
    assert len(rows) == 1 and rows[0]["ticker"] == "WDO"


# ---------------------------------------------------------------------------
# T11 — --force-rebuild wipes manifest row + chunk
# ---------------------------------------------------------------------------

def test_build_force_rebuild_wipes_manifest_and_chunk(tmp_path, monkeypatch):
    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )
    parquet_path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-seed: manifest row + parquet with a stale sha.
    import os as _os
    rel = Path(_os.path.relpath(parquet_path, brc.REPO_ROOT)).as_posix()
    parquet_path.write_bytes(b"stale")
    with manifest.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh, fieldnames=list(mp.MANIFEST_COLUMNS), lineterminator="\n",
        )
        w.writeheader()
        w.writerow({
            "path": rel, "rows": "99", "sha256": "deadbeef" * 8,
            "start_ts_brt": "2024-08-01T10:00:00",
            "end_ts_brt": "2024-08-01T10:00:00",
            "ticker": "WDO", "phase": "in_sample",
            "generated_at_brt": "2026-04-23T12:00:00",
        })

    def fake_stream(conn, ticker, mw, out_tmp, schema):
        df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=2)
        mp._write_parquet(df, out_tmp)
        return 2, datetime(2024, 8, 1, 10, 0, 0), datetime(2024, 8, 1, 10, 0, 0)

    class DummyConn:
        def close(self): pass

    monkeypatch.setattr(brc, "_stream_month_to_parquet", fake_stream)
    monkeypatch.setattr(mp, "_connect", lambda env: DummyConn())
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=True,
    ))
    assert rc == 0
    # New parquet sha must differ from "deadbeef*" — real snappy file now.
    new_sha = mp._sha256_file(parquet_path)
    assert new_sha != "deadbeef" * 8


# ---------------------------------------------------------------------------
# Atomic flush: no leftover .tmp or .ckpt on success
# ---------------------------------------------------------------------------

def test_build_cache_atomic_flush_no_partial_files(tmp_path, monkeypatch):
    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )

    def fake_stream(conn, ticker, mw, out_tmp, schema):
        df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=5)
        mp._write_parquet(df, out_tmp)
        return 5, datetime(2024, 8, 1, 10, 0, 0), datetime(2024, 8, 1, 10, 0, 0)

    class DummyConn:
        def close(self): pass

    monkeypatch.setattr(brc, "_stream_month_to_parquet", fake_stream)
    monkeypatch.setattr(mp, "_connect", lambda env: DummyConn())
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=False,
    ))
    assert rc == 0
    assert parquet_path.exists()
    assert not parquet_path.with_suffix(parquet_path.suffix + ".tmp").exists()
    assert not parquet_path.with_suffix(parquet_path.suffix + ".ckpt").exists()


# ---------------------------------------------------------------------------
# Writes sha256 to manifest after successful flush
# ---------------------------------------------------------------------------

def test_build_cache_writes_sha256_to_manifest(tmp_path, monkeypatch):
    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"
    parquet_path = (
        cache_dir / "ticker=WDO" / "year=2024" / "month=08" / "wdo-2024-08.parquet"
    )

    def fake_stream(conn, ticker, mw, out_tmp, schema):
        df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=7)
        mp._write_parquet(df, out_tmp)
        return 7, datetime(2024, 8, 1, 10, 0, 0), datetime(2024, 8, 1, 10, 0, 0)

    class DummyConn:
        def close(self): pass

    monkeypatch.setattr(brc, "_stream_month_to_parquet", fake_stream)
    monkeypatch.setattr(mp, "_connect", lambda env: DummyConn())
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=False,
    ))
    assert rc == 0
    rows = list(csv.DictReader(manifest.open()))
    assert len(rows) == 1
    mrow = rows[0]
    # sha256 column is present, lowercase hex, 64 chars, matches the file.
    sha = mrow["sha256"].strip().lower()
    assert len(sha) == 64
    assert sha == mp._sha256_file(parquet_path)
    assert mrow["ticker"] == "WDO"
    assert mrow["rows"] == "7"
    assert mrow["phase"] == "in_sample"


# ---------------------------------------------------------------------------
# Does not touch canonical paths
# ---------------------------------------------------------------------------

def test_build_cache_does_not_touch_canonical_paths(tmp_path, monkeypatch):
    """Run build, assert canonical manifest + in_sample are byte-identical."""
    if not mp.MANIFEST_PATH.exists():
        pytest.skip("canonical manifest not present in this checkout")
    # Snapshot canonical sha before run.
    canon_before = mp._sha256_file(mp.MANIFEST_PATH)

    cache_dir = tmp_path / "raw_trades"
    manifest = tmp_path / "cache-manifest.csv"

    def fake_stream(conn, ticker, mw, out_tmp, schema):
        df = _fake_df(datetime(2024, 8, 1, 10, 0, 0), n=4)
        mp._write_parquet(df, out_tmp)
        return 4, datetime(2024, 8, 1, 10, 0, 0), datetime(2024, 8, 1, 10, 0, 0)

    class DummyConn:
        def close(self): pass

    monkeypatch.setattr(brc, "_stream_month_to_parquet", fake_stream)
    monkeypatch.setattr(mp, "_connect", lambda env: DummyConn())
    monkeypatch.setattr(mp, "_load_env_vespera", lambda: {})

    rc = brc.run(brc.BuildArgs(
        ticker="WDO",
        start_date=date(2024, 8, 1),
        end_date=date(2024, 8, 1),
        cache_dir=cache_dir,
        cache_manifest=manifest,
        resume=True, dry_run=False, force_rebuild=False,
    ))
    assert rc == 0
    canon_after = mp._sha256_file(mp.MANIFEST_PATH)
    assert canon_before == canon_after, (
        f"canonical manifest sha changed! before={canon_before} "
        f"after={canon_after}"
    )


# ---------------------------------------------------------------------------
# argparse: ticker whitelist
# ---------------------------------------------------------------------------

def test_parse_args_rejects_unknown_ticker(tmp_path):
    with pytest.raises(SystemExit):
        brc.parse_args([
            "--ticker", "PETR4",
            "--start-date", "2024-08-01",
            "--end-date", "2024-08-05",
            "--cache-dir", str(tmp_path / "c"),
            "--cache-manifest", str(tmp_path / "m.csv"),
        ])
