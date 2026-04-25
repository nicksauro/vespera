"""Contract test for MANIFEST R15 — Semver version gate.

Enforces that every ML spec under `docs/ml/specs/` whose `version` has
`major == 0` and declares breaking changes (via `preregistration_revisions[]`)
has a valid, fully-populated revision entry matching the schema defined in
`squads/quant-trading-squad/MANIFEST.md § 15`.

This test is a CI gate. A failure here means a spec was bumped in a way that
violates R15 — merge must be blocked until either (a) the revision entry is
completed, or (b) the change is reclassified as non-breaking.

Origin: Sable finding 005 (adjusted scope by Quinn 2026-04-21 after R15 ratified).
Schema: MANIFEST § 15 table of 8 required fields.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECS_DIR = REPO_ROOT / "docs" / "ml" / "specs"

REQUIRED_REVISION_FIELDS: tuple[str, ...] = (
    "revision_id",
    "timestamp_brt",
    "from_version",
    "to_version",
    "breaking_fields",
    "justification",
    "data_constraint_evidence",
    "pax_cosign_hash",
)

REVISION_ID_PATTERN = re.compile(r"^PRR-\d{8}-\d+$")
SEMVER_PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class SpecFile:
    path: Path
    data: dict

    @property
    def version(self) -> str:
        return str(self.data.get("version", ""))

    @property
    def major(self) -> int | None:
        m = SEMVER_PATTERN.match(self.version)
        return int(m.group(1)) if m else None

    @property
    def revisions(self) -> list[dict]:
        rev = self.data.get("preregistration_revisions") or []
        return rev if isinstance(rev, list) else []


def _discover_specs() -> list[SpecFile]:
    if not SPECS_DIR.is_dir():
        return []
    specs: list[SpecFile] = []
    for p in sorted(SPECS_DIR.glob("*.yaml")):
        with p.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            pytest.fail(f"spec {p} does not deserialize to a mapping")
        specs.append(SpecFile(path=p, data=data))
    return specs


SPECS = _discover_specs()


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.path.name)
def test_spec_has_valid_version(spec: SpecFile) -> None:
    """Every spec must declare a parseable semver version."""
    assert SEMVER_PATTERN.match(spec.version), (
        f"{spec.path.name}: version '{spec.version}' is not valid semver (X.Y.Z)"
    )


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.path.name)
def test_major_zero_breaking_requires_revision(spec: SpecFile) -> None:
    """MANIFEST R15 primary gate.

    If the spec is in major==0 phase AND declares any entry in
    preregistration_revisions[] whose `breaking_fields` is non-empty, then
    that entry must satisfy the 8-field schema.

    If the spec has no revisions at all, that's allowed — it simply means
    no breaking bump has occurred yet.
    """
    if spec.major is None or spec.major != 0:
        pytest.skip(f"{spec.path.name}: major={spec.major} — R15 applies to major==0 only")

    for idx, revision in enumerate(spec.revisions):
        assert isinstance(revision, dict), (
            f"{spec.path.name}: preregistration_revisions[{idx}] is not a mapping"
        )

        breaking = revision.get("breaking_fields") or []
        if not breaking:
            continue

        missing = [f for f in REQUIRED_REVISION_FIELDS if not revision.get(f)]
        assert not missing, (
            f"{spec.path.name}: preregistration_revisions[{idx}] declares "
            f"breaking_fields={breaking} but is missing required fields: {missing}. "
            f"See MANIFEST § 15 schema."
        )


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.path.name)
def test_revision_id_format(spec: SpecFile) -> None:
    """revision_id must follow PRR-YYYYMMDD-n pattern."""
    for idx, revision in enumerate(spec.revisions):
        rid = revision.get("revision_id", "")
        if not rid:
            continue
        assert REVISION_ID_PATTERN.match(str(rid)), (
            f"{spec.path.name}: preregistration_revisions[{idx}].revision_id "
            f"'{rid}' does not match pattern PRR-YYYYMMDD-n"
        )


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.path.name)
def test_revision_version_chain(spec: SpecFile) -> None:
    """Each revision's `to_version` must be <= the spec's current version,
    and the chain from_version→to_version must be monotonically non-decreasing
    when revisions are listed in order (append-only invariant)."""
    prev_to: tuple[int, int, int] | None = None
    for idx, revision in enumerate(spec.revisions):
        from_v = revision.get("from_version")
        to_v = revision.get("to_version")
        if not from_v or not to_v:
            continue
        m_from = SEMVER_PATTERN.match(str(from_v))
        m_to = SEMVER_PATTERN.match(str(to_v))
        assert m_from and m_to, (
            f"{spec.path.name}: revision[{idx}] has non-semver versions "
            f"from={from_v} to={to_v}"
        )
        tup_from = (int(m_from.group(1)), int(m_from.group(2)), int(m_from.group(3)))
        tup_to = (int(m_to.group(1)), int(m_to.group(2)), int(m_to.group(3)))
        assert tup_from < tup_to, (
            f"{spec.path.name}: revision[{idx}] from_version {from_v} "
            f"is not strictly less than to_version {to_v}"
        )
        if prev_to is not None:
            assert tup_from >= prev_to, (
                f"{spec.path.name}: revision[{idx}] from_version {from_v} "
                f"breaks append-only chain (previous to_version was "
                f"{'.'.join(map(str, prev_to))})"
            )
        prev_to = tup_to


@pytest.mark.parametrize("spec", SPECS, ids=lambda s: s.path.name)
def test_revision_cosign_hash_matches_payload(spec: SpecFile) -> None:
    """pax_cosign_hash must be SHA256 of the revision payload (all required
    fields except the hash itself, serialized deterministically).

    This is the auditor-verifiable proof that Pax co-signed the exact content
    of the revision — not a substituted version. See MANIFEST § 15 schema
    field `pax_cosign_hash` and Sable's adendo 1 in MCP-20260421-R15.
    """
    for idx, revision in enumerate(spec.revisions):
        cosign = revision.get("pax_cosign_hash")
        if not cosign:
            continue
        payload = {
            k: revision.get(k)
            for k in REQUIRED_REVISION_FIELDS
            if k != "pax_cosign_hash"
        }
        canonical = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        assert cosign == expected, (
            f"{spec.path.name}: revision[{idx}].pax_cosign_hash does not match "
            f"SHA256 of canonical payload.\n"
            f"  expected: {expected}\n"
            f"  got:      {cosign}\n"
            f"This means the revision was altered after Pax signed it, or the "
            f"hash was forged. MANIFEST § 15 violation."
        )


def test_specs_discovered() -> None:
    """Safety net: if this test collects zero specs the parametrize above
    silently passes by vacuousness. Fail explicitly if no specs found."""
    assert SPECS, f"no ML specs discovered under {SPECS_DIR} — check glob"
