# Implementation Council 2026-05-01 — Squad Instrumentation Resolution (Q-SDC v2 hardening)

> **Date (BRT):** 2026-05-01
> **Trigger:** T002 RETIRE FINAL — Sable F-01..F-04 + F2-T9-OBS-1 admission + N8.1 closure-Literal bug + N8 verdict-vs-reason inconsistency = 4 procedural gap classes recurring
> **Authority:** Mini-council 4-vote (Aria + Pax + River + Sable)
> **Article IV:** independent ballots verified per ballot self-audit
> **Author:** @aiox-master orchestration capacity, autonomous mode

---

## 1. Outcome

**RATIFIED 4/4 UNANIMOUS** Q-SDC v2 procedural hardening package. 5 architectural amendments + 1 candidate Anti-Article-IV Guard #9 + 1 candidate R16 + 4-Layer audit method + 4-disposition anti-pattern catalog promotion.

| Voter | Authority | Verdict |
|---|---|---|
| Aria (@architect) | Architecture | APPROVE all 4 amendments + 3 regression tests + parallel track engine v1.2.0 |
| Pax (@po) | Story scope + 10-point checklist | APPROVE 5 Q-SDC v2 amendments (A1-A5); ratify Quant top-3 fits scope + budget cap ≤ 60 sessions H_next |
| River (@sm) | Story drafting + spec-first protocol | APPROVE T0f NEW caller-wiring sign-off row + AC binary-verifiable + wiring validation test + single-iteration discipline H_next |
| Sable (@squad-auditor) | Process audit | APPROVE Q-SDC v2 hardening + Guard #9 candidate + R16 candidate + 4-Layer audit method + anti-pattern 3-way disposition |

**4/4 UNANIMOUS** with no blocking conditions.

---

## 2. Consolidated 14 binding instruments

### 2.1 Q-SDC v2 procedural hardening (5 amendments)

| ID | Source voter | Mandate |
|---|---|---|
| **QSDCv2-1** | Pax A1 + Sable F-01 + Aria A1 | **AIOX QA gate template "Check N+1: metric-pipeline-wiring verification" canonical row** — Quinn explicitly enumerate metric fields, trace caller invocations (NOT defaulted), confirm production callsites (NOT orphan code), spot-check zero-with-degenerate-CI signature against §5.8 anti-pattern. Owner: Quinn (@qa). |
| **QSDCv2-2** | River A2 + Aria A3 + Sable F-02 + Pax A2 | **T0f NEW caller-wiring sign-off chain row** mandate. Spec-first protocol every story sign-off chain T0a-T0f explicit. Each caller-wiring row specifies (source caller path, wiring contract verbatim, pre-run prereq status). Owner: River (@sm) story template + Pax 10-point checklist amendment. |
| **QSDCv2-3** | Aria A4 + River + Sable F-03 | **Closure-body Literal completeness invariant** — lint/static-check rule OR Quinn QA gate addition. Any function dispatching on Literal-typed phase/mode parameter MUST update Literal at all callsites + add explicit dispatch branch + regression test on extension. Owner: Quinn (@qa) + Dex (@dev). |
| **QSDCv2-4** | Aria A2 + Sable F-04 + River A2c | **Verdict-vs-reason cross-protocol consistency contract** — generalized R20 → Anti-Article-IV Guard #9 candidate (§3 below). Regression test pattern per `*_status`-flagged field per gate. Owner: Mira (@ml-researcher) v0.3.0 spec amendment. |
| **QSDCv2-5** | Pax A3 + Pax A5 | **3-ESC circuit-breaker review** — T002's 3-ESC count unsustainable; future epics aim ≤2 ESC + Article IV self-audit ≥5 anchors per ballot/sign-off. Single-iteration discipline binding. Owner: Pax (@po) + AIOX-master. |

### 2.2 Anti-Article-IV Guard #9 candidate

**Mira spec amendment v0.3.0 (post H_next ratification) adds Guard #9 verbatim:**

```
For any verdict-input dataclass field with associated *_status provenance flag,
the verdict-layer reason-text emission MUST be consistent with status flag value
across full protocol chain ReportConfig → MetricsResult → KillDecision →
verdict.reasons:

- status='computed': reason text MUST contain computed numeric values; sentinel
  strings ('DEFERRED'/'PENDING'/'UNAVAILABLE') FORBIDDEN
- status='deferred': reason text MUST contain DEFERRED sentinel; computed
  numeric values FORBIDDEN
- status='pre_compute' / dataclass default: verdict layer MUST raise
  InvalidVerdictReport (Guard #8 enforcement) before reason text emission

Cross-protocol consistency contract test MANDATORY per *_status-flagged field.
```

**Owner:** Mira (@ml-researcher) authoring; Sable cosigns audit-rule scope; AIOX-master adjudicates AIOX-canonical vs Mira-spec-local.

### 2.3 R16 candidate (R-rules R1-R15 review)

**R16 candidate text (Sable §3.2 proposal):**

```
R16 — Spec-first sign-off chain caller-wiring explicit enumeration

Every domain spec sign-off chain (Mira/Nova/Riven/Aria/Tiago) MUST EXPLICITLY
ENUMERATE caller-wiring tasks as standalone rows, NOT collapse them into
"implementation gated on spec PASS" envelopes. Each caller-wiring row MUST
specify: source caller path, wiring contract verbatim, pre-run prereq status.

Sable Phase G coherence audit method MUST traverse spec sign-off chain rows
alongside ESC §4 R-conditions, mapping each row to {explicitly verified |
implicit-deferred-to-impl-cross-checked-pre-run | out-of-scope-with-rationale}.
```

**Owner:** AIOX-master + Pax adjudicate ratification (Sable defers per R14 scope discipline). Sable executes Layer A + B + C + D audit method regardless (corrective-action commitment binding).

### 2.4 Audit perimeter widening (4 layers)

**Sable R5-equivalent Phase G coherence audit method post-ESC-013:**

| Layer | Description | Status |
|---|---|---|
| **A** | ESC §4 R-condition list (verbatim per resolution) | Already-honored |
| **B** | Domain spec internal sign-off chain (Mira spec §15.x rows + analog for Nova/Riven/Aria/Tiago) | NEW post-ESC-013 |
| **C** | Closure-body Literal completeness check | NEW post-ESC-013 |
| **D** | Verdict-vs-reason cross-protocol consistency check | NEW post-ESC-013 |

**Promotion:** AIOX framework canonical AUDIT-template. Owner: AIOX-master + Pax canonical-layer.

### 2.5 Anti-pattern catalog promotion (3-way disposition)

| Anti-pattern | Source | Promotion | Owner |
|---|---|---|---|
| **§5.8** zero-with-tight-CI signature | Riven post-mortem v3 | AIOX framework canonical (strategy-agnostic) | AIOX-master + Riven cosign |
| **§5.9 meta-pattern** diagnostic-confusion iteration discipline | Riven v3 | AIOX canonical meta-pattern; specifics T002-local exemplar | Pax + AIOX-master + Riven cosign |
| **§5.10a** Literal-completeness anti-pattern | Riven §5.10 + Sable F-03 split | AIOX canonical (Quinn lint/check rule) | Quinn + AIOX-master + Riven cosign |
| **§5.10b** F-vs-G phase semantics protocol-confusion | Riven §5.10 split | DEFER to H_next spec authoring | Mira + Aria H_next |

---

## 3. H_next budget + scope discipline

Per Pax §4 + River §4 + Aria §4 ratification:

- **H_next budget cap:** ≤ 20 sessions per candidate × 3 candidates = ≤ 60 total sessions
- **Single-iteration discipline binding** (Round X.Y append-only revision pattern from T002 retire preserved as canonical)
- **Circuit-breaker:** at 3rd ESC review escalation pattern (Pax A3); review at 40% of T002 burn (~12 sessions per candidate)
- **OOS budget:** forward-time virgin hold-out 2026-05-01..2026-10-31 (Mira primary preference; Quant Council R7 ratified)
- **Engine v1.2.0 perf optimization PARALLEL-TRACK** (Aria QSDCv2-T1 NON-BLOCKING for first trial; MANDATORY before n_trials=3+ runs)

---

## 4. Quant Council top-3 ratification (Pax authority)

Quant Council PRIMARY (conviction-conditional sizing) + SECONDARY (auction print) + DEFERRED (asymmetric exit) **ALL RATIFIED FIT story scope discipline + 11-point binary AC verifiable + Article IV trace** per Pax (Impl Council §3).

Sequencing: PRIMARY → SECONDARY → DEFERRED per Quant Council resolution sequencing R1-R17.

---

## 5. Status

- [x] 4/4 ballots cast independent (Article IV verified)
- [x] Outcome ratified: 5 Q-SDC v2 amendments + Guard #9 candidate + R16 candidate + 4-Layer audit + 3-way anti-pattern disposition
- [x] H_next budget cap ratified (≤ 60 total sessions; ≤ 20 per candidate)
- [x] Single-iteration discipline binding
- [ ] AIOX-master + Pax adjudicate Q-SDC v2 amendments adoption canonical layer
- [ ] Quinn QA gate template "Check N+1" canonical row addition
- [ ] River T0f sign-off row template amendment
- [ ] Mira spec v0.3.0 Guard #9 amendment (post H_next ratification)
- [ ] AIOX-master + Pax adjudicate R16 R-rule promotion
- [ ] Quinn + Dex closure-body Literal completeness lint/check rule
- [ ] Beckett engine v1.2.0 perf optimization parallel-track (T-1)

---

## 6. Authority chain

```
Council convened: @aiox-master post user mandate Implementation Council 2026-05-01
Voters: 4 (Aria + Pax + River + Sable)
Independence: enforced via parallel Agent dispatch + each ballot self-audit
Quorum: 4/4
Outcome: 4/4 UNANIMOUS Q-SDC v2 hardening ratified
Article II: preserved (no push)
Article IV: preserved (each ballot self-audited; 14 instruments trace to source artifacts)
R14: Sable scope discipline preserved (no self-promotion to global R-rule)
Cosign: @aiox-master 2026-05-01 BRT
```

— @aiox-master, orchestrating the squad
