---
report_id: T002-beckett-t11-bis-smoke-report-N4-2026-04-28
story_id: T002.0h
agent: Beckett (@backtester)
task: T11.bis N4 — AC8 exit gate de T002.0h pós ESC-009 6/6 functional convergence
date_brt: 2026-04-28T08:48 BRT
verdict: HALT-ESCALATE-FOR-CLARIFICATION
verdict_summary: |
  AC8 amended invocation literal (per ESC-009 council ratification 2026-04-27 BRT,
  6/6 functional convergence) FAILS strict-literal exit-code check at smoke phase.

  Pre-flight: 8/8 PASS. Step A.1 (warmup smoke as_of=2025-05-31): PASS exit=0,
  wall=0.427s, cache hit registered ("orchestrator skipped (triple-key match)").

  Step A.2 (CPCV smoke + full per AC8 amended literal):
    - Command (literal):
      python scripts/run_cpcv_dry_run.py --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
        --dry-run --smoke --in-sample-start 2024-08-22 --in-sample-end 2025-06-30
    - Exit: **1** (FAIL per AC8.5 strict-literal)
    - Wall: 2.892s
    - Failure surface: smoke phase WarmUpGate refuses to clear; smoke phase computes
      smoke_in_sample_start = max(2024-08-22, 2025-06-30 - 30d) = **2025-05-31**
      and validates `_DEFAULT_ATR_PATH` / `_DEFAULT_PERCENTILES_PATH` against
      `expected_date=2025-05-31`; default-path JSONs hold `as_of_date=2024-08-22`
      (the most-recent warmup write per orchestrator default-path overwrite policy).
    - Verbatim error (from /tmp/n4/cpcv_n4.log):
      `ERROR: smoke phase failed; aborting full run per AC11: warmup not satisfied
      for 2025-05-31: status=WARM_UP_FAILED, reason=atr: stale as_of_date
      (file=2024-08-22, expected=2025-05-31); percentiles: stale as_of_date
      (file=2024-08-22, expected=2025-05-31)`

  Empirical refutation surfaced **DURING** N4 execution (not pre-flight): the
  ESC-009 council 6/6 ratified a CLI flag append, but the underlying harness
  uses a **single shared `WarmUpGate`** instance reading from `_DEFAULT_ATR_PATH`
  / `_DEFAULT_PERCENTILES_PATH` for **both** smoke phase (as_of=2025-05-31) and
  full phase (as_of=2024-08-22). The default-path JSONs cannot simultaneously
  satisfy both phases. The cache-key 2024-08-22 IS persisted (per pre-flight YA
  validation), but the harness lookup uses default-path **only**, not dated-by-as_of
  paths. No CLI surface allows per-phase warmup state path injection.

  Beckett ran a diagnostic (NO --smoke flag, full phase isolated, run_id
  T002-N4-DIAG-NOSMOKE) to confirm failure isolation:
    - Exit: 0
    - Wall: 4.596s
    - 5 artifacts persisted (full_report.{md,json}, determinism_stamp.json,
      events_metadata.json, telemetry.csv)
    - Peak RSS: 144.16 MiB ≈ 0.14 GiB (well under 6 GiB cap)
    - n_events: 3800 (over 10mo CPCV window)
    - fanout: 1479ms over 225 results (5 trials × 45 paths)
    - Peak RSS (telemetry.csv `rss_mb` column max): 144.16 MiB ≈ 0.14 GiB
    - **KillDecision verdict: NO_GO** — but **synthetic-stub artifact**, not real
      strategy kill: 45 path Sharpes all 0.0, IC=0.0, PBO=0.5 (default neutral),
      DSR=0.5 (default neutral), max_drawdown=0.0. Same degenerate signature as
      N3 smoke (synthetic 22d). Confirms make_backtest_fn still produces neutral
      stub over real events; full phase did NOT execute a real backtest.

  AC8 verdict matrix N4 (strict-literal):
    - 8.1 warmup exit==0: **PASS**
    - 8.2 warmup wall<5s: **PASS** (0.427s)
    - 8.3 2 dated JSONs: **PASS** (atr_20d_2024-08-22.json + percentiles_126d_2024-08-22.json
      persisted by pre-flight precompute)
    - 8.4 2 default-path JSONs: **PASS** (atr_20d.json + percentiles_126d.json present,
      pointing to as_of=2024-08-22)
    - 8.5 CPCV smoke+full exit==0: **FAIL** (exit=1; smoke phase warmup gate failure)
    - 8.6 CPCV total wall<5min: **N/A** (script aborted at 2.892s)
    - 8.7 Peak RSS<6 GiB: **N/A** (process aborted before fanout; psutil poller
      observed 0 samples — process exited before first 5s tick)
    - 8.8 5 artifacts: **N/A** (artifacts not persisted; smoke phase aborted before
      report compute)
    - 8.9 KillDecision verdict ∈ {GO, NO_GO}: **N/A** (verdict not computed in
      strict-literal path; in DIAGNOSTIC path verdict=NO_GO produced but is
      synthetic-stub, not real)

  Strict-literal: 4 PASS / 1 FAIL / 4 N/A. AC8 strict-literal FAIL.

  Beckett NÃO faz workaround. Anti-Article-IV Guards #1-#7 honrados:
    - NO subsample dataset
    - NO modify engine config
    - NO improvise threshold relaxation
    - Peak RSS reported HONESTLY (0.14 GiB on diagnostic; not sampled on amended)
    - Article IV strict — every clause traceable
    - NO modify source code (harness lookup binding NOT amended by Beckett)
    - NO push (Article II → Gage)

  HALT-ESCALATE for orchestrator decision. Three orthogonal mitigation paths
  surface from N4 empirical refutation:

    (E1) Harness amendment to read **dated-by-as_of-date** warmup state files
         (e.g., {atr,percentiles}_{as_of}.{json}) per phase, decoupling smoke
         (2025-05-31) from full (2024-08-22). Code change in run_cpcv_dry_run.py
         (line 848 WarmUpGate construction + line 878/923 _run_phase param threading
         + line 685/710 _load_warmup_state path resolution). Quinn QA + Pax cosign
         + Gage push gate. NEW STORY territory (T002.0h.1 successor).

    (E2) AC8 amended invocation literal **DROPS --smoke** flag — full-phase-only
         execution. Empirically validated by Beckett DIAGNOSTIC (T002-N4-DIAG-NOSMOKE):
         exit=0, wall=4.596s, 5 artifacts, KillDecision=NO_GO (synthetic-stub).
         Trade-off: smoke pre-condition (AC11 protective abort) lost; full phase
         alone proceeds. R15 breaking_field at acceptance_criteria.AC8.invocation_literal
         level (already touched by ESC-009; another append-only PRR-20260428-1).
         New mini-council required to ratify amendment.

    (E3) AC8 amended invocation literal AMENDS --in-sample-end → 2025-05-31
         (smoke window collapses to single-day or subset; smoke_in_sample_start
         = max(2024-08-22, 2025-05-31-30d) = 2025-05-01 → still mismatch unless
         further amended). NOT generally viable; included for completeness.

    Beckett orientation (consumer-side authority): **E2 is the lowest-friction
    closure path** — the smoke pre-condition was a defense-in-depth for AC11,
    and the synthetic-stub make_backtest_fn means full phase alone is the real
    AC8 evidence. E1 is correct LONG-TERM but introduces code change scope
    creep into T002.0h. Council 6/6 D2-narrow ratification is structurally
    preserved either way (in-sample window 2024-08-22..2025-06-30 unchanged).

  Synthetic-stub revelation (NEW finding, parallel to AC8 path mismatch):
  Even if E1/E2 unblocks AC8 strict-literal exit==0, the KillDecision verdict
  produced is **synthetic-stub artifact** (Sharpe=0 forall paths, IC=0, PBO=0.5,
  DSR=0.5). This is identical to N3 smoke degeneracy and indicates make_backtest_fn
  has not yet been wired to real per-event PnL — full phase produces 225 results
  but all are constant zeros. ESC-009 council Mira condition #1 ("statistical
  power preservation at as_of=2024-08-22, ~225 valid sample days, non-degenerate")
  applies to the spec-level POPULATION of trades; the ACTUAL PIPELINE OUTPUT
  remains stub. AC8.9 KillDecision verdict ∈ {GO, NO_GO} is technically PASS
  on the diagnostic (NO_GO produced), BUT semantically the verdict is
  pipeline-degenerate, not strategy-determined. ESCALATION for upstream T002.0h
  scope: confirm whether AC8 is satisfied by stub-NO_GO or whether real
  make_backtest_fn integration is part of T002.0h's exit gate.

authority: |
  Beckett — backtester & execution simulator authority. AC8 exit gate exercised
  post-ESC-009 6/6 functional convergence ratification 2026-04-27 BRT. Article IV
  (No Invention) absoluto. Anti-Article-IV Guards #1-#7 honrados. NO threshold
  relaxation, NO subsample, NO retry of warmup precompute, NO push, NO modify
  story files, NO modify code, NO modify spec, NO modify ESC-009 ledger.

  Beckett's N4 verdict is HALT-ESCALATE because the AC8 amended invocation
  literal as ratified by 6/6 council does not exit 0 — and the corrective
  action (whether E1, E2, or other) requires either code change or another
  R15 amendment, both of which are outside Beckett's consumer authority.
---

# Beckett N4 — T11.bis AC8 exit gate (D2-narrow as_of=2024-08-22) — HALT-ESCALATE

> "Backtest não-reproduzível é lixo. Toda execução registra: seed, versão do simulador,
> hash do dataset, hash da spec de features, config CPCV, timestamp BRT. Sem esses
> campos, o relatório é rejeitado." — Beckett core principle.

## 0. TL;DR

ESC-009 council 6/6 functional convergence ratified D2-narrow `as_of=2024-08-22` with
amended AC8 invocation `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30 --smoke`.
Beckett N4 executes that LITERAL command and observes **exit=1** at smoke phase. Root
cause: `WarmUpGate` is a single shared instance over `_DEFAULT_ATR_PATH` /
`_DEFAULT_PERCENTILES_PATH`; default-path JSONs hold `as_of=2024-08-22`; smoke phase
demands `as_of=2025-05-31` (smoke window = in_sample_end - 30d). Default-path JSONs
cannot simultaneously satisfy two distinct as_of values.

Beckett **DIAGNOSTIC** (full-only, no `--smoke`) PASSES exit=0 wall=4.596s with 5
artifacts and synthetic-stub KillDecision NO_GO. This isolates the failure to the
smoke gate path AND surfaces a **second** finding: full phase produces synthetic-stub
output (Sharpe=0 forall 45 paths, IC=0, PBO=0.5, DSR=0.5) — `make_backtest_fn`
remains a neutral stub over real events.

**Beckett verdict:** HALT-ESCALATE. Two orthogonal corrective actions surface (E1
harness amendment for per-phase warmup state, E2 drop --smoke from AC8 literal);
both require council ratification beyond Beckett consumer authority.

---

## 1. Pre-flight checks (8/8 PASS)

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Python 3.14.3 + psutil 7.2.2 | PASS | `python --version` + `import psutil` |
| 2 | BUILDER_VERSION = "T002.1-builders-v1.0.0" (cache-key suffix "1.0.0") | PASS | `packages/t002_eod_unwind/warmup/orchestrator.py:160` |
| 3 | manifest.csv sha256 prefix | PASS | `78c9adb35851bab4` (mtime 2026-04-21 13:57) |
| 4 | in-sample parquets year=2024 (01-12) + year=2025 (01-06) | PASS | 18 month subdirs present; window 2024-08-22..2025-06-30 ⊂ available |
| 5 | state files (cache_key_2024-08-22.json + dated JSONs + audit miss→write) | PASS | sha256=`3ca5ebd84e5b3373...`; chain `miss` 23:53 → `write` 23:58 |
| 6 | spec sha256 prefix (v0.2.0 + PRR-20260427-1 + pax_cosign `0305e456f072ff52...`) | PASS | `285ab7c475629417` (mtime 2026-04-27 20:09) |
| 7 | calendar_loader sha + cost-atlas sha | PASS | calendar=`1ea46b789ced69e5`; cost-atlas=`bbe1ddf7898e79a7` |
| 8 | hold-out lock 2025-07-01..2026-04-21 UNTOUCHED in spec | PASS | spec L94 `hold_out_virgin: "2025-07-01 to 2026-04-21"`; spec L153 |

---

## 2. Step A.1 — Warmup smoke (as_of=2025-05-31)

```
python scripts/run_warmup_state.py --as-of-dates 2025-05-31 --output-dir state/T002/
```

| Metric | Value |
|--------|-------|
| Exit code | 0 |
| Wall time | 0.427s |
| AC8.1 (exit=0) | PASS |
| AC8.2 (wall<5s) | PASS |

Cache audit chain entry registered:
```json
{"as_of_date":"2025-05-31","computed_at_brt":"2026-04-28T08:45:12",
 "expected_key":{"as_of_date":"2025-05-31","builder_version":"1.0.0",
                 "source_sha256":"7b7e4480425b8da4287f56eb3e8f95745accf62559579990b098a89193e141f7"},
 "found_key":{"as_of_date":"2025-05-31","builder_version":"1.0.0",
              "source_sha256":"7b7e4480425b8da4287f56eb3e8f95745accf62559579990b098a89193e141f7"},
 "note":"orchestrator skipped (triple-key match)","status":"hit"}
```

Note: cache hit. Default-path JSONs were **NOT overwritten** by this hit (orchestrator
skipped). Default-path JSONs continue to hold `as_of=2024-08-22` (from the most-recent
write at 2026-04-27 23:58:38 BRT during pre-flight precompute).

Trajectory of default-path `as_of_date` over T11.bis runs:
| Run | Default-path `atr_20d.json:as_of_date` | Reason |
|-----|----------------------------------------|--------|
| N1 baseline (2026-04-26) | 2025-05-31 | warmup register at-time-of-N1 |
| N2 (2026-04-27 ESC-007 fix) | 2025-05-31 | unchanged |
| N3 (2026-04-27 ea491f6+3598445) | 2025-05-31 | unchanged |
| Pre-N4 (2026-04-27 ESC-009 precompute) | **2024-08-22** | ESC-006 `write` triggered by miss |
| N4 (2026-04-28) | 2024-08-22 | warmup smoke for 2025-05-31 was cache HIT, no overwrite |

The default-path "most-recent-write-wins" semantics means N4 saw default-path pinned
to 2024-08-22 — which satisfies the **full** phase (in_sample_start=2024-08-22) but
fails the **smoke** phase (smoke_in_sample_start=2025-05-31) under shared
`WarmUpGate(_DEFAULT_ATR_PATH, _DEFAULT_PERCENTILES_PATH)`.

AC8.3 (2 dated JSONs persisted): PASS — `state/T002/atr_20d_2024-08-22.json` +
`state/T002/percentiles_126d_2024-08-22.json` exist. Also 2025-05-31 dated JSONs
exist from prior runs.

AC8.4 (2 default-path JSONs present): PASS — both exist, pointing to as_of=2024-08-22.

---

## 3. Step A.2 — CPCV smoke + full (AC8 amended invocation)

### 3.1 Literal command (per ESC-009 council 6/6 ratification, line 234 of council ledger)

```
python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --smoke \
  --in-sample-start 2024-08-22 \
  --in-sample-end 2025-06-30
```

### 3.2 Result

| Metric | Value |
|--------|-------|
| Exit code | **1** |
| Wall time (process from spawn to exit) | **2.892s** |
| psutil poller samples observed | **0** (process exited before first 5s tick) |
| Peak RSS observed (psutil) | **N/A** (no samples; psutil reports 0) |
| Telemetry CSV emitted | **PARTIAL** (telemetry.csv created in `data/baseline-run/cpcv-dryrun-auto-20260428-45cf2c5bf90a/` showing run_start + init + smoke_failed) |
| 5 artifacts (full_report.md/json, determinism_stamp.json, events_metadata.json, telemetry.csv) | **NO** (smoke aborted before report compute; only telemetry.csv created) |
| KillDecision verdict | **NOT COMPUTED** (smoke phase aborted before fanout) |

### 3.3 Verbatim error (from /tmp/n4/cpcv_n4.log)

```
ERROR: smoke phase failed; aborting full run per AC11: warmup not satisfied for
2025-05-31: status=WARM_UP_FAILED, reason=atr: stale as_of_date (file=2024-08-22,
expected=2025-05-31); percentiles: stale as_of_date (file=2024-08-22, expected=2025-05-31)
```

### 3.4 Root cause analysis

`scripts/run_cpcv_dry_run.py` lines:
- L848: `warmup_gate = WarmUpGate(args.warmup_atr, args.warmup_percentiles)` —
  single instance, paths fixed (defaults: `state/T002/atr_20d.json` and
  `state/T002/percentiles_126d.json`).
- L865: `smoke_start = max(in_sample_start, in_sample_end - timedelta(days=DEFAULT_SMOKE_DAYS))`
  → `max(2024-08-22, 2025-06-30 - 30d) = max(2024-08-22, 2025-05-31) = 2025-05-31`.
- `_run_phase` builds events via `build_events_dataframe(in_sample_start, ..., warmup_gate=warmup_gate)`
  and inside the events builder (or downstream) the gate's `check(2025-05-31)` is
  invoked → reads `_DEFAULT_ATR_PATH` → finds `as_of_date=2024-08-22` → returns
  WARM_UP_FAILED with the verbatim reason above.

The harness has **no surface** for swapping warmup state paths between phases. The
CLI flags `--warmup-atr` and `--warmup-percentiles` are single-valued and apply to
both smoke and full identically.

### 3.5 AC8 sub-criteria N4 strict-literal verdict

| # | Criterion | Threshold | N4 Result | Status |
|---|-----------|-----------|-----------|--------|
| 8.1 | warmup exit | 0 | 0 | PASS |
| 8.2 | warmup wall | <5s | 0.427s | PASS |
| 8.3 | 2 dated JSONs | sim | sim | PASS |
| 8.4 | 2 default-path JSONs | sim | sim | PASS |
| 8.5 | **CPCV smoke + full exit script-wide** | **0** | **1** | **FAIL** |
| 8.6 | CPCV total wall | <5min | 2.892s aborted | N/A (aborted) |
| 8.7 | Peak RSS | <6 GiB | not sampled | N/A (process exited too fast) |
| 8.8 | 5 artifacts | sim | NO (1/5: telemetry.csv only) | N/A (aborted) |
| 8.9 | KillDecision verdict ∈ {GO,NO_GO} | sim | not computed | N/A (aborted) |

Strict-literal: **4 PASS / 1 FAIL / 4 N/A** → AC8 strict-literal FAIL.

---

## 4. Diagnostic — full phase isolated (NO --smoke flag)

To confirm failure isolation to smoke gate path (NOT a flaw in cache 2024-08-22),
Beckett ran the same in-sample window WITHOUT `--smoke`:

```
python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --in-sample-start 2024-08-22 \
  --in-sample-end 2025-06-30 \
  --run-id T002-N4-DIAG-NOSMOKE
```

| Metric | Value |
|--------|-------|
| Exit code | **0** |
| Wall time | **4.596s** |
| 5 artifacts persisted | YES |
| Peak RSS (telemetry.csv `rss_mb` column max) | **144.16 MiB ≈ 0.14 GiB** (Windows working-set max=622403584 bytes ≈ 0.58 GiB; both well under 6 GiB) |
| n_events | 3800 |
| n_trials | 5 (T1..T5) |
| fanout duration | 1479ms over 225 results (5 × 45) |
| KillDecision verdict | **NO_GO** |

Artifact sha256:
| File | Size | sha256 (prefix) |
|------|------|-----------------|
| full_report.md | 1025 | `8ca17d2ba1fc6206...` |
| full_report.json | 3673 | `83bc3e35bcfa659e...` |
| determinism_stamp.json | 709 | `d2de36de3aec3f33...` |
| events_metadata.json | 331 | `682241835a1ec0e7...` |
| telemetry.csv | 1119 | `b22bb77060dbb4bb...` |

Determinism stamp:
- seed: 42
- simulator_version: `cpcv-dry-run-T002.0f-T3`
- spec_sha256: `285ab7c475629417...` (matches pre-flight expectation)
- spec_version: 0.2.0
- engine_config_sha256: `9a97e8f8734cbb8c...`
- python: 3.14.3, numpy 2.4.2, pandas 2.3.3
- run_id: `324c151fe42a49bbab6ec44d4fc2ff28` (deterministic from spec+window+seed)
- timestamp_brt: 2026-04-28T08:47:46

### 4.1 KillDecision details (DIAGNOSTIC, not AC8-binding)

```
Verdict: NO_GO
K1 (DSR>0): PASS  (DSR=0.500000)
K2 (PBO<0.4): FAIL (PBO=0.500000 >= 0.4)
K3 (IC decay): FAIL (IC_in_sample=0.000000 non-positive — no edge)
```

### 4.2 Synthetic-stub revelation (NEW N4 finding)

All 45 path Sharpes are **identically 0.0**. IC=0.0. Sortino=0.0. Profit Factor=0.0.
Hit Rate=0.0. Max Drawdown=0.0. PBO and DSR collapse to neutral defaults (0.5, 0.5).

This is the **same degenerate signature** as N3 smoke (synthetic 22d window). It
indicates `make_backtest_fn` is producing a neutral stub over real events — full
phase invokes 225 backtest function calls but all return constant-zero PnL.

**Implication:** ESC-009 council Mira condition #1 ("statistical power preservation
at as_of=2024-08-22, ~225 valid sample days, non-degenerate") applies to the spec
POPULATION of valid sample days, but the actual PIPELINE OUTPUT (PnL distribution
over 45 paths) remains pipeline-degenerate. The KillDecision verdict NO_GO is a
**stub artifact**, not a real strategy kill.

This was masked in N3 because N3 smoke window (22d) was already too small for
non-degenerate output — degeneracy was attributed to small-sample. N4's 10mo
window producing identical degeneracy proves the cause is **not sample size**;
it is `make_backtest_fn` stub architecture.

### 4.3 Diagnostic AC8 sub-criteria (FOR ORIENTATION ONLY — NOT binding)

If ESC-010 council ratifies E2 (drop --smoke from AC8 literal), the diagnostic
path becomes the AC8 evidence. Under that hypothesis:

| # | Criterion | Threshold | DIAG Result | Status |
|---|-----------|-----------|-------------|--------|
| 8.5' | CPCV full exit | 0 | 0 | PASS |
| 8.6' | CPCV total wall | <5min | 4.596s | PASS |
| 8.7' | Peak RSS | <6 GiB | 0.14 GiB (working-set 0.58 GiB) | PASS |
| 8.8' | 5 artifacts | sim | sim | PASS |
| 8.9' | KillDecision verdict ∈ {GO,NO_GO} | sim | NO_GO | PASS literal / SEMANTIC CONCERN (stub-degenerate) |

Diagnostic 5 PASS strict-literal; 1 semantic concern (8.9' stub-degenerate).
**Beckett does NOT have authority to substitute the diagnostic path for the AC8
amended literal command** — that requires council ratification of the path swap.

---

## 5. Comparison vs N1 / N2 / N3 (FAIL chain → ?)

| Run | Date BRT | Trigger / Hypothesis | Result | Root cause | Resolution path |
|-----|----------|----------------------|--------|------------|-----------------|
| N1 | 2026-04-26 | Baseline pre-ESC-007 | HOLD WARM_UP_IN_PROGRESS | parser inversion (later confirmed ESC-007) | ESC-007 fix |
| N2 | 2026-04-27 (243bcad) | Post-ESC-007 fix #1 | FAIL | `_split_yaml_blocks` toggle-fence bug | ESC-007 deeper diagnosis (`ea491f6`) |
| N3 | 2026-04-27 (ea491f6+3598445) | Post-ESC-007 fix #2 + Quinn integration test | FAIL exit=1 | full phase warmup as_of=2024-07-01 NOT precomputed | ESC-008 → ESC-009 (D1 path empirically refuted; D2-narrow as_of=2024-08-22 ratified 6/6) |
| **N4** | **2026-04-28** | **Post-ESC-009 6/6 ratification + pre-flight precompute as_of=2024-08-22** | **FAIL exit=1** | **smoke phase warmup gate path mismatch (default-path JSONs hold 2024-08-22; smoke needs 2025-05-31; harness has no per-phase swap)** | **ESC-010 candidate (this report): E1 harness amend OR E2 drop --smoke** |

Pattern: each N exposes the **next** previously-masked assumption in the AC8 chain.
N3 surfaced the spec-default in_sample_start=2024-07-01 mismatch; N4 surfaces the
**implicit smoke-pre-condition warmup-as_of derivation** (in_sample_end - 30d) which
is independent of `--in-sample-start` flag.

ESC-009 council convergence on D2-narrow `as_of=2024-08-22` correctly addressed
the **full phase** as_of binding, but did NOT model the **smoke phase** as_of
which is a function of `in_sample_end` (untouched by D2-narrow). All 6 voters
including Beckett missed this because the fault line is at line 865 (smoke_start
derivation), not at line 761 (warmup_gate_as_of binding for full phase).

This is a **legitimate empirical refutation** — same Article IV pattern as
PRR-20260421-1 → ESC-008 → ESC-009 chain. Authorization basis for ESC-010 is
the verbatim error message + harness line citation, NOT a "retry until green"
attempt.

---

## 6. Two corrective actions (E1 / E2)

### 6.1 E1 — Harness amendment for per-phase warmup state paths

**Code change required** in `scripts/run_cpcv_dry_run.py`:
- L120-121: introduce `_DATED_ATR_PATH(as_of)` / `_DATED_PERCENTILES_PATH(as_of)` resolvers.
- L848: instantiate `WarmUpGate` per phase (not shared) using the phase-specific as_of.
- L878 / L923: pass the dated path into `_run_phase` per phase.
- L685, L710: `_run_phase` accepts dated paths derived from `in_sample_start`.

**Pros:**
- Architecturally clean — decouples smoke as_of from full as_of canonically.
- Permanent solution; future smoke/full phase divergences naturally handled.
- ESC-006 cache contract (run-once-per-as_of) honored across both phases.

**Cons:**
- Code change — introduces Quinn QA + Pax cosign + Gage push pipeline.
- Article II (Gage push monopoly) requires user-gated push.
- Out of scope for T002.0h closure (T002.0h is "warmup state runtime",
  not "harness phase decoupling"). New story T002.0h.1 territory.

**Estimate:** ~2 days dev (Dex) + ~1 day QA (Quinn) + ~0.5 day cosign chain.

### 6.2 E2 — Drop --smoke from AC8 amended invocation literal

**No code change required.** Council 6/6 ratification of CLI flag append amended;
ESC-010 PRR-20260428-1 appends to spec preregistration_revisions[] documenting
the empirical refutation of the assumption that `--smoke --in-sample-end 2025-06-30`
would be smoke-gate-passable under the cache-2024-08-22 default-path state.

**Pros:**
- Lowest-friction closure; no source code change.
- Diagnostic empirical evidence ALREADY PRESENT (T002-N4-DIAG-NOSMOKE artifacts).
- Hold-out lock UNTOUCHED. Spec data_splits.in_sample UNTOUCHED. Bonferroni
  n_trials=5 PRESERVED.
- AC8 strict-literal exit=0 achievable on next Beckett run if AC8 invocation
  literal becomes:
  ```
  python scripts/run_cpcv_dry_run.py \
    --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
    --dry-run \
    --in-sample-start 2024-08-22 \
    --in-sample-end 2025-06-30
  ```

**Cons:**
- Smoke pre-condition (AC11 protective abort) lost from this AC8 evidence chain.
  AC11 itself remains in spec, but its execution surface is no longer the
  AC8 gating run.
- KillDecision NO_GO from full phase remains synthetic-stub artifact (not real
  strategy kill). 8.9 PASS literal but SEMANTIC CONCERN remains.
- Requires another mini-council ratification (ESC-010, structurally analogous
  to ESC-009 D2-narrow path).

**Estimate:** ~1 hour mini-council ratification + ~5min Beckett re-run +
~0.5 day cosign chain.

### 6.3 Beckett orientation (consumer authority)

**E2 is the lowest-friction closure path** for AC8 strict-literal exit=0.

**E1 is the correct LONG-TERM solution** for harness phase decoupling but introduces
code change scope creep into T002.0h. T002.0h's spec-level scope is "warmup state
runtime + cache contract", NOT "harness phase decoupling".

**Independent of E1/E2:** the synthetic-stub revelation (§4.2) is a SEPARATE
finding — `make_backtest_fn` stub does not produce real PnL distribution. AC8.9
KillDecision verdict ∈ {GO, NO_GO} is technically PASS on the diagnostic (NO_GO
emitted), but the verdict is pipeline-degenerate, not strategy-determined.
ESCALATION for orchestrator to confirm whether AC8 is satisfied by stub-NO_GO
or whether real `make_backtest_fn` integration is part of T002.0h's exit gate.

**Beckett does NOT have authority** to:
- Modify `scripts/run_cpcv_dry_run.py` (E1).
- Substitute the diagnostic path for the AC8 amended literal command.
- Declare AC8 PASS on semantic reading without Pax/Sable + Riven cosign authority.

---

## 7. Anti-Article-IV Guards 7/7 honored

| # | Guard | Status |
|---|-------|--------|
| 1 | NO subsample dataset | HONORED (full 10mo window unchanged in DIAGNOSTIC; AC8-literal aborted before any subsample question) |
| 2 | NO modify engine config | HONORED (engine_config_sha256=`9a97e8f8734cbb8c...` unchanged) |
| 3 | NO improvise threshold relaxation | HONORED (no threshold touched; 6 GiB cap, K1/K2/K3 thresholds unchanged) |
| 4 | Peak RSS reported HONESTLY | HONORED (DIAGNOSTIC 0.58 GiB from telemetry; AC8-literal psutil poller observed 0 samples — reported as N/A not fabricated) |
| 5 | Article IV strict — every clause traceable | HONORED (every clause cites: ESC-009 ledger, harness line, log path, sha256 of artifacts) |
| 6 | NO modify source code | HONORED (no code changed; harness binding preserved) |
| 7 | NO push (Article II → Gage) | HONORED (no commit, no push; Gage monopoly preserved) |

---

## 8. Reproducibility metadata (Beckett core principle)

| Field | Value |
|-------|-------|
| seed | 42 |
| simulator_version | cpcv-dry-run-T002.0f-T3 |
| dataset hash (manifest.csv sha256 prefix) | `78c9adb35851bab4` |
| spec hash (sha256 prefix) | `285ab7c475629417` |
| engine_config_sha256 (prefix) | `9a97e8f8734cbb8c` |
| calendar sha256 prefix | `1ea46b789ced69e5` |
| cost-atlas sha256 prefix | `bbe1ddf7898e79a7` |
| cpcv_config_sha256 prefix | `d2ea61f29d7ccb4c` |
| python | 3.14.3 |
| numpy | 2.4.2 |
| pandas | 2.3.3 |
| timestamp_brt (DIAG run) | 2026-04-28T08:47:46 |
| BRT timezone | -03:00 (per spec, no UTC conversion) |
| DIAG run_id | `324c151fe42a49bbab6ec44d4fc2ff28` |
| AC8 amended literal run output dir | `data/baseline-run/cpcv-dryrun-auto-20260428-45cf2c5bf90a/` (telemetry.csv only) |
| DIAG run output dir | `data/baseline-run/cpcv-dryrun-T002-N4-DIAG-NOSMOKE/` (5 artifacts) |

---

## 9. Recommendation to orchestrator

**Verdict:** HALT-ESCALATE.

**AC8 exit gate verdict:** FAIL (strict-literal). 4/9 PASS, 1/9 FAIL (8.5 script
exit=1), 4/9 N/A (smoke abort upstream of report compute).

**KillDecision (AC8-literal path):** NOT COMPUTED (smoke aborted before fanout).

**KillDecision (DIAGNOSTIC path):** NO_GO — but **synthetic-stub artifact**
(45 path Sharpes all 0.0; PBO=0.5 default; DSR=0.5 default). NOT a real strategy
kill.

**Wall-times:** warmup smoke 0.427s; AC8-literal 2.892s (aborted); DIAGNOSTIC 4.596s.

**Peak RSS:** AC8-literal psutil 0 samples (process exited too fast); DIAGNOSTIC
0.14 GiB (working-set 0.58 GiB; both well under 6 GiB).

**5 artifacts:** AC8-literal NO (only telemetry.csv); DIAGNOSTIC YES (all 5 with
sha256 prefixes recorded in §4).

**Next handoff:**
- **NO push (Article II → Gage; pre-conditions not met).**
- **NO §9 reconciliation** — AC8 strict-literal not PASS, so Riven+Mira §9
  reconciliation prerequisites not satisfied.
- **NO Sable audit** — Sable audits PASS chains; FAIL chain returns to orchestrator
  for ESC-010 council convocation.

**ESC-010 candidate council** (recommended):
- Voters: Aria + Mira + Beckett + Riven + Pax + Dara (same 6/6 as ESC-009,
  continuity preserved).
- Decision: E1 (harness amend, T002.0h.1 successor story) vs E2 (drop --smoke
  from AC8 literal, ESC-010 R15 amendment to story T002.0h AC8 line) vs E3
  (other path surfacing in council).
- Beckett orientation cast: **E2 lowest-friction**, but E1 architecturally
  cleaner long-term.
- **PARALLEL TRACK:** synthetic-stub revelation (§4.2) requires SEPARATE
  orchestrator clarification — is AC8 satisfied by stub-NO_GO, or is real
  `make_backtest_fn` integration part of T002.0h's exit gate?

---

## 10. Beckett signature

```
Validator: Beckett (@backtester) — backtester & execution simulator authority.
Run: T11.bis N4 — AC8 exit gate post-ESC-009 6/6 functional convergence ratification.
Date: 2026-04-28 BRT 08:48.
Verdict: HALT-ESCALATE-FOR-CLARIFICATION.
AC8 strict-literal: FAIL (exit=1; smoke phase warmup gate path mismatch).
DIAGNOSTIC isolation: confirms full-phase-only path is exit=0; stub-degenerate
                      KillDecision artifact reveals make_backtest_fn stub state.
Article IV: NO INVENTION — every clause traceable to (a) ESC-009 council ledger
            6/6 ratification, (b) scripts/run_cpcv_dry_run.py harness lines
            cited, (c) verbatim error log path /tmp/n4/cpcv_n4.log, (d) artifact
            sha256 prefixes in §4 + §8, (e) cache_audit.jsonl chain entries
            recorded in §2.
Anti-Article-IV Guards: 7/7 HONORED.
Reproducibility: seed 42 + simulator T002.0f-T3 + spec sha 285ab7c4... + dataset
                 sha 78c9adb3... + run_id 324c151f... + timestamp 2026-04-28T08:47:46 BRT.
Push: NO. Gage monopoly preserved. Article II honored.
Next gate: ESC-010 mini-council convocation (E1 vs E2 ratification) +
           parallel synthetic-stub clarification.
```

— Beckett, reencenando o passado 🎞️
