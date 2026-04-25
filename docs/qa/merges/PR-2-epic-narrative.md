# PR #2 Epic-Level Merge Narrative

**Branch:** t002-refactor-next-run -> main
**Current PR head (stale):** f08f027
**Authorized target head:** 68627a8
**Commit count:** 10
**Epic orchestrator:** @pm (Morgan)
**Authorization date:** 2026-04-23

---

## Title (proposed, for Gage to apply via `gh pr edit 2 --title`)

`feat(t002): T002.0b+ADR-4+T002.4 — adapters, pre-cache, child telemetry`

(69 chars, within the 70-char convention cap.)

---

## Body (proposed, for Gage to apply via `gh pr edit 2 --body`)

```markdown
## Summary

- **T002.0b Data Adapters** (`feed_timescale` + `feed_parquet`): Beckett-spec adapters with byte-level parity on live 314k-trade window, hold-out guard before I/O, BRT-naive throughout, sha256 integrity per parquet. Story `docs/stories/T002.0b.story.md` (#63) + Quinn gate `docs/qa/gates/T002.0b-qa-gate.md` PASS.
- **ADR-4 Pre-cache Layer (Option B)** — §13.1 streaming cache build (`_stream_month_to_parquet`, peak WS 210.89 MiB = 17x under 3.5 GiB A1 cap) + §13.2 T12a/T12b split proving cache self-sufficiency with sentinel DOWN in 9.94 s + P5 wrapper passthrough (`--source`/`--cache-dir`/`--cache-manifest` mutex-validated). Quinn gate `docs/qa/gates/RA-20260426-1-chain-gate.md` CONCERNS -> fixed via commit `63a9a3a` (CONCERNS-01 test-stub repoint) -> RA-20260426-1 flipped DRAFT -> ISSUED on 2026-04-24 by Orion on Riven-delegated authority (commit `f0e8741`).
- **T002.4 Child-peak Telemetry** (ADR-4 §14.5.2 B1): child-side `psutil.Process().memory_info().peak_pagefile/.peak_wset` kernel-peak emission via `TELEMETRY_CHILD_PEAK_EXIT` line in outer `finally{}`; wrapper parses + augments summary JSON with `peak_commit_bytes_child_self_reported` for RA-20260428-1 step-7 CEILING_BYTES derivation (task #124). Story `docs/stories/T002.4.story.md` (#118) + Pax validation `docs/qa/validations/T002.4-story-draft-validation.md` 10/10 GO + Quinn gate `docs/qa/gates/T002.4-qa-gate.md` CONCERNS + Riven co-sign `docs/qa/cosigns/T002.4-riven-cosign.md` dual-sign complete; FINDING-01 disclosure remediation filed in commit `68627a8`.

## Scope (10 commits)

| # | SHA | Subject | Scope |
|---|-----|---------|-------|
| 1 | `59e03fe` | feat(t002.0e): add Nova cost atlas v1.0.0 with Sable audit | T002.0e cost atlas (Nova + Beckett + Sable + Quinn + Pax 9.5/10) |
| 2 | `f971bb5` | fix(materialize): cursor streaming + per-month flush + gc | T002.0a unblock (Dara R10-custodial patch for next run) |
| 3 | `f08f027` | feat(t002): T002.0b Data Adapters (feed_timescale + feed_parquet) | T002.0b |
| 4 | `8c217bf` | feat(build-cache): §13.1 streaming parquet writer for raw_trades pre-cache | ADR-4 §13.1 |
| 5 | `cb62713` | test(t12-split): §13.2 T12a/T12b split for cache-only sentinel-DOWN proof | ADR-4 §13.2 |
| 6 | `85664f7` | feat(wrapper): passthrough --source/--cache-dir/--cache-manifest (RA-20260426-1 P5) | ADR-4 P5 wrapper |
| 7 | `63a9a3a` | test(build-cache): repoint monkeypatches to _stream_month_to_parquet (CONCERNS-01) | ADR-4 §13 gate CONCERNS-01 remediation |
| 8 | `f0e8741` | docs(governance): flip RA-20260426-1 DRAFT->ISSUED with P1-P5 evidence | ADR-4 / RA-20260426-1 issuance |
| 9 | `80805ac` | feat(T002.4): child-side peak telemetry for CEILING_BYTES derivation | T002.4 primary impl |
| 10 | `68627a8` | docs(T002.4): disclose bundled ADR-4 §10.3 + MWF-20260422-1 scope (FINDING-01) | T002.4 Riven FINDING-01 disclosure fix |

## Governance trail

### T002.0e (Nova cost atlas) — commit 1
- Story: `docs/stories/T002.0e.story.md` (#?)
- Audit: `docs/backtest/nova-cost-atlas-audit.md` — Sable APPROVED_WITH_CONDITIONS (F-02/F-03/F-04 deferred to atlas v1.0.1)
- Atlas: `docs/backtest/nova-cost-atlas.yaml` (sha256 `acf44941...126` locked)
- Pax validate-story-draft: 9.5/10 GO
- Quinn QA gate: PASS (per commit body)
- Consumption: Beckett `engine-config.yaml` with `atlas_version_lock="1.0.0"`

### T002.0a cursor-streaming patch — commit 2
- Author: Dara (@data-engineer, R10-custodial territory)
- Purpose: fix fetchall-buffer memory leak + per-month manifest flush + inter-month gc (for NEXT materialize run, after T002.0a PID 12608 completes)
- Governance: custodial Dara territory under R10; no new story required — patch against future-run `scripts/materialize_parquet.py`; empirically validated downstream by §13.1 pilot build at 210.89 MiB peak WS (17x margin).

### T002.0b Data Adapters — commit 3
- Story: `docs/stories/T002.0b.story.md` (#63)
- Quinn gate: `docs/qa/gates/T002.0b-qa-gate.md` — **PASS** (7/7 checks; AC matrix 15/15 covered; parity test byte-identical; cold budget 8x margin)
- Tests: 12 passed / 1 skipped (T6b hot loop correctly deferred on T002.0a blocker); regression `tests/t002_eod_unwind/` 77/77 PASS
- Ruff: clean; hold-out guard fires before I/O in both adapters.

### ADR-4 Pre-cache Layer (Option B) — commits 4-8
- Design spec: `docs/architecture/pre-cache-layer-spec.md` §1-§14 (#107)
- Amendment: ADR-4 Amendment 20260424-1 §13 (streaming cache build + T12a/T12b split + P5 wrapper passthrough); logged in `docs/MANIFEST_CHANGES.md` as `r4_amendment` entries at lines 112/159/231/327.
- Memory budget §RA-20260426-1 ISSUED block: `docs/architecture/memory-budget.md` L1825-2110 — flipped DRAFT->ISSUED 2026-04-24T11:42:19Z by Orion on Riven-delegated authority per `issuance_preconditions.flip_procedure`.
- §RISK-DISPOSITION-20260423-1 (Riven): Q6a/Q6b/Q6d preconditions satisfied; Q5 DEFERRED (canonical `_fetch_month_dataframe` patch stays in R10-custodial territory).
- Quinn chain gate: `docs/qa/gates/RA-20260426-1-chain-gate.md` — CONCERNS at authoring (CONCERNS-01: 5 stale test stubs in `tests/unit/test_build_raw_trades_cache.py`).
- CONCERNS-01 remediation: commit `63a9a3a` repoints monkeypatches from `mp._fetch_month_dataframe` -> `brc._stream_month_to_parquet`; `tests/unit/` now 11/11 PASS.
- P5 wrapper gate: `docs/qa/gates/wrapper-passthrough-gate.md` — 45/45 tests PASS (3 mutex + 2 forwarding); argparse `add_mutually_exclusive_group` + post-parse `--source` mutex at `scripts/run_materialize_with_ceiling.py` L173-193.
- Retry #4/#5 incident trail: Dex §13.1 pilot build of Aug-2024 WDO produced 21,058,318 rows at `.tmp/ws_peak.txt` `peak_ws_bytes=221_130_752` (**210.89 MiB**) vs A1 cap 3.5 GiB (17x margin) and `elapsed_s=204.21` (~3.40 min) vs A2 cap 10 min (3x margin).
- T12b sentinel-DOWN proof: `tests/integration/test_adapter_parity_cache.py::test_T12b_cache_self_sufficient_sentinel_down` — PASSED with `sentinel-timescaledb` stopped (Q1 empirically closed in 9.94 s).
- §13 amendment registry: `docs/MANIFEST_CHANGES.md` §`r4_amendment` entries document the full chain from incident (retry #4 BASELINE_FAIL + task #106 governance) through issuance.

### T002.4 Child-peak Telemetry — commits 9-10
- Story: `docs/stories/T002.4.story.md` (#118)
- Pax validation: `docs/qa/validations/T002.4-story-draft-validation.md` — **GO 10/10** (AC-F dual-sign Quinn+Riven mandate recorded)
- Dex impl: commit `80805ac` (#121) — `scripts/materialize_parquet.py` +541/-26 (A=135 LOC T002.4 PRIMARY + B=160 LOC ADR-4 §10.3 cache-dispatch BUNDLED + C=245 LOC MWF-20260422-1 §3.1-§4.2 manifest-mode BUNDLED); `scripts/run_materialize_with_ceiling.py` pure T002.4 scope; `tests/core/test_run_with_ceiling.py` pure T002.4 scope.
- Quinn gate: `docs/qa/gates/T002.4-qa-gate.md` — **CONCERNS** (FINDING-01: bundled scope undisclosed in File List / commit body; sole CONCERNS driver; telemetry surface itself PASS on 7/7 checks).
- Riven co-sign: `docs/qa/cosigns/T002.4-riven-cosign.md` — **CO-SIGN** on R1 (R5 invariant byte-identical, `core/memory_budget.py` diff EMPTY, AC-G preserved), R2 (telemetry schema suitable for CEILING_BYTES derivation per `peak_commit_bytes_child_self_reported` primary), R3 (Q6d Nyquist immunity — kernel peak retrieval at child exit, not sampled). FINDING-01 addendum required option B (disclosure fix) before merger.
- FINDING-01 remediation: commit `68627a8` (#122) — docs-only, single file `docs/stories/T002.4.story.md` +26/-3 adding (a) File List LOC breakdown A=135 + B=160 + C=245 = 540 (within 10% of actual 541 delta) with per-bundle spec cites, (b) "Bundled scope disclosure" subsection with Article-IV trace (no invention) + retroactive-rationale honesty.
- Riven remediation-accepted addendum (same co-sign file): "FINDING-01 REMEDIATION ACCEPTED — R1/R2/R3 co-sign + disclosure cross-check now jointly CO-SIGNED"; dual-signature mandate (AC-F / §RISK-DISPOSITION-20260423-1 Q6b B6) **SATISFIED**.
- Tests: `tests/core/test_run_with_ceiling.py` 49/49 PASS (45 pre-existing + 4 new); full suite 263 passed / 1 skipped (skip pre-existing, T002.0a blocker).

## Invariants preserved

- **Canonical manifest sha256:** `data/manifest.csv` = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` — verified byte-identical at (i) Quinn T002.0b gate session open/close, (ii) Quinn RA-20260426-1 chain gate session open/close including post-T12b-replay stop/start of `sentinel-timescaledb`, (iii) Quinn T002.4 gate review, (iv) Riven co-sign R1 + FINDING-01 cross-check + remediation verification, (v) this @pm narrative write. Zero drift across the branch.
- **R5 kill/warn constants (`core/memory_budget.py`):** `CAP_ABSOLUTE = 8_400_052_224` (ADR-1 v3 floor-dominated), `HEADROOM_FACTOR = 1.3`, `KILL_FRACTION = 0.95` — byte-identical; `git diff 80805ac^ 80805ac -- core/memory_budget.py` EMPTY (Riven R1). `CEILING_BYTES = None` awaiting RA-20260428-1 step-7 derivation.
- **Parent R5 polling path (`core/run_with_ceiling.py`):** `git diff` EMPTY; 45 pre-existing tests remain green; Nyquist-vulnerable parent-poll artifact bypassed by T002.4 child-side kernel-peak retrieval, NOT modified.
- **ADR-2 additive-only contract (`core/telemetry_schema.py`):** `git diff` EMPTY; `SUMMARY_JSON_FIELDS` + `TELEMETRY_CSV_COLUMNS` tuples unchanged; new keys (`peak_commit_bytes_child_self_reported`, etc.) added downstream of library write as wrapper-side JSON augmentation only.
- **Hold-out lock (`_holdout_lock` canonical re-export):** fires before any I/O in `feed_timescale.load_trades`, `feed_parquet.load_trades`, `feed_cache.load_trades`, `build_raw_trades_cache.run`, and `generate_t12b_snapshot.main` — proven by sentinel-monkeypatch contract tests; `VESPERA_UNLOCK_HOLDOUT` unset throughout every gate session.
- **R10 custodial boundary (`scripts/materialize_parquet.py` canonical `_fetch_month_dataframe`):** untouched by §13.1/§13.2/P5 commits per §RISK-DISPOSITION Q5 DEFERRED; `git log --all --oneline -- scripts/materialize_parquet.py` returns only `f971bb5` (Dara future-run patch) + `80805ac5` (T002.4 bundled scope, pre-disclosed in `68627a8`).

## Test plan

- [x] **T002.0b contract + parity + perf:** 12 passed / 1 skipped; regression `tests/t002_eod_unwind/` 77/77 PASS; cold budget 1.25 s worst vs 10 s cap (8x margin); parity MD5(pickle) byte-identical over 314,060 rows.
- [x] **ADR-4 §13 + P5 wrapper:** `tests/t002_eod_unwind/adapters/test_feed_cache.py` 8/8 PASS; `tests/integration/test_adapter_parity_cache.py` T12a+T12b+T13 GREEN sentinel UP and sentinel DOWN (T12b 9.94 s empirical Q1 close); `tests/core/test_run_with_ceiling.py` 45/45 PASS (pre-T002.4 baseline); `tests/t002_eod_unwind/` 85/85 PASS; `tests/unit/test_build_raw_trades_cache.py` 11/11 PASS post-`63a9a3a` CONCERNS-01 fix. §13.1 pilot build: 21,058,318 rows, 210.89 MiB peak WS (17x margin), 3.40 min runtime (3x margin).
- [x] **T002.4 telemetry:** `tests/core/test_run_with_ceiling.py` 49/49 PASS (45 pre-existing + 4 new: emission on normal exit via real subprocess, parent parse + summary JSON augmentation with SUMMARY_JSON_FIELDS preservation, missing-line fallback via `child_peak_telemetry_missing=True`, degraded-line `error=<reason>` suffix parse).
- [x] **Full regression:** `pytest tests/` -> **263 passed, 1 skipped** in 15.50 s (skip = `test_parquet_speed.py::test_hot_loop_cpcv_1path_250_sessions_under_budget`, pre-existing T002.0a blocker; Beckett signs when T002.0a full materialization completes).
- [x] **Ruff:** "All checks passed!" on `packages/t002_eod_unwind/adapters/`, on §13.1/§13.2 surfaces, and on the 3 T002.4-touched files.
- [x] **Mypy telemetry scope:** zero new telemetry-scope errors (pre-existing psutil-stubs + 2 cache-dispatch `arg-type` items flagged informationally; `types-psutil` follow-up).
- [x] **Canonical sha:** `sha256sum data/manifest.csv` = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified at merge-authorization time.

## Downstream unblocks

- **Task #124 — RA-20260428-1 draft (Riven):** consumes `peak_commit_bytes_child_self_reported` as step-7 CEILING_BYTES derivation primary input; Riven's R2/R3/R1 latent findings (missing `commit_charge_start_bytes` baseline, no `private_bytes` split, `child_peak_telemetry_missing=True` veto contract, `R5_EMERGENCY_KILL` vs `KILL_FRACTION` naming) carried into task #124 scoping notes.
- **Task #78 — CEILING_BYTES empirical derivation (GitHub issue):** unblocked once RA-20260428-1 step-7 ingests 3-5 runs of telemetry emissions under representative workload.
- **Task #71 — Mai+Jun 2025 materialize relaunch (@devops Gage):** unblocked on P5 wrapper + RA-20260426-1 ISSUED; runs under `--source=cache` per Decision 5 with quiesce retry #5 cleared of pre-merger gating.
- **T002.0a completion (Dex/Dara):** next run benefits from `f971bb5` cursor-streaming + per-month flush + gc patch; once complete, T6b hot-loop test unblocks trivially (remove `@pytest.mark.skip`).

## Execution instructions for @devops Gage

Per AIOX Agent Authority matrix, **@devops Gage has EXCLUSIVE authority** for `git push`, `gh pr edit`, and `gh pr merge` on this repository. Morgan (@pm) does not execute any write operation — this narrative authorizes the merger per epic orchestration scope.

1. **Update PR title:**
   ```bash
   gh pr edit 2 --title "feat(t002): T002.0b+ADR-4+T002.4 — adapters, pre-cache, child telemetry"
   ```

2. **Update PR body** — copy the body section above (between the fenced ```markdown block) into a temp file and apply via:
   ```bash
   gh pr edit 2 --body-file /tmp/pr-2-body.md
   ```

3. **Push branch to update PR #2 head** from stale `f08f027` -> authorized `68627a8`:
   ```bash
   git push origin t002-refactor-next-run
   ```
   This updates PR #2 to include all 10 commits. Do NOT force-push — the PR head is a descendant of the current tip.

4. **Merge strategy: `--merge` (merge commit)** — NOT squash. Rationale in the next section.
   ```bash
   gh pr merge 2 --merge --delete-branch=false
   ```
   (Keep the branch for post-merge audit; delete manually after canonical-sha verification.)

5. **Post-merge verification (Gage):**
   - `git fetch origin && git checkout main && git pull`
   - `sha256sum data/manifest.csv` must equal `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`
   - `git log --oneline origin/main | head -15` should show all 10 merged commits on the main timeline
   - Update story `docs/stories/T002.4.story.md` status: Draft/InReview -> **Done**
   - Optional branch cleanup: `git push origin --delete t002-refactor-next-run` (only after canonical-sha re-verified on main)

6. **Notification to squad:**
   - Riven: RA-20260428-1 task #124 is unblocked; telemetry schema lives in `scripts/run_materialize_with_ceiling.py` `_augment_summary_with_child_peak`.
   - Gage: task #71 (Mai+Jun 2025 relaunch under `--source=cache`) is unblocked; retry #5 clear to launch.

## Merge strategy rationale: MERGE COMMIT (not squash)

This PR bundles **three separately-governed story scopes** on one physical branch:
1. T002.0b adapters (#63, Quinn PASS)
2. ADR-4 pre-cache amendment (§13.1 + §13.2 + P5 + issuance flip, Quinn CONCERNS->resolved + Orion flip)
3. T002.4 child telemetry (#118, Quinn CONCERNS + Riven CO-SIGN dual-sign)

Squashing would collapse these three scopes into a single opaque mainline commit, **destroying the per-scope audit trail** that Riven's FINDING-01 addendum and future RA-20260428-1 task #124 scoping explicitly reference. Specifically: (a) `80805ac` and `68627a8` form the commit+remediation pair that Riven's dual-sign is anchored to — squashing erases `68627a8` as a standalone disclosure artifact; (b) `63a9a3a` is the narrow CONCERNS-01 fix that unlocked RA-20260426-1 DRAFT->ISSUED — squashing hides the cause-and-effect link between Quinn's chain gate CONCERNS and the remediation; (c) `f971bb5` is a Dara R10-custodial patch whose authorship provenance matters for future R10 boundary audits. Merge commit preserves all 10 commits as distinct mainline ancestors; `git log --first-parent main` still reads cleanly as a single epic milestone; `git bisect` remains usable at per-commit granularity.

## Footer

Merger authorized by @pm (Morgan), 2026-04-23.
Dual-sign satisfied (Quinn T002.0b PASS + Quinn+Riven T002.4 CO-SIGN + Quinn RA-20260426-1 CONCERNS->resolved).
Canonical sha verified unchanged: `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## Commit-to-governance map

| # | SHA | Subject | Scope | Primary governance artifact | Supporting artifacts |
|---|-----|---------|-------|------------------------------|----------------------|
| 1 | `59e03fe` | feat(t002.0e): add Nova cost atlas v1.0.0 with Sable audit | T002.0e | `docs/backtest/nova-cost-atlas-audit.md` (Sable APPROVED_WITH_CONDITIONS) | `docs/stories/T002.0e.story.md`, `docs/backtest/nova-cost-atlas.yaml` sha256 `acf44941...`, Pax 9.5/10 GO + Quinn PASS (commit body attested) |
| 2 | `f971bb5` | fix(materialize): cursor streaming + per-month flush + gc | T002.0a unblock (Dara R10-custodial) | Commit body (Dara custodial authority) | `docs/architecture/T002-end-of-day-inventory-unwind-design.md` (R10 boundary); empirically validated at §13.1 pilot build 210.89 MiB |
| 3 | `f08f027` | feat(t002): T002.0b Data Adapters | T002.0b | `docs/qa/gates/T002.0b-qa-gate.md` (Quinn PASS, 7/7 checks, 15/15 AC) | `docs/stories/T002.0b.story.md` (#63), `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` |
| 4 | `8c217bf` | feat(build-cache): §13.1 streaming parquet writer | ADR-4 §13.1 | `docs/qa/gates/RA-20260426-1-chain-gate.md` (Quinn, §13.1 A1-A5 traceability PASS) | `docs/architecture/pre-cache-layer-spec.md` §13.1 (#107/#109); `docs/MANIFEST_CHANGES.md` `r4_amendment` entries (L112/159/231/327); `.tmp/ws_peak.txt` P4 evidence |
| 5 | `cb62713` | test(t12-split): §13.2 T12a/T12b split | ADR-4 §13.2 | `docs/qa/gates/RA-20260426-1-chain-gate.md` (§13.2 T12b sentinel-DOWN GREEN, P1 evidence) | MANIFEST.sha256 `03b2ee8e...` snapshot integrity; snapshot sha256 `2c167eb1...` |
| 6 | `85664f7` | feat(wrapper): --source/--cache-dir/--cache-manifest passthrough | ADR-4 P5 | `docs/qa/gates/wrapper-passthrough-gate.md` + `docs/qa/gates/RA-20260426-1-chain-gate.md` §P5 | `scripts/run_materialize_with_ceiling.py` L134-194 + L238-243; 5 dedicated tests in `tests/core/test_run_with_ceiling.py` L586-681 |
| 7 | `63a9a3a` | test(build-cache): repoint monkeypatches | ADR-4 §13 CONCERNS-01 remediation | `docs/qa/gates/RA-20260426-1-chain-gate.md` §CONCERNS-01 | `tests/unit/test_build_raw_trades_cache.py` 11/11 PASS post-fix |
| 8 | `f0e8741` | docs(governance): flip RA-20260426-1 DRAFT->ISSUED | ADR-4 / RA-20260426-1 issuance | `docs/architecture/memory-budget.md` §RA-20260426-1 ISSUED banner (L1825-2110) | `data/baseline-run/ra-20260426-1-evidence/` sha256 manifest; Orion flip on Riven-delegated authority; §RISK-DISPOSITION-20260423-1 |
| 9 | `80805ac` | feat(T002.4): child-side peak telemetry | T002.4 | `docs/qa/gates/T002.4-qa-gate.md` (Quinn CONCERNS) + `docs/qa/cosigns/T002.4-riven-cosign.md` (Riven CO-SIGN R1/R2/R3) | `docs/qa/validations/T002.4-story-draft-validation.md` (Pax 10/10 GO); `docs/stories/T002.4.story.md` (#118); `docs/architecture/pre-cache-layer-spec.md` §14.5.2 B1 |
| 10 | `68627a8` | docs(T002.4): disclose bundled scope (FINDING-01) | T002.4 Riven FINDING-01 remediation | `docs/qa/cosigns/T002.4-riven-cosign.md` §"Addendum — FINDING-01 remediation verified" | `docs/stories/T002.4.story.md` Dev Agent Record §"Bundled scope disclosure" |

All 10 commits mapped to primary governance artifacts. Zero ungoverned commits. Dual-sign mandate (AC-F / §RISK-DISPOSITION-20260423-1 Q6b B6) SATISFIED for the T002.4 pair.

---

## Execution instructions for @devops Gage

1. `gh pr edit 2 --title "feat(t002): T002.0b+ADR-4+T002.4 — adapters, pre-cache, child telemetry"`
2. `gh pr edit 2 --body-file /tmp/pr-2-body.md` (extract the fenced markdown body above into that temp file first)
3. `git push origin t002-refactor-next-run` (updates PR #2 head `f08f027` -> `68627a8`, adding the 7 trailing commits)
4. **Strategy: merge commit** — `gh pr merge 2 --merge --delete-branch=false`
   Rationale: preserves all 10 commits on the mainline as distinct ancestors; squash would collapse the 3 separately-governed story scopes (T002.0b, ADR-4 pre-cache, T002.4) and lose the per-commit audit trail that Riven's FINDING-01 addendum + RA-20260428-1 task #124 scoping explicitly reference (especially the `80805ac`+`68627a8` commit-remediation pair and the `63a9a3a` CONCERNS-01 narrow fix link to RA-20260426-1 ISSUED).
5. **Post-merge:**
   - `git fetch origin && git checkout main && git pull`
   - Verify `sha256sum data/manifest.csv` = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` (MUST match; zero drift allowed)
   - Update story `docs/stories/T002.4.story.md` status Draft/InReview -> **Done**
   - Optional branch cleanup only after canonical-sha re-verified.
6. **Downstream notifications:** Riven (task #124 RA-20260428-1 unblocked), Gage self (task #71 Mai+Jun 2025 relaunch under `--source=cache` unblocked), Dex (task #78 CEILING_BYTES derivation unblocked once RA-28-1 ingests 3-5 telemetry runs).

---

**Narrative authored by:** @pm (Morgan), 2026-04-23
**Authorization basis:** AIOX Agent Authority — @pm EXCLUSIVE authority for epic orchestration + EPIC-T002 execution management; @devops Gage EXCLUSIVE authority for the git/gh write operations that implement this narrative.
**Canonical sha at narrative write:** `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` (VERIFIED UNCHANGED).
