---
council_id: IMPL-2026-05-01-SQUAD-INSTRUMENTATION
topic: Implementation Council — squad instrumentation & process discipline post T002 retire (Round 3.1 costed_out_edge_oos_confirmed_K3_passed)
voter: River (@sm)
voter_role: Scrum Master — Story creation authority + multi-handoff sign-off chain orchestration + Q-SDC workflow rounds discipline + closure-phase Literal completeness custodial
date_brt: 2026-05-01
voter_authority: |
  AIOX agent authority matrix @sm exclusive — `*draft` / `*create-story` from epic/PRD;
  story template selection; multi-handoff sign-off chain composition (T0a..T0e..T0f pattern);
  Q-SDC workflow rounds discipline (Round 1 / Round 2 / Round 3 / Round 3.1 cadence);
  closure-phase Literal completeness custodial (post N8.1 INCONCLUSIVE bug lesson);
  PRR pre-committed disposition rule integration into story scaffolding (post PRR-20260430-1 lesson).
mandate: |
  PROCESS-PERIMETER adjudication of squad-instrumentation amendments needed post-T002. Vote
  independent — no peer ballots consulted pre-vote per council protocol. T002 surfaced multiple
  process-discipline gaps across 4 Q-SDC iterations (Round 1 wiring gap, Round 2 costed-out IS,
  Round 3 INCONCLUSIVE protocol-compliance gap, Round 3.1 final FAIL costed_out_edge_oos_confirmed_K3_passed).
  River vote concerns ONLY: (a) story drafting protocol amendments — multi-handoff sign-off chain
  T0a..T0e..T0f pattern; (b) spec-first protocol amendments — AC binary-verifiable + caller-wiring
  task explicit + wiring validation test; (c) Q-SDC rounds discipline — pre-committed disposition rule
  + verdict-vs-reason contract test + closure Literal completeness check; (d) story scope discipline
  forward H_next; (e) personal preference disclosure; (f) Article IV self-audit.
inputs_consulted:
  - docs/stories/T002.7.story.md (clean closure pattern)
  - docs/stories/T002.6.story.md (4-sign-off chain T0a-T0e + multi-iteration absorption)
  - docs/stories/T002.0a.story.md..T002.0h.1.story.md (T0-series wave story scaffolding)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md (Round 3.1 final verdict)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Round 3 INCONCLUSIVE protocol gap)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md (Round 2 costed-out)
  - docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md (Round 1 wiring gap closure)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md (Round 2 → Phase G authorization)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md (Round 3 protocol-compliance gap closure + R18-R20 NEW)
  - docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md (pre-committed 4-branch disposition rule pattern)
inputs_NOT_consulted_pre_vote: peer voter ballots (Aria / Pax / Quinn / Sable / Mira / Riven IMPL 2026-05-01 votes)
verdict_summary: |
  §1: Story drafting — preserve T002.6 → T002.7 successor close-pattern (append-only supersede;
  Done with status_transition trail). Multi-handoff 4-sign-off chain T0a-T0e was effective at
  spec-finalize gate but INCOMPLETE — F2-T9-OBS-1 surfaced caller-wiring task as IMPLICIT,
  triggering Round 3 INCONCLUSIVE_phase_g_protocol_compliance_gap. RIVER MANDATE: NEW T0f
  caller-wiring sign-off row binding for any story whose Mira spec §15.x sign-off chain enumerates
  a wiring task. T0f gates Dex T1 begin alongside T0a-T0e.
  §2: Spec-first protocol — three amendments. (i) AC binary-verifiable enforcement: every AC MUST
  reduce to one-of {PASS, FAIL, INCONCLUSIVE} or analogous Literal — Sable F-01 retroactive concern
  carried forward; (ii) caller wiring task EXPLICIT in sign-off chain (Aria F2-T9-OBS-1
  carry-forward) — no IMPLICIT-deferred-to-impl rows allowed; (iii) wiring validation test —
  extend Quinn QA Check 8 to a NEW Check 9 wiring-protocol-conformance test (e.g., R20 contract
  test pattern: verdict-vs-reason invariant + ic_holdout_status='computed' propagation).
  §3: Q-SDC rounds discipline — three lessons binding for H_next. (i) Pre-committed disposition
  rule (PRR-20260430-1 pattern) authored at Round 1 (Mira spec finalize T0a output), NOT at
  Round 3 retroactively; (ii) verdict-vs-reason contract test (post Round 3 lesson; ESC-013 R20
  carry-forward); (iii) closure-phase Literal completeness check (post N8.1 INCONCLUSIVE bug
  — verdict.reasons array MUST be either empty OR contain computed numbers, never sentinel
  strings).
  §4: Story scope discipline H_next — RIVER PREFERENCE: single-iteration discipline (1 Round
  budget) PRIMARY for H_next given fresh virgin tape lock + pre-committed disposition rule
  upfront. ALLOW multi-round budget upfront ONLY IF complexity score ≥ 16 (COMPLEX class per
  Spec Pipeline) AND Aria + Mira + Riven jointly sign multi-round authorization at Round 1
  spec-finalize.
  §5: Personal preference — single-iteration discipline + T0f caller-wiring binding + AC
  binary-verifiable enforcement; (multi-round budget upfront) DEFERRED to council case-by-case.
  §6: Article IV self-audit verbatim.
  §7: River cosign 2026-05-01 BRT.
---

# IMPL 2026-05-01 — Squad Instrumentation River Vote (Process Perimeter Adjudication)

> **Voter:** River (@sm) — Scrum Master & Story-Drafting Authority.
> **Authority basis:** AIOX agent authority matrix @sm exclusive (`*draft` / `*create-story`); story template selection; multi-handoff sign-off chain composition (T0a..T0e..T0f pattern); Q-SDC workflow rounds discipline; closure-phase Literal completeness custodial.
> **Mandate:** Adjudicate squad-instrumentation amendments from PROCESS PERIMETER perspective only. Aria retains architecture authority; Mira retains spec authority; Pax retains scope authority; Quinn retains QA authority; Sable retains process audit authority; Riven retains risk-perimeter authority. River's vote concerns ONLY (a) story drafting protocol amendments; (b) spec-first protocol amendments at the story-template layer; (c) Q-SDC rounds discipline; (d) story scope discipline forward H_next; (e) personal preference; (f) Article IV self-audit.

---

## §1 Story drafting improvements

### §1.1 T002.6 → T002.7 successor close-pattern (PRESERVE verbatim)

The T002.6 → T002.7 transition is exemplary. T002.6 was set Done by Pax 2026-05-01 BRT WITH `status_transition: superseded by T002.7` trail in the story frontmatter and a Change Log entry pointing to the successor. T002.7 was authored by Pax as the closing story for the same epic with explicit `verdict_inherited` provenance back to Mira F2-T9.1. The pattern is **append-only supersede** — no T002.6 mutation, no retroactive AC editing, no narrative re-writing; the old story becomes a sealed artifact and the successor inherits the verdict trail.

**Mandate carry-forward for H_next and beyond:** Whenever a story's verdict cycle is interrupted by a council resolution that prescribes a successor story (e.g., ESC-013 §5(c) prescribed Pax T002.7 close), the successor story MUST be authored as a NEW story file (not as an in-place re-write), MUST carry `inherits:` / `supersedes:` frontmatter pointing back to the predecessor, and MUST close the predecessor story with `Done` status + Change Log entry naming the successor + verdict provenance trail. This pattern preserves the audit trail integrity that Sable depends on for process audits and that Article IV requires for "every clause traces" discipline.

**No amendment needed; pattern is canonical.**

### §1.2 Multi-handoff 4-sign-off chain T0a-T0e effectiveness assessment

The T002.6 sign-off chain was:

| Row | Owner | Task | Effective? |
|---|---|---|---|
| **T0a** | Mira | Spec finalize (8 dimensions) | YES — spec landed; thresholds locked; protocol authored |
| **T0b** | Aria | Archi review (real-tape harness preservation) | YES — T002.1.bis factory pattern preserved; per-fold P126 D-1 invariant honored |
| **T0c** | Beckett | Consumer sign-off (run targets achievable; cost atlas integration testable) | YES — N7-prime executed cleanly under ADR-1 v3 RSS budget |
| **T0d** | Riven | Cost-atlas wiring + Gate 5 fence preservation | YES — atlas SHA `bbe1ddf7…` consumed; Gate 5 fence held through Round 3.1 |
| **T0e** | Pax | 10-point validate-story-draft Mira spec finalize | YES — story status Draft → Ready transition clean |

**Effectiveness verdict:** The 4-sign-off chain at the spec-finalize gate was **EFFECTIVE for the spec authoring layer**. Round 1 entered Beckett N6 with Mira spec v1.0.0 + 4 sign-offs registered + Quinn QA gate pre-cleared; the spec body itself was sound.

**Where the chain FAILED:** The chain enumerated spec-authoring sign-offs but did NOT enumerate **caller-wiring sign-off** as a standalone row. F2-T9-OBS-1 admission (Sable §3 ESC-013 resolution) acknowledged that R5 audit scope collapsed Dex F2-T8-T1 (caller wiring) into the R8 envelope, leaving the wiring task IMPLICIT. The signature was: Mira spec §15.13 Phase G OOS Unlock Protocol authored cleanly with sign-offs T0a-T0e PASS → Beckett N8 launched with the assumption that the caller would honor `--phase G` semantics → caller hardcoded `holdout_locked=True` survived to runtime → N8 produced PHASE-F-PROTOCOL over PHASE-G-WINDOW artifact → Mira F2-T9 Round 3 INCONCLUSIVE_phase_g_protocol_compliance_gap.

The diagnostic is: the sign-off chain was **necessary but insufficient**. Spec-authoring sign-offs do not provide coverage of the caller-side bridge between spec and runtime. The bridge task (caller wiring) was IMPLICITLY assumed PRE-condition for impl T1 begin but was not registered as an explicit gating row.

### §1.3 RIVER MANDATE: NEW T0f caller-wiring sign-off row

**Proposal:** For any future story whose Mira spec §15.x sign-off chain (or analogous spec-§ enumeration) enumerates a wiring task — i.e., any task whose owner is `@dev` and whose deliverable is "caller wiring", "argparse extension", "CLI flag plumbing", "config propagation", "factory injection point", "phase-conditional flag toggle", or any analogous predecessor-of-T1-impl bridge task — that task MUST be registered as a NEW T0f sign-off row in the story header gating Dex T1 begin alongside T0a-T0e.

**T0f row template:**

```
T0f — Dex (or designated wiring agent): caller-wiring sign-off
  Deliverable: explicit caller-side change list (file paths + LoC range +
    phase-conditional logic semantics + test additions); attach pre-impl
    branch sketch reviewed by Aria (cross-check architecture cost) and Quinn
    (cross-check test additions cover the phase-conditional path).
  Pass criteria: (a) explicit file:line target enumerated in spec §15.x
    sign-off chain; (b) phase-conditional logic semantic encoded in spec
    body (not just "holdout_locked=False during Phase G"); (c) NEW
    test_<phase>_unlock_protocol regression guard authored pre-Beckett-run
    invocation; (d) verdict-vs-reason contract test (R20 pattern) added to
    QA Check 8 (or NEW Check 9).
  Gate: blocks Dex T1 begin if T0f sign-off not registered (alongside
    T0a-T0e gating).
```

**Trade-off acknowledgment:** T0f adds a sixth sign-off row. River's process-discipline cost-benefit analysis: T0f sign-off cost ≈ 30-45 min Dex authoring + 15-20 min Aria + Quinn cross-check ≈ 1 squad session total ≈ EXACTLY the cost ESC-013 estimated for the F2-T9-OBS-1 corrective wiring fix (~5-10 LoC + 30-50 LoC tests). The cost is paid upfront in spec-finalize phase OR retroactively in INCONCLUSIVE protocol-gap phase; upfront is strictly cheaper because it does not require a second Beckett ~3h re-run on the OOS budget (which is an irreplaceable resource per Anti-Article-IV Guard #3).

**Effectiveness ratification:** T0a-T0e was effective for Round 1 spec-authoring but failed to prevent Round 3 protocol gap. T0a-T0f (with NEW T0f) is the lessons-learned absorption of F2-T9-OBS-1 admission. Adopt as canonical for H_next and beyond.

---

## §2 Spec-first protocol amendments

Three amendments to the spec-first protocol at the story-template layer. All three derive from specific T002 lessons; each has source provenance.

### §2.1 AC binary-verifiable enforcement (Sable F-01 retroactive concern)

**Source:** Sable F-01 carry-forward (ESC-012 R14 + ESC-013 verbatim — Quinn QA Check 8 NEW Sable F-01 procedural fix retained).

**Mandate:** Every AC in a story MUST reduce to one-of `{PASS, FAIL, INCONCLUSIVE}` or analogous Literal partition. NO open-ended ACs ("the spec is well-authored", "the harness is robust", "documentation is complete"). Every AC MUST have an explicit binary-verifiable closure check authored at Mira T0a finalize phase.

**Pattern carry-forward from T002.7:** AC1..AC12 in T002.7 §3 each reduces to a binary-verifiable check with named evidence artifact. AC8 explicitly emits `{PASS, FAIL, INCONCLUSIVE}` per Mira spec §9 verdict label discipline; AC9 sample-size floor reduces to `events_metadata.n_events ≥ floor` numeric check; etc. THIS IS THE TARGET PATTERN for all H_next stories.

**Story-template enforcement:** River authoring discipline — every AC drafted MUST include an "Evidence artifact" pointer + a "Binary-verifiable closure check" sub-clause naming the file/line or computed metric or Literal value the AC resolves to. AC drafted without binary-verifiable closure are RETURNED to author (River own custodial discipline) before Mira spec finalize T0a.

### §2.2 Caller wiring task EXPLICIT in sign-off chain (Aria F2-T9-OBS-1 carry-forward)

**Source:** Aria F2-T9-OBS-1 carry-forward (ESC-013 §3 admission + §6 corrective action).

**Mandate:** No IMPLICIT-deferred-to-impl sign-off chain rows allowed. Every Mira spec §15.x sign-off chain enumeration MUST explicitly list every caller-wiring task as a separate row with explicit owner + deliverable + LoC estimate + test additions. The Sable corrective-action language ("Future Sable pre-run coherence audits MUST enumerate spec §15.x sign-off chain rows alongside ESC §4 R-conditions, mapping each chain row to 'explicitly verified' OR 'implicit-deferred-to-impl' status") binds at the SABLE audit layer — but RIVER process discipline binds at the STORY DRAFTING layer one step earlier: NO row may be drafted as "implicit-deferred-to-impl" in the FIRST place.

**Story-template enforcement:** River authoring discipline — every sign-off chain row in a story header (T0a..T0f) MUST have:
- Owner (named agent)
- Deliverable (concrete artifact with file path or commit pointer)
- LoC estimate or sub-task estimate
- Pass criteria (binary-verifiable)
- Gate semantics (what subsequent task is blocked until sign-off)
- Test additions (regression guard for the wiring; coupled to QA Check 8 / Check 9)

Rows missing any of these six fields are RETURNED to author before story Status `Draft → Ready` transition.

### §2.3 Wiring validation test (extend Quinn QA Check 8)

**Source:** ESC-013 R20 NEW (verdict-vs-reason contract test regression guard) + Quinn QA Check 8 carry-forward.

**Mandate:** Quinn QA gate currently has 8 standard checks (per AIOX `qa-gate.md` task). For stories whose sign-off chain enumerates a caller-wiring task (i.e., stories with a T0f row per §1.3), Quinn QA Check 8 expands to include a wiring-protocol-conformance test, OR a NEW Check 9 is added for the same purpose.

**Pattern from ESC-013 R20:** "Verdict-vs-reason contract test: K3 PASS reason text MUST contain computed numbers (`IC_holdout=X.XX > 0.5 × IC_in_sample=Y.YY`), NOT sentinel strings ('DEFERRED' forbidden when status='computed'). Regression guard prevents future protocol gaps."

The R20 contract test is a specific instance of a more general pattern: **wiring-protocol-conformance test verifies that runtime artifacts emitted from the wiring path conform to the spec-declared semantic of that path**. For Phase G OOS unlock, the spec-declared semantic was `ic_holdout_status='computed'` (not 'deferred') and `verdict.reasons=[]` (or computed-numbers, not sentinel strings). The R20 test asserts both invariants.

**Generalization carry-forward for H_next:** Whenever a story's sign-off chain enumerates a caller-wiring task at T0f, the QA gate (Check 8 expansion or Check 9 NEW) MUST include a regression test that verifies the runtime artifact conforms to spec-declared semantic at the wiring boundary. River does not pre-empt Quinn QA authority on test design; River mandates that the test BE AUTHORED as a sign-off chain T0f deliverable.

**Story-template enforcement:** T0f row Pass criteria sub-clause (d) per §1.3 already requires R20-pattern test. River discipline — no T0f row PASSES without the regression test artifact registered as a deliverable.

---

## §3 Q-SDC workflow rounds discipline

T002 needed Round 1 + Round 2 + Round 3 + Round 3.1 — four iterations for a single epic. River process-perimeter assessment of each iteration's contribution + lessons:

| Round | Iteration trigger | Lesson absorbed |
|---|---|---|
| **Round 1** | F2 IS Beckett N6 produced IC=0 + CI95=[0,0] (wiring gap signature) | T002.0g harness wiring landed; bucket A `engineering_wiring` post-mortem entry |
| **Round 2** | F2 IS Beckett N7-prime produced IC=0.866 + DSR=0.767 strict FAIL + hit_rate=0.497 inconsistent with leakage | bucket B `costed_out_edge` (provisional pending Phase G OOS) |
| **Round 3** | Phase G N8 produced INCONCLUSIVE_phase_g_protocol_compliance_gap (PHASE-F-PROTOCOL over PHASE-G-WINDOW artifact) | F2-T9-OBS-1 admission; R18-R19-R20 NEW conditions; T0f wiring row mandate (§1.3 above) |
| **Round 3.1** | Phase G N8.2 PROPER unlock produced GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed | Final disposition; T002 retire ceremony; T002.7 close |

Three discipline lessons emerge.

### §3.1 Pre-committed disposition rule (PRR-20260430-1 pattern) earlier

**Lesson:** PRR-20260430-1 was authored 2026-04-30 — i.e., AFTER Round 1 (wiring gap) AND AFTER Round 2 (costed-out IS), at the threshold of Phase G N8 launch. The PRR enumerated 4 explicit branches covering the full outcome partition with each branch's disposition action pre-committed. The PRR was effective at preventing Round 3 outcome-based threshold reinterpretation: when N8.2 produced K1 strict FAIL OOS + K3 PASS, the disposition was already hash-frozen as `T002 retire with refined diagnostic`.

**Diagnostic:** Had a PRR-style 4-branch disposition rule been authored at Round 1 (Mira spec finalize T0a output for T002.6), it would have hash-frozen the outcome partition over the F2 IS run too. Round 2 verdict (`costed_out_edge` provisional) would have had a pre-committed forward branch ("if Phase G OOS confirms K3 decay PASS but K1 strict OOS FAIL → costed_out_edge_oos_confirmed_K3_passed; T002 retire"). This would NOT have prevented Round 2 from being needed (the IS evidence WAS new) but it WOULD have shortened Round 3 → Round 3.1 cycle by pre-empting the disposition deliberation.

**RIVER MANDATE for H_next:** Pre-committed disposition rule (PRR-style 4-branch partition) authored at Round 1 spec-finalize phase as a Mira T0a deliverable companion artifact. The PRR covers the full outcome partition over the FIRST run (not just the OOS run). Subsequent rounds may append refinement PRRs for sub-classifications discovered (e.g., PRR-V2 at Round 2 covering the OOS-confirmation outcome space) but Round 1 PRR is binding from epoch start.

**Story-template enforcement:** New row in story scaffolding — `pre_committed_disposition_rule:` frontmatter pointing to PRR document. River authoring discipline — NO story Status `Draft → Ready` without PRR pointer registered.

### §3.2 Verdict-vs-reason contract test (post Round 3 lesson)

**Lesson:** Round 3 INCONCLUSIVE_phase_g_protocol_compliance_gap was caused by a verdict-vs-reason inconsistency in N8 `full_report.json` — verdict said "K3 PASS" but reason text said "DEFERRED — pending Phase G unlock". This is a contract violation: verdict-PASS implies reasons are empty OR contain computed numbers; sentinel strings ("DEFERRED") in reasons under verdict-PASS is a protocol gap.

ESC-013 R20 NEW added the contract test as a regression guard. The lesson is: **whenever a verdict layer emits both `verdict` and `reasons`, a contract test MUST verify the cross-field invariant**. This is a generalization of "fail loud, fail clear" — verdict layer artifacts are the ground truth for Mira F2-T9 sign-off authority; if the artifacts are internally inconsistent, Mira authority is compromised.

**RIVER MANDATE for H_next:** R20-pattern contract test authored at every sign-off chain row whose deliverable involves a verdict-emitting artifact. Specifically:
- Mira F2-T9 (Gate 4b) verdict layer → R20 contract test (existing; binding)
- Riven Gate 5 cosign verdict layer → analogous contract test (NEW; verifies dual-sign invariant — single-leg fire = automatic REJECT)
- Quinn QA gate verdict layer → analogous contract test (NEW; verifies 8-point-gate rollup invariant)
- Pax T002.x close verdict layer → analogous contract test (NEW; verifies status_transition trail vs Change Log entry)

Each contract test is owned by the verdict-emitting agent (Mira / Riven / Quinn / Pax respectively). River process discipline mandates the test exists as a sign-off chain deliverable.

**Story-template enforcement:** Sign-off chain row Pass criteria sub-clause MUST include "contract test artifact" pointer where applicable.

### §3.3 Closure phase Literal completeness check (post N8.1 INCONCLUSIVE bug)

**Lesson:** When Mira F2-T9 emitted Round 3 INCONCLUSIVE, the verdict-label discipline was strained — INCONCLUSIVE is a Literal in `{PASS, FAIL, INCONCLUSIVE}` per Mira spec §9, but the sub-classification suffix (`phase_g_protocol_compliance_gap`) was authored ad-hoc. The disposition rule PRR-20260430-1 §3 covered 4 branches (R15/R16/R17/R18) but the Round 3 INCONCLUSIVE was a 5th branch outside the PRR partition — surfaced as a "we'll decide when we see the data" implicit fall-through that the PRR explicitly forbids ("no implicit fall-through, no 'we'll decide when we see the data' branch" — PRR §1 verbatim).

The N8.1 → N8.2 ESC-013 §5 4-branch decision tree (a/b/c/d) post-dates the PROPER-Phase-G capability and explicitly adds branch (d) `INCONCLUSIVE_again` for procedural double-failure. This is the closure-phase Literal completeness check: the verdict Literal partition MUST be complete over the outcome space INCLUDING procedural-failure branches.

**RIVER MANDATE for H_next:** Pre-committed disposition rule (PRR-style 4-branch partition per §3.1 above) MUST include a procedural-failure branch covering "INCONCLUSIVE / protocol-gap / wiring-error / determinism-stamp-mismatch / etc." outcomes — i.e., the partition is `{PASS, FAIL_typeI, FAIL_typeII, INCONCLUSIVE_procedural, ...}` not just `{PASS, FAIL_typeI, FAIL_typeII}`. The procedural-failure branch dispositions (e.g., `→ ESC-XXX escalation; deeper protocol audit; retire as default`) are pre-committed alongside the substantive branches.

**Story-template enforcement:** PRR pointer (per §3.1 above) MUST cover the FULL Literal partition including procedural-failure branches. River authoring discipline — review PRR completeness pre-finalize; flag missing procedural-failure branches.

---

## §4 Story scope discipline H_next

T002.7 closed clean per ESC-013 §5(c) — single-iteration close (no T002.7 Round 2; the story was authored AS the close ceremony). This is the target pattern.

For H_next, two options:

**Option A — single-iteration discipline (1 Round budget):**
- H_next stories authored with 1 Round budget upfront
- Pre-committed disposition rule (PRR-style; per §3.1) covers full Literal partition INCLUDING procedural-failure branches
- T0a-T0f sign-off chain (per §1.3) gates Dex T1 begin
- AC binary-verifiable enforcement (per §2.1) gates AC closure
- If Round 1 produces FAIL or INCONCLUSIVE → successor story authored per T002.6 → T002.7 pattern (per §1.1)

**Option B — multi-round budget upfront:**
- H_next stories authored with explicit N-round budget (e.g., Round 1 + Round 2 + Round 3 budget pre-allocated)
- Each round gated by Mira spec re-finalize + sign-off chain re-clear
- Cumulative Bonferroni n_trials accumulation pre-authorized per round
- Risk-side haircut on sizing envelope per §11.5 cumulative

### §4.1 RIVER PREFERENCE: Option A (single-iteration discipline) PRIMARY

**Rationale:** Single-iteration discipline is cleaner for Article IV (No Invention) — no "we'll decide when we see the data" implicit budget for multi-round. Each round consumed costs OOS budget (per Anti-Article-IV Guard #3) which is irreplaceable; budgeting multi-round upfront pre-authorizes consumption that may not be needed. Single-iteration with successor-story pattern preserves the option to extend (via successor story) without pre-paying the cost.

**Empirical evidence basis:** T002.7 single-iteration close was clean — no Round 2, no Round 3 needed. T002.6 needed 4 iterations BECAUSE Round 1 found a wiring gap (Round 1 → Round 2) AND Round 3 found a protocol gap (Round 2 → Round 3 → Round 3.1). Both gaps are addressed by the §1.3 (T0f) + §2.2 (no IMPLICIT rows) + §2.3 (wiring validation test) + §3.1 (pre-committed PRR) + §3.3 (procedural-failure branch in PRR) amendments. WITH these amendments in place, single-iteration discipline is achievable for H_next.

### §4.2 Multi-round budget allowed ONLY under explicit conditions

**Conditions for Option B (multi-round budget upfront):**
1. Complexity score ≥ 16 (COMPLEX class per Spec Pipeline 5-dimension scoring)
2. Aria spec authority co-sign (architecture cost justifies multi-round)
3. Mira statistical authority co-sign (Bonferroni n_trials accumulation pre-authorized; not retroactively inflated)
4. Riven risk-perimeter co-sign (OOS budget consumption explicitly pre-allocated per round; haircut envelope adjusted)

If all 4 conditions met → multi-round budget authorized at Round 1 spec-finalize phase. If any condition fails → Option A (single-iteration discipline) is the default.

**RIVER MANDATE:** Default for H_next is Option A. Option B requires explicit council resolution at Round 1 spec-finalize phase (River does NOT pre-empt — Aria + Mira + Riven jointly decide).

### §4.3 Successor story pattern preserves multi-iteration option without pre-payment

The T002.6 → T002.7 pattern (per §1.1) is the canonical fallback when Round 1 produces FAIL or INCONCLUSIVE. The successor story is authored AT THE TIME the iteration is needed (not pre-allocated upfront), inherits the verdict trail, and operates as a fresh single-iteration. This preserves all the discipline benefits of Option A while allowing iteration when the data demands it.

**This is the path River recommends for H_next:** Option A primary; successor-story pattern when iteration is data-driven (not pre-allocated); Option B reserved for explicit council resolution under complexity ≥ 16.

---

## §5 Personal preference disclosure

### §5.1 River persona prior

Process-discipline-by-default custodial; "every row enumerated, no IMPLICIT fall-through"; Q-SDC workflow rounds discipline binding; sign-off chain composition is pre-flight not retrospective; closure-phase Literal completeness is non-negotiable; multi-handoff stories require multi-handoff sign-offs (not single-handoff sign-off + impl-side bridging).

### §5.2 Application to squad instrumentation amendments

**RIVER PREFERENCES (in priority order):**

1. **§1.3 NEW T0f caller-wiring sign-off row** — HIGHEST PRIORITY. Closes the F2-T9-OBS-1 admission cleanly at the story-drafting layer (one step earlier than Sable's audit-layer corrective action). Cost ≈ 1 squad session per story; benefit ≈ prevents Round 3 protocol-gap class of bugs categorically.

2. **§2.1 AC binary-verifiable enforcement** — HIGH PRIORITY. Closes the Sable F-01 retroactive concern. Cost ≈ author discipline per AC; benefit ≈ closure verification is mechanical, not subjective.

3. **§2.3 Wiring validation test (R20 generalization)** — HIGH PRIORITY. Closes the verdict-vs-reason inconsistency class. Cost ≈ test authoring per T0f row; benefit ≈ runtime artifact conformance verified at QA gate.

4. **§3.1 Pre-committed disposition rule (PRR-style) at Round 1** — HIGH PRIORITY. Closes the outcome-based threshold reinterpretation class. Cost ≈ Mira T0a companion artifact; benefit ≈ disposition is hash-frozen pre-data.

5. **§3.3 Procedural-failure branch in PRR** — MEDIUM PRIORITY (subsumed under §3.1 if §3.1 is enforced rigorously). Closes the "we'll decide when we see the data" implicit fall-through class.

6. **§4.1 Single-iteration discipline default for H_next (Option A)** — MEDIUM PRIORITY. Process discipline + Article IV alignment; multi-round budget reserved for explicit council resolution.

**RIVER DEFERRAL:** §3.2 (verdict-vs-reason contract tests for Riven Gate 5 / Quinn QA / Pax close verdict layers beyond Mira F2-T9). These are GENERALIZATIONS of R20 pattern; River does not pre-empt the verdict-emitting agents on test design. Surface concern only — Riven / Quinn / Pax retain authority on whether to author analogous contract tests for their respective verdict layers.

### §5.3 Counterfactuals

Boundary conditions that would flip River's vote on specific amendments:

- **If T0f sign-off row cost balloons to > 2 squad sessions per story** (i.e., the wiring task is genuinely complex, not just a phase-conditional flag toggle): River reconsiders T0f as a separate STORY (not a sign-off chain row), with its own AC + sign-off chain. This protects against T0f row becoming a hidden-impl-task in disguise.
- **If pre-committed PRR partitions consistently end up incomplete across multiple H_next stories** (i.e., Round N+1 surfaces a 5th branch outside the partition): River escalates to ESC-XXX council for spec-level partition discipline review (Mira spec authority + Aria architecture authority joint).
- **If single-iteration discipline produces excess successor-story authoring overhead** (e.g., > 3 successor stories per epic on average): River reconsiders Option B (multi-round budget) as default — but only under explicit council resolution.

These are NOT pleadings for re-discussion — they are transparency disclosures of boundary conditions.

---

## §6 Article IV self-audit

Every claim in this ballot traces to (a) source artifact in repository, (b) governance ledger entry, (c) AIOX agent authority matrix, (d) Q-SDC workflow rules, (e) River persona / scrum-master process discipline. NO INVENTION. NO threshold relaxation. NO pre-emption of Aria / Mira / Pax / Quinn / Sable / Riven / Beckett / Kira / Dara / Tiago / Nelo / Gage authority.

| Claim category | Trace anchors |
|---|---|
| T002.6 → T002.7 successor close-pattern | `docs/stories/T002.7.story.md` frontmatter `status_transition` + Change Log + `verdict_inherited` |
| T002.6 4-sign-off chain T0a-T0e effectiveness | `docs/stories/T002.6.story.md` lines 43-47 + 65 + 153 |
| F2-T9-OBS-1 admission (caller wiring IMPLICIT) | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §3 + Sable §6 corrective action |
| Round 1 wiring gap (`engineering_wiring`) | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` Round 1 entry; T002.0g harness |
| Round 2 costed_out_edge provisional | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` |
| Round 3 INCONCLUSIVE_phase_g_protocol_compliance_gap | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` |
| Round 3.1 final FAIL | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` |
| ESC-013 R18 (Dex caller wiring fix) | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §4.2 R18 |
| ESC-013 R19 (strict re-run discipline) | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §4.2 R19 |
| ESC-013 R20 (verdict-vs-reason contract test) | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §4.2 R20 |
| PRR-20260430-1 4-branch pre-committed disposition rule pattern | `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` §1 + §3 |
| ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §1 |
| ESC-013 5/5 UNANIMOUS APPROVE_PATH_IV | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §1 |
| Quinn QA Check 8 + Sable F-01 procedural fix | ESC-012 R14 + ESC-013 carry-forward + AIOX `qa-gate.md` 7-check + binary-verifiable AC discipline |
| AIOX agent authority matrix @sm exclusive `*draft` / `*create-story` | `~/.claude/rules/agent-authority.md` @sm row + `workflow-execution.md` SDC Phase 1 |
| Q-SDC 4-phase workflow (Create / Validate / Implement / QA Gate) | `~/.claude/rules/workflow-execution.md` §1 SDC + `~/.claude/rules/story-lifecycle.md` |
| Spec Pipeline complexity scoring (5 dimensions, classes SIMPLE/STANDARD/COMPLEX) | `~/.claude/rules/workflow-execution.md` §3 Spec Pipeline |
| AC binary-verifiable Literal partition | Mira spec §9 verdict label discipline + T002.7 §3 AC pattern |
| Anti-Article-IV Guard #3 (OOS budget irreplaceable) | `_holdout_lock.py` + `assert_holdout_safe` 5 call-sites |
| Anti-Article-IV Guard #4 (thresholds UNMOVABLE) | spec yaml v0.2.3 §kill_criteria L207-209 + Mira spec §1 |

### §6.1 Article IV self-audit verdict

NO INVENTION (all amendments §1-§4 traced to T002 specific lessons + AIOX framework rules; no cross-project speculation). NO threshold relaxation (River does not propose any spec yaml or Mira spec threshold mutation; amendments are at the STORY DRAFTING and SIGN-OFF CHAIN COMPOSITION layer only). NO source-code modification (this ballot is write-only at council-document layer; no story file mutation; no template mutation; no AIOX `.aiox-core/` mutation). NO push (Article II → Gage @devops EXCLUSIVE; River authoring this ballot does NOT push). NO pre-emption of Aria architecture authority (T0f row review by Aria is RECOMMENDED in §1.3 but is Aria's call to accept). NO pre-emption of Mira spec authority (PRR companion artifact §3.1 is Mira T0a deliverable; Mira retains authoring authority and may decline if spec scope is too narrow). NO pre-emption of Pax scope authority (story scope discipline §4 H_next preferences are surfaced; Pax retains scope decision authority). NO pre-emption of Quinn QA authority (Check 8 expansion / Check 9 NEW §2.3 is Quinn's call on test design; River mandates the test EXIST as a deliverable). NO pre-emption of Sable audit authority (§2.2 caller-wiring task EXPLICIT is one step earlier than Sable's audit-layer corrective; complementary not redundant). NO pre-emption of Riven risk-perimeter authority (§4.2 multi-round budget Riven co-sign is Riven's call; River process discipline only mandates the co-sign EXIST when Option B requested).

### §6.2 Anti-Article-IV Guards self-audit (8 guards verbatim)

| Guard | Mandate | THIS ballot reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | THIS ballot REINFORCES via §1.3 NEW T0f row (Dex T1 BLOCKED until T0a-T0f all PASS) |
| **#2** | NO engine config mutation at runtime | THIS ballot does NOT touch engine config |
| **#3** | NO touch hold-out lock | THIS ballot EXPLICITLY PRESERVES — §3.1 pre-committed PRR Round 1 makes hold-out budget consumption pre-authorized + visible |
| **#4** | Gate 4 thresholds UNMOVABLE | THIS ballot does NOT propose any threshold mutation; §2.1 AC binary-verifiable enforcement applies thresholds AS-IS |
| **#5** | NO subsample backtest run | THIS ballot does NOT authorize any backtest run |
| **#6** | NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH | THIS ballot REINFORCES via §3.2 verdict-vs-reason contract test for Riven Gate 5 cosign verdict layer (single-leg fire = automatic REJECT preserved) |
| **#7** | NO push (Gage @devops EXCLUSIVE) | THIS ballot is local-only artifact; no push performed |
| **#8** | Verdict-issuing protocol — `*_status` provenance + verdict-vs-reason invariant | THIS ballot REINFORCES via §2.3 wiring validation test (R20 generalization) + §3.2 contract test pattern |

All eight Anti-Article-IV Guards honored verbatim by THIS ballot.

---

## §7 River cosign 2026-05-01 BRT — IMPL squad-instrumentation ballot

```
Author: River (@sm) — Scrum Master & Story-Drafting Authority
Council: IMPL 2026-05-01 — Squad instrumentation & process discipline post T002 retire
Authority basis: AIOX agent authority matrix @sm exclusive (`*draft` / `*create-story`); story
  template selection; multi-handoff sign-off chain composition; Q-SDC workflow rounds discipline;
  closure-phase Literal completeness custodial.

Story drafting improvements §1:
  - T002.6 → T002.7 successor close-pattern (append-only supersede): PRESERVE verbatim canonical
  - T002.6 4-sign-off chain T0a-T0e: EFFECTIVE for spec-authoring layer; INCOMPLETE on caller-wiring
  - NEW T0f caller-wiring sign-off row mandate: gating Dex T1 begin alongside T0a-T0e

Spec-first protocol amendments §2:
  - §2.1 AC binary-verifiable enforcement (Sable F-01 carry-forward): every AC reduces to Literal partition
  - §2.2 Caller wiring task EXPLICIT in sign-off chain (Aria F2-T9-OBS-1 carry-forward): no IMPLICIT-deferred-to-impl rows
  - §2.3 Wiring validation test (Quinn QA Check 8 expansion or NEW Check 9; R20 contract test pattern)

Q-SDC workflow rounds discipline §3:
  - §3.1 Pre-committed disposition rule (PRR-20260430-1 pattern) authored at Round 1 (Mira T0a deliverable)
  - §3.2 Verdict-vs-reason contract test (R20 carry-forward) — generalization deferred to verdict-emitting agents
  - §3.3 Closure-phase Literal completeness check — PRR partition includes procedural-failure branches

Story scope discipline H_next §4:
  - Option A (single-iteration discipline) PRIMARY default
  - Option B (multi-round budget upfront) ONLY under complexity ≥ 16 + Aria + Mira + Riven joint co-sign
  - T002.6 → T002.7 successor pattern preserves multi-iteration option without pre-payment

Personal preference disclosed §5:
  - PRIORITY: §1.3 (T0f row) > §2.1 (AC binary) > §2.3 (wiring test) > §3.1 (PRR Round 1) > §3.3 (procedural-failure branch) > §4.1 (single-iteration default)
  - DEFERRAL: §3.2 generalization to non-Mira verdict layers — Riven / Quinn / Pax retain authority
  - Counterfactuals openly disclosed §5.3

Article II preservation: NO push performed by River during this ballot authoring. Gage @devops authority preserved.
Article IV preservation: every clause traces (§6); no invention; no threshold mutation; no source-code
  modification; no story file mutation; no template mutation; no AIOX framework mutation; no Aria /
  Mira / Pax / Quinn / Sable / Riven / Beckett / Kira / Dara / Tiago / Nelo / Gage authority pre-emption.

Anti-Article-IV Guards self-audit §6.2: #1-#8 honored verbatim.

Authority boundary: River authors THIS ballot from process-perimeter perspective only. Aria retains
  architecture authority; Mira retains spec + statistical authority; Pax retains scope authority;
  Quinn retains QA authority; Sable retains process audit authority; Riven retains risk-perimeter
  authority. Beckett retains backtester harness authority; Kira retains scientific peer-review;
  Dara retains data-engineering; Tiago / Nelo retain execution; Gage retains push authority.

Pre-vote independence statement: River authored THIS ballot WITHOUT consulting peer voter ballots
  (Aria / Mira / Pax / Quinn / Sable / Riven IMPL 2026-05-01 votes). Independence preserved per
  council protocol. Inputs consulted: T002.6 / T002.7 story files + Mira sign-off chain (Round 1..3.1)
  + ESC-011 / ESC-012 / ESC-013 council resolutions + PRR-20260430-1 + AIOX agent authority matrix +
  Q-SDC workflow rules. NO peer-ballot reading pre-vote.

Cosign: River @sm 2026-05-01 BRT — IMPL squad-instrumentation ballot process lens.
```

— River, drafting the next sprint
