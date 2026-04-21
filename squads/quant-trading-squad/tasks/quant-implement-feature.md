# Task: quant-implement-feature

**Fase do workflow:** D (Implementation)
**Owner primary:** `@dev` (Dex)
**Gate owner:** `@qa` (Quinn)
**Consultores (domain):** `@profitdll-specialist` (Nelo), `@market-microstructure` (Nova), `@ml-researcher` (Mira), `@backtester` (Beckett)
**Data owner:** `@data-engineer` (Dara) — se story afeta storage
**Input:** story aprovada por Pax + mira-beckett-spec.yaml + architecture design
**Output:** código commitado (NÃO pushed — Gage faz push depois) + testes + story com File List atualizada
**Duration estimate:** 1-10 dias por story (segue estimativa da story)

---

## Propósito

Implementar a feature conforme story aprovada, respeitando invariantes do squad e consultando domain agents em qualquer ambiguidade quant.

## Pré-condições

- [ ] Task `quant-thesis-to-story` concluída, story tem verdict GO de Pax
- [ ] Story file existe em `docs/stories/`
- [ ] Dex sabe onde estão thesis + mira-beckett-spec + architecture design

## Sequência de execução

### Passo 1 (condicional) — Dara prepara storage

Gatilho: story afeta schema parquet, TimescaleDB, ou feature store.

Owner: `@data-engineer` (Dara)

- [ ] Migration escrita e testada contra dev DB
- [ ] Schema reflete mira-beckett-spec
- [ ] Timezone BRT preservado em colunas de timestamp (R2)
- [ ] Índices adequados para queries esperadas
- [ ] Rollback plan documentado

Se não aplicável, pular este passo.

### Passo 2 — Dex implementa

Owner: `@dev` (Dex)

Command: `*develop-story`

Regras obrigatórias durante implementação:

#### Invariantes técnicos

- [ ] Nenhum `SendOrder`/`ChangeOrder`/`CancelOrder` fora do módulo de execução do Tiago (R3)
- [ ] Nenhuma conversão de BRT → UTC em features/labels/storage (R2)
- [ ] Features book-based marcadas como LIVE-ONLY, não entram no pipeline de backtest (R7)
- [ ] Sem hardcode de margem/emolumentos/IR — sempre via config parametrizado (R1 + Nova owner)
- [ ] `ClOrderID` atribuído client-side em toda ordem; `profit_id` mapeado pós-ack

#### Consultores (quando acionar)

| Situação | Agente consultar | Como |
|----------|------------------|------|
| Dúvida em signature/callback/rejection DLL | `@profitdll-specialist` (Nelo) | Cite manual seção, não adivinhe |
| Dúvida em semântica de feed (trade type, fase, RLP) | `@market-microstructure` (Nova) | `*decode` no campo ambíguo |
| Dúvida em feature/label/CV | `@ml-researcher` (Mira) | consultar spec YAML primeiro |
| Dúvida em fill rule/latency/slippage | `@backtester` (Beckett) | `*slippage-model` |

**Nunca inventar.** Se nenhum agente tem a resposta, rotular `[TO-VERIFY]` e criar TODO na story.

#### Testes

- [ ] Unitários para cada função pública nova
- [ ] Integração: pipeline end-to-end com dados reais (sampled parquet)
- [ ] Edge cases: rollover, leilão, halt, gap de dados, timestamp na fronteira de sessão
- [ ] Fixtures BRT, nunca UTC

#### Atualização da story

- [ ] File List preenchida com cada arquivo novo/modificado
- [ ] Checkboxes de tarefas marcados `[x]` à medida que completa
- [ ] Testing notes com resultados

Output: commits locais (não push), story com estado `InProgress` → `InReview`.

### Passo 3 — Quinn gate de qualidade

Owner: `@qa` (Quinn)

Command: `*qa-gate`

Quinn aplica os 7 checks AIOX no código:

1. Código: convenções, naming, estrutura
2. Testes: coverage (alvo squad: ≥ 80% para código quant crítico), edge cases cobertos
3. Lint: `npm run lint` / `ruff` passa sem erros
4. Type: `mypy` / `npm run typecheck` passa
5. Security: sem credenciais hardcoded, sem SQL injection, sem path traversal
6. Performance: sem loops N² onde N seria grande, sem alocações em hot path do callback DLL
7. Docs: docstrings em APIs públicas, comentários apenas onde WHY é não-óbvio

Quinn também aplica **checks quant-specific** (override do gate AIOX padrão):

- [ ] Busca por `datetime.utcnow()`, `pytz.UTC`, `tz_convert('UTC')` → FAIL imediato (R2)
- [ ] Busca por `SendOrder(` fora de `src/execution/` → FAIL (R3)
- [ ] Busca por números literais que parecem alíquota tributária (`0.20`, `0.15`, `0.225`) sem referência a config → CONCERNS (R1)
- [ ] Verifica que features book-based têm guard `if live_mode:` → FAIL se ausente (R7)

Veredito: **PASS** | **CONCERNS** (prosseguir com nota) | **FAIL** (loop back para Dex, max 5 iterations) | **WAIVED** (exige humano)

### Passo 4 — Story marca como Done (para gate da Fase E)

- [ ] Story status = `Done` em `docs/stories/`
- [ ] File List finalizada
- [ ] Testing notes com resultados
- [ ] Changelog sintético no PR description (para Gage usar)

**Importante:** Done aqui NÃO significa live. Significa "código passou QA gate e pronto para validação quant (Fase E)".

## Gate de saída

- [ ] Quinn PASS (ou CONCERNS documentado e aceito)
- [ ] Todos os testes passam localmente
- [ ] Story Done com File List completa
- [ ] Nenhum `git push` executado (ainda)

## Red flags que ABORTAM a task

- Quinn FAIL 5× em sequência → escalate `@aiox-master` para análise de root cause
- Domain agent divergência crítica (ex.: Mira diz "feature X tem leakage" durante implementação) → loop back para Fase A
- Mudança inesperada em contrato DLL (Nelo descobre quirk novo) → pausa, atualizar docs, consultar impact

## Handoff para próxima task

Próxima task: **quant-cpcv-gate** (Fase E — Quant Validation Gate)
Responsável: `@backtester` (Beckett), `@ml-researcher` (Mira), `@quant-researcher` (Kira)
Input: código commitado local com Quinn PASS
