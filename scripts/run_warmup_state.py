"""CLI entry — materialize warmup state JSON files (Story T002.0g T2).

Wraps ``packages.t002_eod_unwind.warmup.orchestrator.orchestrate_warmup_state``
with argparse + ``MemoryPoller`` integration (REUSE pattern from
``scripts/run_cpcv_dry_run.py`` per Aria T0 — module + thin CLI).

AC11 contract:
    --as-of-dates DATE,DATE,...    (required, ISO YYYY-MM-DD)
    --source parquet               (default; ``timescaledb`` reserved Phase F)
    --output-dir state/T002/       (default; overridable)
    --seed 42                      (default)
    --mem-poll-interval-s 30       (default)
    --mem-soft-cap-gb 6.0          (default)

Exit codes:
    0 = PASS
    1 = HALT (insufficient trades / hold-out violation / source missing /
        manifest write fail / soft-halt)
    2 = determinism violation (parser error from argparse also)

Hold-out grep contract (DoD §Hold-out intocado):
    grep ``VESPERA_UNLOCK_HOLDOUT`` scripts/run_warmup_state.py >= 1.
"""
from __future__ import annotations

import argparse
import csv
import logging
import sys
import threading
import time
from datetime import date, datetime
from pathlib import Path
from typing import Any, Optional

# Repo root + scripts/ on sys.path so we can import _holdout_lock + packages.
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import psutil  # noqa: E402  AC10 — REQUIRED (no silent degrade per memory protocol)

from _holdout_lock import (  # noqa: E402
    HoldoutLockError,
    assert_holdout_safe,
)

from packages.t002_eod_unwind.warmup.calendar_loader import CalendarLoader  # noqa: E402
from packages.t002_eod_unwind.warmup.orchestrator import (  # noqa: E402
    FeedParquetSource,
    InsufficientCoverage,
    ManifestWriteError,
    orchestrate_warmup_state,
)


# =====================================================================
# Constants — story-locked defaults (AC11)
# =====================================================================
DEFAULT_OUTPUT_DIR: Path = Path("state/T002")
DEFAULT_CALENDAR_PATH: Path = Path("config/calendar/2024-2027.yaml")
DEFAULT_SOURCE: str = "parquet"
DEFAULT_TICKER: str = "WDO"
DEFAULT_SEED: int = 42
DEFAULT_POLL_INTERVAL_S: float = 30.0
DEFAULT_SOFT_CAP_GB: float = 6.0

# Telemetry CSV header — superset of cpcv_dry_run pattern (Pax gap #2 reuse).
TELEMETRY_COLUMNS: tuple[str, ...] = (
    "timestamp_brt",
    "rss_mb",
    "vms_mb",
    "cpu_pct",
    "peak_commit_bytes",
    "peak_wset_bytes",
    "sample_size",
    "duration_ms",
    "as_of_date",
    "phase",
    "note",
)

# Hold-out env grep anchor (DoD requirement — grep at least 1 match).
# This module enforces VESPERA_UNLOCK_HOLDOUT semantics via the
# _holdout_lock import above (R1 + R15(d)). The literal name appears here
# for the DoD grep contract.
_HOLDOUT_UNLOCK_ENV: str = "VESPERA_UNLOCK_HOLDOUT"


logger = logging.getLogger("run_warmup_state")


# =====================================================================
# Argparse (AC11)
# =====================================================================
def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ISO date {value!r}; expected YYYY-MM-DD"
        ) from exc


def _parse_iso_date_list(value: str) -> list[date]:
    """Comma-separated ISO YYYY-MM-DD list."""
    if not value:
        raise argparse.ArgumentTypeError("--as-of-dates must be non-empty")
    items = [v.strip() for v in value.split(",") if v.strip()]
    if not items:
        raise argparse.ArgumentTypeError("--as-of-dates must contain at least one date")
    return [_parse_iso_date(v) for v in items]


def build_arg_parser() -> argparse.ArgumentParser:
    """Argparse parser per AC11. Exposed for tests via ``build_arg_parser``."""
    p = argparse.ArgumentParser(
        prog="run_warmup_state",
        description=(
            "Materialize ATR_20d + Percentiles_126d warmup state JSON files "
            "to state/T002/ from parquet trades. T002.0g orchestrator CLI."
        ),
    )
    p.add_argument(
        "--as-of-dates",
        type=_parse_iso_date_list,
        required=True,
        help="Comma-separated ISO dates (e.g. 2025-05-31,2024-06-30).",
    )
    p.add_argument(
        "--source",
        type=str,
        default=DEFAULT_SOURCE,
        choices=("parquet",),
        help="Trades source. 'timescaledb' reserved for Phase F.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output dir for state JSON + manifest (default state/T002/).",
    )
    p.add_argument(
        "--calendar",
        type=Path,
        default=DEFAULT_CALENDAR_PATH,
        help="Calendar YAML path (Mira T0 — single-source).",
    )
    p.add_argument(
        "--ticker",
        type=str,
        default=DEFAULT_TICKER,
        choices=("WDO", "WIN"),
        help="Adapter ticker whitelist.",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Determinism seed (default {DEFAULT_SEED}).",
    )
    p.add_argument(
        "--mem-poll-interval-s",
        type=float,
        default=DEFAULT_POLL_INTERVAL_S,
        help=f"psutil poller cadence (default {DEFAULT_POLL_INTERVAL_S}s).",
    )
    p.add_argument(
        "--mem-soft-cap-gb",
        type=float,
        default=DEFAULT_SOFT_CAP_GB,
        help=f"Soft halt threshold in GiB (default {DEFAULT_SOFT_CAP_GB}).",
    )
    p.add_argument(
        "--telemetry-csv",
        type=Path,
        default=None,
        help=(
            "Telemetry CSV path. Default: <output-dir>/telemetry-warmup.csv."
        ),
    )
    return p


# =====================================================================
# AC10 — MemoryPoller (REUSE pattern from run_cpcv_dry_run.py)
# =====================================================================
class MemoryPoller:
    """Daemon-thread psutil poller writing telemetry CSV at cadence.

    Pattern REUSED from ``scripts/run_cpcv_dry_run.py::MemoryPoller``
    (T002.0f T3) per Aria T0 + Riven T0 ADR-1 v3 compliance.
    """

    def __init__(
        self,
        csv_path: Path,
        *,
        soft_cap_bytes: int,
        poll_interval_s: float,
        enabled: bool = True,
    ) -> None:
        self.csv_path = csv_path
        self.soft_cap_bytes = soft_cap_bytes
        self.poll_interval_s = poll_interval_s
        self.enabled = enabled
        self.shutdown_event = threading.Event()
        self.halt_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._current_phase = "init"
        self._current_as_of: str = ""
        self._sample_count: int = 0
        self._peak_rss: int = 0
        self._peak_vms: int = 0

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(TELEMETRY_COLUMNS)

    # ----- phase context -----
    def set_phase(self, phase: str, *, as_of: str = "") -> None:
        with self._lock:
            self._current_phase = phase
            self._current_as_of = as_of

    def write_event(self, *, phase: str, note: str = "") -> None:
        self._write_row(phase=phase, note=note)

    # ----- thread lifecycle -----
    def start(self) -> None:
        if not self.enabled:
            return
        self._thread = threading.Thread(
            target=self._run_loop, name="warmup-memory-poller", daemon=True
        )
        self._thread.start()

    def stop(self, *, timeout: float = 5.0) -> None:
        self.shutdown_event.set()
        t = self._thread
        if t is not None and t.is_alive():
            t.join(timeout=timeout)

    # ----- internals -----
    def _run_loop(self) -> None:
        while not self.shutdown_event.is_set():
            self._write_row(phase=self._current_phase, note="poll")
            if self.shutdown_event.wait(timeout=self.poll_interval_s):
                break

    def _write_row(self, *, phase: str, note: str) -> None:
        try:
            proc = psutil.Process()
            mem = proc.memory_info()
            cpu = proc.cpu_percent(interval=None)
        except Exception as exc:  # noqa: BLE001 — diagnostic must not crash
            self._safe_csv_append(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    "", "", "", "", "", "", "",
                    self._current_as_of,
                    phase,
                    f"psutil_error: {exc}",
                ]
            )
            return

        rss = int(mem.rss)
        vms = int(mem.vms)
        with self._lock:
            self._sample_count += 1
            self._peak_rss = max(self._peak_rss, rss)
            self._peak_vms = max(self._peak_vms, vms)
            sample_size = self._sample_count
            peak_rss = self._peak_rss
            peak_vms = self._peak_vms
            as_of = self._current_as_of

        soft_halt_note = note
        if rss > self.soft_cap_bytes:
            self.halt_event.set()
            soft_halt_note = (
                f"{note};SOFT_HALT_FIRED rss={rss} > cap={self.soft_cap_bytes}"
                if note
                else f"SOFT_HALT_FIRED rss={rss} > cap={self.soft_cap_bytes}"
            )

        self._safe_csv_append(
            [
                datetime.now().isoformat(timespec="seconds"),
                f"{rss / (1024 * 1024):.2f}",
                f"{vms / (1024 * 1024):.2f}",
                f"{cpu:.2f}",
                str(peak_rss),
                str(peak_vms),
                str(sample_size),
                "0",
                as_of,
                phase,
                soft_halt_note,
            ]
        )

    def _safe_csv_append(self, row: list[Any]) -> None:
        try:
            with self.csv_path.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(row)
        except OSError:
            pass


# =====================================================================
# Calendar SHA helper (manifest pin)
# =====================================================================
def _sha256_path(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# =====================================================================
# main()
# =====================================================================
def main(argv: Optional[list[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # Calendar load (Mira T0 — single source).
    if not args.calendar.exists():
        print(f"ERROR: calendar not found: {args.calendar}", file=sys.stderr)
        return 1
    try:
        calendar = CalendarLoader.load(args.calendar)
    except (ValueError, OSError) as exc:
        print(f"ERROR: calendar load failed: {exc}", file=sys.stderr)
        return 1
    calendar_sha = _sha256_path(args.calendar)

    # Output dir — fail-closed (Guard #2: NO silent path switch).
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(
            f"ERROR: cannot create output dir {args.output_dir}: {exc}",
            file=sys.stderr,
        )
        return 1

    # AC10 — psutil poller.
    soft_cap_bytes = int(args.mem_soft_cap_gb * 1024**3)
    csv_path = args.telemetry_csv or (args.output_dir / "telemetry-warmup.csv")
    poller = MemoryPoller(
        csv_path,
        soft_cap_bytes=soft_cap_bytes,
        poll_interval_s=args.mem_poll_interval_s,
        enabled=True,
    )
    poller.write_event(phase="run_start", note=f"as_of_dates={[d.isoformat() for d in args.as_of_dates]}")
    poller.start()

    # Source DI per Aria T0 (Phase F: TimescaleSource).
    source: Any
    if args.source == "parquet":
        source = FeedParquetSource(ticker=args.ticker)
    else:  # pragma: no cover — choices=('parquet',) keeps us out of here
        print(f"ERROR: unknown source {args.source!r}", file=sys.stderr)
        poller.stop()
        return 1

    halt_observed = False
    t_start = time.monotonic()
    try:
        # AC3 — defense-in-depth: hold-out lock fired BEFORE adapter open.
        # The orchestrator also wires this internally per as_of_date; we
        # additionally enforce the global window here for early failure
        # (operator sees the violation BEFORE any work).
        # NOTE: per-as_of windows back-date 146bd; the earliest start is
        # the EARLIEST as_of - safety_buffer. We probe each as_of's
        # window via the same compute_window helper.
        from packages.t002_eod_unwind.warmup.orchestrator import compute_window

        for as_of in args.as_of_dates:
            try:
                start, end = compute_window(as_of, calendar)
            except InsufficientCoverage as exc:
                # Surface InsufficientCoverage at this layer too so we
                # don't burn IO/memory before bailing.
                poller.write_event(phase="window_fail", note=str(exc))
                print(f"ERROR: {exc}", file=sys.stderr)
                return 1
            try:
                assert_holdout_safe(start, end)
            except HoldoutLockError as exc:
                poller.write_event(
                    phase="holdout_violation",
                    note=f"as_of={as_of.isoformat()};{exc}",
                )
                print(
                    f"ERROR: hold-out lock violation (R1 + R15(d)): {exc}\n"
                    f"Set {_HOLDOUT_UNLOCK_ENV}=1 with explicit operator "
                    "justification to bypass.",
                    file=sys.stderr,
                )
                return 1

        poller.set_phase(phase="orchestrate")
        poller.write_event(
            phase="orchestrate_start",
            note=f"as_of_count={len(args.as_of_dates)}",
        )
        try:
            result = orchestrate_warmup_state(
                as_of_dates=args.as_of_dates,
                source=source,
                output_dir=args.output_dir,
                calendar=calendar,
                calendar_sha=calendar_sha,
                seed=args.seed,
                ticker=args.ticker,
            )
        except InsufficientCoverage as exc:
            poller.write_event(phase="insufficient_coverage", note=str(exc))
            print(f"HALT: {exc}", file=sys.stderr)
            return 1
        except ManifestWriteError as exc:
            poller.write_event(phase="manifest_write_fail", note=str(exc))
            print(f"HALT: {exc}", file=sys.stderr)
            return 1
        except FileNotFoundError as exc:
            poller.write_event(phase="source_missing", note=str(exc))
            print(f"HALT: source missing — {exc}", file=sys.stderr)
            return 1
        except HoldoutLockError as exc:
            poller.write_event(phase="holdout_violation", note=str(exc))
            print(
                f"ERROR: hold-out lock violation (R1 + R15(d)): {exc}\n"
                f"Set {_HOLDOUT_UNLOCK_ENV}=1 to bypass.",
                file=sys.stderr,
            )
            return 1

        if poller.halt_event.is_set():
            halt_observed = True
            poller.write_event(
                phase="halt_after_orchestrate",
                note="6 GiB soft cap exceeded; state was persisted",
            )
            return 1

        poller.write_event(
            phase="orchestrate_complete",
            note=(
                f"atr_paths={len(result.atr_paths)};"
                f"pct_paths={len(result.percentiles_paths)};"
                f"latest_atr={result.latest_atr_path};"
                f"latest_pct={result.latest_percentiles_path};"
                f"tradetype={result.tradetype_decision.status}"
            ),
        )
        return 0
    finally:
        duration_ms = int((time.monotonic() - t_start) * 1000)
        poller.write_event(
            phase="run_end",
            note=f"halt_observed={halt_observed};duration_ms={duration_ms}",
        )
        poller.stop()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
