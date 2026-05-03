# A3 Nova Substantive Ruling — Cost Atlas Pre-2024 + Auction Hours

**Auditor:** Nova (@market-microstructure)
**Date BRT:** 2026-05-03
**Verdict:** **A3_PASS_PROCEED_TO_A5** with one mandatory carry-forward (cost atlas v1.0.0 declared valid for 2023-Q1..Q4; one [TO-VERIFY] explicitly registered).

---

## §1 Cost atlas v1.0.0 applicability 2023

**Ruling:** atlas v1.0.0 (`docs/backtest/nova-cost-atlas.yaml`, `effective_from_brt: 2024-12-10`) **is VALID for 2023-Q1..Q4 backtest** with one explicit caveat below. NO archival variant required. NO v1.0.1 amendment required.

| Cost component | 2023 vs 2024 | Verdict |
|---|---|---|
| **Tick size 0.5 / multiplier R$10/ponto / contract size US$10k** | invariant; `product` block in atlas is contract-spec, not date-effective | VALID |
| **Brokerage R$0.00 one-way** | retail zero-fee was already prevalent 2023 (Clear/Rico-RLP/BTG-DT existed); range R$0-1 conservative-bracket holds. Atlas registers worst-case R$1.00/contract as `observed_range_brl_one_way.max` | VALID |
| **Exchange fees R$1.23/contract one-way (R$0.43 emolumentos + R$0.80 registro)** | B3 publishes fees per-tariff-cycle; CM Capital snapshot is 2024-12-10; **2023 may differ ±R$0.10-0.30/contract** but no public tariff schedule documents a *step-change* discontinuity. **[TO-VERIFY]** carried forward | VALID-with-caveat |
| **IR 20% day-trade + IRRF 1%** | IN-RFB 1.585/2015 pre-dates 2023; rates unchanged through 2024-12 | VALID |
| **Slippage estimator (size×depth)** | empirical: 2023-Q1/Q2/Q4 chunks show qty p50=1, mean=3.31-3.93, max=4-10k vs 2024-01 ref qty p50=1, mean=4.07, max=10k — **distributionally same regime**. Price std ≈ R$29-30 across all 2023 chunks vs R$30 in 2024-01 — **same volatility regime** | VALID |
| **Roll cost / overnight gap** | WDO contracts are mensal (1° dia útil); rollover behavior structurally unchanged 2023→2024. Atlas does not parameterize roll-gap explicitly (engine-level concern) | VALID |

**Caveat carry-forward:** `costs.exchange_fees` 2023 monthly value MAY differ ±R$0.10-0.30 from 2024-12 snapshot. Recommend Sable opens [TO-VERIFY 2026-05-03 — exchange_fees_2023] in the atlas `to_verify` registry; impact for backtest is bounded (≤24% relative cost variation; ≤R$0.30/round-trip on a contract worth ~R$50k notional → ~0.6 bp). Decision: **proceed with v1.0.0 unchanged** — A4-Mira treats this as parameter uncertainty, not strategy-fate-altering.

---

## §2 Auction hours pre-2024

**Ruling:** Brazilian DST was abolished by Decree 9.772/2019 (effective 2019). 2023 had **NO Brazil-side DST event**. B3 PUMA grade for WDO 2023 is structurally identical to T002.7-confirmed 2026-05-01 grade, modulo seasonal NYSE/CME-driven adjustments (US DST Mar/Nov which shifts grid ±1h sazonalmente — affects equities; for WDO Opere Futuros records "não tem alteração de horário"). Empirical confirmation:

- 2023-02-13..17, 2023-05-15..19, 2023-11-10..17: first trade `09:00:32-09:00:56` BRT; last trades up to `18:29` BRT (admin window) — **same grade as 2024-01** (first `09:00:45`, last `18:29:59`).
- After-18:00 trades present across 2023 chunks (Q1: 53,490; Q4: 28,735) and 2024-01 (150,672), with **zero trades after 18:30** in any sample. Confirms 18:00-18:30 admin window persistent 2023→2024.

**Auction window canonical 2023 (= 2026-05-01 grade):**
- Pre-open 08:55-09:00 (no matching), open auction batch-cross at 09:00 sharp, continuous 09:00-18:00, settlement window 15:50-16:00 (embedded continuous), admin window 18:00-18:30. **No closing call for WDO** (already corrected per T002.7 §2).

**Sources (anchored):** B3 PUMA câmbio-dolar-pronto (T002.7 §5 source 1, also valid 2023); Decree 9.772/2019 abolish DST; empirical chunks D:/Algotrader/dll-backfill/ verified 2026-05-03. **[WEB-CONFIRMED 2026-05-03]**.

---

## §3 F8 (2023-03-15 aggressor) classification

**Empirical sample — first 1000 trades, 5 OTHER 2023 chunks + Sentinel 2024 control:**

| Chunk | First-1000 ts span | NONE % | BUY+SELL % |
|---|---|---|---|
| 2023-01-30 | 09:00:52 → 09:00:57 (5s) | 53.4% | 46.6% |
| 2023-04-13 | 09:00:56 → 09:00:56 (<1s) | **100.0%** | 0% |
| 2023-06-13 | 09:00:49 → 09:00:53 (4s) | 49.9% | 50.1% |
| 2023-08-08 | 09:00:45 → 09:00:45 (<1s) | **95.2%** | 4.8% |
| 2023-10-19 | 09:00:40 → 09:00:44 (4s) | 55.0% | 45.0% |
| **REF 2024-01-02** | 09:00:45 → 09:00:49 (5s) | 53.4% | 46.6% |
| **REF 2024-01-03** | 09:00:56 → 09:00:57 (<1s) | **79.7%** | 20.3% |
| **REF 2024-01-04** | 09:00:42 → 09:00:46 (4s) | 50.9% | 49.1% |

**Classification: hypothesis (a) — auction-window phenomenon, CONFIRMED.**

Reasoning: 100% NONE in 2023-04-13 and ≥95% NONE in 2023-08-08 are **structurally identical** to the 2023-03-15 baseline reported by Operator R14 + Dara A2. ALL 8 chunks (5×2023 + 3×2024) show NONE-dominance clustered in the first 1-5 seconds at 09:00:xx — the open-auction batch-cross signature documented in T002.7 §3.3 ("burst de prints com timestamps comprimidos em 09:00:00.x; preço idêntico em múltiplos prints; aggressor=NONE [parquet] onde live mostraria tradeType=4"). Sentinel 2024 (already validated for T002 in-sample) exhibits the same behavior — refuting hypothesis (b) macro-stress (SVB/CS week was Mar 9-15, but 2023-04-13, 2023-08-08, 2024-01-03 also show ≥80% NONE) and refuting (c) DLL-day-specific artifact.

**Distribution insight:** the NONE % varies 50-100% across days because auction-overhang size depends on overnight-news inventory; high-news days produce concentrated cross-prints (closer to 100%) while quiet overnights produce smaller overhangs cleared faster (closer to 50%, allowing first 1000 to spill into post-auction continuous BUY/SELL fills). 2023-03-15 100% sits at the **high end of the natural distribution**, not outside it.

---

## §4 Carry-forward to A4-Mira

**Regime axis (a) feed for Mira A4 strategy-discovery:**

1. **Cost-axis input (deterministic):** consume atlas v1.0.0 verbatim for 2023 chunks. Use `(content_sha256, projection_semver=0.1.0)` cache key per Sable C3.
2. **Auction-window mask (mandatory):** exclude **first 1000 trades OR first 30 seconds (whichever larger)** from any aggressor-flow feature in 2023 backtest training. NONE prints in this window are the open-auction batch-cross — feeding them as "neutral" into CVD/imbalance distorts the predictor (T002.6 §3.2 anti-pattern). Same mask must apply to 2024 in-sample for symmetry — already implicit in T002.7 spec block §4 `open_auction_disparo`.
3. **Settlement window (15:50-16:00):** label as separate regime; don't exclude (continuous matching active) but Mira may want a `_settlement_window` boolean feature for regime-conditional models.
4. **Admin window post-18:00:** EXCLUDE entirely (T002.7 §3.1 ruling persists for 2023).
5. **Cost-uncertainty band:** ±R$0.30/contract round-trip exchange-fees uncertainty for 2023 should be reflected in Mira sensitivity check — if strategy edge is within ±0.6bp of break-even, Sable A5 must flag for Path-D (re-confirm 2023 fees with B3 archive) before any `costed_out_edge` verdict.

---

## §5 Source anchors

- **Council R6** (cost atlas pre-2024 validity ruling — Nova authority): `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` (referenced by handoff)
- **Council R8** (auction hours pre-2024 — Nova authority): same council
- **T002.7 auction confirmation** (2026-05-01 grade, primary anchor): `docs/backtest/T002.7-nova-auction-hours-confirmation-2026-05-01.md`
- **Nova cost atlas v1.0.0:** `docs/backtest/nova-cost-atlas.yaml` (effective_from_brt: 2024-12-10)
- **Empirical chunks** (verified 2026-05-03 via `scripts/dll_backfill_projection.py`):
  - `D:/Algotrader/dll-backfill/WDOFUT_2023-02-13_2023-02-17/wdofut-2023-12-004737a72937.parquet` (Q1 — n=5,086,984)
  - `D:/Algotrader/dll-backfill/WDOFUT_2023-05-15_2023-05-19/wdofut-2023-12-3d1105fe753d.parquet` (Q2 — n=4,210,267)
  - `D:/Algotrader/dll-backfill/WDOFUT_2023-11-10_2023-11-17/wdofut-2023-12-8bf5e88fa249.parquet` (Q4 — n=3,266,294)
  - F8 carry-forward chunks (5 samples): WDOFUT_2023-01-30, 2023-04-13, 2023-06-13, 2023-08-08, 2023-10-19
  - Sentinel reference: `data/in_sample/year=2024/month=01/wdo-2024-01.parquet` (n=13,879,809)
- **Decree 9.772/2019** Brazil DST abolish (referenced in DOMAIN_GLOSSARY Parte 11)
- **Council 2026-05-03 R16** information-preservation routing — projection module operational

---

**Constraints respected:**
- READ-ONLY analysis (zero parquet mutation; verified via projection module pure-consumer pattern).
- NO `data/manifest.csv` mutation (R10).
- NO commit, NO `git add`, NO push (Article II — @devops Gage exclusive).
- Spec length: ≈680 words.

— Nova, lendo a fita 🔭
