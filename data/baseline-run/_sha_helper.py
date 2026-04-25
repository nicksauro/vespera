"""Ephemeral helper: compute sha256 for all canonical parquets + manifest.
Gage Phase 1b/5e pre- and post-quiesce integrity check.
L4 scratch; safe to delete after audit.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    repo = pathlib.Path(__file__).resolve().parents[2]
    targets: dict[str, pathlib.Path] = {
        "data/manifest.csv": repo / "data" / "manifest.csv",
    }
    for p in sorted((repo / "data" / "in_sample").rglob("*.parquet")):
        rel = p.relative_to(repo).as_posix()
        targets[rel] = p

    out: dict[str, str] = {}
    for rel, p in targets.items():
        out[rel] = sha256_file(p)
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
