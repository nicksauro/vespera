# Council ESC-013 — T002 Phase G Protocol-Compliance-Gap Resolution (5/5 UNANIMOUS APPROVE_PATH_IV)

> **Date (BRT):** 2026-04-30
> **Trigger:** Mira F2-T9 Round 3 INCONCLUSIVE_phase_g_protocol_compliance_gap — N8 ran `--phase F` not `--phase G` proper; K3 DEFERRED-sentinel não COMPUTED. PRR-20260430-1 §3.4 INCONCLUSIVE branch escalation.
> **Authority:** Mini-council 5-vote (Mira already issued technical verdict; her input via verdict file)
> **Article II preserved:** No push during deliberation.
> **Article IV preserved:** Independent ballots — verified per ballot self-audit (Beckett/Riven/Aria/Pax/Sable did NOT read peer ballots before writing own).
> **Author:** @aiox-master orchestration capacity, autonomous mode.

---

## 1. Outcome

**RATIFIED: APPROVE_PATH_IV — Protocol-corrected Phase G proper re-run** (Dex caller wiring fix `holdout_locked=False` + `--phase G` CLI flag → Beckett N8.1 ~3h → Mira F2-T9.1 Round 3.1 verdict COMPUTED).

5/5 UNANIMOUS:

| Voter | Authority | Verdict | Key insight |
|---|---|---|---|
| Beckett (@backtester) | Empirical/simulator | **APPROVE_PATH_IV** | P(definitive verdict | Path iv) ≈ 95%; P(definitive | Path C) = 0%; Path C forfeits hold-out forever. |
| Riven (@risk-manager) | Risk custodial | **APPROVE_PATH_IV** | Bayesian update post-N8: prior P(R15) 0.10 → posterior 0.27. ESC-012 Path C minority disclosed; flips on N8 evidence. |
| Aria (@architect) | Architecture | **APPROVE_PATH_IV** | Refinement of Path B (not new path). 5-10 LoC scripts + 30-50 LoC tests; zero spec mutation; Phase G unlock pre-authored §15.13.2. |
| Pax (@po) | Story scope | **APPROVE_PATH_IV** | Hold-out budget interpretation: §15.13.7 binds K3 decay MEASUREMENT (cross-window IC ratio), NOT parquet read. Story absorption inside T002.7 as F2-T9.1 sub-cycle. |
| Sable (@squad-auditor) | Process audit | **APPROVE_PATH_IV** + F2-T9-OBS-1 ADMISSION | R5 audit scope did not enumerate F2-T8-T1 Dex wiring as standalone pre-N8 prereq; collapsed into R8 envelope. HIGH severity (audit gap), corrective action in §6. |

Path C SECONDARY ACCEPTED 5/5 (minority fallback IF council reads §15.13.7 as parquet-read-as-consumption strict — Riven 14-day fallback trigger).

---

## 2. Convergence basis

5 voters arrived independently at Path IV via DIFFERENT authority lenses:

| Voter | Authority lens | Convergence reasoning |
|---|---|---|
| Beckett | Empirical | Verdict-vs-reason inconsistency in N8 full_report.json (verdict K3 PASS; reason text "DEFERRED — pending Phase G unlock") confirms Mira INCONCLUSIVE — N8.1 first swing at Phase G, not second |
| Riven | Risk-side Bayesian | DSR=0.965 OOS observed PASS forces posterior update from ESC-012 priors; informational density of N8.1 high |
| Aria | Architecture | Path G unlock mechanism PRE-AUTHORED in `cpcv_aggregator.py:251-309` (single boolean flip per Mira spec §15.13.2); flipping a flag is procedural completion, not mutation |
| Pax | Product/scope | §15.13.7 one-shot binds K3 decay metric (canonical cross-window IC ratio per §15.13.5), NOT parquet read; first-attempt principle |
| Sable | Process | F2-T9-OBS-1 admission requires closing audit gap definitively; Path C closes T002 with INCONCLUSIVE-on-record (less rigorous than COMPUTED-FAIL) |

The convergence on `§15.13.7 one-shot binds K3 measurement, NOT parquet read` is a SPEC INTERPRETATION ratification — 5/5 voters via different reasonings reached same reading.

---

## 3. F2-T9-OBS-1 admission (Sable + ratified)

Sable openly acknowledges R5 audit scope gap: F2-T8-T1 Dex wiring task per Mira spec v1.2.0 §15.13.12 sign-off chain was IMPLICIT but NOT explicitly enumerated em pre-N8 R5 coherence audit. Effect: caller hardcoded `holdout_locked=True` survived to N8 invocation, producing PHASE-F-PROTOCOL N8 sobre PHASE-G WINDOW.

**Severity:** ⚠️ HIGH (not CRITICAL — disposition rule held; INCONCLUSIVE was the procedurally-correct verdict route under the gap; no thresholds mutated, no governance violated).

**Corrective action ratified:** Future Sable pre-run coherence audits MUST enumerate spec §15.x sign-off chain rows alongside ESC §4 R-conditions, mapping each chain row to "explicitly verified" OR "implicit-deferred-to-impl" status.

---

## 4. Consolidated binding conditions on Path IV

Total: **17 conditions** (deduplicated; carry-forward ESC-012 R1-R17 PLUS NEW R18-R20 specific to N8.1 protocol-correction).

### 4.1 Carry-forward ESC-012 R1-R17 (verbatim)

All 17 ESC-012 binding conditions remain in force. R10 Gate 5 fence preservation REINFORCED. R6 reusability invariant (engine_config + spec yaml + atlas + calendar + Bonferroni IDENTICAL F2) STRICT. R7 predictor↔label semantics IDENTICAL F2. R9 OOS one-shot discipline PRESERVED (binding K3 measurement, NOT parquet read — per ESC-013 ratified interpretation).

### 4.2 NEW R18-R20 specific to N8.1

| ID | Source | Mandate |
|---|---|---|
| **R18** | Aria + Beckett + Sable | F2-T8-T1 Dex caller wiring — small commit (~5-30 LoC `scripts/run_cpcv_dry_run.py`): (a) new `--phase G` CLI flag; (b) phase-conditional `holdout_locked=False` propagation to `compute_ic_from_cpcv_results` when `phase=='G'`; (c) verdict-layer respects `ic_holdout_status='computed'` for K3 decay full evaluation. NEW test `test_phase_g_unlock_protocol` (regression guard). |
| **R19** | Beckett + Riven + Pax | N8.1 strict re-run discipline: 8/9 reproducibility stamps IDENTICAL F2 + N8 (only `dataset_sha256` may differ if parquet root or trade content shifts; engine_config / spec / atlas / calendar / cpcv_config / Bonferroni / latency / RLP / microstructure ALL IDENTICAL); `--phase G` + `holdout_locked=False` + same in-sample window 2025-07-01..2026-04-21. **No re-run after N8.1** regardless of outcome (one-shot binding K3 measurement). |
| **R20** | Sable | Verdict-vs-reason contract test: K3 PASS reason text MUST contain computed numbers (`IC_holdout=X.XX > 0.5 × IC_in_sample=Y.YY`), NOT sentinel strings ("DEFERRED" forbidden when status='computed'). Regression guard prevents future protocol gaps. |

---

## 5. Decision tree post-N8.1 outcome

| Outcome | Disposition |
|---|---|
| **K1+K2+K3 ALL COMPUTED PASS** (DSR>0.95 + PBO<0.5 + IC_holdout > 0.5×IC_in_sample) | **ESC-014 council** convene to adjudicate K1 strict bar interpretation under OOS-PROPER surprise PASS; Gate 5 still requires paper-mode Phase G/H per R10 fence carry-forward |
| **K3_FAIL_decay_collapse** (IC_holdout < 0.5 × IC_in_sample) | T002 falsified clean per spec §0; Riven 3-bucket reclassify N8.1 → strategy_edge_oos_K3_falsified; T002 retire ceremony |
| **K1_FAIL_OOS_marginal** (DSR drops back below 0.95 with K3 PASS) | costed_out_edge_oos_confirmed_K3_passed (refined from Round 2); T002 retire with refined diagnostic; cost reduction R&D path (BLOCKED by user constraint Path A OFF) |
| **INCONCLUSIVE_again** | ESC-014 escalation (procedural double-failure); deeper protocol audit; T002 retire as default |

---

## 6. Status

- [x] 5/5 ballots independent (Article IV preserved)
- [x] Outcome ratified: APPROVE_PATH_IV
- [x] F2-T9-OBS-1 admission registered (Sable corrective action)
- [x] 17 conditions ESC-012 carry-forward + 3 NEW R18-R20
- [ ] Dex F2-T8-T1 caller wiring (R18) — next step (~5-30 LoC)
- [ ] Quinn QA F2-T8-T2 gate (Check 8 retained)
- [ ] Beckett N8.1 protocol-corrected Phase G re-run (~3h)
- [ ] Mira F2-T9.1 Round 3.1 verdict COMPUTED
- [ ] Riven 3-bucket reclassify Round 3.1 per outcome
- [ ] Pax T002.7 close per outcome decision tree §5

---

## 7. Closure conditions

This escalation will be marked RESOLVED when N8.1 completes + Mira F2-T9.1 verdict published + Riven Round 3.1 reclassify + Pax T002.7 close (or ESC-014 escalation triggered per §5 outcome).

---

## 8. Authority chain

```
Council convened: @aiox-master post Mira F2-T9 INCONCLUSIVE
Voters: backtester (Beckett), risk-manager (Riven), general-purpose-architect (Aria), general-purpose-PO (Pax), squad-auditor (Sable)
Mira technical verdict already issued (F2-T9 Round 3 sign-off) — used as input, not voted again
Independence: enforced via parallel Agent dispatch + each ballot self-audit confirms NO peer-ballot reading
Quorum: 5/5
Outcome: 5/5 UNANIMOUS APPROVE_PATH_IV
Article II: preserved
Article IV: preserved
Cosign: @aiox-master 2026-04-30 BRT
```

— @aiox-master, orchestrating the squad
