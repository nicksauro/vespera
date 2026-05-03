# Mira Vote — Council 2026-05-03 Schema Resolution + R16

> **Voter:** Mira (@ml-researcher) — stationarity, multiple-testing, leakage prevention, IC stability cross-window
> **Date (BRT):** 2026-05-02
> **Status:** FILED — no commit, no push

---

## Vote: **Option D** + **CONCUR R16**

---

## Rationale (authority lens)

### 1. H_next-1 thesis direction — DECISIVE for convergence

H_next-1 draft v0.1.0 (`docs/ml/specs/H_next-1-conviction-conditional-sizing-spec.md`) is **technical-pure**:

- Predictor IP carry-forward: `-intraday_flow_direction = -sign(close[t_entry] - open_day)` (IC=0.866 OOS-robust cross-window).
- Conviction filter T1/T2/T3: `intraday_flow_magnitude > P60`, `atr_day_ratio ∈ [P40,P80]`, bootstrap CI95 — all **price/volume only**.
- Zero broker-identity, zero agent-id, zero smart-money in scope (grep `broker|agent` → only fee references).
- §0.4 Scope OUT: cost atlas re-tuning **BLOCKED**; lista negativa N1-N14 carry-forward.

**Conclusion:** H_next-1 does NOT need broker strings. Spending now on B/C is pre-empting a thesis that does not exist on the spec.

### 2. Multiple-testing α budget (CRITICAL)

Bonferroni cumulative budget is **8 trials hard cap** (T002: 5 + H_next-1: 3) ratified by Quant Council R5. With ~50-100 active brokers, broker-tier conditioning expands hypothesis space by ~10-100× (broker × tier × side × regime). Even with BH-FDR q=0.10, broker-conditioning alone consumes **>50% of remaining α surface** before any technical hypothesis is tested. Option B/C burn α budget on optionality without thesis demand. **REJECT** as α-wasteful.

### 3. Stationarity — Option B is dangerous

Broker behavior 2023→2024 is **demonstrably non-stationary** (XP growth, BTG strategy shift, RLP regime change Nova-confirmed). A 2024-built mapping joined to 2023 trades creates **implicit time-leakage**: the mapping itself encodes 2024-state knowledge applied retroactively to 2023. ADF/KPSS on broker-conditional CVD would fail by construction. Magnitude: **HIGH** — equivalent to scaler-fit-on-full-dataset class of leakage. Option B violates my REGRA ABSOLUTA #3 (leakage by design).

### 4. Sample-size adequacy

~250 trading days × 50 brokers × 3 tiers = ~37k cells. Per-cell N ≈ 7 events/day = ~1750. **Fails** Bailey-LdP §3 minimum-N for K3 generalization once you condition. Bonferroni × small-cell = cell-level DSR threshold ≈ 1.5+ — unattainable. **Unfit** for K3 cross-window stability.

### 5. R16 alignment

R16 **HELPS** anti-leakage discipline: storage preserves raw → projection at consumption is **explicit, traceable, fold-aware**. Scaler/translation can be fit-on-train-only at projection boundary. Fits Lopez de Prado 2018 §7 purged-CV discipline. **CONCUR**.

---

## Decision

- **Option D** — defer broker question; cast `int64→int32` only; H_next-1 proceeds technical-pure.
- **R16 CONCUR** — information preservation default + projection-at-consumption matches my fold-aware leakage discipline.
- IF/WHEN a future H_next-N spec demands brokers: reconvene; choose B *with* fresh Bonferroni budget and stationarity audit, or C if budget allows.

— Mira, mapeando o sinal
