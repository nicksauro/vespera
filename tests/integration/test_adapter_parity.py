"""Integration test — feed_timescale and feed_parquet produce IDENTICAL streams (AC14).

Story: T002.0b (T5)
Epic:  EPIC-T002.0

What this proves
----------------
For the same window and ticker, both adapters emit the EXACT same sequence
of ``Trade(ts, price, qty)`` tuples in the SAME order. We compare via MD5
of a pickled list of 3-tuples — byte-level identity. If the adapters
diverge (missing/extra rows, reordering, float precision, etc.) the hashes
differ and the test fails.

Window
------
``2024-03-04 00:00 .. 2024-03-05 00:00`` — one WDO session (~314k trades
per prior smoke test). Small enough to be reasonable in CI, large enough
to exercise every batch boundary and the sha256 integrity path.

Preconditions
-------------
- TimescaleDB container ``sentinel-timescaledb`` UP on ``localhost:5433``
  with the ``sentinel_ro`` role able to read ``trades``.
- ``data/in_sample/year=2024/month=03/wdo-2024-03.parquet`` present AND
  listed in either ``manifest.csv`` or ``manifest_PREVIEW.csv``.

If either precondition is missing, the test is skipped (not failed) —
this is an integration test that needs a real environment.
"""

from __future__ import annotations

import hashlib
import pickle
from datetime import datetime
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]

_START = datetime(2024, 3, 4)
_END = datetime(2024, 3, 5)
_TICKER = "WDO"


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


def _parquet_available() -> bool:
    expected = _REPO / "data" / "in_sample" / "year=2024" / "month=03" / "wdo-2024-03.parquet"
    return expected.exists()


@pytest.mark.skipif(not _db_reachable(), reason="Sentinel TimescaleDB not reachable on :5433")
@pytest.mark.skipif(not _parquet_available(), reason="2024-03 parquet not materialized")
def test_adapter_parity_2024_03_04():
    """AC14: feed_timescale and feed_parquet produce byte-identical streams.

    A 3-tuple (ts, price, qty) list is collected from each adapter, pickled,
    and MD5-hashed. Hashes must match.
    """
    from packages.t002_eod_unwind.adapters import feed_parquet, feed_timescale

    ts_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_timescale.load_trades(_START, _END, _TICKER)
    ]
    pq_trades = [
        (t.ts, t.price, t.qty)
        for t in feed_parquet.load_trades(_START, _END, _TICKER)
    ]

    assert len(ts_trades) == len(pq_trades), (
        f"length mismatch: timescale={len(ts_trades)} vs parquet={len(pq_trades)}"
    )
    assert len(ts_trades) > 0, "sanity: window must have trades"

    # MD5 over pickled list of 3-tuples — byte-level identity proof.
    ts_hash = hashlib.md5(pickle.dumps(ts_trades, protocol=5)).hexdigest()
    pq_hash = hashlib.md5(pickle.dumps(pq_trades, protocol=5)).hexdigest()

    if ts_hash != pq_hash:
        # Diagnostics: find first divergence index.
        for i, (a, b) in enumerate(zip(ts_trades, pq_trades)):
            if a != b:
                pytest.fail(
                    f"First divergence at index {i}: "
                    f"timescale={a} vs parquet={b}"
                )
        pytest.fail(
            f"Hash mismatch despite element-wise equality: "
            f"ts={ts_hash} pq={pq_hash} (len={len(ts_trades)})"
        )

    assert ts_hash == pq_hash, f"parity hash mismatch: {ts_hash} vs {pq_hash}"
