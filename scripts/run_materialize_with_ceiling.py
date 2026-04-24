"""Thin CLI that composes `materialize_parquet.py` under the memory-ceiling wrapper.

Governance: docs/architecture/memory-budget.md ADR-3 (wrapper responsibility boundary).

This script is DOMAIN-SPECIFIC: it knows about `materialize_parquet.py`, ticker,
dates. All ceiling-enforcement logic lives in `core/run_with_ceiling.py` (library).

Usage
-----
    python scripts/run_materialize_with_ceiling.py \\
        --run-id may-jun-2025 \\
        --start-date 2025-05-01 \\
        --end-date 2025-06-30 \\
        --ticker WDO

BASELINE MODE (Gage G09a only):
    python scripts/run_materialize_with_ceiling.py \\
        --run-id baseline-aug-2024 \\
        --start-date 2024-08-01 \\
        --end-date 2024-08-31 \\
        --ticker WDO \\
        --no-ceiling
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core import memory_budget  # noqa: E402
from core.run_with_ceiling import run_with_ceiling  # noqa: E402

MATERIALIZE_PY = _SCRIPTS_DIR / "materialize_parquet.py"
DEFAULT_LOG_DIR = _REPO_ROOT / "data"


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="run_materialize_with_ceiling",
        description=(
            "Launch scripts/materialize_parquet.py under the memory-ceiling wrapper "
            "(ADR-3 thin CLI). Ceiling / fail-closed semantics per ADR-1 v2 + ADR-2."
        ),
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Operator-supplied run identifier (names log, telemetry CSV, summary JSON).",
    )
    parser.add_argument(
        "--start-date",
        required=True,
        help="YYYY-MM-DD inclusive start date (passed through to materialize_parquet).",
    )
    parser.add_argument(
        "--end-date",
        required=True,
        help="YYYY-MM-DD inclusive end date (passed through to materialize_parquet).",
    )
    parser.add_argument(
        "--ticker",
        required=True,
        help="Ticker symbol (WDO | WIN).",
    )
    parser.add_argument(
        "--poll-seconds",
        type=int,
        default=memory_budget.POLL_SECONDS_DEFAULT,
        help=(
            f"Sampler poll cadence in seconds "
            f"(default {memory_budget.POLL_SECONDS_DEFAULT}, "
            f"clamped to [{memory_budget.POLL_SECONDS_MIN}, {memory_budget.POLL_SECONDS_MAX}])."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing {run_id}.log (default: refuse and exit 1).",
    )
    parser.add_argument(
        "--no-ceiling",
        action="store_true",
        help=(
            "BASELINE MODE ONLY — disable ceiling enforcement. Use exclusively for "
            "G09a baseline-run per ADR-1 v2 remediation step 6."
        ),
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=DEFAULT_LOG_DIR,
        help=f"Directory for run log / telemetry CSV / summary JSON (default: {DEFAULT_LOG_DIR}).",
    )
    # Pass-through to child materialize_parquet.py — mirrors the child's flag.
    parser.add_argument(
        "--output-dir", "--out",
        dest="output_dir",
        type=Path,
        default=None,
        help=(
            "Forwarded to materialize_parquet: parquet output root "
            "(default: data/in_sample). If omitted, the child uses its own default."
        ),
    )
    # MWF-20260422-1 §3.1 — mutually exclusive manifest write-mode flags,
    # mirrored at the wrapper layer so users get the error early.
    manifest_group = parser.add_mutually_exclusive_group()
    manifest_group.add_argument(
        "--no-manifest",
        action="store_true",
        help=(
            "Forwarded to materialize_parquet: do not append to any manifest. "
            "No manifest file is created or mutated. Mutually exclusive "
            "with --manifest-path."
        ),
    )
    manifest_group.add_argument(
        "--manifest-path",
        dest="manifest_path",
        type=Path,
        default=None,
        help=(
            "Forwarded to materialize_parquet: override manifest target to PATH "
            "(scratch manifest). PATH MUST NOT equal the canonical data/manifest.csv. "
            "Mutually exclusive with --no-manifest."
        ),
    )
    # RA-20260426-1 P5 — passthrough of ADR-4 §6.3 source-dispatch flags
    # (--source / --cache-dir / --cache-manifest) so Gage can invoke
    # `--source=cache` retries via the ceiling wrapper. Mirrors the child
    # argparse surface in scripts/materialize_parquet.py §arg-parser.
    parser.add_argument(
        "--source",
        choices=("sentinel", "cache"),
        default="sentinel",
        help=(
            "Forwarded to materialize_parquet: data-origin dispatch "
            "(sentinel = Postgres DB, cache = local pre-cache layer). "
            "Default 'sentinel' preserves pre-RA byte-identical behavior."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        dest="cache_dir",
        type=Path,
        default=None,
        help=(
            "Forwarded to materialize_parquet: cache root (required when "
            "--source=cache; MUST be absent when --source=sentinel)."
        ),
    )
    parser.add_argument(
        "--cache-manifest",
        dest="cache_manifest",
        type=Path,
        default=None,
        help=(
            "Forwarded to materialize_parquet: cache manifest path for sha256 "
            "verification (required when --source=cache; MUST be absent when "
            "--source=sentinel)."
        ),
    )
    ns = parser.parse_args(argv)

    # RA-20260426-1 P5 — source-dispatch mutex validation (wrapper layer so
    # operators get the error before the child is launched under the ceiling).
    if ns.source == "cache":
        missing: list[str] = []
        if ns.cache_dir is None:
            missing.append("--cache-dir")
        if ns.cache_manifest is None:
            missing.append("--cache-manifest")
        if missing:
            parser.error(
                f"--source=cache requires {' and '.join(missing)}."
            )
    else:  # ns.source == "sentinel"
        stray: list[str] = []
        if ns.cache_dir is not None:
            stray.append("--cache-dir")
        if ns.cache_manifest is not None:
            stray.append("--cache-manifest")
        if stray:
            parser.error(
                f"--source=sentinel forbids {' and '.join(stray)} "
                f"(cache flags are only valid with --source=cache)."
            )
    return ns


def _human_gib(byte_count: int) -> str:
    return f"{byte_count / (1024 ** 3):.3f} GiB"


def main(argv: list[str] | None = None) -> int:
    ns = _parse_args(argv)

    # Resolve ceiling: either CEILING_BYTES from memory_budget, or inf for baseline mode.
    if ns.no_ceiling:
        print(
            "WARNING: BASELINE MODE — no ceiling enforcement. Use only for G09a per "
            "ADR-1 v2 remediation step 6.",
            file=sys.stderr,
        )
        ceiling: int | float = math.inf
    else:
        if memory_budget.CEILING_BYTES is None:
            print(
                "ERROR: CEILING_BYTES not yet derived; run G09a baseline-run first "
                "(see docs/architecture/memory-budget.md ADR-1 v2 remediation step 7).",
                file=sys.stderr,
            )
            return 1
        ceiling = int(memory_budget.CEILING_BYTES)

    # Compose materialize_parquet argv (operator-facing CLI surface preserved).
    command = [
        sys.executable,
        str(MATERIALIZE_PY),
        "--start-date", ns.start_date,
        "--end-date", ns.end_date,
        "--ticker", ns.ticker,
    ]
    # Pass-through flags — appended only when operator set them, so the child
    # falls back to its own defaults when unset (Art. IV: no invented semantics).
    if ns.output_dir is not None:
        command.extend(["--output-dir", str(ns.output_dir)])
    if ns.no_manifest:
        command.append("--no-manifest")
    if ns.manifest_path is not None:
        command.extend(["--manifest-path", str(ns.manifest_path)])
    # RA-20260426-1 P5 — always forward --source (explicit for logging),
    # plus cache flags when applicable. Mutex invariants enforced in _parse_args.
    command.extend(["--source", ns.source])
    if ns.source == "cache":
        command.extend(["--cache-dir", str(ns.cache_dir)])
        command.extend(["--cache-manifest", str(ns.cache_manifest)])

    print(f"[wrapper] run_id: {ns.run_id}")
    print(f"[wrapper] command: {' '.join(command)}")
    print(f"[wrapper] log_dir: {ns.log_dir}")
    print(
        f"[wrapper] ceiling: "
        f"{'UNCAPPED (baseline)' if math.isinf(ceiling) else _human_gib(int(ceiling))}"
    )
    print(f"[wrapper] poll_seconds: {ns.poll_seconds}")

    result = run_with_ceiling(
        command,
        run_id=ns.run_id,
        log_dir=ns.log_dir,
        ceiling_bytes=ceiling,
        poll_seconds=ns.poll_seconds,
        force_overwrite=ns.force,
    )

    # Print RunResult summary
    print()
    print("=== RunResult ===")
    print(f"  exit_code         : {result.exit_code}")
    print(f"  peak_commit       : {result.peak_commit} bytes ({_human_gib(result.peak_commit)})")
    print(f"  peak_rss          : {result.peak_rss} bytes ({_human_gib(result.peak_rss)})")
    print(f"  tick_count        : {result.tick_count}")
    print(f"  duration_s        : {result.duration_s:.1f}")
    if math.isfinite(ceiling) and int(ceiling) > 0:
        frac = result.peak_commit / float(ceiling)
        print(f"  peak_commit/ceiling: {frac:.3f}")
    print(f"  telemetry_csv     : {result.telemetry_csv_path}")
    print(f"  summary_json      : {result.summary_json_path}")

    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
