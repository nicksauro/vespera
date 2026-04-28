"""Warm-up pre-session infrastructure for T002.

Exports:
- CalendarLoader: reads and validates config/calendar/*.yaml
- ATR20dBuilder: rolls 20-day ATR from trade history
- Percentiles126dBuilder: rolls 126-day percentiles for regime filters
- WarmUpGate: state machine gating any signal emission
- BUILDER_VERSION: semver string for warmup builder logic (cache key
  component per AC9 / ESC-006 mini-council 4/4 APPROVE_F).

T002.0h AC9 cache validation contract (mini-council 4/4 CONVERGENT):
    Triple-key cache: ``(as_of_date, source_sha256_from_manifest,
    builder_version_semver)``. ``BUILDER_VERSION`` MUST be incremented
    whenever the warmup builder logic changes (atr_20d_builder.py or
    percentiles_126d_builder.py). The CLI ``scripts/run_warmup_state.py``
    enforces fail-closed cache validation against this constant.
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

# T002.0h AC9 — semver for the builder logic surface area. Mini-council
# 4/4 APPROVE_F: "BUILDER_VERSION = '1.0.0' em warmup/__init__.py —
# simpler, testable, R15-clean". Bump MAJOR on breaking change to
# ATR20dState / Percentiles126dState schema; bump MINOR on new builder
# fields; bump PATCH on bug-fix that changes computed values.
BUILDER_VERSION: str = "1.0.0"

__all__ = [
    "BUILDER_VERSION",
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
