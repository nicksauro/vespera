"""MetricsResult / FullReport / KillDecision dataclasses + kill criteria wiring.

Schema source: docs/ml/specs/T002-vespera-metrics-spec.md §1.
Kill criteria source: thesis §5 (K1: DSR>0, K2: PBO<0.4, K3: IC decay).

Note: `compute_full_report` integration (consuming list[BacktestResult] from
T002.0c CPCVEngine) is gated on T002.0c interface stability. This module
ships the dataclasses and `evaluate_kill_criteria` (AC14); the integration
glue (AC12 / AC12.1 / AC13) lands when T002.0c BacktestResult interface is
frozen — tracked in story T002.0d Tasks T4/T5.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np


@dataclass(frozen=True)
class MetricsResult:
    # ---- Primary (spec L160-163) ----
    ic_spearman: float
    ic_spearman_ci95: Tuple[float, float]
    dsr: float
    pbo: float

    # ---- Secondary (spec L164-172) ----
    sharpe_per_path: np.ndarray
    sharpe_mean: float
    sharpe_median: float
    sharpe_std: float
    sortino: float
    mar: float
    ulcer_index: float
    max_drawdown: float
    profit_factor: float
    hit_rate: float

    # ---- Provenance (auditoria, traceability) ----
    n_paths: int
    n_trials_used: int
    n_trials_source: str          # "docs/ml/research-log.md@<git-sha>"
    seed_bootstrap: int
    spec_version: str             # "T002-v0.2.0"
    computed_at_brt: str          # ISO timestamp BRT


@dataclass(frozen=True)
class KillDecision:
    verdict: str                  # "GO" | "NO_GO"
    reasons: Tuple[str, ...]
    k1_dsr_passed: bool
    k2_pbo_passed: bool
    k3_ic_decay_passed: bool


@dataclass(frozen=True)
class FullReport:
    metrics: MetricsResult
    per_path_results: tuple        # tuple[BacktestResult, ...] (T002.0c handshake)
    kill_decision: KillDecision

    def to_markdown(self) -> str:
        """Emit T002-cpcv-report.md schema markdown.

        Schema validated by Beckett at AC13 sign-off; this is the canonical
        layout consumed by docs/research/results/T002-cpcv-report.md.
        """
        m = self.metrics
        kd = self.kill_decision
        lines = []
        lines.append("# T002 CPCV Metrics Report")
        lines.append("")
        lines.append(f"- **Spec version:** `{m.spec_version}`")
        lines.append(f"- **Computed (BRT):** `{m.computed_at_brt}`")
        lines.append(f"- **n_paths:** {m.n_paths}")
        lines.append(f"- **n_trials_used:** {m.n_trials_used}")
        lines.append(f"- **n_trials_source:** `{m.n_trials_source}`")
        lines.append(f"- **bootstrap seed:** {m.seed_bootstrap}")
        lines.append("")
        lines.append("## Primary metrics")
        lines.append("")
        lines.append(f"- **IC Spearman (mean):** {m.ic_spearman:.6f}")
        lines.append(
            f"- **IC Spearman 95% CI:** "
            f"[{m.ic_spearman_ci95[0]:.6f}, {m.ic_spearman_ci95[1]:.6f}]"
        )
        lines.append(f"- **Deflated Sharpe Ratio:** {m.dsr:.6f}")
        lines.append(f"- **PBO:** {m.pbo:.6f}")
        lines.append("")
        lines.append("## Secondary metrics (median over paths unless noted)")
        lines.append("")
        lines.append(f"- **Sharpe (mean over paths):** {m.sharpe_mean:.6f}")
        lines.append(f"- **Sharpe (median):** {m.sharpe_median:.6f}")
        lines.append(f"- **Sharpe (std over paths):** {m.sharpe_std:.6f}")
        lines.append(f"- **Sortino:** {m.sortino:.6f}")
        lines.append(f"- **MAR:** {m.mar:.6f}")
        lines.append(f"- **Ulcer Index:** {m.ulcer_index:.6f}")
        lines.append(f"- **Max Drawdown:** {m.max_drawdown:.6f}")
        lines.append(f"- **Profit Factor:** {m.profit_factor:.6f}")
        lines.append(f"- **Hit Rate:** {m.hit_rate:.6f}")
        lines.append("")
        lines.append("## Kill decision")
        lines.append("")
        lines.append(f"- **Verdict:** **{kd.verdict}**")
        lines.append(f"- K1 (DSR>0): {'PASS' if kd.k1_dsr_passed else 'FAIL'}")
        lines.append(f"- K2 (PBO<0.4): {'PASS' if kd.k2_pbo_passed else 'FAIL'}")
        lines.append(
            f"- K3 (IC decay): {'PASS' if kd.k3_ic_decay_passed else 'FAIL'}"
        )
        if kd.reasons:
            lines.append("")
            lines.append("### Reasons")
            for r in kd.reasons:
                lines.append(f"- {r}")
        lines.append("")
        return "\n".join(lines)


def evaluate_kill_criteria(
    dsr: float,
    pbo: float,
    ic_in_sample: float,
    ic_holdout: float,
    thresholds: Optional[dict] = None,
) -> KillDecision:
    """Evaluate K1/K2/K3 kill criteria per thesis §5 (story T002.0d L126-146).

    K1: DSR > 0
    K2: PBO < 0.4
    K3: IC_holdout >= 0.5 × IC_in_sample
        (equivalent: IC has not decayed below half of in-sample value)

    Returns KillDecision with verdict GO (all pass) or NO_GO (any fail).
    """
    if thresholds is None:
        thresholds = {}
    k1_floor = float(thresholds.get("dsr_floor", 0.0))
    k2_ceiling = float(thresholds.get("pbo_ceiling", 0.4))
    k3_decay = float(thresholds.get("ic_decay_floor_ratio", 0.5))

    k1_passed = dsr > k1_floor
    k2_passed = pbo < k2_ceiling

    # K3: avoid sign flips and NaN. If in-sample IC is non-positive, the
    # decay test is degenerate — we treat as failed (no edge to decay from).
    if ic_in_sample <= 0:
        k3_passed = False
    else:
        k3_passed = ic_holdout >= k3_decay * ic_in_sample

    reasons = []
    if not k1_passed:
        reasons.append(f"K1: DSR={dsr:.6f} <= {k1_floor} (kill criterion)")
    if not k2_passed:
        reasons.append(f"K2: PBO={pbo:.6f} >= {k2_ceiling} (kill criterion)")
    if not k3_passed:
        if ic_in_sample <= 0:
            reasons.append(
                f"K3: IC_in_sample={ic_in_sample:.6f} non-positive — no edge"
            )
        else:
            reasons.append(
                f"K3: IC_holdout={ic_holdout:.6f} < "
                f"{k3_decay} × IC_in_sample={ic_in_sample:.6f}"
            )

    verdict = "GO" if (k1_passed and k2_passed and k3_passed) else "NO_GO"
    return KillDecision(
        verdict=verdict,
        reasons=tuple(reasons),
        k1_dsr_passed=k1_passed,
        k2_pbo_passed=k2_passed,
        k3_ic_decay_passed=k3_passed,
    )
