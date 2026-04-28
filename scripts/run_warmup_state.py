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
    --force-rebuild                (T002.0h AC9 — bypass cache, force
                                    orchestrator invocation)

Exit codes:
    0 = PASS
    1 = HALT (insufficient trades / hold-out violation / source missing /
        manifest write fail / soft-halt / stale cache fail-closed)
    2 = determinism violation (parser error from argparse also)

Hold-out grep contract (DoD §Hold-out intocado):
    grep ``VESPERA_UNLOCK_HOLDOUT`` scripts/run_warmup_state.py >= 1.

T002.0h AC9 — Cache validation contract (ESC-006 mini-council 4/4
APPROVE_F):

    1. Triple-key cache: ``(as_of_date, source_sha256_from_manifest,
       builder_version_semver)``.
    2. Fail-closed on mismatch (``StaleCacheError`` raised, exit 1, NO
       silent regenerate). ``--force-rebuild`` is the explicit operator
       escape hatch.
    3. ``--force-rebuild`` flag bypasses cache and forces a full
       orchestrator invocation regardless of sidecar key state.
    4. Cache hit / miss / stale events logged to
       ``state/T002/cache_audit.jsonl`` (append-only) for Sable audit.
    5. TTL infinito (immutable per key) — cache only invalidates when
       the triple-key changes.

    The cache key is persisted as a sidecar file
    ``state/T002/_cache_key_{as_of}.json`` (CLI-owned; orchestrator
    state JSONs are NOT touched per Anti-Article-IV Guard #4 — builder
    API immutable + R15 orchestrator JSON schema preserved). Sidecar
    presence + matching triple-key signals a valid cache.

Cache hit path: skip orchestrator invocation (< 5s wall-time) — read
sidecar, verify key matches the expected one, log audit, return exit 0.

Cache miss path: invoke orchestrator (existing behavior), then write
the sidecar + audit entry on success.

Cache stale path: sidecar exists but key mismatches expected. Per
mini-council fail-closed contract, raise ``StaleCacheError``, log the
mismatch detail to audit, return exit 1. Operator MUST investigate the
mismatch (possibly upstream data drift) and re-run with
``--force-rebuild`` to acknowledge the override.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import sys
import threading
import time
from datetime import date, datetime, timedelta
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

from packages.t002_eod_unwind.warmup import BUILDER_VERSION  # noqa: E402
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

# T002.0h AC9 — cache validation contract constants.
# Source manifest CSV path (Dara T0 — single-source). The triple-key
# computation hashes the relevant rows of this manifest for the
# orchestrator's lookback window.
DEFAULT_MANIFEST_CSV: Path = Path("data/manifest.csv")
# Lookback buffer (calendar days) used to select manifest rows whose
# trading windows could intersect ``[as_of - WARMUP_CALENDAR_LOOKBACK,
# as_of - 1]``. The orchestrator's ``compute_window`` is calendar-aware
# and the actual lookback is ~2.5×146 ≈ 365 calendar days; we round up
# to 400 to cover edge cases. Conservative wide window is correct
# behavior — stale cache MUST fire if ANY potentially-relevant manifest
# row changes.
WARMUP_CALENDAR_LOOKBACK: int = 400
# Cache audit JSONL filename — append-only Sable-consumable.
CACHE_AUDIT_FILENAME: str = "cache_audit.jsonl"
# Cache key sidecar filename pattern — written next to the orchestrator
# state JSONs but owned by the CLI (orchestrator does NOT touch this).
CACHE_KEY_SIDECAR_PATTERN: str = "_cache_key_{as_of}.json"

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
    p.add_argument(
        "--force-rebuild",
        action="store_true",
        default=False,
        help=(
            "T002.0h AC9 — bypass cache validation and force orchestrator "
            "invocation regardless of sidecar key state. Operator escape "
            "hatch for the fail-closed cache contract (use when upstream "
            "data drift is intentional and acknowledged)."
        ),
    )
    p.add_argument(
        "--manifest-csv",
        type=Path,
        default=DEFAULT_MANIFEST_CSV,
        help=(
            "Manifest CSV used for triple-key cache source_sha256 "
            "aggregation (default data/manifest.csv)."
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
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# =====================================================================
# T002.0h AC9 — cache validation contract (mini-council 4/4 APPROVE_F)
# =====================================================================
class StaleCacheError(RuntimeError):
    """Raised when a cache sidecar exists but its triple-key mismatches.

    Per ESC-006 mini-council 4/4 CONVERGENT (Aria + Mira + Beckett +
    Riven): fail-closed — NO silent regenerate. Operator MUST inspect
    the mismatch (likely upstream data drift or builder version bump)
    and re-run with ``--force-rebuild`` to acknowledge the override.

    The error message includes the expected vs found triple-key for
    operator diagnosis.
    """


def _iter_manifest_rows(manifest_csv: Path) -> list[dict[str, str]]:
    """Read ``manifest_csv`` and return all rows as dicts.

    The CSV schema is set by the materialization pipeline
    (``data/manifest.csv``): ``path,rows,sha256,start_ts_brt,end_ts_brt,
    ticker,phase,generated_at_brt``. We tolerate trailing whitespace and
    case-fold the sha256 to lower (matches feed_parquet adapter).
    """
    rows: list[dict[str, str]] = []
    with manifest_csv.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rows.append(
                {
                    "path": (raw.get("path") or "").strip(),
                    "rows": (raw.get("rows") or "").strip(),
                    "sha256": (raw.get("sha256") or "").strip().lower(),
                    "start_ts_brt": (raw.get("start_ts_brt") or "").strip(),
                    "end_ts_brt": (raw.get("end_ts_brt") or "").strip(),
                    "ticker": (raw.get("ticker") or "").strip(),
                    "phase": (raw.get("phase") or "").strip(),
                }
            )
    return rows


def _compute_source_sha256_for_window(
    manifest_csv: Path,
    as_of: date,
    *,
    ticker: str,
    lookback_calendar_days: int = WARMUP_CALENDAR_LOOKBACK,
) -> str:
    """Aggregate SHA-256 over manifest rows whose trade-window intersects
    the lookback ``[as_of - lookback_calendar_days, as_of - 1]`` (BRT-naive).

    Algorithm:
      1. Read manifest CSV (Dara T0 — single-source).
      2. Filter rows by ticker + by intersection of
         ``[start_ts_brt, end_ts_brt]`` with the lookback window.
      3. Sort matched rows by (path, sha256) ascending — deterministic
         across re-orderings.
      4. SHA-256 the concatenation of ``f"{path}|{sha256}|{rows}\n"``
         lines.

    The returned hex digest changes IFF any relevant manifest row's
    sha256, path, or row count changes — exactly the invalidation
    semantics the mini-council mandated.

    Raises ``FileNotFoundError`` if the manifest CSV is missing
    (caller MUST escalate; no silent fallback).
    """
    if not manifest_csv.exists():
        raise FileNotFoundError(
            f"manifest CSV missing: {manifest_csv} — cannot compute "
            "triple-key source_sha256. Materialize the parquet manifest "
            "before running warmup state."
        )

    rows = _iter_manifest_rows(manifest_csv)
    window_start = datetime.combine(
        as_of - timedelta(days=lookback_calendar_days),
        datetime.min.time(),
    )
    window_end = datetime.combine(as_of, datetime.min.time())

    def _parse_ts(s: str) -> datetime | None:
        try:
            return datetime.fromisoformat(s)
        except (ValueError, TypeError):
            return None

    matched: list[tuple[str, str, str]] = []
    for r in rows:
        if r["ticker"].upper() != ticker.upper():
            continue
        start_ts = _parse_ts(r["start_ts_brt"])
        end_ts = _parse_ts(r["end_ts_brt"])
        if start_ts is None or end_ts is None:
            # Skip malformed rows defensively — they cannot intersect
            # any window. Logged once at debug level by caller.
            continue
        # Intersection test: rows whose [start, end] overlaps the
        # lookback window.
        if end_ts < window_start or start_ts >= window_end:
            continue
        matched.append((r["path"], r["sha256"], r["rows"]))

    if not matched:
        # Empty match is a meaningful key (distinct from any non-empty
        # match). We hash the marker explicitly so the cache key is well-
        # defined even when no manifest rows intersect (e.g. test setups).
        # This makes the contract testable without throwing.
        marker = f"empty|as_of={as_of.isoformat()}|ticker={ticker}".encode("utf-8")
        return hashlib.sha256(marker).hexdigest()

    matched.sort(key=lambda t: (t[0], t[1]))
    h = hashlib.sha256()
    for path_str, sha, rows_str in matched:
        h.update(f"{path_str}|{sha}|{rows_str}\n".encode("utf-8"))
    return h.hexdigest()


def compute_triple_key(
    *,
    as_of: date,
    source_sha256: str,
    builder_version: str,
) -> dict[str, str]:
    """Construct the canonical triple-key per ESC-006 mini-council.

    Returns the dict shape persisted to the sidecar AND inscribed in the
    cache audit log. Determinism: identical inputs ⇒ identical dict.
    """
    return {
        "as_of_date": as_of.isoformat(),
        "source_sha256": source_sha256,
        "builder_version": builder_version,
    }


def _sidecar_path(output_dir: Path, as_of: date) -> Path:
    return output_dir / CACHE_KEY_SIDECAR_PATTERN.format(as_of=as_of.isoformat())


def _write_cache_sidecar(
    output_dir: Path,
    as_of: date,
    triple_key: dict[str, str],
) -> Path:
    """Persist the triple-key sidecar deterministically (sort_keys + compact).

    Sidecar is CLI-owned (orchestrator never reads/writes it). Failure
    surfaces as ``OSError`` so the caller (``main``) can fail-closed.
    """
    path = _sidecar_path(output_dir, as_of)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(triple_key, sort_keys=True, separators=(",", ":"))
    path.write_text(payload, encoding="utf-8")
    return path


def _read_cache_sidecar(output_dir: Path, as_of: date) -> dict[str, str] | None:
    """Return the persisted triple-key for ``as_of`` if the sidecar exists.

    Returns ``None`` if the sidecar is absent (cache miss). Returns a
    dict with ``""`` for any field absent in the file (treated as a
    mismatch by ``_check_cache``). Malformed JSON ⇒ treated as mismatch
    via empty-dict return — caller fail-closes.
    """
    path = _sidecar_path(output_dir, as_of)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        # Malformed sidecar — treat as a cache miss for SAFETY (fail-
        # closed). Returning an empty dict triggers a mismatch downstream.
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        "as_of_date": str(data.get("as_of_date", "")),
        "source_sha256": str(data.get("source_sha256", "")),
        "builder_version": str(data.get("builder_version", "")),
    }


def _orchestrator_outputs_present(output_dir: Path, as_of: date) -> bool:
    """Both ATR + Percentiles dated JSONs must exist for cache HIT.

    Mirrors the orchestrator's per-as_of_date output filename contract
    (``atr_20d_{as_of}.json`` + ``percentiles_126d_{as_of}.json``).
    """
    atr = output_dir / f"atr_20d_{as_of.isoformat()}.json"
    pct = output_dir / f"percentiles_126d_{as_of.isoformat()}.json"
    return atr.exists() and pct.exists()


def _append_cache_audit(
    output_dir: Path,
    *,
    as_of: date,
    status: str,
    expected_key: dict[str, str],
    found_key: dict[str, str] | None,
    note: str = "",
) -> None:
    """Append a JSONL audit entry to ``state/T002/cache_audit.jsonl``.

    Schema: ``{computed_at_brt, as_of_date, status, expected_key,
    found_key, note}``. ``status`` ∈ {hit, miss, stale, write,
    force_rebuild}. Append-only — Sable consumes for cross-run audit.

    Best-effort write — IO failure logs a warning and continues (audit
    is observability, NOT a correctness contract).
    """
    entry = {
        "computed_at_brt": datetime.now().isoformat(timespec="seconds"),
        "as_of_date": as_of.isoformat(),
        "status": status,
        "expected_key": expected_key,
        "found_key": found_key,
        "note": note,
    }
    audit_path = output_dir / CACHE_AUDIT_FILENAME
    try:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry, sort_keys=True, separators=(",", ":"))
        with audit_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        logger.warning(
            "cache_audit append failed at %s: %s (continuing)", audit_path, exc
        )


def check_cache(
    *,
    output_dir: Path,
    as_of: date,
    expected_key: dict[str, str],
    force_rebuild: bool,
) -> tuple[str, dict[str, str] | None]:
    """Decide cache state for ``as_of``.

    Returns ``(status, found_key)`` where ``status`` ∈
    {``"hit"``, ``"miss"``, ``"stale"``, ``"force_rebuild"``}.

    Decision matrix:
      - ``force_rebuild`` ⇒ ``"force_rebuild"`` (orchestrator MUST run).
      - sidecar absent OR orchestrator outputs missing ⇒ ``"miss"``.
      - sidecar present + key matches expected ⇒ ``"hit"``.
      - sidecar present + key mismatch ⇒ ``"stale"`` (caller raises
        ``StaleCacheError``).
    """
    if force_rebuild:
        found = _read_cache_sidecar(output_dir, as_of)
        return "force_rebuild", found

    if not _orchestrator_outputs_present(output_dir, as_of):
        return "miss", None

    found = _read_cache_sidecar(output_dir, as_of)
    if found is None:
        # Outputs exist but no sidecar — pre-AC9 artifact (legacy run
        # without cache key). Treat as miss to force re-materialization
        # under the new contract; the rebuild WILL emit the sidecar so
        # subsequent runs hit the cache.
        return "miss", None

    if found == expected_key:
        return "hit", found
    return "stale", found


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

        # =====================================================
        # T002.0h AC9 — Cache validation contract (pre-orchestrator).
        # =====================================================
        # Compute expected triple-key per as_of and partition into
        # cache-hit (skip) vs cache-miss/force_rebuild (must invoke
        # orchestrator). Stale cache fails-closed before any IO is
        # burned in the orchestrator path.
        expected_keys: dict[date, dict[str, str]] = {}
        cache_decisions: dict[date, str] = {}
        as_ofs_to_run: list[date] = []
        as_ofs_hit: list[date] = []

        for as_of in args.as_of_dates:
            # Compute the expected source_sha256 from the manifest CSV
            # (Dara T0 single-source). Manifest missing ⇒ fail-closed
            # exit 1 (no silent fallback per Anti-Article-IV Guard #1).
            try:
                source_sha = _compute_source_sha256_for_window(
                    args.manifest_csv,
                    as_of,
                    ticker=args.ticker,
                )
            except FileNotFoundError as exc:
                poller.write_event(phase="cache_manifest_missing", note=str(exc))
                print(f"ERROR: {exc}", file=sys.stderr)
                return 1

            expected_key = compute_triple_key(
                as_of=as_of,
                source_sha256=source_sha,
                builder_version=BUILDER_VERSION,
            )
            expected_keys[as_of] = expected_key

            status, found_key = check_cache(
                output_dir=args.output_dir,
                as_of=as_of,
                expected_key=expected_key,
                force_rebuild=args.force_rebuild,
            )
            cache_decisions[as_of] = status

            if status == "hit":
                _append_cache_audit(
                    args.output_dir,
                    as_of=as_of,
                    status="hit",
                    expected_key=expected_key,
                    found_key=found_key,
                    note="orchestrator skipped (triple-key match)",
                )
                poller.write_event(
                    phase="cache_hit",
                    note=f"as_of={as_of.isoformat()};builder={BUILDER_VERSION}",
                )
                as_ofs_hit.append(as_of)
            elif status == "stale":
                _append_cache_audit(
                    args.output_dir,
                    as_of=as_of,
                    status="stale",
                    expected_key=expected_key,
                    found_key=found_key,
                    note="fail-closed; operator must --force-rebuild to override",
                )
                poller.write_event(
                    phase="cache_stale",
                    note=f"as_of={as_of.isoformat()};expected={expected_key};found={found_key}",
                )
                msg = (
                    f"StaleCacheError: cache key mismatch for "
                    f"as_of={as_of.isoformat()}.\n"
                    f"  expected: {expected_key}\n"
                    f"  found:    {found_key}\n"
                    "Per ESC-006 mini-council 4/4 fail-closed contract: NO "
                    "silent regenerate. Investigate the upstream change "
                    "(manifest sha drift OR builder version bump) and re-run "
                    "with --force-rebuild to acknowledge."
                )
                print(f"ERROR: {msg}", file=sys.stderr)
                return 1
            else:  # miss | force_rebuild
                _append_cache_audit(
                    args.output_dir,
                    as_of=as_of,
                    status=status,
                    expected_key=expected_key,
                    found_key=found_key,
                    note="orchestrator invocation queued",
                )
                poller.write_event(
                    phase=f"cache_{status}",
                    note=f"as_of={as_of.isoformat()};builder={BUILDER_VERSION}",
                )
                as_ofs_to_run.append(as_of)

        # If ALL as_ofs are cache hits, short-circuit: no orchestrator
        # call needed. We still emit the run_end event in the finally.
        if not as_ofs_to_run:
            poller.write_event(
                phase="cache_all_hits",
                note=f"as_of_count={len(as_ofs_hit)};orchestrator_skipped",
            )
            return 0

        poller.set_phase(phase="orchestrate")
        poller.write_event(
            phase="orchestrate_start",
            note=(
                f"as_of_count={len(as_ofs_to_run)}/"
                f"{len(args.as_of_dates)};hits={len(as_ofs_hit)}"
            ),
        )
        try:
            result = orchestrate_warmup_state(
                as_of_dates=as_ofs_to_run,
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

        # T002.0h AC9 — write cache sidecars for the as_ofs we just
        # materialized so subsequent runs hit the cache. Sidecar write
        # failure is fail-closed (Anti-Article-IV Guard #2: the sidecar
        # is the cache contract — silent absence would mask state).
        for as_of in as_ofs_to_run:
            try:
                _write_cache_sidecar(
                    args.output_dir,
                    as_of,
                    expected_keys[as_of],
                )
            except OSError as exc:
                poller.write_event(
                    phase="cache_sidecar_write_fail",
                    note=f"as_of={as_of.isoformat()};{exc}",
                )
                print(
                    f"ERROR: cache sidecar write failed for "
                    f"as_of={as_of.isoformat()}: {exc}",
                    file=sys.stderr,
                )
                return 1
            _append_cache_audit(
                args.output_dir,
                as_of=as_of,
                status="write",
                expected_key=expected_keys[as_of],
                found_key=expected_keys[as_of],
                note=(
                    f"sidecar persisted post-orchestrator; "
                    f"prior_decision={cache_decisions[as_of]}"
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
