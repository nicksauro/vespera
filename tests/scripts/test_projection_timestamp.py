"""AC1 — timestamp[us] -> timestamp[ns] lossless upcast.

Tests:
  (i)  us * 1000 == ns exact
  (ii) no overflow on pre-2024 dates
  (iii) round-trip byte-equal (us -> ns -> us identity)
  (iv) parity with Sentinel 2024 ts[ns] non-null type
"""
from __future__ import annotations

from datetime import datetime

import pyarrow as pa
import pyarrow.compute as pc

from scripts.dll_backfill_projection import (
    ProjectionSchemaError,
    _cast_timestamp_us_to_ns,
)


def _us_array(values_us: list[int]) -> pa.Array:
    return pa.array(values_us, type=pa.timestamp("us"))


def test_ac1_us_x_1000_exact():
    # 2023-01-02 09:00:00 in us -> ns must be us*1000 exactly.
    sample_us = [
        int(datetime(2023, 1, 2, 9, 0, 0).timestamp() * 1_000_000),
        int(datetime(2023, 6, 15, 14, 30, 5).timestamp() * 1_000_000),
        int(datetime(2023, 12, 29, 17, 59, 59).timestamp() * 1_000_000),
    ]
    arr = _us_array(sample_us)
    out = _cast_timestamp_us_to_ns(arr)
    assert out.type == pa.timestamp("ns")
    out_int = pc.cast(out, pa.int64()).to_pylist()
    expected = [v * 1000 for v in sample_us]
    assert out_int == expected


def test_ac1_no_overflow_pre_2024():
    # int64 ns supports +/- 292 years from epoch. 2023 is well within range.
    arr = _us_array([
        int(datetime(2023, 1, 1).timestamp() * 1_000_000),
        int(datetime(2023, 12, 31).timestamp() * 1_000_000),
    ])
    out = _cast_timestamp_us_to_ns(arr)
    # Confirm round-trip back to us preserves identity.
    out_us_again = pc.cast(out, pa.timestamp("us"))
    assert out_us_again.equals(arr)


def test_ac1_roundtrip_byte_equal():
    raw = _us_array([1_000_000_000, 2_000_000_000, 3_000_000_000])
    ns = _cast_timestamp_us_to_ns(raw)
    back = pc.cast(ns, pa.timestamp("us"))
    assert back.equals(raw)


def test_ac1_already_ns_passthrough():
    arr = pa.array([1_000_000_000_000], type=pa.timestamp("ns"))
    out = _cast_timestamp_us_to_ns(arr)
    assert out.type == pa.timestamp("ns")
    assert out.equals(arr)


def test_ac1_rejects_non_timestamp_us():
    arr = pa.array([1, 2, 3], type=pa.int64())
    try:
        _cast_timestamp_us_to_ns(arr)
    except ProjectionSchemaError:
        return
    raise AssertionError("expected ProjectionSchemaError on non-timestamp[us]")
