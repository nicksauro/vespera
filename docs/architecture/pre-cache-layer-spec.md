# Pre-Cache Layer for Raw Trades — Option B Design Spec

**Owner:** Aria (@architect, ♎)
**Status:** PROPOSED
**Created:** 2026-04-23 BRT
**Targets:** unblock RA-20260426-1 Option B baseline-run chain
**Scope (pilot):** WDO, 2024-08-01 .. 2024-08-31 (Aug-2024 slice)
**Scope (generic):** any `(ticker, [start, end])` pair outside the hold-out lock

---

## §1. Motivation

Per `data/baseline-run/baseline-aug-2024-halt-report.md` L137-139 (retry-4 root cause):
`scripts/materialize_parquet.py` reads raw trades from the `sentinel-timescaledb`
container on localhost:5433, but RA-20260425-1 Decision 1 (inherited from
RA-20260424-1) stops that container as part of the authorized-quiesce minimum
set. The stop-decision is structurally incompatible with the baseline-run
workload: the child process is severed from its data source and exits with
`psycopg2.OperationalError: could not connect to server` inside 30.6 s. A local
pre-cache layer decouples the read path from the live container: we pre-build
an immutable, sha256-verified local mirror of the Aug-2024 WDO raw-trade slice
*before* the quiesce, then the baseline-run reads from the cache while
Sentinel is stopped. This preserves both the R4 memory gate (container DOWN)
AND the data dependency (trades available).

---

## §2. Decision Record — ADR-4

**ADR-4: Local Pre-Cache Layer for Raw Sentinel Trades (Option B)**

ADRs 1/2/3 are taken by `memory-budget.md` (ROM budget v1/v2/v3, telemetry
mechanism, wrapper responsibility boundary). Next available: **ADR-4**.

- **Status:** PROPOSED, awaiting Riven sign-off for RA-20260426-1.
- **Context:**
  - Retry-4 of baseline-run failed because `materialize_parquet.py` reads from
    a container Decision 1 requires be stopped.
  - Options A (don't stop sentinel) and C (re-derive CAP from sentinel-UP
    floor) were weighed in halt-report §Recommendation. Option A is blocked
    by insufficient reclaim when WSL + Docker Desktop backend remain alive
    (vmmem didn't drop on `wsl --shutdown`). Option C requires re-opening
    ADR-1 v3 and is orthogonal to the structural read-path coupling.
  - Option B addresses the coupling directly: materialize the raw-trade slice
    once, cache it, and let subsequent baseline runs consume the cache.
- **Decision:** Introduce a dedicated cache directory
  `data/cache/raw_trades/` holding deterministic parquet chunks of raw
  Sentinel trades (schema-identical to `data/in_sample/**` but explicitly
  non-canonical), plus a cache-local manifest `data/cache/cache-manifest.csv`
  mirroring the canonical manifest format. Extend `materialize_parquet.py`
  with a `--source {sentinel,cache}` dispatch. Introduce a new adapter
  `packages/t002_eod_unwind/adapters/feed_cache.py` with identical contract
  to `feed_timescale` / `feed_parquet`. Introduce a build script
  `scripts/build_raw_trades_cache.py` that is idempotent, resumable and
  hold-out-locked.
- **Consequences:**
  - **Positive:** baseline-run works with sentinel DOWN (Decision 1 stays
    valid). Cache is reusable across future baseline/other runs. AC14 parity
    is preserved (same 3-tuple contract). R15 append-only + Article IV (No
    Invention) are preserved (no new schema).
  - **Negative:** +~1.5–3 GiB disk for Aug-2024 WDO (~15–22M rows @ snappy).
    Extra one-off build latency (~2–5 min single-month) before quiesce.
    Third read-path adapter to maintain (feed_timescale / feed_parquet /
    feed_cache) — mitigated by 1:1 schema reuse.
  - **Neutral:** no change to canonical `data/manifest.csv` or
    `data/in_sample/**`. Hold-out bounds `[2025-07-01, 2026-04-21]` remain
    authoritative via `_holdout_lock` — the cache cannot hold hold-out data.

---

## §3. Storage Layout

### §3.1. Path conventions

```
data/cache/
├── cache-manifest.csv                             # §7 manifest (chain of custody)
├── raw_trades/
│   ├── ticker=WDO/
│   │   └── year=2024/
│   │       └── month=08/
│   │           ├── wdo-2024-08.parquet            # atomic, immutable once written
│   │           └── wdo-2024-08.parquet.ckpt       # §5.3 checkpoint (deleted on success)
│   └── ticker=WIN/            # future reuse, same layout
└── .gitignore                                     # the whole cache tree is gitignored
```

All paths are relative to repo root. Resolution uses `os.path.relpath` (case-
insensitive on Windows, same pattern as `scripts/materialize_parquet.py:736-
741`).

### §3.2. File naming

`{ticker_lower}-{YYYY}-{MM}.parquet` — same convention as
`scripts/materialize_parquet.py:420`. Month-granular partitioning keeps chunk
sizes bounded (~500K–850K rows/day × 21–23 business days ≈ 11–20M rows, ~1–
2 GiB uncompressed, ~400–800 MiB snappy). Aug-2024 pilot fits cleanly in a
single file.

### §3.3. Format choice — parquet (NOT SQLite)

**Decision: parquet, snappy, `row_group_size=100_000`, pyarrow 2.6.**

Justification:
1. **Schema parity with canonical `data/in_sample/**`.** Exact same 7-column
   schema (`scripts/materialize_parquet.py:330-339`). Makes the cache a
   drop-in *read* source without schema translation layer — Article IV.
2. **`feed_parquet.py` logic reuses verbatim.** §6 shows `feed_cache.py`
   delegates to the same pyarrow row-group / numpy fast-path as
   `feed_parquet.py:228-328` — no new hot-path code.
3. **Deterministic byte-identity.** snappy + fixed row-group size + pyarrow
   2.6 gives reproducible output — the same property the canonical pipeline
   already relies on (`scripts/materialize_parquet.py:488-503`).
4. **SQLite would cost us schema translation + random-access bias.** Our
   workload is strictly sequential monthly scan + window filter — parquet
   row-group pushdown is a better fit than B-tree indexes.

Rejected: per-day parquet chunks (too many files for multi-year future use),
SQLite (schema divergence), zstd (compression determinism less battle-tested
in pyarrow 2.6 than snappy in our toolchain).

---

## §4. Schema

### §4.1. On-disk parquet schema (1:1 with canonical)

Identical to `scripts/materialize_parquet.py:329-339`:

| Column      | Type             | Null  | Notes                                    |
|-------------|------------------|-------|------------------------------------------|
| `timestamp` | `timestamp[ns]`  | NO    | BRT-naive, tz=None (R2)                  |
| `ticker`    | `string`         | NO    | whitelist {WDO, WIN}                     |
| `price`     | `float64`        | NO    | coerced from Postgres NUMERIC (exact)    |
| `qty`       | `int32`          | NO    | Postgres INT fits                        |
| `aggressor` | `string`         | NO    | {BUY, SELL, NONE}                        |
| `buy_agent` | `string`         | YES   | already-resolved name (VARCHAR)          |
| `sell_agent`| `string`         | YES   | already-resolved name (VARCHAR)          |

### §4.2. Mapping to `Trade` dataclass on read

`Trade` (core/session_state.py:19-25) has 3 fields: `ts`, `price`, `qty`.
On read, `feed_cache.load_trades()` projects only those 3 columns — same
discard pattern as `feed_parquet.py:17` and `feed_timescale.py:56-60`. This
preserves AC14 parity byte-for-byte.

**Article IV check:** no new columns, no new types, no renames. Mirror.

---

## §5. Build Flow

### §5.1. Script

`scripts/build_raw_trades_cache.py`

### §5.2. CLI

```bash
python scripts/build_raw_trades_cache.py \
    --ticker WDO \
    --start-date 2024-08-01 \
    --end-date 2024-08-31 \
    --cache-dir data/cache/raw_trades \
    --cache-manifest data/cache/cache-manifest.csv
```

Flags (all `--start`/`--end` aliases accepted, mirroring
`materialize_parquet.py:186,194`):

| Flag                | Type    | Default                           | Notes                                  |
|---------------------|---------|-----------------------------------|----------------------------------------|
| `--ticker`          | str     | required                          | whitelist `{WDO, WIN}`                 |
| `--start-date`      | date    | required                          | BRT, inclusive                         |
| `--end-date`        | date    | required                          | BRT, inclusive                         |
| `--cache-dir`       | Path    | `data/cache/raw_trades`           | must NOT resolve under `data/in_sample`|
| `--cache-manifest`  | Path    | `data/cache/cache-manifest.csv`   | must NOT equal `data/manifest.csv`     |
| `--resume`          | bool    | `true`                            | skip months already in manifest w/ valid sha |
| `--dry-run`         | bool    | false                             | plan only, no DB connect               |
| `--force-rebuild`   | bool    | false                             | wipe target chunks + manifest entries  |

### §5.3. Algorithm

```
1. parse_args()
2. guard: --cache-dir MUST NOT be under data/in_sample/ (fail-closed)
3. guard: --cache-manifest MUST NOT be data/manifest.csv (fail-closed)
4. HOLD-OUT LOCK:
   assert_holdout_safe(args.start_date, args.end_date)   # BEFORE any I/O
5. load .env.vespera, require VESPERA_DB_* (reuse _load_env_vespera pattern)
6. months = iter_month_windows(start, end_inclusive)      # reuse §5.4
7. for each month mw:
   7.1. out_path = {cache_dir}/ticker={T}/year={Y}/month={M}/{t}-{Y}-{M}.parquet
   7.2. if args.resume and manifest has (out_path, sha256) and sha256 matches disk:
            print "[cache] skip {mw.label} (resume)"; continue
   7.3. ckpt = out_path.with_suffix('.parquet.ckpt')
        if ckpt.exists():
            delete partial .parquet.tmp, .parquet.ckpt  # crash cleanup
   7.4. write ckpt as {"status":"in_progress","started_at":..., "month":...}
   7.5. stream-fetch month from sentinel (reuse _fetch_month_dataframe)
   7.6. write {out_path}.tmp via pyarrow (snappy, rg=100_000, pyarrow 2.6)
   7.7. os.replace({out_path}.tmp, out_path)             # atomic rename
   7.8. digest = sha256(out_path)
   7.9. append row to cache-manifest.csv (atomic: tmp+replace)
   7.10. delete ckpt on success
   7.11. gc.collect()
8. connection.close()
9. print summary
```

### §5.4. Reused helpers (no reinvention — Article IV)

From `scripts/materialize_parquet.py`:
- `_parse_date`, `_month_first`, `_month_last`, `iter_month_windows`,
  `MonthWindow` (§5.3 step 6).
- `_build_parquet_schema` (§5.3 step 7.6) — identical schema.
- `_load_env_vespera`, `_sanitize_error_message`, `_connect` (§5.3 step 5 /
  7.5) — DB access with password hygiene.
- `_fetch_month_dataframe` (§5.3 step 7.5) — server-side cursor streaming.
- `_write_parquet` (§5.3 step 7.6) — deterministic write + atomic `.tmp`→rename.
- `_sha256_file` (§5.3 step 7.8).

New helpers (strictly cache-specific):
- `_write_cache_manifest_row(path, row)` — atomic CSV append (open `.tmp` →
  write → `os.replace`), matches `_append_manifest` semantics but writes to
  `--cache-manifest` instead of canonical.
- `_resume_skip(manifest, out_path)` — re-read manifest, check `path+sha256`
  matches the on-disk file.
- `_cleanup_partial(out_path)` — unlink `.tmp` and `.ckpt` if present.

### §5.5. Resumability

The checkpoint file (`*.parquet.ckpt`) is a lightweight JSON sentinel written
BEFORE the parquet tmp is created and deleted AFTER the manifest row is
flushed. On crash:
- If `.parquet` exists AND manifest row exists AND sha matches → already done.
- If `.parquet.tmp` or `.parquet.ckpt` exist → partial; cleanup + redo.
- If `.parquet` exists but manifest row missing → compute sha, append row.
- `--resume` is default true. `--force-rebuild` unlinks everything first.

This mirrors the row-group-atomic property parquet already gives us — we
never leave a half-written parquet on disk because `os.replace` is atomic.

---

## §6. Read Flow

### §6.1. Interface — `feed_cache.py`

New module: `packages/t002_eod_unwind/adapters/feed_cache.py`.

Contract (identical to `feed_timescale.load_trades` L163-206 and
`feed_parquet.load_trades` L331-379):

```python
def load_trades(
    start_brt: datetime,
    end_brt: datetime,
    ticker: str,
) -> Iterable[Trade]:
    ...
```

Same semantics:
- `[start_brt, end_brt)` half-open, BRT-naive.
- Ticker whitelist `{"WDO", "WIN"}`.
- Yields `Trade(ts, price, qty)` — 3 fields (AC14 parity).
- Hold-out guard BEFORE any file open.
- Integrity-verified sha256 per file (§7).

### §6.2. Internals (delegate to feed_parquet core)

`feed_cache.py` is ~80 lines: a manifest loader targeting
`data/cache/cache-manifest.csv` and a `_stream` that reuses
`feed_parquet._iter_parquet_rows` unchanged. No duplicated hot-path code.

### §6.3. `materialize_parquet.py` integration

Add `--source {sentinel,cache}` flag (default `sentinel` — current behavior
preserved; non-breaking).

```bash
# Cache-backed baseline-run:
python scripts/materialize_parquet.py \
    --source cache \
    --cache-dir data/cache/raw_trades \
    --cache-manifest data/cache/cache-manifest.csv \
    --ticker WDO \
    --start-date 2024-08-01 --end-date 2024-08-31 \
    --output-dir data/baseline-run/scratch \
    --no-manifest
```

With `--source cache`:
- Skip `_connect` / psycopg2 (no DB).
- Replace `_fetch_month_dataframe(conn, ticker, mw)` with a cache-backed
  equivalent: read the relevant cache parquet, sha-verify, predicate-filter
  to the month window, return as a DataFrame with the 7-column schema.
- All downstream flow (`_write_parquet`, manifest flush, gc.collect) is
  unchanged.

With `--source sentinel` (default): existing behavior, byte-identical.

### §6.4. Non-goals for read flow

- `feed_cache.py` is NOT a drop-in for `feed_parquet.py`. They point at
  different manifests on purpose — canonical vs cache.
- CPCV hot-path production runs should continue reading canonical
  `data/in_sample/**`. The cache is ONLY for:
  (a) unblocking baseline-run quiesce workflows,
  (b) future ad-hoc slice requests that don't warrant canonical materialization.

---

## §7. Integrity — sha256 manifest

### §7.1. Manifest format (mirror canonical)

`data/cache/cache-manifest.csv` — identical 7+1 columns to
`scripts/materialize_parquet.py:101-110`:

```
path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt
```

Example row:
```
data/cache/raw_trades/ticker=WDO/year=2024/month=08/wdo-2024-08.parquet,
17234812,
3f2b1e...,
2024-08-01T09:00:45.311000,
2024-08-30T18:29:59.577000,
WDO,
in_sample,
2026-04-23T21:05:17
```

`phase` column is populated via `classify_phase` exactly as the canonical
pipeline does (`scripts/materialize_parquet.py:121-153`). For Aug-2024 →
`in_sample`. The phase is informational only; the hold-out gate fires on
bounds, not on phase label.

### §7.2. Verify-on-read

`feed_cache.py` reuses the sha256 verification path from
`feed_parquet.py:189-218` (`_verify_integrity`, `_INTEGRITY_CACHE`). A
mismatch raises `ValueError` — fail-closed.

### §7.3. Cache invalidation rules

The cache is a **read-through bypass**, not a true cache (no TTL, no LRU):

- Manifest is append-only within a build run. Full rebuild requires
  `--force-rebuild` which unlinks parquets + rewrites manifest.
- The cache holds raw Sentinel output — if Sentinel data changes retroactively
  (R15 states it should NOT for frozen windows), the cache goes stale. There
  is no automatic detection. If Riven declares a window retroactively dirty,
  operator re-runs with `--force-rebuild`.
- Canonical `data/manifest.csv` is NEVER touched by the cache pipeline.
  Guarded explicitly in §5.2 argparse validation.

---

## §8. Hold-Out Lock — Guard Placement

### §8.1. Build path (BEFORE any I/O)

`scripts/build_raw_trades_cache.py:run` (same discipline as
`scripts/materialize_parquet.py:682`):

```python
def run(args: Args) -> int:
    # 1. Hold-out guard — MUST be before connecting to DB or touching cache.
    assert_holdout_safe(args.start_date, args.end_date)
    # ... only after the guard can we touch DB, files, manifest.
```

Idempotent; raises `HoldoutLockError` (exit 2) if
`[start, end] ∩ [2025-07-01, 2026-04-21] ≠ ∅` AND `VESPERA_UNLOCK_HOLDOUT != 1`.

### §8.2. Read path (BEFORE any file open)

`packages/t002_eod_unwind/adapters/feed_cache.load_trades`:

```python
# --- 2. Hold-out guard BEFORE any I/O (AC11) ------------------------------
end_inclusive = end_brt - timedelta(microseconds=1)
assert_holdout_safe(start_brt.date(), end_inclusive.date())
```

Same line position (3rd block after input validation) as
`feed_timescale.py:193-197` and `feed_parquet.py:362-365`.

### §8.3. Defense in depth — manifest content gate

During build, the phase classifier raises on any month straddling the
hold-out cutoff. Aug-2024 cleanly classifies as `in_sample`; any attempt to
cache 2025-07 or later will fail at `classify_phase` even if the hold-out
env unlock is granted — this is structural protection against operator
error when the unlock is *legitimately* used for a future hold-out
unsealing event.

### §8.4. Test: hold-out-in-cache is STRUCTURALLY IMPOSSIBLE

See §9.T3. Combined: (a) build-path guard, (b) read-path guard, (c) phase
classifier, (d) argparse date validation. Hold-out bytes cannot reach
the cache unless the operator both sets `VESPERA_UNLOCK_HOLDOUT=1` *and*
passes a straddling window that doesn't cleanly classify — which still
fails (c).

---

## §9. Test Matrix (Dex scope)

All tests live in `tests/packages/t002_eod_unwind/adapters/` (for the
adapter) and `tests/scripts/` (for the build script). Pytest, no marks.

### §9.1. Unit — `feed_cache.py`

- **T1.** `test_feed_cache_rejects_unknown_ticker` — ValueError on `"XYZ"`.
- **T2.** `test_feed_cache_rejects_tz_aware_inputs` — ValueError on tz-aware
  start/end.
- **T3.** `test_feed_cache_holdout_blocks_before_file_open` — call
  `load_trades(2025-08-01, 2025-08-02, "WDO")`; assert `HoldoutLockError`;
  assert no parquet was opened (mock `pyarrow.parquet.ParquetFile` and
  verify zero calls). Matches `feed_timescale` AC11 lock test.
- **T4.** `test_feed_cache_sha256_mismatch_raises` — corrupt one cache
  parquet byte, expect `ValueError` with `sha256 mismatch`.
- **T5.** `test_feed_cache_missing_manifest_raises_filenotfound` — remove
  cache-manifest, expect `FileNotFoundError`.

### §9.2. Unit — `build_raw_trades_cache.py`

- **T6.** `test_build_holdout_fires_before_db_connect` — patch `psycopg2`
  to raise if called; invoke build with a hold-out window; assert
  `HoldoutLockError`; assert psycopg was never called.
- **T7.** `test_build_cache_dir_cannot_point_to_in_sample` — argparse error
  when `--cache-dir data/in_sample`.
- **T8.** `test_build_cache_manifest_cannot_point_to_canonical` — argparse
  error when `--cache-manifest data/manifest.csv`.
- **T9.** `test_build_resume_skips_already_built_month` — pre-create valid
  parquet + manifest row; invoke build; assert no DB call for that month.
- **T10.** `test_build_resume_redoes_partial_month` — create `.ckpt`
  sentinel + orphan `.tmp`; invoke build; assert cleanup + refetch.
- **T11.** `test_build_force_rebuild_wipes_manifest_and_chunk` — smoke test.

### §9.3. Integration — wired to live sentinel DB (marked `slow`)

- **T12.** `test_build_then_read_parity_wdo_aug_2024` — build cache for
  2024-08-01..2024-08-05; then `feed_cache.load_trades(...)` over the same
  window; assert output 3-tuple stream is byte-identical to
  `feed_timescale.load_trades(...)` over the same window (precedent: AC14
  parity test pattern, `feed_parquet.py:17`).
- **T13.** `test_feed_cache_vs_feed_parquet_parity_jan_2024` — if cache is
  built for Jan-2024 and canonical parquet exists for Jan-2024, assert
  byte-identical output across both adapters — proves the cache is schema-
  lossless.

### §9.4. Contract — `materialize_parquet.py --source` dispatch

- **T14.** `test_materialize_source_cache_does_not_connect_postgres` —
  invoke `materialize_parquet.py --source cache ... --dry-run`; assert
  `psycopg2.connect` was never imported / called (test via monkeypatch
  of the lazy import block).
- **T15.** `test_materialize_source_sentinel_unchanged` — regression:
  existing tests for `--source sentinel` default must still pass unchanged.

### §9.5. Constitutional — Article IV check

- **T16.** `test_cache_schema_identical_to_canonical` — load
  `_build_parquet_schema()` from `materialize_parquet.py`; load arrow
  schema from a cache parquet; assert field-by-field identity.

### §9.6. Determinism

- **T17.** `test_build_is_byte_deterministic` — build Aug-2024 twice
  (different runs, `--force-rebuild` second time); assert sha256 of the
  resulting parquets is identical. Matches canonical determinism guarantee.

---

## §10. Interface Sign-Off for Dex

### §10.1. Files to create

1. `scripts/build_raw_trades_cache.py` — new
2. `packages/t002_eod_unwind/adapters/feed_cache.py` — new

### §10.2. Files to modify

3. `scripts/materialize_parquet.py` — add `--source {sentinel,cache}`,
   `--cache-dir`, `--cache-manifest` flags, dispatch in `run()`.
   Default unchanged.
4. `packages/t002_eod_unwind/adapters/__init__.py` — export `feed_cache`.
5. `.gitignore` — add `data/cache/`.

### §10.3. Function signatures

**`scripts/build_raw_trades_cache.py`:**

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path

@dataclass(frozen=True)
class BuildArgs:
    ticker: str                          # {"WDO", "WIN"}
    start_date: date                     # BRT, inclusive
    end_date: date                       # BRT, inclusive
    cache_dir: Path                      # default: data/cache/raw_trades
    cache_manifest: Path                 # default: data/cache/cache-manifest.csv
    resume: bool                         # default True
    dry_run: bool                        # default False
    force_rebuild: bool                  # default False

def parse_args(argv: list[str] | None = None) -> BuildArgs: ...
def run(args: BuildArgs) -> int: ...     # 0 ok, 1 error, 2 HoldoutLockError
def main(argv: list[str] | None = None) -> int: ...
```

**`packages/t002_eod_unwind/adapters/feed_cache.py`:**

```python
from collections.abc import Iterable
from datetime import datetime
from ..core.session_state import Trade

_ALLOWED_TICKERS = frozenset({"WDO", "WIN"})
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CACHE_MANIFEST = _REPO_ROOT / "data" / "cache" / "cache-manifest.csv"
_CACHE_DIR      = _REPO_ROOT / "data" / "cache" / "raw_trades"

def load_trades(
    start_brt: datetime,          # inclusive, BRT-naive
    end_brt: datetime,            # exclusive, BRT-naive
    ticker: str,                  # whitelist {"WDO","WIN"}
    *,
    manifest_path: Path | None = None,   # default: _CACHE_MANIFEST
) -> Iterable[Trade]: ...
```

**`scripts/materialize_parquet.py` changes:**

Add to `Args` dataclass (L160-169):
```python
source: str               # "sentinel" | "cache"; default "sentinel"
cache_dir: Path | None    # None unless --source=cache
cache_manifest: Path | None
```

Add to `build_parser()` (after L238):
```python
parser.add_argument("--source", choices=("sentinel","cache"), default="sentinel",
    help="Raw trades data source. cache: read from data/cache/raw_trades "
         "(no DB connection). sentinel: read from localhost:5433 (default).")
parser.add_argument("--cache-dir", type=Path, default=None,
    help="Cache root (required when --source=cache).")
parser.add_argument("--cache-manifest", type=Path, default=None,
    help="Cache manifest path (required when --source=cache).")
```

Dispatch in `run()` (L680): if `args.source == "cache"`, skip `_connect` and
replace `_fetch_month_dataframe(conn, ...)` with `_fetch_month_from_cache(
cache_dir, cache_manifest, ticker, mw)`.

### §10.4. Exit codes (build script)

- `0`: success
- `1`: generic error (sanitized message)
- `2`: `HoldoutLockError` (match `materialize_parquet.main` L804)
- `11`: reserved to match canonical materializer convention for hard DB errors

### §10.5. Pilot invocation (Aug-2024 WDO)

```bash
# Step 1: build cache (sentinel UP)
python scripts/build_raw_trades_cache.py \
    --ticker WDO --start-date 2024-08-01 --end-date 2024-08-31

# Step 2: quiesce (stop sentinel, wsl shutdown per RA)

# Step 3: baseline-run against cache (sentinel DOWN)
python scripts/materialize_parquet.py \
    --source cache \
    --ticker WDO --start-date 2024-08-01 --end-date 2024-08-31 \
    --output-dir data/baseline-run/scratch \
    --no-manifest
```

---

## §11. Risks + Mitigations

| # | Risk                                                                   | Detection (QA gate)                                                                  | Mitigation                                                 |
|---|------------------------------------------------------------------------|--------------------------------------------------------------------------------------|------------------------------------------------------------|
| 1 | Cache drift: Sentinel data changes retroactively, cache goes stale     | sha256 verify fires on read; also `cache-manifest.generated_at_brt` auditable       | Operator re-runs `--force-rebuild`; R15 says this shouldn't happen for frozen windows |
| 2 | Schema divergence: someone edits `_build_parquet_schema` in materialize but not feed_cache | T16 constitutional parity test fails                                                 | Import `_build_parquet_schema` into `feed_cache` rather than redefine |
| 3 | Hold-out byte leaks to cache via operator unlock flag                  | T3 + T6 tests; phase-classifier in manifest row raises on straddle                  | §8.3 defense in depth; build rejects post-2025-06-30 for Aug-2024 pilot |
| 4 | Partial-write corruption (mid-build crash)                             | Integrity sha verify catches on next read                                            | `.ckpt` sentinel + `.tmp` + `os.replace` atomic; §5.5 resume logic |
| 5 | `--cache-dir` accidentally aliased to `data/in_sample/`                | Fail-closed in argparse (§5.2 guard)                                                 | Hard error pre-I/O                                          |
| 6 | `--cache-manifest` points at canonical `data/manifest.csv`             | Fail-closed in argparse                                                              | Same mechanism as `manifest_path` canonical guard (L252-260) |
| 7 | Cache consumed by production CPCV run instead of canonical             | Manifest mismatch (canonical reads `data/manifest.csv`; cache reads `data/cache/cache-manifest.csv`) | Separate adapters; `feed_parquet` never falls back to cache |
| 8 | `--source=cache` dispatch adds attack surface in materialize           | T14 + T15 regression; existing tests cover `--source=sentinel` default               | Default preserved; new flag opt-in only                     |

QA gate flags to verify:
- sha256 integrity cache works (run T12 cold + warm).
- Article IV: T16 must pass.
- AC11 parity: T3 + T6 must pass.

---

## §12. Open Questions for Riven (RA-20260426-1)

Three questions block Riven's Decision 1 rationale:

**Q1.** *Is the empirical claim "sentinel stop is safe because cache decouples
read path" verifiable AFTER Dex implements this spec?* Proposed verification:
after Dex lands the change, run T12 (parity test) with `sentinel-timescaledb`
STOPPED. If parity test passes, the claim is empirically validated. Riven
should condition RA-20260426-1 Decision 1 on T12 green. **Requested: Riven
explicit acknowledgement.**

**Q2.** *Does Riven accept the pilot scope (Aug-2024 only) as sufficient for
RA-20260426-1, with multi-month/multi-ticker cache as a future-only
enhancement?* The generic design allows it, but we only ship the pilot.
**Requested: scope sign-off.**

**Q3.** *Is `data/cache/` acceptable as a new L4 directory, gitignored?* Per
`boundary.frameworkProtection: true` (project default) the deny rules do
not cover this path today. No new deny rule needed, but Riven should
confirm no friction with the L1–L4 boundary model.

Secondary (advisory):

**Q4.** Should the cache also be telemetry-captured during build (same
telemetry CSV as materialize) so that Aug-2024 `peak_commit` CAN be derived
from the build phase? (Would unblock #78 CEILING_BYTES derivation independent
of baseline-run.) This is an optional scope extension; defaults to NO
unless Riven wants it pulled forward.

---

## Appendix A — Traceability Matrix (Article IV check)

| Design element                    | Traces to                                                            |
|-----------------------------------|----------------------------------------------------------------------|
| ADR-4 itself                      | halt-report retry-4 §Recommendation L194 (Option B)                  |
| Parquet schema 7 cols             | `scripts/materialize_parquet.py:329-339`                             |
| Snappy + rg=100_000 + 2.6         | `scripts/materialize_parquet.py:488-502`                             |
| `Trade` 3-tuple on read           | `core/session_state.py:19-25`, `feed_timescale.py:14-18`             |
| Hold-out guard pre-I/O            | `scripts/_holdout_lock.py`, `feed_timescale.py:193-197`              |
| sha256 verify-on-read             | `feed_parquet.py:189-218`                                            |
| Atomic write `.tmp`→replace       | `scripts/materialize_parquet.py:486-503`                             |
| Cache manifest columns            | `scripts/materialize_parquet.py:101-110`                             |
| `--source {sentinel,cache}`       | halt-report §Recommendation Option B (L194)                          |
| AC14 parity test pattern          | `feed_parquet.py:17,307-318`                                         |
| Month partitioning                | `scripts/materialize_parquet.py:302-322`                             |
| Phase classifier                  | `scripts/materialize_parquet.py:121-153`                             |
| Article IV (No Invention)         | Constitution Article IV                                              |
| R1/R2/R15 invariants              | spec v0.2.0 L93-94; PRR-20260421-1                                   |

Every design element cites existing code, constitution, or spec. No invented
features.

---

*Signed: Aria (@architect, The Designer ♎). 2026-04-23 BRT. Awaits Riven +
Pax cosign on RA-20260426-1 before Dex implements.*

---

## §13. ADR-4 Amendment 20260424-1

**Amendment owner:** Aria (@architect, ♎)
**Date:** 2026-04-24 BRT
**Status:** PROPOSED — Dex to implement §13.1 + §13.2 under @dev authority;
§13.3 is a position statement awaiting Riven disposition (does NOT gate this
amendment).
**Trigger:** Aug-2024 WDO pilot build failed with memory thrash (peak WS
~11.8 GiB on 16 GiB host, overshooting CAP_v3 = 8.4 GiB); T12 parity
validation was structurally blocked by `skipif(not _db_reachable())` firing
before any cache-arm assertion — yielding `2 skipped` instead of the GREEN
empirical proof Riven conditioned RA-20260426-1 Decision 1 on.
**Principle:** Article IV — every element below traces to an observed
failure mode (pilot thrash report, `materialize_parquet.py:515-523`
accumulation loop, `test_adapter_parity_cache.py:97-98,152-153` skipif) or
to a Riven governance requirement (RA-20260426-1 Q1). No speculation.

### §13.1. Streaming pattern fix — scope decision

**Decision: build_raw_trades_cache.py-scoped fix. `materialize_parquet.py`
is NOT patched in this amendment.**

**Rationale:**

1. **Observed failure is in build path only.** The pilot thrash occurred in
   `scripts/build_raw_trades_cache.py:447` delegating to
   `mp._fetch_month_dataframe` which at `materialize_parquet.py:515-523`
   accumulates every 100K `fetchmany` batch into a single `rows: list`
   before building a DataFrame and Arrow Table. The canonical build path
   (T002.0a, G09 future) has NOT been observed to thrash — Gage's historical
   canonical runs completed under the pre-ADR-1 envelope. There is no
   empirical evidence that a canonical run will violate CAP_v3; there is
   direct evidence that the cache build did.

2. **R10 custodial boundary.** `materialize_parquet.py` is the canonical
   manifest writer (MWF-20260422-1 cosign gated). Any patch to
   `_fetch_month_dataframe` modifies a function that — even if only a
   helper — is in the canonical build call graph. That is R10-territory
   and requires Riven co-sign per agent-authority.md § @devops/R10. A
   scoped fix that bypasses `_fetch_month_dataframe` inside
   `build_raw_trades_cache.py` alone does NOT touch canonical surface and
   can proceed under @dev authority.

3. **Article IV — No Invention (but also No Scope Creep).** The observed
   failure mode justifies a new helper, co-located with the build script,
   that streams row-groups directly. It does NOT justify a refactor of the
   canonical materializer. If §13.3 position (below) is accepted by Riven
   and a canonical-path patch is later needed, that becomes a separate
   amendment with a separate co-sign chain.

**What Dex builds (build-script scope only):**

Add to `scripts/build_raw_trades_cache.py` a new private helper
`_stream_month_to_parquet(conn, ticker, mw, out_tmp_path, schema)` that
replaces the `mp._fetch_month_dataframe` + `mp._write_parquet` call pair
at build_raw_trades_cache.py:447-459. The helper:

- Opens the same server-side cursor as `_fetch_month_dataframe`
  (`conn.cursor(name="cache_stream")`, `cur.itersize = 100_000`, same
  query + params).
- Opens a `pyarrow.parquet.ParquetWriter` context on `out_tmp_path` with
  `schema=_build_parquet_schema()`, `compression='snappy'`,
  `version='2.6'`, `use_dictionary=True`, `write_statistics=True`. Row
  group size is determined by the write granularity below.
- Per `fetchmany(100_000)` batch:
  - Convert batch rows (list of tuples) directly to a pyarrow Table via
    `pa.Table.from_pydict({col: [...] for col in 7})` using pre-bound
    column lists built in the same loop (avoid pandas entirely on hot
    path). Strict coercions mirror `_fetch_month_dataframe:532-541`
    (timestamp→`timestamp[ns]`, price→`float64`, qty→`int32`, strings
    as strings, nulls preserved for agent cols).
  - Call `writer.write_table(table)`. PyArrow flushes one row group per
    `write_table` call — batch of 100K rows produces one 100K row group,
    matching `_write_parquet` determinism knobs (`row_group_size=100_000`).
  - `del batch; del table` at end of loop; no inter-batch retention.
- Empty-month short-circuit: if the first `fetchmany` returns `[]`, abort
  before creating the writer; return row_count=0 and let the caller hit
  the existing `_cleanup_partial` branch (build_raw_trades_cache.py:453).
- Returns `(row_count, first_ts, last_ts)` so the caller can populate the
  manifest row without re-reading the parquet. `first_ts` captured from
  first batch's first row; `last_ts` from the last batch's last row. Both
  are already `datetime` objects from psycopg2.
- Atomic rename: after `writer.close()`, caller does `os.replace(out_tmp,
  out_path)` (identical to `_write_parquet`'s atomic step). sha256 is
  then computed post-write by `mp._sha256_file(out_path)` (existing
  streaming hashlib, 1 MiB chunks — already memory-safe).

**Line-level code sketch (illustrative only — Dex owns final impl):**

```python
# scripts/build_raw_trades_cache.py (new helper)
def _stream_month_to_parquet(conn, ticker, mw, out_tmp, schema):
    import pyarrow as pa
    import pyarrow.parquet as pq
    from datetime import timedelta

    end_excl = mw.end_inclusive + timedelta(days=1)
    query = (
        "SELECT timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent "
        "FROM trades WHERE ticker = %(ticker)s "
        "AND timestamp >= %(start)s AND timestamp < %(end_excl)s "
        "ORDER BY ticker, timestamp"
    )
    params = {"ticker": ticker,
              "start": mw.start.isoformat(),
              "end_excl": end_excl.isoformat()}

    row_count = 0
    first_ts = last_ts = None
    writer = None

    with conn.cursor(name="cache_stream") as cur:
        cur.itersize = 100_000
        cur.execute(query, params)
        while True:
            batch = cur.fetchmany(cur.itersize)
            if not batch:
                break
            # Transpose list-of-tuples -> dict-of-lists once per batch.
            cols = list(zip(*batch))
            table = pa.Table.from_pydict({
                "timestamp":  list(cols[0]),
                "ticker":     list(cols[1]),
                "price":      [float(x) for x in cols[2]],
                "qty":        [int(x)   for x in cols[3]],
                "aggressor":  list(cols[4]),
                "buy_agent":  list(cols[5]),
                "sell_agent": list(cols[6]),
            }, schema=schema)

            if writer is None:
                writer = pq.ParquetWriter(
                    out_tmp, schema,
                    compression="snappy", version="2.6",
                    use_dictionary=True, write_statistics=True,
                )
                first_ts = cols[0][0]
            writer.write_table(table)
            last_ts = cols[0][-1]
            row_count += len(batch)
            del batch, cols, table

    if writer is not None:
        writer.close()
    return row_count, first_ts, last_ts
```

**Integration at build_raw_trades_cache.py:442-475 (replace block):**
- DELETE the `mp._fetch_month_dataframe` call (line 447).
- DELETE the `mp._write_parquet` call (line 459).
- REPLACE with: write `.tmp` via `_stream_month_to_parquet`; if
  `row_count == 0`, `_cleanup_partial` branch; else `os.replace(tmp,
  out_path)`, compute `digest = mp._sha256_file(out_path)`, populate
  manifest row from returned `(row_count, first_ts, last_ts)`.
- KEEP: `.ckpt` sentinel write before the stream; manifest flush after;
  `gc.collect()` at end of iteration.

**Acceptance criteria for Dex (QA gate for §13.1):**

- **A1.** Peak WorkingSet during Aug-2024 WDO pilot build stays under
  **3.5 GiB** (headroom: CAP_v3 is 8.4 GiB; if the new pattern approaches
  CAP_v3 something is still wrong). Measured via process-level telemetry
  (reuse existing `scripts/telemetry_workingset.py` or equivalent).
- **A2.** Pilot build completes Aug-2024 WDO within **10 minutes** on the
  reference 16 GiB host. Historic baseline for comparable volume via
  materialize was ~2-5 min (pre-thrash); streaming with per-batch Arrow
  conversion adds overhead but remains bounded.
- **A3.** Output parquet is byte-identical to what `_write_parquet` would
  have produced for the same input set. Proven by: build Aug-2024 once
  via the new streaming helper, build it again (with sentinel UP) via a
  temporary `--legacy-materialize` path that calls the old code path,
  and assert `_sha256_file` matches. (This `--legacy-materialize` flag
  is a throwaway test harness, deleted after A3 is confirmed.) **Note:**
  if PyArrow's `ParquetWriter` stream-per-table pattern produces a
  different but still-valid parquet (row group count differs), A3
  relaxes to "row-for-row equal after `read().to_pandas()`" — Dex picks
  the strictest variant that holds.
- **A4.** Checkpoint resume works: kill the build mid-stream (SIGINT
  during `write_table`), re-run with `--resume`; the partial `.tmp` +
  `.ckpt` are cleaned up and the month is re-fetched cleanly. Existing
  test **T10** covers this shape — extend it with a mid-stream kill
  simulation.
- **A5.** Ruff clean, mypy clean (match existing tree baseline).

**Authority:** Dex @dev — proceeds without Riven co-sign. No
`materialize_parquet.py` lines are touched. Quinn gates A1-A5.

### §13.2. T12 test redesign

**Decision: Option α (split T12 into T12a + T12b).**

**Rationale:**

1. **T12a preserves the byte-identical equivalence proof.** The original
   T12 intent was "cache and sentinel yield the same stream". That's
   still worth keeping — but it's only provable when both arms are up.
   T12a runs in normal CI (sentinel UP) and guards against schema drift
   / conversion bugs in the cache build path. Losing this test (as
   Option β would) would remove the schema-lossless proof that §9 T13
   ALSO covers but less directly (T13 needs canonical parquet to exist
   for the same month — not guaranteed).

2. **T12b is what Riven actually needs for Q1.** The empirical claim in
   RA-20260426-1 Decision 1 is *not* "cache == sentinel". It is "cache
   is self-sufficient with sentinel DOWN". That's a weaker and cleaner
   claim: cache yields some stream, and that stream matches a
   pre-recorded snapshot. No live DB needed. This is runnable ANY time
   post-snapshot — including the exact quiesce window Riven cares about.

3. **Option β rejected** — loses live-equivalence guardrail; schema
   drift in cache build would only be caught by T13 (which requires
   canonical parquet coincidence) and T16 (schema-only, not
   data-accuracy).

4. **Option γ considered (network-mock of psycopg2 against a recorded
   WAL stream) and rejected** — adds invented infrastructure; Article
   IV violation; not justified by observed failure.

**Fixture mechanism:**

- **Path:** `tests/fixtures/adapter_parity_cache/wdo-2024-03-04.snapshot.json`
  - Chosen day: `2024-03-04` (one WDO session, small volume, same as
    the current `_pick_window` candidate; outside hold-out; cache for
    this day is optional but cheap to pre-build).
- **Format:** JSON with:
  ```json
  {
    "version": 1,
    "window": {"start": "2024-03-04T00:00:00",
               "end":   "2024-03-05T00:00:00",
               "ticker": "WDO"},
    "row_count": <int>,
    "sha256_of_pickled_trades": "<64-hex>",
    "first_trade": [ts_iso, price, qty],
    "last_trade":  [ts_iso, price, qty],
    "generated_at_brt": "2026-04-24T..:...",
    "generator": "tests/scripts/generate_t12b_snapshot.py"
  }
  ```
  - The snapshot is the MD5 (kept as MD5 for parity with existing T12
    hash mechanism) of pickled `[(ts, price, qty), ...]` — same shape
    as existing T12a hash. Field name is `sha256_of_pickled_trades` to
    reflect algo upgrade **OR** renamed `md5_of_pickled_trades` — Dex
    picks one and keeps consistent. (Recommended: SHA-256 for the
    snapshot since it's a pinned artifact; keep MD5 only for in-run
    comparison where collision risk is negligible and perf matters.)
- **sha256-manifested:** YES. The snapshot file's own sha256 is
  recorded in `tests/fixtures/adapter_parity_cache/MANIFEST.sha256`.
  T12b asserts the manifest matches before trusting the snapshot — this
  guards against accidental edits to the pinned artifact.
- **Hold-out enforcement in snapshot:**
  - Generator script (`tests/scripts/generate_t12b_snapshot.py`) calls
    `assert_holdout_safe(2024, 3, 4)` at top. Window is 2024-03 —
    cleanly in-sample — cannot match hold-out `[2025-07-01, 2026-04-21]`.
  - T12b itself also calls `assert_holdout_safe(...)` on the snapshot's
    window before loading. Defense in depth.
  - The snapshot file stores ONLY `(ts, price, qty)` tuples for a
    pre-2025-07 day — structurally cannot contain hold-out data.

**Line-level amendments to `tests/integration/test_adapter_parity_cache.py`:**

| Action | Lines | Content |
|--------|-------|---------|
| KEEP | 1-95 | module docstring (update window description), `_db_reachable`, `_cache_manifest_has`, `_pick_window` |
| UPDATE | 1-30 (docstring) | Mention T12 is now T12a+T12b; describe fixture path |
| DELETE | 97-98 | `@pytest.mark.skipif(not _db_reachable(), ...)` decorator on T12a |
| KEEP (renamed) | 99-149 | Rename function `test_adapter_parity_cache_vs_sentinel_2024_03_04` → `test_T12a_cache_vs_sentinel_both_up` — body unchanged except: at top, add `if not _db_reachable(): pytest.skip("T12a requires sentinel UP")` (inline skip, not decorator — keeps it a skip not an error) |
| DELETE | 152-153 | `@pytest.mark.skipif(not _db_reachable(), ...)` on T13 supplementary — REPLACE with an inline skip identical pattern (same reason: decorator evaluates at import time; inline skip fires in test body and doesn't mask a missing fixture) |
| ADD (new test) | after 149 | `def test_T12b_cache_self_sufficient_sentinel_down()` — see body below |
| ADD (new test helper) | module level | `_load_snapshot()` — reads JSON, verifies `MANIFEST.sha256` entry matches the snapshot file's own sha256, returns dict |

**New test body (T12b):**

```python
def test_T12b_cache_self_sufficient_sentinel_down():
    """T12b — prove feed_cache is self-sufficient with sentinel DOWN.

    Riven RA-20260426-1 Q1 empirical proof. Does NOT require DB.
    Compares live feed_cache output to pinned snapshot generated once
    (during T12a run with sentinel UP, committed to repo).
    """
    snap = _load_snapshot()  # sha-verifies fixture
    w = snap["window"]
    start = datetime.fromisoformat(w["start"])
    end   = datetime.fromisoformat(w["end"])
    ticker = w["ticker"]

    # Hold-out guard defense-in-depth (snapshot can't contain hold-out
    # data, but assert window anyway — structural).
    from scripts._holdout_lock import assert_holdout_safe
    assert_holdout_safe(start.date(), (end - timedelta(days=1)).date())

    if not _cache_manifest_has(ticker, start.year, start.month):
        pytest.skip(f"cache parquet missing for {ticker} {w['start']}")

    from packages.t002_eod_unwind.adapters import feed_cache
    trades = [(t.ts, t.price, t.qty)
              for t in feed_cache.load_trades(start, end, ticker)]

    assert len(trades) == snap["row_count"], (
        f"row count drift: got {len(trades)}, snapshot={snap['row_count']}"
    )
    import hashlib, pickle
    h = hashlib.sha256(pickle.dumps(trades, protocol=5)).hexdigest()
    assert h == snap["sha256_of_pickled_trades"], (
        f"cache content drift from snapshot: got {h}, "
        f"snapshot={snap['sha256_of_pickled_trades']}"
    )
```

**Generator (`tests/scripts/generate_t12b_snapshot.py`):**

Not in ADR-4 scope to specify fully — Dex writes a ~40-line script that:
1. Hold-out-guards the window.
2. Requires sentinel UP (fails hard if not reachable).
3. Loads via `feed_timescale.load_trades` (the source of truth for T12a
   equivalence).
4. Pickles + sha256s the result.
5. Writes snapshot JSON + appends entry to `MANIFEST.sha256`.
6. Documents in header: "Run only when updating the pinned snapshot.
   Commit both the snapshot and MANIFEST.sha256 together."

**Acceptance criteria for Dex (QA gate for §13.2):**

- **A6.** With sentinel UP and cache built: T12a GREEN, T12b GREEN.
- **A7.** With sentinel DOWN (container stopped): T12a inline-skips
  cleanly, T12b GREEN. **This is the Riven Q1 empirical proof.** Must
  be demonstrated in Quinn's QA report.
- **A8.** With fixture missing (first run, pre-generation): T12b skips
  with `cache parquet missing` message, not ERRORS.
- **A9.** Tamper detection: edit one byte of the snapshot JSON; T12b
  fails with `snapshot manifest sha mismatch`.

**Authority:** Dex @dev, Quinn gates A6-A9.

### §13.3. ADR-1 v3 implication — Aria's position

**Position: ADR-1 v3 (CAP_v3 = 8.4 GiB) does NOT need amendment on the
basis of the build-script thrash observation alone. HOWEVER, a latent
defect in the canonical build path likely exists and warrants a
follow-up Riven RA.**

**Reasoning:**

1. **CAP_v3 governs the target-process memory ceiling for the baseline-
   run CPCV workload** (per memory-budget.md v3 derivation: headroom
   after Sentinel-UP floor, Docker/WSL reserve, Windows kernel). It was
   derived from observed floor measurements, not from aspirational
   targets for every future script in the repo.

2. **The build-script thrash was a NEW workload** (pilot introduced in
   ADR-4) running under an UNMEASURED pattern (accumulate-all-into-list
   before Arrow conversion). It was not governed by CAP_v3 at derivation
   time because it did not exist. Fixing it via §13.1 brings it under
   CAP_v3 naturally (streaming pattern caps per-batch memory at
   ~50-100 MiB). No ceiling change needed.

3. **`materialize_parquet.py:515-523` uses the same accumulation
   anti-pattern** — but under canonical workloads this has historically
   succeeded (Gage's T002.0a runs, ~500K-850K rows/day × ~22 days ≈
   11-18M rows/month for WDO, similar magnitude to the pilot). Three
   explanations are plausible:
   (a) Canonical runs happened on a host with more free RAM at
       invocation time (Sentinel container may not have been competing).
   (b) Canonical runs succeeded but with undetected swap pressure —
       no telemetry was active to catch it.
   (c) pandas DataFrame(list-of-tuples) is marginally more memory-
       efficient than PyArrow's path here, and historic builds stayed
       under the host ceiling by thin margins.

4. **Implication:** the canonical materializer IS at risk of the same
   failure mode on a future large-month run (e.g., G09 Mai+Jun 2025 if
   trade volume is higher than Aug-2024). Amending CAP_v3 does not fix
   this — the ceiling is already correct. The correct follow-up is a
   separate Riven RA to patch `_fetch_month_dataframe` itself to a
   streaming pattern, with canonical-rebuild co-sign gated.

5. **Therefore: memory-budget.md v3 stays as-is.** I do NOT request an
   amendment to ADR-1 v3. I DO request that Riven open
   **RA-20260428-1 (proposed)** to evaluate patching the canonical
   `_fetch_month_dataframe` to streaming, tracking the same §13.1
   pattern but with full canonical co-sign + A3-equivalent byte
   identity proof. That RA is OUT OF SCOPE for ADR-4.

**This position is advisory; Riven holds final disposition.**

### §13.4. Risk + Rollback

| # | Risk                                                        | Detection (QA gate)                                        | Rollback                                                          |
|---|-------------------------------------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------|
| 1 | Streaming helper produces parquet with different row-group count than legacy → A3 strict-mode fails | A3 harness in §13.1 | Relax A3 to row-for-row equality post-read; document; re-run |
| 2 | PyArrow `Table.from_pydict` coercion differs from pandas inferences (e.g., Decimal → float64 precision) | A3 + existing T17 determinism test | Add explicit `pa.array(..., type=pa.float64())` per-column; regenerate |
| 3 | Empty-month branch mis-handled (writer never opened → `.tmp` doesn't exist for `os.replace`) | A4 resume test; empty-month path from §5 algo | Early-return branch: no writer, no tmp, skip manifest flush |
| 4 | T12b snapshot becomes stale if Sentinel data retroactively changes (R15 forbids but operator error possible) | Snapshot has `generated_at_brt`; T12a will detect (with sentinel UP) | Regenerate snapshot; commit; update MANIFEST.sha256 |
| 5 | Snapshot pinning breaks when a legitimate schema evolution occurs (future) | T16 constitutional schema test catches schema changes | Schema evolution requires ADR amendment; snapshot regeneration piggybacks |
| 6 | T12b passes but T12a fails with sentinel UP → cache drifted silently | CI must run BOTH; QA gate blocks on either failure | Quinn blocks; Dex investigates cache build regression |
| 7 | Operator accidentally runs `generate_t12b_snapshot.py` against hold-out window | Generator's hold-out guard (raises HoldoutLockError) | Guard is fail-closed; no rollback needed |

**Rollback plan if §13.1 regresses:** revert `build_raw_trades_cache.py`
to pre-amendment (use `mp._fetch_month_dataframe` + `mp._write_parquet`
chain again); Aug-2024 pilot is rebuilt under a larger host (32 GiB)
as a one-off; T12a still runs; RA-20260426-1 gets escalated back to
Riven for re-scoping.

**Rollback plan if §13.2 regresses:** revert test file; T12 becomes
two-arm-up-only again; RA-20260426-1 Q1 is answered by a manual
operational demonstration (Dex runs T12b-equivalent interactively and
Riven witnesses, rather than automated CI proof).

### §13.5. Impact on RA-20260426-1

**Before this amendment:** Q1 ("is sentinel-stop safe?") could not be
empirically proven because T12 skipped in exactly the conditions Q1
targets. Q1 answered by architectural-argument only ("the code doesn't
call the DB"), which Riven reasonably rejected as non-empirical.

**After this amendment:** Q1 is answered GREEN by T12b passing with
sentinel container stopped. Specifically:

1. Dex lands §13.1 (build helper) — pilot build succeeds under CAP_v3.
2. Dex lands §13.2 (T12 split) — T12a + T12b defined, snapshot pinned.
3. Dex or Quinn runs: `docker stop sentinel-timescaledb && pytest tests/integration/test_adapter_parity_cache.py -v`.
4. Expected output: `T12a SKIPPED (sentinel down), T12b PASSED`.
5. Quinn attaches the pytest output to Riven's RA evidence packet.
6. Riven can disposition Q1 as "empirically validated" in the RA write-up.

**Q2 (pilot scope Aug-2024) and Q3 (data/cache/ as L4) are unaffected
by this amendment** — they remain as specified in §12.

**Q4 (build-phase telemetry) is unaffected — still advisory.**

**New Q5 raised BY this amendment (for Riven RA draft):**

> **Q5.** Does Riven accept Aria's position in §13.3 that canonical
> `materialize_parquet._fetch_month_dataframe` carries a latent
> streaming-memory defect that warrants a separate follow-up RA
> (proposed RA-20260428-1) with canonical-rebuild co-sign? If Riven
> prefers to fold the canonical patch into RA-20260426-1 directly, §13.1
> scope expands to include that patch and Dex requires co-sign before
> proceeding.

---

*Signed: Aria (@architect, The Designer ♎). 2026-04-24 BRT. Amendment
20260424-1 appended. §13.1 + §13.2 unblock Dex under @dev authority.
§13.3 is advisory, pending Riven disposition via Q5.*

---

## §14. CEILING_BYTES derivation path decision (Retry #5 telemetry-gap response)

**Amendment owner:** Aria (@architect, ♎)
**Date:** 2026-04-26 BRT
**Status:** PROPOSED — Riven disposition required on §14.6 Q6 before action items §14.5 execute.
**Trigger:** Retry #5 under RA-20260426-1 completed SUCCESSFULLY (exit 0, 21,058,318
rows written, canonical sha 17/17 byte-identical, sentinel restored cleanly) but
wrapper telemetry at `--poll-seconds=30` on a ~60 s cache-path child produced
`peak_commit=819,200 bytes` (startup artifact, sub-Nyquist sampling). Not usable
as input to `CEILING_BYTES` derivation per ADR-1 v3 §Next-steps step 5
(`CEILING_BYTES = min(ceil(peak_commit_aug2024 × 1.3), CAP_ABSOLUTE_v3)`).
Escalation documented at `data/baseline-run/baseline-aug-2024-halt-report.md
§Retry #5` §"Key finding for #78"; Gage (@devops) enumerated four candidate
responses (a)–(d) and escalated to @architect + @risk-manager per
constitutional scope (no unilateral authority over derivation-path choice).
**Principle:** Article IV — every element below traces to retry #5 audit YAML
(`data/baseline-run/ra-20260426-1-evidence/retry5-quiesce-audit.yaml`), ADR-1 v3
(`docs/architecture/memory-budget.md §ADR-1 v3`), Riven Co-sign v3 (§R1–§R7),
ADR-4 §13 scope statements, or RA-20260426-1 Decision 5 authorized invocation.
No invented mechanisms.

### §14.1. Observation from retry #5 (telemetry gap)

Source: `retry5-quiesce-audit.yaml` fields under `baseline_child:`.

| Metric                         | Value              | GiB / MiB           | Telemetry status                                              |
|--------------------------------|--------------------|---------------------|---------------------------------------------------------------|
| `duration_s`                   | 60                 | —                   | Wall clock (start → end)                                      |
| `poll_seconds`                 | 30                 | —                   | Wrapper sampler interval                                      |
| `tick_count`                   | 2                  | —                   | Only two samples across 60 s run — Nyquist-violating          |
| `peak_commit_bytes`            | 819,200            | 0.78 MiB            | Python-startup VmSize snapshot; not peak during parquet write |
| `peak_rss_bytes`               | 3,969,024          | 3.79 MiB            | Same interpretation — startup snapshot, not peak              |
| `ratio_commit_rss`             | 0.206              | —                   | Ratio < 1 is structurally impossible at true peak → proves    |
|                                |                    |                     |   both samples landed in a startup/idle window, not runtime   |
| `peak_pagefile_alloc_bytes`    | 2,389,372,928      | 2.22 GiB            | System-wide PageFile end-of-run allocation (not process peak) |
| `delta_pagefile_bytes`         | 159,318,016        | 152 MiB             | System-wide PageFile delta over window (not process peak)     |
| `total_trades_written`         | 21,058,318         | —                   | Cache read + parquet write completed cleanly                  |
| `emergency_kill.tripped`       | false              | —                   | Nowhere near 7.43 GiB KILL threshold                          |
| Canonical sha drift (17/17)    | 0/17               | —                   | All canonical invariants preserved                            |

**Primary finding:** the run succeeded. The telemetry did not. Cache-path read +
parquet write of 21 M rows is an I/O-bound streaming workload (parquet row-group
pushdown via `feed_cache.load_trades` → `pyarrow.Table.from_pylist` → single
`ParquetWriter.write_table` at write close); its peak-memory pressure is an
order of magnitude below sentinel-path `_fetch_month_dataframe` (which
accumulates all rows via psycopg2 buffered fetch + pandas `DataFrame(list)`,
per §13.3 analysis). The 0.21 commit/rss ratio is a tell: at true peak the
committed address space always meets or exceeds resident set; a value < 1
proves both samples captured a sub-working-set allocator state (interpreter
bootstrap before pyarrow imports + one idle tick between phases).

**Why this was predictable in hindsight (not a blame-post):** RA-20260426-1
Decision 5 authorized `--poll-seconds 30` verbatim (inherited from RA-25-1's
expected sentinel-path runtime of 45–120 min, where 30 s samples yield
90–240 samples — well above Nyquist for minute-scale commit growth). When
ADR-4 Option B routed retry #5 to cache-path, the authorized poll interval
did not scale down with the new ~60 s runtime. Gage executed the authorized
invocation verbatim (correct per one-shot discipline); the mismatch surfaced
only at audit write time. No governance rule was broken — the flag scaling
question simply was not contemplated at the RA-26-1 Decision 5 drafting
moment. See §14.6 Q6 for Riven disposition on whether the poll-interval flag
scaling pattern needs to be formalized for future RAs.

### §14.2. Option analysis (Gage's four candidates)

Each option is evaluated against three criteria: **(1)** does it produce a
scientifically valid `peak_commit_aug2024` input to ADR-1 v3 §Next-steps step
5? **(2)** does it measure the workload that `CEILING_BYTES` must constrain
at runtime (i.e. the R5 WARN/KILL target)? **(3)** cost (quiesce windows,
Dex sprint, Riven RAs).

**Option (a): Fresh RA-20260429-1 for retry #6 with `--poll-seconds=1`.**

| Axis               | Assessment                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| Scientific validity | ✓ Nyquist-satisfied for 60 s runtime (60 samples minimum)                         |
| Workload match     | **✗** Measures cache-path peak (~200–500 MiB est.) — NOT the sentinel-path peak    |
|                    | that dominated the Aug-2024 pilot thrash (~11.8 GiB WS per §13 trigger)            |
| Cost               | Low: 1 RA (Riven draft + flip), 1 quiesce window (~5 min), Gage execution          |
| Risk               | If run < 1 s (parquet reader fast-path), still sub-Nyquist. Unlikely at 21 M rows  |
|                    | but not guaranteed. Secondary risk: data point is cheap to collect but not         |
|                    | what #78 actually needs (scope mismatch per criterion 2).                          |
| Verdict            | **Unblocks #78 with a number — but the number does not constrain the real         |
|                    | workload.** Re-running to collect a finer-resolution measurement of the wrong      |
|                    | workload is Article IV–compliant (traces to retry-5 telemetry gap) but            |
|                    | analytically unhelpful — `CEILING_BYTES` derived from a 500 MiB cache-path peak   |
|                    | × 1.3 headroom = ~650 MiB, which is absurd as a runtime kill threshold for a      |
|                    | sentinel-path production run that legitimately consumes 5–7 GiB.                  |

**Option (b): ADR-4 amendment + code patch — self-reported peak telemetry.**

| Axis               | Assessment                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| Scientific validity | ✓ Structural: `GetProcessMemoryInfo.PeakPagefileUsage` (Windows) or                |
|                    | `psutil.Process.memory_info().peak_wset` is a monotonic maximum over the entire    |
|                    | process lifetime — independent of polling frequency. Child self-reports at exit;   |
|                    | wrapper captures, emits to telemetry CSV + summary JSON.                           |
| Workload match     | ✓ Works for any workload — cache-path today, sentinel-path tomorrow, future        |
|                    | months under RA-28-1. Reusable.                                                    |
| Cost               | Medium: 1–2 d Dex sprint (telemetry reporter module + wrapper integration + tests),|
|                    | Quinn gate, **Riven co-sign required** if it touches `core/memory_budget.py`      |
|                    | (R10 custodial surface per ADR-1 v3) OR `run_materialize_with_ceiling.py` telemetry|
|                    | contract (which ADR-2 defines). See §14.5 for scope boundary.                     |
| Risk               | PeakWorkingSetSize is *working set*, not *committed virtual*. Aria's ADR-1 v3     |
|                    | derivation uses `peak_commit` specifically (Signal A ratio in R1 needs BOTH        |
|                    | `peak_commit` and `peak_rss`; leak detection depends on virtual-commit visibility).|
|                    | Dex MUST capture BOTH via `GetProcessMemoryInfo` fields: `PeakPagefileUsage`       |
|                    | (commit-equivalent) AND `PeakWorkingSetSize` (RSS-equivalent). psutil 5.9+ exposes |
|                    | `peak_pagefile` on Windows; fallback to `ctypes` if unavailable.                   |
| Verdict            | **Structurally correct, reusable, decouples from polling frequency.** Right        |
|                    | long-term fix regardless of which option unblocks #78. Does not alone solve the    |
|                    | workload-scope question (cache vs sentinel) — that is (d)'s domain.                |

**Option (c): Use `pagefile_alloc_end=2.22 GiB` or `delta_pagefile=152 MiB` as
conservative upper-bound proxy for peak_commit.**

| Axis               | Assessment                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| Scientific validity | **✗** These are *system-wide* PageFile metrics. `pagefile.used` measures the       |
|                    | total OS-wide pagefile allocation at the snapshot moment, NOT the subprocess's     |
|                    | peak committed bytes. Confounded by vmmem, Docker Desktop, claude.exe, MsMpEng     |
|                    | residual pagefile touch — none of which scale with the materialize child.          |
|                    | `delta_pagefile` is likewise OS-wide (end − start).                                |
| Workload match     | ✗ Same scope mismatch as (a); cache-path peak ≠ sentinel-path peak.                |
| Cost               | Zero (pure accounting).                                                            |
| Risk               | Under-conservative: real sentinel-path peak (§13 trigger: 11.8 GiB WS) is 5× the   |
|                    | 2.22 GiB pagefile end-value. A CEILING_BYTES derived from 2.22 GiB × 1.3 ≈ 2.9 GiB |
|                    | would trip R5 KILL on any legitimate sentinel-path run — effectively an            |
|                    | inoperable ceiling.                                                                |
| Verdict            | **Pragmatic but unprincipled.** Violates ADR-1 v3 §Next-steps step 5 which         |
|                    | specifies `peak_commit` as the input, not end-of-run pagefile allocation.          |
|                    | Riven's R1 dual signal (§R1, Signal B is ΔPageFile computed per-process, not       |
|                    | system-wide) also breaks under this interpretation. **Rejected.**                  |

**Option (d): Accept cache-path ceiling-triviality — derive CEILING_BYTES from
the sentinel-path workload separately.**

| Axis               | Assessment                                                                        |
|--------------------|------------------------------------------------------------------------------------|
| Scientific validity | ✓ Defers `peak_commit_aug2024` derivation to the sentinel-path baseline run       |
|                    | that will occur under **RA-20260428-1** (already placeholder-scheduled per         |
|                    | memory-budget.md §RA-26-1 Q5 disposition for canonical `_fetch_month_dataframe`    |
|                    | streaming patch + G09 Mai+Jun 2025 relaunch). That run IS the sentinel-path       |
|                    | workload CEILING_BYTES must constrain; measuring its peak is the correct          |
|                    | derivation input.                                                                 |
| Workload match     | ✓ Perfect. Sentinel-path is where real memory pressure lives (§13.3 analysis:     |
|                    | canonical `_fetch_month_dataframe` accumulates via pandas DataFrame + psycopg2    |
|                    | buffered fetch — the 11.8 GiB pilot thrash workload). Canonical Mai+Jun 2025      |
|                    | builds will exercise this path. `CEILING_BYTES` derived from THAT run constrains  |
|                    | THAT workload. Direct semantic match.                                             |
| Cost               | Deferred: no new quiesce window today. RA-20260428-1 will carry its own quiesce   |
|                    | window (already required for G09 Mai+Jun 2025). Amortized cost = zero incremental.|
| Risk               | Time: #78 remains open pending RA-28-1 scheduling (orchestrator / @pm timing).    |
|                    | Mitigation: `CEILING_BYTES = None` sentinel in `core/memory_budget.py` already     |
|                    | forces measure-first (v2 step 8, preserved in v3). Production runs cannot use     |
|                    | a derived ceiling until step 7 is executed — which is the correct fail-closed     |
|                    | state. #78 "blocked" in an orchestrator sense but the system is not at risk.      |
| Verdict            | **Structurally correct scope.** Cache-path is ceiling-irrelevant by the           |
|                    | definition of what CEILING_BYTES protects against. Derive from sentinel-path.     |
|                    | Does not alone solve the polling-frequency problem — that is (b)'s domain for     |
|                    | every future baseline.                                                            |

**Options (a) and (c) fail criterion 2 (workload match). (d) and (b) are
orthogonal — (d) chooses the correct workload, (b) fixes the measurement
method. They are composable.**

### §14.3. Recommendation — **Hybrid (d) + (b)**, in that order

**§14.3.1. Recommendation statement**

1. **Adopt (d) as the structural scope decision for #78.** Retry #5's cache-path
   `peak_commit` is ceiling-irrelevant by design (parquet-streaming reads are
   trivially low-memory per §13 amendment trigger analysis and §13.3 position
   statement). `CEILING_BYTES` per ADR-1 v3 §Next-steps step 5 will be derived
   from the next sentinel-path baseline run, which is structurally scheduled
   under RA-20260428-1 (Q5 disposition: canonical `_fetch_month_dataframe`
   streaming patch + G09 Mai+Jun 2025 relaunch) per memory-budget.md §RA-26-1
   Q5 disposition points 2–4.

2. **Adopt (b) as the reusable telemetry fix, landed before RA-20260428-1
   executes.** Dex implements child-side self-reported peak (`PeakPagefileUsage`
   + `PeakWorkingSetSize` captured at exit via `GetProcessMemoryInfo` on
   Windows with psutil `memory_info().peak_*` fallback) + wrapper passthrough
   to telemetry CSV + summary JSON. This fix decouples peak measurement from
   polling frequency — applies to every future baseline regardless of run
   duration, cache-path vs sentinel-path, poll interval authorized in the
   governing RA. See §14.5 for the scope boundary (Dex authority under @dev
   vs Riven co-sign trigger).

3. **Explicitly reject (a).** Issuing RA-20260429-1 for retry #6 with
   `--poll-seconds=1` solves the polling-frequency problem for one data point
   of the wrong workload. The measurement would pass Nyquist but fail the
   semantic test — `CEILING_BYTES` derived from a cache-path peak does not
   constrain the sentinel-path runtime that R5 WARN/KILL must protect. Wastes
   one Riven RA + one quiesce window for a number that does not close #78
   meaningfully.

4. **Explicitly reject (c).** System-wide `pagefile_alloc_end` and
   `delta_pagefile` confound the materialize child with vmmem, Docker
   Desktop, claude.exe, MsMpEng residual. Derived CEILING_BYTES would be
   unprincipled (violates ADR-1 v3 §Next-steps step 5's `peak_commit` input
   specification and Riven R1 Signal B per-process scope) AND likely
   under-conservative vs actual sentinel-path pressure.

**§14.3.2. Rationale — evidence trace**

**Why (d) is structurally correct (cites ADR-1 v3 §R1–R4 + Riven Co-sign v3):**

- **ADR-1 v3 §"Measure-first compatibility statement" (line ~1149) reads:**
  *"v3 preserves the measure-first architecture… The baseline-run's purpose
  is to observe `peak_commit` under a refactored, un-ceiling-enforced run"*.
  The word **"refactored"** is load-bearing. The refactored canonical
  `_fetch_month_dataframe` (streaming pattern per §13.3) does not yet exist;
  RA-26-1 Q5 disposition defers it to RA-28-1. Measuring the pre-refactor
  canonical would just reproduce the pilot thrash (11.8 GiB peak, exceeds
  v3 CAP at 7.82 GiB — E1 would fire, same outcome as §13.3 point 3).
  Measuring the cache-path (retry #5) is a DIFFERENT workload entirely, not
  the "refactored canonical" that step 5 of Next-steps contemplates. The
  correct baseline run is therefore RA-28-1's sentinel-path build of
  Mai+Jun 2025 AFTER the streaming patch lands.

- **ADR-1 v3 §"Next-steps" step 4 (Riven Co-sign v3 line ~1565):**
  *"Aria + Riven at step 7: derive `CEILING_BYTES = min(ceil(peak × 1.3),
  CAP_ABSOLUTE_v3)`"*. The `peak` input must come from a run whose memory
  behavior matches production semantics. Production `materialize_parquet.py`
  runs (future G09 months) will use sentinel-path (cache doesn't exist for
  those months at build time). Cache-path retry #5 is a baseline-run
  operational routing (per ADR-4 §13) to let the pilot Aug-2024 measurement
  happen at all — NOT a claim that cache-path is the production semantic.

- **Riven Co-sign v3 §R1 (line ~1437) preserves Signal A (ratio `peak_commit /
  peak_rss`) and Signal B (ΔPageFile) as subprocess-internal leak detectors.**
  Both require `peak_commit` measured on the subprocess whose production
  workload will exercise R5 WARN/KILL. Cache-path retry #5 ratio = 0.206 is
  structurally invalid (< 1) because the samples missed runtime entirely;
  Signal B Δ = 152 MiB is system-wide, not per-process. Neither signal is
  usable from retry #5 data even for the cache-path workload itself. The
  dual-signal apparatus requires the sentinel-path baseline measurement to
  operate at all.

- **ADR-4 §13 scope (current):** §13.1 build helper is cache-layer scoped;
  §13.3 explicitly positions the canonical `_fetch_month_dataframe` streaming
  patch as out-of-scope for ADR-4 (advisory only, deferred to RA-28-1 per
  Riven Q5 disposition). §14's scope — CEILING_BYTES derivation path — is
  therefore consistent with §13.3: cache-path is the operational routing,
  sentinel-path is the semantic target. §14 formalizes what §13.3 implied:
  CEILING_BYTES derivation belongs downstream of the canonical patch, not
  alongside the cache build.

**Why (b) is the correct reusable fix (cites ADR-2 + Riven Co-sign v3 §R5):**

- **ADR-2 (telemetry mechanism, preserved under v3)** specifies the wrapper
  as the telemetry boundary: the parent (`run_materialize_with_ceiling.py`)
  samples the child via `psutil.Process(pid).memory_info()` on a poll
  cadence. This parent-side sampling is Nyquist-bound by `--poll-seconds`.
  Option (b) adds a **child-side reporter** that reads its own
  `GetProcessMemoryInfo().PeakPagefileUsage` (Windows kernel-maintained
  monotonic maximum) at the `finally` block of main, emits to stdout in a
  structured line (`TELEMETRY_CHILD_PEAK commit=<int> wset=<int>`), and the
  wrapper parses this line into the telemetry CSV and summary JSON. This is
  an **addition**, not a replacement — parent polling remains for runtime
  R5 WARN/KILL gating (which must be reactive, not end-of-run). End-of-run
  self-report is purely for derivation evidence (step-7 input).

- **Riven Co-sign v3 §R5 (line ~1443–1459) keeps WARN/KILL fractions
  (85%/95%) unchanged under v3.** The R5 runtime gate still depends on
  parent-side polling (no change needed). Option (b) does NOT touch R5. It
  adds a separate telemetry pathway used ONLY for step-7 derivation — the
  two pathways coexist. R5 kill = "observed sample ≥ threshold" stays
  sample-based; step-7 `peak_commit` input becomes "kernel-reported
  end-of-run peak" — independent.

- **ADR-1 v3 §"Dual R1 signal preservation" (line ~1195) requires both
  `peak_commit` and `peak_rss` for Signal A calibration.** `GetProcessMemoryInfo`
  exposes both (`PeakPagefileUsage` + `PeakWorkingSetSize`); psutil
  `memory_info()` on Windows returns `peak_pagefile` and `peak_wset`
  (psutil ≥ 5.9.0 — current repo pin is 5.9.8 per `requirements.lock`, so
  no new dependency). R1 Signal A (ratio) remains fully calculable under
  (b); Signal B (ΔPageFile) requires start + end pagefile allocation
  per-process, which `memory_info().peak_pagefile − memory_info().pagefile_at_start`
  captures. Both signals reproducible.

**Why (d) + (b) is better than either alone:**

- (d) alone: right scope, but next sentinel-path baseline (RA-28-1) would
  face the same `--poll-seconds` flag-scaling risk if the canonical patch
  makes the refactored run fast (streaming is faster by design). Risk of
  repeating the retry-#5 telemetry gap at the most important measurement.
- (b) alone: right mechanism, but applied to cache-path retry #6 produces a
  valid-but-scope-mismatched peak. Ceiling would still need to be re-derived
  from sentinel-path later anyway.
- (d) + (b) in this order: defer #78 to the correct workload (d), land the
  telemetry fix (b) before that workload runs, guaranteeing the
  once-in-a-derivation-cycle measurement is robust regardless of runtime
  duration.

### §14.4. Implications for ADR-1 v3 (amendment vs clarification)

**Position: ADR-1 v3 does NOT need numeric amendment. Needs ONE clarification
appended as a cross-reference note — non-normative.**

Reasoning:

1. **No constant changes.** CAP_ABSOLUTE_v3 (8,400,052,224), OS_HEADROOM
   (1,073,741,824), R4 threshold (9,473,794,048), WARN/KILL fractions
   (0.85 / 0.95), HEADROOM_FACTOR (1.3), and E1–E7 escalation triggers all
   remain correct as written. §14 adds no observed evidence that invalidates
   any of them.

2. **Next-steps sequencing is preserved.** ADR-1 v3 §Next-steps steps 1–3
   (Dex populates CAP + OS_HEADROOM + leaves CEILING_BYTES = None) ARE
   COMPLETE. Step 4 (Gage runs G09a under fresh RA) has been partially
   executed — RA-25-1 (CONSUMED, failed Phase 4), RA-26-1 retry #5
   (CONSUMED, SUCCESS_BUT_TELEMETRY_INSUFFICIENT). The step-4 semantic
   target — a `peak_commit_aug2024` measurement usable at step 5 — remains
   unmet. §14 does not re-derive the target; it re-identifies the correct
   source run (sentinel-path under RA-28-1 rather than cache-path under
   RA-26-1+).

3. **Recommended clarification (advisory, non-normative, for future reader):**
   append a single inline cross-reference note to ADR-1 v3 §"Next-steps" step
   4 of the form:

   > *"Step 4 note (added per ADR-4 §14, 2026-04-26): the `peak_commit_aug2024`
   > input to step 5 must be captured from a sentinel-path `materialize_parquet.py`
   > run under the canonical `_fetch_month_dataframe` streaming refactor
   > (deferred to RA-20260428-1 per RA-20260426-1 Q5 disposition). Cache-path
   > runs (RA-20260426-1 Option B routing) exercise a different memory-pressure
   > profile (parquet-streaming reads) and are ceiling-irrelevant. See ADR-4 §14
   > for derivation-path evidence."*

   **This is Riven's call to apply (R10 custodial on memory-budget.md).** Aria
   does not mutate `memory-budget.md` under §14 authority. The clarification
   is OPTIONAL — future readers cross-referencing via §14 would trace the
   same reasoning without the inline note. Applying it is a courtesy, not
   a requirement.

4. **No new ADR-1 version (v4) required.** A v4 would be needed if CAP or R4
   formula changed. Neither does. Scope of §14 is downstream (where to
   measure `peak_commit`), not upstream (what the ceiling arithmetic is).

### §14.5. Action items

**§14.5.1. Option (d) action items (scope decision — no code)**

| # | Who | What | Blocks on | Cost |
|---|-----|------|-----------|------|
| D1 | Aria | Ship §14 (this section) to `pre-cache-layer-spec.md` | — | Done at commit |
| D2 | Riven | Disposition §14.6 Q6 (governance co-sign gate — see below) | D1 | ≤ 1 h review |
| D3 | Orchestrator / @pm | Keep #78 OPEN, re-associate it to the RA-20260428-1 timeline (not RA-20260429-1). Update issue body referencing §14.3. | D2 | ≤ 30 min |
| D4 | Riven | (When RA-28-1 is drafted) include `peak_commit_aug2024` derivation as a step-7 artifact requirement; audit YAML extends with `peak_commit_bytes_child_self_reported` field (see D5–D7 below for the reporter). | RA-28-1 drafting timing | Part of RA-28-1 drafting |
| D5 | Aria (optional) | Cross-reference note appended to memory-budget.md ADR-1 v3 §Next-steps step 4 per §14.4 point 3 — **IF Riven opts-in at Q6**. | D2 | ≤ 15 min edit |

**§14.5.2. Option (b) action items (telemetry patch)**

Scope boundary (§14.5 clarity per hard rules):

**Files touched (proposed — Dex owns precise line ranges):**

- **`scripts/materialize_parquet.py`** (new telemetry emission at `main()`'s
  `finally` block): ~20 LOC addition. Reads
  `psutil.Process().memory_info().peak_pagefile` +
  `.peak_wset` (psutil 5.9.8, already in `requirements.lock`, no new dep).
  Falls back to `ctypes.windll.psapi.GetProcessMemoryInfo` only if psutil
  field is missing (defensive; not expected under current pin). Writes one
  structured line to stdout:
  `TELEMETRY_CHILD_PEAK_EXIT commit=<int> wset=<int> pid=<int> timestamp_brt=<iso>`.

- **`scripts/run_materialize_with_ceiling.py`** (wrapper parse + emit): ~40 LOC.
  Regex-parse the structured line from child's stdout tail; inject into
  the telemetry CSV as a new final row `tag=child_self_peak` (or separate
  summary JSON field — Dex decides layout in coordination with Quinn's
  ADR-2 alignment check). Non-breaking to existing telemetry consumers
  (new tag is additive; existing parsers that filter by known tags skip it).

- **Tests:** `tests/unit/test_materialize_child_peak_telemetry.py` (new) and
  `tests/unit/test_wrapper_peak_passthrough.py` (new). Cover: (i) child emits
  structured line in success path, (ii) wrapper parses + records in CSV +
  JSON, (iii) missing psutil field → ctypes fallback path, (iv) malformed
  child output → wrapper skips gracefully (no crash).

**Files NOT touched (scope discipline):**

- `core/memory_budget.py` — NO change. Constants stay at v3 values. R1/R4/R5
  gating logic unchanged. The telemetry patch is purely additive reporting.
- `data/manifest.csv` — NEVER touched (canonical custody).
- `data/in_sample/**`, `data/cache/**` — not touched by this patch.
- ADR-1 v3 clauses — not superseded (clarification note in §14.4 point 3 is
  optional and owned by Riven).

**Co-sign trigger:** because the patch touches `run_materialize_with_ceiling.py`
which is the ADR-2 telemetry contract surface (and which Riven explicitly
audits under R2 v2 "pre-flight artifact" + Riven Co-sign v3 "one-shot RA
template compatibility" at line ~1491), **Riven co-sign IS required** before
Dex merges. This is the same pattern as the §P5 wrapper patch for RA-26-1
which required Quinn + Riven gate per precondition P5 evidence packet. Aria
confirms: the telemetry patch is NOT @dev-solo authority; it is @dev-impl +
@qa-gate + @risk-manager-cosign.

**Sprint estimate:** 1–2 d Dex + 0.5 d Quinn gate + 0.5 d Riven co-sign review.
Total: **2–3 d wall clock**. Critical path: Dex impl (Day 1) → Quinn test
+ gate (Day 2) → Riven co-sign (Day 2–3).

| # | Who | What | Blocks on | Cost |
|---|-----|------|-----------|------|
| B1 | @pm (Morgan) | Create story `#XX: child-side peak telemetry for step-7 derivation` with scope per §14.5.2, acceptance criteria per B3 | D2 (Riven Q6 disposition) | ≤ 1 h |
| B2 | @sm (River) | Draft story file `docs/stories/{epic}.{N}.child-peak-telemetry.md`; link ADR-4 §14.5.2 + ADR-2 + ADR-1 v3 §R1 | B1 | ≤ 1 h |
| B3 | @po (Pax) | Validate story draft (10-point checklist). Acceptance criteria MUST include: (A) child emits `TELEMETRY_CHILD_PEAK_EXIT` on every successful exit; (B) wrapper records in CSV + JSON; (C) psutil primary + ctypes fallback covered by tests; (D) no perturbation to R5 runtime behavior (parent-side polling unchanged); (E) cache-path + sentinel-path both exercise path (integration test). | B2 | ≤ 1 h |
| B4 | @dev (Dex) | Implement per §14.5.2 scope; self-review via CodeRabbit pre-commit | B3 | 1–2 d |
| B5 | @qa (Quinn) | Gate B4 against ADR-2 + §14.5.2 acceptance; attach pytest output + CodeRabbit report | B4 | 0.5 d |
| B6 | Riven | Co-sign: confirm telemetry patch does not weaken R5 runtime gating; confirm ADR-2 contract extended compatibly; confirm wrapper-surface scope contained | B5 | 0.5 d |
| B7 | @devops (Gage) | Merge (sprint final commit → main); not blocking §14.3 since no quiesce window involved | B6 | ≤ 1 h |
| B8 | Riven | (Future) When RA-28-1 drafts, cite B4 artifact (commit hash) as the telemetry mechanism backing step-7 `peak_commit_aug2024` measurement | RA-28-1 draft | Part of RA-28-1 |

### §14.6. Open question for Riven (governance co-sign gate)

Continuing the numbering from ADR-4 §12 (Q1–Q4) + §13.5 (Q5):

**Q6.** *Does Riven approve the §14.3 hybrid recommendation (d-structural +
b-mechanism), including:*

- *Q6a — Scope decision (d):* defer `peak_commit_aug2024` derivation from
  RA-20260426-1 retry #5 (cache-path, telemetry-insufficient) to the
  sentinel-path baseline that will execute under RA-20260428-1 per
  memory-budget.md §RA-26-1 Q5 disposition, on the rationale that cache-path
  (parquet-streaming read) is ceiling-irrelevant by design and sentinel-path
  (buffered PG fetch + pandas DataFrame accumulation) is the production
  workload `CEILING_BYTES` must constrain. Evidence: §14.2 Option (d)
  analysis + §14.3 rationale citing ADR-1 v3 §R1/§Next-steps step 4 +
  §Measure-first compatibility clause + ADR-4 §13.3 position.

- *Q6b — Telemetry fix (b) — governance class:* approve Aria's position in
  §14.5.2 that the child-side peak telemetry patch touches
  `run_materialize_with_ceiling.py` (ADR-2 telemetry contract surface) and
  therefore requires Riven co-sign (not @dev-solo authority). Specifically:
  confirm that the patch does NOT open `core/memory_budget.py` (constants
  untouched) and does NOT weaken R5 runtime gating (parent-side polling
  preserved). Sprint authority basis: @dev-impl + @qa-gate + @risk-manager-
  cosign.

- *Q6c — ADR-1 v3 clarification (non-normative):* decide whether to append
  the §14.4 point 3 cross-reference note to `memory-budget.md` ADR-1 v3
  §Next-steps step 4. This is R10 custodial territory (memory-budget.md
  mutation). Opt-in increases auditability; opt-out preserves current file
  layout with no loss (future readers reach the same conclusion via §14
  cross-reference). Aria recommends opt-in; defers to Riven.

- *Q6d — RA-template future-proofing:* given that retry #5's
  telemetry-insufficiency root cause was the `--poll-seconds=30` flag
  scaling mismatch when Decision 5 was inherited from RA-25-1's sentinel-
  path expected runtime, should future RA templates include a mandatory
  **"expected runtime vs poll cadence"** sanity check at Riven drafting
  time? Aria's recommendation: YES, as a one-line drafting checklist item
  ("verify `poll_seconds × 10 ≤ expected_child_runtime_s_lower_bound` OR
  cite child-side peak telemetry (B4) as the primary peak source"). This
  closes the retry-#5 class of issue at the RA-drafting layer without
  requiring code changes.

**Q6 disposition gates:**
- D2 (Aria's action item) blocks on Q6a + Q6b at minimum.
- B1 (story creation) blocks on Q6b.
- D5 (optional clarification note) blocks on Q6c.
- Future RA-28-1 template updates block on Q6d.

Riven does NOT need to disposition Q6a-d atomically; each sub-question is
independently actionable. Aria accepts partial dispositions in any order.

---

*Signed: Aria (@architect, The Designer ♎). 2026-04-26 BRT. §14 appended to
ADR-4 as CEILING_BYTES derivation path decision. §14.1–§14.4 are Aria
position (design-only, no code). §14.5 defines action items pending Riven
Q6 disposition. §14.6 Q6 is the governance co-sign gate. Canonical
`data/manifest.csv` sha256 verified byte-identical at commit time:*
`75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`.
