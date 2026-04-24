"""Generate the pinned T12b snapshot for cache-only sentinel-DOWN parity.

ADR-4 §13.2 Amendment 20260424-1.

Purpose
-------
Snapshot one WDO session-day (2024-03-04, strictly in-sample) from the
feed_timescale (source-of-truth) adapter, so T12b can prove cache
self-sufficiency against a pinned artifact with the sentinel container
STOPPED. Run ONLY when:
  1. the pinned snapshot needs to be created for the first time, OR
  2. a legitimate schema evolution triggered by a future ADR amendment
     requires regeneration.

Commit the generated ``wdo-2024-03-04.snapshot.json`` and
``MANIFEST.sha256`` together in the same commit.

Invocation (sentinel UP, hold-out LOCKED)
-----------------------------------------
    python tests/scripts/generate_t12b_snapshot.py

Hold-out lock
-------------
The target window 2024-03-04 is structurally in-sample (pre 2025-07-01),
but the guard is enforced BEFORE any I/O regardless — defense in depth
(§13.4 risk 7).
"""
from __future__ import annotations

import hashlib
import json
import pickle
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Repo root resolution — this script lives at tests/scripts/...
_REPO = Path(__file__).resolve().parents[2]

# Add scripts/ for the hold-out lock import.
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Add repo root so packages.* resolves.
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from _holdout_lock import assert_holdout_safe  # noqa: E402

_FIXTURE_DIR = _REPO / "tests" / "fixtures" / "adapter_parity_cache"
_SNAPSHOT_PATH = _FIXTURE_DIR / "wdo-2024-03-04.snapshot.json"
_MANIFEST_PATH = _FIXTURE_DIR / "MANIFEST.sha256"

# Target window (one WDO session-day, in-sample).
_WINDOW_START = datetime(2024, 3, 4)
_WINDOW_END = datetime(2024, 3, 5)
_TICKER = "WDO"
_GENERATOR_REL = "tests/scripts/generate_t12b_snapshot.py"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    # 1. Hold-out guard BEFORE any I/O — defense in depth (§13.4 R7).
    end_inclusive = (_WINDOW_END - timedelta(microseconds=1)).date()
    assert_holdout_safe(_WINDOW_START.date(), end_inclusive)

    # 2. Sentinel arm must be UP — this script is the source-of-truth
    #    record; running with sentinel DOWN would defeat the purpose.
    from packages.t002_eod_unwind.adapters import feed_timescale

    trades = [
        (t.ts, t.price, t.qty)
        for t in feed_timescale.load_trades(
            _WINDOW_START, _WINDOW_END, _TICKER,
        )
    ]
    if not trades:
        print(
            "ERROR: feed_timescale returned 0 trades — snapshot refused.",
            file=sys.stderr,
        )
        return 1

    # 3. Pickle + sha256 the 3-tuple list — the very contract T12b checks.
    digest = hashlib.sha256(pickle.dumps(trades, protocol=5)).hexdigest()

    # 4. Build snapshot payload (see §13.2 fixture format).
    first = trades[0]
    last = trades[-1]
    snapshot = {
        "version": 1,
        "window": {
            "start": _WINDOW_START.isoformat(),
            "end": _WINDOW_END.isoformat(),
            "ticker": _TICKER,
        },
        "row_count": len(trades),
        "sha256_of_pickled_trades": digest,
        "first_trade": [first[0].isoformat(), first[1], first[2]],
        "last_trade":  [last[0].isoformat(),  last[1],  last[2]],
        "first_3_rows": [
            [t[0].isoformat(), t[1], t[2]] for t in trades[:3]
        ],
        "last_3_rows": [
            [t[0].isoformat(), t[1], t[2]] for t in trades[-3:]
        ],
        "generated_at_brt": datetime.now().isoformat(timespec="seconds"),
        "generator": _GENERATOR_REL,
    }

    # 5. Atomic write (tmp + os.replace) — matches build_raw_trades_cache
    #    discipline so a crashed regeneration cannot leave a truncated JSON.
    _FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = _SNAPSHOT_PATH.with_suffix(_SNAPSHOT_PATH.suffix + ".tmp")
    tmp.write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    import os  # local to keep top-of-module lean
    os.replace(tmp, _SNAPSHOT_PATH)

    # 6. Update MANIFEST.sha256 — atomic. One entry per fixture file.
    snapshot_sha = _sha256_file(_SNAPSHOT_PATH)
    lines: list[str] = []
    if _MANIFEST_PATH.exists():
        existing = _MANIFEST_PATH.read_text(encoding="utf-8").splitlines()
        for ln in existing:
            s = ln.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) >= 2 and parts[1] == _SNAPSHOT_PATH.name:
                continue  # drop stale entry, replace below
            lines.append(s)
    lines.append(f"{snapshot_sha}  {_SNAPSHOT_PATH.name}")
    manifest_text = "\n".join(lines) + "\n"
    mtmp = _MANIFEST_PATH.with_suffix(_MANIFEST_PATH.suffix + ".tmp")
    mtmp.write_text(manifest_text, encoding="utf-8")
    os.replace(mtmp, _MANIFEST_PATH)

    print(f"[t12b-snap] window={_WINDOW_START.date()} ticker={_TICKER}")
    print(f"[t12b-snap] row_count={snapshot['row_count']}")
    print(f"[t12b-snap] pickled-trades sha256={digest}")
    print(f"[t12b-snap] snapshot file sha256={snapshot_sha}")
    print(f"[t12b-snap] written: {_SNAPSHOT_PATH}")
    print(f"[t12b-snap] manifest: {_MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
