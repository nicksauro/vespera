# Aria (@architect) — Ballot — Council 2026-05-03 Schema Resolution

**Vote:** **Option A** (preserve 10-col storage, project + cast at consumption)
**R16:** **CONCUR** — elevate to first-class architectural rule.

---

## §1 Architectural reasoning

### 1.1 Projection-time vs storage-time normalization (Concern #1)

Consumption-time projection is **architecturally cleaner**, full stop. Storage-time normalization couples the custodial layer to the current consumer's needs — every future consumer pivot then forces either a re-ingestion (Option C cost) or a lossy rebuild from the lossy-stored copy (irreversible). Projection-time normalization is the canonical CQRS / medallion-bronze-to-silver pattern: bronze is immutable raw, silver is task-shaped. Options A/B/D respect this boundary. Option C respects it too but pays the cost twice (re-download + re-validate) for a problem we already have a non-destructive answer to.

### 1.2 10-col (2023) vs 7-col (2024) split (Concern #2)

This is **NOT a temporary compromise — it is the canonical state going forward** under R16. The 2024 Sentinel pipeline happens to project to 7-col at ingestion (legacy decision pre-R16). The correct read is: 2023 storage is *more faithful* than 2024 storage; the architectural debt sits on the **2024 side**, not 2023. Forward direction (post-R16): Sentinel ingestion should also preserve raw 10-col and project to 7-col only at consumption. A2 audit findings F1/F2/F3/F4/F5 then dissolve into a projection layer, not a schema migration.

### 1.3 R16 as first-class principle (Concern #3)

CONCUR. R16 is **not data-engineering-specific** — it is a custodial-vs-consumer architectural boundary that applies to ANY raw capture (DLL ticks today; order book snapshots, news feed, alt-data tomorrow). Sits naturally alongside R5 (parity), R6 (cost atlas), R10 (custodial). I'd add one architectural clarification to R16 wording: *"Storage is the registry-of-record; projection is a versioned, replayable consumer-side view."* — this makes it explicit that projections are themselves first-class artifacts (versioned, testable, reversible), not ad-hoc casts.

### 1.4 Option C cost-vs-debt (Concern #4)

Re-download is operationally costly **and architecturally redundant** given R16. C only wins if we believe DLL `TranslateTrade` strings are semantically richer than int64+map. They aren't — they're a convenience projection of the same underlying B3 broker registry. Paying ~6h25 + new DLL session to bake a projection into storage is exactly the anti-pattern R16 forbids.

### 1.5 Future-proofing across thesis pivots (Concern #5)

Option A wins. 10-col storage + projection layer means: technical-pure thesis projects to 7-col canonical; flow-based thesis projects to 10-col + post-hoc broker map (Option B becomes a *projection*, not a *re-ingest*); microstructure thesis projects to ts_raw-preserving view. Schema does not gate thesis. Option D is A-minus-projection-discipline (acceptable fallback if Dara capacity blocks A); Option B prematurely binds to flow thesis; Option C prematurely binds to broker-string thesis.

## §2 Verdict

**A + R16 CONCUR.** Architectural integrity preserved, optionality maximized, cost minimized, debt zero.

— Aria
