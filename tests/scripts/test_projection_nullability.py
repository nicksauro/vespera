"""AC3 — nullability assert + mark.

Tests:
  (i)  ProjectionNullabilityError when nulls present in mandated cols
  (ii) clean bulk passes; non-null flags asserted
  (iii) projected schema flags match Sentinel reference for canonical cols
"""
from __future__ import annotations

import pyarrow as pa

from scripts.dll_backfill_projection import (
    CANONICAL_COLUMNS,
    ProjectionNullabilityError,
    project_table,
)


def _good_storage_table(rows: int = 5) -> pa.Table:
    return pa.table({
        "timestamp":  pa.array([0] * rows, type=pa.timestamp("us")),
        "ticker":     pa.array(["WDOG23"] * rows, type=pa.string()),
        "price":      pa.array([5000.0] * rows, type=pa.float64()),
        "qty":        pa.array([1] * rows, type=pa.int64()),
        "aggressor":  pa.array(["BUY"] * rows, type=pa.string()),
        "buy_agent":  pa.array([308] * rows, type=pa.int64()),
        "sell_agent": pa.array([386] * rows, type=pa.int64()),
    })


def test_ac3_clean_bulk_passes_with_nonnull_flags():
    t = _good_storage_table(10)
    projected, report = project_table(t, source="clean")
    schema_fields = {f.name: f for f in projected.schema}
    # mandated non-null cols
    for c in ("timestamp", "ticker", "price", "qty", "aggressor"):
        assert not schema_fields[c].nullable, f"{c} should be non-null"
    # F2: agents stay nullable (parity with Sentinel 2024 string-nullable)
    assert schema_fields["buy_agent"].nullable
    assert schema_fields["sell_agent"].nullable
    assert report.null_counts["timestamp"] == 0
    assert report.rows == 10


def _table_with_null(col: str) -> pa.Table:
    base = _good_storage_table(3)
    arr = base.column(col).to_pylist()
    arr[1] = None
    if col == "timestamp":
        new_arr = pa.array(arr, type=pa.timestamp("us"))
    elif col == "qty":
        new_arr = pa.array(arr, type=pa.int64())
    elif col == "price":
        new_arr = pa.array(arr, type=pa.float64())
    else:
        new_arr = pa.array(arr, type=pa.string())
    cols = {name: base.column(name) for name in base.schema.names}
    cols[col] = new_arr
    return pa.table(cols)


def test_ac3_null_in_timestamp_raises():
    t = _table_with_null("timestamp")
    try:
        project_table(t, source="bad")
    except ProjectionNullabilityError as exc:
        assert "timestamp" in str(exc)
        return
    raise AssertionError("expected ProjectionNullabilityError")


def test_ac3_null_in_qty_raises():
    t = _table_with_null("qty")
    try:
        project_table(t, source="bad")
    except ProjectionNullabilityError as exc:
        assert "qty" in str(exc)
        return
    raise AssertionError("expected ProjectionNullabilityError")


def test_ac3_null_in_aggressor_raises():
    t = _table_with_null("aggressor")
    try:
        project_table(t, source="bad")
    except ProjectionNullabilityError as exc:
        assert "aggressor" in str(exc)
        return
    raise AssertionError("expected ProjectionNullabilityError")


def test_ac3_null_in_buy_agent_does_not_raise():
    # F2: agents stay nullable; nulls there are NOT a nullability violation.
    t = _good_storage_table(3)
    arr = t.column("buy_agent").to_pylist()
    arr[1] = None
    cols = {name: t.column(name) for name in t.schema.names}
    cols["buy_agent"] = pa.array(arr, type=pa.int64())
    t2 = pa.table(cols)
    projected, report = project_table(t2, source="agent_null_ok")
    assert report.null_counts["buy_agent"] == 1


def test_ac3_canonical_columns_constant_shape():
    assert CANONICAL_COLUMNS == (
        "timestamp", "ticker", "price", "qty",
        "aggressor", "buy_agent", "sell_agent",
    )
