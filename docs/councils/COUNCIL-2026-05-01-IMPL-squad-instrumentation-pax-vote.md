---
council_id: IMPL-2026-05-01
council_topic: Implementation Council 2026-05-01 — squad instrumentation, story-lifecycle hardening, PRR registration discipline, H_next backlog prioritization, squad bandwidth budgeting (post-T002 retire / Round 3.1 FINAL costed_out_edge_oos_confirmed_K3_passed)
voter: Pax (@po — Product Owner)
vote_date_brt: 2026-05-01
ballot_independent: true
ballot_independence_basis: Article IV §6 — Pax authoring without reading other Impl Council ballots
authority_basis:
  - "Pax @po — story scope authority + AC integrity guardian + 10-point checklist owner + backlog prioritization + spec scope discipline"
  - "AIOX framework `validate-next-story.md` 10-point checklist (PO authority)"
  - "ESC-011 R10 — successor story authority; Pax adjudicates forward research path"
  - "ESC-012 R3 — PRR-20260430-1 hash-frozen disposition rule binding precedent (4 branches + INCONCLUSIVE residual)"
  - "ESC-013 R6 reusability invariant + R9 single-shot binding (carry-forward T003+)"
  - "Mira Round 3.1 FINAL — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed"
  - "Quant Council 2026-05-01 — 5 ballots (Mira, Beckett, Riven, Kira, Nova) ranking H_next candidates"
inputs_consumed:
  - "Quant Council ballots Mira + Beckett (read for §3 candidate fit)"
  - "ESC-013 Pax ballot 21 binding conditions C1-C21 (carry-forward to T003)"
  - "ESC-012 R6 + R7 + R8 + R9 + R10 reusability/single-shot/fence invariants"
  - "PRR-20260430-1 §3.1-§3.4 hash-frozen 4-branch disposition rule (canonical pattern)"
  - "Mira spec v1.2.0 §15.13.7 one-shot consumption (binding measurement reading)"
  - "Sable F-04 audit finding (metric chain wiring assumed-but-unbuilt; Phase G protocol-compliance gap root cause)"
  - "T002 epic post-mortem: 50+ squad sessions, 3 ESC councils (ESC-011/012/013), 2 spec amendments (v1.1.0/v1.2.0)"
inputs_explicitly_NOT_read:
  - "Other Impl Council 2026-05-01 ballots (Aria, Riven, Sable, Kira, Mira) — Article IV §6 independence enforced"
verdict_summary: |
  Story-lifecycle Q-SDC v2 amendments PROPOSED (5 changes); PRR-20260430-1 disposition-rule pre-commit pattern PROMOTED canonical
  for T003+ alpha-discovery; H_next backlog candidates Quant top-3 (conviction-conditional sizing, label-horizon swap, asymmetric
  exit) RATIFIED FIT story scope discipline + 10-point binary AC verifiable + Article IV traceable; H_next squad bandwidth budget
  CAP recommended ≤ 20 sessions per candidate (40% of T002 burn) with mandatory single-iteration discipline + circuit-breaker at
  3rd ESC escalation; 21 binding ESC-013 conditions C1-C21 carry forward; 5 personal preferences disclosed (continuity, density,
  Article IV honesty, scope discipline, retro-clarity); Article IV self-audit 9 anchors verified.
spec_yaml_status: NO_MUTATION proposed by Pax (10-point checklist amendment is process-side; PRR pattern is governance-side; H_next ratification is backlog-side; spec yaml v0.2.3 thresholds preserved verbatim Anti-Article-IV Guard #4)
cosign: Pax @po 2026-05-01 BRT — Implementation Council ballot
---

# COUNCIL IMPL-2026-05-01 — Pax Vote: Squad Instrumentation, Story-Lifecycle, PRR, Backlog, Bandwidth

**Council:** IMPL-2026-05-01 — Implementation Council post T002 retire (Round 3.1 FINAL)
**Voter:** Pax (@po — Product Owner)
**Date (BRT):** 2026-05-01
**Branch:** `t002-1-bis-make-backtest-fn` (Pax authoring; no commit/push performed)
**Constraint preserved:** spec yaml v0.2.3 thresholds UNMOVABLE (DSR > 0.95 / PBO < 0.5 / IC > 0; Anti-Article-IV Guard #4 + ESC-011 R14 + ESC-012 R6)
**Constraint preserved:** Article II Gage @devops EXCLUSIVE push authority
**Constraint preserved:** ESC-013 R6 reusability invariant carry-forward to T003+ (engine_config_sha256 + cost atlas v1.0.0 + rollover calendar + Bonferroni accounting semantics)
**Independence:** Article IV §6 — Pax did NOT read other IMPL ballots before authoring

---

## §1 Story-lifecycle improvements for Q-SDC v2

T002 produced **3 escalation rounds** (ESC-011 / ESC-012 / ESC-013) and consumed **50+ squad sessions** across 4 spec amendment cycles. The post-mortem reveals patterns the 10-point checklist did not catch at Pax validate-time. Five amendments proposed for Q-SDC v2.

### §1.1 Amendment A1 — Add 11th binary AC: "metric chain wiring verified"

**Triggering finding:** Sable F-04 audit + Mira F2-T9 Round 3 §1 surfaced `phase_g_protocol_compliance_gap` because the spec v1.2.0 §15.13.2 unlock mechanism was authored AT THE SPEC LAYER but the run-script `scripts/run_cpcv_dry_run.py:1093` `holdout_locked=True` was hardcoded AT THE EXECUTION LAYER. The sign-off chain (Aria spec review + Mira F2-T8-T1 + Beckett N7-prime + Quinn QA gate) ASSUMED the wiring was in place. **The 10-point checklist did not interrogate the metric→run-script→spec chain.**

**Proposed AC11 (11-point amendment):**

> **AC11 — Metric chain wiring verified.** For any story whose AC depend on a metric computation (DSR / PBO / IC / K1 / K2 / K3 / decay / hold-out / OOS measurement): the story MUST cite the EXACT file path + line range where the metric is wired AND name the agent (Aria architectural review OR Dex impl review) who has VERIFIED the wiring matches the spec text. Default boilerplate sentinel value (e.g., `holdout_locked=True` default) MUST be checked against the spec mechanism block at validate-time, NOT assumed.

**Why this is binary-verifiable at validate-time:** Pax can ASK in 10-point validate: "Does the story name the spec mechanism block + the run-script wiring file:line + the agent who verified concordance?" YES = AC11 PASS; NO = AC11 FAIL with required revision.

**Why this would have prevented ESC-013:** the ~5-10 LoC fix at `scripts/run_cpcv_dry_run.py:1093` was a **wiring assumption** — Mira spec v1.2.0 §15.13.2 mechanism block was authored, but no Aria architectural sign-off explicitly traced "spec §15.13.2 → CLI flag `--phase G` → `holdout_locked=False`" at validate-time. AC11 would have forced that trace.

**Impact estimate:** ~0.25 session per story (Pax validate-time interrogation; agent answers from existing artifacts). Negative externality if skipped: 1 ESC escalation (~5-10 sessions). **Net cost is < 5%** of avoided escalation. **Adopt as MUST.**

### §1.2 Amendment A2 — Spec-first protocol T0a-T0e' chain enumeration mandate

**Triggering finding:** T002 spec amendments v1.1.0 and v1.2.0 introduced new mechanism blocks (§15.13.x unlock procedure; §15.13.5 K3 decay test; §15.13.7 one-shot binding; §15.13.8 disposition). Each was authored INCREMENTALLY across ESC councils — the chain "T0a baseline spec → T0b first amendment → T0c second amendment → T0d ...→ T0e' final pre-execution version" was reconstructable BUT not enumerated explicitly in any single story file. **River @sm draft authority did not prescribe chain-enumeration; Pax @po validate did not interrogate it.**

**Proposed Q-SDC v2 amendment:**

> Story drafts (River authority) for any story whose AC consume a spec MUST include a **§Spec Chain** subsection naming: (i) base spec yaml version + sha256; (ii) ALL amendment revisions consumed (T0a-T0e') with their dates + ESC ratifications; (iii) the FINAL pre-execution spec version that the story executes against. Pax 10-point validate verifies the chain is COMPLETE before draft → ready transition.

**Why this is binary-verifiable:** Pax checks (i) base hash present; (ii) every amendment row has date + ESC ratification cite; (iii) final pre-execution version is identified. **Chain incomplete = NO-GO required-fixes list.**

**Why this would have prevented ESC ambiguity:** when ESC-013 §4 council debated whether §15.13.7 binds parquet-read or K3 decay measurement, the dispute traced to UNCERTAINTY about which spec amendment introduced what semantic. Explicit chain enumeration would have surfaced the disagreement at validate-time, not at Mira Round 3 §1 surfacing.

**Impact estimate:** ~0.5 session per story for River draft + ~0.15 session for Pax validate. **Adopt as MUST for ML/spec-consuming stories; SHOULD for infrastructure stories.**

### §1.3 Amendment A3 — Story scope discipline: 3-rounds-is-unsustainable lesson

**Triggering finding:** T002 epic produced **3 ESC escalation rounds** (ESC-011 scope, ESC-012 strategy fate, ESC-013 protocol gap) PLUS a 4th outcome resolution (Round 3.1 FINAL FAIL). Each escalation consumed 5-15 sessions of council deliberation BEYOND impl/QA work. **3 escalations per epic is not sustainable** under squad bandwidth realities.

**Proposed Q-SDC v2 amendment:**

> Epic-level scope discipline (PM @pm + PO @pax authority): an epic that triggers a **3rd ESC escalation** MUST trigger a **circuit-breaker review** before any 4th escalation is authored. The circuit-breaker review (Pax + PM + Aria + active research authority) decides: (a) is the epic salvageable with bounded retire? (b) is the next ESC actually a NEW epic? (c) has scope creep absorbed effort that should have spawned a parallel epic? Default action: retire-with-evidence; require explicit ratification to author 4th ESC.

**Why this is enforceable:** ESC councils are tracked in `docs/councils/`. Pax counts ESC files per epic; reaching 3 triggers the review automatically. PM authority enforces the gate.

**Why this would have improved T002:** ESC-013 was the protocol gap fix. ESC-014 (had it occurred under residual INCONCLUSIVE outcome) would have been prevented by Round 3.1 PROPER computation. But the 3-ESC count IS the trigger to reflect on whether T002.5 / T002.6 / T002.7 should have been distinct epics. Lesson: **aim for ≤ 2 ESCs per epic next-time**.

**Impact estimate:** ~1 session per circuit-breaker review (rare event). Positive externality: prevents indefinite ESC chains.

### §1.4 Amendment A4 — Round 3.1 append-only revision discipline as canonical pattern

**Triggering finding:** Mira F2-T9 Round 3 → Round 3.1 supersession was handled via **append-only revision** under spec §15 discipline (Round 3 sign-off integrity preserved; Round 3.1 added as new entry that supersedes the verdict NOT the audit trail). This worked. It should be the canonical pattern for ANY post-fix re-verdict.

**Proposed Q-SDC v2 amendment:**

> When a story's QA gate verdict is superseded due to a protocol fix or post-execution amendment: the new verdict MUST be authored as an APPEND-ONLY revision (Round X → Round X.1 → Round X.2; never overwrite Round X file). The supersession is metadata at the file frontmatter; the prior verdict text is preserved verbatim. PRR / PRR-equivalent disposition rules cite the append-only revision chain.

**Why this is canonical:** preserves audit trail under Article IV (every verdict claim source-anchored); prevents historical revisionism; matches MANIFEST R15 spec versioning + research-log invariant pattern. **Adopt as MUST.**

### §1.5 Amendment A5 — Article IV self-audit row count threshold

**Triggering finding:** Pax ESC-013 ballot §8 had ~12 anchor-traced rows; Pax ESC-012 ballot had similar; Mira Round 3.1 audit had 7 anchors. The **richer the self-audit, the lower the invention risk**.

**Proposed Q-SDC v2 amendment (SHOULD not MUST):**

> Vote ballots, story drafts, and QA gates SHOULD include an Article IV self-audit table with a minimum of 5 anchor-traced rows (claim → source). Stories whose AC are binary-verifiable and trace cleanly to spec yaml may have fewer; stories that cite emergent reasoning or analogies SHOULD have more (≥ 7).

**Impact estimate:** ~0.1 session per ballot/gate. Cheap; high benefit. **Adopt as SHOULD.**

### §1.6 Summary table of Q-SDC v2 amendments

| Amendment | Severity | Estimated cost/story | Triggering T002 lesson |
|---|---|---|---|
| A1 — AC11 metric chain wiring | MUST | ~0.25 session | ESC-013 phase_g_protocol_compliance_gap (Sable F-04) |
| A2 — Spec chain T0a-T0e' enumeration | MUST (ML) / SHOULD (infra) | ~0.65 session | ESC-013 §4 §15.13.7 reading dispute |
| A3 — 3-ESC circuit-breaker | MUST (epic-level) | ~1 session per trigger | T002 3-ESC count unsustainable |
| A4 — Round X.Y append-only revision | MUST | ~0 session marginal | Round 3 → Round 3.1 worked-pattern |
| A5 — Article IV self-audit ≥ 5 anchors | SHOULD | ~0.1 session | Pax ESC ballots + Mira audits |

---

## §2 PRR registration discipline

PRR-20260430-1 (T002.7 Phase G OOS confirmation pre-committed disposition rule) was a **first-of-its-kind governance artifact** for the squad: a hash-frozen disposition rule authored BEFORE empirical run, with 4 branches (R15 PASS / R16 FAIL_K3_collapse / R17 FAIL_K1+K3_sustains / R18 INCONCLUSIVE residual). It worked. ESC-013 §4 ratified the pattern. Pax recommends promoting it canonical.

### §2.1 Pattern — "Pre-empirical hash-frozen disposition rule"

**The pattern:**

1. **Before** any empirical run with ambiguous outcome semantics, author a PRR-style governance artifact that:
   - Names the metric measurement(s) the run will produce
   - Enumerates ALL possible outcome branches (typically 3-5: clear PASS, clear FAIL with sub-classifications, INCONCLUSIVE residual)
   - Pre-specifies the disposition action for each branch
   - Hash-freezes the entire artifact via sha256 over file content
   - Cites the hash in the parent spec yaml (append-only revision per §15 discipline)
2. **During** the empirical run, no parameter / threshold / disposition mutation is permitted (Anti-Article-IV Guard #4 + #2).
3. **After** the run, the verdict authority (Mira / Quinn / Riven depending on metric type) authors a Round X.Y verdict that maps the empirical observation to ONE of the pre-committed branches.
4. **If** the residual INCONCLUSIVE branch fires, ESC escalation is automatic (the PRR pre-commits this — no fate pre-emption without council ratification).

### §2.2 Why promote canonical?

PRR-20260430-1 worked because it **decoupled the empirical observation from the disposition decision**. The N8 surprise (DSR=0.965 + IC=0.866 + PBO=0.163) would otherwise have triggered ad-hoc deliberation about whether to advance. Instead, the pre-committed K3 status `DEFERRED-sentinel-PASS NOT COMPUTED-PASS` automatically routed to §3.4 INCONCLUSIVE branch → ESC-013. **Disposition was pre-decided; only the empirical observation was new.**

This is the canonical pattern for protecting against:
- Outcome-driven goalpost-moving (Anti-Article-IV Guard spirit)
- Ad-hoc threshold relaxation under surprise observations
- Bonferroni budget inflation through "just one more run with adjusted parameters"
- Survival bias in retrospect

### §2.3 Per-spec PRR breaking_fields[] + carry_forward_unchallenged[] discipline

**Proposal:**

> Every spec yaml amendment (vN → vN+1) authored under §15 append-only revision MUST include in the revision metadata:
> - `breaking_fields[]` — explicit list of spec fields whose semantics CHANGE under the new amendment (triggers full Bonferroni reset; n_trials=1 fresh; no carry-forward)
> - `carry_forward_unchallenged[]` — explicit list of spec fields whose semantics PRESERVE verbatim from prior version (preserves n_trials carry-forward; predictor IP / cost atlas / engine_config / cv_scheme reusability invariant honored)
> - The two lists MUST be DISJOINT and EXHAUSTIVE relative to the spec yaml field set.

**Why this matters:** Bonferroni budget accounting depends on whether amendments break or preserve. ESC-013 R6 reusability invariant codified this for T002 specifically; per-spec PRR-style discipline generalizes it. Mira spec authority owns the breaking/carry-forward classification at amendment-time.

**Worked example for T003 (post-Round 3.1):**

```yaml
amendment: T003-vN+1
breaking_fields:
  - data_splits.hold_out_virgin (NEW window 2026-05-01..2026-09-30; OLD 2025-07..2026-04 BURNED + FORFEITED)
  - trading_rules.entry_filter (NEW conviction threshold τ = P80(|predictor|))
  - n_trials_count (T002 carried 5; T003 adds 3 → total 8 for Bonferroni penalty)
carry_forward_unchallenged:
  - feature_set.predictor (-intraday_flow_direction at {16:55, 17:10, 17:25, 17:40} BRT — predictor IP)
  - cost_atlas (v1.0.0 FROZEN per ESC-012 user reframe)
  - engine_config_sha256 (ccfb575a... DMA2 latency profile)
  - cv_scheme (CPCV N=10 k=2 45 paths embargo=1)
  - rollover_calendar
  - predictor_definition_sha256
  - thresholds (DSR > 0.95 / PBO < 0.5 / IC > 0; UNMOVABLE)
```

### §2.4 Pax recommendation §2 summary

- **PROMOTE PRR-20260430-1 pre-committed-disposition pattern as canonical** for all forward stories with ambiguous-outcome empirical runs (Mira spec authority; Pax governance authority).
- **MANDATE breaking_fields[] + carry_forward_unchallenged[] in every spec amendment revision metadata** (Mira spec authority; Pax 10-point validates list completeness at story validate-time).
- **CITE PRR pattern in Q-SDC v2 documentation** so River draft authority defaults to authoring a PRR for any new ambiguous-outcome story.

---

## §3 Backlog prioritization for H_next — Quant Council fit ratification

Quant Council 2026-05-01 produced 5 ballots (Mira, Beckett, Riven, Kira, Nova) ranking H_next candidates. From Mira ballot §1.2 + Beckett ballot §1.4: top-3 candidates are:

1. **(a) Conviction-conditional sizing** — pre-register `τ = P80(|predictor|)` from F2 in-sample; trade only `|predictor_t| ≥ τ` on new OOS; n_filtered ≈ 760 events (above R9 250 floor)
2. **(d) Label-horizon swap to `ret_to_close_BR` 17:55** — replace F2's intraday `ret_forward_to_17:55_pts` with full session-close return; full 3800 events preserved
3. **(c) Asymmetric exit (R-multiple barriers)** — `tp_pts = 1.5 × ATR_5m`, `sl_pts = 0.6 × ATR_5m`; full 3800 events; 2 new hypotheses

Pax authority: ratify each candidate against (i) story scope discipline, (ii) 10-point binary AC verifiability, (iii) Article IV traceability.

### §3.1 Candidate (a) — Conviction-conditional sizing

| Criterion | Pax assessment |
|---|---|
| **Story scope discipline** | BOUNDED — single new hypothesis (threshold τ); single re-run; identical predictor IP + cost atlas + cv_scheme + engine_config; breaking_fields = {trading_rules.entry_filter, n_trials_count}; carry_forward = {predictor, atlas, engine, cv_scheme, thresholds}. Fits §2.3 PRR pattern cleanly. |
| **10-point binary AC** | AC1 τ pre-registered from F2 in-sample distribution P80 with sha256 hash; AC2 NEW hold-out window pre-registered (forward-time per Mira §3.2); AC3 n_filtered ≥ 250 floor verified post-filter; AC4 PRR-T003-1 4-branch disposition authored before run; AC5 Mira F-T verdict against PRR; AC6 Riven 3-bucket reclassify; AC7 Pax cosign + Gage push; AC8 Bonferroni n_trials=8 (5 carry + 3 new) per Mira §2.2; AC9 ESC-013 R6 reusability verified; AC10 spec chain T0a-T0e' enumerated; AC11 metric chain wiring verified (per §1.1 above). All 11 binary-verifiable. |
| **Article IV traceability** | PASS — every claim traces to T002 Round 3.1 evidence (predictor rank-stability OOS) + Mira Quant ballot §1.2 ranking + spec text. Threshold τ = P80 is justified empirically (top-quintile filter by magnitude); not invented. |
| **Pax verdict** | **RATIFIED FIT** — Quant rank #1; story scope BOUNDED; AC binary-verifiable; Article IV clean. |

### §3.2 Candidate (d) — Label-horizon swap

| Criterion | Pax assessment |
|---|---|
| **Story scope discipline** | BOUNDED — single hypothesis (label semantic re-derivation); same predictor; full 3800 events; breaking_fields = {label.horizon, n_trials_count}; carry_forward = {predictor, atlas, engine, cv_scheme}. |
| **10-point binary AC** | All 11 binary-verifiable analogous to §3.1; key change: AC1 names new label `ret_to_close_BR` 17:55 with sha256 hash + spec citation. |
| **Article IV traceability** | PASS — label semantic change is Mira spec authority; Mira Quant ballot §1.2 ranks #2 with rationale (different time horizon → different cost-atlas-to-edge ratio). Not invented. |
| **Pax verdict** | **RATIFIED FIT** — Quant rank #2; story scope BOUNDED; AC binary-verifiable; Article IV clean. |

### §3.3 Candidate (c) — Asymmetric exit (R-multiple barriers)

| Criterion | Pax assessment |
|---|---|
| **Story scope discipline** | BOUNDED but slightly less than (a)/(d) — 2 new hypotheses (tp ratio 1.5 + sl ratio 0.6). Mira §1.2 notes "2 new hypotheses justified per Bonferroni accounting". Acceptable but tighter scope discipline required. |
| **10-point binary AC** | All 11 binary-verifiable; key risk AC8 Bonferroni accounting becomes n_trials = 5 + 3 + 1 (extra hypothesis from asymmetric pair) = 9 if council strictly counts; Mira §2.2 already accounts for this. |
| **Article IV traceability** | PASS — Lopez de Prado AFML §17 triple-barrier asymmetry is canonical; tp/sl ratios chosen empirically from F2 PnL distribution skew (not invented). |
| **Pax verdict** | **RATIFIED FIT (with caveat)** — Quant rank #3; story scope acceptably BOUNDED; AC binary-verifiable; Article IV clean. **Caveat:** if §4 bandwidth budget binds tightly, candidate (c) deferable to T003-followup epic. |

### §3.4 Sequencing recommendation

Given §4 bandwidth budget recommendation (≤ 20 sessions per candidate; ≤ 60 sessions total H_next), Pax recommends:

| Slot | Candidate | Sessions | Sequencing rationale |
|---|---|---|---|
| 1 | (a) Conviction-conditional sizing | ≤ 20 | Highest information density per Mira ranking; minimal scope; fastest to verdict |
| 2 | (d) Label-horizon swap | ≤ 20 | Independent of (a); can run in parallel after (a) cosign |
| 3 | (c) Asymmetric exit | ≤ 20 | Defer until (a)+(d) verdict known; if either passes, (c) becomes optional refinement; if both fail, (c) is final shot before epic-level retire |

**Hold-out window decision (Mira §3.2):** forward-time 2026-05-01..2026-09-30 (5 months); pre-registered TODAY at council ratification; data accumulates wall-clock; verdict at Q3 2026. (Pax concurs Mira recommendation; old hold-out 2025-07..2026-04 FORFEITED per ESC-013 R9.)

### §3.5 Pax §3 ratification summary

All 3 Quant top-ranked candidates **RATIFIED FIT** for forward backlog under bounded scope, 11-point binary AC, Article IV traceability. Sequencing (a) → (d) → (c). Bandwidth-cap §4 binding. Mira §1.2 (b) Multi-timeframe conditioning REJECTED concurs Pax (Bonferroni inflation; non-pre-registered features; defer to T004+ epic).

---

## §4 Squad bandwidth allocation for H_next

### §4.1 T002 burn audit

T002 epic consumed roughly **50+ squad sessions** across phases T002.0-T002.7. Approximate breakdown:

| Phase | Sessions | Notes |
|---|---|---|
| T002.0a-T002.0h (warmup, ADR-1, dry-run, R15) | ~15-18 | Foundational infrastructure |
| T002.1-T002.1.bis (make_backtest_fn, factory) | ~5-7 | Aria Option B integration |
| T002.5 (telemetria + EOD reconciliation) | ~3-5 | Partial; resumes post-T002 retire |
| T002.6 (F2 spec author + IC pipeline audit) | ~10-12 | Mira deep audit + spec amendments |
| T002.7 (Phase G prep + N8 + N8.1/N8.2 PROPER) | ~12-15 | ESC-012 + ESC-013 path B execution |
| Council overhead (ESC-011, ESC-012, ESC-013) | ~10-12 | 5-7 ballots per ESC × 3 ESC |
| **Total** | **~55-70 sessions** | Order of magnitude 50+ confirmed |

### §4.2 Why 50+ sessions is unsustainable as default

- Each ESC escalation costs 5-7 ballots × 30-90 min/ballot = ~3-10 squad-sessions per ESC. **3 ESCs = 9-30 sessions of council overhead alone.**
- Spec amendments v1.1.0 → v1.2.0 → (Round 3.1 v1.2.1 patch) cost ~3 sessions each in Mira authoring + Pax validate cycles.
- Single-iteration discipline was violated in T002.7 (N8 → N8.1 → N8.2 PROPER required protocol fix re-run; 3 iterations).

### §4.3 H_next bandwidth budget proposal

**Pax recommendation:**

| Bound | Limit | Rationale |
|---|---|---|
| **Per-candidate session cap** | ≤ 20 sessions | 40% of T002 burn; forces tighter scope; prevents indefinite drift |
| **Per-candidate ESC cap** | ≤ 1 ESC escalation | T002 had 3; H_next aim for ≤ 1 per candidate |
| **Total H_next budget (3 candidates)** | ≤ 60 sessions | Conservative ceiling; soft trigger at 45 (75%) for circuit-breaker review |
| **Single-iteration discipline** | MUST | Each candidate gets ONE empirical run on the new pre-registered hold-out; no N → N.1 → N.2 chains permitted (PRR pre-commits the disposition; residual INCONCLUSIVE auto-escalates ESC ONCE only) |
| **Circuit-breaker** | At 3rd ESC across H_next epic | Per §1.3 amendment A3; triggers epic-level retire-with-evidence review |

### §4.4 Trade-off analysis

Tighter budget WILL force:
- Pre-registered binary disposition rules (§2 PRR pattern) authored BEFORE empirical run — no post-run goalpost
- Spec chain enumeration AT DRAFT TIME (§1.2 amendment A2) — no incremental spec amendments mid-execution
- Metric chain wiring verified AT DRAFT TIME (§1.1 amendment A1) — no protocol-compliance gaps surfaced post-execution
- Story scope discipline AT VALIDATE TIME (Pax 10-point ≥ 9/10 hard floor; AC11 binary check)

These are the EXACT amendments §1 proposes. **§1 + §4 are mutually reinforcing**: tighter Q-SDC v2 process discipline enables tighter bandwidth budget enables shorter epic cycles enables faster H_next verdict.

### §4.5 Comparison: H_next ideal-case vs T002 actual

| Metric | T002 actual | H_next target |
|---|---|---|
| Sessions per epic | 55-70 | 45-60 |
| ESCs per epic | 3 | ≤ 2 (1 per candidate ideal) |
| Spec amendments per epic | 2 (v1.1, v1.2) | ≤ 1 per candidate |
| Empirical re-runs | 3 (N8, N8.1, N8.2) | 1 per candidate (single-iteration discipline) |
| Wall-clock to verdict | ~5 weeks | ~3-4 weeks per candidate; total ~9-12 weeks for 3 candidates |
| Council ballot count | 18+ ballots across 3 ESC | ≤ 10 ballots total H_next |

### §4.6 Pax §4 recommendation

**Adopt H_next budget cap ≤ 20 sessions per candidate, ≤ 60 total, single-iteration discipline binding, circuit-breaker at 3rd ESC.** This is enforceable via Pax 10-point checklist (AC binary; bandwidth tracker citation in story file) + PM @pm epic-level governance authority.

---

## §5 Personal preference disclosure

Per autonomous mode council protocol, Pax discloses 5 personal preferences as tie-breakers:

### §5.1 Preference (a) — Continuity with prior council ratifications

Pax cosigned ESC-011 (5/5 unanimous APPROVE_OPTION_C), ESC-012 (5/6 supermajority APPROVE_PATH_B), ESC-013 (path-iv preferred). H_next §3 ratifications continue this pattern: ratify Quant top-3 fit-for-scope; defer (b) regime conditioning; preserve all 21 ESC-013 binding conditions C1-C21 carry-forward to T003+.

### §5.2 Preference (b) — Information density per session invested

Mira Quant ballot §1.2 ranking maximizes info density (HIGH on Bonferroni feasibility + sample size + falsifiability). Pax §3 ratifications preserve this. §4 bandwidth budget further enforces density (forces ≤ 20 sessions per candidate → ≤ 1 ESC per candidate → faster verdict).

### §5.3 Preference (c) — Article IV honesty (no invention; falsifiable)

§1 amendments A1+A2+A3+A4+A5 ALL preserve Article IV (every amendment traceable to T002 lesson; no invention). §2 PRR pattern strengthens Article IV (pre-empirical hash-frozen disposition forecloses outcome-driven goalpost-moving). §3 candidate ratifications all Article IV clean. §4 bandwidth budget non-Article IV-relevant (process-side).

### §5.4 Preference (d) — Story scope discipline

§1 amendments A1+A2 enforce scope at DRAFT and VALIDATE times. §2 breaking_fields[] / carry_forward_unchallenged[] discipline enforces scope at AMENDMENT time. §3 candidate ratifications verify scope BOUNDED. §4 bandwidth cap enforces scope EX-POST. **Strongest tie-breaker dimension for Pax authority.**

### §5.5 Preference (e) — Retro-clarity (post-mortem audit-friendliness)

§1 A4 (Round X.Y append-only revision) preserves audit trail. §2 PRR canonical pattern + breaking_fields[]/carry_forward_unchallenged[] enable cross-epic retrospective. §4 H_next vs T002 comparison table (§4.5) provides retro reference for IMPL Council 2026-Q3.

### §5.6 Aggregated preference

All 5 preferences align with the §1 + §2 + §3 + §4 substantive verdict. No preference-vs-criteria conflict; preferences serve as tie-breakers only.

---

## §6 Article IV self-audit

| Claim category | Trace anchor |
|---|---|
| Sable F-04 finding (metric chain wiring assumed-but-unbuilt) | `docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md` + Mira F2-T9 Round 3 §1 |
| 10-point checklist (PO authority) | `.aiox-core/development/tasks/validate-next-story.md` + AIOX framework `story-lifecycle.md` rules |
| ESC-013 phase_g_protocol_compliance_gap classification + C1-C21 binding conditions | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-pax-vote.md` §7 + ESC-013 resolution |
| PRR-20260430-1 §3.1-§3.4 4-branch hash-frozen disposition rule | `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` |
| Mira spec v1.2.0 §15.13.x mechanism block + Round 3.1 FINAL verdict | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md@v1.2.0` + `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` |
| Spec yaml v0.2.3 thresholds DSR > 0.95 / PBO < 0.5 / IC > 0 UNMOVABLE | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` v0.2.3 + Anti-Article-IV Guard #4 + ESC-011 R14 |
| Quant Council 2026-05-01 top-3 candidate rankings (a, d, c) | `docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-mira-vote.md` §1.2 + `COUNCIL-2026-05-01-QUANT-alpha-discovery-beckett-vote.md` §1.4 |
| ESC-011 R10 successor-story authority + ESC-012 R6 reusability invariant + ESC-013 R6 carry-forward | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` + ESC-012 + ESC-013 resolution files |
| Article II Gage @devops EXCLUSIVE push authority | `.claude/rules/agent-authority.md` Delegation Matrix |

**Self-audit verdict:** every claim in §1-§5 traces to a verifiable source (Mira Quant ballot / Beckett Quant ballot / ESC resolutions / Pax ESC ballots / PRR-20260430-1 / Mira spec v1.2.0 / parent yaml / framework rules). **NO invention.** **NO threshold mutation proposed** (Anti-Article-IV Guard #4 explicitly preserved). **NO Bonferroni mutation proposed** (n_trials carry-forward = 5; +3 new for H_next per Mira §2.2). **NO source code modification by Pax during ballot.** **NO commit / push performed by Pax during this vote.** **NO spec yaml mute by Pax during ballot** (§1 amendments are process-side; §2 PRR is governance-side; §3 ratification is backlog-side; §4 budget is meta-process; spec yaml unchanged).

### §6.1 Anti-Article-IV Guard cross-check

| Guard | Pax vote action | Compliance |
|---|---|---|
| #1 Dex impl gated em Mira spec PASS | §3 candidate ratifications all gated on Mira spec authoring (T003+ specs not yet authored) | PRESERVED |
| #2 NO engine config mutation at runtime | §2.3 carry_forward_unchallenged[] explicitly preserves engine_config_sha256 | PRESERVED |
| #3 NO touch hold-out lock | §3 hold-out: forward-time NEW window; old hold-out FORFEITED per ESC-013 R9 | PRESERVED |
| #4 Gate 4 thresholds UNMOVABLE | §1, §2, §3 all preserve DSR > 0.95 / PBO < 0.5 / IC > 0 | PRESERVED |
| #5 NO subsample backtest run | §4.3 single-iteration discipline binding | PRESERVED |
| #6 NO Gate 5 disarm | T002 retired; Gate 5 fence preserved per ESC-013 R10 carry-forward | PRESERVED |
| #7 NO push (Gage EXCLUSIVE) | Pax authoring vote document only; no commit/push performed | PRESERVED |
| #8 Verdict-issuing protocol (`*_status` provenance) | §1.1 AC11 metric chain wiring verified strengthens Guard #8 forward | PRESERVED + STRENGTHENED |

All 8 guards preserved by Pax IMPL ballot.

---

## §7 Pax cosign

```
Author: Pax (@po — Product Owner) — story scope, AC integrity, 10-point checklist guardian, backlog prioritization
Council: IMPL-2026-05-01 — squad instrumentation, story-lifecycle, PRR registration, H_next backlog, squad bandwidth
Date (BRT): 2026-05-01
Branch: t002-1-bis-make-backtest-fn (Pax authoring; no commit/push performed)
Verdict summary: §1 5 Q-SDC v2 amendments (A1 AC11 metric chain wiring MUST + A2 spec chain T0a-T0e' enumeration MUST + A3 3-ESC circuit-breaker MUST + A4 Round X.Y append-only MUST + A5 Article IV ≥5 anchors SHOULD); §2 PRR-20260430-1 pre-empirical hash-frozen disposition pattern PROMOTED canonical + breaking_fields[]/carry_forward_unchallenged[] per-spec discipline MANDATED; §3 Quant top-3 candidates (a) conviction-conditional sizing + (d) label-horizon swap + (c) asymmetric exit ALL RATIFIED FIT story scope discipline + 11-point binary AC + Article IV; sequencing (a)→(d)→(c) with new forward-time hold-out 2026-05-01..2026-09-30; §4 H_next bandwidth budget ≤ 20 sessions per candidate + ≤ 60 total + single-iteration discipline binding + circuit-breaker at 3rd ESC; §5 5 personal preferences disclosed (continuity / density / Article IV honesty / scope discipline / retro-clarity) all aligned with substantive verdict; §6 9-anchor Article IV self-audit + 8-guard cross-check ALL PRESERVED.
Article II: NO push performed by Pax during vote authoring. Gage @devops authority preserved.
Article IV: every clause §1-§6 traces to verifiable anchor (Sable F-04 audit / 10-point checklist / ESC-013 ballot / PRR-20260430-1 / Mira spec v1.2.0 / Round 3.1 sign-off / parent yaml / Quant Council ballots / framework rules). NO invention; NO threshold mutation proposed (Anti-Article-IV Guard #4 explicitly preserved); NO Bonferroni expansion proposed (n_trials carry-forward = 5 + 3 new = 8 for H_next per Mira §2.2 ratified); NO hold-out modification proposed (forward-time NEW window per Mira §3.2 ratified; OLD hold-out FORFEITED per ESC-013 R9); NO source code modification by Pax during ballot; NO commit / push performed by Pax during this vote; NO spec yaml mute by Pax during ballot (amendments are process/governance/backlog side; spec yaml unchanged).
Anti-Article-IV Guards #1-#8: all preserved per §6.1 cross-check.
Authority boundary: Pax issues this implementation-council ballot under PO authority over story-lifecycle + PRR governance + backlog prioritization + bandwidth budgeting; does NOT pre-empt Mira spec authoring authority over T003+ spec yaml drafts; does NOT pre-empt River @sm draft authority over T003+ stories; does NOT pre-empt Aria architectural review authority; does NOT pre-empt Dex impl authority; does NOT pre-empt Quinn QA gate authority; does NOT pre-empt Beckett N1 H_next run authority; does NOT pre-empt Riven 3-bucket reclassify authority; does NOT pre-empt Sable governance audit authority; does NOT pre-empt Gage push authority; does NOT pre-empt PM @pm epic orchestration authority. Pax exercises ESC-011 R10 forward-research adjudication authority + 10-point checklist guardian authority + spec scope discipline authority + backlog prioritization authority + ESC-012 R13 successor-story discipline authority + ESC-013 21 binding conditions C1-C21 carry-forward authority.
Council fidelity: ESC-011 5/5 + ESC-012 5/6 + ESC-013 supermajority ratifications PRESERVED (R1-R20 + R1-R17 + C1-C21 ALL carry-forward to T003+; particularly ESC-013 R6 reusability invariant binding for predictor IP / engine_config / cost atlas / cv_scheme / rollover calendar / Bonferroni semantics across H_next candidates).
Mira Round 3.1 FINAL verdict authority preserved (Pax does NOT supersede; Pax authors process amendments + PRR pattern promotion + backlog ratification + bandwidth budgeting under PO authority).
Spec yaml status: NO MUTATION proposed by Pax. Amendment §1.2 A2 spec chain enumeration is process-side metadata for stories that consume specs; §2 breaking_fields[]/carry_forward_unchallenged[] is per-amendment revision metadata authored by Mira spec authority at T003+ amendment time. Spec yaml v0.2.3 thresholds at L207-209 UNMOVABLE forward.
Round 3 / Round 3.1 sign-off integrity: PRESERVED (Round 3.1 FINAL is Mira authoritative; §1.4 A4 amendment codifies the append-only revision pattern that worked).
Independence: Article IV §6 — Pax did NOT read other IMPL ballots (Aria, Riven, Sable, Kira, Mira) before authoring this ballot.

Cosign: Pax @po 2026-05-01 BRT — Implementation Council ballot under autonomous mode.
```

---

— Pax @po, 2026-05-01 BRT — Impl Council ballot (squad instrumentation + story-lifecycle Q-SDC v2 + PRR canonical promotion + H_next backlog ratification + squad bandwidth budget).
