"""Per-chunk runner — invoked by orchestrator via subprocess.

Spawns fresh python process, monkey-patches probe module-globals
(_OUTPUT_DIR, _HARD_TIMEOUT_S, _IDLE_WATCHDOG_S), bypasses R1
hard-rule check (handled by orchestrator with explicit override env var
to keep audit trail), and calls run_probe() directly.

This pattern matches dll_control_check_2024_01.py / 2023_12_5d.py — proven
to deliver 8500 trd/s + zero queue_full_drops + reached_100=True.

Article IV: probe arquivo not modified; monkey-patch is in-process module
attribute reassignment after import. Orchestrator-level governance.

Audit-trail (R1 bypass):
    Orchestrator must set DLL_BACKFILL_R1_OVERRIDE=ratified_council_2026_05_03_R1_amendment_quorum_<sha>
    before invoking this runner. The probe's _validate_args() is bypassed
    because run_probe() is called directly (no main() flow). The override env
    var documents intent and is logged on stderr.

    Source: docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md §2.3 R15
    — RATIFIED 6/6 + user MWF cosign 2026-05-03 (token rename per Aria C1 +
    Riven C3 + Nelo C3 BLOCKING; previous token misattributed Aria authorship).

Args (CLI):
    --start-date YYYY-MM-DD
    --end-date YYYY-MM-DD
    --ticker WDOFUT
    --output-dir <path>      absolute; redirects probe._OUTPUT_DIR
    --hard-timeout-s <float> overrides probe._HARD_TIMEOUT_S
    --idle-watchdog-s <float> overrides probe._IDLE_WATCHDOG_S

ENV (forwarded to run_probe):
    DLL_PATH, DLL_ACTIVATION_KEY, DLL_USER, DLL_PASSWORD

Exit codes (passthrough from probe.run_probe):
    0 full_month_works | 1 partial_coverage | 2 retention_exhausted | 3 error
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Ensure scripts/ on path so `import dll_probe_2023_12_wdofut` resolves
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import dll_probe_2023_12_wdofut as probe  # noqa: E402

# Source: docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md §2.3 R15
# — RATIFIED 6/6 + user MWF cosign 2026-05-03. Placeholder _pending_final_sha
# replaced with git short-hash of the commit landing this rename.
_R1_OVERRIDE_TOKEN = "ratified_council_2026_05_03_R1_amendment_quorum_1f9500a"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DLL backfill chunk runner (orchestrator-invoked).")
    p.add_argument("--start-date", required=True, help="ISO YYYY-MM-DD (inclusive)")
    p.add_argument("--end-date", required=True, help="ISO YYYY-MM-DD (inclusive)")
    p.add_argument("--ticker", required=True, help="WDOFUT (continuous)")
    p.add_argument("--output-dir", required=True, help="Absolute path; redirects probe._OUTPUT_DIR")
    p.add_argument("--hard-timeout-s", type=float, required=True)
    p.add_argument("--idle-watchdog-s", type=float, required=True)
    args = p.parse_args()
    # Q09-E enforced parse-time per Council 2026-05-03 R1 Amendment Nelo C5:
    # specific-month contracts (WDOJ26, WDOG26, WDOF26, ...) hit the documented
    # 19ms zero-trade bug; only WDOFUT continuous returns 100% of trades.
    if args.ticker != "WDOFUT":
        raise SystemExit(
            f"E_TICKER_NON_WDOFUT: only WDOFUT continuous allowed "
            f"(Q09-E specific contracts hit 19ms bug); got: {args.ticker!r}"
        )
    return args


def main() -> int:
    args = _parse_args()

    # R1 bypass audit-trail: orchestrator MUST set the override env var.
    override = os.environ.get("DLL_BACKFILL_R1_OVERRIDE", "")
    if override != _R1_OVERRIDE_TOKEN:
        print(
            "ERROR: DLL_BACKFILL_R1_OVERRIDE env var missing or wrong. "
            "Runner refuses to bypass R1 without explicit orchestrator-level ack. "
            f"Expected token: {_R1_OVERRIDE_TOKEN!r}",
            file=sys.stderr,
        )
        return 3
    print(
        f"[runner] R1 bypass acknowledged via override token; window={args.start_date}..{args.end_date}",
        file=sys.stderr,
    )

    if sys.platform != "win32":
        print(
            "ERROR: ProfitDLL is Win64 closed-source; runner runs ONLY on Windows.",
            file=sys.stderr,
        )
        return 3

    # ENV credentials (probe.run_probe takes them as args; surface clear error)
    missing = [
        n
        for n in ("DLL_PATH", "DLL_ACTIVATION_KEY", "DLL_USER", "DLL_PASSWORD")
        if not os.environ.get(n)
    ]
    if missing:
        print(f"ERROR: missing env vars: {missing}", file=sys.stderr)
        return 3

    # Monkey-patch probe module globals (in-process; probe file untouched)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    probe._OUTPUT_DIR = output_dir
    probe._HARD_TIMEOUT_S = float(args.hard_timeout_s)
    probe._IDLE_WATCHDOG_S = float(args.idle_watchdog_s)

    # Cross-drive defense: probe builds telemetry artifact paths via
    # parquet_path.relative_to(_REPO_ROOT). If output_dir is on a different
    # drive (e.g., D:\ external HD vs C:\ repo root), relative_to() raises
    # ValueError after DLLFinalize, killing the final telemetry write.
    # Rebase _REPO_ROOT to a common ancestor of output_dir so the relative_to
    # call succeeds. Probe file untouched (Article IV).
    output_drive_root = Path(output_dir.drive + os.sep) if output_dir.drive else output_dir.anchor
    if not str(output_dir).startswith(str(probe._REPO_ROOT)):
        probe._REPO_ROOT = Path(output_drive_root)

    print(
        f"[runner] monkey-patched probe: _OUTPUT_DIR={output_dir} "
        f"_REPO_ROOT={probe._REPO_ROOT} "
        f"_HARD_TIMEOUT_S={probe._HARD_TIMEOUT_S} _IDLE_WATCHDOG_S={probe._IDLE_WATCHDOG_S}",
        file=sys.stderr,
    )

    # Direct run_probe call — bypasses _validate_args (R1 bound to main() only).
    return probe.run_probe(
        start_date=args.start_date,
        end_date=args.end_date,
        ticker=args.ticker,
        dll_path=os.environ["DLL_PATH"],
        activation_key=os.environ["DLL_ACTIVATION_KEY"],
        user=os.environ["DLL_USER"],
        password=os.environ["DLL_PASSWORD"],
    )


if __name__ == "__main__":
    sys.exit(main())
