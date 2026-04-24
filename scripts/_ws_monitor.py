"""Minimal process-tree WS monitor — captures peak WorkingSet (RSS) in MiB.

Samples every 0.25 s. Writes peak to the path given as argv[2] when target
PID (argv[1]) exits. Exits itself when target is gone. Scratch utility used
only for ADR-4 §13.1 pilot validation (not canonical telemetry).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import psutil  # type: ignore[import-untyped]


def main() -> int:
    pid = int(sys.argv[1])
    out_path = Path(sys.argv[2])
    try:
        target = psutil.Process(pid)
    except psutil.NoSuchProcess:
        out_path.write_text("ERROR: target pid does not exist\n")
        return 1

    peak_bytes = 0
    samples = 0
    try:
        while True:
            if not target.is_running() or target.status() == psutil.STATUS_ZOMBIE:
                break
            total = 0
            try:
                procs = [target] + target.children(recursive=True)
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
    except KeyboardInterrupt:
        pass

    mib = peak_bytes / (1024 * 1024)
    gib = mib / 1024
    out_path.write_text(
        f"peak_ws_bytes={peak_bytes}\n"
        f"peak_ws_mib={mib:.2f}\n"
        f"peak_ws_gib={gib:.4f}\n"
        f"samples={samples}\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
