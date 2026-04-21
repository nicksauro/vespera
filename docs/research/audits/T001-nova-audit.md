# Nova Microstructure Audit — T001 Bar-Close Momentum WDO 5-min

**Owner:** Nova (@market-microstructure)
**Command:** `*audit-feature`
**Thesis ref:** docs/research/thesis/T001-bar-close-momentum-wdo-5min.md
**Data:** 2026-04-21 BRT

---

## 1. Sentido microestrutural B3

Momentum 5-min em WDO é defensável em regime de inércia pós-informação:
- Fluxo de dealers ajustando hedge cambial
- Lag USDBRL spot ↔ futuro mini (1-5 min típico)
- Eventos catalizadores: intervenção BCB, CPI Brasil, payroll/FOMC US

**NÃO vale em:**
- Pré-abertura (08:55-09:00) — não há preço formado, só coleta de ordens
- Leilão de determinação (09:00-09:30) — preço único, momentum não faz sentido
- Call de fechamento (17:55-18:00) — auction, dinâmica diferente
- Regime de baixa vol (ATR < P20) — inércia colapsa em ruído

## 2. Fases de pregão (constraint para session_filter)

| Fase | Horário BRT | Momentum usável? |
|------|-------------|------------------|
| Pré-abertura | 08:55-09:00 | ❌ excluir |
| Leilão de determinação | 09:00-09:30 | ❌ excluir |
| Contínuo | 09:30-17:55 | ✅ incluir |
| Call de fechamento | 17:55-18:00 | ❌ excluir |

Grade [WEB-CONFIRMED 2026-03-09 grade pós-DST]. Mudança sazonal possível.

## 3. Rollover

- WDO vencimento = 1º dia útil do mês → migração de liquidez para próximo vencimento em D-3..D-1
- **Ação:** session_filter exclui esta janela OU aplica haircut de size (Riven)

## 4. RLP / cross / odd-lot

Irrelevante para bar-close de 5-min (ruído diluído na agregação).

## 5. Contract specs (crítico para P&L)

- WDO tick size: 0,5 ponto [WEB-CONFIRMED 2026-01]
- WDO multiplier: **R$ 10/ponto** [WEB-CONFIRMED 2026-04-21 — humano]
- Fonte única: DOMAIN_GLOSSARY Parte 1

**P&L por contrato por ponto:** R$ 10,00.

## 6. Custos (via atlas Nova)

- Emolumentos B3 WDO: [TO-VERIFY via atlas vigente]
- IR day-trade: [TO-VERIFY via atlas vigente]
- Beckett NÃO hardcoda — consome do atlas

## 7. Verdict

**AUDIT-OK** com constraints explícitos:
1. session_filter obrigatório (apenas 09:30-17:55)
2. rollover window exclusion D-3..D-1
3. regime filter recomendado (ATR não-extremo)

---

**Assinado:** Nova (@market-microstructure) — 2026-04-21 BRT
