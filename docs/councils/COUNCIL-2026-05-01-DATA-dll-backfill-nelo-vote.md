---
council: DATA-COUNCIL-2026-05-01
topic: DLL backfill viability for pre-2024 WDO archival window — Nelo authoritative ballot
date_brt: 2026-05-01
voter: Nelo (@profitdll-specialist)
role: ProfitDLL Specialist — Manual-First Keeper of the Nelogica API; sole authority on DLL retention reality, contract-vs-continuous behavior, and historic-trade callback quirks
branch: t003-data-acquisition-council
constraint_recap: |
  - Sentinel TimescaleDB current coverage: 2024-01-02 .. 2026-04-02 (manifest.csv 18 rows in_sample, year=2024-01..2025-06 confirmed; remainder TBC by Dara).
  - Quant Council R6-R8 (2026-05-01): PRIMARY = forward-time virgin 2026-05-01..2026-10-31; FALLBACK R8 = pre-2024 archival 2023-Q1..2024-Q3 contingent on (a) Dara confirming DLL coverage, (b) Sable auditing virgin status (no T002 leakage).
  - Nelo authority basis: manual_profitdll.txt (PDF pt_br oficial, 4452 lines) + feedback_profitdll_quirks.md canonical (2026-04-25) + Whale Detector v2 live mode (2026-03-09) + Sentinel backfill 2026-03-20 WDO empirical run.
  - Article II → Gage @devops EXCLUSIVE on git push; this vote = doc-only artifact under branch t003-data-acquisition-council; NO source mutation; NO push; NO DLL probe execution as part of this ballot.
  - Article IV → no invention; every clause source-anchored to manual section / feedback_profitdll_quirks.md entry / empirical Whale-Sentinel run / quirk registry Q##-* entry.
  - MANIFEST R5 (escopo-negativo): Nelo NÃO opina sobre regulação B3, microestrutura, custos — DLL-ONLY. Coverage windows que dependem de fases de pregão / calendário B3 → deferir a Nova.
authority_basis:
  - manual_profitdll.txt §3.1 (GetHistoryTrades signature, dtDateStart/dtDateEnd format)
  - manual_profitdll.txt §3.2 line 3730 (THistoryTradeCallback) + line 3750 (TProgressCallback)
  - manual_profitdll.txt §3 line 894-955 (NL_* error codes — NL_SERIE_NO_HISTORY 0x80000014, NL_SERIE_NO_DATA 0x80000016, NL_SERIE_NO_MORE_HISTORY 0x80000018)
  - feedback_profitdll_quirks.md §"Tickers e exchanges" (WDOFUT contínuo vs contratos específicos vencidos retornam 0 trades em ~19ms)
  - feedback_profitdll_quirks.md §"detalhe importante WDOFUT histórico" (progresso 99% por 35-45s antes de saltar 100%)
  - Whale Detector v2 live mode 2026-03-09 (validation reference)
  - Sentinel backfill 2026-03-20 (WDOFUT empirical retrieval — produced current 2024-01..2025-06 manifest)
  - Nelo quirk registry Q03-V (exchange="F"), Q05-V (GetAgentName length-first), Q09-E (contrato vigente vs sintético), Q10-E (progress 99% normal)
non_pre_emption:
  - This vote does NOT bind Dara on data engineering / parquet persistence layout (informs only)
  - This vote does NOT bind Sable on virgin-status audit (Sable has exclusive authority on hold-out leakage)
  - This vote does NOT bind Nova on calendar / rollover semantics for pre-2024 contracts (Nova authoritative)
  - This vote does NOT bind Quant Council R7 PRIMARY (forward-time) — assesses fallback R8 only
  - This vote does NOT authorize DLL probe execution; empirical test = separate authorization gate (Pax story + Quinn QA)
  - This vote does NOT mutate any code, schema, or manifest; it is a viability assessment ballot
---

# DATA-COUNCIL-2026-05-01 — Nelo Vote on DLL Pre-2024 WDO Backfill Viability

> **Author:** Nelo (@profitdll-specialist) — Manual-First Keeper of the ProfitDLL Nelogica API.
> **Date (BRT):** 2026-05-01.
> **Branch:** `t003-data-acquisition-council`. Vote = doc-only artifact; no source mutation; no DLL probe execution.
> **Authority lens:** ProfitDLL retention reality + historic-trade callback empirical behavior + WDO contract-vs-continuous quirk. FACT (manual oficial Nelogica PDF pt_br) vs OBSERVATION (Whale Detector + Sentinel empirical runs) vs UNKNOWN (pre-2024 untested in our codebase). Where manual is silent OR empirical is gap, I declare it explicitly — no invention.

---

## §1 DLL retention reality (autoritativa Nelo)

### §1.1 Manual oficial Nelogica — what it says about retention

The Nelogica manual `Manual - ProfitDLL pt_br.pdf` (`manual_profitdll.txt`) describes `GetHistoryTrades(ticker: PWideChar, bolsa: PWideChar, dtDateStart: PWideChar, dtDateEnd: PWideChar) → Integer` in §3.1 with the following semantic surface:

- **Date format** (manual §3.1 line 1737-1745): `"DD/MM/YYYY HH:mm:SS"` — no milliseconds on input.
- **Return value:** `NL_OK` (0) on dispatch success; the actual data flows through `THistoryTradeCallback` (manual §3.2 line 3730) with `TProgressCallback` (line 3750) reporting 1..100.
- **Error path explicit in manual §3 line 894-955:**
  - `NL_SERIE_NO_HISTORY` (`0x80000014`, dec -2147483628): "Série não tem histórico no servidor"
  - `NL_SERIE_NO_DATA` (`0x80000016`, dec -2147483626): "Série não tem dados (count = 0)"
  - `NL_SERIE_NO_MORE_HISTORY` (`0x80000018`, dec -2147483624): "Não tem mais dados disponíveis para a série"

**CRITICAL — what the manual does NOT say:**

> The manual `manual_profitdll.txt` contains **NO explicit retention window** for `GetHistoryTrades`. It does not commit to "N days back" or "N years back" anywhere in §3.1 or §3.2. The only example shown (manual §3.1 line ~1747) is `"PETR4"` with no date range constraint commentary. The Nelogica server **may serve any date the back-end retains** — but the back-end retention policy is **not contractualized in the public manual**. This is a load-bearing silence.

### §1.2 Empirically tested limits in our ecosystem (FACT)

| Source | Window tested | Ticker | Result |
|---|---|---|---|
| Sentinel backfill 2026-03-20 | 2024-01-02 .. 2025-06-30 | `WDOFUT` (contínuo) | **SUCCESS** — produced manifest.csv rows for year=2024-01..2025-06; ~9-14M trades/month; SHA256 sealed |
| Sentinel backfill 2026-03-20 | 2024-01..2024-12 | `WDOF24, WDOG24, ...` (contratos específicos vencidos) | **FAIL** — 0 trades returned in ~19ms (Q09-E confirmed) |
| Whale Detector v2 live | 2026-03-09 | `WDOFUT` real-time | **SUCCESS** — live mode functional |
| Whale Detector v1+v2 historic | various 2023-2024 | `WINFUT` historic | **FAIL** — `WINFUT` does NOT serve historic; only contrato vigente works for WIN historic (canonical quirks §Tickers) |

**Summary table — known empirical retention floor:**

```
WDOFUT historic (continuous proxy):
  CONFIRMED working: 2024-01-02 forward (Sentinel manifest)
  CONFIRMED NOT working: contratos específicos vencidos (any year) → 0 trades 19ms
  UNKNOWN: 2023-12-31 backward (NEVER TESTED in our codebase)

WINFUT historic:
  CONFIRMED NOT working (any window) — must use contrato vigente
  Therefore irrelevant for pre-2024 backfill scope

PETR4 historic (manual canonical example):
  Manual implies works, but spot stock NOT in scope of this council
```

### §1.3 WDOFUT continuous — what it actually is (Nelo authoritative)

`WDOFUT` is the **synthetic continuous-contract alias** that the Nelogica back-end resolves at query time to the active rolling front-month contract for the date range requested. The DLL itself does NOT roll on the client side — the server stitches the historical sequence by mapping each date to its then-active front contract (e.g., `WDOG24` for late-Jan/early-Feb 2024, `WDOH24` for Feb/Mar 2024, etc., per Nova rollover atlas; precise rollover dates ARE Nova authority — outside Nelo R5 scope).

**Implication for pre-2024:** Whether `WDOFUT` resolves correctly for, say, `dtDateStart = "01/12/2023"` depends entirely on (a) whether the Nelogica back-end retains the per-day mapping table for 2023, and (b) whether the per-day raw trade store covers December 2023. Neither (a) nor (b) is documented in the manual; both are server-side opaque.

---

## §2 Pre-2024 backfill viability assessment

### §2.1 Verdict: **NEEDS_EMPIRICAL_TEST** — not YES, not NO

I cannot, from manual + existing empirical runs alone, certify YES or NO for pre-2024. The honest answer:

| Evidence dimension | Status |
|---|---|
| Manual explicit retention statement | **ABSENT** (silent) |
| Empirical test in our codebase pre-2024 | **NEVER ATTEMPTED** |
| Adjacent empirical signal (2024-01 worked) | Suggests retention boundary is at OR earlier than 2024-01 — direction unknown |
| Vendor anecdote / forum knowledge | Out of scope (manual-first principle — I do not cite unsourced) |

**Therefore:** the question "can the DLL serve pre-2024 WDO?" requires an **empirical probe** — a small, time-boxed `GetHistoryTrades("WDOFUT", "F", "01/12/2023 09:00:00", "31/12/2023 18:00:00")` call against the production DLL with full instrumentation.

### §2.2 Likely outcomes ranked (Nelo prior, NOT certainty)

1. **PROBABLE (60%): WDOFUT 2023 works** — Nelogica retention is server-side and there is no published cliff at 2024-01-01. Sentinel reached back to 2024-01-02 simply because that was the project requirement, not a DLL boundary. If this holds, 2023-Q1..Q4 should backfill cleanly using same WDOFUT pipeline as Sentinel 2026-03-20.
2. **POSSIBLE (25%): WDOFUT works for 2023-H2, fails for 2023-H1 or earlier** — many vendor APIs have rolling-N-year retention (e.g., 24 months from current date). At BRT 2026-05-01, a 24-month floor lands at 2024-05; a 36-month floor lands at 2023-05. Either could explain why Sentinel only went back to 2024-01.
3. **POSSIBLE (10%): WDOFUT fails entirely for any pre-2024 window** with `NL_SERIE_NO_HISTORY` or 0-trades-in-19ms. If this happens, fallback R8 is structurally infeasible regardless of Sable virgin audit.
4. **EDGE (5%): WDOFUT returns partial / corrupted data** — silent gaps within the requested range. This is the most dangerous outcome for hold-out integrity and demands strict post-retrieval validation (Nova rollover anchors + DOMAIN_GLOSSARY holiday cross-check).

### §2.3 Pre-2024-specific quirk concerns (Nelo authoritative)

| Quirk | Applies to pre-2024? | Mitigation |
|---|---|---|
| Q09-E: contratos específicos vencidos → 0 trades 19ms | **YES, severely** — pre-2024 contracts (WDOF23..WDOZ23, WDOF24) ALL vencidos. NEVER use specific contracts for pre-2024 backfill. Use ONLY `WDOFUT` (continuous). | Hard rule: pipeline must reject any non-WDOFUT ticker for pre-2024 archival path. |
| Q10-E: 99% progress hangs 35-45s | **PROBABLY YES** — quirk is structural to DLL connection cycling, not date-dependent. Pre-2024 windows likely exhibit same hang. | Timeout ≥ 1800s (per Nelo init guide). Do NOT kill process at apparent stall. Watchdog idle threshold >120s without progress callback firing. |
| Q03-V: exchange="F" not "BMF" | YES (universal) | Hard-coded in pipeline. |
| Q08-E: `_cb_refs` global to prevent GC | YES (universal) | Same as Sentinel pipeline. |
| Q-AMB-02: timestamp separator `.` vs `:` for ms | YES (universal); pre-2024 may have different separator if DLL version evolved over server-stored data | Tolerant parser accepting both — already in Sentinel. Log first observed format on probe. |
| Q11-E: SetHistoryTradeCallback after init silently overwrites slot 9 | YES (universal) | Pass history_cb in `DLLInitializeMarketLogin` slot 9 directly; never reconfigure. |
| **NEW concern Q-PRE2024-?**: Nelogica back-end may have changed schema between 2023 and 2024 | UNKNOWN — would manifest as schema mismatch in returned trades (e.g., missing buy_agent / sell_agent fields, different tradeType enum range) | Probe must validate canonical 7-column schema (timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent) on the FIRST 1000 trades returned and abort on mismatch. |

### §2.4 Memory / storage budget (informational — Dara authoritative)

Per Sentinel manifest empirical: ~9-14M trades/month × 12 months ≈ 100-160M trades for full 2023. Parquet compressed at Sentinel ratio (~0.6-1.0 GB/month observed) → ~7-12 GB for full 2023-Q1..Q4. Feasible on local disk; well within budget. Dara owns final layout call.

---

## §3 Implementation plan if §2 favorable (Path A — empirical test → archival)

This plan is conditional on (a) empirical probe in §3.1 succeeding, (b) Sable virgin-status audit clearing, (c) Pax story authorizing execution, (d) Quinn QA gate on the pipeline code.

### §3.1 Step 1 — empirical probe (small, time-boxed window)

**Probe spec:**
- **Function:** `GetHistoryTrades("WDOFUT", "F", "01/12/2023 09:00:00", "20/12/2023 18:00:00")` — December 2023 first 3 weeks (avoids year-end illiquidity, well after any plausible 24-month cliff if it exists at 2024-04 boundary).
- **Why this window:** ~14 trading days → moderate volume (~5-10M trades expected if it works); recent enough that Q-PRE2024 schema-drift risk is minimal; far enough back to validate the retention claim concretely.
- **Instrumentation:**
  - Capture every `TProgressCallback` invocation with timestamp delta (validates Q10-E manifests as before).
  - Capture FIRST 100 trades from `THistoryTradeCallback` raw — log timestamp string verbatim (validates Q-AMB-02 separator), all 9 callback args, and presence of all canonical fields.
  - Hard timeout: 1800s. Watchdog: abort if no progress callback fires for >180s while progress < 100.
  - Capture return code from `GetHistoryTrades` (must be 0 = NL_OK; any NL_SERIE_* family = retention floor verdict).

**Outcome decision tree:**
- Return = 0, progress reaches 100, ≥ 5M trades received, schema validates → **PROCEED Step 2**.
- Return = `NL_SERIE_NO_HISTORY` or 0 trades in <60s with no real progress → **ABORT — retention cliff confirmed at or after 2023-12; recommend Path B forward-only**.
- Return = 0 but only partial data / schema mismatch / Q-PRE2024 trips → **HOLD — escalate to council; do not proceed to bulk backfill until anomaly understood**.

### §3.2 Step 2 — broaden empirical to multi-month proof-of-coverage

If §3.1 succeeds, run **3 more probe windows** (NOT bulk backfill yet):
- 2023-09-01 .. 2023-09-15 (Q3 sample)
- 2023-06-01 .. 2023-06-15 (Q2 sample)
- 2023-03-01 .. 2023-03-15 (Q1 sample — earliest target of fallback R8)

Each probe: same instrumentation as §3.1; record retrieval time, trade count, schema integrity. This builds an empirical retention floor estimate before committing storage.

### §3.3 Step 3 — schema validation against canonical 7 columns

Per Sentinel canonical: `(timestamp BRT naive, ticker, price, qty, aggressor, buy_agent, sell_agent)`. Pre-2024 trades must populate all 7. Aggressor must be in `{BUY=2, SELL=3, NONE=other}` per quirks §Callbacks. Any trade with `tradeType not in (2,3)` filtered to `aggressor=NONE` (current canonical behavior). NO new columns added in archive phase — schema is frozen.

### §3.4 Step 4 — cross-check vs DOMAIN_GLOSSARY (Nova authority — Nelo defers)

This step is OUT of Nelo R5 scope but listed for completeness. Nova authoritative on:
- Rollover dates 2023 (3rd Wednesday: 2023-01-18, 2023-02-15, 2023-03-15, 2023-04-19, 2023-05-17, 2023-06-21, 2023-07-19, 2023-08-16, 2023-09-20, 2023-10-18, 2023-11-22, 2023-12-20 — to be confirmed by Nova).
- Holidays 2023 (Carnaval 2023-02-20/21, Sexta-Santa 2023-04-07, Tiradentes 2023-04-21, Corpus Christi 2023-06-08, Independência 2023-09-07, Padroeira 2023-10-12, Finados 2023-11-02, Proclamação 2023-11-15, Consciência Negra 2023-11-20, Natal 2023-12-25 — Nova validates).
- COPOM 2023 calendar.

**Nelo's only DLL contribution here:** the empirical retrieval should NOT report trades on dates Nova flags as B3-closed. If it does, that is a data-quality red flag (probably DLL serving cross-session bleed or Nelogica timezone bug) requiring HOLD.

### §3.5 Step 5 — persistence layout (Dara authority — Nelo defers)

Suggested path for archive phase (Dara authoritative on final):

```
data/archive/year=2023/month=01/wdo-2023-01.parquet
data/archive/year=2023/month=02/wdo-2023-02.parquet
...
data/archive/year=2023/month=12/wdo-2023-12.parquet
```

Hive-partitioned matching `data/in_sample/year=YYYY/month=MM/` pattern already in use. Same compression, same row-group sizing, same canonical 7-column schema.

### §3.6 Step 6 — manifest update with new `phase=archive`

Dara extends `data/manifest.csv` with new phase value `archive` (distinct from existing `warmup` / `in_sample` / `holdout`). Rows include path, rows count, sha256, start_ts_brt, end_ts_brt, ticker=`WDO` (normalized), phase=`archive`, generated_at_brt. Existing 18 rows untouched.

### §3.7 Step 7 — Sable virgin-status audit (Sable EXCLUSIVE authority)

This is gating. Sable must certify:
- No T002 R6-R8 backtest ever consumed pre-2024 data → trivially TRUE since manifest shows no archive rows exist; T002 in_sample starts 2024-01.
- No Mira feature engineering ever fit on pre-2024 → must verify via Mira's training-data manifests.
- No Beckett CPCV split ever included pre-2024 → manifest pinning audit.
- No human eyeballing of pre-2024 charts that could leak intuition into hypothesis design (this is the slipperiest leakage vector — Sable owns judgment).

**Nelo position:** I observe no DLL-side leakage path for pre-2024 — the data has never entered our pipeline. But "virgin-as-data" ≠ "virgin-as-knowledge"; Sable's audit is the binding gate.

---

## §4 Alternative paths

### §4.1 Path B — accept forward-time virgin only (Quant Council R7 PRIMARY)

- Wait until 2026-10-31 BRT to accumulate 6 months of forward virgin data.
- Zero DLL retention risk; zero Q-PRE2024 schema-drift risk; zero Sable virgin-question.
- **Cost:** 6-month delay on H_next walk-forward validation.
- **Nelo verdict on Path B:** technically lowest-risk; the answer if this council cannot tolerate empirical-probe gating delay.

### §4.2 Path C — both in parallel (recommended hedge)

- **Track 1:** Authorize empirical probe per §3.1 immediately (Pax story scoped to probe-only, ~1 day work).
- **Track 2:** Forward-time accumulation begins 2026-05-01 regardless (no dependency on probe outcome).
- **Convergence:** by 2026-06-01, probe verdict known; if YES, bulk archive backfill proceeds; if NO, Path B sole reliance, no time lost.
- **Nelo verdict on Path C:** structurally dominant — adds ~1 day of probe work for chance of unlocking 9-12 months extra hold-out data. Asymmetric upside.

---

## §5 Anti-pattern flags (Nelo authoritative — DO NOT VIOLATE)

| # | Anti-pattern | Severity | Manual / Quirk anchor |
|---|---|---|---|
| AP1 | Use `WDOF24, WDOG24, ...` (specific expired contracts) for pre-2024 backfill | **FATAL** — guaranteed 0 trades 19ms | Q09-E |
| AP2 | Use `WINFUT` for any historic backfill | **FATAL** — never works historically | feedback_profitdll_quirks.md §Tickers |
| AP3 | Use `CFUNCTYPE` for callbacks instead of `WINFUNCTYPE` | **FATAL** — DLL is `__stdcall` | Q01-V; manual §3.2 line 2735 |
| AP4 | Use `c_char_p` (UTF-8) for string args instead of `c_wchar_p` (UTF-16) | **FATAL** — corrupts strings | Q02-V |
| AP5 | Pass `"BMF"` as exchange instead of `"F"` | **FATAL** — `NL_EXCHANGE_UNKNOWN` | Q03-V; manual §3.1 line 1673 |
| AP6 | Call `SetHistoryTradeCallback` AFTER `DLLInitializeMarketLogin` | **HIGH** — silently overwrites slot 9 | Q11-E |
| AP7 | Kill the process during 99% progress hang (35-45s normal) | **HIGH** — re-triggers full re-fetch and may exhaust retries | Q10-E; manual §3.1 line 1750 |
| AP8 | Forget `_cb_refs` global list — Python GC collects callbacks | **MEDIUM** — random callback drop after minutes | Q08-E |
| AP9 | Call any DLL function from inside a callback | **HIGH** — undefined behavior, deadlocks | Q04-V; manual §3.2 line 2730, §4 line 4394 |
| AP10 | Resolve agent name (GetAgentName) inside callback | **HIGH** — same as AP9 + manual §3.1 line 1707 (length-first protocol) | Q05-V |
| AP11 | Convert timestamps to UTC before storage | **MEDIUM** — destroys session-phase semantics | MANIFEST R2; consumes from Nova/Beckett/Mira |
| AP12 | Bulk-backfill 2023 in one call without empirical probe first | **HIGH** — wastes 2-4 hours on possibly-empty DLL response; also unknown schema drift risk Q-PRE2024 | §3.1 of this doc |
| AP13 | Skip Sable virgin-status audit on the assumption "data was never touched" | **HIGH** — knowledge leakage ≠ data leakage; Sable owns the judgment | §3.7 of this doc |

---

## §6 Recommendation — Nelo authoritative ballot

### §6.1 Vote

**`APPROVE_EMPIRICAL_TEST`** — conditioned on Path C (parallel track) execution.

### §6.2 Conditions under which empirical test is safe

1. **Probe scope strictly bounded** to §3.1 spec: single window 2023-12-01 .. 2023-12-20, WDOFUT only, full instrumentation, hard timeout 1800s.
2. **Pax story authorization** required before probe execution (no agent-driven impulsive run).
3. **Quinn QA gate** on the probe script before run (validates argtypes/restype, _cb_refs, exchange="F", timeout, schema-validation harness).
4. **Sable consulted** on probe data handling: where the probe's returned trades are stored DURING probe, who has access, and whether intermediate inspection itself constitutes leakage. My read: probe data should land in `data/_scratch/dll-probe-2023-12/` (gitignored) and NOT be incorporated into hold-out unless §3.7 audit clears the full archive plan.
5. **No bulk backfill** until §3.1 succeeds AND §3.2 multi-month proof-of-coverage clears AND §3.7 Sable audit clears.
6. **No silent fallback** — if probe fails, Path B is explicit and ratified, not a default.

### §6.3 Who operates the DLL probe

Per MANIFEST R12-R14:

- **Nelo (me)** authors the probe spec (this document §3.1) and reviews the probe script for DLL-correctness (manual fidelity, quirks compliance). I do NOT execute production DLL calls — that is operational, not specification.
- **Tiago (@execution-trader)** has SendOrder authority but does NOT have historic-trade-fetch authority by role. Probe execution is data-engineering, not execution.
- **Dara (@data-engineer)** owns probe execution: writes the probe script following Nelo's spec, submits to Quinn QA, runs under Pax story authorization, persists output to scratch, reports back to council.
- **Sable** audits virgin status of any retrieved data before any move from scratch to archive.
- **Gage (@devops)** is the only agent who can `git push` any resulting code/manifest changes (Article II).

This delegation matrix has Nelo (me) as DOMAIN authority on the WHAT, Dara as FRAMEWORK authority on the HOW-of-execution, Sable as governance gate, Quinn as QA gate, Pax as story gate, Gage as merge gate. Six-way separation; no agent can unilaterally extend hold-out coverage.

### §6.4 Confidence calibration

| Claim | Confidence |
|---|---|
| Manual is silent on retention floor | HIGH (verified by direct re-read of manual_profitdll.txt sections 3.1 + 3.2 + 3 error-codes) |
| WDOFUT continuous is the ONLY viable ticker for any historic | HIGH (Q09-E + Sentinel empirical) |
| Quirks Q01-V..Q11-E apply identically pre-2024 | HIGH for universal quirks (Q01-Q05, Q08); MEDIUM for date-coupled (Q-AMB-02 separator, Q-PRE2024 schema drift unknown) |
| Pre-2024 DLL serves data | UNKNOWN — empirical probe required (§2.1) |
| Probe is technically safe under conditions §6.2 | HIGH |
| Path C dominates Path B | HIGH conditional on probe authorization timeline (~1 day) being acceptable |

---

## §7 Article IV self-audit (source anchors)

Every claim in this ballot traces to one of the following:

1. `manual_profitdll.txt` §3.1 GetHistoryTrades signature + line 1737-1745 date format + line 1673 exchange "F" example.
2. `manual_profitdll.txt` §3.2 line 2730 callback-no-DLL rule + line 2735 stdcall + line 3730 THistoryTradeCallback + line 3750 TProgressCallback.
3. `manual_profitdll.txt` §3 line 894-955 NL_* error codes (NL_SERIE_NO_HISTORY, NL_SERIE_NO_DATA, NL_SERIE_NO_MORE_HISTORY, NL_EXCHANGE_UNKNOWN).
4. `feedback_profitdll_quirks.md` (canonical 2026-04-25) §"Tickers e exchanges" (WDOFUT contínuo, contratos vencidos 0 trades 19ms) + §"detalhe importante WDOFUT histórico" (99% hang) + §Callbacks (WINFUNCTYPE/c_wchar_p/queue.put_nowait).
5. Sentinel backfill 2026-03-20 empirical run reflected in `data/manifest.csv` (18 rows, year=2024-01..2025-06 confirmed; WDOFUT continuous successful).
6. Whale Detector v2 live mode 2026-03-09 (validation reference, real-time mode confirmed; not historic but anchors Sentinel's WDOFUT pipeline lineage).
7. Nelo internal quirk registry Q01-V..Q11-E + Q-AMB-01..03 (canonical, embedded in profitdll-specialist agent definition).

**No invented retention numbers. No invented vendor commitments. Where evidence is absent, I declare UNKNOWN explicitly (§2.1, §6.4).**

---

## §8 Cosign

Cosign Nelo @profitdll-specialist 2026-05-01 BRT — Data Acquisition Council DLL lead ballot.

Vote: **APPROVE_EMPIRICAL_TEST** under Path C parallel-track conditions §6.2.
Branch: `t003-data-acquisition-council`. Doc-only artifact. No source mutation. No DLL execution. No push.

— Nelo, guardião da DLL.
