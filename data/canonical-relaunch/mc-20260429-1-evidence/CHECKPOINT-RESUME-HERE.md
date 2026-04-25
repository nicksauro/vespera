# MC-20260429-1 Resume Checkpoint — 2026-04-25

> **STATUS UPDATE 2026-04-25T15:08Z (Morgan @pm — Stage-2 closure):** **CLOSED-MC-29-1-DECISIONS-3-AND-4-FULLY-LANDED.** All four governance/closure steps for task #71 are now complete. (1) Riven Decision 9 post-execution co-sign appended to `docs/MANIFEST_CHANGES.md` as `MC-20260429-1` `custodial_signoff` entry under MC-23-1 schema parity (12/12 deterministic checks PASS; signed by Orion-on-Riven-behalf under R10 delegation pattern; consumption clock window CLOSED). (2) Sable G10 post-relaunch rehash executed against 19-row manifest — 16/16 frozen checks vs MC-20260423-1 + 18/18 self-match checks vs current canonical = PASS, evidence persisted at `docs/qa/gates/evidence/T002.0a/g10-rehash-19.txt`. (3) Task #71 (MC-29-1 Decisions 3+4 production runs) **CLOSED** by Morgan — all governance preconditions satisfied; Sentinel-derived data fully landed for May+Jun 2025; in-sample window now extends 2024-07 → 2025-06 contiguous (12 months, ~210M rows total). (4) Gage commit/push **DEFERRED-TO-OPERATOR** — working tree dirty but local-custodial OK per Orion's standing instruction; user retains push-timing authority. **Task #81 (Sable G10) COMPLETE.** **Task #87 (PM AC re-validation) ready to proceed against finalized 19-row state.** **Task #36 (Beckett CPCV) technically unblocked from MC-29-1 closure side; remaining T002.0a gates G01/G06/G07/G08 still gate story Done independently.** Manifest sha unchanged from D4 (`78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`); core/memory_budget.py unchanged (`1d6ed8...287d`). MC-29-1 ONE-SHOT clock state: **STARTED-CONSUMED-DECISIONS-3-AND-4-CLOSED**. Future canonical manifest mutations require new MC-YYYYMMDD-N issuance.
>
> **PRIOR STATUS (superseded — preserved for audit) 2026-04-25T14:31Z (Gage @devops):** **RESUMED-COMPLETE-DECISION-4-SUCCESS.** Decision 4 (Jun-2025) executed cleanly on FIRST attempt under Riven-delegated authority (Q1-Q6 preconditions ALL PASS). Wrapper exit 0, child PID 4664, wall-clock 180.7s, child peak commit **11.556 GiB** / wset 11.156 GiB (under 12.5 GiB R5 ceiling, **+965 MiB HEALTHY margin** vs D3's tight +104 MiB). Cosign-banner present in run log → post-banner exit 0 = in-Decision SUCCESS per Riven §3.3 distinguisher. Parquet `data/in_sample/year=2025/month=06/wdo-2025-06.parquet` created (sha `c89edf9f1d3e2b4746e15e2c9412c6c784ea702ae73ca1a69a67adcd62425c94`, **16_034_706 rows** — exact match to P3 evidence, 77.34 MiB). Manifest row 19 appended; new manifest sha `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` (was `b1f4c34c...86d4`). D6/D4/D6-post all PASS. `core/memory_budget.py` sha unchanged (`1d6ed8...87d`). **Hold-out boundary preserved:** parquet max_ts = 2025-06-30T17:59:59.557 < 2025-07-01 hold-out start; min_ts = 2025-06-02T09:00:44 (Jun-1 was Sunday, expected). MC-29-1 ONE-SHOT clock state: **STARTED-DECISION-3-AND-4-CONSUMED-WITH-SUCCESS** — both ONE-SHOT slots used productively. Decision 4 retry budget consumed: **0 slots** (3 R4-class slots remain untouched; first-attempt clean SUCCESS). Task #71 **COMPLETE-PENDING-MORGAN-CLOSE**; downstream task #81 (Sable G10 post-relaunch rehash) **FULLY UNBLOCKED** (both Mai+Jun parquets now available). Evidence: `decision-4-jun-2025-result-success.json`. Memory-budget.md §R10 Custodial — MC-20260429-1 — ISSUED STAGE 2 block updated with full Decision-4 execution record.
>
> **PRIOR STATUS (superseded — preserved for audit) 2026-04-25T14:20Z (Gage @devops):** **RESUMED-COMPLETE-DECISION-3-SUCCESS.** Retry-3 invocation under Riven Ruling B-extended-2 (Q1-Q6 preconditions ALL PASS) completed cleanly. Wrapper exit 0, child PID 10392, wall-clock 240.6s, child peak commit 12.398 GiB / wset 11.590 GiB (under 12.5 GiB R5 ceiling, +104 MiB margin). Cosign-banner present in run log → post-banner exit 0 = in-Decision SUCCESS per Riven §3.3 distinguisher. Parquet `data/in_sample/year=2025/month=05/wdo-2025-05.parquet` created (sha `561f443c16f36d6d07c01868a3343caa1cd4363d1e1c6b41a9dc909256427875`, 17_249_667 rows, 81.98 MiB). Manifest row 17 appended; D3 sha was `b1f4c34c5aeb3ccca851a7725ae1c91d35dee98790c51959dc9e2ee369bc86d4`. **RESOLVED by Decision 4 SUCCESS above.**
>
> **PRIOR STATUS (superseded — preserved for audit) 2026-04-25 (Riven @risk-manager R10):** RIVEN RULING ISSUED — `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md` (verdict B-extended-2: MC PRESERVED). Cosign-guard exit 11 ruled pre-Decision-3 fail-closed gate (same structural class as R4 / Decision-1). MC-29-1 ONE-SHOT clock remained STARTED-PAUSED. Retry-3 AUTHORIZED under Q1-Q6 preconditions (Q6 NEW: cosign env vars must be exported in invocation shell). Retry budget for Decision 3 extended one-time from 3 → 5 cumulative pre-Decision-gate slots. Decision 4 ceiling unchanged at 3. Distinguisher for future runs: presence of `[manifest-mode] CANONICAL path=... cosign=MC-20260429-1` banner in run log marks transition from gate-class (PRESERVED) to disposition-class (CONSUMED if exit ≥ 10 thereafter). **RESOLVED by retry-3 SUCCESS + Decision 4 first-attempt SUCCESS above.**
>
> **PRIOR STATUS (superseded — preserved for audit) 2026-04-25T13:57Z (Gage @devops):** Retry #2 INVOKED post-reboot. Q1-Q5 ALL PASSED (RAM 9.49 GiB margin). Wrapper invoked, child spawned, child EXITED 11 from `_guard_canonical_write` — missing `VESPERA_MANIFEST_COSIGN` env var. Zero data-plane side-effects. **RESOLVED by Riven extension ruling.**

## State at checkpoint capture

- **Date captured:** 2026-04-25 (initial); UPDATED 2026-04-25T14:31Z post-Decision-4 first-attempt SUCCESS
- **Branch:** `main`
- **HEAD:** `b97ac0370302755b204bc7b3e3cd8509e771c33a` (post-PR #3 squash merge by Gage at 2026-04-24T22:41:13Z UTC; unchanged — Gage did NOT commit during retry-3 or D4 per brief constraints)
- **Working tree:** dirty (new evidence files + memory-budget.md D4 edit + new Jun parquet + mutated manifest — all expected canonical drift authorized by D4 cosign commit)
- **Status flag:** `CLOSED-MC-29-1-DECISIONS-3-AND-4-FULLY-LANDED` (PM closure 2026-04-25T15:08Z; was `RESUMED-COMPLETE-DECISION-4-SUCCESS` post-D4 SUCCESS; was `RESUMED-COMPLETE-DECISION-3-SUCCESS` between D3 retry-3 SUCCESS and D4 SUCCESS)

## Canonical invariants (current state post-D4 Jun commit)

| Path | sha256 |
|------|-----------------|
| `data/manifest.csv` | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` (NEW — post-Decision-4 Jun commit; row count 19 = header + 18 data rows; row 18 = Mai-2025 WDO; row 19 = Jun-2025 WDO) |
| `core/memory_budget.py` | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` (UNCHANGED — R1-1 invariant preserved across both D3 and D4 commits) |

**Manifest sha lineage (preserved for audit):**
- Stage-2 ISSUED (pre-D3): `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`
- Post-D3 (Mai-2025 commit): `b1f4c34c5aeb3ccca851a7725ae1c91d35dee98790c51959dc9e2ee369bc86d4`
- Post-D4 (Jun-2025 commit, current): `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`

**Both D3 + D4 SUCCESS — no further wrapper invocations expected under MC-29-1.** Remaining work is governance ledger closure (Riven Decision 9 post-execution co-sign in `docs/MANIFEST_CHANGES.md` per MC-23-1 schema parity).

## Governance state shas (informational)

| Path | sha256 |
|------|--------|
| `docs/architecture/memory-budget.md` | DRIFTED (post-D4 edit appending Decision-3 SUCCESS execution record) |
| `docs/governance/mc-20260429-1-r4-halt-ruling.md` | `d327b54425c6b077e65d333a0a16652a249094e51db731f28883a6d46bd76bb8` (UNCHANGED) |
| `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md` | (Riven ruling B-extended-2 — sha to be recorded by Orion if needed) |

## MC-20260429-1 status

- **Stage-2 ISSUED** at 2026-04-24T22:42:35Z UTC (Orion under Riven-delegated authority).
- **Consumption clock state:** `STARTED-DECISION-3-AND-4-CONSUMED-WITH-SUCCESS` — both ONE-SHOT slots used productively. Window remains OPEN until Decision 8 SUCCESS (governance closure pending Riven D9 co-sign in MANIFEST_CHANGES.md).
- **Pre-Decision-gate retry budget under MC-29-1 Decision 3 (final state):** **1 slot remaining** under one-time-extended 5-slot ceiling. Used: attempt-1 R4, retry-1 R4, retry-2 cosign, retry-3 SUCCESS. (Slot will not be exercised — D3 already consumed productively.)
- **Decision 4 budget (final state):** **3 R4-class slots remaining (UNTOUCHED)** — first-attempt SUCCESS, no R4 or cosign-guard pre-flight aborts.
- **Sentinel container:** `sentinel-timescaledb` UP at port 5433 (verified pre-D4 Q4).
- **Hold-out boundary:** preserved across both commits (manifest row 18 = 2025-05 max_ts 2025-05-30T18:29:59.617; row 19 = 2025-06 max_ts 2025-06-30T17:59:59.557; zero drift past 2025-06-30).

## Resume procedure (HISTORICAL — Decision 4 already executed)

> **NOTE:** Decision 4 was executed successfully on first attempt at 2026-04-25T14:28:24Z UTC. The procedure below is preserved for audit reference only; no further wrapper invocations are pending under MC-29-1. Next action is **Riven Decision 9 post-execution co-sign in `docs/MANIFEST_CHANGES.md`** (governance ledger closure under MC-23-1 schema parity).

D4 was invoked via:
```bash
export VESPERA_MANIFEST_COSIGN=MC-20260429-1
export VESPERA_MANIFEST_EXPECTED_SHA256=b1f4c34c5aeb3ccca851a7725ae1c91d35dee98790c51959dc9e2ee369bc86d4
.venv/Scripts/python scripts/run_materialize_with_ceiling.py --run-id jun-2025 --start-date 2025-06-01 --end-date 2025-06-30 --ticker WDO --source sentinel --poll-seconds 30
```
Result: exit 0, child PID 4664, peak commit 11.556 GiB, 16,034,706 rows, manifest sha → `78c9adb3...ee72`.

## Open task tracker (resume context)

| Task | Status | Owner | Notes |
|------|--------|-------|-------|
| #71 | **CLOSED** (2026-04-25T15:08Z) | pm (morgan) | MC-29-1 D3+D4 SUCCESS; Riven D9 co-sign appended to MANIFEST_CHANGES.md; Sable G10 PASS; Gage commit/push DEFERRED-TO-OPERATOR |
| #81 | **CLOSED** (2026-04-25T15:03Z) | sable | G10 post-relaunch rehash PASS — 16/16 frozen + 18/18 self-match; evidence at docs/qa/gates/evidence/T002.0a/g10-rehash-19.txt |
| #36 | pending | backtester (beckett) | T002 CPCV gate — gated on #51; technically unblocked from MC-29-1 side, awaits remaining T002.0a gates (G01/G06/G07/G08) |
| #51 | in_progress | pm (morgan) | T002.0a-0e critical path orchestration |
| #59 | in_progress | dara+riven | W1.A T002.0a custodial+parquet |
| #61 | pending | sable | T002.0a process-exit gate checks |
| #80 | pending | sable | G01/G06/G07/G08 execution |
| #87 | **READY** | pm (morgan) | T002.0a AC re-validation against finalized 19-row manifest (sha 78c9ad...ee72) |
| Gage commit/PR/push | **DEFERRED-TO-OPERATOR** | devops (gage) | Working tree dirty (canonical drift authorized by D3+D4+D9+G10); local-custodial OK; awaits operator dispatch on push timing |

## Files to consult on resume

- **NEW Riven D9 co-sign entry: `docs/MANIFEST_CHANGES.md` (`MC-20260429-1` `custodial_signoff` block, appended at end of file)**
- **NEW Sable G10 evidence: `docs/qa/gates/evidence/T002.0a/g10-rehash-19.txt` (16/16 frozen + 18/18 self-match PASS)**
- This checkpoint: `data/canonical-relaunch/mc-20260429-1-evidence/CHECKPOINT-RESUME-HERE.md`
- **NEW Latest evidence (Decision 4 Jun-2025 SUCCESS): `data/canonical-relaunch/mc-20260429-1-evidence/decision-4-jun-2025-result-success.json`**
- Predecessor evidence (Decision 3 Mai-2025 SUCCESS): `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-success.json`
- Riven ruling (parent): `docs/governance/mc-20260429-1-r4-halt-ruling.md`
- Riven ruling (extension B-extended-2): `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md`
- MC-29-1 Stage-2 ISSUED block (now updated with Decision-3 + Decision-4 SUCCESS records): `docs/architecture/memory-budget.md` §R10 Custodial — MC-20260429-1 — ISSUED STAGE 2
- Prior evidence (retry-2 HALT): `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-retry-2.json`
- Prior evidence (retry-1 ABORT): `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result-retry-1.json`
- Initial evidence (attempt-1 ABORT): `data/canonical-relaunch/mc-20260429-1-evidence/decision-3-may-2025-result.json`
- Q5 D4 pre-Jun snapshot: `data/canonical-relaunch/mc-20260429-1-evidence/q5-pre-jun-manifest-snapshot-d4.txt`
- Q5 D3 retry-3 snapshot: `data/canonical-relaunch/mc-20260429-1-evidence/q5-pre-may-manifest-snapshot-retry-3.txt`
- Cosign guard spec: `docs/architecture/manifest-write-flag-spec.md` §4
- P1 evidence: `data/canonical-relaunch/mc-20260429-1-evidence/p1-pr3-merge-commit.txt`
- P3 evidence: `data/canonical-relaunch/mc-20260429-1-evidence/p3-sentinel-smoke.json`
- **NEW Jun-2025 parquet:** `data/in_sample/year=2025/month=06/wdo-2025-06.parquet` (sha `c89edf9f...c94`, 16_034_706 rows, 77.34 MiB)
- Mai-2025 parquet: `data/in_sample/year=2025/month=05/wdo-2025-05.parquet` (sha `561f443c...875`, 17_249_667 rows)
- Jun-2025 telemetry CSV: `data/jun-2025-telemetry.csv`
- Jun-2025 summary JSON: `data/jun-2025-summary.json`
- Jun-2025 run log: `data/jun-2025.log`
- May-2025 telemetry CSV: `data/may-2025-telemetry.csv`
- May-2025 summary JSON: `data/may-2025-summary.json`
- May-2025 run log: `data/may-2025.log`

## Outstanding edits to memory (auto-memory)

None at this checkpoint — auto-memory `MEMORY.md` does not require updates for this success record (Vespera/Sentinel data-source notes are unchanged).
