"""AC2 — qty int64 -> int32 with bounds-safe assert.

Tests:
  (i)  trigger ProjectionOverflowError on int64 max+1
  (ii) clean B3 range (1..10000) passes
  (iii) post-cast type int32 non-null in projected schema
  (iv) byte-equal pre/post cast (values preserved)
"""
from __future__ import annotations

import pyarrow as pa

from scripts.dll_backfill_projection import (
    ProjectionOverflowError,
    ProjectionSchemaError,
    _INT32_MAX,
    _cast_qty_int64_to_int32,
)


def _i64(values: list[int]) -> pa.Array:
    return pa.array(values, type=pa.int64())


def test_ac2_overflow_triggers_fail_closed():
    # _INT32_MAX + 1 overflows.
    arr = _i64([1, 2, _INT32_MAX + 1])
    try:
        _cast_qty_int64_to_int32(arr, source="test")
    except ProjectionOverflowError as exc:
        msg = str(exc)
        assert "fail-closed" in msg
        assert "test" in msg
        return
    raise AssertionError("expected ProjectionOverflowError")


def test_ac2_negative_overflow_triggers_fail_closed():
    arr = _i64([-(2 ** 31) - 1, 0, 1])
    try:
        _cast_qty_int64_to_int32(arr, source="test")
    except ProjectionOverflowError:
        return
    raise AssertionError("expected ProjectionOverflowError on neg overflow")


def test_ac2_clean_b3_range_passes():
    # B3 WDOFUT empirical range: 1..10000.
    arr = _i64([1, 2, 100, 1000, 10000])
    out = _cast_qty_int64_to_int32(arr, source="test")
    assert out.type == pa.int32()
    assert out.to_pylist() == [1, 2, 100, 1000, 10000]


def test_ac2_byte_equal_values_preserved():
    arr = _i64([1, 5, 100, 9999, 10000])
    out = _cast_qty_int64_to_int32(arr, source="test")
    assert out.to_pylist() == arr.to_pylist()


def test_ac2_already_int32_passthrough():
    arr = pa.array([1, 2, 3], type=pa.int32())
    out = _cast_qty_int64_to_int32(arr, source="test")
    assert out.type == pa.int32()
    assert out.equals(arr)


def test_ac2_rejects_non_int64():
    arr = pa.array([1.0, 2.0], type=pa.float64())
    try:
        _cast_qty_int64_to_int32(arr, source="test")
    except ProjectionSchemaError:
        return
    raise AssertionError("expected ProjectionSchemaError on non-int64 qty")
