# T002 — Synthetic-vs-Real-Tape Attribution Post-Mortem

> **Author:** @risk-manager (Riven the Gatekeeper)
> **Authority basis:** ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C — conditions **R7** (Riven §11.5 pre-condition #7 NEW) and **R20** (synthetic-vs-real-tape audit before Gate 5 dual-sign).
> **Status:** LIVING DOCUMENT — updated each new run (N7, N8, …) until Gate 5 fires or T002 is decommissioned.
> **Binding scope:** PRE-CONDITION audit gating Riven §9 HOLD #2 Gate 5 dual-sign (capital ramp protocol RA-XXXXXXXX-X). This document does NOT authorize Gate 5 — it CLASSIFIES evidence so Gate 5 cannot fire on category-confused inputs.
> **Created (BRT):** 2026-04-29
> **Story:** T002.1.bis — `make_backtest_fn` real strategy logic (Aria Option B, factory pattern)
> **Branch:** `t002-1-bis-make-backtest-fn` @ HEAD `9997f14db6db380c408f298280c66e285a5d3cca` (F1 patch landed)

---

## §0 — Purpose

This post-mortem prevents **category errors** between three orthogonal evidentiary regimes that were conflated during the T002.0h → T002.1.bis trajectory and that, if conflated again at Gate 5, would authorize capital deployment against a backtest signal that **does not exist**:

1. **Engineering wiring** — does the pipeline mechanically work? (factory rebuild, per-fold P126, Bonferroni n_trials=5, anti-leak invariants, hold-out lock, atlas SHA wiring, determinism stamp coverage, toy-benchmark discriminator).
2. **Strategy edge** — does the actual WDO end-of-day-inventory-unwind strategy show **economically positive IC** (DSR > 0.95 / PBO < 0.5 / IC > 0) over a **real-tape distribution** that the strategy could have actually traded?
3. **Paper-mode audit** — does the live execution stack survive a real ProfitDLL feed? (latency vs DMA2 default, slippage vs Beckett cost atlas, rejection rate, RLP transitions, rollover-week behavior, fill rate, kill-switch armability under stress).

These three buckets are **serial pre-conditions** for Gate 5. **None of them substitutes another.** Bucket-1 evidence is necessary but not sufficient for bucket-2; bucket-2 evidence is necessary but not sufficient for bucket-3; bucket-3 is the final gating regime before any sizing > paper.

Cumpre:
- **§11.5 capital-ramp pre-condition #7 (NEW)** — synthetic-vs-real-tape attribution audit obrigatório.
- **ESC-011 R7** — Riven §11.5 pre-condition #7 ratified by 5/5 council.
- **ESC-011 R20** — this post-mortem authored before Gate 5 dual-sign.

---

## §1 — Classification framework (3-bucket, mutually-exclusive-by-construction)

Each Beckett iteration N{i} is classified into **at most one** of the three buckets per the rules below. A run can serve as evidence in bucket-1 even if its strategy yields zero economic signal; that does NOT promote it to bucket-2 by silence or by analogy.

### 1.1 Bucket A — `engineering_wiring`

**Question answered:** *"Does the harness compute what it claims to compute, deterministically and reproducibly, end-to-end, when fed any well-formed strategy input?"*

**Inclusion criteria (run must satisfy ALL to qualify):**
- E1. Pipeline reaches a semantically meaningful KillDecision verdict ∈ {GO, NO_GO} without TIMEOUT/MEMORY_HALT.
- E2. Determinism stamp populated for ALL provenance fields the harness owns (dataset, spec, engine_config, cost_atlas, rollover_calendar, cpcv_config, python/numpy/pandas versions, seed).
- E3. Anti-leak invariants observable at source level + test artifact (D-1 lookback per fold, factory pattern with per-fold P126 rebuild).
- E4. Bonferroni n_trials = 5 carry-forward invariant present and provenance-tracked.
- E5. Hold-out window [2025-07-01, 2026-04-21] untouched — no in-sample bleed.
- E6. Bailey-López de Prado 2014 §3 **toy benchmark discriminator** demonstrates harness can distinguish positive-edge synthetic walk from null-by-construction walk (Δ DSR > 0.10 across 5 seeds — Quinn QA owns this confirmation per ESC-011 R12).
- E7. Wall-time and RSS within budget (< 300 s, < 6 GiB).
- E8. 9 artifacts SHA-256 stamped (5 full + 4 smoke) with reproducible recomputation.

**What this bucket DOES NOT answer:**
- Whether the strategy under test has economic edge.
- Whether DSR/PBO/IC numbers reported are economically interpretable.
- Whether σ(sharpe) > 0 implies non-null distribution shape over the **real WDO regime** (it implies it only over the **synthetic walk** that was actually evaluated).
- Whether sizing parameters can be derived from observed μ/σ².

**Synthetic walk admissibility:** YES — this bucket is specifically defined over synthetic walks per Mira spec §0+§7 dual-phase carve-out. A synthetic walk that is **null-by-construction** (e.g., zero-drift random walk where μ→0 by design) IS admissible bucket-A evidence because the discriminator-power gap (toy benchmark E6) supplies the structural bridge.

**Verdict label authorized:** `HARNESS_PASS` (NEVER `GATE_4_PASS`) per ESC-011 R2.

### 1.2 Bucket B — `strategy_edge`

**Question answered:** *"Does the actual T002 end-of-day-inventory-unwind WDO strategy, when run over a real WDO tape distribution that the strategy could have plausibly traded, exhibit DSR > 0.95 and PBO < 0.5 and IC > 0?"*

**Inclusion criteria (run must satisfy ALL to qualify):**
- S1. Underlying tape consumed is **real WDO market data** (parquet/persisted Profit feed for the stipulated in-sample window 2024-08-22..2025-06-30) — NOT a synthetic walk, NOT a null-by-construction process.
- S2. ALL bucket-A criteria E1..E8 ALSO satisfied on the same run (engineering wiring is a pre-requisite, not a substitute).
- S3. Mira-spec §6 thresholds applied verbatim and met: **DSR > 0.95**, **PBO < 0.5**, **IC > 0** with Spearman 95% CI excluding zero.
- S4. Bonferroni n_trials = 5 across {T1..T5} preserved (R9 carry-forward, NON-NEGOTIABLE).
- S5. Sample size ≥ 30-50 per trial × 5 trials minimum (Bailey-LdP 2014 §3) — applies to real-tape, not synthetic.
- S6. Hold-out [2025-07-01, 2026-04-21] still untouched at point of bucket-B clearance.
- S7. Failure attribution scaffolding in place (3-bucket: data quality | strategy edge | both — per ESC-011 R9 / Mira #M5).
- S8. Cost atlas wiring identical to bucket-A clearance run (latency_dma2_profile applied per Beckett engine spec, RLP + rollover calendar consumed per Nova authority).

**What this bucket DOES NOT answer:**
- Whether the live execution stack produces fills compatible with the simulated P&L distribution.
- Whether real-time latency, slippage, queue position, or rejection patterns will preserve the in-sample edge ex-ante.
- Whether the strategy can be **operated** at the size implied by the bucket-B distribution.

**Synthetic walk admissibility:** **NO**. A synthetic walk is a **null hypothesis device**, never a strategy-edge witness. ESC-011 council 5/5 ratified this exclusion explicitly.

**Verdict label authorized:** `GATE_4_PASS` (real-tape edge-existence) — Phase F downstream story (proposed T002.2 per ESC-011 R10).

### 1.3 Bucket C — `paper_mode_audit`

**Question answered:** *"Under live ProfitDLL feed, does the actual order placement → fill → reconciliation cycle reproduce the bucket-B simulated distribution within tolerable attribution drift, sustained for ≥ 5 trading sessions without regression?"*

**Inclusion criteria (run must satisfy ALL to qualify):**
- P1. Live ProfitDLL connection consumed (not historical replay).
- P2. ≥ 5 consecutive trading sessions úteis without unexplained regression.
- P3. Slippage realized vs Beckett cost-atlas modeled within 2σ envelope.
- P4. Latency p95 within 1.5× of `latency_dma2_profile` baseline.
- P5. Rejection rate < 5% (warning threshold) sustained.
- P6. RLP policy transitions observed and reconciled to spec.
- P7. Rollover week behavior inspected if window crosses contract boundary.
- P8. Kill-switch tested for armability under at least one synthetic stress event during paper run.
- P9. ALL bucket-A AND bucket-B criteria satisfied for the model-version backing the paper run.

**What this bucket DOES NOT answer:**
- Whether the strategy survives **multiple regimes** beyond the paper window (this is post-Gate-5 monitoring).
- Whether **scaled** sizing (above paper-mode quantum) preserves the attribution profile (this is the Gate 5 → live ramp-up monitoring problem).

**Synthetic admissibility:** **NO** — by definition.

**Verdict label authorized:** `PAPER_AUDIT_PASS` — Phase G/H downstream.

### 1.4 Mutual exclusivity & ordering rule

```
bucket_A (engineering_wiring) ⊨ NECESSARY for bucket_B
bucket_B (strategy_edge)      ⊨ NECESSARY for bucket_C
bucket_C (paper_mode_audit)   ⊨ NECESSARY for Gate 5 dual-sign
```

A run cannot serve as bucket-B evidence by inheriting bucket-A clearance from itself if S1 (real tape) is not met. A run cannot serve as bucket-C evidence by inheriting bucket-B clearance from a different run unless P9 explicitly cosigns the same model-version. There is no transitive promotion across buckets.

---

## §2 — Classification ledger N5 → N6+ (current state) + forward declarations N7+ / N8+

| Run | Report § anchor | Bucket | Why this bucket | Why NOT the others |
|---|---|---|---|---|
| **N5** (smoke 2026-04-28) | `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md` | **A — `engineering_wiring`** (only — pre-redef) | Pipeline integrity probe under stub-degenerate σ=0 surfaced ESC-010 F2 problem (verdict ∈ {GO, NO_GO} mechanism workable but distribution shape collapsed under stub identity). N5 is the empirical artifact that **forced** AC8.9 redefinition (semantic scope ESC-010 F2 ratified 6/6 in council). | NOT bucket-B (stub `make_backtest_fn` is identity-zero by construction — μ and σ both null by design; nothing economic is being measured). NOT bucket-C (no live feed, no fill audit). |
| **N+1** (smoke 2026-04-28) | `docs/backtest/T002-beckett-t11-bis-smoke-report-N+1-2026-04-28.md` | **A — `engineering_wiring`** (E1 per-phase WarmUpGate fix) | T002.0h.1 successor closed §9 HOLD #2 Gate 1 — per-phase WarmUpGate + dated paths cleared the singleton/default-path binding fault that aborted N4. Gate-1 disarm = engineering correctness, not edge. | NOT bucket-B (still no real backtest_fn; still synthetic). NOT bucket-C. |
| **N6** (full + smoke 2026-04-29) | `docs/backtest/T002-beckett-n6-2026-04-29.md` §11 caveat | **A — `engineering_wiring`** (real strategy logic alive σ=0.192250; factory pattern; Bailey-LdP toy bench discriminator power preserved) | First run with **real `make_backtest_fn`** wired per Aria Option B factory pattern (T002.1.bis). σ(sharpe)=0.192250 over 225 paths with 222/225 unique values demonstrates strategy logic is alive (not stub). Toy benchmark 6/6 PASS with Δ DSR > 0.10 confirms harness can discriminate positive-edge from null. **All 12 strict-literal criteria PASS modulo cost_atlas SHA null (R16/F1).** | NOT bucket-B: the σ=0.192250 distribution is over a **synthetic walk** (`_walk_session_path` / `_walk_to_exit`) which is **strategy-logic-neutral by construction** — μ→0 is a null-by-construction artifact of the random-walk null process, NOT of the WDO market regime. **DSR = 1.5201186062197763e-05 is the NULL-BY-CONSTRUCTION FLOOR**, not an economic statement about WDO end-of-day-inventory-unwind edge. ESC-011 council ratified this exclusion 5/5. NOT bucket-C (no live feed). |
| **N6+** (re-run 2026-04-29 post-F1) | `docs/backtest/T002-beckett-n6-plus-2026-04-29.md` §3 + §6 | **A — `engineering_wiring` FINALIZED** | F1 patch wired `cost_atlas_path` + `rollover_calendar_path` to `_build_runner` (commit `9997f14`). N6+ stamp now populates `cost_atlas_sha256 = bbe1ddf7…c24b84b6d` and `rollover_calendar_sha256 = c6174922…0063fcc2`. **All 225 path-level sharpes bit-equal to N6** (σ=0.1922502285175862 recomputed); 11/13 substantive stamp fields SAME, 2/13 DIFF and both diffs are precisely the previously-null R16/C1 fields now populated. R16 / Quinn F1 / C1 CLOSED. Determinism reproducibility proven. | NOT bucket-B: synthetic walk regime UNCHANGED; F1 was pure plumbing. The underlying noise-floor null measurement DSR=1.52e-05 is bit-equal to N6 — no economic content was added or could be added by a provenance-only patch. NOT bucket-C. |
| **N7+** (Phase F future, T002.2) | NOT YET RUN | **B — `strategy_edge`** (FIRST opportunity for clearance) | Phase F replaces `_walk_session_path` / `_walk_to_exit` synthetic walks with real WDO parquet tape consumption per ESC-011 R8. Preserves factory pattern + per-fold P126 rebuild + Bonferroni n_trials=5 + cost atlas wiring + latency_dma2_profile + RLP + rollover calendar. Re-runs Bailey-LdP toy benchmark to confirm discriminator power preserved over real-tape harness. Gate 4b spec (Mira to draft per R11) freezes thresholds (R14 — DSR>0.95 / PBO<0.5 / IC>0 unmovable). | NOT bucket-A by classification but **DOES** subsume bucket-A (S2 — engineering wiring is a necessary pre-requisite). NOT bucket-C (still backtest, no live feed). |
| **N7 smoke** (Phase F 2026-04-29 — `cpcv-dryrun-N7-smoke-20260429-snapshot/` standalone snapshot + `cpcv-dryrun-auto-20260429-1ce3228230d2/smoke/` companion under full-run dir) | `docs/backtest/T002-beckett-n7-smoke-2026-04-29.md` | **A — `engineering_wiring`** (pipeline integrity PASS — strict-literal smoke) | First Phase F real-tape pipeline integrity exercise: `backtest_phase=="F"` + `parquet_root` resolved + `latency_model_active=true` confirmed verbatim in `events_metadata.json` (Beckett N7 smoke §1 + §3 + §6); 4 SHA-256 artifacts stamped (`determinism_stamp.json` `2728c386…`, `events_metadata.json` `41d2049e…`, `full_report.json` `c15eaa2d…`, `full_report.md` `516d147c…` — Beckett N7 smoke §13); R16 stamps populated (`cost_atlas_sha256` + `rollover_calendar_sha256` + 9/9 reproducibility hashes — F1 patch carry-forward preserved); Bonferroni n_trials=5 carry-forward verbatim (`trials=['T1'..'T5']`, `n_trials_used=5`); all 12 strict-literal pre-flight checks PASS; latency model active (DMA2 lognormal seeded slippage fired). | NOT bucket-B: 30-day smoke window (360 events) is **insufficient sample for K3 IC measurement** by Bailey-LdP 2014 §3 construction (≥150-250 floor not exercised, ≥30-50 per trial × 5 = floor minimum; smoke 360/5=72 events/trial distributed across 45 CPCV paths → effective per-path sample below threshold). DSR saturation at 1.0 is a **smoke-phase Φ-CDF truncation artifact**, NOT an economic statement. Beckett surfaces this verbatim as expected-and-uninformative for K3 (§1 + §6 C2). NOT yet `strategy_edge` clearance — pipeline correctness only. NOT bucket-C (no live feed). |
| **N7 full** (Phase F 2026-04-30 — `cpcv-dryrun-auto-20260429-1ce3228230d2/`, run_id `951241732d334cb6beab75ca71e26cb6`) | `docs/backtest/T002-beckett-n7-2026-04-30.md` + `docs/qa/gates/T002.6-mira-gate-4b-signoff.md` | **A — `engineering_wiring`** (sub: `IC_pipeline_wiring_gap`) | First authoritative Phase F real-tape full-window run (10 months, 3800 events × 5 trials = 19,000 trial-events; sample-size R9 EXCEEDED by 76× total floor multiple). Real-tape regime active (`backtest_phase=="F"`, `parquet_root="data/in_sample"`, `latency_model_active=true`); R16+R17 ALL PASS (9/9 reproducibility hashes populated; `cost_atlas_sha256=bbe1ddf7…c24b84b6d` + `rollover_calendar_sha256=c6174922…0063fcc2`); Bonferroni n_trials=5 verbatim (`trials=['T1'..'T5']`, `n_trials_source=docs/ml/research-log.md@8855a25e…`, matches HEAD `8855a25`). Empirical distribution non-degenerate (225/225 unique sharpes, σ=0.185048, range [-0.546, +0.614], `sortino=+0.109` sign-flip vs synthetic) — strategy logic empirically alive on real-tape regime. **HOWEVER** — per Mira T5 verdict `GATE_4_FAIL_data_quality` (`docs/qa/gates/T002.6-mira-gate-4b-signoff.md` §4): the IC measurement chain is **not wired upstream** of `compute_full_report`. `ReportConfig.ic_in_sample`/`ic_holdout` defaults `0.0` and `ic_spearman_ci95` defaults `(0.0, 0.0)` propagate verbatim through `MetricsResult` → `evaluate_kill_criteria` because the dry-run caller `scripts/run_cpcv_dry_run.py:1070` invokes `ReportConfig(seed_bootstrap=seed)` only — no IC fields supplied. `packages/vespera_metrics/info_coef.py` `ic_spearman()` + `bootstrap_ci()` are **orphan code from the dry-run path**. K3 measurement chain incomplete; falsifiability mandate (Mira spec §0) NOT exercised. Therefore bucket-A IC-pipeline wiring gap (extends bucket-A E2 envelope per Mira §6.1 spec footnote — Riven authority over taxonomy refinement). | NOT bucket-B: S2 (ALL bucket-A criteria E1..E8 ALSO satisfied on the same run) violated by IC pipeline gap — engineering wiring is a pre-requisite, not a substitute. `strategy_edge` cannot be claimed because the falsifying statistic (K3 IC) was never honestly computed. K1 DSR=0.766987 IS honestly measured (Bailey-LdP Φ-CDF wired at `report.py:481-514`) and FAILS strict spec §1 threshold `DSR > 0.95` by 0.183, but joint conjunction `K1 ∧ K2 ∧ K3` cannot be evaluated coherently while K3 is unmeasured. **T002 hypothesis NOT falsified** (per Mira T5 §1 + §4.4 verdict). NOT bucket-C (still backtest, no live feed). |
| **N8+** (Phase G/H future) | NOT YET DEFINED | **C — `paper_mode_audit`** (FIRST opportunity for clearance) | Live ProfitDLL connection; ≥ 5 trading sessions úteis; slippage/latency/rejection/RLP/rollover/kill-switch attribution per §1.3 P1..P9. Subsumes bucket-A AND bucket-B (P9). | — (terminal bucket) |

**Forward declaration — N8+ Phase F2 (post IC pipeline wiring fix):** First opportunity for clean `strategy_edge` adjudication. Phase F2 cycle dispatched per Mira T5 §6.2: F2-T0 Mira spec amendment (`docs/ml/specs/T002-gate-4b-real-tape-clearance-F2-amendment.md` defining IC computation site, predictor-vs-label pairing, bootstrap CI95 protocol, wiring contract from cpcv harness output to `ReportConfig` IC fields) → F2-T1 Dex impl (focused commit; preserves T002.1.bis factory + per-fold P126 + Bonferroni n_trials=5; no strategy logic mutation; no spec yaml mutation; no hold-out touch) → F2-T2/T3 Quinn QA (regression test that synthetic Phase E null-walk → near-zero IC + positive-edge walk → materially-positive IC, confirming discriminator preservation across IC pipeline) → F2-T4 Beckett N7-prime full re-run (same in-sample window 2024-08-22..2025-06-30; new run_id; new SHA256 stamps; toy benchmark Δ DSR > 0.10 across 5 seeds preserved on real-tape harness) → F2-T5 Mira Gate 4b re-clearance (verdict possibilities: `GATE_4_PASS` if K1+K2+K3 jointly clear; `GATE_4_FAIL_strategy_edge` if K3 honestly computes negative/near-zero AND data-quality audit clean — T002 falsified per spec §0; `GATE_4_FAIL_data_quality` recurrence if NEW data-quality finding emerges; `GATE_4_FAIL_both` per spec §7.2 Step 4) → F2-T6 Riven post-mortem update (this file). Phase F2 dispatch authority: Pax (@po) story-creation per ESC-011 R10 — likely T002.6.F2 sub-story or T002.7 if scope warrants.

**Total runs classified:** 6 (N5, N+1, N6, N6+, N7 smoke, N7 full) — **all bucket-A**. Zero bucket-B clearances. Zero bucket-C clearances. **Gate 5 cannot fire.** Per Mira T5 verdict on N7 full: T002 hypothesis NOT yet falsified (K3 unmeasured); Phase F2 cycle required before any `strategy_edge` adjudication.

---

## §3 — Capital-ramp Gate 5 dependency tree (binding)

```
                                     ┌──────────────────────────────────────────┐
                                     │         RIVEN §9 HOLD #2 GATE 5          │
                                     │  Capital ramp dual-sign (Riven + Mira)   │
                                     │       Protocol RA-XXXXXXXX-X             │
                                     └──────────────────────────────────────────┘
                                                       ▲
                                  ┌────────────────────┼────────────────────┐
                                  │                    │                    │
                  ┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
                  │  Gate 4a HARNESS_PASS │  │ Gate 4b GATE_4_PASS  │  │ Paper-mode audit ≥5d  │
                  │  (synthetic harness   │  │ (real-tape edge      │  │ (live ProfitDLL no     │
                  │  correctness)         │  │ existence — Phase F) │  │ regression — Phase G/H)│
                  │  bucket A             │  │ bucket B              │  │ bucket C               │
                  │  Mira authority       │  │ Mira authority        │  │ Riven + Tiago joint    │
                  │  ESC-011 R13/R15/R16  │  │ ESC-011 R8/R9/R11/R14 │  │ ESC-011 R7/R20 +       │
                  │  pending sign-off     │  │ NOT YET RUN           │  │ §11.5 #1..#7 cumulative │
                  └───────────────────────┘  └───────────────────────┘  └───────────────────────┘
                  ALL THREE simultaneously required to fire Gate 5.
                  Any single-leg fire (4a only / 4b only / paper only) → REJECTED by construction.
```

### 3.1 Why all three are required (not "any-of")

- **Gate 4a alone** (HARNESS_PASS only) — only proves the simulator works, not that the strategy works. Sizing under bucket-A only would be Kelly-on-noise — quarter-Kelly of zero is zero, but the framework has no μ/σ² it could parameterize anyway.
- **Gate 4b alone** (real-tape edge, no paper audit) — proves the strategy worked **historically over a clean tape**, but says nothing about whether the live execution stack reproduces it. Slippage drift, latency degradation, queue position penalties, rejection cascades are all bucket-C concerns invisible to backtest.
- **Paper audit alone** — there exists no scenario where this passes without bucket-B (P9 enforces it).

### 3.2 Single-leg fire = automatic REJECT

If any future Gate 5 sign-off attempt presents only a subset of {4a, 4b, paper}, **Riven custodial veto fires automatically**. This is hard-coded into §9 HOLD #2 Gate 5 protocol per ESC-011 R5/R6.

### 3.3 Footer requirement (cross-reference R6)

The Mira Gate 4a sign-off file (`docs/qa/gates/T002.1.bis-mira-gate-4a-signoff.md`) MUST carry verbatim footer **"Gate 4a NOT pre-disarm Gate 5"**. Without that footer = no Riven co-sign downstream — irrespective of how clean the bucket-A evidence is.

---

## §4 — Sizing implication (Riven REGRA ABSOLUTA: quarter-Kelly cap + haircut)

### 4.1 Why bucket-A evidence cannot parameterize Kelly

Riven's REGRA ABSOLUTA: `f* = μ/σ²` with quarter-Kelly cap `f ≤ 0.25 × f*`. Both `μ` and `σ²` MUST come from a distribution the strategy could have actually traded — i.e., real-tape (bucket B) at minimum.

**N6+ observed numerics:**
- σ(sharpe) over 225 paths = 0.1922502285175862 (bit-equal to N6 — synthetic walk regime)
- mean(sharpe) = -0.3007718357850226 (NEGATIVE — but this is over a null-by-construction process)
- DSR = 1.5201186062197763e-05 (noise floor)
- PBO = 0.0; IC = 0.0 with CI95 = [0, 0]

**Why NONE of these can be used for sizing:**
- σ=0.192 is the spread of the **random walk null distribution**, not of WDO end-of-day-inventory-unwind P&L. Multiplying capital × (μ/σ²) over this distribution is dividing zero by random-walk-induced variance — meaningless economically.
- mean(sharpe)=-0.30 is **negative-by-construction** when the strategy tries to predict noise; treating this as "negative edge → short the strategy" would compound the category error.
- DSR=1.52e-05 is the **null floor**, NOT a hostile finding. ESC-011 5/5 ratified this interpretation.
- IC=0.0 with CI95 [0,0] → IC test K3 fails by design, NOT by economic verdict. ESC-011 ratified that K3 fail under bucket-A is expected and non-blocking for HARNESS_PASS sign-off.

### 4.2 Kelly parametrization REQUIRES Phase F (bucket B) at minimum

Once Phase F (T002.2 N7+) produces bucket-B clearance over real WDO tape:

- `μ` = mean P&L per trade over real-tape distribution (post-cost, post-slippage per cost atlas).
- `σ²` = variance of P&L per trade over same distribution.
- Kelly fraction `f* = μ/σ²` constructible.
- Quarter-Kelly cap `f_max = 0.25 × f*` enforced.
- **PLUS** Riven haircut **30-50%** for first ~3 months of live (per persona policy: "trades-only without book, latência DMA2 unloaded, N_trials project-inflating DSR").
- Final operational fraction: `f_op ≤ 0.25 × f* × (1 - haircut)` with `haircut ∈ [0.30, 0.50]`.

### 4.3 Trade-by-trade limits + drawdown budget + kill-switch — **MUDAM materialmente** between bucket-B and bucket-C

Riven cannot freeze the following parameters until paper-mode audit (bucket C) returns:

- **Per-trade stop financeiro** — depends on σ_intraday observed live, NOT in backtest σ_intraday. Beckett cost atlas may underestimate realized intraday vol under stress regimes.
- **Per-day drawdown budget** — depends on per-trade variance × trade frequency × correlation cluster within day. Bucket-B gives expectation; bucket-C gives realization with execution friction.
- **Per-week / per-month rolling stop** — same logic compounded.
- **Kill-switch thresholds** (warning / throttle / halt / kill) — depend on live latency p95, live rejection rate, live margin utilization curve. None observable pre-paper.

**Therefore:** Riven WILL recalibrate the entire risk budget (per-trade, per-day, per-week, per-month, kill thresholds, regime filter modifiers) **between N7+ (bucket-B clearance) and Phase H (bucket-C clearance)** before any Gate 5 firing. This is a binding commitment under ESC-011 R7 and Riven §11.5 #7.

### 4.4 Capital ramp policy under bucket-A only (current state)

- **Authorized live size:** ZERO contracts. Operating at bucket-A only = engineering correctness = simulator works, nothing more.
- **Authorized paper size:** ZERO contracts (paper requires bucket-B per P9 — paper audit must back a model-version that has cleared bucket-B).
- **Authorized backtest activity:** unbounded (no live exposure = no risk budget consumed).

---

## §5 — Anti-pattern catalog (category errors to actively reject)

Each anti-pattern below has been observed or risked at least once during the T002.0h → T002.1.bis trajectory and is rejected here verbatim. Riven custodial veto fires on any future sign-off attempt that commits one of these.

### 5.1 Anti-pattern: "Gate 4 PASS over synthetic walk = strategy edge proven"

**Category error type:** Bucket-confusion (A → B silent promotion).

**Why invalid:** Synthetic walks are null hypothesis devices by construction. ESC-011 council 5/5 ratified the synthetic ↔ real-tape decomposition specifically to prevent this conflation. Promoting bucket-A evidence to bucket-B by silence would defeat the entire decomposition.

**Riven action on observation:** REJECT the sign-off attempt; require explicit bucket-B classification trace per §6 below.

### 5.2 Anti-pattern: "DSR=1.52e-05 → T002 dies / strategy is bad"

**Category error type:** Statistical malpractice (treating null floor as economic verdict).

**Why invalid:** DSR=1.52e-05 is the **noise floor** measured over a null-by-construction synthetic walk. Bailey-LdP 2014 §3 toy benchmark methodology (ESC-011 R12) requires precisely this null measurement as a discriminator power calibrator. Reading it as "strategy is bad" is reading the calibration null as the strategy verdict.

**Riven action:** REJECT any escalation predicated on this reading. Re-anchor reader on §1.1 E6 + §2 N6 row.

### 5.3 Anti-pattern: "Pipeline OK = capital ramp authorized"

**Category error type:** Sizing parametrization missing.

**Why invalid:** Capital ramp authorization requires Kelly parametrization (§4). Kelly parametrization requires real-tape μ, σ². Bucket-A pipeline correctness produces a noise-floor distribution that cannot supply μ, σ². No parametrization possible → no Kelly → no quarter-Kelly cap → no operational fraction → no authorized size > 0.

**Riven action:** REJECT. §4.4 explicit: bucket-A only ⊢ ZERO authorized live size.

### 5.4 Anti-pattern: "Toy benchmark discriminator passes = real edge implied"

**Category error type:** Toy ↔ production conflation.

**Why invalid:** The Bailey-LdP 2014 toy benchmark exists to confirm the harness can discriminate **synthetic positive-edge from synthetic null** — i.e., harness-correctness only. It says NOTHING about whether a real strategy on a real tape has real edge. Δ DSR > 0.10 is a property of the discriminator, not of the strategy.

**Riven action:** REJECT. Toy benchmark is bucket-A E6 evidence ONLY.

### 5.5 Anti-pattern: "F1 patch closed C1 = N6+ promoted to bucket B"

**Category error type:** Provenance-fix → semantic-promotion silent slide.

**Why invalid:** F1 was pure plumbing (`scripts/run_cpcv_dry_run.py` +37 -1 LoC, no strategy logic touched). Determinism stamp now carries cost_atlas_sha256 + rollover_calendar_sha256 → R16/C1/F1 closed → bucket-A criterion E2 fully satisfied. This **strengthens** bucket-A evidence, does NOT promote to bucket-B. The synthetic walk regime is bit-equal to N6 (§4.2 of N6+ report — all 225 path sharpes bit-equal).

**Riven action:** REJECT. N6+ classification stays bucket-A per §2.

### 5.6 Anti-pattern: "Paper-mode audit on bucket-A model = pre-paper for Gate 5"

**Category error type:** P9 violation (paper requires bucket-B-cleared model-version).

**Why invalid:** Running paper mode against a model whose backtest evidence is only bucket-A means the paper audit is reconciling fills against a noise-floor distribution. Slippage attribution becomes meaningless because the backtest distribution has no economic anchor to attribute against.

**Riven action:** REJECT any attempt to bypass §1.3 P9. Paper requires bucket-B-cleared model-version backing.

### 5.7 Anti-pattern: "Gate 5 fire on 4a only because 4b deferred to T002.2"

**Category error type:** Scope-decomposition → scope-collapse silent slide.

**Why invalid:** ESC-011 R5/R6/R10 explicitly: Gate 4a CANNOT pre-disarm Gate 5; Phase F is a separate future story (T002.2); footer "Gate 4a NOT pre-disarm Gate 5" is mandatory in Mira sign-off. Firing Gate 5 on 4a-only would unwind the entire 5/5 council ratification.

**Riven action:** AUTOMATIC VETO + escalation to council reconvene under new ESC-{nnn}.

### 5.8 Anti-pattern: "DSR/PBO/IC zero-with-tight-CI95 ≠ falsificação"

**Category error type:** Wiring-gap → falsification silent slide (the inverse of the §5.2 noise-floor → bad-strategy slide).

**Why invalid:** Per Mira T5 verdict on N7 full (`docs/qa/gates/T002.6-mira-gate-4b-signoff.md` §4), **IC = 0.000000 with CI95 = [0, 0]** (zero-width interval) over a non-degenerate sharpe distribution (225/225 unique values, σ=0.185, sharpe range [-0.546, +0.614]) is the **exact statistical signature of "field not wired"**, NOT of "field measured zero":

- A truly measured Spearman IC over 3800 events would virtually never hit *exactly* `0.000000`; even random noise produces a small non-zero rank correlation with sampling variance.
- A truly measured percentile-bootstrap CI95 (Efron 1979 — `info_coef.bootstrap_ci`) over 3800 paired samples would virtually never collapse to a zero-width interval `[0, 0]`; non-degenerate samples produce non-degenerate intervals.
- Both signatures collapse exactly to `ReportConfig` dataclass defaults (`float = 0.0`, `Tuple[float, float] = (0.0, 0.0)`) — i.e., the values that flow through `MetricsResult` → `evaluate_kill_criteria` when `scripts/run_cpcv_dry_run.py:1070` invokes `ReportConfig(seed_bootstrap=seed)` without supplying IC fields.
- `packages/vespera_metrics/info_coef.py` `ic_spearman()` + `bootstrap_ci()` are perfectly valid implementations (NaN guard, zero-variance guard, ±1.0 snap, percentile bootstrap) — but **orphan code from the dry-run path**: no caller invokes them along the path that produces `full_report.json`.

**Generalized pattern (Riven taxonomy refinement of bucket-A E2):** ANY metric that emerges as `value = exact-default ∧ CI = degenerate-zero-width` over a non-degenerate underlying distribution should be presumed **unwired** until proven otherwise. Falsification under Mira spec §0 falsifiability mandate REQUIRES that the falsifying statistic be **honestly measured against the data**. A statistic that is structurally a dataclass default cannot falsify — it is informationally void about the strategy.

**Why this matters for Gate 5 fence:** if a future Gate 5 sign-off attempt presents `GATE_4_FAIL` evidence whose triplet contains a zero-with-tight-CI signature, Riven custodial protocol fires:
1. Bucket re-classification triage (`data_quality` vs `strategy_edge` vs `both`) — Mira authority adjudicates per spec §7.2 decision tree.
2. NO single-leg promotion to bucket-B by silence (anti-pattern §5.1 carry-forward).
3. NO retirement of T002 hypothesis under spec §0 falsifiability — falsification requires **honest measurement**, not unwired-default measurement.
4. Phase F-prime / F2 re-run cycle dispatched after wiring fix; bucket-B clearance deferred until honest measurement is achieved.

**Riven action on observation:** REJECT any sign-off attempt that treats zero-with-tight-CI as evidence of strategy falsification. Re-anchor reader on Mira T5 §4.3 empirical-signature reasoning + §4.4 authoritative call. Dispatch Phase F2 cycle (Pax story-creation authority per ESC-011 R10).

**Anchor:** This anti-pattern was first documented at N7 full adjudication (2026-04-30 BRT) per Mira T5 verdict + Riven T6 reclassification ledger entry (`docs/qa/gates/T002.0g-riven-cosign.md` §9 HOLD #2 Gate 4b NON-DISARM section). Carries forward as binding for all future Gate 4b verdicts.

---

## §6 — Article IV trace (every classification anchored to source authority)

Each classification in §2 above traces to (a) Beckett report § anchor, (b) governance ledger entry, (c) Mira spec carve-out, (d) external Bailey-LdP / Kelly-Thorp citation. NO INVENTION — every clause is derivative.

### 6.1 N5 → bucket A

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md` — pipeline integrity probe; stub-degenerate σ=0 surfaced. |
| (b) Governance | ESC-010 F2 redefinition: AC8.9 "verdict ∈ {GO, NO_GO}" tests PIPELINE INTEGRITY, NOT strategy edge — `docs/councils/COUNCIL-2026-04-28-ESC-010-dual-track.md` 6/6 functional convergence. |
| (c) Mira spec | T002 spec v0.2.3 PRR-20260428-2 §preregistration_revisions — "Strategy edge validation is exclusive Phase F with real make_backtest_fn + per-fold P126 rebuild — separate story (T002.1.bis) gated by Riven + Mira §9 HOLD #2 cosign." (`docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` lines 252-269.) |
| (d) External | Kelly 1956 / Thorp 2006 §III — Kelly fraction undefined under null process; bucket-A regime ⊢ no parametrization possible. |

### 6.2 N+1 → bucket A

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-t11-bis-smoke-report-N+1-2026-04-28.md` — E1 per-phase WarmUpGate + dated paths, T002.0h.1 closed §9 HOLD #2 Gate 1. |
| (b) Governance | ESC-010 binding F3 commitment fulfilled by T002.0h.1 successor story — Riven §9 HOLD #2 Gate 1 disarm logged. Commit `2daedb6` (T002.0h.1 PR #7). |
| (c) Mira spec | Same PRR-20260428-2 carve-out applies — strategy edge still Phase F. |
| (d) External | — (engineering-mechanics fix, no statistical authority needed beyond bucket-A scope). |

### 6.3 N6 → bucket A

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-n6-2026-04-29.md` §11 caveat (verbatim per ESC-011 R4) + §4 12/12 strict-literal (modulo C1 cost_atlas null) + §6 toy benchmark 6/6 PASS Δ DSR > 0.10 across 5 seeds. |
| (b) Governance | ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification — `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome + §2.1 R1-R4 caveat surfacing + §2.4 R12-R14 toy benchmark + harness-correctness criteria. |
| (c) Mira spec | §0 dual-phase carve-out (T002 spec v0.2.3) — Phase E synthetic-walk pipeline integrity + Phase F real-tape edge-existence; PRR-20260428-2 lines 257-269. |
| (d) External | Bailey & López de Prado 2014 §3 — DSR/PBO methodology over CPCV distribution; toy benchmark methodology calibrates discriminator power; required to bridge synthetic-walk DSR/PBO ↔ harness-correctness signal. |

### 6.4 N6+ → bucket A (finalized)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-n6-plus-2026-04-29.md` §3 stamp delta (11/13 SAME, 2/13 DIFF = previously-null R16/C1 fields populated) + §4 non-regression metrics 12/12 PASS post-F1 + §6 R16/C1 closure formal statement + §7 anti-Article-IV self-audit. |
| (b) Governance | F1 patch commit `9997f14db6db380c408f298280c66e285a5d3cca` — `fix(t002.1.bis): wire cost_atlas_path + rollover_calendar_path in _build_runner` (Quinn QA F1 finding `docs/qa/gates/T002.1.bis-qa-gate.md` §3 Check 6). ESC-011 R16 (Quinn F1 BLOCKING for Gate 4a) CLEARED. |
| (c) Mira spec | Same §0+§7 dual-phase carve-out applies; F1 was scripts-only plumbing, did not touch spec yaml or strategy logic, so spec carve-out unchanged. |
| (d) External | Bailey-LdP 2014 reproducibility requirement — provenance fields in determinism stamp; recomputable via `hashlib.sha256(open(...).read()).hexdigest()` per §3.1 of N6+ report. |

### 6.4.1 N7 smoke → bucket A (engineering_wiring — pipeline integrity strict-literal PASS)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-n7-smoke-2026-04-29.md` §1 verdict + §3 execution metadata + §6 smoke-phase caveats (DSR saturation + IC=0 sample-insufficient) + §13 4 SHA-256 stamps. |
| (b) Governance | T002.6 spec AC11 smoke pre-flight per AC9 sample-size discipline; ESC-011 R8 (Phase F real-tape replay) + R9 (sample-size + Bonferroni); ESC-011 R16 carry-forward (R16/C1/F1 closure preserved at smoke phase via F1 patch — `cost_atlas_sha256` + `rollover_calendar_sha256` populated). |
| (c) Mira spec | §0 dual-phase carve-out; §6 sample-size floor 150-250 events × 5 trials (smoke 360/5=72 per trial near floor BUT distributed across 45 CPCV paths → effective per-path sample insufficient); §7 3-bucket attribution decision tree (Step 1 sample-size route would fire INCONCLUSIVE for K3 specifically at smoke window; Beckett surfaces this verbatim §1 verdict + §6). |
| (d) External | Bailey-LdP 2014 §3 minimum-N — smoke window does NOT exercise IC stability floor; DSR Φ-CDF saturation at 1.0 is BBLP 2014 truncation property (uninformative as economic statement, expected at smoke phase). |

### 6.4.2 N7 full → bucket A (engineering_wiring — sub: IC_pipeline_wiring_gap)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-n7-2026-04-30.md` §1 executive verdict + §3 execution metadata + §4 R16+R17 9/9 reproducibility hashes + §5 distribution diagnostics 225/225 unique non-degenerate σ=0.185 + §6 K3 IC=0/CI95=[0,0] dual-interpretation surfaced (A: clean negative falsification candidate; B: data_quality wiring artifact — Mira T5 authority adjudicates) + §8 anti-leak invariants 6/6 PASS. |
| (b) Governance | Mira T5 verdict `docs/qa/gates/T002.6-mira-gate-4b-signoff.md` `verdict: GATE_4_FAIL_data_quality` (provisional pending Phase F2; T002 NOT yet falsified) — §1 verdict justification + §3 3-bucket decision tree application Step 3 triplet failure → bucket `data_quality` + §4 IC=0 audit findings adjudicating Interpretation B CORRECT (B-confirmed via direct code inspection at `packages/vespera_metrics/report.py:185-189` defaults + `scripts/run_cpcv_dry_run.py:1070` caller wiring + repository-wide grep confirming zero IC computation site upstream of report) + §6.1 Riven T6 path bucket-A E2 envelope extension to IC-pipeline wiring + §6.2 Phase F2 re-run dispatch chain (F2-T0 .. F2-T6). ESC-011 R8/R9/R11/R14 ratification preserved. ESC-011 R16/F1 closure preserved (cost_atlas_sha256 + rollover_calendar_sha256 populated and stable across N6+ → N7 smoke → N7 full). |
| (c) Mira spec | §0 falsifiability mandate (the data MUST be allowed to refute) — REQUIRES honest measurement; N7 full violates this for K3 (unwired). §1 thresholds UNMOVABLE per Anti-Article-IV Guard #4 (DSR>0.95, PBO<0.5, IC>0); strict triplet reading carries N7 full to FAIL. §6 sample-size R9 EXCEEDED (3800 ≫ 250 by 76× total floor multiple — bucket reclassification CANNOT use sample-size route per §7.2 Step 1; falls through to Step 3 triplet adjudication → data-quality bucket per Step 3 IC-pipeline finding). §7.1 bucket `data_quality` definition extended in spirit to "engineering wiring of the measurement chain itself" per Mira T5 §3 Step 3 verdict. §11.2 Anti-Article-IV Guard #5 (NO subsample / NO short-circuit of measurement chain) HONORED — N7 full ran complete in-sample window 2024-08-22..2025-06-30; this verdict does NOT authorize partial-window re-evaluation. |
| (d) External | Bailey-LdP 2014 §3 — DSR/PBO methodology over CPCV distribution is honestly wired at `report.py:481-514`; DSR=0.766987 is real economic measurement (not falsification by §0 because joint conjunction K1∧K2∧K3 cannot be evaluated coherently while K3 unmeasured). Efron 1979 percentile-bootstrap — `info_coef.bootstrap_ci` correct implementation but orphan from dry-run path (signature `(0.0, 0.0)` zero-width CI95 confirms unwired-default origin, NOT honest measurement of true-zero IC over non-degenerate sample). Kelly 1956 / Thorp 2006 §III — Kelly fraction f* = μ/σ² requires distribution of P&L per trade with **honest IC-validated economic edge**; N7 full distribution is **not yet** a Kelly-parametrizable substrate (K3 unmeasured). |

### 6.5 N7+ → bucket B (forward declaration, NOT YET RUN)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | NOT YET RUN — to be authored at `docs/backtest/T002-beckett-n7-{date}.md` post-Phase-F execution. |
| (b) Governance | ESC-011 R8 (Phase F real-tape replay scope), R9 (sample size + Bonferroni + attribution scaffolding), R10 (separate future story T002.2), R11 (Mira drafts Gate 4b spec BEFORE Gate 4a verdict — fence-against-drift), R14 (Mira spec §6 thresholds DSR>0.95 / PBO<0.5 / IC unmovable per Anti-Article-IV Guard #4). |
| (c) Mira spec | §0+§7 Phase F empirical anchor preserved (`docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` line 152). Hold-out [2025-07-01, 2026-04-21] UNTOUCHED until Phase F authorized to consume. |
| (d) External | Bailey-LdP 2014 §3 sample-size minimum (≥ 30-50 per trial × 5 trials); Kelly 1956 / Thorp 2006 §III — first viable Kelly parametrization regime. |

### 6.6 N8+ → bucket C (forward declaration, NOT YET DEFINED)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | NOT YET DEFINED — Phase G/H deliverable. |
| (b) Governance | ESC-011 R7 + R20 (this post-mortem), Riven §11.5 #1..#7 cumulative pre-conditions for Gate 5. |
| (c) Mira spec | TBD — Phase G/H spec authored downstream of Phase F sign-off. |
| (d) External | Riven persona post-trade attribution protocol (slippage real vs Beckett, latency real vs DMA2 default, fill rate, rejection rate) — Bucket-C P3..P8. |

---

## §7 — Operational trigger (living document update protocol)

This post-mortem is **LIVING**. The classification ledger §2 + Article IV trace §6 MUST be updated **before** any of:

1. New Beckett iteration (N7, N8, …) — append row to §2; add Article IV trace subsection to §6.
2. Mira Gate 4a sign-off attempt — verify §2 row for relevant run is `bucket A` and matches sign-off classification verbatim.
3. Mira Gate 4b sign-off attempt (Phase F future) — verify §2 row for relevant run is `bucket B` and S1..S8 satisfied.
4. Gate 5 dual-sign attempt — verify (a) at least one bucket-A row, (b) at least one bucket-B row backing the model-version on paper, (c) at least one bucket-C row for the same model-version with ≥ 5 trading sessions.

### 7.1 Update authority

- **Riven** owns updates to §1 framework, §2 classification ledger, §3 dependency tree, §4 sizing implication, §5 anti-pattern catalog.
- **Beckett** authors the underlying run reports referenced in §2 / §6.
- **Mira** authors Gate 4a / 4b sign-off files; pulls classification from §2 verbatim (NO re-classification by Mira at sign-off time — Riven owns this taxonomy).
- **Quinn** confirms toy benchmark E6 evidence per §1.1 / ESC-011 R12.
- **No one else** modifies §1-§6 without Riven cosign + governance ledger entry.

### 7.2 Pre-Gate-5 audit checklist (binding)

Riven WILL execute this checklist verbatim immediately before any Gate 5 dual-sign attempt:

- [ ] §2 ledger contains ≥ 1 bucket-A row with HARNESS_PASS sign-off published?
- [ ] §2 ledger contains ≥ 1 bucket-B row with GATE_4_PASS sign-off published?
- [ ] §2 ledger contains ≥ 1 bucket-C row with PAPER_AUDIT_PASS for same model-version as bucket-B row?
- [ ] §3 dependency tree confirms simultaneous {4a, 4b, paper} satisfaction?
- [ ] Mira Gate 4a sign-off file carries verbatim footer "Gate 4a NOT pre-disarm Gate 5" (R6)?
- [ ] §4 Kelly parametrization derived from bucket-B μ, σ² (not bucket-A)?
- [ ] §4 quarter-Kelly cap applied (`f ≤ 0.25 × f*`)?
- [ ] §4 haircut 30-50% applied for first 3 months live?
- [ ] §5 anti-pattern checklist run (none of 5.1..5.7 present in sign-off rationale)?
- [ ] §6 Article IV trace complete for every classified row?
- [ ] Riven §11.5 pre-conditions #1..#7 ALL satisfied?
- [ ] Mira independent cosign present?
- [ ] Riven independent cosign present?

If ANY box unchecked → **REJECT Gate 5 sign-off attempt** + escalate via new ESC-{nnn}.

---

## §8 — Authority chain + Riven cosign

```
Authoring agent: @risk-manager (Riven the Gatekeeper)
Authority basis: ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C, conditions R7 (NEW) + R20
Council provenance: docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md (Beckett+Mira+Riven+Aria+Pax)
Companion artifact: docs/backtest/T002-beckett-n6-plus-2026-04-29.md (R16/C1 closure evidence)
Companion artifact: docs/qa/gates/T002.1.bis-qa-gate.md (Quinn F1 → patch landed `9997f14`)
Companion artifact (forthcoming): docs/qa/gates/T002.1.bis-mira-gate-4a-signoff.md (HARNESS_PASS — pending R12 + N6+ + R7 + R11 cleared)

Article II preservation: NO push, NO commit performed by Riven during authoring.
Article IV preservation: every clause traces to (a) Beckett report § anchor, (b) governance ledger entry, (c) Mira spec § carve-out, (d) Bailey-LdP 2014 / Kelly 1956 / Thorp 2006 external citation. No invention. Self-audit §9 below.
Article authority boundary: Riven authors classification taxonomy; does NOT issue Gate 4a/4b/Gate 5 sign-offs from this document. This document is PRE-CONDITION audit, not authorization. Mira retains Gate 4a/4b authority. Gage retains push authority. Tiago retains execution authority.

Riven cosign: 2026-04-29 BRT — guardião do caixa, sob ESC-011 OPTION_C 5/5 UNANIMOUS ratification.
```

---

## §9 — Anti-Article-IV self-audit

| Claim in this document | Source / trace |
|---|---|
| ESC-011 ratified 5/5 UNANIMOUS APPROVE_OPTION_C | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1 outcome table — verbatim |
| 20 conditions consolidated R1..R20 | Same resolution §2 (4 verdict labeling + 3 Gate 5 disarm fence + 4 Phase F scope + 3 toy bench + 3 Article IV + 3 governance) |
| R7 = Riven §11.5 pre-condition #7 (NEW) — synthetic-vs-real-tape audit | Resolution §2.2 R7 verbatim |
| R20 = post-mortem authored before Gate 5 dual-sign | Resolution §2.6 R20 verbatim |
| R6 footer "Gate 4a NOT pre-disarm Gate 5" mandatory | Resolution §2.2 R6 verbatim |
| F1 patch commit `9997f14` closed cost_atlas_sha256 + rollover_calendar_sha256 null | N6+ report §3 stamp delta + §6 closure statement; Quinn QA gate `docs/qa/gates/T002.1.bis-qa-gate.md` §3 Check 6 |
| N6+ σ(sharpe)=0.1922502285175862 bit-equal to N6 over 225 paths 222 unique | N6+ report §4.2 verbatim |
| N6+ DSR=1.5201186062197763e-05 bit-equal to N6 | N6+ report §4.1 verbatim |
| N6+ PBO=0.0, IC=0.0 with CI95 [0,0] | N6+ report §4.1 verbatim |
| Bailey-LdP toy benchmark Δ DSR > 0.10 across 5 seeds — 6/6 PASS | ESC-011 resolution §2.4 R12; Quinn QA `docs/qa/gates/T002.1.bis-qa-gate.md` §3 Check 2 |
| Synthetic walk null-by-construction (`_walk_session_path`/`_walk_to_exit`) | Mira spec PRR-20260428-2 lines 257-269 carve-out — strategy edge exclusively Phase F |
| Hold-out [2025-07-01, 2026-04-21] untouched | Mira spec line 153 verbatim |
| Quarter-Kelly cap = 0.25 × f* | Riven persona REGRA ABSOLUTA + Kelly 1956 / Thorp 2006 §III |
| Haircut 30-50% first 3 months live | Riven persona expertise.sizing_framework.haircut_initial verbatim |
| 5 disarm gates §9 HOLD #2 = Gate 1 (T002.0h.1 DONE) + Gate 2 (cleared by N6) + Gate 3 (cleared by N6) + Gate 4a (pending) + Gate 4b (deferred T002.2) + Gate 5 (pending) | Resolution §5 ESC-011 closure conditions §4 |
| Phase F = T002.2 separate future story (R10) | Resolution §2.3 R10 verbatim |
| Mira spec §0+§7 carve-out ratified by 5/5 council not invented by Riven | Resolution §1 outcome — Beckett+Mira votes both reference Mira spec §0 pre-existence |

**Self-audit verdict:** every classification, every threshold, every commit hash, every numeric value, every governance reference traces to a source artifact. No invention. No source modification. No push. No autocosign of Gate 5. No absorption of Mira Gate 4a authority. No mutation of spec yaml or hold-out lock. Article II preserved. Article IV preserved.

— Riven, guardando o caixa
