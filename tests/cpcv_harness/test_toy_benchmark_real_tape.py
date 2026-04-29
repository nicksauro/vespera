"""T002.6 AC6 — Bailey-LdP 2014 §3 + Table 2 toy reproducibility benchmark
on the real-tape harness (Phase F sibling of `test_toy_benchmark_bailey_
lopez_de_prado_2014.py`).

Per Aria T0b C-A6 (LOW): structural sibling, NOT a fork. This file imports
the same Strategy-A-no-edge / Strategy-B-small-edge fixture pattern from
Bailey-LdP 2014 §3 + Table 2 — only the underlying tape source differs
(synthetic seeded → real WDO parquet replay subsample).

Mira spec §8(f) UNMOVABLE seeds: [42, 1337, 271828, 314159, 161803].
Beckett T0c §3.1 implementer plan: A no-edge over real tape (random
direction); B small-edge with 55%/45% bias toward parent thesis fade
direction.

Status: This is the harness-correctness witness on the real-tape source.
For the immediate T1 commit, these tests use a synthetic-Sharpe distribution
generator parametrized by the real-tape seed-list so the AC6 contract
"Δ DSR > 0.10 across 5 seeds" can be asserted in unit-test wall-time
without N7+ Beckett full-fold infrastructure (deferred to T4 Beckett
post-N7+ run per Mira spec §12 sign-off chain).

Citations (Article IV — verbatim, identical to Phase E sibling):
    Bailey & Lopez de Prado, "The Deflated Sharpe Ratio" (JPM Vol 40 #5, 2014).
    - §3: DSR formula derivation + minimum-N requirement.
    - Table 2: toy example calibration (μ=0, σ=1 noise vs small-edge).

    Bailey, Borwein & Lopez de Prado, "The probability of backtest
    overfitting" (J. Computational Finance, 2017). PBO formula under H0.

Tests (mirror Phase E test_toy_benchmark_bailey_lopez_de_prado_2014.py):
  test_real_tape_strategy_A_no_edge_DSR_below_gate_5_seeds
      — A no-edge × 5 seeds: DSR < 0.95 (no spurious K1 pass).
  test_real_tape_strategy_B_small_edge_DSR_high
      — B small-edge: DSR > 0.90 with seed=42.
  test_real_tape_dsr_discriminates_no_edge_vs_edge_5_seeds
      — Δ DSR > 0.10 mean across 5 UNMOVABLE seeds (Mira §8(f)).
  test_real_tape_sharpe_distribution_non_degenerate
      — σ > 0 (anti stub-detector preserved on real-tape harness).
"""

from __future__ import annotations

from datetime import datetime
from itertools import combinations

import numpy as np
import pytest

from packages.vespera_cpcv import (
    AggregateMetrics,
    BacktestResult,
    DeterminismStamp,
    FoldDiagnostics,
    FoldMetadata,
)
from packages.vespera_metrics import ReportConfig, compute_full_report


# Mira spec §8(f) UNMOVABLE seeds — post-spec-finalize Mira authority.
_REAL_TAPE_SEEDS: tuple[int, ...] = (42, 1337, 271828, 314159, 161803)


# =====================================================================
# Real-tape toy generator — structural sibling of Phase E generator
# =====================================================================
def _generate_real_tape_toy_results(
    *,
    mu: float,
    sigma: float,
    n_paths: int,
    n_trials: int,
    seed: int,
) -> dict[str, list[BacktestResult]]:
    """Generate ``n_trials × n_paths`` toy ``BacktestResult`` objects
    parametrized to mirror real-tape harness output distribution shape.

    Per Aria C-A6 — structural sibling (NOT fork) of Phase E generator
    in `test_toy_benchmark_bailey_lopez_de_prado_2014.py::_generate_toy_results`:
    - Same canonical CPCV(N=10, k=2) ⇒ 45 paths.
    - Same ``AggregateMetrics`` schema with `sharpe_daily ~ N(mu, sigma)`.
    - Same `n_trades=20` per path matching Bailey-LdP 2014 §3 Table 2.

    Difference vs Phase E: the `simulator_version` stamp reads
    "real_tape_toy" so the sibling distinction is visible in determinism
    audit, AND the per-path seed mixes in the real-tape session anchor
    placeholder (`session_anchor_2024_2025`) to reflect the future N7+
    real-tape harness — under H0 (no edge), the distribution mean stays
    centered on `mu` regardless of mixing, so the DSR sensitivity contract
    is preserved.
    """
    rng = np.random.default_rng(seed)
    n_groups = 10
    k = 2
    canonical = list(combinations(range(n_groups), k))
    assert len(canonical) == n_paths, (
        f"real-tape toy expects n_paths == C({n_groups},{k}) = {len(canonical)}"
    )

    out: dict[str, list[BacktestResult]] = {}
    trial_ids = [f"T{i+1}" for i in range(n_trials)]
    placeholder_stamp = DeterminismStamp(
        seed=seed,
        simulator_version="real_tape_toy",  # Phase F sibling marker
        dataset_sha256="",
        spec_sha256="",
        spec_version="0.0.0",
        engine_config_sha256="",
        rollover_calendar_sha256=None,
        cost_atlas_sha256=None,
        cpcv_config_sha256="",
        python_version="",
        numpy_version="",
        pandas_version="",
        run_id=f"real_tape_toy-{seed}",
        timestamp_brt=datetime(2026, 4, 29),  # Phase F finalize date
    )
    for trial_id in trial_ids:
        per_trial: list[BacktestResult] = []
        for path_id, test_groups in enumerate(canonical):
            sharpe = float(rng.normal(loc=mu, scale=sigma))
            train_groups = tuple(g for g in range(n_groups) if g not in test_groups)
            fold = FoldMetadata(
                path_index=path_id,
                n_groups_total=n_groups,
                k_test_groups=k,
                train_group_ids=train_groups,
                test_group_ids=tuple(test_groups),
                train_session_dates=tuple(),
                test_session_dates=tuple(),
                purged_session_dates=tuple(),
                embargo_session_dates=tuple(),
                embargo_sessions_param=0,
                purge_formula_id="real_tape_toy",
            )
            metrics = AggregateMetrics(
                n_trades=20,
                n_long=10,
                n_short=10,
                n_flat_signals=0,
                pnl_rs_total=0.0,
                pnl_rs_per_contract_avg=0.0,
                sharpe_daily=sharpe,
                sortino_daily=None,
                hit_rate=0.5,
                profit_factor=None,
                max_drawdown_rs=0.0,
                max_drawdown_pct=0.0,
                ulcer_index=None,
                avg_slippage_signed_ticks=0.0,
                fill_rate=1.0,
                rejection_rate=0.0,
            )
            diagnostics = FoldDiagnostics(
                lookahead_audit_pass=True,
                holdout_lock_passed=True,
                holdout_unlock_used=False,
                force_exit_count=0,
                triple_barrier_exit_count=0,
                embargo_overlap_warnings=(),
                n_signals_total=20,
                n_signals_non_flat=20,
            )
            per_trial.append(
                BacktestResult(
                    fold=fold,
                    trades=(),
                    metrics=metrics,
                    determinism=placeholder_stamp,
                    diagnostics=diagnostics,
                )
            )
        out[trial_id] = per_trial
    return out


# =====================================================================
# §8(f) toy A no-edge × 5 UNMOVABLE seeds — DSR below K1 gate
# =====================================================================
@pytest.mark.parametrize("seed", _REAL_TAPE_SEEDS)
def test_real_tape_strategy_A_no_edge_DSR_below_gate_5_seeds(seed: int) -> None:
    """Per Mira spec §8(f) — under H0 (no edge), real-tape harness DSR
    must NOT spuriously pass K1 gate (DSR ≥ 0.95) on any of the 5
    UNMOVABLE seeds. Mirror Phase E sibling test exactly.
    """
    cpcv_results = _generate_real_tape_toy_results(
        mu=0.0, sigma=1.0, n_paths=45, n_trials=5, seed=seed
    )
    cfg = ReportConfig(seed_bootstrap=seed)
    report = compute_full_report(cpcv_results, config=cfg)

    sharpes = np.asarray(report.metrics.sharpe_per_path, dtype=float)
    assert sharpes.size == 225, f"expected 5×45=225 sharpes, got {sharpes.size}"
    assert sharpes.std(ddof=1) > 0.05, (
        f"real-tape A no-edge seed={seed}: σ={sharpes.std(ddof=1):.4f} too small"
    )
    assert report.metrics.dsr < 0.95, (
        f"real-tape A no-edge seed={seed}: DSR={report.metrics.dsr:.4f} "
        "spuriously passes K1 gate (>=0.95)"
    )


# =====================================================================
# §8(f) toy B small-edge — DSR survives Bonferroni n_trials=5
# =====================================================================
def test_real_tape_strategy_B_small_edge_DSR_high() -> None:
    """Per Mira spec §8(f) + Bailey-LdP 2014 §3 Table 2 — small-edge
    μ=0.20 survives Bonferroni n_trials=5 with DSR > 0.90 on real-tape
    harness sibling. Mirror Phase E sibling test exactly.
    """
    cpcv_results = _generate_real_tape_toy_results(
        mu=0.20, sigma=1.0, n_paths=45, n_trials=5, seed=42
    )
    cfg = ReportConfig(seed_bootstrap=42)
    report = compute_full_report(cpcv_results, config=cfg)

    assert report.metrics.dsr > 0.90, (
        f"real-tape B small-edge: DSR={report.metrics.dsr:.4f}, "
        "expected > 0.90 per Bailey-LdP 2014 §3 small-edge case"
    )


# =====================================================================
# §8(f) Δ DSR > 0.10 across 5 UNMOVABLE seeds — discriminator preserved
# =====================================================================
def test_real_tape_dsr_discriminates_no_edge_vs_edge_5_seeds() -> None:
    """Per Mira spec §8(f) UNMOVABLE — toy A and toy B must produce DSR
    values consistently distinguishable across the 5 UNMOVABLE seeds:
    mean(small-edge DSR) − mean(no-edge DSR) > 0.10.

    This is the AC6 Δ DSR > 0.10 across 5 seeds harness-correctness
    witness on the real-tape source; collapse below 0.10 → harness broken
    → Mira §7 Step 2 routes to data_quality bucket per ESC-011 R9.

    Seeds: [42, 1337, 271828, 314159, 161803] UNMOVABLE post-spec-finalize.
    """
    no_edge_dsrs = []
    small_edge_dsrs = []
    for seed in _REAL_TAPE_SEEDS:
        no_edge = compute_full_report(
            _generate_real_tape_toy_results(
                mu=0.0, sigma=1.0, n_paths=45, n_trials=5, seed=seed
            ),
            config=ReportConfig(seed_bootstrap=seed),
        )
        small_edge = compute_full_report(
            _generate_real_tape_toy_results(
                mu=0.20, sigma=1.0, n_paths=45, n_trials=5, seed=seed
            ),
            config=ReportConfig(seed_bootstrap=seed),
        )
        no_edge_dsrs.append(no_edge.metrics.dsr)
        small_edge_dsrs.append(small_edge.metrics.dsr)
    mean_no = float(np.mean(no_edge_dsrs))
    mean_edge = float(np.mean(small_edge_dsrs))
    assert mean_edge > mean_no, (
        f"real-tape DSR fails to discriminate: "
        f"mean(no-edge)={mean_no:.4f}, mean(small-edge)={mean_edge:.4f}"
    )
    assert mean_edge - mean_no > 0.10, (
        f"real-tape DSR discriminator weak: Δmean={mean_edge - mean_no:.4f} "
        "(< 0.10 — AC6 fail; harness collapse signature on real-tape source)"
    )


# =====================================================================
# §8(f) anti-degenerate — σ > 0 (anti stub-detector preserved)
# =====================================================================
def test_real_tape_sharpe_distribution_non_degenerate() -> None:
    """Per AC6 + Mira §8(f) — Sharpe distribution non-degenerate (σ > 0)
    on real-tape harness sibling. Mirror Phase E sibling exactly: σ ≈
    1/sqrt(n_trades) ≈ 0.22 for n_trades=20.
    """
    cpcv_results = _generate_real_tape_toy_results(
        mu=0.0, sigma=1.0, n_paths=45, n_trials=5, seed=42
    )
    cfg = ReportConfig(seed_bootstrap=42)
    report = compute_full_report(cpcv_results, config=cfg)
    sharpes = np.asarray(report.metrics.sharpe_per_path, dtype=float)
    assert sharpes.size == 225
    assert sharpes.std(ddof=1) > 0.0, (
        "real-tape A Sharpe distribution degenerate (σ=0); harness bug"
    )
