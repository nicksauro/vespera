# H_next-1 — Conviction-Conditional Sizing on T002 Predictor IP (Draft v0.1.0)

> **spec_id:** H_next-1
> **title:** Conviction-Conditional Sizing on T002 Predictor IP
> **author:** Mira (@ml-researcher) — ML/statistical authority
> **date_brt:** 2026-05-01
> **status:** **Draft v0.1.0** — awaiting T0a-T0f sign-off chain (T0a Mira finalize → T0b Aria archi → T0c Beckett consumer → T0d Riven Gate 5 fence + sizing posture → T0e Pax 10-point + PRR-20260501-1 register → T0f River caller-wiring sign-off)
> **successor_of:** T002 (RETIRE FINAL per spec §0 falsifiability — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` `costed_out_edge_oos_confirmed_K3_passed`; institutional knowledge predictor IP retained per Round 3.1 §6.3 and Riven post-mortem v3 §6.4)
> **inherits_predictor_ip:** **YES** — `predictor = -intraday_flow_direction` (entry-time, sign-of-fade direction); `label = ret_forward_to_17:55_pts` (raw 17:55 close-to-entry-price return in WDO points); IC=0.866 OOS-robust cross-window confirmed (F2 IS 0.866010 / N8.2 OOS 0.865933; decay ratio 0.99991 ≫ 0.5; CI95 lower bound > 0 cross-window)
> **bonferroni_n_trials:** **3 NEW** (T002 cumulative 5 + 3 new = **8 total budget**; adjusted DSR threshold ≈ 1.005 effective per ESC-011/Quant Council R3 ratification + Bailey-LdP 2014 §3 selection-bias correction)
> **holdout_window:** **2026-05-01 .. 2026-10-31 forward-time virgin** (PRIMARY per Mira preference + Quant Council R7); pre-2024 archival 2023-Q1..2024-Q3 fallback IF Dara confirms coverage AND Sable audits virgin status (per R8)
> **council_authority:** `docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md` (5/5 ratified PRIMARY direction; 17 binding conditions R1-R17; lista negativa N1-N14 carry-forward)
> **predecessor docs (consumed verbatim):**
> - Mira spec yaml v0.2.3: `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` (UNMOVABLE — predictor IP source-of-truth; thresholds source-of-truth)
> - Mira spec v0.3.0 Auction State Block (post-correction Nova): `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` §15.14
> - Nova authoritative auction confirmation: `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` §1+§4 (consumed VERBATIM in §4 below)
> - Riven 3-bucket post-mortem v3 + §5.2 per-bucket sizing cap mandate: `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`
> - Round 3.1 verdict (T002 RETIRE FINAL): `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md`
> - Beckett `latency_dma2_profile` spec: `docs/backtest/latency-dma2-profile-spec.md` §4 (consumed VERBATIM in §5)
> - Nova RLP/rollover spec: `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 (consumed VERBATIM in §6)
> - Nova cost atlas v1.0.0 (SHA-locked): `docs/backtest/nova-cost-atlas.yaml` (raw SHA `bbe1ddf7898e79a7…c24b84b6d`)

---

## §0 Purpose + scope

### §0.1 Purpose (PRIMARY direction Quant Council 2026-05-01 ratification)

H_next-1 is the **PRIMARY successor T-series spec** ratified by Quant Council 2026-05-01 5/5 lens convergence (Kira via H_next-2 meta-labeling lens; Mira (a) #1 lens; Nova partial via filter logic; Beckett F1 #1 lens; Riven (A) CONDITIONAL ACCEPT lens). It answers a **structurally distinct question** from T002:

| Aspect | T002 (RETIRED) | **H_next-1 (THIS spec)** |
|---|---|---|
| Hypothesis | "End-of-day inventory unwind in WDO produces fade reversion to 17:55 close at deployable cost-net edge" | **"Conditioning entry on per-trial conviction filters AMPLIFIES gross edge per-trade enough to clear K1 strict bar 0.95 sob FIXED costs (Path A OFF) — i.e. the predictor IP whose rank-stability is OOS-confirmed (IC=0.866) carries deployable PnL when trades are FEWER but with HIGHER conviction"** |
| Predictor | `-intraday_flow_direction` × `ret_forward_to_17:55_pts` | **SAME (carry-forward — IC=0.866 OOS-robust documented)** |
| Filter | `intraday_flow_magnitude > P60_rolling_126d` AND `atr_day_ratio ∈ [P20, P80]_rolling_126d` | **SAME baseline + per-trial conviction filter (T1: P80; T2: P80 + bootstrap CI95 lower > 0.5; T3: P80 + simple regime filter `atr_day_ratio ∈ [P40, P80]` normal regime)** |
| Trial count | 5 (T002 thesis) | **3 NEW (Bonferroni cumulative budget 5+3=8 max)** |
| Verdict bar | DSR > 0.95 / PBO < 0.5 / IC > 0 (UNMOVABLE) | **SAME triplet UNMOVABLE — Anti-Article-IV Guard #4 carry-forward** |
| Hold-out window | 2025-07-01..2026-04-21 (CONSUMED, NOT reusable) | **Forward-time virgin 2026-05-01..2026-10-31 PRIMARY (R7); pre-2024 archival fallback per R8** |
| Sizing | Quarter-Kelly REGRA ABSOLUTA per Riven §11 | **SAME Quarter-Kelly REGRA ABSOLUTA + per-bucket sizing cap = 60% of Quarter-Kelly (R16) on conviction-bucket exposure** |

### §0.2 Falsifiability statement (Popperian, BINDING for Mira clearance T5)

**H_next-1 IS FALSIFIED if:** (a) Bonferroni-adjusted DSR_OOS ≤ 1.005 (effective threshold under n_trials=8) **OR** (b) PBO ≥ 0.5 **OR** (c) IC_OOS_decay_ratio < 0.5 (K3 sub-clause — predictor stability collapses **NEW** OOS window) **OR** (d) capture-rate < 0.6 of theoretical Sharpe (R15 §11.5 #8) **OR** (e) DSR stationarity |DSR_OOS − DSR_IS| > 0.10 (R15 §11.5 #9) **OR** (f) PnL-IC alignment < 0.30 (R15 §11.5 #10).

The triplet K1+K2+K3 is jointly required per Bailey-LdP 2014 §6 canonical reproducible-backtest gating; the §11.5 #8/#9/#10 are NEW BINDING per Quant Council R15 ratification.

### §0.3 Scope IN

1. Reuse T002 predictor IP `(-intraday_flow_direction, ret_forward_to_17:55_pts)` rank-stability OOS-confirmed at IC=0.866 cross-window.
2. Add per-trial conviction filter (T1/T2/T3 per §3 below) to amplify gross edge per-trade SEM mexer custos (Path A original cost reduction OFF per user constraint 2026-04-30 + lista negativa N8 carry-forward).
3. Cost atlas v1.0.0 SHA-locked + cost formula IDENTICAL T002 (R2 lista negativa carry-forward — no cost knob retuning).
4. Triple-barrier exit IDENTICAL T002 (PT=1.5×ATR_hora / SL=1.0×ATR_hora / vertical=17:55:00 BRT) — UNMOVABLE per §15.14 Auction State Block correction (17:55 is **5min buffer pre-close 18:00**, NOT auction boundary).
5. CPCV N=10 / k=2 / 45 paths / embargo=1 session — IDENTICAL T002 cv_scheme (yaml v0.2.3 §cv_scheme).
6. Sample-size mandate: n_trials=3 × P80 filter ≈ 760 events/trial × 3 = **~2280 total trial-events** (Bailey-LdP §3 minimum-N — well above 30-50/trial floor; ≥ 150-250 total floor exceeded by 9-15× margin).
7. 3-bucket attribution carry-forward Riven (`data_quality | strategy_edge | both | inconclusive`).
8. Verdict-vs-reason cross-protocol consistency (Anti-Article-IV Guard #9 candidate per R12) — Mira spec v0.3.0 amendment carry-forward.
9. Per-bucket sizing cap 60% Quarter-Kelly per R16 + capture-rate ≥ 0.6 §11.5 #8.
10. PRR-20260501-1 pre-empirical hash-frozen disposition rule (4-branch decision tree) registered via `python scripts/pax_cosign.py register` BEFORE N1+ Beckett run (R11 carry-forward).

### §0.4 Scope OUT (explicit non-pre-emption)

- **Cost atlas re-tuning / Path A cost reduction R&D:** BLOCKED per user constraint 2026-04-30 + lista negativa N8 (Quant Council). NO retuning of cost atlas / triple-barrier / latency_dma2 / entry-window costs.
- **Auction Print Analysis (SECONDARY direction Nova P1):** `docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md` §1 SECONDARY — separate spec H_next-2 if PRIMARY fails K1; requires fresh Bonferroni budget (R5 carry-forward); NOT this spec.
- **Asymmetric Exit Refinement (DEFERRED direction):** Mira (c) #3 + Beckett F3 #2 — parallel-track if Beckett engine v1.2.0 perf optimization lands; NOT this spec.
- **Overnight horizon swap:** REJECTED per Riven STRONG REJECT (gap variance unbounded; not Quarter-Kelly parametrizable per R14). Lista negativa Quant Council.
- **Multi-timeframe regime filter family:** Mira REJECT Bonferroni blow → COMPROMISE EMBED single regime filter inside T3 conviction trial (per Quant Council Divergence #2 resolution).
- **Spec yaml threshold mutation:** DSR > 0.95 / PBO < 0.5 / IC > 0 thresholds at T002 yaml v0.2.3 L207-209 are **UNMOVABLE per Anti-Article-IV Guard #4** carry-forward. This spec consumes VERBATIM.
- **Live ProfitDLL execution / Quarter-Kelly REGRA ABSOLUTA mutation:** R14 carry-forward; preserved INDEFINITELY.
- **Beckett engine v1.2.0 perf optimization:** PARALLEL-TRACK NON-BLOCKING per R17; MANDATORY only before n_trials=3+ runs (Beckett T-1).

---

## §1 Threshold table — UNMOVABLE (Anti-Article-IV Guard #4 carry-forward)

Per Quant Council R3 + R14 carry-forward and Mira spec yaml v0.2.3 §kill_criteria L207-209 — thresholds are **UNMOVABLE** and inherit unchanged from T002:

| Criterion | Threshold | Source (carry-forward) | Citation |
|---|---|---|---|
| **K1 — Deflated Sharpe Ratio (DSR)** | **DSR > 0.95** strict bar **AND** Bonferroni-adjusted ≈ **1.005 effective** under n_trials=8 cumulative budget | Mira yaml v0.2.3 §kill_criteria.k1_dsr (L207); Quant Council R3 verbatim | Bailey & López de Prado (2014), *Journal of Portfolio Management* 40(5), §3 — "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" |
| **K2 — Probability of Backtest Overfitting (PBO)** | **PBO < 0.5** (ideal < 0.25) | Mira yaml v0.2.3 §kill_criteria.k2_pbo (L208) | Bailey, Borwein & López de Prado (2014), "The Probability of Backtest Overfitting" |
| **K3 — Information Coefficient stability (IC) + decay sub-clause** | **Spearman IC > 0 in-sample with CI95 lower > 0; decay sub-clause: IC_holdout > 0.5 × IC_in_sample (Phase G full evaluation per T002 spec §15.13.5 carry-forward; cross-window decay ratio binding)** | Mira yaml v0.2.3 §kill_criteria.k3_ic (L209); T002 spec §15.13.5 | Lopez de Prado (2018), *Advances in Financial Machine Learning* §8.6 (IC stability) |
| **Bonferroni n_trials cumulative budget** | **8 total (T002: 5 carry-forward + H_next-1: 3 NEW); strict cap (R5)** | Quant Council R1+R3+R5 | Bailey-LdP 2014 §3 selection-bias correction; multiple-testing penalty |
| **§11.5 #8 NEW — capture-rate ≥ 0.6** | `realized_Sharpe / theoretical_Sharpe ≥ 0.6` | Quant Council R15 + Riven §11.5 #8 NEW | Riven post-mortem v3 §6.4 |
| **§11.5 #9 NEW — DSR stationarity** | `\|DSR_OOS − DSR_IS\| ≤ 0.10` | Quant Council R15 + Riven §11.5 #9 NEW | Riven post-mortem v3 §6.4 |
| **§11.5 #10 NEW — PnL-IC alignment** | `Spearman(realized_pnl_per_event, predictor_signal_per_event) ≥ 0.30` | Quant Council R15 + Riven §11.5 #10 NEW | Riven post-mortem v3 §6.4 (canonical anti-`costed_out_edge` test) |

**Decision rule (joint, BINDING for T5 Mira clearance sign-off):**

```
if total_events_in_holdout < 150:
    verdict = INCONCLUSIVE  # AC9 floor (carry-forward T002 §6); route to §8 data_quality bucket
elif (DSR_OOS_bonferroni_adjusted > 1.005)
   AND (PBO < 0.5)
   AND (IC_OOS > 0 with CI95_lower > 0)
   AND (IC_decay_ratio > 0.5)
   AND (capture_rate >= 0.6)
   AND (abs(DSR_OOS - DSR_IS) <= 0.10)
   AND (PnL_IC_alignment >= 0.30):
    verdict = H_NEXT_1_PASS    # all seven conditions jointly PASS
else:
    verdict = H_NEXT_1_FAIL    # any one criterion FAIL
```

There is no partial pass. The seven-fold conjunction is jointly required (per Bailey-LdP 2014 §6 + Quant Council R15 NEW conditions).

**Anti-drift assertion (R3+R14 verbatim):** "H_next-1 K1 strict bar UNMOVABLE per Anti-Article-IV Guard #4. Bonferroni-adjusted threshold tightening (n_trials=8 ≈ 1.005 effective) is **stricter than 0.95 baseline**, never weaker."

---

## §2 Predictor IP carry-forward (T002 institutional knowledge)

Per Round 3.1 §6.3 + Riven post-mortem v3 §6.4 — the predictor IP whose rank-stability is OOS-confirmed at IC=0.866 cross-window is the structural property H_next-1 inherits as foundation. NOT re-discovered, NOT re-derived; **carry-forward as institutional knowledge**.

### §2.1 Predictor↔label binding (verbatim T002 §15.1 + ESC-012 R7)

```
Predictor: -intraday_flow_direction
  formula: -sign(close[t_entry] - open_day)
  semantic: sign-of-fade-direction at entry-time per H1 alternative thesis
  computability: historical (parquet trade-tape; CVD-derivable)

Label: ret_forward_to_17:55_pts
  formula: log(close[17:55] / close[t_entry])
  semantic: forward return entry → 17:55 BRT close (continuous-trading-end buffer pre-18:00)
  computability: historical (parquet trade-tape)

IC measurement: Spearman_rank_correlation(predictor, label)
  primary (BINDING for K3): per-event level over events ∈ holdout AND filter_active(event)
  bootstrap CI: paired-resample n=10000 PCG64 seed=42 paired-index strategy
  decay test (K3 sub-clause): IC_holdout > 0.5 × IC_in_sample
```

### §2.2 Cross-window stability evidence (T002 N8.2 → H_next-1 expectation)

| Window | Period | IC_spearman | CI95 | n_events | Source artifact |
|---|---|---|---|---|---|
| F2 N7-prime in-sample (T002) | 2024-08-22..2025-06-30 | 0.866010 | [0.865288, 0.866026] | 3800 | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §5.1 |
| **N8.2 OOS PROPER (T002)** | **2025-07-01..2026-04-21** | **0.865933** | **[0.864880, 0.866025]** | **3700** | `full_report.json:3-7` |
| **H_next-1 expectation (THIS spec)** | **2026-05-01..2026-10-31 (forward-time virgin) OR pre-2024 archival** | **>= 0.5 × 0.866 = 0.433 (decay floor)** | **CI95_lower > 0** (strict) | **>= 150 floor; >= 760/trial × 3 = ~2280 expected under P80 filter** | T0c Beckett N1+ run (pending) |

**Decay floor 0.5×0.866=0.433** is the K3 sub-clause minimum H_next-1 must satisfy on the NEW holdout window. Below 0.433 = predictor IP collapse → falsification clean. This is the **Bucket B falsification scenario** carry-forward.

### §2.3 What conviction filter changes vs T002

T002 trades on the **full filter universe** (`intraday_flow_magnitude > P60_rolling_126d` AND `atr_day_ratio ∈ [P20, P80]`). Conviction filter restricts to the **upper magnitude tail** (P80 baseline conviction) — fewer trades, higher per-trade gross edge expected if predictor IP magnitude is monotone in conviction.

**Hypothesis:** capture-rate (R15 §11.5 #8) MAY exceed 0.6 under conviction filter when it failed at 0.472 hit_rate / 0.929 profit_factor / -0.053 sharpe under T002 full filter — because trading FEWER lower-conviction predictions removes negative-PnL noise that erased gross edge under fixed costs.

**Counter-hypothesis (BINDING falsifier):** if conviction filter does NOT amplify PnL-IC alignment ≥ 0.30 OR if hit_rate stays < 0.50 OR if sharpe stays NEGATIVE OOS, then `costed_out_edge` is structural to the predictor not an artifact of full-filter noise → H_next-1 falsifies CLEAN; Path C T002+H_next-1 retire ceremony triggered (PRR-20260501-1 disposition rule branch).

---

## §3 Conviction filter trial table (T1-T3, n_trials=3 NEW pre-registered)

Per Quant Council R1+R2+R5 ratification — three trials pre-registered VERBATIM with **single-threshold per trial** (R2 anti-p-hacking; no within-trial threshold optimization). Trials are pre-empirical hash-frozen via PRR-20260501-1 BEFORE N1+ Beckett run (R11 carry-forward).

### §3.1 Trial table

| Trial ID | Name | Parameters | Filter (added on top of T002 baseline filter) | Expected n_events / trial (forward-time virgin) | Bonferroni budget consumed |
|---|---|---|---|---|---|
| **T1** | **conviction_P80_only** | predictor_magnitude > P80_rolling_126d (extreme conviction; trade FEWER) | `intraday_flow_magnitude > P80_rolling_126d` (replaces P60 baseline) | ~760 events / trial (P80 ≈ 20% of P60 baseline ~3800) | 1 of 3 NEW (cumulative 6 of 8) |
| **T2** | **conviction_P80_plus_CI95_stable** | T1 + bootstrap CI95 lower bound > 0.5 (signal-stability conditional) | `intraday_flow_magnitude > P80_rolling_126d` AND `bootstrap_ci95_lower(predictor_t-30bars..predictor_t) > 0.5` | ~500 events / trial (subset of T1) | 1 of 3 NEW (cumulative 7 of 8) |
| **T3** | **conviction_P80_plus_normal_regime** | T1 + simple regime filter `atr_day_ratio ∈ [P40, P80]` normal regime (Riven §1 partial accept + Mira (b) compromise per Quant Council Divergence #2 resolution) | `intraday_flow_magnitude > P80_rolling_126d` AND `atr_day_ratio ∈ [P40_rolling_126d, P80_rolling_126d]` | ~600 events / trial (P80 conviction × normal regime) | 1 of 3 NEW (cumulative 8 of 8) |

### §3.2 Trial design rationale

1. **T1 baseline conviction:** isolates the marginal effect of conviction filtering alone vs T002 full-filter universe. If T1 fails K1 OOS, conviction-filter hypothesis is falsified clean (no compounded effect).
2. **T2 signal stability:** conditions T1 trades on bootstrap CI95 stability of the predictor over a 30-bar lookback. Tests whether **predictor signal stability** (not just magnitude) is the missing dimension. Riven §11.5 #9 DSR stationarity validator informs this design.
3. **T3 regime filter:** embeds simple regime filter as one trial (NOT multi-timeframe family) per Quant Council Divergence #2 PARTIAL ACCEPT resolution. P40-P80 normal regime preserves T002 P20-P80 baseline boundary at the upper edge but tightens the lower edge to exclude calm-market noise.

### §3.3 Single-threshold-per-trial discipline (R2 carry-forward)

For each trial, the threshold is **fixed at spec-time** (this artifact); no within-trial optimization, no per-fold threshold sweep, no posterior threshold reselection. Quinn QA Check N+2 NEW (closure-body Literal completeness check per R13) verifies that trial parameters are encoded as Python `Literal[...]` types in the impl, not as runtime-mutable variables.

### §3.4 Anti-cherry-pick discipline (R5 strict)

n_trials=3 caps total trials over single H_next-1 cycle. If ALL THREE fail K1 OOS, H_next-1 falsifies. **No additional trials may be added under this spec; SECONDARY direction Auction Print Analysis (H_next-2 future) requires fresh Bonferroni budget per R5 verbatim.** Anti-Article-IV Guard #4 + #5 jointly enforce.

---

## §4 Auction state block (consume v0.3.0 corrected from Nova confirmation VERBATIM)

Per Mira spec v0.3.0 §15.14 + Nova authoritative confirmation `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` §1+§4 — the following is consumed VERBATIM. NO mutation allowed in H_next-1 (parent UNMOVABLE per Anti-Article-IV Guard #4).

### §4.1 Nova §4 yaml block (verbatim consumption)

```yaml
# Nova authoritative spec block — auction phases WDO 2026-05-01 BRT
# Source: docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md §4 verbatim
# Status: [WEB-CONFIRMED 2026-05-01]; cross-validated 5 sources (B3 PUMA + 4 retail).

auction_phases_wdo_2026_post_dst:
  pre_open:
    start_brt: "08:55:00"
    end_brt:   "08:59:59"
    matching:  "NONE"
    detection_signal:
      live:    "fase reportada por DLL (Nelo); zero TNewTradeCallback events"
      historic: "timestamp gap > 12h desde último trade D-1; nTradeNumber baixo no primeiro trade D"

  open_auction_disparo:
    timestamp_brt: "09:00:00"
    matching:  "BATCH_CROSS"
    duration:  "<1s normal; pode estender em desbalanceio (margem conservadora 30s)"
    tape_signature:
      live:    "burst de tradeType=4 com prints simultâneos ao mesmo preço (clearing) em <1s"
      historic: "burst de prints com timestamps comprimidos em 09:00:00.x; preço idêntico em múltiplos prints; aggressor=NONE (parquet) onde live mostraria tradeType=4"

  continuous:
    start_brt: "09:00:01"
    end_brt:   "18:00:00"
    matching:  "PRICE_TIME_FIFO"
    embedded_settlement_window:
      start_brt: "15:50:00"
      end_brt:   "16:00:00"
      semantics: "negociação contínua segue; B3 calcula preço de ajuste WDO como VWAP do intervalo (= preço de ajuste do DOL correspondente)"
      tape_signature: "price compression (sigma intra-minuto cai ~30-50% vs janela 15:30-15:50); pin-risk attractor toward expected VWAP"

  post_close_admin_window:
    start_brt: "18:00:00"
    end_brt:   "18:30:00"
    cancellations_allowed_until_brt: "19:00:00"
    matching:  "NONE_NEW_TRADES"
    treatment_in_features: "EXCLUDE — tape >18:00:00 é ruído administrativo, não price discovery"

closing_call_explicit_phase:
  exists_for_wdo: false
  notes: |
    WDO **não possui leilão de fechamento dedicado** análogo às ações que compõem índices B3.
    O timestamp 17:55 do triple-barrier vertical exit é "5min buffer pre-close 18:00",
    NOT "boundary com auction". UNMOVABLE per parent yaml v0.2.3 thesis decision.

dst_brazil:
  applies: false
  abolished_year: 2019

dst_us_impact_on_b3_grade:
  applies: true
  notes: |
    Last transition: 2026-03-09 (winter grade vigente em 2026-05-01).
    Next transition: ~novembro 2026 (re-confirmar grade post-transition).

reduced_sessions_holidays:
  applies: true
  policy: "Pre-feriados B3 half-day excluded from training set per ESC-005 fix; calendar config/calendar/2024-2027.yaml authoritative."
```

### §4.2 H_next-1 entry-window rule (carry-forward T002 verbatim)

Entry windows: **16:55 / 17:10 / 17:25 / 17:40 BRT** (parent thesis end-of-day inventory unwind hypothesis carry-forward; UNMOVABLE per parent yaml v0.2.3 §trading_rules; semantically reinterpreted post-§15.14 as "buffer windows leading to 17:55 vertical exit which is itself 5min pre-close 18:00", NOT "auction boundary windows").

### §4.3 Vertical exit timestamp 17:55 (carry-forward T002 UNMOVABLE)

Triple-barrier vertical exit fires at **17:55:00 BRT** if neither PT nor SL hit. Operationally IDENTICAL T002. Semantically corrected per §4.1 `closing_call_explicit_phase.notes` — 17:55 is a 5-minute conservative buffer before continuous-close 18:00, NOT a regulated auction boundary. This semantic correction does NOT change the operational rule; only the documented rationale.

---

## §5 Cost atlas + latency wiring IDENTICAL T002 (carry-forward verbatim)

Per Quant Council R-carry-forward + lista negativa N8 (cost reduction R&D BLOCKED per user constraint Path A OFF) — cost atlas and latency model are IDENTICAL T002. NO retuning, NO recalibration, NO knob exploration.

### §5.1 Cost atlas v1.0.0 SHA-locked (verbatim)

| Field | Value |
|---|---|
| **Atlas path** | `docs/backtest/nova-cost-atlas.yaml` |
| **Atlas raw SHA** | `bbe1ddf7898e79a7…c24b84b6d` (LF-normalized SHA `acf449415a3c9f5d…`) |
| **Cost formula** | `pnl_net_pts = (exit-entry)*sign*WDO_MULTIPLIER - 2*(brokerage + exchange_fees) - total_slippage_pts` |
| **Determinism stamp** | `cost_atlas_sha256` MUST surface in `determinism_stamp.json` per R8(c) carry-forward (T002 ESC-011 R16) |
| **Rollover calendar** | `config/calendar/2024-2027.yaml` (raw SHA `c6174922dea303a3…0063fcc2`) — `rollover_calendar_sha256` IDENTICAL T002 |
| **Engine config** | `engine_config_sha256` IDENTICAL T002 N8 (`ccfb575a…`) |

### §5.2 Latency profile (Beckett spec consumed VERBATIM)

```yaml
# Source: docs/backtest/latency-dma2-profile-spec.md §4 verbatim
# H_next-1 inherits IDENTICAL T002 §5; NO mutation per N8 lista negativa.

latency_model:
  type: "lognormal_per_event_seeded"
  enabled_for_phase: ["F", "H_next_1"]   # H_next-1 active
  seed_source: ["session", "order_id", "trial_id"]
  hash_function: "blake2b_64"
  components:
    order_submit:
      p50_ms: 2.0
      p95_ms: 8.0
      p99_ms_nominal_target: 20.0
      distribution: "lognormal"
      mu: 0.6931
      sigma: 0.8428
      implied_p99_ms: 14.21
    fill:
      p50_ms: 1.0
      p95_ms: 4.0
      p99_ms_nominal_target: 15.0
      distribution: "lognormal"
      mu: 0.0000
      sigma: 0.8428
      implied_p99_ms: 7.10
    cancel:
      p50_ms: 2.0
      p95_ms: 10.0
      p99_ms_nominal_target: 50.0
      distribution: "lognormal"
      mu: 0.6931
      sigma: 0.9784
      implied_p99_ms: 19.48
  slippage_integration:
    apply_to: ["entry_fill", "barrier_exit_fill"]
    formula: "sign × (mid_at_decision − mid_at_fill_after_latency)"
    units: "points"
    composition_with_existing_slippage: "additive_with_roll_and_extra_ticks"
```

### §5.3 Composition with cost formula (carry-forward T002 §5.3)

```
total_slippage_pts = roll_spread_half_points
                   + slippage_extra_ticks × tick_size
                   + slippage_latency_pts
pnl_net_pts        = (exit - entry) × sign × WDO_MULTIPLIER
                   - 2 × (brokerage + exchange_fees)
                   - total_slippage_pts
```

Sign convention + unit scaffolding UNCHANGED from T002 §5.3 → Mira make_backtest_fn spec §5.3 → Riven §11 audit → Quinn QA §3 Check 1 chain. **NO mutation per lista negativa N8.**

---

## §6 RLP + microstructure flags IDENTICAL T002 (Nova authority — consumed verbatim)

Per Nova authoritative spec `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 yaml block — IDENTICAL T002 §4 carry-forward. Real-tape parquet historical regime: RLP discrimination NOT available (parquet `aggressor ∈ {BUY, SELL, NONE}` only; 13-value `trade_type` enum live-only).

### §6.1 Nova §6 yaml block (verbatim consumption — T002 §4 carry-forward)

```yaml
# Source: docs/backtest/T002.6-nova-rlp-rollover-spec.md §6 verbatim
# H_next-1 inherits IDENTICAL T002 §4 yaml; NO mutation.

rlp_policy:
  active_hours_brt:
    start: "09:00"
    end:   "17:55"
  detection_signal:
    live_field:   "trade_type"          # Nelo TNewTradeCallback enum, value=13
    historic_field: null                # NOT identifiable in parquet (BUY/SELL/NONE only)
  fill_treatment: "B"                   # Option B uniform latency_dma2_profile slippage; no instant-fill bonus
  fill_treatment_rationale_ref: "docs/backtest/T002.6-nova-rlp-rollover-spec.md#§1.4"

rollover:
  flag_d_minus_3_to_d_minus_1: true
  calendar_path: "config/calendar/2024-2027.yaml"
  derivation: "walk back 3 trading days from each wdo_expirations[i], skipping br_holidays"
  treatment: "Option B"
  carry_forward_bug_guard: true

auction:
  exclude_open_close_minutes: 5
  exit_price_rule: "last trade_type in {1,2,3,13} with timestamp < 17:55:00 BRT"
  open_auction_treatment: "no impact on H_next-1 entry windows (entries are late-day per parent thesis)"

circuit_breaker:
  flag_per_session: true
  detection_signal_historic: "continuous aggressor=NONE gap >30min during 09:30-17:55"
  attribution_path: "Riven 3-bucket — inconclusive | strategy_edge case-by-case"

cross_trade:
  flag_per_event: true
  flag_available_historic: false
  cvd_treatment: "exclude tradeType=1 from CVD / OFI / imbalance"
```

### §6.2 Detection-signal gap documentation (carry-forward T002 §4.3 verbatim)

KNOWN GAP: historic parquet exposes only `aggressor ∈ {BUY, SELL, NONE}`. The 13-value `trade_type` enum is NOT present in historic data. RLP-segregated CVD / volume-profile features are NOT computable historically; deferred to Live regime (Phase H downstream H_next-1). Determinism stamp records `data_quality.cross_trade_flag_available: false` and `data_quality.rlp_flag_available_historic: false`.

---

## §7 Sample-size mandate (Bailey-LdP §3 minimum-N) — n_trials=3 cycle

Per Quant Council R1 + R5 + Bailey-LdP 2014 §3 minimum-N — sample-size for H_next-1 per trial:

| Parameter | Mandate | Rationale |
|---|---|---|
| **Events per trial (P80 filter)** | **≥ 30-50 events per trial floor; expected ~500-760 / trial** (P80 conviction restricts to upper magnitude tail; T1 expected ~760, T2 expected ~500, T3 expected ~600) | Bailey-López de Prado 2014 §3 — minimum-N for stable Sharpe variance estimation under non-normal returns |
| **Trials** | **3 NEW (T1..T3 per §3 above)** | Bonferroni n_trials cumulative budget = 5 (T002 carry-forward) + 3 (NEW) = **8 total** (R3 strict cap) |
| **Total events expected (forward-time virgin window)** | **~500-760 × 3 ≈ 1500-2280 trial-events** (well above 150-250 floor; 9-15× margin) | Floor preservation under P80 conviction filter |
| **Floor enforcement (carry-forward T002 AC9)** | If `total_events < 150` per trial → verdict INCONCLUSIVE; bucket attribution `data_quality` default | Sample-size floor NEVER weakened |

**Floor enforcement decision rule (per trial):**

```
total_events_in_trial = sum(events filtered by trial.params)
if total_events_in_trial < 30:
    trial_verdict = INCONCLUSIVE
    bucket_default = data_quality (sample-size insufficiency)
elif 30 <= total_events_in_trial < 150:
    trial_flag = "marginal_sample_size"
    proceed_to_triplet = True  # Mira clearance MUST cite flag
else:
    proceed_to_triplet = True
```

**Citation anchor:** Bailey, D. H., & López de Prado, M. (2014). *Journal of Portfolio Management* 40(5) §3 — minimum-N selection-bias correction. Reproduction harness `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` carry-forward T002 (6/6 PASS); same harness MUST re-run on H_next-1 real-tape harness to confirm Δ DSR > 0.10 across 5 seeds preserved (carry-forward T002 §8(f)).

---

## §8 3-bucket attribution carry-forward Riven (carry-forward T002 §7 verbatim)

Per Quant Council R-carry-forward (Riven 3-bucket framework cumulative) — every H_next-1 run that fails to clear the §1 thresholds MUST classify the failure into one of three mutually-exclusive buckets, recorded in run report and Riven post-mortem `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (extends ledger with H_next-1 entries).

### §8.1 Bucket definitions (carry-forward T002 §7.1)

| Bucket | Definition | Diagnostic signature |
|---|---|---|
| **`data_quality`** | Failure attributable to real-tape ingestion / replay engineering (parquet schema drift, RLP miscoding, rollover-gap mishandling, latency model misapplied, cost atlas miswired, circuit-breaker contamination, cross-trade leakage into CVD, **conviction filter computation gap**) | (a) Toy benchmark Δ DSR > 0.10 still PASS on synthetic walk under same code path (harness still discriminates); (b) trade-by-trade parity check vs reference replay shows unexpected fills/PnL deltas; (c) calendar/RLP/rollover audit reveals gaps; (d) ≥3 sessions with `circuit_breaker_fired=True` OR ≥2 sessions with RLP-detection-gap OR <70% session coverage; (e) **conviction filter `intraday_flow_magnitude > P80` not encoded as Python `Literal[...]` per Quinn QA Check N+2** |
| **`strategy_edge`** | Failure attributable to the conviction-conditional sizing strategy itself (predictor IP rank-stable but conviction filter does NOT amplify deployable PnL under realistic costs+latency) | (a) Toy benchmark Δ DSR > 0.10 PASS on real-tape harness (harness OK); (b) data-quality audit clean (≥70% session coverage; <3 CB events; <2 RLP gaps); (c) DSR/PBO/IC measurements stable across seeds; (d) **PnL-IC alignment ≥ 0.30 (R15 §11.5 #10) tested explicitly** — if FAIL → `costed_out_edge_carry_forward` sub-classification (predictor stable, conviction filter does not amplify) |
| **`both`** | Failure with mixed signature — data-quality issues AND strategy-edge concerns are jointly present and cannot be cleanly separated by single re-run | Requires sequential re-run after addressing data-quality side first (closure of `data_quality` bucket clears line-of-sight to `strategy_edge` verdict) |

### §8.2 Decision tree (BINDING for Mira clearance T5)

```
H_next-1 N1+ run produces metrics + data-quality audit + toy-benchmark re-run + PnL-IC alignment + capture-rate measurement.

Step 1 — Sample-size floor (per §7):
    if total_events < 150 (any trial) OR < 30 (single trial):
        verdict = INCONCLUSIVE
        bucket = data_quality if (session_coverage < 70% OR ≥3 CB OR ≥2 RLP_gaps) else inconclusive_pending_more_data
        STOP

Step 2 — Toy benchmark on real-tape harness (Δ DSR > 0.10 across 5 seeds preservation):
    if toy_benchmark_delta_DSR <= 0.10 across 5 seeds:
        verdict = INCONCLUSIVE
        bucket = data_quality  # harness no longer discriminates under H_next-1 perimeter
        STOP

Step 3 — Triplet adjudication (§1) + R15 §11.5 #8/#9/#10 NEW:
    pass_DSR = (DSR_OOS_bonferroni_adjusted > 1.005)  # n_trials=8 cumulative
    pass_PBO = (PBO < 0.5)
    pass_IC  = (IC_OOS > 0 AND CI95_lower > 0 AND IC_decay_ratio > 0.5)
    pass_capture = (capture_rate >= 0.6)
    pass_DSR_stationarity = (abs(DSR_OOS - DSR_IS) <= 0.10)
    pass_PnL_IC_alignment = (PnL_IC_alignment >= 0.30)
    pass_all = pass_DSR AND pass_PBO AND pass_IC AND pass_capture AND pass_DSR_stationarity AND pass_PnL_IC_alignment

    if pass_all:
        verdict = H_NEXT_1_PASS  # PRIMARY direction CLEARS — Riven Gate 5 dual-sign authorized
        bucket  = strategy_edge_confirmed
        STOP
    else:
        # Triplet failure — classify
        if (session_coverage < 70%) OR (CB_count >= 3) OR (RLP_gap_count >= 2) OR (conviction_filter_literal_check_fail):
            verdict = H_NEXT_1_FAIL
            bucket  = data_quality  # OR both (Step 4)
        elif (data_quality_audit_clean) AND (PnL_IC_alignment < 0.30):
            verdict = H_NEXT_1_FAIL
            bucket  = strategy_edge sub costed_out_edge_carry_forward  # predictor stable conviction does not amplify
        elif (data_quality_audit_clean) AND (IC_decay_ratio < 0.5):
            verdict = H_NEXT_1_FAIL
            bucket  = strategy_edge sub predictor_collapse_OOS  # K3 collapse — predictor IP fails on NEW window
        else:
            verdict = H_NEXT_1_FAIL
            bucket  = both  # sequential re-run required

Step 4 — `both` disambiguation (when applicable):
    If bucket == both:
        - Riven authors entry in post-mortem flagging both contributors quantified.
        - Mira recommends re-run AFTER data_quality side is addressed.
        - No Gate 5 progression possible until disambiguates.

Step 5 — Data-quality bucket procedure:
    - Nova auditing required (RLP / rollover / auction / CB / cross-trade audit).
    - Beckett re-runs after Nova patches; new run_id; sha256 stamps regenerated.
    - Mira re-clears with new evidence.
```

### §8.3 Verdict text mandate

A failed H_next-1 that does NOT cleanly classify into `{data_quality, strategy_edge, both, inconclusive}` is INCONCLUSIVE by default and triggers Mira escalation to mini-council (Nova + Beckett + Riven 3-vote per ESC-011 ratification format precedent). Naming-as-discipline (R2 carry-forward).

---

## §9 Verdict-vs-reason cross-protocol consistency (Anti-Article-IV Guard #9 candidate carry-forward — R12)

Per Quant Council R12 — Anti-Article-IV Guard #9 candidate is the **verdict-vs-reason consistency invariant** raised by Sable as Mira spec v0.3.0 amendment proposal. H_next-1 carries forward the candidate as binding spec-level invariant.

### §9.1 Invariant statement

A Mira clearance verdict (`H_NEXT_1_PASS` / `H_NEXT_1_FAIL` / `INCONCLUSIVE`) MUST be issued with a **reasons array** (`verdict.reasons: list[str]`) that satisfies:

1. **Reason completeness:** if `verdict == H_NEXT_1_FAIL`, then `len(verdict.reasons) >= 1` AND each reason names exactly one failed criterion from §1 (DSR / PBO / IC / capture-rate / DSR-stationarity / PnL-IC-alignment).
2. **Reason consistency:** the failed criteria named in `verdict.reasons` MUST match the criteria computed in `MetricsResult` as actually failing (no orphan reasons; no missing reasons).
3. **PASS short-circuit:** if `verdict == H_NEXT_1_PASS`, then `verdict.reasons == []` (empty array; no reasons because no failures).
4. **INCONCLUSIVE protocol:** if `verdict == INCONCLUSIVE`, `verdict.reasons` MUST cite the AC9 floor breach OR toy-benchmark Δ DSR < 0.10 OR data-quality bucket trigger.

### §9.2 Implementation invariant (impl gate carry-forward T002 §15.5 Anti-Article-IV Guard #8)

`evaluate_kill_criteria()` raises `InvalidVerdictReport` when:
- `verdict == H_NEXT_1_FAIL` AND `len(verdict.reasons) == 0`
- `verdict == H_NEXT_1_PASS` AND `len(verdict.reasons) > 0`
- `verdict.reasons` cites a criterion absent from `MetricsResult` failed-criteria set
- `MetricsResult` failed-criteria set absent from `verdict.reasons`

### §9.3 Quinn QA Check N+2 NEW (R13 carry-forward)

Per Quant Council R13 — Quinn QA gate adds Check N+2 NEW (closure-body Literal completeness check per Sable F-03 carry-forward). Verifies that:
- Trial parameters are encoded as Python `Literal[...]` types in impl
- Threshold values referenced in `evaluate_kill_criteria()` are `Final` / `Literal[...]` constants
- Verdict-reason mapping table is exhaustively defined (no implicit fallthrough)

**Test artifacts:** `tests/h_next_1/test_verdict_reason_consistency.py` (4+ NEW tests covering §9.1 conditions 1-4) per Dex T1 implementation.

---

## §10 Sizing posture (per-bucket cap 60% Quarter-Kelly per R16 + capture-rate ≥ 0.6 §11.5 #8)

Per Quant Council R14 + R16 + R15 §11.5 #8 NEW — H_next-1 sizing posture:

### §10.1 Quarter-Kelly REGRA ABSOLUTA (R14 carry-forward INDEFINITELY)

`max_position_size_per_trade = min(Quarter-Kelly_optimal, hard_cap_R10_2_contracts_initial)`.

Quarter-Kelly is the **conservative ceiling**; never crossed regardless of H_next-1 PASS verdict, regardless of PBO favorable, regardless of capture-rate exceeds. Riven authority preserved INDEFINITELY.

### §10.2 Per-bucket sizing cap = 60% Quarter-Kelly (R16 NEW BINDING)

For H_next-1 conviction-conditional sizing:

```
per_bucket_max_exposure = 0.60 × Quarter-Kelly_per_trade
total_exposure_across_buckets <= Quarter-Kelly_total_capital
```

Conviction buckets (P80 / P80+CI95 / P80+regime per §3) cannot collectively exceed Quarter-Kelly total; per-bucket capped at 60% so concentration risk in single conviction-bucket is bounded. Riven §5.2 mandate carry-forward.

### §10.3 Capture-rate ≥ 0.6 §11.5 #8 NEW BINDING

Post-N1+ run, capture-rate validator computes:

```
capture_rate = realized_Sharpe_OOS / theoretical_Sharpe_under_zero_friction
```

If `capture_rate < 0.6`, K1 effectively FAILS even if DSR strict bar PASSES — the `costed_out_edge_carry_forward` signature is detected and verdict is FAIL with bucket `strategy_edge sub costed_out_edge`.

### §10.4 Half-Kelly fallback (R10 carry-forward)

If H_next-1 PASS BUT capture-rate < 0.7 OR PnL-IC alignment < 0.50, Riven defaults to **Half-Quarter-Kelly** (i.e., 0.5 × 0.25 × Kelly = Eighth-Kelly) for first 30 trading days post-deployment. Riven authority preserved.

---

## §11 R10 Gate 5 fence preservation footer VERBATIM (carry-forward T002 §10.2 + Quant Council R10)

Per Quant Council R10 carry-forward + ESC-011 R5/R6 carry-forward — every H_next-1 sign-off artifact MUST carry the following footer **VERBATIM** (Riven cosign requirement; absence of footer = Riven blocks merge):

```
> **Footer (R5/R6/R10 mandatory per Quant Council 2026-05-01 + ESC-011/ESC-012 carry-forward):**
> H_next-1 PASS does NOT pre-disarm Gate 5 alone. Gate 5 capital ramp dual-sign requires:
>   (a) H_next-1 H_NEXT_1_PASS (THIS spec — DSR/PBO/IC + R15 §11.5 #8/#9/#10 jointly PASS)
>   (b) §11.5 #1..#7 cumulative pre-conditions PASS (Riven authority preserved)
>   (c) Phase H paper-mode audit (Riven 3-bucket bucket C clearance, T002.7+ future)
>   (d) Quarter-Kelly sizing parameter set (Riven authority untouched)
>   (e) Per-bucket sizing cap = 60% Quarter-Kelly (R16) WIRED
>   (f) Capture-rate ≥ 0.6 (R15 §11.5 #8) VERIFIED in N1+ run report
>   (g) DSR stationarity |DSR_OOS - DSR_IS| ≤ 0.10 (R15 §11.5 #9) VERIFIED
>   (h) PnL-IC alignment ≥ 0.30 (R15 §11.5 #10) VERIFIED
> Riven §9 HOLD #2 Gate 5 disarm authority preserved.
> Anti-Article-IV Guard #4 thresholds UNMOVABLE (DSR>0.95 / PBO<0.5 / IC>0).
> Quarter-Kelly REGRA ABSOLUTA preserved INDEFINITELY (R14).
> Cost atlas + latency profile UNTOUCHED per lista negativa N8 (cost reduction R&D BLOCKED per user constraint Path A OFF).
```

Gate-bind mechanism for H_next-1 (precisely which §9 HOLD #2 sub-gate H_next-1 disarms in disarm ledger, and how it composes with prior gates) is **DEFERRED to Aria T0b architectural review** (carry-forward T002 §10.3 deferral pattern). This spec locks the **scientific contract** here without prematurely committing to disarm-ledger plumbing.

---

## §12 Sign-off chain T0a-T0f + T1-T7

| Stage | Owner | Action | Gate (input) | Status |
|---|---|---|---|---|
| **T0a** | Mira (@ml-researcher) | Finalize H_next-1 spec from Quant Council 2026-05-01 PRIMARY ratification (covers §0-§14 + 17 conditions R1-R17) | Quant Council 5/5 ratified PRIMARY direction + Mira spec v0.3.0 §15.14 Auction State correction available | ✅ DONE upon publish (this artifact) |
| **T0b** | Aria (@architect) | Architectural review — H_next-1 carry-forward T002 factory pattern + per-fold P126 + D-1 invariant + IC orchestration module placement (vespera_metrics) preservation; conviction filter wiring as additive `TradeRecord` extension; gate-bind mechanism design | T0a PASS (this) | ⏳ pending |
| **T0c** | Beckett (@backtester) | Consumer sign-off — H_next-1 N1+ run targets achievable; cost-atlas integration testable; sha256 stamping protocol IDENTICAL T002; latency_dma2_profile parameters match VERBATIM; conviction filter computability per `intraday_flow_magnitude` historical (parquet) | T0a + T0b PASS | ⏳ pending |
| **T0d** | Riven (@risk-manager) | Cost-atlas wiring + Gate 5 fence preservation + sizing posture (per-bucket cap 60% Quarter-Kelly per R16 + capture-rate ≥ 0.6 §11.5 #8 + DSR stationarity §11.5 #9 + PnL-IC alignment §11.5 #10) — footer §11 VERBATIM | T0a + T0b PASS | ⏳ pending |
| **T0e** | Pax (@po) | 10-point `*validate-story-draft` + register PRR-20260501-1 disposition rule via `python scripts/pax_cosign.py register` (4-branch decision tree §13 below pre-empirical hash-frozen BEFORE N1 run) per R11 carry-forward | T0a + T0b + T0c + T0d PASS | ⏳ pending |
| **T0f** | River (@sm) | Caller-wiring sign-off (NEW per R10 carry-forward — Impl Council pattern) — verifies caller in `scripts/run_h_next_1_dry_run.py` properly wires §1 thresholds + §3 trial table + §10 sizing posture into `run_cpcv` invocation; R8(c) determinism stamps surface | T0a + T0b + T0c + T0d + T0e PASS | ⏳ pending |
| **T1** | Dex (@dev) | Implementation in `packages/h_next_1_conviction_sizing/cpcv_harness.py` — preserves T002 factory pattern + per-fold P126 + Bonferroni n_trials=8 cumulative (5 carry-forward inert + 3 NEW active); conviction filter as additive `intraday_flow_magnitude_above_P80: bool` + `bootstrap_ci95_lower_signal: float` + `atr_day_ratio_in_normal_regime: bool` `TradeRecord` extensions; verdict-reason consistency Anti-Article-IV Guard #9 enforcement | ALL T0a-T0f sign-offs PASS (Anti-Article-IV Guard #1 carry-forward) | ⏳ blocked on T0 chain |
| **T2/T3** | Quinn (@qa) | Unit + integration tests + ruff + lint + regression vs T002 baseline `9b3b1bc` PRESERVED + Check N+2 NEW closure-body Literal completeness check per R13 + verdict-reason consistency tests per §9.3 | T1 PASS | ⏳ blocked |
| **T4** | Beckett (@backtester) | N1+ real-tape replay run (sha256-stamped artifacts; ADR-1 v3 RSS ≤ 6 GiB; cost atlas SHA `bbe1ddf7…` + rollover SHA `c6174922…` IDENTICAL T002 per R-carry-forward; engine_config_sha256 IDENTICAL T002 N8) over **forward-time virgin holdout 2026-05-01..2026-10-31** OR pre-2024 archival fallback per R8 | T2/T3 PASS + T0a-T0f spec compliance retained + PRR-20260501-1 hash-frozen | ⏳ blocked |
| **T5** | Mira (@ml-researcher) | H_next-1 clearance sign-off (`H_NEXT_1_PASS` / `H_NEXT_1_FAIL_strategy_edge` / `H_NEXT_1_FAIL_data_quality` / `H_NEXT_1_FAIL_both` / `INCONCLUSIVE` per §8 decision tree); §11 footer VERBATIM mandatory; Anti-Article-IV Guard #9 verdict-reason consistency enforced; per-trial table evaluation | T4 PASS | ⏳ blocked |
| **T6** | Riven (@risk-manager) | 3-bucket attribution reclassify ledger entry in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (extends T002 ledger with H_next-1 entries; ledger title may rename to `T002-and-H_next-1-attribution.md` per Pax governance discretion) | T5 verdict issued | ⏳ blocked |
| **T7** | Pax (@po) | H_next-1 close per outcome — story status transition per PRR-20260501-1 disposition rule branch (PASS → ESC escalate convene council pathway to deployment / FAIL → H_next-2 secondary direction Auction Print Analysis fresh budget / INCONCLUSIVE → ESC defer council) | T6 reclassify issued | ⏳ blocked |

Sign-off date + cosign of each T0 stage MUST be appended to §15 ledger below. Status field in spec header updates `Draft v0.1.0` → `Draft v0.1.0 — 6/6 T0 sign-offs registered → Final v0.1.0` once T0f closes.

---

## §13 PRR-20260501-1 disposition rule companion (4-branch decision tree pre-empirical hash-frozen)

Per Quant Council R11 carry-forward (Pax canonical pattern from PRR-20260430-1) — H_next-1 disposition rule is **pre-empirical hash-frozen** via `python scripts/pax_cosign.py register` BEFORE Beckett N1+ run. Disposition rule binds Mira clearance T5 verdict outcomes to downstream T6/T7 actions.

### §13.1 4-branch decision tree (BINDING)

```
Branch A — H_NEXT_1_PASS (all 7 §1 conjunction PASS):
  - Authority chain: Mira T5 verdict cosigned + Riven T6 reclassify + Pax T7 close
  - Outcome: H_next-1 PRIMARY direction CLEARS gross edge per-trade amplification hypothesis
  - Next step: ESC escalate convene mini-council pathway to deployment per Riven §11.5 #1..#10 cumulative pre-conditions Gate 5 dual-sign + Phase H paper-mode audit (separate spec H_next-1.1 future)
  - Quarter-Kelly + per-bucket cap 60% sizing posture activated (R14 + R16)
  - Anti-Article-IV Guard #4 thresholds UNMOVED (PASS does NOT relax bar)

Branch B — H_NEXT_1_FAIL_strategy_edge (sub `costed_out_edge_carry_forward`):
  - Diagnostic: predictor IP rank-stable (IC PASS K3 decay) BUT conviction filter does NOT amplify deployable PnL
  - Authority chain: Mira T5 + Riven T6 + Pax T7
  - Outcome: PRIMARY direction falsified at amplification level; predictor IP still valid as institutional knowledge
  - Next step: H_next-2 SECONDARY direction Auction Print Analysis (Nova P1) — fresh Bonferroni budget per R5; predictor IP retained for separate microstructure-novel hypothesis

Branch C — H_NEXT_1_FAIL_strategy_edge (sub `predictor_collapse_OOS`):
  - Diagnostic: K3 decay collapse (IC_decay_ratio < 0.5) on NEW holdout window — predictor IP fails on 2026-05-01..2026-10-31 OOS
  - Authority chain: Mira T5 + Riven T6 + Pax T7 + ESC convene
  - Outcome: T002 + H_next-1 BOTH falsified clean at predictor-validity level
  - Next step: T002 retire ceremony EXTENDS — predictor IP DEPRECATED in research-log; H_next-2 Auction Print Analysis pursues fully-novel predictor with no carry-forward

Branch D — H_NEXT_1_FAIL_data_quality OR _both OR INCONCLUSIVE:
  - Diagnostic: data-quality bucket trigger (carry-forward T002 §7.1 signatures) OR mixed bucket OR floor breach
  - Authority chain: Mira T5 + Nova audit + Beckett re-run + Riven T6 + Pax T7
  - Outcome: PRIMARY direction adjudication deferred pending data-quality side resolution
  - Next step: Nova auditing required → Beckett re-runs after patches → Mira re-clears with new evidence; verdict potentially upgrades to {Branch A, B, C} on re-run
```

### §13.2 Hash-freeze protocol (R11 carry-forward)

Pax T0e registers PRR-20260501-1 via:

```bash
python scripts/pax_cosign.py register \
    --revision-id PRR-20260501-1 \
    --from-version "n/a (H_next-1 v0.0.0 pre-existence)" \
    --to-version "v0.1.0" \
    --branches A,B,C,D \
    --justification "H_next-1 PRIMARY direction Quant Council 2026-05-01 5/5 ratified disposition rule pre-empirical hash-freeze BEFORE N1+ run per R11" \
    --data-constraint-evidence "docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md §4 R1-R17 + §1 PRIMARY outcome"
```

Hash captured as `pax_cosign_hash` in spec frontmatter `preregistration_revisions[]` array entry. Hash-freeze BEFORE Beckett T4 N1+ run is BINDING — running N1+ without hash-frozen disposition rule = R11 violation = merge block.

### §13.3 Append-only revision discipline (MANIFEST R15.2 carry-forward)

Any future modification to §13.1 disposition rule branches requires NEW revision entry `PRR-20260501-N` in `preregistration_revisions[]`; editing existing entry = forging = merge block per `tests/contracts/test_spec_version_gate.py`. Hold-out window 2026-05-01..2026-10-31 SEMPRE INTOCADO regardless of revisions (Anti-Article-IV Guard #3 carry-forward).

---

## §14 Article IV self-audit

| Claim in this spec | Source anchor (verified) |
|---|---|
| Quant Council 5/5 PRIMARY ratification + 17 conditions R1-R17 + lista negativa N1-N14 | `docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md` §1+§4+§5 verbatim |
| T002 RETIRE FINAL with predictor IP retained as institutional knowledge | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §6.3 + §8 + Riven post-mortem v3 §6.4 |
| IC=0.866 OOS-robust cross-window (F2 IS 0.866010 / N8.2 OOS 0.865933; decay ratio 0.99991) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §4.1 + `full_report.json:3-7` + `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §5.1 |
| Predictor↔label binding `(-intraday_flow_direction, ret_forward_to_17:55_pts)` | T002 yaml v0.2.3 §feature_set + §label + ESC-012 R7 verbatim |
| DSR > 0.95 / PBO < 0.5 / IC > 0 thresholds UNMOVABLE | T002 yaml v0.2.3 §kill_criteria L207-209 + Anti-Article-IV Guard #4 carry-forward + Quant Council R3+R14 |
| Bonferroni n_trials cumulative budget 8 (5 T002 carry-forward + 3 NEW) | Quant Council R1+R3+R5 verbatim |
| Bonferroni-adjusted DSR ≈ 1.005 effective under n_trials=8 | Quant Council R3 verbatim + Bailey-LdP 2014 §3 selection-bias correction |
| Forward-time virgin holdout 2026-05-01..2026-10-31 PRIMARY | Quant Council R7 verbatim (Mira preference; impossible leakage) |
| Pre-2024 archival 2023-Q1..2024-Q3 fallback | Quant Council R8 verbatim (Kira preferred IF Dara confirms coverage AND Sable audits virgin status) |
| Quarter-Kelly REGRA ABSOLUTA preserved INDEFINITELY | Quant Council R14 verbatim + Riven authority preserved |
| Per-bucket sizing cap 60% Quarter-Kelly | Quant Council R16 verbatim (Riven §5.2 NEW mandate) |
| §11.5 #8 capture-rate ≥ 0.6, #9 DSR stationarity ≤ 0.10, #10 PnL-IC alignment ≥ 0.30 | Quant Council R15 verbatim + Riven post-mortem v3 §6.4 |
| Anti-Article-IV Guard #9 verdict-vs-reason consistency | Quant Council R12 verbatim (Mira spec v0.3.0 amendment per Sable proposal) |
| Closure-body Literal completeness check (Quinn QA Check N+2 NEW) | Quant Council R13 verbatim + Sable F-03 |
| PRR-20260501-1 disposition rule mandatory pre-N1+ run | Quant Council R11 verbatim (Pax canonical pattern from PRR-20260430-1) |
| Cost atlas v1.0.0 SHA `bbe1ddf7…` + rollover calendar SHA `c6174922…` IDENTICAL T002 | T002 spec §3.5 + ESC-012 R6 carry-forward + lista negativa N8 (cost reduction R&D BLOCKED) |
| Beckett `latency_dma2_profile` spec consumed VERBATIM §5 | `docs/backtest/latency-dma2-profile-spec.md` §4 yaml block |
| Nova RLP/rollover spec consumed VERBATIM §6 | `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 yaml block |
| Auction state block v0.3.0 corrected per Nova confirmation | `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` §1+§4 + T002 spec §15.14 |
| 17:55 vertical exit semantically corrected to "5min buffer pre-close 18:00" UNMOVABLE operationally | Nova T002.7 §3.2 + T002 spec §15.14.1-§15.14.7 |
| CPCV N=10 / k=2 / 45 paths / embargo=1 session | T002 yaml v0.2.3 §cv_scheme verbatim |
| Triple-barrier PT=1.5×ATR_hora / SL=1.0×ATR_hora / vertical=17:55:00 BRT | T002 yaml v0.2.3 §label_alt + §trading_rules + AFML 2018 §3.4 |
| Sample-size mandate 30-50 per trial floor / 150-250 total floor / expected ~1500-2280 | Bailey-LdP 2014 §3 + Quant Council R5 + carry-forward T002 §6 |
| 3-bucket attribution carry-forward (data_quality / strategy_edge / both) | Riven post-mortem v3 §1+§6 + carry-forward T002 §7 |
| §11.5 cumulative #1..#7 pre-conditions for Gate 5 | Riven post-mortem v3 §3 + carry-forward T002 §10.1 + Quant Council R15 (extends to #10) |
| Beckett engine v1.2.0 perf optimization PARALLEL-TRACK NON-BLOCKING for first trial | Quant Council R17 verbatim |
| Lista negativa N1-N14 carry-forward (cost reduction R&D BLOCKED, overnight horizon REJECTED, multi-timeframe regime family REJECTED, etc.) | Quant Council §5 verbatim |
| AFML §3.4 triple-barrier + §8.6 IC stability | Lopez de Prado (2018), *Advances in Financial Machine Learning* §3.4 + §8.6 |
| Bailey-LdP 2014 §3+§6 + Bailey-Borwein-LdP 2014 PBO | Bailey & López de Prado (2014), *Journal of Portfolio Management* 40(5) §3+§6 + Bailey, Borwein & López de Prado (2014) "The Probability of Backtest Overfitting" |
| Efron 1979 percentile bootstrap for CI95 | Efron, B. (1979). "Bootstrap Methods: Another Look at the Jackknife" — `Annals of Statistics` 7(1) |

**Article IV self-audit verdict:** every clause traces. NO INVENTION. 30+ source anchors verified (Quant Council resolution, T002 yaml v0.2.3, Mira spec v0.3.0 §15.14, Round 3.1 verdict, Riven post-mortem v3, Beckett N7-prime + N8.2 reports, Nova T002.7 + T002.6 spec + cost-atlas v1.0.0, Beckett latency spec, T002.6 story, PRR-20260430-1 + PRR-20260501-1, Bailey-LdP 2014 §3+§6, Bailey-Borwein-LdP 2014, AFML 2018 §3.4+§8.6, Efron 1979 bootstrap, MANIFEST R15.2 spec versioning, ADR-1 v3 RSS ceiling, ESC-011 + ESC-012 + ESC-013 + ESC-014 escalation chain).

**Anchor count:** 30+ source anchors verified (well above 10+ minimum per Mira persona Article IV protocol).

**Anti-invention discipline:** every numerical threshold (IC=0.866, decay 0.5, capture 0.6, DSR-stat 0.10, PnL-IC 0.30, sizing 60%, n_trials 3 NEW + 8 cumulative, P80, P40-P80, ATR PT/SL coefficients, hold-out window dates, embargo 1 session) traces to exactly one source anchor or carry-forward chain. Zero free-floating constants.

---

## §15 Mira cosign 2026-05-01 BRT — H_next-1 v0.1.0 Draft

### §15.1 Mira T0a finalize cosign

```
Author: Mira (@ml-researcher) — ML/statistical authority
Council provenance: Quant Council 2026-05-01 5/5 ratified PRIMARY direction (Kira H_next-2 lens / Mira (a) #1 lens / Nova partial filter lens / Beckett F1 #1 lens / Riven (A) CONDITIONAL ACCEPT lens)
Article IV: every clause traces to (a) Quant Council resolution §1+§4+§5 R1-R17 + lista negativa N1-N14, (b) T002 yaml v0.2.3 / spec v0.3.0 §-anchor, (c) Round 3.1 verdict §4 + §6.3, (d) Riven post-mortem v3 §6.4, (e) Bailey-LdP 2014 §3+§6 / Bailey-Borwein-LdP 2014 / AFML 2018 §3.4+§8.6 / Efron 1979 citation, (f) Nova T002.7 §1+§4 + Beckett latency spec §4 + Nova RLP spec §6 verbatim consumption — verified §14 above (30+ anchors)
Article II: no push (this is a write-only finalize; Gage @devops authority preserved for any future commit)
Anti-Article-IV Guards: #1 (impl gated em spec PASS) + #3 (hold-out 2026-05-01..2026-10-31 forward-virgin UNMOVABLE — never touched by IS measurement) + #4 (thresholds UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0; conjuncted with R15 #8/#9/#10 NEW BINDING) + #5 (no subsample, no cherry-pick across n_trials=3 cycle) + #6 (Gate-5 conjunction footer VERBATIM §11) + #7 (no push) + #8 (verdict-issuing protocol — K_FAIL cannot be emitted with ic_status != 'computed' carry-forward T002 §15.5) + **#9 NEW (verdict-vs-reason consistency invariant per R12 carry-forward Quant Council)** preserved verbatim
Scope discipline: H_next-1 implementation NOT pre-empted (separate story by River T0f); Riven Gate 5 authority NOT pre-empted (§11 conjunction footer VERBATIM); Aria gate-bind mechanism deferred (T0b carry-forward T002 §10.3 deferral pattern); cost atlas + latency UNTOUCHED per lista negativa N8 (Path A cost reduction R&D BLOCKED per user constraint); Quarter-Kelly REGRA ABSOLUTA preserved INDEFINITELY (R14)
Successor relation: H_next-1 inherits T002 predictor IP `(-intraday_flow_direction, ret_forward_to_17:55_pts)` with IC=0.866 OOS-robust as institutional knowledge per Round 3.1 §6.3; T002 RETIRE FINAL stands per spec §0 falsifiability — H_next-1 does NOT re-derive nor mutate predictor IP, only ADDS conviction filter layer (T1/T2/T3 per §3 NEW) on top
Sign-off chain: T0a Mira finalize → T0b Aria archi → T0c Beckett consumer → T0d Riven Gate 5 fence + sizing → T0e Pax 10-point + register PRR-20260501-1 → T0f River caller-wiring → T1 Dex impl → T2/T3 Quinn QA → T4 Beckett N1+ → T5 Mira clearance → T6 Riven reclassify → T7 Pax close per disposition rule branch
PRR-20260501-1: 4-branch disposition rule §13 — pre-empirical hash-frozen at T0e via `python scripts/pax_cosign.py register` BEFORE T4 N1+ run (R11 carry-forward strict)
Cosign: Mira @ml-researcher 2026-05-01 BRT — H_next-1 spec v0.1.0 Draft per Quant Council 2026-05-01 R1-R17 PRIMARY direction ratification
```

### §15.2 Sign-off ledger (to be appended as T0b/T0c/T0d/T0e/T0f close)

| Stage | Owner | Cosign | Date (BRT) | Notes |
|---|---|---|---|---|
| T0a | Mira (@ml-researcher) | ✅ Mira | 2026-05-01 | Spec v0.1.0 Draft — 8 dimensions covered (purpose+scope / thresholds / predictor IP carry-forward / 3 conviction trials / auction state v0.3.0 / costs+latency IDENTICAL T002 / RLP+microstructure / sample-size + attribution + verdict-reason consistency + sizing + disposition rule); Beckett §5 + Nova §4+§6 consumed VERBATIM; Anti-Article-IV Guards #1-#9 preserved (Guard #9 NEW per R12); 30+ source anchors §14; lista negativa N1-N14 carry-forward |
| T0b | Aria (@architect) | ⏳ pending | — | Archi review — T002 factory pattern + per-fold P126 + D-1 invariant carry-forward; conviction filter wiring as additive `TradeRecord` extension (Aria Option D module placement IC orchestration `vespera_metrics`); gate-bind mechanism design |
| T0c | Beckett (@backtester) | ⏳ pending | — | Consumer sign-off — N1+ run targets achievable; cost-atlas integration testable; sha256 stamping IDENTICAL T002; latency_dma2_profile match VERBATIM; conviction filter computability historical (parquet) |
| T0d | Riven (@risk-manager) | ⏳ pending | — | Cost-atlas + Gate 5 fence + sizing posture (§10 per-bucket cap 60% Quarter-Kelly + capture-rate ≥ 0.6 + DSR stationarity + PnL-IC alignment) — footer §11 VERBATIM |
| T0e | Pax (@po) | ⏳ pending | — | 10-point validate + register PRR-20260501-1 disposition rule §13 (4 branches A/B/C/D pre-empirical hash-frozen) BEFORE T4 N1+ run |
| T0f | River (@sm) | ⏳ pending | — | Caller-wiring sign-off (NEW per R10 Impl Council pattern carry-forward) — verifies caller wires §1+§3+§10 into `run_cpcv` invocation; R8(c) determinism stamps surface |

### §15.3 Change Log

| Version | Date (BRT) | Author | Change | Authority |
|---|---|---|---|---|
| v0.1.0 | 2026-05-01 | Mira | Initial Draft per Quant Council 2026-05-01 5/5 PRIMARY ratification — H_next-1 successor T-series spec inheriting T002 predictor IP (IC=0.866 OOS-robust) + adding conviction-conditional sizing layer (T1/T2/T3 trials per §3) | Quant Council §1 PRIMARY direction + R1-R17 binding conditions + Mira spec v0.3.0 §15.14 Auction State correction available |

---

— Mira, mapeando o sinal 🗺️
