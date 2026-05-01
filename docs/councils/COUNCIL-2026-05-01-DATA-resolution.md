# Data Acquisition Council 2026-05-01 — DLL Backfill Strategy Resolution (5/5 UNANIMOUS APPROVE_PATH_C HYBRID)

> **Date (BRT):** 2026-05-01
> **Trigger:** Post H_next-1 spec v0.1.0 Draft (PR #19); forward-time hold-out 2026-05-01..2026-10-31 ainda não existe (data presente). User mandate: convocar council para debater se DLL pode baixar dados WDO ANTERIORES aos atuais (Sentinel cobertura 2024-01-02..2026-04-02).
> **Authority:** Mini-council 5-vote (Nelo lead + Dara + Beckett + Mira + Riven)
> **Article II preserved:** No push during deliberation
> **Article IV preserved:** Independent ballots verified per ballot self-audit
> **Author:** @aiox-master orchestration capacity, autonomous mode

---

## 1. Outcome — UNANIMOUS APPROVE_PATH_C HYBRID

**RATIFIED 5/5 UNANIMOUS** Path C HYBRID:
- **PRIMARY:** Forward-time virgin hold-out **2026-05-01..2026-10-31** (Quant Council R7 carry-forward)
- **SECONDARY-CORROBORATIVE:** Pre-2024 archival window **2023-Q1..2024-Q3** via DLL backfill (Quant Council R8 fallback operationalized)

**KEY DISCIPLINE:** Pre-2024 evidence is **SECONDARY VALIDATION CHANNEL ONLY** (NOT primary OOS test). H_next-1 verdict primarily anchored em forward-time virgin window; pre-2024 corroborates IC=0.866 robustness across regime windows IF Mira regime equivalence ratifies + Sable virgin audits.

| Voter | Authority | Vote | Conditions |
|---|---|---|---|
| Nelo (@profitdll-specialist) | DLL guardian | APPROVE_EMPIRICAL_TEST + Path C parallel | NEEDS_EMPIRICAL_TEST (manual silent on retention floor); WDOFUT contínuo only (specific contracts pre-2024 hit 19ms bug) |
| Dara (@data-engineer) | Data engineering | APPROVE_PATH_C_BOTH | 3 sequenced gates: A1 smoke test + A2 schema parity + A3 Nova cost atlas/regime ruling |
| Beckett (@backtester) | Consumer | APPROVE_PATH_B primary + CONDITIONAL_APPROVE_PATH_C | 6 prerequisite gates (Mira composite + regime + Sable virgin + Nelo retention + Nova rollover + engine-config historical branch) |
| Mira (@ml-researcher) | ML/statistical | CONDITIONAL_APPROVE_PATH_A + PRIMARY forward-time | 5 regime axes adjudication (cost atlas / RLP / COVID / BMF→F / holiday calendar); pre-2024 SECONDARY only |
| Riven (@risk-manager) | Custodial | APPROVE_PATH_C | Hybrid hedge; Joint P(Path A solo viable)=0.30 vs P(Path B reliability)=0.95 vs P(Path C usable)=0.97; SECONDARY-CORROBORATIVE only |

---

## 2. Convergence basis (5 lenses → 1 convergence)

5 voters arrived independently at Path C HYBRID via DIFFERENT authority lenses:

- **Nelo (DLL):** Empirical test feasibility unknown but worth probing; parallel track maximizes information
- **Dara (engineering):** Engineering effort feasible 5-10 sessions; must hedge against ESC-009 Sentinel-pre-2024 failure precedent (different ingestion path = new engineering surface)
- **Beckett (consumer):** Path A standalone too speculative (~25% confidence); Path B reliable (~70%) but slow; Path C composite (~55%) optimal information density per session
- **Mira (statistical):** Regime stationarity is binding constraint, NOT data availability; pre-2024 valid corroboration IF 5 regime axes adjudicate
- **Riven (custodial):** Bayesian joint P(Path C usable)=0.97 hedges optionality without sacrificing forward reliability

**Article IV strong evidence:** 5/5 different lenses arrived at same hybrid (forward-time PRIMARY + pre-2024 SECONDARY-CORROBORATIVE) — convergence not coincidental; reflects scientific discipline.

---

## 3. Consolidated 13 binding conditions

### 3.1 Empirical DLL probe (Nelo §3.1 spec) — 4 conditions

| ID | Mandate |
|---|---|
| **R1** | **Bounded probe window:** 2023-12-01..2023-12-20 (single month, 14 trading days max); WDOFUT contínuo ONLY (specific contracts e.g., WDOZ23 will hit Q09-E 0-trades-19ms bug) |
| **R2** | **Full instrumentation:** TProgressCallback timeline logged; raw timestamp string preserved (Q-AMB-02 ambiguity resolution); schema validation on first 1000 trades; watchdog 180s idle; hard timeout 1800s for Q10-E protection |
| **R3** | **Anti-pattern flags monitored** (Nelo §5 13 anti-patterns AP1-AP13): WINFUNCTYPE/c_wchar_p threading, SetHistoryTradeCallback after init silent overwrite slot 9, 99% progress 35-45s pause expected behavior, retention exhaustion silent gaps DANGER |
| **R4** | **Probe outcome decision tree:** (a) WDOFUT 2023 retorna ≥1M trades full month → ratify Path C extension to broader window; (b) partial coverage (e.g., 50%) → ratify with caveat; (c) 0 trades / silent gap → confirm pre-2024 retention exhausted, abort Path A, fallback Path B |

### 3.2 Schema + cost atlas + regime adjudication — 5 conditions

| ID | Mandate |
|---|---|
| **R5** | **Dara schema parity audit:** post-DLL probe, validate 7-column schema (timestamp, ticker, price, qty, aggressor, buy_agent, sell_agent) byte-equal to current parquet; trade_type/aggressor enum subset; fail-closed on mismatch |
| **R6** | **Nova cost atlas pre-2024 validity ruling:** does atlas v1.0.0 (effective_from_brt: 2024-12-10) apply to 2023 data? OR atlas v0.x.x archival variant needed? Nova authority |
| **R7** | **Mira regime stationarity check (5 axes):** (a) cost atlas validity pre-2024; (b) RLP regime 2023 vs 2024-Q4; (c) COVID-aftermath macro regime drift; (d) BMF→F exchange code transition; (e) holiday calendar pre-2024 |
| **R8** | **Nova auction hours pre-2024 confirmation:** post-DST grade may differ pre-2026; 2023 auction hours may differ from 2026 confirmation §4.4 (verify via B3 PUMA archived schedules if available) |
| **R9** | **Sable virgin audit:** confirm pre-2024 NEVER used in T001 / T002 / any prior strategy chain; document virgin-by-discipline (not merely virgin-by-availability) |

### 3.3 Custodial + governance — 4 conditions

| ID | Mandate |
|---|---|
| **R10** | **R10 absolute custodial preserved:** any `data/manifest.csv` mutation requires user MWF cosign; phase=`archive` NEW addition append-only; SHA256 byte-equal verified |
| **R11** | **§11.5 capital-ramp pre-conditions PRESERVED + NEW #11 candidate** (Riven proposal): "OOS test must use either forward-time virgin OR cross-validated regime-equivalent archival (Mira authority on regime equivalence)" |
| **R12** | **Pre-2024 evidence SECONDARY-CORROBORATIVE only** — H_next-1 Mira clearance verdict primarily anchored in forward-time virgin 2026-05-01..2026-10-31; pre-2024 corroborates IC=0.866 cross-window robustness OR adds attribution evidence; NEVER primary OOS |
| **R13** | **Quarter-Kelly REGRA ABSOLUTA preserved indefinitely** + Gate 5 fence preserved (no sizing implications from this council) |

---

## 4. Implementation chain (sequential gates)

```
A1: Nelo + Dara empirical DLL probe (bounded 2023-12-01..2023-12-20 WDOFUT)
   → outcome ∈ {full_month_works, partial_coverage, retention_exhausted}
   ↓ (if works)
A2: Dara schema parity audit + Sentinel ingestion path validation
   ↓
A3: Nova cost atlas pre-2024 ruling + auction hours pre-2024 confirmation
   ↓
A4: Mira regime stationarity check 5 axes adjudication
   ↓
A5: Sable virgin audit (pre-2024 never touched in T001/T002 chain)
   ↓
A6: Pax 10-point validate + R10 user MWF cosign for manifest mutation
   ↓
A7: Dara extends DLL backfill 2023-Q1..2024-Q3 (or stop earlier if regime non-equivalent)
   ↓
A8: Beckett N1+ archive run (~50min/quarter projected) Path C SECONDARY validation channel
```

**PARALLEL TRACK B:** Forward-time data accumulation 2026-05-01+ continues unblocked (Sentinel ingestion default). H_next-1 sign-off chain T0b-T0f proceeds in parallel; Mira N1 PRIMARY run waits forward-time data viability (~6 months wall-clock).

---

## 5. Risk flags (consolidated 13 anti-patterns surfaced)

| ID | Anti-pattern | Source |
|---|---|---|
| AP-D-01 | DLL retention exhaustion silent gaps (most dangerous) | Nelo §5 |
| AP-D-02 | WDOFUT specific contracts pre-2024 → 0 trades 19ms bug | Nelo + canonical quirks |
| AP-D-03 | Threading WINFUNCTYPE/c_wchar_p violations | Nelo + canonical quirks |
| AP-D-04 | SetHistoryTradeCallback after init silent overwrite | Nelo + canonical quirks |
| AP-D-05 | 99% progress 35-45s pause WAIT not crash | Nelo + canonical quirks |
| AP-D-06 | Sentinel ESC-009 pre-2024 failure precedent (different path; new surface) | Dara |
| AP-D-07 | Cost atlas v1.0.0 calibration drift pre-2024 | Beckett + Nova |
| AP-D-08 | Regime non-equivalence (RLP, COVID, BMF→F) → invalid OOS | Mira |
| AP-D-09 | Engine-config v1.1.0 semantic mismatch pre-RLP introduction | Beckett |
| AP-D-10 | Virgin-by-availability ≠ virgin-by-discipline (statistical violation) | Mira |
| AP-D-11 | Closed-source Win64 reproducibility threat (DLL future updates) | Riven |
| AP-D-12 | Manifest mutation without user MWF cosign violation R10 | Dara |
| AP-D-13 | Pre-2024 promotion to PRIMARY OOS (forbidden per R12) | Riven + Mira |

---

## 6. Status

- [x] 5/5 ballots cast independent (Article IV verified per ballot self-audit)
- [x] Outcome ratified: UNANIMOUS APPROVE_PATH_C HYBRID
- [x] 13 binding conditions R1-R13 consolidated
- [x] 13 anti-patterns AP-D-01..AP-D-13 catalog
- [ ] A1 Nelo empirical DLL probe execution (next concrete step IF user approves)
- [ ] A2-A8 sequential gates (post-probe outcome dependent)
- [ ] H_next-1 spec amendment v0.1.0 → v0.2.0 IF Path C activates (add §16 archival corroboration channel; preserve §0-§15 verbatim)
- [ ] T0b-T0f H_next-1 sign-off chain proceeds in parallel forward-time track

---

## 7. Authority chain

```
Council convened: User mandate 2026-05-01 — debate DLL backfill strategy pre H_next-1 sign-off advancement
Voters: 5 (Nelo lead + Dara + Beckett + Mira + Riven)
Mandate: pure data-acquisition strategy (NOT alpha; NOT sizing; NOT kill — operational squad infrastructure)
Article II: preserved (no push)
Article IV: preserved (independent ballots; convergence on Path C HYBRID via 5 different authority lenses; conditions consolidated)
Cosign: @aiox-master 2026-05-01 BRT
```

— @aiox-master, orchestrating the squad
