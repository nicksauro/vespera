"""FeatureComputer — layer 3 of T002.

Pure function that maps (SessionSnapshot, atr_20d, percentile bands) →
the 3 canonical features of the thesis:

  intraday_flow_direction = sign(close[t] - open_day)
  intraday_flow_magnitude = |close[t] - open_day| / ATR_20d
  atr_day_ratio           = ATR_day / ATR_20d

where `ATR_day` is computed online from session high/low of the current
session (conservative proxy: true_range with no prior close reference —
but here we only have today, so ATR_day = high - low).

Edge cases are folded into `Features.flags` (frozenset of strings) —
NEVER crashes. See AC4, AC5.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime

from .session_state import SessionSnapshot


@dataclass(frozen=True)
class PercentileBands:
    """Rolling 252d bands injected by the caller (from Percentiles252dState)."""

    p20: float
    p60: float
    p80: float


@dataclass(frozen=True)
class Features:
    """Immutable output of FeatureComputer.

    `flags` carries edge-case signals (e.g. ``regime_atr_undefined``) that
    downstream signal rule MUST consume to decide FLAT.
    """

    entry_ts: datetime
    intraday_flow_direction: int  # -1 | 0 | 1
    intraday_flow_magnitude: float  # >= 0, may be +inf
    atr_day_ratio: float  # >= 0, may be +inf
    flags: frozenset[str] = field(default_factory=frozenset)


def _sign(x: float) -> int:
    if x > 0.0:
        return 1
    if x < 0.0:
        return -1
    return 0


def compute_features(
    snapshot: SessionSnapshot,
    atr_20d: float,
    magnitude_bands: PercentileBands,  # reserved for downstream; not used here
    atr_ratio_bands: PercentileBands,  # reserved for downstream; not used here
) -> Features:
    """Compute the 3 features deterministically.

    AC3: pure, no side effects.
    AC4: direction ∈ {-1, 0, 1} (0 when close == open_day exactly).
    AC5: atr_20d == 0 ⇒ magnitude = +inf AND flag regime_atr_undefined; never raises.

    Args:
      snapshot: SessionSnapshot from SessionState.snapshot_at(entry_ts)
      atr_20d: scalar ATR over last 20 business days (from warmup)
      magnitude_bands: P20/P60/P80 for magnitude (reserved, validated shape)
      atr_ratio_bands: P20/P60/P80 for atr_day_ratio (reserved, validated shape)
    """
    _ = magnitude_bands  # injected for contract, unused here — consumed by signal_rule
    _ = atr_ratio_bands

    diff = snapshot.close_at_ts - snapshot.open_day
    direction = _sign(diff)

    flags: set[str] = set()

    if atr_20d == 0.0:
        magnitude = math.inf
        atr_day_ratio = math.inf
        flags.add("regime_atr_undefined")
    elif atr_20d < 0.0:
        # Defensive: ATR can never be negative. Flag and treat as undefined.
        magnitude = math.inf
        atr_day_ratio = math.inf
        flags.add("regime_atr_undefined")
    else:
        magnitude = abs(diff) / atr_20d
        atr_day = snapshot.session_high - snapshot.session_low
        atr_day_ratio = atr_day / atr_20d

    return Features(
        entry_ts=snapshot.as_of_ts,
        intraday_flow_direction=direction,
        intraday_flow_magnitude=magnitude,
        atr_day_ratio=atr_day_ratio,
        flags=frozenset(flags),
    )
