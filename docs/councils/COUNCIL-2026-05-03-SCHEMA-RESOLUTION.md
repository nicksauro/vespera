# Council 2026-05-03 — T003.A2 Schema Resolution + Information Preservation Principle — **RATIFIED OPTION D + R16** (10/10 R16 UNANIMOUS + user MWF tiebreaker D)

> **Date (BRT):** 2026-05-03
> **Trigger:** Dara A2 audit verdict `A2_FAIL_BLOCK_BULK` + user pushback on column-drop + user observation that agent IDs int64 (2023) vs string (2024) is `TranslateTrade` ON/OFF asymmetry between Sentinel ingestion and backfill, NOT a true canonical drift
> **Authority basis:** Council 2026-05-01 R5 (schema parity) + R6 (cost atlas pre-2024) + R10 (custodial); Council 2026-05-03 R1 Amendment (RATIFIED 6/6 + user MWF) bulk window
> **Article II preserved:** No push during deliberation
> **Article IV preserved:** Independent ballot self-audits
> **Author:** @aiox-master orchestration capacity, autonomous mode

---

## §1 The single question

**What to do with the schema mismatch between 2023 backfill (10-col rich + int64 agents) and 2024-01 Sentinel canonical (7-col + string agents), given that H_next-1 thesis is NOT YET FIXED (still in draft by Mira)?**

### §1.1 Empirical state (Dara A2 findings)

| Issue | Severity | Root cause |
|---|---|---|
| F1 cols 10 vs 7 | CRITICAL | Backfill probe captures Q-AMB-02 fidelity (`ts_raw`, `vol_brl`, `trade_number`) — INFORMATION ENRICHMENT, not drift |
| F2 agents int64 vs string | CRITICAL | **`TranslateTrade` ON in Sentinel 2024 ingestion, OFF in backfill 2023** — translation asymmetry, NOT semantic drift |
| F3 timestamp us vs ns | HIGH | Lossless cast required |
| F4 qty int64 vs int32 | HIGH | Width cast (validate no overflow) |
| F5 nullable True vs False | MEDIUM | Cast + assert |
| F8 (carry-forward) | INFO | 2023-03-15 first 1000 NONE = auction window, regime-axis (A4-Mira) |

### §1.2 What's at stake

- **A3-Nova / A4-Mira / A5-Sable downstream chain** is GATED by A2 verdict.
- **H_next-1 thesis NOT YET FIXED** — Mira drafting (Sable D-01 register). Could be technical-pure OR flow-based.
- **Information preservation principle** newly instituted by user 2026-05-03: *"never destroy raw fields at storage time; project at consumption"*.

---

## §2 Four options on the table

### Option A — Defensive minimum (preserve storage, project + cast naive at consumption)

- Storage on D:\ stays 10-col (preserves `ts_raw`/`vol_brl`/`trade_number` + int64 agents)
- A3-Nova ingestion projects 7-col canonical view + casts: `ts[us]→ns`, `qty int64→int32`, `agents int64→string` (zero-pad like `"00308"`)
- **No re-download. No translate-table lookup. Fast.**
- **Cost:** ~4-6h Dara
- **Bet:** H_next-1 will be technical-pure; agent identity not load-bearing
- **Risk:** if H_next-1 turns flow-based later, broker info is stuck as zero-padded numeric IDs (NOT real broker names)

### Option B — Build translate-map post-hoc

- Nelo extracts agent code → broker-name mapping from DLL (call `TranslateTrade` on a small sample) OR from B3 official table
- Dara post-hoc joins mapping at ingestion: int64 ID → real broker string ("BTG", "XP", "ITAU"...)
- Storage stays 10-col + new `agent_translation_map.json` lookup committed
- **Cost:** ~2-4h Nelo + 2-4h Dara
- **Bet:** preserve optionality; H_next-1 might need brokers
- **Risk:** non-stationarity (broker behavior 2023 ≠ 2024 — XP grew 5x, BTG mudou estratégia, mergers happened); naming changes; mapping completeness uncertain

### Option C — Re-download with `TranslateTrade` ON

- Re-run full bulk 50 chunks with `TranslateTrade` enabled in DLL init
- Native string broker names from DLL itself (canonical Nelogica source)
- **Cost:** ~6h25 wall-time + new DLL credentials session + Dara verify
- **Bet:** H_next-1 will definitely need brokers
- **Risk:** large investment without thesis confirming need; quarantines current 50 chunks (or merges later)

### Option D — Defer decision (technical-pure path now, broker question revisited)

- Cast agents `int64`→`int32` (data-preserving, no fake string encoding)
- Storage stays 10-col untouched
- A3-Nova / A4-Mira / A5-Sable proceed on TECHNICAL features only (no broker conditioning)
- IF/WHEN a future strategy needs broker identity → reconvene mini-council, then choose B or C
- **Cost:** ~2h Dara (just type cast)
- **Bet:** thesis-decides-schema, not schema-decides-thesis
- **Risk:** if technical-only strategies underperform, we eventually pay re-download cost anyway

---

## §3 Principle for ratification (R16 candidate)

**R16 (NEW, 2026-05-03):** *"Information preservation by default. Raw fields captured by canonical pipelines are NEVER dropped at storage time. Type/schema normalization happens at consumption boundary (projection + cast), preserving original parquet/manifest/registry-of-record. Reversal of preservation requires explicit Council ratification + Sable [DIVERGENCE] register entry. Storage is custodial; projection is consumer-side concern."*

This principle is CONSEQUENCE of the schema discussion but applies broader (any future data acquisition).

---

## §4 Vote section (10 voters + user MWF cosign)

Each voter files at `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION-{voter}-vote.md`.

| Voter | Authority lens | Vote (A/B/C/D) | R16 (concur/reject) | Ballot |
|---|---|---|---|---|
| Kira (@quant-researcher) | Strategic thesis fitness | **D** | CONCUR | `kira-vote.md` |
| Beckett (@backtester) | Consumer feature requirements | **A** + VETO_B | CONCUR | `beckett-vote.md` |
| Nelo (@profitdll-specialist) | DLL feasibility (translate-map) | **D** + STRONG_NO_C | CONCUR | `nelo-vote.md` |
| Nova (@market-microstructure) | Broker identity microstructural value | **D** | CONCUR | `nova-vote.md` |
| Mira (@ml-researcher) | Stationarity + multiple-testing | **D** | CONCUR | `mira-vote.md` |
| Riven (@risk-manager) | Cost-benefit + custodial | **D** (Bayesian 0.60) | CONCUR | `riven-vote.md` |
| Dara (@data-engineer) | Engineering effort + execution | **A** | CONCUR | `dara-vote.md` |
| Aria (@architect) | Architectural integrity | **A** | CONCUR | `aria-vote.md` |
| Pax (@po) | Story-locus adjudication | **A** | CONCUR | `pax-vote.md` |
| Sable (@squad-auditor) | Governance + Article IV cross-validation | **A** + 4 conditions | CONCUR + 4 conditions | `sable-vote.md` |
| **User MWF cosign** | R10 absolute authority | **D** (tiebreaker 5-5) | CONCUR | inline §6 |

**Result:** Squad split 5A/5D, B=0 (3 VETOs incl. Beckett+Mira+Sable Article IV violation), C=0 (Nelo STRONG_NO + Riven Bayesian 0.06 + Mira α-wasteful). User MWF tiebreaker resolves to **D** per thesis-decides-schema principle (H_next-1 v0.1.0 Draft confirmed technical-pure by Mira+Kira spec read; +2h Option A buys nothing for current thesis). **R16 RATIFIED** 10/10 unanimous CONCUR + user MWF cosign.

---

## §5 Outcome routing

| Convergence | Next |
|---|---|
| Option A wins + R16 ratified | T003.A4 story (Dara) — projection + naive cast — ~4-6h impl, then A3 dispatch |
| Option B wins + R16 ratified | T003.A4 + T003.A5 (Nelo translate-map + Dara remap) — ~6-10h impl, then A3 |
| Option C wins | T003.A2 re-execution with new R1' bound (re-download); ~6h25 bulk + ~10h validation cycle |
| Option D wins + R16 ratified | T003.A4 minimal cast (~2h Dara), proceed A3/A4 on technical-only; broker question parked until thesis demands |

---

## §6 Ratification + user MWF cosign

**Date BRT:** 2026-05-03
**User decision:** **Option D** (defer broker question; minimal int cast; technical-pure A3/A4 path) + **R16 CONCUR** with Sable's 4 conditions.
**Authority basis:** R10 absolute custodial — user is supreme MWF cosign holder; tiebreaker 5A/5D resolved D per thesis-decides-schema discipline.
**Cosign signature:** filed inline `2026-05-03 user MWF cosign — RATIFY OPTION D + R16 UNANIMOUS CONCUR + Sable C1-C4 conditions`.

### §6.1 Sable's 4 conditions on R16 (binding)

- **C1:** R16 text clarifier *"does NOT relax R10 byte-equal nor Gate-5 lock"* — appended to R16 wording §3.
- **C2:** D-02 [DIVERGENCE] register filed post-ratification (Sable owns) — documents Backfill-2023 vs Sentinel-2024 schema split as accepted divergence (parallel to D-01 H_next-1 register).
- **C3:** projection versioning consumer-side — A3-Nova ingestion implements `dataset_hash + projection_semver` so backtests reproduce byte-exact regardless of which projection used.
- **C4:** **7-day council moratorium** — no new councils/amendments through 2026-05-10 unless user-escalated. Riven debt-curve curve disclosure already supports this.

### §6.2 R16 final wording (post-C1 amendment)

> **R16 (RATIFIED 2026-05-03):** *"Information preservation by default. Raw fields captured by canonical pipelines are NEVER dropped at storage time. Type/schema normalization happens at consumption boundary (projection + cast), preserving original parquet/manifest/registry-of-record. Reversal of preservation requires explicit Council ratification + Sable [DIVERGENCE] register entry. Storage is custodial; projection is consumer-side concern. **R16 does NOT relax R10 byte-equal nor Gate-5 lock — both remain absolute.**"*

### §6.3 Anti-Article-IV Guards 1-8 + new R16 impact

Confirmed independently by Sable, Mira, Aria, Riven: **0/8 guards affected** by R16 ratification. R16 elevates information-preservation to first-class principle without relaxing existing R-clauses.

### §6.4 Article II + IV preservation

- Article II: PR #22 + #23 already merged via @devops Gage. Future R16 work on T003.A4 follows default Gage-exclusive push discipline.
- Article IV: every claim in this resolution traces to 10 ballots + Dara A2 audit + Nelo manual citations + Beckett feed_parquet code anchor + Mira H_next-1 spec read.

### §6.5 Implementation routing post-ratification

Per §5 Outcome routing — Option D wins:

1. **T003.A4 minimal-cast story** (Pax adjudication): drafted by Pax post-ratification; Dara owns; ~2.5h impl
   - Cast `timestamp[us]→ns` (lossless)
   - Cast `qty int64→int32` (validate no overflow first)
   - Cast `nullable=True→False` (assert no nulls)
   - **Keep `buy_agent`/`sell_agent` int64** (NO zero-pad string projection — F2 accepted as documented divergence)
   - Drop manifest header `v1` → `v1.1` cosmetic update
   - Document F2 in T003.A4 README as accepted-by-Council-2026-05-03
2. **A2 re-audit** (Dara) post-T003.A4 implementation: confirms parity at projection layer with F2 carry-forward
3. **A3-Nova dispatch** post-A2 PASS: cost atlas pre-2024 ruling + auction hours pre-2024 (Council 2026-05-01 R6+R8)
4. **A4-Mira dispatch** parallel-with-A3 (per Mira C2): regime stationarity 5 axes + F8 (2023-03-15 aggressor) carry-forward; α-correction BH-FDR q=0.10 pre-registered
5. **A5-Sable substantive virgin audit** post-A4
6. **A6-Pax 10-point + R10 user MWF cosign** post-A5
7. **A7-Dara manifest extension** post-A6 cosign
8. **A8-Beckett N1+ archive run** post-A7

### §6.6 D-02 register entry (Sable to file)

Schema divergence: Backfill 2023 (10-col rich + int agents) vs Sentinel 2024 canonical (7-col + string agents) — accepted by Council 2026-05-03 Option D + R16 ratification. Reversal requires Council per R16. Anti-Article-IV Guard #9 candidate (information preservation principle).

### §6.7 7-day moratorium (Sable C4)

No new councils or amendments through **2026-05-10** unless user-escalated. Squad continues operational A3/A4/A5/A6/A7/A8 chain execution per existing ratifications. Routine work proceeds; new governance topics queue.

---

**Status:** **`RATIFIED_SCHEMA_RESOLUTION_OPTION_D_R16_2026_05_03`**.
