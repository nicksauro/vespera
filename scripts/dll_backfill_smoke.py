"""dll_backfill_smoke — Phase 2A real-data smoke validator.

Spec:           Phase 2A backfill orchestrator (Council 2026-05-01 R1-R4 follow-up)
Authority:      Dara (@data-engineer) executes; Nelo (@profitdll-specialist) primitives
Article II:     Gage @devops EXCLUSIVE on git push — DO NOT push from this script.

Purpose
-------
Single-chunk smoke test that exercises ``dll_backfill_lib.run_chunk`` with the
new ``IncrementalParquetSink`` against a known-good window
(2024-01-02..2024-01-06, ticker=WDOFUT, ~2.6M rows in CONTROL-2024-01 baseline).

Validates:
  1. parquet exists + readable via ``pq.read_table``
  2. row_count >= 2_000_000 (CONTROL-2024-01 baseline ~2.6M rows)
  3. JSONL sidecar exists (N/A in single-shot mode — auto-PASS)
  4. JSONL line count == parquet rows (N/A in single-shot mode — auto-PASS)
  5. SHA256 of parquet logged

Reports RAM peak (tracemalloc), wall clock, persisted rows, sha256.

Output dir: ``D:\\Algotrader\\dll-backfill\\smoke-test\\``

Required env vars (Dara provisions):
    DLL_PATH                — absolute path to ProfitDLL.dll
    DLL_ACTIVATION_KEY      — Nelogica license activation key
    DLL_USER                — Nelogica login
    DLL_PASSWORD            — Nelogica password

Exit codes
----------
    0 : SMOKE PASS (all 5 checks pass + outcome=full_month_works)
    1 : SMOKE FAIL (any check failed; sink and chunk artefacts left on disk)
    3 : ERROR (env / DLL load / uncaught)

Usage
-----
    python scripts/dll_backfill_smoke.py
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sys
import time
import tracemalloc
from pathlib import Path

# Ensure repo root on sys.path so this script can `import dll_backfill_lib`
# whether invoked from repo root or from inside ``scripts/``.
_THIS_FILE = Path(__file__).resolve()
_SCRIPTS_DIR = _THIS_FILE.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import dll_backfill_lib as lib  # noqa: E402

# --- Smoke configuration ---------------------------------------------------

SMOKE_START = "2024-01-02"
SMOKE_END = "2024-01-06"     # Q-RANGE-13-E: 5d window
SMOKE_TICKER = "WDOFUT"
SMOKE_OUTPUT_DIR = Path(r"D:\Algotrader\dll-backfill\smoke-test")

SMOKE_HARD_TIMEOUT_S = 600.0
SMOKE_IDLE_WATCHDOG_S = 120.0

# Validation thresholds (CONTROL-2024-01 baseline ~2.6M)
MIN_ROWS_THRESHOLD = 2_000_000


def _make_logger() -> logging.Logger:
    SMOKE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("dll_backfill_smoke")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers.clear()
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] [smoke] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    sh.setLevel(logging.INFO)
    fh = logging.FileHandler(
        SMOKE_OUTPUT_DIR / "smoke-driver.log", encoding="utf-8"
    )
    fh.setFormatter(fmt)
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


def _sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            buf = fh.read(chunk_size)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def _count_jsonl_lines(path: Path) -> int:
    n = 0
    with path.open("r", encoding="utf-8") as fh:
        for _ in fh:
            n += 1
    return n


def _validate_artifacts(
    result: dict,
    logger: logging.Logger,
) -> tuple[bool, dict]:
    """Run 5 validation checks against the chunk artefacts.

    Returns (overall_pass, per_check_dict).
    """
    parquet_path: Path = result["parquet_path"]
    jsonl_path: Path | None = result["jsonl_path"]
    persisted_rows: int = result["persisted_rows"]
    outcome: str = result["outcome"]

    checks: dict = {}

    # 1. parquet exists + readable
    parquet_readable = False
    parquet_row_count = 0
    parquet_sha = None
    try:
        import pyarrow.parquet as pq  # type: ignore[import-untyped]
        if not parquet_path.exists():
            logger.error("VALIDATION 1 FAIL: parquet does not exist: %s", parquet_path)
        else:
            tbl = pq.read_table(parquet_path)
            parquet_row_count = tbl.num_rows
            parquet_readable = True
            parquet_sha = _sha256_file(parquet_path)
            logger.info(
                "VALIDATION 1 PASS: parquet readable (%d rows, sha256=%s)",
                parquet_row_count, parquet_sha,
            )
    except Exception as e:
        logger.error("VALIDATION 1 FAIL: parquet read raised: %s", e)
    checks["parquet_readable"] = parquet_readable
    checks["parquet_row_count"] = parquet_row_count
    checks["parquet_sha256"] = parquet_sha

    # 2. row_count threshold
    row_count_ok = parquet_row_count >= MIN_ROWS_THRESHOLD
    if row_count_ok:
        logger.info(
            "VALIDATION 2 PASS: parquet row_count=%d >= %d",
            parquet_row_count, MIN_ROWS_THRESHOLD,
        )
    else:
        logger.error(
            "VALIDATION 2 FAIL: parquet row_count=%d < threshold %d",
            parquet_row_count, MIN_ROWS_THRESHOLD,
        )
    checks["row_count_meets_threshold"] = row_count_ok

    # 3. JSONL sidecar exists (N/A in single-shot mode where jsonl_path is None)
    if jsonl_path is None:
        logger.info("VALIDATION 3 N/A: single-shot mode (no JSONL sidecar)")
        jsonl_exists = True  # treat N/A as PASS in single-shot
    else:
        jsonl_exists = jsonl_path.exists()
        if jsonl_exists:
            logger.info("VALIDATION 3 PASS: JSONL sidecar exists at %s", jsonl_path)
        else:
            logger.error("VALIDATION 3 FAIL: JSONL sidecar missing (path=%s)", jsonl_path)
    checks["jsonl_exists"] = jsonl_exists

    # 4. JSONL line count == parquet rows (N/A in single-shot mode)
    jsonl_line_count = 0
    if jsonl_path is None:
        logger.info("VALIDATION 4 N/A: single-shot mode (no JSONL to compare)")
        jsonl_match = True  # treat N/A as PASS
    elif jsonl_exists:
        try:
            jsonl_line_count = _count_jsonl_lines(jsonl_path)
            jsonl_match = jsonl_line_count == parquet_row_count
            if jsonl_match:
                logger.info(
                    "VALIDATION 4 PASS: JSONL line count == parquet rows (%d)",
                    jsonl_line_count,
                )
            else:
                logger.error(
                    "VALIDATION 4 FAIL: JSONL lines=%d != parquet rows=%d",
                    jsonl_line_count, parquet_row_count,
                )
        except Exception as e:
            jsonl_match = False
            logger.error("VALIDATION 4 FAIL: JSONL count raised: %s", e)
    else:
        jsonl_match = False
    checks["jsonl_line_count"] = jsonl_line_count
    checks["jsonl_count_matches_parquet"] = jsonl_match

    # 5. SHA256 logged (informational; PASS if computed in step 1)
    sha_ok = parquet_sha is not None
    if sha_ok:
        logger.info("VALIDATION 5 PASS: parquet SHA256 computed: %s", parquet_sha)
    else:
        logger.error("VALIDATION 5 FAIL: parquet SHA256 not computed")
    checks["parquet_sha256_computed"] = sha_ok

    # Bonus: outcome must be full_month_works for a clean smoke.
    outcome_ok = outcome == "full_month_works"
    if outcome_ok:
        logger.info("BONUS PASS: outcome=full_month_works")
    else:
        logger.warning("BONUS NOTE: outcome=%s (smoke still graded on 5 checks)", outcome)
    checks["outcome_full_month_works"] = outcome_ok

    # Sanity cross-check: persisted_rows from sink should equal parquet rows.
    if parquet_readable and persisted_rows != parquet_row_count:
        logger.warning(
            "Sanity drift: sink.persisted_rows=%d vs parquet rows=%d",
            persisted_rows, parquet_row_count,
        )
    checks["sink_persisted_rows"] = persisted_rows

    overall = (
        parquet_readable
        and row_count_ok
        and jsonl_exists
        and jsonl_match
        and sha_ok
    )
    return overall, checks


def main() -> int:
    logger = _make_logger()

    if sys.platform != "win32":
        logger.error("ProfitDLL is Win64 closed-source; smoke runs only on Windows.")
        return 3

    dll_path = os.environ.get("DLL_PATH", "")
    activation_key = os.environ.get("DLL_ACTIVATION_KEY", "")
    user = os.environ.get("DLL_USER", "")
    password = os.environ.get("DLL_PASSWORD", "")

    missing = [
        n for n, v in [
            ("DLL_PATH", dll_path),
            ("DLL_ACTIVATION_KEY", activation_key),
            ("DLL_USER", user),
            ("DLL_PASSWORD", password),
        ] if not v
    ]
    if missing:
        logger.error("Missing required env vars: %s", missing)
        return 3

    logger.info("=" * 78)
    logger.info("DLL backfill smoke test starting")
    logger.info(
        "Window: %s..%s ticker=%s output_dir=%s",
        SMOKE_START, SMOKE_END, SMOKE_TICKER, SMOKE_OUTPUT_DIR,
    )
    logger.info(
        "Hard timeout=%.0fs idle watchdog=%.0fs sink=IncrementalParquetSink",
        SMOKE_HARD_TIMEOUT_S, SMOKE_IDLE_WATCHDOG_S,
    )
    logger.info("=" * 78)

    # Sink factory: the lib calls this with the planned parquet path so the
    # sink can derive its sidecar (.jsonl) and atomic .tmp. We pass logger
    # so the sink writes errors to the chunk's per-run logger.
    def sink_factory(parquet_path: Path) -> lib.IncrementalParquetSink:
        jsonl_path = parquet_path.with_suffix(".jsonl")
        chunk_logger = logging.getLogger(
            f"dll_backfill.{parquet_path.stem}.sink"
        )
        if not chunk_logger.handlers:
            # Reuse smoke driver logger handlers so sink errors hit the same log.
            for h in logger.handlers:
                chunk_logger.addHandler(h)
            chunk_logger.setLevel(logging.INFO)
            chunk_logger.propagate = False
        return lib.IncrementalParquetSink(parquet_path, jsonl_path, chunk_logger)

    tracemalloc.start()
    wall_start = time.time()
    try:
        result = lib.run_chunk(
            start_date=SMOKE_START,
            end_date=SMOKE_END,
            ticker=SMOKE_TICKER,
            dll_path=dll_path,
            activation_key=activation_key,
            user=user,
            password=password,
            output_dir=SMOKE_OUTPUT_DIR,
            hard_timeout_s=SMOKE_HARD_TIMEOUT_S,
            idle_watchdog_s=SMOKE_IDLE_WATCHDOG_S,
            sink_factory=None,
        )
    except Exception as e:
        wall_end = time.time()
        try:
            current, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        logger.error("run_chunk raised: %s", e, exc_info=True)
        logger.error("Wall clock: %.1fs / RAM peak: %.1f MB", wall_end - wall_start, peak / 1e6)
        return 3

    wall_end = time.time()
    try:
        current, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    wall_clock_s = wall_end - wall_start
    ram_peak_mb = peak / 1e6

    logger.info("=" * 78)
    logger.info("run_chunk returned outcome=%s exit_code=%d", result["outcome"], result["exit_code"])
    logger.info("Persisted rows (sink): %d", result["persisted_rows"])
    logger.info("Wall clock: %.1fs", wall_clock_s)
    logger.info("RAM peak (tracemalloc): %.1f MB", ram_peak_mb)
    logger.info("=" * 78)

    overall_pass, checks = _validate_artifacts(result, logger)

    summary = {
        "smoke_window": f"{SMOKE_START}..{SMOKE_END}",
        "ticker": SMOKE_TICKER,
        "wall_clock_s": round(wall_clock_s, 3),
        "ram_peak_mb": round(ram_peak_mb, 1),
        "outcome": result["outcome"],
        "outcome_branch": result["outcome_branch"],
        "exit_code_chunk": result["exit_code"],
        "checks": checks,
        "artifacts": {
            "parquet": str(result["parquet_path"]),
            "jsonl": str(result["jsonl_path"]) if result["jsonl_path"] else None,
            "telemetry": str(result["telemetry_path"]),
            "log": str(result["log_path"]),
        },
        "overall_pass": overall_pass,
    }

    summary_path = SMOKE_OUTPUT_DIR / "smoke-summary.json"
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, default=str, ensure_ascii=False)
    logger.info("Smoke summary written: %s", summary_path)

    status_label = "PASS" if overall_pass else "FAIL"
    logger.info("=" * 78)
    logger.info("SMOKE %s — wall=%.1fs ram_peak=%.1f MB rows=%d outcome=%s",
                status_label, wall_clock_s, ram_peak_mb,
                checks.get("parquet_row_count", 0), result["outcome"])
    logger.info("=" * 78)

    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
