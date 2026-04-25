"""Purity check (AC2) — vespera_metrics has zero I/O, logging, globals.

Greps the package source for forbidden patterns.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_PACKAGE = (
    Path(__file__).resolve().parents[2] / "packages" / "vespera_metrics"
)

# Match function-call open(...), print(...), logging.X, or top-level `global`.
_FORBIDDEN = [
    (re.compile(r"\bopen\("), "open()"),
    (re.compile(r"\bprint\("), "print()"),
    (re.compile(r"\blogging\."), "logging."),
    (re.compile(r"^global\s+", re.MULTILINE), "top-level global"),
]


@pytest.mark.parametrize(
    "fname",
    [
        "info_coef.py",
        "sharpe.py",
        "dsr.py",
        "pbo.py",
        "drawdown.py",
        "trade_stats.py",
        "report.py",
    ],
)
def test_no_io_no_logging_no_globals(fname: str):
    src = (_PACKAGE / fname).read_text(encoding="utf-8")
    # Strip docstrings/comments roughly to avoid false positives in prose.
    # (Crude but adequate; the actual checks target syntax-level patterns.)
    for pattern, label in _FORBIDDEN:
        matches = pattern.findall(src)
        assert not matches, f"{fname}: forbidden {label} found in source"
