"""Unit tests — manifest write-mode flags and custodial guard.

Story: T002.0a (G09a Blocker 2)
Spec:  docs/architecture/manifest-write-flag-spec.md  (MWF-20260422-1, Riven)

All 16 test cases named and asserted per spec §5. Hard rule per spec §5:
NO test may read, write, or stat the real data/manifest.csv. Every test that
exercises the guard monkeypatches ``mp.MANIFEST_PATH`` to a tmp_path.
"""

from __future__ import annotations

import hashlib
import sys
from datetime import date
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import materialize_parquet as mp  # noqa: E402


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

# MWF-20260422-1 §5 — Dex may NOT touch the real data/manifest.csv during
# tests. Every fixture/test that mentions MANIFEST_PATH monkeypatches it.


def _base_parse_args_argv(*extra: str) -> list[str]:
    """Minimum argv suffix to satisfy required --start/--end/--ticker.

    Tests exercising only the new flags need a full parse; this returns a
    valid base so argparse errors relate only to the flags under test.
    """
    return [
        "--start-date", "2024-01-02",
        "--end-date", "2024-01-03",
        "--ticker", "WDO",
        *extra,
    ]


def _patch_canonical_to_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Redirect ``MANIFEST_PATH`` to a tmp-path stand-in for guard tests."""
    fake_canonical = tmp_path / "manifest.csv"
    monkeypatch.setattr(mp, "MANIFEST_PATH", fake_canonical)
    return fake_canonical


# ---------------------------------------------------------------------------
# 1. test_parse_args_no_manifest_flag
# ---------------------------------------------------------------------------

def test_parse_args_no_manifest_flag():
    """--no-manifest sets no_manifest=True and leaves manifest_path=None."""
    args = mp.parse_args(_base_parse_args_argv("--no-manifest"))
    assert args.no_manifest is True
    assert args.manifest_path is None


# ---------------------------------------------------------------------------
# 2. test_parse_args_manifest_path_flag
# ---------------------------------------------------------------------------

def test_parse_args_manifest_path_flag(tmp_path: Path):
    """--manifest-path PATH sets manifest_path and leaves no_manifest=False."""
    scratch = tmp_path / "scratch_manifest.csv"
    args = mp.parse_args(_base_parse_args_argv("--manifest-path", str(scratch)))
    assert args.no_manifest is False
    assert args.manifest_path == Path(str(scratch))


# ---------------------------------------------------------------------------
# 3. test_parse_args_flags_mutually_exclusive
# ---------------------------------------------------------------------------

def test_parse_args_flags_mutually_exclusive(tmp_path: Path):
    """Passing BOTH --no-manifest and --manifest-path raises SystemExit."""
    scratch = tmp_path / "scratch_manifest.csv"
    with pytest.raises(SystemExit):
        mp.parse_args(_base_parse_args_argv(
            "--no-manifest", "--manifest-path", str(scratch),
        ))


# ---------------------------------------------------------------------------
# 4. test_parse_args_rejects_manifest_path_equal_to_canonical
# ---------------------------------------------------------------------------

def test_parse_args_rejects_manifest_path_equal_to_canonical(capsys):
    """--manifest-path pointing at canonical exits with helpful message."""
    canonical = str(mp.MANIFEST_PATH)
    with pytest.raises(SystemExit):
        mp.parse_args(_base_parse_args_argv("--manifest-path", canonical))
    err = capsys.readouterr().err
    assert "manifest-path" in err
    assert "canonical" in err


# ---------------------------------------------------------------------------
# 5. test_resolve_manifest_target_no_manifest_returns_none
# ---------------------------------------------------------------------------

def test_resolve_manifest_target_no_manifest_returns_none():
    """--no-manifest => _resolve_manifest_target returns None."""
    args = mp.Args(
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
        ticker="WDO",
        output_dir=Path("data/in_sample"),
        dry_run=False,
        no_manifest=True,
        manifest_path=None,
    )
    assert mp._resolve_manifest_target(args) is None


# ---------------------------------------------------------------------------
# 6. test_resolve_manifest_target_scratch_returns_given_path
# ---------------------------------------------------------------------------

def test_resolve_manifest_target_scratch_returns_given_path(tmp_path: Path):
    """--manifest-path X => _resolve_manifest_target returns X."""
    scratch = tmp_path / "scratch.csv"
    args = mp.Args(
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
        ticker="WDO",
        output_dir=Path("data/in_sample"),
        dry_run=False,
        no_manifest=False,
        manifest_path=scratch,
    )
    assert mp._resolve_manifest_target(args) == scratch


# ---------------------------------------------------------------------------
# 7. test_resolve_manifest_target_default_returns_canonical
# ---------------------------------------------------------------------------

def test_resolve_manifest_target_default_returns_canonical():
    """Neither flag set => returns MANIFEST_PATH."""
    args = mp.Args(
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
        ticker="WDO",
        output_dir=Path("data/in_sample"),
        dry_run=False,
        no_manifest=False,
        manifest_path=None,
    )
    assert mp._resolve_manifest_target(args) == mp.MANIFEST_PATH


# ---------------------------------------------------------------------------
# 8. test_guard_canonical_blocks_without_cosign
# ---------------------------------------------------------------------------

def test_guard_canonical_blocks_without_cosign(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """Unset VESPERA_MANIFEST_COSIGN => RuntimeError mentioning MC-YYYYMMDD-N."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    monkeypatch.delenv("VESPERA_MANIFEST_COSIGN", raising=False)
    monkeypatch.delenv("VESPERA_MANIFEST_EXPECTED_SHA256", raising=False)
    with pytest.raises(RuntimeError) as exc_info:
        mp._guard_canonical_write(fake)
    assert "MC-YYYYMMDD-N" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 9. test_guard_canonical_blocks_malformed_cosign
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("bad_cosign", ["bogus", "MC-2026", "mc-20260423-1", ""])
def test_guard_canonical_blocks_malformed_cosign(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, bad_cosign: str,
):
    """Malformed cosign values are rejected with RuntimeError."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    monkeypatch.setenv("VESPERA_MANIFEST_COSIGN", bad_cosign)
    monkeypatch.setenv(
        "VESPERA_MANIFEST_EXPECTED_SHA256",
        "0" * 64,
    )
    with pytest.raises(RuntimeError):
        mp._guard_canonical_write(fake)


# ---------------------------------------------------------------------------
# 10. test_guard_canonical_blocks_on_sha_mismatch
# ---------------------------------------------------------------------------

def test_guard_canonical_blocks_on_sha_mismatch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """Cosign OK but EXPECTED_SHA256 != actual sha256 => 'drifted' RuntimeError."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    fake.write_bytes(b"row1\n")
    wrong_sha = "a" * 64  # plausibly-formatted but guaranteed mismatch
    monkeypatch.setenv("VESPERA_MANIFEST_COSIGN", "MC-20260423-1")
    monkeypatch.setenv("VESPERA_MANIFEST_EXPECTED_SHA256", wrong_sha)
    with pytest.raises(RuntimeError) as exc_info:
        mp._guard_canonical_write(fake)
    assert "drifted" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 11. test_guard_canonical_allows_on_sha_match_and_cosign
# ---------------------------------------------------------------------------

def test_guard_canonical_allows_on_sha_match_and_cosign(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """Correct cosign + matching sha256 => guard returns (no raise)."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    payload = b"header\nrow1\nrow2\n"
    fake.write_bytes(payload)
    actual_sha = hashlib.sha256(payload).hexdigest()
    monkeypatch.setenv("VESPERA_MANIFEST_COSIGN", "MC-20260423-1")
    monkeypatch.setenv("VESPERA_MANIFEST_EXPECTED_SHA256", actual_sha)
    # Must not raise.
    mp._guard_canonical_write(fake)


# ---------------------------------------------------------------------------
# 12. test_guard_canonical_bootstrap_create
# ---------------------------------------------------------------------------

def test_guard_canonical_bootstrap_create(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """CREATE sentinel + file absent => guard returns (bootstrap case)."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    assert not fake.exists()
    monkeypatch.setenv("VESPERA_MANIFEST_COSIGN", "MC-20260423-1")
    monkeypatch.setenv("VESPERA_MANIFEST_EXPECTED_SHA256", "CREATE")
    # Must not raise.
    mp._guard_canonical_write(fake)


# ---------------------------------------------------------------------------
# 13. test_guard_canonical_create_rejects_existing_file
# ---------------------------------------------------------------------------

def test_guard_canonical_create_rejects_existing_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """CREATE sentinel but file exists => RuntimeError."""
    fake = _patch_canonical_to_tmp(monkeypatch, tmp_path)
    fake.write_bytes(b"already here\n")
    monkeypatch.setenv("VESPERA_MANIFEST_COSIGN", "MC-20260423-1")
    monkeypatch.setenv("VESPERA_MANIFEST_EXPECTED_SHA256", "CREATE")
    with pytest.raises(RuntimeError) as exc_info:
        mp._guard_canonical_write(fake)
    assert "CREATE" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 14. test_scratch_path_has_no_guard
# ---------------------------------------------------------------------------

def test_scratch_path_has_no_guard(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    """Any non-canonical target bypasses the guard entirely — no env needed."""
    # Keep the real MANIFEST_PATH; our target is explicitly different.
    scratch = tmp_path / "scratch.csv"
    monkeypatch.delenv("VESPERA_MANIFEST_COSIGN", raising=False)
    monkeypatch.delenv("VESPERA_MANIFEST_EXPECTED_SHA256", raising=False)
    # Must not raise despite no env vars set.
    mp._guard_canonical_write(scratch)


# ---------------------------------------------------------------------------
# 15. test_no_manifest_banner_printed_on_launch
# ---------------------------------------------------------------------------

def test_no_manifest_banner_printed_on_launch(capsys):
    """A --no-manifest dry-run prints [manifest-mode] NO-MANIFEST to stderr."""
    rc = mp.run(mp.Args(
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
        ticker="WDO",
        output_dir=Path("data/in_sample"),
        dry_run=True,
        no_manifest=True,
        manifest_path=None,
    ))
    assert rc == 0
    err = capsys.readouterr().err
    assert "[manifest-mode] NO-MANIFEST" in err


# ---------------------------------------------------------------------------
# 16. test_scratch_output_warning_when_canonical_target
# ---------------------------------------------------------------------------

def test_scratch_output_warning_when_canonical_target(capsys):
    """--output-dir under data/baseline-run/ with canonical target -> stderr warn."""
    scratch_out = mp.REPO_ROOT / "data" / "baseline-run" / "scratch"
    rc = mp.run(mp.Args(
        start_date=date(2024, 1, 2),
        end_date=date(2024, 1, 3),
        ticker="WDO",
        output_dir=scratch_out,
        dry_run=True,
        no_manifest=False,
        manifest_path=None,
    ))
    assert rc == 0
    err = capsys.readouterr().err
    assert "[warn] --output-dir points to a scratch location" in err
    assert "CANONICAL path" in err
