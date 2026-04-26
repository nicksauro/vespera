---
report_id: T002-beckett-t11-smoke-report-2026-04-26
story_id: T002.0f
agent: Beckett (@backtester)
task: T11 — execução final do smoke `*run-cpcv --dry-run --smoke` contra baseline pre-flight audited
date_brt: 2026-04-26T03:11 BRT
verdict: HOLD
authority: |
  Beckett — backtester & execution simulator authority. Article IV
  (No Invention) is absolute. Smoke run executed exactly per the
  Quinn-PASS-validated CLI contract; smoke aborted (exit 1) at the
  warmup-gate fail-closed boundary because warmup state files were
  never materialized for the smoke window's `as_of_date`. NOT a code
  defect — a real upstream integration gap surfaced by the gate.
  Beckett refuses to fabricate warmup state.
---

# T002.0f T11 — CPCV Smoke Report (2026-04-26)

## 1. Smoke command executed

```bash
python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --smoke \
  --in-sample-end 2025-06-30 \
  --seed 42
```

Per CLI contract (`run_cpcv_dry_run.py:858-859`), `--smoke` derives the
window as `[in_sample_end - 30d, in_sample_end] = [2025-05-31, 2025-06-30]`
when `--in-sample-start` is omitted. `--in-sample-end 2025-06-30` is the
last in-sample day per spec `data_splits.in_sample` and sits BEFORE the
hold-out start `2025-07-01` (R1 + R15(d) compliant).

## 2. Pre-conditions verified

| # | Pre-condition | Expected | Observed | Match |
|---|---------------|----------|----------|-------|
| 1 | `data/manifest.csv` SHA-256 | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` | YES |
| 2 | Spec parent (`v0.2.0.yaml`) `mira_signature_sha256_of_file_before_this_line` (line-11) | `4b5624ad…dc3fc` | `4b5624ad6ba151c57e263f1d160d7e802354c5e164f777198755b70c59bdc3fc` (line-11) | YES |
| 2b | Spec parent — whole-file SHA-256 (the value `compute_spec_sha256` writes into `determinism_stamp.json`) | (separate convention) | `98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614` — **matches design doc §13 `spec_hash`** and audit `AUDIT-20260425-PRE-DRYRUN-CPCV.md:30` | YES |
| 3 | `T002-vespera-metrics-spec.md` Mira-signature (header) | `bc43487c…4cc59` | `bc43487ca247deee9c0ab3f7f50a8bdbebe9f4b2dee462c1fc61f28c4324cc59` (line-11) | YES |
| 3b | Vespera-metrics-spec — whole-file SHA-256 | (separate convention) | `f03060bc9cbd648fdcb3381bcc10fe167c2d87a92ed0037878d551ba45167701` | YES (consistent w/ Mira signing convention) |
| 4 | `docs/ml/research-log.md` v0.1 exists (Mira pre-condition T2) | exists | 5315 bytes, owner=Mira; ledger header L1-L24 verified | YES |
| 5 | `nova-cost-atlas.yaml` LF-normalized SHA-256 | `acf44941…a5126` | `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126` | YES |
| 6 | `data/in_sample/year=2025/month=06/` parquet | exists | `wdo-2025-06.parquet` present | YES |
| 7 | `_holdout_lock.py` constants | `HOLDOUT_START=2025-07-01`, `HOLDOUT_END_INCLUSIVE=2026-04-21` | Same (lines 39-40) | YES |

**All 7 pre-conditions PASS.** The two "signature" entries (#2 / #3) initially looked like
mismatches because the values cited in the task brief are Mira's
**embedded auto-referential** signatures (sha256 of the file content
*before* the signature line itself) — a different convention from the
**whole-file** sha256 the runner uses. Both conventions match
documented audit AUDIT-20260425-PRE-DRYRUN-CPCV.md L30
("Both shas valid under different conventions; cross-reference
consistent across EPIC + spec + design").

## 3. Smoke metrics — observed

| Metric | Observed | Notes |
|--------|----------|-------|
| Exit code | **1** | HALT per AC11 (smoke aborted; full skipped) |
| Wall-clock duration | **~3.06 s** (`real 0m3.058s`) | well below 5-min smoke ceiling |
| Peak RSS | **~142.00 MB** (`peak_commit_bytes=148893696`) | <<6 GiB soft cap; soft-halt did NOT fire |
| Peak VMS | **~592.32 MB** (`peak_wset_bytes=621096960`) | informational |
| Soft halt fired? | **NO** (`halt_observed=False` in run_end row) | confirms RSS path not the trigger |
| Telemetry samples | 5 rows (run_start + init poll + smoke:events_start + smoke_failed + run_end) | all 12 superset columns present |
| FullReport produced? | **NO** | smoke aborted in `_run_phase` BEFORE `compute_full_report` was reached |
| KillDecision verdict | **N/A** | no FullReport |
| PBO scalar | **N/A** | no FullReport |
| DSR | **N/A** | no FullReport |
| IC Spearman | **N/A** | no FullReport |
| Run dir created | `data/baseline-run/cpcv-dryrun-auto-20260426-d2098a3d865b/` | derived deterministically per `derive_default_run_id` |
| Artifacts persisted | **1 of 5** (`telemetry.csv` only) | `full_report.{md,json}`, `determinism_stamp.json`, `events_metadata.json` NOT written — `persist_artifacts` only runs after report compute (correct fail-closed behavior) |

### Aborting stack trace (verbatim from stderr)

```
ERROR: smoke phase failed; aborting full run per AC11: warmup not satisfied
for 2025-05-31: status=WARM_UP_IN_PROGRESS, reason=state files not yet produced
```

### Telemetry CSV (full content — 5 rows)

```
timestamp_brt,rss_mb,vms_mb,cpu_pct,peak_commit_bytes,peak_wset_bytes,sample_size,duration_ms,fold_index,trial_id,phase,note
2026-04-26T03:11:30,141.95,592.27,0.00,148844544,621039616,1,0,-1,,run_start,run_id=auto-20260426-d2098a3d865b;spec_sha=98f22f3c8cee
2026-04-26T03:11:30,141.99,592.32,0.00,148885504,621092864,2,0,-1,,init,poll
2026-04-26T03:11:30,141.99,592.32,0.00,148889600,621096960,3,0,-1,,smoke:events_start,window=2025-05-31..2025-06-30
2026-04-26T03:11:30,142.00,592.32,0.00,148893696,621096960,4,0,-1,,smoke_failed,"reason: smoke_aborted: RuntimeError: warmup not satisfied for 2025-05-31: status=WARM_UP_IN_PROGRESS, reason=state files not yet produced"
2026-04-26T03:11:30,142.00,592.32,0.00,148893696,621096960,5,0,-1,,run_end,halt_observed=False
```

The CSV header matches the canonical superset (Pax gap #2) — 12 columns
verified: `timestamp_brt, rss_mb, vms_mb, cpu_pct, peak_commit_bytes,
peak_wset_bytes, sample_size, duration_ms, fold_index, trial_id, phase, note`.

## 4. Re-determinism check

A second invocation of the **same command** produced **identical**
behavior — same stderr message, same exit code 1. Run directory
re-derivation is deterministic (`derive_default_run_id` is a sha256 of
`spec_sha|in_sample_start|in_sample_end|seed`), so the second run
landed in the same `cpcv-dryrun-auto-20260426-d2098a3d865b/`
directory. `MemoryPoller` truncates `telemetry.csv` on construction
(line 376-381) so the file was rewritten cleanly — no merge of stale
poller history (Article IV alignment: "we never silently merge poller
history across runs").

**Re-determinism caveat:** because no `FullReport` or
`DeterminismStamp` was emitted (smoke aborted before fan-out),
the canonical AC4 byte-equality check on `content_sha256` of the
225 BacktestResults could NOT be performed in this T11 run. AC4
remains **proven via Quinn's tests** (`test_three_runs_byte_identical_content_sha256`
in `tests/cpcv_harness/test_5_trial_fanout.py`) but **not yet
validated against real backtest_fn at smoke window scale**. This
remains a T11 gating responsibility per Quinn QA-gate L99
("AC10 wall-clock <5min on i5/16GB hardware is gated to Beckett
T11 re-run with real backtest_fn").

## 5. Root-cause analysis — why smoke aborted

### Diagnostic sequence

1. CLI `main()` parsed args, computed `spec_sha256 = 98f22f3c…24614`,
   resolved smoke window `[2025-05-31, 2025-06-30]`.
2. AC9 hold-out lock (`assert_holdout_safe`) PASSED — both window
   bounds < `2025-07-01`.
3. AC13 spec sha256 lock PASSED — first run in `cpcv-dryrun-auto-20260426-d2098a3d865b/`.
4. Calendar (`config/calendar/2024-2027.yaml`) loaded OK; `WarmUpGate`
   constructed with default paths.
5. `MemoryPoller` started (daemon thread, 30s cadence).
6. Smoke phase entered: `build_events_dataframe` invoked
   (`cpcv_harness.py:149-261`).
7. `assert_warmup_satisfied(in_sample_start=2025-05-31)` called
   (`cpcv_harness.py:222`).
8. `WarmUpGate.check(2025-05-31)`:
   - `_check_file(data/warmup/atr_20d.json, 2025-05-31)` → `(False, "missing")`
   - `_check_file(data/warmup/percentiles_126d.json, 2025-05-31)` → `(False, "missing")`
   - both `missing` ⇒ status `WARM_UP_IN_PROGRESS`, reason `"state files not yet produced"`
   (per `gate.py:64-70` — fail-closed contract validated by
   `test_both_files_missing_returns_in_progress`).
9. `assert_warmup_satisfied` raised `RuntimeError` (per `cpcv_harness.py:138-142`).
10. `_run_phase` `except Exception` (line 873) caught → `smoke_failed`
    telemetry row written → stderr message → `return 1` (AC11).

**The warmup gate did exactly what its fail-closed contract
prescribed.** Quinn's tests already prove this path works; what they
could NOT prove is whether the **production state materialization**
upstream had run.

### Where the warmup state lives (or should)

Two filesystem paths are in play:

| Source | Default warmup state path | Status on disk |
|--------|---------------------------|----------------|
| `cpcv_harness.py:94-95` (used by `assert_warmup_satisfied`) | `data/warmup/atr_20d.json` and `data/warmup/percentiles_126d.json` | **directory `data/warmup/` does NOT exist** |
| `run_cpcv_dry_run.py:117-118` (CLI defaults for `--warmup-atr` / `--warmup-percentiles`) | same as above | same |
| T002.1 spec / QA gate AC4 (per `T002.1-qa-gate.md` L42 + `T002.1.story.md` L25, L218, L316, L326) | `state/T002/atr_20d.json` and `state/T002/percentiles_126d.json` | dir exists with only `.gitkeep`; **no state files** |

**Two gaps surface simultaneously:**

1. **PATH MISMATCH (cosmetic):** T002.1 specifies `state/T002/*.json`; T002.0f
   (cpcv_harness + CLI) defaults to `data/warmup/*.json`. Even if the
   builder had run, the gate would not find the file unless the operator
   supplied `--warmup-atr state/T002/atr_20d.json --warmup-percentiles state/T002/percentiles_126d.json`.
2. **STATE NEVER MATERIALIZED (substantive):** Neither path contains the JSON
   state files for `as_of_date=2025-05-31`. `ATR20dBuilder` and
   `Percentiles126dBuilder` are pure-compute modules that require a
   `trades` iterable from the caller (per `atr_20d_builder.py` module
   docstring L10-14). No production orchestrator has yet been wired
   to: (a) pull historical trades for the smoke window, (b) run both
   builders, (c) persist the state. T002.1 shipped the building blocks;
   T002.4 is the integrating story; T002.0f's smoke pre-supposes that
   integration has happened.

Neither gap was visible to Quinn's QA gate because:
- T002.1 tests use synthetic in-memory fixtures (per `T002.1-qa-gate.md`
  edge-case matrix — `test_persist_and_load_roundtrip × 2`).
- T002.0f tests for `assert_warmup_satisfied` inject a stub `WarmUpGate`
  via the `gate=` parameter (avoiding the disk default).
- T002.0f's `test_smoke_completes_with_mock_pipeline` patches
  `build_events_dataframe` and `compute_full_report` to skip the
  warmup IO entirely (per Quinn QA-gate L99 — explicitly deferred to
  T11 re-run).

This is the **first integration test that actually exercises the
production warmup IO path with the real spec window**, and it
correctly surfaced both gaps.

## 6. T11 verdict — **HOLD**

### Summary

| Smoke acceptance criterion (per task brief §6) | Result |
|------------------------------------------------|--------|
| Exit code 0 | **FAIL** — exit 1 (HALT per AC11) |
| 5 artifacts persisted | **FAIL** — only `telemetry.csv` (1 of 5); the other 4 require a successful `compute_full_report` which never ran |
| FullReport contains `KillDecision` (verdict ∈ {GO, NO_GO}) | **FAIL** — no FullReport |
| PBO scalar finite (not NaN) | **FAIL** — no metric |
| DSR finite | **FAIL** — no metric |
| Peak RSS < 6 GiB | **PASS** — ~142 MB |
| Smoke completed in <5 min | **N/A** — completed in 3 s, but failed early |
| Re-determinism: identical behavior on second run | **PASS** (caveat: only stderr + exit code re-tested; no FullReport to byte-compare) |

**4 of 8 acceptance criteria PASS; 4 of 8 FAIL because the smoke aborted
at the warmup gate before any modeling work could run.** Per Article IV,
I refuse to fabricate state files (`data/warmup/atr_20d.json`,
`data/warmup/percentiles_126d.json`) just to make the gate clear —
that would invalidate the entire backtest by injecting unsigned
provenance. The fail-closed gate is doing exactly what it must.

### Verdict: **HOLD pending warmup-state materialization**

T11 cannot certify "ready for 12-month full" until the warmup state
problem is resolved upstream. The downstream pipeline (`build_events_dataframe`
→ fan-out → `compute_full_report`) was never reached — its real-data
behavior remains UNVALIDATED at smoke window scale. The QA-gated
mock test (`test_smoke_completes_with_mock_pipeline`) is necessary
but not sufficient evidence per Quinn's own L99 caveat.

### Open issues for escalation

| # | Issue | Owner | Severity | Action |
|---|-------|-------|----------|--------|
| 1 | Warmup state never materialized for any `as_of_date` (no orchestrator wired) | T002.4 (Tiago, per T002.0f deps L160 mapping or whoever owns the warmup-IO bootstrap) | **BLOCKING** | Run `ATR20dBuilder` + `Percentiles126dBuilder` against historical trades for `as_of_date=2025-05-31` (smoke) AND `as_of_date=2024-06-30` (full's in-sample-start - 1) and persist JSON. Then re-run T11. |
| 2 | Path mismatch: T002.1 ships to `state/T002/`; T002.0f defaults read from `data/warmup/` | Pax / SM (Aria architecture review) — needs `breaking_fields` revision in T002.1 and/or T002.0f to align canonical paths | **HIGH** (cosmetic but bisectable confusion source) | Pick ONE canonical path. Recommend `state/T002/` (matches T002.1 AC4 + already has dir + .gitkeep). Update `cpcv_harness.py:94-95` and `run_cpcv_dry_run.py:117-118`. |
| 3 | `_load_warmup_state` (CLI L503-548) silently falls back to neutral stub `Percentiles126dState` if file missing — bypasses gate logic | Beckett note for T002.0f housekeeping | **LOW** (does not affect smoke because the gate fires FIRST in `build_events_dataframe`, BEFORE `_load_warmup_state` is reached) | Tighten in housekeeping pass: when `_load_warmup_state` is called from production path AND state file is missing, raise rather than fall back. The current fallback was a T11-deferred convenience for the test-mock pipeline. |
| 4 | Re-determinism could not validate FullReport byte-equality (Quinn QA-gate L99 deferral) | Beckett (T11 retry post-issue-1 fix) | **HIGH** (T11 gating per Quinn L99) | Once issues 1-2 cleared, re-run smoke; capture `determinism_stamp.json` `dataset_hash` + PBO scalar across 2 runs and assert byte-equality. |

### Article IV trace — every executive decision justified

| Decision | Source / Reason |
|----------|-----------------|
| Did NOT retry on first exit-1 | Task brief §IMPORTANTE: "Se exit code != 0 → NÃO retry. Capture diagnostic completo e reporte." |
| Did NOT fabricate `data/warmup/*.json` to bypass gate | Article IV (No Invention) + Beckett core_principle: "Sem book histórico... worst-case sempre". Synthetic warmup state would violate spec provenance + invalidate every downstream metric. |
| Did NOT switch CLI to `--warmup-atr state/T002/atr_20d.json` workaround | (a) file doesn't exist there either; (b) workaround would mask the path-mismatch issue from escalation. |
| Did NOT modify any production code | T11 brief is pure execution authority; code changes belong to T002.4 / Pax / SM revision flow per R15 (spec is append-only — breaking_fields revision required). |
| Did NOT run `--no-smoke` to skip directly to full run | Same warmup gate fires in full phase (`_run_phase` is shared body). Full run would abort identically + waste time. |
| Did NOT bypass via `VESPERA_UNLOCK_HOLDOUT` env var | Hold-out lock was NOT the blocker; bypass would be irrelevant + contraband to R1+R15(d). |
| Did record full diagnostic in this report (root cause, dir comparison, actual vs documented paths) | Backtester core_principle: "Backtest não-reproduzível é inútil. Seed fixa, dataset versionado, simulador versionado." Reporting reproducibility evidence + failure surface is mandatory. |

### Reproducibility envelope (what IS already locked)

Even though smoke didn't reach FullReport, this run produced enough
provenance for any operator to reproduce the abort byte-identically:

- **Seed:** 42
- **Simulator version:** `cpcv-dry-run-T002.0f-T3` (per `_build_runner` L578)
- **Dataset hash (manifest.csv):** `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`
- **Spec sha256 (whole-file, runner convention):** `98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614`
- **Spec Mira-signature (auto-referential, header line-11):** `4b5624ad6ba151c57e263f1d160d7e802354c5e164f777198755b70c59bdc3fc`
- **Cost-atlas LF sha:** `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126`
- **Calendar:** `config/calendar/2024-2027.yaml` (loaded OK)
- **Hold-out lock constants:** `HOLDOUT_START=2025-07-01, HOLDOUT_END_INCLUSIVE=2026-04-21`
- **CPCV config (would-have-been):** `N=10, k=2, embargo=1, n_paths=45` (per spec `data_splits.in_sample` parsing — never reached fan-out)
- **Run dir (deterministic):** `data/baseline-run/cpcv-dryrun-auto-20260426-d2098a3d865b/`
- **Python:** 3.14.3 / **psutil:** 7.2.2

## 7. Recommendation to operator (next steps for unblock)

1. **Materialize warmup state** for `as_of_date=2025-05-31` (smoke) and
   `as_of_date=2024-06-30` (full in_sample_start - 1):
   - Open T002.4 (or whatever the warmup-bootstrap story is named).
   - Wire ProfitDLL `GetHistoryTrades` worker-thread fetch → builder
     compute → `to_json()` persist.
   - Land state files at the canonical path (recommend `state/T002/` per
     T002.1 AC4).
2. **Decide canonical warmup path** and update both `cpcv_harness.py:94-95`
   and `run_cpcv_dry_run.py:117-118` if needed (Pax-led R15 breaking_fields
   revision flow if it touches T002.1 or T002.0f signed contract).
3. **Re-run T11**:
   ```bash
   python scripts/run_cpcv_dry_run.py \
     --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
     --dry-run --smoke --in-sample-end 2025-06-30 --seed 42
   ```
   (or with explicit `--warmup-atr` / `--warmup-percentiles` overrides
   pointing at `state/T002/`).
4. **Capture re-run #1 + re-run #2** in same run-id dir → verify
   `determinism_stamp.json.spec_sha256` byte-identical between runs +
   `full_report.json.metrics.pbo` byte-identical.
5. Then promote T11 verdict from HOLD to **PASS**, releasing the
   12-month full run + GO/NO-GO for T002.

---

**Verdict signed by:** Beckett (@backtester) — 2026-04-26 BRT
**Authority:** `*run-cpcv` task; HALT/HOLD verdict per
`backtester.core_principles[FILL EXIGE EVIDÊNCIA NO TAPE]` analogue
applied to upstream provenance ("fill exige evidência no warmup state
- inferir warmup invalida o backtest"). User asleep — no Gage push
authorized.

— Beckett, reencenando o passado 🎞️
