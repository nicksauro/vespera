# Council 2026-05-03 — R1 Amendment Resolution — **RATIFIED** (6/6 UNANIMOUS APPROVE_WITH_CONDITIONS + user MWF cosign)

> **Date (BRT):** 2026-05-03
> **Trigger:** Sable meta-audit `META_AUDIT_HARD_BLOCK_FIX_REQUIRED` (2026-05-03), finding MA-03 CRITICAL: `DLL_BACKFILL_R1_OVERRIDE` env token (`ack_dara_aria_council_2026_05_01`) used in Phase 2C orchestrator bypasses Council 2026-05-01 R1 letter ("single month, 14 trading days max") without Council quorum ratification. Bulk run = 50 chunks × 5d = ~250 trading days = 17.8x R1 letter authorization.
> **Authority basis:** Empirical findings 2026-05-02..03 + Phase 2C orchestrator infra (PR #22 OPEN, branch `t003-a1-dll-probe-2023-12` HEAD `b1802ac`).
> **Council 2026-05-01 R2-R13:** PRESERVED UNCHANGED.
> **Article II preserved:** No push during deliberation (PR #22 already OPEN; review-merge gates downstream).
> **Article IV preserved:** Independent ballot self-audits required.
> **Author:** @aiox-master orchestration capacity, autonomous mode.

---

## §1 What changed empirically since 2026-05-01

### §1.1 DLL retention pre-2024 confirmed beyond December 2023

Spike protocol Nelo (`scripts/dll_spike_nelo_protocol.py` + `data/dll-probes/SPIKE-NELO/`) tested 6 sample dates across 2023 (Jan/Mar/May/Jul/Sep/Nov). Outcome aggregation (S1a + S1b + S1-retry-0315):

| Date | Outcome | Notes |
|---|---|---|
| 2023-01-16 | partial_coverage | retention OK |
| 2023-03-15 | partial_coverage (after retry) | qfd=73,657 drops (queue full → trades lost; root-cause TBD) |
| 2023-05-15 | partial_coverage | retention OK |
| 2023-07-17 | partial_coverage | retention OK |
| 2023-09-15 | **error (exit 3) — never retried** | gap to close before A2 dispatch |
| 2023-11-16 | partial_coverage | retention OK |

**Net retention claim:** 5/6 dates retention-confirmed but 2/6 carry data-quality qualifiers. Sufficient evidence for HYPOTHESIS retention extends to 2023-01, INSUFFICIENT for unqualified bulk certification — see R14-NEW (below).

### §1.2 Phase 2C orchestrator framework operational

Built since 2026-05-02 (commits `cbd6813` → `b6e3a5b` → `c7b1423` → `b1802ac`):

- `scripts/dll_backfill_orchestrator.py` (B3 holiday-aware 5d chunks, atomic manifest, resume protocol idempotent, data-completeness-first classifier)
- `scripts/dll_backfill_chunk_runner.py` (subprocess.Popen fresh per chunk; monkey-patches `probe._OUTPUT_DIR`, `_HARD_TIMEOUT_S`, `_IDLE_WATCHDOG_S`, `_REPO_ROOT`; calls `probe.run_probe()` direct)
- `scripts/dll_backfill_launch_detached.py` (Aria Option D detached launcher)
- Riven blocking caps wired: `max-attempts=3` (per-chunk), `max-consecutive-failures=3` (orchestrator abort), `max-wall-time-s=23400` (6h30 hard kill), `cooldown-s=30` (TCP TIME_WAIT + Q-FIN-12-E DLL quiesce + Q-AMB-04), `max_qfd_global_pct=0.001` (0.1%)
- Heartbeat file (atomic write per chunk; aiox-master kills if stale)
- Exit codes: 0=SUCCESS, 1=PARTIAL, 2=ABORTED, 3=ERROR

### §1.3 4 critical probe bugs discovered + fixed (commit `cbd6813`)

| Bug | Severity | Fix |
|---|---|---|
| `DLLInitializeMarketLogin` ABI: 11 callbacks vs manual §3.1 L991-1010 spec'd 8 slots | CRITICAL | Rewrite to 8 callbacks (state, newTrade, newDaily, priceBook, offerBook, historyTrade=slot 6, progress=slot 7, tinyBook). Q11-E reentry: in MarketLogin, historyTrade is slot 6 (NOT 9 of full DLLInitializeLogin). |
| Q-FIN-12-E (NEW quirk): callbacks emit post-progress=100 for ms-30s; DLLFinalize during callback = SEH access violation silent exit 1 | CRITICAL | `_shutdown_dll` waits `last_callback_ts ≥ 2s idle` (max 30s deadline) before DLLFinalize |
| `_validate_first_1000` hardcoded 2023-12-01..20 window | HIGH | Window-aware schema validator (accepts window_start + window_end params; aggressor threshold lowered to 25% for auction-heavy first 1000 trades) |
| Cross-drive Path bug (D:\ vs C:\) in chunk_runner | MEDIUM | `_REPO_ROOT` monkey-patch override |

### §1.4 Production data state on D:\

- `D:\Algotrader\dll-backfill\` populated: 61 chunk dirs, 63 parquets, 3.9GB
- `manifest.csv` exists at root
- 6 test/scratch dirs (`test-*`, `smoke-test/`) MIXED with production chunks (Sable MA-08 — cleanup tracked, non-blocking)
- Repo only holds ~240KB diagnostic telemetry in `data/dll-probes/` (parquets gitignored per `b1802ac`)

---

## §2 Proposed amendments

### §2.1 R1 EXPANSION (REPLACES original R1)

**Original R1 (2026-05-01 letter):**
> "Bounded probe window: 2023-12-01..2023-12-20 (single month, 14 trading days max); WDOFUT contínuo ONLY"

**R1' (proposed 2026-05-03 amendment):**
> "Bounded backfill window: 2023-01-01..2024-01-01 (~250 trading days, ~12 months) within Phase 2C orchestrator framework; 5-day chunks B3 holiday-aware; WDOFUT contínuo ONLY (specific contracts e.g., WDOZ23 hit Q09-E 0-trades-19ms bug); Riven blocking caps NON-NEGOTIABLE per §1.2; D:\ off-repo storage; ALL R10 custodial constraints PRESERVED (manifest.csv mutation still requires user MWF cosign, separately gated by R5/R6/R7/R9 downstream audits)."

**Justification:**
- Retention claim ratified by spike protocol §1.1 (5/6 with qualifiers; A2-Dara schema parity audit gates downstream)
- Bounded execution envelope provides hard kill switches (Riven caps §1.2)
- Storage discipline preserved (D:\ off-repo; repo only telemetry; gitignored parquets)
- Custodial preservation NOT relaxed (R5/R6/R7/R9/R10 all still binding)
- Window upper bound 2024-01-01 = day before Sentinel manifest floor 2024-01-02 (zero overlap with existing custodial data)

### §2.2 R14 NEW — Spike-protocol completion gate

**R14 (NEW, 2026-05-03):**
> "Before A2-Dara schema parity audit dispatch, S1-retry-0915 (2023-09-15 retry) MUST execute and outcome documented. Additionally, 2023-03-15 qfd=73,657 root cause MUST be characterized (transient stochastic vs reproducible structural). If 0915 retry fails persistently OR 0315 qfd is reproducible-structural, R1' bulk window narrows OR data-quality flags propagate to A4-Mira regime stationarity ruling."

### §2.3 R15 NEW — Orchestrator override token audit-trail

**R15 (NEW, 2026-05-03):**
> "`DLL_BACKFILL_R1_OVERRIDE` env token MUST source-anchor to this amendment (commit SHA + Council ID) in `chunk_runner.py` + `orchestrator.py` docstrings. Token value MUST update from `ack_dara_aria_council_2026_05_01` to `ratified_council_2026_05_03_R1_amendment_quorum_<sha>` post-quorum. Code update gated to commit-4 of T003.A2 story per Pax/River AC."

### §2.4 R2-R13 PRESERVED UNCHANGED

R2 (full instrumentation), R3 (anti-pattern flags), R4 (probe outcome decision tree), R5 (Dara schema parity), R6 (Nova cost atlas), R7 (Mira regime stationarity), R8 (Nova auction hours), R9 (Sable virgin audit), R10 (R10 absolute custodial), R11 (§11.5 capital ramp), R12 (pre-2024 SECONDARY-CORROBORATIVE only), R13 (Quarter-Kelly + Gate 5).

---

## §3 Anti-Article-IV Guards 1-8 impact analysis

| Guard | Affected? | Notes |
|---|---|---|
| 1 — Spec yaml v0.2.3 thresholds UNMOVED | NO | This amendment touches data-acquisition scope, not strategy thresholds |
| 2 — Hold-out lock byte-equal | NO | T002 hold-out CONSUMED + intocada |
| 3 — `data/manifest.csv` UNCHANGED | NO | R10 explicitly preserved; no manifest mutation by this amendment |
| 4 — Spec thresholds UNMOVED post-Phase F2 | NO | Strategy spec untouched |
| 5 — Quarter-Kelly REGRA ABSOLUTA | NO | R13 explicitly preserved |
| 6 — §11.5 capital-ramp pre-conditions | NO | R11 explicitly preserved |
| 7 — Gate 5 fence | NO | LOCKED PERMANENTLY post-T002 retire |
| 8 — H_next-1 PRIMARY virgin window 2026-05-01..2026-10-31 intocada | NO | Backfill window 2023-01..2024-01 disjunto |

**Net:** 0/8 guards affected. Amendment is scope-bounded to data acquisition track.

---

## §4 Vote section (6 quorum + user MWF cosign)

Each agent files independent ballot at `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-{agent}-vote.md`.

| Voter | Authority | Vote | Conditions | Ballot path |
|---|---|---|---|---|
| Nelo (@profitdll-specialist) | DLL guardian | **APPROVE_WITH_CONDITIONS** | 6 (R14, R15 immediate, quirks registry update, WDOFUT parse-time hard-reject, AP-D-14 NEW, hard-cap 2024-01-01) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-nelo-vote.md` |
| Nova (@market-microstructure) | Microstructure validity | **APPROVE_WITH_CONDITIONS** | 5 (A3 auction-hours, A3 cost atlas pre-2024, A2 WDOZ23→WDOG24 roll, 25% aggressor not regime-proof, R14 binding) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-nova-vote.md` |
| Mira (@ml-researcher) | Statistical regime | **APPROVE_WITH_CONDITIONS** | 4 (R12 invariance, A4 post-bulk only, α-correction pre-register BH-FDR q=0.10 ∨ Bonferroni-Holm α=0.05, R14 binding) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-mira-vote.md` |
| Riven (@risk-manager) | Custodial + caps | **APPROVE_WITH_CONDITIONS** | 4 (R14, mid-bulk quarantine semantics code gap orchestrator.py:654-657, R15 PRE-bulk-execution, governance debt curve disclosure). Bayesian joint w/ conditions = 0.82 (≥0.80 threshold) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-riven-vote.md` |
| Aria (@architect) | Architectural design | **APPROVE_WITH_CONDITIONS** | 5 (C1 BLOCKING R15 rename — Aria did NOT pre-authorize literal token, C3 BLOCKING-ish Pax AC downgrade ∨ T003.A3 follow-on, Q-PATH-14-V cross-drive quirk, classifier mask-risk surfaced in manifest, debt curve healthy reactive iteration confirmed) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-aria-vote.md` |
| Dara (@data-engineer) | Engineering execution | **APPROVE_WITH_CONDITIONS** | 6 (R14, R15, hard-cap 2024-01-01, D:\ cleanup 7 dirs, A2 schema parity 2-3 sessions ref month 2024-01 frozen fail-closed, post-A6 manifest extension 4-6h) | `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-dara-vote.md` |
| **User MWF cosign** | R10 absolute authority | **APPROVE_WITH_CONDITIONS** (path A — full package ratified) | All 15 consolidated conditions accepted; remediation tracks dispatched parallel; R14 closure routed to operator (local-IA terminal) per `docs/operator-tasks/R14-CLOSURE-CHECKLIST-2026-05-03.md` | inline this resolution §6 |

**Threshold met:** 6/6 quorum APPROVE_WITH_CONDITIONS + user MWF cosign filed → **`RATIFIED_R1_AMENDMENT_2026_05_03`**.

---

## §5 Outcome routing post-quorum

```
6/6 APPROVE + user MWF cosign
   → Update commit-4 T003.A2 story:
     • chunk_runner.py + orchestrator.py: token rename + docstring source-anchor (R15)
     • Quirks registry update: Q-FIN-12-E + slot-6 MarketLogin distinction
   → Execute S1-retry-0915 + 2023-03-15 qfd root cause (R14)
   → Dispatch A2-Dara schema parity audit (proceed Council 2026-05-01 §4 chain)
   → Dispatch A3-Nova cost atlas pre-2024 ruling
   → Dispatch A4-Mira regime stationarity 5 axes
   → Dispatch A5-Sable substantive virgin audit
   → A6-Pax 10-point + R10 user MWF cosign for manifest mutation
   → A7-Dara backfill manifest extension
   → A8-Beckett N1+ archive run

ANY REJECT or NEEDS_REVISION
   → Block A2-Dara dispatch
   → Open ESC-XXX with REJECT reasoning
   → User authority adjudicates: revise amendment / rollback bulk / re-quorum
```

---

## §6 Ratification + user MWF cosign

**Date BRT:** 2026-05-03
**Decision path selected by user:** (A) full-package ratification — endorses all 15 consolidated conditions
**Authority basis:** R10 absolute custodial + capital-ramp R11 + Quarter-Kelly R13 — user is supreme MWF cosign holder
**Cosign signature:** filed inline `2026-05-03 user MWF cosign — APPROVE 15-condition package — A2-Dara dispatch unblocks ONLY after R14 closure (operator-side) + R15 token rename (squad-side, immediate) + quarantine code gap fix (squad-side) + Pax AC adjudication (squad-side) + remaining conditions tracked`

### §6.1 Consolidated 15-condition package (status tracker)

**🚫 Blocking pre-A2-Dara dispatch:**
1. R14 closure — S1-retry-0915 + 0315 qfd root cause → `OPERATOR_PENDING` (R14-CLOSURE-CHECKLIST §2-§3)
2. R15 token rename `chunk_runner.py:49,67` + `orchestrator.py:126,419` → `SQUAD_PENDING_NELO`
3. Quirks registry update (Q-FIN-12-E + 8-slot MarketLogin slot-6 + AP-D-14 NEW + 25% aggressor + Q-PATH-14-V) → `SQUAD_PENDING_NELO`
4. WDOFUT parse-time hard-reject `chunk_runner.py:56` → `SQUAD_PENDING_NELO`
5. Quarantine code gap fix `orchestrator.py:654-657` (`quarantined_pre_abort` flag) → `SQUAD_PENDING_RIVEN`
6. AC adjudication T003.A2 (downgrade ∨ T003.A3) → `SQUAD_PENDING_PAX`

**📋 Pre-register / governance:**
7. α-correction pre-register doc → `SQUAD_PENDING_MIRA`
8. Hard-cap 2024-01-01 codified — `RATIFIED` (this §6 entry)
9. R12 invariance reaffirmed — `RATIFIED` (§2.4 R12 PRESERVED UNCHANGED)
10. Governance debt curve disclosure → `SQUAD_PENDING_RIVEN`

**🔗 Downstream (sequenced post-amendment, in chain order):**
11. A3-Nova auction-hours pre-2024 → `DEFERRED_TO_A3`
12. A3-Nova cost atlas pre-2024 ruling → `DEFERRED_TO_A3`
13. A2-Dara WDOZ23→WDOG24 roll synthesis verify → `DEFERRED_TO_A2`
14. A2-Dara schema parity 2-3 sessions ref month 2024-01 frozen → `DEFERRED_TO_A2`

**🧹 Operational:**
15. D:\ cleanup 7 dirs quarantine → `OPERATOR_PENDING` (R14-CLOSURE-CHECKLIST §4)

### §6.2 Anti-Article-IV Guards 1-8 ratification

Confirmed independently by Riven, Mira, Aria: **0/8 guards affected**. Amendment scope-bounded to data acquisition only.

### §6.3 Article II preservation

PR #22 OPEN; not yet merged main. All future commits (squad remediation chain §6.1 items 2-7, 10) on branch `t003-a1-dll-probe-2023-12`. @devops Gage exclusive for push/merge — to be invoked after squad remediation lands.

### §6.4 Article IV preservation

Each ballot self-audited. Source anchors filed per ballot. This resolution traces every claim to: original Council 2026-05-01 R-clauses, empirical findings 2026-05-02..03 in commits cbd6813/b6e3a5b/c7b1423/b1802ac, Sable meta-audit MA-01..MA-11, and 6 squad ballots.

### §6.5 MA-02 push provenance — CLEARED

Sable meta-audit MA-02 (CRITICAL: Article II push provenance unverified) resolved 2026-05-03 by user authority declaration: *"(b) I (the user) pushed manually under my R10 absolute authority"*. Article II discipline observed in spirit — @devops Gage normally executes push; user explicit override is supra-Article-II per R10 hierarchy (user is supreme MWF cosign holder, above any agent boundary). No ESC required. MA-02 status: **`CLEARED_USER_AUTHORITY`**. All future pushes from this branch (squad remediation bundle pending R14 + R14 outcomes commit) must invoke @devops Gage per default discipline; user override remains available but is exception-not-rule.

---

**Status:** **`RATIFIED_R1_AMENDMENT_2026_05_03`** — squad-side remediation tracks dispatching parallel; operator-side R14 closure routed.
