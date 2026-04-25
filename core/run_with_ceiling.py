"""
Memory-ceiling wrapper library for T002.0a G09 materialization runs.

Derivation authority: docs/architecture/memory-budget.md ADR-2 (telemetry mechanism)
and ADR-3 (wrapper responsibility boundary — library + thin CLI split).

This module is the LIBRARY. It does NOT know about `materialize_parquet.py`,
`--start-date`, tickers, phases, or any production-domain concern. A thin CLI
at `scripts/run_materialize_with_ceiling.py` composes the actual invocation.

Exit codes (per ADR-2, with v2 early-trip semantics per ADR-1 v2):
    0 — child exited cleanly, no ceiling trip
    1 — wrapper setup error (host drift, launch-time R4 fail, log-exists without --force)
    2 — hold-out lock raised by child (propagated)
    3 — ceiling tripped at >= KILL_FRACTION * ceiling_bytes; child killed (pre-emptive)
    4 — psutil not importable; aborted before launching (handled at import time upstream)
    5 — sampler lost visibility 3x consecutive; child killed defensively
    >=10 — child's own exit code (propagated)
"""
from __future__ import annotations

import math
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

import psutil

from core import memory_budget
from core.telemetry_schema import (
    Sample,
    append_tick,
    compute_ratio,
    write_summary,
)

# Re-export Sample so callers can `from core.run_with_ceiling import Sample`
__all__ = [
    "Sample",
    "RunResult",
    "psutil_sampler",
    "run_with_ceiling",
]


@dataclass(frozen=True)
class RunResult:
    """Immutable outcome of a `run_with_ceiling` invocation."""
    exit_code: int
    peak_commit: int
    peak_rss: int
    tick_count: int
    duration_s: float
    summary_json_path: Path
    telemetry_csv_path: Path


def _now_brt_iso() -> str:
    """ISO-8601 BRT-naive (no tzinfo) timestamp of current local time.

    R2 invariant: BRT-naive throughout. We emit seconds-resolution to keep CSV
    rows readable; sampler is polled at >=10s cadence so millisecond resolution
    has no analytic value here.
    """
    return datetime.now().isoformat(timespec="seconds")


def psutil_sampler(pid: int) -> Sample | None:
    """Primary sampler used by `run_with_ceiling`. See ADR-2.

    Returns None on psutil.NoSuchProcess or psutil.AccessDenied — caller
    handles fail-closed exit 5 on 3 consecutive None's.

    Fields:
      commit_bytes: child process.memory_info().vms (virtual = commit proxy on Win)
      rss_bytes:    child process.memory_info().rss
      pagefile_alloc_bytes: psutil.swap_memory().used (system-wide PageFile; Riven R1 Signal B)
      available_bytes: psutil.virtual_memory().available (system-wide; informational)
    """
    try:
        proc = psutil.Process(pid)
        mem = proc.memory_info()
        swap = psutil.swap_memory()
        vm = psutil.virtual_memory()
        return Sample(
            commit_bytes=int(mem.vms),
            rss_bytes=int(mem.rss),
            pagefile_alloc_bytes=int(swap.used),
            available_bytes=int(vm.available),
            ts_brt=_now_brt_iso(),
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def _top_non_retained_consumers(n: int = 3) -> list[tuple[str, int, int]]:
    """Return top-N non-whitelisted processes by WorkingSet64 (RSS).

    Each entry: (name, pid, rss_bytes). Used to build the R4 exit-1 message.
    """
    ranked: list[tuple[str, int, int]] = []
    for proc in psutil.process_iter(["name", "pid", "memory_info"]):
        try:
            info = proc.info
            name = info.get("name") or ""
            if memory_budget.is_retained(name):
                continue
            mem = info.get("memory_info")
            if mem is None:
                continue
            ranked.append((name, int(info["pid"]), int(mem.rss)))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    ranked.sort(key=lambda t: t[2], reverse=True)
    return ranked[:n]


def _format_top3_consumers(consumers: list[tuple[str, int, int]]) -> str:
    if not consumers:
        return "  (no non-whitelisted consumers identified)"
    lines = []
    for name, pid, rss in consumers:
        rss_mb = rss / (1024 * 1024)
        lines.append(f"  - {name} (PID {pid}): {rss_mb:.1f} MB WorkingSet64")
    return "\n".join(lines)


def _build_summary_dict(
    *,
    run_id: str,
    start_ts: str,
    end_ts: str,
    duration_s: float,
    peak_commit: int,
    peak_rss: int,
    pagefile_alloc_start: int,
    pagefile_alloc_end: int,
    tick_count: int,
    exit_code: int,
) -> dict:
    return {
        "run_id": run_id,
        "start_ts": start_ts,
        "end_ts": end_ts,
        "duration_s": int(duration_s),
        "peak_commit": int(peak_commit),
        "peak_rss": int(peak_rss),
        "pagefile_alloc_start": int(pagefile_alloc_start),
        "pagefile_alloc_end": int(pagefile_alloc_end),
        "delta_pagefile": int(pagefile_alloc_end - pagefile_alloc_start),
        "ratio_commit_rss": compute_ratio(peak_commit, peak_rss),
        "tick_count": int(tick_count),
        "exit_code": int(exit_code),
    }


def run_with_ceiling(
    command: list[str],
    *,
    run_id: str,
    log_dir: Path,
    ceiling_bytes: int | float,
    poll_seconds: int = memory_budget.POLL_SECONDS_DEFAULT,
    sampler: Callable[[int], Sample | None] = psutil_sampler,
    force_overwrite: bool = False,
) -> RunResult:
    """Launch `command` as a subprocess and enforce a memory ceiling.

    Parameters
    ----------
    command : list[str]
        Full argv for the child. Caller is responsible for composition (the
        library is domain-agnostic per ADR-3).
    run_id : str
        Operator-supplied identifier (e.g. "may-jun-2025"). Used to name
        run log, telemetry CSV, and summary JSON.
    log_dir : Path
        Directory to write run log / telemetry CSV / summary JSON into.
    ceiling_bytes : int | float
        Hard ceiling used for WARN / KILL fractions. Pass `float('inf')` to
        disable enforcement (BASELINE MODE — used by Gage at G09a).
    poll_seconds : int
        Sampler cadence. Default 30s (ADR-2). Clamped to [10, 300].
    sampler : Callable
        Injectable for testability. Default is `psutil_sampler`.
    force_overwrite : bool
        If False (default) and `{run_id}.log` exists → exit 1. If True, the
        log is truncated.

    Returns
    -------
    RunResult
    """
    # --- Launch-time gate 1: host drift check (Aria Finding 4) -------------
    ok, detail = memory_budget.check_host_drift()
    if not ok:
        print(f"ERROR: {detail}")
        return _fail_before_launch(
            run_id=run_id,
            log_dir=log_dir,
            exit_code=1,
        )

    # --- Launch-time gate 2: R4 host-quiesce availability check ------------
    # Only enforced when ceiling is finite (i.e. not --no-ceiling baseline mode).
    # ADR-1 v3: formula changed from `1.5 × CAP_ABSOLUTE` (14.37 GiB, unreachable
    # on this host per RA-20260424-1) to `CAP_ABSOLUTE + OS_HEADROOM` (9.47 GiB,
    # equal to OBSERVED_QUIESCE_FLOOR_AVAILABLE by construction → reachable).
    if math.isfinite(ceiling_bytes):
        vm = psutil.virtual_memory()
        threshold = memory_budget.CAP_ABSOLUTE + memory_budget.OS_HEADROOM
        if vm.available < threshold:
            consumers = _top_non_retained_consumers(n=3)
            shortfall = threshold - vm.available
            msg = (
                f"ERROR: launch-time RAM availability check failed (R4).\n"
                f"  psutil.virtual_memory().available     = {vm.available} bytes "
                f"({vm.available / (1024**3):.2f} GiB)\n"
                f"  required (CAP_ABSOLUTE + OS_HEADROOM) = {threshold} bytes "
                f"({threshold / (1024**3):.2f} GiB)\n"
                f"  shortfall                              = {shortfall} bytes "
                f"({shortfall / (1024**3):.2f} GiB)\n"
                f"Top-3 non-whitelisted consumers to close:\n"
                f"{_format_top3_consumers(consumers)}\n"
                f"See {memory_budget.ADR_REF} Riven Co-sign v3 R4 / E6 (supersedes v2 multiplier)."
            )
            print(msg)
            return _fail_before_launch(
                run_id=run_id,
                log_dir=log_dir,
                exit_code=1,
            )

    # --- Launch-time gate 3: log-exists check ------------------------------
    log_dir.mkdir(parents=True, exist_ok=True)
    run_log_path = log_dir / f"{run_id}.log"
    telemetry_csv_path = log_dir / f"{run_id}-telemetry.csv"
    summary_json_path = log_dir / f"{run_id}-summary.json"

    if run_log_path.exists() and not force_overwrite:
        print(
            f"ERROR: log file already exists at {run_log_path}; pass force_overwrite=True "
            f"(or --force on CLI) to overwrite. Current file preserved."
        )
        return RunResult(
            exit_code=1,
            peak_commit=0,
            peak_rss=0,
            tick_count=0,
            duration_s=0.0,
            summary_json_path=summary_json_path,
            telemetry_csv_path=telemetry_csv_path,
        )

    # Truncate old telemetry CSV to avoid mixing runs
    if telemetry_csv_path.exists():
        telemetry_csv_path.unlink()

    # Clamp poll seconds to configured bounds
    poll_seconds = max(
        memory_budget.POLL_SECONDS_MIN,
        min(memory_budget.POLL_SECONDS_MAX, int(poll_seconds)),
    )

    warn_threshold: float = memory_budget.WARN_FRACTION * float(ceiling_bytes)
    kill_threshold: float = memory_budget.KILL_FRACTION * float(ceiling_bytes)

    start_ts = _now_brt_iso()
    start_mono = time.monotonic()
    peak_commit = 0
    peak_rss = 0
    tick_n = 0
    consecutive_none = 0
    warned_already = False
    pagefile_alloc_start: int | None = None
    pagefile_alloc_last: int = 0
    exit_code: int
    killed_by_ceiling = False
    killed_by_blind_sampler = False

    # Open run log for child stdout/stderr
    with run_log_path.open("w", encoding="utf-8") as log_fh:
        child = subprocess.Popen(
            command,
            stdout=log_fh,
            stderr=subprocess.STDOUT,
        )

        try:
            while True:
                # Check if child exited naturally
                rc = child.poll()
                if rc is not None:
                    exit_code = _map_child_exit(rc)
                    break

                sample = sampler(child.pid)
                if sample is None:
                    consecutive_none += 1
                    if consecutive_none >= 3:
                        # Fail-closed defensive kill (ADR-2 exit 5)
                        child.kill()
                        try:
                            child.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            pass
                        killed_by_blind_sampler = True
                        exit_code = 5
                        break
                    time.sleep(poll_seconds)
                    continue

                consecutive_none = 0
                tick_n += 1
                append_tick(telemetry_csv_path, tick_n, sample)

                if pagefile_alloc_start is None:
                    pagefile_alloc_start = sample.pagefile_alloc_bytes
                pagefile_alloc_last = sample.pagefile_alloc_bytes

                peak_commit = max(peak_commit, sample.commit_bytes)
                peak_rss = max(peak_rss, sample.rss_bytes)

                observed = sample.commit_bytes
                # Pre-emptive kill first (slow-paging fabric rationale)
                if math.isfinite(ceiling_bytes) and observed >= kill_threshold:
                    frac = observed / float(ceiling_bytes)
                    print(
                        f"KILL ceiling={int(ceiling_bytes)} observed={observed} "
                        f"fraction={frac:.3f} tick={tick_n}"
                    )
                    child.kill()
                    try:
                        child.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        pass
                    killed_by_ceiling = True
                    exit_code = 3
                    break

                # WARN (log-only, no kill)
                if (
                    math.isfinite(ceiling_bytes)
                    and observed >= warn_threshold
                    and not warned_already
                ):
                    frac = observed / float(ceiling_bytes)
                    print(
                        f"WARN ceiling={int(ceiling_bytes)} observed={observed} "
                        f"fraction={frac:.3f} tick={tick_n}"
                    )
                    warned_already = True

                time.sleep(poll_seconds)
        finally:
            # Defensive cleanup: if we break out of loop with child still alive,
            # terminate then kill. `killed_by_*` branches above already handled kill.
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    child.kill()

    end_ts = _now_brt_iso()
    duration_s = time.monotonic() - start_mono

    # Ensure pagefile_alloc_start is set even in early-failure paths
    if pagefile_alloc_start is None:
        pagefile_alloc_start = 0

    summary = _build_summary_dict(
        run_id=run_id,
        start_ts=start_ts,
        end_ts=end_ts,
        duration_s=duration_s,
        peak_commit=peak_commit,
        peak_rss=peak_rss,
        pagefile_alloc_start=pagefile_alloc_start,
        pagefile_alloc_end=pagefile_alloc_last,
        tick_count=tick_n,
        exit_code=exit_code,
    )
    write_summary(summary_json_path, summary)

    # Suppress unused-flag warnings (they are part of the state machine but
    # only referenced through exit_code now).
    _ = killed_by_ceiling
    _ = killed_by_blind_sampler

    return RunResult(
        exit_code=exit_code,
        peak_commit=peak_commit,
        peak_rss=peak_rss,
        tick_count=tick_n,
        duration_s=duration_s,
        summary_json_path=summary_json_path,
        telemetry_csv_path=telemetry_csv_path,
    )


def _map_child_exit(rc: int) -> int:
    """Map raw child return code to wrapper exit semantics per ADR-2.

    - 0 from child → 0 (clean)
    - 2 from child → 2 (hold-out lock raised, propagate)
    - anything else → max(rc, 10) so we reserve 0-9 for wrapper semantics
      (ADR-2: ">=10 child's own exit code").
    """
    if rc == 0:
        return 0
    if rc == 2:
        return 2
    if rc < 0:
        # Signal-terminated child on POSIX; treat as child error
        return max(10, 10 + abs(rc))
    if rc < 10:
        return rc + 10
    return rc


def _fail_before_launch(
    *,
    run_id: str,
    log_dir: Path,
    exit_code: int,
) -> RunResult:
    """Return a RunResult representing a launch-gate failure (no child spawned)."""
    log_dir.mkdir(parents=True, exist_ok=True)
    telemetry_csv_path = log_dir / f"{run_id}-telemetry.csv"
    summary_json_path = log_dir / f"{run_id}-summary.json"
    return RunResult(
        exit_code=exit_code,
        peak_commit=0,
        peak_rss=0,
        tick_count=0,
        duration_s=0.0,
        summary_json_path=summary_json_path,
        telemetry_csv_path=telemetry_csv_path,
    )
