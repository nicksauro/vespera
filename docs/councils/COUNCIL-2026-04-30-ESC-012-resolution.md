# Council ESC-012 — T002 Strategy-Fate Resolution (5/6 SUPERMAJORITY APPROVE_PATH_B)

> **Date (BRT):** 2026-04-30
> **Trigger:** Mira F2-T5 GATE_4_FAIL_strategy_edge sub `costed_out_edge` (PR #15 main `81139de`) — T002 NOT permanently falsified; user convocou council for strategy-fate adjudication
> **User constraint:** slippage + transaction costs FIXOS já conservadores → Path A original (cost reduction) OFF; reframed to Path A' (strategy refinement no cost change)
> **Authority:** Mini-council 6-vote (autonomous mode mandate, `feedback_always_delegate_governance.md`)
> **Article II preserved:** No push during deliberation
> **Article IV preserved:** Independent ballots — voters cast WITHOUT reading peer ballots; Aria's ballot was authored by agent before org-usage-limit interrupted dispatch (file `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md` exists with full frontmatter + body)
> **Author:** @aiox-master (orchestration capacity, autonomous mode)

---

## 1. Outcome

**RATIFIED: APPROVE_PATH_B — Phase G hold-out unlock OOS confirmation.** 5/6 SUPERMAJORITY (Aria + Kira + Mira + Beckett + Pax). Riven divergence to Path C registered (risk-side OOS-budget economics) — minority preserved governance integrity.

| Voter | Authority | Primary verdict | Secondary fallback | Personal preference disclosure | Ballot artifact |
|---|---|---|---|---|---|
| Kira (@quant-researcher) | Scientific peer-review + falsifiability | **APPROVE_PATH_B** | APPROVE_PATH_C | B over C; A' rejected as statistical malpractice (Bonferroni budget exhausted) | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-kira-vote.md` |
| Mira (@ml-researcher) | ML/statistical authority | **VOTE_PATH_B** | VOTE_PATH_C fallback | B preferred (asymmetric epistemic asset); A' rejected (overfit risk) | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-mira-vote.md` |
| Beckett (@backtester) | Simulation realism + N7-prime author | **APPROVE_PATH_B** | APPROVE_PATH_C if Dara holdout slip > 14d | B primary (cheapest single experiment + most informative); A' rejected (36h burden + Bonferroni inflation) | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-beckett-vote.md` |
| Riven (@risk-manager) | Risk + Gate 5 dual-sign + post-mortem author | **APPROVE_PATH_C** (retire) | (no fallback — primary stance) | C primary on OOS-budget economics + Quarter-Kelly preservation; B = low EV_info under regime-stationarity prior | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-riven-vote.md` |
| Aria (@architect) | Architecture + factory pattern guardian | **APPROVE_PATH_B** | APPROVE_PATH_C if independent governance blocks Path B | B primary (architectural cost minimal + reusability maximal + zero spec yaml mutation); A' rejected (LoC + spec mutation HIGH) | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md` |
| Pax (@po) | Story scope + 10-point checklist guardian | **PATH_B preferred** | PATH_C acceptable | B over C; A' REJECT (fails 10-point checklist on ≥4 dimensions per refinement story) | `COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-pax-vote.md` |

**Path A' UNANIMOUSLY REJECTED 6/6** — all voters cite either Bonferroni n_trials=5 budget exhaustion (Kira/Mira/Aria/Pax) or 36h burden + opportunity cost (Beckett/Pax) or risk-side foreclosure (Riven implicit) or all of the above.

---

## 2. Convergence basis (5/6 Path B)

5 voters arrived independently at Path B primary via DIFFERENT authority lenses converging on the same conclusion — Article IV strong evidence:

| Voter | Authority lens | Convergence reasoning |
|---|---|---|
| Kira | Scientific peer-review | Pre-committed disposition rule + asymmetric OOS asset + strict-§0 compatibility (Phase G adds K3 information without relaxing K1 strict bar) |
| Mira | ML/statistical | Single-shot binary disambiguation IS-fit-vs-genuine; OOS asset = paid-for calendar discipline; cannot be re-used |
| Beckett | Empirical/simulator | Cheapest single experiment ~3h vs A' 36h+; closes costed_out_edge bucket cleanly either way |
| Aria | Architectural | Code change minimal ~5-30 LoC; spec yaml mutation ZERO; reusability MAXIMAL of F2-T1 artifacts |
| Pax | Product/scope | Information yield per session asymmetric upside; backlog discipline preserves bandwidth |

The convergence is NOT coincidental — it reflects the canonical reproducible-backtest gating triplet (Bailey-LdP 2014 §6) treating OOS confirmation as the legitimate end-game test for in-sample-passing strategies, AND the spec contract treating Phase G hold-out window as the pre-authored canonical OOS test for THIS strategy specifically.

## 3. Riven minority dissent (Path C primary)

Riven primary preference is Path C with three load-bearing arguments:

1. **K1 strict bar UNMOVABLE foreclosure invariance:** even Phase G OOS PASS does not rescue Gate 4b under K1>0.95 strict + DSR=0.767 jointly K1 FAIL. So Phase B's "PASS" outcome architecturally cannot disarm Gate 4b → information value of B reduced.
2. **Bonferroni budget under refinement:** Path A' refinement re-uses in-sample window; n_trials inflation tightens K1 strict bar; squad bandwidth burned without bypassing Phase G. (This argument actually supports REJECT A' which all voters share.)
3. **OOS budget economics:** Riven assigns ~85% prior to regime-stationarity preserving cost-erosion → Phase G PASS unlikely; OOS budget best reserved for next strategy hypothesis (H_next).

Riven's argument is RISK-SIDE custodial (consistent with Riven authority) and not refuted by majority — voters acknowledge it as a legitimate alternative reading. Specifically:

- Aria's ballot disclosed: "Riven's counter-argument (Path C primary) is risk-side OOS-budget economics... Aria respects this... but the Mira spec §15.10 pre-authorization treats Phase G as the canonical OOS test for THIS strategy, NOT a generic budget for any future hypothesis."
- Mira and Kira ballots both list Path C as secondary acceptable.

**Resolution:** Path B primary 5/6; Path C secondary 5/6 (Riven's primary aligns with majority's secondary). The single divergence is on PRIORITY ORDER (B>C vs C>B), not on path admissibility.

---

## 4. Consolidated binding conditions on Path B

Total conditions ratified: **17** (deduplicated across 6 ballots; Aria 7 + Kira 4 + Mira 5 + Beckett 4 + Pax 16 — overlaps consolidated to 17 unique).

### 4.1 Pre-run governance (5 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R1** | Aria C-A8 + Mira C-M2 + Kira C-K2 | F2-T5-OBS-1 fix MUST land in Dex small commit BEFORE Phase G N8 run. Verdict-layer must short-circuit decay clause to `K3_DEFERRED` when `ic_holdout_status == 'deferred'` per Mira spec §15.6 + §15.10 strict reading. Test: `test_k3_deferred_short_circuit` (Aria C-A14 + Pax C-P12) NEW. |
| **R2** | Aria C-A9 + Mira C-M3 | Mira spec amendment v1.1.0 → v1.2.0 §15.13 NEW "Phase G OOS unlock protocol" — clarify (a) `holdout_locked=False` parameter path, (b) `ic_holdout_status='computed'` propagation, (c) decay test full evaluation `IC_holdout > 0.5 × IC_in_sample` becomes binding K3 sub-clause. |
| **R3** | Kira C-K1 + Mira C-M4 | **Pre-committed disposition rule (PRR-20260430-1) hash-frozen BEFORE running**: written in advance with 4 explicit branches (PASS K1+K2+K3 → ESC escalate; FAIL K3 collapse → strategy_edge clean falsification; FAIL K1+K3 sustains → costed_out_edge OOS-confirmed clean refutation; INCONCLUSIVE → ESC escalation). Pax cosign hash via `python scripts/pax_cosign.py register`. NO OOS run before disposition rule registered. |
| **R4** | Aria C-A11 + Beckett C-B2 | Hold-out tape Dara pre-requisite — IF parquet aggregation 2025-07 → 2026-04 not yet materialized, Dara T002.7-prep story authorize MUST precede Phase G N8 run. Adds ~10-20h Dara wall-time + ~1-2 squad sessions; acceptable per Beckett §4. |
| **R5** | Pax C-P3 + Aria C-A12 | Sable Phase G coherence audit (single audit pass similar to Sable F2 audit) — verify Phase G governance + spec amendment + reusability invariants. ~1 session. |

### 4.2 Run discipline (4 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R6** | Aria C-A10 + Mira C-M5 + Riven (implicit) | **Reusability invariant — Phase G run MUST consume IDENTICAL** `engine_config_sha256` (`ccfb575a…`), spec yaml v0.2.3 thresholds (DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE), cost atlas v1.0.0 (`bbe1ddf7…`), rollover calendar (`c6174922…`), Bonferroni n_trials=5 (T1..T5 verbatim), latency_dma2_profile, RLP detection, microstructure flags. **NO refinement / no parameter tweak / no Bonferroni expansion / no cost mutation.** |
| **R7** | Mira C-M5 | Predictor↔label semantics IDENTICAL Phase F2 (predictor=`-intraday_flow_direction`, label=`ret_forward_to_17:55_pts`, paired-resample bootstrap n=10000 PCG64 seed=42 per spec §15.4). |
| **R8** | Beckett C-B3 | Wall-time projection ~3h same as N7-prime; engine_config v1.2.0 perf optimization OPTIONAL (not blocking — single OOS run is squad-tolerable at 3h per Beckett §3). |
| **R9** | Kira C-K3 + Mira C-M6 | OOS one-shot discipline — Phase G window 2025-07-01..2026-04-21 is single-shot; result is binding regardless of outcome; CANNOT be re-run with adjusted parameters. |

### 4.3 Verdict + governance (5 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R10** | All voters (R5 carry-forward from ESC-011) | Gate 5 fence preservation — Phase G PASS does NOT pre-disarm Gate 5 alone under K1 strict bar. Gate 5 capital ramp dual-sign requires K1+K2+K3 ALL PASS + paper-mode Phase G/H. K1 strict bar (DSR>0.95) UNMOVABLE per Anti-Article-IV Guard #4. |
| **R11** | Riven (carry-forward) | 3-bucket post-mortem Round 3 entry post-Phase-G run. Riven authoring authority. Gate 4b NON-DISARM Round 3 entry OR Gate 4b DISARM entry (depending on outcome). |
| **R12** | Mira (carry-forward) | Mira F2-T9 re-clearance authority post-Phase-G run. New Gate 4b sign-off Round 3 supersedes Round 2 (NOT overwrite — preserves governance integrity). |
| **R13** | Pax C-P5..C-P11 | T002.7 successor story for Phase G run with 12 binary AC + scope IN/OUT discipline + verdict label discipline (PASS / FAIL_costed_out_edge_confirmed_OOS / FAIL_in_sample_artifact / INCONCLUSIVE_regime_mismatch). |
| **R14** | Pax C-P14 + Sable F-01 carry-forward | Quinn QA F2-T7 gate post-Dex F2-T5-OBS-1 fix; standard 8-point gate (Check 8 NEW Sable F-01 procedural fix retained). |

### 4.4 Decision tree post-Phase-G outcome (3 conditions)

| ID | Outcome | Action |
|---|---|---|
| **R15** | Phase G PASS unlikely outcome (DSR>0.95 OOS — would be ESCALATE per Kira C-K3) | ESC-013 council convene to adjudicate K1 strict bar interpretation under OOS surprise PASS (Aria + Mira + Riven + Pax + Sable + Kira); Gate 5 still requires paper-mode Phase G/H. |
| **R16** | Phase G FAIL_K3_collapse (IC_holdout drops significantly) | T002 hypothesis falsified clean per spec §0; Riven 3-bucket reclassify N8 → `strategy_edge` clean negative; T002 retire ceremony; epic deprecate; squad bandwidth freed. |
| **R17** | Phase G FAIL_K1+K3_sustains (IC stable but DSR<0.95) | costed_out_edge OOS-confirmed; T002 retire ceremony with refined diagnostic (signal real OOS-stable but cost-foreclosed); Riven 3-bucket reclassify N8 → `costed_out_edge_oos_confirmed`; institutional knowledge documented for H_next research. |

---

## 5. Path C as defined fallback

Per Aria + Beckett + Mira + Pax fallback discipline, IF Phase G run cannot proceed within 14 calendar days due to:
- Dara hold-out parquet materialization slip
- Mira spec amendment v1.2.0 dispute
- F2-T5-OBS-1 fix complications

OR IF council escalates to ESC-013 with majority voting Path C, then:
- T002.6 closes Done
- Epic T002 deprecated
- Riven 3-bucket post-mortem final entry: `costed_out_edge_in_sample_only_under_strict_K1`
- Squad bandwidth freed for H_next research
- Hold-out window 2025-07-01..2026-04-21 RESERVED for next strategy hypothesis pre-registration (NOT consumed)

This preserves Riven's risk-side OOS-budget economics argument as the explicit fallback path.

---

## 6. Anti-Article-IV self-audit (council-level)

**Article IV — every claim source-anchored:**

| Council claim | Source / trace |
|---|---|
| 5/6 supermajority Path B | 6 ballot files in `docs/councils/COUNCIL-2026-04-30-ESC-012-*-vote.md` |
| Path A' unanimously rejected 6/6 | All 6 ballots cite Bonferroni budget exhaustion or opportunity cost or both |
| Convergence basis (5 different authority lenses) | Each ballot's §1 + §6 cite distinct authority lens reasoning |
| Riven minority Path C primary | Riven ballot §1 verbatim |
| Pre-committed disposition rule (R3) | Kira ballot §6.1 (C-K1..C-K4) verbatim |
| F2-T5-OBS-1 fix prerequisite (R1) | Aria ballot §6 C-A8 + Mira F2-T5 §6 |
| Reusability invariant (R6) | Aria ballot §6 C-A10 + Mira ballot §6 |
| Phase G window 2025-07-01..2026-04-21 single-shot (R9) | Mira spec yaml v0.2.3 + spec v1.1.0 §3 |
| Anti-Article-IV Guard #4 thresholds UNMOVABLE | All voters confirm; Kira C-K2 + Mira C-M5 + Aria F-04 implicit |
| Anti-Article-IV Guard #3 hold-out lock | Phase G unlock is AUTHORIZED transition per Mira spec §15.10 (NOT violation) |

**Anti-Article-IV Guards 1-8 honored at council level:**
- Guard #1 (Dex impl gated em Mira spec PASS) — preserved (Mira spec amendment v1.2.0 R2 + 4 sign-offs T0a-T0e' precede Dex impl)
- Guard #3 (hold-out lock) — preserved (unlock is authorized transition per spec §15.10)
- Guard #4 (thresholds UNMOVABLE) — preserved (R6 reusability invariant)
- Guard #6 (Gate 5 sem Gate 4 = REJECT) — preserved (R10 Gate 5 fence)
- Guard #7 (no push) — preserved (Article II → Gage exclusive)
- Guard #8 (IC field default 0.0 reserved for pre-compute state only) — preserved (R7 predictor↔label semantics IDENTICAL F2)

---

## 7. Status (this resolution)

- [x] 6/6 ballots cast — 5 truly independent (Kira/Mira/Beckett/Riven/Pax) + 1 (Aria) authored by agent before usage limit interrupt; Aria ballot file complete with frontmatter + body
- [x] Outcome ratified: APPROVE_PATH_B 5/6 supermajority
- [x] Path A' UNANIMOUSLY REJECTED 6/6
- [x] 17 conditions consolidated + deduplicated + bound to F2-T5-OBS-1 fix / Mira spec amendment / Phase G run / Quinn QA / Riven reclassify / Pax close / outcome decision tree
- [x] Path C defined as explicit fallback (Riven minority preserved governance integrity)
- [ ] T002.7 successor story draft (Pax C-P5..C-P11 — next step)
- [ ] F2-T5-OBS-1 fix Dex small commit (R1 — next step)
- [ ] Mira spec amendment v1.1.0 → v1.2.0 §15.13 (R2 — next step)
- [ ] Pre-committed disposition rule PRR-20260430-1 (R3 — next step)
- [ ] Hold-out tape Dara pre-requisite check (R4)
- [ ] Sable Phase G coherence audit (R5)
- [ ] Phase G N8 run (~3h, R8)
- [ ] Mira F2-T9 re-clearance (R12)
- [ ] Riven 3-bucket reclassify Round 3 (R11)
- [ ] Pax T002.7 close + outcome decision (R15/R16/R17)

---

## 8. ESC-012 closure conditions

This escalation will be marked RESOLVED when:
1. Phase G N8 run completes + Mira F2-T9 re-clearance verdict published (PASS / FAIL_K3_collapse / FAIL_K1+K3_sustains / INCONCLUSIVE)
2. Riven 3-bucket Round 3 reclassify entry appended to post-mortem
3. T002.7 story closes Done OR ESC-013 escalation triggered (per R15)
4. §9 HOLD #2 chain status updated (Gate 4b DISARMED OR Gate 4b NON-DISARM Round 3 entry)
5. T002 epic disposition: Done (Phase G PASS unlikely route) OR Deprecated (R16/R17 confirmed) OR ESC-013 (R15 escalate)

---

## 9. Authority chain

```
Council convened: User mandate "agentes que executam decidem" + Kira incluida
Voters dispatched: 6 parallel Agent calls (ml-researcher, risk-manager, backtester, quant-researcher, general-purpose with architect persona, general-purpose with PO persona)
Constraint: User-imposed slippage + costs FIXOS já conservadores (Path A' reframing)
Ballot independence: enforced via parallel Agent dispatch with explicit "DO NOT read other ballots before writing own" + each ballot self-audit confirmed
Quorum: 6/6 (target met; Aria interrupted by agent org-usage-limit but ballot file complete)
Outcome: 5/6 SUPERMAJORITY APPROVE_PATH_B (Aria + Kira + Mira + Beckett + Pax); Riven minority APPROVE_PATH_C
Article II: preserved (no push during deliberation)
Article IV: preserved (each ballot self-audited; this resolution audited; all 17 conditions trace to ballot text + spec + ESC-011 ledger + carry-forward Round 1+2 governance)
R15 compliance: this resolution = governance ledger entry (canonical naming COUNCIL-{date}-ESC-{nnn}-{slug}.md)
Cosign: @aiox-master 2026-04-30 BRT, ratifying 5/6 supermajority council outcome
```

— @aiox-master, orchestrating the squad
