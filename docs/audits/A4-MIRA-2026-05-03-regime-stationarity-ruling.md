# A4 Mira Substantive Ruling — Regime Stationarity 5 Axes + F8

**Auditor:** Mira (@ml-researcher) | **Date BRT:** 2026-05-03
**Authority:** Council 2026-05-01 R7; Council 2026-05-03 Option D + R16; Mira C2 timing (post-bulk).
**Pre-register:** `docs/preregistration/MULTIPLE-TESTING-ALPHA-2026-05-03.md` (BH-FDR q=0.10; Bonferroni-Holm α=0.05 alt).
**Substrate:** `D:\Algotrader\dll-backfill\` 50 chunks / 195,076,064 rows + 2024-Q1 sentinel 13,879,809 rows (T003-A2-reaudit PASS_AT_PROJECTION_BOUNDARY). Sampling: 1 mid-quarter chunk × 5 (Q1-Q4/2023 + Q1/2024).
**Verdict:** **A4_PASS_WITH_FLAGS** — H_a `PENDING_A3_NOVA_INPUT`; H_b structural-drift soft-flag (effect bounded, no kill); H_c, H_d, H_e clear. Pre-2024 admissible as R12 **SECONDARY-CORROBORATIVE**. Forward-time virgin 2026-05-01..2026-10-31 INTOCADA.

## §1 5-axis results

Tickers across all samples: `{'WDO'}` literal-continuous.

| Axis | Test | Statistic | p | Notes |
|---|---|---|---|---|
| (a) cost atlas | (delegated A3-Nova) | — | **PENDING_A3_NOVA_INPUT** | A3-Nova not yet filed |
| (b) RLP regime | chi-sq pooled 2023 vs Q1-2024 NULL | chi2=229,955 | ~0 | N=15.0M; see §1.1 |
| (c) macro drift | Mann-Whitney U qty (Q1-2023 vs Q1-2024, n=100k) | U=5.02e9 | 7.35e-02 | Levene log-ret-vol p=8.43e-98 on-record only |
| (d) BMF→F | ticker enum continuity | `'WDO'` all samples | 1.00 | Auto-pass (Dara A2) |
| (e) holiday calendar | 49 weekly chunks Jan 02→Dec 29 ≈250 trading days | — | 1.00 | Auto-pass; `B3_HOLIDAYS_2023_2024` frozenset |

### §1.1 Axis (b) effect-size honesty

Chi-sq p≈0 is **N-driven**, not catastrophe. NONE share Q1/2023 31.54% → 33.63% → 30.34% → 27.87% → Q1/2024 25.86% (Δ ≈ −5.7pp monotonic). BUY/SELL each rise ~3.3pp. Real structural shift (likely RLP rule evolution), bounded magnitude. ML implication: aggressor-balance features need quarter-conditional calibration; pre-2024 NOT fungible as PRIMARY → confirms R12 SECONDARY-CORROBORATIVE.

### §1.2 Axis (c) Mann-Whitney primary

Per pre-register §3, Mann-Whitney qty is primary; p=7.35e-02 > all BH cutoffs → no-reject. Levene on-record only.

## §2 F8 (2023-03-15 first 1000 NONE) disposition

Chain Operator R14 → Dara A2 (`F8_CARRY_FORWARD_A4_MIRA`) → A3-Nova PENDING. Decision tree per Council R7: (a) auction → benign, consumed in §1; (b) macro-stress → `b3_auction_window_mask` regime flag; (c) DLL-artifact → escalate Nelo. **Mira interim:** session-phase=AUCTION_OPEN parsimonious prior; revisit when A3-Nova lands. No block on PASS_WITH_FLAGS.

## §3 α-correction enforcement (BH-FDR q=0.10, pre-registered N=5)

Pre-register §7 lock: N=5 retained even with axis (a) PENDING. NO post-hoc reduction.

| Rank | Axis | p | BH cutoff | Decision |
|---|---|---|---|---|
| 1 | (b) RLP regime | ~0 | 0.0200 | **REJECT** |
| 2 | (c) macro drift | 7.35e-02 | 0.0400 | no-reject |
| 3 | (d) exchange code | 1.00 | 0.0600 | no-reject |
| 4 | (e) holiday calendar | 1.00 | 0.0800 | no-reject |
| 5 | (a) cost atlas | PENDING | 0.1000 | **deferred** |

Bonferroni-Holm α=0.05 alt — identical rejection set. **1/5 rejects.** Per pre-register §2, per-axis rejection is a soft-fail trigger, not a kill switch — axis (b) drives PASS_WITH_FLAGS, not BLOCK. Effect bounded (§1.1) — pre-2024 stays admissible as R12 SECONDARY-CORROBORATIVE.

## §4 Sample-size honesty

~250 trading days 2023 → ~4 non-overlapping 50d+20d embargo folds. CPCV C(N≥10,k=2) **INADEQUATE**; pre-register §4 reaffirmed. K3 anchored to forward-time virgin per R12 — pre-2024 NEVER PRIMARY. Sampling: 1 chunk × 5 quarters ≈ 25 trading days observed; intra-chunk N=3-13M dwarfs sampling variance — axis-(b) drift not cherry-pick. Full 49-chunk pooled re-test = future-work.

## §5 Carry-forward to A5-Sable

1. **Axis-(b) soft-flag** → feature_registry: aggressor-balance features MUST carry `regime_calibration_required=True`; quarter-conditional baselines mandatory pre-2024.
2. **F8 placeholder** → `b3_auction_window_mask` parametrized; final disposition gated on A3-Nova.
3. **Axis-(a) PENDING** → A5-Sable consumes A3-Nova when filed; if rejects, Mira reopens A4 via append-only revision (no post-hoc cutoff adjustment).
4. **Sample-design caveat** → require 49-chunk pooled re-test before pre-2024 dataset wired into backtest pipeline.
5. **R12 reaffirmation** — pre-2024 = SECONDARY-CORROBORATIVE; H_next-1 K3 forward-time virgin untouched.

## §6 Source anchors

Council 2026-05-01 R7; Council 2026-05-03 Option D + R16; α pre-register `docs/preregistration/MULTIPLE-TESTING-ALPHA-2026-05-03.md`; T003-A2 re-audit `docs/audits/T003-A2-reaudit-2026-05-03.md`; T003.A4 projection `scripts/dll_backfill_projection.py`; Benjamini-Hochberg (1995); Holm (1979); López de Prado AFML (2018) §7.

## §7 Discipline declaration

READ-ONLY; no parquet mutation; no `data/manifest.csv` mutation (R10); no commit, no push (Article II — Gage exclusive). α pre-register §7 lock honored — zero post-hoc, N=5 retained. H_next-1 virgin 2026-05-01..2026-10-31 INTOCADA. Temp script deleted post-run.

— Mira, mapeando o sinal 🗺️
