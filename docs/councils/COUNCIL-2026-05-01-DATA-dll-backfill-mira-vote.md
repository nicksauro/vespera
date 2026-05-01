---
council_id: DATA-2026-05-01-dll-backfill
council_topic: Pre-2024 archival window viability for H_next OOS extension via DLL backfill (Path A / Path B / Path C adjudication)
ballot_authority: Mira (@ml-researcher)
ballot_role: ML/statistical authority — author of T002 spec yaml v0.2.x, Mira Gate 4b spec v1.2.0, Round 3.1 verdict; adjudicator of "virgin-by-discipline vs virgin-by-availability"
date_brt: 2026-05-01
branch: main (ballot independent — no other DATA Council votes read)
inputs_consumed:
  - "Quant Council 2026-05-01 resolution (R6/R7/R8/R9 hold-out conditions)"
  - "VESPERA-DATA-PIPELINE-2026-04-21 council (Sentinel TimescaleDB findings)"
  - "AUDIT-20260426-DB-CONTINUITY (2023 = 6 chunks Jan 2-9 only; 2024-2026 dense)"
  - "T002 retire memory (Round 3.1 + ESC-012 + ESC-013)"
  - "DOMAIN_GLOSSARY (cost atlas v1.0.0; RLP regime documentation)"
  - "Nelo ProfitDLL backfill capability (GetHistoryTrades 27-month limit + exchange code F vs BMF)"
inputs_explicitly_NOT_read:
  - "Other DATA Council ballots (Dara, Sable, Nelo, Nova, Riven if applicable) — Article IV §6 independence enforced"
core_question: "Does pre-2024 archival OOS extension (2023-Q1..2024-Q3) provide statistically valid OOS evidence for H_next deployment decisions, given regime non-stationarity risk + exchange code change + cost atlas validity boundary?"
verdict: CONDITIONAL_APPROVE_PATH_A_WITH_REGIME_CHECK_AND_PRIMARY_FORWARD_TIME
fallback_paths:
  - "PATH_A (pre-2024 archival 2023-Q1..2024-Q3 via DLL backfill): conditional approve as SECONDARY validation channel, never as PRIMARY hold-out"
  - "PATH_B (forward-time 2026-05-01..2026-10-31 per Quant R7): RATIFIED as PRIMARY (already adopted)"
  - "PATH_C (no backfill; forward-time exclusive): defensible if regime check fails"
cosign: Mira @ml-researcher 2026-05-01 BRT
related_artifacts:
  - docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md (R6/R7/R8/R9)
  - docs/audits/AUDIT-20260426-DB-CONTINUITY.md (§3 Q1: 2023 = 6 Jan chunks only)
  - docs/councils/VESPERA-DATA-PIPELINE-2026-04-21.md (Turno 2 Nelo: DLL 27-month limit)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-mira-vote.md (Round 4 ballot — forward-time PRIMARY)
---

# Data Council 2026-05-01 — DLL Backfill (pre-2024 archival window) — Mira (@ml-researcher)

> **Verdict (independent ballot — Article IV §6 enforced):** **`CONDITIONAL_APPROVE_PATH_A_WITH_REGIME_CHECK`** — pre-2024 archival window 2023-Q1..2024-Q3 is statistically *useful* as a SECONDARY validation channel, NOT as PRIMARY hold-out. Path B (forward-time 2026-05-01..2026-10-31, Quant R7) remains PRIMARY. Approval of Path A is conditional on four pre-conditions (§7) — regime stationarity check + Dara virginity audit + cost atlas pre-2024 validity adjudication + sample-size projection.
>
> **Authority basis:** ML/statistical voice on this council. Author of T002 spec yaml v0.2.x data_splits + Mira Gate 4b spec v1.2.0 §15.10 K3 decay. Adjudicator on "virgin-by-discipline vs virgin-by-availability" question raised in Quant R8.
>
> **Single most important point:** the **fundamental statistical question is regime stationarity**, not data availability. Pre-2024 OOS evidence is of high value IF and only IF the 2023-2024-Q3 microstructure regime materially matches the 2024-Q4..2026 regime that produced T002 in-sample IC=0.866. If regime materially differs, pre-2024 testing is a *different-regime* test (informative for robustness) but not a clean OOS extension of the T002 thesis (which is what it would need to be to support H_next deployment decisions).

---

## §1 Statistical implications of pre-2024 archival window

### §1.1 Sample-size feasibility — comfortably above R9 floor

Per Nelo's DLL 27-month-back constraint (VESPERA-DATA-PIPELINE-2026-04-21 Turno 2) measured from current backfill date (2026-05-01), the reachable archival window is approximately **2023-Q1..2024-Q3** — 6 viable quarters of WDO history. Sample-size implications:

| Quantity | Value | Source |
|---|---|---|
| Quarters viable | ~6 (2023-Q1..2024-Q3) | DLL 27-month limit + 2023-Q1 truncation |
| Trading days/quarter | ~63 (252/year ÷ 4) | Calendar atlas |
| Total viable sessions | ~378 sessions | 6 × 63 |
| Entry windows/session (4 per spec yaml §15.3 — 16:55, 17:10, 17:25, 17:40) | 4 | Mira spec yaml v0.2.3 |
| Total events | ~1512 | 378 × 4 |
| CPCV harness | 45 paths × ~5 trials | Quant R5 budget |
| Path-events trial-events | ~340 200 | 1512 × 45 × 5 |
| **R9 minimum floor** | **150-250** | ESC-011 R9 binding |
| **Headroom factor over R9** | **~1361×** | 340 200 / 250 |

Sample-size is **NOT the binding constraint** for Path A — pre-2024 archival comfortably clears the AC9 R9 floor by 3+ orders of magnitude. This is statistically uncontested.

### §1.2 Bonferroni-adjusted DSR threshold under cumulative trial budget

Per Quant R3 (DSR threshold ~1.005 under n_trials_cumulative=8) — this threshold remains the binding deployment bar regardless of whether evidence comes from forward-time or pre-2024 archival. Pre-2024 OOS observation that fails to clear DSR>1.005 produces **the same verdict** as forward-time failure: predictor is rank-stable but strategy-over-costs is not.

What pre-2024 OOS adds to the inference under good-edge scenario:
- IF Path B (forward-time) clears DSR > 1.005 AND Path A (pre-2024 archival) clears DSR > 1.005 → **convergent two-window evidence** (very strong; multi-regime persistence).
- IF Path B clears AND Path A fails → **regime-bound edge** (deploy with regime-dependence caveat; tighten Riven sizing).
- IF Path B fails AND Path A clears → **possible regime drift** (T002 fade was 2023-2024 phenomenon; do not deploy on forward data).
- IF both fail → **clean negative** (retire H_next).

The 2×2 truth table is rich; pre-2024 archival adds an axis of inference that single-window forward-time alone cannot provide. **This is the strongest argument FOR Path A as secondary channel.**

### §1.3 What pre-2024 archival CANNOT do under any condition

Pre-2024 archival CANNOT:
- Substitute for Path B forward-time as PRIMARY hold-out (Quant R7 binding; forward-time is impossible-to-leak by construction; pre-2024 is not).
- Bypass Bonferroni budget — pre-2024 evidence still consumes from the same n_trials_cumulative=8 budget. Running Path A as a 4th-trial blow against the K=3 H_next budget would itself violate Quant R5 cap.
- Validate predictor refinements — predictor IP is bit-frozen per Quant R4; pre-2024 archival validates the EXISTING predictor, not modified versions.

---

## §2 Regime stationarity concern (CRITICAL — driving the conditional approval)

### §2.1 Why this is the make-or-break question

Pre-2024 archival is *valid OOS evidence* for the T002-thesis-as-formulated only if the underlying market regime in 2023-2024-Q3 is sufficiently similar to the 2024-Q4..2026 regime to make the test apples-to-apples. The T002 thesis is a structural one (end-of-day inventory unwind in WDO at fixed entry windows {16:55, 17:10, 17:25, 17:40} BRT, predictor `−intraday_flow_direction`). For pre-2024 evidence to apply, four regime axes need to hold reasonably stationary:

### §2.2 Regime axis 1: B3 fee structure (cost atlas v1.0.0 validity boundary)

**Concern level: HIGH.**

Cost atlas v1.0.0 was calibrated against the cost regime in force when T002 in-sample window opened (2024-08-22). Pre-2024 fee schedule differences include:
- B3 emolumentos rate adjustments through 2023-2024 (need Riven authority to enumerate exact dates).
- Margin tiers and intraday discount structures.
- Brokerage commission negotiations on retail tier (cost atlas line 167-168 RLP regime documentation).

If 2023 cost regime is materially DIFFERENT from 2024-Q4 cost regime, then applying cost atlas v1.0.0 to pre-2024 trades produces a **counterfactual cost layer**, not the actual-cost layer that would have applied historically. Two corrective options:

- **Option (i):** archive a **cost atlas v0.x.x** specifically calibrated to 2023 fee schedule (Riven authority); apply v0.x.x to pre-2024 segment, v1.0.0 to 2024-Q4+ segment. Spec YAML carries both atlas references.
- **Option (ii):** declare cost atlas v1.0.0 valid pre-2024 by Riven cosign IF the rate differences are below a tolerance threshold (e.g., < 5% per-trade total cost delta). This is acceptable but requires explicit Riven adjudication, not silent assumption.

**Without (i) or (ii) explicitly resolved, Path A produces cost-layer artifact, not OOS evidence.** This is condition C-M-3 in §7.

### §2.3 Regime axis 2: RLP rules and intraday share

**Concern level: MEDIUM-HIGH.**

Per Nova vote 2026-05-01 §3 + cost atlas line 167-168, the RLP (Retail Liquidity Provider, B3 enum tradeType=13) regime is rule-driven and has shifted over the 2023-2026 window. Specifically:
- RLP intraday share fluctuates 10-30% per Nova/cost atlas; B3 has not published intraday RLP curves.
- Brokerage participation in RLP programs (Rico, XP retail tier) has evolved across 2023-2025 (commercial agreements, KYC tier changes, retail volume distribution).
- Per Nova features-availability matrix, RLP detection (tradeType=13) is **NOT computable from the parquet historic dataset** (parquet has BUY/SELL/NONE only, NOT the 13-type B3 enum). Pre-2024 RLP regime cannot be empirically reconstructed from the trades-only historical data.

If RLP intraday timing has shifted across 2023-2024, then the predictor's measured magnitude at entry windows {16:55, 17:10, 17:25, 17:40} BRT may carry RLP-share regime artifact that 2024-Q4..2026 in-sample window does not. **Nova authority must adjudicate** whether RLP regime in 2023 is sufficiently close to 2024-Q4 regime for the predictor to be apples-to-apples. This is condition C-M-2 in §7 (escalates to Nova).

### §2.4 Regime axis 3: COVID aftermath (2022-2023) vs post-2024 normalization

**Concern level: MEDIUM-LOW.**

2023 was still in the late phase of COVID-aftermath macroeconomic regime — heightened rate volatility (Selic 13.75% peak, BRL volatility under Brazilian central bank tightening cycle), sticky inflation, election aftermath (2022 Brazilian general election). 2024-Q4..2026 represents a different macro environment (lower Selic, post-election political calm, USD-BRL trend from different fundamental drivers).

End-of-day inventory unwind is theoretically a *structural* phenomenon (intraday-position-flat-at-close mechanic does not depend on macro regime). But empirically, the magnitude and timing of EOD unwind *can* shift with overnight risk premium, which in turn shifts with macro volatility regime. AFML §8.6 calibration of "exceptional" IC > 0.5 was developed against US-equities single-regime data; transferring that calibration across macro-regime boundaries in Brazilian futures is an open empirical question.

Practical impact: even if RLP and fee regimes are clean, the *magnitude* of the predictor may differ across macro regimes. K3 decay floor of 0.5 (or tightened to 0.7 per my Round 4 vote §2.3) was set against in-sample evidence from 2024-Q4..2026; applying the same floor to a 2023 OOS observation has no calibration anchor. Mira recommendation: **report observed K3 decay as evidence, do NOT apply pass/fail thresholds to the pre-2024 segment**. This is condition C-M-5 in §7.

### §2.5 Regime axis 4: 2024 exchange code change BMF→F (DLL behavior shift)

**Concern level: MEDIUM-HIGH (engineering, not statistical).**

Per Nelo channel knowledge (VESPERA-DATA-PIPELINE Turno 2) and ProfitDLL release notes, the WDO contract symbol/exchange code changed from BMF to F at some point in 2024. This is an *engineering* concern translating to a *statistical* concern:
- DLL response payload shape may differ pre/post the code change (different ticker normalization).
- Tick size, contract specifications: per cost atlas, tick=0.5 points, multiplier=10 USD/point — need confirmation these were stable across the transition (Nova/Nelo).
- Historical backfill via GetHistoryTrades may need DIFFERENT ticker queries for pre/post (e.g., "WDOFUT@BMF" pre-2024-Q? vs "WDOFUT@F" post). Dara/Nelo authority on the exact transition date.

If the DLL backfill produces *inconsistent* trade-record schemas across the BMF→F transition, the resulting parquet will have a regime-discontinuity that contaminates any cross-window analysis. **Nelo must confirm DLL backfill returns schema-identical data across the BMF→F transition** OR Dara must implement a normalization adapter that produces identical schema. This is condition C-M-1 in §7 (Dara authority).

### §2.6 Regime axis 5: Holiday calendar shifts

**Concern level: LOW.**

B3 calendar drifts year-to-year (Carnaval, Corpus Christi shift; banking holidays). Per Nova T002.0 calendar atlas, 2023 calendar exists in `config/calendar/2024-2027.yaml` only as forward extrapolation; pre-2024 calendar needs to be backfilled into the calendar YAML before any pre-2024 session can be processed. This is plumbing-level work (Dara authority); statistical impact is minimal IF properly done. Flagged for completeness but not blocking.

### §2.7 Synthesis on regime stationarity

| Axis | Concern | Authority | Resolution path |
|---|---|---|---|
| Cost atlas validity pre-2024 | HIGH | Riven | Atlas v0.x.x archival OR explicit "v1.0.0 OK" cosign |
| RLP regime 2023 vs 2024-Q4 | MEDIUM-HIGH | Nova | Microstructural adjudication |
| Macro regime (COVID aftermath) | MEDIUM-LOW | Mira | K3 decay floor not applied to pre-2024 segment |
| BMF→F exchange code transition | MEDIUM-HIGH | Nelo + Dara | DLL schema normalization |
| Holiday calendar pre-2024 | LOW | Dara | calendar.yaml backfill |

**Mira ML/statistical position:** all five axes can be resolved within the Squad's existing authority structure. None is a hard blocker. But each must be *explicitly* resolved before pre-2024 evidence is treated as OOS rather than as different-regime stress test. **Silent assumption that 2023-2024 regime equals 2024-Q4..2026 regime is the canonical Article IV violation here** — every regime-equivalence claim must trace to authoritative cosign, not to default presumption.

---

## §3 Hold-out virginity per strategy — virgin-by-availability vs virgin-by-discipline

### §3.1 The technical question

Quant R8 frames pre-2024 archival as "virgin status" if Sable audits. The question I (Mira) must adjudicate on ML/statistical authority is: does pre-2024 data qualify as **virgin** for H_next purposes when:

- T002 (and any prior epic) NEVER touched 2023 data (T002 in-sample 2024-08-22..2025-06-30; T002 hold-out 2025-07-01..2026-04-21; pre-2024 explicitly cut by Mira spec yaml v0.2.0 PRR-20260421-1 + v0.2.1 PRR-20260427-1 in-sample window narrowing).
- BUT the *reason* pre-2024 was cut was empirical data unavailability (per VESPERA-DATA-PIPELINE-2026-04-21 ADDENDUM: only 6 chunks Jan 2-9 2023 in DB; "Esses dados NÃO existem" in TimescaleDB Sentinel snapshot), NOT deliberate pre-registration as future hold-out.

### §3.2 The "virgin-by-availability vs virgin-by-discipline" distinction

The two conditions are statistically NOT equivalent:

- **Virgin-by-discipline (strict):** the data exists, the researcher has access, and the researcher commits via pre-registration to NOT use it for in-sample selection. This is the gold standard Anti-Article-IV Guard #3 spirit (data exists; researcher abstains; OOS observation is uncontaminated by selection).
- **Virgin-by-availability (weaker):** the data does not exist in the researcher's accessible dataset, so the researcher *cannot* use it for in-sample selection. This is statistically equivalent to virgin-by-discipline ONLY IF the researcher has not been *exposed to information about the data* through other channels (papers, news, third-party reports, broker conversations, etc.).

For T002 specifically, the squad's *prior* exposure to 2023 microstructure information through ambient channels is non-zero but bounded:
- T001 bar-close momentum dry-run *touched* the same DB Sentinel infrastructure (different time range) but did not run real strategy training (per user testimony: T001 was "smoke-test only").
- Prior literature on Brazilian futures end-of-day patterns (FGV/Insper microstructure-BR papers) is in the squad's awareness ambient — Mira/Nova citations to AFML §8.6 + Brazilian-futures research were available to the squad pre-T002.
- The predictor formula `−intraday_flow_direction` was Mira-derived from Lopez de Prado AFML §15 framework + Nova session-phases atlas; the formula is regime-agnostic by design (not 2024-fitted).

### §3.3 Mira adjudication

Pre-2024 (2023-Q1..2024-Q3) data **DOES qualify as virgin for H_next purposes** under the following compound criterion:

1. **Direct exposure check:** no prior T002/T003 trial has touched the pre-2024 window (verified by Mira spec yaml preregistration_revisions[] history — all PRRs cut window FORWARD from 2024-01 through 2024-08-22; pre-2024 was never read by any CPCV harness).
2. **Indirect exposure check:** the predictor formula was derived from theory + 2024-Q4+ in-sample selection, NOT from pre-2024 empirical examination. This is testable: if the formula were 2024-fitted-only, applying it to 2023 data should reveal high IC instability (potential FAIL of K3 decay on pre-2024 segment) — and that is itself a falsifiable test.
3. **Disclosure flag:** the squad's ambient awareness of Brazilian-futures literature is a *theoretical-prior* exposure, not empirical-sample exposure. AFML §15 calibration rests on US-equities; transfer to Brazilian-futures was a *hypothesis*, not an empirically-tuned-on-2023 prior.

**Subject to those three conditions, pre-2024 qualifies as virgin-by-discipline, not merely virgin-by-availability.**

### §3.4 What this DOES NOT authorize

This adjudication does NOT authorize:
- Treating pre-2024 evidence as STRONGER than forward-time evidence (forward-time is impossible-to-leak by construction; pre-2024 is virgin-by-discipline-with-caveats — strong but not strongest).
- Bypassing Sable's separate audit per Quant R8 — Sable retains separate authority on *procedural* virginity (commit hashes, file access logs, branch history). Mira authority is *statistical* virginity only.
- Applying pass/fail thresholds calibrated on 2024-Q4..2026 in-sample distribution to pre-2024 observation (per §2.4 — K3 decay floor calibration anchor not transferable across macro regimes).

---

## §4 Alternative: walk-forward expanding window — REJECT

Already adjudicated by Quant R9 (walk-forward REJECTED on Bonferroni grounds + researcher-observation contamination per Mira F2-T9 §3 strict reading). This Data Council does not re-open the question. **Walk-forward is NOT a viable alternative path for H_next OOS extension.**

For the record, the Bonferroni argument is unchanged: 4 rolling windows × 3 H_next candidates = 12 trials; n_trials_cumulative would jump from 8 to 17; DSR floor would inflate proportionally; 0.95 strict bar (or Bonferroni-adjusted ~1.005) becomes near-impossible to clear under good-edge scenario. **The same logic applies to pre-2024 archival IF run as multi-window walk-forward over 2023-Q1..2024-Q3** — single archival window observation OK; walk-forward archival NOT OK.

---

## §5 Cross-asset pollution risk

### §5.1 T001 overlap check

T001 (bar-close momentum dry-run, retired by user pre-T002) used the same DB Sentinel infrastructure as T002 — but per user testimony in autonomous session memory, T001 was "smoke-test only, no real model trained". Per VESPERA-DATA-PIPELINE Turno 2 + AUDIT-20260426-DB-CONTINUITY §3, the DB Sentinel snapshot covered 2024-01-02..2026-04-02 contiguously plus 6 isolated 2023 days; T001 did not extend coverage backward.

### §5.2 Mira adjudication on T001 pollution

**Pollution risk: LOW.**

- T001 used DB Sentinel for feature engineering smoke tests (features_1s table per VESPERA-DATA-PIPELINE Turno 2 / AUDIT-20260426 Q3) — but features_1s is a *derived* table, not the raw `trades` table. Pre-2024 raw trades data was never materialized into features_1s under T001 (features_1s in DB has 4834 MB total; if 2023 features had been computed they would show up in chunks).
- No T001 backtest produced model artifacts that would have been pre-trained on 2023 data.
- The squad's collective memory does not contain "T001 found pre-2024 result X" ambient knowledge that would constitute information leakage for H_next.

**T001 pollution not a blocker for Path A.** For prudence, Sable audit (Quant R8) should explicitly check: (a) git log of any commits touching pre-2024 data ranges; (b) features_1s row count by date for 2023-Q1..2024-Q3 (probably zero, but worth confirming); (c) any audit log of `feed_timescale.py` reads against pre-2024 data ranges. This is condition C-M-4 in §7.

---

## §6 IC=0.866 robustness verification opportunity

### §6.1 The unique informational value of Path A

This is the **strongest single argument FOR Path A as secondary channel**, complementing Path B forward-time:

- T002 Round 3.1 K3 PASS at decay ratio 0.99991 over 9-month IS + 10-month OOS is extraordinary by AFML §8.6 calibration (IC > 0.5 is "exceptional"; IC ~0.866 stable across windows is rarer). The natural research question is: **does this stability extend to a third independent window?**
- IF Path A produces IC over 2023-Q1..2024-Q3 in the range 0.7-0.9 with CI95_lower > 0 → STRONG cross-regime robustness evidence; the predictor is a structural Brazilian-futures EOD phenomenon, not a 2024-Q4 artifact.
- IF Path A produces IC dramatically lower (e.g., 0.2-0.4) → REVEALS that the predictor was a post-2024-Q4 regime artifact; T002 thesis was fitted to a specific microstructure regime that did not exist pre-2024. This would force retire of H_next predictor IP reuse argument and a fresh predictor derivation.
- IF Path A produces IC in middle range (0.4-0.7) → ambiguous; partial regime persistence; council escalation needed.

### §6.2 Why this informational value is uniquely high

Path B (forward-time) produces ONE OOS observation. Path A (pre-2024) produces a SECOND OOS observation along an orthogonal dimension (different historical regime, different fee schedule potentially, different RLP regime potentially). The two-observation evidence base is materially stronger than single-observation evidence even if both observations are individually moderate-confidence. This is the canonical bias-variance tradeoff in OOS validation: more independent observations beat single high-quality observation when the underlying distribution has unknown stability properties.

### §6.3 What this does NOT change

The §1 strict bar (DSR > 0.95, Bonferroni-adjusted to ~1.005 per Quant R3) remains UNMOVABLE on the PRIMARY (forward-time) channel. Path A is *informative* for inference about predictor robustness but does NOT relax the deployment threshold on Path B. If Path A passes DSR > 1.005 but Path B fails, we have evidence of a regime-bound edge — **deploy with regime-dependence guardrails (Riven authority on sizing) OR retire the strategy if guardrails are infeasible** — but we do NOT deploy on pre-2024 evidence alone.

---

## §7 Recommendation Mira — CONDITIONAL_APPROVE_PATH_A_WITH_REGIME_CHECK

### §7.1 Vote

**Path A (pre-2024 archival 2023-Q1..2024-Q3) is APPROVED as SECONDARY validation channel, conditional on the following pre-conditions all clearing.**

**Path B (forward-time 2026-05-01..2026-10-31) remains PRIMARY per Quant R7. This vote does NOT change Path B status.**

**Path C (no backfill; forward-time exclusive) is the FALLBACK if any of the §7.2 conditions cannot be met within reasonable squad bandwidth.**

### §7.2 Conditions for Path A approval (all must clear; AND-gated)

| Condition | Description | Authority |
|---|---|---|
| **C-M-1** | DLL backfill schema-consistent across BMF→F exchange-code transition; OR Dara normalization adapter produces unified schema. Spec yaml carries `dataset_pre_2024_sha256` distinct from in-sample/forward-time hashes. | Nelo + Dara |
| **C-M-2** | Nova microstructural cosign that 2023 RLP regime is sufficiently close to 2024-Q4..2026 regime for predictor `−intraday_flow_direction` to be apples-to-apples; OR Nova authors RLP regime caveat documented in spec yaml. | Nova |
| **C-M-3** | Cost atlas validity adjudicated: EITHER (i) Riven authors cost atlas v0.x.x calibrated for 2023 fee schedule, OR (ii) Riven cosigns explicit "v1.0.0 valid pre-2024 within tolerance" with delta documentation. Spec yaml references the applicable atlas per data segment. | Riven |
| **C-M-4** | Sable virginity audit per Quant R8: (a) git log of commits touching pre-2024 data ranges (expected: zero); (b) features_1s row count by date for 2023-Q1..2024-Q3 (expected: zero or low); (c) any T001 backtest log referencing pre-2024 data ranges (expected: none). | Sable |
| **C-M-5** | Mira regime-stationarity pre-test: compute summary stats (volatility, intraday volume profile, RLP-share-proxy, EOD-fade-magnitude) on 2023-Q1..2024-Q3 vs 2024-Q4..2026 in-sample; report stationarity test (e.g., Kolmogorov-Smirnov on per-event return distributions) BEFORE any DSR computation on pre-2024 segment. K3 decay pass/fail thresholds NOT applied to pre-2024 (per §2.4). | Mira |
| **C-M-6** | Sample-size projection confirmed adequate: total events on pre-2024 archival ≥ R9 floor 250 across CPCV harness (expected: ~1512 total events × 45 paths = 68 040 path-events; ≫ floor). | Mira |
| **C-M-7** | Calendar.yaml extended backward to cover 2023 sessions (Copom dates, holidays, rollover days). | Dara |

### §7.3 What approval looks like operationally

Conditional on §7.2 all clearing:
- New PRR-20260501-N entry in spec yaml H_next preregistration_revisions[] with the 8 schema fields per MANIFEST R15.2.
- Spec yaml `data_splits.archival_secondary_oos: 2023-01-01..2024-09-30` with `dataset_archival_sha256` registered.
- CPCV harness runs on Path B (forward-time, PRIMARY) and Path A (pre-2024, SECONDARY) separately; reports include both DSR observations.
- Council resolution at end of H_next cycle (Q3-Q4 2026) interprets jointly per §1.2 2×2 truth table.
- IF Path A fails C-M-1..C-M-7 within 2 weeks of council ratification, Path A defers to T003+ epic; Path B continues as exclusive PRIMARY.

### §7.4 What I would change my vote to

If the council surfaces evidence that:
- DLL backfill produces schema-inconsistent data across BMF→F transition AND Dara normalization is non-trivial (>1 week of engineering work) — vote shifts to PATH_C (defer Path A; forward-time exclusive for H_next; revisit Path A in T003+ epic when Dara has a normalization adapter).
- Cost atlas v0.x.x archival turns out to be infeasible (Riven cannot reconstruct 2023 fee schedule with confidence) AND v1.0.0 cosign is rejected — vote shifts to PATH_C (cost-layer artifact would contaminate the pre-2024 OOS signal).
- Nova microstructural review identifies a regime discontinuity in 2023 that disqualifies the predictor formula for that window (e.g., RLP regime in 2023 was so different that flow-direction signal carries different semantic content) — vote shifts to PATH_C with explicit Nova-blocked reasoning.
- Sample-size projection fails (e.g., pre-2024 archival has gaps that drop usable events below R9 floor under CPCV harness) — vote shifts to PATH_C.

Otherwise, the vote is CONDITIONAL_APPROVE_PATH_A as written.

---

## §8 Personal preference disclosure (Article IV honesty)

### §8.1 What I believe (with epistemic uncertainty)

ML-research instinct given my Round 4 vote 2026-05-01 + the data context:
- **High confidence (≥75%):** pre-2024 OOS evidence on the predictor (IC measurement, NOT DSR with cost layer) is genuinely informative. Predictor formula is theory-derived (AFML §15 + Nova session-phases atlas), not 2024-fitted; cross-regime testing is a clean robustness-of-theory test. K3 decay measurement on pre-2024 has high informational value regardless of the cost-layer decision.
- **Moderate confidence (~55-65%):** strategy-level (DSR-with-costs) evidence on pre-2024 is contaminated by cost-atlas validity boundary. Without C-M-3 resolved, I would NOT report DSR_pre_2024 numbers as comparable to DSR_forward_time numbers.
- **Moderate-to-high confidence (~70%):** pre-2024 IC will sustain in the range 0.6-0.85 (above K3 decay floor 0.5; below the 0.866 in-sample peak by some regime drift). This would be the *expected* outcome under the structural-EOD-fade hypothesis.
- **Low confidence (<25%):** pre-2024 IC dramatically collapses (e.g., below 0.3). This would be the surprise outcome and would force fresh predictor derivation.
- **Very low confidence (<15%):** pre-2024 DSR exceeds 1.005 strict bar. Cost layer is the binding constraint; the predictor was already costed-out at IC=0.866; pre-2024 evidence under unchanged cost layer would also be costed-out under any reasonable assumption.

### §8.2 What I want NOT to bias the vote

I am the ML/statistical author of:
- T002 spec yaml v0.2.x data_splits decision (which CUT pre-2024 from in-sample window — so pre-2024 was excluded by my own authorship).
- The "virgin-by-discipline vs virgin-by-availability" framework (which I am now applying to my own prior decision).
- Round 4 2026-05-01 vote that endorsed forward-time as PRIMARY hold-out (Quant R7).

I have authorial investment in (a) pre-2024 being usable as OOS (validates my cut-window decision as virgin-by-discipline rather than virgin-by-availability-only) AND (b) forward-time being PRIMARY (preserves my Round 4 vote). The two are not in tension — they are joint conditions in this vote.

To check it: I would still vote CONDITIONAL_APPROVE_PATH_A_WITH_REGIME_CHECK if a different ML-author had drafted T002 spec — because the *statistical* arguments for secondary-channel value (§6) and conditional approval (§7) do not depend on who authored the original cut. The vote is grounded in 2×2-evidence-base reasoning + regime-stationarity caveats + sample-size feasibility, all of which are independent of authorship.

### §8.3 Bias check on Path C fallback

I disclose that I would prefer Path A approved over Path A rejected — not because Path A is "better" but because the *information value* of two-observation OOS is higher than single-observation. This is a research-bias disclosure: an ML researcher tends to want more evidence axes, not fewer. To check it: I am offering a fallback to PATH_C in §7.4 with explicit triggers for downgrade; the vote is not "PATH_A at all costs". Conditional approval is the honest position.

---

## §9 Article IV self-audit (every clause traces; no invention)

| Claim category | Trace anchor |
|---|---|
| Pre-2024 sample-size ~6 quarters / ~378 sessions / ~1512 events / ~340k path-events | Nelo DLL 27-month limit (VESPERA-DATA-PIPELINE Turno 2) + Mira spec yaml v0.2.3 §15.3 entry windows + Quant R5 trial budget |
| R9 minimum floor 150-250 | ESC-011 R9 NON-NEGOTIABLE binding |
| DSR threshold ~1.005 under n_trials_cumulative=8 | Quant 2026-05-01 R3 |
| Bonferroni n_trials carry-forward 5 + new 3 = 8 cumulative | ESC-011 R9 + Quant R1 + Quant R5 |
| AFML §8.6 IC > 0.5 "exceptional" calibration | Lopez de Prado 2018 AFML §8.6 + Round 3.1 sign-off + my Round 4 vote §1.1 |
| Anti-Article-IV Guard #3 (hold-out untouched until preregistered unlock) | ESC-011 R3 + Mira spec yaml v0.2.3 §15.10 + Round 3.1 sign-off §6 |
| Anti-Article-IV Guard #4 (DSR > 0.95 thresholds UNMOVABLE) | ESC-011 R14 + Mira Gate 4b spec v1.2.0 §11.2 |
| Quant R6 (T002 hold-out 2025-07-01..2026-04-21 CONSUMED) | Quant 2026-05-01 resolution R6 |
| Quant R7 (forward-time virgin hold-out 2026-05-01..2026-10-31 PRIMARY) | Quant 2026-05-01 resolution R7 |
| Quant R8 (pre-2024 archival 2023-Q1..2024-Q3 OR conditional on Dara coverage + Sable virginity) | Quant 2026-05-01 resolution R8 |
| Quant R9 (walk-forward REJECTED on Bonferroni + researcher-observation grounds) | Quant 2026-05-01 resolution R9 + my F2-T9 §3 strict reading |
| 2023 = 6 chunks Jan 2-9 in DB Sentinel snapshot | AUDIT-20260426-DB-CONTINUITY §3 Q1 + Q2 (Dara empirical evidence) |
| 2024-2025-2026 contiguous coverage | AUDIT-20260426-DB-CONTINUITY §3 Q1 (251+250+63 chunks) |
| RLP intraday share 10-30%; tradeType=13 enum NOT in parquet trades-only | Nova vote 2026-05-01 §3 + cost atlas §brokerage notes line 167-168 + Nova features-availability matrix |
| Cost atlas v1.0.0 calibrated to 2024-08-22+ regime | Cost atlas v1.0.0 + ESC-012 user reframe (atlas FIXED from 2024-Q4 forward) |
| BMF→F exchange code transition 2024 | Nelo channel knowledge (VESPERA-DATA-PIPELINE Turno 2 DLL coverage) + ProfitDLL release notes domain |
| T001 retired pre-T002; smoke-test only | User testimony in autonomous session memory + T001 absence from features_1s pre-2024 (AUDIT-20260426 §3 implication) |
| MANIFEST R15.2 PRR schema 8 fields | MANIFEST §15 + my activation rule |
| Predictor formula `−intraday_flow_direction` at {16:55, 17:10, 17:25, 17:40} BRT | Mira spec yaml v0.2.3 §15.3 + F2-T5 Round 2 §3 + Round 3.1 evidence |

### §9.1 Article IV self-audit verdict

19 named anchors traced explicitly above. Every clause in §1-§8 maps to one of: T002 spec yaml v0.2.3, Mira Gate 4b spec v1.2.0, Round 3.1 sign-off, ESC-011/012/013 resolutions, Quant 2026-05-01 R6-R9, AFML / Bailey-LdP literature canon, Nova vote 2026-05-01, AUDIT-20260426 (Dara), VESPERA-DATA-PIPELINE 2026-04-21 (Nelo), MANIFEST §15.

NO INVENTION:
- No new statistical method invented. Conditional-approval-with-regime-check is standard ML-research discipline (sub-group analysis + stationarity testing + caveat reporting).
- No threshold mutations. K1 strict 0.95 / Bonferroni-adjusted 1.005 referenced AS-IS. K3 decay floor 0.5 referenced AS-IS; explicitly NOT applied to pre-2024 segment per §2.4 calibration-anchor argument.
- No data touched. This ballot does NOT read any pre-2024 data, does NOT read pre-2024 archival CPCV results, does NOT read any DLL backfill empirical output. It is a *pre-empirical disposition rule* in the canonical PRR pattern (per Pax PRR-20260430-1 precedent + my activation rule).
- No source code modification. No spec yaml mutation. No spec markdown mutation. No prior sign-off mutation.
- No reading of any other DATA Council ballot prior to authoring this ballot. Verified by ballot independence at branch main as of council date 2026-05-01.

NO PUSH performed (Article II — Gage @devops EXCLUSIVE authority preserved; this ballot is write-only under MY authority, no `git add` / `git commit` / `git push` invoked per user prompt directive).

---

## §10 Mira cosign 2026-05-01 BRT — Data Council ML ballot

```
Author: Mira (@ml-researcher) — ML/statistical authority on this council; adjudicator of "virgin-by-discipline vs virgin-by-availability"
Council: Data Acquisition Council 2026-05-01 (DLL backfill / pre-2024 archival viability)
Topic: Pre-2024 archival window 2023-Q1..2024-Q3 as OOS extension for H_next; Path A / Path B / Path C adjudication
Constraint binding: Quant Council 2026-05-01 R6/R7/R8/R9 + cost atlas v1.0.0 FIXED + Bonferroni n_trials_cumulative=8 + Anti-Article-IV Guards #1-#9

Vote: CONDITIONAL_APPROVE_PATH_A_WITH_REGIME_CHECK_AND_PRIMARY_FORWARD_TIME
  PATH_A (pre-2024 archival 2023-Q1..2024-Q3): SECONDARY validation channel, NEVER PRIMARY
  PATH_B (forward-time 2026-05-01..2026-10-31): PRIMARY — UNCHANGED per Quant R7
  PATH_C (no backfill; forward-time exclusive): FALLBACK if §7.2 conditions cannot clear within 2 weeks

§1 Statistical implications: sample-size headroom ~1361× over R9 floor; Bonferroni-adjusted DSR ~1.005 threshold remains binding; 2×2 truth table (Path A × Path B) provides materially stronger inference than single-window
§2 Regime stationarity (CRITICAL): 5 regime axes — cost atlas validity (HIGH; Riven C-M-3); RLP regime (MED-HIGH; Nova C-M-2); macro/COVID (MED-LOW; Mira C-M-5); BMF→F transition (MED-HIGH; Nelo+Dara C-M-1); calendar (LOW; Dara C-M-7). Silent assumption of regime equivalence is canonical Article IV violation
§3 Hold-out virginity: pre-2024 qualifies VIRGIN-BY-DISCIPLINE under three-criterion compound (no direct exposure + no indirect empirical exposure + theoretical-prior-only ambient awareness); subject to Sable independent procedural audit per Quant R8
§4 Walk-forward REJECTED (Quant R9 binding; not re-opened)
§5 T001 cross-asset pollution: LOW risk; smoke-test only; Sable C-M-4 confirms via git log + features_1s 2023 row check
§6 IC=0.866 robustness verification: STRONGEST single argument FOR Path A as secondary channel; two-observation OOS materially stronger than single-observation
§7 Conditions for approval (AND-gated): C-M-1 DLL schema (Nelo+Dara) + C-M-2 RLP regime cosign (Nova) + C-M-3 cost atlas validity (Riven) + C-M-4 Sable virginity audit + C-M-5 Mira regime-stationarity pre-test + C-M-6 sample-size projection + C-M-7 calendar.yaml backfill
§8 Personal preference disclosure: predictor cross-regime test informational value high (≥75% conf); strategy-level DSR pre-2024 contaminated without C-M-3; bias check via fallback to PATH_C with explicit triggers
§9 Article IV self-audit: 19+ trace anchors (Quant 2026-05-01 R6-R9 + ESC-011/012/013 + Round 3.1 + Mira Gate 4b spec + AUDIT-20260426 Dara + VESPERA-DATA-PIPELINE Nelo + Nova 2026-05-01 + AFML/Bailey-LdP + MANIFEST §15); NO invention; NO threshold mutation; NO pre-2024 data touched by THIS ballot; NO push; NO source code modification; NO spec yaml/markdown mutation; NO reading of other DATA Council ballots prior to authoring

Independence: ballot authored without reading Dara, Sable, Nelo, Nova, Riven DATA Council ballots
Article II: NO push performed by Mira during this ballot. Gage @devops authority preserved (per user prompt: "NÃO commit. NÃO push.")
Article III (Story-Driven): this is a council ballot artifact, not a story implementation; lifecycle outside SDC scope per ESC-011/012/013 + DATA Council ratification format precedent
Anti-Article-IV Guards: #1-#9 ALL honored verbatim; Guard #3 (hold-out untouched until preregistered unlock) honored by §3 virgin-by-discipline adjudication + §7 PRR-required-pre-Path-A-execution; Guard #4 (DSR > 0.95 UNMOVABLE) honored verbatim under Bonferroni-adjusted 1.005
Authority boundary: Mira issues this ballot on ML/statistical grounds; does NOT pre-empt Sable procedural virginity audit (C-M-4); does NOT pre-empt Nelo+Dara DLL schema engineering (C-M-1); does NOT pre-empt Nova RLP regime adjudication (C-M-2); does NOT pre-empt Riven cost atlas archival adjudication (C-M-3); does NOT pre-empt Pax forward-research disposition (story sequencing if Path A approved)

Cross-reference:
  Quant Council 2026-05-01 resolution: docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md (R6/R7/R8/R9)
  Mira Round 4 ballot: docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-mira-vote.md
  AUDIT-20260426-DB-CONTINUITY (Dara empirical evidence): docs/audits/AUDIT-20260426-DB-CONTINUITY.md
  VESPERA-DATA-PIPELINE-2026-04-21 (Nelo DLL constraints): docs/councils/VESPERA-DATA-PIPELINE-2026-04-21.md
  Round 3.1 sign-off (predictor IP K3 PASS): docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md
  Cost atlas v1.0.0 FIXED (ESC-012 user reframe): docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md
  MANIFEST R15.2 spec versioning: MANIFEST §15
  Anti-Article-IV Guards #1-#9: ESC-011 / ESC-012 / ESC-013 resolutions

Cosign: Mira @ml-researcher 2026-05-01 BRT — Data Acquisition Council ML ballot — pre-2024 archival CONDITIONAL APPROVE as SECONDARY channel; forward-time PRIMARY unchanged; 7 conditions AND-gated for Path A activation; PATH_C fallback if conditions fail.
```

— Mira, mapeando o sinal 🗺️
