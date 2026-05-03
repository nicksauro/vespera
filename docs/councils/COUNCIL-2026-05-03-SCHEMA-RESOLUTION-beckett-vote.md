# Beckett ballot — Council 2026-05-03 Schema Resolution + R16

> **Voter:** Beckett (@backtester)
> **Authority lens:** Consumer feature requirements — what the simulator/backtester needs to ingest 50 chunks of 2023 data fairly and reproducibly.
> **Date:** 2026-05-03 BRT
> **Article IV self-audit:** independent ballot. No prior coordination read.

---

## §1 Vote

**Option:** **A** (defensive minimum: preserve 10-col storage; project + naive cast at consumption)
**R16:** **CONCUR** (information preservation by default — strong)

---

## §2 Specific concerns answered

### §2.1 Current ingestion path — does it expect string agents?

**No.** Empirical check: `packages/t002_eod_unwind/adapters/feed_parquet.py` line 236 documents *"Reads only (timestamp, price, qty) — aggressor/agents are NOT loaded, non-load-bearing per Beckett."* T002 cohort is **agent-blind**. CPCV harness consumes `(ts, price, qty)` only. Casting agents int64→string at projection layer is **zero-impact for current backtester**; T003 onward decides whether to load the column.

### §2.2 Order-flow features in roadmap requiring broker conditioning?

**Not in current Beckett scope.** Slippage model (Roll), aggressor-pressure proxy (`qty_buy − qty_sell`), and OFI proxy use **`aggressor` enum (BUY/SELL/NONE)**, not broker identity. Smart-money / toxicity / cross-trade detection are **Nova/Kira aspirations**, not backtester features today. If H_next-1 ends technical-pure, broker identity stays cosmetic for me.

### §2.3 CPCV / purged k-fold integrity under Option B?

**This is the showstopper for B.** Building a translate-map post-hoc using **2024+ broker behavior** to interpret 2023 IDs imports future-state information into past labels. Even if the mapping is "static B3 codes," **broker behavior is non-stationary** (XP scale change, mergers, strategy shifts). Any CPCV path that trains on a feature derived from such a mapping has a **hidden look-ahead** — feature semantics in t depend on knowledge crystallized at t+future. PBO/DSR estimates would be optimistically biased without anyone seeing why. **I veto B on integrity grounds** unless Mira pre-commits to NOT using broker-conditioned features in any model crossing the 2023↔2024 boundary, AND Sable registers a [DIVERGENCE].

### §2.4 R16 implications for simulator state machines?

**Strongly aligned with my reproducibility doctrine.** Storage = custodial, projection = consumer concern is exactly the boundary I want: dataset hash on the 10-col rich parquet, simulator-version pins the projection function. If a future model needs `ts_raw` (microsecond) or `vol_brl` for impact calibration, the field is already there — no re-acquisition, no quarantine. R16 also matches Beckett's *"backtest non-reproducible is garbage"* axiom: preserving raw fields makes replays bit-faithful even when projection logic evolves.

---

## §3 Why not C or D

- **C (re-download with TranslateTrade ON):** ~6h25 wall-time + DLL session cost without thesis demanding broker strings. Premature investment. Also risks merging two acquisition regimes into one parquet set — provenance ambiguity.
- **D (technical-only, defer):** acceptable but weaker than A. D casts agents int32 (loses zero-pad string convention parity with 2024); A keeps the door open at trivial extra cost. A dominates D.

---

## §4 Caveats / conditions on A

1. Projection function MUST be versioned (semver) + included in dataset/spec hash.
2. Zero-pad encoding MUST be documented as **synthetic** (not real broker name) — Sable [DIVERGENCE] register entry.
3. If Mira's H_next-1 thesis turns flow-based, reconvene mini-council; A→C upgrade path still open since storage preserves int64 originals.

---

**Vote:** **A** + **R16 CONCUR**.

— Beckett, reencenando o passado 🎞️
