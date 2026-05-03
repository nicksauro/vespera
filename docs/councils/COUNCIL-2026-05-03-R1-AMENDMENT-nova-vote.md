# Nova Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Nova (@market-microstructure)
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored to amendment doc, spike JSONs, original Council R6/R7/R8, public B3/macro record. Speculation rotulada [INTERPRETATION]. Spec numbers tagged per glossary discipline.

---

## §1 Verdict + reasoning

APPROVE_WITH_CONDITIONS. The amendment is microstructure-bounded *acquisition-only* — it does NOT pre-judge whether 2023 data is regime-equivalent for OOS use; that question stays under R7 (Mira) and R6/R8 (mine, downstream). Within those guardrails, expanding to 2023-01..2024-01 is operationally sound: spike protocol (5/6 dates, 670k–990k trades, reached_100=true) ratifies retention HYPOTHESIS [Source: spike-summary-S1a/S1b/retry-0315.json]; R12 keeps pre-2024 SECONDARY-CORROBORATIVE only [Council 2026-05-01 R12]; Anti-Article-IV Guards 0/8 affected [Amendment §3]. R14 and R15 explicitly gate downstream rulings on my authority lenses (auction hours, cost atlas) before any A2-Dara dispatch — that is the right ordering.

I do NOT have empirical 2023 confirmation for several of my own R6/R8 obligations. Hence APPROVE_WITH_CONDITIONS rather than unconditional APPROVE: my downstream rulings remain BLOCKING gates, not pre-cleared.

## §2 Conditions

- **C1 (R8 carry-forward):** Acquisition may proceed; my A3-Nova auction-hours ruling pre-2024 must complete before any feature/backtest computation that timestamps phase boundaries (open/call). B3 PUMA archived schedules are [TO-VERIFY] — do not assume 2023 grade equals current 08:55-pre/09:00-open/17:55-call.
- **C2 (R6 carry-forward):** Cost atlas v1.0.0 (effective_from_brt 2024-12-10) is [TO-VERIFY] for 2023; A3-Nova ruling must adjudicate before Beckett N1+ archive run uses 2023 chunks.
- **C3 (Rollover discipline):** A2-Dara schema parity must verify WDOFUT continuous synthesis across 2023 month-boundaries (esp WDOZ23→WDOG24 in late Dec 2023) does not silently drop trades or produce price discontinuities mis-labeled as agressão.
- **C4 (Aggressor 25% threshold):** The lowered threshold (`_validate_first_1000` auction-tolerant) is acceptable as a probe-level smoke check; A4-Mira regime audit must compute *full-day* aggressor distributions (not first-1000) for each 2023 quarter and compare to 2024-Q4 baseline before pre-2024 enters any predictor evaluation.
- **C5 (R14 binding):** S1-retry-0915 must execute and 2023-03-15 qfd=73,657 root cause must be characterized BEFORE A2 dispatch, as amendment already mandates. If qfd is structural (reproducible on macro-event days), A4-Mira receives a data-quality flag for regime stationarity ruling.

## §3 Concerns + mitigations (per 6 audit points)

1. **Auction hours pre-2024.** B3 grade changed multiple times around DST policy and pandemic-era schedule adjustments. B3_HOLIDAYS_2023_2024 frozenset only addresses *dates*, not *intraday phase boundaries*. [INTERPRETATION] my 2023 auction-window confidence is [TO-VERIFY]. *Mitigation:* C1 — A3-Nova ruling blocks feature timestamping until verified against B3 PUMA archived schedules or empirical first/last-trade analysis per chunk.

2. **RLP regime 2023.** RLP exists in 2023 [WEB-CONFIRMED — RLP program live since 2019 per atlas]. However, lift conditions, eligible flow categories and tradeType=13 share-of-volume have evolved; 2023 RLP volume share is [TO-VERIFY]. *Mitigation:* A4-Mira axis (b) explicitly covers this; my RLP_GUIDE.md must annex a 2023-vs-2024 share-comparison appendix before pre-2024 enters CVD/imbalance features.

3. **Rollover quirks pre-2024.** WDOFUT continuous logic in ProfitDLL is [TO-VERIFY] for 2023. WDOZ23→WDOG24 transition late Dec 2023 is the highest-risk roll (year-end, holiday-thinned book, possible PTAX-session anomalies). *Mitigation:* C3 — A2-Dara verifies continuous synthesis byte-equal to current WDOFUT semantic; my rollover atlas requires explicit 2023 mapping table before Beckett uses 2023 data for any cross-roll feature.

4. **Spread regime 2023.** [INTERPRETATION] WDO bid-ask in 2023 was likely structurally similar (mini contract, same matching engine PUMA, same tick=0.5pt) but realized spread is sensitive to volatility regime and HFT participation, both of which differ. Empirical claim deferred to A3-Nova cost-atlas ruling. *Mitigation:* C2 — atlas v1.0.0 [TO-VERIFY] pre-2024; if invalid, atlas v0.x.x archival variant required before Beckett costed-out evaluation.

5. **Spike 0315 qfd=73,657 microstructure interpretation.** 2023-03-15 was Selic decision week + global SVB/Credit Suisse banking turmoil aftermath [WEB-CONFIRMED public record]. Trade volume on retry (990,223) is ~33% above the 670k–772k baseline of other 2023 spike dates — consistent with macro-event volume surge. [INTERPRETATION] qfd is most likely DLL queue-throughput limit hit by *legitimately elevated* volume (microstructure-real), not a microstructure artifact per se. *Mitigation:* C5 / R14 — characterize structural-vs-stochastic; if reproducible on macro-event days, A4-Mira receives flag and bulk run policy may add per-chunk qfd ceiling tighter than 0.1% for high-vol days.

6. **Aggressor distribution validity (25% threshold).** The threshold is tolerant of the first-1000-trades window which can be auction-batch-heavy. [INTERPRETATION] 2023 first-trade composition should not differ structurally from 2024 (same auction mechanism PUMA), but I cannot pre-assert this. *Mitigation:* C4 — full-day aggressor distribution per quarter required before pre-2024 enters any flow-based feature; the 25% smoke threshold is NOT a regime-equivalence proof.

## §4 Source anchors

- Amendment: `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md` §1.1, §1.2, §2.1, §3
- Spike data: `data/dll-probes/SPIKE-NELO/spike-summary-S1a.json`, `S1b.json`, `S1-retry-0315.json`
- Original council: `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` R6, R7, R8, R12
- Microstructure atlas (Nova): trade-types-atlas (RLP=13), session-phases (08:55/09:00/17:55), rollover rules (WDO monthly F-Z cycle), cost atlas v1.0.0 effective 2024-12-10
- Public macro: SVB collapse 2023-03-10..15, Credit Suisse / UBS 2023-03-19, Selic 2023-Q1 cycle [WEB-CONFIRMED]

— Nova, microstructure authority, ballot self-audited 2026-05-03 🔭
