# Council 2026-04-27 — ESC-008 AC8 Clarification (Beckett N3 HALT-ESCALATE)

**Date (BRT):** 2026-04-27
**Trigger:** Beckett T11.bis #3 (N3) HALT-ESCALATE-FOR-CLARIFICATION
**Source report:** [docs/backtest/T002-beckett-t11-bis-smoke-report-N3-2026-04-27.md](../backtest/T002-beckett-t11-bis-smoke-report-N3-2026-04-27.md)
**Council convener:** Orion (@aiox-master)
**Council size:** 5 voters (Aria + Mira + Beckett + Riven + Pax)
**Protocol:** Independent vote, no cross-visibility before consolidation
**Outcome:** **4/5 MAJORITY APPROVE_D1**, 1/5 APPROVE_D3 (Beckett conditional dissent — personal preference declared D1)
**User authorization:** **APPROVED D1** — 2026-04-27 BRT (explicit "autorizo" in response to Orion 🅰️ recommendation)

---

## 1. Context

Beckett T11.bis #3 (N3 iteration) executed AC8 exit gate per execution plan 2026-04-27. Result matrix:

- **Step A (warmup cache hit):** PASS 4/4 sub-criteria (AC8.1–AC8.4). Wall-time 0.335s; peak RSS 24.74 MB.
- **Step C (CPCV full phase via `run_cpcv_dry_run.py --smoke --in-sample-end 2025-06-30`):** exit code **1** — full phase aborts at `warmup_or_pipeline: warmup not satisfied for 2024-07-01`. Smoke phase emitted `smoke_complete` cleanly; full phase fails because warmup state for `as_of=2024-07-01` is missing on disk (only `2025-05-31` present per AC9 cache contract).

**AC8 verdict matrix N3:**
- AC8.5 strict literal (script `exit_code == 0`): **FAIL** (exit=1)
- AC8.5 semantic (smoke phase succeeded, 5 artifacts persisted, KillDecision verdict valid): **PASS** (smoke phase ran to `smoke_complete`; full phase failure independent)
- 8/9 sub-criteria PASS by execution-plan §4.1 PARTIAL_PASS rule (≥8/9 with 1 cosmetic discrepancy ⇒ PARTIAL_PASS).

Beckett honored Anti-Article-IV Guards #1–7 (no subsample, no engine config edit, no improvise threshold relaxation, no retry, no push, no story file edits, plus Guard #8 no AC11 abort bypass) AND escalated rather than precompute `as_of=2024-07-01` without explicit authorization (avoid Article-IV-A "retry until green" violation).

**3 mitigation paths surfaced (Beckett report §11):**
- **(D1) Operator authorizes precompute** of warmup state for `as_of=2024-07-01` per AC9 cache contract + ESC-006 run-once-per-as_of principle (~5–7min cost). After cache populated, AC8 exit gate re-runs cleanly because both warmups (2024-07-01 + 2025-05-31) present. ZERO spec change, ZERO precedent damage.
- **(D2) AC8 spec amendment** — change literal command to `--smoke --no-full` (or equivalent), declaring full phase OUT OF SCOPE for AC8 per ESC-006 reframe. R15 evaluation required (story Done? AC8 invocation literal modified).
- **(D3) AC8 declared PASS on semantic reading** (8/9 PASS + 1 cosmetic discrepancy via execution-plan §4.1 PARTIAL_PASS rule). Beckett moves on without precompute or spec change.

---

## 2. Votes (condensed for ledger; full verbatim transcripts retained in council session log)

### 2.1 Aria voto (@architect — APPROVE_D1)

**Verdict:** APPROVE_D1 (conditional, 5 conditions)
**Personal preference declared:** D1

**Top rationale (3 points):**
1. **AC8 invocation is internally coherent** — it instructs `python scripts/run_cpcv_dry_run.py --spec ... --dry-run --smoke --in-sample-end 2025-06-30`; the literal command exits 0 only when both smoke AND full phases succeed. The gap is operator-setup (warmup precompute for `as_of=2024-07-01` not yet populated), NOT a spec defect. AC9 cache contract was DESIGNED for this case: precompute second as_of cache once, then full pipeline reaches exit 0.
2. **D2 forces an R15 amendment** to a Done-adjacent story for what is purely an operational gap; that's overkill and corrodes the story's append-only stability invariant.
3. **D3 corrodes binary-verifiability of AC8** — declaring "8/9 PASS + cosmetic" sets a semantic-drift precedent inconsistent with Riven's §9 HOLD #1 strict-literal stance; once "cosmetic exit codes" become acceptable, the gate erodes for future iterations.

**5 Conditional approvals (D1 path):**
1. Operator-initiated precompute MUST be logged in `cache_audit.jsonl` as `status:"miss"` then `status:"write"` markers (AC9 audit log invariant).
2. `determinism_stamp.json` `[TO-VERIFY]` tags (`cost_atlas_sha`, `rollover_calendar_sha`) entered into follow-up backlog.
3. Full-phase wall-time captured empirically post-precompute for ESC-009 contingency (D2-narrow if > 5min observed).
4. Riven §9 amendment authority preserved post-N4 PASS (Riven retains §9 cosign veto).
5. Anti-Article-IV Guard #5 honored — operator setup completion is NOT a "retry"; explicit authorization sequence required (Operator → precompute → Beckett N4).

**Boundary preserved:** spec `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` UNTOUCHED; story T002.0h AC8 invocation literal UNTOUCHED.

**Signature:** Aria 2026-04-27 BRT.

---

### 2.2 Mira voto (@ml-researcher — APPROVE_D1 unconditional)

**Verdict:** APPROVE_D1 (unconditional in path; conditional fallback ESC-009 D2-narrow if N4 reveal full > 5min)
**Personal preference declared:** D1

**Top rationale (3 points):**
1. **Smoke 22d synthetic K1/K2/K3 are degenerate-by-design** — they exist to validate harness wiring, NOT statistical power. Bonferroni n_trials=5 + Deflated Sharpe operate on the distribution OVER 5 splits (CPCV K-fold over 12-month in-sample), and that distribution is mathematically degenerate when only smoke phase runs. Only the FULL 12-month CPCV phase produces a non-degenerate distribution to which Bonferroni + DSR can be applied.
2. **D3 = statistical malpractice** — declaring AC8 PASS on smoke-only readings effectively claims statistical clearance from a degenerate distribution. That sets up Phase F to ramp capital based on a stat-test that was never actually exercised. Anti-leak invariants are about WHICH data the gate sees; degenerate-distribution invariants are about WHETHER the gate is mathematically meaningful. Both must hold.
3. **D1 is the only path that empirically exercises the test surface** Riven §9 HOLD #1 was designed around. ESC-006 mini-council 4/4 APPROVE_F established the principle (cache contract is run-once-per-as_of, not retry-on-green). D1 honors that principle.

**Fallback condition (ESC-009 D2-narrow if N4 wall-time > 5min):** Mira open to a narrow D2 amendment ONLY if N4 empirical wall-time on full phase exceeds 5min budget materially; that's a separate decision with empirical data, not a hypothetical.

**Signature:** Mira 2026-04-27 BRT.

---

### 2.3 Beckett voto (@backtester — APPROVE_D3 conditional, dissent registered; personal preference D1)

**Verdict:** APPROVE_D3 (conditional, 4 cosign acknowledgments — degrades to D1 if any unmet)
**Personal preference declared:** D1 ("Voto D3 sobrepõe minha preference D1")

**Top rationale (Beckett's reasoning for voting AGAINST own preference):**
1. **8/9 PASS already covers AC8 reframed exit gate per ESC-006 mini-council 4/4 APPROVE_F.** AC8.5 semantic (smoke phase exit=0, all 5 artifacts persisted, KillDecision valid) is what ESC-006 reframed AC8 to actually mean. Strict-literal exit code is a holdover from pre-reframe AC8.
2. **D1 risks re-escalation** — if N4 full wall-time > 5min, ESC-009 D2-narrow needed; if cache validation fails with a subtle bug, ESC-010 needed. D3 closes the loop NOW with available empirical evidence.
3. **Dissent transparency:** Beckett's preferred personal verdict is D1 (cleanest, no precedent risk). Voting D3 because conditional cosign acknowledgments (4 of them — all related to PARTIAL_PASS rule scope, semantic reframe legitimacy, smoke-phase sufficiency, and full-phase decoupling from AC8) appear strong on paper. **Beckett explicitly notes: if D1 path is chosen, all 4 D3 cosign acknowledgments DO NOT apply (they were reasoning artifacts for D3, not D1 blockers). Dissent registered for transparency only.**

**4 Conditional cosign acknowledgments for D3** (paraphrased; each must hold for D3 to remain Beckett's vote):
1. Execution-plan §4.1 PARTIAL_PASS rule covers exit-code-1 cosmetic discrepancy when smoke phase succeeds.
2. ESC-006 reframe legitimately decouples full-phase AC8 scope.
3. Smoke phase 5 artifacts + valid KillDecision verdict = sufficient empirical clearance for Riven §9 HOLD #1.
4. No statistical malpractice concern overrides PARTIAL_PASS in semantic reading.

**Signature:** Beckett 2026-04-27 BRT (with explicit note that D1 is personal-preference; D3 is conditional vote that degrades cleanly).

---

### 2.4 Riven voto (@risk-manager — APPROVE_D1)

**Verdict:** APPROVE_D1 (conditional, 3 conditions)
**Personal preference declared:** D1

**Top rationale (3 points):**
1. **§9 HOLD #1 strict only clears with full empirical pipeline exit 0.** The §9 amendment language preview Riven holds in reserve REQUIRES `FullReport.KillDecision.verdict ∈ {GO, NO_GO}` from the FULL CPCV phase, not the smoke phase alone. D3 short-circuits that requirement and would force Riven to either (a) waive §9 HOLD #1 (custodially unacceptable), or (b) draft a narrower §9 amendment that creates a precedent gap. D1 clears HOLD #1 cleanly with full empirical pipeline.
2. **Phase F is the last gate before capital ramp.** Custodial discipline at this stage demands strict empirical proof, not semantic reframes. ESC-006 already had to walk back the wall-time threshold; allowing another semantic concession on AC8 exit code creates compounding drift.
3. **D3 is custodially inaceptable** — once "cosmetic exit code" is precedent, the kill-switch infrastructure (which fires on exit codes + structured KillDecision parsing) loses its binary verifiability. Riven cannot custodially endorse a path that erodes binary gate verification.

**3 Conditional approvals (D1 path):**
1. Operator authorizes precompute as ESC-006-contract-completion (NOT a retry — explicit authorization per Anti-Article-IV Guard #5).
2. Beckett N4 captures full-pipeline RSS profile (peak RSS < 6 GiB, ADR-1 v3 CAP_v3 8.4 GiB compliance preserved).
3. Fallback D2 (narrow) ONLY if D1 empirically infeasible (e.g., N4 full wall-time > 5min observed and empirically irreducible — not hypothetical).

**§9 amendment language preview (Riven reserves authority):** "HOLD #1 cleared 2026-04-27 BRT post-Beckett T11.bis #3 N4 PASS. Empirical evidence: full CPCV pipeline exit 0; FullReport.KillDecision.verdict ∈ {GO, NO_GO}; peak RSS < 6 GiB; warmup state cache validation triple-key strict (AC9 contract). Phase F unblocked subject to capital-ramp protocol RA-XXXXXXXX-X."

**Signature:** Riven 2026-04-27 BRT.

---

### 2.5 Pax voto (@po — APPROVE_D1 unconditional)

**Verdict:** APPROVE_D1 (unconditional)
**Personal preference declared:** D1

**Top rationale (3 points):**
1. **ESC-006 established the principle (not a one-off).** ESC-006 mini-council 4/4 APPROVE_F reframed warmup wall-time as run-once-per-as_of accepted cost. That principle is universal across all `as_of_date` precomputes — it does not stop at 2025-05-31. Applying it to 2024-07-01 is the SAME contract, not a new exception. D2 would create a one-off carve-out (full phase scope for AC8); D3 would create a one-off carve-out (cosmetic exit code rule). Both fragment the principle. D1 honors it cleanly.
2. **D1 = zero cosign load + zero spec change + zero precedent damage.** Pax authority sources: (a) ESC-006 mini-council 4/4 APPROVE_F (council ledger 2026-04-26), (b) AC9 cache contract (story T002.0h L73-78 DONE), (c) Beckett N3 report §11 escalation matrix (operator-initiated precompute = cleanest path), (d) Anti-Article-IV Guard #5 (operator setup completion is NOT a retry). All four authority sources align on D1.
3. **No spec or story file modifications required.** R15 NO breaking_fields; T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml UNTOUCHED; T002.0h story AC8 invocation literal UNTOUCHED. Only Change Log entry (append-only, allowed for any agent per story-lifecycle.md).

**Authority sources cross-check:**
- ESC-006 council ledger (2026-04-26): run-once-per-as_of principle ESTABLISHED.
- AC9 cache contract (T002.0h L73–78): triple-key cache validation + `--force-rebuild` flag DONE.
- Beckett N3 report §11.3 mitigation matrix: D1 = explicit recommended path.
- Anti-Article-IV Guards #1–5 (story T002.0h): NÃO retry, NÃO improvise — Operator-initiated setup is explicit per ESC-006 reframe (run-once-per-as_of).

**Signature:** Pax 2026-04-27 BRT (Autonomous Daily Session, council steward authority).

---

## 3. Vote consolidation

| Voter | Verdict | Hard/Conditional | Personal-preference (declared) |
|---|---|---|---|
| Aria | D1 | conditional (5 conditions) | D1 |
| Mira | D1 | unconditional (fallback ESC-009 D2-narrow if N4 wall-time > 5min) | D1 |
| Beckett | D3 | conditional (4 cosign acknowledgments; degrades to D1 if any unmet) | D1 (declared) |
| Riven | D1 | conditional (3 conditions) | D1 |
| Pax | D1 | unconditional | D1 |

**Effective verdict tally:**
- **D1 hard support:** 4/5 (Aria + Mira + Riven + Pax)
- **D1 personal-preference declared:** 5/5 (all voters including Beckett)
- **D3 hard support:** 1/5 (Beckett conditional, dissent acknowledged in own vote)

---

## 4. Convergence analysis

3 points reached independently by all 4 D1 voters:

1. **AC9 cache contract was designed for D1.** Precomputing a second `as_of` is the canonical use case of the triple-key cache + `--force-rebuild` escape hatch + `cache_audit.jsonl` write/hit/miss markers. ESC-006 mini-council 4/4 APPROVE_F established this contract; D1 invokes it.
2. **Smoke 22d synthetic does NOT substitute full 252d real** — Mira (statistical authority: distribution-over-folds non-degenerate ONLY in full CPCV) + Riven (custodial authority: §9 HOLD #1 strict literal exit 0) + Aria (architectural authority: AC8 invocation internally coherent, gap is operator-setup). Three independent authority lenses converge on the same conclusion.
3. **D3 creates a dangerous precedent** — semantic drift from PARTIAL_PASS clause to "cosmetic exit code accepted" erodes binary-verifiability of every future AC gate; once accepted as precedent, future gates become litigation rather than measurement.

**Beckett dissent is functionally D1:** Beckett's declared personal-preference is D1; D3 vote is conditional on 4 cosign acknowledgments that are themselves D3-path-specific (do not apply if D1 is chosen). In effective vote-counting terms, this is a 5/5 personal-preference convergence on D1 with one voter casting a transparency-dissent on the D3 path's procedural legitimacy. Council outcome stands at 4/5 MAJORITY APPROVE_D1.

---

## 5. Outcome

**APPROVE_D1** — 4/5 MAJORITY accepted per council protocol (5/5 CONVERGENT preferred, ≥4/5 MAJORITY acceptable per autonomous-mode council standard).

**User authorization 2026-04-27 BRT:** explicitly approved D1 path execution ("autorizo" in response to Orion 🅰️ recommendation summary).

---

## 6. Action items (post-decision)

1. **Operator** authorizes precompute via:
   ```
   python scripts/run_warmup_state.py --as-of-dates 2024-07-01 --output-dir state/T002/
   ```
   Estimated cost ~5–7min (cache miss per ESC-006 contract). `cache_audit.jsonl` will record `status:"miss"` then `status:"write"` markers per AC9 invariant.
2. **Beckett** executes T11.bis N4 re-run with warmup state complete (2024-07-01 + 2025-05-31 cached). Report path: `docs/backtest/T002-beckett-t11-bis-smoke-report-N4-{date}.md`. Full pipeline RSS profile captured per Riven condition #2.
3. **Riven §9 amendment** post-N4 PASS, language preview already in §2.4 above. HOLD #1 clearance documented in `docs/qa/gates/T002.0g-riven-cosign.md` §9.
4. **Pax** updates T002.0h story Change Log + status post-N4 (Status header from "Ready for Dex (cache validation contract impl)" → "Ready for Riven §9 cosign post-N4 PASS" or final "Done" pending QA gate).
5. **Sable (squad-auditor)** audits coherence post-N4 (workflow Q-SDC Phase G — cosign chain integrity + Article IV traceability).
6. **Gage push** R12 user-gated post-cosign chain complete.

---

## 7. Conditional ledger commitments (per voter approvals)

### 7.1 Aria conditions (D1)
1. `cache_audit.jsonl` operator-initiated precompute markers (status:"miss" → status:"write" sequence).
2. `determinism_stamp.json` `[TO-VERIFY]` tags follow-up backlog (`cost_atlas_sha`, `rollover_calendar_sha`).
3. Full-phase wall-time empirical capture in N4 report.
4. Riven §9 amendment authority preserved post-N4 PASS.
5. Anti-Article-IV Guard #5 honored — NO retry; operator-initiated setup completion is the explicit authorization gate.

### 7.2 Mira conditions (D1 unconditional, fallback D2-narrow if N4 wall-time > 5min)
- Mini-council ESC-009 D2-narrow ONLY if N4 empirical full wall-time > 5min materially (with empirical data, not hypothetical).

### 7.3 Riven conditions (D1)
1. Operator authorizes precompute as ESC-006-contract-completion (not retry).
2. Beckett N4 captures full-pipeline RSS profile (peak RSS < 6 GiB target).
3. Fallback D2 applies only if D1 empirically infeasible.

### 7.4 Beckett conditions (dissent D3 — registered but D1 path executes)
- Beckett's 4 cosign acknowledgments for D3 do NOT apply on D1 path (they were D3-path reasoning artifacts). Dissent registered for transparency only.

---

## 8. Authority chain

- **Council convener:** Orion (@aiox-master)
- **Voters:** Aria + Mira + Beckett + Riven + Pax (independent, no cross-visibility)
- **Outcome ratification:** Pax cosign 2026-04-27 BRT (council steward)
- **User authorization:** explicit 2026-04-27 BRT
- **Execution authority:** D1 path → Operator (precompute) → Beckett (N4) → Riven (§9) → Pax (close) → Gage (push gated)

---

## 9. Pax cosign

```
Validator: Pax (@po) — Product Owner / Story Balancer / Council Steward
Council: ESC-008 AC8 Clarification
Date: 2026-04-27 BRT
Outcome: 4/5 MAJORITY APPROVE_D1
User authorization: GRANTED 2026-04-27 BRT
Article IV: NO INVENTION — every clause traceable to (a) Beckett N3 report,
            (b) ESC-006 mini-council 4/4 APPROVE_F, (c) AC9 cache contract,
            (d) 5 verbatim votes recorded above (condensed for ledger;
            full transcripts retained in council session log).
R15 compliance: NO breaking_fields — D1 honors AC8 invocation literal
                + ESC-006 reframe principle without spec amendment.
Spec compliance: T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml UNTOUCHED.
Next gate: Operator precompute as_of=2024-07-01 (~6min) → Beckett N4.
Cosign: Pax 2026-04-27 BRT (Autonomous Daily Session, user-authorized D1).
```

— Pax, balanceando ✨
