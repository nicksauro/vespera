"""Pax co-sign helper — computes canonical SHA256 for preregistration_revisions[].

Usage:
    python scripts/pax_cosign.py compute <spec-file.yaml> [--index N]
        Prints the expected pax_cosign_hash for revision at index N (default 0).

    python scripts/pax_cosign.py verify <spec-file.yaml>
        Verifies all revision hashes in the spec. Exit 0 if all valid.

The canonical payload is built per MANIFEST § 15 schema:
    yaml.safe_dump({k: rev[k] for k in REQUIRED if k != "pax_cosign_hash"},
                   sort_keys=True, allow_unicode=True)
    sha256(canonical.encode("utf-8")).hexdigest()

This mirrors exactly what tests/contracts/test_spec_version_gate.py asserts,
so a hash computed here will pass the gate.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import yaml

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


def canonical_hash(revision: dict) -> str:
    payload = {
        k: revision.get(k)
        for k in REQUIRED_REVISION_FIELDS
        if k != "pax_cosign_hash"
    }
    canonical = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_spec(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise SystemExit(f"spec {path} does not deserialize to a mapping")
    return data


def cmd_compute(args: argparse.Namespace) -> int:
    spec = load_spec(Path(args.spec))
    revisions = spec.get("preregistration_revisions") or []
    if args.index >= len(revisions):
        print(f"ERROR: spec has {len(revisions)} revision(s); index {args.index} out of range", file=sys.stderr)
        return 2
    rev = revisions[args.index]
    print(canonical_hash(rev))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    spec = load_spec(Path(args.spec))
    revisions = spec.get("preregistration_revisions") or []
    if not revisions:
        print("no revisions to verify")
        return 0
    failures = 0
    for idx, rev in enumerate(revisions):
        expected = canonical_hash(rev)
        got = rev.get("pax_cosign_hash") or ""
        rid = rev.get("revision_id", f"<no-id-idx-{idx}>")
        if expected == got:
            print(f"OK   {rid}  {got}")
        else:
            print(f"FAIL {rid}")
            print(f"     expected: {expected}")
            print(f"     got:      {got}")
            failures += 1
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="pax_cosign", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_compute = sub.add_parser("compute", help="Compute expected hash for a revision")
    p_compute.add_argument("spec", help="Path to spec YAML")
    p_compute.add_argument("--index", type=int, default=0, help="Revision index (default 0)")
    p_compute.set_defaults(func=cmd_compute)

    p_verify = sub.add_parser("verify", help="Verify all revision hashes in a spec")
    p_verify.add_argument("spec", help="Path to spec YAML")
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
