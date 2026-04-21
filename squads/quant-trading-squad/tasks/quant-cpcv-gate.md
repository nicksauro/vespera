# Task: quant-cpcv-gate

**Fase do workflow:** E (Quant Validation Gate)
**Owner primary:** `@backtester` (Beckett)
**Gate owner:** `@quant-researcher` (Kira)
**Consultores:** `@ml-researcher` (Mira), `@market-microstructure` (Nova)
**Input:** código implementado + Quinn PASS + mira-beckett-spec.yaml
**Output:** `docs/backtests/{feature}-cpcv-{date}.md` com veredito Kira
**Duration estimate:** 2-4 horas de compute + 1 dia de review humano/agente

---

## Propósito

**Gate estatístico distintivo do Q-SDC.** Código correto não basta — alpha tem que ser real sob CPCV + DSR + PBO. Este gate decide se a feature promove para Fase F (risco + paper-mode) ou retorna para Fase A (tese reformulada).

## Pré-condições

- [ ] Task `quant-implement-feature` concluída com Quinn PASS
- [ ] mira-beckett-spec.yaml disponível e assinado
- [ ] Dataset histórico `D:\sentinel_data\historical\` acessível
- [ ] Simulador Beckett calibrado com telemetria mais recente de Tiago (se existe)

## Sequência de execução

### Passo 1 — Beckett roda CPCV completo

Owner: `@backtester` (Beckett)

Command: `*run-cpcv --spec {mira-beckett-spec.yaml} --n 10 --k 2 --embargo 1`

Parâmetros padrão squad (MANIFEST R6):
- N = 10-12 grupos sequenciais
- k = 2 (combinatorial: C(10,2) = 45 paths)
- embargo = 1 sessão (elimina leakage de autocorrelação)
- Purging: remove observações cujas labels cruzam train/test

Durante execução:
- [ ] Custos aplicados (corretagem [TO-VERIFY], emolumentos via atlas Nova, IR day-trade via atlas Nova)
- [ ] Slippage model calibrado com dados mais recentes
- [ ] Latency profile DMA2 aplicado (p50=20ms, p95=60ms, p99=100ms, tail=500ms)
- [ ] Fill rules trades-only aplicadas conforme Parte 10 do GLOSSARY
- [ ] Stress-regime reports: abertura, fechamento, alta vol (ATR > P80), baixa vol (ATR < P20), rollover week

Output: `docs/backtests/{feature}-cpcv-{date}.md` com:
- Distribuição de Sharpe across 45 paths
- Equity curves por path
- Métricas agregadas (mediana, IQR)
- Stress-regime breakdown

### Passo 2 — Mira computa DSR + PBO

Owner: `@ml-researcher` (Mira)

Commands: `*deflate-sharpe --n-trials {N}` + `*overfit-diagnose`

Mira computa:

#### DSR (Deflated Sharpe Ratio)
Fórmula Bailey-Lopez de Prado 2014. Input: Sharpe observado, N_trials (do research log), skew, kurt, sample size.

Critério:
- DSR < 0 → backtest indistinguível de ruído → **FAIL imediato**
- DSR ≥ 0 e DSR < threshold squad → **CONCERNS** (Kira decide no review)
- DSR ≥ threshold → **continua**

#### PBO (Probability of Backtest Overfitting)
Calculado sobre os 45 paths do CPCV.

Critério:
- PBO > 0.5 → overfitting severo → **FAIL**
- PBO 0.3-0.5 → **CONCERNS**
- PBO < 0.3 → **continua**

#### Outras checagens

- [ ] IS vs OOS gap por path: mediana < threshold
- [ ] Rolling Sharpe estável (não colapsa em segundo metade)
- [ ] Performance por regime: não concentrada em um único regime
- [ ] Sample size: ≥ 100 trades no total do backtest

Output: DSR/PBO numbers anotados no backtest doc.

### Passo 3 — Kira peer review final

Owner: `@quant-researcher` (Kira)

Command: `*review {backtest-result}`

Kira aplica checklist rigoroso:

- [ ] Economic rationale ainda faz sentido frente aos resultados?
- [ ] Falsificabilidade: a hipótese H1 foi testada conforme pré-registrada? Nada de p-hacking a posteriori?
- [ ] Out-of-sample protection: fold models genuínos? Embargo adequado?
- [ ] Multiple testing correction aplicada (Bonferroni/FDR)?
- [ ] Kill criteria ex-ante definidos e testáveis nesta estratégia?
- [ ] Sample size ≥ 100 trades?
- [ ] Custos realistas?
- [ ] DSR positivo e acima do threshold?
- [ ] Regime analysis presente?
- [ ] Capacity estimate realística?

Veredito:

| Verdict | Critério | Próxima fase |
|---------|----------|-------------|
| **APPROVED** | todos os checks OK, DSR > threshold, PBO < 0.3 | Fase F (Risk & Paper-mode) |
| **APPROVED_WITH_CHANGES** | passa mas com concerns específicos | Fase F com concerns documentados |
| **REJECTED** | qualquer FAIL do Mira OU qualquer check Kira NO | **Loop back para Fase A** — tese precisa reformulação |

Output: verdict annex no backtest doc + assinatura Kira + data BRT.

## Gate de saída

Para avançar para Fase F:

- [ ] Kira APPROVED ou APPROVED_WITH_CHANGES
- [ ] DSR, PBO, 45-path distribution, stress-regime breakdown todos em `docs/backtests/`
- [ ] Nenhum 🔴 de Sable aberto (se Sable foi acionado)

## Red flags que ABORTAM a task

- CPCV detecta leakage em algum path (OOS performance absurdamente acima do IS) → suspeita de bug → volta para Dex investigar
- PBO > 0.5 → overfitting severo → tese precisa reformulação (Fase A)
- DSR < 0 → tese é ruído → descartar OU reformular features
- Kira identifica violação de economic rationale nos resultados → descartar

## Handoff para próxima task

Próxima task: **[não definida como canônica ainda]** — Fase F (Risk & Paper-mode) é conduzida diretamente por Riven + Tiago sem necessidade de task formalizada (processos Tiago `*paper-mode` e Riven `*sizing` já cobrem).

Após Fase F, vem Fase G (Sable + humano) e Fase H (Gage push). Estas são executadas pelos próprios agentes ao comando do humano quando condições forem atingidas.

## Observação arquitetural

Este gate é **mandatório mesmo quando o código é perfeito** (Quinn PASS). Razão: podemos ter código impecável que implementa tese de alpha inexistente. Este é o princípio "sobrevivência antes de retorno" do MANIFEST aplicado em gate de pipeline. Nenhum atalho.
