"""AC6 — PROJECTION_SEMVER + dataset_hash tuple (Sable C3 binding).

Tests:
  (i)   PROJECTION_SEMVER constant equals "0.1.0"
  (ii)  compute_dataset_hash returns tuple shape (str, str)
  (iii) hash is deterministic across calls on same file
  (iv)  semver comparable (parses cleanly)
  (v)   different content -> different hash; same content -> same hash
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.dll_backfill_projection import (
    PROJECTION_SEMVER,
    compute_dataset_hash,
)


def test_ac6_semver_constant_value():
    assert PROJECTION_SEMVER == "0.1.0"


def test_ac6_semver_parseable():
    parts = PROJECTION_SEMVER.split(".")
    assert len(parts) == 3
    for p in parts:
        int(p)  # raises if non-numeric


def test_ac6_dataset_hash_tuple_shape(tmp_path):
    p = tmp_path / "stub.parquet"
    p.write_bytes(b"PAR1\x00\x01\x02deadbeefPAR1")
    res = compute_dataset_hash(p)
    assert isinstance(res, tuple)
    assert len(res) == 2
    h, semver = res
    assert isinstance(h, str)
    assert isinstance(semver, str)
    assert len(h) == 64       # sha256 hex digest length
    assert semver == PROJECTION_SEMVER


def test_ac6_hash_deterministic(tmp_path):
    p = tmp_path / "stub.parquet"
    p.write_bytes(b"some-fixed-content-1234")
    h1 = compute_dataset_hash(p)
    h2 = compute_dataset_hash(p)
    assert h1 == h2


def test_ac6_different_content_different_hash(tmp_path):
    a = tmp_path / "a.parquet"
    b = tmp_path / "b.parquet"
    a.write_bytes(b"content-A")
    b.write_bytes(b"content-B")
    ha, _ = compute_dataset_hash(a)
    hb, _ = compute_dataset_hash(b)
    assert ha != hb


def test_ac6_same_content_same_hash(tmp_path):
    a = tmp_path / "a.parquet"
    b = tmp_path / "b.parquet"
    payload = b"identical-bytes" * 1000
    a.write_bytes(payload)
    b.write_bytes(payload)
    ha, _ = compute_dataset_hash(a)
    hb, _ = compute_dataset_hash(b)
    assert ha == hb


def test_ac6_tuple_usable_as_dict_key(tmp_path):
    p = tmp_path / "stub.parquet"
    p.write_bytes(b"x" * 16)
    key = compute_dataset_hash(p)
    cache = {key: "cached-value"}
    assert cache[key] == "cached-value"
    # Different semver in tuple breaks cache hit (Sable C3 binding)
    fake_key = (key[0], "0.2.0")
    assert fake_key not in cache
