# T003 A6 Cosign Request — User MWF Authority on R10 Manifest Extension

**Compiler:** Pax (@po)
**Date BRT:** 2026-05-03
**Authority sought:** User R10 absolute custodial cosign
**Chain position:** A6 of A1→A2→A3→A4→A5→A6→A7→A8 (Council 2026-05-01 §4)
**Predecessor verdict:** Sable A5 `A5_PASS_WITH_FLAGS — PROCEED_TO_A6` (2026-05-03)
**Moratorium status:** Council 7-day moratorium ATIVO through 2026-05-10 — A6 is operational chain continuation, NOT a new council.

---

## §1 What user is asked to cosign (concise statement)

> "I, the user, cosign R10 absolute custodial mutation: extend `data/manifest.csv` to include 2023-Q1..Q4 archival rows (50 chunks from `D:\Algotrader\dll-backfill\`, ~195M trades / 195,076,064 rows verified post-projection) per Council 2026-05-03 §6.5 routing, with phase=`archive` append-only addition, byte-equal SHA256 verified per R10. Pre-2024 evidence remains SECONDARY-CORROBORATIVE per R12 — NEVER promotes to PRIMARY OOS. H_next-1 forward-time virgin window 2026-05-01..2026-10-31 INTOCADA — remains PRIMARY OOS anchor. Gate-5 lock + R10 byte-equal preserved (per Sable C1 binding into R16 final wording §6.2)."

This cosign authorizes A7-Dara to dispatch the manifest extension PR. NO Gate-5 unlock. NO PRIMARY OOS promotion of pre-2024 data. Custodial parquet at `D:\Algotrader\dll-backfill\` stays untouched (R16 information-preservation); the extension only adds **archive-phase** manifest rows referencing already-acquired chunks.

---

## §2 10-point story validation cumulative T003 (Pax checklist)

Applied to T003 cumulative artifact set: T003.A1 (probe spec/script `d224a4f`) + T003.A2 (orchestrator Phase-2C prototype) + T003.A3 (lib extraction follow-on, debt named) + T003.A4 (minimal-cast projection, Draft → AC7 PASS) + Council 2026-05-03 (Option D + R16 ratified) + Audit chain A2-reaudit/A3-Nova/A4-Mira/A5-Sable/D-02.

| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | Clear and objective title | **PASS** | T003 epic title explicit (Pre-2024 WDOFUT acquisition for H_next preregistered window); each sub-story (A1/A2/A3/A4) has scoped title. |
| 2 | Complete description | **PASS** | Each story §1 names consumers (Mira/Beckett downstream + Dara custodial) + custodial intent. Council 2026-05-03 ratifies thesis-decides-schema. |
| 3 | Testable acceptance criteria | **PASS** | T003.A4 7 ACs binary-verifiable (AC1-AC7); A2-reaudit AC7 verdict `A2_REAUDIT_PASS_AT_PROJECTION_BOUNDARY` confirmed across 50/50 chunks empirical. T003.A2 ACs amended via §0.5 PROTOTYPE_SATISFIED vs PHASE_3_HARDENING_TARGET split — debt named, not hidden. |
| 4 | Well-defined scope (IN/OUT) | **PASS** | T003.A4 §4 explicit IN: casts ts/qty/nullable + F2 doc + v1.1 + versioning. OUT: lib extraction (A3), 15→19 col bump (A3), recovery (A3). T003.A3 captures extraction debt as separate story. Sable D-02 register documents F2 schema-split as ACCEPTED divergence (not silent). |
| 5 | Dependencies mapped | **PASS** | T003.A4 §4 hard prereq Council 2026-05-03 RATIFIED (DONE) + T003.A2 bulk run (DONE — 50 chunks empirical); soft prereq T003.A3 lib extraction independent. T003.A2 §0.5 amendment + T003.A3 dependency on bulk completion both explicit. |
| 6 | Complexity estimate | **PASS** | T003.A4 §6 itemized ~2.5h; T003.A3 ~3-5 sessions; T003.A2 ~6-9 sessions. Riven Bayesian estimates anchored. |
| 7 | Business value | **PASS** | A3/A4/A5 unblock + reproducibility tuple (`content_sha256, projection_semver=0.1.0`); pre-2024 admissibility as R12 SECONDARY-CORROBORATIVE for H_next-1. |
| 8 | Risks documented | **CONCERNS** | T003.A4 §3 R-1/R-2/R-3 explicit with mitigations; F-A5-01 exchange_fees ±0.6bp uncertainty surfaces as moderate severity (bounded, deterministic resolution path to A8-Beckett sensitivity-band); F-A5-02 49-chunk pooled re-test as cosmetic. Risk inventory complete; carry-forward path documented. |
| 9 | Definition of Done | **PASS** | T003.A4 §5 7 items; T003.A3 §DoD 7 items; both reference Quinn 7-check + Sable pre-push + Pax cosign + Gage push exclusive. |
| 10 | PRD/Epic alignment | **PASS** | T003 epic via §6.5 Council routing item 1 (T003.A4 minimal-cast); Article II/IV/R10/R12/R14/R16 invariants preserved; thesis-decides-schema explicit. H_next-1 spec read confirms technical-pure thesis (Mira+Kira) — D-02 thesis-irrelevant for current chain. |

**Cumulative score:** 9 PASS + 1 CONCERNS + 0 FAIL.

---

## §3 Carry-forward acknowledgments (user must accept)

User cosign acknowledges these 7 carry-forward flags propagate downstream — all PASS_WITH_FLAGS class, none blocking:

1. **F-A5-01** (Nova exchange_fees 2023 ±R$0.10-0.30/contract uncertainty ≤0.6bp impact) → carries to **A8-Beckett mandatory sensitivity-band check**. If strategy edge within ±0.6bp break-even → escalate Path-D (B3 archive lookup) BEFORE any `costed_out_edge` verdict.

2. **Mira axis-(b) RLP REJECT bounded** (NONE share Q1/2023 31.54% → Q1/2024 25.86%, Δ −5.7pp monotonic, N=15M drives p~0; effect-size honest §1.1) → SOFT-FAIL trigger per pre-register §2 (NOT kill-switch); R12 SECONDARY-CORROBORATIVE locked; pre-2024 NEVER promotes PRIMARY.

3. **Mira flag #1: aggressor-balance features** require `regime_calibration_required=True` mandatory in feature_registry; quarter-conditional baselines mandatory pre-2024.

4. **Mira flag #2: `b3_auction_window_mask`** parametrized — first-1000-trades-OR-30s-whichever-larger exclusion (Nova A3 §3 hypothesis-(a) auction-window phenomenon CONFIRMED; 5×2023 + 3×2024 chunks structurally identical NONE-dominance signature; F8 disposition closed at AUCTION_OPEN session-phase prior).

5. **F-A5-02** 49-chunk pooled re-test = future-work pre-condition for any future PRIMARY promotion of pre-2024 (currently locked SECONDARY-CORROBORATIVE — no immediate block).

6. **D-02** schema split (10-col rich storage + int64 agents 2023 vs 7-col + string agents 2024) = ACCEPTED divergence per Sable register; reversal requires new mini-Council + register addendum (R16 reversal protocol §5).

7. **Guard #9 candidate** (Information Preservation Principle) status `candidate` per Sable C4 moratorium 2026-05-10 — adjudication deferred to AIOX-master + Pax post-moratorium expiry; Sable does NOT promote unilaterally (R14).

---

## §4 Article II/IV/R10/R12/R16 invariants preserved (confirmation list)

- ✅ **Article II (Push exclusive @devops):** No agent in A1-A5 chain executed `git push` or `gh pr create/merge`. All merges (PR #21 `bfc5ff3`, #22-#25) via @devops Gage default channel per Council §6.4.
- ✅ **Article IV (No Invention):** Every claim source-traced — A2-reaudit (50/50 chunks empirical), A3-Nova (8 source anchors §5; Decree 9.772/2019 + B3 PUMA + empirical chunks), A4-Mira (6 source anchors §6; pre-register §7 lock honored), A5-Sable (9 source anchors §5), D-02 (10 ballots + Dara A2 + Nelo manual + Beckett code anchor + Mira spec read).
- ✅ **R10 (Absolute custodial — `data/manifest.csv`):** Currently 100% 2024-onward; sentinel `2024-01-02..` first row L2; zero 2023 entries in repo manifest (grep count 0). User MWF cosign (this request) is the **only authorization channel** for any mutation. Sable C1 binding clause baked into R16 final wording §6.2: *"R16 does NOT relax R10 byte-equal nor Gate-5 lock — both remain absolute."*
- ✅ **R12 (SECONDARY-CORROBORATIVE pre-2024 lock):** Pre-2024 NEVER promotes PRIMARY OOS. Mira A4 §1.1 + §5 #5 reaffirms; A5-Sable S3 verifies; pre-register §7 line 49 lock honored; H_next-1 K3 forward-time virgin INTOCADA.
- ✅ **R14 (Off-repo data + auditor self-audit):** Backfill data lives `D:\Algotrader\dll-backfill\` (off-repo, D: drive); `.gitignore` covers. Sable does not audit Sable.
- ✅ **R16 (Information preservation):** Storage byte-equal preserved (custodial 10-col + int64 agents); consumption-time projection (`scripts/dll_backfill_projection.py` v0.1.0) handles type/nullability normalization. Reversal protocol active (D-02 §5).
- ✅ **Anti-Article-IV Guards 1-8:** All PASS — confirmed independently by Sable + Mira + Aria + Riven (Council §6.3 line 136). Guard #9 candidate deferred per moratorium.
- ✅ **Forward-time virgin H_next-1 2026-05-01..2026-10-31:** INTOCADA — remains PRIMARY OOS anchor.

---

## §5 Implementation routing post-cosign (A7/A8)

Sequence on user APPROVE:

| Step | Owner | Action | Estimate | Gate |
|---|---|---|---|---|
| **A7** | Dara (@data-engineer) | `data/manifest.csv` extension PR — append 50 archive-phase rows (chunk_id, start_date, end_date, ticker=WDOFUT, exchange=F, phase=archive, parquet_sha256, projection_semver=0.1.0). Preserve int64 agents per Council §6.5 #1; consumer-side cast enforced. Backward-compat header read. | ~1.5-2h | Sable pre-push coherence + Pax cosign on schema; @devops Gage push EXCLUSIVE. |
| **A8** | Beckett (@backtester) | N1+ archive backtest run consuming projection module + cost atlas v1.0.0 + sensitivity-band ±0.6bp (F-A5-01) + auction-window mask (Mira #2) + regime-calibration flag (Mira #1). Pre-2024 backtest as SECONDARY-CORROBORATIVE only — NEVER feeds PRIMARY OOS verdict. | ~1-2 sessions | Mira IC pipeline wiring verified; Quinn QA gate; if `costed_out_edge` borderline → Path-D escalation BEFORE final verdict. |

A8 output is **corroborative evidence only** — does NOT alter T002 RETIRE FINAL status (Phase G OOS confirmed `costed_out_edge` per memory ledger 2026-05-01). H_next-1 strategy validation uses NEW preregistered window 2026-05-01..2026-10-31.

---

## §6 Decision menu

User selects ONE:

- **(1) APPROVE** — Sign R10 cosign as written §1. A7-Dara dispatches manifest extension; A8-Beckett N1+ archive run follows. All §3 carry-forward acknowledgments accepted.

- **(2) APPROVE_WITH_AMENDMENT** — Sign with caveat. Specify caveat text (e.g., narrow scope to subset of chunks, additional gate on A8 verdict, explicit Path-D pre-trigger threshold tighter than ±0.6bp, etc.). Pax re-issues cosign request with amendment incorporated for re-sign.

- **(3) REJECT** — Chain blocked. ESC review opened. Manifest extension does NOT proceed. T003.A4 stays Draft pending alternative path. Custodial parquet at `D:\Algotrader\dll-backfill\` retained but unused for H_next-1 corroboration.

- **(4) REQUEST_INFO** — Specify what additional analysis needed BEFORE cosign decision (e.g., 49-chunk pooled re-test executed first, B3 archive 2023 fees lookup pre-emptive, additional Mira axis-(b) sub-window analysis, etc.). Chain pauses; Pax dispatches requested analysis; cosign request re-compiled with new evidence.

---

## §7 Verdict

**Cumulative 10-point score:** 9 PASS + 1 CONCERNS (#8 risk, F-A5-01 moderate but bounded) + 0 FAIL.

**Verdict: GO — Cosign-ready for user authority decision.**

**Recommendation:** Pax recommends **APPROVE** (option 1).

Rationale:
- Zero critical findings across A1-A5 substantive chain (Sable A5 §2 explicit: 0 🔴 critical; F-A5-01 only ⚠️ moderate, bounded ≤0.6bp deterministic resolution path).
- All 7 carry-forward flags have documented owners + actions in §3 + §5.
- Article II/IV/R10/R12/R14/R16 invariants ALL preserved + Anti-Article-IV Guards 1-8 ALL PASS.
- H_next-1 forward-time virgin window INTOCADA — PRIMARY OOS anchor preserved.
- D-02 schema-split is thesis-irrelevant for current technical-pure H_next-1 (Mira+Kira spec read confirms; Beckett `feed_parquet` consumer-zero-impact).
- Council 2026-05-03 RATIFIED 10/10 + user MWF tiebreaker; A6 is operational continuation, not new council.

Single CONCERN on point 8 (risks) is bounded carry-forward to A8-Beckett — sensitivity-band check is mandatory but does NOT block cosign authorization to extend manifest.

If user prefers belt-and-suspenders, **option 4 REQUEST_INFO** with scope "execute B3 archive 2023 exchange_fees lookup pre-emptive (resolves F-A5-01 deterministically before A8 enters sensitivity-band scenario)" is a legitimate conservative path. Pax does not recommend rejection — chain integrity strong.

---

## §8 Source anchors

**Verdict files (5):**
- `docs/audits/T003-A2-reaudit-2026-05-03.md` — Dara A2-reaudit `A2_REAUDIT_PASS_AT_PROJECTION_BOUNDARY` (50/50 chunks; F3/F4/F5 RESOLVED; F1 PRESERVED-by-R16; F2 CARRY-FORWARD; F8 → A4).
- `docs/audits/A3-NOVA-2026-05-03-cost-atlas-auction-hours-ruling.md` — Nova A3 `A3_PASS_PROCEED_TO_A5` (cost atlas v1.0.0 valid 2023-Q1..Q4 + 1 TO-VERIFY exchange_fees ≤0.6bp).
- `docs/audits/A4-MIRA-2026-05-03-regime-stationarity-ruling.md` — Mira A4 `A4_PASS_WITH_FLAGS` (5-axis: 1/5 axis-(b) REJECT bounded; (c)(d)(e) clear; (a) PENDING→consumed via A3; F8 → AUCTION_OPEN session-phase).
- `docs/audits/A5-SABLE-2026-05-03-substantive-virgin-audit.md` — Sable A5 `A5_PASS_WITH_FLAGS — PROCEED_TO_A6` (8/8 PASS; 3 findings non-blocking; READY for A6).
- `docs/audits/AUDIT-2026-05-03-T003.A2-schema-split-divergence.md` — D-02 register (Sable; ACCEPTED divergence; reversal protocol §5).

**Story files (3):**
- `docs/stories/t003.a4.minimal-cast-projection.story.md` — T003.A4 (Draft, 7 ACs binary; AC7 PASS; 10/10 Pax self-applied).
- `docs/stories/t003.a3.backfill-lib-extraction.story.md` — T003.A3 (Draft; structural extraction debt named, not hidden).
- `docs/stories/t003.a2.dll-backfill-orchestrator.story.md` — T003.A2 (In-Progress-Phase-2C-Prototype; AC §0.5 PROTOTYPE_SATISFIED vs PHASE_3_HARDENING_TARGET split per Pax HYBRID adjudication).

**Council files (2):**
- `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` — R7/R9/R10/R12/R14 anchors.
- `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md` — Option D + R16 RATIFIED 10/10 + user MWF + Sable C1-C4 binding; §6.2 R16 verbatim; §6.5 routing; §6.6 D-02 mandate; §6.7 7-day moratorium through 2026-05-10.

**Pre-register:**
- `docs/preregistration/MULTIPLE-TESTING-ALPHA-2026-05-03.md` — BH-FDR q=0.10 + Bonferroni-Holm α=0.05; §2 soft-fail clause L27; §7 R12 lock L49.

**Memory ledger:**
- T002 RETIRE FINAL 2026-05-01 (PR #16 ESC-012 + #17 `06dcdda`); T002.6 Round 2 closure (Mira F2-T9.1 FINAL `costed_out_edge_oos_confirmed_K3_passed`); H_next-1 forward-time virgin 2026-05-01..2026-10-31 INTOCADA.

---

— Pax, Product Owner, A6 cosign request compiled 2026-05-03

**Discipline declaration:** READ-ONLY analysis. Zero file mutation outside this NEW doc. NO commit, NO push (Article II — Gage exclusive). Verdict file is the only output. Pax does not promote rules; user MWF authority adjudicates §6 decision.

---

## §9 USER MWF COSIGN — FILED 2026-05-03

**Decision:** **(1) APPROVE** — full package ratified.

**Cosign signature (inline):**

> *"I, the user, cosign R10 absolute custodial mutation: extend `data/manifest.csv` to include 2023-Q1..Q4 archival rows (50 chunks from `D:\Algotrader\dll-backfill\`, ~195M trades) per Council 2026-05-03 §6.5 routing, with phase=`archive` append-only addition, byte-equal SHA256 verified per R10. Pre-2024 evidence remains SECONDARY-CORROBORATIVE per R12 — NEVER promotes to PRIMARY OOS. All 7 carry-forward acknowledgments accepted (F-A5-01 exchange_fees ±0.6bp sensitivity-band + Mira axis-b RLP bounded -5.7pp soft-fail + flag #1 regime_calibration_required=True + flag #2 b3_auction_window_mask first-1000-OR-30s exclusion + F-A5-02 49-chunk pooled re-test future-work + D-02 schema split divergence reversal-protocol-locked + Guard #9 candidate post-moratorium 2026-05-10). Cosign authorizes A7-Dara manifest extension dispatch + A8-Beckett N1+ archive run downstream."*

**Authority basis:** User R10 absolute MWF cosign holder (supreme authority above any agent boundary).
**Date BRT:** 2026-05-03
**Status:** **`A6_COSIGN_RATIFIED — A7_DARA_DISPATCH_AUTHORIZED`**

— @aiox-master orchestration, recording user authority decision 2026-05-03
