# T002 — Nova Audit (Microstructure B3 / *audit-feature)

**Thesis:** T002 — End-of-Day Inventory Unwind WDO
**Owner:** Nova (@market-microstructure)
**Data:** 2026-04-21 BRT
**Comando de origem:** `*audit-feature`

---

## 1. Validação microestrutural do mecanismo

**Claim da tese:** dealers reduzem exposição WDO nos últimos ~60 min para limitar VaR overnight e ajustar hedge contábil → fluxo forçado contra o acúmulo intraday.

**Audit Nova:**

| Ponto | Validação | Evidência microestrutural |
|-------|-----------|---------------------------|
| Dealers carregam inventário intraday | ✅ | Bancos market-makers em USDBRL são contraparte ativa no WDO; bid/ask WDO segue USDBRL spot via arbitragem |
| VaR overnight força redução | ✅ | Regulação Bacen + desks internos tratam overnight como risk category distinta; redução parcial é obrigatória para maioria das mesas |
| Tesourarias corporativas ajustam no fechamento | ✅ (parcial) | Exportadores/importadores com hedge em DOL → mini rebalanceiam posição contábil no EOD; efeito é secundário mas existe |
| Fluxo é contrário ao acúmulo do dia | ⚠️ | Premissa depende de "dealers compraram o que retail vendeu" — válido se fluxo intraday foi direcional (|ret_dia| > P60); em dias laterais não há inventário desbalanceado |

**Conclusão:** mecanismo válido **condicional a magnitude**. Filtro P60 da tese já captura isso. OK.

## 2. Fases de pregão e janelas — constraint canônico

**Sessão contínua WDO:** 09:30 → 17:55 BRT (Nova canônico)
**Call de fechamento:** 17:55 → 18:00 BRT — **EXCLUIR** (leilão, regras de formação diferentes)

Janelas de entrada {16:55, 17:10, 17:25, 17:40} são todas na sessão contínua ✅.
Janela de saída 17:55 é o último ponto antes do call ✅.

**Risco observado:** bar 17:50-17:55 pode ter volatilidade elevada (pre-call positioning). Recomendar Fase E testar sensitividade a saída antecipada em 17:50.

## 3. Rollover

Excluir janela **D-3 a D-1** do vencimento (dia 15 do mês):
- D-3 e D-2: liquidez migra para próximo contrato; preço do vigente pode deslocar
- D-1: último dia de negociação — dinâmica de ajuste final não replica regime normal

Em 27 meses, isso remove ~27 × 3 = 81 dias ≈ 14% dos dias úteis. Mira já considerou no sample size.

## 4. Stress regimes (obrigatório em Fase E — MANIFEST)

Separar métricas em breakdown:

| Regime | Definição | Hipótese |
|--------|-----------|----------|
| Pré-Copom | D-1 de reunião Copom | Unwind amplificado; tese pode intensificar |
| Pós-Copom | D+0 da reunião | Distorcido por repricing macro; REMOVER ou tratar separado |
| Pré-feriado longo | D-1 de feriado BRA com mercado EUA aberto | Unwind forçado pela impossibilidade de carregar overnight prolongado; tese pode intensificar |
| Pré-vencimento | D-3 a D-1 | JÁ EXCLUÍDO |
| Alta vol | ATR_dia > P80 | Ruído domina; tese FALHA esperadamente |
| Baixa vol | ATR_dia < P20 | Sem acúmulo significativo; tese não dispara (filtro) |
| Abertura NY (intraday) | 10:30-11:00 BRT overlap | Não afeta (janela tese é 16:55+) |

Calendário Copom: público (BCB divulga datas). Não é feed externo complexo — uma lista estática por ano resolve.

## 5. Custos (ownership Nova via atlas)

| Componente | Valor | Fonte |
|-----------|-------|-------|
| Multiplier WDO | **R$ 10,00 / ponto** | [WEB-CONFIRMED 2026-04-21] glossário (single-source) |
| Tick size | 0,5 ponto = R$ 5,00 | B3 |
| Emolumentos B3 | ~0,00002 × notional por lado | via atlas Nova (spec usa referência, não número hardcoded) |
| Brokerage | corretora-específico — assumir R$ 0,25/contrato/lado como default conservador | TO-VERIFY com corretora real |
| Slippage modelo | Roll spread + 1 tick worst-case ordem a mercado | Beckett default |
| IR day-trade | 20% lucro líquido (apurado no ledger Beckett) | atlas Nova |

**Regra canônica:** spec YAML NÃO duplica o multiplier (G005 fix). Spec referencia `contract_multiplier_source_ref`; Beckett lê do glossário em runtime.

## 6. Red flags observados

1. **Efeito pode ter sido arbitrado por HFT institucional.** Mitigation: hold-out virgem 2025-07→2026-04 testa recente. Se hold-out IC < 50% in-sample, K3 ativa.
2. **Dias pós-Copom têm dinâmica distinta.** Não são "regime de stress" — são **distribuições diferentes**. Recomendar REMOVER pós-Copom do in-sample (não apenas breakdown).
3. **Fim de mês contábil** (último dia útil) pode ter efeito amplificado OU invertido por fluxo de rebalanceamento de fundos. Testar em Fase E como regime separado.

## 7. Verdict

**AUDIT-OK ✅ com 3 constraints:**
1. REMOVER dias pós-Copom do sample in-sample (não apenas breakdown Fase E)
2. Excluir D-3 a D-1 de vencimento (rollover — já na spec)
3. Testar saída em 17:50 como sensitivity em Fase E (alternativa a 17:55)

**Assinatura:**
Nova (@market-microstructure) — 2026-04-21T17:20:00 BRT
