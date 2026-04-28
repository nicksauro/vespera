---
report_id: T002-beckett-t11-bis-smoke-report-2026-04-27
story_id: T002.0h
agent: Beckett (@backtester)
task: T6 — execução do T11.bis re-run (AC8 exit gate de T002.0h)
date_brt: 2026-04-27T21:36 BRT
verdict: HALT-ESCALATE
verdict_summary: |
  Step A (warmup cache hit) PASS 4/4 sub-criteria (8.1-8.4).
  Step C (CPCV smoke) FAIL 3/5 sub-criteria (8.5, 8.8, 8.9 FAIL; 8.6, 8.7 PASS).
  AC8 OVERALL = FAIL (5/9 PASS, 4/9 FAIL). HALT-ESCALATE.
  Root cause: NÃO É memory blocker, NÃO É perf regression, NÃO É streaming
  refactor regression. CPCV harness ran to completion (peak RSS 142.85 MB
  = 0.14 GiB, headroom 97.67% vs 6 GiB threshold; fanout 1279ms produzindo
  225 results). Failure is in POST-PROCESSING — `compute_full_report` →
  `read_research_log_cumulative` raises ValueError "YAML parse error" no
  parsing de `docs/ml/research-log.md` por bug latente no parser
  `_split_yaml_blocks` (toggle fence walker está invertido vs estrutura
  da production ledger: parser captura prose bodies, ignora frontmatter
  blocks). Tests exercem o parser apenas via _write_research_log helper
  (mocks tightly-formatted), nunca contra production file. Fail-closed
  guard AC11 funciona como esperado, abortando smoke.
  Beckett NÃO fixa parser (Dex/Mira authority), NÃO edita ledger
  (Mira sole authority append-only), NÃO bypassa AC11 (Riven invariant),
  NÃO retry (Anti-Article-IV Guard #5). HALT-ESCALATE.
authority: |
  Beckett — backtester & execution simulator authority. AC8 exit gate
  exercised post-AC9-cache-validation-contract (Dex commit 243bcad).
  Article IV (No Invention) absoluto. Anti-Article-IV Guards #1-#7
  honrados. Wall-time honestly measured via Bash `time` builtin + telemetry
  CSV duration_ms cross-check. Peak RSS honestly captured via psutil
  poller daemon-thread (canonical per ADR-1 v3 governance memory
  protocol). NO threshold relaxation, NO subsample, NO retry, NO push.
preconditions_met:
  - "Dex AC9 commitado (BUILDER_VERSION=1.0.0 + triple-key sidecar + StaleCacheError + --force-rebuild + cache_audit.jsonl) — commit 243bcad"
  - "Quinn T5 PASS (gate docs/qa/gates/T002.0h-qa-gate.md, validated 243bcad, 7/7 PASS)"
  - "All 8 pre-flight checks PASSED (P1-P8 §2)"
---

# T11.bis Smoke Report — T002.0h AC8 Exit Gate

**Date (BRT):** 2026-04-27T21:36
**Commit:** 243bcad (head of t002-1-warmup-impl-126d branch)
**Spec:** docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml
**Spec sha256:** `98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614`
**Authority:** Beckett (@backtester) — AC8 reframed exit gate post-ESC-006

---

## §0. Verdict overview

**AC8 exit gate verdict:** **FAIL — HALT-ESCALATE** (5/9 sub-criteria PASS, 4/9 FAIL).

| Phase | Status | Notes |
|-------|--------|-------|
| Pre-flight (8 checks) | **PASS** (8/8) | All shas + constants match expected |
| Step A — warmup cache hit | **PASS** (4/4 sub-criteria) | 0.336s wall-time; cache hit path validated |
| Step B — force-rebuild scratch | **SKIPPED** | Optional; not required for AC8 PASS per plan §1.3 |
| Step C — CPCV dry-run smoke | **FAIL** (2/5 sub-criteria) | Exit 1 in 4.198s; AC11 abort on research-log parse error |

**Root cause classification:**
- **NOT a memory blocker** — peak RSS = 142.85 MB (0.14 GiB), headroom 97.67% vs 6 GiB AC8 threshold.
- **NOT a perf regression** — wall-time 4.198s including failure; fanout phase completed in 1.279s (225 results).
- **NOT a T002.0h streaming refactor regression** — warmup gate passed, cpcv_harness fanout passed.
- **IS a latent parser bug** — `packages/vespera_metrics/research_log.py::_split_yaml_blocks` toggle-fence walker is structurally inverted vs production ledger format. The parser captures prose bodies (lines 72-78, 88-95) and skips actual frontmatter blocks (lines 64-70, 80-86). Existing tests use `_write_research_log` mock helper that produces tightly-formatted ledgers (no Authority/Schema/Version sections) — never validated against production `docs/ml/research-log.md`.
- **AC11 abort guard worked correctly** — invocation `read_research_log_cumulative()` raised `ValueError`; `run_cpcv_dry_run.py` smoke phase aborted as designed; KillDecision NOT computed (CORRECT — Article IV: invention forbidden).

**Riven §9 HOLD #1 clearance:** **NOT MET**. `full_report.json` does not exist; KillDecision verdict NOT extracted; 4/5 smoke artifacts missing. Evidence package incomplete.

**Phase F unblock:** **NO**. AC8 exit gate not satisfied.

---

## §1. Pre-flight verification (8 checks)

| # | Check | Expected | Observed | Status |
|---|-------|----------|----------|--------|
| P1 | Python + psutil | Python 3.14.x; psutil ≥ 5.x | Python 3.14.3; psutil 7.2.2 | **PASS** |
| P2 | BUILDER_VERSION constant | `'1.0.0'` | `'1.0.0'` | **PASS** |
| P3 | manifest.csv sha256 | `78c9adb3...22dee72` | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` | **PASS** |
| P4 | parquets in-sample [2025-05, 2025-06] | both exist | both present | **PASS** |
| P5 | state/T002/ snapshot pre-run | sidecar + audit "hit" | sidecar present, last 2 entries `status:"hit"` | **PASS** (cache-hit branch active) |
| P6 | spec sha256 | `98f22f3c...4d4b24614` | `98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614` | **PASS** |
| P7 | calendar + cost-atlas shas | calendar `4f6876...`; cost-atlas LF-norm `acf44941...4a5126` | calendar `4f6876689aaaf15134b43c11f48f84e0d6bc23051b5331cb94c55356afd5540a`; cost-atlas whole-file `bbe1ddf7898e79a7b8dadf4408c854fa010bd7444e2c2f3b9fcb006c24b84b6d`, LF-normalized `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126` | **PASS** |
| P8 | Hold-out lock constants | `2025-07-01` / `2026-04-21` | `2025-07-01` / `2026-04-21` | **PASS** |

All pre-flights PASS — execution proceeded to Step A.

---

## §2. Step A — Warmup cache hit (path principal AC8)

**Command:**
```bash
time python scripts/run_warmup_state.py --as-of-dates 2025-05-31 --output-dir state/T002/
```

**Result:**
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Exit code | 0 | == 0 | PASS |
| Wall-time (real) | 0.336s | < 5s (cache hit) | PASS |
| stdout | empty | (informational) | OK |
| stderr | empty | (no warnings) | OK |
| Peak RSS (warmup poller) | 24.84 MB | < 6 GiB | PASS (0.4% of cap) |
| Internal duration_ms (run_end event) | 3 ms | (informational) | OK |

**State files post-run (no mtime change on JSONs — confirms cache hit):**

```
-rw-r--r--  136 Apr 26 20:49  _cache_key_2025-05-31.json
-rw-r--r--  362 Apr 26 20:49  atr_20d.json
-rw-r--r--  362 Apr 26 20:49  atr_20d_2025-05-31.json
-rw-r--r-- 2049 Apr 27 21:35  cache_audit.jsonl       (+1 line)
-rw-r--r--  338 Apr 26 20:49  determinism_stamp.json
-rw-r--r--  436 Apr 26 20:49  manifest.json
-rw-r--r-- 1910 Apr 26 20:49  percentiles_126d.json
-rw-r--r-- 1910 Apr 26 20:49  percentiles_126d_2025-05-31.json
-rw-r--r--  602 Apr 27 21:35  telemetry-warmup.csv     (rewritten)
```

**New cache_audit.jsonl entry (line 5, appended this run):**

```json
{
  "as_of_date": "2025-05-31",
  "computed_at_brt": "2026-04-27T21:35:59",
  "expected_key": {
    "as_of_date": "2025-05-31",
    "builder_version": "1.0.0",
    "source_sha256": "7b7e4480425b8da4287f56eb3e8f95745accf62559579990b098a89193e141f7"
  },
  "found_key": {
    "as_of_date": "2025-05-31",
    "builder_version": "1.0.0",
    "source_sha256": "7b7e4480425b8da4287f56eb3e8f95745accf62559579990b098a89193e141f7"
  },
  "note": "orchestrator skipped (triple-key match)",
  "status": "hit"
}
```

**Warmup telemetry (5 samples):**

| timestamp_brt | rss_mb | peak_wset_bytes | phase | note |
|---|---|---|---|---|
| 2026-04-27T21:35:59 | 24.73 | 19103744 | run_start | as_of_dates=['2025-05-31'] |
| 2026-04-27T21:35:59 | 24.80 | 19173376 | init | poll |
| 2026-04-27T21:35:59 | 24.84 | 19177472 | cache_hit | as_of=2025-05-31;builder=1.0.0 |
| 2026-04-27T21:35:59 | 24.84 | 19177472 | cache_all_hits | as_of_count=1;orchestrator_skipped |
| 2026-04-27T21:35:59 | 24.84 | 19177472 | run_end | halt_observed=False;duration_ms=3 |

**Step A sub-criteria verdict:**

| # | Sub-criterion | Threshold | Observed | Status |
|---|--------------|-----------|----------|--------|
| 8.1 | warmup exit 0 | == 0 | 0 | **PASS** |
| 8.2 | warmup wall-time < 5s (cache hit) | < 5s | 0.336s | **PASS** (93% under) |
| 8.3 | 2 dated JSONs persisted | atr_20d_2025-05-31.json + percentiles_126d_2025-05-31.json | both present (mtime 20:49 unchanged → cache hit) | **PASS** |
| 8.4 | 2 default-path JSONs (symlink/copy) | atr_20d.json + percentiles_126d.json | both present (mtime 20:49 unchanged → cache hit) | **PASS** |

Step A: 4/4 PASS. Cache contract (AC9) empirically validated end-to-end. Triple-key match confirmed by audit JSONL.

---

## §3. Step B — Force-rebuild scratch (SKIPPED)

Per plan §1.3 + §4.1: Step B is OPTIONAL, non-blocking for AC8. Skipped because:
1. Step A satisfied warmup half of AC8 (8.1-8.4 PASS).
2. Step C blocked the gate at AC11 (research-log parser bug, see §4).
3. Force-rebuild evidence cannot unblock the parser bug — it would only validate the warmup miss-path (which is independent of CPCV smoke phase).
4. Anti-Article-IV Guard #5 (NO retry after exit ≠ 0) and operator brief: focus on diagnostic + escalation.

If/when parser is fixed (Dex/Mira), Beckett will re-run T11.bis #2 including Step B for completeness.

---

## §4. Step C — CPCV dry-run smoke

**Command:**
```bash
time python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --smoke \
  --in-sample-end 2025-06-30 \
  --seed 42 \
  --warmup-atr state/T002/atr_20d.json \
  --warmup-percentiles state/T002/percentiles_126d.json
```

**Result summary:**
| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Exit code | 1 | == 0 | **FAIL** |
| Wall-time (real) | 4.198s | < 300s | (PASS-irrelevant — exit 1) |
| Peak RSS observed | 142.85 MB (0.1395 GiB) | < 6 GiB | **PASS** (97.67% headroom) |
| Peak working set (Windows) | 592.32 MB (0.5784 GiB) | < 6 GiB | **PASS** (90.6% headroom) |
| Smoke artifacts persisted | 1/5 (only telemetry.csv) | 5/5 | **FAIL** |
| KillDecision verdict | NOT PRODUCED | ∈ {GO, NO_GO} | **FAIL** |

**Run dir derived (deterministic):** `data/baseline-run/cpcv-dryrun-auto-20260427-d2098a3d865b/`

**Telemetry CSV (8 samples):**

| sample | timestamp_brt | rss_mb | peak_wset_bytes | phase | note |
|---|---|---|---|---|---|
| 1 | 2026-04-27T21:36:18 | 141.30 | 621031424 | run_start | run_id=auto-20260427-d2098a3d865b;spec_sha=98f22f3c8cee |
| 2 | 2026-04-27T21:36:18 | 141.33 | 621084672 | init | poll |
| 3 | 2026-04-27T21:36:18 | 141.34 | 621092864 | smoke:events_start | window=2025-05-31..2025-06-30 |
| 4 | 2026-04-27T21:36:18 | 141.95 | 621092864 | smoke:events_built | n_events=360 |
| 5 | 2026-04-27T21:36:18 | 142.03 | 621092864 | smoke:fanout_start | trials=['T1','T2','T3','T4','T5'] |
| 6 | 2026-04-27T21:36:19 | 142.84 | 621092864 | smoke:fanout_complete | duration_ms=1279;total_results=225 |
| 7 | 2026-04-27T21:36:19 | 142.85 | 621092864 | smoke_failed | reason: smoke_aborted: ValueError ... research-log parse error |
| 8 | 2026-04-27T21:36:19 | 142.85 | 621092864 | run_end | halt_observed=False |

**Crucial observations:**
- The CPCV harness phase (the expensive part) **completed successfully**: events built (n=360), 5-trial fanout completed in 1.279s producing 225 results (5 trials × 45 paths each).
- Memory profile is **flat** at ~142 MB throughout — no spikes, no leaks. T002.0h streaming refactor + AC9 cache contract are working as designed.
- Failure occurred in `compute_full_report` post-fanout, when `read_research_log_cumulative()` was invoked.

**Stderr (verbatim):**
```
ERROR: smoke phase failed; aborting full run per AC11: docs\ml\research-log.md entry #3:
YAML parse error mapping values are not allowed here
  in "<unicode string>", line 3, column 31:
    varrer. Os cinco trials varrem: (a) sensitivity ao threshold d ...
                                  ^
```

### §4.1. Root cause analysis — research-log parser bug

The parser `packages/vespera_metrics/research_log.py::_split_yaml_blocks` walks the file as a **toggling fence sequence** (open→close→open→close). The production `docs/ml/research-log.md` has 8 `---` fence lines (12, 23, 59, 63, 71, 79, 87, 96) which produce **4 blocks** when toggle-walked:

| Block | Content (lines) | yaml.safe_load() result | Action |
|---|---|---|---|
| 1 | 13-22 (Authority statement prose) | string | skipped (not dict) |
| 2 | 60-62 ("## Entries" header alone) | string | skipped (not dict) |
| 3 | **72-78 (T002.0d body prose)** | **ValueError** ("varrer. Os cinco trials varrem: (a)" contains `:` interpreted as YAML mapping value) | **HALT** |
| 4 | 88-95 (T002.0f body prose) | (not reached) | n/a |

**The parser CAPTURES prose bodies and SKIPS actual frontmatter entries** (lines 64-70 = T002.0d, lines 80-86 = T002.0f).

**Why tests pass anyway:** All 5 parser-related tests in `tests/vespera_metrics/test_compute_full_report.py` use the `_write_research_log(tmp_path, entries)` helper (lines 180-217 of test file), which writes a TIGHT minimal ledger:
```
# Mock Research Log
                         ← (blank line)
---
{entry_1_keys}
---
{entry_2_keys}
---
```
This format produces **block 1 = entry 1, block 2 = entry 2** under toggle parsing — works correctly. But the production ledger has Authority Statement + Schema + Append-only sections BEFORE the entries, breaking the toggle-walk alignment.

**This is a latent end-to-end integration bug**: parser is unit-tested, ledger format is documented, but their combination was never exercised against the production file before T11.bis. The very first attempt to parse the real ledger failed.

### §4.2. Step C sub-criteria verdict

| # | Sub-criterion | Threshold | Observed | Status |
|---|--------------|-----------|----------|--------|
| 8.5 | CPCV smoke exit 0 | == 0 | 1 | **FAIL** |
| 8.6 | CPCV smoke wall-time < 5min | < 300s | 4.198s | (PASS-irrelevant — exit 1) |
| 8.7 | Peak RSS < 6 GiB | < 6144 MB | 142.85 MB | **PASS** (97.67% headroom) |
| 8.8 | 5 smoke artifacts persisted | 5/5 | 1/5 (only telemetry.csv) | **FAIL** |
| 8.9 | KillDecision.verdict ∈ {GO, NO_GO} | ∈ {GO, NO_GO} | NOT PRODUCED | **FAIL** |

Step C: 1/5 PASS (8.7), 1/5 PASS-IRRELEVANT (8.6), 3/5 FAIL.

---

## §5. 5 artifacts checksum table

| spec name | file path | sha256 | size | status |
|-----------|-----------|--------|------|--------|
| Splits.json (logical) → full_report.json.splits | `<run_dir>/smoke/full_report.json` | n/a | n/a | **MISSING** |
| FoldStats.json (logical) → full_report.json.fold_stats | `<run_dir>/smoke/full_report.json` | n/a | n/a | **MISSING** |
| FullReport.json | `<run_dir>/smoke/full_report.json` | n/a | n/a | **MISSING** |
| FullReport.md | `<run_dir>/smoke/full_report.md` | n/a | n/a | **MISSING** |
| KillDecision.json (logical) → full_report.json.kill_decision | `<run_dir>/smoke/full_report.json` | n/a | n/a | **MISSING** |
| determinism_stamp.json | `<run_dir>/smoke/determinism_stamp.json` | n/a | n/a | **MISSING** |
| events_metadata.json | `<run_dir>/smoke/events_metadata.json` | n/a | n/a | **MISSING** |
| telemetry.csv | `<run_dir>/telemetry.csv` | `0aaafd288e5b60bf021ecfc8eceeebf0dba567093df5531e49a2685c050283ba` | 1266 B | **PRESENT** |

Only `telemetry.csv` was written (by the MemoryPoller daemon thread, which runs orthogonally to the smoke phase). All 4 artifacts produced by `persist_artifacts` (full_report.{json,md}, determinism_stamp.json, events_metadata.json) are MISSING because `compute_full_report` raised before reaching the persist step.

---

## §6. KillDecision verdict + metrics summary

**KillDecision verdict:** **NOT PRODUCED** (full_report.json does not exist).

**Reason:** `compute_full_report()` raised `ValueError` during `read_research_log_cumulative()` invocation; control returned to `run_cpcv_dry_run.py` smoke handler which logged `smoke_failed` and exited with code 1 per AC11 fail-closed contract. KillDecision computation is gated downstream of `compute_full_report` success.

**This is CORRECT behavior** under Article IV (No Invention) + AC11 (smoke gate fail-closed) — the system refused to fabricate a verdict from incomplete data. The bug is in the parser, not the kill decision logic.

---

## §7. cache_audit.jsonl diff (pre/post Step A)

**Pre-run audit lines:** 4
**Post-run audit lines:** 5
**Delta:** +1 entry, `status:"hit"`, `note:"orchestrator skipped (triple-key match)"`

Cache contract behavior: **as designed**. Triple-key match (as_of_date + builder_version + source_sha256) confirmed; orchestrator NOT invoked; sub-second wall-time achieved.

---

## §8. Re-determinism check — N/A

Skipped because Step C did not produce a `full_report.json` to compare. Re-determinism evidence cannot be produced until the parser bug is resolved.

---

## §9. Article IV trace

| Decision | Source | Justification |
|---|---|---|
| Spec v0.2.0 used | spec sha matches `98f22f3c...4d4b24614` (P6 PASS) | Mira-pinned, unchanged since prior runs |
| Cost atlas v1.0.0 LF-normalized used | sha matches `acf44941...4a5126` (P7 PASS) | Nova-pinned, unchanged |
| Calendar 2024-2027 used | sha `4f6876689...afd5540a` (P7 PASS) | Pax errata included (commit 460c702) |
| BUILDER_VERSION 1.0.0 | constant import (P2 PASS) | Dex AC9 commit 243bcad |
| Hold-out 2025-07-01 → 2026-04-21 | _holdout_lock constants (P8 PASS) | Mira PRR-20260421-1, Riven cosign |
| Smoke window [2025-05-31, 2025-06-30] | CLI default `--in-sample-end 2025-06-30` + DEFAULT_SMOKE_DAYS=30 | Anti-Article-IV Guard #1: NO subsample |
| Engine config NOT mutated | docs/backtest/engine-config.yaml READ-ONLY | Anti-Article-IV Guard #2 |
| AC11 abort respected | run_cpcv_dry_run.py exited 1 on smoke failure | Anti-Article-IV Guard #5: NO retry |
| Threshold NOT relaxed | AC8.5/8.8/8.9 reported as FAIL, not waived | Anti-Article-IV Guard #3 |
| Peak RSS reported honestly | poller CSV `max(rss_mb)` = 142.85 MB | Anti-Article-IV Guard #4 |
| Parser NOT modified | research_log.py untouched by Beckett | Beckett is execution authority, not code mutator |
| Ledger NOT edited | research-log.md untouched | Mira sole authority over ledger (R15-style append-only discipline) |

---

## §10. Reproducibility envelope

| Field | Value |
|---|---|
| seed | 42 |
| simulator version | TBD (not stamped — full_report.json missing) |
| dataset hash (manifest.csv) | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` |
| spec sha256 | `98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614` |
| spec path | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` |
| calendar sha256 | `4f6876689aaaf15134b43c11f48f84e0d6bc23051b5331cb94c55356afd5540a` |
| cost-atlas sha256 (whole-file) | `bbe1ddf7898e79a7b8dadf4408c854fa010bd7444e2c2f3b9fcb006c24b84b6d` |
| cost-atlas sha256 (LF-normalized) | `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126` |
| BUILDER_VERSION | `1.0.0` |
| HOLDOUT_START | `2025-07-01` |
| HOLDOUT_END_INCLUSIVE | `2026-04-21` |
| Python | 3.14.3 |
| psutil | 7.2.2 |
| run dir (CPCV) | `data/baseline-run/cpcv-dryrun-auto-20260427-d2098a3d865b/` |
| log dir (Beckett) | `data/baseline-run/cpcv-dryrun-T002-2026-04-27/` |
| commit (HEAD) | `243bcad` |
| branch | `t002-1-warmup-impl-126d` |

---

## §11. Verdict + recommendation

### §11.1. AC8 sub-criteria pass/fail matrix (all 9)

| # | Sub-criterion | Threshold | Observed | Status |
|---|--------------|-----------|----------|--------|
| 8.1 | warmup exit 0 | == 0 | 0 | **PASS** |
| 8.2 | warmup wall-time < 5s (cache hit) | < 5s | 0.336s | **PASS** |
| 8.3 | 2 dated JSONs persisted | both present | both present | **PASS** |
| 8.4 | 2 default-path JSONs (symlink/copy) | both present | both present | **PASS** |
| 8.5 | CPCV smoke exit 0 | == 0 | 1 | **FAIL** |
| 8.6 | CPCV smoke wall-time < 5min | < 300s | 4.198s | (PASS-irrelevant — exit 1) |
| 8.7 | Peak RSS < 6 GiB | < 6144 MB | 142.85 MB | **PASS** |
| 8.8 | 5 smoke artifacts persisted | 5/5 | 1/5 | **FAIL** |
| 8.9 | KillDecision.verdict ∈ {GO, NO_GO} | ∈ {GO, NO_GO}; not TIMEOUT/MEMORY_HALT | NOT PRODUCED | **FAIL** |

**Composite:** 5/9 PASS, 1/9 PASS-IRRELEVANT, 3/9 FAIL → **AC8 FAIL** (PASS requires 9/9 per plan §4.1).

### §11.2. Verdict

- **AC8 exit gate:** **FAIL**
- **Riven §9 HOLD #1 clearance criteria:** **NOT MET** (full_report.json + KillDecision.verdict missing)
- **Phase F unblock:** **NO** (AC8 failed)

### §11.3. HALT-ESCALATE diagnostic

**Blocker:** `packages/vespera_metrics/research_log.py::_split_yaml_blocks` toggle-fence parser is structurally incompatible with the production `docs/ml/research-log.md` format. Latent bug — never exercised end-to-end before T11.bis #2.

**Owner classification:**
- **Parser implementation:** Dex (@dev) — fix `_split_yaml_blocks` to correctly identify YAML frontmatter blocks (recommend: switch to a state machine that recognizes "consecutive `---` fences delimit a frontmatter block", or use a regex like `^---\n(?P<body>.*?)\n---$` with re.MULTILINE+DOTALL, OR change ledger format to use python-frontmatter library convention).
- **Ledger format authority:** Mira (@ml-researcher) — the documented schema (header line 30) said "splitting on top-level `---` fences" which the implementer interpreted as toggle-walk; if the intent was "find every PAIR of fences delimiting frontmatter", the schema doc needs an unambiguous restatement. R15 governance: ledger schema change is a `breaking_fields` event requiring full revision pre-registration.
- **Test coverage gap:** Quinn (@qa) — re-QA missed the integration test gap. Existing 5 parser tests all use mocks. RECOMMEND: add an integration test that loads the ACTUAL `docs/ml/research-log.md` from disk and asserts `n_trials_cumulative == 5` (sum of T002.0d=5 + T002.0f=0).

**Anti-Article-IV Guards honored:**
- #1 NO subsample: dataset window unchanged (`[2025-05-31, 2025-06-30]`).
- #2 NO modify engine config: `engine-config.yaml` read-only.
- #3 NO improvise threshold relaxation: AC8.5/8.8/8.9 reported as FAIL, not waived.
- #4 Reported peak RSS HONESTLY: 142.85 MB from poller CSV `max(rss_mb)`.
- #5 NO retry after exit ≠ 0: single Step C invocation, captured + reported.
- #6 NO push: no git push attempted (Gage authority).
- #7 NO modify story files: this report is the only artifact written by Beckett.

**Mitigation NOT attempted (with rationale):**
- Editing the parser to fix `_split_yaml_blocks` — Beckett is execution authority, NOT code mutator. Parser is owned by Dex implementation + Mira contract. Suggested fix is documented but NOT applied.
- Editing `docs/ml/research-log.md` to fit the toggle parser — Mira sole authority over ledger (R15 append-only). Beckett cannot edit Mira artifacts.
- Bypassing AC11 smoke abort — Riven invariant. Bypassing would require Riven cosign + governance entry, NOT Beckett unilateral.
- Subsampling smoke window — Anti-Article-IV Guard #1.

### §11.4. Escalation list (USER-ESCALATION-QUEUE.md → P1 candidate)

**Suggested escalation entry:**

```
ESC-007 (Beckett T11.bis #2 HALT 2026-04-27 21:36 BRT): research-log
parser bug blocks AC8 exit gate of T002.0h. CPCV smoke harness ran to
completion (peak RSS 0.14 GiB; fanout 1279ms producing 225 results),
but compute_full_report aborted in read_research_log_cumulative because
_split_yaml_blocks toggle-walker is structurally inverted vs production
ledger format (parser captures prose bodies, skips frontmatter blocks).
Latent bug — existing tests use _write_research_log mock helper (tightly
formatted), never validated against production docs/ml/research-log.md.

Owners:
- Dex (@dev): fix _split_yaml_blocks (recommend regex-based block
  extraction OR python-frontmatter library OR state machine recognizing
  consecutive --- as frontmatter delimiter).
- Mira (@ml-researcher): clarify ledger header schema language ("top-
  level --- fences" is ambiguous between "toggle" and "delimit pairs").
  R15 evaluation if breaking_fields revision required.
- Quinn (@qa): add integration test loading ACTUAL production ledger;
  re-QA gate to require this coverage before any future close.

Evidence: docs/backtest/T002-beckett-t11-bis-smoke-report-2026-04-27.md
Story T002.0h status: AC8 still RED. Phase F still BLOCKED.
Riven §9 HOLD #1 NOT cleared (requires re-run after parser fix).
```

### §11.5. Next handoff

| To | What | Trigger |
|----|------|---------|
| Operator (autonomous squad) | This report + ESC-007 entry | NOW |
| Dex (@dev) | Parser fix request (suggested implementations in §11.3) | After operator triage |
| Mira (@ml-researcher) | Ledger schema clarification + R15 evaluation | After operator triage |
| Quinn (@qa) | Integration test coverage gap | After parser fix |
| Beckett (@backtester) | T11.bis #3 re-run (full plan re-execution) | After Dex fix + Quinn re-QA |
| Riven (@risk-manager) | Evidence package + §9 amendment | T11.bis #3 PASS only |

---

## §12. Cosign

**Verdict signed by:** Beckett (@backtester) — 2026-04-27T21:36 BRT
**Signature:** 🎞️
**Co-sign required:** none (Beckett execution authority + report authority over backtest artifacts).
**Not authorized:** story status promotion (Pax/Sm), QA Results section update (Quinn), §9 amendment (Riven), git push (Gage).

— Beckett, reencenando o passado 🎞️
