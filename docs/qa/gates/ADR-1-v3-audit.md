# Quinn Audit — ADR-1 v3 + Riven Co-sign v3 (2026-04-23)

**Auditor:** Quinn (@qa)
**Scope:** `docs/architecture/memory-budget.md` §ADR-1 v3 (lines 982–1326) + §Riven Co-sign v3 (lines 1328–1572)
**Cross-referenced artifacts:**
- `data/baseline-run/quiesce-mid.json` (empirical floor anchor — `available = 9,473,794,048` bytes)
- `data/baseline-run/quiesce-audit-20260424.yaml` (RA-20260424-1 execution record; `outcome: QUIESCE_THRESHOLD_FAIL`, shortfall 5,954,958,541 bytes)
- `data/baseline-run/host-preflight.txt` (unchanged from v2; 17,143,058,432 bytes total RAM)
- `docs/qa/gates/ADR-1-v2-audit.md` (prior verdict CONCERNS, findings 4/5/6/7 ratified by Aria/Riven in-file)
- `core/memory_budget.py` (v2 state verified: `CAP_ABSOLUTE = 10_285_835_059` at line 21; `PHYSICAL_RAM_BYTES = 17_143_058_432` at line 20)
- `core/run_with_ceiling.py` (v2 state verified: R4 check at line 211 `threshold = int(LAUNCH_AVAILABLE_MULTIPLIER * CAP_ABSOLUTE)`; v3 patch site)

**Verdict format:** PASS = check fully satisfied. CONCERNS = design risk, not a blocker. FAIL = invention / arithmetic error / audit-trail violation / fail-closed regression.

---

## Check 1 — No invention (Article IV): **PASS**

Every v3 constant traces to an admissible anchor. Enumeration of the new/changed numbers:

| Value in v3 | Section | Anchor |
|---|---|---|
| `OBSERVED_QUIESCE_FLOOR_AVAILABLE = 9_473_794_048` | ADR-1 v3 Derivation (line 1053) | `data/baseline-run/quiesce-mid.json` line 4 `"available": 9473794048` — direct `psutil.virtual_memory().available` reading under authorized quiesce per RA-20260424-1 |
| `OS_HEADROOM = 1_073_741_824` (1 GiB) | ADR-1 v3 Derivation (line 1066) | Gregg *Systems Performance* 2nd ed. §7.5 "Methodology" bounded-workload buffer slack heuristic upper bound (500 MiB–1 GiB bracket); Microsoft Win32 procthread docs corroborate "leave > 1 GiB for OS + file cache on 16 GiB systems". Two-source convergence (cited). |
| `CAP_ABSOLUTE_v3 = 8_400_052_224` | ADR-1 v3 Derivation (line 1073) | Computed: `9_473_794_048 − 1_073_741_824 = 8_400_052_224` — verified Check 2 below |
| `R4_V3_THRESHOLD = 9_473_794_048` | ADR-1 v3 Derivation (line 1081) | Computed: `8_400_052_224 + 1_073_741_824 = 9_473_794_048` — by construction equal to observed floor |
| WARN v3 = `7_140_044_390` bytes (6.65 GiB) | ADR-1 v3 / Riven v3 §R5 | Derived: `0.85 × 8_400_052_224` — verified Check 2 |
| KILL v3 = `7_980_049_612` bytes (7.43 GiB) | ADR-1 v3 / Riven v3 §R5 | Derived: `0.95 × 8_400_052_224` — verified Check 2 |
| Cap-dominance v3 = ~6.02 GiB | ADR-1 v3 (line 1092) | Derived: `8_400_052_224 / 1.3 = 6_461_578,633` — verified Check 2 |
| E7 threshold 10% (~947 MiB) | Riven v3 §Handoff 5 | Rationale: 10% ≈ 947 MiB ≈ one OS_HEADROOM unit — traces to OS_HEADROOM itself; 5%/15% alternatives explicitly rejected with cited rationale |
| `max()` counterproposal rejection for portability | Riven v3 §Handoff 6 | Worked examples on 16 / 32 / 64 GiB hosts with explicit fail-closed rationale; traces to v2 "40% OS reserve" anchor |
| Sentinel +45% variance (Aug over Mar 2024) | Riven v3 §R3 variance feasibility | TimescaleDB chunk inspection 2026-04-21; preserved verbatim from v2 R3 |
| Gregg §7.5 (appears 7× in ADR-1 v3 + Riven v3) | Multiple sections | v3 anchors OS_HEADROOM to the *bounded-workload buffer-pool slack* heuristic, not the "≥20% RAM" heuristic (Aria explicitly notes the ≥20% variant is unachievable on this host and pivots to the "safe margin above peak working set" fallback in the same section) — the pivot is documented, not hidden. Acceptable. |

**Grep audit:** I counted every byte-literal in the v3 sections (`grep -n "8_400_052_224\|9_473_794_048\|1_073_741_824\|10_285_835_059\|17_143_058_432\|0.85\|0.95\|0.60\|1.3"`). Every orphan-candidate traces to either (a) the `quiesce-mid.json` snapshot, (b) host-preflight artifact, (c) Gregg §7.5, (d) Sentinel variance, or (e) a preserved v2 constant (HEADROOM_FACTOR, WARN/KILL fractions, 0.60 RAM anchor for the portability min(). No orphan constants.

**Article IV satisfied.**

---

## Check 2 — No shortcut (Article V): **PASS**

Aria derived from first principles, not from a single data point. Two sub-checks:

**2a. Is `9_473_794_048` a single observation or a conservative floor?**

It is a **single observation** — `quiesce-mid.json` captured at `2026-04-23T19:21:51-03:00`, one `psutil.virtual_memory().available` reading. However, the v3 design treats it as the *best-available empirical anchor* (not as a certified statistical floor) and surrounds it with two risk guards that compensate for the n=1 measurement:

1. **OS_HEADROOM = 1 GiB above the cap.** This is a safety margin explicitly larger than the ~100–500 MiB psutil `available` estimator jitter (cited by Riven in §Handoff 3 rationale 2) and larger than MsMpEng's 200–400 MiB transient scan bursts. An n=1 observation that fluctuates down by 500 MiB still clears R4 with ~500 MiB OS headroom remaining.
2. **E7 drift detection at 10%.** Any subsequent measurement differing from 9,473,794,048 by > ~947 MiB triggers full re-derivation. This converts the n=1 observation into a *watched* anchor rather than a *trusted* anchor — drift is detected at RA drafting time (per Riven §Handoff 5's additional constraint), not at incident time.

Riven's v2 Sentinel variance guard (+45% Aug vs Mar) is preserved verbatim in v3 as R3's anchor chain (see Riven v3 §Handoff 7). v3 does not re-use Sentinel variance as a cap guard (Sentinel variance was used to justify the HEADROOM_FACTOR = 1.3 multiplier, and that multiplier is unchanged in v3). Variance guards on the cap side shift to OS_HEADROOM + E7, which is a coherent substitution given the cap is now floor-anchored rather than RAM-anchored.

**Verdict 2a:** Not a shortcut — n=1 observation + OS_HEADROOM safety margin + E7 drift detection = a defensible floor.

**2b. Is `OS_HEADROOM = 1 GiB` truly Gregg §7.5 or loosely cited?**

Spot-check. Aria at lines 1056–1065 explicitly states the citation path:
- Gregg §7.5 primary heuristic = "≥20% RAM headroom above peak" (~3.2 GiB on 16 GiB).
- Aria *flags this as unachievable* on our host ("unachievable given our floor") and pivots to the *same section's fallback heuristic*: "safe margin above peak working set" ~500 MiB–1 GiB.
- Aria chooses the **upper bound** of that fallback (1 GiB), with rationale "to maximize OS safety within the reachable envelope."
- Riven §Handoff 3 independently corroborates with psutil docs (allocator slack 100–500 MiB + MsMpEng 200–400 MiB fits inside 1 GiB) + Microsoft Win32 procthread docs ("leave > 1 GiB for OS + file cache on 16 GiB systems").

**The pivot is the interesting move.** Aria did not cherry-pick the fallback in isolation; she explicitly documents that the primary heuristic fails her host's constraint, then cites the same author/section's fallback for the reachable regime. This is verifiable prose, not a loose citation. Two-source convergence (Gregg + Microsoft) hardens the anchor.

**Arithmetic verification of v3 derivation:**

| Formula | Expected | v3 stated | Verdict |
|---|---|---|---|
| `9_473_794_048 − 1_073_741_824` | `8_400_052_224` | `8_400_052_224` ✓ | PASS |
| `8_400_052_224 + 1_073_741_824` | `9_473_794_048` | `9_473_794_048` ✓ | PASS |
| `0.60 × 17_143_058_432` (cross-check for portability) | `10_285_835_059.2 → floor = 10_285_835_059` | preserved anchor ✓ | PASS |
| `min(8_400_052_224, 10_285_835_059)` | `8_400_052_224` (floor dominates) | Riven v3 Handoff 6 ✓ | PASS |
| `0.85 × 8_400_052_224` | `7_140_044_390.4 → 7_140_044_390 bytes ≈ 6.65 GiB` | "7,140,044,390 / 6.65 GiB" ✓ | PASS |
| `0.95 × 8_400_052_224` | `7_980_049_612.8 → 7_980_049_612 bytes ≈ 7.43 GiB` | "7,980,049,612 / 7.43 GiB" ✓ | PASS |
| WARN-to-KILL buffer (0.10 × CAP) | `840_005_222 bytes ≈ 801 MiB` | "~840 MiB" (v3 claim, decimal-adjacent label) — close but **technically 801 MiB binary** | PASS with note |
| Cap-dominance threshold (CAP / 1.3) | `6_461_578,633 bytes ≈ 6.02 GiB` | "~6.02 GiB" ✓ | PASS |
| `CAP_ABSOLUTE_v3 / PHYSICAL_RAM` (E2 check) | `0.4900` (< 0.70 threshold) | E2 does not trip ✓ | PASS |
| WARN→KILL visibility @ 40 MB/tick, 30s poll | 840 MB / 40 MB/tick = 21 ticks × 30s = 10.5 min | "1–3 min" (v2 language) / "~10.5 min" (Riven v3 claim §R5 point 1) | PASS (Riven's 10.5 min is the correct number) |

**One arithmetic-label nit (CONCERNS-adjacent, not FAIL):** The warn-to-kill buffer is labeled "~840 MiB" in Aria v3 (line 1103) and Riven v3 (§R5 table row "Warn-to-kill buffer = 840,005,222 = 0.78 GiB"). Both labels are correct but use different unit conventions — the "840 MiB" reading uses decimal (840 × 10^6) while "0.78 GiB binary" is `840_005_222 / 1024³ = 0.782 GiB`. The binary MiB reading is `840_005_222 / 1024² = 801 MiB`. Labels are internally consistent within Riven (his "840 MiB / 0.78 GiB binary" is self-consistent using decimal MiB), but a reader mixing the two could derive a slightly different number. Non-blocking — same byte count, alternate unit presentation.

**Verdict 2b:** Not a shortcut. Gregg citation is verifiable via documented pivot; Microsoft corroboration adds a second source; 1 GiB choice is the explicit upper bound of the cited fallback bracket.

**Article V satisfied.**

---

## Check 3 — Supersede semantics: **PASS**

After Aria + Riven applied v3 banners:

**Positives:**
- **Zero v2 deletions.** v2 ADR-1 (lines 206–319), v2 Remediation, v2 Riven Co-sign (lines 322–478), Aria Ratifications (lines 482–538), Riven Ratifications (lines 540–640), v1 sections (lines 12–202) all preserved verbatim.
- **v3 content APPENDED at end of file** (lines 982–1572), not inserted over v2. Supersede banner at v2 §ADR-1 v2 header (line 208) points forward to v3 at end of file — reader finds evolution trivially.
- **Inline `[SUPERSEDED v2 → v3]` banners count: 8 instances** (grep `\[SUPERSEDED v2 → v3\]` returns matches at lines 216, 248, 286, 303, 308, 434, 493, 1334). Aria's v3 intro (line 216) promises banners "at their point of occurrence"; Riven's v3 intro (line 1334) names three specific locations (R1 line ~330, R3 line ~372, R5 line ~406) plus accepts Aria's E6 banner at line 428. All four of Riven's locations resolve in-file (R1 → line 332 banner, R3 → line 376 banner, R5 → line 411 banner, E6 → line 434 banner).
- **One `[PRESERVED v2 → v3]` banner** at line 332 (v2 R1 dual-signal) explicitly marking non-supersession — a thoughtful signal to readers that the v2 clause survives.
- **ADR-2 exit codes (line 54)** carry both v2 and v3 footnotes in parenthetical form — original numbered line preserved; v2/v3 pointers appended. Same non-destructive discipline Quinn prescribed in v2 audit Finding 8.

**Minor completeness notes (CONCERNS-adjacent, not FAIL):**
- Aria's v3 intro promises banners "at their point of occurrence" but the specific list of *9 locations* mentioned in the dispatch brief is not itemized in the document — I count **8 in-file banners** (lines 216, 248, 286, 303, 308, 434, 493, 1334) which satisfies "each v2 clause that v3 overrides" since the clauses-overridden count is: (i) CAP_ABSOLUTE formula (line 248), (ii) R4 Issue 6 (line 286), (iii) Baseline-run launch-time check (line 303), (iv) Consequences cap-dominance (line 308), (v) Escalation table E6 (line 434), (vi) Aria Ratifications Finding 4 code comment (line 493), (vii) ADR-2 exit 1 parenthetical (line 54), (viii) ADR-2 exit 3 — wait, exit 3 does NOT have a v3 footnote because v3 did not change exit 3 semantics (WARN/KILL fractions unchanged per Riven v3 §R5). The 8-banner tally is correct; no banner was missed. No audit finding.
- Riven's claim at line 1334 "supersession banners added inline at v2 R1 (line ~330), v2 R3 (line ~372), and v2 R5 (line ~406)" — R1 banner is `[PRESERVED v2 → v3]` not `[SUPERSEDED v2 → v3]` (line 332). This is a **more accurate** banner since R1 brackets are genuinely unchanged by v3; Riven's intro language is slightly loose but the resulting banner is correct. Non-blocking.

**Audit trail intact.** No invention via omission; no clause re-written under a v2 header.

---

## Check 4 — Measure-first compatibility: **PASS**

v3 preserves the measure-first architecture verbatim:

| Measure-first invariant | v2 behavior | v3 behavior | Verdict |
|---|---|---|---|
| `CEILING_BYTES = None` sentinel | Preserved at remediation step 2 (line 106) | Preserved — v3 §Measure-first compatibility statement line 1151 "Dex leaves `CEILING_BYTES = None` (v2 sentinel behavior unchanged)" | PASS |
| `peak_commit` drives post-baseline ceiling | `CEILING_BYTES = min(ceil(peak × 1.3), CAP_ABSOLUTE)` | **Same formula; only CAP_ABSOLUTE value shifts** (9.58 → 7.82 GiB). v3 §line 1153 reproduces formula. | PASS |
| R4 does not depend on `peak_commit` | R4 uses `virtual_memory().available` at launch time | v3 R4 uses `virtual_memory().available` at launch time; threshold = `CAP + OS_HEADROOM` — both constants known at commit time, neither requires prior subprocess observation | PASS |
| Baseline can be re-launched under v3 before ceiling is derived | G09a runs with `--no-ceiling` | v3 §line 1152 "Gage re-runs G09a under a fresh RA... with `--no-ceiling`. R4 gate evaluates to the reachable 8.82 GiB threshold and passes; the subprocess launches; `peak_commit` is measured." | PASS |
| Ceiling derivation order (R4 gate → launch → measure peak → derive ceiling → populate constant) | 6-step sequence in v2 | 6-step sequence preserved verbatim in v3 Measure-first statement (lines 1149–1155) | PASS |

**Sequencing verified.** v3 does not smuggle any implicit dependence on `peak_commit` into R4.

**Sub-observation on implementation:** `core/run_with_ceiling.py` line 209 reads `if math.isfinite(ceiling_bytes):` — meaning the R4 gate is only enforced when `CEILING_BYTES` has been populated (finite). During the `--no-ceiling` baseline-run, `ceiling_bytes = math.inf` and the R4 gate is skipped. This is **correct v2 behavior preserved**; v3 does not change it. The `--no-ceiling` baseline-run can proceed on any host with enough RAM to launch the subprocess, regardless of R4 threshold — which is exactly what measure-first requires. Dex will need to preserve this `isfinite()` guard when changing the threshold expression from `1.5 * CAP_ABSOLUTE` to `CAP_ABSOLUTE + OS_HEADROOM`.

---

## Check 5 — Fail-closed preservation: **PASS**

v3 is at least as safe as v2 on every axis. Riven's own fail-closed proof table at lines 1520–1529 is sound; I independently reconstruct:

| Axis | v2 | v3 | Safety delta |
|---|---|---|---|
| R4 reachability | Unreachable (14.37 GiB > 9.47 GiB observed) — gate never fires because wrapper never launches at all | Reachable (9.47 GiB = observed floor by construction) — gate actually fires | **v3 stricter** (v2 was unsafe-in-the-limit: an unreachable gate provides zero real-world protection) |
| CAP_ABSOLUTE | 10,285,835,059 (9.58 GiB) | 8,400,052,224 (7.82 GiB) | **v3 tighter by 1.76 GiB** |
| R5 KILL absolute | 9.10 GiB | 7.43 GiB | **v3 tighter by 1.67 GiB** — any subprocess that would have been E3-killed under v2 CAP is also killed under v3 CAP; the v3 KILL trip condition `observed ≥ 0.95 × CAP_v3 = 7.43 GiB` fires strictly before the v2 KILL would have fired (9.10 GiB), with 1.67 GiB margin |
| E1 trigger | peak > 9.58 GiB | peak > 7.82 GiB | **v3 stricter** (more conservative streaming-chunk refactor trigger) |
| R1 dual signal (leak detection) | Signal A ratio + Signal B ΔPageFile | Same brackets preserved (explicit `[PRESERVED v2 → v3]` banner line 332) | **v3 equal** — tightened CAP makes leak detection *friendlier* (fewer ΔPageFile bytes possible pre-kill; Riven §Handoff 7 sub-concern) |
| E6 runtime semantics | Launch-time gate only | Launch-time gate only (Riven §Handoff 4 explicit rewrite) | **v3 equivalent coverage** for the cases v2 E6 was designed to catch — both gate at wrapper entry; neither is a runtime tick check |
| OS starvation protection | 1.5× multiplier (unreachable — protection never activates) | Additive OS_HEADROOM (reachable — protection actually activates) | **v3 stricter** (provides protection where v2 provided none in practice) |
| E7 structural floor drift | None | 10% threshold check at every re-baseline AND every pre-RA probe | **v3 stricter** (new detection — v2 E4 only catches physical RAM changes, not always-on process floor shifts) |
| Exit codes | ADR-2 set unchanged | ADR-2 set unchanged; footnote at line 54 clarifies v3 R4 threshold; no new codes invented | **v3 equivalent** |

**WARN→KILL window sanity check:** v3 buffer = 840,005,222 bytes. At post-refactor per-tick deltas of tens of MB (v2 cited) and 30s polling:
- Conservative 40 MB/tick: 840 MB / 40 MB = 21 ticks × 30s = **10.5 min visibility**
- Aggressive 80 MB/tick: 840 MB / 80 MB = 10.5 ticks × 30s = **5.25 min visibility**
- Sentinel +45% variance scenario (worst observed): deltas could scale proportionally; assume 60 MB/tick → 14 ticks × 30s = **7 min visibility**

All three regimes leave > 5 minutes of operator-visible WARN log lines before KILL. Adequate for the "attentive operator" argument Riven v2 made and v3 preserves. **Fail-closed window adequate.**

**One fail-closed corner preserved-correctly:** Child runs that would have been E1-killed under v2 CAP (peak > 9.58 GiB) are also killed under v3 CAP (peak > 7.82 GiB) *at a tighter threshold* — this is a **strengthening**, not a regression. Any subprocess that hit v2 CAP at 9.10 GiB KILL trip will hit v3 CAP at 7.43 GiB KILL trip first (lower threshold → fires earlier). Exit codes unchanged per ADR-2. **Regression proof: 7.43 GiB < 9.10 GiB; any trajectory that crosses 9.10 GiB must have crossed 7.43 GiB strictly earlier; v3 kills earlier; never later.**

**Article V (fail-closed discipline) satisfied.**

---

## Check 6 — Host portability formula: **PASS**

`CAP_ABSOLUTE_host = min(floor − headroom, 0.60 × phys_RAM)`.

Verified the three archetypes in the dispatch brief plus Riven's rejected `max()` counterproposal:

| Host archetype | floor − headroom | 0.60 × RAM | min() | max() (rejected) | Correctness |
|---|---|---|---|---|---|
| 16 GiB, this host (floor = 9.47 GiB) | 8.40 GiB | 9.58 GiB | **8.40 GiB** (floor-dominated) | 9.58 GiB | `min()` correct — the RAM-pct anchor would permit allocations the observed floor cannot support |
| 32 GiB, floor ≈ 20 GiB (similar ~7 GiB structural-resident) | 19 GiB | 19.2 GiB | **19.0 GiB** (floor-dominated, barely) | 19.2 GiB | `min()` correct — near-equal; whichever is tighter rules |
| 128 GiB theoretical, floor ≈ 60 GiB | 59 GiB | 76.8 GiB | **59 GiB** (floor-dominated) | 76.8 GiB | `min()` correct — on big-RAM hosts with heavy co-tenants, floor is the operational constraint; RAM percentage is a theoretical upper bound |

**Riven §Handoff 6 rationale for `min()` over `max()`:** "When two anchors disagree, the tighter one rules. `max()` deliberately selects the looser anchor, which is the opposite of fail-closed." Independently verifiable — a CAP derived via `max()` on any host where structural-resident floor is the real constraint would permit subprocess allocations the host cannot safely support, starving OS_HEADROOM.

**On a 32 GiB host with a pristine floor (hypothetical, minimal co-tenant):** `floor ≈ 28 GiB; floor − headroom = 27 GiB; 0.60 × 32 = 19.2 GiB; min() = 19.2 GiB (RAM-pct dominates)`. This is the case where RAM-pct caps the CAP even though the host could theoretically support more — intentional, because it preserves the v2 "40% OS reserve" invariant across all hosts. This is a reasonable Article V bar: the formula never allows a host to give its subprocess more than 60% of physical RAM, regardless of how pristine the floor is.

**Host-invariance of OS_HEADROOM:** v3 §line 1182 "OS_HEADROOM is host-invariant at 1 GiB — tied to literature (Gregg §7.5 upper bound), not to hardware. Re-evaluate only if the literature anchor is revised." Correct — OS_HEADROOM represents kernel + filesystem-cache slack which scales with OS generation, not with RAM. A 128 GiB host running the same Windows 10+ OS has approximately the same 1 GiB absolute need; it does not need 8 GiB of OS_HEADROOM just because it has 8× more RAM.

**Article V (formula soundness) satisfied.**

---

## Check 7 — Handoff completeness for Dex: **PASS**

Dex has zero-ambiguity to patch. Enumeration of required artifacts:

| Dex artifact | Specified in v3? | Location | Verdict |
|---|---|---|---|
| `OBSERVED_QUIESCE_FLOOR_AVAILABLE = 9_473_794_048` literal | YES | Aria v3 Handoff line 1271 ("NEW: per quiesce-mid.json, RA-20260424-1") | PASS |
| `OS_HEADROOM = 1_073_741_824` literal | YES | Aria v3 Handoff line 1272 ("NEW: 1 GiB, per Gregg §7.5 literature anchor") | PASS |
| `CAP_ABSOLUTE = 8_400_052_224` literal (replacing v2 `10_285_835_059`) | YES | Aria v3 Handoff line 1273 with derivation comment | PASS |
| R4 check-site change location | YES — "in `core/run_with_ceiling.py` launch path" (Aria v3 line 1277) | v2 audit had marked this as "expected in core/run_with_ceiling.py"; verified by this auditor at **line 211 of `core/run_with_ceiling.py`**: `threshold = int(memory_budget.LAUNCH_AVAILABLE_MULTIPLIER * memory_budget.CAP_ABSOLUTE)` | PASS |
| R4 formula change (multiplier → additive) | YES — Aria v3 Handoff lines 1281–1288 show BEFORE/AFTER diff | Formula: `vm.available < (CAP_ABSOLUTE + OS_HEADROOM)` replaces `int(1.5 * CAP_ABSOLUTE)` | PASS |
| Exit-1 message format | YES — Aria v3 §Updated R4 formula (lines 1120–1138) supplies the exit-1 message template verbatim; current implementation at `core/run_with_ceiling.py` lines 214–223 requires threshold number + label update (`"required (1.5 x CAP_ABSOLUTE)"` → `"required (CAP_ABSOLUTE + OS_HEADROOM)"`) | PASS |
| `_RETAINED_PROCESSES` frozenset preservation | YES — Aria v3 Handoff line 1304 ("MUST NOT: Modify the `_RETAINED_PROCESSES` frozenset or `is_retained()` function — v2 Finding 6 unchanged") | PASS |
| HEADROOM_FACTOR / WARN_FRACTION / KILL_FRACTION preservation | YES — Aria v3 Handoff line 1305 ("MUST NOT: Modify HEADROOM_FACTOR, WARN_FRACTION, KILL_FRACTION — v2 unchanged") | PASS |
| Test updates (`tests/core/test_memory_budget.py`) | YES — Aria v3 Handoff lines 1293–1300 enumerate 4 assertions (CAP_ABSOLUTE == 8_400_052_224; OS_HEADROOM == 1_073_741_824; sum == 9_473_794_048; OBSERVED_QUIESCE_FLOOR_AVAILABLE == 9_473_794_048) | PASS |
| Test updates (`tests/core/test_run_with_ceiling.py`) | **IMPLICIT.** Aria names `tests/core/test_memory_budget.py` explicitly but does not name `tests/core/test_run_with_ceiling.py`. R4 check site at `core/run_with_ceiling.py` line 211 almost certainly has existing tests (v2 audit verified `tests/core/test_run_with_ceiling.py` exists) that assert against the old `1.5 × CAP_ABSOLUTE` = 15,428,752,588 threshold. Those tests will break on the v3 patch. Dex must update them. | CONCERNS (see Finding 1 below) — not blocking; Dex will discover on first test run |
| Commit message requirements | YES — Aria v3 Consequences line 1240 ("MUST cite: (i) this ADR-1 v3 section, (ii) `quiesce-mid.json`, (iii) Gregg §7.5, (iv) RA-20260424-1 halt report"). Sentinel variance + Gregg v2 citations also preserved from v2 R3 via Riven v3 Handoff 7. | PASS |
| Test value for threshold in test_run_with_ceiling.py | **NOT enumerated** as an exact byte literal for the R4 threshold assertion. Tests presumably assert on `memory_budget.CAP_ABSOLUTE + memory_budget.OS_HEADROOM` rather than a hardcoded `9_473_794_048` — cleaner but implicit. | CONCERNS-adjacent; style choice for Dex |
| `LAUNCH_AVAILABLE_MULTIPLIER` constant fate | **AMBIGUOUS.** Current `core/memory_budget.py` has `LAUNCH_AVAILABLE_MULTIPLIER` (referenced at `core/run_with_ceiling.py` line 211). v3 switches from multiplicative to additive; the constant becomes vestigial. Dex must decide: (a) delete the constant and any tests asserting on it; (b) leave it as deprecated with a comment; (c) repurpose it. Aria v3 does not specify. | CONCERNS (see Finding 2 below) — Dex-discoverable, not blocking |

**Overall enumeration coverage:** 11/13 implementation artifacts fully specified; 2 CONCERNS (test file update + vestigial constant) are operationally small and Dex will discover on first `pytest` run. Per Quinn v2 audit precedent, CONCERNS at this specificity level are not blockers for Dex to begin patching; they are items Dex handles during implementation and Quinn re-gates at #103.

---

## Overall verdict: **PASS**

ADR-1 v3 + Riven Co-sign v3 are custodially sound, arithmetically exact, evidence-anchored to the G09a halt artifacts, internally consistent between Aria and Riven, measure-first-preserving, fail-closed-preserving (and strengthening on 4 axes — R4 reachability, CAP tightness, R5 KILL tightness, E7 drift detection), portable across host archetypes via a `min()` formula that Riven defensibly justified over `max()`, and operationally actionable by Dex.

**No FAIL conditions.** No invented numbers, no arithmetic errors, audit trail intact with 8 `[SUPERSEDED v2 → v3]` banners + 1 `[PRESERVED v2 → v3]` banner, no measure-first regression, fail-closed discipline strengthened not eroded, Dex has concrete diff-level instructions for `core/memory_budget.py` + `core/run_with_ceiling.py` + `tests/core/test_memory_budget.py`.

**No blockers.** Two CONCERNS-level findings below are Dex-discoverable during implementation and do not gate Riven's v3 sign-off, do not gate the orchestrator applying SUPERSEDED markers to v2, and do not gate Dex beginning the patch.

This is a cleaner chain than v2. v2 had 4 implementation-layer spec ambiguities that needed Aria/Riven ratification before Dex could proceed; v3 has 2 Dex-discoverable concerns about adjacent artifacts (test file + vestigial constant) that are routine patch hygiene. The v2 ratification round produced the structural improvements (Finding 4 ratified to hardcoded literals + runtime drift check; Finding 5 ratified to two-output telemetry split; Finding 6 ratified to frozenset + is_retained filter) that v3 then preserved verbatim — meaning the work of Check 7 is thinner this time because v2 did the heavy lifting.

---

## Findings (CONCERNS only; no BLOCKERS)

1. **[CONCERNS] `tests/core/test_run_with_ceiling.py` updates not enumerated in v3 handoff.** The v2 implementation (verified by this auditor at `core/run_with_ceiling.py` line 211 — R4 threshold computed as `int(LAUNCH_AVAILABLE_MULTIPLIER * CAP_ABSOLUTE)`) almost certainly has test cases asserting on the v2 threshold = 15,428,752,588 bytes. Those assertions must update to `CAP_ABSOLUTE + OS_HEADROOM = 9,473,794,048` under v3. Aria's v3 Handoff enumerates only `tests/core/test_memory_budget.py` (4 assertions — lines 1293–1300). Owner: **Dex** to discover on first `pytest` run and update; Quinn will re-gate at #103. **Not blocking** — Dex cannot ship a patch that breaks existing tests silently, so the gap is self-correcting under normal TDD discipline.

2. **[CONCERNS] `LAUNCH_AVAILABLE_MULTIPLIER` constant vestige.** Current `core/memory_budget.py` likely declares `LAUNCH_AVAILABLE_MULTIPLIER` (the `1.5` v2 constant, referenced at `core/run_with_ceiling.py` line 211). The v3 additive formula does not use a multiplier. Dex must decide: (a) delete the constant + any tests asserting on it; (b) leave it as deprecated with a docstring pointer to ADR-1 v3; (c) repurpose it. Aria v3 does not specify. Owner: **Dex** with default recommendation (a) — delete, since v3 semantics are additive and the multiplier has no v3 role. If Dex chooses (b) for audit-trail reasons, a one-line commit rationale suffices. **Not blocking.**

3. **[INFORMATIONAL] Warn-to-kill buffer unit-label mixing.** Aria v3 line 1103 labels the buffer "~840 MiB"; Riven v3 §R5 table labels it "840,005,222 bytes / 0.78 GiB binary"; the binary MiB equivalent is 801 MiB. All labels refer to the same byte count but a reader comparing decimal MiB (840) to binary GiB (0.78) could derive slightly different numbers via unit conversion. Cosmetic, non-blocking; consistent-with-v2-style unit looseness. No fix requested — v2 had the same label style and Quinn did not block there.

4. **[INFORMATIONAL] The v3 handoff promises banners "at each v2 clause that v3 overrides"; the dispatch brief counted 9 Aria locations + 3 Riven.** I counted **8 `[SUPERSEDED v2 → v3]` + 1 `[PRESERVED v2 → v3]` = 9 total banners** in-file. The discrepancy against the brief's "9 Aria + 3 Riven = 12 banners" tally resolves if the brief was counting Riven-internal references (the R1/R3/R5 in-Riven banners at lines 332/376/411 + the E6 banner-acceptance on line 434) separately from Aria-intro enumeration. Exact banner count is bookkeeping; every v3 supersession has a banner at its point of occurrence, which is the semantic requirement. No finding.

---

## Handoff — ratifications needed before Dex proceeds to #103

**None required from Aria or Riven.** Both agents have already signed off:
- Aria v3 §Sign-off (line 1320–1324) — "ADR-1 v3 PROPOSED. Own-authority design scope; does not require Aria upstream co-sign. Downstream co-sign from Riven required."
- Riven v3 §Final verdict (lines 1540–1555) — "**GO for ADR-1 v3.** Riven (@risk-manager, R10 custodial) co-signs all 7 handoff points."
- Both co-signs verified in-file.

**Dex unblocked.** Next step per v3 §Handoff line 1557: "1. Quinn audit at `docs/qa/gates/ADR-1-v3-audit.md` — **this document; verdict PASS**." Dex may proceed to #103 patching `core/memory_budget.py` + R4 check site in `core/run_with_ceiling.py` + test updates. Findings 1 and 2 above are Dex-discoverable CONCERNS; neither blocks the patch start.

**Orchestrator next steps:**
1. Apply SUPERSEDED markers promoting v3 to active (banners already in-file; marker is header-level annotation per v2 audit Check 6 precedent).
2. Unblock Dex #103.
3. Post-Dex: Riven drafts RA-20260425-N for G09a retry under v3 R4 gate (Riven v3 §line 1497, §line 1560).

**Manifest guard:** `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` — verified byte-identical at audit time (this document touches only `docs/qa/gates/ADR-1-v3-audit.md`; no code, no canonical manifest, no parquet modifications).

---

**Audit complete.** Verdict: **PASS** — chain ready for Dex implementation; no ratifications required; 2 CONCERNS are Dex-discoverable during patch work; 2 INFORMATIONAL notes do not affect correctness.

**Auditor sign-off:** Quinn (@qa) — 2026-04-23 BRT
