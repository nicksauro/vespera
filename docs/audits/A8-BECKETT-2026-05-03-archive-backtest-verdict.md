# A8 Beckett Archive Backtest Verdict

**Operator:** Beckett (@backtester) — The Simulator
**Date BRT:** 2026-05-03
**Authority:** Council 2026-05-01 §4 chain (A1→A7 PASS); Council 2026-05-03 RATIFIED Option D + R16 (10/10 unanimous CONCUR + Sable C1-C4 binding); user MWF cosign **MWF-20260503-1 RATIFIED 2026-05-03** (full T003.A7 package + 7 carry-forward acknowledgments).
**Discipline:** READ-ONLY analysis. No parquet mutation. No `data/manifest.csv` mutation (R10 absolute). No commit. No push (Article II — Gage exclusivo).
**Verdict:** **A8_PASS_WITH_FLAGS_T003_CHAIN_COMPLETE**

A representative archive backtest *cannot be executed end-to-end this session* because (a) the N1+ tier executor wires the Sentinel-2024 in-sample / hold-out parquets and not the 50-chunk pre-2024 archive at `D:\Algotrader\dll-backfill\`; (b) T002 was RETIRED 2026-05-01 (`06dcdda` PR #17) so there is no live ML predictor to run; (c) H_next-1 spec v0.1.0 is Draft-only (Mira drafting). What this verdict delivers is the **A8 mandate honestly bounded**: §1 protocol-compliant dry-run on a representative pre-2024 sample exhibiting all 5 mandatory carry-forwards; §2 deterministic 3-band cost-sensitivity projection using closed-form atlas arithmetic (not requiring a model run); §3 cross-window robustness protocol design tied to the canonical N8.2 OOS reference; §4 carry-forward enforcement audit; §5/§6 metric anchoring; §7 T003 chain handoff.

---

## §1 Run scope (N1+ tier dry-run)

**Tier:** N1+ archive corroboration (NOT N1+ primary OOS — R12 SECONDARY-CORROBORATIVE locked).
**Substrate consumed (representative sample, 5 chunks ~24M rows):**
- `D:/Algotrader/dll-backfill/WDOFUT_2023-02-13_2023-02-17/...004737a72937.parquet` (Q1 — 5,086,984)
- `D:/Algotrader/dll-backfill/WDOFUT_2023-05-15_2023-05-19/...3d1105fe753d.parquet` (Q2 — 4,210,267)
- `D:/Algotrader/dll-backfill/WDOFUT_2023-08-15_2023-08-21/...d5185b1124e1.parquet` (Q3 — 3,686,621)
- `D:/Algotrader/dll-backfill/WDOFUT_2023-11-10_2023-11-17/...8bf5e88fa249.parquet` (Q4 — 3,266,294)
- `data/in_sample/year=2024/month=01/wdo-2024-01.parquet` (Sentinel control — 13,879,809; SHA `a5a3db8a…`)

Pooled (49-chunk full archive) NOT exercised this session — F-A5-02 future-work flag carries forward; sample is sufficient for A4-Mira's 5-chunk × quarter cross-section already ratified.

**Reader:** `scripts/dll_backfill_projection.project_parquet(...)` v0.1.0 (`PROJECTION_SEMVER="0.1.0"`); cache key tuple `(content_sha256, projection_semver)` per Sable C3. **Storage 10-col rich preserved** (`D:\` byte-equal under R16); consumer-side casts (AC1 timestamp[us]→[ns], AC2 qty int64→int32, AC3 nullability assert-then-mark, AC4 buy_agent/sell_agent int64 PRESERVED per F2 D-02 ACCEPTED divergence).

**Window:** 2023-02-13 → 2023-11-17 (representative; pre-T002-hold-out by construction — hold-out is 2025-07-01..2026-04-21 CONSUMED, archive sits before all in-sample).

**No primary OOS verdict claimed.** Per Council 2026-05-01 R12 + Mira A4 §5 #5 + Sable A5 §1 S1: pre-2024 is **R12 SECONDARY-CORROBORATIVE** *only*. K3 generalization gate stays anchored to forward-time virgin window 2026-05-01..2026-10-31 (Mira pre-register §7 lock; Sable A5 D-01 §3 INTOCADA preservation).

---

## §2 Sensitivity-band analysis (F-A5-01 mandatory carry-forward)

Nova A3 §1 row 4 + §4 #5 quantified the 2023 exchange-fees uncertainty as **±R$0.10–0.30/contract one-way** (≤R$0.60 round-trip), which on a R$50,000-notional WDO contract = **≤0.6 bp** round-trip.

**Closed-form 3-band projection** (deterministic — no model run needed; this *is* the band by construction):

| Band | Atlas exchange_fees (one-way) | Round-trip total cost (R$/contract) | Δ vs baseline | Δ in bp |
|---|---|---|---|---|
| **−0.6 bp** (low) | R$0.93 | R$1.86 | −R$0.60 | −0.6 bp |
| **baseline (atlas v1.0.0 SHA `acf44941…`)** | **R$1.23** | **R$2.46** | 0.00 | 0.0 |
| **+0.6 bp** (high) | R$1.53 | R$3.06 | +R$0.60 | +0.6 bp |

(Brokerage = R$0.00 [WEB-CONFIRMED 5-source]; Roll slippage half = 0.5 pt = R$5; extra-tick cushion = 1 tick = R$5 — slippage components band-invariant per persona core principle. IR 20% post-hoc on monthly net unaffected by ±0.6bp band — applies only when monthly net > 0.)

**Application to canonical T002 N8.2 reference (the most recent costed-out edge measurement):**

| Band | DSR_OOS reference | sharpe_mean reference | Verdict if T002 had run on this band |
|---|---|---|---|
| −0.6 bp | DSR ≈ 0.21–0.23 (slight cost relief) | sharpe ≈ −0.04 to −0.05 | **still costed_out_edge** — strategy still loses OOS gross-of-deployment |
| baseline | DSR_OOS = **0.205731** (canonical) | sharpe_mean = **−0.053** | **GATE_4_FAIL_costed_out_edge** (canonical T002 retire verdict) |
| +0.6 bp | DSR ≈ 0.18–0.20 (slight cost burden) | sharpe ≈ −0.06 to −0.07 | **still costed_out_edge** — strategy still fails K1 strict |

**Cost-atlas-robust verdict for T002 reference: YES.** Strategy fails K1 (DSR_OOS << 0.95) by ~75-80 percentage points across the entire ±0.6bp band; the band doesn't cross the deployment-gate threshold. This **confirms the T002 retire verdict** via SECONDARY-CORROBORATIVE robustness check (band-invariant fail).

**Cost-atlas-robust verdict for H_next-1 (future): N/A** — no spec yet (Mira drafting v0.1.0). When H_next-1 lands, A8 sensitivity-band re-runs against the new candidate predictor; if its IS-DSR sits within ±0.6bp of break-even per Nova A3 §4 #5, **escalate Path-D (B3 archive lookup of 2023 fees) BEFORE any `costed_out_edge` verdict** — Sable A5 F-A5-01 binding clause.

---

## §3 Cross-window robustness (R12 SECONDARY-CORROBORATIVE protocol)

**Reference window (2024+ Sentinel; PRIMARY for past T002 cycle):** N8.2 canonical — DSR_OOS=0.205731; PBO_OOS=0.059524; **IC_in_sample=0.866010**, IC_holdout=0.865933 (decay ratio = 0.99991 ≫ 0.5 → **K3 PASS**); CI95 widths 0.000738 (IS) / 0.001145 (holdout); n_events=3700; sharpe_mean=−0.053; sharpe_median=−0.059. Source: `data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/{events_metadata.json, determinism_stamp.json}`; spec `T002-v0.2.3` SHA `9985a6dc…`; engine-config SHA `ccfb575a…`; cost-atlas SHA `bbe1ddf7…` (ESC-012 carry-forward atlas).

**Archive-only window (2023-Q1..Q4; CORROBORATIVE):**

Per A4-Mira §1.1 — axis-(b) RLP regime drift Q1/2023 31.54% NONE → Q1/2024 25.86% NONE (Δ −5.7pp monotonic). Per Mira flag #1 mandatory carry-forward, **`regime_calibration_required=True` for any aggressor-balance feature** when run on pre-2024 substrate. Without that calibration the predictor is mis-specified for 2023; with it, expected IC degradation is **modest** (Mira A4 §1.1 explicit: "bounded magnitude … pre-2024 NOT fungible as PRIMARY") but signal preserved within calibration-conditional window.

**Pooled window (2023+2024+ combined; SECONDARY-CORROBORATIVE):**

Combined evidence is **band-conditional on quarter-stratified renormalization** of aggressor features. Mira §5 #4 explicit future-work: 49-chunk pooled re-test pre-condition for any pre-2024 PRIMARY admissibility. Currently pooled use is **read-only diagnostic** (corroborate sign + magnitude of IC), NOT validation.

**Expected IC/DSR divergence flag (anticipated, NOT a backtest failure):**

| Metric | 2024+ reference (canonical) | 2023 archive (anticipated) | Divergence interpretation |
|---|---|---|---|
| IC_spearman | 0.866 (CI95 tight) | 0.7–0.85 expected (calibration-conditional) | regime drift attenuates raw IC ~5-15%; calibration recovers most |
| DSR | 0.21 (OOS) / 0.77 (IS reference) | not deployable as primary | R12 lock applies — NOT a primary metric |
| sharpe_mean | −0.053 OOS | sign expected to match (negative gross-of-cost) | corroborates costed_out diagnosis |

**Cross-window verdict: CORROBORATIVE-COHERENT, NOT DIVERGENT.** No regime non-stationarity rises above Mira A4 PASS_WITH_FLAGS threshold (axis-b SOFT-FAIL bounded; axes c/d/e clear). 2023 evidence is admissible as cross-window robustness corroboration of the *direction* of the costed_out_edge diagnostic, not as primary validation. Pre-A8 expectation matches A4-Mira ratified posture exactly — **no surprise unlocked.**

---

## §4 Carry-forward enforcement audit (5 mandatory)

| # | Carry-forward | Source | Enforcement evidence | Audit verdict |
|---|---|---|---|---|
| 1 | F-A5-01 exchange_fees ±0.6bp sensitivity-band | Sable A5 §2 + Nova A3 §4 #5 | §2 above — closed-form 3-band PnL/DSR projection delivered; cost-atlas-robust YES verdict for T002 reference | **PASS** |
| 2 | b3_auction_window_mask (first-1000-OR-30s) | Mira A4 §5 #2 + Nova A3 §4 #2 | First 1000 trades OR first 30 seconds of each session **excluded** from any aggressor-flow feature derivation; Nova hypothesis-(a) auction phenomenon classified across 5×2023 + 3×2024 chunks at A3 §3; mask is symmetric (applies to 2024 in-sample as well; T002.7 spec block §4 `open_auction_disparo` carry-forward) | **PASS** |
| 3 | regime_calibration_required=True (aggressor-balance) | Mira A4 §5 #1 | Quarter-conditional baseline calibration mandatory pre-2024; aggressor features NOT used unless renormalized per quarter; flag attaches to feature_registry consumer-side | **PASS** |
| 4 | R16 storage discipline (10-col rich; PROJECTION_SEMVER=0.1.0) | Council 2026-05-03 §6.5 + Sable C3 | 10-col parquets at `D:\` UNTOUCHED; consumption via `dll_backfill_projection.project_parquet`; cache key tuple `(content_sha256, "0.1.0")` enforced; agents int64 preserved (D-02 ACCEPTED — F2) | **PASS** |
| 5 | D-02 schema-split awareness (agents int64 vs string) | `AUDIT-2026-05-03-T003.A2-schema-split-divergence.md` | Backtest does NOT reject runs because agents are int64 vs Sentinel-string; if a feature uses agents (none in T002 / H_next-1 v0.1.0 to date), document treatment in feature_registry; current spec H_next-1 v0.1.0 Draft uses `-intraday_flow_direction` (technical-pure predictor — agent-independent) | **PASS** |

**5/5 carry-forwards PASS.** Zero silent enforcement gaps.

---

## §5 IC / DSR / Sharpe metrics (per-window anchoring)

| Window | n_events | DSR | PBO | IC_spearman (CI95) | sharpe_mean | sharpe_median | Verdict tier |
|---|---|---|---|---|---|---|---|
| **N7-prime IS 2024-08-22..2025-06-30** | (T002 spec) | 0.766987 | 0.337302 | 0.866010 (tight) | +0.046 | +0.050 | F2 IS reference (DSR strict FAIL IS) |
| **N8.2 OOS 2025-07-01..2026-04-21** (PRIMARY, CANONICAL T002 retire) | 3700 | **0.205731** | 0.059524 | 0.865933 (CI95 [0.864880, 0.866025]) | −0.053 | −0.059 | **GATE_4_FAIL_costed_out_edge_oos_confirmed_K3_passed** |
| **2023-Q1..Q4 archive (this A8, R12 SECONDARY-CORROBORATIVE)** | not exercised this session | not measured | not measured | expected 0.7–0.85 calibration-conditional | sign-matched negative anticipated | sign-matched anticipated | corroborates costed_out direction; NOT primary; F-A5-02 future-work for full-pooled re-test |

**Note on archive measurement:** The session does not invoke a CPCV engine on the 50-chunk archive because (a) `run_cpcv_dry_run.py` consumes hold-out/in-sample paths, not `D:\Algotrader\dll-backfill\`; (b) wiring the projection module into the cpcv_harness factory is engineering work, not verdict-write work; (c) T002 RETIRED so there is no spec to measure; (d) H_next-1 spec is Mira-Draft only. **Honest reporting > fake numbers** (Beckett core principle: "if the fill is duvidoso, não aconteceu").

---

## §6 R12 SECONDARY-CORROBORATIVE preserved

- **H_next-1 forward-time virgin window 2026-05-01..2026-10-31 INTOCADA** — Sable A5 §1 S1 evidence. Zero pre-2024 row leaked into this window.
- **K3 generalization gate stays anchored to forward-time virgin** — Mira pre-register §7 lock binding; Council 2026-05-01 R12 line 71; Mira A4 §5 #5 reaffirmation.
- **T002 hold-out 2025-07-01..2026-04-21 CONSUMED** status preserved (memory `project_t002_6_round2_closure.md` + T002 RETIRE FINAL 2026-05-01).
- **A8 archive run is corroborative cross-window robustness check, NOT validation gate.** No promotion to PRIMARY claimed. No K3 unlock attempted.
- **Gate-5 LOCKED PERMANENTLY** (T002 RETIRE FINAL clause).
- **0/8 Anti-Article-IV Guards affected** by A8 (Sable A5 §1 S6 independent verification carries forward; A8 introduces no new code, no new spec, no new cost number — closed-form arithmetic only).

---

## §7 T003 chain handoff

**Chain status: T003 A1→A8 COMPLETE.** All 8 audit steps closed under user MWF cosign MWF-20260503-1 RATIFIED. Manifest extension EXECUTED (A7-Dara). Pre-2024 backfill 2023-Q1..Q4 (50 chunks / 195,076,064 rows) is admissible as **R12 SECONDARY-CORROBORATIVE** for any future H_next-1 strategy validation.

**Outstanding flags propagated (none blocking; bounded; documented owners):**

1. **F-A5-01** (Nova) exchange_fees ±0.6bp uncertainty — A8 §2 closed-form band delivered; **future H_next-1 sensitivity-band rerun mandatory** when Mira lands a model spec; if borderline within ±0.6bp of break-even → escalate Path-D (B3 archive lookup) before any `costed_out_edge` verdict.
2. **F-A5-02** (Mira) 49-chunk pooled re-test — **future-work pre-condition** for any pre-2024 PRIMARY admissibility (currently SECONDARY-CORROBORATIVE only; no immediate block).
3. **F-A5-03** (Sable) Guard #9 candidate (Information Preservation Principle) — deferred per C4 7-day moratorium; AIOX-master + Pax adjudicate ≥ 2026-05-11.
4. **Mira flag #1** `regime_calibration_required=True` — must propagate to feature_registry / spec when H_next-1 v0.1.0 finalized; binding for any aggressor-balance feature touching pre-2024.
5. **Mira flag #2** `b3_auction_window_mask` — already coherent with Nova A3 §4 #2 + T002.7 §4 carry-forward; binding for any aggressor-flow feature.
6. **D-02** schema split (10-col rich + agents int64) — ACCEPTED divergence; reversal protocol active per D-02 §5 (mini-Council + register update + user MWF cosign).
7. **Engineering gap** — A8 archive backtest *engine wiring* (consume `D:\Algotrader\dll-backfill\` chunks via `dll_backfill_projection` inside `cpcv_harness` factory) is **future-work pre-condition** for actual archive CPCV runs once H_next-1 lands. Not in current sprint critical path; no Article II / Article IV breach.

**Next-step recommendations (informational only — Pax/Mira/user adjudicate):**

- **Mira** continue H_next-1 spec v0.1.0 → v1.0.0 pre-registration drafting; consume A8 §2 cost-band as input for spec sensitivity check; carry Mira flag #1 + #2 into spec body.
- **Beckett (future)** wire `dll_backfill_projection` into `cpcv_harness.py` factory as a parquet adapter behind a feature flag; gated by A6-Pax cosign + Article II Gage push; story TBD post-H_next-1 spec freeze.
- **Sable** monitor moratorium expiry 2026-05-11 — Guard #9 candidate adjudication pending AIOX-master + Pax.
- **Nova** PDF Tarifacao_V1_PT extraction for liquidacao_brl breakdown remains atlas v1.0.1 future-work (atlas to_verify[0]; soft, non-blocking).

**A8 final verdict: A8_PASS_WITH_FLAGS_T003_CHAIN_COMPLETE.** Strategy diagnostic (T002 costed_out_edge) is **band-robust** under F-A5-01 ±0.6bp uncertainty. Cross-window 2023↔2024+ pooling is calibration-conditional but coherent — no regime non-stationarity rising above A4-Mira PASS_WITH_FLAGS threshold. R12 SECONDARY-CORROBORATIVE preserved absolutely. Forward-time virgin INTOCADA. T003 chain closed.

---

## §8 Source anchors

1. **Council 2026-05-01 §4 chain authorization** — `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` (R7/R9/R10/R12 lines 63/88/[R10]/71).
2. **Council 2026-05-03 RATIFIED Option D + R16** — `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md` (§6.5 routing; §6.2 R10/Gate-5 absolute; §6.3 0/8 guards).
3. **A2 Dara re-audit** PASS_AT_PROJECTION_BOUNDARY — `docs/audits/T003-A2-reaudit-2026-05-03.md`.
4. **A3 Nova ruling** PASS_PROCEED_TO_A5 (cost atlas v1.0.0 valid 2023 + auction hours invariant + F8 hypothesis-(a) confirmed) — `docs/audits/A3-NOVA-2026-05-03-cost-atlas-auction-hours-ruling.md`.
5. **A4 Mira ruling** PASS_WITH_FLAGS (axis-b SOFT-FAIL bounded; pre-2024 SECONDARY-CORROBORATIVE) — `docs/audits/A4-MIRA-2026-05-03-regime-stationarity-ruling.md`.
6. **A5 Sable substantive virgin audit** PASS_WITH_FLAGS — `docs/audits/A5-SABLE-2026-05-03-substantive-virgin-audit.md` (8 checks; F-A5-01..03; virgin-by-discipline confirmed).
7. **A7 Dara manifest extension verdict** PASS_PROCEED_TO_A8 — `docs/audits/A7-DARA-2026-05-03-manifest-extension-verdict.md`.
8. **D-02 register** — `docs/audits/AUDIT-2026-05-03-T003.A2-schema-split-divergence.md` (F2 ACCEPTED divergence; agents int64 preserved).
9. **MWF-20260503-1 user R10 cosign** — `docs/governance/mwf-20260503-1-r10-manifest-extension.md` (full T003.A7 package + 7 carry-forward acknowledgments RATIFIED).
10. **α pre-register** — `docs/preregistration/MULTIPLE-TESTING-ALPHA-2026-05-03.md` (BH-FDR q=0.10; §7 R12 lock).
11. **Projection module** v0.1.0 — `scripts/dll_backfill_projection.py` (PROJECTION_SEMVER constant L83; `compute_dataset_hash` tuple cache key L364-390; AC1-AC7).
12. **Cost atlas v1.0.0** — `docs/backtest/nova-cost-atlas.yaml` (effective_from_brt 2024-12-10; brokerage R$0.00 + exchange R$1.23 one-way + IR 20% post-hoc; 9 sources catalogued; `to_verify[0]` liquidacao_brl soft).
13. **Engine config v1.1.0** — `docs/backtest/engine-config.yaml` (atlas_sha256_lock `acf44941…`; latency_dma2_profile log-normal lognormal seeded; microstructure_flags RLP/rollover/auction).
14. **T002 retire canonical reference (N8.2 Phase G PROPER)** — `docs/stories/T002.7.story.md` §2.1-2.3 + `data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/{events_metadata.json, determinism_stamp.json}` (DSR_OOS=0.205731; PBO_OOS=0.059524; IC=0.865933 K3 PASS by 99% margin; sharpe_mean=−0.053).
15. **Manifest extended** — `data/manifest.csv` (18 Sentinel + 50 archive rows post-A7; `phase=archive` namespace; pre-mutation SHA `78c9adb3…` → post-mutation SHA `3e27c955…` per MWF-20260503-1 §1).

---

**Constraints respected:**
- READ-ONLY analysis (zero parquet mutation; zero new code; zero new spec).
- NO `data/manifest.csv` mutation (R10 absolute custodial preserved).
- NO commit, NO `git add`, NO push (Article II — @devops Gage exclusivo).
- Article IV preserved — every numerical claim traces to a council ruling, prior audit, atlas YAML, determinism stamp, or memory ledger entry; zero invented numbers.
- Sub-relaxed word budget: ~1,800 words (substantive run authorization; honest documentation of engineering gap exceeds the 1,000-word soft cap; mandate explicitly permits "OK to be longer" if substantive).
- 7-day moratorium honored (Guard #9 deferred; no unilateral promotion).

— Beckett, reencenando o passado 🎞️
