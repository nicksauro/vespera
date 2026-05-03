# Nova ballot — Council 2026-05-03 Schema Resolution

**Voter:** Nova (@market-microstructure) — The Reader
**Authority lens:** Microstructural value of broker identity for B3 WDO/WIN tape
**Date (BRT):** 2026-05-03
**Self-audit:** Independent of other ballots (Article IV)

---

## Vote: **Option D** + **R16 CONCUR**

---

## §1 Broker identity for WDO microstructure — necessary, useful, or noise?

**USEFUL, not necessary — and dangerous if conditioned on prematurely.**

- **Aggressor semantics (tradeType=2/3):** broker ID is ORTHOGONAL. The agressor flag itself carries the directional bit. Knowing "XP cruzou" doesn't change that compra agredida = bullish flow.
- **Cross-trade attribution (tradeType=1):** broker DOES matter — same-broker cross is structurally non-directional. But this is INTRA-broker logic, not broker-identity-as-feature.
- **RLP regime (tradeType=13):** RLP is a B3 program flag, NOT a broker-identity feature. tradeType=13 already isolates it. Broker name on top is decoration.
- **Smart-money tier:** THIS is where broker identity bites — institutional desks (BTG, Itaú BBA, Morgan, Goldman) vs retail-heavy (XP, Clear, Modal). Real signal exists here in WDO. But it's a SECOND-ORDER feature, not load-bearing for first-pass thesis.

**Verdict:** broker is condiment, not protein. H_next-1 should not be built around it.

## §2 Non-stationarity 2023→2024 — magnitude estimate

**HIGH and structurally documented.** Conditioning on broker 2023 → expect alpha decay 2024.

- **XP:** retail growth ~3-5x 2020-2024; broker behavior signature changed materially
- **BTG:** strategy rotation post-acquisitions (Necton 2021, Ourinvest); flow profile drifted
- **Itaú BBA:** desk reorganizations 2022-2023; market-making allocation changed
- **Mergers:** Spinelli, Necton, Genial consolidations — broker codes effectively renamed/merged
- **B3 broker-code reassignments:** happen quietly via ofício circular

A feature like `broker_BTG_aggressor_share` measured in 2023 is NOT the same statistical object in 2024. This is precisely the **non-stationary regime risk** Mira flags as VPIN/PIN-style trap.

**Risk if we condition early:** false alpha 2023 → null 2024 OOS → wasted dry-runs (we have ONE holdout left after T002 retire).

## §3 Cost atlas pre-2024 (R6) — broker-agnostic?

**Atlas is broker-AGNOSTIC by design.** Cost atlas computes spread proxy (Roll), tick-cost (R$ 10/ponto WDO mini), exchange fees, slippage from tape size×depth — NONE of which require broker ID. Broker identity does NOT feed into atlas math. Confirms Option D viability.

## §4 10-col rich preservation — useful for any feature I'd compute?

**YES — `vol_brl`, `trade_number`, `ts_raw` ALL load-bearing for trades-only features:**

- `vol_brl` (dVol R$): exact dollar-CVD without recomputing price×qty×multiplier (multiplier is [WEB-CONFIRMED] R$10/ponto WDO but [TO-VERIFY] for full DOL — pre-computed dVol is custodial truth)
- `trade_number` (nTradeNumber): only ground-truth for ordering ties at us-resolution timestamps; required for VPIN bucket boundaries and Hawkes inter-trade time stats
- `ts_raw`: BRT preservation (R-fase de pregão depende disso); fase classification breaks if we lose sub-second BRT

Drop these → I lose Roll-spread proxy precision, VPIN bucket integrity, and dollar-CVD audit trail.

## §5 R16 — does it help or constrain?

**STRONGLY HELPS.** R16 codifies what I already enforce in feature audits: *consumer projects, custodial preserves*. Storage as registry-of-record + projection at consumption is exactly the discipline that prevents "we should have kept that field" regret 6 months in. **CONCUR.**

---

## Final ballot

| Field | Value |
|---|---|
| Option | **D — defer broker decision, technical-only path now** |
| R16 | **CONCUR** |
| Conditional flip to B/C | Only if Mira H_next-1 explicitly requires broker conditioning AND survives stationarity audit |

— Nova, lendo a fita
