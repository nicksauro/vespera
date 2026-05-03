# Multiple-Testing α-Correction Pre-Registration — Bulk Backfill 2023-01..2024-01

**Status:** PRE-REGISTERED — locked 2026-05-03 BRT BEFORE bulk data arrival
**Owner:** Mira (ML Researcher) — Council 2026-05-03 R1 Amendment ballot C3
**Branch:** `t003-a1-dll-probe-2023-12`
**Scope:** A4-Mira regime stationarity audit downstream of Council R7 5-axis evidence

---

## §1 Hypothesis structure (5 axes per Council R7)

A4-Mira tests five regime-stationarity hypotheses across the bulk backfill 2023-01..2024-01 (~250 trading days):

- **H_a — Cost atlas pre-2024:** post-2024 cost params generalize to 2023 microstructure
- **H_b — RLP regime:** RLP (tradeType=13) share invariant 2023 vs 2024-Q4
- **H_c — Macro drift:** vol-cluster / term-structure regime stationary 2023→2024
- **H_d — BMF→F transition:** exchange-code change introduces no structural break
- **H_e — Holiday calendar:** Nova session-phase taxonomy maps cleanly to pre-2024

**Correlation:** H_a..H_e exploratory and potentially positively dependent (H_a~H_b cost/RLP; H_b~H_c flow/macro). BH-FDR is robust under positive dependence (Benjamini-Yekutieli 2001 not required at q=0.10 conservative).

## §2 α-correction strategy

**DEFAULT:** Benjamini-Hochberg FDR @ q=0.10 across the 5 axes.
**ALTERNATIVE (if escalated to confirmatory-independent):** Bonferroni-Holm @ α=0.05 (FWER strict).

**Justification:** A4-Mira is an *exploratory regime audit*, not a confirmatory edge test. The 5 axes screen whether pre-2024 evidence is admissible as SECONDARY-CORROBORATIVE under R12; per-axis rejection is a soft-fail trigger, not a kill switch. BH-FDR (Benjamini-Hochberg 1995) preserves screening power while bounding expected FDR at 10%. Bonferroni-Holm (Holm 1979) stays on-record as the strict fallback if PO/Sable later escalates any axis. López de Prado (AFML 2018, §7) anchors the multiple-testing discipline.

## §3 Reject thresholds — pre-registered cutoffs

For ranked p-values p_(1) ≤ p_(2) ≤ ... ≤ p_(5) across the 5 axes:
- **BH-FDR @ q=0.10:** reject H_(i) if p_(i) ≤ (i/5) × 0.10
- **Bonferroni-Holm @ α=0.05:** reject H_(i) if p_(i) ≤ 0.05/(5-i+1)

| Rank i | BH-FDR cutoff (q=0.10) | Bonferroni-Holm cutoff (α=0.05) |
|--------|------------------------|---------------------------------|
| 1      | 0.0200                 | 0.0100                          |
| 2      | 0.0400                 | 0.0125                          |
| 3      | 0.0600                 | 0.0167                          |
| 4      | 0.0800                 | 0.0250                          |
| 5      | 0.1000                 | 0.0500                          |

(Aritmética verificada: BH cutoff_i = (i/5)×0.10; Holm cutoff_i = 0.05/(5−i+1). Both correct.)

## §4 Sample-size honesty

- ~250 trading days → ~4 non-overlapping folds (50d + 20d embargo): **marginally adequate** for purged k-fold.
- Full CPCV C(N≥10, k=2) **INADEQUATE** at this size — do not promise CPCV paths from pre-2024 alone.
- **K3 gate** (post-T002 retire) stays anchored to the forward-time virgin window per R12. Pre-2024 is **SECONDARY-CORROBORATIVE only**; never promotes to PRIMARY.

## §5 Anti-leakage discipline

- H_next-1 spec v0.1.0 forward-time virgin window **2026-05-01..2026-10-31 INTOCADA**.
- Pre-2024 evidence consumed only inside A4-Mira under R12; never mixed with the forward-time virgin clearance protocol.
- Sable D-01 [DIVERGENCE] holds; D-02 (R1 bulk expansion) ratified 2026-05-03 — append-only.

## §6 Source anchors

- Council 2026-05-01 R7 (5-axis definition): `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md`
- Council 2026-05-03 R1 Amendment R12 invariance: `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md` §2.4
- Mira ballot C3 (this α-correction condition): `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-mira-vote.md`
- Statistical anchors: Benjamini & Hochberg (JRSS-B, 1995); Holm (Scand. J. Stat., 1979); López de Prado, *Advances in Financial Machine Learning* (2018), §7.

## §7 Lock declaration

> This α-correction strategy and the §3 reject thresholds are **PRE-REGISTERED 2026-05-03 BRT BEFORE bulk data arrival**. Any post-hoc adjustment requires mini-Council ratification AND a Sable Article IV [DIVERGENCE] register entry. Tampering with this document after bulk arrival breaks H_next-1 anti-leakage discipline and is a Constitution Article IV violation.

— Mira, mapping signal from noise 🗺️
