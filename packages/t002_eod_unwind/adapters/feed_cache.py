"""feed_cache — cache-read adapter streaming trades from the local pre-cache
layer materialized by ``scripts/build_raw_trades_cache.py``.

Story:  T002.0a (ADR-4, Option B pre-cache layer)
Epic:   EPIC-T002.0
Owner:  Dex (@dev)
Spec:   docs/architecture/pre-cache-layer-spec.md §6, §10

Contract (identical to ``feed_timescale`` / ``feed_parquet`` — AC14 parity)
---------------------------------------------------------------------------
``load_trades(start_brt, end_brt, ticker) -> Iterable[Trade]``

- ``start_brt`` inclusive, ``end_brt`` exclusive (BRT-naive ``datetime``).
- ``ticker`` whitelist ``{"WDO", "WIN"}``; ValueError otherwise.
- Yields ``Trade(ts, price, qty)`` — 3 fields only (aggressor/agents are
  read from the cache parquet schema but discarded, matching feed_parquet).
- Timestamps BRT-naive; runtime assert on first yield.

Hold-out lock (ADR-4 §8.2)
--------------------------
``assert_holdout_safe`` fires BEFORE any file open or manifest read — strict
ordering per AC11 (sentinel-patched ``pq.ParquetFile`` verifies zero opens
on a locked window).

Manifest
--------
Reads ``data/cache/cache-manifest.csv`` (ADR-4 §7; mirror of canonical
``data/manifest.csv`` column layout but explicitly NON-canonical).
``FileNotFoundError`` if the manifest is missing. Each parquet's sha256 is
verified against the manifest before the file is opened — integrity gate
shared verbatim with ``feed_parquet._verify_integrity`` via delegation.

Hot-path reuse (ADR-4 §6.2)
---------------------------
This module is intentionally thin: the actual parquet iteration reuses
``feed_parquet._iter_parquet_rows`` unchanged. No duplicated streaming /
numpy fast-path code. See ADR-4 §Appendix A trace row "AC14 parity test
pattern".
"""

from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta
from pathlib import Path

from ..core.session_state import Trade
from ._holdout_lock import assert_holdout_safe
from . import feed_parquet as _fp  # delegation — see module docstring

_ALLOWED_TICKERS = frozenset({"WDO", "WIN"})
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CACHE_MANIFEST = _REPO_ROOT / "data" / "cache" / "cache-manifest.csv"
_CACHE_DIR = _REPO_ROOT / "data" / "cache" / "raw_trades"


def _read_cache_manifest(path: Path) -> list[_fp._ManifestRow]:
    """Parse the cache-manifest CSV into ``_fp._ManifestRow`` records.

    Shares the same 8-column format as the canonical manifest
    (``scripts/materialize_parquet.py:MANIFEST_COLUMNS``); the cache-
    manifest lives at a different path on purpose (ADR-4 §7.1).
    """
    if not path.exists():
        raise FileNotFoundError(
            f"feed_cache: cache-manifest {path} not found. "
            "Run scripts/build_raw_trades_cache.py first."
        )
    rows: list[_fp._ManifestRow] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(
            line for line in fh if not line.lstrip().startswith("#")
        )
        for raw in reader:
            rows.append(_fp._ManifestRow(
                path=_REPO_ROOT / raw["path"],
                rows=int(raw["rows"]),
                sha256=raw["sha256"].strip().lower(),
                start_ts_brt=_fp._parse_manifest_ts(raw["start_ts_brt"]),
                end_ts_brt=_fp._parse_manifest_ts(raw["end_ts_brt"]),
                ticker=raw["ticker"].strip(),
                phase=raw["phase"].strip(),
            ))
    return rows


def load_trades(
    start_brt: datetime,
    end_brt: datetime,
    ticker: str,
    *,
    manifest_path: Path | None = None,
) -> Iterable[Trade]:
    """Stream ``Trade`` rows from the local cache for ``[start_brt, end_brt)``.

    Raises
    ------
    ValueError
        Ticker not in whitelist / tz-aware inputs / manifest sha256 mismatch.
    HoldoutLockError
        Window intersects pre-registered hold-out without unlock flag. Fires
        BEFORE the manifest is read or any parquet is opened (AC11).
    FileNotFoundError
        Cache manifest absent or a listed parquet is missing.
    """
    # --- 1. Input validation ---------------------------------------------
    if ticker not in _ALLOWED_TICKERS:
        raise ValueError(
            f"ticker must be one of {sorted(_ALLOWED_TICKERS)}; got {ticker!r}"
        )
    if start_brt.tzinfo is not None or end_brt.tzinfo is not None:
        raise ValueError(
            "feed_cache: start_brt and end_brt must be BRT-naive (tzinfo=None)"
        )
    if not start_brt < end_brt:
        raise ValueError(
            f"feed_cache: start_brt ({start_brt}) must be < end_brt ({end_brt})"
        )

    # --- 2. Hold-out guard BEFORE any I/O (AC11, ADR-4 §8.2) --------------
    end_inclusive = end_brt - timedelta(microseconds=1)
    assert_holdout_safe(start_brt.date(), end_inclusive.date())

    # --- 3. Manifest load (cache-specific path) ---------------------------
    mpath = manifest_path if manifest_path is not None else _CACHE_MANIFEST
    all_rows = _read_cache_manifest(mpath)

    # --- 4. Filter by ticker + window intersection ------------------------
    relevant = [
        r for r in all_rows
        if r.ticker == ticker and _fp._intersects_window(r, start_brt, end_brt)
    ]
    relevant.sort(key=lambda r: r.start_ts_brt)

    return _stream(relevant, start_brt, end_brt)


def _stream(
    rows: list[_fp._ManifestRow],
    start_brt: datetime,
    end_brt: datetime,
) -> Iterator[Trade]:
    """Yield trades from every relevant cache parquet, post-integrity-verify."""
    tz_check_state = {"checked": False}
    for row in rows:
        _fp._verify_integrity(row)
        yield from _fp._iter_parquet_rows(
            row.path, start_brt, end_brt, tz_check_state,
        )


__all__ = ["load_trades"]
