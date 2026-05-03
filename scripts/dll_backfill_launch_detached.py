"""Launch orchestrator detached from current shell.

Aria pattern (Option D): Popen with creationflags = DETACHED_PROCESS |
CREATE_BREAKAWAY_FROM_JOB | CREATE_NEW_PROCESS_GROUP. Wrapper exits
immediately after spawning; orchestrator continues independently of the
parent shell, terminal close, or Claude Code session lifecycle.

Usage:
    python scripts/dll_backfill_launch_detached.py \\
        --start-date 2023-01-02 \\
        --end-date 2024-01-01 \\
        --ticker WDOFUT \\
        --output-root "D:\\Algotrader\\dll-backfill" \\
        --max-attempts 3 \\
        --max-consecutive-failures 3 \\
        --max-wall-time-s 23400 \\
        --cooldown-s 30 \\
        --pidfile "<output_root>/orchestrator.pid"

Prints PID to stdout. Orchestrator stdout/stderr is redirected to
<output_root>/orchestrator.log.

Kill-switch (aiox-master use):
    Stop-Process -Id <PID> -Force

Phase 2C — autonomous 5h+ backfill (Aria + Nelo + Riven consensus
2026-05-02). Windows-only (creationflags). Non-Windows raises early.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_ORCHESTRATOR_PATH = _SCRIPT_DIR / "dll_backfill_orchestrator.py"

# Win32 process creation flags (from MSDN). Hardcoded to keep this script
# dependency-free (no win32api / pywin32 import).
_DETACHED_PROCESS = 0x00000008
_CREATE_BREAKAWAY_FROM_JOB = 0x01000000
_CREATE_NEW_PROCESS_GROUP = 0x00000200
_DETACH_FLAGS = _DETACHED_PROCESS | _CREATE_BREAKAWAY_FROM_JOB | _CREATE_NEW_PROCESS_GROUP


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Launch dll_backfill_orchestrator detached (Aria Option D)."
    )
    p.add_argument("--start-date", required=True)
    p.add_argument("--end-date", required=True)
    p.add_argument("--ticker", required=True)
    p.add_argument("--output-root", required=True)
    p.add_argument("--max-attempts", type=int, default=3)
    p.add_argument("--max-consecutive-failures", type=int, default=3)
    p.add_argument("--max-wall-time-s", type=float, default=23400.0)
    p.add_argument("--cooldown-s", type=float, default=30.0)
    p.add_argument(
        "--heartbeat-path",
        type=str,
        default=None,
        help="Forwarded to orchestrator (default <output-root>/manifest.heartbeat).",
    )
    p.add_argument(
        "--pidfile",
        type=str,
        default=None,
        help="Pidfile path (default <output-root>/orchestrator.pid).",
    )
    p.add_argument(
        "--logfile",
        type=str,
        default=None,
        help="Log file path (default <output-root>/orchestrator.log).",
    )
    return p.parse_args()


def main() -> int:
    if sys.platform != "win32":
        print(
            "FATAL: detached launcher is Windows-only (uses Win32 creationflags).",
            file=sys.stderr,
        )
        return 3

    if not _ORCHESTRATOR_PATH.exists():
        print(f"FATAL: orchestrator not found at {_ORCHESTRATOR_PATH}", file=sys.stderr)
        return 3

    args = _parse_args()
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    pidfile = Path(args.pidfile) if args.pidfile else output_root / "orchestrator.pid"
    logfile = Path(args.logfile) if args.logfile else output_root / "orchestrator.log"
    heartbeat_path = (
        Path(args.heartbeat_path) if args.heartbeat_path else output_root / "manifest.heartbeat"
    )

    cmd: list[str] = [
        sys.executable,
        str(_ORCHESTRATOR_PATH),
        "--start-date",
        args.start_date,
        "--end-date",
        args.end_date,
        "--ticker",
        args.ticker,
        "--output-root",
        str(output_root),
        "--max-attempts",
        str(args.max_attempts),
        "--max-consecutive-failures",
        str(args.max_consecutive_failures),
        "--max-wall-time-s",
        str(args.max_wall_time_s),
        "--cooldown-s",
        str(args.cooldown_s),
        "--heartbeat-path",
        str(heartbeat_path),
    ]

    # Open log in append mode so resume runs accumulate history.
    log_fh = logfile.open("ab")
    try:
        proc = subprocess.Popen(  # noqa: S603 — controlled args
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=log_fh,
            stderr=log_fh,
            close_fds=True,
            creationflags=_DETACH_FLAGS,
            cwd=str(_SCRIPT_DIR.parent),
        )
    finally:
        # Parent does not need the log handle; child inherited it.
        try:
            log_fh.close()
        except OSError:
            pass

    pid = proc.pid
    pidfile.parent.mkdir(parents=True, exist_ok=True)
    pidfile.write_text(f"{pid}\n", encoding="utf-8")

    # Print to caller stdout. Wrapper exits 0 and orchestrator runs on.
    print(pid)
    print(f"[launcher] orchestrator PID={pid}", file=sys.stderr)
    print(f"[launcher] log={logfile}", file=sys.stderr)
    print(f"[launcher] pidfile={pidfile}", file=sys.stderr)
    print(f"[launcher] heartbeat={heartbeat_path}", file=sys.stderr)
    print(f"[launcher] kill-switch: Stop-Process -Id {pid} -Force", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
