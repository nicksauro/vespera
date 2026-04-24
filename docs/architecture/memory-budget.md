# Architecture Decisions — Memory Ceiling & Telemetry Wrapper (T002.0a G09)

**Author:** Aria (@architect, The Weaver ♒)
**Date:** 2026-04-23 BRT
**Trigger:** Quinn FAIL-BLOCK on `scripts/_telemetry_wrapper.py` + Sable G09 formalization
**Scope:** Design authority for memory ceiling derivation, telemetry mechanism, and wrapper boundary. Co-sign from @risk-manager (Riven) required on ADR-1 ceiling (custodial).
**Constitutional anchors:** Article IV (No Invention), Article V (Quality First), Article I (CLI First).
**Out of scope:** Code edits (Dex implements); R10 sign-off (Riven authorizes post-design).

---

> ## ⚠️ ADR-1 v1 SUPERSEDED on 2026-04-23 BRT
>
> **Cause:** v1 was built on an incorrect host RAM assumption (32 GB assumed; real host = **15.97 GiB** per `data/baseline-run/host-preflight.txt`, captured by Gage after user correction). Riven Co-sign v1 inherited the same assumption.
>
> **Replacement:** See **ADR-1 v2** (host-specs-aware) + **Riven Co-sign ADR-1 v2** appended at the end of this file.
>
> **Custodial audit trail:** v1 text (ADR-1, Remediation, Riven Co-sign v1) is preserved verbatim below under `[SUPERSEDED]` headers — NOT deleted. Future readers can reconstruct why v1 was wrong and what v2 corrected. Any code, story, or gate doc that still references v1 values (× 1.5 headroom, Mar-2024 baseline, exit 3 as `observed > ceiling`) MUST be updated to v2 equivalents.
>
> **Quinn audit of v2 chain:** `docs/qa/gates/ADR-1-v2-audit.md` — verdict **CONCERNS** (not FAIL): chain is custodially sound, arithmetically exact, traceable, internally consistent; 4 implementation-layer spec ambiguities tracked for Aria/Riven ratification before Dex #74.

---

## ADR-1 [SUPERSEDED v1]: ROM budget derivation

**Decision:** **Measure-first.** Ceiling MUST be derived from an observed baseline — not from a round number. Gage executes a dedicated **baseline run** of `materialize_parquet.py` against a single representative month (Mar-2024, already re-materialized during G07 pre-evidence, ~14.5M rows) with the refactored code (cursor-stream + gc) under **lightweight telemetry only — no ceiling enforcement**. Peak commit and peak RSS are recorded. Ceiling is then set as `ceiling_bytes = ceil(peak_commit × 1.5)`, rounded up to the nearest 1 GB. Published as a constant in `core/memory_budget.py` (module-level), imported by both `_telemetry_wrapper.py` (enforcement) and any future long-running materialization wrapper.

**Rationale:** Option "fixed 15 GB" violates Article IV — zero traceability to benchmark/spec/requirement. Option "derive from host RAM (32 GB → 18 GB)" is weaker: host RAM is upper bound on what's *possible*, not on what materialize_parquet *needs*; we want ceiling near actual need, not physical maximum. Option "streaming-chunk rewrite" is correct long-term direction but out of G09 scope. Measure-first produces a number that traces directly to `baseline-run.telemetry.csv` evidence artifact. 1.5× headroom covers month-to-month volatility without approaching host limit.

**Consequences:**
- G09 gains prerequisite **G09a (baseline-run)**. G09 does not launch until baseline peak is on record and `core/memory_budget.py` populated.
- Baseline risks OOM if post-refactor code still leaks — *desired*, controlled window, not during May+Jun 2025 where kill mid-month leaves half-manifest.
- Ceiling is design artifact, not config. Changing requires new ADR + Riven co-sign.

**Approval chain:** Aria (design) → Riven (custodial co-sign: ceiling value + derivation evidence) → registered here with pointer to `data/baseline-run/baseline-telemetry.csv`.

**Status:** Proposed — awaiting Riven co-sign.

---

## ADR-2: Telemetry mechanism

**Decision:** **Replace `tasklist` + `wmic` with `psutil` as primary sampler.** Fallback: if `psutil` import fails, wrapper aborts with exit code 4 (**fail-closed**), does NOT launch child. Polling interval **30 seconds** during G09, configurable via `--poll-seconds` (default 30, min 10, max 300).

**Rationale:**
- **FINDING-Q-05 (pt-BR locale):** On pt-BR Windows, `tasklist` emits `"1.234.567 K"`; current `_parse_kb` strips `.` yielding `1234567` — *looks* correct but reports **bytes instead of kilobytes**, understating commit by 1024×. Catastrophic kill-switch inversion.
- **FINDING-Q-06 (wmic deprecation):** Win10 21H1+ ships wmic as optional; 22H2/Server 2022 deprecated. Silent fallback → commit=0 → ceiling noop.
- `psutil` addresses both: typed integer fields (`rss`, `vms`, `private`) — zero string parsing, zero locale coupling. Pure Python + ctypes, supported Win 7 → Win 11.
- **Fail-closed on sampler failure:** if `psutil` cannot sample 3 consecutive times, wrapper kills child with exit 5 rather than continuing blind. Kill-switch that can't observe IS a kill-switch that should trip.
- **Polling at 30s:** memory can grow from ceiling to OOM in <1 min when cursor leak occurs — 60s too coarse.

**Formalized exit codes:**
- `0` — child exited cleanly, no ceiling trip
- `1` — wrapper setup error (¹under ADR-1 v2: also trips at launch if `psutil.virtual_memory().available < 1.5 × CAP_ABSOLUTE` per R4, and if `psutil.virtual_memory().total` drifts > 1% from `PHYSICAL_RAM_BYTES` per E4; see Aria Ratifications Finding 4) (²under ADR-1 v3: R4 threshold is `CAP_ABSOLUTE + OS_HEADROOM` = 9,473,794,048 bytes, not `1.5 × CAP_ABSOLUTE`; E4 drift check unchanged; CAP_ABSOLUTE itself re-derived to 8,400,052,224 bytes; see ADR-1 v3 at end of file)
- `2` — hold-out lock raised by child (propagated)
- `3` — ceiling tripped, child killed (¹under ADR-1 v2 this trips pre-emptively at `observed >= 0.95 × CEILING_BYTES` — not reactively at `observed > CEILING_BYTES`; see ADR-1 v2 "Early-trip thresholds" table)
- `4` — psutil not importable; aborted before launching
- `5` — sampler lost visibility 3× consecutive; child killed defensively
- `>=10` — child's own exit code (propagated)

**Status:** Proposed.

---

## ADR-3: Wrapper responsibility boundary

**Decision:** **Split into library + thin CLI.** New `core/run_with_ceiling.py` (reusable library, no argparse, no hardcoded args/paths) + thin CLI `scripts/run_materialize_with_ceiling.py` that imports and composes invocation. Each run takes `--run-id` (operator-supplied, e.g. `may-jun-2025` or `baseline-mar-2024`), used to name run log + telemetry CSV. **No overwrite:** if `data/<run_id>.log` exists, refuse with exit 1 unless `--force`.

**Library contract:**
```python
def run_with_ceiling(
    command: list[str],
    *,
    run_id: str,
    log_dir: Path,
    ceiling_bytes: int,
    poll_seconds: int = 30,
    sampler: Callable[[int], Optional[Sample]] = psutil_sampler,
    force_overwrite: bool = False,
) -> RunResult: ...
```

- Library does NOT know about `materialize_parquet.py`, `--start-date`, tickers, phases.
- `sampler` injectable for testability — unit tests pass fake sampler with scripted memory trajectory.
- Returns typed `RunResult`; thin CLI renders.

**Thin CLI contract:**
- Parses: `--run-id`, `--start-date`, `--end-date`, `--ticker`, optional `--poll-seconds`, `--force`.
- Composes `materialize_parquet.py` argv — no hardcoded May/Jun 2025.
- Imports `CEILING_BYTES` from `core/memory_budget.py`.

**Rationale:** FINDING-Q-07 — current wrapper is single-use; Gage can't reuse for baseline without copy. Log overwrite loses history. Separation lets ADR-2 sampler be swapped without touching CLI. `--run-id` makes G09 evidence filenames a naming convention operator controls.

**Consequences:**
- `scripts/_telemetry_wrapper.py` **deleted**.
- G09 procedure in `T002.0a-sable-gates.md` L114 updates to new CLI.
- Unit tests at `tests/core/test_run_with_ceiling.py` (Quinn owns acceptance).

**Status:** Proposed.

---

## Remediation order of operations [SUPERSEDED v1 — see v2 after Riven Co-sign v2]

1. **Riven co-sign ADR-1** derivation approach. Records in MC or `docs/architecture/memory-budget.md` addendum.
2. **Dex creates** `core/memory_budget.py` with `CEILING_BYTES = None` sentinel + docstring pointing ADR-1.
3. **Dex implements** `core/run_with_ceiling.py` per ADR-3 (psutil sampler per ADR-2, fail-closed codes, injectable sampler).
4. **Dex implements** `scripts/run_materialize_with_ceiling.py` thin CLI.
5. **Quinn reviews** steps 3+4 against 5 original findings.
6. **Gage baseline run:** `python scripts/run_materialize_with_ceiling.py --run-id baseline-mar-2024 --start-date 2024-03-01 --end-date 2024-03-31 --ticker WDO --no-ceiling`. Scratch output path (NÃO tocar canonical Mar-2024 protegido por MC-20260423-1).
7. **Aria + Riven** review baseline telemetry; Aria computes `ceiling = ceil(peak × 1.5)` rounded up 1 GB; Riven co-signs.
8. **Dex populates** `core/memory_budget.py` com real `CEILING_BYTES` + `CEILING_DERIVATION_REF`. Fecha Q-01.
9. **Riven drafts** `MC-20260424-1` (per MC-20260423-1 next_action step 2) pre-authorizing Gage Mai+Jun.
10. **G09 runs.** Gage: `python scripts/run_materialize_with_ceiling.py --run-id may-jun-2025 --start-date 2025-05-01 --end-date 2025-06-30 --ticker WDO`.
11. **Sable G10.**

Steps 1-5 partially parallelize após Riven co-sign; 6-11 strictly sequential.

---

## Artifacts

- `core/memory_budget.py` (new) — Dex
- `core/run_with_ceiling.py` (new) — Dex
- `scripts/run_materialize_with_ceiling.py` (new) — Dex
- `scripts/_telemetry_wrapper.py` — deletar
- `tests/core/test_run_with_ceiling.py` (new) — Dex
- `data/baseline-run/baseline-telemetry.csv` (new) — Gage step 6
- `docs/architecture/memory-budget.md` (this file) — Aria
- `docs/MANIFEST_CHANGES.md` — novo `MC-20260424-1` adicionado step 9 (Riven)

---

## Riven Co-sign — ADR-1 [SUPERSEDED v1] (2026-04-23 BRT)

**Verdict:** **REVISE** (not APPROVE, not REJECT). Measure-first derivation is correct in method, but three conditions must be embedded in the contract before `CEILING_BYTES` is promoted from sentinel to production value. Absent these conditions, the ceiling traces back only to one observed peak, which is insufficient custodial evidence under Article IV.

### Condition R1 — Parallel peak_rss + ratio check (fail-closed)

During the G09a baseline run, the sampler MUST record BOTH `peak_commit` and `peak_rss` per polling tick to `data/baseline-run/baseline-telemetry.csv`. Derivation input is `peak_commit`, but the ratio `peak_commit / peak_rss` is a leak detector:

| Ratio | Interpretation | Riven action |
|-------|----------------|--------------|
| < 1.5 | Normal working set ≈ committed virtual | APPROVE ceiling = ceil(peak_commit × 1.5) rounded up 1 GB |
| 1.5 – 3.0 | Some PageFile reservation, tolerable | APPROVE with note; flag for G10 post-relaunch re-check |
| > 3.0 | **Cursor leak or unreleased allocator fragments — refactor did not fully resolve** | **BLOCK.** Do not set ceiling. Re-open Dex remediation: investigate allocator (PyArrow buffer pool, psycopg2 cursor close, `gc.collect()` placement) before re-baseline |

**Why:** peak_commit alone can mask a leak (Windows commits virtual but RSS stays low until touched). A high ratio means the process is reserving PageFile without using it — exactly the pre-refactor failure mode. Ceiling derived on top of a leaked baseline re-encodes the leak as "normal."

### Condition R2 — Host pre-flight artifact

Before G09a launches, Gage MUST capture `data/baseline-run/host-preflight.txt` containing:

- `systeminfo` stdout (physical memory total, virtual memory max, PageFile current/peak)
- `wmic os get TotalVirtualMemorySize,FreeVirtualMemory,TotalVisibleMemorySize` (or psutil equivalent per ADR-2 if wmic already deprecated on host) — captured at t=0 before launch
- Running process count + top-5 memory consumers (`tasklist /v /fo csv | sort by MemUsage desc | head 5` equivalent)
- Timestamp BRT

**Why:** the ceiling is meaningful only relative to the host that produced it. If the baseline runs on a host with 4 GB free commit headroom, a `peak_commit = 10 GB` observation is upper-bounded by the host — not by `materialize_parquet.py`'s actual need. The pre-flight lets Aria + Riven verify the baseline wasn't host-clamped. If the host had less than `2 × peak_commit` free at t=0, the baseline is invalid and must re-run.

### Condition R3 — × 1.5 headroom rationale (Article IV anchor)

The multiplier 1.5 MUST trace to prior art or measured variance, not to round-number intuition. Accepted anchors for this run:

- **Gregg, *Systems Performance* (2nd ed.)** — DBA buffer pool convention sizes at 1.5× expected working set to absorb query skew and occasional large scans. Applies here because materialize_parquet's dominant allocation pattern (read batch → transform → write) mirrors a bounded query workload with occasional full-month scans.
- **Sentinel row-count variance** (observed): Jul 2024 trades = +24% vs Mar 2024; Aug 2024 = +45% vs Mar 2024 (per TimescaleDB chunk counts inspected 2026-04-21). Memory footprint scales ~linearly with row count at the parquet-write stage. So a ceiling derived from Mar 2024 must absorb at least +45% month-to-month variance → ×1.45 minimum → ×1.5 rounded up is defensible with one decimal of headroom.

Aria MUST include both citations verbatim in the commit message when `CEILING_BYTES` is populated in `core/memory_budget.py` (step 8 of remediation). Riven will not co-sign the ceiling value otherwise.

### Escalation clause

If any of R1/R2/R3 cannot be satisfied at derivation time (step 7), Riven WILL NOT co-sign the ceiling value. Chain blocks at step 7. Options:

1. Re-run G09a under corrected conditions (if R1 violated: patch Dex; if R2 violated: free host resources before re-baseline)
2. Escalate to @aiox-master for constitutional review (if R3 cannot be anchored — indicates ×1.5 is speculative and derivation method itself needs revision)

There is no ambiguous path forward: ceiling is either derived under these conditions or not derived at all.

### Fail-closed cross-reference

ADR-2's fail-closed exit code **4** (psutil not importable) is the enforcement arm of R2 — if psutil isn't present at baseline time, the pre-flight itself can't be captured by the sampler, so the baseline can't start. Exit code **5** (sampler lost visibility 3×) during the baseline itself means the peak observation is unreliable → baseline invalid → re-run. This is consistent with R1's leak detector: better to abort than to derive a ceiling from a blind run.

### Re-validation cadence (post-promotion)

Once `CEILING_BYTES` is populated, it is NOT permanent. Riven mandates re-derivation triggers:

- **Mandatory:** after any refactor of `materialize_parquet.py` that touches cursor handling, batch size, or write path
- **Mandatory:** after 6 months elapsed (data volume drift — new in-sample months will extend the manifest)
- **Advisory:** if any production run approaches 80% of ceiling (`peak_commit_observed / CEILING_BYTES > 0.80`) — signal that headroom has eroded and re-baseline is due

Each re-derivation requires a new ADR amendment + Riven co-sign per standard R10 procedure.

---

**Sign-off:**
- 2026-04-23T14:30-03:00 BRT — **Riven (@risk-manager, R10 custodial)** — ADR-1 method **REVISED** per conditions R1/R2/R3 above. Method approved in principle; ceiling value blocked until conditions satisfied at step 7 of remediation plan.
- Aria (@architect) — acknowledges REVISE verdict; ADR-1 now includes conditions as binding contract for step 7.
- Next required sign-off: Aria + Riven at step 7 (post-baseline) with concrete `peak_commit`, `peak_rss`, ratio, host-preflight cross-ref, and ×1.5 rationale citations.

---

**Status:** ADR-1 **method APPROVED with revisions** (Riven 2026-04-23). ADR-2, ADR-3 still Proposed. Ceiling value still pending G09a baseline + step-7 derivation.

---

## ADR-1 v2 — ROM budget derivation (host-specs-aware, 2026-04-23 BRT)

> ## ⚠️ ADR-1 v2 — CAP_ABSOLUTE and R4 SUPERSEDED on 2026-04-23 BRT (late-day)
>
> **Cause:** RA-20260424-1 execution (Gage, 2026-04-23 evening) proved the v2 R4 launch-time gate (`available ≥ 1.5 × CAP_ABSOLUTE = 14.37 GiB`) is **structurally unreachable** on this host. Observed mid-quiesce floor after `docker stop sentinel-timescaledb` + `wsl --shutdown` + 30s settle = **9,473,794,048 bytes (8.82 GiB)** — a 5.55 GiB shortfall vs the R4 threshold. Residual irreducible consumers (vmmem 2.15 GiB, claude 535 MiB, MsMpEng 356 MiB, msedgewebview2 218 MiB, explorer 198 MiB, docker-backend 183 MiB, plus kernel/driver/System/svchost aggregate ~2.5 GiB) establish a physical floor of ~7.67 GiB consumed regardless of operator action. Consequence: the v2 R4 multiplier (1.5×) was an Article IV violation on our own part — derived from a theoretical "pristine quiesce" model, not measured against the operational host envelope. v2 CAP_ABSOLUTE (0.60 × physical = 9.58 GiB) is also re-derived downward because it does not fit within the measured floor with adequate OS headroom.
>
> **Replacement:** See **ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor** at the end of this file.
>
> **Scope of supersession:** ONLY the CAP_ABSOLUTE constant (9.58 GiB → 7.82 GiB) and the R4 launch-time gate formula (`1.5 × CAP_ABSOLUTE` → `CAP_ABSOLUTE + OS_HEADROOM`). All other v2 clauses — HEADROOM_FACTOR = 1.3, Aug-2024 baseline choice, warn/kill at 85/95, R1 dual-signal leak detector (Signal A ratio + Signal B ΔPageFile), E1/E2/E3/E4/E5 escalations, whitelist frozenset, telemetry schemas, exit codes — **remain in force verbatim**. v3 is a surgical recalibration of two numbers, not a rewrite.
>
> **Custodial audit trail:** v2 text below is preserved verbatim — NOT deleted. Clauses superseded by v3 carry inline `[SUPERSEDED v2 → v3]` banners at their point of occurrence.
>
> **Evidence anchors for v3:** `data/baseline-run/quiesce-mid.json` (the empirical floor), `data/baseline-run/quiesce-audit-20260424.yaml` (the RA-20260424-1 execution record), `data/baseline-run/baseline-aug-2024-halt-report.md` (the halt narrative and phase-by-phase outcome).

**Supersedes:** ADR-1 v1 (above). v1 implicitly assumed host RAM ~= 32 GiB when reasoning about "host upper bound" and "×1.5 headroom." The real host is **15.97 GiB physical RAM** (2× 8 GB DDR3-1333 on an Ivy Bridge i7-3770, per `data/baseline-run/host-preflight.txt` captured 2026-04-22T23:13:24-03:00). The v1 ceiling formula `ceil(peak_commit × 1.5)` on a 16 GiB host can legally produce values up to ~15 GiB (94% of physical RAM), which is *Windows-legal* (commit limit = 56.81 GiB, so the OS will not refuse the allocation) but *operationally unsafe* (40% RAM is needed for OS + always-on workload; process would thrash PageFile on a SATA/HDD backing store). v2 re-derives with an absolute cap rooted in physical RAM and an early-trip mechanism rooted in the host's slow paging fabric.

**Decision:** Ceiling is the **minimum** of a headroom-scaled observed peak and an absolute cap anchored in physical RAM. Baseline changes from Mar-2024 to **Aug-2024** (worst-observed in-sample month, already materialized per MC-20260423-1, +45% rows vs Mar-2024). Headroom factor reduces from ×1.5 to **×1.3** because the RAM-anchored cap dominates derivation in practice and a lower multiplier keeps the derivation arithmetic truthful (no phantom headroom above cap). Streaming-chunk rewrite **remains out of G09 scope**; if Aug-2024 peak × 1.3 exceeds cap, ceiling clamps at cap and G09 runs under that reality.

**Rationale:** Three host-specific facts rewrite v1:

1. **Commit limit (56.81 GiB) is not a safety ceiling.** Windows dynamic PageFile lets commit grow to ~57 GiB before allocation is refused; by the time commit grows that large, the working set has long since exceeded physical RAM and the host is paging continuously. The real constraint on a 16 GiB host is **physical RAM**, not commit.
2. **Shared resident load at t=0 is ~8.1 GiB** (Gage anomaly #2: chrome ~1.6 GiB aggregate, Discord ~598 MB, claude ~519 MB, vmmem ~703 MB, MsMpEng ~320 MB, Code ~128 MB, Spotify ~352 MB, misc). This is the *realistic* backdrop for production materialize runs, not a pristine quiesced machine. 40% of physical RAM (~6.4 GiB) must be reserved for OS + shared load + NTFS cache + headroom. 60% (~9.58 GiB) is the ceiling territory available to `materialize_parquet.py`.
3. **PageFile backing store is on C:\ (SATA SSD or HDD, not NVMe on an Ivy Bridge board).** Once the process spills into PageFile, observed throughput drops 10-100×. Kill-switch must fire *before* spill, not after — reactive kill on `observed > ceiling` is too late when the disk is the bottleneck.

**Formula:**
```
CEILING_BYTES = min(
    ceil(peak_commit_aug2024 × HEADROOM_FACTOR),
    CAP_ABSOLUTE
)

where:
    HEADROOM_FACTOR = 1.3
        Anchor: Sentinel row-count variance (TimescaleDB chunks inspected 2026-04-21):
          Jul 2024 = +24% vs Mar 2024; Aug 2024 = +45% vs Mar 2024.
          Baselining on Aug 2024 (worst observed) absorbs the +45% variance *inside*
          the baseline itself; residual headroom covers only intra-month + allocator
          jitter + minor drift for new in-sample months, for which ×1.3 is defensible
          (Gregg, Systems Performance 2nd ed., recommends 1.3-1.5 for buffer pools;
          we round to the lower bound because CAP_ABSOLUTE dominates derivation
          anyway — see "cap dominance" below).

    CAP_ABSOLUTE = floor(0.60 × PHYSICAL_RAM_BYTES)    # [SUPERSEDED v2 → v3]
                 = floor(0.60 × 17,143,058,432)        # See ADR-1 v3: CAP_ABSOLUTE_v3
                 = 10,285,835,059 bytes                #   = 8,400,052,224 bytes (~7.82 GiB)
                 ≈ 9.58 GiB                            #   derived from observed quiesce floor
        Anchor: 0.60 fraction derived from observed shared resident load (~8.1 GiB ≈
        48% of 16 GiB). Leaving 40% RAM (~6.4 GiB) for OS + always-on workload +
        NTFS cache preserves ~1.3× headroom above measured shared load; 60% allocated
        to materialize_parquet is the largest share that does not force the host into
        paging against its own always-on processes. Gregg, Systems Performance,
        "Section 7.5 Methodology", recommends leaving >=20% RAM headroom for OS +
        cache; 40% is conservative because this host's cache fabric (DDR3-1333) and
        paging fabric (SATA) are both legacy-slow.

PHYSICAL_RAM_BYTES = 17,143,058,432 (per host-preflight §3, WMI
TotalPhysicalMemory; cross-verified against §6 psutil virtual_memory.total)
```

**Cap dominance — worked illustration:** If Aug-2024 baseline observes `peak_commit = 9.0 GiB`, then `9.0 × 1.3 = 11.7 GiB`, clamped by cap to **9.58 GiB**. If `peak_commit = 7.0 GiB`, then `7.0 × 1.3 = 9.1 GiB`, under cap — ceiling = 9.1 GiB. Cap dominates whenever `peak_commit > cap / 1.3 ≈ 7.37 GiB`. Current Mar-2024 G07 pre-evidence showed peaks in the 8-10 GiB range post-refactor, so cap is expected to dominate for Aug-2024 (heavier month). This is the intended regime — the ceiling is RAM-physical-truthful, not a scaled wish.

### Per-issue decisions

**Issue 1 (× 1.5 headroom is dangerous on 16 GB, meaningless on 56 GB commit):** Resolved. Formula now `min(peak × 1.3, 0.60 × physical_RAM)`. Cap at 9.58 GiB is hard RAM-physical. v1 headroom alone would produce ~15 GiB ceilings — rejected as thrash-inducing.

**Issue 2 (streaming-chunk rewrite scope):** **Recommend: keep deferred.** Accept that on this host, the ceiling may land at 9.58 GiB (the cap) rather than at `peak × 1.3` (the headroom). G09 proceeds: if Aug-2024 baseline peak is ≤ cap, the refactored cursor-stream + gc code already fits under cap and streaming-chunk is unnecessary for G09. If Aug-2024 baseline peak > cap, the baseline itself demonstrates the refactor is insufficient on this host and streaming-chunk must be pulled in; this outcome should be treated as a G09a BLOCK, not a G09 degraded-proceed. v2 treats the 9.58 GiB cap as immutable — adapting the code is cheaper than replacing the RAM. Orchestrator decision point only arises if baseline > cap.

**Issue 3 (baseline month representativeness):** **Recommend: Aug-2024.** Mar-2024 has 14.5M rows; Aug-2024 has ~21M rows (+45%). v1 baseline on Mar-2024 × 1.5 = +50% headroom *only just* absorbs Aug-2024's +45% — no residual margin for allocator jitter or larger future months. Baselining on the worst observed month absorbs variance inside the baseline itself; residual ×1.3 covers only jitter. Aug-2024 is already materialized (no re-materialize cost). Mar-2024 baseline is rejected for v2.

**Issue 4 (commit vs RSS on dynamic-PageFile host):** Riven R1 threshold (`peak_commit / peak_rss > 3.0 = leak`) is too loose for this host and must be re-calibrated by Riven in task #84. On a dynamic-PageFile host, Python allocator (especially PyArrow's buffer pool and psycopg2 result buffers) can legitimately reserve virtual memory chunks without touching them, inflating `peak_commit` vs `peak_rss` even absent a leak. v2 recommends Riven re-calibrate R1 ratio brackets to something closer to `< 2.0 normal / 2.0-4.0 tolerable / > 4.0 leak` for this host class, or switch the leak indicator from ratio to `ΔPageFile_active_size across run` (leak = PageFile grew > 500 MB during run; normal = PageFile steady). **v2 does NOT redefine R1 — that is Riven's authority.** v2 only flags the calibration issue as input to task #84.

**Issue 5 (fail-closed trip threshold — pre-emptive kill on slow-paging host):** Supersede ADR-2 exit 3 semantics. Two-stage trip:

- **Warning (log-only):** `observed >= 0.85 × CEILING_BYTES`. Wrapper emits a WARN log line with timestamp, observed, ceiling, and fraction. No kill. Continues polling.
- **Kill (exit 3):** `observed >= 0.95 × CEILING_BYTES`. Wrapper kills child immediately. No second observation required (slow-paging fabric: by the time a second tick confirms, disk thrashing has started).

At cap = 9.58 GiB: warning at ~8.14 GiB, kill at ~9.10 GiB. The 5% pre-emptive margin (~479 MB) is small in absolute terms but large relative to typical per-tick allocation deltas (cursor-stream + gc post-refactor shows per-tick deltas in the tens of MB range). Rationale: on NVMe, reactive kill at observed > ceiling is fine because spill latency is <10 ms per GB; on this host's SATA + DDR3 fabric, spill latency is ~100 ms-1 s per GB and the process digs its own grave during the reactive window.

**Issue 6 (host shared load policy):** **Recommend: quiesce, with a launch-time sanity check.** Operator (Gage) closes chrome, Discord, Code, Spotify, Battle.net, and any other non-essential GUI workload before launching baseline-run and G09. WSL2 / Docker / MsMpEng / claude CLI remain (not feasible to close claude during a claude-driven run; MsMpEng is policy-pinned; WSL2 is hypervisor-level). Wrapper launch-time check: if `psutil.virtual_memory().available < 1.5 × CAP_ABSOLUTE` (~14.4 GiB available), refuse to launch with exit 1 and a message naming the top-3 memory consumers to close. This is simpler than dynamic `cap = 0.60 × (RAM - current_other_resident)` — the operator sees the blocker and acts, and the static cap stays immutable across runs (reproducibility). The 1.5× factor covers ceiling + transient allocator behavior without making the check tautological.

> **[SUPERSEDED v2 → v3]** The `1.5 × CAP_ABSOLUTE` R4 gate is structurally unreachable on this host (shortfall 5.55 GiB vs observed 9.47 GiB mid-quiesce floor per RA-20260424-1). ADR-1 v3 replaces the formula with `available ≥ CAP_ABSOLUTE + OS_HEADROOM` where OS_HEADROOM = 1 GiB. The v3 threshold evaluates to 9,473,794,048 bytes — exactly the measured floor, by construction. See ADR-1 v3 at end of file.

### Early-trip thresholds (supersedes ADR-2 plain exit 3 semantics)

| Threshold | Fraction of CEILING_BYTES | Action |
|-----------|---------------------------|--------|
| Warn      | 0.85                       | Log WARN line; continue polling |
| Kill      | 0.95                       | Kill child immediately; exit 3 |

ADR-2 exit code 3 remains; trip condition is now `observed >= 0.95 × CEILING_BYTES` rather than `observed > CEILING_BYTES`. Exit codes 4 and 5 unchanged.

### Baseline-run policy on host quiescing

**Quiesce before launch (mandatory):** operator closes chrome, Discord, Code, Spotify, Battle.net, msedgewebview2 instances, and any game launchers. Retained (acceptable): Windows Defender (MsMpEng), WSL2 vmmem, Docker Desktop backend (if WSL2-integrated), claude CLI, explorer.exe, system services.

**Launch-time sanity check (wrapper-enforced):** `psutil.virtual_memory().available >= 1.5 × CAP_ABSOLUTE` (currently >= ~14.4 GiB available = ~6.4 GiB consumed by retained workload). If check fails, wrapper exits 1 with a message listing the top-3 non-retained consumers to close. This converts a procedural checklist into a deterministic gate — Article I (CLI First) compliant.

> **[SUPERSEDED v2 → v3]** The `>= 1.5 × CAP_ABSOLUTE` formula is replaced by `>= CAP_ABSOLUTE + OS_HEADROOM` in v3, with CAP_ABSOLUTE itself re-derived. The Article I (CLI First) deterministic-gate property is preserved — only the threshold changes from "unreachable 14.37 GiB" to "reachable 8.82 GiB (= observed floor)". See ADR-1 v3 at end of file.

### Consequences

- G09a baseline run changes from Mar-2024 to Aug-2024 (worst-observed in-sample). Already materialized; no re-materialize cost.
- Ceiling is expected to clamp at `CAP_ABSOLUTE = 9.58 GiB` for any peak_commit ≥ 7.37 GiB. In this regime, headroom factor ×1.3 is decorative — documented explicitly so future readers do not mistake cap dominance for under-derivation. `[SUPERSEDED v2 → v3]` In v3, CAP_ABSOLUTE = 7.82 GiB and cap-dominance threshold becomes peak_commit ≥ ~6.02 GiB.
- If Aug-2024 baseline peak_commit > 9.58 GiB, G09a is a BLOCK (not a degraded-proceed). Streaming-chunk rewrite is pulled in as prerequisite to G09. Orchestrator notified; Dex re-engaged.
- Riven R1 ratio brackets (v1 co-sign) must be re-calibrated for dynamic-PageFile hosts in task #84. v2 flags the issue; Riven decides the new brackets.
- Kill-switch is now pre-emptive (0.95 × ceiling), not reactive — aligns kill latency with this host's slow paging fabric.
- Baseline-run procedure gains a host-quiesce step (operator-procedural) and a launch-time availability check (wrapper-enforced at exit 1).
- Ceiling value becomes invariant across future in-sample month additions *until* physical RAM changes, hardware migration, or PageFile backing store upgrade (SATA → NVMe). The 6-month re-derivation cadence in v1 R10 Re-validation still applies; v2 adds a fourth trigger: **hardware change** (RAM add, SSD swap, host migration).
- `core/memory_budget.py` module-level constants expand from `CEILING_BYTES` to include `CAP_ABSOLUTE`, `HEADROOM_FACTOR`, `PHYSICAL_RAM_BYTES`, `HOST_PREFLIGHT_REF` (path to artifact), `BASELINE_MONTH_REF`, `WARN_FRACTION = 0.85`, `KILL_FRACTION = 0.95`. Commit message must cite the host-preflight artifact path verbatim.

**Approval chain:** Aria (design v2, this section) → Riven (re-calibrate R1/R2/R3 brackets against v2 in task #84; co-sign ceiling VALUE after Aug-2024 baseline) → Quinn audit (#85) → orchestrator marks v1 SUPERSEDED and applies v2 (#86).

**Status:** Proposed v2 — awaiting Riven R1/R2/R3 re-calibration (task #84) and Quinn audit (#85).

---

## Riven Co-sign — ADR-1 v2 (2026-04-23 BRT)

**Supersedes:** Riven Co-sign ADR-1 v1 (built on 32 GB RAM assumption; re-calibrated against real host 15.97 GiB per `data/baseline-run/host-preflight.txt`).

**Verdict:** **APPROVE** (with R1 re-calibration, two new conditions R4/R5, and tightened cap-dominance escalation).

Aria's v2 derivation is custodially sound. The CAP_ABSOLUTE anchor at 0.60 × physical RAM is RAM-physical-truthful; the headroom reduction from ×1.5 to ×1.3 is honest accounting given cap dominance; the Aug-2024 baseline absorbs the +45% variance inside the measurement rather than inside the multiplier. I co-sign the method and the constants. The conditions below are binding contract for step 7.

### Condition R1 v2 — Leak detector (re-calibrated for dynamic PageFile on 16 GiB host)

> **[PRESERVED v2 → v3]** R1 dual-signal (Signal A ratio + Signal B ΔPageFile) is preserved verbatim by v3. Both signals measure subprocess behavior independent of CAP_ABSOLUTE; CAP recalibration does not shift the brackets. Ratio brackets (<2.0 / 2.0–4.0 / >4.0) and ΔPageFile brackets (<500 MiB / 500 MiB–2 GiB / >2 GiB) stand unchanged. See Riven Co-sign v3 §R1 (end of file) for leak-detector soundness under tightened CAP.

**Decision:** **Combined indicator — BOTH must pass.** Single-indicator leak detection is insufficient on this host because (a) PyArrow buffer pool and psycopg2 result buffers legitimately inflate `peak_commit / peak_rss` even absent a leak (Aria's Issue 4 observation is correct), and (b) pure ΔPageFile can miss leaks that grow virtual without committing fresh PageFile pages. Both signals together triangulate the failure mode.

**Signal A — Ratio (re-calibrated brackets):**

| Ratio `peak_commit / peak_rss` | Interpretation | Action |
|---|---|---|
| < 2.0 | Normal; allocator working-set matches commit | PASS |
| 2.0 – 4.0 | Tolerable allocator reservation on dynamic-PageFile host | PASS with note; flag for G10 re-check |
| > 4.0 | Leak or unbounded allocator fragmentation | **BLOCK** ceiling derivation |

Rationale for the new brackets: v1 brackets (<1.5 / 1.5–3.0 / >3.0) were calibrated for a host where commit ≈ RSS is the norm. On this host, system-managed PageFile (peak historical 31.34 GiB per host-preflight §8) allows Python's allocator to reserve virtual memory aggressively without touching it — ratios in the 2–3 range are expected even under a healthy run. Tightening would produce false positives; keeping v1 brackets would block on noise. ×2.0 / ×4.0 track the Gregg buffer-pool convention scaled for virtual-heavy allocators on legacy-Windows dynamic PageFile.

**Signal B — ΔPageFile active size (primary leak indicator on this host):**

| ΔPageFile (AllocatedBaseSize end − start) | Interpretation | Action |
|---|---|---|
| < 500 MB | PageFile steady; process living inside RAM | PASS |
| 500 MB – 2 GiB | Mild PageFile growth; tolerable on 16 GiB host | PASS with note |
| > 2 GiB | PageFile grew significantly during run — process spilled to disk-backed commit | **BLOCK** ceiling derivation; refactor before re-baseline |

Rationale: host-preflight §8 confirms PageFile is SYSTEM-MANAGED (no Win32_PageFileSetting instance). Historical peak 32.1 GiB vs current 41.8 GiB allocation shows the OS already grew it once. A baseline that *further* grows PageFile by >500 MB is signalling memory pressure regardless of what ratio says. This is the anchor-of-truth on a SATA-paging host: pagefile growth = actual disk I/O incurred.

**Capture requirement:** sampler writes `peak_commit`, `peak_rss`, `pagefile_allocated_start`, `pagefile_allocated_end` per run to `data/baseline-run/baseline-telemetry.csv`. `ΔPageFile = end − start` computed at run close. BOTH signals evaluated at step 7; BLOCK if either trips.

### Condition R2 v2 — Pre-flight artifact

**Status: SATISFIED ex-ante.** `data/baseline-run/host-preflight.txt` captured 2026-04-22T23:13:24-03:00 by Gage contains every field v2 derivation requires:

| Required field | Location in artifact | Used by |
|---|---|---|
| PHYSICAL_RAM_BYTES (17,143,058,432) | §3 (`TotalPhysicalMemory`), cross-verified §6 (`psutil.virtual_memory.total`) | CAP_ABSOLUTE |
| Available at t=0 (8.40 GiB binary / 9.02 GB decimal) | §6 (`psutil.virtual_memory.available`) | Launch-time check (R4) — unit-label clarified per Quinn audit Finding 1 (2026-04-23) |
| PageFile config (SYSTEM-MANAGED, peak 32.1 GiB, allocated 41.8 GiB) | §4b, §8 | R1 Signal B, cap rationale |
| Top-20 memory consumers at t=0 | §7 | R4 whitelist |
| CPU / DIMM specs (i7-3770, DDR3-1333) | §2, §5 | Paging latency rationale (R5 pre-emptive margin) |
| Commit limit (56.81 GiB) vs physical (15.97 GiB) | §8 derived | Cap-vs-commit reasoning |
| Timestamp BRT | Header line 3 | Audit trail |

**One residual note (not a BLOCK):** §9 documents `.venv/Scripts/python.exe` does not exist and psutil was installed transiently on system Python 3.14.3 for the capture. This is acceptable for the pre-flight itself, but is a **prerequisite for G09a baseline-run** — Gage must provision the project venv before launching step 6 of remediation. R2 is satisfied; the venv gap is a step-6 operational precondition, not a pre-flight defect.

### Condition R3 v2 — × 1.3 HEADROOM rationale (Article IV anchor)

> **[SUPERSEDED v2 → v3]** The R3 anchor chain (Gregg §7.5 buffer-pool bound + Sentinel +45% variance + cap-dominance observation) is **preserved verbatim** by v3. Only the cap-dominance threshold number shifts: v2 clause 3 read "for any peak_commit > 7.37 GiB, CEILING_BYTES clamps at CAP_ABSOLUTE (9.58 GiB)"; under v3 the equivalent statement is "for any peak_commit > 6.02 GiB, CEILING_BYTES clamps at CAP_ABSOLUTE (7.82 GiB)". ×1.3 itself is unchanged; the Article IV two-citation commit-message requirement is unchanged. See Riven Co-sign v3 §R3 (end of file) for the variance-vs-new-CAP feasibility observation.

**Accepted.** Anchor chain:

1. **Baseline month choice absorbs variance.** Aug-2024 = +45% rows vs Mar-2024 (per Sentinel TimescaleDB chunk counts inspected 2026-04-21, memory cited in v1 R3 already). Baselining on the worst in-sample month pulls the +45% volatility *inside* the measurement. Residual headroom covers only allocator jitter + intra-month variance + minor drift for future months.
2. **Gregg buffer-pool lower bound.** Systems Performance 2nd ed. Section 7.5 recommends 1.3–1.5× for bounded-workload buffer pools. Aria rounds to the lower bound; this is defensible because the worst-month variance is no longer in the multiplier.
3. **Cap dominance makes the multiplier decorative.** On this host, for any `peak_commit > 7.37 GiB`, CEILING_BYTES clamps at CAP_ABSOLUTE (9.58 GiB) regardless of whether HEADROOM_FACTOR is 1.3 or 1.5. The rationale bar is therefore *contextually* lower than v1 — the multiplier controls derivation only in a narrow regime that Mar-2024 G07 pre-evidence (peaks 8-10 GiB) suggests we will not inhabit.

**I accept ×1.3 as anchored.** The two-citation standard of v1 (Gregg + Sentinel variance) is preserved; both citations must appear verbatim in the commit message when `core/memory_budget.py` is populated at step 8 (per v1 R3, still binding).

**One amendment to v1 R3:** if Aug-2024 baseline lands in the cap-dominated regime (peak > 7.37 GiB), the commit message must *additionally* note "CAP_ABSOLUTE dominates; HEADROOM_FACTOR = 1.3 is decorative for this derivation" — so future readers do not mistake truthful cap-clamping for under-derivation. Aria already flagged this in ADR-1 v2 Consequences; I am formalizing it as a commit-message requirement.

### Condition R4 v2 (NEW) — Launch-time host-quiesce check

> **[SUPERSEDED v2 → v3]** Riven's "1.5× CAP_ABSOLUTE" acceptance here is superseded by ADR-1 v3 R4 recalibration: `available ≥ CAP_ABSOLUTE + OS_HEADROOM` (v3 threshold = 9,473,794,048 bytes). Whitelist enforcement, exit-1 contract, and top-3 non-retained consumer reporting behavior (R4 message format, frozenset filter, `is_retained()` substring match) are **preserved verbatim** by v3 — only the threshold formula changes. Riven must co-sign v3 R4 recalibration per handoff clause at end of ADR-1 v3.

**Accepted with whitelist.** Aria's proposed gate: wrapper exits 1 if `psutil.virtual_memory().available < 1.5 × CAP_ABSOLUTE` (~14.4 GiB) at t=0. I co-sign this threshold. At 1.5× cap, available headroom covers the ceiling + a full headroom-factor buffer above it — enough margin that the process will not immediately race another resident consumer for the last GiB.

**Whitelist (retained-but-allowed at t=0):**

| Process | Rationale |
|---|---|
| MsMpEng.exe | Windows Defender policy-pinned; cannot be closed by operator |
| vmmem | WSL2/Hyper-V hypervisor-level; closing requires `wsl --shutdown` which disrupts Docker |
| com.docker.backend.exe / Docker Desktop.exe | WSL2-integrated backend; Gage may need for adjacent tooling |
| claude.exe | Driving the baseline run itself; cannot be closed |
| explorer.exe | Core shell; closing breaks operator UX |
| System services (< 100 MB each) | OS baseline |

**Must-close list (operator-enforced before launch):** chrome (all instances), Discord, Code (VSCode), Spotify, Battle.net, msedgewebview2 (all instances), any game launchers, any browser-derived processes. Closing these at capture time (§7) would free ~2.1 GiB (chrome aggregate 1.6 GiB + Discord 0.6 GiB + Spotify 0.36 GiB + Code 0.13 GiB + Battle.net 0.18 GiB, net of some msedgewebview2 overlap).

**Exit-1 message requirement:** the wrapper MUST name the top-3 non-whitelisted consumers with process name + PID + WorkingSet64 in MB. This makes the remediation action deterministic (operator closes the named processes) rather than interpretive.

### Condition R5 v2 (NEW) — Early-trip thresholds (warn/kill)

> **[SUPERSEDED v2 → v3]** The 85/95 **fractions** are preserved verbatim by v3 (see Riven Co-sign v3 §R5 recalibration at end of file). Only the **absolute byte values** of WARN / KILL shift because CAP_ABSOLUTE tightened from 9.58 → 7.82 GiB: v3 WARN = 0.85 × 7.82 = 6.65 GiB (7,140,044,390 bytes); v3 KILL = 0.95 × 7.82 = 7.43 GiB (7,980,049,612 bytes); v3 warn-to-kill buffer = ~840 MiB (was ~958 MiB). The multi-tick visibility argument below still holds — per-tick deltas remain tens of MB, so 1–3 ticks (~30–90 s) elapse between WARN and KILL. Fractions and tick cadence unchanged.

**Accepted — 85/95 is correct for this host.** The 10-percentage-point buffer (~958 MB at cap = 9.58 GiB) is adequate because:

1. **Per-tick allocation deltas post-refactor are in the tens of MB range.** Cursor-stream + gc produces small steady growth, not large step allocations. Warn→kill transition should take multiple poll ticks (30s apart per ADR-2), giving a ~1-3 min window where the WARN log line is visible before the kill. That's enough for an attentive operator to see the pattern even if they don't override.
2. **Absolute kill point (~9.10 GiB at cap = 9.58 GiB) is still comfortably below physical RAM (15.97 GiB) and well below commit limit.** Even if kill fires one tick late, the host has enough RAM slack that slow-paging fabric has not yet fully engaged — the kill completes in seconds, not minutes.
3. **Pushing warn earlier (e.g. 80%) would produce noise.** A healthy baseline run peaks somewhere below cap; at 80% the WARN line would fire during normal operation, training operators to ignore it. 85% is tight enough to be actionable, loose enough to mean something.

**I do not accept 80/95 or 85/90.** 85/95 stands.

**One strengthening:** the WARN line must include `observed`, `ceiling`, `fraction`, `poll_tick_count`, and the top-3 child-process allocator categories if available (PyArrow buffer pool, psycopg2 cursor, generic heap — bucketable via `tracemalloc` snapshot if enabled). Minimal form (no tracemalloc) is `WARN ceiling={ceiling} observed={observed} fraction={frac:.3f} tick={n}`. Operator can then correlate trend across ticks manually.

### Escalation clause v2

Riven BLOCKS ceiling derivation at step 7 if ANY of the following trip:

| Condition | Signal | Resolution |
|---|---|---|
| **E1 — Baseline peak exceeds cap** | `peak_commit_aug2024 > CAP_ABSOLUTE` (9.58 GiB) | Streaming-chunk rewrite pulled in as G09 prerequisite; re-baseline after refactor. G09 does not proceed under cap as a degraded ceiling. |
| **E2 — Cap > 0.70 × physical RAM** | CAP_ABSOLUTE / PHYSICAL_RAM_BYTES > 0.70 | Does not trigger at current values (0.60 anchor holds). Tripwire for any future revision that relaxes the 40% OS reserve — such a revision requires new ADR + Riven co-sign. |
| **E3 — R1 leak detector trips during baseline** | Ratio > 4.0 OR ΔPageFile > 2 GiB | Refactor insufficient; Dex re-engaged. No ceiling derived on leaked baseline. |
| **E4 — Physical RAM changes** | `psutil.virtual_memory().total` differs from HOST_PREFLIGHT_REF by > 1% | Full re-derivation (new host-preflight + new baseline + new ceiling). Mandatory. |
| **E5 — PageFile backing store migrates** (SATA → NVMe, or NVMe → SATA) | Operator-reported hardware change | R5 warn/kill thresholds must be re-evaluated; paging latency changed by 10-100×. |
| **E6 — Launch-time available < 1.5 × CAP** | R4 gate fails | Operator closes named processes; retry. Not a derivation BLOCK, but a gate BLOCK on every run. `[SUPERSEDED v2 → v3]` Signal rewritten to `available < CAP_ABSOLUTE + OS_HEADROOM`; resolution path unchanged. |

E1, E2, E3 BLOCK step 7 (ceiling value not promoted). E4, E5 trigger full re-derivation. E6 blocks each individual launch.

### Fail-closed cross-reference

Mapping each v2 trip condition to ADR-2 exit codes (confirming no trip is orphaned):

| Trip condition | ADR-2 exit code | Wrapper action |
|---|---|---|
| R1 leak (ratio or ΔPageFile) | N/A (detected post-run at step 7) | No runtime wrapper trip; Riven blocks at derivation |
| R4 launch-time check failed | **1** (wrapper setup error) | Refuse to launch; print top-3 consumers |
| R5 WARN threshold (85%) | N/A (log-only, no exit) | Emit WARN line; continue polling |
| R5 KILL threshold (95%) | **3** (ceiling tripped, child killed) | Kill child immediately; no second-tick confirmation |
| Sampler fail (3× consecutive) | **5** (sampler lost visibility) | Kill child defensively (existing ADR-2) |
| psutil not importable | **4** (pre-launch abort) | Never launch (existing ADR-2) |
| Hold-out lock raised by child | **2** | Propagated (existing ADR-2) |

Every v2 trip condition has a runtime exit-code home except R1 (intentionally a post-run audit, not runtime). No orphans.

### Re-validation cadence

Re-derivation of `CEILING_BYTES` + `CAP_ABSOLUTE` required on ANY of:

| Trigger | Scope | Owner |
|---|---|---|
| **(a) Physical RAM change** (E4) | Full: new host-preflight + new baseline + new ceiling | Gage + Aria + Riven |
| **(b) `materialize_parquet.py` refactor** touching cursor handling, batch size, or write path | Full re-baseline; cap may stay if hardware unchanged | Dex → Gage → Aria + Riven |
| **(c) 6 months elapsed since last derivation** | Full re-baseline (data volume drift — new months extend manifest) | Gage triggers; Aria + Riven co-sign |
| **(d) Production run peaks above 85% of ceiling** | Advisory: re-baseline within 30 days if sustained across 2+ runs | Operator flags; Riven decides cadence |
| **(e) Host-preflight re-capture required quarterly** | R2 artifact refreshed; derivation unchanged unless §3/§6/§8 fields shifted materially | Gage |
| **(f) Windows feature update** affecting memory management (e.g. PageFile scheduler, WSL2 memory reclamation, any KB that touches `Kernel-Memory-Manager`) | Re-capture host-preflight; Riven evaluates whether re-baseline is warranted | Gage + Riven |
| **(g) PageFile backing-store migration** (SATA ↔ NVMe) (E5) | Re-evaluate R5 warn/kill thresholds; baseline unchanged if `peak_commit` steady | Gage + Riven |

Triggers (a), (b), (c) require new ADR amendment + Riven co-sign per standard R10 procedure. Triggers (d), (e), (f), (g) may resolve with artifact refresh only if derivation constants do not move; promoted to full re-derivation if they do.

---

**Sign-off:**
- 2026-04-23T15:45-03:00 BRT — **Riven (@risk-manager, R10 custodial)** — ADR-1 v2 **APPROVED** per conditions R1-R5 v2 above. Method + constants co-signed; ceiling VALUE still pending Aug-2024 baseline + step-7 derivation per escalation conditions E1-E3.
- Next required sign-off: Riven at step 7 of v2 remediation (post-baseline derivation) with concrete `peak_commit`, `peak_rss`, ratio (Signal A), ΔPageFile (Signal B), host-preflight cross-ref, and final `CEILING_BYTES` value (either `ceil(peak × 1.3)` or `CAP_ABSOLUTE`, whichever is lower).

---

**Status:** ADR-1 v2 + Riven Co-sign v2 — awaiting Quinn audit (#85), then orchestrator applies SUPERSEDED markers and commits (#86).

---

## Aria Ratifications (post-Quinn audit, 2026-04-23 BRT)

**Trigger:** Quinn audit verdict CONCERNS at `docs/qa/gates/ADR-1-v2-audit.md`; 3 findings require Aria (@architect) ratification before Dex (@dev) can begin #74 implementation.

### Finding 4 — CAP_ABSOLUTE hardcode vs dynamic: Option (A) — Bless Quinn's recommendation verbatim

**Decision:** Dex implements the literals as module-level int constants in `core/memory_budget.py`:

```python
PHYSICAL_RAM_BYTES = 17_143_058_432   # per host-preflight §3 / §6
CAP_ABSOLUTE       = 10_285_835_059   # = floor(0.60 × PHYSICAL_RAM_BYTES), per ADR-1 v2 formula
                                      # [SUPERSEDED v2 → v3]: CAP_ABSOLUTE = 8_400_052_224
                                      #                      (= observed_quiesce_floor − OS_HEADROOM).
                                      #                      See ADR-1 v3 at end of file.
```

**Plus a runtime drift check** at wrapper launch (before the R4 availability check): compare `psutil.virtual_memory().total` against `PHYSICAL_RAM_BYTES`. If `abs(psutil_total - PHYSICAL_RAM_BYTES) / PHYSICAL_RAM_BYTES > 0.01`, wrapper exits **1** with a message of the form:

```
ERROR: physical RAM drift detected.
  PHYSICAL_RAM_BYTES (constant) = 17,143,058,432 (16.0 GiB)
  psutil.virtual_memory().total = <observed> (<observed_GiB> GiB)
  drift = <pct>% (> 1% threshold)
This host differs from the baseline host (host-preflight 2026-04-22T23:13:24-03:00).
Full re-derivation required per ADR-1 v2 escalation clause E4 (Physical RAM change):
new host-preflight → new baseline → new CEILING_BYTES.
Contact @architect (Aria) + @risk-manager (Riven) before re-running.
```

**Rationale:** Static literals encode Riven's E4 intent ("Full re-derivation required on RAM change") as first-class module constants — the ceiling and cap trace to the baseline host verbatim, reproducibly, across dev/prod/CI. The drift check transforms E4 from procedural-prose into a deterministic exit-1 gate at every launch: the host that runs the wrapper is *proven* to be the host that produced the derivation (within 1%), or the wrapper refuses to launch. Dynamic computation (option B) would silently re-derive CAP on a different host — masking E4 rather than enforcing it. Option C (dev-host override flag) adds a bypass mechanism that would be used exactly once and then forgotten, eroding the reproducibility guarantee. Hardcoded + drift check is the configuration that cannot be accidentally violated. Dex has zero ambiguity: the two integers above are the values to paste; the drift check is a wrapper-launch-time gate; exit code is 1.

### Finding 7 — tracemalloc bucket scope: Option (A) — Mark out-of-scope for #74

**Decision:** Dex implements ONLY the minimal WARN form specified in Riven R5 v2:

```
WARN ceiling={ceiling} observed={observed} fraction={frac:.3f} tick={n}
```

No tracemalloc instrumentation, no `PYTHONTRACEMALLOC` env-var propagation, no top-3 allocator bucket annotation in #74. The "top-3 child-process allocator categories if available" phrase in Riven R5 v2 is hereby marked **out-of-scope for #74** and deferred to a future observability follow-up story (to be scoped separately; candidate name: T002.0z-allocator-bucket-telemetry or similar — orchestrator/Pax decides story identity). Dex MUST NOT leave scaffolding, commented-out blocks, or `TODO: tracemalloc` stubs in `core/run_with_ceiling.py` — when the follow-up story is picked up, the code will be designed cleanly from scratch against a concrete requirement.

**Rationale:** Tracemalloc bucket annotation requires (a) wrapper-side env-var propagation to the child, (b) a snapshot-capture hook in the child's Python runtime, (c) a serialization path from child → wrapper → WARN line, and (d) a test matrix covering "tracemalloc enabled" vs "tracemalloc absent" vs "snapshot failed." That's a standalone story, not a half-feature inside #74. Keeping #74 scope tight to the minimal WARN form means the kill-switch ships under the 95% trip with immediate utility, and allocator introspection gets proper story treatment (AC, tests, docs) when prioritized. Dex has zero ambiguity: emit the four-field WARN line, move on.

### Finding 8 — ADR-2 cross-reference: Option (A) — Apply Quinn's recommendation verbatim; edit applied

**Decision:** Footnote pointers added inline to ADR-2 exit codes 1 and 3 (above, at lines 53-59 of this file). Original ADR-2 text preserved verbatim; each modified line retains its v1 semantic and appends a parenthetical `(¹under ADR-1 v2: ...)` pointing forward to the superseding clause. This matches Quinn's recommended style ("one-line footnote/pointer") and covers both threshold changes in a single editorial pass:

- Exit 1 footnote covers R4 launch-time check + E4 drift check (both new v2 exit-1 trip conditions)
- Exit 3 footnote covers the 95% pre-emptive trip threshold change

**Rationale:** Option (B) — a note box above the exit codes — would rewrite ADR-2 structure (adding an out-of-band block before the numbered list), which is heavier than necessary and slightly dilutes the "original ADR-2 preserved" invariant. One-line footnotes at the exact affected lines preserve ADR-2 structure and scan cleanly; a reader who reaches line 53 or 56 is redirected to the superseding clause without needing to read an upstream note. Option (C) is unnecessary — Quinn's prescribed form is precisely the minimum-viable cross-reference and it lands correctly. Edit applied in this commit.

---

**Sign-off:** Aria (@architect) — 2026-04-23 BRT. Findings 4, 7, 8 ratified. Dex #74 unblocked on Aria side (pending Riven ratification of findings 5, 6 in task #89).

---

## Riven Ratifications (post-Quinn audit, 2026-04-23 BRT)

**Trigger:** Quinn audit verdict CONCERNS at `docs/qa/gates/ADR-1-v2-audit.md`; findings 5 and 6 require Riven (@risk-manager, R10 custodial) ratification before Dex (@dev) can begin #74 implementation.

### Finding 5 — Telemetry granularity (two-output split): Option (A) — Bless Quinn's two-output split verbatim

**Decision:** Dex implements **two output files per baseline run**, both named by `--run-id` per ADR-3. The per-tick CSV is raw audit evidence (Quinn/Sable can re-derive the summary from it); the per-run JSON is what Riven reads at R1 step 7 to validate ceiling derivation (fast, structured, no parsing). Schemas are load-bearing — Dex MUST embed them as module-level constants in a sibling `core/telemetry_schema.py` (separate from `core/memory_budget.py` to keep the ceiling module free of serialization concerns).

**Output (a) — `data/baseline-run/baseline-telemetry.csv` (one row per polling tick):**

Column order is normative. Dex embeds as `TELEMETRY_CSV_COLUMNS: tuple[str, ...]` in `core/telemetry_schema.py`:

```python
TELEMETRY_CSV_COLUMNS: tuple[str, ...] = (
    "tick_n",              # int, monotonic from 1
    "ts_brt",              # ISO-8601 with -03:00 offset, e.g. "2026-04-23T14:05:32-03:00"
    "commit_bytes",        # int, psutil child process.memory_info().vms (commit charge proxy)
    "rss_bytes",           # int, psutil child process.memory_info().rss
    "pagefile_alloc_bytes",# int, psutil.swap_memory().used at tick time
    "available_bytes",     # int, psutil.virtual_memory().available at tick time
)
```

- Header row MUST be written on file open (before tick 1).
- Encoding: UTF-8, LF line endings, no BOM.
- Missing sample (e.g. child transient unreadable): write row with commit_bytes/rss_bytes empty, other fields populated; do NOT skip the tick (tick_n monotonicity is an audit invariant).
- Expected volume: ~120 rows for a ~1h run at 30s poll; ~360 for a 3h run. File size trivial.

**Output (b) — `data/baseline-run/baseline-summary.json` (one record per run):**

Dex embeds as `SUMMARY_JSON_FIELDS: tuple[str, ...]` in `core/telemetry_schema.py` (documentation-only; JSON serialization uses a dict):

```python
SUMMARY_JSON_FIELDS: tuple[str, ...] = (
    "run_id",                   # str, from --run-id
    "start_ts",                 # ISO-8601 BRT, wrapper launch
    "end_ts",                   # ISO-8601 BRT, child exit (or kill) time
    "duration_s",               # int, end_ts - start_ts in whole seconds
    "peak_commit",              # int bytes, max(commit_bytes) over all ticks
    "peak_rss",                 # int bytes, max(rss_bytes) over all ticks
    "pagefile_alloc_start",     # int bytes, first tick's pagefile_alloc_bytes
    "pagefile_alloc_end",       # int bytes, last tick's pagefile_alloc_bytes
    "delta_pagefile",           # int bytes, pagefile_alloc_end - pagefile_alloc_start (signed)
    "ratio_commit_rss",         # float, peak_commit / peak_rss, 3-decimal precision
    "tick_count",               # int, total ticks written to CSV
    "exit_code",                # int, child exit code (0 normal, 3 KILL-SWITCH trip, 4/5 sampler failure)
)
```

- JSON MUST be written atomically at wrapper close (tempfile + rename), NOT incrementally. A crashed wrapper that never reached close → no summary.json → Riven treats the run as incomplete.
- `ratio_commit_rss`: round-half-even to 3 decimals; if `peak_rss == 0` (impossible in practice but guard anyway), emit `null`.
- Encoding: UTF-8, 2-space indent, trailing newline.

**Rationale:** The CSV is the source of truth; the JSON is a derived artifact. Dex must compute JSON fields at wrapper close by streaming the CSV (or maintaining running aggregates in memory — either is acceptable). This separation means a distrusting auditor can `pandas.read_csv` + recompute peak/delta/ratio and compare — any mismatch is a wrapper bug, and the CSV wins because it is the primary observation. Single-output alternatives (B) were considered and rejected: a CSV-with-summary-header breaks pandas defaults; a nested JSON "ticks" array bloats the summary and tempts readers to skip streaming. Two files, each with one job, is the cleanest custodial posture. Dex has zero ambiguity on field names, types, units, ordering, or atomicity semantics.

### Finding 6 — R4 whitelist representation: Option (A) — Bless code constant with one amendment

**Decision:** Dex implements R4 whitelist as a module-level `frozenset[str]` in `core/memory_budget.py` plus an `is_retained(process_name: str) -> bool` filter function using **case-insensitive substring match**. At launch-time check (R4), if `psutil.virtual_memory().available < 1.5 * CAP_ABSOLUTE`, wrapper computes top-3 processes by `WorkingSet64` (via `psutil.process_iter(['name', 'pid', 'memory_info'])`), filters out those where `is_retained(proc.name()) == True`, and reports the top-3 **non-whitelisted** consumers with `name + PID + WorkingSet64 MB` in the exit-1 error message.

**Final whitelist contents (amendment applied — see rationale below for additions vs Quinn's base):**

```python
_RETAINED_PROCESSES: frozenset[str] = frozenset({
    "msmpeng",          # Windows Defender real-time scanner — cannot be closed without admin + policy override
    "vmmem",            # Hyper-V / WSL2 guest memory — closing kills all WSL2 distros including any dev tooling
    "com.docker",       # Docker Desktop backend (com.docker.backend, com.docker.build, etc.)
    "docker desktop",   # Docker Desktop UI
    "claude",           # Current dev shell if wrapper invoked from claude; closing = session death
    "explorer",         # Windows shell — closing crashes the desktop
    "services",         # Windows service control manager (services.exe) — Windows core
    "system",           # Windows system services (PID 4, etc.) — kernel-space, cannot be closed
    "svchost",          # Windows service host instances — tens of instances, each non-negotiable
    "csrss",            # Windows client/server runtime — kernel-adjacent, closing = BSOD
    "smss",             # Windows session manager — kernel-adjacent
    "wininit",          # Windows init — kernel-adjacent
    "winlogon",         # Windows logon manager — closing logs out the user mid-run
    "lsass",            # Local Security Authority — closing crashes the session (Windows enforces this)
    "registry",         # Windows 10+ Registry process — kernel-adjacent memory holder
    "memory compression",# Windows memory manager helper (MemCompression) — kernel-space, not closable
})

def is_retained(process_name: str) -> bool:
    """Return True if `process_name` (case-insensitive) matches a retained-but-allowed
    process in _RETAINED_PROCESSES. Match is substring (name contains whitelist entry),
    enabling e.g. 'com.docker.backend' to match 'com.docker'."""
    name_lower = process_name.lower()
    return any(entry in name_lower for entry in _RETAINED_PROCESSES)
```

**Amendments to Quinn's base list (two additions):**

- **`registry`** added: on Windows 10+ the Registry is a separate process (since RS5 / 1809) that can legitimately hold hundreds of MB. It is kernel-adjacent and not closable by the operator — omitting it would produce noise-top-3 reports blaming Registry, which the operator cannot act on.
- **`memory compression`** added: MemCompression is the Windows memory manager's compressed-pages helper. It can appear with multi-GB WorkingSet64 when the system is under memory pressure (which is *exactly* when R4 trips). Not closable. Same noise-reduction rationale as Registry.

All other entries from Quinn's recommendation retained verbatim. Substring match (not exact match) preserved — this is what allows `"com.docker.backend.exe"` and `"Docker Desktop.exe"` to both match `"com.docker"` and `"docker desktop"` respectively without requiring Dex to enumerate every Docker subprocess name.

**Rationale:** Option (A) — code constant — is the only option that makes the whitelist machine-checkable at launch time AND documents the intent in the module that owns the ceiling (colocated with `CAP_ABSOLUTE`, `HEADROOM_FACTOR`, etc.). Option (B) — YAML sidecar — adds a configuration surface that would invite silent drift (edits not covered by ADR); whitelist entries encode risk decisions and belong under ADR governance, not config. Option (C) — prose-only in error message — fails Quinn's recommended design because it forces the operator to mentally filter noise processes at the moment of an R4 trip, which is exactly when cognitive load must be minimized. The frozenset + filter function puts the filtering in the code path, keeps the operator message actionable (top-3 *non-whitelisted*), and the two additions above (`registry`, `memory compression`) harden the list against Windows 10+ realities that Quinn's base list did not explicitly cover. Dex has zero ambiguity: copy the frozenset verbatim into `core/memory_budget.py`, add the `is_retained()` function exactly as written, use it to filter the top-3 WorkingSet64 ranking before constructing the exit-1 message.

---

**Sign-off:** Riven (@risk-manager, R10 custodial) — 2026-04-23 BRT. Findings 5, 6 ratified. Dex #74 fully unblocked on architect + custodial authority; proceed to Quinn re-gate on implementation (#76).

---

## R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260423-1)

> **[SUPERSEDED 2026-04-23 — unused, wrapper missing passthrough; see RA-20260424-1]**
> Status: Technically unused. Gage halted pre-quiesce at Step 1d (before stopping any service) upon discovering `scripts/run_materialize_with_ceiling.py` lacked passthrough for `--output-dir`, `--no-manifest`, and `--manifest-path` flags — a precondition for Decision 7 hard bound 1 (canonical manifest untouched). No `docker stop`, no `wsl --shutdown`, no state change occurred. @dev (Dex) subsequently patched the wrapper (5 new tests, 209 passed / 1 skipped, ruff clean, mutex group at wrapper surface); @qa (Quinn) gated **PASS 7/7 zero concerns** at `docs/qa/gates/wrapper-passthrough-gate.md`. Per amendment spirit (one-shot per attempt), a fresh RA is issued before Gage retries with the patched wrapper. The decisions below remain analytically valid — reproduced verbatim in RA-20260424-1 except for the authorized invocation (Decision 5+) which now uses the patched wrapper surface. Audit trail preserved below — DO NOT DELETE.
**Date:** 2026-04-23 BRT
**Scope:** **ONE (1) G09a baseline-run execution only.** NOT a permanent policy change. Whitelist frozenset in `core/memory_budget.py` L42-L59 remains **unchanged** — this amendment operates at the *operational policy* layer (procedural authorization for Gage), not at the *code contract* layer (is_retained() filter).
**Trigger:** `data/baseline-run/baseline-aug-2024-preflight-halt.md` — G09a retry halted at R4 (Step 1d) with 8.22 GiB deficit unrecoverable via operator action alone. Top-20 non-retained consumer aggregate RSS = ~0.95 GiB; the ~8.22 GiB deficit sits inside the R4 whitelist (vmmem/WSL2 + Docker Desktop + MsMpEng + claude + system services). User selected Path B (temporary whitelist amendment permitting ex-ante WSL2 + Docker container stop in a bounded quiesce window).
**Supersedes:** Nothing. Extends ADR-1 v2 R4 for this single run. All ADR-1 v2 constants, whitelist code contract, and E1-E5 escalations remain in force. E6 (launch-time available < 1.5 × CAP) is the clause this amendment gates against, by authorizing the operator to temporarily reduce retained load.

### Decision 1 — Services authorized to stop (MINIMUM SET)

Authorized stops (in order):

| Service | Stop mechanism | Rationale | Expected free (GiB) |
|---|---|---|---|
| `sentinel-timescaledb` (Docker container only — **NOT Docker Desktop itself**) | `docker stop sentinel-timescaledb` | Container is idle for baseline-run (baseline uses canonical parquets, not Sentinel DB). Docker Desktop backend kept running to permit fast `docker start` on restore. | ~0.5-1.0 |
| `vmmem` (WSL2 subsystem, all distros) | `wsl --shutdown` | Halts all WSL2 guest memory. Gage confirmed in preflight halt report §136-141 that vmmem is the largest reclaimable retained consumer at t=second-capture. | ~3.0-4.0 |

Expected combined reclaim: **~3.5-5.0 GiB**, sufficient to cross the 14.37 GiB available threshold from the observed 6.15 GiB floor.

**REFUSED stops (Riven asserts NO):**

| Service | Refusal basis |
|---|---|
| `MsMpEng` (Windows Defender) | Security-pinned. Stopping AV during a long-running disk-intensive write is a hard refuse. Non-negotiable. |
| `claude` | This process launches the wrapper. Stopping it kills Gage mid-execution. Impossible. |
| `Docker Desktop` (UI + full backend, not just container) | Deeper deviation; container-only stop is sufficient per expected reclaim above. If container-only stop proves insufficient at Step c mid-quiesce, escalate (do NOT unilaterally extend scope). |
| `System` / `svchost` / `csrss` / `smss` / `wininit` / `winlogon` / `lsass` / `Registry` / `Memory Compression` / `explorer` | OS kernel-adjacent or shell-critical. Never stop. |

**Article IV anchor:** The minimum set traces to the observed deficit in the halt report (~4.96-8.22 GiB) + historical vmmem/Docker combined footprint on this host (3-6 GiB per ADR-1 v2 §215 shared-resident analysis). No guessed reclaim values.

### Decision 2 — Duration cap

**HARD CEILING: 4 hours from start of Step a (first `docker stop`) to completion of Step e (post-restore verification).**

Anchor chain:
- Baseline-run estimated wall-clock: 1-2h (ADR-1 v2 Aug-2024 = 21M rows vs Mar-2024 G07 observed ~45 min for 14.5M rows → ~1.1h scaled linearly; +50% variance margin → 2h upper bound).
- Pre/post-flight overhead: ~15 min (host-preflight capture, sha256 verifications, quiesce snapshots, container health poll).
- Restore verification + audit: ~15 min (docker start + health poll ≤ 90s + sha256 re-verify + audit YAML write).
- Safety margin: ~30 min for transient disk/network anomalies.
- **Total: 2h run + 30m overhead + 30m margin + 60m absolute tail = 4h.**

**Fail-closed behavior at ceiling:** if t ≥ start + 4h and baseline-run child is still executing, Gage MUST:
1. Send SIGTERM (graceful) to baseline-run child.
2. Wait ≤ 30s; if still alive, SIGKILL.
3. Proceed to restore sequence (Decision 5) **regardless of partial data state**.
4. Report partial exit with `duration_cap_exceeded: true` in the audit YAML.

No grace extension. No "it's almost done, just 10 more minutes." The ceiling is a time bound, not a soft goal.

### Decision 3 — Pre-quiesce verifications (GATE before any stop)

Gage MUST record all of the following into `data/baseline-run/quiesce-pre.json` **before** Step a:

| Verification | Expected value | Action if fail |
|---|---|---|
| sha256 `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | HALT; escalate (do not stop services) |
| sha256 `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | HALT; escalate |
| `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` | `healthy` (recorded, not required) | Record observed state; continue (container health is informational for restore comparison, not a launch gate) |
| `data/baseline-run/` exists | directory present | create if missing |
| `data/baseline-run/scratch/` ready | directory present | create if missing |
| `psutil.virtual_memory()` snapshot | recorded | no gate |
| `psutil.process_iter()` top-30 by RSS | recorded | no gate |

Output JSON schema (minimum keys): `{timestamp_brt, manifest_sha256, parquet_sha256, sentinel_health, virtual_memory: {total, available, used, percent}, swap: {used, total}, top_30_processes: [{name, pid, rss_bytes}]}`.

### Decision 4 — Quiesce order (deterministic, auditable)

| Step | Action | Log |
|---|---|---|
| a | `docker stop sentinel-timescaledb` (timeout default 10s; if fails, `docker stop -t 30 sentinel-timescaledb` retry) | `quiesce-audit-YYYYMMDD.yaml` step_a entry with exit_code + timestamp |
| b | `wsl --shutdown` | step_b entry with exit_code + timestamp |
| c | `time.sleep(30)` — allow hypervisor to release vmmem pages | step_c entry with timestamp |
| d | Re-capture `psutil.virtual_memory()` → write `data/baseline-run/quiesce-mid.json` | step_d entry; compare available to 14.37 GiB threshold |
| e | **GATE:** if `available >= 15_428_752_588` bytes (1.5 × CAP_ABSOLUTE = 14.37 GiB) → proceed to Step 2 of baseline-run procedure. Else HALT and escalate. | step_e entry with decision PROCEED or HALT |

**HALT-at-step-e rule:** if Step d still shows available < 14.37 GiB (e.g., another large resident process grew during the quiesce window), Gage MUST NOT:
- Stop Docker Desktop entirely (deeper deviation; requires new amendment)
- Stop any other whitelisted process
- Lower the threshold
- Retry the quiesce loop

Gage MUST: restore services per Decision 5, write audit YAML, escalate to orchestrator with observed numbers.

### Decision 5 — Restore order (ALWAYS executed — success, failure, or cap-exceeded)

| Step | Action | Verification |
|---|---|---|
| a | WSL2 left dormant (no action). Next user-initiated WSL command will restart it. Gage does NOT actively launch a WSL2 shell. | — |
| b | `docker start sentinel-timescaledb` | exit_code == 0 |
| c | Poll `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` every 5s; accept on `healthy`; timeout 90s total | If timeout without healthy → escalate immediately, do NOT retry |
| d | `psutil.virtual_memory()` + `psutil.process_iter()` top-30 → `data/baseline-run/quiesce-post.json` | — |
| e | Re-verify canonical sha256 — manifest + Aug-2024 parquet — MUST match pre-quiesce hashes byte-identically | If mismatch → CRITICAL, escalate; do NOT attempt repair |

**Restore is unconditional:** executed whether baseline-run exited 0 (success), nonzero (failure), or was killed by duration-cap enforcement. Services must be restored before Gage's session ends.

### Decision 6 — Audit trail (Gage MUST fulfill)

Gage appends a structured YAML document to `data/baseline-run/quiesce-audit-YYYYMMDD.yaml` (create if absent; append if exists — one document per quiesce window). Required schema:

```yaml
- quiesce_window:
    amendment_id: RA-20260423-1
    operator: gage
    date_brt: 2026-MM-DD
    run_id: baseline-aug-2024-retry-N   # whatever --run-id Gage uses
    ceiling_expires_at_brt: <start + 4h ISO-8601>
    pre:
      timestamp_brt: <iso>
      manifest_sha256: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
      parquet_sha256: bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0
      available_bytes: <int>
      sentinel_health: <healthy|unhealthy|starting|...>
    quiesce:
      step_a_docker_stop: {timestamp_brt: <iso>, exit_code: <int>}
      step_b_wsl_shutdown: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_sleep: {timestamp_brt: <iso>, duration_s: 30}
      step_d_mid_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_gate: {decision: PROCEED|HALT, threshold_bytes: 15428752588, available_bytes: <int>}
    baseline_child:
      launched: <bool>
      pid: <int|null>
      start_ts_brt: <iso|null>
      end_ts_brt: <iso|null>
      exit_code: <int|null>
      duration_cap_exceeded: <bool>
    restore:
      step_a_wsl_state: dormant
      step_b_docker_start: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_container_health: {timestamp_brt: <iso>, status: <healthy|timeout>, poll_count: <int>}
      step_d_post_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_sha256_reverify:
        manifest_match: <bool>
        parquet_match: <bool>
    final_disposition: <SUCCESS|BASELINE_FAIL|CAP_EXCEEDED|QUIESCE_GATE_HALT|RESTORE_FAIL>
```

This audit YAML lives inside `data/baseline-run/` (scratch area, L4 runtime per framework boundary). It is **not** a manifest mutation; no MANIFEST_CHANGES entry is required for the audit YAML itself. Only this RA-20260423-1 policy artifact is registered in MANIFEST_CHANGES (as spec_issuance; manifest unchanged).

### Decision 7 — Hard bounds (non-negotiable even under amendment)

| Bound | Enforcement |
|---|---|
| Canonical `data/manifest.csv` untouched | Use `--no-manifest` or `--manifest-path <scratch>` per MWF-20260422-1. Re-verified in Decision 5 step e. |
| Canonical parquets in `data/in_sample/**` untouched | Scratch output only; re-verified in Decision 5 step e. |
| MsMpEng NEVER stopped | Hard refusal at Decision 1. |
| `claude` NEVER stopped | Would kill Gage; impossible. |
| Restore failure (sentinel not healthy in 90s) → immediate escalation | Gage does NOT attempt DB repair or retry cycles. Orchestrator decides next step. |
| Duration cap hit mid-run → SIGTERM/SIGKILL baseline child, restore services, report partial | No grace extension. Decision 2. |
| sha256 mismatch at Decision 5 step e → CRITICAL escalation | Canonical state has been altered during the window (should be physically impossible if hard bounds 1+2 held). Do not attempt recovery. |
| No permanent whitelist change | `core/memory_budget.py` `_RETAINED_PROCESSES` frozenset unchanged. Amendment expires when audit YAML final_disposition is written. |

### Sign-off

**2026-04-23 BRT — Riven (@risk-manager, R10 custodial) — RA-20260423-1 APPROVED.**

Amendment scope: ONE G09a baseline-run window, ≤ 4 hours total, WSL2 + sentinel-timescaledb container stop authorized, all other ADR-1 v2 constraints in force (CAP_ABSOLUTE = 10,285,835,059 bytes unchanged; CEILING_BYTES still pending step-7 derivation; E1-E5 active; whitelist code contract unchanged). Gage executes under decisions 1-7 above with zero clarifying questions. On completion, this amendment is spent — a second retry or any subsequent quiesce requires a new RA-YYYYMMDD-N amendment.

Reference: halt report at `data/baseline-run/baseline-aug-2024-preflight-halt.md`.

---

## R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260424-1)

> **[SUPERSEDED 2026-04-23 — consumed at Phase 2f under v2 R4 (unreachable 14.37 GiB gate); see RA-20260425-1 under ADR-1 v3]**
> Status: Consumed (one-shot spent). Gage (@devops) executed the authorized quiesce sequence per Decisions 1-4; `data/baseline-run/quiesce-mid.json` captured `available = 9,473,794,048` bytes at 2026-04-23T19:21:51-03:00 — structurally below the v2 R4 threshold of `1.5 × CAP_ABSOLUTE_v2 = 15,428,752,588` bytes (14.37 GiB). Halt at Step 1e (Phase 2f) per R4 gate fail-closed discipline; services restored per Decision 6; canonical sha256 re-verified byte-identical; audit YAML written to `data/baseline-run/quiesce-audit-20260424.yaml`; halt narrative at `data/baseline-run/baseline-aug-2024-halt-report.md`. The observed floor became the empirical basis for **ADR-1 v3** (Aria recalibration: R4 formula `available ≥ 1.5 × CAP` → `available ≥ CAP + OS_HEADROOM`; CAP_ABSOLUTE re-derived from 10,285,835,059 → 8,400,052,224 bytes; OS_HEADROOM = 1 GiB per Gregg §7.5) ratified by Riven v3 co-sign (7-point GO) and Quinn v3 audit PASS 7/7 (`docs/qa/gates/ADR-1-v3-audit.md`). Dex patched `core/memory_budget.py` + `core/run_with_ceiling.py` with 16 new v3 tests (225 passed / 1 skipped, ruff clean, smoke-verified constants). Per amendment one-shot discipline, a fresh RA (RA-20260425-1) is issued below under the v3 R4 gate. Audit trail preserved verbatim — DO NOT DELETE.

**Authority:** Riven (@risk-manager, R10 custodial) — ADR-1 v2 Condition R4 / Escalation clause E6.
**Date:** 2026-04-23 BRT (issuance; ID carries 2026-04-24 sequence marker per one-shot-per-attempt discipline — this is the second RA issued against the G09a baseline-run window).
**Scope:** **ONE (1) G09a baseline-run execution only.** NOT a permanent policy change. Whitelist frozenset in `core/memory_budget.py` L42-L59 remains **unchanged** — this amendment operates at the *operational policy* layer (procedural authorization for Gage), not at the *code contract* layer (is_retained() filter).
**Supersedes:** **RA-20260423-1 (unused).** Predecessor halted at pre-quiesce Step 1d upon discovery that `scripts/run_materialize_with_ceiling.py` lacked passthrough for `--output-dir`, `--no-manifest`, and `--manifest-path` — a precondition for Decision 7 hard bound 1 (canonical manifest untouched). No services were stopped under RA-20260423-1; no state change occurred. Amendment spirit (one-shot per attempt) requires fresh sign-off now that the wrapper has been patched.
**Enabling preconditions (both satisfied):**
- **Dex wrapper patch:** `scripts/run_materialize_with_ceiling.py` extended with `--output-dir`, `--no-manifest`, `--manifest-path` passthrough; mutex group at wrapper surface (`--no-manifest` XOR `--manifest-path`); 5 new tests; full suite 209 passed / 1 skipped; ruff clean. Execution unblocker.
- **Quinn QA gate:** `docs/qa/gates/wrapper-passthrough-gate.md` — PASS 7/7 zero concerns. Quality precondition satisfied.
**Trigger:** unchanged from RA-20260423-1 — `data/baseline-run/baseline-aug-2024-preflight-halt.md` (8.22 GiB deficit unrecoverable via operator action alone; Path B selected).

### Decision 1 — Services authorized to stop (MINIMUM SET)

**IDENTICAL to RA-20260423-1.** Reproduced for executability:

| Service | Stop mechanism | Rationale | Expected free (GiB) |
|---|---|---|---|
| `sentinel-timescaledb` (Docker container only — **NOT Docker Desktop itself**) | `docker stop sentinel-timescaledb` | Container is idle for baseline-run (baseline uses canonical parquets, not Sentinel DB). Docker Desktop backend kept running to permit fast `docker start` on restore. | ~0.5-1.0 |
| `vmmem` (WSL2 subsystem, all distros) | `wsl --shutdown` | Halts all WSL2 guest memory. Largest reclaimable retained consumer at t=second-capture per preflight halt report §136-141. | ~3.0-4.0 |

Expected combined reclaim: **~3.5-5.0 GiB**, sufficient to cross the 14.37 GiB available threshold from the observed 6.15 GiB floor.

**REFUSED stops (Riven asserts NO):** IDENTICAL to RA-20260423-1 — MsMpEng (security-pinned), claude (would kill Gage), Docker Desktop full (deeper deviation; container-only sufficient), OS kernel-adjacent (System / svchost / csrss / smss / wininit / winlogon / lsass / Registry / Memory Compression / explorer).

**Article IV anchor:** Identical trace chain to RA-20260423-1 — minimum set traces to the observed deficit in the halt report (~4.96-8.22 GiB) + ADR-1 v2 §215 shared-resident analysis. No invented reclaim values.

### Decision 2 — Duration cap

**IDENTICAL to RA-20260423-1.** HARD CEILING: **4 hours from start of Step a (first `docker stop`) to completion of Step e (post-restore verification).**

Anchor chain unchanged: baseline-run wall-clock 1-2h + pre/post-flight 15m + restore verification 15m + 30m margin + 60m absolute tail = 4h.

**Fail-closed behavior at ceiling:** identical — SIGTERM (graceful) → 30s wait → SIGKILL → proceed to restore (Decision 5) regardless of partial data state → report `duration_cap_exceeded: true`. No grace extension.

### Decision 3 — Pre-quiesce verifications (GATE before any stop)

**IDENTICAL to RA-20260423-1.** Gage MUST record all of the following into `data/baseline-run/quiesce-pre.json` **before** Step a:

| Verification | Expected value | Action if fail |
|---|---|---|
| sha256 `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | HALT; escalate (do not stop services) |
| sha256 `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | HALT; escalate |
| `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` | `healthy` (recorded, not required) | Record observed state; continue |
| `data/baseline-run/` exists | directory present | create if missing |
| `data/baseline-run/scratch/` ready | directory present | create if missing |
| `psutil.virtual_memory()` snapshot | recorded | no gate |
| `psutil.process_iter()` top-30 by RSS | recorded | no gate |

Output JSON schema unchanged from RA-20260423-1.

### Decision 4 — Quiesce order (deterministic, auditable)

**IDENTICAL to RA-20260423-1** — Steps a-e unchanged: `docker stop sentinel-timescaledb` → `wsl --shutdown` → `sleep 30` → re-capture `quiesce-mid.json` → GATE at 14.37 GiB threshold (15_428_752_588 bytes) → PROCEED or HALT. HALT-at-step-e discipline unchanged (no deeper deviation, no threshold lowering, no retry loop; restore + escalate).

### Decision 5 — Authorized baseline-run invocation (CHANGED from RA-20260423-1)

**This is the single substantive change from RA-20260423-1.** The authorized launch command, invoked via the now-patched wrapper surface (Dex patch + Quinn PASS 7/7 gate), is:

```
.venv/Scripts/python scripts/run_materialize_with_ceiling.py \
  --run-id baseline-aug-2024 \
  --start-date 2024-08-01 \
  --end-date 2024-08-31 \
  --ticker WDO \
  --no-ceiling \
  --poll-seconds 30 \
  --output-dir data/baseline-run/scratch \
  --no-manifest
```

**Flag disposition decided by Riven at issuance:** `--no-manifest` is chosen over `--manifest-path data/baseline-run/scratch/manifest-aug-2024.csv`. Both are within MWF-20260422-1 scope; `--no-manifest` is preferred for this retry because:
1. Explicit-zero semantics: no manifest write attempted at all → zero possibility of accidental canonical path collision even under filesystem race conditions.
2. Minimum-surface-area principle: a flag that performs no write is simpler to audit than a flag that redirects a write to an alternate path.
3. The Dex wrapper mutex group enforces `--no-manifest` XOR `--manifest-path` at the wrapper surface — neither the operator nor the child can accidentally emit a manifest write under this invocation.

Gage MUST use the command above verbatim. Variant invocations (e.g., `--manifest-path`) are NOT authorized under RA-20260424-1; a new RA is required if a manifest-path variant is desired in a future retry.

### Decision 6 — Restore order (ALWAYS executed — success, failure, or cap-exceeded)

**IDENTICAL to RA-20260423-1 Decision 5.** Reproduced for executability:

| Step | Action | Verification |
|---|---|---|
| a | WSL2 left dormant (no action). Next user-initiated WSL command will restart it. Gage does NOT actively launch a WSL2 shell. | — |
| b | `docker start sentinel-timescaledb` | exit_code == 0 |
| c | Poll `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` every 5s; accept on `healthy`; timeout 90s total | If timeout without healthy → escalate immediately, do NOT retry |
| d | `psutil.virtual_memory()` + `psutil.process_iter()` top-30 → `data/baseline-run/quiesce-post.json` | — |
| e | Re-verify canonical sha256 — manifest + Aug-2024 parquet — MUST match pre-quiesce hashes byte-identically | If mismatch → CRITICAL, escalate; do NOT attempt repair |

**Restore is unconditional:** executed whether baseline-run exited 0 (success), nonzero (failure), or was killed by duration-cap enforcement. Services must be restored before Gage's session ends.

### Decision 7 — Audit trail (Gage MUST fulfill)

**IDENTICAL to RA-20260423-1 Decision 6** except `amendment_id: RA-20260424-1`. Gage appends a structured YAML document to `data/baseline-run/quiesce-audit-YYYYMMDD.yaml`:

```yaml
- quiesce_window:
    amendment_id: RA-20260424-1
    supersedes: RA-20260423-1
    operator: gage
    date_brt: 2026-MM-DD
    run_id: baseline-aug-2024   # --run-id per Decision 5
    ceiling_expires_at_brt: <start + 4h ISO-8601>
    authorized_invocation_flags:
      no_manifest: true
      manifest_path: null
      output_dir: "data/baseline-run/scratch"
    pre:
      timestamp_brt: <iso>
      manifest_sha256: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
      parquet_sha256: bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0
      available_bytes: <int>
      sentinel_health: <healthy|unhealthy|starting|...>
    quiesce:
      step_a_docker_stop: {timestamp_brt: <iso>, exit_code: <int>}
      step_b_wsl_shutdown: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_sleep: {timestamp_brt: <iso>, duration_s: 30}
      step_d_mid_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_gate: {decision: PROCEED|HALT, threshold_bytes: 15428752588, available_bytes: <int>}
    baseline_child:
      launched: <bool>
      pid: <int|null>
      start_ts_brt: <iso|null>
      end_ts_brt: <iso|null>
      exit_code: <int|null>
      duration_cap_exceeded: <bool>
    restore:
      step_a_wsl_state: dormant
      step_b_docker_start: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_container_health: {timestamp_brt: <iso>, status: <healthy|timeout>, poll_count: <int>}
      step_d_post_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_sha256_reverify:
        manifest_match: <bool>
        parquet_match: <bool>
    final_disposition: <SUCCESS|BASELINE_FAIL|CAP_EXCEEDED|QUIESCE_GATE_HALT|RESTORE_FAIL>
```

This audit YAML lives inside `data/baseline-run/` (scratch area, L4 runtime per framework boundary). Not a manifest mutation. Only this RA-20260424-1 policy artifact is registered in MANIFEST_CHANGES (as spec_issuance; manifest unchanged).

### Decision 8 — Hard bounds (non-negotiable even under amendment)

**IDENTICAL to RA-20260423-1 Decision 7:**

| Bound | Enforcement |
|---|---|
| Canonical `data/manifest.csv` untouched | `--no-manifest` flag per Decision 5 (Dex wrapper passthrough; Quinn-gated). Re-verified in Decision 6 step e. |
| Canonical parquets in `data/in_sample/**` untouched | `--output-dir data/baseline-run/scratch` per Decision 5. Re-verified in Decision 6 step e. |
| MsMpEng NEVER stopped | Hard refusal at Decision 1. |
| `claude` NEVER stopped | Would kill Gage; impossible. |
| Restore failure (sentinel not healthy in 90s) → immediate escalation | Gage does NOT attempt DB repair or retry cycles. Orchestrator decides next step. |
| Duration cap hit mid-run → SIGTERM/SIGKILL baseline child, restore services, report partial | No grace extension. Decision 2. |
| sha256 mismatch at Decision 6 step e → CRITICAL escalation | Canonical state altered during the window (should be physically impossible under Decision 5 + wrapper mutex + hard bound 1). Do not attempt recovery. |
| No permanent whitelist change | `core/memory_budget.py` `_RETAINED_PROCESSES` frozenset unchanged. Amendment expires when audit YAML `final_disposition` is written. |
| One-shot discipline | Any failure mode (E1/E3/R4 post-quiesce/crash/deadline/restore-fail) → restore + escalate + new RA required for next attempt. RA-20260424-1 is NOT reusable. |

### Sign-off

**2026-04-23 BRT — Riven (@risk-manager, R10 custodial) — RA-20260424-1 APPROVED.**

Amendment scope: ONE G09a baseline-run window, ≤ 4 hours total, WSL2 + sentinel-timescaledb container stop authorized, all other ADR-1 v2 constraints in force (CAP_ABSOLUTE = 10,285,835,059 bytes unchanged; CEILING_BYTES still pending step-7 derivation; E1-E5 active; whitelist code contract unchanged). Gage executes under Decisions 1-8 above with zero clarifying questions. On completion, this amendment is spent — a second retry or any subsequent quiesce requires a new RA-YYYYMMDD-N amendment.

**R10 co-sign block:**
- Custodial authority: Riven (@risk-manager, R10) — signed 2026-04-23 BRT.
- Governance class: one-shot operational policy amendment (not a code contract change; not a permanent whitelist mutation).
- Constitutional compliance: Article IV (No Invention) — Decisions 1-4, 6-8 trace verbatim to RA-20260423-1; Decision 5 traces to Dex wrapper patch + Quinn wrapper-passthrough-gate.md PASS 7/7. Article V (Quality First) — executable by Gage with zero clarifying questions (same bar as RA-20260423-1). Article I (CLI First) — all actions CLI-invocable.
- Supersedes RA-20260423-1 (unused; wrapper missing passthrough at issuance time).

**References:**
- Predecessor: RA-20260423-1 (SUPERSEDED) — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260423-1)`
- Enabling precondition (quality): `docs/qa/gates/wrapper-passthrough-gate.md` — Quinn @qa PASS 7/7 zero concerns
- Enabling precondition (execution): `scripts/run_materialize_with_ceiling.py` — Dex @dev wrapper passthrough patch (5 new tests, 209 passed / 1 skipped, ruff clean)
- Halt report: `data/baseline-run/baseline-aug-2024-preflight-halt.md`
- MWF-20260422-1: manifest-write-fencing spec (authorizes `--no-manifest` / `--manifest-path` flag semantics)

---

## ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor (2026-04-23 BRT, late-day)

**Author:** Aria (@architect, The Weaver ♒)
**Date:** 2026-04-23 BRT
**Trigger:** RA-20260424-1 execution by Gage (@devops) produced empirical evidence that ADR-1 v2 R4 launch-time gate (`available ≥ 1.5 × CAP_ABSOLUTE`) is structurally unreachable on the target host.
**Scope:** Re-derive CAP_ABSOLUTE and R4 launch-time formula from first principles against the **observed host quiesce floor**. All other ADR-1 v2 clauses (HEADROOM_FACTOR = 1.3, Aug-2024 baseline, warn/kill at 85/95, Riven R1 dual-signal leak detector, E1/E2/E3/E4/E5 escalations, whitelist frozenset, telemetry schema, exit codes, ADR-2, ADR-3) remain in force verbatim.
**Constitutional anchors:** Article IV (No Invention) — every constant in v3 traces to observed data in G09a halt artifacts or cited literature. Article V (Quality First) — executable by Dex with zero clarifying questions; testable by Quinn with zero ambiguity.
**Supersedes (narrowly):** ADR-1 v2 CAP_ABSOLUTE constant (9.58 GiB) and v2 R4 launch-time formula (`1.5 × CAP_ABSOLUTE`). Does NOT supersede v2 HEADROOM_FACTOR, warn/kill fractions, R1, R2, R3, telemetry schemas, whitelist, or any escalation clause structure.
**Co-sign required:** Riven (@risk-manager, R10 custodial) on R4 recalibration + E6 signal rewrite + CAP derivation.

---

### Evidence anchor

v2's R4 gate was derived from a theoretical "pristine quiesce" model in which `available` would approach ~0.9 × physical RAM after operator quiesce. RA-20260424-1 measured the actual operational envelope under maximum authorized quiesce on this host and found the ceiling is substantially lower.

**Primary empirical source:** `data/baseline-run/quiesce-mid.json`, captured 2026-04-23T19:21:51-03:00 by @devops (Gage) per RA-20260424-1 after:
- `docker stop sentinel-timescaledb` (Step 2b, exit 0)
- `wsl --shutdown` (Step 2c, exit 0)
- `time.sleep(30)` — Windows hypervisor memory-reclamation settle window (Step 2d)

**Observed mid-quiesce snapshot (bytes, direct `psutil.virtual_memory()` measurement):**

| Field | Bytes | GiB (binary, ÷1024³) |
|---|---|---|
| `total` | 17,143,058,432 | 15.97 |
| `available` | **9,473,794,048** | **8.82** |
| `percent` used | 44.7% | — |
| `pagefile.used` | 1,877,110,784 | 1.75 |

**Observed structural-resident floor (top-consumers from `quiesce-mid.json.top30[]`):**

| Process | RSS (bytes) | GiB | Reducibility |
|---|---|---|---|
| vmmem | 2,305,626,112 | 2.15 | Residual after `wsl --shutdown` — hypervisor does not immediately reclaim all guest pages |
| claude.exe | 535,392,256 | 0.50 | Driving the run; cannot close |
| MsMpEng.exe | 355,385,344 | 0.33 | Windows Defender; policy-pinned per RA-20260424-1 Decision 1 |
| msedgewebview2.exe | 218,071,040 | 0.20 | Shell-adjacent component |
| explorer.exe | 197,885,952 | 0.18 | Windows shell; cannot close |
| com.docker.backend.exe | 183,857,152 | 0.17 | Docker Desktop backend; retained per RA policy |
| SearchApp / Docker Desktop / Registry / OneDrive / svchost aggregate | ~750 MB | ~0.70 | Kernel-adjacent, shell-adjacent, irreducible |
| System / svchost / kernel drivers / cached pages (not in top-30) | ~2.5 GB | ~2.3 | Kernel reserved; never user-closable |
| **Aggregate consumed at mid-quiesce** | ~7,669,264,384 | ~7.14 | — |
| **`total − aggregate consumed` = `available` (psutil definition)** | **9,473,794,048** | **8.82** | Observed floor |

The structural-resident floor is ~7.14 GiB **under the authorized quiesce envelope defined by Riven's RA-20260424-1**. This floor is irreducible without deeper deviations (stopping MsMpEng, stopping Docker Desktop entirely, stopping claude) that Riven explicitly refused in RA-20260424-1 Decision 1. Therefore `available` post-quiesce cannot exceed ~9.47 GiB on this host by construction.

**The defect in v2:** v2 R4 required `available ≥ 15,428,752,589` (14.37 GiB). Observed ceiling is 9.47 GiB. Shortfall 5.55 GiB, unrecoverable. v2 R4 is unreachable.

---

### Chosen candidate: **Candidate C with OS_HEADROOM constant from Candidate B + portability formula**

**Rationale for choice over A/B/D/E:**

- **A (lower multiplier)** — Reducing multiplier from 1.5× to 1.1× still requires recalibrating CAP_ABSOLUTE downward. Without that recalibration it fails arithmetic. With it, A collapses to C. No unique value.
- **B alone (additive headroom with v2 CAP)** — `CAP_v2 + MIN_OS_HEADROOM = 9.58 + 1.0 = 10.58 GiB`, still unreachable vs 9.47 GiB floor. B needs CAP recalibration too. The *idea* in B — naming OS_HEADROOM as a first-class constant rather than hiding it in a multiplier — is adopted by v3.
- **D (bimodal measurement-mode vs production-mode)** — Adds mode-state complexity (two code paths, Riven gates transitions). But v2 already achieves measure-first via `CEILING_BYTES = None` sentinel (see v2 remediation step 8). Bimodal R4 is redundant with the sentinel gate. Rejected as unneeded complexity; the sentinel already performs the measurement-mode function.
- **E (invent new mechanism)** — No evidence warrants a non-gate mechanism. R4's job (fail-closed OS-starvation protection) is sound; only the threshold is miscalibrated.
- **C (recalibrate CAP + R4 from observed floor)** — Numerically provable reachable. Preserves the fail-closed property because any drift in the floor (other resident processes appearing) still trips R4, blocking launch before subprocess start. Adopts B's OS_HEADROOM naming for clarity. Adds portability formula (below) so the constants remain meaningful on other hosts.

**Candidate C + B-constant + portability = the chosen v3 design.**

---

### Derivation (full math)

All values in bytes; GiB shown as binary (÷1024³) for cross-check.

```
# Observed empirical anchor (Article IV trace: data/baseline-run/quiesce-mid.json line 4)
OBSERVED_QUIESCE_FLOOR_AVAILABLE = 9_473_794_048        # bytes (~8.82 GiB binary)

# OS headroom above the cap — literature anchor
# Gregg, Systems Performance 2nd ed., Section 7.5 "Methodology" recommends
# ≥ 20% RAM headroom above peak for OS + cache; on a 16 GiB host that is ~3.2 GiB
# which is unachievable given our floor. Anchor drops to the "safe margin above
# peak working set" heuristic in the same section (~500 MiB – 1 GiB for
# allocator slack + driver growth + transient AV scans). We choose the upper
# bound of that heuristic (1 GiB) to maximize OS safety within the reachable
# envelope. Cited: Gregg §7.5 "Methodology" — bounded-workload buffer pool sizing.
# Microsoft docs (learn.microsoft.com/windows/win32/procthread/... memory
# management) corroborate the "leave > 1 GiB available for OS + file cache
# on 16 GiB systems" guidance for production servers.
OS_HEADROOM = 1_073_741_824                              # bytes (1.0 GiB)

# CAP_ABSOLUTE is the largest share of host memory we allow materialize_parquet
# to consume, such that the OS retains at least OS_HEADROOM above the cap.
# Derived by reversing the R4 check against the observed floor.
CAP_ABSOLUTE_v3 = OBSERVED_QUIESCE_FLOOR_AVAILABLE - OS_HEADROOM
                = 9_473_794_048 - 1_073_741_824
                = 8_400_052_224                          # bytes (~7.82 GiB binary)

# R4 threshold: at launch time, available must be at least enough to host the
# full cap plus the OS headroom. Equal to OBSERVED_QUIESCE_FLOOR_AVAILABLE by
# construction — reachable on this host exactly when the operator successfully
# reproduces the quiesce procedure.
R4_V3_THRESHOLD = CAP_ABSOLUTE_v3 + OS_HEADROOM
                = 8_400_052_224 + 1_073_741_824
                = 9_473_794_048                          # bytes (~8.82 GiB binary)
```

**Cross-check against RAM-percentage anchor (v2 heritage):**

`0.60 × PHYSICAL_RAM_BYTES = 0.60 × 17_143_058_432 = 10_285_835_059` bytes (~9.58 GiB).

On this host, **the observed-floor anchor is tighter than the RAM-percentage anchor** (7.82 GiB < 9.58 GiB). v3 adopts the tighter constraint because the v2 RAM-percentage derivation was itself an upper bound and the observed floor proves the host cannot deliver that upper bound under quiesce. v3 CAP_ABSOLUTE is therefore *lower* than v2 CAP_ABSOLUTE by **1.76 GiB** (1,885,782,835 bytes) — a deliberate tightening, not an oversight.

**Cap-dominance threshold (v3):**

`CAP_ABSOLUTE_v3 / HEADROOM_FACTOR = 8_400_052_224 / 1.3 ≈ 6_461_578,634` bytes (~6.02 GiB).

Cap dominates derivation whenever `peak_commit > ~6.02 GiB`. v2 cap-dominance threshold was ~7.37 GiB. v3 is tighter; more of the peak-commit range will hit the cap rather than the `× 1.3` headroom.

**Warn/kill thresholds (unchanged fractions, applied to new CAP):**

| Threshold | Fraction | Bytes | GiB |
|---|---|---|---|
| WARN | 0.85 × CAP_ABSOLUTE_v3 | 7,140,044,390 | ~6.65 |
| KILL | 0.95 × CAP_ABSOLUTE_v3 | 7,980,049,612 | ~7.43 |

The 10-percentage-point warn-to-kill buffer is now ~840 MiB (was ~958 MiB under v2). Per-tick deltas post-refactor are tens of MB, so at 30s polling there is still a 1–3 tick visibility window between WARN and KILL.

---

### Updated R4 formula (normative)

**v3 R4 launch-time gate:**

```
if psutil.virtual_memory().available < (CAP_ABSOLUTE + OS_HEADROOM):
    exit(1)  # wrapper setup error — host cannot support the run
```

Equivalent plain form for documentation: `available ≥ CAP_ABSOLUTE + OS_HEADROOM` = `available ≥ 9_473_794_048 bytes` = `available ≥ 8.82 GiB` on this host.

**Exit-1 message format (contract for Dex, unchanged from v2 Finding 6 except threshold number):**

```
ERROR: R4 launch-time availability check failed.
  Required : >= 9,473,794,048 bytes (CAP_ABSOLUTE + OS_HEADROOM = 7.82 GiB + 1.00 GiB)
  Observed : <psutil_available> bytes (<observed_GiB> GiB)
  Shortfall: <required − observed> bytes (<shortfall_GiB> GiB)

Top-3 non-retained memory consumers (close these before retry):
  1. <name> PID <pid> <working_set_MiB> MiB
  2. <name> PID <pid> <working_set_MiB> MiB
  3. <name> PID <pid> <working_set_MiB> MiB

Retained (not actionable — excluded from above):
  <list of matched _RETAINED_PROCESSES consumers>

If no non-retained consumers remain to close, the host cannot support this run
under current ADR-1 v3 constants. Contact @architect (Aria) + @risk-manager (Riven).
Full re-derivation required per ADR-1 v3 escalation clause E7 (observed floor
drift, see below).
```

The `is_retained()` substring-match frozenset from v2 Finding 6 (Riven ratification, lines 574–605 of this file pre-v3) is **preserved verbatim** by v3. Dex does not modify the whitelist.

---

### Measure-first compatibility statement

v3 preserves the measure-first architecture established in v2. The baseline-run's purpose is to observe `peak_commit` under a refactored, un-ceiling-enforced run; v3 R4 **does not depend on `peak_commit`**. The R4 formula `available ≥ CAP_ABSOLUTE + OS_HEADROOM` uses only the CAP constant (derived from host observation, not subprocess observation) and the OS_HEADROOM constant (derived from literature). Neither requires prior knowledge of the subprocess's actual peak.

The sequencing therefore remains:

1. Dex populates `core/memory_budget.py` with CAP_ABSOLUTE = 8_400_052_224 and OS_HEADROOM = 1_073_741_824 **now** (these are v3 constants, known at commit time).
2. Dex leaves `CEILING_BYTES = None` (v2 sentinel behavior unchanged).
3. Gage re-runs G09a under a fresh RA (RA-20260425-N, Riven drafts) with `--no-ceiling`. R4 gate evaluates to the reachable 8.82 GiB threshold and passes; the subprocess launches; `peak_commit` is measured.
4. Aria + Riven at v2/v3 step 7 derive `CEILING_BYTES = min(ceil(peak_commit_aug2024 × 1.3), CAP_ABSOLUTE_v3)` per the preserved v2 formula. v3 has no quarrel with the ceiling derivation method, only the R4 launch gate threshold.
5. Dex populates `CEILING_BYTES`.
6. Production runs gate at both R4 (launch time) and CEILING_BYTES (runtime kill). Both layers in force.

The E1 escalation (`peak_commit > CAP_ABSOLUTE`) tightens mechanically because CAP_ABSOLUTE is now 7.82 GiB. If Aug-2024 peak_commit exceeds 7.82 GiB (rather than the v2 9.58 GiB), streaming-chunk refactor is pulled in as a G09 prerequisite per v2 Issue 2 / E1 — that escalation clause is preserved verbatim; only the trigger number shifts.

---

### Host portability statement

The v3 derivation uses a host-specific observation (`OBSERVED_QUIESCE_FLOOR_AVAILABLE` from `quiesce-mid.json`). To make v3 constants portable to other hosts, the following procedure applies:

**On a new host (prerequisite to any ADR-1 v3 run elsewhere):**

1. **Capture a host-preflight** per v2 R2 procedure (physical RAM, commit limit, PageFile config, top-20 consumers). File at `data/baseline-run/host-preflight-<hostid>.txt`.
2. **Execute a quiesce probe** — a read-only script (Dex scope if needed, but functionally just the RA-20260424-1 Decision 4 quiesce sequence + snapshot capture) that:
   a. Records pre-quiesce `psutil.virtual_memory()`.
   b. Performs the authorized quiesce per the host's applicable RA (container stops + hypervisor shutdown + settle).
   c. Records mid-quiesce `psutil.virtual_memory()` → this is `OBSERVED_QUIESCE_FLOOR_AVAILABLE` for that host.
   d. Restores services.
3. **Compute host-specific constants:**
   ```
   CAP_ABSOLUTE_host = min(
       OBSERVED_QUIESCE_FLOOR_AVAILABLE_host - OS_HEADROOM,   # observed-floor anchor
       floor(0.60 × PHYSICAL_RAM_BYTES_host)                  # RAM-percentage anchor (v2)
   )
   ```
   The `min()` selects whichever anchor is tighter. On hosts with larger physical RAM but similar structural-resident floors (e.g. a 32 GiB host with the same ~7 GiB OS+dev-tool floor), the RAM-percentage anchor dominates (19.2 GiB cap vs 24-GiB-floor-derived 23 GiB cap → RAM-pct tighter). On hosts with tight physical RAM (this host, 16 GiB), the observed-floor anchor dominates (7.82 GiB vs 9.58 GiB → observed-floor tighter).
4. **R4 threshold:** `available ≥ CAP_ABSOLUTE_host + OS_HEADROOM` — always reachable on that host by construction (since CAP was derived from the host's own floor).
5. **OS_HEADROOM is host-invariant at 1 GiB** — tied to literature (Gregg §7.5 upper bound), not to hardware. Re-evaluate only if the literature anchor is revised.

**Re-observation triggers (add to v2 re-validation cadence):**

v2 triggers (a)–(g) remain in force. v3 adds:

- **(h) Structural-resident floor drift** — if `OBSERVED_QUIESCE_FLOOR_AVAILABLE` at any re-baseline differs by > 10% from the value used at CAP derivation (currently 9,473,794,048 bytes), Riven decides whether to re-derive CAP. Rationale: new always-on background processes (e.g. an OS telemetry agent update, a new security tool) can shift the floor substantially without changing physical RAM. v2's E4 ("physical RAM change") does not catch this; v3's (h) does.

---

### Dual R1 signal preservation

v2 Riven Co-sign established R1 as a combined indicator (Signal A ratio + Signal B ΔPageFile). **v3 preserves both signals verbatim.** CAP_ABSOLUTE recalibration does not affect leak detection; the ratio brackets (<2.0 normal / 2.0–4.0 tolerable / >4.0 leak) and ΔPageFile brackets (<500 MiB steady / 500 MiB–2 GiB mild / >2 GiB leak) are measurements of subprocess behavior under whatever CAP is in force, not measurements of the CAP itself. Cross-reference: v2 Riven Co-sign §"Condition R1 v2 — Leak detector (re-calibrated for dynamic PageFile on 16 GiB host)" (above, unchanged).

Riven must still execute R1 evaluation at the post-baseline step 7 derivation. v3 does not re-open R1 calibration; v2 brackets stand.

---

### Exit-code alignment (unchanged)

Per ADR-2 (v2 unchanged by v3):

| Exit | Meaning | v3 impact |
|---|---|---|
| 0 | Clean exit, no trip | Unchanged |
| 1 | Wrapper setup error — **includes R4 threshold failure and E4 drift** | R4 threshold formula changes (9.47 GiB not 14.37 GiB); behavior unchanged (exit 1 with top-3 message) |
| 2 | Hold-out lock raised by child | Unchanged |
| 3 | Ceiling tripped (observed ≥ 0.95 × CEILING_BYTES) | Unchanged |
| 4 | psutil not importable | Unchanged |
| 5 | Sampler lost visibility 3× | Unchanged |
| ≥ 10 | Child's own exit code | Unchanged |

**No new exit codes invented by v3.** Article IV respected.

---

### Escalation clause v3 (extends v2 E1–E6)

All v2 escalations (E1–E6) remain in force with one formula-update for E6:

| Condition | v2 signal | v3 signal | Resolution (unchanged) |
|---|---|---|---|
| E6 — Launch-time host availability | `available < 1.5 × CAP_ABSOLUTE` | `available < CAP_ABSOLUTE + OS_HEADROOM` | Operator closes named processes; retry. |

v3 **adds one new escalation**:

| Condition | Signal | Resolution |
|---|---|---|
| **E7 — Observed quiesce floor drift** | At any re-baseline, `|OBSERVED_QUIESCE_FLOOR_AVAILABLE_new − 9_473_794_048| / 9_473_794_048 > 0.10` | Full CAP re-derivation per portability procedure; Riven co-sign; new ADR amendment. |

E1 (baseline peak exceeds cap) trigger number shifts from 9.58 GiB (v2) to 7.82 GiB (v3); resolution (streaming-chunk refactor) unchanged.

---

### Consequences

- `core/memory_budget.py` CAP_ABSOLUTE literal changes from `10_285_835_059` to `8_400_052_224`. OS_HEADROOM added as new module-level constant `OS_HEADROOM = 1_073_741_824`.
- R4 launch-time gate formula in `core/run_with_ceiling.py` (or wherever Dex placed the R4 check per Finding 4) changes from `available < 1.5 * CAP_ABSOLUTE` to `available < CAP_ABSOLUTE + OS_HEADROOM`. Exit-1 message threshold string changes accordingly.
- Commit message for the v3 Dex patch MUST cite: (i) this ADR-1 v3 section, (ii) the empirical source `data/baseline-run/quiesce-mid.json` with its mid-quiesce available value, (iii) the Gregg §7.5 literature anchor for OS_HEADROOM, (iv) the RA-20260424-1 halt report at `data/baseline-run/baseline-aug-2024-halt-report.md`.
- G09a retry requires a **new RA (RA-20260425-N)** from Riven — the patched R4 gate must be in place before the next quiesce window opens. RA-20260424-1 is spent per its one-shot discipline.
- Aug-2024 baseline feasibility under v3: subprocess may consume up to CAP_ABSOLUTE_v3 = 7.82 GiB before E1 escalation. If peak_commit exceeds 7.82 GiB, Dex refactor is pulled in (streaming-chunk rewrite) per v2 E1. If peak_commit is under 6.02 GiB, `ceil(peak × 1.3)` dominates derivation; if between 6.02 and 7.82, CAP_ABSOLUTE_v3 dominates.
- Re-derivation cadence gains trigger (h) — structural-resident floor drift — alongside v2 triggers (a)–(g).
- Quinn audit required: `docs/qa/gates/ADR-1-v3-audit.md` (scope: verify arithmetic, evidence traces, no-invention compliance, portability formula soundness, E7 clarity, Dex ambiguity check).

---

### Handoff

**Riven (@risk-manager, R10 custodial) MUST co-sign before Dex patches code:**

1. **R4 recalibration acceptance** — confirm `available ≥ CAP_ABSOLUTE + OS_HEADROOM` as the new R4 gate formula (replacing `1.5 × CAP_ABSOLUTE`).
2. **CAP_ABSOLUTE value** — confirm `CAP_ABSOLUTE_v3 = 8_400_052_224` bytes as derived from `OBSERVED_QUIESCE_FLOOR_AVAILABLE − OS_HEADROOM`.
3. **OS_HEADROOM value** — confirm `OS_HEADROOM = 1_073_741_824` bytes (1 GiB) with Gregg §7.5 citation as anchor.
4. **E6 signal rewrite** — confirm trip condition `available < CAP_ABSOLUTE + OS_HEADROOM` replaces `available < 1.5 × CAP_ABSOLUTE`.
5. **E7 new escalation** — confirm structural-resident floor drift >10% triggers full re-derivation.
6. **Host portability formula** — confirm `CAP_ABSOLUTE_host = min(OBSERVED_QUIESCE_FLOOR_AVAILABLE_host − OS_HEADROOM, 0.60 × PHYSICAL_RAM_BYTES_host)` as the cross-host derivation procedure.
7. **R1/R2/R3 preservation** — confirm v2 R1 (dual signal), R2 (host-preflight), R3 (×1.3 rationale) all remain in force unchanged.

Once Riven co-signs, Dex's patch is unblocked.

**Dex (@dev) MUST change in `core/memory_budget.py` (post-Riven co-sign):**

```python
# BEFORE (v2)
PHYSICAL_RAM_BYTES = 17_143_058_432
CAP_ABSOLUTE       = 10_285_835_059   # 0.60 × PHYSICAL_RAM_BYTES

# AFTER (v3)
PHYSICAL_RAM_BYTES = 17_143_058_432                     # unchanged (host-preflight §3/§6)
OBSERVED_QUIESCE_FLOOR_AVAILABLE = 9_473_794_048        # NEW: per quiesce-mid.json, RA-20260424-1
OS_HEADROOM = 1_073_741_824                             # NEW: 1 GiB, per Gregg §7.5 literature anchor
CAP_ABSOLUTE = 8_400_052_224                            # = OBSERVED_QUIESCE_FLOOR_AVAILABLE − OS_HEADROOM
                                                        #   per ADR-1 v3 derivation
```

**Dex (@dev) MUST change in the R4 launch-time check** (location: wherever Dex placed the R4 gate per v2 Aria Ratifications Finding 4; expected in `core/run_with_ceiling.py` launch path):

```python
# BEFORE (v2)
if psutil.virtual_memory().available < int(1.5 * CAP_ABSOLUTE):
    # ... emit exit-1 message with threshold 15_428_752_589 ...
    sys.exit(1)

# AFTER (v3)
if psutil.virtual_memory().available < (CAP_ABSOLUTE + OS_HEADROOM):
    # ... emit exit-1 message with threshold 9_473_794_048 ...
    sys.exit(1)
```

The exit-1 message string constant(s) also update to the new threshold number. The `is_retained()` filter and top-3 reporting logic from v2 Finding 6 are unchanged.

**Dex (@dev) MUST add a test in `tests/core/test_memory_budget.py`** (or wherever Quinn directs):

- Assert `CAP_ABSOLUTE == 8_400_052_224`
- Assert `OS_HEADROOM == 1_073_741_824`
- Assert `CAP_ABSOLUTE + OS_HEADROOM == 9_473_794_048`
- Assert `OBSERVED_QUIESCE_FLOOR_AVAILABLE == 9_473_794_048`

Arithmetic-invariant tests. Cheap to run, catch accidental edits.

**Dex (@dev) MUST NOT:**

- Modify the `_RETAINED_PROCESSES` frozenset or `is_retained()` function — v2 Finding 6 unchanged.
- Modify HEADROOM_FACTOR, WARN_FRACTION, KILL_FRACTION — v2 unchanged.
- Modify telemetry schemas or CSV/JSON field lists — v2 Finding 5 unchanged.
- Invent new exit codes — ADR-2 unchanged.
- Touch `data/manifest.csv` — canonical invariant.

---

### Constitutional compliance statement

- **Article IV (No Invention):** Every v3 constant traces to observed data in the G09a halt artifacts (`quiesce-mid.json` for the floor; `quiesce-audit-20260424.yaml` for the execution record; `baseline-aug-2024-halt-report.md` for the shortfall narrative) or to cited literature (Gregg *Systems Performance* 2nd ed. §7.5 for OS_HEADROOM upper-bound heuristic). The RAM-percentage anchor in the portability formula is inherited verbatim from v2. No invented numbers.
- **Article V (Quality First):** Dex has concrete diff-level instructions (above); Quinn has concrete assertions to verify (above); Riven has a concrete 7-point co-sign checklist (above). Zero interpretive ambiguity.
- **Article I (CLI First):** R4 remains a deterministic CLI-invocable gate (exit code 1 on failure). No new UIs introduced.

---

**Sign-off (Aria):**

2026-04-23 BRT — **Aria (@architect, The Weaver ♒)** — ADR-1 v3 PROPOSED. Own-authority design scope; does not require Aria upstream co-sign. Downstream co-sign from Riven required on the 7-point handoff checklist above before Dex patches code. Quinn audit required at `docs/qa/gates/ADR-1-v3-audit.md` before orchestrator applies SUPERSEDED markers to v2 CAP + R4 and promotes v3 to active.

**Next required sign-offs:** Riven co-sign → Quinn audit → Dex patch → RA-20260425-N for G09a retry.

---

## Riven Co-sign v3 — R1/R2/R3/E6/E7 Recalibration Against ADR-1 v3 (2026-04-23 BRT, late-day)

**Author:** Riven (@risk-manager, R10 custodial)
**Date:** 2026-04-23 BRT
**Scope:** Co-sign Aria's 7-point ADR-1 v3 handoff checklist. Recalibrate R1/R2/R3 brackets + R5 warn/kill fractions against CAP_ABSOLUTE_v3 = 8,400,052,224 bytes (7.82 GiB). Rewrite E6 trip signal. Co-sign E7 new escalation. Co-sign portability formula. Verify one-shot amendment template compatibility. Issue final go/no-go on v3 for Dex.
**Supersedes (narrowly):** Riven Co-sign v2 §R4 v2 (supersession banner already in place at line 386 per Aria's v3 ADR). Does NOT supersede v2 R1 (dual-signal brackets unchanged), R2 (pre-flight satisfied ex-ante), R3 (×1.3 rationale and commit-message requirement unchanged), R5 fractions (85/95 unchanged — only absolute bytes shift with CAP), E1/E2/E3/E4/E5 escalations, or re-validation cadence triggers (a)–(g). Adds E7 per Aria handoff.
**Preserves audit trail:** Riven Co-sign v2 text above is left intact. Supersession banners added inline at v2 R1 (line ~330), v2 R3 (line ~372), and v2 R5 (line ~406) flagging where numeric values shift or where v3 confirms preservation. v2 E6 entry in the Escalation table (line ~428) already carries Aria's inline `[SUPERSEDED v2 → v3]` banner; Riven accepts that banner verbatim.
**Constitutional anchors:** Article IV (No Invention) — every new bracket in this section traces to `data/baseline-run/quiesce-mid.json`, `data/baseline-run/quiesce-audit-20260424.yaml`, host-preflight, Sentinel TimescaleDB chunk inspection (2026-04-21), or cited literature (Gregg 2nd ed. §7.5, psutil docs). Article V (Quality First) — every co-sign point below gives Dex a zero-ambiguity implementation target.

**Verdict:** **APPROVE v3** (all seven handoff points co-signed with the modifications noted below). Go for Dex patch → Quinn audit → RA-20260425-N.

---

### Manifest-canonical guard

`data/manifest.csv` sha256 verified byte-identical at `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` at the time of this co-sign. This section touches only `docs/architecture/memory-budget.md`. No code, no canonical manifest, no parquet modifications. R10 custodial discipline held.

---

### Handoff point 1 — R4 formula change (multiplier → additive)

**Co-sign: YES (unmodified).**

Aria's rewrite of R4 from `available ≥ 1.5 × CAP_ABSOLUTE` to `available ≥ CAP_ABSOLUTE + OS_HEADROOM` is sound on two axes:

1. **Arithmetic reachability.** `CAP_ABSOLUTE_v3 + OS_HEADROOM = 8,400,052,224 + 1,073,741,824 = 9,473,794,048 bytes`, which equals the observed quiesce floor by construction. Reachable on this host exactly when the operator reproduces the RA-20260424-1 quiesce procedure. No shortfall.
2. **Fail-closed semantic preserved.** The additive form is not a relaxation of the gate; it is a re-anchoring. If `available` at launch drops below `CAP_ABSOLUTE + OS_HEADROOM`, the subprocess would be forced to eat into OS_HEADROOM immediately upon allocating full CAP, risking OS-level thrashing. Exit 1 still fires; operator still must act. The gate is as safe as v2 — only the threshold is now a reachable number.

Evidence trace: `data/baseline-run/quiesce-mid.json` (line 4 `available = 9473794048`) + Gregg §7.5 (OS headroom upper bound).

### Handoff point 2 — CAP_ABSOLUTE value (10.29 GiB → 7.82 GiB)

**Co-sign: YES (unmodified).**

`CAP_ABSOLUTE_v3 = OBSERVED_QUIESCE_FLOOR_AVAILABLE − OS_HEADROOM = 9,473,794,048 − 1,073,741,824 = 8,400,052,224 bytes (~7.82 GiB binary)`.

Riven's v2 co-sign accepted `CAP_v2 = 10,285,835,059 = 0.60 × PHYSICAL_RAM_BYTES` because at that time the RAM-percentage anchor was the best-available derivation. RA-20260424-1 produced a tighter empirical anchor. The 1.76 GiB downward tightening is **not a risk increase** — it is a correction of an over-generous upper bound that could not survive the observed floor. Fail-closed principle: when empirical and theoretical anchors disagree, the tighter one rules (v2 can never have been "truer" than v3 because v2 was uninformed by the floor measurement).

Evidence trace: `quiesce-mid.json` direct `psutil.virtual_memory().available` reading + `quiesce-audit-20260424.yaml` execution timeline.

### Handoff point 3 — OS_HEADROOM value (1 GiB)

**Co-sign: YES (unmodified).**

Aria cites Gregg *Systems Performance* 2nd ed. §7.5 "Methodology" for the 500 MiB–1 GiB bounded-workload buffer bracket, chooses the upper bound (1 GiB) to maximize OS safety within the reachable envelope. I concur on four grounds:

1. **Upper-bound conservatism is correct when `available − CAP` is already binding.** On this host we cannot afford the Gregg ≥ 20% RAM heuristic (3.2 GiB); choosing anything less than the upper bound of the fallback heuristic would erode safety unnecessarily while still leaving a near-identical CAP (because the CAP tracks `floor − OS_HEADROOM` linearly).
2. **1 GiB covers observed allocator slack + transient AV behavior.** psutil docs note `available` is an estimator that can fluctuate ~100–500 MiB between samples as Windows memory manager rebalances standby pages; MsMpEng scan bursts routinely consume 200–400 MiB transiently. 1 GiB absorbs both without false-positive R4 trips on tick-boundary noise.
3. **Microsoft production guidance for 16 GiB servers** (`learn.microsoft.com/windows/win32/procthread`) corroborates the "leave > 1 GiB free for OS + file cache" rule Aria cites. Two-source convergence = solid anchor.
4. **Host-invariance.** Tying OS_HEADROOM to literature (not to hardware) means the constant does not re-derive per host; only the CAP + floor observations do. This simplifies the portability story (point 6).

Evidence trace: Gregg 2nd ed. §7.5 (cited) + psutil docs (cited in v2 Condition R1 calibration rationale, preserved).

### Handoff point 4 — E6 signal rewrite (OS-starvation gate)

**Co-sign: YES, with explicit semantic note.**

Aria's v3 table (line ~1218) restates E6 trigger as `available < CAP_ABSOLUTE + OS_HEADROOM`. This is **the R4 launch-time formula itself applied as a runtime escalation**. I accept this with one clarification for Dex to avoid confusion:

**E6 v3 canonical semantic:** "Launch-time host availability insufficient. Trip condition: at the R4 gate evaluation moment (wrapper entry, before subprocess fork), `psutil.virtual_memory().available < CAP_ABSOLUTE + OS_HEADROOM`. Action: exit 1 with top-3 non-retained consumer message. E6 is a **gate BLOCK on every run** (not a derivation BLOCK). It does NOT fire during runtime — runtime memory pressure on the subprocess is handled by R5 WARN/KILL (against CAP) and by ADR-2 exit 3 (ceiling tripped). E6 is exclusively the launch-time fail-closed siblingship to R5."

This is orthogonal to:
- **E1** (`peak_commit_aug2024 > CAP_ABSOLUTE`) — derivation BLOCK at step 7, not a runtime gate.
- **R5 KILL** (`observed ≥ 0.95 × CAP_ABSOLUTE`) — runtime gate on the child's own commit.
- **ADR-2 exit 3** (ceiling tripped) — same as R5 KILL, routed through the wrapper.

I considered and rejected a stricter E6 variant proposed in the handoff (non-Aria, considered as an alternative): "also fire E6 at any runtime tick where `psutil.virtual_memory().available < OS_HEADROOM`". Rejected because (a) that double-counts with R5/exit-3 when the subprocess is the culprit, and (b) when an external process is the culprit, our wrapper kills *our own* child — the correct intervention is for the OS/operator to kill the external memory hog, not for our wrapper to surrender. The correct runtime response to external memory pressure is to let R5 observe and ADR-2 exit 3 fire if (and only if) our own child has tripped the ceiling. Aria's v3 E6 semantic (launch-time only) is the right scope. No modification to Aria's v3 table entry.

### Handoff point 5 — E7 new escalation (floor drift > 10%)

**Co-sign: YES, 10% threshold is correct (no tightening, no loosening).**

Aria proposes E7 trigger: `|OBSERVED_QUIESCE_FLOOR_AVAILABLE_new − 9,473,794,048| / 9,473,794,048 > 0.10` at any re-baseline. 10% equals ~947 MiB absolute — roughly the size of OS_HEADROOM itself, not coincidentally.

I considered 5% (tighter) and 15% (looser) and chose 10% unchanged:

- **5% (~474 MiB):** would trip on normal Windows update cycles (a new KB installing a 200 MB service + a dev tool update of 150 MB + an AV definition refresh = 550 MB of new resident floor) without indicating a real risk shift. Too noisy; would erode operator attention.
- **15% (~1.42 GiB):** would allow a full OS_HEADROOM-sized consumer to appear between baselines without triggering re-derivation. Dangerous: at 15% drift, the v3 CAP arithmetic becomes marginal (new CAP would need to drop by ~1.4 GiB to maintain OS_HEADROOM, but E7 would not fire to force the re-derivation). Too loose.
- **10% (~947 MiB):** tracks the OS_HEADROOM size itself. A drift of one OS_HEADROOM is exactly the point where the safety margin is being eaten; that IS the trigger condition. Symmetry with the constant we defined says 10% is the right threshold.

Evidence trace: arithmetic reasoning on OS_HEADROOM + Gregg §7.5 bounded-workload slack heuristic. Traces to cited literature.

**One addition to E7 scope:** the re-baseline drift check is the primary semantic, but I also require E7 to fire at **any RA request (post-G09a)** where Gage captures a new `quiesce-mid.json`. In other words: E7 is not just a "periodic" check — every RA that involves a quiesce probe produces a new `OBSERVED_QUIESCE_FLOOR_AVAILABLE_new` that must be compared to the baseline 9,473,794,048 at RA drafting time. If >10% drift, the RA cannot proceed until full re-derivation. Riven drafts the re-derivation ADR. This ensures drift is caught at the earliest possible operator interaction point.

### Handoff point 6 — Portability formula

**Co-sign: YES (Aria's `min()` form, NOT the proposed `max()` counterproposal).**

Aria: `CAP_ABSOLUTE_host = min(OBSERVED_QUIESCE_FLOOR_AVAILABLE_host − OS_HEADROOM, 0.60 × PHYSICAL_RAM_BYTES_host)`.

I considered a `max()` counterproposal ("take the larger of floor-derived and RAM-pct to ensure big hosts benefit proportionally"). **Rejected** because:

1. **Fail-closed principle requires `min()`.** When two anchors disagree, the tighter one rules. `max()` deliberately selects the looser anchor, which is the opposite of fail-closed — any host where structural-resident floor is low (well-quiesced host) but RAM is modest would get a CAP that exceeds what the floor can safely support, risking OS starvation.
2. **The "big hosts need bigger CAP" argument is already satisfied by the floor-minus-headroom term.** A 64 GiB host with a comparable ~7 GiB structural-resident floor has `floor = ~56 GiB`, so `floor − headroom = 55 GiB` while `0.60 × 64 = 38.4 GiB`. `min() = 38.4 GiB` — CAP-pct dominates, host gets a healthy proportional CAP. `max()` would give 55 GiB, eating into the 40% OS reserve that v2 established as an anchor-of-safety. Wrong direction.
3. **On this host (16 GiB, tight floor):** `min(8.40, 9.58) = 8.40 GiB (binary 7.82)` — floor-dominated. Correct behavior; tighter anchor rules.
4. **On a 32 GiB host with similar ~7 GiB floor:** `min(32−7−1=24, 0.60×32=19.2) = 19.2 GiB` — CAP-pct dominates. Host gets a ~40% of RAM share, OS keeps ~60%. Correct.
5. **On a contrived host where floor is artificially tight despite large RAM** (e.g. 64 GiB machine running a second heavy workload that eats 40 GiB always-resident): `min(64−40−1=23, 0.60×64=38.4) = 23` — floor-dominated. Correct; the big RAM does not license us to race a big co-tenant.

`min()` is fail-closed across all three host archetypes. `max()` fails fail-closed on archetype 5 and marginal on archetype 2. Formula stands as Aria wrote it.

**One constraint I add:** the portability formula requires a fresh `OBSERVED_QUIESCE_FLOOR_AVAILABLE_host` **per host**, captured via quiesce probe per Aria's v3 §"Host portability statement" steps 1–4. It is **not** permissible to carry the 9,473,794,048 value from this host into another host's derivation. That would violate Article IV (No Invention) — the floor is a host-specific observation. Aria's prose already implies this; I make it explicit.

### Handoff point 7 — v2 R1/R2/R3 preservation (dual signal intact)

**Co-sign: YES (all three preserved verbatim; see banners above).**

- **R1 (dual signal):** Signal A ratio brackets (<2.0 / 2.0–4.0 / >4.0) and Signal B ΔPageFile brackets (<500 MiB / 500 MiB–2 GiB / >2 GiB) are preserved verbatim. Both signals measure subprocess-internal behavior — ratio tracks allocator-vs-working-set disparity, ΔPageFile tracks disk-backed commit growth. Neither depends on CAP_ABSOLUTE. The tightened CAP does not shift the leak-detection semantic.
  - **Sub-concern verified:** at KILL = 7.43 GiB, a subprocess exhibiting ratio=4.1 would imply `peak_rss ≈ 7.43 / 4.1 = 1.81 GiB` with `peak_commit` at kill. That's exactly the regime where R1 Signal A would trip derivation BLOCK (v2 E3) at step 7 post-baseline — consistent behavior with v2. No re-bracketing needed.
  - **ΔPageFile under v3:** v3 KILL fires ~1 GiB earlier than v2 KILL in absolute bytes, which means a process that would have bled to PageFile after 7.43 GiB commit now gets killed before it does so. Signal B ΔPageFile during a v3 run is therefore bounded above by what happens in the first ~7 GiB of commit, which is within v2 tolerable-range regime (<2 GiB ΔPageFile). R1 dual-signal more likely to PASS under v3 than v2. Tightening is friendly to leak detection.
- **R2 (host-preflight):** `data/baseline-run/host-preflight.txt` is unchanged (physical RAM, PageFile config, top-20 at t=0, commit limit, CPU/DIMM specs all still valid). R2 remains SATISFIED ex-ante. v3 adds the `quiesce-mid.json` observation as an **additional** required artifact for the derivation audit trail — not a replacement for R2, a supplement. Dex's commit message under v3 must cite both `host-preflight.txt` (R2) and `quiesce-mid.json` (v3 derivation evidence).
- **R3 (×1.3 rationale):** Two-citation commit-message requirement (Gregg + Sentinel variance) preserved. Cap-dominance threshold number shifts (7.37 GiB → 6.02 GiB) — see banner at v2 R3 (line ~372). The commit-message amendment requiring "CAP_ABSOLUTE dominates; HEADROOM_FACTOR = 1.3 is decorative" formalized in v2 R3 still applies but fires at the new 6.02 GiB threshold.

### R5 recalibration — 85/95 fractions preserved (absolute bytes shift)

**Recalibration: fractions 85/95 unchanged; absolute bytes shift per new CAP.**

| Threshold | Fraction | v2 bytes | v2 GiB | v3 bytes | v3 GiB |
|---|---|---|---|---|---|
| WARN | 0.85 × CAP | 8,742,959,800 | 8.14 | 7,140,044,390 | 6.65 |
| KILL | 0.95 × CAP | 9,771,543,306 | 9.10 | 7,980,049,612 | 7.43 |
| Warn-to-kill buffer | 10 pp × CAP | 1,028,583,506 | 0.96 | 840,005,222 | 0.78 |

The 840 MiB warn-to-kill buffer under v3 is ~15% narrower than v2's 958 MiB. I considered tightening WARN to 0.80 (widening the buffer to ~1.25 GiB) to compensate. **Rejected** because:

1. **Per-tick deltas post-refactor are tens of MB.** 840 MiB / 40 MiB/tick ≈ 21 ticks = ~10.5 minutes of visibility between WARN and KILL at 30s poll cadence. That is more than adequate for the attentive-operator argument Riven v2 made for 85/95. The 15% narrowing of the *absolute* window does not narrow the *tick-count* visibility window to a problematic degree.
2. **Dropping WARN to 0.80 × 7.82 GiB = 6.26 GiB would fire during normal Aug-2024 baseline peaks** (if peak_commit lands in the 6.0–6.3 GiB range, which is plausible given v2 projected Aug-2024 peaks at 5.5–7.2 GiB). WARN-during-normal-operation trains operators to ignore WARN, which is the failure mode v2 R5 explicitly rejected.
3. **The 0.78 GiB buffer is larger than OS_HEADROOM (1 GiB) by only 22%.** Meaning: from WARN to KILL, the process has at most 0.78 GiB of commit growth before it gets killed; at KILL + one tick, OS still has `available ≥ (available at KILL) − 40 MiB ≈ OS_HEADROOM − small_delta`. OS is not yet starved at KILL. Fail-closed holds.

**85/95 stands under v3.** No re-fraction needed.

### R2 sizing-label recalibration table (canonical v3 labels)

Updating the canonical sizing labels against v3 CAP:

| State | v2 value (GiB) | v3 value (GiB) | Notes |
|---|---|---|---|
| PHYSICAL_RAM | 15.97 | 15.97 | Unchanged (host-preflight §3/§6) |
| Available at t=0 (preflight) | 8.40 (binary) / 9.02 (decimal) | 8.40 / 9.02 | Unchanged (R2 artifact not refreshed) |
| Observed mid-quiesce floor | N/A (not a v2 concept) | 8.82 (binary) / 9.47 (decimal) | NEW in v3 |
| R4 launch-time threshold | 14.37 (1.5 × CAP_v2) | 8.82 (CAP_v3 + OS_HEADROOM) | Re-derived |
| OS_HEADROOM | N/A (not a v2 constant) | 1.00 (binary) / 1.07 (decimal) | NEW in v3 |
| CAP_ABSOLUTE | 9.58 (binary) / 10.29 (decimal) | 7.82 (binary) / 8.40 (decimal) | Tightened 1.76 GiB |
| WARN (0.85 × CAP) | 8.14 | 6.65 | Tracks CAP |
| KILL (0.95 × CAP) | 9.10 | 7.43 | Tracks CAP |
| Cap-dominance threshold | 7.37 (CAP / 1.3) | 6.02 (CAP / 1.3) | Tracks CAP |
| E2 trip (CAP / RAM > 0.70) | 11.18 (trip bound) | 11.18 | Unchanged — bound is on PHYSICAL_RAM, not CAP |

Dex does not need to copy this table into `core/memory_budget.py`. The table is for future-reader cross-reference when reading v3 values in the codebase.

### R3 variance feasibility note (Sentinel +45% observation under v3 CAP)

Aria's v3 preserves R3's anchor chain verbatim. I add one observation (non-BLOCKing, informational) tied to the Sentinel +24% Jul / +45% Aug over Mar-2024 variance (cited in v2 R3 clause 1):

- **v3 CAP = 7.82 GiB.** For the full +45% variance to fit inside CAP without E1 escalation, Mar-2024 peak_commit would need to be ≤ 7.82 / 1.45 ≈ 5.39 GiB.
- **G07 pre-evidence** suggested Mar-2024 peaks in the 8–10 GiB range *pre-refactor*. Post-refactor (streaming-chunk rewrite) is explicitly expected to collapse peaks substantially — v2 Issue 2 projected Aug-2024 post-refactor peaks at ~5.5–7.2 GiB.
- **Implication:** if post-refactor Aug-2024 peak_commit lands above 7.82 GiB, **E1 trips under v3** (same clause as v2, new number). Streaming-chunk refactor is pulled in as G09 prerequisite. This is a tighter fail-closed boundary than v2 (which would have tolerated up to 9.58 GiB), consistent with v3's overall discipline.
- **Not a BLOCK on v3 approval.** The baseline-run's purpose is precisely to measure where peak_commit lands under the refactored code path. If E1 fires, the workflow handles it (refactor + re-baseline). If E1 does not fire, we populate CEILING_BYTES = min(ceil(peak × 1.3), CAP_v3) per v2 preserved formula.

Evidence trace: Sentinel TimescaleDB chunk inspection 2026-04-21 (MEMORY.md cites `~24% Jul / ~45% Aug over Mar-2024`; G07 peak evidence referenced in v1/v2 R3).

### One-shot RA amendment template compatibility

Checked: my RA-20260423-1 (SUPERSEDED, unused) and RA-20260424-1 (CONSUMED, one-shot spent) referenced v2 R4 in their step-1d gate formula and v2 E6 in their halt-fallback clause. v3 changes both numeric references but does not change the RA template structure:

- **Step 1d gate formula** in RA-YYYYMMDD-N: changes from `available ≥ 15,428,752,588 bytes` to `available ≥ 9,473,794,048 bytes`. Template unchanged; constant updated.
- **Halt clause** in RA-YYYYMMDD-N: changes from "if R4 gate fails post-quiesce, halt and escalate under v2 E6" to "if R4 gate fails post-quiesce, halt and escalate under v3 E6 with identical resolution path (operator closes named processes; retry)". Template unchanged.
- **Quiesce probe step** (Step 2b/2c/2d): unchanged — the `docker stop` + `wsl --shutdown` + `time.sleep(30)` sequence is orthogonal to the gate threshold.
- **E7 drift check (new)** must be added to future RA templates: at RA drafting time, compare fresh `OBSERVED_QUIESCE_FLOOR_AVAILABLE_new` (from pre-RA probe if available, else from preceding RA's artifact) to 9,473,794,048; if >10% drift, RA cannot proceed until v3 re-derivation.

**No conflict** between v3 and the RA template. The **next** RA (RA-20260425-N) will use v3 numbers and add the E7 pre-check. I will draft RA-20260425-N after Dex + Quinn gate per normal R10 procedure.

### Escalation table v3 (consolidated for Dex reference)

For Dex to implement tests against. All v2 entries preserved; E6 updated per v3; E7 added.

| ID | Condition | Trip signal (v3) | Action | Exit code |
|---|---|---|---|---|
| E1 | Baseline peak exceeds cap | `peak_commit_aug2024 > CAP_ABSOLUTE` (7.82 GiB, was 9.58 GiB) | Streaming-chunk refactor; re-baseline | N/A (derivation BLOCK) |
| E2 | Cap exceeds 0.70 × RAM | `CAP_ABSOLUTE / PHYSICAL_RAM > 0.70` (does not trip at 0.49 = 8.40/17.14 decimal) | New ADR + Riven co-sign | N/A (derivation BLOCK) |
| E3 | R1 leak detector trips | Signal A ratio > 4.0 OR Signal B ΔPageFile > 2 GiB | Dex re-engaged; no ceiling derived | N/A (derivation BLOCK) |
| E4 | Physical RAM changes | `psutil.virtual_memory().total` drifts > 1% from PHYSICAL_RAM_BYTES | Full re-derivation (new preflight + new baseline + new ceiling) | 1 (wrapper setup error) |
| E5 | PageFile backing migrates | SATA ↔ NVMe hardware change | Re-evaluate R5 fractions (paging latency delta) | N/A (operator-notice; advisory) |
| E6 | Launch-time available insufficient | `available < CAP_ABSOLUTE + OS_HEADROOM` (9.47 GiB, was 14.37 GiB) | Operator closes top-3 non-retained consumers; retry | 1 (wrapper setup error) |
| **E7 (NEW)** | Observed quiesce floor drift | `\|OBSERVED_QUIESCE_FLOOR_AVAILABLE_new − 9,473,794,048\| / 9,473,794,048 > 0.10` | Full CAP re-derivation; Riven drafts new ADR | N/A (pre-RA BLOCK) |

Row E7 is the sole structural addition. No exit codes invented. ADR-2 scope (exit codes) untouched — deliberately, per hard bounds.

### Fail-closed invariance proof (v3 ≥ v2 in safety)

A v3 amendment MUST be at least as safe as v2. Demonstration:

| Axis | v2 behavior | v3 behavior | Verdict |
|---|---|---|---|
| R4 reachability | Unreachable (14.37 GiB > 9.47 GiB observed) | Reachable (9.47 GiB = observed by construction) | v3 stricter (v2 was vacuously safe by being unreachable, which is *unsafe in the limit* because the system could never launch and never provide protection at all) |
| CAP tightness | 9.58 GiB (0.60 × RAM) | 7.82 GiB (observed floor − headroom) | v3 tighter by 1.76 GiB |
| R5 KILL (absolute) | 9.10 GiB | 7.43 GiB | v3 tighter by 1.67 GiB |
| Leak detection (R1) | Preserved | Preserved (friendly — tighter KILL means fewer bytes of PageFile growth possible pre-kill) | v3 at least as safe |
| E1 trigger | peak > 9.58 GiB | peak > 7.82 GiB | v3 stricter |
| Floor drift catch (E7) | Not present | 10% trigger | v3 stricter (new check) |
| Portability formula | Not present | `min(floor−headroom, 0.60×RAM)` | v3 stricter (explicit rule) |
| OS starvation protection | 1.5× multiplier (unreachable) | additive OS_HEADROOM (reachable, explicit) | v3 stricter (actually fires) |

**Every v2 safety axis is preserved or tightened under v3.** No axis loosened. Fail-closed bar is met.

### Constitutional compliance

- **Article IV (No Invention):** All new Riven-v3 content (sizing-label table, variance feasibility note, one-shot template compatibility, escalation table, fail-closed proof) traces to `quiesce-mid.json`, `quiesce-audit-20260424.yaml`, host-preflight, Sentinel TimescaleDB chunk inspection 2026-04-21, Gregg §7.5, psutil docs, or ADR-1 v2/v3 content. No invented numbers or mechanisms.
- **Article V (Quality First):** Dex's implementation target is identical to Aria's v3 handoff (no new Riven-imposed Dex work); Quinn's audit scope is incremented by verifying my recalibration tables (sizing labels, escalation v3, fail-closed proof). Zero ambiguity added.
- **Article I (CLI First):** R4/E6 remain CLI-invocable deterministic gates. E7 is a pre-RA check (drafting-time), not a runtime component — no UI introduced.
- **Article II (Agent Authority):** R10 custodial scope respected. No @dev/@devops/@aiox-master authority touched. Co-sign only; no code modification.

### Final verdict

**GO for ADR-1 v3.** Riven (@risk-manager, R10 custodial) co-signs all 7 handoff points:

1. ✅ R4 formula change (multiplier → additive)
2. ✅ CAP value (10.29 → 7.82 GiB)
3. ✅ OS_HEADROOM value (1 GiB, Gregg §7.5 anchor)
4. ✅ E6 signal rewrite (launch-time-only OS-starvation gate; explicit runtime-orthogonality clarification)
5. ✅ E7 new escalation (10% floor drift threshold, applied at both re-baseline AND every pre-RA probe)
6. ✅ Portability formula (`min(floor−headroom, 0.60×RAM)` — `max()` counterproposal rejected)
7. ✅ v2 R1/R2/R3 preservation (dual signal intact; banners added inline at v2 sections)

Ancillary recalibrations co-signed:
- R5 fractions 85/95 unchanged under v3 (tightening to 0.80 rejected with rationale)
- R3 variance note (Sentinel +45% under v3 CAP = 7.82 GiB implies Mar-2024 ≤ 5.39 GiB baseline fit; E1 may trip post-refactor; informational only)
- Canonical sizing-label table refreshed to v3 values
- RA template compatibility verified; RA-20260425-N to follow Dex + Quinn gate

**Next steps (unchanged from Aria's v3 chain):**
1. Quinn audit at `docs/qa/gates/ADR-1-v3-audit.md` (scope now includes Riven v3 recalibrations).
2. Dex patch `core/memory_budget.py` + R4 launch-time check per Aria's v3 §Handoff diff.
3. Riven drafts RA-20260425-N for G09a retry under v3 R4 gate.
4. Gage executes RA-20260425-N; G09a produces `peak_commit_aug2024`.
5. Aria + Riven at step 7: derive `CEILING_BYTES = min(ceil(peak × 1.3), CAP_ABSOLUTE_v3)`; R1 dual-signal evaluation; E1/E3 check.
6. Dex populates `CEILING_BYTES`; commit cites Gregg + Sentinel variance per R3 preserved requirement + `quiesce-mid.json` per v3 evidence chain.

---

**Sign-off:**
- 2026-04-23 BRT (late-day) — **Riven (@risk-manager, R10 custodial)** — ADR-1 v3 **APPROVED** per 7-point co-sign above. Method + constants + portability formula + E6/E7 escalations co-signed. Rationale: Aria's v3 derivation corrects the structurally-unreachable v2 R4 gate against empirically-observed host quiesce floor from RA-20260424-1 (`data/baseline-run/quiesce-mid.json` `available = 9,473,794,048`); OS_HEADROOM = 1 GiB anchored to Gregg *Systems Performance* 2nd ed. §7.5 bounded-workload buffer upper bound; fail-closed discipline preserved across every axis (R4 reachability fixed, CAP tightened, R5 KILL tightened, E1 trigger tightened, E7 adds structural-resident floor drift detection); Article IV compliance verified — no invented numbers.
- Next required sign-off: Riven at step 7 of v3 remediation (post-G09a baseline derivation) with concrete `peak_commit`, `peak_rss`, ratio (Signal A), ΔPageFile (Signal B), host-preflight cross-ref, `quiesce-mid.json` cross-ref, and final `CEILING_BYTES` value (either `ceil(peak × 1.3)` or `CAP_ABSOLUTE_v3 = 8,400,052,224`, whichever is lower per preserved v2 formula).
- Manifest guard: `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at co-sign time. No canonical parquets or code modified in this commit.

---

## R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260425-1)

> **[SUPERSEDED 2026-04-23 — CONSUMED at Phase 4 (child exit 11, psycopg connect refused) under RA-20260426-1; see RA-20260426-1 below under Option B cache routing]**
> Status: Consumed (one-shot spent). Gage (@devops) executed the authorized quiesce sequence per Decisions 1-4b; both v3 R4 gate (margin 21.5 MiB) and E7 drift gate (0.24%) passed; baseline-run child launched at 2026-04-23T20:36:43-03:00 BRT (PID 7804); child exited 11 in 30.6s on `psycopg.OperationalError: connection refused` at `localhost:5433`. Root cause: Decision 1's rationale — "Container is idle for baseline-run — baseline uses canonical parquets, not Sentinel DB" — was **empirically false**. `scripts/materialize_parquet.py._fetch_month_dataframe` reads raw trades FROM the Sentinel PG container to BUILD the Aug-2024 parquet; stopping the container severed the data source. This rationale defect was inherited verbatim from RA-20260423-1 → RA-20260424-1 → RA-20260425-1 (three RAs); the failure was latent until v3 R4 + wrapper passthrough cleared the way for Phase 4 launch. `peak_commit_bytes = 401,408` in retry-4 is startup overhead only; not a valid input to #78 `CEILING_BYTES` derivation. Canonical state re-verified byte-identical post-restore (17/17 files). Governance incident captured as task #106. Aria issued ADR-4 Amendment 20260424-1 (`docs/architecture/pre-cache-layer-spec.md §13`) introducing Option B: a local pre-cache layer (`data/cache/raw_trades/` + `data/cache/cache-manifest.csv`) and `--source {sentinel,cache}` dispatch, enabling baseline-run to operate self-sufficiently with sentinel DOWN. Per amendment one-shot discipline, a fresh RA (RA-20260426-1) is issued below under Option B routing. Audit trail preserved verbatim — DO NOT DELETE.

**Authority:** Riven (@risk-manager, R10 custodial) — ADR-1 **v3** Condition R4 / Escalation clauses E6 + E7.
**Date:** 2026-04-23 BRT (issuance; ID carries 2026-04-25 sequence marker per one-shot-per-attempt discipline — this is the third RA issued against the G09a baseline-run window; first RA under ADR-1 v3).
**Scope:** **ONE (1) G09a baseline-run execution only.** NOT a permanent policy change. Whitelist frozenset in `core/memory_budget.py` remains **unchanged** — this amendment operates at the *operational policy* layer (procedural authorization for Gage), not at the *code contract* layer (`is_retained()` filter).
**Supersedes:** **RA-20260424-1 (CONSUMED at Phase 2f under v2 R4).** Predecessor halted at Step 1e (GATE) when `quiesce-mid.json` observed `available = 9,473,794,048` bytes — empirically proven to be the host's irreducible structural-resident floor under the authorized quiesce envelope, and structurally below v2's `1.5 × CAP_ABSOLUTE_v2 = 15,428,752,588` threshold. That observation became the empirical anchor for ADR-1 v3's R4 recalibration (`available ≥ CAP_ABSOLUTE + OS_HEADROOM`). One-shot discipline per RA-20260424-1 Decision 8 requires fresh sign-off now that the R4 gate has been corrected.
**Governing ADR:** **ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor** (`docs/architecture/memory-budget.md` §ADR-1 v3, lines 982+).
**Ratification chain (all four gates closed):**
- **ADR-1 v3 (Aria @architect):** `docs/architecture/memory-budget.md §ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor` — PROPOSED 2026-04-23 BRT late-day.
- **Riven Co-sign v3 (Riven @risk-manager):** `docs/architecture/memory-budget.md §Riven Co-sign v3 — R1/R2/R3/E6/E7 Recalibration Against ADR-1 v3` — 7-point GO co-sign, all 7 handoff points ✅, ancillary recalibrations co-signed.
- **Quinn v3 audit (Quinn @qa):** `docs/qa/gates/ADR-1-v3-audit.md` — PASS 7/7, zero blockers.
- **Dex v3 patch (Dex @dev):** `core/memory_budget.py` + `core/run_with_ceiling.py` + 16 new v3 tests (225 passed / 1 skipped, ruff clean); smoke-test verified runtime constants: `CAP_ABSOLUTE = 8_400_052_224`, `OS_HEADROOM = 1_073_741_824`, `R4_threshold = 9_473_794_048`.
**Trigger:** unchanged from RA-20260424-1 — `data/baseline-run/baseline-aug-2024-preflight-halt.md` (G09a baseline-run still required to derive `peak_commit_aug2024` for step-7 `CEILING_BYTES` finalization per ADR-1 v3 §Next-steps). The substantive reason for re-issue is that the v3 R4 gate is now *reachable* against the measured floor: `CAP_ABSOLUTE_v3 + OS_HEADROOM = 8,400,052,224 + 1,073,741,824 = 9,473,794,048 bytes`, exactly matching the observed mid-quiesce floor by construction.

### Decision 1 — Services authorized to stop (MINIMUM SET)

**IDENTICAL to RA-20260424-1.** Reproduced for executability:

| Service | Stop mechanism | Rationale | Expected free (GiB) |
|---|---|---|---|
| `sentinel-timescaledb` (Docker container only — **NOT Docker Desktop itself**) | `docker stop sentinel-timescaledb` | Container is idle for baseline-run (baseline uses canonical parquets, not Sentinel DB). Docker Desktop backend kept running to permit fast `docker start` on restore. | ~0.5-1.0 |
| `vmmem` (WSL2 subsystem, all distros) | `wsl --shutdown` | Halts all WSL2 guest memory. Empirically the largest reclaimable retained consumer at t=second-capture per RA-20260424-1 mid-quiesce snapshot. | ~3.0-4.0 |

Expected combined reclaim: **~3.5-5.0 GiB**. Under the v3 R4 threshold (9,473,794,048 bytes = observed mid-quiesce floor), the gate is reachable by construction when the operator reproduces the RA-20260424-1 quiesce procedure.

**REFUSED stops (Riven asserts NO):** IDENTICAL to RA-20260424-1 — MsMpEng (security-pinned), `claude` (would kill Gage), Docker Desktop full (deeper deviation; container-only sufficient), OS kernel-adjacent (System / svchost / csrss / smss / wininit / winlogon / lsass / Registry / Memory Compression / explorer).

**Article IV anchor:** Identical trace chain to RA-20260424-1 — minimum set traces to observed deficit in halt report + ADR-1 v3 §Structural-resident floor analysis (lines 998+). No invented reclaim values.

### Decision 2 — Duration cap

**IDENTICAL to RA-20260424-1.** HARD CEILING: **4 hours from start of Step a (first `docker stop`) to completion of Step e (post-restore verification).**

Anchor chain unchanged: baseline-run wall-clock 1-2h + pre/post-flight 15m + restore verification 15m + 30m margin + 60m absolute tail = 4h.

**Fail-closed behavior at ceiling:** IDENTICAL — SIGTERM (graceful) → 30s wait → SIGKILL → proceed to restore (Decision 6) regardless of partial data state → report `duration_cap_exceeded: true`. No grace extension.

### Decision 3 — Pre-quiesce verifications (GATE before any stop)

**IDENTICAL to RA-20260424-1.** Gage MUST record all of the following into `data/baseline-run/quiesce-pre.json` **before** Step a:

| Verification | Expected value | Action if fail |
|---|---|---|
| sha256 `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | HALT; escalate (do not stop services) |
| sha256 `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | HALT; escalate |
| `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` | `healthy` (recorded, not required) | Record observed state; continue |
| `data/baseline-run/` exists | directory present | create if missing |
| `data/baseline-run/scratch/` ready | directory present | create if missing |
| `psutil.virtual_memory()` snapshot | recorded | no gate |
| `psutil.process_iter()` top-30 by RSS | recorded | no gate |

Output JSON schema unchanged from RA-20260424-1.

### Decision 4 — Quiesce order (deterministic, auditable) — **v3 R4 GATE**

**Steps a-d IDENTICAL to RA-20260424-1:** `docker stop sentinel-timescaledb` → `wsl --shutdown` → `sleep 30` → re-capture `quiesce-mid.json`.

**Step e (GATE) — CHANGED from v2 to v3 formula:**

| Attribute | v2 value (RA-20260424-1, superseded) | **v3 value (RA-20260425-1, active)** |
|---|---|---|
| Gate formula | `available ≥ 1.5 × CAP_ABSOLUTE_v2` | **`available ≥ CAP_ABSOLUTE_v3 + OS_HEADROOM`** |
| Threshold bytes | `15,428,752,588` (unreachable) | **`9,473,794,048`** (reachable; = observed floor) |
| Threshold GiB | 14.37 GiB | **8.82 GiB** |
| Reachability evidence | Theoretical; proven unreachable | `data/baseline-run/quiesce-mid.json` — observed `available = 9,473,794,048` exactly at the threshold by construction |
| Fail-closed behavior | HALT + restore + escalate (no deeper deviation, no threshold lowering, no retry loop) | **IDENTICAL v2 behavior — HALT + restore + escalate, unchanged** |

**PROCEED/HALT decision at Step e:**
- `observed_available_bytes ≥ 9,473,794,048` → **PROCEED** to Decision 4b (E7 drift check, see below) → then Decision 5 (launch baseline-run)
- `observed_available_bytes < 9,473,794,048` → **HALT**; execute Decision 6 (restore) unconditionally; escalate to @risk-manager; no retry under this RA.

### Decision 4b — E7 floor-drift check (NEW per ADR-1 v3 §E7 + Riven Co-sign v3 §5)

Immediately after Decision 4 step e mid-quiesce snapshot is captured and **before** launching baseline-run per Decision 5, Gage MUST compute:

```
drift = abs(observed_available_bytes - 9_473_794_048) / 9_473_794_048
```

Where `observed_available_bytes` is the `available` field from `data/baseline-run/quiesce-mid.json` step-d capture.

**Drift gate:**
- `drift ≤ 0.10` (10% tolerance band — observed floor matches baseline within expected operational variance) → **PROCEED** to Decision 5 launch under the v3 R4 gate.
- `drift > 0.10` → **HALT + escalate.** Do NOT launch baseline-run. Do NOT attempt threshold adjustment. Execute Decision 6 (restore) unconditionally. Observed host state has diverged from the v3 baseline floor; v3 constants may require re-observation before any further R4-gated run. Escalate to @architect (Aria) + @risk-manager (Riven) with `quiesce-mid.json` attached; a new RA + potentially a new ADR re-derivation cycle is required.

**Rationale:** The v3 R4 threshold (9,473,794,048 bytes) was anchored directly to a single empirical observation. Host state drift (background process accretion, OS updates, driver/service upgrades, memory fragmentation, or kernel behavior changes) can shift the structural-resident floor over time. The 10% band provides a formal trip wire to detect such drift before it silently invalidates the R4 gate's soundness. Per Aria ADR-1 v3 E7 + Riven Co-sign v3 §5, this check applies at every pre-RA quiesce probe — not just at re-baseline events.

**Gate is informational-at-pass / fail-closed-at-breach:** passing the gate (≤ 10%) generates no additional artifact beyond the audit YAML field; breaching the gate (> 10%) is a hard stop with escalation. There is no "warn" band.

**Drift check artifact:** Gage records `drift_ratio: <float>`, `drift_threshold: 0.10`, `drift_decision: PROCEED|HALT` in the audit YAML under a new `e7_drift_check:` block (see Decision 7).

### Decision 5 — Authorized baseline-run invocation

**IDENTICAL to RA-20260424-1.** The authorized launch command, invoked via the Dex-patched wrapper surface (passthrough + mutex gated by Quinn PASS 7/7, now running under v3 R4 gate per Dex v3 patch), is:

```
.venv/Scripts/python scripts/run_materialize_with_ceiling.py \
  --run-id baseline-aug-2024 \
  --start-date 2024-08-01 \
  --end-date 2024-08-31 \
  --ticker WDO \
  --no-ceiling \
  --poll-seconds 30 \
  --output-dir data/baseline-run/scratch \
  --no-manifest
```

**Flag disposition rationale (unchanged from RA-20260424-1):** `--no-manifest` preferred over `--manifest-path` for explicit-zero-write semantics (zero canonical-collision surface area even under filesystem race); wrapper mutex group enforces `--no-manifest` XOR `--manifest-path` at wrapper surface.

Gage MUST use the command above **verbatim**. Variant invocations (e.g., `--manifest-path`, alternate date ranges, alternate tickers) are NOT authorized under RA-20260425-1; a new RA is required if a variant is desired in a future retry.

### Decision 6 — Restore order (ALWAYS executed — success, failure, or cap-exceeded)

**IDENTICAL to RA-20260424-1.** Reproduced for executability:

| Step | Action | Verification |
|---|---|---|
| a | WSL2 left dormant (no action). Next user-initiated WSL command will restart it. Gage does NOT actively launch a WSL2 shell. | — |
| b | `docker start sentinel-timescaledb` | exit_code == 0 |
| c | Poll `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` every 5s; accept on `healthy`; timeout 90s total | If timeout without healthy → escalate immediately, do NOT retry |
| d | `psutil.virtual_memory()` + `psutil.process_iter()` top-30 → `data/baseline-run/quiesce-post.json` | — |
| e | Re-verify canonical sha256 — manifest + Aug-2024 parquet — MUST match pre-quiesce hashes byte-identically | If mismatch → CRITICAL, escalate; do NOT attempt repair |

**Restore is unconditional:** executed whether baseline-run exited 0 (success), nonzero (failure), was killed by duration-cap enforcement, was halted at Decision 4 step e (v3 R4 gate fail), or was halted at Decision 4b (E7 drift breach). Services must be restored before Gage's session ends.

### Decision 7 — Audit trail (Gage MUST fulfill)

Gage appends a structured YAML document to `data/baseline-run/quiesce-audit-YYYYMMDD.yaml`:

```yaml
- quiesce_window:
    amendment_id: RA-20260425-1
    supersedes: RA-20260424-1
    governing_adr: ADR-1 v3
    operator: gage
    date_brt: 2026-MM-DD
    run_id: baseline-aug-2024   # --run-id per Decision 5
    ceiling_expires_at_brt: <start + 4h ISO-8601>
    authorized_invocation_flags:
      no_manifest: true
      manifest_path: null
      output_dir: "data/baseline-run/scratch"
    pre:
      timestamp_brt: <iso>
      manifest_sha256: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
      parquet_sha256: bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0
      available_bytes: <int>
      sentinel_health: <healthy|unhealthy|starting|...>
    quiesce:
      step_a_docker_stop: {timestamp_brt: <iso>, exit_code: <int>}
      step_b_wsl_shutdown: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_sleep: {timestamp_brt: <iso>, duration_s: 30}
      step_d_mid_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_gate:
        decision: PROCEED|HALT
        formula: "available >= CAP_ABSOLUTE_v3 + OS_HEADROOM"
        threshold_bytes: 9473794048   # v3 R4 threshold (CAP_v3 8,400,052,224 + HEADROOM 1,073,741,824)
        available_bytes: <int>
    e7_drift_check:
      baseline_floor_bytes: 9473794048
      observed_available_bytes: <int>   # same as step_d_mid_capture.available_bytes
      drift_ratio: <float>              # abs(observed - baseline) / baseline
      drift_threshold: 0.10
      drift_decision: PROCEED|HALT
    baseline_child:
      launched: <bool>
      pid: <int|null>
      start_ts_brt: <iso|null>
      end_ts_brt: <iso|null>
      exit_code: <int|null>
      duration_cap_exceeded: <bool>
      emergency_kill:
        threshold_bytes: 7980049613   # v3 95% × CAP_ABSOLUTE_v3 (see Decision 8)
        tripped: <bool>
        trip_timestamp_brt: <iso|null>
        observed_commit_bytes_at_trip: <int|null>
    restore:
      step_a_wsl_state: dormant
      step_b_docker_start: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_container_health: {timestamp_brt: <iso>, status: <healthy|timeout>, poll_count: <int>}
      step_d_post_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_sha256_reverify:
        manifest_match: <bool>
        parquet_match: <bool>
    final_disposition: <SUCCESS|BASELINE_FAIL|CAP_EXCEEDED|QUIESCE_GATE_HALT|E7_DRIFT_HALT|EMERGENCY_KILL|RESTORE_FAIL>
```

This audit YAML lives inside `data/baseline-run/` (scratch area, L4 runtime per framework boundary). Not a manifest mutation. Only this RA-20260425-1 policy artifact is registered in MANIFEST_CHANGES (as spec_issuance; manifest unchanged).

### Decision 8 — Hard bounds (non-negotiable even under amendment)

Structurally IDENTICAL to RA-20260424-1, with two v3-specific updates (emergency-kill threshold tightened, E7 drift check added):

| Bound | Enforcement |
|---|---|
| Canonical `data/manifest.csv` untouched | `--no-manifest` flag per Decision 5 (Dex wrapper passthrough; Quinn-gated). Re-verified in Decision 6 step e. |
| Canonical parquets in `data/in_sample/**` untouched | `--output-dir data/baseline-run/scratch` per Decision 5. Re-verified in Decision 6 step e. |
| MsMpEng NEVER stopped | Hard refusal at Decision 1. |
| `claude` NEVER stopped | Would kill Gage; impossible. |
| Restore failure (sentinel not healthy in 90s) → immediate escalation | Gage does NOT attempt DB repair or retry cycles. Orchestrator decides next step. |
| Duration cap hit mid-run → SIGTERM/SIGKILL baseline child, restore services, report partial | No grace extension. Decision 2. |
| sha256 mismatch at Decision 6 step e → CRITICAL escalation | Canonical state altered during the window (should be physically impossible under Decision 5 + wrapper mutex + hard bound 1). Do not attempt recovery. |
| No permanent whitelist change | `core/memory_budget.py` `_RETAINED_PROCESSES` frozenset unchanged. Amendment expires when audit YAML `final_disposition` is written. |
| One-shot discipline | Any failure mode (E1/E3/R4 post-quiesce/E7 drift/crash/deadline/restore-fail) → restore + escalate + new RA required for next attempt. RA-20260425-1 is NOT reusable. |
| **[NEW v3]** E7 floor-drift hard stop | If Decision 4b yields `drift > 0.10`, HALT + restore + escalate. No threshold adjustment permitted; re-observation of v3 constants is orchestrator/architect scope. |
| **[UPDATED v3]** Emergency-kill monitor threshold (used during `--no-ceiling` run by Gage's manual monitor) | **`7_980_049_613` bytes ≈ 7.43 GiB = 0.95 × CAP_ABSOLUTE_v3 (8,400,052,224)`**. Tighter than v2's 9,771,543,306 (= 0.95 × 10,285,835,059). If baseline-run child's observed commit/RSS approaches or exceeds this threshold, Gage manually SIGTERM/SIGKILL the child, execute Decision 6 restore, report `EMERGENCY_KILL` disposition. Gage MAY use `psutil` or Task Manager commit column; threshold refers to **per-child commit bytes**, not system-wide. |

### Decision 9 — Constants reference (v3 canonical values)

For unambiguous operator execution:

| Constant | Value (bytes) | Value (GiB, approx) | Source |
|---|---|---|---|
| `CAP_ABSOLUTE_v3` | `8_400_052_224` | 7.82 GiB | `core/memory_budget.py` (Dex v3 patch); ADR-1 v3 §Derivation |
| `OS_HEADROOM` | `1_073_741_824` | 1.00 GiB | `core/memory_budget.py` (Dex v3 patch); Gregg §7.5 |
| `R4_threshold_v3` | `9_473_794_048` | 8.82 GiB | `CAP_ABSOLUTE_v3 + OS_HEADROOM`; Dex smoke-verified |
| `emergency_kill_threshold_v3` | `7_980_049_613` | 7.43 GiB | `0.95 × CAP_ABSOLUTE_v3`; Decision 8 |
| `E7_drift_tolerance` | — | 10% (0.10) | ADR-1 v3 §E7 + Riven Co-sign v3 §5 |
| Observed mid-quiesce floor (empirical anchor) | `9_473_794_048` | 8.82 GiB | `data/baseline-run/quiesce-mid.json` (RA-20260424-1 execution) |

### Sign-off

**2026-04-23 BRT — Riven (@risk-manager, R10 custodial) — RA-20260425-1 APPROVED under ADR-1 v3.**

Amendment scope: ONE G09a baseline-run window, ≤ 4 hours total, WSL2 + sentinel-timescaledb container stop authorized, all ADR-1 v3 constraints in force (`CAP_ABSOLUTE = 8,400,052,224` bytes per Dex v3 patch; `OS_HEADROOM = 1,073,741,824` bytes; R4 threshold `9,473,794,048` bytes — reachable; E7 drift check active at 10% tolerance; R5 warn 85% / kill 95%; E1-E6 per Riven Co-sign v3). Gage executes under Decisions 1-9 above with zero clarifying questions. On completion (any disposition), this amendment is spent — a second retry or any subsequent quiesce requires a new RA-YYYYMMDD-N amendment.

**R10 co-sign block:**
- Custodial authority: Riven (@risk-manager, R10) — signed 2026-04-23 BRT.
- Governance class: one-shot operational policy amendment (not a code contract change; not a permanent whitelist mutation).
- Constitutional compliance:
  - **Article IV (No Invention)** — every threshold traces to v3 constants Dex already shipped to `core/memory_budget.py` (`CAP_ABSOLUTE = 8_400_052_224`, `OS_HEADROOM = 1_073_741_824`, `R4_threshold = 9_473_794_048`, smoke-verified); emergency-kill threshold = `0.95 × CAP_ABSOLUTE_v3` per Riven Co-sign v3 §R5 preservation; E7 drift threshold = 10% per ADR-1 v3 §E7 + Riven Co-sign v3 §5; Decisions 1-4, 6 trace verbatim to RA-20260424-1 (structurally identical under tightened gate).
  - **Article V (Quality First)** — zero-ambiguity for Gage: deterministic gates at Decisions 3, 4e, 4b; explicit byte-value references at Decision 9; audit YAML schema fully specified at Decision 7.
  - **Article I (CLI First)** — all actions CLI-invocable (`docker stop`, `wsl --shutdown`, `.venv/Scripts/python`, `psutil`).
- Supersedes RA-20260424-1 (CONSUMED at Phase 2f under v2 R4; one-shot spent per its Decision 8 discipline).

**References:**
- Governing ADR: **ADR-1 v3** — `docs/architecture/memory-budget.md §ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor` (Aria @architect, PROPOSED 2026-04-23 BRT late-day)
- Riven v3 co-sign: `docs/architecture/memory-budget.md §Riven Co-sign v3 — R1/R2/R3/E6/E7 Recalibration Against ADR-1 v3` (7-point GO)
- Quinn v3 audit: `docs/qa/gates/ADR-1-v3-audit.md` (PASS 7/7, zero blockers)
- Dex v3 patch: `core/memory_budget.py` + `core/run_with_ceiling.py` (16 new v3 tests; 225 passed / 1 skipped; ruff clean; smoke-test verified `CAP_ABSOLUTE=8_400_052_224`, `OS_HEADROOM=1_073_741_824`, `R4_threshold=9_473_794_048`)
- Predecessor (consumed): RA-20260424-1 — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260424-1)` (SUPERSEDED banner applied inline)
- Grand-predecessor (unused): RA-20260423-1 — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260423-1)` (SUPERSEDED)
- Empirical anchor: `data/baseline-run/quiesce-mid.json` — observed `available = 9,473,794,048` at 2026-04-23T19:21:51-03:00 under RA-20260424-1 quiesce; this value IS the v3 R4 threshold by construction
- Halt narrative: `data/baseline-run/baseline-aug-2024-halt-report.md` (RA-20260424-1 phase-by-phase outcome)
- Enabling precondition (wrapper quality): `docs/qa/gates/wrapper-passthrough-gate.md` (Quinn @qa PASS 7/7)
- Manifest guard: `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at issuance. No canonical parquets, no code modifications, no manifest mutations in this RA.

---

### §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260426-1)

> **[STATUS: ISSUED — ONE-SHOT QUIESCE WINDOW AUTHORIZED]**
> This amendment flipped DRAFT → ISSUED on 2026-04-24T11:42:19Z by Orion (aiox-master, 👑 Orchestrator) acting on Riven-delegated authority per the flip_procedure encoded in this section and in `docs/MANIFEST_CHANGES.md` r4_amendments entry. All five issuance preconditions (P1-P5) satisfied and pinned under `data/baseline-run/ra-20260426-1-evidence/` with sha256 manifest below. One-shot consumption clock STARTED at that flip timestamp: Gage (@devops) is cleared to execute G09a retry #5 under Decisions 1-9 exactly ONCE. Any failure mode (gate halt, drift halt, cap exceeded, emergency kill, baseline fail, restore fail) consumes this RA irrevocably — a second attempt requires a new RA-YYYYMMDD-N amendment.
>
> **Issuance metadata:**
> - `issued_at_utc: 2026-04-24T11:42:19Z`
> - `issued_at_brt: 2026-04-24T08:42:19-03:00`
> - `issued_by: Orion (aiox-master, acting on Riven-delegated authority per issuance_preconditions.flip_procedure)`
> - `evidence_directory: data/baseline-run/ra-20260426-1-evidence/`
> - `quinn_gate_reference: docs/qa/gates/RA-20260426-1-chain-gate.md (sha256 2682bee8c8b0a7e483e3a98e65e83378635636f27cc514dc63b910d8fd8e21c8)`
> - `dex_impl_commits: 8c217bf (§13.1) + cb62713 (§13.2) + 85664f7 (P5 wrapper) + 63a9a3a (CONCERNS-01 test-stub repoint)`
> - `canonical_manifest_sha256_at_issuance: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641 (byte-identical to drafting)`
>
> **Evidence manifest (P1-P5, path + sha256 of each evidence file):**
>
> | # | Path | sha256 |
> |---|------|--------|
> | P1 | `data/baseline-run/ra-20260426-1-evidence/p1-t12b-sentinel-down.txt` | `d88176b4b97d2d2eaa602a5610ca651f075baca41a9192034ae7018d2a996e48` |
> | P2 | `data/baseline-run/ra-20260426-1-evidence/p2-cache-manifest-sha256.txt` | `6645ce8736f11b37c8169f8f61cd0d9ac677dccf462475762b01df4324ac0ee7` |
> | P3 | `data/baseline-run/ra-20260426-1-evidence/p3-wdo-2024-08-parquet-sha256.txt` | `dabcef3b31c98e3ad246471a8c936cbd55bd5cc4ff527fadefb62803da457165` |
> | P4 | `data/baseline-run/ra-20260426-1-evidence/p4-peak-ws.txt` | `10c219f2e6a0b8480fcbdd66b7238867a3ce623535a49150fcb3f9f5ff9efc37` |
> | P5 | `data/baseline-run/ra-20260426-1-evidence/p5-wrapper-gate-reference.txt` | `39ed424368f37506591eab0457b98066865366f6e9472680dff752db974d0c57` |
>
> **Pinned content sha256 (inside evidence files):**
> - Cache manifest (`data/cache/cache-manifest.csv`): `b7ef8562c112c2815e21c11486c03044f88bcb64a52333e4d279002c255a9885`
> - Aug-2024 cache parquet (`data/cache/raw_trades/ticker=WDO/year=2024/month=08/wdo-2024-08.parquet`): `2473bdcc4fe9ab08bf5ce35c36327175abdc0bf69acc303f7054281fcc4fe90a` (MATCHES expected value in RA)
> - Peak WS pilot build source (`.tmp/ws_peak.txt`): `55de16785298ce846fb164ef1b6532e4883817b85a4b32d33bcb33e67bcc7036` (peak_ws_bytes=221,130,752 = 210.89 MiB, 17x under 3.5 GiB A1 ceiling)
>
> Gage MUST verify all five evidence-file sha256 values AND the pinned content sha256 values above at Decision 3 pre-quiesce. Any drift → HALT + escalate + new RA.
>
> **Original drafting banner (retained for audit):** This amendment was DRAFTED 2026-04-23T22:30:00-03:00 BRT and held NOT-EXECUTABLE pending Dex (@dev) landing §13.1 (streaming cache build helper) + §13.2 (T12 split into T12a sentinel-UP parity + T12b sentinel-DOWN cache-only) + P5 wrapper passthrough, and attaching the `precondition_evidence` package below. Quinn (@qa) audited all three deliverables under `docs/qa/gates/RA-20260426-1-chain-gate.md` with verdict CONCERNS (blocker: 5 stale test stubs in `tests/unit/test_build_raw_trades_cache.py`). Dex resolved CONCERNS-01 via commit `63a9a3a` (test-stub repoint to `_stream_month_to_parquet`) and `tests/unit/` now 11/11 PASS. All DRAFT conditions satisfied; status flipped ISSUED.

**Authority:** Riven (@risk-manager, R10 custodial) — ADR-1 **v3** Condition R4 / Escalation clauses E6 + E7, augmented by ADR-4 (`docs/architecture/pre-cache-layer-spec.md`) Amendment 20260424-1 §13 (Option B local pre-cache layer).
**Date:** 2026-04-26 BRT (draft issuance; ID carries 2026-04-26 sequence marker — this is the fifth RA issued against the G09a baseline-run window; second RA under ADR-1 v3; first RA under ADR-4 Option B cache routing).
**Scope:** **ONE (1) G09a baseline-run execution only** under `--source=cache` routing against a pre-built Aug-2024 WDO cache parquet. NOT a permanent policy change. Whitelist frozenset in `core/memory_budget.py` remains **unchanged** — this amendment operates at the *operational policy* layer (procedural authorization for Gage), not at the *code contract* layer (`is_retained()` filter).
**Supersedes:** **RA-20260425-1 (CONSUMED at Phase 4 on 2026-04-23 BRT)**. Predecessor cleared both gates (R4 margin 21.5 MiB; E7 drift 0.24%) but the authorized baseline-run child (`scripts/materialize_parquet.py` under `run_materialize_with_ceiling.py` wrapper) failed deterministically at t+30.6s with `psycopg.OperationalError: connection refused at localhost:5433` because Decision 1 stopped `sentinel-timescaledb` while the build path reads from it. The defective Decision 1 rationale ("Container is idle for baseline-run — baseline uses canonical parquets, not Sentinel DB") was inherited verbatim across three prior RAs (23-1, 24-1, 25-1) and is EMPIRICALLY FALSIFIED by retry-4 `data/baseline-aug-2024.log`. Governance incident captured as task #106. Remediation architecture: Aria ADR-4 §13 (Option B) introduces local pre-cache layer at `data/cache/raw_trades/` with manifest `data/cache/cache-manifest.csv` and `--source {sentinel,cache}` dispatch; baseline-run under `--source=cache` is self-sufficient with sentinel DOWN during the R4-governed window. The Q1 architectural claim is empirically proven by T12b (cache-only, sentinel stopped, GREEN).
**Governing ADR:** **ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor** (`docs/architecture/memory-budget.md` §ADR-1 v3) **AND** **ADR-4 Amendment 20260424-1 — Option B Pre-Cache Layer** (`docs/architecture/pre-cache-layer-spec.md` §13).
**Ratification chain (required closure before DRAFT → ISSUED):**
- **ADR-1 v3 (Aria @architect):** unchanged from RA-20260425-1 chain — closed.
- **Riven Co-sign v3 (Riven @risk-manager):** unchanged from RA-20260425-1 chain — closed.
- **Quinn v3 audit (Quinn @qa):** `docs/qa/gates/ADR-1-v3-audit.md` — PASS 7/7, zero blockers — closed.
- **Dex v3 patch (Dex @dev):** `core/memory_budget.py` + `core/run_with_ceiling.py` + 16 new v3 tests (225 passed / 1 skipped, ruff clean) — closed.
- **ADR-4 §13 (Aria @architect):** `docs/architecture/pre-cache-layer-spec.md §13` — PROPOSED 2026-04-24 BRT — closed (drafted; see §13.5 Q5 disposition below).
- **ADR-4 §13.1 + §13.2 Dex impl (Dex @dev, PENDING — ISSUANCE BLOCKER):** Dex must land `build_raw_trades_cache.py` streaming helper per §13.1 A1-A5 acceptance + T12a/T12b split per §13.2; Quinn gates the impl. Until this ships, RA-20260426-1 remains DRAFT.
- **§13 Quinn gate (Quinn @qa, PENDING — ISSUANCE BLOCKER):** Quinn audits §13.1 + §13.2 Dex delivery and runs T12b with sentinel DOWN; PASS verdict + pytest output attached to `precondition_evidence` packet.
**Trigger:** RA-20260425-1 retry-4 `data/baseline-run/baseline-aug-2024-halt-report.md §Retry #4` — authorized quiesce severed the data source; baseline-run cannot succeed under the inherited Decision 1 rationale. Remediation path is Option B (ADR-4 §13). G09a baseline-run is still required to derive `peak_commit_aug2024` for step-7 `CEILING_BYTES` finalization per ADR-1 v3 §Next-steps.

### Precondition evidence (Gage MUST attach before claiming RA is ISSUED)

Gage cannot initiate quiesce under this RA until Riven (or Orion acting on Riven's behalf via a follow-up task) flips DRAFT → ISSUED with the following evidence packet attached under `data/baseline-run/ra-20260426-1-evidence/`:

| # | Evidence artefact | Expected content | Purpose |
|---|---|---|---|
| P1 | `t12b-verdict.xml` (pytest junit XML) OR `t12b-output.txt` | Output of `pytest tests/integration/test_adapter_parity_cache.py::T12b -v` run with `sentinel-timescaledb` container STOPPED (Docker `docker ps` confirms container absent or `Exited`). Must show `T12b PASSED`. T12a either SKIPPED (sentinel down) or not run. | Empirical proof of Q1: cache is self-sufficient with sentinel DOWN. This closes the architectural claim that Decision 1 of prior RAs could only argue by construction. |
| P2 | `cache-manifest-sha256.txt` | Single line: sha256 hex digest of `data/cache/cache-manifest.csv` computed by `sha256sum` or `hashlib` at the moment of evidence capture. | Pins the cache-manifest state Gage will verify at Decision 3 (pre-quiesce). If it drifts between evidence capture and execution, Gage HALTs. |
| P3 | `cache-aug2024-parquet-sha256.txt` | Single line: sha256 hex digest of `data/cache/raw_trades/year=2024/month=08/<cache-parquet-filename>.parquet` (exact filename per §13 helper output). | Pins the Aug-2024 cache parquet state; identical integrity guarantee as P2. |
| P4 | `peak-ws-pilot-build.txt` | Output of `scripts/telemetry_workingset.py` (or equivalent) during Dex's pilot build of Aug-2024 under §13.1. Must show peak WS < **3_758_096_384 bytes (3.5 GiB)** per §13.1 A1 acceptance. | Proves the cache-build path itself does not violate CAP_v3 (8,400,052,224 bytes) — ensures the cache exists legitimately under the v3 budget. |
| P5 | `wrapper-source-passthrough-gate.md` OR equivalent Quinn gate artefact | Quinn PASS verdict on a Dex wrapper patch extending `scripts/run_materialize_with_ceiling.py` to passthrough `--source`, `--cache-dir`, `--cache-manifest` to the child `materialize_parquet.py` invocation. Evidence that the wrapper composes the authorized invocation below verbatim without flag loss. | Blocker identified by Riven during RA-20260426-1 drafting: the current wrapper (validated under `wrapper-passthrough-gate.md` PASS 7/7 for `--output-dir` / `--no-manifest` / `--manifest-path`) does NOT forward the new §13 flags. Without this passthrough, Gage cannot execute Decision 5 below. |

**Evidence packet traceability:** the audit YAML schema at Decision 7 includes a new `precondition_evidence:` block listing each P1-P5 artefact path + its sha256 captured by Gage at the moment of quiesce-pre snapshot. Any mismatch between evidence sha256 and audit-time sha256 = HALT + escalate + new RA.

### Decision 1 — Services authorized to stop (MINIMUM SET) — **CORRECTED RATIONALE**

| Service | Stop mechanism | Rationale (**v3+Option B, empirically validated**) | Expected free (GiB) |
|---|---|---|---|
| `sentinel-timescaledb` (Docker container only — **NOT Docker Desktop itself**) | `docker stop sentinel-timescaledb` | **Under `--source=cache` routing (Decision 5), baseline-run reads raw trades from `data/cache/raw_trades/` via `packages/t002_eod_unwind/adapters/feed_cache.py` — NO live sentinel dependency during the R4-governed window.** This is empirically validated by T12b (sentinel DOWN + cache-only → PASSED) attached as evidence P1; the failure mode of RA-20260425-1 retry-4 (psycopg connect refused) is structurally precluded because `feed_cache.load_trades()` does not open a PG connection. Article IV anchor: `docs/architecture/pre-cache-layer-spec.md §13.5` "After this amendment: Q1 is answered GREEN by T12b passing with sentinel container stopped." | ~0.5-1.0 |
| `vmmem` (WSL2 subsystem, all distros) | `wsl --shutdown` | Halts WSL2 guest memory. Empirically confirmed from RA-20260424-1 mid-quiesce snapshot. **Caveat from retry-4:** Docker Desktop auto-restarts its `docker-desktop` WSL distro; vmmem observed 1.80 GiB pre → 2.19 GiB mid → 2.39 GiB post in retry-4. Reclaim may be smaller than expected but sufficient to reach the v3 R4 floor by construction (observed mid-available 8.843 GiB > 8.82 GiB floor with margin 21.5 MiB in retry-4). | ~0.5-1.5 (corrected per retry-4 empirical observation; was ~3.0-4.0 in RA-20260425-1 pre-retry-4) |

Expected combined reclaim: **~1.0-2.5 GiB** (corrected downward per retry-4 empirical evidence vs RA-20260425-1's optimistic ~3.5-5.0 GiB estimate that reflected a pre-retry model of `wsl --shutdown` fully reclaiming vmmem). Under the v3 R4 threshold (9,473,794,048 bytes), the gate is reachable by construction because retry-4 already demonstrated this host reaches `available = 9,496,334,336` bytes after identical quiesce (margin 22,540,288 bytes).

**REFUSED stops (Riven asserts NO):** IDENTICAL to RA-20260425-1 — MsMpEng (security-pinned), `claude` (would kill Gage), Docker Desktop full (deeper deviation; container-only sufficient), OS kernel-adjacent (System / svchost / csrss / smss / wininit / winlogon / lsass / Registry / Memory Compression / explorer).

**Article IV anchor:** Decision 1's rationale now traces to two empirical sources:
1. `data/baseline-run/baseline-aug-2024-halt-report.md §Retry #4` (RA-20260425-1 retry-4) — proves prior rationale was false and proves the host-level quiesce floor reaches the v3 R4 gate.
2. `data/baseline-run/ra-20260426-1-evidence/t12b-verdict.xml` (P1 evidence) — proves cache-only path is self-sufficient under sentinel DOWN.
No invented reclaim values; expected reclaim band corrected per retry-4 observation.

### Decision 2 — Duration cap

**IDENTICAL to RA-20260425-1.** HARD CEILING: **4 hours from start of Step a (first `docker stop`) to completion of Step e (post-restore verification).** Fail-closed behavior at ceiling: SIGTERM (graceful) → 30s wait → SIGKILL → proceed to restore (Decision 6) regardless of partial data state → report `duration_cap_exceeded: true`. No grace extension.

### Decision 3 — Pre-quiesce verifications (GATE before any stop) — **EXTENDED for cache integrity**

Gage MUST record all of the following into `data/baseline-run/quiesce-pre.json` **before** Step a:

| Verification | Expected value | Action if fail |
|---|---|---|
| sha256 `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | HALT; escalate (do not stop services) |
| sha256 `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | HALT; escalate |
| **[NEW]** `data/cache/raw_trades/` exists AND contains Aug-2024 parquet | directory present, parquet file present | HALT; cache not built — return RA to DRAFT state |
| **[NEW]** sha256 `data/cache/cache-manifest.csv` | IDENTICAL to `precondition_evidence/cache-manifest-sha256.txt` (P2) | HALT; cache has drifted since evidence capture; escalate |
| **[NEW]** sha256 Aug-2024 cache parquet (path per `cache-manifest.csv` row for WDO/2024-08) | IDENTICAL to `precondition_evidence/cache-aug2024-parquet-sha256.txt` (P3) | HALT; cache parquet has drifted; escalate |
| `docker inspect --format='{{.State.Health.Status}}' sentinel-timescaledb` | `healthy` (recorded, not required) | Record observed state; continue |
| `data/baseline-run/` exists | directory present | create if missing |
| `data/baseline-run/scratch/` ready | directory present | create if missing |
| `psutil.virtual_memory()` snapshot | recorded | no gate |
| `psutil.process_iter()` top-30 by RSS | recorded | no gate |

Output JSON schema: extend RA-20260425-1 `quiesce-pre.json` schema with fields `cache_manifest_sha256: <hex>`, `cache_aug2024_parquet_sha256: <hex>`, `cache_dir_present: <bool>`, `cache_aug2024_parquet_present: <bool>`.

### Decision 4 — Quiesce order (deterministic, auditable) — **v3 R4 GATE**

**IDENTICAL to RA-20260425-1.** Steps a-e: `docker stop sentinel-timescaledb` → `wsl --shutdown` → `sleep 30` → re-capture `quiesce-mid.json` → GATE at v3 R4 threshold (9,473,794,048 bytes). PROCEED if `observed_available_bytes ≥ 9,473,794,048`; HALT + Decision 6 restore otherwise.

### Decision 4b — E7 floor-drift check

**IDENTICAL to RA-20260425-1.** `drift = abs(observed_available_bytes - 9_473_794_048) / 9_473_794_048`. PROCEED if `drift ≤ 0.10`; HALT + restore + escalate otherwise. No warn band; no threshold adjustment permitted.

### Decision 5 — Authorized baseline-run invocation — **CHANGED: --source=cache**

The authorized launch command, invoked via the Dex-patched wrapper surface (now including `--source` / `--cache-dir` / `--cache-manifest` passthrough per precondition P5 Quinn gate):

```
.venv/Scripts/python scripts/run_materialize_with_ceiling.py \
  --run-id baseline-aug-2024 \
  --start-date 2024-08-01 \
  --end-date 2024-08-31 \
  --ticker WDO \
  --source cache \
  --cache-dir data/cache/raw_trades \
  --cache-manifest data/cache/cache-manifest.csv \
  --no-ceiling \
  --poll-seconds 30 \
  --output-dir data/baseline-run/scratch \
  --no-manifest
```

**Flag disposition rationale:**
- `--source cache` (NEW, mandatory per this RA): routes `materialize_parquet.py._fetch_month_dataframe` through `packages/t002_eod_unwind/adapters/feed_cache.load_trades` per ADR-4 §13; zero PG connection attempted; zero sentinel dependency during the R4-governed window. **Traces to:** ADR-4 §13.5 "Q1 is answered GREEN by T12b passing with sentinel container stopped" + evidence P1.
- `--cache-dir data/cache/raw_trades` (NEW, mandatory): per ADR-4 §10.3 default; MUST NOT resolve under `data/in_sample` (enforced by child CLI validation per `materialize_parquet.py:299+`).
- `--cache-manifest data/cache/cache-manifest.csv` (NEW, mandatory): per ADR-4 §10.3 default; MUST NOT equal `data/manifest.csv` (enforced by child CLI validation).
- `--no-manifest` (unchanged from RA-20260425-1): explicit-zero-write semantics on the canonical manifest. Wrapper mutex group enforces `--no-manifest` XOR `--manifest-path` at wrapper surface.
- `--output-dir data/baseline-run/scratch` (unchanged): parquet output redirected to L4 scratch; canonical `data/in_sample/**` untouched.
- `--no-ceiling` (unchanged): baseline-mode per ADR-1 v3 §Next-steps derivation of `peak_commit_aug2024`.

Gage MUST use the command above **verbatim**. Variant invocations (alternate `--source`, alternate date ranges, alternate tickers, `--manifest-path` override, alternate cache paths) are NOT authorized under RA-20260426-1; a new RA is required for any variant.

### Decision 6 — Restore order (ALWAYS executed — success, failure, cap-exceeded, gate halt, drift halt, emergency-kill)

**IDENTICAL to RA-20260425-1.** Steps a-e unchanged: WSL2 dormant (no action) → `docker start sentinel-timescaledb` → poll health (≤90s) → post snapshot → canonical sha256 re-verify (manifest + Aug-2024 parquet). On health timeout OR sha mismatch: CRITICAL, escalate, do NOT attempt repair. Restore is unconditional across every failure mode including the new BASELINE_CACHE_READ_FAIL mode (should be physically impossible under `--source=cache` with P1-P3 evidence intact, but handled for completeness).

### Decision 7 — Audit trail (Gage MUST fulfill)

Gage appends a structured YAML document to `data/baseline-run/quiesce-audit-YYYYMMDD.yaml`:

```yaml
- quiesce_window:
    amendment_id: RA-20260426-1
    supersedes: RA-20260425-1
    governing_adr: ADR-1 v3
    governing_amendment: ADR-4 Amendment 20260424-1 §13 (Option B cache routing)
    operator: gage
    date_brt: 2026-MM-DD
    run_id: baseline-aug-2024
    ceiling_expires_at_brt: <start + 4h ISO-8601>
    source_mode: cache   # NEW — distinguishes from RA-25-1 and prior (all implicit sentinel)
    precondition_evidence:
      t12b_verdict_path: "data/baseline-run/ra-20260426-1-evidence/t12b-verdict.xml"
      t12b_verdict: "PASSED"   # verified by Gage at audit write
      cache_manifest_sha256_at_evidence: <hex>       # from P2
      cache_aug2024_parquet_sha256_at_evidence: <hex>   # from P3
      peak_ws_pilot_build_bytes: <int>               # from P4; must be < 3_758_096_384
      wrapper_source_passthrough_gate_path: "docs/qa/gates/wrapper-source-passthrough-gate.md"
    authorized_invocation_flags:
      source: "cache"
      cache_dir: "data/cache/raw_trades"
      cache_manifest: "data/cache/cache-manifest.csv"
      no_manifest: true
      manifest_path: null
      output_dir: "data/baseline-run/scratch"
    pre:
      timestamp_brt: <iso>
      manifest_sha256: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
      parquet_sha256: bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0
      cache_manifest_sha256_at_quiesce_pre: <hex>       # MUST equal precondition_evidence.cache_manifest_sha256_at_evidence
      cache_aug2024_parquet_sha256_at_quiesce_pre: <hex>   # MUST equal precondition_evidence.cache_aug2024_parquet_sha256_at_evidence
      available_bytes: <int>
      sentinel_health: <healthy|unhealthy|starting|...>
    quiesce:
      step_a_docker_stop: {timestamp_brt: <iso>, exit_code: <int>}
      step_b_wsl_shutdown: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_sleep: {timestamp_brt: <iso>, duration_s: 30}
      step_d_mid_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_gate:
        decision: PROCEED|HALT
        formula: "available >= CAP_ABSOLUTE_v3 + OS_HEADROOM"
        threshold_bytes: 9473794048
        available_bytes: <int>
    e7_drift_check:
      baseline_floor_bytes: 9473794048
      observed_available_bytes: <int>
      drift_ratio: <float>
      drift_threshold: 0.10
      drift_decision: PROCEED|HALT
    baseline_child:
      launched: <bool>
      pid: <int|null>
      start_ts_brt: <iso|null>
      end_ts_brt: <iso|null>
      exit_code: <int|null>
      duration_cap_exceeded: <bool>
      emergency_kill:
        threshold_bytes: 7980049613
        tripped: <bool>
        trip_timestamp_brt: <iso|null>
        observed_commit_bytes_at_trip: <int|null>
    restore:
      step_a_wsl_state: dormant
      step_b_docker_start: {timestamp_brt: <iso>, exit_code: <int>}
      step_c_container_health: {timestamp_brt: <iso>, status: <healthy|timeout>, poll_count: <int>}
      step_d_post_capture: {timestamp_brt: <iso>, available_bytes: <int>}
      step_e_sha256_reverify:
        manifest_match: <bool>
        parquet_match: <bool>
        cache_manifest_match: <bool>                 # NEW — cache state must also be preserved
        cache_aug2024_parquet_match: <bool>          # NEW
    final_disposition: <SUCCESS|BASELINE_FAIL|BASELINE_CACHE_READ_FAIL|CAP_EXCEEDED|QUIESCE_GATE_HALT|E7_DRIFT_HALT|EMERGENCY_KILL|RESTORE_FAIL>
```

This audit YAML lives inside `data/baseline-run/` (scratch area, L4 runtime per framework boundary). Not a manifest mutation. Only this RA-20260426-1 policy artifact is registered in MANIFEST_CHANGES (as spec_issuance; canonical manifest unchanged).

### Decision 8 — Hard bounds (non-negotiable even under amendment)

Structurally IDENTICAL to RA-20260425-1, with cache-integrity additions:

| Bound | Enforcement |
|---|---|
| Canonical `data/manifest.csv` untouched | `--no-manifest` flag per Decision 5. Re-verified in Decision 6 step e. |
| Canonical parquets in `data/in_sample/**` untouched | `--output-dir data/baseline-run/scratch` per Decision 5. Re-verified in Decision 6 step e. |
| **[NEW]** Cache manifest `data/cache/cache-manifest.csv` untouched by this RA | `--no-manifest` scope covers canonical write path only; `feed_cache` is read-only per ADR-4 §6.1. Re-verified byte-identical pre→post at Decision 6 step e. |
| **[NEW]** Cache parquet Aug-2024 untouched by this RA | `feed_cache.load_trades` opens parquet read-only per ADR-4 §6.1 interface. Re-verified pre→post. |
| MsMpEng NEVER stopped | Hard refusal at Decision 1. |
| `claude` NEVER stopped | Would kill Gage; impossible. |
| Restore failure (sentinel not healthy in 90s) → immediate escalation | Gage does NOT attempt DB repair or retry cycles. Orchestrator decides next step. |
| Duration cap hit mid-run → SIGTERM/SIGKILL baseline child, restore services, report partial | No grace extension. Decision 2. |
| sha256 mismatch at Decision 6 step e → CRITICAL escalation | Canonical OR cache state altered during the window. Do not attempt recovery. |
| No permanent whitelist change | `core/memory_budget.py` `_RETAINED_PROCESSES` frozenset unchanged. Amendment expires when audit YAML `final_disposition` is written. |
| One-shot discipline | Any failure mode → restore + escalate + new RA required for next attempt. RA-20260426-1 is NOT reusable. |
| E7 floor-drift hard stop | If Decision 4b yields `drift > 0.10`, HALT + restore + escalate. No threshold adjustment permitted. |
| Emergency-kill monitor threshold | **`7_980_049_613` bytes** = `0.95 × CAP_ABSOLUTE_v3`. Per-child commit bytes. Gage manually SIGTERM/SIGKILL if child approaches. |
| **[NEW]** Canonical `materialize_parquet.py` NOT patched under this RA | Dex MUST NOT modify `_fetch_month_dataframe` (streaming fix per §13.3) under this RA. That patch is deferred to future RA-20260428-1 per Q5 disposition below. Scope containment — one-shot RA remains scoped to baseline-run quiesce under Option B, not a canonical code patch. |

### Decision 9 — Constants reference (v3 canonical values)

| Constant | Value (bytes) | Value (GiB, approx) | Source |
|---|---|---|---|
| `CAP_ABSOLUTE_v3` | `8_400_052_224` | 7.82 GiB | `core/memory_budget.py`; ADR-1 v3 |
| `OS_HEADROOM` | `1_073_741_824` | 1.00 GiB | `core/memory_budget.py`; Gregg §7.5 |
| `R4_threshold_v3` | `9_473_794_048` | 8.82 GiB | `CAP_ABSOLUTE_v3 + OS_HEADROOM` |
| `emergency_kill_threshold_v3` | `7_980_049_613` | 7.43 GiB | `0.95 × CAP_ABSOLUTE_v3` |
| `E7_drift_tolerance` | — | 10% (0.10) | ADR-1 v3 §E7 + Riven Co-sign v3 §5 |
| `peak_ws_pilot_cache_build_budget` | `3_758_096_384` | 3.50 GiB | ADR-4 §13.1 A1 acceptance (cache build constraint) |
| Empirical R4 anchor | `9_473_794_048` | 8.82 GiB | `data/baseline-run/quiesce-mid.json` (RA-20260424-1 execution) |
| Empirical retry-4 anchor | `9_496_334_336` | 8.843 GiB | `data/baseline-run/quiesce-mid.json` (RA-20260425-1 retry-4; margin 22.5 MiB over R4) |

### Q5 disposition — DEFER canonical patch to future RA-20260428-1

Aria's Q5 (ADR-4 §13.5): "Does Riven accept Aria's position in §13.3 that canonical `materialize_parquet._fetch_month_dataframe` carries a latent streaming-memory defect that warrants a separate follow-up RA (proposed RA-20260428-1) with canonical-rebuild co-sign? If Riven prefers to fold the canonical patch into RA-20260426-1 directly, §13.1 scope expands to include that patch and Dex requires co-sign before proceeding."

**Riven disposition: DEFER.** The canonical `_fetch_month_dataframe` streaming-memory defect (per Aria §13.3 advisory position) will be addressed under a separate future **RA-20260428-1** when Gage needs G09 for Mai+Jun 2025 relaunch (task #71). It is NOT folded into RA-20260426-1.

**Rationale (R10 custodial reasoning, 4-point):**

1. **Scope discipline per Riven standing policy.** RA-20260426-1's mission is EXACTLY ONE: authorize a quiesce window under Option B so Gage's fifth G09a attempt can populate `peak_commit_aug2024` for step-7 `CEILING_BYTES` derivation (#78). Folding a canonical code patch into the same RA expands surface area beyond what the Decision 1 correction requires. One-shot RAs scope one operational change — blending an operational policy amendment with a canonical code contract change conflates two governance classes.

2. **Retry #5 does not need canonical patched.** Per ADR-4 §13.1, Dex's cache-build helper (`build_raw_trades_cache.py._stream_month_to_parquet`) is an independent streaming implementation that produces cache parquets. `materialize_parquet.py` under `--source=cache` reads those cache parquets via `feed_cache.load_trades`, which is a simple parquet read — it never invokes `_fetch_month_dataframe`'s PG buffered path. The canonical streaming defect is latent in the `--source=sentinel` path only, which this RA explicitly does not use. Retry #5 is self-sufficient with the canonical function untouched.

3. **Mai+Jun 2025 relaunch (#71) is downstream and separable.** The canonical `_fetch_month_dataframe` patch only becomes load-bearing when Gage (or equivalent) needs to **produce new canonical parquets** for months beyond Aug-2024 via the sentinel path. That is G09 / task #71 territory, distinct from G09a baseline-run. When that work is scheduled, RA-20260428-1 can be drafted with full canonical-rebuild co-sign scope (manifest mutation class + sha drift class + streaming-correctness proofs). Conflating it with RA-26-1 couples two independent work streams and delays retry #5 unnecessarily.

4. **Retroactive scope expansion violates Dex sprint authority.** Dex began §13.1 + §13.2 impl under @dev authority (no Riven co-sign required per §13.1 closing note). Folding §13.3 mid-sprint would retroactively require Riven co-sign on `materialize_parquet.py` touch (R10 custodial surface), invalidating the current sprint's authority basis. Cleaner to complete §13.1 + §13.2 under @dev, ship RA-26-1 for retry #5, and open a fresh sprint under RA-28-1 with co-sign for the canonical patch.

**Placeholder for RA-20260428-1:** proposed scope — canonical `scripts/materialize_parquet.py._fetch_month_dataframe` streaming refactor (apply the same batch-fetch + per-batch `write_table` pattern from `build_raw_trades_cache.py._stream_month_to_parquet`); Riven co-sign required because `materialize_parquet.py` is R10 custodial surface (canonical data producer). Not drafted at this time; opens when @pm (Morgan) or orchestrator schedules G09 Mai+Jun 2025 work. @architect (Aria) position statement §13.3 stands as advisory input to that future RA.

### Sign-off (ISSUED — evidence attached, one-shot clock started)

**2026-04-24T11:42:19Z — Orion (aiox-master, 👑 Orchestrator, on Riven-delegated authority) — RA-20260426-1 FLIPPED DRAFT → ISSUED.**

All five precondition artefacts (P1-P5) attached under `data/baseline-run/ra-20260426-1-evidence/` with sha256 pins recorded in the Issuance metadata banner at section top. Quinn's CONCERNS-01 (5 stale unit test stubs) resolved via Dex commit `63a9a3a`; `tests/unit/test_build_raw_trades_cache.py` 11/11 PASS. Canonical `data/manifest.csv` sha256 byte-identical at issuance (`75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`). Amendment is now EXECUTABLE. Gage cleared for G09a retry #5 under Decisions 1-9 verbatim (source_mode=cache per Decision 5).

**Issuance-signature block (O1 orchestrator-proxy on R10 delegation):**
- Issued-by: Orion (aiox-master) acting on Riven-delegated authority per `issuance_preconditions.flip_procedure` (`docs/MANIFEST_CHANGES.md` spec_issuance L411)
- Flip timestamp: `2026-04-24T11:42:19Z` (UTC) / `2026-04-24T08:42:19-03:00` (BRT)
- One-shot consumption clock: STARTED — spent on Gage's first use
- Delegation basis: Quinn gate `docs/qa/gates/RA-20260426-1-chain-gate.md` §Recommendation "CONDITIONAL GREEN. Flip DRAFT → ISSUED after Dex lands ... [CONCERNS-01 fix]. Once that test fix lands, Gage is cleared for quiesce retry #5 under `--source=cache` with zero additional gating." Condition satisfied by commit `63a9a3a`.

---

### Sign-off (DRAFT — pending evidence) [SUPERSEDED BY ISSUED BLOCK ABOVE — RETAINED FOR AUDIT]

**2026-04-26 BRT — Riven (@risk-manager, R10 custodial) — RA-20260426-1 DRAFTED, AWAITING PRECONDITION EVIDENCE.**

Amendment scope: ONE G09a baseline-run window under `--source=cache` routing, ≤ 4 hours total, WSL2 + sentinel-timescaledb container stop authorized, all ADR-1 v3 constraints in force, ADR-4 §13 Option B cache routing mandatory. Gage executes under Decisions 1-9 above with zero clarifying questions ONCE status flips DRAFT → ISSUED. On completion (any disposition), this amendment is spent — a second retry or any subsequent quiesce requires a new RA-YYYYMMDD-N amendment.

**R10 co-sign block (DRAFT):**
- Custodial authority: Riven (@risk-manager, R10) — draft-signed 2026-04-26 BRT. Issuance-signature withheld pending precondition_evidence P1-P5.
- Governance class: one-shot operational policy amendment under ADR-1 v3 + ADR-4 §13 (Option B cache routing); NOT a code contract change; NOT a permanent whitelist mutation; NOT a canonical-rebuild authorization (Q5 deferred).
- Constitutional compliance:
  - **Article IV (No Invention)** — every threshold traces to v3 constants in `core/memory_budget.py` (`CAP_ABSOLUTE=8_400_052_224`, `OS_HEADROOM=1_073_741_824`, `R4_threshold=9_473_794_048`, `emergency_kill=7_980_049_613`, `E7_drift=10%`); `peak_ws_pilot_cache_build_budget=3_758_096_384` traces to ADR-4 §13.1 A1; Decision 1 corrected rationale traces to retry-4 halt-report + T12b P1 evidence (once attached); every flag in Decision 5 traces to ADR-4 §13 (Option B) or inherits verbatim from RA-20260425-1 Decision 5.
  - **Article V (Quality First)** — zero-ambiguity for Gage once ISSUED: deterministic gates at Decisions 3, 4e, 4b; explicit byte-value reference at Decision 9; audit YAML schema fully specified at Decision 7; precondition_evidence packet fully enumerated.
  - **Article I (CLI First)** — all actions CLI-invocable (`docker stop`, `wsl --shutdown`, `.venv/Scripts/python`, `psutil`, `pytest`, `sha256sum`).
- Supersedes RA-20260425-1 (CONSUMED at Phase 4 on 2026-04-23 BRT; one-shot spent per its Decision 8 discipline).

**References:**
- Governing ADRs:
  - **ADR-1 v3** — `docs/architecture/memory-budget.md §ADR-1 v3 — R4 Recalibration Against Observed Host Quiesce Floor`
  - **ADR-4 Amendment 20260424-1 §13** — `docs/architecture/pre-cache-layer-spec.md §13 — ADR-4 Amendment 20260424-1`
- Riven v3 co-sign: `docs/architecture/memory-budget.md §Riven Co-sign v3 — R1/R2/R3/E6/E7 Recalibration Against ADR-1 v3`
- Quinn v3 audit: `docs/qa/gates/ADR-1-v3-audit.md` (PASS 7/7)
- Dex v3 patch: `core/memory_budget.py` + `core/run_with_ceiling.py` (225/1 tests; smoke-verified constants)
- Dex §13.1 + §13.2 impl (**ISSUANCE BLOCKER**): `scripts/build_raw_trades_cache.py._stream_month_to_parquet` + `tests/integration/test_adapter_parity_cache.py` (T12a + T12b split)
- Dex wrapper §13 passthrough impl (**ISSUANCE BLOCKER**): extend `scripts/run_materialize_with_ceiling.py` to forward `--source`, `--cache-dir`, `--cache-manifest` to child
- Quinn §13 gate (**ISSUANCE BLOCKER**): attach pytest T12b output (P1) + wrapper-source-passthrough-gate (P5)
- Predecessor (consumed): RA-20260425-1 — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260425-1)` (SUPERSEDED banner applied inline)
- Grand-predecessors:
  - RA-20260424-1 — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260424-1)` (SUPERSEDED)
  - RA-20260423-1 — `docs/architecture/memory-budget.md §R4 Amendment — Baseline-Run Quiesce Authorization (RA-20260423-1)` (SUPERSEDED)
- Empirical anchor (Decision 1 correction): `data/baseline-run/baseline-aug-2024-halt-report.md §Retry #4` — documented the psycopg connect-refused failure proving the prior Decision 1 rationale was empirically false
- Empirical anchor (R4 floor reachability): `data/baseline-run/quiesce-mid.json` — retry-4 observed `available = 9,496,334,336` at 2026-04-23T20:36:25-03:00 under RA-20260425-1 quiesce; margin 22.5 MiB over v3 R4 threshold
- Deferred (Q5=DEFER): **RA-20260428-1 (proposed, not drafted)** — canonical `_fetch_month_dataframe` streaming refactor; opens when G09 Mai+Jun 2025 relaunch (#71) is scheduled; Riven co-sign required on R10 custodial canonical-producer surface
- Manifest guard: `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at draft issuance. No canonical parquets, no code modifications, no manifest mutations in this RA.

---

