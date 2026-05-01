# Quant Council 2026-05-01 — Alpha Discovery Resolution post T002 RETIRE

> **Date (BRT):** 2026-05-01
> **Trigger:** T002 RETIRE FINAL (PR #17 main `06dcdda`); user convocou Quant Council para alpha discovery direction
> **Authority:** Mini-council 5-vote (Kira lead + Mira + Nova + Beckett + Riven)
> **User constraints:** custos FIXOS imutáveis (Path A original cost reduction OFF); algoritmo (não indicator)
> **Article IV:** independent ballots verified per self-audit per ballot
> **Author:** @aiox-master orchestration capacity, autonomous mode

---

## 1. Outcome — DUAL-DIRECTION RATIFICATION

**Convergence achieved on 2 primary candidates** + 1 deferred direction. Council does NOT pursue single-thesis monolithic; instead recommends sequential pipeline with explicit Bonferroni discipline:

### **PRIMARY (sequential T1):** **Conviction-Conditional Sizing on T002 predictor IP**

5/5 voters reference (Kira via H_next-2 meta-labeling; Mira (a) #1; Nova partial via filter logic; Beckett F1 #1; Riven (A) CONDITIONAL ACCEPT). Reuse IC=0.866 OOS-robust predictor + add per-trial conviction filter (e.g., predictor magnitude >P80 OR bootstrap CI tight). Goal: amplify gross edge per-trade by trading FEWER but with HIGHER conviction → potentially clear K1 strict bar 0.95 sob fixed costs. Single-iteration discipline (single binary AC per trial; Bonferroni new=3 trials max).

### **SECONDARY (sequential T2 if PRIMARY fails K1):** **Microstructure-novel: Auction Print Analysis**

Nova P1 PRIMARY (information density per event highest na estrutura B3; trades-only computable; pre-RLP timing; white space FGV/Insper microstructure-BR). Open auction (09:00-09:30) implied direction → first 30min trend persistence prediction. Distinct from T002 perimeter (different time-of-day, different microstructure regime). New predictor IP (não reuse T002).

### **DEFERRED (parallel-track if Beckett engine v1.2.0 perf optimization lands):** **Asymmetric Exit Refinement**

Mira (c) #3 + Beckett F3 #2. Replace fixed triple-barrier `1.5×ATR PT / 1.0×ATR SL` com asymmetric "winners run longer, losers tight stop". Risco overfitting médio; Bonferroni budget compatible se single-threshold pre-registered. Aria archi review needed (~5-10 days).

---

## 2. Vote distribution matrix

| Direction | Kira | Mira | Nova | Beckett | Riven |
|---|---|---|---|---|---|
| **Conviction sizing** | (H_next-2 meta) | **(a) #1** | (filter logic) | **F1 #1** | **(A) cond accept** |
| Label horizon swap (overnight) | **H_next-1 #1** | (d) #2 | — | — | **(D) STRONG REJECT** (gap variance unbounded) |
| Asymmetric exit | — | (c) #3 | — | F3 #2 | (C) deferred |
| Multi-timeframe regime filter | (within H_next-2) | **REJECT (b)** Bonferroni blow | — | F2 #3 | **(B) PRIMARY** |
| **Auction print** (Nova P1) | — | — | **P1 #1** | — | — |
| Cross-trade signature (Nova P2) | — | — | P2 #2 | — | — |
| Rollover spread (Nova P3) | — | — | P3 #3 | — | — |
| Cross-asset WDO×WIN dispersion | H_next-3 #3 | — | — | — | — |
| VPIN microstructure | (mention) | — | de-prioritized | — | (E) cond pos book-wiring |

---

## 3. Critical divergences resolved

### Divergence #1: Overnight horizon swap (Kira H_next-1 PRIMARY vs Riven STRONG REJECT)

**Resolution: REJECT overnight per Riven risk veto.**

Rationale: Riven argument verbatim — "gap variance unbounded; not Quarter-Kelly parametrizable". Quarter-Kelly REGRA ABSOLUTA preserved indefinitely per §11.5 binding. Overnight gap exposure violates sizing posture. Mira's (d) label horizon swap to `ret_to_close_BR` 17:55 is INCLUDED em PRIMARY (intraday close-of-session, not overnight) — preserves Mira's preference without overnight exposure.

### Divergence #2: Multi-timeframe regime filter (Mira REJECT vs Riven PRIMARY)

**Resolution: PARTIAL ACCEPT — embed simple regime filter inside Conviction-Conditional Sizing PRIMARY.**

Rationale: Mira's REJECT was on Bonferroni budget (multi-timeframe = multi-trial family; Bonferroni inflation tightens K1 bar). Riven's PRIMARY was on risk control (regime conditioning reduces drawdown variance). **Compromise:** PRIMARY conviction sizing uses single regime filter (e.g., `atr_day_ratio ∈ P40-P80 normal regime`) as one of trial conditions, NOT multi-timeframe family. Bonferroni budget contained at n_trials=3.

### Divergence #3: VPIN / book-features (defer)

5/5 alignment on DEFER pending ProfitDLL book-snapshot wiring (Riven E condition; T003+ infrastructure work; not H_next first cycle).

---

## 4. Consolidated 17 binding conditions (Bonferroni + budget + governance)

### 4.1 New Bonferroni budget (5 conditions)

| ID | Mandate |
|---|---|
| **R1** | Fresh research-log invariant `n_trials: 0` for H_next first cycle; PRIMARY uses Bonferroni n_trials=3 NEW (carry-forward 5 from T002 + 3 new = 8 total budget); H_next FRESH research-log commit hash hash-frozen pre-spec |
| **R2** | Single-threshold per trial; no within-trial threshold optimization (anti p-hacking) |
| **R3** | Bonferroni adjusted DSR threshold: 0.95 → ~1.005 effective (n_trials=8); strict bar reinforced |
| **R4** | Mira spec template §15 IC wiring + §15.13 Phase G unlock protocol PRESERVED canonical (Aria approved); H_next inherits |
| **R5** | n_trials=3 PRIMARY caps total trials over single H_next cycle; secondary T2 (auction print) requires fresh budget if pursued |

### 4.2 Hold-out window (4 conditions)

| ID | Mandate |
|---|---|
| **R6** | T002 hold-out 2025-07-01..2026-04-21 CONSUMED (one-shot per ESC-012 R9 + ESC-013 R19) — NOT reusable |
| **R7** | Forward-time virgin hold-out PRIMARY: 2026-05-01..2026-10-31 (impossível leakage; data ainda não existe; Mira preferred) |
| **R8** | OR pre-2024 archival hold-out 2023-Q1..2024-Q3 IF Dara confirms coverage AND Sable audits virgin status (Kira preferred) |
| **R9** | Walk-forward rolling REJECTED (Mira: 12 trials Bonferroni blow; Riven: researcher-observation contamination) |

### 4.3 Spec-first protocol (4 conditions)

| ID | Mandate |
|---|---|
| **R10** | T0a-T0e + T0f NEW caller-wiring sign-off chain (River Impl Council carry-forward) |
| **R11** | PRR-{date}-1 pre-empirical hash-frozen disposition rule mandatory pre-N1+ run (Pax canonical pattern from PRR-20260430-1) |
| **R12** | Anti-Article-IV Guard #9 candidate (verdict-vs-reason consistency invariant) — Mira spec v0.3.0 amendment per Sable proposal |
| **R13** | Closure-body Literal completeness check (Quinn QA Check N+2 NEW per Sable F-03) |

### 4.4 Risk + sizing (4 conditions)

| ID | Mandate |
|---|---|
| **R14** | Quarter-Kelly REGRA ABSOLUTA preserved INDEFINITELY |
| **R15** | §11.5 capital-ramp pre-conditions #1-#7 PRESERVED + NEW #8 capture-rate ≥ 0.6 of theoretical Sharpe (Riven) + #9 DSR stationarity \|DSR_OOS - DSR_IS\| ≤ 0.10 + #10 PnL-IC alignment ≥ 0.30 |
| **R16** | Per-bucket sizing cap if Conviction-Conditional Sizing PRIMARY (Riven §5.2 mandate; max conviction-bucket exposure = 60% of Quarter-Kelly cap) |
| **R17** | Beckett engine v1.2.0 perf optimization PARALLEL-TRACK NON-BLOCKING for first trial; MANDATORY before n_trials=3+ runs (Beckett T-1) |

---

## 5. Lista negativa updated (N8-N14 NEW + N1-N7 carry-forward)

| ID | Direction | Rejected by |
|---|---|---|
| N1-N7 | (per T002 thesis prior — trend-following / pairs WDO×WIN unconditional / carry / Turtle / OBI / 1-tick prediction / smart-money following) | Quant Council 2026-04-21 |
| N8 | Re-investigate T002 fade with refined cost (Path A original) | User constraint 2026-04-30 |
| N9 | Triple-barrier label refinement | Bonferroni blow risk |
| N10 | Vol breakout naive | Same-window IS-fit risk |
| N11 | Book L2 features in backtest | Histórico GAP (R7) |
| N12 | Pure ML black-box | Article IV no-invention violation risk |
| N13 | HFT tick-by-tick prediction | DMA2 latency p99 100ms binding |
| N14 | Calendar arbitrage cross-asset | Insufficient sample WIN×WDO history |

---

## 6. Status

- [x] 5/5 ballots cast independent (Article IV verified)
- [x] Outcome ratified: PRIMARY conviction-conditional sizing + SECONDARY auction print + DEFERRED asymmetric exit
- [x] 3 critical divergences resolved (overnight veto / regime filter compromise / VPIN defer)
- [x] 17 conditions consolidated R1-R17
- [x] Lista negativa N1-N14 updated
- [ ] Mira spec H_next-1 spec drafting (next step)
- [ ] Aria archi review per H_next spec
- [ ] River SM story drafting T002.7+1 successor
- [ ] PRR-{date}-1 disposition rule register pre-N1
- [ ] Beckett T-1 engine v1.2.0 perf optimization parallel-track

---

## 7. Authority chain

```
Council convened: User mandate 2026-05-01 — convoke whole-team alpha discovery post T002 retire
Voters: 5 (Kira lead + Mira + Nova + Beckett + Riven)
Inputs: T002 retire memory + Round 3.1 verdict + Riven 3-bucket post-mortem + cost atlas v1.0.0 + DOMAIN_GLOSSARY
Constraint: custos FIXOS imutáveis (Path A original cost reduction OFF); algoritmo não indicator
Article II: preserved (no push)
Article IV: preserved (independent ballots; convergence on PRIMARY 5/5 different lenses; divergences resolved via composition)
Cosign: @aiox-master 2026-05-01 BRT
```

— @aiox-master, orchestrating the squad
