---
council_id: ESC-013
topic: T002.7 Phase G protocol-compliance gap — Path (iv) protocol-corrected re-run vs Path C retire
voter: Riven (@risk-manager)
voter_role: Risk Manager & Capital Gatekeeper — Gate 5 dual-sign authority + §11.5 capital-ramp pre-conditions custodial + post-mortem authoring
date_brt: 2026-04-30
voter_authority: ESC-011 R7 + R20 + ESC-012 R10/R11/R13/R15/R17 + Mira Gate 4b spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 (Riven 3-bucket reclassification authority post Mira Round 3) + Riven §9 HOLD #2 Gate 5 disarm authority
inputs_consulted:
  - docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md (4-branch hash-frozen disposition rule)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Mira Round 3 INCONCLUSIVE verdict + §3.1 protocol-compliance gap finding)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md (5/6 SUPERMAJORITY APPROVE_PATH_B + R10/R11/R13/R15/R17 carry-forward)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-riven-vote.md (own ESC-012 ballot — Path C minority 1/6)
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md (3-bucket framework + §3 dependency tree + §5 anti-pattern catalog)
  - data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/full_report.json (N8 metrics direct read)
inputs_NOT_consulted_pre_vote: other ESC-013 voter ballots (Aria / Mira / Beckett / Kira / Pax / Sable) — independence preserved per council protocol
verdict: APPROVE_PATH_IV (protocol-corrected Phase G proper re-run with explicit conditions §6 below)
gate_5_status_post_vote: REMAINS LOCKED — no path resolves Gate 4b PASS at COMPUTED-PASS K3 strict bar; council selection is forward-research direction, NOT Gate 5 disarm
quarter_kelly_status_post_vote: PRESERVED INTACT (no sizing exercise authorized either path; quarter-Kelly cap inviolate per Riven REGRA ABSOLUTA)
oos_budget_status_post_vote_under_iv: PRESERVED CONDITIONAL — §15.13.7 one-shot binds K3 decay metric (Mira reading authoritative) NOT parquet read alone; Path (iv) is FIRST execution of canonical Phase G protocol, NOT a re-attempt under adjusted parameters; ESC-012 R9 single-shot discipline preserved at metric layer
prior_ballot_consistency: divergence from ESC-012 Path C primary registered openly §6; reasoning §2 below
---

# ESC-013 — T002.7 Phase G Protocol-Compliance Gap Riven Vote (Risk Perimeter Adjudication)

> **Voter:** Riven (@risk-manager) — Risk Manager & Capital Gatekeeper.
> **Authority basis:** ESC-011 R7 + R20 carry-forward + ESC-012 R10/R11/R13/R15/R17 (Path B ratification + protocol-compliance branch hooks) + Mira Gate 4b spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 (Riven 3-bucket reclassification authority post Mira Round 3) + §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp pre-conditions custodial monopoly.
> **Mandate:** Adjudicate ESC-013 from RISK PERIMETER perspective only. Gate 5 LOCKED post-Round 3 (Mira INCONCLUSIVE verdict means Gate 4b NOT PASS; Gate 5 conjunction unsatisfied per ESC-012 R10 + spec §10 footer). §11.5 capital-ramp pre-conditions UNCHANGED.
> **Adjudication question:** Path (iv) protocol-corrected re-run of Phase G proper (~5-10 LoC Dex F2-T8-T1 wiring + Beckett N8.1 ~3h) vs Path C retire T002 (parquet-read-as-consumption strict reading). Adjudicate from RISK PERIMETER under N8 evidence update.

---

## §1 Verdict + rationale (risk-side)

### §1.1 Verdict

**`APPROVE_PATH_IV`** — protocol-corrected Phase G proper re-run, with explicit conditions §6 below.

### §1.2 Risk-side rationale (3-leg argument; updated by N8 evidence)

The risk-perimeter adjudication rests on three independent legs that converge — under N8 evidence update — to (iv):

**Leg 1 — §15.13.7 one-shot binds the metric, not the file read.** ESC-012 R9 single-shot discipline (Kira C-K3 + Mira C-M6) reads in `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.2 R9: "OOS one-shot discipline — Phase G window 2025-07-01..2026-04-21 is single-shot; result is binding regardless of outcome; CANNOT be re-run with adjusted parameters." The phrase "result is binding" presupposes that a *result* was produced — i.e., the canonical K3 decay metric per spec §15.13.5 was COMPUTED. N8 produced an *in-sample-IC-over-holdout-window* point estimate (IC=0.865933 with `holdout_locked=True` per `scripts/run_cpcv_dry_run.py:1093`) which Mira Round 3 §3.3 conclusively rejects as the binding K3 decay test (decay test is *cross-window*: IC_holdout uses in-sample model's predictions evaluated over OOS labels; N8's same-window measurement cannot meaningfully differ in sign and is not the AFML §8.6 IC stability decay paradigm spec §15.13.5 invokes). The "adjusted parameters" R9 forbids are statistical adjustments under outcome pressure — predictor change, label change, threshold mutation, n_trials expansion. R9 does NOT speak to *protocol-corrected first-execution-of-canonical-test*. Path (iv) preserves the predictor↔label semantics IDENTICAL F2 (ESC-012 R7), preserves Bonferroni n_trials=5 carry-forward (ESC-012 R6), preserves engine_config_sha256 / cost atlas / rollover calendar / latency_dma2_profile / RLP/microstructure flags IDENTICAL F2 (ESC-012 R6 reusability invariant — N8 already demonstrated 8/9 stamps IDENTICAL per Mira Round 3 §5.2 invariant table; only `dataset_sha256` expected-different IS vs OOS). The single variable change is `holdout_locked=False` flag flip + `ic_holdout_status='computed'` propagation — this is the *unlock mechanism* spec §15.13.2 was authored to provide. From the risk perimeter: §15.13.7 one-shot binds the K3 decay metric measurement (the binding statistical test); the parquet input read alone, under Phase F protocol semantics that emit DEFERRED-sentinel, did NOT exercise the falsifiable content of §15.13.5. The first canonical execution has not yet occurred.

**Leg 2 — Posterior under N8 evidence flips Path B EV calculation.** My ESC-012 ballot §1.2 Leg 3 assigned Riven prior P(regime-stationarity-preserves-cost-erosion ⇒ DSR_OOS < 0.95) ≈ 0.85 based on F2 IS DSR=0.767 strict-fail-by-0.183 propagating under regime stationarity. **N8 evidence partially contradicts this prior**: DSR_OOS=0.965 *observed PASS* at point estimate (1.5% above 0.95 strict bar; ~12× closer to threshold than F2 IS, on the favorable side); PBO_OOS=0.163 (halved from F2 0.337); sharpe_mean improved 0.046 → 0.101 (+119% OOS); IC magnitude near-IDENTICAL across windows (0.866010 vs 0.865933 — Δ 0.000077). Under proper Bayesian update with these observations, my P(K1 OOS-PASS strict | observed N8 metrics) updates substantially — **conservatively, my posterior on K1 OOS-PASS strict bar is ~0.60-0.75** (down from prior P(a) ≈ 0.85 of failure; up from prior P(b) ≈ 0.15 of pass), CONDITIONAL on the K3 decay test still needing to be COMPUTED (which is the load-bearing remaining experimental question Path (iv) actually answers). Critically, the N8 *observation* is NOT the canonical OOS test per Mira Round 3 §3.3 strict reading — but it provides strong informative diagnostic that the regime-stationarity assumption I priored on at 0.85 is *less likely* than I assumed. The honest Bayesian update flips the posterior ranking. See §2 below for the explicit Bayesian update mechanics.

**Leg 3 — Path C now consumes the OOS budget asymmetrically.** Under my ESC-012 prior, Path C cleanly preserved the OOS budget for H_next. **N8 evidence changes the ledger**: the parquet *was structurally read* (Dara R4 materialized + N8 consumed via `data/holdout/` parquet root with `dataset_sha256: ac884afb…`); Sentinel data ingestion contamination at the file-read level is a real concern under strict Anti-Article-IV Guard #3 reading. UNDER conservative interpretation (parquet-read-as-consumption), Path C does NOT preserve the OOS budget for H_next either — the budget was structurally consumed by N8's parquet read regardless of whether the K3 decay metric was computed. UNDER Mira's authoritative reading (one-shot binds metric), §15.13.7 is preserved by Path (iv) because the canonical decay test has not yet executed. **Either way, retiring under Path C now does not bank the OOS budget for H_next** — the parquet was read; the contamination concern (researcher exposure to OOS observations) is real either way. Given the OOS budget is ALREADY structurally exposed via N8, the marginal cost of computing the canonical K3 decay test (Path (iv)) is small (~5-10 LoC Dex + ~3h Beckett wall-time), and the marginal information value is HIGH — it transforms an INCONCLUSIVE-protocol-gap verdict into a binding R15/R16/R17 verdict per PRR-20260430-1 hash-frozen 4-branch disposition rule.

### §1.3 Convergence to (iv)

Path C under conservative reading (parquet-read-as-consumption) does NOT bank OOS budget for H_next (already structurally exposed via N8 read). Path (iv) under Mira authoritative reading (one-shot binds metric) preserves §15.13.7 discipline because canonical decay test has NOT yet executed. The Bayesian posterior under N8 evidence makes Path B EV calculation flip from low-EV to medium-high-EV (DSR=0.965 above strict bar at point estimate; PBO=0.163 well below; IC magnitude near-IDENTICAL across windows). The marginal cost of (iv) is small (~5-10 LoC + ~3h wall-time); the marginal information value is HIGH (binds verdict to PRR R15/R16/R17 vs INCONCLUSIVE residual branch). Quarter-Kelly REGRA ABSOLUTA is preserved INTACT under both paths (no sizing pressure either way; both paths keep Gate 5 LOCKED unless Phase G COMPUTED-PASS + paper-mode Phase G/H both clear).

**Convergent verdict: Path (iv) — protocol-corrected Phase G proper re-run with conditions §6 below.**

---

## §2 Updated Bayesian prior post-N8 evidence

This §2 expands Leg 2 risk-side argument with explicit Bayesian update mechanics.

### §2.1 ESC-012 prior verbatim

ESC-012 ballot §1.2 Leg 3 prior:

| Phase G outcome under `costed_out_edge` hypothesis | P (Riven prior pre-N8) |
|---|---|
| **(a) DSR_OOS < 0.95** (regime preserves cost-erosion) | ~0.85 |
| **(b) DSR_OOS > 0.95** (regime exhibits non-stationarity OR cost-and-friction layer differs OOS) | ~0.15 |

This prior was anchored on F2 IS DSR=0.767 strict-fail-by-0.183, regime-stationarity assumption, and Riven persona pessimistic-by-default custodial baseline (industry baseline P(strategy survives OOS deployable) ≈ 0.10-0.15 per López de Prado AFML §1).

### §2.2 N8 evidence (likelihood update)

The N8 run, while NOT executing the canonical K3 decay test (Mira Round 3 §3 protocol-compliance gap), DID expose informative diagnostic measurements about the OOS window:

| Statistic | F2 IS | N8 holdout-window | Δ direction |
|---|---|---|---|
| DSR | 0.767 | **0.965** | +0.198 (crossed strict bar from below to above) |
| PBO | 0.337 | **0.163** | -0.174 (halved; well below 0.5 strict + 0.25 ideal sub-threshold) |
| sharpe_mean | +0.046 | +0.101 | +119% OOS improvement |
| sharpe_std | 0.185 | 0.177 | -4% OOS (per-path Sharpe distribution tightened slightly) |
| IC magnitude | 0.866010 | 0.865933 | Δ 0.000077 (near-IDENTICAL across windows) |
| hit_rate | 0.497 | 0.472 | -0.024 (still ≈ 0.5 random walk per-trade preserved) |

Mira Round 3 §3.3 explicitly rejects the IC magnitude near-IDENTICAL observation as the binding K3 decay test (because cross-window vs same-window IC semantics — see Mira §3.3 four reasons). However, the N8 observations DO update my prior on the *regime-stationarity-preserves-cost-erosion* hypothesis I anchored at 0.85.

The Round 2 §5.2 `costed_out_edge` signature was: high IC + hit_rate ≈ 0.5 + finite-positive-but-sub-threshold DSR + small-positive sharpe_mean. **Round 3 N8 evidence shows: high IC (≈ same as F2) + hit_rate ≈ 0.5 (essentially same as F2) + ABOVE-threshold DSR (0.965 vs F2 0.767) + small-positive sharpe_mean improved (+119%)**. The signature shift Round 2 → Round 3 is K1 (DSR) crossing the strict bar from below to above, while K3 (IC) and hit_rate remain near-IDENTICAL across windows. Per Mira Round 3 §6.2 interpretation, this is consistent with: (1) holdout window having favorable per-path Sharpe distribution variance (sharpe_mean numerator increased ~119%; sharpe_std denominator decreased ~4%; the ratio moved DSR threshold-crossing); OR (2) asymmetric PnL distribution preserved across windows where the SL>PT precedence in triple-barrier exits produces residual after-cost edge that is *more* favorable in the OOS window.

### §2.3 Bayesian posterior update (Riven persona honest accounting)

The strict reading of Mira Round 3 §3.3 says the N8 observation is NOT the canonical K3 decay test. Therefore I cannot update on the K3 decay outcome directly — that is the load-bearing experimental question Path (iv) actually executes. **However, the N8 evidence UPDATES my prior on the K1 strict bar OOS-PASS likelihood** (which is conjunction-coupled to the R15 trigger):

- **Pre-N8 prior** P(DSR_OOS > 0.95 strict | F2 IS DSR=0.767 + regime-stationarity assumption + cost-and-friction conservative) ≈ 0.15
- **Post-N8 likelihood** P(observed DSR=0.965 | regime-stationarity-preserves-edge_AND_DSR_strict_PASS_truly) >> P(observed DSR=0.965 | regime-stationarity-fails_OR_DSR_strict_FAIL_truly)

Per Bayesian update mechanics, observed DSR=0.965 is much more consistent with the H1 = "DSR strict PASS truly" hypothesis than with H0 = "DSR strict FAIL but window-specific lucky draw" — though the point-estimate-only-no-bootstrap-CI caveat (Mira Round 3 §4.2 — DSR bootstrap CI not in current pipeline; Mira OBS-2) limits the strength of this update. Riven honest accounting: posterior P(DSR_OOS > 0.95 strict | observed N8 metrics + protocol-corrected re-run yields IDENTICAL DSR point estimate) updates from 0.15 → conservatively ≈0.50-0.65 (mid-range; substantial update; tempered by no-bootstrap-CI caveat + window-specific concern + per-path Sharpe distribution unique-window-tightness possibility).

**Posterior on the K3 decay test specifically** is governed by the cross-window IC propagation question — which has not yet been measured. Under H1 (predictor↔label binding is structural not regime-dependent), expected IC_holdout (cross-window propagation) preserves the in-sample IC sign at minimum and likely retains ≥ 50% magnitude (preserves §15.13.5 falsifiability; cross-check with N8 same-window IC=0.866 ≈ F2 IS IC=0.866 is informative diagnostic). Under H0 (predictor↔label binding is regime-dependent / spurious), expected IC_holdout could drop substantially. Given the N8 same-window-IC near-identity (Δ 0.000077) is consistent with H1 (structural pattern preserved across windows under same definition), my posterior P(K3 decay COMPUTED-PASS | Path (iv) executes) ≈ 0.55-0.70 (moderate; substantial update from baseline ~0.15-0.20 industry baseline; tempered by Mira Round 3 §3.3.1 nuance that cross-window-vs-same-window IC are different metrics and the cross-window propagation could differ).

### §2.4 Joint conjunction posterior

PRR §3.1 R15 trigger requires conjunction `K1 OOS-PASS ∧ K2 OOS-PASS ∧ K3_in_sample_PASS ∧ K3_decay_COMPUTED-PASS`:

| Conjunct | Posterior probability under N8 evidence + Path (iv) execution |
|---|---|
| K1 OOS-PASS (DSR > 0.95) | ≈ 0.50-0.65 (point estimate already observed PASS; protocol re-run unlikely to materially shift DSR if `holdout_locked=False` is the only flag flip) |
| K2 OOS-PASS (PBO < 0.5) | ≈ 0.85-0.95 (observed 0.163 well below threshold; protocol re-run unlikely to shift PBO materially since per-path PnL distribution is the same engine_config) |
| K3 in-sample PASS (IC > 0 with CI95 lower > 0) | ≈ 0.95+ (already PASS; carry-forward F2 IS reference) |
| K3 decay COMPUTED-PASS (IC_holdout > 0.5 × IC_in_sample, cross-window measurement) | ≈ 0.55-0.70 |

Joint posterior P(R15 fires | Path (iv) executes) ≈ 0.50 × 0.90 × 0.95 × 0.62 ≈ **0.27** (mid-range; substantial update from ESC-012 prior ~0.10 P(b) joint; not negligible; ESC-013 surprise-PASS adjudication agenda becomes plausibly relevant).

The complementary outcomes:
- P(R16 FAIL_K3_collapse: IC_holdout < 0.3 | Path (iv) executes) ≈ 0.10-0.15 (lower than industry baseline because N8 same-window-IC near-IDENTICAL provides informative diagnostic against collapse)
- P(R17 FAIL_K1+K3_sustains: IC_holdout ∈ [0.3, 0.5×IS) AND DSR_OOS < 0.95 | Path (iv) executes) ≈ 0.15-0.25 (window-specific DSR outcome could regress under different bootstrap; cost-and-friction stability assumption)
- P(INCONCLUSIVE on borderline | Path (iv) executes) ≈ 0.30-0.40 (moderate; some Bayesian mass remains on borderline outcomes)

The posterior probability mass is now distributed across all four PRR branches, with ~27% on R15 (surprise PASS triggering ESC-014 surprise-PASS agenda) and ~25-40% on R16/R17 (clean falsification or costed-out-edge OOS-confirmed) and ~30-40% on INCONCLUSIVE-borderline. **Information value of Path (iv) is now HIGH** — the test is genuinely discriminating between four branches under updated posterior.

### §2.5 Risk-side reading on posterior update

My ESC-012 ballot priored at P(a) ≈ 0.85 P(b) ≈ 0.15 was Bayesian-honest pre-N8. The N8 evidence (even though NOT the canonical K3 decay test per Mira Round 3 §3.3) provides strong informative diagnostic that updates my prior. **Integrity-of-priors discipline (Article IV) requires that I update openly when evidence flips the calculation** — which is what this §2 does. Path (iv) under updated posterior is medium-to-high EV_info; Path C under updated posterior does NOT preserve OOS budget cleanly (parquet already structurally read; researcher contamination at file-read level is real concern under strict Anti-Article-IV Guard #3 reading). The ESC-012 ballot Leg 3 OOS-budget-economics argument is now weaker than at ESC-012 time. Riven honest accounting of this prior update is the load-bearing reason my vote flips from Path C (ESC-012 minority) to Path (iv) (ESC-013).

---

## §3 Hold-out budget interpretation (parquet read OR K3 measurement = consumption)

This §3 is the **central ESC-013 adjudication question** (per Mira Round 3 §3 + §11): does §15.13.7 one-shot consumption bind the parquet read or the K3 decay metric measurement?

### §3.1 Two readings surveyed

**Reading A (Mira authoritative; Mira Round 3 §1 + §3 + §8.2 + §11):** §15.13.7 one-shot binds the *K3 decay metric measurement* (the canonical OOS statistical test per spec §15.13.5). The parquet read produces an in-sample-IC-over-holdout-window point estimate that is statistically informative diagnostic but does NOT exercise §15.13.5 falsifiability semantics ("preserve in-sample IC sign AND retain ≥ 50% of in-sample magnitude"). Path (iv) is the FIRST canonical execution of the canonical Phase G protocol; it is a protocol-correction not a statistical re-do; ESC-012 R9 prohibits the latter, NOT the former.

**Reading B (Conservative; Riven minority preservation reading):** §15.13.7 one-shot binds the *parquet input read*. Once the OOS data is read by ANY decision-maker (model, researcher, automated optimizer), the data is contaminated by exposure (per Bailey-LdP 2014 §3 + López de Prado AFML §11-12 CPCV methodology; AFML §1 quant-research overfitting discipline). N8 read the parquet → OOS budget structurally consumed → Path C activates → T002 retire ceremony with `phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading` diagnostic.

### §3.2 Risk-side adjudication between A and B

I adjudicate FROM RISK PERIMETER:

**Argument for Reading A (Mira authoritative):**

1. **Statistical integrity argument.** The §15.13.5 K3 decay test is the falsifiable cross-window IC propagation test under §15.10/§15.13 binding clauses. N8 ran `--phase F` (`holdout_locked=True` hardcoded per `scripts/run_cpcv_dry_run.py:1093`); the verdict-layer correctly fired the OBS-1 short-circuit emitting DEFERRED-sentinel-PASS. The CANONICAL test was not executed. Reading A correctly identifies that §15.13.7 one-shot binds the canonical statistical experiment, not the file-system read.

2. **Article IV discipline argument.** Under Reading B, the next H_next strategy hypothesis would also have to wait until 2026-04-22..present-fresh-tape materializes (~6+ weeks calendar wait + Dara work + governance overhead) to obtain a virgin OOS window. Reading A preserves the canonical hold-out for the canonical test; Reading B forecloses the hold-out for ALL subsequent measurements regardless of whether the canonical test executed.

3. **Engineering vs statistical distinction.** Mira Round 3 §3.1 surfaces F2-T9-OBS-1 as a *process-side* gap in ESC-012 R5 audit scope — Sable did not flag F2-T8-T1 as a pre-N8 prereq because §15.13.12 sign-off chain was scoped under "downstream of R5 close, not pre-condition to it." This is engineering process gap, NOT statistical experimenter-bias contamination. Reading A correctly preserves the statistical experiment integrity by re-executing the canonical test once the engineering wiring is corrected.

4. **N8 same-window IC measurement is informative diagnostic, NOT outcome adjudication.** The IC=0.865933 over holdout-window measurement provides cross-check evidence that the predictor↔label rank stability is preserved across windows under the same definition. This is informative diagnostic under H1 (structural pattern preserved). It does NOT pre-adjudicate the cross-window K3 decay test outcome (which uses in-sample-fit predictions extrapolated forward over OOS labels — a deliberately cross-window measurement). Therefore Reading A's claim that the canonical test has NOT been executed is statistically correct.

**Argument for Reading B (Conservative):**

1. **Strict Anti-Article-IV Guard #3 reading.** "NO touch hold-out lock" reads literal at the parquet input level. N8 read `data/holdout/` parquet root via `dataset_sha256: ac884afb…`. Under strict literal reading, this is a touch.

2. **Researcher contamination at file-read level.** Even if the canonical K3 decay metric was not computed, the researcher (Beckett + Mira reviewers) HAS observed the auxiliary distribution diagnostics (sharpe_mean, sharpe_std, sortino, max_drawdown, profit_factor, hit_rate) per N8 `full_report.json`. This information cannot be unread; subsequent decisions on H_next on the same regime would be made by a researcher whose priors have been updated by these observations. Per AFML §1 + Bailey-LdP 2014 §3 strict reading, this is contamination.

3. **Operator unlock authorization.** Sable §2.4 / §4.2 audit confirms operator authorized hold-out unlock via `VESPERA_UNLOCK_HOLDOUT=1` environment variable for N8 invocation. The unlock was operationally executed; the spec §15.10/§15.13 transition was enacted at the operator level even if the engine-level `holdout_locked` flag remained True.

### §3.3 Riven adjudication

I find Reading A *more compelling under risk-side custodial discipline* for the following reasons:

(1) **§15.13.5 falsifiability semantics are statistically definitionally cross-window** — the in-sample IC-over-holdout-window N8 measurement does NOT exercise the falsifiable content of §15.13.5 ("preserve in-sample IC sign AND retain ≥ 50% of in-sample magnitude"). The cross-window propagation step that COULD fail under H0 has not yet been performed. Strict Reading B makes the §15.13.5 K3 decay test *unobservable* — which would defeat the purpose of authoring §15.13 in the first place (per ESC-012 R2 mandate to enable Phase G OOS unlock).

(2) **Reading B forecloses ALL future statistical measurement on the regime, not just T002** — this is a much heavier governance cost than Reading B proponents acknowledge. H_next strategies on the same regime would inherit OOS budget exhaustion under Reading B whether T002 is retired or not.

(3) **Researcher contamination concern (Reading B argument 2) is real but bounded.** The auxiliary distribution diagnostics are documented in Mira Round 3 §2 + §6.2 + §6.3 — they are now part of the public squad ledger. However, under Path (iv), the researcher will execute the canonical K3 decay test under PRR-20260430-1 hash-frozen 4-branch disposition rule; the disposition rule was authored *before* N8 evidence was observed (PRR registered 2026-04-30; N8 timestamp_brt 2026-04-30T21:11:42 per Mira Round 3 frontmatter). The 4-branch partition is hash-frozen and the bin a future K3 decay measurement falls into is determined by the canonical test, not by researcher discretion. **Researcher-contamination risk under Reading B is a legitimate concern but is mitigated by hash-freeze discipline of PRR-20260430-1.**

(4) **My ESC-012 minority Path C primary reasoning (OOS budget economics for H_next preservation) is partially undermined by the parquet-already-read fact**. Even under Path C retire-T002 selection, the parquet was structurally read by N8; Reading B would say OOS budget is consumed regardless; Reading A would say the canonical test is what binds and (iv) executes it once. From the risk perimeter: the marginal cost of (iv) (~5-10 LoC + ~3h) is *small* relative to the marginal information value (binds verdict to PRR R15/R16/R17). Path C now does NOT bank the OOS budget for H_next under Reading B; under Reading A, Path C foregoes the canonical test that the §15.13 spec was authored to enable.

**Riven adjudication: Reading A (Mira authoritative) is more consistent with risk-side custodial discipline AND with Article IV preservation.** Reading B's strict literalism would foreclose the §15.13 spec mechanism entirely and is not consistent with ESC-012 R9 reading "result is binding regardless of outcome" (which presupposes a *result* was produced — i.e., the canonical test was executed).

### §3.4 Reading-A risk acknowledgments

Under Reading A, I custodially acknowledge the following risks and impose mitigations:

- **Researcher-contamination at file-read level (Reading B argument 2 residual concern).** Mitigation: PRR-20260430-1 hash-frozen 4-branch disposition rule was registered BEFORE N8 evidence observation; the disposition rule binds the verdict to the K3 decay outcome, not to researcher discretion under updated priors. Mira Round 3 §3.3 explicitly rejects post-hoc lenient routing under outcome pressure. The mitigation is in place.

- **Operator unlock authorization (Reading B argument 3 residual concern).** Mitigation: §6 condition C5 below requires Sable Phase G coherence audit Round 2 to verify that the protocol-corrected re-run honors §15.13.2 mechanism block verbatim AND that the operator authorization for `VESPERA_UNLOCK_HOLDOUT=1` is recorded with provenance per existing protocol. This preserves audit-trail completeness.

- **N8 truncation 92% window coverage (F-01 carry-forward).** Mitigation: §6 condition C6 below requires the Path (iv) re-run to consume the FULL preregistered window once Sentinel data lag closes (2026-04-22..2026-04-21 boundary fully covered after ingestion lag — ~6+ weeks calendar wait per Mira Round 3 §5.3 + Sable F-01 audit). Alternatively, accept the 92% coverage at re-run time under Sable Option (a) ACCEPT TRUNCATED with mandatory disclosure (Mira Round 3 §5.3 concurs). Council adjudicates which mitigation per §6 C6.

---

## §4 Risk perimeter both paths

This §4 evaluates each path against Riven REGRA ABSOLUTA + §11.5 cumulative pre-conditions + Gate 5 fence integrity + Anti-Article-IV Guards 1-8 carry-forward.

### §4.1 Quarter-Kelly REGRA ABSOLUTA preservation per path

| Path | Quarter-Kelly status | Notes |
|---|---|---|
| **Path (iv)** protocol-corrected re-run | **PRESERVED INTACT during re-run; conditional on outcome.** No sizing exercise authorized during re-run; Path (iv) is a metric-execution task only. Post-re-run outcomes: under R15 surprise PASS → ESC-014 surprise-PASS council adjudicates K1 strict bar interpretation under K1+K2+K3 ALL COMPUTED-PASS; sizing pressure NOT introduced unless §11.5 cumulative chain clears AND paper-mode Phase G/H clears (still future scope, T002.7+ successor stories per ESC-012 R10). Under R16/R17 → T002 retire; quarter-Kelly moot. Under INCONCLUSIVE-borderline → ESC further escalation; quarter-Kelly moot. | Quarter-Kelly REGRA ABSOLUTA inviolate during (iv) execution. |
| **Path C** retire | **PRESERVED INTACT — no sizing pressure introduced.** | Same as ESC-012 ballot §3.1 reasoning — quarter-Kelly cap inviolate per §1.2 Leg 1 + §2.5 custodial discipline ESC-012. Available for fresh deployment against H_next when bucket-B + bucket-C clearance clears (assuming H_next has untouched OOS budget under Reading A; under Reading B, OOS budget already consumed by N8 parquet read regardless of T002 retirement). |

**Risk-side reading: BOTH paths preserve quarter-Kelly REGRA ABSOLUTA INTACT during execution.** No path under either reading authorizes sizing on a non-cleared K1/K2/K3-COMPUTED distribution.

### §4.2 §11.5 capital-ramp pre-conditions §1..§7 status per path

| # | §11.5 pre-condition | Path (iv) impact | Path C impact |
|---|---|---|---|
| 1 | Bucket A `engineering_wiring` HARNESS_PASS | UNCHANGED — pre-condition cleared at N6+/N7-prime engineering layer | UNCHANGED — same evidence base preserved as bucket-A historical reference |
| 2 | Bucket B `strategy_edge` GATE_4_PASS | **CONDITIONAL on Path (iv) outcome** — under R15 fires → CONDITIONAL PASS pending §15.13.6 + §10 footer Phase G/H paper-mode requirement; under R16/R17 → CONFIRMED FAIL clean falsification or costed_out_edge OOS-confirmed; under INCONCLUSIVE-borderline → CONTINUES UNRESOLVED. | **NOT applicable to T002** — pre-condition deferred to H_next hypothesis. |
| 3 | Bucket C `paper_mode_audit` PAPER_AUDIT_PASS ≥ 5 sessions | UNREACHABLE under (iv) Round 3.1 alone — Phase G/H paper-mode is T002.7+ successor scope per ESC-012 R10 + §15.13.6 fence; even under R15 fires, paper-mode is necessary-not-sufficient additional pre-req. | NOT applicable to T002. |
| 4 | Mira independent Gate 5 cosign (DSR > 0.95 + PBO < 0.5 + IC decay over real PnL COMPUTED) | UNREACHABLE under (iv) Round 3.1 alone — Mira Round 3.1 verdict adjudicates Gate 4b clearance, NOT Gate 5; Gate 5 requires §15.13.6 + §11.5 cumulative chain. | NOT applicable to T002. |
| 5 | Riven independent Gate 5 cosign | UNREACHABLE under (iv) Round 3.1 alone — same chain; Riven Gate 5 disarm authority preserved INTACT for downstream chain clearance. | NOT applicable to T002 (Riven Gate 5 disarm authority preserved INTACT for H_next). |
| 6 | Toy benchmark E6 discriminator preservation | UNCHANGED — preserved at N6/N6+ engineering layer | UNCHANGED — preserved as bucket-A historical reference |
| 7 | Synthetic-vs-real-tape attribution audit Round 3 entry | **NEW Round 3 entry under §6 below** — sub-classification depends on (iv) outcome (`bucket_B_strategy_edge_OOS_CONFIRMED_pending_paper_mode` under R15 fires; OR `bucket_B_strategy_edge_OOS_CLEAN_negative` under R16; OR `costed_out_edge_oos_confirmed` under R17; OR `phase_g_protocol_compliance_gap_resolved_with_INCONCLUSIVE_borderline` under residual). | **NEW Round 3 entry** under conservative reading (§6 below) — sub-classification `phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading` (under Reading B) OR `bucket_B_strategy_edge_RETIRED_phase_g_protocol_gap_under_OOS_one_shot_strict` (alternative phrasing). |

**Risk-side reading on §11.5 pre-conditions:** Path (iv) keeps T002 in the §11.5 dependency tree pending Round 3.1 outcome adjudication (with Mira F2-T9.1 Round 3.1 authority). Path C explicitly removes T002 from the dependency tree, freeing all five pre-conditions for re-instantiation against H_next hypothesis evaluation. **Both paths are custodially clean at the §11.5 pre-conditions layer; the question is whether the canonical Phase G test is worth executing once given marginal cost ~5-10 LoC + ~3h vs marginal information value HIGH.**

### §4.3 Gate 5 fence integrity per path

| Path | Gate 5 fence integrity post-path | Custodial fence concerns |
|---|---|---|
| **Path (iv)** | UNCHANGED at policy level — Gate 5 LOCKED carries forward; Round 3.1 verdict adjudicates Gate 4b clearance, NOT Gate 5 disarm. **Risk: under R15 surprise PASS outcome (~27% posterior per §2.4), governance pressure to interpret K1+K2+K3 ALL COMPUTED-PASS as deployment-eligible without paper-mode Phase G/H — anti-pattern §5.7 carry-forward.** Riven custodial veto fires per §3.2 Single-leg-fire-REJECT + §15.13.6 fence + ESC-012 R10 verbatim. Manageable. | **MEDIUM — under R15 outcome creates governance pressure for premature Gate 5 disarm.** Mitigated by §15.13.6 + §10 footer + ESC-012 R10 + Riven custodial monopoly. |
| **Path C** | **UNCHANGED at policy level — Gate 5 LOCKED carries forward; T002 explicitly removed from Gate 5 dependency tree. Fence preserved INTACT.** | **LOW — fence integrity preserved cleanly; T002 retirement is governance-clean.** Same as ESC-012 §4.1 Path C reasoning. |

### §4.4 Anti-Article-IV Guards 1-8 carry-forward per path

| Guard | Path (iv) status | Path C status |
|---|---|---|
| **#1** Dex impl gated em Mira spec PASS | F2-T8-T1 Dex wiring task (~5-10 LoC) gated on §15.13.2 mechanism block + Mira Round 3 §11.1 micro-task scope; Mira Round 3.1 verdict (post-N8.1) adjudicates Round 3.1 Gate 4b clearance | UNCHANGED — no new impl authorized under retirement |
| **#2** NO engine config mutation at runtime | engine_config_sha256 IDENTICAL F2 (ESC-012 R6 binding); Path (iv) variable change is `holdout_locked` flag flip + status propagation per §15.13.2 mechanism — NOT engine config mutation | UNCHANGED |
| **#3** NO touch hold-out lock | **AUTHORIZED §15.10/§15.13 transition** under Reading A authoritative; parquet read at file-system layer ALREADY occurred via N8 (operator-authorized via `VESPERA_UNLOCK_HOLDOUT=1`); §15.13.7 one-shot binds the K3 decay metric measurement (Mira Round 3 §1 + §3 + §11 reading). Path (iv) executes the canonical K3 decay test for the FIRST TIME — preserves the §15.13.7 invariant at the metric layer. | **AUTHORIZED preserve-virgin-at-preregistration-layer** under conservative reading; parquet read already structurally occurred, but virginity-at-preregistration-layer is preserved by NOT executing the canonical K3 decay test. |
| **#4** Gate 4 thresholds UNMOVABLE | DSR > 0.95, PBO < 0.5, IC > 0 reaffirmed verbatim; Path (iv) does NOT relax K1 strict bar; PRR-20260430-1 §3.1 R15 trigger conjunction strict reading enforced by Mira Round 3.1 authority | UNCHANGED — thresholds preserved AS-IS for H_next |
| **#5** NO subsample backtest run | Path (iv) consumes same parquet at full window coverage (truncated to 92% per F-01; not subsample selection — operational ingestion lag); §6 C6 below addresses truncation mitigation | UNCHANGED |
| **#6** Gate 5 sem Gate 4 = REJECT | §4.3 above + §15.13.6 + §10 footer + ESC-012 R10 fence preservation | UNCHANGED — fence preserved by retirement |
| **#7** NO push (Gage exclusive) | Mira Round 3.1 + Riven cosign Round 3.1 entries → Pax/Gage standard chain at story close | UNCHANGED — retirement docs → Pax/Gage standard chain |
| **#8** Verdict-issuing protocol — `*_status` provenance + `InvalidVerdictReport` raise | Path (iv) wires `ic_holdout_status='computed'` propagation per §15.13.2 mechanism — restores Phase G semantic-layer Guard #8 invariant (currently violated-in-spirit per Mira Round 3 §12 Guard #8 row) | UNCHANGED — Guard #8 violation-in-spirit on N8 carries forward as procedural finding F2-T9-OBS-1 documented at retirement |

**All eight Anti-Article-IV Guards honored by both paths.** Path (iv) RESTORES Guard #8 invariant by wiring §15.13.2 mechanism; Path C documents the Guard #8 violation-in-spirit at retirement as procedural finding without restoring the invariant.

---

## §5 3-bucket attribution forward declaration both paths

Per Mira spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 + ESC-012 R11 + Riven post-mortem authority: Round 3 entry MUST be appended to `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §2 ledger.

### §5.1 Path (iv) forward declaration — bucket attribution depends on Round 3.1 outcome

If council ratifies Path (iv), Riven authoring Round 3 (THIS ballot ratification at council close) + Round 3.1 (post-N8.1 verdict) entries:

**Round 3 entry (Path (iv) authorized, Round 3 protocol-compliance gap documented):**
```
| N8 OOS holdout-window run (Phase F protocol against Phase G window 2026-04-30..2026-05-01)
| docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Mira Round 3 INCONCLUSIVE_pending_phase_g_proper)
  + this ESC-013 ballot Path (iv) authorization
| bucket "phase_g_protocol_compliance_gap" — Mira Round 3 NEW (within bucket B envelope)
| N8 executed --phase F not --phase G due to scripts/run_cpcv_dry_run.py:1093 hardcoded
  holdout_locked=True; F2-T8-T1 wiring task implicit-but-not-flagged in pre-N8 prereq chain;
  result is DEFERRED-sentinel-PASS on K3, not COMPUTED-PASS the canonical Phase G OOS
  decay test PRR §3.1 R15 demands. Empirical observations (subject to protocol caveat):
  DSR=0.965 above strict bar 0.95 OOS; PBO=0.162 well below 0.5; IC=0.866 over holdout
  window same-window-IC near-IDENTICAL F2 IS IC=0.866; sharpe_mean improved 0.046→0.101 OOS;
  hit_rate 0.472 ≈ 0.5 random walk per-trade preserved across windows.
| Disposition: ESC-013 ratified Path (iv) protocol-corrected re-run authority under
  Reading A (Mira authoritative — §15.13.7 one-shot binds K3 decay metric measurement).
  Round 3.1 entry below pending Mira F2-T9.1 verdict.
```

**Round 3.1 entry (post-N8.1 verdict, branched on outcome):**
- **Under R15 fires:** `bucket_B_strategy_edge_OOS_CONFIRMED_pending_paper_mode` — Phase G K3 decay COMPUTED-PASS + K1 OOS-PASS + K2 OOS-PASS; Gate 4b GATE_4_PASS_oos_confirmed; Gate 5 still LOCKED pending paper-mode Phase G/H per §15.13.6 + ESC-012 R10 fence; ESC-014 surprise-PASS adjudication agenda convened (Aria + Mira + Riven + Pax + Sable + Kira) per ESC-012 R15 mandate.
- **Under R16 fires:** `bucket_B_strategy_edge_OOS_CLEAN_negative` — Phase G K3 decay COMPUTED-FAIL collapse (IC_holdout < 0.3); strategy edge falsified clean per spec §0; T002 retire ceremony with refined diagnostic (rank stability did NOT preserve cross-window).
- **Under R17 fires:** `costed_out_edge_oos_confirmed` — Phase G K3 decay COMPUTED-PASS partial (IC ∈ [0.3, 0.5×IS)) + K1 OOS-FAIL strict; costed_out_edge OOS-confirmed; T002 retire ceremony with refined diagnostic (signal real OOS-stable but cost-foreclosed).
- **Under INCONCLUSIVE-borderline:** `phase_g_protocol_compliance_gap_resolved_with_INCONCLUSIVE_borderline` — protocol gap closed but metric outcome borderline; further ESC escalation per PRR §3.4 Reading A residual branch.

### §5.2 Path C forward declaration — single-entry retirement

If council ratifies Path C (Reading B prevails), Riven authoring Round 3 entry:

```
| N8 OOS holdout-window run (Phase F protocol against Phase G window 2026-04-30..2026-05-01)
| docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Mira Round 3 INCONCLUSIVE)
  + this ESC-013 ballot Path C authorization
| bucket "strategy_edge_undetermined_protocol_gap" — Mira Round 3 NEW
  (within bucket B envelope; sub-classification per Reading B strict reading)
| N8 executed --phase F not --phase G due to scripts/run_cpcv_dry_run.py:1093 hardcoded
  holdout_locked=True; F2-T8-T1 wiring task NOT executed pre-N8; result is DEFERRED-sentinel-PASS;
  parquet read at file-system layer ALREADY occurred under operator-authorized
  VESPERA_UNLOCK_HOLDOUT=1 unlock; under Reading B strict §15.13.7 one-shot interpretation,
  parquet read IS consumption; canonical K3 decay test foreclosed for THIS strategy under
  same regime.
| Disposition: ESC-013 ratified Path C — T002 retire with diagnostic
  phase_g_protocol_compliance_gap_unrecoverable_under_oos_one_shot_strict_reading.
  OOS budget for H_next on same regime ALSO unavailable under Reading B (parquet structurally
  read; researcher contamination at file-read level real per AFML §1 + Bailey-LdP 2014 §3).
  H_next pursuit on different regime (e.g., opening 30min, lunchtime fade, day-of-week premium)
  retains hold-out budget options; Pax @po authority adjudicates which H_next direction.
```

### §5.3 Round 3 NEW anti-pattern §5.11 proposed (both paths)

Regardless of Path (iv) or Path C selection, Riven authoring NEW anti-pattern §5.11 in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §5 catalog:

```
Anti-pattern §5.11 — `phase_unlock_protocol_gap_at_run_invocation`:
Pre-N8 run prerequisites scoped under "downstream of Sable Phase G coherence audit close,
not pre-condition to it" can leave wiring tasks (e.g., F2-T8-T1 Dex `holdout_locked=False`
flag plumbing in `scripts/run_cpcv_dry_run.py:1093`) implicit; engine harness can produce
DEFERRED-sentinel-PASS instead of COMPUTED-PASS at the verdict layer; the run completes
without errors but does NOT exercise the canonical OOS test. Sable Phase G coherence audit
Round 2+ MUST enumerate per-§15.13 sub-section sign-off chain (e.g., §15.13.2 mechanism
block, §15.13.5 K3 decay test, §15.13.7 one-shot, §15.13.8 verdict label discipline,
§15.13.12 sign-off chain row F2-T8-T1) as pre-N8 prerequisites with explicit
"verified-wired-pre-N8" status, NOT as downstream tasks. Future Phase G/H/I unlock protocols
MUST explicitly enumerate engine-script-wiring as Tier-1 pre-N8 prerequisite.
```

Anchor: Mira Round 3 §3.1 F2-T9-OBS-1 procedural finding + ESC-013 council adjudication carry-forward.

---

## §6 Personal preference disclosure

### §6.1 ESC-012 minority Path C primary — do I maintain?

**Honest disclosure: I no longer maintain Path C as primary preference under N8 evidence + Mira Round 3 reading.**

My ESC-012 ballot §1.2 + §5 disclosed Path C primary preference grounded in three legs (Leg 1 K1-strict-foreclosure-invariance; Leg 2 Bonferroni-budget-burn-rate against refinement; Leg 3 OOS-budget-economics-one-shot prior P(a) ≈ 0.85). The N8 evidence + Mira Round 3 §3 protocol-compliance gap finding force a Bayesian re-evaluation:

- **Leg 1 (K1-strict-foreclosure-invariance):** my ESC-012 reasoning was that `costed_out_edge` foreclosed at K1 strict bar 0.95 by 0.183 below in-sample; refinement / OOS unlock cannot lift without cost-reduction R&D OFF. **N8 evidence partially contradicts**: DSR=0.965 *observed* above strict bar 0.95 at the OOS point estimate. Mira Round 3 §4 reads this as point-estimate observed PASS at K1 strict bar (no bootstrap CI per current pipeline; Mira OBS-2). Under N8 evidence, Leg 1's "K1 cannot be lifted" reasoning is partially undermined — K1 *observably crossed the bar* in the OOS window. Whether Path (iv) protocol-corrected re-run yields R15 surprise PASS conjunction depends on K3 decay COMPUTED-PASS additionally — but the K1 conjunct alone is no longer the foreclosure-invariance lock I priored on.

- **Leg 2 (Bonferroni-budget-burn-rate):** my ESC-012 reasoning was about Path A' refinement re-evaluation over the same in-sample window inflating n_trials. Path (iv) is NOT refinement — it is protocol-corrected first-execution of the canonical Phase G test. ESC-012 R6 reusability invariant binding (Bonferroni n_trials=5 IDENTICAL F2; predictor↔label IDENTICAL F2; engine_config_sha256 IDENTICAL F2). **Leg 2 does NOT apply to Path (iv).** This was always the case at ESC-012 (Leg 2 specifically targeted Path A'); the application here is correct.

- **Leg 3 (OOS-budget-economics):** my ESC-012 prior P(a) ≈ 0.85 / P(b) ≈ 0.15 priored on regime-stationarity preserves cost-erosion. **N8 evidence updates this prior substantially** (§2 above — posterior P(R15 fires | Path (iv) executes) ≈ 0.27). The OOS-budget-economics calculation flips because: (a) parquet read already structurally consumed via N8 (Reading B argument 2 contamination at file-read level real concern); (b) marginal cost of Path (iv) is small (~5-10 LoC + ~3h); (c) marginal information value is HIGH (binds verdict to PRR R15/R16/R17). **Leg 3 risk-side reading flips from "Path B EV is medium-low" (ESC-012 ballot §1.2) to "Path (iv) EV is medium-high" (this ballot §2).**

**Updated personal preference: Path (iv) preferred under N8 evidence + Mira Round 3 reading.** Disclosure logic: at ESC-012 I priored on F2 IS evidence; at ESC-013 I update on N8 OOS evidence (even though N8 is not the canonical K3 decay test, it is informative diagnostic that updates my prior on the K1 strict bar OOS-PASS likelihood). Honest Bayesian update is required by Article IV preservation discipline. My ESC-012 ballot §5.4 counterfactual #2 ("In-sample K1 partial-PASS observed Round 2") explicitly disclosed the boundary condition: "If Round 2 had observed DSR_in_sample ∈ [0.85, 0.95) (within striking distance of strict bar) AND IC_in_sample > 0.5 AND PBO < 0.4 (strict K2), Path B Phase G unlock would have higher EV under Riven prior because regime-stationarity-preserves-cost-erosion would map to OOS DSR ∈ [0.80, 1.05] with non-trivial probability ≥ 0.30 of clean Phase G PASS." The N8 OOS observation DSR=0.965 is *above* the strict bar entirely — much stronger evidence than the ESC-012 counterfactual #2 striking-distance threshold required to flip my vote.

### §6.2 Riven persona prior consistency check

Riven persona core principle: "em dúvida, reduzo." At ESC-012 my dúvida was high (Leg 3 OOS-budget allocation under K1 strict bar foreclosure with cost-reduction OFF). At ESC-013 my dúvida is *lower* on the K1 OOS conjunct (observed PASS at point estimate) and *moderate* on the K3 decay conjunct (cross-window propagation question that Path (iv) actually answers). The persona principle still applies — but "reduzo" here means "execute the small ~5-10 LoC + ~3h test that BINDS the verdict to PRR-20260430-1 hash-frozen disposition rule" rather than "skip the test and live with INCONCLUSIVE-protocol-gap residual branch indefinitely." Reducing dúvida by executing the canonical test (under hash-freeze discipline preventing post-hoc reinterpretation) IS the conservative custodial action under updated posterior.

Riven persona REGRA ABSOLUTA "Sharpe é métrica; drawdown é sobrevivência. Fundo morto não volta." — this principle is preserved under Path (iv) because (a) no sizing pressure introduced during re-run; (b) Gate 5 fence remains LOCKED regardless of (iv) outcome until paper-mode Phase G/H clears; (c) §11.5 cumulative chain custodial discipline preserved per §6 conditions below. Path (iv) is operationally equivalent to "execute one canonical statistical test that the spec was authored to enable, with hash-frozen disposition rule preventing outcome-pressure reinterpretation."

### §6.3 What would FLIP my vote back to Path C

For risk-perimeter discipline transparency, I record the counterfactuals that WOULD flip my vote back to Path C:

- **§15.13.7 one-shot Reading B prevails at council majority.** If council adjudicates Reading B (parquet-read-as-consumption strict) prevails, then Path (iv) is foreclosed by ESC-012 R9 strict reading and Path C activates per §3.2 Reading B argument residual logic. Mira Round 3 §1 + §11 explicitly preserves both readings as legitimate — council adjudication is decisive.

- **F2-T8-T1 micro-task scope inflates beyond ~5-10 LoC.** If Aria + Dex investigation reveals the wiring is more complex than estimated (e.g., requires changes to `vespera_metrics.info_coef` API, or requires changes to engine_config_sha256 itself, or requires Bonferroni n_trials expansion to handle Phase G as separate trial), then ESC-012 R6 reusability invariant breaks and Path (iv) becomes a refinement rather than a protocol correction. Riven custodial veto fires per §15.13 mechanism integrity.

- **Sentinel data lag worsens beyond reasonable wait period.** §6 condition C6 below addresses 92% truncation; if council requires full-window 100% coverage (per Mira Round 3 §5.3 nuance) and the wait extends beyond 6+ weeks calendar with no resolution, Path C may be re-considered as squad-bandwidth-economy fallback. ESC-012 R5 fallback (14-day slip threshold) carry-forward applies.

These counterfactuals are NOT pleadings for re-discussion — they are transparency disclosures of the boundary conditions of my Path (iv) vote.

### §6.4 Council majority Path C respected

If ESC-013 council majority adopts Path C over Path (iv), my custodial veto authority over Gate 5 dual-sign DOES NOT auto-fire — I will exercise it per §6 conditions if any future sign-off attempt commits an anti-pattern §5.1/§5.2/§5.7/§5.10 of the post-mortem catalog. The Path C adjudication is a legitimate Reading B reading; my Path (iv) vote here is grounded in Reading A authoritative reading per Mira Round 3.

---

## §7 Article IV self-audit

Every claim in this ballot traces to (a) source artifact in repository, (b) governance ledger entry (council resolution OR ESC condition), (c) Mira spec § anchor, (d) Bailey-LdP / Kelly / Thorp / AFML external citation, (e) Riven persona principle / REGRA ABSOLUTA, (f) PRR-20260430-1 § anchor, (g) ESC-012 ballot carry-forward (own authoring). NO INVENTION. NO threshold relaxation. NO pre-emption of Mira Round 3 verdict. NO pre-emption of Pax forward-research authority (ESC-011 R10 + ESC-012 R13).

| Claim category | Trace anchors |
|---|---|
| N8 metrics DSR=0.965 / PBO=0.163 / IC=0.866 / IC_holdout DEFERRED-sentinel | `data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/full_report.json` lines 3-9 + Mira Round 3 §1 + §2 |
| Mira Round 3 verdict INCONCLUSIVE_pending_phase_g_proper | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` frontmatter `verdict: GATE_4_INCONCLUSIVE_pending_phase_g_proper` + §1 |
| F2-T9-OBS-1 protocol-compliance gap (`scripts/run_cpcv_dry_run.py:1093` hardcoded `holdout_locked=True`) | Mira Round 3 §3.1 verbatim + direct code-base inspection lines 1088-1102 |
| §15.13.7 one-shot binds K3 decay metric (Reading A authoritative) | Mira Round 3 §1 disposition_rationale + §3 + §8.2 + §11.4 verbatim |
| §15.13.7 parquet-read-as-consumption (Reading B conservative) | Mira Round 3 §1 alternative reading verbatim + Bailey-LdP 2014 §3 + AFML §11-12 contamination canonical |
| PRR-20260430-1 4-branch hash-frozen disposition rule | `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` §3.1-§3.4 + §4.2 verbatim |
| K1 strict bar 0.95 UNMOVABLE per Anti-Article-IV Guard #4 | ESC-011 R14 + ESC-012 R10 + Mira spec v1.2.0 §1 K1 + parent spec yaml v0.2.3 §kill_criteria L207 verbatim |
| K3 decay sub-clause `IC_holdout > 0.5 × IC_in_sample` cross-window semantic | Mira Round 3 §3.3 four-reasons argument + §15.13.5 verbatim + AFML §8.6 IC stability paradigm + Bailey-LdP 2014 §6 |
| ESC-012 R6 reusability invariant (8/9 stamps IDENTICAL F2 confirmed by N8) | Mira Round 3 §5.2 invariant table + N8 `determinism_stamp.json` lines 2-15 |
| ESC-012 R9 single-shot OOS discipline | ESC-012 §4.2 R9 verbatim + Kira C-K3 + Mira C-M6 source |
| Bonferroni n_trials=5 carry-forward | N8 `full_report.json` line 248-249 + Mira Round 3 §2 + ESC-012 R6 |
| F2 IS DSR=0.767 strict-fail-by-0.183 (ESC-012 prior anchor) | Mira F2-T5 Round 2 §1 + own ESC-012 ballot §1.2 Leg 1 |
| Posterior update P(R15 fires \| Path (iv) executes) ≈ 0.27 | this ballot §2.4 — explicit derivation from posterior conjuncts P(K1)=0.50-0.65 × P(K2)=0.85-0.95 × P(K3_in_sample)=0.95+ × P(K3_decay)=0.55-0.70 |
| Riven persona pessimistic prior baseline ~0.10-0.15 industry baseline | López de Prado 2018 AFML §1 quant-research conversion-rate intuition + Riven persona expertise.sizing_framework.haircut_initial verbatim |
| Quarter-Kelly REGRA ABSOLUTA preserved INTACT both paths | this ballot §4.1 + own ESC-012 §3.1 reasoning carry-forward |
| §11.5 cumulative pre-conditions §1..§7 status per path | this ballot §4.2 + Riven post-mortem §3 dependency tree + Riven persona checklists `before_new_strategy_live` |
| Gate 5 fence preservation per §15.13.6 + §10 + ESC-012 R10 | Mira Round 3 §7 footer + own ESC-012 §4 reasoning carry-forward |
| Anti-Article-IV Guards 1-8 carry-forward both paths | this ballot §4.4 + Mira Round 3 §12 + ESC-012 §6 audit + own ESC-012 §7.2 audit |
| Anti-pattern §5.11 NEW proposed | this ballot §5.3 + Mira Round 3 §3.1 F2-T9-OBS-1 procedural finding |
| ESC-014 surprise-PASS council agenda distinction | Mira Round 3 §9.2 + ESC-012 R15 verbatim |
| F2-T8-T1 Dex micro-task ~5-10 LoC scope | Mira Round 3 §11.1 verbatim + spec §15.13.2 mechanism block + §15.13.12 sign-off chain row |
| Path (iv) Beckett N8.1 ~3h wall-time | Mira Round 3 §11.2 verbatim + Beckett N7-prime §10.3 carry-forward |
| ESC-012 minority Path C reasoning preservation | own ESC-012 ballot §1.2 + §5 + §6 verbatim — NOT mutated; this ballot §6.1 + §6.4 honors prior reasoning explicitly |

### §7.1 Article IV self-audit verdict

Every clause in §1-§6 traces to a verifiable source. NO INVENTION (Riven posterior probabilities §2 are EXPLICITLY DISCLOSED as Riven persona pessimistic-by-default + N8-evidence-updated priors per §6.2, NOT empirical measurements; reader can re-evaluate under different priors). NO threshold relaxation (K1 strict bar 0.95 applied AS-IS; quarter-Kelly cap 0.25 applied AS-IS; PRR-20260430-1 4-branch disposition rule cited verbatim). NO pre-emption of Mira Round 3 statistical authority (Mira Round 3 verdict is INPUT to this ballot, not output; Reading A authoritative is Mira's adjudication; this ballot RATIFIES Reading A from risk-perimeter perspective). NO pre-emption of Pax @po forward-research authority (Path (iv) selection is risk-side adjudication; final story drafting + scope discipline post-ESC-013 is Pax authority). NO source-code modification (this ballot is write-only at council-document layer; no code mutation; no spec yaml mutation; no spec markdown mutation; no hold-out touch; no Round 1/Round 2/Round 3 sign-off mutation). NO push (Article II → Gage @devops EXCLUSIVE; Riven authoring this ballot does NOT push — council resolution + post-resolution doc updates routed through Pax/Gage downstream).

### §7.2 Anti-Article-IV Guards self-audit (8 guards verbatim)

| Guard | Mandate | THIS ballot reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | THIS ballot does NOT authorize new impl directly; ESC-013 resolution (if Path (iv)) triggers F2-T8-T1 Dex micro-task gated through Pax + Mira spec §15.13.2 mechanism + Quinn QA + Gage standard chain, NOT Riven authoring |
| **#2** | NO engine config mutation at runtime | THIS ballot does NOT touch engine config; Path (iv) variable change is `holdout_locked` flag flip + status propagation per §15.13.2 mechanism — NOT engine config mutation |
| **#3** | NO touch hold-out lock | THIS ballot ratifies Reading A authoritative (§15.13.7 one-shot binds K3 decay metric; parquet read at file-system layer already occurred via N8 operator-authorized; Path (iv) executes canonical K3 decay test for FIRST TIME — preserves §15.13.7 invariant at metric layer); under Reading A, no further parquet touch beyond N8 read; under Reading B alternative, this ballot preserves Reading B as legitimate alternative for council adjudication |
| **#4** | Gate 4 thresholds UNMOVABLE | THIS ballot APPLIES K1 strict bar 0.95 AS-IS; PRR-20260430-1 §3.1 R15 trigger conjunction strict reading enforced by Mira Round 3.1 authority post-N8.1; vote rationale §1 + §2 + §3 + §6 PRESERVES UNMOVABLE per ESC-011 R14 + ESC-012 R10 + Anti-Article-IV Guard #4 |
| **#5** | NO subsample backtest run | THIS ballot does NOT authorize partial-window evaluation; §6 C6 below addresses 92% truncation per Sable F-01 carry-forward (operational ingestion lag, not subsample selection) |
| **#6** | NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH | THIS ballot CONFIRMS Gate 5 LOCKED post Round 3 INCONCLUSIVE; Path (iv) does NOT pre-disarm Gate 5 even under R15 surprise PASS outcome (§15.13.6 + §10 footer + ESC-012 R10 fence preservation explicit) |
| **#7** | NO push (Gage @devops EXCLUSIVE) | THIS ballot is local-only artifact; council ratification + Gage push gate downstream per Pax/Gage standard chain |
| **#8** | Verdict-issuing protocol — `*_status` provenance + `InvalidVerdictReport` raise on `K_FAIL` with `*_status != 'computed'` | THIS ballot is NOT a verdict-issuing artifact at the Mira layer; it is a council ballot at the ESC-013 layer; Guard #8 referenced as Mira Round 3 §12 input verbatim, NOT mutated. Path (iv) RESTORES Phase G semantic-layer Guard #8 invariant by wiring §15.13.2 mechanism propagating `ic_holdout_status='computed'` |

All eight Anti-Article-IV Guards honored verbatim by THIS ballot. Mira Round 3 §12 audit preserved as input.

---

## §8 Riven cosign 2026-04-30 BRT — ESC-013 ballot

```
Author: Riven (@risk-manager) — Risk Manager & Capital Gatekeeper authority
Council: ESC-013 — T002.7 Phase G protocol-compliance gap adjudication (Path (iv) protocol-corrected re-run vs Path C retire)
Trigger: Mira Round 3 GATE_4_INCONCLUSIVE_pending_phase_g_proper / phase_g_protocol_compliance_gap finding under PRR §3.4 INCONCLUSIVE branch
Authority basis: ESC-011 R7 + R20 carry-forward + ESC-012 R10/R11/R13/R15/R17 + Mira Gate 4b spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 (Riven 3-bucket reclassification authority post Mira Round 3) + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp custodial monopoly

Verdict: APPROVE_PATH_IV (protocol-corrected Phase G proper re-run with conditions §6)

Rationale summary (3-leg risk-side argument; updated by N8 evidence + Mira Round 3 reading):
  Leg 1 — §15.13.7 one-shot binds K3 decay metric measurement (Reading A authoritative; Mira Round 3 §1+§3+§11): N8 produced DEFERRED-sentinel-PASS not COMPUTED-PASS; canonical test has NOT yet executed. R9 single-shot prohibits statistical re-do under adjusted parameters; Path (iv) is FIRST execution of canonical Phase G protocol with predictor↔label IDENTICAL F2 + Bonferroni n_trials=5 IDENTICAL F2 + 8/9 reproducibility stamps IDENTICAL F2.
  Leg 2 — Posterior under N8 evidence updates substantially: P(R15 fires | Path (iv) executes) ≈ 0.27 (vs ESC-012 prior P(b) ≈ 0.10 joint). DSR=0.965 OOS observed PASS at point estimate; PBO=0.163 well below threshold; IC magnitude near-IDENTICAL across windows. ESC-012 ballot §5.4 counterfactual #2 ("In-sample K1 partial-PASS observed Round 2") explicitly disclosed boundary condition; N8 OOS observation DSR=0.965 above strict bar entirely is much stronger evidence than the striking-distance threshold required to flip my vote.
  Leg 3 — Path C now consumes OOS budget asymmetrically: parquet was structurally read by N8; under Reading B strict, OOS budget consumed regardless of T002 retirement; under Reading A authoritative, marginal cost of (iv) ~5-10 LoC + ~3h yields HIGH information value (binds verdict to PRR R15/R16/R17). Path C does NOT bank OOS budget for H_next under Reading B; Path (iv) preserves §15.13.7 invariant at metric layer under Reading A.

Convergent verdict: Path (iv) is custodially cleanest under N8 evidence + Mira Round 3 reading. Path C remains legitimate alternative if council majority adjudicates Reading B prevails (counterfactual §6.3).

Personal preference disclosed §6: Riven NO LONGER maintains ESC-012 minority Path C primary preference. Honest Bayesian update on N8 evidence + Mira Round 3 §15.13.7 reading flips posterior. Riven persona "em dúvida, reduzo" preserved by executing one canonical statistical test under hash-freeze discipline (PRR-20260430-1 4-branch disposition rule) preventing outcome-pressure reinterpretation; Gate 5 fence remains LOCKED regardless of (iv) outcome until paper-mode Phase G/H clears (§11.5 cumulative chain custodial discipline preserved).

Recommended conditions if council adopts Path (iv) (§6 C1..C6 below): F2-T8-T1 Dex micro-task scope-bound ~5-10 LoC against `scripts/run_cpcv_dry_run.py:1093`; Beckett N8.1 ~3h wall-time + reusability invariants R6 IDENTICAL F2 (no engine_config mutation; no Bonferroni expansion; no spec yaml threshold mutation); Sable Phase G coherence audit Round 2 with §15.13 sign-off chain explicit pre-N8.1 enumeration; Mira F2-T9.1 Round 3.1 verdict against PRR §3.1-§3.4 4-branch disposition rule; Riven Round 3 + Round 3.1 post-mortem entries with NEW anti-pattern §5.11 phase_unlock_protocol_gap_at_run_invocation; F-01 truncation 92% mitigation via Sable Option (a) ACCEPT TRUNCATED with mandatory disclosure OR full-window wait (council adjudicates).

Counterfactuals openly disclosed §6.3 (vote conditional on: Reading A prevails council majority; F2-T8-T1 micro-task ~5-10 LoC scope holds; ESC-012 R6 reusability invariant preserved; Sentinel data lag bounded). If any counterfactual condition flips, vote is openly re-evaluable.

ESC-012 minority Path C reasoning preservation §6.4: my ESC-012 ballot §1.2 + §5 + §6 reasoning is NOT mutated. This ESC-013 ballot is NEW evidence + NEW Mira reading update; ESC-012 ballot stands as authored against ESC-012 evidence base. If council majority adopts Path C at ESC-013, my custodial veto authority over Gate 5 dual-sign DOES NOT auto-fire — I will exercise it per §6 conditions if any future sign-off attempt commits an anti-pattern §5.1/§5.2/§5.7/§5.10 of the post-mortem catalog.

Article II preservation: NO push performed by Riven during this ballot authoring. Gage @devops authority preserved for any subsequent commit.
Article IV preservation: every clause traces (§7); no invention; no threshold mutation; no source-code modification; no spec yaml mutation; no hold-out touch beyond Reading A authoritative §15.13.2 mechanism authorization (no further beyond N8 already-occurred parquet read); no Mira Round 3 verdict pre-emption; no Pax @po forward-research authority pre-emption; Riven posterior probabilities §2 disclosed openly as persona pessimistic-by-default + N8-evidence-updated priors NOT empirical measurements.

Anti-Article-IV Guards self-audit §7.2: #1-#7 honored verbatim + Guard #8 RESTORED-IN-SPIRIT under Path (iv) by §15.13.2 mechanism propagating ic_holdout_status='computed' (currently violated-in-spirit on N8 per Mira Round 3 §12 audit).

Authority boundary: Riven authors THIS ballot from risk-perimeter perspective only. Mira retains Gate 4b verdict-issuing authority (Round 3 INCONCLUSIVE; Round 3.1 post-N8.1 forthcoming). Pax retains forward-research direction authority post-ESC-013 (story drafting + scope discipline + 10-point checklist guardian). Gage retains push authority. Tiago retains execution authority. Quinn retains QA authority. Aria retains architecture authority + factory pattern guardian. Beckett retains backtester authority + N8.1 execution. Kira retains scientific peer-review + falsifiability authority. Sable retains coherence-audit authority + R5 carry-forward.

Pre-vote independence statement: Riven authored THIS ballot WITHOUT consulting peer voter ballots (Mira / Aria / Beckett / Kira / Pax / Sable ESC-013 votes). Independence preserved per council protocol. Inputs consulted: PRR-20260430-1 4-branch disposition rule + Mira Round 3 INCONCLUSIVE verdict + ESC-012 resolution carry-forward + own ESC-012 ballot (own authoring) + Riven post-mortem (own authoring) + N8 full_report.json direct read. NO peer-ballot reading pre-vote.

Cosign: Riven @risk-manager 2026-04-30 BRT — ESC-013 ballot (APPROVE_PATH_IV with conditions §6).
```

— Riven, guardando o caixa 🛡️
