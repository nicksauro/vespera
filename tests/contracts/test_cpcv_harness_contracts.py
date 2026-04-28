"""T9 — contract tests for the CPCV dry-run runner (AC12 + AC13 of T002.0f).

Coverage:
    AC12 artifacts persisted (5 files in data/baseline-run/cpcv-dryrun-{run_id}/):
      - test_artifacts_persisted_five_files
      - test_run_id_directory_structure (--run-id custom-test-001 honoured)

    AC13 spec_sha256 lock:
      - test_spec_sha256_lock_match_passes (re-run same spec → exit 0)
      - test_spec_sha256_lock_mismatch_exit_2 (modify spec between runs → exit 2)
      - test_compute_spec_sha256_stable (sha256 byte-stable across calls)
      - test_assert_spec_lock_first_run_no_op (no prior stamp → no-op)
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest


# Ensure scripts/ + repo root importable.
_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import run_cpcv_dry_run as sut  # noqa: E402


# =====================================================================
# Local fixtures (mirrors tests/scripts but kept independent so contract
# tests can run alone in CI gating).
# =====================================================================
def _write_minimal_spec(path: Path, *, in_sample: str = "2024-07-15 to 2024-07-31") -> None:
    import yaml
    path.write_text(
        yaml.safe_dump(
            {
                "data_splits": {"in_sample": in_sample},
                "cv_scheme": {
                    "type": "CPCV",
                    "n_groups": 10,
                    "k": 2,
                    "embargo_sessions": 1,
                },
            }
        ),
        encoding="utf-8",
    )


def _write_warmup_stubs(tmp_path: Path, as_of: date) -> tuple[Path, Path]:
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
    log = tmp_path / "research-log.md"
    log.write_text(
        "---\n"
        "story_id: TEST.0\n"
        "date_brt: '2026-04-26'\n"
        f"n_trials: {n_trials}\n"
        "trials_enumerated: ['T1', 'T2', 'T3', 'T4', 'T5']\n"
        "description: test seed entry\n"
        "spec_ref: docs/ml/specs/test.yaml\n"
        "signed_by: test-suite\n"
        "---\n",
        encoding="utf-8",
    )
    return log


def _build_argv(base: dict[str, str], *extras: str) -> list[str]:
    argv: list[str] = []
    for k, v in base.items():
        argv.append(k)
        argv.append(v)
    argv.extend(extras)
    return argv


def _make_fake_report_and_stamp(spec_sha: str = "deadbeef" * 8):
    """Build a minimal FullReport + DeterminismStamp that survives JSON round-trip."""
    from packages.vespera_metrics.report import (
        FullReport,
        KillDecision,
        MetricsResult,
    )
    from packages.vespera_cpcv import DeterminismStamp

    metrics = MetricsResult(
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
    kd = KillDecision(
        verdict="GO",
        reasons=(),
        k1_dsr_passed=True,
        k2_pbo_passed=True,
        k3_ic_decay_passed=True,
    )
    report = FullReport(metrics=metrics, per_path_results=(), kill_decision=kd)
    stamp = DeterminismStamp(
        seed=42,
        simulator_version="test",
        dataset_sha256="dataset-sha",
        spec_sha256=spec_sha,
        spec_version="0.2.0",
        engine_config_sha256="",
        rollover_calendar_sha256=None,
        cost_atlas_sha256=None,
        cpcv_config_sha256="cpcv-sha",
        python_version="3.11.0",
        numpy_version="1.0.0",
        pandas_version="2.0.0",
        run_id="contract-test",
        timestamp_brt=datetime(2026, 4, 26, 0, 0, 0),
    )
    return report, stamp


@pytest.fixture
def base_args(tmp_path: Path) -> dict[str, str]:
    spec = tmp_path / "spec.yaml"
    _write_minimal_spec(spec)
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
        "--mem-poll-interval-s": "60",
        "--in-sample-start": "2024-07-15",
        "--in-sample-end": "2024-07-31",
        "--seed": "42",
    }


# =====================================================================
# AC12 — artifacts persisted
# =====================================================================
def test_artifacts_persisted_five_files(base_args, tmp_path, monkeypatch):
    """Per AC12 — post-run, 5 files exist in data/baseline-run/cpcv-dryrun-{run_id}/.

    Files:
        telemetry.csv
        full_report.md
        full_report.json
        determinism_stamp.json
        events_metadata.json
    """
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    spec_sha = sut.compute_spec_sha256(Path(base_args["--spec"]))
    fake_report, fake_stamp = _make_fake_report_and_stamp(spec_sha=spec_sha)
    fake_meta = {"phase": "full", "n_events": 10, "n_trials": 5}

    def fake_run_phase(*, label, **_kwargs):  # noqa: ARG001
        return fake_report, fake_stamp, fake_meta

    with patch.object(sut, "_run_phase", side_effect=fake_run_phase):
        rc = sut.main(_build_argv(base_args, "--run-id", "ac12-artifacts"))

    assert rc == 0, f"expected exit 0, got {rc}"

    out_dir = Path(base_args["--output-root"]) / "cpcv-dryrun-ac12-artifacts"
    expected = {
        "telemetry.csv",
        "full_report.md",
        "full_report.json",
        "determinism_stamp.json",
        "events_metadata.json",
    }
    actual = {p.name for p in out_dir.iterdir() if p.is_file()}
    missing = expected - actual
    assert not missing, f"AC12 missing artifacts: {missing}; have {actual}"


def test_run_id_directory_structure(base_args, tmp_path, monkeypatch):
    """Per AC12 — --run-id custom-test-001 → cpcv-dryrun-custom-test-001/ created."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    fake_report, fake_stamp = _make_fake_report_and_stamp()
    fake_meta = {"phase": "full", "n_events": 1, "n_trials": 5}

    with patch.object(
        sut, "_run_phase", side_effect=lambda **kw: (fake_report, fake_stamp, fake_meta)
    ):
        rc = sut.main(_build_argv(base_args, "--run-id", "custom-test-001"))

    assert rc == 0
    target = Path(base_args["--output-root"]) / "cpcv-dryrun-custom-test-001"
    assert target.exists() and target.is_dir(), f"expected {target} to exist"


def test_full_report_json_round_trip(base_args, tmp_path, monkeypatch):
    """Per AC12 — full_report.json is valid JSON and contains expected top-level keys."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    fake_report, fake_stamp = _make_fake_report_and_stamp()
    fake_meta = {"phase": "full"}

    with patch.object(
        sut, "_run_phase", side_effect=lambda **kw: (fake_report, fake_stamp, fake_meta)
    ):
        sut.main(_build_argv(base_args, "--run-id", "json-roundtrip"))

    json_path = Path(base_args["--output-root"]) / "cpcv-dryrun-json-roundtrip" / "full_report.json"
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "metrics" in payload
    assert "kill_decision" in payload
    assert payload["metrics"]["dsr"] == 0.5
    assert payload["kill_decision"]["verdict"] == "GO"


def test_determinism_stamp_json_contains_spec_sha(base_args, tmp_path, monkeypatch):
    """Per AC13 — persisted determinism_stamp.json contains spec_sha256 (used for lock check)."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    spec_sha = sut.compute_spec_sha256(Path(base_args["--spec"]))
    fake_report, fake_stamp = _make_fake_report_and_stamp(spec_sha=spec_sha)
    fake_meta = {"phase": "full"}

    with patch.object(
        sut, "_run_phase", side_effect=lambda **kw: (fake_report, fake_stamp, fake_meta)
    ):
        sut.main(_build_argv(base_args, "--run-id", "stamp-sha-check"))

    stamp_path = (
        Path(base_args["--output-root"]) / "cpcv-dryrun-stamp-sha-check" / "determinism_stamp.json"
    )
    payload = json.loads(stamp_path.read_text(encoding="utf-8"))
    assert payload["spec_sha256"] == spec_sha


# =====================================================================
# AC13 — spec_sha256 lock
# =====================================================================
def test_compute_spec_sha256_stable(tmp_path: Path):
    """Per AC13 — repeated sha256 calls on identical bytes yield identical digest."""
    spec = tmp_path / "spec.yaml"
    spec.write_text("hello: world\n", encoding="utf-8")
    a = sut.compute_spec_sha256(spec)
    b = sut.compute_spec_sha256(spec)
    assert a == b
    assert len(a) == 64  # sha256 hex


def test_assert_spec_lock_first_run_no_op(tmp_path: Path):
    """Per AC13 — when no prior determinism_stamp.json exists, lock is a no-op."""
    stamp_path = tmp_path / "determinism_stamp.json"
    # Should not raise, should not write anything.
    sut.assert_spec_lock(stamp_path, "any-sha")
    assert not stamp_path.exists()


def test_assert_spec_lock_match_passes(tmp_path: Path):
    """Per AC13 — prior stamp with matching spec_sha256 is a no-op (no exit)."""
    stamp_path = tmp_path / "determinism_stamp.json"
    sha = "a" * 64
    stamp_path.write_text(json.dumps({"spec_sha256": sha}), encoding="utf-8")
    # Should NOT raise.
    sut.assert_spec_lock(stamp_path, sha)


def test_assert_spec_lock_mismatch_exits_2(tmp_path: Path):
    """Per AC13 — prior stamp with different spec_sha256 raises SystemExit(2)."""
    stamp_path = tmp_path / "determinism_stamp.json"
    stamp_path.write_text(json.dumps({"spec_sha256": "old-sha"}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        sut.assert_spec_lock(stamp_path, "new-sha")
    assert exc_info.value.code == 2


def test_spec_sha256_lock_end_to_end_mismatch_exit_2(base_args, tmp_path, monkeypatch):
    """Per AC13 — modify spec between runs sharing a --run-id → second run exits 2."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    spec_path = Path(base_args["--spec"])
    spec_sha_v1 = sut.compute_spec_sha256(spec_path)
    fake_report, fake_stamp_v1 = _make_fake_report_and_stamp(spec_sha=spec_sha_v1)
    fake_meta = {"phase": "full"}

    # Run 1 — populates the determinism_stamp.json with spec_sha_v1.
    with patch.object(
        sut, "_run_phase", side_effect=lambda **kw: (fake_report, fake_stamp_v1, fake_meta)
    ):
        rc1 = sut.main(_build_argv(base_args, "--run-id", "lock-test"))
    assert rc1 == 0

    # Sanity: the stamp on disk has spec_sha_v1.
    stamp_path = Path(base_args["--output-root"]) / "cpcv-dryrun-lock-test" / "determinism_stamp.json"
    assert json.loads(stamp_path.read_text(encoding="utf-8"))["spec_sha256"] == spec_sha_v1

    # Modify the spec — sha256 changes.
    _write_minimal_spec(spec_path, in_sample="2024-07-16 to 2024-07-31")  # different content
    spec_sha_v2 = sut.compute_spec_sha256(spec_path)
    assert spec_sha_v2 != spec_sha_v1

    # Run 2 — same --run-id → assert_spec_lock should fire exit code 2.
    rc2 = sut.main(_build_argv(base_args, "--run-id", "lock-test"))
    assert rc2 == 2, f"expected exit 2 on spec mismatch, got {rc2}"


def test_spec_sha256_lock_match_idempotent_passes(base_args, tmp_path, monkeypatch):
    """Per AC13 — re-running with identical spec + same --run-id passes (idempotent)."""
    _write_research_log(tmp_path)
    monkeypatch.chdir(tmp_path)

    spec_sha = sut.compute_spec_sha256(Path(base_args["--spec"]))
    fake_report, fake_stamp = _make_fake_report_and_stamp(spec_sha=spec_sha)
    fake_meta = {"phase": "full"}

    with patch.object(
        sut, "_run_phase", side_effect=lambda **kw: (fake_report, fake_stamp, fake_meta)
    ):
        rc1 = sut.main(_build_argv(base_args, "--run-id", "idempotent-test"))
        rc2 = sut.main(_build_argv(base_args, "--run-id", "idempotent-test"))

    assert rc1 == 0
    assert rc2 == 0  # spec unchanged → lock check is a no-op
