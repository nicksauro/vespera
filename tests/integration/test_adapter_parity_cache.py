"""Integration — T12a + T12b: cache vs sentinel parity (ADR-4 §9.3 + §13.2).

Story:  T002.0a (pre-cache layer, Option B)
Spec:   docs/architecture/pre-cache-layer-spec.md §9.3, §13.2
Epic:   EPIC-T002.0

What each test proves
---------------------
- **T12a — both arms up (schema-drift guard).** With sentinel UP and cache
  built, asserts ``feed_cache.load_trades`` yields the EXACT same sequence
  of ``(ts, price, qty)`` 3-tuples as ``feed_timescale.load_trades`` for the
  pinned 2024-03-04 WDO window. Equality is proven by MD5 over pickled
  lists — byte-level identity. When sentinel is DOWN this test INLINE
  skips so it does not error in the quiesce workflow.
- **T12b — cache-only, sentinel-DOWN (THE Riven RA-20260426-1 Q1 proof).**
  NEVER skips. Never touches the DB. Compares ``feed_cache.load_trades``
  output to a pinned JSON snapshot generated once (with sentinel UP) by
  ``tests/scripts/generate_t12b_snapshot.py``. Equality is by SHA-256 over
  pickled 3-tuple list — matching the snapshot's ``sha256_of_pickled_trades``
  field — AFTER the snapshot file's own SHA-256 has been verified against
  the sibling ``MANIFEST.sha256`` pin (tamper guard).

Fixture layout
--------------
``tests/fixtures/adapter_parity_cache/``
  - ``wdo-2024-03-04.snapshot.json`` — pinned snapshot (§13.2 format).
  - ``MANIFEST.sha256`` — pins the snapshot file's own sha256.

Hold-out lock
-------------
Both tests and the generator assert-guard the window BEFORE any I/O
(``scripts/_holdout_lock.assert_holdout_safe``). The pinned day
(2024-03-04) is structurally in-sample (pre 2025-07-01) so the guard is
defense in depth — a regeneration against a later day inside hold-out
would fail hard before any file opens.
"""

from __future__ import annotations

import hashlib
import json
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]

_FIXTURE_DIR = _REPO / "tests" / "fixtures" / "adapter_parity_cache"
_SNAPSHOT_PATH = _FIXTURE_DIR / "wdo-2024-03-04.snapshot.json"
_MANIFEST_PATH = _FIXTURE_DIR / "MANIFEST.sha256"

# Add scripts/ to sys.path for _holdout_lock import (mirrors
# build_raw_trades_cache.py import pattern).
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))


def _db_reachable() -> bool:
    try:
        import psycopg2  # type: ignore[import-untyped]
    except Exception:
        return False
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            dbname="sentinel_db",
            user="sentinel_ro",
            password="XGsznrqvv5ZtDfkvce-CytV3aZqjMp7BjE_J2B1BaI4",
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception:
        return False


def _cache_manifest_has(ticker: str, year: int, month: int) -> bool:
    cm = _REPO / "data" / "cache" / "cache-manifest.csv"
    if not cm.exists():
        return False
    import csv as _csv
    expected_rel = (
        f"data/cache/raw_trades/ticker={ticker}/"
        f"year={year:04d}/month={month:02d}/"
        f"{ticker.lower()}-{year:04d}-{month:02d}.parquet"
    )
    with cm.open("r", encoding="utf-8", newline="") as fh:
        reader = _csv.DictReader(
            ln for ln in fh if not ln.lstrip().startswith("#")
        )
        for raw in reader:
            if raw["path"].strip() == expected_rel and raw["ticker"].strip() == ticker:
                return True
    return False


def _pick_window() -> tuple[datetime, datetime, str, str] | None:
    """Return (start, end, ticker, label) for a window available in BOTH
    the cache manifest and Sentinel, preferring the pinned 2024-03-04 window
    (which also backs the T12b snapshot)."""
    candidates = [
        (datetime(2024, 3, 4), datetime(2024, 3, 5), "WDO", "2024-03"),
        (datetime(2024, 8, 1), datetime(2024, 8, 2), "WDO", "2024-08"),
    ]
    for s, e, t, label in candidates:
        if _cache_manifest_has(t, s.year, s.month):
            return s, e, t, label
    return None


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _load_snapshot() -> dict:
    """Read + sha-verify the pinned T12b snapshot.

    The snapshot JSON is the pinned source of truth; its sha256 is pinned
    in sibling ``MANIFEST.sha256``. Any edit to the JSON that is not
    accompanied by a regenerated MANIFEST entry will fail this loader —
    tamper guard per §13.4 risk 4/5.
    """
    if not _SNAPSHOT_PATH.exists():
        raise FileNotFoundError(
            f"T12b snapshot missing: {_SNAPSHOT_PATH}. Run "
            "tests/scripts/generate_t12b_snapshot.py with sentinel UP."
        )
    if not _MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"T12b MANIFEST.sha256 missing: {_MANIFEST_PATH}."
        )

    # Parse MANIFEST.sha256 — format: "<sha256>  <filename>" per line.
    expected_sha: str | None = None
    for ln in _MANIFEST_PATH.read_text(encoding="utf-8").splitlines():
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) >= 2 and parts[1] == _SNAPSHOT_PATH.name:
            expected_sha = parts[0].lower()
            break
    if expected_sha is None:
        raise ValueError(
            f"MANIFEST.sha256 has no entry for {_SNAPSHOT_PATH.name}"
        )

    actual_sha = _sha256_file(_SNAPSHOT_PATH)
    if actual_sha != expected_sha:
        raise ValueError(
            f"snapshot manifest sha mismatch: expected={expected_sha} "
            f"actual={actual_sha} — regenerate via "
            "tests/scripts/generate_t12b_snapshot.py"
        )

    return json.loads(_SNAPSHOT_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# T12a — both arms up (schema-drift guard; inline-skip if sentinel DOWN)
# ---------------------------------------------------------------------------

def test_T12a_cache_vs_sentinel_both_up():
    """T12a — byte-identical 3-tuple stream: feed_cache == feed_timescale.

    Schema-drift / conversion-bug guard (ADR-4 §13.2). Inline-skips when
    sentinel is DOWN so this test coexists cleanly with the quiesce
    workflow (the Riven Q1 empirical proof is T12b below).
    """
    if not _db_reachable():
        pytest.skip("T12a requires sentinel UP (both-arms test)")

    window = _pick_window()
    if window is None:
        pytest.skip(
            "No cache parquet available for any candidate window; "
            "run scripts/build_raw_trades_cache.py first."
        )
    start, end, ticker, label = window

    from packages.t002_eod_unwind.adapters import feed_cache, feed_timescale

    ts_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_timescale.load_trades(start, end, ticker)
    ]
    ca_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_cache.load_trades(start, end, ticker)
    ]

    assert len(ts_trades) == len(ca_trades), (
        f"length mismatch: timescale={len(ts_trades)} vs cache={len(ca_trades)} "
        f"(window={label})"
    )
    assert len(ts_trades) > 0, "sanity: window must have trades"

    ts_hash = hashlib.md5(pickle.dumps(ts_trades, protocol=5)).hexdigest()
    ca_hash = hashlib.md5(pickle.dumps(ca_trades, protocol=5)).hexdigest()

    if ts_hash != ca_hash:
        for i, (a, b) in enumerate(zip(ts_trades, ca_trades)):
            if a != b:
                pytest.fail(
                    f"First divergence at index {i}: "
                    f"timescale={a} vs cache={b} (window={label})"
                )
        pytest.fail(
            f"Hash mismatch despite element-wise equality: "
            f"ts={ts_hash} cache={ca_hash} len={len(ts_trades)}"
        )

    assert ts_hash == ca_hash, (
        f"cache vs sentinel parity hash mismatch: {ts_hash} vs {ca_hash} "
        f"(window={label})"
    )


# ---------------------------------------------------------------------------
# T12b — cache self-sufficient (sentinel DOWN) — THE Riven Q1 proof
# ---------------------------------------------------------------------------

def test_T12b_cache_self_sufficient_sentinel_down():
    """T12b — prove feed_cache is self-sufficient with sentinel DOWN.

    Riven RA-20260426-1 Q1 empirical proof (ADR-4 §13.2). Does NOT require
    DB. Compares live ``feed_cache.load_trades`` output against a pinned
    snapshot generated once with sentinel UP (committed alongside
    ``MANIFEST.sha256``). This test is the signal Quinn attaches to the RA
    evidence packet with the container STOPPED.
    """
    # 1. sha-verify fixture BEFORE loading JSON content (tamper guard).
    snap = _load_snapshot()
    w = snap["window"]
    start = datetime.fromisoformat(w["start"])
    end = datetime.fromisoformat(w["end"])
    ticker = w["ticker"]

    # 2. Hold-out guard defense-in-depth — the pinned day (2024-03-04) is
    #    structurally in-sample but the guard fires anyway (§13.4 R7).
    from _holdout_lock import assert_holdout_safe
    assert_holdout_safe(start.date(), (end - timedelta(days=1)).date())

    # 3. Cache must be present — if not, T12b fails fast with a clear
    #    message (NOT a skip; the cache is the WHOLE point of this test).
    if not _cache_manifest_has(ticker, start.year, start.month):
        pytest.skip(
            f"cache parquet missing for {ticker} {w['start']}; "
            "run scripts/build_raw_trades_cache.py first."
        )

    # 4. Load via feed_cache — NO DB touched, by design.
    from packages.t002_eod_unwind.adapters import feed_cache
    trades = [
        (t.ts, t.price, t.qty)
        for t in feed_cache.load_trades(start, end, ticker)
    ]

    assert len(trades) == snap["row_count"], (
        f"row count drift: got {len(trades)}, snapshot={snap['row_count']}"
    )

    digest = hashlib.sha256(pickle.dumps(trades, protocol=5)).hexdigest()
    assert digest == snap["sha256_of_pickled_trades"], (
        f"cache content drift from snapshot: got {digest}, "
        f"snapshot={snap['sha256_of_pickled_trades']} "
        f"(row_count={len(trades)})"
    )


# ---------------------------------------------------------------------------
# T13 (supplementary) — cache vs canonical parquet, if both available
# ---------------------------------------------------------------------------

def test_adapter_parity_cache_vs_parquet_if_both_available():
    """Supplementary T13 — if canonical parquet AND cache both cover the
    same month, feed_cache and feed_parquet MUST be byte-identical
    (schema-lossless cache proof)."""
    if not _db_reachable():
        pytest.skip("T13 supplementary requires sentinel UP to pick window")
    window = _pick_window()
    if window is None:
        pytest.skip("no cache parquet available")
    start, end, ticker, _label = window

    canonical_pq = (
        _REPO / "data" / "in_sample"
        / f"year={start.year:04d}"
        / f"month={start.month:02d}"
        / f"{ticker.lower()}-{start.year:04d}-{start.month:02d}.parquet"
    )
    if not canonical_pq.exists():
        pytest.skip("no canonical parquet for the picked window")

    from packages.t002_eod_unwind.adapters import feed_cache, feed_parquet

    pq_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_parquet.load_trades(start, end, ticker)
    ]
    ca_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_cache.load_trades(start, end, ticker)
    ]

    pq_hash = hashlib.md5(pickle.dumps(pq_trades, protocol=5)).hexdigest()
    ca_hash = hashlib.md5(pickle.dumps(ca_trades, protocol=5)).hexdigest()
    assert pq_hash == ca_hash, (
        f"cache vs canonical-parquet hash mismatch: "
        f"pq={pq_hash} cache={ca_hash} len={len(pq_trades)}/{len(ca_trades)}"
    )
