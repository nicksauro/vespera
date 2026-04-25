"""API surface check (AC1) — verify imports + signatures match spec §1.

Module structure mirrors spec §1.1 dataclass + per-metric submodules.
"""
from __future__ import annotations

import inspect

import pytest


def test_imports_succeed():
    from packages.vespera_metrics import (  # noqa: F401
        FullReport,
        KillDecision,
        MetricsResult,
        bootstrap_ci,
        deflated_sharpe_ratio,
        evaluate_kill_criteria,
        hit_rate,
        ic_spearman,
        mar_ratio,
        max_drawdown,
        probability_backtest_overfitting,
        profit_factor,
        sharpe_distribution,
        sharpe_ratio,
        sortino_ratio,
        ulcer_index,
    )


def test_dataclass_frozen():
    from packages.vespera_metrics import KillDecision

    # Frozen dataclasses raise on attribute set.
    kd = KillDecision(
        verdict="GO",
        reasons=(),
        k1_dsr_passed=True,
        k2_pbo_passed=True,
        k3_ic_decay_passed=True,
    )
    with pytest.raises((AttributeError, Exception)):
        kd.verdict = "NO_GO"


@pytest.mark.parametrize(
    "func_path, expected_param_names",
    [
        ("packages.vespera_metrics.info_coef.ic_spearman", ["predictions", "labels"]),
        (
            "packages.vespera_metrics.info_coef.bootstrap_ci",
            ["sample", "statistic", "n_resamples", "confidence", "seed"],
        ),
        (
            "packages.vespera_metrics.sharpe.sharpe_ratio",
            ["returns", "freq", "rf"],
        ),
        (
            "packages.vespera_metrics.dsr.deflated_sharpe_ratio",
            ["sr_observed", "sr_distribution", "n_trials", "skew", "kurt", "sample_length"],
        ),
        (
            "packages.vespera_metrics.pbo.probability_backtest_overfitting",
            ["cv_results_matrix", "statistic"],
        ),
        ("packages.vespera_metrics.drawdown.max_drawdown", ["equity"]),
        ("packages.vespera_metrics.drawdown.mar_ratio", ["cagr", "max_dd"]),
        ("packages.vespera_metrics.drawdown.ulcer_index", ["equity"]),
        (
            "packages.vespera_metrics.trade_stats.sortino_ratio",
            ["returns", "freq", "target"],
        ),
        ("packages.vespera_metrics.trade_stats.hit_rate", ["trades_pnl"]),
        ("packages.vespera_metrics.trade_stats.profit_factor", ["trades_pnl"]),
    ],
)
def test_function_signatures(func_path, expected_param_names):
    mod_path, _, fn_name = func_path.rpartition(".")
    import importlib

    mod = importlib.import_module(mod_path)
    fn = getattr(mod, fn_name)
    params = list(inspect.signature(fn).parameters.keys())
    assert params == expected_param_names, (
        f"{func_path} signature mismatch: got {params}, expected {expected_param_names}"
    )


def test_to_markdown_exists():
    from packages.vespera_metrics import FullReport

    assert hasattr(FullReport, "to_markdown")
    assert callable(FullReport.to_markdown)
