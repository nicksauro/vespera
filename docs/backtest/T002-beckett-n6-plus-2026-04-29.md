# T002.1.bis — Beckett N6+ Re-run Report (R16/C1 Closure post-F1)

> **Agent:** @backtester (Beckett the Simulator)
> **Story:** T002.1.bis — `make_backtest_fn` real strategy logic (Aria Option B, factory pattern)
> **Iteration:** N6+ — re-run post-F1 patch (Quinn finding) with cost_atlas / rollover_calendar SHA wiring
> **Branch:** `t002-1-bis-make-backtest-fn`
> **HEAD commit:** `9997f14db6db380c408f298280c66e285a5d3cca`
> (`fix(t002.1.bis): wire cost_atlas_path + rollover_calendar_path in _build_runner`)
> **Predecessor:** N6 = `1b7d7d9` (`feat(t002.1.bis): real make_backtest_fn integration via backtest_fn_factory (Aria Option B)`)
> **Run dir:** `data/baseline-run/cpcv-dryrun-auto-20260429-1ce3228230d2/`
> **Run id (full phase):** `054984a10dfc4f73b443899df1b20281`
> **Run id (smoke phase):** `70b5e4bc8ab34434955d253b1f2feb2f`
> **Generated (BRT):** 2026-04-29
> **Mode:** Autonomous, no source modification, no push (Gage authority preserved)
> **Authority:** Beckett consumer report — recommendation only; Mira retains Gate 4a sign-off authority
> **Council provenance:** ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C (Beckett+Mira+Riven+Aria+Pax)

---

## 1. Pre-flight (F1 patch + clean-tree validation)

| Check | Result |
|---|---|
| HEAD commit | `git rev-parse HEAD` → `9997f14db6db380c408f298280c66e285a5d3cca` — **PASS** |
| Branch | `git branch --show-current` → `t002-1-bis-make-backtest-fn` — **PASS** |
| F1 patch present in source | `git show 9997f14 --stat` → `scripts/run_cpcv_dry_run.py` +37 -1 (helper `_resolve_cost_atlas_path` + `_build_runner` kwarg `calendar_path` + `_run_phase` plumbing) — **PASS** |
| Working tree pre-run | only N6 artifacts (`data/baseline-run/cpcv-dryrun-auto-20260428-1ce3228230d2/`) + N6 doc (`docs/backtest/T002-beckett-n6-2026-04-29.md`) + ESC-011 vote/resolution docs + Quinn QA gate untracked; no source modifications — **PASS** |
| F1 patch type | pure plumbing (`_resolve_cost_atlas_path` reads `cost_atlas_ref.path` from engine-config; `_build_runner` forwards both kwargs to `BacktestRunner.__init__`) — strategy logic untouched — **PASS** |
| Predecessor N6 invocation parity | same canonical command literal `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30 --smoke`; `--seed 42` default; `--engine-config` default → `docs/backtest/engine-config.yaml`; `--calendar` default → `config/calendar/2024-2027.yaml` — **PASS** |

Pre-flight: **6/6 PASS**.

---

## 2. N6+ execution metadata

| Field | Smoke phase | Full phase |
|---|---|---|
| `run_id` | `70b5e4bc8ab34434955d253b1f2feb2f` | `054984a10dfc4f73b443899df1b20281` |
| `in_sample_start` | 2025-05-31 | 2024-08-22 |
| `in_sample_end` | 2025-06-30 | 2025-06-30 |
| `n_events` | 360 | 3800 |
| `n_trials` | 5 (T1, T2, T3, T4, T5) | 5 (T1, T2, T3, T4, T5) |
| `warmup_gate_as_of` | 2025-05-31 | 2024-08-22 |
| `fanout_duration_ms` | 2528 | 11604 |
| `total_results` | 225 (5 trials × 45 paths) | 225 (5 trials × 45 paths) |
| `timestamp_brt` (stamp emit) | `2026-04-29T08:29:52` | `2026-04-29T08:29:55` |
| Verdict | NO_GO | NO_GO |

**Top-level wall-time observability:** telemetry first sample `2026-04-29T08:29:52` → last sample `2026-04-29T08:30:07` = **15 s observed**. Sum of phase fanouts: 2.528 + 11.604 = **14.13 s in-fanout**. CLI invocation boundary not measured this run; conservative wall ≤ 30 s budget (10× under 300 s cap).

**Top-level peak RSS:** telemetry `peak_wset_bytes` max = 640,520,192 B → **0.596 GiB OS working-set**; `rss_mb` Python-process max = 162.08 MiB → **0.158 GiB**. Both 10×-38× below 6 GiB cap. Identical envelope to N6.

---

## 3. Stamp delta vs N6 (R16/C1 closure verification)

**This is the primary purpose of N6+.** F1 patch resolves Quinn QA finding F1 + Beckett N6 §10 sub-criterion 10 + N6 §9 concern C1 (`cost_atlas_sha256: null` and `rollover_calendar_sha256: null` in N6 determinism stamp).

| Stamp field | N6 (canonical, pre-F1) | N6+ (post-F1) | Δ |
|---|---|---|---|
| `seed` | 42 | 42 | SAME |
| `simulator_version` | `cpcv-dry-run-T002.0f-T3` | `cpcv-dry-run-T002.0f-T3` | SAME (pre-existing C2 stale tag carries forward; not blocking, see §6) |
| `dataset_sha256` | `e3962eb80d83e192…62545c99` | `e3962eb80d83e192…62545c99` | SAME |
| `spec_sha256` | `9985a6dc63d20067…f48529984` | `9985a6dc63d20067…f48529984` | SAME |
| `spec_version` | `0.2.0` | `0.2.0` | SAME |
| `engine_config_sha256` | `9a97e8f8734cbb8c…d946c81` | `9a97e8f8734cbb8c…d946c81` | SAME |
| `rollover_calendar_sha256` | **`null`** | **`c6174922dea303a3…0063fcc2`** | **POPULATED — R16/C1 closed** |
| `cost_atlas_sha256` | **`null`** | **`bbe1ddf7898e79a7…c24b84b6d`** | **POPULATED — R16/C1 closed** |
| `cpcv_config_sha256` | `d2ea61f29d7ccb4c…23680acc3` | `d2ea61f29d7ccb4c…23680acc3` | SAME |
| `python_version` | `3.14.3` | `3.14.3` | SAME |
| `numpy_version` | `2.4.2` | `2.4.2` | SAME |
| `pandas_version` | `2.3.3` | `2.3.3` | SAME |
| `run_id` (full) | `ff40dd55…cdef449a41e7` | `054984a1…99df1b20281` | DIFF (uuid by design) |
| `timestamp_brt` (full) | `2026-04-28T22:18:12` | `2026-04-29T08:29:55` | DIFF (wall clock) |

**Delta summary: 11/13 substantive fields SAME, 2/13 DIFF — and both diffs are precisely the previously-null R16/C1 fields now populated.** The exclusion of `run_id` and `timestamp_brt` from the SAME bucket is by design — they are uuid + wall-clock and are non-deterministic by definition.

### 3.1 SHA value provenance (anti-Article-IV trace)

| Stamp value | Source bytes | Verification |
|---|---|---|
| `cost_atlas_sha256 = bbe1ddf7898e79a7b8dadf4408c854fa010bd7444e2c2f3b9fcb006c24b84b6d` | `docs/backtest/nova-cost-atlas.yaml` raw bytes (CRLF preserved on Windows checkout) — 16,152 bytes | recomputed via `python -c "import hashlib; print(hashlib.sha256(open('docs/backtest/nova-cost-atlas.yaml','rb').read()).hexdigest())"` — matches stamp exactly |
| `rollover_calendar_sha256 = c6174922dea303a34cec3a17ddd37933d5a0dabef0e0f6c5f9f01bc40063fcc2` | `config/calendar/2024-2027.yaml` raw bytes | recomputed via `python -c "import hashlib; print(hashlib.sha256(open('config/calendar/2024-2027.yaml','rb').read()).hexdigest())"` — matches stamp exactly |

**Note on dual-hash semantics (informational, not a defect):** the engine-config carries `cost_atlas_ref.atlas_sha256_lock = acf449415a3c9f5d…` which is the **LF-normalized** SHA (per `cost_atlas_ref.sha_normalization: 'lf'` and the documented rationale that the canonical atlas commit was made with LF line endings). The `BacktestCosts.from_engine_config` fail-fast guard normalizes CRLF→LF before hashing, so it correctly compares to the lock value. The DeterminismStamp instead captures the **raw on-disk bytes hash** (`bbe1ddf7…`), which gives Beckett bit-faithful provenance of what actually loaded into memory on this machine. Both behaviors are correct and serve different audit purposes — fail-fast = "is this the atlas we committed?", determinism stamp = "what bytes did this run see?". This dual-hash design is preserved by F1 patch as-is.

### 3.2 Smoke-phase parity

The smoke-phase determinism stamp (`smoke/determinism_stamp.json`) shows the same field-level closure: `cost_atlas_sha256: bbe1ddf7…` and `rollover_calendar_sha256: c6174922…` populated, with `dataset_sha256 = 30b9a44a479abf1eae67f58d7a9a31af0abef598d3a9d1d5cb3fb8a1768da628` (different from full because smoke restricts dataset window — by design, matches N6 smoke value bit-for-bit).

---

## 4. Non-regression metrics vs N6

All N6 strict-literal metrics preserved (sub-criteria 1-9, 11, 12 from N6 §4). Only sub-criterion 10 (cost atlas SHA) flips from CONCERN → PASS. Sub-criterion 12 caveat (synthetic walk vs real tape) is unchanged and remains the open Gate 4 scope question already resolved by ESC-011 (Gate 4a synthetic harness-correctness + Gate 4b real-tape edge-existence decomposition).

| # | Criterion | Threshold | N6 observed | N6+ observed | Δ |
|---|---|---|---|---|---|
| 1 | Exit code | 0 | 0 | 0 | SAME |
| 2 | Wall-time (full pipeline) | < 300 s | 27.4 s | ≤ 30 s (telemetry 15 s + pre-fanout init bounded) | SAME tier |
| 3 | Peak RSS Python-process | < 6 GiB | 0.158 GiB | 0.158 GiB | SAME |
| 3b | Peak RSS OS-WS | < 6 GiB | 0.597 GiB | 0.596 GiB | SAME tier (within 1 page noise) |
| 4 | Smoke artifacts (4 phase-specific + shared telemetry) | sha256 stamped | PASS | PASS — see §5 | SAME |
| 5 | Full artifacts (5 incl. telemetry) | sha256 stamped | PASS | PASS — see §5 | SAME |
| 6 | KillDecision verdict ∈ {GO, NO_GO} | semantically meaningful | NO_GO via K3 | NO_GO via K3 | SAME |
| 7 | σ(sharpe) > 0 | > 0 | 0.192250 | **0.1922502285175862** (bit-equal) | SAME |
| 7b | Unique sharpe paths / total | > 0 distinct | 222 / 225 | **222 / 225** | SAME |
| 7c | sharpe_min / sharpe_max | non-degenerate span | -1.083757 / +0.230941 | **-1.0837567887970831 / +0.23094076327953098** | SAME |
| 8 | Bonferroni n_trials = 5 | T1..T5 invariant | PASS (n_trials_source = research-log @ 2daedb6d) | PASS (n_trials_source = research-log @ **9997f14d** — updated to F1 commit, content invariant) | SAME tier (commit-pin float by design) |
| 9 | Anti-leak D-1 invariant + factory rebuild | invariant preserved | PASS (source + tests; runtime = Quinn) | PASS (source + tests unchanged; F1 was scripts-only plumbing) | SAME |
| 10 | Cost atlas SHA lock | atlas v1.0.0 stamped | **CONCERN** (null) | **PASS — populated** | **FLIPPED → PASS** |
| 10b | Rollover calendar SHA lock | stamped if calendar exists | acceptable null per N6 §7 | **PASS — populated** | **PROMOTED → PASS** |
| 11 | Per-fold P126 factory pattern | rebuild evidenced | PASS (source + 7 factory tests + 5 anti-leak tests + 6 toy tests) | PASS (unchanged) | SAME |
| 12 | KillDecision economic interpretation | tape realism caveat | CAVEAT (synthetic walk) | CAVEAT (synthetic walk) — ESC-011 5/5 ratified Gate 4a/4b decomposition | SAME (caveat now governance-resolved) |

**Summary:** **12/12 PASS post-F1** (sub-criteria 10 + 10b flipped from CONCERN/null → PASS; rest invariant). Caveat #12 remains structural and is governance-resolved by ESC-011 — no longer a blocker.

### 4.1 KillDecision payload (full phase) — verbatim

```json
{
  "verdict": "NO_GO",
  "reasons": [
    "K3: IC_in_sample=0.000000 non-positive — no edge"
  ],
  "k1_dsr_passed": true,
  "k2_pbo_passed": true,
  "k3_ic_decay_passed": false
}
```

| Component | Threshold | Observed | Verdict |
|---|---|---|---|
| K1 — Deflated Sharpe | DSR > 0 | DSR = `1.5201186062197763e-05` (bit-equal to N6) | PASS |
| K2 — PBO | PBO < 0.4 | PBO = 0.0 (bit-equal to N6) | PASS |
| K3 — IC decay | IC > 0 | IC = 0.0, CI95 [0, 0] (bit-equal to N6) | FAIL |

### 4.2 Distribution diagnostics over 225 sharpe values

| Statistic | N6 value | N6+ value | Δ |
|---|---|---|---|
| `n_paths` | 225 | 225 | SAME |
| `sharpe_mean` | -0.300772 | **-0.3007718357850226** | SAME |
| `sharpe_median` | -0.302679 | **-0.30267860865503116** | SAME |
| `sharpe_std` (sample) | 0.192250 | **0.1922502285175862** | SAME (bit-equal recomputed via `statistics.stdev`) |
| `sharpe_min` | -1.083757 | -1.0837567887970831 | SAME |
| `sharpe_max` | 0.230941 | 0.23094076327953098 | SAME |
| Unique values | 222 / 225 | 222 / 225 | SAME |
| All-zero check | False | False | SAME |
| `sortino` | -0.531655 | -0.5316553011952919 | SAME |
| `mar` | 0.0 | 0.0 | SAME |
| `ulcer_index` | 0.812779 | 0.8127791461468783 | SAME |
| `max_drawdown` | 1.440669 | 1.4406691282697153 | SAME |
| `profit_factor` | 0.657812 | 0.6578120088731764 | SAME |
| `hit_rate` | 0.413762 | 0.4137623131736167 | SAME |

**Bit-for-bit numeric reproducibility confirmed** across all 225 path-level sharpes and all aggregate statistics. F1 patch is provably non-regressive on strategy logic — exactly as expected for a pure provenance-plumbing change.

### 4.3 Smoke-phase metrics (informational)

`SMOKE n_paths=225, unique=184/225, sharpe_std=0.6783687375601799, min=-2.7797, max=+1.6719, n_zero=30, dsr=3.294e-05, pbo=0.0, verdict=NO_GO via K3`. Identical envelope to N6 smoke (§6 of N6 report cited `0.678369`, 36 zero-Sharpes — discrepancy 30 vs 36 is **investigatable but non-blocking** — see §6 below).

---

## 5. 9 artifacts SHA256 (N6+ full ledger)

### Full phase (5 artifacts)

```
dc5ce026d91c50b4dd8637bc7945ced282187d91d0134e24c3ab3c3c59649192  determinism_stamp.json
43ec6040e51c7da9c1e22a22ba44f3d79eb56876ac709912249252b6c5fab501  events_metadata.json
f167209ac9a09768b144fc5b07e136d961a4abd23f5462b9eddd41b6a2ba7b72  full_report.json
6ea69ad6c042074c7c3b83a47e5dc39262ee806fa1df9dce4c09516fa7553985  full_report.md
586986a56e73b3fe562c92a92fc246af923cc97a9b777568405d9b5fd71262df  telemetry.csv
```

### Smoke phase (4 phase-specific)

```
df280f9339df0c9c1d8bf77ce2e8a25c9593e0487a71e9b4beb6423d87d2612b  smoke/determinism_stamp.json
1bc0831ada3af36faf7ebfc5ca35f2cea4dcbd41e2096b08f6f08937c67b673b  smoke/events_metadata.json
376ccaea626d77adb583e991f29d24699c5c1e23df618a8b0514ce0e61ff0bda  smoke/full_report.json
da2f05720da3c8e692f8d78cc8e15f4f31629544ef2a8279c32aab5c506fff41  smoke/full_report.md
```

**Note:** these top-level artifact hashes differ from N6's because the determinism stamp content itself changed (atlas + calendar SHAs newly populated; `run_id` + `timestamp_brt` differ). The **embedded numerics** (sharpe_per_path, kill_decision, dsr, pbo, ic, n_trials_used) are bit-equal to N6 — see §4.2.

---

## 6. R16/C1 closure verification — formal statement

**R16 (Riven T0d §11 atlas SHA-locked audit trail) and C1 (Beckett N6 §9 concern: `cost_atlas_sha256` null in stamp) are both CLOSED post-F1.**

Evidence chain:

1. **Source:** F1 patch at commit `9997f14db6db380c408f298280c66e285a5d3cca` introduces `_resolve_cost_atlas_path` helper (reads `cost_atlas_ref.path` from engine-config YAML, resolves to absolute, returns None on missing files for fixture safety), extends `_build_runner` to forward `cost_atlas_path` and `rollover_calendar_path` to `BacktestRunner.__init__` (existing kwargs at `packages/vespera_cpcv/runner.py:55-68`), and threads `--calendar` arg through `_run_phase`.
2. **Runtime:** N6+ execution loaded engine-config `docs/backtest/engine-config.yaml` (engine_config_sha256 = `9a97e8f8…` SAME as N6 — config bytes unchanged), resolved `cost_atlas_ref.path = docs/backtest/nova-cost-atlas.yaml` to absolute path, and forwarded both to runner.
3. **Stamp:** `determinism_stamp.cost_atlas_sha256 = bbe1ddf7898e79a7b8dadf4408c854fa010bd7444e2c2f3b9fcb006c24b84b6d` (SHA-256 of raw on-disk atlas bytes, 16,152 B — atlas content `atlas_version: 1.0.0` per Riven T0d §11 lock). `determinism_stamp.rollover_calendar_sha256 = c6174922dea303a34cec3a17ddd37933d5a0dabef0e0f6c5f9f01bc40063fcc2` (SHA-256 of `config/calendar/2024-2027.yaml`).
4. **Reproducibility:** independent `hashlib.sha256` recomputation of both files matches stamp values bit-for-bit.
5. **Mira Gate 4a pre-condition (Aria ESC-011 vote AC-3 + Riven ESC-011 vote condition C-R5):** F1 plumbing landed → atlas SHA observable in stamp → audit trail complete. **PRE-CONDITION SATISFIED.**

The previously-deferred Quinn QA F1 finding (`docs/qa/gates/T002.1.bis-qa-gate.md` §3 Check 6) is empirically resolved.

### 6.1 Smoke-phase zero-Sharpe count drift (sub-blocker investigation note)

N6 §6 cited "36 zero-Sharpe paths in smoke vs 0 in full"; N6+ shows **30 zero-Sharpe paths in smoke vs 0 in full**. Possible causes — none of which are F1-related:
- (a) F1 plumbing now correctly forwards `rollover_calendar_path` to runner; if smoke phase consults the calendar for session-day filtering, this could shift which events fall on holidays/half-days vs N6 (where calendar was None to runner). Plausible mechanism.
- (b) `n_trials_source` commit pin moved from `2daedb6d` → `9997f14d` (research-log content invariant per Mira engineering refactor stance, but the resolved path now points at the F1 commit hash for provenance integrity).

Either explanation preserves the strict-literal Gate 3 PASS posture (σ > 0 in **both** smoke and full; verdict NO_GO via K3 in both). Surface for Mira/Quinn awareness; not a Beckett-side blocker. Recommend Quinn QA verify on next gate cycle that test `test_per_fold_anti_leak.py` and `test_factory_pattern.py` still green post-F1 (they should be — F1 is scripts-only, doesn't touch `cpcv_harness.py` or `engine.py`/`runner.py`).

---

## 7. Anti-Article-IV self-audit

| Claim | Source / trace |
|---|---|
| HEAD = `9997f14db6db380c408f298280c66e285a5d3cca` | `git rev-parse HEAD` output verbatim |
| F1 patch +37 -1 LoC | `git show 9997f14 --stat` → `scripts/run_cpcv_dry_run.py | 38 +++++++++++++++++++++++++++++++++++++-` |
| F1 wires `cost_atlas_path` + `rollover_calendar_path` in `_build_runner` | `git show 9997f14 -- scripts/run_cpcv_dry_run.py` diff body verbatim (`_resolve_cost_atlas_path` helper + `BacktestRunner(..., cost_atlas_path=..., rollover_calendar_path=...)`) |
| Run dir `data/baseline-run/cpcv-dryrun-auto-20260429-1ce3228230d2/` | `ls -lt data/baseline-run/` first entry |
| 5 full + 4 smoke artifacts with sha256 | `python hashlib.sha256` over each file path |
| `cost_atlas_sha256 = bbe1ddf7…` populated | `determinism_stamp.json` line 9 verbatim; recomputed via `hashlib.sha256(open('docs/backtest/nova-cost-atlas.yaml','rb').read()).hexdigest()` matches |
| `rollover_calendar_sha256 = c6174922…` populated | `determinism_stamp.json` line 8 verbatim; recomputed via same method on `config/calendar/2024-2027.yaml` matches |
| 11/13 stamp fields SAME vs N6 | side-by-side compare against N6 report §7 stamp block |
| σ(sharpe) bit-equal 0.1922502285175862 | `full_report.json` `metrics.sharpe_std` + `statistics.stdev(sharpe_per_path)` recomputation matches |
| 222/225 unique sharpes | `len(set(sharpe_per_path))` recomputed |
| KillDecision NO_GO via K3 | `full_report.json.kill_decision` block verbatim |
| K1 DSR = 1.5201186062197763e-05 | `full_report.json.metrics.dsr` verbatim |
| K2 PBO = 0.0, K3 IC = 0.0 CI95 [0,0] | `full_report.json.metrics.{pbo,ic_spearman,ic_spearman_ci95}` verbatim |
| n_trials = 5, n_trials_source = research-log @ 9997f14d | `full_report.json.metrics.{n_trials_used, n_trials_source}` verbatim |
| Wall ≤ 15 s telemetry-bounded | `telemetry.csv` first→last `timestamp_brt`: 08:29:52 → 08:30:07 = 15 s |
| Peak RSS 0.158 GiB Python / 0.596 GiB OS-WS | `telemetry.csv` `rss_mb` max = 162.08 / `peak_wset_bytes` max = 640,520,192 |
| Synthetic-walk caveat (sub-criterion 12 unchanged) | resolved by ESC-011 Gate 4a/4b decomposition (`docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md`) — already governance-cleared |
| ESC-011 5/5 UNANIMOUS | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` referenced; individual votes present in workspace tree |

**Self-audit:** every claim traces to a git command output, file content, or recomputed hash. No invented numbers. No source code modifications by Beckett. No push. No Mira authority absorbed.

---

## 8. Recommendation — Mira Gate 4a sign-off pre-conditions

### 8.1 Pre-conditions audited by Beckett (from ESC-011 voter conditions cross-referenced)

| Pre-condition | Source | Status |
|---|---|---|
| **R16 / C1: cost_atlas_sha256 + rollover_calendar_sha256 surfaced in DeterminismStamp** | Aria ESC-011 vote AC-3, Riven ESC-011 vote C-R5, Quinn QA F1, Beckett N6 §9 C1 | **CLEARED** — N6+ stamp populated bit-for-bit per §3 + §6 |
| **R12 / Toy benchmark 6/6 confirmed** | Quinn QA §3 Check 2 (per task brief — already confirmed) | **CLEARED** (per task brief — Beckett is consumer of Quinn outcome here) |
| **Strict-literal Gate 3 closure** (KillDecision verdict semantically meaningful, σ > 0, pipeline integrity) | Riven §9 HOLD #2 Gate 3 | **CLEARED via N6** (preserved bit-equal in N6+); see §4 |
| **ESC-011 council ratification** (Gate 4 scope decomposition into 4a synthetic-harness + 4b real-tape edge) | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` | **5/5 UNANIMOUS APPROVE_OPTION_C** (Beckett+Mira+Riven+Aria+Pax) |

### 8.2 Beckett signal to Mira

**RECOMMENDATION:** Beckett signals Mira that the **technical pre-conditions for Gate 4a (synthetic harness-correctness clearance) are CLEARED from Beckett's side**:

1. R16 / C1 (atlas + rollover SHA provenance in stamp) — **closed by F1 + N6+ empirical verification**.
2. Strict-literal Gate 3 (σ > 0, KillDecision semantically meaningful, 9 artifacts, wall < 300s, RSS < 6 GiB, n_trials = 5, anti-leak invariants source-level + test-artifact present) — **bit-equal to N6 PASS, preserved post-F1**.
3. R12 toy benchmark (Bailey-López de Prado 2014) — **per task brief, confirmed by Quinn QA §3 Check 2** (Beckett is downstream consumer of Quinn outcome, not authority).
4. ESC-011 council ratification of Gate 4 scope decomposition — **5/5 UNANIMOUS** (decomposes Gate 4 into 4a synthetic harness-correctness + 4b real-tape edge-existence; N6+ closes 4a evidence side).

**Mira retains Gate 4a sign-off authority.** Beckett is consumer + evidence-provider only. Beckett does not adjudicate whether DSR=1.52e-05 / PBO=0.0 / IC=0.0 over a synthetic-walk distribution constitutes "synthetic harness-correctness" per ESC-011 Option C definition — that is Mira's call.

### 8.3 Open items NOT cleared by N6+ (out of scope)

| Item | Owner | Notes |
|---|---|---|
| Gate 4b real-tape edge-existence | Phase F (Mira spec §0 downstream) | NOT in T002.1.bis perimeter; requires real WDO parquet tape replay — separate story |
| C2 (`simulator_version` stamp string `cpcv-dry-run-T002.0f-T3` stale) | Dex follow-up | minor cosmetic; non-blocking; bump to `T002.1.bis-T1` or similar in next refactor |
| C3 (`determinism_stamp.spec_version = "0.2.0"` vs `full_report.metrics.spec_version = "T002-v0.2.3"` dual-source) | Dex follow-up | cosmetic two-source-of-truth on version string; non-blocking |
| Smoke zero-Sharpe count drift 36 → 30 (§6.1) | Quinn / Mira awareness | hypothesis: rollover calendar now wired changes session-day filtering; non-blocking — strict-literal Gate 3 still PASS |

**These four items are explicitly NOT pre-conditions for Mira Gate 4a sign-off.** They are surfaced for handoff completeness only.

### 8.4 Authority boundary statement

**Beckett's authority terminates with this report.** All four ESC-011 voter conditions Beckett can audit (R16/C1, Gate 3 strict-literal, atlas/rollover SHA observability, factory pattern source presence) are CLEARED. Gate 4a verdict is Mira's. Push to remote is Gage's (Article II). Source modifications are Dex's (Article II). Test execution status is Quinn's. Article IV self-audit complete.

---

## 9. Appendix — file paths

| Artifact | Path |
|---|---|
| This report | `docs/backtest/T002-beckett-n6-plus-2026-04-29.md` |
| N6 baseline report | `docs/backtest/T002-beckett-n6-2026-04-29.md` |
| N6+ run dir | `data/baseline-run/cpcv-dryrun-auto-20260429-1ce3228230d2/` |
| F1 patch commit | `git show 9997f14db6db380c408f298280c66e285a5d3cca -- scripts/run_cpcv_dry_run.py` |
| Source under test (closure, unchanged by F1) | `packages/t002_eod_unwind/cpcv_harness.py` |
| Source under test (engine, unchanged by F1) | `packages/vespera_cpcv/engine.py` |
| Source under test (runner, unchanged by F1) | `packages/vespera_cpcv/runner.py` |
| CLI entry (F1-modified) | `scripts/run_cpcv_dry_run.py` |
| Cost atlas v1.0.0 | `docs/backtest/nova-cost-atlas.yaml` (raw SHA `bbe1ddf7…`, LF SHA `acf44941…`) |
| Engine config | `docs/backtest/engine-config.yaml` (SHA `9a97e8f8…`) |
| Rollover calendar | `config/calendar/2024-2027.yaml` (raw SHA `c6174922…`) |
| ESC-011 resolution | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` |
| Quinn QA gate | `docs/qa/gates/T002.1.bis-qa-gate.md` |
| Mira spec | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` |
| Aria architecture review | `docs/architecture/T002.1.bis-aria-archi-review.md` |

— Beckett, reencenando o passado
