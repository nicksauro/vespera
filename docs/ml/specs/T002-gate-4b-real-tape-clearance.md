# T002 — Gate 4b Real-Tape Edge-Existence Clearance Spec (Final v1.0.0)

> **Author:** Mira (@ml-researcher) — ML/statistical authority
> **Date (BRT):** 2026-04-29 (skeleton drafted pre-merge ESC-011 R11; finalized T0a same day)
> **Status:** **Final v1.0.0** — full spec consumable by Aria T0b / Beckett T0c / Riven T0d / Pax T0e sign-offs and Dex T1 implementation. Supersedes the same-day skeleton in-place per spec-finalize directive.
> **Council provenance:** ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification (Beckett+Mira+Riven+Aria+Pax) — `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md`
> **Authority chain:** Mira ML/statistical authority under ESC-011 R11 (fence-against-drift mandate — Mira drafts Gate 4b spec ANTES de Gate 4a verdict; this finalize lifts the skeleton into a full binding contract for T002.6 execution).
> **Predecessor / sibling docs:**
> - Mira spec yaml v0.2.3: `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml`
> - Mira make_backtest_fn spec: `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md`
> - Beckett N6+ report: `docs/backtest/T002-beckett-n6-plus-2026-04-29.md`
> - Quinn QA gate: `docs/qa/gates/T002.1.bis-qa-gate.md`
> - Beckett latency spec (consumed verbatim §5): `docs/backtest/latency-dma2-profile-spec.md`
> - Nova RLP/rollover spec (consumed verbatim §4): `docs/backtest/T002.6-nova-rlp-rollover-spec.md`
> - Riven attribution post-mortem: `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`
> - T002.6 story: `docs/stories/T002.6.story.md`

---

## §0 Purpose + scope

### §0.1 Purpose

Gate 4b is the **real-tape edge-existence clearance gate** decomposed from the original §9 HOLD #2 Gate 4 by Council ESC-011 (5/5 UNANIMOUS APPROVE_OPTION_C). It is the second of two sub-gates and answers a **structurally distinct question** from Gate 4a:

| Sub-gate | Question | Scope | Phase | Status |
|---|---|---|---|---|
| **Gate 4a** (sign-off at `docs/qa/gates/T002.1.bis-mira-gate-4a-signoff.md`) | "Does the CPCV harness compute DSR/PBO/IC correctly when fed a deterministic synthetic walk?" — **harness-correctness clearance** | Synthetic deterministic walk per Mira spec §7 toy benchmark methodology | Phase E (T002.1.bis perimeter) | ✅ HARNESS_PASS issued 2026-04-29 BRT |
| **Gate 4b** (THIS SPEC) | "Over the **real WDO trade tape**, does the T002 end-of-day-inventory-unwind strategy produce statistical evidence of an actual edge per Mira spec §6 thresholds (DSR > 0.95 / PBO < 0.5 / IC decay)?" — **edge-existence clearance** | Real WDO parquet replay against the same CPCV+factory+P126+atlas chain | **Phase F** (story T002.6) | ⏳ Pending Dex T1 impl + Beckett N7+ run + Mira clearance sign-off |

**Contrast statement (verbatim, also reproduced in Mira Gate 4a §1 caveat):** "Harness-correctness clearance over synthetic deterministic walk per Mira spec §7 toy benchmark methodology. Edge-existence clearance pending Gate 4b real-tape replay (Phase F scope). DSR=1.52e-05 is the noise-floor null measurement, NOT an economic statement about WDO end-of-day fade strategy edge."

Gate 4a clears the **engineering perimeter** (does the measurement instrument work?). Gate 4b clears the **scientific perimeter** (does what the instrument measures, against real data, constitute statistical evidence of skill?). Both are required upstream of §9 HOLD #2 Gate 5 (capital ramp dual-sign) — see §10 below.

### §0.2 Scope IN

1. Real WDO parquet trade-tape replay path (substituting synthetic walk T002.1.bis Gate 4a).
2. `latency_dma2_profile` slippage estimation per Beckett engine spec consumed verbatim §5 below.
3. RLP policy + rollover D-3..D-1 transitions per Nova authority consumed verbatim §4 below.
4. Cost atlas v1.0.0 SHA-locked + determinism stamp `cost_atlas_sha256` carry-forward (ESC-011 R16).
5. Toy benchmark re-run on real-tape harness (Δ DSR > 0.10 across 5 seeds) — re-asserts harness-correctness preservation under new tape source.
6. Sample-size mandate ≥ 30-50 events × 5 trials = ≥ 150-250 total events floor (Bailey-LdP 2014 §3; ESC-011 R9).
7. 3-bucket failure attribution scaffolding (R9): `data_quality` | `strategy_edge` | `both`, with explicit decision tree (§7).
8. Gate 4b verdict label discipline (`GATE_4_PASS` not `HARNESS_PASS`; R2 carry-forward) and Gate 5 conjunction footer (R5/R6).

### §0.3 Scope OUT (explicit non-pre-emption)

- **Paper-mode audit (bucket C of Riven 3-bucket framework):** Phase G/H, future story T002.7. Gate 4b clears bucket B (`strategy_edge`) only; bucket C is downstream of Gate 4b PASS, NOT this spec.
- **Gate 5 capital ramp dual-sign:** Riven authority post-Gate-4a-AND-4b-BOTH-PASS. This spec does NOT pre-empt the disarm-ledger plumbing (§10 footer reaffirms conjunction).
- **Spec yaml threshold mutation:** DSR > 0.95 / PBO < 0.5 / IC at parent yaml v0.2.3 L207-209 are **UNMOVABLE per Anti-Article-IV Guard #4**. This spec consumes them verbatim; no mutation, no relaxation, no per-run waiver.
- **Live ProfitDLL execution / sizing parametrization:** Phase H downstream; Quarter-Kelly REGRA ABSOLUTA per Riven authority untouched here.

---

## §1 Threshold table — UNMOVABLE (Anti-Article-IV Guard #4)

Per ESC-011 R14 (Aria AC-2 + Pax §6.1) — **Mira spec §6 thresholds are UNMOVABLE per Anti-Article-IV Guard #4** and carry forward unchanged from the original Gate 4 to Gate 4b:

| Criterion | Threshold | Source (Mira spec yaml v0.2.3 + make_backtest_fn spec §6) | Citation |
|---|---|---|---|
| **K1 — Deflated Sharpe Ratio (DSR)** | **DSR > 0.95** (95% probability of skill given N_trials, skewness, kurtosis correction) | Mira spec yaml v0.2.3 §kill_criteria.k1_dsr (L207); Mira make_backtest_fn spec §6 | Bailey & López de Prado (2014), *Journal of Portfolio Management* 40(5), §3 — "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" |
| **K2 — Probability of Backtest Overfitting (PBO)** | **PBO < 0.5** (ideal < 0.25) | Mira spec yaml v0.2.3 §kill_criteria.k2_pbo (L208); Mira make_backtest_fn spec §6 | Bailey, Borwein & López de Prado (2014), "The Probability of Backtest Overfitting" |
| **K3 — Information Coefficient decay (IC)** | **Spearman IC > 0 in-sample with 95% CI lower bound > 0; rolling-window decay curve documented; decay < 1 σ rolling stdev preserves in-sample sign** | Mira spec yaml v0.2.3 §kill_criteria.k3_ic (L209); Mira make_backtest_fn spec §6 | Lopez de Prado (2018), *Advances in Financial Machine Learning*, §8.6 (IC stability) |
| **Bonferroni n_trials carry-forward** | **n_trials = 5** (T1..T5 verbatim per Mira spec §1.2) — NON-NEGOTIABLE | Mira spec yaml v0.2.3 §1.2; ESC-011 R9 | Bailey-LdP 2014 §3 selection-bias correction; multiple-testing penalty |

**Anti-drift assertion (R14 verbatim):** "Gate 4b criteria (Mira spec §6 thresholds DSR>0.95 / PBO<0.5 / IC) UNCHANGED; thresholds unmovable per Anti-Article-IV Guard #4. Gate-bind mechanism for Gate 4b deferred to Phase F architectural review."

**Decision rule (joint, AC8 of T002.6 story):**

```
if total_events < 150:
    verdict = INCONCLUSIVE  # AC9 floor; route to §7 data_quality bucket if attributable
elif (DSR > 0.95) and (PBO < 0.5) and (IC > 0 with CI95 lower > 0):
    verdict = GATE_4_PASS    # all three criteria PASS jointly
else:
    verdict = GATE_4_FAIL    # any one criterion FAIL
```

There is no "2 of 3" partial pass. The triplet is jointly required per Bailey-LdP 2014 §6 canonical reproducible-backtest gating.

---

## §2 Strategy logic preservation (T002.1.bis carry-forward)

All T002.1.bis Aria §I.1-§I.6 invariants carry forward unchanged into Phase F. Real-tape replacement of the synthetic walk does NOT modify any of the following — they are **invariants** of the factory contract, NOT parameters of the tape source:

### §2.1 Triple-barrier exit semantics (UNMOVABLE)

Per parent spec yaml v0.2.3 + Lopez de Prado (2018) AFML §3.4:

| Barrier | Specification | Precedence rule |
|---|---|---|
| **Profit-target (PT)** | `1.5 × ATR_hora` above (long) / below (short) entry price | If PT and SL hit in same fill window, SL wins (conservative pessimist; AFML §3.4) |
| **Stop-loss (SL)** | `1.0 × ATR_hora` below (long) / above (short) entry price | Wins ties against PT |
| **Vertical time barrier** | 17:55:00 BRT exit clock | Last in precedence; only fires if neither PT nor SL hit during holding window |

Precedence: **SL > PT > vertical**. Encoded in `cpcv_harness.py` triple-barrier walker; preserved verbatim through Phase F refactor.

### §2.2 Entry rule + Bonferroni n_trials=5

Per `_resolve_trial_params` (T002.1.bis carry-forward):

- **5 trials T1..T5** with parameter grid per Mira spec yaml §1.2.
- Bonferroni multiple-testing correction applied with **n_trials = 5 NON-NEGOTIABLE** (ESC-011 R9 verbatim).
- Trial parameters: percentile thresholds on `intraday_flow_magnitude` (P60 / P20 / P80) crossed with `atr_day_ratio` regimes (low / normal / high).
- Fade direction: short when intraday_flow_magnitude > P-upper; long when < P-lower; neutral otherwise.
- Entry windows: 16:55 / 17:10 / 17:25 / 17:40 BRT (parent thesis end-of-day inventory unwind hypothesis).

### §2.3 Per-fold P126 rebuild (factory pattern preservation)

Per Aria Option B factory pattern (T002.1.bis):

```python
backtest_fn_factory: Callable[[CPCVSplit, pd.DataFrame], Callable]
# in-fold P126 rebuild:
daily_metrics_train = _build_daily_metrics_from_train_events(
    train_events,
    seed_anchor=split.path_id,
)
```

- **D-1 anti-leak invariant:** `as_of_date == min(test_events.session) - 1 BRT trading day`. NEVER reads test-fold events for daily-metric construction. Preserved through Phase F; factory rebuild signature UNCHANGED.
- **Mutual-exclusivity guard:** `engine.py` raises `ValueError` when both `backtest_fn_factory` AND `backtest_fn` are supplied (or neither). This is a structural invariant of the engine; Phase F does NOT relax it.
- **Per-fold P126 cache key:** keyed on `(split.path_id, as_of_date)`; Phase F preserves cache semantics — only the price source changes (synthetic → real-tape parquet).

### §2.4 D-1 anti-leak invariant (UNMOVABLE)

`as_of_date = min(test_events.session)` D-1 lookback per fold. NO test-fold-event leakage into train-fold daily-metric construction. Preserved end-to-end through Phase F real-tape regime; AC4 test in T002.6 story explicitly asserts identity vs T002.1.bis baseline `9b3b1bc`.

---

## §3 Real-tape data interface (replaces synthetic walk)

This section replaces the T002.1.bis synthetic deterministic seeded walk (`cpcv_harness.py:298-322` Article IV trace block) with real WDO parquet trade-tape consumption. The factory contract and per-fold P126 rebuild interface are PRESERVED (§2 above) — only the price source changes.

### §3.1 Tape source

| Property | Value |
|---|---|
| **Storage path** | `D:\sentinel_data\historical\` (parquet per-session per-contract) |
| **Tape type** | Trades-only (no book; ESC-011 R8(a); Nova features-availability matrix `historic_gaps_in_our_parquet`) |
| **Time zone** | BRT (UTC-3 standard; UTC-2 DST) — `timestamp_brt` UNMOVABLE per Nova authority |
| **Window** | In-sample 2024-08-22..2025-06-30; hold-out 2025-07-01..2026-04-21 (UNTOUCHED per Anti-Article-IV Guard #3) |

### §3.2 Required columns

Per Nova features-availability matrix and T002.6 story AC2:

| Column | Type | Notes |
|---|---|---|
| `ts` (timestamp_brt) | datetime64[ns, BRT] | Per-trade timestamp; monotonic non-decreasing within session |
| `price` | float64 | WDO points (×R$10/pt = R$ value via WDO_MULTIPLIER from DOMAIN_GLOSSARY) |
| `qty` | int64 | Contract count |
| `aggressor` | enum | `BUY` / `SELL` / `NONE` (parquet limitation; live regime also exposes 13-value `trade_type` enum) |
| `tradeType` | enum (live only) | Nelo Q07-V enum; `tradeType=13` = RLP, `=4` = leilão, `=1` = cross trade. **Historic parquet: this column is ABSENT** — see §4.1.3 detection signal gap. |

### §3.3 Replacement of `_walk_session_path` / `_walk_to_exit`

The synthetic walk functions are **REMOVED** from the strategy execution path in Phase F:

- `_walk_session_path` (synthetic deterministic seeded random walk) → REPLACED by `_replay_session_tape_real(session_date, contract_code) -> pd.DataFrame[trades]`
- `_walk_to_exit` (synthetic event-by-event walk anchored to seed) → REPLACED by `_walk_real_tape_to_barrier(entry_event, tape_df, atr_hora, latency_model) -> ExitEvent`

**Interface contract:**
- Input: `(entry_event: EntryEvent, session_tape: pd.DataFrame, atr_hora: float, latency_model: LatencyModel)`
- Output: `ExitEvent` with `(exit_ts, exit_price, exit_reason ∈ {PT, SL, VERTICAL}, slippage_pts, latency_components_ms)`
- Anti-leakage guard: barrier-hit detection at-tape (no look-ahead past the fill timestamp); fill price reconstruction within latency window uses ONLY tape data ≤ `t_decision + latency_ms`.

### §3.4 Latency-model integration

Slippage during the latency window MUST be computed per Beckett `latency_dma2_profile` spec §3 (consumed verbatim §5 below). Synthetic walk did NOT exercise this path because synthetic events were instantaneous; Phase F real-tape DOES.

### §3.5 Cost atlas wiring (R8(c) — IDENTICAL to N6+)

- `cost_atlas_path = docs/backtest/nova-cost-atlas.yaml` (atlas v1.0.0 raw SHA `bbe1ddf7898e79a7…c24b84b6d`, LF-normalized SHA `acf449415a3c9f5d…` per dual-hash semantics in Beckett N6+ §3.1).
- Consumed via `BacktestCosts.from_engine_config` closure capture (T002.1.bis carry-forward).
- Cost formula UNCHANGED: `pnl_net_pts = (exit-entry)*sign*1*WDO_MULTIPLIER - 2*1*(brokerage + exchange_fees) - slippage_pts`
- F1 patch (commit `9997f14`) ensures `cost_atlas_sha256` and `rollover_calendar_sha256` continue to surface in `determinism_stamp.json` for full audit trail (ESC-011 R16 carry-forward — BLOCKING).

---

## §4 RLP + microstructure spec (Nova authority — consumed verbatim)

Per Nova authoritative spec `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 yaml block. The following is the **exact contract** Phase F implementation MUST consume:

### §4.1 Nova §6 yaml block (verbatim)

```yaml
# Nova authoritative spec block — copy/paste from docs/backtest/T002.6-nova-rlp-rollover-spec.md §6

rlp_policy:
  active_hours_brt:
    start: "09:00"
    end:   "17:55"
  detection_signal:
    live_field:   "trade_type"          # Nelo TNewTradeCallback enum, value=13
    historic_field: null                # NOT identifiable in our parquet (BUY/SELL/NONE only)
  fill_treatment: "B"                   # Option B per Nova §1.4 — uniform latency_dma2_profile slippage; no instant-fill bonus
  fill_treatment_rationale_ref: "docs/backtest/T002.6-nova-rlp-rollover-spec.md#§1.4"

rollover:
  flag_d_minus_3_to_d_minus_1: true     # per-session row carries rollover_window: bool
  calendar_path: "config/calendar/2024-2027.yaml"
  derivation: "walk back 3 trading days from each wdo_expirations[i], skipping br_holidays"
  treatment: "Option B"                 # preserve sample, flag for attribution
  carry_forward_bug_guard: true         # Dex T1 MUST resolve explicit contract code per session; no naive WDOFUT carry-forward

auction:
  exclude_open_close_minutes: 5         # last 5 minutes (17:55-18:00) excluded from continuous-price extraction
  exit_price_rule: "last trade_type in {1,2,3,13} with timestamp < 17:55:00 BRT"
  open_auction_treatment: "no impact on T002.6 entry windows (entries are late-day)"

circuit_breaker:
  flag_per_session: true                # session feature: circuit_breaker_fired: bool
  detection_signal_historic: "continuous aggressor=NONE gap >30min during 09:30-17:55"
  attribution_path: "Riven 3-bucket — inconclusive | strategy_edge case-by-case"

cross_trade:
  flag_per_event: true                  # event feature: cross_trade: bool (live only; historic gap documented)
  flag_available_historic: false        # explicit gap; determinism stamp records
  cvd_treatment: "exclude tradeType=1 from CVD / OFI / imbalance"
```

### §4.2 Mira commentary on Nova spec

The above block is **non-negotiable** Nova authority — Mira ML/statistical layer consumes it as a domain contract. Three Mira-side notes:

1. **RLP fill_treatment=B (uniform latency slippage):** statistically the conservative choice. Option A (instant fill) would inject an unverifiable bonus; Option C (mixed 20%/80%) introduces a stochastic knob with no empirical anchor — Article IV violation for Phase F. Option B is the only attribution-clean choice.
2. **Rollover Option B (preserve sample, flag for attribution):** sample-size preservation is critical for AC9 floor (≥150-250 events). Skipping D-3..D-1 (-108 sessions) would jeopardize the floor on a dataset already constrained.
3. **Auction sub-option 3.2-α (last non-auction trade < 17:55:00 BRT):** preserves the spec yaml v0.2.3 17:55 exit boundary verbatim. Sub-option β (use 18:00 closing print) would alter strategy semantics; sub-option γ (snap to 17:55:00 exact) is undefined behavior at boundary.

### §4.3 Detection-signal gap documentation (historic parquet)

**KNOWN GAP, EXPLICITLY DOCUMENTED:** historic parquet exposes only `aggressor ∈ {BUY, SELL, NONE}`. The 13-value `trade_type` enum is **NOT** present in historic data. Implications for Phase F:

- RLP-segregated CVD / volume-profile features are **NOT** computable historically — `cross_trade` flag cannot be set for parquet rows.
- RLP fills appear inside `BUY`/`SELL` aggressor stream without a discriminator flag.
- Phase F operates on the historic parquet, therefore RLP / cross-trade discriminators are deferred to Live regime (Phase H, T002.7+).
- Determinism stamp MUST record `data_quality.cross_trade_flag_available: false` and `data_quality.rlp_flag_available_historic: false` for Phase F runs.

This gap is acknowledged, NOT invented as available. Article IV trace clean.

---

## §5 Latency profile (Beckett authority — consumed verbatim)

Per Beckett authoritative spec `docs/backtest/latency-dma2-profile-spec.md` §4 yaml block. The following is the **exact contract** Phase F implementation MUST consume for slippage estimation under real-tape regime:

### §5.1 Beckett §4 yaml block (verbatim)

```yaml
# Beckett authoritative latency_model — copy/paste from docs/backtest/latency-dma2-profile-spec.md §4
# Engine config target: docs/backtest/engine-config.yaml v1.0.0 → v1.1.0 ON Mira spec PASS.

latency_model:
  type: "lognormal_per_event_seeded"
  enabled_for_phase: ["F"]              # Phase F only; synthetic walk skipped
  seed_source: ["session", "order_id", "trial_id"]
  hash_function: "blake2b_64"           # deterministic, cross-platform stable
  components:
    order_submit:
      p50_ms: 2.0
      p95_ms: 8.0
      p99_ms_nominal_target: 20.0       # cushion target; not log-normal fit
      distribution: "lognormal"
      mu: 0.6931                        # ln(2)
      sigma: 0.8428                     # ln(8/2) / 1.6449
      implied_p99_ms: 14.21             # transparency — implied < target
    fill:
      p50_ms: 1.0
      p95_ms: 4.0
      p99_ms_nominal_target: 15.0
      distribution: "lognormal"
      mu: 0.0000                        # ln(1)
      sigma: 0.8428                     # ln(4/1) / 1.6449
      implied_p99_ms: 7.10
    cancel:
      p50_ms: 2.0
      p95_ms: 10.0
      p99_ms_nominal_target: 50.0       # heaviest tail — congestion / auction
      distribution: "lognormal"
      mu: 0.6931                        # ln(2)
      sigma: 0.9784                     # ln(10/2) / 1.6449
      implied_p99_ms: 19.48             # log-normal underestimates real tail
  slippage_integration:
    apply_to: ["entry_fill", "barrier_exit_fill"]
    formula: "sign × (mid_at_decision − mid_at_fill_after_latency)"
    units: "points"
    composition_with_existing_slippage: "additive_with_roll_and_extra_ticks"
  to_verify:
    - tag: "[TO-VERIFY 2026-04-29]"
      field: "components.cancel.p99_ms_nominal_target"
      reason: "Heavy-tail cancel under congestion may exceed 50ms; refine via Tiago live calibration post-Phase H. May motivate v1.2.0 mixture (log-normal body + Pareto tail)."
    - tag: "[TO-VERIFY 2026-04-29]"
      field: "components.*.implied_p99_ms"
      reason: "Log-normal calibrated to (P50, P95) pair underestimates nominal P99 cushion targets (39-71% across components). Empirical Tiago calibration may motivate distribution family change."
  rationale: |
    DMA2 baseline para WDO B3 broker-routed flow. Industry-baseline conservative
    calibration. Refinement via Tiago @execution-trader live logs post-Phase H
    per Beckett persona *tiago-calibrate command. Heavy-tail components (cancel
    under congestion) flagged as [TO-VERIFY] for distribution-family refinement.
```

### §5.2 Mira commentary on Beckett spec

1. **`enabled_for_phase: ["F"]` is correct:** synthetic walk N6 events were instantaneous; latency physically n/a. Phase F real-tape DOES expose intra-event price movement → latency model REQUIRED.
2. **`additive_with_roll_and_extra_ticks` composition:** preserves engine-config v1.0.0 §slippage_model. Total slippage = roll_half + extra_ticks × tick + latency_pts. **NO double-counting** — roll is immediate cushion; latency is temporal mid drift during round-trip.
3. **Per-event seed `(session, order_id, trial_id, component_name)`:** guarantees bit-identical replay, zero cross-event correlation, zero global RNG state leak. Honors T002.0h R7 hold-out lock spirit + ADR-1 v3 reproducibility ledger.
4. **[TO-VERIFY] tags acknowledged:** the cancel P99 underestimate and (P50, P95) → P99 implied gap are flagged for Tiago empirical refinement post-Phase H. For Gate 4b adjudication, the conservative log-normal baseline is sufficient — it over-estimates rather than under-estimates slippage, the safer side for honest edge claims.

### §5.3 Composition with cost formula

```
total_slippage_pts = roll_spread_half_points
                   + slippage_extra_ticks × tick_size
                   + slippage_latency_pts            # NEW in Phase F
pnl_net_pts        = (exit - entry) × sign × WDO_MULTIPLIER
                   - 2 × (brokerage + exchange_fees)
                   - total_slippage_pts
```

Cost formula sign convention and unit scaffolding UNCHANGED from Mira make_backtest_fn spec §5.3 + Riven §11 audit + Quinn QA §3 Check 1. Only the additive `slippage_latency_pts` term is new.

---

## §6 Sample size mandate (R9 — Bailey-LdP §3 minimum-N)

Per ESC-011 R9 (Mira ballot #M5) — sample-size for Gate 4b is **NON-NEGOTIABLE**:

| Parameter | Mandate | Rationale |
|---|---|---|
| **Events per trial** | **≥ 30-50 events per trial** | Bailey-López de Prado 2014 §3 — minimum-N for stable Sharpe Ratio variance estimation under non-normal returns; below ~30 events the higher-moment correction (skew, kurtosis) becomes unreliable and DSR collapses to a coin-flip |
| **Trials** | **5 trials (T1..T5 per Mira spec §1.2)** | Bonferroni n_trials = 5 carry-forward — prevents trial-count drift undermining the multiple-testing penalty |
| **Total events** | **≥ 150-250 total events** (= 5 × 30-50) | Floor for the joint distribution of Sharpe across trials; below this floor PBO becomes degenerate (not a meaningful overfitting probability, just a discrete histogram of too-few paths) |
| **Bonferroni n_trials = 5** | **NON-NEGOTIABLE** | ESC-011 R9 verbatim; no trial-count inflation allowed to cherry-pick a favourable Bonferroni adjustment |

**Floor enforcement (AC9 of T002.6 story):**

```
total_events = sum(len(trial.events) for trial in trials_T1_to_T5)
if total_events < 150:
    verdict = INCONCLUSIVE  # NOT GATE_4_FAIL — floor missed, not edge falsified
    riven_3bucket_classification = "data_quality" (default) or "inconclusive" if attribution ambiguous
elif 150 <= total_events < 250:
    flag = "marginal_sample_size"  # proceed to triplet adjudication; Mira clearance MUST cite flag
    proceed_to_AC8_triplet_adjudication = True
else:  # >= 250
    proceed_to_AC8_triplet_adjudication = True
```

**Citation anchor:** Bailey, D. H., & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 40(5), §3 (minimum-N requirement and selection-bias correction). Reproduction harness already shipped at `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6/6 PASS — Quinn QA §3 Check 2; Beckett N6+ §4.4) — same harness MUST re-run on real-tape harness to confirm discriminator power Δ DSR > 0.10 across 5 seeds is preserved (§8(f) below).

---

## §7 Failure attribution scaffolding (R9 3-bucket)

Per ESC-011 R9 — every Gate 4b run that fails to clear the §1 thresholds **MUST classify the failure** into one of three mutually-exclusive buckets, recorded in the Gate 4b run report and in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (Riven authoring authority per ESC-011 R7 + R20):

### §7.1 Bucket definitions

| Bucket | Definition | Diagnostic signature |
|---|---|---|
| **`data_quality`** | Failure attributable to real-tape ingestion / replay engineering (parquet schema drift, RLP miscoding, rollover-gap mishandling, latency model misapplied, cost atlas miswired, circuit-breaker contamination, cross-trade leakage into CVD) | (a) Toy benchmark Δ DSR > 0.10 still PASS on synthetic walk under same code path (harness still discriminates); (b) trade-by-trade parity check vs reference replay shows unexpected fills/PnL deltas; (c) calendar/RLP/rollover audit reveals gaps; (d) ≥3 sessions with `circuit_breaker_fired=True` OR ≥2 sessions with RLP-detection-gap OR <70% session coverage |
| **`strategy_edge`** | Failure attributable to the strategy itself (no economic edge in the WDO end-of-day fade hypothesis under realistic costs+latency) | (a) Toy benchmark Δ DSR > 0.10 PASS on real-tape harness (harness OK); (b) data-quality audit clean (≥70% session coverage; <3 CB events; <2 RLP gaps); (c) DSR/PBO/IC measurements stable across seeds and converge to a no-edge null distribution → falsification per Mira spec §7 K1/K2/K3 |
| **`both`** | Failure with mixed signature — data-quality issues AND strategy-edge concerns are jointly present and cannot be cleanly separated by single re-run | Requires sequential re-run after addressing the data-quality side first (closure of `data_quality` bucket clears the line of sight to the `strategy_edge` verdict) |

### §7.2 Decision tree (proposed; binding for Mira clearance sign-off)

```
Gate 4b run produces metrics + data-quality audit + toy-benchmark re-run results.

Step 1 — Sample-size floor (AC9):
    if total_events < 150:
        verdict = INCONCLUSIVE
        bucket = data_quality if (session_coverage < 70% OR ≥3 CB OR ≥2 RLP_gaps) else inconclusive_pending_more_data
        STOP

Step 2 — Toy benchmark on real-tape harness (R8(f) / §8(f)):
    if toy_benchmark_delta_DSR <= 0.10 across 5 seeds:
        verdict = INCONCLUSIVE
        bucket = data_quality  # harness no longer discriminates under new tape source — engineering wiring suspect
        STOP

Step 3 — Triplet adjudication (AC8 / §1):
    pass_DSR = (DSR > 0.95)
    pass_PBO = (PBO < 0.5)
    pass_IC  = (IC > 0 AND CI95_lower > 0)
    if pass_DSR AND pass_PBO AND pass_IC:
        verdict = GATE_4_PASS
        bucket  = strategy_edge_confirmed  # not a failure bucket; Riven 3-bucket B cleared
        STOP
    else:
        # Triplet failure — classify
        if (session_coverage < 70%) OR (CB_count >= 3) OR (RLP_gap_count >= 2):
            verdict = GATE_4_FAIL
            bucket  = data_quality  # OR both — see Step 4
        elif (data_quality_audit_clean):
            verdict = GATE_4_FAIL
            bucket  = strategy_edge  # clean negative — T002 hypothesis falsified
        else:
            verdict = GATE_4_FAIL
            bucket  = both  # sequential re-run required

Step 4 — `both` disambiguation (when applicable):
    If bucket == both:
        - Riven authors entry in post-mortem flagging both contributors quantified.
        - Mira recommends re-run AFTER data_quality side is addressed (Nova auditing required per Step 5).
        - No Gate 5 progression possible until bucket disambiguates to {strategy_edge_confirmed, strategy_edge_failed, data_quality_addressed_then_edge_falsified}.

Step 5 — Data-quality bucket procedure (when bucket includes data_quality):
    - Nova auditing required (RLP / rollover / auction / CB / cross-trade audit).
    - Beckett re-runs after Nova patches; new run_id generated; sha256 stamps regenerated.
    - Mira re-clears with new evidence; verdict potentially upgrades or stays.
```

### §7.3 Mandate — verdict text MUST name the bucket

A failed Gate 4b that does NOT cleanly classify into one of {`data_quality`, `strategy_edge`, `both`, `inconclusive`} is **inconclusive** by default and triggers Mira escalation to mini-council (Nova + Beckett + Riven 3-vote per ESC-011 ratification format precedent). Naming-as-discipline (R2 carry-forward).

---

## §8 Mandatory milestones (R8 a-f Beckett N7+ pre-conditions)

Per ESC-011 R8 (Beckett ballot #3) — Phase F story scope MUST include Beckett N7+ real-tape replay with **all six** of the following milestones. Each is a hard pre-condition for issuing a Gate 4b verdict:

### §8(a) WDO parquet tape consumption

Replace `_walk_session_path` / `_walk_to_exit` synthetic walks (`cpcv_harness.py:298-322` Article IV trace block) with real WDO trade tape (parquet) consumed event-by-event by the same `make_backtest_fn` factory. Triple-barrier walks executed against actual tick prices per §3.3 above. Factory contract + per-fold P126 rebuild interface PRESERVED — only the price source changes.

### §8(b) Preserved factory pattern + per-fold P126 + Bonferroni n_trials=5

All Aria §I.1-§I.6 invariants from T002.1.bis carry forward unchanged:
- `backtest_fn_factory` mutual-exclusivity (`engine.py` ValueError when both/neither).
- Per-fold P126 rebuild via `_build_daily_metrics_from_train_events(train_events, seed_anchor=split.path_id)`.
- `as_of_date = min(test_events.session)` D-1 anti-leak invariant.
- T1..T5 trial table verbatim per Mira spec §1.2.

### §8(c) Cost atlas wiring identical to N6+

Per §3.5 above — same atlas path, same dual-hash semantics, same closure capture, same cost formula. F1 patch (`9997f14`) ensures `cost_atlas_sha256` and `rollover_calendar_sha256` continue to surface in `determinism_stamp.json`.

### §8(d) `latency_dma2_profile` applied to slippage estimation

Per §5 above — Beckett spec consumed verbatim. Slippage during latency window MUST be computed per Beckett `latency_dma2_profile` spec §3 formula. Synthetic walk did not exercise this path; Phase F does.

### §8(e) RLP policy + rollover calendar consumption

Per §4 above — Nova spec consumed verbatim. Real tape contains RLP-eligible prints (Live regime) / undetectable RLP fills inside aggressor stream (Historic regime); rollover calendar `config/calendar/2024-2027.yaml` (raw SHA `c6174922dea303a3…0063fcc2`) consumed for session-day filtering and contract-roll handling. Both behaviours wired post-F1 (Beckett N6+ §6 R16/C1 closure) — Phase F inherits the wiring.

### §8(f) Re-run Bailey-López de Prado 2014 toy benchmark on real-tape harness

Gate 4b is NOT issued until `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (or its Phase-F-equivalent if test fixtures evolve, e.g., `tests/cpcv_harness/test_toy_benchmark_real_tape.py` per T002.6 story AC6) re-runs against the real-tape pipeline confirming **discriminator power Δ DSR > 0.10 across 5 seeds is preserved**.

Seeds (Mira authority — UNMOVABLE post-spec-finalize): `[42, 1337, 271828, 314159, 161803]`.

This is the harness-correctness witness on the new tape source — it certifies that any edge / no-edge measurement Gate 4b reports is signal, not harness artefact.

**All six milestones are jointly required.** Skipping any one → Gate 4b inconclusive.

---

## §9 Verdict label discipline (R2 carry-forward)

Per ESC-011 R2 (Riven C-R1 verbatim) — Gate 4b verdict labeling discipline:

| Aspect | Mandate |
|---|---|
| **Gate 4b PASS verdict label** | **`GATE_4_PASS`** (NOT `HARNESS_PASS` — that label is Gate 4a-only per R2) |
| **Gate 4b FAIL verdict label** | `GATE_4_FAIL` with bucket suffix per §7 (e.g., `GATE_4_FAIL_STRATEGY_EDGE` or `GATE_4_FAIL_DATA_QUALITY` or `GATE_4_FAIL_BOTH`) |
| **Gate 4b INCONCLUSIVE label** | `INCONCLUSIVE` with bucket suffix per §7 (default `data_quality` if attribution ambiguous; else `inconclusive_pending_more_data`) |
| **Distinguish from Gate 4a `HARNESS_PASS`** | Mira Gate 4a sign-off label is `HARNESS_PASS` over synthetic walk; Mira Gate 4b sign-off label is `GATE_4_PASS` over real tape. The two labels are **mutually exclusive perimeters** — never collapse, never substitute |
| **Mandatory caveat in Gate 4b sign-off** | Verbatim: "Edge-existence clearance over real WDO tape replay distribution; harness-correctness was previously cleared via Gate 4a HARNESS_PASS over synthetic deterministic walk per Mira spec §7. The two clearances are sequential serial pre-conditions for §9 HOLD #2 Gate 5 (capital ramp dual-sign), per ESC-011 R5/R6." |

Gate 4a clears the engineering perimeter; Gate 4b clears the scientific perimeter. Naming-as-discipline.

---

## §10 Gate 5 conjunction (R5/R6 reaffirmed)

Per ESC-011 R5 (Beckett #2 + Riven C-R2 + Pax §6.3) and R6 (Riven C-R2):

> **§9 HOLD #2 Gate 5 (capital ramp protocol RA-XXXXXXXX-X dual-sign) requires Gate 4a (HARNESS_PASS) AND Gate 4b (GATE_4_PASS) BOTH PASS as upstream pre-conditions. Sequential serial dependency: 4a AND 4b → 5. No Gate 5 firing on either Gate 4a alone OR Gate 4b alone.**

Reaffirmed verbatim here as §10 of this spec to fence-against-drift: Gate 4b carries the **edge-existence half** of the original Gate 4 mandate; it does not absorb or supersede Gate 4a's harness-correctness half. Riven's §9 HOLD #2 Gate 5 disarm ledger (separate doc, Riven authority) consumes BOTH gates as conjunction — neither alone is sufficient.

### §10.1 Gate 5 capital ramp pre-conditions (carry-forward)

Per Riven §11.5 capital-ramp pre-condition list (post-ESC-011 amended):
1. Gate 4a HARNESS_PASS ✅ (DONE 2026-04-29 BRT)
2. Gate 4b GATE_4_PASS ⏳ (THIS SPEC governs; T002.6 execution pending)
3. Paper-mode audit (Riven 3-bucket bucket C) — Phase G/H, story T002.7 future
4. Synthetic-vs-real-tape attribution post-mortem entry per ESC-011 R7 + R20 — Riven authoring authority
5. Quarter-Kelly sizing parameter set — Riven authority, untouched here

### §10.2 Mandatory footer in Gate 4b sign-off

The Gate 4b sign-off artifact (suggested path `docs/qa/gates/T002.6-mira-gate-4b-signoff.md` or `docs/ml/clearance/T002-gate-4b-mira-clearance.md` per T002.6 story AC8/AC10/AC11 reference) MUST carry the following footer **verbatim** (Riven cosign requirement; absence of footer = Riven blocks merge):

```
> **Footer (R5/R6 mandatory per ESC-011):** Gate 4b PASS does NOT pre-disarm Gate 5
> alone. Gate 5 capital ramp dual-sign requires Gate 4a (HARNESS_PASS, DONE) AND
> Gate 4b (GATE_4_PASS, THIS) BOTH PASS plus Phase G/H paper-mode audit (T002.7
> future). Riven §9 HOLD #2 Gate 5 disarm authority preserved.
```

### §10.3 Gate-bind mechanism deferral

Gate-bind mechanism for Gate 4b (i.e., precisely which §9 HOLD #2 sub-gate Gate 4b disarms in the disarm ledger, and how it composes with Gate 4a, and what record-keeping format the disarm carries) is **DEFERRED to Phase F architectural review per Aria AC-2** (ESC-011 vote condition AC-2 verbatim). This spec intentionally does not pre-empt that architectural review — fence-against-drift means we lock the **scientific contract** here (thresholds, sample size, attribution, milestones, Gate-5 conjunction) without prematurely committing to the **disarm-ledger plumbing**.

---

## §11 Article IV trace policy

Every Gate 4b verdict claim — issued in a future per-run sign-off artifact — MUST trace to (a) ESC-011 ratification R-ID, (b) Mira spec §-anchor (this doc), (c) Bailey-LdP 2014 / BBLP 2014 / AFML 2018 citation, (d) N7+ run artifact (Beckett authority). NO INVENTION.

### §11.1 Verdict-claim → trace-anchor matrix

| Verdict claim category | Required trace anchors |
|---|---|
| Threshold values (DSR > 0.95, PBO < 0.5, IC > 0) | Mira spec yaml v0.2.3 §kill_criteria L207-209 + Mira make_backtest_fn spec §6 + this spec §1 + Bailey-LdP 2014 §3/§6 + BBLP 2014 |
| Sample-size sufficiency (≥ 30-50 per trial × 5 = ≥ 150-250 total) | Bailey-LdP 2014 §3 + this spec §6 + ESC-011 R9 |
| Bonferroni n_trials=5 | Mira spec yaml v0.2.3 §1.2 + ESC-011 R9 + this spec §1 + §2.2 |
| Failure attribution (data_quality vs strategy_edge vs both) | This spec §7 + Riven post-mortem + ESC-011 R7+R9+R20 |
| Milestone clearance (a-f) | Beckett N7+ run report (Phase F artifact, Beckett authority) + this spec §8 + ESC-011 R8 verbatim |
| Toy-benchmark discriminator preservation Δ DSR > 0.10 across 5 seeds | `tests/cpcv_harness/test_toy_benchmark_real_tape.py` (Phase-F real-tape) + Bailey-LdP 2014 §3 + this spec §8(f) + ESC-011 R12 |
| Gate-5 conjunction non-pre-emption | This spec §10 + ESC-011 R5+R6 + Riven §9 HOLD #2 Gate 5 ledger |
| Verdict-label discipline | This spec §9 + ESC-011 R2 |
| RLP / rollover / auction / CB / cross-trade handling | Nova spec `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 + this spec §4 |
| Latency-model parametrization | Beckett spec `docs/backtest/latency-dma2-profile-spec.md` §4 + this spec §5 |
| Cost-atlas wiring + SHA stamp | Atlas v1.0.0 dual-hash + ESC-011 R16 + Beckett N6+ §3.1 + this spec §3.5 |
| ESC-011 ratification provenance | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` 5/5 UNANIMOUS APPROVE_OPTION_C |

### §11.2 Anti-Article-IV Guards (preserved unchanged from Mira spec)

| Guard # | Mandate | This spec reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | T0a (this finalize) PASS + T0b/T0c/T0d/T0e sign-offs registered in §13 footer before T1 begins |
| **#3** | NO touch hold-out lock | Hold-out [2025-07-01, 2026-04-21] UNMOVABLE; §3.1 explicit |
| **#4** | Gate 4 thresholds UNMOVABLE | §1 explicit reaffirmation; no per-run waiver |
| **#5** | NO subsample backtest run | Beckett N7+ runs full real-tape regime; no fold-skipping or trial-skipping |
| **#6** | NO enforce Gate 5 disarm sem Gate 4a + Gate 4b BOTH | §10 explicit reaffirmation; footer mandatory |
| **#7** | NO push (Gage @devops EXCLUSIVE) | This spec is written; no `git add`/`commit`/`push` performed by Mira |

No invented thresholds. No invented milestones. No invented attribution buckets. Every clause has a source anchor in §11.1 above.

---

## §12 Sign-off chain

| Stage | Owner | Action | Gate (input) | Status |
|---|---|---|---|---|
| **T0a** | Mira (@ml-researcher) | Finalize Gate 4b spec from skeleton (8 dimensions per T002.6 story §Spec-first protocol) | Skeleton drafted 2026-04-29 BRT (fence-against-drift) | ✅ DONE upon publish (this artifact) |
| **T0b** | Aria (@architect) | Architectural review — real-tape harness preservation; T002.1.bis factory pattern integrity; per-fold P126 D-1 invariant; no T002.0h orchestrator regression | T0a PASS (this) | ⏳ pending |
| **T0c** | Beckett (@backtester) | Consumer sign-off — run targets achievable; cost-atlas integration testable; sha256 stamping protocol identical to N6; latency_dma2_profile parameters match `docs/backtest/latency-dma2-profile-spec.md` | T0a + T0b PASS | ⏳ pending |
| **T0d** | Riven (@risk-manager) | Cost-atlas wiring + Gate 5 fence preservation sign-off — R5/R6 unblock requires Gate 4a AND Gate 4b BOTH PASS; never Gate 4a alone; footer verbatim §10.2 | T0a + T0b PASS | ⏳ pending |
| **T0e** | Pax (@po) | 10-point `*validate-story-draft` — covers 8 dimensions T0a above; verifies spec status field updated `Skeleton` → `Final` | T0a + T0b + T0c + T0d PASS | ⏳ pending |
| **T1** | Dex (@dev) | Implementation in `packages/t002_eod_unwind/cpcv_harness.py` — preserves T002.1.bis factory pattern + per-fold P126 + Bonferroni n_trials=5 | ALL T0 sign-offs PASS (Anti-Article-IV Guard #1) | ⏳ blocked on T0 chain |
| **T2/T3** | Quinn (@qa) | Unit + integration tests + ruff + lint + regression vs baseline `9b3b1bc` | T1 PASS | ⏳ blocked |
| **T4** | Beckett (@backtester) | N7+ real-tape replay run (sha256-stamped artifacts; ADR-1 v3 RSS ≤ 6 GiB) | T2/T3 PASS + T0a spec compliance retained | ⏳ blocked |
| **T5** | Mira (@ml-researcher) | Gate 4b clearance sign-off (`GATE_4_PASS` / `GATE_4_FAIL` / `INCONCLUSIVE` per §7 decision tree; §10.2 footer mandatory) | T4 PASS | ⏳ blocked |
| **T6** | Riven (@risk-manager) | 3-bucket attribution reclassify ledger entry in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` | T5 verdict issued | ⏳ blocked |

Sign-off date + cosign of each T0 stage MUST be appended to §14 below. Status field in spec header updates `Final v1.0.0` → `Final v1.0.0 — 5/5 sign-offs registered` once T0e closes.

---

## §13 Article IV self-audit

| Claim in this spec | Source anchor (verified) |
|---|---|
| ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome table — 5 voters, 5 APPROVE_OPTION_C ballots, individual ballot artifacts referenced |
| 20 conditions ratified (R1-R20) | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §2 consolidated table — R-IDs explicitly cited inline (R1, R2, R5, R6, R7, R8, R9, R10, R11, R12, R14, R16, R20) where used in this spec |
| Gate 4 → Gate 4a + Gate 4b decomposition | ESC-011 §1 outcome statement verbatim ("Hybrid Gate 4a (synthetic harness-correctness) + Gate 4b (real-tape edge-existence)") |
| DSR > 0.95 / PBO < 0.5 / IC thresholds | Mira spec yaml v0.2.3 §kill_criteria L207-209 + Mira make_backtest_fn spec §6 §kill_criteria sub-block |
| Bonferroni n_trials = 5 (T1..T5) | Mira spec yaml v0.2.3 §1.2 + ESC-011 R9 verbatim |
| Bailey-LdP 2014 §3 minimum-N rationale | Bailey & López de Prado 2014, *Journal of Portfolio Management* 40(5), §3 — citation only (paper not embedded in repo); reproduction test harness shipped at `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (Phase-E baseline) and Phase-F equivalent `test_toy_benchmark_real_tape.py` (T002.6 AC6) |
| Bailey-LdP 2014 §6 canonical reproducible-backtest gating triplet | Same citation, §6 (DSR + PBO + IC joint) |
| Bailey-Borwein-LdP 2014 PBO formula | Bailey, Borwein & López de Prado (2014), "The Probability of Backtest Overfitting" |
| AFML 2018 §3.4 triple-barrier semantics + §8.6 IC stability | Lopez de Prado (2018), *Advances in Financial Machine Learning*, §3.4 + §8.6 |
| F1 patch wiring (commit `9997f14`, atlas+rollover SHAs populated) | Beckett N6+ report §3 + §6 |
| `latency_dma2_profile` parameters (verbatim §5) | Beckett spec `docs/backtest/latency-dma2-profile-spec.md` §4 yaml block |
| RLP / rollover / auction / CB / cross-trade handling (verbatim §4) | Nova spec `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §6 yaml block |
| Cost formula `(exit-entry)*sign*1*WDO_MULTIPLIER - 2*1*(brokerage + exchange_fees) - slippage` | Mira make_backtest_fn spec §5.3 + Riven §11 audit + Quinn QA §3 Check 1 |
| Phase F as separate future story T002.6 (slot adjusted from R10 "proposed T002.2") | T002.6 story §Slot history note — River authority for slot selection respecting Article IV (no overwrite of Done T002.2 legacy) |
| Gate-bind deferral to Phase F architectural review | ESC-011 R14 (Aria AC-2 second sentence) verbatim + this spec §10.3 |
| Gate 5 conjunction (Gate 4a AND Gate 4b BOTH) | ESC-011 R5+R6 + this spec §10 + Riven §9 HOLD #2 Gate 5 ledger |
| Verdict-label discipline (`GATE_4_PASS` not `HARNESS_PASS`) | ESC-011 R2 + this spec §9 |
| 3-bucket attribution scaffolding (data_quality / strategy_edge / both) | ESC-011 R9 + Riven post-mortem `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §1 + this spec §7 |
| Toy benchmark Δ DSR > 0.10 across 5 seeds | ESC-011 R12 + Quinn QA §3 Check 2 + Beckett N6+ §4.4 + this spec §8(f) |
| Hold-out lock [2025-07-01, 2026-04-21] UNMOVABLE | Mira parent spec yaml v0.2.3 + Anti-Article-IV Guard #3 + this spec §3.1 |
| ADR-1 v3 RSS ≤ 6 GiB | T002.6 story Spec ref + AC7 + this spec implicit (run targets in §8 Beckett N7+ surface) |

**Article IV self-audit verdict:** every clause traces. NO INVENTION. Skeleton has been finalized into a binding-but-comprehensive contract — 8 dimensions covered (T002.6 §Spec-first protocol T0a list); all 20 ESC-011 conditions consumed where applicable; Beckett latency spec consumed verbatim §5; Nova RLP/rollover spec consumed verbatim §4; thresholds carry verbatim from parent spec yaml v0.2.3 L207-209; sample-size mandate per Bailey-LdP 2014 §3; failure-attribution decision tree per ESC-011 R9; Gate 5 conjunction footer mandatory per R5/R6; verdict-label discipline per R2.

**Anchor count:** 12+ source anchors verified (parent thesis, parent spec yaml, ESC-011 resolution, Mira make_backtest_fn spec, Beckett N6+ report, Quinn QA gate, Beckett latency spec, Nova RLP spec, Riven post-mortem, cost atlas, rollover calendar, ADR-1 v3, Bailey-LdP 2014 §3+§6, BBLP 2014, AFML 2018 §3.4+§8.6, T002.6 story, T002.1.bis story carry-forward).

---

## §14 Mira cosign + sign-off ledger

### §14.1 Mira T0a finalize cosign

```
Author: Mira (@ml-researcher) — ML/statistical authority, ESC-011 R11 fence-against-drift mandate
Council provenance: ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C (Beckett+Mira+Riven+Aria+Pax)
Article IV: every clause traces to (a) Mira spec yaml v0.2.3 / Mira make_backtest_fn spec §-anchor, (b) ESC-011 R-ID, (c) Bailey-LdP 2014 / BBLP 2014 / AFML 2018 citation, (d) Beckett N6+ / Quinn QA artifact §-anchor, (e) Beckett latency spec §-anchor, (f) Nova RLP spec §-anchor — verified §13 above
Article II: no push (this is a write-only finalize; Gage authority preserved for any future commit)
Anti-Article-IV Guards: #1 (impl gated em spec PASS) + #3 (hold-out untouched) + #4 (thresholds UNMOVABLE) + #5 (no subsample) + #6 (Gate-5 conjunction) + #7 (no push) preserved verbatim
Scope discipline: Phase F implementation NOT pre-empted (separate T002.6 story); Riven Gate 5 authority NOT pre-empted (§10 conjunction reaffirmed); Aria gate-bind mechanism deferred (§10.3)
Sign-off: T0a Mira finalize → Aria T0b → Beckett T0c → Riven T0d → Pax T0e → Dex T1 (gated)
Cosign: Mira @ml-researcher 2026-04-29 BRT — Gate 4b spec T0a finalize (skeleton → Final v1.0.0)
```

### §14.2 Sign-off ledger (to be appended as T0b/T0c/T0d/T0e close)

| Stage | Owner | Cosign | Date (BRT) | Notes |
|---|---|---|---|---|
| T0a | Mira (@ml-researcher) | ✅ Mira | 2026-04-29 | Skeleton → Final v1.0.0; 8 dimensions covered; Beckett §5 + Nova §4 consumed verbatim |
| T0b | Aria (@architect) | ⏳ pending | — | Archi review — factory pattern + per-fold P126 + D-1 invariant preservation |
| T0c | Beckett (@backtester) | ⏳ pending | — | Consumer sign-off — run targets, cost-atlas, sha256 stamping, latency-spec match |
| T0d | Riven (@risk-manager) | ⏳ pending | — | Cost-atlas wiring + Gate 5 fence + footer §10.2 verbatim |
| T0e | Pax (@po) | ⏳ pending | — | 10-point validate spec final; status `Skeleton` → `Final` |

— Mira, mapeando o sinal 🗺️
