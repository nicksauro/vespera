# User Escalation Queue — Autonomous Session 2026-04-26+

**Purpose:** track decisions that mini-councils could not resolve in 1 round. User reviews on return.

**Rules:**
- Each entry = 1 unresolved decision
- Format: ID + date + scope + council attempted + divergence + recommended path
- Append-only — never delete; mark RESOLVED when user decides

---

## Active escalations

### ESC-002 — TimescaleDB hold-out window exposure (high-priority informational)

- **Date:** 2026-04-26 BRT
- **Scope:** Custodial defense-in-depth (R10 hold-out invariant)
- **Trigger:** User reportou pós-2025/06 dados materializados; Dara empirical audit confirmou
- **Detail:**
  - Filesystem `data/in_sample/`: 2024-01..2025-06 (curado, manifest-pinned `78c9adb3...ee72`, intact)
  - TimescaleDB `sentinel-timescaledb` (container UP): chunks **2023-01-02 → 2026-04-02** (570 chunks)
  - **Hold-out window [2025-07-01, 2026-04-21] está integralmente em DB** (Jul 2025 → Apr 2026 chunks)
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
- **Status:** Informational — não bloqueia T002.0g closure (Quinn PASS); tracked para usuário decidir prioridade.

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

- **TimescaleDB tem chunks 2023-01-02 → 2026-04-02** (570 chunks na tabela `trades`)
- **Filesystem `year=2023/` continua vazio** (parquets não materializados)
- Para satisfazer as_of=2024-06-30 lookback até ~2023-12-22, dados ESTÃO disponíveis em DB
- **Reframing da decisão (per nova evidência):**
  - Option (a) original "RE-FETCH DLL para 2023-11/12" = INVÁLIDO (user constraint)
  - **Option (a-bis) NEW:** "MATERIALIZE DB → parquet para 2023-11/12" — dados JÁ estão em DB local; NÃO é "baixar de novo"; é leitura de DB+pyarrow.write_parquet. Estimate: ~1 sessão (story T002.0h-bis).
  - **Option (b) RESTRICTED T11 set:** mantém-se atual (já implementado em AC5 amendment)
- **User decision necessária:**
  - Confirma que "não baixar de novo" NÃO bloqueia DB→parquet materialization?
  - Se SIM: approve story T002.0h-bis "Materialize 2023-Q4 from TimescaleDB to parquet" → desbloqueia full 12-month run
  - Se NÃO: aceitar smoke-only closure permanente; full requires retroactive permission
- **Council reluctant to autonomously decide this** — interpretação de constraint ambígua, escalation legítima.

---

## Resolved escalations

(none yet)
