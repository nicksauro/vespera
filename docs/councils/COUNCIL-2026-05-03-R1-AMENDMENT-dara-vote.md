# Dara Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Dara (@data-engineer)
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored

---

## §1 Verdict + reasoning

**APPROVE_WITH_CONDITIONS.** The Phase 2C orchestrator is operationally sound for the bulk-acquisition layer: 50/50 chunks `status=ok` in `D:\Algotrader\dll-backfill\manifest.csv` (verified column 5 distribution), atomic manifest write + history snapshots + idempotent resume implemented per amendment §1.2, Riven blocking caps wired (`max-attempts=3`, `max-consecutive-failures=3`, `max-wall-time-s=23400`, `max_qfd_global_pct=0.001`), 4 critical probe bugs fixed in `cbd6813`, and storage discipline preserved (D:\ off-repo, parquets gitignored). Window 2024-01-01 upper bound has zero overlap with Sentinel manifest floor 2024-01-02 → R10 absolute custodial **NOT touched** by this amendment (manifest mutation deferred to A6/A7 cosign chain). 0/8 Anti-Article-IV Guards affected.

I cannot approve unconditionally because: (a) **Sable MA-10 AC gap is real** — the current orchestrator is a Phase-2C prototype with a 15-column `# backfill-manifest v1 - NOT R10 custodial` schema; T003.A2 AC1-AC10 promises 19-col manifest + extracted `IncrementalParquetSink`/`ChunkPlanner`/`ManifestStore`/`ValidateGate` + `recover_parquet_from_jsonl.py` + `generate_backfill_report.py` (last two confirmed MISSING from `scripts/`); (b) **D:\ contamination MA-08 confirmed** — 6 dirs (`test-*` x5 + `smoke-test`) co-mingled with 50 production chunk dirs in `D:\Algotrader\dll-backfill\`; (c) **Schema parity audit unexecuted** — 7-col canonical schema (timestamp/ticker/price/qty/aggressor/buy_agent/sell_agent) vs 50 chunk parquets is the gating downstream gate I owe (R5).

The amendment is ratifiable for **bulk acquisition completion under Phase-2C**; the AC-gap closure is sequenced to A2-A7 dispatch chain, NOT to bulk-window expansion itself.

## §2 Conditions

1. **D:\ cleanup before A2 dispatch (MA-08):** `D:\Algotrader\dll-backfill\` MUST be cleaned — all `test-*` + `smoke-test/` + `verify-*` dirs moved to `D:\Algotrader\dll-backfill-scratch\` (or deleted). 50 production chunk dirs only at root before A2-Dara schema parity opens.
2. **Manifest v1→v2 schema gap closure tracked in T003.A2 AC, not bulk:** Phase-2C 15-col `manifest.csv` is AUTHORITATIVE-FOR-BULK only (header explicitly says "NOT R10 custodial"). T003.A2 commit-1 MUST extract `ManifestStore` + extend to 19 cols (add: schema_parity_status, validate_gate_status, parity_audit_ts_brt, parity_audit_sha) before A2 schema parity verdict commits. `recover_parquet_from_jsonl.py` + `generate_backfill_report.py` deferred to A2 commits-3/4 acceptable.
3. **Schema parity reference frozen pre-A2:** A2 reference month = 2024-01 from existing `data/in_sample/year=2024/month=01/` parquet (sha256 byte-equal locked). All 50 chunks compared against same reference; mismatch = fail-closed per R5/§3.4 of original ballot.
4. **R15 token rename non-deferrable (concur Nelo cond #3):** `_R1_OVERRIDE_TOKEN` rename to `ratified_council_2026_05_03_R1_amendment_quorum_<sha>` BEFORE A2-Dara executes first parity verification. Audit-trail integrity is downstream-blocking.
5. **R14 spike completion (concur Nelo cond #1+#2):** S1-retry-0915 outcome MUST land + 0315 qfd characterization MUST classify transient-vs-structural before A2 schema audit dispatches; if structural, A4-Mira propagates `qfd_pct >0.1%` regime-stationarity flag.
6. **Hard-cap 2024-01-01 codified (concur Nelo cond #6):** No silent rolling expansion. 2022 backfill = NEW Council quorum + fresh spike protocol.

## §3 Concerns + mitigations (per 7 audit points)

1. **A2 schema parity feasibility (50 chunks ~12mo):** ~2-3 sessions (1 ref freeze + 1 batch parity walk via pyarrow schema().equals() + 1 enum subset audit on `aggressor`/`trade_type`). Bottleneck is enum subset verification pre-2024 vs current canonical, not throughput. Mitigation: cond #3 freeze + fail-closed rule per ballot §3.4 prior.
2. **MA-10 AC gap (15 vs 19 cols + missing extracted libs):** Phase-2C prototype is **ENOUGH for bulk acquisition + downstream A2-A8 audits**, but T003.A2 commits MUST close the extraction gap (`ManifestStore`/`ChunkPlanner`/`ValidateGate` from `dll_backfill_lib.py`) and add 4 audit-trail cols. Mitigation: cond #2 sequences extraction to A2 commits.
3. **MA-08 D:\ contamination:** PASS_WITH_CONDITION cleanup. Contamination is co-located not commingled-by-content (separate dirs); manifest correctly excludes test/smoke rows (50 ok = production only). Mitigation: cond #1 cleanup before A2.
4. **Atomic manifest + resume:** confirmed (amendment §1.2 + verified `manifest.heartbeat` + `orchestrator.pid` + `manifest.csv` co-located, `status=ok` skip-protocol idempotent). Engineering effort for POST-A6 R10 manifest extension (phase=archive, append-only, byte-equal): **~4-6 hours** (classify_phase enum + 3 boundary tests + Sable byte-equal verifier + MWF cosign loop integration).
5. **Cross-drive `_REPO_ROOT` monkey-patch:** acceptable engineering precedent. Pattern matches `dll_control_check_*.py` per Sable C1 INFO; subprocess.Popen fresh-process boundary makes monkey-patch scope-bounded (no leak to parent). Not architecturally clean but pragmatically justified for Win64 cross-drive ProfitDLL constraint.
6. **Recovery path (e.g., 35/50 partial):** **resume protocol via existing idempotent skip** (status=ok rows skipped on re-run; failed/partial rows re-attempted up to `max-attempts=3`). NO mini-Council reconvene needed for partial. Discard whole bulk only IF >25% chunks fail OR systemic schema-drift surfaces (>3 chunks parity-fail in A2). Engineering opinion: re-run failed chunks with `max-consecutive-failures=3` cap; if cap trips → escalate to Riven + Nelo + Council.
7. **Pre-2023 schema drift risk:** **establish hard-stop at 2023-01-01.** ProfitDLL retention pre-2023 is unprobed; 2022 may carry pre-RLP-rule regime + pre-BMF→F transition + potentially pre-DLL-version schema variance. NO rolling expansion in spirit — every additional year = fresh spike protocol + Council quorum (concur Nelo #6).

## §4 Effort estimates

| Track | Effort | Notes |
|---|---|---|
| A2 schema parity (50 chunks vs 2024-01 ref) | **2-3 sessions** | byte-equal 7-col + enum subset + aggressor/trade_type audit + fail-closed gate |
| Post-A6 manifest extension (R10 phase=archive append) | **4-6 hours** | classify_phase enum + boundary tests + byte-equal verifier + MWF cosign loop |
| MA-10 AC gap closure (T003.A2 commits) | **3-4 sessions** | extract ManifestStore/ChunkPlanner/ValidateGate + recover_parquet_from_jsonl + generate_backfill_report + 19-col extension |
| D:\ cleanup MA-08 | **0.25 sessions** | move test-*/smoke-test/verify-* to scratch, regenerate orchestrator state if needed |

Dara solo budget A2-A7 chain: **~6-9 sessions** (parallelizable with Nova/Mira/Sable).

## §5 Source anchors

- Manifest 15-col schema + "NOT R10 custodial" header: `D:\Algotrader\dll-backfill\manifest.csv` lines 1-2 (verified read 2026-05-03)
- 50 ok production chunks: `awk -F',' 'NR>2 {print $5}' manifest.csv | sort | uniq -c` → 50 ok
- D:\ contamination dirs: 5 `test-*` + 1 `smoke-test` + 1 `verify-2023-12-29` (MA-08 confirmed)
- Missing scripts: `scripts/recover_parquet_from_jsonl.py` + `scripts/generate_backfill_report.py` NOT FOUND (MA-10 confirmed)
- Existing scripts present: `scripts/dll_backfill_{lib,smoke,chunk_runner,orchestrator,launch_detached}.py` (5/7 of T003.A2 promised set)
- Atomic manifest + heartbeat + pid co-located: `manifest.heartbeat`, `orchestrator.pid`, `orchestrator.log` present in D:\ root
- Original Council R5/R10/R12 binding: `docs/councils/COUNCIL-2026-05-01-DATA-resolution.md` §3.1-3.3
- Prior Dara vote engineering precedent: `docs/councils/COUNCIL-2026-05-01-DATA-dll-backfill-dara-vote.md` §3.4 fail-closed schema rule + §6.1 Gate A2
- Sentinel manifest floor 2024-01-02 (zero overlap): amendment §2.1
- Riven caps NON-NEGOTIABLE: amendment §1.2
- 0/8 Anti-Article-IV Guards: amendment §3
- R10 absolute custodial preserved (this amendment does NOT mutate `data/manifest.csv`): amendment §2.1 + §2.4

— Dara, data engineering, ballot self-audited 2026-05-03
