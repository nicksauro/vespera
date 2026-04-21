# EPIC-T001 — Bar-Close Momentum WDO 5-min

**Owner:** Morgan (@pm)
**Status:** DRY-RUN (smoke-test Q-SDC Fase C)
**Thesis ref:** docs/research/thesis/T001-bar-close-momentum-wdo-5min.md
**Architecture ref:** docs/architecture/T001-bar-close-momentum-design.md

---

## Business goal
Validar empiricamente se momentum 5-min em WDO tem IC ≥ 0.03 pós-Bonferroni em 45 paths CPCV, como primeira iteração de alpha capturável pelo squad quant sob trades-only.

## Stories candidatas

| Story ID | Título | Estimate |
|----------|--------|----------|
| T001.1 | Implementar bar_aggregator + session_filter + testes | 2 dias |
| T001.2 | Implementar features.mom_3bar + labels.regression + testes | 1 dia |
| T001.3 | Integrar pipeline ao Beckett runner (consumer do spec YAML) | 1 dia |
| T001.4 | Rodar CPCV + DSR + PBO + stress regimes → backtest doc | 2 dias (Fase E) |

(Dry-run vai exercer T001.1 apenas; T001.2-4 são escopo futuro se tese real for adotada.)

## Acceptance criteria (Epic-level)

- AC1: Pipeline end-to-end roda sobre 12 meses de WDOFUT sem erro
- AC2: Nenhum valor UTC aparece em qualquer estágio do pipeline (R2)
- AC3: Todos os números em CPCV result doc são [WEB-CONFIRMED] ou [TO-VERIFY] explícitos (R1)
- AC4: Feature é marcada `historical_availability=computable` no spec YAML
- AC5: Backtest respeita fill rules trades-only Beckett (R7)

## Dependencies

- Dataset `D:\sentinel_data\historical\` WDO 2023-2026 acessível
- Beckett *run-cpcv funcional
- Mira spec YAML assinada

## Risk assessment

| Fase | Risco |
|------|-------|
| D (implementação) | Leakage em agregação — mitigado por teste unitário |
| E (CPCV gate) | DSR pode vir < 0 → descartar T001 e recomeçar (esperado para smoke-test) |
| F (paper-mode) | N/A para dry-run |
