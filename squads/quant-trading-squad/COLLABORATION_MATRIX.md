# Quant Trading Squad — COLLABORATION MATRIX

> Criado em 2026-04-21. Escopo: quem fala com quem, em que direção, sobre quê. Define autoridade (quem decide), handoffs (quem pergunta) e anti-padrões (quem NÃO deve se comunicar diretamente).

## Princípio

Cada agente tem **domínio exclusivo** (onde é autoridade absoluta) e **consultas saída/entrada** (onde pergunta ou responde). Nenhuma decisão cruza domínio sem handoff explícito. Violação = bug de protocolo, não liberdade individual.

---

## Matriz de Autoridade

Cada agente é **fonte única** sobre seu domínio. Questões sobre esse domínio devem ser roteadas para ele.

| Agente | Domínio Exclusivo (é fonte única) | Não é fonte sobre |
|--------|-----------------------------------|--------------------|
| **Nelo** (@profitdll-specialist) | ProfitDLL: funções, callbacks, structs, rejection codes NL_*, sequência de init/login | Margens B3, limites corretora, microestrutura, regime de mercado |
| **Nova** (@market-microstructure) | Fases de pregão B3, trade types (13-type enum), RLP, rollover, margens B3, ticks/multiplicadores, horário | Funções DLL, sizing, features ML, fills do simulador |
| **Mira** (@ml-researcher) | Features, labels, CV (CPCV), PBO, DSR, overfitting, feature registry, importance | Microestrutura B3 (consulta Nova), APIs DLL (Nelo), fills (Beckett) |
| **Beckett** (@backtester) | Simulação DLL-fiel, fill rules, latency profile, slippage model, CPCV executor, métricas robustas | Ideação de alpha (Kira/Mira), decisão de kill (Riven), envio real de ordem (Tiago) |
| **Riven** (@risk-manager) | Sizing, stops, drawdown budget, kill-switch, regime filter, Kelly, quarter-Kelly, limits aggregation | Fatos de DLL (Nelo), microestrutura (Nova), features (Mira), fill model (Beckett) |
| **Tiago** (@execution-trader) | SendOrder/ChangeOrder/CancelOrder, lifecycle de ordem, telemetria real, reconciliação EOD, paper-mode | Decisão de sizing (Riven), seleção de trade (Mira), model de fill (Beckett) |
| **Kira** (@quant-researcher) | Ideação de alpha, EDA exploratória, hipótese primária, revisão literária | Validação estatística rigorosa (Mira), viabilidade live (Nelo), sizing (Riven) |
| **Sable** (@squad-auditor) | Auditoria de coerência squad (MANIFEST/MATRIX/GLOSSARY), findings estruturados, red-team de fluxos | Alpha, sizing, execução, features, backtest — NÃO é owner de nada operacional |
| **Aria** (@architect) | Arquitetura de sistema, seleção de tech stack, integração patterns, complexity assessment | Semântica quant (domain agents), envio de ordem (Tiago), sizing (Riven) |
| **Morgan** (@pm) | PRDs, epic orchestration, requirements gathering, spec pipeline | Alpha thesis (Kira), validação estatística (Mira), decisão DLL (Nelo) |
| **Pax** (@po) | Validação de story draft (10-point checklist + quant adds), backlog priorization | Conteúdo técnico de story (domain + Dex), implementação |
| **River** (@sm) | Criação de story a partir de epic/PRD, story template + quant adds | Validação de story (Pax), conteúdo de alpha (Kira) |
| **Dex** (@dev) | Implementação de código, File List, progresso de checkboxes da story, commits locais | Alpha thesis, sizing, validação estatística — consulta domain agents em dúvida |
| **Quinn** (@qa) | Code gate AIOX (7 checks) + quant-specific checks (BRT, SendOrder monopoly, trades-only guards, alíquota hardcode) | Coerência de squad (Sable), alpha, sizing |
| **Dara** (@data-engineer) | Schema TimescaleDB, parquet schema, feature store, migrations, índices, query optimization | Decisão de feature quant (Mira), microestrutura (Nova) |
| **Gage** (@devops) | git push, gh pr create/merge, CI/CD, MCP configuration, release management | Qualquer decisão técnica/quant — opera APÓS gates passarem |

---

### Sable (Auditor) — posição especial

Sable NÃO aparece na matriz de handoffs operacionais — ele não participa de pesquisa/execução/risco. Relação dele com o squad:

| De → Para | Tópico |
|-----------|--------|
| Sable → qualquer agente | Finding aberto contra o agente + ação sugerida |
| Sable → humano | Relatório `*full-audit`, waiver crítico, alteração estrutural do MANIFEST |
| Qualquer agente → Sable | Notificação de correção (owner diz "ok, ajustei") — Sable re-audita |
| Humano → Sable | Trigger (`*preblock-review`, `*post-incident`, `*full-audit` trimestral) |

**Regra:** Sable lê tudo, não é consultado por ninguém sobre decisão operacional, não toma decisão executiva.

---

## Matriz de Handoffs (Consulta → Resposta)

Linha = quem pergunta, coluna = quem responde. Célula = tópico do handoff. "—" = sem handoff direto esperado.

| ↓ pergunta \ → responde | Nelo | Nova | Mira | Beckett | Riven | Tiago | Kira |
|--------|------|------|------|---------|-------|-------|------|
| **Nelo** | — | callback availability ao vivo | — | — | — | telemetria real de callbacks | — |
| **Nova** | DLL param para captura book | — | quais features microestrutura entregar | — | — | observações de rejection/latency live | — |
| **Mira** | feature `X` disponível no feed live? | feature faz sentido microestrutural? | — | custo CPCV; fill plausível? | Kelly/constraint para sizing dinâmico | — | ideação/hipótese raiz |
| **Beckett** | param DLL p/ fill model | latência típica por fase; behavior RLP | spec de feature+label+CV | — | drawdown budget para stress | telemetria real p/ calibração | — |
| **Riven** | rejection codes p/ halt map | fase de pregão + margens B3 | distribuição de PnL por trade | loss/DD simulado CPCV | — | posição/PnL real em tempo real | — |
| **Tiago** | spec de SendOrder; rejection parsing | horário B3 + behavior rollover | — | fill esperado (pré-envio) | gateway approve/reject | — | — |
| **Kira** | — | fase, rollover, regime B3 | é exploráble? overfits? | simulação rápida de ideia | — | — | — |

**Legenda de setas:**
- Linha responde → coluna é quem deveria perguntar. Ex.: Mira consulta Nelo sobre availability live.
- Diagonal (Agente-X ↔ Agente-X) é "—" por definição (auto-consulta não existe).

---

### Matriz de Handoffs Domain ↔ Framework (AIOX)

Linha = agente framework perguntando, coluna = agente domain respondendo (ou vice-versa). Célula = tópico.

| ↓ pergunta \ → responde | Kira | Mira | Nova | Nelo | Beckett | Riven | Tiago |
|--------|------|------|------|------|---------|-------|-------|
| **Aria** (@architect) | alpha thesis impacta arch? | feature pipeline shape | — | callback contract | simulador contract | risk boundaries | execution boundary |
| **Morgan** (@pm) | business goal do thesis | métricas primárias | fases B3 afetadas | availability live | capacity estimate | budget DD aceitável | paper-mode exigido? |
| **River** (@sm) | hipótese resumida | spec YAML para referenciar | — | — | — | — | — |
| **Pax** (@po) | thesis suporta ACs? | feature computable? | microestrutura respeitada? | availability live confirmada? | fill rule testável? | sizing testável? | handoff execução claro? |
| **Dex** (@dev) | — | spec YAML + dúvidas de feature/label/CV | semântica de campo ambíguo | signature/callback/rejection DLL | fill rule / latency / slippage | sizing interface | execução interface |
| **Quinn** (@qa) | — | spec YAML bate com código? | invariantes B3 respeitadas? | SendOrder monopoly respeitado? | fill rules implementadas corretamente? | kill-switch implementado? | R3 violado? |
| **Dara** (@data-engineer) | — | schema parquet/feature store | timezone BRT, fase B3 persistida | — | schema de trades históricos | — | — |
| **Gage** (@devops) | — | — | — | — | — | live approval | paper-mode completo? |

**Ordem temporal típica:** Morgan/Aria/River/Pax consultam domain em Fases A-C (design). Dex consulta em Fase D (implementação). Quinn consulta em Fase D-gate. Dara consulta em Fase D se schema muda. Gage consulta em Fase H (push).

---

## Fluxos Canônicos

**Nota hierárquica (2026-04-21):** O **Fluxo 6 — Q-SDC end-to-end** é o fluxo canônico de desenvolvimento de nova feature do squad. Os Fluxos 1-5 são fluxos táticos consumidos **dentro** de etapas específicas do Q-SDC:

| Fluxo tático | Consumido em Q-SDC |
|--------------|-------------------|
| Fluxo 1 — Pesquisa (ideação) | Fase A (Research) — Kira/Mira/Nova/Nelo |
| Fluxo 2 — Ordem live | Fase F (Risk & Paper) / pós-H (produção) |
| Fluxo 3 — Backtest / validation | Fase E (Quant Validation Gate) |
| Fluxo 4 — Incidente live | Fase F + gatilho Sable (coherence re-audit) |
| Fluxo 5 — Rollout novo agente | Meta-fluxo (fora do Q-SDC; envolve aiox-master) |

Em caso de conflito entre Fluxo 1-5 e Fluxo 6, Fluxo 6 prevalece — os táticos foram pensados pré-expansão e o Q-SDC é o superset atual.

### Fluxo 1 — Pesquisa (greenfield, ideia nova)

```
Kira (ideia) 
  → Mira (validação preliminar estatística)
    → Nova (audit microestrutural)
      → Nelo (availability live + spec DLL para captura)
        → Mira (spec final: feature + label + CV)
          → Beckett (CPCV completo + PBO + DSR)
            → Riven (sizing + regime filter + kill config)
              → Tiago (paper-mode ≥ 5 sessões)
                → Riven + humano (approve live)
```

**Gates:**
- Mira → Nova: rejeita se não tiver intuição microestrutural
- Nelo: rejeita se feature não tem fonte no feed
- Beckett: rejeita se CPCV DSR_critical < limiar
- Riven: rejeita se sizing implicar DD > budget
- Tiago → humano: rejeita se paper mode tem falha lógica

### Fluxo 2 — Ordem em produção live

```
Sinal (Mira pipeline, runtime)
  → Tiago monta ordem (com size sugerido e contexto)
    → Riven *tiago-gateway (valida size, budget, regime, margin, kill)
      ├─ APPROVE → Tiago SendOrder via Nelo spec
      │    → callbacks TOrderChangeCallback
      │       → telemetria + posição atualizada
      │          → Beckett (*tiago-calibrate semanal)
      │             → Riven (attribution diária)
      │                → Riven (rebalance se drift vs backtest)
      └─ REJECT → ordem morre; Riven loga razão; Tiago não tenta novamente sem gateway
```

### Fluxo 3 — Feature nova (proposta por Mira)

```
Mira propõe feature
  → Nova *audit-feature (reality-check microestrutural)
    → Nelo *callback-spec (availability live + DLL path)
      → Mira registra em feature_registry (com historical_availability)
        → Beckett testa em CPCV (se computable trades-only ou se book disponível)
          → Mira registra importance + OOS
```

**Gate especial:** feature book-based + dataset trades-only → feature fica `live_only`, não entra em backtest histórico.

### Fluxo 4 — Evento DLL inesperado (rejection, disconnect, timeout)

```
Tiago observa evento anômalo (rejection_code desconhecido, timeout, disconnect)
  → Nelo *rejection-explain (mapeia código para causa)
    → Nelo *disconnect-protocol (se for conexão)
      → Tiago classifica (RECOVERABLE / BUSINESS / CATASTROPHIC)
        → Riven *kill-check (avalia se eleva nível)
          ├─ throttle/halt → Riven notifica squad + humano
          └─ kill → Riven *kill-arm + post-mortem obrigatório
```

### Fluxo 5 — Reconciliação EOD

```
Tiago *reconcile (EOD)
  → compara posição interna vs posição corretora via DLL (Nelo spec)
    ├─ match → Tiago *telemetria publica report
    │    → Riven *attribution diária (PnL realizado + unrealized + costs)
    │       → Mira (se discrepância de slippage vs backtest)
    │          → Beckett *tiago-calibrate (recalibra latency/fill)
    └─ mismatch → HALT automático
         → Tiago escala a humano
            → Nelo verifica callbacks perdidos
               → Riven decide resumir ou kill
```

### Fluxo 6 — Q-SDC (Quant Story Development Cycle) end-to-end

**Domain decide O QUÊ. Framework decide COMO. Gage publica.** Este é o fluxo mestre do squad.

```
Fase A — Research                   [quant-research-to-thesis.md]
  Kira *hypothesize
    → Mira *feature-eval + *leakage-audit
      → Nova *audit-feature
        → Nelo *callback-spec (availability)
          → Mira *export-spec → mira-beckett-spec.yaml (imutável)

Fase B+C — Architecture & Story     [quant-thesis-to-story.md]
  Aria architecture-design
    → Morgan *create-epic
      → River *draft {epicId}
        → Pax *validate-story-draft  (GO score ≥ 7)

Fase D — Implementation             [quant-implement-feature.md]
  Dara (se schema muda) *migrate
    → Dex *develop-story
        ↖ consulta Nelo (DLL) / Nova (feed) / Mira (feature) / Beckett (fill)
      → Quinn *qa-gate (7 checks + quant-specific)
        ├─ PASS → Fase E
        └─ FAIL → loop Dex (max 5)

Fase E — Quant Validation Gate      [quant-cpcv-gate.md]
  Beckett *run-cpcv --spec mira-beckett-spec.yaml --n 10 --k 2 --embargo 1
    → Mira *deflate-sharpe + *overfit-diagnose (DSR, PBO)
      → Kira *review (peer review final)
        ├─ APPROVED → Fase F
        ├─ APPROVED_WITH_CHANGES → Fase F com concerns
        └─ REJECTED → volta Fase A (tese reformulada)

Fase F — Risk & Paper-Mode
  Riven *sizing + kill config
    → Tiago *paper-mode ≥ 5 sessões
      → Tiago *reconcile EOD

Fase G — Coherence Audit & Live Gate
  Sable *preblock-review ou *full-audit
    → humano assina go-live

Fase H — Push & Release
  Gage git push + gh pr create/merge
    → CI/CD + release notes
```

**Gate crítico:** Fase E (CPCV gate) é **mandatório mesmo com Quinn PASS**. Código correto pode implementar alpha inexistente. Kira veta em nome do squad.

**Loop-back:** qualquer REJECT em E ou F volta para A (tese) — não para D (código). Rebuilding code sem rebuilding thesis é sintoma de sunk-cost.

---

## Regras de Autoridade

Decisões onde a palavra de um agente encerra o debate.

### Exclusividades

| Decisão | Agente Final | Ninguém Mais Pode Decidir |
|---------|--------------|---------------------------|
| Armar / desarmar kill-switch | **Riven** | Tiago obedece; humano aprova desarmar |
| Enviar ordem real (SendOrder) | **Tiago** | Mira gera sinal; Riven autoriza; só Tiago envia |
| Rotular fato de DLL como confirmado | **Nelo** | Nova/Mira/Beckett consultam, não afirmam |
| Decidir fase de pregão em curso | **Nova** | Fonte única B3; Tiago/Beckett seguem |
| Aceitar backtest como válido | **Beckett** (métrica) + **Mira** (estat.) | Veto mútuo; ambos precisam aprovar |
| Publicar feature no feature_registry | **Mira** | Nova audita, Nelo valida availability, Mira registra |
| Declarar ideia "pesquisável" | **Kira** (exploratório) → **Mira** (rigoroso) | Duas camadas obrigatórias |

### Gateway Obrigatório

**Toda ordem real passa pelo Riven antes do Tiago.** Sem exceção. Inclusive ordens de unwind, stop manual, trades de teste, qualquer coisa. `*tiago-gateway` é síncrono (Tiago espera resposta).

### Consulta Obrigatória

**Antes de adicionar feature ao backtest:** Mira consulta Nova (microestrutura) E Nelo (availability) E registra historical_availability. Pular = feature fantasma.

**Antes de aprovar estratégia para live:** Riven consulta Beckett (CPCV stats) E Mira (distribuição) E Tiago (paper-mode log) E humano. Pular = operar cego.

---

## Anti-Padrões (Quem NÃO Deve Falar Com Quem Diretamente)

Caminhos proibidos — indicam bug de protocolo se acontecerem.

### Mira → Tiago (direto)
**Errado.** Mira não manda ordem; Mira gera sinal. Ordem vai por pipeline Mira → Tiago monta → Riven approve → Tiago envia. Se Mira "fala direto" com Tiago, gateway Riven é pulado.

### Kira → Tiago (direto)
**Errado.** Kira é pesquisa exploratória; não entra em produção sem Mira (rigor) + Beckett (backtest) + Riven (sizing).

### Nelo → Riven (sobre margem)
**Errado.** Nelo não sabe margem. Riven consulta Nova (B3 oficial) e corretora (externa), não Nelo. Nelo só fornece rejection codes *após* corretora rejeitar.

### Beckett → Tiago (sobre fill real)
**Errado.** Beckett simula; Tiago observa realidade. Handoff é reverso: Tiago alimenta Beckett com telemetria real para calibração. Nunca Beckett "ensina" Tiago como a ordem será preenchida.

### Nova → Nelo (sobre DLL) ou Nelo → Nova (sobre microestrutura)
**Pode acontecer (cordialmente), mas sem autoridade cruzada.** Nelo não é fonte sobre fases B3 mesmo que callback contenha timestamp; Nova não é fonte sobre quais callbacks existem mesmo que use dados via callback.

### Qualquer agente → SendOrder/ChangeOrder/CancelOrder
**Errado. Somente Tiago.** Mira, Beckett, Riven, Kira, Nova, Nelo não chamam essas funções. Monopólio é explícito.

### Mira ou Beckett → ajustar size em tempo real
**Errado.** Sizing é Riven. Mira entrega probabilidade; Beckett entrega distribuição esperada; Riven traduz em size final.

### Dex → SendOrder / ChangeOrder / CancelOrder
**Errado (R3 + R11).** Dex implementa código, mas execução de ordem é monopólio Tiago. Dex implementa *interface* que Tiago chamará; nunca coloca a chamada DLL em código de feature/label/pipeline.

### Dex → decidir semântica de feature sem Mira
**Errado (R11).** Framework não inventa. Dúvida em feature/label/CV → consulta Mira spec YAML. Ambiguidade persistente → rotular `[TO-VERIFY]` e criar TODO na story. Nunca "chutar".

### Quinn → aprovar alpha (ou Sable → aprovar código)
**Errado (R14).** Quinn audita CÓDIGO (AIOX 7 checks + quant overrides). Sable audita SQUAD (MANIFEST/MATRIX/GLOSSARY). Escopos distintos. Quinn dizendo "alpha parece boa" = overreach; Sable dizendo "coverage < 80%" = overreach.

### Gage → push antes de Kira APPROVED OU Tiago paper-mode completo
**Errado (R12 + Fase G).** Gage opera APÓS gates passarem. Fases E (CPCV), F (paper-mode ≥ 5), G (Sable/humano) são pré-requisito de push. Pular = publicar código sem validação quant.

### Aria → decidir schema quant sem Mira+Nova
**Errado.** Aria decide tech stack (lib, framework); Mira decide shape de feature/label; Nova decide quais campos B3 preservar. Schema quant é intersecção dos três — Aria não pode decidir sozinho.

### Morgan → escrever AC que referencia coisa não no thesis
**Errado (R13 + Constitution IV).** Toda AC de story quant rastreia ao thesis ou ao PRD. "Implementar volume imbalance" sem thesis que mencione volume imbalance = invenção. Pax deve pegar em `*validate-story-draft`.

### Dara → migration sem consultar Mira+Nova
**Errado.** Se schema toca feature/label/timestamp, Dara consulta Mira (spec YAML) e Nova (BRT, fase B3) antes de finalizar migration. Timezone BRT (R2) e campos de fase são críticos.

---

## Matriz de Velocidade (Síncrono vs Assíncrono)

Nem todo handoff é em tempo real. Alguns são batch (overnight, semanal).

| Handoff | Velocidade | Comentário |
|---------|-----------|-----------|
| Tiago → Riven (*tiago-gateway) | **Síncrono** (ms) | Ordem espera resposta |
| Mira → Tiago (sinal) | **Síncrono** (ms) | Runtime em produção |
| Nelo callback → Tiago | **Síncrono** (ms) | Callback DLL |
| Tiago → Riven (*reconcile) | **Síncrono diário** (EOD) | Fecha o dia |
| Tiago → Beckett (*tiago-calibrate) | **Batch semanal** | Recalibra engine |
| Mira → Beckett (feature spec) | **Assíncrono** | Spec antes de CPCV |
| Beckett → Riven (stress-test result) | **Assíncrono** | Pré-live ou trimestral |
| Nova → Mira (audit-feature) | **Assíncrono** | Durante design de feature |
| Kira → Mira (ideia) | **Assíncrono** | Pesquisa |
| River → Pax (story draft) | **Assíncrono** | Fase C do Q-SDC |
| Dex → Quinn (qa-gate) | **Assíncrono** | Fim da Fase D |
| Beckett → Mira → Kira (CPCV/DSR/PBO) | **Batch (horas)** | Fase E |
| Tiago → Sable (pré go-live) | **Assíncrono** | Fase G |
| Kira APPROVED → Gage (push) | **Assíncrono** | Fase H — só após todos gates |

---

## Protocolos de Escalação

### Quando humano entra

- **Ativação de live** (qualquer estratégia nova em produção) — Riven + humano assinam
- **Desarmar kill-switch** — após post-mortem, humano aprova
- **Mismatch EOD não resolvido em 30min** — Tiago escala
- **Feature book-based solicitada** (storage + pipeline) — decisão infra precisa humano
- **Conflito de autoridade entre agentes** (ex.: Nova vs Nelo sobre timestamp) — humano decide protocolo

### Quando Riven para tudo (kill)

- DD diário > 2 × daily budget
- Conexão DLL oscilando (≥ 3 disconnects em 10min)
- Mismatch de posição interno vs corretora
- Feature flag de regime "extreme" ativa por ≥ 5min
- Qualquer violação constitucional do squad (ex.: ordem sem gateway)

---

## Revisões

Este documento é revisado:
- **Antes de cada Block** (Block 1 Project Identity, Block 2 Alpha Thesis, etc.) — via `@squad-auditor *preblock-review {block}`
- **Após cada incidente live** (kill trigger, mismatch, rejection cascade) — via `@squad-auditor *post-incident {id}`
- **Ao adicionar novo agente ou alterar domínio** — via `@squad-auditor *full-audit`

**Quem revisa:** Sable (@squad-auditor). Humano aprova/rejeita findings críticos. Owner do agente corrige. Sable re-audita. Auditor nunca audita a si mesmo — humano audita Sable quando necessário.

---

*Matriz consolidada em 2026-04-21. Ver [MANIFEST.md](MANIFEST.md) para visão geral do squad.*
