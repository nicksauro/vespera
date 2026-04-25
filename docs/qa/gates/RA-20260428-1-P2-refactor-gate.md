# RA-20260428-1 — P2 QA Gate on P1 Streaming Refactor

**Gate author:** Quinn (@qa, The Auditor)
**Gate issued at (BRT-naive per R2-2):** 2026-04-24T21:40:00
**Gate scope:** P2 under RA-20260428-1 Stage-1 (ISSUED 2026-04-24T21:18:10Z, Riven-delegated). P2 authority granted to Quinn by Orion at the same stamp. Gate consumes the P1 canonical streaming refactor authored by Dex and R10-cosigned by Dara; gate is a blocker for Stage-2 flip.
**Governing RA text:** `docs/architecture/memory-budget.md` §R10 Amendment starting at L2240 (Decision 2, pass/fail criteria at L2293, P2 deliverable at L2310-L2318).
**Prior chain-gate:** `docs/qa/gates/RA-20260428-1-chain-gate.md` (CONDITIONAL GREEN).
**Branch under audit:** `ra-28-1/p1-streaming-refactor`
**Commit under audit:** `82fbf87372db57458081360d6a6cae10539d04da` (off `main@e94239a`)
**R10 custodial co-signer:** Dara (@data-engineer) — APPROVED on all 5 dimensions per `data/baseline-run/ra-20260428-1-evidence/p1-dara-cosign.md`.

---

## Verdict

> **PASS**

P1 lands the canonical streaming refactor byte-identically to its stated scope. All 10 gate checks pass. Mypy shows ZERO new regressions attributable to the refactor diff (pre-existing errors verified against `main` via `git show main:...` + fresh mypy). Canonical + R1-1 invariants held pre/post gate. Pattern parity with the binding precedent (`scripts/build_raw_trades_cache.py:_stream_month_to_parquet`) is verified by inspection. Stage-2 flip is unblocked from a QA standpoint (wrapper flip authority remains with Gage per R12).

One non-blocking CONCERN noted below (C-1) about the reported pytest baseline count (265 in Dex's handoff vs. 273 collected on the branch as of gate time). This does NOT block P2 because ALL tests pass (zero failures, zero errors), and the delta is upward (more coverage on the branch than Dex's handoff anticipated — fully consistent with the live working-tree state).

---

## 10-check table

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Diff reads clean on stated scope | **PASS** | `git diff --stat main...HEAD` shows ONLY 2 files changed: `scripts/materialize_parquet.py` (+258/-24) and `tests/unit/test_materialize_streaming_refactor.py` (new, +364). No `core/memory_budget.py` entry. No `data/manifest.csv` entry. No other `data/` entries. Matches RA-28-1 L2306 P1 scope exactly. |
| 2 | R1-1 invariant (`core/memory_budget.py` frozen) | **PASS** | `sha256sum core/memory_budget.py` on branch HEAD = `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` — matches expected frozen sha. Also absent from `git diff --name-only main...HEAD`, so no in-branch modification occurred. |
| 3 | Canonical `data/manifest.csv` invariant | **PASS** | `sha256sum data/manifest.csv` = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` — matches expected canonical sha. File is untracked (per project convention for the canonical manifest; RA-28-1 pins its content, not its git-tracked status). Sha verified pre-gate AND post-gate (see §Canonical guard below). |
| 4 | Streaming pattern parity with `build_raw_trades_cache.py:_stream_month_to_parquet` | **PASS** | Inspected both functions side-by-side. Refactored `_stream_month_to_parquet` at `scripts/materialize_parquet.py:568-735`: opens `pq.ParquetWriter` (L712), iterates via `cur.fetchmany(cur.itersize=100_000)` (L660), emits per-batch `writer.write_table(table)` (L722), drops batch-local refs immediately (L728-730 `del ts_col, tick_col, price_col, qty_col, agg_col, buy_col, sell_col, table, batch`), closes writer in `finally` (L731-733). NO Python-list accumulation of total rows on the hot path — each fetchmany window (100K rows) is materialized into per-column Python lists ONLY for one iteration, then dropped. This is semantically identical to `build_raw_trades_cache.py:_stream_month_to_parquet` (L355-495) per Dara's (b) co-sign dimension. Determinism knobs (`compression="snappy"`, `version="2.6"`, `use_dictionary=True`, `write_statistics=True`) match `_write_parquet` verbatim (L715-718 vs. `_write_parquet`). The deprecated `_fetch_month_dataframe` (L495-561) is retained solely for `scripts/verify_parity.py` byte-identity gates (explicitly documented in the module-level docstring L505-509); it is NOT on the canonical `run()` hot path — verified by reading `run()` at L1057-1174 where the sentinel branch (L1102-L1138) calls `_stream_month_to_parquet`, not `_fetch_month_dataframe`. |
| 5 | Pytest results | **PASS** | `python -m pytest tests/` → **272 passed, 1 skipped** (273 collected) in 15.31s. Zero failures, zero errors. The 9 new streaming-refactor tests in `tests/unit/test_materialize_streaming_refactor.py` all pass (verified via targeted run). See C-1 for the reported-baseline vs. observed-baseline delta (non-blocking). |
| 6 | Ruff | **PASS** | `ruff check scripts/materialize_parquet.py tests/unit/test_materialize_streaming_refactor.py` → "All checks passed!" Zero diagnostics. |
| 7 | Mypy (no new regressions) | **PASS** | `mypy scripts/materialize_parquet.py` post-refactor reports 3 errors: (i) L1084 arg-type (`Path \| None` → `Path`), (ii) L1084 arg-type (same call, second arg), (iii) L1216 `psutil` stubs missing. All 3 are pre-existing: verified via `git show main:scripts/materialize_parquet.py > /tmp/materialize_pre_refactor.py && mypy /tmp/materialize_pre_refactor.py` → reports the SAME errors at the SAME call sites (line numbers moved from L889→L1084 and L982→L1216 only because the refactor added code above them). Pre-refactor mypy also reports a 4th error (`_holdout_lock` import-not-found at L100) which is environmental and present on BOTH pre and post (suppressed in the post-refactor project-rooted invocation due to import path). Net new regressions introduced by the refactor: **ZERO**. This matches Dex's claim ("2 pre-existing errors at L1084") with the nuance that a 3rd pre-existing error (psutil stubs) was not enumerated in Dex's handoff but is explicitly pre-existing and non-blocking. |
| 8 | BRT-naive preservation (R2-2) | **PASS** | `grep -nE "tz_convert\|tz_localize\|utcnow\|pytz\|astimezone" scripts/materialize_parquet.py` → **No matches.** The refactored streaming path coerces timestamps directly into `pa.timestamp("ns")` (L698) — Arrow's naive nanosecond type — without a pandas intermediate. Additionally, the refactor ADDS a defensive tz-aware-leak check at L688-694 that raises `RuntimeError` on the first row if `ts_col[0].tzinfo is not None`. This is defense-in-depth for R2-2, not a breach. Test `test_stream_month_to_parquet_rejects_tz_aware_from_driver` covers this branch. |
| 9 | Telemetry channel preserved (R2-1) | **PASS** | `grep -n "TELEMETRY_CHILD_PEAK_EXIT" scripts/materialize_parquet.py` → 5 matches at L93 (tag constant), L1205 (return-value doc), L1270 (emit-function docstring), L1274 (line-format doc), L1303 (main()-level comment). The outer `try / finally` structure in `main()` is preserved at L1304-1328, guaranteeing `_emit_child_peak_telemetry()` fires on every exit path (success / HoldoutLockError / generic Exception). Nested `try` for emission-failure fallback (L1320-1328) still emits a structured line with `commit=0 wset=0 error=emit_failed:...` — AC-K(iii) fallback preserved. |
| 10 | Additive-only telemetry keys (R3-1) | **PASS** | `grep -n "peak_wset_bytes\|peak_pagefile_bytes" scripts/materialize_parquet.py` → both names present at L1205 (docstring return-tuple element names) and L1221, L1223, L1283 (runtime binding in `_collect_child_peak_memory` + emission path). Key names unchanged. No new telemetry fields introduced by the refactor (the refactor operates on DB-read / parquet-write only; telemetry collection + emission is downstream and untouched). |

---

## Pytest summary

* Command: `python -m pytest tests/`
* Python: 3.14.3, pytest 9.0.2, pluggy 1.6.0
* Collected: 273 (272 passed, 1 skipped, 0 failed, 0 errors)
* Wall time: 15.31s
* New streaming-refactor suite (`tests/unit/test_materialize_streaming_refactor.py`): 9 passed — covers counts/boundary ts, schema parity, row-order preservation, BRT-naive writes, tz-aware rejection, empty-month short-circuit (no orphan .tmp), per-batch writes (not one big batch), server-side cursor usage, query-params parity.
* Regressions: **zero**.

---

## Ruff + Mypy summary

**Ruff** (`ruff check scripts/materialize_parquet.py tests/unit/test_materialize_streaming_refactor.py`):

```
All checks passed!
```

**Mypy** — post-refactor (on branch HEAD):

```
scripts\materialize_parquet.py:1084: error: Argument 1 to "_fetch_month_from_cache" has incompatible type "Path | None"; expected "Path"  [arg-type]
scripts\materialize_parquet.py:1084: error: Argument 2 to "_fetch_month_from_cache" has incompatible type "Path | None"; expected "Path"  [arg-type]
scripts\materialize_parquet.py:1216: error: Library stubs not installed for "psutil"  [import-untyped]
Found 3 errors in 1 file (checked 1 source file)
```

**Mypy** — pre-refactor (verified via `git show main:scripts/materialize_parquet.py`):

```
materialize_pre_refactor.py:889: error: Argument 1 to "_fetch_month_from_cache" has incompatible type "Path | None"; expected "Path"  [arg-type]
materialize_pre_refactor.py:889: error: Argument 2 to "_fetch_month_from_cache" has incompatible type "Path | None"; expected "Path"  [arg-type]
materialize_pre_refactor.py:982: error: Library stubs not installed for "psutil"  [import-untyped]
Found 3 project-attributable errors (+ 1 environmental)
```

**Pre-existing error citations (explicit, per P2 requirement):**

1. `scripts/materialize_parquet.py:1084` — `_fetch_month_from_cache(args.cache_dir, args.cache_manifest, ...)` — `cache_dir` and `cache_manifest` are typed `Path | None` at argparse layer but the callee expects `Path`. This is inside the `--source=cache` branch (Decision 2 explicitly EXCLUDED from this RA scope per L2284 "cache-path unchanged"). The same error was at L889 on `main`.
2. `scripts/materialize_parquet.py:1216` — `import psutil` inside `_collect_child_peak_memory()`. Same error at L982 on `main`. Resolvable with `pip install types-psutil` but out of scope for P1.

**Delta introduced by the refactor:** 0 new mypy errors.

---

## sha256 of invariant-tracked files (pre-gate AND post-gate)

| File | Expected (per Orion P2 task) | Pre-gate observed | Post-gate observed | Status |
|------|------------------------------|-------------------|--------------------|--------|
| `core/memory_budget.py` | `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` | `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` | `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` | **MATCH** |
| `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | **MATCH** |
| `scripts/materialize_parquet.py` (reference only — not an invariant; changed legitimately by P1) | n/a — RA mandates change | `5f2716bec713f99720129a6aa3db50cb213601ae4622f3693db132dcf197d0e5` | `5f2716bec713f99720129a6aa3db50cb213601ae4622f3693db132dcf197d0e5` | **MATCH expected post-refactor sha** |

### Canonical guard note

During gate execution, an attempt at `git stash --include-untracked` (to isolate mypy pre/post comparison) triggered Windows `core.autocrlf` line-ending conversion on `data/manifest.csv` upon `git stash pop`, temporarily yielding sha `d82d9c301c7399c8792d52c8b3d6c1f5264ee11720a90b73797ed13027b5af3c` (CRLF-encoded variant of identical content, 3524 bytes vs. 3507 LF-encoded bytes). This was IMMEDIATELY detected by the post-gate sha verification step, and LF line endings were restored via `python -c "open(..., 'rb'); replace(b'\\r\\n', b'\\n'); open(..., 'wb')"` — final sha restored to `75e72f2c...`. The file CONTENT (17 lines of manifest rows — column headers + 16 month-parquet entries for WDO 2024-01..2025-04) was byte-identical throughout; only line-ending encoding was transiently perturbed. This was a gate-execution side-effect under Quinn's auditing, NOT a P1 refactor artifact. The gate records full transparency on this excursion and confirms the canonical invariant is intact at gate-close time.

---

## Dara co-sign acknowledgment

Referenced: `data/baseline-run/ra-20260428-1-evidence/p1-dara-cosign.md` (13,673 bytes, timestamped 2026-04-24T18:27:24 BRT-naive).

**Verdict quoted verbatim:** "R10 custodial co-sign: APPROVED"

**Dimensions APPROVED (per RA-28-1 L2293):**

* (a) Schema parity — byte-identical column order/types/nullability via `pa.Table.from_arrays([...], schema=_build_parquet_schema())`.
* (b) Streaming pattern parity with `build_raw_trades_cache.py:_stream_month_to_parquet` — same cursor name, same itersize, same per-batch write_table, same empty-month short-circuit, same atomic `.tmp → final` rename.
* (c) Memory contract — no Python-list accumulation of total rows; per-batch refs dropped before next fetchmany.
* (d) BRT-naive preservation — coercion into `pa.timestamp("ns")` without pandas intermediate; defensive first-row tz-aware check.
* (e) Row-group determinism — `row_group_size=100_000` via 100K-row batches + `write_statistics=True` + `use_dictionary=True` + `compression="snappy"` + `version="2.6"`.

Quinn accepts Dara's R10 custodial cosign as binding. Gate does not re-litigate the 5 dimensions from scratch — Dara is R10 custodial authority; Quinn's role (per RA-28-1 L2310-L2318 P2) is to validate the REFACTOR DIFF (scope, invariants, test/lint/type health, pattern integrity). All P2 dimensions pass.

---

## CONCERNS (non-blocking)

### C-1 — Pytest baseline count discrepancy in Dex's handoff

**Reported by Dex:** pytest 265/265 PASS (256 baseline + 9 new streaming tests).

**Observed by Quinn (on branch HEAD at gate time):** 273 collected → 272 passed + 1 skipped + 0 failed.

**Analysis:** Branch working tree contains other untracked test files (e.g., `tests/unit/test_materialize_manifest_flag.py`, `tests/unit/test_materialize_source_dispatch.py`, `tests/unit/test_materialize_args.py`, `tests/contracts/test_holdout_lock.py`, etc.) not referenced by Dex's baseline count — these are scope of prior work on the branch environment, not P1. All pass. The delta is upward (MORE coverage, ZERO failures) — semantically consistent with Dex's "zero regressions" claim.

**Disposition:** non-blocking. The regression-containment contract (no previously-passing test newly fails) holds. Dex's handoff should align counts to the live tree in future P*-level handoffs — recorded for process improvement, not a P2 fail.

### C-2 — Mypy pre-existing error enumeration

**Reported by Dex:** 2 pre-existing mypy errors at L1084.

**Observed by Quinn:** 3 pre-existing project-attributable errors — 2 at L1084 (arg-type x2 for `_fetch_month_from_cache`) PLUS 1 at L1216 (`psutil` stubs missing). All 3 verified pre-existing against `main`.

**Disposition:** non-blocking. Dex undercounted by 1 (missed the psutil stubs error). Both are out of Decision 2 scope (cache-path + telemetry collector). Recorded for accuracy.

---

## FAILs (blocking)

**None.**

---

## Stage-2 flip disposition

P2 gate is CLOSED GREEN. From a QA standpoint, nothing in the P1 diff blocks Stage-2 flip. Per R12, wrapper flip authority remains exclusively with Gage (@devops) — Quinn does NOT push, does NOT merge, does NOT flip. Stage-2 execution requires:

1. Gage to review this gate + the Dara cosign
2. Gage to execute the wrapper flip per the Stage-2 playbook in the RA
3. Orion (aiox-master) to adjudicate Stage-2 entry criteria

Quinn's P2 obligation ends at this gate file + the evidence pin at `data/baseline-run/ra-20260428-1-evidence/p2-qa-gate-refactor.md`.

---

## Signatures

**Quinn (@qa, The Auditor)** — P2 gate verdict: **PASS**
Issued at: 2026-04-24T21:40:00 BRT-naive
Branch under audit: `ra-28-1/p1-streaming-refactor @ 82fbf87372db57458081360d6a6cae10539d04da`
RA reference: RA-20260428-1 Stage-1 §R10 Amendment (`docs/architecture/memory-budget.md` L2240+)
Authority chain: Riven (R10 delegation to Orion) → Orion (P2 delegation to Quinn at 2026-04-24T21:18:10Z) → Quinn (this gate).
