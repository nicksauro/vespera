# MANIFEST_CHANGES — Histórico Append-Only

> Histórico formal de mudanças governadas pelo protocolo de `MANIFEST.md § Governança do MANIFEST`. Append-only: nenhuma entrada é editada ou removida após ratificação. Correções posteriores entram como nova entrada com `corrects: {revision_id}`.

---

## MCP-20260421-R15 — Adição de cláusula R15 (Semver em major==0)

- **Proposta por:** Mira (`@ml-researcher`)
- **Data deliberação:** 2026-04-21 BRT
- **Origem:** Auditoria Sable (`@squad-auditor`) sobre plano de Mira para re-emitir spec T002 como v0.2.0 com in_sample shift de 2024-01-01 → 2024-07-01 e P252→P126. Sable apontou que o bump era breaking e não ritualmente minor; Mira contra-propôs reconhecer major==0 como fase de desenvolvimento inicial com permissão explícita para breaking minor + trilha auditável. Sable aceitou com 3 condições. Pax apontou falta de ownership do MANIFEST. Orion (`@aiox-master`) organizou deliberação coletiva.

### Cláusula ratificada

> **R15. Semver em fase major==0 — minor pode ser breaking, com trilha auditável**
>
> Durante fase de desenvolvimento inicial (major == 0 no semver da spec ML), incrementos minor (0.X.0 → 0.Y.0) PODEM introduzir mudanças não-retrocompatíveis em specs ML, desde que TODAS as condições abaixo sejam satisfeitas:
> - (a) Revisão registrada em `preregistration_revisions[]` append-only na spec, com schema formalizado
> - (b) Co-assinatura de Pax (`@po`) no ADR da revisão
> - (c) Justificativa ancorada em constraint de dados descoberto, NÃO em otimização de resultado
> - (d) Hold-out virgem permanece intocado
>
> Após o primeiro major bump (1.0.0), semver 2.0.0 padrão volta a valer.

Texto integral e schema de `preregistration_revisions[]` em `MANIFEST.md § 15`.

### Afetados deliberantes (mapeados por Pax)

| Agente | Por que é afetado |
|--------|------------------|
| Mira (`@ml-researcher`) | Produtora de specs ML — R15 rege o ritmo dela |
| Beckett (`@backtester`) | Consumidor de specs — precisa saber o que "minor" significa para re-execução CPCV |
| Dex (`@dev`) | Consumidor de specs — implementa features; quebras afetam código |
| Quinn (`@qa`) | Audita specs via contract tests — precisa saber o que testar |
| Pax (`@po`) | Co-assinante obrigatória de cada revisão + editor do MANIFEST |

**Não afetados:** Nelo (`@profitdll-specialist`), Nova (`@market-microstructure`) — não produzem nem consomem specs ML.
**Observadores:** Riven (`@risk-manager`), Tiago (`@execution-trader`) — afetados indiretamente.
**Não-votante:** Sable (`@squad-auditor`) — emite parecer técnico (conflito de interesse: audita MANIFEST).

### Votos (registro formal)

| Agente | Voto | Razão |
|--------|------|-------|
| Mira | **ACCEPT** | Cláusula codifica proposta original com as 3 salvaguardas de Sable. Condição (c) é a mais importante — previne p-hacking disfarçado. Aceita inclusive (d) hold-out intocado, redundante com R1 mas explícito para evitar ambiguidade. |
| Beckett | **ACCEPT (com condição incorporada)** | Exigiu que `preregistration_revisions[]` contenha campo `breaking_fields[]` listando exatamente o que mudou — sem isso, não sabe se re-executa CPCV do zero. Campo incorporado ao schema. |
| Dex | **ACCEPT** | Em fase major==0 retrabalho é esperado — é o que SemVer 2.0.0 §4 define. Condição (a) dá changelog estruturado para saber o que tocar. Sem R15, major bump a cada ajuste de data criaria ruído semântico inútil. |
| Quinn | **ACCEPT (com requisito técnico)** | Contract test `test_spec_version_gate.py` muda de forma: valida que SE breaking change detectado E major==0 ENTÃO `preregistration_revisions[]` tem entrada nova com campos (a)(b)(c) populados. Testável determinístico — implementável em CI. |
| Pax | **ACCEPT** | Aceita o ônus de co-assinatura — é exatamente o freio que PO deve oferecer em pré-registrações. Incorpora as condições de Beckett e Quinn como melhorias de schema, não como novas cláusulas. |

**Resultado:** 5/5 ACCEPT — unanimidade. Override de Guardião não necessário.

### Parecer técnico — Sable

1. **Quórum válido:** 5/5 deliberantes ACCEPT (2 com condições técnicas incorporadas por Pax).
2. **Auditabilidade:** As 4 condições (a)(b)(c)(d) são objetivas e verificáveis via arquivos versionados. Condição (c) é subjetiva mas mitigada por `preregistration_revisions[].data_constraint_evidence`, auditável post-hoc.
3. **Adendo 1 (incorporado):** schema de `preregistration_revisions[]` formalizado ANTES da primeira aplicação, com campos mínimos `revision_id, timestamp_brt, from_version, to_version, breaking_fields[], justification, data_constraint_evidence, pax_cosign_hash`.
4. **Adendo 2 (incorporado):** contract test em CI ANTES de Mira emitir v0.2.0. Gate temporal explícito.
5. **Não-retroatividade:** R15 aplica-se a bumps futuros. v0.1.0 → v0.2.0 será o primeiro caso.

**Verdict:** `QUÓRUM_VÁLIDO` — nenhuma violação de processo detectada.

### Ratificação do Guardião

- **Guardião:** Usuário
- **Data:** 2026-04-21
- **Decisão:** `SIM` — aprovado modelo de ownership, protocolo de 8 passos, mapa de afetados, e cláusula R15 com adendos Sable incorporados.

### Execução (sequência)

1. ✅ Pax edita `MANIFEST.md` — preâmbulo de Governança + R15 + schema de `preregistration_revisions[]` (task #40)
2. ✅ Pax cria `MANIFEST_CHANGES.md` — esta ata (task #41)
3. ⏳ Pax formaliza schema (já transcrito no MANIFEST § 15 — task #42 praticamente completa junto com #40)
4. ⏳ Quinn implementa `tests/contracts/test_spec_version_gate.py` (task #43)
5. ⏳ Mira edita spec T002 v0.2.0 com primeira entrada `preregistration_revisions[]` (task #44)
6. ⏳ Sable re-audita findings 001/002/005 (task #45)
7. ⏳ Task #36 (Beckett CPCV Phase E) destravada

### Referências

- `MANIFEST.md § Governança do MANIFEST` — ownership + protocolo
- `MANIFEST.md § 15` — cláusula + schema
- Council doc: `docs/councils/VESPERA-DATA-PIPELINE-2026-04-21.md`
- Spec alvo: `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.1.0.yaml` → v0.2.0

---

*Arquivo append-only. Próxima entrada será `MCP-YYYYMMDD-{id}` no fim do arquivo.*
