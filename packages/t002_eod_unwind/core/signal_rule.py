"""Signal rule — layer 4 of T002.

Pure function that maps Features + trial_id → Signal(direction, reason).

Trials T1..T5 are defined in the spec YAML. The rule itself is agnostic to
WHICH trial — it just consumes the threshold and regime bands that were
selected upstream. The caller (backtest runner / live loop) injects the
correct threshold based on trial_id.

Zero side effects, zero I/O, zero logging.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .feature_computer import Features, PercentileBands


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


@dataclass(frozen=True)
class Signal:
    direction: Direction
    reason: str


@dataclass(frozen=True)
class TrialParams:
    """Params injected per trial. `magnitude_threshold` selects which P of the
    magnitude bands to use (e.g. T1 uses P60; T2 uses P50; T3 uses P70).

    `apply_regime_filter` controls whether atr_day_ratio must lie within
    [atr_ratio_bands.p20, atr_ratio_bands.p80] (T4 disables this).

    `allowed_entry_windows` is a frozenset of "HH:MM" strings; empty = all.
    T5 restricts to {"17:25"}.
    """

    trial_id: str  # "T1".."T5"
    magnitude_threshold: float  # e.g. bands.p60 for T1
    apply_regime_filter: bool = True
    allowed_entry_windows: frozenset[str] = frozenset()  # empty = all 4 windows


def compute_signal(
    features: Features,
    atr_ratio_bands: PercentileBands,
    trial: TrialParams,
) -> Signal:
    """Apply trading rule from spec.

    AC1: pure. AC2: baseline entry = magnitude > P60 AND atr_ratio ∈ [P20, P80]
    ⇒ FADE (direction = -sign(flow_direction)).
    """
    # AC4: atr_undefined edge — never trade
    if "regime_atr_undefined" in features.flags:
        return Signal(Direction.FLAT, "atr_undefined")

    # AC4: flow flat — cannot fade zero
    if features.intraday_flow_direction == 0:
        return Signal(Direction.FLAT, "flow_flat")

    # T5 window restriction
    if trial.allowed_entry_windows:
        hhmm = features.entry_ts.strftime("%H:%M")
        if hhmm not in trial.allowed_entry_windows:
            return Signal(Direction.FLAT, "window_not_in_trial")

    # Magnitude threshold
    if features.intraday_flow_magnitude <= trial.magnitude_threshold:
        return Signal(Direction.FLAT, "magnitude_below_threshold")

    # Regime filter (T4 disables this check)
    if trial.apply_regime_filter:
        if (
            features.atr_day_ratio < atr_ratio_bands.p20
            or features.atr_day_ratio > atr_ratio_bands.p80
        ):
            return Signal(Direction.FLAT, "atr_ratio_outside_regime")

    # FADE: short when flow was up; long when flow was down
    if features.intraday_flow_direction > 0:
        return Signal(Direction.SHORT, "entered_fade_short")
    return Signal(Direction.LONG, "entered_fade_long")
