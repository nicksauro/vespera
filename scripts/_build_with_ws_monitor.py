"""Launch build_raw_trades_cache.py and capture peak working-set RSS.

Scratch utility for ADR-4 §13.1 pilot acceptance (A1: peak WS < 3.5 GiB).
Spawns the build as a subprocess; samples the child + descendants every
0.25 s; writes peak + duration to argv[-1].
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import psutil  # type: ignore[import-untyped]

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: _build_with_ws_monitor.py <out_metrics.txt> -- <cmd...>",
              file=sys.stderr)
        return 2

    out_path = Path(sys.argv[1])
    # Expect `--` separator between out path and child cmd.
    try:
        sep_idx = sys.argv.index("--")
    except ValueError:
        print("missing -- separator", file=sys.stderr)
        return 2
    child_cmd = sys.argv[sep_idx + 1:]
    if not child_cmd:
        print("empty child cmd", file=sys.stderr)
        return 2

    # Resolve relative executable against REPO_ROOT (Windows subprocess does
    # not honor cwd when looking up the program image).
    if child_cmd and not Path(child_cmd[0]).is_absolute():
        candidate = (REPO_ROOT / child_cmd[0]).resolve()
        if candidate.exists():
            child_cmd = [str(candidate)] + child_cmd[1:]

    t0 = time.monotonic()
    proc = subprocess.Popen(
        child_cmd,
        cwd=str(REPO_ROOT),
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    psu = psutil.Process(proc.pid)

    peak_bytes = 0
    samples = 0
    try:
        while proc.poll() is None:
            total = 0
            try:
                procs = [psu] + psu.children(recursive=True)
                for p in procs:
                    try:
                        total += p.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except psutil.NoSuchProcess:
                break
            if total > peak_bytes:
                peak_bytes = total
            samples += 1
            time.sleep(0.25)
    finally:
        rc = proc.wait()

    elapsed = time.monotonic() - t0
    mib = peak_bytes / (1024 * 1024)
    gib = mib / 1024
    out_path.write_text(
        f"child_rc={rc}\n"
        f"peak_ws_bytes={peak_bytes}\n"
        f"peak_ws_mib={mib:.2f}\n"
        f"peak_ws_gib={gib:.4f}\n"
        f"samples={samples}\n"
        f"elapsed_s={elapsed:.2f}\n"
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
