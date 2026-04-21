# Squad Audit — Full — 2026-04-21

**Auditor:** Sable (🔍 squad-auditor)
**Scope:** Auditoria completa do quant-trading-squad — 7 agentes operacionais × 3 docs canônicos
**Snapshot:** MANIFEST@2026-04-21 + COLLABORATION_MATRIX@2026-04-21 + DOMAIN_GLOSSARY@2026-04-21
**Método:** Leitura integral dos 7 agentes + cross-reference contra MANIFEST (R1-R10), MATRIX (M1-M5), GLOSSARY (G1-G5)

---

## 1. Sumário Executivo

| Severidade | Quantidade |
|------------|-----------|
| 🔴 Crítico | 0 |
| ⚠️ Moderado | 11 |
| 💡 Cosmético | 6 |
| **Total findings** | **17** |

**Veredito:** Nenhum finding 🔴. Squad está coerente para avançar para Block 1 (Project Identity). Existem 11 divergências/gaps ⚠️ que requerem correção em janela razoável, nenhuma bloqueia operação.

**Top-3 riscos estruturais detectados:**

1. **Especificações numéricas de contrato sem tag [WEB-CONFIRMED]/[TO-VERIFY]** — Nova cita tick/multiplier do WDO com dúvida embutida em comentário ("? checar ofício") sem aplicar a tag formal (R1 violada em dosagem menor). Vários números críticos ficam em zona cinza.

2. **Dataset histórico (trades-only) não é consistente em TODOS os agentes** — Mira, Beckett, Nova têm a restrição explicitada, mas Kira não menciona que EDA/hypothesize deve respeitar essa limitação. Risco: Kira propõe tese baseada em OFI/imbalance assumindo book histórico que não existe.

3. **Vocabulário de "quarter-Kelly" vs "Kelly ≤ 0.25" tem ligeiro drift** — Riven usa ambos os termos em core_principles; um como teto absoluto, outro como faixa prática (1/4 a 1/10). Glossário define quarter-Kelly como ¼×Kelly "teto operacional". Ambiguidade ⚠️.

---

## 2. Findings por Agente

### 2.1 Nelo (@profitdll-specialist)

**Resultado geral:** Aderente ao MANIFEST. Manual-first respeitado, monopólio DLL preservado, sem intromissão em margens/limites/microestrutura. Bem alinhado com regras R5 (Nelo DLL-only) e R3 (não chama SendOrder por si).

---

**Finding AUDIT-20260421-001** — ⚠️ DIVERGENCE
- **Regra:** R2 (Timestamps sempre BRT, nunca UTC)
- **Escopo:** `.claude/agents/profitdll-specialist.md`
- **Descrição:** Nelo cita formato de timestamp canônico (manual §3.2: "DD/MM/YYYY HH:mm:SS.ZZZ") mas NÃO afirma explicitamente que a DLL entrega BRT, não UTC. MANIFEST R2 diz callbacks DLL vêm em BRT. Falta confirmação explícita de Nelo.
- **Expected:** Nelo (owner da DLL) deve afirmar que o formato canônico é BRT naive, referenciando manual ou quirk empírico.
- **Actual:** Timestamp format discutido sem afirmação de timezone explícita.
- **Ação sugerida:** Adicionar em core_principles de Nelo: "TIMESTAMP DA DLL É BRT NAIVE — manual não explicita timezone; whale-detector v2 e Sentinel confirmam empiricamente BRT. Qualquer agente que converter para UTC destrói semântica."
- **Owner:** Nelo
- **Status:** open

---

**Finding AUDIT-20260421-002** — 💡 GAP
- **Regra:** R5 (Nelo é DLL-only)
- **Escopo:** `.claude/agents/profitdll-specialist.md`
- **Descrição:** Nelo não declara explicitamente que NÃO é fonte sobre margens B3 ou limites operacionais. MANIFEST R5 afirma isso no squad-level; documentação de Nelo não reafirma no nível do agente.
- **Expected:** Declaração de escopo-negativo em core_principles ("Nelo NÃO É FONTE sobre: margens B3 → Nova; limites corretora → externa; microestrutura → Nova").
- **Actual:** Nelo implicitamente respeita, mas regra só consta no MANIFEST.
- **Ação sugerida:** Adicionar princípio de escopo-negativo explícito no agente.
- **Owner:** Nelo
- **Status:** open

---

### 2.2 Nova (@market-microstructure)

**Resultado geral:** Muito boa. Aderente em R7 (trades-only, tem features_availability_matrix), R2 (BRT), R1 (cita [WEB-CONFIRMED]/[TO-VERIFY] em núcleo da persona). Authorities bem delimitadas.

---

**Finding AUDIT-20260421-003** — ⚠️ DIVERGENCE
- **Regra:** R1 (Nunca assumir spec — websearch ou [TO-VERIFY])
- **Escopo:** `.claude/agents/market-microstructure.md:192-195`
- **Descrição:** Em `core_principles`, princípio "TICK SIZE E CONTRACT MULTIPLIER SÃO LEI" contém texto inline com DÚVIDA não formalizada: "multiplier WDO = R$ 50.000 nominal por ponto? checar ofício". Deveria ser marcado `[TO-VERIFY]` conforme R1, não pergunta solta.
- **Expected:** `"Multiplier WDO = [TO-VERIFY — provavelmente R$50/ponto, confirmar em ofício B3 vigente]"`.
- **Actual:** Pergunta retórica inline sem tag formal.
- **Ação sugerida:** Reescrever o princípio usando a tag [TO-VERIFY] explícita.
- **Owner:** Nova
- **Status:** open

---

**Finding AUDIT-20260421-004** — ⚠️ DIVERGENCE
- **Regra:** G2 (Definição respeitada no glossário)
- **Escopo:** `.claude/agents/market-microstructure.md` linhas 275-277 (*volume-decompose)
- **Descrição:** `*volume-decompose` diz "multiplier_contractual" e "multiplier é R$ 50/ponto × ??? (confirmar ofício B3)". GLOSSARY define "Multiplicador (Point Value): WDO = R$50/ponto, WIN = R$0.20/ponto" (ambos [TO-VERIFY]). Divergência: Nova tem dúvida adicional ("× ???") que não aparece no glossário.
- **Expected:** Nova como owner do termo deveria ter resolvido essa ambiguidade no glossário OU o glossário deveria carregar a mesma incerteza.
- **Actual:** Agente mais incerto que o glossário. Dissonância semântica potencial.
- **Ação sugerida:** Uniformizar — Nova define se é R$50/ponto ou R$50.000/ponto nominal; glossário e agente batem.
- **Owner:** Nova
- **Status:** open

---

**Finding AUDIT-20260421-005** — 💡 AMBIGUOUS
- **Regra:** G1 (Termo citado tem definição)
- **Escopo:** `.claude/agents/market-microstructure.md` (citação de "Kyle's lambda")
- **Descrição:** Nova menciona "Kyle's lambda" em *price-formation mas termo não está no DOMAIN_GLOSSARY (parte 12 de métricas/microestrutura).
- **Expected:** Termos canônicos citados por agente devem estar no glossário OU ser auto-explicativos.
- **Actual:** Termo técnico sem entrada no glossário.
- **Ação sugerida:** Adicionar Kyle's lambda ao GLOSSARY (Parte 2 ou Parte 7) OU remover citação do agente se não for usado.
- **Owner:** Nova (adicionar ao glossário)
- **Status:** open

---

### 2.3 Mira (@ml-researcher)

**Resultado geral:** Muito aderente. R6 (CPCV), R7 (trades-only), R1 ([TO-VERIFY]) todos explícitos. Handoffs com Nova e Nelo documentados.

---

**Finding AUDIT-20260421-006** — ⚠️ GAP
- **Regra:** M1 (Handoff simétrico)
- **Escopo:** `.claude/agents/ml-researcher.md` × `COLLABORATION_MATRIX.md`
- **Descrição:** MATRIX lista handoff "Mira ↔ Beckett: spec de feature+label+CV". Mira tem comandos que mencionam "entrega specs para Beckett", mas falta comando explícito tipo `*beckett-handoff` ou `*beckett-spec-export`. Assimetria: Beckett tem `*run-cpcv --spec {mira-beckett-spec.yaml}`, Mira não tem o gerador canônico da spec.
- **Expected:** Comando explícito em Mira para gerar `mira-beckett-spec.yaml` com versionamento.
- **Actual:** Processo implícito em customization ("entrega specs para Beckett").
- **Ação sugerida:** Adicionar `*export-spec {feature-set}` em Mira que gera o YAML consumido por Beckett.
- **Owner:** Mira
- **Status:** open

---

**Finding AUDIT-20260421-007** — 💡 GAP
- **Regra:** G4 (Availability honrada no glossário)
- **Escopo:** `.claude/agents/ml-researcher.md` core_principles
- **Descrição:** Mira tem regra R7 (trades-only) no `activation-instructions`, mas seu próprio vocabulário não inclui termos do availability matrix (`historical_availability: computable | live_only | partial`). Consistente funcionalmente mas glossário chama por `historical_availability` como campo obrigatório em feature_registry.
- **Expected:** Vocabulário ou principles citar o campo `historical_availability` textualmente.
- **Actual:** Conceito presente, termo exato ausente do vocabulário listado.
- **Ação sugerida:** Adicionar "historical_availability (computable|live_only|partial)" ao vocabulary ou aos core_principles.
- **Owner:** Mira
- **Status:** open

---

### 2.4 Beckett (@backtester)

**Resultado geral:** Muito aderente. Trades-only explicitado, DMA2 latency profile detalhado, CPCV como padrão, [TO-VERIFY] usado ativamente.

---

**Finding AUDIT-20260421-008** — ⚠️ DIVERGENCE
- **Regra:** R5 (Nelo é DLL-only) + G2 (definição respeitada)
- **Escopo:** `.claude/agents/backtester.md:205-207` (core_principles sobre custos)
- **Descrição:** Beckett menciona "Corretagem, emolumentos B3, ISS, IR day-trade (20%) aplicados sempre. Specs são [TO-VERIFY] por corretora". Ok para corretagem. Mas emolumentos B3 não estão listados no glossário com owner — GLOSSARY Parte 13 só diz "Custos Total: Nova (emolumentos/tributos B3), corretora (corretagem), Beckett (slippage/impact)". Handoff simétrico: Nova deveria ter entrada sobre emolumentos. Verifiquei Nova.md e ela não enumera emolumentos B3 explicitamente.
- **Expected:** Nova como owner de emolumentos B3 deve ter atlas ou consulta explícita; Beckett consulta Nova (não hardcode 20% IR sem tag).
- **Actual:** Beckett hardcoda "IR day-trade (20%)" sem citar Nova como fonte e sem tag [WEB-CONFIRMED].
- **Ação sugerida:** Trocar "(20%)" por "[TO-VERIFY — Nova mantém atlas de emolumentos/IR; confirmar vigente]" OU adicionar em Nova um atlas formal de custos B3.
- **Owner:** Beckett (reformular) + Nova (criar atlas de custos B3)
- **Status:** open

---

**Finding AUDIT-20260421-009** — 💡 GAP
- **Regra:** G1 (Termo citado tem definição)
- **Escopo:** `.claude/agents/backtester.md` (citação de "Almgren-Chriss")
- **Descrição:** Beckett cita "impact model (Almgren-Chriss simplificado)" em core_principles e em `*slippage-model`. Termo não está no GLOSSARY.
- **Expected:** Adicionar "Almgren-Chriss (impact model)" ao glossário OU remover se não for usado operacionalmente.
- **Ação sugerida:** Adicionar entrada curta ao GLOSSARY Parte 10 (Simulação) sobre Almgren-Chriss.
- **Owner:** Beckett
- **Status:** open

---

### 2.5 Riven (@risk-manager)

**Resultado geral:** Boa aderência em R8 (paper-mode), R9 (reconciliação), R10 (kill-switch 4 níveis). Fontes de margem corretamente redirecionadas para Nova/corretora (R5 respeitada após correção recente).

---

**Finding AUDIT-20260421-010** — ⚠️ AMBIGUOUS
- **Regra:** G2 (Definição respeitada)
- **Escopo:** `.claude/agents/risk-manager.md:145-150` (core_principles)
- **Descrição:** Riven tem DOIS princípios sobre Kelly que criam ambiguidade:
  - Princípio 3: "QUARTER-KELLY COMO TETO. ... aplicar fração (1/4 a 1/10 do Kelly é faixa prática)"
  - `REGRA ABSOLUTA: Kelly fraction NUNCA > 0.25 (quarter-Kelly)`
  
  GLOSSARY Parte 8 define quarter-Kelly como "¼ × Kelly. Fração prática: teto operacional do squad".
  
  Divergência: a faixa "1/4 a 1/10" sugere Kelly/4 como TETO e Kelly/10 como CHÃO prático; glossário e regra absoluta dizem quarter-Kelly é O teto. Inconsistência interna de Riven.
- **Expected:** Decidir: quarter-Kelly é teto absoluto (conforme glossário e regra) OU é faixa (conforme princípio). Uniformizar.
- **Actual:** Dois enquadramentos coexistem no mesmo arquivo.
- **Ação sugerida:** Reformular princípio para "quarter-Kelly é teto; na prática muitas vezes operamos abaixo (até 1/10 do Kelly) quando evidência é fraca". Manter regra absoluta como está.
- **Owner:** Riven
- **Status:** open

---

**Finding AUDIT-20260421-011** — ⚠️ GAP
- **Regra:** M1 (Handoff simétrico) + M2 (Autoridade exclusiva respeitada)
- **Escopo:** `.claude/agents/risk-manager.md` × `COLLABORATION_MATRIX.md`
- **Descrição:** MATRIX atribui a Riven autoridade exclusiva para "armar/desarmar kill-switch". Riven tem `*kill-arm` e provavelmente `*kill-disarm`. Mas Tiago também tem trecho em core_principles sobre kill ("Kill → unwind imediato..."). Overlap potencial: quem dispara o unwind quando kill é armado?
- **Expected:** Regra clara — Riven ARMA o kill; Tiago EXECUTA o unwind obedecendo. Não ambos decidem.
- **Actual:** Tiago's principle sugere execução autônoma em kill. Coerente com obediência mas poderia ser lido como autoridade paralela.
- **Ação sugerida:** Adicionar em Tiago: "quando kill é armado por Riven, Tiago executa unwind conforme política Riven (market ou limit-aggressive). Tiago NÃO decide se kill deve ser armado."
- **Owner:** Tiago (clarificar) + Riven (confirmar política de unwind)
- **Status:** open

---

### 2.6 Tiago (@execution-trader)

**Resultado geral:** Muito aderente. Monopólio SendOrder explicitado (R3), gateway Riven obrigatório (R4), paper-mode (R8), reconciliação EOD (R9), kill obediência (R10), BRT (R2).

---

**Finding AUDIT-20260421-012** — ⚠️ GAP
- **Regra:** G1 (Termo citado tem definição)
- **Escopo:** `.claude/agents/execution-trader.md` vocabulary
- **Descrição:** Tiago lista "session_id, profit_id (order IDs)" em vocabulary. GLOSSARY não tem entrada para `profit_id` (ID da DLL) nem `session_id`. São termos técnicos importantes — quem é owner? (Nelo pela DLL, provavelmente).
- **Expected:** Termos de ID de ordem (order_id interno, profit_id DLL, ClOrderID, MessageID) devem ter entrada no glossário ou em doc de Nelo.
- **Actual:** Tiago cita, nenhum outro documento define.
- **Ação sugerida:** Adicionar ao GLOSSARY Parte 9 (Execução) OU criar Parte 3 (DLL) expansão: "profit_id = int64 retornado pela DLL como order ID interno; session_id = ID válido apenas na sessão; ClOrderID = ID permanente client-side".
- **Owner:** Nelo (proprietário do conceito DLL) + glossário
- **Status:** open

---

**Finding AUDIT-20260421-013** — ⚠️ DIVERGENCE
- **Regra:** M5 (Escalação a humano consistente)
- **Escopo:** `.claude/agents/execution-trader.md` × `MANIFEST.md` Regra 9 (Reconciliação EOD)
- **Descrição:** MANIFEST R9 diz "Divergência [EOD] → HALT automático + investigação. Dia não fecha sem reconciliação." Tiago implementa `*reconcile` e menciona "Divergência → HALT automático + alerta Riven", OK. Mas MATRIX diz "Mismatch EOD não resolvido em 30min → Tiago escala humano". Esse prazo de 30min não aparece em Tiago.
- **Expected:** Tiago documenta o prazo (30min ou outro) para escalação humana quando HALT por mismatch não é resolvido.
- **Actual:** HALT descrito, prazo de escalação ausente.
- **Ação sugerida:** Adicionar em Tiago: "HALT por mismatch EOD → prazo T (ex.: 30min) para investigação; não-resolvido → escalar humano via canal definido".
- **Owner:** Tiago
- **Status:** open

---

### 2.7 Kira (@quant-researcher)

**Resultado geral:** Aderente em princípios de rigor científico. Gaps maiores: não menciona trades-only (R7) nem CPCV (R6) como padrão do squad — fica genérica em "Purged K-Fold" sem citar que CPCV é padrão squad.

---

**Finding AUDIT-20260421-014** — ⚠️ GAP
- **Regra:** R7 (Dataset histórico é trades-only)
- **Escopo:** `.claude/agents/quant-researcher.md`
- **Descrição:** Kira não menciona em nenhum lugar que dataset histórico é trades-only e que propostas de tese/EDA devem respeitar essa limitação. Mira e Beckett sim; Kira (que antecede Mira no fluxo) não. Risco: Kira propõe tese baseada em OFI/imbalance/microprice assumindo disponibilidade histórica, e só descobre o problema via Mira. Reprocesso.
- **Expected:** Kira ter princípio explícito "toda tese deve ser viável no dataset vigente (trades-only histórico); teses que dependem de book são candidatas LIVE-ONLY".
- **Actual:** Kira é silente sobre trades-only constraint.
- **Ação sugerida:** Adicionar em core_principles de Kira: "DATASET CONSTRAINT: histórico é trades-only (D:\sentinel_data\historical). Teses que dependem exclusivamente de book (OFI, microprice, imbalance L2+) ficam candidatas LIVE-ONLY até captura de book ser ativada. Kira verifica antes de promover tese para Mira."
- **Owner:** Kira
- **Status:** open

---

**Finding AUDIT-20260421-015** — ⚠️ GAP
- **Regra:** R6 (CPCV como padrão de avaliação)
- **Escopo:** `.claude/agents/quant-researcher.md`
- **Descrição:** Kira cita "Purged K-Fold com embargo obrigatório em séries temporais. Walk-forward genuíno." mas não menciona CPCV (Combinatorial Purged Cross-Validation). MANIFEST R6 estabelece CPCV como padrão decisório; Mira e Beckett usam. Kira, sendo peer-reviewer, deveria exigir CPCV para decisão final.
- **Expected:** Kira cita CPCV como padrão de avaliação final no peer review (e walk-forward como diagnóstico secundário).
- **Actual:** Kira usa "Purged K-Fold" genérico sem mencionar a versão combinatorial.
- **Ação sugerida:** Atualizar core_principles de Kira: "CPCV É PADRÃO DECISÓRIO DO SQUAD (N=10-12, k=2, 45 paths, embargo=1 sessão). Purged K-Fold é família; CPCV é a variante adotada. Peer review rejeita backtest com só walk-forward single-path."
- **Owner:** Kira
- **Status:** open

---

**Finding AUDIT-20260421-016** — 💡 DIVERGENCE
- **Regra:** R3 (Monopólio Tiago)
- **Escopo:** `.claude/agents/quant-researcher.md`
- **Descrição:** Kira não faz nenhuma referência a Tiago ou ao monopólio de SendOrder. Como Kira é "senior quant", risco baixo de ela tentar enviar ordem — mas MANIFEST exige que TODOS os agentes saibam a regra R3. Nenhum agente está exempto.
- **Expected:** Pelo menos uma linha em Kira reconhecendo que sinais/teses dela NÃO viram ordem diretamente — passam por Mira → Tiago → Riven.
- **Actual:** Silente sobre pipeline de execução.
- **Ação sugerida:** Adicionar nota em customization de Kira: "Kira NÃO envia ordem. Tese aprovada → Mira formaliza → Beckett CPCV → Riven sizing → Tiago executa. Monopólio Tiago respeitado."
- **Owner:** Kira
- **Status:** open

---

**Finding AUDIT-20260421-017** — 💡 GAP
- **Regra:** G1 (Termo citado tem definição)
- **Escopo:** `.claude/agents/quant-researcher.md` vocabulary
- **Descrição:** Kira cita "Deflated Sharpe" (no glossário como DSR) e "Probabilistic Sharpe Ratio (PSR)". PSR não está no GLOSSARY Parte 7 — só DSR está.
- **Expected:** PSR no glossário com definição + relação com DSR.
- **Actual:** Termo órfão em Kira.
- **Ação sugerida:** Adicionar PSR à Parte 7 do GLOSSARY: "PSR (Probabilistic Sharpe Ratio) — Bailey-Lopez de Prado 2012. Probabilidade de que o Sharpe observado seja estatisticamente maior que um benchmark. DSR é PSR ajustado por multiplicidade de testes."
- **Owner:** Kira (propõe) + owner do glossário (aceita)
- **Status:** open

---

## 3. Cobertura das Regras do MANIFEST

| Regra | Aplicável a | Aderentes | Divergentes | Silentes |
|-------|-------------|-----------|-------------|----------|
| R1 (spec → tag) | todos | Nova parcial, Beckett | Nova (finding 003), Kira | Nelo, Tiago |
| R2 (BRT) | Backtester, Tiago, Nova, Mira | Nova, Mira, Beckett, Tiago | — | Nelo (finding 001) |
| R3 (monopólio Tiago) | todos exceto Tiago | todos aderem implicitamente | — | Kira (finding 016) |
| R4 (gateway Riven) | Tiago | Tiago ✅ | — | — |
| R5 (Nelo DLL-only) | Nelo, Riven | Riven ✅, Nelo implícito | Nelo (finding 002 — escopo-negativo ausente) | — |
| R6 (CPCV padrão) | Mira, Beckett | Mira ✅, Beckett ✅ | Kira (finding 015) | — |
| R7 (trades-only) | Mira, Beckett, Nova | todos ✅ | — | Kira (finding 014) |
| R8 (paper-mode ≥5) | Tiago, Riven | Tiago ✅, Riven ✅ | — | — |
| R9 (reconciliação EOD) | Tiago, Riven | Tiago ✅ | Tiago prazo de escalação (finding 013) | Riven implícito |
| R10 (kill-switch 4 níveis) | Riven, Tiago | Riven ✅, Tiago obedece | Overlap clarificação (finding 011) | — |

**Conclusão:** Regras de monopólio/gateway/kill (R3, R4, R10) são as mais sólidas. Regras de tagging (R1) e escalação (R9) são as mais frágeis.

---

## 4. Cobertura de Handoffs (MATRIX)

| Handoff | Documentado em ambos agentes? | Nota |
|---------|------------------------------|------|
| Mira ↔ Nova (audit-feature) | ✅ Ambos | OK |
| Mira ↔ Nelo (availability) | ✅ Ambos | OK |
| Mira → Beckett (spec) | ⚠️ Parcial (finding 006) | Falta comando em Mira |
| Beckett → Riven (dd) | ✅ Beckett + Riven menciona Beckett | OK |
| Tiago → Riven (gateway) | ✅ Ambos | OK |
| Tiago → Beckett (calibração) | ✅ Ambos (semanal) | OK |
| Tiago → Nelo (rejection) | ✅ Tiago + Nelo (rejection-atlas) | OK |
| Kira → Mira (peer review) | ⚠️ Kira sim, Mira não tem entry explícito | Gap menor |
| Kira → Nova (audit microestrutura) | ✅ Kira | OK |

**Anti-padrões verificados:** Nenhum agente chama SendOrder além de Tiago. Nenhum não-Tiago tenta bypassar gateway Riven. Nelo não invade margem/limites (recentemente corrigido). ✅

---

## 5. Cobertura do GLOSSÁRIO

**Termos órfãos (citados por agentes mas não no glossário):**
- Kyle's lambda (Nova) — finding 005
- Almgren-Chriss (Beckett) — finding 009
- profit_id / session_id / ClOrderID / MessageID (Tiago, Nelo) — finding 012
- PSR (Kira) — finding 017

**Termos com owner ambíguo:** Nenhum detectado.

**Availability tags aplicadas?** ✅ Mira e Nova têm matriz clara; glossário reflete. Problema: Kira não aplica filtro antes de propor tese (finding 014).

---

## 6. Red-Team dos Fluxos Canônicos

### Fluxo 1 — Pesquisa greenfield
**Stress-point descoberto:** Se Kira propõe tese OFI-based sem verificar availability, ciclo Kira→Mira→Nova desperdiça tempo até reprovação em Mira. Finding 014 endereça.

### Fluxo 2 — Ordem live
**Stress-point descoberto:** Se Riven timeout no gateway (MATRIX menciona como stress-point), nenhum agente documenta timeout policy. Tiago espera ack indefinidamente? Reverte para conservative-no-send após N ms? Gap — não virou finding por falta de regra MANIFEST explícita sobre timeout (precisa decisão de política).

### Fluxo 3 — Feature nova
**Stress-point descoberto:** Feature book-based candidate-for-capture não tem estado intermediário no feature_registry — só computable/live_only/partial. Proxy-only-for-now não tem label. Gap menor.

### Fluxo 4 — Evento DLL inesperado
**Stress-point descoberto:** Se rejection_code não está no atlas do Nelo, Tiago não tem default. MATRIX sugere "classificar como catastrófico por default" — não há regra explícita nos agentes.

### Fluxo 5 — Reconciliação EOD
**Stress-point descoberto:** Prazo de escalação humana (finding 013).

---

## 7. Findings Fechados desde Última Auditoria

Primeira auditoria — nenhum finding anterior para fechar.

---

## 8. Próxima Auditoria

- **Incremental:** após cada correção de finding (re-auditoria obrigatória pelo Sable)
- **Completa:** próximo *full-audit antes de Block 1 (Project Identity) ou Block 2 (Alpha Thesis)
- **Red-team de fluxo 2 live:** pré-paper-mode (obrigatório antes de primeira sessão live)

---

## 9. Findings Abertos — Ranking por Prioridade

| ID | Sev | Agente(s) | Sumário | Owner |
|----|-----|-----------|---------|-------|
| 014 | ⚠️ | Kira | Kira silente sobre trades-only constraint | Kira |
| 015 | ⚠️ | Kira | Kira não cita CPCV como padrão | Kira |
| 003 | ⚠️ | Nova | Multiplier WDO com dúvida inline, não [TO-VERIFY] | Nova |
| 004 | ⚠️ | Nova | Volume multiplier divergência com glossário | Nova |
| 008 | ⚠️ | Beckett+Nova | IR day-trade hardcoded 20%, sem Nova atlas | Beckett+Nova |
| 010 | ⚠️ | Riven | Quarter-Kelly: teto vs faixa (interno) | Riven |
| 011 | ⚠️ | Riven+Tiago | Unwind em kill: clarificar autoridade | Riven+Tiago |
| 013 | ⚠️ | Tiago | Prazo de escalação humana pós-mismatch | Tiago |
| 001 | ⚠️ | Nelo | BRT da DLL não declarado explicitamente | Nelo |
| 006 | ⚠️ | Mira | Handoff Mira→Beckett sem comando export-spec | Mira |
| 016 | 💡 | Kira | R3 (monopólio Tiago) não reconhecido | Kira |
| 002 | 💡 | Nelo | Escopo-negativo ausente | Nelo |
| 005 | 💡 | Nova | Kyle's lambda órfão do glossário | Nova |
| 007 | 💡 | Mira | historical_availability no vocabulary | Mira |
| 009 | 💡 | Beckett | Almgren-Chriss órfão do glossário | Beckett |
| 012 | ⚠️ | Nelo+Tiago | IDs de ordem sem entrada no glossário | Nelo |
| 017 | 💡 | Kira | PSR órfão do glossário | Kira |

---

## 10. Decisão Bloqueio

**Algum 🔴 aberto?** Não.
**Block 1 (Project Identity) pode prosseguir?** Sim, desde que findings ⚠️ entrem em backlog de correção.
**Block 2 (Alpha Thesis) pode prosseguir?** Sim, porém recomenda-se corrigir findings 014 + 015 (Kira) ANTES — senão Kira entrará no Block 2 propondo teses que Mira potencialmente reprova por trades-only ou CV inadequado.

**Recomendação Sable:** antes de Block 2, priorizar correção de findings da Kira (014, 015, 016) + Nova (003, 004) por terem maior probabilidade de travar pipeline de pesquisa.

---

— Sable, o cético do squad 🔍
