"""feed_timescale — slow-path adapter streaming trades from the Sentinel
TimescaleDB via the read-only ``sentinel_ro`` role.

Story:  T002.0b (T2)
Epic:   EPIC-T002.0
Owner:  Dex (@dev)
Spec:   docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml

Contract
--------
``load_trades(start_brt, end_brt, ticker) -> Iterable[Trade]``

- ``start_brt`` inclusive, ``end_brt`` exclusive (BRT-naive ``datetime``).
- ``ticker`` must be in the whitelist ``{"WDO", "WIN"}``; ValueError otherwise.
- Yields ``Trade(ts, price, qty)`` — the 3-field public type defined in
  ``core/session_state.py:20``. Aggressor / ticker / agents are **not**
  materialized into the stream (Beckett 2026-04-22, spec v0.2.0 CPCV feature
  set).
- Timestamps are BRT-naive — a runtime assert on the first yield verifies
  ``trade.ts.tzinfo is None``.
- Ordered ascending by ``ts``. No dedupe. Empty iterator is valid.

Hold-out lock
-------------
``assert_holdout_safe(start.date(), (end - 1us).date())`` fires BEFORE any
call to ``psycopg2.connect``. This is a hard contract verified by the T4
adapter lock tests (AC11/AC12).

Server-side streaming
---------------------
Uses a named server-side cursor (``conn.cursor(name='ts_stream')``) with
``itersize=100_000`` so a single session (~500k-850k trades WDO) never
materializes as a Python list. Rows flow trade-by-trade out of the iterator.

Credentials
-----------
Read from ``.env.vespera`` (loaded via ``os.environ`` after a lightweight
dotenv parse). Fail-fast if any ``VESPERA_DB_*`` is missing.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..core.session_state import Trade
from ._holdout_lock import assert_holdout_safe

# Whitelist per AC2. ValueError otherwise.
_ALLOWED_TICKERS = frozenset({"WDO", "WIN"})

# Single source of truth for the SQL query (AC4). 3 columns only — aggressor
# and agents stay custodial in the parquet layer, not in the CPCV stream.
_QUERY = (
    "SELECT timestamp, price, qty FROM trades "
    "WHERE ticker = %s AND timestamp >= %s AND timestamp < %s "
    "ORDER BY timestamp ASC"
)

_REQUIRED_ENV_KEYS: tuple[str, ...] = (
    "VESPERA_DB_HOST",
    "VESPERA_DB_PORT",
    "VESPERA_DB_NAME",
    "VESPERA_DB_USER",
    "VESPERA_DB_PASSWORD",
)

_REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_env_vespera() -> dict[str, str]:
    """Parse ``.env.vespera`` and merge with ``os.environ`` (env wins).

    This mirrors the behavior of ``scripts.materialize_parquet._load_env_vespera``
    but prefers values already present in ``os.environ`` so tests can override
    via ``monkeypatch.setenv`` without having to write a fixture file.
    """
    import os

    merged: dict[str, str] = {}
    env_path = _REPO_ROOT / ".env.vespera"
    if env_path.exists():
        for raw in env_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            merged[k.strip()] = v.strip()
    # os.environ overrides the file — allows CI and tests to substitute.
    for key in _REQUIRED_ENV_KEYS:
        val = os.environ.get(key)
        if val is not None:
            merged[key] = val
    return merged


def _require_env(env: dict[str, str]) -> None:
    missing = [k for k in _REQUIRED_ENV_KEYS if not env.get(k)]
    if missing:
        raise ValueError(
            f"feed_timescale: missing required env vars {missing}. "
            "Populate .env.vespera or export the vars."
        )


def _connect(env: dict[str, str]) -> Any:
    """Open a psycopg2 connection to the Sentinel DB.

    Mirrors the hardening from ``scripts.materialize_parquet._connect`` in
    spirit (read-only session) but does NOT re-implement sanitization —
    adapters do not log connection errors upstream; any driver error
    propagates as-is to the caller (CPCV harness).
    """
    import psycopg2  # type: ignore[import-untyped]

    return psycopg2.connect(
        host=env["VESPERA_DB_HOST"],
        port=int(env["VESPERA_DB_PORT"]),
        dbname=env["VESPERA_DB_NAME"],
        user=env["VESPERA_DB_USER"],
        password=env["VESPERA_DB_PASSWORD"],
        options="-c default_transaction_read_only=on",
    )


def _iter_rows(
    conn: Any, ticker: str, start_brt: datetime, end_brt: datetime
) -> Iterator[Trade]:
    """Drain the server-side cursor, yielding ``Trade`` per row.

    Runtime invariants:
      - First row's ``ts.tzinfo`` is None (BRT-naive, R2).
      - Cursor is closed in ``finally`` even if consumer short-circuits.
    """
    tz_checked = False
    cur = conn.cursor(name="ts_stream")
    try:
        cur.itersize = 100_000
        cur.execute(_QUERY, (ticker, start_brt, end_brt))
        for row in cur:
            ts, price, qty = row[0], row[1], row[2]
            if not tz_checked:
                if getattr(ts, "tzinfo", None) is not None:
                    raise AssertionError(
                        f"feed_timescale: tz-aware timestamp received ({ts!r}); "
                        "Sentinel schema is BRT-naive (R2). Aborting."
                    )
                tz_checked = True
            # psycopg2 returns Decimal for NUMERIC price — coerce to float for
            # parity with feed_parquet. qty is INT already.
            yield Trade(ts=ts, price=float(price), qty=int(qty))
    finally:
        try:
            cur.close()
        except Exception:
            pass


def load_trades(
    start_brt: datetime,
    end_brt: datetime,
    ticker: str,
) -> Iterable[Trade]:
    """Stream ``Trade`` rows from TimescaleDB for ``[start_brt, end_brt)``.

    Raises
    ------
    ValueError
        If ticker not in whitelist or if inputs are tz-aware.
    HoldoutLockError
        If the window intersects the pre-registered hold-out
        ``[2025-07-01, 2026-04-21]`` and ``VESPERA_UNLOCK_HOLDOUT!=1``.
        This check fires BEFORE any DB connection (AC11).
    """
    # --- 1. Input validation (no I/O yet) ---------------------------------
    if ticker not in _ALLOWED_TICKERS:
        raise ValueError(
            f"ticker must be one of {sorted(_ALLOWED_TICKERS)}; got {ticker!r}"
        )
    if start_brt.tzinfo is not None or end_brt.tzinfo is not None:
        raise ValueError(
            "feed_timescale: start_brt and end_brt must be BRT-naive (tzinfo=None)"
        )
    if not start_brt < end_brt:
        raise ValueError(
            f"feed_timescale: start_brt ({start_brt}) must be < end_brt ({end_brt})"
        )

    # --- 2. Hold-out guard BEFORE I/O (AC11) ------------------------------
    # end_brt is exclusive at the microsecond level; the lock is date-based
    # and inclusive-end, so we subtract 1us before coercing to a date.
    end_inclusive = end_brt - timedelta(microseconds=1)
    assert_holdout_safe(start_brt.date(), end_inclusive.date())

    # --- 3. Env + connect (only after guard passed) -----------------------
    env = _load_env_vespera()
    _require_env(env)

    # We return a generator so the caller controls cursor lifetime. The
    # connection is opened HERE (inside the generator body below) so that
    # if the caller never iterates, we never connect.
    return _stream(env, ticker, start_brt, end_brt)


def _stream(
    env: dict[str, str],
    ticker: str,
    start_brt: datetime,
    end_brt: datetime,
) -> Iterator[Trade]:
    conn = _connect(env)
    try:
        yield from _iter_rows(conn, ticker, start_brt, end_brt)
    finally:
        try:
            conn.close()
        except Exception:
            pass


__all__ = ["load_trades"]
