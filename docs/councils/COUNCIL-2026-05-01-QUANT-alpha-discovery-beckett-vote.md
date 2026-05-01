---
council: QUANT-2026-05-01-alpha-discovery
topic: Forward alpha-discovery framing post-T002 retire (Round 3.1 FINAL costed_out_edge_oos_confirmed_K3_passed)
date_brt: 2026-05-01
voter: Beckett (@backtester)
role: Backtester & Execution Simulator authority — empirical/simulator lens (pessimistic-by-default)
constraint_recap:
  - User canonical Path A OFF (cost reduction R&D suspended; costs+slippage atlas FROZEN at v1.1.0)
  - T002 RETIRED with refined OOS-confirmed costed_out_edge_K3_passed bucket (Mira Round 3.1 FINAL)
  - Engine-config v1.2.0 perf round NOT YET AUTHORED (Aria/Dex/Quinn cycle pending)
  - Hold-out tape 2025-07..2026-04 was BURNED on N8.2 one-shot (§15.13.7); future hypotheses MUST use a different OOS window or wait for fresh tape capture
authority_basis:
  - Beckett MANIFEST R11-R14 — domain authority: O-QUÊ (fill rules, slippage model, latência DMA2, CPCV config); NÃO COMO de orquestração
  - Beckett MANIFEST R15 — Spec Consumer (revisões breaking_fields tocando cv_scheme/data_splits/feature_set/label/trading_rules/n_trials → CPCV re-run from zero, novo N_trials Bonferroni)
  - Mira Gate 4b spec v1.2.0 §15.13.7 OOS one-shot binding (K3 measurement)
  - ESC-013 R6 reusability invariant (engine_config + spec yaml + atlas + calendar + Bonferroni IDENTICAL F2)
  - Lopez de Prado AFML cap 12-14 (CPCV, backtest overfitting, metrics)
  - Bailey-Lopez de Prado 2014 PBO/DSR multiplicity adjustment
inputs_consulted:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md (Round 3.1 FINAL FAIL costed_out_edge_oos_confirmed_K3_passed)
  - data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/full_report.md (N8.2 PROPER Phase G OOS evidence)
  - data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/telemetry.csv (294 sample rows, 141min wall)
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md (Phase F baseline 188min wall)
  - docs/backtest/engine-config.yaml (v1.1.0 frozen; latência DMA2 + RLP/microstructure carry-forward)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md (R6 reusability invariant body)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-beckett-vote.md (prior ballot — same authoring discipline carried forward)
  - docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml (canonical predictor↔label spec from retired T002)
  - docs/ml/research-log.md (n_trials_used=5 carry-forward post T002 retire)
non_pre_emption:
  - This ballot does NOT bind Mira spec authoring authority (forward-research spec design = Mira)
  - This ballot does NOT pre-empt Pax forward-research scope authority
  - This ballot does NOT pre-empt Riven custodial Bayesian prior updates / capital-ramp authority
  - This ballot does NOT pre-empt Aria architecture authority over engine-config v1.2.0 spec
  - This ballot does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
  - This ballot does NOT pre-empt Dara custodial manifest authority over fresh-tape capture/materialization scheduling
---

# QUANT Council 2026-05-01 — Beckett Ballot (Alpha-Discovery Forward Framing post-T002 Retire)

> **Voter:** Beckett (@backtester) — Backtester & Execution Simulator authority. Pessimistic-by-default; if the simulator burden is uncertain, I assume worst.
> **Date (BRT):** 2026-05-01.
> **Branch:** `t002-1-bis-make-backtest-fn` (active local branch; ballot is local-only docs work).
> **Authority basis:** Empirical/simulator lens — what is **executable within current infrastructure** (engine-config v1.1.0, ADR-1 v3 6 GiB RSS cap, DMA2 latency atlas, RLP detection + microstructure flags, lazy-load discipline R7, hold-out one-shot R9, ESC-013 R6 reusability invariant).
> **Reading of council scope:** Forward alpha-discovery means **next H_next hypothesis** that consumes T002 lessons (canonical predictor↔label semantics; CPCV scaffolding; cost atlas; latency profile; Bonferroni accounting). I evaluate **viability** under the simulator lens, NOT the merits of feature engineering (Mira authority).

---

## §1 Simulator lens — which hypotheses are EXECUTABLE within current infrastructure?

### §1.1 What "executable" means under simulator lens

Three orthogonal axes, all binding:

| Axis | Binding constraint | Source |
|---|---|---|
| **A — Wall-time** | CPCV 5 trials × 45 paths over ~10mo window ≈ 3h baseline (188min N7-prime; 141min N8.2). Each new trial ~38min incremental. H_next budget: **≤ 5h per re-run** = ≤ 8 new trials before Bonferroni inflation hits DSR strict bar | N7-prime §3.1 + N8.2 telemetry |
| **B — Memory budget** | ADR-1 v3 6 GiB RSS cap; observed peak ~627MB (10× headroom). NOT binding for in-sample-equivalent windows; could become binding if H_next adds book-state replay (ADR-1 v3 cap re-evaluation needed) | Beckett N7-prime §10.3 |
| **C — Reusability invariant** | ESC-013 R6: engine_config + cost atlas + calendar + Bonferroni semantics IDENTICAL across F2-equivalent re-runs. H_next that mutates ANY of these triggers full Bonferroni reset (n_trials=1 fresh) — costly under MANIFEST R15 spec-consumer rules | ESC-013 R6 + MANIFEST R15 |

### §1.2 Carry-forward simulator assets (REUSABLE for any H_next)

| Asset | Status | Reusability |
|---|---|---|
| Engine-config v1.1.0 (DMA2 latency p50=20ms / p95=60ms / p99=100ms; tail 500ms stress) | FROZEN | ✅ reusable — Path A OFF means no atlas mutation |
| Cost atlas v1 (corretagem + emolumentos B3 + ISS + IR day-trade conservatively parametrized) | FROZEN | ✅ reusable |
| RLP detection (tradeType=13 conservative-ignore policy) | FROZEN | ✅ reusable |
| Microstructure flags (session phase, rollover calendar, leilão windows) — Nova authority | FROZEN | ✅ reusable |
| Lazy-parquet load (R7 invariant) | OPERATIONAL | ✅ reusable; chunked monthly parquet contract preserved |
| CPCV scaffolding (N=10, k=2 → 45 paths, embargo=1 session) | OPERATIONAL | ✅ reusable (caveats §3) |
| Hold-out one-shot discipline (§15.13.7) | DISCIPLINE | ⚠️ **2025-07..2026-04 BURNED on N8.2** — H_next needs different OOS window or fresh tape capture |
| n_trials counter (research-log.md) | n_trials_used=5 | ⚠️ Bonferroni carry-forward applies if H_next consumes same in-sample window; resets to 1 on FRESH window |

### §1.3 What is BLOCKED in current infrastructure (vote-relevant)

- **Book-aware features** (top-of-book imbalance, depth, queue-position-weighted microprice) — historical dataset is **trades-only**. Decision pending: ligar captura diária de book. ANY H_next that depends on book features is BLOCKED until 6-12 calendar months of book capture accumulate.
- **Tick-level latency strategies** (edge < 2 ticks per trade) — DMA2 p50=20ms makes this fragile. Beckett MANIFEST §latency_dma2_profile.implicacoes_para_estrategia: HFT/scalping not viable.
- **Strategies with high turnover under fixed costs** — Path A OFF means costs+slippage are conservatively static. Any H_next that increases trades-per-session 10×+ inherits unchanged per-trade cost drag.

### §1.4 Three candidate hypotheses — simulator-lens viability scoring

I evaluate three plausible H_next candidates the council might surface. For each, I score: (1) wall-time projection, (2) memory budget fit, (3) reusability of assets, (4) Bonferroni inflation risk.

#### Candidate H_next.A — Conviction-conditional sizing on T002 predictor (no new label, no new CV scheme)

- **Premise:** Same predictor (end-of-day inventory unwind v0.2.0); same triple-barrier label; trade FEWER but LARGER when predictor magnitude ≥ Pq quantile (e.g., Pq=70, 80, 90); refined position-sizing function f(predictor_magnitude).
- **Wall-time:** ~3h per re-run (single CPCV pass; sizing rule is a post-prediction transform that does NOT alter feature pipeline or label generation; cached events DataFrame reusable across sizing-rule sweeps if engine-config v1.2.0 lands)
- **Memory:** within 6 GiB cap; identical to T002 baseline
- **Reusability:** ✅ engine-config v1.1.0 reusable; cost atlas reusable; latency reusable; RLP reusable; microstructure reusable
- **Bonferroni:** ⚠️ HIGH RISK — re-uses same in-sample window 2024-08..2025-06; each Pq-level sweep is a new trial; spec yaml v0.2.3 says n_trials_used=5; sizing-axis sweep at 3 levels × baseline = +3 trials → n_trials=8; DSR strict bar inflation factor √(ln(8)/ln(5)) ≈ 1.16× — manageable IF Mira authors a NEW spec branch (T003 not T002.x) so n_trials counter resets cleanly per MANIFEST R15
- **OOS hold-out:** ⚠️ 2025-07..2026-04 BURNED. Either (a) wait for fresh tape (Tiago + Dara collection) accumulating 9-12 months from 2026-05 onward; OR (b) shift in-sample to 2024-08..2024-12 and use 2025-01..2025-06 as new OOS — but this contradicts ESC-013 R6 reusability invariant (in-sample window changes) and forces fresh n_trials=1 Bonferroni from scratch
- **Simulator verdict:** ✅ **FEASIBLE** in calendar terms but with Bonferroni HEAD-WIND. Best fit IF Mira authors fresh spec (T003) AND Dara begins fresh tape capture pipeline NOW for OOS unlock 2026-Q4 or later.

#### Candidate H_next.B — Multi-timeframe regime filter (regime-gate same predictor)

- **Premise:** Same predictor + label. Add macro-regime gate (e.g., ATR_dia_ratio percentile band; VIX-equivalent or DI rate spread proxy) that EXCLUDES trades when regime is unfavorable. Goal: amplify per-trade gross edge by removing low-quality events.
- **Wall-time:** ~3h per re-run (regime filter is a pre-trade boolean mask; does NOT touch CPCV mechanics; reusable cached events)
- **Memory:** within cap; regime feature (1 scalar per session) is negligible
- **Reusability:** ✅ engine + cost + latency reusable; regime feature is NEW (Mira spec authoring required; MANIFEST R15 breaking_field `feature_set` triggers full CPCV re-run from zero)
- **Bonferroni:** ⚠️ HIGH RISK — regime threshold is a continuous parameter; each threshold level is a new trial. Combinatorial 2-axis (Pq × regime threshold) = 9-15 new trials → n_trials inflates to 14-20. Lopez de Prado AFML §11 p-hacking territory unless Mira pre-registers a SINGLE regime threshold with explicit ex-ante justification.
- **OOS hold-out:** Same problem as H_next.A. Hold-out 2025-07..2026-04 BURNED.
- **Simulator verdict:** ⚠️ **FEASIBLE BUT RISKY** — high Bonferroni inflation if not pre-registered cleanly. Mira spec authoring discipline determines viability.

#### Candidate H_next.C — Asymmetric exit (winners run; losers cut faster)

- **Premise:** Same predictor + entry rule. Modify exit: trail stop on winners, hard stop on losers, allow extended holding period for winners (e.g., overnight carry beyond triple-barrier upper window).
- **Wall-time:** ⚠️ 3-4h per re-run (NEW exit logic touches simulator fill engine; partial-fill walks may extend; overnight carry ⇒ rollover-week regime crosses get exercised more frequently; CPCV per-fold PnL recomputation full)
- **Memory:** within cap; exit state machine adds <100MB
- **Reusability:** ⚠️ engine-config v1.1.0 carries forward but exit-rule is NEW spec primitive; Mira spec breaking_field `trading_rules` (MANIFEST R15) triggers full CPCV re-run + n_trials=1 reset (clean Bonferroni!); cost atlas + latency + RLP reusable
- **Bonferroni:** ✅ CLEAN — fresh n_trials=1 if Mira spec pre-registers a SINGLE asymmetric exit configuration
- **OOS hold-out:** Same BURNED problem; needs fresh window
- **Simulator verdict:** ✅ **FEASIBLE WITH ENGINE WORK** — exit logic is the most invasive simulator-side change (estimated 5-10 days Aria/Dex/Quinn cycle for fill-engine extension); but offers cleanest Bonferroni reset because spec-breaking-field triggers fresh trial counter.

### §1.5 Simulator-lens ranking (executability only — NOT alpha quality)

| Candidate | Executable now? | Wall-time per re-run | Bonferroni risk | Engine work | Hold-out availability |
|---|---|---|---|---|---|
| H_next.A — conviction sizing | ✅ YES | 3h | ⚠️ HIGH | none | ❌ BURNED, needs fresh capture |
| H_next.B — regime filter | ✅ YES | 3h | ⚠️ HIGH | minimal | ❌ BURNED, needs fresh capture |
| H_next.C — asymmetric exit | ⚠️ AFTER engine work | 3-4h | ✅ CLEAN reset | 5-10 day cycle | ❌ BURNED, needs fresh capture |

**Common blocker (all three):** OOS hold-out window 2025-07..2026-04 was burned on N8.2 per §15.13.7 one-shot. Forward alpha-discovery needs FRESH tape — Dara + Tiago capture pipeline starting 2026-05 onward, accumulating 9-12 months until adequate OOS window unlocks (~2027-Q1 minimum for statistically meaningful 250+ event OOS per spec §6 floor).

---

## §2 Costed_out_edge salvage path under fixed costs?

### §2.1 The empirical situation

T002 Round 3.1 FINAL evidence (N8.2 PROPER Phase G OOS):

| Metric | In-sample (N7-prime) | Hold-out OOS (N8.2) | Reading |
|---|---|---|---|
| IC Spearman | 0.866010 | **0.865933** | ✅ K3 PASS — predictor↔label rank-stability robust cross-window (decay ratio 0.99991 ≫ 0.5 floor) |
| DSR | 0.767 | **0.205731** | ❌ K1 STRICT FAIL — costs eat realized PnL |
| Sharpe (mean over paths) | +0.046 | **−0.053** | ❌ NEGATIVE OOS |
| Hit rate | 0.497 | **0.472** | ❌ sub-50% trade-level OOS |
| Profit factor | 0.952 | **0.929** | ❌ losing money OOS gross-of-deployment |
| PBO | 0.137 | **0.060** | ✅ low overfitting per-se |

**Diagnostic:** prediction-level edge SURVIVES OOS cleanly (IC=0.866); realization-level edge does NOT (DSR=0.21, Sharpe<0, PF<1). This is the canonical signature of **edge magnitude < cost+friction drag per trade**.

### §2.2 Salvage axes that DO NOT mutate cost atlas (Path A OFF)

The user constraint is binding: cost atlas v1 stays FROZEN. So salvage = amplify gross edge per trade WITHOUT lowering costs. Four families:

| Family | Mechanism | Simulator-side viability | Signal-to-cost-ratio reading |
|---|---|---|---|
| **F1 — Conviction sizing** | Trade FEWER but LARGER on highest-conviction signals | ✅ executable; cost is amortized over larger position | **HIGH ratio** if predictor magnitude is informative AND sizing is bounded by Riven max-position cap (which it is: §9 HOLD #2 Gate 5 fence preserved) |
| **F2 — Regime filter** | Skip unfavorable regimes (low-vol days, rollover week, macro events) | ✅ executable; reduces trade count without increasing per-trade cost | **MEDIUM ratio** — depends on regime predictivity; subject to Bonferroni inflation if multiple thresholds tested |
| **F3 — Asymmetric exit** | Let winners run beyond triple-barrier upper window; cut losers fast | ⚠️ requires engine work (exit state machine extension) | **MEDIUM-HIGH ratio** — winners-run is theoretically the strongest asymmetric leverage (skewness amplification) but adds overnight risk + rollover crossings |
| **F4 — Different label horizon** | Replace intraday triple-barrier with overnight or multi-day label | ⚠️ requires Mira spec re-derivation; predictor↔label coherence may break | **UNCERTAIN ratio** — IC=0.866 is on intraday label; overnight label may have different IC; would need fresh CPCV from zero |

### §2.3 Beckett simulator-lens reading: best signal-to-cost-ratio under fixed costs

**Tier 1 (HIGHEST simulator viability):** **F1 — Conviction-conditional sizing.**

- Reasoning: predictor IC=0.866 is exceptionally high for a financial signal (Lopez de Prado AFML §8 baseline IC 0.05-0.15 for "good" features; 0.866 is multi-σ outlier — likely capturing structural microstructure regularity). If IC is genuinely 0.866 OOS, then conditioning trades on the TOP DECILE of predictor magnitude should preserve IC while DRASTICALLY reducing trade count. Cost-per-dollar-traded becomes amortized; gross-edge-per-trade scales with conviction.
- Empirical caveat: N8.2 OOS metrics are AGGREGATE over all signals. The marginal trade in the bottom deciles is presumably the costed-out one. **Sizing axis directly attacks the binding constraint** without mutating costs.
- Simulator burden: NEAR-ZERO new engine work. Sizing function is a post-prediction scalar transform applied at order-submission time. Can be CPCV-tested in single run if cached events are reused (engine v1.2.0 not strictly required but helpful).
- Risk: Bonferroni inflation IF multiple Pq levels tested without pre-registration. Mira authority to author T003 spec with SINGLE pre-registered Pq (e.g., Pq=80 or Pq=90 with explicit ex-ante justification) — fresh n_trials=1 Bonferroni clean reset.

**Tier 2:** **F3 — Asymmetric exit (winners-run).**

- Reasoning: triple-barrier label is STRUCTURALLY symmetric — caps winners and losers at same horizon. If predictor identifies high-conviction directional moves, capping winners destroys positive skewness. Asymmetric exit (trail stop on winners, hard stop on losers) is the canonical fix.
- Simulator burden: 5-10 day Aria/Dex/Quinn cycle for fill-engine exit-state-machine extension. Partial-fill walks may extend; rollover-week regime gets exercised more frequently (winners-running across rollover triggers Nova rollover-adjustment branch).
- Risk: overnight carry expands risk surface (Riven authority — capital sizing, gap risk, financial cost overnight per cost-engine config; needs Riven sign-off on overnight exposure ladder).

**Tier 3:** **F2 — Regime filter.**

- Reasoning: regime gating is intuitive but empirically risky under multi-threshold sweep. Each threshold is a new trial; Bonferroni inflation is real.
- Mitigation: pre-register a SINGLE regime feature with SINGLE threshold (Mira authority). Otherwise it's p-hacking dressed as research.

**Tier 4:** **F4 — Different label horizon.**

- Reasoning: the IC=0.866 result is on intraday label. Overnight label changes the entire prediction problem. Beckett would need fresh CPCV from scratch (n_trials=1 reset, full hold-out re-allocation, Mira spec re-derivation).
- Simulator-side cost: HIGH — essentially a new strategy, not a salvage of T002.

### §2.4 Combined recommendation

**Beckett recommends F1 (conviction sizing) as the cheapest, highest-signal-to-cost-ratio salvage path.** F3 (asymmetric exit) is a strong follow-on but engine-bound.

A possible TWO-LEG roadmap (NOT a council pre-emption — surfaced for council deliberation):

1. **Leg 1 (next 1-2 sprints):** T003 spec authored by Mira on conviction-conditional sizing F1; uses retired T002 in-sample window 2024-08..2025-06 for fresh CPCV (clean n_trials=1 reset under MANIFEST R15 spec-version increment); 5-trial Bonferroni baseline.
2. **Leg 2 (when fresh OOS tape unlocks ~2027-Q1):** Phase G OOS confirmation on FRESH tape window 2026-05..2027-01.

Engine-config v1.2.0 perf round becomes valuable in Leg 1 IF F1 spec sweeps multiple Pq levels — but a single pre-registered Pq avoids this.

---

## §3 New CV scheme proposal

### §3.1 Three options under simulator lens

| Option | Mechanics | Wall-time | Statistical power | Bonferroni discipline |
|---|---|---|---|---|
| **CV.1 — Same CPCV N=10 k=2 → 45 paths embargo=1** (T002 carry-forward) | Identical to T002 spec yaml v0.2.3 | 3h per trial | HIGH (45 paths distribution) | accumulates n_trials with each spec |
| **CV.2 — Walk-forward online learning** | Rolling train+test windows; no purge needed if test is strictly future | 4-5h per pass (more sequential model fits) | LOW for hypothesis testing (single-path; high autocorrelation) | Bonferroni applies per walk-forward step (worse) |
| **CV.3 — Purged k-fold simpler if H_next is single-trial Bonferroni n_trials=1** | k=5 purged folds, single-fold test, embargo preserved | 1.5-2h per trial | MEDIUM (5 paths only) | n_trials=1 if pre-registered |

### §3.2 Beckett simulator-lens recommendation

**APPROVE CV.1 (same CPCV N=10 k=2 → 45 paths embargo=1) as forward-default for H_next CANDIDATES F1, F2, F3.**

Reasoning:

1. **Reusability invariant (ESC-013 R6):** mutating CPCV scheme is a breaking_field per MANIFEST R15. A new CV scheme triggers full Bonferroni reset BUT also forfeits direct comparability with T002 baseline metrics (DSR, PBO distribution shapes calibrated against 45-path scaffolding). Beckett pessimistic-by-default favors comparability when the alpha problem is "did we fix the costed_out_edge". Same scheme = direct DSR comparison T002 vs T003.
2. **Walk-forward CV.2 is strictly weaker** for hypothesis testing — single-path metrics have high variance, autocorrelation across rolling windows inflates Type I error per Lopez de Prado AFML §13.3. Walk-forward is for online-learning monitoring (post-deployment), NOT for go/no-go research decisions. Beckett discipline: single-path walk-forward is DIAGNOSTIC, never veredicto final.
3. **Purged k-fold CV.3 has lower statistical power** (5 paths vs 45). DSR multiplicity inflation is borderline for low-IC strategies; we already saw T002 IC=0.866 (high) needing 45 paths to detect costed_out signature with PBO=0.06. A regime where we expect SMALLER IC under salvage paths needs MORE paths, not fewer.
4. **Walk-forward ONLY makes sense post-Gate-5** as live-monitoring scaffold (Beckett command `*walk-forward-monitor`). Not as primary research CV.

**Conditional exception:** if H_next is genuinely a SINGLE-TRIAL pre-registered hypothesis (Mira authors T003 spec with explicit "ex-ante chosen Pq=80, no sweep") and if Pax/Riven approve a faster-iteration regime, CV.3 purged k-fold could be acceptable. Beckett would not block, but would mark the decision in run report as "REDUCED-POWER CV scheme" for council audit.

### §3.3 What is NOT changeable (ESC-013 R6 reusability invariant carry-forward)

| Element | Status |
|---|---|
| CPCV N_groups=10, k_per_test=2, embargo=1 session | FROZEN for H_next CANDIDATES that compare to T002 baseline |
| Engine-config v1.1.0 (DMA2 latency, RLP policy, microstructure) | FROZEN per Path A OFF |
| Cost atlas v1 | FROZEN per Path A OFF |
| Bonferroni accounting (n_trials counter in research-log.md) | INCREMENTS per new trial; resets to 1 only on spec-version major bump per MANIFEST R15 |
| Rollover calendar (Nova authority) | FROZEN (calendrical fact, not a research decision) |
| Hold-out one-shot discipline (§15.13.7) | DISCIPLINE; binds K3 measurement; 2025-07..2026-04 window BURNED |

---

## §4 Engine-config v1.2.0 perf optimization (carry-forward)

### §4.1 Current state

T002 wall-time: ~3h per CPCV run. Pichau 8 logical cores; CPU single-threaded; RAM ample (627 MB peak vs 6 GiB cap = 10× headroom). I/O bound on monthly parquet lazy-load + per-fold P126 D-1 anti-leak walks. Hard cap projected by Beckett T0c was 60min — observed 3.0-3.1× over.

### §4.2 v1.2.0 candidate optimizations (carry-forward from N7-prime §10.3)

| Optimization | Expected speedup | Effort | Acceptance risk |
|---|---|---|---|
| **Parquet pre-aggregation per session** (cached OHLCV summary per-session vs full trade walk) | 3-5× | Aria spec + Dex impl ~5-7 days | Quinn QA must preserve trade-tape walk semantics under hold-out / lookahead invariants — non-trivial |
| **Numba/Cython hot-path** (per-fold PnL accumulation; CPCV path-walk inner loop) | 2-3× on hot loops; 1.3-1.5× total | Dex impl ~3-5 days | Quinn QA contract test for bit-equality with engine v1.1.0 reference output |
| **Parallel CPCV path execution** (multiprocessing.Pool over 45 paths) | 2-4× depending on N_cores; Pichau 8 logical cores realistic 3× | Aria spec + Dex impl ~5-10 days | ADR-1 v3 6 GiB RSS cap × parallelism × per-process overhead — needs RSS budget redesign per ADR |
| **Session caching across CPCV folds** (LRU cache of preprocessed events DataFrames) | 2-3× | Dex impl ~2-3 days | Quinn QA must preserve per-fold P126 D-1 anti-leak invariant per ADR-5 / Sable T0b ratification |

### §4.3 Beckett v1.2.0 recommendation (simulator-lens, NOT pre-empting Aria)

**Approval order under simulator viability:**

1. **Session caching** (lowest risk + medium gain ~2-3×) — Dex impl ~2-3 days; ESC-013 R6 reusability invariant honored if cache key includes spec_yaml_sha256 + cpcv_config sha256 + parquet_root_sha256 (cache invalidates cleanly on spec mutation).
2. **Numba hot-path** (medium gain ~1.3-1.5× total, low parallelism risk) — bit-equality contract test mandatory.
3. **Parquet pre-aggregation** (highest single-source gain ~3-5× but trade-tape semantic risk) — Quinn must validate against N8.2 reference output bit-equal; deferred until Mira authors a session-aggregation spec compatible with predictor pipeline.
4. **Parallel CPCV paths** (DEFERRED) — ADR-1 v3 6 GiB RSS cap × 8 processes = potential 48 GiB peak; needs ADR-1 amendment first (Aria authority).

**Rough combined target:** 188min → 60-90min full-run if (1) + (2) land. Brings Beckett within hard cap projection. Useful for H_next iteration BUT not blocking — the single-trial pre-registered discipline (CV.1 + Mira pre-registered Pq) keeps wall-time at ~3h whether or not v1.2.0 lands.

**Simulator verdict:** v1.2.0 is **valuable but NOT blocking** for forward alpha-discovery. Approve session caching as cheapest first step; defer parquet aggregation and parallelism until ADR-1 is amended.

---

## §5 Personal preference disclosure (pessimistic-by-default)

Per Beckett MANIFEST persona discipline — full transparency.

### §5.1 Subjective priors (surfaced for council audit)

| Hypothesis | My subjective P(survives 1-year fresh OOS) |
|---|---|
| H_next.A — conviction sizing F1 (single Pq pre-registered) | ~25% |
| H_next.B — regime filter F2 (single regime, pre-registered) | ~15% |
| H_next.C — asymmetric exit F3 (winners-run, with engine work) | ~20% |
| H_next.D — different label F4 (overnight) | ~10% (different problem; high refit risk) |
| Combination F1 + F3 | ~15% (compound risk; multiple spec breaking_fields) |

**Why so pessimistic:** Lopez de Prado AFML cap 11 multiplicity discount + Bailey 2014 PBO/DSR posterior = baseline P(strategy works on fresh OOS | survives in-sample) is structurally low (~10-30% for "good" research). I have no signal that T002 lessons make us materially better at this — the costed_out_edge bucket evidence is empirically clean (refines diagnostic) but does not prove F1/F2/F3 will work.

### §5.2 Why I prefer F1 over F2/F3 (already in §2)

- F1 directly attacks the binding constraint (cost-per-dollar-traded amortization) without engine work or new spec primitives
- F1 has cleanest Bonferroni story (single Pq pre-registered → n_trials=1 reset)
- F1 has shortest calendar (3h wall + Mira spec authoring ~1-2 days)

### §5.3 Why I am skeptical of "alpha discovery" framing in general

Pessimistic-by-default discipline forces me to surface this:

1. **Selection bias:** the fact that we are looking for forward alpha is itself a signal that prior alpha was not found. Each council that ratifies a new H_next inflates the project's effective n_trials counter — even though MANIFEST R15 resets the counter on spec-version major bump, the META-research n_trials (across H_next.A, H_next.B, H_next.C ...) accumulates AT THE PROJECT LEVEL. Mira research-log discipline tracks this; council should be aware that approving 3 distinct H_next directions in parallel is multi-armed-bandit territory.
2. **Hold-out scarcity:** OOS hold-out tape is a non-renewable resource at the calendar scale we operate (years). 2025-07..2026-04 BURNED on N8.2; the next adequate OOS window unlocks ~2027-Q1 if Dara starts capture NOW. Approving multiple H_next in parallel means competing for the same future hold-out.
3. **Cost-side immutability:** Path A OFF means we are committed to amplifying gross edge under static frictions. The gross-edge ceiling for low-volume Pq=90 conviction sizing on ~3800 events/year is bounded by event count × per-trade gross edge. Bayesian prior: hard ceiling.

I am NOT against forward alpha-discovery. I AM against scheduling 3 parallel H_next directions with shared OOS budget. Beckett's pessimistic recommendation: **pick ONE H_next, pre-register cleanly, run on retired-T002 in-sample window for fresh CPCV; accumulate fresh tape in parallel; defer OOS unlock until 2027-Q1 minimum.**

### §5.4 Bias self-audit

- I am **biased toward fewer experiments + tighter pre-registration** (pessimistic about p-hacking; high prior that refinement is overfitting)
- I am **biased toward F1 (conviction sizing)** because it has the simplest engine path and cleanest Bonferroni story; not because it is alpha-superior to F2/F3
- I am **biased AGAINST scheduling 3 H_next in parallel** under shared OOS budget; recommend serial single-thread research roadmap
- I am **NOT biased against engine-config v1.2.0** in principle; only against treating it as a pre-requisite for any H_next

---

## §6 Article IV self-audit

Per Constitution Article IV (No Invention) + Beckett MANIFEST R15 spec-consumer discipline + Anti-Article-IV Guards #1-#8 carry-forward from T002 retire ceremony.

### §6.1 Trace anchoring

| Claim category | Trace anchor |
|---|---|
| T002 Round 3.1 FINAL FAIL costed_out_edge_oos_confirmed_K3_passed | docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md frontmatter + §1 disposition |
| N8.2 OOS metrics IC=0.865933 / DSR=0.205731 / Sharpe=-0.053 / hit=0.472 / PF=0.929 / PBO=0.06 | data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/full_report.md (verbatim values) |
| N7-prime in-sample IC=0.866010 / DSR=0.767 / Sharpe=+0.046 / hit=0.497 / PF=0.952 | docs/backtest/T002-beckett-n7-prime-2026-04-30.md §3 (carry-forward from prior Beckett ballot ESC-012) |
| Wall-time 188min N7-prime + 141min N8.2 | per-run telemetry.csv + N7-prime §10.3 + N8.2 frontmatter |
| Engine-config v1.1.0 frozen (DMA2 latency p50=20ms / p95=60ms / p99=100ms / tail 500ms) | docs/backtest/engine-config.yaml + Beckett MANIFEST §latency_dma2_profile |
| ESC-013 R6 reusability invariant | docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md §4 |
| MANIFEST R15 spec-consumer rules + breaking_fields list | Beckett MANIFEST core_principles §15 verbatim |
| Bonferroni inflation factor √(ln(n2)/ln(n1)) DSR adjustment | Bailey-Lopez de Prado 2014 §2.3 (canonical formula) |
| §15.13.7 OOS one-shot binds K3 measurement | Mira spec v1.2.0 §15.13.7 + ESC-013 §4.2 R9 ratified interpretation |
| Hold-out 2025-07..2026-04 BURNED on N8.2 | Mira Round 3.1 sign-off frontmatter `n8_2_run_dir` + spec one-shot |
| Trades-only dataset blocking book-aware features | Beckett MANIFEST §historical_data_reality + §o_que_NÃO_temos |
| Subjective priors §5.1 / §5.3 | EXPLICITLY MARKED AS SUBJECTIVE per pessimistic-by-default disclosure protocol |
| Calendar estimates (1-2 days Mira spec; 5-7 days v1.2.0; 9-12 months fresh OOS capture) | per-task estimates surfaced as informational; not spec-binding |

### §6.2 Invention check

- ❌ NO new statistical thresholds invented (DSR>0.95 / PBO<0.5 / IC>0 verbatim from Mira spec v1.2.0)
- ❌ NO new spec-binding rules introduced (CV.1 = T002 spec yaml v0.2.3 verbatim)
- ❌ NO new agent authorities created (existing matrix preserved)
- ❌ NO new data-quality bucket sub-classifications proposed (costed_out_edge_oos_confirmed_K3_passed is Mira Round 3.1 verbatim disposition)
- ❌ NO simulator semantics modified (engine-config v1.1.0 preserved across all candidates)
- ❌ NO H_next selected on Beckett's behalf (Mira authors spec; Pax authors story; this ballot ranks viability ONLY)
- ✅ Subjective probability priors §5.1 / §5.3 are explicitly surfaced as subjective for council audit
- ✅ Calendar-cost ranges are estimates (clearly marked as estimates) — no false precision
- ✅ Hypothesis ranking §1.5 is per-this-council framing, not new spec rule

### §6.3 Authority boundary check

- ✅ Vote does NOT bind Mira spec authoring authority (forward-research spec design = Mira)
- ✅ Vote does NOT pre-empt Pax forward-research scope authority
- ✅ Vote does NOT pre-empt Riven custodial Bayesian prior updates / capital-ramp authority
- ✅ Vote does NOT pre-empt Aria architecture authority over engine-config v1.2.0 spec
- ✅ Vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE; no `git add` / `commit` / `push` performed by this authoring)
- ✅ Vote does NOT pre-empt Dara custodial manifest authority over fresh-tape capture/materialization scheduling
- ✅ Vote does NOT pre-empt Quinn QA authoring forward gates
- ✅ MANIFEST R11-R14 escopo respeitado: domain authority (O-QUÊ — fill rules / slippage / latency / CPCV config); NÃO COMO de orquestração
- ✅ Anti-Article-IV Guard #8 verdict-issuing protocol respected — Beckett does not emit ML/risk/verdict labels outside simulator-feasibility domain

### §6.4 Round 3.1 fidelity check

- ✅ Mira Round 3.1 verdict `GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed` accepted as binding context (NOT rebutted, NOT relaxed, NOT salvage-pathed away)
- ✅ T002 retire disposition preserved (this ballot is FORWARD scope, not T002 re-litigation)
- ✅ ESC-013 §5(c) outcome `costed_out_edge_oos_confirmed_K3_passed` acknowledged as the empirical input that frames forward research
- ✅ Path A OFF user constraint honored verbatim (no cost atlas mutation considered)
- ✅ §15.13.7 OOS one-shot honored (BURNED hold-out window not re-litigated)

### §6.5 Self-audit verdict

**Article IV PASSED.** No invention. All claims trace. All authority boundaries respected. Round 3.1 fidelity preserved. Subjective preferences explicitly surfaced for council audit. MANIFEST R11-R15 honored. Pessimistic-by-default discipline maintained.

---

## §7 Beckett cosign 2026-05-01 BRT — Quant Council ballot simulator lens

```
Voter: Beckett (@backtester) — Backtester & Execution Simulator authority
Council: QUANT-2026-05-01-alpha-discovery
Topic: Forward alpha-discovery framing post-T002 retire (Round 3.1 FINAL FAIL costed_out_edge_oos_confirmed_K3_passed)
Constraint recap:
  - User canonical Path A OFF (cost reduction R&D suspended)
  - T002 RETIRED with refined OOS-confirmed costed_out_edge_K3_passed bucket
  - Engine-config v1.2.0 NOT YET AUTHORED
  - Hold-out 2025-07..2026-04 BURNED on N8.2 one-shot

Simulator-lens viability ranking (executability ONLY, not alpha quality):
  H_next.A — conviction sizing F1: ✅ FEASIBLE NOW; 3h re-run; Bonferroni HIGH if not pre-registered; cleanest signal-to-cost-ratio attack on costed_out_edge
  H_next.B — regime filter F2: ⚠️ FEASIBLE BUT RISKY; 3h re-run; Bonferroni HIGH unless single-threshold pre-registered
  H_next.C — asymmetric exit F3: ✅ FEASIBLE WITH ENGINE WORK (5-10 days); 3-4h re-run; Bonferroni CLEAN reset (spec-breaking-field triggers fresh n_trials=1)
  Common blocker (all three): OOS hold-out window BURNED; fresh tape capture from 2026-05 onward; OOS unlock ~2027-Q1 minimum

Costed_out_edge salvage simulator recommendation:
  Tier 1 (HIGHEST signal-to-cost-ratio): F1 conviction-conditional sizing (single Pq pre-registered)
  Tier 2: F3 asymmetric exit (winners-run, engine work required)
  Tier 3: F2 regime filter (single regime pre-registered or skip)
  Tier 4: F4 different label horizon (essentially a new strategy)
  Combined recommendation: PICK ONE; serial single-thread research; defer OOS unlock 2027-Q1

CV scheme proposal:
  Approve CV.1 — same CPCV N=10 k=2 → 45 paths embargo=1 (T002 carry-forward)
  Reject CV.2 walk-forward as primary research CV (DIAGNOSTIC ONLY; post-Gate-5 monitoring scaffold)
  Accept CV.3 purged k-fold ONLY for explicit single-trial pre-registered hypothesis with reduced-power disclosure

Engine-config v1.2.0 perf round (carry-forward):
  Approval order: session caching → numba hot-path → parquet pre-aggregation → parallel CPCV (deferred until ADR-1 amended)
  Combined target 188min → 60-90min if first two land
  NOT BLOCKING for forward alpha-discovery (single pre-registered Pq keeps wall-time at 3h regardless)

Personal preference disclosure (pessimistic-by-default):
  Subjective P(F1 survives 1yr fresh OOS) ≈ 25%
  Subjective P(F2 survives) ≈ 15%
  Subjective P(F3 survives) ≈ 20%
  Subjective P(F4 survives) ≈ 10%
  Combined F1+F3 ≈ 15% (compound risk)
  Bias self-audit: biased FOR fewer experiments + tighter pre-registration; biased FOR F1 cleanest engine path; biased AGAINST scheduling 3 parallel H_next under shared OOS budget

Authority boundary preservation:
  NO push (Article II → Gage exclusive)
  NO Mira spec authoring pre-emption (forward-research spec design = Mira authority)
  NO Pax forward-research scope pre-emption
  NO Riven custodial Bayesian prior / capital-ramp pre-emption
  NO Aria engine-config v1.2.0 spec pre-emption
  NO Dara fresh-tape capture/materialization pre-emption
  NO Quinn forward-gate authoring pre-emption
  NO new spec rules; no new statistical thresholds; no engine semantics modification

Round 3.1 fidelity:
  Mira Gate 4b Round 3.1 FINAL FAIL costed_out_edge_oos_confirmed_K3_passed accepted as binding context
  Path A OFF user constraint honored verbatim
  §15.13.7 OOS one-shot honored (BURNED window not re-litigated)
  ESC-013 R6 reusability invariant honored

Article IV self-audit (§6): PASSED — no invention; all claims trace; subjective preferences surfaced; authority boundaries respected; MANIFEST R11-R15 honored.

R15 compliance: ballot under canonical docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-beckett-vote.md naming.

Decision: BECKETT VIABILITY RANKING + RECOMMENDATIONS surfaced for council aggregate
  (1) F1 conviction sizing as cheapest highest-signal-to-cost-ratio salvage path
  (2) CV.1 same CPCV scheme carry-forward
  (3) Engine v1.2.0 NOT BLOCKING; session caching first if any work
  (4) Serial single-thread H_next; defer OOS unlock to 2027-Q1 minimum on fresh tape
  (5) Begin Dara fresh-tape capture pipeline NOW for forward OOS budget

Cosign: Beckett @backtester 2026-05-01 BRT — Quant Council ballot simulator lens
```

---

— Beckett, reencenando o passado para informar o futuro com fidelidade pessimista 🎞️
