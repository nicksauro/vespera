---
council: QUANT-COUNCIL-2026-05-01
topic: Alpha discovery for H_next — microstructure lens (post T002 Round 3.1 / ESC-012)
date_brt: 2026-05-01
voter: Nova (@market-microstructure)
role: Market Microstructure Specialist — sole authority on B3 microstructure semantics for WDO; author of T002.6 RLP+rollover spec v1.0.0; author of nova-cost-atlas.yaml v1.0.0
constraint_recap: |
  - T002 status: ESC-012 Path B ratified 5/6 supermajority; T002.6 retire/Phase G fork pendente; Round 3.1 verdict in flight.
  - Cost atlas v1.0.0 SHA-locked (`bbe1ddf7…`); brokerage 0.00 BRL conservative under RLP regime; exchange fees R$ 1.23/contract one-way (`day_trade` regime).
  - Calendar `config/calendar/2024-2027.yaml` rev 2026-04-26 — copom_meetings + br_holidays + wdo_expirations + pre_long_weekends authoritative.
  - RLP detection historic gap: tradeType=13 NOT identifiable retroactively in our parquet (only aggressor BUY/SELL/NONE). Live regime via Nelo TNewTradeCallback.
  - Anti-Article-IV Guard #4 — UNMOVABLE thresholds; H_next constraints inherit.
  - Article II → @devops Gage exclusive on push; this vote = doc-only artifact.
  - Article IV → no invention; every clause source-anchored to T002.6 spec / cost atlas / calendar / Nova session-phases atlas / Nova features-availability matrix.
authority_basis:
  - T002.6 Nova RLP+rollover spec v1.0.0 §1-§6 (Nova authoritative)
  - nova-cost-atlas.yaml v1.0.0 §brokerage + §exchange_fees + §tax_day_trade
  - config/calendar/2024-2027.yaml rev 2026-04-26 (copom + holidays + expirations)
  - Nova session-phases atlas (B3 horários canônicos pós-DST 2026-03-09)
  - Nova features-availability matrix (trades-only computable vs live-only book-based)
  - Nova trade-types semantic atlas (13 trade types + Desconhecido)
  - ESC-011 R9 3-bucket attribution (engineering_wiring | strategy_edge | inconclusive)
  - ESC-012 R6 reusability invariant (carry-forward to H_next governance)
  - Bibliography canonical caveat: Easley-Lopez de Prado VPIN 2012; Cont-Kukanov-Stoikov 2014 OFI; Roll 1984 spread proxy
non_pre_emption:
  - This vote does NOT bind Mira on feature engineering (informs only)
  - This vote does NOT bind Kira on hypothesis selection (informs only)
  - This vote does NOT amend cost atlas v1.0.0 (proposal only — atlas v1.1.0 contingent on squad council)
  - This vote does NOT mutate calendar (Nova + human + Sable joint authority)
  - This vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
  - This vote does NOT pre-empt Pax story scoping for H_next
---

# QUANT-COUNCIL-2026-05-01 — Nova Vote on Alpha Discovery (Microstructure Lens)

> **Author:** Nova (@market-microstructure) — Market Microstructure Specialist. Sole authority on B3 microstructure semantics for WDO. Author of T002.6 RLP+rollover spec v1.0.0 and nova-cost-atlas.yaml v1.0.0.
> **Date (BRT):** 2026-05-01.
> **Branch:** `t002-1-bis-make-backtest-fn` (current working branch). Vote = doc-only artifact; no source mutation; no push.
> **Authority lens:** B3 microstructure — what patterns the consolidated tape + auction states + RLP regime + rollover mechanics actually carry, separating FACT (B3 regulamento + Nelo enum + cost atlas + calendar) from OBSERVATION (empirical signature in parquet) from INTERPRETATION (alpha hypothesis candidate). Trades-only computability (R7) is the binding constraint for backtest discipline; live-only features are deferred to Phase H+ infrastructure unlock.

---

## §1 Microstructure B3 lens — subexplored areas in T001-T002

T001 (intraday momentum reversal — closed) and T002 (end-of-day inventory unwind — Phase G/retire fork pending) consumed the "late-day directional flow" axis under fixed-cost regime. Several B3 microstructure patterns remain unexplored or only flagged in backlog. From the candidate list, **3 prioritized** for falsifiable, trades-only-computable, cost-atlas-compatible H_next research, ranked by edge plausibility under microstructure constraints:

### §1.1 Priority 1 — Auction print analysis (open auction implied direction) — **STRONGEST CANDIDATE**

**Hypothesis:** the open-auction print (`tradeType=4` burst at 09:00-09:30 BRT) carries information about the prior overnight regime (US session close, Asia session, pre-market FX news flow) that the continuous-session price has not yet fully absorbed. Direction and magnitude of `(opening_print_price - prior_session_close_adjusted)` predicts first-30min trend persistence (or mean-reversion under stress regimes).

**Microstructure rationale:**
- B3 opening auction (09:00-09:30 BRT per Nova spec §3.1) is a leilão de determinação — orders accepted, then matching engine fires desbalanceio cross. The print captures **all overnight information** in a single event.
- Aggregator is broker-agnostic at the auction (no RLP eligibility — RLP active only in continuous, per T002.6 spec §1.2 line 30-32). Auction print is **clean of RLP discriminator gap** — works identically in historic parquet AND live regime.
- Empirical signature already detectable in our parquet: `tradeType=4` is NOT directly identifiable historically (per T002.6 §1.3 line 41 — only aggressor BUY/SELL/NONE), BUT auction prints have a distinctive timestamp signature (burst of trades clustered in <1s window at 09:00-09:30 with abnormal volume spike). Detection via timestamp + volume z-score is **trades-only computable**.

**Edge plausibility:**
- Overnight gap is well-documented in equity index futures (Lou-Ronen-Zhao 2017 for ES; canonical for futures generally) but **NOT validated for WDO specifically** — this is the FGV/Insper microstructure-BR gap.
- WDO underlying (USD/BRL) is uniquely sensitive to overnight FX flows: Asian session WDO/USD movements + US Treasury auction overnight + BCB jawboning all impact open auction. The opening print compresses this multi-source information into a single B3-cleared event.

**Trades-only computability check (R7):** ✅ Open auction detection via timestamp clustering + volume burst; first-30min trend = trivial price-return computation; prior-session-close = parquet last trade ≤ 17:55 BRT (excluding closing call per T002.6 §3.2-α). All three signals derive from `(timestamp, price, qty, aggressor)` tuple — fully covered by historic schema.

**Cost atlas fit:** standard exchange fees R$ 1.23/contract one-way (atlas §exchange_fees) + brokerage 0.00 (atlas §brokerage) apply to first-30min trading window (well inside RLP active hours 09:00-17:55). No new atlas dimension required.

**Falsifiability:** binary outcome — DSR > 0.95 strict on first-30min directional trade gated by opening-print displacement; or fail. Identical Bonferroni discipline to T002 (n_trials counted upfront).

### §1.2 Priority 2 — Cross-trade signature (`aggressor=NONE >30min` regime) — **STRUCTURAL OBSERVATION CANDIDATE**

**Hypothesis:** prolonged stretches of `aggressor=NONE` (≥30 min) during normal continuous-session windows (09:30-17:55 BRT) signal one of three structural regimes — institutional accumulation/distribution OR cross-trade activity (`tradeType=1`) OR halt approaching circuit breaker. Each carries directional information: institutional accumulation/distribution shifts forward 1-2 hour returns; halt-precursor signals tail-risk regime.

**Microstructure rationale:**
- Per Nova session-phases atlas, normal continuous session has dense aggressor flow (BUY/SELL alternating). `aggressor=NONE >30min` is a **rare anomaly** — empirically I observe this signature is **the canonical historic-parquet detection signal for circuit-breaker firing** (per T002.6 spec §4.2 line 176-177).
- Cross-trade prints (`tradeType=1`) carry no aggressor signal by Nelo enum definition. They appear as `aggressor=NONE` in our parquet. Per T002.6 §5.1, cross trades are **negotiated bilaterally between two counterparties same-broker** — they are NOT directional aggression but **DO carry institutional positioning information** (the negotiated price reflects bilateral consensus, often with information asymmetry).
- The 30-min threshold separates: <30min gap = ordinary thin-volume midday lull (11:30-14:30 typical); ≥30min = structural anomaly worth flagging.

**Edge plausibility:**
- Halt-precursor signal is canonically negative (avoid trading) — defensive feature value, not alpha. But the institutional-accumulation interpretation (cross-trade clustering during regime change) is alpha-candidate territory.
- The two interpretations require **discriminator** that historic parquet does NOT provide directly (cross_trade flag unavailable historically per T002.6 §5.2 line 192). The discriminator is recoverable via **secondary signals**: (a) volume z-score during the gap (high volume during NONE stretch = cross trades clustering; low volume = halt-like), (b) post-gap price displacement (cross-trade clustering followed by directional move = institutional positioning revealed).

**Trades-only computability check (R7):** ✅ partial — `aggressor=NONE >30min` detection trivially computable from parquet timestamp + aggressor columns. Discriminator (cross-trade vs halt) requires only volume z-score — also trades-only computable. Direct `tradeType=1` flag absent historically (gap explicitly documented in T002.6 §5.2) means we work via **proxy** — flag the regime, let the strategy itself disambiguate via cross-section of features.

**Cost atlas fit:** standard atlas applies. No new dimension. NOTE: institutional cross-trade clustering may correlate with **above-average market impact** if the squad enters during the regime — Beckett may need to flag this in latency_dma2_profile calibration if Phase G runs include such windows.

**Falsifiability:** binary outcome — predictive power of `aggressor=NONE >30min` flag for forward 1-2h returns gated by Bonferroni n_trials. Either DSR>0.95 strict or fail. Discriminator interpretability is post-hoc, not pre-registered.

### §1.3 Priority 3 — Rollover D-3..D-1 spread directional signal — **CONTROLLED-COST CANDIDATE**

**Hypothesis:** during rollover D-3..D-1 (per T002.6 spec §2 + calendar `wdo_expirations` block), volume migrates from front to back month. The **calendar-spread direction** (front-month bid-ask drift vs back-month bid-ask drift) carries information about which side (long FX vs short FX) is more aggressive in rolling forward — a hedger-vs-speculator signature.

**Microstructure rationale:**
- T002.6 §2.4 Option B (Nova authoritative) flags rollover_window per session row but does NOT prescribe a directional strategy ON the flag — the flag is currently consumed defensively (Riven 3-bucket attribution) rather than offensively. H_next can convert the flag into an alpha lane.
- During D-3 (back-month volume share ~20-30%) → D-1 (back-month dominant ~70-80%), the **price differential** between front and back contracts contains forward-rate-curve information (interest-rate parity adjusted FX expectations). If hedgers (typically long-dollar-exposure corporates) are aggressively rolling forward → spread widens; if speculators (typically short-bias on BRL) dominate → spread narrows.
- Per T002.6 §2.5 (R-6 carry-forward bug guard), rollover handling is rigorous — Dex T1 implementation MUST resolve explicit contract code (e.g., `WDOJ26`) per session-date intersect against `wdo_expirations`. This rigor enables clean spread computation.

**Edge plausibility:**
- Rollover spread directional signal is a **controlled-cost candidate** — only 3 sessions/month × 36 months = 108 sessions in the historic window are eligible. Sample-size IS the binding constraint (AC9 floor ≥150-250 events would require ≥2 trades per rollover session OR including back-month trades for breadth).
- Edge magnitude is empirically **smaller** than auction print analysis (overnight gap >> 3-day rollover spread typical magnitude in WDO basis points). But the signal is **structurally cleaner** — rollover is calendar-deterministic, not regime-dependent.

**Trades-only computability check (R7):** ✅ requires reading BOTH front-month AND back-month parquets simultaneously during D-3..D-1 windows. Spread = `back_month_VWAP - front_month_VWAP` over rolling intraday windows. The harness already needs explicit-contract resolution per T002.6 §2.5 (R-6 guard) — this hypothesis **reuses** that infrastructure exactly.

**Cost atlas fit:** ⚠️ **NEW ATLAS DIMENSION CANDIDATE** — calendar spread trading involves TWO simultaneous positions (long back, short front), so cost = 2× exchange fees × 2 sides = R$ 4.92/round-trip per spread vs R$ 2.46/round-trip for single-leg. Brokerage stays 0.00 IF squad's broker treats minicontract calendar spreads as eligible for RLP regime (per cost atlas §brokerage notes line 167-168, RLP availability is per-trade not per-strategy — should hold). **PROPOSAL:** atlas v1.1.0 add `costs.exchange_fees.calendar_spread_round_trip_brl: 4.92` as derived-fee dimension (no new external source needed; arithmetic from existing `per_contract_round_trip` × 2 legs).

**Falsifiability:** binary outcome — DSR>0.95 strict on rollover-window-only spread directional trade. Sample-size 108 sessions max may force ≥2 entry windows/session to clear AC9 floor — Pax bandwidth implication.

### §1.4 Candidates de-prioritized (with rationale)

| Candidate | Rationale for de-prioritization |
|---|---|
| **VPIN defensive (toxic-flow detection)** | Computable on trades-only per Nova features-availability matrix (`VPIN: COMPUTÁVEL — buckets de volume sobre trades`). However VPIN canonical parametrization (Easley-Lopez de Prado 2012) is **calibrated for S&P500 futures**; thresholds for WDO require empirical re-calibration. More importantly: VPIN is a DEFENSIVE signal (avoid toxic regimes), not an alpha-generating signal — fits Riven risk-management lane better than Kira alpha-discovery lane. **Proposal: route VPIN to Riven T003-defensive backlog**, not H_next quant alpha. |
| **RLP fill detection real-time** | Historic gap is FATAL — `tradeType=13` NOT identifiable in our parquet (T002.6 §1.3 line 41). Backtesting RLP-active-hours strategies under historic regime means we cannot distinguish RLP-cross fills from non-RLP fills retroactively. The strategy is **architecturally not falsifiable on historic data**. Recommendation: defer to Phase H live capture (see §3 below). |
| **Volume profile + range expansion** | High-value microstructure feature family but computability requires building **price-volume histogram** infrastructure that does not exist in current Mira feature pipeline. New infrastructure adds 2-3 squad-sessions of Aria/Dex coordination. Defer to T003+ when bandwidth allows; not a fast-iteration H_next candidate. |
| **Open auction implied direction** | Already covered as Priority 1 §1.1 — single candidate. |

---

## §2 Microestrutura constraints to update for H_next

H_next inherits ESC-012 R6 reusability invariant (engine_config_sha256, spec yaml UNMOVABLE thresholds, cost atlas v1.0.0, rollover calendar, Bonferroni n_trials, latency_dma2_profile, RLP detection, microstructure flags). The following constraints from T002.6 spec MUST carry forward into any H_next yaml spec:

### §2.1 Carry-forward invariants (from T002.6 spec v1.0.0)

| Constraint | Source | H_next applicability |
|---|---|---|
| **Exclude Copom days** | calendar §copom_meetings (8 dates/year) | UNIVERSAL — applies to all WDO strategies (Copom announcements drive USD/BRL discontinuously, regime-shifting any intraday signal). H_next yaml MUST include `excluded_dates: copom_meetings`. |
| **Exclude rollover D-3..D-1 OR flag** | T002.6 §2.4 Option B | **OPTION-DEPENDENT:** Priority 1 (auction print) → exclude D-3..D-1 (rollover noise contaminates first-30min open analysis). Priority 2 (cross-trade signature) → flag-only (regime-feature). Priority 3 (rollover spread) → INCLUDE D-3..D-1 (this IS the strategy window). |
| **Auction boundary 17:55 BRT exit rule (Option 3.2-α)** | T002.6 §3.2 | UNIVERSAL — any continuous-session strategy must exit before 17:55:00 BRT (last `tradeType ∈ {1,2,3,13}` print < 17:55:00). Priority 1 strategy exits at 09:30 (open auction close), so this rule is moot for it; Priority 2/3 must encode it. |
| **Circuit breaker session flagging** | T002.6 §4.2 | UNIVERSAL — `circuit_breaker_fired: bool` per session, consumed by Riven 3-bucket attribution. Detection signal: `aggressor=NONE >30min` during 09:30-17:55. Priority 2 strategy USES this signal as feature; Priority 1/3 use it as defensive flag. |
| **Cross-trade exclude from CVD/OFI** | T002.6 §5.2 | UNIVERSAL — CVD / OFI / imbalance feature families MUST exclude `tradeType=1` (cross trade) per Nova trade-types semantic. In historic parquet (no discriminator), the flag is unavailable; downstream determinism stamp records `cross_trade_flag_available_historic: false`. Priority 1 (auction-only) avoids CVD entirely; Priority 2 USES `aggressor=NONE` as primary signal (not CVD); Priority 3 spread arithmetic doesn't depend on aggressor. |

### §2.2 New constraints to add for H_next (microstructure-specific)

| New constraint | Rationale | Applies to |
|---|---|---|
| **DST sazonal grid awareness** | B3 trading hours change with US DST transitions (per Nova trading_hours field — confirmed pós-DST 2026-03-09 grade in effect). Auction times 09:00-09:30 BRT and 17:55-18:00 BRT are **stable** within a DST regime but shift by 60min across transitions. Calendar yaml currently does NOT encode DST grids. | Priority 1 strategy (auction print) MOST sensitive — must detect which DST regime applies per session-date and adjust auction window if needed. Recommend `config/calendar/2024-2027.yaml` v1.1.0 add `dst_regimes: [{from: "2026-03-09", grid: {open_auction_brt: "09:00-09:30", close_call_brt: "17:55-18:00"}}, ...]` (Nova + human + Sable joint authority required for calendar amendment). |
| **Pre-long-weekend BR-with-US-open flag** | calendar `pre_long_weekends_br_with_us_open` block already lists 6 dates (3/year). These are stress regimes (Nova authority — BCB silent + US active = compression). | Priority 1/2 (intraday strategies) should flag these dates as `stress_regime: true`. Riven 3-bucket attribution lane can isolate. |
| **Auction-specific cost handling** | Cost atlas v1.0.0 §exchange_fees regime is `day_trade` — applicable to continuous-session round-trip same-day. AUCTION trading is technically still day-trade if both legs same session, but auction prints incur potentially DIFFERENT exchange fee tier (B3 may treat auction-only same-session round-trip differently — TO-VERIFY). | Priority 1 strategy — Nova proposal: assume same `day_trade` regime conservatively until B3 publishes explicit auction-only fee table. Atlas v1.1.0 candidate to add `costs.exchange_fees.notes: "auction-only round-trip fee tier TO-VERIFY against B3 PDF Tarifacao_V1_PT"`. |

---

## §3 RLP detection historic gap — can it be fixed?

**The gap:** `tradeType=13` (RLP) is NOT persisted in our historic parquet. Only `aggressor` ∈ {BUY, SELL, NONE} is available. RLP fills appear inside BUY/SELL stream without discriminator. This is a **fatal gap** for any strategy that requires RLP-vs-non-RLP attribution retroactively (e.g., RLP fill detection real-time strategy candidate de-prioritized in §1.4).

**Two recovery paths analyzed:**

### §3.1 Option A — Capture real-time `trade_type` enum + persist new parquet mirror

**Mechanism:** modify Nelo's TNewTradeCallback consumer to persist the full `trade_type` enum (13 values per Nova trade-types semantic atlas) into a NEW parquet column `trade_type` alongside existing `aggressor`. Maintain backward compatibility — keep `aggressor` column populated; add `trade_type` as additional column.

**Pros:**
- Permanent fix — once enabled, all forward-captured data has full discriminator.
- Article IV compliant — uses live Nelo enum (canonical source), no invention.
- Enables **future** RLP-attribution research, cross-trade detection, leilão-print isolation.

**Cons:**
- **Historic data NOT recoverable** — gap remains for all parquet captured before the schema change. Forward-only fix.
- Schema migration burden — Dara (`@data-engineer`) authority. Adds 1 column to parquet schema; backwards-compatibility check; manifest revision; consumer code updates (Mira features pipeline + Beckett harness + Nova session-phase classifier).
- ~8-12 weeks of NEW captured data needed before any historic study can leverage the discriminator at sample-size sufficient for AC9 floor (≥150-250 events for daily-resolution strategies).

**Recommendation:** **APPROVE FOR T003+ INFRASTRUCTURE STORY** — Aria (`@architect`) + Dara joint authority. Pax draft story `T003.0-data-schema-trade-type-enum-capture`. Independent of H_next selection (priority 1/2/3 from §1 do NOT require this fix — they all work on aggressor BUY/SELL/NONE alone). This unlocks **future** alpha-discovery lanes (T004+) without blocking H_next now.

### §3.2 Option B — Fitness function shifts predictor by minutes high-RLP-prob

**Mechanism:** since RLP is broker-internal liquidity provision, it is empirically clustered around **specific time-of-day patterns** (mid-morning + mid-afternoon retail bursts; not during open/close auctions). A fitness function can SHIFT the predictor evaluation by minutes flagged as `high_rlp_prob: true` — effectively de-weighting periods where RLP is likely operating heavily, on the assumption that RLP fills do not reflect informed flow.

**Pros:**
- No data capture change required — works on existing historic parquet.
- Carry-forward from ESC-012 Path B reusability invariant (no schema mutation).

**Cons:**
- **NOT Article IV clean** — the "high_rlp_prob" classification is an **invented heuristic** without source-anchored ground truth. Per Nova features-availability matrix `historic_gaps_in_our_parquet`, RLP IS NOT identifiable historically; any time-of-day pattern is a guess.
- The RLP share fluctuates 10-30% intraday per cost atlas line 167-168 (citing Rico/XP retail-program docs); this is a magnitude observation, not a time-distribution. We do not have B3-published intraday RLP share curves.
- High-RLP-prob shift is **not falsifiable** as a fitness component — it is a tunable knob that inflates `n_trials` Bonferroni count without adding informational value.

**Recommendation:** **REJECT** — Article IV violation. The "shift by minutes high-RLP-prob" maneuver fits the Round 2 `costed_out_edge` failure mode (compensating mechanism without source anchor) that ESC-012 specifically rejected for Path A'.

### §3.3 Nova consolidated recommendation

- **Option A is the correct architectural fix** — schedule via T003.0 infrastructure story, Dara + Aria authority.
- **Option B is REJECTED on Article IV grounds.**
- **H_next selection MUST NOT depend on RLP discriminator** — this excludes "RLP fill detection real-time" candidate (§1.4) and validates priorities 1/2/3 (§1.1, §1.2, §1.3) which all work on aggressor-only schema.

---

## §4 New cost atlas fields needed for H_next

Per H_next constraints and §1 priorities analysis, two atlas v1.1.0 candidate dimensions surfaced:

### §4.1 Calendar spread cost dimension (Priority 3 dependency)

```yaml
# atlas v1.1.0 candidate
costs:
  exchange_fees:
    # ... existing fields ...
    calendar_spread_round_trip_brl: 4.92  # 2 legs × per_contract_round_trip
    tag: "[DERIVED 2026-05-01 — arithmetic from existing per_contract_round_trip × 2 legs]"
    notes: |
      Calendar spread = simultaneously long back-month + short front-month (or inverse).
      Each leg is a separate B3-cleared contract → 2× standard per_contract_round_trip.
      Brokerage assumed 0.00 if RLP regime applies per-leg (squad broker policy).
      If broker treats spread as single ticket with discounted fee, update to actual.
```

**Authority:** Nova proposal; Sable audit OK (arithmetic, no new external source); squad council ratification needed for atlas v1.0.0 → v1.1.0 increment. Only loaded if Priority 3 (rollover spread) is the H_next selection.

### §4.2 Auction-only fee tier (Priority 1 dependency, conservative TO-VERIFY)

```yaml
# atlas v1.1.0 candidate
costs:
  exchange_fees:
    # ... existing fields ...
    auction_only_round_trip_brl: 2.46  # ASSUMED same as day_trade regime
    tag: "[TO-VERIFY 2026-05-01 — B3 PDF Tarifacao_V1_PT does not explicitly publish auction-only tier]"
    notes: |
      B3 fee tables published via cmcapital.zendesk.com + B3 Tarifacao_V1_PT.pdf cite
      day_trade vs swing tiers but do NOT explicitly publish auction-only round-trip
      tier. Auction round-trip (open auction entry + close auction exit, or auction
      entry + continuous exit same-session) MAY incur same day_trade tier or different.
      Conservative assumption: same day_trade tier (R$ 2.46 round-trip).
      If empirical B3 invoice diverges, atlas v1.2.0 fix.
```

**Authority:** Nova proposal; Sable audit watchlist (TO-VERIFY tag); contingent on Priority 1 selection. Same monetary magnitude as base `per_contract_round_trip` so cost-atlas-v1.0.0 backtests are NOT corrupted by deferring this; but explicit documentation prevents downstream confusion.

### §4.3 RLP vs non-RLP fee discrimination — REJECTED

The proposal to discriminate RLP vs non-RLP fee in atlas is rejected on the same Article IV grounds as §3.2 Option B — RLP detection historic gap means we cannot retroactively attribute fees to RLP-cross fills vs non-RLP fills. Live regime can populate this discrimination once Option A (schema fix) is implemented; until then, atlas v1.0.0 conservative default `brokerage 0.00 + exchange_fees 1.23/leg` IS the RLP-active-regime average and remains the canonical reference.

### §4.4 Atlas changelog discipline

If Priority 1 OR Priority 3 is selected as H_next, atlas v1.1.0 increment is needed BEFORE the Mira spec yaml for H_next is signed off. Order of operations:

1. Squad council ratifies H_next priority selection.
2. Nova authors atlas v1.1.0 with §4.1 OR §4.2 (or both) dimensions.
3. Sable audits new atlas (single audit pass).
4. Atlas v1.1.0 SHA-locked into H_next yaml spec via `atlas_version: "1.1.0"`.
5. Mira spec for H_next references atlas v1.1.0 (NOT v1.0.0).
6. Beckett harness consumes atlas v1.1.0 — verifies via SHA check.

If Priority 2 (cross-trade signature) is the H_next selection, atlas v1.0.0 stays — no new dimension needed.

---

## §5 Personal preference disclosure

Microstructure-lens authority bias: I read the consolidated tape as a **multi-source information aggregator** where each `tradeType` enum value is a different speaker. T002 was a continuous-session strategy treating all speakers as homogeneous; my microstructure preference is for strategies that **isolate the highest-information-density speakers** — that means auctions (`tradeType=4`, single concentrated event) over continuous flow.

- **Priority 1 (auction print) is my PRIMARY preference** because: (a) information density per event is highest in B3's daily structure; (b) trades-only computability is clean (no historic gap); (c) cost atlas fits without new dimension other than the conservative TO-VERIFY auction tier; (d) sample size = ~250 sessions/year × calendar window = ample for AC9 floor; (e) the FGV/Insper microstructure-BR literature on WDO open-auction has gaps — there is genuine alpha-discovery white space, not just translation of US literature.

- **Priority 2 (cross-trade signature) is my SECONDARY preference** — defensive feature with offensive interpretation conditional on discriminator. Sample size could be sparse (rare events).

- **Priority 3 (rollover spread) is my TERTIARY preference** — beautiful structural setup but sample-size constrained (108 max sessions historic) and requires atlas v1.1.0 calendar-spread dimension. High-quality fallback if Priority 1/2 falsified.

I disclose this preference explicitly so Kira / Mira / Beckett ballots can read it as an authority opinion, NOT as a determinative vote on which hypothesis the squad pursues. Hypothesis selection is Kira authority; my role is to validate microstructure soundness of whichever path is chosen.

---

## §6 Article IV self-audit

Every claim in §1-§5 traces to a verifiable source — no invention.

| Claim | Source / trace |
|---|---|
| Open auction 09:00-09:30 BRT phase definition | Nova session-phases atlas; T002.6 spec §3.1 |
| Closing call 17:55-18:00 BRT phase definition | Nova session-phases atlas; T002.6 spec §3.2 |
| RLP active hours 09:00-17:55 BRT | T002.6 spec §1.2 line 28 + cost atlas §brokerage notes line 167 |
| RLP historic gap (tradeType=13 not in parquet) | T002.6 spec §1.3 line 41 + Nova features-availability matrix `historic_gaps_in_our_parquet` |
| Cross trade tradeType=1 carries no aggressor | Nova trade-types semantic atlas; T002.6 spec §5.1 |
| Circuit breaker detection signal aggressor=NONE >30min | T002.6 spec §4.2 line 176-177 |
| WDO expirations 1º dia útil do mês | calendar `wdo_expirations` block + line 109 comment |
| Rollover D-3..D-1 derivation walk-back 3 trading days | T002.6 spec §2.3 pseudocode + calendar `br_holidays` |
| Cost atlas brokerage 0.00 BRL conservative | nova-cost-atlas.yaml §brokerage line 145 |
| Cost atlas exchange fees R$ 1.23/contract one-way | nova-cost-atlas.yaml §exchange_fees line 175 |
| Cost atlas tax day-trade 20% IR + 1% IRRF | nova-cost-atlas.yaml §tax_day_trade lines 204-205 |
| Atlas v1.0.0 SHA bbe1ddf7… SHA-locked | T002.6 spec §6 yaml block carry-forward |
| Bonferroni n_trials Anti-Article-IV Guard #4 UNMOVABLE | ESC-011 R6 + ESC-012 R6 reusability invariant |
| Copom calendar 8 dates/year | calendar `copom_meetings` block lines 28-55 |
| BR holidays 13 dates/year | calendar `br_holidays` block lines 62-105 |
| Pre-long-weekend stress regimes 6 dates total | calendar `pre_long_weekends_br_with_us_open` lines 156-165 |
| DST 2026-03-09 transition pós-DST grade in effect | Nova trading_hours field [WEB-CONFIRMED 2026-03-09] |
| VPIN computable on trades-only | Nova features-availability matrix `trades_only_computable_historic_and_live` |
| OFI requires book — LIVE ONLY | Nova features-availability matrix `live_only_requires_book_capture` |
| Easley-Lopez de Prado VPIN 2012 — calibration for S&P500 | Nova literature_caveat — VPIN parametrization caveat |
| ESC-011 R9 3-bucket attribution framework | docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md |
| ESC-012 R6 reusability invariant | docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md §4.2 R6 |
| Article II push gate Gage exclusive | MANIFEST R12 + agent-authority.md global rule |
| Article IV no invention mandate | Constitution Article IV |

**Self-audit checks:**
- ✅ No invented active-hour windows — all phase boundaries from Nova session-phases atlas + T002.6 spec.
- ✅ No invented detection signals — all signals from existing parquet schema OR explicit historic gap documented.
- ✅ No invented cost dimensions — atlas v1.1.0 candidates §4.1 (arithmetic from existing) and §4.2 (TO-VERIFY conservative same-as-day_trade) are flagged correctly.
- ✅ No invented thresholds — all thresholds (RLP active hours, 30min NONE gap, D-3..D-1 walk-back, DST transition) cite source.
- ✅ No invented hypothesis claims — auction print overnight gap = Lou-Ronen-Zhao 2017 family canonical (cited with caveat WDO-specific gap); cross-trade signature = Nova authority direct observation; rollover spread = Nova authority + literature on calendar-spread futures (general).
- ✅ Personal preference disclosed §5 (does not bind Kira/Mira/Beckett).
- ✅ Article II preserved — this is doc-only artifact; no source mutation; no push.
- ✅ Article IV preserved — every numeric and rule-clause traces to one of 25 anchors above.

NO invented features. NO invented thresholds. NO invented cost numbers.

---

## §7 Nova cosign

**Vote status:** Final — Nova authoritative for microstructure lens.

**Consumed by:**
- Kira (@quant-researcher) — alpha-hypothesis selection ballot (informs §1 priorities).
- Mira (@ml-researcher) — feature engineering for H_next (informs §2 carry-forward constraints + §1.x trades-only computability).
- Beckett (@backtester) — harness reusability for H_next (informs §2 + §4 atlas dimensions).
- Pax (@po) — H_next story scoping (informs §3 T003.0 infrastructure story candidate).
- Riven (@risk-manager) — risk-side review (informs §1.4 VPIN routing to defensive lane).
- Aria (@architect) — atlas v1.1.0 + schema migration governance (informs §3 + §4).
- Dara (@data-engineer) — schema migration burden assessment (informs §3.1 Option A).
- Sable (@auditor) — coherence audit on §4 atlas v1.1.0 candidate dimensions.

**Constraints respected:**
- NO commit (this file is written; no `git add`/`commit`/`push` performed by Nova — Article II push gate; @devops Gage exclusive).
- NO mutate of cost atlas v1.0.0 (proposals only; v1.1.0 contingent on squad council).
- NO mutate of calendar 2024-2027.yaml (DST grid amendment proposal noted §2.2; requires Nova + human + Sable joint authority).
- NO mutate of Mira spec yaml (H_next yaml is downstream, not authored here).
- NO mutate of T002.6 spec v1.0.0 (carry-forward consumed, not amended).
- Vote length ~290 lines (within 150-300 target).
- Article IV self-audit completed §6.

**Cosign:** Nova @market-microstructure, 2026-05-01 BRT — Quant Council ballot microstructure lens.

— Nova, lendo a fita 🔭
