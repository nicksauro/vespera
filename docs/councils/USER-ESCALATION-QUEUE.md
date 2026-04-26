# User Escalation Queue — Autonomous Session 2026-04-26+

**Purpose:** track decisions that mini-councils could not resolve in 1 round. User reviews on return.

**Rules:**
- Each entry = 1 unresolved decision
- Format: ID + date + scope + council attempted + divergence + recommended path
- Append-only — never delete; mark RESOLVED when user decides

---

## Active escalations

### ESC-002 — TimescaleDB hold-out window exposure (ESCALATED → NEEDS_DB_GUARD)

**Update 2026-04-26 BRT — Dara attempt 3 audit (Docker survived):**
- Q1 chunks per year empirical:
  - 2023: 6 chunks (Jan 2-6 + Jan 9) — user's "~3 random days" PARTIALLY CONFIRMED, actual is 6 consecutive trading days, ~720MB total. Operational conclusion ("unusable") STANDS.
  - 2024: 251 chunks (Jan 2 → Dec 31) — DENSE
  - 2025: 250 chunks (Jan 2 → Dec 31) — DENSE
  - 2026: 63 chunks (Jan 2 → Apr 3) — DENSE
- Q3 hold-out window (2025-07-01 → 2026-04-22): **AMBIGUOUS RED FLAG**
  - 100+ chunks metadata exist
  - **All chunks report `pg_relation_size = 0 bytes`**
  - Two hypotheses:
    (i) Chunks compressed (heap empty, data in compressed segments)
    (ii) Genuinely empty (metadata only, no actual rows)
  - NOT verified empirically in this attempt
- **ESC-002 verdict ESCALATED:** NEEDS_DB_GUARD
  - LAYERED_SAFE at L1 (5 fail-closed call-sites) + L2 (CI gate) — CONFIRMED
  - L3 operational claim "DB has hold-out data": NOT empirically confirmed (zero-byte chunks RED FLAG)
  - DB-side guard view JUSTIFIED before any CPCV dry-run that involves DB queries
- **Follow-up needed:** ONE defensive query against `chunk_compression_stats` to disambiguate compressed-with-data vs genuinely empty. (Dispatching Dara now.)

#### Update 2026-04-26 BRT — Dara §4 + Riven mini-council finalization

- **Dara §4 confirmed:** 23/23 hold-out trades chunks `is_compressed=true`; trades hypertable 53 GB total payload. `pg_relation_size=0` is canonical TimescaleDB compressed-chunk signature. **Hold-out window CONTAINS real data (compressed).**
- **Riven mini-council Q2 verdict:** **ESC-002_LAYERED_SAFE_SUFFICIENT_NO_NEW_STORY**
  - L1 (5 fail-closed `assert_holdout_safe` call-sites + Guard #1 silent-fallback removal) — CONFIRMED
  - L2 (CI gate active-blocking + enforce_admins=true) — CONFIRMED
  - L3 (DB density confirmed by Dara §4) — present + protected by L1+L2
  - DB-side guard view (potential T002.0i) JUSTIFIED as proactive defense BUT NOT prerequisite
  - T002.0g orchestrator never queries DB (parquet primary, AC1)
- **ESC-002 status: CLOSEABLE — defense-in-depth empirically validated. No new story T002.0i required for safety; only as future hardening if user prefers belt-and-suspenders.**

---

### ESC-003 — T002.0g orchestrator memory-budget gap (NEW, real T11.bis blocker)

- **Date:** 2026-04-26 BRT
- **Scope:** T002.0g warmup state orchestrator runtime/perf
- **Trigger:** Beckett T11.bis HALT 2026-04-26 BRT — RSS 1.95→4.10→6.09 GB em 90s, SIGTERM kill em 120s, exit 124, 0 JSONs persisted
- **Root cause (Aria + Dex confirmed):** `orchestrator.py:640-642` (`_aggregate_daily_with_close_at`) feeds `:334-336` (`buckets.setdefault(day, []).append(tr)`) — retains ALL Trade objects per day for full 146bd window before aggregating. 365d × ~850k trades/day × ~120B/Trade ≈ 3.7 GB residente.
- **Riven HOLD condition #1 RETRACTED:** "depends on Docker engine restoration" — INCORRECT; T002.0g orchestrator parquet-only, zero Docker dep. Real blocker is design.
- **Mini-council 5/5 CONVERGENT:** APPROVE_OPTION_A_NEW_STORY_T002.0h (streaming aggregation patch)
  - Aria: per-day chunked outer loop, builder API stays pure, R15 forbids amend Done T002.0g
  - Mira: ANTI_LEAK_PRESERVED_UNDER_CHUNKED conditional on (a) ascending iteration, (b) deques 20/126 reusing batch API, (c) Quinn fixture n_days≥127
  - Dex: ~150 LoC fix scope, ~1 session 8h estimate, builder API NO change, spec UNTOUCHED
  - Riven: T002.0h DoD MUST include real-scale memory regression test + ADR-1 v3 CAP_v3 explicit compliance
  - Beckett: smaller smoke window first + repeat per revision + Quinn fixture upgrade > Beckett pre-merge gate
- **Action items:**
  1. River drafte T002.0h (Wave W6 sequential post-T002.0g)
  2. Pax validate
  3. Dex impl (~1 session)
  4. Quinn re-QA with real-scale fixture
  5. Beckett T11.bis re-run as exit gate
  6. Article IV explicit AC: "Dex MUST NOT extend timeout, raise cap, or subsample to mask bug"
- **Status:** Council adopted Option A autonomously per autonomous mandate; River drafting now.

---

### ESC-006 — T002.0h Option B ALSO insufficient + worse (root cost is pyarrow Python materialization, structural)

- **Date:** 2026-04-26 BRT (post Dex Option B empirical)
- **Scope:** T002.0h wall-time mitigation — STRUCTURAL FINDING
- **Trigger:** Dex Option B implementation complete (Mira golden equivalence PASS, ESC-005 fix verified, R15-clean) — empirical wall-time **WORSE**: 444s (7m25s) vs Option C 382s (6m22s); peak RSS 3.49 GiB vs Option C 120 MB
- **Aria hypothesis empirically REFUTED:** per-month batching does NOT amortize root cost
- **Root cause:** per-row-group I/O + Python materialization in pyarrow (`to_numpy.tolist + map(Trade)`), NOT file open overhead. Cache (Option C) helps metadata 18:1 but cannot eliminate per-row-group; per-month (Option B) trades memory for time INEFFICIENTLY.
- **Dex HALT-ESCALATE per task spec** (> 180s threshold absolute exceeded by 2.5×). Article IV strict: NÃO improvisou, NÃO pursued Option E sem mini-council.
- **3 mitigation options remaining:**
  - **(E) Numpy-direct adapter** — bypass `to_numpy.tolist + map(Trade)` Python materialization in `feed_parquet._iter_parquet_rows`. Adapter modification (T002.0b touch). R15 question (story Done). Aria + Dara cosign required. ~3-4h Dex + R15 amendment overhead.
  - **(F) Relax AC8 threshold strategically** — warmup is run-once-per-as_of with cached outputs. Beckett's < 60s budget assumed dev-loop iteration. Reframe as one-time cost: 5-7min acceptable IF cached and rare. AC8 → "warmup wall-time NOT a smoke gate criterion; smoke total < 5min applies only to CPCV simulation post-warmup."
  - **(G) Hybrid C + E** — per-day streaming (Option C memory profile 120 MB) + numpy-direct (Option E CPU profile). Combines best of both. Adapter touch still required.
- **Mini-council convocado:** Aria + Mira + Beckett + Dara (Dara needed for adapter Option E sign-off)
- **Status:** HALT-ESCALATE_USER per task spec — autonomous mode dispatching mini-council; if convergent → execute; if divergent → user reviews on return
- **Decisions for user (if council can't converge):**
  1. Approve Option E adapter R15 amend (T002.0b reopen)?
  2. Approve Option F AC8 strategic relax (accept warmup as one-time-per-as_of cost)?
  3. Approve Option G hybrid (E + per-day streaming)?

---

### ESC-004 — T002.0h Option C insufficient (wall-time 6m22s vs amended < 60s budget)

- **Date:** 2026-04-26 BRT
- **Scope:** T002.0h streaming refactor wall-time mitigation
- **Trigger:** Dex empirical run post Option C (cached ParquetFile handles) — 6m22s, exit 0 (clean InsufficientCoverage HALT)
- **Cache effectiveness empirically validated:** 138 hits + 8 misses (94%, 18:1 metadata amortization) — helped MAS NÃO eliminate per-row-group I/O
- **Root cause:** Per-day row-group reads + Python materialization (`pf.read_row_group` + `to_numpy.tolist` + `map(Trade)`) AC2-bounded. Cache amortizes metadata only.
- **Mini-council consensus** (pre-empirical) escolheu Option C como "least invasive first" with Option B as fallback. Empirical proved C insufficient.
- **Three mitigation options surfaced:**
  - **(B) Per-month outer loop** — orchestrator chunks ~21 days into single ParquetFile open per month, internal per-day bucket. Mira sign-off REQUIRED (AC2 literal interpretation amend). Estimated ~4-5h Dex.
  - **(D) Calendar fix 2024-12-24** — SEPARATE concern, addresses InsufficientCoverage but NOT wall-time. Nova authority (B3 reduced-trading days).
  - **(E) Numpy-direct Trade construction** — adapter (T002.0b) modification, bypasses Python materialization. R15 question (T002.0b is Done). Estimated ~3-4h Dex + R15 amendment overhead.
- **Mini-council convocado:** Aria + Mira + Beckett + Nova (4 agents)
- **Status:** HALT-ESCALATE — autonomous mode dispatching mini-council to converge on B/D/E selection.

---

### ESC-005 — Calendar 2024-12-24 valid-sample-day assumption refuted (orthogonal to ESC-004)

- **Date:** 2026-04-26 BRT
- **Scope:** Calendar/data integrity — `config/calendar/2024-2027.yaml` (or similar)
- **Trigger:** Dex Option C empirical run revealed `2024-12-24` marked as valid sample day em calendar BUT parquet has 0 trades on that date
- **Empirical:** `days_with_trades=145 vs expected 146` for as_of=2025-05-31 lookback window — 2024-12-24 missing trades
- **Hypothesis:** B3 reduced-trading day (Christmas Eve early-close OR full holiday) not modeled in current calendar
- **Authority:** Nova (@market-microstructure, B3 trading day expertise)
- **Action:** Nova investigates whether 2024-12-24 should be excluded from valid sample days; if YES, Pax errata in calendar config; if calendar fix changes lookback window math, Mira anti-leak re-validation needed
- **Independent of ESC-004 wall-time:** This calendar fix solves InsufficientCoverage HALT specifically, NOT wall-time issue
- **Status:** PARTIALLY_RESOLVED (2026-04-26 BRT)
  - **Resolved:** Pax errata applied — `2024-12-24` added to `br_holidays` em `config/calendar/2024-2027.yaml` (treated as full-exclusion; `is_business_day()` → `is_valid_sample_day()` excludes via `br_holidays` membership). Calendar `version` bumped to `2026-04-26`. Inline YAML comment cita Nova confirmation + ESC-005.
  - **Schema gap (NOT auto-fixed):** Loader (`packages/t002_eod_unwind/warmup/calendar_loader.py`) only consumes `copom_meetings`/`br_holidays`/`wdo_expirations`/`pre_long_weekends_br_with_us_open`. NO `half_day` field, NO `excluded_from_lookback` flag. Adding such fields silently ignored — would require code change (out of scope for this errata; escalate as separate story).
  - **Open (tracked, NOT in scope):** Full B3 half-day audit (other historical Christmas Eves, Sextas pré-Carnaval que B3 fechou cedo, Ano Novo véspera, etc.) — recommend new story (e.g., `T002.0i` or governance audit) com Nova como owner para enriquecer schema com `half_day` + `excluded_from_lookback` + auditar 2024-2027.
  - **Dex Option B re-run unblocked:** lookback math agora exclui `2024-12-24`; `days_with_trades` esperado deve alinhar com calendar truth.


---

### ESC-002 — TimescaleDB hold-out window exposure (UNVERIFIED DB density / L2 CI gate CONFIRMED ACTIVE)

**Update 2026-04-26 BRT — Gage proxy empirical gh api check:**
- Branch protection main has 4 canonical-invariant jobs in `required_status_checks.contexts` ✓
- `enforce_admins=true`, `strict=true`, `allow_force_pushes=false`, `allow_deletions=false`, `required_conversation_resolution=true` ✓
- L2 CI gate G6 enforcement: **ACTIVE_BLOCKING_CONFIRMED** (Sable initial concern INVALIDATED)
- Riven LAYERED_SAFE rationale CONFIRMED at L2; only DB density (L3) remains UNVERIFIED
- R15.2 T6 was actually done previously, just unchecked in story; needs cosmetic `[x]` update + audit §8 evidence link
- Caveat noted: `required_approving_review_count=0` (single-author posture) — recommend documenting in ADR-5 or governance ledger
- **Sub-blocker for T002.0g T8 dual-sign on G6/CI aspect: CLOSED** (DB audit aspect still HOLD pending Docker)

---

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

#### Update 2026-04-26 BRT post-Dara re-audit (DOCKER_UNAVAILABLE)

- **Dara mea culpa registered:** prior "570 chunks continuous" claim was extrapolation from 5 metadata rows. RETRACTED.
- **Docker engine status:** DOCKER_UNAVAILABLE — `docker info` + `docker ps` return 500 from `dockerDesktopLinuxEngine` named pipe. Empirical DB audit BLOCKED.
- **2023 DB content:** UNVERIFIABLE from disk (no 2023 parquet). User claim "~3 random days" is authoritative until DB reachable.
- **2025-07+ DB content:** UNVERIFIABLE. Filesystem has ZERO hold-out parquets (strong signal hold-out never materialized to disk, but DB density unknown).
- **ESC-002 LAYERED_SAFE rationale RETRACTED** — was based on same metadata-extrapolation error. R10 defense (`assert_holdout_safe` + manifest pin) still blocks accidental reads, but does NOT prove hold-out density empirically.
- **Riven T8 dual-sign HOLD** until: (a) Docker engine restored AND DB continuity confirmed via SQL, OR (b) explicit user statement on hold-out content.
- **Action items (Dara final):**
  1. (@devops) Restore Docker Desktop Linux engine
  2. (Dara, post-restoration) Run 3 continuity queries → `docs/audits/AUDIT-20260426-DB-CONTINUITY.md`
  3. (PO/PM) Treat prior 570 chunks claim as RETRACTED — Article IV violation logged
  4. (Riven/T8) Hold ESC-002 progression
  5. (Dara) Lesson: chunk-metadata queries must be paired with `COUNT(DISTINCT date_trunc('day'))` before any continuity claim

#### Update 2026-04-26 BRT — Docker re-down (post user restart)

- User restarted Docker; `docker ps` initially showed container UP 19s.
- `docker exec` immediately failed with 500 on dockerDesktopLinuxEngine pipe.
- Postgres logs showed recovery + ready, query `SELECT ... GROUP BY year` ran in background but timed out (~10min) producing zero output.
- Dara second-attempt audit: `com.docker.service` (Windows) found STOPPED, all Docker API endpoints returning 500 across 1.53 + 1.47.
- Dara honored Article IV — aborted clean, no re-extrapolation, doc `docs/audits/AUDIT-20260426-DB-CONTINUITY.md` (status ABORTED — DOCKER_DAEMON_DOWN_500).
- ESC-001 + ESC-002 status UNCHANGED.
- T002.0g T8 Riven dual-sign + T10 Beckett T11.bis remain HOLD.
- Operational follow-up needed: `com.docker.service` restart on host before audit can proceed.

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
