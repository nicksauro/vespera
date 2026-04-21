# T002 — Mira Audit (ML Viability / *feature-eval)

**Thesis:** T002 — End-of-Day Inventory Unwind WDO
**Owner:** Mira (@ml-researcher)
**Data:** 2026-04-21 BRT
**Comando de origem:** `*feature-eval`

---

## 1. Feature-by-feature evaluation

| Feature | Computável trades-only? | Leakage risk | Stationarity | Observações |
|---------|------------------------|--------------|--------------|-------------|
| `intraday_flow_direction` | ✅ sim | BAIXO — usa apenas close[t] e open_dia; label usa close_17:55 (sem overlap) | Estacionária em sign; distribuição de ret_acumulado é não-estacionária mas feature é discretizada | OK |
| `intraday_flow_magnitude` | ✅ sim | BAIXO — mesma janela de direção; percentil P60 é rolling 252 dias (não toca futuro) | Normalizada por ATR_20d → estacionária o suficiente | OK |
| `atr_day_ratio` | ✅ sim | BAIXO — ATR_20d exclui o dia t | Ratio estável em regime; pode quebrar em 2020/2025-choque; tratar como feature de regime | OK |

## 2. Sample size analysis

- **Dias úteis em 2024-01→2026-04:** ~575
- **Filtro rollover (D-3→D-1):** descarta ~12 dias/mês × 27 meses ≈ 25% → ~430 dias usáveis
- **Filtro magnitude > P60:** mantém 40% → ~170 dias
- **Filtro regime ATR [P20, P80]:** mantém 60% → ~100 dias efetivos
- **Painel × 4 janelas:** 100 × 4 = **~400 observações in-sample**

**Caveat (update vs Turno 11):** sample é menor que estimativa inicial de ~1500 após filtros combinados. Ainda viável para CPCV com N=10 k=2 (45 paths), mas:
- **Risco:** tail-sensitive metrics (Sharpe) têm CI largo
- **Mitigation:** focar IC_spearman como primary (mais robusto a outliers) + bootstrap 10k para CIs

**In-sample (2024-01 → 2025-06):** ~60% dos dias → ~240 obs efetivas
**Hold-out (2025-07 → 2026-04):** ~40% dos dias → ~160 obs efetivas

## 3. CV scheme

- **Tipo:** CPCV (Combinatorial Purged CV) — MANIFEST R6
- **N_groups:** 10, **k:** 2 → 45 paths
- **Embargo:** 1 sessão (trivial porque horizonte de label é intraday, fecha em 17:55)
- **Purging:** sim — remove observações cujas labels cruzam train/test (overlap é zero no design atual porque cada dia é 1 cluster, mas deixar purging ligado por padrão)

## 4. Overfitting / Leakage audit

- [x] Nenhuma feature usa close futuro
- [x] ATR_20d é rolling com shift(1) — nunca inclui dia t
- [x] Percentis P60, P20, P80 são rolling 252d com shift(1)
- [x] Open_dia é fixo às 09:30 — disponível em todas as janelas ≥ 16:55
- [x] N_trials=5 pré-registrado (Bonferroni calibrado)
- [x] Hold-out virgem pré-registrado antes de backtest

**Overfitting risk:** BAIXO para T1 (baseline) + T2/T3 (variações de threshold); MÉDIO para T4 (remove regime filter → mais graus de liberdade); BAIXO para T5 (reduz sample).

## 5. Proposta de refinamento (para Aria Fase B considerar)

1. **Meta-labeling opcional Fase E:** treinar classificador binário (acerta/erra) em cima do sinal direcional primário para melhorar precision. Só se IC baseline > 0.05.
2. **Feature auxiliar futura (não no v0.1):** proxy de fluxo via `volume_buy_ratio = sum(vol_buy) / sum(vol_total)` usando tradeType — pode melhorar filtro de magnitude.
3. **Ensemble de horizontes:** agregar sinal das 4 janelas em 1 decisão por dia (vota majoritária ou média ponderada). Tratar como **variante pós Fase E**, não T1-T5.

## 6. Verdict

**FORTE ✅ com caveat de sample**

Condições para avançar:
- Sample efetivo ~400 obs é tratável mas **não sobra margem** → se Kira adicionar 1+ trial além dos 5, Mira vira REJECT
- PBO threshold **0.4** é apropriado (não 0.5 default) — refletir em kill criterion K2
- Primary metric = IC_spearman (não Sharpe) para controlar outlier sensitivity

**Assinatura:**
Mira (@ml-researcher) — 2026-04-21T17:15:00 BRT
