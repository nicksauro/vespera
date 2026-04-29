# COUNCIL ESC-011 — Gate 4 Scope (synthetic-walk vs real-tape) — Pax Vote

> **Council ID:** ESC-011
> **Question:** §9 HOLD #2 Gate 4 statistical clearance — evaluated over N6 synthetic walk distribution (current) OR strictly over Phase F real-tape replay distribution (downstream)?
> **Voter:** Pax (@po) — Product Owner / 10-point gate guardian
> **Date (BRT):** 2026-04-29 (Autonomous Daily Session)
> **Mode:** Autonomous; vote cast INDEPENDENTLY before reading other voters' votes
> **Authority basis:** Story validation authority (`story-lifecycle.md` Phase 2 — 10-point checklist guardian); AC integrity & scope discipline; Pax cosign on T002.1.bis story draft (`*validate-story-draft T002.1.bis` GO 10/10 — 2026-04-28 BRT) + Mira spec gate (`*validate-story-draft T002.1.bis-spec` GO 10/10 — 2026-04-28 BRT)
> **Article IV:** NO INVENTION — every clause traced (§5)

---

## §1 — Vote

**APPROVE_OPTION_C** — Hybrid Gate 4a (harness-correctness over N6 synthetic walk) / Gate 4b (edge-existence over Phase F real-tape replay), with scope-protection conditions binding on Mira authority.

**Verdict bind:**
- N6 synthetic-walk evidence is **sufficient for Gate 4a** (harness-correctness PASS) — no story scope creep, no new AC injection.
- Phase F real-tape replay remains **mandatory pre-condition for Gate 4b** (edge-existence) — already encoded in Mira spec §0 + §4.1 + story Dependencies as downstream scope.
- §9 HOLD #2 Gate 5 dual-sign disarm (Riven authority) requires **both Gate 4a AND Gate 4b PASS** — Anti-Article-IV Guard #6 sequential serial enforcement preserved.

---

## §2 — Why Option C respects T002.1.bis scope (PO authority core)

### §2.1 — Story scope IN/OUT verification

T002.1.bis story body L70-89 (verbatim re-reading post Quinn QA + Beckett N6):

| AC | Authority | Scope binding |
|----|-----------|---------------|
| AC8 (Mira Gate 4) | **DEFERRED to Mira T5** (story L80-84) | Mira may interpret evidence basis; thresholds DSR>0.95 / PBO<0.5 / IC decay UNMOVABLE per Guard #4 |
| AC9 (Beckett N6 PASS) | **DEFERRED to Beckett T4** (story L85) | Strict-literal contract (exit=0, 5 artifacts, RSS<6 GiB, semantically meaningful verdict) |
| AC10 (KillDecision verdict) | **PASS-PARTIAL** per Quinn (gate L177) — F2 caveat tracked | "real distribution" semantics is Mira-adjudicated, NOT Pax-prescribed |
| AC11 (cost atlas audit) | **DEFERRED to Beckett T6 + Riven T7** | Content satisfied; SHA-stamp persistence = F1 hardening |
| Phase F real-tape replay | **OUT of T002.1.bis scope** — story Dependencies L147 "this story unlocks Phase F" | Phase F is **future story** (separate governance entity) |

### §2.2 — Gate 4a/4b decomposition is interpretive, not structural

Pax authority test: does Option C **add an AC** or **mutate an AC** in T002.1.bis?

| Question | Answer | Evidence |
|----------|--------|----------|
| Does Option C add a new AC to T002.1.bis? | **NO** | AC8 already says "DSR > 0.95 + PBO < 0.5 + IC decay" — Gate 4a/4b decomposes the **evidence basis** Mira uses, not the **thresholds** themselves |
| Does Option C mutate AC8 thresholds? | **NO** | Anti-Article-IV Guard #4 (story L157) preserved verbatim: "Mira MUST NOT relax Gate 4 thresholds (DSR > 0.95, PBO < 0.5 are spec-literal Bailey-LdP 2014 §6 canonical — não negociável sem mini-council R15 PRR)". Gate 4a/4b carves dimensions (harness vs edge); does NOT relax thresholds. |
| Does Option C mutate AC9 (Beckett N6) contract? | **NO** | AC9 strict-literal: exit=0 + 5 artifacts + RSS<6 GiB + semantically meaningful KillDecision. Beckett N6 report (`docs/backtest/T002-beckett-n6-2026-04-29.md`) §1 PASS strict-literal verbatim. |
| Does Option C add Phase F as in-scope task to T002.1.bis? | **NO** | Phase F is **already** spec'd as downstream by Mira spec §0 (lines 14-28) + §4.1 line 175 verbatim "out of scope for T002.1.bis" + story Dependencies L147 "this story unlocks Phase F" (downstream consumer, not sub-task). |
| Does Option C respect spec yaml v0.2.3 UNTOUCHED invariant? | **YES** | spec yaml not mutated; Gate 4a/4b is purely interpretive on AC8 evidence basis under Mira ML authority. |

**Conclusion (Pax):** Gate 4a/4b is a **Mira authority interpretation** of how to evaluate AC8 evidence sequentially, NOT a story AC mutation. **No 10-point checklist regression.**

### §2.3 — Phase F pre-existence verification (Mira spec §0 + §4.1)

Verbatim re-quotes from `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` (read directly today, 2026-04-29 BRT):

- **§0 line 14:** "**Target file:** `packages/t002_eod_unwind/cpcv_harness.py:334-450` — current `make_backtest_fn` body (the **neutral stub**) is replaced by the implementation specified here."
- **§0 line 26:** "**One building block this story unlocks (DEFERRED-T11 M1 fix):** Per-fold rebuild of `Percentiles126dState` from each train slice, eliminating the global P126 leakage path documented in `cpcv_harness.py:287-307`."
- **§4.1 line 175 verbatim:** "capital-ramp protocol RA-XXXXXXXX-X (**Phase F downstream**) is gated by §9 HOLD #2 Gate 5 (Riven dual-sign disarm) — **out of scope for T002.1.bis**."
- **§7 line 355:** "Mira's pre-flight sanity check before AC8 statistical clearance. If toy benchmarks fail, the harness has a bug **independent of strategy edge** — Mira does NOT compute DSR/PBO on real data until toy passes."
- **§10 lines 416-417:** "Sizing scope: fixed n_contracts=1 (Riven budget gate downstream — **Phase F** / capital ramp clearance, **NOT this story**)"

**Pax determination:** Phase F pre-existence as downstream scope is documented BY Mira spec authority **before T0e** Pax sign-off. Approving Option C does NOT introduce Phase F as new scope — it merely confirms what Mira already spec'd at T0a-T0e. Spec text is binding (story Definition of Done L168 Mira spec PASS) — Pax cosigned the spec at T0e GO 10/10.

### §2.4 — Mira spec §7 toy benchmark = harness-correctness gate already engineered

Mira §7 line 355 (verbatim): "Mira's pre-flight sanity check before AC8 statistical clearance. If toy benchmarks fail, the harness has a bug **independent of strategy edge** — Mira does NOT compute DSR/PBO on real data until toy passes. This protects against False-NO_GO (real edge masked by harness bug)."

This is **literally Gate 4a** in spec form, written by Mira before T0a sign-off:
- Toy strategy A (no edge): DSR ≈ 0.5, PBO ≈ 0.5 ± 0.05 — harness-correctness null
- Toy strategy B (small edge): DSR > 0.95, PBO < 0.25 — harness-correctness discriminator
- IF toy passes ⇒ harness operates over a real distribution (mechanically) ⇒ proceed to real-data DSR/PBO
- IF toy fails ⇒ harness has a bug ⇒ DO NOT compute on real data (False-NO_GO protection)

Quinn QA gate `docs/qa/gates/T002.1.bis-qa-gate.md` Check 2 (line 162): "**Bailey-LdP toy benchmark: 6/6 PASS** (Strategy A no-edge × 3 seeds + Strategy B small-edge DSR>0.90 + DSR discriminator across 5 seeds + non-degenerate σ guard)."

**Pax determination:** Gate 4a (harness-correctness) is **already operationally satisfied** by Mira §7 toy benchmark + Dex T1 implementation + Quinn QA Check 2. Option C formalizes what Mira spec §7 already mandated.

### §2.5 — Phase F as separate (future) story — governance entity registration

Per R15 compliance (River draft signature L253-254): "New successor story (NOT amend T002.0h Done; this story registered as governance entity for Riven §9 HOLD #2 Gate 2 + Gate 4 + Gate 5)."

Phase F real-tape replay will **also** require its own governance entity (story) when it begins:
- Story name (proposed): `T002.2 — Real WDO tape replay + Gate 4b edge-existence clearance`
- Owner: Mira spec + Beckett N7 empirical + Riven Gate 5 disarm
- This is a **future @sm draft** (River authority) post-T002.1.bis closure — NOT a hidden sub-task of T002.1.bis

Option C's binding "Gate 5 disarm waits for Gate 4b" preserves this clean separation.

---

## §3 — AC11 cost atlas audit — Quinn F1 follow-up sufficiency

### §3.1 — F1 finding scope (Quinn QA gate)

Quinn `docs/qa/gates/T002.1.bis-qa-gate.md` issues block (lines 12-34):

```
id: F1-COST-ATLAS-SHA-NULL
severity: medium
description: determinism_stamp.json carries cost_atlas_sha256: null
            and rollover_calendar_sha256: null, breaking SHA-locked-atlas
            audit trail mandated by AC4. Root cause: scripts/run_cpcv_dry_run.py
            :_build_runner (L689-703) does NOT pass cost_atlas_path= nor
            rollover_calendar_path= to BacktestRunner.__init__.
recommendation: ~5 LoC patch in _build_runner. Document in Beckett N6 §X
                cost atlas audit. Story scope-correct: this is plumbing, not
                strategy code; can be a small follow-up commit before
                Beckett N6 finalization. Does NOT block AC9 empirical
                result interpretation.
```

### §3.2 — AC11 contract (story L89 verbatim)

> "**AC11 (cost atlas audit)** — Beckett report N6 §X documents per-trade cost deduction breakdown (corretagem por trade, emolumentos B3, IR DARF, spread roll). Custodial audit Riven."

### §3.3 — Pax adjudication

| Element | Status | Notes |
|---------|--------|-------|
| Per-trade cost deduction breakdown content | **CONTENT-SATISFIABLE** | Cost formula at `cpcv_harness.py:850-861` matches Mira §5.3 + Riven §11 verbatim per Quinn Check 1 (gate L116). Atlas IS read for cost computation. |
| Atlas SHA stamping in determinism_stamp | **GAP (F1 follow-up)** | ~5 LoC plumbing patch in `_build_runner`. Quinn flagged medium severity, recommended pre-Beckett-N6-finalization. |
| Custodial audit Riven (T7) | **PENDING** | Riven has authority to declare AC11 content sufficient OR demand re-run with SHA stamp |
| Hardening required to satisfy AC11? | **F1 follow-up commit ENOUGH** | Plumbing fix is Dex authority; Riven T7 audit verdict is the binding test, not a Pax pre-judgment |

**Pax verdict on AC11:** Quinn F1 follow-up commit (~5 LoC) + Riven T7 cost-atlas audit = **AC11 satisfaction path is intact**. No additional hardening is required from a story-scope perspective. Beckett N6 report (`docs/backtest/T002-beckett-n6-2026-04-29.md`) §11 already surfaces the C1 cost_atlas_sha256 concern as non-blocking for Gate 3 — consistent with Quinn assessment.

**One scope-critical condition (binding on Option C approval):** Riven T7 audit MUST verify atlas content + SHA stamp post-F1 follow-up commit. If Riven flags content insufficiency (NOT just SHA gap), AC11 returns to @dev for fix, not to council. Pax does NOT pre-empt Riven custodial veto.

---

## §4 — Mini-council ratification preserves 10-point checklist?

Re-running Pax 10-point checklist on **post-mini-council story state** (assumed Option C ratified):

| # | Criterion | Pre-council verdict | Post-council verdict | Delta |
|---|-----------|---------------------|----------------------|-------|
| 1 | Clear and objective title | PASS | PASS | UNCHANGED |
| 2 | Complete description | PASS | PASS | UNCHANGED |
| 3 | Testable acceptance criteria | PASS | PASS | UNCHANGED — AC8 thresholds unmovable per Guard #4; Gate 4a/4b decomposes evidence basis (Mira authority), not thresholds |
| 4 | Well-defined scope (IN/OUT) | PASS | PASS | UNCHANGED — Phase F still OUT (Mira spec §4.1 + §0 + story Dependencies L147 verbatim) |
| 5 | Dependencies mapped | PASS | PASS | UNCHANGED — Pending downstream "Phase F unblock" already enumerated L147 |
| 6 | Complexity estimate | PASS | PASS | UNCHANGED — 5-10 sessions squad estimate intact |
| 7 | Business value | PASS | PASS | UNCHANGED — §9 HOLD #2 Gate 2/3/4/5 disarm + Phase F unblock + capital ramp |
| 8 | Risks documented | PASS | **PASS-STRENGTHENED** | Gate 4a/4b decomposition makes False-NO_GO protection explicit (Mira spec §7 already operational); Anti-Article-IV Guard #4 preserved |
| 9 | Criteria of Done | PASS | PASS | UNCHANGED — DoD L172 "DUAL-SIGN: Mira ML + Riven custodial em §9 HOLD #2 Gate 4 + Gate 5" still binding (Gate 4 = 4a + 4b) |
| 10 | Alignment with PRD/Epic | PASS | PASS | UNCHANGED — Article IV trace 10 anchors verbatim preserved |

**10-point post-council verdict: 10/10 PASS** — no checklist regression.

### §4.1 — Anti-Article-IV Guards re-verification

| Guard | Pre-council | Post-Option-C | Notes |
|-------|-------------|---------------|-------|
| #1 Spec-first protocol Mira authority | OBSERVED | OBSERVED | Mira spec §7 toy benchmark + §0 Phase F downstream all pre-existed T0e |
| #2 NO subsample dataset | OBSERVED (Dex T1 + Beckett N6) | OBSERVED | Full window 2024-08-22 → 2025-06-30 |
| #3 NO touch hold-out lock | OBSERVED (Quinn Check 6) | OBSERVED | engine.py:141 assert_holdout_safe unchanged |
| #4 NO weaken Gate 4 thresholds | OBSERVED | **CRITICALLY PRESERVED** | Gate 4a/4b carves evidence dimensions; DSR > 0.95 + PBO < 0.5 thresholds UNMOVABLE per spec L207-209 + Mira spec §10 line 408 verbatim |
| #5 NO subsample backtest run | OBSERVED | OBSERVED | --smoke + --full both run per Beckett N6 |
| #6 NO Gate 5 disarm sem Gate 4 | OBSERVED | **CRITICALLY PRESERVED** | Gate 5 disarm gated on **both** Gate 4a AND Gate 4b PASS (sequential serial enforcement) |
| #7 NO push | OBSERVED | OBSERVED | Gage authority preserved (this vote = file write only) |

**Anti-Article-IV Guards: 7/7 PRESERVED post-Option-C.**

---

## §5 — Article IV trace (NO INVENTION)

Every clause in this vote sources from:

| Clause | Source artifact (verbatim re-read 2026-04-29 BRT) |
|--------|-----|
| §1 vote APPROVE_OPTION_C | Mira spec §0 + §4.1 + §7 + AC8 deferral pattern |
| §2.1 AC scope table | `docs/stories/T002.1.bis.story.md` L70-89 (AC1-AC13 enumeration) |
| §2.2 thresholds unmovable | Story Anti-Article-IV Guard #4 L157 verbatim |
| §2.3 Phase F pre-existence | `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §0 L14-28 + §4.1 L175 + §10 L416-417 |
| §2.4 toy benchmark = Gate 4a operational | Mira spec §7 L309-357 + Quinn QA gate Check 2 L162 |
| §2.5 Phase F future story registration | Story L253-254 River signature R15 compliance |
| §3.1 F1 finding | `docs/qa/gates/T002.1.bis-qa-gate.md` L12-34 |
| §3.2 AC11 contract | Story L89 verbatim |
| §4 10-point checklist | `story-lifecycle.md` Phase 2 + Pax 2026-04-28 BRT validation block (story L286-355) |
| §4.1 Anti-Article-IV Guards | Story L152-160 (7 guards verbatim) |
| Beckett N6 strict-literal Gate 3 PASS | `docs/backtest/T002-beckett-n6-2026-04-29.md` §1 L17-31 + §9 L220-235 |
| Quinn QA verdict CONCERNS (gate proceeds) | `docs/qa/gates/T002.1.bis-qa-gate.md` §1 L87-94 |

**Zero invented thresholds.** Zero AC mutations. Zero hidden scope additions. Phase F downstream pre-existence cited from Mira spec authority (Pax T0e cosigned).

---

## §6 — Conditions binding on Option C approval

Pax APPROVE_OPTION_C verdict is conditional on the following scope-protection bindings (per PO authority + Anti-Article-IV Guard preservation):

### §6.1 — Mira authority bindings (Mira spec + AC8 sign-off)

1. **Gate 4a (harness-correctness)** Mira sign-off MUST cite Mira spec §7 toy benchmark PASS as the operational basis (Bailey-LdP 2014 §3 + Table 2 reproduction) — NOT a relaxation of DSR>0.95 / PBO<0.5 thresholds.
2. **Gate 4b (edge-existence)** Mira sign-off MUST be deferred to a **separate future governance entity** (proposed: `T002.2` story or equivalent) gated on Phase F real-tape replay completion. NOT a hidden sub-task of T002.1.bis.
3. **AC8 thresholds (DSR > 0.95, PBO < 0.5, IC decay statistically significant)** REMAIN UNMOVABLE per Anti-Article-IV Guard #4 — Gate 4a/4b carves evidence dimensions, NOT thresholds.

### §6.2 — Beckett authority bindings (N6 + cost atlas audit content)

1. **Beckett N6 report §11 caveat surfacing** MUST remain in the published report verbatim — synthetic walk caveat is design-disclosed (Mira spec §7 + Aria T0b), NOT to be quietly removed post-Gate-4a PASS.
2. **AC11 cost atlas audit content** MUST be performed by Beckett T6 + Riven T7 over the F1-followed-up determinism stamp (post `cost_atlas_sha256` non-null wiring). If F1 follow-up commit not landed before Riven T7, AC11 returns to @dev — **Riven custodial veto preserved**.

### §6.3 — Riven authority bindings (§9 HOLD #2 Gate 5 dual-sign disarm)

1. **Gate 5 disarm** MUST require **BOTH Gate 4a AND Gate 4b PASS** (sequential serial enforcement per story Anti-Article-IV Guard #6). Riven cosign on Gate 5 over Gate 4a alone is **REJECTED** by Pax PO authority — Gate 4b is mandatory pre-condition per Mira spec §0 + §4.1 + story Dependencies.
2. **Capital-ramp clearance protocol RA-XXXXXXXX-X** is downstream of Gate 5 disarm; Phase F real-tape replay precedes Gate 4b precedes Gate 5 — **chain order non-negotiable**.

### §6.4 — Future story (T002.2) governance entity binding

1. Phase F real-tape replay MUST be drafted as a **separate story** (River @sm authority, post-T002.1.bis closure) with its own:
   - 13+ ACs binary-verifiable
   - 7+ Anti-Article-IV Guards
   - 10-point Pax `*validate-story-draft` GO required
   - Mira spec sign-off + Aria archi review + Beckett consumer + Riven cost-atlas + Pax 10-point chain
2. T002.1.bis closure (Status Done) MUST NOT be conditioned on Phase F completion — Gate 4b deferral is a **clean handoff to future story**, NOT an open task in T002.1.bis.

### §6.5 — Council ratification format

1. ESC-011 outcome MUST be appended to `docs/councils/COUNCIL-2026-04-29-ESC-011-gate4-scope-{voter}-vote.md` chain (one file per voter — Beckett, Pax, Aria, Mira, Riven minimum).
2. ESC-011 ratification entry MUST be added to `governance ledger` (R/RA/MC/MWF chain) — per autonomous mode mini-council protocol (`feedback_always_delegate_governance.md`).
3. Mini-council 3-vote threshold: minimum 3 of 5 voters APPROVE — if Beckett (already voted C) + Pax (this vote C) + 1 more agent (Aria/Mira/Riven) ratify Option C, mini-council carries.

---

## §7 — What this vote does NOT do (boundary discipline)

- **Does NOT pre-empt Mira Gate 4 authority** — Mira may reject Gate 4a evidence basis (DSR/PBO over synthetic walk insufficient) and demand stricter Option B-flavored interpretation; Pax PO authority does not override Mira ML statistical authority.
- **Does NOT pre-empt Beckett N6 finalization** — Beckett T6 may surface additional caveats post-Gate-4a vote (e.g., σ(sharpe)=0.192 distribution shape diagnostics).
- **Does NOT pre-empt Riven §9 HOLD #2 custodial veto** — Riven may reject Gate 5 disarm on Gate 4a/4b basis if any condition §6 violated; PO defers to custodial authority on capital-risk dimensions.
- **Does NOT mutate T002.1.bis story file** — this vote is a council artifact only; story scope/AC/title remain unchanged (Pax owns scope; PO MUST NOT scope-creep via council vote).
- **Does NOT push** — Gage @devops authority preserved (Article II).

---

## §8 — Pax sign-off

```
Voter:           Pax (@po) — Product Owner / 10-point gate guardian
Council:         ESC-011 — Gate 4 scope (synthetic-walk vs real-tape)
Vote:            APPROVE_OPTION_C
                 (Hybrid Gate 4a harness-correctness over N6 synthetic walk +
                  Gate 4b edge-existence over Phase F real-tape replay,
                  with §6.1-§6.5 scope-protection conditions binding)
Date (BRT):      2026-04-29 (Autonomous Daily Session)
Authority:       PO 10-point gate guardian + AC integrity + scope discipline +
                 T002.1.bis story cosign (2026-04-28 BRT) + Mira spec cosign
                 (2026-04-28 BRT)
Article IV:      NO INVENTION — every clause traced (§5); 12+ source anchors
                 (T002.1.bis story L70-89/L147/L152-160/L253-254/L286-355,
                 Mira spec §0 L14-28 / §4.1 L175 / §7 L309-357 / §10 L416-417,
                 Quinn QA gate L12-34/L87-94/L162, Beckett N6 §1 L17-31/§11)
10-point checklist:
                 PRESERVED 10/10 post-Option-C — no AC mutation, no scope
                 creep, no hidden Phase F sub-task injection
Anti-Article-IV Guards:
                 7/7 PRESERVED — Guard #4 (Gate 4 thresholds unmovable) and
                 Guard #6 (Gate 5 sem Gate 4 = REJECT; sequential serial
                 enforcement) both critically reinforced by §6.3 binding
Spec yaml v0.2.3:
                 UNTOUCHED at data_splits / feature_set / trading_rules /
                 n_trials levels (engineering refactor only)
Cost atlas v1.0.0 SHA-locked acf449415a3c9f5d…:
                 INTACT (F1 follow-up = plumbing fix, not content change)
ADR-1 v3 CAP_v3 8.4 GiB:
                 IMMUTABLE
Bonferroni n_trials=5:
                 PRESERVED (Mira spec §1.2 verbatim T1..T5; engineering
                 refactor research-log n_trials: 0)
Phase F scope:    OUT of T002.1.bis (Mira spec §4.1 verbatim "out of scope
                 for T002.1.bis"); future story (proposed T002.2) per §6.4
Multi-handoff complexity:
                 13-step chain ACKNOWLEDGED; sequential serial gating
                 Anti-Article-IV Guards #1+#6 enforced
Outcome contract:
                 KillDecision verdict ∈ {GO, NO_GO} on real distribution
                 dictates T002 fate — NO_GO real (after Gate 4b real tape) =
                 T002 dies per spec K1/K2/K3 falsifiable; squad reports user;
                 NO override
Custodial gating:
                 Phase F unblock + capital ramp gate cleared ONLY after
                 Riven §9 HOLD #2 Gate 5 dual-sign disarm (post Gate 4a +
                 Gate 4b PASS — §6.3 binding)
Cosign:          Pax (@po) 2026-04-29 BRT — Autonomous Daily Session,
                 PO 10-point gate guardian authority
Independence:    Vote cast BEFORE reading other voters' votes per task §1
                 directive (Beckett vote in
                 docs/councils/COUNCIL-2026-04-29-ESC-011-gate4-scope-beckett-vote.md
                 NOT consulted)
Next handoff:    Council quorum (Aria + Mira + Riven votes) → ratification
                 entry in governance ledger → Mira AC8 Gate 4a sign-off path
                 unblocked + F1 follow-up commit (Dex authority, ~5 LoC) +
                 Beckett T6 report finalization + Riven T7 cost-atlas audit +
                 Riven Gate 5 disarm consideration (gated on Gate 4a+4b)
```

— Pax (@po), product owner / scope discipline guardian
