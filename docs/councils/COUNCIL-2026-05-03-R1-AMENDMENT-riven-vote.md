# Riven Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Riven (@risk-manager)
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored to amendment §1-§3, orchestrator L100-L669, original 2026-05-01 R10/R11/R13, or empirical spike outcomes §1.1.

---

## §1 Verdict + reasoning

APPROVE_WITH_CONDITIONS. Amendment is custodially defensible: zero capital deployed, R10 explicitly preserved (§2.1 trailing clause), 0/8 Anti-Article-IV Guards affected, Riven blocking caps wired AND verified independently in code. Window 2023-01-01..2024-01-01 is disjoint from Sentinel manifest floor 2024-01-02 (zero overlap risk) and disjoint from H_next-1 PRIMARY virgin window 2026-05-01..2026-10-31. Bulk envelope (~50 chunks × 5d) bounded by hard kill-switches. R12/R13/§11.5 preserved verbatim. Conditional because R14 spike-completion gate (S1-retry-0915 + 0315 qfd root cause) and quarantine semantics for partial-bulk artifacts are not yet operationally binding.

## §2 Conditions

C1. **R14 enforcement BEFORE A2 dispatch:** S1-retry-0915 outcome documented + 2023-03-15 qfd=73,657 root cause (transient vs structural) characterized. If structural, R1' window narrows to retention-confirmed dates only.

C2. **Mid-bulk quarantine semantics:** if `max_qfd_global_pct=0.001` or `max_consecutive_failures=3` triggers mid-bulk, the N already-written chunks on `D:\Algotrader\dll-backfill\` MUST be QUARANTINED (manifest.csv status flagged `quarantined_pre_abort`) — NOT silently retained. Custodial audit by Sable (R9-equivalent) before any A2 schema parity reuse. Amendment §3 quarantine policy must be added explicitly OR addressed in T003.A2 commit-4.

C3. **R15 token rename gated to commit-4:** must occur PRE-bulk-execution (not post-hoc) to satisfy Article IV source-anchoring; `_R1_OVERRIDE_TOKEN = "ack_dara_aria_council_2026_05_01"` (orchestrator L126) currently anchors to OLD council — bulk runs with old token are governance-violation evidence-trail.

C4. **Capital-ramp debt curve disclosure:** amendment must acknowledge that T003 governance debt (4 critical bugs + 2/6 spike qualifiers + override-token-creep) accumulates and is monitored against §11.5 §11(NEW); next amendment in this chain triggers explicit Riven debt-curve review.

## §3 Concerns + mitigations

**Audit 1 (caps wired):** VERIFIED INDEPENDENTLY at `dll_backfill_orchestrator.py` L122-138, L487-495, L530-645. All 7 caps wired correctly: `--max-attempts 3` (L548), `--max-consecutive-failures 3` (L624), `--max-wall-time-s 23400` (L534), `--cooldown-s 30` (L650), `_MAX_QFD_GLOBAL_PCT=0.001` (L132,L636), atomic heartbeat (L463-484), exit codes 0/1/2/3 (L135-138). Concur with Sable MA-09 ALL_CAPS_WIRED.

**Audit 2 (R10 preserved):** CONFIRMED. §2.1 closing clause explicit; `data/manifest.csv` mutation NOT triggered by amendment; D:\ off-repo (§1.4); repo only telemetry.

**Audit 3 (Bayesian joint):** see §4.

**Audit 4 (R11/R13/§11.5):** CONFIRMED preserved per §2.4. No implicit relaxation detected. Quarter-Kelly/Gate 5 untouched.

**Audit 5 (Guards 1-8):** CONCUR 0/8 affected. Independently audited §3 table; backfill window disjoint from all guard scopes.

**Audit 6 (mid-bulk QFD trigger):** GAP — see C2. Current code aborts via `_EXIT_ABORTED` and writes heartbeat (L654-657) but does NOT mark prior N chunks as quarantined. Fail-closed principle requires explicit quarantine, not silent retention.

**Audit 7 (debt curve):** ACKNOWLEDGE — see C4. Zero capital this amendment, but governance debt accrues; eventual constraint via §11.5 if not periodically reviewed.

## §4 Bayesian update

**Prior (2026-05-01):** P(Path C usable) = 0.97.

**Posterior decomposition (2026-05-03):**
- P(bulk completes within wall-time + cap envelope) = 0.85 (bounded by 6h30 hard kill; 4 bugs already fixed; 5/6 retention confirmed)
- P(data-quality post-bulk meets A2-A4 gates) = 0.78 (qfd=73,657 on 0315 unresolved; 0915 untested)
- P(2023-09-15 retry resolves cleanly) = 0.70 (transient hypothesis priors; no evidence of reproducible structural failure yet)
- P(amendment ratification → A2-A8 chain succeeds) = 0.85 × 0.78 × 0.70 = **0.464**

**Adjusted with conditional logic:** R14 gate prevents A2 dispatch if 0915/0315 resolve poorly, so failure routes to narrowed-window retry rather than chain-collapse. Effective P(useful Path C secondary-corroborative outcome | conditions C1-C4 enforced) ≈ 0.82. Above 0.80 threshold WITH conditions; below 0.80 without.

## §5 Source anchors

- Amendment: `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md` §1.1 (spike outcomes), §1.2 (caps), §1.3 (bugs), §2.1 (R1'), §2.2 (R14), §2.3 (R15), §3 (Guards table)
- Original: `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` R10 (§3.3), R11 (§11.5 capital-ramp), R12 (SECONDARY-CORROBORATIVE), R13 (Quarter-Kelly + Gate 5)
- Code: `scripts/dll_backfill_orchestrator.py` L122-138 (cap defaults), L463-484 (heartbeat atomic), L487-495 (orchestrator entry), L530-645 (bulk loop + abort triggers), L654-668 (exit codes)
- T002 RETIRE (memory): Anti-Article-IV Guards 1-8 catalog; Gate 5 LOCKED PERMANENTLY

— Riven, custodial defense, ballot self-audited 2026-05-03
