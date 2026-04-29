"""CPCV dry-run executor — Beckett ``*run-cpcv --dry-run`` invocation script.

Story: T002.0f T3 (final integration km).
Spec:  docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml v0.2.0
Memory protocol: feedback_cpcv_dry_run_memory_protocol.md (6 GiB soft halt + psutil 30s telemetry)
Hold-out: R1 + R15(d) — defense-in-depth via ``_holdout_lock.assert_holdout_safe``.

This script wires:
    spec.yaml + engine-config + cost-atlas + calendar + warmup state
        ↓
    build_events_dataframe (warmup gate + Nova session validity)
        ↓
    make_backtest_fn (Nova cost-atlas + per-fold P126 closure)
        ↓
    run_5_trial_fanout (BacktestRunner uniform DeterminismStamp)
        ↓
    compute_full_report (Mira squad-cumulative DSR + BBLZ PBO + KillDecision)
        ↓
    persist artifacts (telemetry, full_report.{md,json}, determinism_stamp.json,
                       events_metadata.json) under data/baseline-run/cpcv-dryrun-{run_id}/

Exit codes (AC7, AC8, AC11, AC13):
    0 — PASS (FullReport emitted, KillDecision computed, no soft-halt)
    1 — HALT  (mem soft-cap exceeded OR warmup failure OR hold-out violation
               OR smoke failure aborting full run)
    2 — DETERMINISM violation (spec_sha256 mismatch vs prior run in same --run-id dir)
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import hashlib
import json
import os
import sys
import threading
import time
from dataclasses import asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Ensure scripts/ is importable so we use the canonical _holdout_lock
# implementation that the rest of the pipeline grep'd against (R15(d)).
_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from _holdout_lock import (  # noqa: E402  (sys.path injection above)
    HoldoutLockError,
    assert_holdout_safe,
)

# psutil is the canonical memory poller; per AC8 + memory protocol it is
# imported at module top-level so test patches via mocker hit the right
# binding. We do NOT silently degrade if psutil is missing — the dry-run
# protocol REQUIRES the poller per feedback_cpcv_dry_run_memory_protocol.md.
import psutil  # noqa: E402  (post-sys.path)
import yaml    # noqa: E402

from packages.t002_eod_unwind.adapters.exec_backtest import BacktestCosts  # noqa: E402
from packages.t002_eod_unwind.cpcv_harness import (  # noqa: E402
    TRIALS_DEFAULT,
    _build_daily_metrics_from_train_events,
    build_events_dataframe,
    make_backtest_fn,
    run_5_trial_fanout,
)
from packages.t002_eod_unwind.warmup.calendar_loader import (  # noqa: E402
    CalendarData,
    CalendarLoader,
)
from packages.t002_eod_unwind.warmup.gate import WarmUpGate  # noqa: E402
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (  # noqa: E402
    Percentiles126dBuilder,
    Percentiles126dState,
)
from packages.vespera_cpcv import CPCVSplit  # noqa: E402
from packages.vespera_cpcv import BacktestRunner, CPCVConfig  # noqa: E402
from packages.vespera_metrics import (  # noqa: E402
    FullReport,
    ReportConfig,
    compute_full_report,
)


# =====================================================================
# Constants — story-locked defaults
# =====================================================================
DEFAULT_SOFT_CAP_GB: float = 6.0  # AC8 + memory protocol
DEFAULT_POLL_INTERVAL_S: float = 30.0  # AC8 + memory protocol
DEFAULT_SEED: int = 42  # Beckett T0 handshake (CI repro)
DEFAULT_OUTPUT_ROOT: Path = Path("data/baseline-run")
DEFAULT_SMOKE_DAYS: int = 30  # AC10 1-month subset

# Telemetry CSV header — Pax gap #2: SUPERSET satisfying both the story
# (rss_mb, vms_mb, cpu_pct, fold_index, trial_id) AND the memory
# protocol (peak_commit_bytes, peak_wset_bytes, sample_size, duration_ms).
TELEMETRY_COLUMNS: tuple[str, ...] = (
    "timestamp_brt",
    "rss_mb",
    "vms_mb",
    "cpu_pct",
    "peak_commit_bytes",
    "peak_wset_bytes",
    "sample_size",
    "duration_ms",
    "fold_index",
    "trial_id",
    "phase",
    "note",
)

# Default file paths used when caller omits --warmup-* overrides.
#
# T002.0g AC6 atomic path lift (Aria + Beckett T0) — canonical state/T002/
# replaces legacy data/warmup/. R15 non-breaking — overridable via
# --warmup-atr / --warmup-percentiles. Resolves T002.0f T11 finding HIGH
# (path mismatch between materializer output and harness consumer).
#
# T002.0h.1 AC2 (E1 harness amendment) — these constants are now **CLI
# affordance only**. WarmUpGate semantics resolve via the dated path
# helpers ``_dated_atr_path`` / ``_dated_percentiles_path`` per-phase.
# When the operator omits ``--warmup-atr`` / ``--warmup-percentiles``,
# these defaults are detected as the legacy sentinels and substituted
# for the per-phase dated paths inside ``_run_phase``. When the operator
# explicitly passes a non-default override, it is honoured verbatim
# (operator authority for ad-hoc state files). See Aria T1 design memo
# in docs/stories/T002.0h.1.story.md.
_DEFAULT_ATR_PATH = Path("state/T002/atr_20d.json")
_DEFAULT_PERCENTILES_PATH = Path("state/T002/percentiles_126d.json")
_DEFAULT_CALENDAR_PATH = Path("config/calendar/2024-2027.yaml")
_DEFAULT_ENGINE_CONFIG = Path("docs/backtest/engine-config.yaml")

# T002.0h.1 AC2 — canonical state directory + cache_audit consumer file.
_STATE_DIR = Path("state/T002")
_CACHE_AUDIT_FILENAME = "cache_audit.jsonl"


def _dated_atr_path(as_of_date: date) -> Path:
    """Canonical ATR_20d state path bound to a specific ``as_of_date``.

    Returns ``state/T002/atr_20d_{as_of}.json`` matching the producer-side
    naming convention in ``scripts/run_warmup_state.py`` (per-as_of dated
    outputs). This is the canonical lookup for ``WarmUpGate`` per-phase
    semantics (T002.0h.1 AC2). The legacy ``_DEFAULT_ATR_PATH`` is retained
    as CLI affordance only and is NOT used by the gate under default
    invocation.
    """
    return _STATE_DIR / f"atr_20d_{as_of_date.isoformat()}.json"


def _dated_percentiles_path(as_of_date: date) -> Path:
    """Canonical Percentiles_126d state path bound to a specific ``as_of_date``.

    Returns ``state/T002/percentiles_126d_{as_of}.json`` matching the
    producer-side naming convention in ``scripts/run_warmup_state.py``.
    Canonical lookup for ``WarmUpGate`` per-phase semantics (T002.0h.1 AC2).
    Legacy ``_DEFAULT_PERCENTILES_PATH`` retained as CLI affordance only.
    """
    return _STATE_DIR / f"percentiles_126d_{as_of_date.isoformat()}.json"


def _resolve_warmup_path(cli_arg: Path, dated_default: Path) -> Path:
    """Resolve effective warmup path for per-phase ``WarmUpGate``.

    Per Aria T1 design memo §1: if the caller passed the legacy default
    constant (i.e., omitted the override on the CLI), substitute the
    dated default for the phase. Otherwise honour the operator override
    verbatim (preserves CLI affordance for ad-hoc operator runs with
    hand-crafted state files).

    Invariant — gate semantics MUST resolve to the dated path on default
    invocation; operator-override path MUST be honoured verbatim. This
    detection is by *path equality*: the argparse default sentinels are
    ``_DEFAULT_ATR_PATH`` / ``_DEFAULT_PERCENTILES_PATH``.
    """
    if cli_arg in (_DEFAULT_ATR_PATH, _DEFAULT_PERCENTILES_PATH):
        return dated_default
    return cli_arg


def _append_consumer_cache_audit(
    audit_dir: Path,
    *,
    as_of: date,
    phase: str,
    status: str,
    expected_key: dict[str, str] | None,
    found_key: dict[str, str] | None,
    note: str = "",
) -> None:
    """Append a consumer-side ``cache_audit.jsonl`` entry tagged with ``phase``.

    T002.0h.1 AC3 — consumer-side audit emission tagged with phase
    (``"smoke" | "full"``). The producer-side ``_append_cache_audit`` in
    ``scripts/run_warmup_state.py`` is **untouched** (Aria memo §3 — keep
    producer schema canonical, consumer audit is a separate enrichment).

    Schema (additive ``phase`` field; existing fields preserved verbatim):
        ``{computed_at_brt, as_of_date, status, expected_key, found_key,
        note, phase}``

    ``status`` for consumer entries is by convention ``"consumer_check"``
    (does not collide with producer enum ``{hit, miss, stale, write,
    force_rebuild}``). Best-effort append — IO failure logs nothing and
    continues (audit is observability, NOT a correctness contract).
    """
    entry = {
        "computed_at_brt": datetime.now().isoformat(timespec="seconds"),
        "as_of_date": as_of.isoformat(),
        "status": status,
        "expected_key": expected_key,
        "found_key": found_key,
        "note": note,
        "phase": phase,
    }
    audit_path = audit_dir / _CACHE_AUDIT_FILENAME
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        with audit_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        # Best-effort write per producer-side convention; audit is
        # observability-only and must never break the gate decision.
        pass


# =====================================================================
# Argparse (AC7)
# =====================================================================
def build_arg_parser() -> argparse.ArgumentParser:
    """Return the canonical argparse parser for the dry-run CLI.

    Per AC7 + Beckett T0 handshake non-blocking adds (--seed,
    --mem-soft-cap-gb). Exposed as a function so test_argparse_*
    can introspect without invoking the runtime.
    """
    p = argparse.ArgumentParser(
        prog="run_cpcv_dry_run",
        description=(
            "Execute Beckett *run-cpcv --dry-run pipeline: warmup gate → "
            "events → 5-trial × 45-path CPCV fan-out → compute_full_report → "
            "KillDecision, with psutil 30s telemetry + 6 GiB soft halt."
        ),
    )
    p.add_argument(
        "--spec",
        type=Path,
        required=True,
        help="Path to spec yaml (e.g. docs/ml/specs/T002-...-v0.2.0.yaml).",
    )
    p.add_argument(
        "--dry-run",
        dest="dry_run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Enable dry-run mode (default). --no-dry-run disables psutil "
            "polling for performance benchmarks."
        ),
    )
    p.add_argument(
        "--in-sample-start",
        type=_parse_iso_date,
        default=None,
        help="Override in-sample start (YYYY-MM-DD). Default: read spec data_splits.in_sample.",
    )
    p.add_argument(
        "--in-sample-end",
        type=_parse_iso_date,
        default=None,
        help="Override in-sample end inclusive (YYYY-MM-DD). Default: read spec data_splits.in_sample.",
    )
    p.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Run a 1-month subset (in_sample_end - 30d) before any full run. "
            "Smoke failure aborts the full run (AC11)."
        ),
    )
    p.add_argument(
        "--run-id",
        type=str,
        default=None,
        help=(
            "Override run id (used as cpcv-dryrun-{run_id} subdir name). "
            "Default: deterministic hash of (spec_sha256[:8], window, seed)."
        ),
    )
    p.add_argument(
        "--mem-poll-interval-s",
        type=float,
        default=DEFAULT_POLL_INTERVAL_S,
        help=f"psutil poller cadence in seconds (default {DEFAULT_POLL_INTERVAL_S}).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Override CPCVConfig.seed (default {DEFAULT_SEED}).",
    )
    p.add_argument(
        "--mem-soft-cap-gb",
        type=float,
        default=DEFAULT_SOFT_CAP_GB,
        help=(
            f"Soft halt threshold in GiB (default {DEFAULT_SOFT_CAP_GB}). "
            "R3 mitigation: configurable to dampen Windows RSS false-positive."
        ),
    )
    p.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Root directory for run artifacts (default {DEFAULT_OUTPUT_ROOT}).",
    )
    # The following are NOT in the story AC7 contract but are needed
    # for non-default test fixtures. Defaults preserve prod behaviour.
    p.add_argument(
        "--calendar",
        type=Path,
        default=_DEFAULT_CALENDAR_PATH,
        help="Calendar YAML path (default config/calendar/2024-2027.yaml).",
    )
    p.add_argument(
        "--engine-config",
        type=Path,
        default=_DEFAULT_ENGINE_CONFIG,
        help="engine-config.yaml path (Nova cost-atlas wire).",
    )
    p.add_argument(
        "--warmup-atr",
        type=Path,
        default=_DEFAULT_ATR_PATH,
        help="ATR_20d warmup state path.",
    )
    p.add_argument(
        "--warmup-percentiles",
        type=Path,
        default=_DEFAULT_PERCENTILES_PATH,
        help="Percentiles_126d warmup state path.",
    )
    return p


def _parse_iso_date(value: str) -> date:
    """argparse type for YYYY-MM-DD strings; raises argparse.ArgumentTypeError on bad input."""
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError(
            f"invalid ISO date {value!r}; expected YYYY-MM-DD"
        ) from exc


# =====================================================================
# Spec parsing (AC7 default window) + sha256 lock (AC13)
# =====================================================================
def compute_spec_sha256(spec_path: Path) -> str:
    """SHA-256 of the spec file bytes (matches BacktestRunner._hash_file)."""
    h = hashlib.sha256()
    with spec_path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_in_sample_window(spec_path: Path) -> tuple[date, date]:
    """Read ``data_splits.in_sample`` from the spec yaml.

    Format per spec v0.2.0 L93: ``"YYYY-MM-DD to YYYY-MM-DD"``.
    Raises ValueError if the field is missing or malformed.
    """
    with spec_path.open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    if not isinstance(spec, dict):
        raise ValueError(f"spec yaml root is not a mapping: {spec_path}")
    splits = spec.get("data_splits")
    if not isinstance(splits, dict) or "in_sample" not in splits:
        raise ValueError(
            f"spec {spec_path} missing data_splits.in_sample (required for "
            "default window — pass --in-sample-start/end to override)"
        )
    raw = str(splits["in_sample"]).strip()
    parts = [p.strip() for p in raw.split(" to ")]
    if len(parts) != 2:
        raise ValueError(
            f"data_splits.in_sample {raw!r} not in 'YYYY-MM-DD to YYYY-MM-DD' format"
        )
    return date.fromisoformat(parts[0]), date.fromisoformat(parts[1])


def assert_spec_lock(stamp_path: Path, current_sha: str) -> None:
    """Per AC13: if a prior determinism_stamp.json exists in this run dir
    and its ``spec_sha256`` differs from ``current_sha``, raise SystemExit(2).

    Idempotent re-runs with identical specs PASS (the stamp is rewritten
    with the same value). Spec drift between runs sharing a --run-id is
    a determinism violation.
    """
    if not stamp_path.exists():
        return  # first run — nothing to compare against
    try:
        prior = json.loads(stamp_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return  # corrupted prior stamp — treat as first run, do not block
    prior_sha = prior.get("spec_sha256", "")
    if prior_sha and prior_sha != current_sha:
        raise SystemExit(
            2  # exit code 2 per AC7 — determinism violation
        )


# =====================================================================
# Default --run-id derivation (deterministic; story Decisão T0 Beckett)
# =====================================================================
def derive_default_run_id(
    spec_sha256: str,
    in_sample_start: date,
    in_sample_end: date,
    seed: int,
) -> str:
    """Deterministic --run-id default — avoids uuid.uuid4 (Beckett T0 + R6).

    The id is a short hash of the canonical run inputs so that re-running
    with identical args lands in the same artifact dir (which then
    triggers the AC13 spec lock check correctly). Override via --run-id
    when the operator needs ad-hoc isolation.
    """
    payload = f"{spec_sha256}|{in_sample_start.isoformat()}|{in_sample_end.isoformat()}|{seed}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    # Prefix with a date stamp to keep filesystem listings human-readable.
    return f"auto-{datetime.now().strftime('%Y%m%d')}-{digest}"


# =====================================================================
# Memory poller (AC8) — psutil daemon thread + telemetry CSV writer
# =====================================================================
class MemoryPoller:
    """psutil-backed memory poller writing telemetry CSV at a fixed cadence.

    Per AC8 + feedback_cpcv_dry_run_memory_protocol.md:
      - cadence configurable via --mem-poll-interval-s (default 30s)
      - emits one CSV row per tick + one row per phase transition (start,
        smoke_complete, fold_complete, halt, end)
      - sets ``halt_event`` when RSS exceeds ``soft_cap_bytes`` so the
        orchestrator can persist current state and HALT GRACEFULLY
        (NOT kill -9 — explicit per AC8)

    The class is daemon-thread based (background) with a stop event
    (``shutdown_event``) for clean teardown. The thread also exposes
    ``halt_event`` (set when soft cap exceeded) which the orchestrator
    polls between trials/folds.
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
        self._current_fold_index: int = -1
        self._current_trial_id: str = ""
        self._sample_count: int = 0
        self._peak_rss: int = 0
        self._peak_vms: int = 0

        # Initialize CSV with header on first construction (truncate prior
        # content) so re-runs in the same dir start clean — Article IV:
        # we never silently merge poller history across runs.
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(TELEMETRY_COLUMNS)

    # -----------------------------------------------------------------
    # Phase / context updates (called from main thread)
    # -----------------------------------------------------------------
    def set_phase(self, phase: str, *, fold_index: int = -1, trial_id: str = "") -> None:
        with self._lock:
            self._current_phase = phase
            self._current_fold_index = fold_index
            self._current_trial_id = trial_id

    def write_event(self, *, phase: str, note: str = "") -> None:
        """Force a synchronous telemetry row (independent of poll cadence)."""
        self._write_row(phase=phase, note=note)

    # -----------------------------------------------------------------
    # Thread lifecycle
    # -----------------------------------------------------------------
    def start(self) -> None:
        if not self.enabled:
            return
        self._thread = threading.Thread(
            target=self._run_loop, name="cpcv-memory-poller", daemon=True
        )
        self._thread.start()

    def stop(self, *, timeout: float = 5.0) -> None:
        self.shutdown_event.set()
        t = self._thread
        if t is not None and t.is_alive():
            t.join(timeout=timeout)

    # -----------------------------------------------------------------
    # Internals
    # -----------------------------------------------------------------
    def _run_loop(self) -> None:
        # Poll until shutdown is requested. We use Event.wait so that
        # stop() can break the loop within poll_interval_s instead of
        # blocking the orchestrator on join().
        while not self.shutdown_event.is_set():
            self._write_row(phase=self._current_phase, note="poll")
            # Event.wait returns True when set; that's our shutdown signal.
            if self.shutdown_event.wait(timeout=self.poll_interval_s):
                break

    def _write_row(self, *, phase: str, note: str) -> None:
        try:
            proc = psutil.Process()
            mem = proc.memory_info()
            cpu = proc.cpu_percent(interval=None)
        except Exception as exc:  # noqa: BLE001 — diagnostic write must not crash
            # Article IV: do not invent values — record the failure.
            self._safe_csv_append(
                [
                    datetime.now().isoformat(timespec="seconds"),
                    "", "", "", "", "", "", "",
                    self._current_fold_index,
                    self._current_trial_id,
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
            fold_idx = self._current_fold_index
            trial_id = self._current_trial_id

        # Per AC8 — soft halt threshold. We set halt_event so the
        # orchestrator's between-trial check can persist + abort.
        # We DO NOT raise — graceful halt requires the caller to react.
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
                str(peak_rss),  # peak_commit_bytes (memory protocol naming)
                str(peak_vms),  # peak_wset_bytes (memory protocol naming)
                str(sample_size),
                "0",  # duration_ms — populated by event-based writes only
                str(fold_idx),
                trial_id,
                phase,
                soft_halt_note,
            ]
        )

    def _safe_csv_append(self, row: list[Any]) -> None:
        """Append a row to the CSV; survive concurrent writes from main thread."""
        try:
            with self.csv_path.open("a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(row)
        except OSError:
            # If the disk vanishes, the run is doomed anyway — let the
            # main thread surface the failure via its own IO. We don't
            # raise here because the poller is daemon: an exception
            # would silently kill telemetry without flagging the cause.
            pass


# =====================================================================
# Pipeline assembly (shared between smoke + full)
# =====================================================================
def _load_warmup_state(percentiles_path: Path) -> Percentiles126dState:
    """Load canonical ``Percentiles126dState`` from JSON — fail-closed.

    T002.0g Anti-Article-IV Guard #1 (story §Anti-Article-IV Guards):
        Dex MUST NOT improvise neutral PercentilesState fallback if
        parquet missing — escalate (resolves Beckett T11 issue #3).

    T002.0h.1 AC2 — under per-phase usage the ``percentiles_path`` arg
    is now phase-specific dated path resolved from ``as_of_date`` (e.g.,
    ``state/T002/percentiles_126d_2024-08-22.json`` for full phase or
    ``state/T002/percentiles_126d_2025-05-31.json`` for smoke phase),
    NOT the legacy default-path singleton. Function semantics are
    UNCHANGED — only the path argument value changes per phase. The
    triple-key cache contract (Mira AC9) is preserved per-phase via the
    sidecar ``_cache_key_{as_of}.json`` validated upstream by the
    producer; consumer-side this function only deserializes the dated
    state file and raises fail-closed on missing/corrupt.

    The prior implementation silently fell back to neutral bands
    (p20=1.0/p60=2.0/p80=3.0) when the file was missing OR when
    deserialization failed. That fallback is REMOVED — both failure
    modes now raise, so the operator sees the gap immediately and either
    (a) runs ``scripts/run_warmup_state.py`` to materialize state, or
    (b) escalates upstream data coverage (USER-ESCALATION-QUEUE.md).

    Raises
    ------
    FileNotFoundError
        ``percentiles_path`` does not exist. Operator should run
        ``python scripts/run_warmup_state.py --as-of-dates <D>`` to
        materialize state first.
    ValueError
        File exists but JSON deserialization failed (corrupt/schema
        drift). Anti-Article-IV: do NOT improvise; surface the parse
        error so root cause is visible.
    """
    if not percentiles_path.exists():
        raise FileNotFoundError(
            f"warmup state missing: {percentiles_path}. "
            "Run scripts/run_warmup_state.py --as-of-dates <YYYY-MM-DD> "
            "to materialize before invoking the CPCV dry-run "
            "(T002.0g Anti-Article-IV Guard #1)."
        )
    try:
        data = json.loads(percentiles_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(
            f"warmup state corrupt at {percentiles_path}: {exc}. "
            "Re-run scripts/run_warmup_state.py to regenerate "
            "(T002.0g Anti-Article-IV Guard #1: NO neutral fallback)."
        ) from exc
    try:
        return Percentiles126dState.from_json(data)
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError(
            f"warmup state schema drift at {percentiles_path}: {exc}. "
            "Re-run scripts/run_warmup_state.py with current builders."
        ) from exc


def _load_costs(engine_config_path: Path) -> BacktestCosts:
    """Load Nova cost-atlas v1.0.0 via engine-config; fall back to defaults if missing.

    Production runs MUST have the engine-config + atlas wired (T002.0e).
    The fallback is gated on file existence so test fixtures without the
    real atlas can still exercise the pipeline.
    """
    if engine_config_path.exists():
        try:
            return BacktestCosts.from_engine_config(engine_config_path)
        except FileNotFoundError:
            pass
    return BacktestCosts()  # deprecated defaults — docstring warned


def _build_runner(
    spec_path: Path,
    engine_config_path: Path,
    seed: int,
    run_id: str,
) -> BacktestRunner:
    """Construct BacktestRunner with full provenance for DeterminismStamp."""
    cfg = CPCVConfig.from_spec_yaml(spec_path, seed=seed)
    return BacktestRunner(
        config=cfg,
        spec_path=spec_path,
        spec_version="0.2.0",
        simulator_version="cpcv-dry-run-T002.0f-T3",
        engine_config_path=engine_config_path if engine_config_path.exists() else None,
    )


# =====================================================================
# Artifact persistence (AC12)
# =====================================================================
def _serialize_full_report(report: FullReport) -> dict[str, Any]:
    """Convert FullReport to a JSON-safe dict (numpy → list, etc.)."""
    m = report.metrics
    kd = report.kill_decision
    metrics_dict = {
        "ic_spearman": float(m.ic_spearman),
        "ic_spearman_ci95": [float(m.ic_spearman_ci95[0]), float(m.ic_spearman_ci95[1])],
        "dsr": float(m.dsr),
        "pbo": float(m.pbo),
        "sharpe_per_path": [float(x) for x in m.sharpe_per_path.tolist()],
        "sharpe_mean": float(m.sharpe_mean),
        "sharpe_median": float(m.sharpe_median),
        "sharpe_std": float(m.sharpe_std),
        "sortino": float(m.sortino),
        "mar": float(m.mar),
        "ulcer_index": float(m.ulcer_index),
        "max_drawdown": float(m.max_drawdown),
        "profit_factor": float(m.profit_factor),
        "hit_rate": float(m.hit_rate),
        "n_paths": int(m.n_paths),
        "n_pbo_groups": int(m.n_pbo_groups),
        "n_trials_used": int(m.n_trials_used),
        "n_trials_source": m.n_trials_source,
        "seed_bootstrap": int(m.seed_bootstrap),
        "spec_version": m.spec_version,
        "computed_at_brt": m.computed_at_brt,
    }
    kd_dict = {
        "verdict": kd.verdict,
        "reasons": list(kd.reasons),
        "k1_dsr_passed": bool(kd.k1_dsr_passed),
        "k2_pbo_passed": bool(kd.k2_pbo_passed),
        "k3_ic_decay_passed": bool(kd.k3_ic_decay_passed),
    }
    return {
        "metrics": metrics_dict,
        "kill_decision": kd_dict,
        "n_per_path_results": len(report.per_path_results),
    }


def _serialize_determinism_stamp(stamp: Any) -> dict[str, Any]:
    """Convert DeterminismStamp to JSON dict; coerce datetime to ISO string."""
    d = asdict(stamp) if dataclasses.is_dataclass(stamp) else dict(stamp)
    if isinstance(d.get("timestamp_brt"), datetime):
        d["timestamp_brt"] = d["timestamp_brt"].isoformat(timespec="seconds")
    return d


def persist_artifacts(
    out_dir: Path,
    *,
    full_report: FullReport,
    determinism_stamp: Any,
    events_metadata: dict[str, Any],
) -> None:
    """Write full_report.{md,json}, determinism_stamp.json, events_metadata.json.

    Per AC12 — telemetry.csv is written by MemoryPoller; this writes the
    other 4 artifacts. All writes are atomic-enough (write whole file)
    for the dry-run footprint; concurrent runs MUST use distinct
    --run-id values (the AC13 lock catches accidental re-use).
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "full_report.md").write_text(
        full_report.to_markdown(), encoding="utf-8"
    )
    (out_dir / "full_report.json").write_text(
        json.dumps(_serialize_full_report(full_report), indent=2),
        encoding="utf-8",
    )
    (out_dir / "determinism_stamp.json").write_text(
        json.dumps(_serialize_determinism_stamp(determinism_stamp), indent=2),
        encoding="utf-8",
    )
    (out_dir / "events_metadata.json").write_text(
        json.dumps(events_metadata, indent=2, default=str), encoding="utf-8"
    )


# =====================================================================
# Phase runners (smoke + full share this body via window param)
# =====================================================================
def _run_phase(
    *,
    label: str,
    spec_path: Path,
    engine_config_path: Path,
    in_sample_start: date,
    in_sample_end: date,
    calendar: CalendarData,
    seed: int,
    run_id: str,
    poller: MemoryPoller,
    as_of_date: date,
    warmup_atr_cli: Path = _DEFAULT_ATR_PATH,
    warmup_percentiles_cli: Path = _DEFAULT_PERCENTILES_PATH,
) -> tuple[FullReport, Any, dict[str, Any]]:
    """Execute one phase (smoke or full): events → fan-out → report.

    T002.0h.1 AC1 / AC2 — per-phase ``WarmUpGate`` ownership semantics.
    Each call constructs its **own** ``WarmUpGate`` instance bound to the
    dated path resolved from ``as_of_date`` (smoke and full are independent
    gate decisions, never share the same gate instance). This eliminates
    the Track A structural defect surfaced by Beckett N4 (singleton at the
    legacy ``:848`` site forced both phases to share the same default
    path → strict-equality false-failure when smoke and full required
    distinct as_of dates).

    The CLI override sentinels (``warmup_atr_cli`` / ``warmup_percentiles_cli``)
    are routed through ``_resolve_warmup_path`` — when they equal the
    legacy default constants, dated paths from ``_dated_*_path(as_of_date)``
    are used; otherwise the operator override is honoured verbatim
    (CLI affordance preserved).

    Per AC3, this function emits a consumer-side ``cache_audit.jsonl``
    entry tagged with ``phase ∈ {"smoke", "full"}`` (additive enrichment;
    producer-side schema and triple-key contract untouched).

    Per AC7 / AC9 — ``_load_warmup_state`` semantics are NOT modified;
    only the path bound to the gate changes (default → dated). Gate
    strict-equality fail-closed semantics in ``WarmUpGate._check_file``
    are preserved verbatim.

    Returns ``(full_report, determinism_stamp, events_metadata)``. Raises
    on any failure; caller maps to exit code 1 (HALT) per AC8/AC11.
    """
    # T002.0h.1 AC1 — construct phase-local WarmUpGate against dated paths.
    atr_path = _resolve_warmup_path(warmup_atr_cli, _dated_atr_path(as_of_date))
    pct_path = _resolve_warmup_path(
        warmup_percentiles_cli, _dated_percentiles_path(as_of_date)
    )
    warmup_gate = WarmUpGate(atr_path, pct_path)

    # T002.0h.1 AC3 — consumer-side audit entry (additive `phase` field).
    # Best-effort write — observability only; never affects gate decision.
    _append_consumer_cache_audit(
        _STATE_DIR,
        as_of=as_of_date,
        phase=label,
        status="consumer_check",
        expected_key=None,
        found_key=None,
        note=(
            f"atr={atr_path.as_posix()};pct={pct_path.as_posix()};"
            f"window={in_sample_start.isoformat()}..{in_sample_end.isoformat()}"
        ),
    )

    poller.set_phase(f"{label}:events")
    poller.write_event(phase=f"{label}:events_start", note=f"window={in_sample_start}..{in_sample_end}")

    events = build_events_dataframe(
        in_sample_start,
        in_sample_end,
        TRIALS_DEFAULT,
        calendar=calendar,
        warmup_gate=warmup_gate,
    )
    n_events = int(len(events))
    n_trials = int(events["trial_id"].nunique())

    poller.write_event(phase=f"{label}:events_built", note=f"n_events={n_events}")

    # Cost atlas + per-fold P126 rebuild via backtest_fn_factory.
    # T002.0g Guard #1: NO neutral fallback — _load_warmup_state raises if missing/corrupt.
    # T002.0h.1 AC2 — `pct_path` is the phase-local dated percentiles path
    # resolved above (default → dated; operator override honoured verbatim).
    # T002.1.bis — per Aria T0b APPROVE_OPTION_B (DEFERRED-T11 M1 fix), each
    # fold receives its own ``Percentiles126dState`` rebuilt from the fold's
    # train slice (``as_of_date == first_test_session_of_fold`` per Mira
    # spec §3.1 anti-leak invariant). The cached warmup state at ``pct_path``
    # is the global-window baseline (Beckett N5 backward compat / fallback);
    # the factory below uses the **fold-local** rebuild for the engine
    # per-fold dispatch, but falls back to the global state when the fold
    # train slice is too small (< 126 valid days) so smoke runs over short
    # windows still execute end-to-end.
    costs = _load_costs(engine_config_path)
    p126_global = _load_warmup_state(pct_path)
    p126_builder = Percentiles126dBuilder(calendar)

    def _backtest_fn_factory(split: CPCVSplit, train_events):
        """Per-fold factory — rebuilds P126 from THIS fold's train slice.

        Per Aria T0b APPROVE_OPTION_B + Mira spec §3.1 + §6.1:
          1. Reduce ``train_events`` to per-day ``DailyMetrics`` via
             ``_build_daily_metrics_from_train_events`` (fold-local).
          2. ``as_of_date`` = first session of fold's TEST slice (D-1
             anti-leak invariant — Mira spec §3.4).
          3. Rebuild ``Percentiles126dState`` via ``Percentiles126dBuilder.build``.
             When the fold has < 126 valid days (smoke / short windows),
             fall back to the global cached state — preserves N5 wall-time
             baseline + Beckett T0c projection.
          4. Wrap the existing pure ``make_backtest_fn`` closure with
             fold-local state.
        """
        # 1. Per-day metrics (fold-local, anchored to split.path_id for
        # determinism + cross-fold distinguishability).
        metrics = _build_daily_metrics_from_train_events(
            train_events, seed_anchor=split.path_id
        )
        # 2. as_of_date = min(test_events.session) per Mira §3.4 D-1 invariant.
        if "session" in split.test_events.columns and len(split.test_events) > 0:
            as_of_date = min(split.test_events["session"])
        else:
            as_of_date = p126_global.as_of_date
        # 3. Rebuild P126 — fall back to global state when train slice is
        # too small (< 126 valid days; common in --smoke runs).
        try:
            fold_p126 = p126_builder.build(
                metrics=metrics,
                as_of_date=as_of_date,
                now_brt=p126_global.computed_at_brt,
            )
        except ValueError:
            fold_p126 = p126_global
        # 4. Per-fold closure bound to fold-local state.
        return make_backtest_fn(costs, calendar, fold_p126)

    runner = _build_runner(spec_path, engine_config_path, seed, run_id)

    # Per AC8 — check the halt flag between phase boundaries; this gives
    # the poller a chance to surface 6 GiB before kicking off the heavy
    # 5-trial fan-out.
    if poller.halt_event.is_set():
        raise MemoryError(
            f"soft halt fired before {label} fan-out — see telemetry.csv"
        )

    poller.set_phase(f"{label}:fanout")
    poller.write_event(phase=f"{label}:fanout_start", note=f"trials={list(TRIALS_DEFAULT)}")
    t_fanout_start = time.monotonic()
    cpcv_results = run_5_trial_fanout(
        events,
        runner=runner,
        backtest_fn_factory=_backtest_fn_factory,
    )
    fanout_ms = int((time.monotonic() - t_fanout_start) * 1000)
    poller.write_event(
        phase=f"{label}:fanout_complete",
        note=f"duration_ms={fanout_ms};total_results={sum(len(v) for v in cpcv_results.values())}",
    )

    # Per AC8 — check halt flag after the heavy phase too. If the poller
    # tripped DURING fanout, we still emit the report (the work is done)
    # but the orchestrator returns HALT after persist.
    if poller.halt_event.is_set():
        # We allow the report below to compute since the data is in RAM
        # already; the orchestrator surfaces HALT once persistence is done.
        poller.write_event(phase=f"{label}:halt_observed", note="continuing to persist before halt")

    poller.set_phase(f"{label}:report")
    cfg = ReportConfig(seed_bootstrap=seed)
    full_report = compute_full_report(cpcv_results, config=cfg)
    poller.write_event(
        phase=f"{label}:report_complete",
        note=f"verdict={full_report.kill_decision.verdict};dsr={full_report.metrics.dsr:.6f};pbo={full_report.metrics.pbo:.6f}",
    )

    # Recover the per-run DeterminismStamp from the first result (uniform
    # across all 225 per Beckett T0).
    sample_result = next(iter(cpcv_results.values()))[0]
    determinism_stamp = sample_result.determinism

    events_metadata = {
        "phase": label,
        "in_sample_start": in_sample_start.isoformat(),
        "in_sample_end": in_sample_end.isoformat(),
        "n_events": n_events,
        "n_trials": n_trials,
        "trials": list(TRIALS_DEFAULT),
        "warmup_gate_as_of": in_sample_start.isoformat(),
        "warmup_gate_passed_at_brt": datetime.now().isoformat(timespec="seconds"),
        "fanout_duration_ms": fanout_ms,
    }
    return full_report, determinism_stamp, events_metadata


# =====================================================================
# main() — orchestration + exit codes
# =====================================================================
def main(argv: Optional[list[str]] = None) -> int:
    """Entry point — returns process exit code per AC7.

    Exposed for tests via ``main(["--spec", ...])``. The CLI exits
    via ``sys.exit(main())`` at module bottom.
    """
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    # ---------- AC13 spec sha256 (computed early; used by run_id + lock) ----------
    if not args.spec.exists():
        print(f"ERROR: spec not found: {args.spec}", file=sys.stderr)
        return 1
    spec_sha = compute_spec_sha256(args.spec)

    # ---------- AC7 — resolve in-sample window (CLI override > spec default) ----------
    if args.in_sample_start is None or args.in_sample_end is None:
        try:
            spec_start, spec_end = parse_in_sample_window(args.spec)
        except (ValueError, OSError) as exc:
            print(f"ERROR: cannot resolve in-sample window: {exc}", file=sys.stderr)
            return 1
        in_sample_start = args.in_sample_start or spec_start
        in_sample_end = args.in_sample_end or spec_end
    else:
        in_sample_start = args.in_sample_start
        in_sample_end = args.in_sample_end

    if in_sample_end < in_sample_start:
        print(
            f"ERROR: in_sample_end ({in_sample_end}) < in_sample_start "
            f"({in_sample_start})",
            file=sys.stderr,
        )
        return 1

    # ---------- AC9 — hold-out lock guard FIRES BEFORE any iteration ----------
    # Defense-in-depth: also enforced inside CPCVEngine.generate_splits
    # (T002.0c AC12). This is the script-level gate operators see first.
    try:
        assert_holdout_safe(in_sample_start, in_sample_end)
    except HoldoutLockError as exc:
        # R1 + R15(d) — explicit hold-out violation; HALT.
        print(
            f"ERROR: hold-out lock violation (R1 + R15(d)): {exc}\n"
            f"Set {os.environ.get('VESPERA_UNLOCK_HOLDOUT', 'VESPERA_UNLOCK_HOLDOUT')}=1 "
            "with explicit operator justification to bypass.",
            file=sys.stderr,
        )
        return 1

    # ---------- run_id (deterministic default per Beckett T0) ----------
    run_id = args.run_id or derive_default_run_id(
        spec_sha, in_sample_start, in_sample_end, args.seed
    )
    out_dir = args.output_root / f"cpcv-dryrun-{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------- AC13 — spec sha256 lock against any prior run in this dir ----------
    stamp_path = out_dir / "determinism_stamp.json"
    try:
        assert_spec_lock(stamp_path, spec_sha)
    except SystemExit as se:
        # Exit code 2 surfaced verbatim; print diagnostic before returning.
        print(
            f"ERROR: spec sha256 mismatch vs prior run in {out_dir} "
            f"(current={spec_sha[:12]}...). Determinism violation (exit 2).",
            file=sys.stderr,
        )
        return int(se.code) if isinstance(se.code, int) else 2

    # ---------- Calendar (shared across phases) ----------
    try:
        calendar = CalendarLoader.load(args.calendar)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: calendar load failed: {exc}", file=sys.stderr)
        return 1

    # T002.0h.1 AC1 — NO shared WarmUpGate singleton at this site. Each
    # ``_run_phase`` call constructs its own phase-local gate against
    # dated paths derived from the phase-specific ``as_of_date`` (smoke =
    # max(in_sample_start, in_sample_end - 30d); full = in_sample_start).
    # Track A structural defect (Beckett N4 root-cause `:848`) eliminated.

    # ---------- AC8 — psutil poller (daemon thread, telemetry CSV) ----------
    soft_cap_bytes = int(args.mem_soft_cap_gb * 1024**3)
    poller = MemoryPoller(
        out_dir / "telemetry.csv",
        soft_cap_bytes=soft_cap_bytes,
        poll_interval_s=args.mem_poll_interval_s,
        enabled=args.dry_run,  # --no-dry-run disables polling for perf
    )
    poller.write_event(phase="run_start", note=f"run_id={run_id};spec_sha={spec_sha[:12]}")
    poller.start()

    halt_observed = False
    try:
        # ---------- AC10/AC11 — smoke pre-condition ----------
        if args.smoke:
            smoke_start = max(in_sample_start, in_sample_end - timedelta(days=DEFAULT_SMOKE_DAYS))
            try:
                # T002.0h.1 AC1 — smoke phase derives as_of = smoke_start
                # and constructs its own WarmUpGate against
                # ``_dated_*_path(smoke_start)`` (e.g., 2025-05-31).
                smoke_report, smoke_stamp, smoke_meta = _run_phase(
                    label="smoke",
                    spec_path=args.spec,
                    engine_config_path=args.engine_config,
                    in_sample_start=smoke_start,
                    in_sample_end=in_sample_end,
                    calendar=calendar,
                    seed=args.seed,
                    run_id=run_id,
                    poller=poller,
                    as_of_date=smoke_start,
                    warmup_atr_cli=args.warmup_atr,
                    warmup_percentiles_cli=args.warmup_percentiles,
                )
            except Exception as exc:  # noqa: BLE001 — must abort full per AC11
                # Per AC11 — smoke failure aborts full run; reason logged.
                poller.write_event(
                    phase="smoke_failed",
                    note=f"reason: smoke_aborted: {type(exc).__name__}: {exc}",
                )
                print(
                    f"ERROR: smoke phase failed; aborting full run per AC11: {exc}",
                    file=sys.stderr,
                )
                return 1
            # Persist smoke artifacts under a nested dir so they don't
            # collide with the full-run artifacts (which use out_dir directly).
            smoke_dir = out_dir / "smoke"
            persist_artifacts(
                smoke_dir,
                full_report=smoke_report,
                determinism_stamp=smoke_stamp,
                events_metadata=smoke_meta,
            )
            poller.write_event(
                phase="smoke_complete",
                note=f"verdict={smoke_report.kill_decision.verdict}",
            )
            if poller.halt_event.is_set():
                # Per AC8 — graceful HALT after smoke; do NOT proceed to full.
                halt_observed = True
                poller.write_event(phase="halt_after_smoke", note="6 GiB soft cap exceeded; full skipped")
                return 1

        # ---------- Full run ----------
        try:
            # T002.0h.1 AC1 — full phase derives as_of = in_sample_start
            # and constructs its own WarmUpGate against
            # ``_dated_*_path(in_sample_start)`` (e.g., 2024-08-22).
            full_report, full_stamp, full_meta = _run_phase(
                label="full",
                spec_path=args.spec,
                engine_config_path=args.engine_config,
                in_sample_start=in_sample_start,
                in_sample_end=in_sample_end,
                calendar=calendar,
                seed=args.seed,
                run_id=run_id,
                poller=poller,
                as_of_date=in_sample_start,
                warmup_atr_cli=args.warmup_atr,
                warmup_percentiles_cli=args.warmup_percentiles,
            )
        except RuntimeError as exc:
            # Warmup failures (assert_warmup_satisfied) bubble as RuntimeError.
            poller.write_event(phase="full_failed", note=f"warmup_or_pipeline: {exc}")
            print(f"ERROR: full phase failed: {exc}", file=sys.stderr)
            return 1
        except FileNotFoundError as exc:
            # T002.0g Guard #1: warmup state missing fail-closed (no fallback).
            poller.write_event(phase="warmup_state_missing", note=str(exc))
            print(f"ERROR: warmup state missing: {exc}", file=sys.stderr)
            return 1
        except ValueError as exc:
            # Warmup state corrupt/schema-drift fail-closed (Guard #1).
            poller.write_event(phase="warmup_state_corrupt", note=str(exc))
            print(f"ERROR: warmup state corrupt: {exc}", file=sys.stderr)
            return 1
        except MemoryError as exc:
            poller.write_event(phase="full_halt", note=f"soft_halt: {exc}")
            print(f"HALT: {exc}", file=sys.stderr)
            return 1

        persist_artifacts(
            out_dir,
            full_report=full_report,
            determinism_stamp=full_stamp,
            events_metadata=full_meta,
        )
        poller.write_event(
            phase="full_complete",
            note=f"verdict={full_report.kill_decision.verdict}",
        )
        if poller.halt_event.is_set():
            # Soft halt fired during full — artifacts persisted, but signal HALT.
            halt_observed = True
            poller.write_event(phase="halt_after_full_persist", note="6 GiB soft cap exceeded")
            return 1

        return 0
    finally:
        poller.write_event(phase="run_end", note=f"halt_observed={halt_observed}")
        poller.stop()


if __name__ == "__main__":  # pragma: no cover — entrypoint guard
    raise SystemExit(main())
