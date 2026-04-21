# EPIC-T002 — End-of-Day Inventory Unwind WDO

**Status:** Draft (Fase C handoff)
**Owner (PM):** Morgan (@pm)
**Origem:** Quant Council 2026-04-21 — voto unânime Turno 12
**Thesis:** docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md (Kira, Fase A PASS)
**Spec:** docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml (`sha256:c7c020ef…0b751`, Mira assinada)
**Design:** docs/architecture/T002-end-of-day-inventory-unwind-design.md (Aria, Fase B PASS)

---

## 1. Epic goal

Implementar e validar em backtest (Fase E — CPCV 45 paths) + paper-mode (Fase F ≥5 dias) a estratégia **T002 End-of-Day Inventory Unwind WDO** até decisão GO/NO-GO para capital real (Fase H).

**Kill gates incorporados:**
- K1: DSR < 0 → descartar
- K2: PBO > 0.4 → descartar (threshold rigoroso por sample ~400 obs)
- K3: IC hold-out (2025-07→2026-04) < 50% IC in-sample → descartar
- K4: DD paper > 3σ budget Riven → kill imediato

---

## 2. Business value

- **Alpha:** edge estimado positivo em janela determinística 16:55-17:55 BRT, condicional a magnitude > P60
- **Risco controlado:** janelas determinísticas evitam hold overnight; exit hard 17:55
- **Capital eficiente:** 4 entradas/dia × contratos sizing via Riven; ADV WDO absorve > 100× o tamanho previsto
- **Baixa complexidade operacional:** zero dependência de feed externo (só relógio + histórico DLL)

---

## 3. Stories plan — 2-stage Fase D (decisão squad 2026-04-21)

**Gate intermediário:** após D1 (engine + backtest) merged, Beckett roda CPCV (Fase E). Resultado decide se D2 (live adapter) é autorizado. Se K1/K2/K3 ativam em CPCV, T002 morre com 7 dias investidos (não 11).

### Estágio D1 — Engine + Backtest (bloqueia Fase E)

**Unidade de estimativa:** *sessão de trabalho* (conversa humano↔squad de 1-4h cada). NÃO usar calendar-days de dev humano — o squad opera como agente persistente, não como dev presencial 8h/dia. Estimativas abaixo refletem custo real.

| Story | Escopo | Estimate | Bloqueia |
|-------|--------|----------|----------|
| **T002.1** | Warm-up (ATR_20d + Percentis 252d + gate) | 1 sessão | T002.2+ |
| **T002.2** | Session state builder + feature computer (layer 2+3) | 1 sessão | T002.3+ |
| **T002.3** | Signal rule (layer 4) + backtest adapter (layer 5 Fase E) | 1 sessão | Beckett CPCV + T002.4 |
| + | Mira review distribuições + Sable coherence audit + Quinn QA gate | ~0.5 sessão (overhead de revisão) | merge PR1 |

**Sub-total D1:** **~3-4 sessões de trabalho** (≈ 1-2 dias de calendar real, dependendo da cadência humano). Merge como **PR1 único**.

### → Gate CPCV (Fase E) — decisão humana

Beckett roda `*run-cpcv`; custo ~minutos-horas de máquina; humano lê relatório:
- Se K1 (DSR<0) OR K2 (PBO>0.4) OR K3 (IC_holdout < 0.5 × IC_insample) → **NO-GO**, T002 descartada
- Se métricas passam → **GO D2**

### Estágio D2 — Live adapter (bloqueia Fase F)

| Story | Escopo | Estimate | Bloqueia |
|-------|--------|----------|----------|
| **T002.4** | Live adapter (ProfitDLL + RivenGate stub + TiagoExecutor) | 1-2 sessões | Fase F paper-mode |
| **T002.5** | Telemetria + EOD reconciliation | 0.5 sessão | Fase F paper-mode |

**Sub-total D2:** **~2 sessões**. Merge como **PR2**.

**Total D1+D2 (sucesso):** ~5-6 sessões de trabalho. **Se CPCV falhar:** ~3-4 sessões (kill antecipado).

**Status atual:**
- T002.1 em Pax GO (10/10) — pronto para Dex
- T002.2-T002.3 drafts pendentes (a criar em paralelo por River)
- T002.4-T002.5 drafts pendentes até gate CPCV

**Deliberação completa:** [docs/councils/QUANT-COUNCIL-2026-04-21-phase-D-decision.md](../councils/QUANT-COUNCIL-2026-04-21-phase-D-decision.md) — voto unânime 13 agentes

---

## 4. Squad responsibility matrix

| Story | Dev | Consultores | QA | Auditor |
|-------|-----|-------------|-----|---------|
| T002.1 | Dex | Nelo (DLL quirks), Dara (schema state), Mira (stats percentis), Nova (calendar) | Quinn (code) | Sable (coherence) |
| T002.2 | Dex | Nova (session filters), Mira (feature purity) | Quinn | Sable |
| T002.3 | Dex | Mira (signal rule parity), Beckett (CPCV wiring) | Quinn | Sable |
| T002.4 | Dex | Nelo (ProfitDLL live), Riven (budget gate), Tiago (SendOrder) | Quinn | Sable |
| T002.5 | Dex | Quinn (test schema), Gage (log pipeline) | Quinn | Sable |

**Gage** é monopolista de `git push` / `gh pr create` para TODAS as stories (R12).

---

## 5. Fase E (CPCV) — após T002.3 merged

**Owner:** Beckett
**Input:** `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml`
**Execução:** `*run-cpcv --spec docs/ml/specs/T002-...-v0.1.0.yaml`
**Output:** `docs/research/results/T002-cpcv-report.md` com:
- IC_spearman por path (distribuição 45 paths)
- DSR
- PBO
- Bootstrap 10k CI
- Breakdown por stress regime (6 regimes do spec)
- Comparação in-sample vs hold-out

**Decisão pós Fase E:**
- Se K1 ou K2 ou K3 ativa → descartar; retornar ao conselho para próxima tese
- Se métricas passam → Fase F (paper-mode) autorizada

---

## 6. Fase F (paper-mode) — após Fase E pass

**Owner:** Riven + Tiago (operação) + Quinn (monitoring)
**Duração mínima:** 5 dias úteis (MANIFEST R8)
**Regra:** nenhum capital real; Tiago roteia ordens para ambiente de paper da B3 ou simulador local

**Métricas monitoradas:**
- IC rolling 5 dias vs CI in-sample
- Hit rate
- DD paper vs budget
- EOD reconciliation (R9): posição paper zerada a cada 17:55

**Decisão pós Fase F:**
- Se K4 ativa OU IC out-of-CI → kill
- Se passa 5 dias sem kill → handoff Fase H (Morgan + humano decidem capital)

---

## 7. Dependências / risk register

| Dependência | Risco | Mitigação |
|-------------|-------|-----------|
| Dataset trades-only WDO (~27 meses) | Backfill Sentinel ainda em progresso (per memory: ETA ~17:00 BRT 2026-04-03) | Usar subset disponível para dev; re-rodar Fase E quando backfill completar |
| ProfitDLL estabilidade | Quirks já mapeados; Whale Detector v2 LIVE validado | Nelo garante; teste Fase F detecta regressões |
| Calendário Copom/feriados correto | Humano mantém anual | Sable audita coerência anualmente |
| Riven gateway implementado | Compartilhado entre estratégias | Dev de gateway é escopo separado; pode ser stubbed em T002.4 até gateway real |

---

## 8. Gate Signature — Fase C → Fase D (2-stage)

```yaml
gate_C_signature:
  verdict: pass
  signed_by: Morgan (@pm) + Pax (@po) + squad (13 agentes)
  signed_at_brt: "2026-04-21T19:00:00"
  thesis_ref: "docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md"
  design_ref: "docs/architecture/T002-end-of-day-inventory-unwind-design.md"
  stage_D1:
    stories_drafted: ["T002.1"]
    stories_planned: ["T002.2", "T002.3"]
    pax_validation_T002_1: "GO 10/10"
    estimate_days: 7
    exit_criterion: "PR1 merged + Quinn PASS + Sable coherence audit"
    triggers_phase: "E (Beckett CPCV)"
  gate_CPCV:
    owner: Beckett + humano
    decision_input: "docs/research/results/T002-cpcv-report.md"
    NO_GO_if: "K1 OR K2 OR K3 ativos"
    GO_authorizes: "Stage D2"
  stage_D2:
    stories_planned: ["T002.4", "T002.5"]
    estimate_days: 4
    exit_criterion: "PR2 merged + Quinn PASS + Sable coherence audit"
    triggers_phase: "F (paper-mode ≥5 dias)"
  deliberation_ref: "docs/councils/QUANT-COUNCIL-2026-04-21-phase-D-decision.md"
  prerequisite_for_next: "humano autoriza início de D1 (T002.1)"
```

---

**Assinatura:** Morgan (@pm) + Pax (@po) — 2026-04-21 BRT

## Dry-run note

T002 é **tese real** (não é smoke-test como T001). Fase D (Dex implementa) requer autorização humana explícita porque consome budget de desenvolvimento de vários dias. Próximo gate de decisão é humano.
