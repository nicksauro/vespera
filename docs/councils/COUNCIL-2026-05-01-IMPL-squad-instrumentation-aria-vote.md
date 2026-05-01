---
council: IMPL-2026-05-01
council_topic: Implementation Council — squad instrumentation post T002 RETIRE FINAL (ESC-011/012/013 closure + Sable F-01..F-04 + F2-T9-OBS-1) for next Q-SDC cycle on H_next
voter: Aria @architect
voter_authority: System architecture; factory pattern + closure isolation guardianship; spec yaml threshold guardianship; engineering-placement bindings; Q-SDC v2 architectural-surface adjudication; Anti-Article-IV Guards #3/#4/#8 cosignatory; F2-T0b/F2-T0b' precedence
date_brt: 2026-05-01
mode: autonomous
branch: t002-1-bis-make-backtest-fn (working tree)
ballot_independence: Aria did NOT read other IMPL-2026-05-01 agent votes pre-cast (task discipline)
predecessor_councils:
  - ESC-011 (gate 4 scope; Beckett N6 baseline ratification)
  - ESC-012 (T002 strategy fate; APPROVE_PATH_B 5/6 supermajority + Riven Path C minority dissent)
  - ESC-013 (T002 Phase G protocol-compliance gap; APPROVE_PATH_iv 5/5)
  - QUANT-2026-05-01 (alpha discovery direction post T002 retire; H_next pre-vote)
inputs_consumed:
  - docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-aria-vote.md (own ESC-013 ballot — C-iv1..C-iv6 + C-iv-NEG-1..-NEG-4 binding precedent)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-sable-vote.md (Sable F2-T9-OBS-1 §2 admission + R5 audit scope corrective action — process-side audit-perimeter widening canonical text)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-mira-vote.md (Mira top-3 H_next ranked: conviction-conditional sizing / label horizon swap / asymmetric R-multiple exit)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-riven-vote.md (Riven §11.5 #8/#9/#10 NEW pre-conditions + 3-bucket post-mortem v4 NEW buckets)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-beckett-vote.md (Beckett simulator-lens carry-forward assets §1.2 + engine-config v1.2.0 perf round PENDING)
  - docs/ml/specs/T002-gate-4b-real-tape-clearance.md §15 (sign-off chain canonical pattern; PRE-AUTHORED §15.13 Phase G mechanism)
  - docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md (F2-T0b' Option D placement design — window-agnostic orchestration helper)
  - docs/architecture/ADR-5-canonical-invariant-hardening.md (tri-sig content_sha256 byte-stability invariant)
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md (Riven 3-bucket framework canonical)
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md §10.3 (engine-config v1.2.0 perf optimization opportunity flagged — wall-time 188 min)
  - docs/backtest/T002-beckett-n6-2026-04-29.md (latency_dma2 design residing canonical)
inputs_NOT_consumed_pre_cast:
  - other IMPL-2026-05-01 agent ballots (independent vote; task discipline)
scope_discipline:
  - Aria votes on ARCHITECTURAL-SURFACE-CHANGE TO Q-SDC v2 — protocol shape, factory contracts, regression-guard test surface, perf-optimization architectural decision
  - Aria does NOT pre-empt Pax Q-SDC orchestration authority, Mira spec-authoring authority, Riven §11.5 + 3-bucket authority, Sable audit-perimeter authority, Beckett baseline-run authority, Quinn QA-gate authority, Dex impl-side authority, Gage Article II push exclusivity
verdict_summary: |
  §1 Q-SDC v2 architectural changes — ratify FOUR minimal-surface protocol amendments:
    (1) §15.x sign-off chain canonical AIOX template promotion (Sable F-01 closure pattern);
    (2) Anti-Article-IV Guard #9 NEW — verdict-vs-reason-text consistency cross-protocol invariant
        (F2-T5-OBS-1 enforcement gap → contract);
    (3) caller-wiring task explicit row in sign-off chain (F2-T9-OBS-1 → not implicit-but-unbuilt);
    (4) closure-body Phase Literal completeness assertion (regression guard against N8.1-class
        argparse-choice gaps).
  §2 Reusable F2 + Phase G artifacts catalog for H_next — preserve verbatim:
    cpcv_aggregator.ic_holdout_locked flag pattern; info_coef.bootstrap_ci pattern; Mira spec template
    §15 (IC wiring + decay sub-clause + status flag); Riven 3-bucket post-mortem framework;
    Beckett latency_dma2 spec; Nova RLP+rollover spec.
  §3 NEW regression-guard tests — three contract tests:
    (a) verdict-vs-reason consistency contract;
    (b) Phase Literal completeness check;
    (c) cross-protocol propagation (status flag persistence ic_holdout_status / phase / holdout_unlocked).
  §4 Engine config v1.2.0 perf optimization — RECOMMEND CARRY-FORWARD as parallel architectural
    track (parquet pre-aggregation + session caching across folds); 188 min → ~60-90 min target;
    NON-BLOCKING for H_next first run; OPTIONAL for first H_next CPCV trial; MANDATORY before
    H_next reaches Bonferroni n_trials=3+.
  §5 Personal preference disclosure — Aria primary preference architectural-minimum-disruption
    + maximum-information per-effort; bias toward protocol-amendment over framework-rewrite.
  §6 Article IV self-audit verbatim with 11 anchors verified.
  §7 Aria cosign 2026-05-01 BRT — Implementation Council ballot.
---

# IMPL-2026-05-01 Aria Architectural Vote — squad instrumentation for Q-SDC v2 (post T002 RETIRE FINAL)

> **Authority basis:** Aria @architect under AIOX agent-authority matrix (system architecture decisions, technology selection, integration patterns, factory pattern + closure isolation guardianship, spec yaml threshold guardianship, Q-SDC v2 architectural-surface adjudication). Per the IMPL-2026-05-01 council framing, Aria adjudicates **FROM SYSTEM DESIGN**: which minimal-surface protocol amendments to Q-SDC instrument the squad against the F2-T5-OBS-1 / F2-T9-OBS-1 / N8.1 closure-Literal-incompleteness / Round-1-IC-pipeline-orphan-code procedural gaps surfaced over T002 lifecycle, WITHOUT mutating Constitution Articles I-IV or the agent authority matrix (Article II push gate / Article IV no invention / R-rules R1-R15 carry-forward).
>
> **Self-consistency disclosure:** Aria voted APPROVE_PATH_B in ESC-012 + APPROVE_PATH_iv in ESC-013 with C-G1..C-G6 + C-iv1..C-iv6 conditions binding. The Q-SDC v2 amendments below ARE the procedural-cleanup mechanism for the gaps those ballots already conditioned on. Consistency preserved.
>
> **Discipline:** Aria did NOT read other IMPL-2026-05-01 agent votes pre-cast (task mandate). Independent ballot. No spec yaml mutation. No Constitution mutation. No agent-authority-matrix mutation.

---

## §1 Architectural changes for Q-SDC v2 (FOUR minimal-surface amendments)

### §1.1 Amendment QSDCv2-A1 — §15.x sign-off chain canonical AIOX template promotion (Sable F-01 closure)

**Procedural gap surfaced:** Mira spec v1.2.0 §15.13.12 sign-off chain row format (per-task: T-id / owner / inputs / outputs / sign-off authority / pre-condition / post-condition) was authored as a one-off in the T002 spec. Sable R5 audit (per ESC-013 Sable ballot §2) explicitly admitted: "R5 audited the R1-R17 envelope and trusted §15.13.12 sign-off chain to be Pax/Aria/Dex authority territory. *That trust delegation was the procedural gap.*" The §15.x sign-off chain is THE authoritative pre-run task ledger but lives outside the council-ratified ESC §4 R1-R17 condition list, creating a perimeter ambiguity that allowed F2-T8-T1 (Dex caller wiring) to be implicit-but-unbuilt.

**Architectural amendment (Q-SDC v2):**

- **Promote the §15.x sign-off chain row schema to a canonical AIOX template** (`.aiox-core/development/templates/spec-signoff-chain-tmpl.yaml`). All future H_next specs MUST author a §15.x sign-off chain section as a MANDATORY spec sub-section, NOT optional. Pax `*validate-story-draft` 10-point checklist gains a NEW point #11: "spec contains §15.x sign-off chain table with all caller-wiring tasks enumerated as standalone rows (not implicit in adjacent envelopes)".
- **Audit perimeter widening:** Sable R5-equivalent pre-run coherence audits MUST traverse BOTH (a) ESC §4 R1-R17 council-ratified conditions AND (b) spec §15.x sign-off chain rows. Sable corrective action per ESC-013 §2 ratified by IMPL-2026-05-01.
- **Authority binding:** Mira authors §15.x sign-off chain table; Pax validates row completeness; Aria thin-cross-checks for caller-wiring rows specifically; Sable cross-traverses both R-rules and §15.x rows in coherence audit.
- **Architectural surface impact:** ~50-100 LoC AIOX template + ~30-50 LoC `*validate-story-draft` task amendment + ~30 LoC Sable `coherence-audit-method.md` amendment. ZERO code-side mutation; ZERO factory contract impact; ZERO closure-body impact.

**Why this is minimal-surface:** the §15.x sign-off chain pattern ALREADY EXISTS (Mira spec v1.2.0). The amendment promotes it from one-off-in-T002-spec to canonical-AIOX-template + adds Pax/Sable enforcement hooks. No new authoring discipline; just enforcement.

### §1.2 Amendment QSDCv2-A2 — Anti-Article-IV Guard #9 NEW (verdict-vs-reason-text consistency cross-protocol invariant; F2-T5-OBS-1 enforcement gap closure)

**Procedural gap surfaced:** F2-T5-OBS-1 (Mira F2-T5 Round 2 finding, ratified Round 3 §3.2) — the verdict-layer in `evaluate_kill_criteria` could in principle emit a `verdict='PASS'` while `reason_text` still contained DEFERRED-sentinel language, OR emit `verdict='FAIL_K3'` while `reason_text` referenced a different kill clause. Dex commit `fadacf4` landed a short-circuit fix for the specific `ic_holdout_status='deferred'` → `K3` short-circuit case. BUT: the GENERAL invariant (verdict-text and reason-text MUST cross-validate against each other across ALL kill-criteria branches) is not contracted at the architectural level. The fix is point-in-time; the contract is missing.

**Architectural amendment (Q-SDC v2):**

- **NEW Anti-Article-IV Guard #9:** "Verdict-vs-reason consistency invariant — for any spec-yaml-defined kill-criteria evaluator function (Gate-4-class, Gate-5-class, K-criteria-class), the (verdict_label, reason_text) pair MUST cross-validate atomically: every verdict label has a defined set of allowed reason-text fragments, and every reason-text fragment maps to exactly one verdict label. The evaluator function MUST raise `InvalidVerdictReport` if the pair is inconsistent."
- **Contract enforcement mechanism:** the existing `InvalidVerdictReport` exception type (introduced in Mira spec v1.2.0 §15.5 + Dex `fadacf4`) is promoted from one-off T002 contract to canonical contract for ALL future Gate-N evaluator functions. NEW shared module `packages/vespera_metrics/verdict_contract.py` exposes a `validate_verdict_vs_reason(verdict, reason, allowed_pairs)` helper that all kill-criteria evaluators MUST consume.
- **Spec authoring discipline:** every H_next Mira spec MUST include a §-anchor "verdict-vs-reason allowed-pairs table" enumerating the (verdict_label, reason_text_pattern) cross-product. Pax `*validate-story-draft` checklist gains NEW point #12: "spec contains verdict-vs-reason allowed-pairs table at §-anchor; evaluator function consumes `validate_verdict_vs_reason` helper".
- **Architectural surface impact:** ~100-150 LoC NEW `verdict_contract.py` shared module + ~30-50 LoC test coverage + ~50 LoC Pax checklist amendment + ~30 LoC Mira spec template amendment. ZERO factory contract impact (helper is pure-function consumed at evaluator level); ZERO closure-body impact.

**Why this is minimal-surface:** the `InvalidVerdictReport` mechanism ALREADY EXISTS in T002 codebase. The amendment refactors it into a shared canonical contract + adds spec-authoring discipline. The fix Dex landed at `fadacf4` becomes the canonical pattern, not a one-off.

### §1.3 Amendment QSDCv2-A3 — caller-wiring task explicit row in sign-off chain (F2-T9-OBS-1 closure)

**Procedural gap surfaced:** F2-T9-OBS-1 (Mira F2-T9 Round 3 finding) — F2-T8-T1 Dex caller wiring (`scripts/run_cpcv_dry_run.py:1088-1102`, `--phase G` argparse choice + `holdout_locked=False` propagation) was authored in Mira spec §15.13.12 sign-off chain row but was NOT extracted as a Sable R5 audit standalone pre-N8 prereq. The task lived ambiguously between the Mira spec sign-off chain and the ESC-012 R1-R17 council-ratified conditions, and was implicit-but-unbuilt at N8 launch. Beckett N8 ran under Phase F protocol against the Phase G window producing INCONCLUSIVE.

**Architectural amendment (Q-SDC v2):**

- **NEW canonical row class in §15.x sign-off chain template:** "caller-wiring task row" — distinct from "spec-internal task row" (algorithmic / aggregator / metric definition tasks) and from "data-plumbing task row" (manifest / parquet / cost atlas tasks). Caller-wiring tasks are tasks that connect spec-pre-authored mechanisms (e.g., `compute_ic_from_cpcv_results(holdout_locked=False)` per spec §15.13.2) to invocation surfaces (e.g., `scripts/run_cpcv_dry_run.py` argparse `--phase G` branch). All caller-wiring rows MUST be explicit in sign-off chain; Pax `*validate-story-draft` checklist NEW point #13: "for every spec mechanism block (e.g., Phase G unlock per §15.13.2), there exists a corresponding caller-wiring task row in §15.x sign-off chain with explicit pre-N invocation prereq binding".
- **Sable audit-perimeter binding:** Sable R5-equivalent pre-run coherence audits MUST traverse caller-wiring task rows as standalone pre-run prereqs (NOT collapse them into adjacent envelope conditions). Sable corrective action per ESC-013 ratified by IMPL-2026-05-01.
- **Aria thin-cross-check binding:** Aria F2-T0b'-style architectural review MUST explicitly cosign caller-wiring row completeness BEFORE Beckett baseline-run authorization. The thin-cross-check format remains unchanged (~50-100 LoC standalone or absorbed into existing F2-T8-T0b ledger entry per spec §15.13.12).
- **Architectural surface impact:** ~30-50 LoC AIOX template extension + ~30 LoC Pax checklist amendment + ~30 LoC Sable audit method amendment + ~20 LoC Aria cosign protocol amendment. ZERO code-side mutation.

**Why this is minimal-surface:** the caller-wiring task pattern ALREADY EXISTS as the F2-T8-T1 task in T002. The amendment formalizes the row class + binds Pax/Sable/Aria enforcement hooks. No new authoring discipline beyond what F2-T0b' already established.

### §1.4 Amendment QSDCv2-A4 — closure-body Phase Literal completeness assertion (regression guard against N8.1-class argparse-choice gaps)

**Procedural gap surfaced:** N8 launched with `scripts/run_cpcv_dry_run.py` argparse `choices=["E", "F"]` — Phase G was NOT in the Literal type (despite spec §15.13.2 PRE-AUTHORING the Phase G unlock mechanism). The closure-body / Literal types in the script were INCOMPLETE relative to the spec. The CLI argparse + the inner `phase: Literal["E", "F"]` type annotation (or equivalent) silently allowed F-protocol execution against G-context window.

**Architectural amendment (Q-SDC v2):**

- **NEW invariant:** any script / closure / function whose `phase` parameter is typed as `Literal["E", "F", ...]` MUST include all phases the spec authorizes. Where spec §15.x mechanism block authorizes Phase G unlock, the closure-body Literal MUST include "G". This is an assertable architectural invariant.
- **Contract enforcement mechanism:** a NEW unit-test `test_phase_literal_completeness.py` (per-T002-class strategy, parameterized) asserts that for every Phase Literal in `scripts/run_cpcv_dry_run.py` (or any future H_next-class script), the Literal contains every phase the spec authorizes (introspection: list spec mechanism blocks; for each block with a phase tag, assert phase is in the Literal). The test FAILS if a spec mechanism block is authored for a phase not in the closure Literal.
- **Sign-off chain binding:** caller-wiring task rows (per QSDCv2-A3) MUST explicitly enumerate which phase Literals the row touches; Aria thin-cross-check verifies Literal completeness post-implementation.
- **Architectural surface impact:** ~50-80 LoC test module + ~30 LoC test fixture / spec-introspection helper + ~20 LoC AIOX template extension. ZERO factory contract impact.

**Why this is minimal-surface:** the Literal completeness check is a single test pattern. The amendment formalizes the test as a regression guard required for all H_next-class scripts.

### §1.5 Round-1 IC pipeline orphan code (Sable F-02 procedural finding) closure mechanism

**Procedural gap surfaced:** Sable F-02 — Round-1 IC pipeline contained orphan code (functions / branches authored in Round 1 but never consumed by the canonical Round 3 path). The orphan code was not surfaced until post-implementation deep audit.

**Architectural amendment (Q-SDC v2):**

- **NEW Pax `*validate-story-draft` checklist point #14:** "spec authoring rounds (Round 1 / Round 2 / ...) MUST trace every Round-N additive code surface to either (a) Round-(N+1) consumption, OR (b) explicit deprecation entry in Round-(N+1) §-anchor". Orphan code is grounds for Round-(N+1) NO-GO until traced.
- **Coverage tooling:** existing pytest-coverage tooling (`pytest --cov=packages.vespera_metrics`) is promoted to MANDATORY pre-Beckett-baseline-run gate. Coverage threshold ≥ 95% on the `packages/vespera_metrics/` surface (T002 codebase). Lower threshold raises Pax NO-GO. Quinn QA-gate gains NEW point #8: "vespera_metrics surface coverage ≥ 95%; orphan code surfaced + traced or deleted".
- **Architectural surface impact:** ~30 LoC Pax checklist amendment + ~30 LoC Quinn QA-gate amendment + ~5 LoC pyproject.toml coverage threshold update. ZERO factory contract impact.

**Why this is minimal-surface:** pytest-coverage already runs. The amendment promotes it from advisory to gate-binding + adds Pax round-traceability discipline.

---

## §2 Reusable F2 + Phase G artifacts catalog for H_next

The following artifacts are ratified PRESERVED as canonical for H_next (extending ESC-012 §3.1 + ESC-013 §3.1 inventory). Aria architectural cosign that these surfaces are window-agnostic by design and consume any H_next predictor↔label spec without refactor.

### §2.1 Code-side reusable artifacts

| Artifact | Path | Pattern preserved | Architectural rationale |
|---|---|---|---|
| `cpcv_aggregator.compute_ic_from_cpcv_results` `holdout_locked` flag pattern | `packages/vespera_metrics/cpcv_aggregator.py:251-309` | Window-agnostic kwarg flip — any H_next CPCV pipeline reuses verbatim by passing `holdout_locked=phase != 'G'` (or analog) at the caller site | F2-T0b' Option D placement design — orchestration helper separated from harness factory; single boolean flip suffices for IS/OOS semantics switch |
| `info_coef.ic_spearman` + `bootstrap_ci` pattern | `packages/vespera_metrics/info_coef.py` | Bootstrap CI on Spearman rank-correlation with seed=42 + n_resample=10000; window-agnostic | Bailey-Lopez de Prado §3 multiplicity adjustment substrate; reusable for any rank-correlation H_next |
| `make_backtest_fn` factory pattern (T002.1.bis) | `scripts/run_cpcv_dry_run.py` (factory) + `cpcv_harness.py` (consumer) | R/O captures `enclosed_costs / enclosed_calendar / enclosed_percentiles`; per-fold P126 D-1 invariant; mutually-exclusive engine guard | T002.1.bis APPROVE_OPTION_B precedent; closure-isolation philosophy preserved across H_next |
| `BacktestResult.content_sha256` byte-stability | `packages/vespera_engine/backtest_result.py` | Tri-sig content_sha256 invariant per ADR-5 | ADR-5 canonical invariant hardening |
| `DeterminismStamp` 9-field receipt | (per Beckett T0 schema) | 9-field stamp: engine_config_sha256, spec_sha256, cost_atlas_sha256, rollover_calendar_sha256, cpcv_config_sha256, python/numpy/pandas versions, seed, dataset_sha256 | Reproducibility receipt canonical |
| `_holdout_lock.assert_holdout_safe` + `VESPERA_UNLOCK_HOLDOUT=1` env affordance | `scripts/_holdout_lock.py:103-137` | Two-layer hold-out lock contract (data-engineering layer + statistical layer) | Anti-Article-IV Guard #3 substrate |

### §2.2 Spec-side reusable artifacts

| Artifact | Path | Pattern preserved | H_next reuse mode |
|---|---|---|---|
| Mira spec §15 template (IC wiring + decay sub-clause + status flag propagation) | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` §15 | Sign-off chain table (T0a-T0e + T1-T7) + mechanism blocks (§15.13.2-style) + status flag propagation contract | Promote to canonical AIOX template per QSDCv2-A1 above; H_next Mira spec authors adapts §15 structure verbatim |
| Riven 3-bucket post-mortem framework (synthetic_vs_real_tape / costed_out_edge / IC_pnl_misalignment / +v4 NEW buckets gap_variance_unbounded / book_snapshot_dependency / regime_filter_overfit) | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` | 3-bucket reclassification authority per Mira spec §12.1 sign-off chain row F2-T8-T6 | Riven 3-bucket post-mortem v4 canonical for H_next; new bucket additions per Riven authority |
| Beckett `latency_dma2_profile` spec | `docs/backtest/latency-dma2-profile-spec.md` | DMA2 latency p50=20ms / p95=60ms / p99=100ms; tail 500ms stress | Engine-config v1.1.0 frozen; reused verbatim under H_next |
| Nova RLP+rollover spec | (per Beckett N6 baseline + Nova authority) | RLP detection (tradeType=13 conservative-ignore policy); rollover calendar c6174922; microstructure flags (circuit_breaker_fired, cross_trade) | Reused verbatim |
| Beckett N6 latency_dma2 spec | `docs/backtest/T002-beckett-n6-2026-04-29.md` | Latency design residing canonical | Reused verbatim |

### §2.3 Reusability discipline (binding for H_next)

- **No mutation:** H_next cannot mutate any artifact in §2.1-§2.2 without convening an architectural sub-council with Aria + Beckett + Mira + Riven cosign. Engine-config v1.1.0 FROZEN per Path A OFF (ESC-012 R6 carry-forward) + cost atlas v1.0.0 FROZEN.
- **Bonferroni bookkeeping:** n_trials=5 carry-forward IF H_next consumes same in-sample window; resets to 1 if H_next uses fresh IS window per Riven §11.5 + Mira spec §15.13.3 invariant.
- **Hold-out window forward virgin:** old hold-out [2025-07-01, 2026-04-21] CONSUMED + FORFEITED per Round 3.1 + ESC-013 R9 single-shot binding. H_next requires NEW pre-registered forward virgin window per Riven QUANT-2026-05-01 §3 (forward 2026-05+ ≥ 6 months calendar-locked).

---

## §3 NEW regression-guard tests for Q-SDC v2

Three NEW contract tests Aria mandates as MANDATORY pre-Beckett-baseline-run gates for every H_next-class spec implementation. These EXTEND existing test surface (`tests/cpcv_harness/`, `tests/vespera_metrics/`) without breaking changes.

### §3.1 Test T-RG1 — verdict-vs-reason consistency contract (extend `test_k3_pass_reason_text_no_sentinel`)

**Scope:** extend existing `tests/vespera_metrics/test_k3_pass_reason_text_no_sentinel.py` from T002-specific to H_next-class general. Parameterize across all kill-criteria evaluator functions exposed in `packages/vespera_metrics/`. For each (verdict_label, reason_text) pair authored in spec yaml, assert:

(a) `verdict_label` ∈ {allowed verdict labels per spec}
(b) `reason_text` matches a spec-authored regex pattern from the verdict-vs-reason allowed-pairs table (per QSDCv2-A2)
(c) The (verdict, reason) pair is allowed per the table (cross-product validity)
(d) `validate_verdict_vs_reason()` helper raises `InvalidVerdictReport` for any inconsistent pair

**LoC estimate:** ~50-80 LoC parameterize + ~30 LoC fixture for spec-introspection. ZERO factory contract impact.

**Failure mode targeted:** F2-T5-OBS-1-class verdict-text mismatch where the verdict says PASS but reason carries DEFERRED-sentinel language (or analogous mismatch in any future kill-criteria class).

### §3.2 Test T-RG2 — Phase Literal completeness check (NEW)

**Scope:** parameterize across all `scripts/*.py` and closure-body functions. For each Phase Literal type annotation (e.g., `phase: Literal["E", "F", "G"]`), introspect spec yaml `kill_criteria` + spec markdown `§15.x` mechanism blocks for phase-tagged authorizations; assert every spec-authored phase is present in the Literal AND every Literal phase has at least one spec mechanism block.

**LoC estimate:** ~50-80 LoC test module + ~30-50 LoC introspection helper. ZERO factory contract impact.

**Failure mode targeted:** N8.1-class argparse-choice gap — Phase G PRE-AUTHORED in spec §15.13 but NOT in closure Literal nor in argparse `choices`.

### §3.3 Test T-RG3 — cross-protocol propagation (status flag persistence)

**Scope:** end-to-end smoke test asserting status flag propagation from caller → orchestration helper → aggregator → metrics → verdict. For T002-class: assert `phase='G'` + `holdout_unlocked=True` (events_metadata) + `holdout_locked=False` (compute_ic_from_cpcv_results kwarg) + `ic_holdout_status='computed'` (MetricsResult) + verdict label NOT containing DEFERRED-sentinel. For H_next-class: parameterize per spec.

**LoC estimate:** ~80-120 LoC end-to-end test + ~30 LoC fixture. ZERO factory contract impact.

**Failure mode targeted:** F2-T9-OBS-1-class implicit-but-unbuilt — caller-wiring task incomplete, status flag not propagating end-to-end despite spec authorization.

### §3.4 Test surface aggregate

**Total NEW test LoC: ~250-400 LoC across 3 modules.** All tests are pure-function-style (introspection over spec + smoke-test over public-API surfaces); ZERO factory contract impact; ZERO closure-body mutation; ZERO engine signature change. Quinn QA-gate gains 3 NEW points (T-RG1 / T-RG2 / T-RG3 PASS) as MANDATORY pre-Beckett-baseline-run gates.

---

## §4 Engine-config v1.2.0 perf optimization carry-forward (~3h baseline → 60-90 min target)

### §4.1 Architectural decision

**RECOMMEND CARRY-FORWARD as parallel architectural track. NON-BLOCKING for H_next first run; OPTIONAL for first H_next CPCV trial; MANDATORY before H_next reaches Bonferroni n_trials=3+.**

### §4.2 Rationale

- **Beckett N7-prime §10.3 flagged opportunity:** "future Beckett engine-config v1.2.0 perf optimization (parquet pre-aggregation OR session caching across folds) to bring full-run under 60 min. Tracked for council attention; non-blocking for F2-T5 statistical verdict interpretability — wall-time is operational, not statistical."
- **Beckett QUANT-2026-05-01 ballot §1.1:** wall-time budget is a binding executability axis; 188 min N7-prime / 141 min N8.2 baseline establishes ~3h per re-run; H_next budget ~5h per re-run = ≤ 8 incremental trials before Bonferroni hits DSR strict bar. Engine-config v1.2.0 perf round COULD bring per-trial cost from ~38 min to ~12-18 min (3-4× speedup), enabling more CPCV trials per H_next budget envelope.
- **Architectural shape:** parquet pre-aggregation (pre-compute per-session aggregates BEFORE CPCV fan-out) + session caching across folds (memoize per-session features across overlapping fold train/test sets). Both are PURE optimizations — NO statistical impact; NO factory contract mutation; NO spec yaml mutation; NO Bonferroni accounting impact.

### §4.3 Architectural risk surface

- **HIGH-priority risk:** byte-stability invariant per ADR-5 (`BacktestResult.content_sha256`) MUST be preserved across the optimization. The optimization changes WHEN aggregation happens, not WHAT is aggregated. Aria thin-cross-check binds: pre-optimization N7-prime/N8.2 `BacktestResult.content_sha256` MUST equal post-optimization N7-prime'/N8.2' `BacktestResult.content_sha256` for IDENTICAL (engine_config_sha256, spec_sha256, cost_atlas_sha256, rollover_calendar_sha256, dataset_sha256, seed=42).
- **MEDIUM-priority risk:** RSS budget per ADR-1 v3 (6 GiB cap). Pre-aggregation may inflate peak RSS. Aria thin-cross-check binds: post-optimization peak RSS ≤ 0.5 × ADR-1 cap (3 GiB) to preserve 2× headroom for any future H_next features (e.g., book-snapshot replay per Riven QUANT-2026-05-01 §1 (E)).
- **LOW-priority risk:** caching consistency across CPCV folds. Aria recommends an explicit cache-invalidation protocol tied to `engine_config_sha256` + `cost_atlas_sha256` + `rollover_calendar_sha256` (cache key = tuple of 3 SHAs); cache MUST invalidate on any SHA change.

### §4.4 Architectural amendment (Q-SDC v2 optional track)

- **NEW track QSDCv2-T1 (parallel optional):** `engine-config v1.2.0 perf optimization` story; Aria authors architectural design (~150-200 LoC ADR document); Dex implements (~200-400 LoC); Quinn validates byte-stability invariant via NEW test `test_engine_config_v120_byte_stability.py` asserting `BacktestResult.content_sha256` INVARIANT across v1.1.0 → v1.2.0 transition.
- **Sequencing:** track QSDCv2-T1 runs IN PARALLEL with H_next first CPCV trial (which may use engine-config v1.1.0 at full ~3h cost). After QSDCv2-T1 lands + byte-stability gate PASSES, H_next subsequent trials transition to v1.2.0. Bonferroni n_trials accounting unaffected (engine-config switch is operational, NOT statistical mutation).
- **MANDATORY trigger:** if H_next reaches Bonferroni n_trials=3 still on v1.1.0 (Riven §11.5 #8 capture-rate evaluation requires multiple trials at reasonable wall-budget), QSDCv2-T1 becomes blocking before n_trials=4.

### §4.5 Verdict on §4

**APPROVE_PARALLEL_TRACK.** Engine-config v1.2.0 perf optimization is architecturally clean (byte-stability + RSS + cache-invalidation guards) and operationally beneficial (3-4× wall speedup) WITHOUT statistical impact. Should be carried forward but is NOT a blocker for H_next first trial. This preserves Aria philosophy "minimum-disruption + maximum-information per-effort" — H_next can proceed without waiting for v1.2.0; v1.2.0 lands when the engineering bandwidth opens.

---

## §5 Personal preference disclosure

**Aria personal preference (transparent for council):** APPROVE all FOUR Q-SDC v2 amendments QSDCv2-A1..A4 + APPROVE_PRESERVED reusability inventory §2 + APPROVE all THREE NEW regression-guard tests T-RG1..T-RG3 + APPROVE_PARALLEL_TRACK engine-config v1.2.0 (QSDCv2-T1).

**Rationale:** Aria architectural philosophy = minimum-disruption + maximum-information per-effort. Each Q-SDC v2 amendment is a minimal-surface protocol-cleanup that closes a procedural gap surfaced over T002 lifecycle, WITHOUT mutating Constitution Articles I-IV, agent authority matrix, or factory pattern. The amendments are CUMULATIVELY ~300-500 LoC across templates + checklists + audit methods + 3 new tests — a small price for closing F-01..F-04 + F2-T9-OBS-1 + F2-T5-OBS-1 procedural surface forever.

**Bias disclosures (carry-forward + new):**

- **ESC-012/ESC-013 carry-forward bias:** Aria voted APPROVE_PATH_B + APPROVE_PATH_iv with C-G1..C-G6 + C-iv1..C-iv6 conditions binding. The Q-SDC v2 amendments here ARE the procedural-cleanup closures of those conditions. Self-consistency preserved; same bias as prior votes (architectural-minimum-disruption preference).
- **F2-T0b' authorship bias:** Aria authored the Option D placement design for `compute_ic_from_cpcv_results` (window-agnostic). The reusability inventory §2.1 includes that artifact verbatim. Aria flags this as a potential bias toward over-praising own design; counter-check: the F2-T0b' design DID hold up across N7-prime / N8 / N8.2 with ZERO refactor — the Mira Round 3.1 verdict + Beckett N8.2 reproducibility receipt 8/9 IDENTICAL fields validate the design empirically. Bias-trip not triggered.
- **AIOX template promotion bias:** Aria recommends promoting the §15.x sign-off chain pattern to canonical AIOX template (QSDCv2-A1). Aria flags potential bias toward formalizing Aria-cosigned patterns; counter-check: the §15.x pattern was authored by Mira (NOT by Aria); promotion benefits Pax / Sable / Quinn / Mira / Riven authoring discipline equally, not Aria specifically. Bias-trip not triggered.

**Counter-bias check passed.** Q-SDC v2 amendment preferences hold independent of Aria authorship history.

**Acknowledgement of council authority:** Aria votes the §1-§4 architectural amendments but defers to:
- Pax @po Q-SDC orchestration authority (story-creation flow + checklist amendments + epic-context binding format);
- Mira @ml-researcher spec-authoring authority (§15.x template promotion + verdict-vs-reason allowed-pairs table format + caller-wiring row format details);
- Sable @squad-auditor audit-perimeter authority (R5-equivalent audit method amendments + §15.x traversal binding);
- Riven @risk-manager 3-bucket post-mortem v4 authority + §11.5 #8/#9/#10 NEW pre-conditions;
- Beckett @backtester engine-config v1.2.0 perf authoring authority (Aria architectural design + Beckett implementation review);
- Quinn @qa QA-gate authority (NEW points #8 + T-RG1/T-RG2/T-RG3 binding format);
- Dex @dev impl-side authority (engineering details of caller-wiring rows + verdict_contract.py module + perf-optimization implementation);
- Gage @devops Article II push-exclusivity (no commit / push by this vote per task discipline).

If Pax determines that Q-SDC v2 amendment QSDCv2-A1..A4 priorities differ (e.g., A1 lands first while A2-A4 stage later), Aria cosigns the staging — these are minimal-surface independent amendments and can land in any order without architectural coupling.

---

## §6 Article IV self-audit

| Claim in this vote | Source anchor (verified in this session) |
|---|---|
| Sable F-01..F-04 procedural findings + R5 audit scope gap admission | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-sable-vote.md` §2 verbatim |
| F2-T9-OBS-1 = F2-T8-T1 caller wiring implicit-but-unbuilt | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-sable-vote.md` §2 + Aria own ESC-013 ballot §1.1 |
| F2-T5-OBS-1 = verdict-vs-reason mismatch enforcement gap; Dex `fadacf4` short-circuit | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-aria-vote.md` §7.1 C-iv4 |
| Mira spec v1.2.0 §15 (sign-off chain + mechanism blocks + status flag) canonical pattern | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` §15 verbatim |
| `compute_ic_from_cpcv_results(holdout_locked: bool = True)` window-agnostic kwarg pattern (F2-T0b' Option D) | `packages/vespera_metrics/cpcv_aggregator.py:251-309` + `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` §5.1 |
| `BacktestResult.content_sha256` byte-stability invariant per ADR-5 | `docs/architecture/ADR-5-canonical-invariant-hardening.md` |
| Riven 3-bucket post-mortem framework canonical | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 + §5 anti-pattern catalog |
| Engine-config v1.2.0 perf optimization opportunity (188 min N7-prime / 141 min N8.2; target 60-90 min via parquet pre-aggregation + session caching) | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §10.3 + `docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-beckett-vote.md` §1.1 |
| Bonferroni n_trials=5 carry-forward + reset on fresh IS window | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-aria-vote.md` §4.1 + Mira spec §15.13.3 |
| Two-layer hold-out lock contract (data-engineering + statistical) per Anti-Article-IV Guard #3 | `docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-aria-vote.md` §5.1 |
| Riven §11.5 #8/#9/#10 NEW pre-conditions + 3-bucket post-mortem v4 NEW buckets | `docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-riven-vote.md` §2 + §4 |

**Article IV self-audit verdict:** every architectural claim in this vote traces to (a) ESC-013 ballot anchor (Aria own + Sable), (b) Mira spec v1.2.0 §15 anchor, (c) direct repo file inspection (`packages/vespera_metrics/cpcv_aggregator.py:251-309`, `scripts/_holdout_lock.py:103-137`, `docs/architecture/ADR-5-canonical-invariant-hardening.md`), (d) Beckett N7-prime §10.3 + Beckett QUANT-2026-05-01 §1.1, OR (e) Riven QUANT-2026-05-01 §2 + §4. **NO INVENTION. NO Constitution mutation. NO agent authority matrix mutation. NO spec yaml mutation. NO factory contract refactor. NO closure isolation break. NO new env-var. NO new bypass mechanism. NO H_next strategy preference (Mira authority preserved). NO §11.5 mutation (Riven authority preserved). NO Q-SDC orchestration mutation (Pax authority preserved).**

The vote does NOT pre-empt:
- Pax @po Q-SDC orchestration authority (checklist amendments format; epic context binding format).
- Mira @ml-researcher spec authoring authority (§15.x template promotion details + verdict-vs-reason table format + caller-wiring row format).
- Sable @squad-auditor audit-perimeter authority (R5-equivalent traversal mechanism details).
- Riven @risk-manager 3-bucket post-mortem v4 authoring + §11.5 pre-conditions authoring.
- Beckett @backtester engine-config v1.2.0 implementation authority (perf optimization choice — parquet pre-aggregation OR session caching OR both).
- Quinn @qa QA-gate authority (NEW point format details).
- Dex @dev impl-side authority (caller-wiring rows + verdict_contract.py module + perf-optimization implementation details).
- Gage @devops Article II push-exclusivity (no commit / push by this vote per task discipline).

---

## §7 Aria cosign 2026-05-01 BRT — IMPL-2026-05-01 squad instrumentation ballot

```
Authority: Aria (@architect) — system architecture + factory pattern + closure isolation + spec yaml threshold guardianship
Council: IMPL-2026-05-01 — squad instrumentation post T002 RETIRE FINAL (ESC-011/012/013 closure +
         Sable F-01..F-04 + F2-T9-OBS-1) for next Q-SDC cycle on H_next
Mode: autonomous; voter did NOT consult other IMPL-2026-05-01 agent ballots pre-cast (task discipline)

Architectural verdict (4 amendments + 3 tests + 1 parallel track):
  QSDCv2-A1 (APPROVE) — §15.x sign-off chain canonical AIOX template promotion
                        (Sable F-01 closure pattern); ~50-100 LoC template + ~80 LoC enforcement hooks
  QSDCv2-A2 (APPROVE) — Anti-Article-IV Guard #9 NEW (verdict-vs-reason cross-protocol invariant);
                        F2-T5-OBS-1 enforcement gap closure; ~100-150 LoC verdict_contract.py module
                        + ~80 LoC test + ~80 LoC discipline amendments
  QSDCv2-A3 (APPROVE) — caller-wiring task explicit row in sign-off chain (F2-T9-OBS-1 closure);
                        ~110 LoC AIOX/Pax/Sable/Aria amendments
  QSDCv2-A4 (APPROVE) — closure-body Phase Literal completeness assertion regression guard;
                        ~80-130 LoC test + introspection helper
  Sable F-02 closure — Round-1 IC pipeline orphan code via Pax checklist #14 +
                       Quinn QA-gate #8 (vespera_metrics ≥ 95% coverage); ~65 LoC amendments

Reusable F2 + Phase G artifacts ratified PRESERVED for H_next (§2 verbatim):
  Code: cpcv_aggregator.holdout_locked flag + info_coef.bootstrap_ci + make_backtest_fn factory +
        BacktestResult.content_sha256 + DeterminismStamp 9-field + _holdout_lock.assert_holdout_safe
  Spec: Mira §15 template (PROMOTE) + Riven 3-bucket v4 framework + Beckett latency_dma2 +
        Nova RLP+rollover + Beckett N6 latency design

NEW regression-guard tests (3 contract tests; ~250-400 LoC total):
  T-RG1 — verdict-vs-reason consistency contract (extends test_k3_pass_reason_text_no_sentinel)
  T-RG2 — Phase Literal completeness check (NEW)
  T-RG3 — cross-protocol propagation (status flag persistence end-to-end)

Engine-config v1.2.0 perf optimization (QSDCv2-T1 parallel track):
  APPROVE_PARALLEL_TRACK — non-blocking for H_next first trial; OPTIONAL through n_trials=2;
  MANDATORY before n_trials=3+; target 188 min → 60-90 min via parquet pre-aggregation +
  session caching; ARCHITECTURAL GUARDS: byte-stability (BacktestResult.content_sha256 INVARIANT
  v1.1.0 → v1.2.0); RSS ≤ 3 GiB (preserve 2× headroom); cache-key = (engine_config_sha256,
  cost_atlas_sha256, rollover_calendar_sha256) tuple; INVALIDATE on any SHA change.

Personal preference: APPROVE all 4 amendments + 3 tests + parallel track; bias toward
  minimum-disruption + maximum-information per-effort preserved from ESC-012/ESC-013;
  self-consistency bias disclosed (Q-SDC v2 amendments close the same procedural gaps Aria
  cosigned conditions for in ESC-013); F2-T0b' authorship bias counter-checked (design held up
  empirically across N7-prime/N8/N8.2 with ZERO refactor); AIOX template promotion bias
  counter-checked (§15.x pattern Mira-authored, promotion benefits all squad authoring agents).

Article II (Gage push exclusivity): preserved — vote document is write-only, no commit/push initiated
Article IV (No Invention): preserved — every clause traces in §6 to ESC-013 ballot anchor, Mira spec
  §15 anchor, repo file inspection, Beckett §10.3 anchor, Riven QUANT-2026-05-01 anchor, OR own prior
  ballot anchor; no Constitution mutation; no agent authority matrix mutation; no spec yaml mutation;
  no factory contract refactor; no closure isolation break; no H_next strategy preference smuggling;
  no Q-SDC orchestration override
Anti-Article-IV Guards (preserved + extended):
  #1 (Dex impl gated em Mira spec PASS) — preserved through QSDCv2-A1 (§15.x table mandatory)
  #3 (NO touch hold-out lock contract) — preserved through reusability §2 (two-layer contract canonical)
  #4 (Gate thresholds UNMOVABLE) — preserved (no spec yaml mutation; H_next gets fresh kill-criteria
      table per Mira authority; thresholds for T002 v0.2.3 frozen as forensic record)
  #5 (NO subsample backtest run) — preserved (engine-config v1.2.0 perf optimization is operational,
      NOT statistical; no sub-sample averaging introduced)
  #6 (NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH) — preserved (T002 Gate 5 LOCKED
      PERMANENTLY; H_next gets fresh dependency tree per Riven QUANT-2026-05-01 §5)
  #7 (NO push) — preserved (Aria authoring; no git operations)
  #8 (Verdict-layer *_status provenance + InvalidVerdictReport) — REINFORCED through QSDCv2-A2
      (Anti-Article-IV Guard #9 NEW + verdict_contract.py canonical module)
  #9 (NEW — verdict-vs-reason cross-protocol invariant) — INTRODUCED by QSDCv2-A2 if council ratifies
Boundary respected:
  NÃO override Mira ML semantics (H_next strategy ranking + spec template format details = Mira)
  NÃO override Riven §11.5 + 3-bucket post-mortem v4 (= Riven authority)
  NÃO pre-empt Sable audit-perimeter (= Sable authority — corrective action ratified by IMPL-2026-05-01)
  NÃO pre-empt Pax Q-SDC orchestration (= Pax authority — checklist amendments format details)
  NÃO pre-empt Beckett engine-config v1.2.0 implementation (= Beckett authority — perf choice details)
  NÃO pre-empt Quinn QA-gate (= Quinn authority — point format details)
  NÃO pre-empt Dex impl-side (= Dex authority — caller-wiring + module impl details)
  NÃO commit / NÃO push (Gage @devops authority preserved for any future commit)
  NÃO read other IMPL-2026-05-01 agent votes pre-cast (task discipline; independent ballot)

Cosign: Aria @architect 2026-05-01 BRT — IMPL-2026-05-01 squad instrumentation for Q-SDC v2 ballot
        Vote: APPROVE QSDCv2-A1..A4 + reusable §2 + T-RG1..T-RG3 + QSDCv2-T1 parallel track
        Relationship: PROCEDURAL-CLEANUP_OF_ESC-012 + ESC-013 conditions (C-G1..C-G6 + C-iv1..C-iv6)
                      INSTRUMENTATION FOR H_next — instrumenting the squad against F-01..F-04 +
                      F2-T9-OBS-1 + F2-T5-OBS-1 procedural surface forever
```

— Aria, escolhendo a postura arquitetural canônica: gaps procedurais fecham via amendments mínimos de protocolo, não via reescrita de framework. O squad chega ao Q-SDC v2 com a mesma constituição, com hooks de enforcement mais rigorosos, e com uma reusability surface preservada.
