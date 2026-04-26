# T002 — Beckett Mira-Handshake Sign-Off (Pre-Flight Gate, Pre Dry-Run)

**Validator:** Beckett (@backtester) — The Simulator (Capricorn ♑)
**Trigger:** Squad pre-flight gate before `*run-cpcv --dry-run` executes Fase E.
**Date:** 2026-04-25 BRT
**Authority:** Article IV (No Invention) — every alignment row traces to spec §section, code path, or doc artifact.

---

## 0. Source matrix (read-only — Beckett does not modify any of these)

| Artifact | Path | Version / Lock | Hash (LF-normalized SHA256) |
|----------|------|----------------|-----------------------------|
| ML parent spec | `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` | v0.2.0 (Pax cosigned PRR-20260421-1) | (header self-ref) `4b5624ad…dc3fc` |
| Metrics spec (Mira-signature subject of handshake) | `docs/ml/specs/T002-vespera-metrics-spec.md` | spec_version: v0.2.2 (errata sweep, Quinn finding) | header claims `56238dc2…891f`; live disk LF SHA = `70c6a385…aba2e7` (header is self-referential — recomputed post-write per Mira convention; divergence is **expected**, not a fault) |
| Cost atlas | `docs/backtest/nova-cost-atlas.yaml` | v1.0.0 (Sable APPROVED_WITH_CONDITIONS) | `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126` ✅ matches engine-config lock |
| Engine-config | `docs/backtest/engine-config.yaml` | v1.0.0 | (locks atlas above by sha) |
| Dataset manifest | `data/manifest.csv` | 18 rows (6 warmup + 12 in_sample) | `78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72` ✅ matches prompt |
| Hold-out lock module | `scripts/_holdout_lock.py` (re-export `packages/t002_eod_unwind/adapters/_holdout_lock.py`) | hardcoded — not spec-driven | `[2025-07-01, 2026-04-21]` |

**Naming clarification (process finding, not a defect):** the prompt referred to "spec ML T002 v0.2.2". On disk, v0.2.2 is the version of the **metrics module spec** (`T002-vespera-metrics-spec.md`), not the ML parent spec, which remains v0.2.0. The metrics spec at v0.2.2 is a child of ML spec v0.2.0 §metrics_required L159-172 and has not changed `cv_scheme`, `data_splits`, `feature_set`, `label`, `trading_rules`, or `n_trials`. Per MANIFEST R15 / Beckett persona §spec_consumer, no breaking field was touched → no CPCV invalidation, no Bonferroni recount needed. v0.2.2 is a §6.5 errata sweep + §14 stale reference fix (PBO 0.8333→1.0 walkthrough correction was already in v0.2.1; v0.2.2 cleans up one remaining checklist line). Handshake proceeds.

---

## 1. Spec → Implementation alignment matrix

| # | Spec section (v0.2.2 metrics + v0.2.0 ML) | Claim | Implementation locus | Verdict |
|---|-------------------------------------------|-------|----------------------|---------|
| 1 | metrics §6.4 PBO convention LOCKED | rank ASCENDING via `scipy.stats.rankdata(method='min')`; argmax IS first-index via `np.argmax`; overfit ⟺ λ_n ≤ 0 | `packages/vespera_metrics/pbo.py` lines 73-84 (`np.argmax(r_is)`, `stats.rankdata(r_oos, method="min")`, `if lam <= 0.0: overfit_count += 1`) | **PASS** — byte-faithful to LOCKED convention; docstring (lines 7-17) cites §6.4 |
| 2 | metrics §6.5 walkthrough corrected (var2/var3 IS = 5.5 in s=3) → T11 byte-exact 1.0 | T11 expected = 1.0, tolerance 1e-12 | Endorsed independently in `docs/backtest/T002-pbo-beckett-validation.md` (Beckett v0.2.1 cross-val); v0.2.2 errata only re-numbers references — formula and walkthrough unchanged from v0.2.1 | **PASS** — already endorsed; v0.2.2 sweep is residual cosmetic |
| 3 | ML spec §10 (PRR-20260421-1) lookback P126 (not P252) | rolling 126 valid business days for magnitude + atr_day_ratio | `packages/t002_eod_unwind/warmup/percentiles_126d_builder.py` module docstring lines 1-23 explicitly cites P126 + PRR-20260421-1 rationale; `T002.1 Quinn PASS` | **PASS** |
| 4 | ML spec §feature_set 3 features | `intraday_flow_direction = sign(close[t] - open_day)`; `intraday_flow_magnitude = |close[t] - open_day| / ATR_20d`; `atr_day_ratio = ATR_day / ATR_20d` | `packages/t002_eod_unwind/core/feature_computer.py` lines 1-16 docstring + `compute_features` body | **PASS** |
| 5 | metrics §K1 kill criterion | DSR > 0 (boolean) | `KillDecision.k1_dsr_passed` in `vespera_metrics/report.py` (per spec §1.3) | **PASS — DECLARED** (gate evaluation deferred to Fase E final) |
| 6 | metrics §K2 kill criterion | PBO < 0.4 | `KillDecision.k2_pbo_passed` declared | **PASS — DECLARED** |
| 7 | metrics §K3 kill criterion | IC_holdout >= 0.5 × IC_in_sample (decay rule) | `KillDecision.k3_ic_decay_passed` declared; evaluated at Fase E final only (hold-out untouched in dry-run) | **PASS — DECLARED** (correctly deferred — would violate hold-out lock if computed now) |
| 8 | metrics provenance fields | `MetricsResult.spec_version`, `seed_bootstrap`, `n_trials_used`, `n_trials_source`, `computed_at_brt` | `vespera_metrics/report.py` MetricsResult dataclass | **PASS — DECLARED** in spec; runtime provenance asserted on first CPCV result |

**Net:** 8/8 alignment rows PASS. No misalignment between spec v0.2.2 / ML v0.2.0 and the four implementation packages (`vespera_metrics`, `vespera_cpcv`, `t002_eod_unwind/core`, `t002_eod_unwind/warmup`).

---

## 2. Atlas → engine-config wire alignment

| Field | Atlas v1.0.0 | engine-config.yaml v1.0.0 | Result |
|-------|--------------|---------------------------|--------|
| `atlas_sha256_lock` | (compute LF) `acf44941…a5126` | declared `acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126` | ✅ byte-exact match |
| `atlas_version_lock` | `atlas_version: "1.0.0"` | `atlas_version_lock: "1.0.0"` | ✅ |
| `cost_components.brokerage` | `costs.brokerage.per_contract_one_way: 0.00` | `from: "costs.brokerage.per_contract_one_way"` → expected_brl 0.00 | ✅ wired |
| `cost_components.exchange_fees` | `costs.exchange_fees.per_contract_one_way: 1.23` | wired identically; expected_brl 1.23 | ✅ |
| `cost_components.ir_day_trade` | `tax_day_trade.ir_rate: 0.20`, treatment `post_hoc_on_monthly_net_gain` | wired with `applies_at: metrics_aggregation_monthly`, `applies_at_per_fill: false` | ✅ correctly post-hoc, NOT per-fill |
| WDO contract spec | `product.tick_size_points: 0.5`, `product.contract_multiplier_brl_per_point: 10.00` | wired with module-constant assertions in `exec_backtest.py` | ✅ |
| `policy_on_sha_mismatch` | n/a | `fail_fast` | ✅ Article IV honored |
| `sha_normalization` | n/a | `lf` | ✅ resists CRLF on Windows (verified — raw-disk and LF-normalized hashes match for atlas: both `acf44941…a5126`) |

**Open audit conditions tracked in engine-config (F-02/F-03/F-04 + atlas.to_verify[0] liquidacao_brl):** all flagged `blocks_phase_E: false`. Beckett confirms — these are sourcing/provenance follow-ups, not numerical drift. Non-blocking for dry-run.

**Net:** 8/8 atlas wire rows PASS. Atlas-engine-config link is sha-locked, fail-fast on drift.

---

## 3. CPCV defaults vs spec §cv_scheme

| Spec field (v0.2.0 cv_scheme) | Spec value | Implementation default (`vespera_cpcv/config.py`) | Verdict |
|-------------------------------|-----------|---------------------------------------------------|---------|
| `type` | CPCV | `CPCVConfig.from_spec_yaml` rejects anything else (line 120) | ✅ |
| `n_groups` | 10 | accepted at runtime; valid for `n_groups >= 2` (line 50) | ✅ |
| `k` | 2 | accepted at runtime; valid for `1 <= k < n_groups` (line 55) | ✅ |
| `n_paths` | 45 (= C(10,2)) | computed property `math.comb(n_groups, k)` line 71 | ✅ — derived, not invented |
| `embargo_sessions` | 1 | accepted; non-negative validation line 60 | ✅ |
| `purge_formula_id` | `AFML_7_4_1_intraday_H_eq_session` (Mira spec §8 ref) | default in `CPCVConfig` line 47 — exact string match | ✅ |
| Purge implementation | AFML §7.4.1 eq.7.1 (label-horizon overlap) | `vespera_cpcv/purge.py:purge_train` lines 103-135 — formula `t_end(e) >= window_start AND t_start(e) <= window_end` | ✅ matches AFML eq.7.1 |
| Embargo implementation | AFML §7.4.2 (next k sessions after test block) | `vespera_cpcv/purge.py:embargo_train` lines 138-188 — drops first `embargo_sessions` distinct sessions strictly after `block.last_session` | ✅ matches Mira purge-formula doc §4.2 |
| Seed plumbing | R6 deterministic | `CPCVConfig.seed: int` field; `from_spec_yaml(seed=...)` accepts override; default 42 via `SPEC_SEED` env | ✅ |

**Net:** 9/9 CPCV default rows PASS. Defaults bate spec byte-exact. Purge formula tag id is the canonical Mira string.

---

## 4. Dataset readiness

### 4.1 Manifest verification (live disk vs prompt-asserted hash)

```
data/manifest.csv
  rows: 19 (1 header + 18 data rows)
  raw SHA256 = LF SHA256 = 78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72  ✅
```

### 4.2 Per-parquet integrity (manifest declared SHA vs computed SHA)

All 18 parquets — recomputed live, byte-exact match against manifest column `sha256`:

| Parquet | Phase | Manifest SHA | Computed SHA | Match |
|---------|-------|--------------|--------------|-------|
| wdo-2024-01 | warmup | `a5a3db8a…36b30` | `a5a3db8a…36b30` | ✅ |
| wdo-2024-02 | warmup | `9b2afe21…7424e` | `9b2afe21…7424e` | ✅ |
| wdo-2024-03 | warmup | `0e4d59d6…03d6a6` | `0e4d59d6…03d6a6` | ✅ |
| wdo-2024-04 | warmup | `bd890da5…23dab` | `bd890da5…23dab` | ✅ |
| wdo-2024-05 | warmup | `72a7b8e6…07340` | `72a7b8e6…07340` | ✅ |
| wdo-2024-06 | warmup | `1ebf2603…c8b3a` | `1ebf2603…c8b3a` | ✅ |
| wdo-2024-07 | in_sample | `62dd957a…7e68e` | `62dd957a…7e68e` | ✅ |
| wdo-2024-08 | in_sample | `bf7d42f5…83ce0` | `bf7d42f5…83ce0` | ✅ |
| wdo-2024-09 | in_sample | `c142aa8a…58757c` | `c142aa8a…58757c` | ✅ |
| wdo-2024-10 | in_sample | `91bb2b91…02141` | `91bb2b91…02141` | ✅ |
| wdo-2024-11 | in_sample | `810bb881…860f7e4` | `810bb881…860f7e4` | ✅ |
| wdo-2024-12 | in_sample | `2c7a5c59…76057` | `2c7a5c59…76057` | ✅ |
| wdo-2025-01 | in_sample | `2023ad05…12e17` | `2023ad05…12e17` | ✅ |
| wdo-2025-02 | in_sample | `90790b67…0b69d` | `90790b67…0b69d` | ✅ |
| wdo-2025-03 | in_sample | `81d97890…09ca85` | `81d97890…09ca85` | ✅ |
| wdo-2025-04 | in_sample | `6cbc3ef1…fda313` | `6cbc3ef1…fda313` | ✅ |
| wdo-2025-05 | in_sample | `561f443c…27875` | `561f443c…27875` | ✅ |
| wdo-2025-06 | in_sample | `c89edf9f…25c94` | `c89edf9f…25c94` | ✅ |

### 4.3 In-sample window check

- 6 warmup parquets cover 2024-01-02 → 2024-06-28 (≈ 126 valid business days for P126 lookback) ✅
- 12 in_sample parquets cover 2024-07-01 → 2025-06-30 (12 contiguous months) ✅
- Last in_sample timestamp = 2025-06-30 17:59:59.557000 BRT
- Hold-out boundary = 2025-07-01 (HARDCODED in `scripts/_holdout_lock.py:39`)
- Gap between last in_sample and hold-out start: zero days — **exact, no overlap** ✅

### 4.4 Hold-out preserved

`scripts/_holdout_lock.py:HOLDOUT_START = date(2025, 7, 1)`; `HOLDOUT_END_INCLUSIVE = date(2026, 4, 21)`. Module is **hardcoded** by design (lines 35-40 docstring) — spec edits cannot silently re-shape the gate. No file under `data/in_sample/` references any date ≥ 2025-07-01. **Hold-out is virgin and lock-protected.** ✅

**Net:** 4/4 dataset readiness rows PASS.

---

## 5. Verdict

**HANDSHAKE_OK_FOR_DRY_RUN.**

- Spec → impl alignment: 8/8 PASS
- Atlas → engine-config wire: 8/8 PASS
- CPCV defaults: 9/9 PASS
- Dataset readiness: 4/4 PASS (manifest, per-parquet, window contiguity, hold-out virginity)
- v0.2.2 errata is non-breaking per MANIFEST R15 — no CPCV re-execution from-scratch required, no N_trials Bonferroni recount.
- All open Sable atlas conditions (F-02/F-03/F-04 + liquidacao_brl) are non-blocking for Phase E; they remain tracked.
- All [TO-VERIFY] tags (slippage cushion, IRRF) are explicit and parametrized — Article IV honored.

**Next handoff:** `*run-cpcv --dry-run` is cleared. Beckett will produce `docs/backtest/runs/{run_id}/report.md` with seed, simulator version, dataset hash (`78c9adb3…ee72`), spec hash (metrics LF `70c6a385…aba2e7`; ML v0.2.0 self-ref `4b5624ad…dc3fc`), CPCV config (`N=10, k=2, embargo=1, n_paths=45, purge_formula_id=AFML_7_4_1_intraday_H_eq_session`), atlas hash (`acf44941…a5126`), and engine-config version 1.0.0.

---

— Beckett, reencenando o passado 🎞️
