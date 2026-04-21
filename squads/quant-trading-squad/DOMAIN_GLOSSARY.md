# Quant Trading Squad — DOMAIN GLOSSARY

> Criado em 2026-04-21. Dicionário unificado dos termos que os 7 agentes usam. Cada termo tem definição, owner (quem é fonte), fórmula se aplicável, e availability (histórico trades-only vs live-only).
>
> Regra: se um agente usa um termo, a definição aqui é a válida. Divergência entre agentes é bug de glossário, não opinião.

## Convenções

- **Owner:** agente autoridade sobre o termo. Outros consultam, não redefinem.
- **Availability:** `trades-only` (computável com nosso parquet histórico), `book-required` (precisa captura de book), `live-only` (só em produção), `live+history` (disponível em ambos).
- **Tag `[WEB-CONFIRMED {YYYY-MM}]`:** fato checado em fonte oficial (B3, Nelogica, CVM) em data indicada.
- **Tag `[TO-VERIFY]`:** fato a confirmar empiricamente antes de operar.

---

## Parte 1 — Ativos, Contratos, Mercado

### WDO (Mini Dólar Futuro)
Contrato futuro B3 sobre USD/BRL. Tick 0.5 ponto [WEB-CONFIRMED 2026-01]. Tick value = R$5 por contrato (0,5 × R$10). Multiplicador R$10/ponto [WEB-CONFIRMED 2026-04-21 — humano]. Vencimento mensal primeira letra do mês. **Owner:** Nova. O contrato cheio DOL (R$50/ponto) NÃO é operado por este squad — menção apenas para evitar confusão com valores secundários. [TO-VERIFY: margem vigente conforme broker]

### WIN (Mini Índice Futuro)
Contrato futuro B3 sobre Ibovespa. Tick 5 pontos = R$1 por contrato. Multiplicador R$0.20/ponto. Vencimento bi-mensal (par). **Owner:** Nova. Role no sistema: **supporting** (correlação, cointegração, hedge), não primário. [TO-VERIFY]

### Contrato Vigente
Contrato com liquidez ativa em dado momento. Para WDO: primeiro WDO do mês corrente até rollover (~D-1 do último dia útil). **Owner:** Nova (rollover calendar). Tiago segue.

### Rollover
Transição do contrato atual para o próximo vencimento. Liquidez migra em ~1-3 dias. Riven aplica multiplicador de size ×0.7 em janela de rollover. **Owner:** Nova.

### Lote Padrão
1 contrato = unidade mínima de trading. Para WDO e WIN, lotes são inteiros. Sem fração. **Owner:** Nova.

### Tick Size
Menor incremento de preço negociável. WDO = 0.5 ponto. WIN = 5 pontos. Edge < 2 ticks em DMA2 é frágil (Riven aplica haircut). **Owner:** Nova.

### Multiplicador (Point Value)
Valor em R$ por ponto de variação do contrato. WDO = R$10/ponto [WEB-CONFIRMED 2026-04-21]. WIN = R$0.20/ponto [TO-VERIFY]. Usado para conversão PnL e sizing. **Owner:** Nova. Fonte única canônica deste número — agentes referenciam este glossário; proibido redefinir inline em features ou testes.

---

## Parte 2 — Microestrutura B3

### PUMA
Matching engine B3. Price-time priority FIFO. Sem pro-rata (exceto alguns contratos específicos). **Owner:** Nova.

### Fases de Pregão
Sequência cronológica diária B3 (horário BRT):
- **Pré-abertura** (com leilão de abertura)
- **Abertura** (auction cross)
- **Continuous trading** (pregão regular)
- **Leilão de fechamento**
- **After-market** (quando disponível)

Horários exatos variam por DST e evento B3. **Owner:** Nova. Beckett e Tiago consultam para regime de fill/latency.

### RLP (Retail Liquidity Provider)
Mecanismo B3 onde formador de mercado cruza com retail sem exposição pública do book. Trade type = **13** no enum histórico B3. **Owner:** Nova. **Availability:** identificável em datasets B3 com enum completo, **não identificável em nosso parquet atual** (enum reduzido BUY/SELL/NONE).

### Trade Type Enum (B3 oficial)
13 tipos: regular, cross, blocktrade, odd-lot, forward, RLP, etc. Aparece em datasets oficiais B3. **Owner:** Nova. **Availability em nosso dataset:** não disponível — nosso parquet traz apenas enum reduzido BUY/SELL/NONE baseado em lado do agressor.

### Aggressor (Lado Agressor)
Lado que cruzou o spread, consumindo liquidez. No nosso parquet: campo `aggressor` ∈ {BUY, SELL, NONE}. **Owner:** Nova (definição), Beckett (uso em simulação). **Availability:** live+history.

### Cross Trade
Negócio casado (buy e sell do mesmo participante). Preço fora de midprice geralmente. Filtrar em CVD/VPIN. **Owner:** Nova. **Availability:** histórico parquet tem via `trade_number` colisão + agentes iguais.

### Leilão de Abertura / Fechamento
Matching único em horário fixo. Não segue FIFO contínuo — clearing price. **Owner:** Nova. Beckett simula separadamente (fill model especial). Tiago evita enviar ordens regulares em leilão.

### Kyle's Lambda (λ)
Impacto temporário de preço por unidade de net order flow: `λ = Δprice / ΔnetFlow`. Mede iliquidez — λ alto = mercado raso (ordem pequena já move preço). Referência canônica: Kyle 1985 ("Continuous Auctions and Insider Trading"). Usado em price-formation por Nova e em impact models por Beckett. **Owner:** Nova (conceito microestrutural), Beckett (estimação empírica). **Availability:** computable em trades-only via regressão Δprice × Δ(CVD/volume assinado).

---

## Parte 3 — ProfitDLL Nelogica

### ProfitDLL
DLL Nelogica de acesso ao feed B3 + roteamento de ordens. Única porta de conexão ao mercado deste sistema. **Owner:** Nelo.

### DMA2
Nível 2 de acesso direto — ordem vai via servidor da corretora, não co-location. Latência p50 ≈ 20ms, p95 ≈ 60ms, p99 ≈ 100ms, tail ≈ 500ms. **Owner:** Nelo (spec técnica) + Nova (contexto mercado) + corretora (infra). [TO-VERIFY: latências empíricas por corretora específica]

### DMA1 / DMA3 / DMA4
Outros níveis de acesso (conhecimento geral, não usados aqui). DMA1 = mais alto overhead, DMA4 = co-location (mais rápido, indisponível neste sistema). **Owner:** Nelo.

### SendOrder
Função DLL para envio de ordem nova. Retorna order ID interno. **Monopólio Tiago.** Rejection codes começam `NL_`. **Owner:** Nelo.

### ChangeOrder
Função DLL para alterar ordem ativa (preço, quantidade). Pode gerar race condition com fill pendente. **Monopólio Tiago.** **Owner:** Nelo.

### CancelOrder
Função DLL para cancelar ordem ativa. Pode falhar se ordem já foi preenchida (race). **Monopólio Tiago.** **Owner:** Nelo.

### Callback
Função que a DLL chama de volta em evento assíncrono. Executa em thread DLL — Tiago/Nelo cuidam para não bloquear. **Owner:** Nelo.

### TOrderChangeCallback
Callback disparado em cada mudança de estado de ordem (ack, fill, partial, cancel, reject). Timestamps em BRT. Usado por Tiago para construir lifecycle. **Owner:** Nelo.

### Trade Callback (live)
Callback de trade observado no feed (qualquer trade, não só nosso). Usado por Tiago/Mira para pipeline ao vivo. **Owner:** Nelo.

### OfferBookV2 / PriceBookV2
Callbacks de book (profundidade). **Availability:** live-only em nosso sistema — NÃO capturados historicamente. Decisão pendente: habilitar captura diária para feature backtest futura. **Owner:** Nelo (spec), Nova (valor microestrutural).

### Rejection Code (NL_*)
Código de erro da DLL após tentativa de ordem. Exemplos: `NL_INVALID_ARGS`, `NL_CONNECTION_BROKEN`, `NL_ORDER_NOT_FOUND`, `NL_INTERNAL_ERROR`. Nelo mantém atlas completo. Tiago rotula; Riven aplica política (retry, halt, escalate). **Owner:** Nelo.

### Business Rejection
Rejeição da corretora após DLL aceitar (ex.: limite excedido, margem insuficiente). Vem como callback com motivo textual. Riven interpreta, não Nelo. **Owner:** corretora + Riven.

---

## Parte 4 — Dataset Histórico

### Parquet Histórico
Arquivos em `D:\sentinel_data\historical\` — 840 parquets WDO+WIN (2023-2026). **Trades-only (sem book).** **Owner:** Beckett (uso), infra (storage).

### Schema do Parquet
Colunas:
- `timestamp` (BRT naive)
- `ticker` (WDOFUT, WINFUT)
- `price` (float)
- `vol` (volume em R$)
- `qty` (quantidade de contratos)
- `buy_agent` (código agente comprador)
- `sell_agent` (código agente vendedor)
- `aggressor` ∈ {BUY, SELL, NONE}
- `trade_type` ∈ {BUY, SELL, NONE} (enum reduzido, não é o enum 13-type)
- `trade_number` (sequência B3)

**Owner:** Beckett.

### Trades-Only
Constraint absoluta do nosso dataset: não há snapshot/delta de book histórico. Features book-based não podem ser computadas em backtest até captura diária ativar. **Consequência:** Mira/Beckett respeitam; features book-based ficam `live_only`.

### Captura Diária de Book
Plano futuro: capturar OfferBookV2/PriceBookV2 todo dia para habilitar features microestruturais em backtest. Custo estimado: 1-5 GB/dia + pipeline live confiável. **Decisão pendente.** Participantes: Aria (infra), Dara (schema), Nova (valor), Mira (feature).

---

## Parte 5 — Features (ML)

### CVD (Cumulative Volume Delta)
Σ (volume comprador agressor) − Σ (volume vendedor agressor). Fluxo direcional. **Availability:** trades-only computable. **Owner:** Mira (como feature), Nova (microestrutura). Fórmula:
```
CVD_t = Σ_{i ≤ t} (qty_i × sign(aggressor_i))
```

### VPIN (Volume-Synchronized Probability of Informed Trading)
Proxy de probabilidade de informed trading. Agrega trades em buckets de volume constante, calcula imbalance. **Availability:** trades-only computable. **Owner:** Mira + Nova. Fonte: Easley, Lopez de Prado, O'Hara papers.

### OFI (Order Flow Imbalance)
Fluxo líquido de ordens no book top. ΔBid − ΔAsk ponderado. **Availability:** book-required → **LIVE-ONLY** em nosso sistema. **Owner:** Mira.

### Imbalance_BookTop (L2/L5/L10)
Razão de volume bid vs ask em N níveis do book. **Availability:** book-required → **LIVE-ONLY**. **Owner:** Mira.

### Microprice
Média ponderada bid-ask pelo volume oposto: `microprice = (bid × ask_qty + ask × bid_qty) / (ask_qty + bid_qty)`. Melhor estimador de "preço justo" que midprice. **Availability:** book-required → **LIVE-ONLY**. **Owner:** Mira.

### Roll Spread Estimator
Proxy de bid-ask spread inferido de trades só: `2 × sqrt(−cov(Δp_t, Δp_{t-1}))` quando cov negativa. **Availability:** trades-only computable. **Owner:** Mira + Nova. Fonte: Roll (1984).

### Aggressor Intensity
Taxa de trades agressor-buy vs agressor-sell em janela. **Availability:** trades-only computable. **Owner:** Mira.

### Trade Size Statistics
Média, mediana, P99 de `qty` por janela. Detecta "whales". **Availability:** trades-only computable. **Owner:** Mira.

### Queue Position
Posição estimada de ordem passive no book. **Availability:** book-required → **LIVE-ONLY**. **Owner:** Mira + Beckett (uso em fill rules).

### Spoofing Detection
Padrão de colocar e cancelar ordens sem intenção de fill. Requer book histórico para backtest. **Availability:** book-required → **LIVE-ONLY**. **Owner:** Nova (microestrutura), Mira (feature).

### Historical Availability (campo de feature_registry)
Campo obrigatório em toda feature: `computable | live_only | partial`. Force explicitar se feature pode entrar em backtest. **Owner:** Mira (mantém registry).

---

## Parte 6 — Labels & Cross-Validation

### Triple Barrier
Método de labelagem (Lopez de Prado AFML): define target = primeiro evento entre (take-profit, stop-loss, max-holding). Label = {+1, −1, 0}. **Owner:** Mira. Fonte: AFML cap. 3.

### Meta-Labeling
Duas camadas: modelo primário prediz lado (buy/sell/pass); modelo secundário prediz *confiança* da primária. Útil para sizing. **Owner:** Mira. Fonte: AFML cap. 3.

### CPCV (Combinatorial Purged Cross-Validation)
Cross-validation que resiste a leakage temporal. Parâmetros default do squad: N = 10-12 grupos, k = 2 grupos de teste, 45 paths, embargo = 1 sessão. **Owner:** Mira + Beckett. Fonte: AFML cap. 12. **Padrão decisório do squad — substitui walk-forward single-path.**

### Embargo
Janela temporal entre fim do treino e início do teste, para prevenir leakage de label que depende de futuro. Default: 1 sessão (~8 horas B3). **Owner:** Mira.

### Purged K-Fold
Versão básica de CPCV — remove amostras cujo label observável vaza no fold de teste. **Owner:** Mira.

### Sample Uniqueness
Peso de amostra dado overlap temporal de labels. Amostras sobrepostas são downweighted. **Owner:** Mira. Fonte: AFML cap. 4.

### Fractional Differentiation
Transformação que torna série estacionária preservando memória (ao contrário de returns que destroem memória). **Owner:** Mira. Fonte: AFML cap. 5.

---

## Parte 7 — Estatística & Overfitting

### PBO (Probability of Backtest Overfitting)
Probabilidade de que a estratégia selecionada por melhor Sharpe in-sample tenha Sharpe OOS abaixo da mediana. **PBO > 0.5 = overfitting severo.** **Owner:** Mira + Beckett. Fonte: Bailey & Lopez de Prado.

### DSR (Deflated Sharpe Ratio)
Sharpe ajustado pela multiplicidade de testes e pela não-normalidade dos retornos. Evita "Sharpe de sorte". Squad define limiar mínimo para aprovação de estratégia. **Owner:** Mira + Beckett. Fonte: Bailey & Lopez de Prado 2014. DSR = PSR corrigido para N tentativas independentes.

### PSR (Probabilistic Sharpe Ratio)
Probabilidade de que o Sharpe observado seja estatisticamente maior que um benchmark (geralmente zero), considerando skew e kurtosis dos retornos (não-normalidade). Base estatística do DSR. **Owner:** Kira + Mira. Fonte: Bailey & Lopez de Prado 2012. Relação: `DSR = PSR_adjusted(N_trials)`.

### DSR Critical Threshold
Limiar de DSR abaixo do qual Beckett rejeita o backtest. **Owner:** Mira (define), Beckett (aplica). [TO-VERIFY: valor exato pós-calibração empírica]

### Haircut
Redução aplicada a métricas backtest para refletir realidade (slippage, costs, capacity). Default squad: 30-50% nos primeiros meses live. **Owner:** Riven + Beckett.

### Capacity
Tamanho máximo de posição sem degradar alpha materialmente. Função de volume médio, turn ratio, market impact. **Owner:** Beckett (simulação), Riven (enforcement via max position).

---

## Parte 8 — Risk (Riven)

### Kelly Fraction
Fração ótima de capital por trade dado edge e odds: `f* = (p × b − q) / b` no caso Bernoulli. Usado como teto teórico, nunca aplicado direto. **Owner:** Riven.

### Quarter-Kelly
Fração prática: ¼ × Kelly. Teto operacional do squad. Quarter evita quebra em drawdown e respeita incerteza de edge. **Owner:** Riven. Regra invariável do squad.

### Drawdown Budget
Orçamento de perda por horizonte:
- **trade:** 0.5-1% do capital
- **day:** 2-3%
- **week:** 5-7%
- **month:** 10-12%

Trigger de throttle/halt/kill usa esses budgets. **Owner:** Riven. [TO-VERIFY: calibração empírica ajusta após primeiras sessões live]

### Regime Filter
Multiplicador de size aplicado pelo Riven baseado em regime:
- opening/closing: ×0.5
- rollover: ×0.7
- evento macro (COPOM, FOMC, payroll): ×0.3
- high-vol: ×0.5
- low-vol: ×0.7

**Owner:** Riven + Nova (identifica regime).

### Kill-Switch (4 Níveis)
Escada de defesa:
1. **warning** — métrica próxima de limite; log + notificação
2. **throttle** — reduz size ×0.5 automaticamente
3. **halt** — para envio de novas ordens; mantém posições
4. **kill** — fecha todas posições market + trava sistema

Kill exige post-mortem + aprovação humana para desarmar. **Owner:** Riven. Regra invariável.

### Margin
Capital exigido pela B3 + corretora por contrato aberto. B3 publica margem oficial; corretora aplica margem adicional própria. Riven consulta ambos. **Owner:** Nova (B3), corretora (adicional). Nelo NÃO é fonte. [TO-VERIFY: margem vigente B3]

### Limits Aggregation
Soma de exposição corrente + exposição pretendida vs limites (daily loss, position, capital). Antes de approve, Riven agrega. **Owner:** Riven.

### Stress Test
Simulação de eventos extremos (flash crash, gap, disconnect, rollover falho) contra a estratégia atual. Mínimo trimestral ou antes de live. **Owner:** Beckett (simula), Riven (orquestra, decide).

---

## Parte 9 — Execução (Tiago)

### Order Lifecycle States
11 estados: `CREATED, GATEWAY_REJECTED, GATEWAY_APPROVED, SENT, ACK_RECEIVED, PARTIALLY_FILLED, FILLED, CANCELLED, REJECTED, FAILED, RACE_FILL`. **Owner:** Tiago.

### Order Types
- **market** (a mercado, preenche imediato contra book)
- **limit** (preço fixo, preenche se cruzar)
- **stop** (vira market ao tocar preço gatilho)
- **stop-limit** (vira limit ao tocar)
- **IOC** (Immediate-or-Cancel — preenche o que pode, cancela resto)
- **FOK** (Fill-or-Kill — preenche tudo ou nada)

**Owner:** Nelo (spec DLL), Tiago (uso).

### Ack (Acknowledgment)
Confirmação da DLL de que ordem foi recebida (não implica preenchimento). Timestamp `t_ack`. **Owner:** Nelo + Tiago.

### Fill
Execução (total ou parcial) de ordem. Timestamp `t_first_fill`, `t_last_fill`. **Owner:** Tiago.

### Partial Fill
Ordem preenchida parcialmente — restante fica aberto (limit) ou cancelado (IOC). **Owner:** Tiago.

### Race Condition
Evento onde callback chega fora de ordem lógica:
- **RACE_FILL:** cancel enviado após fill já ocorrido — fill prevalece
- **change_cancel_vs_original_fill:** change chega após fill original
- **double_fill_on_retry:** retry envia segunda ordem antes de ack original

Tiago detecta e loga; Riven decide política. **Owner:** Tiago (detecção), Nelo (causa DLL).

### Telemetry (Tiago)
Log estruturado por ordem com timestamps (t_decision, t_gateway_in, t_gateway_out, t_send, t_ack, t_first_fill, t_last_fill), slippage esperado vs realizado, rejection code, lifecycle path. Feed para Beckett calibrar. **Owner:** Tiago.

### Reconciliação EOD
Comparação fim-de-dia entre posição interna Tiago ≡ posição corretora (via DLL). Mismatch → HALT automático + investigação. Dia não fecha sem reconciliação. **Owner:** Tiago. Regra invariável.

### Paper-Mode
Modo onde Tiago consome feed real mas NÃO chama SendOrder real — engine Beckett simula fills. Obrigatório ≥ 5 sessões antes de transição para live. **Owner:** Tiago + Beckett.

### Idempotency Key
Chave única por intent-to-order (não por retry). Evita envio duplicado quando ack demora. **Owner:** Tiago.

### Order IDs (ClOrderID / profit_id / session_id / MessageID)
Quatro identificadores distintos no ciclo de vida de uma ordem:
- **ClOrderID** — ID permanente client-side atribuído por Tiago no momento da criação; imutável; rastreia ordem cross-session.
- **profit_id** — int64 retornado pela DLL como order ID interno ProfitDLL; stable após ack.
- **session_id** — ID válido apenas durante a sessão DLL corrente; perdido se DLL reconecta.
- **MessageID** — ID de cada mensagem/callback da DLL (não da ordem — útil para correlacionar callbacks duplicados).

**Owner:** Nelo (ProfitDLL spec), Tiago (uso). Fluxo: Tiago cria `ClOrderID` → SendOrder → DLL retorna `profit_id` + `session_id` no ack → Tiago mapeia `ClOrderID ↔ profit_id`.

---

## Parte 10 — Simulação (Beckett)

### DLL-Fiel
Propriedade do simulador de reproduzir comportamento DLL real: rejection codes, latência, sequência de callbacks, race conditions. **Owner:** Beckett.

### Fill Rules (Trades-Only)
Regras para determinar se ordem simulada teria preenchido, usando apenas trades observados (sem book):
- **market:** preenche ao próximo trade, preço = trade price + slippage model
- **limit_passive:** preenche SE trade oposto cruza seu preço E tempo no book > threshold (worst-case queue)
- **limit_aggressive:** preenche imediato
- **stop:** vira market ao trade tocar gatilho

**Owner:** Beckett. **Availability:** trades-only (se livro disponível, rules mais precisas).

### Slippage Model
Estimativa de quanto preço de fill diverge de decisão. Função de aggressor intensity, volatilidade, fase. Calibrado com telemetria Tiago. **Owner:** Beckett.

### Almgren-Chriss (Impact Model)
Framework clássico para decomposição de custo de execução em (a) impacto temporário (desloca preço enquanto executa, recupera parcialmente) e (b) impacto permanente (informação revelada, não recupera). Trade-off: execução rápida paga impacto; execução lenta paga risco de mercado. Referência: Almgren & Chriss 1999/2000. **Owner:** Beckett (implementação simplificada para impact model do simulador). **Availability:** computable (estimação via trade log + volatilidade).

### Latency Profile (DMA2)
Distribuição estocástica: p50=20ms, p95=60ms, p99=100ms, tail stress=500ms. Aplicada em simulação. [TO-VERIFY: empírico por corretora]. **Owner:** Beckett + Nelo (info DLL).

### Calibration Loop
Ciclo: Tiago telemetria → Beckett ajusta fill/latency model → Beckett recomputa backtest → Mira/Riven veem gap vs paper-mode. Frequência: semanal em produção. **Owner:** Beckett.

### Backtest Engine
Motor que consome parquet histórico + spec de estratégia + fill rules + latency model e produz equity curve, trades, métricas. **Owner:** Beckett.

---

## Parte 11 — Timestamps & Timezone

### BRT (Brasília Time)
Timezone de referência absoluta. UTC-03:00 (sem DST atualmente — DST abolido em 2019). **Owner:** Nova. **Regra invariável:** todos timestamps em BRT, nunca UTC. Converter destrói fase de pregão.

### BRT Naive
Timestamp sem offset explícito, assumido BRT. Formato do parquet. **Owner:** Beckett.

### ISO 8601 com Offset
Formato de timestamp externo (logs, relatórios): `2026-04-21T14:30:00-03:00`. **Owner:** convenção squad.

### DST (Daylight Saving Time)
Horário de verão — abolido no Brasil desde 2019. Relevante historicamente (parquets pré-2019 cuidado). **Owner:** Nova.

---

## Parte 12 — Tags & Convenções de Escrita

### `[WEB-CONFIRMED {YYYY-MM}]`
Fato confirmado via websearch em fonte oficial (B3, Nelogica, CVM) na data indicada. Ex.: `[WEB-CONFIRMED 2026-04]`. **Uso:** obrigatório antes de citar tick/multiplicador/margem/horário.

### `[TO-VERIFY]`
Fato a confirmar empiricamente antes de operar. Indica placeholder que precisa recálculo contra realidade. **Uso:** obrigatório quando agente não tem certeza.

### Convention for ProfitDLL Codes
Maiúsculo, prefixo `NL_`. Exemplos: `NL_OK`, `NL_INVALID_ARGS`, `NL_CONNECTION_BROKEN`. **Owner:** Nelo.

### Convention for Squad Commands
Prefixo `*`. Ex.: `*size-trade`, `*tiago-gateway`, `*run-cpcv`. Um agente só responde comandos do seu namespace.

---

## Parte 13 — Outros

### Edge
Retorno esperado positivo por trade (bruto de custos). Em ticks ou R$/contrato. **Owner:** Mira (estima), Riven (valida viabilidade pós-custos).

### Costs (Total)
Corretagem + emolumentos + tributos + slippage + market impact. **Owner:** Nova (emolumentos/tributos B3), corretora (corretagem), Beckett (slippage/impact).

### Alpha
Retorno em excesso do benchmark ajustado a risco. Neste squad, benchmark é buy-and-hold do contrato vigente. **Owner:** Mira (research), Beckett (medição).

### Turnover
Taxa de giro de capital — Σ |trade notional| / capital. Alto turnover → custos dominam. **Owner:** Beckett.

### Sharpe Ratio
`(retorno médio − risk-free) / σ(retornos)`. Anualizado por √252 (dias úteis) ou √(sessões/ano). Métrica base, mas **DSR é preferido para decisão.** **Owner:** Mira + Beckett.

### Sortino Ratio
Sharpe com σ apenas dos retornos negativos (downside deviation). **Owner:** Mira.

### Calmar Ratio
Retorno anualizado / max drawdown. **Owner:** Beckett.

### Hit Rate
% de trades vencedores. Não é métrica primária — DSR/PBO são. Pode ser alta com edge negativo se R:R ruim. **Owner:** Mira.

### R:R (Reward:Risk)
Razão entre target e stop. Tripleto: take-profit / stop-loss. **Owner:** Mira (label), Riven (stop design).

### Autocorrelation of Returns
Correlação entre retornos consecutivos. B3 exibe momentum intraday curto (AR(1) pequeno positivo) e reversão em janelas longas. **Owner:** Kira (EDA), Mira (feature).

### Cointegration
Série combinada estacionária entre pares não-estacionários. WDO e WIN podem apresentar cointegração em janelas. **Owner:** Kira (EDA), Mira (modelo pairs).

---

## Parte 14 — Auditoria (Sable)

### Finding
Registro estruturado de divergência/gap/overlap detectado pelo auditor. Campos: ID, data, escopo, regra, severidade, tag, descrição, evidência, ação, owner, status. **Owner:** Sable (@squad-auditor).

### Severidade (finding)
- **🔴 crítico:** viola regra invioláve do MANIFEST ou impede live ou risco material
- **⚠️ moderado:** divergência semântica, gap de handoff, ambiguidade
- **💡 cosmético:** clarificação, consistência estilística

**Owner:** Sable.

### Tag (finding)
Rótulo do tipo de problema:
- `[CONFIRMED]` — item validado sem divergência
- `[DIVERGENCE]` — agente e doc canônico discordam
- `[GAP]` — ausência de cobertura
- `[OVERLAP]` — dois agentes com mesma autoridade
- `[AMBIGUOUS]` — termo/regra interpretável em múltiplas formas

**Owner:** Sable.

### Red-Team (fluxo)
Stress-test de fluxo canônico: simula falha em cada ponto e verifica quem detecta, em quanto tempo, qual fallback. **Owner:** Sable. Aplicado aos 5 fluxos canônicos da MATRIX.

### Re-auditoria
Processo: finding aberto → owner corrige → notifica Sable → Sable re-audita → Sable fecha OU reabre. Owner NUNCA fecha sozinho. **Owner:** Sable.

### Waiver
Aceite humano de um finding aberto que não será corrigido (decisão de política). Registrado no finding com `status: waived` e `waiver_reason`. **Owner:** humano autoriza; Sable registra.

### Pré-Block Review
Auditoria obrigatória antes de Block decisório do projeto. Bloqueia avanço se houver finding 🔴 aberto. Comando: `@squad-auditor *preblock-review {block}`. **Owner:** Sable.

### Post-Incident Audit
Auditoria pós-evento live (kill trigger, mismatch EOD, rejection cascade). Foca em: qual regra deveria ter prevenido, qual handoff falhou, qual agente foi cego. Prazo: 24h após evento. **Owner:** Sable.

### Dissonância Semântica
Termo usado por agentes diferentes com significados sutilmente diferentes. Causa clássica de falha sistêmica em mesas quant. Detectada via `*audit-glossary`. **Owner:** Sable.

### Drift
Divergência gradual entre definição canônica (GLOSSARY) e uso real pelos agentes ao longo do tempo. Monitorado em auditorias sucessivas. **Owner:** Sable.

---

## Manutenção do Glossário

- **Quem edita:** qualquer agente pode propor; owner do termo aprova.
- **Quando revisar:** antes de cada Block; após incidentes que revelarem ambiguidade.
- **Conflito entre agentes:** glossário é a verdade. Divergência no uso = bug; corrigir o agente, não o glossário.
- **Termos novos:** adicionar sempre que Block 2+ introduzir conceito recorrente.

---

*Glossário consolidado em 2026-04-21. Ver [MANIFEST.md](MANIFEST.md) e [COLLABORATION_MATRIX.md](COLLABORATION_MATRIX.md).*
