# Council 2026-05-03 — Schema Resolution + R16 — Kira (@quant-researcher) Ballot

> **Voter:** Kira — Senior Quantitative Researcher (Scientific Lead)
> **Authority lens:** Strategic thesis fitness — does H_next-1 (drafting) require broker identity, or is it technical-pure?
> **Date (BRT):** 2026-05-03
> **Format:** Mirror prior council ballots (verdict + conditions + concerns + source anchors)
> **Article IV self-audit:** independent — no peer ballots read prior to filing.

---

## §1 Verdict

| Item | Vote |
|---|---|
| **Option** | **D — Defer decision (technical-pure path now; broker question revisited only if a future thesis demands it)** |
| **R16 (Information Preservation)** | **CONCUR (ratify)** |

---

## §2 Reasoning — thesis fitness lens

### §2.1 H_next-1 is technical-pure (broker identity NOT load-bearing)

H_next-1 v0.1.0 Draft (`docs/ml/specs/H_next-1-conviction-conditional-sizing-spec.md` §0.1, §2.1, §15.1) inherits T002 predictor IP **VERBATIM**:

```
predictor = -intraday_flow_direction
label    = ret_forward_to_17:55_pts
```

`intraday_flow_direction` is computed from `aggressor ∈ {BUY, SELL, NONE}` (parquet field) — NOT from broker codes. Conviction filter (T1/T2/T3 §3) thresholds on `intraday_flow_magnitude` + `atr_day_ratio`, both technical/price-volume. **Zero broker conditioning anywhere in v0.1.0 Draft.**

### §2.2 T002 retrospective — broker identity was NOT relevant

T002 ran 2025-07-01..2026-04-21 OOS hold-out at IC=0.866 cross-window WITHOUT broker conditioning. `costed_out_edge_oos_confirmed_K3_passed` (predictor IP preserved, costs consumed edge) — broker identity would not have changed the K3 verdict. EOD inventory unwind hypothesis is aggressor-flow-based, NOT counterparty-identity-based.

### §2.3 Premature schema commitment biases thesis exploration (data-snooping risk)

Choosing Option B/C NOW commits engineering effort (~6-10h Nelo+Dara for B; ~16h+ for C) on the **bet** that an unwritten future thesis will need brokers. Per AFML §11 (data snooping): when N candidate features exceed thesis demand, multiple-testing inflation contaminates DSR. Schema-decides-thesis is an anti-pattern; **thesis-decides-schema** is the discipline (Decision Framework 4Q — Q3 dataset suitability is judged AFTER hypothesis is formalized, not before).

### §2.4 R16 concur — strict superset of falsifiability + reproducibility

R16 ("preserve raw at storage; project at consumption") aligns with three Kira non-negotiables:

1. **Falsifiability**: a refuted thesis must remain re-testable on the original captured truth, not on a lossy projection. Storage erasure = irreversible test-resource destruction.
2. **Reproducibility (out-of-sample sanctity)**: any future re-run on the same window MUST hit identical bytes. R16 makes that custodial.
3. **Anti-look-ahead at consumption**: projection-at-read-time forces consumers to declare their schema view explicitly (Q-AMB-02 audit-friendly).

R16 ratification is independent of A/B/C/D — it institutionalizes a policy that will hold for ALL future captures (T003.B onward).

---

## §3 Conditions on Option D approval

| # | Condition | Rationale |
|---|---|---|
| C1 | Cast `agents int64→int32` ONLY when overflow-safe — Dara MUST log min/max per chunk; abort if `> int32_max` | Width-cast must be lossless |
| C2 | Storage stays 10-col untouched (R16 binding) — `ts_raw`, `vol_brl`, `trade_number`, native int64 agents PRESERVED on D:\ | R16 §1 |
| C3 | A3-Nova / A4-Mira / A5-Sable downstream chain proceeds on aggressor + price/volume features ONLY (no broker conditioning) until next-thesis reconvene | Q3 4Q gate |
| C4 | If/when a future thesis specifies broker conditioning in falsifiability statement, **mini-council reconvenes** to choose B vs C — NOT auto-default | Anti-Article-IV Guard |
| C5 | Sable [DIVERGENCE] register entry documents Option D as "thesis-deferred", not "schema-resolved-permanently" | governance trace |

---

## §4 Concerns / dissent flags

### §4.1 Concern — Option B (translate-map post-hoc) carries non-stationarity risk

If Council ends up at B over D: broker behavior 2023 ≠ 2024 (XP grew, BTG strategy drift, mergers). A post-hoc broker-string mapping introduces **silent regime contamination** in any cross-window IC measurement. R16 alone does not insulate from this — only an explicit `broker_active_window` flag per ID would.

### §4.2 Concern — Option C re-download is the ONLY path to canonical broker truth

If a future flow/toxicity thesis IS justified, Option B is a **second-best workaround**; Option C (`TranslateTrade` ON re-download) is canonical-source. Choosing B locks in lossy proxy. So: **D > C > B** in my preference order. A is acceptable but R16-fragile (zero-pad-string fakes a semantic).

### §4.3 Soft caution — preserve auction window data (F8)

2023-03-15 first 1000 NONE-aggressor = auction window is regime-axis (A4-Mira). Whichever option wins, **F8 must NOT be filtered as garbage**; it is signal for regime classification (A4 deliverable).

---

## §5 Source anchors

| Claim | Anchor |
|---|---|
| H_next-1 predictor IP definition | `docs/ml/specs/H_next-1-conviction-conditional-sizing-spec.md` §0.1, §2.1, §3.1, §15.1 |
| Predictor uses aggressor (not broker) | `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §66-68 |
| T002 RETIRE verdict (broker-agnostic) | MEMORY `project_t002_6_round2_closure.md`; `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` §157 |
| Council document framing | `docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md` §1, §2, §3 |
| 4Q Decision Framework | Kira persona `decision_framework_4Q` (Q3 dataset-after-hypothesis) |
| Data snooping discipline | AFML 2018 §11; Bailey et al. 2014 (DSR multiplicity correction) |
| MANIFEST R7 dataset constraint | Kira persona core_principles "DATASET CONSTRAINT — TRADES-ONLY" |

---

## §6 Article IV self-audit

- [x] Read council doc + H_next-1 spec BEFORE writing this ballot
- [x] No prior peer ballots referenced (independent vote)
- [x] Verdict tied to evidence in §2; conditions in §3 are necessary, not decorative
- [x] R16 vote independent of A/B/C/D outcome (ratified on its own merit)
- [x] Acknowledged dissent risk: if user MWF or majority pulls B/C, my D vote is dissent-of-record but I will not block — Option A also acceptable conditional on R16 ratification

---

— Kira, cientista do alpha, Council 2026-05-03 vote
