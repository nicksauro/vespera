# Sentinel — Documento Mestre do Projeto

**Versão:** 1.0  
**Data:** 2026-04-21  
**Gerado por:** Orion (@aiox-master) — Squad Sentinel  
**Status do projeto:** Pesquisa ativa — Walk-Forward em calibração

---

## Sumário

1. [O que é o Sentinel](#1-o-que-é-o-sentinel)
2. [Ativos e Contratos](#2-ativos-e-contratos)
3. [Arquitetura Técnica](#3-arquitetura-técnica)
4. [Estrutura de Diretórios](#4-estrutura-de-diretórios)
5. [Pipeline de Dados](#5-pipeline-de-dados)
6. [Estratégia — Sistema de 3 Camadas](#6-estratégia--sistema-de-3-camadas)
7. [SmartScore V2 — Como é Calculado](#7-smartscore-v2--como-é-calculado)
8. [Gestão de Risco](#8-gestão-de-risco)
9. [Modelo de Custos](#9-modelo-de-custos)
10. [Validação — Walk-Forward](#10-validação--walk-forward)
11. [Machine Learning — XGBoost](#11-machine-learning--xgboost)
12. [Integração com a ProfitDLL](#12-integração-com-a-profitdll)
13. [Dashboard — Plotly Dash](#13-dashboard--plotly-dash)
14. [Bugs Críticos — Histórico Completo](#14-bugs-críticos--histórico-completo)
15. [Experimentos e Resultados](#15-experimentos-e-resultados)
16. [Estado Atual dos Dados](#16-estado-atual-dos-dados)
17. [Stories e Roadmap](#17-stories-e-roadmap)
18. [Decisões Estratégicas](#18-decisões-estratégicas)
19. [Infraestrutura — Comandos Operacionais](#19-infraestrutura--comandos-operacionais)
20. [Próximos Passos](#20-próximos-passos)

---

## 1. O que é o Sentinel

**Sentinel** é um sistema algorítmico de trading intradiário para minicontratos da B3, baseado em análise de fluxo de ordens em granularidade de 1 segundo.

### Hipótese Central

> Agentes institucionais (fundos, HFTs, market-makers) deixam rastros de agressão direcionada no book antes de movimentos significativos de preço. É possível detectar esses rastros combinando três filtros independentes em cascata e usar essa informação para operar com vantagem estatística.

### Por que fluxo de ordens?

No mercado brasileiro de futuros (B3 — segmento BMF), cada trade tick-a-tick contém o **código do agente comprador e vendedor** — informação que a maioria dos mercados globais não disponibiliza publicamente. Isso permite identificar quais corretoras/fundos estão agredindo o book em tempo real e cruzar com o histórico de acerto direcional de cada agente.

### Foco operacional

- **Ativo principal:** WDO (Mini Dólar) — decisão estratégica em 2026-04-03
- **WIN (Mini Índice):** dados mantidos no banco como referência histórica, sem uso em sinais ou treinamento
- **Granularidade:** barras de 1 segundo
- **Horizon de holding:** segundos a minutos (intradiário puro)

---

## 2. Ativos e Contratos

| Ativo | Nome | Tick | Valor do Tick | Valor por Ponto |
|-------|------|------|---------------|-----------------|
| WIN | Mini Índice Bovespa | 5 pontos | R$ 1,00 | R$ 0,20/ponto |
| WDO | Mini Dólar | 0,5 pontos | R$ 5,00 | R$ 10,00/ponto |

### Vencimentos

WIN e WDO expiram na **3ª quarta-feira de cada mês**. Códigos de mês:

```
F=Jan  G=Feb  H=Mar  J=Apr  K=Mai  M=Jun
N=Jul  Q=Ago  U=Set  V=Out  X=Nov  Z=Dez
```

Exemplos: `WDOJ26` = Mini Dólar Abril 2026 | `WINH26` = Mini Índice Março 2026

### Blackout de Horário (sem operação)

| Janela | Motivo |
|--------|--------|
| 09:00 – 09:10 BRT | Abertura B3 — spread alto, TFI distorcido |
| 15:00 – 15:15 BRT | Abertura NYSE — fluxo externo não modelado |
| Após 17:25 BRT | Fechamento forçado de posições |
| 3ª Quarta-feira do mês | Dia de vencimento WIN/WDO — comportamento atípico |

---

## 3. Arquitetura Técnica

### Stack Completa

```
┌─────────────────────────────────────────────────────────────┐
│                    SENTINEL — STACK                         │
├─────────────┬───────────────────────────────────────────────┤
│ Linguagem   │ Python 3.14                                   │
│ Banco       │ TimescaleDB (PostgreSQL 16 + extensão)        │
│ Container   │ Docker — sentinel-timescaledb                 │
│ ML          │ XGBoost + Platt Scaling (calibração sigmoid)  │
│ Dashboard   │ Plotly Dash (Dash 2.x)                       │
│ DLL         │ ProfitDLL.dll (Nelogica) via ctypes.WinDLL   │
│ OS          │ Windows 10 Pro (compatibilidade com a DLL)   │
└─────────────┴───────────────────────────────────────────────┘
```

### Docker — TimescaleDB

```bash
# Container
nome:  sentinel-timescaledb
porta: 5433 (host) → 5432 (container)

# Conexão
host:     localhost
port:     5433
database: sentinel_db
user:     sentinel
password: sentinel123

# URL completa
postgresql://sentinel:sentinel123@localhost:5433/sentinel_db

# Iniciar
docker start sentinel-timescaledb

# Verificar
docker ps | grep sentinel
```

### Configuração (config.py)

```python
# config.py — valores base
DB_HOST     = "localhost"
DB_PORT     = 5433
DB_NAME     = "sentinel_db"
DB_USER     = "sentinel"
DB_PASSWORD = "sentinel123"

TICKERS  = ["WINFUT", "WDOFUT"]
EXCHANGE = "F"  # B3 BMF — código real (NÃO "BMF")

# config_local.py — gitignored — credenciais reais
ACTIVATION_KEY = "..."   # chave de ativação Nelogica
LOGIN          = "..."   # login Nelogica
PASSWORD       = "..."   # senha Nelogica
DLL_PATH       = r"C:\Users\Pichau\Desktop\profitdll\DLLs\Win64\ProfitDLL.dll"
```

---

## 4. Estrutura de Diretórios

```
sentinel/
├── config.py                    # Configuração base (DB, tickers)
├── config_local.py              # ⚠️ gitignored — credenciais reais
├── requirements.txt
│
├── connector/                   # Integração com ProfitDLL
│   ├── dll_connector.py         # Conector real (DLL via ctypes)
│   ├── mock_connector.py        # Conector mock para testes
│   ├── callbacks.py             # Definição de callbacks WINFUNCTYPE
│   └── base.py                  # Interface abstrata do conector
│
├── strategy/                    # Lógica de trading (não usada no backtest — engine)
│
├── backtest/                    # Motor de backtesting
│   ├── engine_v2.py             # Engine principal — processa barras, aplica 3 camadas
│   ├── signal_evaluator.py      # Avalia L1, L2, L3 para cada barra
│   ├── walk_forward.py          # Walk-forward: janelas treino/teste
│   ├── cost_model.py            # Custos de transação (slippage, corretagem, emolumentos)
│   ├── metrics.py               # Cálculo de métricas (Sharpe, WR, PF, drawdown)
│   └── results/                 # Arquivos de resultado (JSON + CSV por run)
│       ├── wdo_metrics_*.json
│       ├── wdo_trades_*.csv
│       └── progress_WDO.json    # Progresso em tempo real (atualizado por janela)
│
├── ml/                          # Machine learning
│   └── feature_builder.py       # Constrói features para XGBoost a partir de features_1s
│
├── models/                      # Modelos treinados
│   ├── xgboost_wdo_20260313.pkl             # Modelo legado (sem fold)
│   ├── xgboost_wdo_20260320.pkl             # Modelo final (fold models gerados aqui)
│   ├── xgboost_wdo_fold01_20240328.pkl      # Fold 1 — cobre a partir de Mar/2024
│   ├── xgboost_wdo_fold02_20240513.pkl
│   ├── ...                                  # fold03 → fold15
│   ├── xgboost_wdo_fold16_20260115.pkl      # Fold 16 — cobre a partir de Jan/2026
│   ├── xgboost_win_20260313.pkl             # WIN — descartado (WDO-only)
│   └── fold_manifest_wdo_20260320.json      # Manifesto: qual fold usar por data
│
├── scripts/                     # Scripts utilitários e de pipeline
│   ├── ingest_historical.py     # Ingestão histórica via DLL (GetHistoryTrades)
│   ├── ingest_from_parquets.py  # Ingestão de parquets locais
│   ├── batch_smart_money_backfill.py  # Backfill agent_scores dia a dia
│   ├── calc_smart_money_v2.py   # Calcula SmartScore para um único dia
│   ├── backfill_close_price.py  # Refresh do continuous aggregate close_price_1s
│   ├── train_ml_v2.py           # Treinamento XGBoost (suporta --fold-models)
│   ├── run_backtest_v2.py       # Roda backtest (suporta --fold-manifest)
│   ├── pipeline_r2_to_r4.py     # Pipeline automático: backfill → retrain → backtest
│   ├── run_full_pipeline.py     # Pipeline completo
│   ├── validate_pipeline.py     # Validação do estado dos dados
│   ├── analyze_backtest_results.py  # Análise de resultados
│   └── gates/                   # Gate scripts de qualidade
│       ├── gate_r2_agent_scores.py
│       ├── gate_r3_ml_retrain.py
│       └── gate_r4_backtest.py
│
├── dashboard/                   # Plotly Dash — interface visual
│   ├── app.py                   # Entry point (--mode backtest|live, --refresh-ms)
│   ├── db.py                    # Queries ao TimescaleDB
│   ├── layout.py                # Layout do dashboard (grid responsivo)
│   ├── callbacks.py             # Callbacks Dash (backtest + live)
│   ├── progress_bridge.py       # Bridge para progresso em tempo real do backtest
│   ├── components/
│   │   ├── position_card.py     # Card de posição aberta
│   │   ├── tfi_chart.py         # Mini gráfico TFI com threshold
│   │   ├── strategy_badge.py    # Badge OPERANDO/AGUARDANDO/FORA DO HORÁRIO
│   │   ├── top_players.py       # Ranking de agentes (cards inline-styled)
│   │   └── error_banner.py      # Banner DB offline
│   └── assets/
│       └── sentinel.css         # Estilos (precedência menor que inline styles)
│
├── docs/                        # Documentação
│   ├── SENTINEL_MASTER_DOCUMENT.md    # Este arquivo
│   ├── SENTINEL_TECHNICAL_BRIEFING.md
│   ├── SQUAD_UPDATE_APR07_2026.md
│   ├── REVISAO_COMPLETA_SQUAD.md
│   └── stories/                 # User stories do projeto
│       ├── 1.1.story.md → 6.2.story.md
│       └── R1.story.md → R4.story.md (revisão de dados)
│
├── tests/                       # Testes automatizados
├── data/                        # Dados locais (parquets históricos)
├── logs/                        # Logs de execução
└── profitdll-knowledge.md       # Quirks e API da ProfitDLL (referência técnica)
```

---

## 5. Pipeline de Dados

### Fluxo Completo

```
B3 (trades raw via DLL)
        │
        ▼
┌───────────────────────────────────────┐
│  tabela: trades                       │
│  tick-by-tick completo                │
│  campos: timestamp, ticker, price,    │
│          qty, buy_agent, sell_agent,  │
│          aggressor                    │
│  cobertura WDO: 2024-01-02 →         │
│                 2026-04-01 ✅         │
│  índice único: (ticker, timestamp,    │
│                trade_number)          │
└───────────────────────────────────────┘
        │
        ├──────────────────────────────────────────────────────┐
        │                                                      │
        ▼                                                      ▼
┌──────────────────────────────┐   ┌──────────────────────────────────┐
│  features_1s                 │   │  netflow_agent_1s                │
│  continuous aggregate (1s)   │   │  continuous aggregate (1s)       │
│  OHLCV + TFI + VWAP          │   │  net_flow = Σbuy - Σsell         │
│  por ativo por segundo        │   │  por agente por segundo          │
│  WDO: 2024-01-02 →           │   │  WDO: 2024-01-02 →               │
│       2026-04-01 ✅           │   │       2026-04-01 ✅               │
│  ~16.4M barras               │   │  base para SmartScore            │
└──────────────────────────────┘   └──────────────────────────────────┘
        │                                       │
        │                                       │
        │              ┌────────────────────────┘
        │              │
        │              ▼
        │    ┌──────────────────────────────────┐
        │    │  close_price_1s                  │
        │    │  continuous aggregate (1s)        │
        │    │  LAST(price, ts) por segundo      │
        │    │  usado em KLA (Kyle's Lambda)     │
        │    │  WDO: completo ✅                 │
        │    └──────────────────────────────────┘
        │              │
        │              ▼
        │    ┌──────────────────────────────────┐
        │    │  agent_scores (diário)            │
        │    │  SmartScore por agente por dia    │
        │    │  janela rolante 20 dias úteis     │
        │    │  calculado por                   │
        │    │  batch_smart_money_backfill.py    │
        │    │  WDO: 524 datas ✅               │
        │    │  (2024-01-02 → 2026-04-02)        │
        │    └──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────┐
│  Engine / Backtester         │
│  lê features_1s +            │
│  netflow_agent_1s +          │
│  agent_scores                │
│  → aplica L1 → L2 → L3      │
│  → emite sinal / trade       │
└──────────────────────────────┘
```

### Schema das Tabelas Principais

#### `trades` — Tabela base (hypertable TimescaleDB)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `timestamp` | `TIMESTAMPTZ` | Timestamp do trade em BRT |
| `ticker` | `VARCHAR(10)` | `WINFUT` ou `WDOFUT` |
| `price` | `DECIMAL(10,2)` | Preço do trade |
| `qty` | `INTEGER` | Quantidade de contratos |
| `buy_agent` | `INTEGER` | ID numérico do agente comprador |
| `sell_agent` | `INTEGER` | ID numérico do agente vendedor |
| `aggressor` | `VARCHAR(4)` | `BUY` ou `SELL` |
| `trade_number` | `BIGINT` | Número único do trade (da DLL) |

> **Índice único:** `(ticker, timestamp, trade_number)` — `ON CONFLICT DO NOTHING` permite reprocessar sem duplicatas.

#### `features_1s` — Continuous Aggregate (1s)

| Coluna | Descrição |
|--------|-----------|
| `ts` | Timestamp truncado ao segundo |
| `ticker` | Ativo |
| `open`, `high`, `low`, `close` | OHLC da barra |
| `volume` | Volume total |
| `buy_vol`, `sell_vol` | Volume por lado agressor |
| `tfi` | Trade Flow Imbalance = `buy_vol - sell_vol` |
| `vwap` | Volume Weighted Average Price acumulado do dia |
| `trades_count` | Número de trades na barra |

#### `netflow_agent_1s` — Continuous Aggregate (1s)

| Coluna | Descrição |
|--------|-----------|
| `ts` | Timestamp truncado ao segundo |
| `ticker` | Ativo |
| `agent_id` | ID do agente |
| `net_flow` | `Σbuy_qty - Σsell_qty` para este agente neste segundo |

#### `agent_scores` — Tabela calculada (diário)

| Coluna | Descrição |
|--------|-----------|
| `data_calculo` | Data do score (D) |
| `ticker` | Ativo |
| `agent_id` | ID do agente |
| `hrd` | Hit Rate Direcional (raw) |
| `pra` | PnL Realizado Ajustado (raw) |
| `kla` | Kyle's Lambda por Agente (raw) |
| `smart_score` | Score composto normalizado |

> **Nota crítica:** `smart_score` está centrado em 0 com range aproximado de -4.4 a +3.96. **NÃO é uma escala 0–1.** O threshold de 0.75 para L2 usa essa escala (equivale a aproximadamente 1.5 desvios padrão acima da média).

---

## 6. Estratégia — Sistema de 3 Camadas

A execução de uma ordem requer aprovação **sequencial e obrigatória** das 3 camadas. É um **AND lógico em cascata** — qualquer falha encerra o sinal naquele segundo.

```
Barra 1s → [L1: TFI Spike] ──falha──► IGNORA
                │ aprovado
                ▼
           [L2: Smart Money] ──falha──► IGNORA
                │ aprovado
                ▼
           [L3: XGBoost] ──falha──► IGNORA
                │ aprovado
                ▼
           EXECUTA ORDEM
```

---

### Camada 1 — Trade Flow Imbalance (TFI)

**O que detecta:** Desequilíbrio estatisticamente significativo entre agressores compradores e vendedores.

**Cálculo:**

```
TFI(t)      = buy_volume(t) − sell_volume(t)

std_TFI     = desvio_padrão(TFI, últimas 300 barras = 5 minutos)
threshold   = 2.0 × std_TFI

Sinal BUY:  TFI(t) >  +threshold  → pressão de compra anormal
Sinal SELL: TFI(t) < −threshold   → pressão de venda anormal
```

**Interpretação econômica:**
- `buy_volume` = contratos executados por agressores que bateram no ask
- `sell_volume` = contratos executados por agressores que bateram no bid
- O z-score (TFI / std) normaliza pelo contexto de volatilidade do momento

**Parâmetros:**

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `tfi_std_multiplier` | 2.0 | Threshold em desvios padrão |
| `tfi_window_seconds` | 300 | Janela de 5 minutos para std |
| `min_bars_before_signal` | 30 | Aguarda 30s de histórico antes de emitir |

---

### Camada 2 — Smart Money Confirmation

**O que detecta:** Presença de um agente com histórico comprovado de bom timing agredindo na mesma direção do sinal L1 nos últimos 5 segundos.

**Cálculo:**

```python
# Para cada agente nos últimos L2_LOOKBACK_SECONDS = 5s:
recent_aggressors = {
    agent_id: smart_score[agent_id]
    for agent_id, net_flow in netflow_agent_1s[-5s:]
    if (sinal == "BUY"  and net_flow > 0) or
       (sinal == "SELL" and net_flow < 0)
}

L2_aprovado = any(score >= 0.75 for score in recent_aggressors.values())
```

**Por que isso tem alpha:**
Agentes com alto SmartScore são corretoras/fundos cujas agressões historicamente precedem movimentos favoráveis. Eles podem ser HFTs com acesso a dados OTC, fundos com order flow proprietário, ou market-makers que giram posição antes de movimentos.

**Parâmetros:**

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| `smart_score_min` | 0.75 | Score mínimo para qualificar |
| `layer2_lookback_seconds` | 5 | Janela de busca de agressores recentes |

**Taxa de filtragem observada:** L2 rejeita ~99.16% dos sinais L1 (apenas 0.84% dos disparos L1 passam para L3). Isso é esperado — a combinação TFI spike + smart money na mesma direção é rara.

---

### Camada 3 — XGBoost Probability Gate

**O que detecta:** Contexto favorável para execução baseado em features de mercado atuais.

**Modelo:** XGBoost com Platt Scaling (calibração isotônica sigmoidal)

**Features (8):**

| Feature | Fonte | Descrição |
|---------|-------|-----------|
| `tfi` | `features_1s` | TFI bruto da barra atual |
| `tfi_zscore` | calculado | `(tfi - mean_300s) / std_300s` |
| `cumulative_delta` | calculado | Delta acumulado desde abertura do pregão |
| `smart_score_max` | `agent_scores` | Maior SmartScore entre agentes ativos no L2 |
| `smart_score_mean` | `agent_scores` | Média dos SmartScores ativos |
| `vwap_dist` | `features_1s` | `(close - vwap) / close` — distância à VWAP diária |
| `bar_volume` | `features_1s` | Volume total da barra em contratos |
| `time_of_day` | calculado | Segundos desde 09:00 BRT |

**Target (variável alvo):**
```
label = 1 se |Δclose(t+60s)| > 0.5 ponto na direção correta (WDO)
label = 0 caso contrário
```

**Threshold de execução:**
```
prob >= threshold_do_fold (normalmente 0.50) → L3 aprovado → executa
prob <  threshold_do_fold                    → L3 rejeitado → ignora
```

> **Nota sobre threshold:** O threshold global do config era 0.65, calibrado para modelos com AUC > 0.70. Os fold models têm AUC ~0.55 e geram probs em torno de 0.50–0.55 — nunca chegam a 0.65. Cada fold model carrega seu próprio `predictor.threshold = 0.50` que é usado diretamente.

---

## 7. SmartScore V2 — Como é Calculado

O SmartScore é calculado pelo `calc_smart_money_v2.py` e armazenado em `agent_scores`. Para cada data D, usa uma janela rolante dos últimos 20 dias úteis.

### Três Componentes

#### HRD — Hit Rate Direcional

> Para cada trade agressivo do agente nos últimos 20 dias, verifica se o preço se moveu na direção correta 60 segundos após a agressão.

```
HRD = acertos_direcionais / total_agressões
```

#### PRA — PnL Realizado Ajustado

> PnL médio por contrato se o agente tivesse mantido a posição por 60 segundos, normalizado pelo ATR do período.

```
PRA = mean(Δprice_60s) / ATR(20d)
```

#### KLA — Kyle's Lambda por Agente

> Impacto de preço do agente — regressão linear do net_flow do agente contra a variação de preço. Mede o "market impact" — agentes com KLA alto movem o mercado.

```
ΔPrice(t, t+60s) ~ α + λ × NetFlow_agente(t)
KLA = coeficiente λ
```

Requer `close_price_1s` para calcular `ΔPrice`. Esse era o **Gap Crítico #1** que bloqueou o backfill até 2026-03-31.

### Score Composto

```
HRD_z = (HRD - media_todos) / std_todos     # Z-Score entre todos os agentes
PRA_z = (PRA - media_todos) / std_todos
KLA_z = (KLA - media_todos) / std_todos

SmartScore = 0.4 × HRD_z + 0.3 × PRA_z + 0.3 × KLA_z
```

### Por que o score não é 0–1

O SmartScore é uma combinação de Z-Scores — por construção, tem média 0 e desvio padrão ~1 entre todos os agentes. O range observado no histórico WDO é de aproximadamente **-4.4 a +3.96**.

O threshold de 0.75 para L2 significa: agente está ~0.75 desvios padrão acima da média histórica — top ~22% dos agentes.

---

## 8. Gestão de Risco

### Sizing

- **1 contrato por operação** (máximo conservador para Day 1 de produção)
- **1 posição aberta por vez** (sem pirâmide, sem médio)

### Stop Loss e Take Profit

**Base:** ATR das últimas 300 barras de 1s (5 minutos de mercado)

```
ATR(5min)   = média(True Range, últimas 300 barras de 1s)

Stop Loss   = entry ± (ATR × 2.0)
Take Profit = entry ± (ATR × 3.0)   →  Risco : Retorno = 1 : 1.5
```

**Exemplo prático WDO (ATR = 10 pontos = R$100):**
```
Entry:  5.847
Stop:   5.847 - (10 × 2.0) = 5.827  →  risco = R$200
Take:   5.847 + (10 × 3.0) = 5.877  →  ganho = R$300
```

### Fechamento Forçado

Qualquer posição aberta às **17:25 BRT** é encerrada ao preço de mercado independente do resultado.

### Break-even de Win Rate

```
Relação R:R = 1:1.5  →  win rate mínimo para break-even bruto = 1/(1+1.5) = 40%

Com custos WDO (R$13,90 round-trip) e take típico ~R$300:
win rate necessário com custos ≈ 44%
```

**Estado atual:** Win Rate de 43–44% — **marginalmente abaixo** do break-even com custos. Esse é o problema fundamental identificado.

---

## 9. Modelo de Custos

### WIN — Mini Índice

| Componente | Cálculo | Valor (1 contrato, WIN=128.000) |
|------------|---------|--------------------------------|
| Slippage entrada | 1 tick × R$0,20 | R$ 1,00 |
| Slippage saída | 1 tick × R$0,20 | R$ 1,00 |
| Corretagem (entrada+saída) | 2 × R$0,50 | R$ 1,00 |
| Emolumentos B3 (2×) | 128.000 × R$0,20 × 0,002% × 2 | R$ 0,10 |
| **Total round-trip** | | **≈ R$ 2,42** |

### WDO — Mini Dólar

| Componente | Cálculo | Valor (1 contrato, WDO=5.800) |
|------------|---------|-------------------------------|
| Slippage entrada | 1 tick × R$5,00 | R$ 5,00 |
| Slippage saída | 1 tick × R$5,00 | R$ 5,00 |
| Corretagem (entrada+saída) | 2 × R$0,50 | R$ 1,00 |
| Emolumentos B3 (2×) | 5.800 × R$10,00 × 0,0025% × 2 | R$ 2,90 |
| **Total round-trip** | | **≈ R$ 13,90** |

### Break-even em Pontos

- WIN: mínimo **12 pontos** (sem slippage adicional)
- WDO: mínimo **1.4 pontos** para cobrir custos

---

## 10. Validação — Walk-Forward

### Por que Walk-Forward?

Evita data snooping — cada janela de teste é genuinamente out-of-sample. Simula a realidade operacional: modelo treinado em dados passados, testado em dados futuros.

### Configuração de Janelas (WDO)

```
Período total: 2024-01-02 → 2026-03-21  (~560 dias úteis)

Configuração:
  Treino:  60 dias calendário
  Teste:   30 dias calendário
  Step:    30 dias (avanço da janela)
  Janelas: 24 (run atual)

W1:  treino 2024-01-02→03-02  | teste 2024-03-02→04-01
W2:  treino 2024-02-01→04-01  | teste 2024-04-01→05-01
...
W24: treino 2025-12-xx→02-xx  | teste 2026-01-21→02-21
```

### Métricas por Janela

- PnL líquido (após custos)
- Sharpe Ratio
- Win Rate
- Profit Factor
- Max Drawdown (R$ e %)
- `l1_fired`, `l2_fired`, `l3_fired` (contadores do funil)
- Exit reasons: STOP / TAKE / FORCE_CLOSE

### Fold Models — Arquitetura Anti-Look-Ahead

A partir de 2026-04-06, o backtest usa **modelos fold-específicos**: cada janela de teste usa um modelo treinado apenas com dados anteriores àquela janela. O `fold_manifest_wdo_20260320.json` mapeia cada data para o fold correto.

```json
// fold_manifest_wdo_20260320.json (estrutura)
{
  "fold_01": {
    "model_file": "xgboost_wdo_fold01_20240328.pkl",
    "train_end": "2024-03-28",
    "threshold": 0.500
  },
  ...
  "fold_16": {
    "model_file": "xgboost_wdo_fold16_20260115.pkl",
    "train_end": "2026-01-15",
    "threshold": 0.500
  }
}
```

---

## 11. Machine Learning — XGBoost

### Hiperparâmetros

```yaml
n_estimators:     200
max_depth:        5
learning_rate:    0.05
subsample:        0.8
colsample_bytree: 0.8
calibration:      Platt Scaling (sigmoid)
```

### Histórico de Treinamentos

| Data | Folds | AUC médio | Arquivo | Manifesto |
|------|-------|-----------|---------|-----------|
| Mar 31, 11:53 | 6 | 0.567 | `xgboost_wdo_20260313.pkl` | ❌ |
| Apr 05, 12:51 | 7 | 0.564 | `xgboost_wdo_20260320.pkl` | ❌ |
| **Apr 06, 20:22** | **16** | **0.556** | `xgboost_wdo_fold01→16` | **✅** |

O treinamento de Apr 06 foi o primeiro a gerar:
1. Modelos individuais por fold sem look-ahead
2. O manifesto `fold_manifest_wdo_20260320.json`
3. Cobertura temporal completa: fold1 cobre 2024-03-28, fold16 cobre 2026-02-27

### Resultados por Fold (Retrain Apr 05 — WDO)

| Fold | Período Teste | AUC-ROC | Viável |
|------|--------------|---------|--------|
| F1 | ~2025-04→05 | 0.552 | ✅ |
| F2 | ~2025-05→06 | 0.550 | ✅ |
| F3 | ~2025-06→07 | 0.578 | ✅ |
| F4 | ~2025-07→08 | 0.580 | ✅ |
| F5 | ~2025-08→09 | 0.572 | ✅ |
| F6 | ~2025-09→10 | 0.568 | ✅ |
| F7 | ~2025-10→2026-03 | 0.549 | ✅ |
| **Média** | | **0.564** | **7/7** |

**Critério de viabilidade:** AUC-ROC > 0.55 em ≥ 2 folds (definido em `config/ml.yaml`)

### Problema de Distribuição (identificado)

O modelo treinado em Jan–Mar 2026 e aplicado em 2024 sofre **distribution shift**: as probabilidades geradas caem sistematicamente abaixo de 0.500 em janelas antigas porque o regime de mercado de 2024 é diferente. Isso bloqueou 100% dos sinais em W1 do backtest antes da implementação dos fold models.

**Solução:** arquitetura fold-específica — cada fold usa o modelo treinado com dados anteriores àquela janela.

---

## 12. Integração com a ProfitDLL

### Localização

```
C:\Users\Pichau\Desktop\profitdll\DLLs\Win64\ProfitDLL.dll
```

### Quirks Críticos (descobertos em produção)

| Errado | Correto | Motivo |
|--------|---------|--------|
| `DLLInitialize` | `DLLInitializeMarketLogin` | Função com esse nome não existe |
| `DLLFinalize` | `Finalize` | Idem |
| `CFUNCTYPE` | `WINFUNCTYPE` | DLL usa `__stdcall`, não `cdecl` |
| `c_char_p` | `c_wchar_p` | DLL usa UTF-16, não ASCII |
| `"BMF"` como exchange | `"F"` | Código real da B3 BMF é `"F"` |
| `WINFUT`/`WDOFUT` em GetHistoryTrades | `WINJ26`, `WDOJ26` (contrato vigente) | `WINFUT` retorna 0 trades no histórico |

### Inicialização

```python
import ctypes
from ctypes import WINFUNCTYPE, c_wchar_p, c_int, c_double, c_uint, c_wchar

dll = ctypes.WinDLL(r"C:\Users\Pichau\Desktop\profitdll\DLLs\Win64\ProfitDLL.dll")

dll.DLLInitializeMarketLogin.argtypes = [
    c_wchar_p,   # activation_key  ← 1º argumento, obrigatório
    c_wchar_p,   # user
    c_wchar_p,   # password
    c_void_p,    # state_cb         ← TStateCallback
    c_void_p,    # trade_cb         ← TNewTradeCallback
    c_void_p,    # daily_cb
    c_void_p,    # price_book_cb
    c_void_p,    # offer_book_cb
    c_void_p,    # history_cb       ← slot 9 — NUNCA chamar SetHistoryTradeCallback depois
    c_void_p,    # progress_cb
    c_void_p,    # tiny_book_cb
]
dll.DLLInitializeMarketLogin.restype = c_int  # 0 = NL_OK

ret = dll.DLLInitializeMarketLogin(
    ACTIVATION_KEY, LOGIN, PASSWORD,
    _state_cb, _trade_cb, _noop_daily,
    _noop_pbook, _noop_obook, _noop_history,
    _noop_prog, _noop_tiny,
)
assert ret == 0, f"Init falhou: {ret}"
```

### TStateCallback — Estados de Conexão

```python
StateCallbackType = WINFUNCTYPE(None, c_int, c_int)

@StateCallbackType
def on_state(conn_type: int, result: int):
    # conn_type: 0=DLL interno, 1=MarketData, 2=Trading
    # result:    0=desconectado, 1=conectado, 2=logado, 3=erro
    if result == 2 and conn_type in (1, 2):
        login_event.set()  # ← condição de login pronto
```

**Sequência normal na inicialização:**
1. `(0, 0)` — DLL desconectado
2. `(1, 1)` — MarketData conectando
3. `(1, 2)` — MarketData logado → **liberar engine**

### TNewTradeCallback — Trades em Tempo Real (~24.5/s WIN+WDO)

```python
NewTradeCallbackType = WINFUNCTYPE(
    None,
    TAssetID,   # assetId — (ticker, bolsa, feed)
    c_wchar_p,  # date: "DD/MM/YYYY HH:MM:SS:mmm" — timezone BRT
    c_uint,     # tradeNumber
    c_double,   # price
    c_double,   # vol  ← volume FINANCEIRO em reais (não contratos!)
    c_int,      # qtd  ← quantidade de contratos
    c_int,      # buyAgent  (ID numérico)
    c_int,      # sellAgent (ID numérico)
    c_int,      # tradeType: 2=compra agressão, 3=venda agressão
    c_wchar,    # bIsEdit: '1'=edição, '0'=novo trade
)

trade_queue = queue.Queue(maxsize=20_000)

@NewTradeCallbackType
def on_trade(assetId, date, tradeNum, price, vol, qtd,
             buyAgent, sellAgent, tradeType, bIsEdit):
    # ⚠️ NUNCA chamar DLL aqui — thread da DLL
    # ✅ Enfileirar e processar na engine thread
    trade_queue.put_nowait({
        'ticker':        'WIN' if 'WIN' in (assetId.ticker or '') else 'WDO',
        'timestamp':     datetime.strptime(date[:23], "%d/%m/%Y %H:%M:%S:%f"),
        'price':         price,
        'quantity':      int(qtd),
        'buy_agent_id':  buyAgent,
        'sell_agent_id': sellAgent,
        'aggressor':     'BUY' if tradeType == 2 else 'SELL',
        'is_edit':       bIsEdit == '1',
    })
```

> **Parsing de timestamp:** formato exato `"DD/MM/YYYY HH:MM:SS:mmm"` (23 chars). Timezone BRT — **não converter para UTC**.

### Estrutura TAssetID

```python
class TAssetID(Structure):
    _fields_ = [
        ("ticker", c_wchar_p),  # "WINFUT", "WDOFUT"
        ("bolsa",  c_wchar_p),  # "F" = BMF
        ("feed",   c_int),      # 0 = Nelogica
    ]
```

### Modelo de Threading

```
[DLL thread — callbacks __stdcall]
        │  put_nowait()
        ▼
  trade_queue (Queue, maxsize=20_000)   ← thread-safe por design
        │  get(timeout=0.05)
        ▼
[Engine thread — processamento]
  ├── resolve_agent(buy_agent_id)   ← GetAgentName é seguro aqui
  ├── resolve_agent(sell_agent_id)
  ├── atualiza janelas deslizantes
  ├── L1 → L2 → L3
  └── INSERT no TimescaleDB
```

**Regra de ouro:** callbacks executam na thread da DLL — jamais bloquear, jamais chamar a DLL de dentro de um callback.

### Resolução de Nomes de Agentes

```python
# V2 — recomendado (buffer controlado)
short_flag = 0  # 0=nome completo, 1=nome curto
length = dll.GetAgentNameLength(agent_id, short_flag)   # 2 args obrigatórios!
buf    = ctypes.create_unicode_buffer(length + 1)        # +1 para null terminator
dll.GetAgentName(length, agent_id, buf, short_flag)     # length PRIMEIRO
name   = buf.value

# Cache para evitar chamadas repetidas
_agent_cache: dict[int, str] = {}
def resolve_agent(agent_id: int) -> str:
    if agent_id not in _agent_cache:
        _agent_cache[agent_id] = dll.GetAgentNameByID(agent_id) or f"Agent#{agent_id}"
    return _agent_cache[agent_id]
```

### Subscriptions e Ciclo de Vida

```python
# Login feito → subscrever
dll.SubscribeTicker("WINFUT", "F")
dll.SubscribeTicker("WDOFUT", "F")

# Ao encerrar
dll.Finalize()   # ← função correta (não DLLFinalize)

# Manter referências vivas (CRÍTICO — evita GC)
_cb_refs = [_state_cb, _trade_cb, _noop_daily, ...]
```

### GetHistoryTrades — Comportamento Confirmado

O ciclo normal de entrega de 1 dia histórico:

1. `GetHistoryTrades` chamado → `ret=0` (NL_OK)
2. `progress` dispara: 0% → 96% → 97% → 98% → 99% com `buffer=0` — **NORMAL, não matar o processo**
3. DLL cicla conexão: `(0,0)` → reconecta → `(2,4)`
4. Após 1–3 reconexões (30s–5min), trades chegam via `_on_history_trade`
5. `progress=100%` com `buffer=<N>` → download completo

**Limitações confirmadas:**
- Chunk máximo de **1 dia para WIN** (volume alto ~7.5M trades/dia — chunks maiores causam 99% eterno)
- Chunk de até **5 dias para WDO** (volume ~500K–1M trades/dia)
- Timeout mínimo: **1800s (30 min)** por chunk
- `WINFUT`/`WDOFUT` retornam 0 trades no histórico — usar contrato vigente (`WINJ26`, `WDOJ26`)

### Frequências de Eventos

| Evento | Callback | Frequência (WIN+WDO simultâneos) |
|--------|----------|----------------------------------|
| Trades em tempo real | `TNewTradeCallback` | ~24.5/s |
| Melhor bid/ask | `TNewTinyBookCallBack` | ~50/s |
| Livro de preços | `TPriceBookCallback` | ~100/s |
| OHLCV diário | `TNewDailyCallback` | 1x ao fim do pregão |
| Estado da conexão | `TStateCallback` | 3 eventos na inicialização |

---

## 13. Dashboard — Plotly Dash

### Como Iniciar

```bash
cd C:\Users\Pichau\Desktop\sentinel

# Modo backtest (análise histórica)
python dashboard/app.py --mode backtest --start 2024-01-02 --end 2026-04-02

# Modo live (pregão em tempo real)
python dashboard/app.py --mode live

# Modo live com refresh customizado
python dashboard/app.py --mode live --refresh-ms 2000

# Acesse:
http://localhost:8050

# Hard refresh (limpa cache CSS do Dash):
Ctrl+Shift+R no browser
```

### Painéis — Modo Backtest

| Painel | Descrição |
|--------|-----------|
| Equity Curve | PnL acumulado janela a janela |
| Funil L1→L2→L3 | Quantos sinais passaram em cada camada |
| Top Players | Ranking de agentes por frequência ≥ SmartScore 0.75 (cards com barras de progresso coloridas) |
| Trades Table | Histórico de trades com entry, exit, PnL, motivo de saída |
| Métricas resumo | WinRate, Sharpe, PnL total, max drawdown |

### Painéis Adicionais — Modo Live

| Painel | Descrição |
|--------|-----------|
| Posição Aberta | Direção (COMPRADO/VENDIDO), entry, stop, take, PnL flutuante |
| TFI Spike | Mini gráfico das últimas 300 barras com threshold line |
| Badge de Status | 🟢 OPERANDO / 🟡 AGUARDANDO / ⚫ FORA DO HORÁRIO / 🔴 HORÁRIO PROIBIDO |
| Relógio | BRT em tempo real (atualiza mesmo com DB offline) |

### Notas Técnicas do Dashboard

- **Polling 1s:** `dcc.Interval(interval=1000)` — Dash não tem WebSocket nativo; o polling é equivalente para granularidade de 1s
- **Top Players:** reescrito com cards HTML 100% inline-styled (sem dependência de CSS externo) — evita o problema de cache agressivo do Dash que impedia renderização das barras de progresso
- **Separação de intervals:** o relógio usa um `dcc.Interval` separado do interval de dados — continua mostrando hora mesmo com DB offline
- **PnL flutuante WDO:** `(close_atual - entry_price) × n_contratos × 10.0` (1 ponto WDO = R$10)

---

## 14. Bugs Críticos — Histórico Completo

### Bug #1 — `_load_agent_scores` sem filtro de ticker (CRÍTICO — descoberto 2026-03-31)

**Sintoma:** L2 aprovava trades baseado em scores de todos os tickers misturados (WIN + WDO juntos).

**Impacto:** L2 não filtrava nada de útil. Win Rate de 18–20% era resultado de L2 inoperante, não da estratégia. Todos os backtests antes de 2026-04-04 são inválidos por este motivo.

**Prova:** Após o fix, L2 passou a rejeitar 99.16% dos sinais L1 (vs 0% antes). W1 pós-fix: 54 trades/mês vs 18.724 antes; WR=50% vs 18.6%.

**Arquivo corrigido:** `backtest/engine_v2.py` — query de `agent_scores` passou a filtrar por `ticker`.

---

### Bug #2 — `agent_scores` com apenas 3 datas (CRÍTICO — descoberto 2026-03-31)

**Sintoma:** A tabela `agent_scores` tinha apenas 3 registros (2025-01-01, 2025-12-16, 2026-03-31). O script `calc_smart_money_v2.py` nunca foi rodado em modo batch histórico.

**Impacto:** Features L3 `smart_score_max` e `smart_score_mean` eram essencialmente constantes em todo o histórico. XGBoost treinado com features constantes → AUC = 0.508 (equivalente a aleatório). Todos os backtests com L3 antes de 2026-04-05 são inválidos.

**Correção:** `batch_smart_money_backfill.py` — calcula scores dia a dia para todo o histórico. Resultado: WDO com 524 datas (2024-01-02 → 2026-04-02).

---

### Bug #3 — L3 usando threshold do config em vez do threshold do fold (CRÍTICO — descoberto 2026-04-06)

**Sintoma:** Os fold models têm threshold=0.50, mas `signal_evaluator.py` usava sempre o threshold do config global (`layer3_min_probability: 0.65`). Os folds geravam probs em torno de 0.50–0.55 — nunca chegavam a 0.65 → **0 trades em janelas com fold models reais**.

**Arquivo:** `backtest/signal_evaluator.py`

**Antes:**
```python
def evaluate_layer3(self, predictor=None, features=None):
    prob = predictor.predict(features or {})
    return prob >= self.l3_min_prob, prob  # ← sempre 0.65 do config
```

**Depois:**
```python
def evaluate_layer3(self, predictor=None, features=None):
    prob = predictor.predict(features or {})
    return prob >= predictor.threshold, prob  # ← 0.50 do fold
```

**Impacto após fix:** L3 passou a filtrar ~63% dos sinais L2 (fold models conservadores mas funcionais).

---

### Bug #4 — `close_price_1s` com apenas 90 dias materializados (CRÍTICO — descoberto 2026-03-31)

**Sintoma:** O continuous aggregate `close_price_1s` tinha apenas ~58 dias materializados (2025-12-17 → 2026-03-16). Como `calc_smart_money_v2.py` depende de `close_price_1s` via INNER JOIN para calcular KLA, qualquer data anterior a 2025-12-17 retornava "Sem trades no período" e não gerava score.

**Correção:** `backfill_close_price.py` — refresh completo do continuous aggregate para 2025-02-17 → 2026-03-20. Executado em ~5-10 minutos (apenas materializa dados já existentes em `trades`).

---

### Bug #5 — `max_drawdown_pct` sempre 0.0 com equity negativa

**Sintoma:** Quando a equity curve ficava negativa, o cálculo de drawdown percentual retornava 0.0 por divisão por zero ou denominador negativo.

**Correção:** `backtest/metrics.py` — usa valor absoluto do equity mínimo como denominador.

---

### Bug #6 — Funil L1→L2→L3 sem contadores de rejeição

**Sintoma:** Impossível diagnosticar qual camada estava rejeitando sinais durante o desenvolvimento.

**Correção:** `engine_v2.py` + `walk_forward.py` — exportam contadores reais `l1_fired`, `l2_fired`, `l3_fired` por janela nos arquivos de resultado.

---

### Bug #7 — Dashboard Top Players não renderizava barras de progresso (UI — 2026-04-07)

**Sintoma:** Dash faz cache agressivo de CSS. As barras de progresso nunca apareciam porque as classes CSS do arquivo externo não eram carregadas após a primeira build.

**Correção:** `dashboard/components/top_players.py` — reescrita completa. `DataTable` substituído por cards HTML com 100% de estilos inline, sem dependência de CSS externo.

---

### Bug #8 — GetHistoryTrades travava em 99% (DLL — 2026-03 sessão de ingestão)

**Sintoma:** `progress` ficava em 99% com `buffer=0` indefinidamente, levando à interrupção prematura do processo.

**Descoberta:** Esse comportamento é **normal** — a DLL cicla a conexão antes de entregar os dados. O processo NÃO deve ser encerrado. Após 1–3 ciclos de reconexão (30s–5min), os trades chegam normalmente.

**Mitigação:** Timeout mínimo de 1800s implementado. Watchdog de idle como fallback.

---

## 15. Experimentos e Resultados

### Todos os Runs WDO — Histórico Completo

| Run | Data/Hora | L3 Mode | Janelas | Trades | WinRate | PnL Total | Sharpe | Validade |
|-----|-----------|---------|---------|--------|---------|-----------|--------|----------|
| S03 | Mar 2026 | Mock | ~8 | — | — | Descartado | — | ❌ Bugs #1+#2 |
| S04-A | Apr 3, 00:27 | Mock | 11 (2025-04→) | — | — | -R$4.141 | — | ✅ parcial |
| S04-A v2 | Apr 3, 02:06 | Mock | 11 | — | — | -R$1.867 | — | ✅ parcial |
| **S04-B** ← **MELHOR** | **Apr 3, 11:43** | **Mock** | **11 (2025-04→)** | **375** | **~44%** | **-R$818** | — | **✅** |
| Apr-5 full | Apr 5, 14:48 | Mock (prob=0.700) | 24 (2024-03→) | 1590 | 44.3% | -R$11.014 | -1.11 | ⚠️ Bug #3 latente |
| Apr-6 full | Apr 6, 21:43 | Mock (prob=0.700) | 24 | 1427 | 42.6% | -R$13.615 | -1.53 | ⚠️ Bug #3 latente |
| **H1-Fold Real** | **Apr 7, 02:06** | **Real (16 folds)** | **24 (2024-03→)** | **1388** | **43.6%** | **-R$11.045** | **-1.34** | **✅ atual** |

### Análise Janela a Janela (H1-Fold Real — melhor run atual)

```
W1  2024-03-02:  +R$59     | Acumulado:  +R$59
W2  2024-04-01:  -R$81     | Acumulado:  -R$22
W3  2024-05-01: -R$1.098   | Acumulado: -R$1.120
W4  2024-05-31:  +R$12     | Acumulado: -R$1.108
W5  2024-06-30: -R$1.707   | Acumulado: -R$2.815
W6  2024-07-30: -R$2.241   | Acumulado: -R$5.056  ← pior W1-W12
W7  2024-08-29:  +R$145    | Acumulado: -R$4.911
W8  2024-09-28:  +R$495    | Acumulado: -R$4.416
W9  2024-10-28:  -R$811    | Acumulado: -R$5.227
W10 2024-11-27: +R$2.089   | Acumulado: -R$3.138  ← melhor janela
W11 2024-12-27:  -R$528    | Acumulado: -R$3.666
W12 2025-01-26:  -R$405    | Acumulado: -R$4.071
W13 2025-02-25: -R$2.466   | Acumulado: -R$6.537
W14 2025-03-27: -R$3.414   | Acumulado: -R$9.951  ← pior janela geral
W15 2025-04-26: +R$1.399   | Acumulado: -R$8.552
W16 2025-05-26:  +R$31     | Acumulado: -R$8.521
W17 2025-06-25:  -R$351    | Acumulado: -R$8.872
W18 2025-07-25:  +R$288    | Acumulado: -R$8.584
W19 2025-08-24:  -R$582    | Acumulado: -R$9.166
W20 2025-09-23: -R$2.340   | Acumulado: -R$11.506
W21 2025-10-23: -R$1.172   | Acumulado: -R$12.678
W22 2025-11-22:  +R$361    | Acumulado: -R$12.317
W23 2025-12-22: +R$1.475   | Acumulado: -R$10.842
W24 2026-01-21:  -R$201    | Acumulado: -R$11.045
```

### Observações Críticas dos Resultados

**Período problemático — 2024:**
- W1–W6 (Mar–Jul 2024): -R$5.056. Menor densidade de agent_scores, regime desfavorável.
- Estender o walk-forward de 11 para 24 janelas (incluindo 2024) importou -R$5.000 adicionais.

**Período mais favorável — 2025+:**
- S04-B (11 janelas, Apr-2025 → Feb-2026) = -R$818. Significativamente melhor.
- W10, W15, W23 são positivas e consistentes — há sinal nesse período.

**Por que o L3 não resolve:**
- Mock L3 (Apr-5): -R$11.014
- Real L3 (Apr-7): -R$11.045
- Diferença: R$31. O L3 não é o problema e tampouco é a solução.
- **Problema fundamental:** L1+L2 geram sinais estruturalmente perdedores. WinRate 43–44% com R:R 1:1.5 resulta em Profit Factor ~0.90 — marginalmente negativo.

**Distribuição de exit reasons (esperada com base em S04):**
- STOP (~49%): avg ~-R$240 por trade
- TAKE (~30%): avg ~+R$329 por trade
- FORCE_CLOSE (~23%): avg ~+R$20

---

## 16. Estado Atual dos Dados

### Inventário (2026-04-21)

| Tabela | Status | Cobertura WDO | Observação |
|--------|--------|---------------|------------|
| `trades` | ✅ Completo | 2024-01-02 → 2026-04-01 | ~560 dias úteis |
| `features_1s` | ✅ Completo | 2024-01-02 → 2026-04-01 | ~16.4M barras |
| `netflow_agent_1s` | ✅ Completo | 2024-01-02 → 2026-04-01 | base do SmartScore |
| `close_price_1s` | ✅ Completo | 2024-01-02 → 2026-04-01 | após backfill Mar-31 |
| `agent_scores` | ✅ Completo | 2024-01-02 → 2026-04-02 | 524 datas |

### Modelos

| Arquivo | Status | AUC médio | Uso |
|---------|--------|-----------|-----|
| `xgboost_wdo_fold01→16.pkl` | ✅ Ativo | 0.556 (16 folds) | Backtest H1-Fold |
| `fold_manifest_wdo_20260320.json` | ✅ Ativo | — | Mapeia data → fold correto |
| `xgboost_wdo_20260320.pkl` | ⚠️ Legado | 0.564 (7 folds) | Não usar (distribution shift) |
| `xgboost_win_*.pkl` | ❌ Descartado | 0.508 | WDO-only decision |

---

## 17. Stories e Roadmap

### Epic 1–2: Infraestrutura e Pipeline de Dados ✅

| Story | Descrição | Status |
|-------|-----------|--------|
| 1.1 | Setup TimescaleDB + Docker | ✅ Done |
| 1.2 | Ingestão histórica via DLL | ✅ Done |
| 1.3 | Continuous aggregates (features_1s, netflow_agent_1s) | ✅ Done |
| 1.4 | Conector real-time (DLL → Queue → DB) | ✅ Done |
| 2.1 | calc_smart_money_v2.py | ✅ Done |
| 2.2 | batch_smart_money_backfill.py | ✅ Done |
| 2.3 | Backfill completo WDO | ✅ Done |

### Epic 3: Estratégia e Backtesting

| Story | Descrição | Status |
|-------|-----------|--------|
| 3.1 | Backtester event-driven (engine_v2) | ✅ Done |
| 3.2 | Calibração da estratégia + XGBoost | 🔄 Em andamento |

### Epic R: Revisão de Dados (inserida 2026-03-31)

| Story | Descrição | Status |
|-------|-----------|--------|
| R1 | Backfill close_price_1s | ✅ Done |
| R2 | Backfill agent_scores histórico | ✅ Done |
| R3 | Retrain XGBoost com dados corretos | ✅ Done (AUC 0.564, 7/7 viáveis) |
| R4 | Backtest walk-forward válido (L1 / L1+L2 / Full) | 🔴 Pendente |

### Epic 4–6: Produção e Dashboard

| Story | Descrição | Status |
|-------|-----------|--------|
| 4.1 | Live Feed + Paper Trading | ⏸ Aguardando R4 |
| 5.1 | OrderManager + execução real | ⏸ Aguardando 4.1 |
| 6.1 | Dashboard Base (backtest mode) | ✅ Done |
| 6.2 | Dashboard Live Mode | ✅ Done (41 testes passando) |
| 6.3 | Expansões do dashboard | ⏸ Aguardando |

### Próximo Gate Obrigatório — R4

Story R4 estabelece o **primeiro backtest válido** com os 3 modos comparativos:

| Modo | Descrição | Objetivo |
|------|-----------|----------|
| Modo A | L1 apenas | Baseline puro — TFI sem filtros |
| Modo B | L1 + L2 | Descobrir se smart money adiciona alpha |
| Modo C | L1 + L2 + L3 | Sistema completo |

**Framework de decisão (após R4):**

| Cenário | Critério | Ação |
|---------|----------|------|
| A — Alpha confirmado | L1+L2 WR > 48%, PF > 1.2 | → Story 4.1 Paper Trading |
| B — Alpha marginal | L1+L2 WR 42-48%, PF 1.0-1.2 | → Paper Trading conservador |
| C — Alpha insuficiente | L1+L2 WR < 42% ou PF < 1.0 | → Revisão de tese em 3.2 |

---

## 18. Decisões Estratégicas

### 2026-04-03 — WDO-Only

**Decisão:** Descartar WIN como ativo de operação. Manter dados WIN no banco como referência.

**Motivação:**
- WDO tem microestrutura mais previsível (spread mais apertado relativo ao tick)
- Custos de transação WIN são piores em relação ao movimento mínimo esperado
- Dados históricos WDO mais extensos disponíveis via DLL (alcança Jan 2024)
- Simplifica pipeline de treinamento e validação

### 2026-04-06 — Fold Models

**Decisão:** Implementar arquitetura fold-específica para backtest.

**Motivação:** O modelo único (treinado em Jan–Mar 2026) sofria distribution shift ao ser aplicado em 2024. Isso bloqueava 100% dos sinais em janelas antigas porque as probs geradas ficavam abaixo do threshold de execução.

**Resultado:** 16 fold models, cada um treinado com dados apenas anteriores à sua janela de teste. Eliminou o look-ahead contamination no backtest.

### 2026-04-07 — Diagnóstico Fundamental

**Decisão:** L3 não é o problema central. O problema é L1+L2.

**Evidência:** Mock L3 vs Real L3 = diferença de apenas R$31 em 24 janelas. O WinRate estrutural de 43–44% com R:R 1:1.5 é marginalmente perdedor independente do filtro ML.

**Implicação:** O próximo esforço deve focar em melhorar L1+L2 (regime filter, recorte temporal) antes de otimizar L3.

---

## 19. Infraestrutura — Comandos Operacionais

### Backtest

```bash
cd C:\Users\Pichau\Desktop\sentinel

# H1-Fold com modelos fold-específicos (recomendado)
python scripts/run_backtest_v2.py \
  --symbol WDO \
  --start 2024-01-02 \
  --end 2026-03-21 \
  --fold-manifest models/fold_manifest_wdo_20260320.json

# Período 2025+ (melhor performance histórica)
python scripts/run_backtest_v2.py \
  --symbol WDO \
  --start 2025-01-01 \
  --end 2026-03-21 \
  --fold-manifest models/fold_manifest_wdo_20260320.json

# Mock L3 (para comparação rápida)
python scripts/run_backtest_v2.py \
  --symbol WDO \
  --start 2024-01-02 \
  --end 2026-03-21
```

### Treinamento

```bash
# Fold models (correto — sem look-ahead)
python scripts/train_ml_v2.py \
  --symbol WDO \
  --start 2024-01-02 \
  --end 2026-03-21 \
  --fold-models

# Modelo único (legado)
python scripts/train_ml_v2.py \
  --symbol WDO \
  --start 2025-02-17 \
  --end 2026-03-21
```

### SmartScore Backfill

```bash
# Calcula scores WDO para todo o histórico
python scripts/batch_smart_money_backfill.py \
  --ticker WDO \
  --start 2024-01-02 \
  --end 2026-04-02

# Score de um único dia
python scripts/calc_smart_money_v2.py \
  --ticker WDO \
  --date 2026-04-21
```

### Gates de Qualidade

```bash
python scripts/gates/gate_r2_agent_scores.py
python scripts/gates/gate_r3_ml_retrain.py
python scripts/gates/gate_r4_backtest.py
```

### Dashboard

```bash
# Backtest
python dashboard/app.py --mode backtest --start 2024-01-02 --end 2026-04-02
# http://localhost:8050
# Ctrl+Shift+R para hard refresh (limpa cache CSS)

# Live
python dashboard/app.py --mode live
```

### Monitoramento do Progresso (backtest em execução)

```bash
# Arquivo atualizado em tempo real após cada janela
cat backtest/results/progress_WDO.json

# Ou via dashboard (painel de progresso)
```

### Banco de Dados

```bash
# Verificar container
docker ps | grep sentinel

# Iniciar se parado
docker start sentinel-timescaledb

# Conectar via psql
psql postgresql://sentinel:sentinel123@localhost:5433/sentinel_db

# Verificar cobertura de dados
psql -c "SELECT ticker, MIN(timestamp), MAX(timestamp), COUNT(*) FROM trades GROUP BY ticker;"
psql -c "SELECT ticker, COUNT(DISTINCT data_calculo) FROM agent_scores GROUP BY ticker;"
```

---

## 20. Próximos Passos

### Imediato — Story R4

Executar o backtest comparativo que ainda não foi feito:

```bash
# Verificar se run_backtest_v2.py suporta --disable-l2 e --disable-l3
# Se não suportar, adicionar flags antes de executar R4

# Modo A — L1 apenas
python scripts/run_backtest_v2.py --symbol WDO --start 2025-01-01 --end 2026-03-21 --disable-l2 --disable-l3

# Modo B — L1+L2
python scripts/run_backtest_v2.py --symbol WDO --start 2025-01-01 --end 2026-03-21 --disable-l3

# Modo C — Full
python scripts/run_backtest_v2.py --symbol WDO --start 2025-01-01 --end 2026-03-21 \
  --fold-manifest models/fold_manifest_wdo_20260320.json
```

### Médio Prazo — Hipóteses de Melhoria

| Hipótese | Descrição | Impacto Esperado |
|----------|-----------|-----------------|
| **H5 — Regime Filter** | Só operar quando indicadores de regime são favoráveis (ADX, volatilidade realizada, tendência) | Eliminar W6, W14, W20 que destroem capital |
| **Recorte 2025+** | Focar walk-forward em 2025-01→2026-03 (período melhor) | Reproduzir condições do S04-B |
| **Ajuste Stop/Take** | R:R 1:1.5 com WR 44% é marginalmente perdedor — testar 1:1.2 ou stop dinâmico por ATR 5min | Melhorar Profit Factor |
| **L2 threshold** | SmartScore ≥ 0.75 pode ser brando — testar ≥ 0.85 | Trades mais seletivos e com maior WR esperado |
| **Análise EDA dos piores W** | O que W6, W14, W20 têm em comum? Volume? Volatilidade? | Fundamentar o regime filter com dados |

### Longo Prazo

| Marco | Critério de Entrada | Ação |
|-------|--------------------|----|
| Paper Trading | Sharpe > -0.5 em backtest walk-forward | Story 4.1 |
| Execução real | WR > 48%, PF > 1.2 em paper trading de 30 dias | Story 5.1 |
| Retreinar com dados 2025-2026 | Quando completar 2+ anos de dados densos | AUC potencialmente > 0.60 |

---

*Sentinel Master Document v1.0 — gerado por Orion (@aiox-master) em 2026-04-21*  
*Agentes envolvidos ao longo do projeto: @dev (Dex), @qa (Quinn), @data-engineer (Dara), @analyst (Atlas), @ux-design-expert (Uma), @aiox-master (Orion)*
