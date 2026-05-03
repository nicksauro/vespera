# MWF-20260503-1 — R10 Manifest Extension Ruling (T003.A7)

**Date BRT:** 2026-05-03
**Authority:** User R10 absolute MWF cosign holder (supreme authority)
**Decision:** **(1) APPROVE** — full T003.A7 cosign package ratified
**Status:** RATIFIED 2026-05-03

---

## §1 What this ruling authorizes

User MWF cosign for R10 absolute custodial mutation of `data/manifest.csv`:

- **Append-only addition** of 50 archival rows for 2023-Q1..Q4 WDOFUT pre-2024 backfill (~195,076,064 trades)
- **`phase=archive`** column value (separate namespace from existing Sentinel `phase` values)
- **Source data:** `D:\Algotrader\dll-backfill\` (off-repo external HD; backfill manifest v1.1)
- **SHA256 byte-equal verified** pre/post on existing 18 Sentinel rows (R10 paranoia check)
- **Pre-mutation SHA256:** `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`
- **Post-mutation SHA256:** `3e27c955b3cd9cb6a6fbb67c77c07ce55d37cd2223dc41796d6af24da76d0ba4`

## §2 Authority chain

This MWF ruling references and ratifies:

1. **Council 2026-05-01 R5/R6/R7/R8/R9/R10/R12** — original schema parity + cost atlas + regime + auction + virgin + custodial + secondary-corroborative clauses
2. **Council 2026-05-03 R1 Amendment** — bulk-backfill window expansion 2023-01-01..2024-01-01 (RATIFIED 6/6 + user MWF prior cosign)
3. **Council 2026-05-03 Schema Resolution + R16** — RATIFIED Option D + R16 Information Preservation Principle (10/10 R16 + user MWF Option D tiebreaker)
4. **A2-A7 audit chain** — Dara A2 re-audit / Nova A3 / Mira A4 / Sable A5 verdicts, all PASS or PASS_WITH_FLAGS, no FAIL
5. **A6-Pax cosign request package** — 10-point GO 9/10, 7 carry-forward acknowledgments compiled

## §3 Carry-forward acknowledgments accepted

User explicit acceptance of all 7 flags:

1. **F-A5-01** Nova exchange_fees ±0.6bp uncertainty → A8-Beckett mandatory sensitivity-band
2. **Mira axis-(b) RLP REJECT** bounded -5.7pp NONE share drift → SOFT-FAIL pre-reg §2 NOT kill-switch; R12 SECONDARY-CORROBORATIVE locked
3. **Mira flag #1** aggressor-balance features → `regime_calibration_required=True` mandatory for backtest features
4. **Mira flag #2** `b3_auction_window_mask` → first-1000-OR-30s exclusion (Nova classified F8 hypothesis-(a) auction phenomenon)
5. **F-A5-02** 49-chunk pooled re-test future-work
6. **D-02 schema split** (10-col + int agents) ACCEPTED divergence → reversal requires new mini-Council
7. **Guard #9 candidate** (Information Preservation Principle) → status `candidate` per Council 2026-05-03 §6.7 7-day moratorium until 2026-05-10

## §4 Invariants explicitly preserved by this ruling

- **Article II** push discipline (Gage exclusive; user direct R10 override registered §6.5 R1 Amendment as exception-not-rule)
- **Article IV** No Invention (every claim source-anchored to ballots, council resolutions, manual citations, code anchors)
- **R10 absolute custodial** — this ruling IS the R10 cosign event; pre-segment byte-equal preserved
- **R12** — pre-2024 evidence SECONDARY-CORROBORATIVE only; NEVER promotes to PRIMARY OOS
- **R16 (RATIFIED 2026-05-03)** — storage 10-col preserved at D:\; projection module is consumer-side concern
- **0/8 Anti-Article-IV Guards affected** (independent re-verification by Sable A5)
- **Hold-out 2025-07-01..2026-04-21** — UNCHANGED (T002 hold-out CONSUMED status preserved)
- **H_next-1 forward-time virgin window 2026-05-01..2026-10-31** — INTOCADA (Sable D-01 register)

## §5 Implementation downstream

- **A7-Dara** manifest extension EXECUTED (this ruling's mutation event)
- **A8-Beckett** N1+ archive backtest run AUTHORIZED post-A7 land:
  - Consumes `dll_backfill_projection v0.1.0` (T003.A4 module)
  - Cost atlas v1.0.0 + ±0.6bp sensitivity-band per F-A5-01
  - `b3_auction_window_mask` first-1000-OR-30s exclusion per Mira flag #2
  - `regime_calibration_required=True` per Mira flag #1
  - R12 SECONDARY-CORROBORATIVE locked (no PRIMARY promotion)

## §6 Reversal protocol

If any future audit refutes pre-2024 archival validity, reversal requires:

- Mini-Council ratification (NOT unilateral revert)
- Sable [DIVERGENCE] register update
- User MWF cosign for the reversal mutation (pre-segment byte-equal preserved on rollback)

## §7 Source anchors

- `docs/stories/T003-A6-COSIGN-REQUEST-2026-05-03.md` §9 — user MWF cosign signature (decision (1) APPROVE)
- `docs/audits/A7-DARA-2026-05-03-manifest-extension-verdict.md` — A7_PASS_PROCEED_TO_A8 verdict
- `docs/audits/A5-SABLE-2026-05-03-substantive-virgin-audit.md` — A5_PASS_WITH_FLAGS — PROCEED_TO_A6
- `docs/audits/A4-MIRA-2026-05-03-regime-stationarity-ruling.md` — A4_PASS_WITH_FLAGS
- `docs/audits/A3-NOVA-2026-05-03-cost-atlas-auction-hours-ruling.md` — A3_PASS_PROCEED_TO_A5
- `docs/audits/AUDIT-2026-05-03-T003.A2-schema-split-divergence.md` — D-02 register
- `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md` — Council §6.5 routing + R16 final wording
- `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md` — R1 amendment + §6.5 user direct push exception
- `.github/canonical-invariant.sums` — post-mutation SHA256 anchor

---

**Ruling token:** `MWF-20260503-1`
**Cosigning authority:** User R10 absolute MWF holder
**Date filed:** 2026-05-03 BRT
**Filed via:** @aiox-master orchestration recording user authority decision
