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

### §2.R2 — Round 2 update (N7-prime, Phase F2 IC pipeline post-fix; 2026-04-30 BRT)

> **Section type:** APPEND-ONLY Round 2 update post Mira F2-T5 verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` — `verdict: GATE_4_FAIL_strategy_edge`, sub-classification `costed_out_edge`; supersedes Round 1 `GATE_4_FAIL_data_quality` per Mira spec v1.1.0 §15 append-only revision discipline). NO MUTATION to §1-§2 Round 1 ledger rows above this break (Round 1 N7 smoke + N7 full rows preserved verbatim — both correctly classified `bucket A engineering_wiring` (sub: `IC_pipeline_wiring_gap`) under Round 1 evidence). Round 2 entries APPENDED below; Round 2 supersedes Round 1 N7 full bucket attribution **at the verdict-disposition layer** while **preserving Round 1 ledger entry integrity** for governance audit-trail provenance per Mira spec §15 append-only revision invariant.

#### §2.R2.1 — N7-prime classification ledger row (NEW Round 2; bucket B `strategy_edge` sub `costed_out_edge`)

| Run | Report § anchor | Bucket | Why this bucket | Why NOT the others |
|---|---|---|---|---|
| **N7-prime** (Phase F2 full 2026-04-30 — `data/baseline-run/cpcv-dryrun-auto-20260430-1ce3228230d2/`, run_id `3c0b25cadf284544ae33518921c255e4`; run-time HEAD `2445bae`; post-merge HEAD `0903eaf` PR #14 merged main 2026-04-30 12:36 BRT) | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` + `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` | **B — `strategy_edge` sub: `costed_out_edge`** (Mira F2-T5 Round 2 nuance per spec v1.1.0 §1 + §5.2 evidence matrix) | First authoritative Phase F2 real-tape full-window run with IC pipeline wiring CLOSED structurally per F2-T1 commit `2445bae` + PR #14 main `0903eaf`. K3 in-sample PASS strict per §15.10 Phase F2 binding clause: IC=0.866010 + CI95 [0.865288, 0.866026] tight (width 0.000738 over n=10000 PCG64 paired-resample bootstrap seed=42; NON-degenerate vs Round 1 zero-width CI95 [0,0] sentinel signature). K1 (DSR=0.766987) honestly measured strict FAIL by 0.183 below 0.95 threshold (Bailey-LdP 2014 §3 Φ-CDF wired at `packages/vespera_metrics/report.py:481-514` — IDENTICAL to Round 1; bit-equal sharpe distribution preserved across F2 amendment boundary per Beckett §5.1). K2 (PBO=0.337302) PASS strict. Hit_rate=0.4966981 (essentially break-even at trade level); sharpe_mean=+0.046251 (positive small-magnitude); sharpe_std=0.185048 (non-degenerate); 225/225 unique sharpe values. The IC=0.866 + hit_rate=0.497 + DSR=0.767 trio is the **canonical `costed_out_edge` signature** per Mira F2-T5 §5.2 four-cell evidence matrix: prediction-level edge strong (rank-correlation rules out leakage hypothesis because hit_rate would track IC near saturation under leakage; rules out spurious correlation because CI95 width 0.000738 + sample 3800 dwarfs floor); CPCV path-level realized Sharpe distribution does NOT survive the cost+friction+early-exit (triple-barrier) layer at the deployable 0.95 strict bar (Anti-Article-IV Guard #4 UNMOVABLE per ESC-011 R14). All bucket-B inclusion criteria S1..S8 satisfied: S1 real WDO market data ✅ (`backtest_phase: F`, `parquet_root: data/in_sample`, 18 monthly parquets verified, 3800 events); S2 ALL bucket-A criteria E1..E8 satisfied on the same run ✅ (Round 2 closes the Round 1 IC-pipeline-wiring gap that violated E2 envelope extension); S3 Mira spec §6 thresholds applied verbatim (DSR strict FAIL by 0.183 = honest measurement against UNMOVABLE bar) ✅; S4 Bonferroni n_trials=5 verbatim (`trials=['T1'..'T5']`, `n_trials_used=5`, `n_trials_source=docs/ml/research-log.md@c84f7475…`) ✅; S5 sample size 3800 events ≫ 250 floor (76× headroom; ≫ 30 minimum per §15.7 dedup invariant) ✅; S6 hold-out [2025-07-01, 2026-04-21] UNTOUCHED ✅ (Anti-Article-IV Guard #3 UNMOVABLE; `ic_holdout_status='deferred'` per §15.6); S7 failure attribution scaffolding in place ✅ (this Round 2 entry); S8 cost atlas wiring identical to bucket-A clearance run ✅ (`engine_config_sha256=ccfb575a…` IDENTICAL Round 1 vs Round 2; `cost_atlas_sha256=bbe1ddf7…` IDENTICAL; `dataset_sha256=ff9b5058…` IDENTICAL — F2 fix is purely post-hoc compute over identical CPCV path-PnL). | NOT bucket-A Round 2: bucket-A `IC_pipeline_wiring_gap` sub-classification opened Round 1 is **CLOSED** by Round 2 evidence per Mira F2-T5 §6.4 + §8.1 — IC measurement chain demonstrably honest (CI95 non-degenerate over n=10000 paired-resample; verdict layer did NOT raise `InvalidVerdictReport` per spec §15.6 invariant body; Anti-Article-IV Guard #8 in-sample channel honored). NOT bucket B clean negative `strategy_edge` (would require IC_in_sample ≤ 0 OR CI95_lower ≤ 0 — NOT observed; IC=0.866 is far from clean negative). NOT bucket-A `data_quality` recurrence: Round 1 wiring-gap channel CLOSED structurally; F2-T5-OBS-1 verdict-layer decay-clause enforcement gap surfaced (Mira F2-T5 §4 + §8.2 — Dex follow-up scope) does NOT contaminate in-sample channel verdict. NOT bucket-C: still backtest, no live feed; Phase G holdout unlock authorized as **OOS confirmation step** under `costed_out_edge` hypothesis (NOT salvage path — K1 strict bar UNMOVABLE forecloses Gate 4b PASS at Phase F2). Phase H paper-mode is T002.7 future. |

#### §2.R2.2 — Round 1 N7 full reclassification disposition (governance integrity preserved)

**Round 1 N7 full ledger row (line ~126 above) is NOT MUTATED.** Round 1 attribution `bucket A engineering_wiring (sub: IC_pipeline_wiring_gap)` was honestly classified per the wiring-gap evidence at the time (Mira T5 Round 1 §4.4 authoritative call: IC=0 with CI95=[0,0] = unwired-default signature, NOT honest measurement of true-zero IC). Round 2 SUPERSEDES Round 1 at the verdict-disposition layer for the **same underlying CPCV path-PnL distribution** (`dataset_sha256=ff9b5058…` IDENTICAL across F2 amendment boundary per Beckett §3.3 + §5.1 — bit-equal sharpe distribution proves F2 fix is purely post-hoc compute), but Round 1 ledger row is preserved verbatim per Mira spec v1.1.0 §15 append-only revision invariant + governance audit-trail provenance discipline. Both entries co-exist: Round 1 = "honest classification under Round 1 evidence (IC unmeasured)"; Round 2 = "honest classification under Round 2 evidence (IC measured at 0.866; cost-eroded edge)". Future readers MUST consult Round 2 row for current bucket disposition; MAY consult Round 1 row for historical wiring-gap diagnosis context (and §5.8 anti-pattern signature reference — Round 1 zero-with-tight-CI is the canonical exemplar).

#### §2.R2.3 — Refined bucket framework Round 2: `costed_out_edge` sub-classification within `strategy_edge`

Mira F2-T5 §1 + §5.2 authority introduces **`costed_out_edge`** as a sub-classification WITHIN the bucket B `strategy_edge` envelope (§1.2 above). Riven custodial endorsement Round 2:

**Definition (`costed_out_edge`):** A failure regime where the predictor-label rank-correlation Information Coefficient over CPCV events is **strong** (IC_in_sample > 0 with CI95_lower > 0; in N7-prime concretely IC=0.866 with CI95 [0.865, 0.866]) BUT the realized CPCV path-level Sharpe distribution does **NOT** survive the cost-and-friction layer at the deployable strict threshold (DSR > 0.95 per Mira spec §1; in N7-prime concretely DSR=0.767 strict FAIL by 0.183). The diagnostic key is the **hit_rate paradox**: hit_rate ≈ 0.5 (trade-level break-even) coexists with high IC. This signature is **inconsistent with leakage** (which would force hit_rate to track IC near saturation) and **inconsistent with spurious correlation** (CI95 narrow + sample size 3800 ≫ floor). The signature IS consistent with: predictor correctly ranks forward-return label sign; magnitude of forward return is insufficient to overcome triple-barrier early exits + cost atlas (broker fees + exchange fees + slippage_latency_pts) + DMA2 latency profile slippage at the level needed to produce hit-rate-realized PnL distribution Sharpe ≥ 0.95 strict bar.

**Distinction from clean `strategy_edge` (per §1.2 authorized verdict label):**

| Failure regime | IC_in_sample | CI95_lower | Hit_rate | DSR | Diagnostic |
|---|---|---|---|---|---|
| **Clean `strategy_edge` (no signal at all)** | ≤ 0 OR near-zero non-degenerate | ≤ 0 | ≈ 0.5 | < spec | Predictor has no rank-power; T002 hypothesis fully falsified per spec §0 mandate |
| **`costed_out_edge` (signal exists; eroded by costs)** | > 0 strong (e.g., 0.866) | > 0 strict (e.g., 0.865) | ≈ 0.5 | < spec but finite-positive | Predictor ranks forward-returns correctly; cost-and-friction layer consumes the deployable Sharpe |
| **Round 1 wiring-gap signature (unmeasured)** | exactly 0.0 (default) | 0.0 (zero-width CI) | n/a (or tracks; here was ≈ 0.5 incidentally) | partial | Field-default propagation; NOT honest measurement; falsification cannot fire per spec §0 (§5.8 anti-pattern) |

**Implication for thesis falsifiability under spec §0 mandate ("the data MUST be allowed to refute"):** `costed_out_edge` is **provisional, NOT permanent** falsification of T002 hypothesis. Per Mira F2-T5 §5.3:

- Q4 K1 kill criterion `DSR < 0`: observed DSR=0.767 > 0 → **NOT triggered** (kill is strict-negative; finite-positive does not fire kill)
- Q4 K2 kill criterion `PBO > 0.4`: observed PBO=0.337 < 0.4 → **NOT triggered**
- Q4 K3 kill criterion `IC_holdout < 50% IC_in_sample`: Phase G holdout locked (Anti-Article-IV Guard #3 UNMOVABLE) — **deferred, cannot test in Phase F2**
- Q4 K4 kill criterion `DD > 3σ budget Riven em paper`: Phase H paper-mode — **deferred, cannot test in Phase F2**

The thesis Q4 kill triplet does **NOT** refute T002 hypothesis. The Mira Gate 4b spec v1.1.0 §1 strict bar (`DSR > 0.95`) is the **deployment gate**, NOT the **thesis falsification gate**. Two distinct bars:

- **Thesis falsified** (clean `strategy_edge` with IC ≤ 0) → retire T002 entirely; redirect research path
- **Deployment gate failed** (`costed_out_edge`) → T002 cannot deploy at this iteration; partial-edge story remains in scope; cost-reduction R&D path OR Phase G OOS confirmation may be warranted

**Pure refutation under spec §0 falsifiability is PROVISIONAL Round 2, NOT permanent.** Pax forward-research authority (ESC-011 R10) adjudicates whether the path forward is (a) Phase G OOS confirmation under `costed_out_edge` hypothesis (T002.7+ future story), (b) cost-side parameter exploration before Phase G unlock (Phase F3 future — broker fee renegotiation / cost atlas re-tuning / triple-barrier widening / latency-DMA2 alternative profile / entry-window narrowing — preserves hold-out lock), or (c) T002 retirement at Phase F2 + redirect to alternative thesis. Riven Round 2 does NOT pre-empt Pax decision; surfaces three options consistent with `costed_out_edge` evidence per Mira F2-T5 §8.3.

#### §2.R2.4 — Total runs classified Round 2 update

**Total runs classified post Round 2:** 7 (N5, N+1, N6, N6+, N7 smoke, N7 full Round 1 = bucket A; N7-prime Round 2 = bucket B `strategy_edge` sub `costed_out_edge`). 1 bucket-B classification (Round 2 — N7-prime). Zero bucket-C clearances. **Gate 5 cannot fire** — single-leg Gate 4b sub-bucket classification at `costed_out_edge` is NOT `GATE_4_PASS`; R5/R6 conjunction `Gate 4a HARNESS_PASS ∧ Gate 4b GATE_4_PASS ∧ paper-mode audit` UNSATISFIED (K1 strict FAIL on Gate 4b leg per Mira F2-T5 spec v1.1.0 §1 decision rule + Anti-Article-IV Guard #4 UNMOVABLE). Capital ramp barrier remains LOCKED post Round 2; Riven §9 HOLD #2 Gate 4b NON-DISARM Round 2 ledger entry recorded in companion file `docs/qa/gates/T002.0g-riven-cosign.md` §9 HOLD #2 Round 2 section (appended same authoring window).

### §2.R3.1 — Round 3.1 update (N8 synthetic-fallback-bug + N8.2 PROPER Phase G OOS confirmation; T002 RETIRE per ESC-013 §5(c); 2026-05-01 BRT)

> **Section type:** APPEND-ONLY Round 3.1 update post Mira F2-T9.1 FINAL verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` — `verdict: GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed`; sub-classification `costed_out_edge_oos_confirmed_K3_passed`; ESC-013 §5 outcome (c) match; supersedes Round 3 INCONCLUSIVE_pending_phase_g_proper sign-off + Round 2 `costed_out_edge` sign-off + Round 1 `data_quality` sign-off). Per Mira spec v1.2.0 §15 append-only revision discipline: §1-§6 prior content (Round 1 + Round 2 entries) preserved verbatim above; Round 3.1 entries APPENDED here. Round 3.1 is the **FINAL** Gate 4b adjudication round of the T002 chain — T002 RETIRE per ESC-013 §5(c) outcome (c) action: "T002 retire with refined diagnostic; cost reduction R&D path Path A explicitly OFF per user constraint; Path C (ESC-012 fallback) auto-trigger for T002.7 close ceremony".

#### §2.R3.1.1 — N8.1 ledger row (synthetic-fallback bug; Phase G unlock caller gap)

| Run | Report § anchor | Bucket | Why this bucket | Why NOT the others |
|---|---|---|---|---|
| **N8.1** (Phase G attempted 2026-04-30, synthetic-fallback bug; artifact run, ~12s wall) | (no Beckett report — bug-killed run; artifact disposition only) | **A — `engineering_wiring`** sub: `phase_g_unlock_caller_gap` (Riven taxonomy refinement Round 3.1) | First attempt to invoke Phase G OOS unlock revealed a **caller-side closure gap**: the closure-phase `Literal` enum at the call site (`scripts/run_cpcv_dry_run.py` pre-R18) did not include `"G"` as an admissible phase value. When the harness was invoked with `--phase G`, the closure-Literal mismatch caused silent fall-through to the synthetic walk path (`_walk_session_path` / `_walk_to_exit`) instead of consuming the holdout-window parquet. Wall-time ~12s (synthetic walk completes orders of magnitude faster than real-tape CPCV — clear smoke signal of fall-through). Result: artifact run with synthetic walk regime instead of Phase G real-tape OOS measurement. ESC-013 R18 mandate prescribed Dex caller-wiring fix (~5-30 LoC: extend phase Literal to `{"E", "F", "G"}` + propagate `holdout_locked=False` only for phase=="G"). Caller wiring closed structurally per N8.2 successor run; N8.1 run dir disposition: artifact-tagged, NOT a bucket-B candidate (synthetic walk regime by construction; null-by-construction process per §1.1 admissibility). | NOT bucket-B: synthetic walk regime is null-by-construction per §1.1 admissibility; ESC-011 council 5/5 ratified this exclusion explicitly. NOT bucket-C: no live feed. NOT a Round 3 candidate verdict input (Mira Round 3 INCONCLUSIVE adjudication consumed the pre-fix N8 artifact under F-protocol-over-holdout-window semantics; N8.1 wall-time ~12s is the Phase-G-attempted-but-fell-through diagnostic signature). |

#### §2.R3.1.2 — N8.2 ledger row (PROPER Phase G OOS unlock; bucket B sub `costed_out_edge_oos_confirmed_K3_passed`)

| Run | Report § anchor | Bucket | Why this bucket | Why NOT the others |
|---|---|---|---|---|
| **N8.2** (Phase G PROPER OOS 2026-05-01 — `data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/`, run_id `3da49a82343e4650abfd0d4921ee1897`; timestamp_brt `2026-05-01T02:55:55`; wall 141 min 19 s; post-R18 Dex caller wiring closed) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1-§6 + ESC-013 §5(c) outcome match | **B — `strategy_edge` sub: `costed_out_edge_oos_confirmed_K3_passed`** (Mira F2-T9.1 FINAL Round 3.1 refinement per ESC-013 §5(c)) | First authoritative Phase G OOS PROPER unlock run with `holdout_locked=False` propagated correctly per ESC-013 R18 Dex caller wiring (`backtest_phase==G` + `parquet_root` resolved to holdout-window parquet `data/in_sample` carry-forward via Phase G unlock semantics). K3 decay test fully evaluated: IC_holdout=0.865933 ≫ 0.5 × IC_in_sample=0.433005; decay ratio 0.99991 ≫ 0.5 threshold → **K3 decay COMPUTED PASS** (verdict.reasons=[] empty array; `ic_holdout_status='computed'` propagated; OBS-1 short-circuit DID NOT fire). K3 in-sample binding PASS (IC=0.865933 with CI95=[0.864880, 0.866025] non-degenerate width 0.001145; CI95_lower=0.864880 > 0). K2 PBO=0.059524 PASS strict (0.441 below 0.5 threshold; well below 0.25 ideal). **K1 STRICT FAIL** at DSR_OOS=0.205731 (0.744 below 0.95 threshold; ~3.6× worse than F2 N7-prime IS DSR=0.766987). Realized PnL distribution OOS materially worse than IS: sharpe_mean +0.046 IS → -0.053 OOS (NEGATIVE OOS); profit_factor 1.075 IS → 0.929 OOS (BELOW 1 OOS — losers exceed winners gross-of-deployment); sortino +0.109 IS → -0.122 OOS (NEGATIVE OOS); max_drawdown 0.995 IS → 1.274 OOS (28% worse OOS); hit_rate 0.497 IS → 0.472 OOS (sub-50% trade-level OOS). Per Mira F2-T9.1 §4.3 four-cell evidence matrix (refined OOS): pure-leakage REJECTED OOS (hit_rate 0.472 ≠ near-saturation IC 0.866); spurious-correlation REJECTED OOS (CI95 tight + sign preserved); real-edge-fully-realized REJECTED OOS (DSR 0.206 << 0.95; hit_rate < 0.5; profit_factor < 1); **real-edge-costed-out CONFIRMED OOS** (predictor-rank stability cross-window via K3 PASS COMPUTED; cost-foreclosure hypothesis OOS-confirmed by NEGATIVE sharpe + sub-50% hit + sub-1 profit_factor). All bucket-B inclusion criteria S1..S8 satisfied: S1 real WDO holdout-window market data ✅; S2 ALL bucket-A criteria E1..E8 satisfied on the same run ✅ (Phase G unlock caller-wiring gap CLOSED structurally per ESC-013 R18 Dex commit); S3 Mira spec v1.2.0 §1 thresholds applied verbatim (DSR strict FAIL OOS by 0.744 = honest measurement against UNMOVABLE bar) ✅; S4 Bonferroni n_trials=5 verbatim (`trials=['T1'..'T5']`, `n_trials_used=5`, `n_trials_source=docs/ml/research-log.md@fadacf48…`) ✅; S5 sample size 3700 events ≫ 250 floor (123× over 30 minimum per §15.7 dedup) ✅; S6 hold-out [2025-07-01, 2026-04-21] CONSUMED Round 3.1 (one-shot per ESC-012 R9 + ESC-013 R19; Phase G unlock authority exercised exactly once) ✅; S7 failure attribution scaffolding in place ✅ (this Round 3.1 entry); S8 cost atlas wiring identical to F2 IS run (`cost_atlas_sha256=bbe1ddf7…c24b84b6d` IDENTICAL N6+ → N7 smoke → N7 full Round 1 → N7-prime Round 2 → N8 → N8.2; ESC-012 R6 reusability invariant binding). | NOT bucket-A Round 3.1: bucket-A `phase_g_unlock_caller_gap` sub-classification opened in N8.1 row is **CLOSED** structurally Round 3.1 by ESC-013 R18 Dex caller wiring commit (extend phase Literal `{"E", "F", "G"}` + propagate `holdout_locked=False` for phase=="G"). NOT clean negative `strategy_edge` (would require IC_holdout ≤ 0 OR CI95_lower ≤ 0 OR sign-flip cross-window — NONE observed; IC robust ~0.866 IS+OOS with CI95_lower > 0 strict in both windows; K3 decay PASS by 99% margin). NOT Round 2 `costed_out_edge` provisional (Round 2 was IS-only; Round 3.1 is OOS-CONFIRMED with stronger diagnostic — refined within same bucket B sub envelope). NOT Round 3 INCONCLUSIVE (Round 3 INCONCLUSIVE_pending_phase_g_proper consumed N8 F-protocol artifact under DEFERRED K3 sentinel; Round 3.1 N8.2 PROPER unlock resolves the INCONCLUSIVE residual cleanly). NOT bucket-C: still backtest, no live feed; bucket-C never opened. |

#### §2.R3.1.3 — Round 3 N8 reclassification disposition (governance integrity preserved; ESC-013 §3 ratification)

**Round 2 N7-prime ledger row + Round 1 N7 full ledger row are NOT MUTATED.** Both Round 1 + Round 2 attributions were honestly classified per the evidence at the time of their authoring (Round 1 = IC-pipeline-wiring gap identified Mira T5; Round 2 = `costed_out_edge` sub-classification surfaced Mira F2-T5 with K3 deferred to Phase G). Round 3 INCONCLUSIVE_pending_phase_g_proper (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md`) is preserved per spec §15 append-only revision discipline; ESC-013 5/5 UNANIMOUS APPROVE_PATH_IV ratified Mira's Round 3 strict reading that K3 DEFERRED-sentinel ≠ COMPUTED-PASS therefore R15 trigger NOT met regardless of artifact DSR=0.965 above 0.95 threshold (Anti-Article-IV Guard #4 honored — strict reading preserved through three rounds).

**Round 3.1 SUPERSEDES Round 3 + Round 2 + Round 1 at the verdict-disposition layer** for the **same underlying T002 strategy hypothesis evaluated under proper Phase G OOS unlock**, but ALL prior round entries are preserved verbatim per Mira spec v1.2.0 §15 append-only revision invariant + governance audit-trail provenance discipline. Co-existence: Round 1 row = "honest data_quality classification under Round 1 evidence (IC unmeasured)"; Round 2 row = "honest costed_out_edge classification under Round 2 evidence (IC measured IS + K3 deferred to Phase G)"; Round 3 row = "honest INCONCLUSIVE classification under Round 3 evidence (K3 DEFERRED-sentinel under F-protocol-over-holdout artifact)"; Round 3.1 row = "honest costed_out_edge_oos_confirmed_K3_passed classification under Round 3.1 evidence (K3 COMPUTED PASS under PROPER Phase G unlock; DSR_OOS strict FAIL)". Future readers MUST consult Round 3.1 row for current bucket disposition; MAY consult prior rows for round-by-round diagnostic genealogy (Round 3 → Round 3.1 protocol-correction chain is **Article IV exemplary** per Mira F2-T9.1 §3.4: near-miss surprise held to strict-reading scrutiny → strict reading prescribed protocol-corrected re-run → re-run revealed artifact and confirmed Round 2 `costed_out_edge` diagnostic with stronger OOS evidence + K3 PASS).

#### §2.R3.1.4 — Refined bucket framework Round 3.1: `costed_out_edge_oos_confirmed_K3_passed` sub-classification within `strategy_edge`

Mira F2-T9.1 FINAL §1 + §4 + §5 authority introduces **`costed_out_edge_oos_confirmed_K3_passed`** as a refinement of the Round 2 `costed_out_edge` sub-classification within bucket B `strategy_edge`. Riven custodial endorsement Round 3.1:

**Definition (`costed_out_edge_oos_confirmed_K3_passed`):** Refines Round 2 `costed_out_edge` with explicit OOS confirmation under K3 COMPUTED-PASS. Four conditions hold simultaneously (per Mira F2-T9.1 §5.2 OOS confirmation logic):
1. **K3 decay PASS COMPUTED** — predictor-rank stability cross-window (IC magnitudes near-IDENTICAL IS=0.866010 / OOS=0.865933, decay ratio 0.99991 ≫ 0.5 threshold; CI95_lower > 0 strict in both windows).
2. **K1 OOS strict FAIL** — DSR_OOS << 0.95 (observed N8.2 DSR_OOS=0.205731; 0.744 below threshold; ~3.6× worse than IS).
3. **Realized PnL distribution worse OOS than IS** — sharpe_mean drops (+0.046 → -0.053), hit_rate drops (0.497 → 0.472), profit_factor drops (1.075 → 0.929), max_drawdown rises (0.995 → 1.274). All four metrics worsen OOS.
4. **Realized PnL distribution sub-deployable OOS** — sharpe_mean NEGATIVE OOS, hit_rate sub-50% OOS, profit_factor sub-1 OOS. All three sub-deployable on absolute scale.

The N8.2 evidence satisfies ALL FOUR conditions cleanly. This is the **strongest possible empirical signature short of clean K3 collapse (Bucket B falsification) or surprise PASS (ESC-014 trigger)** per Mira F2-T9.1 §5.2.

**Distinction from Round 2 `costed_out_edge` (provisional):**

| Failure regime | IC_in_sample | IC_holdout | K3 decay | DSR_IS | DSR_OOS | Diagnostic |
|---|---|---|---|---|---|---|
| **Round 1 wiring-gap signature (unmeasured)** | exactly 0.0 (default) | not computed | not computed | n/a (partial) | n/a | Field-default propagation; NOT honest measurement |
| **Round 2 `costed_out_edge` (IS-only; provisional)** | 0.866010 PASS strict | DEFERRED (Phase G locked) | DEFERRED | 0.766987 strict FAIL by 0.183 | not measured | Predictor-rank IS strong; deployment FAIL IS; OOS UNCONFIRMED |
| **Round 3 INCONCLUSIVE (artifact)** | 0.866010 (carry-forward) | 0.865933 (artifact under F-protocol-over-holdout) | DEFERRED-sentinel (OBS-1 short-circuit fired under F-protocol) | 0.766987 (IS) | 0.965085 (artifact) | DSR=0.965 surprise; K3 status DEFERRED ≠ COMPUTED → R15 NOT met; protocol-corrected re-run prescribed |
| **Round 3.1 `costed_out_edge_oos_confirmed_K3_passed` (PROPER)** | 0.866010 PASS strict | **0.865933 PASS strict** | **0.99991 ≫ 0.5 COMPUTED PASS** | 0.766987 (IS) | **0.205731 STRICT FAIL OOS by 0.744** | Predictor-rank cross-window confirmed; cost-foreclosure OOS-confirmed; T002 NOT permanently falsified at predictor level BUT NOT deployable at strict bar |
| **Clean `strategy_edge` falsified (counterfactual)** | ≤ 0 OR CI95_lower ≤ 0 OR sign-flip cross-window | n/a | n/a | n/a | n/a | T002 thesis falsified per spec §0; retire entirely |
| **Real edge fully realized (counterfactual deployable)** | > 0 strict | > 0 strict + CI tight | decay PASS | > 0.95 IS | > 0.95 OOS strict | Bucket B PASS; Phase H paper-mode dispatch authorized |

**Implication for thesis falsifiability under spec §0 mandate ("the data MUST be allowed to refute"):** `costed_out_edge_oos_confirmed_K3_passed` is the **OOS-confirmation strengthening** of Round 2 `costed_out_edge`. The thesis is **OOS-confirmed-as-valid-but-undeployable** — predictor-rank stability hypothesis holds across windows (K3 PASS COMPUTED OOS confirms the H1 alternative thesis "end-of-day inventory unwind in WDO produces fade reversion to 17:55 close" at the rank-correlation level); the deployment hypothesis fails OOS (DSR_OOS=0.206 << 0.95 strict + sub-deployable PnL distribution OOS). Per ESC-013 §5(c) action prescription:

- **T002 retire with refined diagnostic** triggered (Path C ESC-012 §5 fallback auto-activate; Pax T002.7 close ceremony per ESC-013 §6 closure conditions row 6).
- **Path A (cost reduction R&D) BLOCKED per user constraint** — ESC-013 §5(c) explicitly notes "cost reduction R&D path (BLOCKED by user constraint Path A OFF)". No retuning of cost atlas / triple-barrier / latency_dma2 / entry-window is authorized as forward research within T002 scope. (Path A would reopen Phase F3 with mutated cost-side parameters; user constraint forecloses.)
- **Path B (Phase G OOS confirmation) CONSUMED Round 3.1** — N8.2 PROPER Phase G unlock executed per ESC-013 R18; OOS evidence is now in the ledger; Phase G one-shot exhausted per ESC-012 R9 + ESC-013 R19. Hold-out window [2025-07-01, 2026-04-21] is **CONSUMED** post-Round 3.1; future H_next research must use a NEW preregistered window.
- **Path C (T002 retire + redirect) AUTO-TRIGGER** per ESC-013 §5(c).

**OOS-confirmed `costed_out_edge_oos_confirmed_K3_passed` is the FINAL Gate 4b verdict for T002.** No further Phase F2 / Phase F3 / Phase G iteration is authorized within T002 scope (Path A user-blocked; Path B exhausted; Path C activated). Pax T002.7 close trigger is the binding forward action.

#### §2.R3.1.5 — Total runs classified Round 3.1 update

**Total runs classified post Round 3.1:** 9 (N5, N+1, N6, N6+, N7 smoke, N7 full Round 1 = bucket A — engineering_wiring sub-variants; N7-prime Round 2 = bucket B `strategy_edge` sub `costed_out_edge` provisional; N8.1 Round 3.1 = bucket A `engineering_wiring` sub `phase_g_unlock_caller_gap` artifact; N8.2 Round 3.1 = bucket B `strategy_edge` sub `costed_out_edge_oos_confirmed_K3_passed` FINAL). 1 bucket-B FINAL classification (Round 3.1 — N8.2 OOS-confirmed). Zero bucket-C clearances. **Gate 5 cannot fire — LOCKED PERMANENTLY post-T002-retire** — single-leg Gate 4b sub-bucket classification at `costed_out_edge_oos_confirmed_K3_passed` is NOT `GATE_4_PASS`; R5/R6 conjunction `Gate 4a HARNESS_PASS ∧ Gate 4b GATE_4_PASS ∧ paper-mode audit` UNSATISFIED (K1 strict FAIL OOS on Gate 4b leg per Mira F2-T9.1 spec v1.2.0 §1 decision rule + ESC-013 §5(c) outcome match + Anti-Article-IV Guard #4 UNMOVABLE). Capital ramp barrier remains LOCKED post Round 3.1; Riven §9 HOLD #2 Gate 4b NON-DISARM Round 3.1 ledger entry recorded in companion file `docs/qa/gates/T002.0g-riven-cosign.md` §9 HOLD #2 Round 3.1 section (appended same authoring window as this Round 3.1 post-mortem update).

**T002 chain status post Round 3.1:** Gate 4b adjudication chain CLOSED at FINAL FAIL `costed_out_edge_oos_confirmed_K3_passed`. Gate 5 LOCKED PERMANENTLY (capital ramp impossible per spec §0 falsifiability + ESC-013 §5(c)). Hold-out window [2025-07-01, 2026-04-21] CONSUMED (one-shot per ESC-012 R9 + ESC-013 R19) — future H_next research direction (separate story / separate predictor / separate horizon / separate filter) MUST use NEW preregistered window per spec §0 falsifiability discipline. Pax authority adjudicates H_next research direction via T002.7 close → new epic/story dispatch.

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

### 5.9 Anti-pattern: "`costed_out_edge` ≠ Round 1 wiring gap" (Round 2 NEW — 2026-04-30 BRT)

**Category error type:** Diagnostic-confusion (Round 2 superficially similar K3 FAIL signature mistakenly attributed to Round 1 root cause — or vice versa).

**Why this matters:** N7 full Round 1 and N7-prime Round 2 BOTH emit `KillDecision verdict: NO_GO` with K3 reason text in `kill_decision.reasons[0]`. A casual reader could conflate the two failures into the same root cause ("K3 FAILed both times, must be the same thing"). They are **inverse** root causes:

| Diagnostic axis | Round 1 (wiring gap) | Round 2 (costed_out_edge) |
|---|---|---|
| `IC_spearman` mean | exactly `0.000000` (`ReportConfig.ic_in_sample` field-default propagation) | **`0.866010`** (paired-resample bootstrap honest measurement over 3800 events) |
| `IC_spearman_ci95` | `[0.0, 0.0]` (zero-width = wiring gap signature; bootstrap never invoked) | **`[0.865288, 0.866026]`** (width 0.000738; non-degenerate paired-resample bootstrap n=10000 PCG64 seed=42 paired-index strategy per spec §15.4 — implementation contract honored) |
| `ic_status` provenance flag (Anti-Article-IV Guard #8) | not propagated (pre-§15 amendment; defaults flowed through `MetricsResult` → `evaluate_kill_criteria` unmodified) | implicitly `'computed'` (verdict layer did NOT raise `InvalidVerdictReport` per §15.6 invariant body for in-sample channel; honestly serialized) |
| `hit_rate` | 0.4966981 (incidentally near 0.5; NOT diagnostic in isolation under wiring-gap regime because IC was unmeasured) | 0.4966981 (essentially break-even; canonical `costed_out_edge` diagnostic when paired with IC=0.866) |
| `K3 verdict reason text` (kill_decision.reasons[0]) | "K3: IC=0.000000 not strictly > 0" (or equivalent default-value emission) | "K3: IC_holdout=0.000000 < 0.5 × IC_in_sample=0.866010" (decay clause emission under deferred holdout — F2-T5-OBS-1 implementation enforcement gap; spec §15.10 strict reading short-circuits to `K3_DEFERRED` for Phase F2 per Mira F2-T5 §4.4) |
| Bucket attribution | bucket A `engineering_wiring` (sub: `IC_pipeline_wiring_gap`) — Mira spec §6.1 footnote envelope extension Round 1 | bucket B `strategy_edge` (sub: `costed_out_edge`) — Mira F2-T5 §1 + §5.2 evidence matrix Round 2 |
| Falsifiability under spec §0 mandate | Cannot fire — measurement chain incomplete; falsification requires honest measurement (§5.8 binding) | PARTIAL — IC>0 strict satisfied (K3 in-sample binding PASS Phase F2 per §15.10); DSR strict FAIL is deployment-gate failure NOT thesis-falsification (§5.3 of Mira F2-T5); thesis Q4 kill triplet `(DSR<0, PBO>0.4, IC_holdout decay, DD>3σ)` NOT triggered |
| Forward path | Phase F2 cycle (F2-T0..F2-T6) — wire IC pipeline structurally | Phase G OOS confirmation OR Phase F3 cost-side parameter exploration OR T002 retirement (Pax authority adjudicates) |

**Generalized diagnostic key (Riven taxonomy refinement Round 2):** to distinguish Round 1-class wiring-gap from Round 2-class `costed_out_edge` on any future Gate 4b run that emits K3 reason text, inspect the **(IC magnitude, CI95 width, hit_rate)** triplet:

- **Round 1 signature (wiring gap):** IC = exactly 0.0 default ∧ CI95 = exactly [0.0, 0.0] zero-width ∧ hit_rate = any value (informationally void about the strategy because IC was unmeasured) → Anti-pattern §5.8 binding (zero-with-tight-CI ≠ falsificação); Phase F2-prime cycle dispatch
- **Round 2 signature (`costed_out_edge`):** IC > 0 with CI95_lower > 0 strict (e.g., IC > 0.05 meaningful per AFML §8.6; IC > 0.5 exceptional) ∧ CI95 width finite + narrow but non-degenerate (e.g., 0.000738 over n=10000 paired bootstrap) ∧ hit_rate ≈ 0.5 ∧ DSR finite-positive but < strict bar → bucket B `strategy_edge` sub `costed_out_edge` Round 2 nuance; cost-reduction R&D OR Phase G OOS confirmation OR retirement decision
- **Clean `strategy_edge` signature (no signal):** IC ≤ 0 OR CI95_lower ≤ 0 ∧ hit_rate ≈ 0.5 ∧ DSR finite-near-zero or negative → bucket B `strategy_edge` clean negative; T002 retired per spec §0 falsifiability mandate
- **Real edge fully realized (deployable):** IC > 0 strict ∧ CI95_lower > 0 ∧ hit_rate tracks IC at deployable level ∧ DSR > 0.95 strict ∧ PBO < 0.5 → bucket B `strategy_edge_confirmed` (`GATE_4_PASS` per Mira spec §9 verdict-label discipline); Phase G holdout unlock authorized as final OOS cross-check before bucket-C paper-mode dispatch

**Riven action on observation:** REJECT any future sign-off attempt or post-mortem update that conflates these four regimes. Each regime has distinct forward-research path and distinct sizing implication. Conflating Round 1 (wiring gap = unmeasured) with Round 2 (`costed_out_edge` = measured + cost-eroded) would either (a) re-trigger Phase F2-prime cycle unnecessarily (if Round 2 signature is misread as Round 1) — wasting compute + governance bandwidth; or (b) prematurely retire T002 (if Round 1 signature is misread as Round 2 clean negative `strategy_edge`) — falsification by unwired-default which §5.8 already forbids.

**Anchor:** This anti-pattern was first documented at N7-prime Round 2 adjudication (2026-04-30 BRT) per Mira F2-T5 verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §1 + §5.2 + §6.4 + §8.1) + Beckett N7-prime report (`docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §3.4 hit-rate paradox + §4 IC measurement validity). Carries forward as binding for all future Gate 4b verdicts presenting K3 reason text emission. Companion to anti-pattern §5.8 (Round 1 — zero-with-tight-CI ≠ falsificação).

### 5.10 Anti-pattern: "Phase F-over-holdout DSR ≠ Phase G unlock proper DSR" (Round 3.1 NEW — 2026-05-01 BRT)

**Category error type:** Protocol-confusion (running Phase F semantics over the holdout-window parquet does NOT produce a proper Phase G OOS DSR measurement; the resulting DSR is a procedural artifact, NOT an OOS verdict input).

**Why this matters:** The Round 3 N8 run produced a surprise DSR=0.965085 over the holdout window — apparently above the 0.95 strict threshold, an apparent near-miss PASS for K1. Mira Round 3 INCONCLUSIVE held the strict reading: K3 status DEFERRED-sentinel ≠ COMPUTED-PASS, therefore PRR §3.1 R15 trigger NOT met regardless of artifact DSR appearing above threshold. ESC-013 5/5 UNANIMOUS APPROVE_PATH_IV ratified the strict reading and prescribed a protocol-corrected re-run (PROPER Phase G unlock with `holdout_locked=False` propagated and phase Literal extended to include `"G"`). The N8.2 PROPER unlock revealed DSR_OOS=0.205731 — a sign-flip of -0.759 from the artifact value.

**Mechanism (Mira F2-T9.1 §3.1-§3.3 forensic):** Pre-R18 Dex caller wiring (`scripts/run_cpcv_dry_run.py:1088-1102`) hardcoded `holdout_locked=True` under `phase=="F"` semantics; the `--phase` CLI flag accepted only `{"E", "F"}` — Phase G was NOT a recognized choice. When N8 was invoked over the holdout-window parquet path, the harness ran under Phase F semantics: `holdout_locked=True`, `ic_holdout_status='deferred'`, `ic_holdout=0.0` field default propagated; OBS-1 short-circuit fired in `evaluate_kill_criteria`; verdict-layer reported `k3_ic_decay_passed=true` with reason text `K3: DEFERRED — ic_holdout_status='deferred' — decay test pending Phase G unlock`. The N8 DSR=0.965 was computed as the **in-sample-DSR-over-holdout-window** measurement under Phase F protocol short-circuit semantics — Bailey-LdP DSR factors (per-trial mean Sharpe + skewness + kurtosis + Bonferroni n_trials=5) were applied to the holdout-window CPCV path-PnL distribution but under the F-protocol carry-forward, producing an artifact value. NOT an OOS-DSR measurement; an IS-DSR measurement over the OOS-window data. Same window same data **different statistical treatment**.

**Diagnostic key (Riven taxonomy refinement Round 3.1):** to distinguish a **Phase F-over-holdout artifact** from a **PROPER Phase G unlock measurement** on any future run claiming "DSR over holdout window", inspect TWO determinism-stamp flags simultaneously:

1. **`holdout_locked` flag** must be **False** (i.e., Phase G unlock authorized at the caller wiring layer; ESC-013 R18 binding).
2. **closure phase Literal** at the call site must include **"G"** as an admissible phase value (i.e., the harness recognizes `--phase G` and routes to Phase G semantics; pre-R18 caller wiring fell through to synthetic walk silently if "G" was not in the Literal — see N8.1 ledger row §2.R3.1.1 for the synthetic-fallback bug signature: ~12s wall-time vs ~141 min for proper Phase G real-tape CPCV).

If EITHER flag is `True` (or the Literal lacks "G"), the run is **NOT a proper Phase G OOS measurement** — it is at best a Phase F-over-holdout artifact (if Phase F semantics carry-forward), and at worst a synthetic-walk fall-through (if the closure-Literal mismatch causes silent fall-through to `_walk_session_path` / `_walk_to_exit`).

**Phase F2-binding K3 PASS clause (spec v1.1.0 §15.10) carry-forward to Phase G:** under Phase F2, K3 PASS = `(IC_in_sample > 0) AND (CI95_lower > 0)` strict; decay sub-clause is Phase G binding, not Phase F2. Under PROPER Phase G unlock (Mira spec v1.2.0 §15.13.5), K3 PASS adds the decay sub-clause `IC_holdout > 0.5 × IC_in_sample` as a binding evaluation. The N8 artifact ran under Phase F2 K3 binding semantics over the holdout-window parquet — this is a **protocol confusion**, NOT a proper Phase G evaluation. The N8.2 PROPER run satisfies the Phase G binding clauses (K3 in-sample PASS strict + K3 decay COMPUTED PASS) and produces the binding K1 OOS measurement (DSR_OOS=0.206 << 0.95 STRICT FAIL OOS).

**Why this matters for Article IV (Anti-Article-IV Guard #4 UNMOVABLE):** had Round 3 ratified `GATE_4_PASS_oos_confirmed` based on the N8 artifact DSR=0.965, it would have constituted a **soft Article IV violation** (passing at threshold based on an unreliable measurement). Mira Round 3 INCONCLUSIVE verdict + ESC-013 5/5 ratification of the strict reading prevented this. The Round 3 → Round 3.1 protocol-correction chain is **Article IV exemplary** per Mira F2-T9.1 §3.4: a near-miss surprise was held to strict-reading scrutiny; the strict reading prescribed protocol-corrected re-run; the re-run revealed the artifact and confirmed the Round 2 `costed_out_edge` diagnostic with stronger OOS evidence + K3 PASS. NO threshold relaxation occurred; NO post-hoc disposition rule mutation occurred; NO favorable interpretation of artifact data was retained. The strict reading was preserved through three rounds.

**Riven action on observation:** REJECT any future sign-off attempt or post-mortem update that uses a Phase F-over-holdout artifact DSR as evidence input to PRR §3.1 R15 / R16 / R17 / §3.4 INCONCLUSIVE branch evaluation. The PRR partition is binding ONLY over PROPER Phase G unlock measurements (`holdout_locked=False` AND closure phase Literal includes "G"). Any DSR-over-holdout claim MUST present BOTH flags verified PROPER per ESC-013 R18 contract test (R20 NEW per ESC-013 — verdict-vs-reason invariant: K3 PASS reason text MUST contain computed numbers OR be empty, NOT sentinel strings; R20 contract test verifies under PROPER Phase G unlock).

**Anchor:** This anti-pattern was first documented at N8.2 Round 3.1 adjudication (2026-05-01 BRT) per Mira F2-T9.1 FINAL verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1 + §3 N8 surprise DSR artifact disambiguation + §3.3 DSR sign-flip 0.965 → 0.206 forensic + §3.4 Article IV exemplary protocol-correction chain) + ESC-013 §5(c) outcome match (`docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` 5/5 UNANIMOUS APPROVE_PATH_IV) + Mira Round 3 INCONCLUSIVE_pending_phase_g_proper sign-off (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` strict reading preservation). Carries forward as binding for all future post-T002-retire research direction (H_next epics/stories) presenting any "DSR over OOS window" claim. Companion to anti-patterns §5.8 (Round 1 — zero-with-tight-CI ≠ falsificação) and §5.9 (Round 2 — `costed_out_edge` ≠ Round 1 wiring gap). The three anti-patterns §5.8 + §5.9 + §5.10 together constitute the Riven taxonomy for distinguishing four orthogonal failure regimes at the Gate 4b level: **wiring-gap (§5.8)** vs **costed-out-edge IS-only (§5.9)** vs **costed-out-edge OOS-confirmed via PROPER Phase G (§5.10 implicit positive case)** vs **F-over-holdout artifact (§5.10 explicit negative case)**.

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

### 6.4.3 N7-prime Round 2 → bucket B `strategy_edge` sub `costed_out_edge` (Phase F2 IC pipeline post-fix; APPENDED 2026-04-30 BRT)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §1 executive verdict (pipeline integrity PASS + IC measurement CONFIRMED at IC=0.866 + tight CI [0.865, 0.866]) + §3 execution metadata (3800 events × 5 trials = 19,000 trial-events; sample-size R9 EXCEEDED 76×; wall-time 188 min) + §3.3 cross-check vs N7 Round 1 stamp (8/9 reproducibility receipt fields IDENTICAL — `dataset_sha256=ff9b5058…` IDENTICAL proves F2 fix is purely post-hoc compute over identical CPCV walk; only `run_id` + `timestamp_brt` differ by design) + §4 IC pipeline measurement validity (CI95 width 0.000738 non-degenerate paired-resample bootstrap n=10000 PCG64 seed=42 paired-index strategy per spec §15.4; CI95_lower 0.865288 > 0 strict per §15.10 Phase F2 binding K3_PASS condition) + §5.1 distribution diagnostics bit-equal to N7 Round 1 (sharpe_mean=+0.046251, sharpe_std=0.185048, sharpe_min=-0.546, sharpe_max=+0.614, 225/225 unique sharpes — proves engine UNCHANGED at runtime + closure-capture preserved + threshold UNMOVED + Bonferroni n_trials=5 verbatim) + §6 KillDecision verdict NO_GO via K3 decay-clause false-fail (F2-T4-OBS-1 verdict-layer enforcement gap surfaced — orthogonal to Round 2 verdict per Mira F2-T5 §4) + §7 three-interpretation surfacing (A/B/C) + Beckett §7.4 non-pre-emption stance + §8 5 SHA-stamped artifacts (`determinism_stamp.json` 40a14df4…, `events_metadata.json` 5488b3ef…, `full_report.json` ef106df2…, `full_report.md` a4aa3e05…, `telemetry.csv` 7c50f7b7…) + §9 Anti-Article-IV self-audit 7 guards + Guard #8 NEW honored. |
| (b) Governance | Mira F2-T5 verdict `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` `verdict: GATE_4_FAIL_strategy_edge` `verdict_sub_classification: costed_out_edge` (provisional, Mira F2-T5 Round 2 nuance per §1 + §5.2; supersedes Round 1 GATE_4_FAIL_data_quality per spec v1.1.0 §15 append-only revision discipline; Round 1 sign-off integrity preserved) — §1 executive verdict + bucket suffix justification + §2 threshold table strict (K1 FAIL by 0.183 / K2 PASS / K3 in-sample PASS strict per §15.10 Phase F2 binding clause) + §3 IC measurement validity audit (3.1 wiring evidence vs Round 1 zero-signature; §3.2 statistical validity 4 anchors; §3.3 cross-check Round 1 vs Round 2; §3.4 IC=0.866 engineering correctness vs strategy edge interpretation — 5 reasoning anchors including hit-rate paradox §3.4.4) + §4 K3 decay-clause enforcement clarity (F2-T5-OBS-1 implementation enforcement gap; 4 sub-anchors §4.1-§4.5; Mira authoritative reading: in-sample channel binding for Phase F2 verdict; decay-clause Phase G NOT applicable Phase F2 per spec §15.10) + §5 IC=0.866 strategy edge evidence vs measurement artifact (3-cell evidence matrix §5.1 rejecting leakage + spurious correlation; §5.2 four-cell hit-rate-paradox + IC + DSR + sharpe_mean diagnostic; §5.3 thesis falsifiability implication — Q4 kill triplet NOT triggered; §5.4 clean falsification counterfactual) + §6 3-bucket attribution decision-tree application Step 1-5 verbatim against Round 2 evidence + §7 R6 footer reinforced verbatim + §8.1 Riven T6 reclassification path (bucket A `IC_pipeline_wiring_gap` CLOSED Round 2 + bucket B `strategy_edge / costed_out_edge` OPENED Round 2; S1..S8 satisfied) + §8.2 F2-T5-OBS-1 Dex follow-up scope + §8.3 Phase G holdout unlock authorization status (3 forward-research path options) + §8.4 wall-time concern carry-forward + §8.5 simulator_version housekeeping + §9 Anti-Article-IV self-audit 8 guards (Guard #1-#7 honored verbatim + Guard #8 NEW in-sample channel honored). ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification preserved Round 2; ESC-011 R8/R9/R11/R14 + Aria T0b C-A7 HIGH single atomic AND-conjunction ledger row format binding for FAIL-path entries preserved Round 2. F2-T1 IC pipeline wiring CLOSED structurally per commit `2445bae` + PR #14 main `0903eaf` (merged 2026-04-30 12:36 BRT). Quinn QA F2 PASS 8/8 pre-run preserved. Mira spec v1.1.0 §15.10 Phase F2 narrowing applied: K3 PASS = `(IC_in_sample > 0) AND (CI95_lower > 0)` strict reading; decay sub-clause Phase G; not Phase F2. |
| (c) Mira spec | §0 falsifiability mandate (the data MUST be allowed to refute) — Round 2 HONORS for K1 + K2 + K3 in-sample binding (all three honestly measured; K1 strict FAIL is honest measurement against UNMOVABLE bar). §1 thresholds UNMOVABLE per Anti-Article-IV Guard #4 (DSR>0.95, PBO<0.5, IC>0 with CI95_lower>0); strict reading applied AS-IS Round 2 despite strong K3 in-sample evidence — partial-pass does NOT promote (joint conjunction required). §6 sample-size R9 EXCEEDED 76× (3800 ≫ 250 floor; bucket reclassification falls through to Step 3 triplet adjudication per §7.2 decision tree). §7.1 bucket `strategy_edge` envelope verbatim definition consumed: "Failure attributable to the strategy itself (no economic edge in the WDO end-of-day fade hypothesis under realistic costs+latency)" — refined Round 2 to sub-classification `costed_out_edge` (Mira F2-T5 §1 + §5.2 evidence matrix authority; nuance distinguishes prediction-level edge present + cost-eroded from clean negative no-signal). §11.2 Anti-Article-IV Guards #1-#7 honored Round 2 (no subsample / engine UNCHANGED at runtime / hold-out UNTOUCHED [2025-07-01, 2026-04-21] / thresholds UNMOVED / RSS honest 600 MB / no source mod / no push). §15 IC pipeline wiring spec FULLY OPERATIONALIZED Round 2: §15.1 per-event predictor=−intraday_flow_direction × label=ret_forward_to_17:55_pts paradigm + filter_active gate honored; §15.4 paired-resample percentile bootstrap n=10000 PCG64 seed=42 honored; §15.5 Anti-Article-IV Guard #8 NEW in-sample channel honored (`ic_status='computed'` propagated; verdict serialized; no `InvalidVerdictReport` exception); §15.6 enforcement invariant respected for in-sample channel; §15.7 dedup invariant `(session_date, trial_id, entry_window_brt)` first-occurrence honored (3800 unique events; matches `events_metadata.n_events`); §15.10 Phase F2 binding clause `(IC_in_sample > 0) AND (CI95_lower > 0)` PASS strict; F2-T5-OBS-1 verdict-layer decay-clause enforcement gap surfaced (Dex follow-up scope; non-blocking for F2-T5 verdict per Mira F2-T5 §4.4 authoritative reading). |
| (d) External | Bailey-LdP 2014 §3 — DSR/PBO methodology over CPCV distribution honestly wired at `report.py:481-514` (IDENTICAL Round 1 to Round 2; bit-equal sharpe distribution proves engine + closure-capture + thresholds UNCHANGED across F2 amendment boundary). DSR=0.766987 is **honest economic measurement against UNMOVABLE 0.95 bar**; Round 2 measurement is now **coherent jointly with K3 in-sample PASS** (per §15.10 strict reading) so the joint conjunction K1 ∧ K2 ∧ K3_in_sample CAN be coherently evaluated for Phase F2 verdict — and FAILS strict at K1 (0.766987 < 0.95 by 0.183). Efron 1979 percentile-bootstrap — `info_coef.bootstrap_ci` Round 2 invocation honored: 10000 paired-resample iterations with PCG64 seed=42 paired-index strategy produced CI95 [0.865288, 0.866026] non-degenerate (width 0.000738) — confirms wiring works under honest measurement protocol. AFML §8.6 IC stability calibration — IC > 0.05 meaningful; IC > 0.5 exceptional; observed 0.866 is far above exceptional. Caveat: AFML §8.6 calibrated for cross-sectional asset returns at daily frequency, not intraday WDO end-of-day fade events — direct comparability loose; exceptional reading checked against thesis Q4+H1 structural predictability hypothesis; known structural pattern (custodian flows + inventory unwind at close) can produce IC orders of magnitude higher than typical cross-sectional fund-management IC ranges. Kelly 1956 / Thorp 2006 §III — Kelly fraction f* = μ/σ² requires distribution of P&L per trade with **honest IC-validated economic edge AND deployable Sharpe distribution**; N7-prime Round 2 distribution is **not yet** a Kelly-parametrizable substrate at deployable level (DSR=0.767 strict FAIL; sharpe_mean=+0.046 finite-positive but small-magnitude; Kelly cheio over costed-out distribution would size below quarter-Kelly cap but is still inappropriate without bucket-C paper-mode confirmation per §1.4 mutual-exclusivity-and-ordering rule). Authorized live size remains ZERO contracts post Round 2 per §4.4 (carry-forward Round 1 disposition). |

### 6.5 N7+ → bucket B (forward declaration, NOT YET RUN — Round 1 declaration; superseded operationally by §6.4.3 Round 2 actually-realized N7-prime ledger row)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | NOT YET RUN — to be authored at `docs/backtest/T002-beckett-n7-{date}.md` post-Phase-F execution. |
| (b) Governance | ESC-011 R8 (Phase F real-tape replay scope), R9 (sample size + Bonferroni + attribution scaffolding), R10 (separate future story T002.2), R11 (Mira drafts Gate 4b spec BEFORE Gate 4a verdict — fence-against-drift), R14 (Mira spec §6 thresholds DSR>0.95 / PBO<0.5 / IC unmovable per Anti-Article-IV Guard #4). |
| (c) Mira spec | §0+§7 Phase F empirical anchor preserved (`docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` line 152). Hold-out [2025-07-01, 2026-04-21] UNTOUCHED until Phase F authorized to consume. |
| (d) External | Bailey-LdP 2014 §3 sample-size minimum (≥ 30-50 per trial × 5 trials); Kelly 1956 / Thorp 2006 §III — first viable Kelly parametrization regime. |

#### 6.5.R2 Round 2 update (2026-04-30 BRT) — N7-prime Phase F2 consumed §6.5 forward declaration; Round 2 operative trace at §6.4.3

§6.5 forward declaration (originally authored 2026-04-29 BRT pre-Phase-F2-T5) anticipated bucket-B clearance via "Phase F future story T002.2". Round 2 actually-realized trajectory: bucket-B classification was achieved via **Phase F2 IC pipeline post-fix cycle** (T002.6 Phase F2 sub-story; F2-T0..F2-T6 dispatched per Mira F2-T5 §6.2 + §8 + Pax authority ESC-011 R10) — but at sub-classification `costed_out_edge` which is bucket-B FAIL, not PASS, at the deployment-gate threshold (DSR > 0.95 strict per spec v1.1.0 §1 + Anti-Article-IV Guard #4 UNMOVABLE). §6.4.3 above is the **operative Article IV trace** for the Round 2 N7-prime ledger row; §6.5 row content (originally written for "first PASS bucket-B clearance") is **superseded operationally by §6.4.3** for the N7-prime bucket-B classification, while §6.5 row stays as the forward declaration for **future bucket-B PASS-clearance attempt**, which would require either: **(a)** Phase G holdout unlock confirming `costed_out_edge` salvages to deployable Sharpe under OOS — unlikely given in-sample DSR=0.767 strict below 0.95 (Phase G OOS would need DSR > 0.95 to lift Gate 4b PASS, which is structurally improbable given the in-sample regime); **(b)** Phase F3 future cost-side parameter exploration (broker fee renegotiation / cost atlas re-tuning / triple-barrier widening / latency-DMA2 alternative profile / entry-window narrowing) successfully reducing cost-and-friction drag enough to lift CPCV path-level Sharpe distribution above 0.95 strict bar — preserves hold-out lock under Anti-Article-IV Guard #3; **(c)** T002 redirect to alternative thesis with different predictor/horizon/filter producing genuine bucket-B PASS at first-attempt level. Forward research direction adjudication is **Pax authority** (ESC-011 R10) post Mira F2-T5 + Riven F2-T6 (this Round 2 update). Riven Round 2 does NOT pre-empt Pax decision — surfaces the three options consistent with `costed_out_edge` evidence per Mira F2-T5 §8.3.

### 6.6 N8+ → bucket C (forward declaration, NOT YET DEFINED)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | NOT YET DEFINED — Phase G/H deliverable. |
| (b) Governance | ESC-011 R7 + R20 (this post-mortem), Riven §11.5 #1..#7 cumulative pre-conditions for Gate 5. |
| (c) Mira spec | TBD — Phase G/H spec authored downstream of Phase F sign-off. |
| (d) External | Riven persona post-trade attribution protocol (slippage real vs Beckett, latency real vs DMA2 default, fill rate, rejection rate) — Bucket-C P3..P8. |

### 6.7 N8.1 Round 3.1 → bucket A `engineering_wiring` sub `phase_g_unlock_caller_gap` (synthetic-fallback bug; APPENDED 2026-05-01 BRT)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | NO Beckett report (bug-killed run; ~12s wall-time signature of synthetic-walk fall-through, orders of magnitude faster than Phase G real-tape CPCV ~141 min — clear smoke signal of `_walk_session_path` / `_walk_to_exit` fall-through instead of holdout-window parquet consumption). Disposition recorded in this Round 3.1 post-mortem update §2.R3.1.1 + §5.10 anti-pattern definition. |
| (b) Governance | ESC-013 R18 mandate `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` §5(c) — caller-side closure-Literal extension required (`{"E", "F"}` → `{"E", "F", "G"}`) + `holdout_locked=False` propagated for `phase=="G"`; Dex caller-wiring fix (~5-30 LoC `scripts/run_cpcv_dry_run.py:1088-1102`); ESC-013 §3 ratification 5/5 UNANIMOUS APPROVE_PATH_IV. ESC-013 R20 NEW contract test (verdict-vs-reason invariant: K3 PASS reason text MUST contain computed numbers OR be empty under PROPER Phase G unlock; sentinel strings forbidden under PASS path). |
| (c) Mira spec | Mira spec v1.2.0 §15.13 + §15.13.5 Phase G binding clause (extends spec v1.1.0 §15.10 Phase F2 binding clause); §15.13.7 caller-wiring contract; §15.13.8 disposition rule (ESC-013 §5 outcome decision tree binding). Phase G unlock caller wiring is binding pre-condition for any K3 decay COMPUTED-PASS evaluation. |
| (d) External | Riven taxonomy refinement Round 3.1 — synthetic walk admissibility per §1.1 admissibility carry-forward (null-by-construction process; ESC-011 council 5/5 ratified exclusion from bucket-B). N8.1 fall-through to synthetic walk does NOT make it bucket-B candidate; remains bucket-A `engineering_wiring` sub `phase_g_unlock_caller_gap` per Riven taxonomy. |

### 6.8 N8.2 Round 3.1 FINAL → bucket B `strategy_edge` sub `costed_out_edge_oos_confirmed_K3_passed` (PROPER Phase G OOS unlock; APPENDED 2026-05-01 BRT)

| Anchor | Citation |
|---|---|
| (a) Beckett report § | N8.2 run dir `data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/` (run_id `3da49a82343e4650abfd0d4921ee1897`; timestamp_brt `2026-05-01T02:55:55`; wall 141 min 19 s); `full_report.json` with K1+K2+K3 fields populated (K1 DSR=0.205731 line 8; K2 PBO=0.059524 line 9; K3 IC=0.865933 lines 3-7; verdict.reasons=[] empty array line 256; engine-level `kill_decision.verdict='GO'` informational only — Mira spec §1 strict bar is binding deployment threshold per Anti-Article-IV Guard #4 + ESC-012 R3 hash-frozen + ESC-013 R20 contract test). Auxiliary distribution diagnostics OOS (lines 237-246): sharpe_mean=-0.053056, sharpe_median=-0.059359, sharpe_std=0.184340, sortino=-0.121502, mar=0.0, ulcer_index=0.888747, max_drawdown=1.273941, profit_factor=0.929058, hit_rate=0.472377, n_paths=225. Sample-of-sharpe distribution lines 10-235: 225 path-Sharpe values; range [-0.7249, +0.6422]; > 50% paths show negative OOS Sharpe. n_events=3700 (≫ 250 floor; 123× over 30 minimum per spec §15.7 dedup). |
| (b) Governance | Mira F2-T9.1 FINAL verdict `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` `verdict: GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed` `verdict_sub_classification: costed_out_edge_oos_confirmed_K3_passed` (FINAL Round 3.1; supersedes Round 3 INCONCLUSIVE_pending_phase_g_proper + Round 2 `costed_out_edge` + Round 1 `data_quality` per Mira spec v1.2.0 §15 append-only revision discipline; all prior round sign-offs preserved verbatim governance integrity); §1 executive verdict + ESC-013 §5(c) outcome match; §2 threshold table strict (K1 OOS FAIL by 0.744 / K2 OOS PASS / K3 in-sample PASS strict / K3 decay COMPUTED PASS strict per spec v1.2.0 §15.13.5 Phase G full evaluation); §3 N8 surprise DSR=0.965 artifact disambiguation (Phase F-over-holdout vs Phase G unlock proper) + §3.3 DSR sign-flip 0.965 → 0.206 forensic + §3.4 Article IV exemplary protocol-correction chain; §4 IC=0.866 robust OOS interpretation (signal real but costs eat it; cross-window IC stability 0.99991 ≫ 0.5 decay threshold); §5 hit_rate < 50% + sharpe negative + profit_factor < 1 OOS confirmation evidence. ESC-013 5/5 UNANIMOUS APPROVE_PATH_IV ratification (`docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md`) + ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B ratification (`docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` Round 2 → 3 path adjudication) + ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification (Round 1 framing) preserved chain Round 3.1. PRR-20260430-1 (`docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md`) §3.1-§3.4 4-branch disposition rule + ESC-013 §5 outcome decision tree extended for PROPER-Phase-G capability (PRR §3 frames strict-trigger conjunction; ESC-013 §5 specifies disposition under each strict-trigger-failure decomposition; outcome (c) is binding disposition for N8.2 evidence). Quinn QA F2.1 PASS pre-run (`docs/qa/gates/T002.7-f2-qa-gate.md` carry-forward) + Pax T002.7 spec validate carry-forward. |
| (c) Mira spec | Mira spec v1.2.0 §0 falsifiability mandate (the data MUST be allowed to refute) — Round 3.1 HONORS for K1 + K2 + K3 in-sample binding + K3 decay sub-clause (all four honestly measured; K1 OOS strict FAIL is honest measurement against UNMOVABLE bar OOS; K3 decay is COMPUTED PASS by 99% margin OOS). §1 thresholds UNMOVABLE per Anti-Article-IV Guard #4 (DSR>0.95, PBO<0.5, IC>0 with CI95_lower>0; decay sub-clause IC_holdout > 0.5 × IC_in_sample); strict reading applied AS-IS Round 3.1 despite K3 decay COMPUTED PASS — partial-pass at K3 decay does NOT promote at K1 OOS strict FAIL (joint conjunction required per PRR §3.1 R15). §6 sample-size R9 EXCEEDED (3700 OOS events ≫ 250 floor; 123× over 30 minimum per §15.7 dedup invariant; matches `events_metadata.n_events=3700`). §7.1 bucket `strategy_edge` envelope verbatim definition consumed: "Failure attributable to the strategy itself (no economic edge in the WDO end-of-day fade hypothesis under realistic costs+latency)" — refined Round 3.1 to sub-classification `costed_out_edge_oos_confirmed_K3_passed` (Mira F2-T9.1 §1 + §4 + §5 evidence matrix authority; refines Round 2 `costed_out_edge` with explicit OOS confirmation under K3 COMPUTED PASS). §11.2 Anti-Article-IV Guards #1-#8 honored Round 3.1 (no subsample / engine UNCHANGED at runtime / hold-out CONSUMED Round 3.1 [one-shot per ESC-012 R9 + ESC-013 R19; future H_next research must use NEW preregistered window] / thresholds UNMOVED / no source mod / no push / Guard #8 verdict-issuing protocol honored — ic_holdout_status='computed' propagated; verdict.reasons=[] empty; no InvalidVerdictReport raised). §15.13 Phase G binding clause FULLY OPERATIONALIZED Round 3.1: §15.13.2 holdout_locked=False under phase=="G"; §15.13.5 K3 decay sub-clause IC_holdout > 0.5 × IC_in_sample COMPUTED PASS; §15.13.7 caller-wiring contract honored per ESC-013 R18 Dex commit; §15.13.8 disposition rule applied per ESC-013 §5(c) outcome match. |
| (d) External | Bailey-LdP 2014 §3 — DSR/PBO methodology over CPCV distribution honestly wired at `report.py:481-514`; DSR_OOS=0.205731 is **honest economic measurement against UNMOVABLE 0.95 bar OOS**; Round 3.1 measurement is now coherent jointly with K3 in-sample PASS + K3 decay COMPUTED PASS (per spec v1.2.0 §15.13.5 strict reading) so the joint conjunction K1 ∧ K2 ∧ K3_in_sample ∧ K3_decay CAN be coherently evaluated for Phase G OOS verdict — and FAILS strict at K1 OOS (0.205731 << 0.95 by 0.744). Efron 1979 percentile-bootstrap — `info_coef.bootstrap_ci` Round 3.1 invocation honored: 10000 paired-resample iterations with PCG64 seed=42 paired-index strategy produced CI95_OOS [0.864880, 0.866025] non-degenerate (width 0.001145 over n=3700 OOS samples) — confirms wiring works under honest measurement protocol cross-window (IS width 0.000738 over n=3800 vs OOS width 0.001145 over n=3700; ~50% wider OOS reflects slightly smaller n_events). AFML §8.6 IC stability calibration — IC > 0.5 exceptional; observed IS=0.866 + OOS=0.866 cross-window stable at exceptional level; predictor-rank stability hypothesis ROBUSTLY OOS-CONFIRMED. Caveat: AFML §8.6 calibrated for cross-sectional asset returns at daily frequency, not intraday WDO end-of-day fade events — direct comparability loose; exceptional reading checked against thesis Q4+H1 structural predictability hypothesis cross-window. Kelly 1956 / Thorp 2006 §III — Kelly fraction f* = μ/σ² requires distribution of P&L per trade with **honest IC-validated economic edge AND deployable Sharpe distribution**; N8.2 Round 3.1 distribution is **definitively NOT a Kelly-parametrizable substrate** (DSR_OOS=0.206 strict FAIL by 0.744; sharpe_mean=-0.053 NEGATIVE OOS; hit_rate=0.472 sub-50% OOS; profit_factor=0.929 sub-1 OOS — strategy LOSES money OOS gross-of-deployment). Authorized live size remains ZERO contracts post Round 3.1 (carry-forward all prior dispositions; T002 retire ceremony triggers per ESC-013 §5(c) Path C auto-activate). |

### 6.X.R3.1 — Forward declaration: T002 RETIRE per spec §0 falsifiability + ESC-013 §5(c) (APPENDED 2026-05-01 BRT)

> **Section type:** Forward declaration of T002 retire ceremony per ESC-013 §5(c) outcome (c) action prescription. The post-T002-retire research path (H_next epics/stories) operates under a NEW preregistered window per spec §0 falsifiability discipline; the consumed hold-out window [2025-07-01, 2026-04-21] is not reusable.

| Forward action | Authority | Reference |
|---|---|---|
| **T002 RETIRE ceremony** (Path C ESC-012 §5 fallback auto-activate per ESC-013 §5(c)) | Pax (@po) story-creation authority (ESC-011 R10 + ESC-013 §5(c) explicit trigger) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1 "(c) Pax T002.7 close trigger (story status DONE | ARCHIVED per ESC-013 §6 closure conditions row 6)"; `docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md` §3.3 R17 strict reading branch route |
| **Hold-out window [2025-07-01, 2026-04-21] CONSUMED** (one-shot per ESC-012 R9 + ESC-013 R19; future H_next research MUST use NEW preregistered window per spec §0 falsifiability discipline) | Riven custodial gateway authority (R7 §11.5 #5 hold-out lock invariant) + Mira spec authority §0 + ESC-012 R9 + ESC-013 R19 | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §10 closure conditions; `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` R9 verbatim; `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` R19 verbatim |
| **Path A (cost reduction R&D within T002 scope) BLOCKED** per user constraint Path A explicitly OFF | User constraint binding (ESC-013 §5(c) explicit notation) | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §5.3 + §1 "Path A explicitly OFF per user constraint"; ESC-013 resolution §5(c) outcome action prescription |
| **Path B (Phase G OOS confirmation) EXHAUSTED** Round 3.1 per N8.2 PROPER unlock (one-shot consumed) | ESC-012 R9 + ESC-013 R19 (Phase G unlock authority exercised exactly once) | This Round 3.1 update §2.R3.1.2 N8.2 ledger row + §6.8 Article IV trace |
| **Path C (T002 retire + redirect to NEW preregistered H_next research) AUTO-TRIGGER** | ESC-013 §5(c) explicit outcome action; Pax T002.7 close adjudicates redirect direction | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1 + §10 + ESC-013 §5(c) action prescription |
| **Gate 5 LOCKED PERMANENTLY** (capital ramp impossible per spec §0 falsifiability + ESC-013 §5(c) — T002 retire = fence preserved indefinitely; no Gate 5 advancement possible within T002 scope) | Riven custodial §9 HOLD #2 Gate 5 fence authority (R5/R6 conjunction UNSATISFIED PERMANENTLY for T002; ESC-011 OPTION_C 5/5 + ESC-012 R10 + ESC-013 R20 carry-forward) | This Round 3.1 update §2.R3.1.5; companion §9 HOLD #2 Gate 4b NON-DISARM Round 3.1 + Gate 5 LOCKED PERMANENTLY ledger entry in `docs/qa/gates/T002.0g-riven-cosign.md` |
| **Predictor-rank stability hypothesis OOS-CONFIRMED valid-but-undeployable for T002** (institutional knowledge preserved for H_next research direction adjudication; the H1 alternative thesis "end-of-day inventory unwind in WDO produces fade reversion to 17:55 close" is OOS-confirmed at the rank-correlation level via K3 PASS COMPUTED; future H_next research may consume this institutional finding as starting hypothesis under NEW preregistered window) | Mira F2-T9.1 §4 + §5.3 strategic interpretation; Pax forward-research adjudication authority for H_next direction | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §4.3 + §4.4 + §5.3 |
| **Quarter-Kelly REGRA ABSOLUTA preserved Round 3.1** — sizing parametrization NEVER invoked across the entire T002 chain (zero authorized live size at any iteration); haircut policy never engaged; per-trade / per-day / per-week / per-month drawdown budget never engaged; kill-switch thresholds never armed. T002 retires without ever having consumed any sizing-parametrization authority — the discipline held throughout. | Riven persona REGRA ABSOLUTA + Kelly 1956 / Thorp 2006 §III + post-mortem §4 | This Round 3.1 update §4.4 carry-forward (authorized live size = ZERO contracts); companion §9 HOLD #2 Round 3.1 ledger entry sizing_authorization=NONE-FINAL |
| **Article IV exemplary protocol-correction chain preserved** — Round 3 → Round 3.1 chain demonstrates strict-reading discipline against near-miss surprise (N8 DSR=0.965 artifact above 0.95 threshold held to strict scrutiny → ESC-013 5/5 ratified protocol-corrected re-run → N8.2 PROPER Phase G unlock revealed real OOS DSR=0.206 << 0.95 strict FAIL). NO threshold relaxation; NO post-hoc disposition rule mutation; NO favorable interpretation of artifact data retained. The strict reading was preserved through three rounds. | Mira F2-T9.1 §3.4 Article IV exemplary protocol-correction chain; ESC-013 §3 5/5 UNANIMOUS APPROVE_PATH_IV ratification | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §3.4 + ESC-013 resolution §3 |

**Future H_next research direction:** Pax T002.7 close ceremony adjudicates whether H_next is (a) different predictor over different horizon over different filter under NEW preregistered window; (b) preserved predictor `-intraday_flow_direction` under different cost regime / different broker / different exchange / different asset under NEW preregistered window (NOT cost-reduction R&D within T002 scope — different asset/broker/exchange would constitute new thesis); (c) cross-asset H1 generalization under NEW preregistered window; (d) thesis pivot to alternative inventory-unwind microstructure. Adjudication authority = Pax (@po) per ESC-011 R10 + ESC-013 §5(c). Riven custodial constraint Round 3.1: **any H_next direction MUST use NEW preregistered window per spec §0 falsifiability discipline; the [2025-07-01, 2026-04-21] hold-out is exhausted under T002 chain consumption**.

**Riven custodial closure note Round 3.1:** the T002 retire ceremony marks the formal close of the first quant-research thesis chain in this squad's history. The chain produced (a) a fully-instrumented synthetic-vs-real-tape attribution post-mortem (this living document, now retiring with T002); (b) a fully-instrumented IC-pipeline + Phase G unlock + verdict-vs-reason invariant test stack (Mira spec v1.0.0 → v1.1.0 → v1.2.0); (c) an empirically-confirmed predictor-rank stability finding (IC ~0.866 IS+OOS, K3 decay PASS by 99% margin) preserved as institutional knowledge for H_next; (d) a chain of three governance councils ESC-011 + ESC-012 + ESC-013 ratifying the protocol-correction discipline; (e) a Riven taxonomy of four anti-pattern signatures (§5.7 single-leg fire / §5.8 wiring-gap / §5.9 IS-only costed-out / §5.10 F-over-holdout artifact) carried forward as binding for any future Gate 4b chain. The chain produced **zero authorized capital deployment**. The Quarter-Kelly REGRA ABSOLUTA held. The hold-out lock held until Phase G unlock, then was consumed exactly once per ESC-012 R9 + ESC-013 R19 discipline. The strict thresholds UNMOVABLE held through three rounds of near-miss artifact pressure. The thesis is honest about itself: predictor-rank-stable-but-cost-foreclosed — not falsified at the rank level, not deployable at the strict bar. **Sobrevivência antes de retorno.** O caixa segue vivo porque a sequência foi respeitada do início ao fim. The T002 chain closes.

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
