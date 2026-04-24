"""Unit tests for `core.run_with_ceiling` + `core.memory_budget` + `core.telemetry_schema`.

Story: T002.0a (T9 / #74) — Dex implementation of ADR-1 v2 + ADR-2 + ADR-3.
Owner (acceptance): Quinn (@qa).

Mocks psutil via monkeypatch; uses an injectable fake sampler to drive the
state machine without launching a real child process. `tmp_path` isolates
artifacts from the repo tree.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import psutil
import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core import memory_budget, run_with_ceiling  # noqa: E402
from core.run_with_ceiling import run_with_ceiling as rwc  # noqa: E402
from core.telemetry_schema import (  # noqa: E402
    SUMMARY_JSON_FIELDS,
    TELEMETRY_CSV_COLUMNS,
    Sample,
    append_tick,
    compute_ratio,
    write_summary,
)


# --- Helpers ---------------------------------------------------------------


@dataclass
class _FakeVM:
    total: int
    available: int


def _mk_sample(commit: int, rss: int, pf: int = 0, avail: int = 0, ts: str = "2026-04-23T12:00:00") -> Sample:
    return Sample(
        commit_bytes=commit,
        rss_bytes=rss,
        pagefile_alloc_bytes=pf,
        available_bytes=avail,
        ts_brt=ts,
    )


def _scripted_sampler(samples: list[Sample | None]) -> "callable":
    """Build a fake sampler that yields from `samples` in order; returns the
    tail element forever after the list is exhausted (or raises if None-tail).
    """
    it: Iterator[Sample | None] = iter(samples)
    last: list[Sample | None] = [None]

    def _sampler(pid: int) -> Sample | None:
        try:
            last[0] = next(it)
        except StopIteration:
            pass
        return last[0]

    return _sampler


class _FakeChild:
    """Minimal stand-in for subprocess.Popen — lets us control poll() / wait() / kill().

    The `lifespan_polls` field controls how many `poll()` calls return None
    before the child "exits" with `exit_rc`.
    """
    def __init__(self, *, lifespan_polls: int, exit_rc: int):
        self._lifespan = lifespan_polls
        self._polled = 0
        self._exit_rc = exit_rc
        self.pid = 12345
        self.killed = False
        self.terminated = False
        self.returncode: int | None = None

    def poll(self) -> int | None:
        self._polled += 1
        if self._polled > self._lifespan:
            self.returncode = self._exit_rc
            return self._exit_rc
        return None

    def wait(self, timeout: int | None = None) -> int:
        self.returncode = self._exit_rc
        return self._exit_rc

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9

    def terminate(self) -> None:
        self.terminated = True


@pytest.fixture
def patch_host_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make check_host_drift() + R4 availability check both PASS by default.

    ADR-1 v3: R4 threshold = CAP_ABSOLUTE + OS_HEADROOM. We set available to
    threshold + 1 GiB so the gate passes comfortably on any host.
    """
    threshold = memory_budget.CAP_ABSOLUTE + memory_budget.OS_HEADROOM
    fake_vm = _FakeVM(
        total=memory_budget.PHYSICAL_RAM_BYTES,
        available=threshold + (1 << 30),  # 1 GiB above v3 R4 threshold
    )
    monkeypatch.setattr(psutil, "virtual_memory", lambda: fake_vm)
    monkeypatch.setattr(run_with_ceiling.psutil, "virtual_memory", lambda: fake_vm)


@pytest.fixture
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip time.sleep entirely in the polling loop (tests run fast)."""
    monkeypatch.setattr(run_with_ceiling.time, "sleep", lambda _s: None)


# --- memory_budget ---------------------------------------------------------


def test_host_drift_detects_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_vm = _FakeVM(total=8_000_000_000, available=0)
    monkeypatch.setattr(memory_budget.psutil, "virtual_memory", lambda: fake_vm)

    ok, detail = memory_budget.check_host_drift()
    assert ok is False
    assert "drift" in detail.lower()
    assert "E4" in detail


def test_host_drift_accepts_within_tolerance(monkeypatch: pytest.MonkeyPatch) -> None:
    # 0.5% drift — below 1% threshold
    drift_bytes = int(0.005 * memory_budget.PHYSICAL_RAM_BYTES)
    fake_vm = _FakeVM(
        total=memory_budget.PHYSICAL_RAM_BYTES + drift_bytes,
        available=0,
    )
    monkeypatch.setattr(memory_budget.psutil, "virtual_memory", lambda: fake_vm)

    ok, detail = memory_budget.check_host_drift()
    assert ok is True
    assert "ok" in detail.lower()


@pytest.mark.parametrize(
    "proc_name",
    [
        "MsMpEng.exe",
        "vmmem",
        "com.docker.backend.exe",
        "Docker Desktop.exe",
        "claude.exe",
        "explorer.exe",
        "services.exe",
        "System",
        "svchost.exe",
        "csrss.exe",
        "smss.exe",
        "wininit.exe",
        "winlogon.exe",
        "lsass.exe",
        "Registry",
        "Memory Compression",
    ],
)
def test_is_retained_matches_whitelist(proc_name: str) -> None:
    assert memory_budget.is_retained(proc_name) is True, f"expected whitelist match for {proc_name!r}"


@pytest.mark.parametrize(
    "proc_name",
    ["chrome.exe", "Discord.exe", "Spotify.exe"],
)
def test_is_retained_rejects_non_whitelist(proc_name: str) -> None:
    assert memory_budget.is_retained(proc_name) is False


def test_is_retained_empty_string_returns_false() -> None:
    assert memory_budget.is_retained("") is False


# --- telemetry_schema ------------------------------------------------------


def test_compute_ratio_rounds_half_even() -> None:
    # 10 / 4 = 2.5 exactly → rounded to 2.500
    assert compute_ratio(10, 4) == 2.500


def test_compute_ratio_zero_rss_returns_none() -> None:
    assert compute_ratio(1_000_000, 0) is None


def test_compute_ratio_three_decimal_precision() -> None:
    # 7 / 3 = 2.333333... → 2.333
    assert compute_ratio(7, 3) == 2.333


def test_write_summary_requires_all_fields(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    incomplete = {k: 0 for k in SUMMARY_JSON_FIELDS[:-1]}
    with pytest.raises(ValueError, match="missing required fields"):
        write_summary(out, incomplete)


def test_write_summary_atomic_and_ordered(tmp_path: Path) -> None:
    out = tmp_path / "summary.json"
    full = {k: (0 if k != "run_id" else "t") for k in SUMMARY_JSON_FIELDS}
    full["ratio_commit_rss"] = 1.5
    full["start_ts"] = "2026-04-23T12:00:00"
    full["end_ts"] = "2026-04-23T13:00:00"
    write_summary(out, full)
    assert out.exists()
    # No .tmp leftover
    assert not (tmp_path / "summary.json.tmp").exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert list(data.keys()) == list(SUMMARY_JSON_FIELDS)


# --- run_with_ceiling: state-machine ---------------------------------------


def test_no_overwrite_without_force(tmp_path: Path, patch_host_ok, no_sleep) -> None:
    """If {run_id}.log exists and force=False → exit 1 without launching child."""
    run_id = "preexist"
    (tmp_path / f"{run_id}.log").write_text("pre-existing content", encoding="utf-8")

    # Build a sampler that would be called if we actually launched (should NOT be called)
    sampler = _scripted_sampler([_mk_sample(1, 1)])

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id=run_id,
        log_dir=tmp_path,
        ceiling_bytes=memory_budget.CAP_ABSOLUTE,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=False,
    )

    assert result.exit_code == 1
    assert result.tick_count == 0
    # Log content not overwritten
    assert (tmp_path / f"{run_id}.log").read_text(encoding="utf-8") == "pre-existing content"


def test_launch_time_check_fails_on_low_ram(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, no_sleep
) -> None:
    """R4 (ADR-1 v3): available < CAP_ABSOLUTE + OS_HEADROOM → exit 1 before launching child.

    v3 threshold equals OBSERVED_QUIESCE_FLOOR_AVAILABLE (9,473,794,048 bytes) by
    construction. v2 used `1.5 × CAP_ABSOLUTE` (14.37 GiB, unreachable); v3 additive
    formula is reachable on this host post-quiesce.
    """
    threshold = memory_budget.CAP_ABSOLUTE + memory_budget.OS_HEADROOM
    fake_vm = _FakeVM(total=memory_budget.PHYSICAL_RAM_BYTES, available=threshold - 1)
    monkeypatch.setattr(psutil, "virtual_memory", lambda: fake_vm)
    monkeypatch.setattr(run_with_ceiling.psutil, "virtual_memory", lambda: fake_vm)
    # Minimal process iterator (empty) so top-3 report does not explode
    monkeypatch.setattr(
        run_with_ceiling.psutil,
        "process_iter",
        lambda attrs=None: iter([]),
    )

    sampler = _scripted_sampler([_mk_sample(1, 1)])
    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="low-ram",
        log_dir=tmp_path,
        ceiling_bytes=memory_budget.CAP_ABSOLUTE,
        sampler=sampler,
    )
    assert result.exit_code == 1
    assert result.tick_count == 0


def test_ceiling_trip_kills_child(
    tmp_path: Path, patch_host_ok, no_sleep, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Child commit crosses 0.96 * ceiling → exit 3, summary.json written."""
    ceiling = memory_budget.CAP_ABSOLUTE
    # Trajectory: warm-up, then a single tick that is 0.96 * ceiling → KILL
    samples = [
        _mk_sample(int(0.10 * ceiling), int(0.08 * ceiling), pf=100, avail=10_000_000_000),
        _mk_sample(int(0.50 * ceiling), int(0.40 * ceiling), pf=120, avail=10_000_000_000),
        _mk_sample(int(0.96 * ceiling), int(0.70 * ceiling), pf=140, avail=10_000_000_000),
    ]
    sampler = _scripted_sampler(samples)

    fake_child = _FakeChild(lifespan_polls=100, exit_rc=0)
    monkeypatch.setattr(run_with_ceiling.subprocess, "Popen", lambda *a, **kw: fake_child)

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="trip",
        log_dir=tmp_path,
        ceiling_bytes=ceiling,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=True,
    )

    assert result.exit_code == 3
    assert fake_child.killed is True
    summary = json.loads((tmp_path / "trip-summary.json").read_text(encoding="utf-8"))
    assert summary["exit_code"] == 3
    assert summary["peak_commit"] >= int(0.96 * ceiling)


def test_warn_emitted_at_85_percent(
    tmp_path: Path, patch_host_ok, no_sleep, monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Observed reaches 0.86 * ceiling for 3 ticks; no KILL; WARN emitted once; child exits 0."""
    ceiling = memory_budget.CAP_ABSOLUTE
    samples = [
        _mk_sample(int(0.50 * ceiling), int(0.40 * ceiling), pf=100, avail=10_000_000_000),
        _mk_sample(int(0.86 * ceiling), int(0.60 * ceiling), pf=120, avail=10_000_000_000),
        _mk_sample(int(0.86 * ceiling), int(0.60 * ceiling), pf=130, avail=10_000_000_000),
    ]
    sampler = _scripted_sampler(samples)
    # Child exits cleanly after 3 ticks of sampling
    fake_child = _FakeChild(lifespan_polls=3, exit_rc=0)
    monkeypatch.setattr(run_with_ceiling.subprocess, "Popen", lambda *a, **kw: fake_child)

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="warn",
        log_dir=tmp_path,
        ceiling_bytes=ceiling,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=True,
    )

    out = capsys.readouterr().out
    assert result.exit_code == 0
    assert fake_child.killed is False
    assert "WARN" in out
    # Should only appear once (we dedupe with warned_already)
    assert out.count("WARN ceiling=") == 1


def test_sampler_three_consecutive_none_triggers_exit_5(
    tmp_path: Path, patch_host_ok, no_sleep, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sampler returns None 3× consecutive → wrapper kills child, exit 5."""
    sampler = _scripted_sampler([None, None, None])
    fake_child = _FakeChild(lifespan_polls=100, exit_rc=0)
    monkeypatch.setattr(run_with_ceiling.subprocess, "Popen", lambda *a, **kw: fake_child)

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="blind",
        log_dir=tmp_path,
        ceiling_bytes=memory_budget.CAP_ABSOLUTE,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=True,
    )
    assert result.exit_code == 5
    assert fake_child.killed is True


def test_summary_json_contains_all_fields(
    tmp_path: Path, patch_host_ok, no_sleep, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """After any run (clean or killed), summary.json has all SUMMARY_JSON_FIELDS."""
    samples = [
        _mk_sample(1_000_000, 500_000, pf=10, avail=10_000_000_000),
        _mk_sample(2_000_000, 900_000, pf=20, avail=10_000_000_000),
    ]
    sampler = _scripted_sampler(samples)
    fake_child = _FakeChild(lifespan_polls=2, exit_rc=0)
    monkeypatch.setattr(run_with_ceiling.subprocess, "Popen", lambda *a, **kw: fake_child)

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="fields",
        log_dir=tmp_path,
        ceiling_bytes=memory_budget.CAP_ABSOLUTE,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=True,
    )
    assert result.exit_code == 0

    summary = json.loads((tmp_path / "fields-summary.json").read_text(encoding="utf-8"))
    for field in SUMMARY_JSON_FIELDS:
        assert field in summary, f"missing summary field: {field}"


def test_telemetry_csv_header_first(
    tmp_path: Path, patch_host_ok, no_sleep, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """First line of the CSV is the header row with exactly TELEMETRY_CSV_COLUMNS."""
    samples = [
        _mk_sample(1_000_000, 500_000, pf=10, avail=10_000_000_000),
        _mk_sample(2_000_000, 900_000, pf=20, avail=10_000_000_000),
    ]
    sampler = _scripted_sampler(samples)
    fake_child = _FakeChild(lifespan_polls=2, exit_rc=0)
    monkeypatch.setattr(run_with_ceiling.subprocess, "Popen", lambda *a, **kw: fake_child)

    result = rwc(
        command=[sys.executable, "-c", "pass"],
        run_id="csvhdr",
        log_dir=tmp_path,
        ceiling_bytes=memory_budget.CAP_ABSOLUTE,
        poll_seconds=10,
        sampler=sampler,
        force_overwrite=True,
    )
    assert result.exit_code == 0

    csv_path = tmp_path / "csvhdr-telemetry.csv"
    lines = csv_path.read_text(encoding="utf-8").splitlines()
    assert lines, "CSV is empty"
    assert lines[0] == ",".join(TELEMETRY_CSV_COLUMNS)


# --- Schema writer standalone (independent of wrapper) ---------------------


def test_append_tick_writes_header_once(tmp_path: Path) -> None:
    """First append_tick writes header + row; second append_tick writes only row."""
    path = tmp_path / "tele.csv"
    s1 = _mk_sample(1, 2, pf=3, avail=4, ts="2026-04-23T12:00:00")
    s2 = _mk_sample(5, 6, pf=7, avail=8, ts="2026-04-23T12:00:30")
    append_tick(path, 1, s1)
    append_tick(path, 2, s2)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == ",".join(TELEMETRY_CSV_COLUMNS)
    assert len(lines) == 3  # header + 2 rows


# --- run_materialize_with_ceiling (wrapper) -------------------------------
#
# These tests verify the MWF-20260422-1 + Gage-halt passthrough fix:
# --output-dir, --no-manifest, --manifest-path must all forward from the
# wrapper to the child `scripts/materialize_parquet.py`, and the two manifest
# flags must be mutually exclusive at the wrapper layer.

# Import the wrapper module lazily so the core tests above stay independent.
import importlib  # noqa: E402

_WRAPPER_MODULE_NAME = "run_materialize_with_ceiling"


def _load_wrapper():
    """Import the wrapper script as a module (scripts/ is added to sys.path)."""
    scripts_dir = _REPO_ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    if _WRAPPER_MODULE_NAME in sys.modules:
        return importlib.reload(sys.modules[_WRAPPER_MODULE_NAME])
    return importlib.import_module(_WRAPPER_MODULE_NAME)


def _run_wrapper_capturing_command(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    extra_args: list[str],
) -> list[str]:
    """Invoke the wrapper `main()` with baseline-safe args + `extra_args`,
    intercepting `run_with_ceiling` to capture the child `command` list
    without actually launching a subprocess. Returns the captured command.
    """
    wrapper = _load_wrapper()
    captured: dict[str, list[str]] = {}

    def _fake_rwc(command, **_kwargs):
        captured["command"] = list(command)
        # Return a minimal RunResult so main() can finish printing/returning.
        return run_with_ceiling.RunResult(
            exit_code=0,
            peak_commit=0,
            peak_rss=0,
            tick_count=0,
            duration_s=0.0,
            summary_json_path=tmp_path / "x-summary.json",
            telemetry_csv_path=tmp_path / "x-telemetry.csv",
        )

    monkeypatch.setattr(wrapper, "run_with_ceiling", _fake_rwc)

    base_args = [
        "--run-id", "wrapper-test",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        "--no-ceiling",  # skip CEILING_BYTES-None guard + host-drift path
        "--log-dir", str(tmp_path),
    ]
    rc = wrapper.main(base_args + extra_args)
    assert rc == 0, f"wrapper main() returned {rc}"
    assert "command" in captured, "run_with_ceiling was not invoked"
    return captured["command"]


def test_wrapper_forwards_output_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--output-dir X` appends `--output-dir X` to the child command."""
    out_dir = tmp_path / "scratch_parquets"
    command = _run_wrapper_capturing_command(
        monkeypatch, tmp_path, ["--output-dir", str(out_dir)],
    )
    assert "--output-dir" in command
    idx = command.index("--output-dir")
    assert command[idx + 1] == str(out_dir)


def test_wrapper_forwards_no_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--no-manifest` appends the flag (no value) to the child command."""
    command = _run_wrapper_capturing_command(
        monkeypatch, tmp_path, ["--no-manifest"],
    )
    assert "--no-manifest" in command
    # Must NOT also add --manifest-path
    assert "--manifest-path" not in command


def test_wrapper_forwards_manifest_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--manifest-path X` appends `--manifest-path X` to the child command."""
    scratch_manifest = tmp_path / "scratch-manifest.csv"
    command = _run_wrapper_capturing_command(
        monkeypatch, tmp_path, ["--manifest-path", str(scratch_manifest)],
    )
    assert "--manifest-path" in command
    idx = command.index("--manifest-path")
    assert command[idx + 1] == str(scratch_manifest)
    assert "--no-manifest" not in command


def test_wrapper_mutex_no_manifest_and_manifest_path(
    tmp_path: Path,
) -> None:
    """Passing both `--no-manifest` and `--manifest-path` must argparse-exit 2."""
    wrapper = _load_wrapper()
    args = [
        "--run-id", "mutex-test",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        "--no-ceiling",
        "--log-dir", str(tmp_path),
        "--no-manifest",
        "--manifest-path", str(tmp_path / "x.csv"),
    ]
    with pytest.raises(SystemExit) as excinfo:
        wrapper.main(args)
    assert excinfo.value.code == 2


def test_wrapper_omits_flags_when_not_set(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With none of the three flags set, child command contains none of them."""
    command = _run_wrapper_capturing_command(monkeypatch, tmp_path, [])
    assert "--output-dir" not in command
    assert "--no-manifest" not in command
    assert "--manifest-path" not in command


# --- RA-20260426-1 P5: --source / --cache-dir / --cache-manifest passthrough ---


def test_forwards_source_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--source=cache --cache-dir X --cache-manifest Y` forwards all three flags."""
    cache_dir = tmp_path / "raw_trades_cache"
    cache_manifest = tmp_path / "cache-manifest.csv"
    command = _run_wrapper_capturing_command(
        monkeypatch,
        tmp_path,
        [
            "--source", "cache",
            "--cache-dir", str(cache_dir),
            "--cache-manifest", str(cache_manifest),
        ],
    )
    assert "--source" in command
    idx_source = command.index("--source")
    assert command[idx_source + 1] == "cache"
    assert "--cache-dir" in command
    idx_dir = command.index("--cache-dir")
    assert command[idx_dir + 1] == str(cache_dir)
    assert "--cache-manifest" in command
    idx_man = command.index("--cache-manifest")
    assert command[idx_man + 1] == str(cache_manifest)


def test_forwards_source_sentinel_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No --source flag → child command contains `--source sentinel`, no cache flags."""
    command = _run_wrapper_capturing_command(monkeypatch, tmp_path, [])
    assert "--source" in command
    idx = command.index("--source")
    assert command[idx + 1] == "sentinel"
    assert "--cache-dir" not in command
    assert "--cache-manifest" not in command


def test_mutex_source_cache_requires_cache_dir(
    tmp_path: Path,
) -> None:
    """`--source=cache` without `--cache-dir` must argparse-exit 2."""
    wrapper = _load_wrapper()
    args = [
        "--run-id", "mutex-cache-dir",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        "--no-ceiling",
        "--log-dir", str(tmp_path),
        "--source", "cache",
        "--cache-manifest", str(tmp_path / "m.csv"),
    ]
    with pytest.raises(SystemExit) as excinfo:
        wrapper.main(args)
    assert excinfo.value.code == 2


def test_mutex_source_cache_requires_cache_manifest(
    tmp_path: Path,
) -> None:
    """`--source=cache` without `--cache-manifest` must argparse-exit 2."""
    wrapper = _load_wrapper()
    args = [
        "--run-id", "mutex-cache-manifest",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        "--no-ceiling",
        "--log-dir", str(tmp_path),
        "--source", "cache",
        "--cache-dir", str(tmp_path / "cache"),
    ]
    with pytest.raises(SystemExit) as excinfo:
        wrapper.main(args)
    assert excinfo.value.code == 2


def test_mutex_source_sentinel_rejects_cache_flags(
    tmp_path: Path,
) -> None:
    """`--source=sentinel --cache-dir X` must argparse-exit 2 (stray cache flag)."""
    wrapper = _load_wrapper()
    args = [
        "--run-id", "mutex-sentinel",
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-31",
        "--ticker", "WDO",
        "--no-ceiling",
        "--log-dir", str(tmp_path),
        "--source", "sentinel",
        "--cache-dir", str(tmp_path / "cache"),
    ]
    with pytest.raises(SystemExit) as excinfo:
        wrapper.main(args)
    assert excinfo.value.code == 2


# --- T002.4 / ADR-4 §14.5.2 B1 — child-side peak telemetry -----------------
#
# These tests verify the ADR-4 §14.5.2 B1 telemetry mechanism:
#   AC-A: child emits TELEMETRY_CHILD_PEAK_EXIT on exit
#   AC-B: parent wrapper records in CSV + JSON
#   AC-C: psutil primary path exercised (ctypes fallback path is covered by
#         hand-crafting a log line so the parser is unit-tested in isolation)
#   AC-K(iii): missing-telemetry fallback does not crash
#
# The tests are scoped to the parsing + summary augmentation surface of
# ``scripts/run_materialize_with_ceiling.py`` — the child-side emission
# function is tested in ``tests/unit/test_materialize_child_peak_telemetry.py``.


def test_child_peak_telemetry_emitted_on_normal_exit(
    tmp_path: Path,
) -> None:
    """AC-A: the child's ``main()`` emits one TELEMETRY_CHILD_PEAK_EXIT line.

    We invoke ``scripts/materialize_parquet.py`` as a real subprocess with
    ``--dry-run`` (plan-only, no DB connect) and scan stdout for the
    structured line. psutil 7.2.2 is the live primary path (AC-C psutil side).
    """
    import subprocess as _sp

    scripts_dir = _REPO_ROOT / "scripts"
    cmd = [
        sys.executable,
        str(scripts_dir / "materialize_parquet.py"),
        "--start-date", "2024-08-01",
        "--end-date", "2024-08-01",
        "--ticker", "WDO",
        "--dry-run",
        "--no-manifest",
        "--output-dir", str(tmp_path / "dry_out"),
    ]
    completed = _sp.run(cmd, capture_output=True, text=True, timeout=60)
    # Dry-run returns 0 regardless of DB state.
    assert completed.returncode == 0, (
        f"child rc={completed.returncode}\n"
        f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
    )
    # Peak-telemetry line must be on stdout exactly once.
    peak_lines = [
        ln for ln in completed.stdout.splitlines()
        if ln.startswith("TELEMETRY_CHILD_PEAK_EXIT")
    ]
    assert len(peak_lines) == 1, (
        f"expected exactly 1 TELEMETRY_CHILD_PEAK_EXIT line, "
        f"got {len(peak_lines)}:\n{completed.stdout}"
    )
    # Parse and sanity-check the values.
    wrapper = _load_wrapper()
    payload = wrapper._parse_child_peak_line(peak_lines[0])
    assert payload is not None
    # AC-A: psutil primary path on Windows yields positive peak values.
    assert payload["peak_commit_bytes_child_self_reported"] > 0
    assert payload["peak_wset_bytes_child_self_reported"] > 0
    assert payload["child_pid"] > 0
    assert "child_peak_error" not in payload


def test_wrapper_parses_and_surfaces_child_peak_in_summary(
    tmp_path: Path,
) -> None:
    """AC-B: the parent wrapper parses the child's structured line from the
    run log and merges the new fields into the summary JSON.

    This isolates the parser + summary-augmentation surface so we can assert
    the exact JSON layout (AC-I: additive, non-breaking to SUMMARY_JSON_FIELDS).
    """
    wrapper = _load_wrapper()
    # Simulate a child run log — library would write it via subprocess.Popen
    # redirection, but we only need its tail to contain the peak line.
    run_id = "ac-b-surface"
    log_path = tmp_path / f"{run_id}.log"
    log_path.write_text(
        "[dry-run] ticker=WDO window=2024-08-01..2024-08-01 months=1\n"
        "[dry-run]   -> 2024-08 [2024-08-01 .. 2024-08-01] -> ...\n"
        "TELEMETRY_CHILD_PEAK_EXIT commit=123456789 wset=98765432 "
        "pid=12345 timestamp_brt=2026-04-24T10:20:30\n",
        encoding="utf-8",
    )
    # Seed a minimal summary JSON matching SUMMARY_JSON_FIELDS so the
    # augmentation function has something to merge into.
    summary_path = tmp_path / f"{run_id}-summary.json"
    base_summary = {k: 0 for k in SUMMARY_JSON_FIELDS}
    base_summary["run_id"] = run_id
    base_summary["start_ts"] = "2026-04-24T10:19:00"
    base_summary["end_ts"] = "2026-04-24T10:20:30"
    base_summary["ratio_commit_rss"] = None
    summary_path.write_text(json.dumps(base_summary, indent=2) + "\n", encoding="utf-8")

    peak_payload = wrapper._extract_child_peak_from_log(log_path)
    assert peak_payload is not None
    wrapper._augment_summary_with_child_peak(summary_path, peak_payload)

    augmented = json.loads(summary_path.read_text(encoding="utf-8"))
    # AC-I: existing SUMMARY_JSON_FIELDS keys all still present, untouched.
    for field in SUMMARY_JSON_FIELDS:
        assert field in augmented, f"missing summary field after augment: {field}"
    # AC-B: new fields present with the exact values from the log line.
    assert augmented["peak_commit_bytes_child_self_reported"] == 123_456_789
    assert augmented["peak_wset_bytes_child_self_reported"] == 98_765_432
    assert augmented["child_pid"] == 12345
    assert augmented["child_peak_timestamp_brt"] == "2026-04-24T10:20:30"
    assert augmented["child_peak_telemetry_missing"] is False


def test_wrapper_handles_missing_child_peak_without_crash(
    tmp_path: Path,
) -> None:
    """AC-K(iii): if the child never emits the structured line (e.g. crashed
    before the ``finally`` ran), the wrapper MUST NOT crash. It records
    ``child_peak_telemetry_missing=True`` in the summary JSON so downstream
    consumers can distinguish "missing" from "zero"."""
    wrapper = _load_wrapper()
    run_id = "ac-k-missing"
    log_path = tmp_path / f"{run_id}.log"
    # Log contains normal output but NO TELEMETRY_CHILD_PEAK_EXIT line.
    log_path.write_text(
        "[materialize] some normal output\n"
        "[materialize] more normal output\n"
        "ERROR: simulated crash before finally ran\n",
        encoding="utf-8",
    )
    summary_path = tmp_path / f"{run_id}-summary.json"
    base_summary = {k: 0 for k in SUMMARY_JSON_FIELDS}
    base_summary["run_id"] = run_id
    base_summary["start_ts"] = "2026-04-24T11:00:00"
    base_summary["end_ts"] = "2026-04-24T11:01:00"
    base_summary["ratio_commit_rss"] = None
    summary_path.write_text(json.dumps(base_summary, indent=2) + "\n", encoding="utf-8")

    peak_payload = wrapper._extract_child_peak_from_log(log_path)
    assert peak_payload is None
    # Augmentation with None MUST still succeed (AC-K(iii)) and mark missing.
    wrapper._augment_summary_with_child_peak(summary_path, peak_payload)
    augmented = json.loads(summary_path.read_text(encoding="utf-8"))
    assert augmented["child_peak_telemetry_missing"] is True
    # Must NOT invent peak values (AC-B non-breaking: missing means missing).
    assert "peak_commit_bytes_child_self_reported" not in augmented
    assert "peak_wset_bytes_child_self_reported" not in augmented


def test_wrapper_parses_degraded_line_with_error_field(
    tmp_path: Path,
) -> None:
    """AC-C (defensive): a ``TELEMETRY_CHILD_PEAK_EXIT`` line carrying an
    ``error=<reason>`` suffix (psutil+ctypes both failed) is still parsed
    — the wrapper preserves ``commit=0 wset=0`` plus the error message so
    Quinn/Riven can audit the collection failure without the run aborting.
    """
    wrapper = _load_wrapper()
    line = (
        "TELEMETRY_CHILD_PEAK_EXIT commit=0 wset=0 pid=7777 "
        "timestamp_brt=2026-04-24T12:00:00 "
        "error=psutil_missing_peak_fields;ctypes_error:OSError:boom"
    )
    payload = wrapper._parse_child_peak_line(line)
    assert payload is not None
    assert payload["peak_commit_bytes_child_self_reported"] == 0
    assert payload["peak_wset_bytes_child_self_reported"] == 0
    assert payload["child_pid"] == 7777
    assert "child_peak_error" in payload
    assert "psutil_missing_peak_fields" in payload["child_peak_error"]
