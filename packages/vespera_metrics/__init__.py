"""vespera_metrics — canonical metrics module for T002 CPCV reports.

Implements the contract defined in:
- docs/ml/specs/T002-vespera-metrics-spec.md (Mira, AC0 gate)
- docs/stories/T002.0d.story.md

All formulas trace to canonical references (Article IV — No Invention):
- IC Spearman: AFML Ch.8 §8.4.1
- Bootstrap CI: Efron 1979
- Sharpe: Sharpe 1966; AFML Ch.14
- DSR: Bailey & Lopez de Prado 2014 (J. Portfolio Mgmt. 40(5):94-107)
- PBO: Bailey, Borwein, Lopez de Prado, Zhu 2014 (CSCV); AFML Ch.11 §11.5
- Sortino: Sortino & van der Meer 1991
- Max Drawdown / MAR: Young 1991; Schwager 1989
- Ulcer Index: Martin 1989

All functions are pure (zero I/O, zero logging, zero global state).
Bootstrap uses numpy.random.Generator(PCG64) with explicit seed.
"""

from packages.vespera_metrics.info_coef import ic_spearman, bootstrap_ci
from packages.vespera_metrics.sharpe import sharpe_ratio, sharpe_distribution
from packages.vespera_metrics.dsr import deflated_sharpe_ratio
from packages.vespera_metrics.pbo import probability_backtest_overfitting
from packages.vespera_metrics.drawdown import max_drawdown, mar_ratio, ulcer_index
from packages.vespera_metrics.trade_stats import (
    sortino_ratio,
    hit_rate,
    profit_factor,
)
from packages.vespera_metrics.report import (
    MetricsResult,
    FullReport,
    KillDecision,
    ReportConfig,
    compute_full_report,
    evaluate_kill_criteria,
    ICStatus,
    InvalidVerdictReport,
)
from packages.vespera_metrics.research_log import (
    DEFAULT_RESEARCH_LOG,
    read_research_log_cumulative,
)
# T002.6 F2-T1 — IC pipeline orchestrator (Aria Option D — separate
# submodule decoupled from cpcv_harness and report.py per Mira spec §15.2).
from packages.vespera_metrics.cpcv_aggregator import (
    ICAggregateResult,
    compute_ic_from_cpcv_results,
)

__all__ = [
    "ic_spearman",
    "bootstrap_ci",
    "sharpe_ratio",
    "sharpe_distribution",
    "deflated_sharpe_ratio",
    "probability_backtest_overfitting",
    "max_drawdown",
    "mar_ratio",
    "ulcer_index",
    "sortino_ratio",
    "hit_rate",
    "profit_factor",
    "MetricsResult",
    "FullReport",
    "KillDecision",
    "ReportConfig",
    "compute_full_report",
    "evaluate_kill_criteria",
    "ICStatus",
    "InvalidVerdictReport",
    "ICAggregateResult",
    "compute_ic_from_cpcv_results",
    "read_research_log_cumulative",
    "DEFAULT_RESEARCH_LOG",
]
