---
council_id: ESC-012
ballot_topic: T002 strategy-fate adjudication post-Gate-4b GATE_4_FAIL_strategy_edge / costed_out_edge
voter: Pax (@po — Product Owner)
vote_date_brt: 2026-04-30
ballot_paths:
  - "Path A' — Strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble; cost reduction OFF per user constraint)"
  - "Path B — Phase G hold-out unlock OOS confirmation (single-step confirm; no scope expansion)"
  - "Path C — Retire T002 (Article IV honesty; resources redirected; epic deprecated)"
verdict: PATH_B (preferred) with PATH_C (acceptable fallback) — REJECT PATH_A'
rationale_summary: |
  From product perspective: maximum information per session invested AND backlog discipline AND Article IV honesty all point AWAY from Path A' (4 new stories, ~40 squad sessions, doubling T002 epic burn, indefinite refinement-loop risk, no falsifiability anchor) and TOWARD a single-step OOS confirmation (~6-10 sessions) followed by either clean retirement (if OOS confirms costed_out) or ESC-013 escalation (if OOS contradicts in-sample). Path B is the minimum-spend maximum-information move; Path C is the honest fallback if backlog signal degrades further.
spec_yaml_status: NO_MUTATION_PERMITTED across all paths (DSR > 0.95, PBO < 0.5, IC > 0 thresholds UNMOVABLE per Anti-Article-IV Guard #4 + ESC-011 R14 carry-forward)
authority_basis:
  - "Pax @po — story scope, AC integrity, 10-point checklist guardian"
  - "ESC-011 R10 — successor story authority; Pax adjudicates forward research path"
  - "Mira F2-T5 sign-off §8.3 — surfaces three forward-research options, defers to Pax decision"
  - "Riven F2-T6 ledger reclassification — bucket B `strategy_edge / costed_out_edge` confirmed Round 2"
council_provenance:
  - "ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C (carry-forward; 20 binding conditions R1-R20)"
  - "Mira Gate 4b sign-off Round 2 — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` GATE_4_FAIL_strategy_edge / costed_out_edge"
  - "Riven post-mortem — `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` 3-bucket framework"
article_iv_self_audit: PASS (every clause traces to listed source anchor; no invention)
cosign: Pax @po — ESC-012 strategy-fate ballot 2026-04-30 BRT
---

# COUNCIL ESC-012 — Pax Vote: T002 Strategy-Fate Adjudication

**Council:** ESC-012 — T002 strategy-fate post-Gate-4b GATE_4_FAIL_strategy_edge / costed_out_edge
**Voter:** Pax (@po — Product Owner)
**Date (BRT):** 2026-04-30
**Constraint preserved:** slippage + cost atlas FIXOS (conservative; Path A cost reduction OFF per user mandate)
**Constraint preserved:** spec yaml v0.2.3 thresholds UNMOVABLE (DSR > 0.95 / PBO < 0.5 / IC > 0; Anti-Article-IV Guard #4)
**Verdict:** **PATH_B preferred, PATH_C acceptable fallback, PATH_A' REJECT**

---

## §1 Verdict + rationale (product perspective)

### §1.1 Vote

| Path | Vote | Rank |
|---|---|---|
| **Path A'** — Strategy refinement (4 new stories: T002.7 entry timing, T002.8 regime filter, T002.9 conviction threshold, T002.10 signal ensemble) | **REJECT** | 3rd (last) |
| **Path B** — Phase G hold-out unlock OOS confirmation (single new story T002.7 Phase G; ~6-10 squad sessions) | **APPROVE (PREFERRED)** | 1st |
| **Path C** — Retire T002 (single closure ceremony; resources freed) | **APPROVE (FALLBACK)** | 2nd |

### §1.2 Product-perspective rationale

Pax adjudicates from four product-side criteria:

1. **Spec compliance** — does the path preserve spec yaml v0.2.3 thresholds AS-IS? Anti-Article-IV Guard #4 forbids threshold relaxation. All three paths are spec-compliant in this dimension (no threshold mutation requested by any path). Tie.

2. **Story scope discipline** — does the path preserve T002 epic boundary or push it into refinement-loop sprawl? **Path A' = sprawl** (4 new stories chain refinement attempts indefinitely; signal ensemble is open-ended; conviction threshold tuning has no natural stopping criterion); **Path B = bounded** (1 new story, single-step OOS confirm); **Path C = closure** (terminate epic cleanly). Path B / Path C win this criterion decisively.

3. **AC integrity (10-point checklist)** — can the new story be specified with binary-verifiable ACs at draft time? **Path A' = NO** (each refinement story carries unspecified AC: which entry-window mutation? which regime feature? which conviction quantile? — these become research questions, NOT engineering ACs); **Path B = YES** (Phase G OOS confirmation has clear AC: unlock hold-out partition, run real-tape on [2025-07-01, 2026-04-21], compute DSR/PBO/IC under same Mira spec §1 strict bar, classify per Riven 3-bucket); **Path C = YES** (closure ceremony has clear AC: status Done, epic deprecated, resources redirected). Path B / Path C win.

4. **Article IV honesty** — does the path accept the evidence the data has produced, or does it search for ways to rescue the hypothesis? Mira Round 2 §5.3 explicitly: "thesis is NOT falsified at thesis Q4 kill triplet; deployment gate strict §1 is FAILED. The two are distinct." Path B asks the falsifying question (does OOS confirm in-sample costed_out_edge?); Path A' rescues; Path C accepts. **Path B is the strongest Article IV move** — it asks the data to refute or confirm; it does NOT mutate the question. Path C is honest acceptance. Path A' is rescue mode.

### §1.3 Why Path B over Path C as primary preference

Path B ranks above Path C because the marginal information value of a single OOS run is high relative to the small additional spend (~6-10 sessions). Mira §5.3 frames the decision boundary precisely:

> "if OOS DSR also < 0.95, T002 retired with full bucket B clean-negative confirmation; if OOS DSR > 0.95, regime evidence is mixed (in-sample costed-out + OOS deployable) and council escalation"

Translating to product terms:

- **OOS DSR < 0.95** (probable outcome under Mira's Round 2 reading): Path B converts Path C's clean retirement into a **strongly evidenced** clean retirement. The post-mortem record gains both in-sample AND OOS confirmation that the strategy is costed-out — this is closure with maximum evidentiary force, future-Pax-friendly, audit-trail complete.
- **OOS DSR > 0.95** (low-probability surprise per Mira's reading): Path B reveals an in-sample-vs-OOS regime mismatch that would **NEVER** be discoverable under Path C, and that DOES warrant council escalation (ESC-013 future). This is asymmetric upside — small probability × high information value.

Path C alone forfeits the OOS confirmation step. Given the squad has already invested 30+ sessions in T002, the marginal 6-10 sessions to extract OOS evidence is a high-leverage spend.

### §1.4 Why Path A' is rejected (not just deferred)

Path A' is **structurally inconsistent with PO authority constraints**:

- **AC-undefined at draft time** — each of the 4 proposed stories cannot pass 10-point checklist (point 3: testable acceptance criteria) because the refinement direction is itself the research question. This is a category error: research questions are NOT engineering stories. They belong upstream in spec pipeline (Phase 5 critique → Phase 4 research) or in @analyst scope, NOT in @sm story drafting.
- **Spec yaml mutation pressure** — the more refinement variants tested, the higher the temptation to expand Bonferroni n_trials beyond 5 (currently UNMOVABLE per ESC-011 R9 + Mira spec §6 anchor `docs/ml/research-log.md@c84f7475…`). This is an Anti-Article-IV Guard #4 violation vector.
- **Indefinite refinement loop risk** — "signal ensemble" especially has no natural stopping criterion; each ensemble variant produces new DSR/PBO/IC; failure mode is squad burn proportional to ensemble depth.
- **Opportunity cost** — see §3 below; squad bandwidth is a finite resource; T002 has consumed disproportionate share already.

Path A' is not "wrong forever" — it could become legitimate AFTER Phase G OOS confirmation if Mira authors a NEW spec proposing specific refinement axes with falsifiability anchors. But it is wrong NOW, before the OOS evidence is in.

---

## §2 Resource allocation per path (squad sessions)

### §2.1 Path A' resource cost (REJECT path — for opportunity-cost analysis)

10-step chain × 4 stories minimum:

| Step | Agent | Per-story sessions | × 4 stories |
|---|---|---|---|
| Mira spec finalize | Mira | ~1.5 | 6 |
| Aria archi review | Aria | ~0.5 | 2 |
| Beckett consumer sign-off | Beckett | ~0.5 | 2 |
| Riven post-mortem update | Riven | ~0.5 | 2 |
| Pax 10-point validate | Pax | ~0.5 | 2 |
| Dex impl | Dex | ~3 | 12 |
| Quinn QA | Quinn | ~1 | 4 |
| Beckett N-prime re-run | Beckett | ~2 | 8 |
| Mira re-clearance | Mira | ~1 | 4 |
| Riven reclassify | Riven | ~0.5 | 2 |
| **Subtotal** | | **~11** | **~44** |

Plus Sable governance audits per story (~0.5 × 4 = 2) + Pax cosign + Gage push (~0.5 × 4 = 2) = **~48 sessions total**.

T002 epic to date: ~30+ sessions (T002.0 → T002.0h → T002.1.bis → T002.6 Round 1 → T002.6 Round 2). Path A' would push the cumulative to ~78+ sessions. **2.6× current burn for refinement variants with no falsifiability anchor.**

### §2.2 Path B resource cost (PREFERRED path)

6-step chain × 1 story:

| Step | Agent | Sessions |
|---|---|---|
| F2-T5-OBS-1 fix (decay-clause `K3_DEFERRED` short-circuit; Mira §4.5 + §8.2 follow-up) | Dex | ~0.5-1 |
| Phase G hold-out unlock spec amendment (Mira spec v1.1.0 → v1.2.0; minimal change unlock window [2025-07-01, 2026-04-21] for OOS only) | Mira | ~1 |
| Pax 10-point validate (single small-scope story) | Pax | ~0.5 |
| Beckett N8 OOS run real-tape | Beckett | ~2-3 (~3h wall + analysis) |
| Mira re-clearance (Round 3 OOS confirmation; spec §15.10 decay sub-clause now Phase G binding) | Mira | ~1 |
| Riven 3-bucket reclassify (OOS row appended to post-mortem ledger) | Riven | ~0.5 |
| Pax cosign + close + Gage push | Pax + Gage | ~0.5 |
| **Total** | | **~6-7.5** |

Plus contingency for F2-T5-OBS-1 if it surfaces deeper enforcement gap (Quinn QA add-on ~1) = **~7-9 sessions total**, conservative ceiling **~10**.

**Ratio Path A' / Path B = ~5-6× burn for orders-of-magnitude less information per session.**

### §2.3 Path C resource cost (FALLBACK path)

1 closure ceremony:

| Step | Agent | Sessions |
|---|---|---|
| Pax cosign Status Done on T002.6 | Pax | ~0.25 |
| Epic T002 status update (deprecated; reasoning anchored to Mira F2-T5 + Riven F2-T6) | Pax + River | ~0.5 |
| Memory rotation (project_algotrader_t002_state.md final) | Pax | ~0.25 |
| Gage push close ceremony | Gage | ~0.25 |
| **Total** | | **~1-1.5** |

Cleanest spend; lowest information yield (no OOS evidence captured).

### §2.4 Comparative table

| Path | Sessions | Information yield | Risk of refinement-loop | Spec yaml mutation pressure |
|---|---|---|---|---|
| Path A' | ~48 | LOW per session (rescue mode; no falsifiability anchor) | HIGH (open-ended) | HIGH (Bonferroni expansion temptation) |
| Path B | ~7-10 | HIGH (OOS = falsification anchor) | LOW (single step) | LOW (unlock mechanism documented; thresholds untouched) |
| Path C | ~1-1.5 | NONE-incremental (closes the question without OOS evidence) | NONE | NONE |

---

## §3 Backlog prioritization (opportunity cost)

### §3.1 T002 epic burn vs squad bandwidth

T002 has consumed approximately 30+ squad sessions across:
- T002.0a-e (foundational harness; ~6 sessions)
- T002.0f-h (warmup orchestrator + WarmUpGate per-phase; ~10 sessions; 4 escalations ESC-007/008/009/010)
- T002.1.bis (real make_backtest_fn integration; ~6 sessions)
- T002.6 Round 1 (real-tape replay; ~5 sessions)
- T002.6 Round 2 (IC pipeline post-fix Phase F2; ~3 sessions)

This is **already a large fraction** of cumulative squad bandwidth in this trading system project. The backlog beyond T002 includes (from `project_algotrader_t002_state.md` + `project_algotrader.md`):

- **T002.5 reservada** — telemetria + EOD reconciliation (planned; pre-Gate-5 dependency).
- **MC-29-1+** Vespera metrics extensions (D5+ planned).
- **Alternative alpha hypotheses** — currently UN-explored because squad was T002-locked.
- **Live ProfitDLL paper-mode integration** — Phase H (post-Gate-5).
- **Risk infrastructure hardening** — Riven §11.5 capital ramp protocol completion.

### §3.2 Opportunity cost of Path A'

If Path A' is chosen, ~48 sessions are consumed by T002 refinement variants. At current squad cadence, this is multiple sprints of bandwidth that COULD instead develop:

- **At least one alternative alpha thesis** end-to-end (new hypothesis → spec → harness → backtest → clearance) at the per-thesis cost demonstrated by T002 itself.
- **OR** the entire T002.5 telemetria/EOD reconciliation infrastructure that pre-conditions Gate 5 anyway.
- **OR** complete paper-mode integration setup that blocks Phase H.

**The opportunity cost of Path A' is the strongest single argument against it.** Even if we believed every refinement variant had 25% probability of producing GATE_4_PASS (an optimistic prior given Mira's `costed_out_edge` reading), the expected information yield per session is much lower than redirecting to a fresh alpha or Gate 5 pre-condition work.

### §3.3 Opportunity cost of Path B

~7-10 sessions is **comparable to a single normal story** in this project. Bandwidth impact is minor; insurance value (asymmetric upside via OOS surprise + clean retirement evidentiary force) is high. **Path B does not meaningfully delay backlog work.**

### §3.4 Opportunity cost of Path C

~1-1.5 sessions; effectively zero opportunity cost. Frees squad immediately for next priority.

### §3.5 Backlog priority post-vote (Pax recommendation conditional on Path B)

If Path B passes council:

1. **T002.7** — Phase G OOS confirmation (NEW story; this council ratifies story creation; @sm draft authority)
2. **T002.5** — telemetria + EOD reconciliation (resume planned work; can run in parallel if squad has capacity)
3. **F2-T5-OBS-1** Dex follow-up (decay-clause short-circuit) — folded into T002.7 AC1 or sequenced before T002.7 Beckett N8 run

If Path B fails / OOS DSR < 0.95: pivot to Path C (clean retirement). If OOS DSR > 0.95: ESC-013 council escalation; Path A' may become legitimate at THAT point with proper falsifiability anchors authored by Mira.

---

## §4 Spec yaml mutation risk per path

Pax authority bears DIRECT responsibility for spec yaml integrity (UNMOVABLE thresholds at L207-209; Anti-Article-IV Guard #4; ESC-011 R14 carry-forward).

### §4.1 Path A' — HIGH risk

Mutation pressure vectors:

1. **Bonferroni n_trials expansion** — testing 4+ refinement variants tempts increasing n_trials beyond 5 to "give the strategy a fair chance under multiple hypothesis correction". This DIRECTLY violates ESC-011 R9 carry-forward (`n_trials_source: docs/ml/research-log.md@c84f7475…` UNMOVABLE).
2. **DSR threshold relaxation** — refinement story cycles produce DSR values clustered near but below 0.95; pressure to argue "0.92 is close enough" or "weighted ensemble DSR should use different threshold" emerges naturally. Anti-Article-IV Guard #4 forbids; but the social pressure of 4 sequential FAIL outcomes is a real risk.
3. **PBO / IC threshold drift** — same dynamic; particularly IC threshold with `costed_out_edge` evidence ("IC=0.866 is so high that surely the threshold should be re-examined"). Forbidden but tempting.
4. **n_trials_source anchor mutation** — pressure to update research-log.md anchor or change provenance chain to admit new refinement axes.

**Pax assessment: Path A' is the highest spec-mutation-pressure path.** The squad would face cumulative pressure across 4 stories to "honor work invested" by relaxing thresholds. This is precisely what Anti-Article-IV Guard #4 was designed to prevent.

### §4.2 Path B — LOW risk

Mutation pressure vectors:

1. **Phase G hold-out unlock** — this is a documented mechanism (Anti-Article-IV Guard #3 governs hold-out lock; spec §15.10 decay sub-clause is "Phase G; not Phase F2" by explicit design). Unlocking for OOS confirmation is the spec-authorized mechanism, NOT a mutation.
2. **K3 decay sub-clause activation** — Phase G binding clause activates `IC_holdout > 0.5 × IC_in_sample` per spec §1 K3 row + §15.10. This is a spec-PRESERVED clause, not a mutation. Pre-authored.
3. **Spec v1.1.0 → v1.2.0 amendment** — minor version bump to formalize Phase G unlock procedure; threshold values (DSR > 0.95 / PBO < 0.5 / IC > 0) preserved verbatim. No L207-209 mutation. Append-only revision per spec §15 discipline.

**Pax assessment: Path B has near-zero spec-mutation pressure.** The unlock is mechanical execution of a pre-authored spec clause.

### §4.3 Path C — ZERO risk

No spec changes. Spec yaml + Mira spec v1.1.0 frozen as canonical record of T002 trajectory. Future re-litigation requires new ESC council + new spec authorship.

### §4.4 Spec mutation risk matrix

| Path | Threshold mutation pressure | Bonferroni expansion pressure | Anchor mutation pressure | Overall |
|---|---|---|---|---|
| Path A' | HIGH | HIGH | MEDIUM | **HIGH** |
| Path B | NONE | NONE | LOW (spec amendment v1.1.0→v1.2.0 minor; thresholds preserved) | **LOW** |
| Path C | NONE | NONE | NONE | **ZERO** |

---

## §5 Story discipline preservation

### §5.1 10-point checklist applicability

For Path A' to proceed, 4 new stories must pass Pax 10-point validation. Checking against current information state:

| Checklist point | Path A' (per story) | Path B (T002.7 Phase G OOS) | Path C (closure ceremony — not a normal story) |
|---|---|---|---|
| 1. Clear and objective title | Possibly | YES | N/A (ceremony) |
| 2. Complete description | **NO** (refinement direction is the research question) | YES | N/A |
| 3. Testable AC | **NO** (which entry mutation? which regime feature? — research-question-shaped) | YES (DSR/PBO/IC over hold-out window with strict bar) | N/A |
| 4. Well-defined scope IN/OUT | **NO** (signal ensemble has no natural boundary) | YES (single OOS run; F2-T5-OBS-1 fix; reclassify) | N/A |
| 5. Dependencies mapped | YES | YES | N/A |
| 6. Complexity estimate | Possibly | YES (~6-10 sessions) | N/A |
| 7. Business value | WEAK (refinement-loop signal) | STRONG (definitive answer; either clean retire or escalate) | STRONG (clean closure; bandwidth freed) |
| 8. Risks documented | Possibly | YES | N/A |
| 9. Definition of Done | **NO** (refinement loop has no DoD without arbitrary cutoff) | YES (Mira Round 3 verdict + Riven reclassify + Pax cosign) | N/A |
| 10. Alignment with PRD/Epic | **NO** (refinement axes invented post-hoc; no PRD source anchor) | YES (ESC-011 R10 forward research direction; Mira §8.3 (a) explicit) | YES (Article IV honesty per spec §0 falsifiability mandate) |

**Pax verdict: Path A' fails 10-point checklist on ≥4 dimensions per story (points 2, 3, 4, 9, 10) — FAIL by Pax authority.** Path B passes 10/10. Path C is ceremony, not story; passes Article IV self-audit instead.

### §5.2 Article II push gate compatibility

All three paths are Article II compatible (Gage @devops EXCLUSIVE push authority preserved; no path requires push from any non-Gage agent).

### §5.3 Successor story authority chain (ESC-011 R10)

ESC-011 R10 grants Pax adjudication authority over successor story creation post-T002.6 verdict. This council ESC-012 IS the R10 exercise. Whatever path passes here becomes the binding adjudication.

---

## §6 Personal preference disclosure

Pax discloses personal preference per autonomous mode council protocol (council fidelity > silent preference):

### §6.1 Preference (a) — Maximum information per session invested

Path B yields ~OOS-evidence per ~7-10 sessions = high information density. Path A' yields ~refinement-variant DSR per ~12 sessions per story × 4 stories = lower information density (and rescue-mode-shaped, which compounds Article IV concern). Path C yields zero new information for ~1.5 sessions = density undefined (but high efficiency at converting bandwidth to closure). **Preference (a) ranks: B > C > A'.**

### §6.2 Preference (b) — Backlog discipline (don't chain refinements into infinite loop)

Path A' is the textbook refinement-loop pattern — chaining 4 stories where each FAIL outcome creates pressure to author yet another story (T002.11 ensemble-of-ensembles? T002.12 regime-conditional ensemble?). Path B has natural stopping criterion (OOS confirms or contradicts). Path C is the strongest backlog-discipline move (terminates the chain entirely). **Preference (b) ranks: C > B > A'.**

### §6.3 Preference (c) — Article IV honesty (accept what evidence shows)

Mira Round 2 §5.3 frames the honest reading: thesis Q4 kill triplet is NOT triggered (DSR=0.767 > 0; PBO=0.337 < 0.4; IC decay deferred to Phase G; DD untestable Phase H); deployment gate strict §1 IS failed. Path A' attempts to mutate the strategy until the deployment gate is met, which is rescue-mode, NOT acceptance. Path B asks the data the falsifying question (does OOS confirm in-sample costed_out?). Path C accepts the in-sample failure as sufficient. Both B and C are Article-IV-honest; A' is not. **Preference (c) ranks: B ≈ C > A'.**

### §6.4 Aggregated preference

- Path B: ranks 1st on (a), 2nd on (b), tied 1st on (c) → **average rank 1.33**
- Path C: ranks 2nd on (a), 1st on (b), tied 1st on (c) → **average rank 1.33**
- Path A': ranks 3rd on all three → **average rank 3.00**

Paths B and C are statistically tied at the preference-aggregate level. Pax breaks the tie via §1.3 reasoning: marginal information value of OOS run (~6-10 sessions for asymmetric upside) tips the balance toward B as primary, with C as fallback if B's OOS evidence does not arrive cleanly.

### §6.5 Preference disclosure declaration

Pax preference does NOT override product-criteria adjudication; it serves as tie-breaker after spec/scope/AC/Article IV criteria are applied. The §1 vote (Path B preferred, Path C fallback, Path A' reject) is supported by both criteria-based reasoning AND personal-preference aggregation. No preference-vs-criteria conflict to disclose.

---

## §7 Recommended conditions

If Path B passes council, Pax recommends the following binding conditions on the successor story T002.7 Phase G OOS confirmation:

### §7.1 Spec amendment (Mira authority)

- **C1** — Mira authors spec v1.1.0 → v1.2.0 amendment activating Phase G binding clauses: K3 decay sub-clause (`IC_holdout > 0.5 × IC_in_sample`) becomes operative; hold-out window [2025-07-01, 2026-04-21] unlocked for SINGLE OOS run; Anti-Article-IV Guard #3 modified to "post-Phase-G-unlock; no further hold-out modification".
- **C2** — DSR > 0.95 / PBO < 0.5 / IC > 0 thresholds preserved verbatim (parent yaml L207-209; Anti-Article-IV Guard #4 UNMOVABLE).
- **C3** — Bonferroni n_trials = 5 carry-forward (ESC-011 R9; `n_trials_source` anchor preserved verbatim).
- **C4** — Spec amendment append-only revision per §15 discipline; Round 1 + Round 2 sign-offs integrity preserved; v1.2.0 supersedes via append-only.

### §7.2 Story scope discipline (Pax + River authority)

- **C5** — T002.7 scope IN: (i) F2-T5-OBS-1 Dex follow-up (decay-clause `K3_DEFERRED` short-circuit per Mira §4.5 + §8.2); (ii) Phase G hold-out unlock execution; (iii) Beckett N8 OOS real-tape run; (iv) Mira Round 3 OOS verdict; (v) Riven F2-T6+ ledger entry; (vi) Pax cosign close.
- **C6** — T002.7 scope OUT: (i) ANY refinement of strategy logic (entry/exit/regime/conviction/ensemble — explicitly NOT this story; deferred to potential Path A' future story IF and ONLY IF OOS surprise warrants ESC-013); (ii) cost atlas modification (constraint preserved); (iii) Bonferroni n_trials expansion; (iv) threshold mutation.
- **C7** — 12 binary-verifiable AC required at draft time; Pax 10-point validate must reach ≥9/10 before T1 begin (Mira spec amendment-first protocol; mirrors T002.6 spec-first discipline).

### §7.3 Verdict discipline (Mira authority)

- **C8** — Mira Round 3 verdict label per spec §9 discipline: `GATE_4_PASS` (in-sample AND OOS strict triplet PASS; lowest probability per Mira §5.3 reading) | `GATE_4_FAIL_strategy_edge` sub-classification `costed_out_edge_confirmed_OOS` (in-sample FAIL persists OOS; clean retirement evidentiary path; highest probability per Mira) | `INCONCLUSIVE_regime_mismatch` (in-sample FAIL but OOS PASS; ESC-013 escalation path; low probability surprise).
- **C9** — Mira spec §15 deferred-decay clause becomes binding under Phase G; no spec-side relaxation under any verdict.

### §7.4 Risk reclassification (Riven authority)

- **C10** — Riven F2-T6+ ledger entry classifies N8 OOS row per 3-bucket framework (bucket B `strategy_edge` with sub-classification confirmed/contradicted/regime-mismatch); §11.5 capital ramp pre-condition #7 audit final disposition recorded.
- **C11** — Gate 5 fence preserved verbatim (R5/R6 conjunction Gate 4a HARNESS_PASS ∧ Gate 4b GATE_4_PASS ∧ paper-mode audit; R6 footer §10 carry-forward Round 3).

### §7.5 Forward-research path conditional on Round 3 outcome

- **C12** — IF Round 3 = `GATE_4_PASS` (low probability): unlock Phase H paper-mode planning (T002.8 future story); ESC-013 NOT required.
- **C13** — IF Round 3 = `GATE_4_FAIL_strategy_edge / costed_out_edge_confirmed_OOS` (high probability per Mira): execute Path C clean retirement; epic T002 deprecated; squad bandwidth freed; memory rotation final.
- **C14** — IF Round 3 = `INCONCLUSIVE_regime_mismatch`: trigger ESC-013 council with FULL squad; reconsider Path A' refinement direction WITH Mira-authored falsifiability anchors per axis (NOT post-hoc); spec yaml v0.2.4+ amendment may become warranted under proper governance.

### §7.6 Sable governance audit

- **C15** — Sable Phase G coherence audit gate before Gage push (Mira Round 3 sign-off + Riven post-mortem + spec v1.2.0 amendment + Pax cosign + 10-point checklist trace ALL coherent).

### §7.7 Article II push gate

- **C16** — Gage @devops EXCLUSIVE push authority preserved per usual (carry-forward; T002.6 Round 2 closure already merged main 2026-04-30 12:36 BRT per Mira frontmatter `head_post_merge_main: 0903eaf`).

---

## §8 Article IV self-audit

Per Constitutional Article IV (No Invention) + AIOX framework Article IV enforcement (every claim source-anchored):

| Claim category | Trace anchor |
|---|---|
| Gate 4b verdict GATE_4_FAIL_strategy_edge / costed_out_edge | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` frontmatter + §1 |
| K1 DSR=0.767 / K2 PBO=0.337 / K3 in-sample IC=0.866 | Mira Round 2 §1 + §2 + N7-prime full report `data/baseline-run/cpcv-dryrun-auto-20260430-1ce3228230d2/full_report.json` |
| Spec yaml thresholds DSR > 0.95 / PBO < 0.5 / IC > 0 UNMOVABLE | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` v0.2.3 L207-209 + Anti-Article-IV Guard #4 + ESC-011 R14 |
| Bonferroni n_trials = 5 anchor | `docs/ml/research-log.md@c84f7475…` per Beckett §5.3 + ESC-011 R9 |
| 3-bucket attribution framework (engineering_wiring / strategy_edge / paper_mode_audit) | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §1.1-§1.3 |
| Mira §8.3 three forward-research options (Phase G OOS / cost-side exploration / retirement+redirect) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §8.3 |
| Pax forward-research authority | ESC-011 R10 + Mira §8.3 + spec §0 falsifiability mandate |
| ESC-011 R5/R6 Gate 5 conjunction fence | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome + §2 conditions |
| Anti-Article-IV Guard #4 (threshold UNMOVABLE) | Mira spec v1.1.0 §11.2 + ESC-011 R14 + Round 2 §9 row #4 |
| Anti-Article-IV Guard #3 (hold-out lock; Phase G unlock spec-authorized) | Mira spec v1.1.0 §11.2 + §15.10 + Round 2 §3 |
| Costed_out_edge sub-classification definition | Mira Round 2 §1 + §5.2 evidence matrix; Riven post-mortem §1.2 bucket B envelope |
| 10-point checklist (PO authority) | `.aiox-core/development/tasks/validate-next-story.md` + AIOX framework story-lifecycle.md rules |
| Squad session burn estimates per agent | T002.6 story estimate L14 + observed T002.0a-h + T002.1.bis + T002.6 R1+R2 cumulative |
| Backlog candidates (T002.5 telemetria; alternative alphas; paper-mode integration) | `project_algotrader_t002_state.md` memory + `project_algotrader.md` snapshot |
| Spec append-only revision discipline | Mira Gate 4b spec v1.1.0 §15 + Round 2 frontmatter `supersedes` field |

**Self-audit verdict:** every claim in §1-§7 traces to a verifiable source (Mira sign-off OR Riven post-mortem OR ESC-011 resolution OR spec yaml OR memory file OR AIOX framework rule). NO INVENTION. NO threshold relaxation proposed by Pax (threshold mutation rejected as a vector under ALL three paths via §4 analysis). NO Bonferroni expansion proposed by Pax. NO hold-out modification proposed by Pax (Path B unlock is pre-authored spec mechanism, NOT mutation). NO Round 1 / Round 2 sign-off mutation. NO source code modification. NO commit / push performed by Pax during this vote.

### §8.1 Anti-Article-IV Guard cross-check

| Guard | Pax vote action | Compliance |
|---|---|---|
| #1 Dex impl gated em Mira spec PASS | Pax does NOT authorize new impl; T002.7 (if approved) gated em Mira spec v1.2.0 PASS | PRESERVED |
| #2 NO engine config mutation at runtime | No config changes proposed | PRESERVED |
| #3 NO touch hold-out lock | Path B uses pre-authored Phase G unlock mechanism (spec §15.10 explicit; NOT mutation) | PRESERVED |
| #4 Gate 4 thresholds UNMOVABLE | Pax explicitly rejects threshold relaxation across all paths | PRESERVED |
| #5 NO subsample backtest run | No subsample proposed | PRESERVED |
| #6 NO Gate 5 disarm sem Gate 4a + Gate 4b BOTH | Pax preserves R5/R6 fence; current verdict Round 2 GATE_4_FAIL means Gate 5 LOCKED — Pax confirms no pre-disarm authorized | PRESERVED |
| #7 NO push (Gage EXCLUSIVE) | Pax authoring vote document only; no commit/push performed | PRESERVED |
| #8 Verdict-issuing protocol (`*_status` provenance) | Path B Round 3 verdict will exercise Guard #8 fully (OOS channel `ic_holdout_status='computed'` + decay-clause now binding under Phase G) | PRESERVED forward |

All 8 guards preserved by Pax vote.

---

## §9 Pax cosign

```
Author: Pax (@po — Product Owner) — story scope, AC integrity, 10-point checklist guardian
Council: ESC-012 — T002 strategy-fate adjudication post-Gate-4b GATE_4_FAIL_strategy_edge / costed_out_edge
Date (BRT): 2026-04-30
Branch: main (Pax authoring; no commit/push performed)
Verdict: PATH_B (preferred) > PATH_C (acceptable fallback) >> PATH_A' (REJECT)
Rationale: Path B yields maximum information per session invested via single-step OOS confirmation under Mira spec v1.2.0 amendment (~7-10 sessions); preserves backlog discipline (no refinement-loop sprawl); honors Article IV (asks falsifying question, does NOT rescue hypothesis); near-zero spec-yaml mutation risk (Phase G unlock is pre-authored spec mechanism, NOT threshold mutation). Path C (clean retirement) is honest fallback if Path B yields confirmed costed_out OOS or if council prefers immediate closure; ~1-1.5 sessions, zero opportunity cost. Path A' rejected: 4 new stories × ~12 sessions each = ~48 sessions for refinement variants without falsifiability anchors, fails 10-point checklist on ≥4 points per story (description, AC, scope, DoD, PRD-alignment), HIGH spec-yaml mutation pressure (Bonferroni n_trials expansion + threshold relaxation vectors), refinement-loop indefinite-burn risk, opportunity cost = 1+ alternative alpha thesis OR Gate 5 pre-condition (T002.5 telemetria) infrastructure forfeited.
Article II: NO push performed by Pax during vote authoring. Gage @devops authority preserved.
Article IV: every clause §1-§8 traces to verifiable anchor (Mira Round 2 sign-off / Riven post-mortem / ESC-011 resolution / spec yaml v0.2.3 / memory files / AIOX framework rules); NO invention; NO threshold mutation proposed; NO Bonferroni expansion proposed; NO hold-out modification proposed (Path B unlock is pre-authored spec mechanism); NO source code modification; NO commit / push performed.
Anti-Article-IV Guards #1-#8: all preserved per §8.1 cross-check (#3 hold-out under Path B uses spec §15.10 pre-authored unlock; #4 threshold UNMOVABLE preserved across all paths; #6 Gate 5 fence preserved; #7 Gage push exclusive preserved; #8 Round 3 future verdict will exercise fully under Phase G binding clauses).
Authority boundary: Pax issues this strategy-fate ballot; does NOT pre-empt River @sm draft authority over T002.7 (if Path B passes); does NOT pre-empt Mira spec amendment authority (v1.2.0); does NOT pre-empt Beckett N8 run authority; does NOT pre-empt Riven 3-bucket reclassification authority; does NOT pre-empt Sable governance audit; does NOT pre-empt Gage push authority. Pax exercises ESC-011 R10 forward-research adjudication authority + 10-point checklist guardian authority + spec scope discipline authority + backlog prioritization authority.
Council fidelity: ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification preserved (R1-R20 all carry-forward; particularly R5/R6 fence + R9 Bonferroni + R10 successor authority + R14 threshold UNMOVABLE + R20 post-mortem audit). Mira Round 2 sign-off integrity preserved (Pax does NOT supersede Mira verdict; Pax adjudicates forward path consistent with Mira §8.3 menu).
Spec yaml status: NO MUTATION proposed by Pax under any path. Path B authorizes Mira spec markdown amendment v1.1.0 → v1.2.0 minor (Phase G unlock procedure formalized; thresholds preserved verbatim; append-only revision per §15 discipline); parent spec yaml v0.2.3 thresholds at L207-209 UNMOVABLE Round 3 forward.
Round 1 / Round 2 sign-off integrity: PRESERVED (no overwrite; Round 3 supersedes Round 2 only IF Path B executes and produces new verdict; supersession via append-only revision per spec §15 discipline).
F2-T5-OBS-1 Dex follow-up: ratified as in-scope for T002.7 AC1 (decay-clause `K3_DEFERRED` short-circuit under `ic_holdout_status='deferred'` per Mira §4.5 + §8.2); implementation-side fix, NOT spec-side amendment; recommended sequence-before-Beckett-N8 per §7.5 C7.

Cosign: Pax @po 2026-04-30 BRT — ESC-012 strategy-fate ballot under autonomous mode.
```

---

— Pax @po, 2026-04-30 BRT — ESC-012 T002 strategy-fate ballot.
