"""T8 — tests for ``scripts/run_cpcv_dry_run.py`` (AC7-AC11 of Story T002.0f).

Coverage:
    AC7  argparse:
      - test_argparse_required_spec               — missing --spec → SystemExit 2
      - test_argparse_seed_default_and_override   — --seed 99 propagates
      - test_argparse_mem_soft_cap_default        — default == 6.0 GiB
      - test_argparse_dry_run_default_true        — --dry-run BooleanOptional
      - test_argparse_run_id_override             — --run-id custom flows
    AC8  telemetry CSV + soft halt:
      - test_telemetry_csv_columns_match_superset — header matches story+protocol superset
      - test_6gb_soft_halt_mock_graceful          — psutil patched to 7 GiB → halt_event fires + exit 1
    AC9  hold-out lock guard:
      - test_holdout_lock_guard_fires             — window inside hold-out → exit 1
      - test_holdout_lock_bypass_with_env         — VESPERA_UNLOCK_HOLDOUT=1 → guard does NOT fire
    AC10 smoke:
      - test_smoke_completes_with_mock_pipeline   — --smoke + outside-holdout window → exit 0
    AC11 smoke failure aborts full:
      - test_smoke_failure_aborts_full            — smoke raises → full not invoked, exit 1
"""
from __future__ import annotations

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import pytest


# Ensure scripts/ is importable for the SUT.
_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import run_cpcv_dry_run as sut  # noqa: E402


# =====================================================================
# Fixtures — minimal valid spec yaml + warmup state stubs
# =====================================================================
def _write_minimal_spec(path: Path, *, in_sample: str = "2024-07-01 to 2025-06-30") -> None:
    """Write a spec yaml with just the fields the CLI consumes:
    ``data_splits.in_sample`` and ``cv_scheme`` (for CPCVConfig).
    """
    content = {
        "data_splits": {"in_sample": in_sample},
        "cv_scheme": {
            "type": "CPCV",
            "n_groups": 10,
            "k": 2,
            "embargo_sessions": 1,
        },
    }
    import yaml
    path.write_text(yaml.safe_dump(content), encoding="utf-8")


def _write_warmup_stubs(tmp_path: Path, as_of: date) -> tuple[Path, Path]:
    """Write atr + percentiles JSON state files that satisfy WarmUpGate."""
    atr = tmp_path / "atr_20d.json"
    pct = tmp_path / "percentiles_126d.json"
    atr.write_text(json.dumps({"as_of_date": as_of.isoformat()}), encoding="utf-8")
    pct.write_text(
        json.dumps(
            {
                "as_of_date": as_of.isoformat(),
                "magnitude": {"p20": 1.0, "p60": 2.0, "p80": 3.0},
                "atr_day_ratio": {"p20": 0.5, "p60": 1.0, "p80": 1.5},
            }
        ),
        encoding="utf-8",
    )
    return atr, pct


def _write_calendar(tmp_path: Path) -> Path:
    """Write a permissive calendar YAML (no holidays/copom/expirations)."""
    import yaml
    cal = tmp_path / "calendar.yaml"
    cal.write_text(
        yaml.safe_dump(
            {
                "version": "test",
                "copom_meetings": [],
                "br_holidays": [],
                "wdo_expirations": [],
            }
        ),
        encoding="utf-8",
    )
    return cal


def _write_research_log(tmp_path: Path, n_trials: int = 5) -> Path:
    """Write a minimal research-log.md that read_research_log_cumulative accepts."""
    log = tmp_path / "research-log.md"
    body = (
        "---\n"
        "story_id: TEST.0\n"
        "date_brt: '2026-04-26'\n"
        f"n_trials: {n_trials}\n"
        "trials_enumerated: ['T1', 'T2', 'T3', 'T4', 'T5']\n"
        "description: test seed entry\n"
        "spec_ref: docs/ml/specs/test.yaml\n"
        "signed_by: test-suite\n"
        "---\n"
    )
    log.write_text(body, encoding="utf-8")
    return log


@pytest.fixture
def base_args(tmp_path: Path) -> dict[str, str]:
    """Common CLI arg set — valid spec + permissive calendar + warmup OK + seed=42.

    Window defaults to 2024-07-15..2024-07-31 (outside hold-out
    [2025-07-01, 2026-04-21]).
    """
    spec = tmp_path / "spec.yaml"
    _write_minimal_spec(spec, in_sample="2024-07-15 to 2024-07-31")
    cal = _write_calendar(tmp_path)
    atr, pct = _write_warmup_stubs(tmp_path, date(2024, 7, 15))
    out_root = tmp_path / "out"

    return {
        "--spec": str(spec),
        "--calendar": str(cal),
        "--warmup-atr": str(atr),
        "--warmup-percentiles": str(pct),
        "--output-root": str(out_root),
        "--engine-config": str(tmp_path / "missing-engine-config.yaml"),
        "--mem-poll-interval-s": "60",  # slow poller for tests
        "--in-sample-start": "2024-07-15",
        "--in-sample-end": "2024-07-31",
        "--seed": "42",
    }


def _argv_from(d: dict[str, str], *extras: str) -> list[str]:
    """Flatten an ordered dict of CLI args into argv list, plus extras."""
    out: list[str] = []
    for k, v in d.items():
        out.append(k)
        out.append(v)
    out.extend(extras)
    return out


# =====================================================================
# AC7 — argparse
# =====================================================================
def test_argparse_required_spec_exits_2():
    """Per AC7 — omitting --spec raises SystemExit(2) (argparse default)."""
    parser = sut.build_arg_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code == 2


def test_argparse_seed_default_and_override():
    """Per Beckett T0 — --seed default 42, override propagates to args.seed."""
    parser = sut.build_arg_parser()
    a_default = parser.parse_args(["--spec", "x.yaml"])
    assert a_default.seed == sut.DEFAULT_SEED == 42
    a_override = parser.parse_args(["--spec", "x.yaml", "--seed", "99"])
    assert a_override.seed == 99


def test_argparse_mem_soft_cap_default_six_gib():
    """Per AC8 + memory protocol — default 6.0 GiB soft cap; configurable."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--spec", "x.yaml"])
    assert a.mem_soft_cap_gb == sut.DEFAULT_SOFT_CAP_GB == 6.0
    a2 = parser.parse_args(["--spec", "x.yaml", "--mem-soft-cap-gb", "8.0"])
    assert a2.mem_soft_cap_gb == 8.0


def test_argparse_dry_run_default_true():
    """Per AC7 — --dry-run is BooleanOptionalAction; default True; --no-dry-run → False."""
    parser = sut.build_arg_parser()
    assert parser.parse_args(["--spec", "x.yaml"]).dry_run is True
    assert parser.parse_args(["--spec", "x.yaml", "--no-dry-run"]).dry_run is False


def test_argparse_run_id_override(tmp_path: Path):
    """Per AC7 — --run-id is a free-form string used as artifact dir suffix."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--spec", "x.yaml", "--run-id", "custom-run-001"])
    assert a.run_id == "custom-run-001"


def test_argparse_in_sample_dates_iso_parsed():
    """--in-sample-start/end accept YYYY-MM-DD."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(
        ["--spec", "x.yaml", "--in-sample-start", "2024-07-01", "--in-sample-end", "2024-07-31"]
    )
    assert a.in_sample_start == date(2024, 7, 1)
    assert a.in_sample_end == date(2024, 7, 31)


def test_argparse_invalid_iso_date_rejected():
    """Bad ISO date → argparse error."""
    parser = sut.build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--spec", "x.yaml", "--in-sample-start", "07/15/2024"])


# =====================================================================
# AC9 — hold-out lock guard
# =====================================================================
def test_holdout_lock_guard_fires_inside_holdout(base_args, tmp_path, monkeypatch):
    """Per AC9 — window crossing [2025-07-01, 2026-04-21] without unlock → exit 1."""
    # Force window into hold-out range.
    base_args["--in-sample-start"] = "2025-07-15"
    base_args["--in-sample-end"] = "2025-08-15"
    # Re-write warmup to that date so gate would otherwise pass.
    _write_warmup_stubs(tmp_path, date(2025, 7, 15))
    base_args["--warmup-atr"] = str(tmp_path / "atr_20d.json")
    base_args["--warmup-percentiles"] = str(tmp_path / "percentiles_126d.json")

    # Ensure unlock env var is NOT set.
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)

    rc = sut.main(_argv_from(base_args))
    assert rc == 1


def test_holdout_lock_bypass_with_env(base_args, tmp_path, monkeypatch):
    """Per AC9 — VESPERA_UNLOCK_HOLDOUT=1 allows hold-out window (guard does NOT fire).

    NOTE: We do NOT actually run a hold-out backtest — we only verify that
    the guard does not raise. The full pipeline may still fail downstream
    on warmup or other constraints; we assert specifically that the exit
    is NOT 1 due to hold-out.
    """
    base_args["--in-sample-start"] = "2025-07-15"
    base_args["--in-sample-end"] = "2025-08-15"
    _write_warmup_stubs(tmp_path, date(2025, 7, 15))
    base_args["--warmup-atr"] = str(tmp_path / "atr_20d.json")
    base_args["--warmup-percentiles"] = str(tmp_path / "percentiles_126d.json")
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VESPERA_UNLOCK_HOLDOUT", "1")

    # Patch _holdout_lock module to verify it was called and did NOT raise.
    with patch.object(sut, "assert_holdout_safe") as mock_guard:
        # Force the guard to be a no-op (we only want to verify it is INVOKED
        # with the unlock env active — actual unlock semantics belong to the
        # holdout_lock module's own contract tests).
        mock_guard.return_value = None
        # Patch the heavy pipeline so we don't actually run CPCV; the
        # assertion is that the guard ran AND we got past it.
        with patch.object(sut, "_run_phase", side_effect=RuntimeError("stub-shortcut")):
            rc = sut.main(_argv_from(base_args))

    mock_guard.assert_called_once()
    # Exit 1 from the stubbed RuntimeError, NOT from the guard.
    assert rc == 1


# =====================================================================
# AC8 — telemetry CSV columns + 6 GiB soft halt mock
# =====================================================================
def test_telemetry_csv_columns_superset(tmp_path: Path):
    """Per AC8 + Pax gap #2 — header MUST contain story columns AND memory protocol columns."""
    csv_path = tmp_path / "tele.csv"
    poller = sut.MemoryPoller(
        csv_path,
        soft_cap_bytes=10 * 1024**3,
        poll_interval_s=60.0,
        enabled=True,
    )
    # Story-required columns.
    for col in ("rss_mb", "vms_mb", "cpu_pct", "fold_index", "trial_id"):
        assert col in sut.TELEMETRY_COLUMNS, f"story column {col} missing from header"
    # feedback_cpcv_dry_run_memory_protocol.md columns.
    for col in ("peak_commit_bytes", "peak_wset_bytes", "sample_size", "duration_ms"):
        assert col in sut.TELEMETRY_COLUMNS, f"protocol column {col} missing from header"
    # Header was written.
    with csv_path.open("r", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert tuple(header) == sut.TELEMETRY_COLUMNS

    poller.stop()


def test_6gb_soft_halt_mock_sets_event(tmp_path: Path):
    """Per AC8 — psutil patched to return 7 GiB RSS → halt_event fires; NO kill -9."""
    csv_path = tmp_path / "tele.csv"
    poller = sut.MemoryPoller(
        csv_path,
        soft_cap_bytes=6 * 1024**3,  # 6 GiB cap
        poll_interval_s=60.0,
        enabled=True,
    )

    class _FakeMem:
        rss = 7 * 1024**3  # over the cap
        vms = 8 * 1024**3

    class _FakeProc:
        def memory_info(self):  # noqa: D401
            return _FakeMem()

        def cpu_percent(self, interval=None):  # noqa: ARG002
            return 5.0

    with patch.object(sut.psutil, "Process", return_value=_FakeProc()):
        poller._write_row(phase="test_halt", note="forced")

    assert poller.halt_event.is_set(), "halt_event must fire when RSS exceeds soft cap"
    # CSV row was written (graceful — no crash, no kill).
    with csv_path.open("r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    # Header + at least one row.
    assert len(rows) >= 2
    # Soft-halt note recorded in last row.
    last = rows[-1]
    note_col_idx = sut.TELEMETRY_COLUMNS.index("note")
    assert "SOFT_HALT_FIRED" in last[note_col_idx]

    poller.stop()


def test_6gb_soft_halt_does_not_set_event_under_cap(tmp_path: Path):
    """Per AC8 — RSS UNDER the cap does NOT set halt_event."""
    csv_path = tmp_path / "tele.csv"
    poller = sut.MemoryPoller(
        csv_path,
        soft_cap_bytes=6 * 1024**3,
        poll_interval_s=60.0,
        enabled=True,
    )

    class _FakeMem:
        rss = 1 * 1024**3  # 1 GiB — well under
        vms = 2 * 1024**3

    class _FakeProc:
        def memory_info(self):
            return _FakeMem()

        def cpu_percent(self, interval=None):  # noqa: ARG002
            return 3.0

    with patch.object(sut.psutil, "Process", return_value=_FakeProc()):
        poller._write_row(phase="test_normal", note="probe")

    assert not poller.halt_event.is_set()
    poller.stop()


# =====================================================================
# AC10 — smoke completes
# =====================================================================
def test_smoke_completes_with_mock_pipeline(base_args, tmp_path, monkeypatch):
    """Per AC10 — --smoke executes the smoke 1-month phase and completes (exit 0).

    Pipeline is mocked at _run_phase (smoke + full both invoke the same fn);
    we assert that smoke ran first AND full ran after, both succeeded.
    """
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    call_log: list[str] = []

    # Build a fake FullReport + DeterminismStamp the orchestrator can persist.
    from packages.vespera_metrics.report import (
        FullReport,
        KillDecision,
        MetricsResult,
    )
    from packages.vespera_cpcv import DeterminismStamp
    import numpy as np

    fake_metrics = MetricsResult(
        ic_spearman=0.0,
        ic_spearman_ci95=(0.0, 0.0),
        dsr=0.5,
        pbo=0.2,
        sharpe_per_path=np.array([0.5, 0.6]),
        sharpe_mean=0.55,
        sharpe_median=0.55,
        sharpe_std=0.05,
        sortino=0.6,
        mar=0.3,
        ulcer_index=0.05,
        max_drawdown=0.1,
        profit_factor=1.5,
        hit_rate=0.55,
        n_paths=2,
        n_pbo_groups=2,
        n_trials_used=5,
        n_trials_source="docs/ml/research-log.md@test",
        seed_bootstrap=42,
        spec_version="T002-v0.2.3",
        computed_at_brt="2026-04-26T00:00:00",
    )
    fake_kd = KillDecision(
        verdict="GO",
        reasons=(),
        k1_dsr_passed=True,
        k2_pbo_passed=True,
        k3_ic_decay_passed=True,
    )
    fake_report = FullReport(metrics=fake_metrics, per_path_results=(), kill_decision=fake_kd)
    fake_stamp = DeterminismStamp(
        seed=42,
        simulator_version="test",
        dataset_sha256="abc",
        spec_sha256="def",
        spec_version="0.2.0",
        engine_config_sha256="",
        rollover_calendar_sha256=None,
        cost_atlas_sha256=None,
        cpcv_config_sha256="ghi",
        python_version="3.11.0",
        numpy_version="1.0.0",
        pandas_version="2.0.0",
        run_id="test-run",
        timestamp_brt=datetime(2026, 4, 26),
    )
    fake_meta = {"phase": "test", "n_events": 10, "n_trials": 5}

    def fake_run_phase(*, label, **_kwargs):  # noqa: ARG001
        call_log.append(label)
        return fake_report, fake_stamp, fake_meta

    with patch.object(sut, "_run_phase", side_effect=fake_run_phase):
        rc = sut.main(_argv_from(base_args, "--smoke"))

    assert rc == 0, f"smoke run expected exit 0, got {rc}"
    assert call_log == ["smoke", "full"], f"expected smoke→full sequence, got {call_log}"
    # Smoke artifacts persisted under nested smoke/ dir.
    out_root = Path(base_args["--output-root"])
    runs = list(out_root.glob("cpcv-dryrun-*"))
    assert len(runs) == 1
    smoke_dir = runs[0] / "smoke"
    assert (smoke_dir / "full_report.md").exists()
    assert (smoke_dir / "full_report.json").exists()
    # Full artifacts in run dir top-level.
    assert (runs[0] / "full_report.md").exists()


# =====================================================================
# AC11 — smoke failure aborts full
# =====================================================================
def test_smoke_failure_aborts_full(base_args, tmp_path, monkeypatch):
    """Per AC11 — smoke phase raising aborts full; exit 1; reason in telemetry."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    call_log: list[str] = []

    def fake_run_phase(*, label, **_kwargs):  # noqa: ARG001
        call_log.append(label)
        if label == "smoke":
            raise RuntimeError("smoke pipeline simulated failure")
        return None

    with patch.object(sut, "_run_phase", side_effect=fake_run_phase):
        rc = sut.main(_argv_from(base_args, "--smoke"))

    assert rc == 1
    assert call_log == ["smoke"], f"full must NOT be invoked after smoke fails, got {call_log}"

    # Reason in telemetry CSV.
    out_root = Path(base_args["--output-root"])
    runs = list(out_root.glob("cpcv-dryrun-*"))
    assert len(runs) == 1
    tele = (runs[0] / "telemetry.csv").read_text(encoding="utf-8")
    assert "smoke_aborted" in tele or "smoke_failed" in tele


# =====================================================================
# Run-id derivation determinism (Beckett T0 + R6)
# =====================================================================
def test_derive_default_run_id_deterministic():
    """Same inputs → same run_id (so re-runs land in the same dir)."""
    rid1 = sut.derive_default_run_id("a" * 64, date(2024, 7, 1), date(2025, 6, 30), 42)
    rid2 = sut.derive_default_run_id("a" * 64, date(2024, 7, 1), date(2025, 6, 30), 42)
    assert rid1 == rid2
    rid3 = sut.derive_default_run_id("a" * 64, date(2024, 7, 1), date(2025, 6, 30), 99)
    assert rid3 != rid1
