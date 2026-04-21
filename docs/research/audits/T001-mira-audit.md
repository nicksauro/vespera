# Mira Feature-Eval Audit — T001 Bar-Close Momentum WDO 5-min

**Owner:** Mira (@ml-researcher)
**Command:** `*feature-eval + *leakage-audit`
**Thesis ref:** docs/research/thesis/T001-bar-close-momentum-wdo-5min.md
**Data:** 2026-04-21 BRT

---

## 1. Features propostas

| Feature | Computável trades-only? | Leakage risk | Nota |
|---------|------------------------|--------------|------|
| `mom_3bar = sum(log_return[t-3:t])` | SIM | BAIXO — usa só close[t-3:t] | OK |
| `regime_vol_filter = ATR(14)/close` | SIM | BAIXO — ATR usa histórico puro | OK |

## 2. Label

- `ret_next = log(close[t+1]/close[t])`
- **Leakage check:** feature timestamp (t) < label timestamp (t+1) → OK
- **Purging requirement:** sim (label usa barra futura, observações na fronteira do fold precisam purga)

## 3. Sample size

- ~12.000 barras 5-min por mês × 30 meses = ~360.000 observações
- Bem acima do mínimo 100 trades (R6 MANIFEST) — OK

## 4. CV scheme aplicabilidade

- CPCV N=10, k=2, embargo=1 sessão aplicável
- 45 paths garante distribuição de métricas (não ponto)

## 5. Flags

- ⚠️ Overfitting risk: feature é simplíssima, mas N_trials pode crescer se Beckett testar múltiplos thresholds → Bonferroni correction obrigatória

## 6. Verdict

**PRELIMINARY-OK**

Mira libera para Beckett rodar CPCV. Esperado baixo IC (feature é trivial) — objetivo é smoke-test de pipeline, não descoberta de alpha.

---

**Assinado:** Mira (@ml-researcher) — 2026-04-21 BRT
