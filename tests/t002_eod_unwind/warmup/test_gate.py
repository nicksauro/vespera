"""Tests for WarmUpGate.

AC5: 3-state machine.
AC6: fail-closed — corrupt/missing/stale files collapse to safe states,
     check() never raises.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path


from packages.t002_eod_unwind.warmup.gate import (
    WarmUpGate,
    WarmUpStatus,
)


def _write_state(path: Path, as_of: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"as_of_date": as_of, "payload": "..."}), encoding="utf-8")


def test_both_files_valid_returns_ready(tmp_path: Path) -> None:
    atr = tmp_path / "atr.json"
    pct = tmp_path / "pct.json"
    _write_state(atr, "2024-03-15")
    _write_state(pct, "2024-03-15")
    gate = WarmUpGate(atr, pct)
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.READY_TO_TRADE
    assert result.atr_file_ok
    assert result.percentiles_file_ok


def test_both_files_missing_returns_in_progress(tmp_path: Path) -> None:
    gate = WarmUpGate(tmp_path / "atr.json", tmp_path / "pct.json")
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.WARM_UP_IN_PROGRESS


def test_only_atr_missing_returns_failed(tmp_path: Path) -> None:
    atr = tmp_path / "atr.json"
    pct = tmp_path / "pct.json"
    _write_state(pct, "2024-03-15")
    gate = WarmUpGate(atr, pct)
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.WARM_UP_FAILED


def test_corrupt_atr_returns_failed(tmp_path: Path) -> None:
    atr = tmp_path / "atr.json"
    pct = tmp_path / "pct.json"
    atr.write_text("not-json{{{", encoding="utf-8")
    _write_state(pct, "2024-03-15")
    gate = WarmUpGate(atr, pct)
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.WARM_UP_FAILED
    assert "corrupt JSON" in result.reason


def test_stale_as_of_returns_failed(tmp_path: Path) -> None:
    atr = tmp_path / "atr.json"
    pct = tmp_path / "pct.json"
    _write_state(atr, "2024-03-14")  # yesterday — stale
    _write_state(pct, "2024-03-15")
    gate = WarmUpGate(atr, pct)
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.WARM_UP_FAILED
    assert "stale" in result.reason


def test_missing_as_of_field_returns_failed(tmp_path: Path) -> None:
    atr = tmp_path / "atr.json"
    pct = tmp_path / "pct.json"
    atr.write_text(json.dumps({"payload": "..."}), encoding="utf-8")
    _write_state(pct, "2024-03-15")
    gate = WarmUpGate(atr, pct)
    result = gate.check(as_of_date=date(2024, 3, 15))
    assert result.status == WarmUpStatus.WARM_UP_FAILED


def test_check_never_raises_on_bad_inputs(tmp_path: Path) -> None:
    """Fail-closed contract: no exception escapes check()."""
    gate = WarmUpGate(tmp_path / "a.json", tmp_path / "b.json")
    # should not raise
    _ = gate.check(as_of_date=date(2024, 3, 15))
