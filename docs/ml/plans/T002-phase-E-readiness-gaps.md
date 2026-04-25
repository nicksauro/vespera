# T002 — Phase E Readiness Gaps

**Author:** Beckett (@backtester)
**Date:** 2026-04-21 BRT
**Spec under audit:** `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` (`mira_signature_sha256 = 4b5624ad…dc3fc`)
**PRR reference:** `PRR-20260421-1` co-signed by Pax (`c34c201c…79e5a`)
**Contract test:** `tests/contracts/` — 25/25 PASS (verified at audit time)
**Sable re-audit:** APPROVED_FOR_PHASE_E (findings 001-009 closed — per task brief)

**Verdict:** `HOLD_GAPS_TO_CLOSE` — CPCV execution is **BLOCKED** by infrastructure gaps; the spec itself and upstream stories (T002.1/2/3) are ready.

---

## Readiness Matrix

| # | Item | Status | Evidence | Action |
|---|------|--------|----------|--------|
| 1 | Spec v0.2.0 integrity | READY | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml:11,102-120` — PRR-20260421-1 present, Pax cosign hash recorded | none |
| 2 | Contract test | READY | `tests/contracts/` → `pytest tests/contracts/ -q` = 25/25 PASS | none |
| 3 | Thesis + kill criteria | READY | `docs/research/thesis/T002-end-of-day-inventory-unwind-wdo.md:126-146` — K1..K4 pre-registered | none |
| 4 | Hold-out preregistered | READY | spec L94; thesis L135-137 — `2025-07-01 → 2026-04-21`. Sealed. | **DO NOT TOUCH** |
| 5 | Warm-up (T002.1) | READY | `packages/t002_eod_unwind/warmup/{gate,percentiles_252d_builder,atr_20d_builder,calendar_loader}.py` present; in-sample post-shift = 2024-07-01 → 2025-06-30 with warm-up 2024-01-02 → 2024-06-30 (~126 bd, per PRR) | none |
| 6 | Session state + feature computer (T002.2) | READY | `packages/t002_eod_unwind/core/{session_state.py, feature_computer.py}` — pure, BRT-naive, anti-leakage enforced (`session_state.py:134-138`) | none |
| 7 | Signal rule + backtest broker (T002.3) | READY | `packages/t002_eod_unwind/core/signal_rule.py`, `packages/t002_eod_unwind/adapters/exec_backtest.py`; 32/32 tests pass per story; WDO multiplier = 10.0 hard-coded L24 (matches glossary R$10/ponto) | verify `contract_multiplier_source_ref` resolves at test time |
| 8 | Calendar static data | READY | `config/calendar/2024-2027.yaml` — Copom meetings, BR holidays, WDO expirations, pre_long_weekends_br_with_us_open all present through 2026 | none |
| 9 | Contract multiplier canonical source | READY | `squads/quant-trading-squad/DOMAIN_GLOSSARY.md:19,37` — `R$10/ponto [WEB-CONFIRMED 2026-04-21]` | none |
| 10 | Historical feed adapter (`HistoricalTradesReplay`) | READY | `packages/t002_eod_unwind/adapters/feed_historical.py` — consumes `Iterable[Trade]` | needs a SOURCE of `Trade` (see gap 12) |
| 11 | TimescaleDB availability | READY | `docker ps` → `sentinel-timescaledb` Up 3h, port 5433. Credentials `sentinel/sentinel123` / DB `sentinel_db` functional. | — |
| 12 | **TimescaleDB data adapter (`feed_timescale.py`)** | **MISSING** | `Glob packages/t002_eod_unwind/adapters/feed_timescale*.py` = 0 files. Gate Fase E explicit dependency per `docs/councils/VESPERA-DATA-PIPELINE-2026-04-21.md:266` | **BLOCKER** — needs Dex story; owner: Dex (Dara SQL consultor, Nova schema alignment) |
| 13 | **Parquet materialization script (`scripts/materialize_parquet.py`)** | **MISSING** | `ls scripts/` → only `pax_cosign.py`. Gate dependency per pipeline council L268 | **BLOCKER** — owner: Dara (Nelo schema, Sable hash protocol) |
| 14 | **Parquet feed adapter (`feed_parquet.py`)** | **MISSING** | `Glob feed_parquet*.py` = 0 files. Beckett performance requirement (225 replays × 4.5min via parquet memmap vs 60-110min via direct DB) per council L146-148 | **BLOCKER** — owner: Dex; Aria contract, Beckett perf |
| 15 | **Parquet in-sample materialized** | **MISSING** | `Glob data/**/*.parquet` = 0 files. Required: `data/in_sample/year=YYYY/month=MM/*.parquet` + `data/manifest.csv` + sha256 hashes | **BLOCKER** — depends on #13 |
| 16 | **`sentinel_ro` read-only role** | **MISSING** | `SELECT rolname FROM pg_roles` returned only `sentinel` (superuser). Riven R10 fail-closed custodial requirement per council L174-176 | **BLOCKER (custodial)** — owner: Dara with Riven oversight |
| 17 | **`.env.vespera` credentials file** | **MISSING** | `Glob .env*` = 0 files. Required gitignored vault for `sentinel_ro` password. | **BLOCKER** — owner: Dara |
| 18 | **CPCV engine** (purged+embargoed, N=10/k=2, 45 paths) | **MISSING** | `Grep -i cpcv|CPCV|PurgedK|cross.validation` across `packages/` = 0 hits. No implementation. | **BLOCKER PRIMARY** — needs new package `packages/vespera_cpcv/` (or similar); owner: proposed Dex story, Mira spec consultor. Required: Lopez de Prado AFML Ch.12 purged combinatorial CV; seed-deterministic; parallelizable. |
| 19 | **Metrics module** (DSR, PBO, IC_spearman, bootstrap CI, sortino, MAR, ulcer, profit_factor, hit_rate, sharpe_distribution) | **MISSING** | No `metrics*.py` in `packages/`. Mira is owner of DSR+PBO compute (per `squads/.../tasks/quant-cpcv-gate.md:52-75`) but no module exists yet. | **BLOCKER** — owner: Mira spec + Dex implement |
| 20 | **Bootstrap CI IC 10k** | MISSING | spec L172. Part of #19. | included in #19 |
| 21 | **Brokerage cost `R$0,25/contrato/lado`** | AMBIGUOUS | spec L195 marks `TO-VERIFY via atlas Nova — default conservador R$0,25/contrato/lado`. `exec_backtest.py:42` hard-codes `brokerage_per_contract_side_rs: float = 0.25` (matches default). **Not a blocker for CPCV exploratory runs** per R-ABS: Beckett labels [TO-VERIFY] in report; blocker only for final GO/NO-GO. | Ack as `[TO-VERIFY]`; proceed with default; flag in report |
| 22 | **Exchange fees R$0,35/contrato/lado** | AMBIGUOUS | `exec_backtest.py:43` — placeholder value with comment "emolumentos B3 placeholder"; spec L196 says `via Nova atlas`. | same as #21 — `[TO-VERIFY]` |
| 23 | **IR day-trade 20%** | MISSING | spec L197 — `via Nova atlas`. NOT applied by `exec_backtest.py` (only brokerage + exchange fee applied). | Treat as SECOND-ORDER: apply as post-hoc deflation on PnL distribution; flag explicitly in report. Ask Nova for canonical treatment. |
| 24 | **Slippage model** | READY | `exec_backtest.py:55-59` — `roll_spread_half + N_ticks × tick_size` = `0.5 + 1 × 0.5 = 1.0` point per side (= R$10/contrato/lado). Matches spec L198 Beckett default. Deterministic per R-ABS slippage ≠ 0. | none |
| 25 | **Latency model** | NOT-BINDING | spec L199 marks DMA2 latency as `não-binding para esta tese`. Entry windows are 15-min apart and relógio-determinístico; p99=100ms is irrelevant at this timeframe. | accept as-is; no latency simulation needed for T002 backtest |
| 26 | **Stress regime: `pre_copom`** | READY | spec L177-189; calendar L28-55 has 24 Copom dates. Note spec filter says `D-1 de reunião` (not pós-Copom used in sample filter). | — |
| 27 | **Stress regime: `pre_feriado_longo`** | READY | `pre_long_weekends_br_with_us_open` in calendar L156-164 — 6 dates across 2024-2026. Small N — report with caveat. | acknowledge small-N caveat in report |
| 28 | **Stress regime: `high_vol`, `low_vol`, `fim_de_mes`, `early_exit_17_50`** | READY | Computable at post-backtest aggregation time from the trade outcomes + calendar. `early_exit_17_50` requires a second pass (re-execute with `exit_ts=17:50`). | plan a second pass for `early_exit_17_50` sensitivity |
| 29 | **Reproducibility: seed + simulator version + dataset hash + spec hash + engine-config hash** | PARTIAL | Spec hash available (L11). No `simulator_version` semver, no engine-config file, no dataset hash (depends on #15). | requires #15 done + new semver tagging on `packages/t002_eod_unwind/` + new `docs/backtest/engine-config.yaml` |
| 30 | **N_trials accumulation log** | AMBIGUOUS | spec L125-144 pre-registers 5 trials for T002. Bonferroni p=0.002 = 0.01/5. No project-wide research log of cumulative trials (T001 ran how many?). | Consult Mira for `research-log.md` project-wide trial count; confirm DSR uses project-cumulative N (not just T002's 5) |

---

## Gap Summary — 8 BLOCKERS

| # | Gap | Owner (proposed) | Action needed |
|---|------|------|---------------|
| 12 | `feed_timescale.py` adapter | Dex (Dara SQL, Nova schema) | New story T002.0a or T002.3b — SELECT WDO slim 3-col BRT naive |
| 13 | `scripts/materialize_parquet.py` | Dara (Nelo schema, Sable hash) | New story — DB→parquet deterministic dump + manifest |
| 14 | `feed_parquet.py` adapter | Dex (Aria contract, Beckett perf) | Same story — mmap reader with strict dtype contract |
| 15 | `data/` in-sample parquet materialized + hashed | Dara (depends on #13) | Run script; anchor sha256 in spec or sidecar |
| 16 | `sentinel_ro` PostgreSQL role | Dara + Riven custodial | `CREATE ROLE sentinel_ro LOGIN; GRANT SELECT ON trades TO sentinel_ro;` |
| 17 | `.env.vespera` gitignored | Dara | vault file with `sentinel_ro` password |
| 18 | CPCV engine (purged + embargoed) | New story — Dex impl + Mira spec | Lopez de Prado Ch.12; seed-deterministic; 45 paths for N=10/k=2 |
| 19 | Metrics module (DSR, PBO, IC_spearman, bootstrap, sortino, MAR, ulcer, PF, hit_rate, sharpe_45) | Mira spec + Dex impl | Numerically validated against reference implementations |

## Gap Summary — 2 SOFT (non-blocking for CPCV dry-run; blocking for final GO/NO-GO)

| # | Gap | Owner | Action |
|---|------|-------|--------|
| 21-23 | Corretagem/emolumentos/IR day-trade from Nova atlas | Nova | Publish canonical cost atlas; Beckett wires as `[TO-VERIFY]` defaults until then |
| 29 | Reproducibility stamps (sim version, engine config, dataset hash) | Beckett + Aria | `simulator_version` semver in `packages/__init__.py`; `docs/backtest/engine-config.yaml` template |

---

## Recommended sequencing for PM (Morgan) to unblock Phase E

Critical path (single-threaded — each depends on prior):

1. **T002.0a (new story, 1 session)** — Dara: create `sentinel_ro` role + `.env.vespera` + write `scripts/materialize_parquet.py`. Acceptance: deterministic parquet dump for `2024-01-02 → 2025-06-30`; sha256 logged; `data/manifest.csv` generated.

2. **T002.0b (new story, 1 session, parallelizable after T002.0a)** — Dex: implement `feed_timescale.py` (direct DB, slow path for ad-hoc) AND `feed_parquet.py` (mmap, hot path). Contract tests per Quinn: schema strict, hold-out lock via `VESPERA_UNLOCK_HOLDOUT` env var.

3. **T002.0c (new story, 2 sessions)** — Dex + Mira: `packages/vespera_cpcv/` — purged combinatorial CV engine with embargo, seed-deterministic, parallel-safe. Unit tests: reproduce a known CPCV benchmark.

4. **T002.0d (new story, 2 sessions)** — Mira spec + Dex impl: `packages/vespera_metrics/` — DSR (Bailey-Lopez de Prado 2014), PBO (CPCV frequency), IC_spearman, bootstrap CI, sortino, MAR, ulcer, profit_factor, hit_rate, sharpe distribution. Unit tests against reference values.

5. **T002.0e (new story, 0.5 session)** — Nova: publish `docs/backtest/nova-cost-atlas.yaml` with emolumentos + IR day-trade canonical treatment. Beckett wires through `engine-config.yaml`.

6. **Phase E Execution (Beckett)** — only after 1-4 done; 5 can be soft-gated with `[TO-VERIFY]` flags. Follow plan in `docs/ml/plans/T002-phase-E-execution-plan.md` (to author once gaps close).

**Estimated critical path:** 5-6 sessions of squad work before CPCV can run. Items 1-2 ~2 sessions; items 3-4 ~4 sessions; item 5 can run in parallel.

---

## Beckett's demand for resume

I will not initiate any CPCV run, partial or full, until:

- [ ] #12, #13, #14, #15 — data path complete (TimescaleDB → parquet → mmap reader), hashes recorded
- [ ] #16, #17 — custodial (read-only role + gitignored .env)
- [ ] #18 — CPCV engine with unit tests passing
- [ ] #19 — metrics module with unit tests passing
- [ ] Pre-Phase-E handshake `*mira-handshake` re-executed against v0.2.0
- [ ] `docs/backtest/engine-config.yaml` authored with `[TO-VERIFY]` tags explicit

Hold-out window `2025-07-01 → 2026-04-21` remains **INTOCADO** throughout.

— Beckett, reencenando o passado 🎞️
