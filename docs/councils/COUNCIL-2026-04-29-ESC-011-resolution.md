# Council ESC-011 — Gate 4 Scope Resolution (5/5 UNANIMOUS APPROVE_OPTION_C)

> **Date (BRT):** 2026-04-29
> **Trigger:** Beckett N6 §11 caveat — Quinn QA gate F2 — Gate 4 scope ambiguity over synthetic walk PnL distribution (ESC-009 condition #4)
> **Authority:** Mini-council 5-vote (autonomous mode mandate, `feedback_always_delegate_governance.md`)
> **Article II preserved:** No push during deliberation (Gage exclusive).
> **Article IV preserved:** All 5 ballots cast independently (each voter blind to others' ballots before writing own — verified in each ballot's self-audit).
> **Author:** @aiox-master (squad-orchestration capacity, autonomous mode)

---

## 1. Outcome

**RATIFIED: APPROVE_OPTION_C — Hybrid Gate 4a (synthetic harness-correctness) + Gate 4b (real-tape edge-existence).**

| Voter | Authority | Verdict | Personal preference disclosed | Ballot artifact |
|---|---|---|---|---|
| Beckett (@backtester) | Simulation realism + N6 evidence holder | **APPROVE_OPTION_C** | Personal: A (strict). Subordinated to Quinn F2 framing + Mira spec §0 pre-existence. | `COUNCIL-2026-04-29-ESC-011-gate4-scope-beckett-vote.md` |
| Mira (@ml-researcher) | ML/statistical authority (DSR/PBO/IC) | **APPROVE_OPTION_C** | Personal: A (orthodox). Subordinated to Article IV (Phase F pre-existing in own spec §0+§7). | `COUNCIL-2026-04-29-ESC-011-gate4-scope-mira-vote.md` |
| Riven (@risk-manager) | Risk/sizing/Gate 5 dual-sign | **APPROVE_OPTION_C** | No personal divergence — operationally aligned. | `COUNCIL-2026-04-29-ESC-011-gate4-scope-riven-vote.md` |
| Aria (@architect) | Architecture/design | **APPROVE_OPTION_C** | No personal divergence — Spec §0 pre-existence + factory pattern survives both phases. | `COUNCIL-2026-04-29-ESC-011-gate4-scope-aria-vote.md` |
| Pax (@po) | Story scope + 10-point checklist | **APPROVE_OPTION_C** | No personal divergence — Phase F pre-existed Pax T0e cosign. | `COUNCIL-2026-04-29-ESC-011-gate4-scope-pax-vote.md` |

**Convergência independente 5/5 — Article IV strong evidence.** Mira + Beckett both disclose A as personal aesthetic preference but vote C; Riven/Aria/Pax converge directly. No ballot was subjected to influence from another before writing.

---

## 2. Consolidated binding conditions on Option C

Total conditions ratified: **20** (deduplicated across 5 ballots; some overlap collapsed).

### 2.1 Verdict labeling + caveat surfacing (4 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R1** | Beckett #1 + Mira #M2 | Gate 4a verdict text MUST carry verbatim caveat: "Harness-correctness clearance over synthetic deterministic walk per Mira spec §7 toy benchmark methodology. Edge-existence clearance pending Gate 4b real-tape replay (Phase F scope). DSR=1.52e-05 is the noise-floor null measurement, NOT an economic statement about WDO end-of-day fade strategy edge." Caveat appears in (a) Mira Gate 4a sign-off artifact, (b) Riven §9 HOLD #2 Gate 2+3 disarm ledger, (c) any downstream story/epic consuming Gate 4a as input. |
| **R2** | Riven C-R1 | Mira Gate 4a sign-off label MUST be `HARNESS_PASS` (NOT `GATE_4_PASS`). Naming-as-discipline. |
| **R3** | Riven C-R3 | Warning prepend obrigatório em todo artefato citando N6 DSR/PBO/IC numbers. |
| **R4** | Pax §6.2 + Beckett #4 | Synthetic-walk caveat verbatim em Beckett N6 report stays; AC11 cost atlas audit = post-F1 stamp re-run. |

### 2.2 Gate 5 disarm fence (3 conditions, REDUNDANT — explicit by design)

| ID | Source voter | Mandate |
|---|---|---|
| **R5** | Beckett #2 + Riven C-R2 + Pax §6.3 | **Gate 4a CANNOT pre-disarm Gate 5.** Riven §9 HOLD #2 Gate 5 (capital ramp protocol RA-XXXXXXXX-X dual-sign) MUST require Gate 4b (real-tape) PASS as upstream pre-condition. No Gate 5 firing on Gate 4a alone. Sequential serial dependency: Gate 4a AND Gate 4b BOTH required upstream of Gate 5. |
| **R6** | Riven C-R2 | Footer verbatim "Gate 4a NOT pre-disarm Gate 5" no arquivo de sign-off Mira (sem footer = sem co-sign Riven). |
| **R7** | Riven §11.5 pre-condition #7 (new) | Synthetic-vs-real-tape attribution audit obrigatório (`docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`) classificando cada artefato N5→N7 como `engineering_wiring | strategy_edge | paper_mode_audit`. Gate 5 dual-sign prerequisite. |

### 2.3 Phase F scope (4 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R8** | Beckett #3 | Phase F story scope MUST include Beckett N7+ real-tape replay with: (a) WDO parquet tape consumption replacing `_walk_session_path`/`_walk_to_exit` synthetic walks, (b) preserved factory pattern + per-fold P126 rebuild + Bonferroni n_trials=5, (c) cost atlas wiring identical to N6, (d) latency_dma2_profile applied to slippage estimation per Beckett engine spec, (e) RLP policy + rollover calendar consumption per Nova authority, (f) re-run Bailey-LdP 2014 toy benchmark on real-tape harness to confirm discriminator power preserved. |
| **R9** | Mira #M5 | Gate 4b sample-size ≥ 30-50 per trial × 5 trials per Bailey-LdP §3 minimum; Bonferroni n_trials=5 carry-forward NON-NEGOTIABLE; failure attribution scaffolding 3-bucket (data quality | strategy edge | both). |
| **R10** | Pax §6.4 | Phase F MUST become a separate future story (proposed T002.2) — NOT a hidden T002.1.bis sub-task. |
| **R11** | Riven C-R4 | Mira draftar Gate 4b spec ANTES de Gate 4a verdict (fence-against-drift). |

### 2.4 Toy benchmark + harness-correctness criteria (3 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R12** | Beckett #5 + Mira #M3 | Quinn QA MUST confirm `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6 tests) executed green with mean Δ DSR > 0.10 across 5 seeds. Structural evidentiary bridge for treating synthetic-walk DSR/PBO as harness-correctness signals. |
| **R13** | Aria AC-1 | Gate 4a criteria = K1a/K2a/K3a (harness-correctness only — DSR shape, PBO non-degenerate, toy benchmark §7); NO economic-edge claim in Gate 4a text. |
| **R14** | Aria AC-2 + Pax §6.1 | Gate 4b criteria (Mira spec §6 thresholds DSR>0.95 / PBO<0.5 / IC) UNCHANGED; thresholds unmovable per Anti-Article-IV Guard #4. Gate-bind mechanism for Gate 4b deferred to Phase F architectural review. |

### 2.5 Article IV trace + housekeeping (3 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R15** | Beckett #6 + Mira #M4 | Article IV trace for Gate 4a verdict: every clause in Mira sign-off must trace to (a) N6 report §-anchor, (b) Mira spec §-anchor, (c) ESC-009 cond #4 + ESC-010 F2 ruling + this ESC-011 ratification entry. NO invention. |
| **R16** | Beckett #4 + Aria AC-3 + Riven C-R5 | **Quinn F1 (cost_atlas_sha256 null) BLOCKING for Gate 4a sign-off.** Atlas SHA-lock audit chain is part of harness-correctness perimeter. F2/F3/F4 non-blocking. |
| **R17** | Beckett #4 | C2 (simulator_version stamp string stale) + C3 (spec_version dual-source) NICE-TO-HAVE for Gate 4a; BLOCKING for Gate 4b reproducibility. |

### 2.6 Council ledger + governance (3 conditions)

| ID | Source voter | Mandate |
|---|---|---|
| **R18** | Pax §6.5 | Mini-council 3-vote ratification format + governance ledger entry preserved; this resolution doc IS the entry. |
| **R19** | Mira #M5 | Mira retains right to escalate if council ratifies Option B against ML authority dissent — N/A (Option C ratified). |
| **R20** | Riven §11.5 #7 | Synthetic-vs-real-tape post-mortem authored before Gate 5 dual-sign (see R7). |

---

## 3. Pre-conditions for Mira Gate 4a sign-off (BLOCKING checklist)

Per consolidated conditions above, Mira Gate 4a CANNOT issue verdict until ALL of:

- [x] **R16:** Quinn F1 patch landed (`cost_atlas_path` + `rollover_calendar_path` wired in `_build_runner`). **DONE 2026-04-29 — commit `9997f14`** (`fix(t002.1.bis): wire cost_atlas_path + rollover_calendar_path in _build_runner`).
- [ ] **R12:** Quinn confirms toy benchmark 6/6 PASS with Δ DSR > 0.10 across 5 seeds (currently confirmed in QA gate §3 Check 2; re-confirm post-F1 patch).
- [ ] **Beckett N6+ re-run** post-F1 commit confirming `cost_atlas_sha256` populated (resolves N6 §9 C1; satisfies R7 + R16 + Riven §11.5 pre-condition #1).
- [ ] **R11:** Mira drafts Gate 4b spec skeleton at `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` (fence-against-drift; can be terse — mandatory milestones, sample-size R9, criteria carry-forward R14, attribution scaffolding R9).
- [ ] **R7:** Synthetic-vs-real-tape attribution post-mortem stub at `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (Riven authors; classifies N5→N7 evidence).

Once all 5 satisfied → Mira issues Gate 4a `HARNESS_PASS` (NOT `GATE_4_PASS`) sign-off at `docs/qa/gates/T002.1.bis-mira-gate-4a-signoff.md` carrying R1+R2+R3+R6+R13+R15 verbatim.

---

## 4. Status (this resolution)

- [x] 5/5 ballots cast independent (Article IV verified per ballot self-audit)
- [x] Outcome ratified: APPROVE_OPTION_C
- [x] 20 conditions consolidated + deduplicated
- [x] R16 (F1 patch) DONE — commit `9997f14`
- [ ] N6+ re-run dispatched to Beckett (next step)
- [ ] Mira Gate 4b draft spec (next step, can be parallel)
- [ ] Riven attribution post-mortem stub (next step, can be parallel)
- [ ] Quinn re-QA leve pós-F1 (downstream of N6+)
- [ ] Mira Gate 4a `HARNESS_PASS` sign-off (downstream of all above)
- [ ] Gage push branch → PR (downstream of all gates)

---

## 5. ESC-011 closure conditions

This escalation will be marked RESOLVED when:
1. Mira Gate 4a `HARNESS_PASS` sign-off published with R1-R20 conditions verbatim.
2. Riven §9 HOLD #2 Gate 2+3 disarm ledger appended with caveat R1.
3. T002.2 Phase F story stub created (R10, low-priority — can be after Gate 4a sign-off).
4. Pre-existing 5 disarm gates of §9 HOLD #2 re-mapped: Gate 1 (DONE T002.0h.1) + Gate 2 (cleared by N6 pipeline integrity) + Gate 3 (cleared by N6 strict-literal §9) + **Gate 4a (this council; pending sign-off)** + Gate 4b (deferred Phase F) + Gate 5 (Riven dual-sign, gated on 4a AND 4b).

---

## 6. Authority chain

```
Council convened: @aiox-master (autonomous mode mandate, feedback_always_delegate_governance.md)
Voters dispatched: ml-researcher (Mira), risk-manager (Riven), backtester (Beckett — pre-emptive ballot 2026-04-29 BRT), general-purpose w/ persona context (Aria, Pax)
Ballot independence: enforced via parallel Agent dispatch with explicit "DO NOT read other ballots before writing own" + each ballot self-audit confirmed
Quorum: 5/5 (target — Sable abstained as auditor-only per `feedback_always_delegate_governance.md`)
Outcome: 5/5 UNANIMOUS APPROVE_OPTION_C
Article II: preserved (no push during deliberation)
Article IV: preserved (all 20 conditions trace to ballot text + N6 evidence + Mira spec § anchors + ESC-009/010 ledger)
R15 compliance: this resolution = governance ledger entry (canonical naming COUNCIL-{date}-ESC-{nnn}-{slug}.md)
Cosign: @aiox-master 2026-04-29 BRT, ratifying 5/5 unanimous council outcome
```

— @aiox-master, orchestrating the squad
