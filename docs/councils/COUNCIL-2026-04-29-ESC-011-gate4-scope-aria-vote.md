# COUNCIL ESC-011 — Gate 4 Scope (Synthetic vs Real WDO Tape) — Aria Vote

**Voter:** Aria (@architect) — architectural authority
**Date (BRT):** 2026-04-29
**Story:** T002.1.bis — `make_backtest_fn` real strategy logic (factory pattern, Aria T0b APPROVE_OPTION_B)
**Branch:** `t002-1-bis-make-backtest-fn`
**HEAD commit:** `1b7d7d9` (Dex T1 — `feat(t002.1.bis): real make_backtest_fn integration via backtest_fn_factory (Aria Option B)`)
**Quinn QA verdict:** CONCERNS (6 PASS / 1 CONCERN, 0 FAIL) per `docs/qa/gates/T002.1.bis-qa-gate.md`
**Beckett N6 verdict:** Gate 3 strict-literal PASS with explicit synthetic-walk caveat (§11) per `docs/backtest/T002-beckett-n6-2026-04-29.md`
**Vote independence:** This vote was authored BEFORE reading Beckett's ESC-011 vote (per task brief §1).

---

## 1. Question on the table

**Pergunta ESC-011:** Gate 4 statistical clearance (DSR / PBO / IC) deve ser avaliado sobre qual distribuição?

| Option | Definition |
|--------|------------|
| **A** | Real WDO tape obrigatório — Gate 4 só pós-Phase F (real-tape replay como hard precondition) |
| **B** | Synthetic walk suficiente com caveat (Gate 4 sobre N6 evidence + caveat documentado) |
| **C** | Hybrid — Gate 4a synthetic (harness-correctness) + Gate 4b real-tape (edge-existence) |

---

## 2. Aria architectural decision

### Vote

**APPROVE_OPTION_C** — hybrid Gate 4a (synthetic harness clearance) + Gate 4b (real-tape edge clearance) — with three architectural conditions binding for all subsequent voters.

### One-sentence rationale

Option C is the **only** decomposition that simultaneously (a) preserves the existing factory-pattern + closure-purity invariants ratified at T0b, (b) honors the spec §0 dual-phase carve-out (synthetic harness in T002.1.bis perimeter, real-tape replay explicitly Phase F downstream), and (c) does NOT force a refactor of the binding §I.1–§I.6 implementation contract that Dex shipped in `1b7d7d9`. Options A and B are architecturally inferior for distinct, structural reasons enumerated in §3.

---

## 3. Architectural reasoning (authority lens)

### 3.1 — What the existing architecture asserts (already-ratified invariants)

The T0b architectural review (`docs/architecture/T002.1.bis-aria-archi-review.md`) ratified by Pax T0e 10/10 + Beckett T0c HANDSHAKE_OK + Riven T0d 5/5 imposes the following **structural invariants** that ANY Gate 4 scope decision MUST respect:

| Invariant | Source | Status post-`1b7d7d9` |
|-----------|--------|-----------------------|
| §I.1 — `CPCVEngine.run` mutually-exclusive `backtest_fn` xor `backtest_fn_factory` | `engine.py:206-218` | PASS (Quinn Check 1) |
| §I.2 — `BacktestRunner.run` mirror with uniform `DeterminismStamp` injection | `runner.py:111-147` | PASS (Quinn Check 1) |
| §I.3 — `run_5_trial_fanout` accepts factory; mutual-exclusivity preserved | `cpcv_harness.py` + `test_factory_pattern.py` 2 mutex tests | PASS (7/7 factory tests) |
| §I.4 — Per-fold rebuild via factory closure; `as_of_date = min(test_events.session)` | `scripts/run_cpcv_dry_run.py:873-945` | PASS (Quinn Check 1) |
| §I.5 — `_build_daily_metrics_from_train_events` pure function | `cpcv_harness.py:324-397` | PASS |
| §I.6 — Back-compat for legacy `backtest_fn` callers (no breakage) | 10/10 existing AC2 tests + 49/49 harness suite | PASS (Quinn Check 4 — ZERO regression, +18 net) |
| Closure purity (no wall-clock, no uuid, no global mutation, byte-equal hash for identical inputs) | `cpcv_harness.py:298-322` Article IV trace | PASS — toy benchmark 6/6 with byte-equal `BacktestResult.content_sha256()` across reruns |
| Engine thread-safety (AC7 from T002.0c, future parallelization) | `engine.py:106-108` docstring | PASS — factory invocation per fold is independent across folds |

**These invariants are not up for re-litigation in ESC-011.** Any Gate 4 scope option that REQUIRES weakening, refactoring, or violating any of them is automatically architecturally non-viable.

### 3.2 — Spec §0 dual-phase carve-out: pre-existing or invented?

A core architectural question for this council is: **does the synthetic-walk vs real-tape phase split pre-exist as canonical scope (so Option C is just naming what is already there), or would it be invention now?**

**Architect ruling: PRE-EXISTING. Not invention.**

Trace:

| Source | Verbatim text | Implication |
|--------|---------------|-------------|
| Mira spec §0 ¶3 | "Beckett N4 §4.2 demonstrated that the stub returns `n_trades=0`, `pnl_rs_total=0.0`, `sharpe_daily=None` for every fold... `cpcv_harness.py:707` already documents the deferred swap: *'T11 will swap in real per-fold rebuild'*. **This spec is the swap.**" | T002.1.bis perimeter is the stub→real-strategy-logic swap. NOT real-tape replay. |
| Mira spec §0 ¶4 | "Three building blocks already coded (consumed read-only by Dex)" — `signal_rule.py`, `feature_computer.py`, `exec_backtest.py` | The spec is binding on strategy logic + cost wiring + factory rebuild. Real-tape replay is NOT in this perimeter (no parquet replay module is listed). |
| Aria T0b §"Future Phase F extensibility" | "§9 HOLD #2 Gate 5 (Riven dual-sign disarm + capital ramp) will eventually need additional per-fold state... With Option B, those are **additive parameters to the factory**" | Phase F extensibility is explicitly carved out at T0b — the factory pattern was chosen PRECISELY because it accommodates real-tape replay later as an additive change to the factory body, not a refactor. |
| Aria T0b §"Anti-Article-IV trace" row 11 | "DEFERRED-T11 M1 finding origin — Aria architecture review 2026-04-26 (cpcv_harness.py:287-307 docstring)" | The DEFERRED-T11 mechanism is the closure-purity factory; real-tape replay was never folded into M1 scope. |
| Story `T002.1.bis.story.md` AC10 | KillDecision verdict ∈ {GO, NO_GO} contract — "Strategy logic alive (synthetic walk acceptable per spec §0; real-tape Phase F downstream)" | AC10 contract literally encodes the synthetic-walk-acceptable-for-this-story-perimeter clause. |
| Quinn QA gate AC10 row | "NO_GO over real chain — F2 caveat tracked... Phase F real-tape replay is the authoritative falsification test per Mira §7 + Aria T0b dual-phase carve-out" | Quinn independently validated the dual-phase carve-out as architecturally pre-existing, not council-invented. |
| Beckett N6 §11.1–§11.3 | "Phase F is per-Mira-spec §0 explicit downstream scope and is NOT in T002.1.bis AC9 perimeter" | Beckett operationalized the same dual-phase reading from the spec. |

**Architect verdict on §3.2:** the synthetic-vs-real split is **canonical scope**, not council invention. Option C is **naming a pre-existing architectural fact** — Gate 4a maps to harness-correctness which is THIS story's perimeter, Gate 4b maps to edge-existence which is Phase F's perimeter. Article IV trace is clean.

### 3.3 — Per-option architectural analysis

#### Option A — real-tape obligatory; Gate 4 only post-Phase F

**Architectural objections (3, all structural):**

1. **Gate-monolith violation in the OPPOSITE direction.** Option A insists Gate 4 is a single monolith that ONLY fires post-real-tape. But §9 HOLD #2 Gate 4 spec (Riven custodial) was authored when real-tape replay was already canonically downstream — Gate 4 was always understood as a **statistical-clearance gate** that the harness produces, NOT an edge-existence gate. Forcing Gate 4 to wait for Phase F **conflates** two distinct architectural concerns (mechanism correctness vs economic edge) into a single gate that fires too late to provide architectural diagnostic value.

2. **Toy benchmark §7 becomes orphan.** Mira spec §7 Bailey-LdP 2014 §3 + Table 2 toy benchmark is **specifically** designed to discriminate harness-correctness from strategy-edge: "If toy benchmarks fail, the harness has a bug **independent of strategy edge**" (spec §7.3 verbatim). Under Option A, the toy benchmark has nowhere to plug into a gate — it would become a sanity-check that produces no formal sign-off authority. **This is an architectural waste of a load-bearing test (6/6 PASS in Dex T1 commit `1b7d7d9`).**

3. **Phase F gating amplification.** If Gate 4 cannot fire until Phase F real-tape exists, then EVERY downstream gate (Gate 5 Riven dual-sign disarm, Gate 6 capital ramp ESC-protocol) is also blocked on Phase F. This makes Phase F a **monolith blocker** for the entire post-Gate-3 chain. Architectural smell: gates should be **layered**, not **chained-by-monolith**.

**Verdict:** REFUTED — gate-monolith error (in the strict-blocking direction); orphans the toy benchmark; amplifies Phase F into a single point of failure.

#### Option B — synthetic walk suffices with caveat

**Architectural objections (2):**

1. **Conflates mechanism clearance with economic clearance.** Under Option B, Mira issues a single Gate 4 GO based on synthetic-walk evidence with a caveat documented. But the caveat is **not gate-bound** — there is no architectural mechanism that prevents the system from progressing to Gate 5 (capital ramp) on caveat-only evidence. **A caveat without a gate is documentation theater.** Riven §9 HOLD #2 Gate 5 disarm authority would have to re-litigate the synthetic-vs-real distinction outside the gate chain, which is exactly the kind of out-of-band re-litigation the gate framework was designed to prevent.

2. **AC10 "T002 dies per spec K1/K2/K3 falsifiable" semantics broken.** AC10 contract is that NO_GO over real-chain authorizes T002 falsification. Under Option B, NO_GO over **synthetic chain** would Gate-4-clear and propagate to AC10 falsification — but the synthetic walk is **edge-neutral by construction** (μ=0 cost-drag per `_SYNTH_*` constants). False-NO_GO would falsify T002 on a strategy that was never given the chance to demonstrate edge against real volatility regimes. **This is False-NO_GO at the architectural-contract level, not just statistical level.** Quinn explicitly flags this risk in QA gate AC10 row.

**Verdict:** REFUTED — caveat-without-gate is non-binding architecturally; AC10 contract semantics break under False-NO_GO risk.

#### Option C — hybrid Gate 4a (synthetic / harness) + Gate 4b (real-tape / edge) [CHOSEN]

**Architectural arguments FOR (5, all structural):**

1. **Layered gates, not monolithic.** Gate 4a fires on harness-correctness (DSR/PBO/IC over synthetic-walk distribution + toy benchmark §7 cross-validation). Gate 4b fires on edge-existence (DSR/PBO/IC over real-tape distribution post-Phase F). Each gate has **distinct, independently-falsifiable criteria**; each gate has its own authority owner; each gate is **architecturally bounded** (does not depend on the other except by sequencing). This is the canonical AFML §7 + §12 layered-gate pattern.

2. **Toy benchmark §7 promoted to architecturally load-bearing.** Under Option C, Gate 4a explicitly **requires** the Bailey-LdP 2014 §3 + Table 2 reproducibility test (already 6/6 PASS in `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` per `1b7d7d9`). This means the toy benchmark goes from "sanity check" to **gate-clearance evidence** — its 6/6 PASS becomes formally consumed by Gate 4a sign-off, not just a Quinn checklist line item. Existing tested infrastructure becomes load-bearing — **zero new code required**.

3. **Factory pattern + per-fold rebuild + closure isolation defensible under BOTH gates without refactor.** This is the central architect concern raised by the brief §3. Under Option C:
   - Gate 4a consumes the existing factory closure → `make_backtest_fn` over synthetic walk → `_build_daily_metrics_from_train_events` per fold. Nothing changes.
   - Gate 4b will (post-Phase F) consume the SAME factory closure → `make_backtest_fn` over real tape → SAME per-fold rebuild. The only delta is the events DataFrame carrying real bars/ticks instead of metadata-only. The closure body is **invariant** (signal_rule + triple-barrier + cost atlas + filter activation are all real-code paths, agnostic to the price-walk source).
   - **NO refactor required for Phase F.** The factory pattern was chosen at T0b PRECISELY because the per-fold lifecycle is engine-owned and the closure is consumer-only — swapping synthetic walk for real tape is an **additive change** to the factory body (new `_build_real_tape_walk` helper), not a structural change to the engine, runner, or `make_backtest_fn` signature.
   - Architectural defensibility: the closure-purity invariant (`cpcv_harness.py:298-322`) holds under both walks; the D-1 anti-leak invariant (`Percentiles126dBuilder._select_window`) holds under both walks; the `as_of_date = min(test_events.session)` contract holds under both walks. **Three load-bearing invariants survive both phases unchanged.**

4. **AC10 contract semantics preserved.** Gate 4a NO_GO over synthetic walk → "harness mechanically valid; strategy edge UNDECIDED" (no AC10 falsification yet). Gate 4b NO_GO over real tape → "strategy edge DECIDED null; AC10 falsification authorized." This restores the architectural contract that NO_GO authorizes T002 falsification ONLY when the test was given a fair chance.

5. **Phase F sequencing decoupled from Gate 4 monolith.** Gate 4a clears NOW (Mira authority on N6 + toy benchmark evidence). Gate 5 (Riven dual-sign capital ramp) becomes consumable on Gate 4a + Phase F + Gate 4b — three separable conditions, each independently auditable. Phase F retains its scope (real-tape replay + edge-existence gate) but is no longer a **single point of blockage** for the entire post-Gate-3 chain.

**Architectural cost (honest accounting):**

- One new gate node in the §9 HOLD #2 chain (Gate 4a / Gate 4b). The chain becomes Gate 1 → Gate 2 → Gate 3 → **Gate 4a → Gate 4b** → Gate 5. Riven §9 HOLD #2 spec must absorb this, but the absorption is documentation-only (no new code, no new test).
- Two distinct Mira sign-off artifacts (Gate 4a + Gate 4b) instead of one. Cost: ~1 additional sign-off doc; well below council-coordination threshold.
- Gate 4b is unblocked only by Phase F. So Phase F remains a downstream blocker for Gate 4b, but Gate 5 → Gate 6 dependency on Gate 4b is now layered (not monolithic).
- **Total LoC delta:** zero. Option C is pure governance decomposition; the existing T0b implementation contract is sufficient for both phases.

**Verdict:** APPROVED — layered gates; toy benchmark promoted; closure-purity + factory pattern + per-fold rebuild defensible under BOTH walks without refactor; AC10 contract semantics preserved; Phase F decoupled.

---

## 4. Architectural conditions for Option C (binding for all subsequent voters)

If ESC-011 ratifies Option C, the architect imposes three binding conditions:

### Condition AC-1 — Gate 4a criteria MUST be defined as harness-correctness, NOT edge-existence

Mira Gate 4a sign-off MUST explicitly enumerate:
- **K1a:** DSR distribution shape valid (σ > 0) — already PASS at N6 (σ=0.192).
- **K2a:** PBO computable and non-degenerate — already PASS at N6 (PBO=0.0, K1 DSR moves off default 0.5, K2 PBO measurably 0 ≠ default 0.5).
- **K3a:** Toy benchmark Bailey-LdP 2014 §3 + Table 2 reproducibility — already PASS at `1b7d7d9` (6/6 in `test_toy_benchmark_bailey_lopez_de_prado_2014.py`).
- **NO economic-edge claim.** Gate 4a issues "harness clears" verdict, NOT "strategy has edge" verdict. Mira sign-off doc MUST cite spec §7 verbatim and disclose synthetic-walk methodology with the same Article IV trace block already present at `cpcv_harness.py:298-322`.

### Condition AC-2 — Gate 4b is NOT pre-defined here; deferred to Phase F spec

Gate 4b criteria (DSR > 0.95 / PBO < 0.5 / IC decay over real-tape distribution) are the **canonical** Mira spec §6 thresholds and remain UNCHANGED. But the **gate-bind mechanism** (which artifact authorizes Gate 4b GO, which authority chain consumes it) is Phase F architectural scope — NOT this council's authority. ESC-011 ratifies the **decomposition**; Phase F architectural review will ratify the **binding**.

### Condition AC-3 — F1 / F2 / F3 / F4 (Quinn QA findings) MUST close before Gate 4a sign-off

Quinn QA gate `T002.1.bis-qa-gate.md` flagged 4 findings (F1 medium, F2 medium, F3 low, F4 low). Architect ruling:
- **F1 (cost atlas SHA null in determinism stamp)** — BLOCKING for Gate 4a. The audit trail invariant requires `cost_atlas_sha256` populated before Mira can sign Gate 4a; the atlas content drives the cost computation in the synthetic walk, and the SHA-locked-atlas audit chain (Riven T0d 5/5) is part of Gate 4a's harness-correctness perimeter. Estimated patch ~5 LoC in `scripts/run_cpcv_dry_run.py:_build_runner` (wire `cost_atlas_path=` and `rollover_calendar_path=`).
- **F2 (synthetic-walk caveat)** — STRUCTURAL for Gate 4a (Mira sign-off MUST disclose; this is exactly the AC-1 condition above). Already documented at `cpcv_harness.py:298-322` — sufficient surfacing already in code; only needs Mira-level governance restatement in Gate 4a artifact.
- **F3 (factory pattern test count nit "5+" vs actual 7)** — NON-BLOCKING; one-line story-doc update.
- **F4 (forward-ref placeholder stamp style)** — NON-BLOCKING; optional cosmetic.

**Net:** Condition AC-3 reduces to "F1 patch must land before Gate 4a sign-off." Estimated effort ~5 LoC + Beckett N7 re-run with stamp populated. Fully bounded.

---

## 5. Article IV trace (zero invention)

Every architectural claim in this vote traces to a primary source. No Aria invention.

| Claim | Source |
|-------|--------|
| Factory pattern + closure purity + per-fold rebuild are the T0b binding contract | `docs/architecture/T002.1.bis-aria-archi-review.md` §I.1–§I.6 + Pax T0e 10/10 ratification + Beckett T0c HANDSHAKE_OK + Riven T0d 5/5 |
| §I.1 mutually-exclusive `backtest_fn` xor `backtest_fn_factory` shipped in `1b7d7d9` | Quinn QA gate Check 1 + `engine.py:206-218` + 7/7 `test_factory_pattern.py` PASS |
| Per-fold rebuild via `_build_daily_metrics_from_train_events` shipped | Quinn QA gate Check 1 + `cpcv_harness.py:324-397` + 5/5 `test_per_fold_anti_leak.py` PASS |
| Closure purity invariant (no wall-clock, no uuid, no global mutation, byte-equal hash) | `cpcv_harness.py:298-322` Article IV trace block + Quinn QA gate §"Anti-Article-IV guards verified" |
| AC10 contract: NO_GO over real chain authorizes T002 falsification | Story `T002.1.bis.story.md` AC10 + Quinn QA gate AC10 row |
| Spec §0 dual-phase carve-out: T002.1.bis perimeter = stub→real-logic swap; Phase F = real-tape replay | Mira spec §0 ¶3 verbatim + spec §6 + Aria T0b §"Future Phase F extensibility" + Beckett N6 §11.1–§11.3 |
| Toy benchmark Bailey-LdP 2014 §3 + Table 2 anchor (False-NO_GO protection) | Mira spec §7 verbatim + 6/6 `test_toy_benchmark_bailey_lopez_de_prado_2014.py` PASS |
| Synthetic walk: σ=0.192 K3 IC=0 reflects strategy-logic-neutral construction | Beckett N6 §6 + §11.1 + `cpcv_harness.py:298-322` `_SYNTH_*` constants |
| AFML §7+§12 canonical layered-gate pattern (per-fold lifecycle factory) | Aria T0b §"Reasoning" + Lopez de Prado AFML 2018 |
| F1 cost atlas SHA null + F2 synthetic-walk caveat + F3 nit + F4 cosmetic | Quinn QA gate `T002.1.bis-qa-gate.md` issues block |
| Gate 4 spec §6 thresholds DSR>0.95 / PBO<0.5 / IC | Mira spec §6 (canonical thresholds preserved unchanged) |
| §9 HOLD #2 Gate chain (Gate 1 → Gate 5) | `project_algotrader_t002_state.md` + Riven custodial authority |
| ESC-009 condition #4 "real PnL distribution" | Mira ESC-009 council closure |
| ESC-010 6/6 ratification | `docs/councils/COUNCIL-2026-04-28-ESC-010-dual-track.md` |
| DEFERRED-T11 M1 finding | Aria architecture review 2026-04-26 (`cpcv_harness.py:287-307` original docstring) |

**Zero invented thresholds. Zero invented signatures. Zero invented gate criteria.** Gate 4a / Gate 4b decomposition is naming a pre-existing dual-phase architectural fact (spec §0); criteria for Gate 4a are existing toy benchmark §7 + N6 distribution diagnostics; criteria for Gate 4b are unchanged Mira spec §6.

---

## 6. Final vote summary

```
Voter:           Aria (@architect)
Council:         ESC-011 — Gate 4 Scope (synthetic vs real WDO tape)
Vote:            APPROVE_OPTION_C (hybrid Gate 4a synthetic / Gate 4b real-tape)
Authority:       architectural authority + DEFERRED-T11 M1 owner + T0b APPROVE_OPTION_B author
Conditions:      3 binding (AC-1 Gate 4a = harness-correctness; AC-2 Gate 4b deferred to Phase F arch review; AC-3 F1 BLOCKING for Gate 4a sign-off)
Independence:    Voted BEFORE reading Beckett's vote (per task brief §1)
Article IV:      NO INVENTION — 14 source anchors traced; Gate 4a/4b decomposition is pre-existing spec §0 dual-phase fact
Closure-purity invariant: PRESERVED under both Option C phases (no refactor required)
Factory pattern + per-fold rebuild: PRESERVED under both Option C phases (additive change at Phase F, not structural)
AC10 contract semantics: PRESERVED (Gate 4a NO_GO ≠ AC10 falsification; Gate 4b NO_GO = AC10 falsification authorized)
Toy benchmark §7: PROMOTED from sanity-check to architecturally-load-bearing Gate 4a evidence (6/6 PASS in 1b7d7d9)
Phase F monolith risk: ELIMINATED (gates layered, not chained-by-monolith)
Push gating:     Gage @devops Article II exclusive — preserved
Story scope:     UNMUTATED (Pax @po authority — preserved)
Code:            UNMODIFIED (Dex @dev authority — preserved)
QA gate:         UN-PRE-EMPTED (Quinn @qa CONCERNS verdict respected; F1 surfaced as blocking AC-3)
Mira authority:  UN-PRE-EMPTED (Gate 4a / Gate 4b sign-off remains Mira ML statistical authority — this vote architects the SCOPE, not the THRESHOLDS)
Cosign:          Aria 2026-04-29 BRT (Autonomous Daily Session, architectural authority)
```

— Aria, validando contornos
