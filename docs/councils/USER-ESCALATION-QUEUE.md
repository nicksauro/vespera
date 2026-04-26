# User Escalation Queue — Autonomous Session 2026-04-26+

**Purpose:** track decisions that mini-councils could not resolve in 1 round. User reviews on return.

**Rules:**
- Each entry = 1 unresolved decision
- Format: ID + date + scope + council attempted + divergence + recommended path
- Append-only — never delete; mark RESOLVED when user decides

---

## Active escalations

### ESC-001 — T002.0g coverage gap as_of=2024-06-30 (manifest pré-2024 ausente)

- **Date:** 2026-04-26 BRT
- **Scope:** T002.0g warmup state orchestrator — full 12-month run pre-condition
- **Trigger:** Dara T0 handshake BLOCK_GAP_UPSTREAM
- **Detail:**
  - Beckett T11 smoke retry needs as_of_dates `{2025-05-31, 2024-06-30}`
  - 2025-05-31: ✅ manifest cobre lookback 146bd → ~Nov 2024 (rows 11-18)
  - 2024-06-30: ❌ lookback 146bd → ~2023-12-22; `data/in_sample/year=2023/` vazio; manifest começa 2024-01-02
  - Faltam ≥dez/2023 (idealmente nov+dez/2023) no manifest
- **User constraint canonical (2026-04-26):** "todos os dados que tenho salvos são da DLL — não adianta nada baixarmos de novo"
- **Ambiguidade:** constraint cobre claramente RE-fetch de períodos JÁ materializados; é **ambíguo** sobre fetch INICIAL de períodos NUNCA materializados (2023-11/12)
- **Mini-council attempted:** Beckett + Pax + Sable + Morgan → 4/4 APPROVE_OPTION_B (restringir T11 set para {2025-05-31}; tech-debt 2024-06-30)
- **Council can resolve in 1 round:** SIM (Option B aplicada). Mas DECISÃO DE CONSTRAINT INTERPRETATION fica para user.
- **Recommended path (council):** Option B — restrict + tech-debt
- **Decisão necessária do user:**
  1. **Confirmar interpretação constraint:** "não baixar de novo" cobre fetch INICIAL de 2023-11/12, ou apenas RE-fetch?
  2. **Se cobre:** Aceitar smoke-only closure (T002.0g full deferred indefinitely; Phase E GO_EXECUTE bloqueado até constraint relaxar)
  3. **Se NÃO cobre:** Autorizar nova story MC-30-1 (data backfill 2023-11/12 sob protocol RA-20260428-1, ~3 sessões)
- **Status:** Council adotou Option B autonomamente per autonomous mandate; T002.0g prossegue com escopo restrito; user revisa no retorno.

---

## Resolved escalations

(none yet)
