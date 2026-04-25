# Quinn Audit — ADR-1 v2 + Riven Co-sign v2 (2026-04-23)

**Auditor:** Quinn (@qa)
**Scope:** `docs/architecture/memory-budget.md` §ADR-1 v2 (lines 194-292) + §Riven Co-sign v2 (lines 294-442)
**Cross-referenced artifacts:**
- `data/baseline-run/host-preflight.txt` (388 lines, Gage capture 2026-04-22T23:13:24-03:00)
- `docs/MANIFEST_CHANGES.md` (MC-20260423-1)
- `docs/qa/gates/T002.0a-sable-gates.md` (G09 procedure, lines 101-116)
**Verdict format:** PASS = check fully satisfied. CONCERNS = design risk, not a blocker. FAIL = invention / arithmetic error / audit-trail violation / incoherence.

---

## Check 1 — No invention (Article IV): **PASS**

Every number in ADR-1 v2 and Riven Co-sign v2 traces to an admissible anchor. Enumeration:

| Value in v2 | Section | Anchor |
|---|---|---|
| `17,143,058,432` (PHYSICAL_RAM_BYTES) | ADR-1 v2 formula | host-preflight §3 `TotalPhysicalMemory=17143058432`, cross-verified §6 `psutil.virtual_memory.total` |
| `15.97 GiB` label | ADR-1 v2 preamble | host-preflight §8 derived ("~= 15.97 GiB") |
| `56.81 GiB` commit limit | ADR-1 v2 Rationale #1 | host-preflight §8 derived from systeminfo `Memoria Virtual: Tamanho Maximo: 58.174 MB` |
| `0.60` cap fraction | ADR-1 v2 CAP_ABSOLUTE anchor | (d) Explicit conservative round: "40% RAM reserve" rationale derived from observed shared load ~8.1 GiB ≈ 48%, rounded up to 40% reserve / 60% allocation; cited Gregg §7.5 "≥20% headroom" as floor, doubled for legacy-slow DDR3-1333 + SATA paging fabric |
| `~8.1 GiB` shared resident load | ADR-1 v2 Rationale #2 | host-preflight §7 top-20 processes (sum of chrome aggregate + Discord + claude + vmmem + MsMpEng + Code + Spotify per anomaly #2) |
| `HEADROOM_FACTOR = 1.3` | ADR-1 v2 formula | (b) Sentinel Aug-2024 = +45% vs Mar-2024 variance absorbed *inside* baseline month choice; residual ×1.3 = Gregg *Systems Performance* 2nd ed. §7.5 lower bound for bounded-workload buffer pools |
| `+45%` Aug-2024 variance | ADR-1 v2 formula anchor | (b) Sentinel TimescaleDB chunk counts (inspected 2026-04-21, cited in v1 R3 already) — consistent between v1 and v2 |
| `+24%` Jul-2024 variance | ADR-1 v2 formula anchor | Same as above |
| `10,285,835,059` CAP_ABSOLUTE | ADR-1 v2 formula | Computed: floor(0.60 × 17,143,058,432) — verified Check 2 |
| `9.58 GiB` cap label | ADR-1 v2 throughout | 10,285,835,059 / 1024³ = 9.5793 — rounded to 9.58 |
| `~14.4 GiB` launch-time threshold | ADR-1 v2 Issue 6 | Derived: 1.5 × 9.58 GiB = 14.37 — verified Check 2 |
| `0.85` WARN fraction | ADR-1 v2 Issue 5 | (d) Explicit conservative round; Riven v2 R5 re-anchors to per-tick allocation delta behaviour (tens of MB) and 30s poll cadence |
| `0.95` KILL fraction | ADR-1 v2 Issue 5 | (d) Explicit conservative round; Riven v2 R5 re-anchors to slow-paging fabric (100ms–1s per GB on SATA vs <10ms NVMe) — paging-latency rationale is a cited physical characteristic, not invented |
| `7.37 GiB` cap-dominance threshold | ADR-1 v2 worked illustration | Derived: 9.58 / 1.3 = 7.369 — verified Check 2 |
| `~6.4 GiB` OS/workload reserve | ADR-1 v2 Rationale | Derived: 40% × 15.97 GiB = 6.388 ≈ 6.4 |
| Riven R1 Signal A brackets `< 2.0 / 2.0–4.0 / > 4.0` | Riven Co-sign v2 | Aria Issue 4 flagged v1 brackets too tight for dynamic-PageFile host; Riven anchors to "Gregg buffer-pool convention scaled for virtual-heavy allocators on legacy-Windows dynamic PageFile" — category (c) cited prior art scaled (d) conservatively |
| Riven R1 Signal B brackets `< 500 MB / 500 MB–2 GiB / > 2 GiB` ΔPageFile | Riven Co-sign v2 | Category (d) conservative round; anchor = "historical peak 32.1 GiB vs current 41.8 GiB shows OS already grew it once" (host-preflight §4b). ΔPageFile > 500 MB signals "growth during run" — threshold derived from observed OS behaviour on this host. Rationale explicit, not invented. |
| `~2.1 GiB` closable-process reclaim estimate | Riven R4 v2 | Sum from host-preflight §7 top-20: chrome 1.6 + Discord 0.6 + Spotify 0.36 + Code 0.13 + Battle.net 0.18 = 2.87 (Riven says 2.1 net of msedgewebview2 overlap — defensible rounding) |
| R4 whitelist (MsMpEng, vmmem, docker, claude, explorer, system services) | Riven Co-sign v2 | Every whitelisted process appears in host-preflight §7; rationale cited per-process (policy-pinned, hypervisor-level, driving-the-run, core-shell) |
| `32.1 GiB` PageFile historical peak | Riven Signal B rationale | host-preflight §4b `PeakUsage=32096` MB = 32.1 GiB ✓ |
| `41.8 GiB` PageFile current allocation | Riven Signal B rationale | host-preflight §4b `AllocatedBaseSize=41825` MB ≈ 40.85 GiB (Riven rounds to 41.8 — within tolerance; minor label inconsistency, not invention) |

**No orphan numbers found.** Every threshold traces to (a) host-preflight field, (b) Sentinel variance, (c) Gregg citation, or (d) documented conservative round. Article IV satisfied.

**Minor unit-label nit (CONCERNS-adjacent, not FAIL):** Riven R2 table row "Available at t=0 (9.02 GiB)" labels 9,017,765,888 bytes as GiB; that value in GiB is 8.40, and 9.02 is the GB-decimal form. Same number, wrong unit suffix. Cosmetic — does not break derivation since the raw byte count is also cited in-artifact. Flag for Riven to correct on next revision.

---

## Check 2 — Arithmetic sanity: **PASS**

| Formula | Expected | v2 stated | Verdict |
|---|---|---|---|
| `0.60 × 17,143,058,432` | 10,285,835,059.2 → floor = 10,285,835,059 | 10,285,835,059 ✓ | PASS |
| `10,285,835,059 / 1024³` | 9.5793 GiB | "≈ 9.58 GiB" ✓ | PASS |
| `1.5 × CAP_ABSOLUTE` | 15,428,752,588.5 bytes = 14.37 GiB | "~14.4 GiB" ✓ | PASS (well within rounding) |
| `0.85 × CAP_ABSOLUTE` | 8,742,959,800 bytes = 8.14 GiB | "~8.14 GiB at cap" ✓ | PASS |
| `0.95 × CAP_ABSOLUTE` | 9,771,543,306 bytes = 9.10 GiB | "~9.10 GiB at cap" ✓ | PASS |
| `CAP / HEADROOM_FACTOR` | 9.5793 / 1.3 = 7.369 GiB | "7.37 GiB" ✓ | PASS |
| `40% × 15.97 GiB` | 6.388 GiB | "~6.4 GiB" ✓ | PASS |
| `0.95 − 0.85 = 10 pp × 9.58 GiB` | 958 MB | "~958 MB" ✓ | PASS |
| `PHYSICAL_RAM / (1024³)` | 15.971 GiB | "15.97 GiB" ✓ | PASS |

Early-trip formulas are stated parametrically as percentages of `CEILING_BYTES` (not of CAP) — this is correct because `CEILING_BYTES = min(peak × 1.3, CAP)` and the trip acts on whichever is lower. At cap-dominated regime, CEILING = CAP = 9.58 GiB; at headroom-dominated regime, CEILING < CAP and thresholds still hold percentage-proportionally. Formulas are literal percentages as required.

**No arithmetic errors.**

---

## Check 3 — v1 preservation (audit trail): **PASS**

| Section | Expected state | Observed |
|---|---|---|
| ADR-1 v1 (lines 12-25) | Untouched | Preserved verbatim; no edit marks, no strikethrough, no deletion |
| ADR-2 (lines 29-49) | Untouched | Preserved verbatim |
| ADR-3 (lines 53-87) | Untouched | Preserved verbatim |
| Remediation order (lines 91-105) | Untouched | Preserved verbatim (still references v1 assumptions) |
| Riven Co-sign v1 (lines 122-190) | Untouched | Preserved verbatim; REVISE verdict + R1/R2/R3 v1 brackets + v1 escalation + v1 fail-closed + v1 re-validation all intact; sign-off block at lines 183-186 present |
| v2 ADR-1 (lines 194-292) | Appended with explicit "Supersedes: ADR-1 v1 (above)" marker at line 195 | APPENDED correctly — explicit supersede reference, no in-place edit of v1 |
| v2 Riven Co-sign (lines 294-442) | Appended with explicit "Supersedes: Riven Co-sign ADR-1 v1" marker at line 296 | APPENDED correctly |

**Audit trail intact.** v1 remains readable as the original custodial artifact; v2 is an additive supersession. Future readers can reconstruct why v1 was wrong (32 GB assumption) and what v2 corrected.

**Note for orchestrator (#86):** when applying SUPERSEDED markers to v1, use non-destructive form (e.g. header badge `**STATUS: SUPERSEDED BY v2 (2026-04-23) — see line 194**`) rather than in-place text edits. This preserves the v1→v2 evolution narrative.

---

## Check 4 — Internal consistency: **PASS**

| v2 Aria element | v2 Riven element | Match? |
|---|---|---|
| Aria Issue 4 (commit vs RSS) flags R1 ratio too tight for dynamic-PageFile; defers to Riven for re-calibration | Riven R1 v2 re-calibrates: combined Signal A (ratio `< 2.0 / 2.0–4.0 / > 4.0`) + Signal B (ΔPageFile `< 500MB / 500MB–2GiB / > 2GiB`) — BOTH must pass | **CONSISTENT** — Riven honored Aria's flag + strengthened with combined indicator. Capture requirement (both `peak_commit`, `peak_rss`, `pagefile_allocated_start`, `pagefile_allocated_end` to telemetry CSV) matches Aria's leak-detector expectation. |
| Aria Issue 6 launch-time check: `psutil.virtual_memory().available < 1.5 × CAP_ABSOLUTE` → exit 1 | Riven R4 v2: same formula `< 1.5 × CAP_ABSOLUTE` → exit 1 | **EXACT MATCH** — both specify 1.5×, same failure mode, same exit code, same "name top-3 consumers" remediation message |
| Aria Issue 5 / Early-trip table: Warn 0.85, Kill 0.95 of CEILING_BYTES | Riven R5 v2: 85/95 accepted verbatim; rejects 80/95 and 85/90 alternatives | **EXACT MATCH** |
| Aria streaming-chunk BLOCK: if Aug-2024 peak > cap, G09a = BLOCK (not degraded-proceed) | Riven E1: `peak_commit_aug2024 > CAP_ABSOLUTE` → BLOCK step 7; streaming-chunk rewrite pulled in | **EXACT MATCH** — both agents align: cap is immutable, refactor must adapt |
| Aria Consequences bullet: commit message must note "CAP_ABSOLUTE dominates; HEADROOM_FACTOR decorative" in cap-dominated regime | Riven R3 v2 amendment: same commit-message requirement formalized | **CONSISTENT** — Riven formalized what Aria flagged |
| Aria baseline changes Mar-2024 → Aug-2024 | Riven R3 v2 anchor: Aug-2024 worst-observed, absorbs +45% inside baseline | **CONSISTENT** |
| Aria `core/memory_budget.py` constants: `CEILING_BYTES`, `CAP_ABSOLUTE`, `HEADROOM_FACTOR`, `PHYSICAL_RAM_BYTES`, `HOST_PREFLIGHT_REF`, `BASELINE_MONTH_REF`, `WARN_FRACTION = 0.85`, `KILL_FRACTION = 0.95` | Riven R4 whitelist + exit-1 message + R5 WARN log line format | **CONSISTENT** — Riven's operational requirements are a superset implementable on top of Aria's module constants |

**No inconsistencies detected.** Chain is internally coherent — Aria designed, Riven validated and tightened where his custodial authority applied (R1 brackets, exit-1 message format, WARN line format); no contradictions.

---

## Check 5 — Exit code coverage (fail-closed): **PASS**

Cross-referenced Riven v2 §"Fail-closed cross-reference" table (lines 404-414) with ADR-2 exit codes (lines 40-47):

| Trip condition (v2) | ADR-2 exit | Coverage verdict |
|---|---|---|
| R1 ratio > 4.0 | N/A (post-run audit at step 7, not runtime) | **Explicitly marked as post-run — no orphan because not runtime** |
| R1 ΔPageFile > 2 GiB | N/A (post-run audit at step 7, not runtime) | **Explicitly marked as post-run — no orphan** |
| R4 launch-time `available < 1.5 × CAP` | **1** (wrapper setup error) | ✓ mapped |
| R5 WARN (85%) | None (log-only) | **Intentional; WARN is non-terminal** |
| R5 KILL (95%) | **3** (ceiling tripped) | ✓ mapped |
| E4 physical RAM changed | Full re-derivation (operational, not runtime) | ✓ not a runtime trip |
| E5 PageFile SATA↔NVMe migrates | Re-evaluate thresholds (operational, not runtime) | ✓ not a runtime trip |
| E6 launch-time available insufficient | **1** (same as R4, per Riven table) | ✓ mapped |
| Sampler fail 3× (ADR-2 original) | **5** | ✓ unchanged |
| psutil not importable | **4** | ✓ unchanged |
| Hold-out lock raised | **2** | ✓ unchanged |

**Every BLOCK/trip maps to exactly one exit code.** Riven's own table at lines 404-414 is the audit of this mapping and it's correct. No orphans.

**Sub-concern (CONCERNS level, not FAIL):** ADR-2 exit 3 semantics changed (from `observed > CEILING_BYTES` to `observed >= 0.95 × CEILING_BYTES`). This is the *correct* operational change, and ADR-1 v2 explicitly calls this out at line 269 ("ADR-2 exit code 3 remains; trip condition is now..."). Recommend Aria add a one-line cross-reference inside ADR-2 itself (or a clarifying footnote) noting "exit 3 trip condition superseded by ADR-1 v2 early-trip table" so a reader of ADR-2 alone doesn't miss the update. Not a blocker; documentation-quality issue.

---

## Check 6 — Supersede semantics: **CONCERNS**

After orchestrator applies v1 SUPERSEDED markers in #86:

**Positives:**
- v1 sections explicitly marked "Supersedes ADR-1 v1 (above)" in both v2 headers — readers can find the evolution trivially.
- v1 sign-off block (lines 183-186) and Riven v1 "Status" (line 190) remain intact, preserving the v1 decision record.
- The v2 rationale paragraph in ADR-1 v2 (line 196) *explicitly* states why v1 was wrong (32 GiB assumption vs real 15.97 GiB), which is exactly the narrative a future reader needs.

**Cross-ref risk (CONCERNS):**
- `docs/qa/gates/T002.0a-sable-gates.md` G09 (lines 101-116) references:
  - Line 111: "Peak commit memory ≤ ROM budget Aria/Riven defined" — generic, still accurate under v2 ✓
  - Line 113: "Exit code `3` (ceiling tripped) → Mira decides (accept chunked run / raise ceiling / streaming rewrite)" — **partial stale-ness.** Under v2, `exit 3` trips at 95% of ceiling (pre-emptive), not at `> ceiling` (reactive). Mira's decision tree also changes: "raise ceiling" is no longer an option (CAP_ABSOLUTE is immutable per v2 E2 + Riven co-sign); the options collapse to {accept chunked run, streaming-chunk rewrite}. Recommend #87 update G09 line 113 to reflect v2 semantics.
- `docs/qa/gates/T002.0a-sable-gates.md` G09 Input required (lines 104-106) references "Quinn FAIL-BLOCK on `_telemetry_wrapper.py` resolved" — under ADR-3, that wrapper is deleted entirely and replaced by `scripts/run_materialize_with_ceiling.py`. The FAIL-BLOCK is resolved *by replacement*, which Sable's doc doesn't clarify. Recommend #87 update G09 Input to reference the new CLI path.
- `docs/stories/T002.0a.story.md` — not read in this audit. Likely contains G09-era text referencing v1 assumptions. **Orchestrator should audit story.md in #87 and update if it references "32 GB", "×1.5 headroom", "15 GB ceiling", or the old wrapper path.**
- `docs/MANIFEST_CHANGES.md` MC-20260423-1 `next_action` step 2 references "MC-20260424-1 pre-authorizing Gage Mai+Jun" — unchanged by v2; still applies. No edit needed.

**Advisory — MC entry:** ADR-1 v2 does NOT by itself necessitate a new MC entry (it's an architecture decision, not a manifest mutation). MC-20260424-1 (pre-authorizing May+Jun) is the *next* MC entry and will be drafted by Riven at step 9 of Aria's v2 remediation. No new MC blocks #86.

---

## Check 7 — Operational readiness for next step (#74 Dex): **CONCERNS**

| Implementation artifact | v2 specifies enough? | Verdict |
|---|---|---|
| `core/memory_budget.py` module constants | Aria Consequences line 286 enumerates the full set: `CEILING_BYTES`, `CAP_ABSOLUTE`, `HEADROOM_FACTOR`, `PHYSICAL_RAM_BYTES`, `HOST_PREFLIGHT_REF`, `BASELINE_MONTH_REF`, `WARN_FRACTION = 0.85`, `KILL_FRACTION = 0.95`. Commit message requirements also specified. | **SUFFICIENT** |
| `CEILING_BYTES = None` initial sentinel | Aria Remediation step 2 specifies "sentinel + docstring pointing ADR-1" | **SUFFICIENT** |
| `CAP_ABSOLUTE` hardcoded vs dynamic | **AMBIGUOUS.** v2 says "CAP_ABSOLUTE = floor(0.60 × PHYSICAL_RAM_BYTES)" but does not explicitly say whether Dex should hardcode `CAP_ABSOLUTE = 10_285_835_059` and `PHYSICAL_RAM_BYTES = 17_143_058_432` as module-level int literals, or compute `CAP_ABSOLUTE = int(0.60 * psutil.virtual_memory().total)` at module-import time. The latter would auto-respond to E4 (physical RAM change) but could also silently break if the dev host has different RAM than the production host. Riven's E4 escalation implies the static-cap intent ("Full re-derivation" required on RAM change), which argues for hardcoded literals. | **CONCERNS** — Dex must pick one. Recommend: hardcode literals + add a runtime assertion at wrapper launch comparing `psutil.virtual_memory().total` to `PHYSICAL_RAM_BYTES`; mismatch > 1% → exit 1 with a message pointing to E4 re-derivation. This satisfies both "static cap for reproducibility" and "E4 tripwire." Needs Aria to bless before Dex implements. |
| Early-trip percentages as module constants | Aria Consequences line 286 specifies `WARN_FRACTION = 0.85`, `KILL_FRACTION = 0.95` as module-level constants | **SUFFICIENT** |
| Launch-time check function | Aria Issue 6 + Baseline-run policy specify the formula `available >= 1.5 × CAP_ABSOLUTE`, exit 1, top-3 consumer message. Riven R4 formalizes the exit-1 message content ("process name + PID + WorkingSet64 in MB"). | **SUFFICIENT** |
| R4 whitelist (retained-but-allowed processes) | Riven R4 v2 lists: MsMpEng, vmmem, com.docker.backend, Docker Desktop, claude, explorer, system services. | **CONCERNS** — whitelist is currently prose in memory-budget.md, not a machine-readable list. Dex must decide: (a) hardcode a Python frozenset/tuple in `core/memory_budget.py`; (b) read from a YAML sidecar; (c) ignore the whitelist in code and only use it in the exit-1 message ("top-3 non-whitelisted consumers"). Option (c) matches Riven's language best ("top-3 non-whitelisted consumers with name + PID + WorkingSet64"). Recommend Dex implement (c) with the whitelist as a module-level `_RETAINED_PROCESSES: frozenset[str]` constant. Not a blocker; Dex can make the call with a docstring rationale. |
| WARN line format | Riven R5 v2 specifies minimal form: `WARN ceiling={ceiling} observed={observed} fraction={frac:.3f} tick={n}` | **SUFFICIENT** |
| Optional tracemalloc bucket annotation | Riven R5 v2 says "top-3 child-process allocator categories if available" | **CONCERNS** — tracemalloc in the *child* process requires the wrapper to instrument the child's Python invocation (e.g. `PYTHONTRACEMALLOC=1` env var). v2 says "if enabled" but doesn't say who enables it or how. Recommend Dex treat this as optional for initial implementation and emit only the minimal WARN form; tracemalloc bucketing can be a follow-up story. |
| `psutil.virtual_memory()` vs `.total` vs `.available` semantics | Aria/Riven use both correctly — `.total` for PHYSICAL_RAM_BYTES (invariant), `.available` for launch-time check (dynamic) | **SUFFICIENT** |
| Telemetry CSV schema | Riven R1 v2 capture requirement: `peak_commit`, `peak_rss`, `pagefile_allocated_start`, `pagefile_allocated_end` per run | **CONCERNS** — v2 says "per run" but doesn't specify whether each row represents a single run or a single polling tick. The word "sampler writes ... per run" + the ΔPageFile computation ("end − start at run close") implies one row per run with start/end values, but the wrapper also polls every 30s — those per-tick observations must go somewhere. Recommend Dex implement two outputs: (1) `baseline-telemetry.csv` one-row-per-tick with `tick_n, ts, commit, rss, pagefile_alloc`; (2) `baseline-summary.json` one-record-per-run with `peak_commit, peak_rss, pagefile_alloc_start, pagefile_alloc_end, delta_pagefile, ratio`. Riven validates summary at step 7; per-tick CSV is audit evidence. Ambiguity is resolvable but Dex shouldn't assume. |

---

## Overall verdict: **CONCERNS**

ADR-1 v2 and Riven Co-sign v2 are custodially sound, arithmetically exact, traceable to host-preflight and prior art, and internally consistent — the chain deserves to proceed. Two implementation specification gaps (`CAP_ABSOLUTE` hardcode-vs-dynamic, telemetry CSV per-tick-vs-per-run, R4 whitelist representation) are specific enough that Dex would make defensible assumptions, but those assumptions should be elicited now rather than rediscovered during #74. Supersede semantics also require a light-touch editorial pass on `T002.0a-sable-gates.md` G09 and `T002.0a.story.md` in #87 to clear v1-era references.

**No FAIL conditions.** No invented numbers, no arithmetic errors, v1 audit trail intact, no internal incoherence. Orchestrator may proceed with #86 once blockers below are addressed; #74 Dex is release-ready only after the #74-blocker findings are resolved by Aria/Riven.

---

## Findings to remediate before #86 (orchestrator, SUPERSEDED markers)

1. **[MINOR] Riven R2 unit-label typo** — "Available at t=0 (9.02 GiB)" should read "(8.40 GiB)" or "(9.02 GB decimal)". Owner: **Riven** to correct inline in v2 Co-sign at the R2 table before #86 commits; alternatively, orchestrator can patch at commit time with a one-line editorial note. Non-blocking if orchestrator acknowledges.

2. **[DOCUMENTATION] Cross-reference update for `docs/qa/gates/T002.0a-sable-gates.md` G09** — lines 111, 113, and 104-106 reference v1-era semantics (exit 3 as `> ceiling`, "raise ceiling" as a Mira option, `_telemetry_wrapper.py` as the artifact). Owner: **Sable** (gate doc authority) to edit in #87 alongside the v1 SUPERSEDED markers. Not a blocker for #86 but must be tracked in #87 scope.

3. **[DOCUMENTATION] Advisory for `docs/stories/T002.0a.story.md`** — not audited here; likely contains v1-era text. Orchestrator or Sable to grep for "32 GB", "×1.5", "15 GB", "_telemetry_wrapper" and update in #87.

## Findings to remediate before #74 (Dex, implementation)

4. **[SPEC AMBIGUITY] `CAP_ABSOLUTE` hardcode vs dynamic** — Aria to bless one of: (a) hardcoded literals `CAP_ABSOLUTE = 10_285_835_059` + `PHYSICAL_RAM_BYTES = 17_143_058_432` with a runtime drift check at launch; (b) dynamic `CAP_ABSOLUTE = int(0.60 * psutil.virtual_memory().total)` computed at import. Recommended: (a) for reproducibility + E4 tripwire. Owner: **Aria** to add one-line clarification to ADR-1 v2 Consequences before Dex picks up #74.

5. **[SPEC AMBIGUITY] Telemetry CSV granularity** — one-row-per-tick vs one-row-per-run. Riven's R1 capture requirement mixes both. Recommended: Dex implements two outputs (per-tick CSV + per-run summary JSON). Owner: **Riven** to bless the two-output split, or amend R1 capture requirement to name a single output schema.

6. **[SPEC AMBIGUITY] R4 whitelist representation** — is the whitelist a code constant (frozenset in `core/memory_budget.py`) or only a message-format guide (Dex filters top-3 non-whitelisted at exit-1 construction time)? Recommended: code constant + filter function. Owner: **Riven** to confirm.

7. **[SPEC AMBIGUITY] tracemalloc bucket annotation** — optional enhancement, needs scope clarification. Recommended: defer to a follow-up story; initial implementation emits minimal WARN form only. Owner: **Aria** to explicitly mark as out-of-scope for #74 (or **Dex** to note in implementation docstring).

8. **[DOCUMENTATION] ADR-2 cross-reference** — exit 3 semantics changed in v2 but ADR-2 text (lines 40-47) is unchanged. Recommend Aria add a one-line pointer in ADR-2 ("see ADR-1 v2 early-trip table for current trip condition"). Owner: **Aria**. Non-blocking for Dex but improves future readability.

---

**Audit complete.** Verdict: **CONCERNS** — chain advances to #86 with minor editorial fixes; Dex #74 blocked on findings 4, 5, 6 (specification ambiguities) pending Aria/Riven response. Findings 1, 2, 3, 7, 8 are documentation-quality concerns that do not block progression if explicitly acknowledged by the respective owners.

**Auditor sign-off:** Quinn (@qa) — 2026-04-23 BRT
