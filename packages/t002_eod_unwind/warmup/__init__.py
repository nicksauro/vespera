"""Warm-up pre-session infrastructure for T002.

Exports:
- CalendarLoader: reads and validates config/calendar/*.yaml
- ATR20dBuilder: rolls 20-day ATR from trade history
- Percentiles252dBuilder: rolls 252-day percentiles for regime filters
- WarmUpGate: state machine gating any signal emission
"""

from packages.t002_eod_unwind.warmup.calendar_loader import (
    CalendarLoader,
    CalendarData,
)
from packages.t002_eod_unwind.warmup.atr_20d_builder import (
    ATR20dBuilder,
    ATR20dState,
)
from packages.t002_eod_unwind.warmup.percentiles_252d_builder import (
    Percentiles252dBuilder,
    Percentiles252dState,
)
from packages.t002_eod_unwind.warmup.gate import (
    WarmUpGate,
    WarmUpStatus,
)

__all__ = [
    "CalendarLoader",
    "CalendarData",
    "ATR20dBuilder",
    "ATR20dState",
    "Percentiles252dBuilder",
    "Percentiles252dState",
    "WarmUpGate",
    "WarmUpStatus",
]
