# Thesis T002 — End-of-Day Inventory Unwind WDO

**Status:** Fase A — Research (in progress)
**Data:** 2026-04-21 BRT
**Owner:** Kira (@quant-researcher)
**Fase:** A — Research
**Tipo:** Microestrutura (liquidity-driven, determinística)
**Origem:** Quant Council 2026-04-21 — Turno 12 (voto unânime), Turno 13 (handoff)

---

## 1. Decision Framework 4Q (estruturado — template canônico)

```yaml
decision_framework_4q:
  Q1_economic_rationale:
    question: "Existe economic rationale? Quem perde dinheiro do outro lado?"
    answer: yes
    justification: >
      Dealers (bancos market makers em USDBRL) e tesourarias corporativas reduzem
      exposição em WDO nos últimos ~60 min do pregão para limitar VaR overnight e
      ajustar hedge contábil do dia. Esse fluxo é OBRIGATÓRIO (risk desk, não
      discricionário), gerando pressão direcional contrária ao acúmulo intraday.
      Contraparte perdedora: quem entra na direção do fluxo do dia na última hora
      (trend-followers tardios; retail momentum).
    decided_by: Kira
    decided_at_brt: "2026-04-21T17:05:00"

  Q2_falsifiable:
    question: "É falsificável? Consigo escrever H1 com métrica + p-value?"
    answer: yes
    justification: >
      H1: IC_spearman(intraday_flow_direction × (-1), ret_forward_to_17:55) ≥ 0.05
      com p < 0.01 pós-Bonferroni (N_trials=5), em 45 paths CPCV, condicional a
      |intraday_flow_magnitude| > P60 e ATR_dia ∈ [P20, P80].
    decided_by: Kira
    decided_at_brt: "2026-04-21T17:05:00"

  Q3_dataset_support:
    question: "Dataset suporta? Trades-only é suficiente?"
    answer: yes
    justification: >
      Todas as features computáveis de trades-only. Nenhuma dependência de book
      (R7 respeitado). Nenhuma dependência de feed externo (calendário, news).
      Histórico WDO 2024-01→2026-04 (~27 meses). Nelo verdict LIVE-READY.
    decided_by: Kira
    decided_at_brt: "2026-04-21T17:05:00"

  Q4_kill_criteria:
    question: "Kill criteria definíveis ex-ante?"
    answer: yes
    justification: >
      4 critérios pré-registrados: DSR<0, PBO>0.4 (rigoroso por sample pequeno),
      IC_hold-out < 50% IC_in-sample, DD > 3σ budget Riven em paper. Todos
      mensuráveis antes de decisão ir/não-ir para Fase F.
    decided_by: Kira
    decided_at_brt: "2026-04-21T17:05:00"

  gate_result: pass
```

Todos 4Q = YES → gate passa, prosseguir.

---

## 2. Hipóteses (Popperian)

### H0 (nula)
O retorno entre t ∈ {16:55, 17:10, 17:25, 17:40} e 17:55 é independente da direção
do retorno acumulado do dia (open_dia → t), condicional a magnitude > P60 e regime
de vol normal.

### H1 (alternativa)
IC_spearman(−sign(ret_acumulado_dia), ret_forward_to_17:55) ≥ **0.05** em 45 paths
CPCV, com p < 0.01 pós-Bonferroni (N_trials=5), restrito a dias com
|ret_acumulado_dia| > P60 e ATR_dia ∈ [P20, P80].

---

## 3. Especificação

**Universo:** WDOFUT (contrato vigente), sessão contínua 09:30-17:55 BRT.
**Rollover:** excluir D-3 a D-1 do vencimento (MANIFEST — aderente ao padrão Nova).

**Janelas de entrada (painel de 4):** 16:55, 17:10, 17:25, 17:40 BRT.
**Janela de saída:** 17:55 BRT (última barra do contínuo).

**Feature primária direcional:**
- `intraday_flow_direction = sign(close[t] − open_dia)`

**Features condicionais (filtros de regime):**
- `intraday_flow_magnitude = |close[t] − open_dia| / ATR_20d` — operar só se > **P60 rolling 252 dias**
- `atr_day_ratio = ATR_dia / ATR_20d` — operar só se ∈ **[P20, P80]** (evita dias anômalos de vol)

**Direção do trade:** **fade** (contrário ao fluxo do dia).
- Se `intraday_flow_direction > 0` (dia de alta) → SHORT
- Se `intraday_flow_direction < 0` (dia de queda) → LONG

**Label:**
- Primário: `ret_forward_to_17:55 = log(close_17:55 / close[t])`
- Alternativo Fase E: triple-barrier (pt=1.5×ATR_hora, sl=1.0×ATR_hora, timeout=barras até 17:55)

**Métrica primária:** IC_spearman (correlação rank entre `−intraday_flow_direction` e `ret_forward_to_17:55`).
**Métricas secundárias:** Sharpe, Sortino, MAR, hit_rate, profit_factor, max_drawdown, ulcer_index.
**Sample size alvo:** ≥ 1500 obs (4 janelas × ~375 dias pós-filtro em in-sample).

---

## 4. Economic rationale (1 parágrafo)

Dealers que market-makeam USDBRL carregam inventário intraday resultante do fluxo
bilateral de exportadores (venda de dólar) vs importadores/hedgers (compra).
Regras internas de VaR overnight + requisitos regulatórios de capital forçam
redução/zeragem dessa exposição antes do call de fechamento (17:55-18:00).
Tesourarias corporativas replicam o comportamento ajustando hedge cambial no
fechamento contábil. Esse fluxo de liquidação é **obrigatório, não-discricionário
e calendário-determinístico** — diferente de alpha preditivo que compete com HFT.
Efeito é documentado em múltiplos futuros de FX emergentes (USDMXN, USDZAR têm
literatura). Hipótese NÃO vale em: (a) dias de vol extrema (ATR > P80) onde fluxo
de stress domina unwind; (b) dias sem acumulação direcional clara (|ret_dia| < P60)
onde não há inventário desequilibrado para desfazer; (c) dias pré-feriado ou
pré-vencimento onde o mecanismo se distorce.

---

## 5. Kill criteria ex-ante

| ID | Trigger | Ação | Owner |
|----|---------|------|-------|
| K1 | DSR < 0 na CPCV | descartar (tese é ruído) | Kira |
| K2 | PBO > 0.4 na CPCV | descartar (overfitting severo; threshold rigoroso por sample pequeno) | Mira |
| K3 | IC hold-out (2025-07→2026-04) < 50% do IC in-sample | descartar (efeito arbitrado/regime-dependente) | Kira |
| K4 | Drawdown em paper-mode > 3σ acima do budget Riven | desligar imediato | Riven |

**Hold-out virgem pré-registrado:** 2025-07-01 → 2026-04-21 (10 meses). NÃO tocar
durante desenvolvimento. Split foi decidido antes de qualquer análise de dados
(ver §11 gate signature timestamp).

**N_trials pré-registrado:** 5
- T1: baseline (4 janelas, threshold P60, regime ATR [P20,P80])
- T2: threshold P50 em vez de P60
- T3: threshold P70 em vez de P60
- T4: sem filtro de regime ATR
- T5: só janela 17:25 (em vez de 4 janelas)

Qualquer trial fora desta lista invalida Bonferroni. Fix ex-ante.

---

## 6. Consulta Mira (ML viability) — *feature-eval

**Artefato:** [docs/research/audits/T002-mira-audit.md](../audits/T002-mira-audit.md)

- [ ] Features computáveis com trades-only (verificar agregação de ATR por dia)
- [ ] Risco de leakage controlado (sign do ret_acumulado usa APENAS close[t], label usa close[17:55])
- [ ] Sample efetivo ~1500 obs é tratável com CPCV N=10 k=2 45 paths
- [ ] N_trials=5 pré-registrado → Bonferroni viável
- [ ] Overfitting risk BAIXO: 1 parâmetro direcional + 2 thresholds de regime

**Mira verdict:** FORTE ✅ (ver audit)

---

## 7. Consulta Nova (microestrutura B3) — *audit-feature

**Artefato:** [docs/research/audits/T002-nova-audit.md](../audits/T002-nova-audit.md)

- [ ] Mecanismo de dealer unwind validado microestruturalmente
- [ ] Fases de pregão: só contínuo 09:30-17:55; EXCLUI call fechamento 17:55-18:00 (Nova canônico)
- [ ] Rollover D-3 a D-1 excluído (liquidez migra)
- [ ] Pré-feriado e pré-Copom excluídos como stress regime separado em Fase E
- [ ] Multiplier R$10/ponto referenciado via glossário (não duplicado no spec)

**Nova verdict:** AUDIT-OK com constraints (ver audit)

---

## 8. Consulta Nelo (availability live) — *callback-spec

**Artefato:** [docs/research/audits/T002-nelo-audit.md](../audits/T002-nelo-audit.md)

- [ ] `intraday_flow_direction`: computable — sinal(close_t − open_dia), O(1) do callback
- [ ] `intraday_flow_magnitude`: computable — requer ATR_20d rolling (pré-computado em memória no start do dia)
- [ ] `atr_day_ratio`: computable — idem
- [ ] Janelas determinísticas {16:55, 17:10, 17:25, 17:40}: relógio do servidor basta; zero dependência externa
- [ ] Execução: ordens a mercado em t; saída a mercado em 17:55 OU triple-barrier na variante Fase E
- [ ] Tolerância latência: p99 < 100ms (DMA2) é ordem de magnitude menor que janela de 15 min

**Nelo verdict:** LIVE-READY (ver audit)

---

## 9. Gate de saída Fase A

- [x] 4Q estruturado (template canônico — G001 respeitado)
- [x] Thesis revisada por Kira + Mira + Nova + Nelo
- [x] Todas features com `historical_availability = computable`
- [x] Kill criteria ex-ante escritos (K1-K4)
- [x] Hold-out virgem pré-registrado ANTES de Fase E
- [x] N_trials pré-registrado (5 variantes) → Bonferroni válido
- [x] Spec YAML Mira→Beckett exportada com SHA256 real (§11 hash)

**Verdict:** PASS — liberado para Fase B (Architecture — Aria)

---

## 10. Anexo — Histórico do conselho

Esta tese é output de deliberação estruturada em 13 turnos do Quant Council
2026-04-21. Histórico completo: [docs/councils/QUANT-COUNCIL-2026-04-21.md](../../councils/QUANT-COUNCIL-2026-04-21.md).

Eventos relevantes:
- Turno 2: lista negativa N1-N7 eliminou trend-following, pairs trading, carry, Turtle, OBI, 1-tick prediction, smart-money following
- Turno 3-5: Nova+Nelo+Kira identificaram 5 oportunidades O1-O5 arsenal-compatíveis
- Turno 6: Mira ranqueou top-3 (O1 > O5 > O2)
- Turno 7: O1 foi winner inicial
- Turno 8: red-team WOUND O1 4×
- Turno 9: humano invalidou O1 por **ausência de feed de eventos macro** (constraint de arsenal)
- Turnos 10-12: re-vote arsenal-aware, convergência unânime em O5
- Turno 13: handoff Fase A

---

## 11. Gate Signature — Fase A → Fase B

```yaml
gate_A_signature:
  verdict: pass
  signed_by: Kira (@quant-researcher)
  signed_at_brt: "2026-04-21T17:30:00"
  mira_beckett_spec_ref: "docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml"
  mira_beckett_spec_hash: "sha256:c7c020ef987abe17d1246feab930087742c97d7731fbfd7e5a3711082c50b751"  # computado sobre o arquivo pré-assinatura
  consultations_signed:
    mira: "docs/research/audits/T002-mira-audit.md"
    nova: "docs/research/audits/T002-nova-audit.md"
    nelo: "docs/research/audits/T002-nelo-audit.md"
  hold_out_preregistered_at_brt: "2026-04-21T17:30:00"
  hold_out_window: "2025-07-01 to 2026-04-21"
  n_trials_preregistered: 5
  next_phase: B
  next_owner: Aria (@architect)
```

**Assinatura:** Kira (@quant-researcher) — 2026-04-21 BRT
