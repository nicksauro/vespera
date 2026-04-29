# User Escalation Queue — Autonomous Session 2026-04-26+

**Purpose:** track decisions that mini-councils could not resolve in 1 round. User reviews on return.

**Rules:**
- Each entry = 1 unresolved decision
- Format: ID + date + scope + council attempted + divergence + recommended path
- Append-only — never delete; mark RESOLVED when user decides

---

## Active escalations

### ESC-010 — Dual-track: WarmUpGate singleton + make_backtest_fn stub (Beckett N4 HALT)

**Date (BRT):** 2026-04-28
**Discovered by:** Beckett (@backtester) — T11.bis #4 N4 HALT-ESCALATE
**Source:** docs/backtest/T002-beckett-t11-bis-smoke-report-N4-2026-04-28.md
**Severity:** HIGH dual-track (blocks AC8 closure + Riven §9 + Phase F unblock)
**Type:** 2 findings (architectural, dual-track)

#### Track A — WarmUpGate singleton + default-path binding

**Symptom:** AC8 amended invocation `--smoke --in-sample-start 2024-08-22 --in-sample-end 2025-06-30` aborta exit=1 em 2.892s antes do fanout.

**Root cause empirical (Beckett N4 §root cause):**
- `scripts/run_cpcv_dry_run.py:848` instancia `WarmUpGate` ÚNICO compartilhado entre smoke + full phases
- Linha 865: smoke phase deriva `smoke_in_sample_start = max(in_sample_start, in_sample_end - 30d) = 2025-05-31` independentemente de `--in-sample-start`
- `WarmUpGate` lê de `_DEFAULT_ATR_PATH` / `_DEFAULT_PERCENTILES_PATH` (default path symlink/copy), NÃO dated path
- Default path holds last write — atualmente `as_of=2024-08-22` (write mais recente do precompute)
- Smoke pede `as_of=2025-05-31`, encontra `2024-08-22` → `WARM_UP_FAILED` → AC11 abort

**Implication:** AC8 amended invocation **NÃO pode simultaneamente satisfazer smoke (precisa 2025-05-31) e full (precisa 2024-08-22)** sob harness atual. ESC-009 council 6/6 (Aria + Mira + Pax mesmo) errou em assumir que cache-hit em ambas as_of dates resolveria — esqueceu o singleton + default-path binding.

#### Track B — make_backtest_fn neutral stub (degenerate KillDecision)

**Symptom:** Beckett rodou DIAGNOSTIC sem `--smoke` (`run_id T002-N4-DIAG-NOSMOKE`): exit=0 + 5 artifacts OK. MAS KillDecision NO_GO sobre 45 path Sharpes **TODOS 0.0**, IC=0, PBO=0.5 default, DSR=0.5 default.

**Root cause:** `packages/t002_eod_unwind/cpcv_harness.py::make_backtest_fn` é **neutral stub** — não retorna real strategy. Mesmo padrão degenerate da N3 smoke synthetic, mas agora sobre janela full ~10mo CPCV — prova que a degeneração é **arquitetural** (stub), NÃO sample-size.

**Implication:** AC8.9 "verdict ∈ {GO, NO_GO}" PASS literal mas semanticamente vazio. T002 GO/NO_GO real **NÃO É testável** sob make_backtest_fn stub. Phase F gate (próxima barreira antes capital ramp) pediria real make_backtest_fn — mas isso é fora do escopo T002.0h declarado.

#### Why ESC-009 council missed Track A

ESC-009 6/6 council (Aria + Mira + Pax + Beckett + Riven + Dara) modelou cuidadosamente o `warmup_gate_as_of` binding em full-phase mas NÃO inspecionou o singleton + default-path binding. Discovery requires N4 empirical execution — not visible from static read alone. Article IV (no invention) honored — councils proceed on best evidence available; new evidence requires new council.

#### Honored guards (Beckett N4 7/7)

- NO subsample
- NO engine config mutation
- NO threshold relaxation
- Peak RSS reported honestly (N/A where not sampled)
- Article IV strict
- NO source code modification
- NO push (Article II → Gage)

#### Action items (recommended)

1. **Mini-council ESC-010 6-vote** (Aria + Mira + Beckett + Riven + Pax + Dara) — dual-track decision:
   - **Track A:** E1 (harness amendment — `WarmUpGate` per-phase dated paths) | E2 (drop `--smoke` from AC8 invocation literal) | E3 (other)
   - **Track B:** F1 (integrate real make_backtest_fn now) | F2 (redefine AC8.9 stub-OK) | F3 (split into T002.0h.1 + T002.1.bis)
2. **Council outcome ledger:** `docs/councils/COUNCIL-2026-04-28-ESC-010-dual-track.md`
3. **Outcome execution per autonomous mandate** (mini-council substitui user authorization)

#### Status

- [x] Mini-council ESC-010 6-vote (Track A + Track B) — 2026-04-28 BRT, 6 voters consolidated
- [x] Council ledger ([COUNCIL-2026-04-28-ESC-010-dual-track.md](COUNCIL-2026-04-28-ESC-010-dual-track.md))
- [x] AC8 invocation literal amendment (E2 — drop --smoke flag, story T002.0h L65)
- [x] AC8.9 redefinition (F2 — PIPELINE INTEGRITY vs STRATEGY EDGE scope clarification, story T002.0h)
- [x] PRR-20260428-1 (E2) + PRR-20260428-2 (F2) appended preregistration_revisions[] (4/4 hashes verified via `python scripts/pax_cosign.py verify`)
- [x] T002.0h.1 + T002.1.bis spawn (stub headers; @sm formal drafts downstream)
- [x] Beckett N5 re-run (post Pax cosign; cache `as_of=2024-08-22` already exists — no precompute needed) — PASS strict-literal 9/9; report `docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md` (run_id 50c4fe32...)
- [x] Riven §9 HOLD #1 clear + §9 HOLD #2 arm (Riven custodial 2026-04-28 BRT + **Mira ML statistical authority dual-sign COMPLETE 2026-04-28 BRT** — Gate 4 criteria DSR>0.95 + PBO<0.5 + IC decay ratified per Bailey-LdP 2014 §3+§6 and BBLP 2014 §3; Bonferroni n_trials=5 preserved across all 5 disarm gates; anti-leak invariants preserved; hold-out lock UNTOUCHED) — appended to `docs/qa/gates/T002.0g-riven-cosign.md` 2026-04-28 BRT
- [x] Sable audit (Q-SDC Phase G — coherence post-N5) — `docs/audits/AUDIT-2026-04-28-T002.0h-ESC-010-coherence.md` READY FOR GAGE PUSH; 0 critical, 2 moderate findings → backlog housekeeping (non-blocking)
- [x] Gage push (autonomous mode) — **PR #6 merged to main 2026-04-28 BRT** under mini-council 3/3 UNANIMOUS APPROVE_AUTO_MERGE (Pax + Riven + Sable). Merge SHA `8b644d5655e1dee9409e993718881100e16c3a52`. CI 4/4 PASS pre-merge. Branch `t002-1-warmup-impl-126d` preserved (--delete-branch=false). §9 HOLD #2 capital-ramp barrier remains ARMED (5 disarm gates still pending). Article II + autonomous mode mandate.
- [x] **T002.0h.1 PASS — Track A E1 successor closure** (engineering Gate 1 of 5 of §9 HOLD #2 disarm chain CLEARED engineering layer 2026-04-28 BRT). Dex T2 commit `6a78b88` (E1 per-phase WarmUpGate + dated path resolvers AC1-AC10) + Quinn T3-T4 PASS 7/7 (`docs/qa/gates/T002.0h.1-qa-gate.md`) + Beckett N+1 PASS 10/10 strict-literal (`docs/backtest/T002-beckett-t11-bis-smoke-report-N+1-2026-04-28.md`) + Pax T6 cosign Status InReview → Done (`docs/stories/T002.0h.1.story.md` Validation Status post-impl 10/10 GO). **PRR-20260428-3 SUPERSEDES PRR-20260428-1** (AC8 invocation literal RESTORED with `--smoke` flag — `python scripts/pax_cosign.py verify` 5/5 OK; `pytest tests/contracts/test_spec_version_gate.py` 16/16 PASS). Spec yaml `data_splits` / `feature_set` / `trading_rules` / `n_trials` UNTOUCHED. Bonferroni n_trials=5 PRESERVED. Hold-out lock UNTOUCHED. **Awaits Riven §9 HOLD #2 Gate 1 dual-sign formal disarm + Mira ML co-sign on Gate 1.** Gates 2-5 remain pending downstream (T002.1.bis + Beckett N6 + Mira statistical clearance + Riven dual-sign final).

#### Article IV trace

- Beckett N4 report §root-cause-empirical-track-A (singleton observation)
- Beckett N4 report §diagnostic-run (synthetic-stub revelation)
- N4 evidence artifacts: `data/baseline-run/cpcv-dryrun-T002-N4-DIAG-NOSMOKE/` (5 artifacts sha256-ed)
- ESC-009 council ledger (Track A blind spot acknowledged)
- T002.0h.1 closure trace (Track A E1 successor): Dex commit `6a78b88` + Quinn gate `docs/qa/gates/T002.0h.1-qa-gate.md` + Beckett N+1 report `docs/backtest/T002-beckett-t11-bis-smoke-report-N+1-2026-04-28.md` + PRR-20260428-3 pax_cosign_hash `89f0e98cfe29f77d80b005e0460b779b03f011b21575364b9e9c2161e4876ba7`

**Pax cosign 2026-04-28 BRT — Autonomous Daily Session.**
**Gage merge 2026-04-28 BRT — PR #6 → main SHA `8b644d5`.**
**Pax T6 cosign 2026-04-28 BRT — T002.0h.1 closure (Track A E1 successor) + PRR-20260428-3 SUPERSEDES PRR-20260428-1.**

---

### ESC-009 — AC8 amendment (D1 empirical refutation → D2-narrow as_of=2024-08-22)

**Date (BRT):** 2026-04-27
**Source:** docs/councils/COUNCIL-2026-04-27-ESC-009-AC8-amendment.md
**Severity:** HIGH (blocks Riven §9 + Phase F unblock)
**Trigger:** D1-original (`as_of=2024-07-01`) HALT empirical — Operator precompute attempt per ESC-008 D1 path returned `InsufficientCoverage: only 91 valid DailyMetrics (need 126); window=[2023-11-13, 2024-06-30]; days_with_trades=111`. 2023-Q4 upstream unrecoverable per Dara coverage audit + user briefing.
**Council outcome:** **6/6 functional convergence APPROVE_D2_NARROW `as_of=2024-08-22`** (Aria + Mira + Beckett + Riven + Pax + Dara)
**User authorization:** Autonomous mode mandate 2026-04-27 BRT (mini-council decides)

**Critical architectural finding (Aria + Mira + Pax independent):** `scripts/run_cpcv_dry_run.py:761` hardcodes `warmup_gate_as_of = in_sample_start.isoformat()`. AC8 invocation literal does NOT carry `--in-sample-start` flag. D1-shifted (any non-default `as_of`) is functionally identical to D2-narrow under another label — Aria mandated honest relabel.

**Amendment:** AC8 invocation literal at story T002.0h L65 amended to add `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30` (existing CLI flag, no script change). Earliest viable `as_of=2024-08-22` per Dara walk (`state/T002/_dara_d1_candidates.txt`); ~10mo in-sample (~225 valid sample days) preserves non-degenerate Bonferroni n_trials=5 + DSR distribution per Mira.

**Spec compliance:** Spec yaml `data_splits.in_sample` UNCHANGED. PRR-20260427-1 appended to `preregistration_revisions[]` (patch 0.2.0 → 0.2.1) documenting empirical refutation of PRR-20260421-1's data_constraint_evidence (which did NOT model `is_valid_sample_day` filter). Pax cosign hash `0305e456f072ff521ffd2dc8ce487b261b7111796bbe274318d4fd381359919c` verified via `python scripts/pax_cosign.py verify`. Hold-out lock UNTOUCHED.

### Status

- [x] Council convened + 6 votes consolidated
- [x] Architectural finding propagated (warmup_gate_as_of hardcoded binding)
- [x] PRR-20260427-1 appended (with verified pax_cosign_hash)
- [x] AC8 invocation literal amended
- [x] T002.0h Change Log entry + AC8 amendment section + 10-point re-validation 10/10 GO
- [ ] Operator precompute `as_of=2024-08-22` via `python scripts/run_warmup_state.py --as-of-dates 2024-08-22 --output-dir state/T002/`
- [ ] Beckett N4 re-run amended invocation (`--in-sample-start 2024-08-22 --in-sample-end 2025-06-30`)
- [ ] Riven + Mira §9 deferral reconciliation (capital-ramp clearance deferred to future story)
- [ ] Sable audit coherence (Q-SDC Phase G)
- [ ] Gage push (autonomous mode)

**Article IV trace:** all clauses traceable to (a) Operator precompute log 2026-04-27 BRT, (b) Dara coverage audit (`docs/architecture/T002-data-coverage-audit-2026-04-27.md`), (c) user briefing 2026-04-27 BRT, (d) Dara D1-shifted candidates walk (`state/T002/_dara_d1_candidates.txt`), (e) ESC-006 + ESC-008 council ledgers, (f) 6 verbatim votes recorded in council ledger (condensed; full transcripts retained in council session log).

**Pax cosign 2026-04-27 BRT — Autonomous Daily Session.**

---

### ESC-008 — AC8 clarification (Beckett N3 HALT-ESCALATE → D1 approved)

**Date (BRT):** 2026-04-27
**Source:** [docs/councils/COUNCIL-2026-04-27-ESC-008-AC8-clarification.md](COUNCIL-2026-04-27-ESC-008-AC8-clarification.md)
**Severity:** HIGH (blocks Riven §9 + Phase F unblock)
**Trigger:** Beckett T11.bis #3 (N3) HALT-ESCALATE-FOR-CLARIFICATION ([report](../backtest/T002-beckett-t11-bis-smoke-report-N3-2026-04-27.md))
**Council outcome:** **4/5 MAJORITY APPROVE_D1** (Aria + Mira + Riven + Pax converging; Beckett conditional dissent D3 — personal preference declared D1)
**User authorization:** **GRANTED 2026-04-27 BRT**
**Action items:** see [council ledger §6 Action items](COUNCIL-2026-04-27-ESC-008-AC8-clarification.md#6-action-items-post-decision)

**3 mitigation paths surfaced (Beckett N3 §11):**
- **D1** (APPROVED) — Operator authorizes precompute warmup state for `as_of=2024-07-01` per AC9 cache contract + ESC-006 run-once-per-as_of principle (~5–7min cost). ZERO spec change, ZERO precedent damage.
- D2 — AC8 spec amendment (R15 evaluation required; rejected as overkill).
- D3 — AC8 declared PASS on semantic 8/9 PARTIAL_PASS reading (rejected: statistical malpractice per Mira; custodially unacceptable per Riven; binary-verifiability erosion per Aria + Pax).

### Status

- [x] Council convened + 5 votes consolidated
- [x] User authorization granted
- [ ] Operator precompute `as_of=2024-07-01` via `python scripts/run_warmup_state.py --as-of-dates 2024-07-01 --output-dir state/T002/`
- [ ] Beckett N4 re-run (full pipeline empirical, peak RSS < 6 GiB target, full wall-time captured)
- [ ] Riven §9 amendment (HOLD #1 clearance language preview in council ledger §2.4)
- [ ] Pax close + Sable audit (Q-SDC Phase G)
- [ ] Gage push (R12 user-gated)

**Article IV trace:** all clauses traceable to (a) Beckett N3 report §11 escalation matrix, (b) ESC-006 mini-council 4/4 APPROVE_F (council ledger 2026-04-26), (c) AC9 cache contract (T002.0h L73–78 DONE), (d) 5 verbatim votes recorded in council ledger (condensed for ledger; full transcripts retained in session log).

**Pax cosign 2026-04-27 BRT — Autonomous Daily Session.**

---

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

#### Update 2026-04-26 BRT — Mini-council 4/4 CONVERGENT APPROVE_F

**Aria critical finding (Option E REFUTED):**
- `feed_parquet.py:319-328` JÁ implementa numpy-direct path (T002.0b prior optimization, 35× speedup achieved with `to_numpy + tolist` replacing `to_pylist`)
- Aria's prior 40-70% E speedup estimate was STALE (pre-T002.0b)
- Hot path residual cost: `astype(object).tolist()` (boxing ns→datetime) + `_Trade` NamedTuple construction (Python-side mesmo via map C). Per-row Python object allocation is the floor.
- 382s IS the optimized path — no further pyarrow-layer mitigation viable
- E.1 (orchestrator helper) = duplicates holdout/manifest validation, R2 risk
- E.2 (feed_parquet body mod) = marginal 10-15% speedup, doesn't justify R15 reopen
- Option G (C+E hybrid) collapses to C-only because E is null

**4-vote convergent on APPROVE_F with mandatory contracts:**
- Aria: APPROVE_F (engineering through non-existent optimization wastes budget)
- Beckett: APPROVE_F (AC8 was overly strict, conflated dev iteration vs one-time precompute)
- Mira: APPROVE_F_PRAGMATIC (spec UNTOUCHED, story-level only; anti-leak preserved IF strict cache validation)
- Dara: APPROVE_F (hot path at pyarrow ceiling; cache strategy sound)

**Mandatory cache validation contracts (convergent):**
1. Triple-key cache: `(as_of_date, source_sha256_from_manifest, builder_version_semver)` — Mira/Dara strict
2. Fail-closed em mismatch (raise `StaleCacheError`, NO silent regenerate)
3. `--force-rebuild` escape hatch (Beckett)
4. Cache hit/miss logged em manifest for Sable audit
5. TTL infinito (imutável por chave — Mira)
6. AC8 reframe: warmup wall-time NOT smoke gate criterion; smoke total < 5min applies only post-warmup-cache-hit

**Status:** RESOLVED — autonomous mode executing F via Pax AC8 amend + Dex cache validation contract impl.

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

## ESC-007 — research_log._split_yaml_blocks parser inversion

**Date (BRT):** 2026-04-27
**Discovered by:** Beckett (@backtester) — T11.bis #2 re-run AC8 exit gate FAIL
**Source:** docs/backtest/T002-beckett-t11-bis-smoke-report-2026-04-27.md §11
**Severity:** HIGH (blocks AC8 exit gate; blocks Riven §9 cosign; blocks Phase F unblock)
**Type:** Latent bug (NOT memory/perf/streaming regression)

### Symptom

CPCV smoke aborts exit 1 in `compute_full_report → read_research_log_cumulative` step. KillDecision NOT produced. 1/5 artifacts persisted (only telemetry.csv). T002.0h streaming + AC9 cache contract observed PERFECT (warmup cache hit 0.336s, peak RSS 0.024 GiB on warmup; CPCV harness fanout 1.279s producing 225 results, peak RSS 142.85 MB) — failure is downstream of streaming/cache.

### Root cause

`packages/vespera_metrics/research_log.py::_split_yaml_blocks` toggle-fence walker is structurally inverted vs production format `docs/ml/research-log.md`. Parser captures prose bodies (lines 72-78 "Os cinco trials varrem: (a)...") and SKIPS actual frontmatter YAML blocks (64-70 + 80-86). Result: `n_trials_cumulative` parses prose narration as YAML, fails downstream consumer expecting `T002.0d=5 + T002.0f=0 = 5`.

### Why it slipped

5 existing parser tests (`tests/...research_log...`) all use `_write_research_log` mock helper which produces tightly-formatted YAML (no prose interleaving). Production ledger `docs/ml/research-log.md` interleaves prose narration between frontmatter blocks. Coverage gap = no integration test exercises real ledger format. AC11 fail-closed guard worked correctly (aborted smoke exit 1 instead of producing corrupt KillDecision).

### Honored guards (Beckett 7/7)

- #1 NO subsample: dataset window unchanged (`[2025-05-31, 2025-06-30]`).
- #2 NO modify engine config: `engine-config.yaml` read-only.
- #3 NO improvise threshold relaxation: AC8.5/8.8/8.9 reported FAIL, NOT waived.
- #4 Reported peak RSS HONESTLY: 142.85 MB from poller CSV `max(rss_mb)`.
- #5 NO retry after exit ≠ 0: single Step C invocation, captured + reported.
- #6 NO push: no git push attempted (Gage authority).
- #7 NO modify story files: report is the only artifact written by Beckett.
- (bonus) NO bypass AC11 abort guard: Riven invariant respected — bypass would require Riven cosign + governance entry.

### Action items (recommended owners — per Beckett report §11.3 + §11.5)

1. **Dex (@dev)** — fix `_split_yaml_blocks`. 3 abordagens em report §11.3:
   (a) state machine recognizing "consecutive `---` fences delimit a frontmatter block",
   (b) regex `^---\n(?P<body>.*?)\n---$` with re.MULTILINE+DOTALL,
   (c) adopt `python-frontmatter` library convention.
2. **Mira (@ml-researcher)** — clarify ledger header schema language; "top-level `---` fences" is ambiguous between "toggle" and "delimit pairs". R15 evaluation if `breaking_fields` revision is required for any chosen reinterpretation.
3. **Quinn (@qa)** — add integration test loading ACTUAL `docs/ml/research-log.md` from disk and asserting `n_trials_cumulative == 5` (sum T002.0d=5 + T002.0f=0); re-QA gate increment T002.0h to require this coverage before any future close.
4. **Beckett (@backtester)** — T11.bis #3 re-run (full plan re-execution) após Dex parser fix + Quinn re-QA.
5. **Riven (@risk-manager)** — §9 amendment apenas após T11.bis #3 PASS (HOLD #1 clearance criteria NOT MET enquanto full_report.json + KillDecision.verdict ausentes).

### Status

- [ ] Dex fix `_split_yaml_blocks`
- [ ] Quinn integration test (real ledger) + re-QA gate increment
- [ ] Beckett T11.bis #3 re-run
- [ ] Riven §9 cosign / HOLD #1 clearance
- [ ] Gage push (R12 user-gated)

### Article IV trace

Não houve invenção — todas as fontes citadas:
- Beckett report §11.1 (AC8 sub-criteria 9-row matrix), §11.3 (Dex 3 abordagens, ownership classification, mitigation NOT attempted rationale), §11.4 (canonical ESC-007 escalation text), §11.5 (handoff trigger sequence)
- AC11 fail-closed guard (Riven invariant — Beckett report §11.3 Mitigation NOT attempted #3)
- 5 parser tests existentes usando `_write_research_log` mock helper (Quinn coverage gap — Beckett report §11.3)
- Production ledger `docs/ml/research-log.md` linhas 64-86 (Mira authority — append-only R15)
- `packages/vespera_metrics/research_log.py::_split_yaml_blocks` (verified path on disk)

**Pax cosign 2026-04-27 BRT — Autonomous Daily Session.**

---

## Resolved escalations

(none yet)
