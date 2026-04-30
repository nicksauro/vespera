---
council_id: ESC-012
title: T002 Strategy-Fate Adjudication — Kira Independent Ballot
voter: Kira (@quant-researcher)
date_brt: 2026-04-30
ballot_round: independent (pre-aggregation)
context_constraint: "User-imposed: slippage + costs FIXED, ALREADY CONSERVATIVE. Path A original (cost reduction) OFF-TABLE."
paths_under_vote:
  - id: A_prime
    label: Strategy refinement (regime filter / conviction threshold / signal ensemble / hold-window tightening)
  - id: B
    label: Phase G hold-out unlock OOS confirmation
  - id: C
    label: Retire T002 per spec §0 falsifiability
verdict: APPROVE_PATH_B
verdict_secondary_acceptable: APPROVE_PATH_C
verdict_rejected: APPROVE_PATH_A_PRIME
authority_basis: |
  ESC-011 R8/R11 — Kira quant-researcher peer-review authority on Gate 4b interpretation;
  spec §0 falsifiability mandate adjudication;
  Anti-Article-IV Guard #4 thresholds UNMOVABLE custodian;
  Bonferroni multiple-testing budget custodian (Bailey-LdP 2014 §3).
independence_disclosed: |
  This ballot was drafted WITHOUT reading any other ESC-012 voter's artifact
  (Article IV independence). Inputs read: Round 2 closure memory, Mira F2-T5
  authoritative verdict, Beckett N7-prime report, Mira spec amended v1.1.0,
  original thesis, spec yaml v0.2.3, Riven post-mortem §5.9 anti-pattern.
  No peer ballots referenced.
---

# ESC-012 — T002 Strategy-Fate Adjudication: Kira Independent Ballot

> **Voter:** Kira (@quant-researcher) — Senior Quantitative Researcher, Scientific Lead
> **Date (BRT):** 2026-04-30
> **Constraint received:** User authority forecloses Path A original (no cost / slippage reduction). Reframed paths: A' (strategy refinement under fixed costs), B (hold-out unlock OOS), C (retirement per §0).
> **Verdict:** **APPROVE_PATH_B** — Phase G hold-out unlock for OOS confirmation, with PRE-COMMITTED disposition rule that ties OOS evidence to T002 retirement vs cost-research-redirect, eliminating any post-hoc rescue ambiguity.
> **Authority chain:** ESC-011 R8 + R11 + R14 + Anti-Article-IV Guard #4 + spec §0 falsifiability mandate + Bonferroni n_trials=5 budget custodianship.

---

## §1 Verdict — APPROVE_PATH_B (with secondary acceptance of Path C)

**Primary verdict:** APPROVE_PATH_B — unlock hold-out 2025-07-01..2026-04-21, run identical pipeline (same spec hash, same engine config, same cost atlas, same n_trials=5), report IC_holdout, DSR_holdout, PBO_holdout, hit_rate_holdout, and the K3 decay statistic `IC_holdout / IC_in_sample`. **PRE-REGISTER the disposition rule BEFORE running** to eliminate post-hoc rescue.

**Rationale (5 lines, condensed):**

1. **Path A' is statistical malpractice under the strict reading of our own framework.** Bonferroni n_trials=5 budget is consumed (T1..T5 verbatim per spec §1.2 + ESC-009 + ESC-010). Adding regime filter / conviction threshold / signal ensemble / hold-window tightening expands the family-wise hypothesis space MID-EXPERIMENT, requiring NEW Bonferroni corrections that the spec was not pre-registered to absorb. Running A' on the SAME in-sample window 2024-08-22..2025-06-30 is **textbook in-sample re-fit / p-hacking via threshold tuning** — and Round 2 has zero remaining hold-out capital to validate it without burning the only OOS asset we hold.
2. **Path B is the single most informative experiment we can run with the assets we have.** The hold-out has been pre-registered locked since 2026-04-21 (gate Phase A signature §11 of the original thesis). It was reserved EXACTLY for the moment of K3 verdict. That moment is now. Using it for A'-validation BEFORE pre-committing the disposition rule converts it into an in-sample extension; using it for B with a pre-registered disposition preserves its scientific value.
3. **IC=0.866 is unprecedented territory** (AFML §8.6: IC>0.5 is exceptional; 0.866 is far above) and demands an OOS test before any conclusion — positive OR negative — about T002. Retiring T002 today (Path C) without burning the OOS opportunity discards a measurement that costs us nothing additional to obtain and may change the bucket attribution from `costed_out_edge` to `in_sample_artifact` (decisive negative) or `cost_eroded_real_edge` (informative for future cost-research even if cost work is currently off-table per user constraint).
4. **DSR>0.95 strict bar remains UNMOVABLE.** Path B is NOT a salvage path under K1 strict. It is a falsifiability extension: if OOS IC drops below 0.5 × IC_in_sample (K3 decay test, the original Q4 kill criterion), T002 hypothesis is **fully falsified** per spec §0 + thesis §5 K3 + Mira §5.4. If OOS IC holds, the strategy is `cost_eroded_real_edge` and gets formally retired with a CLEAN refutation under K1 strict — not a partial / ambiguous one.
5. **Path C is acceptable as fallback** if council judges Path B operationally too expensive (e.g., 3h wall × N reruns, Beckett bandwidth, telemetry constraints) OR if user authority decides the marginal information value of OOS is below the marginal cost of squad capacity. But Path C is strictly inferior on information: it forecloses the K3 decay measurement that spec §5 K3 was authored to enable.

**Path A' is REJECTED.** No conditions. See §2 for the multiple-testing audit.

---

## §2 Multiple-testing budget audit — why Path A' is statistical malpractice

### §2.1 Bonferroni n_trials=5 is fully consumed

Per spec yaml v0.2.3 §n_trials.total=5 + §n_trials.bonferroni_adjusted_p_value=0.002 (= 0.01 / 5):

| Trial | Pre-registered params (spec yaml L407-421) | Status post N7-prime |
|---|---|---|
| T1 | baseline (4 windows, P60 threshold, ATR [P20,P80] regime, lookback 126d) | CONSUMED (run + reported) |
| T2 | threshold P50 | CONSUMED |
| T3 | threshold P70 | CONSUMED |
| T4 | no regime filter | CONSUMED |
| T5 | only 17:25 window | CONSUMED |

The Bonferroni budget is **exhausted** at the family-wise level the spec was pre-registered for. Per Bailey-LdP 2014 §3 (selection-bias correction) + Harvey-Liu-Zhu 2016 (multiple-hypothesis adjustment in finance research): adding any new hypothesis to the family AFTER seeing the data is **post-hoc selection** and requires a new pre-registration (new spec version) AND a new corrected p-value.

### §2.2 Path A' explicit hypothesis-space expansion

Path A' as proposed enumerates:

- **Entry/exit timing optimization** (e.g., narrow entry windows from {16:55, 17:10, 17:25, 17:40} to a single window OR shift to alternative timestamps)
- **Regime filter** (skip rollover D-3..D-1, Copom days, high-vol regime — note Copom + rollover ALREADY excluded per spec yaml universe block; this proposal ADDS more filters)
- **Conviction threshold** (top-decile predictor only — i.e., further percentile threshold tightening from P60 to P90)
- **Signal ensemble** (combine T1..T5 trials into a meta-strategy — this is a NEW trial T6 by definition)
- **Position hold window tightening** (e.g., 1.0×ATR PT instead of 1.5× — this is a triple-barrier parameter mutation, NOT a free parameter under the original spec)

**Each of these is a NEW trial** in the multiple-testing accounting sense. If the council adopts A' with N additional refinements, the corrected p-value becomes `0.01 / (5 + N)`, which for N=5 (one per refinement above) yields `0.001` — far stricter than the original `0.002`. **Note:** if A' is adopted with SOME refinements only (e.g., 2-3 of the 5 above), the corrected p-value is correspondingly less strict than 0.001 but still stricter than the pre-registered 0.002. **Either way, the new threshold cannot be applied retroactively to the existing T1..T5 trial set without re-running the entire CPCV with new pre-registered hypotheses.** Doing so converts the analysis from confirmatory to exploratory, and the DSR threshold 0.95 (already pre-Bonferroni-adjusted at the Bailey-LdP level) becomes mechanically un-clearable without a parallel adjustment to the Deflated Sharpe formula's `n_trials` parameter (Bailey-LdP 2014 eq. 7).

### §2.3 Re-using same in-sample window 2024-08-22..2025-06-30

Path A' refinement cannot be validated on the in-sample window without recomputing IC and DSR over the same data the parameter selection was performed on. This is the **canonical in-sample-fit** anti-pattern (López de Prado 2018 AFML §1.5: "tuning parameters on data is overfitting; tuning hyperparameters on the same data validation is double-overfitting"). The DSR formula's selection-bias correction does NOT cover this — Bailey-LdP DSR is calibrated for a single trial-multiplicity penalty, not for sequential refinement on the same fold structure.

### §2.4 Hold-out lock UNTOUCHED constraint precludes A' OOS validation in same epic

Per spec yaml §data_splits + Anti-Article-IV Guard #3 (Mira §11.2 row 3, Beckett N7-prime §9 row 3): hold-out 2025-07-01..2026-04-21 is locked until Phase G unlock authorization. ESC-012 has not authorized hold-out unlock under Path A' (and SHOULD NOT — see §3 below). Therefore Path A' would have to be validated on yet ANOTHER source of OOS evidence — which we do not have.

The post-2026-04-21 forward window is NOT a substitute: (a) it is partially live-data territory (real-time WDO), exposing the strategy to current-regime contamination; (b) any forward window is short relative to the 10-month hold-out reservation; (c) under autonomous mode constraints, sourcing additional historical data is gated by Dara coverage audit and is unrelated to this ESC.

### §2.5 Anti-pattern §5.9 explicit invocation

Per Riven post-mortem §5.9 anti-pattern catalog (NEW 2026-04-30): the canonical `costed_out_edge` signature (IC > 0 strong, CI95_lower > 0, hit_rate ≈ 0.5, DSR finite-positive < strict bar) admits THREE forward paths: **cost-reduction R&D** (forbidden by user constraint), **Phase G OOS confirmation** (= Path B), **retirement** (= Path C). Path A' (refinement-on-same-in-sample) is **NOT** in the §5.9 admissible list because it would commit anti-pattern §5.1 ("single-leg promotion") AND §5.4 ("post-hoc threshold tuning") simultaneously. Riven custodial veto authority would fire on a sign-off attempting it. Kira concurs Round 2: **Path A' is rejected at the framework level, not just the council level.**

### §2.6 Verdict §2

**Path A' is statistical malpractice under the strict reading of our own framework.** Bonferroni budget exhausted; in-sample re-fit; hold-out lock precludes legitimate OOS validation in same epic; Riven §5.9 admissible list excludes it. **REJECT.**

---

## §3 OOS integrity argument — Path B legitimate use of hold-out

### §3.1 Pre-registration is intact

Per thesis §11 gate Phase A signature 2026-04-21T17:30:00 BRT: hold-out window 2025-07-01..2026-04-21 was pre-registered as the SOLE OOS validation asset for T002, decided BEFORE any in-sample data analysis. Per the original thesis Q4 kill criterion K3: "IC hold-out (2025-07→2026-04) < 50% do IC in-sample → descartar (efeito arbitrado/regime-dependente)". The hold-out exists for EXACTLY this measurement.

### §3.2 OOS measurement value

The K3 decay test computes `IC_holdout / IC_in_sample`. Under Path B with IC_in_sample = 0.866:

| OOS scenario | Measurement | T002 disposition |
|---|---|---|
| IC_holdout ≥ 0.5 × IC_in_sample = 0.433 | K3 decay PASS | Confirms in-sample edge is OOS-stable. Strategy is `cost_eroded_real_edge` per Mira §5.2 — predictor has real rank-correlation power that survives 10-month OOS. T002 still cannot deploy under K1 strict (DSR_holdout would also need >0.95) but the predictor knowledge becomes a CITABLE finding for future research (different thesis, different exit logic, different cost regime). |
| IC_holdout < 0.5 × IC_in_sample | K3 decay FAIL | Confirms in-sample artifact. T002 fully falsified per spec §0 + thesis K3 + Mira §5.4 ("clean negative evidence would require K3 to also fail honestly"). Bucket B reclassified `clean_negative_strategy_edge`; T002 retired with CLEAN refutation. |
| IC_holdout ≈ 0 with CI95 spanning 0 | K3 inconclusive | Predictor has no OOS power. T002 retired; partial regime-dependence interpretation possible if Riven taxonomy refinement Round 3 admits it. |

All three scenarios produce a **decisive disposition** for T002. Path B is NOT a stalling tactic — it is a single-experiment K3 measurement with a 10-month sample size that resolves the `costed_out_edge` ambiguity definitively.

### §3.3 OOS integrity is preserved by pre-committing disposition rule

The risk with Path B is that we run OOS, then post-hoc rationalize the result toward whatever next-step we were already inclined toward. To eliminate this:

**MANDATORY: BEFORE running the Phase G unlock, the council must pre-commit a disposition rule (§6 conditions C-K1..C-K6 below) and freeze it in the ESC-012 resolution document with hash signatures.** Once frozen, the OOS run is mechanical: the disposition follows the rule with zero post-hoc adjudication.

Mira §5.4 framing applies: "clean negative evidence would require K3 to also fail honestly". If we run OOS and IC_holdout = 0.43 (just below the 0.5 × IC_in_sample threshold), the disposition rule must say `K3 FAIL → retire` — NOT `K3 borderline → debate further`. Pre-commitment is the only protection.

### §3.4 DSR strict bar UNMOVABLE preservation

Path B does NOT relax the DSR > 0.95 K1 strict bar. Even if OOS confirms IC = 0.866 with full statistical power, DSR_holdout would need to also exceed 0.95 to clear Gate 4b — which is unlikely given DSR_in_sample = 0.767 and the 10-month OOS window has the SAME cost atlas / SAME slippage / SAME triple-barrier (per user constraint these are fixed). Therefore Path B B-class outcome (best case) is `cost_eroded_real_edge` evidence with K1 still failing strict — formal Gate 4b PASS remains foreclosed. This is FINE: Path B's purpose is not Gate 4b PASS rescue; it is K3 disposition and clean falsification.

### §3.5 Anti-Article-IV Guard #3 ratification post-Path-B

Once Phase G hold-out is unlocked under Path B, Guard #3 ("NO touch hold-out lock") is operationally consumed. Future Gate 4b iterations (e.g., a hypothetical T002.bis with new cost regime under user-future-permission) would need to source a NEW hold-out window from data post-2026-04-21 — which we currently do not have at scale. **This is irreversible.** The council should accept Path B with full awareness that the hold-out is a one-shot resource. This reinforces the case for pre-committing the disposition rule (§3.3): if we burn the only OOS asset, we must extract maximum information value from the single measurement.

### §3.6 Verdict §3

Path B is **legitimate use** of the pre-registered hold-out. It IS the experiment for which the hold-out was reserved. Pre-committed disposition rule (§6) preserves OOS integrity. Burning the hold-out is irreversible — but its purpose is to be burned EXACTLY at this gate, with this hypothesis under test.

---

## §4 Falsifiability argument — Path C strict reading

### §4.1 Spec §0 strict reading

Per spec yaml falsifiability mandate (§0 carry-forward from thesis Q2): "the data MUST be allowed to refute". Per Mira §1 K1 strict reading: DSR=0.767 < 0.95 already constitutes K1 strict FAIL; Anti-Article-IV Guard #4 mandates K1 UNMOVABLE; therefore Gate 4b is FAILED at the deployment gate level; therefore T002 cannot proceed to Phase G/H deployment chain regardless of K3 evidence.

Under this strict reading, **Path C (retirement) is the textbook outcome**: refutation has fired; the squad capacity is best redirected; T002.6 closes Done; epic T002 deprecated.

### §4.2 Why Path C is acceptable (secondary verdict)

If council judges that:

1. The marginal information value of the K3 decay measurement is below the marginal cost of:
   - Beckett squad bandwidth (3h wall per run; multiple runs may be needed for diagnostic edge cases)
   - Sable + Quinn re-audit chain at the Phase G transition
   - Riven §9 HOLD #2 Gate 5 disarm ledger update overhead
2. The user has expressed preference for capacity redirect over diagnostic completion
3. The squad is already saturated and a clean Path C closure unblocks novel alpha hypothesis research

…then Path C is acceptable as a clean strict-§0 outcome. The cost of Path C is informational: we lose the ability to distinguish `cost_eroded_real_edge` from `in_sample_artifact` for the partial-edge story, which means future research on similar hypothesis structures (intraday inventory unwind in other instruments / regimes) cannot cite T002 evidence as either supportive or refuting.

### §4.3 Why Path B preserves strict-§0 compatibility

A common confusion: Path B may LOOK like a salvage path. It is NOT. Under Path B with pre-committed disposition rule:

- IF OOS confirms IC: T002 still retires under K1 strict (DSR > 0.95 unmet); the K3 PASS just adds a secondary informational finding about predictor stability.
- IF OOS refutes IC: T002 retires with K1 + K3 BOTH failing — strongest possible falsification chain.
- IF OOS is inconclusive: T002 retires under K1 strict + K3 inconclusive — equivalent to Path C with marginal extra evidence.

**Under all three OOS outcomes, T002 retires.** Path B is therefore strict-§0 compatible: it does not alter the K1 verdict. It only adds K3 disposition information that is otherwise lost forever (since the hold-out cannot be queried later post-retirement without reopening the epic — which is itself a §0 violation if attempted post-hoc).

### §4.4 Verdict §4

**Path C is strict-§0 correct** and acceptable as secondary verdict. **Path B is strict-§0 superior** because it generates the K3 measurement before final retirement, at the cost of one Phase G unlock (which is the unlock the hold-out was reserved for) and Beckett bandwidth (~3h wall). Kira recommends B over C if council bandwidth admits, with C as fallback if it does not.

---

## §5 Personal scientific preference vs council authority — disclosure

**Personal preference:** Path B with pre-committed disposition rule. Kira would run Phase G unlock before retiring T002 because the K3 measurement is the ONLY remaining piece of evidence the spec §0 framework was designed to extract, and discarding it before extraction violates the spirit (though not the letter) of the falsifiability mandate.

**Concession:** I recognize that the squad-capacity argument for Path C is real. If user authority determines that:
- The 10-month OOS measurement is not worth ~3-6h Beckett bandwidth + Sable/Quinn audit chain
- Squad capacity should redirect to novel hypothesis exploration immediately
- T002 closure as a clean strict-§0 retirement is the priority

…then Path C is acceptable and I do not dissent. But absent that explicit user prioritization, Path B is the scientifically superior choice.

**Divergence statement:** Kira's vote (B with C secondary) may diverge from peers who weight squad capacity heavier or who interpret the strict §0 reading as foreclosing Phase G unlock outright. Both are defensible positions; I do not pre-empt them. I disclose my preference for transparency per Article IV.

**Anti-bias declaration:** I have not read any other ESC-012 ballot before drafting this. I have read the Round 2 closure memory, Mira F2-T5 verdict, Beckett N7-prime report, Mira spec v1.1.0 (§1, §15.10, §11.2), original thesis (§5 K3 + §11 gate signature), spec yaml v0.2.3 (§n_trials, §data_splits, §kill_criteria), and Riven post-mortem §5.9 anti-pattern. No peer ballot influence.

---

## §6 Recommended conditions if council adopts Path B

If council aggregates to APPROVE_PATH_B, Kira mandates the following conditions BEFORE Phase G unlock fires:

### §6.1 Pre-committed disposition rule (MANDATORY — must be hash-frozen in ESC-012 resolution doc)

- **C-K1 (decisive OOS PASS):** IF `IC_holdout ≥ 0.5 × IC_in_sample = 0.433` AND `IC_holdout_CI95_lower > 0` THEN K3 PASS; T002 disposition = `retire_with_cost_eroded_real_edge_finding` (citable for future research; T002.6 closes Done; epic T002 deprecated). Rationale: K1 strict still FAILS regardless; no Gate 4b PASS rescue.
- **C-K2 (decisive OOS FAIL):** IF `IC_holdout < 0.5 × IC_in_sample` OR `IC_holdout_CI95_lower ≤ 0` THEN K3 FAIL; T002 disposition = `retire_with_clean_negative_strategy_edge` (full thesis falsification per spec §0 + Mira §5.4). T002.6 closes Done; epic T002 deprecated.
- **C-K3 (inconclusive OOS):** IF `IC_holdout` measurement chain has data-quality flags (sample size shortfall, parquet coverage gap, Quinn QA fail) THEN K3 INCONCLUSIVE; T002 disposition = `retire_under_K1_strict_with_K3_data_quality_addendum`. Same retirement; logged distinctly.
- **C-K4 (no other dispositions admissible):** the disposition rule is EXHAUSTIVE. No "ESC-013 reopen for further refinement" / "extend hold-out window" / "adopt Path A' post-hoc". The disposition is mechanical post-OOS.

### §6.2 OOS run constraints

- **C-R1:** Same spec yaml v0.2.3 (UNMOVED). Same `engine_config_sha256 = ccfb575a…`. Same `cost_atlas_sha256 = bbe1ddf7…`. Same `cpcv_config_sha256 = d2ea61f2…`. Same n_trials=5 (T1..T5 pre-registered; NO T6 added). Same triple-barrier (PT=1.5×ATR_hora; SL=1.0×ATR_hora; vertical 17:55 BRT). Same entry windows {16:55, 17:10, 17:25, 17:40}.
- **C-R2:** Hold-out window 2025-07-01..2026-04-21 unlocked at full extent (no sub-window selection — that would be selection bias).
- **C-R3:** Beckett N8 (suggested label) report follows the same N7-prime structure (§3 events metadata, §4 IC pipeline measurement validity, §5 distribution diagnostics, §9 8-guard self-audit). Reproducibility receipt 9/9 fields.
- **C-R4:** Mira issues F3-T5 OOS clearance verdict using the §6.1 disposition rule mechanically. NO post-hoc threshold relaxation. Anti-Article-IV Guard #4 preserved.
- **C-R5:** Riven F3-T6 reclassifies the OOS row in post-mortem §2 ledger per Mira F3-T5 verdict.
- **C-R6:** Quinn QA gate validates the Phase G run pre-Beckett: no source modification (Phase G unlock is pure data path expansion); engine config UNCHANGED; spec yaml UNMOVED.

### §6.3 Article IV self-audit gates

- **C-A1:** All N7-prime Anti-Article-IV Guards #1-#8 preserved verbatim Phase G. No new guard relaxation. Guard #3 (hold-out lock) is consumed by definition (this IS the unlock event); it transitions from `intact` to `consumed_for_T002_terminal_OOS`. Future Gate 4b iterations on different theses would require a NEW hold-out reservation from non-overlapping data.
- **C-A2:** ESC-012 resolution doc hashes the disposition rule §6.1 BEFORE Beckett N8 fires. The resolution doc cannot be edited post-OOS without explicit ESC-013 reopening (which itself would be a §0 violation absent a NEW hypothesis).

### §6.4 Wall-time and capacity bound

- **C-W1:** Beckett N8 wall-time budget capped at ~6h (2× N7-prime envelope, since OOS may have different latency profile under Phase G data paths; conservative bound). If exceeded, escalate to ESC-013 and DO NOT extrapolate / retry under different parameters (would consume more multiple-testing budget).

### §6.5 Conditions if council adopts Path C instead

If council aggregates to APPROVE_PATH_C, Kira mandates:

- **C-C1:** T002.6 story formally closes Done with disposition = `retired_under_K1_strict_with_K3_OOS_unmeasured`. Rationale block in story file documents the council's choice to forgo K3 OOS measurement.
- **C-C2:** Hold-out 2025-07-01..2026-04-21 is FORMALLY released back to the data-asset pool, available for future hypothesis pre-registration. The hold-out is NOT consumed by Path C (it remains intact). This is Path C's ONE advantage over Path B — preserves OOS asset for novel hypothesis.
- **C-C3:** Riven §9 HOLD #2 Gate 5 disarm ledger appends T002 retirement entry; Gate 5 remains LOCKED because Gate 4b never PASSED.
- **C-C4:** Squad redirect to novel alpha hypothesis kicks off via @analyst (Alex) literature review + Kira *hypothesize cycle on a fresh thesis. Bonferroni budget resets at the new spec yaml level (zero shared trials with T002).

### §6.6 Conditions REJECTED if council attempts Path A'

If council attempts to aggregate to APPROVE_PATH_A_PRIME (which Kira opposes), Kira mandates:

- **C-X1:** Path A' would require a NEW spec yaml version (v0.3.0 minimum, breaking change), with NEW pre-registered n_trials list (T1..T(5+N) where N = number of refinements), NEW Bonferroni-adjusted p-value, and NEW pre-registered hold-out window from data NOT YET COLLECTED (post-2026-04-21 forward window with sufficient duration TBD).
- **C-X2:** Hold-out 2025-07-01..2026-04-21 CANNOT be used for A' validation under Anti-Article-IV Guard #3 + spec §11 thesis pre-registration discipline. Using it would be a §0 falsifiability violation.
- **C-X3:** Riven custodial veto per post-mortem §5.9 admissible list would fire. Path A' is NOT in the §5.9 admissible forward-paths set. **Council adoption of A' would require explicit override of Riven custodial authority** — which Kira does not endorse.
- **C-X4:** Kira would dissent and escalate to user authority if council adopts A' over the §C-X1..C-X3 objections.

---

## §7 Article IV self-audit — source anchor table

Every claim in §1-§6 traces to a verifiable source. NO INVENTION.

| Claim | Source anchor |
|---|---|
| DSR=0.767, IC=0.866, CI95 [0.865, 0.866], PBO=0.337, hit_rate=0.497 (Round 2 measurement) | Mira F2-T5 verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §1, §2 threshold table) + Beckett N7-prime report (`docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §1, §3.1, §6.1) |
| Bonferroni n_trials=5 fully consumed (T1..T5 pre-registered) | Spec yaml v0.2.3 §n_trials.total=5 + §n_trials.variants L407-421 + thesis §5 N_trials block + ESC-009 6/6 + ESC-010 6/6 ratification |
| K1 strict bar UNMOVABLE (DSR>0.95) | Spec yaml v0.2.3 §kill_criteria.k1_dsr L207 + Mira spec v1.1.0 §1 K1 row + Anti-Article-IV Guard #4 + ESC-011 R14 |
| Hold-out window 2025-07-01..2026-04-21 pre-registered locked | Spec yaml v0.2.3 §data_splits.hold_out_virgin L94 + thesis §5 K3 + thesis §11 gate signature 2026-04-21T17:30:00 BRT + Anti-Article-IV Guard #3 |
| K3 decay test definition (`IC_holdout < 50% IC_in_sample`) | Thesis §5 K3 kill criterion + spec yaml v0.2.3 §kill_criteria.k3_ic |
| Path A' = statistical malpractice (in-sample re-fit + p-hacking) | López de Prado 2018 AFML §1.5 (anti-overfitting discipline) + Bailey-LdP 2014 §3 (selection-bias correction) + Harvey-Liu-Zhu 2016 (multiple-hypothesis adjustment) + Riven post-mortem §5.9 admissible list (does NOT include refinement-on-same-IS) |
| `costed_out_edge` admits 3 forward paths (cost-research / OOS / retire) | Riven post-mortem §5.9 anti-pattern catalog (Round 2 NEW 2026-04-30 BRT) + Mira F2-T5 §5.3 ("`costed_out_edge` admits...") |
| Path B preserves strict-§0 compatibility (T002 retires under all OOS scenarios) | Mira F2-T5 §5.4 ("clean negative evidence would require K3 to also fail honestly") + Anti-Article-IV Guard #4 (K1 strict UNMOVABLE) + thesis §5 K3 kill criterion structure |
| AFML §8.6 IC stability calibration (IC>0.5 exceptional) | Lopez de Prado 2018 AFML §8.6 |
| Article II push monopoly (Gage @devops EXCLUSIVE) — Kira does NOT push | Constitution Article II + Manifest R3 + agent-authority.md |

---

## §8 Kira cosign 2026-04-30 BRT

```
Voter: Kira (@quant-researcher) — Senior Quantitative Researcher, Scientific Lead
Council: ESC-012 — T002 strategy-fate adjudication post-PR #15 closure
Branch context: main @ 81139de (Round 2 closure merged; ESC-012 deliberation pre-aggregation)
Constraint received: User authority forecloses Path A original (cost reduction OFF). Reframed paths
                     A' (strategy refinement) / B (hold-out unlock OOS) / C (retire per §0).

Verdict: APPROVE_PATH_B (primary) — Phase G hold-out unlock for OOS confirmation,
         conditional on hash-frozen pre-committed disposition rule §6.1 (C-K1..C-K4)
         and §6.2..§6.4 OOS run + Article IV constraints.
Secondary acceptable: APPROVE_PATH_C (retire under strict §0) if council/user prioritize
                      squad capacity redirect over K3 disposition measurement.
Rejected: APPROVE_PATH_A_PRIME — statistical malpractice under strict reading of
          Bonferroni n_trials=5 budget custodianship + spec §11 pre-registration
          + Anti-Article-IV Guard #3 hold-out lock + Riven §5.9 admissible list.

Personal scientific preference: B over C (disclosed §5).
Article IV independence: ballot drafted without reading any other ESC-012 voter's artifact;
                         no peer ballot influence; sources cited §7 anchor table.
Article II preservation: NO push performed (Gage @devops EXCLUSIVE); NO commit;
                         NO threshold mutation; NO source code modification;
                         NO spec yaml mutation; NO hold-out touch (this ballot is
                         deliberation-layer only, pre-aggregation).
Anti-Article-IV Guards: #1-#7 preserved verbatim; #8 (verdict-issuing protocol)
                        not applicable to council ballot layer.

Quant-researcher authority basis: ESC-011 R8 + R11 + R14 peer-review;
                                  Bonferroni multiple-testing budget custodianship
                                  (Bailey-LdP 2014 §3); spec §0 falsifiability mandate
                                  adjudication; Anti-Article-IV Guard #4 thresholds
                                  UNMOVABLE custodian.

Scope OUT (explicit non-pre-emption):
  - Mira F3-T5 OOS verdict adjudication (Mira authority, post-Beckett-N8 if Path B adopted)
  - Riven F3-T6 reclassification (Riven authority, gated em Mira F3-T5)
  - Pax story-creation for T002.7 / T002 retirement closure (Pax authority)
  - Council aggregation outcome (orchestrator authority)
  - User authority final call between B and C secondary fallback

Cosign: Kira @quant-researcher 2026-04-30 BRT — ESC-012 strategy-fate independent ballot
        (autonomous mode; mini-council ballot stage).
```

— Kira, cientista do alpha 🔬
