# `dll_backfill_projection.py` — Consumer-side projection (T003.A4)

> **Authority:** Council 2026-05-03 SCHEMA-RESOLUTION (RATIFIED Option D + R16).
> **Story:** [T003.A4 minimal-cast projection](../docs/stories/t003.a4.minimal-cast-projection.story.md).
> **Owner:** Dara (@data-engineer).
> **Status:** Implementation 2026-05-03 (this README cosigned with module).

---

## What this module does

Storage at `D:\Algotrader\dll-backfill\` is the **custodial 10-column rich
artifact** captured by the canonical DLL probe:

```
timestamp[us], ts_raw[string], ticker, price, qty[int64], aggressor,
buy_agent[int64], sell_agent[int64], vol_brl, trade_number
```

Sentinel 2024 canonical at `data/in_sample/year=2024/month=01/wdo-2024-01.parquet`
is the **7-column projected** view consumers expect:

```
timestamp[ns] non-null, ticker non-null, price non-null, qty[int32] non-null,
aggressor non-null, buy_agent[string] nullable, sell_agent[string] nullable
```

This module bridges the two **at consumption time only** — storage is never
mutated (R16 + R10 + Gate 5 absolute).

| AC | Cast / behavior | Direction |
|---|---|---|
| AC1 | `timestamp[us] -> timestamp[ns]` | lossless upcast |
| AC2 | `qty int64 -> int32` | bounds-asserted, fail-closed if overflow |
| AC3 | `nullable=True -> False` | assert-then-mark for 5 mandated cols |
| AC4 | `buy_agent / sell_agent` int64 PRESERVED | F2 ACCEPTED DIVERGENCE — see below |
| AC5 | manifest header `v1 -> v1.1` | cosmetic, off-repo backfill manifest only |
| AC6 | `PROJECTION_SEMVER` + `compute_dataset_hash()` | Sable C3 cache key tuple |
| AC7 | `reaudit_at_projection_boundary()` | A2 re-audit verdict generator |

---

## F2 — ACCEPTED DIVERGENCE (`buy_agent` / `sell_agent` stay int64)

**Backfill 2023 emits int64 broker agent IDs from the DLL `TranslateTrade`
callback. Sentinel 2024 canonical encodes them as zero-padded string. This is
a documented schema split — NOT a defect.**

The split is formally accepted by Council 2026-05-03 §6.5 (Option D + R16,
ratified 5-5 with user MWF tiebreaker D + R16 unanimous CONCUR 10/10). The
module **DOES NOT** zero-pad and **DOES NOT** coerce to string — both
explicitly REJECTED by:

- **Beckett ballot** — VETO_B (consumer feature requirements: zero-pad fakes
  brokerage identity that the strategy chain doesn't actually need)
- **Riven ballot** — Bayesian posterior 0.06 against zero-pad (cost-benefit)
- **Mira ballot** — α-wasteful (multiple-testing cost without thesis demand)
- **Nelo ballot** — STRONG_NO_C (DLL `TranslateTrade` ON re-download deferred)

### Reversal protocol (per R16 reversal-clause)

If a future H_next thesis demands real broker name conditioning:

1. Mini-Council convened (Beckett + Mira + Riven + Nelo + Dara minimum).
2. New `[DIVERGENCE]` register entry filed by Sable amending D-02.
3. `PROJECTION_SEMVER` bumped (e.g. `0.1.0 -> 0.2.0`) so all backtests
   invalidate cached results.
4. Either translate-map (Option B) OR re-download `TranslateTrade=ON`
   (Option C) executed.

**Until then:** F2 is parked. Anti-Article-IV Guard #9 candidate (information
preservation principle).

### References

- [Council 2026-05-03 SCHEMA-RESOLUTION](../docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md)
  §1.1 (Dara A2 findings F1-F5 + F8 table) and §6.5 (Option D routing).
- [D-02 register](../docs/audits/AUDIT-2026-05-03-T003.A2-schema-split-divergence.md)
  — Sable [DIVERGENCE] entry parallel to D-01 H_next-1 register.
- [Story T003.A4](../docs/stories/t003.a4.minimal-cast-projection.story.md)
  — AC1-AC7 mandate + 10-point Pax validation.

---

## Usage

```python
from scripts.dll_backfill_projection import (
    project_parquet,
    compute_dataset_hash,
    PROJECTION_SEMVER,
)

# 1. Load + cast a backfill chunk to canonical 7-col projection
projected, report = project_parquet(
    r"D:\Algotrader\dll-backfill\WDOFUT_2023-01-02_2023-01-06\wdofut-2023-12-bf3feaa06054.parquet"
)
assert projected.schema.field("timestamp").type.unit == "ns"
assert projected.schema.field("qty").type.bit_width == 32
assert projected.schema.field("buy_agent").type.bit_width == 64  # F2

# 2. Reproducibility cache key (Sable C3)
cache_key = compute_dataset_hash(
    r"D:\Algotrader\dll-backfill\WDOFUT_2023-01-02_2023-01-06\wdofut-2023-12-bf3feaa06054.parquet"
)
# cache_key = (sha256_hex, PROJECTION_SEMVER)
```

---

## R10 / Gate 5 / Article II discipline

- This module **NEVER** writes to `data/manifest.csv` (in-repo R10 custodial);
  `upgrade_manifest_header()` raises `PermissionError` if pointed at it.
- This module **NEVER** mutates production parquet at `D:\Algotrader\dll-backfill\`.
- Only the off-repo backfill orchestrator manifest at
  `D:\Algotrader\dll-backfill\manifest.csv` is touched (and the comment line
  literally says `NOT R10 custodial`).
- Push @devops Gage exclusive (Article II) — Dara does not commit/push.

---

## Test artifacts

| AC | Test file |
|---|---|
| AC1 | `tests/scripts/test_projection_timestamp.py` |
| AC2 | `tests/scripts/test_projection_qty.py` |
| AC3 | `tests/scripts/test_projection_nullability.py` |
| AC4 | `tests/scripts/test_projection_f2.py` |
| AC5 | `tests/scripts/test_manifest_header_v1_1.py` |
| AC6 | `tests/scripts/test_projection_versioning.py` |
| AC7 | A2 re-audit verdict generated on demand via
        `reaudit_at_projection_boundary()`; verdict file lives at
        `docs/audits/T003-A2-reaudit-2026-05-03.md`. |

---

## Change log

| Date (BRT) | Author | Change |
|---|---|---|
| 2026-05-03 | Dara (@data-engineer) | Initial implementation per Council 2026-05-03 §6.5 routing item 1. F2 documented as ACCEPTED DIVERGENCE with full ballot trace. PROJECTION_SEMVER 0.1.0. |
