"""Warm-up gate — fail-closed state machine.

No signal can be emitted unless status == READY_TO_TRADE. Corrupt state
files, missing history, or exceptions during load all collapse to
WARM_UP_FAILED (never propagates an exception out of check()).

Design reference:
- docs/architecture/T002-end-of-day-inventory-unwind-design.md §3.3
- Story T002.1 AC5, AC6
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class WarmUpStatus(str, Enum):
    READY_TO_TRADE = "READY_TO_TRADE"
    WARM_UP_IN_PROGRESS = "WARM_UP_IN_PROGRESS"
    WARM_UP_FAILED = "WARM_UP_FAILED"


@dataclass(frozen=True)
class GateCheckResult:
    status: WarmUpStatus
    reason: str
    atr_file_ok: bool
    percentiles_file_ok: bool


class WarmUpGate:
    """Checks that warm-up state files exist, parse, and match as_of_date.

    Fail-closed contract:
    - Missing file       -> WARM_UP_IN_PROGRESS (builder not yet run)
    - Corrupt JSON       -> WARM_UP_FAILED
    - Date mismatch      -> WARM_UP_FAILED
    - Unexpected error   -> WARM_UP_FAILED (never raises)
    """

    def __init__(self, atr_path: Path, percentiles_path: Path) -> None:
        self._atr_path = atr_path
        self._percentiles_path = percentiles_path

    def check(self, as_of_date: date) -> GateCheckResult:
        atr_ok, atr_reason = self._check_file(self._atr_path, as_of_date)
        pct_ok, pct_reason = self._check_file(self._percentiles_path, as_of_date)

        if atr_ok and pct_ok:
            return GateCheckResult(
                status=WarmUpStatus.READY_TO_TRADE,
                reason="all state files valid and current",
                atr_file_ok=True,
                percentiles_file_ok=True,
            )

        if atr_reason == "missing" and pct_reason == "missing":
            return GateCheckResult(
                status=WarmUpStatus.WARM_UP_IN_PROGRESS,
                reason="state files not yet produced",
                atr_file_ok=False,
                percentiles_file_ok=False,
            )

        reasons = []
        if not atr_ok:
            reasons.append(f"atr: {atr_reason}")
        if not pct_ok:
            reasons.append(f"percentiles: {pct_reason}")

        return GateCheckResult(
            status=WarmUpStatus.WARM_UP_FAILED,
            reason="; ".join(reasons),
            atr_file_ok=atr_ok,
            percentiles_file_ok=pct_ok,
        )

    @staticmethod
    def _check_file(path: Path, expected_date: date) -> tuple[bool, str]:
        if not path.exists():
            return False, "missing"
        try:
            with path.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            logger.warning("corrupt warm-up file %s: %s", path, exc)
            return False, "corrupt JSON"
        except OSError as exc:
            logger.warning("cannot read warm-up file %s: %s", path, exc)
            return False, f"read error ({exc.__class__.__name__})"

        file_date_raw = data.get("as_of_date")
        if not isinstance(file_date_raw, str):
            return False, "missing as_of_date field"
        try:
            file_date = date.fromisoformat(file_date_raw)
        except ValueError:
            return False, f"invalid as_of_date: {file_date_raw!r}"
        if file_date != expected_date:
            return False, f"stale as_of_date (file={file_date}, expected={expected_date})"
        return True, "ok"
