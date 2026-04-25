# EPIC-T002.0 — T002 Phase E Infrastructure (CPCV Execution Readiness)

**Status:** Draft (awaiting handshakes)
**Owner (PM):** Morgan (@pm)
**Origem:** Beckett (@backtester) Phase E Readiness Audit — 2026-04-21 BRT
**Verdict raiz:** `HOLD_GAPS_TO_CLOSE` — 8 blockers primários + 2 soft gaps impedem CPCV run
**Source doc:** [docs/ml/plans/T002-phase-E-readiness-gaps.md](../ml/plans/T002-phase-E-readiness-gaps.md)
**Spec alvo:** [docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml](../ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml) (`sha256:4b5624ad…dc3fc`)
**PRR:** `PRR-20260421-1` co-signed by Pax (`c34c201c…79e5a`)
**Thesis:** [docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md](../research/thesis/T002-end-of-day-inventory-unwind-wdo.md) — K1..K4 pré-registrados

---

## 1. Epic goal

Entregar as 8 peças de infraestrutura que **desbloqueiam Task #36 (Beckett CPCV Gate / Fase E)** sobre a spec T002 v0.2.0. Este epic **não executa** Fase E — apenas habilita.

**Exit criterion (binário):**
- `pytest tests/contracts/` mantém 25/25 PASS
- Beckett roda `*run-cpcv --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run` e recebe verdict `GO_EXECUTE`
- Hold-out `2025-07-01 → 2026-04-21` **não foi lido** durante todo o epic (evidência: grep de acessos logados + audit de `VESPERA_UNLOCK_HOLDOUT` = `0` em toda a CI)

---

## 2. Background & escopo

### 2.1 Background
Spec v0.2.0 está ratificada (PRR-20260421-1 + Pax cosign). T002.1/2/3 já implementados (32/32 tests). Calendar static data OK. O que falta é a **camada de dados + CPCV + métricas + custódia**. Beckett recusa iniciar CPCV até os 8 blockers fecharem.

### 2.2 In-scope
- Infra de leitura de dados (TimescaleDB role, .env, adapter direto, materialização parquet, adapter mmap)
- Engine CPCV canônico (Lopez de Prado AFML Ch.12, purged + embargoed, N=10/k=2/45 paths)
- Módulo de métricas canônico (DSR, PBO, IC_spearman, bootstrap CI, sortino, MAR, ulcer, PF, hit_rate, sharpe distribution)
- Cost atlas canônico (brokerage + emolumentos + IR day-trade)

### 2.3 Out-of-scope
- ❌ Execução da Fase E em si (Task #36 — separada, destravada por este epic)
- ❌ Fase F paper-mode (T002.4+)
- ❌ Fase G live adapter
- ❌ Soft-gap #29 (simulator semver + engine-config.yaml): documentado como backlog, **não bloqueia este epic**
- ❌ Qualquer mudança na spec v0.2.0 (se surgir necessidade, escalar Mira para v0.3.0 com PRR-novo — este epic recusa edição da spec)

---

## 3. Success criteria (DoD do epic)

- [ ] T002.0a (Dara): `sentinel_ro` role criada + `.env.vespera` gitignored + `scripts/materialize_parquet.py` funcional + materialização in-sample completa com sha256 registrado
- [ ] T002.0b (Dex): `feed_timescale.py` + `feed_parquet.py` com contract tests verdes; hold-out lock via `VESPERA_UNLOCK_HOLDOUT` verificado fail-closed
- [ ] T002.0c (Dex + Mira): `packages/vespera_cpcv/` — purged combinatorial CV (N=10/k=2/45 paths, embargo=1), seed-determinístico, benchmark unit test reproduz valor conhecido
- [ ] T002.0d (Mira + Dex): `packages/vespera_metrics/` — DSR+PBO+IC_spearman+bootstrap 10k+sortino+MAR+ulcer+PF+hit_rate+sharpe_45paths, validado contra reference values
- [ ] T002.0e (Nova): `docs/backtest/nova-cost-atlas.yaml` com brokerage + emolumentos B3 + IR day-trade canônicos e fontes [WEB-CONFIRMED]
- [ ] Todas as 5 stories merged via Gage (R12); Quinn PASS em todas; Sable coherence audit no epic todo
- [ ] Beckett re-executa `*mira-handshake` contra v0.2.0 e confirma dry-run `GO_EXECUTE`

---

## 4. Stories plan

**Unidade:** sessão de trabalho squad (1-4h humano↔squad).

| Story | Título | Owner primário | Consultores | QA | Estimate | Depends on |
|-------|--------|----------------|-------------|-----|----------|-----------|
| **T002.0a** | Custodial + materialização parquet | Dara (@data-engineer) | Riven (custodial R10), Nelo (schema DLL side), Sable (hash protocol) | Quinn | 1 sessão | — |
| **T002.0b** | Data adapters (Timescale + Parquet) | Dex (@dev) | Aria (contract), Beckett (perf), Dara (SQL) | Quinn | 1 sessão | T002.0a |
| **T002.0c** | CPCV engine (purged + embargoed) | Dex (@dev) | Mira (algo spec), Beckett (interface p/ Fase E) | Quinn | 2 sessões | T002.0b |
| **T002.0d** | Metrics module (DSR/PBO/IC/etc) | Mira (@ml-researcher) spec + Dex impl | Beckett (consome), Kira (tese-metric alignment) | Quinn | 2 sessões | T002.0c (paralelizável se API ≥ esqueleto) |
| **T002.0e** | Nova cost atlas canônico | Nova (@market-microstructure) | Beckett (consome em backtest), Sable (fonte audit) | Quinn | 0.5 sessão | — (paralelo) |

**Total:** ~6.5 sessões. **Paralelizável:** T002.0a + T002.0e desde T0. T002.0b após 0a. T002.0c após 0b. T002.0d pode começar em paralelo com 0c se Mira define API primeiro.

---

## 5. Sequencing (Gantt ASCII)

```
Session 1 ─┬─ T002.0a (Dara+Riven) ───────────────┐
           └─ T002.0e (Nova atlas)  ─── done      │
                                                  │
Session 2 ──── T002.0b (Dex, adapters)  ──────────┤
                                                  │
Session 3 ─┬─ T002.0c begin (Dex+Mira, CPCV) ─┐   │
           └─ T002.0d spec (Mira API design) ─┘   │
                                                  │
Session 4 ──── T002.0c cont. ─── T002.0d impl ────┤
                                                  │
Session 5 ──── T002.0d close + Quinn + Sable ─────┤
                                                  │
  Sync point ─────────────────────────────────────┘
  └─► Beckett *run-cpcv --dry-run → GO_EXECUTE
      └─► Task #36 destravada → Fase E inicia
```

Paralelismo real: T002.0a + T002.0e rodam juntas; T002.0d spec pode ir adiante enquanto 0c implementa engine.

---

## 6. Handshakes required (pré-start)

Cada story precisa do handshake do agente abaixo **antes** de sair de Draft:

| Story | Handshake required (sign-off na story) |
|-------|---------------------------------------|
| T002.0a | **Dara** (schema + role scope) + **Riven** (custodial R10 aprovou read-only + .env scheme) |
| T002.0b | **Aria** (contract de adapters) + **Beckett** (perf budget parquet mmap ≤ 4.5 min por replay) |
| T002.0c | **Mira** (config CPCV N=10/k=2/45 paths/embargo=1 alinhado com spec) + **Beckett** (interface consumível por `*run-cpcv`) |
| T002.0d | **Mira** (fórmulas DSR/PBO/IC corretas vs spec metrics_required L159-172) + **Beckett** (shape dos outputs consumível no relatório) |
| T002.0e | **Nova** (fontes canônicas + [WEB-CONFIRMED] tags) + **Beckett** (formato consumível em `engine-config.yaml`) |
| **Epic (este doc)** | **Beckett** assina que a ordem + DoD alinham com o readiness audit 2026-04-21 |

> Morgan (@pm) **lista** estes handshakes; a execução dos sign-offs fica com @sm (draft fino) + agentes respectivos antes de cada story mover para Pax validation.

---

## 7. Constraints (epic-wide invariants)

### 7.1 Hold-out intocado (R1 + R15(d))
Qualquer story que toque data path **DEVE** incluir AC explícito:
> "Leitura de qualquer timestamp ∈ `[2025-07-01, 2026-04-21]` requer `VESPERA_UNLOCK_HOLDOUT=1` e é **fail-closed** por default. Contract test prova o bloqueio."

### 7.2 R15 + Não-retroatividade
Stories criadas neste epic são **fluxo normal de desenvolvimento** — **não** precisam de `preregistration_revisions[]`. A spec T002 v0.2.0 é **imutável** durante este epic. Se qualquer story descobrir necessidade de mudança funcional na spec, **pare e escale Mira** para emitir v0.3.0 com PRR-novo — o epic é blocking-but-recoverable nesse caso.

### 7.3 R12 — Gage monopolista de push
Nenhuma story deste epic executa `git push` / `gh pr create`. Todo merge passa por @devops (Gage).

### 7.4 Soft gaps explicitamente deferidos
- Custos ambíguos (#21-23 do readiness) são tratados em T002.0e. Enquanto T002.0e não fecha, Beckett wire `[TO-VERIFY]` defaults (R$0.25 brokerage, R$0.35 fees, IR não aplicado) — aceitável para CPCV dry-run + exploratório; blocker apenas para GO/NO-GO final.
- Reprodutibilidade stamps (#29) ficam para epic separado pós-Fase-E.

**Beckett commitment:** o relatório CPCV dry-run produzido ao fim deste epic anexará bloco `[TO-VERIFY]` explícito listando as **3 categorias de reprodutibilidade/dados diferidas**:

1. **Cost atlas ausente ou parcial** (se T002.0e atrasar além do dry-run) — defaults `[TO-VERIFY]` brokerage/fees/IR em uso.
2. **`simulator_version` semver não-tagged** (gap #29) — sem identificador de versão do simulador amarrado ao resultado.
3. **`docs/backtest/engine-config.yaml` hash não-computado** (gap #29) — configuração do engine não selada por sha256.

Essa anotação garante que o dry-run **NUNCA** seja interpretado como GO/NO-GO final — qualquer decisão Fase-F (paper-mode) exige **fechamento explícito dos itens `[TO-VERIFY]`**, idealmente via epic subsequente T002.0.2 (reprodutibilidade + cost atlas closure).

---

## 8. Dependencies e risk register

| Dependência | Risco | Mitigação |
|-------------|-------|-----------|
| `sentinel-timescaledb` Docker UP | Container pode cair | Healthcheck em T002.0a; parquet materializado é o caminho quente (Docker down ≠ blocker após 0a/0b) |
| Cobertura WDO 2024-01→2025-06 in-sample (spec L93) | Gaps no DB | T002.0a registra manifest.csv com sha256 por mês — gaps visíveis antes de CPCV |
| CPCV correctness (Lopez de Prado Ch.12) | Bug sutil em purging/embargo → PBO falso | Unit test de T002.0c reproduz benchmark numérico conhecido (referência AFML Ch.12 §12.4) |
| DSR / PBO numerical correctness | Valores errados matam ou falsos-positivam tese | T002.0d valida contra reference implementation (Bailey-Lopez de Prado 2014 toy example) |
| Nova cost atlas atrasa | Soft gap — não bloqueia dry-run | Beckett usa defaults com `[TO-VERIFY]` tags; T002.0e pode rodar em paralelo |
| Mudança de spec durante epic | Quebra ratificação | Epic **recusa** edição da spec; escala Mira se necessário (v0.3.0 + PRR-novo) |

---

## 9. Gate signature — Epic → Stories active

```yaml
gate_epic_T002_0:
  verdict: PENDING
  requires:
    - dara_handshake: T002.0a schema+role
    - riven_handshake: T002.0a custodial R10
    - aria_handshake: T002.0b adapter contract
    - mira_handshake: T002.0c CPCV + T002.0d metrics
    - nova_handshake: T002.0e cost atlas
    - beckett_handshake: epic-wide (order + DoD)
  signed_by: Morgan (@pm) + Pax (@po) — pending
  signed_at_brt: pending
  spec_ref: docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml
  spec_sha256: "4b5624ad6ba151c57e263f1d160d7e802354c5e164f777198755b70c59bdc3fc"
  prr_ref: PRR-20260421-1
  readiness_audit_ref: docs/ml/plans/T002-phase-E-readiness-gaps.md
  next_action: "Collect 6 handshakes → Pax *validate-story-draft por story → @sm *draft detalhado"
  unblocks: "Task #36 (Beckett CPCV Gate / Fase E)"
```

---

## 10. Execution plan companion

Sequenciamento operacional detalhado em: [docs/prd/EPIC-T002.0-EXECUTION.yaml](./EPIC-T002.0-EXECUTION.yaml)

---

**Assinatura:** Morgan (@pm) — 2026-04-21 BRT
**Status:** Draft, awaiting 6 handshakes listed in §6
