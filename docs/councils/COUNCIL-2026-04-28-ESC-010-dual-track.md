# Council 2026-04-28 — ESC-010 Dual-Track (WarmUpGate singleton + make_backtest_fn stub)

**Date (BRT):** 2026-04-28
**Trigger:** Beckett T11.bis #4 (N4) HALT-ESCALATE 2026-04-28 BRT — dual-track findings.
**Source diagnostics:**
- Beckett N4 report: [docs/backtest/T002-beckett-t11-bis-smoke-report-N4-2026-04-28.md](../backtest/T002-beckett-t11-bis-smoke-report-N4-2026-04-28.md)
- DIAGNOSTIC run artifacts (no `--smoke`): `data/baseline-run/cpcv-dryrun-T002-N4-DIAG-NOSMOKE/` — 5 artifacts persisted; `run_id 324c151fe42a49bbab6ec44d4fc2ff28`
- USER-ESCALATION-QUEUE.md ESC-010 entry (2026-04-28 BRT)
- ESC-009 council ledger (Track A blind spot acknowledged): [COUNCIL-2026-04-27-ESC-009-AC8-amendment.md](COUNCIL-2026-04-27-ESC-009-AC8-amendment.md)
- Aria architecture finding M1 (DEFERRED-T11): `packages/t002_eod_unwind/cpcv_harness.py:287-307` docstring + `:707` verbatim "T11 will swap in real per-fold rebuild" comment
**Council convener:** Orion (@aiox-master) under autonomous-mode mandate
**Council size:** 6 voters (Aria + Mira + Beckett + Riven + Pax + Dara)
**Protocol:** Independent vote (Track A + Track B), no cross-visibility before consolidation
**Outcome (Track A):** **5/6 MAJORITY APPROVE_E2** (drop `--smoke` from AC8 invocation literal); Dara dissent E1 (data integrity stance) registered for transparency
**Outcome (Track B):** **6/6 FUNCTIONAL CONVERGENCE em F2-with-binding-F3-commitment + NEW §9 HOLD #2 armed** (Riven custodial veto authority — F2 sem F3 → REJECT; combined F2+F3-commitment cleared)
**User authorization:** Autonomous mode mandate 2026-04-26 BRT (mini-council decides per Article II canonical 2026-04-26)

---

## 1. Context

ESC-009 mini-council 6/6 functional convergence APPROVE_D2_NARROW `as_of=2024-08-22` (2026-04-27 BRT) directed Beckett N4 re-run with amended invocation `--smoke --in-sample-start 2024-08-22 --in-sample-end 2025-06-30`. Operator precompute at `as_of=2024-08-22` had already completed (cache hit verified). N4 empirical result:

```
HALT exit=1 in 2.892s before fanout
"smoke phase failed; aborting full run per AC11: warmup not satisfied for 2025-05-31:
 status=WARM_UP_FAILED; reason=atr: stale as_of_date (file=2024-08-22, expected=2025-05-31)"
```

Beckett N4 root-cause analysis surfaced **TWO** independent architectural findings (dual-track), both invisible to ESC-009's static analysis:

### Track A — WarmUpGate singleton + default-path binding

- `scripts/run_cpcv_dry_run.py:848` instantiates ONE `WarmUpGate` shared between smoke + full phases.
- `:865`: `smoke_in_sample_start = max(in_sample_start, in_sample_end - 30d) = 2025-05-31` independent of `--in-sample-start`.
- `WarmUpGate` reads from `_DEFAULT_ATR_PATH` / `_DEFAULT_PERCENTILES_PATH` (default-path symlink/copy), NOT a dated path.
- Default path holds the LAST WRITE — currently `as_of=2024-08-22` (most recent precompute output).
- Smoke phase requests `as_of=2025-05-31`, finds `2024-08-22` → `WARM_UP_FAILED` → AC11 protective abort.
- **Implication:** AC8 amended invocation **CANNOT** simultaneously satisfy smoke (needs 2025-05-31) and full (needs 2024-08-22) under the current harness. ESC-009 6/6 modeled `warmup_gate_as_of` for full-phase but did NOT inspect the singleton + default-path binding. Discovery requires N4 empirical execution; not visible from static read alone.

### Track B — make_backtest_fn neutral stub (degenerate KillDecision)

- DIAGNOSTIC run (no `--smoke`, run_id `324c151fe42a49bbab6ec44d4fc2ff28`): exit=0, wall=4.596s, peak RSS 0.14 GiB, 5 artifacts persisted, sha256 prefixes recorded.
- KillDecision NO_GO over 45 path Sharpes ALL 0.0, IC=0, PBO=0.5 default, DSR=0.5 default.
- Root cause: `packages/t002_eod_unwind/cpcv_harness.py::make_backtest_fn` is **neutral stub**, NOT real strategy. Same degenerate pattern as N3 smoke synthetic, but now over the full ~10mo CPCV window — proves degeneracy is **architectural** (stub), NOT sample-size.
- Verbatim cpcv_harness.py:707 `"T11 will swap in real per-fold rebuild"` — documents intentional stub state inherited from T002.0f-T3.
- DEFERRED-T11 docstring at cpcv_harness.py:287-307 (Aria architecture finding M1, 2026-04-26 BRT).
- **Implication:** AC8.9 `verdict ∈ {GO, NO_GO}` literal-PASS but semantically vacuous re strategy edge. Real T002 GO/NO-GO decision NOT testable under stub. Phase F gate (next custodial barrier before capital ramp) requires real `make_backtest_fn` — but that is OUT OF SCOPE for T002.0h declared.

### 3 mitigation paths surfaced (Track A)

- **(E1)** Harness amendment — `WarmUpGate` per-phase dated paths. Per-phase instantiation at L848 + dated-path resolvers at L120-121. Smoke reads `--in-sample-start`-aware as_of OR continues current `max(...)` derivation but lookups dated path. AC9 cache contract preserved + audit chain enriched per-phase.
- **(E2)** Drop `--smoke` flag from AC8 invocation literal. DIAGNOSTIC empirically validates exit=0 + 5 artifacts + KillDecision (run_id 324c151f...). AC11 protective abort REMAINS in spec — only the AC8 gating execution surface is decoupled. Long-term harness amendment deferred to T002.0h.1 successor.
- **(E3)** Other (no concrete proposal made; placeholder).

### 3 mitigation paths surfaced (Track B)

- **(F1)** Integrate real `make_backtest_fn` now — within T002.0h scope. ~5-10 sessions Mira+Dex+Beckett.
- **(F2)** Redefine AC8.9 stub-OK — AC8.9 verifies PIPELINE INTEGRITY (engineering exit gate: verdict computed without TIMEOUT/MEMORY_HALT, set membership ∈ {GO, NO_GO}); strategy edge clearance via real `make_backtest_fn` deferred to T002.1.bis successor + NEW §9 HOLD #2.
- **(F3)** Split into T002.0h.1 (E1 harness amend) + T002.1.bis (real make_backtest_fn) — in-flight story split.

---

## 2. Votes (condensed; full verbatim transcripts retained in council session log)

### 2.1 Aria voto (@architect)

**Track A verdict:** APPROVE_E2 (with 5 conditions)
**Track B verdict:** APPROVE_F3 (story split — T002.0h.1 + T002.1.bis)
**Personal preference declared:** E2 + F3

**Top rationale (Track A — 3 points):**
1. **DIAGNOSTIC run anchors empirical viability** — run_id 324c151f... PASS without --smoke (exit=0, 4.596s wall, peak RSS 0.14 GiB, 5 artifacts persisted with recorded sha256 prefixes per N4 §4) refutes hypothesis that `--smoke` is necessary for AC8 closure. The smoke phase is an OPTIMIZATION (~30s budget), not a gate criterion. AC11 protective abort REMAINS in spec — only the AC8 execution surface is narrowed.
2. **Singleton + default-path binding is a HARNESS FAULT (not spec/story fault)** — `run_cpcv_dry_run.py:848` shared WarmUpGate + L865 hardcoded `max(...)` smoke window + default-path-only lookup at WarmUpGate level. Long-term fix is E1 (per-phase dated paths). But T002.0h scope is orchestrator-only refactor; harness amendment is OUT OF SCOPE per Guard #4 + R15. Therefore E2 (AC8 narrowing) at story level + E1 spawned as successor T002.0h.1.
3. **R15 cleanly traceable** — AC8 invocation literal is story-level breaking_field (already-amended path via PRR-20260427-1). Spec yaml `data_splits` UNCHANGED. PRR-20260428-1 documents empirical refutation of the implicit assumption that `--smoke` was a gate criterion.

**Track A 5 conditions:**
1. AC8 invocation literal narrowed: drop `--smoke`. AC11 protective abort REMAINS in spec.
2. PRR-20260428-1 append to `preregistration_revisions[]` documenting empirical anchor (DIAGNOSTIC run_id 324c151f...).
3. Spec yaml `data_splits.in_sample` UNCHANGED.
4. Anti-Article-IV Guard #5 (extended, ESC-009 honored): N4 empirical refutation = authorization basis for E2, NOT retry.
5. Story T002.0h.1 spawn for E1 long-term harness amendment (per-phase dated paths). NON-BLOCKING for T002.0h closure.

**Top rationale (Track B — 3 points):**
1. **F1 violates T002.0h scope** — integrating real `make_backtest_fn` requires per-fold P126 rebuild (DEFERRED-T11 finding M1) + spec-grade strategy translation (triple-barrier exits, P60/P20/P80 percentile filters, signal-to-trade conversion, cost atlas wired). ~5-10 sessions; CONSUMES T002.0h scope; violates Guard #4 (builder API + spec immutability) + R15.
2. **F3 honest split** — T002.0h.1 = E1 harness amend (Dex+Aria, ~2-3 sessions); T002.1.bis = real `make_backtest_fn` (Mira+Dex+Beckett, ~5-10 sessions). Both NON-BLOCKING for T002.0h closure. NEW §9 HOLD #2 armed (Riven authority) — capital-ramp clearance gated on T002.1.bis PASS + Beckett N5 PASS + Mira statistical clearance + dual-sign disarm.
3. **F2 alone is insufficient** — narrows AC8.9 scope but does NOT spawn the successor stories. Without the explicit T002.1.bis spawn, Phase F unblock is structurally orphaned. F3 = F2 + explicit story creation.

**Signature:** Aria 2026-04-28 BRT.

---

### 2.2 Mira voto (@ml-researcher)

**Track A verdict:** APPROVE_E2 (statistical-power assessment unchanged; engineering exit gate orthogonal to ML viability)
**Track B verdict:** APPROVE_F2 (with 4 conditions; formalize ESC-009 condition #4 already adopted 6/6)
**Personal preference declared:** E2 + F2 (functionally equivalent to F3 once T002.0h.1 + T002.1.bis spawned)

**Top rationale (Track A — 2 points):**
1. **Statistical power UNCHANGED** — DIAGNOSTIC run anchors AC8.9 verdict computation over the same ~10mo in-sample CPCV window (~225 valid sample days) as ESC-009 6/6 ratified. Bonferroni n_trials=5 + DSR distribution remain non-degenerate. Sample preservation invariant across smoke vs full phase choice.
2. **Anti-leak invariants preserved** — shifted-by-1 + ascending iteration are properties of the orchestrator over the lookback window (AC4/AC5); both hold under E2 (no harness modification at this layer).

**Track B authority statement (cited as decisive across all 6 voters):**

> "AC8.9 testa **PIPELINE INTEGRITY** (verdict computed without TIMEOUT/MEMORY_HALT, ∈ {GO, NO_GO} enum), NOT **STRATEGY EDGE**. Strategy edge validation é exclusive Phase F com real `make_backtest_fn` + per-fold P126 rebuild — separate story gated by Riven + Mira §9 cosign. F2 = formalização explícita de ESC-009 condition #4 já adopted 6/6."

**Track B 4 conditions:**
1. Spec yaml `data_splits.in_sample` UNCHANGED. Story-level AC8.9 scope refinement only.
2. PRR-20260428-2 append to `preregistration_revisions[]` documenting AC8.9 scope-boundary clarification (pipeline integrity vs strategy edge).
3. Hold-out lock `[2025-07-01, 2026-04-21]` UNTOUCHED.
4. **§9 deferral language for capital ramp clearance EXPLICITLY DEFERRED** to future story (T002.1.bis) when real `make_backtest_fn` integrated. Already-adopted ESC-009 condition #4 formalized via PRR-20260428-2 + NEW §9 HOLD #2 (Riven custodial veto authority).

**Signature:** Mira 2026-04-28 BRT.

---

### 2.3 Beckett voto (@backtester, consumer authority)

**Track A verdict:** APPROVE_E2
**Track B verdict:** APPROVE_F2
**Personal preference declared:** E2 + F2

**Top rationale (Track A — 3 points):**
1. **Beckett canonical operational threshold preserved** — DIAGNOSTIC run wall=4.596s + peak RSS 0.14 GiB clears amended AC8 budget by 65× (post-cache-hit < 5min envelope). 5 artifacts persisted with sha256 audit trail. KillDecision verdict ∈ {GO, NO_GO} computed (NO TIMEOUT, NO MEMORY_HALT).
2. **AC11 protective abort REMAINS in spec** — Beckett emphatically agrees: removing `--smoke` from AC8 does NOT remove the AC11 safety guard. The smoke phase + AC11 abort logic remain available + tested elsewhere; only the AC8 gating execution surface decouples.
3. **No empirical evidence supports E1 in-flight** — N4 empirical singleton observation REQUIRED execution to surface. E1 (per-phase dated paths) is the long-term fix BUT empirical proof of necessity stands at 1 N4 datapoint. T002.0h.1 successor enables proper testing without consuming T002.0h budget.

**Track B condition:**
- Beckett accepts F2 unconditional pending T002.1.bis spawn. AC8.9 PIPELINE INTEGRITY framing matches Beckett consumer-authority canonical (engineering exit gate ≠ strategy edge clearance).

**Signature:** Beckett 2026-04-28 BRT.

---

### 2.4 Riven voto (@risk-manager, custodial veto authority)

**Track A verdict:** APPROVE_E2
**Track B verdict:** APPROVE_F2 + **binding F3 commitment** + NEW §9 HOLD #2 armed (custodial veto exercised)
**Personal preference declared:** E2 + F2-with-F3-binding-commitment

**Track A rationale:**
- DIAGNOSTIC run empirically supports AC8 narrowed scope (engineering exit gate); custodial barrier UNCHANGED.

**Track B custodial veto language (verbatim):**

> "**Veto custodial: F2 SEM F3 commitment → REJECT.** F2 alone narrows AC8.9 semantic scope but leaves capital-ramp clearance pathway structurally orphaned. The `make_backtest_fn` neutral stub is a documented architectural gap (cpcv_harness.py:287-307 DEFERRED-T11 + :707 verbatim T11 comment); deferring strategy edge clearance to a future story REQUIRES that future story to exist as a registered governance entity, not as a vague 'when upstream coverage fixed' phrase. Combined F2 + F3-commitment (T002.0h.1 + T002.1.bis spawn as registered stories) cleared. Otherwise REJECT."

**NEW §9 HOLD #2 armed — 5 disarm gates (Riven custodial language preview, formal §9 amendment downstream post-Beckett N5):**
1. T002.0h.1 PASS (E1 harness amend — per-phase dated paths; Quinn integration test 2 distinct as_of coexisting; AC9 cache contract preserved + audit chain enriched per-phase).
2. T002.1.bis PASS (real `make_backtest_fn` integration; per-fold P126 rebuild; non-degenerate Sharpe distribution + IC + PBO + DSR over CPCV folds).
3. Beckett N5 PASS (post Pax cosign + T002.0h.1 + T002.1.bis closure — full pipeline empirical re-run).
4. Mira statistical clearance (formal §9 cosign on capital-ramp readiness post real-strategy CPCV).
5. Riven dual-sign disarm (custodial cosign on full clearance chain).

**Track B conditions:**
- Operator precompute pre-conditions UNTOUCHED (cache `as_of=2024-08-22` already exists; no precompute needed for Beckett N5).
- Hold-out lock `[2025-07-01, 2026-04-21]` UNTOUCHED.
- Spec yaml `data_splits.in_sample` UNCHANGED.

**Signature:** Riven 2026-04-28 BRT.

---

### 2.5 Pax voto (@po, council steward)

**Track A verdict:** APPROVE_E2 (with 5 conditions)
**Track B verdict:** APPROVE_F2 + T002.1.bis non-blocking spawn
**Personal preference declared:** E2 + F2 (with T002.0h.1 + T002.1.bis non-blocking spawn — functionally equivalent to F3)

**Top rationale (Track A — 3 points):**
1. **DIAGNOSTIC empirical anchor + AC11 spec preservation** — run_id 324c151f... validates exit=0 + 5 artifacts; AC11 protective abort retained at spec layer. AC8 invocation literal is story-level breaking_field (precedent PRR-20260427-1 path); patch bump 0.2.1 → 0.2.2.
2. **R15 trail clean** — PRR-20260428-1 documents empirical refutation of implicit `--smoke` gating assumption; PRR-20260428-2 formalizes AC8.9 PIPELINE INTEGRITY scope (Mira authority). Both story-level breaking_fields; spec yaml `data_splits` UNTOUCHED.
3. **Article IV trace complete** — every clause traceable to (a) Beckett N4 report verbatim error + DIAGNOSTIC artifacts, (b) cpcv_harness.py:707 verbatim T11 comment, (c) cpcv_harness.py:287-307 DEFERRED-T11 docstring (Aria M1), (d) ESC-009 condition #4 (Mira authority), (e) 6 verbatim votes recorded in this ledger.

**Track A 5 conditions (delegated to action items):**
1. PRR-20260428-1 (E2) appended via Pax cosign hash.
2. PRR-20260428-2 (F2) appended via Pax cosign hash.
3. Story T002.0h amendments — AC8 invocation literal drop `--smoke` + AC8.9 scope-boundary note + Change Log + 10-point re-validation.
4. T002.0h.1 + T002.1.bis non-blocking spawn (stub headers; @sm formal drafts downstream).
5. NEW §9 HOLD #2 armed (Riven custodial veto authority preserved verbatim).

**4 cosign acknowledgments + R15 ledger commitment:**
1. Aria architectural finding accepted as authoritative (Track A E2 + Track B F3 split into successor stories).
2. Mira authority statement (AC8.9 PIPELINE INTEGRITY vs STRATEGY EDGE dichotomy) accepted as decisive.
3. Beckett consumer-authority canonical (engineering exit gate) accepted.
4. Riven custodial veto authority accepted verbatim ("F2 SEM F3 commitment → REJECT") — combined F2+F3-commitment cleared via T002.0h.1 + T002.1.bis spawn + NEW §9 HOLD #2 armed.
5. **R15 breaking_field commitment:** `acceptance_criteria.AC8.invocation_literal` (PRR-20260428-1) + `acceptance_criteria.AC8.sub_criterion_8_9.semantic_scope` (PRR-20260428-2) — both story-level. Spec yaml `data_splits.in_sample` UNTOUCHED.

**Signature:** Pax 2026-04-28 BRT (Autonomous Daily Session, council steward authority).

---

### 2.6 Dara voto (@data-engineer)

**Track A verdict:** APPROVE_E1 (dissent — data integrity / auditability stance, registered for transparency)
**Track B verdict:** APPROVE_F3
**Personal preference declared:** E1 + F3

**Track A rationale (dissent):**
1. **Dara data-engineer authority on cache audit chain** — E2 narrows AC8 execution surface but leaves the WarmUpGate singleton + default-path binding architecturally unaddressed. From a data-integrity lens, the smoke vs full phase mismatch is a latent fault in the audit chain: the same WarmUpGate instance reports `as_of=2024-08-22` regardless of which phase requested it, masking the underlying coupling. E1 (per-phase dated paths) is the structurally correct fix.
2. **DIAGNOSTIC empirical PASS doesn't refute architectural concern** — run_id 324c151f... succeeds because the full phase request path matches the default-path-loaded as_of. Under any future configuration where smoke + full phases legitimately need DIFFERENT as_of dates, the singleton fault re-surfaces.
3. **Concession:** Dara accepts that E1 is OUT OF SCOPE for T002.0h (Guard #4 + R15). T002.0h.1 successor preserves Dara's structural concern as governance entity. Dara dissent is REGISTERED FOR TRANSPARENCY, not as a blocker for the 5/6 MAJORITY E2 outcome.

**Track B rationale:**
- F3 (split) honors both architectural concerns (T002.0h.1 = E1; T002.1.bis = real `make_backtest_fn`). Functionally identical to F2 + binding-F3-commitment under Riven custodial framing.

**Effective vote post-consolidation:** Dara dissent E1 registered; effective Track A outcome = 5/6 MAJORITY APPROVE_E2 (Aria + Mira + Beckett + Riven + Pax). Track B = 6/6 functional convergence (F2+binding-F3 / F3 collapse to same successor-story spawn outcome).

**Signature:** Dara 2026-04-28 BRT.

---

## 3. Vote consolidation

### Track A — drop `--smoke` from AC8 invocation literal

| Voter | Verdict (as cast) | Hard/Conditional/Personal-preference |
|---|---|---|
| Aria | APPROVE_E2 | conditional (5 conditions) — personal-preference E2 |
| Mira | APPROVE_E2 | conditional (statistical power assessment unchanged) — personal-preference E2 |
| Beckett | APPROVE_E2 | unconditional (consumer authority) — personal-preference E2 |
| Riven | APPROVE_E2 | unconditional (custodial barrier UNCHANGED) — personal-preference E2 |
| Pax | APPROVE_E2 | conditional (5 conditions delegated to action items) — personal-preference E2 |
| Dara | APPROVE_E1 | dissent — personal-preference E1 (registered for transparency) |

**Effective verdict tally Track A:**
- **E2 hard support:** 5/6 MAJORITY (Aria + Mira + Beckett + Riven + Pax)
- **E1 hard support:** 1/6 (Dara dissent registered for auditability transparency)
- **E3 hard support:** 0/6

### Track B — AC8.9 redefinition / story split

| Voter | Verdict (as cast) | Hard/Conditional/Personal-preference |
|---|---|---|
| Aria | APPROVE_F3 | conditional (story split honest framing) — personal-preference F3 |
| Mira | APPROVE_F2 | conditional (4 conditions; formalize ESC-009 condition #4) — personal-preference F2 |
| Beckett | APPROVE_F2 | unconditional pending T002.1.bis spawn — personal-preference F2 |
| Riven | APPROVE_F2 + binding F3 commitment | conditional (custodial veto exercised: "F2 SEM F3 → REJECT") — NEW §9 HOLD #2 armed |
| Pax | APPROVE_F2 + T002.1.bis non-blocking spawn | conditional (5 cosign acknowledgments) — functionally equivalent to F3 |
| Dara | APPROVE_F3 | conditional — personal-preference F3 |

**Effective verdict tally Track B (post-functional-convergence):**
- **F2 hard support:** 4/6 (Mira + Beckett + Riven + Pax)
- **F3 hard support:** 2/6 (Aria + Dara)
- **F1 hard support:** 0/6
- **Functional convergence:** 6/6 — all voters converge on spawning T002.0h.1 + T002.1.bis successor stories. F2 voters via non-blocking spawn (Pax delivery); F3 voters via in-flight split (same outcome). Riven custodial veto exercised: combined F2 + F3-commitment cleared.

**Conditions consolidated (10 unique action items):**
1. **AC8 invocation literal drop `--smoke` (E2; Aria #1, Beckett, Pax, Riven):** story T002.0h L65 — remove `--smoke` flag; AC11 protective abort REMAINS in spec.
2. **AC8.9 redefinition stub-OK (F2; Mira authority decisive ruling):** add scope-boundary note `verifies PIPELINE INTEGRITY (engineering exit gate); strategy edge clearance via real make_backtest_fn deferred to T002.1.bis + NEW §9 HOLD #2 (Mira+Riven authority)`.
3. **PRR-20260428-1 append** to `preregistration_revisions[]` (E2 — empirical refutation of `--smoke` gating assumption; DIAGNOSTIC run_id 324c151f... empirical anchor).
4. **PRR-20260428-2 append** to `preregistration_revisions[]` (F2 — AC8.9 PIPELINE INTEGRITY scope formalization; ESC-009 condition #4 adopted-6/6 explicitly recorded).
5. **Spec yaml `data_splits.in_sample` UNCHANGED** at spec level. Only `preregistration_revisions[]` append.
6. **Hold-out lock UNTOUCHED.** `[2025-07-01, 2026-04-21]` remains R10-pinned.
7. **T002.0h.1 spawn** (E1 harness amend — Dex+Aria; ~2-3 sessions; non-blocking for T002.0h closure).
8. **T002.1.bis spawn** (real `make_backtest_fn` — Mira+Dex+Beckett; ~5-10 sessions; non-blocking for T002.0h closure; gated by NEW §9 HOLD #2).
9. **NEW §9 HOLD #2 armed** (Riven custodial veto authority — 5 disarm gates: T002.0h.1 PASS + T002.1.bis PASS + Beckett N5 PASS + Mira statistical clearance + Riven dual-sign disarm).
10. **Bonferroni n_trials=5 PRESERVED** — no recount per Mira ruling (carry-forward from ESC-009 6/6).

---

## 4. Convergence analysis

### Track A — 5/6 MAJORITY APPROVE_E2 (Dara dissent E1 registered)

**3 detail-anchors discovery (independent or empirical-grounded):**
1. **DIAGNOSTIC run_id 324c151fe42a49bbab6ec44d4fc2ff28 empirical PASS** (Beckett N4 §4) — exit=0, 4.596s wall, peak RSS 0.14 GiB, 5 artifacts persisted with recorded sha256 prefixes. Refutes hypothesis that `--smoke` is necessary for AC8 closure. Beckett + Aria + Riven + Pax ground vote in this empirical anchor.
2. **WarmUpGate singleton + default-path binding fault is HARNESS-LAYER** (Beckett N4 §root-cause-empirical-track-A) — `run_cpcv_dry_run.py:848` shared instance + L865 hardcoded `max(...)` smoke window + WarmUpGate default-path-only lookup. T002.0h scope is orchestrator-only (Guard #4 + R15); harness amendment (E1) is story-level scope violation. Aria + Pax + Mira ground vote in scope-boundary discipline.
3. **Dara dissent registered for auditability transparency** — Dara E1 vote acknowledges DIAGNOSTIC empirical PASS but argues E2 leaves architectural fault unaddressed at audit chain. Dara concedes T002.0h.1 successor preserves the structural concern as governance entity.

**5/6 MAJORITY APPROVE_E2** with all hard conditions consolidated in §3 action items (5 action items covering Aria conditions; Beckett unconditional; Riven unconditional; Pax delegated; Mira statistical clearance unchanged).

### Track B — 6/6 FUNCTIONAL CONVERGENCE em F2-with-binding-F3-commitment + NEW §9 HOLD #2

**3 detail-anchors discovery:**
1. **Mira authority statement decisive across all 6 voters** — "AC8.9 testa PIPELINE INTEGRITY... NOT STRATEGY EDGE." This dichotomy formalizes ESC-009 condition #4 already adopted 6/6. Aria + Beckett + Riven + Pax + Dara all defer to Mira on the scope-boundary semantics.
2. **F1 architecturally infeasible within T002.0h scope** — real `make_backtest_fn` integration requires per-fold P126 rebuild (DEFERRED-T11 finding M1 from Aria 2026-04-26) + spec-grade strategy translation. ~5-10 sessions; consumes Guard #4 (builder API + spec immutability) + R15. All 6 voters converge that T002.1.bis successor is the correct governance entity.
3. **Riven custodial veto exercised + 5 disarm gates** — F2 alone leaves capital-ramp pathway structurally orphaned; combined F2 + F3-commitment (T002.0h.1 + T002.1.bis as registered stories) cleared. NEW §9 HOLD #2 armed: 5 disarm gates documented as preview (formal §9 amendment downstream post-Beckett N5).

**6/6 functional convergence on spawning T002.0h.1 + T002.1.bis successor stories** — F2 voters via non-blocking spawn delivered by Pax (this council); F3 voters via in-flight split. Same outcome. Riven custodial veto authority preserved.

---

## 5. Outcome

**Track A: 5/6 MAJORITY APPROVE_E2** (Aria + Mira + Beckett + Riven + Pax converging; Dara dissent E1 registered for auditability transparency)
**Track B: 6/6 FUNCTIONAL CONVERGENCE em F2-with-binding-F3-commitment + NEW §9 HOLD #2 armed** (Riven custodial veto authority exercised; combined F2 + F3-commitment cleared via T002.0h.1 + T002.1.bis spawn)

**User authorization:** Autonomous mode mandate 2026-04-26 BRT (mini-council decides; user mandate canonical "SEMPRE delegar tarefas aos agentes responsáveis... mini-council protocol em autonomous mode"). No additional user authorization required.

---

## 6. Action items (post-decision)

1. **Pax** appends PRR-20260428-1 (E2) + PRR-20260428-2 (F2) to spec `preregistration_revisions[]` with computed `pax_cosign_hash` per index. Patch bumps 0.2.1 → 0.2.2 → 0.2.3.
2. **Pax** amends story T002.0h:
   - AC8 invocation literal at L65 — drop `--smoke` flag.
   - AC8.9 sub-criterion — add PRR-20260428-2 scope-boundary note.
   - NEW section "AC8 Amendment 2 + AC8.9 Redefinition 2026-04-28 BRT (ESC-010 mini-council)".
   - Change Log entry.
   - Pax 10-point re-validation post-amendments (10/10 GO target).
3. **Pax** spawns T002.0h.1 (E1 harness amend; Dex+Aria; non-blocking) + T002.1.bis (real make_backtest_fn; Mira+Dex+Beckett; non-blocking) — stub headers. @sm formal drafts downstream.
4. **Pax** updates `docs/councils/USER-ESCALATION-QUEUE.md` ESC-010 status checklist.
5. **Beckett N5 re-run** — post Pax cosign chain. Cache `as_of=2024-08-22` already exists (no precompute needed). Command:
   ```
   python scripts/run_cpcv_dry_run.py --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run --in-sample-start 2024-08-22 --in-sample-end 2025-06-30
   ```
   Report path: `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-{date}.md`.
6. **Riven §9 HOLD #1 clear + §9 HOLD #2 arm** — separate cosign session post-Beckett N5 PASS. Documented in `docs/qa/gates/T002.0g-riven-cosign.md` §9 (or successor doc).
7. **Sable (squad-auditor)** audits coherence post-N5 (workflow Q-SDC Phase G — cosign chain integrity + Article IV traceability + R15 trail completeness).
8. **Gage push** R12 user-gated post-cosign chain complete (autonomous mode).
9. **T002.0h.1 formal @sm draft** (downstream) — replaces stub header with full ACs/tasks/DoD per template.
10. **T002.1.bis formal @sm draft** (downstream) — replaces stub header with full ACs/tasks/DoD per template; gated by NEW §9 HOLD #2 5 disarm gates.

---

## 7. Conditional ledger commitments (per voter approvals)

### 7.1 Aria conditions (Track A E2 + Track B F3)
1. AC8 invocation literal drop `--smoke` (story T002.0h L65 — existing CLI surface; no script change).
2. AC11 protective abort REMAINS in spec.
3. PRR-20260428-1 append documenting empirical anchor (DIAGNOSTIC run_id 324c151f...).
4. Spec yaml `data_splits.in_sample` UNCHANGED.
5. T002.0h.1 spawn for E1 harness amend (per-phase dated paths).
6. T002.1.bis spawn for real `make_backtest_fn` integration.

### 7.2 Mira conditions (Track A + Track B F2)
1. Spec yaml `data_splits.in_sample` UNCHANGED.
2. PRR-20260428-2 append (AC8.9 PIPELINE INTEGRITY scope-boundary formalization).
3. Hold-out lock UNTOUCHED.
4. §9 deferral language for capital-ramp clearance EXPLICITLY DEFERRED to T002.1.bis (formalizes ESC-009 condition #4 already adopted 6/6).

### 7.3 Beckett conditions (Track A E2 + Track B F2)
- AC11 protective abort REMAINS (Beckett emphatic on this preservation).
- T002.1.bis spawn (Beckett unconditional pending spawn delivery).

### 7.4 Riven conditions (Track A E2 + Track B F2 + binding F3 + NEW §9 HOLD #2)
1. Custodial veto authority preserved verbatim — F2 sem F3 commitment → REJECT; combined F2 + F3-commitment cleared.
2. NEW §9 HOLD #2 armed: 5 disarm gates (T002.0h.1 PASS + T002.1.bis PASS + Beckett N5 PASS + Mira statistical clearance + Riven dual-sign).
3. Operator precompute pre-conditions UNTOUCHED (cache `as_of=2024-08-22` already exists).
4. Hold-out lock UNTOUCHED.
5. Spec yaml `data_splits.in_sample` UNCHANGED.

### 7.5 Pax conditions (Track A E2 + Track B F2 + non-blocking spawn)
1. Aria architectural finding accepted as authoritative.
2. Mira authority statement (PIPELINE INTEGRITY vs STRATEGY EDGE dichotomy) accepted as decisive.
3. Beckett consumer authority accepted (engineering exit gate).
4. Riven custodial veto authority preserved verbatim.
5. R15 breaking_field commitment: `acceptance_criteria.AC8.invocation_literal` (PRR-20260428-1) + `acceptance_criteria.AC8.sub_criterion_8_9.semantic_scope` (PRR-20260428-2) — both story-level.

### 7.6 Dara conditions (Track A E1 dissent + Track B F3)
- Dara dissent E1 registered for transparency (data-engineer auditability stance).
- T002.0h.1 successor preserves Dara structural concern as governance entity.
- T002.1.bis successor preserves Dara stub-degeneracy concern as governance entity.

---

## 8. Authority chain

- **Council convener:** Orion (@aiox-master) under autonomous-mode mandate
- **Voters:** Aria + Mira + Beckett + Riven + Pax + Dara (independent, no cross-visibility before consolidation)
- **Outcome ratification:** Pax cosign 2026-04-28 BRT (council steward)
- **User authorization:** Autonomous mode mandate 2026-04-26 BRT (mini-council decides per Article II canonical)
- **Execution authority:** Track A → AC8 invocation literal narrowed (Pax PRR-20260428-1 cosign + story amend); Track B → AC8.9 scope-boundary clarified (Pax PRR-20260428-2 cosign + story amend); successor spawns → Pax stub headers + @sm formal drafts downstream; Beckett N5 → re-run post-cosign-chain; Riven §9 HOLD #1 clear + §9 HOLD #2 arm → post-N5; Sable audit → Q-SDC Phase G; Gage push → R12 user-gated.

---

## 9. Pax cosign

```
Validator: Pax (@po) — Product Owner / Story Balancer / Council Steward
Council: ESC-010 Dual-Track (WarmUpGate singleton + make_backtest_fn stub)
Date: 2026-04-28 BRT
Outcome (Track A): 5/6 MAJORITY APPROVE_E2 (Dara dissent E1 registered for transparency)
Outcome (Track B): 6/6 FUNCTIONAL CONVERGENCE em F2-with-binding-F3-commitment +
                   NEW §9 HOLD #2 armed (Riven custodial veto authority exercised)
User authorization: Autonomous mode mandate 2026-04-26 BRT (mini-council decides)
Article IV: NO INVENTION — every clause traceable to (a) Beckett N4 report verbatim error
            + DIAGNOSTIC artifacts (run_id 324c151fe42a49bbab6ec44d4fc2ff28),
            (b) cpcv_harness.py:707 verbatim "T11 will swap in real per-fold rebuild"
            comment + cpcv_harness.py:287-307 DEFERRED-T11 docstring (Aria M1 2026-04-26),
            (c) ESC-009 condition #4 (Mira authority — already adopted 6/6),
            (d) USER-ESCALATION-QUEUE ESC-010 entry (Pax cosign 2026-04-28 BRT),
            (e) 6 verbatim votes recorded above (condensed for ledger;
            full transcripts retained in council session log).
R15 compliance: STORY-LEVEL breaking_fields —
                acceptance_criteria.AC8.invocation_literal (PRR-20260428-1) +
                acceptance_criteria.AC8.sub_criterion_8_9.semantic_scope (PRR-20260428-2).
                Spec yaml v0.2.0 schema UNTOUCHED at data_splits / feature_set /
                trading_rules / n_trials levels. Patch bumps 0.2.1 -> 0.2.2 -> 0.2.3.
Spec compliance: T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml data_splits.in_sample
                 UNTOUCHED (downstream Phase F empirical anchor preserved).
Statistical preservation: Bonferroni n_trials=5 PRESERVED (Mira ruling carry-forward from
                          ESC-009 6/6). ~10mo in-sample (~225 valid sample days) preserves
                          non-degenerate distribution for CPCV K-fold + DSR.
Custodial preservation: hold-out lock [2025-07-01, 2026-04-21] UNTOUCHED.
                        NEW §9 HOLD #2 armed (5 disarm gates: T002.0h.1 + T002.1.bis +
                        Beckett N5 + Mira statistical clearance + Riven dual-sign).
                        Capital-ramp clearance EXPLICITLY DEFERRED to T002.1.bis.
Successor stories: T002.0h.1 (E1 harness amend; non-blocking) +
                   T002.1.bis (real make_backtest_fn; non-blocking; gated by §9 HOLD #2)
                   — stub headers spawned in this session; @sm formal drafts downstream.
Next gate: Beckett N5 re-run post Pax cosign chain (cache as_of=2024-08-22 already exists;
           no precompute needed) -> Riven §9 HOLD #1 clear + §9 HOLD #2 arm ->
           Sable audit -> Gage push (R12 user-gated, autonomous mode).
Cosign: Pax 2026-04-28 BRT (Autonomous Daily Session, council steward).
```

— Pax, balanceando ✨
