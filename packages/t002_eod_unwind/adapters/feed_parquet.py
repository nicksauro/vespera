"""feed_parquet — hot-path adapter streaming trades from deterministic
monthly parquet files materialized by T002.0a.

Story:  T002.0b (T3)
Epic:   EPIC-T002.0
Owner:  Dex (@dev)
Spec:   docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml

Contract (same as feed_timescale — Aria AC1)
--------------------------------------------
``load_trades(start_brt, end_brt, ticker) -> Iterable[Trade]``

- ``start_brt`` inclusive, ``end_brt`` exclusive (BRT-naive ``datetime``).
- ``ticker`` whitelist ``{"WDO", "WIN"}``; ValueError otherwise.
- Yields ``Trade(ts, price, qty)`` — 3 fields only. Aggressor / agents are
  read from the parquet schema but discarded (non-load-bearing per Beckett
  2026-04-22). The discard is symmetric with feed_timescale (AC14 parity).
- Timestamps BRT-naive; runtime assert on first yield.

Hold-out lock
-------------
``assert_holdout_safe`` fires BEFORE any ``ParquetFile`` open (AC11).

Manifest discovery
------------------
Reads ``data/manifest.csv`` (canonical). If absent, falls back to
``data/manifest_PREVIEW.csv`` (dev fixture while PID 12608 is still
materializing) and logs a warning. Each parquet's sha256 is verified against
the manifest before the file is opened — integrity gate per AC7.

Window predicate pushdown
-------------------------
The manifest carries ``start_ts_brt`` / ``end_ts_brt`` per file, so we can
skip files that don't intersect ``[start_brt, end_brt)`` without opening
them. For the files that DO intersect, we stream row-batches via
``pyarrow.parquet.ParquetFile.iter_batches(batch_size=65536)`` (mmap,
zero-copy, no full materialization).

Per-row filtering within a batch is a simple numpy predicate — pyarrow's
full expression pushdown would require ``dataset.Dataset`` (overkill; we
already know which months matter from the manifest).
"""

from __future__ import annotations

import csv
import hashlib
import logging
import warnings
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..core.session_state import Trade
from ._holdout_lock import assert_holdout_safe

logger = logging.getLogger(__name__)

_ALLOWED_TICKERS = frozenset({"WDO", "WIN"})
_REPO_ROOT = Path(__file__).resolve().parents[3]
_MANIFEST_CANONICAL = _REPO_ROOT / "data" / "manifest.csv"
_MANIFEST_PREVIEW = _REPO_ROOT / "data" / "manifest_PREVIEW.csv"

_BATCH_SIZE = 65_536  # AC8

# Integrity cache — sha256 verification is O(file) and the parquet is
# immutable by contract (R15 append-only). Verifying once per process per
# file is correct: we're proving the file on disk matches the manifest for
# THIS run. Caching avoids a 40+ second hit per session in the CPCV hot
# loop when the same parquet backs hundreds of sessions.
_INTEGRITY_CACHE: dict[Path, str] = {}


@dataclass(frozen=True)
class _ManifestRow:
    path: Path
    rows: int
    sha256: str
    start_ts_brt: datetime
    end_ts_brt: datetime
    ticker: str
    phase: str


def _parse_manifest_ts(raw: str) -> datetime:
    """Parse an ISO-8601 BRT-naive timestamp string from the manifest."""
    ts = datetime.fromisoformat(raw)
    if ts.tzinfo is not None:
        raise ValueError(
            f"feed_parquet: manifest timestamp is tz-aware ({raw!r}); "
            "schema must be BRT-naive (R2)."
        )
    return ts


def _read_one_manifest(path: Path) -> list[_ManifestRow]:
    rows: list[_ManifestRow] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(
            # The PREVIEW manifest carries leading ``# ...`` comment lines
            # before the header; DictReader cannot handle them, so strip here.
            line for line in fh if not line.lstrip().startswith("#")
        )
        for raw in reader:
            rows.append(_ManifestRow(
                path=_REPO_ROOT / raw["path"],
                rows=int(raw["rows"]),
                sha256=raw["sha256"].strip().lower(),
                start_ts_brt=_parse_manifest_ts(raw["start_ts_brt"]),
                end_ts_brt=_parse_manifest_ts(raw["end_ts_brt"]),
                ticker=raw["ticker"].strip(),
                phase=raw["phase"].strip(),
            ))
    return rows


def _load_manifest_with_fallback() -> tuple[list[_ManifestRow], bool]:
    """Load manifest rows with canonical-over-PREVIEW merge semantics.

    Dev rationale (T3 note): while PID 12608 still materializes months,
    ``data/manifest.csv`` is partial (e.g. only Jan 2024 listed). The
    PREVIEW fixture ``data/manifest_PREVIEW.csv`` carries Jan 2024-Mar 2025
    so CPCV exploration can proceed. We merge: canonical entries WIN on
    path collision (canonical is authoritative for whatever it covers);
    PREVIEW fills the gaps. Returns ``(rows, used_preview)``.

    If neither manifest exists, raises FileNotFoundError.
    """
    canonical_rows: list[_ManifestRow] = []
    preview_rows: list[_ManifestRow] = []

    if _MANIFEST_CANONICAL.exists():
        canonical_rows = _read_one_manifest(_MANIFEST_CANONICAL)
    if _MANIFEST_PREVIEW.exists():
        preview_rows = _read_one_manifest(_MANIFEST_PREVIEW)

    if not canonical_rows and not preview_rows:
        raise FileNotFoundError(
            f"feed_parquet: neither {_MANIFEST_CANONICAL} nor "
            f"{_MANIFEST_PREVIEW} is usable. Run scripts/materialize_parquet.py."
        )

    # Merge: canonical wins on path collision.
    by_path: dict[Path, _ManifestRow] = {}
    used_preview = False
    for r in preview_rows:
        by_path[r.path] = r
        used_preview = True
    for r in canonical_rows:
        by_path[r.path] = r  # overwrite preview row
    # Consider preview "actually used" only if at least one PREVIEW row
    # survived the merge (wasn't shadowed by canonical).
    canonical_paths = {r.path for r in canonical_rows}
    preview_surviving = [r for r in preview_rows if r.path not in canonical_paths]
    if preview_surviving:
        warnings.warn(
            f"feed_parquet: using {len(preview_surviving)} row(s) from "
            f"manifest_PREVIEW.csv (non-custodial dev fixture). "
            f"Canonical manifest covers {len(canonical_rows)} file(s). "
            "This should NOT persist past T002.0a completion.",
            stacklevel=4,
        )
        logger.warning(
            "feed_parquet using %d PREVIEW rows (canonical=%d)",
            len(preview_surviving), len(canonical_rows),
        )
    else:
        used_preview = False

    return sorted(by_path.values(), key=lambda r: r.start_ts_brt), used_preview


def _intersects_window(
    row: _ManifestRow, start_brt: datetime, end_brt: datetime
) -> bool:
    """Closed/open interval intersection: [file_start, file_end] vs [start, end)."""
    return row.start_ts_brt < end_brt and row.end_ts_brt >= start_brt


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verify_integrity(row: _ManifestRow) -> None:
    """Compute sha256 and compare against manifest; raise if mismatch (AC7).

    Uses ``_INTEGRITY_CACHE`` so the full-file hash is paid at most once per
    process per file. The parquet is immutable by contract (R15), so this
    caching is semantically equivalent to per-call verification.
    """
    if not row.path.exists():
        raise FileNotFoundError(
            f"feed_parquet: parquet {row.path} listed in manifest but missing on disk"
        )
    cached = _INTEGRITY_CACHE.get(row.path)
    if cached is not None:
        if cached != row.sha256:
            # Manifest sha256 changed across calls with the same path — this
            # would imply the manifest was edited during the process lifetime,
            # which violates R15 append-only semantics.
            raise ValueError(
                f"feed_parquet: manifest sha256 for {row.path} changed "
                f"mid-process (cached={cached} vs new={row.sha256}). "
                "Manifest is append-only (R15)."
            )
        return
    digest = _sha256_file(row.path)
    if digest.lower() != row.sha256:
        raise ValueError(
            f"feed_parquet: sha256 mismatch for {row.path}: "
            f"manifest={row.sha256} disk={digest}"
        )
    _INTEGRITY_CACHE[row.path] = row.sha256


def _reset_integrity_cache() -> None:
    """Testing-only: clear the sha256 cache so a fresh cold measurement can
    be taken (e.g. pytest-benchmark fixture).
    """
    _INTEGRITY_CACHE.clear()


def _iter_parquet_rows(
    path: Path,
    start_brt: datetime,
    end_brt: datetime,
    tz_check_state: dict[str, bool],
) -> Iterator[Trade]:
    """Stream trades from ONE parquet file within [start_brt, end_brt).

    Reads only (timestamp, price, qty) — aggressor/agents are NOT loaded,
    matching feed_timescale (AC14 parity). Row-groups fully outside the
    window are skipped via parquet stats (cheap). Row-groups that overlap
    are filtered at the pyarrow compute level.
    """
    import pyarrow as pa  # type: ignore[import-untyped]
    import pyarrow.compute as pc  # type: ignore[import-untyped]
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    pf = pq.ParquetFile(path)
    schema = pf.schema_arrow
    timestamp_col_idx = schema.get_field_index("timestamp")

    # pyarrow scalars for filter — must match timestamp[ns] schema.
    start_scalar = pa.scalar(start_brt, type=pa.timestamp("ns"))
    end_scalar = pa.scalar(end_brt, type=pa.timestamp("ns"))

    # Local aliases — micro-opt for the hot yield loop.
    _Trade = Trade

    for rg_idx in range(pf.num_row_groups):
        rg_meta = pf.metadata.row_group(rg_idx)
        col_stats = rg_meta.column(timestamp_col_idx).statistics
        # Row-group skip: if stats say the entire group lies outside window.
        # Fully-inside fast path: if stats say the whole group lies within
        # [start_brt, end_brt), we can skip the per-row filter compute.
        fully_inside = False
        if col_stats is not None and col_stats.has_min_max:
            rg_min = col_stats.min
            rg_max = col_stats.max
            # Stats come as stdlib datetime.
            if rg_max < start_brt or rg_min >= end_brt:
                continue
            if rg_min >= start_brt and rg_max < end_brt:
                fully_inside = True

        # Read this row-group's 3 columns (mmap'd — no full-table load).
        table = pf.read_row_group(
            rg_idx, columns=["timestamp", "price", "qty"]
        )

        if not tz_check_state["checked"]:
            if table.schema.field(0).type.tz is not None:
                raise AssertionError(
                    f"feed_parquet: tz-aware timestamp in {path} "
                    f"(type={table.schema.field(0).type}); schema must "
                    "be BRT-naive (R2)."
                )
            tz_check_state["checked"] = True

        if table.num_rows == 0:
            continue

        if fully_inside:
            filtered = table
        else:
            # Partial overlap — filter this row-group (one compute, no batching).
            ts_array = table.column(0)
            mask = pc.and_(
                pc.greater_equal(ts_array, start_scalar),
                pc.less(ts_array, end_scalar),
            )
            if not pc.any(mask).as_py():
                continue
            filtered = table.filter(mask)

        # Hot-path materialization (the 10s bottleneck on 854k rows).
        #
        # `to_pylist()` on a timestamp[ns] ChunkedArray boxes each element
        # into a pandas.Timestamp (not stdlib datetime — pyarrow delegates
        # to pandas when available). That is slow (~10s / 854k rows) AND
        # breaks AC14 parity (feed_timescale yields stdlib datetime via
        # psycopg2).
        #
        # Fix: pull the column via numpy (datetime64[ns], zero-copy), then
        # bulk-cast to datetime64[us] -> object via numpy's C path, and
        # finally `.tolist()` to get stdlib `datetime.datetime` objects.
        # ~35x faster than `to_pylist()` on timestamps, and parity-correct.
        #
        # Casting ns -> us truncates sub-microsecond precision, which is
        # the same behavior psycopg2 exhibits for TIMESTAMP WITHOUT TIME
        # ZONE (Postgres itself stores microseconds), so AC14 parity is
        # preserved end-to-end.
        ts_np = filtered.column(0).to_numpy(zero_copy_only=False)
        ts_py = ts_np.astype("datetime64[us]").astype(object).tolist()
        # For float/int columns, to_numpy().tolist() is 2-3x faster than
        # to_pylist() because the C cast is vectorized.
        price_py = filtered.column(1).to_numpy(zero_copy_only=False).tolist()
        qty_py = filtered.column(2).to_numpy(zero_copy_only=False).tolist()

        # `map(Trade, ...)` pushes per-row construction into C (builtin
        # map), saving several seconds vs a Python for-loop.
        yield from map(_Trade, ts_py, price_py, qty_py)


def load_trades(
    start_brt: datetime,
    end_brt: datetime,
    ticker: str,
) -> Iterable[Trade]:
    """Stream ``Trade`` rows from the parquet manifest for ``[start_brt, end_brt)``.

    Raises
    ------
    ValueError
        Ticker not in whitelist / tz-aware inputs / manifest sha256 mismatch.
    HoldoutLockError
        Window intersects pre-registered hold-out without unlock flag. Fires
        BEFORE the manifest is read or any parquet is opened (AC11).
    FileNotFoundError
        Manifest (canonical + preview) absent, or a listed parquet is missing.
    """
    # --- 1. Input validation ---------------------------------------------
    if ticker not in _ALLOWED_TICKERS:
        raise ValueError(
            f"ticker must be one of {sorted(_ALLOWED_TICKERS)}; got {ticker!r}"
        )
    if start_brt.tzinfo is not None or end_brt.tzinfo is not None:
        raise ValueError(
            "feed_parquet: start_brt and end_brt must be BRT-naive (tzinfo=None)"
        )
    if not start_brt < end_brt:
        raise ValueError(
            f"feed_parquet: start_brt ({start_brt}) must be < end_brt ({end_brt})"
        )

    # --- 2. Hold-out guard BEFORE any I/O (AC11) --------------------------
    from datetime import timedelta
    end_inclusive = end_brt - timedelta(microseconds=1)
    assert_holdout_safe(start_brt.date(), end_inclusive.date())

    # --- 3. Manifest locate + read (canonical with PREVIEW fallback) -----
    all_rows, _used_preview = _load_manifest_with_fallback()

    # --- 4. Filter by ticker + window ------------------------------------
    relevant = [
        r for r in all_rows
        if r.ticker == ticker and _intersects_window(r, start_brt, end_brt)
    ]
    # Deterministic order — by start_ts_brt (file ranges are non-overlapping
    # for a given ticker since they are monthly partitions).
    relevant.sort(key=lambda r: r.start_ts_brt)

    return _stream(relevant, start_brt, end_brt)


def _stream(
    rows: list[_ManifestRow],
    start_brt: datetime,
    end_brt: datetime,
) -> Iterator[Trade]:
    tz_check_state = {"checked": False}
    for row in rows:
        _verify_integrity(row)
        yield from _iter_parquet_rows(row.path, start_brt, end_brt, tz_check_state)


__all__ = ["load_trades"]
