# Thesis T001 — Bar-Close Momentum WDO 5-min

**Status:** DRY-RUN (smoke-test Q-SDC, não é tese real para operar)
**Data:** 2026-04-21 BRT
**Owner:** Kira (@quant-researcher)
**Fase:** A — Research
**Tipo:** Price-action, momentum intraday

---

## 1. Decision Framework 4Q

| Q | Pergunta | Resposta |
|---|----------|----------|
| Q1 | Existe economic rationale? | SIM — inércia de fluxo direcional de dealers + lag USDBRL spot↔futuro. Quem perde: mean-reversion cego sem filtro de regime. |
| Q2 | É falsificável? | SIM — H1 mensurável com IC, p-value, Bonferroni. |
| Q3 | Dataset suporta? | SIM — trades-only 2023-2026 permite agregação OHLCV 5-min. |
| Q4 | Kill criteria ex-ante? | SIM — 3 critérios (DSR<0, PBO>0.5, IC out-of-CI 2 meses). |

Todos 4Q = SIM → prosseguir.

---

## 2. Hipóteses

### H0 (nula)
Sinal momentum baseado em soma dos retornos das últimas 3 barras de 5-min de WDO não tem correlação estatisticamente significativa com o retorno da barra seguinte.

### H1 (alternativa)
IC_spearman entre sinal_momentum(t) e retorno(t+1) ≥ 0.03 com p < 0.01 após correção Bonferroni, em 45 paths CPCV.

---

## 3. Especificação

**Universo:** WDOFUT (vigente), sessão contínua 09:30-17:55 BRT
**Horizonte:** 5 minutos (1 barra à frente)
**Feature primária:** `mom_3bar = sum(log_return[-3:-1])` — janela não-antecipativa
**Label:** `ret_next = log(close[t+1] / close[t])` — triple-barrier opcional na Fase E
**Métrica primária:** IC spearman
**Métricas secundárias:** Sharpe, MAR, max DD, hit rate, profit factor
**Sample size alvo:** ≥ 100 trades no backtest total
**p-value target:** 0.01 pós-Bonferroni (N_trials estimado: 5)

---

## 4. Economic rationale (1 parágrafo)

WDO tem microestrutura dominada por dealers (bancos market makers em USDBRL spot) e fluxos de hedge cambial de exportadores/importadores. Após release de informação (intervenção BCB, CPI Brasil, payroll US, decisão Copom/FOMC), o ajuste de posições em DOL spot leva tempo para refletir no mini via arbitragem — gerando inércia direcional de 5-30 min. Agentes que operam mean-reversion cego sem filtro de regime (ex.: scalpers estatísticos genéricos) perdem para momentum nesse regime. Hipótese NÃO vale em: (a) pré-abertura/leilão de determinação; (b) regime de baixa vol onde inércia colapsa em ruído.

---

## 5. Kill criteria ex-ante

1. **DSR < 0** na CPCV → tese é ruído, descartar
2. **PBO > 0.5** na CPCV → overfitting severo, descartar
3. **IC out-of-CI 95%** em 2 meses seguidos em paper-mode → tese degradou, desligar
4. **Drawdown > 3σ acima do budget Riven** em live → kill imediato (Riven owner)

---

## 6. Consulta Mira (ML viability) — *feature-eval

**Artefato:** [docs/research/audits/T001-mira-audit.md](../audits/T001-mira-audit.md)


- [x] Feature `mom_3bar` é computável com trades-only (agregação OHLCV 5-min por janela temporal)
- [x] Risco de leakage: BAIXO — feature usa apenas close[t-3:t]; label usa close[t+1]
- [x] Sample size estimado: ~12k barras/mês × 30 meses = ~360k observações → overkill, mas aceitável
- [x] CV scheme aplicável: CPCV N=10, k=2, embargo=1 sessão (purging remove labels cruzando folds)

**Mira verdict:** PRELIMINARY-OK

---

## 7. Consulta Nova (microestrutura B3) — *audit-feature

**Artefato:** [docs/research/audits/T001-nova-audit.md](../audits/T001-nova-audit.md)


- [x] Feature faz sentido microestrutural: sim, com ressalva de regime (alta vs baixa vol)
- [x] Fases de pregão: filtro obrigatório — só contínuo 09:30-17:55, EXCLUI pré-abertura (08:55-09:00), leilão de determinação (09:00-09:30) e call de fechamento (17:55-18:00)
- [x] Rollover: janela D-3 a D-1 do vencimento precisa haircut ou exclusão (liquidez migra para próximo contrato)
- [x] RLP/cross/odd-lot: irrelevante para bar close de 5-min (ruído diluído)

**Nova verdict:** AUDIT-OK com constraint de fase + rollover

---

## 8. Consulta Nelo (availability live) — *callback-spec

**Artefato:** [docs/research/audits/T001-nelo-audit.md](../audits/T001-nelo-audit.md)


- [x] Feature computável no callback real-time: SIM — TNewTradeCallback fornece preço + timestamp BRT naive
- [x] Nenhuma dependência de `GetHistoryTrades` no callback (quirk confirmado)
- [x] Orçamento de latência: agregação 5-min é trivial; recomputação rolante cabe em << 100ms
- [x] Availability tag: `computable` (trades-only, feed contínuo)

**Nelo verdict:** LIVE-READY

---

## 9. Gate de saída Fase A

- [x] Q1-Q4: todos SIM
- [x] Thesis revisada por Kira + Mira + Nova + Nelo
- [x] Feature tem `historical_availability = computable`
- [x] Kill criteria ex-ante escritos
- [x] Spec YAML Mira→Beckett a ser exportada (próximo arquivo)

**Verdict:** PASS — liberado para Fase B (Architecture)

---

## 10. Nota de dry-run

Esta thesis é um smoke-test do workflow Q-SDC. Não há compromisso de levar T001 para produção. Objetivo: exercitar todas as fases A-H e detectar gaps no processo antes de discutir tese real com o conselho quant (Kira+Mira+Nova+Nelo+humano).

---

## 11. Gate Signature — Fase A → Fase B (fix G004)

```yaml
gate_A_signature:
  verdict: pass
  signed_by: Kira (@quant-researcher)
  signed_at_brt: "2026-04-21T15:20:00"
  mira_beckett_spec_ref: "docs/ml/specs/T001-bar-close-momentum-wdo-5min-v0.1.0.yaml"
  mira_beckett_spec_hash: "sha256:dry-run-placeholder"  # recalcular quando *export-spec automatizar G002
  consultations_signed:
    mira: "docs/research/audits/T001-mira-audit.md"
    nova: "docs/research/audits/T001-nova-audit.md"
    nelo: "docs/research/audits/T001-nelo-audit.md"
  next_phase: B
  next_owner: Aria (@architect)
```

**Assinatura:** Kira (@quant-researcher) — 2026-04-21 BRT
