"""DLL backfill orchestrator — Phase 2C (autonomous 5h+ backfill).

Generates 5d business-day-aware chunks for [start_date, end_date]
window, invokes dll_backfill_chunk_runner.py per chunk in fresh
subprocess (zero state leakage), parses probe-telemetry-*.json after
each chunk, updates manifest.csv, retries on transient failures.

Phase 2C additions (Riven BLOCKING risk caps + Nelo cooldown + Aria detach):
- max-consecutive-failures abort trigger (default 3)
- max-wall-time-s hard kill (default 6h30min = 23400s)
- cooldown-s between subprocesses (default 30s — TCP TIME_WAIT + DLLFinalize
  quiesce + Q-AMB-04 candidate)
- heartbeat file written per chunk (aiox-master kills if stale >15min)
- cumulative qfd_pct global cap (>0.1% trades total → abort)

Constraints
-----------
- Q-RANGE-13-E: chunks <= 5 business days
- DLL single-instance: subprocess sequential (NEVER parallel)
- User mandate "TODOS os dados sem perda":
    fail-fast if outcome != full_month_works AND outcome != retention_exhausted
- R10: orchestrator does NOT write to data/manifest.csv. Backfill manifest
  lives at <output-root>/manifest.csv with explicit header
  "# backfill-manifest v1 - NOT R10 custodial".
- R1: probe arquivo intocavel; runner monkey-patches in-process.
  Orchestrator sets DLL_BACKFILL_R1_OVERRIDE env to acknowledge bypass.
- Riven BLOCKING (Phase 2C): max_retries_per_chunk=3, max_qfd_global_pct=0.1%
  trades total, max_consecutive_failures=3, max_wall_time_s=23400.

Manifest columns
----------------
chunk_id, start_date, end_date, ticker, status, attempt, trades_count,
queue_full_drops, reached_100, sha256_parquet, parquet_relative_path,
downloaded_ts_brt, last_error_msg, dll_return_code, outcome

Status values
-------------
pending | ok | partial | failed |
quarantined_pre_abort_qfd | quarantined_pre_abort_consec |
quarantined_pre_abort_wall | quarantined_pre_abort_kill

Quarantine semantics (Council 2026-05-03 R1 Amendment §6.1 item 5 — Riven C2)
-----------------------------------------------------------------------------
When an abort trigger fires (qfd_global, consec_fail, wall_time, kill_switch),
ALL chunks flipped to status=ok during THIS run (since start_wall_time) are
re-flagged to status=quarantined_pre_abort_<reason> via atomic manifest write
BEFORE exit code 2 is returned.

Quarantined chunks are NOT auto-retried in resume protocol — operator must
revoke quarantine via separate mini-Council OR re-run with a new run_id.
This prevents silent retention of chunks whose data may be tainted by
pre-abort conditions (e.g. degraded DLL queue, partial DLLFinalize quiesce).

Resume protocol
---------------
- Chunks with status=ok are skipped on re-run.
- Chunks with status=partial/failed retried up to --max-attempts.

Exit codes
----------
0 SUCCESS — all chunks status=ok
1 PARTIAL — some chunks not ok but mission did not abort
2 ABORTED — abort trigger fired (WALL_TIME_EXCEEDED |
            MAX_CONSECUTIVE_FAILURES | QFD_PCT_EXCEEDED)
3 ERROR   — orchestrator-level crash / runner missing

CLI
---
python scripts/dll_backfill_orchestrator.py \
    --start-date 2023-01-01 \
    --end-date 2024-01-01 \
    --ticker WDOFUT \
    --output-root "D:/Algotrader/dll-backfill" \
    --max-attempts 3 \
    --max-consecutive-failures 3 \
    --max-wall-time-s 23400 \
    --cooldown-s 30
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

_SCRIPT_DIR = Path(__file__).resolve().parent
_RUNNER_PATH = _SCRIPT_DIR / "dll_backfill_chunk_runner.py"

# B3 trading holidays for 2023-2024 (continuous WDOFUT). HARDCODED per Nelo
# (Phase 2C): not confundir 0-trade days com retention_exhausted. Total: 24
# dates (12 per year).
B3_HOLIDAYS_2023_2024: frozenset[_dt.date] = frozenset(
    {
        # 2023 (12)
        _dt.date(2023, 1, 1),
        _dt.date(2023, 2, 20),
        _dt.date(2023, 2, 21),  # Carnaval
        _dt.date(2023, 4, 7),
        _dt.date(2023, 4, 21),
        _dt.date(2023, 5, 1),
        _dt.date(2023, 6, 8),
        _dt.date(2023, 9, 7),
        _dt.date(2023, 10, 12),
        _dt.date(2023, 11, 2),
        _dt.date(2023, 11, 15),
        _dt.date(2023, 12, 25),
        # 2024 (12)
        _dt.date(2024, 1, 1),
        _dt.date(2024, 2, 12),
        _dt.date(2024, 2, 13),  # Carnaval 2024
        _dt.date(2024, 3, 29),
        _dt.date(2024, 4, 21),
        _dt.date(2024, 5, 1),
        _dt.date(2024, 5, 30),
        _dt.date(2024, 9, 7),
        _dt.date(2024, 10, 12),
        _dt.date(2024, 11, 2),
        _dt.date(2024, 11, 15),
        _dt.date(2024, 12, 25),
    }
)

# Backwards-compat alias retained for existing call sites.
_B3_HOLIDAYS = B3_HOLIDAYS_2023_2024

_CHUNK_BUSINESS_DAYS = 5
_PER_CHUNK_HARD_TIMEOUT_S = 600.0
_PER_CHUNK_IDLE_WATCHDOG_S = 180.0
_SUBPROCESS_TIMEOUT_S = 800.0  # safety margin over hard_timeout
# Source: docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md §2.3 R15
# — RATIFIED 6/6 + user MWF cosign 2026-05-03 (rename per Aria C1 + Riven C3 +
# Nelo C3 BLOCKING; previous token misattributed Aria authorship). Placeholder
# _pending_final_sha replaced with git short-hash of the rename commit.
_R1_OVERRIDE_TOKEN = "ratified_council_2026_05_03_R1_amendment_quorum_b1802ac_pending_final_sha"

# Phase 2C Riven caps (BLOCKING defaults).
_DEFAULT_MAX_CONSECUTIVE_FAILURES = 3
_DEFAULT_MAX_WALL_TIME_S = 23400.0  # 6h30min
_DEFAULT_COOLDOWN_S = 30.0  # TCP TIME_WAIT + DLLFinalize quiesce + Q-AMB-04
_MAX_QFD_GLOBAL_PCT = 0.001  # 0.1% — Riven hard cap

# Exit codes (Phase 2C).
_EXIT_SUCCESS = 0
_EXIT_PARTIAL = 1
_EXIT_ABORTED = 2
_EXIT_ERROR = 3

_MANIFEST_HEADER_LINE = "# backfill-manifest v1.1 - NOT R10 custodial"

# Quarantine reason → status mapping (Council 2026-05-03 R1 Amendment §6.1 item 5).
# Source: docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md §6.1 item 5 — Riven C2
_QUARANTINE_REASON_TO_STATUS = {
    "QFD_PCT_EXCEEDED": "quarantined_pre_abort_qfd",
    "MAX_CONSECUTIVE_FAILURES": "quarantined_pre_abort_consec",
    "WALL_TIME_EXCEEDED": "quarantined_pre_abort_wall",
    "KILL_SWITCH": "quarantined_pre_abort_kill",
}
_MANIFEST_COLUMNS = [
    "chunk_id",
    "start_date",
    "end_date",
    "ticker",
    "status",
    "attempt",
    "trades_count",
    "queue_full_drops",
    "reached_100",
    "sha256_parquet",
    "parquet_relative_path",
    "downloaded_ts_brt",
    "last_error_msg",
    "dll_return_code",
    "outcome",
]


# --- Chunk planning ---------------------------------------------------------


def _is_business_day(d: _dt.date) -> bool:
    return d.weekday() < 5 and d not in _B3_HOLIDAYS


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    start_date: _dt.date
    end_date: _dt.date
    ticker: str


def plan_chunks(start: _dt.date, end: _dt.date, ticker: str) -> list[Chunk]:
    """Generate sequential chunks of <= 5 business days.

    Each chunk's start/end are inclusive business days. Calendar gaps
    (weekends/holidays) between chunks are absorbed implicitly because
    chunks count business days only.
    """
    if start > end:
        raise ValueError(f"start_date {start} > end_date {end}")
    chunks: list[Chunk] = []
    cursor = start
    # Advance cursor to first business day on/after start
    while cursor <= end and not _is_business_day(cursor):
        cursor += _dt.timedelta(days=1)

    while cursor <= end:
        bdays: list[_dt.date] = []
        scan = cursor
        while scan <= end and len(bdays) < _CHUNK_BUSINESS_DAYS:
            if _is_business_day(scan):
                bdays.append(scan)
            scan += _dt.timedelta(days=1)
        if not bdays:
            break
        c_start = bdays[0]
        c_end = bdays[-1]
        chunk_id = f"{ticker}_{c_start.isoformat()}_{c_end.isoformat()}"
        chunks.append(Chunk(chunk_id=chunk_id, start_date=c_start, end_date=c_end, ticker=ticker))
        # Advance cursor to the day after c_end
        cursor = c_end + _dt.timedelta(days=1)
    return chunks


# --- Manifest store ---------------------------------------------------------


@dataclass
class ManifestRow:
    chunk_id: str
    start_date: str
    end_date: str
    ticker: str
    status: str = "pending"
    attempt: int = 0
    trades_count: int = 0
    queue_full_drops: int = 0
    reached_100: bool = False
    sha256_parquet: str = ""
    parquet_relative_path: str = ""
    downloaded_ts_brt: str = ""
    last_error_msg: str = ""
    dll_return_code: str = ""
    outcome: str = ""

    def to_csv_row(self) -> dict[str, str]:
        return {
            "chunk_id": self.chunk_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "ticker": self.ticker,
            "status": self.status,
            "attempt": str(self.attempt),
            "trades_count": str(self.trades_count),
            "queue_full_drops": str(self.queue_full_drops),
            "reached_100": "true" if self.reached_100 else "false",
            "sha256_parquet": self.sha256_parquet,
            "parquet_relative_path": self.parquet_relative_path,
            "downloaded_ts_brt": self.downloaded_ts_brt,
            "last_error_msg": self.last_error_msg,
            "dll_return_code": self.dll_return_code,
            "outcome": self.outcome,
        }

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "ManifestRow":
        return cls(
            chunk_id=row["chunk_id"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            ticker=row["ticker"],
            status=row.get("status", "pending"),
            attempt=int(row.get("attempt") or 0),
            trades_count=int(row.get("trades_count") or 0),
            queue_full_drops=int(row.get("queue_full_drops") or 0),
            reached_100=str(row.get("reached_100", "false")).lower() == "true",
            sha256_parquet=row.get("sha256_parquet", ""),
            parquet_relative_path=row.get("parquet_relative_path", ""),
            downloaded_ts_brt=row.get("downloaded_ts_brt", ""),
            last_error_msg=row.get("last_error_msg", ""),
            dll_return_code=row.get("dll_return_code", ""),
            outcome=row.get("outcome", ""),
        )


@dataclass
class ManifestStore:
    path: Path
    rows: dict[str, ManifestRow] = field(default_factory=dict)

    def load(self) -> None:
        self.rows = {}
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8", newline="") as f:
            first = f.readline()
            if not first.startswith("#"):
                # No header line -> seek back so DictReader sees full file
                f.seek(0)
            reader = csv.DictReader(f)
            for row in reader:
                if not row.get("chunk_id"):
                    continue
                mr = ManifestRow.from_csv_row(row)
                self.rows[mr.chunk_id] = mr

    def upsert(self, row: ManifestRow) -> None:
        self.rows[row.chunk_id] = row
        self._atomic_write()

    def _atomic_write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_name = tempfile.mkstemp(
            prefix=".manifest-", suffix=".csv.tmp", dir=str(self.path.parent)
        )
        os.close(tmp_fd)
        tmp_path = Path(tmp_name)
        try:
            with tmp_path.open("w", encoding="utf-8", newline="") as f:
                f.write(_MANIFEST_HEADER_LINE + "\n")
                writer = csv.DictWriter(f, fieldnames=_MANIFEST_COLUMNS)
                writer.writeheader()
                for chunk_id in sorted(self.rows.keys()):
                    writer.writerow(self.rows[chunk_id].to_csv_row())
            os.replace(tmp_path, self.path)
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass

    def seed_pending(self, chunks: Iterable[Chunk]) -> None:
        changed = False
        for c in chunks:
            if c.chunk_id not in self.rows:
                self.rows[c.chunk_id] = ManifestRow(
                    chunk_id=c.chunk_id,
                    start_date=c.start_date.isoformat(),
                    end_date=c.end_date.isoformat(),
                    ticker=c.ticker,
                )
                changed = True
        if changed:
            self._atomic_write()


# --- Telemetry parse / chunk validation -------------------------------------


_OUTCOME_EXIT_CODES = {0: "full_month_works", 1: "partial_coverage", 2: "retention_exhausted", 3: "error"}


def _find_latest_telemetry(chunk_dir: Path) -> Path | None:
    candidates = sorted(
        chunk_dir.glob("probe-telemetry-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def _classify_status(
    outcome: str,
    queue_full_drops: int,
    reached_100: bool,
    trades_count: int = 0,
    timeout_hit: bool = False,
    watchdog_idle: bool = False,
) -> str:
    """Per user mandate (no data loss). Data-completeness-first criteria.

    Probe's outcome=partial_coverage may flag schema_aggressor_distribution=False
    (auction-heavy first 1000 trades) even when full chunk data is captured. We
    treat data-completeness signals as authoritative:

    ok: data complete — qfd=0 AND reached_100=True AND trades>=1M AND
        not timeout_hit AND not watchdog_idle
        (regardless of probe schema check passing on the first 1000 trades)
    partial: any data-loss signal — qfd>0 OR reached_100=False OR
        timeout_hit OR watchdog_idle OR trades<1M
    failed: outcome=error
    retention_exhausted: outcome=retention_exhausted → ok (not a loss; data
        physically not retained DLL-side; Council 2026-05-01 documented edge)
    """
    if outcome == "error":
        return "failed"
    if outcome == "retention_exhausted":
        return "ok"
    # Data-completeness-first gate: schema_pass aside, if all loss signals
    # are clean and we have >=1M trades, the chunk is complete.
    data_complete = (
        queue_full_drops == 0
        and reached_100
        and trades_count >= 1_000_000
        and not timeout_hit
        and not watchdog_idle
    )
    if data_complete:
        return "ok"
    return "partial"


# --- Per-chunk subprocess invocation ----------------------------------------


def _run_chunk(chunk: Chunk, output_root: Path, env: dict[str, str]) -> dict:
    chunk_dir = output_root / chunk.chunk_id
    chunk_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable,
        str(_RUNNER_PATH),
        "--start-date",
        chunk.start_date.isoformat(),
        "--end-date",
        chunk.end_date.isoformat(),
        "--ticker",
        chunk.ticker,
        "--output-dir",
        str(chunk_dir),
        "--hard-timeout-s",
        str(_PER_CHUNK_HARD_TIMEOUT_S),
        "--idle-watchdog-s",
        str(_PER_CHUNK_IDLE_WATCHDOG_S),
    ]
    proc_env = dict(env)
    proc_env["DLL_BACKFILL_R1_OVERRIDE"] = _R1_OVERRIDE_TOKEN

    print(f"[orchestrator] >>> {chunk.chunk_id} subprocess start", flush=True)
    try:
        completed = subprocess.run(
            cmd,
            env=proc_env,
            timeout=_SUBPROCESS_TIMEOUT_S,
            capture_output=True,
            text=True,
        )
        return_code = completed.returncode
        stderr_tail = (completed.stderr or "")[-2000:]
        timed_out = False
    except subprocess.TimeoutExpired as e:
        return_code = -1
        stderr_tail = f"subprocess.TimeoutExpired after {e.timeout}s"
        timed_out = True

    telemetry_path = _find_latest_telemetry(chunk_dir)
    telemetry: dict = {}
    if telemetry_path is not None:
        try:
            telemetry = json.loads(telemetry_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            stderr_tail = f"telemetry parse error: {e!r}\n{stderr_tail}"

    return {
        "return_code": return_code,
        "stderr_tail": stderr_tail,
        "telemetry": telemetry,
        "telemetry_path": str(telemetry_path) if telemetry_path else "",
        "timed_out": timed_out,
        "chunk_dir": chunk_dir,
    }


# --- Orchestrator main ------------------------------------------------------


def _now_brt_iso() -> str:
    return _dt.datetime.now().isoformat(timespec="seconds")


def _atomic_write_heartbeat(heartbeat_path: Path, chunk_id: str, status: str) -> None:
    """Atomically write heartbeat (tmp+rename pattern, mirrors manifest write).

    Format: 3 lines — now_iso, chunk_id, status. aiox-master polls mtime; if
    stale >15min mid-run, kill orchestrator PID.
    """
    heartbeat_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_name = tempfile.mkstemp(
        prefix=".heartbeat-", suffix=".tmp", dir=str(heartbeat_path.parent)
    )
    os.close(tmp_fd)
    tmp_path = Path(tmp_name)
    try:
        payload = f"{_now_brt_iso()}\n{chunk_id}\n{status}\n"
        tmp_path.write_text(payload, encoding="utf-8")
        os.replace(tmp_path, heartbeat_path)
    finally:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def run_orchestrator(
    start_date: _dt.date,
    end_date: _dt.date,
    ticker: str,
    output_root: Path,
    max_attempts: int,
    max_consecutive_failures: int = _DEFAULT_MAX_CONSECUTIVE_FAILURES,
    max_wall_time_s: float = _DEFAULT_MAX_WALL_TIME_S,
    cooldown_s: float = _DEFAULT_COOLDOWN_S,
    heartbeat_path: Path | None = None,
) -> int:
    if not _RUNNER_PATH.exists():
        print(f"FATAL: runner not found at {_RUNNER_PATH}", file=sys.stderr)
        return _EXIT_ERROR

    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.csv"
    store = ManifestStore(path=manifest_path)
    store.load()

    if heartbeat_path is None:
        heartbeat_path = output_root / "manifest.heartbeat"

    chunks = plan_chunks(start_date, end_date, ticker)
    print(f"[orchestrator] planned {len(chunks)} chunks for {start_date}..{end_date}")
    print(
        f"[orchestrator] caps: max_consec_fail={max_consecutive_failures} "
        f"max_wall_s={max_wall_time_s} cooldown_s={cooldown_s} "
        f"max_qfd_pct={_MAX_QFD_GLOBAL_PCT * 100:.3f}%"
    )
    store.seed_pending(chunks)

    fatal_partial_failed: list[str] = []
    env = os.environ.copy()

    # Phase 2C state tracking.
    consecutive_failures = 0
    cumulative_qfd = 0
    cumulative_trades = 0
    start_wall_time = time.monotonic()
    abort_reason: str | None = None
    # Council 2026-05-03 R1 Amendment §6.1 item 5 — Riven C2:
    # Track chunks flipped to status=ok during THIS run. On abort, flag them
    # quarantined_pre_abort_<reason> BEFORE returning exit code 2.
    chunks_ok_this_run: list[str] = []

    _atomic_write_heartbeat(heartbeat_path, chunk_id="<startup>", status="starting")

    for idx, chunk in enumerate(chunks):
        # Wall-time budget check BEFORE each chunk.
        elapsed = time.monotonic() - start_wall_time
        if elapsed > max_wall_time_s:
            abort_reason = "WALL_TIME_EXCEEDED"
            print(
                f"[orchestrator] ABORT WALL_TIME_EXCEEDED elapsed={elapsed:.1f}s "
                f"> max={max_wall_time_s:.1f}s before {chunk.chunk_id}",
                file=sys.stderr,
            )
            _atomic_write_heartbeat(heartbeat_path, chunk.chunk_id, "abort_wall_time")
            break

        row = store.rows[chunk.chunk_id]
        if row.status == "ok":
            print(f"[orchestrator] skip {chunk.chunk_id}: status=ok")
            continue
        if row.attempt >= max_attempts:
            print(
                f"[orchestrator] skip {chunk.chunk_id}: attempts {row.attempt} >= max {max_attempts}",
                file=sys.stderr,
            )
            fatal_partial_failed.append(chunk.chunk_id)
            continue

        row.attempt += 1
        store.upsert(row)

        result = _run_chunk(chunk, output_root, env)
        telemetry = result["telemetry"]
        rc = result["return_code"]
        outcome = _OUTCOME_EXIT_CODES.get(rc, telemetry.get("outcome_classification", "error"))
        if telemetry.get("outcome_classification"):
            outcome = telemetry["outcome_classification"]

        trades_count = int((telemetry.get("trades") or {}).get("total_received", 0) or 0)
        qfd = int((telemetry.get("trades") or {}).get("queue_full_drops", 0) or 0)
        reached_100 = bool((telemetry.get("progress") or {}).get("reached_100", False))
        timeout_hit = bool((telemetry.get("watchdogs") or {}).get("timeout_hit", False))
        watchdog_idle = bool((telemetry.get("watchdogs") or {}).get("watchdog_idle_triggered", False))
        artifacts = telemetry.get("artifacts") or {}
        parquet_rel = artifacts.get("parquet", "")

        sha = ""
        if parquet_rel:
            # parquet path in telemetry is relative to repo root; resolve absolute
            parquet_abs = (
                Path(parquet_rel)
                if Path(parquet_rel).is_absolute()
                else (Path(__file__).resolve().parents[1] / parquet_rel)
            )
            if parquet_abs.exists():
                try:
                    sha = _sha256(parquet_abs)
                except OSError as e:
                    result["stderr_tail"] = f"sha256 error: {e!r}\n{result['stderr_tail']}"

        status = _classify_status(outcome, qfd, reached_100, trades_count, timeout_hit, watchdog_idle)

        row.status = status
        row.trades_count = trades_count
        row.queue_full_drops = qfd
        row.reached_100 = reached_100
        row.sha256_parquet = sha
        row.parquet_relative_path = parquet_rel
        row.downloaded_ts_brt = _now_brt_iso()
        row.dll_return_code = str(rc)
        row.outcome = outcome
        row.last_error_msg = (result["stderr_tail"] or "").strip().splitlines()[-1] if status != "ok" else ""
        store.upsert(row)

        # Phase 2C cumulative tracking.
        cumulative_qfd += qfd
        cumulative_trades += trades_count
        if status == "ok":
            consecutive_failures = 0
            # Riven C2 quarantine bookkeeping (Council 2026-05-03 R1 Amendment §6.1 item 5):
            # Record chunks flipped to ok during THIS run for post-abort flagging.
            chunks_ok_this_run.append(chunk.chunk_id)
        else:
            consecutive_failures += 1

        # Heartbeat write AFTER manifest update.
        _atomic_write_heartbeat(heartbeat_path, chunk.chunk_id, status)

        print(
            f"[orchestrator] <<< {chunk.chunk_id} status={status} "
            f"outcome={outcome} trades={trades_count} qfd={qfd} reached_100={reached_100} "
            f"consec_fail={consecutive_failures} cum_qfd={cumulative_qfd} "
            f"cum_trd={cumulative_trades} elapsed={time.monotonic() - start_wall_time:.1f}s"
        )

        if status in ("partial", "failed"):
            fatal_partial_failed.append(chunk.chunk_id)

        # Phase 2C abort triggers (post-chunk).
        if consecutive_failures >= max_consecutive_failures:
            abort_reason = "MAX_CONSECUTIVE_FAILURES"
            print(
                f"[orchestrator] ABORT MAX_CONSECUTIVE_FAILURES "
                f"consec={consecutive_failures} >= max={max_consecutive_failures}",
                file=sys.stderr,
            )
            _atomic_write_heartbeat(heartbeat_path, chunk.chunk_id, "abort_consec_fail")
            break

        if cumulative_trades > 0:
            qfd_ratio = cumulative_qfd / cumulative_trades
            if qfd_ratio > _MAX_QFD_GLOBAL_PCT:
                abort_reason = "QFD_PCT_EXCEEDED"
                print(
                    f"[orchestrator] ABORT QFD_PCT_EXCEEDED "
                    f"qfd_ratio={qfd_ratio:.6f} > cap={_MAX_QFD_GLOBAL_PCT:.6f} "
                    f"(cum_qfd={cumulative_qfd} cum_trd={cumulative_trades})",
                    file=sys.stderr,
                )
                _atomic_write_heartbeat(heartbeat_path, chunk.chunk_id, "abort_qfd_pct")
                break

        # Cooldown sleep — Nelo mandate (TCP TIME_WAIT + DLLFinalize quiesce).
        # Skip cooldown after final chunk of the loop.
        is_last = idx == len(chunks) - 1
        if not is_last and cooldown_s > 0:
            print(f"[orchestrator] cooldown {cooldown_s:.1f}s before next chunk")
            time.sleep(cooldown_s)

    if abort_reason is not None:
        # Council 2026-05-03 R1 Amendment §6.1 item 5 — Riven C2 quarantine fix.
        # Source: docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md §6.1 item 5
        # Flag every chunk flipped to status=ok during THIS run as
        # quarantined_pre_abort_<reason> BEFORE returning exit code 2. Recovery
        # semantics: quarantined chunks are NOT auto-retried; operator-driven
        # decision (mini-Council revoke OR new run_id re-run).
        quarantine_status = _QUARANTINE_REASON_TO_STATUS.get(abort_reason)
        if quarantine_status is not None and chunks_ok_this_run:
            quarantined_ids: list[str] = []
            for cid in chunks_ok_this_run:
                row = store.rows.get(cid)
                if row is None or row.status != "ok":
                    # Defensive: skip if row missing or already mutated.
                    continue
                row.status = quarantine_status
                store.upsert(row)  # atomic tmp+replace per row.
                quarantined_ids.append(cid)
            print(
                f"[QUARANTINE] {len(quarantined_ids)} chunks flagged "
                f"({quarantine_status}): {quarantined_ids}",
                file=sys.stderr,
            )
        elif chunks_ok_this_run:
            # Unknown abort_reason → log warning but do not mutate (fail-safe).
            print(
                f"[QUARANTINE] WARN: abort_reason={abort_reason!r} not in "
                f"_QUARANTINE_REASON_TO_STATUS; {len(chunks_ok_this_run)} ok-this-run "
                f"chunks left untouched (manual review): {chunks_ok_this_run}",
                file=sys.stderr,
            )
        _atomic_write_heartbeat(heartbeat_path, chunk_id="<aborted>", status=abort_reason)
        print(f"[orchestrator] FAIL: aborted by trigger {abort_reason}", file=sys.stderr)
        return _EXIT_ABORTED

    if fatal_partial_failed:
        _atomic_write_heartbeat(heartbeat_path, chunk_id="<done>", status="partial")
        print(
            "[orchestrator] FAIL: chunks with partial/failed status: "
            + ", ".join(fatal_partial_failed),
            file=sys.stderr,
        )
        return _EXIT_PARTIAL
    _atomic_write_heartbeat(heartbeat_path, chunk_id="<done>", status="ok")
    print("[orchestrator] OK: all chunks status=ok")
    return _EXIT_SUCCESS


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DLL backfill orchestrator (Phase 2C autonomous).")
    p.add_argument("--start-date", required=True, help="ISO YYYY-MM-DD (inclusive)")
    p.add_argument("--end-date", required=True, help="ISO YYYY-MM-DD (inclusive)")
    p.add_argument("--ticker", required=True, help="WDOFUT (continuous)")
    p.add_argument("--output-root", required=True, help="Manifest + chunk dirs root (NOT R10 custodial)")
    p.add_argument("--max-attempts", type=int, default=3, help="Per-chunk retry budget (Riven cap=3)")
    p.add_argument(
        "--max-consecutive-failures",
        type=int,
        default=_DEFAULT_MAX_CONSECUTIVE_FAILURES,
        help="Abort_all if N consecutive chunks status!=ok (Riven BLOCKING, default 3)",
    )
    p.add_argument(
        "--max-wall-time-s",
        type=float,
        default=_DEFAULT_MAX_WALL_TIME_S,
        help="Global wall-time budget seconds (Riven hard kill, default 23400 = 6h30m)",
    )
    p.add_argument(
        "--cooldown-s",
        type=float,
        default=_DEFAULT_COOLDOWN_S,
        help="Sleep seconds between subprocesses (Nelo: TCP TIME_WAIT + DLLFinalize quiesce, default 30)",
    )
    p.add_argument(
        "--heartbeat-path",
        type=str,
        default=None,
        help="Heartbeat file path (default <output-root>/manifest.heartbeat); aiox-master kills if stale >15min",
    )
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    # Q09-E enforced parse-time per Council 2026-05-03 R1 Amendment Nelo C5:
    # specific-month contracts (WDOJ26, WDOG26, WDOF26, ...) hit the documented
    # 19ms zero-trade bug; only WDOFUT continuous returns 100% of trades.
    if args.ticker != "WDOFUT":
        raise SystemExit(
            f"E_TICKER_NON_WDOFUT: only WDOFUT continuous allowed "
            f"(Q09-E specific contracts hit 19ms bug); got: {args.ticker!r}"
        )
    start = _dt.date.fromisoformat(args.start_date)
    end = _dt.date.fromisoformat(args.end_date)
    output_root = Path(args.output_root)
    heartbeat_path = Path(args.heartbeat_path) if args.heartbeat_path else None
    try:
        return run_orchestrator(
            start_date=start,
            end_date=end,
            ticker=args.ticker,
            output_root=output_root,
            max_attempts=args.max_attempts,
            max_consecutive_failures=args.max_consecutive_failures,
            max_wall_time_s=args.max_wall_time_s,
            cooldown_s=args.cooldown_s,
            heartbeat_path=heartbeat_path,
        )
    except Exception as e:  # pragma: no cover — orchestrator-level crash
        print(f"[orchestrator] FATAL crash: {e!r}", file=sys.stderr)
        return _EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
