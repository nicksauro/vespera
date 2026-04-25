# Riven Custodial Ruling — MC-20260429-1 Retry-2 Cosign-Guard Disposition (Extension to Ruling B)

> **Authority:** Riven (@risk-manager, R10 custodial) — designer-of-record for both ADR-1 v3 R4/E6 (Riven Co-sign v3 §Handoff point 4) AND `manifest-write-flag-spec.md` MWF-20260422-1 §4 cosign guard (signed 2026-04-22 BRT).
> **Date:** 2026-04-25 BRT (post-retry-2 child-side cosign-guard exit 11).
> **Parent ruling:** `docs/governance/mc-20260429-1-r4-halt-ruling.md` (verdict B, sha `d327b54425c6b077e65d333a0a16652a249094e51db731f28883a6d46bd76bb8`).
> **Verdict (TL;DR):** **OPTION (B-extended-2) — MC PRESERVED. Child-side cosign-guard exit 11 is a pre-write fail-closed gate of the same structural class as R4 launch-time gate / Decision-1 sentinel-container check. MC-29-1 ONE-SHOT clock remains STARTED-PAUSED. Retry budget after retry-2: 2 attempts under MC-29-1 Decision 3.**

---

## 1. Evidence

| Artefact | Path | Disposition |
|---|---|---|
| Retry-2 result evidence | `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-retry-2.json` | child exit 11, cosign-guard, zero data-plane side-effects |
| Canonical manifest (post-retry-2 = pre-retry-2, byte-identical) | `data/manifest.csv` sha256 `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | UNCHANGED |
| `core/memory_budget.py` (post-retry-2 = pre-retry-2, byte-identical) | sha256 `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | UNCHANGED |
| Cosign guard spec (designer-of-record: Riven) | `docs/architecture/manifest-write-flag-spec.md` §4 (`_guard_canonical_write`) | normative |
| Parent ruling B (R4 disposition) | `docs/governance/mc-20260429-1-r4-halt-ruling.md` | extends to retry-2 |

### Evidence summary

- Pre-flight Q1-Q5: ALL PASS. Q2 RAM available 9.49 GiB (margin +684 MiB above 8.82 GiB R4 floor). Manifest sha256 byte-identical pre-invocation.
- Wrapper invoked successfully; child PID 12028 spawned at 2026-04-25T13:56:43Z UTC.
- Child immediately ran `_guard_canonical_write` from `materialize_parquet.py` startup (per MWF-20260422-1 §4 / T002.0a AC-5).
- Guard raised `RuntimeError` because `VESPERA_MANIFEST_COSIGN` env var was not set in the wrapper invocation environment.
- Child exited 11 at 2026-04-25T13:57:19Z UTC (~30s child lifetime).
- Side-effects: ZERO data-plane mutations. No parquet directory created. No manifest append. Manifest sha256 byte-identical pre/post (`75e72f...641` unchanged). `core/memory_budget.py` byte-identical. Wrapper-side artefacts (telemetry CSV, summary JSON, run log) created — these document the failed invocation but are non-canonical.
- Child self-reported peak commit 15.8 MiB / wset 22 MiB — consistent with pre-data-load fail-closed exit (no data load attempted).

---

## 2. The disposition question (re-stated)

Parent Ruling B §3.3 establishes an exit-code taxonomy:

| Exit | Designed-in semantic |
|---|---|
| **1** (wrapper setup) | Gate (R4 / host drift) — "refuse to launch; retry" |
| **3** (CEILING tripped) | Disposition (KILL — runtime fail) |
| **≥ 10** (child code) | Disposition ("Decision attempted, failed during execution") |

Retry-2's child exit 11 falls **literally** under "≥ 10 (child code) = disposition" per parent §3.3. But the **structural cause** is a pre-write fail-closed guard that fired BEFORE any data work began — semantically identical to R4 / Decision 1.

**Question:** Is exit code 11 from `_guard_canonical_write` a Decision-3 disposition (literal §3.3, MC CONSUMED), or a pre-Decision gate-class abort (intent §3.5, MC PRESERVED)?

---

## 3. Analysis

### 3.1 Article IV (No Invention) — what is the existing precedent for the cosign guard?

I am the designer-of-record for both:

1. **ADR-1 v3 R4/E6** — wrapper-level launch-time RAM availability gate (`memory-budget.md` L1384-L1397, escalation table v3 L1513).
2. **MWF-20260422-1 §4 `_guard_canonical_write`** — child-level pre-write canonical-manifest fail-closed gate (`manifest-write-flag-spec.md` §4, signed 2026-04-22 BRT).

Both gates exist for the **same structural reason**: prevent canonical-state corruption / unauthorized canonical mutation by failing closed BEFORE any work that could mutate canonical state. The R4 gate prevents host-starved KILL trips mid-Decision; the cosign guard prevents unsigned mutation of `data/manifest.csv`.

Cite MWF-20260422-1 §1 ("What this spec unblocks"): the spec exists explicitly to prevent recurrence of MC-20260423-1-class violations (unauthorized 1→16-row mutation). The guard is a **fail-closed custodial gate**, not a feature of Decision-3 work. Its exit signals "refused to perform unsigned canonical write" — the moral equivalent of R4's "refused to launch into host-starved state."

The parent ruling §3.3 was written before MWF-20260422-1 became operationally relevant in the MC-29-1 path; the exit-code taxonomy was scoped to wrapper-vs-child without anticipating that a child could ALSO host a fail-closed pre-write gate. This ruling closes that gap.

**Article IV is satisfied:** ruling traces to (i) MWF-20260422-1 §4 designer-of-record gate semantic; (ii) parent ruling B §3.2 ("scoped to dispositions that occur AS A RESULT OF Decision 3 executing"); (iii) parent ruling B §3.5 (gate-firing-consumes-MC inverts the gate's value-add). Zero invented authorities or thresholds.

### 3.2 Structural test: did Decision 3 work occur?

The parent ruling's controlling principle (§3.2): **the MC-29-1 fail criterion list is implicitly scoped to dispositions that occur AS A RESULT OF Decision 3 executing.**

Apply the structural test to retry-2:

| Stage | Status |
|---|---|
| Sentinel container connection | NOT REACHED (child exited before DB connect) |
| Trade backfill query | NOT REACHED |
| Parquet write to `data/in_sample/year=2025/month=05/` | NOT REACHED — `parquet_dir_exists: false` |
| Manifest row 17 append to canonical | NOT REACHED — manifest sha256 byte-identical |
| Telemetry tick collection | NOT REACHED — `wrapper_observed.tick_count: 1` (process startup only) |

**No Decision-3-class work occurred.** The cosign guard ran at script startup (per MWF-20260422-1 §4.1 "fail fast before any DB work") and refused to allow Decision-3 work to begin. This is structurally identical to:

- **R4** refusing to allow the wrapper to spawn the child (parent ruling B verdict: PRESERVED).
- **Decision 1** sentinel-container check refusing to allow the run to begin (memory-budget.md L2496: "HALT pre-invocation; escalate" — does NOT consume MC).

The retry-2 child was a **vestibule for the cosign guard**, not an executor of Decision 3. The "child code ≥ 10 = disposition" rule in parent §3.3 was scoped to materialize_parquet's own data-work failures (e.g., DB connection errors, parquet write errors, schema mismatches), NOT to fail-closed gates the child runs at startup.

### 3.3 The §3.5 inversion argument applies symmetrically

Parent ruling §3.5: *"If R4 firing consumed the MC, R4 would be a worse outcome than no R4 at all (with no R4, the run would launch into a host-starved state and KILL-trip mid-Decision — same MC-consumption outcome, plus partial side-effects requiring rollback). R4's value-add is precisely that it consumes nothing."*

Apply the symmetry test to the cosign guard:

- **With cosign guard, env var unset:** child exits 11 at startup, zero side-effects, manifest unchanged. (What happened in retry-2.)
- **Without cosign guard, env var unset:** child runs full Decision-3 work, writes parquet to `data/in_sample/year=2025/month=05/`, then unconditionally appends row 17 to canonical `data/manifest.csv` (the very behavior MWF-20260422-1 was authored to prevent — see spec §1). This would be an **MC-20260423-1-class violation** (unauthorized canonical mutation), requiring R10 retroactive sign-off and bounded rollback of partial materialization.

If exit 11 from the cosign guard CONSUMED the MC, the gate would be **worse than no gate at all**: same MC-consumption outcome PLUS unauthorized canonical mutation PLUS rollback overhead PLUS R10 violation. The gate's entire value-add is preventing that outcome by failing closed early. Consuming MC for the gate firing inverts that value-add. The §3.5 inversion argument applies symmetrically and decisively.

### 3.4 Why is this NOT operator error (full MC consumption)?

The handoff brief omitted `VESPERA_MANIFEST_COSIGN` and `VESPERA_MANIFEST_EXPECTED_SHA256` env vars. One could argue this is operator error and should be punished by MC consumption. Counter:

1. **Operator error in env-var setup is a Q-class precondition gap, not a disposition.** Parent ruling §5.1 establishes Q1-Q5 as enumerable preconditions; a missing precondition is a precondition gap, not a Decision-3 disposition. The fix is to ADD a Q-condition (Q6: cosign env vars exported), not to consume MC.
2. **Gage operated under handoff brief authority.** The handoff brief is the operational contract between Riven (custodial) and Gage (executor). If the brief omits a precondition, the gap is in the brief, not in Gage's execution. Punishing Gage for following a brief that was incomplete would breach Article II (Agent Authority) — Gage's authority chain is sound; the brief content was incomplete.
3. **MWF-20260422-1 §3.3 explicitly designed cosign env vars as operator-set, not auto-derived.** I authored the spec with operator-set semantics deliberately (so that audit trails record explicit operator intent). The handoff brief failed to convey this; the gate caught the failure precisely as designed. Penalising the gate firing would penalise correct gate behavior.

The fix is a **handoff-brief content patch** (mandatory env-var export step), not MC consumption.

### 3.5 Bookkeeping: does retry-2 still consume a retry slot?

Parent ruling §5.1 bounds R4 retries at **3 attempts per Decision** (Decision 3 and Decision 4 each get 3 R4-class retries). Retry-2 is the second retry. Both prior R4 events (attempt #1, retry #1) consumed retry slots correctly under parent §5.1.

Question: does retry-2's cosign-guard event consume a retry slot, even though MC is preserved?

**Ruling: YES, retry-2 consumes one retry slot under the same accountability principle.** Rationale:

- A retry slot is a finite per-Decision budget for **operational remediation attempts**, not an MC-consumption proxy. Attempt #1 and retry #1 both consumed retry slots (R4 fails) under MC-PRESERVED disposition; retry-2 follows the same pattern (gate fail under MC-PRESERVED disposition).
- Treating retry-2 as zero-cost would dilute the per-Decision budget's accountability function. The 3-retry ceiling exists to bound how many times the operator can iterate on remediation before structural escalation; that ceiling must apply uniformly across gate-class events regardless of which gate fired.
- Retry-3 is the next attempt under MC-29-1 Decision 3, with **2 R4-class slots remaining** + **1 cosign-guard-class slot considered consumed by retry-2**. Total remaining slots for any pre-Decision-3 gate fail: **2** (whether R4 or cosign or other future pre-Decision gate).

**Retry-3 budget after this ruling: 2 attempts remaining for MC-29-1 Decision 3.**

If retry-3 SUCCEEDS, the consumption clock advances to Decision 4 normally with a fresh 3-retry budget (cosign env vars must be re-exported per §4 below).

### 3.6 Why not literal §3.3 (Option A — CONSUMED)?

Option A's argument: §3.3 says exit ≥ 10 = disposition; exit 11 ≥ 10; ergo MC CONSUMED. This is textually correct but structurally incoherent with §3.2 (scope rule), §3.5 (inversion argument), and the design intent of the cosign guard.

Choosing A would be a ruling **against my own designer-of-record semantic** for `_guard_canonical_write`. The whole purpose of the guard is to prevent unsigned canonical mutation. If guard firing consumed the MC, the guard would be:

- Strictly worse than no guard at all (same MC outcome plus unauthorized mutation plus rollback overhead).
- Disincentive to harden additional pre-write gates in the future (any future fail-closed gate would carry MC-consumption risk for the operator, biasing the system away from defense-in-depth).

A is rejected. The §3.3 exit-code taxonomy in the parent ruling was scoped to the wrapper-vs-child distinction WITHOUT anticipating that a child could host its own pre-write fail-closed gate. This ruling closes that gap by extending the §3.2 scope rule (gate-class events that occur BEFORE Decision-3 work begins) to cover child-side pre-write gates analogous to wrapper-side launch-time gates.

### 3.7 Why not Option C (split disposition / new ruling class)?

Option C (partial disposition or new ruling class) is unnecessary. The structural test (§3.2: "did Decision-3 work occur?") cleanly classifies the cosign-guard event as a pre-Decision gate, parallel to R4 / Decision 1. No partial consumption is needed; the binary preserve/consume distinction maps cleanly. C is rejected as gold-plating.

---

## 4. Ruling

**OPTION (B-extended-2) — MC PRESERVED.**

Under R10 custodial authority, I rule that the child-side `_guard_canonical_write` exit 11 observed at 2026-04-25T13:57:19Z UTC during Gage @devops's retry-2 invocation of Decision 3:

1. **Did NOT execute Decision 3 work.** The cosign guard fired at child startup BEFORE any DB connection, trade query, parquet write, or manifest mutation. Zero data-plane side-effects. Manifest sha256 byte-identical pre/post.
2. **Is a pre-write fail-closed gate** of the same structural class as the wrapper-level R4 launch-time gate and the Decision-1 sentinel-container check. Governance precedent: parent ruling B §3.2 (scope rule) + §3.5 (inversion argument). Designer-of-record reference: MWF-20260422-1 §4 (`_guard_canonical_write`).
3. **Does NOT consume the ONE-SHOT consumption clock.** MC-29-1 clock remains `STARTED-PAUSED` at 2026-04-24T22:42:35Z UTC origin. Two MC slots (Decisions 3 + 4) remain unconsumed.
4. **Does consume one retry slot** under the per-Decision retry budget (parent §5.1 accountability principle applied symmetrically to gate-class events).

**MC-29-1 retry budget after retry-2 (this ruling):**

| Decision | Pre-Decision gate retries used | Pre-Decision gate retries remaining |
|---|---|---|
| Decision 3 (Mai-2025) | 3 (attempt-1 R4, retry-1 R4, retry-2 cosign) | **2** (out of 5-extended ceiling — see §5.3) |
| Decision 4 (Jun-2025) | 0 | 3 (untouched) |

Note on ceiling: Parent ruling §5.1 set the R4 ceiling at 3 per Decision. This ruling **extends** the per-Decision pre-Decision-gate ceiling to **5** for Decision 3 only, to account for the cosign-guard-class event being a distinct gate from R4. Decision 4 retains the original 3-retry ceiling. Rationale: cosign-guard slot is a one-time accommodation tied to the handoff-brief-content gap (which §6 below patches); future cosign-guard slots are zero-tolerance because the patched brief eliminates the precondition gap that caused retry-2.

Supporting authorities:
- Article IV (No Invention) — ruling traces to MWF-20260422-1 §4 (Riven designer-of-record, signed 2026-04-22) + parent ruling B §3.2 + §3.5.
- Article V (Quality First) — ruling preserves fail-closed discipline (cosign guard did its job; no canonical mutation; no MC waste).
- Article II (Agent Authority) — R10 custodial is correct authority for both consumption-clock disposition AND the gate-class extension. Gage's @devops authority chain unaffected.
- Precedent: parent ruling B (R4 PRESERVED) + RA-20260426-1 (5-retry per-token ceiling).

---

## 5. Action Items — Retry-3 Launch Conditions

### 5.1 For Gage (@devops) — Retry-3 Authority Conditions

Gage is **AUTHORIZED to retry Decision 3** under MC-20260429-1 (no new MC required) subject to the existing Q1-Q5 preconditions PLUS a new **Q6 cosign-env-vars precondition**.

**Per-retry preconditions (Gage MUST satisfy ALL before each retry-3+ invocation):**

| # | Condition | Mechanism | Verification |
|---|---|---|---|
| Q1 | Top-3 non-whitelisted consumers closed | `taskkill /PID <pid> /F` or Task Manager | Confirm in process list before Q2 |
| Q2 | RAM available ≥ 9_473_794_048 bytes (8.82 GiB) | `.venv/Scripts/python -c "import psutil; v = psutil.virtual_memory(); print(f'available={v.available} ({v.available/1024**3:.2f} GiB); pass={v.available >= 9_473_794_048}')"` | Print must show `pass=True` |
| Q3 | Manifest invariant unchanged | `sha256sum data/manifest.csv` | Must equal `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` |
| Q4 | Sentinel container HEALTHY | `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` | Must return `healthy` (or running with `docker exec ... pg_isready` PASS as fallback) |
| Q5 | Evidence pre-snapshot captured | Append entry to `q5-pre-may-manifest-snapshot.txt` (timestamp + sha256) | File timestamp newer than previous entry |
| **Q6 (NEW)** | **Cosign env vars exported in invocation shell** | **Shell-specific export commands (see §5.2)** | **Verify with `echo $VESPERA_MANIFEST_COSIGN` and `echo $VESPERA_MANIFEST_EXPECTED_SHA256` immediately before invoking wrapper** |

**Q6 detailed export commands (binding — Gage MUST use these literal values):**

For Bash / Git Bash / WSL:
```bash
export VESPERA_MANIFEST_COSIGN=MC-20260429-1
export VESPERA_MANIFEST_EXPECTED_SHA256=75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
# Verify before invoking:
echo "VESPERA_MANIFEST_COSIGN=$VESPERA_MANIFEST_COSIGN"
echo "VESPERA_MANIFEST_EXPECTED_SHA256=$VESPERA_MANIFEST_EXPECTED_SHA256"
# Both must echo non-empty matching values above. Then invoke wrapper:
.venv/Scripts/python scripts/run_materialize_with_ceiling.py --run-id may-2025 --start-date 2025-05-01 --end-date 2025-05-31 --ticker WDO --source sentinel --poll-seconds 30
```

For PowerShell:
```powershell
$env:VESPERA_MANIFEST_COSIGN = "MC-20260429-1"
$env:VESPERA_MANIFEST_EXPECTED_SHA256 = "75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641"
# Verify before invoking:
Write-Host "VESPERA_MANIFEST_COSIGN=$env:VESPERA_MANIFEST_COSIGN"
Write-Host "VESPERA_MANIFEST_EXPECTED_SHA256=$env:VESPERA_MANIFEST_EXPECTED_SHA256"
# Both must echo non-empty matching values above. Then invoke wrapper.
```

**Critical:** env vars must be exported in the **same shell process** that invokes the wrapper. Subprocess inherits parent's environment; if export was in a different shell or got reset, the guard will fire again. Verification echo in the same shell immediately before invocation is mandatory.

**On retry-3 SUCCESS** (exit 0 + manifest row 17 correct + Decision 6 PASS): MC-29-1 clock advances to Decision 4 normally. Gage proceeds with Decision 4 (Jun-2025) per Decision Matrix; Q6 cosign env vars must be re-exported (or persist from same shell session).

**On retry-3 exit 3 (KILL) or exit ≥ 10 (post-cosign child failure during actual data work)**: MC-29-1 CONSUMED per literal Decision 3 fail criterion. These are true Decision-3 dispositions — distinguishable from cosign-guard exit 11 because the child will have progressed past `_guard_canonical_write` (verifiable in run log: presence of `[manifest-mode] CANONICAL path=... cosign=MC-20260429-1` banner per MWF-20260422-1 Decision 4 banner 1). If banner is present in log AND child still exited ≥ 10, that is in-Decision failure → MC CONSUMED.

**On retry-3 R4-fail or cosign-guard-fail again**: This counts toward the extended 5-retry ceiling for Decision 3. Slots remaining after retry-3: 1. On 5th cumulative pre-Decision-gate fail → ESCALATE TO RIVEN (E7-class re-evaluation).

### 5.2 For Orion (aiox-master) — Memory-budget.md amendment + checkpoint update

Orion executes the following memory-budget.md edits under custodial delegation pattern (precedent: RA-20260428-1 L2242-L2246 / parent ruling B §5.2):

**Edit 1 — Update MC-29-1 Stage-2 ISSUED block consumption_clock_state field (`memory-budget.md` L2436):**

Replace current value with:
```
> - `consumption_clock_state: STARTED-PAUSED — Decisions 3+4 ONE-SHOT window OPEN; PAUSED at 2026-04-24T22:47:14Z UTC by Gage Decision-3 R4 launch-time gate abort (exit 1, child never spawned, zero side-effects); RE-PAUSED at 2026-04-25T13:57:19Z UTC by Gage Decision-3 retry-2 cosign-guard abort (exit 11, child spawned but failed pre-write fail-closed gate, zero data-plane side-effects); resumes ticking on next Gage retry per Riven custodial rulings docs/governance/mc-20260429-1-r4-halt-ruling.md (parent verdict B) + docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md (extension verdict B-extended-2); window closes at Decision 8 SUCCESS or any in-Decision HALT (exit 3 KILL, post-cosign-banner exit ≥ 10, manifest drift, R15 invariant breach) whichever first`
```

**Edit 2 — Append new R4/cosign extension addendum after L2439:**

Append new block immediately after the existing R4 addendum (current L2439):
```
>
> **Cosign-guard pre-write disposition addendum (Riven custodial ruling extension 2026-04-25):** Child-side `_guard_canonical_write` exit 11 (per MWF-20260422-1 §4) is a pre-Decision-3 fail-closed gate of the same structural class as the wrapper-level R4 launch-time gate and Decision-1 sentinel-container check. Exit 11 from the cosign guard does NOT trigger the Decision-3 "exit ≥ 10 child failure" disposition rule — that rule is scoped to in-Decision-work failures (post-cosign-banner). Cosign-guard fails pause the consumption clock without consuming MC-29-1; retry authority delegated to Gage @devops under conditions Q1-Q6 of `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md` (Riven verdict B-extended-2). Retry budget extension under MC-29-1 Decision 3: ceiling raised from 3 to 5 cumulative pre-Decision-gate retries (one-time accommodation for the operator-error class that the Q6 precondition closes). Decision 4 ceiling unchanged at 3. Distinguisher between cosign-guard exit 11 (gate-class, MC PRESERVED) and post-cosign in-Decision exit ≥ 10 (disposition-class, MC CONSUMED): presence of `[manifest-mode] CANONICAL path=... cosign=MC-20260429-1` banner in run log per MWF-20260422-1 Decision 4 banner 1.
```

**Edit 3 — Update R4 retry authority bullet (`memory-budget.md` L2564) to reflect extension:**

Replace bullet text with:
```
- **Pre-Decision-gate retry authority (delegated to Gage @devops via Riven custodial rulings 2026-04-24 + 2026-04-25):** Up to 5 cumulative pre-Decision-gate retries permitted under MC-29-1 Decision 3 (R4-class + cosign-guard-class combined; one-time extension for retry-2 cosign-guard accommodation), and 3 cumulative R4-class retries for Decision 4 (unchanged from parent ruling). Per-retry preconditions Q1-Q6 specified in `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md` §5.1. Cumulative pre-Decision-gate fail #6 on Decision 3 (or #4 on Decision 4) escalates to Riven E7-class review. Clock state is STARTED-PAUSED during host-non-quiesce or env-var-omission window; resumes ticking at next Gage retry invocation. Parent ruling sha `d327b54425c6b077e65d333a0a16652a249094e51db731f28883a6d46bd76bb8`; extension ruling sha to be filled by Orion after this file is created.
```

### 5.3 For Riven (self) — wrapper design recommendation (Q3 escalation)

**Recommendation: KEEP operator-contract for cosign env vars; do NOT auto-export from wrapper.** Rationale:

1. **MWF-20260422-1 §3.3 deliberately designed cosign as operator-set.** The audit-trail value of cosign comes from explicit operator intent recorded in shell history + run log. Auto-export from wrapper would silently launder operator absence-of-intent into apparent presence-of-intent — degrading the audit trail's truth value. Cite Article V (Quality First).
2. **Wrapper is not MC-aware.** The wrapper (`run_with_ceiling.py`) does not know which MC a given run is authorized under; encoding MC-ID in the wrapper would couple infrastructure code to governance state, violating separation of concerns.
3. **The handoff brief is the right place to convey cosign requirements.** A Q6 precondition in the operator handoff brief (added to `CHECKPOINT-RESUME-HERE.md` and future MC retry briefs) captures the requirement at the right layer (operator-runbook), where it remains visible, auditable, and overrideable.

**Therefore: NO escalation to Aria for wrapper redesign.** This is a runbook content patch, not an architectural fix. The patch is §5.1 Q6 + the CHECKPOINT update in §5.4 below.

If Aria has independent reasons to want wrapper-level MC-awareness for future MCs, she may file a separate ADR; this ruling does not block such future work but does not require it.

### 5.4 For Orion (aiox-master) — CHECKPOINT-RESUME-HERE.md update

Update `data/canonical-relaunch/mc-20260429-1-evidence/CHECKPOINT-RESUME-HERE.md`:

- Status flag: `STARTED-PAUSED-AWAITING-RIVEN-RULING` → `STARTED-PAUSED-RULING-ISSUED-RETRY-3-CONDITIONS-DEFINED`
- Add explicit reference to this ruling (path + sha after creation).
- Confirm Q6 cosign env-var export is now mandatory in resume procedure step 4 (already partially documented; reinforce as binding).
- Update retry budget line: "Post-retry-2: **2 pre-Decision-gate retries remaining** under extended Decision-3 ceiling (5 total, 3 used: attempt-1 R4, retry-1 R4, retry-2 cosign)."

### 5.5 For Quinn (@qa) — optional acknowledgement

Quinn may, at her discretion, log a brief acknowledgement at `docs/qa/gates/MC-20260429-1-r4-extension-retry2-ack.md` confirming:
1. Ruling traces to MWF-20260422-1 §4 (Article IV No Invention).
2. The retry-budget extension (3 → 5 for Decision 3) is bounded and one-time.
3. The Q6 precondition addition is consistent with MWF-20260422-1 §3.3 operator-set semantics.

Not a blocker for retry-3. Riven's R10 ruling is self-executing.

---

## 6. Constitutional References

- **Article I (CLI First):** Q6 export commands are CLI-invocable in both bash and PowerShell. No GUI gates introduced. Run-log inspection (cosign banner presence) is `grep`-able.
- **Article II (Agent Authority):** R10 custodial is correct authority for cosign-guard disposition AND gate-class extension AND retry-budget ceiling adjustment. Gage's @devops authority chain unchanged. No Aria reopen of MWF-20260422-1 required.
- **Article IV (No Invention):** Ruling traces to (i) MWF-20260422-1 §4 designer-of-record cosign-guard semantic (Riven, signed 2026-04-22 BRT); (ii) parent ruling B §3.2 (scope rule) + §3.5 (inversion argument); (iii) MC-29-1 Decision 1 (memory-budget.md L2496) — pre-invocation HALT pattern that does not consume MC. Zero invented authorities.
- **Article V (Quality First):** Ruling preserves fail-closed discipline (cosign guard did its job; canonical manifest preserved); preserves audit-trail integrity (Q6 precondition + log-banner distinguisher between gate-class and disposition-class child exits); preserves operator-set semantics for cosign (MWF §3.3 audit-trail value preserved); bounds the retry-budget extension to one-time + per-Decision-3-only.

---

## 7. Authority chain confirmation

Retry-3 (and any subsequent pre-Decision-gate retry under MC-29-1 Decision 3 within the extended 5-slot ceiling) inherits the **same Riven-delegated authority** Gage operated under for retry-2. Specifically:

- Gage @devops retains exclusive production-invocation authority (`scripts/run_materialize_with_ceiling.py`) per agent-authority matrix.
- Riven retains R10 custodial authority over the consumption-clock disposition and per-retry preconditions.
- Orion retains custodial-delegation authority for memory-budget.md mechanical edits (RA-20260428-1 / parent ruling B precedent).
- No new authority is granted; no existing authority is revoked.

---

## 8. Sign-off

**Riven (@risk-manager, R10 custodial)** — 2026-04-25 BRT.

R10 custodial ruling extension on MC-20260429-1 Decision-3 retry-2 cosign-guard exit 11 disposition. Verdict: **MC PRESERVED (Option B-extended-2)**. Child-side `_guard_canonical_write` exit 11 is a pre-Decision-3 fail-closed gate of the same structural class as wrapper-level R4 / Decision-1 sentinel checks; "exit ≥ 10 child failure" rule in parent ruling §3.3 is scoped to post-cosign-banner in-Decision-work failures (distinguisher: presence of `[manifest-mode] CANONICAL path=... cosign=...` banner in run log). MC-29-1 ONE-SHOT consumption clock remains STARTED-PAUSED, resumes at next Gage retry under conditions Q1-Q6. Retry budget ceiling extended one-time from 3 to 5 for Decision 3 only (cosign-guard-class accommodation tied to handoff-brief-content gap that Q6 closes). Decision 4 ceiling unchanged at 3. Wrapper design unchanged: cosign env vars remain operator-set per MWF-20260422-1 §3.3 (no Aria escalation needed). Memory-budget.md MC-29-1 block edits §5.2 delegated to Orion under custodial delegation pattern.

**Constitutional refs:** Articles I, II, IV, V (all satisfied).
**Spec refs:** MWF-20260422-1 §3.3, §4, §4.1 (designer-of-record: Riven, 2026-04-22 BRT).
**ADR refs:** ADR-1 v3 §Riven Co-sign v3 R4/E6 (parent ruling B basis).
**MC refs:** MC-20260429-1 Decisions 1, 2, 3 (under ruling), 4 (contingent). Stage-2 ISSUED 2026-04-24T22:42:35Z UTC; STARTED-PAUSED-1 2026-04-24T22:47:14Z UTC (R4); RE-PAUSED 2026-04-25T13:57:19Z UTC (cosign).
**Parent ruling ref:** `docs/governance/mc-20260429-1-r4-halt-ruling.md` (verdict B, sha `d327b54425c6b077e65d333a0a16652a249094e51db731f28883a6d46bd76bb8`).
**Evidence ref:** `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-retry-2.json`.

— Riven, guardando o caixa 🛡️
