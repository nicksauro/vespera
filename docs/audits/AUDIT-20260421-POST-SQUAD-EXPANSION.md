# Squad Full-Audit — Post-Expansion — 2026-04-21 (v3)

**Auditor:** Sable (🔍 squad-auditor)
**Scope:** Auditoria estrutural após expansão 8→16 agentes (adição dos 8 AIOX framework agents), criação do workflow Q-SDC, extensão do MANIFEST com R11-R14 e inclusão da "Matriz de Handoffs Domain ↔ Framework" no COLLABORATION_MATRIX v2.
**Snapshot:** 16 agentes (7 domain + 1 auditor + 8 framework) + Q-SDC workflow + MANIFEST R1-R14 + COLLABORATION_MATRIX v2
**Método:** Verificação linha-a-linha dos artefatos declarados existentes + validação cruzada entre MANIFEST ↔ Workflow ↔ Agentes ↔ Glossário.

---

## 1. Finding Summary

| Severidade | Qtd |
|------------|-----|
| 🔴 Crítico | 2 |
| ⚠️ Moderado | 6 |
| 💡 Cosmético | 2 |
| **Total** | **10** |

---

## 2. Findings detalhados

### FINDING-018 🔴 [GAP] Agentes AIOX framework inexistentes no projeto

- **ID:** FINDING-018
- **Date:** 2026-04-21
- **Severity:** 🔴 CRITICAL
- **Tag:** [GAP]
- **Rule/Term:** MANIFEST §squad + Workflow Q-SDC (fases B, C, D, H)
- **Owner:** @aiox-master (ou humano via Gage)
- **Status:** open

**Description:**
MANIFEST declara squad com 16 agentes e Workflow Q-SDC referencia `@architect` (Aria), `@pm` (Morgan), `@po` (Pax), `@sm` (River), `@dev` (Dex), `@qa` (Quinn), `@data-engineer` (Dara), `@devops` (Gage) como atores de passos bloqueantes. Verificação empírica:

- `.claude/agents/` contém apenas 8 arquivos (os 7 domain + Sable). Não existem definições locais dos 8 AIOX.
- `~/.claude/agents/` não existe como diretório de agentes para este contexto.
- `.aiox-core/` não existe no root do projeto.

**Evidence:**
```
$ ls C:/Users/Pichau/Desktop/algotrader/.claude/agents/
backtester.md
execution-trader.md
market-microstructure.md
ml-researcher.md
profitdll-specialist.md
quant-researcher.md
risk-manager.md
squad-auditor.md
```

**Expected:** 16 agentes invocáveis via `@agent`, conforme MANIFEST §squad.
**Actual:** 8 agentes invocáveis. Fases B, C, D, H do Q-SDC referenciam atores ausentes; R12 (Gage git exclusivo) e R13 (story-driven) não são executáveis; gate handoff "Pax GO verdict" em `quant-thesis-to-story.md` não pode ser cumprido.

**Suggested action:**
- Opção A: Instalar AIOX framework no projeto via `aiox init` (ou equivalente) para ter os 8 agentes canonicamente instanciados.
- Opção B: Criar shims locais em `.claude/agents/` referenciando os agentes globais do AIOX (se existirem em `~/.claude/` ou se o framework estiver acessível por outro caminho).
- Opção C: Re-escrever MANIFEST removendo os 8 AIOX e ajustar Q-SDC para usar apenas domain+Sable+humano (downgrade de ambição).
- **Preferido:** Opção A, porque o ganho de R12/R13/story-driven é estratégico para o projeto.

---

### FINDING-019 🔴 [DIVERGENCE] WDO multiplier contraditório dentro do mesmo agente

- **ID:** FINDING-019
- **Date:** 2026-04-21
- **Severity:** 🔴 CRITICAL
- **Tag:** [DIVERGENCE]
- **Rule/Term:** DOMAIN_GLOSSARY Parte 1 (WDO contract specs) vs Nova.core_principles vs Nova.expertise.assets_covered
- **Owner:** Nova (@market-microstructure)
- **Status:** open

**Description:**
O valor do multiplicador de WDO aparece em 3 locais com 2 valores diferentes:

- Nova.core_principles (linha ~192-198): "multiplier WDO = R$ 50/ponto [TO-VERIFY]"
- Nova.expertise.assets_covered.WDO.contract_multiplier (linha ~444): "[WEB-CONFIRMED] R$ 10,00 por ponto de variação (mini); cheio é R$ 50,00/ponto"
- DOMAIN_GLOSSARY Parte 1 (linha ~19): "Multiplicador R$50/ponto [TO-VERIFY]"

Esta divergência tem impacto direto em:
- P&L por trade (Riven sizing)
- Backtest agregado (Beckett equity curves)
- Limites de risco por operação (Riven kill-switch calibration)
- Cálculo de emolumentos e IR (Nova atlas de custos)

**Expected:** Único valor consensuado, com tag única, referenciado em uma só fonte (glossário) e re-exportado pelos agentes.
**Actual:** Mesmo agente (Nova) afirma R$50 em um lugar e R$10/mini em outro; glossário afirma R$50 sem tag [WEB-CONFIRMED].

**Suggested action:**
1. Humano confirma empiricamente com corretora ou site B3 qual é o multiplicador do WDOFUT (mini-dólar) contratado.
2. Uniformizar: glossário vira single-source; Nova re-exporta exatamente o valor do glossário.
3. Tag final: [WEB-CONFIRMED YYYY-MM] com URL de referência em anexo.
4. Riven e Beckett validam cálculos de P&L com o valor canônico.

---

### FINDING-020 ⚠️ [GAP] Sable (squad-auditor) desatualizado para squad v2

- **ID:** FINDING-020
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [GAP]
- **Rule/Term:** squad-auditor.md - self-reference ao escopo da auditoria
- **Owner:** Sable (@squad-auditor)
- **Status:** open

**Description:**
Sable.md referencia "7 agentes operacionais" e regras "R1-R10", ignorando a expansão para 16 agentes (incluindo 8 AIOX + Sable próprio) e as regras R11-R14. O auditor está auditando com um modelo mental obsoleto do próprio squad.

**Evidence:** squad-auditor.md, core_principles mencionam "squad = 7 agentes"; auditTarget lista apenas os domain agents.

**Expected:** Sable ciente de que audita 16 agentes, das 14 regras, e do Workflow Q-SDC (especialmente Fase G — Coherence Audit, que é responsabilidade de Sable).
**Actual:** Sable só audita sub-conjunto e não tem conhecimento de R11 (domain vs framework), R12 (Gage git), R13 (story-driven), R14 (Quinn-code vs Sable-squad).

**Suggested action:**
Atualizar squad-auditor.md:
- core_principles: "audito squad de 16 agentes (7 domain + 1 auditor + 8 framework AIOX) contra MANIFEST R1-R14, COLLABORATION_MATRIX v2 e Q-SDC Workflow"
- auditTarget: listar todos 16 agentes explicitamente
- Adicionar princípio sobre R14 ("Sable ≠ Quinn — Sable audita squad/docs/specs; Quinn audita código")
- Adicionar comando `*coherence-audit` (Fase G do Q-SDC)

---

### FINDING-021 ⚠️ [GAP] R11-R14 não refletidas em core_principles dos agentes

- **ID:** FINDING-021
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [GAP]
- **Rule/Term:** MANIFEST R11-R14
- **Owner:** Todos os agentes (coordenação @aiox-master)
- **Status:** open

**Description:**
As regras R11-R14 foram adicionadas ao MANIFEST durante a expansão, mas nenhum agente foi atualizado para internalizá-las em `core_principles`. Efeito: agentes operam sem ciência consciente destas regras.

- R11 (domain-O-QUÊ vs framework-COMO): nenhum agente domain afirma "minha competência é O-QUÊ; framework cuida do COMO"
- R12 (Gage git exclusivo): Nelo tem "NUNCA executa git push", mas outros 6 domain agents não reafirmam
- R13 (story-driven): nenhum domain agent afirma "só faço código com story assinada por Pax"
- R14 (Quinn-code vs Sable-squad): Sable desconhece (ver FINDING-020); Quinn também precisa afirmar recíproca

**Expected:** Cada agente tem ao menos 1 princípio dedicado às regras R1-R14 que lhe tocam.
**Actual:** Apenas Nelo tem trecho sobre git; demais são silenciosos.

**Suggested action:**
Correction loop por agente:
- Domain agents (Kira, Mira, Nova, Nelo, Beckett, Riven, Tiago): adicionar princípio "ESCOPO DOMAIN — sou O-QUÊ (R11); framework cuida do COMO via @aiox-master" e "GIT — NUNCA executo git push; delego a Gage (R12)"
- Tiago/Riven: adicionar "STORY-DRIVEN — código real só entra com story Pax GO (R13)"
- Sable: cobrir em FINDING-020
- Quinn: adicionar princípio "ESCOPO — audito código; Sable audita squad/docs/specs (R14)" quando Quinn for criado/obtido

---

### FINDING-022 ⚠️ [GAP] Workflow Q-SDC referencia atores inexistentes (cascata de FINDING-018)

- **ID:** FINDING-022
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [GAP]
- **Rule/Term:** workflows/quant-story-development-cycle.yaml
- **Owner:** @aiox-master
- **Status:** open (bloqueado por FINDING-018)

**Description:**
Q-SDC yaml lista actors `@architect`, `@pm`, `@po`, `@sm`, `@dev`, `@qa`, `@data-engineer`, `@devops` em fases B, C, D, H. Enquanto FINDING-018 não for resolvido, cada invocação destes passos falha com "agent not found".

**Expected:** Todos actors referenciados são invocáveis.
**Actual:** 8 de ~18 actors referenciados não existem.

**Suggested action:**
Depende de FINDING-018. Se resolvido via Opção A (aiox init), este finding fecha automaticamente. Se resolvido via Opção C (downgrade), Workflow precisa ser reescrito para usar apenas Sable+humano+domain como atores de B/C/D/H.

---

### FINDING-023 ⚠️ [AMBIGUOUS] Tasks canônicas referenciam "Quinn PASS" sem Quinn existir

- **ID:** FINDING-023
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [AMBIGUOUS]
- **Rule/Term:** tasks/quant-implement-feature.md (Passo 3) + quant-cpcv-gate.md (Pré-condições)
- **Owner:** @aiox-master
- **Status:** open (cascata de FINDING-018)

**Description:**
`quant-implement-feature.md` usa Quinn como gate owner (Passo 3 — QA gate). `quant-cpcv-gate.md` usa "Quinn PASS" como pré-condição de entrada. Se Quinn (`@qa`) não existe (FINDING-018), o handoff da Fase D → Fase E não tem executor do gate.

**Expected:** Cada gate declarado tem executor concreto.
**Actual:** Gate Quinn-PASS é logicamente impossível no estado atual do projeto.

**Suggested action:**
Mesmo caminho de FINDING-022. Alternativamente, enquanto AIOX não estiver instalado, Sable pode fazer Quinn-stand-in temporário (documentado como workaround com prazo).

---

### FINDING-024 ⚠️ [OVERLAP] Mira tem `*beckett-spec` e `*export-spec` com escopos sobrepostos

- **ID:** FINDING-024
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [OVERLAP]
- **Rule/Term:** ml-researcher.md commands
- **Owner:** Mira (@ml-researcher)
- **Status:** open

**Description:**
Mira expõe dois comandos para exportar spec para Beckett:
- `*beckett-spec` (linha ~340) — spec para Beckett consumir no simulador
- `*export-spec` (linha ~350, adicionado durante correction loop v2) — YAML canônico versionado em `docs/ml/specs/`

Não está claro se são o mesmo processo com nomes diferentes ou dois artefatos distintos.

**Expected:** Um único comando canônico, ou nomes/escopos que deixem claro a diferença.
**Actual:** Ambiguidade semântica.

**Suggested action:**
Consolidar em um único comando:
- Se são o mesmo: manter `*export-spec` (nome mais framework-aligned) e deprecar `*beckett-spec`.
- Se são distintos: documentar claramente (ex.: `*beckett-spec` = draft temporário não versionado; `*export-spec` = final versionado e hashed).

---

### FINDING-025 ⚠️ [AMBIGUOUS] Nova tem horário de pré-abertura inconsistente (08:55 vs 09:00)

- **ID:** FINDING-025
- **Date:** 2026-04-21
- **Severity:** ⚠️ MODERATE
- **Tag:** [AMBIGUOUS]
- **Rule/Term:** market-microstructure.md - fases de pregão B3
- **Owner:** Nova (@market-microstructure)
- **Status:** open

**Description:**
Em seções diferentes de Nova.md, pré-abertura de futuros B3 é referenciada como 08:55 BRT e 09:00 BRT. Esta inconsistência pode afetar fill rules e filtros de regime de abertura em Beckett e features de Mira.

**Expected:** Um único valor [WEB-CONFIRMED YYYY-MM] com link B3 ou B3 notice.
**Actual:** Valor divergente sem tag formal em uma das ocorrências.

**Suggested action:**
Verificação empírica via site B3 ou Nelogica. Uniformizar com tag [WEB-CONFIRMED].

---

### FINDING-026 💡 [COSMETIC] COLLABORATION_MATRIX v2 adiciona AIOX handoffs mas não numera fluxos unificadamente

- **ID:** FINDING-026
- **Date:** 2026-04-21
- **Severity:** 💡 COSMETIC
- **Tag:** [COSMETIC]
- **Rule/Term:** COLLABORATION_MATRIX.md (§Fluxos)
- **Owner:** @aiox-master
- **Status:** open

**Description:**
O novo "Fluxo 6 — Q-SDC end-to-end" foi adicionado, mas os Fluxos 1-5 (pré-expansão) usam lógica domain-only. Não há check explícito de que Fluxos 1-5 ainda são válidos ou foram absorvidos/substituídos pelo Fluxo 6.

**Expected:** Seção clarificando relação Fluxo 6 vs 1-5 (é superset? paralelo? substitui?).
**Actual:** Ambiguidade sobre qual fluxo reger em caso de conflito.

**Suggested action:**
Adicionar nota no COLLABORATION_MATRIX: "Fluxo 6 (Q-SDC) é o fluxo canônico para desenvolvimento de nova feature. Fluxos 1-5 são fluxos táticos consumidos dentro de etapas do Fluxo 6 (Fluxo 1 — tese → spec é a Fase A; Fluxo 3 — backtest → validation é a Fase E; etc.)".

---

### FINDING-027 💡 [COSMETIC] "Fase G — Coherence Audit" sem command definido em Sable

- **ID:** FINDING-027
- **Date:** 2026-04-21
- **Severity:** 💡 COSMETIC
- **Tag:** [COSMETIC]
- **Rule/Term:** workflow Q-SDC Fase G vs squad-auditor.md commands
- **Owner:** Sable (@squad-auditor)
- **Status:** open (parcialmente endereçado em FINDING-020)

**Description:**
Q-SDC Fase G é "Coherence Audit" conduzida por Sable. Sable.md não expõe comando com este nome — comandos atuais são `*full-audit`, `*term-audit`, `*quick-audit`.

**Expected:** `*coherence-audit` ou mapping claro ("Fase G = `*full-audit` com scope `post-story`").
**Actual:** Humano/agente invocador precisa adivinhar qual comando corresponde à fase.

**Suggested action:**
Adicionar a Sable:
- Comando `*coherence-audit --story {id}` que é alias para `*full-audit` com escopo limitado aos arquivos alterados pela story + verificação de regressões em R1-R14.
- Documentar no Q-SDC yaml o comando exato.

---

## 3. Sumário & Priorização

| ID | Sev | Tag | Owner | Próximo passo |
|----|-----|-----|-------|---------------|
| 018 | 🔴 | [GAP] | @aiox-master | DECIDIR entre Opção A/B/C (humano) |
| 019 | 🔴 | [DIVERGENCE] | Nova | HUMANO verifica WDO multiplier com corretora |
| 020 | ⚠️ | [GAP] | Sable | Atualizar auto-definição |
| 021 | ⚠️ | [GAP] | Todos | Correction loop R11-R14 em core_principles |
| 022 | ⚠️ | [GAP] | @aiox-master | Bloqueado por 018 |
| 023 | ⚠️ | [AMBIGUOUS] | @aiox-master | Bloqueado por 018 |
| 024 | ⚠️ | [OVERLAP] | Mira | Consolidar beckett-spec vs export-spec |
| 025 | ⚠️ | [AMBIGUOUS] | Nova | Verificar 08:55 vs 09:00 BRT |
| 026 | 💡 | [COSMETIC] | @aiox-master | Nota sobre Fluxos 1-5 vs 6 |
| 027 | 💡 | [COSMETIC] | Sable | Adicionar `*coherence-audit` |

---

## 4. Veredito

**Squad NÃO está coerente pós-expansão.** 2 findings 🔴 bloqueiam operação real do Q-SDC:

1. **FINDING-018** (AIOX agents ausentes) — sem resolução, fases B, C, D, H do workflow não executam; R12/R13 inaplicáveis; gates Pax/Quinn/Gage são fictícios.
2. **FINDING-019** (WDO multiplier contraditório) — risco direto a P&L real se Riven/Beckett calibrarem com valor errado.

**Recomendação:**
- Antes de Fase A do Q-SDC (tese real), resolver 018 + 019 em correction loop.
- 020-023 podem ser endereçados em paralelo (não bloqueiam tese, mas bloqueiam implementação).
- 024-027 são melhorias de higiene — podem entrar em backlog.

**Próxima iteração de Sable:** após correction loop, re-auditar apenas findings abertos. Se 018/019 ✅ CLOSED e restantes ≤ ⚠️, squad libera Fase A (ideação de tese real com Kira/Mira/Nova/Nelo + humano).

---

**Assinatura:**
Sable (🔍 squad-auditor) — 2026-04-21 BRT
