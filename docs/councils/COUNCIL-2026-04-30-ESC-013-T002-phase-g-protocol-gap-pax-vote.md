---
council_id: ESC-013
ballot_topic: T002.7 Phase G protocol-compliance-gap adjudication post-Mira F2-T9 INCONCLUSIVE Round 3 (`phase_g_protocol_compliance_gap` sub-classification; N8 surprise DSR=0.965 OOS + IC=0.866 + PBO=0.163 strong evidence; K3 DEFERRED-sentinel-PASS NOT COMPUTED-PASS; PRR-20260430-1 §3.4 INCONCLUSIVE residual branch fired)
voter: Pax (@po — Product Owner)
vote_date_brt: 2026-04-30
ballot_paths:
  - "Path (iv) — Protocol-corrected Phase G proper re-run (N8.1): Aria + Dex micro-fix (~5-10 LoC against scripts/run_cpcv_dry_run.py:1093 wiring --phase G CLI flag flipping holdout_locked=False per Mira spec v1.2.0 §15.13.2 mechanism block) + Beckett N8.1 ~3h wall + Mira F2-T9.1 Round 3.1 verdict against PRR-20260430-1 §3.1-§3.4 + Riven 3-bucket reclassify Round 3 + Quinn QA gate post-Dex fix + Pax cosign close — total ~5-10 squad sessions (~7 mid-estimate)"
  - "Path C — Retire T002 (ESC-012 §5 fallback activates with refined diagnostic phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading; epic deprecated; squad bandwidth freed; ~1-1.5 sessions retire ceremony)"
verdict: PATH_(iv) (preferred — protocol-corrected Phase G proper re-run); PATH_C acceptable fallback IF council majority rules §15.13.7 one-shot consumption binds parquet-read alone
rationale_summary: |
  From product perspective Path (iv) is the continuation of ESC-012 R8 Path B that the council approved 5/6 supermajority — same window, same predictor↔label, same Bonferroni n_trials=5, same engine_config_sha256, same cost atlas, same rollover calendar — with the §15.13.2 unlock-mechanism protocol fix Mira spec v1.2.0 mandates that was assumed in the F2-T8-T1 sign-off chain but not explicitly built at the run-script layer. The N8 DSR=0.965 + IC=0.866 + PBO=0.163 surprise is strong evidence of either (a) genuine OOS-stable signal disambiguating in-sample-vs-OOS regime preservation OR (b) a structural in-sample-IC measurement artifact under the holdout-window CPCV path-PnL — and ONLY a protocol-corrected K3 decay test computing IC_holdout cross-window against IC_in_sample F2 reference can disambiguate which. ~5-10 sessions for the K3 disambiguation is high-leverage spend (asymmetric upside identical to ESC-012 §1.3 reasoning); Path C alone retires WITHOUT extracting the K3 decay evidence the squad has structurally already paid the parquet-materialization cost to obtain. Path (iv) is bounded (single re-run; one binding outcome; no scope expansion permitted), passes 10-point checklist as a sub-fix story (T002.7.1) AND fits more cleanly as absorption inside T002.7 completion (recommended scope decision §2 below). Path C remains the honest fallback IF council majority rules §15.13.7 one-shot consumption binds parquet-read alone (Mira surfaced this question explicitly as council-ratification-mandatory).
spec_yaml_status: NO_MUTATION across both paths (DSR > 0.95 / PBO < 0.5 / IC > 0 thresholds UNMOVABLE per Anti-Article-IV Guard #4 + ESC-011 R14 + ESC-012 R6 reusability invariant; Mira spec v1.2.0 §15.13.2 unlock mechanism is pre-authored not mutation; Phase G protocol fix at run-script layer is implementation-side wiring NOT spec-side relaxation)
authority_basis:
  - "Pax @po — story scope, AC integrity, 10-point checklist guardian"
  - "ESC-011 R10 — successor story authority; Pax adjudicates forward research path"
  - "ESC-012 R3 — PRR-20260430-1 hash-frozen disposition rule binding (4 branches + INCONCLUSIVE residual)"
  - "ESC-012 §1 + 5/6 supermajority APPROVE_PATH_B + 17 conditions (R1-R17) carry-forward"
  - "Mira F2-T9 Round 3 §1 + §3 + §11 — INCONCLUSIVE residual + sub-classification phase_g_protocol_compliance_gap surfaced for ESC ratification"
  - "Mira spec v1.2.0 §15.13.2 unlock mechanism + §15.13.5 decay test full evaluation + §15.13.7 one-shot discipline + §15.13.8 disposition rule"
council_provenance:
  - "ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C (R1-R20 carry-forward)"
  - "ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B (R1-R17 binding conditions; Path B = Phase G hold-out unlock OOS confirmation)"
  - "Pax ESC-012 ballot — PATH_B preferred 1st, PATH_C acceptable fallback 2nd, PATH_A' rejected"
  - "Mira F2-T9 Round 3 sign-off — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` GATE_4_INCONCLUSIVE_pending_phase_g_proper sub `phase_g_protocol_compliance_gap`"
  - "PRR-20260430-1 — `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` §3.4 INCONCLUSIVE branch (ESC escalation; defer to council; cannot pre-empt fate without council ratification)"
article_iv_self_audit: PASS (every claim traces to listed source anchor; no invention; no threshold mutation; no Bonferroni expansion; spec yaml v0.2.3 thresholds preserved; this PR is local-write artifact only — no commit, no push, no spec yaml mute)
cosign: Pax @po — ESC-013 Phase G protocol-gap ballot 2026-04-30 BRT
---

# COUNCIL ESC-013 — Pax Vote: T002.7 Phase G Protocol-Compliance-Gap Adjudication

**Council:** ESC-013 — T002.7 Phase G protocol-compliance-gap adjudication post-Mira F2-T9 Round 3 INCONCLUSIVE
**Voter:** Pax (@po — Product Owner)
**Date (BRT):** 2026-04-30
**Constraint preserved:** spec yaml v0.2.3 thresholds UNMOVABLE (DSR > 0.95 / PBO < 0.5 / IC > 0 / Bonferroni n_trials=5; Anti-Article-IV Guard #4 + ESC-011 R14 + ESC-012 R6)
**Constraint preserved:** Article II Gage @devops EXCLUSIVE push authority
**Constraint preserved:** ESC-012 R6 reusability invariant (engine_config_sha256 + cost atlas v1.0.0 + rollover calendar + predictor↔label semantics IDENTICAL F2)
**Verdict:** **PATH_(iv) preferred (protocol-corrected re-run)** > **PATH_C acceptable fallback** (per §4 hold-out-budget interpretation outcome)

---

## §1 Verdict + rationale (product perspective)

### §1.1 Vote

| Path | Vote | Rank |
|---|---|---|
| **Path (iv)** — Protocol-corrected Phase G proper re-run (N8.1; ~5-10 sessions) | **APPROVE (PREFERRED)** | 1st |
| **Path C** — Retire T002 (ESC-012 §5 fallback; ~1-1.5 sessions) | **APPROVE (FALLBACK)** | 2nd |

### §1.2 Product-perspective rationale

Pax adjudicates ESC-013 from FIVE product-side criteria, building on the ESC-012 framework Pax cosigned 5/6 supermajority APPROVE_PATH_B:

1. **Continuity with ESC-012 R8 mandate** — Path (iv) is NOT a new path. It is the COMPLETION of ESC-012 Path B as 17-condition-binding-mandate written. ESC-012 R6 demands "Phase G run MUST consume IDENTICAL `engine_config_sha256` (`ccfb575a…`) ... Bonferroni n_trials=5 (T1..T5 verbatim) ... NO refinement / no parameter tweak / no Bonferroni expansion / no cost mutation." Path (iv) is COMPLIANT R6 verbatim — the ~5-10 LoC fix in `scripts/run_cpcv_dry_run.py:1093` wiring `--phase G` CLI flag flipping `holdout_locked=False` per Mira spec v1.2.0 §15.13.2 mechanism block is **not a parameter tweak / not a Bonferroni expansion / not a cost mutation / not a threshold mutation** — it is the run-script protocol wiring that the F2-T8-T1 sign-off chain ASSUMED would be in place but was not explicitly built. Mira F2-T9 Round 3 §1 surfaces this as `phase_g_protocol_compliance_gap` because the unlock-mechanism layer was assumed-but-unbuilt; the §15.13.2 spec text was authored BEFORE the run-script wiring was inspected. Path (iv) closes this gap as an **implementation completion of the spec-side R6 contract**, not as a new spec or new scope.

2. **Information yield asymmetry** — N8 produced surprise observations: DSR=0.965 (above 0.95 strict threshold by 0.015), PBO=0.163 (well below 0.5 + below 0.25 ideal), IC=0.866 (n=3700 events × 5 trials × 45 paths). These are **strong evidence** signals — but Mira Round 3 §1 + §3 explicitly classifies the K3 status as **DEFERRED-sentinel-PASS, NOT COMPUTED-PASS**. The N8 IC of 0.866 is in-sample-IC over the holdout-window CPCV path-PnL; it is NOT the K3 decay test (`IC_holdout > 0.5 × IC_in_sample` cross-window per Mira spec v1.2.0 §15.13.5). The decay test was definitionally not performed — N8 measured ONE IC over ONE window; the decay test requires TWO IC values across TWO windows (IC_in_sample from F2 N7-prime in-sample window 2024-08-22..2025-06-30 = 0.866010 AND IC_holdout from Phase G unlock over 2025-07-01..2026-04-21 with `holdout_locked=False` and `ic_holdout_status='computed'`). Path (iv) extracts the K3 disambiguation; Path C forfeits it. Given the squad has already paid the parquet-materialization cost (Dara R4 hold-out tape ~10-20h wall-time), the marginal ~5-10 sessions to extract the K3 cross-window decay evidence is **highest-leverage spend in the entire T002 epic to date**. The information value is asymmetric: the N8 surprise could be (a) genuine OOS-stable signal (in which case T002 advances to Phase H paper-mode planning) OR (b) in-sample-IC measurement artifact under the same predictor↔label binding (in which case T002 retires with maximum-evidentiary-force clean-negative confirmation per Mira §5.3 framing). ONLY the cross-window decay test disambiguates.

3. **Story scope discipline** — Path (iv) fits the §2 story scope decision (recommend absorb inside T002.7 completion as F2-T9.1 sub-cycle; T002.7.1 sub-fix story optional alternative). The scope is BOUNDED: single re-run, identical R6 invariant, single Mira F2-T9.1 verdict against PRR-20260430-1 §3.1-§3.4 4-branch disposition, single Riven reclassify entry, single Pax cosign. No scope expansion, no parameter sweep, no second OOS run. **Path (iv) is bounded; Path C is closure.** Both pass story-discipline test.

4. **AC integrity (10-point checklist)** — Path (iv) AC are all binary-verifiable at draft time:
   - AC1: `--phase G` CLI flag wired in `scripts/run_cpcv_dry_run.py` flipping `holdout_locked=False` per Mira spec v1.2.0 §15.13.2 mechanism block (Aria architectural sign-off + Dex impl + Quinn QA verify)
   - AC2: N8.1 run executed against same holdout parquet (`data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/`) with corrected protocol → produces real IC_holdout for K3 decay test cross-window
   - AC3: Mira F2-T9.1 verdict against PRR-20260430-1 §3.1-§3.4 4-branch disposition rule (R15 PASS / R16 FAIL_K3_collapse / R17 FAIL_K1+K3_sustains / R18 INCONCLUSIVE residual — but residual now requires re-justification post-protocol-fix)
   - AC4: Riven 3-bucket reclassify Round 3.1 entry per outcome
   - AC5: ESC-012 R6 reusability invariant verified (engine_config_sha256 / cost atlas / rollover calendar / Bonferroni n_trials=5 / predictor↔label semantics IDENTICAL F2)
   - AC6: Pax cosign close + Gage push
   All six AC binary-verifiable; passes 10-point checklist 9-10/10. Path (iv) **passes** Pax 10-point gate.

5. **Article IV honesty** — Path (iv) asks the data the falsifying question Mira spec v1.2.0 §15.13.5 was authored to ask: "does IC_holdout (cross-window OOS) preserve > 0.5 × IC_in_sample (cross-window IS reference)?" This is the exact decay test PRR-20260430-1 R15 + R16 + R17 partition was hash-frozen against. Path C accepts INCONCLUSIVE residual as final without extracting the cross-window decay evidence. Both are Article-IV-honest; Path (iv) is **MORE honest** because it completes the falsifying question the §15.13.5 spec text mandates. ESC-012 §1.3 reasoning carries forward: marginal information value of cross-window decay test (~5-10 sessions) is high-leverage relative to small additional spend, given the squad has structurally already invested the parquet-materialization cost.

### §1.3 Why Path (iv) over Path C as primary preference

This is the SAME reasoning Pax applied at ESC-012 §1.3 (Path B over Path C as primary), now applied to the protocol-fix completion of that same Path B mandate. The ESC-012 vote was 5/6 supermajority for Path B because the marginal information value of single OOS run is high relative to small additional spend. ESC-013 reaffirms that vote — the OOS run that ESC-012 R8 approved was supposed to compute the K3 cross-window decay test; it executed against the holdout parquet without the K3 decay measurement at the metric layer. The product-side question is: does the council ratify the protocol fix (extracting the K3 decay evidence the spec mandates) OR does the council retire on a residual technicality (parquet-read-alone consumes the one-shot budget)?

Pax recommends Path (iv) because:
- ESC-012 5/6 supermajority approved Path B = K3 decay disambiguation as the core epistemic deliverable
- The protocol gap is a run-script wiring assumption not a spec mutation
- The K3 cross-window decay evidence is precisely what the squad invested 30+ sessions + Dara R4 parquet materialization to obtain
- Path C forfeits the K3 evidence at the LAST mile after the squad has already paid the squad-bandwidth cost
- §6 and §7 conditions below tightly bound Path (iv) to prevent any scope creep or Bonferroni inflation

### §1.4 Why Path C remains the acceptable fallback

Path C ranks acceptable fallback because IF the council rules §15.13.7 one-shot consumption binds **parquet-read alone** (conservative reading; Mira surfaced this explicitly as council-ratification-mandatory in Round 3 §1), THEN the hold-out budget is structurally consumed and Path (iv) is foreclosed regardless of whether the K3 decay test was actually computed. Pax respects Mira's deference of this reading to council adjudication and votes Path (iv) only IF council majority rules the consumption binds **the K3 decay measurement** (Mira's authoritative reading per Round 3 §1 §3.4 reasoning), NOT parquet-read alone. See §4 below for Pax's authoritative reading of §15.13.7 from PO authority.

---

## §2 Story scope decision

**Recommendation: ABSORB inside T002.7 completion as F2-T9.1 sub-cycle (NOT new T002.8 story; T002.7.1 sub-fix optional alternative if council prefers explicit story-numbering discipline).**

### §2.1 Three story-scope options analyzed

| Option | Mechanism | Pros | Cons | Pax verdict |
|---|---|---|---|---|
| **(A) Absorb inside T002.7** | T002.7 status remains InProgress; F2-T9.1 sub-cycle appended; Aria + Dex protocol fix lands as commit on `t002-7-phase-g-prep` branch; Beckett N8.1 run + Mira Round 3.1 sign-off + Riven reclassify + Pax cosign all under T002.7 banner | Cleanest scope discipline (no new story; inherits T002.7 12 binary AC discipline + ESC-012 R1-R17 binding conditions); minimum process overhead; honors ESC-012 R8 mandate as completion-of-existing-mandate | T002.7 timeline extends ~5-10 sessions beyond original close date; story tracker shows extended InProgress | **PREFERRED** — clean continuity ESC-012 R8 mandate |
| **(B) New T002.7.1 sub-fix story** | T002.7.1 = "Phase G protocol-compliance-gap fix + N8.1 re-run"; minimal story scope (AC1-AC6 from §1.2 above); River @sm draft + Pax 10-point validate ≥ 9/10; T002.7 closes provisionally INCONCLUSIVE pending T002.7.1 outcome; T002.7.1 either flips T002.7 to Done (R15 PASS) or to Done-with-fail-disposition (R16/R17) | Explicit governance trace ("the protocol fix was its own bounded story with sign-offs"); easier audit in retrospective; clear story-tracker status | Process overhead (1 extra River draft + 1 extra Pax validate cycle = ~0.5-1 session vs option A); slightly slower | **ACCEPTABLE** — fallback if council prefers explicit story-numbering |
| **(C) New T002.8 successor story** | T002.8 = full new story superseding T002.7 entirely | Clean separation | **REJECTED** — ESC-012 R8 mandate not yet completed (T002.7 still InProgress per spec contract; no Round 3 verdict that closes T002.7 yet because Round 3 is INCONCLUSIVE residual); creating T002.8 fragments the governance trace and wastes story-numbering discipline | **REJECT** |

### §2.2 Scope IN / OUT discipline (Option A or B)

**Scope IN** (binding under either option A or B):
- (i) Aria architectural review of `--phase G` CLI flag + `holdout_locked=False` parameter wiring (~0.5 session)
- (ii) Dex `scripts/run_cpcv_dry_run.py:1093` micro-fix (~5-10 LoC against existing function signature; Mira spec v1.2.0 §15.13.2 mechanism block trace; ~0.5-1 session impl)
- (iii) Quinn QA gate post-Dex fix (test_phase_g_unlock_mechanism + regression test for Phase F2 default `holdout_locked=True`; ~0.5-1 session)
- (iv) Beckett N8.1 re-run against same holdout parquet with `--phase G` flag (~3h wall + ~1 session analysis)
- (v) Mira F2-T9.1 Round 3.1 sign-off against PRR-20260430-1 §3.1-§3.4 4-branch disposition rule (~1 session)
- (vi) Riven 3-bucket reclassify Round 3.1 entry (~0.5 session)
- (vii) Pax cosign close + Gage push (~0.5 session)

**Scope OUT** (forbidden under either option):
- ANY refinement of strategy logic (entry/exit/regime/conviction/ensemble — explicitly NOT this re-run; ESC-012 R6 reusability invariant)
- Bonferroni n_trials expansion beyond 5 (ESC-012 R6 + ESC-011 R9 carry-forward UNMOVABLE)
- Threshold mutation (DSR > 0.95 / PBO < 0.5 / IC > 0 UNMOVABLE per Anti-Article-IV Guard #4)
- Cost atlas modification (constraint preserved per ESC-012 R6 + user-imposed slippage + cost atlas FIXOS)
- Predictor↔label semantic change (`-intraday_flow_direction` / `ret_forward_to_17:55_pts` IDENTICAL F2 per ESC-012 R7)
- Engine config mutation at runtime (Anti-Article-IV Guard #2)
- ANY new OOS run beyond N8.1 single-shot (post-N8.1 hold-out lock binding regardless of outcome per Mira §15.13.7 + ESC-012 R9)

### §2.3 Pax recommendation

**Option A (absorb inside T002.7) preferred** for clean continuity ESC-012 R8 mandate. **Option B (T002.7.1 sub-fix) acceptable** if council prefers explicit story-numbering for retrospective audit clarity. **Option C (new T002.8) REJECTED** as fragmenting governance trace.

Note: Pax does NOT pre-empt River @sm draft authority. IF council rules Option B, River drafts T002.7.1 with the §2.2 scope IN/OUT discipline + AC1-AC6 from §1.2.4 above + 12 binary AC discipline; Pax then 10-point validates.

---

## §3 Resource allocation per path

### §3.1 Path (iv) resource cost (PREFERRED path)

| Step | Agent | Sessions |
|---|---|---|
| Aria architectural review of protocol fix (CLI flag + `holdout_locked=False` propagation; spec v1.2.0 §15.13.2 mechanism alignment) | Aria | ~0.5 |
| Dex `scripts/run_cpcv_dry_run.py:1093` fix (~5-10 LoC) | Dex | ~0.5-1 |
| Quinn QA gate (test_phase_g_unlock + regression test Phase F2 default; 8-point gate Sable F-01 carry-forward) | Quinn | ~0.5-1 |
| Beckett N8.1 re-run real-tape (~3h wall + analysis report) | Beckett | ~2-3 |
| Mira F2-T9.1 Round 3.1 verdict against PRR §3.1-§3.4 | Mira | ~1 |
| Riven 3-bucket Round 3.1 reclassify entry | Riven | ~0.5 |
| Pax cosign close + 10-point checklist trace | Pax | ~0.5 |
| Sable Phase G coherence audit (R5 carry-forward; ~1 session) | Sable | ~0.5-1 |
| Gage push close ceremony | Gage | ~0.25 |
| **Total** | | **~5-9** |

Conservative ceiling **~10 sessions**. Mid-estimate **~7 sessions**. Compares favorably to ESC-012 §2.2 Path B estimate ~7-10 sessions (Path (iv) is the completion of that same scope; the fix-cost is < 1 session marginal over original Path B because Beckett N8.1 re-uses identical parquet input + identical engine config + identical Bonferroni n_trials=5).

### §3.2 Path C resource cost (FALLBACK path)

ESC-012 §5 already defines this; ESC-013 ratification adds nothing new:

| Step | Agent | Sessions |
|---|---|---|
| Pax cosign Status Done on T002.7 with refined diagnostic `phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading` | Pax | ~0.25 |
| Riven 3-bucket post-mortem final entry: `costed_out_edge_in_sample_only_under_strict_K1` (refined per ESC-013 disposition) | Riven | ~0.5 |
| Epic T002 status update (deprecated; reasoning anchored to Mira F2-T9 Round 3 + ESC-013 ruling) | Pax + River | ~0.25 |
| Memory rotation (project_algotrader_t002_state.md final) | Pax | ~0.25 |
| Gage push close ceremony | Gage | ~0.25 |
| **Total** | | **~1-1.5** |

### §3.3 Comparative table

| Path | Sessions | K3 disambiguation extracted | Spec yaml mutation | Bandwidth defer to H_next |
|---|---|---|---|---|
| Path (iv) | ~5-10 | YES (cross-window decay test computed) | NONE (R6 reusability invariant) | DEFERS ~5-10 sessions |
| Path C | ~1-1.5 | NO (forfeited) | NONE | FREES bandwidth immediately |

### §3.4 Marginal-cost reasoning

The fix-cost is structurally LOW because:
- Parquet already materialized (Dara R4 sunk cost; ~10-20h wall-time)
- Engine config sha256 frozen (`ccfb575a…`; ESC-012 R6)
- Bonferroni n_trials=5 frozen
- Cost atlas frozen
- Rollover calendar frozen
- Predictor↔label binding frozen (ESC-012 R7)
- Beckett N8.1 wall-time is identical to N8 (~3h) — single-shot regression

The **only new artifact** is the ~5-10 LoC protocol fix in `scripts/run_cpcv_dry_run.py:1093`. Everything else is reuse of N8 inputs. Marginal cost is dominated by Mira Round 3.1 sign-off + Riven reclassify + Pax cosign cycle (~3-4 sessions). This is consistent with ESC-012 §2.2 mid-estimate ~7 sessions for Path B.

---

## §4 Hold-out budget interpretation (data engineering vs scientific consumption)

This is the **central ambiguity** Mira F2-T9 Round 3 §1 surfaced for council ratification: does §15.13.7 ESC-012 R9 OOS one-shot discipline ("the hold-out window collapses to a single committed measurement") bind:

- **(a) parquet-read alone** (conservative reading; data-engineering interpretation; hold-out tape consumed at the I/O layer regardless of metric computation) → Path C activates
- **(b) K3 decay measurement** (Mira authoritative reading; scientific-consumption interpretation; hold-out tape consumed at the binding-metric layer when the K3 cross-window decay test is computed) → Path (iv) authorized

### §4.1 Pax reading from PO authority

**Pax rules: §15.13.7 binds the K3 decay MEASUREMENT, NOT the parquet-read alone.**

Reasoning:

1. **Spec text §15.13.5 + §15.13.7 trace** — §15.13.5 defines the canonical K3 decay test as "IC_holdout > 0.5 × IC_in_sample (full evaluation)". §15.13.7 ESC-012 R9 reads "the hold-out window collapses to a single committed measurement." The "single committed measurement" is the K3 cross-window decay TEST per the §15.13.5 definition — NOT the I/O-layer parquet read. This reading is consistent with the rest of §15.13 mechanism block which treats the K3 decay as the binding metric.

2. **Spec authoring intent** — the §15.13 unlock mechanism block was authored under ESC-012 R2 spec amendment v1.1.0 → v1.2.0 to formalize the Phase G OOS unlock procedure. The procedure is explicitly the K3 decay test at the metric layer; the parquet-read is an I/O prerequisite NOT the binding measurement. If parquet-read alone consumed the hold-out budget, the spec would say so explicitly — it does not. The §15.13.5 + §15.13.7 conjunction names the K3 decay test as the binding measurement.

3. **PRR-20260430-1 disposition rule alignment** — PRR §3.1 R15 trigger requires `K3_decay COMPUTED-PASS`, not `K3_decay DEFERRED-sentinel-PASS`. PRR §3.2 R16 + §3.3 R17 require IC_holdout cross-window measurements. PRR §3.4 INCONCLUSIVE branch fires "ESC escalation; defer to council; cannot pre-empt fate without council ratification." The PRR was hash-frozen ESC-012 R3 against the K3 decay measurement at the metric layer — NOT against parquet-read consumption. Reading §15.13.7 as binding parquet-read alone would render PRR §3.4 INCONCLUSIVE branch nonsensical (because the council would have nothing to adjudicate; the budget would be auto-consumed).

4. **Article IV honesty** — the K3 decay test was the canonical Phase G epistemic deliverable. Reading §15.13.7 as binding parquet-read alone would let a structurally invalid protocol (run-script forcing `holdout_locked=True` against the spec §15.13.2 mechanism intent) consume the budget WITHOUT producing the binding measurement. This is the opposite of Article IV honesty — it would let an implementation gap (assumed-but-unbuilt unlock wiring) extinguish the ESC-012 5/6 supermajority APPROVE_PATH_B mandate.

5. **First-attempt principle** — Mira Round 3 §1 explicitly notes "this is the *first attempt* at Phase G and no statistical re-do of OOS results has occurred." A protocol-fix re-run is NOT a Bonferroni-inflating re-run with adjusted parameters; it is the **first valid execution** of the §15.13.2 mechanism. ESC-012 R9 prohibits "re-run with adjusted parameters" — Path (iv) re-run uses IDENTICAL parameters (R6 reusability invariant; ESC-012 R7 predictor↔label IDENTICAL F2; Bonferroni n_trials=5 IDENTICAL). The protocol fix is at the run-script wiring layer, not the spec-parameter layer.

### §4.2 Conservative-reading respected

Pax acknowledges the conservative reading (parquet-read alone consumes one-shot) is defensible — it is the most stringent possible interpretation of "single committed measurement" and would foreclose Path (iv) on the most-protective grounds. Pax votes Path (iv) preferred under the authoritative reading (§4.1.1-5) but defers to council majority IF the council rules conservative; in that case Path C activates per §1.4.

### §4.3 Implication for spec amendment

IF Path (iv) is authorized, Pax recommends Mira spec v1.2.0 → v1.2.1 patch revision (append-only per §15 discipline) clarifying §15.13.7 explicitly:

> "§15.13.7 (clarified Round 3.1): The hold-out window one-shot consumption binds the K3 cross-window decay measurement (the canonical OOS metric per §15.13.5), NOT the parquet I/O read alone. A protocol-corrected re-run that computes the K3 decay test for the FIRST time against the same hold-out parquet is consistent with §15.13.7 because no prior K3 decay measurement has occurred. This clarification is non-mutative of thresholds (DSR > 0.95 / PBO < 0.5 / IC > 0 UNMOVABLE per Anti-Article-IV Guard #4)."

This patch is implementation-side wiring of the spec-side mechanism intent — NOT spec mutation. Mira spec authority owns this amendment.

---

## §5 Backlog prioritization

### §5.1 Path (iv) backlog impact

Path (iv) defers H_next research by ~5-10 sessions (mid-estimate ~7). Compared to ESC-012 §3 analysis where Path B was estimated 7-10 sessions, the marginal incremental over Path B is ~0 sessions because Path (iv) IS the completion of Path B. The K3 disambiguation evidence Path (iv) extracts is the **definitive** answer to the T002 epic question — either:
- (a) `R15 PASS_oos_confirmed` → T002 advances to Phase H paper-mode planning (T002.8 future story); ESC-013 escalation NOT required (R15 branch action explicitly states "ESC-013 council convene to adjudicate K1 strict bar interpretation under OOS surprise PASS" — but this is the PRR-20260430-1 R15 branch, not ESC-013 itself; the ESC-013 ratification authorizing Path (iv) closes ESC-013)
- (b) `R16 FAIL_K3_collapse` → T002 retire ceremony with **strongly evidenced** clean-negative confirmation (in-sample IC=0.866 + OOS K3 collapse cross-window — the most evidentiary-force retirement possible); audit trail complete; future-Pax-friendly post-mortem
- (c) `R17 FAIL_K1+K3_sustains` → T002 retire ceremony with refined `costed_out_edge_oos_confirmed` diagnostic (signal real OOS-stable but cost-foreclosed); institutional knowledge documented for H_next research direction
- (d) Residual INCONCLUSIVE again (low probability under protocol-corrected re-run because the K3 decay test will be COMPUTED-PASS or COMPUTED-FAIL, not DEFERRED-sentinel) → re-escalate

In ALL outcomes (a)-(c), T002 reaches definitive disposition — the K3 disambiguation evidence is the **highest-leverage spend** in the entire T002 epic to date because it converts INCONCLUSIVE to either PASS or one of two clearly-classified FAILs.

### §5.2 Path C backlog impact

Path C frees ~5-10 sessions immediately for H_next research. The trade-off: T002 retires WITHOUT extracting the K3 cross-window decay evidence the squad has structurally already paid the parquet-materialization cost to obtain. The retire-diagnostic becomes `phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading` — informative but less evidentiary-force than R16/R17 outcomes under Path (iv).

### §5.3 Backlog priority post-vote (Pax recommendation conditional on Path (iv))

If Path (iv) passes ESC-013:

1. **T002.7 (Option A) OR T002.7.1 (Option B)** — Phase G protocol-corrected re-run; ~5-10 sessions; absorption inside T002.7 (Option A) preferred by Pax §2.3
2. **T002.5** — telemetria + EOD reconciliation (resume planned work; can run in parallel if squad has capacity; pre-Gate-5 dependency)
3. **F2-T9.1 sequenced after Aria + Dex + Quinn protocol fix completion**

If Path (iv) fails ESC-013 / council rules conservative §15.13.7 reading: pivot to Path C (clean retirement); H_next research bandwidth freed immediately.

### §5.4 Carry-forward Pax ESC-012 §3 reasoning

Pax ESC-012 ballot §3 cited backlog candidates "T002.5 telemetria; alternative alphas; paper-mode integration; risk infrastructure hardening" as the alternative spend if Path A' had passed ($48-session burn). ESC-013 Path (iv) at ~5-10 sessions is **2 orders of magnitude cheaper** than that hypothetical Path A' burn — backlog impact is minor by comparison. The §3.5 ESC-012 reasoning ("Path B does not meaningfully delay backlog work") carries forward to ESC-013 Path (iv).

---

## §6 Personal preference disclosure

Pax discloses personal preference per autonomous mode council protocol:

### §6.1 Preference (a) — Continuity with ESC-012 5/6 supermajority APPROVE_PATH_B

Path (iv) IS the completion of Path B. Voting Path C in ESC-013 would partially nullify the ESC-012 5/6 supermajority decision the squad ratified just hours earlier. Council fidelity demands continuity unless new evidence FUNDAMENTALLY changes the calculus. The protocol-compliance-gap is NOT new evidence about the strategy or the spec — it is an implementation-side wiring assumption gap that Mira F2-T9 Round 3 explicitly surfaces as fixable. **Preference (a) ranks: (iv) > C.**

### §6.2 Preference (b) — Maximum information per session invested

Path (iv) yields cross-window K3 decay evidence per ~5-10 sessions = high information density. Path C yields zero new information for ~1-1.5 sessions = density undefined. The same ESC-012 §6.1 reasoning carries forward. **Preference (b) ranks: (iv) > C.**

### §6.3 Preference (c) — Article IV honesty

Path (iv) asks the K3 decay falsifying question Mira spec v1.2.0 §15.13.5 was authored to ask. Path C accepts INCONCLUSIVE residual without extracting the K3 evidence. Both honest; Path (iv) MORE honest because it completes the falsifying question. **Preference (c) ranks: (iv) > C.**

### §6.4 Preference (d) — Backlog discipline

Path C frees bandwidth immediately. Path (iv) defers ~5-10 sessions. ESC-012 Pax ballot §6.2 ranked Path C ahead of Path B on this preference dimension; the same applies in ESC-013. **Preference (d) ranks: C > (iv).**

### §6.5 Aggregated preference

- Path (iv): ranks 1st on (a), (b), (c); 2nd on (d) → average rank 1.25
- Path C: ranks 2nd on (a), (b), (c); 1st on (d) → average rank 1.75

Path (iv) wins 3-of-4 preferences. The marginal information value reasoning (§1.3 + §3.4 marginal-cost) tips the balance further toward (iv) as primary, with C as fallback if §15.13.7 is read conservatively (§4.2).

### §6.6 Preference disclosure declaration

Pax preference does NOT override product-criteria adjudication; it serves as tie-breaker after spec/scope/AC/Article IV criteria are applied. The §1 vote (Path (iv) preferred, Path C fallback) is supported by both criteria-based reasoning AND personal-preference aggregation. No preference-vs-criteria conflict.

---

## §7 Recommended conditions

If Path (iv) passes ESC-013 council, Pax recommends the following binding conditions on the protocol-fix completion:

### §7.1 Story scope discipline (Pax + River authority)

- **C1** — Story scope per §2.3: Option A (absorb inside T002.7) preferred; Option B (T002.7.1 sub-fix) acceptable if council prefers explicit numbering. Option C (new T002.8) REJECTED.
- **C2** — Scope IN per §2.2.IN (i)-(vii): Aria review + Dex protocol fix + Quinn QA + Beckett N8.1 + Mira F2-T9.1 + Riven reclassify + Pax cosign + Sable audit + Gage push.
- **C3** — Scope OUT per §2.2.OUT: NO refinement / NO Bonferroni expansion / NO threshold mutation / NO cost atlas mutation / NO predictor↔label change / NO engine config mutation / NO second OOS run beyond N8.1.
- **C4** — Pax 10-point checklist must reach ≥9/10 before Beckett N8.1 begin (carry-forward ESC-012 R13 + §1.2.4 binary-AC discipline).

### §7.2 Spec amendment (Mira authority)

- **C5** — Mira spec v1.2.0 → v1.2.1 patch revision clarifying §15.13.7 per §4.3 above (append-only revision per §15 discipline; thresholds preserved verbatim; Anti-Article-IV Guard #4 UNMOVABLE).
- **C6** — Mira spec v1.2.0 §15.13.2 unlock-mechanism block confirmed binding for N8.1 protocol; Aria + Dex implementation traces to spec text exactly.

### §7.3 Run discipline (carry-forward ESC-012 R6-R9)

- **C7** — N8.1 MUST consume IDENTICAL `engine_config_sha256` (`ccfb575a…`), Bonferroni n_trials=5, cost atlas v1.0.0, rollover calendar, predictor↔label binding F2 IDENTICAL. NO refinement / NO parameter tweak / NO Bonferroni expansion / NO cost mutation. (ESC-012 R6 verbatim.)
- **C8** — N8.1 Predictor↔label semantics IDENTICAL F2 (`-intraday_flow_direction` / `ret_forward_to_17:55_pts`; paired-resample bootstrap n=10000 PCG64 seed=42 per spec §15.4). (ESC-012 R7 verbatim.)
- **C9** — N8.1 wall-time projection ~3h same as N8; engine_config v1.2.0 perf optimization OPTIONAL. (ESC-012 R8 verbatim.)
- **C10** — N8.1 single-shot binding regardless of outcome; CANNOT be re-run with adjusted parameters. The protocol-corrected re-run IS the first valid §15.13.2 mechanism execution per Mira Round 3 §1 + §4.1.5 above. (ESC-012 R9 + §4.1 reading.)

### §7.4 Verdict + governance (carry-forward ESC-012 R10-R14 + new ESC-013 conditions)

- **C11** — Gate 5 fence preservation. N8.1 PASS does NOT pre-disarm Gate 5. Gate 5 capital ramp dual-sign requires K1+K2+K3 ALL COMPUTED-PASS + paper-mode Phase G/H. K1 strict bar (DSR>0.95) UNMOVABLE per Anti-Article-IV Guard #4. (ESC-012 R10 verbatim.)
- **C12** — Mira F2-T9.1 Round 3.1 verdict authority preserved (supersedes Round 3 INCONCLUSIVE residual; Round 3 + Round 2 sign-off integrity preserved per spec §15 append-only revision discipline; Round 3.1 authoritative).
- **C13** — Riven 3-bucket Round 3.1 reclassify entry per outcome (R15 PASS / R16 FAIL_K3_collapse / R17 FAIL_K1+K3_sustains).
- **C14** — Sable Phase G coherence audit Round 3.1 (single audit pass; verify protocol fix + spec amendment v1.2.1 + reusability invariants). (ESC-012 R5 carry-forward.)
- **C15** — Quinn QA F2-T9.1 gate post-Aria + Dex protocol fix; standard 8-point gate (Check 8 NEW Sable F-01 procedural fix retained). (ESC-012 R14 verbatim.)
- **C16** — PRR-20260430-1 §3.1-§3.4 4-branch disposition rule binding for Round 3.1 verdict; INCONCLUSIVE residual MUST re-escalate to ESC-014 (low probability under protocol-corrected re-run because K3 decay will be COMPUTED-PASS or COMPUTED-FAIL not DEFERRED-sentinel; but contingency preserved).

### §7.5 Outcome decision tree (carry-forward ESC-012 R15-R17)

- **C17** — N8.1 R15 outcome (`PASS_oos_confirmed`; cross-window decay IC_holdout > 0.5 × IC_in_sample = 0.433005 strict; K1+K2+K3 ALL COMPUTED-PASS): unlock Phase H paper-mode planning (T002.8 future story); ESC-012 R15 escalation trigger to ESC-013-followup council convene to adjudicate K1 strict bar interpretation under OOS surprise PASS (Aria + Mira + Riven + Pax + Sable + Kira). (ESC-012 R15 verbatim.)
- **C18** — N8.1 R16 outcome (`FAIL_K3_collapse`; IC_holdout < 0.3): T002 hypothesis falsified clean per spec §0; Riven 3-bucket reclassify N8.1 → `strategy_edge` clean negative; T002 retire ceremony; epic deprecate; squad bandwidth freed. (ESC-012 R16 verbatim.)
- **C19** — N8.1 R17 outcome (`FAIL_K1+K3_sustains`; IC_holdout ∈ [0.3, 0.5 × IC_in_sample) AND DSR_OOS < 0.95): costed_out_edge OOS-confirmed; T002 retire ceremony with refined diagnostic (signal real OOS-stable but cost-foreclosed); Riven 3-bucket reclassify N8.1 → `costed_out_edge_oos_confirmed`; institutional knowledge documented for H_next research. (ESC-012 R17 verbatim.)
- **C20** — N8.1 INCONCLUSIVE residual outcome (low probability post-protocol-fix; reserved): ESC-014 convene; reconsider whether spec §15.13 mechanism block requires further amendment OR whether T002 retire is the residual answer.

### §7.6 Article II push gate (carry-forward)

- **C21** — Gage @devops EXCLUSIVE push authority preserved. Pax authoring vote document only. No commit / no push performed by Pax during ESC-013 ballot.

---

## §8 Article IV self-audit

Per Constitutional Article IV (No Invention) + AIOX framework Article IV enforcement (every claim source-anchored):

| Claim category | Trace anchor |
|---|---|
| N8 surprise observations DSR=0.965 / IC=0.866 / PBO=0.163 | Mira Round 3 §2 + `data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/full_report.json:3-9` |
| K3 status DEFERRED-sentinel-PASS not COMPUTED-PASS | Mira Round 3 §3 + `packages/vespera_metrics/report.py:760-781` (Dex `fadacf4` OBS-1 fix) + `full_report.json:257` |
| `holdout_locked=True` hardcoded `scripts/run_cpcv_dry_run.py:1093` | Mira Round 3 §1 (run-script protocol violation) |
| Mira spec v1.2.0 §15.13.2 unlock mechanism + §15.13.5 decay test + §15.13.7 one-shot + §15.13.8 disposition | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md@v1.2.0` |
| PRR-20260430-1 §3.1-§3.4 4-branch disposition rule | `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` |
| ESC-012 R1-R17 binding conditions (especially R6 reusability invariant + R7 predictor↔label IDENTICAL F2 + R8 wall-time ~3h + R9 single-shot + R10 Gate 5 fence) | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4 |
| ESC-012 5/6 supermajority APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §1 + 6 ballot files |
| Pax ESC-012 ballot PATH_B preferred + 16 conditions C1-C16 | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-pax-vote.md` |
| Spec yaml v0.2.3 thresholds DSR > 0.95 / PBO < 0.5 / IC > 0 UNMOVABLE | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` v0.2.3 L207-209 + Anti-Article-IV Guard #4 + ESC-011 R14 |
| Bonferroni n_trials=5 anchor `docs/ml/research-log.md@c84f7475` | ESC-011 R9 + ESC-012 R6 |
| Hold-out window 2025-07-01..2026-04-21 single-shot canonical OOS | Mira spec v1.2.0 §15.13.7 + ESC-012 R9 + parent yaml `data_splits.hold_out_virgin` |
| F2 N7-prime in-sample reference IC=0.866010 over 2024-08-22..2025-06-30 | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §5.1 + Mira Round 3 §2 table row K3 IS column |
| 10-point checklist (PO authority) | `.aiox-core/development/tasks/validate-next-story.md` + AIOX framework `story-lifecycle.md` rules |
| Article II Gage @devops exclusive push | `.claude/rules/agent-authority.md` Delegation Matrix |

**Self-audit verdict:** every claim in §1-§7 traces to a verifiable source (Mira Round 3 sign-off / PRR-20260430-1 / ESC-011 + ESC-012 resolutions / Pax ESC-012 ballot / Mira spec v1.2.0 / parent spec yaml / N8 full_report.json / framework rules). NO INVENTION. NO threshold relaxation proposed by Pax (threshold mutation rejected as a vector under both paths via §7.3 C7 + Anti-Article-IV Guard #4 preserved). NO Bonferroni expansion proposed by Pax. NO hold-out modification proposed by Pax (Path (iv) re-run is FIRST valid §15.13.2 mechanism execution per §4.1 reading; protocol-fix is run-script wiring of pre-authored spec mechanism intent NOT spec mutation). NO Round 1 / Round 2 / Round 3 sign-off mutation (Round 3.1 supersedes via append-only revision per spec §15 discipline). NO source code modification by Pax during ballot. NO commit / push performed by Pax during this vote. NO spec yaml mute by Pax during ballot.

### §8.1 Anti-Article-IV Guard cross-check

| Guard | Pax vote action | Compliance |
|---|---|---|
| #1 Dex impl gated em Mira spec PASS | Pax does NOT authorize new impl directly; Path (iv) impl gated em Aria architectural review + Mira spec v1.2.1 patch (if amendment authored) + Quinn QA gate | PRESERVED |
| #2 NO engine config mutation at runtime | C7 explicitly forbids engine config mutation | PRESERVED |
| #3 NO touch hold-out lock | Path (iv) uses Mira spec v1.2.0 §15.13.2 pre-authored unlock mechanism; protocol-fix wires what was assumed-but-unbuilt; NOT mutation per §4.1.2 reading | PRESERVED |
| #4 Gate 4 thresholds UNMOVABLE | Pax explicitly preserves DSR > 0.95 / PBO < 0.5 / IC > 0 across both paths (C7 verbatim) | PRESERVED |
| #5 NO subsample backtest run | C3 explicitly forbids second OOS run beyond N8.1 single-shot | PRESERVED |
| #6 NO Gate 5 disarm sem Gate 4a + Gate 4b BOTH | Pax preserves R10 fence (C11) | PRESERVED |
| #7 NO push (Gage EXCLUSIVE) | Pax authoring vote document only; no commit/push performed | PRESERVED |
| #8 Verdict-issuing protocol (`*_status` provenance) | Path (iv) Round 3.1 verdict will exercise Guard #8 fully (OOS channel `ic_holdout_status='computed'` + decay-clause now COMPUTED under Phase G proper) | PRESERVED forward |

All 8 guards preserved by Pax vote.

---

## §9 Pax cosign

```
Author: Pax (@po — Product Owner) — story scope, AC integrity, 10-point checklist guardian
Council: ESC-013 — T002.7 Phase G protocol-compliance-gap adjudication post-Mira F2-T9 Round 3 INCONCLUSIVE
Date (BRT): 2026-04-30
Branch: t002-1-bis-make-backtest-fn (Pax authoring; no commit/push performed)
Verdict: PATH_(iv) preferred (protocol-corrected Phase G proper re-run; ~5-10 sessions; T002.7 absorption Option A preferred per §2.3) > PATH_C acceptable fallback (~1-1.5 sessions; activates IF council majority rules conservative §15.13.7 reading per §4.2)
Rationale: Path (iv) is COMPLETION of ESC-012 5/6 supermajority APPROVE_PATH_B mandate (R8 N8 run was supposed to compute K3 cross-window decay test; ran as F2 protocol against holdout-window parquet because run-script forced holdout_locked=True; decay test definitionally not performed). Mira F2-T9 Round 3 surfaces this as `phase_g_protocol_compliance_gap` sub-classification of GATE_4_INCONCLUSIVE_pending_phase_g_proper. Protocol fix is ~5-10 LoC at run-script wiring layer (NOT spec mutation; spec v1.2.0 §15.13.2 mechanism block already authored). Marginal cost ~5-10 sessions over original ESC-012 Path B estimate is ~0 sessions because parquet already materialized (Dara R4 sunk cost) + engine config sha256 frozen + Bonferroni n_trials=5 frozen + cost atlas frozen + rollover calendar frozen + predictor↔label binding frozen — only new artifact is the protocol-fix wiring. K3 cross-window decay disambiguation is the highest-leverage spend in T002 epic to date because it converts INCONCLUSIVE residual to definitive PRR §3.1-§3.3 disposition (R15 PASS / R16 FAIL_K3_collapse / R17 FAIL_K1+K3_sustains). Path C remains acceptable fallback IF council rules §15.13.7 one-shot consumption binds parquet-read alone (Mira surfaced this for council ratification per Round 3 §1 §3.4); Pax authoritative reading from PO + spec text + PRR alignment + Article IV honesty + first-attempt principle (§4.1.1-5) rules §15.13.7 binds K3 decay MEASUREMENT not parquet-read alone, but defers to council majority. Story scope decision: ABSORB inside T002.7 (Option A preferred §2.3; T002.7.1 sub-fix Option B acceptable; new T002.8 REJECTED). Hold-out budget interpretation: K3 decay measurement binding (§4.1 authoritative); §15.13.7 patch revision v1.2.1 recommended for spec append-only clarification. Backlog impact ~5-10 sessions defer to H_next (minor; 2 orders of magnitude cheaper than hypothetical Path A' ESC-012 §3 burn). 21 binding conditions §7 C1-C21 carry-forward + extend ESC-012 R1-R17 + add §15.13.7 patch (C5).
Article II: NO push performed by Pax during vote authoring. Gage @devops authority preserved.
Article IV: every clause §1-§8 traces to verifiable anchor (Mira Round 3 sign-off / PRR-20260430-1 / ESC-011 + ESC-012 resolutions / Pax ESC-012 ballot / Mira spec v1.2.0 / parent yaml / N8 full_report.json / framework rules). NO invention; NO threshold mutation proposed (Anti-Article-IV Guard #4 explicitly preserved); NO Bonferroni expansion proposed (R6 + R9 carry-forward); NO hold-out modification proposed (Path (iv) re-run is FIRST valid §15.13.2 mechanism execution per Mira Round 3 §1 + §4.1.5 reading; protocol-fix is run-script wiring of pre-authored spec mechanism intent NOT spec mutation); NO source code modification by Pax during ballot; NO commit / push performed by Pax during this vote; NO spec yaml mute by Pax during ballot.
Anti-Article-IV Guards #1-#8: all preserved per §8.1 cross-check.
Authority boundary: Pax issues this strategy-fate ESC-013 ballot; does NOT pre-empt River @sm draft authority over T002.7.1 sub-fix (if Option B chosen) or T002.7 absorption update (if Option A chosen); does NOT pre-empt Aria architectural review authority over CLI flag wiring; does NOT pre-empt Dex impl authority over `scripts/run_cpcv_dry_run.py:1093` fix; does NOT pre-empt Quinn QA gate authority over post-Dex regression test; does NOT pre-empt Beckett N8.1 run authority; does NOT pre-empt Mira F2-T9.1 Round 3.1 verdict authority; does NOT pre-empt Mira spec v1.2.0 → v1.2.1 amendment authority (if §15.13.7 clarification authored); does NOT pre-empt Riven 3-bucket Round 3.1 reclassify authority; does NOT pre-empt Sable governance audit authority; does NOT pre-empt Gage push authority. Pax exercises ESC-011 R10 forward-research adjudication authority + 10-point checklist guardian authority + spec scope discipline authority + backlog prioritization authority + ESC-012 R13 successor-story discipline authority.
Council fidelity: ESC-011 5/5 + ESC-012 5/6 supermajority ratification preserved (R1-R20 + R1-R17 ALL carry-forward; particularly R5/R6 fence + R9 Bonferroni n_trials=5 + R10 successor authority + R14 threshold UNMOVABLE + R20 post-mortem audit + ESC-012 R6 reusability invariant + R8 wall-time + R9 single-shot binding). Mira Round 3 INCONCLUSIVE residual authority preserved (Pax does NOT supersede Mira verdict; Pax adjudicates protocol-fix authorization conditional on §15.13.7 reading per Mira §1 §3.4 deferral to council).
Spec yaml status: NO MUTATION proposed by Pax under either path. Path (iv) authorizes Mira spec v1.2.0 → v1.2.1 patch revision (§15.13.7 clarification per §4.3 above; thresholds preserved verbatim; append-only revision per §15 discipline); parent spec yaml v0.2.3 thresholds at L207-209 UNMOVABLE Round 3.1 forward.
Round 1 / Round 2 / Round 3 sign-off integrity: PRESERVED (no overwrite; Round 3.1 supersedes Round 3 only IF Path (iv) executes and produces new verdict; supersession via append-only revision per spec §15 discipline).
F2-T5-OBS-1 Dex follow-up (Mira spec §4.5 + §8.2 short-circuit): already landed Dex `fadacf4` per Mira Round 3 §1 (verdict-layer K3 status field reports K3: DEFERRED — ic_holdout_status='deferred'); ESC-013 protocol fix is independent-and-additive at run-script `scripts/run_cpcv_dry_run.py:1093` wiring layer.

Cosign: Pax @po 2026-04-30 BRT — ESC-013 Phase G protocol-compliance-gap ballot under autonomous mode.
```

---

— Pax @po, 2026-04-30 BRT — ESC-013 T002.7 Phase G protocol-compliance-gap ballot.
