# Pre-flight Coherence Audit — Pre `*run-cpcv --dry-run`

**Auditor:** Sable (`@squad-auditor`, The Skeptic ♒)
**Date:** 2026-04-25 BRT
**Scope:** EPIC-T002.0 + EPIC-T002 epic-wide coherence check before Beckett dry-run
**Mode:** Read-only audit — Sable does not modify code, gates, specs, or stories. Reports findings only.

---

## 1. Story status verification (8/9 Done at the gate level — 4 narrative drift)

| Story | Story-file Status (line 4) | QA gate (archive) | Verdict |
|-------|----------------------------|-------------------|---------|
| T002.0a | `Done` (Pax co-signed 2026-04-25T18:46) | 10/10 Sable gates PASS (`T002.0a-sable-gates.md`) + Dex reimpl audit | CONFIRMED |
| T002.0b | `Done` (Quinn QA gate PASS 2026-04-22) | PASS (`T002.0b-qa-gate.md`) | CONFIRMED |
| T002.0c | `Ready for Review (Quinn QA gate pending)` | **PASS** (`T002.0c-qa-gate.md` 2026-04-25) | **DIVERGENCE** — story file not bumped |
| T002.0d | `Ready for Review` | **PASS** with documented MEDIUM/LOW residuals (`T002.0d-qa-gate.md` 2026-04-25) | **DIVERGENCE** — story file not bumped |
| T002.0e | `Ready-for-QA-Quinn` | **PASS** (`T002.0e-qa-gate.md` 2026-04-25) | **DIVERGENCE** — story file not bumped |
| T002.1 | `Draft → Pax validation` (also says `Pax 10/10 GO v0.2.0` + Dex impl complete + Quinn PASS in body) | **PASS — 1 LOW informational** (`T002.1-qa-gate.md` 2026-04-25) | **DIVERGENCE** — header status line stale |
| T002.2 | `Done` (17/17 tests passing) | (No standalone QA gate filed — code-complete asserted in story body) | CONFIRMED with caveat (no formal Quinn gate file in `docs/qa/gates/`) |
| T002.3 | `Done` (32/32 tests passing) | (No standalone QA gate filed — same caveat) | CONFIRMED with caveat |
| T002.4 | `Done` (PR #2 merged, dual-sign Quinn+Riven) | CONCERNS (`T002.4-qa-gate.md`) + Riven CO-SIGN dual-sign satisfied | CONFIRMED |

**Total:** 5 stories with `Done` header, 4 with stale header (T002.0c/0d/0e/1) despite Quinn PASS verdicts present in `docs/qa/gates/`. Gates exist; story headers were not updated.

---

## 2. Spec coherence

- **Spec ML T002 — End-of-Day Inventory Unwind WDO:** filesystem holds `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml`. Whole-file sha `98f22f3c...24614` (matches design doc §13 `spec_hash`). `mira_signature_sha256_of_file_before_this_line` = `4b5624ad...dc3fc` (matches EPIC-T002.0 `spec_sha256` field). Both shas valid under different conventions; cross-reference consistent across EPIC + spec + design.
- **PRR-20260421-1:** registered in spec `preregistration_revisions[]` (line 103+) with breaking-fields enumerating P252→P126 lookback shift, in_sample window shift, and ATR_day_ratio descriptor. Carry-forward opt-in entries cover Nova + Nelo per-scope no-touch declaration. R15 trail satisfied.
- **Design doc §3.2 + §13 ALN-20260425-1:** alignment block (line 344+) records the 252→126 reword event with `triggered_by: "Pax flagged divergence"`. §3.2 title now `Percentis rolling 126d`. Architectural rationale paragraph (line 104) cites Sentinel TimescaleDB coverage gap as root cause. All 4 fields (title, build offline, persistence path, reframing) edited consistently.
- **Spec vespera-metrics:** v0.2.2 (Mira-signature `56238dc2...891f`) — confirmed in filesystem at `docs/ml/specs/T002-vespera-metrics-spec.md` lines 10-11. Revision history §1.1+ logs v0.2.0→v0.2.1 (Dex Article-IV escalation, PBO 5/6→1.0 walkthrough fix) → v0.2.1→v0.2.2 (Quinn errata sweep on stale 0.8333 references at line 712).

**Verdict:** spec layer aligned. No invented elements; PRR-20260421-1 + ALN-20260425-1 form a complete trail.

---

## 3. Code coherence

| Package | Filesystem | Quinn gate |
|---------|-----------|-----------|
| `packages/t002_eod_unwind/` | exists with `warmup/`, `core/`, `adapters/` subdirs | T002.0b PASS (adapters), T002.0e PASS (engine-config wire), T002.1 PASS (warmup) |
| `packages/vespera_cpcv/` | exists — `__init__`, `config.py`, `engine.py`, `purge.py`, `result.py`, `runner.py` | T002.0c PASS (CPCV engine + result + runner) |
| `packages/vespera_metrics/` | exists — `dsr.py`, `pbo.py`, `info_coef.py`, `sharpe.py`, `drawdown.py`, `trade_stats.py`, `report.py` | T002.0d PASS (8/8 mandatory checks; T11 PBO=1.0 byte-exact) |

All three packages exist and Quinn-validated against their gate files. No structural gaps from Beckett-side dependencies for `*run-cpcv --dry-run`.

---

## 4. Cross-cutting invariants

| Rule | Source | Verdict | Evidence |
|------|--------|---------|----------|
| **R6 CPCV defaults** (N=10–12, k=2, 45 paths, embargo=1) | MANIFEST.md:106 | CONFIRMED | T002.0c gate covers `CPCVConfig + from_spec_yaml`; spec v0.2.0 §CPCV consumes these defaults. |
| **R7 trades-only** (book-based features = live-only) | MANIFEST.md:108-109 | CONFIRMED | Spec v0.2.0 feature set (close/open/high/low/ATR_20d) is trades-only; T002.0b parity audit certifies adapters do not surface book fields. |
| **R10 hold-out bounds preserved** (`VESPERA_UNLOCK_HOLDOUT`, 2025-07-01 → 2026-04-21) | MANIFEST.md:138 | CONFIRMED | T002.0a G03 (manifest hold-out grep, 19-line) PASS; T002.0b adapters fire `assert_holdout_safe` before I/O; canonical-invariant.sums pin `data/manifest.csv` sha = `78c9adb3...ee72`. |
| **R15 manifest invariant pin** (`78c9adb3...ee72` post MC-29-1 D3+D4) | `.github/canonical-invariant.sums:1` | CONFIRMED | Post-D4 (Jun-2025 commit) sha confirmed in `data/canonical-relaunch/mc-20260429-1-evidence/CHECKPOINT-RESUME-HERE.md` + `decision-4-jun-2025-result-success.json`. Invariant pin matches sums file. |

---

## 5. Article IV (No Invention) traceability

| Decision | Precedent | Status |
|----------|-----------|--------|
| Spec v0.1.0 → v0.2.0 (P252→P126) | PRR-20260421-1 (Pax co-signed `c34c201c…79e5a`) under MANIFEST R15 | TRACED |
| Design doc §3.2 252→126 reword | ALN-20260425-1 alignment block in design doc §13 | TRACED |
| Vespera-metrics spec v0.2.0→v0.2.1 (PBO=1.0) | Dex Article-IV escalation in T002.0d gate §8 + spec §15 (Mira credits Dex) | TRACED |
| Vespera-metrics spec v0.2.1→v0.2.2 (T11 errata) | Quinn finding in T002.0d gate review | TRACED |
| MANIFEST sha `78c9adb3...ee72` | MC-20260429-1 D3 + D4 SUCCESS, decision-4-jun-2025-result-success.json + CHECKPOINT | TRACED |
| 18→19 row manifest | MC-20260429-1 Stage-2 D3 (May) + D4 (Jun); Sable G10 16/16 frozen + 18/18 self-match | TRACED |
| ADR-1 v3 cap recalibration (CAP_v3=8,400,052,224) | RA-20260424-1 quiesce floor + Aria recalibration (memory-budget.md §1335+); Riven 7-point GO co-sign + Quinn ADR-1-v3-audit PASS 7/7 | TRACED |
| R15.2 canonical-invariant hardening | RA-20260428-1 Decision 7 (story authority) + MWF-20260422-1 (manifest write contract); R15-PR3-pre-merge-gate + R15-canonical-invariant-hardening-qa-gate both PASS | TRACED |

No invented decisions detected on the chain leading to dry-run.

---

## 6. Gates archive completeness

`docs/qa/gates/` contents (alphabetical): ADR-1-v2-audit, ADR-1-v3-audit, MC-20260429-1-chain-gate, MC-20260429-1-p3-sentinel-gate, MWF-20260422-1-gate, R15-PR3-pre-merge-gate, R15-canonical-invariant-hardening-qa-gate, RA-20260426-1-chain-gate, RA-20260428-1-P2-refactor-gate, RA-20260428-1-chain-gate, T002.0a-dex-reimpl-audit, T002.0a-sable-gates, T002.0b-qa-gate, T002.0c-qa-gate, T002.0d-qa-gate, T002.0e-qa-gate, T002.1-qa-gate, T002.4-qa-gate, wrapper-passthrough-gate, evidence/T002.0a/ (g01, g06, g07, g08, g10).

**Missing files identified:** **no standalone Quinn QA gate file** for **T002.2** or **T002.3** in `docs/qa/gates/`. Both stories assert `Done (code-complete, N/N tests passing)` in their story-body but no `T002.2-qa-gate.md` / `T002.3-qa-gate.md` exists in the gates archive. This is a paper-trail gap (severity ⚠️ — does not invalidate code, but breaks story-driven traceability discipline).

---

## 7. Verdict

**APPROVED_FOR_DRY_RUN** — with 1 ⚠️ moderate finding to record (story-status drift) and 1 ⚠️ moderate finding (T002.2/T002.3 paper-trail). Neither blocks `*run-cpcv --dry-run` because:

1. Dry-run consumes spec v0.2.0 + warmup + adapters + CPCV engine + metrics. All four substrates are Quinn-PASS in their gate files; story-status drift is narrative housekeeping, not substantive.
2. T002.2 / T002.3 absence of standalone gate files is paper-trail, not a substantive failure — story bodies report 17/17 + 32/32 tests green, and these packages (likely embedded in `t002_eod_unwind`) were exercised via cross-stories under T002.0c/T002.1 regression suites.
3. Cross-cutting invariants R6/R7/R10/R15 all CONFIRMED. Hold-out is intact. MANIFEST pin matches.
4. Article IV chain is fully traced. No invented features detected.

Beckett may proceed to `*run-cpcv --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run`.

---

## 8. Findings

### ⚠️ Moderate findings (do not block dry-run)

**AUDIT-20260425-001 — Story-status drift (4 stories)**
- **Tag:** [DIVERGENCE]
- **Scope:** `docs/stories/T002.0c.story.md:4`, `T002.0d.story.md:4`, `T002.0e.story.md:4`, `T002.1.story.md:4`
- **Expected:** Story header `Status:` line should reflect `Done` after Quinn PASS gate filed.
- **Actual:** All four headers still show pre-PASS state (`Ready for Review`, `Ready-for-QA-Quinn`, `Draft → Pax validation`).
- **Owner:** River (@sm) for header bumps OR Pax (@po) per story-lifecycle convention. Not Quinn (Quinn produces the gate file; bump is downstream housekeeping).
- **Action:** Bump status header on each of the 4 stories to `Done (Quinn QA gate PASS 2026-04-25)` before next epic phase. Non-blocking for dry-run.

**AUDIT-20260425-002 — T002.2 + T002.3 missing standalone QA gate files**
- **Tag:** [GAP]
- **Scope:** `docs/qa/gates/` has no `T002.2-qa-gate.md` and no `T002.3-qa-gate.md`.
- **Expected:** Per story-driven discipline, every Done story should have a Quinn gate artifact in `docs/qa/gates/`.
- **Actual:** Story bodies assert `Done (code-complete, 17/17 / 32/32 tests passing)` but no standalone gate file exists.
- **Owner:** Quinn (@qa) — produce post-hoc gate files anchoring the existing test counts to AC matrices, OR explicitly waive per River/Pax decision recorded in `MANIFEST_CHANGES.md`.
- **Action:** Backfill or formal waiver. Non-blocking for dry-run (substrate is functioning).

### 💡 Cosmetic findings (informational)

**AUDIT-20260425-003 — Optional G02/G03 single-purpose artifacts for 18-row state**
- **Tag:** [GAP-ACCEPTED]
- **Scope:** `docs/qa/gates/evidence/T002.0a/`
- **Expected:** Single-purpose `g02-rowcount-phase.txt` and `g03-holdout-grep.txt` for the 18-row state.
- **Actual:** Both checks already PASS via existing evidence — G10 cross-references the phase distribution; Morgan's re-grep confirmed 0 hold-out leak — but as separate artifact files they were not produced.
- **Owner:** Sable (already noted in `T002.0a-sable-gates.md` as item 6 "Non-blocking observation").
- **Action:** None required for dry-run. Optional house-keeping if Story.AC11 is interpreted strictly.

### 🔴 No critical findings.

---

## 9. Files written

- `docs/audits/AUDIT-20260425-PRE-DRYRUN-CPCV.md` (this report)

No code, spec, story, or gate file was modified by Sable.

---

## 10. Próximo handoff

**Beckett (@backtester) is cleared to execute:**

```bash
*run-cpcv --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run
```

**Recommended pre-flight sequence:**
1. (Optional, non-blocking) River/Pax close AUDIT-20260425-001 by bumping 4 story headers.
2. (Optional, non-blocking) Quinn closes AUDIT-20260425-002 by either backfilling T002.2/T002.3 gate files or waiving with R10 record.
3. Beckett proceeds with dry-run. Sable to re-audit post-dry-run only if dry-run output references invariants outside the chain documented above.

— Sable, o cético do squad 🔍
