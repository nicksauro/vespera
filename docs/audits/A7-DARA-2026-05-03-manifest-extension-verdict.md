# A7 Dara Manifest Extension Verdict

**Operator:** Dara (@data-engineer)
**Date BRT:** 2026-05-03
**Verdict:** **`A7_PASS_PROCEED_TO_A8`**

---

## §1 Cosign authority ratification

User MWF cosign filed `docs/stories/T003-A6-COSIGN-REQUEST-2026-05-03.md` §9 — decision **(1) APPROVE** — status `A6_COSIGN_RATIFIED — A7_DARA_DISPATCH_AUTHORIZED`. Cosign signature inline §9 paragraph 2: *"...extend `data/manifest.csv` to include 2023-Q1..Q4 archival rows (50 chunks from `D:\Algotrader\dll-backfill\`, ~195M trades) per Council 2026-05-03 §6.5 routing, with phase=`archive` append-only addition, byte-equal SHA256 verified per R10..."*. Authority basis: User R10 absolute MWF cosign holder. Council 2026-05-03 §6.5 routing item 1 (archive-phase append-only) is the procedural anchor.

## §2 Schema alignment

Canonical Sentinel header (line 1 of `data/manifest.csv`, unchanged):

```
path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt
```

| Canonical column | Source from backfill v1.1 | Reconciliation |
|---|---|---|
| `path` | `parquet_relative_path` | Prefixed with `D:/` to denote off-repo custodial location; backslashes normalized to forward slashes for CSV cleanliness. |
| `rows` | `pq.read_table(...).num_rows` | Empirical recount via pyarrow (50/50 chunks match `trades_count` in backfill v1.1 row-by-row). |
| `sha256` | hash of raw on-disk parquet bytes | `hashlib.sha256` over parquet file (same semantics as `compute_dataset_hash`); backfill v1.1 had `sha256_parquet` column empty, so computed empirically. |
| `start_ts_brt` | `pc.min(timestamp)` from parquet | ISO-microsecond format matching Sentinel rows. |
| `end_ts_brt` | `pc.max(timestamp)` from parquet | Same. |
| `ticker` | `WDOFUT` (B3 mini-dollar full code) | Distinct from Sentinel `WDO` shorthand — namespace separation reinforces no-collision. |
| `phase` | `archive` | New enum value added per Council §6.5 mandate; coexists with `warmup` and `in_sample`. |
| `generated_at_brt` | `2026-05-03T00:00:00` | A7 dispatch date BRT. |

Backfill v1.1 columns NOT carried (out-of-canonical): `attempt`, `queue_full_drops`, `reached_100`, `downloaded_ts_brt`, `last_error_msg`, `dll_return_code`, `outcome`, `status`, `chunk_id`, `start_date`, `end_date`. The off-repo backfill manifest at `D:\Algotrader\dll-backfill\manifest.csv` retains these for orchestrator audit-trail (R14 off-repo); the canonical manifest carries only the 8-column Sentinel-compatible projection.

## §3 50 archival rows added

- **Count:** 50/50 (matches backfill v1.1 chunk inventory).
- **Phase:** `archive` (uniform across all 50).
- **Coverage:** 2023-01-02 → 2023-12-29 (51 calendar weeks; partial weeks bridge year boundaries with 2022 and 2024 — first parquet starts 2023-01-02; last parquet ends 2023-12-28T18:29:59.942000).
- **First chunk_id:** `WDOFUT_2023-01-02_2023-01-06` → `D:/Algotrader/dll-backfill/WDOFUT_2023-01-02_2023-01-06/wdofut-2023-12-bf3feaa06054.parquet` — sha256 `195f5cb5b990244d5490949ebf3d098fe2364d375a81a94cc860e5e50725b45a` (rows=4,792,151).
- **Last chunk_id:** `WDOFUT_2023-12-26_2023-12-29` → `D:/Algotrader/dll-backfill/WDOFUT_2023-12-26_2023-12-29/wdofut-2023-12-b231f1d7ba65.parquet` — sha256 `2cd917909376ebb9cc58188e652fd2dff894b6b48f40fa91718545c0d00e7faf` (rows=1,489,884).
- **Total archive trades:** 195,076,064 (matches cosign §1 statement "~195M trades / 195,076,064 rows verified post-projection" exactly).
- **Sentinel total trades preserved:** 295,146,482 (2024-onward, byte-equal pre/post).

## §4 Byte-equal preservation (R10 strict)

| Quantity | Value |
|---|---|
| Pre-mutation SHA256 | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` |
| Backup SHA256 (`data/manifest.csv.pre-A7-backup-2026-05-03.csv`) | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` |
| Pre-mutation size | 3,939 bytes (1 header + 18 Sentinel rows, LF-only line endings) |
| Post-mutation SHA256 | `3e27c955b3cd9cb6a6fbb67c77c07ce55d37cd2223dc41796d6af24da76d0ba4` |
| Post-mutation size | 16,639 bytes (1 header + 18 Sentinel rows + 50 archive rows) |
| Pre-segment SHA256 (post-mutation, byte-range 0..3939) | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` ✓ matches pre |
| Atomic write | `tempfile.mkstemp` in `data/` + `os.replace` (Windows fs-atomic, same volume) |

Append-only append; existing 3,939 bytes byte-identical pre/post. Independent post-mutation re-hash via separate Python invocation confirms `pre_segment_byte_equal: True`. R10 absolute custodial discipline preserved.

## §5 Custodial cross-checks

| Invariant | Status |
|---|---|
| Hold-out window 2025-07-01..2026-04-21 (T002 CONSUMED, locked permanently) | **0 rows added in window** ✓ untouched |
| H_next-1 forward-virgin window 2026-05-01..2026-10-31 (PRIMARY OOS anchor) | **0 rows added in window** ✓ INTOCADA |
| Pre-2024 archive rows (2023-Q1..Q4) | **50 rows; all `start_ts_brt` ∈ 2023** ✓ |
| Sentinel namespace (`path` starts with `data/in_sample/`) | **18 rows, byte-equal pre/post** ✓ no collision with archive `D:/...` paths |
| Ticker separation | **Sentinel `WDO` (18) vs Archive `WDOFUT` (50)** ✓ distinct |
| Phase enum | `warmup` (6), `in_sample` (12), `archive` (50) ✓ new enum coexists |
| D:\ source data mutated? | **No** — read-only access via `pq.read_table` and file-byte hashing. |

## §6 Carry-forward to A8-Beckett

A8-Beckett N1+ archive backtest run (Council §6.5 routing item 2) consumes the manifest extension as **SECONDARY-CORROBORATIVE only** per R12. Carry-forwards to action:

1. **F-A5-01 — exchange_fees ±0.6bp sensitivity-band** mandatory check before any `costed_out_edge` verdict; if strategy edge within ±0.6bp of break-even → escalate Path-D (B3 archive lookup) BEFORE final verdict.
2. **Mira flag #1 — `regime_calibration_required=True`** mandatory in feature_registry; quarter-conditional baselines mandatory for pre-2024 features.
3. **Mira flag #2 — `b3_auction_window_mask`** parametrized as first-1000-trades-OR-30s-whichever-larger exclusion; AUCTION_OPEN session-phase prior closed.
4. **Mira axis-(b) RLP soft-fail bounded** (NONE share Q1/2023 31.54% → Q1/2024 25.86%, Δ −5.7pp monotonic); pre-2024 NEVER promotes PRIMARY OOS.
5. **D-02 schema split** — agents stay int64 in archive parquets per F2 ACCEPTED divergence; A8 consumes via `dll_backfill_projection.project_parquet` with `PROJECTION_SEMVER=0.1.0` cache key.
6. **F-A5-02 49-chunk pooled re-test** future-work pre-condition for any future PRIMARY promotion of pre-2024 (currently locked SECONDARY-CORROBORATIVE).
7. **Guard #9 candidate** (Information Preservation Principle) status `candidate` per moratorium 2026-05-10; adjudication deferred.

A8 output is corroborative evidence only — does NOT alter T002 RETIRE FINAL status. H_next-1 strategy validation uses NEW preregistered window 2026-05-01..2026-10-31.

## §7 Source anchors

1. **User cosign:** `docs/stories/T003-A6-COSIGN-REQUEST-2026-05-03.md` §9 (decision APPROVE; signature inline; status `A6_COSIGN_RATIFIED — A7_DARA_DISPATCH_AUTHORIZED`).
2. **Council routing:** `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md` §6.5 item 1 (archive-phase append-only) + §6.2 R16 verbatim binding (R10 byte-equal + Gate-5 absolute).
3. **R10 custodial rule:** `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` R10 anchor (any `data/manifest.csv` mutation requires user MWF cosign — satisfied via §1 above).
4. **Backfill source manifest v1.1:** `D:\Algotrader\dll-backfill\manifest.csv` (50 rows; off-repo, R14, NOT R10 custodial).
5. **Projection module:** `scripts/dll_backfill_projection.py` v0.1.0 (`compute_dataset_hash` semantics for sha256 of raw parquet bytes; PROJECTION_SEMVER=0.1.0 cache key).
6. **Sentinel pre-mutation reference:** 19 lines × 8 columns × 3,939 bytes; SHA256 `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72`.
7. **Backup file:** `data/manifest.csv.pre-A7-backup-2026-05-03.csv` (byte-equal copy pre-mutation; SHA256 matches pre).
8. **Mutation tooling:** `scripts/_a7_dara_extend_manifest.py` (one-shot atomic append with tmp+os.replace; pre-segment byte-equal paranoia check; in-script SHA256 verification).

— Dara, manifest extension complete 2026-05-03
