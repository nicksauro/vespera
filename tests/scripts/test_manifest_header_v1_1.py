"""AC5 — manifest header v1 -> v1.1 cosmetic upgrade.

Tests:
  (i)   v1 read OK (backward-compat reader)
  (ii)  v1.1 write succeeds atomically
  (iii) round-trip data rows byte-equal pre/post upgrade
  (iv)  refuses to operate on data/manifest.csv (R10 protection)
  (v)   refuses on mismatched header
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts.dll_backfill_projection import (
    read_manifest_rows,
    upgrade_manifest_header,
)


_V1_HEADER = "# backfill-manifest v1 - NOT R10 custodial"
_V1_1_HEADER = "# backfill-manifest v1.1 - NOT R10 custodial"

_SAMPLE_CSV_BODY = (
    "chunk_id,start_date,end_date,ticker,status\n"
    "WDOFUT_2023-01-02_2023-01-06,2023-01-02,2023-01-06,WDOFUT,ok\n"
    "WDOFUT_2023-01-09_2023-01-13,2023-01-09,2023-01-13,WDOFUT,ok\n"
)


def _write_v1(tmp: Path) -> Path:
    p = tmp / "manifest.csv"
    p.write_text(_V1_HEADER + "\n" + _SAMPLE_CSV_BODY, encoding="utf-8")
    return p


def _write_v1_1(tmp: Path) -> Path:
    p = tmp / "manifest.csv"
    p.write_text(_V1_1_HEADER + "\n" + _SAMPLE_CSV_BODY, encoding="utf-8")
    return p


def test_ac5_read_v1_ok(tmp_path):
    p = _write_v1(tmp_path)
    header, rows = read_manifest_rows(p)
    assert header == _V1_HEADER
    assert len(rows) == 2
    assert rows[0]["chunk_id"] == "WDOFUT_2023-01-02_2023-01-06"


def test_ac5_read_v1_1_ok(tmp_path):
    p = _write_v1_1(tmp_path)
    header, rows = read_manifest_rows(p)
    assert header == _V1_1_HEADER
    assert len(rows) == 2


def test_ac5_upgrade_v1_to_v1_1(tmp_path):
    p = _write_v1(tmp_path)
    res = upgrade_manifest_header(p)
    assert res["status"] == "upgraded"
    assert res["new_header"] == _V1_1_HEADER
    text = p.read_text(encoding="utf-8")
    assert text.startswith(_V1_1_HEADER)
    # Data rows preserved byte-for-byte
    assert _SAMPLE_CSV_BODY in text


def test_ac5_data_rows_byte_equal_post_upgrade(tmp_path):
    p = _write_v1(tmp_path)
    _, rows_before = read_manifest_rows(p)
    upgrade_manifest_header(p)
    _, rows_after = read_manifest_rows(p)
    assert rows_before == rows_after


def test_ac5_idempotent_on_v1_1(tmp_path):
    p = _write_v1_1(tmp_path)
    res = upgrade_manifest_header(p)
    assert res["status"] == "noop_already_at_target"


def test_ac5_dry_run_does_not_write(tmp_path):
    p = _write_v1(tmp_path)
    original = p.read_bytes()
    res = upgrade_manifest_header(p, dry_run=True)
    assert res["status"] == "dry_run"
    assert p.read_bytes() == original


def test_ac5_refuses_data_manifest_r10_path(tmp_path):
    # Even simulated path containing data/manifest.csv must be refused.
    fake = tmp_path / "data" / "manifest.csv"
    fake.parent.mkdir(parents=True)
    fake.write_text(_V1_HEADER + "\n" + _SAMPLE_CSV_BODY, encoding="utf-8")
    with pytest.raises(PermissionError):
        upgrade_manifest_header(fake)


def test_ac5_refuses_unknown_header(tmp_path):
    p = tmp_path / "manifest.csv"
    p.write_text("# not-a-backfill-manifest\nchunk_id\n", encoding="utf-8")
    with pytest.raises(ValueError):
        upgrade_manifest_header(p)
