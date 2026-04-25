#!/usr/bin/env python
"""WIP preview manifest generator — NOT CUSTODIAL.

Lê parquets em data/in_sample/ read-only e produz data/manifest_PREVIEW.csv
com schema compatível ao manifest.csv oficial.

Usado por T002.0b dev (feed_parquet.py) como fixture enquanto o script oficial
(scripts/materialize_parquet.py PID 12608) ainda grava o manifest real no fim
de seu run. DESCARTÁVEL quando data/manifest.csv oficial for gravado.
"""
from __future__ import annotations

import csv
import hashlib
import sys
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.materialize_parquet import MANIFEST_COLUMNS, classify_phase

PREVIEW_PATH = REPO_ROOT / "data" / "manifest_PREVIEW.csv"
IN_SAMPLE_DIR = REPO_ROOT / "data" / "in_sample"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def preview_row(parquet_path: Path) -> dict[str, str]:
    meta = pq.read_metadata(parquet_path)
    rows = meta.num_rows
    sha = sha256_file(parquet_path)
    tbl = pq.read_table(parquet_path, columns=["timestamp"])
    ts_col = tbl.column("timestamp").to_pandas()
    start_ts = ts_col.min()
    end_ts = ts_col.max()
    phase = classify_phase(start_ts.to_pydatetime().date(), end_ts.to_pydatetime().date())
    rel = parquet_path.relative_to(REPO_ROOT).as_posix()
    return {
        "path": rel,
        "rows": str(rows),
        "sha256": sha,
        "start_ts_brt": start_ts.isoformat(),
        "end_ts_brt": end_ts.isoformat(),
        "ticker": "WDO",
        "phase": phase,
        "generated_at_brt": datetime.now().isoformat(timespec="seconds"),
    }


def main() -> int:
    parquets = sorted(IN_SAMPLE_DIR.rglob("*.parquet"))
    print(f"[preview] Found {len(parquets)} parquets in {IN_SAMPLE_DIR}")
    if not parquets:
        print("[preview] nothing to preview", file=sys.stderr)
        return 1

    with PREVIEW_PATH.open("w", encoding="utf-8", newline="") as fh:
        fh.write("# WIP PREVIEW — NOT CUSTODIAL MANIFEST.\n")
        fh.write("# SOURCE=dara_preview_wip_NOT_CUSTODIAL.\n")
        fh.write("# Descartavel quando data/manifest.csv oficial for gravado pelo PID 12608.\n")
        writer = csv.DictWriter(
            fh, fieldnames=list(MANIFEST_COLUMNS), lineterminator="\n"
        )
        writer.writeheader()
        for p in parquets:
            row = preview_row(p)
            print(
                f"[preview]   {row['path']} rows={row['rows']} "
                f"phase={row['phase']} sha256={row['sha256'][:12]}..."
            )
            writer.writerow(row)

    print(f"[preview] DONE -> {PREVIEW_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
