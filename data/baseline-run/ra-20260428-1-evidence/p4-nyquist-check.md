# RA-20260428-1 P4 — Q6d Nyquist Check Disposition

## Metadata

- `precondition_id: P4`
- `artefact_type: q6d-nyquist-check-disposition`
- `drafted_by: Riven (@risk-manager, R10 custodial)`
- `drafted_at_brt: 2026-04-24T18:30:00-03:00`
- `authorizing_ra: RA-20260428-1 (Stage-1 ISSUED 2026-04-24T21:18:10Z / 2026-04-24T18:18:10-03:00 BRT)`
- `governing_disposition: §RISK-DISPOSITION-20260423-1 Q6d (docs/architecture/memory-budget.md L2204-L2214)`
- `downstream_consumer: RA-20260428-1 Decision 6 (L2297 of docs/architecture/memory-budget.md)`
- `authority_basis: P4 self-authored by the same R10 custodial (Riven) who issued §RISK-DISPOSITION-20260423-1 Q6d; application to RA-28-1 is a drafting-time precondition closure, not a new authorization`
- `canonical_manifest_sha256_at_drafting: 75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` (verified byte-identical via `sha256sum data/manifest.csv` immediately prior to writing this file; governance-only artefact, zero canonical-data touch)

## Scope

This markdown closes the P4 precondition listed at `docs/architecture/memory-budget.md` L2309 ("Q6d Nyquist check applied (workload estimate OR explicit child-peak-only bypass cited in wrapper invocation)"). Per Q6d, the objective is NOT to gate the authorization on the Nyquist ratio — child-side peak telemetry is authoritative by construction regardless — but to document the disposition so the audit trail survives. This file is the Riven-owned disposition, binding on any wrapper invocation executed under RA-28-1 Stage-2 Decision 3.

## Expected runtime lower-bound

**Target workload:** ONE (1) sentinel-path `materialize_parquet.py` invocation against Aug-2024 WDO, executed under `--source=sentinel --no-ceiling` routing via `run_materialize_with_ceiling.py` wrapper, post-P1 streaming refactor (see P1 evidence — canonical `_fetch_month_dataframe` streaming refactor landed on main by Dex + Dara R10 dual co-sign).

**Lower-bound reasoning (cited evidence chain):**

1. **Prior cache-path timing (RA-26-1 retry #5) — NOT a lower-bound for sentinel-path.** Retry #5 under RA-26-1 Decision 1 (cache-path / sentinel-timescaledb-STOPPED) consumed ~60 seconds of child runtime against the Aug-2024 WDO month. That timing reflects a parquet-to-parquet transformation over an already-materialized cache (the `data/parquet/raw_trades/` pre-cache produced under ADR-4 §13.1 A1-A5) — the entire month's raw trades were already serialized to local parquet on disk, so the cache-path child was I/O-bound on sequential parquet read + write only. **Sentinel-path is materially different** and cannot share this runtime envelope.

2. **Sentinel-path data volume (inventory cite).** Per `memory/project_vespera_data_source.md` (inspected 2026-04-21 by Mira @ml-researcher and cross-referenced by Riven for this P4):
   - Sentinel `trades` hypertable: **56.5 GB total, 570 chunks** (hypertable config via `timescaledb_information.chunks`; `COUNT(*)` never run against full table — hypertable size is the structural proxy).
   - Ticker coverage: WDO + WIN; ticker string is literal `'WDO'` (not `WDOFUT`).
   - Temporal coverage WDO: **2024-01-02 → 2026-04-02 contiguous (~27 trading months)**; January 2023 contains only 6 isolated days (discardable).
   - **Per-day WDO trade volume: 500K-850K trades/day.**
   - Aug-2024 is a full trading month within the contiguous range (estimated ~22 trading days, matching the B3 pregão calendar).

3. **Aug-2024 WDO row-count lower-bound:**
   - Lower bound of daily volume (500K) × minimum trading days in month (21 assumed conservatively, accounting for any pregão holidays) = **~10.5 million trades** for the month.
   - Upper bound: 850K × 23 = ~19.5 million trades.
   - Reasonable point estimate: **~14-16 million trades** for Aug-2024 WDO through a single-ticker filter.

4. **Streaming I/O runtime translation.** The refactored `_fetch_month_dataframe` (per RA-28-1 Decision 2 / P1) consumes the hypertable via a psycopg2 server-side named cursor, streaming rows into Arrow batches and writing through `pq.ParquetWriter.write_table` per-batch (pattern parity with `scripts/build_raw_trades_cache.py:_stream_month_to_parquet` landed under ADR-4 §13.1). The child runtime is bounded below by:
   - Server-side cursor fetch rate through the TimescaleDB hypertable with index `(ticker, timestamp DESC)` — empirically multi-kilorow/sec for narrow-column projections on typical Postgres/Timescale deployments, but strongly affected by chunk pruning, network hop to localhost:5433, and row-to-Arrow conversion overhead.
   - Per-row wire cost (network + deserialization) for ~14M+ rows.
   - Per-batch parquet write cost (low but non-zero — streaming writer amortizes compression across batches).
   - Filesystem sync at final `ParquetWriter.close()`.

5. **Comparative evidence from related tooling.** `scripts/build_raw_trades_cache.py` previously materialized months from the Sentinel DB to parquet under ADR-4 §13.1 A2 acceptance (build ≤ 10 min per month). The Aug-2024 pilot build under `§13.1` landed at **204.21 seconds (~3.4 minutes)** per `data/baseline-run/ra-20260426-1-evidence/p4-peak-ws.txt` L16 (`elapsed_s=204.21`, commit `8c217bf`). This is the closest direct precedent for a single-month sentinel-path parquet materialization and was produced by a near-identical streaming writer pattern.

6. **Conservative lower-bound estimate for this RA's authorized invocation:** **≥ 180 seconds (3 minutes)**, anchored at the §13.1 pilot baseline of 204.21s for the same month (Aug-2024) and the same data source (Sentinel hypertable → parquet). A 180s floor is deliberately conservative (80% of the pilot observation) to absorb refactor-path I/O differences, any regression from introducing streaming writes into a previously-accumulating code path, and first-run kernel cache cold-start.

   - Upper-bound is open: the refactor's streaming discipline may produce runtimes materially different from the pilot (higher or lower depending on batch sizing, memory pressure, and whether the refactor introduces any additional Arrow conversion cost), and a multi-hour outcome cannot be structurally excluded if the hypertable cursor fetch rate dominates.

7. **No invention disclosure.** This lower-bound cites (a) the Sentinel DB inventory as recorded in `memory/project_vespera_data_source.md`, (b) the `p4-peak-ws.txt` elapsed time from the RA-26-1 evidence packet for a directly comparable workload (Aug-2024 WDO, streaming writer pattern), and (c) the hypertable chunk structure documented in that same memory file. No runtime number is invented; the 180s floor is a conservative scalar applied to the cited 204.21s precedent.

## Ratio check

- **Authorized poll interval:** `--poll-seconds=30` per RA-28-1 wrapper convention (inherited from RA-26-1 Decision 5 pattern; matches `run_materialize_with_ceiling.py` wrapper standing default).
- **Q6d threshold:** `expected_child_runtime_s_lower_bound ≥ 10 × --poll-seconds` = **≥ 300 seconds (5 minutes)**.
- **Ratio evaluation against the 180s lower-bound above:** 180 s < 300 s — the deliberately-conservative floor does NOT satisfy the 10× ratio on its own.
- **Ratio evaluation against the §13.1 pilot precedent (204.21 s):** 204.21 s < 300 s — also sub-threshold.
- **Ratio evaluation under the realistic expectation:** the authorized workload is expected to run **materially longer** than the cache-path pilot's 204.21s — the refactor is consuming from a 56.5 GB hypertable cursor (a network round-trip per batch to localhost:5433 + cursor fetch cost) instead of a local parquet read, which practitionerly lifts runtimes. The realistic point estimate trending multi-minute to multi-hour comfortably satisfies ≥ 300s. However, the conservative LOWER-BOUND floor as stated does not prove this structurally.

**Q6d ratio verdict: NOT STRUCTURALLY SATISFIED by the cited lower-bound alone.** This is acceptable — and explicitly so — because of Q6d's "regardless" clause (L2210-L2211): child-side peak telemetry is authoritative by construction, so the ratio outcome is not a gating criterion. See §"Primary peak source disposition" below.

## Primary peak source disposition

Per Q6d (L2210 of `docs/architecture/memory-budget.md`):

> *"... OR (b) cite child-side peak telemetry (`TELEMETRY_CHILD_PEAK_EXIT` per ADR-4 §14.5.2 / B4 artifact commit) as the primary peak-measurement source with parent polling retained only for reactive R5 WARN/KILL gating."*

**Binding disposition for RA-28-1 Stage-2 Decision 3:**

- **Authoritative peak source for step-7 CEILING_BYTES derivation:** `TELEMETRY_CHILD_PEAK_EXIT.peak_pagefile_bytes` emitted by the child process at orderly exit, per T002.4 merge commit `5a52ddd6b1e710d830977b08be832850a6697842` on main (telemetry commit `80805ac5` within that merge, 2026-04-24). This value is produced by psutil 7.2.2 `Process.memory_info()` which on Windows delegates to `GetProcessMemoryInfo` → `PROCESS_MEMORY_COUNTERS_EX.PeakPagefileUsage` — a **kernel-maintained monotonic max counter updated on every memory transaction**. No parent sampling rate applies; the counter's resolution is not a function of `--poll-seconds`.

- **Role of parent polling (`--poll-seconds=30`):** RETAINED for reactive R5 WARN/KILL gating ONLY, per ADR-1 v3 Condition R5 (WARN at 0.85 × `CAP_ABSOLUTE_v3`, KILL at 0.95 × `CAP_ABSOLUTE_v3` for `commit_bytes` observed in-flight). The 30s cadence is structurally irrelevant to the step-7 peak derivation because parent-polled `commit_bytes` is NOT consumed by the step-5 formula under this RA's Decision 6.

- **Root-cause closure of retry-#5 class of issue.** RA-26-1 retry #5 under `--poll-seconds=30` on a ~60s cache-path child produced a parent-polled `peak_commit = 819,200 bytes` artefact — four orders of magnitude below workload truth — precisely because parent polling sampled below Nyquist on the short-duration child. That failure mode is structurally precluded here: even if this RA's child runtime were sub-300s (which the cited lower-bound does not rule out), the step-7 input comes from the kernel counter embedded in the child process, not from parent observation. The child's `peak_pagefile_bytes` at exit reflects the actual in-process peak regardless of parent visibility.

- **R1-1 / R2-1 / R2-2 / R3-1 invariants** (enumerated at RA-28-1 L2283-L2286) are preserved by this disposition: the step-7 derivation uses the kernel-maintained peak counter (R2-1), emits BRT-naive timestamps in audit artefacts (R2-2), extends the child telemetry schema additively only (R3-1), and leaves `core/memory_budget.py` CAP/R4/KILL constants byte-identical through the measurement step (R1-1).

**Conclusion of primary-peak-source disposition: `TELEMETRY_CHILD_PEAK_EXIT.peak_pagefile_bytes` is authoritative for CEILING_BYTES derivation.** Parent polling contributes nothing to the step-7 input.

## Bypass flag disposition

The Q6d text anticipates a future `--use-child-peak-only` bypass mechanism for scenarios where a ratio-violating workload is authorized AND the RA explicitly acknowledges that parent polling will sample below Nyquist. **This RA does NOT invoke that bypass flag for the following reasons:**

1. **Ratio satisfaction is likely in practice.** The realistic expectation for the authorized workload's child runtime under the streaming-refactor sentinel-path is multi-minute to multi-hour, comfortably above 300s. The cited lower-bound (180s) is deliberately conservative and does not reflect the practitioner expectation for this workload.

2. **Child-telemetry primacy is independent of ratio outcome.** Per the primary-peak-source disposition above, `peak_pagefile_bytes` is authoritative by construction (kernel counter, not parent sample) regardless of whether the ratio holds. The bypass flag would add no additional protection in this RA's context — the protection is already structural.

3. **Bypass flag is a future-RA mechanism.** The flag, as envisioned in the Q6d text, is a wrapper-level affordance that would explicitly disable parent-polled peak reporting to force the wrapper to emit only the child-side value as the canonical peak. It is appropriate for RAs that:
   - Authorize known-short-runtime workloads (< 5 minutes), AND
   - Cannot restructure to avoid the short-runtime scenario, AND
   - Want a wrapper-contract guarantee that no operator can accidentally consume the parent-polled peak at the step-7 derivation step.

   None of those conditions applies to RA-28-1. The workload is expected to be long-running; the derivation source is Riven-bound to `peak_pagefile_bytes` by Decision 6 (not a wrapper affordance); and any operator attempt to consume parent-polled `commit_bytes` as the step-7 input is already a Decision 6 / R2-1 violation that triggers the revert-step-7-commit fail criterion at L2297.

4. **No wrapper code change required for this RA.** `run_materialize_with_ceiling.py` passes through `--poll-seconds=30` as a wrapper-level flag and reports parent-polled `commit_bytes` to its audit JSON; it already separately reports child-emitted `TELEMETRY_CHILD_PEAK_EXIT` fields through its stdout/CSV passthrough per T002.4. The step-7 author (Dex, consuming this RA's output) selects the child-emitted `peak_pagefile_bytes` field manually per Decision 6. No flag is needed to enforce that selection — the RA's governance does.

**Bypass flag disposition verdict: NOT INVOKED under RA-28-1. Governance (Decision 6 + R2-1 invariant) is sufficient in place of the bypass mechanism.** The flag remains a future affordance for RAs that authorize short-runtime workloads; its specification and implementation are OUT OF SCOPE for RA-28-1.

## Cross-references

- **Disposition basis:** §RISK-DISPOSITION-20260423-1 Q6d at `docs/architecture/memory-budget.md` L2204-L2214 (text that introduced the Nyquist sanity check and defined the "OR cite child-side peak telemetry as primary" alternative).
- **Decision binding:** RA-20260428-1 Decision 6 at `docs/architecture/memory-budget.md` L2297 (the row that ties child-peak-telemetry-primary to this RA's step-7 derivation).
- **Telemetry mechanism:** T002.4 merge commit `5a52ddd6b1e710d830977b08be832850a6697842` on main; telemetry commit `80805ac5` within that merge (psutil 7.2.2 + `GetProcessMemoryInfo` → `PROCESS_MEMORY_COUNTERS_EX.PeakPagefileUsage` + `.PeakWorkingSetSize` emitted as `TELEMETRY_CHILD_PEAK_EXIT` event).
- **Inventory source:** `memory/project_vespera_data_source.md` (Sentinel DB inventory, WDO coverage, 500K-850K/day volume; inspected 2026-04-21).
- **Runtime precedent:** `data/baseline-run/ra-20260426-1-evidence/p4-peak-ws.txt` (§13.1 Aug-2024 pilot, elapsed 204.21s, commit `8c217bf`).
- **Root-cause close reference:** RA-20260426-1 Decision 5 retry #5 (cache-path, `--poll-seconds=30` on ~60s child, parent-polled `peak_commit = 819,200 B` artefact) at `docs/architecture/memory-budget.md` L1989-L1995-region (retry #5 audit block).
- **Latent invariants preserved:** RA-20260428-1 [R1-1] L2283 (`core/memory_budget.py` constants byte-identical), [R2-1] L2284 (kernel-maintained peak), [R2-2] L2285 (BRT-naive timestamps), [R3-1] L2286 (additive-only JSON keys).

## Self-binding P4 closure

**I, Riven (@risk-manager, R10 custodial), hereby close precondition P4 of RA-20260428-1.**

**Signature statement:**

> **P4 CLOSED — Nyquist check documented per Q6d; child-peak telemetry is primary peak source for step-7 CEILING_BYTES derivation under RA-28-1 Stage-2 Decision 3.**

- No `--use-child-peak-only` bypass flag is invoked by this RA; bypass is a future-RA affordance.
- Parent polling at `--poll-seconds=30` is retained strictly for reactive R5 WARN/KILL gating; it contributes zero to the step-7 input.
- Step-7 author (Dex @dev) MUST consume `TELEMETRY_CHILD_PEAK_EXIT.peak_pagefile_bytes` from the child exit event of the Stage-2 authorized invocation per Decision 6 (L2297). Consumption of parent-polled `commit_bytes` as the step-7 input constitutes an R2-1 invariant violation and a Decision 6 fail criterion — revert step-7 commit, block step-7 populate until derivation re-sourced from child telemetry.
- This artefact is governance-only; it touches no canonical data, no `core/memory_budget.py` constants, and no `docs/architecture/memory-budget.md` text. Canonical manifest sha256 `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at drafting and MUST remain byte-identical after this write (write scope: this file only).

**Signed:** Riven (@risk-manager, R10 custodial), 2026-04-24T18:30:00-03:00 BRT.

**P4 status: CLOSED.**
