"""Backfill canonical manifest.csv from parquet files already on disk.

Story: T002.0a — Phase 1 of the Option C manifest strategy (squad vote
4/4 Dara/Riven/Beckett/Sable).

Purpose
-------
The canonical ``data/manifest.csv`` has 1 row (Jan 2024, written by the
very first test run of the pre-patch materializer) but 16 parquet files
exist on disk (Jan 2024 through Apr 2025). This script rebuilds a
complete canonical manifest with 16 rows, with every field traced back
to either:

  * the parquet file's bytes (sha256 via _sha256_file, num_rows + min/max
    timestamp via pyarrow metadata / column scan), or
  * the filename date pattern (year, month).

NO DB queries. NO re-materialization. Observation-only.

Article IV compliance
---------------------
Every emitted field traces to file bytes or filename parse. No invented
data. The ``generated_at_brt`` column reflects when THIS script ran (not
when the parquet was originally written), which is honest — the parquet
is the custodial source of truth, and this manifest is a re-indexing of
already-custodial artifacts.

Write strategy
--------------
The existing 1-row ``data/manifest.csv`` is REPLACED atomically. The
Jan 2024 row is recomputed from the current on-disk parquet; if the old
row's sha256 matched the current file, the replacement is a no-op
semantically. If the sha256 differs, that indicates the Jan 2024 parquet
was re-written between the old manifest row and now — worth logging as
an anomaly.

Guardrails
----------
* NEVER writes to ``data/in_sample/`` (read-only).
* Writes ``data/manifest.csv`` via atomic temp+replace.
* Fails loudly on any read/hash error — no silent skip.
"""

from __future__ import annotations

import csv
import hashlib
import os
import re
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from materialize_parquet import (  # noqa: E402
    MANIFEST_COLUMNS,
    classify_phase,
)

REPO_ROOT = _SCRIPTS_DIR.parent
IN_SAMPLE_DIR = REPO_ROOT / "data" / "in_sample"
MANIFEST_PATH = REPO_ROOT / "data" / "manifest.csv"

EXPECTED_SCHEMA = (
    "timestamp", "ticker", "price", "qty", "aggressor",
    "buy_agent", "sell_agent",
)

_PARQUET_NAME_RE = re.compile(
    r"^(?P<ticker>[a-z]+)-(?P<year>\d{4})-(?P<month>\d{2})\.parquet$"
)


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _iter_parquets(root: Path) -> list[Path]:
    out: list[Path] = []
    for year_dir in sorted(root.glob("year=*")):
        if not year_dir.is_dir():
            continue
        for month_dir in sorted(year_dir.glob("month=*")):
            if not month_dir.is_dir():
                continue
            for pq in sorted(month_dir.glob("*.parquet")):
                out.append(pq)
    return out


def _load_existing_manifest() -> dict[str, dict[str, str]]:
    """Return {path: row} from existing manifest.csv, or empty dict if none."""
    out: dict[str, dict[str, str]] = {}
    if not MANIFEST_PATH.exists():
        return out
    with MANIFEST_PATH.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            path = row.get("path", "")
            if path:
                out[path] = row
    return out


def _inspect(pq_path: Path):
    """Return (row_dict, anomalies) for one parquet file."""
    import pyarrow.parquet as pq  # type: ignore[import-untyped]

    anomalies: list[str] = []
    rel = Path(os.path.relpath(pq_path, REPO_ROOT)).as_posix()
    name = pq_path.name
    m = _PARQUET_NAME_RE.match(name)
    if not m:
        anomalies.append(f"{rel}: filename does not match wdo-YYYY-MM.parquet")
        return None, anomalies

    file_ticker = m.group("ticker").upper()

    meta = pq.read_metadata(str(pq_path))
    num_rows = int(meta.num_rows)
    if num_rows == 0:
        anomalies.append(f"{rel}: num_rows == 0")
        return None, anomalies

    schema = pq.read_schema(str(pq_path))
    got_fields = tuple(schema.names)
    if got_fields != EXPECTED_SCHEMA:
        anomalies.append(
            f"{rel}: schema mismatch got={got_fields} expected={EXPECTED_SCHEMA}"
        )
        return None, anomalies

    # timestamp min/max — use row-group statistics (footer-only, cheap).
    # Since the materializer's query is ORDER BY ticker, timestamp and each
    # parquet contains a single ticker, the first row-group's min is the
    # file's min and the last row-group's max is the file's max. We still
    # sweep all row-groups defensively.
    ts_col_idx = None
    for i, name in enumerate(schema.names):
        if name == "timestamp":
            ts_col_idx = i
            break
    if ts_col_idx is None:
        anomalies.append(f"{rel}: timestamp column not found in schema")
        return None, anomalies

    rg_mins = []
    rg_maxes = []
    for rg_idx in range(meta.num_row_groups):
        rg = meta.row_group(rg_idx)
        col_meta = rg.column(ts_col_idx)
        if not col_meta.is_stats_set:
            anomalies.append(
                f"{rel}: row-group {rg_idx} has no statistics for timestamp"
            )
            return None, anomalies
        stats = col_meta.statistics
        rg_mins.append(stats.min)
        rg_maxes.append(stats.max)

    if not rg_mins:
        anomalies.append(f"{rel}: no row-groups found")
        return None, anomalies
    start_ts = min(rg_mins)
    end_ts = max(rg_maxes)

    try:
        phase = classify_phase(start_ts.date(), end_ts.date())
    except ValueError as exc:
        anomalies.append(f"{rel}: phase classification error: {exc}")
        return None, anomalies

    digest = _sha256_file(pq_path)

    row = {
        "path": rel,
        "rows": str(num_rows),
        "sha256": digest,
        "start_ts_brt": start_ts.isoformat(),
        "end_ts_brt": end_ts.isoformat(),
        "ticker": file_ticker,
        "phase": phase,
    }
    return row, anomalies


def main(argv: list[str] | None = None) -> int:
    parquets = _iter_parquets(IN_SAMPLE_DIR)
    if not parquets:
        print(f"FATAL: no parquets found under {IN_SAMPLE_DIR}", file=sys.stderr)
        return 1

    print(f"[backfill] found {len(parquets)} parquet file(s) under {IN_SAMPLE_DIR}")

    existing = _load_existing_manifest()
    if existing:
        print(f"[backfill] existing manifest.csv has {len(existing)} row(s) — will be replaced")

    generated_at = datetime.now().isoformat(timespec="seconds")

    rows_out: list[dict[str, str]] = []
    all_anomalies: list[str] = []
    resha_matches = 0
    resha_mismatches = 0

    for pq_path in parquets:
        rel = Path(os.path.relpath(pq_path, REPO_ROOT)).as_posix()
        print(f"[backfill] inspecting {rel}")
        row, anoms = _inspect(pq_path)
        all_anomalies.extend(anoms)
        if row is None:
            print(f"[backfill]   FAIL — skipped due to anomaly", file=sys.stderr)
            continue

        # Cross-check vs existing manifest row if any.
        prior = existing.get(rel)
        if prior is not None:
            prior_sha = prior.get("sha256", "")
            if prior_sha and prior_sha == row["sha256"]:
                resha_matches += 1
                print(f"[backfill]   sha256 matches prior manifest row")
            elif prior_sha:
                resha_mismatches += 1
                print(
                    f"[backfill]   ANOMALY: prior sha256={prior_sha} != "
                    f"current={row['sha256']}",
                    file=sys.stderr,
                )
                all_anomalies.append(
                    f"{rel}: sha256 drift vs prior manifest (prior={prior_sha} "
                    f"current={row['sha256']})"
                )

        row["generated_at_brt"] = generated_at
        rows_out.append(row)
        print(
            f"[backfill]   rows={row['rows']} phase={row['phase']} "
            f"ts=[{row['start_ts_brt']} .. {row['end_ts_brt']}] "
            f"sha256={row['sha256'][:16]}..."
        )

    if not rows_out:
        print("FATAL: no valid rows to write", file=sys.stderr)
        return 1

    # Atomic write: write to .tmp then os.replace.
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST_PATH.with_suffix(MANIFEST_PATH.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=list(MANIFEST_COLUMNS), lineterminator="\n"
        )
        writer.writeheader()
        for row in rows_out:
            writer.writerow({k: row.get(k, "") for k in MANIFEST_COLUMNS})
    os.replace(tmp, MANIFEST_PATH)

    phase_counts: dict[str, int] = {}
    for row in rows_out:
        phase_counts[row["phase"]] = phase_counts.get(row["phase"], 0) + 1

    print(f"[backfill] wrote {len(rows_out)} row(s) -> {MANIFEST_PATH}")
    print(
        f"[backfill] phase breakdown: "
        + ", ".join(f"{k}={v}" for k, v in sorted(phase_counts.items()))
    )
    if existing:
        print(
            f"[backfill] re-sha256 vs prior manifest: "
            f"matches={resha_matches} mismatches={resha_mismatches}"
        )
    if all_anomalies:
        print("[backfill] ANOMALIES DETECTED:", file=sys.stderr)
        for a in all_anomalies:
            print(f"[backfill]   - {a}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
