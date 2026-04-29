# T002 — Gate 4b Real-Tape Edge-Existence Clearance Spec (skeleton)

> **Author:** Mira (@ml-researcher) — ML/statistical authority
> **Date (BRT):** 2026-04-29
> **Status:** SKELETON — terse-but-binding fence-against-drift draft per ESC-011 R11
> **Council provenance:** ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification (Beckett+Mira+Riven+Aria+Pax) — `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md`
> **Authority chain:** Mira ML/statistical authority under ESC-011 R11 (fence-against-drift mandate — Mira drafts Gate 4b spec ANTES de Gate 4a verdict)
> **Predecessor / sibling docs:**
> - Mira spec yaml v0.2.3: `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml`
> - Mira make_backtest_fn spec: `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md`
> - Beckett N6+ report: `docs/backtest/T002-beckett-n6-plus-2026-04-29.md`
> - Quinn QA gate: `docs/qa/gates/T002.1.bis-qa-gate.md`

---

## §0 Purpose — real-tape edge-existence clearance gate

**Gate 4b is the second of two sub-gates** decomposed from the original §9 HOLD #2 Gate 4 by Council ESC-011 (5/5 UNANIMOUS APPROVE_OPTION_C). Gate 4b answers a **structurally distinct question** from Gate 4a:

| Sub-gate | Question | Scope | Phase |
|---|---|---|---|
| **Gate 4a** (issued separately at `docs/qa/gates/T002.1.bis-mira-gate-4a-signoff.md`) | "Does the CPCV harness compute DSR/PBO/IC correctly when fed a deterministic synthetic walk?" — **harness-correctness clearance** | Synthetic deterministic walk per Mira spec §7 toy benchmark methodology | Phase E (T002.1.bis perimeter) |
| **Gate 4b** (this spec) | "Over the **real WDO trade tape**, does the T002 end-of-day-inventory-unwind strategy produce statistical evidence of an actual edge per Mira spec §6 thresholds (DSR > 0.95 / PBO < 0.5 / IC decay)?" — **edge-existence clearance** | Real WDO parquet replay against the same CPCV+factory+P126+atlas chain | **Phase F** (per Mira spec §0 + Aria T0b dual-phase carve-out — separate future story T002.2 per ESC-011 R10) |

**Contrast statement (verbatim, also reproduced in Mira Gate 4a §1 caveat):** "Harness-correctness clearance over synthetic deterministic walk per Mira spec §7 toy benchmark methodology. Edge-existence clearance pending Gate 4b real-tape replay (Phase F scope). DSR=1.52e-05 is the noise-floor null measurement, NOT an economic statement about WDO end-of-day fade strategy edge."

Gate 4a clears the **engineering perimeter** (does the measurement instrument work?). Gate 4b clears the **scientific perimeter** (does what the instrument measures, against real data, constitute statistical evidence of skill?). Both are required upstream of §9 HOLD #2 Gate 5 (capital ramp dual-sign) — see §5 below.

---

## §1 Carry-forward thresholds (R14 verbatim — UNCHANGED)

Per ESC-011 R14 (Aria AC-2 + Pax §6.1) — **Mira spec §6 thresholds are UNMOVABLE per Anti-Article-IV Guard #4** and carry forward unchanged from the original Gate 4 to Gate 4b:

| Criterion | Threshold | Source (Mira spec yaml v0.2.3 + make_backtest_fn spec §6) |
|---|---|---|
| **K1 — Deflated Sharpe Ratio (DSR)** | **DSR > 0.95** (95% probability of skill given N_trials, skewness, kurtosis correction per Bailey-López de Prado 2014) | Mira spec yaml v0.2.3 §kill_criteria.k1_dsr ; Mira make_backtest_fn spec §6 |
| **K2 — Probability of Backtest Overfitting (PBO)** | **PBO < 0.5** (per Bailey et al. 2016; ideal < 0.25) | Mira spec yaml v0.2.3 §kill_criteria.k2_pbo ; Mira make_backtest_fn spec §6 |
| **K3 — Information Coefficient decay (IC)** | **IC > 0** in-sample with non-zero CI95 lower bound; decay curve documented | Mira spec yaml v0.2.3 §kill_criteria.k3_ic ; Mira make_backtest_fn spec §6 |
| **Bonferroni n_trials carry-forward** | **n_trials = 5** (T1..T5 verbatim per Mira spec §1.2) — NON-NEGOTIABLE | Mira spec yaml v0.2.3 §1.2 ; ESC-011 R9 |

**Anti-drift assertion (R14 verbatim):** "Gate 4b criteria (Mira spec §6 thresholds DSR>0.95 / PBO<0.5 / IC) UNCHANGED; thresholds unmovable per Anti-Article-IV Guard #4. Gate-bind mechanism for Gate 4b deferred to Phase F architectural review." — see §5 deferred clause below.

---

## §2 Sample-size mandate (R9 — Bailey-LdP §3 minimum-N rationale)

Per ESC-011 R9 (Mira ballot #M5) — sample-size for Gate 4b is **NON-NEGOTIABLE**:

| Parameter | Mandate | Rationale |
|---|---|---|
| **Events per trial** | **≥ 30-50 events per trial** | Bailey-López de Prado 2014 §3 — minimum-N for stable Sharpe Ratio variance estimation under non-normal returns; below ~30 events the higher-moment correction (skew, kurtosis) becomes unreliable and DSR collapses to a coin-flip |
| **Trials** | **5 trials (T1..T5 per Mira spec §1.2)** | Bonferroni n_trials = 5 carry-forward — prevents trial-count drift undermining the multiple-testing penalty |
| **Total events** | **≥ 150-250 total events** (= 5 × 30-50) | Floor for the joint distribution of Sharpe across trials; below this floor PBO becomes degenerate (not a meaningful overfitting probability, just a discrete histogram of too-few paths) |
| **Bonferroni n_trials = 5** | **NON-NEGOTIABLE** | ESC-011 R9 verbatim; no trial-count inflation allowed to cherry-pick a favourable Bonferroni adjustment |

**Citation anchor:** Bailey, D. H., & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality." *Journal of Portfolio Management*, 40(5), §3 (minimum-N requirement and selection-bias correction). Reproduction harness already shipped at `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6/6 PASS — Quinn QA §3 Check 2; Beckett N6+ §4.4) — same harness MUST re-run on real-tape Gate 4b output to confirm discriminator power Δ DSR > 0.10 across 5 seeds is preserved.

---

## §3 Failure attribution scaffolding (R9 3-bucket)

Per ESC-011 R9 — every Gate 4b run that fails to clear the §1 thresholds **MUST classify the failure** into one of three mutually-exclusive buckets, recorded in the Gate 4b run report and in `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (Riven authoring authority per ESC-011 R7 + R20):

| Bucket | Definition | Diagnostic signature |
|---|---|---|
| **`data_quality`** | Failure attributable to real-tape ingestion / replay engineering (parquet schema drift, RLP miscoding, rollover-gap mishandling, latency model misapplied, cost atlas miswired) | (a) Toy benchmark Δ DSR > 0.10 still PASS on synthetic walk under same code path (harness still discriminates); (b) trade-by-trade parity check vs reference replay shows unexpected fills/PnL deltas; (c) calendar/RLP audit reveals gaps |
| **`strategy_edge`** | Failure attributable to the strategy itself (no economic edge in the WDO end-of-day fade hypothesis under realistic costs+latency) | (a) Toy benchmark Δ DSR > 0.10 PASS (harness OK); (b) data-quality audit clean; (c) DSR/PBO/IC measurements stable across seeds and converge to a no-edge null distribution → falsification per Mira spec §7 K1/K2/K3 |
| **`both`** | Failure with mixed signature — data-quality issues AND strategy-edge concerns are jointly present and cannot be cleanly separated by single re-run | Requires sequential re-run after addressing the data-quality side first (closure of `data_quality` bucket clears the line of sight to the `strategy_edge` verdict) |

**Mandate:** Gate 4b verdict text MUST name the failure bucket explicitly when applicable. A failed Gate 4b that does not cleanly classify is **inconclusive**, not a falsification — see §6 Article IV trace.

---

## §4 Mandatory Gate 4b milestones (R8 verbatim — Beckett N7+ pre-conditions)

Per ESC-011 R8 (Beckett ballot #3) — Phase F story scope MUST include Beckett N7+ real-tape replay with **all six** of the following milestones. Each is a hard pre-condition for issuing a Gate 4b verdict:

- **(a) WDO parquet tape consumption replacing `_walk_session_path`/`_walk_to_exit` synthetic walks.** The synthetic deterministic seeded walk used in T002.1.bis (per `cpcv_harness.py:298-322` Article IV trace block) is **REMOVED** from the strategy path in Phase F. Real WDO trade tape (parquet) is consumed event-by-event by the same `make_backtest_fn` factory, with triple-barrier walks executed against actual tick prices. The factory contract and the in-fold P126 rebuild interface are PRESERVED — only the price source changes from synthetic to real.
- **(b) Preserved factory pattern + per-fold P126 rebuild + Bonferroni n_trials=5.** All Aria §I.1-§I.6 invariants from T002.1.bis carry forward unchanged: `backtest_fn_factory` mutual-exclusivity (`engine.py` ValueError when both/neither), per-fold P126 rebuild via `_build_daily_metrics_from_train_events(train_events, seed_anchor=split.path_id)`, `as_of_date = min(test_events.session)` D-1 anti-leak invariant, T1..T5 trial table verbatim per Mira spec §1.2.
- **(c) Cost atlas wiring identical to N6+.** Same `cost_atlas_path = docs/backtest/nova-cost-atlas.yaml` (atlas v1.0.0 raw SHA `bbe1ddf7898e79a7…c24b84b6d`, LF-normalized SHA `acf449415a3c9f5d…` per dual-hash semantics described in Beckett N6+ §3.1) and same `BacktestCosts.from_engine_config` consumption via closure capture. Cost formula `(exit-entry)*sign*1*WDO_MULTIPLIER - 2*1*(brokerage + exchange_fees) - slippage` (Mira spec §5.3 + Riven §11 audit verbatim) UNCHANGED. F1 patch (commit `9997f14`) ensures `cost_atlas_sha256` and `rollover_calendar_sha256` continue to surface in `determinism_stamp.json` for full audit trail.
- **(d) `latency_dma2_profile` applied to slippage estimation per Beckett engine spec.** Phase F replay MUST consume the latency profile (DMA-2 microstructure latency proxy) when computing slippage on real-tape fills — synthetic walk did not exercise this path; Phase F does. Latency profile source: `docs/backtest/engine-config.yaml` (`latency_profile_ref` block, SHA-locked).
- **(e) RLP policy + rollover calendar consumption per Nova authority.** Real tape contains RLP (last-trade) prints that must be filtered/handled per Nova authority's RLP policy (defined in `docs/backtest/engine-config.yaml`); rollover calendar (`config/calendar/2024-2027.yaml`, raw SHA `c6174922dea303a3…0063fcc2`) MUST be consumed for session-day filtering and contract-roll handling. Both behaviours are ALREADY wired post-F1 (per Beckett N6+ §6 R16/C1 closure) — Phase F inherits the wiring.
- **(f) Re-run Bailey-López de Prado 2014 toy benchmark on real-tape harness.** Gate 4b is NOT issued until `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (or its Phase-F-equivalent if test fixtures evolve) re-runs against the real-tape pipeline confirming **discriminator power Δ DSR > 0.10 across 5 seeds is preserved**. This is the harness-correctness witness on the new tape source — it certifies that any edge / no-edge measurement Gate 4b reports is signal, not harness artefact.

**All six milestones are jointly required.** Skipping any one → Gate 4b inconclusive.

---

## §5 Gate 4b cannot pre-disarm Gate 5 alone — both 4a AND 4b required (R5 reaffirmed)

Per ESC-011 R5 (Beckett #2 + Riven C-R2 + Pax §6.3) and R6 (Riven C-R2):

> **§9 HOLD #2 Gate 5 (capital ramp protocol RA-XXXXXXXX-X dual-sign) requires Gate 4a (HARNESS_PASS) AND Gate 4b (this spec) BOTH PASS as upstream pre-conditions. Sequential serial dependency: 4a AND 4b → 5. No Gate 5 firing on either Gate 4a alone OR Gate 4b alone.**

Reaffirmed verbatim here as §5 of this spec to fence-against-drift: Gate 4b carries the **edge-existence half** of the original Gate 4 mandate; it does not absorb or supersede Gate 4a's harness-correctness half. Riven's §9 HOLD #2 Gate 5 disarm ledger (separate doc, Riven authority) consumes BOTH gates as conjunction — neither alone is sufficient.

**Gate-bind mechanism for Gate 4b (i.e., precisely which §9 HOLD #2 sub-gate Gate 4b disarms in the disarm ledger, and how it composes with Gate 4a, and what record-keeping format the disarm carries) is DEFERRED to Phase F architectural review per Aria AC-2** (ESC-011 vote condition AC-2 verbatim). This skeleton spec intentionally does not pre-empt that architectural review — fence-against-drift means we lock the **scientific contract** here (thresholds, sample size, attribution, milestones, Gate-5 conjunction) without prematurely committing to the **disarm-ledger plumbing**.

---

## §6 Article IV trace policy

Every Gate 4b verdict claim — issued in a future per-run sign-off artifact at (suggested) `docs/qa/gates/T002.2-mira-gate-4b-signoff.md` — MUST trace to the following anchors. NO INVENTION:

| Verdict claim category | Required trace anchors |
|---|---|
| Threshold values (DSR > 0.95, PBO < 0.5, IC > 0) | Mira spec yaml v0.2.3 §kill_criteria + Mira make_backtest_fn spec §6 + this spec §1 |
| Sample-size sufficiency (≥ 30-50 per trial × 5 = ≥ 150-250 total) | Bailey-López de Prado 2014 §3 + this spec §2 + ESC-011 R9 |
| Bonferroni n_trials=5 | Mira spec yaml v0.2.3 §1.2 + ESC-011 R9 + this spec §1 |
| Failure attribution (data_quality vs strategy_edge vs both) | This spec §3 + Riven post-mortem `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (Riven authoring authority per ESC-011 R7+R20) |
| Milestone clearance (a-f) | Beckett N7+ run report (separate Phase F artifact, Beckett authority) + this spec §4 + ESC-011 R8 verbatim |
| Toy-benchmark discriminator preservation Δ DSR > 0.10 across 5 seeds | `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (Phase-F real-tape re-run) + Bailey-López de Prado 2014 §3 + this spec §4(f) + ESC-011 R12 |
| Gate-5 conjunction non-pre-emption | This spec §5 + ESC-011 R5+R6 + Riven §9 HOLD #2 Gate 5 ledger |
| ESC-011 ratification provenance | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` 5/5 UNANIMOUS APPROVE_OPTION_C |

**Anti-Article-IV Guards (preserved unchanged from Mira spec):**
- Guard #4 (Gate 4 thresholds UNMOVABLE) — explicit reaffirmation in this spec §1.
- Guard #6 (NO enforce Gate 5 disarm sem Gate 4) — explicit reaffirmation in this spec §5.
- No invented thresholds. No invented milestones. No invented attribution buckets. Every clause of this skeleton has a source anchor above.

---

## §7 Self-audit (Article IV)

| Claim in this spec | Source anchor (verified) |
|---|---|
| ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome table — 5 voters, 5 APPROVE_OPTION_C ballots, individual ballot artifacts referenced |
| 20 conditions ratified (R1-R20) | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §2 consolidated table — R-IDs explicitly cited inline (R5, R6, R7, R8, R9, R10, R11, R12, R14, R20) where used in this spec |
| Gate 4 → Gate 4a + Gate 4b decomposition | ESC-011 §1 outcome statement verbatim ("Hybrid Gate 4a (synthetic harness-correctness) + Gate 4b (real-tape edge-existence)") |
| DSR > 0.95 / PBO < 0.5 / IC thresholds | Mira spec yaml v0.2.3 §kill_criteria + Mira make_backtest_fn spec §6 §kill_criteria sub-block |
| Bonferroni n_trials = 5 (T1..T5) | Mira spec yaml v0.2.3 §1.2 + ESC-011 R9 verbatim |
| Bailey-LdP 2014 §3 minimum-N rationale | Bailey & López de Prado 2014, *Journal of Portfolio Management* 40(5), §3 — citation only (paper not embedded in repo); reproduction test harness shipped at `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` |
| F1 patch wiring (commit `9997f14`, atlas+rollover SHAs populated) | Beckett N6+ report §3 + §6 |
| latency_dma2_profile / RLP policy / rollover calendar wiring | `docs/backtest/engine-config.yaml` (referenced; not modified by this spec) + Beckett N6+ §3.1 dual-hash discussion + §6 R16/C1 closure |
| Cost formula `(exit-entry)*sign*1*WDO_MULTIPLIER - 2*1*(brokerage + exchange_fees) - slippage` | Mira make_backtest_fn spec §5.3 + Riven §11 audit + Quinn QA §3 Check 1 (cited verbatim there) |
| Phase F as separate future story T002.2 | ESC-011 R10 (Pax §6.4) verbatim |
| Gate-bind deferral to Phase F architectural review | ESC-011 R14 (Aria AC-2 second sentence) verbatim |

**Self-audit verdict:** every clause traces. NO INVENTION. Skeleton is binding-but-terse — full Phase F implementation spec to be authored as part of T002.2 story creation (Pax authority, Mira ML co-authoring) when that story enters the SDC.

---

## §8 Authority chain + cosign

```
Author: Mira (@ml-researcher) — ML/statistical authority, ESC-011 R11 fence-against-drift mandate
Council provenance: ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C (Beckett+Mira+Riven+Aria+Pax)
Article IV: every clause traces to (a) Mira spec yaml v0.2.3 / Mira make_backtest_fn spec §-anchor, (b) ESC-011 R-ID, (c) Bailey-LdP 2014 / AFML 2018 citation, or (d) Beckett N6+ / Quinn QA artifact §-anchor — verified §7 above
Article II: no push (this is a write-only skeleton draft; Gage authority preserved for any future commit)
Anti-Article-IV Guards: #4 (thresholds UNMOVABLE) + #6 (Gate-5 conjunction) preserved verbatim
Scope discipline: Phase F implementation NOT pre-empted (separate T002.2 story per ESC-011 R10); Riven Gate 5 authority NOT pre-empted (§5 conjunction reaffirmed)
Cosign: Mira 2026-04-29 BRT
```

— Mira, mapeando o sinal 🗺️
