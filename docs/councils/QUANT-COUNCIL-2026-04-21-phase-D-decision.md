# Squad Deliberation — T002 Fase D Gate Decision

**Data:** 2026-04-21 BRT
**Facilitador:** Orion (@aiox-master)
**Contexto:** T002 passou gate C→D. 4 opções em mesa para decisão do humano. Humano delegou decisão ao squad.
**Formato:** round-table; cada agente dá verdict do ângulo próprio; convergência no final.

---

## Opções em mesa

1. **Full Fase D** — Dex implementa T002.1→T002.5 em sequência, ~10-11 dias, começando já
2. **Ajustar escopo** — mudar ordem/trials/stories antes de começar
3. **Pausar T002** — voltar ao conselho para outra iteração de tese
4. **Dry-run Fase D** — esqueleto + testes sem DLL real, valida arquitetura antes do esforço full

---

## Turno 1 — Round-table (cada agente fala do seu ângulo)

### Morgan (@pm) — delivery/valor

> "Opção 1 é delivery de 10-11 dias comprometidos sem dado novo que autoriza. Opção 3 queima o investimento de Fases A/B/C. Opção 4 é seguro mas não destrava o ativo crítico — **a decisão binária sobre T002 é o resultado da CPCV (Fase E)**. Quanto mais cedo o humano tem um número real de IC/DSR/PBO, mais cedo decide GO/NO-GO para live. Logo: **quero CPCV o mais rápido possível com o mínimo de código**. Isso sugere híbrido, não pura opção 1 nem pura opção 4."

### Pax (@po) — validation/risk-before-commit

> "T002.1 é plumbing reusável (warm-up serve qualquer estratégia futura). T002.2 e T002.3 também são reusáveis — session state + feature computer + signal rule são arquitetura genérica da engine. **T002.4 é onde o investimento se torna T002-específico e difícil de reverter** (live adapter, calendário, gateway Riven, Tiago wiring). Logo: **gate antes de T002.4, não antes de T002.1**."

### Aria (@architect) — design risk

> "O design tem 1 invariante crítico não-testado: *engine pura compartilhada entre backtest e live, adapters pluggáveis*. Se isso quebrar, toda a arquitetura falha. **A única forma de validar isso é escrever as layers 2-3-4 e rodar em backtest real**. Opção 4 (só esqueleto) não prova o invariante porque esqueleto não toca dado real. Opção 1 prova tarde demais. **Quero layers 2-3-4 implementadas sobre histórico real — exatamente o que Beckett precisa para CPCV**."

### Dex (@dev) — implementation dependency

> "T002.1 bloqueia T002.2 bloqueia T002.3. Até aqui é ~7 dias. T002.4 e T002.5 são 4 dias adicionais e MAIS ARRISCADOS (DLL live, gateway, etc.). Se eu parar após T002.3 e Beckett rodar CPCV, eu ganho 4 dias se o resultado é NO-GO. **Dividir em 2 PRs grandes: PR1 = T002.1+T002.2+T002.3 (engine + backtest); PR2 = T002.4+T002.5 (live). Gate entre eles = resultado CPCV**."

### Quinn (@qa) — testability

> "T002.1-T002.3 são puramente testáveis com dados históricos e fixtures — **zero dependência de DLL live**. T002.4 requer DLL real OU stub robusto (caro de manter). Do ponto de vista de QA gate: **quero chegar em CPCV sem tocar DLL**. Se CPCV passa, aí sim vale investir em T002.4 com DLL real e fazer paper-mode sério."

### Beckett (@backtester) — CPCV readiness

> "Para rodar `*run-cpcv --spec T002-v0.1.0.yaml` eu preciso de: (a) signal rule callable sobre histórico, (b) feature computer determinístico, (c) warm-up builders para gerar ATR_20d e percentis 252d sobre o dataset histórico. **Isso é exatamente T002.1+T002.2+T002.3**. Não preciso de T002.4 (live) nem T002.5 (telemetry runtime). Portanto, minha Fase E só bloqueia após merge de T002.3."

### Mira (@ml-researcher) — sample + dataset status

> "Sample efetivo é ~400 obs após filtros. Qualquer atraso em rodar CPCV é desperdício porque não mudamos sample. Sentinel backfill estava ETA 17:00 2026-04-03 (per memory) — em 2026-04-21 deve estar completo; Dara pode confirmar. **Quanto antes eu ver IC e PBO em 45 paths, antes eu recomendo kill ou go**. Voto firme em caminho curto até Fase E."

### Nova (@market-microstructure) — arsenal check

> "Calendário Copom + feriados + vencimentos é pré-requisito para warm-up (exclusão pós-Copom, rollover). Eu posso entregar o YAML 2024-2027 em 1 dia durante T002.1. **Esta é a única entrada de humano para a engine funcionar** (humano confirma datas) — e o custo é baixo se feito agora."

### Nelo (@profitdll-specialist) — DLL availability

> "T002.1 precisa de `GetHistoryTrades` para warm-up sobre dados reais. Em backtest via Beckett, o histórico vem do dataset parquet, NÃO da DLL. Então T002.1/T002.2/T002.3 podem ser testados e backtesteados **sem tocar DLL live**. T002.4 é onde DLL live entra. **DLL live fica reservada para Fase F paper-mode, depois que CPCV autorizar**."

### Riven (@risk-manager) — gateway

> "Gateway Riven ainda não existe como código compartilhado no monorepo — é design. Em T002.3 (backtest adapter) ele não é necessário (Beckett tem modelo próprio de capital). Em T002.4 ele é obrigatório. **Implementar gateway genérico em T002.4 é risco de scope creep** — poderia virar Epic separado. Por enquanto: stub simples em T002.4, gateway real depois."

### Tiago (@execution-trader) — SendOrder

> "Zero impacto em T002.1-T002.3 (não toca execução real). Em T002.4, meu contrato é bem-definido (ver design §5). Não bloqueio nada até T002.4."

### Kira (@quant-researcher) — scientific integrity

> "Minha preocupação é **alinhar spec imutável com implementação**. Enquanto signal rule (T002.3) reflete exatamente o que Mira assinou, estamos OK. Qualquer drift entre spec e código é R11 violation. **Sable audita antes de T002.3 merge**. Fora isso, caminho curto até Fase E é cientificamente correto — dá o falsificador que Popper pede o mais cedo possível."

### Sable (@squad-auditor) — coherence check

> "Observo que Opção 4 como originalmente descrita (esqueleto SEM dado real) não valida nada de Fase A/B. Mas a versão emergente do debate — **T002.1-T002.3 com dado real histórico + gate CPCV antes de T002.4** — resolve os 3 riscos (Aria: invariante; Pax: investimento reversível; Mira: kill rápido). Isso é **híbrido de Opção 1 e Opção 4**, não Opção 4 pura."

---

## Turno 2 — Convergência

Consenso emergente (10 de 11 agentes): **não é nenhuma das 4 opções puras. É um híbrido estruturado.**

### Proposta consolidada: **Opção 5 — Fase D em 2 estágios com gate CPCV**

**Unidade de estimativa:** *sessão de trabalho* (humano↔squad, 1-4h). Estimativas em "dias" na deliberação original foram inflacionadas por assumirem dev humano 8h/dia — squad opera como agente persistente. Corrigido abaixo.

**Estágio D1 — Engine + Backtest (bloqueia Fase E)**

| Story | Escopo | Sessões |
|-------|--------|---------|
| T002.1 | Warm-up (ATR_20d + percentis 252d + gate) | 1 |
| T002.2 | Session state builder + feature computer | 1 |
| T002.3 | Signal rule + backtest adapter | 1 |
| Review | Mira distribuições + Sable coherence + Quinn QA | ~0.5 |

**Sub-total: ~3-4 sessões de trabalho.** Merge como 1 PR único.

**→ Gate de decisão (humano):** Beckett roda CPCV Fase E (minutos-horas de máquina); se K1/K2/K3 ativam, **NO-GO**, T002 morre aqui com ~3-4 sessões investidas (não 5-6). Se passam, autoriza D2.

**Estágio D2 — Live adapter (bloqueia Fase F)**

| Story | Escopo | Sessões |
|-------|--------|---------|
| T002.4 | Live adapter (ProfitDLL + Riven stub + Tiago wiring) | 1-2 |
| T002.5 | Telemetria + EOD reconciliation | 0.5 |

**Sub-total: ~2 sessões.** Merge como PR2.

**→ Fase F paper-mode 5 dias úteis → decisão humano sobre capital real (Fase H).**

---

### Benefícios vs Opção 1

| Critério | Opção 1 (full) | Opção 5 (2-stage) |
|----------|----------------|-------------------|
| Tempo até 1º kill criterion testado | ~5-6 sessões | **~3-4 sessões** ✅ |
| Investimento perdido se CPCV falhar | ~5-6 sessões | **~3-4 sessões** ✅ |
| Risco de drift spec↔código | Alto (scope grande) | Baixo (PR menor, audit mais incisivo) |
| Pressão sobre gateway Riven | Imediata | Adiada para D2 (resolve sozinha) |
| Paralelismo de River/Morgan | Não precisam | River pode draftar T002.2-T002.3 enquanto Dex faz T002.1 |

### Benefícios vs Opção 4 (dry-run puro)

| Critério | Opção 4 (skeleton) | Opção 5 (2-stage) |
|----------|-------------------|-------------------|
| Valida invariante Aria (engine pura) | Não | **Sim** ✅ |
| Valida sample real vs estimado 400 | Não | **Sim** ✅ |
| Produz resultado acionável (IC, DSR) | Não | **Sim** ✅ |
| Reutilizável para próximas estratégias | Parcial | **Total** ✅ |

---

## Turno 3 — Voto final

| Agente | Voto Opção 5 |
|--------|-------------|
| Morgan | ✅ (acelera o gate real) |
| Pax | ✅ (investimento reversível) |
| Aria | ✅ (valida invariante) |
| Dex | ✅ (2 PRs gerenciáveis) |
| Quinn | ✅ (testes sem DLL até D2) |
| Beckett | ✅ (CPCV tem tudo que precisa) |
| Mira | ✅ (caminho mais curto até falsificador) |
| Nova | ✅ (calendário cabe em D1) |
| Nelo | ✅ (DLL live só em D2) |
| Riven | ✅ (gateway pode ser stub em D2) |
| Tiago | ✅ (contrato respeitado em D2) |
| Kira | ✅ (integridade científica preservada) |
| Sable | ✅ (coherence audit cabe em 2 gates) |

**Unânime: Opção 5.**

---

## Ação final (assinatura do squad)

**Veredito:** executar **Opção 5 — Fase D em 2 estágios com gate CPCV intermediário**.

**Ajustes necessários:**
1. Morgan atualiza `EPIC-T002.md` dividindo em D1 (T002.1-T002.3) e D2 (T002.4-T002.5) com gate explícito
2. River draft stories T002.2 e T002.3 agora (paralelo a Dex em T002.1) para não serializar
3. Nova entrega `config/calendar/2024-2027.yaml` durante T002.1
4. Sable acrescenta audit checklist de coerência spec↔código antes de PR1 merge
5. Gate entre D1 e D2 = humano decide após Beckett publicar `docs/research/results/T002-cpcv-report.md`

**Next action:** atualizar `EPIC-T002.md` com estrutura D1/D2; criar tasks para T002.2 e T002.3 drafts; humano autoriza início de T002.1 quando estiver pronto.

---

**Assinaturas do squad:**
- Orion (@aiox-master) — facilitador
- Morgan (@pm), Pax (@po), River (@sm), Aria (@architect), Dex (@dev), Quinn (@qa)
- Kira (@quant-researcher), Mira (@ml-researcher), Nova (@market-microstructure), Nelo (@profitdll-specialist)
- Beckett (@backtester), Riven (@risk-manager), Tiago (@execution-trader)
- Sable (@squad-auditor)

2026-04-21 BRT
