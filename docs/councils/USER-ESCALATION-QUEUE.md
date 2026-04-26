# User Escalation Queue — Autonomous Session 2026-04-26+

**Purpose:** track decisions that mini-councils could not resolve in 1 round. User reviews on return.

**Rules:**
- Each entry = 1 unresolved decision
- Format: ID + date + scope + council attempted + divergence + recommended path
- Append-only — never delete; mark RESOLVED when user decides

---

## Active escalations

### ESC-002 — TimescaleDB hold-out window exposure (UNVERIFIED — Dara claims need re-audit)

- **Date:** 2026-04-26 BRT
- **Scope:** Custodial defense-in-depth (R10 hold-out invariant)
- **Trigger:** User reportou pós-2025/06 dados materializados; Dara empirical audit reportou
- **STATUS WARNING (added post-user correction):** Dara extrapolated 2023 chunks from 5 metadata rows; user CONFIRMED 2023 = 3 random days only (not Q4 continuous). **By extension, 2025-07+ chunks may also be sparse/random — Dara's "570 chunks 2023-2026" claim needs re-audit for continuity, not just metadata extent.** Findings below kept for record but TREAT AS UNVERIFIED.
- **Detail (per Dara — UNVERIFIED for continuity):**
  - Filesystem `data/in_sample/`: 2024-01..2025-06 (curado, manifest-pinned `78c9adb3...ee72`, intact) ← VERIFIED
  - TimescaleDB `sentinel-timescaledb` (container UP): chunks **range** 2023-01-02 → 2026-04-02 (570 chunks **across full range**) ← UNVERIFIED CONTINUITY
  - **Hold-out window [2025-07-01, 2026-04-21] presence em DB:** UNVERIFIED — could be sparse points, not continuous coverage
- **Riven static analysis verdict:** **LAYERED_SAFE — NO BREACH atual**
  - `assert_holdout_safe` chamado em 5 call-sites (feed_parquet, feed_timescale, warmup/orchestrator, run_cpcv_dry_run, run_warmup_state)
  - Manifest authoritative em parquet path (NO filesystem glob)
  - TimescaleDB queries usam `WHERE timestamp >= %s AND timestamp < %s` (caller-controlled)
  - R15 pin intact
- **Riven recommendation:** NÃO acionar kill-switch. Mas:
  - Dara recomenda DB-side `in_sample_*` guard view (RLS) para tornar leak structurally impossível
  - Story potencial: T002.0h "DB-side hold-out guard view + RLS migration"
  - Riven recomenda confirmar com Sable que CI gate G6 (`canonical-invariant.sums` verify) está ATIVO no pipeline (pin sem enforcement = decoração)
- **User decision necessária:**
  - Approve T002.0h (DB guard view) como PROACTIVE defense (~1.5 sessões)?
  - OR aceitar status quo defense-in-depth (5 call-sites + caller-discipline)?
- **Status:** UNVERIFIED — DB continuity re-audit pendente; Riven T8 dual-sign HOLD até reassessment; T002.0g Quinn PASS independente disso (orchestrator não usa DB).
- **Action:** Re-disparar Dara empirical com query `SELECT date_trunc('day', timestamp) AS d, COUNT(*) FROM trades GROUP BY d ORDER BY d` (NÃO via chunk metadata — direto na data) para CONFIRMAR continuidade real. Aguardar resultado antes de assumir LAYERED_SAFE rationale.

---

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

#### Update 2026-04-26 BRT post-Dara empirical audit (TimescaleDB inspection)

- **Dara reportou chunks 2023-01-02 → 2026-04-02** (570 chunks na tabela `trades`)
- **Filesystem `year=2023/` continua vazio** (parquets não materializados)

#### Update 2026-04-26 BRT post-USER CORRECTION (CRITICAL)

> User: "sim eu acho q temos 3 dias de 2023 aleatorios, n podemos usar isso pra nada"

- **Dara claim REFUTADA pelo user** — chunks 2023 NÃO são contínuos. São ~3 dias aleatórios (provavelmente artifacts de imports antigos), inutilizáveis para warmup compute.
- **Dara extrapolou de 5 chunks de metadata** (`_hyper_1_1222_chunk` até `_hyper_1_1228_chunk`, range 2023-01-02..2023-01-06) sem auditar continuidade — premise error.
- **Reframing CANCELADO:**
  - **Option (a) RE-FETCH DLL** — INVÁLIDO (user constraint canonical)
  - **Option (a-bis) DB→parquet materialize 2023-Q4** — INVÁLIDO (dados não existem; user CONFIRMADO)
  - **Option (b) RESTRICTED T11 set {2025-05-31}** — ÚNICA opção viável; já implementada em AC5 amendment
- **Status final ESC-001:** as_of=2024-06-30 **DEFINITIVAMENTE bloqueado** sem ação humana extraordinária. Smoke-only closure de T002.0g é o estado terminal salvo nova decisão user.
- **Implicação Phase E:** full 12-month CPCV run pre-condition é warmup state com 126bd lookback retroativo. Sem dados pré-2024 contínuos, in_sample window precisa começar pelo menos 6 meses depois de 2024-01 = **2024-07 ainda OK** (lookback até ~2024-01) MAS perde-se 6 meses de in-sample (12 → 6 meses). Mira/Beckett/Morgan precisam reavaliar viabilidade Phase E com window encurtada.
- **Nova decisão user pendente:**
  - Aceitar Phase E com in_sample window 2024-07..2025-06 → window de teste = 6 meses (Jan-Jun 2024 vira warmup)
  - OR adiar Phase E até backfill DLL inicial 2023-Q4 (viola constraint atual)
  - OR aceitar smoke-only Phase E preliminar (insuficiente estatisticamente per Morgan)

---

## Resolved escalations

(none yet)
