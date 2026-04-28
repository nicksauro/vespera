"""T5 — tests for ``scripts/run_warmup_state.py`` CLI (Story T002.0g AC11).

Coverage:
- argparse required ``--as-of-dates`` (exit 2)
- ``--seed`` propagation
- hold-out lock guard fires (exit 1) for window inside [2025-07-01, 2026-04-21]
- telemetry CSV columns superset (REUSE pattern from cpcv_dry_run T8)
- 6 GiB soft halt mock (psutil patched ⇒ halt_event fires; no kill)
- 2025-05-31 smoke completes with mocked orchestrator (exit 0)
- ``VESPERA_UNLOCK_HOLDOUT`` grep contract (DoD)

T002.0h AC9 — Cache validation contract (mini-council 4/4 APPROVE_F):
- ``test_cache_hit_skips_orchestrator`` — pre-create valid sidecar +
  outputs; orchestrator NOT invoked; exit 0.
- ``test_cache_miss_invokes_orchestrator`` — empty output dir; orchestrator
  runs and writes sidecar.
- ``test_cache_stale_fail_closed`` — sidecar with wrong source_sha ⇒
  StaleCacheError, exit 1.
- ``test_force_rebuild_bypasses_cache`` — ``--force-rebuild`` invokes
  orchestrator even with valid cache.
- ``test_cache_audit_jsonl_appends`` — cache_audit.jsonl gets one entry
  per call.
"""

from __future__ import annotations

import csv
import sys
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure scripts/ + repo importable.
_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import run_warmup_state as sut  # noqa: E402


# =====================================================================
# Fixtures
# =====================================================================
def _write_calendar(tmp_path: Path) -> Path:
    """Permissive calendar — every weekday valid."""
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


@pytest.fixture
def base_args(tmp_path: Path) -> dict[str, str]:
    cal = _write_calendar(tmp_path)
    out_dir = tmp_path / "state_T002"
    return {
        "--as-of-dates": "2025-05-31",
        "--source": "parquet",
        "--output-dir": str(out_dir),
        "--calendar": str(cal),
        "--seed": "42",
        "--mem-poll-interval-s": "60",
    }


def _argv_from(d: dict[str, str], *extras: str) -> list[str]:
    out: list[str] = []
    for k, v in d.items():
        out.append(k)
        out.append(v)
    out.extend(extras)
    return out


# =====================================================================
# AC11 — argparse contract
# =====================================================================
def test_argparse_required_as_of_dates_exit_2():
    """Per AC11 — missing --as-of-dates raises SystemExit(2)."""
    parser = sut.build_arg_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code == 2


def test_argparse_seed_propagated():
    """Per AC11 — --seed default 42; override propagates."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--as-of-dates", "2025-05-31"])
    assert a.seed == sut.DEFAULT_SEED == 42
    a2 = parser.parse_args(["--as-of-dates", "2025-05-31", "--seed", "99"])
    assert a2.seed == 99


def test_argparse_as_of_dates_list_parsed():
    """Per AC11 — comma-separated list parses to list[date]."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--as-of-dates", "2025-05-31,2024-06-30"])
    assert a.as_of_dates == [date(2025, 5, 31), date(2024, 6, 30)]


def test_argparse_invalid_iso_rejected():
    """Per AC11 — bad ISO date → argparse error."""
    parser = sut.build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--as-of-dates", "07/15/2024"])


def test_argparse_default_output_dir():
    """Per AC11 — default output dir = state/T002/."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--as-of-dates", "2025-05-31"])
    assert a.output_dir == Path("state/T002")


# =====================================================================
# Hold-out lock guard (AC3 defense-in-depth + DoD grep)
# =====================================================================
def test_holdout_lock_guard_fires(base_args, tmp_path, monkeypatch):
    """Per AC3 — as_of=2025-08-15 (inside hold-out) ⇒ exit 1, no orchestrator call."""
    base_args["--as-of-dates"] = "2025-08-15"
    monkeypatch.delenv("VESPERA_UNLOCK_HOLDOUT", raising=False)
    # We need to stub orchestrate_warmup_state so we know the guard fired
    # BEFORE the orchestrator (the guard runs at CLI top, even before
    # the orchestrator's own internal holdout check).
    with patch.object(sut, "orchestrate_warmup_state") as mock_orch:
        rc = sut.main(_argv_from(base_args))
    assert rc == 1
    mock_orch.assert_not_called()


def test_holdout_unlock_env_grep_contract():
    """DoD — VESPERA_UNLOCK_HOLDOUT literal must appear in run_warmup_state.py."""
    src = (_SCRIPTS / "run_warmup_state.py").read_text(encoding="utf-8")
    # >= 1 match required by DoD §"Hold-out intocado".
    assert src.count("VESPERA_UNLOCK_HOLDOUT") >= 1


# =====================================================================
# Telemetry CSV columns + 6 GiB soft halt mock (REUSE pattern)
# =====================================================================
def test_telemetry_csv_columns(tmp_path: Path):
    """AC10 — telemetry CSV header = TELEMETRY_COLUMNS superset."""
    csv_path = tmp_path / "tele.csv"
    poller = sut.MemoryPoller(
        csv_path,
        soft_cap_bytes=10 * 1024**3,
        poll_interval_s=60.0,
        enabled=True,
    )
    # Required cols.
    for col in (
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
    ):
        assert col in sut.TELEMETRY_COLUMNS
    with csv_path.open("r", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert tuple(header) == sut.TELEMETRY_COLUMNS
    poller.stop()


def test_6gb_soft_halt_mock(tmp_path: Path):
    """AC10 — psutil patched to 7 GiB ⇒ halt_event fires + soft-halt note."""
    csv_path = tmp_path / "tele.csv"
    poller = sut.MemoryPoller(
        csv_path,
        soft_cap_bytes=6 * 1024**3,
        poll_interval_s=60.0,
        enabled=True,
    )

    class _FakeMem:
        rss = 7 * 1024**3
        vms = 8 * 1024**3

    class _FakeProc:
        def memory_info(self):
            return _FakeMem()

        def cpu_percent(self, interval=None):  # noqa: ARG002
            return 5.0

    with patch.object(sut.psutil, "Process", return_value=_FakeProc()):
        poller._write_row(phase="test_halt", note="forced")

    assert poller.halt_event.is_set()
    with csv_path.open("r", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    note_idx = sut.TELEMETRY_COLUMNS.index("note")
    assert "SOFT_HALT_FIRED" in rows[-1][note_idx]
    poller.stop()


# =====================================================================
# 2025-05-31 smoke (mocked orchestrator)
# =====================================================================
def test_2025_05_31_smoke_completes(base_args, tmp_path):
    """AC11 + AC5 amendment — invoke CLI for 2025-05-31; orchestrator mocked."""
    from packages.t002_eod_unwind.warmup.orchestrator import (
        OrchestratorResult,
        TradeFilterDecision,
    )

    out_dir = Path(base_args["--output-dir"])
    fake_atr = out_dir / "atr_20d_2025-05-31.json"
    fake_pct = out_dir / "percentiles_126d_2025-05-31.json"
    fake_result = OrchestratorResult(
        atr_paths=[fake_atr],
        percentiles_paths=[fake_pct],
        latest_atr_path=out_dir / "atr_20d.json",
        latest_percentiles_path=out_dir / "percentiles_126d.json",
        manifest_path=out_dir / "manifest.json",
        determinism_stamp_path=out_dir / "determinism_stamp.json",
        tradetype_decision=TradeFilterDecision(
            status="escalated_adapter_gap",
            note="[USER-ESCALATION-PENDING] T002.0b adapter discards tradeType",
        ),
    )

    with patch.object(sut, "orchestrate_warmup_state", return_value=fake_result):
        rc = sut.main(_argv_from(base_args))
    assert rc == 0


def test_argparse_parquet_only_choices():
    """AC11 + Phase F deferral — only ``parquet`` source accepted today."""
    parser = sut.build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--as-of-dates", "2025-05-31", "--source", "timescaledb"])


# =====================================================================
# Insufficient coverage propagation (Guard #1)
# =====================================================================
def test_insufficient_coverage_returns_exit_1(base_args, tmp_path):
    """Guard #1 — InsufficientCoverage from orchestrator ⇒ exit 1."""
    from packages.t002_eod_unwind.warmup.orchestrator import InsufficientCoverage

    with patch.object(
        sut,
        "orchestrate_warmup_state",
        side_effect=InsufficientCoverage("not enough trades"),
    ):
        rc = sut.main(_argv_from(base_args))
    assert rc == 1


# =====================================================================
# T002.0h AC9 — Cache validation contract (mini-council 4/4 APPROVE_F)
# =====================================================================
import json  # noqa: E402  Local import — keeps the AC9 test block self-contained.

from packages.t002_eod_unwind.warmup import BUILDER_VERSION  # noqa: E402
from packages.t002_eod_unwind.warmup.orchestrator import (  # noqa: E402
    OrchestratorResult,
    TradeFilterDecision,
)


def _write_empty_manifest(tmp_path: Path) -> Path:
    """Write a minimal empty-row manifest CSV.

    The empty match path inside ``_compute_source_sha256_for_window``
    produces a deterministic marker hash — perfect for tests that don't
    need real parquet rows.
    """
    csv_path = tmp_path / "manifest_test.csv"
    csv_path.write_text(
        "path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt\n",
        encoding="utf-8",
    )
    return csv_path


def _seed_orchestrator_outputs(out_dir: Path, as_of: date) -> tuple[Path, Path]:
    """Pre-create the orchestrator's dated JSON outputs (cache HIT prereq)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    atr = out_dir / f"atr_20d_{as_of.isoformat()}.json"
    pct = out_dir / f"percentiles_126d_{as_of.isoformat()}.json"
    atr.write_text('{"atr":42.0}', encoding="utf-8")
    pct.write_text('{"bands":{}}', encoding="utf-8")
    return atr, pct


def _ac9_args(tmp_path: Path) -> dict[str, str]:
    """Argparse dict tailored for AC9 cache tests (with manifest CSV)."""
    cal = _write_calendar(tmp_path)
    out_dir = tmp_path / "state_T002"
    manifest = _write_empty_manifest(tmp_path)
    return {
        "--as-of-dates": "2025-05-31",
        "--source": "parquet",
        "--output-dir": str(out_dir),
        "--calendar": str(cal),
        "--seed": "42",
        "--mem-poll-interval-s": "60",
        "--manifest-csv": str(manifest),
    }


def test_cache_hit_skips_orchestrator(tmp_path: Path):
    """AC9 — pre-seeded sidecar + outputs ⇒ orchestrator NOT invoked, exit 0."""
    args = _ac9_args(tmp_path)
    out_dir = Path(args["--output-dir"])
    as_of = date(2025, 5, 31)

    # Seed outputs.
    _seed_orchestrator_outputs(out_dir, as_of)

    # Compute the canonical expected key for this manifest+as_of and
    # write the sidecar so the cache check returns HIT.
    source_sha = sut._compute_source_sha256_for_window(
        Path(args["--manifest-csv"]), as_of, ticker="WDO"
    )
    expected_key = sut.compute_triple_key(
        as_of=as_of, source_sha256=source_sha, builder_version=BUILDER_VERSION
    )
    sut._write_cache_sidecar(out_dir, as_of, expected_key)

    with patch.object(sut, "orchestrate_warmup_state") as mock_orch:
        rc = sut.main(_argv_from(args))

    assert rc == 0
    mock_orch.assert_not_called()


def test_cache_miss_invokes_orchestrator(tmp_path: Path):
    """AC9 — empty output dir ⇒ orchestrator invoked, sidecar written."""
    args = _ac9_args(tmp_path)
    out_dir = Path(args["--output-dir"])
    as_of = date(2025, 5, 31)

    # Mock orchestrator to "materialize" the dated outputs so the post-
    # orchestrator sidecar write proceeds (sidecar write does not gate
    # on output presence — it only requires the output_dir to be
    # writable).
    def _fake_orch(**kwargs):  # noqa: ANN001, ANN003
        # Mimic orchestrator: persist the dated JSONs.
        _seed_orchestrator_outputs(out_dir, as_of)
        return OrchestratorResult(
            atr_paths=[out_dir / f"atr_20d_{as_of.isoformat()}.json"],
            percentiles_paths=[out_dir / f"percentiles_126d_{as_of.isoformat()}.json"],
            latest_atr_path=out_dir / "atr_20d.json",
            latest_percentiles_path=out_dir / "percentiles_126d.json",
            manifest_path=out_dir / "manifest.json",
            determinism_stamp_path=out_dir / "determinism_stamp.json",
            tradetype_decision=TradeFilterDecision(
                status="applied", note="test"
            ),
        )

    with patch.object(sut, "orchestrate_warmup_state", side_effect=_fake_orch) as mock_orch:
        rc = sut.main(_argv_from(args))

    assert rc == 0
    mock_orch.assert_called_once()
    sidecar = sut._sidecar_path(out_dir, as_of)
    assert sidecar.exists(), "post-orchestrator sidecar must be persisted"
    persisted = json.loads(sidecar.read_text(encoding="utf-8"))
    assert persisted["builder_version"] == BUILDER_VERSION
    assert persisted["as_of_date"] == as_of.isoformat()


def test_cache_stale_fail_closed(tmp_path: Path):
    """AC9 — sidecar with wrong source_sha ⇒ exit 1, orchestrator NOT invoked.

    Per ESC-006 mini-council 4/4 fail-closed contract: NO silent
    regenerate; operator must --force-rebuild to acknowledge the drift.
    """
    args = _ac9_args(tmp_path)
    out_dir = Path(args["--output-dir"])
    as_of = date(2025, 5, 31)

    _seed_orchestrator_outputs(out_dir, as_of)

    # Write a sidecar with a deliberately mismatched source_sha256 so
    # the cache check returns STALE and fails closed.
    stale_key = sut.compute_triple_key(
        as_of=as_of,
        source_sha256="0" * 64,  # not the manifest-derived value
        builder_version=BUILDER_VERSION,
    )
    sut._write_cache_sidecar(out_dir, as_of, stale_key)

    with patch.object(sut, "orchestrate_warmup_state") as mock_orch:
        rc = sut.main(_argv_from(args))

    assert rc == 1, "stale cache must fail-closed (exit 1)"
    mock_orch.assert_not_called()


def test_force_rebuild_bypasses_cache(tmp_path: Path):
    """AC9 — --force-rebuild forces orchestrator even with valid cache."""
    args = _ac9_args(tmp_path)
    out_dir = Path(args["--output-dir"])
    as_of = date(2025, 5, 31)

    _seed_orchestrator_outputs(out_dir, as_of)
    source_sha = sut._compute_source_sha256_for_window(
        Path(args["--manifest-csv"]), as_of, ticker="WDO"
    )
    valid_key = sut.compute_triple_key(
        as_of=as_of, source_sha256=source_sha, builder_version=BUILDER_VERSION
    )
    sut._write_cache_sidecar(out_dir, as_of, valid_key)

    def _fake_orch(**kwargs):  # noqa: ANN001, ANN003
        _seed_orchestrator_outputs(out_dir, as_of)
        return OrchestratorResult(
            atr_paths=[out_dir / f"atr_20d_{as_of.isoformat()}.json"],
            percentiles_paths=[out_dir / f"percentiles_126d_{as_of.isoformat()}.json"],
            latest_atr_path=out_dir / "atr_20d.json",
            latest_percentiles_path=out_dir / "percentiles_126d.json",
            manifest_path=out_dir / "manifest.json",
            determinism_stamp_path=out_dir / "determinism_stamp.json",
            tradetype_decision=TradeFilterDecision(status="applied", note="test"),
        )

    with patch.object(sut, "orchestrate_warmup_state", side_effect=_fake_orch) as mock_orch:
        rc = sut.main(_argv_from(args) + ["--force-rebuild"])

    assert rc == 0
    mock_orch.assert_called_once(), "--force-rebuild MUST invoke orchestrator"


def test_cache_audit_jsonl_appends(tmp_path: Path):
    """AC9 — cache_audit.jsonl appends entries on cache decisions.

    Two-call sequence: first run is a miss (queues + writes sidecar →
    2 audit entries: ``miss`` then ``write``), second run is a hit
    (1 entry: ``hit``). Total ≥ 3 entries; explicit assert on each.
    """
    args = _ac9_args(tmp_path)
    out_dir = Path(args["--output-dir"])
    as_of = date(2025, 5, 31)

    def _fake_orch(**kwargs):  # noqa: ANN001, ANN003
        _seed_orchestrator_outputs(out_dir, as_of)
        return OrchestratorResult(
            atr_paths=[out_dir / f"atr_20d_{as_of.isoformat()}.json"],
            percentiles_paths=[out_dir / f"percentiles_126d_{as_of.isoformat()}.json"],
            latest_atr_path=out_dir / "atr_20d.json",
            latest_percentiles_path=out_dir / "percentiles_126d.json",
            manifest_path=out_dir / "manifest.json",
            determinism_stamp_path=out_dir / "determinism_stamp.json",
            tradetype_decision=TradeFilterDecision(status="applied", note="test"),
        )

    # First run — cache miss path (queue + write).
    with patch.object(sut, "orchestrate_warmup_state", side_effect=_fake_orch):
        rc1 = sut.main(_argv_from(args))
    assert rc1 == 0

    # Second run — cache hit path (no orchestrator invocation).
    with patch.object(sut, "orchestrate_warmup_state") as mock_orch:
        rc2 = sut.main(_argv_from(args))
    assert rc2 == 0
    mock_orch.assert_not_called()

    audit_path = out_dir / sut.CACHE_AUDIT_FILENAME
    assert audit_path.exists(), "cache_audit.jsonl must be created"
    lines = [
        line for line in audit_path.read_text(encoding="utf-8").splitlines() if line
    ]
    statuses = [json.loads(line)["status"] for line in lines]
    # Expected sequence: miss (run1 pre-orch) → write (run1 post-orch) →
    # hit (run2 pre-orch). Exact length asserts no extra spurious appends.
    assert statuses == ["miss", "write", "hit"], (
        f"unexpected audit sequence: {statuses}"
    )


def test_argparse_force_rebuild_default_false():
    """AC9 — --force-rebuild defaults to False; flag flips to True."""
    parser = sut.build_arg_parser()
    a = parser.parse_args(["--as-of-dates", "2025-05-31"])
    assert a.force_rebuild is False
    a2 = parser.parse_args(["--as-of-dates", "2025-05-31", "--force-rebuild"])
    assert a2.force_rebuild is True


def test_compute_triple_key_deterministic():
    """AC9 — compute_triple_key produces identical dict for identical inputs."""
    k1 = sut.compute_triple_key(
        as_of=date(2025, 5, 31), source_sha256="abc", builder_version="1.0.0"
    )
    k2 = sut.compute_triple_key(
        as_of=date(2025, 5, 31), source_sha256="abc", builder_version="1.0.0"
    )
    assert k1 == k2 == {
        "as_of_date": "2025-05-31",
        "source_sha256": "abc",
        "builder_version": "1.0.0",
    }


def test_source_sha_changes_with_manifest(tmp_path: Path):
    """AC9 — modifying the manifest CSV changes the computed source_sha."""
    cal_dir = tmp_path
    csv_path = cal_dir / "manifest.csv"
    csv_path.write_text(
        "path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt\n"
        "data/p1.parquet,100,aaa,2025-04-01T09:00:00,2025-04-30T18:00:00,WDO,warmup,2026-01-01T00:00:00\n",
        encoding="utf-8",
    )
    sha1 = sut._compute_source_sha256_for_window(
        csv_path, date(2025, 5, 31), ticker="WDO"
    )
    csv_path.write_text(
        "path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt\n"
        "data/p1.parquet,100,bbb,2025-04-01T09:00:00,2025-04-30T18:00:00,WDO,warmup,2026-01-01T00:00:00\n",
        encoding="utf-8",
    )
    sha2 = sut._compute_source_sha256_for_window(
        csv_path, date(2025, 5, 31), ticker="WDO"
    )
    assert sha1 != sha2, "source_sha MUST change when manifest sha changes"


def test_manifest_missing_fails_closed(tmp_path: Path):
    """AC9 — missing manifest CSV ⇒ exit 1 (Anti-Article-IV Guard #1)."""
    args = _ac9_args(tmp_path)
    args["--manifest-csv"] = str(tmp_path / "does_not_exist.csv")
    with patch.object(sut, "orchestrate_warmup_state") as mock_orch:
        rc = sut.main(_argv_from(args))
    assert rc == 1
    mock_orch.assert_not_called()
