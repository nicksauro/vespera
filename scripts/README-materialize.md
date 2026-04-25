# materialize_parquet.py — operator runbook

Story: T002.0a | Epic: EPIC-T002.0 | Owner: Dara (@data-engineer)

## What it does

Reads trades from the Sentinel TimescaleDB (via the read-only `sentinel_ro` role) and writes one deterministic parquet file per `(ticker, year, month)` under `data/in_sample/year=YYYY/month=MM/<ticker>-YYYY-MM.parquet`. Appends one row per file to `data/manifest.csv` with `sha256` for downstream audit.

## When to run it

- After applying `scripts/sql/create-sentinel-ro.sql` (once per environment).
- Whenever `data/in_sample/` needs to be regenerated from the source DB (e.g. Sentinel chunk added a backfill day).
- Never against the hold-out window `2025-07-01 .. 2026-04-21` during the T002.0 epic.

## Hold-out policy (fail-closed)

- Default: `VESPERA_UNLOCK_HOLDOUT=0` -> materializer raises `HoldoutLockError` before any DB connection if the requested `[start, end]` intersects `[2025-07-01, 2026-04-21]`.
- Unlock path: only after Fase E final (R1 unlock gate + Pax/Mira co-sign). Never set `=1` inside this epic.

## Usage

```bash
# Full in-sample materialization (one-shot):
python scripts/materialize_parquet.py \
  --start-date 2024-01-02 \
  --end-date   2025-06-30 \
  --ticker     WDO \
  --output-dir data/in_sample/

# Plan-only (no DB connection):
python scripts/materialize_parquet.py \
  --start-date 2024-01-02 --end-date 2024-06-30 --ticker WDO --dry-run
```

Aliases `--start` / `--end` / `--out` accepted.

## Idempotency

- Parquet writes are atomic (`write to .tmp`, `os.replace`). Re-running with the same args produces byte-identical output (verified: determinism test in `tests/unit/test_materialize_args.py`).
- `manifest.csv` **appends** on every run. If you re-materialize a month, the new row is added on top; the hash proves the file content. For a clean state, delete `data/in_sample/` and `data/manifest.csv` before re-running.

## Rollback

```bash
rm -rf data/in_sample/ data/manifest.csv
```

Both paths are gitignored; the only committed artifact is `data/manifest.csv`, which is regenerable. Roll back by deleting and re-running.

## Verification

```bash
# AC1 — role custodial
docker exec sentinel-timescaledb psql -U sentinel -d sentinel_db -c \
  "SELECT has_table_privilege('sentinel_ro','public.trades','SELECT'),
          has_table_privilege('sentinel_ro','public.trades','INSERT')"
# expected: t | f

# AC8.1 — no hold-out row ever appears in manifest
grep -cE '^2025-0[789]|^2025-1[012]|^2026-' data/manifest.csv
# expected: 0

# Determinism — identical hash on re-run of same window
sha256sum data/in_sample/year=2024/month=01/wdo-2024-01.parquet
# (run materialize again with same args, hash must match)
```

## Manifest schema (Riven Condition 3)

`data/manifest.csv` columns, in fixed order:

| # | column              | notes                                             |
|---|---------------------|---------------------------------------------------|
| 1 | `path`              | repo-relative parquet path (posix slashes)        |
| 2 | `rows`              | row count in that parquet file                    |
| 3 | `sha256`            | SHA-256 of the parquet bytes                      |
| 4 | `start_ts_brt`      | earliest `timestamp` in the file (BRT-naive ISO)  |
| 5 | `end_ts_brt`        | latest `timestamp` in the file (BRT-naive ISO)    |
| 6 | `ticker`            | e.g. `WDO`, `WIN`                                 |
| 7 | `phase`             | `warmup` \| `in_sample` \| `hold_out` (see below) |
| 8 | `generated_at_brt`  | wall-clock at run start (BRT-naive ISO)           |

**Phase cutoffs** (spec v0.2.0 L93 + PRR-20260421-1):

- `warmup`    : `2024-01-02 → 2024-06-30` (≈125 business days)
- `in_sample` : `2024-07-01 → 2025-06-30` (≈250 business days)
- `hold_out`  : `2025-07-01 → 2026-04-21` (NOT materialized in T002.0a)

Monthly partitioning keeps each parquet cleanly inside one phase; a window
straddling a cutoff is rejected at classifier level (`ValueError`).

## Secrets

`.env.vespera` is gitignored. Assign the `sentinel_ro` password out of band:

```sql
ALTER ROLE sentinel_ro WITH PASSWORD '<value-from-dara>';
```
