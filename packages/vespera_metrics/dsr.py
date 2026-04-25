"""Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014).

"The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest
Overfitting, and Non-Normality", J. Portfolio Mgmt. 40(5):94-107.

Equation (10) of the paper:

    SR_0 = sqrt(Var(SR_dist)) ×
           ( (1 - γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)) )

    DSR = Φ( (SR_obs - SR_0) × sqrt(T - 1)
             / sqrt(1 - skew·SR_obs + ((kurt - 1)/4)·SR_obs²) )

where γ = Euler-Mascheroni constant ≈ 0.5772, Φ is the standard normal
CDF, N is the number of trials and T is the sample length.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

# Euler-Mascheroni constant (Bailey-LdP 2014 eq. 10).
_GAMMA = 0.5772156649015329


def deflated_sharpe_ratio(
    sr_observed: float,
    sr_distribution: np.ndarray,
    n_trials: int,
    skew: float = 0.0,
    kurt: float = 3.0,
    sample_length: int = 252,
) -> float:
    """Deflated Sharpe Ratio per Bailey-LdP 2014 eq. (10).

    Args:
        sr_observed: observed annualised Sharpe of the selected strategy.
        sr_distribution: array of Sharpes from the N trials (used for
            Var(SR_dist)).
        n_trials: number of independent trials (selection bias source).
        skew: skewness of the per-period return distribution (default 0).
        kurt: kurtosis (NOT excess); default 3 = normal.
        sample_length: number of periods T.

    Edge cases (per spec §5.3):
        n_trials <= 1                                → ValueError
        Var(sr_distribution) == 0                    → SR_0 = 0 (warn upstream)
        1 - skew·SR + ((kurt-1)/4)·SR² <= 0          → ValueError
        kurt < 1                                     → ValueError
        sample_length < 2                            → ValueError
    """
    if n_trials <= 1:
        raise ValueError("DSR requires N >= 2 trials")
    if sample_length < 2:
        raise ValueError("DSR requires sample_length >= 2")
    if kurt < 1.0:
        raise ValueError("kurtosis must be >= 1")

    sr_dist = np.asarray(sr_distribution, dtype=float)
    if sr_dist.ndim != 1 or sr_dist.size < 2:
        raise ValueError("sr_distribution must be 1-dim with >= 2 entries")
    if np.isnan(sr_dist).any():
        raise ValueError("NaN in sr_distribution — clean upstream")

    var_sr = float(np.var(sr_dist, ddof=1))
    sigma_sr = math.sqrt(var_sr) if var_sr > 0 else 0.0

    # Bailey-LdP eq. (10): expected max under selection bias.
    n = n_trials
    phi_inv_1 = float(stats.norm.ppf(1.0 - 1.0 / n))
    phi_inv_2 = float(stats.norm.ppf(1.0 - 1.0 / (n * math.e)))
    sr_0 = sigma_sr * ((1.0 - _GAMMA) * phi_inv_1 + _GAMMA * phi_inv_2)

    denom_inside = 1.0 - skew * sr_observed + ((kurt - 1.0) / 4.0) * sr_observed ** 2
    if denom_inside <= 0.0:
        raise ValueError(
            "DSR denominator non-positive: "
            f"1 - skew·SR + ((kurt-1)/4)·SR² = {denom_inside}"
        )
    denom = math.sqrt(denom_inside)

    z = (sr_observed - sr_0) * math.sqrt(sample_length - 1) / denom
    return float(stats.norm.cdf(z))
