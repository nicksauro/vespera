"""Negative tests for MANIFEST R15 gate — proves the gate fails when it must.

A contract test that never fails is worthless. This module constructs
synthetic spec payloads that violate R15 in each possible way and verifies
that the corresponding assertion in test_spec_version_gate.py catches them.

We don't write fake YAML files to disk; we instantiate SpecFile directly
with synthetic data and invoke the test functions as plain callables.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
import yaml

from tests.contracts.test_spec_version_gate import (
    REQUIRED_REVISION_FIELDS,
    SpecFile,
    test_major_zero_breaking_requires_revision as _check_major_zero,
    test_revision_cosign_hash_matches_payload as _check_cosign,
    test_revision_id_format as _check_rev_id,
    test_revision_version_chain as _check_chain,
    test_spec_has_valid_version as _check_version,
)

FAKE_PATH = Path("synthetic/fake-spec-v0.1.0.yaml")


def _canonical_hash(revision: dict) -> str:
    payload = {
        k: revision.get(k)
        for k in REQUIRED_REVISION_FIELDS
        if k != "pax_cosign_hash"
    }
    canonical = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _valid_revision() -> dict:
    rev = {
        "revision_id": "PRR-20260421-1",
        "timestamp_brt": "2026-04-21T18:00:00",
        "from_version": "0.1.0",
        "to_version": "0.2.0",
        "breaking_fields": ["splits.in_sample", "features.percentile_lookback"],
        "justification": "TimescaleDB coverage starts 2024-01-02; P252 warm-up impossible.",
        "data_constraint_evidence": "SELECT MIN(range_start) FROM timescaledb_information.chunks → 2023-01-02 isolated, 2024-01-02 continuous.",
        "pax_cosign_hash": None,
    }
    rev["pax_cosign_hash"] = _canonical_hash(rev)
    return rev


def test_invalid_version_is_caught() -> None:
    spec = SpecFile(path=FAKE_PATH, data={"version": "v0.1"})
    with pytest.raises(AssertionError, match="not valid semver"):
        _check_version(spec)


def test_major_zero_breaking_without_revision_is_caught() -> None:
    rev = _valid_revision()
    rev["data_constraint_evidence"] = ""
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    with pytest.raises(AssertionError, match="missing required fields"):
        _check_major_zero(spec)


def test_major_zero_non_breaking_is_allowed() -> None:
    rev = _valid_revision()
    rev["breaking_fields"] = []
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    _check_major_zero(spec)


def test_invalid_revision_id_is_caught() -> None:
    rev = _valid_revision()
    rev["revision_id"] = "REV-001"
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    with pytest.raises(AssertionError, match="does not match pattern"):
        _check_rev_id(spec)


def test_revision_version_not_monotonic_is_caught() -> None:
    rev1 = _valid_revision()
    rev2 = _valid_revision()
    rev2["revision_id"] = "PRR-20260422-1"
    rev2["from_version"] = "0.1.0"
    rev2["to_version"] = "0.1.5"
    rev2["pax_cosign_hash"] = _canonical_hash(rev2)
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev1, rev2]},
    )
    with pytest.raises(AssertionError, match="breaks append-only chain"):
        _check_chain(spec)


def test_revision_from_geq_to_is_caught() -> None:
    rev = _valid_revision()
    rev["from_version"] = "0.2.0"
    rev["to_version"] = "0.1.0"
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    with pytest.raises(AssertionError, match="is not strictly less than"):
        _check_chain(spec)


def test_forged_cosign_hash_is_caught() -> None:
    rev = _valid_revision()
    rev["pax_cosign_hash"] = "0" * 64
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    with pytest.raises(AssertionError, match="does not match SHA256"):
        _check_cosign(spec)


def test_altered_revision_after_cosign_is_caught() -> None:
    rev = _valid_revision()
    rev["justification"] = "retroactively edited after Pax signed"
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    with pytest.raises(AssertionError, match="does not match SHA256"):
        _check_cosign(spec)


def test_valid_revision_passes_all_gates() -> None:
    rev = _valid_revision()
    spec = SpecFile(
        path=FAKE_PATH,
        data={"version": "0.2.0", "preregistration_revisions": [rev]},
    )
    _check_version(spec)
    _check_major_zero(spec)
    _check_rev_id(spec)
    _check_chain(spec)
    _check_cosign(spec)
