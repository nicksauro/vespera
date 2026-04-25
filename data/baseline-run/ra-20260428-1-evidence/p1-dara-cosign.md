# RA-20260428-1 P1 — @data-engineer (Dara) R10 Custodial Co-sign

**Co-signer:** Dara (@data-engineer, The Architect), R10 custodial on the canonical-producer surface (`scripts/materialize_parquet.py`).
**Co-signed-at (BRT-naive per R2-2):** 2026-04-24T18:27:24
**Co-signing scope:** RA-20260428-1 P1 (Decision 2) — canonical streaming refactor of `scripts/materialize_parquet.py:_fetch_month_dataframe` replaced by per-batch `pyarrow.parquet.ParquetWriter.write_table` streaming via new helper `_stream_month_to_parquet`.
**Author under co-sign:** Dex (@dev, The Builder).
**Commit under co-sign:** `82fbf87372db57458081360d6a6cae10539d04da` on branch `ra-28-1/p1-streaming-refactor` (off `main@e94239a`).
**Governing authority:** Stage-1 ISSUED RA-20260428-1 (§R10 Amendment L2240-L2354 of `docs/architecture/memory-budget.md`) on Riven-delegated authority, Quinn chain-gate CONDITIONAL GREEN at `docs/qa/gates/RA-20260428-1-chain-gate.md`. R10 custodial dual co-sign required per RA-28-1 Decision 2 pass-criterion (L2293) and P1 precondition (L2306).

---

## Verdict

> **R10 custodial co-sign: APPROVED**

The refactor lands byte-identical canonical-producer semantics while eliminating the Python-list accumulation root cause. Stream is schema-correct, order-preserving, count-parity, BRT-naive, and pattern-parity with the binding precedent `scripts/build_raw_trades_cache.py:_stream_month_to_parquet`. No R1-1 / R2-1 / R2-2 / R3-1 invariant is breached.

---

## Review dimensions (mandated by RA-28-1 L2293 fail-criterion)

### (a) Schema parity — PASS

The refactored helper builds each Arrow `Table` via `pa.Table.from_arrays([...], schema=schema)` where `schema` is the shared `_build_parquet_schema()` output. Column order, column names, element types, and nullability match the canonical schema byte-for-byte:

| Column     | Type                    | Nullable | Source of type     |
|------------|-------------------------|----------|--------------------|
| timestamp  | `pa.timestamp("ns")`    | False    | `_build_parquet_schema` L403 |
| ticker     | `pa.string()`           | False    | L404 |
| price      | `pa.float64()`          | False    | L405 |
| qty        | `pa.int32()`            | False    | L406 |
| aggressor  | `pa.string()`           | False    | L407 |
| buy_agent  | `pa.string()`           | True     | L408 |
| sell_agent | `pa.string()`           | True     | L409 |

Schema-parity is further locked in by `tests/unit/test_materialize_streaming_refactor.py:test_stream_month_to_parquet_schema_parity`, which reads the produced parquet back and asserts `produced.names == schema.names` + per-column type equality + `buy_agent`/`sell_agent` nullability.

ParquetWriter determinism knobs are identical to `_write_parquet`:
* `compression="snappy"`
* `version="2.6"`
* `use_dictionary=True`
* `write_statistics=True`

The one knob `_write_parquet` passes that `ParquetWriter` does not expose directly is `row_group_size=100_000`. This is not a regression: `ParquetWriter.write_table(table)` emits one row group per call, and the helper calls `write_table` on a 100_000-row batch (= `itersize`), so every row group is exactly 100_000 rows — matching the `row_group_size=100_000` semantics of the pre-refactor path byte-for-byte. A trailing batch smaller than 100_000 rows produces a smaller final row group, also matching `_write_parquet` behavior (PyArrow auto-truncates the last row group).

### (b) Row ordering parity — PASS

The SQL query is byte-identical to `_fetch_month_dataframe`:

```sql
SELECT timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent
FROM trades
WHERE ticker = %(ticker)s
  AND timestamp >= %(start)s
  AND timestamp < %(end_excl)s
ORDER BY ticker, timestamp
```

The `ORDER BY ticker, timestamp` clause is preserved verbatim. Server-side named cursor (`name="materialize_stream"`) streams rows in the order the server emits them — PostgreSQL guarantees `ORDER BY` ordering holds across `FETCH` / `fetchmany` boundaries. The helper appends each batch to the parquet via `writer.write_table(table)` in fetch order; no re-sort, no shuffle. Parity test: `test_stream_month_to_parquet_preserves_row_order` reads back via `pq.read_table` and asserts `ts == [r[0] for r in rows]` — exact input-order preservation.

### (c) Row count parity — PASS

`row_count` is incremented by `len(batch)` on every fetch that returns rows (L724). The final return `(row_count, first_ts, last_ts)` carries the count, and `run()` places it in the manifest's `rows` column at L1137. Empty-month short-circuit returns `(0, None, None)` WITHOUT opening the writer (no orphan `.tmp` on disk) — matches `_fetch_month_dataframe`'s `if df.empty: return df` semantics. Parity test: `test_stream_month_to_parquet_returns_counts_and_boundary_ts` asserts `row_count == N` for a non-empty month; `test_stream_month_to_parquet_empty_month_no_orphan` asserts the short-circuit contract.

### (d) BRT-naive preservation (R2-2) — PASS, stronger than pre-refactor

`_fetch_month_dataframe` used a post-hoc check (`if getattr(df["timestamp"].dt, "tz", None) is not None: raise`) AFTER loading into pandas. The refactored helper tightens this by:

1. Skipping the pandas layer entirely on the hot path (psycopg2 `datetime` tuples → `pa.array(ts_col, type=pa.timestamp("ns"))`). `pa.timestamp("ns")` is Arrow's naive nanosecond type (no `tz` parameter) — any tz-aware input would either raise in `pa.array` construction or strip the offset.
2. Adding a defense-in-depth check BEFORE `pa.array` is called: on the first batch, if `ts_col[0]` has `tzinfo is not None`, raise `RuntimeError("psycopg2 yielded tz-aware datetime; violates R2-2 BRT-naive timestamp contract")` — fail-closed BEFORE any parquet byte hits disk.

Parity + strengthening tests: `test_stream_month_to_parquet_writes_brt_naive` asserts the written parquet's `timestamp` field type is `timestamp[ns]` with `tz is None`; `test_stream_month_to_parquet_rejects_tz_aware_from_driver` injects an aware `datetime` and asserts `RuntimeError` is raised with a "BRT-naive" message before any output.

### (e) Pattern parity with `scripts/build_raw_trades_cache.py:_stream_month_to_parquet` — PASS

AST-level parity check performed on the function body; the following hot-path markers are byte-identical between the two helpers:

| Marker                                  | brc | mp  |
|-----------------------------------------|-----|-----|
| `SELECT timestamp, ticker, price, ...`  | ✓   | ✓   |
| `ORDER BY ticker, timestamp`            | ✓   | ✓   |
| `cur.itersize = 100_000`                | ✓   | ✓   |
| `compression='snappy'`                  | ✓   | ✓   |
| `version='2.6'`                         | ✓   | ✓   |
| `use_dictionary=True`                   | ✓   | ✓   |
| `write_statistics=True`                 | ✓   | ✓   |
| Empty-month short-circuit (`writer is None` path → no .tmp) | ✓ | ✓ |
| `pa.array(ts_col, type=pa.timestamp('ns'))` | ✓ | ✓ |
| `pa.array(price_col, type=pa.float64())`    | ✓ | ✓ |
| `pa.array(qty_col, type=pa.int32())`        | ✓ | ✓ |
| Per-batch `del ts_col, tick_col, ...`      | ✓ | ✓ |

The intentional differences between the two helpers:

1. **Cursor name:** `"materialize_stream"` (mp) vs `"cache_stream"` (brc). Preserves the pre-refactor `_fetch_month_dataframe` cursor name in the materialize script — intentional, no parity concern (cursor names are private to each connection).
2. **R2-2 defense-in-depth check:** mp adds explicit tz-aware rejection BEFORE the first `pa.array` call. brc does not — brc relies on `pa.array(..., type=pa.timestamp("ns"))` to implicitly fail. mp's check is strictly ADDITIVE hardening, never subtractive.
3. **Docstring length:** mp's docstring is slightly longer (cites `verify_parity.py` backward-compat explicitly). Not a hot-path difference.

No hot-path logic diverges. No determinism knob diverges. No schema-contract surface diverges.

---

## Latent invariant guard (L2283-L2286)

| Invariant | Pre-refactor sha256 | Post-refactor sha256 | Verdict |
|-----------|--------------------|-----------------------|---------|
| **[R1-1]** `core/memory_budget.py` CAP/R4/KILL constants byte-identical | `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` | `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` | **BYTE-IDENTICAL — PASS** |
| **Canonical data guard** `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | **BYTE-IDENTICAL — PASS** |

**[R2-1] Child-peak telemetry mechanism preserved — PASS.** `_collect_child_peak_memory` (psutil 7.2.2 + Windows `GetProcessMemoryInfo` fallback) and `_emit_child_peak_telemetry` are untouched. `main()`'s outer `try/finally` still wraps the `run()` dispatch and emits `TELEMETRY_CHILD_PEAK_EXIT` at exit. The refactor changes data-flow INSIDE the `run()` loop; it does not alter the process-exit emission contract. Dex verified by inspecting `scripts/materialize_parquet.py:main` — unchanged since T002.4 commit `80805ac5`.

**[R2-2] BRT-naive preserved — PASS** (reviewed above under (d)).

**[R3-1] Additive-only JSON keys — PASS.** The refactor emits zero new telemetry JSON fields. `TELEMETRY_CHILD_PEAK_EXIT` schema (`commit=`, `wset=`, `pid=`, `timestamp_brt=`, optional `error=`) is unchanged — the helper does not print any new telemetry line. `peak_wset_bytes` and `peak_pagefile_bytes` names from commit `80805ac5` are frozen; no rename, no removal.

---

## Mypy disposition (fairness note)

`python -m mypy scripts/materialize_parquet.py --ignore-missing-imports` reports two errors at `L1084` (post-refactor) — `args.cache_dir` / `args.cache_manifest` inferred as `Path | None` at the `_fetch_month_from_cache(...)` call site. These errors:

* **Pre-exist on `main`** at the equivalent line (L889 pre-refactor) — verified by `git stash` + mypy on the pre-refactor tree. Not a regression.
* Live in the cache-path branch (`is_cache_source=True`), which is **explicitly OUT OF SCOPE for RA-28-1 Decision 2** (cache files are 1-2 GiB and not the canonical-producer surface the RA targets).
* The `parse_args` function already rejects `--source=cache` without `--cache-dir` / `--cache-manifest` at `L308-L328`, so at runtime the values are non-None on the cache branch — mypy cannot infer this through the CLI validator.

Dara's disposition: **not a co-sign blocker.** The RA-28-1 P2 Quinn gate may choose to open a follow-up cleanup (e.g. add `assert args.cache_dir is not None` at the call site), but that is a style tightening and not a canonical-producer correctness issue.

---

## Tests

| Suite                                        | Pre-refactor | Post-refactor | Verdict |
|----------------------------------------------|--------------|---------------|---------|
| `tests/unit/` + `tests/t002_eod_unwind/` + `tests/core/` + `tests/contracts/` | 256/256 PASS | 265/265 PASS | PASS — zero regression, +9 new streaming-contract tests |
| `tests/unit/test_materialize_streaming_refactor.py` (new, 9 tests) | — | 9/9 PASS | PASS |

Ruff: clean on both changed files.

---

## Decision 2 pass-criterion traceback

From RA-28-1 L2293:

> Refactor commit landed on main [*branch off main for the dual co-sign workflow*]; Dex authors + Dara reviews & co-signs (Dara commit approval explicit); Quinn @qa-gate PASS on refactor diff (unit tests + regression + ruff + mypy); step-5 `peak_commit_aug2024` input measurement derived from REFACTORED child (no prior-to-refactor measurement acceptable)

Status:
* ✅ Refactor commit landed: `82fbf87372db57458081360d6a6cae10539d04da` on `ra-28-1/p1-streaming-refactor` (off `main@e94239a`). Per RA-28-1 workflow, the branch awaits @devops (Gage) exclusive push authority (R12) — R10 co-sign precedes push.
* ✅ Dex authors + Dara reviews & co-signs: this document is Dara's explicit commit approval.
* ⏳ Quinn @qa-gate PASS: pending P2 (Quinn's scope, not this P1 artefact).
* ⏳ Step-5 `peak_commit_aug2024` measurement: pending Stage-2 flip + Decision 3 execution by Gage (gated, not in P1 scope).

Fail-criterion test:

> Refactor regresses any existing sentinel-path invariant (schema, ordering, row count, BRT-naive timestamps) → halt, Quinn CONCERNS + Dara block; if Dara DOES NOT co-sign → R10 violation, halt, escalate

None of the four invariants is regressed (verified above under (a)-(d)). Dara co-signs.

---

## Sign-off

**Dara (@data-engineer, The Architect) — R10 custodial co-sign: APPROVED**

Scope discipline: this co-sign is scoped to RA-28-1 P1 (Decision 2) only. It authorizes the commit `82fbf87` for Quinn's P2 gate consumption; it does NOT authorize push (Gage R12 exclusive) and does NOT authorize Decision 3 sentinel-path baseline invocation (Stage-2 gated).

Article IV (No Invention) compliance: every review claim above traces to either the RA-28-1 text (§R10 Amendment in `docs/architecture/memory-budget.md`), the binding pattern source (`scripts/build_raw_trades_cache.py:_stream_month_to_parquet`), the canonical schema (`materialize_parquet._build_parquet_schema`), or test evidence in `tests/unit/test_materialize_streaming_refactor.py`. No invented invariants, no invented determinism knobs, no invented schema columns.

Co-signed in the custodial dual-agent split protocol: first-of-its-kind Dex (@dev) + Dara (@data-engineer) joint R10 sign-off pattern established under RA-28-1 Decision 2 territorial split (agent-authority.md L59-L73 — Dara owns schema/DDL/query-optimization; Dex owns implementation).
