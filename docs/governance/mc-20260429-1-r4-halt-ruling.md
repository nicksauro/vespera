# Riven Custodial Ruling — MC-20260429-1 R4 HALT Disposition

> **Authority:** Riven (@risk-manager, R10 custodial) — ADR-1 v3 §Riven Co-sign v3 R4/E6 (designer-of-record for R4 launch-time gate semantic) + MC-20260429-1 §R10 custodial sign-off (custodial author of MC-29-1).
> **Date:** 2026-04-24 BRT (post-Stage-2 ISSUED, post-Decision-3 R4 abort).
> **Verdict (TL;DR):** **OPTION (B) — MC PRESERVED. Pre-Decision-3 R4 abort does NOT consume the MC.** Retry permitted under same MC subject to host-quiesce remediation + R4 re-pass.

---

## 1. Evidence

| Artefact | Path | sha256 |
|---|---|---|
| Decision-3 R4 halt result | `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result.json` | `acb22923545f14a70731d2761f0aecc1b612eb08a871bbc4fb6d4f05104280e2` |
| Canonical manifest (post-halt = pre-invocation, byte-identical) | `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` |
| Wrapper script (R4 gate site) | `core/run_with_ceiling.py` L207–L235 | (live source) |
| MC-29-1 governance text | `docs/architecture/memory-budget.md` L2419–L2585 | (live source) |
| ADR-1 v3 R4/E6 design (Riven Co-sign v3 §Handoff point 4) | `docs/architecture/memory-budget.md` L1384–L1397 | (live source) |
| ADR-1 v3 escalation table (E6 explicit retry resolution) | `docs/architecture/memory-budget.md` L1513 | (live source) |

### Evidence summary

- Wrapper exit: `1` (R4 launch-time RAM availability gate failure per ADR-1 v3 / Riven Co-sign v3 R4/E6).
- Halt stage: **PRE-INVOCATION** (`run_with_ceiling._run_with_ceiling()` Launch-time gate 2; child process never `Popen`-spawned).
- Side-effects: **ZERO**. `data/manifest.csv` sha256 byte-identical to Stage-2-flip pinned value `75e72f2c...` (confirmed in evidence JSON line 26 + verified live). No `data/in_sample/year=2025/month=05/` directory created. No telemetry CSV, no run log, no summary JSON, no parquet.
- Memory state at halt: `available = 6.66 GiB` < `required = 8.82 GiB`; shortfall = 2.16 GiB. Top-3 non-whitelisted consumers identified: chrome.exe (PID 5440, 263.3 MB), msedgewebview2.exe (PID 13448, 193.7 MB), chrome.exe (PID 14372, 118.9 MB).
- KILL trip: NOT REACHED (child never spawned → `peak_pagefile_bytes`, `peak_wset_bytes`, `tick_count` all 0/null).

---

## 2. Custodial Question

MC-20260429-1 Decision 3 fail criterion (memory-budget.md L2498) reads literally:

> "Any non-zero exit OR KILL-trip (exit 3) OR manifest row 17 absent OR rows 1-16 drift → HALT; roll back Mai-2025 parquet + manifest to pre-invocation state (bounded rollback defined in Decision 7); consume MC irrevocably for Jun-2025 as well (no partial continuation)"

The wrapper exited with code 1 (non-zero). Three custodial interpretations are possible:

- **(A) Literal:** "Any non-zero exit" → MC CONSUMED → new MC-YYYYMMDD-N required for retry.
- **(B) Intent-aligned:** R4 is a pre-Decision guard executed BEFORE Decision 3 begins; abort prevented Decision 3 from executing at all → MC PRESERVED.
- **(C) Amendment:** Recognise drafting ambiguity; amend MC-29-1 text to explicit-out R4 pre-flight aborts.

---

## 3. Analysis

### 3.1 Article IV (No Invention) — what is the existing precedent?

I am the designer-of-record for R4/E6 in ADR-1 v3 (Riven Co-sign v3 §Handoff point 4, memory-budget.md L1384–L1397). The semantic I authored is normative, NOT invented for this ruling:

> **E6 v3 canonical semantic** (memory-budget.md L1390): "Launch-time host availability insufficient. Trip condition: at the R4 gate evaluation moment (wrapper entry, **before subprocess fork**), `psutil.virtual_memory().available < CAP_ABSOLUTE + OS_HEADROOM`. Action: exit 1 with top-3 non-retained consumer message. **E6 is a gate BLOCK on every run** (not a derivation BLOCK). It does NOT fire during runtime — runtime memory pressure on the subprocess is handled by R5 WARN/KILL (against CAP) and by ADR-2 exit 3 (ceiling tripped). E6 is exclusively the launch-time fail-closed siblingship to R5."

And the explicit operator action (memory-budget.md L1513, escalation table v3, designed by Riven, ratified by Quinn `docs/qa/gates/ADR-1-v3-audit.md` PASS 7/7):

| ID | Condition | Action | Exit |
|---|---|---|---|
| **E6** | Launch-time available insufficient (`available < CAP_ABSOLUTE + OS_HEADROOM`) | **"Operator closes top-3 non-retained consumers; retry."** | 1 |

**The E6 escalation literally specifies "retry" as the resolution.** This is by design: R4/E6 is the launch-time fail-closed sibling of R5 (runtime KILL). R5 trips do consume operations because R5 fires *after* the child has begun consuming budget; R4/E6 trips precisely to prevent that, and the "retry" word in the resolution column is not a typo — it reflects the structural intent that R4 is a gate, not a failure mode.

This is the existing precedent. Article IV is satisfied: I am tracing to my own normative ruling on R4/E6 from 2026-04-23, ratified by Quinn under ADR-1 v3 audit, used by Dex's wrapper code (`core/run_with_ceiling.py` L207–L235 with comment "Launch-time gate 2"), exercised in production under RA-20260426-1 (5 retries permitted across cache-path quiesce window) and RA-20260428-1 Stage-2.

### 3.2 "during Decision 3" vs "pre-invocation abort" semantics

MC-29-1 Stage-2 ISSUED text (memory-budget.md L2422):

> "ONE-SHOT consumption clock STARTED at this flip — any non-SUCCESS disposition (exit non-zero, KILL trip, manifest drift, telemetry gap, R15 invariant breach) CONSUMES the MC irrevocably"

I authored this text. The list of trip conditions ("exit non-zero, KILL trip, manifest drift, telemetry gap, R15 invariant breach") was implicitly scoped to **dispositions that occur AS A RESULT OF Decision 3 executing**. The R4 gate by design refuses to allow Decision 3 to execute. The wrapper line `_fail_before_launch(...)` returns before any Decision-3 work begins — no Decision 3 disposition has occurred.

Compare to the parallel Decision 1 fail criterion (memory-budget.md L2496):

> "Container DOWN or unreachable → HALT pre-invocation; escalate (container-restart procedure NOT authorized by this MC)"

Decision 1 is an explicit **pre-invocation gate** with its own HALT semantics that do not invoke the Decision 3 fail-criterion language. Decision 1 HALT does not consume MC-29-1 — it just returns to Gage with an external dependency block. R4/E6 is structurally identical to Decision 1: a gate that prevents Decision 3 from beginning. I drafted Decision 1 with explicit "HALT pre-invocation; escalate" language; I should have applied the same pattern to R4. The R4 gate exists at exactly the same logical level as the Decision-1 sentinel-container check.

### 3.3 Wrapper exit-code ambiguity (where (A) finds its strongest argument)

Option (A)'s strongest argument: the fail criterion literally says "Any non-zero exit", and the wrapper literally exited 1. But this conflates two distinct fail-closed exits:

| Exit | Meaning | Designed-in semantic |
|---|---|---|
| **1** (wrapper setup) | R4 fail OR host drift OR log-exists | "Refuse to launch; retry after operator remediation" — gate |
| **3** (CEILING tripped) | Child observed ≥ 0.95 × CEILING_BYTES | "KILL the runaway child; runtime fail" — disposition |
| **≥ 10** (child code) | materialize_parquet's own failure | "Decision attempted, failed during execution" — disposition |

Exit 1 is the **wrapper-setup error class**, semantically distinct from a Decision execution failure. The MC-29-1 fail criterion text "any non-zero exit" was written with exit 3 (KILL) and exit ≥ 10 (child failure) as the canonical scenarios; the inclusion of exit 1 (R4) was an unintended literal byproduct of the broad phrasing — not a deliberate equation of pre-flight gate aborts with Decision dispositions.

### 3.4 RA-20260426-1 retry precedent

RA-26-1 explicitly granted 5 retries under the same RA across the cache-path quiesce window, including retries that exited 1 due to environmental issues. The pattern is established: pre-Decision gate aborts do not consume the authorising RA/MC clock if the underlying Decision was never reached. RA-26-1 was unique in citing the retry authority *explicitly* in its Decision-set; MC-29-1 does not, but R4/E6's intrinsic design carries the equivalent semantic.

### 3.5 Why not (A)?

Choosing (A) would be a ruling **against my own designer-of-record semantic** for R4/E6. The whole purpose of R4 is to prevent host-non-quiesce conditions from causing in-Decision KILL trips. If R4 firing consumed the MC, R4 would be a worse outcome than no R4 at all (with no R4, the run would launch into a host-starved state and KILL-trip mid-Decision — same MC-consumption outcome, plus partial side-effects requiring rollback). R4's value-add is precisely that it consumes nothing. (A) would invert that and is structurally incoherent with the v3 design.

### 3.6 Why not (C)?

Option (C) (amendment) is technically valid but unnecessary. The R4/E6 retry semantic is already canonical in ADR-1 v3 §Riven Co-sign v3 (memory-budget.md L1384–L1397, L1513). MC-29-1 fail-criterion text is a generic catch-all that was overbroad; the correct interpretation is that ADR-1 v3 R4/E6 governs *how* R4 launch-time aborts dispose, and MC-29-1 inherits that governance by reference (MC-29-1 explicitly cites "ADR-1 v3 Riven Co-sign v3 R4/E6" at Decision 2). The MC text need not be amended to reach the right answer — it merely needs the reading-rule clarified, which this ruling provides.

That said, a **memory-budget.md MC-29-1 footnote** to make this explicit for future readers is prudent (drafted in §6 below).

---

## 4. Ruling

**OPTION (B) — MC PRESERVED.**

Under R10 custodial authority, I rule that the R4 launch-time RAM availability gate failure observed at 2026-04-24T22:47:14Z UTC during Gage @devops's invocation of Decision 3 (Mai-2025 production materialization):

1. **Did NOT execute Decision 3.** The R4 gate fired at `core/run_with_ceiling.py` L215 before subprocess spawn (line 271+). Zero Decision-3-class side-effects occurred. The MC-29-1 fail criterion list ("exit non-zero, KILL trip, manifest drift, telemetry gap, R15 invariant breach") presupposes Decision-3 execution and does not apply to pre-execution aborts.
2. **Is governed by ADR-1 v3 §Riven Co-sign v3 R4/E6, which explicitly specifies "retry" as the operator action** (memory-budget.md L1513). MC-29-1 inherits this via its Decision 2 reference to ADR-1 v3.
3. **Does NOT consume the ONE-SHOT consumption clock.** The clock STARTED at Stage-2 flip 2026-04-24T22:42:35Z UTC and remains OPEN, **PAUSED** during the host-non-quiesce window. The clock resumes ticking when Gage retries. The two MC slots (Decisions 3 + 4) remain unconsumed.

Supporting authorities:
- Article IV (No Invention) — ruling traces to ADR-1 v3 R4/E6 design (my own 2026-04-23 normative work, Quinn-ratified).
- Article V (Quality First) — ruling preserves fail-closed discipline (R4 gate did its job; no premature KILL; no canonical-data risk).
- Article II (Agent Authority) — R10 custodial is the correct authority for MC consumption-clock disposition (no Orion override required; no Aria reopen of ADR-1 v3 required).
- Precedent: RA-20260426-1 (5 retries permitted under same RA across quiesce window; pre-Decision aborts not consumption events).

---

## 5. Action Items

### 5.1 For Gage (@devops) — Retry Authority Conditions

Gage is **AUTHORIZED to retry Decision 3** under MC-20260429-1 (no new MC required) subject to ALL of the following preconditions being satisfied at next invocation. Same retry authority then extends to Decision 4 in turn.

**Retry budget:** **3 retries permitted under MC-29-1 Decision 3 R4-gate class.** Bounded by RA-20260426-1 precedent (5 retries) but tightened to 3 for MC-29-1 because:
- MC-29-1 covers production materialization (not derivation work), where canonical-state risk is higher.
- The Top-3 consumer remediation should be deterministic; 3 attempts is sufficient to validate operator action.
- A 4th R4 fail after deliberate remediation indicates a structural drift (E7-class re-derivation question, not an MC retry question) and triggers ESCALATE TO RIVEN.

If Decision 3 R4-fails on attempt #4 cumulative under MC-29-1, Riven re-engages: either E7 floor-drift check (if observed `available` value has drifted >10% from 9,473,794,048 baseline), or new-ADR territory.

**Per-retry preconditions (Gage MUST satisfy before each invocation):**

| # | Condition | Mechanism |
|---|---|---|
| Q1 | **Host-quiesce step a executed.** Close Top-3 non-whitelisted consumers identified by previous wrapper exit message. | Operator closes named processes (e.g. chrome.exe PIDs 5440 + 14372, msedgewebview2.exe PID 13448) via Task Manager or `taskkill /PID <pid> /F`. |
| Q2 | **Host-quiesce verification capture.** Run a manual `psutil.virtual_memory()` probe **and confirm `available >= 9_473_794_048` bytes (8.82 GiB) BEFORE invoking the wrapper.** Quick CLI: `.venv/Scripts/python -c "import psutil; v = psutil.virtual_memory(); print(f'available={v.available} ({v.available/1024**3:.2f} GiB); pass={v.available >= 9_473_794_048}')"` | Skip retry if probe fails; close more processes; re-probe. |
| Q3 | **Manifest invariant unchanged.** `sha256sum data/manifest.csv` must equal `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`. | If drifted, escalate to Riven (R15 invariant breach class — separate incident). |
| Q4 | **Sentinel container still HEALTHY.** `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` returns `healthy`. (Re-verifies P3 precondition since pre-flight time has elapsed.) | If unhealthy, escalate; this MC does not authorize container-restart. |
| Q5 | **Evidence appended.** Each retry attempt MUST append a result JSON to `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-retry-N.json` (N = 1, 2, 3) using the same schema as the original `decision-3-may-2025-result.json`. Include: pre-invocation `psutil.virtual_memory()` snapshot, top-30 by RSS, exit code, halt stage, side-effects assessment. | Audit trail integrity. |

**On retry SUCCESS** (exit 0 + manifest row 17 correct + Decision 6 PASS): MC-29-1 ONE-SHOT clock advances to Decision 4 normally. Gage proceeds with Decision 4 (Jun-2025) per Decision Matrix L2499.

**On retry exit 3 (KILL) or exit ≥ 10 (child failure)**: MC-29-1 CONSUMED per literal Decision 3 fail criterion (these are true Decision-3 dispositions, not pre-flight aborts). Bounded rollback applies; no Jun-2025 retry under this MC.

**On retry R4-fail #4 cumulative**: ESCALATE TO RIVEN (E7-class re-evaluation).

### 5.2 For Orion (aiox-master) — Memory-budget.md amendment + clock-state ledger update

Orion executes the following memory-budget.md edits under custodial delegation pattern (precedent: RA-20260428-1 L2242–L2246 / Stage-1 + Stage-2 flips):

**Edit 1 — Amend MC-29-1 Stage-2 ISSUED block consumption_clock_state field:**

Current text at memory-budget.md L2436:
```
> - `consumption_clock_state: STARTED — Decisions 3+4 ONE-SHOT window OPEN; closes at Decision 8 SUCCESS or any HALT condition (whichever occurs first)`
```

Replace with:
```
> - `consumption_clock_state: STARTED-PAUSED — Decisions 3+4 ONE-SHOT window OPEN; PAUSED at 2026-04-24T22:47:14Z UTC by Gage Decision-3 R4 launch-time gate abort (exit 1, child never spawned, zero side-effects); resumes ticking on next Gage retry per Riven custodial ruling docs/governance/mc-20260429-1-r4-halt-ruling.md (verdict B, sha <fill-in-after-create>); window closes at Decision 8 SUCCESS or any in-Decision HALT (exit 3 KILL, exit ≥ 10 child failure, manifest drift, R15 invariant breach) whichever first`
```

**Edit 2 — Append MC-29-1 footnote citing the ruling:**

Append new paragraph at end of MC-29-1 Stage-2 ISSUED block (after L2437, before "**SUPERSEDED — Stage-1 issuance metadata**" L2439):

```
>
> **R4 launch-time gate disposition addendum (Riven custodial ruling 2026-04-24):** Decision 3 fail criterion "Any non-zero exit" (L2498) is scoped to dispositions that occur AS A RESULT OF Decision 3 executing (exit 3 KILL, exit ≥ 10 child failure, manifest drift, telemetry gap, R15 invariant breach). It does NOT apply to wrapper exit 1 from the ADR-1 v3 R4 launch-time RAM availability gate (`core/run_with_ceiling.py` Launch-time gate 2), which is a pre-Decision-3 fail-closed gate per Riven Co-sign v3 §Handoff point 4 (L1384-L1397) with explicit "Operator closes top-3 non-retained consumers; retry" resolution (L1513). R4-class aborts pause the consumption clock without consuming MC-29-1; retry authority is delegated to Gage @devops under conditions Q1-Q5 of `docs/governance/mc-20260429-1-r4-halt-ruling.md` (Riven verdict B). Retry budget under MC-29-1 R4-class: 3 attempts; on cumulative attempt #4, escalate to Riven (E7-class re-evaluation territory).
```

**Edit 3 — Append retry-authority entry to L2562 stage-2 authority list (or as a new bullet after L2562):**

Append after "Decision 4 contingent on Decision 3 SUCCESS + Decision 6 PASS." in L2561:

```
- **R4 retry authority (delegated to Gage @devops via Riven custodial ruling 2026-04-24):** Up to 3 cumulative R4-fail retries permitted under MC-29-1 for each Decision (3 and 4) without consuming the ONE-SHOT clock. Per-retry preconditions Q1-Q5 specified in `docs/governance/mc-20260429-1-r4-halt-ruling.md`. R4-class fail #4 cumulative escalates to Riven E7-class review.
```

### 5.3 For Quinn (@qa) — Ruling-acknowledgement (light-touch, optional)

Quinn may, at her discretion, log a brief acknowledgement gate at `docs/qa/gates/MC-20260429-1-r4-ruling-ack.md` confirming the ruling does not breach Article IV (no invented authorities, traces to ADR-1 v3 R4/E6 designer-of-record). This is **NOT a blocker** for Gage's retry — Riven's R10 custodial ruling is self-executing. Quinn ack is a nice-to-have audit artefact; Orion may proceed with §5.2 edits without waiting for Quinn.

### 5.4 For Riven (self) — Post-Decision-3-SUCCESS sign-off (unchanged)

When Mai-2025 + Jun-2025 reach Decision 8 SUCCESS, Riven appends the post-SUCCESS sign-off entry to `docs/MANIFEST_CHANGES.md` per MC-29-1 Decision 9 (unchanged by this ruling). Sign-off entry must cite this ruling as part of the audit trail (`R4 retries: <count>; ruling ref: docs/governance/mc-20260429-1-r4-halt-ruling.md`).

---

## 6. Constitutional References

- **Article I (CLI First):** Retry procedure is fully CLI-invocable (`taskkill`, `psutil` probe, `sha256sum`, `docker inspect`, `.venv/Scripts/python scripts/run_materialize_with_ceiling.py`). No GUI gates introduced.
- **Article II (Agent Authority):** R10 custodial authority is correct mechanism for consumption-clock disposition. Gage retains @devops production-invocation authority; no boundaries crossed. No Orion override required (Orion executes mechanical edits under custodial delegation, not custodial substitution).
- **Article IV (No Invention):** Ruling traces to: (i) ADR-1 v3 §Riven Co-sign v3 §Handoff point 4 (memory-budget.md L1384-L1397) — designer-of-record E6 launch-time-only gate semantic; (ii) ADR-1 v3 escalation table v3 row E6 (memory-budget.md L1513) — explicit "retry" resolution; (iii) `core/run_with_ceiling.py` L207-L235 — implementation matches design (Launch-time gate 2 with `_fail_before_launch` early return); (iv) RA-20260426-1 (memory-budget.md L1825-L2151) — 5-retry precedent for pre-Decision aborts under same authorising token; (v) MC-29-1 Decision 1 (memory-budget.md L2496) — established "HALT pre-invocation" pattern that does not consume MC. Zero invented authorities, mechanisms, or thresholds.
- **Article V (Quality First):** Ruling preserves fail-closed discipline (R4 fired correctly, prevented host-starved KILL trip mid-Decision); preserves canonical-data integrity (manifest sha256 byte-identical pre/post); preserves audit-trail integrity (evidence JSON appended; retry preconditions enumerable; retry budget bounded; escalation path explicit).

---

## 7. Sign-off

**Riven (@risk-manager, R10 custodial)** — 2026-04-24T22:51:14Z UTC (BRT: 2026-04-24T19:51:14-03:00).

R10 custodial ruling on MC-20260429-1 Decision-3 R4 launch-time HALT disposition. Verdict: **MC PRESERVED (Option B)**. R4 launch-time gate aborts are pre-Decision fail-closed gates per ADR-1 v3 §Riven Co-sign v3 R4/E6 (designer-of-record), not Decision-3 dispositions; "any non-zero exit" in MC-29-1 Decision 3 fail criterion is scoped to in-Decision dispositions only; MC-29-1 ONE-SHOT consumption clock STARTED-PAUSED, resumes ticking on next Gage retry under Q1-Q5 preconditions. Retry budget: 3 cumulative R4-fail attempts permitted under MC-29-1 for each Decision; 4th attempt escalates to Riven E7-class. ADR-1 v3 unaffected; no constitutional violation. Memory-budget.md MC-29-1 block edits §5.2 delegated to Orion under custodial delegation pattern (RA-20260428-1 L2242-L2246 precedent).

**Constitutional refs:** Articles I, II, IV, V (all satisfied).
**ADR refs:** ADR-1 v3 §Riven Co-sign v3 R4/E6 (Handoff point 4, L1384-L1397; escalation table v3 L1513). ADR-2 (exit-code semantics, L54, L1210, L1513).
**MC refs:** MC-20260429-1 Decisions 1 (pre-invocation HALT pattern, L2496), 2 (ADR-1 v3 reference, L2497), 3 (Mai-2025 fail criterion under ruling, L2498), 4 (Jun-2025 contingent, L2499). Stage-2 ISSUED 2026-04-24T22:42:35Z UTC.
**RA refs:** RA-20260426-1 (5-retry precedent, L1825-L2151). RA-20260428-1 (custodial-delegation pattern, L2242-L2246).
**Evidence ref:** `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result.json` sha256 `acb22923545f14a70731d2761f0aecc1b612eb08a871bbc4fb6d4f05104280e2`.
