---
council: DATA-2026-05-01-dll-backfill
topic: Pre-2024 DLL archival backfill viability for forward H_next-1 OOS hold-out (consumer perspective)
date_brt: 2026-05-01
voter: Beckett (@backtester)
role: Backtester & Execution Simulator authority — consumer of historical tape (CPCV runner; pessimistic-by-default; "if the dataset is uncertain, I parameterize")
constraint_recap:
  - User canonical Path A OFF (cost atlas v1.1.0 FROZEN); Path here means BACKFILL data path, NOT cost reduction
  - QUANT 2026-05-01 ratified PRIMARY = H_next-1 Conviction-Conditional Sizing on T002 predictor IP (R1-R17)
  - QUANT R7: forward-time virgin hold-out 2026-05-01..2026-10-31 PRIMARY hold-out window (Mira preferred)
  - QUANT R8: pre-2024 archival hold-out 2023-Q1..2024-Q3 FALLBACK conditional on Dara coverage + Sable virgin audit (Kira preferred)
  - QUANT R9: walk-forward rolling REJECTED (carry-forward — reaffirmed)
  - Hold-out 2025-07..2026-04 BURNED on N8.2 (§15.13.7 one-shot binding); not reusable
  - Existing dataset: D:\sentinel_data\historical\ — 571 WDO days + 269 WIN days (840 parquet files; 2024-01..2026-03)
  - Trades-only schema (no historical book) — Beckett MANIFEST §historical_data_reality
authority_basis:
  - Beckett MANIFEST R11-R14 — domain authority: simulator-side viability (CPCV executability, fill rules, slippage model, dataset hash discipline); NÃO COMO de orquestração/captura
  - Beckett MANIFEST R15 — Spec Consumer (Mira spec authoring forward-binding; Beckett executes)
  - Beckett MANIFEST §reproducibility_checklist — every run registers seed + simulator version + dataset hash + spec hash + engine-config hash + rollover-calendar hash + cpcv config + lockfiles
  - QUANT R3 — Bonferroni adjusted DSR threshold 0.95 → ~1.005 (n_trials=8 carry-forward); EXTRA evidence required at fresh-OOS scale
  - QUANT R8 — pre-2024 archival hold-out CONDITIONAL on Dara coverage confirm + Sable virgin audit (NOT ratified blanket; this council ballot is on whether to PURSUE that path)
  - Lopez de Prado AFML cap 11-14 (multiplicity, CPCV, backtest overfitting, metrics)
  - ESC-013 R6 reusability invariant (engine_config + cost atlas + calendar + Bonferroni semantics IDENTICAL across F2-equivalent re-runs)
inputs_consulted:
  - docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md (R1-R17; PRIMARY conviction sizing; R7/R8 hold-out alternatives)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-beckett-vote.md (prior simulator-lens ranking)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-mira-vote.md (regime / stationarity reasoning §270-281)
  - data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/full_report.md + telemetry.csv (N8.2 telemetry baseline 141min wall, 9-month window)
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md §3 + §10.3 (Phase F baseline 188min wall)
  - docs/backtest/engine-config.yaml v1.1.0 (DMA2 latency profile, RLP policy, microstructure)
  - Beckett MANIFEST §historical_data_reality (trades-only dataset structural constraint)
  - Beckett MANIFEST §dataset-version (datasets-registry.yaml hash discipline)
non_pre_emption:
  - This ballot does NOT bind Dara custodial manifest authority over capture pipeline / materialization / parquet schema
  - This ballot does NOT bind Nelo authority over ProfitDLL retention semantics / backfill API (Nelo manual_profitdll.txt is canonical)
  - This ballot does NOT bind Mira regime-stationarity verdict (Mira authority on whether 2023 in-sample equivalence is acceptable for OOS measurement)
  - This ballot does NOT bind Sable virgin-audit authority (Sable QA on whether pre-2024 archival window is uncontaminated)
  - This ballot does NOT pre-empt Pax forward-research scope authority
  - This ballot does NOT pre-empt Riven custodial Bayesian prior / capital-ramp authority
  - This ballot does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
  - This ballot is CONSUMER perspective only — what Beckett would do with the data IF it existed; not whether/how Dara should produce it
---

# DATA Council 2026-05-01 — Beckett Ballot (Pre-2024 DLL Archival Backfill, Consumer Perspective)

> **Voter:** Beckett (@backtester) — Backtester & Execution Simulator authority. Pessimistic-by-default; "if the data is uncertain, I parameterize and tag [TO-VERIFY]".
> **Date (BRT):** 2026-05-01.
> **Branch:** `t002-1-bis-make-backtest-fn` (active local branch; ballot is local-only docs work).
> **Reading of council scope:** Should the squad invest in backfilling pre-2024 DLL archival data (2023-Q1..2024-Q3) to unlock H_next-1 OOS hold-out earlier than the forward-time PRIMARY window 2026-05-01..2026-10-31? Beckett evaluates **as the downstream consumer** of that hypothetical dataset: would I trust it, would I run on it, what would the run look like, what are the failure modes.

---

## §1 Consumer perspective — pre-2024 archival utility for H_next-1

### §1.1 H_next-1 OOS measurement requirements (consumer specification)

H_next-1 (Conviction-Conditional Sizing) reuses T002 predictor IP under fresh-spec-version-bump per MANIFEST R15 (n_trials counter resets cleanly to 1 IF spec-major-bump, otherwise carries Bonferroni n_trials=8 per QUANT R1-R3). For OOS measurement under §15.13.7 one-shot discipline, Beckett needs:

| Requirement | Detail | Pre-2024 archival fit |
|---|---|---|
| **Dataset virgin status** | Window NEVER touched by any prior CPCV run, dry-run, smoke test, calibration, exploratory plot, or feature-engineering pass | ⚠️ CONDITIONAL — Sable virgin-audit authoritative; Beckett cannot certify alone |
| **Schema parity with in-sample** | Same parquet columns (timestamp/ticker/price/vol/qty/buy_agent/sell_agent/aggressor/trade_type/trade_number); same BRT timezone; same trade-aggressor encoding | ⚠️ CONDITIONAL — Dara/Nelo confirm DLL retention preserved schema across 2023-2024 boundary; ProfitDLL version drift (pre-RLP introduction!) is a real risk |
| **Sample size floor** | Mira spec §6 floor 250 events OOS minimum (per T002 §15 wiring) | ✅ LIKELY MET — 6 quarters × ~50M trade-events/quarter = ~300M raw events; H_next-1 trades-per-day order ~10-50 → ~6,000-30,000 trades over 6 quarters, well above 250 floor |
| **Rollover calendar coverage** | Nova authority — 2023-Q1..2024-Q3 must have rollover dates registered (every WDO/WIN contract transition flagged) | ⚠️ CONDITIONAL — Nova materializes calendar; backfill effort if rollover-calendar.yaml does NOT extend pre-2024 |
| **Engine-config v1.1.0 applicability** | DMA2 latency profile + cost atlas v1.1.0 + RLP policy must be VALID semantic for 2023-2024 microstructure | ⚠️ HIGH RISK — RLP introduction timing in B3 may be POST-2023; cost atlas v1.1.0 reflects current emolumentos B3, NOT 2023 emolumentos; latency p50/p95/p99 estimates were calibrated against current corretora routing path; semantic mismatch is structural |
| **Reproducibility hash** | Dataset hash (SHA-256) registered in datasets-registry.yaml; rollover-calendar hash + engine-config hash + spec hash all locked | ✅ Beckett can register on receipt; Dara coordinates |

### §1.2 Sample size implication (Beckett quantitative read)

User context note states: 6 quarters × ~50M events/quarter ≈ 300M trial-events. **Important reframing:** events ≠ trial-events for hypothesis testing.

| Quantity | Value | Note |
|---|---|---|
| Raw trade-tape events 2023-Q1..2024-Q3 | ~300M | Order of magnitude; depends on ticker rollover density and intraday volume |
| Sessions covered | ~378 trading sessions (6 quarters × ~63 sessions/quarter average) | BRT calendar; needs Nova confirmation |
| Predicted H_next-1 trade events (decisions) | ~3,800-19,000 | Order-of-magnitude: 10-50 trades/session × 378 sessions; conviction-sizing reduces total trades vs T002 baseline |
| Bonferroni-adjusted DSR strict bar | ~1.005 (n_trials=8 per QUANT R3) | Demands robust evidence; small effect sizes won't clear |

**Beckett consumer read:** sample-size floor IS met by margin. The binding constraint is NOT volume — it is **semantic validity of the engine-config + cost atlas across the 2023-2024 → 2024-2026 microstructure boundary** (see §5).

### §1.3 Wall-time projection for pre-2024 archival CPCV run

Per N7-prime baseline (188 min wall for 9-month window) and N8.2 (141 min wall for hold-out of similar length):

| Window | Wall-time projection | Note |
|---|---|---|
| 1 quarter pre-2024 (e.g., 2023-Q1) | ~50 min wall | Linear scaling N7-prime baseline; 1Q ≈ 1/9 of 9mo full |
| 6 quarters full backfill (2023-Q1..2024-Q3) | ~300-400 min wall (~5-6.5h) | Linear scaling; H_next-1 OOS window would NOT be full 6Q (smaller hold-out tail) |
| H_next-1 fresh CPCV in-sample (2024-08..2025-06 retired T002) + OOS pre-2024 archival hold-out tail | ~3-4h in-sample + ~1-1.5h OOS tail | Standard one-shot pattern §15.13.7 |

**Consumer verdict on wall-time:** ✅ FEASIBLE within current Pichau infrastructure. NOT blocked by simulator throughput. Engine-config v1.2.0 perf round optional (would compress 188min → 60-90min full per Beckett QUANT vote §4) but NOT required for first pre-2024 OOS run.

---

## §2 Reusability across strategies (T-series)

### §2.1 Strategy roster post-T002 retire

| Strategy | Status | OOS hold-out need | Pre-2024 archival fit |
|---|---|---|---|
| **T002 (end-of-day inventory unwind WDO v0.2.0)** | RETIRE FINAL | predictor IP preserved; no further OOS planned | N/A |
| **H_next-1 (Conviction-Conditional Sizing on T002 predictor)** | QUANT PRIMARY | YES — fresh OOS required per §15.13.7 (2025-07..2026-04 burned) | ✅ DIRECT REUSE — uses T002 predictor IP; 2023-Q1..2024-Q3 is genuinely virgin if Sable audits |
| **H_next-2 (Auction Print Analysis Nova SECONDARY)** | QUANT SECONDARY (sequential T2) | YES — fresh OOS required; new predictor (auction-print) | ✅ POTENTIAL REUSE — auction-print signal is computable trades-only; pre-2024 window virgin per Sable audit; BUT new predictor → fresh n_trials=1 so OOS budget is NEW per QUANT R5 |
| **H_next-3 (Asymmetric Exit DEFERRED)** | QUANT DEFERRED (parallel-track if engine v1.2.0 lands) | YES — fresh OOS required; same predictor + new exit logic | ✅ POTENTIAL REUSE — same predictor IP; needs engine-config v1.2.0 OR exit state machine extension |

### §2.2 Per-strategy virgin status concern

**Critical consumer point:** "virgin per-strategy" is NOT automatic. Sable virgin-audit authority must verify that no strategy-specific touching happened. For example:

- If H_next-1 runs on pre-2024 archival as OOS → that window is BURNED for H_next-1 only (not for H_next-2 or H_next-3 conceptually, since those are different predictors)
- BUT if any **feature engineering** or **exploratory plotting** of pre-2024 data was done while developing H_next-2 (auction print analysis), the window is contaminated for H_next-2 as well
- Sable must keep a CONTAMINATION LEDGER per (strategy, window) pair

**Beckett consumer recommendation:** if pre-2024 archival is materialized, Sable maintains `docs/governance/data-contamination-ledger.yaml` with rows per `(strategy_id, window, touch_event)` and Beckett refuses to run OOS on any strategy with non-empty touches in the target window.

### §2.3 OOS budget arithmetic across H_next family

| Strategy | OOS window candidate | Cost (events/sessions) | Reusable? |
|---|---|---|---|
| H_next-1 | 2023-Q1..2024-Q3 archival | ~378 sessions; ~6,000-19,000 trades | ✅ if Sable audits virgin |
| H_next-1 | 2026-05..2026-10 forward (R7) | ~125 sessions; ~1,250-6,250 trades | ✅ NO contamination by construction (data does not exist yet) |
| H_next-2 (auction print) | 2023-Q1..2024-Q3 archival | same as above; auction-print needs first-30min data slice | ✅ if Sable audits virgin AND no auction-print exploratory work touched it |
| H_next-2 | forward-time | ~125 sessions | ✅ |
| H_next-3 (asymmetric exit) | 2023-Q1..2024-Q3 archival | same | ⚠️ exit logic uses same predictor as H_next-1; if H_next-1 ran OOS on archival, archival is BURNED for H_next-3 too (same predictor IP family) |
| H_next-3 | forward-time | ~125 sessions | ✅ |

**Critical insight:** pre-2024 archival is **NOT a free buffet** even if materialized. Each OOS run consumes the window for the corresponding predictor IP family. The serial-single-thread research discipline I argued in QUANT vote §5.3 still applies.

---

## §3 Run cost estimation (Beckett-side)

### §3.1 Beckett-side runtime cost

| Item | Cost | Note |
|---|---|---|
| First pre-2024 archival CPCV run (H_next-1 OOS tail) | ~50-90min wall on N7-prime engine config | Linear scaling baseline |
| Dataset hash registration in datasets-registry.yaml | < 5min | SHA-256 over parquet files; one-time per backfill batch |
| Engine-config v1.1.0 applicability validation (cost atlas + latency + RLP semantic) | 2-3 sessions Beckett analysis + Nova/Nelo consultation | NON-trivial; see §5 |
| Rollover calendar pre-2024 extension | depends on Nova authoring | Nova authority |
| Re-running fill-audit (`*fill-audit`) sample over pre-2024 fills | ~30min | Standard QA validation |
| `*replay` smoke-test on a known incident date pre-2024 | ~30min | Sanity check that engine semantics produce sensible fills |

### §3.2 Storage / bandwidth (NOT Beckett authority — Dara handles)

User context cites "~3 GB additional (Dara estimate)". Beckett consumer-side note: that figure is plausible for trades-only parquet (no book). If captura de book retroativo is somehow possible via DLL, multiply by 100-1000× (book updates are dense). Dara confirms.

### §3.3 Total Beckett-side cost-per-run (post-backfill landing)

| Phase | Effort | Wall |
|---|---|---|
| Engine semantic validation across 2023-2026 boundary | 2-3 sessions Beckett + cross-consult Nova/Nelo | calendar 1-2 days |
| First H_next-1 OOS pre-2024 archival run | 1 session | ~3-4h wall (in-sample + OOS) |
| Fill-audit + replay smoke-test | 1 session | ~1h wall |

**Total Beckett-side absorption:** ~3-4 sessions calendar-time once Dara/Nelo land the backfill + Sable audits virgin.

---

## §4 Alternative timeline analysis

### §4.1 Path B — Forward-only (QUANT R7 PRIMARY)

| Dimension | Reading |
|---|---|
| **Wall-clock waiting** | 6 months minimum for OOS window 2026-05..2026-10 to fully populate (Beckett N1+ run end of October 2026 minimum); realistic ~2027-Q1 if 9-month OOS sample |
| **Squad bandwidth opportunity cost** | User context cites ~120 sessions opportunity cost; Beckett perspective: this is real BUT squad can pursue parallel work (engine v1.2.0 perf round; Aria/Dex/Quinn cycle on ADR-1 amendment; Mira H_next-2 spec authoring; Nova auction-print feature exploration — though Nova exploratory work CONTAMINATES archival window per §2.2) |
| **Engine-config validity** | ✅ HIGH — forward window inherits CURRENT cost atlas + DMA2 latency calibration directly; no semantic mismatch risk |
| **Bonferroni discipline** | ✅ CLEAN — forward window is virgin by construction (data does not exist yet); no contamination ledger concern |
| **Risk: regime-shift between in-sample (2024-08..2025-06) and OOS (2026-05..2026-10)** | ⚠️ MEDIUM — 1-year forward gap; if Brazilian macro/microstructure shifts (e.g., tax regime change, B3 migration to PUMA-2.0 hypothetical, RLP policy change), OOS measurement may NOT be stationary. Mira authority on regime equivalence judgment. |
| **Beckett consumer verdict** | ✅ STRONG PREFERENCE if calendar permits; cleanest semantic + Bonferroni path |

### §4.2 Path A — DLL backfill pre-2024 (QUANT R8 FALLBACK)

| Dimension | Reading |
|---|---|
| **Wall-clock waiting** | 5-10 sessions Dara/Nelo engineering for backfill pipeline + Sable virgin audit (estimate; not Beckett authority) → THEN immediate Beckett run |
| **Squad bandwidth gain** | ~6 months earlier OOS unlock vs Path B |
| **Engine-config validity** | ⚠️ HIGH RISK — see §5; cost atlas v1.1.0, RLP detection, latency profile may be SEMANTICALLY INVALID for 2023-2024 |
| **Bonferroni discipline** | ⚠️ MEDIUM — Sable virgin audit must certify; contamination ledger discipline must be enforced; n_trials=8 carry-forward (per QUANT R3) means strict bar 1.005 DSR remains |
| **Regime-shift risk** | ⚠️ HIGH — different direction of risk vs Path B: 2023-2024 may be PRE-RLP introduction, PRE current cost atlas, PRE current DMA2 routing infrastructure. Mira authority on whether this regime is even comparable. |
| **Beckett consumer verdict** | ⚠️ ACCEPTABLE WITH CONDITIONS — only if §5 engine-validity audit clears AND Mira regime-equivalence concurrence AND Sable virgin audit clean |

### §4.3 Path C — Both (parallel-track)

| Dimension | Reading |
|---|---|
| **Information density** | ✅ HIGHEST — two independent OOS windows (2023-2024 archival + 2026-05.. forward); if BOTH confirm K1 PASS, evidence is materially stronger; if they DISAGREE, regime-shift hypothesis is empirically testable |
| **Squad bandwidth** | ⚠️ Dara/Nelo backfill while squad accumulates forward data; engineering cost is paid once on Path A, then Path B comes for free as time passes |
| **Bonferroni accounting** | ⚠️ COMPLEX — two OOS observations on same predictor IP doubles n_trials count UNLESS Mira spec pre-registers as composite OOS test (e.g., kill criterion: PASS = both windows pass strict bar; FAIL = either fails). Mira authority. |
| **Multi-window kill criterion design** | ⚠️ SPEC AUTHORING BURDEN — Mira must author composite test with explicit pre-registration; otherwise it's two separate trials |
| **Beckett consumer verdict** | ✅ THEORETICAL OPTIMUM IF Mira designs composite kill criterion cleanly; ⚠️ AVOID IF it becomes "two separate trials" (effectively halving Bonferroni power per trial) |

### §4.4 Comparison summary

| Path | Calendar | Engine validity | Bonferroni | Beckett confidence |
|---|---|---|---|---|
| **B (forward-only R7)** | +6mo wait | ✅ HIGH | ✅ CLEAN | ★★★★★ |
| **A (pre-2024 backfill R8)** | ~5-10 sessions | ⚠️ HIGH RISK (§5) | ⚠️ Sable+contamination ledger | ★★ |
| **C (both parallel)** | ~5-10 sessions + +6mo | ⚠️ HIGH RISK on A leg | ⚠️ COMPLEX (composite test) | ★★★★ if composite well-designed |

---

## §5 Microstructure regime concern (CRITICAL — Mira authority dependency)

### §5.1 Why pre-2024 archival data may NOT be valid OOS measurement

This is the deepest consumer-side concern. From Beckett MANIFEST §historical_data_reality and §expertise.session_phases_engine_behavior + §rlp_handling, the **engine semantic** is calibrated to a specific microstructure regime. Pre-2024 archival data potentially violates these calibrations:

| Engine semantic | Calibration era | Pre-2024 risk |
|---|---|---|
| **DMA2 latency profile** (p50=20ms / p95=60ms / p99=100ms / tail 500ms) | [TO-VERIFY] — current corretora routing path (2024-2026 era); no formal calibration against 2023 era | UNKNOWN — corretora may have changed routing, OEG path, network infra over 2023-2026 |
| **Cost atlas v1.1.0** (corretagem + emolumentos B3 + ISS + IR day-trade conservative) | Current B3 emolumentos schedule + current corretora pricing | **HIGH RISK** — emolumentos B3 changed multiple times historically; 2023 schedule ≠ 2026 schedule; if Path A OFF means cost atlas is FROZEN (user constraint), forcing 2026 atlas onto 2023 trades is structurally wrong (artificially favors / disfavors fills) |
| **RLP detection (tradeType=13 conservative-ignore policy)** | Post-RLP B3 microstructure regime | **CRITICAL** — RLP introduction date is a regime boundary. If 2023-Q1 is PRE-RLP, the RLP policy is not just "conservatively ignore" but "does not exist" — different microstructure altogether; queue dynamics, spread regimes, retail liquidity provisioning all differ |
| **Rollover calendar (Nova)** | Current WDO/WIN contract cycle | Pre-2024 contracts have different spec details? (WIN futures spec changes are rare but possible; Nova authority) |
| **Session phases** (pré-abertura, leilão, contínuo, call) | Current B3 trading hours post-DST normalization | Pre-2024 may have had different session windows during DST migration |

### §5.2 Beckett pessimistic-by-default consumer reading

If I run H_next-1 CPCV on pre-2024 archival data with engine-config v1.1.0 calibrated to current era, **the OOS measurement is contaminated by engine-semantic drift, not just stationarity drift**. The DSR I produce is a measure of "edge under HYPOTHETICAL 2026 cost+latency atlas applied to 2023 tape" — not "edge under actual 2023 conditions" and not "edge under current conditions". It is neither.

This is a **structural Article IV concern**: the simulator output would not faithfully reproduce ANY actual execution regime. Pessimistic-by-default discipline forces me to flag this LOUDLY.

### §5.3 Mira authority dependency

Mira regime-stationarity verdict is the gating decision per QUANT R8. Specifically:

| Question for Mira | Why it matters |
|---|---|
| Is microstructure regime in 2023-2024 stationary-equivalent to 2024-2026 for purposes of evaluating H_next-1 conviction-sizing on T002 predictor IP? | Determines whether the OOS measurement is meaningful at all |
| Are RLP introduction date, B3 emolumentos schedule changes, COVID aftermath effects sufficient to invalidate engine-config v1.1.0 applicability to pre-2024? | Determines whether engine-config v1.1.0 needs a "v1.0.0-historical" branch for pre-2024 era |
| If regime is materially different, does Mira accept a TWO-ATLAS regime (engine-config v1.1.0 for 2024+; engine-config v1.0.0-historical for pre-2024)? | Triggers a NEW spec breaking_field per MANIFEST R15 (engine_config family change) → fresh n_trials=1 reset on H_next-1 OOS calibration; this could actually be CLEANER Bonferroni-wise |

**Beckett consumer verdict on §5:** I cannot vote APPROVE Path A in good conscience without Mira concurrence on regime equivalence (or explicit Mira approval of two-atlas regime). I CAN vote conditional approval pending Mira sign-off.

### §5.4 Engine-config v1.0.0-historical branch (if Path A pursued)

If council does pursue Path A despite §5.1-§5.3, Beckett would author engine-config v1.0.0-historical with the following [TO-VERIFY] parameters:

| Parameter | v1.1.0 current | v1.0.0-historical 2023-2024 candidate |
|---|---|---|
| RLP policy | conservative-ignore (tradeType=13) | DOES-NOT-EXIST (pre-RLP era) [TO-VERIFY Nelo on RLP introduction date] |
| Cost atlas (corretagem) | current corretora pricing | [TO-VERIFY] historical pricing; may need corretora archive |
| Cost atlas (emolumentos B3) | current B3 schedule | [TO-VERIFY Nova] — historical emolumentos schedule per official B3 publication |
| DMA2 latency profile | current routing | [TO-VERIFY Tiago/Nelo] — 2023 routing may not have telemetry; Beckett would default to 1.5× current (more conservative under uncertainty) |
| Rollover calendar | Nova v current | Nova extension pre-2024 |

This is a **non-trivial engineering effort** — easily 5-10 sessions of Nelo + Nova + Beckett collaboration even before Dara backfill lands.

---

## §6 Personal preference disclosure (pessimistic-by-default)

### §6.1 Subjective priors

| Path | My subjective P(produces a meaningful, trustworthy H_next-1 OOS verdict in 2026) |
|---|---|
| **Path B (forward-only)** | ~70% (limited by H_next-1 being a real strategy that survives; engine semantic is HIGH confidence) |
| **Path A (pre-2024 backfill standalone)** | ~25% (limited by §5 engine semantic mismatch + Sable audit pass + Mira regime concurrence — three independent gates) |
| **Path C (both, composite kill criterion)** | ~55% (gains over A standalone via cross-validation; loses vs B standalone via complexity surface) |
| **DEFER (no backfill, Path B only, accept 6mo wait)** | matches Path B |

### §6.2 Why I am pessimistic on Path A standalone

Three compounding gates:

1. **§5 engine semantic validity** — must be cleared by Nelo (RLP date), Nova (emolumentos schedule), Tiago (latency calibration archive), all [TO-VERIFY]
2. **Sable virgin audit** — must certify no contamination from prior exploratory work
3. **Mira regime equivalence concurrence** — must affirm 2023-2024 is stationary-equivalent enough that the OOS measurement is interpretable

Probability of all three independently passing: pessimistic-by-default I price at ~30-40%. Any one failure invalidates the entire backfill investment.

### §6.3 Why I lean toward DEFER over A or C

The core hypothesis I am testing is:

> Does H_next-1 conviction-conditional sizing recover gross edge above costs?

The answer to this hypothesis does NOT depend on running OOS measurement EARLIER. It depends on running OOS measurement RELIABLY. Path B is the most reliable. Path A introduces three new failure modes (§6.2). The 6-month wait is a real cost but it is dominated by squad bandwidth opportunity cost calculation, NOT by simulator-side urgency.

In the meantime, the squad can productively:
- Run engine-config v1.2.0 perf round (Aria/Dex/Quinn — non-blocking from Beckett vote QUANT §4)
- Have Mira author H_next-1 spec under fresh-spec-major-bump (clean MANIFEST R15 reset)
- Have Mira author H_next-2 (auction print) spec in parallel as backup direction
- Begin Dara fresh-tape capture pipeline NOW (forward OOS budget for 2027-Q1+ unlocks)
- Build out Sable contamination ledger discipline
- Run smoke tests on T002 predictor IP under conviction-sizing transformation against in-sample window (no new OOS consumed)

That is roughly 6 months of useful work. Calendar is not idle.

### §6.4 Bias self-audit

- I am **biased toward Path B** because it has the cleanest engine-semantic story (no §5 burden) — this is a Beckett-MANIFEST persona bias (pessimistic-by-default), not an alpha bias
- I am **biased AGAINST Path A** because §5 risk surface compounds — this is a fair simulator-lens read; if Mira/Nelo/Nova all confirm engine semantic carries forward cleanly, my prior shifts upward
- I am **biased toward DEFER** as a natural "do less, do well" position; this is consistent with Lopez de Prado AFML cap 13 anti-overfitting discipline
- I am **NOT biased against Dara fresh-tape capture pipeline kickoff** — that is canonically valuable regardless of this council outcome (preserves forward-OOS budget)
- I am **NOT biased against engine-config v1.0.0-historical authoring** as such — it is a clean engineering deliverable IF council decides Path A is worth pursuing

---

## §7 Recommendation

### §7.1 Beckett vote: **APPROVE_PATH_B** (forward-only, with parallel productivity work)

**Vote rationale (consumer-perspective summary):**

1. Path B forward-only window 2026-05..2026-10 is the cleanest engine-semantic OOS measurement. No §5 regime-shift risk surface; no Sable virgin audit dependency; engine-config v1.1.0 directly applicable.
2. Path A pre-2024 archival has three independent failure gates (§6.2) compounding at ~30-40% all-pass probability. Investment in Dara backfill + Nelo retention extension + Nova rollover-calendar pre-2024 + engine-config v1.0.0-historical authoring is at risk of producing an OOS measurement that is neither valid for 2023 conditions nor for current conditions.
3. Path C parallel both is theoretically optimal IF Mira designs composite kill criterion cleanly, but operationally complex (Bonferroni accounting, contamination ledger across windows, two-atlas regime). Beckett consumer-side confidence ~55%.
4. The 6-month wait under Path B is NOT idle calendar (§6.3 — engine v1.2.0 perf round, Mira spec authoring, Dara fresh-tape capture kickoff, Sable contamination ledger discipline, in-sample smoke tests).

### §7.2 Conditional approval of Path C (downgrade from primary recommendation)

If council nonetheless prefers parallel-track for information density: Beckett conditional APPROVE Path C **only if** all of:

1. Mira authors composite kill criterion explicitly pre-registered (single OOS verdict from two windows; not two separate trials)
2. Mira concurs on regime equivalence (or authors two-atlas regime spec branch)
3. Sable audits 2023-Q1..2024-Q3 archival window virgin per per-strategy contamination ledger
4. Nelo confirms ProfitDLL retention semantics extend cleanly pre-2024 with same schema
5. Nova confirms rollover calendar materialization for pre-2024 contracts
6. Beckett authors engine-config v1.0.0-historical [TO-VERIFY] branch with explicit conservative defaults (§5.4)

If ANY of conditions 1-6 fails, Beckett auto-downgrades vote to APPROVE_PATH_B.

### §7.3 Reject Path A standalone

Beckett consumer-side reject of Path A as STANDALONE (without Path B fallback) — too much engine-semantic risk, too much dependency surface, no upside vs Path C if council wants the early information unlock.

### §7.4 Independently of A/B/C choice

**Beckett independently recommends** (overlap with QUANT §5.3):

- Begin Dara fresh-tape capture pipeline NOW for forward OOS budget unlock 2027-Q1+ (Path B feeds this naturally; Path C accelerates it)
- Sable contamination ledger discipline `docs/governance/data-contamination-ledger.yaml` instituted regardless of A/B/C choice (per-strategy × per-window touch tracking)
- Engine-config v1.2.0 perf round non-blocking parallel-track (per QUANT R17)
- Mira H_next-1 spec authoring under fresh-spec-major-bump (clean MANIFEST R15 n_trials reset)

---

## §8 Article IV self-audit

Per Constitution Article IV (No Invention) + Beckett MANIFEST R15 spec-consumer discipline.

### §8.1 Trace anchoring

| Claim | Trace anchor |
|---|---|
| QUANT 2026-05-01 R7/R8/R9 hold-out conditions | docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md §4.2 verbatim |
| QUANT R1-R3 Bonferroni n_trials=8 carry-forward + DSR strict bar ~1.005 | COUNCIL-2026-05-01-QUANT-resolution.md §4.1 verbatim |
| §15.13.7 OOS one-shot; 2025-07..2026-04 BURNED on N8.2 | Mira spec v1.2.0 §15.13.7 + COUNCIL-2026-05-01-QUANT-resolution.md §4.2 R6 |
| N7-prime 188min wall + N8.2 141min wall baselines | docs/backtest/T002-beckett-n7-prime-2026-04-30.md §3 + data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/full_report.md verbatim |
| Engine-config v1.1.0 frozen DMA2 latency p50=20ms/p95=60ms/p99=100ms/tail 500ms | docs/backtest/engine-config.yaml + Beckett MANIFEST §latency_dma2_profile |
| Trades-only dataset structural constraint; 571 WDO / 269 WIN days; 2024-01..2026-03 coverage | Beckett MANIFEST §historical_data_reality |
| Sample size order-of-magnitude (~50M events/quarter; ~63 sessions/quarter) | User context note + Beckett MANIFEST §historical_data_reality coverage figures |
| RLP introduction as regime boundary [TO-VERIFY] | Beckett MANIFEST §rlp_handling + flagged [TO-VERIFY] in §5.1 |
| Cost atlas v1.1.0 frozen per Path A OFF | User canonical constraint carry-forward + COUNCIL-2026-05-01-QUANT-resolution.md preamble |
| Subjective priors §6.1 / §6.2 | EXPLICITLY MARKED AS SUBJECTIVE per pessimistic-by-default disclosure protocol |
| Calendar estimates (5-10 sessions Dara/Nelo; 6 months forward wait; 50min/quarter wall) | Per-task estimates surfaced as informational; not spec-binding |

### §8.2 Invention check

- ❌ NO new statistical thresholds invented (DSR 1.005 carry-forward from QUANT R3)
- ❌ NO new spec-binding rules introduced (CV scheme = T002 carry-forward; same engine; same Bonferroni)
- ❌ NO new agent authorities created (Mira regime authority, Sable virgin audit, Nelo retention semantics, Nova rollover calendar, Dara backfill — all existing matrix)
- ❌ NO new dataset semantic categories (engine-config v1.0.0-historical is a HYPOTHETICAL conditional construct, only authored if Path A/C pursued; its parameter values are explicitly [TO-VERIFY])
- ❌ NO simulator semantics modified for Path B (engine-config v1.1.0 preserved)
- ❌ NO H_next selected on Beckett's behalf (QUANT council ratified; this ballot is consumer-side data-sourcing perspective only)
- ✅ Subjective priors §6.1/§6.2 explicitly surfaced as subjective for council audit
- ✅ §5.4 v1.0.0-historical parameters explicitly [TO-VERIFY] tagged
- ✅ Calendar estimates clearly marked as estimates

### §8.3 Authority boundary check

- ✅ Vote does NOT bind Dara custodial manifest authority over capture pipeline / parquet schema / materialization scheduling
- ✅ Vote does NOT bind Nelo authority over ProfitDLL retention semantics / backfill API / RLP introduction date
- ✅ Vote does NOT bind Mira regime-stationarity verdict (explicitly identified as gating dependency)
- ✅ Vote does NOT bind Sable virgin-audit authority (explicitly identified as gating dependency)
- ✅ Vote does NOT pre-empt Pax forward-research scope authority
- ✅ Vote does NOT pre-empt Riven custodial Bayesian prior / capital-ramp authority
- ✅ Vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
- ✅ MANIFEST R11-R14 escopo respeitado: domain authority on simulator-side viability + dataset-hash discipline; NÃO COMO de captura/orquestração
- ✅ Anti-Article-IV Guard #8 verdict-issuing protocol respected — Beckett does not emit data/regime/risk verdicts outside simulator-feasibility domain

### §8.4 Round 3.1 / QUANT 2026-05-01 fidelity check

- ✅ T002 RETIRE FINAL accepted as binding context (predictor IP preserved per QUANT PRIMARY direction)
- ✅ Path A OFF user constraint (cost atlas frozen) honored verbatim — Path A in this DATA council refers to BACKFILL DATA path, NOT cost reduction R&D path
- ✅ §15.13.7 OOS one-shot honored (BURNED window 2025-07..2026-04 not re-litigated)
- ✅ ESC-013 R6 reusability invariant honored (engine-config / cost atlas / calendar identical across F2-equivalent re-runs; pre-2024 backfill would NEED engine-config v1.0.0-historical fork to honor)
- ✅ QUANT R1-R17 carried forward verbatim into context

### §8.5 Self-audit verdict

**Article IV PASSED.** No invention. All claims trace. All authority boundaries respected. Subjective preferences explicitly surfaced for council audit. Engine-semantic risk surface §5 explicitly flagged with proper [TO-VERIFY] tags. MANIFEST R11-R15 honored. Pessimistic-by-default discipline maintained.

---

## §9 Beckett cosign 2026-05-01 BRT — Data Council consumer ballot

```
Voter: Beckett (@backtester) — Backtester & Execution Simulator authority
Council: DATA-2026-05-01-dll-backfill
Topic: Pre-2024 DLL archival backfill viability for forward H_next-1 OOS hold-out (consumer perspective)
Constraint recap:
  - User canonical Path A OFF (cost atlas v1.1.0 FROZEN; this DATA council Path A = backfill data, not cost R&D)
  - QUANT 2026-05-01 PRIMARY = H_next-1 Conviction-Conditional Sizing on T002 predictor IP
  - QUANT R7 forward-time virgin hold-out 2026-05..2026-10 PRIMARY (Mira preferred)
  - QUANT R8 pre-2024 archival hold-out 2023-Q1..2024-Q3 FALLBACK conditional (Kira preferred)
  - Hold-out 2025-07..2026-04 BURNED on N8.2 (§15.13.7 one-shot)
  - Existing dataset trades-only; 2024-01..2026-03 coverage; 571 WDO / 269 WIN days

Consumer perspective on pre-2024 archival (§1):
  - Sample-size floor MET by margin (~6,000-19,000 H_next-1 trades over 6 quarters; well above 250 floor)
  - Wall-time projection ~50min per quarter; ~5-6.5h full backfill scan
  - Engine-config v1.1.0 applicability HIGH RISK across 2023-2024→2024-2026 boundary (§5)

Reusability across T-series (§2):
  - H_next-1 (PRIMARY): direct reuse if Sable virgin audits archival window
  - H_next-2 (auction print SECONDARY): direct reuse on different predictor IP family
  - H_next-3 (asymmetric exit DEFERRED): reuses H_next-1 predictor → BURNS archival if H_next-1 ran first
  - Sable contamination ledger discipline mandatory: per (strategy, window, touch_event) tracking

Run cost estimation (§3):
  - First H_next-1 OOS pre-2024 archival run: ~50-90min wall on N7-prime engine; ~3-4h total (in-sample + OOS tail)
  - Beckett-side absorption: ~3-4 sessions calendar-time once Dara/Nelo/Sable land prerequisites
  - Storage ~3 GB additional (Dara estimate; not Beckett authority)

Alternative timeline (§4):
  - Path B forward-only: +6mo wait; engine validity HIGH; Bonferroni CLEAN; confidence ★★★★★
  - Path A pre-2024 backfill: ~5-10 sessions Dara/Nelo + audits; engine validity ⚠️HIGH RISK §5; confidence ★★
  - Path C parallel both: complex but theoretically optimum if Mira designs composite kill criterion; confidence ★★★★

Microstructure regime concern (§5 — CRITICAL):
  - DMA2 latency profile [TO-VERIFY] for 2023 corretora routing
  - Cost atlas v1.1.0 reflects current B3 emolumentos; 2023 schedule different [TO-VERIFY]
  - RLP detection assumes post-RLP B3 microstructure; pre-2024 may be PRE-RLP era [TO-VERIFY Nelo]
  - Rollover calendar requires Nova pre-2024 extension
  - Mira authority on regime equivalence GATING per QUANT R8
  - If Path A/C pursued, engine-config v1.0.0-historical branch authoring required (5-10 sessions Nelo+Nova+Beckett)

Personal preference (pessimistic-by-default §6):
  - Subjective P(meaningful H_next-1 OOS verdict | Path B) ≈ 70%
  - Subjective P(meaningful | Path A standalone) ≈ 25%
  - Subjective P(meaningful | Path C composite) ≈ 55%
  - Bias FOR Path B (cleanest engine semantic story; pessimistic-by-default discipline)
  - Bias AGAINST Path A standalone (compounded gate failures; engine semantic mismatch risk)
  - Bias FOR Dara fresh-tape capture pipeline kickoff regardless of A/B/C outcome

Decision: APPROVE_PATH_B (forward-only, R7) — PRIMARY recommendation
  Conditional APPROVE_PATH_C only if all 6 conditions §7.2 cleared:
    (1) Mira composite kill criterion pre-registered
    (2) Mira regime equivalence concurrence (or two-atlas spec branch)
    (3) Sable virgin audit pass
    (4) Nelo confirms DLL retention pre-2024 schema parity
    (5) Nova confirms rollover calendar pre-2024 materialized
    (6) Beckett authors engine-config v1.0.0-historical [TO-VERIFY] branch
  REJECT_PATH_A standalone (no Path B fallback) — too much compound risk

Independent recommendations (§7.4):
  - Begin Dara fresh-tape capture pipeline NOW for forward OOS budget unlock 2027-Q1+
  - Sable contamination ledger discipline `docs/governance/data-contamination-ledger.yaml` instituted regardless of choice
  - Engine-config v1.2.0 perf round non-blocking parallel-track (per QUANT R17)
  - Mira H_next-1 spec authoring under fresh-spec-major-bump (clean MANIFEST R15 n_trials reset)

Authority boundary preservation:
  NO push (Article II → Gage exclusive)
  NO Dara custodial manifest pre-emption (capture pipeline / parquet schema)
  NO Nelo ProfitDLL semantic pre-emption (retention / RLP date)
  NO Mira regime-stationarity verdict pre-emption (gating dependency identified)
  NO Sable virgin-audit pre-emption (gating dependency identified)
  NO Pax forward-research scope pre-emption
  NO Riven custodial Bayesian / capital-ramp pre-emption
  NO new spec rules; no new statistical thresholds; no engine semantics modification for Path B

Round 3.1 / QUANT 2026-05-01 fidelity:
  T002 RETIRE FINAL accepted as binding (predictor IP preserved)
  Path A OFF user constraint (cost atlas frozen) honored verbatim
  §15.13.7 OOS one-shot honored (2025-07..2026-04 BURNED window not re-litigated)
  ESC-013 R6 reusability invariant honored
  QUANT R1-R17 carried forward verbatim

Article IV self-audit (§8): PASSED — no invention; all claims trace; subjective preferences surfaced; authority boundaries respected; engine-semantic risk surface §5 flagged with [TO-VERIFY]; MANIFEST R11-R15 honored.

R15 compliance: ballot under canonical docs/councils/COUNCIL-2026-05-01-DATA-dll-backfill-beckett-vote.md naming.

Cosign: Beckett @backtester 2026-05-01 BRT — Data Council consumer ballot.
```

---

— Beckett, reencenando o passado para informar o futuro com fidelidade pessimista 🎞️
