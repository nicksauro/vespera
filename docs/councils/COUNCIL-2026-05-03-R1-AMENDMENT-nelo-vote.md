# Nelo Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Nelo (@profitdll-specialist) — DLL guardian
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored

---

## §1 Verdict + reasoning

**APPROVE_WITH_CONDITIONS.** Empirical retention is confirmed for **5/6** sample dates spread across the proposed bulk window (2023-01..2023-11), totaling ~3.87M trades persisted across S1a+S1b+retry-0315 (sums of `trades_persisted`: 734,902 + 990,223 + 772,038 + 672,464 + 698,622). The Phase 2C orchestrator framework provides hard-kill envelopes (Riven caps §1.2 amendment) and the 4 critical probe bugs surfaced 2026-05-02 are now fixed in `cbd6813` (verified: 8-slot MarketLogin ABI + Q-FIN-12-E DLL quiesce + window-aware schema + cross-drive Path). Risk surface is bounded: window 2023-01-01..2024-01-01 has zero overlap with Sentinel manifest floor 2024-01-02, R10 manifest mutation still gated downstream by user MWF cosign, and 0/8 Anti-Article-IV Guards are touched (per amendment §3).

I am NOT comfortable approving unconditionally because: (a) S1-2023-09-15 errored at exit 3 and was never retried — a genuine retention claim for September is currently absent, not just "not yet verified"; (b) S1-2023-03-15 retry succeeded but with `queue_full_drops=73,657` (~7.4% drop ratio against 990,223 persisted) — root-cause must be characterized as transient vs structural before bulk hits structurally similar dates; (c) `Q-FIN-12-E` + 8-slot MarketLogin distinction are NOT in `feedback_profitdll_quirks.md` (Sable MA-05 confirmed); (d) the override token still reads `ack_dara_aria_council_2026_05_01` in code (`chunk_runner.py:49`, `orchestrator.py:419`) — this is misleading audit-trail today; (e) orchestrator does NOT hard-reject non-WDOFUT tickers (only docstrings/help-text mention WDOFUT — `chunk_runner.py:56`, `orchestrator.py:676`).

R1' window expansion is justified by spike evidence — but only with R14 (close 0915 + 0315 root cause) AND R15 (token rename + quirks registry update) executed BEFORE first orchestrator chunk of A2 dispatch.

## §2 Conditions (APPROVE_WITH_CONDITIONS)

1. **R14 PRECEDES bulk:** S1-retry-0915 MUST execute and reach `outcome ∈ {partial_coverage, full_month_works}` before any A2 chunk runs. If 0915 retry persistently errors, R1' narrows to `2023-{01,03,05,07,11}-* + 2023-12` only (5 confirmed months) and 2023-08..2023-10 marked `RETENTION_GAP_OPEN` until A4-Mira regime ruling.
2. **0315 qfd characterization:** root-cause investigation MUST classify `queue_full_drops=73,657` as transient (random burst) vs structural (auction-day pattern reproducible). If structural, A2-Dara MUST raise `max-attempts` per chunk and halve initial chunk size for matching auction days, OR propagate `qfd_pct >0.1%` flag to A4-Mira regime stationarity ruling.
3. **R15 commit-4 rename non-deferrable:** `_R1_OVERRIDE_TOKEN` MUST be renamed to `ratified_council_2026_05_03_R1_amendment_quorum_<sha>` BEFORE first A2 chunk; docstrings at `chunk_runner.py:14-18` and `orchestrator.py:26` must source-anchor to this amendment SHA + Council ID.
4. **Quirks registry update before A2 dispatch:** `feedback_profitdll_quirks.md` MUST gain entries for: Q-FIN-12-E (DLL quiesce post-progress=100), 8-slot MarketLogin ABI distinction (vs 11-slot full DLLInitializeLogin), 25% aggressor threshold rationale (auction-heavy first 1000), and AP-D-14 NEW (post-finalize callback SEH).
5. **Ticker hard-reject:** `chunk_runner.py` _parse_args() MUST hard-reject `args.ticker not in {"WDOFUT"}` with exit 3, source-anchored to Q09-E. Help-text alone is insufficient guard.
6. **Hard-cap precedent:** R1' window upper bound 2024-01-01 hard-capped (no rolling expansion). Future pre-2023 backfill requires NEW Council quorum + fresh spike protocol — this amendment does NOT establish silent rolling-expansion precedent.

## §3 Concerns + mitigations

1. **Retention floor evidence (5/6 with qualifiers):** Acceptable for HYPOTHESIS bulk under Riven caps (caps catch silent gaps within 3 consecutive failures), INSUFFICIENT for unqualified "retention proven". Mitigation: Condition #1 (R14 0915 retry blocks bulk).
2. **Q-FIN-12-E + slot-6 vs registry stale:** `cbd6813` fix is correct (verified `chunk_runner.py` calls `probe.run_probe()` with 8-slot probe; commit message explicitly cites Manual §3.1 L991-1010 for MarketLogin and §4 L4394 for callback rentry rule). Registry stale is the gap. Mitigation: Condition #4 (registry update gated to commit-4).
3. **Q09-E continuous-only enforcement:** Orchestrator does NOT hard-reject non-WDOFUT — `--ticker` is free string. Today this is documentation-only guard. Mitigation: Condition #5 (parse-time hard-reject).
4. **Token audit-trail misleading:** Current value is technically "Dara/Aria pre-Council acknowledgement" — NOT Council-quorum-ratified. Mitigation: Condition #3 (rename non-deferrable to commit-4, BEFORE A2 first chunk).
5. **AP-D-01..AP-D-14 telemetry monitoring:** AP-D-14 (post-finalize callback SEH) does NOT exist as named flag in orchestrator output today. Mitigation: Condition #4 (registry adds AP-D-14; A2-Dara wires telemetry monitor).
6. **Pre-2023 precedent risk:** Without explicit hard-cap, R1' could be cited to silently expand to 2022. Mitigation: Condition #6 (hard-cap 2024-01-01 codified; future expansion = new Council).

## §4 Source anchors

- Spike outcomes: `data/dll-probes/SPIKE-NELO/spike-summary-S1a.json:9-50`, `spike-summary-S1b.json:9-50`, `spike-summary-S1-retry-0315.json:5-19`
- 8-slot MarketLogin fix + Q-FIN-12-E quiesce: `git show cbd6813` commit message + `scripts/dll_probe_2023_12_wdofut.py` (slot wiring rewrite)
- Override token current value: `scripts/dll_backfill_chunk_runner.py:49`, `scripts/dll_backfill_orchestrator.py:419`
- Ticker free-string (no hard reject): `scripts/dll_backfill_chunk_runner.py:56`, `scripts/dll_backfill_orchestrator.py:676`
- Manual references for fix correctness: Manual §3.1 L991-1010 (MarketLogin 8 callbacks), §4 L4394 (no DLL calls in callback)
- Quirks registry stale: `~/.claude/projects/C--Windows-system32/memory/feedback_profitdll_quirks.md` (no Q-FIN-12-E / AP-D-14 / 8-slot entries; only Q-FIN line 22 references it as defense-in-depth justification)
- Sentinel manifest floor: amendment §2.1 + custodial constraint R10 (preserved)

— Nelo, DLL guardian, ballot self-audited 2026-05-03
