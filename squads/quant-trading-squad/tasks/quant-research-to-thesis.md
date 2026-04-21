# Task: quant-research-to-thesis

**Fase do workflow:** A (Research)
**Owner primary:** `@quant-researcher` (Kira)
**Consultores:** `@ml-researcher` (Mira), `@market-microstructure` (Nova), `@profitdll-specialist` (Nelo)
**Output:** `docs/research/thesis/{id}-{slug}.md` + `docs/ml/specs/{feature-set-id}-v{version}.yaml`
**Duration estimate:** 2-5 dias (depende de complexidade da tese e se requer websearch)

---

## Propósito

Transformar uma ideia informal em uma **tese quantitativa falsificável** que sobreviva ao crivo científico do squad antes de gastar ciclos de engenharia. É o primeiro gate do Quant Story Development Cycle.

## Pré-condições

- [ ] Ideia inicial expressa em 1-3 frases (sem compromisso formal ainda)
- [ ] `@quant-researcher` sabe se é bull/bear thesis sobre microestrutura, ML, price-action, etc
- [ ] Dataset trades-only disponível em `D:\sentinel_data\historical\` (ou decisão de que tese é LIVE-ONLY)

## Sequência de execução (elicit=true)

### Passo 1 — Kira aplica Decision Framework 4Q

Quatro perguntas antes de qualquer trabalho:

```
Q1 — EXISTE ECONOMIC RATIONALE?
     Quem perde dinheiro do outro lado? Que ineficiência estamos capturando?
Q2 — É FALSIFICÁVEL?
     Consigo escrever H1 com métrica mensurável e p-value target?
Q3 — DATASET SUPORTA?
     Trades-only é suficiente? OU exige book (→ tese LIVE-ONLY)?
Q4 — KILL CRITERIA SÃO DEFINÍVEIS EX-ANTE?
     Consigo escrever "se X acontecer, paramos"?
```

Se qualquer Q for NO → **pedir reformulação** (não prosseguir).

### Passo 2 — Kira cria thesis doc

Command: `*hypothesize {topic}`

Template mínimo (thesis-tmpl.yaml):
- H0 / H1 (nula e alternativa exatas)
- Métrica primária (IC, hit rate, Sharpe, profit factor)
- Horizonte (segundos, minutos, holding period)
- Economic rationale (1 parágrafo)
- Kill criteria ex-ante
- p-value target pós-correção Bonferroni/FDR

Saída: `docs/research/thesis/{id}-{slug}.md`

### Passo 3 — Mira avalia viabilidade ML

Command: `*feature-eval + *leakage-audit`

Mira verifica:
- [ ] Features propostas são computáveis com dataset atual (trades-only)?
- [ ] Risco de leakage (target usa info futura)?
- [ ] Sample size estimado ≥ 100 trades no backtest?
- [ ] CV scheme aplicável (CPCV N=10-12, k=2, 45 paths)?

Output: preliminary eval + feature spec draft no thesis doc.

### Passo 4 — Nova audita microestrutura

Command: `*audit-feature`

Nova verifica:
- [ ] Features fazem sentido microestrutural B3?
- [ ] Fases de pregão corretamente tratadas?
- [ ] Leilão vs contínuo separados?
- [ ] RLP/cross/odd-lot handling correto?
- [ ] Rollover respeitado?

Output: audit-feature annex no thesis doc.

### Passo 5 — Nelo valida availability em live

Command: `*callback-spec`

Nelo verifica:
- [ ] Features são computáveis dentro do orçamento de latência do callback?
- [ ] Dados exigidos estão na DLL em real-time?
- [ ] Nenhuma feature depende de `GetHistoryTrades` no callback (quirk empírico)?

Output: availability tag em cada feature (`computable | live_only | partial`).

### Passo 6 — Mira formaliza spec final

Command: `*export-spec {feature-set-id} --version {semver}`

Output: `docs/ml/specs/{feature-set-id}-v{version}.yaml` — spec imutável consumível por Beckett em fase E do workflow.

## Gate de saída

Para avançar para Fase B (Architecture), TODOS devem estar marcados:

- [ ] Q1-Q4 do Decision Framework 4Q: todos SIM
- [ ] thesis.md existe e revisado pelos 4 agentes
- [ ] Cada feature tem `historical_availability` definido
- [ ] Kill criteria ex-ante escritos
- [ ] mira-beckett-spec YAML exportado com hash de assinatura Mira

## Red flags que ABORTAM a task

- Kira não consegue formular H1 falsificável → ideia é slogan, não tese
- Tese depende exclusivamente de book histórico e não aceita ser LIVE-ONLY → descartar
- Nelo não garante availability live de features críticas → reformular
- Leakage descoberto por Mira em feature core → reformular

## Handoff para próxima task

Próxima task: **quant-thesis-to-spec** (Fase B — Architecture & Epic)
Responsável: `@architect` (Aria) + `@pm` (Morgan)
Input artefatos: thesis doc + mira-beckett-spec.yaml
