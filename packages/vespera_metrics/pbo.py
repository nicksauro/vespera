"""Probability of Backtest Overfitting (CSCV) per BBLZ 2014.

Bailey, Borwein, Lopez de Prado, Zhu (2014)
"The Probability of Backtest Overfitting" J. Computational Finance.
AFML Ch.11 §11.5 p.156-159.

Convention (LOCKED — Mira-decision, spec §6.4):

    rank_n = ASCENDING rank of R_OOS_t* via scipy.stats.rankdata(method='min').
             rank=1 → t* was WORST OOS; rank=T → t* was BEST OOS.
    w_n    = rank_n / (T + 1)
    λ_n    = log( w_n / (1 - w_n) )
    OVERFIT ⟺ λ_n ≤ 0  ⟺  rank_n ≤ (T+1)/2  (t* below OOS median)

    PBO = #{s : λ_s ≤ 0} / S

Argmax IS tie-breaking: np.argmax (first wins by lowest index) — spec §6.4.
"""
from __future__ import annotations

import math
from itertools import combinations
from typing import Callable

import numpy as np
from scipy import stats


def probability_backtest_overfitting(
    cv_results_matrix: np.ndarray,
    statistic: Callable[[np.ndarray], float] = np.mean,
) -> float:
    """PBO per BBLZ 2014 CSCV.

    Args:
        cv_results_matrix: shape (T, N) — T strategy variants × N folds.
        statistic: aggregator over folds (default mean of fold metrics, e.g. SR).

    Edge cases (per spec §6.3):
        T < 2          → ValueError
        N < 2 or N odd → ValueError (CSCV needs N even for balanced pairs)
        all variants identical → 0.5 by convention
        NaN in input   → ValueError
    """
    m = np.asarray(cv_results_matrix, dtype=float)
    if m.ndim != 2:
        raise ValueError("cv_results_matrix must be 2-dim (T variants × N folds)")
    T, N = m.shape
    if T < 2:
        raise ValueError("PBO requires >= 2 strategy variants (T >= 2)")
    if N < 2 or N % 2 != 0:
        raise ValueError("PBO requires N even and >= 2 (CSCV balanced pairs)")
    if np.isnan(m).any():
        raise ValueError("NaN in cv_results_matrix — clean upstream")

    # All-identical variants → no signal → PBO = 0.5 by convention.
    if np.allclose(m - m[0:1, :], 0.0):
        return 0.5

    folds = list(range(N))
    half = N // 2
    overfit_count = 0
    total = 0

    for is_combo in combinations(folds, half):
        is_idx = list(is_combo)
        oos_idx = [f for f in folds if f not in is_combo]

        # Per-variant aggregate over IS folds and OOS folds.
        r_is = np.array([statistic(m[t, is_idx]) for t in range(T)])
        r_oos = np.array([statistic(m[t, oos_idx]) for t in range(T)])

        # IS winner: argmax with first-wins-by-index (np.argmax default).
        t_star = int(np.argmax(r_is))

        # Ascending rank in OOS, method='min' tie-break.
        ranks_oos = stats.rankdata(r_oos, method="min")
        rank_t_star = float(ranks_oos[t_star])

        w = rank_t_star / (T + 1.0)
        # logit(w); w ∈ (0, 1) strictly because rank ∈ [1, T] and denom T+1.
        lam = math.log(w / (1.0 - w))

        if lam <= 0.0:
            overfit_count += 1
        total += 1

    return overfit_count / total
