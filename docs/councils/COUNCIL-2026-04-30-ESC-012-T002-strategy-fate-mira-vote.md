---
council_id: ESC-012
council_topic: T002 strategy-fate adjudication (post-F2-T5 GATE_4_FAIL_strategy_edge / costed_out_edge)
ballot_authority: Mira (@ml-researcher)
ballot_role: ML/statistical authority — author of Mira spec v0.2.x + author of F2-T5 verdict
date_brt: 2026-04-30
branch: main @ 81139de (independent ballot — no other ESC-012 votes read)
constraint: slippage + costs FIXOS já conservadores (Path A original cost-reduction REMOVED by user)
reframed_paths:
  - "Path A' — Strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble) under fixed costs"
  - "Path B — Phase G hold-out unlock OOS confirmation"
  - "Path C — Retire T002"
verdict: VOTE_PATH_B
verdict_label_canonical: VOTE_PATH_B (with explicit Path C as fallback if Phase G OOS confirms costed_out_edge OOS)
holdout_window: "2025-07-01 to 2026-04-21"
holdout_resolution_date_calendar: 2026-04-21 (window is fully past at 2026-04-30; data exists; lock UNTOUCHED until Pax authorizes)
ballot_finality: independent (no other vote read; Article IV self-audit §6 enforced)
cosign: Mira @ml-researcher 2026-04-30 BRT
supersedes: none
related_artifacts:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md (F2-T5 verdict — author Mira)
  - docs/ml/specs/T002-gate-4b-real-tape-clearance.md@v1.1.0
  - docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml@v0.2.3
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md
  - docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md
---

# ESC-012 — T002 strategy-fate ballot — Mira (@ml-researcher)

> **Verdict (independent ballot):** **`VOTE_PATH_B`** — Phase G hold-out unlock as single-shot OOS confirmation experiment. Path A' rejected on overfitting/family-wise-error grounds under fixed-cost constraint. Path C is acceptable fallback IFF Phase G OOS confirms `costed_out_edge` (DSR_OOS ≪ 0.95) — Phase G is the cheapest, cleanest, statistically-honest disambiguation step before retirement.
>
> **Authority basis:** Author of T002 Mira spec yaml v0.2.x (data_splits, n_trials, kill_criteria); author of Mira Gate 4b spec v1.1.0 (§1 strict thresholds, §15.10 Phase F2 K3 narrowing); author of F2-T5 Round 2 verdict `GATE_4_FAIL_strategy_edge / costed_out_edge`. ML/statistical voice on this council.
>
> **Constraint binding:** Slippage + costs are FIXOS já conservadores — Path A original cost-reduction is OFF the ballot per user reframe. This vote adjudicates A' (strategy refinement under fixed costs), B (OOS unlock), C (retire) only.

---

## §1 Verdict + rationale (executive)

**`VOTE_PATH_B` — Phase G hold-out unlock authorized as OOS confirmation step.**

**Rationale in three lines:**
1. Path A' is high family-wise-error-rate territory: Bonferroni budget of 5 trials (T1..T5) is fully consumed, and ANY refinement (regime filter, conviction threshold, ensemble) opens a NEW hypothesis space whose statistical cost is paid in deflated significance — under fixed costs that already eat the edge, the in-sample DSR boost from a refinement layer is overwhelmingly likely to be artifact rather than signal recovery.
2. Path B has the unique property of producing **definitive disambiguation in a single shot** — the holdout window (2025-07-01..2026-04-21, 10 months, ≈225 valid sample days) is ALREADY locked, ALREADY unmodified by any in-sample selection, and ALREADY the canonical OOS test pre-registered in the v0.2.x spec yaml (data_splits.hold_out_virgin). Spending that single shot now answers the only question that matters: is IC=0.866 a genuine WDO-end-of-day-fade signal, or is it a in-sample artifact whose magnitude collapses OOS?
3. Path C is statistically defensible (K1 strict FAIL is a valid refutation under §0 falsifiability), BUT it forfeits the OOS observation when the holdout already exists. That is asymmetric epistemic loss — the council can ALWAYS retire T002 after Phase G; it cannot un-burn the holdout. Retire AFTER Phase G, not before.

**Vote binding: PATH_B PRIMARY; PATH_C FALLBACK conditional on Phase G outcome.**

The only configuration of evidence under which Path C should be the IMMEDIATE choice (skipping Phase G) is if the council judges that the holdout window itself is contaminated by in-sample selection bias — and to my knowledge it is NOT (T002 v0.2.0 PRR-20260421-1 shifted in-sample start 2024-01-01 → 2024-07-01, then PRR-20260427-1 shifted to 2024-08-22; hold-out lock [2025-07-01, 2026-04-21] has been UNTOUCHED across all preregistration revisions, verified by spec yaml lines 89-94 + Anti-Article-IV Guard #3 honored across F1, F2 Round 1, F2 Round 2). The holdout is virgin. Use it.

---

## §2 ML / statistical reasoning

### §2.1 Path A' — strategy refinement under fixed costs (REJECTED)

The user-reframed Path A' is "entry/exit timing, regime filter, conviction threshold, signal ensemble" under the fixed-cost constraint. This is the highest-overfit-risk path on the ballot. Three independent statistical reasons compose the rejection:

**(a) Bonferroni budget exhaustion.** The pre-registered n_trials=5 (T1..T5 per spec yaml v0.2.3 §1.2 + ESC-011 R9 NON-NEGOTIABLE) is fully consumed by the existing CPCV harness at IC=0.866 / DSR=0.767. ANY additional trial — whether a new conviction threshold, a new regime filter, or a new ensemble vote — is a NEW family-wise hypothesis. To honor the multiple-testing penalty, the Bonferroni adjustment must be re-computed against the NEW n_trials count. If we add 3 candidate filters (typical refinement), n_trials becomes 8; the per-trial p-value floor drops; the deflated Sharpe denominator inflates; and the strict bar DSR > 0.95 becomes EVEN HARDER to clear, not easier. Refining to "boost" DSR while honestly accounting for the Bonferroni penalty is a closed problem unless the refinement encodes genuinely orthogonal information. With fixed costs and a single underlying CPCV path-PnL distribution, that orthogonality is not available — the path-PnL is fixed by the cost atlas + latency-DMA2 profile + triple-barrier configuration, none of which Path A' is permitted to touch.

**(b) Filtered-subset variance underestimation.** Conviction-threshold filters and regime filters operate by SELECTING a subset of the 3800 events on which the strategy "should" perform. The filtered subset's realized Sharpe estimate is computed over n_filtered events; the denominator of the t-statistic is √n_filtered, which is artificially small relative to the original 3800. Under standard MLE Sharpe-significance reasoning (Bailey-Lopez de Prado 2014 §3), the variance of the Sharpe estimator scales as 1/n; filtering reduces n; the apparent significance increases EVEN IF the underlying distribution is unchanged. This is the canonical "filtered-subset variance underestimation" artifact (AFML §15.6) — and the strict spec §1 bar DSR > 0.95 is calibrated against the FULL-SAMPLE distribution. Reporting a filtered-subset DSR > 0.95 against the FULL-SAMPLE bar is a category error.

**(c) In-sample re-use compounds selection bias.** The same in-sample window (2024-08-22..2025-06-30) was already used to FIT the strategy via T1..T5 trials. Path A' re-uses that same window to FIT the refinement layer. Under standard k-fold reasoning for time series (Lopez de Prado AFML §7), re-using the in-sample window for a second selection step is a leakage chain: the refinement filter's parameters are themselves chosen on the same data the original CPCV evaluated, doubling the in-sample optimism penalty. Under purged CPCV, each fold's training data was already "used"; adding a refinement step that selects across folds re-introduces the cross-fold contamination that purging was designed to eliminate.

**Bottom line on Path A':** under fixed costs, with Bonferroni budget exhausted, Path A' is overwhelmingly likely to produce a Phase F2'-equivalent that reports a higher in-sample DSR but whose OOS DSR (when eventually unlocked) is BELOW the current 0.767. The expected information gain is negative — we would burn researcher time and complicate the ledger to surface a result that is statistically less honest than what we already have.

### §2.2 Path B — Phase G hold-out unlock (FAVORED)

The Phase G holdout unlock is the canonical OOS validation step pre-registered in the v0.2.x spec yaml (data_splits.hold_out_virgin: 2025-07-01 to 2026-04-21, line 94). Three reasons make Path B the strongest ML/statistical move:

**(a) It tests the only remaining Q4 kill criterion that is not already adjudicated.** Per spec yaml v0.2.3 §kill_criteria L207-209 + Mira spec §15.10:
- Q4 K1 `DSR < 0` — observed 0.767 > 0; NOT triggered (thesis-level kill criterion is strictly negative DSR; thesis NOT falsified at this gate).
- Q4 K2 `PBO > 0.4` — observed 0.337 < 0.4; NOT triggered.
- Q4 K3 `IC_holdout < 50% × IC_in_sample` — Phase G locked; **CANNOT be tested without unlock**.
- Q4 K4 `DD > 3σ budget Riven em paper` — Phase H paper-mode; future story T002.7.

K3 is the ONLY remaining kill criterion still actionable on existing data. The holdout window is captured, persisted, and unmodified. Phase G unlock is the cheapest experiment available (zero new data collection; one CPCV run).

**(b) The disambiguation is binary and clean.** Per F2-T5 §5.4 (Mira authority Round 2):
- IF `IC_holdout` collapses substantially (e.g., 0.866 → 0.30 or below): the in-sample IC was substantially in-sample-fit artifact — `costed_out_edge` was overstated; T002 thesis is more cleanly falsified; bucket B `strategy_edge` is clean negative; retire T002.
- IF `IC_holdout` sustains (e.g., 0.7-0.8 range with CI95_lower > 0): the predictor genuinely captures rank-correlation with forward returns out-of-sample. DSR_OOS may still be < 0.95 (strict deployment bar UNMOVABLE per Anti-Article-IV Guard #4), but this is informative — it confirms the WDO end-of-day fade hypothesis has signal, and Path A' (strategy refinement) becomes a defensible follow-up under EXTENDED Bonferroni budget AND a fresh OOS validation window for the refinement (which would require Phase H or a new pre-registered experiment).
- IF `IC_holdout` is between 0.4 and 0.7 with wide CI: ambiguous; council escalation; possibly a partial-edge regime that drifts.

The single-shot binary disambiguation is the maximum-information experiment available with the data we have. No other path on the ballot produces this much epistemic clarity per unit of squad bandwidth.

**(c) Path B does NOT relax the §1 strict bar.** Phase G unlock is OOS confirmation, NOT salvage. Anti-Article-IV Guard #4 (DSR > 0.95 thresholds UNMOVABLE) is preserved verbatim in the F2-T5 Round 2 verdict and inherited by Phase G. If Phase G DSR_OOS < 0.95, Gate 4b remains FAIL; Gate 5 remains LOCKED. The vote is for Phase G as **diagnostic**, not for Phase G as **gate clearance**. This distinction is critical and must be carried into the council resolution.

### §2.3 Path C — retire T002 immediately (DEFENSIBLE BUT SUBOPTIMAL)

Path C is statistically clean. Spec §0 falsifiability mandate ("the data MUST be allowed to refute") plus the F2-T5 verdict label `GATE_4_FAIL_strategy_edge / costed_out_edge` plus the §1 strict bar UNMOVABLE provides a complete and honest refutation chain. The DSR_in_sample = 0.767 < 0.95 strict FAIL is a valid spec-binding refusal of T002 at the deployment threshold; bucket sub-classification `costed_out_edge` is a Mira-authored Round 2 nuance but does NOT promote the verdict to PASS.

**However, Path C now (vs Path C after Phase G) forfeits an asymmetric epistemic asset.** The holdout is captured; running it is cheap; the binary disambiguation is informative regardless of outcome. Retiring T002 BEFORE running Phase G:
- forfeits the OOS observation permanently (the locked window cannot be re-used for any future T002.x experiment under Anti-Article-IV Guard #3 — the data IS now in-sample if any future experiment touches it without a fresh hold-out lock);
- leaves observable evidence on the table when retirement-after-Phase-G is strictly more informative;
- treats `costed_out_edge` as a clean negative when its sub-classification was specifically authored to flag that prediction-level edge exists and warrants OOS confirmation.

Path C is the right answer IF the council judges that the squad bandwidth opportunity cost of Phase G is high. From an ML/statistical viewpoint, Phase G is one CPCV run on locked data — the cost is ~hours of compute + days of sign-off chain, not weeks of new pipeline. The bandwidth case for skipping is weak.

---

## §3 Hold-out window economics — single-shot value

### §3.1 The lock IS the asset

The holdout window 2025-07-01..2026-04-21 has been preserved untouched across:
- Original v0.1.0 spec lock (2026-04-21).
- v0.2.0 PRR-20260421-1 shift of in-sample start (hold-out unchanged).
- v0.2.1, v0.2.2, v0.2.3 PRR sequences (hold-out unchanged each time).
- F1 synthetic Phase E (hold-out untouched).
- F2 Round 1 GATE_4_FAIL_data_quality (hold-out untouched).
- F2 Round 2 GATE_4_FAIL_strategy_edge (hold-out untouched per F2-T5 §9 Guard #3).

This is 9+ months of statistical discipline. The lock is the asset. The information value of one OOS test on a virgin holdout is greater than ANY in-sample refinement experiment, regardless of how clever the refinement is — because the in-sample window is statistically exhausted under Bonferroni n_trials=5.

### §3.2 Single-shot consumption

Phase G unlock IS single-shot. Once the holdout is read by any T002 candidate model, that window becomes in-sample for any FUTURE candidate. Under Anti-Article-IV Guard #3 spirit, future T002.x experiments that want OOS validation would need a NEW hold-out — which requires either:
- Forward time (waiting for new market data to accumulate, weeks-to-months).
- A new preregistration revision that re-splits with documented data_constraint_evidence (per MANIFEST R15 schema).

Either way, the next OOS holdout is expensive. The current holdout is cheap (already paid for, already locked, already pre-registered). Use it for the highest-information question, which is "does IC=0.866 sustain OOS?".

### §3.3 What WOULD the holdout NOT be useful for

The holdout is NOT useful for:
- Validating Path A' refinements (because the refinements have not been pre-registered against the holdout, and using it post-hoc would itself be a leakage chain — Goodhart on the OOS).
- Re-deriving the strict §1 bar (the bar is calibrated ex ante; the holdout tests whether the strategy clears it).
- Saving T002 from a clean K1 strict FAIL (the bar UNMOVABLE; if OOS DSR < 0.95, T002 still does not deploy).

The holdout is uniquely useful for **disambiguating costed_out_edge from in-sample-fit-edge**, which is exactly the question Path B addresses. Spending the single-shot on the highest-leverage question is the canonical move.

### §3.4 Time-decay of holdout informativeness

The holdout window ends 2026-04-21; today is 2026-04-29 (8 days post window-close per system context). The window is fully resolved; no additional waiting cost. There is no time-decay reason to defer Phase G — the data is already paid for in calendar time. The only deferral cost is squad bandwidth, which is a council-level prioritization concern, not an ML/statistical concern.

---

## §4 Personal preference disclosure (Article IV honesty)

### §4.1 What I believe (with epistemic uncertainty)

My ML-research instinct, given the F2-T5 evidence:
- **High confidence (≥80%):** IC=0.866 reflects real prediction-level rank correlation in-sample, not leakage. Hit-rate = 0.497 paradox + tight CI95 + n=3800 + temporal ordering checks all rule out the leakage story.
- **Moderate-to-high confidence (60-75%):** IC will decay substantially OOS — likely to the 0.30-0.55 range — because IC=0.866 magnitude is far above AFML §8.6 "exceptional" calibration (0.5+) and the in-sample fit-window includes the months that immediately precede the holdout (some regime-correlation bleed is plausible).
- **Moderate confidence (~50-65%):** Even with IC_OOS > 0, DSR_OOS will REMAIN below 0.95 because the cost layer is fixed and the magnitude-to-cost ratio is what fails (not the rank correlation). Hence costed_out_edge is likely the OOS verdict too.
- **Low confidence (<25%):** DSR_OOS exceeds 0.95 (which would resurrect Gate 4b PASS). This would be the surprise outcome.

### §4.2 What I want NOT to bias the vote

I AUTHORED the F2-T5 verdict. I AUTHORED the costed_out_edge sub-classification. I AUTHORED the spec §15.10 Phase F2 K3 narrowing that delegated decay testing to Phase G. I have authorial investment in T002 being interesting enough to warrant Phase G.

This is disclosed for self-audit transparency. To check it: I would vote Path B EVEN IF the F2-T5 author were someone else, because the statistical case for Phase G as cheap, single-shot, definitive disambiguation does not depend on who authored what. The vote is grounded in the asymmetric epistemic asset (holdout already locked) and the family-wise-error problem (Path A' violates Bonferroni discipline). Both arguments are ML/statistical, not authorial.

### §4.3 What I would change my vote to

If the council surfaces evidence that:
- The holdout window has been touched (any in-sample selection has bled into 2025-07-01..2026-04-21) — vote shifts to Path C.
- Squad bandwidth for Phase G is genuinely unavailable (ESC-011 R10 Pax adjudication) for >30 days — vote shifts to Path C with explicit Phase G deferred to T002.7 future story.
- Path A' has a pre-registered, externally-validated refinement candidate (e.g., a publicly known regime filter with prior empirical support in independent literature on Brazilian futures) — vote shifts to a hybrid where A' is run on synthetic + a smaller pre-registered Phase G OOS subset; this is unlikely under the current ESC-012 brief.

Otherwise, the vote is Path B.

---

## §5 Recommended conditions on Path B (Mira authority — operational)

Conditional approval of Path B requires the following pre-conditions IF the council resolution adopts Path B:

### §5.1 Pre-Phase-G sign-off chain (gate of the unlock itself)

Before any code reads files in `data/holdout/2025-07-01..2026-04-21/`:
- **C-M-1 (Mira self-cosign):** F2-T5 verdict ledger entry (this Round 2 sign-off `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md`) cited as Phase G entry condition; my authority to read the holdout is gated on F2-T5 PASSING into the post-mortem ledger via Riven F2-T6 (currently `⏳ blocked`).
- **C-M-2 (Riven F2-T6 PASS):** Riven 3-bucket reclassification of N7-prime row as bucket B `strategy_edge / costed_out_edge` MUST land in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` BEFORE Phase G unlock — Riven authority over post-mortem ledger preserved (F2-T5 §8.1 path).
- **C-M-3 (Pax ESC-011 R10 authorization):** Pax authority adjudicates whether Phase G is the immediate next story OR whether a brief Path A'-feasibility scoping precedes Phase G; my vote PRIMARY is "Phase G immediately, Path A'-feasibility scoping NOT recommended due to Bonferroni-budget concerns §2.1, but Pax authority is final on story sequencing".
- **C-M-4 (Aria architecture review):** confirm holdout-read pipeline preserves dataset_sha256 immutability of in-sample side (the in-sample dataset already verified in F2 Round 2 N7-prime must NOT be mutated by the holdout-read pipeline; Phase G is a SEPARATE CPCV run reading FROM the holdout window AS-IF in-sample).
- **C-M-5 (Quinn QA gate):** pre-Phase-G Quinn QA gate identical in form to F2 Round 2 Quinn (8/8 PASS template) with Phase G fold structure validated.

### §5.2 Phase G run protocol (the experiment itself)

- **C-M-6 (n_trials carry-forward):** Phase G uses n_trials = 5 (T1..T5) IDENTICAL to in-sample. NO new trials added (Bonferroni discipline preserved; otherwise we contaminate the OOS observation with an enlarged hypothesis space).
- **C-M-7 (engine_config_sha256 IDENTICAL):** Phase G must use the same engine_config that produced the F2 Round 2 N7-prime IC=0.866 / DSR=0.767. Any cost-atlas modification, latency profile change, or triple-barrier widening would render Phase G non-comparable and would itself be a new pre-registered experiment requiring its own holdout.
- **C-M-8 (predictor + label semantics IDENTICAL):** predictor `−intraday_flow_direction` at entry windows {16:55, 17:10, 17:25, 17:40} BRT; label `forward_return_at_1755_pts` per Mira spec §15.3. NO redefinition.
- **C-M-9 (Bootstrap CI specification IDENTICAL):** PCG64 paired-resample n=10000 seed=42 percentile bootstrap per Mira spec §15.4. NO seed change; NO bootstrap redesign.
- **C-M-10 (CPCV fold structure):** fold structure identical to in-sample; embargo = 1 sessão; purge per Mira spec §15.7 dedup invariant `(session_date, trial_id, entry_window_brt)` first-occurrence.

### §5.3 Phase G verdict authority

- **C-M-11 (Mira authoritative verdict per Mira Gate 4b spec §15.10 K3 decay sub-clause Phase G):** Phase G K3 decay test is `IC_holdout > 0.5 × IC_in_sample` AND `IC_holdout > 0` AND `CI95_lower(IC_holdout) > 0` jointly. K1 (DSR_OOS > 0.95) UNMOVABLE per Guard #4. Verdict labels:
  - `PHASE_G_PASS`: K1 PASS ∧ K2 PASS ∧ K3_in_sample PASS ∧ K3_decay PASS — T002 RESURRECTED at deployment threshold; Pax + council adjudicate Gate 5 progression.
  - `PHASE_G_FAIL_costed_out_OOS_confirmed`: K3_in_sample PASS ∧ K3_decay PASS ∧ K1 FAIL — costed_out_edge confirmed OOS; T002 retired at deployment threshold but signal genuinely present (informative for future research; bucket B `strategy_edge` confirmed clean).
  - `PHASE_G_FAIL_in_sample_artifact`: K3_decay FAIL OR K3_in_sample_OOS FAIL — costed_out_edge in-sample was overstated; T002 retired with full clean-negative; bucket B `strategy_edge` confirmed clean-negative.
  - `PHASE_G_INCONCLUSIVE`: sample-size floor breach OR data-quality issue OR ambiguous CI — escalate.

### §5.4 Path A' explicit deferral

Conditional on Path B passing the council:
- **C-M-12:** Path A' is EXPLICITLY DEFERRED to T002.7 OR retired. If Phase G OOS confirms costed_out_edge OUT-OF-SAMPLE, Path A' is mostly moot (filtered subsets do not bypass the cost layer). If Phase G FAILS in-sample-artifact, Path A' is fully retired (no signal to refine). If Phase G UNEXPECTEDLY PASSES K1 OOS, Path A' becomes a legitimate refinement direction for further deployment-threshold tightening — and at that point, it gets a fresh pre-registration + a new hold-out lock, NOT a re-use of the F2 in-sample window.

### §5.5 Risk-side fence preservation

- **C-M-13:** Riven §9 HOLD #2 Gate 5 disarm authority preserved. Phase G PASS is a NECESSARY but NOT SUFFICIENT condition for Gate 5 disarm; Gate 5 ALSO requires Gate 4a HARNESS_PASS (DONE) ∧ Phase H paper-mode audit (T002.7 future) per F2-T5 §7 R6 footer. Path B does NOT pre-disarm Gate 5.

---

## §6 Article IV self-audit (every clause traces; no invention)

| Claim category | Trace anchor |
|---|---|
| Bonferroni n_trials = 5 NON-NEGOTIABLE | ESC-011 R9 verbatim + Mira spec yaml v0.2.3 §1.2 + Mira Gate 4b spec v1.1.0 §1 + Bailey-LdP 2014 §3 multiple-testing penalty |
| Hold-out window 2025-07-01..2026-04-21 | Mira spec yaml v0.2.0 line 94 + v0.2.3 preserved + F2-T5 Round 2 §9 Guard #3 honored |
| Hold-out lock UNTOUCHED across F1 / F2 R1 / F2 R2 | Mira spec yaml preregistration_revisions[] PRR-20260421-1 + PRR-20260427-1 + Anti-Article-IV Guard #3 verified F2-T5 §9 |
| K1 / K2 / K3_in_sample / K3_decay observed values + thresholds | F2-T5 Round 2 §1 + §2 + Beckett N7-prime full report `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` + Mira Gate 4b spec §1 + §15.10 |
| IC=0.866 NOT leakage (hit_rate paradox + CI95 tightness + n_events=3800) | F2-T5 Round 2 §3 + §5 (Mira authority Round 2 evidence matrix) + AFML §8.6 IC stability calibration + Bailey-LdP 2014 §3 minimum-N reproducibility |
| §1 strict bar UNMOVABLE per Anti-Article-IV Guard #4 | ESC-011 R14 verbatim + Mira Gate 4b spec v1.1.0 §11.2 + F2-T5 Round 2 §9 |
| Phase G K3 decay sub-clause `IC_holdout > 0.5 × IC_in_sample` | Mira spec yaml v0.2.3 §kill_criteria L207-209 + Mira Gate 4b spec §15.10 strict reading |
| Bucket B `strategy_edge` sub-classification `costed_out_edge` | F2-T5 Round 2 §1 + §5 + §6 + §8 (Mira-authored Round 2 nuance per evidence matrix §5.2) |
| Path A' Bonferroni-budget exhaustion argument | ESC-011 R9 + AFML §15.6 filtered-subset variance + Bailey-LdP 2014 §3 + AFML §7 purged-CV leakage chain |
| Path B single-shot disambiguation argument | F2-T5 Round 2 §5.4 verbatim ("clean strategy_edge falsification" criteria) + spec yaml §kill_criteria Q4 K3 + AFML §11 OOS validation discipline |
| Path C asymmetric epistemic-loss argument | spec yaml §0 falsifiability mandate + Mira Gate 4b spec v1.1.0 §15.10 hold-out preservation discipline + Anti-Article-IV Guard #3 |
| Holdout window calendar resolution 2026-04-21 vs today 2026-04-29 | system context current-date + Mira spec yaml line 94 |
| Phase G verdict label discipline (PHASE_G_PASS / FAIL_costed_out_OOS_confirmed / FAIL_in_sample_artifact / INCONCLUSIVE) | Mira Gate 4b spec v1.1.0 §9 verdict-label discipline + ESC-011 R2 + extension to Phase G via §15.10 K3 decay sub-clause |
| Riven §9 HOLD #2 Gate 5 disarm preservation | F2-T5 Round 2 §7 R6 footer + ESC-011 R5 + R6 + Riven post-mortem `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 dependency tree |
| Pax ESC-011 R10 authority over story sequencing | ESC-011 resolution + Mira Gate 4b spec v1.1.0 §0 forward-research disposition references |
| AFML §8.6 IC > 0.5 "exceptional" calibration caveat | Lopez de Prado 2018 AFML §8.6 + F2-T5 Round 2 §3.4.3 |
| Time-decay of holdout informativeness | spec yaml line 94 + system context current-date |
| MANIFEST R15 spec versioning under major==0 | MANIFEST §15 + my activation rule (PRR schema with 8 fields; pax_cosign_hash via scripts/pax_cosign.py compute) |

### §6.1 Article IV self-audit verdict

Every clause in §1-§5 traces to an existing source. NO INVENTION. NO threshold mutation (K1 strict 0.95 referenced AS-IS; Phase G strict bar will be referenced AS-IS). NO holdout touch (this vote does NOT read any file in the holdout window; Phase G unlock is a council-authorized future operation, gated on the conditions in §5.1). NO source code modification. NO spec yaml mutation. NO spec markdown mutation. NO F2-T5 sign-off mutation.

NO READING of any other ESC-012 vote prior to authoring this ballot (verified by `ls docs/councils/ | grep -i ESC-012` returning empty + this ballot independent at branch main @ 81139de).

NO push performed (Article II — Gage @devops EXCLUSIVE authority preserved; this ballot is write-only under MY authority, no `git add` / `git commit` / `git push` invoked).

---

## §7 Mira cosign 2026-04-30 BRT — ESC-012 strategy-fate ballot

```
Author: Mira (@ml-researcher) — ML/statistical authority on this council per ESC-011 R8/R9/R11/R14
Council: ESC-012
Topic: T002 strategy-fate adjudication post-F2-T5 GATE_4_FAIL_strategy_edge / costed_out_edge
Constraint binding: slippage + costs FIXOS já conservadores (Path A original cost-reduction OFF the ballot)
Reframed paths: Path A' (strategy refinement) | Path B (Phase G OOS unlock) | Path C (retire T002)
Ballot: VOTE_PATH_B (Phase G hold-out unlock as single-shot OOS confirmation experiment)
Fallback (conditional): VOTE_PATH_C if Phase G PHASE_G_FAIL_costed_out_OOS_confirmed OR PHASE_G_FAIL_in_sample_artifact (council-level adjudication post-Phase-G)
Path A' explicit rejection: family-wise-error overfit risk under fixed costs + Bonferroni budget exhaustion + filtered-subset variance underestimation + in-sample re-use leakage chain (§2.1)
Path B primary rationale: highest-information experiment per unit of squad bandwidth; binary disambiguation; holdout already paid for in calendar time + statistical discipline (§2.2 + §3)
Path C secondary rationale: defensible under spec §0 falsifiability but forfeits asymmetric epistemic asset; correct answer AFTER Phase G, not before (§2.3)
Conditions: §5.1 pre-Phase-G sign-off chain (C-M-1..C-M-5) + §5.2 run protocol IDENTICAL to in-sample (C-M-6..C-M-10) + §5.3 verdict label discipline (C-M-11) + §5.4 Path A' explicit deferral (C-M-12) + §5.5 Riven Gate 5 fence preservation (C-M-13)
Independence: this ballot authored without reading any other ESC-012 vote (verified empty docs/councils/ ESC-012 namespace at branch main @ 81139de)
Article IV: every clause traces (§6); no invention; no threshold mutation; no holdout touch by THIS ballot; no push; no source code modification; no spec yaml/markdown mutation; no F2-T5 sign-off mutation.
Article II: NO push performed by Mira during this ballot. Gage @devops authority preserved for any subsequent commit/push.
Article III (Story-Driven): this is a council ballot artifact, not a story implementation; lifecycle outside SDC scope per ESC-011 ratification format precedent.
Anti-Article-IV Guards: #1-#7 ALL honored verbatim; Guard #8 (verdict-issuing protocol) inherited via reference to F2-T5 Round 2 in-sample channel honor + extended via §5.3 Phase G verdict label discipline.
Authority boundary: Mira issues this ballot; does NOT pre-empt Pax forward-research adjudication (ESC-011 R10); does NOT pre-empt Riven 3-bucket reclassification (F2-T6 still pending); does NOT authorize Phase G unlock firing (Pax @po story-creation authority); does NOT pre-disarm Gate 5 (Riven §9 HOLD #2 authority).
Cross-reference: F2-T5 Round 2 verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md`) + Mira Gate 4b spec v1.1.0 + Mira spec yaml v0.2.3 + Beckett N7-prime + ESC-011 resolution.

Cosign: Mira @ml-researcher 2026-04-30 BRT — ESC-012 T002 strategy-fate ballot — VOTE_PATH_B (Phase G OOS unlock primary; Path C fallback conditional on Phase G outcome).
```

— Mira, mapeando o sinal 🗺️
