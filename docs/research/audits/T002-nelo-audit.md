# T002 — Nelo Audit (Availability Live / *callback-spec)

**Thesis:** T002 — End-of-Day Inventory Unwind WDO
**Owner:** Nelo (@profitdll-specialist)
**Data:** 2026-04-21 BRT
**Comando de origem:** `*callback-spec`

---

## 1. Availability tag por feature

| Feature | Tag | Como computar no callback real-time |
|---------|-----|-------------------------------------|
| `open_dia` | `computable` | Primeiro trade recebido após 09:30:00 BRT no TNewTradeCallback; armazenar em estado de sessão |
| `close[t]` para t ∈ {16:55, 17:10, 17:25, 17:40} | `computable` | Último trade recebido antes do timestamp alvo; polling por relógio do servidor |
| `intraday_flow_direction` | `computable` | `sign(close[t] − open_dia)`, O(1) |
| `intraday_flow_magnitude` | `computable` | `abs(close[t] − open_dia) / ATR_20d`; ATR_20d pré-computado no startup a partir de `GetHistoryTrades` (warm-up), atualizado ao fim de cada sessão |
| `atr_day_ratio` | `computable` | ATR_dia computado em memória (rolling high-low durante o dia); dividido por ATR_20d |
| Filtros P20/P60/P80 | `computable` | Percentis rolling 252d; recalcular ao final de cada sessão, usar do dia anterior |

Todas `computable`. **Nenhuma `live_only` nem `partial`.**

## 2. Orçamento de latência

| Operação | Tempo esperado | Orçamento disponível |
|----------|---------------|----------------------|
| Receber trade do callback | driven by feed | — |
| Computar `intraday_flow_*` | < 1ms | folga enorme |
| Decisão de trade em t ∈ {janelas} | polling 1s no loop principal | janela de 15 min folga total |
| Envio de ordem SendOrder | p50=20ms, p95=60ms, p99=100ms, tail=500ms (DMA2) | ordem em 16:55:00 chega na mesa antes de 16:55:01 |
| Execução na bolsa | variável (ordem a mercado) | janela de 15 min até próxima entrada |

**Conclusão:** latência é **não-binding** para esta tese. Horizonte intra-janela de 15 min absorve ordens de magnitude acima do necessário.

## 3. Warm-up requirements

Na inicialização do trading live:
1. **ATR_20d baseline:** chamar `GetHistoryTrades` para últimos 30 dias úteis → agregar em OHLC diário → ATR(20)
   - Alerta: GetHistoryTrades tem quirks (não chamar do callback; usar thread worker)
   - Warm-up deve completar ANTES da abertura às 09:30; falha em warm-up ⇒ NÃO operar hoje (state: `WARM_UP_FAILED`)
2. **Percentis rolling 252d:** requer 252 dias de histórico de `|ret_acumulado_dia|` e `ATR_dia`. Pré-computar offline (batch) e carregar no startup.
3. **Calendário Copom / feriados / vencimentos:** arquivo estático `config/calendar-2024-2027.yaml` — humano mantém, Nelo lê.

## 4. Verificação dos quirks DLL

- [x] `TNewTradeCallback` entrega timestamp BRT naive direto — sem conversão (R2)
- [x] Nenhum uso de `GetHistoryTrades` dentro do callback (quirk confirmado no Whale Detector v2 live)
- [x] Agent name resolvido via `GetAgentName` na engine thread se necessário (não usado na tese atual)
- [x] Finalize (não DLLFinalize) no shutdown
- [x] Strings c_wchar_p em callbacks (WINFUNCTYPE)
- [x] Exchange code `"F"` para WDO mini

## 5. Execução (interface com Tiago)

| Evento | Ação |
|--------|------|
| Sinal disparado em t | Tiago monopólio de SendOrder (R3) — Nelo apenas sinaliza "trade autorizado" via gateway Riven |
| Tipo de ordem | Market (ou aggressive limit se Tiago preferir controle de slippage) |
| Saída | 17:55:00 hard stop OR triple-barrier (Fase E decide) |
| Position sizing | Riven define via budget gate (R4) — Nelo não opina |

## 6. Fallback / failure modes

| Evento | Ação |
|--------|------|
| Feed para entre 16:55 e 17:55 (sem trades por > 30s) | Abort trades abertos OU skip próxima janela (Tiago decide política) |
| Relógio do servidor drift > 2s vs NTP | Alertar Gage; não operar até sincronizar |
| Warm-up falha ao startup | `WARM_UP_FAILED`, dia ignorado, alerta Quinn |
| Ordem rejeitada pela B3 | Tiago gerencia retry; se falha persistente → kill-switch (R10) |

## 7. Verdict

**LIVE-READY ✅**

Nenhuma dependência de book, nenhuma dependência de feed externo, nenhuma dependência de timestamp preciso além do relógio local. Tese é **trivial para operar live** assumindo warm-up bem-sucedido.

Caveat: warm-up depende de `GetHistoryTrades` funcionar estavelmente — já validado no Whale Detector v2 mas precisa retestar em Fase F (paper-mode) antes de capital real.

**Assinatura:**
Nelo (@profitdll-specialist) — 2026-04-21T17:25:00 BRT
