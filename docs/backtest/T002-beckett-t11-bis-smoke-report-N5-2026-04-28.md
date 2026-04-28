# T002.0h — Beckett T11.bis N5 Smoke Report (AC8 Strict-Literal, Post-ESC-010 Amendments)

> **Agent:** @backtester (Beckett the Simulator)
> **Story:** T002.0h — Warmup state-builder (AC8 exit gate)
> **Iteration:** N5 (5ª) — post ESC-010 mini-council 6/6 functional convergence
> **Spec version:** v0.2.3 (post PRR-20260428-1 + PRR-20260428-2)
> **Spec sha256:** `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8`
> **Generated (BRT):** 2026-04-28T09:19:20
> **Run ID:** `cpcv-dryrun-auto-20260428-c5d5a708acda` (UUID `50c4fe32602b448c943ca7277f1f08ef`)
> **Branch:** `t002-1-warmup-impl-126d`
> **Mode:** Autonomous, no push, no source modification

---

## 1. Executive verdict

**AC8 STRICT-LITERAL: PASS** (post-ESC-010 amendments PRR-20260428-1 + PRR-20260428-2).

| Sub-criterion | Threshold | N5 actual | Verdict |
|---|---|---|---|
| 8.5' CPCV exit code | == 0 | **0** | PASS |
| 8.6' Wall-time | < 5 min (300 s) | **4.381 s** | PASS |
| 8.7' Peak RSS | < 6 GiB | **0.140 GiB** (143.83 MiB) | PASS |
| 8.8' 5 artifacts persisted | sha256-stamped | **5/5 present** | PASS |
| 8.9' KillDecision verdict ∈ {GO, NO_GO} | F2-stub-OK redef | **NO_GO** (stub-degenerate) | PASS |

KillDecision verdict: **NO_GO** — explicitly annotated as **stub-degenerate per F2 redef** (PRR-20260428-2): AC8.9 verifies **PIPELINE INTEGRITY**, NOT strategy edge. Mira authority statement (ESC-010 council) established that stub `make_backtest_fn` returning identity-zero PnL produces this exact NO_GO signature — the pipeline executed end-to-end (warmup → events → 5×45 fan-out → KillDecision) without abort, which is what AC8 validates.

---

## 2. Pre-flight (8 checks)

| # | Check | Result |
|---|---|---|
| 1 | Python + psutil | Python 3.14.3, psutil 7.2.2 — PASS |
| 2 | `BUILDER_VERSION == "1.0.0"` | `packages/t002_eod_unwind/warmup/__init__.py:46` confirmed — PASS |
| 3 | `data/manifest.csv` (sha + count) | sha256 `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`, 18 entries (2024-01..2025-06) — PASS |
| 4 | Parquets in-sample 2024-08..2025-06 (~11 meses) | `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` ✅ + `…/year=2025/month=06/wdo-2025-06.parquet` ✅ + months between — PASS |
| 5 | State files (dated JSONs + sidecars + audit) | `_cache_key_2024-08-22.json` ✅, `atr_20d_2024-08-22.json` ✅, `percentiles_126d_2024-08-22.json` ✅, `_cache_key_2025-05-31.json` ✅, default-path JSONs (mtime 2026-04-27 23:58) ✅, `cache_audit.jsonl` chains miss→write→hit ✅ — PASS |
| 6 | Spec sha (post 2 PRRs) | `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8`; revisions PRR-20260428-1 (`6fda5cbc…`) + PRR-20260428-2 (`e55b0d5f…`) confirmed in `preregistration_revisions[]`; `to_version: 0.2.3` reached — PASS |
| 7 | Calendar + cost-atlas | `config/calendar/2024-2027.yaml` present; cost-atlas wired via `engine_config_sha256=9a97e8f8…` in determinism stamp — PASS |
| 8 | Hold-out lock 2025-07-01 / 2026-04-21 UNTOUCHED | `data/in_sample/year=2025/` stops at `month=06`; no `holdout/` or `out_of_sample/` dirs created/modified during N5; `_holdout_lock` modules present and unmodified — PASS |

**Pre-flight 8/8 PASS.** All artifacts cached from prior phases (no precompute needed).

---

## 3. N5 amended invocation (literal per PRR-20260428-1 — sem `--smoke`)

```
python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --in-sample-start 2024-08-22 \
  --in-sample-end 2025-06-30
```

**Started (BRT):** 2026-04-28T09:19:16.559586
**Ended (BRT):** 2026-04-28T09:19:20.940 (approx)
**Wall-clock:** **4.381 s** (psutil-instrumented Popen wrapper)
**Exit code:** **0**
**Peak RSS:** **143.83 MiB = 0.140 GiB** (psutil 0.5s poll, 9 samples)
**Output dir:** `data/baseline-run/cpcv-dryrun-auto-20260428-c5d5a708acda/`

No subsample. No engine config modification. No source modification. Honest peak RSS reported.

---

## 4. AC8 sub-criteria evaluation (post-ESC-010 amendments)

### 8.5' CPCV exit code 0 — PASS

Process returned **0**. No `--smoke` flag → AC11 abort path not engaged (per E2 amendment). No HALT (mem soft-cap 6 GiB not approached; warmup gate passed; hold-out lock not violated). No DETERMINISM exit (no prior run in same `--run-id` dir to compare against).

### 8.6' Wall-time < 5 min — PASS

**4.381 s** observed (vs 300 s budget). Within ~5% of N4 DIAGNOSTIC anchor (4.596 s). Variance attributable to warm OS cache vs N4 cold start.

Telemetry breakdown:
- `init` → `events_start`: ~0 ms
- `events_built` (n_events=3800): ~10 ms after start
- `fanout_start` → `fanout_complete`: 1464 ms (5 trials × 45 paths)
- `report_complete` → `run_end`: <100 ms

### 8.7' Peak RSS < 6 GiB — PASS

**0.140 GiB observed** vs 6 GiB soft halt. **42.9× headroom**. Telemetry RSS column max = 143.99 MiB; psutil parent+children poller saw same (no subprocess ballooning). R3 false-positive risk on Windows is moot — orders of magnitude below cap.

### 8.8' 5 artifacts persisted (sha256-stamped) — PASS

| Artifact | Bytes | sha256 |
|---|---|---|
| `determinism_stamp.json` | 709 | `5c245ed338225b963d2d426f87296c5e6039f75baed417ff50e26f5b821ccd60` |
| `events_metadata.json` | 331 | `a4337d806cd7fed21cb77095c1b26ed78c9aa4d1532f783a4987626c44fe745d` |
| `full_report.json` | 3673 | `7e2b43d5ecd5f4a3f221162b6c60ef3094ae55cc5aad9eb5fd9dfa8db92fdb3f` |
| `full_report.md` | 1025 | `0f9c4eb38bcc036a8175c610f8055db056465fc4cbff46713842adebe6d94381` |
| `telemetry.csv` | 1125 | `992bb46ac21e7a902fa0d5a290a8cdb9efbbeed5f5222947d6344504ea13ed39` |

All 5 files present, non-empty, well-formed JSON/CSV/MD. `determinism_stamp.spec_sha256` matches the on-disk spec (`72261326…`), confirming N5 ran against the post-amendment v0.2.3 spec. `full_report.md` carries label `T002-v0.2.3` (derived from preregistration revision chain, top-level `version` field still `0.2.0` as documented behavior — the canonical version for the report comes from latest revision `to_version`).

### 8.9' KillDecision verdict ∈ {GO, NO_GO} — PASS (F2-stub-OK annotation)

**Verdict: NO_GO** (stub-degenerate signature).

```
K1 (DSR > 0):       PASS  (DSR = 0.500000, neutral baseline from null bootstrap)
K2 (PBO < 0.4):     FAIL  (PBO = 0.500000 — symmetric flip, stub-deterministic)
K3 (IC decay):      FAIL  (IC_in_sample = 0.000000 — non-positive, stub returns zero edge)
```

**F2-stub-OK annotation (per PRR-20260428-2, ESC-010 council Mira authority):**

> AC8.9 verifies **PIPELINE INTEGRITY**, NOT strategy edge. The current `make_backtest_fn` is a stub returning identity-zero PnL across all 225 path-trials (45 paths × 5 trials). This produces the exact mathematical signature observed: IC=0 (no signal), Sharpe=0 (no return), PBO=0.5 (perfectly symmetric null-distribution flip rate), DSR=0.5 (Bonferroni-deflated centerpoint of null bootstrap). The KillDecision pipeline correctly emitted `NO_GO` with two specific failure reasons, demonstrating that:
>
> - the warmup gate fired (`warmup_gate_as_of: "2024-08-22"`, `warmup_gate_passed_at_brt`);
> - events were built (n_events=3800);
> - 5-trial × 45-path fan-out executed (n_per_path_results=225, fanout_duration_ms=1464);
> - `compute_full_report` consumed all metrics including squad-cumulative DSR + BBLZ PBO;
> - `KillDecision` emitted a structured verdict with K1/K2/K3 disaggregation and reasons array.
>
> This is **wiring validation**, not edge claim. Strategy edge will be validated by T002.1.bis (real `make_backtest_fn`) and T002.0h.1 (E1 harness amend). Both spawned non-blocking from ESC-010.

The verdict `"NO_GO"` ∈ {GO, NO_GO} per AC8.9 amended literal → **PASS**.

---

## 5. Determinism + provenance audit

| Field | Value |
|---|---|
| `seed` | 42 |
| `simulator_version` | `cpcv-dry-run-T002.0f-T3` |
| `dataset_sha256` | `e3962eb80d83e1928f1a26fda5fb3f0c3d243456b63a0bc693eb067b62545c99` |
| `spec_sha256` | `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8` |
| `engine_config_sha256` | `9a97e8f8734cbb8cd35362d7a336fe876a5b16257a170b9436d9e868ad946c81` |
| `cpcv_config_sha256` | `d2ea61f29d7ccb4c86cb6447d957d3ea2563897599f3e142a55258123680acc3` |
| `python_version` | 3.14.3 |
| `numpy_version` | 2.4.2 |
| `pandas_version` | 2.3.3 |
| `n_trials_source` | `docs/ml/research-log.md@359844528d7768b9ea7642708d32d13fc08ab9ba` |

`rollover_calendar_sha256` and `cost_atlas_sha256` are `null` in stamp — these are subsumed under `engine_config_sha256` per current wiring; not a regression vs N1-N4.

---

## 6. Comparison vs N1/N2/N3/N4 chain

| Iteration | Date | Verdict | Wall | Peak RSS | Exit | Failure mode |
|---|---|---|---|---|---|---|
| N1 | 2026-04-26 | HOLD WARM_UP_IN_PROGRESS | n/a | n/a | n/a | Warmup not built — baseline state |
| N2 | 2026-04-27 (243bcad) | **FAIL** | n/a | n/a | n/a | `_split_yaml_blocks` parser inversion → ESC-007 |
| N3 | 2026-04-27 (ea491f6+3598445) | **FAIL** | n/a | n/a | n/a | Warmup as_of=2024-07-01 missing → ESC-008→ESC-009 |
| N4 | 2026-04-28 | **FAIL** (strict-literal) | 4.596 s | ~0.14 GiB | 0 (DIAGNOSTIC) | WarmUpGate singleton + default-path binding bug; AC8 spec literal called for `--smoke` which engaged AC11 abort path → ESC-010 dual-track |
| **N5** | **2026-04-28** (this report) | **PASS strict-literal** | **4.381 s** | **0.140 GiB** | **0** | — |

**Chain resolution:** ESC-010 mini-council 6/6 functional convergence on E2 + F2-with-binding-F3 amendments unblocked the literal-literal interpretation: drop `--smoke` from invocation (E2) + redefine 8.9 as pipeline integrity (F2). N5 replicates the empirical signature of the N4 DIAGNOSTIC run (which was already exit=0 + 5 artifacts + KillDecision=NO_GO when invoked without `--smoke`), now under the formal post-amendment spec v0.2.3 with all pre-flight checks intact.

**Pipeline determinism:** N5 metrics (PBO=0.5, DSR=0.5, IC=0, NO_GO) are bit-equivalent to N4 DIAGNOSTIC metrics — confirms the stub identity-zero engine is deterministic across runs (seed=42). Different `run_id` UUIDs (`50c4fe32…` vs N4) reflect timestamp-based hash, not non-determinism.

---

## 7. §9 HOLD #1 clearance criteria assessment (engineering layer)

Per ESC-010 council, §9 HOLD #1 (engineering exit gate) clearance is gated on AC8 strict-literal PASS plus collateral artifacts. Beckett assessment:

| Criterion (engineering) | N5 evidence | Status |
|---|---|---|
| AC8 strict-literal PASS | All 9 sub-criteria 8.5'-8.9' PASS (this report §1, §4) | CLEARED |
| Pipeline integrity end-to-end | warmup gate → events_built (3800) → fan-out (225 results, 1464 ms) → KillDecision emitted with K1/K2/K3 disaggregation | CLEARED |
| Reproducibility footprint | seed=42, spec_sha=`72261326…`, dataset_sha=`e3962eb8…`, simulator_version, python/numpy/pandas pinned | CLEARED |
| Hold-out untouched | `data/in_sample/year=2025/` ends at `month=06`; no holdout dir mutation; `_holdout_lock` modules unchanged | CLEARED |
| Memory safety | 0.140 GiB peak vs 6 GiB cap (42.9× headroom) | CLEARED |
| Wall-time budget | 4.381 s vs 300 s (68.5× headroom) | CLEARED |

**Engineering layer clearance: GO for §9 HOLD #1 disarm by Riven + Mira.**

**Out of scope for Beckett (do not represent as cleared):**
- Strategy edge validation (deferred to T002.1.bis with real `make_backtest_fn`)
- Capital ramp authorization (gated by NEW §9 HOLD #2 — Riven custodial authority, 5 disarm gates)
- Phase F unblock (gated by §9 HOLD #2 — NOT cleared by N5 alone)

---

## 8. Anti-Article-IV self-audit

| Guard | Status |
|---|---|
| No subsample | PASS — full window 2024-08-22..2025-06-30 (n_events=3800) |
| No engine config modification | PASS — `engine_config_sha256` matches pre-flight expectation |
| No improvisation | PASS — invocation literal per PRR-20260428-1 |
| Honest peak RSS | PASS — 0.140 GiB reported as observed, not guessed |
| No source code mutation | PASS — `git status` shows only docs/state edits, no `packages/`/`scripts/` source changes during N5 run |
| No push | PASS — local-only; @devops Gage is push gate |

---

## 9. Limitations & confidence tags

- **[F2-stub-degenerate]** AC8.9 verdict NO_GO is structurally guaranteed by the stub `make_backtest_fn`. Real strategy-edge claim requires T002.1.bis completion. This is a documented and council-approved limitation, not a backtest defect.
- **[engine_config_sha256 single-hash]** rollover_calendar and cost_atlas individual sha256 not separately stamped — subsumed under engine_config. Acceptable for N5; future stamping refinement = housekeeping.
- **[no `simulator_changelog`]** Beckett-side simulator changelog (`docs/backtest/simulator-changelog.md`) not updated in this run — deferred to post-clearance housekeeping; does not affect AC8.

---

## 10. Recommendation

**AC8 strict-literal: PASS.** Engineering exit gate clear from Beckett's authority. Recommend handoff to:

1. **Riven (@risk-manager)** + **Mira (@ml-researcher)** to formally disarm §9 HOLD #1 and arm §9 HOLD #2 (capital ramp barrier with 5 disarm gates).
2. **Pax (@po)** to update story T002.0h status (InReview → Done conditional on Riven+Mira concurrence).
3. **Phase F remains BLOCKED** by NEW §9 HOLD #2 (capital ramp barrier) — Beckett does not represent N5 as Phase F unblock.

Non-blocking parallel work (already spawned per ESC-010): T002.0h.1 (E1 harness amend) + T002.1.bis (real `make_backtest_fn`).

---

— Beckett, reencenando o passado 🎞️
