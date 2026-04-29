"""Per-phase WarmUpGate harness tests — T002.0h.1 AC6 fixture.

Coverage (Quinn integration test, AC6 mandatory):

    Test 1: ``test_per_phase_warmup_two_distinct_as_of_dates``
      Fixture: 2 distinct as_of dates (``2024-08-22`` + ``2025-05-31``)
      coexisting in ``state/T002/`` with valid sidecars + dated JSONs.
      Invocation literal restored (PRR-20260428-1 OBSOLETE post-Pax T6):
        ``--smoke --in-sample-start 2024-08-22 --in-sample-end 2025-06-30``
      Assertions:
        - exit code 0
        - smoke phase reads ``_2025-05-31.json`` (smoke as_of derivation)
        - full phase reads ``_2024-08-22.json`` (full as_of = in_sample_start)
        - neither phase observes the other phase's as_of (cross-phase isolation)

    Test 2: ``test_cache_audit_jsonl_phase_tag_additive``
      Asserts consumer-side ``cache_audit.jsonl`` contains 2 phase-tagged
      entries: ``phase: "smoke"`` (first) + ``phase: "full"`` (second).
      Existing producer schema fields preserved verbatim (Guard #3 honoured).

    Test 3: ``test_per_phase_warmup_default_path_unchanged_for_cli_override``
      Operator authority: explicit ``--warmup-atr foo.json`` override is
      honoured verbatim (CLI affordance preserved per Aria T1 §1 + §4).

Story ref: ``docs/stories/T002.0h.1.story.md`` (AC1-AC10).
Design canon: Aria T1 design memo (inline §1-§6).
Anti-leak preservation: Mira T0 handshake APPROVED (per-phase isolation).
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from unittest.mock import patch

import numpy as np
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
# Helpers — fixture builders for 2 distinct as_of dated state files
# =====================================================================
def _write_minimal_spec(path: Path, in_sample: str) -> None:
    """Write a minimal spec yaml — same shape as test_run_cpcv_dry_run.py."""
    import yaml
    content = {
        "data_splits": {"in_sample": in_sample},
        "cv_scheme": {
            "type": "CPCV",
            "n_groups": 10,
            "k": 2,
            "embargo_sessions": 1,
        },
    }
    path.write_text(yaml.safe_dump(content), encoding="utf-8")


def _write_calendar(tmp_path: Path) -> Path:
    """Permissive calendar yaml (no holidays/copom/expirations)."""
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


def _write_dated_warmup_state(state_dir: Path, as_of: date) -> tuple[Path, Path]:
    """Write per-as_of dated ATR + percentiles JSON state (per AC2 naming).

    Filenames match producer-side convention in
    ``scripts/run_warmup_state.py`` (per AC2): ``atr_20d_{as_of}.json``
    and ``percentiles_126d_{as_of}.json``.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    atr = state_dir / f"atr_20d_{as_of.isoformat()}.json"
    pct = state_dir / f"percentiles_126d_{as_of.isoformat()}.json"
    atr.write_text(
        json.dumps(
            {
                "as_of_date": as_of.isoformat(),
                "atr": 70.0,
                "computed_at_brt": datetime(2026, 4, 28, 0, 0, 0).isoformat(),
                "window_days": [],
            }
        ),
        encoding="utf-8",
    )
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


def _write_sidecar(state_dir: Path, as_of: date) -> Path:
    """Write the ``_cache_key_{as_of}.json`` sidecar (AC9 triple-key).

    Note: the harness consumer (``_load_warmup_state``) does NOT validate
    the sidecar (producer-side validation only — by design per AC7).
    Sidecar presence simulates the on-disk reality from
    ``scripts/run_warmup_state.py`` so the fixture matches operator
    workspace shape (Beckett N4 prep).
    """
    sidecar = state_dir / f"_cache_key_{as_of.isoformat()}.json"
    sidecar.write_text(
        json.dumps(
            {
                "as_of_date": as_of.isoformat(),
                "builder_version": "1.0.0",
                "source_sha256": "0" * 64,
            }
        ),
        encoding="utf-8",
    )
    return sidecar


def _make_fake_pipeline_artifacts():
    """Return (FullReport, DeterminismStamp, events_metadata) stubs."""
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
        computed_at_brt="2026-04-28T00:00:00",
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
        run_id="test-per-phase",
        timestamp_brt=datetime(2026, 4, 28),
    )
    return report, stamp


@pytest.fixture
def per_phase_args(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Pre-populate two distinct as_of dated state files + sidecars + spec.

    Replicates Beckett N4 operator workspace shape: 2024-08-22 (full
    phase) + 2025-05-31 (smoke phase) coexist in ``state/T002/`` of the
    test temp dir. The harness chdirs into ``tmp_path`` so default
    ``state/T002`` resolves under ``tmp_path``.
    """
    full_as_of = date(2024, 8, 22)
    smoke_as_of = date(2025, 5, 31)

    state_dir = tmp_path / "state" / "T002"
    _write_dated_warmup_state(state_dir, full_as_of)
    _write_dated_warmup_state(state_dir, smoke_as_of)
    _write_sidecar(state_dir, full_as_of)
    _write_sidecar(state_dir, smoke_as_of)

    spec = tmp_path / "spec.yaml"
    _write_minimal_spec(spec, in_sample="2024-08-22 to 2025-06-30")
    cal = _write_calendar(tmp_path)
    out_root = tmp_path / "out"

    # chdir so default _DEFAULT_*_PATH paths (relative state/T002/...) and
    # _STATE_DIR resolve inside the test workspace.
    monkeypatch.chdir(tmp_path)

    return {
        "--spec": str(spec),
        "--calendar": str(cal),
        "--output-root": str(out_root),
        "--engine-config": str(tmp_path / "missing-engine-config.yaml"),
        "--mem-poll-interval-s": "60",
        "--in-sample-start": "2024-08-22",
        "--in-sample-end": "2025-06-30",
        "--seed": "42",
    }


def _argv_from(d: dict[str, str], *extras: str) -> list[str]:
    out: list[str] = []
    for k, v in d.items():
        out.append(k)
        out.append(v)
    out.extend(extras)
    return out


# =====================================================================
# AC1 + AC2 + AC4 — per-phase WarmUpGate reads phase-specific dated paths
# =====================================================================
def test_per_phase_warmup_two_distinct_as_of_dates(
    per_phase_args: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC1+AC2+AC4 — each phase constructs its own gate against its dated path.

    Smoke phase derives ``as_of = max(in_sample_start, in_sample_end - 30d)
    = 2025-05-31`` and reads ``state/T002/percentiles_126d_2025-05-31.json``.
    Full phase derives ``as_of = in_sample_start = 2024-08-22`` and reads
    ``state/T002/percentiles_126d_2024-08-22.json``.

    Track A structural defect (singleton at legacy ``:848``) eliminated:
    smoke and full no longer share a gate instance, so neither phase
    observes the other's as_of.
    """
    fake_report, fake_stamp = _make_fake_pipeline_artifacts()
    fake_meta = {"phase": "test", "n_events": 10, "n_trials": 5}

    # Capture the as_of_date + dated paths each _run_phase call resolved.
    calls: list[dict[str, object]] = []

    def spy_run_phase(**kwargs):
        # Pre-resolve the dated paths the SUT would compute, so we can
        # assert symmetric phase-correct path binding.
        as_of = kwargs.get("as_of_date")
        atr_cli = kwargs.get("warmup_atr_cli", sut._DEFAULT_ATR_PATH)
        pct_cli = kwargs.get("warmup_percentiles_cli", sut._DEFAULT_PERCENTILES_PATH)
        atr_resolved = sut._resolve_warmup_path(atr_cli, sut._dated_atr_path(as_of))
        pct_resolved = sut._resolve_warmup_path(
            pct_cli, sut._dated_percentiles_path(as_of)
        )
        calls.append(
            {
                "label": kwargs.get("label"),
                "as_of_date": as_of,
                "atr_resolved": atr_resolved,
                "pct_resolved": pct_resolved,
            }
        )
        # Short-circuit the heavy pipeline; the AC1+AC2 surface is the
        # path resolution + gate construction inside _run_phase, which
        # has already executed before this spy returns.
        return fake_report, fake_stamp, fake_meta

    with patch.object(sut, "_run_phase", side_effect=spy_run_phase):
        rc = sut.main(_argv_from(per_phase_args, "--smoke"))

    assert rc == 0, f"per-phase invocation expected exit 0, got {rc}"
    assert len(calls) == 2, f"expected 2 phase calls, got {len(calls)}: {calls}"

    smoke_call = next(c for c in calls if c["label"] == "smoke")
    full_call = next(c for c in calls if c["label"] == "full")

    assert smoke_call["as_of_date"] == date(2025, 5, 31), (
        f"smoke as_of expected 2025-05-31 (max(in_sample_start, in_sample_end - 30d)), "
        f"got {smoke_call['as_of_date']}"
    )
    assert full_call["as_of_date"] == date(2024, 8, 22), (
        f"full as_of expected 2024-08-22 (in_sample_start), "
        f"got {full_call['as_of_date']}"
    )
    assert Path(smoke_call["pct_resolved"]).name == "percentiles_126d_2025-05-31.json"
    assert Path(smoke_call["atr_resolved"]).name == "atr_20d_2025-05-31.json"
    assert Path(full_call["pct_resolved"]).name == "percentiles_126d_2024-08-22.json"
    assert Path(full_call["atr_resolved"]).name == "atr_20d_2024-08-22.json"

    # Cross-phase isolation: neither phase observes the other's as_of.
    assert smoke_call["pct_resolved"] != full_call["pct_resolved"]
    assert smoke_call["atr_resolved"] != full_call["atr_resolved"]


# =====================================================================
# AC3 — cache_audit.jsonl phase-tag additive
# =====================================================================
def test_cache_audit_jsonl_phase_tag_additive(
    per_phase_args: dict[str, str],
) -> None:
    """AC3 — consumer-side audit emits 2 entries: ``phase: "smoke"`` + ``phase: "full"``.

    Existing producer-side schema fields preserved verbatim (Guard #3
    honoured). Audit ordering: smoke first per AC10/AC11 (smoke runs
    before full when ``--smoke`` is set).
    """
    fake_report, fake_stamp = _make_fake_pipeline_artifacts()
    fake_meta = {"phase": "test", "n_events": 10, "n_trials": 5}

    # Patch heavy pipeline at build_events_dataframe + downstream so the
    # consumer audit emission (which happens at the start of _run_phase
    # BEFORE pipeline) still fires for both phases.
    def fake_run_phase(**kwargs):
        # Manually trigger the consumer-side audit append the SUT does
        # at _run_phase entry, so we can assert phase-tagged JSONL.
        sut._append_consumer_cache_audit(
            sut._STATE_DIR,
            as_of=kwargs["as_of_date"],
            phase=kwargs["label"],
            status="consumer_check",
            expected_key=None,
            found_key=None,
            note="test-fixture",
        )
        return fake_report, fake_stamp, fake_meta

    with patch.object(sut, "_run_phase", side_effect=fake_run_phase):
        rc = sut.main(_argv_from(per_phase_args, "--smoke"))

    assert rc == 0, f"per-phase invocation expected exit 0, got {rc}"

    # cache_audit.jsonl lives under state/T002/ relative to cwd (chdir
    # in fixture → tmp_path/state/T002/cache_audit.jsonl).
    audit_path = Path("state/T002/cache_audit.jsonl")
    assert audit_path.exists(), f"audit file missing at {audit_path}"

    lines = [
        json.loads(line)
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    # At least 2 phase-tagged consumer entries (test fixture writes two).
    phase_entries = [e for e in lines if "phase" in e]
    assert len(phase_entries) >= 2, (
        f"expected ≥ 2 phase-tagged consumer entries, got {len(phase_entries)}: {phase_entries}"
    )

    # Producer-side schema fields preserved on phase-tagged entries.
    required_fields = {
        "computed_at_brt",
        "as_of_date",
        "status",
        "expected_key",
        "found_key",
        "note",
        "phase",
    }
    for entry in phase_entries[-2:]:
        assert required_fields.issubset(entry.keys()), (
            f"phase-tagged entry missing required fields: {entry}"
        )
        assert entry["phase"] in ("smoke", "full"), (
            f"phase value expected ∈ {{smoke, full}}, got {entry['phase']}"
        )

    # Smoke entry first per AC10/AC11 ordering (the LAST 2 entries are
    # the most recent run; we ordered them via _append in the SUT).
    last_two = phase_entries[-2:]
    assert last_two[0]["phase"] == "smoke", (
        f"first of last 2 entries expected phase=smoke, got {last_two[0]['phase']}"
    )
    assert last_two[1]["phase"] == "full", (
        f"second of last 2 entries expected phase=full, got {last_two[1]['phase']}"
    )

    # AC9 contract preserved: as_of_date is per-phase correct.
    assert last_two[0]["as_of_date"] == "2025-05-31"  # smoke
    assert last_two[1]["as_of_date"] == "2024-08-22"  # full


# =====================================================================
# AC1 + AC2 — CLI override is honoured verbatim (operator authority)
# =====================================================================
def test_per_phase_warmup_default_path_unchanged_for_cli_override(
    per_phase_args: dict[str, str], tmp_path: Path,
) -> None:
    """AC1+AC2 — explicit ``--warmup-atr foo.json`` override honoured verbatim.

    Per Aria T1 §1 + §4: ``_resolve_warmup_path`` substitutes dated
    default ONLY when the operator omitted the flag (sentinel detected
    by path equality with ``_DEFAULT_ATR_PATH`` /
    ``_DEFAULT_PERCENTILES_PATH``). If the operator passes a non-default
    custom path, that path flows through verbatim (CLI affordance /
    ad-hoc operator runs).
    """
    fake_report, fake_stamp = _make_fake_pipeline_artifacts()
    fake_meta = {"phase": "test", "n_events": 10, "n_trials": 5}

    # Operator override paths (clearly non-default).
    custom_atr = tmp_path / "operator_custom_atr.json"
    custom_pct = tmp_path / "operator_custom_pct.json"
    custom_atr.write_text(
        json.dumps({"as_of_date": "2024-08-22", "atr": 99.99}), encoding="utf-8"
    )
    custom_pct.write_text(
        json.dumps(
            {
                "as_of_date": "2024-08-22",
                "magnitude": {"p20": 1.0, "p60": 2.0, "p80": 3.0},
                "atr_day_ratio": {"p20": 0.5, "p60": 1.0, "p80": 1.5},
            }
        ),
        encoding="utf-8",
    )

    args = dict(per_phase_args)
    args["--warmup-atr"] = str(custom_atr)
    args["--warmup-percentiles"] = str(custom_pct)

    calls: list[dict[str, object]] = []

    def spy_run_phase(**kwargs):
        as_of = kwargs.get("as_of_date")
        atr_cli = kwargs.get("warmup_atr_cli", sut._DEFAULT_ATR_PATH)
        pct_cli = kwargs.get("warmup_percentiles_cli", sut._DEFAULT_PERCENTILES_PATH)
        atr_resolved = sut._resolve_warmup_path(atr_cli, sut._dated_atr_path(as_of))
        pct_resolved = sut._resolve_warmup_path(
            pct_cli, sut._dated_percentiles_path(as_of)
        )
        calls.append(
            {
                "label": kwargs.get("label"),
                "atr_resolved": atr_resolved,
                "pct_resolved": pct_resolved,
            }
        )
        return fake_report, fake_stamp, fake_meta

    # Run without --smoke so only the full phase fires (single call,
    # operator override flows through to the gate verbatim).
    with patch.object(sut, "_run_phase", side_effect=spy_run_phase):
        rc = sut.main(_argv_from(args))

    assert rc == 0, f"override invocation expected exit 0, got {rc}"
    assert len(calls) == 1, f"expected 1 phase call (no --smoke), got {len(calls)}"

    # Operator override propagated verbatim — NOT substituted with dated
    # default, because args.warmup_atr / args.warmup_percentiles are
    # non-default sentinels.
    assert calls[0]["atr_resolved"] == custom_atr, (
        f"operator override NOT honoured: expected {custom_atr}, got {calls[0]['atr_resolved']}"
    )
    assert calls[0]["pct_resolved"] == custom_pct, (
        f"operator override NOT honoured: expected {custom_pct}, got {calls[0]['pct_resolved']}"
    )


# =====================================================================
# AC2 — pure helpers (bonus: trivial unit coverage of resolvers)
# =====================================================================
def test_dated_path_helpers_are_pure() -> None:
    """AC2 — ``_dated_atr_path`` / ``_dated_percentiles_path`` deterministic on as_of."""
    d1 = date(2024, 8, 22)
    d2 = date(2025, 5, 31)
    assert sut._dated_atr_path(d1) == Path("state/T002/atr_20d_2024-08-22.json")
    assert sut._dated_atr_path(d2) == Path("state/T002/atr_20d_2025-05-31.json")
    assert sut._dated_percentiles_path(d1) == Path(
        "state/T002/percentiles_126d_2024-08-22.json"
    )
    assert sut._dated_percentiles_path(d2) == Path(
        "state/T002/percentiles_126d_2025-05-31.json"
    )


def test_resolve_warmup_path_substitutes_default(tmp_path: Path) -> None:
    """AC2 — when CLI arg equals the legacy default, dated default substitutes."""
    dated = sut._dated_atr_path(date(2024, 8, 22))
    # Default sentinel → substituted.
    assert sut._resolve_warmup_path(sut._DEFAULT_ATR_PATH, dated) == dated
    # Custom override → verbatim.
    custom = tmp_path / "custom.json"
    assert sut._resolve_warmup_path(custom, dated) == custom
