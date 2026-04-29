# T002.0h.1 — Beckett T11.bis N+1 Smoke Report (Post Dex E1 Per-Phase WarmUpGate Fix)

> **Agent:** @backtester (Beckett the Simulator)
> **Story:** T002.0h.1 — Per-phase WarmUpGate + dated path resolvers (AC1–AC10)
> **Iteration:** N+1 (sixth in chain N1→N2→N3→N4→N5→**N+1**) — first iteration post Dex T2 impl commit `6a78b88`
> **Spec version:** v0.2.3 (post PRR-20260428-1 + PRR-20260428-2)
> **Spec sha256:** `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8`
> **Run ID:** `cpcv-dryrun-auto-20260428-c5d5a708acda` (UUID `9f5b545a29794ade820e8649366b3a7b` for full phase determinism stamp)
> **Run start (BRT):** 2026-04-28T20:34:19
> **Run end (BRT):** 2026-04-28T20:34:23 (run_end telemetry event, sample 15)
> **Branch:** `t002-1-warmup-impl-126d`
> **Mode:** Autonomous, no push, no source modification, T5 within T002.0h.1 task plan
> **Empirical evidence:** orchestrator-supplied (Pax-witnessed N+1 launch wrapper) — Beckett T5 = formalisation, not re-execution

---

## 0. Authority + scope

**T5 = AC9 N+1 empirical exit gate verdict (consumer + simulation realism).**

Beckett does NOT re-execute. The N+1 run already landed on disk via the orchestrator-supervised launch (`run_id` reused vs N5 by design — same `out_dir`, smoke artifacts added via new `out_dir/smoke/` subdir per Dex E1 implementation in `scripts/run_cpcv_dry_run.py:1065-1073`). N+1 artifacts **overwrote N5 root artifacts** (mtimes 2026-04-28T20:34 vs N5 09:19); N5 evidence preserved exclusively in `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md` sha256s.

**Out of scope (Beckett):** strategy-edge claim (deferred T002.1.bis); spec mutation (Pax T6); push (Gage); custodial dual-sign (Riven post-T6).

---

## 1. Executive verdict

**T002.0h.1 AC9 STRICT-LITERAL: PASS** (engineering exit gate cleared; F2-stub-OK annotation retained).

| AC9 sub-criterion | Threshold | N+1 actual | Verdict |
|---|---|---|---|
| 1 — Exit code | == 0 | **0** | PASS |
| 2 — Wall-time total (smoke + full) | < 90 s (story envelope; Mira T0 anchor < 5 min) | **3.910 s** observed* | PASS |
| 3 — Smoke phase exit success | no early HALT on `--smoke` branch | smoke_complete telemetry event (sample 8) NO_GO verdict, no halt | PASS |
| 4 — Full phase exit success | full_complete telemetry event present | full_complete telemetry event (sample 14) NO_GO verdict, no halt | PASS |
| 5 — Smoke as_of binding | 2025-05-31 | smoke determinism_stamp + events_metadata.warmup_gate_as_of = `2025-05-31` | PASS |
| 6 — Full as_of binding | 2024-08-22 | full determinism_stamp + events_metadata.warmup_gate_as_of = `2024-08-22` | PASS |
| 7 — Audit JSONL phase-tagged 2 entries (AC3) | smoke first, full second, ordered AC10/AC11 | `state/T002/cache_audit.jsonl` lines 3–4 (run window 20:34) — `phase:"smoke"` 20:34:19 then `phase:"full"` 20:34:21 | PASS |
| 8 — 5 artifacts persisted at run root (sha256-stamped, full phase) | 5 files at `data/baseline-run/cpcv-dryrun-{run_id}/` | 5/5 — full phase artifacts at root + telemetry.csv covering both phases | PASS |
| 9 — Smoke phase artifacts persisted (sha256-stamped) | 4 files at `out_dir/smoke/` (architectural — telemetry.csv is run-level, written once by MemoryPoller per `persist_artifacts` docstring `scripts/run_cpcv_dry_run.py:764-767`) | 4/4 at `cpcv-dryrun-auto-20260428-c5d5a708acda/smoke/` | PASS (architectural footnote — see §3 "5 vs 4 ambiguity") |
| 10 — KillDecision verdict ∈ {GO, NO_GO} | F2-stub-OK redef | smoke = `NO_GO`; full = `NO_GO` (both stub-degenerate per F2) | PASS |

\* Wall-time = 3.910 s computed from telemetry sample 1 (`run_start` at 2026-04-28T20:34:19) → sample 15 (`run_end` at 2026-04-28T20:34:23). The 7.489 s wall-time supplied in the orchestrator T5 brief reflects an outer wrapper window; the inner orchestrator instrumentation (psutil poller) records 3.910 s end-to-end from `run_start` to `run_end`. Both are vastly under the 90 s sub-criterion budget.

**N+1 verdict: PASS (10/10 sub-criteria).** Engineering exit gate clear. KillDecision NO_GO is **stub-degenerate** per F2 ESC-010 redef (PRR-20260428-2): pipeline integrity validated end-to-end, strategy edge clearance deferred to T002.1.bis.

---

## 2. Pre-flight (orchestrator-validated, per T5 brief)

| # | Check | Result |
|---|---|---|
| 1 | Source/spec/calendar/cost-atlas hashes | Per determinism_stamp: spec_sha=`72261326…`, engine_config_sha=`9a97e8f8…`, cpcv_config_sha=`d2ea61f2…` — UNCHANGED from N5 |
| 2 | Cached warmup states present (both as_of) | `state/T002/atr_20d_2024-08-22.json` ✅ + `state/T002/percentiles_126d_2024-08-22.json` ✅ + `state/T002/atr_20d_2025-05-31.json` ✅ + `state/T002/percentiles_126d_2025-05-31.json` ✅ + sidecars `_cache_key_2024-08-22.json` + `_cache_key_2025-05-31.json` ✅ |
| 3 | Hold-out lock 2025-07-01 / 2026-04-21 UNTOUCHED | `data/in_sample/year=2025/` ends `month=06`; `_holdout_lock` modules unmodified per `git status` |
| 4 | Dex T2 commit landed | `6a78b88 feat(t002.0h.1): E1 per-phase WarmUpGate + dated path resolvers (AC1-AC10)` — current HEAD-1 (HEAD is impl commit; T2 work) |
| 5 | Quinn T3-T4 PASS 7/7 | per orchestrator brief; not re-asserted by Beckett |
| 6 | Audit JSONL N+1 window | lines 3-4 timestamped 2026-04-28T20:34:19 (smoke) + 20:34:21 (full) match telemetry sequence |

**Pre-flight 6/6 PASS** (delegated to orchestrator + Quinn upstream; Beckett verifies on-disk evidence only).

---

## 3. Architectural clarification — "5 artifacts" semantics under E1 multi-phase regime

**Spec literal (T002.0h.1 AC9 L80):** "5 artifacts persisted in `data/baseline-run/cpcv-dryrun-{run_id}/`". Path explicitly = run root, NOT `/smoke/`.

**Implementation (post-Dex T2):** `persist_artifacts(out_dir, ...)` writes 4 JSON/MD files; the 5th artifact `telemetry.csv` is written by `MemoryPoller` at the run-level (single CSV containing both phase-tagged event series), per docstring `scripts/run_cpcv_dry_run.py:764-767`:

> "Per AC12 — telemetry.csv is written by MemoryPoller; this writes the other 4 artifacts."

**Result on disk (N+1):**
- Run root (`out_dir/`): 5 files = `determinism_stamp.json` + `events_metadata.json` + `full_report.json` + `full_report.md` + `telemetry.csv` ← **maps to AC9 strict-literal "5 artifacts"**
- Smoke subdir (`out_dir/smoke/`): 4 files = same 4 JSON/MD set, sans telemetry (telemetry is shared at root)

**Strict-literal reading of AC9:** PASS at run root (5/5). The smoke 4-artifact subdir is **architectural correctness**, not a deficiency — `telemetry.csv` covers smoke window via phase-tagged rows (samples 3–8 in the run-level CSV, all `note` prefixed `smoke:*`). Sub-criterion #9 in the T5 brief table is satisfied as 4/4 + 1 shared (sub-criterion-#8 telemetry counted once at run root, semantically covers both phases).

This is consistent with N4 DIAGNOSTIC anchor (`cpcv-dryrun-T002-N4-DIAG-NOSMOKE/` = 5 files at root, no smoke dir because no `--smoke` flag in N4) and N5 (same 5 files, no smoke dir). N+1 is the **first iteration with smoke + full both populating** under E1 per-phase architecture.

---

## 4. AC9 sub-criteria evaluation

### AC9.1 — Exit code 0 (PASS)

Process returned **0** per orchestrator-supplied evidence. Confirmed by absence of any HALT artifact, presence of `run_end` telemetry sample 15 with `note=halt_observed=False`. Both phases reached `*_complete` events.

### AC9.2 — Wall-time < 90 s (PASS)

| Stage | Telemetry samples | Δ time |
|---|---|---|
| Run start | sample 1 (run_start) → sample 3 (smoke:events_start) | < 1 s (same `2026-04-28T20:34:19` timestamp resolution) |
| Smoke events build (n_events=360) | sample 3 → sample 4 (smoke:events_built) | < 1 s |
| Smoke fan-out (5 trials × 45 paths = 225 results) | sample 5 → sample 6 (smoke:fanout_complete) | **1.620 s** (recorded `duration_ms=1620`, events_metadata.fanout_duration_ms=1620) |
| Smoke report + persist | sample 6 → sample 8 (smoke_complete) | < 1 s |
| Full events build (n_events=3800) | sample 9 → sample 10 (full:events_built) | < 1 s |
| Full fan-out (5 trials × 45 paths = 225 results) | sample 11 → sample 12 (full:fanout_complete) | **1.914 s** (recorded `duration_ms=1914`, events_metadata.fanout_duration_ms=1914) |
| Full report + persist | sample 12 → sample 14 (full_complete) | < 1 s |
| Run end | sample 14 → sample 15 (run_end) | < 1 s |
| **Total inner orchestrator** | sample 1 → sample 15 | **3.910 s** (telemetry timestamp delta `20:34:23.000` − `20:34:19.090` ≈ 3.91 s) |

Comparison vs sub-criterion budget: **3.910 s vs 90 s = 23× headroom.** Outer wrapper 7.489 s window (orchestrator brief) = 19× headroom. Either reading PASSES decisively.

### AC9.3 — Smoke phase exit success (PASS)

Telemetry sample 8 `note=smoke_complete,verdict=NO_GO`. No `smoke_failed`/`halt_after_smoke`/`smoke_aborted` event observed — AC11 protective abort path (`run_cpcv_dry_run.py:1054-1064`) NOT engaged. Full phase proceeded normally.

### AC9.4 — Full phase exit success (PASS)

Telemetry sample 14 `note=full_complete,verdict=NO_GO`. No `full_failed`/`full_halt`/`warmup_state_missing`/`warmup_state_corrupt` event. Soft-cap halt event absent (`halt_observed=False` in run_end note).

### AC9.5 — Smoke as_of = 2025-05-31 (PASS)

`out_dir/smoke/events_metadata.json`:

```json
{
  "phase": "smoke",
  "in_sample_start": "2025-05-31",
  "in_sample_end": "2025-06-30",
  "n_events": 360,
  "warmup_gate_as_of": "2025-05-31",
  "warmup_gate_passed_at_brt": "2026-04-28T20:34:21"
}
```

Cache audit JSONL line 3 (run window): `"as_of_date":"2025-05-31","phase":"smoke","note":"atr=state/T002/atr_20d_2025-05-31.json;pct=state/T002/percentiles_126d_2025-05-31.json;window=2025-05-31..2025-06-30"`. Dated path resolution honored per Dex E1.

### AC9.6 — Full as_of = 2024-08-22 (PASS)

`out_dir/events_metadata.json` (full phase, run root):

```json
{
  "phase": "full",
  "in_sample_start": "2024-08-22",
  "in_sample_end": "2025-06-30",
  "n_events": 3800,
  "warmup_gate_as_of": "2024-08-22",
  "warmup_gate_passed_at_brt": "2026-04-28T20:34:23"
}
```

Cache audit JSONL line 4: `"as_of_date":"2024-08-22","phase":"full","note":"atr=state/T002/atr_20d_2024-08-22.json;pct=state/T002/percentiles_126d_2024-08-22.json;window=2024-08-22..2025-06-30"`. Dated path resolution honored — full phase reads `_2024-08-22.json` series, not the legacy default-path singleton (Track A structural defect from Beckett N4 root-cause is empirically resolved).

### AC9.7 — Audit JSONL phase-tagged chain (AC3 — PASS)

`state/T002/cache_audit.jsonl` total 4 lines. Lines 1-2 are an earlier dry attempt at 2026-04-28T14:25 (pre-N+1 launch warmup-gate dry-test); lines 3-4 are the canonical N+1 run window:

```jsonl
{"as_of_date":"2025-05-31","computed_at_brt":"2026-04-28T20:34:19","expected_key":null,"found_key":null,"note":"atr=state/T002/atr_20d_2025-05-31.json;pct=state/T002/percentiles_126d_2025-05-31.json;window=2025-05-31..2025-06-30","phase":"smoke","status":"consumer_check"}
{"as_of_date":"2024-08-22","computed_at_brt":"2026-04-28T20:34:21","expected_key":null,"found_key":null,"note":"atr=state/T002/atr_20d_2024-08-22.json;pct=state/T002/percentiles_126d_2024-08-22.json;window=2024-08-22..2025-06-30","phase":"full","status":"consumer_check"}
```

**AC3 contract:** ✅ phase tag additive (existing schema fields preserved), ✅ smoke-first/full-second ordering matches AC10/AC11, ✅ both rows status=`consumer_check` (cache hit on both as_of, expected for cached state). Dara auditability requirement honored (2 phase-tagged entries per multi-phase run).

### AC9.8 — 5 artifacts at run root (PASS)

```
0xdc7a2e1b5e928e384fb6ffa89531a512c4b96fb2b7a43dc36179993d0da586f9  determinism_stamp.json    (709 B)
0x847f1a18b510e5c9a3fd7513624bb6cfe55d57ba881df5a4298da7f9dd775d9f  events_metadata.json      (331 B)
0xe9ad057a85963e0222c5e3ad1a17d50f9d760206d92a243b242591232b34e42a  full_report.json         (3673 B)
0x8b401008b9ed3912d64012b69d80922bcd687e7e6020ff1939723ee156520eec  full_report.md           (1025 B)
0xd512ab42f530e12106615f27804b6691aa8239c657907cecfb483b0d145e8d78  telemetry.csv            (1827 B)
```

5/5 present, all non-empty, well-formed JSON/CSV/MD. `determinism_stamp.spec_sha256 == 72261326…` matches on-disk spec post-PRR chain v0.2.3. `full_report.md` carries label `T002-v0.2.3`. **Note vs N5 sha256:** all 5 hashes differ from the N5 archived sha256s — expected, because (a) `computed_at_brt` field rotates on every run, (b) telemetry.csv contents are timestamped per-sample, (c) `run_id` UUID embeds in determinism stamp. Mathematical content (metrics, kill_decision verdict, K1/K2/K3 disaggregation) is **bit-equivalent** to N5 — confirms stub-engine determinism (seed=42 → same identity-zero PnL signature).

### AC9.9 — Smoke artifacts persisted (PASS — 4/4 + shared telemetry per §3)

```
0xbfe69802d656befad2e3515aa908c6cfb4f85a369f03bf9fd23ced8d4ce4fa18  smoke/determinism_stamp.json   (709 B)
0x91686174cc1f96ea6fc65a3d2f5932e8a28829ecc98f2426cdf95c4de2bf940e  smoke/events_metadata.json     (331 B)
0x0054abc299129dae9826bb7c8070de42659a2a0a1e157ed916ba6270f56de3c5  smoke/full_report.json        (3673 B)
0x34ceb894ffca938b1b15a77ebbed85726fe6b7c9fdfc71c5631aaead269e6bd1  smoke/full_report.md          (1025 B)
```

4/4 written by `persist_artifacts(smoke_dir, ...)` (`scripts/run_cpcv_dry_run.py:1067-1073`). Telemetry.csv (5th nominal artifact) shared at run root, contains 6 smoke-phase samples (rows 3-8 in CSV, all `note` prefixed `smoke:*` or `smoke_complete`). Architectural correctness per `persist_artifacts` docstring contract — NOT a deficiency.

`smoke/determinism_stamp.json` carries distinct `run_id` (`0da6271bddf645bd8958e729006311ff`) and `dataset_sha256` (`30b9a44a479abf1eae67f58d7a9a31af0abef598d3a9d1d5cb3fb8a1768da628`) vs full phase root (`9f5b545a29794ade820e8649366b3a7b` / `e3962eb8…`). This is **expected** — each `_run_phase` call gets its own determinism stamp scoped to that phase's events; the dataset sha differs because the smoke window contains a strict subset of in-sample bars (n_events=360) vs the full window (n_events=3800).

### AC9.10 — KillDecision verdict ∈ {GO, NO_GO} (PASS — F2-stub-OK)

**Smoke phase verdict:**

```json
{
  "verdict": "NO_GO",
  "reasons": [
    "K2: PBO=0.500000 >= 0.4 (kill criterion)",
    "K3: IC_in_sample=0.000000 non-positive — no edge"
  ],
  "k1_dsr_passed": true,
  "k2_pbo_passed": false,
  "k3_ic_decay_passed": false
}
```

**Full phase verdict:** identical kill_decision payload (bit-equivalent — stub identity-zero engine deterministic across windows under seed=42).

Both ∈ {GO, NO_GO} → **PASS strict-literal**.

**F2-stub-OK annotation (PRR-20260428-2 / ESC-010 Mira authority):** AC9.10 verifies **PIPELINE INTEGRITY**, NOT strategy edge. The current `make_backtest_fn` is a stub returning identity-zero PnL across all 225 path-trials per phase (45 paths × 5 trials). This produces the exact mathematical signature observed: IC=0 (no signal), Sharpe=0 (no return), PBO=0.5 (perfectly symmetric null-distribution flip rate), DSR=0.5 (Bonferroni-deflated centerpoint of null bootstrap).

Pipeline integrity demonstrated by:

- per-phase WarmUpGate fired against dated paths (2025-05-31 + 2024-08-22, both bound to distinct `_dated_*_path()` resolutions per Dex E1);
- per-phase events built (smoke n_events=360, full n_events=3800);
- two independent 5-trial × 45-path fan-outs executed (smoke 1620 ms, full 1914 ms);
- `compute_full_report` consumed metrics including squad-cumulative DSR + BBLZ PBO twice;
- two `KillDecision` verdicts emitted with K1/K2/K3 disaggregation + reasons array;
- 4 artifacts persisted under `out_dir/smoke/` + 5 artifacts persisted under `out_dir/` + 1 audit JSONL row per phase.

Strategy edge clearance: **deferred** to T002.1.bis (real `make_backtest_fn`).

---

## 5. Determinism + provenance audit

| Field | Smoke phase value | Full phase value |
|---|---|---|
| `seed` | 42 | 42 |
| `simulator_version` | `cpcv-dry-run-T002.0f-T3` | `cpcv-dry-run-T002.0f-T3` |
| `dataset_sha256` | `30b9a44a479abf1eae67f58d7a9a31af0abef598d3a9d1d5cb3fb8a1768da628` | `e3962eb80d83e1928f1a26fda5fb3f0c3d243456b63a0bc693eb067b62545c99` |
| `spec_sha256` | `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8` | `72261326d61d59224709ba1c072a0ec4798ed2f21b789a89480421245d8d26c8` |
| `engine_config_sha256` | `9a97e8f8734cbb8cd35362d7a336fe876a5b16257a170b9436d9e868ad946c81` | `9a97e8f8734cbb8cd35362d7a336fe876a5b16257a170b9436d9e868ad946c81` |
| `cpcv_config_sha256` | `d2ea61f29d7ccb4c86cb6447d957d3ea2563897599f3e142a55258123680acc3` | `d2ea61f29d7ccb4c86cb6447d957d3ea2563897599f3e142a55258123680acc3` |
| `python_version` | 3.14.3 | 3.14.3 |
| `numpy_version` | 2.4.2 | 2.4.2 |
| `pandas_version` | 2.3.3 | 2.3.3 |
| `run_id` | `0da6271bddf645bd8958e729006311ff` | `9f5b545a29794ade820e8649366b3a7b` |
| `timestamp_brt` | 2026-04-28T20:34:19 | 2026-04-28T20:34:21 |
| `n_trials_source` (full_report.json) | `docs/ml/research-log.md@69d97aeea2276370a797a5f32dabde6a6ad7261e` | same |

`rollover_calendar_sha256` and `cost_atlas_sha256` are `null` in both stamps — subsumed under `engine_config_sha256` per current wiring; not a regression vs N1-N5.

**Distinct `run_id` per phase:** expected behavior — per-phase determinism stamp is generated inside `_run_phase` for that phase's window; the `out_dir/{run_id}` ID and the per-phase determinism `run_id` fields are intentionally decoupled (run-id is the orchestrator-level identifier passed to all phases; the determinism stamp `run_id` is regenerated inside compute_full_report). This is **N+1's first observation of this decoupling under multi-phase regime** — useful provenance signal for Quinn/Sable future audits.

---

## 6. Comparison vs N1/N2/N3/N4/N5 chain

| Iteration | Date | Verdict | Wall | Peak RSS | Exit | Smoke phase | Full phase | Failure mode / outcome |
|---|---|---|---|---|---|---|---|---|
| N1 | 2026-04-26 | HOLD WARM_UP_IN_PROGRESS | n/a | n/a | n/a | n/a | n/a | Warmup not built — baseline state |
| N2 | 2026-04-27 (243bcad) | **FAIL** | n/a | n/a | n/a | n/a | n/a | `_split_yaml_blocks` parser inversion → ESC-007 |
| N3 | 2026-04-27 (ea491f6+3598445) | **FAIL** | n/a | n/a | n/a | n/a | n/a | Warmup as_of=2024-07-01 missing → ESC-008→ESC-009 |
| N4 | 2026-04-28 | **FAIL** strict-literal (`--smoke` engaged AC11 abort) / DIAGNOSTIC PASS no-`--smoke` | 4.596 s | 0.14 GiB | 0 (DIAG only) | aborted (singleton + default-path) | only ran (DIAG) | WarmUpGate singleton + default-path binding bug; ESC-010 dual-track |
| N5 | 2026-04-28 (09:19) | **PASS strict-literal** post-E2 (drop `--smoke`) | 4.381 s | 0.140 GiB | 0 | n/a (no `--smoke`) | only phase | E2 + F2 amendments unblocked literal-literal interpretation; T002.0h closed engineering layer |
| **N+1** | **2026-04-28 (20:34) — this report** | **PASS strict-literal** under E1 (per-phase regime) | **3.910 s inner / 7.489 s outer** | TBD telemetry CSV last RSS row = **145.26 MB ≈ 0.142 GiB** (peak across all 15 samples; max RSS column value) | **0** | **executes (n_events=360, NO_GO stub)** | **executes (n_events=3800, NO_GO stub)** | E1 per-phase WarmUpGate + dated path resolvers (Dex `6a78b88`) restore `--smoke` flag without AC11 abort path engagement |

**Chain resolution summary:**

- N1→N3 = warmup state production failures (resolved via T002.0g Dex implementation + ESC-008/009 PRR chain).
- N4 = harness binding defect surfaced by Beckett strict-literal execution → ESC-010 6/6 functional convergence.
- N5 = first PASS, but under E2 amendment (drop `--smoke`) — engineering layer closed for T002.0h.
- **N+1 = first PASS under E1 amendment (per-phase regime restored).** Both phases execute with their own dated-path-bound WarmUpGate, no fallback to default-path singleton, no AC11 abort path engagement. T002.0h.1 engineering layer closed.

**Pipeline determinism cross-check:**

- N+1 full phase metrics (PBO=0.5, DSR=0.5, IC=0, NO_GO, K1 PASS / K2 FAIL / K3 FAIL) are bit-equivalent to N4 DIAGNOSTIC + N5.
- N+1 smoke phase metrics are bit-equivalent to full phase metrics — consistent with stub identity-zero engine producing same null signature regardless of n_events.
- Different `run_id` UUIDs across runs reflect timestamp/UUID rotation, not non-determinism. Confirmed by spec_sha + engine_config_sha + cpcv_config_sha all unchanged across N4/N5/N+1.

---

## 7. Telemetry deep-dive (peak RSS + wall-time honesty)

`out_dir/telemetry.csv` 15 samples covering both phases:

| Sample | Time (BRT) | Phase | Note | RSS (MB) | VMS (MB) |
|---|---|---|---|---|---|
| 1 | 20:34:19 | -1 | run_start | 141.71 | 591.74 |
| 2 | 20:34:19 | -1 | init | 141.73 | 591.79 |
| 3 | 20:34:19 | -1 | smoke:events_start | 141.74 | 591.79 |
| 4 | 20:34:19 | -1 | smoke:events_built (n=360) | 142.38 | 591.79 |
| 5 | 20:34:19 | -1 | smoke:fanout_start (5 trials) | 142.54 | 591.79 |
| 6 | 20:34:21 | -1 | smoke:fanout_complete (1620 ms, 225 results) | 143.23 | 591.79 |
| 7 | 20:34:21 | -1 | smoke:report_complete | 143.41 | 591.89 |
| 8 | 20:34:21 | -1 | smoke_complete (verdict=NO_GO) | 143.42 | 591.89 |
| 9 | 20:34:21 | -1 | full:events_start | 143.42 | 591.89 |
| 10 | 20:34:21 | -1 | full:events_built (n=3800) | 144.48 | 593.07 |
| 11 | 20:34:21 | -1 | full:fanout_start (5 trials) | 144.79 | 593.46 |
| 12 | 20:34:23 | -1 | full:fanout_complete (1914 ms, 225 results) | 145.21 | 593.78 |
| 13 | 20:34:23 | -1 | full:report_complete | 145.26 | 593.91 |
| 14 | 20:34:23 | -1 | full_complete (verdict=NO_GO) | 145.26 | 593.91 |
| 15 | 20:34:23 | -1 | run_end (halt_observed=False) | 145.26 | 593.91 |

**Peak RSS observed (psutil-instrumented):** **145.26 MiB = 0.142 GiB.** vs 6 GiB soft halt cap → **42.3× headroom.** Honest reporting per Anti-Article-IV Guard #4.

**Wall-time inner orchestrator:** sample 1 → sample 15 ≈ 3.910 s. **Wall-time outer wrapper (orchestrator T5 brief):** 7.489 s — both PASS the 90 s sub-criterion budget by ≥ 12×.

**Smoke vs full memory delta:** smoke fan-out (sample 5 → 6) added ~0.7 MiB; full fan-out (sample 11 → 12) added ~0.4 MiB. Both negligible. Per-phase regime shows **no memory leak across phase boundary** — memory growth across smoke→full transition is ≤ 1.5 MiB (sample 8 → sample 11), well below any leak-suspect threshold.

**psutil sample resolution:** 0.5 s default poll interval; 15 samples over ~4 s inner execution = oversampled (some sub-second events captured in same timestamp bucket). This is an instrumentation artifact, not a wall-time discrepancy — fan-out durations are sourced from `events_metadata.fanout_duration_ms` which is computed in-process, not from sample-time deltas.

---

## 8. §9 HOLD #2 Gate 1 clearance criteria (engineering layer)

Per ESC-010 council ruling (Riven custodial veto authority) §9 HOLD #2 has 5 disarm gates. Gate 1 = T002.0h.1 N+1 empirical PASS (engineering exit gate restoration under E1 regime). Beckett assessment for Gate 1:

| Criterion | N+1 evidence | Status |
|---|---|---|
| AC9 strict-literal PASS | All 10 sub-criteria PASS (this report §1, §4) | **CLEARED** |
| Pipeline integrity end-to-end (both phases) | 2× (warmup gate → events_built → fan-out → KillDecision emitted) — bit-equivalent metrics across phases under stub engine | **CLEARED** |
| Per-phase isolation (E1 architectural intent) | smoke as_of=2025-05-31 + full as_of=2024-08-22 both bound to dated paths via `_dated_*_path()`; no singleton observed; no default-path fallback observed; audit JSONL phase-tagged 2 entries per AC3 | **CLEARED** |
| Reproducibility footprint | seed=42, spec_sha=`72261326…`, dataset_sha (smoke=`30b9a44a…`, full=`e3962eb8…`), engine_config_sha=`9a97e8f8…`, cpcv_config_sha=`d2ea61f2…`, simulator_version, python/numpy/pandas pinned | **CLEARED** |
| Hold-out untouched | `data/in_sample/year=2025/` ends `month=06`; `_holdout_lock` modules unmodified per `git status`; full window `2024-08-22..2025-06-30` strictly within in-sample manifest | **CLEARED** |
| Memory safety | 0.142 GiB peak vs 6 GiB cap (42.3× headroom); no halt event | **CLEARED** |
| Wall-time budget | 3.910 s inner / 7.489 s outer vs 90 s sub-criterion (or 5 min Mira anchor) — ≥ 12× headroom either reading | **CLEARED** |

**Gate 1 engineering layer: GO for §9 HOLD #2 Gate 1 disarm by Riven custodial dual-sign post-Pax T6 cosign.**

**Out of scope for Beckett (do not represent as cleared by N+1 alone):**

- Strategy edge validation (deferred T002.1.bis with real `make_backtest_fn` — Mira authority).
- Capital ramp authorization (gated by §9 HOLD #2 — 5 gates total; N+1 only addresses Gate 1).
- Phase F unblock (gated by all 5 §9 HOLD #2 gates — NOT cleared by N+1 alone).
- Spec-yaml `preregistration_revisions[]` PRR-20260428-1 disposition flip (OBSOLETE / superseded annotation) — Pax T6 authority post-N+1 PASS, NOT Beckett.

---

## 9. Anti-Article-IV self-audit

| Guard | Status |
|---|---|
| #1 No subsample | PASS — full window 2024-08-22..2025-06-30 (n_events=3800) + smoke window 2025-05-31..2025-06-30 (n_events=360) both faithful to spec |
| #2 No engine config modification | PASS — `engine_config_sha256=9a97e8f8…` matches pre-flight expectation; both phases share identical engine_config |
| #3 No improvisation | PASS — invocation literal per T002.0h.1 AC9 (with `--smoke` restored) honored by orchestrator; Beckett only formalises empirical evidence |
| #4 Honest peak RSS | PASS — 0.142 GiB reported as observed from telemetry sample 15, not guessed |
| #5 No source code mutation | PASS — `git status` shows only docs/state edits, no `packages/`/`scripts/` source changes during T5 |
| #6 No push | PASS — local-only; @devops Gage is push gate (Article II) |
| #7 No spec mutation | PASS — Pax T6 authority for spec yaml `preregistration_revisions[]` PRR-1 disposition; Beckett does not touch spec |
| #8 Reproducibility complete | PASS — seed + simulator_version + spec_sha + engine_config_sha + cpcv_config_sha + python/numpy/pandas + dataset_sha (per phase) + run_id all recorded |
| #9 Every claim traced to artifact | PASS — every numerical claim cites either `out_dir/{file}` line or telemetry sample number |

---

## 10. Limitations & confidence tags

- **[F2-stub-degenerate]** AC9.10 verdict NO_GO is structurally guaranteed by the stub `make_backtest_fn`. Real strategy-edge claim requires T002.1.bis completion. Council-approved limitation, not a backtest defect.
- **[engine_config_sha256 single-hash]** rollover_calendar and cost_atlas individual sha256 not separately stamped — subsumed under engine_config. Acceptable for N+1; future stamping refinement = housekeeping (separate from §9 HOLD #2 disarm).
- **[N5 root artifacts overwritten]** N+1 reused `run_id=cpcv-dryrun-auto-20260428-c5d5a708acda` → root artifacts mtimes are 20:34 (N+1), N5 (09:19) sha256s no longer recoverable from disk. N5 evidence preserved only in `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md`. Future runs SHOULD use distinct `run_id` for archival hygiene — recommend Quinn/Pax track this as housekeeping item (not blocking).
- **[Per-phase determinism stamp run_id decoupling]** smoke determinism `run_id=0da6271b…` differs from full determinism `run_id=9f5b545a…` and from orchestrator out_dir `cpcv-dryrun-auto-20260428-c5d5a708acda`. This is **first multi-phase observation** of decoupling — useful provenance signal but warrants documentation in simulator-changelog post-T6 (housekeeping).
- **[Audit JSONL pre-N+1 lines 1-2]** Lines 1-2 of `cache_audit.jsonl` are timestamped 2026-04-28T14:25 — predate N+1 launch (20:34). These were a dry warmup-gate consumer-check during orchestrator pre-flight setup. Lines 3-4 are the canonical N+1 run rows. Audit JSONL is **append-only** by spec; this is correct behavior, not a regression. Quinn/Sable future audits should scope to timestamp window when verifying AC3 contract.
- **[no `simulator_changelog`]** Beckett-side simulator changelog (`docs/backtest/simulator-changelog.md`) not updated in T5 — deferred to post-Pax T6 housekeeping; does not affect AC9.

---

## 11. Recommendation

**T002.0h.1 AC9 strict-literal: PASS (10/10 sub-criteria).** Engineering exit gate clear from Beckett's authority. Recommend handoff sequence:

1. **Pax (@po, T6)** — cosign N+1 PASS into story T002.0h.1 status (`InProgress → InReview → Done`). Pax to flip PRR-20260428-1 disposition in spec yaml `preregistration_revisions[]` to OBSOLETE/superseded per ESC-010 ruling. Append Change Log row.
2. **Riven (@risk-manager, custodial cosign)** — disarm §9 HOLD #2 **Gate 1** in `docs/qa/gates/T002.0g-riven-cosign.md` §9 (or successor doc); dual-sign with Mira if statistical review concurrent. Gates 2–5 remain pending (T002.1.bis + Mira statistical clearance + Riven dual-sign + capital ramp).
3. **Phase F remains BLOCKED** by remaining §9 HOLD #2 gates — Beckett does NOT represent N+1 as Phase F unblock.

Non-blocking parallel work:

- **T002.1.bis** — real `make_backtest_fn` (Dex+Mira, edge clearance authority) — strategy edge.
- **Spec yaml PRR disposition flip** — Pax T6 authority.

Engineering exit gate handoff: Beckett T5 → Pax T6 → Riven Gate 1 disarm → Mira/Dex T002.1.bis (parallel).

---

— Beckett, reencenando o passado 🎞️
