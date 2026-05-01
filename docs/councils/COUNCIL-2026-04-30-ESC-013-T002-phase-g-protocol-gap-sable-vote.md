---
council: ESC-013
title: T002 Phase G Protocol-Compliance Gap — adjudicate Path (iv) re-run vs Path C retire
date_brt: 2026-04-30
voter: Sable (@squad-auditor)
authority_basis: Q-SDC Phase G coherence audit ownership (R5 ESC-012); R14 Sable-squad audit perimeter; auditor não audita a si mesmo
prior_artifact: docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md
trigger_artifact: docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (verdict GATE_4_INCONCLUSIVE_pending_phase_g_proper / phase_g_protocol_compliance_gap)
esc_012_ref: docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md
prr_ref: docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md
mira_spec_ref: docs/ml/specs/T002-gate-4b-real-tape-clearance.md@v1.2.0 §15.13
ballot_independence: voter wrote without reading peer ballots (per Article IV council protocol)
verdict_primary: APPROVE_PATH_iv_protocol_corrected_phase_g_rerun
verdict_secondary_fallback: APPROVE_PATH_C_if_council_reads_parquet_consumption_as_oos_one_shot
path_a_prime_status: out_of_scope_council_already_rejected_unanimously_in_esc_012
f2_t9_obs_1_admission: ACKNOWLEDGED — R5 audit scope did not enumerate F2-T8-T1 Dex wiring as pre-N8 prereq; gap surfaced post-N8 by Mira Round 3
push_authorization_scope: not_in_play_this_ballot (Article II — Gage exclusive at story close)
---

# Sable ballot — ESC-013 adjudication: Path (iv) protocol-corrected Phase G re-run vs Path C retire

> **Voter:** Sable (@squad-auditor) — auditor externo, sem voto operacional sobre alpha / sizing / kill / data-fate.
> **Council:** ESC-013 convened under PRR-20260430-1 §3.4 INCONCLUSIVE branch (NOT under ESC-012 R15 surprise-PASS agenda — distinction surfaced by Mira Round 3 §9).
> **Question on the floor:** does the squad authorize a protocol-corrected Phase G proper re-run (Path (iv); ~5-10 LoC Dex wiring + N8.1 ~3h Beckett) OR retire T002 under Path C (ESC-012 §5 fallback)?
> **Sable scope discipline (R14):** Sable adjudica **process integrity + governance ledger coherence**, NÃO data-fate (Mira ML authority + council jointly), NÃO architecture micro-task design (Aria), NÃO run scope (Beckett), NÃO 3-bucket reclassify (Riven), NÃO story scope (Pax). Sable independent ballot input on procedural integrity.

---

## §1 Verdict + rationale (process audit perspective)

**Sable primary verdict: `APPROVE_PATH_iv_PROTOCOL_CORRECTED_PHASE_G_RERUN`.**
**Sable secondary fallback: `APPROVE_PATH_C` if council reads parquet consumption as §15.13.7 one-shot binding (legitimate alternative reading).**

Process-side rationale, in priority order:

1. **F2-T9-OBS-1 closure mechanism preference.** Path (iv) closes the protocol-compliance gap definitively by *executing the canonical Phase G OOS decay test the spec was hash-frozen against* (Mira spec v1.2.0 §15.13.2 + §15.13.5 + PRR-20260430-1 §3.1). The Round 3 verdict label `phase_g_protocol_compliance_gap` is a procedural diagnostic that has a procedural fix. Path C closes T002 *without* closing the procedural gap — the gap remains an open finding in the audit ledger forever, attached to a retired epic. From a Sable audit-trail perspective, Path (iv) yields a cleaner historical record: F2-T9-OBS-1 → F2-T8-T1.1 (Dex micro-task) → N8.1 → Mira Round 3.1 verdict COMPUTED → ledger closure. Path C yields: F2-T9-OBS-1 → epic retired → finding archived as "unrecoverable under strict §15.13.7 one-shot reading" without the COMPUTED measurement that would have disambiguated R15 vs R16/R17.

2. **R15 trigger evaluability.** Path (iv) makes the ESC-012 R15 trigger condition *evaluable* (K1+K2+K3 ALL PASS COMPUTED yes/no). Path C leaves R15 trigger condition *permanently unevaluated* — the squad never finds out whether the ESC-013 surprise-PASS pathway would have fired or not. From a governance integrity standpoint, a pre-authored trigger condition (ESC-012 R15) deserves an answer, especially when the in-sample evidence (DSR=0.965 OOS point estimate, PBO=0.163, IC=0.866) is suggestive but not binding without the COMPUTED K3 decay test.

3. **Article IV traceability rigor.** Path (iv) yields Article IV-traceable evidence: Round 3.1 verdict against PRR §3.1-§3.4 with K3 COMPUTED status — every disposition-rule branch becomes evaluable on observed metric values. Path C yields T002 closure *with* an INCONCLUSIVE-on-record (a strictly-less-rigorous outcome than COMPUTED-FAIL would have been: COMPUTED-FAIL is a falsifiable result; INCONCLUSIVE is a measurement that didn't happen). From a No-Invention perspective, Path (iv) is *more* compliant — it forces the squad to *measure* rather than *infer* the OOS edge fate.

4. **Cost-benefit asymmetry.** Path (iv) cost: ~5-10 LoC Dex (`scripts/run_cpcv_dry_run.py:1088-1102` micro-task per Mira §11.1) + ~3h Beckett N8.1 wall-time + Mira Round 3.1 verdict + Riven 3-bucket Round 3 entry append. Total wall-time ~half a day plus one Beckett run. Path C cost: zero implementation + retire ceremony + epic deprecate. Path (iv) BENEFIT: definitive Phase G fate measurement + R15 trigger condition evaluable + audit ledger gap closed clean. Path C BENEFIT: faster epic close + squad bandwidth freed for H_next research. The marginal cost of Path (iv) (~half-day) is small compared to the marginal benefit (definitive measurement closing a hash-frozen disposition rule branch).

5. **Precedent risk asymmetry (process-side).** If Path C activates here, future Sable audits face a precedent: *"procedural gap → retire path."* This creates a perverse incentive structure where any procedural gap (caught late by audit or by post-execution discovery) routes to retirement rather than fix, regardless of cost. This precedent risk affects *all future* Sable audits, not just T002. Path (iv) sets the opposite precedent: procedural gaps are *fixed* via minimal-scope corrections that preserve the spec's hash-frozen disposition rule. From an auditor incentives standpoint, Path (iv) preserves the audit's value-add (catching gaps early enables fix) over Path C (catching gaps late triggers retire).

The fallback to Path C is preserved because the §15.13.7 OOS one-shot reading admits two legitimate interpretations (Mira Round 3 §1 + §3.3 + §10.3): (a) one-shot binds the K3 decay measurement (Mira-recommended; supports Path (iv)); (b) one-shot binds the parquet read alone (Riven-leaning conservative reading; supports Path C). Both are spec-compatible. Sable does NOT pre-empt this interpretation — it is a council-level policy call. Sable primary preference (iv) reflects audit-trail rigor + R15-evaluability; Sable accepts Path C if council majority adopts the conservative §15.13.7 reading.

---

## §2 F2-T9-OBS-1 admission (Sable R5 audit scope gap acknowledgment)

**Admitted: Sable R5 audit (`docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md`) did NOT enumerate F2-T8-T1 Dex wiring (`scripts/run_cpcv_dry_run.py:1088-1102` `--phase G` flag + `holdout_locked=False` propagation) as a pre-N8 prerequisite.**

Specifics of the gap:

- R5 §1 conformance audit table (lines 39-55) listed R1 (Dex F2-T5-OBS-1 fix verdict-layer short-circuit) as ✅ COMPLETE and R8 (Beckett N8 OOS run authorization) as DEFERRED-to-N8. The gap: there is a *separate* Dex wiring task (F2-T8-T1 per Mira spec v1.2.0 §15.13.12) that lives BETWEEN R1 (F2-T5-OBS-1 verdict-layer fix) and R8 (Beckett N8 invocation). R5 collapsed F2-T8-T1 into the R8 envelope ("DEFERRED to N8 invocation") rather than surfacing it as its own pre-N8 blocker.
- R5 §8.2 vote on N8 run authorization listed conditions: F-01 R4 disposition + F-02 R13 T002.7 story draft. F-02 surfaced "T002.7 successor story draft pending" as outside R5 perimeter — but the §15.13.12 sign-off chain row for F2-T8-T1 (Dex caller wiring) was NOT extracted as a separate finding F-05 or as a §1 conformance row.
- The mechanism that caused the gap: R5 audit method §1 traversed ESC-012 §4.1 R1-R5 (pre-run governance) + §4.2 R6-R9 (run discipline, deferred to N8) + §4.3 R10-R14 (verdict + governance, deferred to post-N8) + §4.4 R15-R17 (decision-tree, deferred to post-N8). The F2-T8-T1 wiring task lives in Mira spec §15.13.12 sign-off chain (the spec-internal task ledger) rather than in ESC-012 §4 R1-R17 (the council-ratified condition list). R5 audited the R1-R17 envelope and trusted §15.13.12 sign-off chain to be Pax/Aria/Dex authority territory. *That trust delegation was the procedural gap.* §15.13.12 includes Dex-side caller wiring tasks that ARE pre-N8 invocation prereqs but were not surfaced in R5 audit's §1 conformance enumeration.

**Severity assessment (Sable on Sable):** ⚠️ HIGH (not 🔴 CRITICAL). Justification:

- Not 🔴: the gap did NOT cause an Anti-Article-IV Guard violation. Anti-Article-IV Guard #8 ("ic_holdout_status='computed' propagation") was preserved at the verdict-layer level (Dex `fadacf4` short-circuit fires correctly under deferred sentinel; the InvalidVerdictReport raise path is intact for non-deferred mismatches). The gap caused *Phase F protocol N8 against Phase G window* — a procedural mismatch that produced an INCONCLUSIVE verdict (the disposition-rule-correct route per PRR §3.4) rather than a malformed PASS or a corrupted measurement. The disposition rule held; the squad reached a defensible (if procedurally suboptimal) verdict.
- ⚠️ HIGH not 🟡 MODERATE: the gap delayed canonical Phase G OOS measurement by one squad cycle (~half-day Dex + ~3h Beckett) and required convening ESC-013 to adjudicate Path (iv) vs Path C. A truly catastrophic gap would have produced a corrupted disposition (e.g., R15 trigger fired on misclassified evidence, leading to incorrect surprise-PASS escalation, or R16/R17 fired on misclassified evidence, leading to incorrect retire). Round 3 verdict-label discipline is intact; the spec's verdict-layer correctly reported DEFERRED-sentinel-PASS (not COMPUTED-PASS) — Mira Round 3 read this correctly and routed to PRR §3.4. The disposition rule worked as designed in the *presence* of the gap; the gap was *detected* by the disposition rule rather than *masked* by it. This is an audit-system success story under partial information — but Sable should have surfaced F2-T8-T1 in R5 to prevent the gap from manifesting at all.

**Corrective action — Sable side, applicable to future audits:** add to Sable R5-equivalent audit method an explicit §15-spec-internal sign-off chain enumeration. Future Phase X coherence audits will traverse not only ESC §4 R1-R17 council-ratified conditions but ALSO the spec's §15.x sign-off chain rows (T0a-T0e + T1-T7 in Mira's case) for caller-wiring tasks that are pre-run invocation prereqs. This widens the R5 audit perimeter to catch the F2-T8-T1-class gaps ahead of run invocation.

**Corrective action — F2-T9-OBS-1 closure mechanism:** Sable does NOT directly close F2-T9-OBS-1 (Mira-authored finding); Sable acknowledges the finding stands and recommends Path (iv) as the closing mechanism. If council adopts Path (iv): F2-T9-OBS-1 closes upon Mira F2-T9.1 Round 3.1 verdict COMPUTED. If council adopts Path C: F2-T9-OBS-1 remains open in the ledger as an unrecovered procedural gap attached to the retired epic. The latter is a less-clean closure but still admissible governance-wise.

---

## §3 Procedural integrity per path

### §3.1 Path (iv) — protocol-corrected Phase G re-run

| Procedural integrity dimension | Path (iv) status |
|---|---|
| ESC-012 R6 reusability invariant (engine_config + cost atlas + rollover + Bonferroni IDENTICAL F2) | **PRESERVED** — only `holdout_locked` flag flips + `ic_holdout_status` propagation; per Mira §11.2 zero parameter mutation; spec yaml v0.2.3 thresholds UNMOVED |
| ESC-012 R7 predictor↔label semantics IDENTICAL F2 | **PRESERVED** — re-run uses same predictor=`-intraday_flow_direction` + label=`ret_forward_to_17:55_pts` |
| ESC-012 R9 OOS one-shot discipline | **PRESERVED IF council reads §15.13.7 one-shot as binding K3 decay measurement (Mira's recommended reading);** ambiguous-but-defensible if council reads as binding parquet read alone (the alternative reading) — this IS the central council adjudication question §1 |
| Anti-Article-IV Guard #4 (thresholds UNMOVABLE) | **PRESERVED** — DSR>0.95 / PBO<0.5 / IC>0 verbatim from spec yaml v0.2.3 §kill_criteria L207-209; PRR §3.1 trigger conjunction UNCHANGED |
| Anti-Article-IV Guard #5 (no sub-sample averaging) | **PRESERVED** — Path (iv) is *first* COMPUTED-PASS measurement, not an average of N8 + N8.1; Mira §1 explicit |
| Anti-Article-IV Guard #8 (`ic_holdout_status` propagation) | **STRENGTHENED** — Path (iv) wires the propagation that was missing in N8; brings actual implementation into compliance with spec invariant |
| PRR-20260430-1 hash-frozen 4-branch rule | **PRESERVED** — branches §3.1-§3.4 evaluate against COMPUTED metric values; no rule mutation; Round 3.1 verdict applies the *same* rule the PRR was hash-frozen against |
| Mira spec v1.2.0 §15.13.2 mechanism block | **FULFILLED** — the mechanism block defines exactly what F2-T8-T1.1 wiring needs to do |
| Article II push gate | **PRESERVED** — Gage exclusive at story close |
| R15 governance ledger | **PRESERVED** — Round 3.1 verdict + Riven 3-bucket Round 3 entry + ESC-013 resolution all sign-offs append-only ledger pattern |

Sable verdict on Path (iv) procedural integrity: **CLEAN with one council-level interpretation question** (R9 / §15.13.7 one-shot reading). If council ratifies the K3-decay-measurement reading, Path (iv) is fully procedure-compliant.

### §3.2 Path C — retire T002 under ESC-012 §5 fallback

| Procedural integrity dimension | Path C status |
|---|---|
| ESC-012 §5 fallback condition triggered | **CONDITIONALLY YES** — §5 lists slip causes (Dara materialization slip, Mira spec dispute, F2-T5-OBS-1 fix complications); F2-T9-OBS-1 protocol gap is NOT explicitly enumerated as a §5 slip cause but admits a council-interpretation extension |
| ESC-012 §5 14-day clock | **NOT triggered as schedule slip** — Path C activation here is policy-driven (conservative §15.13.7 reading) not schedule-driven |
| Riven minority dissent preservation | **PRESERVED + ELEVATED** — Path C activation aligns with Riven's ESC-012 ballot primary; minority-becomes-majority procedural pathway preserved per Round 3 §10.3 |
| Anti-Article-IV Guards 1-8 | **PRESERVED** — no new run; no metric mutation; no spec yaml mutation |
| F2-T9-OBS-1 closure | **OPEN-IN-LEDGER** — finding remains unrecovered in audit history; Sable §2 admission stands as record |
| Audit-trail rigor | **MEDIUM** — Round 2 + Round 3 + ESC-013 + retire ceremony provides full chain; missing element is the COMPUTED-PASS measurement that would have disambiguated R15 vs R16/R17 |
| OOS budget economics (Riven argument) | **HONORED** — hold-out window 2025-07-01..2026-04-21 reserved for next strategy hypothesis pre-registration per ESC-012 §5 |
| Article II push gate | **PRESERVED** |
| R15 governance ledger | **PRESERVED** with retire ceremony entry |

Sable verdict on Path C procedural integrity: **CLEAN under conservative §15.13.7 reading + ESC-012 §5 council-extended slip-cause interpretation.** Path C does NOT violate any guard or invariant; it preserves Riven's risk-side OOS-budget economics; it forecloses the COMPUTED-PASS measurement.

### §3.3 Comparative procedural verdict

Both paths are procedurally admissible. The deciding factor is the §15.13.7 one-shot interpretation choice + the precedent the squad sets for handling protocol-compliance gaps. Sable's process-audit-perspective recommendation favors Path (iv) on audit-trail-rigor + R15-evaluability + precedent grounds (§1.5).

---

## §4 R-rules R1-R15 + Article IV implications

### §4.1 R-rules per path

| R-rule | Path (iv) | Path C |
|---|---|---|
| R1 (CLI First) | N/A | N/A |
| R2 (Agent Authority) | PRESERVED — Aria architecture micro-task scope; Dex wiring in own perimeter; Beckett re-run in own perimeter; Mira F2-T9.1 in own perimeter; Riven 3-bucket Round 3 in own perimeter; Pax story scope in own perimeter | PRESERVED — Pax retire ceremony in own perimeter; Riven Path C activation per ESC-012 §5; Mira Round 3 INCONCLUSIVE final |
| R3 (Story-Driven) | PRESERVED — T002.7 story scope expansion to include F2-T8-T1.1 micro-task + N8.1 + Round 3.1 verdict; Pax 10-point validate Round 3 update | PRESERVED — T002 retire ceremony closes story chain |
| R4 (No Invention) | **STRENGTHENED** — every claim in Round 3.1 traces to spec §15.13 + PRR §3.1-§3.4 + ESC-012 R6 + R7; the COMPUTED measurement IS the no-invention evidence the spec demanded | PRESERVED — retire ceremony documents INCONCLUSIVE-final without inventing surrogate evidence |
| R5 (Quality First) | PRESERVED — F2-T8-T1.1 micro-task adds 1 NEW test `test_phase_g_holdout_unlock_propagation`; existing 637 PASS / 7 skip / 0 FAIL preserved + extended | PRESERVED — no new code; existing tests unchanged |
| R6/R9 (Bonferroni n_trials=5) | PRESERVED — IDENTICAL F2 carry-forward; spec §15.13.3 reusability invariant binding | PRESERVED |
| R8 (Hold-out lock) | **PRESERVED + RESOLVED** — Phase G unlock IS authorized §15.10 transition per ESC-012 R10; Path (iv) operationalizes the authorized transition that N8 missed | PRESERVED — hold-out window reserved for H_next per ESC-012 §5 |
| R10 (Gate 5 fence) | PRESERVED — Phase G PASS does NOT pre-disarm Gate 5 alone; Gate 5 still requires paper-mode Phase G/H per Mira spec §15.13.6 + Round 3 §7; Round 3.1 outcome cannot bypass this fence | PRESERVED — Gate 5 capital ramp authority remains LOCKED at retire |
| R11 (Spec-first protocol) | PRESERVED — Mira spec v1.2.0 §15.13 PRECEDED any Path (iv) implementation; no spec mutation under outcome pressure | PRESERVED |
| R12 (Anti-leak D-1 invariant) | PRESERVED — hold-out window structurally separated from in-sample; CPCV cost atlas + rollover SHAs IDENTICAL F2 | PRESERVED |
| R13 (Append-only revision) | PRESERVED — Round 3 sign-off + Round 3.1 sign-off + ESC-013 resolution all append-only; Round 1 + Round 2 sign-offs UNMOVED | PRESERVED — retire ceremony append-only entry |
| R14 (Auditor não audita a si mesmo) | **PRESERVED with §2 admission** — Sable acknowledges R5 audit scope gap (F2-T9-OBS-1) without modifying squad-auditor.md; admission documents the audit-process-self-correction without breaching R14 | PRESERVED |
| R15 (Governance ledger) | PRESERVED — ESC-013 resolution + Round 3.1 sign-off + Path (iv) implementation tasks all under canonical naming | PRESERVED — ESC-013 resolution + retire ceremony under canonical naming |

### §4.2 Article IV (No Invention) per path

**Path (iv):** STRENGTHENS Article IV compliance. The COMPUTED K3 decay measurement is the *direct, source-anchored evidence* the disposition rule was designed to evaluate. Path (iv) closes a measurement gap by *measuring*, not by *inferring*. Every Round 3.1 claim traces to spec §15.13.5 + PRR §3.1 + ESC-012 R6 + R7 + R9 + Anti-Article-IV Guard #4 verbatim. No surrogate evidence; no post-hoc rule mutation; no sub-sample averaging.

**Path C:** PRESERVES Article IV but at a lower-rigor outcome — INCONCLUSIVE-on-record means the squad chose to *not* perform the measurement that would have produced source-anchored OOS evidence. Article IV does not *require* every measurement to be performed; it requires every claim to trace. Path C's closure claim ("§15.13.7 one-shot binds parquet read; OOS budget reserved for H_next") traces to ESC-012 §5 + Riven minority dissent + Round 3 §3.3 alternative reading. Compliant; but strictly less-source-anchored than COMPUTED-PASS / COMPUTED-FAIL would have been.

### §4.3 ESC-012 R15 / R16 / R17 trigger evaluability per path

| Branch | Path (iv) | Path C |
|---|---|---|
| R15 (Phase G PASS unlikely outcome — DSR>0.95 OOS, K1+K2+K3 ALL PASS COMPUTED → ESC-013 surprise-PASS council) | **EVALUABLE** post Round 3.1 (fires or doesn't fire on observed K3 COMPUTED status) | **PERMANENTLY UNEVALUATED** — trigger condition unmeasured; pre-authored council pathway never invoked |
| R16 (FAIL_K3_collapse — IC_holdout < 0.3 → strategy_edge clean negative → retire) | **EVALUABLE** | UNEVALUATED |
| R17 (FAIL_K1+K3_sustains — IC_holdout ∈ [0.3, 0.5×IC_in_sample) AND DSR<0.95 → costed_out_edge OOS-confirmed → retire) | **EVALUABLE** | UNEVALUATED |

Path (iv) lights up the entire decision-tree branch evaluation; Path C dark-ends the decision-tree at the trigger. From a governance standpoint, a decision-tree that was pre-authored with R15/R16/R17 explicit deserves a fate observation. Path (iv) supplies it.

---

## §5 Personal preference disclosure

**Sable personal preference: Path (iv).**

Disclosed reasoning (process-audit perspective + audit-trail rigor):
- Path (iv) closes F2-T9-OBS-1 cleanly; Path C archives F2-T9-OBS-1 unrecovered.
- Path (iv) makes ESC-012 R15/R16/R17 trigger conditions evaluable; Path C dark-ends them.
- Path (iv) sets the precedent "procedural gap → minimal-scope fix" (audit-positive incentive); Path C sets the precedent "procedural gap → retirement" (audit-negative incentive).
- Path (iv) cost (~half day + 3h Beckett) is small; benefit (definitive measurement + R15 evaluability + clean ledger closure) is large; cost-benefit ratio strongly favors (iv).
- Path C has a legitimate read of §15.13.7 one-shot (Riven-leaning conservative); Sable accepts this reading as policy-admissible but does not personally prefer it.

Sable preference is not the only consideration. Council majority — particularly Riven (custodial veto on OOS-budget economics) and Mira (ML statistical authority + Round 3 author with disclosure that Mira recommends (iv) but does not pre-empt council) — drives the call. Sable provides process-audit input alongside.

**No conflict-of-interest disclosure required:** Sable has no operational stake in T002 outcome (no alpha generation, no sizing, no execution authority); Sable's preference is purely procedural-rigor-driven.

---

## §6 Recommended conditions for whichever path council adopts

### §6.1 IF council adopts Path (iv) protocol-corrected re-run

Sable cosigns the following procedural conditions (not a substitute for Aria's architecture conditions, Mira's ML conditions, Beckett's run conditions, Pax's story conditions, Riven's risk conditions — Sable conditions are process-side ADDITIVE):

1. **C-S1 (audit-trail) — F2-T8-T1.1 Dex micro-task scope MUST be Article IV-traceable to Mira spec §15.13.2 mechanism block verbatim.** Implementation diff against `scripts/run_cpcv_dry_run.py:1088-1102` MUST include in PR description a citation to §15.13.2 lines + PRR-20260430-1 §3.1 R15 binding clause + ESC-012 R2 spec amendment. ZERO surrogate logic; no parameter additions beyond `holdout_locked=False` flip + `ic_holdout_status='computed'` propagation per spec.
2. **C-S2 (regression guard) — existing `test_k3_deferred_short_circuit` GREEN-PRESERVED.** Path (iv) extends Phase G branch but does NOT touch the Phase F deferred-sentinel path. Dex `fadacf4` short-circuit fires correctly under DEFERRED for legacy callsites. Test must remain GREEN post-implementation as regression guard. Sable will spot-check the test assertion text in post-implementation R5.1 audit.
3. **C-S3 (NEW test mandatory) — `test_phase_g_holdout_unlock_propagation` per Mira §11.1.** Asserts (a) `holdout_locked=False` flag wires through to `compute_ic_from_cpcv_results`; (b) `MetricsResult.ic_holdout_status == 'computed'` post-call; (c) `ic_holdout != 0.0` (non-sentinel value). All three assertions binding.
4. **C-S4 (Sable R5.1 supplemental audit) — Sable performs R5.1 supplemental coherence audit pre-N8.1 invocation.** Scope: F2-T8-T1.1 implementation diff Article IV trace + test assertions + spec §15.13.2 mechanism conformance. Estimated ~half-session. Closes upon Sable cosign before Beckett N8.1 invocation. This is the corrective action for Sable's R5 audit scope gap §2.
5. **C-S5 (R4 truncation disclosure carry-forward) — N8.1 inherits R5 §4.4 mandatory disclosure mechanism.** N8.1 determinism stamp report MUST disclose hold-out window 92% coverage truncation 2026-04-03..2026-04-21 missing; sample-size verification ≥ 150 floor. Same disclosure mandate Round 3 §5.3 + Round 3 §10.2 already honored carry-forward.
6. **C-S6 (Mira spec v1.2.0 → v1.2.1 micro-amendment if needed) — IF Path (iv) implementation requires any spec text clarification beyond §15.13.2 mechanism block as written, Mira authors v1.2.1 amendment append-only + 4 sign-offs T0a-T0e' precede Dex implementation.** Anti-Article-IV Guard #1 (Dex impl gated on Mira spec PASS) preserved. Sable verifies pre-N8.1.
7. **C-S7 (Round 3.1 verdict label discipline) — Mira F2-T9.1 verdict label MUST adhere to spec §15.13.8 + PRR §3.1-§3.4 4-branch enumeration: `GATE_4_PASS_oos_confirmed` (R15 trigger fires) / `GATE_4_FAIL_strategy_edge_K3_collapse` (R16 fires) / `GATE_4_FAIL_K1+K3_sustains_costed_out_edge_oos_confirmed` (R17 fires) / `GATE_4_INCONCLUSIVE_<refined_diagnostic>` (PRR §3.4 partition).** No new label classes invented; no PASS-without-K3-COMPUTED; no FAIL-without-K3-COMPUTED.
8. **C-S8 (post-N8.1 Sable R5.2 closing audit) — Sable performs final post-N8.1 / pre-Round-3.1-publication audit.** Scope: Round 3.1 verdict trace + 3-bucket reclassify Round 3 entry consistency + ESC-013 resolution closure + R-rules R1-R15 carry-forward. Estimated ~one session.
9. **C-S9 (ESC-013 council ID adjudication) — Pax authority adjudicates whether ESC-013 retains current ID for Path (iv) ratification or whether the current council closes ESC-013 with Path (iv) ratification + a separate ESC-014 opens for any R15-surprise-PASS Round 3.1 outcome.** Either is acceptable per Mira Round 3 §9. Sable preference: re-use ESC-013 for Path (iv) ratification + open ESC-014 (or re-purpose ESC-013) for R15-surprise-PASS *if and only if* Round 3.1 fires R15. Reduces ledger entropy.

### §6.2 IF council adopts Path C retire

1. **C-S1' (F2-T9-OBS-1 ledger closure with rationale) — Sable open-finding F2-T9-OBS-1 archived with explicit closure rationale "council adjudicated §15.13.7 one-shot binds parquet read; protocol gap unrecovered under conservative reading; T002 retired."** No silent archive; rationale must trace to ESC-013 resolution.
2. **C-S2' (3-bucket Round 3 entry per Riven) — Riven 3-bucket reclassify Round 3 entry per Mira Round 3 §10.2 + Round 3 §10.3 with addendum: bucket label `phase_g_protocol_compliance_gap_unrecovered_under_strict_§15.13.7_reading` + Path C activation rationale.** Bucket B `costed_out_edge` Round 2 entry preserved; Round 3 entry append-only.
3. **C-S3' (T002 retire ceremony scope) — Pax authors T002 retire ceremony per ESC-012 §5: T002.6 closes Done; T002.7 closes Done (Path C activated; pre-N8 prep work landed; F2-T9-OBS-1 archived); epic T002 deprecated; squad bandwidth freed for H_next; hold-out window 2025-07-01..2026-04-21 reserved for next strategy hypothesis pre-registration per ESC-012 §5.**
4. **C-S4' (audit history correction) — Sable adds note to `docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md` §1 R-status table cross-reference: "F2-T8-T1 Dex caller wiring task per Mira spec §15.13.12 was implicit in R8 envelope but not enumerated as standalone pre-N8 prereq in this audit; gap surfaced post-N8 by Mira Round 3 F2-T9-OBS-1; council adjudicated Path C; corrective action for future Sable audits: enumerate spec §15.x sign-off chain rows alongside ESC §4 R1-R17 conditions in pre-run coherence audits."** This corrects the audit history without R14 violation (Sable amends the audit's own scope discipline note, not the audit's primary findings).
5. **C-S5' (precedent documentation) — ESC-013 resolution explicitly notes Path C activation here is a §15.13.7 conservative-reading policy choice + a §5 slip-cause council-extended interpretation, NOT a precedent for "any procedural gap → retire."** Future protocol-compliance gaps should default to Path-(iv)-class minimal-scope corrections; Path C activation requires explicit conservative §15.13.7 council ratification each time.

### §6.3 Conditions common to either path

1. **C-S10 (Article II push gate preservation) — no Gage push during ESC-013 deliberation; Round 3 sign-off + ESC-013 ballots + ESC-013 resolution land via Gage exclusive at story close.** Standard Article II honored (Constitution Article II + global instructions).
2. **C-S11 (R-15 governance ledger naming) — ESC-013 resolution canonical name `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-resolution.md`; ballot files canonical `COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-{voter}-vote.md`.** Sable spot-checks naming pattern post-resolution.
3. **C-S12 (ballot independence preserved) — voters MUST cast without reading peer ballots until resolution authoring stage; Sable ballot (THIS) was authored without reading other ESC-013 ballots per user mandate + ESC-012 §6 Article IV strong-evidence pattern carry-forward.**

---

## §7 Article IV self-audit (Sable on Sable, this ballot)

| Claim | Source anchor (verified) | Disposition |
|---|---|---|
| Mira Round 3 verdict `GATE_4_INCONCLUSIVE_pending_phase_g_proper / phase_g_protocol_compliance_gap` | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` frontmatter + §1 verbatim | **CONFIRMED** verbatim |
| F2-T9-OBS-1 surfaced by Mira Round 3 §3.1 | Round 3 §3.1 verbatim "Round 3 procedural finding F2-T9-OBS-1 (NEW): F2-T8-T1 Dex wiring was a hidden prerequisite to R8…" | **CONFIRMED** verbatim |
| Sable R5 audit scope did not enumerate F2-T8-T1 | `docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md` §1 R1-R17 conformance table (lines 39-55) — F2-T8-T1 not listed; R8 listed as DEFERRED-to-N8 envelope | **CONFIRMED** by direct inspection of own prior audit |
| ESC-012 R6 reusability invariant content | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.2 R6 verbatim ("engine_config_sha256 ccfb575a…; spec yaml v0.2.3 thresholds DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE; cost atlas v1.0.0 bbe1ddf7…; rollover calendar c6174922…; Bonferroni n_trials=5; latency_dma2_profile, RLP detection, microstructure flags") | **CONFIRMED** verbatim |
| ESC-012 R9 OOS one-shot discipline | ESC-012 §4.2 R9 + Mira spec §15.13.7 verbatim | **CONFIRMED** |
| ESC-012 R10 Gate 5 fence + R15 surprise-PASS council | ESC-012 §4.3 R10 + §4.4 R15 verbatim | **CONFIRMED** |
| ESC-012 §5 Path C fallback triggers | ESC-012 §5 list ("Dara hold-out parquet materialization slip / Mira spec amendment v1.2.0 dispute / F2-T5-OBS-1 fix complications") + 14-day clock | **CONFIRMED** |
| PRR-20260430-1 §3.1-§3.4 4-branch disposition rule | `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` §3 + §4.2 partition; Round 3 §8.1 branch tracing verbatim | **CONFIRMED** verbatim via Round 3 transcription |
| Mira spec v1.2.0 §15.13.2 mechanism block | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` §15.13.2 verbatim per Round 3 §3.1 transcription | **CONFIRMED** |
| F2-T8-T1.1 micro-task scope ~5-10 LoC | Mira Round 3 §11.1 verbatim "Scope: ~5-10 LoC modification to scripts/run_cpcv_dry_run.py:1088-1102 adding a phase == 'G' branch (or extending the --phase choices to include 'G') that flips holdout_locked=False and propagates ic_holdout_status='computed'" | **CONFIRMED** verbatim |
| Beckett N8.1 wall-time projection ~3h | Mira Round 3 §11.2 + Beckett ESC-012 ballot §3 carry-forward | **CONFIRMED** |
| R14 (auditor não audita a si mesmo) preserved this ballot | Sable ballot does NOT include `.claude/agents/squad-auditor.md` in scope; §2 admission is process-self-correction documentation, NOT self-audit verdict | **CONFIRMED** |
| Anti-Article-IV Guards 1-8 preserved both paths | Round 3 §3.2 + §3.3 + §10 + Sable §3.1 + §3.2 trace verbatim | **CONFIRMED** |
| Path (iv) cost ~half-day + ~3h Beckett | Composition: F2-T8-T1.1 micro-task (~5-10 LoC; tests +1 NEW; PR review): ~2-3h Dex + ~half-session reviewer; Beckett N8.1 ~3h; Mira Round 3.1 verdict ~1-2 sessions; Riven 3-bucket Round 3 entry ~half-session; Sable R5.1 + R5.2 audits ~1 session total — sum ~5-7h elapsed time + parallel work | **CONFIRMED** by composition cite to Round 3 §11.1-§11.3 + ESC-012 R8 wall-time invariant + Beckett ESC-012 ballot §3 |

**Article IV self-audit verdict:** every claim in this ballot traces to source artifact cited verbatim. NO INVENTION. Sable preference disclosed §5; Sable scope discipline R14 preserved; Sable does not modify squad-auditor.md or audit own scope-discipline; the §2 admission is documentation of a process gap surfaced post-event by another agent's authority (Mira Round 3 F2-T9-OBS-1), which is the correct R14-compatible audit-self-correction mechanism.

---

## §8 Sable cosign 2026-04-30 BRT

```
Ballot type: ESC-013 council vote — Sable independent ballot
Ballot scope: process-audit-perspective adjudication of Path (iv) protocol-corrected Phase G re-run vs Path C retire
Ballot independence: written without reading peer ESC-013 ballots (per Article IV council protocol + ESC-012 §6 strong-evidence pattern carry-forward)
Ballot authority basis: R14 Sable-squad audit perimeter; R5 ESC-012 audit author; F2-T9-OBS-1 ledger admission

Source artifacts traversed:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Mira Round 3 verdict + F2-T9-OBS-1 surfacing)
  - docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md (Sable R5 prior audit; scope gap §2 admission)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md (R6 / R7 / R9 / R10 / R15 / R16 / R17 / §5 carry-forward)
  - docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md (§3.1-§3.4 4-branch disposition rule)
  - docs/ml/specs/T002-gate-4b-real-tape-clearance.md@v1.2.0 §15.13 (mechanism block + sign-off chain)

Verdict primary: APPROVE_PATH_iv_PROTOCOL_CORRECTED_PHASE_G_RERUN
Verdict secondary fallback: APPROVE_PATH_C if council adopts conservative §15.13.7 one-shot reading

F2-T9-OBS-1 admission: ACKNOWLEDGED — Sable R5 audit scope did not enumerate F2-T8-T1 Dex wiring as standalone pre-N8 prereq; collapsed into R8 envelope; gap surfaced post-N8 by Mira Round 3; severity ⚠️ HIGH (not 🔴 — disposition rule held; INCONCLUSIVE was the disposition-rule-correct verdict route, just procedurally suboptimal); corrective action: future R5-equivalent audits enumerate spec §15.x sign-off chain rows alongside ESC §4 R1-R17

R-rules R1-R15 implications: both paths preserve all R-rules; Path (iv) STRENGTHENS R4 (No Invention) by performing the COMPUTED measurement; Path C preserves R4 at lower-rigor (INCONCLUSIVE-final without surrogate evidence)

Anti-Article-IV Guards 1-8 implications: both paths preserve all guards; Path (iv) STRENGTHENS Guard #8 (ic_holdout_status='computed' propagation) by wiring the propagation that was missing in N8

Personal preference: Path (iv) on audit-trail-rigor + R15-evaluability + precedent grounds; preference disclosed §5; Path C accepted as legitimate alternative under conservative §15.13.7 reading

Recommended conditions if Path (iv) adopted: C-S1..C-S9 process-side additive conditions (§6.1)
Recommended conditions if Path C adopted: C-S1'..C-S5' process-side additive conditions (§6.2)
Common conditions either path: C-S10..C-S12 (§6.3)

Article II preservation: Sable does NOT push; commit + push delegated to Gage @devops at story close per ESC-012 §7 closure conditions + Constitution Article II
Article IV self-audit: every claim in this ballot traces to source artifact cited verbatim §7; NO INVENTION

Out-of-scope explicitly NOT decided by Sable:
  - data-fate (Mira ML statistical authority)
  - architecture micro-task design (Aria authority)
  - run scope (Beckett authority)
  - 3-bucket reclassify (Riven authority)
  - story scope expansion (Pax authority)
  - council ID adjudication (Pax authority — Sable preference re-use ESC-013 for Path (iv) ratification noted §6.1.C-S9 but does not pre-empt)
  - kill / sizing / alpha (Sable does not vote operational-side)

Cosign: Sable @squad-auditor 2026-04-30 BRT — ESC-013 ballot + F2-T9-OBS-1 admission + R5 audit scope corrective action documented for future-audit application.
```

— Sable, o cético do squad 🔍
