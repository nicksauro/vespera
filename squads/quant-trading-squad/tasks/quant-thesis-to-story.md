# Task: quant-thesis-to-story

**Fase do workflow:** B + C (Architecture & Epic → Story)
**Owner primary:** `@architect` (Aria), então `@pm` (Morgan), então `@sm` (River), então `@po` (Pax)
**Consultores:** `@data-engineer` (Dara), `@profitdll-specialist` (Nelo)
**Input:** thesis doc + mira-beckett-spec.yaml
**Output:** `docs/prd/EPIC-{ID}.md` + `docs/stories/{epicNum}.{storyNum}.story.md` (validated)
**Duration estimate:** 1-3 dias

---

## Propósito

Transformar uma thesis aprovada cientificamente em **arquitetura executável + stories prontas para implementação**. Esta task é a ponte domain → framework do squad.

## Pré-condições

- [ ] Task `quant-research-to-thesis` concluída com todas checkboxes verdes
- [ ] thesis doc versionado em `docs/research/thesis/`
- [ ] mira-beckett-spec.yaml assinado por Mira

## Sequência de execução

### Passo 1 — Aria desenha arquitetura

Owner: `@architect` (Aria)

Aria consulta:
- `@data-engineer` (Dara) — se a feature afeta schema do parquet, feature store, TimescaleDB
- `@profitdll-specialist` (Nelo) — se afeta integração com callback DLL ou envio de ordem
- `@backtester` (Beckett) — se altera contract do simulador

Saídas:
- [ ] Módulos/pacotes afetados identificados
- [ ] Interfaces públicas definidas (tipo de input/output)
- [ ] Dependências entre módulos mapeadas
- [ ] Decisão tech stack (libs, frameworks) — se divergente do atual
- [ ] Data contract (input → pipeline → output) documentado

Output: `docs/architecture/{feature}-design.md`

### Passo 2 — Morgan cria Epic

Owner: `@pm` (Morgan)

Command: `*create-epic`

Morgan consolida:
- Business goal (extraído do thesis economic rationale)
- User stories candidatas (quebradas por limite de PR razoável)
- Acceptance criteria por story
- Dependencies com outros epics
- Risk assessment (citar fase do workflow onde risco aparece)

Output: `docs/prd/EPIC-{ID}.md`

### Passo 3 — River drafta primeira story

Owner: `@sm` (River)

Command: `*draft {epicId}`

River usa story template AIOX + adiciona campos quant-specific:
- Feature availability tag (computable | live_only | partial)
- Impact em regras invariáveis (R1-R14) — se aplicável
- Agentes consultores por passo de implementação

Output: `docs/stories/{epicNum}.{storyNum}.story.md`

### Passo 4 — Pax valida story

Owner: `@po` (Pax)

Command: `*validate-story-draft`

Pax aplica 10-point checklist + quant-specific additions:
- [ ] Acceptance criteria 100% rastreáveis ao thesis ou PRD
- [ ] Testing strategy respeita R7 (trades-only) quando aplicável
- [ ] Timestamps BRT (R2) preservados em todas APIs tocadas
- [ ] Se afeta execução: explicitar handoff com Tiago/Riven
- [ ] Se afeta custo: explicitar consulta a Nova (owner emolumentos B3)
- [ ] File List estimada é realística

Decisão: **GO (score ≥ 7)** | **NO-GO (fixes listed)**

## Gate de saída

Para avançar para Fase D (Implementation):

- [ ] EPIC-{ID}.md existe e inclui todas stories planejadas
- [ ] Story {epicNum}.{storyNum} tem Pax GO verdict
- [ ] Architecture design concordante com mira-beckett-spec
- [ ] Handoffs com Dara/Nelo/Beckett documentados quando aplicáveis

## Red flags que ABORTAM a task

- Aria detecta conflito entre thesis e arquitetura atual que exige refactor grande → split em duas epics (refactor primeiro, depois feature)
- Pax detecta que story precisa split em 2+ stories (muito grande) → retornar a River
- Data contract inviável com dataset atual → voltar para task `quant-research-to-thesis` com constraint adicional

## Handoff para próxima task

Próxima task: **quant-implement-feature** (Fase D — Implementation)
Responsável: `@dev` (Dex) com consultas a domain agents
Input: story aprovada por Pax
