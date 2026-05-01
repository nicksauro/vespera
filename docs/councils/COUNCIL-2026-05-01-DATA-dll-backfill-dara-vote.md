---
council: DATA-COUNCIL-2026-05-01
topic: DLL backfill viability for pre-2024 WDO history (Path A) vs forward-only (Path B) vs both (Path C)
date_brt: 2026-05-01
voter: Dara (@data-engineer)
role: Data Engineer — Sentinel ingestion + parquet materialization + manifest custodial (R10) + coverage audit authority
branch: t003-data-acquisition-council
constraint_recap: |
  - User question: "DLL pode baixar dados WDO pré-2024?" — engineering feasibility + custodial governance
  - ESC-009 council 2026-04-27 closed: "2023-Q4 upstream unrecoverable per Dara coverage audit + user briefing" (refute via Sentinel chunk metadata + user verbatim "garanto que NÃO tem 2023, tem tipo uns 2 dias quebrados")
  - T002 thesis 2026-04-21: data_constraint_evidence cited "DB Sentinel sem 2023 contínuo" — already canonical in spec preregistration_revisions[0]
  - Sentinel TimescaleDB UP localhost:5433 (sentinel_db, sentinel_ro role); trades hypertable 56.5 GB / 570 chunks / range 2023-01-02..2026-04-02 UTC; only 6 sparse chunks in Jan 2023, zero Feb-Dec 2023, continuous 2024-01-02 onward
  - Manifest data/manifest.csv = 18 rows phase∈{warmup, in_sample}, hash-verified, no hold_out rows yet (per R10 custodial; phase=archive is NEW not yet defined in classify_phase)
  - Memory budget ADR-1 v3 6 GiB cap (lazy-load preserved per session)
  - Article II (Gage exclusive on push) + Article IV (no invention; trace to Sentinel SQL + manifest + ESC-009 ledger + user briefing)
  - This vote: doc-only artifact, no source mutation, no commit, no push
authority_basis:
  - Sentinel TimescaleDB sentinel_ro queries (chunk metadata 2023 sparse, 2024+ continuous)
  - data/manifest.csv (18 rows, byte-equal SHA256 invariant per R10)
  - docs/architecture/T002-data-coverage-audit-2026-04-27.md (Dara prior audit, ESC-009 trigger evidence)
  - ESC-009 council ledger (4/5 MAJORITY APPROVE_D1-SHIFTED; 2023-Q4 backfill INFEASIBLE upstream)
  - User briefing 2026-04-27 BRT (verbatim "NÃO tem 2023")
  - T002 spec v0.2.0+ preregistration_revisions[0].data_constraint_evidence
  - scripts/materialize_parquet.py::classify_phase (warmup | in_sample | hold_out — current vocab)
  - feedback_profitdll_quirks.md (Tiago/Nelo/etc canonical DLL semantics)
  - feedback_cpcv_dry_run_memory_protocol.md
non_pre_emption:
  - Vote does NOT bind Mira on regime-stationarity arbitration (microstructure 2023 vs 2026 = Mira authority)
  - Vote does NOT bind Nova on cost-atlas applicability pre-2024 (atlas v1.0.0 vs v0.x.x = Nova authority)
  - Vote does NOT amend manifest.csv or classify_phase (extension to phase=archive requires R10 absolute custodial → user cosign)
  - Vote does NOT pre-empt Sable virgin/audit verdict on pre-2024 territory
  - Vote does NOT authorize push (Article II → Gage @devops EXCLUSIVE)
  - Vote does NOT alter T002 holdout-lock (HOLDOUT_END_INCLUSIVE = 2026-04-21 unchanged)
  - Vote does NOT pre-empt Pax story scoping for Path A implementation epic
---

# DATA-COUNCIL-2026-05-01 — Dara Vote on DLL Pre-2024 Backfill Question

> **Author:** Dara (@data-engineer) — Data Engineer. Authority on Sentinel ingestion topology, parquet materialization pipeline, manifest custodial (R10), classify_phase semantics, and coverage audits. Author of `docs/architecture/T002-data-coverage-audit-2026-04-27.md` (ESC-009 evidence anchor).
> **Date (BRT):** 2026-05-01.
> **Branch:** `t003-data-acquisition-council`. Vote = doc-only artifact; no source mutation; no commit; no push.
> **Authority lens:** Empirical Sentinel coverage + parquet materialization mechanics + manifest custodial constraints + memory/disk budget. Engineering feasibility ranking under R10 absolute custodial gate, separating FACT (Sentinel chunk metadata + manifest hash invariant + DLL ingestion topology per Tiago/Nelo) from POLICY (user cosign required for phase=archive extension) from JUDGMENT (effort estimate, virgin-status implications).

---

## §1 Sentinel TimescaleDB retention reality (FACT layer)

### §1.1 Container topology — verified

| Property | Value | Source |
|---|---|---|
| Container | `sentinel-timescaledb` | docker ps (prior verification ESC-009 audit) |
| Host:Port | `localhost:5433` (sentinel_db, PG 16.11 + TimescaleDB) | sentinel_ro `current_user` 2026-04-27 22:45 BRT |
| Role (read) | `sentinel_ro` (default_transaction_read_only=on) | Beckett gap #16 closure; Dara audit |
| Hypertable | `trades` (56.5 GB, 570 chunks) + `features_1s` | timescaledb_information.hypertables |
| Chunk range | `range_start` ∈ [2023-01-02 UTC, 2026-04-02 UTC] | timescaledb_information.chunks |
| Schema (trades) | timestamp(BRT-naive), ticker, price, vol, qty, buy_agent, sell_agent, aggressor, trade_type, trade_number | INFORMATION_SCHEMA.columns; Dara audit §"Hypertable inventory" |

### §1.2 2023 evidence — REFUTES contiguous backfill claim

Spec `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` `preregistration_revisions[0].data_constraint_evidence` records canonical SQL evidence:

> "SQL: `SELECT MIN(range_start), MAX(range_end) FROM timescaledb_information.chunks WHERE hypertable_name='trades' AND range_start >= '2023-01-01' AND range_start < '2024-01-01'` -> **6 chunks total in Jan 2023, zero in Feb-Dec 2023; continuous from 2024-01-02**."

User briefing 2026-04-27 BRT (verbatim): "garanto que NÃO tem 2023, tem tipo uns 2 dias quebrados" — corroborates 6 sparse chunks (≈ "uns 2 dias" colloquial).

**Conclusion:** Sentinel-as-source for 2023 backfill is **INFEASIBLE upstream** (already adjudicated ESC-009; this is recall, not new evidence).

### §1.3 Pre-2024 ingestion attempt history

- T002 thesis 2026-04-21 (Quant Council ledger `docs/councils/VESPERA-DATA-PIPELINE-2026-04-21.md` ADDENDUM Turno 5 revision): "DB Sentinel sem 2023 contínuo" formally registered.
- ESC-009 council 2026-04-27 (resolution): "2023-Q4 upstream unrecoverable per Dara coverage audit + user briefing" — RATIFIED.
- No prior DLL-direct backfill attempt has been logged. Sentinel ingestion was always live-tape via TNewTradeCallback (Nelo path); historical replay via DLL `GetHistoryTrades`-class endpoint has **never been exercised** by this squad. This is a **new engineering surface**, not a retry of prior failure.

> **Distinction (load-bearing):** ESC-009 closed *Sentinel-as-source for 2023*. It did NOT close *DLL-as-source for pre-2024* — those are different ingestion paths. Whether the DLL itself can serve historical trades depends on DLL/broker retention policy (per `feedback_profitdll_quirks.md` canonical), not Sentinel chunk metadata.

---

## §2 Path A engineering — IF DLL can backfill (Nelo §3 plan)

If Nelo confirms DLL `GetHistoryTrades` (or equivalent) returns pre-2024 WDO ticks, the engineering pipeline is **mechanically straightforward** but custodially load-bearing.

### §2.1 Storage layout (Hive partitioning, parallel to existing)

```
data/
├── archive/                    # NEW phase=archive root
│   └── year=YYYY/
│       └── month=MM/
│           └── wdo-YYYY-MM.parquet
├── in_sample/                  # existing (warmup + in_sample phases)
│   └── year=2024.../
└── holdout/                    # existing (locked, untouched)
    └── year=2025.../
```

Partitioning scheme matches existing `data/in_sample/year=YYYY/month=MM/wdo-YYYY-MM.parquet` convention — pyarrow dataset discovery works without code changes for read-side; only `materialize_parquet.py` write-side classify_phase needs extension.

### §2.2 Manifest amendment — phase=archive (NEW phase)

Current `classify_phase` vocab: `warmup | in_sample | hold_out` (per `scripts/materialize_parquet.py`). Adding `archive` requires:

1. **Code change (Dara R&D):** extend `classify_phase` enum + boundary checks (archive = anything strictly before warmup_start_inclusive); add archive-aware path mapping in materializer.
2. **Manifest schema parity (R10):** existing 8 columns (path, rows, sha256, start_ts_brt, end_ts_brt, ticker, phase, generated_at_brt) — no schema mutation needed; `phase` column accepts new value. **Byte-equal SHA256 invariant per R10 absolute custodial preserved**.
3. **Manifest write — MWF gate:** every new row appended via Manifest Write Flag protocol. Per R10 absolute custodial, **phase=archive rows require user-cosign** (no autonomous append; mini-council MWF protocol governs each batch).
4. **Re-hash invariant test:** any row touching existing in_sample/warmup/holdout hashes is BLOCKED — archive append is **additive only**. Verifier test: `sha256(archive_row.sha256_bytes)` recomputed against parquet bytes; existing 18 rows unchanged.

### §2.3 Verification protocol (Sable audit ready)

For each pre-2024 month materialized:
- (a) DLL fetch → in-memory DataFrame (10 columns, BRT-naive timestamp).
- (b) Schema parity check vs reference month (e.g., 2024-01) — **MUST be 7-column trades schema or fail-closed** (see §3.4).
- (c) Write parquet with snappy compression, column order locked, dtypes locked.
- (d) Compute SHA256, append row to staging manifest.
- (e) Re-read parquet, verify row count + min/max timestamp + SHA256 byte-equal.
- (f) Diff against any prior parquet for same period (replay-safety): if exists, byte-equal; if mismatch, BLOCK and escalate.
- (g) MWF cosign request → user → Pax acknowledgment → Sable audit row → manifest commit.

### §2.4 Effort estimate (Dara engineering)

| Step | Owner | Effort (sessions) |
|---|---|---|
| DLL pre-2024 endpoint discovery + 1-day smoke test | Tiago/Nelo | 1 |
| Schema parity audit (sample 2023-08 vs 2024-08) | Dara | 1 |
| classify_phase extension + materializer R&D | Dara | 1-2 |
| Cost-atlas applicability research (delegate) | Nova | 1 (parallel) |
| Regime-stationarity gate (delegate) | Mira | 1 (parallel) |
| Full backfill materialization (e.g., 2022-01 → 2023-12) | Dara + Tiago | 1-2 (depending on DLL throughput) |
| Sable audit + virgin certification | Sable | 1 |
| Pax story scoping + MWF cosign coordination | Pax | 1 |
| Gage push gate (post all approvals) | Gage | 0.5 |
| **Total** | **squad** | **~5-10 sessions** (parallelizable across Dara/Nova/Mira/Sable) |

**Bottleneck:** DLL throughput (broker-side rate limits per `feedback_profitdll_quirks.md`) and MWF cosign cadence — not parquet-side mechanics. Engineering is **boring** in the good sense.

---

## §3 Pre-2024 data quality concerns (CAVEAT layer)

Even IF DLL delivers pre-2024 ticks, four data-quality fault lines exist. Each is a **gating concern**, not a vetoer — mitigation is delegation to the relevant authority.

### §3.1 B3 microstructure regime drift

- RLP rules (Retail Liquidity Provider) **changed structurally** between 2023 and 2024 (per Nova T002.6 spec §1 — RLP detection historic-gap argument). Pre-2024 trade_type semantics may not align with current Nelo enum mapping.
- Fee structure — exchange fees R$ 1.23/contract one-way (`day_trade` regime, atlas v1.0.0) — Nova authority required to confirm fees were identical 2022-2023.
- **Delegation:** Nova @market-microstructure for definitive ruling. Dara cannot adjudicate microstructure semantics.

### §3.2 Auction hours 2023 vs current

- B3 opening auction (09:00-09:30 BRT) and closing call windows had at least one schedule revision in the 2023-2024 window (DST transitions + B3 communiqué amendments).
- Cross-verify against Nova session-phases atlas (rev pós-DST 2026-03-09) and `config/calendar/2024-2027.yaml` — **calendar pre-2024 NOT covered** by current YAML (rev only goes 2024-2027).
- **Delegation:** Nova confirmation 2026-05-01 + calendar extension to 2022-2023 (joint Nova + human + Sable cosign per ESC-012 calendar custodial).

### §3.3 Cost atlas applicability

- `nova-cost-atlas.yaml v1.0.0` SHA-locked (`bbe1ddf7…`) — declared valid for current regime. Validity pre-2024 is **unverified**.
- Two paths:
  - (i) Atlas v1.0.0 holds back-compatibly → use as-is for archive runs.
  - (ii) Separate `atlas v0.x.x` (archive-only) declared for the 2022-2023 fee/RLP regime — keeps v1.0.0 immutable, adds explicit archive variant.
- Path (ii) is custodially cleaner (atlas immutability per ESC-012 invariant); path (i) is operationally simpler but requires Nova affirmative ruling.
- **Delegation:** Nova @market-microstructure SOLE authority. Dara records the variant once Nova rules.

### §3.4 Schema parity (Dara native authority)

The 7-column trade schema (timestamp, price, qty, aggressor, buy_agent, sell_agent, trade_type) — does pre-2024 DLL output match byte-for-byte?

- `trade_type` enum: 14 values per Nelo trade-types semantic atlas. Pre-2024 may have fewer / different / re-numbered values.
- `aggressor` field: BUY/SELL/NONE per current parquet. Pre-2024 may have only 2 values or different sentinel for ambiguous fills.
- `buy_agent`/`sell_agent` (broker codes): retention policy at broker may anonymize older rows or return NULL.

**Dara engineering rule:** schema mismatch → fail-closed, NO heuristic remap. Either DLL returns the canonical 7-column shape or Path A is BLOCKED on schema-incompatibility (and Sentinel/parquet pipeline cannot ingest).

**This is the only §3 concern Dara adjudicates directly** — items §3.1-§3.3 delegate to Nova/Mira.

---

## §4 Storage + memory budget (FACT layer, Dara native)

### §4.1 Disk

| Metric | Value | Notes |
|---|---|---|
| WDO 1 year throughput | ~100M trades / ~1.5 GB parquet (snappy) | Empirical from existing manifest (12-month in_sample = 222.0M rows, ~3.3 GB pre-compression) |
| 2 years pre-2024 (2022 + 2023) | ~3 GB additional disk | Linear extrapolation; B3 volume 2022-2023 lower than 2024-2026 (conservative upper bound) |
| Current `data/` total | ~5 GB (warmup + in_sample + holdout sparse) | Manifest 18 rows × ~3.3 GB / 12 ≈ 5 GB |
| Post-Path A `data/` | ~8 GB | Well within OS-side budget (no constraint) |

**Verdict (disk):** OK. No infrastructure escalation needed.

### §4.2 Memory (ADR-1 v3 hard cap 6 GiB per session)

- Lazy-load preserved: pyarrow dataset reads **only requested partition** per session. Adding archive does NOT increase peak RSS — backtests opt-in via `phase∈{archive}` filter or stay at `phase∈{warmup, in_sample}`.
- N6 evidence (Beckett 2026-04-29): peak RSS 0.158 GiB Python / 0.597 GiB OS-WS for 5-trial CPCV — well under 6 GiB cap. Archive partition does not stress this.
- **Caveat:** if a future strategy reads ALL phases simultaneously (warmup + in_sample + archive), peak RSS grows. Mira/Beckett gate any such cross-phase strategy through warmup-orchestrator review.

**Verdict (memory):** OK under lazy-load discipline. ADR-1 v3 cap NOT threatened.

---

## §5 Virgin status (Sable audit territory)

### §5.1 Pre-2024 in T002 — never used

T002 thesis (per ESC-012 Round 3.1 ledger + spec v0.2.x):
- Warmup (4-fold + 6 buffer) = `2024-01-02 → 2024-08-22` (warmup_end_exclusive = 2024-08-22).
- In-sample CPCV = `2024-08-22 → 2025-06-30` (10-month ≈ 224 valid bd).
- Holdout-virgin = `2025-07-01 → 2026-04-21` (HOLDOUT_END_INCLUSIVE locked).

No T002 fold, train, validate, holdout, or warmup window touches **any pre-2024 row**. Therefore **pre-2024 IS virgin per spec §0 falsifiability discipline** at the data-touch layer.

### §5.2 Caveat — virgin ≠ usable

Virgin status is **necessary but not sufficient**:
- Mira authority on regime-stationarity — is 2022-2023 microstructure regime statistically equivalent to 2024-2026 regime? If NOT, archive data fails the IID-ish assumption that backtest/CPCV machinery presumes (even if it never leaks into holdout, training on out-of-regime data is methodologically suspect).
- Sable authority on virgin-territory certification — once pre-2024 is materialized, it transitions from "virgin (never observed)" to "virgin-and-untouched (observed but not used in any strategy)". Subsequent strategy may consume it as in-sample, but only ONCE — re-use violates run-once-per-as_of (ESC-006 principle).
- Pax authority on story-level scoping — which T002.x or Hₙₑₓₜ story actually consumes archive? Not Dara's call.

**Dara position:** virgin at data-layer ✅; usability gated by Mira (regime) + Sable (custodial) + Pax (scoping).

---

## §6 Recommendation — Dara authoritative vote

### §6.1 Verdict

**APPROVE_PATH_C_BOTH** (with explicit decomposition + delegations)

- **Path B (forward-only) ratified unconditionally.** Live ingestion via Sentinel + Nelo TNewTradeCallback continues; manifest grows daily under MWF protocol; no engineering surface change. This is the steady-state and the **cheapest path to T002.x / Hₙₑₓₜ unblock** if the squad chooses to defer Path A.
- **Path A (DLL pre-2024 backfill) APPROVED CONDITIONAL** on three sequenced gates:
  1. **Gate A1 (Nelo/Tiago smoke test, ~1 session):** confirm DLL endpoint actually returns pre-2024 ticks (not 0-row, not error, not synthetic placeholder). If FAIL → Path A becomes infeasible upstream, Path B remains (vote degrades to APPROVE_PATH_B_FORWARD_ONLY). This gate is **load-bearing** and must execute first.
  2. **Gate A2 (Dara schema parity audit, ~1 session, parallel):** sample 2023-08 vs 2024-08 (1 day each); 7-column shape match + trade_type enum subset + aggressor enum subset; fail-closed on mismatch.
  3. **Gate A3 (Nova + Mira ratification, parallel):** Nova rules cost-atlas variant (v1.0.0 holds OR atlas v0.x.x archive-variant); Mira rules regime-stationarity (block if non-stationary). If both PASS → proceed to materialization + MWF cosign cadence.

If Gate A1 PASSES + Gate A2 PASSES + Gate A3 PASSES → materialization proceeds session-by-session under user MWF cosign; Sable audits; Gage pushes per Article II.

### §6.2 Why C and not A-only or B-only

- **Not A-only:** if Gate A1 fails (DLL has no pre-2024 retention at the broker) the squad still needs forward-only operational continuity — Path B is the floor and never blocks.
- **Not B-only:** pre-2024 is a **scarce, virgin, plausibly-useful resource**. Refusing to even ask the DLL is a policy choice the human author should make, not Dara unilaterally. Engineering says "feasible if upstream cooperates"; the cosign chain (R10 absolute custodial + Pax scoping + Sable virgin certification + Mira regime + Nova atlas) is exactly the mechanism designed to make this kind of decision safely.
- **Path C (both):** preserves operational continuity (B unconditional) and opens the optional R&D track (A conditional on three gates), with engineering, governance, and quality fault lines explicitly named and delegated.

### §6.3 Sentinel TimescaleDB also can ingest from DLL output (alternative store)

Engineering note (not a vote alteration): if Path A executes, the materialized parquets can ALSO be back-fed into Sentinel TimescaleDB via `COPY trades FROM …` for archive chunks. This is **optional**, not required. Trade-off:
- (+) Sentinel becomes single source of truth across all eras (operationally cleaner; future strategies can SQL-query archive + live uniformly).
- (−) Doubles storage (Sentinel ~3 GB additional + parquet ~3 GB additional); requires Tiago/Nelo Sentinel-side write privilege gate.
- (=) Pure parquet-side archive is sufficient for backtest consumers (Beckett path).

Dara recommendation: **parquet-only first**; Sentinel back-feed deferred to a separate council if a multi-era SQL query path materializes as a need.

---

## §7 Article IV self-audit (No Invention)

Every load-bearing claim in this vote traces to a source:

| Claim | Source |
|---|---|
| Sentinel container UP localhost:5433, sentinel_ro role | Dara coverage audit `docs/architecture/T002-data-coverage-audit-2026-04-27.md` §"Connection authority" + sentinel_ro `current_user` 2026-04-27 22:45 BRT |
| trades hypertable 56.5 GB / 570 chunks / 2023-01-02..2026-04-02 UTC | timescaledb_information.{hypertables, chunks} probe (Dara audit §"Hypertable inventory") |
| 2023 has 6 sparse chunks Jan-only, zero Feb-Dec | Spec `data_constraint_evidence` SQL evidence + user briefing 2026-04-27 |
| ESC-009 council closed 2023-Q4 upstream-unrecoverable | `docs/councils/COUNCIL-2026-04-27-ESC-009-AC8-amendment.md` (4/5 MAJORITY APPROVE_D1-SHIFTED) |
| T002 thesis 2026-04-21 cited "DB Sentinel sem 2023 contínuo" | Spec `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` preregistration_revisions[0] |
| Manifest 18 rows, 8 columns, byte-equal SHA256 invariant per R10 | `data/manifest.csv` direct read; R10 Manifest Custodial protocol |
| classify_phase vocab = warmup | in_sample | hold_out | `scripts/materialize_parquet.py::classify_phase` |
| Memory cap 6 GiB ADR-1 v3 | ADR-1 v3 ledger; N6 peak RSS evidence (Beckett 2026-04-29 N6 report §wall-time + RSS table) |
| WDO ~1.5 GB parquet/year | Manifest empirical (222.0M rows / 12 months / ~3.3 GB pre-compression for in_sample) |
| RLP detection historic gap, cost atlas v1.0.0 SHA `bbe1ddf7…` | T002.6 Nova spec v1.0.0 §1.2-1.3 + Nova atlas SHA-lock |
| Holdout-lock HOLDOUT_END_INCLUSIVE = 2026-04-21 | `_holdout_lock.py` constant |
| feedback_profitdll_quirks.md canonical Tiago/Nelo | Project memory @import |
| Article II Gage exclusive on push | Constitution Article II + agent-authority.md delegation matrix |

**No invented features.** No claim asserted without source. Every delegation in §6 names the authority.

---

## §8 Dara cosign 2026-05-01 BRT

Cosign — Dara @data-engineer — Data Acquisition Council ballot — 2026-05-01 BRT.

Vote: **APPROVE_PATH_C_BOTH** (Path B unconditional + Path A conditional on Gate A1 [Nelo DLL smoke test] AND Gate A2 [Dara schema parity] AND Gate A3 [Nova cost-atlas + Mira regime]).

Engineering effort estimate (if all gates pass): ~5-10 sessions across Dara/Nova/Mira/Sable/Pax/Gage; Dara solo budget ~3-4 sessions (classify_phase R&D + schema audit + materialization + manifest custodial cadence).

Article II preserved (no push). Article IV preserved (no invention). R10 absolute custodial preserved (manifest mutation via MWF user-cosign protocol only).

Branch `t003-data-acquisition-council`. No commit. No push. Doc-only artifact.

—Dara
