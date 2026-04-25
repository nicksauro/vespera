"""Warm-up pre-session infrastructure for T002.

Exports:
- CalendarLoader: reads and validates config/calendar/*.yaml
- ATR20dBuilder: rolls 20-day ATR from trade history
- Percentiles126dBuilder: rolls 126-day percentiles for regime filters
- WarmUpGate: state machine gating any signal emission
"""

from packages.t002_eod_unwind.warmup.calendar_loader import (
    CalendarLoader,
    CalendarData,
)
from packages.t002_eod_unwind.warmup.atr_20d_builder import (
    ATR20dBuilder,
    ATR20dState,
    Trade,
    DailyOHLC,
)
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    Percentiles126dBuilder,
    Percentiles126dState,
    DailyMetrics,
    PercentileBands,
)
from packages.t002_eod_unwind.warmup.gate import (
    WarmUpGate,
    WarmUpStatus,
    GateCheckResult,
)

__all__ = [
    "CalendarLoader",
    "CalendarData",
    "ATR20dBuilder",
    "ATR20dState",
    "Trade",
    "DailyOHLC",
    "Percentiles126dBuilder",
    "Percentiles126dState",
    "DailyMetrics",
    "PercentileBands",
    "WarmUpGate",
    "WarmUpStatus",
    "GateCheckResult",
]
