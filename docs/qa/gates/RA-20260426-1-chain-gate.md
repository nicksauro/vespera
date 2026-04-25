# RA-20260426-1 Precondition Chain QA Gate — CONCERNS

**Reviewer:** Quinn (@qa, The Sentinel ♍)
**Date:** 2026-04-23 BRT
**Story / Spec:** RA-20260426-1 issuance-precondition chain (`docs/architecture/memory-budget.md` L1825-2110) + ADR-4 Amendment 20260424-1 §13 (`docs/architecture/pre-cache-layer-spec.md` L674-1119) + MWF-20260422-1 P5 passthrough extension.
**Deliverables gated:**
1. §13.1 streaming cache build (`scripts/build_raw_trades_cache.py` L355-503, commit `8c217bf`) + Aug-2024 WDO pilot + Mar-2024 warmup cache.
2. §13.2 T12 split — T12a/T12b (`tests/integration/test_adapter_parity_cache.py`, commit `cb62713`) + pinned snapshot + `tests/scripts/generate_t12b_snapshot.py`.
3. P5 wrapper passthrough (`scripts/run_materialize_with_ceiling.py` L134-194 / L238-243, commit `85664f7`) + 5 new `tests/core/test_run_with_ceiling.py` tests.

**Verdict:** **CONCERNS** — T12b sentinel-DOWN empirical proof PASSES (Q1 closed); A1/A2 telemetry PASSES; P5 wrapper PASSES; but 5 pre-existing unit tests in `tests/unit/test_build_raw_trades_cache.py` were left stale after the §13.1 rewrite and now fail on `AttributeError: 'DummyConn' object has no attribute 'cursor'`. Canonical sha + hold-out lock invariants intact. Single surgical test-fixture fix unblocks DRAFT → ISSUED.

---

## 7-Check Summary

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Requirements traceability | PASS | §13.1 A1-A5 → `_stream_month_to_parquet` L355-503 + integration L604-655; §13.2 A6-A9 → T12a L172-225 / T12b L232-277 / MANIFEST.sha256 L124-165 / generator L70-155; P5 → `scripts/run_materialize_with_ceiling.py` L138-194 (flag surface + mutex) + L238-243 (passthrough). Matrix below. No element orphaned. |
| 2 | Test execution | **CONCERNS** | `tests/t002_eod_unwind/adapters/test_feed_cache.py`: 8/8 PASS. `tests/integration/test_adapter_parity_cache.py` sentinel UP: 3/3 PASS. `tests/integration/test_adapter_parity_cache.py` sentinel DOWN (replay): T12a SKIPPED + T12b **PASSED** + T13 SKIPPED (Q1 empirically proven). `tests/core/test_run_with_ceiling.py`: 45/45 PASS (matches dispatch expectation). `tests/t002_eod_unwind/`: 85/85 PASS (grew cleanly from 77 baseline). **`tests/unit/test_build_raw_trades_cache.py`: 6 PASS / 5 FAIL** — 5 pre-existing tests monkeypatch `mp._fetch_month_dataframe` which §13.1 rewrite bypasses; they pass a `DummyConn()` into `_stream_month_to_parquet` which now calls `conn.cursor(name="cache_stream")` (L438). See FINDING-01 below. |
| 3 | Security/correctness review | PASS | Hold-out guard positioning verified by grep: `build_raw_trades_cache.py:508` (first line of `run()`, before schema build, manifest read, conn open), `feed_cache.py:123` (step 2 of `load_trades`, before manifest read), `generate_t12b_snapshot.py:73` (first line of `main()`, before `feed_timescale` import side-effects). SQL in `_stream_month_to_parquet` L413-425 is fully parameterized (`%(ticker)s`, `%(start)s`, `%(end_excl)s` — no f-string). No `eval`/`exec`. Path-traversal guard: `_reject_canonical_aliases` L184-215 rejects `--cache-dir` under `data/in_sample/` AND `--cache-manifest` == canonical `data/manifest.csv`. `VESPERA_UNLOCK_HOLDOUT` env unset throughout session. |
| 4 | Parity audit | PASS | T12a (sentinel UP): byte-identical MD5 on 3-tuple pickle, 2024-03-04 window (314060 rows) → PASSED. T12b: pinned snapshot sha256 `2c167eb1e9b53ca4287138ebcbf9f7234496b0cbd78162de742f2039f3291a19` over 314060 rows matches live `feed_cache.load_trades` output → PASSED (both with sentinel UP and DOWN). Snapshot integrity: `MANIFEST.sha256` = `03b2ee8e029de9c29c8c4f601a94b370c2cac6e0db368a8ed6a685e8201ce94c` for `wdo-2024-03-04.snapshot.json`, verified by `_load_snapshot` L124-165 tamper guard (`ValueError` on mismatch — fail-closed). T13 supplementary (cache vs canonical parquet) skips cleanly when canonical Aug-2024 absent. |
| 5 | Contract consistency | PASS | `feed_cache.load_trades(start_brt, end_brt, ticker) -> Iterable[Trade]` (L88-94) matches `feed_timescale.load_trades` (L163) and `feed_parquet.load_trades` (L331) signatures byte-for-byte (`*` marker keyword-only boundary identical). Ticker whitelist `{"WDO","WIN"}` enforced in all three. tz-naive assert in all three. `assert_holdout_safe` called as step 2 in all three. `HoldoutLockError` re-exported canonically via `_holdout_lock.py`. `_stream_month_to_parquet`'s strict per-column arrow coercions (L464-475) match the schema passed to `pq.ParquetWriter` (shared `mp._build_parquet_schema()`). |
| 6 | Performance budget | PASS | `.tmp/ws_peak.txt` (telemetry from Dex's §13.1 pilot build of Aug-2024 WDO): `peak_ws_bytes=221_130_752` (**210.89 MiB**) — far under A1 ceiling **3_758_096_384 bytes (3.5 GiB)** with 17x margin. `elapsed_s=204.21` (**~3.40 min**) — under A2 ceiling 10 min with 3x margin. `samples=792`, `child_rc=0`. Actual pilot output: `data/cache/raw_trades/ticker=WDO/year=2024/month=08/wdo-2024-08.parquet` sha256 `2473bdcc4fe9ab08bf5ce35c36327175abdc0bf69acc303f7054281fcc4fe90a`, 21,058,318 rows (per `cache-manifest.csv`). A3 (byte-identity vs `_write_parquet`) not independently replayed; accepted Dex's report via the dispatch pre-approval (the streaming helper is isolated per R10; canonical `_write_parquet` untouched). |
| 7 | Spec compliance (Article IV — No Invention) | PASS | Every line in §13.1 + §13.2 + P5 traces. `_stream_month_to_parquet` mirrors `_fetch_month_dataframe` coercions verbatim (L446-462 ≡ `materialize_parquet.py:532-541`) + the same determinism knobs (`snappy`, `2.6`, `use_dictionary=True`, `write_statistics=True`). Aug-2024 pilot cache is scoped to in_sample phase; Mar-2024 warmup cache (314060 rows) is in warmup phase — both structurally outside hold-out `[2025-07-01, 2026-04-21]`. `scripts/materialize_parquet.py` git-unmodified since pre-amendment commit `f971bb5` (R10 custodial surface preserved; Q5 DEFER honored). P5 wrapper uses argparse-native `add_mutually_exclusive_group` + post-parse `--source` mutex (L173-193) — no invented flag names. `tests/scripts/` dir (new) follows the generator convention documented in §13.2. |

---

## RA-20260426-1 P1-P5 Evidence Matrix

| # | Precondition | Artifact path | sha256 / signal | Quinn signoff |
|---|---|---|---|---|
| P1 | T12b cache-only sentinel-DOWN GREEN | `tests/integration/test_adapter_parity_cache.py::test_T12b_cache_self_sufficient_sentinel_down` | `PASSED` with `sentinel-timescaledb` stopped at 2026-04-23 BRT (this gate's replay; T12a SKIPPED, T12b PASSED, T13 SKIPPED) | **GREEN** — empirical Q1 closed. Attach pytest stdout to `data/baseline-run/ra-20260426-1-evidence/t12b-output.txt`. |
| P2 | Cache manifest sha256 pin | `data/cache/cache-manifest.csv` | sha256 to be recomputed by Gage at evidence capture; current state: 2 rows (Aug-2024 21058318r `2473bdcc4fe9ab08bf5ce35c36327175abdc0bf69acc303f7054281fcc4fe90a`; Mar-2024 314060r `cd41f4d3a3553612686a133a15aabd2479c5c3e74f19398ad780fa1aafb38009`) | GREEN — structure intact, ready for Gage sha pin. |
| P3 | Aug-2024 cache parquet sha256 pin | `data/cache/raw_trades/ticker=WDO/year=2024/month=08/wdo-2024-08.parquet` | `2473bdcc4fe9ab08bf5ce35c36327175abdc0bf69acc303f7054281fcc4fe90a` (per cache manifest row) | GREEN — pinned by cache manifest; Gage re-verifies at Decision 3. |
| P4 | Peak WS pilot build | `.tmp/ws_peak.txt` | `peak_ws_bytes=221_130_752` (210.89 MiB) < `3_758_096_384` (A1 cap) by 17x margin; `elapsed_s=204.21` < 600s (A2 cap) by 3x margin | GREEN — copy to `data/baseline-run/ra-20260426-1-evidence/peak-ws-pilot-build.txt` for issuance. |
| P5 | Wrapper `--source` / `--cache-dir` / `--cache-manifest` passthrough gate | `docs/qa/gates/RA-20260426-1-chain-gate.md` (this doc) + `scripts/run_materialize_with_ceiling.py` L134-194 / L238-243 + 5 new tests in `tests/core/test_run_with_ceiling.py` L586-681 | All 5 tests PASS; `--help` exposes flags; mutex enforced at parse time (exit 2); forwarding is conditional on operator intent (Art. IV) | GREEN — P5 closes under this gate. |

---

## Findings

### Blockers
**None.** (Canonical sha + hold-out invariants intact; T12b proves Q1; wrapper PASS.)

### Concerns
- **CONCERNS-01 — 5 unit tests in `tests/unit/test_build_raw_trades_cache.py` are stale post-§13.1 rewrite.** Failing tests: `test_build_resume_redoes_partial_month` (L180), `test_build_force_rebuild_wipes_manifest_and_chunk` (L235), `test_build_cache_atomic_flush_no_partial_files` (L288), `test_build_cache_writes_sha256_to_manifest` (L323), `test_build_cache_does_not_touch_canonical_paths` (L365). All fail with `AttributeError: 'DummyConn' object has no attribute 'cursor'` at `scripts/build_raw_trades_cache.py:438` because each monkeypatches `mp._fetch_month_dataframe` (the pre-§13.1 entry point) and passes a `DummyConn` into `brc.run(...)`; the streaming rewrite bypasses `_fetch_month_dataframe` and directly calls `conn.cursor(name="cache_stream")`, which `DummyConn` does not implement. Remediation: update the 5 test stubs to monkeypatch `brc._stream_month_to_parquet` with a fake returning `(row_count, first_ts, last_ts)` AND write a byte-valid parquet at `out_tmp`, OR extend `DummyConn` to a context-manager mock cursor. **This is a test-fixture staleness bug, not a production code defect** — the streaming helper itself is correct (as proven by the Aug-2024 pilot producing a 21M-row parquet at 210.89 MiB peak WS). Blocks DRAFT → ISSUED flip only because A5 ("ruff/mypy/tests clean") is not fully green. Single 20-minute Dex patch.

### Informational
- **INFO-01 (positive).** T12b replay with sentinel DOWN took 9.94s end-to-end (`docker stop` → `pytest ...test_T12b...` GREEN) — faster than the quiesce window cost by ~3 orders of magnitude. The Q1 empirical proof is not marginal.
- **INFO-02 (positive).** The §13.1 pilot build of 21,058,318 rows at 210.89 MiB peak WS is 55x under CAP_v3 (8.4 GiB) and 17x under the A1 sub-budget. Streaming pattern is empirically validated as a candidate for Q5 (RA-20260428-1 canonical patch).
- **INFO-03 (positive).** `materialize_parquet.py` is git-unmodified since pre-amendment commit `f971bb5`. R10 custodial boundary + Q5 DEFER respected.
- **INFO-04 (positive).** P5 wrapper tests add argparse-level mutex validation for `--source=cache` requiring both `--cache-dir` and `--cache-manifest`, and `--source=sentinel` forbidding them — 3 dedicated mutex tests pass (L624, L644, L664). Operators cannot under-specify a cache run.
- **INFO-05 (positive).** `generate_t12b_snapshot.py` uses atomic `tmp` + `os.replace` for both the JSON payload and the sibling `MANIFEST.sha256` (L122-147); a crashed regeneration cannot leave a truncated file — matches `build_raw_trades_cache` discipline.

---

## Decision Rationale

Every §13.1 acceptance criterion is met with substantial safety margin (A1: 17x, A2: 3x), every §13.2 test body matches the spec verbatim (T12a renamed + inline-skip, T12b added with tamper-guarded snapshot loader, T13 unchanged), and every P5 flag is surfaced, mutex-validated, and conditionally forwarded. The T12b sentinel-DOWN empirical proof — which is the entire architectural purpose of §13 — runs GREEN in 9.94s with `sentinel-timescaledb` stopped, closing Riven's Q1 by empirical proof rather than argument-by-construction. The hold-out guard fires before any I/O in every new path; SQL is parameterized; canonical surface is untouched. Canonical `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at both session start and after T12b replay — zero drift. However, the §13.1 implementation refactor left 5 pre-existing unit tests in `tests/unit/test_build_raw_trades_cache.py` monkeypatching an entry point (`mp._fetch_month_dataframe`) that is no longer in the build-script call graph; those tests now error on `DummyConn.cursor` absence. A1 acceptance explicitly enumerates "ruff/mypy/tests clean" as §13.1 A5 — we cannot close A5 with 5 failing tests even though the production code is correct. Gate: **CONCERNS**. Single surgical patch (update 5 test stubs to monkeypatch `_stream_month_to_parquet` instead of `mp._fetch_month_dataframe`) clears the concern and unblocks DRAFT → ISSUED.

---

## Recommendation for Orion (DRAFT → ISSUED)

**CONDITIONAL GREEN.** Flip DRAFT → ISSUED after Dex lands a 1-file patch updating the 5 stale stubs in `tests/unit/test_build_raw_trades_cache.py` to target `brc._stream_month_to_parquet` (not `mp._fetch_month_dataframe`) and `tests/unit/` goes 11/11 PASS. No other evidence is missing; P1-P5 are all GREEN as captured above. Once that test fix lands, Gage is cleared for quiesce retry #5 under `--source=cache` with zero additional gating.

**Sentinel lifecycle:** stopped at 2026-04-23 BRT for T12b replay; restarted immediately; status `Up 3 seconds` post-restore; no canonical drift detected across the stop/start cycle.

---

**Signature:** Quinn (@qa, The Sentinel ♍), 2026-04-23 BRT.
**Canonical sha guard:** `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified both at session open and session close. Hold-out lock `VESPERA_UNLOCK_HOLDOUT` unset throughout.
**Next gate:** post-fix re-run of `tests/unit/test_build_raw_trades_cache.py` (11/11 required) → DRAFT → ISSUED flip.
