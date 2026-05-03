# Dara ballot — Council 2026-05-03 Schema Resolution + R16

> **Voter:** Dara (@data-engineer)
> **Authority lens:** Engineering effort (honest hours) + execution risk per option.
> **Date:** 2026-05-03 BRT
> **Article IV self-audit:** independent ballot. Read only the council brief, Beckett's vote, Riven's vote (cross-context), and the empirical artefacts I authored (`_audit_a2.out`, `t003.a2` story, `manifest-write-flag-spec.md`).

---

## §1 Vote

**Option:** **A** (preserve 10-col storage; project + naive cast at consumption).
**R16:** **CONCUR.**

---

## §2 Honest effort estimates (Dara hours)

| Option | Impl | Tests | A2 re-audit | **Total** |
|---|---|---|---|---|
| A — projection + naive cast (zero-pad) | 2.0h | 1.5h | 1.0h | **4.5h** |
| B — translate-map + post-hoc remap | 3.0h Dara + 2-4h Nelo | 2.0h | 1.5h | **6.5h Dara + 2-4h Nelo** |
| C — re-download `TranslateTrade` ON | 0.5h orchestration + 6h25 wall-time + 4h validation | 1.0h regression | 4.0h (full bytes-equal redo on 50 chunks) | **~16h wall + 9.5h Dara** |
| D — minimal `int32` cast | 1.0h | 1.0h | 0.5h | **2.5h** |

D is cheapest, A is +2h for **strict superset** of D's capability (zero-pad string preserves 2024 string-encoding shape; `int32` cast preserves only numeric). The +2h buys downstream codepath uniformity (one consumer pattern across 2023 ↔ 2024).

## §3 Storage v1.1 manifest impact

**Manifest v1.1 is 15-col chunk-level metadata** (`chunk_id..outcome` per `_audit_a2.out:14`), orthogonal to parquet column count. **No option requires manifest schema bump.**
- A/B/D: 10-col parquet stays as-is on D:\, manifest rows unchanged.
- C: new chunks → new manifest rows (still v1.1) + old chunks must be quarantined per Riven R10 (additive, not schema mutation).

T003.A3 will bump manifest to **19-col v1.2** independently (per `t003.a2.story.md:30,40`). That work is NOT gated by this vote.

## §4 A2 re-audit per option (parity verification)

| Option | Bytes-equal at projection? | Bytes-equal at physical? | Audit method |
|---|---|---|---|
| A | YES (post-projection 7-col matches Sentinel canonical bytewise except agents which match by `f"{int:05d}"` zero-pad) | NO (10-col physical preserved by design — that's R16) | Run `compare_schemas.py` on **projected** view vs Sentinel 2024-01 head; assert dtype + null + value parity. Add `agents_zeropad_invariant` test (round-trip int64 → str → int64). |
| B | YES on rows where mapping resolves; UNDEFINED on missing keys | NO | Plus mapping-completeness audit: % rows with successful broker resolution; reject if <99.5%. |
| C | YES bytewise after re-download | YES (new physical = canonical) | Full re-run of A2 audit (16 checks). Plus quarantine attestation for old 50 chunks. |
| D | NO (agents stay numeric int32, not zero-pad string) — fails F2 parity | NO | Partial parity only; F2 documented as accepted divergence in [DIVERGENCE] register. |

**Parity bar for A:** projection-time bytes-equal on the 7-col view. That's a clean, auditable contract.

## §5 R16 implementation cost

**Pure principle (~zero tooling).** R16 codifies what backfill probe already does empirically — capture rich, project at consumer. Concrete deltas needed:
- One projection module per consumer family (**~150 LoC**, T003.A4 scope) — would be written for Option A anyway.
- `[DIVERGENCE]` register entry template — 1 markdown stub.
- `aiox doctor` check (optional, future) verifying registry-of-record paths exist.
**No retroactive refactor of past pipelines.** R16 is forward-binding.

## §6 Engineering risk per option (highest → lowest)

1. **C — re-download:** highest. Unknown DLL state across new credentials session, possible new bugs (Q-FIN-12-E quiesce, Q-PATH-14-V, IncrementalParquetSink bloat patterns). 6h25 wall-time exposed to single-point-of-failure. **Reject on risk.**
2. **B — translate-map:** medium-high. Mapping completeness uncertain; non-stationarity 2023≠2024 (Beckett's CPCV showstopper); broker-name churn (mergers, rebrands). Imports future-state info silently.
3. **A — projection + zero-pad cast:** low. Zero-pad of int64 broker codes within `[0, 99999]` is bounds-safe (validated empirically: max code in 2023-12 sample fits in 5-digit). Projection is pure function, deterministic, testable. Risk = none-load-bearing for current backtester (Beckett confirmed agent-blind).
4. **D — int32 cast:** lowest impl risk BUT carries data-loss risk if any agent code >2^31-1 (need to validate; broker codes empirically <100000 so safe — but D loses string-shape parity with 2024).

**Overflow check (D):** broker IDs in 2023-12 sample are all <2^15. int32 safe. Not the failure mode.

## §7 Why A over D

D is cheaper by 2h but ships a permanent F2 divergence (numeric agents 2023, string agents 2024). A invests 2h to retire F2 cleanly. Across A3/A4/A5 horizon, **uniform consumer pattern is worth 2h**. If Mira's H_next-1 turns flow-based, A's zero-pad is reversible to real broker strings via Option B upgrade *without re-download* (storage preserved). D would force a Phase-2 broker decision later anyway.

---

## §8 Caveats binding A

1. Projection function lives in `packages/data/projection_2023_canonical.py` — **versioned semver**, included in dataset hash.
2. Zero-pad encoding documented as **synthetic placeholder** (NOT real broker name) in module docstring + Sable [DIVERGENCE] register.
3. Round-trip invariant test: `int64 → str(zero-pad) → int64` = identity. Hard QA gate.
4. A3-Nova / A4-Mira ingestion CONSUMES projected view by default; raw 10-col reachable via `load_raw=True` opt-in for future flow-based work.
5. R16 implementation in T003.A4 includes a `registry_of_record.yaml` listing canonical raw paths per dataset (Dara owns, Sable cross-validates).

---

**Vote:** **A** + **R16 CONCUR**.

— Dara, custodial-by-default, projection-by-discipline.
