"""
Telemetry schema for T002.0a G09 materialization wrapper.

Derivation authority: docs/architecture/memory-budget.md Riven Ratification Finding 5
(Option A two-output split). Per-tick CSV is raw audit evidence; per-run summary JSON
is what Riven reads at step 7 to validate ceiling derivation.

Two outputs per baseline run, both named by `--run-id` per ADR-3:

  (a) baseline-telemetry.csv  — one row per polling tick (audit evidence).
  (b) baseline-summary.json   — one record per run (Riven reads at step 7).

The CSV is the source of truth; the JSON is a derived artifact. An auditor can
`pandas.read_csv` + recompute peak/delta/ratio and compare — any mismatch is a
wrapper bug, and the CSV wins because it is the primary observation.
"""
from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal
from pathlib import Path


# --- Normative schemas ------------------------------------------------------

TELEMETRY_CSV_COLUMNS: tuple[str, ...] = (
    "tick_n",              # int, monotonic from 1
    "ts_brt",              # ISO-8601 with -03:00 offset
    "commit_bytes",        # int, psutil child process.memory_info().vms
    "rss_bytes",           # int, psutil child process.memory_info().rss
    "pagefile_alloc_bytes",# int, psutil.swap_memory().used at tick time
    "available_bytes",     # int, psutil.virtual_memory().available at tick time
)

SUMMARY_JSON_FIELDS: tuple[str, ...] = (
    "run_id",                   # str, from --run-id
    "start_ts",                 # ISO-8601 BRT, wrapper launch
    "end_ts",                   # ISO-8601 BRT, child exit (or kill) time
    "duration_s",               # int, end_ts - start_ts in whole seconds
    "peak_commit",              # int bytes, max(commit_bytes) over all ticks
    "peak_rss",                 # int bytes, max(rss_bytes) over all ticks
    "pagefile_alloc_start",     # int bytes, first tick's pagefile_alloc_bytes
    "pagefile_alloc_end",       # int bytes, last tick's pagefile_alloc_bytes
    "delta_pagefile",           # int bytes, pagefile_alloc_end - pagefile_alloc_start
    "ratio_commit_rss",         # float or None, peak_commit / peak_rss rounded to 3 dp
    "tick_count",               # int, total ticks written to CSV
    "exit_code",                # int, child exit code (0 normal, 3 KILL, 4/5 sampler fail)
)


# --- Sample dataclass used by the library at run-time --------------------

@dataclass(frozen=True)
class Sample:
    """One per-tick memory observation. Immutable; passed into telemetry writer."""
    commit_bytes: int
    rss_bytes: int
    pagefile_alloc_bytes: int
    available_bytes: int
    ts_brt: str  # ISO-8601 BRT-naive or BRT-offset; whichever the sampler emits


# --- Writers ----------------------------------------------------------------

def append_tick(csv_path: Path, tick_n: int, sample: Sample) -> None:
    """Append one tick row to `csv_path`.

    Writes the header row first if the file does not exist. Uses UTF-8 + LF
    line endings + no BOM. Flushes after each row so a crash between ticks
    leaves a partial-but-consistent CSV.
    """
    file_exists = csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=TELEMETRY_CSV_COLUMNS, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "tick_n": tick_n,
            "ts_brt": sample.ts_brt,
            "commit_bytes": sample.commit_bytes,
            "rss_bytes": sample.rss_bytes,
            "pagefile_alloc_bytes": sample.pagefile_alloc_bytes,
            "available_bytes": sample.available_bytes,
        })
        fh.flush()


def write_summary(json_path: Path, summary: dict) -> None:
    """Atomic write of per-run summary JSON.

    Validates that every SUMMARY_JSON_FIELDS key is present. Writes to
    `<json_path>.tmp` then `os.replace`s into the final path (crash-safe).
    Uses UTF-8, 2-space indent, trailing newline.
    """
    missing = [f for f in SUMMARY_JSON_FIELDS if f not in summary]
    if missing:
        raise ValueError(
            f"summary JSON missing required fields: {missing}; expected all of {SUMMARY_JSON_FIELDS}"
        )
    # Preserve schema order for readability
    ordered: dict[str, object] = {k: summary[k] for k in SUMMARY_JSON_FIELDS}
    json_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = json_path.with_suffix(json_path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as fh:
        fh.write(json.dumps(ordered, indent=2))
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp_path, json_path)


def compute_ratio(peak_commit: int, peak_rss: int) -> float | None:
    """Return peak_commit / peak_rss rounded half-even to 3 decimals.

    Returns None if peak_rss == 0 (defensive; Riven R1 Signal A guidance).
    """
    if peak_rss == 0:
        return None
    # Use Decimal for deterministic half-even rounding (mirrors spec wording)
    raw = Decimal(peak_commit) / Decimal(peak_rss)
    rounded = raw.quantize(Decimal("0.001"), rounding=ROUND_HALF_EVEN)
    return float(rounded)


__all__ = [
    "TELEMETRY_CSV_COLUMNS",
    "SUMMARY_JSON_FIELDS",
    "Sample",
    "append_tick",
    "write_summary",
    "compute_ratio",
]
