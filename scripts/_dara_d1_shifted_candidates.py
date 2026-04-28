"""Compute D1-shifted as_of candidates from calendar + manifest bounds.

Walks the calendar to find the earliest as_of in the in_sample window
(2024-07-01..2025-06-30) such that ``compute_window`` returns a window_start
>= 2024-01-02 (manifest earliest).

Output: list of viable as_of dates with their (window_start, window_end)
spans for the council to evaluate.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from packages.t002_eod_unwind.warmup.calendar_loader import CalendarLoader
from packages.t002_eod_unwind.warmup.orchestrator import (
    WARMUP_VALID_DAYS_REQUIRED,
    compute_window,
    InsufficientCoverage,
)


CALENDAR_PATH = REPO_ROOT / "config" / "calendar" / "2024-2027.yaml"
MANIFEST_EARLIEST = date(2024, 1, 2)
IN_SAMPLE_START = date(2024, 7, 1)
IN_SAMPLE_END = date(2025, 6, 30)
MANIFEST_LATEST = date(2025, 6, 30)


def main() -> None:
    cal = CalendarLoader.load(CALENDAR_PATH)
    out_lines = [
        f"WARMUP_VALID_DAYS_REQUIRED = {WARMUP_VALID_DAYS_REQUIRED}",
        f"manifest_earliest = {MANIFEST_EARLIEST.isoformat()} (2024-01-02 wdo-2024-01.parquet)",
        f"manifest_latest   = {MANIFEST_LATEST.isoformat()} (2025-06-30 wdo-2025-06.parquet)",
        f"in_sample range   = [{IN_SAMPLE_START.isoformat()}, {IN_SAMPLE_END.isoformat()}]",
        "",
        f"{'as_of':<12} {'valid?':<7} {'window_start':<14} {'window_end':<14} {'notes'}",
        "-" * 90,
    ]

    # Iterate through every valid sample day in the in_sample window.
    cur = IN_SAMPLE_START
    n_emitted = 0
    n_total = 0
    first_viable: date | None = None
    while cur <= IN_SAMPLE_END:
        if cal.is_valid_sample_day(cur):
            n_total += 1
            try:
                ws, we = compute_window(cur, cal)
            except InsufficientCoverage as exc:
                out_lines.append(f"{cur.isoformat():<12} NO     -            -            calendar buffer too small: {exc}")
            else:
                manifest_ok = ws >= MANIFEST_EARLIEST and we <= MANIFEST_LATEST
                if manifest_ok:
                    if first_viable is None:
                        first_viable = cur
                    if n_emitted < 10 or cur in (
                        date(2024, 7, 1), date(2024, 8, 1), date(2024, 8, 15),
                        date(2024, 8, 30), date(2024, 9, 30), date(2024, 12, 30),
                        date(2025, 3, 31), date(2025, 5, 30), date(2025, 6, 30),
                    ):
                        notes = ""
                        if cur == first_viable:
                            notes = "<-- EARLIEST viable as_of"
                        out_lines.append(
                            f"{cur.isoformat():<12} YES    {ws.isoformat():<14}{we.isoformat():<14}{notes}"
                        )
                        n_emitted += 1
                else:
                    if n_emitted < 5:
                        out_lines.append(
                            f"{cur.isoformat():<12} NO     {ws.isoformat():<14}{we.isoformat():<14}window outside manifest [{MANIFEST_EARLIEST}, {MANIFEST_LATEST}]"
                        )
                        n_emitted += 1
        cur += timedelta(days=1)

    out_lines.append("")
    out_lines.append(f"Total valid sample days in in_sample range: {n_total}")
    out_lines.append(f"First viable D1-shifted as_of: {first_viable.isoformat() if first_viable else 'NONE'}")

    target = REPO_ROOT / "state" / "T002" / "_dara_d1_candidates.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"WROTE {target} ({len(out_lines)} lines)")
    # Also dump to stdout so we can see it.
    print("\n".join(out_lines))


if __name__ == "__main__":
    main()
