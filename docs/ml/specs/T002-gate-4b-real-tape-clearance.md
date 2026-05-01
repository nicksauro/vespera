# T002 — Gate 4b Real-Tape Edge-Existence Clearance Spec (Final v0.3.0)

> **Author:** Mira (@ml-researcher) — ML/statistical authority
> **Date (BRT):** 2026-04-29 (skeleton drafted pre-merge ESC-011 R11; finalized T0a same day) — **2026-04-30 BRT v1.1.0 Phase F2 Amendment** appended (§15 IC Pipeline Wiring Spec §15.1..§15.12; §12 sign-off chain extended F2-T0a..F2-T6) — **2026-04-30 BRT v1.2.0 Phase G OOS Unlock Amendment** appended (§15.13 NEW; §12.2 sign-off chain extended F2-T8-T0a..F2-T8-T7; §14.4 cosign ledger Round 3 added) per ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification — **2026-05-01 BRT v0.3.0 Auction State Block Correction** appended (§15.14 NEW; semantic correction of §4 auction block per Nova authoritative confirmation `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md`)
> **Status:** **Final v0.3.0** — Auction state block semantic correction applied per Nova authoritative confirmation 2026-05-01 BRT (§15.14 NEW; semver re-baselined from v1.2.0 → v0.3.0 to reflect MANIFEST R15 minor-bump for major==0 spec series — v1.x labeling was internal Phase F/F2/G iteration counter, v0.x is the canonical Mira-spec versioning under Anti-Article-IV Guard #4 thresholds-frozen + major==0 pre-stable governance). v1.0.0 skeleton finalized 2026-04-29 BRT; v1.1.0 (2026-04-30 BRT) appended §15.1..§15.12 IC Pipeline Wiring Spec; v1.2.0 (2026-04-30 BRT) appended §15.13 Phase G OOS Unlock Protocol per ESC-012; v0.3.0 (2026-05-01 BRT) appends §15.14 Auction State Block Correction per Nova authoritative confirmation. Body §0-§14 v1.0.0 content UNCHANGED + §15.1-§15.12 v1.1.0 content UNCHANGED + §15.13 v1.2.0 content UNCHANGED — append-only revision.
> **Phase F2 Amendment 2026-04-30 (v1.1.0):** §15 NEW (IC Pipeline Wiring Spec, sub-sections §15.1..§15.12); §12 extended F2-T0a..F2-T6 (sign-off chain for §15 amendment + N7-prime re-run + re-clearance); Change Log entry below. NO mutation of §1 thresholds (Anti-Article-IV Guard #4 preserved); NO mutation of hold-out lock; NO mutation of Round 1 T5 sign-off.
> **Phase G OOS Unlock Amendment 2026-04-30 (v1.2.0):** §15.13 NEW (Phase G OOS Unlock Protocol — 13 sub-sections §15.13.1..§15.13.13); §12.2 sign-off chain extended F2-T8-T0a..F2-T8-T7 (Round 3 — spec amendment + Phase G N8 OOS run + re-clearance + reclassify + close); §14.4 cosign ledger added; Change Log entry below. Authority: ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B + 17 conditions R1-R17 (`docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.1 R2). NO mutation of §1 thresholds (Anti-Article-IV Guard #4 preserved); NO mutation of hold-out lock policy (Phase G unlock IS the authorized §15.10 transition, NOT a guard violation per ESC-012 R10 K1 strict bar UNMOVABLE preservation); NO mutation of §0-§14 v1.0.0 body content; NO mutation of §15.1-§15.12 v1.1.0 content; NO mutation of Round 1 T5 sign-off; NO mutation of Round 2 F2-T5 sign-off (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` OBS-1 surfaced).
> **Auction State Block Correction Amendment 2026-05-01 (v0.3.0):** §15.14 NEW (Auction State Block Correction — 7 sub-sections §15.14.1..§15.14.7 covering: source provenance Nova confirmation cross-checked B3 official + 6 secondary sources; semantic correction WDO has SINGLE open auction at 09:00 sharp + settlement window 15:50-16:00 VWAP; NO close auction; triple-barrier 17:55 vertical SEMANTICS CORRECTED to "5min buffer before continuous close 18:00" NOT "boundary with auction"; §4 auction state block updated yaml — Nova §4 verbatim consumption; carry-forward implications T002 retire artifacts Round 1+2+3+3.1 NOT INVALIDATED — DSR/PBO/IC interpretations stand because triple-barrier 17:55 was conservative buffer not auction boundary, so cost/PnL computation correct, only DOCUMENT semantics corrected; H_next-1 successor inherits CORRECTED auction block; Article IV self-audit 7 anchors). §12 sign-off chain extended for v0.3.0 (single-stage Mira semantic-correction publish — no re-run required because triple-barrier exit timestamp 17:55 BRT operational rule UNCHANGED). Authority: Nova authoritative finding `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` (270 lines, 8 source anchors B3 official). NO mutation of §1 thresholds (Anti-Article-IV Guard #4 preserved — DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE); NO mutation of triple-barrier 17:55 vertical timestamp (UNMOVED operationally — only the documented SEMANTICS corrected from "auction boundary" to "5min pre-close buffer"); NO mutation of Round 1 T5 sign-off; NO mutation of Round 2 F2-T5 sign-off; NO mutation of Round 3 F2-T8-T5 sign-off; NO mutation of Round 3.1 verdict (T002 RETIRE FINAL stands per spec §0 falsifiability — DSR=0.206 strict bar fail; correction here is semantic/documentation, not statistical interpretation); NO mutation of §0-§14 v1.0.0 + §15.1-§15.13 v1.1.0/v1.2.0 body content — append-only revision.
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

### §12.1 Phase F2 amendment sign-off chain (added 2026-04-30 BRT v1.1.0)

The following stages F2-T0a..F2-T6 govern the §15 IC Pipeline Wiring Spec amendment and its downstream Beckett N7-prime re-run + Mira re-clearance + Riven reclassify. Decoupled from T0a..T6 above per Aria Option D (separate IC orchestration module in `vespera_metrics`); N7-prime re-run REQUIRED because `TradeRecord` shape changes per §15.3 (additive frozen-dataclass extension; semver minor bump in `t002_eod_unwind` package).

| Stage | Owner | Action | Gate (input) | Status |
|---|---|---|---|---|
| **F2-T0a** | Mira (@ml-researcher) | Apply §15 IC Pipeline Wiring Spec amendment (11 sub-sections §15.1..§15.11) per deep audit `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` §6 + Aria Option D + Beckett consumer audit + Sable F-01..F-04 | Round 1 T5 sign-off + Aria archi review APPROVE_OPTION_D + Beckett consumer audit + Sable 8-finding audit + this v1.1.0 publish | ⏳ in-progress (this artifact) |
| **F2-T0b** | Aria (@architect) | Validate §15 against Aria archi review `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` C-A1..C-A7 conditions (separate orchestration module in `vespera_metrics`; factory contract preservation; hold-out lock interaction) | F2-T0a PASS | ⏳ pending |
| **F2-T0c** | Beckett (@backtester) | Consumer sign-off — additive `TradeRecord.predictor_signal_per_trade` + `.forward_return_at_1755_pts` fields wired in `make_backtest_fn` factory; smoke-fixture viability; wall-time budget §15.9 (~100s incremental, non-blocking C1') | F2-T0a + F2-T0b PASS | ⏳ pending |
| **F2-T0d** | Riven (@risk-manager) | Gate 5 fence preservation §15.10 + post-mortem ledger entry path (bucket A `IC_pipeline_wiring_gap` CLOSED upon F2-T5; new entry per F2-T4 verdict) | F2-T0a + F2-T0b PASS | ⏳ pending |
| **F2-T0e** | Pax (@po) | 10-point `*validate-story-draft` over §15 amendment scope (covers §15.1..§15.11 dimensions; verifies status field updated v1.0.0 → v1.1.0; sign-off chain extended; Anti-Article-IV Guard #8 added; no §1-§14 mutation) | F2-T0a + F2-T0b + F2-T0c + F2-T0d PASS | ⏳ pending |
| **F2-T1** | Dex (@dev) | Implementation per §15.2-§15.6 — `_compute_ic_in_sample` helper in `vespera_metrics` (Aria Option D); `ic_bootstrap_ci` (paired PCG64 seed=42, n=10000); `TradeRecord.predictor_signal_per_trade` + `.forward_return_at_1755_pts` extension; `_run_phase` wiring at `scripts/run_cpcv_dry_run.py:~1050-1071` between fanout return and `ReportConfig` construction; `MetricsResult.ic_status` + `.ic_holdout_status` (`computed`/`deferred`/`not_computed`/`inconclusive_underN`); `evaluate_kill_criteria` raises `InvalidVerdictReport` per §15.5 Anti-Article-IV Guard #8 | ALL F2-T0 sign-offs PASS (Anti-Article-IV Guard #1) | ⏳ blocked on F2-T0 chain |
| **F2-T2/T3** | Quinn (@qa) | Tests per §15.8 — 4 NEW tests in `tests/vespera_metrics/test_ic_pipeline_wired.py` (`test_ic_computed_non_zero`, `test_ic_deterministic`, `test_ic_status_flag`, `test_ic_inconclusive_path`) + ruff + lint + regression vs Round 1 T4 baseline (TradeRecord shape change is additive — no behavioural regression on existing fields) | F2-T1 PASS | ⏳ blocked |
| **F2-T4** | Beckett (@backtester) | N7-prime real-tape replay run — REQUIRED because `TradeRecord` shape changes per §15.3 (Aria Option D decoupling cannot avoid N7-prime; cached run-225 artifacts cannot be re-used for IC compute even though path-PnL data unchanged in mathematical content). New `run_id` generated; sha256 stamps regenerated; ADR-1 v3 RSS ≤ 6 GiB; cost atlas + rollover calendar SHAs identical to Round 1 T4 | F2-T2/T3 PASS + F2-T0a..F2-T0e spec compliance retained | ⏳ blocked |
| **F2-T5** | Mira (@ml-researcher) | Gate 4b re-clearance sign-off — verdict possibilities `GATE_4_PASS`, `GATE_4_FAIL_strategy_edge`, `GATE_4_FAIL_data_quality` (recurrence with new bucket attribution), `GATE_4_FAIL_both`, or `INCONCLUSIVE` per §7 decision tree; §10.2 Gate 5 footer mandatory; Anti-Article-IV Guard #8 verdict-issuing protocol enforced (no `K_FAIL` emitted with `ic_status != 'computed'`) | F2-T4 PASS | ⏳ blocked |
| **F2-T6** | Riven (@risk-manager) | 3-bucket attribution reclassification — bucket A `IC_pipeline_wiring_gap` CLOSED in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`; new entry per F2-T4 verdict (bucket B `strategy_edge_confirmed`/`strategy_edge_failed`, bucket C `data_quality_addressed_then_edge_falsified`, or `both` disambiguation per §7) | F2-T5 verdict issued | ⏳ blocked |

Round 1 T0a..T6 chain (Phase F skeleton-finalize → Beckett N7 → Mira clearance → Riven reclassify) PRESERVED above without mutation. Phase F2 amendment chain F2-T0a..F2-T6 is **append-only** continuation per Pax governance + ESC-011 R10 (Phase F as separate story T002.6) + Mira deep audit Round 1 attribution finding (IC pipeline wiring gap is bucket A `harness_gap` not bucket B `strategy_edge`).

### §12.2 Phase G OOS unlock sign-off chain (added 2026-04-30 BRT v1.2.0)

The following stages F2-T8-T0a..F2-T8-T7 govern the §15.13 Phase G OOS Unlock Protocol amendment and its downstream Beckett N8 OOS run + Mira F2-T9 re-clearance Round 3 (supersedes Round 2 via append-only ledger entry) + Riven Round 3 reclassify + Pax T002.7 close. Authority chain: ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification (`docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.1 R2) + Aria F2-T0b' archi review APPROVE_OPTION_D + 7 conditions C-A8..C-A14 carry-forward + Mira F2-T5 Round 2 OBS-1 surface + Riven minority Path C explicit fallback preserved.

| Stage | Owner | Action | Gate (input) | Status |
|---|---|---|---|---|
| **F2-T8-T0a** | Mira (@ml-researcher) | Apply §15.13 Phase G OOS Unlock Protocol amendment (13 sub-sections §15.13.1..§15.13.13) per ESC-012 R2 ratification + Aria F2-T0b' APPROVE_OPTION_D + 7 conditions C-A8..C-A14 + Mira F2-T5 Round 2 OBS-1 | Round 1 T5 sign-off + Round 2 F2-T5 sign-off + ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B + 17 conditions R1-R17 + this v1.2.0 publish | ⏳ in-progress (this artifact) |
| **F2-T8-T0b** | Aria (@architect) | Small archi review — gated em F2-T8-T0a; verify C-A8/C-A9 carry-forward conditions held (factory contract preservation across Phase F2 → Phase G transition; Aria Option D module placement intact in `vespera_metrics`); no new architectural surface introduced (only `holdout_locked` flag flip + `--phase G` CLI flag) | F2-T8-T0a PASS | ⏳ pending |
| **F2-T8-T0c** | Beckett (@backtester) | Consumer sign-off — Phase G run plan + budget; smoke-fixture viability OOS context; wall-time §15.13.10 (~3h wall, ~600 MB RSS peak); cost-atlas `bbe1ddf7…` + rollover `c6174922…` SHAs IDENTICAL F2 per ESC-012 R6; new `run_id` generation protocol; ADR-1 v3 RSS ≤ 6 GiB | F2-T8-T0a + F2-T8-T0b PASS | ⏳ pending |
| **F2-T8-T0d** | Riven (@risk-manager) | Cost-atlas + Gate 5 fence preserve (carry-forward) — §10.2 footer verbatim mandatory; §15.13.6 K1 strict bar UNMOVABLE preserved; bucket A `IC_pipeline_wiring_gap` CLOSED upon F2-T5 Round 2 (no change); new entry path per F2-T8-T4 verdict (bucket B/C/both per §15.13.8 + §7) | F2-T8-T0a + F2-T8-T0b PASS | ⏳ pending |
| **F2-T8-T0e** | Pax (@po) | 10-point `*validate-story-draft` over §15.13 amendment scope (covers §15.13.1..§15.13.13 dimensions; verifies status field updated v1.1.0 → v1.2.0; sign-off chain extended F2-T8-T0a..F2-T8-T7; Anti-Article-IV Guards #3 + #4 + #8 preserved verbatim; no §1 threshold mutation; no hold-out lock policy mutation; no §0-§14 + §15.1-§15.12 mutation); register PRR-20260430-1 via `python scripts/pax_cosign.py register` (hash-freeze 4-branch disposition rule §15.13.8 BEFORE N8 run per ESC-012 R3) | F2-T8-T0a + F2-T8-T0b + F2-T8-T0c + F2-T8-T0d PASS | ⏳ pending |
| **F2-T8-T1** | Dex (@dev) | Implementation per §15.13.2 — small ~10-20 LoC change at `scripts/run_cpcv_dry_run.py:~1050-1071` insertion zone: (a) flip `holdout_locked=False` for Phase G context; (b) introduce `--phase G` CLI flag gating the unlock; (c) propagate `MetricsResult.ic_holdout_status` `'deferred' → 'computed'`; preserve Anti-Article-IV Guard #8 verdict-issuing protocol; no `TradeRecord` shape change (F2 v1.1.0 fields sufficient — additive frozen-dataclass extension already in place per F2-T1) | ALL F2-T8-T0 sign-offs PASS (Anti-Article-IV Guard #1) + PRR-20260430-1 hash-frozen | ⏳ blocked on F2-T8-T0 chain |
| **F2-T8-T2/T3** | Quinn (@qa) | QA Gate 8-point + Check 8 retained — Phase G unlock invariant tests (`holdout_locked=False` propagation per §15.13.2 mechanism; `ic_holdout_status='computed'` invariant per §15.6); regression vs F2 N7-prime baseline (TradeRecord shape unchanged — F2-T2/T3 4 NEW tests in `tests/vespera_metrics/test_ic_pipeline_wired.py` continue to PASS); Article IV trace test for §15.13 anchors (17 source anchors per §15.13.13); ruff + lint + regression | F2-T8-T1 PASS | ⏳ blocked |
| **F2-T8-T4** | Beckett (@backtester) | N8 OOS run — Phase G window 2025-07-01..2026-04-21 (~10 months ~210 trading days; ~3000-4000 events × 5 trials × 45 paths CPCV combinatorial); ~3h wall + ~600 MB RSS peak per §15.13.10; sha256-stamped new `run_id`; cost atlas `bbe1ddf7…` + rollover calendar `c6174922…` SHAs IDENTICAL F2 per ESC-012 R6; engine_config_sha256 `ccfb575a…` IDENTICAL F2; ADR-1 v3 RSS ≤ 6 GiB; predictor↔label IDENTICAL F2 per ESC-012 R7 (predictor=`-intraday_flow_direction`, label=`ret_forward_to_17:55_pts`); single-shot OOS discipline per ESC-012 R9 (cannot re-run / expand / reformulate / average) | F2-T8-T2/T3 PASS + F2-T8-T0a..F2-T8-T0e spec compliance retained + PRR-20260430-1 hash-frozen | ⏳ blocked |
| **F2-T8-T5** | Mira (@ml-researcher) | F2-T9 Gate 4b re-clearance Round 3 sign-off (supersedes F2-T5 Round 2 via append-only ledger entry — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md`) — verdict per §15.13.8 4-branch disposition rule (`PASS K1+K2+K3` → ESC-013 escalate / `FAIL_K3_collapse` → T002 falsified clean / `FAIL_K1+K3_sustains` → costed_out_edge OOS-confirmed / `INCONCLUSIVE` → ESC escalation); §10.2 Gate 5 footer mandatory; Anti-Article-IV Guard #8 verdict-issuing protocol enforced (`ic_holdout_status='computed'` invariant — `K_FAIL` cannot be emitted with `ic_holdout_status != 'computed'`); §15.13.5 decay test full evaluation (`IC_holdout > 0.5 × IC_in_sample` BINDING per K3 sub-clause); §15.13.6 K1 strict bar UNMOVABLE preservation; §15.13.7 OOS one-shot discipline | F2-T8-T4 PASS | ⏳ blocked |
| **F2-T8-T6** | Riven (@risk-manager) | 3-bucket attribution reclassify Round 3 — `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` append-only ledger entry; bucket A `IC_pipeline_wiring_gap` CLOSED (carry-forward Round 2); new entry per F2-T8-T4 verdict (bucket B `strategy_edge_falsified_OOS` / bucket B `costed_out_edge_OOS_confirmed` / bucket C `data_quality_addressed_then_edge_OOS_falsified` / `both` disambiguation per §15.13.8 + §7) | F2-T8-T5 verdict issued | ⏳ blocked |
| **F2-T8-T7** | Pax (@po) | T002.7 close per outcome — story status transition per §15.13.8 disposition rule branch: PASS → ESC-013 escalate (council convene to ratify pathway to T002.7 Phase G/H paper-mode audit; K1 strict bar UNMOVABLE preserved upstream of capital ramp per ESC-012 R10) / FAIL_K3_collapse → T002 falsified clean (epic deprecate; retire ceremony at `docs/risk/post-mortems/T002-retire-ceremony-{date}.md`; institutional knowledge captured for H_next) / FAIL_K1+K3_sustains → T002 retire with refined diagnostic (institutional knowledge for H_next on cost-atlas calibration / latency-budget refinement / sizing economics) / INCONCLUSIVE → ESC escalation defer to council | F2-T8-T6 reclassify issued | ⏳ blocked |

Round 1 T0a..T6 + Round 2 F2-T0a..F2-T6 chains PRESERVED above without mutation. Phase G OOS unlock chain F2-T8-T0a..F2-T8-T7 is **append-only** Round 3 continuation per Pax governance + ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification + Mira F2-T5 Round 2 sign-off OBS-1 surface (decay test deferred under `ic_holdout_status='deferred'` Phase F2 → activated under `ic_holdout_status='computed'` Phase G).

Riven minority Path C explicit fallback preserved per ESC-012 ballot dissent: IF Phase G run cannot proceed within 14 calendar days (i.e. by 2026-05-14 BRT), retire-clean Path C activates (T002 retire without OOS measurement; institutional knowledge captured per Riven dissent rationale).

### §12.3 Auction state block correction sign-off (added 2026-05-01 BRT v0.3.0)

The following single stage governs the §15.14 Auction State Block Correction amendment. **No re-run required** because the triple-barrier 17:55 BRT vertical exit timestamp operational rule is UNCHANGED — only the documented SEMANTICS of that timestamp is corrected (from "boundary with closing auction" to "5min conservative buffer before continuous close at 18:00"). Round 1 + Round 2 + Round 3 + Round 3.1 verdict ledgers are NOT INVALIDATED; the cost/PnL computation produced by the existing N7 / N7-prime / N8 runs is mathematically correct because the exit timestamp it consumed was the same operational rule that v0.3.0 reaffirms — only the prose explanation of WHY 17:55 was chosen is corrected.

| Stage | Owner | Action | Gate (input) | Status |
|---|---|---|---|---|
| **v0.3.0-T0a** | Mira (@ml-researcher) | Apply §15.14 Auction State Block Correction amendment — consume Nova `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` §4 yaml block verbatim; update §4.1 auction sub-block via §15.14.4 carry-forward reference (§4 v1.0.0 prose preserved verbatim per append-only governance; §15.14 supersedes for semantic interpretation — readers consult §15.14.4 for canonical Nova-authoritative auction state block); Article IV self-audit §15.14.7 (7 anchors); v1.2.0 → v0.3.0 semver re-baseline per MANIFEST R15 major==0 governance | Round 3.1 T002 RETIRE FINAL verdict + Nova authoritative confirmation 2026-05-01 BRT + 8 source anchors B3 official | ✅ in-progress (this artifact) |

Round 1 T0a..T6 + Round 2 F2-T0a..F2-T6 + Round 3 F2-T8-T0a..F2-T8-T7 chains PRESERVED above without mutation. v0.3.0 amendment chain v0.3.0-T0a is **append-only** Round 3.5 continuation per Pax governance + Nova authoritative finding.

**No downstream re-run / re-clearance / reclassify required:** the Round 3.1 verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` if extant; or per Pax T002.7 close ledger) STANDS per spec §0 falsifiability — DSR=0.206 strict bar fail under K1>0.95 UNMOVABLE was the statistical interpretation result; the auction state correction here is purely SEMANTIC/DOCUMENTATION (corrects the prose explanation of the 17:55 timestamp's relationship to nonexistent close auction) and does NOT alter any numeric threshold, label, predictor, or backtest computation. Carry-forward implications fully enumerated §15.14.5.

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

### §14.3 Phase F2 amendment cosign + sign-off ledger (added 2026-04-30 BRT v1.1.0)

```
Author: Mira (@ml-researcher) — ML/statistical authority
Phase F2 amendment authority: Mira deep audit `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` §6 (Recommended Phase F2 spec amendment §15) + Aria archi review `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` (APPROVE_OPTION_D — separate IC orchestration module in vespera_metrics; 7 conditions C-A1..C-A7) + Beckett consumer audit `docs/backtest/T002.6-beckett-consumer-signoff.md` §T0c + Sable audit `docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md` (8 findings — F-01..F-04 procedural recommendations consumed)
Article IV: every clause in §15.1-§15.11 traces to (a) Mira deep audit §-anchor, (b) Aria archi review C-A1..C-A7 condition, (c) Beckett consumer audit §T0c, (d) Sable F-01..F-04 finding, (e) Bailey-LdP 2014 §3 / AFML §8.6 / Efron 1979 percentile bootstrap citation — verified §15 self-audit row below
Article II: no push (this is a write-only amendment; Gage authority preserved for any future commit)
Anti-Article-IV Guards: #1-#7 preserved verbatim; **Guard #8 NEW (§15.5)** — verdict-issuing protocol forbidding K_FAIL emission while `*_status != 'computed'`; Guards collectively cumulative, council-ratification path is F2-T0a..F2-T0e cosign chain (§12.1)
Scope discipline: NO §1 thresholds mutation (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0); NO Round 1 T5 sign-off mutation; NO hold-out lock mutation (Anti-Article-IV Guard #3); NO §0-§14 v1.0.0 body content mutation — append-only revision per Pax governance
Sign-off: F2-T0a Mira amendment → F2-T0b Aria validate → F2-T0c Beckett consumer → F2-T0d Riven preserve → F2-T0e Pax 10-point validate → F2-T1 Dex impl → F2-T2/T3 Quinn QA → F2-T4 Beckett N7-prime re-run (decoupled per Aria Option D — re-run necessário porque TradeRecord shape muda per §15.3) → F2-T5 Mira re-clearance → F2-T6 Riven reclassify
Cosign: Mira @ml-researcher 2026-04-30 BRT — F2-T0a spec amendment §15 IC Pipeline Wiring Spec applied
```

| Stage | Owner | Cosign | Date (BRT) | Notes |
|---|---|---|---|---|
| F2-T0a | Mira (@ml-researcher) | ✅ Mira | 2026-04-30 | §15 IC Pipeline Wiring Spec applied (11 sub-sections); v1.0.0 → v1.1.0 bump; §12.1 sign-off chain extended F2-T0a..F2-T6; Anti-Article-IV Guard #8 added §15.5; Change Log entry below; Aria Option D module placement (`vespera_metrics`) honored |
| F2-T0b | Aria (@architect) | ⏳ pending | — | Validate §15 against C-A1..C-A7 conditions in archi review |
| F2-T0c | Beckett (@backtester) | ⏳ pending | — | Consumer sign-off — additive `TradeRecord` fields wired in `make_backtest_fn`; smoke fixture; wall-time §15.9 |
| F2-T0d | Riven (@risk-manager) | ⏳ pending | — | Gate 5 fence preservation §15.10 + post-mortem ledger entry path |
| F2-T0e | Pax (@po) | ⏳ pending | — | 10-point validate §15 amendment scope; verifies v1.0.0 → v1.1.0; sign-off chain extended; no §1-§14 mutation |

### §14.4 Phase G OOS unlock cosign + sign-off ledger (added 2026-04-30 BRT v1.2.0)

```
Author: Mira (@ml-researcher) — ML/statistical authority
Phase G OOS unlock authority: ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification (`docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.1 R2 — pre-authored Phase G unlock per spec §3.1 + §15.10) + Aria F2-T0b' archi review APPROVE_OPTION_D + 7 conditions C-A8..C-A14 carry-forward (`docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md`) + Mira F2-T5 Round 2 sign-off OBS-1 surface (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §6) + Riven minority Path C explicit fallback preserved (`docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-riven-vote.md`)
Article IV: every clause in §15.13.1-§15.13.13 traces to (a) ESC-012 ratification R1-R17, (b) Mira spec § anchor (§1 thresholds + §3.1 hold-out + §6 sample-size + §7 attribution + §10.2 footer + §15.1-§15.12 IC pipeline + §15.13 self), (c) PRR-20260430-1 disposition rule (hash-frozen BEFORE N8 run via `python scripts/pax_cosign.py register`), (d) N8 run artifact (Beckett OOS run report, sha256-stamped, ADR-1 v3 RSS verified), (e) Bailey-LdP 2014 §3+§6 / Bailey-Borwein-LdP 2014 / AFML 2018 §8.6 citation — verified §15.13.13 self-audit row above
Article II: no push (this is a write-only amendment; Gage authority preserved for any future commit)
Anti-Article-IV Guards: #1-#8 preserved verbatim (Guard #4 DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE; Guard #3 hold-out window structurally preserved — Phase G unlock IS the authorized §15.10 transition pre-authored at spec §3.1, NOT a guard violation per ESC-012 R10 K1 strict bar UNMOVABLE preservation; Guard #5 OOS one-shot discipline extended per ESC-012 R9 — cannot re-run / expand trials / reformulate / average; Guard #8 verdict-issuing protocol — `K_FAIL` cannot be emitted with `ic_holdout_status != 'computed'` in Phase G context)
Scope discipline: NO §1 thresholds mutation (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0); NO Round 1 T5 sign-off mutation; NO Round 2 F2-T5 sign-off mutation (F2-T8-T5 Round 3 supersedes via append-only ledger entry NOT mutation); NO hold-out lock policy mutation (Phase G unlock IS authorized §15.10 transition); NO §0-§14 v1.0.0 body content mutation; NO §15.1-§15.12 v1.1.0 content mutation — append-only revision per Pax governance
Sign-off: F2-T8-T0a Mira amendment → F2-T8-T0b Aria small archi review → F2-T8-T0c Beckett consumer (Phase G run plan + budget) → F2-T8-T0d Riven (cost-atlas + Gate 5 fence preserve) → F2-T8-T0e Pax 10-point validate amendment + register PRR-20260430-1 → F2-T8-T1 Dex caller wiring (`holdout_locked=False` + `--phase G` flag, ~10-20 LoC) → F2-T8-T2/T3 Quinn QA Gate (8-point + Check 8 retained) → F2-T8-T4 Beckett N8 OOS run (~3h wall, ~600 MB RSS peak) → F2-T8-T5 Mira F2-T9 re-clearance Round 3 (supersedes Round 2 via append-only ledger) → F2-T8-T6 Riven 3-bucket reclassify Round 3 → F2-T8-T7 Pax T002.7 close per outcome
Cosign: Mira @ml-researcher 2026-04-30 BRT — F2-T8-T0a spec amendment §15.13 Phase G OOS Unlock Protocol applied (v1.1.0 → v1.2.0)
```

| Stage | Owner | Cosign | Date (BRT) | Notes |
|---|---|---|---|---|
| F2-T8-T0a | Mira (@ml-researcher) | ✅ Mira | 2026-04-30 | §15.13 Phase G OOS Unlock Protocol applied (13 sub-sections §15.13.1..§15.13.13); v1.1.0 → v1.2.0 bump; §12.2 sign-off chain extended F2-T8-T0a..F2-T8-T7; §14.4 cosign ledger added; Change Log entry below; ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification operationalized; 17 conditions R1-R17 consumed where applicable; Aria F2-T0b' APPROVE_OPTION_D + 7 conditions C-A8..C-A14 carry-forward; Mira F2-T5 Round 2 OBS-1 fix activated (decay test full evaluation under `ic_holdout_status='computed'`); Riven minority Path C explicit fallback preserved (14-day window 2026-05-14 BRT) |
| F2-T8-T0b | Aria (@architect) | ⏳ pending | — | Small archi review — verify C-A8/C-A9 carry-forward conditions held; no new architectural surface (only `holdout_locked` flag flip + `--phase G` CLI flag) |
| F2-T8-T0c | Beckett (@backtester) | ⏳ pending | — | Consumer sign-off — Phase G run plan + budget; smoke-fixture viability OOS context; wall-time §15.13.10; cost-atlas + rollover SHAs IDENTICAL F2 per ESC-012 R6; new `run_id` generation |
| F2-T8-T0d | Riven (@risk-manager) | ⏳ pending | — | Cost-atlas + Gate 5 fence preserve (carry-forward) §10.2 footer verbatim; §15.13.6 K1 strict bar UNMOVABLE preserved; bucket A CLOSED carry-forward; new entry path per F2-T8-T4 verdict |
| F2-T8-T0e | Pax (@po) | ⏳ pending | — | 10-point validate §15.13 amendment scope; verifies v1.1.0 → v1.2.0; sign-off chain extended F2-T8-T0a..F2-T8-T7; Anti-Article-IV Guards #3 + #4 + #8 preserved; register PRR-20260430-1 via `python scripts/pax_cosign.py register` (hash-freeze 4-branch disposition rule §15.13.8 BEFORE N8 run per ESC-012 R3) |

---

## §15 IC Pipeline Wiring Spec (Phase F2 amendment 2026-04-30 BRT v1.1.0)

> **Provenance:** This §15 is the operationalization of Mira deep audit `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` §6 (Recommended Phase F2 spec amendment) + Aria archi review `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` (APPROVE_OPTION_D — separate IC orchestration module in `vespera_metrics`; conditions C-A1..C-A7) + Beckett consumer audit `docs/backtest/T002.6-beckett-consumer-signoff.md` §T0c (additive `TradeRecord` fields, smoke fixture viability, wall-time budget) + Sable audit `docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md` F-01..F-04 procedural recommendations.

> **Scope discipline:** §15 ADDS a new section to the Gate 4b spec. It does NOT mutate §1 thresholds (Anti-Article-IV Guard #4 honored: DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE), §3 real-tape data interface, §4 Nova RLP, §5 Beckett latency, §6 sample-size mandate, §7 3-bucket attribution, §8 milestones (a-f), §9 verdict-label discipline, §10 Gate 5 conjunction, §11 Article IV trace, §12 sign-off chain (extends in §12.1, does not mutate), §13 self-audit, or §14 cosign ledger. Hold-out lock UNTOUCHED. Round 1 T5 sign-off UNMOVED. Append-only revision.

### §15.1 IC measurement semantics (BINDING)

Per §1.4 of `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` and §1 K3 row of this spec — IC is computed at the **per-event** level (not per-fold-aggregate), under the C1 paradigm (forward return at 17:55 BRT) as primary binding measurement, with C2 (PnL after triple-barrier exit) as robustness check:

```
Primary (BINDING for K3 verdict):
    IC_spearman_C1 = Spearman_rank_correlation(
        predictor = (-intraday_flow_direction)_per_event,  # sign of fade direction
        label     = ret_forward_to_17:55_per_event,         # raw 17:55 close-to-entry-price return, in WDO points
        sample    = events ∈ in_sample_window AND filter_active(event)
    )

Secondary (robustness, reported alongside):
    IC_spearman_C2 = Spearman_rank_correlation(
        predictor = (-intraday_flow_direction)_per_event,
        label     = pnl_rs_per_event,                       # actual realized PnL after triple-barrier exit (existing TradeRecord.pnl_rs)
        sample    = same as C1
    )

K3 verdict consumes C1 (primary). C2 is reported alongside in MetricsResult for
cross-checking. Large divergence between C1 and C2 surfaces as information for
Riven 3-bucket attribution (Phase G/H downstream); does NOT alter Phase F2 verdict.

Filter (per H1 alternative thesis from Q4 of thesis doc):
    filter_active(event) =
        |intraday_flow_magnitude_at_entry| > P_lower_or_upper_for_trial AND
        ATR_dia_ratio ∈ [P20, P80]

Hold-out lock (Anti-Article-IV Guard #3 — UNMOVABLE):
    Phase F2 measures IC_in_sample only.
    IC_holdout is DEFERRED to Phase G hold-out unlock.
    Phase F2 K3 PASS = (IC_in_sample > 0) AND (CI95_lower > 0) (strict reading per §1 K3 row).
    K3 decay sub-clause (rolling-window decay < 1 σ rolling stdev preserves in-sample sign) is Phase G; not Phase F2.
```

**Authoritative anchors:** `docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md` Q4 + H1; this spec §1 K3 row; AFML §8.6 (IC stability); Bailey-LdP 2014 §3 (minimum-N reproducibility floor). Predictor sign convention: `predictor = -intraday_flow_direction` because the strategy **fades** the intraday flow — when flow direction is positive (buying pressure intraday), the strategy goes **short** at entry, expecting reversion to 17:55 close; therefore the predictor of expected forward return is the NEGATIVE of intraday flow direction. Per-event paradigm because CPCV path-PnL aggregates obscure event-level discriminator power; per-event IC is the canonical Spearman measurement that AFML §8.6 stability metric is defined over.

### §15.2 Caller specification

| Aspect | Specification |
|---|---|
| **Module placement (Aria Option D)** | NEW dedicated submodule `packages/vespera_metrics/info_coef.py` (or equivalent path in `vespera_metrics`) — separate from `cpcv_harness` and from `compute_full_report`. Honors Aria conditions C-A1 (no factory contract pollution), C-A2 (no per-fold P126 D-1 invariant interaction), C-A3 (hold-out lock interaction surface narrow). Decouples IC compute from CPCV walk path so `cpcv_results` (existing) flows unmodified into `_compute_ic_in_sample`. |
| **NEW orchestration helper** | `vespera_metrics.info_coef.compute_ic_in_sample(cpcv_results, *, seed: int, n_resamples: int = 10_000) -> dict[str, Any]` returning `{"ic_c1": float, "ic_c1_ci95": (lo, hi), "ic_c2": float, "ic_c2_ci95": (lo, hi), "n_events_used": int, "ic_status": str}`. |
| **NEW bootstrap helper** | `vespera_metrics.info_coef.ic_bootstrap_ci(predictor: ndarray, label: ndarray, *, n_resamples: int = 10_000, confidence: float = 0.95, seed: int = 42) -> tuple[float, float]` (paired-resample, percentile bootstrap; PCG64; details §15.4). |
| **Caller site** | `scripts/run_cpcv_dry_run.py` `_run_phase` function — invocation IMMEDIATELY after `run_5_trial_fanout` returns `cpcv_results` (currently line ~1050) AND BEFORE `ReportConfig(seed_bootstrap=seed)` construction (currently line ~1070). Insertion zone: lines ~1050-1071 between fanout return and `ReportConfig` build. |
| **Phase guard** | Computed for both `phase='E'` and `phase='F'`. Phase E sanity check: synthetic null walk → near-zero IC; synthetic positive-edge walk → materially positive IC. Phase F binding measurement — `ic_status="computed"` flowed through to `MetricsResult` and verdict layer. |
| **Wiring to `ReportConfig`** | `ic_payload = compute_ic_in_sample(cpcv_results, seed=seed, n_resamples=10_000)` then `cfg = ReportConfig(seed_bootstrap=seed, ic_in_sample=ic_payload["ic_c1"], ic_holdout=0.0, ic_spearman_ci95=ic_payload["ic_c1_ci95"], ic_in_sample_status=ic_payload["ic_status"], ic_holdout_status="deferred")`. The pre-compute default `ReportConfig.ic_in_sample=0.0` is RESERVED for pre-compute state per Anti-Article-IV Guard #8 (§15.5); explicit override required at this caller site. |
| **`ic_status` propagation** | NEW `MetricsResult.ic_status` field (§15.6 below); status enum `{"computed", "deferred", "not_computed", "inconclusive_underN"}`; produced by `compute_ic_in_sample` and propagated to `ReportConfig` → `MetricsResult` → `KillDecision` reason chain. |

### §15.3 NEW `TradeRecord` fields (additive to existing harness)

Per Beckett consumer audit §T0c (additive frozen-dataclass extension; semver minor bump in `t002_eod_unwind` package; backward-compatible with Round 1 N7 cached artifacts in mathematical content but `TradeRecord` shape changes hence N7-prime re-run REQUIRED at F2-T4):

| Field (NEW or existing) | Type | Source | Used for |
|---|---|---|---|
| `TradeRecord.predictor_signal_per_trade` (NEW) | `float` | `make_backtest_fn` closure at entry-decision time — signed value `-intraday_flow_direction` per §15.1 sign convention | C1 + C2 predictor vector |
| `TradeRecord.forward_return_at_1755_pts` (NEW) | `float \| None` | `make_backtest_fn` closure at trade-record time — session-tape lookup at 17:55:00 BRT close minus entry price, in WDO points. **None** if trade exit was vertical at 17:55 itself (degenerate label — zero forward window) | C1 label vector |
| `TradeRecord.pnl_rs` (existing) | `float` | already present (T002.1.bis carry-forward) | C2 label vector |
| `TradeRecord.session_date`, `.trial_id`, `.entry_window_brt` (existing) | `date`, `int`, `str` | already present | dedup key per §15.7 invariant |
| `BacktestResult.fold.test_session_dates` (existing) | `list[date]` | already present | window-membership for in-sample IC filter |

The NEW fields are **additive** to `TradeRecord` (frozen dataclass minor-version compat per Beckett consumer §T0c). Factory signature, per-fold P126 D-1 invariant, and CPCV split semantics UNCHANGED. F2-T4 N7-prime re-run REQUIRED because the dataclass shape change invalidates pickled/parquet TradeRecord caches even though path-PnL mathematical content is identical (Aria Option D decoupling cannot avoid this — the new fields must be populated at `make_backtest_fn` execution time, not post-hoc).

### §15.4 Bootstrap CI specification

| Parameter | Value | Rationale |
|---|---|---|
| `n_resamples` | **10,000** | T002.0d Mira spec §3 default; Bailey-LdP 2014 §3 minimum-N stable estimate |
| `seed_bootstrap` | from `ReportConfig.seed_bootstrap` (= `args.seed`, default 42) | determinism witness; cross-platform stable via PCG64 |
| `distribution` | percentile bootstrap (Efron 1979) | non-parametric; no normality assumption — appropriate for Spearman rank statistic with known non-Gaussian sampling distribution |
| `confidence` | 0.95 | matches §1 K3 row CI95 lower-bound > 0 threshold |
| `paired_index_strategy` | single PCG64 stream of `idx[r] = rng.integers(0, n, size=n)` per resample; predictor and label use the **SAME** `idx[r]` (paired) | preserves event-level pairing — `(predictor[i], label[i])` is the per-event sample; resampling rows preserves this pairing whereas independent resampling of predictor and label vectors would destroy the dependence structure being measured |
| `RNG family` | `numpy.random.Generator(numpy.random.PCG64(seed))` | T002.0d standard; bit-identical replay across platforms |

Implementation of `ic_bootstrap_ci(predictor, label, *, n_resamples=10_000, confidence=0.95, seed=42)`: reuses `ic_spearman()` (existing); PCG64 paired indices; cross-platform stable. Determinism witness: same `(predictor, label, seed)` → same `(lo, hi)` to floating-point determinism.

### §15.5 Anti-Article-IV Guard #8 (NEW — verdict-issuing protocol)

> **Anti-Article-IV Guard #8 (NEW 2026-04-30 BRT):**
> "IC field MUST be computed from CPCV path-PnL data; field default `0.0` is RESERVED for pre-compute state only; emit value of `0.0` only if explicitly Mira-authorized inconclusive case (NEVER as default). `ReportConfig.ic_in_sample` / `.ic_holdout` / `.ic_spearman_ci95` require explicit `_status` provenance flag (`computed` | `deferred` | `not_computed` | `inconclusive_underN`).
>
> Every numeric metric serialized in a verdict-issuing `KillDecision` MUST carry a per-metric `*_status` provenance flag with values from `{computed, deferred, not_computed, inconclusive_underN}`. The verdict layer (`evaluate_kill_criteria`) MUST consume the `*_status` flag and emit `K_NOT_COMPUTED` (or `K_DEFERRED` for hold-out-locked cases) rather than `K_FAIL` when the flag is anything other than `computed`. A verdict report that emits `K_FAIL` while `*_status != 'computed'` is **invalid by construction** and MUST raise `InvalidVerdictReport` before persisting `full_report.json`."

**Carry-forward semantics:**
- Anti-Article-IV Guard #8 ratifies and operationalizes Article IV (No Invention) at the verdict layer — closing the Round 1 attribution finding (IC silently emitted as `0.0` default, leaking through verdict layer as `K3_FAIL` even though no IC measurement was ever performed).
- Cumulative with Guards #1-#7 (preserved verbatim from §11.2 v1.0.0).
- Applies to `K1` (DSR), `K2` (PBO), `K3` (IC) and any future K-criterion added under future spec revision.
- Implementation at `evaluate_kill_criteria` raises `InvalidVerdictReport` when a `K_FAIL` reason would be emitted but the corresponding `*_status` flag is not `"computed"`.
- Council-ratification path: this Guard becomes a binding constraint on Mira spec yaml v0.2.X+1 only AFTER F2-T0a Aria/Beckett/Riven/Pax cosigns close (per §12.1 sign-off chain). Until then it is a binding constraint **of this Gate 4b spec v1.1.0** specifically — applies to F2-T1 Dex implementation regardless of the parent yaml bump status.

### §15.6 Phase F2 enforcement — `MetricsResult` extension + invariant

Additive frozen-dataclass extension; semver minor bump. Implementation in `vespera_metrics`:

```python
# Phase F2 — additive frozen dataclass fields, semver minor bump
@dataclass(frozen=True)
class MetricsResult:
    # ... existing fields verbatim — no mutation ...
    ic_status: str           # "computed" | "deferred" | "not_computed" | "inconclusive_underN"
    ic_holdout_status: str   # same enum; default for Phase F2 = "deferred" (hold-out locked per Anti-Article-IV Guard #3)

# evaluate_kill_criteria invariant (Phase F2 binding — Anti-Article-IV Guard #8):
if ic_status == "computed":
    k3_passed = (ic_in_sample > 0) and (ci95_lower > 0)
elif ic_status == "deferred":
    raise ValueError(
        "ic_in_sample cannot be deferred under Phase F2 — Phase F2 binding measures in-sample IC. "
        "Status 'deferred' is reserved for ic_holdout_status under Anti-Article-IV Guard #3."
    )
elif ic_status in ("not_computed", "inconclusive_underN"):
    raise InvalidVerdictReport(
        f"K3 verdict cannot be emitted: ic_status={ic_status}. "
        "Wire upstream caller per Mira Gate 4b spec §15.2 before issuing verdict. "
        "Anti-Article-IV Guard #8 (§15.5) forbids K_FAIL emission with ic_status != 'computed'."
    )
```

`InvalidVerdictReport` is a NEW exception class introduced in `vespera_metrics` Phase F2; raised before persisting `full_report.json` per §15.5. Phase F2 binding measurement enforces `ic_status == "computed"` at the `evaluate_kill_criteria` boundary — `not_computed` / `inconclusive_underN` paths short-circuit the verdict and surface as `K_NOT_COMPUTED` in the report aggregation, not as `K_FAIL`.

`test_ic_pipeline_wired.py` (NEW per §15.8) — asserts: (a) IC ≠ 0.0 over real CPCV path-PnL with `mean(rank) ≠ 0` (positive-edge regression); (b) `_status == "computed"` flag set; (c) `InvalidVerdictReport` raised on `not_computed` path.

### §15.7 Dedup invariant — one event one count

When assembling `(predictor_vector, label_vector)` from `cpcv_results` for IC computation, group trades by **per-event pairing keys = `(session_date, trial_id, entry_window_brt)`**; take the FIRST occurrence sorted by `path_index` ascending. Each `(session_date, trial_id, entry_window_brt)` tuple is one event; the same event MUST NOT be counted multiple times across the C(N,k) overlapping CPCV test sets.

Deduplication semantics (when same event appears in multiple folds): the per-event predictor and label values are deterministic functions of `(session_date, trial_id, entry_window_brt)` — they do NOT depend on which fold the event was tested in (per-fold P126 D-1 invariant from §2.4 ensures train-fold daily-metric construction is the only fold-conditional input to fanout, and that input does NOT modify the entry decision or the forward-return label, only the daily-metric percentile thresholds for the trial). Therefore the FIRST-occurrence dedup is mathematically equivalent to any other deterministic occurrence selection; we standardize on lowest `path_index` for determinism witness. If different folds produce DIFFERENT predictor/label values for the same event tuple, that is a harness-correctness regression and the smoke test (§15.8 test 1) catches it.

Expected `N_unique_events` for in-sample 2024-08-22..2025-06-30 ≈ 3000-3800 (matches Beckett N7 `n_events=3800`). Bailey-LdP 2014 §3 minimum-N (N >= 30) trivially satisfied at this scale.

### §15.8 Test artifact specification (F2-T2/T3)

NEW unit test file `tests/vespera_metrics/test_ic_pipeline_wired.py` containing **four NEW tests**:

1. **`test_ic_computed_non_zero`** — fixture: real CPCV path-PnL (10-day Phase F real-tape replay slice, smoke-equivalent); assert `IC_in_sample != 0.0` AND `ic_spearman_ci95 != (0.0, 0.0)` AND `ic_status == "computed"`. **Direct regression on the Round 1 Phase F failure mode** — IC silently flowed `0.0` through verdict layer; this test guarantees IC pipeline emits a non-zero numeric measurement on real CPCV path-PnL data with `mean(rank) ≠ 0`.
2. **`test_ic_deterministic`** — fixture: same input `cpcv_results` + same `seed=42` invoked twice; assert `compute_ic_in_sample(cpcv_results, seed=42, n_resamples=10_000)` returns bit-identical `(ic_c1, ic_c1_ci95, ic_c2, ic_c2_ci95)` across both calls. PCG64 paired indices determinism witness.
3. **`test_ic_status_flag`** — fixture: real CPCV path-PnL (small valid fixture); assert `compute_ic_in_sample` returns `ic_status == "computed"`; assert `ic_status` propagates through `ReportConfig` → `MetricsResult.ic_status` → `KillDecision` reason chain unmodified; assert `evaluate_kill_criteria` reads `ic_status == "computed"` and proceeds to numeric K3 evaluation rather than short-circuiting.
4. **`test_ic_inconclusive_path`** — fixture: explicit Mira-authorized inconclusive case — `cpcv_results = {}` (empty, simulating no events captured) OR `n_unique_events < 30` (under-N case); assert `compute_ic_in_sample` returns `ic_status ∈ {"not_computed", "inconclusive_underN"}` AND `ic_c1 == 0.0` (Mira-authorized 0.0, NOT silent default); assert `evaluate_kill_criteria` raises `InvalidVerdictReport` rather than emitting `K3_FAIL` (per §15.5 Anti-Article-IV Guard #8 + §15.6 invariant).

Each test deterministic via PCG64 seed. ADR-1 v3 6 GiB RSS budget honored (small synthetic fixtures for tests 2-4; 10-day smoke fixture for test 1). Integrated into `pytest tests/` full-suite regression (no separate slow-mark).

### §15.9 Phase F2 wall-time budget interaction

Beckett N7 full report §7 surfaced wall-time concern C1' (181 min vs 60 min hard cap). Phase F2 IC computation at 3800 events × 10,000 bootstrap resamples × 2 IC variants (C1 + C2) ≈ 2 × 10,000 paired-rank-correlation evaluations on N=3800 vectors. With `scipy.stats.spearmanr` at ~5ms per evaluation, that is **~100 seconds added to the report-aggregation phase** — negligible relative to the 181 min real-tape walk. Phase F2 wall-time interaction is **non-blocking** for C1' wall-time concern. Engine-config v1.2.0 perf round (Beckett T0c) remains a separate concern, unaffected by §15 amendment. F2-T4 N7-prime re-run is post-hoc compute with respect to the 181 min walk — incremental cost is the ~100s IC compute on top.

### §15.10 Gate 5 fence preservation (R5/R6)

This §15 amendment does NOT touch §1 thresholds (Anti-Article-IV Guard #4: DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE), §3 real-tape data interface, §4 Nova RLP / rollover / auction / CB / cross-trade contracts, §5 Beckett latency model, §6 sample-size mandate (≥ 150-250 events floor), §7 3-bucket attribution, §8 milestones (a-f), §9 verdict-label discipline (`GATE_4_PASS` not `HARNESS_PASS`), §10 Gate 5 conjunction footer (R5/R6 + Riven §9 HOLD #2 fence), §11 Article IV trace, §12 sign-off chain (extends in §12.1, does not mutate Round 1), §13 self-audit, or §14 cosign ledger.

**IC compute does NOT pre-disarm Gate 5 alone.** Gate 5 capital ramp dual-sign requires Gate 4a (HARNESS_PASS, DONE) AND Gate 4b (GATE_4_PASS pending F2-T5 re-clearance) BOTH PASS plus Phase G/H paper-mode audit (T002.7 future). Riven §9 HOLD #2 Gate 5 disarm authority preserved. F2-T5 Mira re-clearance is the gating step; F2-T6 Riven reclassify operates after F2-T5 verdict — neither pre-empts Gate 5 conjunction nor relaxes the §10.2 mandatory footer text. Gate 5 fence is **reinforced**, not relaxed: Anti-Article-IV Guard #8 (§15.5) makes it harder to forge a `GATE_4_PASS` because numeric metric emission now requires `*_status == "computed"` provenance.

### §15.11 Sign-off chain F2-T0a..F2-T6

Reproduced from §12.1 above for §15-local readability:

| Stage | Owner | Action |
|---|---|---|
| **F2-T0a** | Mira | Apply §15 amendment (this artifact) — operationalize deep audit §6 + Aria archi review + Beckett consumer + Sable F-01..F-04 |
| **F2-T0b** | Aria | Validate §15 against C-A1..C-A7 conditions in archi review (separate orchestration module in `vespera_metrics`; factory contract preservation; hold-out lock interaction) |
| **F2-T0c** | Beckett | Consumer sign-off — additive `TradeRecord.predictor_signal_per_trade` + `.forward_return_at_1755_pts` fields wired in `make_backtest_fn`; smoke-fixture viability; wall-time budget §15.9 |
| **F2-T0d** | Riven | Gate 5 fence preservation §15.10 + post-mortem ledger entry path |
| **F2-T0e** | Pax | 10-point validate §15 amendment scope; verifies v1.0.0 → v1.1.0; sign-off chain extended; no §1-§14 mutation |
| **F2-T1** | Dex | Implementation — `_compute_ic_in_sample`, `ic_bootstrap_ci`, `TradeRecord` extension, `_run_phase` wiring, `MetricsResult.ic_status` + `.ic_holdout_status`, `evaluate_kill_criteria` invariant per §15.6, `InvalidVerdictReport` exception per §15.5 |
| **F2-T2/T3** | Quinn | 4 NEW tests in `test_ic_pipeline_wired.py` per §15.8 + ruff + lint + regression |
| **F2-T4** | Beckett | N7-prime real-tape replay run — DECOUPLED per Aria Option D (separate orchestration module); re-run necessário porque `TradeRecord` shape muda per §15.3 (additive frozen-dataclass extension); new `run_id`; sha256 stamps regenerated; ADR-1 v3 RSS ≤ 6 GiB |
| **F2-T5** | Mira | Gate 4b re-clearance — verdict possibilities `GATE_4_PASS`, `GATE_4_FAIL_strategy_edge`, `GATE_4_FAIL_data_quality`, `GATE_4_FAIL_both`, or `INCONCLUSIVE` per §7 decision tree; §10.2 footer mandatory; Anti-Article-IV Guard #8 enforced |
| **F2-T6** | Riven | 3-bucket attribution reclassify — bucket A `IC_pipeline_wiring_gap` CLOSED; new entry per F2-T4 verdict (bucket B/C/both per §7) |

### §15.12 Article IV self-audit (§15 amendment)

| §15 claim | Source anchor (verified) |
|---|---|
| IC measurement semantics (per-event C1 binding paradigm; predictor `-intraday_flow_direction`; label `ret_forward_to_17:55_pts`) | `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` §1.4 verbatim; thesis doc Q4 + H1; this spec §1 K3 row; AFML §8.6; Bailey-LdP 2014 §3 |
| Caller specification (script `run_cpcv_dry_run.py:~1050-1071` insertion zone; orchestration module per Aria Option D) | `scripts/run_cpcv_dry_run.py` lines 1050-1071 (verified exists); Aria archi review APPROVE_OPTION_D; Beckett consumer §T0c |
| NEW `TradeRecord` fields (`predictor_signal_per_trade`, `forward_return_at_1755_pts: float \| None`) | Beckett consumer audit §T0c (additive frozen-dataclass extension; semver minor bump) |
| Bootstrap CI specification (paired-resample n=10000; PCG64 seed=42; percentile bootstrap) | T002.0d Mira spec §3 (bootstrap defaults); Efron 1979 (percentile bootstrap); deep audit §3.3 (paired index strategy) |
| Anti-Article-IV Guard #8 (NEW) | This spec §15.5; deep audit §6 (recommended Guard #8 text); Article IV (No Invention) — operationalization at verdict layer |
| Phase F2 enforcement (`InvalidVerdictReport` raise on `ic_status != "computed"` with K_FAIL) | Deep audit §6 enforcement block; Anti-Article-IV Guard #8 (§15.5) |
| Dedup invariant (per-event keys `(session_date, trial_id, entry_window_brt)`) | Deep audit §6 dedup invariant; Beckett N7 `n_events=3800` |
| 4 NEW tests in `test_ic_pipeline_wired.py` | Deep audit §15.8 test list + Sable F-04 procedural recommendation (test artifact specification) |
| Wall-time budget ~100s incremental, non-blocking C1' | Deep audit §15.9; Beckett N7 §7 wall-time concern C1' |
| Gate 5 fence preservation (R5/R6) | This spec §10 + §10.2 footer + ESC-011 R5/R6; deep audit §15.10 |
| Sign-off chain F2-T0a..F2-T6 (decoupled per Aria Option D — N7-prime re-run necessário) | Deep audit §15.11; Aria archi review (separate orchestration module decouples wiring but TradeRecord shape change forces re-run); Beckett consumer §T0c |
| Aria conditions C-A1..C-A7 reference | `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` |
| Beckett consumer §T0c reference | `docs/backtest/T002.6-beckett-consumer-signoff.md` §T0c (appended) |
| Sable F-01..F-04 procedural recommendations | `docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md` 8 findings |
| No §1 threshold mutation (Anti-Article-IV Guard #4 UNMOVABLE) | This spec §1 reaffirmation; §15.10 explicit non-touch list |
| No hold-out lock mutation (Anti-Article-IV Guard #3 UNMOVABLE) | This spec §3.1 + §15.1 (`IC_holdout` deferred to Phase G); §15.10 |
| No Round 1 T5 sign-off mutation | §12 Round 1 chain preserved; §12.1 is append-only continuation |

**Article IV self-audit verdict (§15 amendment):** every clause traces. NO INVENTION. The §15 amendment is the **operationalization** of the deep audit Round 1 attribution finding (IC pipeline wiring gap is bucket A `harness_gap`, not bucket B `strategy_edge`); thresholds UNMOVABLE; hold-out UNTOUCHED; Round 1 T5 sign-off UNMOVED; §0-§14 v1.0.0 body content UNCHANGED; append-only revision per Pax governance.

**Anchor count (§15-local):** 14 source anchors verified — Mira deep audit §6 + §1.4 + §3.3 + §15.8 + §15.9 + §15.10 + §15.11; Aria archi review C-A1..C-A7 (APPROVE_OPTION_D); Beckett consumer audit §T0c; Sable audit F-01..F-04; thesis doc Q4 + H1; this spec §1 K3 row + §3.1 hold-out + §10.2 footer + §11.2 Anti-Article-IV Guards; AFML §8.6 (IC stability); Bailey-LdP 2014 §3 (minimum-N); Efron 1979 (percentile bootstrap); ESC-011 R5/R6 + R10; T002.0d Mira spec §3 (bootstrap defaults); ADR-1 v3 (6 GiB RSS); `scripts/run_cpcv_dry_run.py:~1050-1071` (verified caller site).

---

### §15.13 Phase G OOS Unlock Protocol (Phase G amendment 2026-04-30 BRT v1.2.0)

> **Provenance:** This §15.13 is the operationalization of ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification (`docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §4.1 R2 — "Pre-authored Phase G unlock per spec §3.1 + §15.10"). Authority chain: Aria archi review F2-T0b' APPROVE_OPTION_D + 7 conditions C-A8..C-A14 carry-forward to Phase G (`docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md`); Mira F2-T5 Round 2 sign-off OBS-1 surface (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §6); ESC-012 17 ratified conditions R1-R17.

> **Scope discipline:** §15.13 ADDS sub-section to §15. It does NOT mutate §1 thresholds (Anti-Article-IV Guard #4 honored: DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE), §3 real-tape data interface, §4 Nova RLP, §5 Beckett latency, §6 sample-size mandate, §7 3-bucket attribution, §8 milestones (a-f), §9 verdict-label discipline, §10 Gate 5 conjunction, §11 Article IV trace, §12 sign-off chain (extends in §12.2, does not mutate), §13 self-audit, §14 cosign ledger (extends in §14.4, does not mutate), §15.1-§15.12 v1.1.0 content. Phase G unlock IS the authorized §15.10 transition (pre-authored at spec §3.1 + §15.10), NOT a hold-out lock violation per ESC-012 R10 K1 strict bar UNMOVABLE preservation. Round 1 T5 + Round 2 F2-T5 sign-offs UNMOVED. Append-only revision per Pax governance.

#### §15.13.1 Phase G unlock authorization

Per ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification:

| Voter | Vote | Ballot artifact |
|---|---|---|
| Aria (@architect) | APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md` |
| Kira (@quant-researcher) | APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-kira-vote.md` |
| Mira (@ml-researcher) | APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-mira-vote.md` |
| Beckett (@backtester) | APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-beckett-vote.md` |
| Pax (@po) | APPROVE_PATH_B | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-pax-vote.md` |
| Riven (@risk-manager) | DISSENT — Path C minority | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-riven-vote.md` |

Tally: 5/6 APPROVE_PATH_B (supermajority threshold met; ≥ 5/6 cleared). Riven minority dissent preserved: Path C explicit fallback IF Phase G run cannot proceed within 14 calendar days (i.e. by 2026-05-14 BRT) — preserves the disciplined retire-clean option.

Pre-authored unlock per spec §3.1 (real-tape data interface — hold-out window structurally defined) + §15.10 (Gate 5 fence preservation — fence is reinforced, not relaxed) + Mira parent spec yaml v0.2.3 §3 hold-out window. Phase G unlocks for SINGLE OOS confirmation run.

#### §15.13.2 Unlock mechanism

```python
ic_result = compute_ic_from_cpcv_results(
    results,
    seed_bootstrap=42,
    n_resample=10000,
    holdout_locked=False,  # Phase G unlock: holdout=AVAILABLE
)
# Propagation: ic_holdout_status='computed' (was 'deferred' Phase F2)
# Decay test full evaluation: IC_holdout > 0.5 × IC_in_sample becomes BINDING K3 sub-clause
```

Caller site: same `scripts/run_cpcv_dry_run.py:~1050-1071` insertion zone wired in F2-T1 (Aria Option D — `vespera_metrics` orchestration module). Dex F2-T8-T1 implementation: small ~10-20 LoC change to (a) flip `holdout_locked=False` for Phase G; (b) introduce `--phase G` CLI flag gating the unlock; (c) propagate `ic_holdout_status='computed'` through `MetricsResult` extension §15.6 invariant. Anti-Article-IV Guard #8 (§15.5) verdict-issuing protocol applies verbatim — `K_FAIL` cannot be emitted with `ic_holdout_status != 'computed'` in Phase G context.

#### §15.13.3 Phase G run window

| Field | Value |
|---|---|
| **in-sample-start** | 2025-07-01 |
| **in-sample-end** | 2026-04-21 |
| **Window length** | ~10 months ~210 trading days |
| **Expected event count** | ~3000-4000 events × 5 trials × 45 paths (CPCV combinatorial) |

**Reusability invariants per ESC-012 R6 (binding — engine_config + spec yaml + cost atlas + rollover + Bonferroni + latency + RLP + microstructure flags ALL IDENTICAL to F2 N7-prime):**

| Invariant | F2 N7-prime stamp | Phase G N8 (MUST be IDENTICAL) |
|---|---|---|
| `engine_config_sha256` | `ccfb575a…` | `ccfb575a…` (no change) |
| Spec yaml `T002-end-of-day-inventory-unwind-wdo-v0.2.3.yaml` thresholds | DSR>0.95 / PBO<0.5 / IC | UNMOVABLE (Anti-Article-IV Guard #4) |
| Cost atlas v1.0.0 SHA-locked | `bbe1ddf7…` | `bbe1ddf7…` (no change) |
| Rollover calendar SHA-locked | `c6174922…` | `c6174922…` (no change) |
| Bonferroni `n_trials` | 5 (T1..T5 verbatim) | 5 (T1..T5 verbatim — IDENTICAL) |
| `latency_dma2_profile` | per Beckett spec §5 | IDENTICAL (no parameter tweak) |
| RLP detection (Nova §4) | per Nova spec | IDENTICAL |
| Microstructure flags (Nova §4) | per Nova spec | IDENTICAL |

#### §15.13.4 Predictor↔label semantics IDENTICAL F2 (ESC-012 R7)

Per §15.1 Phase F2 binding paradigm — Phase G consumes the SAME predictor↔label pair without modification:

- **predictor** = `-intraday_flow_direction` (sign de fade — verbatim §15.1 binding)
- **label** = `ret_forward_to_17:55_pts` em pontos WDO (verbatim §15.1 binding)

NO refinement / no parameter tweak / no Bonferroni expansion / no horizon shift / no triple-barrier reformulation. ESC-012 R7 enforces predictor↔label IDENTICALITY because Phase G is **single-shot OOS confirmation**, not a research iteration.

#### §15.13.5 Decay test full evaluation

Phase G unlock activates the canonical K3 decay sub-clause (§1 carry-forward — Mira spec yaml v0.2.3 L209 + parent §6 K3 row):

```
K3_decay_passed = (IC_holdout > 0.5 × IC_in_sample)
```

**Phase F2 short-circuit (per OBS-1 fix in F2-T5 Round 2 sign-off + ESC-012 R1) NO LONGER applies** in Phase G context because `ic_holdout_status='computed'` (vs `'deferred'` in F2). The full BINDING K3 evaluation activates: IC_holdout magnitude must preserve in-sample IC sign AND retain ≥ 50% of in-sample magnitude. Decay below this threshold = K3 FAIL = Gate 4b FAIL.

This IS the canonical Lopez de Prado AFML §8.6 IC-stability rolling decay paradigm activated in OOS measurement form per Bailey-LdP 2014 §6 reproducible-backtest gating.

#### §15.13.6 K1 strict bar UNMOVABLE preservation (ESC-012 R10)

Phase G PASS does NOT pre-disarm Gate 4b alone under K1 strict bar (DSR>0.95 spec §1; Mira spec yaml v0.2.3 L207). Gate 5 capital ramp dual-sign STILL requires:

- **K1 PASS** (DSR > 0.95) — UNMOVABLE per Anti-Article-IV Guard #4
- **K2 PASS** (PBO < 0.5) — UNMOVABLE per Anti-Article-IV Guard #4
- **K3 PASS** (IC > 0 with CI95 lower > 0; decay stable per §15.13.5) — UNMOVABLE per Anti-Article-IV Guard #4
- **+ paper-mode Phase G/H audit (T002.7 future scope)** — bucket C of Riven 3-bucket framework

K1 strict bar UNMOVABLE per Anti-Article-IV Guard #4. ESC-012 R10 explicitly preserves the K1 fence: a Phase G PASS on K2+K3 with K1 borderline does NOT relax K1; verdict pathway routes through §7 decision tree (3-bucket attribution).

#### §15.13.7 OOS one-shot discipline (ESC-012 R9)

Phase G window 2025-07-01..2026-04-21 is **single-shot**. The result is binding regardless of outcome:

- CANNOT be re-run with adjusted parameters (would constitute IS-fit on hold-out — Anti-Article-IV Guard #3 + #4 violation)
- CANNOT be expanded with additional trials beyond Bonferroni n=5 carry-forward (would violate ESC-012 R6 reusability invariant)
- CANNOT be reformulated mid-flight (would violate ESC-012 R7 predictor↔label IDENTICALITY)
- CANNOT be averaged with subsequent re-runs (Anti-Article-IV Guard #5 sub-sample averaging prohibition extended to OOS)

The hold-out window collapses to a **single committed measurement**. This is the Bailey-LdP 2014 §6 + §3 selection-bias guarantee — once we look at the hold-out, the hold-out is consumed.

#### §15.13.8 Pre-committed disposition rule (ESC-012 R3 — PRR-20260430-1)

Hash-frozen BEFORE Phase G N8 run via `python scripts/pax_cosign.py register` (per MANIFEST R15 spec versioning protocol). 4 explicit branches per ESC-012 decision tree:

| Outcome | Definition | Action (per ESC-012 decision tree) |
|---|---|---|
| **PASS K1+K2+K3** | DSR>0.95 AND PBO<0.5 AND IC>0 with CI95 lower>0 AND IC_holdout > 0.5 × IC_IS | **ESC-013 escalate** (K1 strict bar surprise PASS — would still require paper-mode Phase G/H per R10 fence; council convene to ratify pathway to T002.7 Phase G/H paper-mode audit; K1 strict bar UNMOVABLE preserved upstream of capital ramp) |
| **FAIL_K3_collapse** | IC_holdout drops significantly (e.g., <0.3 or sign-flip from in-sample) | **T002 falsified clean per spec §0**; retire ceremony (`docs/risk/post-mortems/T002-retire-ceremony-{date}.md`); epic deprecate; bucket B `strategy_edge_falsified_OOS` per §7; institutional knowledge captured for H_next |
| **FAIL_K1+K3_sustains** | IC stable holdout but DSR<0.95 (cost gates dominate edge magnitude) | **costed_out_edge OOS-confirmed**; T002 retire with refined diagnostic; bucket B `costed_out_edge_OOS_confirmed` per §7; institutional knowledge for H_next (cost-atlas calibration / latency-budget refinement / sizing economics) |
| **INCONCLUSIVE** | E.g., IC borderline + K2 borderline + N events under floor (§6 ≥ 150-250 mandate violated in OOS context) | **ESC escalation**; defer to council; route per §7 INCONCLUSIVE branch (R9 1-of-4 verdict possibilities); cannot pre-empt fate without council ratification |

The PRR-20260430-1 hash freeze BEFORE the run is the Article IV (No Invention) defense: every disposition pathway is enumerated, anchored, and binding ex-ante. NO post-hoc rationalization of an unanticipated outcome (Anti-Article-IV Guard #3 + #4 + #8 collectively).

#### §15.13.9 Sample-size considerations

| Phase | Window | Trials × Paths | Expected events |
|---|---|---|---|
| **F2 N7-prime** (in-sample) | spec yaml §3 in-sample | 5 × 45 | ~3800 events (Beckett N7-prime report) |
| **Phase G N8** (out-of-sample) | 2025-07-01..2026-04-21 (~10 months) | 5 × 45 | ~3000-4000 events (estimated — comparable order of magnitude) |

Phase G ~3000-4000 events vs Phase F2 ~3800 events — **comparable order of magnitude**. Floor mandate per §6 + Bailey-LdP 2014 §3 (≥ 150-250 events) is comfortably cleared in expectation. Bonferroni `n_trials=5` carry-forward (T1..T5 verbatim — IDENTICAL to F2; ESC-012 R6); bootstrap `n_resample=10000` PCG64 `seed=42` IDENTICAL (per §15.4 + §15.13.2 mechanism). Sample-size INCONCLUSIVE branch (§15.13.8) only triggers if actual N falls below floor — to be verified post-run, NOT pre-emptively assumed.

#### §15.13.10 Wall-time + RSS budget

Beckett N8 OOS run constraints:

- **Wall-time:** ~3h (same envelope as F2 N7-prime per Beckett consumer §T0c — single OOS run squad-tolerable at this duration)
- **RSS peak:** ~600 MB (well under ADR-1 v3 6 GiB cap)
- **Engine_config v1.2.0 perf optimization:** OPTIONAL (single OOS run within budget without optimization — perf work deferable to post-Phase-G if T002.7 Phase G/H paper-mode pathway activates)
- **Sha256 stamping:** new `run_id` generated; cost atlas + rollover calendar SHAs IDENTICAL to F2 N7-prime per ESC-012 R6 reusability invariant

#### §15.13.11 Article IV trace policy

Every Phase G verdict claim traces to:

- **(a)** ESC-012 ratification R1-R17 — `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md`
- **(b)** Mira spec § anchor (§1 thresholds + §3.1 hold-out + §6 sample-size + §7 attribution + §10.2 footer + §15.1-§15.12 IC pipeline + §15.13 this section)
- **(c)** PRR-20260430-1 disposition rule (hash-frozen BEFORE N8 run via `scripts/pax_cosign.py register`)
- **(d)** N8 run artifact (Beckett OOS run report, sha256-stamped, ADR-1 v3 RSS verified)
- **(e)** Bailey-LdP 2014 §3+§6 / Bailey-Borwein-LdP 2014 / AFML 2018 §8.6 citation

**NO INVENTION.** Phase G verdict label discipline carries forward §9 (`GATE_4_PASS` / `GATE_4_FAIL_*` / `INCONCLUSIVE` per §15.13.8 4 branches × §7 3-bucket disambiguation; never `HARNESS_PASS`).

#### §15.13.12 Sign-off chain F2-T8

Reproduced from §12.2 below for §15.13-local readability:

| Stage | Owner | Action |
|---|---|---|
| **F2-T8-T0a** | Mira (@ml-researcher) | Apply §15.13 spec amendment (this artifact) — operationalize ESC-012 R2 Phase G OOS unlock pre-authored protocol |
| **F2-T8-T0b** | Aria (@architect) | Small archi review — gated em T0a; verify C-A8/C-A9 carry-forward conditions held (factory contract preservation across Phase F2 → Phase G transition; Aria Option D module placement intact in `vespera_metrics`) |
| **F2-T8-T0c** | Beckett (@backtester) | Consumer sign-off — Phase G run plan + budget; smoke-fixture viability OOS context; wall-time §15.13.10; cost-atlas + rollover SHAs IDENTICAL F2 per ESC-012 R6 |
| **F2-T8-T0d** | Riven (@risk-manager) | Cost-atlas + Gate 5 fence preserve (carry-forward §10.2 footer verbatim; §15.13.6 K1 strict bar UNMOVABLE preserved; bucket A `IC_pipeline_wiring_gap` CLOSED upon F2-T5 Round 2 already; new entry per F2-T8-T4 verdict) |
| **F2-T8-T0e** | Pax (@po) | 10-point `*validate-story-draft` over §15.13 amendment scope; verifies v1.1.0 → v1.2.0; sign-off chain extended F2-T8-T0a..F2-T8-T7; Anti-Article-IV Guards #3 + #4 + #8 preserved verbatim; register PRR-20260430-1 via `python scripts/pax_cosign.py register` (hash-freeze disposition rule BEFORE N8 run) |
| **F2-T8-T1** | Dex (@dev) | Caller wiring `holdout_locked=False` + `--phase G` CLI flag (small ~10-20 LoC) — `scripts/run_cpcv_dry_run.py:~1050-1071` insertion zone; `MetricsResult.ic_holdout_status` propagation `'deferred' → 'computed'`; Anti-Article-IV Guard #8 verdict-issuing protocol preserved |
| **F2-T8-T2/T3** | Quinn (@qa) | QA Gate (8-point + Check 8 retained) — Phase G unlock invariant tests (`holdout_locked=False` propagation); regression vs F2 N7-prime baseline (TradeRecord shape unchanged — F2-T2/T3 4 NEW tests in `tests/vespera_metrics/test_ic_pipeline_wired.py` continue to PASS); Article IV trace test for §15.13 anchors |
| **F2-T8-T4** | Beckett (@backtester) | N8 OOS run (~3h wall, ~600 MB RSS peak per §15.13.10) — Phase G window 2025-07-01..2026-04-21; sha256-stamped new `run_id`; cost atlas + rollover SHAs IDENTICAL F2 per ESC-012 R6; ADR-1 v3 RSS ≤ 6 GiB |
| **F2-T8-T5** | Mira (@ml-researcher) | F2-T9 re-clearance Round 3 (supersedes F2-T5 Round 2 sign-off via append-only ledger entry — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md`) — verdict per §15.13.8 disposition rule (PASS / FAIL_K3_collapse / FAIL_K1+K3_sustains / INCONCLUSIVE); §10.2 footer mandatory; Anti-Article-IV Guard #8 verdict-issuing protocol enforced (`ic_holdout_status='computed'` invariant) |
| **F2-T8-T6** | Riven (@risk-manager) | 3-bucket attribution reclassify Round 3 (`docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` append-only ledger entry) — bucket A `IC_pipeline_wiring_gap` CLOSED (carry-forward Round 2); new entry per F2-T8-T4 verdict (bucket B/C/both per §15.13.8 + §7 disambiguation) |
| **F2-T8-T7** | Pax (@po) | T002.7 close per outcome — story status transition per §15.13.8 disposition rule; epic deprecate or T002.7 Phase G/H paper-mode pathway activate per ESC-012 R10 fence + ESC-013 escalate if surprise PASS |

#### §15.13.13 Article IV self-audit (§15.13 amendment)

| §15.13 claim | Source anchor (verified) |
|---|---|
| ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B (Aria + Kira + Mira + Beckett + Pax APPROVE; Riven Path C dissent) | `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` §1 outcome table — 6 voters, 5 APPROVE_PATH_B ballots, 1 Path C dissent; individual ballot artifacts referenced in §15.13.1 table |
| Phase G unlock pre-authored at spec §3.1 + §15.10 | This spec §3.1 (real-tape data interface — hold-out window structurally defined) + §15.10 (Gate 5 fence preservation — fence reinforced not relaxed); ESC-012 R2 verbatim |
| Phase G window 2025-07-01..2026-04-21 (~10 months ~210 trading days) | Mira parent spec yaml v0.2.3 §3 hold-out window; ESC-012 R6 reusability invariant table this spec §15.13.3 |
| Reusability invariants (engine_config + spec yaml + cost atlas + rollover + Bonferroni + latency + RLP + microstructure ALL IDENTICAL F2) | ESC-012 R6 verbatim; Beckett N7-prime sha256 stamps (`engine_config_sha256=ccfb575a…`, cost atlas `bbe1ddf7…`, rollover `c6174922…`); spec yaml §kill_criteria L207-209 UNMOVABLE; spec §1.2 Bonferroni n=5; Beckett spec §5 latency; Nova spec §6 RLP / microstructure |
| Predictor↔label IDENTICAL F2 (predictor=`-intraday_flow_direction`, label=`ret_forward_to_17:55_pts`) | §15.1 binding paradigm verbatim; ESC-012 R7 enforce IDENTICALITY for single-shot OOS; deep audit §1.4 |
| Decay test full evaluation `IC_holdout > 0.5 × IC_in_sample` BINDING in Phase G context | §1 K3 row + spec yaml §kill_criteria.k3_ic L209 + AFML §8.6 IC stability + Bailey-LdP 2014 §6 reproducible-backtest gating; F2 OBS-1 fix per F2-T5 Round 2 sign-off + ESC-012 R1 |
| K1 strict bar UNMOVABLE in Phase G PASS context (does NOT pre-disarm Gate 4b alone; Gate 5 STILL requires K1+K2+K3 + paper-mode Phase G/H) | Anti-Article-IV Guard #4 verbatim; ESC-012 R10 K1 strict bar fence preservation; this spec §10 Gate 5 conjunction; Riven §9 HOLD #2 Gate 5 ledger |
| OOS one-shot discipline (cannot re-run / expand trials / reformulate / average) | ESC-012 R9 verbatim; Bailey-LdP 2014 §3 + §6 selection-bias guarantee; Anti-Article-IV Guards #3 + #4 + #5 collective application to OOS |
| 4-branch pre-committed disposition rule (PRR-20260430-1 hash-frozen BEFORE N8 run) | ESC-012 R3 verbatim; MANIFEST R15 spec versioning protocol; `scripts/pax_cosign.py register` interface; Anti-Article-IV Guards #3 + #4 + #8 collective |
| Phase G ~3000-4000 events comparable F2 ~3800 events | Beckett N7-prime report event count; Mira spec yaml §3 hold-out window length × intraday event rate estimate |
| Wall-time ~3h + RSS ~600 MB (well under ADR-1 v3 6 GiB cap) | Beckett consumer §T0c F2-T0c sign-off precedent; ADR-1 v3 RSS cap; this spec §15.9 wall-time budget pattern |
| Article IV trace 5-source policy (a-e) | ESC-012 resolution + this spec §-anchors + PRR-20260430-1 + N8 artifact + Bailey-LdP / BBLP / AFML citations |
| Sign-off chain F2-T8-T0a..F2-T8-T7 (Round 3 — supersedes F2-T5 Round 2 via append-only ledger) | This §15.13.12 + §12.2 (pending edit below) + §14.4 (pending edit below); Aria archi review F2-T0b' APPROVE_OPTION_D conditions C-A8/C-A9 carry-forward; Mira F2-T5 Round 2 sign-off `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §6 OBS-1 |
| No §1 threshold mutation (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0) | This spec §1 reaffirmation; §15.13.6 K1 strict bar UNMOVABLE; ESC-012 R10 |
| No hold-out lock policy mutation (Phase G unlock IS authorized §15.10 transition, NOT Anti-Article-IV Guard #3 violation) | This spec §3.1 hold-out window definition + §15.10 fence preservation; ESC-012 R2 pre-authored unlock; Anti-Article-IV Guard #3 verbatim (hold-out is for OOS measurement, not training) |
| No §0-§14 v1.0.0 body mutation | §0-§14 content preserved verbatim in this artifact; v1.0.0 / v1.1.0 / v1.2.0 are append-only revisions |
| No §15.1-§15.12 v1.1.0 content mutation | §15.1-§15.12 content preserved verbatim; this §15.13 is append-only sub-section |
| No Round 1 T5 sign-off mutation; No Round 2 F2-T5 sign-off mutation | §12 + §14.2 Round 1 chain preserved; §12.1 + §14.3 Round 2 chain preserved; F2-T8-T5 Round 3 supersedes via append-only ledger entry NOT mutation |

**Article IV self-audit verdict (§15.13 amendment):** every clause traces. **NO INVENTION.** §15.13 is the **operationalization** of ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification + 17 conditions R1-R17 + Aria F2-T0b' archi review APPROVE_OPTION_D + 7 conditions C-A8..C-A14 carry-forward + Mira F2-T5 Round 2 OBS-1 surface + Riven minority Path C explicit fallback preserve. K1 strict bar UNMOVABLE; hold-out unlock IS authorized §15.10 transition NOT violation; Round 1 + Round 2 sign-offs UNMOVED; §0-§14 v1.0.0 + §15.1-§15.12 v1.1.0 body content UNCHANGED; append-only revision per Pax governance.

**Anchor count (§15.13-local):** 17 source anchors verified — ESC-012 resolution + 6 ballot artifacts (§15.13.1 table); Mira parent spec yaml v0.2.3 §3 hold-out + §kill_criteria L207-209 UNMOVABLE; this spec §1 K3 + §3.1 hold-out + §10.2 footer + §11.2 Anti-Article-IV Guards + §15.1 IC binding paradigm + §15.5 Guard #8 + §15.10 fence preservation; ESC-012 R1-R17 (R1 OBS-1 fix, R2 pre-authored unlock, R3 PRR disposition, R6 reusability invariants, R7 predictor↔label IDENTICALITY, R9 OOS one-shot, R10 K1 strict bar UNMOVABLE); Aria F2-T0b' archi review APPROVE_OPTION_D + 7 conditions C-A8..C-A14; Mira F2-T5 Round 2 sign-off OBS-1; Riven minority Path C dissent ballot; AFML 2018 §8.6 (IC stability); Bailey-LdP 2014 §3+§6 (minimum-N + reproducible-backtest gating); Bailey-Borwein-LdP 2014 PBO; ADR-1 v3 (6 GiB RSS); MANIFEST R15 spec versioning; `scripts/pax_cosign.py register` (PRR hash-freeze interface); Beckett N7-prime sha256 stamps (`ccfb575a…` / `bbe1ddf7…` / `c6174922…`); Beckett spec §5 latency; Nova spec §4 RLP/microstructure.

---

### §15.14 Auction State Block Correction (post-T002 retire) (v0.3.0 amendment 2026-05-01 BRT)

> **Provenance:** This §15.14 is the operationalization of Nova authoritative confirmation `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` (Final v1.0.0; 270 lines; 8 source anchors B3 official + secondary cross-validation). Nova is the single autoritative voice on B3 session phases / WDO auction hours. The confirmation was user-mandated as a pre-condition for Quant Council to approve any "Auction Print Analysis" SECONDARY direction; it surfaced a CRITICAL discrepancy in this spec's §4 auction state block (inherited from `docs/backtest/T002.6-nova-rlp-rollover-spec.md` §3.2 which had a documented error — a "closing call 17:55-18:00" phase that does NOT exist regulamentadamente for WDO and was an artifact of equities-regime confusion). This v0.3.0 amendment corrects the documented SEMANTICS while preserving the operational triple-barrier 17:55 vertical exit timestamp (which is unaffected because that timestamp was selected as a strategy-thesis "5min buffer before continuous close" — it just was previously DOCUMENTED as a "boundary with auction" which was wrong prose).

> **Scope discipline:** §15.14 ADDS a sub-section to §15. It does NOT mutate §1 thresholds (Anti-Article-IV Guard #4 honored: DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE), §3 real-tape data interface, §4 v1.0.0 auction state block (preserved verbatim per append-only governance — §15.14.4 below provides the corrected canonical block readers consult; §4 prose remains as historical record of the v1.0.0 inheritance from T002.6 §3.2), §5 Beckett latency, §6 sample-size mandate, §7 3-bucket attribution, §8 milestones, §9 verdict-label discipline, §10 Gate 5 conjunction, §11 Article IV trace, §12 sign-off chain (extends in §12.3, does not mutate §12.0/§12.1/§12.2), §13 self-audit, §14 cosign ledger, §15.1-§15.13 content. Round 1 T5 + Round 2 F2-T5 + Round 3 F2-T8-T5 + Round 3.1 T002 RETIRE FINAL verdicts UNMOVED. Append-only revision per Pax governance.

#### §15.14.1 Source provenance

The correction consumed in this §15.14 is sourced from Nova authoritative finding `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md`. Source cross-checking per Article IV (No Invention):

| Anchor | Source | Status |
|---|---|---|
| **Primary regulatory** | B3 oficial PUMA — Câmbio e Dólar Pronto: `https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/horario-de-negociacao/derivativos/cambio-e-dolar-pronto/` (accessed_at_brt 2026-05-01) | [WEB-CONFIRMED 2026-05-01] |
| **Primary regulatory PDF** | B3 oficial — Regras de Pregão V2 PDF: `https://www.b3.com.br/data/files/03/22/CE/29/87C0C6100F5DFBB6AC094EA8/Regras%20de%20Pregao%20V2.pdf` | [WEB-CONFIRMED 2026-05-01 via search-snippet cross-ref] |
| **Secondary retail #1** | Opere Futuros — Horários de Negociação Contratos Futuros BMF | [WEB-CONFIRMED 2026-05-01] |
| **Secondary retail #2** | XP Investimentos — atendimento WIN/WDO | [WEB-CONFIRMED 2026-05-01 via search-snippet cross-ref] |
| **Secondary financeira** | Empirícus — explica Mini Dólar WDO | [WEB-CONFIRMED 2026-05-01 via search-snippet cross-ref] |
| **Secondary retail #3** | Inter — ajuda investimentos mini contratos | [WEB-CONFIRMED 2026-05-01 via search-snippet cross-ref] |
| **Repo authority** | Nova persona `expertise.assets_covered.WDO.trading_hours` (auto-validation: persona was already correct; T002.6 §3.2 was the doc that needed correction, not the persona) | [WEB-CONFIRMED 2026-03-09] |
| **Glossary cross-check** | DOMAIN_GLOSSARY Parte 11 — DST abolido no Brasil desde 2019 | repo-anchored |

Cross-validation depth: every timestamp claim in §15.14.2-§15.14.4 is anchored against ≥2 independent sources (B3 official + ≥1 retail/financeira). Nova's confirmation §5 catalogs all 8 anchors and the Article IV self-audit verdict (§5 of Nova doc) explicitly confirms NO INVENTION.

#### §15.14.2 Correction (factual)

**WDO has SINGLE open auction at 09:00 sharp + settlement window 15:50-16:00 VWAP; NO close auction.**

Concretely, per Nova §1 + §3.1 confirmed authoritative:

| WDO phase (2026-05-01 BRT, post-DST winter grade) | Timestamp | Treatment |
|---|---|---|
| **Pré-abertura** (call de abertura accumulator) | 08:55:00 → 08:59:59 | Ofertas aceitas, ZERO matching |
| **Open auction disparo** (BATCH_CROSS) | **09:00:00 sharp** (<1s normal; 30s margem em desbalanceio) | Single batch-cross at clearing price; burst tradeType=4 prints simultâneos |
| **Continuous trading** | 09:00:01 → 18:00:00 | PRICE_TIME_FIFO; settlement window EMBEDDED inside continuous |
| **Settlement window** (calculation, NOT auction) | 15:50:00 → 16:00:00 | Continuous trading PROCEEDS; B3 calcula preço de ajuste como VWAP do intervalo |
| **Continuous close** | 18:00:00 | End of price-discovery contínuo |
| **Post-close admin window** | 18:00:00 → 18:30:00 (até 19:00 cancelamentos) | Apenas correções/cancelamentos; NÃO é price discovery |
| **Closing call (NOT APPLICABLE WDO)** | — | **Does NOT exist regulamentadamente for WDO**. Equities-regime confusion in T002.6 §3.2; eventual `tradeType=4` prints próximos a 18:00 são interrupções pontuais (circuit breaker / halt técnico / surveillance), NÃO fase regulada. |

Settlement price WDO = **VWAP da janela 15:50-16:00** (per B3 footnote oficial: "A apuração do preço de ajuste será das 15:50 às 16:00. Os preços de ajuste do WDO são os preços de ajuste dos respectivos vencimentos do DOL"). **NOT** a "close auction print at 18:00" as previously stated in T002.6 §3.2 inheritance.

Open auction = **09:00 SHARP single batch disparo (<1s normal duration)**. **NOT** a "09:00-09:30 prolonged auction window" — that prose in T002.6 §3.1 / persona Nova prior version was a conservative margin for desbalanceio, not the regulated phase.

#### §15.14.3 Triple-barrier 17:55 vertical SEMANTICS CORRECTED

**Operational rule UNCHANGED. Documented semantics CORRECTED.**

Operationally — verbatim preservation per Anti-Article-IV Guard #4 (thresholds) + parent spec yaml v0.2.3 (triple-barrier vertical exit):

```
Vertical time barrier rule (UNMOVED):
    last `tradeType ∈ {1,2,3,13}` print with timestamp < 17:55:00 BRT
```

Documented semantics — CORRECTED:

| Aspect | v1.0.0..v1.2.0 prose (INCORRECT) | v0.3.0 prose (CORRECTED) |
|---|---|---|
| Why 17:55 BRT? | "Boundary with closing auction phase 17:55-18:00" (inherited from T002.6 §3.2 closing-call confusion — NONEXISTENT phase) | **"5-minute conservative buffer before continuous-trading close at 18:00:00 BRT"** — strategy-thesis decision to exit positions before the operational close; protects against late-day liquidity thinning + microstructure outliers + admin-window contamination 18:00-18:30 |
| Relationship to settlement window | (implicit / unstated) | **17:55 BRT is 1h55min after settlement window ENDED at 16:00**; settlement is COMPLETED long before vertical exit fires. Settlement and triple-barrier are temporally independent; they do not interact |
| Protective interpretation of `auction.exclude_open_close_minutes: 5` | "Excludes call-de-fechamento 17:55-18:00" (NONEXISTENT phase) | **"Conservative protection against esporádicos `tradeType=4` micro-leilões/halts próximos ao close 18:00"** — circuit-breaker / halt-técnico / surveillance interrupções, NOT a regulated fase |
| Backtest computation impact | NONE (the operational rule is unchanged) | NONE — confirmed |

**The triple-barrier 17:55 vertical timestamp was operationally correct all along.** v1.0.0..v1.2.0 prose erroneously DOCUMENTED it as "boundary with auction"; v0.3.0 prose CORRECTLY documents it as "5min pre-close buffer". Any DSR / PBO / IC numeric result computed in Round 1 (N7) / Round 2 (N7-prime) / Round 3 (N8 OOS) consumed the SAME exit timestamp under either prose interpretation; the numeric verdicts STAND.

#### §15.14.4 §4 auction state block — corrected canonical yaml (Nova §4 verbatim consumption)

**Per Anti-Article-IV (No Invention) trace policy: this is verbatim consumption of Nova `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` §4 yaml block, which is itself sourced from B3 official PUMA + 7 cross-checked anchors enumerated §15.14.1.**

Readers MUST consult this §15.14.4 block as the canonical Nova-authoritative auction state for any future Mira/Beckett/Riven/Pax/Nelo consumer of this Gate 4b spec. The §4.1 v1.0.0 yaml (which inherited T002.6 §3.2 closing-call confusion) is preserved verbatim above per append-only governance — it remains as historical record of the inheritance error, NOT as a source of truth for v0.3.0+ consumers.

```yaml
# Nova authoritative spec block — auction phases WDO 2026-05-01 BRT
# Substitui (semanticamente, NOT operacionalmente): Mira spec v0.2.x §4 auction state block (que herdou erro T002.6 §3.2 "closing call 17:55-18:00")
# Status: [WEB-CONFIRMED 2026-05-01]; cross-validated 5 sources (B3 PUMA + 4 retail).
# Fonte primária: https://www.b3.com.br/pt_br/solucoes/plataformas/puma-trading-system/para-participantes-e-traders/horario-de-negociacao/derivativos/cambio-e-dolar-pronto/

auction_phases_wdo_2026_post_dst:
  pre_open:
    start_brt: "08:55:00"
    end_brt:   "08:59:59"
    matching:  "NONE"           # ofertas aceitas, sem cruzamento
    detection_signal:
      live:    "fase reportada por DLL (Nelo); zero TNewTradeCallback events"
      historic: "timestamp gap > 12h desde último trade D-1; nTradeNumber baixo no primeiro trade D"

  open_auction_disparo:
    timestamp_brt: "09:00:00"
    matching:  "BATCH_CROSS"    # cruza overhang ao clearing price único
    duration:  "<1s normal; pode estender em desbalanceio (margem conservadora 30s)"
    tape_signature:
      live:    "burst de tradeType=4 com prints simultâneos ao mesmo preço (clearing) em <1s"
      historic: "burst de prints com timestamps comprimidos em 09:00:00.x; preço idêntico em múltiplos prints; aggressor=NONE (parquet) onde live mostraria tradeType=4"

  continuous:
    start_brt: "09:00:01"        # imediatamente pós-disparo open
    end_brt:   "18:00:00"
    matching:  "PRICE_TIME_FIFO"
    embedded_settlement_window:
      start_brt: "15:50:00"
      end_brt:   "16:00:00"
      semantics: "negociação contínua segue; B3 calcula preço de ajuste WDO como VWAP do intervalo (= preço de ajuste do DOL correspondente)"
      tape_signature: "price compression (sigma intra-minuto cai ~30-50% vs janela 15:30-15:50); pin-risk attractor toward expected VWAP"

  post_close_admin_window:
    start_brt: "18:00:00"
    end_brt:   "18:30:00"        # janela administrativa B3
    cancellations_allowed_until_brt: "19:00:00"
    matching:  "NONE_NEW_TRADES"  # apenas correções/cancelamentos
    treatment_in_features: "EXCLUDE — tape >18:00:00 é ruído administrativo, não price discovery"

closing_call_explicit_phase:
  exists_for_wdo: false           # CRÍTICO — diferente de equities
  notes: |
    WDO **não possui leilão de fechamento dedicado** análogo às ações que compõem índices B3.
    Eventuais tradeType=4 prints próximos a 18:00 são interrupções pontuais (circuit breaker,
    halt técnico, surveillance), NÃO uma fase regulada da grade diária.
    Spec T002.6 §3.2 que afirmava "closing call 17:55-18:00" foi corrigida nesta T002.7 — o
    timestamp 17:55 do triple-barrier exit do parent yaml v0.2.3 mantém-se UNMOVABLE como
    decisão de strategy thesis (5min de buffer pré-close), mas a SEMÂNTICA não é "boundary
    com auction" e sim "buffer conservador antes do encerramento contínuo às 18:00".

dst_brazil:
  applies: false
  abolished_year: 2019
  source_glossary: "DOMAIN_GLOSSARY Parte 11"

dst_us_impact_on_b3_grade:
  applies: true
  notes: |
    B3 ajusta sazonalmente a grade WDO/DOL devido sobreposição com NYSE/CME.
    Última transição: 2026-03-09 (fim do DST EUA → grade "winter" vigente em 2026-05-01).
    Próxima transição esperada: novembro 2026 (início DST EUA → grade "summer").
    Grade winter vs summer NÃO altera os horários WDO segundo Opere Futuros ("Não possui
    alteração de horário"); altera horário de equities. CONFIRMAR no boot do projeto contra
    comunicado B3 sazonal vigente.

reduced_sessions_holidays:
  applies: true
  policy: |
    Pré-feriados longos B3 historicamente operam half-day (encerramento antecipado).
    Calendar config/calendar/2024-2027.yaml linha 76 já registra ESC-005 fix:
    "B3 half-day Christmas Eve — Nova confirmed 2026-04-26; empirical parquet 0 trades;
    treated as full-exclusion until schema supports half_day flag".
    Auction Print Analysis DEVE excluir half-day sessions do training set até schema
    expor half_day boolean per session row.
```

#### §15.14.5 Carry-forward implications — T002 retire artifacts NOT INVALIDATED

**Round 1 + Round 2 + Round 3 + Round 3.1 retire artifacts STAND — DSR / PBO / IC interpretations are NOT modified by this v0.3.0 semantic correction.**

Why the retire verdicts stand intact:

| Round | Artifact | Was 17:55 vertical exit consumed? | Numeric verdict valid under v0.3.0 prose? | Reason |
|---|---|---|---|---|
| **Round 1 T5** (Phase F N7) | Mira Gate 4b Round 1 sign-off | YES — same operational rule | YES | The triple-barrier exit consumed `last tradeType ∈ {1,2,3,13}` print with timestamp < 17:55:00 BRT — IDENTICAL operational rule under v1.0.0 "auction-boundary" prose vs v0.3.0 "5min pre-close buffer" prose; cost/PnL math UNCHANGED |
| **Round 2 F2-T5** (Phase F2 N7-prime IC pipeline wiring) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` | YES — same operational rule | YES | F2 N7-prime added IC compute on top of N7 path-PnL; the path-PnL itself was generated by SAME operational triple-barrier rule; IC compute on `forward_return_at_1755_pts` consumed same 17:55 timestamp; semantics correction does not alter the numeric correlation |
| **Round 3 F2-T8-T5** (Phase G N8 OOS) | Mira Round 3 OOS re-clearance sign-off | YES — same operational rule | YES | OOS hold-out window 2025-07-01..2026-04-21 consumed IDENTICAL operational triple-barrier rule per ESC-012 R6 reusability invariant; numeric verdict (DSR/PBO/IC + decay test) unaffected by prose correction |
| **Round 3.1 T002 RETIRE FINAL** | Per spec §0 falsifiability — DSR=0.206 strict bar fail under K1>0.95 UNMOVABLE | YES — same operational rule | YES — VERDICT STANDS | The K1 strict bar fail (DSR=0.206 << 0.95) was the statistical interpretation result; auction state correction is purely SEMANTIC/DOCUMENTATION (corrects the prose explanation of WHY 17:55 was chosen). The retire verdict STANDS per spec §0 falsifiability. T002 is RETIRED per Round 3.1; v0.3.0 amendment does NOT reverse, weaken, or modify that verdict. |

**Why this is not Article IV invention:** the operational rule consumed by the backtest harness was literally the same string `"last tradeType ∈ {1,2,3,13}` print with timestamp < 17:55:00 BRT"` under both prose explanations. The prose was wrong; the rule was right; the math is unaffected. v0.3.0 corrects the explanation to match the rule, not the rule to match the explanation.

**Riven 3-bucket attribution unaffected:** bucket B `costed_out_edge OOS-confirmed` (Round 3.1 final attribution per Riven F2-T8-T6 Round 3 reclassify) STANDS. v0.3.0 does NOT reopen attribution; the auction-state semantic correction is documentation-layer, not data-quality-layer.

**No re-run / re-clearance / reclassify required.** §12.3 sign-off chain is single-stage Mira semantic-correction publish — no Aria archi review / no Beckett N9 re-run / no Quinn QA gate / no Riven reclassify needed because nothing the downstream depends on has changed.

#### §15.14.6 H_next-1 successor inheritance

The H_next-1 successor strategy spec (in drafting on branch `t003-h-next-spec-drafting`; future story T003+) MUST inherit the **CORRECTED** auction state block from §15.14.4 verbatim — NOT the v1.0.0 §4 inheritance from T002.6 §3.2 closing-call confusion.

Concretely:

- H_next-1 spec authors (Mira authority for ML/statistical layer; Nova authority for microstructure layer) MUST consume §15.14.4 yaml block, NOT §4.1 yaml block, when building auction state contract for the successor strategy.
- Any feature design referencing "close auction 17:55-18:00" / "leilão de fechamento WDO" / "settlement print 18:00 closing" is **REJECTED a priori** as Article IV (No Invention) violation — those phases do NOT exist regulamentadamente for WDO per §15.14.2 + Nova §3.2 confirmation.
- Settlement Window Analysis (Nova §3.2 P2 SECONDARY recommendation: VWAP 15:50-16:00 deviation feature) IS in-scope for H_next-1 candidate features, computable in trades-only parquet (VWAP of timestamp-windowed subset), per Nova's GREEN-LIGHT.
- Open Auction Print Analysis (Nova §3.2 P1 SECONDARY recommendation: gap_overnight feature 08:55-09:00:30 BRT window) IS in-scope for H_next-1 candidate features, computable in trades-only parquet for the gap component (cross-day price differential); pre-open book imbalance live-only deferred to Phase H.

Successor spec versioning: H_next-1 spec inherits this v0.3.0 auction state correction; v0.3.0 is the current canonical Mira spec at the time of T003 spec drafting commencement.

#### §15.14.7 Article IV self-audit

| §15.14 claim | Source anchor (verified) |
|---|---|
| Nova authoritative confirmation 2026-05-01 BRT (8 source anchors B3 official + secondary cross-validation) | `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` Final v1.0.0 §1-§6 (270 lines) |
| WDO settlement = VWAP 15:50-16:00 (NOT close auction print 18:00) | B3 oficial PUMA Câmbio e Dólar Pronto footnote (2): "A apuração do preço de ajuste será das 15:50 às 16:00" — Nova §1 row "Cálculo do preço de ajuste" + §5 anchor #1 verbatim |
| WDO has NO close auction (regulamentadamente) — equities-regime confusion in T002.6 §3.2 | Nova §2 Discrepancy 1 verbatim ("CRÍTICA — call de fechamento WDO 17:55-18:00 não existe formalmente"); B3 oficial Regras de Pregão V2 PDF (closing-call regime is equities-only) — Nova §5 anchor #8 |
| Open auction = 09:00 SHARP single disparo <1s (NOT 09:00-09:30 window) | Nova §1 row "Início negociação contínua" + §2 Discrepancy 3 ("o call de abertura ocorre 08:55→09:00. Em 09:00 sharp o leilão dispara, gera burst de tradeType=4 em <1s, e inicia imediatamente a fase contínua. Não existe janela 09:00-09:30 de auction prolongado em condições normais"); B3 PUMA oficial + Opere Futuros cross-validated |
| Triple-barrier 17:55 vertical operational rule UNMOVED (only semantics corrected) | Parent spec yaml `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` triple-barrier vertical exit; this spec §2.1 operational rule preserved verbatim; Nova §2 Discrepancy 1 explicit: "o exit triple-barrier 17:55 BRT da spec yaml v0.2.3 É VÁLIDO como timestamp de entrada/saída — o que muda é a SEMÂNTICA" |
| Round 1+2+3+3.1 retire artifacts NOT INVALIDATED (numeric verdicts stand) | This spec §15.14.5 carry-forward table; Anti-Article-IV Guard #4 thresholds UNMOVABLE; Round 3.1 verdict per spec §0 falsifiability stands |
| H_next-1 successor inherits v0.3.0 corrected auction state block | This spec §15.14.6; Nova §3.2 GREEN-LIGHT for Settlement Window + Open Auction Print Analysis SECONDARY directions; Article IV (No Invention) bars H_next-1 from referencing nonexistent close auction phase |

**Article IV self-audit verdict (§15.14 amendment):** every claim traces. **NO INVENTION.** §15.14 is the **operationalization** of Nova authoritative finding 2026-05-01 BRT (270-line confirmation, 8 source anchors B3 official). Thresholds UNMOVABLE; triple-barrier 17:55 operational rule UNMOVED (only semantics corrected); Round 1 + Round 2 + Round 3 + Round 3.1 sign-offs UNMOVED; Round 3.1 T002 RETIRE FINAL verdict STANDS per spec §0 falsifiability; §0-§14 v1.0.0 + §15.1-§15.13 v1.1.0/v1.2.0 body content UNCHANGED; §4.1 v1.0.0 yaml preserved verbatim as historical record; §15.14.4 is the canonical auction state for v0.3.0+ consumers — append-only revision per Pax governance.

**Anchor count (§15.14-local):** 7 source anchors verified — Nova authoritative confirmation `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` (Final v1.0.0; 270 lines; 8 internal source anchors §5 #1-#8); B3 oficial PUMA Câmbio e Dólar Pronto (regulatory primary); B3 oficial Regras de Pregão V2 PDF; Nova persona `expertise.assets_covered.WDO.trading_hours` (auto-validation [WEB-CONFIRMED 2026-03-09]); DOMAIN_GLOSSARY Parte 11 (DST abolido Brasil 2019); parent spec yaml `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` (triple-barrier 17:55 vertical exit operational rule); this spec §1 thresholds UNMOVABLE + §2.1 triple-barrier semantics + §4.1 v1.0.0 inheritance preserved + Anti-Article-IV Guards #1-#8.

---

## Change Log

| Version | Date (BRT) | Author | Change |
|---|---|---|---|
| **v1.0.0** | 2026-04-29 | Mira (@ml-researcher) | Skeleton drafted pre-merge ESC-011 R11 (fence-against-drift); finalized T0a same day — full spec consumable by Aria T0b / Beckett T0c / Riven T0d / Pax T0e + Dex T1; 8 dimensions covered (T002.6 §Spec-first protocol); Beckett latency spec §5 + Nova RLP/rollover spec §4 consumed verbatim |
| **v1.1.0** | 2026-04-30 | Mira (@ml-researcher) | **Phase F2 amendment §15 IC Pipeline Wiring Spec applied** per Mira deep audit `docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md` §6 + Aria archi review `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` (APPROVE_OPTION_D — separate orchestration module in `vespera_metrics`; conditions C-A1..C-A7) + Beckett consumer audit `docs/backtest/T002.6-beckett-consumer-signoff.md` §T0c + Sable audit `docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md` (8 findings — F-01..F-04 procedural recommendations consumed). §12.1 sign-off chain extended F2-T0a..F2-T6; §14.3 cosign ledger added; §15.5 Anti-Article-IV Guard #8 NEW (verdict-issuing protocol — IC field default 0.0 reserved for pre-compute state only; `*_status` provenance flag mandatory; `InvalidVerdictReport` raise on `K_FAIL` with `*_status != "computed"`); §15.8 4 NEW tests in `tests/vespera_metrics/test_ic_pipeline_wired.py` (`test_ic_computed_non_zero`, `test_ic_deterministic`, `test_ic_status_flag`, `test_ic_inconclusive_path`). NO mutation of §1 thresholds (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0); NO mutation of hold-out lock (Anti-Article-IV Guard #3); NO mutation of Round 1 T5 sign-off; NO §0-§14 v1.0.0 body content mutation — append-only revision. Cosign Mira @ml-researcher 2026-04-30 BRT — F2-T0a spec amendment applied. |
| **v1.2.0** | 2026-04-30 | Mira (@ml-researcher) | **Mira spec amendment v1.1.0 → v1.2.0 §15.13 Phase G OOS unlock protocol applied per ESC-012 R2 ratification (5/6 supermajority APPROVE_PATH_B + 17 conditions R1-R17).** §15.13 NEW (Phase G OOS Unlock Protocol — 13 sub-sections §15.13.1..§15.13.13 covering: unlock authorization 5/6 supermajority + Riven minority Path C dissent preserved; unlock mechanism `holdout_locked=False`; Phase G run window 2025-07-01..2026-04-21; reusability invariants engine_config + cost atlas + rollover + Bonferroni + latency + RLP + microstructure ALL IDENTICAL F2 per ESC-012 R6; predictor↔label IDENTICAL F2 per ESC-012 R7; decay test full evaluation `IC_holdout > 0.5 × IC_in_sample` BINDING; K1 strict bar UNMOVABLE preservation per ESC-012 R10; OOS one-shot discipline per ESC-012 R9; pre-committed 4-branch disposition rule PRR-20260430-1 hash-frozen BEFORE N8 run per ESC-012 R3; sample-size considerations ~3000-4000 events; wall-time + RSS budget ~3h/~600 MB; Article IV trace policy 5-source; sign-off chain F2-T8-T0a..F2-T8-T7; self-audit 17 source anchors). §12.2 sign-off chain extended F2-T8-T0a..F2-T8-T7 (Round 3 — spec amendment + Phase G N8 OOS run + re-clearance + reclassify + close). §14.4 cosign ledger added (Round 3). NO mutation of §1 thresholds (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0); NO mutation of hold-out lock policy (Phase G unlock IS the authorized §15.10 transition pre-authored at spec §3.1, NOT a guard violation per ESC-012 R10 K1 strict bar UNMOVABLE preservation); NO mutation of Round 1 T5 sign-off; NO mutation of Round 2 F2-T5 sign-off (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md`; F2-T8-T5 Round 3 supersedes via append-only ledger entry NOT mutation); NO §0-§14 v1.0.0 body content mutation; NO §15.1-§15.12 v1.1.0 content mutation — append-only revision. Cosign Mira @ml-researcher 2026-04-30 BRT — F2-T8-T0a spec amendment v1.2.0 applied. |
| **v0.3.0** | 2026-05-01 | Mira (@ml-researcher) | **Mira spec amendment v1.2.0 → v0.3.0 §15.14 Auction State Block Correction applied per Nova authoritative confirmation `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md` (Final v1.0.0; 270 lines; 8 source anchors B3 official + secondary cross-validation).** **Semver re-baseline v1.2.0 → v0.3.0** per MANIFEST R15 spec versioning protocol — major==0 governance recognizes prior v1.x labels were internal Phase F/F2/G iteration counters; v0.x is the canonical Mira-spec series under Anti-Article-IV Guard #4 thresholds-frozen + pre-stable governance. §15.14 NEW (Auction State Block Correction — 7 sub-sections §15.14.1..§15.14.7 covering: source provenance Nova confirmation cross-checked B3 PUMA + B3 Regras de Pregão V2 PDF + 6 secondary anchors; correction WDO has SINGLE open auction at 09:00 SHARP single-batch disparo <1s + settlement window 15:50-16:00 VWAP; NO close auction regulamentadamente — equities-regime confusion in T002.6 §3.2 corrected here; triple-barrier 17:55 vertical SEMANTICS CORRECTED to "5-minute conservative buffer before continuous-trading close at 18:00:00 BRT" NOT "boundary with closing auction"; §4 auction state block updated yaml — Nova §4 verbatim consumption per §15.14.4 canonical block readers MUST consult for v0.3.0+ semantic interpretation; carry-forward implications T002 retire artifacts Round 1+2+3+3.1 NOT INVALIDATED — DSR/PBO/IC numeric verdicts STAND because triple-barrier 17:55 operational rule was UNCHANGED under both prose interpretations, only the documented prose explanation was wrong, the math is unaffected; H_next-1 successor on branch `t003-h-next-spec-drafting` MUST inherit CORRECTED §15.14.4 auction block, NOT v1.0.0 §4 inheritance from T002.6 §3.2 closing-call confusion; Article IV self-audit §15.14.7 with 7 source anchors). §12.3 sign-off chain extended (single-stage Mira semantic-correction publish v0.3.0-T0a — no re-run / re-clearance / reclassify required because operational rule UNCHANGED and downstream depends on rule not prose). NO mutation of §1 thresholds (Anti-Article-IV Guard #4 UNMOVABLE: DSR>0.95 / PBO<0.5 / IC>0); NO mutation of triple-barrier 17:55 vertical timestamp operational rule (UNMOVED — only documented SEMANTICS corrected from "auction boundary" to "5min pre-close buffer"); NO mutation of Round 1 T5 sign-off; NO mutation of Round 2 F2-T5 sign-off; NO mutation of Round 3 F2-T8-T5 sign-off; **NO mutation of Round 3.1 verdict (T002 RETIRE FINAL stands per spec §0 falsifiability — DSR=0.206 strict bar fail; v0.3.0 correction is semantic/documentation, not statistical interpretation reversal); NO mutation of Riven 3-bucket attribution (bucket B `costed_out_edge OOS-confirmed` STANDS)**; NO §0-§14 v1.0.0 + §15.1-§15.13 v1.1.0/v1.2.0 body content mutation; §4.1 v1.0.0 yaml preserved verbatim as historical record of T002.6 §3.2 inheritance error — append-only revision per Pax governance. Cosign Mira @ml-researcher 2026-05-01 BRT — v0.3.0-T0a spec amendment v1.2.0 → v0.3.0 applied (auction state block semantic correction). |

— Mira, mapeando o sinal 🗺️
