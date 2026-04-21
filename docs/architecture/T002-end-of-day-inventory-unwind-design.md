# T002 — End-of-Day Inventory Unwind WDO — Design Técnico (Fase B)

**Owner:** Aria (@architect)
**Data:** 2026-04-21 BRT
**Fase:** B — Architecture
**Input:** `docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md` + `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml` (sha256 `c7c020ef…0b751`)
**Output:** este documento → handoff para River (Fase C — story)

---

## 1. Goal do design

Traduzir a spec imutável Mira→Beckett em uma arquitetura executável que sirva simultaneamente:

1. **Backtest** (Beckett, Fase E): consumo do spec YAML + dataset histórico trades-only + CPCV 45 paths
2. **Paper-mode** (Fase F): mesma engine de sinal rodando contra feed live da ProfitDLL, sem ordens reais
3. **Live** (Fase H, se kill criteria sobreviverem): Tiago liga SendOrder via gateway Riven

**Princípio de design:** *uma única implementação da engine de sinal*. Backtest e live divergem apenas no adapter de feed e no adapter de execução — nunca na lógica de decisão. Isto elimina drift backtest↔live.

---

## 2. Arquitetura em camadas

```
┌─────────────────────────────────────────────────────────────┐
│  1. FEED ADAPTER (pluggable)                                │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │ HistoricalTradesReplay │  │ ProfitDLLLiveFeed      │    │
│  │ (Fase E)               │  │ (Fase F + H)           │    │
│  └───────────┬────────────┘  └───────────┬────────────┘    │
│              └─────────────┬─────────────┘                  │
│                            ▼                                │
│                   TradeEvent(ts, price, qty, side)          │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  2. SESSION STATE BUILDER (pure, stateful, O(1) per trade)  │
│  - open_day (primeiro trade pós 09:30:00)                   │
│  - last_price / last_ts                                     │
│  - session_high, session_low → ATR_day (atualizado online)  │
│  - closed_bars registry (últimos preços às 16:55/17:10/...) │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  3. FEATURE COMPUTER (pure, triggered por relógio/timestamp)│
│  Dispara nos entry_timestamps {16:55, 17:10, 17:25, 17:40}: │
│    intraday_flow_direction  = sign(close[t] - open_day)     │
│    intraday_flow_magnitude  = |close[t]-open_day| / ATR_20d │
│    atr_day_ratio            = ATR_day / ATR_20d             │
│  Recebe context rolling (ATR_20d, P20/P60/P80) de cache     │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  4. SIGNAL RULE (pure function, ZERO side effects)          │
│  Input:  features + trial_id (T1..T5)                       │
│  Output: Signal(direction ∈ {LONG, SHORT, FLAT}, reason)    │
│  Regra T1 baseline:                                         │
│    if magnitude > P60 AND atr_ratio ∈ [P20,P80]:            │
│        direction = -sign(flow_direction)  # FADE            │
│    else:                                                    │
│        direction = FLAT                                     │
└──────────────────────────┬─────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  5. EXECUTION ADAPTER (pluggable)                           │
│  ┌────────────────────────┐  ┌────────────────────────┐    │
│  │ BacktestBroker         │  │ RivenGate→TiagoExec    │    │
│  │ (Beckett slippage model)│ │ (R3 + R4)              │    │
│  └───────────┬────────────┘  └───────────┬────────────┘    │
│              └─────────────┬─────────────┘                  │
│                            ▼                                │
│                    Fill(ts, price, qty, fees)               │
└─────────────────────────────────────────────────────────────┘
```

**Benefício crítico:** camadas 2-3-4 são **idênticas** em backtest e live. Garante que backtest reflete com fidelidade o comportamento live — e vice-versa. Zero código duplicado, zero drift.

---

## 3. Warm-up (pré-condição obrigatória)

Antes de qualquer sessão operar, duas estruturas precisam estar prontas:

### 3.1. ATR_20d rolling

| Fonte | Método |
|-------|--------|
| Histórico | `ProfitDLL.GetHistoryTrades` chamado em thread worker (NÃO no callback — quirk Nelo) para últimos 30 dias úteis |
| Agregação | Trades → OHLC diário em memória |
| Saída | `ATR_20d_today = average(true_range[D-20:D-1])` |
| Persistência | Cache em `state/T002/atr_20d.json` atualizado ao final de cada sessão |

### 3.2. Percentis rolling 252d (P20, P60, P80)

Para `|ret_acumulado_dia|/ATR_20d` e `ATR_day/ATR_20d`:

| Fonte | Método |
|-------|--------|
| Build offline | Batch job que consome dataset histórico, agrupa por dia, computa a série de `magnitude` e `atr_ratio` dos últimos 252 dias úteis |
| Persistência | `state/T002/percentiles_252d.json` — atualizado 1× ao fim de cada sessão |
| Runtime | Carrega do JSON no startup da sessão; NÃO recomputa durante o pregão |

### 3.3. Warm-up state machine

```
startup → WARM_UP_IN_PROGRESS
  ├─ ATR_20d OK AND percentiles_252d OK → READY_TO_TRADE
  └─ qualquer falha → WARM_UP_FAILED (loga Quinn, DIA IGNORADO)
```

**Regra canônica:** nenhum sinal pode disparar com estado ≠ `READY_TO_TRADE`. Fail-closed.

---

## 4. Integração com gateway Riven (R4 — budget authority)

Toda ordem candidata passa pelo gateway Riven antes de chegar em Tiago:

```
Signal(LONG, reason) ──▶ RivenGate.authorize(signal, context)
                            │
                            ├─ ok, N_contracts = K ──▶ Tiago.send_order(LONG, K)
                            ├─ ok, N = 0           ──▶ log + no trade (budget esgotado)
                            └─ reject              ──▶ log + kill event (R10)
```

**Context passado ao Riven:**
- Strategy ID (T002-end-of-day-unwind)
- Capital em uso atual
- DD atual vs budget (bps)
- Número de trades abertos de outras estratégias
- Volatilidade estimada ATR_day

**Riven decide K** (número de contratos) via Kelly fracionado + constraint de budget (não detalhado aqui — Riven é owner exclusivo dessa lógica).

---

## 5. Integração com Tiago (R3 — SendOrder monopoly)

Tiago recebe ordens autorizadas via interface única:

```python
# contrato (spec, não código)
TiagoExecutor.send_order(
    strategy_id: str = "T002",
    direction: Literal["LONG", "SHORT"],
    n_contracts: int,  # vindo de Riven, não de signal
    order_type: Literal["MARKET", "AGGRESSIVE_LIMIT"] = "MARKET",
    exit_deadline_brt: time,  # "17:55:00" — hard stop
)
```

**Tiago responsibilities** (fora deste design; seu escopo):
- Chunking se K > tamanho de ordem admissível
- Retry em rejeição da B3
- Enforcing `exit_deadline_brt`: às 17:55:00 força saída a mercado de qualquer posição aberta do T002
- EOD reconciliation (R9)

---

## 6. Clock authority e janelas determinísticas

**Fonte de verdade do relógio:** relógio do servidor sincronizado via NTP.

| Componente | Relógio |
|-----------|---------|
| Backtest | Relógio do evento (ts do trade replayed) |
| Live | Relógio do servidor (NTP-synced) |

**Loop de timing live:** thread que verifica a cada 500ms se `now_brt ≥ next_entry_timestamp`. Ao disparar, consome snapshot do state → computa features → aplica signal rule.

**Drift check:** Gage monitora drift NTP. Se drift > 2s, componente sinaliza `CLOCK_UNSAFE` e R10 kill-switch nível 1 é acionado (pausar novas entradas; posições abertas respeitam exit deadline).

---

## 7. Calendário estático (Copom, feriados, vencimentos)

Arquivo versionado `config/calendar/2024-2027.yaml` com estrutura:

```yaml
copom_meetings: ["2024-01-31", "2024-03-20", ...]
br_holidays: ["2024-01-01", "2024-02-12", ...]
wdo_expirations: ["2024-01-02", "2024-02-01", ...]  # 1º dia útil do mês
pre_long_weekends_br_with_us_open: ["2024-02-12", ...]
```

**Ownership:** humano mantém anualmente; Nelo lê no startup; Sable audita coerência (R14).

**Uso:**
- `post_copom_exclusion: true` no spec → skip dias no sample training que são D+0 de Copom (Nova constraint 3)
- `rollover_exclusion: "D-3 a D-1"` → skip 3 dias antes de cada vencimento
- Stress regime breakdown Fase E usa o calendário para classificar dias

---

## 8. Observability (what Quinn will test / Sable will audit)

Cada decisão produz **telemetria estruturada** (escrita em `logs/T002/decisions_YYYYMMDD.jsonl`):

```json
{
  "ts_brt": "2026-04-21T16:55:00",
  "strategy_id": "T002",
  "trial_id": "T1",
  "session_state": {
    "warm_up_status": "READY_TO_TRADE",
    "clock_drift_ms": 34,
    "open_day": 5234.0,
    "close_now": 5248.5,
    "atr_20d": 22.3,
    "atr_day_so_far": 19.8
  },
  "features": {
    "intraday_flow_direction": 1,
    "intraday_flow_magnitude": 0.65,
    "atr_day_ratio": 0.89
  },
  "thresholds_used": {
    "magnitude_P60": 0.52,
    "atr_day_P20": 0.45,
    "atr_day_P80": 1.62
  },
  "signal": {
    "direction": "SHORT",
    "reason": "magnitude>P60 AND atr_ratio in [P20,P80] AND flow_up"
  },
  "riven_decision": {
    "authorized": true,
    "n_contracts": 2,
    "budget_remaining_bps": 47
  },
  "tiago_outcome": {
    "order_id": "...",
    "filled_avg_price": 5248.0,
    "fees_rs": 3.50
  }
}
```

Este log é o **ground truth** para: (1) EOD reconciliation (R9), (2) Quinn code audit, (3) Sable coherence audit, (4) Beckett backtest replay comparison.

---

## 9. Failure modes e fallbacks

| Evento | Detector | Ação | Severidade |
|--------|----------|------|------------|
| Feed para > 30s na janela 16:55-17:55 | FeedWatchdog | Sinalizar `FEED_STALE`; signal rule retorna FLAT até retomar | MÉDIA |
| Clock drift > 2s vs NTP | ClockMonitor | R10 kill-switch nível 1 (pausa novas entradas) | ALTA |
| Warm-up falhou ao startup | WarmUpGate | `WARM_UP_FAILED`; dia inteiro ignorado; alerta Quinn | ALTA |
| Ordem rejeitada pela B3 | Tiago (seu escopo) | Retry político; falha persistente → R10 nível 2 | MÉDIA |
| Posição aberta às 17:55:00 | Tiago | Força market sell/buy — não respeita outros critérios | CRÍTICA |
| State file corrupto (atr_20d.json / percentiles.json) | WarmUpGate | Rebuild from scratch; se > 10 min, DIA IGNORADO | MÉDIA |
| Dia pós-Copom em live | Filter | Skip entries inteiras (respeita spec) | BAIXA |

---

## 10. Package / módulo layout proposto

Alinhado ao princípio da Constitution (Article VI — Absolute Imports) e à convenção do projeto algotrader:

```
packages/
  t002_eod_unwind/
    __init__.py
    adapters/
      feed_historical.py          # Fase E
      feed_profitdll_live.py      # Fase F + H
      exec_backtest.py            # Fase E
      exec_live.py                # Fase F + H (wraps Riven + Tiago)
    core/
      session_state.py            # Layer 2 (pure)
      feature_computer.py         # Layer 3 (pure)
      signal_rule.py              # Layer 4 (pure) — T1..T5 variants
      schedule.py                 # Timing loop
    warmup/
      atr_20d_builder.py
      percentiles_252d_builder.py
      gate.py                     # WARM_UP state machine
    telemetry/
      decision_logger.py
    config/
      trials.yaml                 # T1..T5 definitions (mirror do spec)
    tests/
      test_session_state.py
      test_feature_computer.py
      test_signal_rule.py
      test_warmup.py
      test_integration_backtest.py
      test_integration_live_paper.py
```

**Import convention:** `from algotrader.packages.t002_eod_unwind.core.signal_rule import compute_signal` (absolute).

---

## 11. O que é escopo do T002 vs. framework

| Item | Onde vive | Owner |
|------|-----------|-------|
| Engine de sinal T002 | `packages/t002_eod_unwind/` | Dex implementa a partir de story River |
| Gateway de budget | framework compartilhado (outras estratégias reusam) | Riven define interface; Aria valida |
| Executor Tiago SendOrder | framework compartilhado | Tiago é monopolista (R3) |
| Calendar file | `config/calendar/` | humano + Nelo |
| CPCV runner Beckett | framework | Beckett |
| Kill-switch R10 | framework | Riven |

---

## 12. Gate Signature — Fase B → Fase C

```yaml
gate_B_signature:
  verdict: pass
  signed_by: Aria (@architect)
  signed_at_brt: "2026-04-21T18:00:00"
  thesis_ref: "docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md"
  spec_ref: "docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml"
  spec_hash: "sha256:c7c020ef987abe17d1246feab930087742c97d7731fbfd7e5a3711082c50b751"
  design_invariants:
    - "engine de sinal é PURA e compartilhada entre backtest e live (layers 2-3-4)"
    - "backtest↔live divergem apenas nos adapters (layer 1 e 5)"
    - "fail-closed: warm-up não-READY ⇒ zero sinais"
    - "Tiago é monopolista de SendOrder (R3); Nelo apenas sinaliza"
    - "Riven autoriza K contratos (R4); signal rule não decide sizing"
    - "Gage monitora clock drift; >2s ⇒ R10 nível 1"
  next_phase: C
  next_owner: River (@sm) — criar story T002.1 + Pax valida
```

**Assinatura:** Aria (@architect) — 2026-04-21 BRT
