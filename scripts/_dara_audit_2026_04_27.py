"""Dara T002 ESC-009 data coverage audit script.

ONE-OFF — Reads sentinel_ro Vespera DB metadata + light row-presence checks
to map gaps. Strictly read-only. Not registered in manifest.

Usage:
    python scripts/_dara_audit_2026_04_27.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_env() -> dict[str, str]:
    env = {}
    for line in (REPO_ROOT / ".env.vespera").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def _connect():
    import psycopg2
    env = _load_env()
    return psycopg2.connect(
        host=env["VESPERA_DB_HOST"],
        port=int(env["VESPERA_DB_PORT"]),
        dbname=env["VESPERA_DB_NAME"],
        user=env["VESPERA_DB_USER"],
        password=env["VESPERA_DB_PASSWORD"],
        options="-c default_transaction_read_only=on",
    )


def chunks_per_month(cur):
    cur.execute(
        """
        SELECT date_trunc('month', range_start AT TIME ZONE 'UTC')::date AS month,
               COUNT(*) AS n_chunks,
               MIN((range_start AT TIME ZONE 'UTC')::date) AS first_chunk,
               MAX((range_start AT TIME ZONE 'UTC')::date) AS last_chunk
        FROM timescaledb_information.chunks
        WHERE hypertable_name='trades'
        GROUP BY month
        ORDER BY month
        """
    )
    rows = cur.fetchall()
    print("=== Chunks per month (TimescaleDB metadata, fast) ===")
    print(f"{'month':<12}{'chunks':>7}  {'first':<12}{'last':<12}")
    for r in rows:
        print(f"{r[0].isoformat():<12}{r[1]:>7}  {r[2].isoformat():<12}{r[3].isoformat():<12}")
    print(f"TOTAL months_with_chunks={len(rows)}, total_chunks={sum(r[1] for r in rows)}")
    return rows


def trades_per_day_window(cur, start: date, end_inclusive: date, ticker: str = "WDO", max_rows: int = 400):
    """Count rows per day for a given window — uses a HAVING-based pruning."""
    cur.execute(
        """
        SELECT timestamp::date AS day, COUNT(*) AS rows
        FROM trades
        WHERE ticker=%s AND timestamp >= %s AND timestamp < %s
        GROUP BY day
        ORDER BY day
        """,
        (ticker, start, end_inclusive + timedelta(days=1)),
    )
    rows = cur.fetchall()
    print(f"=== {ticker} trades per day [{start} .. {end_inclusive}] ({len(rows)} days with rows) ===")
    print(f"{'day':<12}{'rows':>10}")
    for r in rows[:max_rows]:
        print(f"{r[0].isoformat():<12}{r[1]:>10}")
    if len(rows) > max_rows:
        print(f"... +{len(rows) - max_rows} more rows truncated")
    return rows


def hard_bounds(cur, ticker: str = "WDO"):
    """Use index-only scan via timestamp ASC/DESC LIMIT 1 — sub-second."""
    print(f"=== {ticker} hard bounds (index-only) ===")
    cur.execute(
        "SELECT timestamp FROM trades WHERE ticker=%s ORDER BY timestamp ASC LIMIT 1",
        (ticker,),
    )
    earliest = cur.fetchone()
    cur.execute(
        "SELECT timestamp FROM trades WHERE ticker=%s ORDER BY timestamp DESC LIMIT 1",
        (ticker,),
    )
    latest = cur.fetchone()
    print(f"  earliest={earliest}")
    print(f"  latest  ={latest}")
    return earliest, latest


def main():
    conn = _connect()
    try:
        cur = conn.cursor()
        # 1. Chunk metadata (fast).
        chunks_per_month(cur)
        print()

        # 2. WDO + WIN hard bounds via index lookups (sub-second each).
        hard_bounds(cur, "WDO")
        hard_bounds(cur, "WIN")
        print()

        # 3. 2023-Q4 day-level row counts (user said "uns 2 dias quebrados").
        trades_per_day_window(cur, date(2023, 10, 1), date(2023, 12, 31), "WDO")
        print()

        # 4. 2025-07..2026-04 day-level (user said available).
        trades_per_day_window(cur, date(2025, 7, 1), date(2026, 4, 27), "WDO")
        print()

        cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
