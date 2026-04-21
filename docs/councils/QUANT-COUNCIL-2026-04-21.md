# Quant Council #001 — Ideação de Tese Real

**Data:** 2026-04-21 BRT
**Facilitador:** Orion (@aiox-master)
**Status:** OPEN — em Fase 3 (stress-test)

---

## Participantes

| Papel | Agente | Autoridade no conselho |
|-------|--------|----------------------|
| Chair / científico | Kira (@quant-researcher) — ♌ | decide se tese entra em Fase A formal |
| Viabilidade ML | Mira (@ml-researcher) | vota em leakage/overfitting risk |
| Microestrutura B3 | Nova (@market-microstructure) | vota em plausibilidade estrutural |
| Availability live | Nelo (@profitdll-specialist) | vota em computabilidade em tempo real |
| Humano (product owner) | você | direção estratégica, veto final |

**Observadores silenciosos** (não votam, podem ser invocados):
- Beckett (viabilidade de backtest) — chamar se tese exige construção de simulador especial
- Riven (sizing/budget DD) — chamar se tese tem perfil de risco atípico
- Tiago (execução) — chamar se tese exige algoritmo de execução específico
- Sable (coerência) — chamar se surgir dúvida de regra R1-R14
- Dara, Aria, Quinn, Dex, Pax, Morgan, River, Gage — framework, fora desta fase

---

## Protocolo

**Fase 0 — Escopo (agora):**
- Humano expressa 1-3 direções de interesse OU solicita brainstorming aberto
- Kira prioriza entre direções com base em: economic rationale aparente, testabilidade, custo de desenvolvimento

**Fase 1 — Divergência (3-5 ideias):**
- Kira propõe 3-5 teses candidatas na direção escolhida
- Cada agente (Mira/Nova/Nelo) adiciona 1 ou mais alternativas do seu ângulo
- Humano pode adicionar/redirecionar

**Fase 2 — Convergência (3 teses finalistas):**
- Cada tese recebe scorecard rápido: (a) economic rationale 1-5, (b) testability 1-5, (c) availability 1-5, (d) cost-to-develop 1-5
- Top 3 avançam

**Fase 3 — Stress-test (1 tese winner):**
- Para a tese #1 do ranking: red-team dos 4 (tenta matar) e depois humano decide GO/NO-GO para Fase A formal

**Fase 4 — Handoff Fase A:**
- Se GO: Kira abre `docs/research/thesis/T{NNN}-{slug}.md` usando template canônico + aciona Mira/Nova/Nelo para artefatos de consulta

---

## Histórico (roda no formato abaixo)

### Turno 0 — Abertura (Orion)
Conselho aberto. Aguardando direção inicial do humano.

### Turno 1 — Decisão metodológica (Orion + conselho, humano delega)
Humano delegou decisão ao conselho. Escolha: **caminho 2 + 5 combinados**.
- Nova+Nelo abrem oportunidades observáveis em WDO trades-only (caminho 2)
- Kira filtra contra lista negativa do que já sabemos não funcionar (caminho 5)
- Mira entra depois com scorecard ML sobre o subset sobrevivente

Racional: evita queimar ciclos em direções mortas; maximiza sinal/ruído da fase de ideação.

### Turno 2 — Lista Negativa (Kira chair)

**O que NÃO tentaremos em WDO trades-only (expectativa calibrada):**

| # | Estratégia | Por que NÃO |
|---|-----------|-------------|
| N1 | Trend-following multi-dia clássico (MA crossover, Donchian) | WDO tem forte mean-reversion intraday; Sharpe histórico de trend-following em futuros de FX emergentes é baixo (~0.3) e alvo de HFTs |
| N2 | Pairs trading WDO × WIN cointegração estática | Relação é instável — quebra em regime de stress cambial ou choque Ibovespa; exige refit muito frequente que destrói edge |
| N3 | Carry estrutural (comprar mini por diferencial de juros) | Carry em USDBRL é hedge de macro, não alpha explorável em intraday com trades-only |
| N4 | Volatility breakout estilo Turtle | Alpha histórico foi erodido por HFT; spread + slippage comem o edge em WDO mini |
| N5 | Order book imbalance clássico | PROIBIDO por R7 — livemente requer book, tese vira LIVE-ONLY sem backtest honesto |
| N6 | Predição de direção 1 tick à frente | Curto demais; latência DMA2 (p50=20ms) e spread de 1 tick comem qualquer edge estatístico |
| N7 | Seguir agente específico (ex: "smart money") | Dataset trades-only não tem agent_id confiável granular; WIN teria mais sentido mas não é primary |

**Consequência:** teses só avançam se escaparem destes 7 anti-padrões.

### Turno 3 — Nova: 5 oportunidades observáveis em WDO trades-only

Nova abre as 5 oportunidades estruturais mais observáveis sob constraint trades-only:

| # | Tese microestrutural | Observabilidade trades-only | Economic rationale curto |
|---|---------------------|----------------------------|--------------------------|
| O1 | **Momentum pós-evento macro** (CPI-BR, Copom, payroll US, FOMC) | ALTA — eventos têm timestamp conhecido, bars 1-5 min pós-evento são observáveis | Lag USDBRL spot → futuro + ajuste de hedge de dealers gera inércia direcional 5-30 min |
| O2 | **Mean-reversion em overextension intraday** (z-score de retorno acumulado desde open) | ALTA — computável de trades | Exportadores/importadores entram contra movimento extremo para hedgear fluxo do dia |
| O3 | **Opening range break** (break do range 09:30-10:00 com filtro de volume) | ALTA — range é trivial de trades | Fluxo de abertura forma range; break com volume confirma direção institucional do dia |
| O4 | **VPIN-like toxicity → regime de evitar trade** | MÉDIA — VPIN clássico usa buckets de volume, computável mas aproximado | Alto fluxo tóxico (informed trading) → market maker recua → spread widens; evitar operar reduz tail loss |
| O5 | **End-of-day inventory unwind** (última hora: 16:55-17:55) | ALTA — janela fixa | Dealers fecham/reduzem posição pré-call; gera pressão direcional previsível condicional ao posicionamento do dia |

### Turno 4 — Nelo: availability de cada O1-O5

| # | Availability live | Observações |
|---|------------------|-------------|
| O1 | `computable` | Eventos macro têm calendário público; timestamp no feed BRT naive direto do callback |
| O2 | `computable` | Retorno acumulado é O(1) por trade; z-score usa janela rolante |
| O3 | `computable` | Range 09:30-10:00 fechado em memória, break detectado em tempo real |
| O4 | `partial` | VPIN clássico usa bucket por volume — computável, mas versão que usa imbalance de agressão é mais robusta e exige tradeType (TNewTradeCallback entrega — OK) |
| O5 | `computable` | Janela fixa, trivial |

Todas 5 sobrevivem ao filtro Nelo (nenhuma exige book ou GetHistoryTrades no callback).

### Turno 5 — Kira cruza com lista negativa (N1-N7)

| # | Sobrevive? | Risco de colisão com lista negativa |
|---|-----------|-------------------------------------|
| O1 | ✅ | Nenhum — momentum pós-evento ≠ trend-following cego (N1). Janela curta, catalisador identificável. |
| O2 | ✅ | Não é mean-reversion estatístico puro (seria pair trading N2) — é mean-reversion **condicional a overextension** com filtro de regime. |
| O3 | ⚠️ | Parentesco distante com N4 (Turtle). Diferença: opening range é janela determinística 09:30-10:00 com filtro de volume + fase específica do dia. Aceitável se filtro de custos for realista. |
| O4 | ✅ | Não é predição — é **regime filter defensivo**. Reduz exposição em toxic flow; não é alpha direcional. Complementar a qualquer tese, não standalone. |
| O5 | ✅ | Janela e mecanismo específicos; não é carry (N3) nem trend (N1). |

Kira ranqueia por (a) economic rationale, (b) testability, (c) cost-to-develop, (d) não-triviality:

| Rank | Tese | RA | Test | Cost | Trivial? | Score |
|------|------|----|----|------|----------|-------|
| 1º | **O1 — Momentum pós-evento macro** | 5 | 4 | 3 | baixa (catalisador real) | **4.5** |
| 2º | **O5 — End-of-day inventory unwind** | 4 | 5 | 2 | média | **4.3** |
| 3º | **O2 — Mean-reversion condicional overextension** | 4 | 4 | 3 | média | **4.0** |
| 4º | O4 — VPIN defensivo | 3 | 3 | 4 | baixa | 3.5 (não-standalone, fica como módulo auxiliar) |
| 5º | O3 — Opening range break | 3 | 4 | 3 | alta | 3.3 (overplayed no mercado retail) |

### Turno 6 — Mira scorecard ML sobre top-3

| Tese | IC esperado | Sample size viável | Overfitting risk | Leakage risk | Veredito Mira |
|------|-------------|-------------------|------------------|--------------|---------------|
| O1 | **MÉDIO-ALTO** — catalisadores + direção clara | ~500 eventos macro × 30 meses = ~15k janelas | BAIXO se feature set for parco (não jogar tudo em tree) | BAIXO se timestamp de evento for strict | FORTE ✅ |
| O5 | MÉDIO — regime repetitivo | ~500 dias × 30 meses × 1 obs/dia = ~500 obs (PROBLEMA: sample pequeno) | MÉDIO — overtuning em janela específica | BAIXO | OK com caveat — aumentar granularidade (janelas dentro da última hora) |
| O2 | BAIXO-MÉDIO — mean-reversion intraday é crowded | ~30k barras/mês × 30 meses = alto | ALTO — fácil overfittar threshold | MÉDIO — cuidar de overlap de labels | FRACO ⚠️ |

### Turno 7 — Decisão do conselho

**Tese escolhida para avançar à Fase 3 (stress-test e então Fase A formal):**

🏆 **O1 — Momentum pós-evento macro em WDO**

Racional consolidado:
- Economic rationale sólido (lag de ajuste USDBRL spot → mini; hedge de dealers)
- Falsificável (IC entre feature-momentum-pós-evento e retorno direcional 5-30 min)
- Dataset trades-only suporta (eventos têm timestamp conhecido; bars 1-5 min computáveis)
- Kill criteria ex-ante viáveis (DSR<0, IC out-of-CI em 2 períodos, drift condicional a regime macro)
- Escapa dos 7 anti-padrões da lista negativa
- Mira dá verdict FORTE; Nova dá AUDIT-OK; Nelo dá LIVE-READY
- Cost-to-develop: médio (precisa calendário macro + mapeamento evento→timestamp)

**Próxima ação:** Fase 3 — Stress-test de 15 minutos (red-team pelos 4 agentes tentando matar a tese) antes de abrir Fase A formal com o template canônico.

---

### Turno 8 — Fase 3: Stress-test red-team em O1 (4 agentes tentam matar a tese)

**Regra do red-team:** cada agente apresenta o ataque mais forte possível contra O1; Kira decide se o ataque mata (KILL), fere (WOUND — vira constraint na Fase A) ou falha (DEFLECTED).

#### 8.1 — Mira (ML viability) ataca: **Sample size real vs aparente**

> "Vocês disseram ~15k janelas, mas eventos macro de alto impacto (Copom, FOMC, CPI-BR, CPI-US, payroll) somados dão ~15 eventos/mês × 30 meses = **~450 eventos relevantes**, não 15k. As 15k barras pós-evento são observações fortemente correlacionadas (autocorrelação intra-evento). Sample efetivo para um teste IC no horizonte 5-30 min é da ordem de 400-600, o que dá power baixo para detectar IC ≥ 0.03 com p<0.01 pós-Bonferroni. Overfitting risk sobe porque temos poucos eventos mas muitos hiperparâmetros candidatos (janela, tipo de evento, filtro de regime de vol, horizonte)."

**Kira verdict:** ⚠️ WOUND. Vira constraint:
- N_trials controlado por lista pré-registrada ex-ante (≤5 variantes); Bonferroni calibrado para N=5
- Unidade de análise = **1 evento** (não barra); autocorrelação dentro do evento tratada com bloco embargo
- Kill criterion ex-ante: DSR<0 OU PBO>0.4 (rigoroso, reflete sample pequeno)

#### 8.2 — Nova (microestrutura) ataca: **O "lag" é frontrunado por HFT**

> "A premissa do lag USDBRL spot → WDO mini existe em livro-texto, mas em 2026 com HFTs B3 roteando via DMA o ajuste não espera 5-30 min. A inércia real observável em trades-only provavelmente colapsou para <60s — abaixo do nosso horizonte mínimo de 1 bar. Se o lag sobreviver, é apenas em eventos com **surpresa direcional alta** (expectativa vs realizado), não em todos os releases. O efeito é condicional a surpresa e a regime, não universal."

**Kira verdict:** ⚠️ WOUND. Vira constraint:
- Tese foca em **subset de eventos com surpresa direcional mensurável** (proxy: desvio do consensus Bloomberg/Reuters), não em todos os releases macro
- Horizonte mínimo testado sobe para 3-5 min (evita janela dominada por HFT sub-minuto)
- Teste de robustez obrigatório: IC por tercil de surpresa (alta/média/baixa); se alpha só aparece em tercil alto, tese é "momentum condicional a surpresa", não "momentum pós-evento"

#### 8.3 — Nelo (availability live) ataca: **Timestamp de evento não é confiável no feed**

> "Eu entrego trades com timestamp BRT naive do callback, mas o timestamp de **release do evento macro** (ex: CPI-BR às 09:00 ou Copom 18:30) é externo. Fontes públicas (B3, banco central) têm precisão de minuto, não segundo. Para a tese funcionar em live, precisamos um segundo feed de calendário macro sincronizado com relógio do servidor onde o loop roda. Se o timestamp do evento chega 30-90s atrasado, metade do alpha do 1º minuto pós-evento é perdido. Além disso: alguns releases têm **horário variável** (Copom: decisão sai aprox 18:30 mas publicação real pode variar ±2 min), o que torna a janela alvo instável."

**Kira verdict:** ⚠️ WOUND. Vira constraint:
- Arquitetura Fase B exige: (1) fonte canônica de calendário macro (Investing.com API ou equivalente) (2) clock skew monitorado entre fonte-calendário e feed ProfitDLL (3) tolerância ±60s no timestamp do evento aplicada em backtest também (não só live)
- Eventos de horário variável (Copom statement, FOMC press conference) entram com **janela alargada** e são marcados separadamente (label: "scheduled_variable")
- Em backtest Fase E, simular cenário "timestamp do evento +60s" como stress regime

#### 8.4 — Kira (self-red-team, científico) ataca: **Economic rationale é post-hoc?**

> "Pergunta honesta: se backtest falhar, vamos dizer 'ah, mas em 2023-2025 o regime era atípico' ou 'HFT evoluiu'? Essa tese tem a gramática clássica de narrativas irrefutáveis. Precisamos de um teste **out-of-sample fora do período de construção** + um teste que seria capaz de **refutar** a tese (Popper). Sem isso, é só storytelling."

**Kira verdict (sobre si mesma):** ⚠️ WOUND. Vira constraint:
- Período de construção congelado: **2024-01 a 2025-06** (18 meses in-sample)
- **Hold-out virgem**: 2025-07 a 2026-04 (10 meses out-of-sample) — nunca tocado durante desenvolvimento
- Falsificador pré-registrado: "Se IC no hold-out < 50% do IC in-sample, tese falha" (não é kill criterion durante Fase E; é **critério de não-prosseguimento** Fase E→F)
- Pré-registrar o hold-out no thesis.md antes de Beckett rodar CPCV

#### 8.5 — Consolidação: O1 sobrevive com 4 WOUNDS

| Ataque | Veredito | Constraint resultante |
|--------|----------|----------------------|
| Sample size efetivo pequeno | WOUND | N_trials ≤5 pré-registrado; unidade=evento; DSR<0 OR PBO>0.4 |
| HFT frontrunning colapsou lag | WOUND | Subset "surpresa direcional alta"; horizonte 3-5 min mínimo |
| Timestamp de evento impreciso | WOUND | Calendário canônico + clock skew monitor; ±60s tolerance |
| Economic rationale post-hoc | WOUND | Hold-out virgem 2025-07→2026-04; falsificador pré-registrado |

**Nenhum ataque mata.** 4 constraints endurecem a tese. O1 avança à Fase A formal com scope reduzido e kill criteria mais rigorosos que o dry-run T001.

### Turno 9 — Humano invalida O1 (constraint de arsenal)

Humano observa: **não temos feed de eventos macro confiável**. Toda a constraint 8.3 (Nelo) vira bloqueante, não apenas caveat. O1 é retirada da corrida.

Humano delega ao conselho: **"vocês decidem a tese mais plausível considerando o arsenal que temos"**. Kira reabre deliberação com restrição de arsenal explícita.

### Turno 10 — Arsenal real auditado (input comum para todos os votos)

**O que temos (confirmado):**

| Item | Estado |
|------|--------|
| Feed trades WDO via TNewTradeCallback | ✅ preço, volume, timestamp BRT naive, tradeType (agressão) |
| Histórico WDO trades-only | ✅ ~2024-01 → 2026-04 (~27 meses após backfill Sentinel) |
| Relógio servidor | ✅ confiável para qualquer janela determinística |
| Multiplier WDO R$10/ponto | ✅ canônico no glossário |
| Calendário macro externo sincronizado | ❌ NÃO TEMOS |
| Feed de book | ❌ R7 proíbe (trades-only) |
| tradeType (BUY/SELL agressão) | ✅ no callback |
| WIN correlato | ✅ disponível como exógena |

**Candidatas reativadas (exceto O1):**

| # | Tese | Depende de feed externo? |
|---|------|--------------------------|
| O2 | Mean-reversion condicional overextension | NÃO |
| O3 | Opening range break | NÃO |
| O4 | VPIN defensivo (filtro, não standalone) | NÃO |
| O5 | End-of-day inventory unwind | NÃO |

### Turno 11 — Voto independente de cada agente (arsenal-aware)

#### 11.1 — Kira (científico)

> "Priorizo **economic rationale estrutural + falsificabilidade + sample viável**. O5 tem microestrutura sólida (dealers limitam VaR overnight) + janela determinística + falsificador claro (IC no hold-out). O2 é crowded e difícil de separar de ruído. O3 é overplayed mas determinístico — não descarto como módulo. O4 é filtro, não alpha standalone. **Voto: O5 primária, O4 como módulo de regime defensivo se sobreviver Fase E.**"

#### 11.2 — Mira (ML viability)

> "Reviso meu verdict do Turno 6 com arsenal-aware: O5 tem sample ~500 dias, mas expandindo para painel de 4 janelas dentro da última hora (16:55, 17:10, 17:25, 17:40) × 500 dias = **~2000 obs efetivas com efeitos fixos de dia** — suficiente para IC com N_trials≤5 Bonferroni. Overfitting risk controlável porque threshold de magnitude é 1 parâmetro pré-registrado. O2 tem sample grande (~900k barras) mas IC esperado baixo e crowded. **Voto: O5, porque sample é tratável e estrutura é mais parcimoniosa que O2.**"

#### 11.3 — Nova (microestrutura)

> "Efeito de unwind de dealers em fim de pregão é documentado em múltiplos futuros de FX emergentes (USDMXN, USDZAR têm papers) e é **estrutural, não moda**. Em WDO, o call de fechamento 17:55-18:00 força redução de posição — isso não é arbitrado por HFT porque é **fluxo obrigatório de risco**, não predição. O3 opening range: racional existe (institucional forma level na 1ª meia hora), mas o efeito em WDO é fraco porque abertura 09:30 é dominada por fluxo de rollover EUR/USDBRL de overnight. O2: crowded, sem edge diferencial. **Voto: O5 primária; O3 como alternativa se conselho quiser redundância.**"

#### 11.4 — Nelo (availability live)

> "Todas 4 são `computable` em trades-only exceto O4 que é `partial` (VPIN clássico usa bucket de volume; versão com agressão do tradeType funciona). Peso a **robustez de execução**: O5 tem janela determinística (sei em que minuto operar); O2/O3 dependem de threshold em tempo real (mais fragil a parametrização). **Voto: O5, pela simplicidade de execução live.**"

### Turno 12 — Convergência (unânime)

| Agente | Voto | Score sob novas constraints |
|--------|------|----------------------------|
| Kira | O5 primária | 4.5 (up de 4.3) |
| Mira | O5 | FORTE (up de OK-com-caveat; sample resolvido via painel) |
| Nova | O5 | AUDIT-OK (estrutural, não moda) |
| Nelo | O5 | LIVE-READY (determinística) |

**🏆 Tese vencedora: O5 — End-of-day Inventory Unwind WDO**

Escopo formal (input para T002):
- **Janela de entrada:** 4 pontos {16:55, 17:10, 17:25, 17:40} BRT (painel)
- **Janela de saída:** 17:55 BRT (fim do contínuo)
- **Feature primária direcional:** `intraday_flow_direction` = sign(close_16:55 − open_dia)
- **Feature condicional:** `intraday_flow_magnitude` = |return_open_to_16:55| / ATR_20d — só opera se > P60
- **Feature regime vol:** `atr_day_ratio` = ATR_dia / ATR_20d — só opera se ATR_dia ∈ [P20, P80]
- **Label:** `ret_forward_to_17:55` para cada ponto de entrada
- **Direção:** fade (contra o fluxo acumulado do dia)
- **Hold-out virgem:** 2025-07 → 2026-04 (10 meses), nunca tocado em desenvolvimento
- **Sample in-sample:** 2024-01 → 2025-06 (18 meses) × 4 janelas ≈ 1500 obs
- **Kill criteria ex-ante:**
  1. DSR < 0 na CPCV → tese é ruído
  2. PBO > 0.4 → overfitting severo (mais rigoroso que default 0.5 por sample pequeno)
  3. IC hold-out < 50% do IC in-sample → efeito arbitrado ou regime-dependente
  4. Drawdown > 3σ acima do budget Riven em paper → kill imediato
- **N_trials pré-registrado:** ≤5 (4 janelas × 1 threshold configurações + 1 baseline sem filtro regime); Bonferroni N=5
- **Módulo opcional futuro:** O4 (VPIN defensivo) pode entrar como filtro se Fase E indicar tail loss concentrado em toxic-flow days

### Turno 13 — Handoff para Fase A formal

Conselho fecha votação. Kira assume handoff:

1. Cria `docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md` usando `squads/quant-trading-squad/templates/thesis-tmpl.yaml`
2. Aciona Mira/Nova/Nelo para 3 artefatos de consulta: `docs/research/audits/T002-{mira,nova,nelo}-audit.md`
3. Mira exporta `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml` com SHA256 real (G002 canônico)
4. Kira sela §11 Gate Signature A→B

**Próxima ação:** criar artefatos Fase A agora.
