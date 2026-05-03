# Mira Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Mira (@ml-researcher)
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored to amendment §§1-3, Council 2026-05-01 R7/R12, spike-summary-S1{a,b,retry-0315}.json, AFML chap. 7/12.

---

## §1 Verdict + reasoning

R1 expansion to 2023-01-01..2024-01-01 within Phase 2C orchestrator is **acquisition-scope only** — it does NOT promote pre-2024 evidence to PRIMARY OOS, does NOT mutate strategy thresholds, does NOT touch H_next-1 forward-time virgin window (Guard 8 PASS, amendment §3 0/8 affected). My A4-Mira regime stationarity 5-axes ruling remains downstream and unaltered. Acquiring data is necessary-but-not-sufficient for any ML inference: ratifying R1' does NOT preempt R7. Therefore APPROVE the acquisition envelope, conditional on R12/R7/R14 being held strictly downstream and on conditions C1-C4 below.

## §2 Conditions

- **C1 (R12 invariance):** R12 SECONDARY-CORROBORATIVE clause is **non-negotiable** even post-A4 clean ratification. Pre-2024 NEVER promotes to PRIMARY-CORROBORATIVE (audit-point 6 confirmed NO). Any future motion attempting promotion requires a separate council and is currently pre-blocked.
- **C2 (A4 evidence ordering):** A4-Mira regime stationarity sign-off is **post-bulk + post-R14 closure**, NOT post-amendment-ratification. I sign R1' as acquisition envelope only; I do NOT sign regime equivalence today (insufficient evidence — only 5 sample dates).
- **C3 (Multiple-testing pre-registration):** A4 ruling pre-registers test set + α correction **before** seeing bulk regime statistics. Default: BH-FDR @ q=0.10 across the 5 R7 axes (a-e); Bonferroni-Holm @ α=0.05 if axes are treated as independent confirmatory tests. Locked in A4 spec before bulk arrives.
- **C4 (R14 hard gate):** S1-retry-0915 + 0315 qfd root-cause MUST close before A4 dispatch (amendment §2.2 already requires this — re-asserted as ML precondition; a structurally errored Sept'23 chunk masks regime axis (e) holiday calendar + (c) macro and would force a reduced 2023 effective window).

## §3 Concerns + mitigations (per 7 audit points)

1. **Regime stationarity from spike alone:** From spike data I can adjudicate ONLY axis (b) RLP regime presence/absence (qualitative — 5/6 dates show normal trade volumes 670-990k consistent with active RLP) and partially axis (e) holiday calendar (B3 days behave as trade-bearing). Axes (a) cost atlas v1.0.0 validity, (c) COVID-aftermath macro drift, (d) BMF→F transition, and full (e) require **bulk** + Nova A3 ruling. **Signing R7 today = signing blind.** Mitigation: C2 + C4.
2. **Sample size:** ~250 trading days × 1 series. With 20-day embargo + 50-day folds → effective ~200 usable days → ~4 non-overlapping folds. **Marginally adequate for purged k-fold; INADEQUATE for CPCV C(N,k) with N≥10.** Mitigation: pre-2024 used as SECONDARY-CORROBORATIVE channel (R12) — single IC point estimate + bootstrap CI per regime sub-window, NOT a full CPCV-based generalization claim. K3 generalization gate remains anchored to forward-time virgin (R12).
3. **IC stability cross-window:** A 2023-Q1 IC=0.4 due to SVB/Selic shock does NOT retroactively REFUTE T002 IC=0.866 — T002 is RETIRED (memory `project_t002_6_round2_closure`) and its IC was measured on its consumed window. R12 protects: pre-2024 corroborates, never refutes-retroactively. However, divergent IC IS a regime-non-equivalence signal feeding A4 axis (c). Mitigation: pre-register IC-by-sub-window analysis with bootstrap CI overlap test before bulk lands (C3).
4. **2023-09-15 errored:** If S1-retry-0915 fails persistently, Sept 2023 chunk masks axes (c)+(e). **Whole-bulk integrity does NOT auto-fail** — regime ratification proceeds on the ~11 ratifiable months with explicit Sept gap flag propagated to A4 verdict. Mitigation: R14 (amendment §2.2) — already binding.
5. **Multiple-testing inflation:** Yes, 50 chunks × A2-A8 chain create surface area. But the **inferential test** is downstream: A4 5-axes ruling + IC stability tests. α correction applies there, NOT to acquisition. Recommendation locked in A4 spec: **BH-FDR @ q=0.10** for 5 axes (more powerful than Bonferroni; appropriate for confirmatory family of moderate size — Benjamini-Hochberg 1995). Sub-window IC tests inside axis (b)/(c) → nested FDR. Pre-registered (C3).
6. **R12 graduation:** **NO.** Even with A4 clean ratification, pre-2024 stays SECONDARY-CORROBORATIVE. Promotion to PRIMARY-CORROBORATIVE would require: (i) separate council, (ii) explicit AP-D-13 anti-pattern override justification, (iii) virgin-by-discipline proof beyond Sable A5. Confirmed.
7. **H_next-1 spec leakage:** Amendment is acquisition-only; no spec yaml v0.2.x edits, no virgin-window edits (Guard 8 PASS). H_next-1 forward-time virgin clearance protocol unbreached. Anti-leakage discipline preserved. **Pre-condition for me:** A4 ruling + any IC sub-window readout is documented in a SEPARATE artifact from the H_next-1 spec; no findings backflow into spec parameters until forward-time PRIMARY clears (R12).

## §4 Source anchors

- Amendment §§1-3 (this file's parent doc) — empirical spike outcomes, R14/R15 introduction, 0/8 guards.
- Council 2026-05-01 R7 (5 regime axes a-e), R12 (SECONDARY-CORROBORATIVE clause), AP-D-08, AP-D-10, AP-D-13.
- spike-summary-S1a/S1b/S1-retry-0315.json — 5/6 partial_coverage; 0915 errored unretried; 0315 qfd=73,657 with 990,223 persisted.
- AFML 2018 chap. 7 (purged k-fold + embargo), chap. 12 (CPCV N,k), Bailey-LdP 2014 (DSR), Benjamini-Hochberg 1995 (FDR).
- Memory `project_t002_6_round2_closure` (T002 RETIRED; IC=0.866 historical-consumed); `feedback_cpcv_dry_run_memory_protocol`.

— Mira, ML/statistical authority, ballot self-audited 2026-05-03
