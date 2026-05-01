---
council_id: QUANT-2026-05-01-ALPHA-DISCOVERY
topic: H_next alpha discovery direction post T002 retire (Round 3.1 costed_out_edge_oos_confirmed_K3_passed)
voter: Riven (@risk-manager)
voter_role: Risk Manager & Capital Gatekeeper — Quarter-Kelly REGRA ABSOLUTA + §11.5 capital-ramp pre-conditions custodial monopoly + Gate 5 dual-sign disarm authority + 3-bucket post-mortem authoring authority
date_brt: 2026-05-01
voter_authority: |
  ESC-011 R7 + R20 carry-forward + ESC-012 R10/R11 carry-forward + ESC-013 R10/R11 carry-forward
  + Mira spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 (Riven 3-bucket reclassification authority)
  + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority
  + §11.5 capital-ramp pre-conditions §1..§7 custodial monopoly
  + Riven persona REGRA ABSOLUTA (quarter-Kelly cap 0.25 × f* + sizing-deferred + paper-mode pre-condition + haircut 30-50% first 3 months live)
mandate: |
  RISK PERIMETER adjudication of H_next alpha discovery direction. Vote independent — no peer ballots
  consulted pre-vote per council protocol. Post T002 retire (Round 3.1 final fail), Phase G hold-out
  CONSUMED under H_T002, Bonferroni n_trials=5 monotonic carry-forward, §11.5 pre-conditions reset to
  unsatisfied for H_next, Gate 5 LOCKED PERMANENTLY for T002 (UNMOVABLE per Anti-Article-IV Guard #4).
inputs_consulted:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md (Round 3.1 FINAL FAIL costed_out_edge_oos_confirmed_K3_passed)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md (5/6 Path B + Riven Path C minority)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md (5/5 Path IV protocol-correction)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-riven-vote.md (own ESC-012 ballot — Path C minority §1.2 Leg 1-3)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-T002-phase-g-protocol-gap-riven-vote.md (own ESC-013 ballot — Path IV §2 Bayesian update)
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md (3-bucket framework + §3 dependency tree + §5 anti-pattern catalog §5.1-§5.9)
inputs_NOT_consulted_pre_vote: peer voter ballots (Mira / Pax / Beckett / Aria / Kira / Sable / Dara)
verdict_summary: |
  §1: Risk lens veto-screen on candidate H_next directions — overnight gap STRONG REJECT (gap variance
  unbounded under regime breaks; quarter-Kelly substrate not parametrizable); VPIN/microstructure
  CONDITIONAL ACCEPT (only with ProfitDLL book-snapshot wiring delivered + bucket-A re-clearance);
  asymmetric exit DEFERRED (DD profile change requires fresh Beckett distribution before any sizing
  envelope); multi-timeframe regime filter ACCEPT with #8 capture-rate floor; conviction-conditional
  sizing CONDITIONAL ACCEPT (concentration risk requires tighter haircut + per-bucket position cap).
  §2: Carry-forward §11.5 #1-#7 verbatim PLUS NEW #8 capture-rate ≥ 0.6 of theoretical Sharpe AND
  NEW #9 OOS-stationarity check (DSR_OOS within ±0.10 of DSR_IS) AND NEW #10 PnL-vs-IC alignment
  (avoid Round 3.1 IC-rich-PnL-poor signature recurrence).
  §3: H_next OOS budget — REJECT walk-forward rolling (contamination); REJECT reserve-from-existing-IS
  (Bonferroni n_trials inflation + already-observed-tape contamination); ACCEPT forward 2026-05+
  fresh tape ≥ 6 months calendar-locked virgin pre-registration. Riven preference: forward virgin
  hold-out single-shot, identical lock discipline as T002 had.
  §4: 3-bucket post-mortem v4 NEW buckets — `ic_pnl_misalignment` (IC strong + PnL costed-out
  signature) NEW Round 3.1 lesson; `gap_variance_unbounded` (overnight strategies); `book_snapshot_dependency`
  (microstructure strategies); `regime_filter_overfit` (multi-timeframe filters).
  §5: Quarter-Kelly REGRA ABSOLUTA preserved INTACT. Capture rate ≥ 0.6 of theoretical Sharpe FLOOR
  for sizing > 0. Haircut 30-50% first 3 months live PRESERVED. New: per-bucket position cap when
  conviction-conditional sizing in scope.
  §6: Personal preference — multi-timeframe regime filter (lowest variance shift; cleanest §11.5
  re-instantiation) PREFERRED; VPIN microstructure ACCEPT IF book wiring lands first.
  §7: Article IV self-audit verbatim.
oos_budget_status_post_vote: T002 hold-out [2025-07-01, 2026-04-21] CONSUMED under H_T002 (Round 3.1 binding); H_next requires fresh forward virgin window (preferred) or strict pre-registration discipline on alternative.
quarter_kelly_status_post_vote: PRESERVED INTACT (no sizing exercise authorized; quarter-Kelly cap inviolate per Riven REGRA ABSOLUTA; haircut 30-50% first 3 months live preserved as default for any future H_next-PASS).
gate_5_status_post_vote: LOCKED PERMANENTLY for T002 (UNMOVABLE per Anti-Article-IV Guard #4); fresh dependency tree required for H_next (no inheritance).
---

# QUANT 2026-05-01 — H_next Alpha Discovery Riven Vote (Risk Perimeter Adjudication)

> **Voter:** Riven (@risk-manager) — Risk Manager & Capital Gatekeeper.
> **Authority basis:** ESC-011 R7 + R20 + ESC-012 R10/R11 + ESC-013 R10/R11 cumulative carry-forward + Mira spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 (Riven 3-bucket reclassification authority) + §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp custodial monopoly + Riven persona REGRA ABSOLUTA (quarter-Kelly + sizing-deferred + paper-mode pre-condition + haircut).
> **Mandate:** Adjudicate H_next alpha discovery direction from RISK PERIMETER perspective only. Pax retains scope authority; Mira retains statistical authority; Kira retains scientific peer-review authority; Beckett retains simulation realism authority; Aria retains architecture authority. Riven's vote concerns ONLY (a) which candidate hypotheses pass the §11.5 + Quarter-Kelly + sizing-deferred + paper-mode fence; (b) what new pre-conditions are needed; (c) what OOS budget topology is risk-clean; (d) what new buckets/anti-patterns are needed in the post-mortem catalog v4; (e) what sizing posture the next epic inherits.

---

## §1 Risk-side veto screen on candidate H_next directions

Five candidate directions surfaced by other voters in pre-council framing. Risk-side custodial screen evaluates each against: (a) does it satisfy §11.5 #1-#7 cumulative pre-conditions when re-instantiated? (b) is its return distribution Quarter-Kelly parametrizable cleanly (μ/σ² well-defined; tails not unbounded)? (c) does it inherit the Round 3.1 `costed_out_edge_oos_confirmed_K3_passed` lesson cleanly (avoid IC-rich-PnL-poor signature)? (d) what is the per-trade variance and sizing concentration profile?

### §1.1 Candidate evaluation matrix

| Candidate | μ/σ² parametrizable? | Tail risk profile | §11.5 cleanly re-instantiable? | Round 3.1 lesson absorption | Risk verdict |
|---|---|---|---|---|---|
| **(A) Conviction-conditional sizing (variable size by signal strength)** | CONDITIONAL — fewer trades larger size raises per-trade variance σ²; Kelly fraction f* inflates mechanically but tails widen | CONCENTRATION — fewer larger trades = single-trade DD becomes larger fraction of daily budget; σ_per_trade up; SL absolute size up | YES at framework layer; tighter at #5 (Riven Gate 5 cosign concentration pre-check needed) | NEUTRAL — does not address IC-rich-PnL-poor signature directly; orthogonal | **CONDITIONAL ACCEPT** with explicit per-bucket concentration cap §5.2 |
| **(B) Multi-timeframe regime filter (variable trade frequency)** | YES — same per-trade label/predictor; filter only gates entry; μ/σ² estimated per regime-bucket | REGIME-DEPENDENT — variable frequency means variable capital deployment per session; needs capacity floor or trade-count discipline | YES cleanly; Mira spec amendment needed for regime-bucket DSR/PBO accounting | DIRECTLY ABSORBS — filter could remove cost-erosion regime bucket where T002 lost edge OOS | **ACCEPT** with NEW §11.5 #8 capture-rate floor + §11.5 #9 OOS-stationarity-check |
| **(C) Asymmetric exit (winners run / losers cut tight)** | CONDITIONAL — μ shifts up under proper trailing; σ² distribution becomes right-skewed (heavier upside tail); DD distribution changes shape (Beckett re-run mandatory) | DD PROFILE CHANGES — max-DD potentially worse if losers-cut aggressive AND winners give back; needs full Beckett N-prime re-distribution before sizing envelope | NO immediately — bucket-A re-clearance needed (engine_config / exit logic mutation = new spec yaml + factory re-wiring); §11.5 #1 not pre-cleared | INDIRECTLY ABSORBS — but introduces NEW concern (give-back risk on winners) | **DEFERRED** until fresh Beckett N-prime distribution + bucket-A re-clearance |
| **(D) Different label (overnight horizon, e.g., 17:55 → next-09:30 close)** | NO — overnight gap variance is regime-conditional (FOMC / Copom / weekend / earnings season) and tails are heavy / unbounded under structural breaks; μ/σ² point estimates from CPCV understate tail | UNBOUNDED — gap variance under regime breaks (overnight Fed surprise; BCB Copom; weekend macro) cannot be sized via Kelly; quarter-Kelly substrate not parametrizable cleanly | NO — overnight margin requirement (B3 overnight margin per contract) different from day-trade; #1 (margin parametrization) requires Nova [TO-VERIFY] re-survey; bucket-A engine config different (no end-of-day flatten) | NEGATIVE — overnight introduces orthogonal new failure modes (gap risk, margin call risk overnight) without addressing Round 3.1 lesson | **STRONG REJECT** — gap risk unbounded; quarter-Kelly substrate not parametrizable; persona REGRA ABSOLUTA "em dúvida, reduzo" → reject |
| **(E) VPIN / microstructure (book-imbalance, queue position, order-flow toxicity)** | YES IF book snapshot data wired; NO if trades-only (current Beckett constraint per Round 3.1 caveat) | DEPENDS on book wiring — with book snapshots: tight per-trade σ²; without: substrate unparametrizable | NO immediately — bucket-A re-clearance needed (ProfitDLL book-snapshot integration; new feature engineering); §11.5 #1 (engineering wiring) requires new Mira Gate 4a sign-off | DIRECTLY ABSORBS — microstructure features potentially explain cost-erosion (queue position determines fill quality which is the core Round 3.1 IC-rich-PnL-poor signature root cause) | **CONDITIONAL ACCEPT** — only after ProfitDLL book-snapshot wiring delivered (Tiago/Nelo/Aria scope) AND bucket-A re-clearance (Mira Gate 4a) |

### §1.2 Risk-side preference ranking under Quarter-Kelly + §11.5 + paper-mode pre-condition fence

1. **(B) Multi-timeframe regime filter** — cleanest §11.5 re-instantiation (no spec yaml mutation; framework-layer filter); μ/σ² parametrizable per regime-bucket; DIRECTLY ABSORBS Round 3.1 lesson via cost-erosion regime exclusion; lowest engineering risk.
2. **(E) VPIN/microstructure** — DIRECTLY ABSORBS Round 3.1 root cause (queue position = fill quality = cost erosion mechanism); BUT requires book-snapshot wiring delivery first (Tiago/Nelo); CONDITIONAL ACCEPT pending bucket-A re-clearance.
3. **(A) Conviction-conditional sizing** — orthogonal to Round 3.1 lesson; introduces concentration risk; ACCEPT only with explicit per-bucket cap.
4. **(C) Asymmetric exit** — DEFERRED until fresh Beckett distribution; bucket-A re-clearance prerequisite.
5. **(D) Overnight horizon** — STRONG REJECT (gap variance unbounded; not Quarter-Kelly parametrizable; introduces orthogonal new failure modes).

### §1.3 Composite preference

If council adopts a single H_next direction: **(B) Multi-timeframe regime filter** primary, with (E) VPIN/microstructure as deferred-companion if book-snapshot wiring lands within 4-6 weeks. Composite is risk-clean because (B) frames the strategy at a layer ABOVE the cost-erosion mechanism (filter-out vulnerable regime buckets) while (E) addresses it BELOW (queue-position-aware fill model). Both share predictor↔label semantics that survive the Round 3.1 IC-rich-PnL-poor signature absorption test (regime filter excludes the cost-erosion regime; microstructure prices in queue/book toxicity which IS the cost-erosion mechanism).

---

## §2 New §11.5 capital-ramp pre-conditions for H_next

§11.5 cumulative pre-conditions §1..§7 from `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 dependency tree + §4.4 + §6 anti-pattern catalog. Round 1 (wiring gap, T002.0g harness), Round 2 (costed_out at K1 strict bar), Round 3.1 (OOS-confirmed costed_out with K3 PASS) lessons each contributed binding conditions. For H_next:

### §2.1 Carry-forward §11.5 #1-#7 verbatim

All seven existing pre-conditions remain binding for H_next:

| # | Pre-condition (verbatim) | Carry-forward status | Notes |
|---|---|---|---|
| **1** | Bucket A `engineering_wiring` HARNESS_PASS sign-off (Mira Gate 4a authority) | CARRY-FORWARD; reset to unsatisfied for H_next | New bucket-A clearance required for H_next implementation; Quinn 8-point gate retained; Sable §15.x sign-off chain enumeration discipline (ESC-013 §3 corrective action) carries-forward verbatim |
| **2** | Bucket B `strategy_edge` GATE_4_PASS sign-off over real WDO tape | CARRY-FORWARD; reset to unsatisfied for H_next | K1 (DSR>0.95) UNMOVABLE per Anti-Article-IV Guard #4; K2 (PBO<0.5) UNMOVABLE; K3 (IC>0 with CI95 lower>0) UNMOVABLE; joint conjunction strict |
| **3** | Bucket C `paper_mode_audit` PAPER_AUDIT_PASS ≥ 5 sessions | CARRY-FORWARD; reset to unsatisfied for H_next | Tiago execution telemetry + post-trade attribution (slippage real vs Beckett; latency real vs DMA2 default; fill rate) MUST be running and clean ≥ 5 sessions before any sizing > 0 |
| **4** | Mira independent Gate 5 cosign (DSR > 0.95 + PBO < 0.5 + IC decay over real PnL) | CARRY-FORWARD | Independence preserved; Mira retains verdict-issuing authority; Riven cannot pre-empt Mira; Mira cannot pre-empt Riven (dual-sign) |
| **5** | Riven independent Gate 5 cosign (Riven §9 HOLD #2 disarm authority) | CARRY-FORWARD | Single-leg fire = automatic REJECT preserved; concentration risk pre-check NEW for any H_next with conviction-conditional sizing in scope |
| **6** | Toy benchmark E6 discriminator preservation (Bailey-LdP 2014 §3 — Quinn QA authority per ESC-011 R12) | CARRY-FORWARD | Harness-correctness witness inheritable as bucket-A historical reference for H_next |
| **7** | Synthetic-vs-real-tape attribution audit (post-mortem authoring; ESC-011 R7 + R20) | CARRY-FORWARD | Round 4+ entries to be appended for H_next iterations; Riven authoring authority |

### §2.2 NEW §11.5 #8 — Capture-rate ≥ 0.6 of theoretical Sharpe (post-cost vs pre-cost)

**Mandate:** Before any sizing exercise > 0 for H_next, Beckett N-prime distribution MUST produce a capture-rate metric defined as:
```
capture_rate := sharpe_post_cost_post_friction / sharpe_pre_cost_pre_friction
```
where `sharpe_pre_cost_pre_friction` is computed under engine_config with cost atlas zeroed and slippage zeroed (idealized fill at signal price), and `sharpe_post_cost_post_friction` is the standard CPCV-distribution Sharpe under full cost atlas + slippage + latency_dma2_profile + RLP/microstructure flags identical to F2/T002 specifications. Capture rate FLOOR: **0.6**. Below 0.6: H_next is at risk of Round 3.1 `costed_out_edge` repeat signature; sizing-deferred MANDATORY. Above 0.6: capture rate is a leading indicator that the strategy has structural slack against cost erosion before OOS confirmation.

**Rationale:** Round 3.1 final fail signature was IC=0.866 cross-window robust BUT realized PnL costed-out (sharpe_mean -0.053 OOS, hit_rate 0.472 sub-50%, profit_factor 0.929 LOSING money OOS gross-of-deployment). The IC predicted the rank-correlation but the cost+friction layer ate the deployable Sharpe. A capture-rate floor surfaces this risk EARLY in the sign-off chain (bucket-A or bucket-B layer, not waiting for OOS to discover). Capture rate 0.6 floor is consistent with industry benchmark for slippage-tolerant retail-algo strategies (López de Prado AFML §13 transaction-cost-adjusted Sharpe; Bailey-LdP 2014 §6 deployment robustness).

**Source artifact:** Mira spec v1.3.0 §15.x amendment NEW (post-Mira approval); Beckett harness emits `capture_rate` field in `full_report.json` for any H_next CPCV run.

**Enforcement:** Quinn 8-point gate Check 9 NEW: capture_rate ≥ 0.6 PASS, < 0.6 surface to Riven for sizing-deferred determination. Cannot bypass for H_next.

### §2.3 NEW §11.5 #9 — OOS-stationarity check (DSR_OOS within ±0.10 of DSR_IS)

**Mandate:** After H_next Phase G (or equivalent virgin OOS test) executes, the observed |DSR_OOS - DSR_IS| MUST be ≤ 0.10 for the OOS confirmation to count as deployment-eligible (in addition to K1+K2+K3 strict PASS conjunction). If |DSR_OOS - DSR_IS| > 0.10, the strategy is flagged **regime-instability** and capital ramp is DEFERRED pending fresh-tape multi-window confirmation.

**Rationale:** Round 3.1 N8.2 produced DSR_OOS=0.205731 vs DSR_IS=0.766987 — a |Δ|=0.561 gap, which would have failed the ≤0.10 stationarity check by 5.6× the tolerance. This catastrophic IS↔OOS DSR divergence is itself a diagnostic signature that the IS distribution did not generalize, even when K3 IC decay PASSED (cross-window predictor↔label rank-stability preserved). The stationarity check surfaces this kind of mismatch as a deployment-veto signal independent of the joint-conjunction strict bar. This is risk-side custodial discipline against deploying strategies whose IS and OOS look different enough that the per-trade σ² estimates used for Quarter-Kelly sizing become unreliable.

**Source artifact:** Mira spec v1.3.0 §15.x amendment NEW (post-Mira approval); Beckett harness emits IS+OOS Sharpe distributions from same engine_config side-by-side; Mira verdict layer adds `dsr_stationarity_check` field with `pass/fail` + delta magnitude.

**Enforcement:** Mira Gate 4b verdict layer (existing code path; small amendment). Quinn 8-point gate Check 10 NEW: DSR stationarity ≤ 0.10. Riven Gate 5 cosign blocks sizing > 0 if check FAILS regardless of K1/K2/K3 outcome.

### §2.4 NEW §11.5 #10 — PnL-vs-IC alignment check (avoid IC-rich-PnL-poor recurrence)

**Mandate:** Beckett N-prime distribution for H_next MUST emit a `pnl_ic_alignment_score` defined as:
```
pnl_ic_alignment_score := correlation(per_path_realized_PnL, per_path_IC)
```
across CPCV 45 paths (or whatever path count config v0.2.3 inherits). Score MUST be ≥ 0.30 (positive correlation between IC magnitude and realized PnL across paths). Score < 0.30: strategy exhibits **Round 3.1 signature** (IC-rich predictor↔label rank-stability NOT translating to realized PnL) and is flagged for risk-side review before any sizing.

**Rationale:** Round 3.1 final FAIL was characterized by IC ≈ 0.866 cross-window stable BUT per-path PnL distribution costed-out OOS (sharpe_mean negative). The DIAGNOSTIC was that the IC-PnL correlation across paths was weak — IC predicted ordering but cost+friction ate the realized PnL signal. A direct cross-check (correlation of per-path PnL and per-path IC) would have surfaced this risk earlier in the sign-off chain. This is a NEW diagnostic specifically born of Round 3.1 lesson (Round 1 wiring gap and Round 2 costed-out had different dominant signatures).

**Source artifact:** Mira spec v1.3.0 §15.x amendment NEW; Beckett harness already has per-path IC and per-path Sharpe — addition is a single correlation computation across the 45 paths.

**Enforcement:** Quinn 8-point gate Check 11 NEW. Mira Gate 4b verdict layer adds `pnl_ic_alignment` field. Riven Gate 5 cosign uses this as a deployment-veto signal alongside K1/K2/K3.

### §2.5 Tighter, looser, or same vs T002?

Net effect: **TIGHTER on three new dimensions (capture rate, stationarity, PnL-IC alignment) — NO LOOSENING on any existing dimension**. K1/K2/K3 strict bars UNMOVABLE per Anti-Article-IV Guard #4 carry forward verbatim. Bonferroni n_trials cumulative (n=5 carry-forward at α/n=0.002) preserved monotonically; H_next inherits the n=5 Bonferroni budget consumed and any new trial increments cumulatively (Mira spec §15.10 + ESC-011 R9 verbatim discipline). Riven persona REGRA ABSOLUTA inviolate: quarter-Kelly cap 0.25 × f* + sizing-deferred + paper-mode pre-condition + haircut 30-50% first 3 months live ALL preserved.

The three new pre-conditions (#8 capture rate, #9 stationarity, #10 PnL-IC alignment) are LESSONS-LEARNED from Round 3.1 specifically and address the dominant `costed_out_edge_oos_confirmed_K3_passed` failure mode. They are TIGHTER because they introduce new fail-paths that were not previously enforced; they do NOT relax any existing strict bar.

---

## §3 H_next OOS budget topology — risk-side preference

T002 hold-out window [2025-07-01, 2026-04-21] is CONSUMED under H_T002 (Round 3.1 binding per ESC-013 R9 single-shot discipline; one-shot at K3 decay metric layer; Mira authoritative reading). H_next cannot inherit this window. Three options surfaced in pre-council framing:

### §3.1 Option (i) — Reserve forward 2026-05+ live data as fresh virgin hold-out

**Mechanics:** Pax pre-registers H_next predictor↔label spec + 4-branch disposition rule (PRR-style) BEFORE any forward-2026-05+ data is ingested. Spec-yaml-pinned. Hold-out window e.g., [2026-05-01, 2026-12-31] virgin under Anti-Article-IV Guard #3 mechanics identical to T002 (`_holdout_lock.py` pinned; `assert_holdout_safe` enforced at all call sites; per-line manifest provenance recording on unlock).

**Risk-side evaluation:** STRONGEST OOS evidence. Calendar-locked virgin window cannot be contaminated by researcher exposure; predictor↔label spec hash-frozen pre-data. Single-shot binding identical to T002 successful methodology (the one part of T002 governance that worked correctly was the OOS lock discipline; H_next inherits this verbatim).

**Quarter-Kelly timeline impact:** Forward 6-9 months calendar wait for sufficient sample (~150-220 trading sessions, similar to T002 hold-out cardinality). Sizing-deferred period is LONG but disciplined.

### §3.2 Option (ii) — Walk-forward rolling validation

**Mechanics:** Slide a window forward through 2024-08+ data; re-fit per window; evaluate next window OOS.

**Risk-side evaluation:** **REJECT** for risk-side custodial reasons. Walk-forward rolling on already-observed tape is structurally exposed to:
- Researcher-observation contamination (every window has been seen in some prior context — by Beckett N6/N6+/N7-prime/N8/N8.1/N8.2 runs; by Mira Round 1/2/3/3.1 verdict layer scrutiny; by post-mortem authoring).
- Implicit hyperparameter selection bias (window length, fold structure, re-fit cadence are all decisions made AFTER seeing the data).
- Bonferroni n_trials inflation (each rolling-window evaluation is a fresh trial under multiple-testing accounting; n_trials carries over from current 5 → could rapidly inflate).
- Anti-Article-IV Guard #3 violation under strict reading (the spirit of the hold-out lock is virgin OOS; rolling-window-on-observed-tape is not virgin).

### §3.3 Option (iii) — Reserve from existing IS

**Mechanics:** Carve a sub-window out of the existing 2024-08-22..2025-06-30 IS and treat it as OOS for H_next.

**Risk-side evaluation:** **REJECT** for the same researcher-observation contamination reason as (ii), AGGRAVATED. The existing IS has been:
- Used for predictor engineering (T002 feature design).
- Used for Bonferroni n_trials accumulation (T1..T5 cumulative).
- Exposed to Mira CPCV PASS/FAIL adjudication 4 times (Round 1, Round 2, Round 3, Round 3.1).

Carving a sub-window does not produce virgin tape; it produces a sub-window of contaminated tape with selection bias on which sub-window is chosen. Risk-side veto.

### §3.4 Risk-side preference: Option (i) — forward virgin hold-out

**Strongest OOS evidence within Quarter-Kelly timeline discipline.** The Quarter-Kelly REGRA ABSOLUTA does not impose calendar pressure — it imposes a strict cap once sizing > 0 is authorized. The waiting period for sufficient virgin forward-window cardinality is not a Quarter-Kelly violation; it is the standard sizing-deferred discipline applied at appropriate temporal granularity.

**Concrete proposal:** Pax pre-registers H_next spec + 4-branch disposition rule BEFORE 2026-05-01 data is ingested into Beckett harness. Hold-out window [2026-05-01, 2026-10-31] (~6 months calendar; ~125 trading sessions; floor cardinality preserved per Mira spec §6 sample-size rules — Bonferroni-adjusted at carry-forward n=5 + any new H_next trials accumulating). Per-line manifest provenance lock identical to T002 mechanics. Single-shot binding at K3 decay metric layer (Mira spec §15.13.7 carry-forward).

**Counter-veto note:** If H_next requires longer evaluation window for sample-size discipline (e.g., for low-frequency strategies with < 1 trade per session), the hold-out window extends accordingly (e.g., 2026-05-01..2026-12-31 = ~9 months calendar). Risk-side accepts this calendar cost as the price of clean OOS evidence.

---

## §4 3-bucket post-mortem v4 carry-forward + new buckets/anti-patterns

The 3-bucket post-mortem framework (`docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`) carries forward verbatim for H_next. Round 1 (wiring gap), Round 2 (costed_out_in_sample_K1_strict_fail), Round 3 (INCONCLUSIVE protocol-compliance gap), Round 3.1 (`costed_out_edge_oos_confirmed_K3_passed` final). New buckets and anti-patterns proposed for H_next absorption:

### §4.1 New bucket sub-classifications expected for H_next

| Bucket | Sub-classification (NEW) | Trigger signature | Lesson source |
|---|---|---|---|
| `engineering_wiring` | `book_snapshot_dependency` | Strategy depends on book state but ProfitDLL book-snapshot wiring incomplete; must clear before bucket-A PASS | (E) VPIN/microstructure candidate |
| `strategy_edge` | `ic_pnl_misalignment` | IC strong cross-window + per-path PnL costed-out; pnl_ic_alignment_score < 0.30 | Round 3.1 final FAIL signature |
| `strategy_edge` | `regime_instability_oos` | DSR_IS↔DSR_OOS gap > 0.10; new §11.5 #9 surface | Round 3.1 N8.2 catastrophic divergence |
| `strategy_edge` | `gap_variance_unbounded` | Overnight-horizon strategies whose tail risk under macro events (FOMC/Copom) violates Quarter-Kelly substrate | Risk-side veto for candidate (D) |
| `paper_mode_audit` | `regime_filter_overfit` | Multi-timeframe filter that PASSES backtest but fails paper-mode by over-filtering live regimes | (B) candidate forward concern |
| `paper_mode_audit` | `concentration_excursion` | Conviction-conditional sizing concentration causing daily DD breach in paper-mode | (A) candidate forward concern |

### §4.2 New anti-patterns proposed for §5 catalog (current §5.1-§5.10)

| ID | Anti-pattern (NEW) | Mandate |
|---|---|---|
| **§5.11** | `H_next_inherit_T002_consumed_holdout_silent_slide` | Any future H_next sign-off attempt that proposes re-using the [2025-07-01, 2026-04-21] window as "untouched OOS for H_next" fires Riven custodial VETO automatically. T002 consumption is binding regardless of K3-decay-vs-parquet-read interpretation; researcher-observation contamination is real. |
| **§5.12** | `walk_forward_rolling_on_observed_tape` | Walk-forward rolling validation on tape already exposed to T002 sign-off chain (Beckett runs N6..N8.2 + Mira Round 1..3.1 verdict scrutiny + post-mortem authoring) is NOT virgin OOS. Custodial VETO on any H_next sign-off attempt that substitutes walk-forward for fresh forward virgin window. |
| **§5.13** | `pre_registration_skipped_for_speed` | Any H_next attempt to skip Pax pre-registered hash-frozen 4-branch disposition rule (PRR-style discipline per ESC-012 R3 carry-forward) before consuming the fresh virgin OOS window fires Riven custodial VETO. PRR discipline is non-negotiable. |
| **§5.14** | `sizing_envelope_proposed_pre_capture_rate_check` | Any H_next sizing exercise > 0 proposed before §11.5 #8 capture-rate ≥ 0.6 PASS fires Riven custodial VETO. The capture-rate floor is a NECESSARY pre-condition for Quarter-Kelly substrate parametrizability. |
| **§5.15** | `ic_strong_pnl_unverified_silent_slide` | Any H_next sign-off attempt that promotes K3 IC PASS to deployment-eligible without §11.5 #10 PnL-IC alignment verification fires Riven custodial VETO. Round 3.1 lesson: IC strong cross-window does NOT imply realized PnL deployable. |
| **§5.16** | `overnight_horizon_quarter_kelly_pretense` | Any sizing proposal for overnight-horizon strategies that pretends Quarter-Kelly substrate is parametrizable from CPCV trades-only distribution (without explicit gap-variance regime decomposition) fires Riven custodial VETO. Tail risk under macro events is structurally unbounded. |

### §4.3 §5 catalog binding for H_next

The full §5.1..§5.16 catalog (existing §5.1-§5.10 + new §5.11-§5.16) is binding for ALL H_next sign-off attempts. Riven authoring authority preserves catalog integrity per ESC-011 R7 + R20 carry-forward.

---

## §5 Sizing posture for H_next

### §5.1 Quarter-Kelly REGRA ABSOLUTA preserved INTACT

Riven persona REGRA ABSOLUTA: `f* = μ/σ²`; quarter-Kelly cap `f ≤ 0.25 × f*`. Both `μ` and `σ²` MUST come from a distribution H_next strategy could have actually traded — i.e., real-tape (bucket B GATE_4_PASS clearance) at minimum + cost-and-friction layer faithful to live execution + capture rate ≥ 0.6 + DSR stationarity ≤ 0.10 + PnL-IC alignment ≥ 0.30. Below-floor on ANY of these = sizing-deferred MANDATORY.

**Quarter-Kelly cap 0.25 is the operational TETO intransponível.** In practice, Riven will frequently operate BELOW this teto (1/6, 1/8, 1/10 of f*) when N_trials is high, DSR is marginal, capture rate is marginal, or stationarity is marginal. **Below quarter-Kelly is fine; above quarter-Kelly is FORBIDDEN ABSOLUTELY** per persona REGRA ABSOLUTA.

### §5.2 NEW per-bucket position cap (if conviction-conditional sizing in scope)

If H_next direction includes (A) conviction-conditional sizing variant, a NEW per-bucket position cap applies: NO single trade exceeds 2× the median trade size from the CPCV distribution. This caps concentration risk; prevents single-trade DD breach of daily budget. Cap is binding regardless of conviction strength; high-conviction signals get capped at the per-bucket cap and signal goes to next-best opportunity (or sized-down trade) rather than oversizing.

### §5.3 Capture rate ≥ 0.6 of theoretical Sharpe — sizing minimum floor

Per §2.2 NEW §11.5 #8, capture rate < 0.6: **sizing-deferred MANDATORY** regardless of other K1/K2/K3 outcomes. Capture rate is the leading indicator of cost-erosion vulnerability; below 0.6 = strategy at risk of Round 3.1 repeat signature; cannot authorize any sizing > 0.

### §5.4 Haircut 30-50% first 3 months live PRESERVED

Riven persona expertise.sizing_framework.haircut_initial: 0.30 to 0.50 multiplicative on quarter-Kelly recommended sizing for the first ~3 months of live deployment. Rationale: backtest is trades-only without book; latency_dma2 not yet calibrated empirically vs live; N_trials inflating DSR; regime conditions may drift from backtest. ALL FOUR rationales carry-forward unchanged for H_next. Haircut applies AFTER quarter-Kelly cap — i.e., operational sizing is `min(f_quarter_kelly, capacity_constraint) × (1 - haircut)` for first 3 months live.

### §5.5 Composite operational sizing envelope

```
H_next operational sizing for first 3 months live:
  f_operational = min(0.25 × μ/σ², capacity_5min, daily_budget_remaining) × (1 - haircut_initial)
  
  with the following pre-conditions ALL ENFORCED:
  - capture_rate ≥ 0.6
  - DSR_OOS strict PASS (>0.95)
  - DSR stationarity |DSR_OOS - DSR_IS| ≤ 0.10
  - K2 PBO < 0.5 strict
  - K3 IC > 0 strict CI95 lower > 0
  - K3 decay COMPUTED-PASS (IC_holdout > 0.5 × IC_in_sample cross-window)
  - pnl_ic_alignment_score ≥ 0.30
  - paper_mode ≥ 5 sessions clean
  - bucket-A engineering wiring HARNESS_PASS
  - Mira Gate 5 cosign + Riven Gate 5 cosign (dual-sign)
  
  haircut_initial = 0.30 to 0.50 (Riven discretion within range; tighter for first 30 days; looser
  for days 30-90 conditional on attribution telemetry tracking Beckett baseline within ±2σ)
  
  per-bucket position cap (if conviction-conditional sizing): 2× median trade size from CPCV
  
  minimum: f_operational ≥ 1 contract; if recommendation < 1 contract, NÃO OPERA
```

---

## §6 Personal preference disclosure

### §6.1 Riven persona prior

Pessimistic-by-default custodial; "em dúvida, reduzo"; 2020 trauma anchor; quarter-Kelly cap inviolate; OOS budget custodially scarce; researcher-observation contamination is real; calendar-locked pre-registered virgin tape is the gold standard for OOS evidence.

### §6.2 Application to H_next direction selection

Among the five candidate directions, my risk-side preference is:

**(B) Multi-timeframe regime filter as PRIMARY** — cleanest §11.5 re-instantiation; lowest variance shift from T002; framework-layer change (no spec yaml mutation; no engine config mutation; no bucket-A re-clearance prerequisite); DIRECTLY ABSORBS Round 3.1 lesson (filter out the cost-erosion regime bucket where T002 lost edge OOS); μ/σ² parametrizable cleanly per regime-bucket; capture rate likely above 0.6 if filter excludes vulnerable regimes; PRR-style 4-branch disposition rule pre-registerable cleanly.

**(E) VPIN/microstructure as DEFERRED-COMPANION** — DIRECTLY ABSORBS Round 3.1 root cause (queue position = fill quality = cost-erosion mechanism); BUT conditional on ProfitDLL book-snapshot wiring delivery (Tiago/Nelo/Aria scope; estimate 4-6 weeks for clean integration + bucket-A clearance + Quinn 8-point gate); accept as parallel research track if engineering bandwidth permits; DO NOT block (B) on (E) timeline.

**(A) Conviction-conditional sizing as DEFERRED** — orthogonal to Round 3.1 lesson; introduces concentration risk; ACCEPT only as a layer ON TOP of (B) once (B) has bucket-B PASS + Phase G OOS + 5+ sessions paper-mode + Riven custodial Gate 5 cosign clean. Concentration cap §5.2 binding when ON.

**(C) Asymmetric exit DEFERRED** — bucket-A re-clearance prerequisite; DD profile change requires fresh Beckett distribution; not first-priority.

**(D) Overnight horizon STRONG REJECT** — gap variance unbounded; quarter-Kelly substrate not parametrizable cleanly; persona REGRA ABSOLUTA "em dúvida, reduzo" → REJECT. WIN/WDO end-of-day-flatten architectural choice is the right one for retail-algo squad of this size.

### §6.3 Personal preference openly disclosed

I, Riven, prefer **(B) multi-timeframe regime filter as PRIMARY for H_next, with (E) VPIN/microstructure as deferred-companion conditional on ProfitDLL book-snapshot wiring**. (A) and (C) DEFERRED to subsequent epics. (D) STRONG REJECT. This preference is consistent with Riven persona core principles + Round 3.1 lessons + Quarter-Kelly substrate parametrizability + §11.5 #1-#10 cumulative pre-conditions discipline.

This disclosure is per QUANT council protocol mandate (voter discloses personal preference for transparency; voter does NOT pre-empt council majority adjudication). Pax @po retains forward-research direction selection authority post-council resolution.

### §6.4 Counterfactuals

For risk-perimeter discipline transparency, I record what would flip my vote:

- **If ProfitDLL book-snapshot wiring delivers within 2 weeks** (faster than my estimate 4-6 weeks): (E) elevates to co-PRIMARY with (B); both pursued in parallel.
- **If multi-timeframe filter complexity blow-up exceeds 30 LoC** (becomes a refactor, not a filter): (E) overtakes (B) on architectural cost basis.
- **If forward virgin hold-out window (Option i) cannot be procured** (e.g., live data ingestion blocker): all H_next directions DEFERRED until OOS budget topology resolved.
- **If Bonferroni n_trials carry-forward at n=5 makes any new strict bar mathematically unreachable for H_next**: trigger Mira spec amendment council to re-evaluate Bonferroni discipline (Riven does NOT pre-empt; surface concern only).

These counterfactuals are NOT pleadings for re-discussion — they are transparency disclosures of boundary conditions of my vote.

---

## §7 Article IV self-audit

Every claim in this ballot traces to (a) source artifact in repository, (b) governance ledger entry, (c) Mira spec § anchor, (d) Bailey-LdP / Kelly / Thorp / AFML external citation, (e) Riven persona principle / REGRA ABSOLUTA. NO INVENTION. NO threshold relaxation. NO pre-emption of Mira / Pax / Aria / Beckett / Kira / Sable / Dara / Tiago / Nelo / Quinn / Gage authority.

| Claim category | Trace anchors |
|---|---|
| T002 Round 3.1 final FAIL `costed_out_edge_oos_confirmed_K3_passed` | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` frontmatter + disposition |
| ESC-012 5/6 SUPERMAJORITY Path B + Riven Path C minority | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §1 + §3 |
| ESC-013 5/5 UNANIMOUS Path IV protocol-correction | `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §1 |
| §11.5 cumulative pre-conditions §1..§7 | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 + §4.4 + §6 + Riven persona checklists |
| K1/K2/K3 strict bars UNMOVABLE per Anti-Article-IV Guard #4 | ESC-011 R14 + Mira spec v1.2.0 §11.2 + parent spec yaml v0.2.3 §kill_criteria L207-209 |
| Bonferroni n_trials cumulative carry-forward monotonic | Mira spec §6 + ESC-011 R9 + Bailey-LdP 2014 §3 |
| Hold-out lock virgin discipline Anti-Article-IV Guard #3 | `_holdout_lock.py` R10 + `assert_holdout_safe` enforced 5 call-sites + per-line manifest provenance |
| Quarter-Kelly cap 0.25 × f* REGRA ABSOLUTA | Riven persona expertise.sizing_framework.quarter_kelly_default + Kelly 1956 + Thorp 2008 + López de Prado 2018 AFML §15-16 |
| Haircut 30-50% first ~3 months live | Riven persona expertise.sizing_framework.haircut_initial verbatim |
| OOS budget one-shot property | Bailey-LdP 2014 §3 + AFML §11-12 (CPCV methodology) + Bailey-Borwein-Lopez de Prado 2014 (PBO methodology) |
| Researcher-observation contamination on observed tape | Mira spec PRR-20260421-1 + Anti-Article-IV Guard #3 + AFML §11 hold-out integrity |
| Round 3.1 IC=0.866 cross-window robust + costed-out OOS PnL | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` disposition_rationale |
| 3-bucket post-mortem framework + §5.1-§5.10 anti-pattern catalog | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §2 + §5 verbatim |
| Capture rate / DSR stationarity / PnL-IC alignment as risk-side checks | NEW §11.5 #8/#9/#10 proposed in this ballot; mandate is for Mira spec amendment v1.3.0 (subject to Mira approval) |
| Gap variance unbounded under macro events for overnight strategies | Industry baseline (overnight gap risk; AFML §17 microstructure intraday-overnight asymmetry); Riven persona "em dúvida, reduzo" |
| Industry baseline P(retail strategy survives OOS deployable) ≈ 0.10-0.15 | López de Prado AFML §1 quant-research conversion-rate intuition; Riven persona pessimistic prior |
| ProfitDLL book-snapshot wiring scope (Tiago/Nelo/Aria) | `feedback_profitdll_quirks.md` autoMemory + ESC-009 Tiago/Nelo authority matrix |

### §7.1 Article IV self-audit verdict

NO INVENTION (all probability priors §1.1 / §6.2 disclosed openly as Riven persona pessimistic priors NOT empirical measurements; reader can re-evaluate under different priors). NO threshold relaxation (K1/K2/K3 strict bars applied AS-IS; quarter-Kelly cap 0.25 applied AS-IS; haircut 30-50% applied AS-IS). NEW §11.5 #8/#9/#10 are TIGHTER not looser. NO source-code modification (this ballot is write-only at council-document layer; no code mutation; no spec yaml mutation; no spec markdown mutation; no hold-out touch). NO push (Article II → Gage @devops EXCLUSIVE; Riven authoring this ballot does NOT push). NO pre-emption of Mira statistical authority (NEW §11.5 #8/#9/#10 are PROPOSED for Mira spec amendment; Mira retains approval authority). NO pre-emption of Pax forward-research direction selection authority (this ballot expresses preference among candidates §6 but does NOT bind Pax scope decision). NO pre-emption of Aria architecture authority (architectural cost assessments §1.1 are surfaced for Aria adjudication, not bound). NO pre-emption of Beckett harness amendment authority (Beckett retains authority on capture_rate / pnl_ic_alignment / dsr_stationarity field emission; this ballot proposes the fields, Beckett implements).

### §7.2 Anti-Article-IV Guards self-audit (8 guards verbatim)

| Guard | Mandate | THIS ballot reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | THIS ballot does NOT authorize impl; H_next impl gated through Mira spec v1.3.0 amendment (with #8/#9/#10) → Mira approval → Pax story → Quinn QA → Dex impl standard chain |
| **#2** | NO engine config mutation at runtime | THIS ballot does NOT touch engine config |
| **#3** | NO touch hold-out lock | THIS ballot EXPLICITLY PRESERVES hold-out lock discipline; Option (i) forward virgin window inherits T002 lock mechanics verbatim |
| **#4** | Gate 4 thresholds UNMOVABLE | THIS ballot APPLIES K1/K2/K3 strict bars AS-IS for H_next; NEW §11.5 #8/#9/#10 are ADDITIONAL not RELAXING |
| **#5** | NO subsample backtest run | THIS ballot does NOT authorize partial-window evaluation |
| **#6** | NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH | THIS ballot CONFIRMS Gate 5 LOCKED PERMANENTLY for T002; H_next requires fresh Gate 5 dependency tree |
| **#7** | NO push (Gage @devops EXCLUSIVE) | THIS ballot is local-only artifact |
| **#8** | Verdict-issuing protocol — `*_status` provenance + `InvalidVerdictReport` raise on `K_FAIL` with `*_status != 'computed'` | THIS ballot does NOT issue verdicts; NEW §11.5 #9 (DSR stationarity) is consistent with Guard #8 (computed status discipline) — verdict layer extends, does not violate |

All eight Anti-Article-IV Guards honored verbatim by THIS ballot.

---

## §8 Riven cosign 2026-05-01 BRT — QUANT alpha-discovery ballot

```
Author: Riven (@risk-manager) — Risk Manager & Capital Gatekeeper authority
Council: QUANT 2026-05-01 — H_next alpha discovery direction post T002 retire (Round 3.1 final FAIL costed_out_edge_oos_confirmed_K3_passed)
Authority basis: ESC-011 R7 + R20 + ESC-012 R10/R11 + ESC-013 R10/R11 cumulative + Mira spec v1.2.0 §12.1 sign-off chain row F2-T8-T6 + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp custodial monopoly + Riven persona REGRA ABSOLUTA (quarter-Kelly + sizing-deferred + paper-mode pre-condition + haircut 30-50% first 3 months live)

Risk-lens veto-screen on candidate directions §1:
  - (A) Conviction-conditional sizing: CONDITIONAL ACCEPT with per-bucket cap §5.2
  - (B) Multi-timeframe regime filter: ACCEPT (PREFERRED PRIMARY) — cleanest §11.5 re-instantiation; directly absorbs Round 3.1 lesson via cost-erosion regime exclusion
  - (C) Asymmetric exit: DEFERRED — bucket-A re-clearance prerequisite; fresh Beckett distribution required
  - (D) Overnight horizon: STRONG REJECT — gap variance unbounded; quarter-Kelly substrate not parametrizable cleanly
  - (E) VPIN/microstructure: CONDITIONAL ACCEPT — only after ProfitDLL book-snapshot wiring delivery + bucket-A re-clearance; preferred deferred-companion to (B)

§11.5 carry-forward §2: §1-#7 verbatim; NEW #8 capture-rate ≥ 0.6 of theoretical Sharpe; NEW #9 DSR stationarity |DSR_OOS - DSR_IS| ≤ 0.10; NEW #10 PnL-IC alignment score ≥ 0.30. Net: TIGHTER on three new dimensions; NO LOOSENING on any existing dimension. K1/K2/K3 strict bars UNMOVABLE carry forward.

OOS budget §3: REJECT walk-forward rolling (researcher-observation contamination); REJECT reserve-from-existing-IS (Bonferroni inflation + already-observed-tape contamination); ACCEPT Option (i) forward virgin hold-out [2026-05-01, 2026-10-31] or longer with hash-frozen pre-registered spec + 4-branch disposition rule + per-line manifest provenance lock identical to T002 mechanics. RISK PREFERENCE: Option (i) — strongest OOS evidence within Quarter-Kelly timeline discipline.

3-bucket post-mortem v4 §4: NEW sub-classifications (book_snapshot_dependency, ic_pnl_misalignment, regime_instability_oos, gap_variance_unbounded, regime_filter_overfit, concentration_excursion); NEW anti-patterns §5.11-§5.16 (H_next inherit T002 hold-out silent slide; walk-forward rolling on observed tape; pre-registration skipped for speed; sizing envelope pre capture-rate check; IC strong PnL unverified silent slide; overnight Quarter-Kelly pretense).

Sizing posture H_next §5: Quarter-Kelly REGRA ABSOLUTA preserved INTACT; capture rate ≥ 0.6 floor for sizing > 0; per-bucket cap §5.2 if (A) in scope; haircut 30-50% first 3 months live preserved; minimum ≥ 1 contract; NÃO OPERA if recommendation < 1.

Personal preference disclosed §6: (B) multi-timeframe regime filter as PRIMARY; (E) VPIN/microstructure as deferred-companion conditional on ProfitDLL book wiring; (A) and (C) DEFERRED to subsequent epics; (D) STRONG REJECT. Pax @po retains forward-research direction selection authority post-council; Riven preference is risk-side input, not scope decision.

Counterfactuals openly disclosed §6.4 (vote conditional on: ProfitDLL wiring timeline; multi-timeframe filter complexity; forward hold-out window procurement; Bonferroni n_trials reachability).

Article II preservation: NO push performed by Riven during this ballot authoring. Gage @devops authority preserved.
Article IV preservation: every clause traces (§7); no invention; no threshold mutation; no source-code modification; no spec yaml mutation; no hold-out touch; no Mira / Pax / Aria / Beckett / Kira / Sable / Dara / Tiago / Nelo / Quinn / Gage authority pre-emption.

Anti-Article-IV Guards self-audit §7.2: #1-#8 honored verbatim.

Authority boundary: Riven authors THIS ballot from risk-perimeter perspective only. Mira retains Gate 4b verdict-issuing authority (executed Round 3.1 final FAIL); Mira retains spec amendment authority (§11.5 #8/#9/#10 NEW are PROPOSED subject to Mira approval). Pax retains forward-research direction authority post-council. Gage retains push authority. Tiago retains execution authority. Quinn retains QA authority. Aria retains architecture authority. Beckett retains backtester harness authority. Kira retains scientific peer-review authority. Sable retains process audit authority.

Pre-vote independence statement: Riven authored THIS ballot WITHOUT consulting peer voter ballots (Mira / Pax / Aria / Beckett / Kira / Sable / Dara QUANT 2026-05-01 votes). Independence preserved per council protocol. Inputs consulted: Round 3.1 Mira sign-off (verdict file) + ESC-012/ESC-013 resolutions (governance ledger) + own ESC-012/ESC-013 ballots (consistency anchoring) + Riven post-mortem (own authoring). NO peer-ballot reading pre-vote.

Cosign: Riven @risk-manager 2026-05-01 BRT — QUANT alpha-discovery ballot risk lens.
```

— Riven, guardando o caixa 🛡️
