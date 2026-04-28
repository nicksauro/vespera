"""Single-shot: chunks per month."""
from pathlib import Path
import sys

env = {}
for line in (Path(__file__).resolve().parents[1] / ".env.vespera").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip()
import psycopg2
conn = psycopg2.connect(
    host=env["VESPERA_DB_HOST"], port=int(env["VESPERA_DB_PORT"]),
    dbname=env["VESPERA_DB_NAME"], user=env["VESPERA_DB_USER"],
    password=env["VESPERA_DB_PASSWORD"],
    options="-c default_transaction_read_only=on",
)
cur = conn.cursor()
cur.execute(
    """
    SELECT date_trunc('month', range_start AT TIME ZONE 'UTC')::date AS month,
           COUNT(*) AS n_chunks,
           MIN((range_start AT TIME ZONE 'UTC')::date) AS first_chunk,
           MAX((range_start AT TIME ZONE 'UTC')::date) AS last_chunk
    FROM timescaledb_information.chunks
    WHERE hypertable_name='trades'
    GROUP BY month ORDER BY month;
    """
)
rows = cur.fetchall()
out = ["month       chunks  first       last"]
for r in rows:
    out.append(f"{r[0].isoformat():<12}{r[1]:>6}  {r[2].isoformat():<12}{r[3].isoformat():<12}")
out.append(f"TOTAL months_with_chunks={len(rows)}, total_chunks={sum(r[1] for r in rows)}")
text = "\n".join(out)
target = Path(__file__).resolve().parents[1] / "state" / "T002" / "_dara_chunks.txt"
target.write_text(text, encoding="utf-8")
sys.stderr.write(f"WROTE {target} {len(text)} bytes {len(rows)} months\n")
cur.close(); conn.close()
