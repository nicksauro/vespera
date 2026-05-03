# Riven (Risk Manager) — Vote Ballot

> **Council:** 2026-05-03 Schema Resolution + R16
> **Lens:** Cost-benefit (Bayesian joint), custodial preservation (R10), governance debt curve, kill-switch / blocking caps
> **Date:** 2026-05-03

---

## §1 Bayesian joint per option

P(thesis-fit) × P(cost-OK) × P(stationarity-OK) × P(custodial-OK).

| Option | thesis-fit | cost-OK | stationarity-OK | custodial-OK | **Joint** |
|---|---|---|---|---|---|
| A — project + cast naive | 0.65 | 0.90 | 0.85 | 0.90 | **0.45** |
| B — translate-map post-hoc | 0.70 | 0.55 | 0.40 | 0.70 | **0.11** |
| C — re-download TranslateTrade ON | 0.75 | 0.10 | 0.85 | 0.95 | **0.06** |
| D — defer (cast int32 only) | 0.70 | 0.95 | 0.95 | 0.95 | **0.60** |

**No option crosses 0.80** — all carry residual uncertainty (H_next-1 thesis still in draft by Mira). **Option D leads** by maximizing custodial-preservation × cost-OK × stationarity (no broker mapping = no broker non-stationarity exposure). Option A second. B+C below threshold (B fails stationarity 2023≠2024; C fails cost-OK with 6h25 sunk + 6h25 new).

## §2 Sunk cost honesty

~6h25 already spent on bulk = **sunk, irrecoverable**. Decision rule (Riven principle): *future cost-benefit only*. Re-running C costs **another** 6h25 + DLL session + validation cycle (~15h total marginal) for a thesis that **does not yet require brokers**. A/B/D salvage. C does not — quarantines current 50 chunks pending merge. Thesis-decides-schema, not schema-decides-thesis (Option D framing).

## §3 Custodial (R10) preservation

All 4 options preserve `data/manifest.csv` registry-of-record — **CONFIRMED**. A/B/D preserve raw 10-col parquet on D:\ untouched (R10 strict). C creates new bulk that supersedes — must explicitly archive old 50 chunks under `data/quarantine/` with manifest entry to remain R10-compliant. **C is custodially weakest** unless quarantine protocol enforced.

## §4 R16 — concur

**CONCUR.** R16 *tightens* custodial discipline (it forbids destructive normalization at storage; forces projection to consumer boundary). Aligns with R10 spirit. Risk lens: information once destroyed is irrecoverable; information preserved is optionality. Optionality has positive expected value when future thesis is uncertain. Concur with one caveat: R16 must specify **who** owns "registry-of-record" definition (proposed: Dara per data engineering authority + Sable cross-validation).

## §5 Governance debt curve

Council 2026-05-01 (R1+R5+R6) → Council 2026-05-03 (R16) = **2 amendments in 3 days**. My prior disclosure flagged debt curve. Mitigation: R16 is **principle-elevation** not tactical patch — generalizes across future acquisitions, reducing future amendment frequency. Net debt curve: **acceptable** if next 14 days yield zero new amendments. Sable should track.

## §6 Vote

| Item | Vote |
|---|---|
| **Option** | **D** (defer broker question; cast int32; preserve 10-col storage; technical-pure A3/A4 path) |
| **R16** | **CONCUR** |

**Rationale:** D maximizes Bayesian joint (0.60), respects sunk cost, preserves custodial under R10+R16, minimizes governance debt impact, lowest cost (~2h Dara), preserves optionality for future B/C if thesis demands. Kill-switch principle: when uncertain, reduce. D is the reduction.

— Riven, guardando o caixa
