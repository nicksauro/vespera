# Operator Task — R14 Closure Checklist (Council 2026-05-03 R1 Amendment)

> **Audience:** Operator (you) running on the **local AI / local terminal** with DLL credentials in env vars. This document is self-contained — the receiving IA doesn't need to see prior chat.
> **Date issued (BRT):** 2026-05-03
> **Issued by:** @aiox-master post 6/6 UNANIMOUS APPROVE_WITH_CONDITIONS quorum on Council 2026-05-03 R1 Amendment
> **Blocking dependency:** Tasks below MUST complete before A2-Dara schema parity audit dispatch

---

## §0 Why this exists

Council 2026-05-03 R1 Amendment ratified the bulk-backfill window expansion `2023-01-01..2024-01-01` **conditionally** with 6/6 quorum. One of the binding conditions (R14, ratified unanimously) gates the post-amendment chain on **two outstanding spike-protocol gaps** that require DLL execution with live credentials. Cloud AI cannot execute these tasks (credential-isolation discipline).

**Tasks marked CRITICAL block the entire A2 → A3 → A4 → A5 → A6 → A7 → A8 chain.** Tasks marked OPERATIONAL are non-blocking but should land before bulk continuation.

---

## §1 Context summary (for the receiving IA)

### §1.1 Where we are

- Branch: `t003-a1-dll-probe-2023-12` (HEAD `b1802ac`, pushed origin, PR #22 OPEN, NOT yet merged into main)
- Production data: `D:\Algotrader\dll-backfill\` — 61 chunk dirs, 63 parquets, 3.9GB, manifest.csv at root (`# backfill-manifest v1 - NOT R10 custodial`, 15 cols, 50 production rows + 6 contamination dirs)
- Diagnostic data: `data/dll-probes/SPIKE-NELO/` — sample protocol Nelo, 6 sample dates 2023 (Jan/Mar/May/Jul/Sep/Nov)
- Probe script (canonical, post-Phase-1 fixes): `scripts/dll_probe_2023_12_wdofut.py` (commit `cbd6813`)
- Spike protocol script: `scripts/dll_spike_nelo_protocol.py`
- Backfill orchestrator: `scripts/dll_backfill_orchestrator.py` + `dll_backfill_chunk_runner.py` + `dll_backfill_launch_detached.py`

### §1.2 Why R14 was raised

Spike aggregation across S1a + S1b + S1-retry-0315 shows:

| Date | Outcome | Notes |
|---|---|---|
| 2023-01-16 | partial_coverage | OK |
| 2023-03-15 | partial_coverage (after 1 retry) | **qfd=73,657 (queue_full_drops)** — trades lost in callback queue overflow |
| 2023-05-15 | partial_coverage | OK |
| 2023-07-17 | partial_coverage | OK |
| **2023-09-15** | **error (exit 3) — never retried** | **GAP** |
| 2023-11-16 | partial_coverage | OK |

R14 (Council 2026-05-03 amendment, §2.2): *"Before A2-Dara schema parity audit dispatch, S1-retry-0915 (2023-09-15 retry) MUST execute and outcome documented. Additionally, 2023-03-15 qfd=73,657 root cause MUST be characterized (transient stochastic vs reproducible structural). If 0915 retry fails persistently OR 0315 qfd is reproducible-structural, R1' bulk window narrows OR data-quality flags propagate to A4-Mira regime stationarity ruling."*

### §1.3 Required env vars (operator-side, never in repo)

```powershell
$env:DLL_PATH            = "C:\Users\Pichau\Desktop\profitdll\DLLs\Win64\ProfitDLL.dll"
$env:DLL_USER            = "<your-Nelogica-CPF>"
$env:DLL_ACTIVATION_KEY  = "<your-Nelogica-key>"
$env:DLL_PASSWORD        = "<your-Nelogica-password-after-rotation>"
```

These vars exist only in your PowerShell session. Never commit, never echo, never paste in any chat (cloud or local). Close PowerShell → vars vanish.

---

## §2 CRITICAL Task 1 — S1-retry-0915 (2023-09-15)

**Goal:** establish whether 2023-09-15 retention is reproducibly broken or transient.

### §2.1 Pre-flight

```powershell
# verify env vars set (no values printed; just names if missing)
$missing = @()
foreach ($v in @('DLL_PATH','DLL_USER','DLL_ACTIVATION_KEY','DLL_PASSWORD')) {
    if (-not (Test-Path "Env:$v")) { $missing += $v }
}
if ($missing) { Write-Host "MISSING env vars: $($missing -join ', ')" -ForegroundColor Red; exit 1 } else { Write-Host "All 4 env vars set." -ForegroundColor Green }

# verify DLL exists
if (-not (Test-Path $env:DLL_PATH)) { Write-Host "DLL not found at $env:DLL_PATH" -ForegroundColor Red; exit 1 }

# git state
git status --short
git log --oneline -3
# expected HEAD: b1802ac (or descendant if you've added remediation commits)
```

### §2.2 Execution

The spike script has a defined retry mode. Pattern from `S1-retry-0315`:

```powershell
# from repo root
cd C:\Users\Pichau\Desktop\Algotrader

# inspect spike script API
Get-Content scripts\dll_spike_nelo_protocol.py | Select-Object -First 80

# execute S1-retry-0915 (mirror flags used for S1-retry-0315 — adapt date)
# expected wall-time: 100-180s for single-day spike
# expected exit code: 1 (partial_coverage) if retention OK, 3 (error) if reproducibly broken
python scripts\dll_spike_nelo_protocol.py --batch S1-retry-0915 --date 2023-09-15
```

If the script signature differs from this, read its `__main__` block first:

```powershell
Select-String -Path scripts\dll_spike_nelo_protocol.py -Pattern '"--batch"|"--date"|argparse|add_argument' -SimpleMatch:$false
```

### §2.3 Expected outputs

```
data/dll-probes/SPIKE-NELO/S1-2023-09-15-retry/
├── probe-telemetry-{run_id}.json    ← outcome here
├── probe-stdout-stderr-{run_id}.log
├── progress-timeline-{run_id}.csv
└── (parquet only if reached_100=True)
data/dll-probes/SPIKE-NELO/spike-summary-S1-retry-0915.json   ← aggregate summary
```

### §2.4 Outcome decision tree

Read `spike-summary-S1-retry-0915.json` after run completes:

| outcome field | trades_total | queue_full_drops | reached_100 | classification |
|---|---|---|---|---|
| `partial_coverage` | ≥500k | <1000 | true | **R14_0915_RESOLVED_CLEAN** — proceed |
| `partial_coverage` | ≥500k | ≥1000 | true | **R14_0915_RESOLVED_QUALIFIED** — qfd carry-forward, A4-Mira flag |
| `partial_coverage` | <500k | * | true | **R14_0915_PARTIAL_THIN** — investigate 09-15 macro events; A4 data-quality flag |
| `error` (exit 3) | * | * | * | **R14_0915_PERSISTENT_FAIL** — bulk window must narrow (exclude Sept 2023) OR escalate to mini-Council R1' revision |
| `full_month_works` | n/a (single day) | n/a | true | upgrade noted |

---

## §3 CRITICAL Task 2 — 2023-03-15 qfd=73,657 root cause

**Goal:** classify the 73,657 dropped-trades event as **transient stochastic** (run-specific load) OR **reproducible structural** (queue capacity insufficient for that day's tape volume).

### §3.1 Theory

`queue_full_drops` increments when the callback puts a trade onto the python.Queue and `put_nowait` raises `queue.Full`. The queue has a finite size (`maxsize` parameter in script init). Possible causes:

1. **Transient:** main thread blocked momentarily (GC pause, OS scheduler hiccup, pyarrow flush) → queue spiked → drops; **non-reproducible** on re-run.
2. **Structural:** 2023-03-15 had unusually high tape volume (Selic decision day BCB COPOM, US banking turmoil week — SVB/Signature/CS) → DLL emit rate exceeded queue.put + drain rate **regardless** of retry; **reproducible** on every run.

### §3.2 Procedure

```powershell
# RE-RUN spike on 2023-03-15 with FRESH cooldown (30s+)
# This is a second retry to test reproducibility. Use a new label to avoid clobbering prior data.
Start-Sleep -Seconds 30
python scripts\dll_spike_nelo_protocol.py --batch S1-retry2-0315 --date 2023-03-15
```

### §3.3 Outcome decision tree

Compare new `S1-retry2-0315/probe-telemetry-{run_id}.json` field `queue_full_drops` against prior `S1-retry-0315` qfd=73,657:

| New qfd | Δ vs 73,657 | Classification |
|---|---|---|
| < 5,000 | strong drop | **R14_0315_TRANSIENT** — queue depth was sized OK, prior run was unlucky → no action |
| 5,000-50,000 | partial drop | **R14_0315_TRANSIENT_QUEUE_TUNE** — recommend `maxsize` tuning before bulk |
| 50,000-100,000 | similar | **R14_0315_REPRODUCIBLE_BORDERLINE** — A4-Mira flags 2023-03-15 chunk; bulk continues but data-quality qualifier propagates |
| > 100,000 | worse | **R14_0315_REPRODUCIBLE_STRUCTURAL** — that day's tape exceeds DLL+queue throughput; mini-Council R1' revision required |

### §3.4 Quick microstructure cross-check (no DLL needed)

If you have access to historical news, confirm 2023-03-15 macro context (just for the report):

- BCB COPOM 2023-03-22 (one week later) — high anticipation week
- SVB collapse 2023-03-10, Signature 2023-03-12, Credit Suisse rescue news 2023-03-15..19
- VIX/Brazilian-VIX spike confirmed in any market data feed for that week

If macro context is "extreme stress week", `R14_0315_REPRODUCIBLE_STRUCTURAL` is more plausible than transient.

---

## §4 OPERATIONAL Task 3 — D:\ contamination cleanup

**Goal:** quarantine test dirs from production (Sable MA-08 + Dara D:\ verify).

### §4.1 Inventory

7 contamination dirs identified:

```
D:\Algotrader\dll-backfill\test-chunk3-isolated\
D:\Algotrader\dll-backfill\test-multi\
D:\Algotrader\dll-backfill\test-multi-v2\
D:\Algotrader\dll-backfill\test-orchestrator\
D:\Algotrader\dll-backfill\test-orchestrator-v2\
D:\Algotrader\dll-backfill\smoke-test\
D:\Algotrader\dll-backfill\verify-2023-12-29\
```

### §4.2 Action — quarantine, NOT delete

R10 custodial discipline: **never delete data, even test data, without explicit cosign**. Move to quarantine subdir instead.

```powershell
$src = "D:\Algotrader\dll-backfill"
$qdir = "D:\Algotrader\dll-backfill-quarantine-2026-05-03"
New-Item -ItemType Directory -Path $qdir -Force | Out-Null

$contaminated = @(
  'test-chunk3-isolated',
  'test-multi',
  'test-multi-v2',
  'test-orchestrator',
  'test-orchestrator-v2',
  'smoke-test',
  'verify-2023-12-29'
)

foreach ($d in $contaminated) {
    $from = Join-Path $src $d
    if (Test-Path $from) {
        Move-Item -Path $from -Destination (Join-Path $qdir $d) -Force
        Write-Host "Moved: $d → quarantine"
    } else {
        Write-Host "Not found (skip): $d"
    }
}

# verify only production chunks remain in src (should match WDOFUT_*pattern + manifest.csv)
Get-ChildItem $src | Select-Object -First 5 | Format-Table Name
Get-ChildItem $src | Where-Object { $_.PSIsContainer -and $_.Name -notlike 'WDOFUT_*' }
# expected: empty (only WDOFUT_* chunks + manifest.csv at root)
```

### §4.3 Manifest sanity check

```powershell
Get-Content "D:\Algotrader\dll-backfill\manifest.csv" | Select-Object -First 3
# line 1: comment header
# line 2: column header
# line 3+: production chunk rows (50 rows expected per Dara verify)

# row count
(Get-Content "D:\Algotrader\dll-backfill\manifest.csv" | Measure-Object -Line).Lines
# expected: ~52 (1 header comment + 1 col header + 50 data rows)
```

---

## §5 OPERATIONAL Task 4 — MA-02 push provenance verification

**Goal:** Sable meta-audit MA-02 (CRITICAL) requires confirmation of who pushed `b1802ac` to origin. Article II discipline: only @devops Gage may push.

You're the only person with shell access to your system. Tell the receiving IA which of these is true:

- [ ] **(a)** Push was executed by @devops Gage (AIOX:agents:devops invoked in this terminal session before push)
- [ ] **(b)** I (the user) pushed manually under my R10 absolute authority — this is supreme authority, supersedes Article II
- [ ] **(c)** Another agent (aiox-master, sm, dev, etc.) pushed without invoking @devops — this is an Article II VIOLATION; needs ESC

If (c), the receiving IA should help you draft an ESC ticket so the breach is logged, then audit `git reflog` + recent `claude` session transcripts to identify which agent did it.

---

## §6 What to bring back to the cloud session

After completing tasks above, you can return to the cloud session (or this same session if you stay) and report back **just the classification labels** + key numbers. No raw credentials, no full telemetry dumps — those live in `data/dll-probes/SPIKE-NELO/` and the cloud IA will read from disk.

### §6.1 Minimal report template

```
R14 closure report — operator 2026-05-03

Task 1 (S1-retry-0915):
  - Classification: R14_0915_RESOLVED_CLEAN | RESOLVED_QUALIFIED | PARTIAL_THIN | PERSISTENT_FAIL
  - trades_total: <N>
  - queue_full_drops: <N>
  - reached_100: true | false
  - exit_code: <N>
  - wall_clock_s: <N>

Task 2 (0315 qfd root cause):
  - Classification: R14_0315_TRANSIENT | TRANSIENT_QUEUE_TUNE | REPRODUCIBLE_BORDERLINE | REPRODUCIBLE_STRUCTURAL
  - New qfd: <N>
  - Δ vs 73,657: <relative>
  - Macro context: <stress week confirmed | normal week | unknown>

Task 3 (D:\ cleanup):
  - 7 dirs moved to D:\Algotrader\dll-backfill-quarantine-2026-05-03 | partial (specify which) | none
  - manifest.csv intact: yes | no

Task 4 (MA-02):
  - Push provenance: (a) Gage | (b) user direct R10 authority | (c) other agent (specify which)
```

### §6.2 Files the cloud IA will re-read

- `data/dll-probes/SPIKE-NELO/spike-summary-S1-retry-0915.json` (Task 1 outcome)
- `data/dll-probes/SPIKE-NELO/S1-2023-09-15-retry/probe-telemetry-*.json` (Task 1 detail)
- `data/dll-probes/SPIKE-NELO/spike-summary-S1-retry2-0315.json` (Task 2 outcome)
- `data/dll-probes/SPIKE-NELO/S1-2023-03-15-retry2/probe-telemetry-*.json` (Task 2 detail)

If those files exist, the cloud IA can independently classify against §2.4 + §3.3 trees — your minimal report is corroboration, not the only evidence.

---

## §7 What the cloud IA will do next (post your return)

Conditional on Task 1+2 outcomes:

| Combined classification | Next chain action |
|---|---|
| 0915_CLEAN ∧ 0315_TRANSIENT | A2-Dara dispatch unblocked. Remediation conditions §1-§6 (R15 token rename, quirks update, parse-time hard-reject, quarantine code gap, AC adjudication, registry) execute in parallel. ~3-5 squad sessions until A8-Beckett. |
| 0915_QUALIFIED ∨ 0315_BORDERLINE | A2-Dara dispatched with data-quality flag carried forward to A4-Mira; A4 may down-weight 03-15 + 09-15 chunks |
| 0915_PARTIAL_THIN | Investigate 09-15 macro events; A4-Mira axis flag — A2 still proceeds |
| 0915_PERSISTENT_FAIL | Bulk window narrows: exclude Sept 2023 from final manifest extension OR mini-Council R1' revision |
| 0315_REPRODUCIBLE_STRUCTURAL | Mini-Council R1' revision required before bulk re-runs that day; current 03-15 chunk gets quarantined |

---

## §8 Hard rules (operator discipline)

1. **Never paste credentials in any chat — cloud or local.** Env vars in PowerShell session only.
2. **Never modify `data/manifest.csv`** (R10 absolute custodial; user MWF cosign required separately).
3. **Never delete data** — quarantine only.
4. **Don't push, don't open PRs** without invoking @devops in the local IA (Article II).
5. **If anything fails unexpectedly** — capture `probe-stdout-stderr-{run_id}.log` + `progress-timeline-{run_id}.csv` and bring filenames back to cloud IA for forensics.

---

**Status of cloud-side R1 amendment ratification:** awaiting **user MWF cosign** on the 15-condition package (Council 2026-05-03 6/6 UNANIMOUS APPROVE_WITH_CONDITIONS). Tasks in this document close 2 of those 15 conditions (R14 + MA-02 + D:\ cleanup); the other 13 are squad-side remediations that can execute in parallel while you run these tasks.

— @aiox-master, 2026-05-03 BRT
