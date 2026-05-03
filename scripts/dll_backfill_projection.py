"""dll_backfill_projection — consumption-time minimal-cast projection for Backfill 2023.

Source of truth:
    Council 2026-05-03 SCHEMA-RESOLUTION (RATIFIED Option D + R16, 5-5 + user MWF
    tiebreaker D, R16 10/10 unanimous CONCUR + Sable C1-C4 binding).
Spec:
    docs/stories/t003.a4.minimal-cast-projection.story.md  (AC1-AC7).
Council ref:
    docs/councils/COUNCIL-2026-05-03-SCHEMA-RESOLUTION.md  (§6.5 routing item 1).
D-02 register:
    docs/audits/AUDIT-2026-05-03-T003.A2-schema-split-divergence.md  (F2 accepted
    divergence — agents stay int64; reversal requires mini-Council per R16).
Authority:
    Dara (@data-engineer) implementation; Sable C3 versioning; Pax cosign on ACs.
    Article IV: every cast traces to §1.1 (Dara A2 findings F1-F5+F8) or §6.5
    (Option D routing) — no semantics invented.

Purpose
-------
R16 thesis: *"Information preservation by default. Raw fields captured by
canonical pipelines are NEVER dropped at storage time. Type/schema normalization
happens at consumption boundary (projection + cast), preserving original
parquet/manifest/registry-of-record."*

Storage at ``D:\\Algotrader\\dll-backfill\\`` is custodial 10-col rich
(``timestamp[us]``, ``ts_raw``, ``ticker``, ``price``, ``qty int64``, ``aggressor``,
``buy_agent int64``, ``sell_agent int64``, ``vol_brl``, ``trade_number``) with
``nullable=True`` flags. This module is the **consumer-side normalizer**: it
projects the 7-col canonical view (``timestamp, ticker, price, qty, aggressor,
buy_agent, sell_agent``) and applies minimal type/nullability casts so that
downstream A3-Nova / A4-Mira / A5-Sable consume an artifact byte-comparable to
Sentinel-2024 canonical (``data/in_sample/year=2024/month=01/wdo-2024-01.parquet``)
modulo F2 (the documented int64 agent divergence).

F2 ACCEPTED DIVERGENCE per Council 2026-05-03 — agents stay int64; zero-pad
REJECTED (Beckett VETO_B + Riven Bayesian 0.06 + Mira α-wasteful). Reversal
requires mini-Council per R16. See README companion at
``scripts/dll_backfill_projection.README.md``.

Casts applied (consumption-time only; storage is NEVER touched)
---------------------------------------------------------------
- ``timestamp[us] -> timestamp[ns]``  (lossless upcast; AC1)
- ``qty int64 -> int32``  (assert min/max in INT32 range first; AC2)
- ``nullable=True -> nullable=False`` for canonical 5 cols  (assert no
  nulls present first; AC3)
- ``buy_agent`` / ``sell_agent`` int64 **PRESERVED** as int64 (F2; AC4)

Versioning (Sable C3 binding)
-----------------------------
``PROJECTION_SEMVER = "0.1.0"`` is the consumer-side cache key component.
``compute_dataset_hash(path)`` returns a tuple ``(content_sha256, projection_semver)``.
Backtests use this tuple as cache key so reproducibility is byte-exact regardless
of which projection version a consumer applied.

R10 / Gate-5 / Article II preserved
-----------------------------------
- This module **NEVER** writes to ``data/manifest.csv`` (R10 custodial).
- This module **NEVER** mutates any production parquet at ``D:\\``.
- This module produces a **read-projected pyarrow Table in memory** (or writes
  to a caller-specified output path); it is a pure consumer adaptor.
- Push @devops Gage exclusive (Article II).
"""

from __future__ import annotations

import csv
import hashlib
import io
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

# ---------------------------------------------------------------------------
# Versioning surface (Sable C3 binding)
# ---------------------------------------------------------------------------

PROJECTION_SEMVER = "0.1.0"
"""Consumer-side projection version. Bumps via [DIVERGENCE] register per R16
reversal-clause. Backtest cache key tuple: ``(content_sha256, PROJECTION_SEMVER)``.
"""

_INT32_MIN = -(2 ** 31)
_INT32_MAX = (2 ** 31) - 1

# Canonical 7-col projection (matches Sentinel 2024 column ORDER + names).
# F2: buy_agent / sell_agent kept int64 here — DOCUMENTED carry-forward.
CANONICAL_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "ticker",
    "price",
    "qty",
    "aggressor",
    "buy_agent",
    "sell_agent",
)

# Subset asserted non-null after cast (Sentinel parity for these 5):
# timestamp, ticker, price, qty, aggressor.  buy_agent/sell_agent stay
# nullable in Sentinel 2024 itself, so we do NOT mark them non-null here.
_NONNULL_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "ticker",
    "price",
    "qty",
    "aggressor",
)


# ---------------------------------------------------------------------------
# Errors (fail-closed contracts)
# ---------------------------------------------------------------------------


class ProjectionOverflowError(ValueError):
    """Raised when AC2 qty cast would overflow int32 range.

    Carries chunk path + observed min/max for triage.
    """


class ProjectionNullabilityError(ValueError):
    """Raised when AC3 nullability assertion fails (nulls present in a column
    that Sentinel-2024 marks ``nullable=False``).

    Carries chunk path + per-column null counts for triage.
    """


class ProjectionSchemaError(ValueError):
    """Raised when input parquet is missing required canonical columns or has
    unexpected dtype that we do not know how to cast."""


# ---------------------------------------------------------------------------
# Cast primitives (each maps 1:1 to an AC)
# ---------------------------------------------------------------------------


def _cast_timestamp_us_to_ns(arr: pa.Array) -> pa.Array:
    """AC1 — timestamp[us] -> timestamp[ns] lossless upcast.

    pyarrow stores timestamps as int64 ticks at given unit. us -> ns is exactly
    multiplication by 1000 and fits in int64 for any reasonable date range
    (int64 ns supports ~+/-292 years from epoch). Backfill 2023 dates are
    well within range.
    """
    if arr.type == pa.timestamp("ns"):
        return arr
    if arr.type != pa.timestamp("us"):
        raise ProjectionSchemaError(
            f"AC1: expected timestamp[us], got {arr.type!r}"
        )
    # pa.compute.cast handles the lossless us->ns upcast correctly.
    return pc.cast(arr, pa.timestamp("ns"))


def _cast_qty_int64_to_int32(arr: pa.Array, *, source: str) -> pa.Array:
    """AC2 — qty int64 -> int32 with bounds assertion.

    Fails CLOSED via ``ProjectionOverflowError`` if any value lies outside
    [INT32_MIN, INT32_MAX]. No partial cast.
    """
    if arr.type == pa.int32():
        return arr
    if arr.type != pa.int64():
        raise ProjectionSchemaError(
            f"AC2: expected qty int64, got {arr.type!r}"
        )
    qty_min = pc.min(arr).as_py()
    qty_max = pc.max(arr).as_py()
    if qty_min is None or qty_max is None:
        # column is empty or all-null — degenerate; let downstream null-check
        # catch it via AC3.
        return pc.cast(arr, pa.int32())
    if qty_min < _INT32_MIN or qty_max > _INT32_MAX:
        raise ProjectionOverflowError(
            f"AC2 qty cast aborted (fail-closed): source={source} "
            f"observed_min={qty_min} observed_max={qty_max} "
            f"int32_range=[{_INT32_MIN},{_INT32_MAX}]"
        )
    return pc.cast(arr, pa.int32())


def _assert_no_nulls(table: pa.Table, *, source: str) -> None:
    """AC3 helper — assert that ``_NONNULL_COLUMNS`` have null_count==0.

    Raises ``ProjectionNullabilityError`` listing per-column null counts on
    failure. Called BEFORE we mark fields non-nullable in the projected
    schema (assert-then-mark discipline).
    """
    offenders: dict[str, int] = {}
    for col in _NONNULL_COLUMNS:
        if col not in table.schema.names:
            raise ProjectionSchemaError(
                f"AC3: missing required canonical column {col!r} in {source}"
            )
        nc = table.column(col).null_count
        if nc != 0:
            offenders[col] = nc
    if offenders:
        raise ProjectionNullabilityError(
            f"AC3 nullability assertion failed: source={source} "
            f"null_counts={offenders}"
        )


def _build_projected_schema(input_schema: pa.Schema) -> pa.Schema:
    """Build the post-cast 7-col canonical schema.

    - timestamp: timestamp[ns], non-null (AC1 + AC3)
    - ticker:    string, non-null (AC3)
    - price:     double, non-null (AC3)
    - qty:       int32, non-null (AC2 + AC3)
    - aggressor: string, non-null (AC3)
    - buy_agent: int64, NULLABLE (F2 ACCEPTED — AC4)
    - sell_agent: int64, NULLABLE (F2 ACCEPTED — AC4)
    """
    # Sanity: all canonical cols must be present in input (storage form).
    missing = [c for c in CANONICAL_COLUMNS if c not in input_schema.names]
    if missing:
        raise ProjectionSchemaError(
            f"input parquet missing canonical columns: {missing}"
        )
    fields: list[pa.Field] = [
        pa.field("timestamp", pa.timestamp("ns"), nullable=False),
        pa.field("ticker",    pa.string(),         nullable=False),
        pa.field("price",     pa.float64(),        nullable=False),
        pa.field("qty",       pa.int32(),          nullable=False),
        pa.field("aggressor", pa.string(),         nullable=False),
        pa.field("buy_agent", pa.int64(),          nullable=True),  # F2
        pa.field("sell_agent", pa.int64(),         nullable=True),  # F2
    ]
    return pa.schema(fields)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProjectionReport:
    """Per-chunk projection report (returned alongside projected Table)."""
    source: str
    rows: int
    qty_min: int | None
    qty_max: int | None
    null_counts: dict[str, int]      # observed nulls in canonical 7 cols
    cast_applied: dict[str, str]     # col -> "src_dtype -> dst_dtype"
    projection_semver: str = PROJECTION_SEMVER


def project_table(
    table: pa.Table,
    *,
    source: str = "<in-memory>",
) -> tuple[pa.Table, ProjectionReport]:
    """Apply AC1+AC2+AC3+AC4 casts to an in-memory pyarrow Table.

    Returns ``(projected_table, ProjectionReport)``. Fail-closed via
    ``ProjectionOverflowError`` (AC2) or ``ProjectionNullabilityError`` (AC3).

    ``buy_agent`` and ``sell_agent`` are PRESERVED as int64 per AC4 (F2
    documented divergence; reversal requires mini-Council per R16).
    """
    # 1. Schema sanity — all 7 canonical cols must be present.
    projected_schema = _build_projected_schema(table.schema)

    # 2. AC2 — qty bounds + cast.
    qty_arr = table.column("qty")
    qty_min = pc.min(qty_arr).as_py() if qty_arr.length() > 0 else None
    qty_max = pc.max(qty_arr).as_py() if qty_arr.length() > 0 else None
    qty_cast = _cast_qty_int64_to_int32(qty_arr, source=source)

    # 3. AC1 — timestamp upcast.
    ts_cast = _cast_timestamp_us_to_ns(table.column("timestamp"))

    # 4. Preserve untouched-cast cols (string/double/int64 agents).
    ticker_arr    = table.column("ticker")
    price_arr     = table.column("price")
    aggressor_arr = table.column("aggressor")
    buy_agent_arr  = table.column("buy_agent")   # F2 — kept int64
    sell_agent_arr = table.column("sell_agent")  # F2 — kept int64

    # 5. AC3 — assert no nulls in non-null-mandated cols, computed on the
    #          PROJECTED arrays (post-cast) for true safety.
    pre_proj = pa.table({
        "timestamp": ts_cast,
        "ticker":    ticker_arr,
        "price":     price_arr,
        "qty":       qty_cast,
        "aggressor": aggressor_arr,
        "buy_agent":  buy_agent_arr,
        "sell_agent": sell_agent_arr,
    })
    _assert_no_nulls(pre_proj, source=source)

    # 6. Mark non-null in schema (AC3 second half — assert-then-mark).
    projected_table = pa.Table.from_arrays(
        [
            ts_cast,
            ticker_arr,
            price_arr,
            qty_cast,
            aggressor_arr,
            buy_agent_arr,
            sell_agent_arr,
        ],
        schema=projected_schema,
    )

    null_counts = {c: pre_proj.column(c).null_count for c in CANONICAL_COLUMNS}
    cast_applied = {
        "timestamp": "timestamp[us] -> timestamp[ns]",
        "qty":       "int64 -> int32",
        "buy_agent": "int64 (PRESERVED — F2 accepted divergence)",
        "sell_agent": "int64 (PRESERVED — F2 accepted divergence)",
    }
    report = ProjectionReport(
        source=source,
        rows=projected_table.num_rows,
        qty_min=qty_min,
        qty_max=qty_max,
        null_counts=null_counts,
        cast_applied=cast_applied,
    )
    return projected_table, report


def project_parquet(
    src_path: str | Path,
    *,
    columns: Iterable[str] | None = None,
) -> tuple[pa.Table, ProjectionReport]:
    """Read a backfill chunk parquet and apply ``project_table``.

    ``columns`` is informational; we always read the canonical 7 (plus any the
    caller wants explicitly). Default reads exactly the canonical 7.
    """
    src_path = Path(src_path)
    cols = list(columns) if columns is not None else list(CANONICAL_COLUMNS)
    # Ensure canonical cols always present.
    for c in CANONICAL_COLUMNS:
        if c not in cols:
            cols.append(c)
    table = pq.read_table(src_path, columns=cols)
    # Reorder to canonical-only for return (drop any extra cols the caller
    # asked for so the output schema is byte-stable).
    table = table.select(list(CANONICAL_COLUMNS))
    return project_table(table, source=str(src_path))


# ---------------------------------------------------------------------------
# AC6 — dataset_hash + projection_semver tuple
# ---------------------------------------------------------------------------


def compute_dataset_hash(
    path: str | Path,
    *,
    bufsize: int = 1 << 20,
) -> tuple[str, str]:
    """Compute ``(content_sha256, PROJECTION_SEMVER)`` for a parquet file.

    The hash is computed over the **raw on-disk parquet bytes** (the storage
    custodial artifact). The tuple is the consumer-side cache key per Sable
    C3 — cache hits require BOTH content match AND projection version match.

    This is deliberately the file content hash (NOT the projected table hash)
    because:
      1. Storage is custodial (R10) — its sha256 IS the identity of the dataset.
      2. The projection layer is versioned independently via
         ``PROJECTION_SEMVER``; bumping it correctly invalidates downstream
         caches without recomputing the (expensive) file hash.
    """
    path = Path(path)
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return (h.hexdigest(), PROJECTION_SEMVER)


# ---------------------------------------------------------------------------
# AC5 — manifest header v1 -> v1.1 cosmetic bump
# ---------------------------------------------------------------------------


_MANIFEST_HEADER_V1 = "# backfill-manifest v1 - NOT R10 custodial"
_MANIFEST_HEADER_V1_1 = "# backfill-manifest v1.1 - NOT R10 custodial"


def upgrade_manifest_header(
    manifest_path: str | Path,
    *,
    from_version: str = "v1",
    to_version: str = "v1.1",
    dry_run: bool = False,
) -> dict[str, str]:
    """AC5 — bump backfill manifest header v1 -> v1.1 cosmetically.

    - Atomic write: tmp file in same dir + ``shutil.move`` replace.
    - Preserves ALL data rows byte-for-byte.
    - Reads BOTH ``v1`` and ``v1.1`` headers (backward-compat); refuses to
      modify unrelated headers (raises).
    - Backfill manifest at ``D:\\Algotrader\\dll-backfill\\manifest.csv`` is
      explicitly **NOT R10 custodial** (the comment line says so verbatim);
      it is the off-repo backfill orchestrator manifest. R10 protects
      ``data/manifest.csv`` (in-repo Sentinel manifest) which this function
      MUST NEVER touch.

    Returns a dict ``{"status": "...", "old_header": "...", "new_header": "..."}``.
    ``dry_run=True`` returns the dict without writing.
    """
    manifest_path = Path(manifest_path)
    if "data\\manifest.csv" in str(manifest_path).lower() \
            or "data/manifest.csv" in str(manifest_path).lower():
        raise PermissionError(
            "R10 violation refused: data/manifest.csv is custodial; "
            "this function only operates on the off-repo backfill manifest."
        )
    expected_old = f"# backfill-manifest {from_version} - NOT R10 custodial"
    expected_new = f"# backfill-manifest {to_version} - NOT R10 custodial"

    with open(manifest_path, "r", encoding="utf-8", newline="") as fh:
        first_line = fh.readline()
        rest = fh.read()
    first_stripped = first_line.rstrip("\r\n")

    if first_stripped == expected_new:
        return {
            "status": "noop_already_at_target",
            "old_header": first_stripped,
            "new_header": expected_new,
        }
    if first_stripped != expected_old:
        raise ValueError(
            f"manifest header mismatch: expected {expected_old!r}, "
            f"got {first_stripped!r}"
        )

    # Preserve original line ending of first line.
    if first_line.endswith("\r\n"):
        new_first = expected_new + "\r\n"
    elif first_line.endswith("\n"):
        new_first = expected_new + "\n"
    else:
        new_first = expected_new

    if dry_run:
        return {
            "status": "dry_run",
            "old_header": expected_old,
            "new_header": expected_new,
        }

    # Atomic write: tmp in same directory, then replace.
    tmp_dir = manifest_path.parent
    fd, tmp_name = tempfile.mkstemp(
        prefix=manifest_path.name + ".", suffix=".tmp", dir=str(tmp_dir)
    )
    try:
        with open(fd, "w", encoding="utf-8", newline="") as out:
            out.write(new_first)
            out.write(rest)
        # On Windows, os.replace is atomic if both paths are on the same volume.
        Path(tmp_name).replace(manifest_path)
    except Exception:
        try:
            Path(tmp_name).unlink(missing_ok=True)
        except Exception:
            pass
        raise

    return {
        "status": "upgraded",
        "old_header": expected_old,
        "new_header": expected_new,
    }


def read_manifest_rows(manifest_path: str | Path) -> tuple[str, list[dict[str, str]]]:
    """Read a backfill manifest CSV (v1 or v1.1 header) and return
    ``(header_line, [row_dicts...])``.

    Backward-compat reader for AC5 — accepts both v1 and v1.1 headers.
    """
    manifest_path = Path(manifest_path)
    rows: list[dict[str, str]] = []
    with open(manifest_path, "r", encoding="utf-8", newline="") as fh:
        first = fh.readline()
        first_stripped = first.rstrip("\r\n")
        if not first_stripped.startswith("#"):
            # No header comment line — rewind.
            fh.seek(0)
            first_stripped = ""
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return first_stripped, rows


# ---------------------------------------------------------------------------
# AC7 — A2 re-audit support (verdict generation helper)
# ---------------------------------------------------------------------------


def reaudit_at_projection_boundary(
    chunk_paths: Iterable[str | Path],
    *,
    sentinel_path: str | Path,
) -> dict[str, object]:
    """AC7 — run the A2 schema parity audit AT THE PROJECTION OUTPUT.

    For each chunk in ``chunk_paths``:
      1. Read storage (10-col, int64 agents, ts[us], nullable=True).
      2. Apply ``project_table`` (consumer-side casts).
      3. Compare projected schema against Sentinel reference schema.

    Per-column expectations at projection boundary
    ----------------------------------------------
      timestamp  -> timestamp[ns] non-null   (matches Sentinel)
      ticker     -> string non-null          (matches Sentinel)
      price      -> double non-null          (matches Sentinel)
      qty        -> int32 non-null           (matches Sentinel)
      aggressor  -> string non-null          (matches Sentinel)
      buy_agent  -> int64 nullable           (F2 DOCUMENTED — Sentinel string nullable)
      sell_agent -> int64 nullable           (F2 DOCUMENTED — Sentinel string nullable)

    Returns a dict report; verdict is ``A2_REAUDIT_PASS_AT_PROJECTION_BOUNDARY``
    iff F3/F4/F5 are all RESOLVED across all chunks AND F2 is the *only*
    residual divergence.
    """
    sentinel_schema = pq.read_schema(Path(sentinel_path))
    sentinel_fields = {f.name: f for f in sentinel_schema}

    per_chunk: list[dict[str, object]] = []
    overall_pass = True

    for cp in chunk_paths:
        cp = Path(cp)
        try:
            projected, report = project_parquet(cp)
            proj_fields = {f.name: f for f in projected.schema}
            per_col: dict[str, dict[str, object]] = {}

            # F3: timestamp must be ns non-null
            ts = proj_fields["timestamp"]
            per_col["timestamp"] = {
                "expected": "timestamp[ns] non-null",
                "actual": f"{ts.type} {'non-null' if not ts.nullable else 'nullable'}",
                "verdict": "F3_RESOLVED" if (ts.type == pa.timestamp("ns") and not ts.nullable)
                                          else "F3_FAIL",
            }
            # F4: qty must be int32 non-null
            q = proj_fields["qty"]
            per_col["qty"] = {
                "expected": "int32 non-null",
                "actual": f"{q.type} {'non-null' if not q.nullable else 'nullable'}",
                "verdict": "F4_RESOLVED" if (q.type == pa.int32() and not q.nullable)
                                          else "F4_FAIL",
            }
            # F5: ticker / price / aggressor non-null
            for c in ("ticker", "price", "aggressor"):
                f = proj_fields[c]
                per_col[c] = {
                    "expected": f"{sentinel_fields[c].type} non-null",
                    "actual": f"{f.type} {'non-null' if not f.nullable else 'nullable'}",
                    "verdict": "F5_RESOLVED" if (f.type == sentinel_fields[c].type
                                                  and not f.nullable)
                                              else "F5_FAIL",
                }
            # F2 carry-forward: buy_agent / sell_agent stay int64
            for c in ("buy_agent", "sell_agent"):
                f = proj_fields[c]
                expected_sentinel = sentinel_fields[c]
                per_col[c] = {
                    "expected_sentinel": f"{expected_sentinel.type} {'nullable' if expected_sentinel.nullable else 'non-null'}",
                    "actual_projected":  f"{f.type} {'nullable' if f.nullable else 'non-null'}",
                    "verdict": "F2_DOCUMENTED_CARRY_FORWARD",
                }
            chunk_pass = all(
                v["verdict"].endswith("_RESOLVED")
                or v["verdict"] == "F2_DOCUMENTED_CARRY_FORWARD"
                for v in per_col.values()
            )
            if not chunk_pass:
                overall_pass = False
            per_chunk.append({
                "chunk": str(cp),
                "rows": report.rows,
                "qty_min": report.qty_min,
                "qty_max": report.qty_max,
                "per_col": per_col,
                "chunk_pass": chunk_pass,
            })
        except (ProjectionOverflowError, ProjectionNullabilityError,
                ProjectionSchemaError) as exc:
            overall_pass = False
            per_chunk.append({
                "chunk": str(cp),
                "error": f"{type(exc).__name__}: {exc}",
                "chunk_pass": False,
            })

    verdict = (
        "A2_REAUDIT_PASS_AT_PROJECTION_BOUNDARY"
        if overall_pass
        else "A2_REAUDIT_FAIL_AT_PROJECTION_BOUNDARY"
    )
    return {
        "verdict": verdict,
        "projection_semver": PROJECTION_SEMVER,
        "sentinel": str(sentinel_path),
        "n_chunks": len(per_chunk),
        "per_chunk": per_chunk,
    }


__all__ = [
    "PROJECTION_SEMVER",
    "CANONICAL_COLUMNS",
    "ProjectionOverflowError",
    "ProjectionNullabilityError",
    "ProjectionSchemaError",
    "ProjectionReport",
    "project_table",
    "project_parquet",
    "compute_dataset_hash",
    "upgrade_manifest_header",
    "read_manifest_rows",
    "reaudit_at_projection_boundary",
]
