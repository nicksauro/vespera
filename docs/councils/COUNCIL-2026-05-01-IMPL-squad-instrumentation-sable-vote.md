---
council: IMPL-2026-05-01-squad-instrumentation
title: Squad-instrumentation post-T002-retire — Q-SDC v2 procedural hardening + Anti-Article-IV Guard #9 candidate + R-rules R1-R15 review + Phase G audit perimeter widening + anti-pattern catalog promotion
date_brt: 2026-05-01
voter: Sable (@squad-auditor)
authority_basis: R14 audit perimeter; ESC-013 §3 F2-T9-OBS-1 admission carry-forward; R5 audit-method owner
ballot_independence: written without reading peer ESC-013 ballots OR peer IMPL-2026-05-01 ballots before authoring
verdict_high_level: APPROVE_Q_SDC_V2_PROCEDURAL_HARDENING + APPROVE_GUARD_9_CANDIDATE_FOR_MIRA_V0_3_0 + APPROVE_AUDIT_PERIMETER_WIDENING + APPROVE_RIVEN_ANTI_PATTERN_PROMOTION
note_persistence: Sable agent returned ballot text directly per system reminder; @aiox-master persisted file inline 2026-05-01 BRT
---

# Sable ballot — Implementation Council 2026-05-01: squad-instrumentation post-T002 retire

> **Voter:** Sable (@squad-auditor) — auditor externo, sem voto operacional sobre alpha / sizing / kill / data-fate.
> **Question:** what procedural / R-rule / audit-perimeter / anti-pattern instruments does the squad ratify into Q-SDC v2 + AIOX canonical layer post-T002 retire?

## §1 Procedural gaps consolidados — recurring pattern analysis

| Gap ID | First manifestation | Severity | Owner | Q-SDC v2 instrument |
|---|---|---|---|---|
| **F-01** | Round 1 N7 IC-pipeline-wiring-gap (zero-with-tight-CI signature) | ⚠️ HIGH | Quinn (@qa) | AIOX QA gate template "Check N+1: metric-pipeline-wiring verification" canonical row |
| **F-02** | F2-T9-OBS-1 (R5 audit not enumerated F2-T8-T1 Dex wiring) | ⚠️ HIGH | Sable committed | R5 audit method includes spec §15.x sign-off chain enumeration alongside ESC §4 R-conditions |
| **F-03** | N8.1 closure-Literal completeness bug (~12s synthetic fallback) | ⚠️ HIGH | Quinn + Dex | Closure-body Literal completeness invariant — lint/static-check rule OR Quinn QA gate addition |
| **F-04** | N8 verdict-vs-reason inconsistency (verdict K3 PASS / reason DEFERRED) | ⚠️ HIGH-to-🔴 | Mira + Sable cross-ref | Generalize R20 → Anti-Article-IV Guard #9 (§2 below) |

**Recurring root-cause pattern:** trust-delegation-without-cross-check between agent perimeters at every spec-implementation transition. **Q-SDC v2 systemic shift:** explicit cross-perimeter handoff verification.

## §2 Anti-Article-IV Guard #9 candidate (verdict-vs-reason cross-protocol invariant)

```
Anti-Article-IV Guard #9 — Cross-protocol consistency invariant

For any verdict-input dataclass field with an associated *_status provenance
flag (Anti-Article-IV Guard #8 pattern), the verdict-layer reason-text
emission MUST be consistent with the status flag value across the full
protocol chain ReportConfig → MetricsResult → KillDecision → verdict.reasons:

  - status == 'computed': reason text MUST contain computed numeric values
    (e.g., "IC_holdout=0.866 > 0.5 × IC_in_sample=0.433"). Sentinel strings
    ('DEFERRED', 'PENDING', 'UNAVAILABLE') FORBIDDEN.
  - status == 'deferred': reason text MUST contain DEFERRED sentinel verbatim;
    computed numeric values FORBIDDEN.
  - status == 'pre_compute' / dataclass default: verdict layer MUST raise
    InvalidVerdictReport (Guard #8 enforcement) before reason text emission.

Cross-protocol consistency contract test MANDATORY per *_status-flagged field.
```

**Promotion path:** Mira spec amendment v0.3.0 (after H_next ratification). Sable cosigns audit-rule scope; Mira authors canonical text; AIOX-master adjudicates AIOX-canonical vs Mira-spec-local.

## §3 R-rules R1-R15 review + R16 candidate

**R1-R15 ALL PRESERVED** through T002 retire (Round 3.1 audit confirms).

**R16 candidate text:**

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

**Sable disposition:** defers to AIOX-master + Pax adjudication on R16 promotion to global R-rule status (R14 scope discipline).

## §4 Audit perimeter widening (Q-SDC v2 — Layers A/B/C/D)

**Sable R5-equivalent audit method post-ESC-013:**
- **Layer A** — ESC §4 R-condition list (verbatim per resolution). Already-honored.
- **Layer B** — Domain spec internal sign-off chain (NEW post-ESC-013). Each row mapped to status.
- **Layer C** — Closure-body Literal completeness check (NEW; cross-references Quinn F-03).
- **Layer D** — Verdict-vs-reason cross-protocol consistency (NEW; cross-references R20 / Guard #9).

**Promotion:** AIOX framework canonical AUDIT-template adopts four-layer method. Owner: AIOX-master + Pax. Sable executes regardless (corrective-action commitment binding).

## §5 Anti-pattern catalog promotion (Riven §5.8/5.9/5.10)

| Anti-pattern | Disposition |
|---|---|
| **§5.8** zero-with-tight-CI signature | APPROVE AIOX framework canonical (strategy-agnostic mechanism) |
| **§5.9 meta-pattern** diagnostic-confusion iteration discipline | APPROVE AIOX canonical meta-pattern; specifics T002-local exemplar |
| **§5.10a** Literal-completeness anti-pattern | APPROVE AIOX canonical (Quinn lint/check rule) |
| **§5.10b** F-vs-G phase semantics protocol-confusion | DEFER to H_next spec authoring (Mira + Aria) |

**Owner:** Riven (@risk-manager) post-mortem author cosign required before AIOX canonical-layer mutation.

## §6 Personal preference disclosure

- **Q-SDC v2 procedural hardening:** STRONG YES on F-01..F-04 (systemic shift toward explicit cross-perimeter verification).
- **Anti-Article-IV Guard #9 promotion:** STRONG YES (mechanism strategy-agnostic; T002 was near-miss).
- **R16 candidate:** MEDIUM YES; defer global R-rule ratification to AIOX-master + Pax.
- **Audit perimeter widening:** STRONG YES on Layers A/B/C/D adoption canonical AUDIT-template.
- **Anti-pattern catalog:** MEDIUM-to-STRONG YES per disposition above.

**No conflict-of-interest** — Sable has no operational stake T002 OR H_next.

## §7 Article IV self-audit

Every claim traces to source artifact cited verbatim:
- F-01..F-04 → `docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md`
- F2-T9-OBS-1 admission → ESC-013 resolution §3 + Sable ESC-013 ballot §2
- R20 NEW + R18 + R19 → ESC-013 resolution §4.2
- Round 1 → 3.1 cascade → Riven post-mortem §2 + Mira sign-off chain
- N8.1 closure-Literal bug → Riven §2.R3.1.1
- N8 verdict-vs-reason inconsistency → Mira Round 3 §3 + ESC-013 resolution §2
- Riven anti-pattern §5.8/5.9/5.10 → Riven post-mortem verbatim
- Anti-Article-IV Guards 1-8 canonical → Mira spec v1.2.0 §15.5
- R-rules R1-R15 preservation → Round 3.1 §12 + Constitution Article I-VI

NO INVENTION. R14 preserved (Sable not promoting audit-method to global R-rule unilaterally; deferred to AIOX-master + Pax).

## §8 Sable cosign

Sable @squad-auditor 2026-05-01 BRT — IMPL Council ballot squad-instrumentation post-T002-retire.

**Out-of-scope explicitly:** Mira v0.3.0 spec text (Mira authority); AIOX canonical-layer mutation (AIOX-master); Quinn QA gate template (Quinn); R16 ratification (AIOX-master + Pax); Riven anti-pattern catalog ownership (Riven cosign required); H_next strategy (Pax + Kira + Mira); kill/sizing/alpha (operational-side); push (Gage @devops Article II).

— Sable, o cético do squad
