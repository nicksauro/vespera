"""A7-Dara manifest extension — atomic append-only mutation.

Authority: User MWF cosign §9 of T003-A6-COSIGN-REQUEST-2026-05-03.md.
Council ref: 2026-05-03 §6.5 routing item 1 (phase=archive append-only).
R10 strict: byte-equal pre/post for existing rows; tmp+os.replace atomic write.
Article IV: every value source-traced to backfill manifest v1.1 + parquet bytes.

This script is one-shot tooling for the A7 mutation event. NOT a library.
"""
from __future__ import annotations

import csv
import hashlib
import io
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq
import pyarrow.compute as pc

REPO_ROOT = Path("C:/Users/Pichau/Desktop/Algotrader")
CANONICAL_MANIFEST = REPO_ROOT / "data" / "manifest.csv"
BACKUP_MANIFEST = REPO_ROOT / "data" / "manifest.csv.pre-A7-backup-2026-05-03.csv"
BACKFILL_ROOT_D = Path("D:/Algotrader/dll-backfill")
BACKFILL_MANIFEST = BACKFILL_ROOT_D / "manifest.csv"

GENERATED_AT_BRT = "2026-05-03T00:00:00"  # A7 dispatch date (BRT)


def _sha256_file(path: Path, bufsize: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _read_existing_rows() -> tuple[bytes, str]:
    """Return (raw_bytes, sha256) of canonical manifest pre-mutation."""
    raw = CANONICAL_MANIFEST.read_bytes()
    return raw, hashlib.sha256(raw).hexdigest()


def _read_backfill_rows() -> list[dict]:
    """Read backfill v1.1 manifest (50 chunks) — comment line + DictReader."""
    rows: list[dict] = []
    with open(BACKFILL_MANIFEST, "r", encoding="utf-8", newline="") as fh:
        first = fh.readline()  # comment "# backfill-manifest v1.1 ..."
        assert first.startswith("# backfill-manifest v1.1"), f"unexpected header: {first!r}"
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def _extract_chunk_metadata(parquet_abs: Path) -> tuple[int, str, str, str]:
    """Return (rows, sha256_parquet, start_ts_brt_iso, end_ts_brt_iso).

    Reads the parquet to extract first/last timestamp (us precision storage).
    Hash is computed over raw on-disk bytes (compute_dataset_hash semantics).
    """
    sha = _sha256_file(parquet_abs)
    table = pq.read_table(parquet_abs, columns=["timestamp"])
    nrows = table.num_rows
    ts_col = table.column("timestamp")
    ts_min = pc.min(ts_col).as_py()
    ts_max = pc.max(ts_col).as_py()
    # ts_min / ts_max are datetime objects (us-precision); render ISO with us.
    start_iso = ts_min.isoformat(timespec="microseconds") if ts_min else ""
    end_iso = ts_max.isoformat(timespec="microseconds") if ts_max else ""
    return nrows, sha, start_iso, end_iso


def main() -> int:
    # ---- 1. Pre-mutation snapshot --------------------------------------------
    pre_raw, pre_sha = _read_existing_rows()
    backup_sha = _sha256_file(BACKUP_MANIFEST)
    print(f"[A7] pre_sha={pre_sha}")
    print(f"[A7] backup_sha={backup_sha}")
    assert pre_sha == backup_sha, "backup mismatch — ABORT"

    # ---- 2. Build 50 archive rows -------------------------------------------
    backfill_rows = _read_backfill_rows()
    assert len(backfill_rows) == 50, f"expected 50 chunks, got {len(backfill_rows)}"

    new_rows: list[dict] = []
    for i, br in enumerate(backfill_rows, start=1):
        rel_path = br["parquet_relative_path"]  # "Algotrader\\dll-backfill\\..."
        # Backfill rows have a leading-Algotrader\ relative path; the actual
        # absolute path is D:\Algotrader\dll-backfill\... . Build absolute D:\.
        abs_path = Path("D:/") / rel_path.replace("\\", "/")
        if not abs_path.exists():
            raise FileNotFoundError(
                f"chunk parquet not found: {abs_path} "
                f"(from backfill row {i}: {br['chunk_id']})"
            )
        nrows, sha, start_iso, end_iso = _extract_chunk_metadata(abs_path)
        # Cross-check trades_count from backfill manifest matches actual rows.
        bf_trades = int(br["trades_count"])
        if nrows != bf_trades:
            print(
                f"[A7][WARN] row-count mismatch chunk={br['chunk_id']} "
                f"backfill={bf_trades} actual={nrows} (using actual)"
            )
        # Path field stored in canonical manifest:
        #   reference D:\ archive parquet via posix-style path with D:/ prefix.
        #   This is OFF-REPO custodial — never touched by repo Glob/Read.
        canonical_path = "D:/" + rel_path.replace("\\", "/")
        new_rows.append({
            "path": canonical_path,
            "rows": str(nrows),
            "sha256": sha,
            "start_ts_brt": start_iso,
            "end_ts_brt": end_iso,
            "ticker": "WDOFUT",  # B3 mini-dollar (vs Sentinel WDO shorthand)
            "phase": "archive",
            "generated_at_brt": GENERATED_AT_BRT,
        })
        print(f"[A7] chunk {i:02d}/50 OK rows={nrows} sha={sha[:12]}...")

    # ---- 3. Compose post-mutation bytes -------------------------------------
    # Render new rows in canonical Sentinel CSV format (LF-only, no quoting,
    # field order matches existing header). Append directly to pre-mutation
    # bytes — preserving every existing byte verbatim.
    buf = io.StringIO()
    writer = csv.DictWriter(
        buf,
        fieldnames=["path", "rows", "sha256", "start_ts_brt", "end_ts_brt",
                    "ticker", "phase", "generated_at_brt"],
        lineterminator="\n",
        quoting=csv.QUOTE_MINIMAL,
    )
    for r in new_rows:
        writer.writerow(r)
    new_block = buf.getvalue().encode("utf-8")

    # Pre-raw ends with \n (verified earlier). Just concatenate.
    assert pre_raw.endswith(b"\n"), "pre-raw missing trailing newline — ABORT"
    post_raw = pre_raw + new_block

    # ---- 4. Byte-equal pre-segment paranoia check ---------------------------
    assert post_raw[: len(pre_raw)] == pre_raw, "pre-segment mutated — ABORT"
    pre_segment_sha = hashlib.sha256(post_raw[: len(pre_raw)]).hexdigest()
    assert pre_segment_sha == pre_sha, "pre-segment SHA mismatch — ABORT"
    print(f"[A7] pre_segment_sha_post={pre_segment_sha}  (matches pre_sha)")

    # ---- 5. Atomic write (tmp + os.replace) ---------------------------------
    tmp_dir = CANONICAL_MANIFEST.parent
    fd, tmp_name = tempfile.mkstemp(
        prefix="manifest.csv.", suffix=".a7tmp", dir=str(tmp_dir)
    )
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(post_raw)
        # os.replace is atomic on Windows when src/dst are on same volume.
        os.replace(tmp_name, CANONICAL_MANIFEST)
    except Exception:
        try:
            Path(tmp_name).unlink(missing_ok=True)
        except Exception:
            pass
        raise

    # ---- 6. Post-mutation verification ---------------------------------------
    post_disk = CANONICAL_MANIFEST.read_bytes()
    post_sha = hashlib.sha256(post_disk).hexdigest()
    assert post_disk == post_raw, "disk bytes != intended bytes — ABORT"
    assert post_disk[: len(pre_raw)] == pre_raw, "on-disk pre-segment mutated — ABORT"
    print(f"[A7] post_sha={post_sha}")
    print(f"[A7] rows_added=50  size_pre={len(pre_raw)}  size_post={len(post_disk)}")

    # ---- 7. Emit summary -----------------------------------------------------
    print(f"[A7] first_chunk={new_rows[0]['path']}")
    print(f"[A7] last_chunk={new_rows[-1]['path']}")
    print(f"[A7] sample_first_sha={new_rows[0]['sha256']}")
    print(f"[A7] sample_last_sha={new_rows[-1]['sha256']}")
    print("[A7] A7_PASS_PROCEED_TO_A8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
