# Architecture Design — T001 Bar-Close Momentum WDO 5-min

**Owner:** Aria (@architect)
**Status:** DRY-RUN (smoke-test Q-SDC Fase B)
**Data:** 2026-04-21 BRT
**Input:** thesis T001 + spec v0.1.0
**Consultores:** Dara (@data-engineer), Nelo (@profitdll-specialist), Beckett (@backtester)

---

## 1. Módulos afetados

| Pacote | Impacto | Novo? |
|--------|---------|-------|
| `src/features/momentum/` | NOVO — implementa `mom_3bar` | SIM |
| `src/data/bar_aggregator/` | NOVO — agregação trades → 5-min OHLCV | SIM |
| `src/data/session_filter/` | NOVO — filtro fases B3 | SIM |
| `src/labels/regression/` | NOVO — next-bar return label | SIM |
| `src/backtest/runner/` | EXISTE (Beckett) — integrar via spec YAML | NÃO |
| `src/storage/parquet/` | EXISTE (Dara) — reaproveitar | NÃO |

---

## 2. Interfaces públicas

### `bar_aggregator`
```python
def aggregate_trades_to_bars(
    trades: pd.DataFrame,  # colunas: ts_brt, price, qty, trade_type
    bar_size_minutes: int = 5,
) -> pd.DataFrame:  # colunas: ts_bar_open_brt, ts_bar_close_brt, open, high, low, close, volume_contracts, volume_brl
```

### `session_filter`
```python
def filter_continuous_session(
    bars: pd.DataFrame,
    asset: str = "WDO",
) -> pd.DataFrame:  # filtra 09:30-17:55 BRT, exclui pré-abertura/leilões/rollover window
```

### `features.momentum`
```python
def compute_mom_3bar(bars: pd.DataFrame) -> pd.Series:  # retorna série alinhada ao ts_bar_close
```

### `labels.regression`
```python
def compute_next_bar_return(bars: pd.DataFrame) -> pd.Series:  # label log(close[t+1]/close[t])
```

---

## 3. Dependências e data contract

```
ParquetStore (Dara)
   ↓ read trades-only WDO 2023-2026
bar_aggregator
   ↓ bars 5-min OHLCV
session_filter
   ↓ bars 5-min filtered
features.momentum + labels.regression (paralelo)
   ↓ (X, y) alinhado
backtest.runner (Beckett) ← spec YAML Mira
   ↓ CPCV results
docs/backtests/T001-cpcv-20260421.md
```

---

## 4. Decisões tech

- **Python 3.11** (já padrão do projeto)
- **Pandas 2.x** para agregação/features
- **Polars** considerado mas descartado para smoke-test (Pandas suficiente; migrar depois se volume exigir)
- **Timezone:** BRT naive em todas DataFrames (R2 MANIFEST)
- **Sem nova dependência externa** fora das já presentes no projeto

---

## 5. Consulta Dara (storage)

- [x] Schema parquet atual (trades-only) é suficiente — não precisa migration
- [x] Nenhuma coluna nova em storage; bars são computados em-memória ou cache local
- [x] Rollback plan: N/A (sem migration)

**Dara verdict:** NO-OP — não toca storage

---

## 6. Consulta Nelo (DLL)

- [x] Pipeline é 100% histórico — não toca callback DLL
- [x] Para live depois (fora do dry-run), `bar_aggregator` precisaria wrapper para consumir TNewTradeCallback em tempo real e fechar bars a cada 5 min
- [x] Availability `computable` do spec é respeitada

**Nelo verdict:** LIVE-READY quando chegar a hora; dry-run não aciona DLL

---

## 7. Consulta Beckett (simulador contract)

- [x] Spec YAML v0.1.0 bate com contrato do simulador (CPCV, metrics, costs)
- [x] Stress-regimes listados no spec são suportados
- [x] Contract multiplier R$10/ponto — Beckett deve ler do spec, NÃO hardcodar

**Beckett verdict:** CONTRACT-OK

---

## 8. Riscos arquiteturais

| Risco | Severidade | Mitigação |
|-------|-----------|-----------|
| `bar_aggregator` mal implementado → leakage por uso de trade DEPOIS do close do bar | 🔴 | Teste unitário obrigatório de timestamp < bar_close |
| `session_filter` exclui rollover incorretamente → sample size cai | ⚠️ | Teste de integração com 1 mês histórico |
| BRT vs UTC drift em scheduler | 🔴 | Quinn check obrigatório (R2) |

---

## 9. Gate de saída Fase B

- [x] Interfaces públicas definidas
- [x] Data contract diagramado
- [x] Dara/Nelo/Beckett consultados e OK
- [x] Sem conflito com arquitetura atual do projeto

**Verdict:** PASS — liberado para Fase C (Morgan→River→Pax)
