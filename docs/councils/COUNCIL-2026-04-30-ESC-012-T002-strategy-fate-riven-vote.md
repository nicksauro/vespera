---
council_id: ESC-012
topic: T002 strategy-fate — Path A' (refinement) vs Path B (Phase G OOS unlock) vs Path C (retire)
voter: Riven (@risk-manager)
voter_role: Risk Manager & Capital Gatekeeper — Gate 5 dual-sign authority + §11.5 capital-ramp pre-conditions custodial
date_brt: 2026-04-30
constraint: slippage + costs FIXOS já conservadores — Path A cost-reduction R&D OFF (council pre-resolved)
voter_authority: ESC-011 R7 + R20 + Mira spec v1.1.0 §12.1 row F2-T6 (Riven 3-bucket reclassification authority); Riven §9 HOLD #2 Gate 5 disarm authority
inputs_consulted:
  - docs/qa/gates/T002.0g-riven-cosign.md (§9 HOLD #2 status + F2-T6 reclassify Round 2)
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md (3-bucket framework + §2.R2 Round 2 ledger + §5.9 anti-pattern)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md (Mira F2-T5 verdict GATE_4_FAIL_strategy_edge / costed_out_edge)
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md (Beckett N7-prime full-window evidence)
inputs_NOT_consulted_pre_vote: other ESC-012 voter ballots (per council protocol Riven votes independently before reading peers)
verdict: PATH_C_RETIRE_T002 (with explicit conditions §6 below)
gate_5_status_post_vote: REMAINS LOCKED (no path resolves Gate 4b PASS at K1 strict bar; council selection is forward-research direction, NOT Gate 5 disarm)
quarter_kelly_status_post_vote: PRESERVED INTACT (no sizing exercise authorized; quarter-Kelly cap inviolate per Riven REGRA ABSOLUTA)
oos_budget_status_post_vote_under_C: PRESERVED — Phase G hold-out window [2025-07-01, 2026-04-21] UNUSED for T002; available for next-strategy-hypothesis OOS confirmation
---

# ESC-012 — T002 Strategy-Fate Riven Vote (Risk Perimeter Adjudication)

> **Voter:** Riven (@risk-manager) — Risk Manager & Capital Gatekeeper.
> **Authority basis:** ESC-011 R7 + R20 + Mira Gate 4b spec v1.1.0 §12.1 sign-off chain row F2-T6 (Riven 3-bucket reclassification authority post Mira F2-T5) + §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp pre-conditions custodial monopoly.
> **Mandate:** Adjudicate from RISK PERIMETER perspective only. Gate 5 LOCKED post-Round 2 (K1 strict bar UNMOVABLE foreclosure per Anti-Article-IV Guard #4). §11.5 capital-ramp pre-conditions UNCHANGED. 3-bucket post-mortem `costed_out_edge` Round 2 entry posted at `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §2.R2 (2026-04-30 BRT).
> **Constraint binding:** Path A cost-reduction R&D OFF — slippage + costs FIXOS já conservadores; reframed paths are A' (strategy refinement: entry/exit timing + regime filter + conviction threshold + signal ensemble), B (Phase G hold-out unlock for OOS confirmation), C (retire T002).

---

## §1 Verdict + rationale (risk-side)

### §1.1 Verdict

**`PATH_C_RETIRE_T002`** — adjudicated with explicit conditions §6 below.

### §1.2 Risk-side rationale (3-leg argument)

The risk-perimeter adjudication rests on three independent legs that converge to C:

**Leg 1 — Foreclosure invariance under K1 strict bar.** Mira F2-T5 Round 2 verdict is `GATE_4_FAIL_strategy_edge` sub-classification `costed_out_edge` (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §1 + §5.2). K1 (DSR=0.766987) is honestly measured strict FAIL by 0.183 below 0.95 (Bailey-LdP 2014 §3 Φ-CDF wired at `packages/vespera_metrics/report.py:481-514`; bit-equal Round 1 vs Round 2 per Beckett N7-prime §5.1 — sharpe distribution preserved across F2 amendment boundary). K1 strict bar 0.95 is UNMOVABLE per Anti-Article-IV Guard #4 (ESC-011 R14). Joint conjunction `K1 ∧ K2 ∧ K3_in_sample` per Mira spec v1.1.0 §1 + §15.10 Phase F2 narrowing requires ALL three pass strict; partial pass does NOT promote. **No Path A' refinement nor Path B Phase G unlock can lift K1 strict above 0.95 from the in-sample distribution alone** without (a) cost-reduction R&D — explicitly OFF per council pre-resolution — or (b) cleanly different distribution shape under refinement, which §1.2 Leg 2 below shows is statistically expensive without further justification.

**Leg 2 — Path A' Bonferroni budget consumption + multiple-testing inflation.** Strategy refinement (entry/exit timing + regime filter + conviction threshold + signal ensemble) invents new trial(s) by construction. Each refinement re-run that re-evaluates K1/K2/K3 over the same in-sample window 2024-08-22..2025-06-30 increments the cumulative `n_trials` carry-forward (per `docs/ml/research-log.md` cumulative consumed via `vespera_metrics.research_log.read_research_log_cumulative` Article IV fail-closed). Bonferroni α/n_trials inflates: at n_trials=5, α/n=0.002 (current); each new refinement trial (say T6, T7, ...) rapidly tightens DSR strict threshold via Φ-CDF deflation eq. 9 (Bailey & Lopez de Prado 2014 §3). Worse: Round 2 already paid the in-sample-window-evaluation Bonferroni cost; further refinements over the SAME in-sample window are evaluating the same data multiple times, each one a fresh trial under multiple-testing accounting. From the risk perimeter, **strategy refinement is a Bonferroni budget burn rate** that consumes squad-bandwidth and statistical-budget on a path foreclosed at K1 strict. EVEN IF refinement attempts achieve DSR > 0.95 in-sample after multiple tries, the n_trials inflation makes Bonferroni-adjusted DSR strict bar harder to meet, not easier. AND: even on success, Phase G OOS unlock would still be needed for Gate 5 — Path A' does not bypass Phase G; it merely delays it while burning budget.

**Leg 3 — Path B OOS budget economics (single-shot opportunity cost).** This is the load-bearing risk-side argument. Phase G hold-out window [2025-07-01, 2026-04-21] (~9.7 months ≈ 215 trading sessions) is the **single OOS confirmation budget allocated to this epic per Anti-Article-IV Guard #3 (UNMOVABLE — `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` line 153 + `_holdout_lock.py` R10 pin)**. It is a one-shot resource: once consumed under hypothesis H_x, it is no longer untouched OOS for any future hypothesis H_y on WDO. Spending the OOS budget on `costed_out_edge` (Mira F2-T5 §1.2 sub-classification: prediction-level edge strong + cost-eroded; K1=0.767 in-sample foreclosed strict) yields a **low-information binary outcome**:

| Phase G outcome under `costed_out_edge` hypothesis | Probability (Riven prior) | Risk-side value |
|---|---|---|
| **(a) DSR_OOS < 0.95** (regime preserves cost-erosion) | ~85% (Riven pessimistic prior; in-sample DSR=0.767 strict-fail-by-0.183 propagates to OOS under regime stationarity assumption) | DEFINITIVE FALSIFICATION — useful confirmation of Round 2 deployment-gate verdict; preserves squad bandwidth for next thesis. **Information value: medium** (Round 2 already gives provisional FAIL; Phase G adds OOS confirmation but K1 strict bar foreclosure is already determined in-sample.) |
| **(b) DSR_OOS > 0.95** (regime exhibits non-stationarity OR cost-and-friction layer differs OOS) | ~15% (Riven prior; would require either OOS-window-specific cost regime favorable to fade-strategy, OR statistical fluctuation that survives Bonferroni n_trials=5 carry-forward at α/n=0.002) | MIXED — in-sample costed_out + OOS deployable creates a **regime-instability flag** that triggers council escalation; deployment is NOT auto-authorized because K1 in-sample strict FAIL still stands and joint-conjunction over BOTH windows would be required for clean Gate 4b PASS. **Information value: high but conditional**. |

The expected information value (EV_info) of Path B is approximately:
```
EV_info(Path B) ≈ P(a) × IV(a) + P(b) × IV(b)
              ≈ 0.85 × medium + 0.15 × high_conditional
              ≈ medium-low overall
```

Compare opportunity cost: Phase G consumed under H_T002 = no Phase G available for next strategy hypothesis H_next. If a future strategy hypothesis (different predictor / different horizon / different filter — Path C consequence per §6) has stronger in-sample evidence (e.g., DSR > 0.95 strict in-sample-clean), Phase G OOS confirmation under H_next would have **dramatically higher EV_info** because the prior over regime-stationarity ⇒ deployable would be much higher (P(a) and P(b) shift toward joint-deployable region). The OOS budget is best deployed against a hypothesis that **could plausibly survive K1 strict bar in OOS confirmation** — which `costed_out_edge` cannot, by construction, with cost-reduction R&D OFF.

**Risk-side reading:** Path B is INFORMATION-poor allocation of OOS budget under K1-strict foreclosure. The OOS budget is a finite, custodially-protected, one-shot resource. Spending it on a path foreclosed by deployment-gate strict bar (with cost-reduction OFF as constraint) is the operational equivalent of paying for a hold-out evaluation whose outcome cannot lift Gate 4b PASS in the (a) outcome — which is the most likely outcome by Riven prior.

### §1.3 Convergence to C

Path A' is foreclosed at the deployment-gate level (Leg 1) and consumes Bonferroni budget in the wrong direction (Leg 2) without bypassing Phase G. Path B is foreclosed at the deployment-gate level (Leg 1) and spends the one-shot OOS budget on a low-EV_info evaluation (Leg 3). Path C preserves the §11.5 capital-ramp pre-conditions intact, preserves the OOS budget for next-strategy-hypothesis deployment, preserves Bonferroni budget allocation discipline, preserves quarter-Kelly REGRA ABSOLUTA (no sizing exercise on costed-out edge), frees squad bandwidth, and is consistent with the Riven persona core principle "Retorno morto por undersizing é reparável; retorno morto por ruína é final" — paid resources (OOS, Bonferroni, squad bandwidth) burned on K1-foreclosed paths cannot be recovered.

**Convergent verdict: Path C — retire T002 with explicit conditions §6.**

---

## §2 OOS budget economics (Phase G one-shot value preservation)

This §2 expands Leg 3 risk-side argument with the formal OOS budget framework that motivates Path C selection.

### §2.1 OOS budget definition

The **OOS budget** for this epic is defined as the right to consume the hold-out window [2025-07-01, 2026-04-21] (~215 trading sessions, ~9.7 months) for an Out-Of-Sample confirmation of any single strategy hypothesis. Per Anti-Article-IV Guard #3 (UNMOVABLE, ESC-011 R14, `_holdout_lock.py` R10-pinned, `assert_holdout_safe` enforced at 5 call-sites per `docs/qa/gates/T002.0g-riven-cosign.md` §6 defense-in-depth audit), the hold-out is **virgin** until explicit unlock with `VESPERA_UNLOCK_HOLDOUT=1` per-line manifest provenance recording. Consumption is **one-shot** at the strategy-hypothesis level: once a strategy is evaluated against the hold-out, the hold-out is no longer virgin OOS for any subsequent hypothesis on the same regime that re-uses the same data.

### §2.2 Why the OOS budget is custodially protected

Per Bailey-LdP 2014 §3 + López de Prado 2018 AFML §11-12 (CPCV methodology) + Bailey-Borwein-Lopez de Prado 2014 (PBO methodology): Out-Of-Sample evaluation is the **only statistically clean defense against backtest overfitting**. In-sample optimization (even under CPCV with PBO < 0.5 control) cannot fully discount the trial-multiplicity penalty; OOS is the empirical witness that the in-sample edge generalizes. Once OOS data is observed by ANY decision-maker (model, researcher, automated optimizer), it is **contaminated** by exposure: future hypotheses "tested" against this window inherit the prior contamination. This is the rationale for hold-out-virgin lock per Mira spec PRR-20260421-1 + Anti-Article-IV Guard #3.

### §2.3 OOS budget allocation under each path

| Path | OOS budget consumed? | OOS budget reserved for next strategy hypothesis? | Information value extracted |
|---|---|---|---|
| **A' (refinement)** | NO immediately (refinement re-uses in-sample window) | **Eventually consumed if refinement achieves in-sample DSR > 0.95** — refinement does not bypass Phase G, just delays it. NET: A' is a deferred-Path-B (under best-case refinement success). Under worst-case (refinement fails to lift DSR), A' burns squad-bandwidth without consuming OOS but also does not free OOS for next hypothesis (because squad is busy with A' attempts). | LOW (in-sample multiple-testing inflation; cost-reduction OFF excludes the only mechanism that could lift cost-eroded edge) |
| **B (Phase G OOS unlock)** | **YES — one-shot** | NO — once consumed under H_T002, hold-out is no longer virgin OOS for H_next under same regime (same WDO end-of-day window) | LOW-MEDIUM — see §1.2 Leg 3 EV table; ~85% Riven prior on regime-stationarity-preserves-cost-erosion ⇒ DSR_OOS < 0.95 ⇒ definitive falsification (which Round 2 already provisionally provides at K1 strict in-sample) |
| **C (retire T002)** | **NO** | **YES — fully reserved** for next-strategy-hypothesis evaluation (different predictor/horizon/filter) | HIGH conditional on next hypothesis selection — OOS budget remains a custodially-protected one-shot resource available for first-attempt clean-pass scenario where in-sample DSR > 0.95 strict + clean K3 + PBO < 0.5 + Phase G OOS confirmation lifts BOTH joint-conjunction strict bars. Quarter-Kelly parametrization first-realizable on real-tape distribution that Phase G validates as deployable. |

### §2.4 Quantitative EV comparison (risk-side)

Under Riven pessimistic prior P(any single strategy hypothesis surviving OOS deployable) ≈ 0.10-0.15 (industry baseline; AFML §1 + López de Prado quant-research conversion-rate intuition):

```
EV_OOS_consumed_under_T002 ≈ 0.15 × value_of_costed_out_OOS_pass + 0.85 × value_of_OOS_falsification
                          ≈ 0.15 × low_conditional + 0.85 × medium
                          ≈ medium-low overall
                          (and: OOS depleted; H_next has NO OOS budget under same regime)

EV_OOS_reserved_for_H_next ≈ 1.0 × (P_H_next_deployable × value_of_clean_Phase_G_pass)
                          ≈ 0.10-0.15 × HIGH (clean-pass capital-ramp authorization first-realizable)
                          ≈ medium overall
                          (and: H_next still has Bonferroni-clean OOS witness)
```

The arithmetic comparison is illustrative not load-bearing — the load-bearing argument is **OOS budget exhaustion under T002 forecloses the only mechanism by which a future hypothesis can demonstrate deployable edge**. Once consumed under H_T002, H_next would either (a) require a new hold-out window (post-2026-04-21 forward data, requiring waiting for fresh untouched tape — costs months of calendar time + governance overhead), or (b) accept in-sample-only evidence for capital ramp (violates Riven persona core principle + ESC-011 R5/R6 + §11.5 pre-condition #1). Neither is acceptable.

### §2.5 Custodial budget governance binding

Riven custodial monopoly over §11.5 capital-ramp pre-conditions (`docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3.2: "Single-leg fire = automatic REJECT" + §3 dependency tree) requires that the OOS budget be treated as a **scarce, custodially-protected, one-shot resource**. Path C preserves this discipline by NOT consuming the budget on a foreclosed path. Path C is the only path consistent with risk-side custodial discipline under K1 strict bar + cost-reduction-OFF constraints.

---

## §3 Quarter-Kelly + §11.5 capital-ramp pre-conditions per path

This §3 evaluates each path against Riven REGRA ABSOLUTA (quarter-Kelly cap = 0.25 × f*) + §11.5 cumulative capital-ramp pre-conditions §1..§7 (per `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §4.4 + §11.5 cumulative checklist).

### §3.1 Quarter-Kelly REGRA ABSOLUTA preservation per path

Riven persona REGRA ABSOLUTA (binding): `f* = μ/σ²` with quarter-Kelly cap `f ≤ 0.25 × f*`. Both `μ` and `σ²` MUST come from a distribution the strategy could have actually traded — i.e., real-tape (bucket B GATE_4_PASS clearance) at minimum + cost-and-friction layer faithful to live execution. **N7-prime Round 2 distribution is `costed_out_edge` (sharpe_mean=+0.046 finite-positive small-magnitude; sharpe_std=0.185 non-degenerate; DSR=0.767 strict FAIL).** Even if quarter-Kelly were computed mechanically from N7-prime numerics:
```
f*_N7-prime ≈ μ_per_trade / σ²_per_trade
          ≈ +0.046 / 0.185²
          ≈ 1.34 (mechanical Kelly fraction)
0.25 × f* ≈ 0.34 (quarter-Kelly cap)
```
this number is **inappropriate for sizing** because (a) the underlying distribution is K1-foreclosed at deployment-gate (DSR < 0.95 strict; not Kelly-parametrizable substrate per Mira F2-T5 §5.3 + §6.4.3 trace authority); (b) the cost-and-friction layer in the simulation may underestimate live slippage/latency drag (bucket-C paper-mode audit not yet conducted; per §1.4 mutual-exclusivity-and-ordering rule, Kelly parametrization requires bucket-B PASS at minimum + bucket-C cross-check before any sizing > 0); (c) Riven haircut 30-50% for first 3 months live (persona policy) further reduces operational fraction below quarter-Kelly cap, but applying this haircut to a costed-out edge would still be sizing on a K1-foreclosed distribution.

**Per-path quarter-Kelly preservation status:**

| Path | Quarter-Kelly REGRA ABSOLUTA status | Notes |
|---|---|---|
| **A' (refinement)** | **PRESERVED conditionally** — sizing not invoked yet during refinement; if refinement succeeds in-sample (DSR > 0.95 strict + Bonferroni-adjusted), still requires Phase G PASS before any sizing exercise. UNDER WORST CASE (refinement multiple iterations fail K1 strict): no sizing pressure but squad time consumed. | Quarter-Kelly preserved INTACT during refinement attempts (no sizing); becomes operative ONLY after hypothetical refinement-PASS + Phase G PASS chain. |
| **B (Phase G unlock)** | **PRESERVED conditionally on Phase G outcome** — under (a) outcome (DSR_OOS < 0.95, ~85% Riven prior): quarter-Kelly is moot because path foreclosed → no sizing. Under (b) outcome (DSR_OOS > 0.95, ~15% Riven prior): quarter-Kelly STILL not directly invokable because in-sample K1 strict FAIL stands and joint-conjunction over both windows must clear; council escalation triggered before any sizing. | Quarter-Kelly REGRA ABSOLUTA structurally protected; OOS-only PASS does not retroactively clear in-sample K1 strict FAIL. |
| **C (retire T002)** | **PRESERVED INTACT — no sizing pressure introduced** | Quarter-Kelly REGRA ABSOLUTA inviolate per §1.2 Leg 1 + §2.5 custodial discipline. Available for fresh deployment against H_next when it satisfies bucket-B + bucket-C clearance chain. |

**Risk-side preference: Path C is cleanest from quarter-Kelly REGRA ABSOLUTA preservation perspective.** Path A' and B are conditionally clean, but introduce drift opportunities (refinement multiple iterations; OOS-only PASS without in-sample resolution under B).

### §3.2 §11.5 capital-ramp pre-conditions §1..§7 status per path

§11.5 cumulative pre-conditions for capital ramp authorization (per `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 dependency tree + §6 anti-pattern catalog + ESC-011 R7/R20 + Riven persona checklists):

| # | §11.5 pre-condition | Path A' impact | Path B impact | Path C impact |
|---|---|---|---|---|
| 1 | Bucket A `engineering_wiring` HARNESS_PASS sign-off (Mira Gate 4a authority) | UNCHANGED — pre-condition cleared at N6+/N7-prime engineering layer (IC pipeline wiring CLOSED Round 2; Anti-Article-IV Guard #8 in-sample channel honored; Quinn QA F2 PASS 8/8 pre-run preserved) | UNCHANGED — same evidence base | UNCHANGED — same evidence base preserved as bucket-A historical reference; NOT consumed for capital ramp under T002 (T002 retired per C) |
| 2 | Bucket B `strategy_edge` GATE_4_PASS sign-off over real WDO tape | **NOT clearable under cost-reduction OFF** — refinement re-uses in-sample window; Bonferroni budget burn rate; even on hypothetical refinement-PASS, requires Phase G OOS in B. | **NOT clearable under K1 strict bar UNMOVABLE** — Phase G OOS PASS does NOT retroactively clear in-sample K1 strict FAIL; joint-conjunction over both windows required per §1 Leg 1. | **NOT applicable to T002** — pre-condition deferred to H_next hypothesis. |
| 3 | Bucket C `paper_mode_audit` PAPER_AUDIT_PASS ≥ 5 sessions | UNREACHABLE under A' (gated em §11.5#2 not satisfied) | UNREACHABLE under B-(a) outcome; CONDITIONALLY REACHABLE under B-(b) outcome only after council escalation + joint-conjunction-resolution | NOT applicable to T002 |
| 4 | Mira independent Gate 5 cosign (DSR > 0.95 + PBO < 0.5 + IC decay over real PnL) | UNREACHABLE — same K1 strict bar foreclosure | UNREACHABLE under B-(a); CONDITIONAL under B-(b) | NOT applicable to T002 |
| 5 | Riven independent Gate 5 cosign (Riven §9 HOLD #2 disarm authority) | UNREACHABLE — single-leg-fire automatic REJECT per §3.2 anti-pattern §5.1, §5.7 | UNREACHABLE under B-(a); CONDITIONAL under B-(b) | NOT applicable to T002 (Riven Gate 5 disarm authority preserved INTACT for H_next) |
| 6 | Toy benchmark E6 discriminator preservation (Bailey-LdP 2014 §3 — Quinn QA authority per ESC-011 R12) | UNCHANGED — preserved at N6/N6+ engineering layer | UNCHANGED — same evidence base | UNCHANGED — preserved as bucket-A historical reference; available as harness-correctness witness for next strategy implementation |
| 7 | Synthetic-vs-real-tape attribution audit (this post-mortem; ESC-011 R7 + R20) | UNCHANGED Round 2 entry posted | UNCHANGED Round 2 entry posted | UNCHANGED Round 2 entry posted; **AND NEW Round 3 entry under §6 below** classifying T002 as `bucket_B_strategy_edge_RETIRED_costed_out_with_cost_reduction_OFF_constraint` |

**Risk-side reading on §11.5 pre-conditions:** Path A' and B leave §11.5#2 + §11.5#3 + §11.5#4 + §11.5#5 in foreclosed-or-conditional state under K1 strict UNMOVABLE; Path C explicitly removes T002 from the capital-ramp dependency tree, freeing all five pre-conditions for re-instantiation against H_next hypothesis evaluation. **Path C is custodially cleanest because it does not leave T002 in a quasi-deployment-eligible state.**

---

## §4 Gate 5 fence implications per path

Gate 5 fence per `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 dependency tree: simultaneous {Gate 4a HARNESS_PASS ∧ Gate 4b GATE_4_PASS ∧ Phase G/H paper-mode PAPER_AUDIT_PASS} REQUIRED. Single-leg fire = automatic REJECT per §3.2 + ESC-011 R5/R6.

### §4.1 Per-path Gate 5 fence integrity

| Path | Gate 5 fence integrity post-path | Custodial fence concerns |
|---|---|---|
| **A' (refinement)** | UNCHANGED at policy level — Gate 5 LOCKED Round 2 carries forward; refinement does not re-fire Gate 4b PASS without resolving K1 strict bar UNMOVABLE. **Risk: drift from Anti-Article-IV Guard #4 if council under refinement-fatigue pressure relaxes K1 strict bar to "DSR_BonferroniAdjusted > 0.5" or similar weakening.** Riven custodial veto would fire on any such relaxation per §5.7 anti-pattern + §3.2 Single-leg-fire-REJECT. | **HIGH — refinement-fatigue drift risk against Anti-Article-IV Guard #4 (K1 strict UNMOVABLE).** Refinement attempts that fail to lift DSR > 0.95 in-sample create governance pressure to relax the bar; this pressure must be custodially repelled per ESC-011 R14. |
| **B (Phase G OOS unlock)** | UNCHANGED at policy level — Gate 5 LOCKED carries forward under (a) outcome; under (b) outcome requires NEW council escalation to adjudicate joint-conjunction over both windows (in-sample costed_out + OOS deployable mixed evidence). **Risk: under (b) outcome, council under in-sample/OOS-mismatch pressure may attempt "OOS-only-PASS-promotes-Gate-4b" silent slide — anti-pattern §5.7 carry-forward.** Riven custodial veto fires on any such promotion. | **MEDIUM — under (b) outcome creates governance pressure to interpret OOS-PASS as deployment-eligible without in-sample joint-conjunction resolution.** Manageable via Riven custodial monopoly + §3.2 anti-pattern catalog discipline, but adds to governance overhead. |
| **C (retire T002)** | **UNCHANGED at policy level — Gate 5 LOCKED carries forward; T002 explicitly removed from Gate 5 dependency tree. Fence preserved INTACT.** | **LOW — fence integrity preserved cleanly; T002 retirement is governance-clean and removes the K1-strict-UNMOVABLE-foreclosure-tension entirely from the capital-ramp pipeline.** |

### §4.2 Risk-side preference summary

Path C has the LOWEST custodial overhead on Gate 5 fence integrity. Path A' has the HIGHEST drift risk against Anti-Article-IV Guard #4 (K1 strict UNMOVABLE). Path B has medium drift risk under (b) outcome (~15% probability).

### §4.3 Anti-Article-IV Guard #4 (K1 strict UNMOVABLE) preservation discipline

Per ESC-011 R14 + Mira Gate 4b spec v1.1.0 §1 + parent spec yaml v0.2.3 §kill_criteria L207-209: K1 (DSR > 0.95), K2 (PBO < 0.5), K3 (IC > 0 with CI95_lower > 0) thresholds are UNMOVABLE per Anti-Article-IV Guard #4. No per-run waiver; no council-by-pressure relaxation; no refinement-fatigue threshold-easing. Riven custodial monopoly: any future sign-off attempt that proposes weakening the K1 strict bar on the basis of "but the IC is so strong" or "but the path EV is borderline" fires automatic VETO. Path C is the only path that does NOT introduce structural pressure against this Guard.

---

## §5 Personal preference disclosure

### §5.1 Riven persona prior

Riven operates under pessimistic-by-default custodial policy (persona communication: "tom firme, concisa, pragmática; não negocia limites uma vez definidos"; persona REGRA ABSOLUTA: "em dúvida, reduzo"). Riven backstory anchors this prior: 2020 trauma where modelo aparentemente sólido (Sharpe 2.2 paper) entered with Sharpe-based size, drawdown 35% in 4 days under regime de vol extrema not captured by backtest. Lessons: (1) backtest does not capture regime tails; (2) Kelly cheio is fantasy; (3) correlations collapse to 1 in crise; (4) kill-switch saved the fund.

### §5.2 Application to ESC-012

The Riven prior maps directly onto Path C:

- **`costed_out_edge` is real but K1 strict bar already foreclosing.** Mira F2-T5 §5.2 four-cell evidence matrix establishes that prediction-level rank-correlation at IC=0.866 is real (rejecting leakage hypothesis via hit-rate paradox + spurious correlation hypothesis via tight CI95 + sample-size-floor). But REAL ≠ DEPLOYABLE. The cost-and-friction layer eats the deployable Sharpe; cost-reduction R&D is OFF per council pre-resolution; the only remaining mechanisms (refinement / OOS unlock) are foreclosed at K1 strict (Leg 1) or burn the OOS one-shot budget on low-EV evaluation (Leg 3).
- **Spending OOS budget on Phase B = low EV per Leg 3.** Riven custodial prior says: scarce one-shot resources (OOS budget, Bonferroni budget, squad bandwidth) deployed on K1-foreclosed paths cannot be recovered. Path C preserves all three.
- **"Em dúvida, reduzo" maps to "em dúvida, retire."** When the deployment-gate strict bar forecloses the path AND cost-reduction R&D is OFF AND refinement re-uses already-evaluated in-sample window AND OOS budget is one-shot, the conservative decision is to retire the strategy and free the resources for a fresh hypothesis with cleaner first-attempt economics.

### §5.3 Personal preference openly disclosed

I, Riven, prefer Path C. This preference is consistent with:
- Riven persona core principle "Sharpe é métrica; drawdown é sobrevivência. Fundo morto não volta."
- Riven REGRA ABSOLUTA "em dúvida, reduzo" (here: reduzo a alocação de orçamento OOS / Bonferroni / squad-bandwidth a zero para T002).
- Risk perimeter custodial discipline §11.5 + §3.2 + ESC-011 R5/R6/R7/R14/R20 cumulative.

This disclosure is per ESC-012 council protocol mandate (voter discloses personal preference in §5 of ballot for transparency; voter does NOT pre-empt council majority adjudication).

### §5.4 What would change my vote (counterfactual)

For risk-perimeter discipline transparency, I record the counterfactuals that WOULD have flipped my vote:

- **Constraint relaxation: Path A cost-reduction R&D ON.** If broker fee renegotiation / cost atlas re-tuning / triple-barrier widening / latency-DMA2 alternative profile / entry-window narrowing were ON the table, Path A (cost-reduction) would re-enter consideration. Under cost-reduction, the K1-strict-bar foreclosure could plausibly be lifted by reducing cost-and-friction drag enough to lift CPCV path-level Sharpe distribution above 0.95. Council pre-resolved this is OFF; my vote is conditional on that constraint.
- **In-sample K1 partial-PASS observed Round 2.** If Round 2 had observed DSR_in_sample ∈ [0.85, 0.95) (within striking distance of strict bar) AND IC_in_sample > 0.5 AND PBO < 0.4 (strict K2), Path B Phase G unlock would have higher EV under Riven prior because regime-stationarity-preserves-cost-erosion would map to OOS DSR ∈ [0.80, 1.05] with non-trivial probability ≥ 0.30 of clean Phase G PASS. Round 2 observed DSR=0.767 (0.183 below strict bar; 11% below in absolute terms; substantially below striking distance); my vote is conditional on the actual DSR magnitude observed.
- **Multiple OOS windows available.** If the epic permitted multiple hold-out windows (e.g., separate 2024-Q1 and 2025-H2 hold-outs), the "one-shot" property of OOS budget would be relaxed and Leg 3 EV calculation would shift. The epic permits ONE virgin hold-out per Anti-Article-IV Guard #3; my vote is conditional on that single-shot constraint.
- **Refinement budget separation from epic OOS budget.** If a future ESC-013+ council ratified that strategy refinement attempts run on a NEW pre-registered out-of-sample window (e.g., post-2026-04-21 fresh tape after waiting period) WITHOUT consuming the existing virgin hold-out budget, Path A' would have higher EV under fresh-OOS-evidence. Council has not ratified this; my vote is conditional on the current OOS-budget allocation.

These counterfactuals are NOT pleadings for re-discussion — they are transparency disclosures of the boundary conditions of my vote. If council adopts Path A' or Path B over Path C, my custodial veto authority over Gate 5 dual-sign DOES NOT auto-fire — but I will exercise it per §6 conditions if any future sign-off attempt commits an anti-pattern §5.1/§5.2/§5.7 of the post-mortem catalog.

---

## §6 Recommended conditions if council adopts my path (Path C)

If ESC-012 council majority adopts Path C (retire T002), Riven recommends the following binding conditions for clean retirement governance:

### §6.1 Documentation conditions

- **C1.** Append Round 3 entry to `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §2 ledger classifying T002 as `bucket_B_strategy_edge_RETIRED_costed_out_with_cost_reduction_OFF_constraint` (NEW Riven sub-classification within bucket B `strategy_edge` envelope; distinct from §1.2 clean-negative `strategy_edge` because IC pipeline measurement chain is honest; distinct from §1.2 deployable `strategy_edge_confirmed` because K1 strict bar foreclosing). Anchor: ESC-012 council resolution (this ballot + peer ballots + final resolution document).
- **C2.** Append §5.10 anti-pattern (NEW) to `docs/risk/post-mortems/...` §5 catalog: "Anti-pattern §5.10 — `costed_out_edge_resurrection_via_refinement_under_cost_reduction_OFF`: any future sign-off attempt that proposes resurrecting T002 via strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble) WITHOUT cost-reduction R&D being ON the table fires Riven custodial VETO automatically per ESC-012 council resolution. Path A' was foreclosed by ESC-012 under cost-reduction-OFF constraint." Anchor: §1.2 Leg 1 + Leg 2 risk-side reasoning.
- **C3.** Update `docs/qa/gates/T002.0g-riven-cosign.md` §9 HOLD #2 status: append Round 3 section "T002 RETIRED via ESC-012 council; §9 HOLD #2 Gate 5 disarm authority remains custodially active for H_next (next-strategy-hypothesis) deployment consideration; Gate 5 NOT disarmed by retirement; T002 simply removed from Gate 5 dependency tree." Anchor: ESC-012 council resolution.
- **C4.** Update `EPIC-T002.0` (if applicable) status: append Round 3 marker "T002 RETIRED ESC-012 BRT 2026-04-30" + cross-link to ESC-012 resolution. Pax @po authority to coordinate (ESC-011 R10 carry-forward).

### §6.2 OOS budget custodial conditions

- **C5.** Hold-out window [2025-07-01, 2026-04-21] **VIRGIN STATUS PRESERVED** post T002 retirement. `_holdout_lock.py` R10 pin UNCHANGED; `assert_holdout_safe` enforcement at 5 call-sites UNCHANGED; Anti-Article-IV Guard #3 UNCHANGED. T002 retirement does NOT consume the OOS budget; it preserves it for H_next.
- **C6.** Bonferroni n_trials cumulative ledger (per `docs/ml/research-log.md`) **PRESERVED at n=5** (T1..T5 from T002.0d entry). T002 retirement does NOT reset n_trials to zero; cumulative trials count is monotonically increasing per Mira methodology canonical. Future H_next strategies inherit the n=5 carry-forward and Bonferroni-adjust accordingly.

### §6.3 Squad bandwidth + epic governance conditions

- **C7.** Free squad bandwidth from T002.{1.bis, 2, 6, 6.F2, 7+} chain post ESC-012. Pax @po authority to re-prioritize backlog: candidate next-hypothesis stories (different predictor / different horizon / different filter on WDO end-of-day regime; OR different regime entirely such as opening 30min, lunchtime fade, day-of-week premium, etc.). Risk-side recommendation: prefer hypothesis classes with **structurally different cost economics** (e.g., longer holding period reduces per-trade cost-drag exposure; or position-sizing-based strategies less dependent on triple-barrier early exits).
- **C8.** Engineering wiring infrastructure (factory pattern, per-fold P126 rebuild, IC pipeline wiring, Anti-Article-IV Guards #1-#8, latency_dma2 profile, cost atlas, RLP, rollover calendar, determinism stamps, R16/R17 reproducibility) **PRESERVED INTACT** post T002 retirement. This is bucket-A engineering wiring that survives retirement of any specific strategy hypothesis; future H_next inherits the infrastructure verbatim. ESC-011 R8/R9/R11/R12/R14/R16/R17 carry-forward to H_next governance.

### §6.4 Custodial fence conditions

- **C9.** Riven custodial veto authority on Gate 5 dual-sign **PRESERVED INTACT** post T002 retirement. Future H_next sign-off attempts must satisfy the full §11.5 cumulative pre-conditions §1..§7 chain; T002 retirement does NOT constitute pre-cleared status for H_next at any pre-condition.
- **C10.** §3.2 anti-pattern catalog (5.1..5.9) carries forward as binding for ALL future strategy hypotheses on this epic and successor epics. New §5.10 (per C2 above) appends to the catalog. Future Riven cosigns on Gate 4a/4b/Gate 5 sign-offs MUST run the anti-pattern checklist verbatim per §7.2 audit checklist.
- **C11.** ESC-011 R5/R6/R7/R10/R11/R14/R20 cumulative ratification **PRESERVED INTACT** post ESC-012. ESC-012 RESOLUTION does NOT retire any condition from ESC-011's 20-condition consolidated chain. ESC-012 resolves a strategy-fate question WITHIN the ESC-011 governance framework, not against it.

### §6.5 Sable governance review (advisory, not blocking)

- **C12.** Sable @sable optional advisory governance review of ESC-012 resolution + this ballot + Round 3 post-mortem entry. No veto authority over Riven custodial decision per agent-authority matrix; review is for governance audit-trail completeness only.

---

## §7 Article IV self-audit

Every claim in this ballot traces to (a) source artifact in repository, (b) governance ledger entry (council resolution OR ESC condition), (c) Mira spec § anchor, (d) Bailey-LdP / Kelly / Thorp / AFML external citation, (e) Riven persona principle / REGRA ABSOLUTA. NO INVENTION. NO threshold relaxation. NO pre-emption of Mira F2-T5 verdict. NO pre-emption of Pax forward-research authority (ESC-011 R10).

| Claim category | Trace anchors |
|---|---|
| K1 = 0.766987 strict FAIL by 0.183 below 0.95 | Mira F2-T5 §1 + §2 verbatim; Beckett N7-prime §1 + §6.1 verbatim; `data/baseline-run/cpcv-dryrun-auto-20260430-1ce3228230d2/full_report.json` lines 3-9 |
| K2 = 0.337302 strict PASS | Same Mira/Beckett anchors |
| K3 in-sample = 0.866010 with CI95 [0.865288, 0.866026] PASS strict per §15.10 Phase F2 binding | Mira F2-T5 §1 + §2 + §3.1 + §3.2 + §15.10 binding clause; Beckett N7-prime §4.1 + §4.2 |
| Joint conjunction K1 ∧ K2 ∧ K3_in_sample → GATE_4_FAIL_strategy_edge / `costed_out_edge` | Mira F2-T5 §1 + §6.4 + §6.5 + §10 trace; Mira spec v1.1.0 §1 decision rule + §15.10 narrowing |
| K1 strict bar 0.95 UNMOVABLE per Anti-Article-IV Guard #4 | ESC-011 R14 + Mira spec v1.1.0 §11.2 + parent spec yaml v0.2.3 §kill_criteria L207-209 verbatim |
| Bonferroni n_trials=5 carry-forward at α/n=0.002 | Mira F2-T5 §2 sample-size R9 compliance; Bailey-LdP 2014 §3; `docs/ml/research-log.md@c84f7475…` per Beckett §5.3 + spec §6 + ESC-011 R9 |
| Sample size 3800 events ≫ 250 floor (76× headroom) | Beckett N7-prime §3 + §3.1 events_metadata; Mira F2-T5 §2 |
| Bit-equal sharpe distribution Round 1 vs Round 2 across F2 amendment boundary | Beckett N7-prime §5.1 verbatim |
| Hold-out window [2025-07-01, 2026-04-21] virgin per Anti-Article-IV Guard #3 UNMOVABLE | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` line 153 + `_holdout_lock.py` R10-pinned + `assert_holdout_safe` 5-call-site enforcement per `docs/qa/gates/T002.0g-riven-cosign.md` §6 |
| `costed_out_edge` sub-classification within bucket B strategy_edge envelope (Mira Round 2 nuance) | Mira F2-T5 §1 + §5.2 four-cell evidence matrix + §6.5 final classification + Riven post-mortem §1.2 envelope verbatim |
| 3-bucket dependency tree {4a HARNESS_PASS ∧ 4b GATE_4_PASS ∧ paper-mode PAPER_AUDIT_PASS} required for Gate 5 | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 dependency tree + ESC-011 R5/R6 verbatim |
| Single-leg fire = automatic REJECT | Same post-mortem §3.2 + ESC-011 R5/R6 |
| §11.5 capital-ramp cumulative pre-conditions §1..§7 | Same post-mortem §3 + §4.4 + §6 + Riven persona checklists `before_new_strategy_live` + `before_trade` |
| Quarter-Kelly cap 0.25 × f* REGRA ABSOLUTA | Riven persona expertise.sizing_framework.quarter_kelly_default + Kelly 1956 + Thorp 2006 §III + Lopez de Prado 2018 AFML §15-16 |
| Riven haircut 30-50% first ~3 months live | Riven persona expertise.sizing_framework.haircut_initial verbatim |
| OOS budget one-shot property | Bailey-LdP 2014 §3 + López de Prado 2018 AFML §11-12 (CPCV methodology) + Bailey-Borwein-Lopez de Prado 2014 (PBO methodology) — combined: OOS evaluation contamination on observation; hold-out-virgin lock per Mira spec PRR-20260421-1 + Anti-Article-IV Guard #3 |
| Pessimistic Riven prior P(strategy survives OOS deployable) ≈ 0.10-0.15 | Industry baseline (López de Prado AFML §1 quant-research conversion-rate intuition); Riven persona backstory 2020 trauma; Riven persona communication "em dúvida, reduzo" |
| Anti-pattern §5.1, §5.2, §5.7, §5.8, §5.9 verbatim | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §5.1-§5.9 verbatim |
| ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome + §2 consolidated 20 conditions verbatim |
| Mira F2-T5 verdict supersedes Round 1 via append-only revision discipline | Mira spec v1.1.0 §15 amendment scope; Mira F2-T5 frontmatter `supersedes:` field |
| Riven F2-T6 reclassification authority post Mira F2-T5 | Mira spec v1.1.0 §12.1 sign-off chain row F2-T6 + ESC-011 R7 + R20 |
| Pax @po forward-research authority ESC-011 R10 | ESC-011 resolution §2.3 R10 verbatim |
| Sable governance review advisory only (no veto over Riven custodial) | agent-authority matrix per `.claude/rules/agent-authority.md` (Riven domain authority over risk perimeter; Sable framework authority — non-overlapping) |

### §7.1 Article IV self-audit verdict

Every clause in §1-§6 traces to a verifiable source. NO INVENTION (no fabricated probability, no fabricated EV calculation — Riven priors §1.2 P(a) ≈ 0.85 / P(b) ≈ 0.15 are EXPLICITLY DISCLOSED as Riven persona pessimistic priors per §5.1, NOT empirical measurements; reader can re-evaluate under different priors). NO threshold relaxation (K1 strict bar 0.95 applied AS-IS; quarter-Kelly cap 0.25 applied AS-IS). NO pre-emption of Mira F2-T5 statistical authority (Mira F2-T5 verdict is INPUT to this ballot, not output). NO pre-emption of Pax @po forward-research authority (Path C selection is risk-side adjudication; final forward-research direction selection — which specific H_next hypothesis to pursue — is Pax authority post-ESC-012 resolution). NO source-code modification (this ballot is write-only at council-document layer; no code mutation; no spec yaml mutation; no spec markdown mutation; no hold-out touch; no Round 1/Round 2 sign-off mutation). NO push (Article II → Gage @devops EXCLUSIVE; Riven authoring this ballot does NOT push — council resolution + post-resolution doc updates routed through Pax/Gage downstream).

### §7.2 Anti-Article-IV Guards self-audit (8 guards verbatim)

| Guard | Mandate | THIS ballot reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | THIS ballot does NOT authorize new impl; ESC-012 resolution may trigger code changes (e.g., epic status update, post-mortem appendix) but those are gated through Pax + Quinn + Gage standard chain, NOT Riven authoring |
| **#2** | NO engine config mutation at runtime | THIS ballot does NOT touch engine config |
| **#3** | NO touch hold-out lock | THIS ballot EXPLICITLY PRESERVES hold-out virgin status per §6.5 C5 condition; Path C does NOT consume OOS budget |
| **#4** | Gate 4 thresholds UNMOVABLE | THIS ballot APPLIES K1 strict bar AS-IS; vote rationale §1.2 Leg 1 PRESERVES UNMOVABLE per ESC-011 R14 |
| **#5** | NO subsample backtest run | THIS ballot does NOT authorize partial-window evaluation |
| **#6** | NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH | THIS ballot CONFIRMS Gate 5 LOCKED post Round 2; Path C does NOT pre-disarm Gate 5 |
| **#7** | NO push (Gage @devops EXCLUSIVE) | THIS ballot is local-only artifact; council ratification + Gage push gate downstream per Pax/Gage standard chain |
| **#8** | Verdict-issuing protocol — `*_status` provenance + `InvalidVerdictReport` raise on `K_FAIL` with `*_status != 'computed'` | THIS ballot is NOT a verdict-issuing artifact at the Mira F2-T5 layer; it is a council ballot at the ESC-012 layer; Guard #8 is referenced as Round 2 input verbatim, NOT mutated |

All eight Anti-Article-IV Guards honored verbatim by THIS ballot. Mira F2-T5 Guard #8 NEW endorsement preserved as input.

---

## §8 Riven cosign 2026-04-30 BRT — ESC-012 strategy-fate ballot

```
Author: Riven (@risk-manager) — Risk Manager & Capital Gatekeeper authority
Council: ESC-012 — T002 strategy-fate adjudication (Path A' refinement vs Path B Phase G OOS unlock vs Path C retire T002)
Constraint binding: Path A cost-reduction R&D OFF (council pre-resolved); slippage + costs FIXOS já conservadores
Authority basis: ESC-011 R7 + R20 + Mira Gate 4b spec v1.1.0 §12.1 sign-off chain row F2-T6 (Riven 3-bucket reclassification authority post Mira F2-T5) + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp custodial monopoly

Verdict: PATH_C_RETIRE_T002

Rationale summary (3-leg risk-side argument):
  Leg 1 — Foreclosure invariance under K1 strict bar UNMOVABLE (Anti-Article-IV Guard #4 / ESC-011 R14): Round 2 DSR=0.766987 strict FAIL by 0.183 below 0.95; refinement / OOS unlock cannot lift without cost-reduction R&D (OFF per council pre-resolution).
  Leg 2 — Path A' Bonferroni budget consumption + multiple-testing inflation: refinement re-uses in-sample window; n_trials inflates strict bar; squad bandwidth burned without bypassing Phase G.
  Leg 3 — Path B OOS budget economics one-shot: spending Phase G hold-out (~85% Riven prior on cost-erosion-preserves under regime stationarity ⇒ DSR_OOS < 0.95) on costed_out path is INFORMATION-poor allocation; OOS budget best preserved for H_next hypothesis deployment.

Convergent verdict: Path C is custodially cleanest from quarter-Kelly REGRA ABSOLUTA preservation, §11.5 capital-ramp pre-conditions integrity, Gate 5 fence preservation, and Anti-Article-IV Guard #4 K1-strict-UNMOVABLE protection.

Personal preference disclosed §5: Riven prefers Path C openly; preference grounded in pessimistic-by-default custodial prior + 2020 trauma anchor + REGRA ABSOLUTA "em dúvida, reduzo".

Recommended conditions if council adopts Path C (§6 C1..C12): documentation conditions C1-C4 (Round 3 post-mortem entry + §5.10 anti-pattern + §9 HOLD #2 update + EPIC-T002.0 status); OOS budget custodial C5-C6 (hold-out virgin preserved + Bonferroni n=5 monotonic carry-forward); squad bandwidth + governance C7-C8 (free bandwidth + engineering infrastructure preserved); custodial fence C9-C11 (Riven veto + anti-pattern catalog + ESC-011 cumulative); Sable advisory C12.

Counterfactuals openly disclosed §5.4 (vote conditional on: cost-reduction OFF; observed DSR=0.767 not striking-distance; single-shot OOS budget; refinement consuming current OOS budget). If any counterfactual condition flips, vote is openly re-evaluable.

Article II preservation: NO push performed by Riven during this ballot authoring. Gage @devops authority preserved for any subsequent commit.
Article IV preservation: every clause traces (§7); no invention; no threshold mutation; no source-code modification; no spec yaml mutation; no hold-out touch; no Mira F2-T5 verdict pre-emption; no Pax @po forward-research authority pre-emption; Riven priors §1.2 disclosed openly as persona pessimistic priors NOT empirical measurements.

Anti-Article-IV Guards self-audit §7.2: #1-#7 honored verbatim + Guard #8 NEW Mira F2-T5 endorsement preserved as input (THIS ballot is not a verdict-issuing artifact at Mira F2-T5 layer; it is a council ballot at ESC-012 layer).

Authority boundary: Riven authors THIS ballot from risk-perimeter perspective only. Mira retains Gate 4b verdict-issuing authority (executed Round 2). Pax retains forward-research direction authority post-ESC-012 (which specific H_next hypothesis to pursue). Gage retains push authority. Tiago retains execution authority. Quinn retains QA authority. Aria retains architecture authority. Beckett retains backtester authority.

Pre-vote independence statement: Riven authored THIS ballot WITHOUT consulting peer voter ballots (Mira / Pax / Aria / Beckett ESC-012 votes). Independence preserved per council protocol. Inputs consulted: Mira F2-T5 Round 2 verdict + Beckett N7-prime full report + Riven post-mortem (own authoring) + Riven cosign §9 HOLD #2 (own authoring). NO peer-ballot reading pre-vote.

Cosign: Riven @risk-manager 2026-04-30 BRT — ESC-012 strategy-fate ballot (PATH_C_RETIRE_T002 with conditions §6).
```

— Riven, guardando o caixa 🛡️
