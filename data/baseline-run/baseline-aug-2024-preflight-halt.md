# G09a Baseline-Run Pre-flight HALT Report

**Task:** G09a baseline-run Aug-2024 WDO (retry after blockers cleared)
**Executor:** @devops (Gage)
**Captured at:** 2026-04-23 BRT
**Outcome:** **HALT — R4 gate fail, exit code 1 per ADR-3 / Riven Co-sign v2 R4 / E6**
**Authority:** `docs/architecture/memory-budget.md` Riven Co-sign v2 R4/E6, Article V (Quality First)
**Launch attempted:** NO — pre-flight gate refused.

---

## Step 1a — Host drift check (PASS)

Command:
```
.venv/Scripts/python -c "import psutil, json; mem=psutil.virtual_memory(); sw=psutil.swap_memory(); print(json.dumps({'total':mem.total,'available':mem.available,'percent':mem.percent,'pagefile_used':sw.used,'pagefile_total':sw.total,'pid_count':len(list(psutil.process_iter()))}))"
```

Output (first capture):
```json
{"total": 17143058432, "available": 10099269632, "percent": 41.1, "pagefile_used": 4579053568, "pagefile_total": 43567714304, "pid_count": 244}
```

| Metric | Value | Expected | Drift |
|---|---|---|---|
| `virtual_memory().total` | 17,143,058,432 bytes | 17,143,058,432 bytes | **0.0000%** |

Drift tolerance per `memory_budget.DRIFT_TOLERANCE = 0.01` (1%). **PASS.**

---

## Step 1b — Venv + import chain (PASS)

- `.venv/Scripts/python.exe` present: YES
- Python version: 3.14.3 (per #84 Dex bootstrap)
- Import verify `python -c "import psutil, psycopg2, pyarrow, pandas, pytest; print('ok')"` → printed `ok`. **PASS.**

---

## Step 1c — Canonical artifact sha256 verification (PASS)

| Artifact | Computed sha256 | Expected sha256 | Match |
|---|---|---|---|
| `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | **YES** |
| `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` | **YES** |

Canonical Aug-2024 parquet size: 116,625,226 bytes (~111 MiB).

Both artifacts **BYTE-IDENTICAL** to MWF-20260422-1 post-gate state. **PASS.**

`data/baseline-run/scratch/` not yet created (halt preempted creation).

---

## Step 1d — R4 launch-time availability check (FAIL — HALT TRIGGER)

### First capture (at pre-flight start)

```
available = 10,099,269,632 bytes (9.406 GiB)
required  = 15,428,752,588 bytes (14.369 GiB)   [= 1.5 × CAP_ABSOLUTE]
deficit   =  5,329,482,956 bytes (4.963 GiB)
```

### Second capture (a few minutes later, after other diagnostics)

```
available =  6,603,972,608 bytes (6.150 GiB)
required  = 15,428,752,588 bytes (14.369 GiB)
deficit   =  8,824,779,980 bytes (8.219 GiB)
```

**Host memory pressure is actively worsening during pre-flight** (available dropped ~3.25 GiB in a few minutes, likely driven by vmmem/WSL2/Chrome workloads).

### Top 10 non-retained (closable) consumers by RSS, t=second-capture

```
msedgewebview2.exe             pid= 13448 rss=   145.9 MiB
SearchApp.exe                  pid= 15192 rss=   111.7 MiB
msedgewebview2.exe             pid= 12092 rss=    93.8 MiB
msedgewebview2.exe             pid=  7152 rss=    74.0 MiB
nvcontainer.exe                pid= 15016 rss=    59.9 MiB
NVIDIA Share.exe               pid= 14464 rss=    59.2 MiB
WhatsApp.Root.exe              pid=  9644 rss=    50.6 MiB
SearchApp.exe                  pid= 16340 rss=    44.9 MiB
OneDrive.exe                   pid=  5492 rss=    42.3 MiB
AdobeCollabSync.exe            pid= 13220 rss=    34.2 MiB
```

**Aggregate top-20 closable RSS: ~0.953 GiB.** Even terminating every one of these leaves a ~7.27 GiB deficit against threshold. R4 whitelist (vmmem, MsMpEng, claude, explorer, svchost, system, registry, memory compression, etc.) holds the remaining ~9 GiB and is non-closable under Riven Finding 6.

**Verdict: R4 FAIL — unrecoverable at this host state.** Operator cannot quiesce the host into the 1.5× envelope without shutting down protected processes (violates R4 whitelist intent).

### ADR-3 disposition

Per `core/run_with_ceiling.py` L207-229 and `memory-budget.md` Table (Exit codes):
- R4 launch-time check fail → **exit 1 (wrapper setup error)**.

Under `--no-ceiling` the wrapper's in-code R4 gate is skipped (L209: `if math.isfinite(ceiling_bytes):`), so a naive launch would proceed. The task prompt explicitly overrides this as a devops-level safety guard:

> *"If `available` at launch-time is below the 1.5× threshold, HALT with exit code 1 per ADR-3 and report — do not launch a baseline-run that could starve OS."*

Honoring that guard is what this report records.

---

## Step 1e — Sentinel DB connectivity (PASS)

Container `sentinel-timescaledb` UP. Connection via `.env.vespera` credentials succeeded.

Query executed:
```sql
SELECT count(*) FROM trades WHERE ticker='WDO' AND timestamp >= '2024-08-01' AND timestamp < '2024-09-01';
```

Result: **21,058,318 rows** for Aug-2024 WDO.

Baseline expectation from task brief: 15-18M (based on 500K-850K/day × ~22 sessions). Observed 21M is above the top of that band — consistent with Aug-2024 being a heavier month (close to the 850K/day ceiling × ~22 sessions ≈ 18.7M + some margin; or using ~30 calendar days × ~700K average ≈ 21M). **Not a HALT — within order of magnitude.** Worth noting that a heavier-volume month may push the baseline peak memory higher than if we'd observed a median month.

**PASS.**

---

## Steps 2-6 — NOT EXECUTED

Pre-flight HALT at Step 1d. Launch was not attempted. No scratch parquet written. No telemetry captured. No canonical files touched.

- `data/baseline-run/scratch/` — not created
- `data/manifest.csv` — unchanged (sha256 verified pre-halt, re-verifiable post-halt by inspector)
- `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` — unchanged (sha256 verified pre-halt)
- No process killed, no subprocess launched, no git commit, no git push

---

## Why operator-level remediation is not straightforward

Under ADR-1 v2 Condition R4 v2, the standard remediation is: "Operator closes named processes; retry." The top-3 non-retained consumer message exists to tell the operator what to close.

On this host at 2026-04-23:
- The ~8.2 GiB deficit cannot be reclaimed from non-retained processes (top-20 aggregate is ~0.95 GiB).
- The rest lives inside the R4 whitelist (vmmem/WSL2 ~3.5 GiB PrivateMemorySize in prior capture, Docker Desktop backend, MsMpEng, claude, system services). The whitelist exists precisely because these are not operator-closable without breaking the host or the wrapper itself (claude is the shell launching the wrapper).

Decisions outside devops remit (and therefore points of escalation to orchestrator / Aria / Riven):

1. **Cold-host remediation:** reboot the machine to clear all non-essential accumulation, then launch baseline-run as the very first workload before opening claude/Chrome/Discord/Spotify/etc. Operator-led; requires Aria/Riven sign-off on procedure since it changes the host-preflight assumptions captured in #82.

2. **WSL2/Docker shutdown:** `wsl --shutdown` + stop Docker Desktop would reclaim the vmmem allocation (~3-4 GiB). Both are in the R4 whitelist, so this is a planned deviation from Finding 6, not an ad-hoc operator action. Requires Riven sign-off.

3. **Relax R4 multiplier for baseline-run only:** Baseline runs under `--no-ceiling` have a different failure mode than capped production runs (OS starvation vs. ceiling trip). Aria could author an ADR-1 v3 clause that permits baseline-run at e.g. 1.1× CAP_ABSOLUTE given that we emergency-kill at 95% of CAP regardless. This trades risk of OS paging during baseline for ability to measure at all on this host.

4. **Spec out ceiling derivation on a quiet host:** if the orchestrator can schedule this at an off-hours window when the user leaves the machine cold with only the strictly-retained set running, the deficit may shrink enough to pass R4 naturally.

None of 1-4 is within devops authority to decide. Gage stops at: "R4 fails, cannot proceed, handing back."

---

## Exit status

**exit_code = 1** (wrapper-equivalent, though no wrapper launch occurred)
**gate_failed:** R4 launch-time host-quiesce availability (Riven Co-sign v2 R4 / E6)
**blockers cleared this attempt:** venv, manifest write flag (both verified PASS)
**blocker discovered this attempt:** R4 — host-quiesce deficit ~8.2 GiB, unrecoverable at current host state

## Handoff

Returning control to orchestrator. Decision required on remediation path (1-4 above) before G09a can be retried. No canonical files mutated. No scratch files written. Hard bounds (manifest/in_sample preservation, no git, venv-only) honored.
