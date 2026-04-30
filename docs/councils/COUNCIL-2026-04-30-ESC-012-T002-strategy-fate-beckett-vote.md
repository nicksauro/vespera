---
council: ESC-012
topic: T002 strategy-fate adjudication post-Mira-Round-2 (GATE_4_FAIL_strategy_edge / costed_out_edge)
date_brt: 2026-04-30
voter: Beckett (@backtester)
role: Backtester & Execution Simulator authority — empirical feasibility adjudicator
constraint_recap: slippage + costs FIXOS já conservadores; Path A cost-reduction OFF
paths_under_vote:
  - "A' — Strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble) sob custos fixos"
  - "B  — Phase G hold-out unlock OOS confirmation"
  - "C  — Retire T002"
authority_basis:
  - ESC-011 R8/R11/R14 (Gate 4b empirical evidence beat preserved)
  - Mira Gate 4b spec v1.1.0 §15.10 + §15.11 stage F2-T5 (Round 2 verdict consumed)
  - Beckett N7-prime full report 2026-04-30 (3h 8min wall, 188min)
  - Beckett N7 baseline 2026-04-30 (3h 1min 50s wall, 182min)
  - Anti-Article-IV Guards #1-#8 (Round 2 §9 ratified)
inputs_consulted:
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md (this Beckett's authority output)
  - docs/backtest/T002-beckett-n7-2026-04-30.md (this Beckett's authority output)
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md (Mira F2-T5 Round 2 authoritative re-clearance)
  - data/in_sample/year=*/month=*/wdo-*.parquet (manifest verified directly via Read+Bash)
  - data/manifest.csv (Dara custodial manifest — phase column inspected)
  - D:/sentinel_data/historical/ (raw daily WDO_YYYYMMDD.parquet; hold-out window verified present)
non_pre_emption:
  - This vote does NOT bind Pax forward-research authority (ESC-011 R10)
  - This vote does NOT pre-disarm Riven §9 HOLD #2 Gate 5 (Riven authority preserved)
  - This vote does NOT amend Mira spec v1.1.0 §1 thresholds (Anti-Article-IV Guard #4 verbatim)
  - This vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
  - This vote does NOT pre-empt Dara custodial manifest authority over hold-out materialization
---

# ESC-012 — Beckett Vote on T002 Strategy-Fate (post Mira Round 2 GATE_4_FAIL_strategy_edge / costed_out_edge)

> **Author:** Beckett (@backtester) — Backtester & Execution Simulator authority. Empirical-feasibility adjudicator over the three reframed paths. Pessimistic-by-default; if the simulator burden is incertain, I assume the worst.
> **Date (BRT):** 2026-04-30.
> **Branch:** `main` @ `81139de`. Vote authoring is local-only docs work; no source mutation; no push.
> **Decision authority basis:** ESC-011 R7/R8/R9/R11/R14 + Mira Gate 4b spec v1.1.0 §15.11 + Mira Round 2 sign-off `GATE_4_FAIL_strategy_edge / costed_out_edge`. Round 2 partial-falsification reading establishes the empirical context; this council adjudicates the forward-research path.

---

## §1 Verdict + rationale

**Verdict:** **`APPROVE_PATH_B`** — **Phase G hold-out unlock OOS confirmation, single experiment, with hard preconditions on Dara hold-out materialization and Riven §9 HOLD #2 Gate 5 lock preservation.**

**Conditional fallback:** if Dara hold-out materialization is **not** feasible inside a council-acceptable window (e.g., > 14 days), my vote shifts to **`APPROVE_PATH_C`** (retire T002 cleanly). Path A' is **rejected** as my primary recommendation under empirical-feasibility scrutiny — see §2.A.

**One-line rationale:** Path B is **cheapest information-per-experiment** under the costed_out_edge hypothesis Mira Round 2 surfaced (single ~3h re-run on already-captured raw daily tape vs Path A' ~36h burden across 12 refinement re-runs). Path B answers the only Round-2-pendant scientific question that K1 strict bar leaves open (does the in-sample IC=0.866 prediction-level edge survive on tape the strategy never saw?). Path A' is high-noise refinement territory with no engineering pre-requisite resolved (perf v1.2.0 not authored; 36h simulator burden under fixed costs). Path C is acceptable as cleanest-exit fallback, but burns the in-sample IC=0.866 evidence without OOS confirmation — Mira Round 2 §8.3 explicitly classifies Phase G as "OOS confirmation step (NOT salvage path)", which is the disposition I want preserved.

**Why I do NOT vote Path A' as primary:**

1. **Empirical burden:** 12 re-runs × ~3h each ≈ 36h simulator wall-time **without** engine-config v1.2.0 perf optimization (which is itself a 3-card hold per N7-prime §10.3 + Beckett T0c projection). Until Aria/Dex deliver v1.2.0, A' is unaffordable in calendar terms;
2. **Statistical hazard:** refinement under fixed costs + same in-sample window = canonical p-hacking territory per Lopez de Prado AFML §11. Each refinement axis (entry timing × regime filter × conviction threshold × signal ensemble) inflates `n_trials` Bonferroni count; spec §6 floor 250 is fine but DSR threshold 0.95 strict gets harder, not easier, with each new trial. Mira spec yaml v0.2.3 L207-209 + Anti-Article-IV Guard #4 are UNMOVABLE — A' has to **clear DSR > 0.95 strict on the SAME in-sample window with MORE trials**, which is a tighter bar after Bonferroni inflation;
3. **No OOS confirmation:** A' refines on the same in-sample window the strategy already failed K1 strict on. Any "improvement" lacks Phase G confirmation and is therefore epistemically inferior to a single Phase G experiment under the costed_out_edge hypothesis Mira Round 2 surfaced.

**Why Path B over Path C:**

The Mira Round 2 verdict is **partial falsification** with sub-classification `costed_out_edge` — an explicit Round 2 nuance distinguishing prediction-level edge (IC=0.866 strong) from execution-layer realization (DSR=0.767, hit_rate=0.497, sharpe_mean=+0.046). Round 2 §8.3 authorized Phase G holdout unlock as **OOS confirmation step (NOT salvage)**. Two outcomes after Phase G:

- (B-out-1) OOS DSR also < 0.95 strict ⇒ T002 retired with **clean negative confirmation** of the costed_out_edge bucket. This is **strictly stronger** than Path C (T002 retired with no OOS confirmation), because the partial-edge story stays plausible without Phase G evidence — and a strategy hypothesis that retires without OOS evidence is canonically weaker per spec §0 falsifiability mandate.
- (B-out-2) OOS DSR > 0.95 ⇒ regime evidence is mixed (in-sample costed-out + OOS deployable) → Mira-led council escalation under ESC-011 R8/R20 governance. Note: B-out-2 is improbable given in-sample DSR=0.767 (a 0.18+ jump on tape never seen would be statistically extraordinary), but its low probability is itself information.

Path C burns the empirical work of N7+, N7, N7-prime + the IC pipeline wiring fix without consuming the OOS confirmation step Mira Round 2 explicitly designed for. Path B costs ~3h simulator wall-time + Dara hold-out materialization burden, in exchange for **clean evidence** that closes the costed_out_edge story one way or the other.

**Pessimistic-by-default disclaimer:** I expect B-out-1 with high subjective probability (>75%) given DSR=0.767 in-sample and the canonical pattern of in-sample-strong / OOS-fade. But high expected probability of FAIL does **not** undermine the decision to run Path B — it strengthens it, because the outcome is informationally valuable either way (evidence of the partial-edge being entirely costed-out vs evidence of regime-shift survival).

---

## §2 Empirical feasibility analysis (each path's run-cost)

### §2.A Path A' — Strategy refinement (rejected as primary)

**Refinement axes (per ESC-012 task framing):**
1. Entry timing (e.g., 16:50 / 16:55 / 17:00 / 17:05 / 17:10 / 17:15 / 17:20 / 17:25 / 17:30 entry windows)
2. Regime filter (e.g., narrower ATR_dia_ratio percentile bands; volatility regime gating)
3. Conviction threshold (e.g., higher predictor magnitude floor; higher signal-strength bar)
4. Signal ensemble (e.g., add intraday VWAP slope; add EMA-deviation; add depth proxy)

**Per-axis re-run estimate (under engine-config v1.1.0 — i.e., NO perf round):**
- Each refinement experiment = re-run CPCV 5 trials × 45 paths over in-sample window (3800 events; ~10 months)
- Per Beckett N7-prime §3.1: 3800 events × 5 trials = 19,000 trial-events → 188 min wall (~3h 8min)
- Per Beckett N7 baseline: 182 min (~3h 1min 50s) — consistent ±3.5%
- **Per re-run estimate: ~3h ± 0.2h simulator wall-time on Pichau hardware**

**Combinatorial burden:**
- 4 axes × ~3 levels each (conservative) = 12 single-axis re-runs (no joint coverage)
- 4 axes × ~5 levels each (modest) = 20 single-axis re-runs
- Joint coverage 2-axis cross-tab (~3 levels × ~3 levels × 6 axis-pairs) = 54 joint re-runs
- **Lower-bound estimate: 12 re-runs × 3h ≈ 36h wall-time**
- **Modest estimate: 20 re-runs × 3h ≈ 60h wall-time**
- **Joint-coverage estimate: 54 re-runs × 3h ≈ 162h wall-time (≈1 week of continuous CPCV runs)**

**Engine-config v1.2.0 perf optimization pre-requisite:**
- Beckett N7-prime §10.3 + N7 §7 surfaced **C1' wall-time concern carry-forward** — full-run 3.0-3.1× over the 60min hard cap
- Beckett T0c projection recommended **engine-config v1.2.0** with parquet pre-aggregation OR session caching across CPCV folds
- v1.2.0 spec is NOT YET AUTHORED — would require Aria/Dex/Quinn cycle (rough order: 5-10 days)
- Absent v1.2.0, A' lower-bound 36h wall-time means **~5 calendar days of continuous CPCV running** (no parallelism on this hardware; ADR-1 v3 6 GiB RSS cap; 627 MB observed leaves headroom but no spare CPU)
- WITH v1.2.0 (hypothetical 3-5× speedup): 36h becomes 7-12h (~1-2 days continuous)

**Statistical-hazard inflation:**
- Each refinement re-run is a **new trial under Bonferroni accounting** per Mira spec §6 + research-log canonical n_trials counter
- N7-prime currently at `n_trials_used=5`; A' adds at minimum 12 new trials → n_trials=17 → DSR threshold inflation of √(ln(17)/ln(5)) ≈ 1.32× — current DSR=0.767 with n_trials=5 must rise to roughly DSR=1.01 effective with n_trials=17 to clear the strict 0.95 bar after multiplicity correction
- This is statistically **unfeasible** with cost+slippage held fixed conservatively — refinement of entry/exit timing without cost reduction has very limited Sharpe upside relative to the drag introduced by Bonferroni inflation
- Exception: if A' finds an axis that **dramatically reduces drawdown** (e.g., regime filter that excludes 30% of low-quality events while retaining 90% of edge), DSR could rise materially. But this is an empirical conjecture, not a likely-to-pay bet under fixed costs

**Verdict simulator-side:** A' is **executable but expensive AND statistically hazardous**. **Rejected as primary recommendation** under empirical-feasibility scrutiny.

### §2.B Path B — Phase G hold-out unlock OOS confirmation (PRIMARY)

**Single re-run estimate:**
- Hold-out window per Mira spec §0 + parent thesis Q5: **2025-07-01 → 2026-04-21** (≈ 10 months — same duration as in-sample 2024-08-22..2025-06-30)
- Same `n_events × n_trials` order of magnitude expected (~3800 events × 5 trials ≈ 19,000 trial-events, give or take ±10% for differing session counts and rollover dynamics in 2025-2026)
- Same engine-config v1.1.0 (no perf round needed for **single** re-run; the 3h-1.2h cost is acceptable for single experiment whereas it's prohibitive across 12+)
- **Estimated wall-time: ~3h ± 0.3h** (single re-run, mirror of N7-prime full-run on different parquet window)

**Hold-out tape availability — critical pre-condition (verified §4):**
- ❌ **Hold-out NOT materialized** in `data/holdout/year=YYYY/month=MM/wdo-YYYY-MM.parquet` form expected by Beckett `BacktestRunConfig` parquet_root contract
- ✅ **Raw per-day parquets EXIST** on `D:/sentinel_data/historical/WDO_YYYYMMDD.parquet` for 2025-07-01 → 2026-03-16 (last verified file `WDO_20260313.parquet`, with WIN files extending to 2026-03-16)
- Coverage gap: hold-out window per spec end is 2026-04-21; D-drive coverage to 2026-03-16 means **~5 weeks short on the right edge** at run-time-of-this-vote
- Materialization burden = Dara T002.7-prep task (per `docs/architecture/data-pipeline.md` materialize-full pattern; ref `data/materialize-full.log` on disk evidences prior runs)
- Estimated Dara materialization wall-time: ~1-2h per month × 10 months ≈ 10-20h Dara-side (parallelizable per month; one-shot job). NOT Beckett's authority — surfaced for council awareness

**Single-experiment information value:**
- Phase G OOS run produces directly comparable metrics to N7-prime at the same dimensionality (sharpe_distribution, DSR, PBO, IC_in_sample → re-named IC_holdout once unlock fires per spec §15.10 K3 decay sub-clause activation)
- IC_holdout vs IC_in_sample = 0.866 → tests the canonical decay condition `IC_holdout > 0.5 × IC_in_sample = 0.433`
- DSR_holdout vs DSR_in_sample = 0.767 → tests whether costed_out_edge holds out-of-sample
- Hit-rate, sharpe_mean, sharpe_std, max_drawdown, ulcer_index → side-by-side reproducibility table mirror

**Verdict simulator-side:** B is **cheapest single experiment with highest information density**. **APPROVED as primary** under conditions §6.

### §2.C Path C — Retire T002

**Re-run cost:** Zero. No new simulator runs.

**Simulator side burden:**
- Preserve N7+, N7, N7-prime artifacts (`data/baseline-run/cpcv-dryrun-*-1ce3228230d2/` directories) under R16/R17 reproducibility receipts (already in place; no action needed)
- Update Riven post-mortem ledger entry to reflect bucket B `strategy_edge / costed_out_edge` (Riven authority; F2-T6 task — gated em this ESC outcome)
- Update Mira research-log to mark T002 as RETIRED with link to Round 2 sign-off
- Optional: write a 1-page "lessons learned" summary capturing:
  - IC pipeline wiring gap → Round 2 fix → demonstrated wired-fix-via-bit-equal-stamps reproducibility pattern
  - K3 in-sample binding clause (§15.10) value vs decay-clause (§15.10 Phase G) — useful for future edge-existence specs
  - costed_out_edge sub-classification recipe for Riven 4-bucket attribution future work

**Strategic cost (NOT simulator-side, but worth surfacing to council):**
- T002 retirement WITHOUT Phase G confirmation = **partial-falsification disposition** persists per Mira Round 2 §8.3
- The partial-edge story is **plausible but unconfirmed**; future research on related theses (e.g., other end-of-day inventory unwind variants) lacks the OOS data to anchor priors
- Path C burns the cheapest information experiment available

**Verdict simulator-side:** C is **cheapest by run-cost (0)** but **most expensive by information-cost** (forfeits OOS confirmation step Mira Round 2 explicitly designed for). **Acceptable as fallback** when Path B's hold-out materialization is not feasible inside a council-acceptable window.

---

## §3 Simulator wall-time considerations + perf prerequisite

### §3.1 N7+, N7, N7-prime wall-time empirical baseline

| Run | Wall-time observed | Hard cap (Beckett T0c) | Ratio | Notes |
|---|---|---|---|---|
| N7+ smoke (30 days) | ~17 min (per smoke report cross-ref) | < 60 min | 0.28× | warmup + 1-2 month coverage smoke |
| N7 full (10 months) | **181 min 50s** = 3.03h | < 60 min | **3.03×** | first authoritative full Phase F run |
| N7-prime full (10 months, IC fix) | **188 min 12s** = 3.14h | < 60 min | **3.14×** | Round 2 IC pipeline post-fix; +22s incremental for IC compute (n=10000 PCG64 paired-resample bootstrap) |

**Carry-forward observation:** N7+, N7, N7-prime are consistent ±3.5% in wall-time. Linear scaling of CPCV path-PnL walk dominates; IC compute is sub-1% incremental. **Wall-time is structurally 3.0-3.1× over the 60min hard cap** under engine-config v1.1.0.

### §3.2 Engine-config v1.2.0 perf optimization options

Surfaced N7-prime §10.3 + N7 §7 — **NOT YET AUTHORED**; would require Aria/Dex/Quinn cycle:

| Optimization | Expected speedup | Implementation burden | Acceptance risk |
|---|---|---|---|
| Parquet row-group pre-aggregation (per-session OHLCV cache) | ~3-5× | medium (Aria spec + Dex impl ~5-7 days) | Quinn QA acceptance — must preserve trade-tape walk semantics under hold-out / lookahead invariants |
| Session caching across CPCV folds (LRU cache of preprocessed events DataFrames) | ~2-3× | low-medium (Dex impl ~2-3 days) | Quinn QA — must preserve per-fold P126 D-1 anti-leak invariant per ADR-5 / Sable T0b ratification |
| Parallelism over CPCV paths (multiprocessing.Pool) | ~2-4× depending on N_cores; Pichau = 8 logical | medium (Aria spec + Dex impl ~5-10 days) | ADR-1 v3 6 GiB RSS cap × parallelism × per-process overhead — needs careful design or multi-process RSS budget |
| Lazy-load + lazy-eval (current) | baseline | n/a | n/a — already in place |

**Acceptable v1.2.0 implementation path (rough order, NOT pre-empting Aria authority):** session caching (lowest risk) → parquet pre-aggregation (medium risk + medium gain) → parallelism (highest risk, hardest QA acceptance). Combined hypothetical 3-5× speedup brings full-run from 188min to 38-63min (close to but not reliably under the 60min hard cap).

**Vote-relevant takeaway:**
- Path B's **single re-run** does NOT require v1.2.0 (3h is acceptable for one experiment)
- Path A's **12+ re-runs** materially benefit from v1.2.0 (cuts 36h to 7-12h), but v1.2.0 itself is a 5-10 day pre-requisite that has not been authored or scheduled
- Path C requires no perf round

### §3.3 Pichau hardware ceiling (relevant for both A' and B)

- ADR-1 v3 RSS cap: 6 GiB → observed peak ~627 MB (Beckett N7-prime telemetry §10.3) ⇒ 10× headroom; not binding
- Telemetry sampling overhead: ~51 KB CSV per run; negligible
- Disk I/O per run: 18 monthly parquets (~1.4 GB total) lazy-loaded per session-walk; negligible incremental I/O over RAM cost
- CPU: single-thread CPCV walk; engine v1.1.0 not parallelized — 8 logical cores idle during run; clear opportunity for v1.2.0 multiprocessing if A' approved

### §3.4 Wall-time pessimism inflation under fixed costs (vote-relevant)

Pessimistic-by-default Beckett practice: when in doubt, multiply wall-time estimates by 1.5×. Applied here:

| Path | Best-case wall-time | Pessimistic-inflation | Calendar implication |
|---|---|---|---|
| Path A' (12 re-runs, no v1.2.0) | 36h | **54h** (~2.25 calendar days continuous) | unfeasible in 1-day council deadline; needs scheduling |
| Path A' (12 re-runs, with v1.2.0 hypothetical 3×) | 12h | **18h** (~0.75 calendar day continuous) | feasible in calendar terms IF v1.2.0 lands; v1.2.0 itself is 5-10 days |
| Path A' (modest 20 re-runs, no v1.2.0) | 60h | **90h** (~3.75 calendar days) | unfeasible without v1.2.0 |
| Path B (1 re-run) | 3h | **4.5h** | feasible in calendar terms once Dara hold-out lands |
| Path C | 0h | 0h | n/a |

---

## §4 Hold-out tape availability check

### §4.1 Materialized hold-out parquets — **NOT PRESENT**

Verified directly via Bash + Glob (vote-time 2026-04-30 BRT):

```
data/in_sample/year=2024/month=01..12/wdo-2024-MM.parquet  → present (12 files)
data/in_sample/year=2025/month=01..06/wdo-2025-MM.parquet  → present (6 files)
data/holdout/...                                            → DIRECTORY DOES NOT EXIST
data/hold_out/...                                           → DIRECTORY DOES NOT EXIST
data/out_of_sample/...                                      → DIRECTORY DOES NOT EXIST
```

`data/manifest.csv` Dara custodial manifest (vote-time inspection): **18 rows; phase column ∈ {warmup, in_sample}; no hold_out/holdout/oos phase rows**. This confirms that materialized hold-out parquets at the canonical filesystem layout `data/holdout/year=YYYY/month=MM/wdo-YYYY-MM.parquet` (or equivalent monthly aggregation) are **not yet generated** for the 2025-07-01 → 2026-04-21 hold-out window.

### §4.2 Raw daily files — **PRESENT on D:/sentinel_data/historical/**

Verified directly via Bash:

| Period | Coverage status |
|---|---|
| WDO_20250701 → WDO_20250731 (2025-07) | ✅ all sessions present |
| WDO_20250801 → WDO_20250811 onward (sample only spot-checked) | ✅ partial enumeration confirmed |
| Coverage extends to | WDO_20251231, WIN_20260316 (most recent file in tail) |
| **Implication** | Raw per-day files exist for **2025-07 → 2026-03** (~9 months); 2026-04 partial — **~5 weeks of coverage gap on right edge of spec hold-out window 2026-04-21** |

### §4.3 Materialization workload (Dara authority — surfaced for council)

- Dara T002.7-prep equivalent task: aggregate D:/sentinel_data/historical/WDO_*.parquet daily files into `data/holdout/year=YYYY/month=MM/wdo-YYYY-MM.parquet` monthly format
- Reference pattern: `data/materialize-full.log` + `data/materialize-may-jun-2025.log` evidence prior monthly aggregation runs by Dara
- Per-month aggregation wall-time estimate: ~1-2h Dara-side (per-month parquet concat + sha256 stamp + manifest row append)
- 10-month materialization = ~10-20h Dara wall-time (parallelizable; one-shot job)
- **Right-edge gap remediation:** spec hold-out runs to 2026-04-21; raw daily coverage to ~2026-03-16. Either (a) accept coverage to 2026-03 only (≈9-month hold-out, slightly truncated from spec ≈10-month) OR (b) wait for Dara/Tiago to capture remaining 5-6 weeks of daily files via ProfitDLL collection
- Manifest update + sha256 stamping is part of the Dara workflow

### §4.4 Vote-relevant takeaway

- Path B is **technically feasible** because raw daily files exist (the underlying tape is captured) — ✅
- Path B is **NOT immediately runnable** because monthly aggregation has not happened — ❌ until Dara T002.7-prep
- **Council cost of Path B = ~10-20h Dara wall-time + ~3h Beckett wall-time + ~1-3 days calendar for Dara aggregation**
- Right-edge truncation (2026-03-16 vs spec 2026-04-21) is a **~5-week shortening** that I judge **acceptable** because:
  - 9 months OOS is statistically nearly equivalent to 10 months OOS at the in-sample dimensionality (~3500 events vs ~3800 events; well within Bailey-LdP §3 reproducibility floor)
  - Right-edge gap can be filled later via Tiago live collection if Phase G OOS results justify continued T002 investment
  - Spec strict reading (§0 + Mira Round 2 §8.3) authorizes "Phase G holdout unlock"; spec yaml v0.2.3 hold-out window endpoint is canonical but Mira authority can authorize a slight right-edge truncation under Round 2 partial-falsification disposition (Mira authority — surfaced as informational, not binding from Beckett side)

---

## §5 Personal preference disclosure

Per ESC-012 task framing — full transparency on Beckett's pessimistic-by-default heuristics:

### §5.1 Hypothetical priors (subjective; surfaced for council audit)

| Path | My subjective P(generates new actionable evidence) | My subjective P(burns calendar with no decision-improving signal) |
|---|---|---|
| Path A' (no v1.2.0 first) | ~15% | ~75% (p-hacking territory + DSR Bonferroni inflation) |
| Path A' (with v1.2.0) | ~30% | ~50% |
| **Path B** | **~85%** (regardless of OUTCOME, OOS evidence is decision-improving — "FAIL confirms costed_out, PASS opens regime-shift question") | ~10% (only if Dara materialization slips badly) |
| Path C | ~50% (lessons-learned valuable) | ~30% (preserves option but burns OOS confirmation step) |

### §5.2 Why I judge Path A' high-noise / low-signal

1. **Refinement under fixed costs** — the variable being controlled (entry timing × regime filter × etc.) is **not the binding constraint**. The binding constraint is realized PnL magnitude per trade after costs+slippage. No refinement axis directly attacks magnitude per trade unless it's a regime filter that excludes low-magnitude events at high precision (which is a possible but unlikely win)
2. **Bonferroni inflation** — every refinement adds an n_trial. DSR threshold becomes harder, not easier. The strategy needs to **clear DSR > 0.95 strict on the SAME in-sample window the strategy already failed K1 strict on with MORE trials**. This is statistically unrealistic
3. **No OOS validation** — even if A' produces a refinement that nominally clears K1+K2+K3, that refinement is **definitionally over-fit to the same in-sample window**. Phase G OOS confirmation is still required afterward. So A' is at best a step on the way to Path B; it's not a substitute
4. **Calendar cost** — 36-90h continuous CPCV runs vs Path B's 3h. Even if A' had a positive expected value (which I doubt), the opportunity cost is high

### §5.3 Why I judge Path B information-dense

1. **Single experiment, decisive question** — does prediction-level edge IC=0.866 survive on tape the strategy never saw? This is a **yes/no question with hold-out tape** and the answer **closes the costed_out_edge bucket cleanly** either way
2. **Empirically valuable regardless of outcome** — even if (probable) FAIL confirms strategy_edge clean negative, the IC fade pattern is itself reusable evidence for future edge-existence specs (calibration of IC-decay curves under WDO microstructure)
3. **Mira Round 2 designed for it** — §15.10 K3 decay sub-clause is Phase G specifically; the verdict layer is already wired (modulo F2-T5-OBS-1 short-circuit) to handle the IC_holdout vs IC_in_sample comparison

### §5.4 Why I judge Path C clean-but-incomplete

1. **Cheapest by run-cost** — true; zero new wall-time
2. **Most expensive by information-cost** — burns the cheapest experiment available
3. **Acceptable fallback** — if Dara materialization is infeasible, Path C is honest closure (Round 2 already establishes partial-falsification disposition; persisting with the disposition is an accepted research outcome per spec §0 falsifiability mandate)
4. **Sub-optimal as primary** — only path C-as-fallback after Path B precondition failure, not C-as-primary

### §5.5 Bias self-audit

- I am **biased toward fewer experiments** in general (pessimistic about p-hacking; high prior that refinement is overfitting)
- I am **biased against engine-config v1.2.0 work being scheduled fast** (5-10 day Aria/Dex/Quinn cycle is realistic; a "we'll just optimize" claim is anti-realistic)
- I am **biased FOR Path B** because OOS confirmation is the canonical pessimistic-side experiment (you don't get to dismiss costed_out_edge claims without OOS evidence)
- I am NOT biased against T002 retirement; I'm just biased against retirement WITHOUT OOS confirmation when the OOS confirmation is cheap

If council reads my §1 verdict as "hostile to A'", that's a fair characterization. I am hostile to A' as primary because it fails empirical-feasibility scrutiny under fixed costs. If council prefers A' for non-empirical reasons (e.g., "we want to learn refinement infrastructure"), that's a Pax forward-research authority decision that I do NOT pre-empt — but I would not vote A' as primary given the data.

---

## §6 Recommended conditions

If council ratifies Path B per this vote, the following conditions are recommended (Beckett surface; ratified in council aggregate):

### §6.1 Pre-conditions for Path B execution

| Cond ID | Pre-condition | Authority | Estimated effort |
|---|---|---|---|
| **C-B1** | Dara materializes hold-out parquets for 2025-07 → 2026-03 (or 2026-04 if right-edge data lands) into `data/holdout/year=YYYY/month=MM/wdo-YYYY-MM.parquet`; manifest updated with phase=`hold_out`; sha256 stamping per row | Dara (@data-engineer) | ~10-20h wall; 1-3 calendar days |
| **C-B2** | Mira authors Phase G unlock spec amendment OR ratification (per spec §15.10 unlock clause) — explicitly authorizing IC_holdout measurement against in-sample IC_in_sample=0.866; documents whether right-edge truncation (2026-03-16 vs spec 2026-04-21) is acceptable | Mira (@ml-researcher) | ~1-2h authoring |
| **C-B3** | Quinn QA gate Phase G — Anti-Article-IV Guard #3 (hold-out lock UNTOUCHED until this point) ratified as **disarmed** by Phase G unlock; new invariant for Phase G runs (e.g., "no in-sample re-fitting; predictor pipeline frozen at N7-prime HEAD"); n_trials accounting verified under Bonferroni | Quinn (@qa) | ~2-3h gate authoring |
| **C-B4** | Pax adjudicates whether Phase G runs against IS+OOS combined window OR OOS-only window (per spec §15.10 explicit rule) | Pax (@po) | ~1h authoring |

### §6.2 Beckett-side execution conditions for Path B run

| Cond ID | Execution condition | Authority |
|---|---|---|
| **C-B5** | I re-run CPCV under engine-config v1.1.0 (NO new perf round, NO engine mutation) over hold-out window — single experiment, no re-runs, no parameter sweeps | Beckett |
| **C-B6** | Predictor pipeline + cost atlas + spec yaml SHA256 IDENTICAL to N7-prime stamps | Beckett (audit) |
| **C-B7** | n_trials_used carried forward from N7-prime; no new trial added by Phase G | Beckett (audit + Mira spec §6) |
| **C-B8** | Report under `docs/backtest/T002-beckett-n8-phase-g-oos-{date}.md` per R15 canonical naming | Beckett (R15) |
| **C-B9** | Three interpretation surfaces (Phase G FAIL costed_out_clean_negative / Phase G PASS regime-shift / Phase G INCONCLUSIVE small-N or other) — Mira T7 adjudicates | Beckett (non-pre-emption) |
| **C-B10** | F2-T5-OBS-1 implementation enforcement gap (verdict-layer decay-clause emission) — recommend Dex follow-up impl per Mira spec §15.10 strict reading short-circuit BEFORE Phase G run, so verdict text is correct | Dex (@dev) post-Sable audit |

### §6.3 Anti-Article-IV invariants preserved across Path B

| Guard | Phase G compatibility |
|---|---|
| **#1** Dex impl gated em Mira spec PASS | C-B10 wires Dex follow-up appropriately gated em Mira spec §15.10 |
| **#2** NO engine config mutation at runtime | C-B5 explicitly preserves engine-config v1.1.0; no mutation |
| **#3** Hold-out lock UNTOUCHED | DISARMED by spec §15.10 Phase G unlock authorized in C-B2 (controlled disarmament; not violation) |
| **#4** Gate 4 thresholds UNMOVABLE | preserved; Phase G uses same DSR>0.95 / PBO<0.5 / IC>0 verbatim against IC_holdout |
| **#5** NO subsample | C-B1 + C-B2 ratified full hold-out window (or canonically truncated 2026-03 endpoint per Mira authority) |
| **#6** NO Gate 5 disarm without Gate 4a + Gate 4b BOTH | preserved; Path B does NOT pre-disarm Gate 5; Riven §9 HOLD #2 Gate 5 stays locked |
| **#7** NO push (Gage @devops EXCLUSIVE) | preserved; Beckett vote authoring is local-only docs work |
| **#8** Verdict-issuing protocol — `*_status` provenance | preserved; ic_holdout_status flips from 'deferred' to 'computed' upon Phase G unlock per spec §15.6 invariant body |

### §6.4 Fallback-to-Path-C conditions

If Path B preconditions C-B1..C-B4 cannot land within **14 calendar days** of council ratification, my vote shifts to Path C (retire T002):

| Trigger | Fallback action |
|---|---|
| Dara materialization slips > 14 days | Retire under partial-falsification disposition; Riven F2-T6 ledger entry per Mira Round 2 §8.1 |
| Mira spec amendment slips > 14 days | Retire same disposition |
| Quinn Phase G QA gate slips > 14 days | Retire same disposition |
| Right-edge data gap unable to be remediated AND Mira does not authorize 2026-03-16 truncation | Retire same disposition |

### §6.5 NOT in scope of Path B

- T002.7 paper-mode (Phase H) — separate story; ESC-012 does NOT pre-empt
- Riven 4-bucket attribution refinement to add `costed_out_clean_negative` post-Phase-G — Riven authority, F2-T7-equivalent (NEW task name TBD)
- Engine-config v1.2.0 perf round — separate story; not blocking Path B
- Cost-side parameter exploration (e.g., re-tuning cost atlas, alternative latency-DMA2 profile) — Pax forward-research authority, NOT pre-empted by this vote

---

## §7 Article IV self-audit

Per Constitution Article IV (No Invention) + Mira Gate 4b spec v1.1.0 §11.2 + Anti-Article-IV Guards #1-#8 (all reaffirmed Round 2 §9):

### §7.1 Trace anchoring

Every numerical claim in this vote sources to:

| Claim category | Trace anchor |
|---|---|
| N7 wall-time 181 min 50s | docs/backtest/T002-beckett-n7-2026-04-30.md §3 + §7 |
| N7-prime wall-time 188 min 12s | docs/backtest/T002-beckett-n7-prime-2026-04-30.md §3.1 + §10.3 |
| 3.0-3.1× over 60 min hard cap | N7 §7 + N7-prime §10.3 (carry-forward) |
| ~3h ± 0.3h single re-run estimate | N7 baseline + N7-prime ±3.5% consistency observation |
| 36-162h A' burden envelope | combinatorial 4-axis × 3-5-level × ~3h per-run multiplication; standard combinatorial accounting |
| Bonferroni inflation factor √(ln(17)/ln(5)) ≈ 1.32× | Mira spec §6 + Bailey-LdP 2014 §2.3 + DSR n_trials adjustment formula |
| In-sample parquets 2024-01..2025-06 present, 18 files | data/manifest.csv direct inspection (Read+Bash output §4.1) + data/in_sample/ ls direct |
| Hold-out parquets NOT materialized | data/manifest.csv phase column ∈ {warmup, in_sample}; no hold_out rows; data/holdout/ DOES NOT EXIST verified |
| Raw daily files present on D:/sentinel_data/historical/ for 2025-07..2026-03 | direct ls verification §4.2 |
| 9-10 month nearly-equivalent stat reading | Bailey-LdP 2014 §3 sample-size reproducibility floor; spec §6 minimum 250 events very far below 9-month estimate ~3500 events |
| Mira Round 2 verdict GATE_4_FAIL_strategy_edge / costed_out_edge | docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md §1 + frontmatter |
| Anti-Article-IV Guards #1-#8 | Mira spec v1.1.0 §11.2 + §15.5 + Round 2 §9 cross-reference |
| §15.10 K3 decay sub-clause Phase G | Mira spec v1.1.0 §15.10 + Round 2 §4 enforcement reading |
| Phase G unlock authorization disposition | Round 2 §8.3 verbatim "OOS confirmation step (NOT salvage path)" |
| F2-T5-OBS-1 implementation gap | Round 2 §4 + Beckett N7-prime §6.2 |
| C-B10 Dex follow-up wiring | Round 2 §8.2 verbatim |
| Calendar costs (~10-20h Dara, ~3h Beckett, 1-3 days, 14-day fallback trigger) | per-task estimates surfaced as informational; not spec-binding | <!-- estimates marked as such, no false precision -->
| Subjective probability priors §5.1 | EXPLICITLY MARKED AS SUBJECTIVE, surfaced for council audit per pessimistic-by-default disclosure protocol |

### §7.2 Invention check

- ❌ NO new statistical thresholds invented (DSR>0.95 / PBO<0.5 / IC>0 verbatim)
- ❌ NO new spec-binding rules introduced
- ❌ NO new agent authorities created (existing matrix preserved)
- ❌ NO new data-quality bucket sub-classifications proposed (costed_out_edge is Mira Round 2 nuance, not Beckett invention)
- ❌ NO simulator semantics modified (engine-config v1.1.0 preserved across all scenarios)
- ✅ Calendar-cost ranges are estimates (clearly marked as estimates) — no false precision
- ✅ Subjective probability priors §5.1 are explicitly surfaced as subjective for council audit
- ✅ Verdict label `APPROVE_PATH_B` is per-this-council aggregate framing per ESC-012 task framing — not a new spec rule

### §7.3 Authority boundary check

- ✅ Vote does NOT bind Pax forward-research authority (ESC-011 R10) — recommends, does not commit
- ✅ Vote does NOT pre-disarm Riven §9 HOLD #2 Gate 5 (Riven authority preserved per Round 2 §7 + §9 invariant #6)
- ✅ Vote does NOT amend Mira spec v1.1.0 §1 thresholds (Anti-Article-IV Guard #4 verbatim preserved)
- ✅ Vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE; no `git add` / `commit` / `push` performed by this authoring)
- ✅ Vote does NOT pre-empt Dara custodial manifest authority over hold-out materialization scheduling
- ✅ Vote does NOT pre-empt Quinn QA authoring Phase G gate
- ✅ Vote does NOT pre-empt Mira F2-T5-equivalent Phase G unlock spec authoring or amendment scope
- ✅ Anti-Article-IV Guard #8 verdict-issuing protocol respected — Beckett does not emit ML/risk/verdict labels outside simulator-feasibility domain

### §7.4 Round 2 fidelity check

- ✅ Mira Round 2 verdict `GATE_4_FAIL_strategy_edge / costed_out_edge` accepted as binding context (NOT rebutted, NOT relaxed)
- ✅ Round 2 §8.3 Phase G OOS confirmation step (NOT salvage) preserved verbatim in §1 and §6
- ✅ Round 2 §4 F2-T5-OBS-1 implementation enforcement gap forwarded as C-B10 follow-up
- ✅ Round 2 §9 invariants ALL ratified by §6.3 Path B compatibility table
- ✅ Round 1 sign-off integrity not modified (this vote does NOT alter Round 1 or Round 2 documents; surfaces forward path)

### §7.5 Self-audit verdict

**Article IV PASSED.** No invention. All claims trace. All authority boundaries respected. Round 2 fidelity preserved. Subjective preferences explicitly surfaced for council audit. Anti-Article-IV Guards #1-#8 honored.

---

## §8 Beckett cosign 2026-04-30 BRT

```
Voter: Beckett (@backtester) — Backtester & Execution Simulator authority
Council: ESC-012 — T002 strategy-fate adjudication
Constraint recap: slippage + costs FIXOS já conservadores; Path A cost-reduction OFF
Reframed paths considered:
  Path A' — Strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble) sob custos fixos
  Path B  — Phase G hold-out unlock OOS confirmation
  Path C  — Retire T002

Vote: APPROVE_PATH_B
Conditional fallback: APPROVE_PATH_C if Dara hold-out materialization slips > 14 calendar days
Path A' rejected as primary under empirical-feasibility scrutiny (36-162h burden, Bonferroni inflation, no OOS validation)

Empirical-feasibility scoring (simulator-side wall-cost vs information density):
  Path A': 36-162h wall, low information per re-run (high p-hacking prior; DSR Bonferroni inflation makes K1 strict harder)
  Path B : ~3h wall + Dara ~10-20h materialization, HIGH information density (single experiment closes costed_out_edge bucket cleanly)
  Path C : 0h wall, ZERO new information (forfeits OOS confirmation Mira Round 2 §8.3 explicitly designed for)

Hold-out tape availability check (§4):
  data/holdout/...           NOT MATERIALIZED   (Dara T002.7-prep needed)
  D:/sentinel_data/historical/WDO_*_.parquet    PRESENT 2025-07 → 2026-03 (10 months minus right-edge gap to 2026-04-21)
  Path B is technically feasible; conditional on Dara materialization sequence

Personal preference disclosure (§5):
  Subjective P(A' generates actionable evidence | no v1.2.0): 15%
  Subjective P(B generates decision-improving evidence regardless of outcome): 85%
  Subjective P(C is acceptable fallback if Dara slips): 50%
  Bias self-audit: hostile to A' as primary; not biased against retirement; biased FOR OOS confirmation step

Recommended conditions §6:
  C-B1..C-B4 pre-conditions (Dara materialization, Mira Phase G unlock spec, Quinn QA gate, Pax window adjudication)
  C-B5..C-B10 execution conditions (engine-config v1.1.0 preserved, n_trials carried forward, R15 naming, three-interpretation surface, F2-T5-OBS-1 wired before Phase G run)
  Anti-Article-IV Guards #1-#8 ALL preserved across Path B (§6.3)
  14-day fallback trigger to Path C if any precondition slips (§6.4)

Authority boundary preservation:
  NO push (Article II → Gage exclusive)
  NO Pax forward-research authority pre-emption (ESC-011 R10)
  NO Riven §9 HOLD #2 Gate 5 disarm (Riven authority)
  NO Mira spec §1 threshold mutation (Anti-Article-IV Guard #4)
  NO Dara custodial manifest pre-emption (materialization scheduling = Dara authority)
  NO Quinn Phase G QA gate authoring pre-emption
  NO Mira F2-T5-equivalent Phase G unlock spec pre-emption
  NO new spec rules, no new statistical thresholds, no engine semantics modification

Round 2 fidelity:
  Mira Gate 4b spec v1.1.0 §15.10 Phase F2 K3 narrowing preserved
  Mira Round 2 verdict GATE_4_FAIL_strategy_edge / costed_out_edge accepted as binding context
  Round 2 §8.3 "Phase G OOS confirmation step (NOT salvage)" disposition forwarded verbatim
  Round 2 §4 F2-T5-OBS-1 implementation enforcement gap captured as C-B10 follow-up

Article IV self-audit (§7): PASSED — no invention; all claims trace; subjective preferences explicitly surfaced; authority boundaries respected; Anti-Article-IV Guards #1-#8 honored.

Council fidelity:
  ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification preserved
  Mira Round 2 §1 + §8.3 + §9 honored
  Beckett N7-prime + N7 baseline empirical evidence consumed verbatim (no new measurements taken in this vote authoring)

R15 compliance: vote under canonical docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-beckett-vote.md naming.

Decision: APPROVE_PATH_B (with C-fallback per §6.4)

Cosign: Beckett @backtester 2026-04-30 BRT — ESC-012 strategy-fate ballot
```

---

— Beckett, reencenando o passado com fidelidade pessimista para Phase G 🎞️
