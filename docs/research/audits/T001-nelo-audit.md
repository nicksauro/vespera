# Nelo Availability Audit — T001 Bar-Close Momentum WDO 5-min

**Owner:** Nelo (@profitdll-specialist)
**Command:** `*callback-spec`
**Thesis ref:** docs/research/thesis/T001-bar-close-momentum-wdo-5min.md
**Data:** 2026-04-21 BRT

---

## 1. Features × availability em live

| Feature | Source no feed | Availability | Observação |
|---------|----------------|--------------|-----------|
| `mom_3bar` | TNewTradeCallback → price + ts | `computable` | Agregação 5-min é trivial no callback |
| `regime_vol_filter` (ATR) | TNewTradeCallback → high/low/close | `computable` | ATR usa OHLC das barras agregadas |

## 2. Callback budget de latência

- `TNewTradeCallback` dispara a cada trade — volume WDO típico: 10-200 trades/s em horário contínuo
- Agregação 5-min em ring buffer: O(1) por trade (update OHLCV)
- Recomputação de `mom_3bar` apenas no close do bar: O(1) custo fixo
- **Budget consumido:** << 1ms por trade → sobra folga para outras features

## 3. Quirks DLL relevantes

- **Timestamp:** BRT naive direto do callback — NÃO converter (R2 MANIFEST)
- **GetHistoryTrades no callback:** PROIBIDO (quirk empírico confirmado pelo squad whale-detector v2) — bar_aggregator deve funcionar puramente com stream de trades, sem consulta retrospectiva
- **Rollover:** WDOFUT (sintético) aponta para vigente; bar_aggregator vê preço sem descontinuidade na troca — mas exposição precisa respeitar contrato específico para fins de posição

## 4. Manual references

- Manual ProfitDLL seção `TNewTradeCallback` — fornece `dPrice`, `nQtd`, `ts_trade` (BRT)
- Nelo atlas Q07-V: `dVol` é volume em R$
- Nelo atlas Q09-E: WDOFUT histórico — para backtest usar arquivos históricos (trades-only parquet), não DLL

## 5. Verdict

**LIVE-READY**

Nenhuma feature de T001 depende de book, nenhuma precisa de GetHistoryTrades no callback, nenhuma excede budget de latência. Quando tese real chegar em live, Nelo confirma que feature pipeline é executável em real-time.

---

**Assinado:** Nelo (@profitdll-specialist) — 2026-04-21 BRT
