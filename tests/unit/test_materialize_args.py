"""Unit tests — CLI parsing and parquet schema for materialize_parquet.py.

Story: T002.0a (AC4 argparse + schema)
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import materialize_parquet as mp  # noqa: E402


# ---------------------------------------------------------------------------
# parse_args — canonical form
# ---------------------------------------------------------------------------

def test_parse_args_canonical():
    args = mp.parse_args([
        "--start-date", "2024-01-02",
        "--end-date", "2024-06-30",
        "--ticker", "WDO",
        "--output-dir", "data/in_sample",
    ])
    assert args.start_date == date(2024, 1, 2)
    assert args.end_date == date(2024, 6, 30)
    assert args.ticker == "WDO"
    assert args.output_dir == Path("data/in_sample")
    assert args.dry_run is False


def test_parse_args_short_aliases():
    """--start and --end aliases work."""
    args = mp.parse_args([
        "--start", "2024-01-02",
        "--end", "2024-06-30",
        "--ticker", "WDO",
        "--out", "data/in_sample",
    ])
    assert args.start_date == date(2024, 1, 2)
    assert args.end_date == date(2024, 6, 30)


def test_parse_args_dry_run_flag():
    args = mp.parse_args([
        "--start-date", "2024-03-01",
        "--end-date", "2024-03-15",
        "--ticker", "WIN",
        "--dry-run",
    ])
    assert args.dry_run is True


def test_parse_args_rejects_start_after_end():
    with pytest.raises(SystemExit):
        mp.parse_args([
            "--start-date", "2024-06-30",
            "--end-date", "2024-01-02",
            "--ticker", "WDO",
        ])


def test_parse_args_rejects_empty_ticker():
    with pytest.raises(SystemExit):
        mp.parse_args([
            "--start-date", "2024-01-02",
            "--end-date", "2024-06-30",
            "--ticker", "   ",
        ])


def test_parse_args_rejects_bad_date_format():
    with pytest.raises(SystemExit):
        mp.parse_args([
            "--start-date", "01/02/2024",
            "--end-date", "2024-06-30",
            "--ticker", "WDO",
        ])


# ---------------------------------------------------------------------------
# iter_month_windows
# ---------------------------------------------------------------------------

def test_iter_month_windows_single_month():
    mws = mp.iter_month_windows(date(2024, 3, 5), date(2024, 3, 20))
    assert len(mws) == 1
    assert mws[0].year == 2024
    assert mws[0].month == 3
    assert mws[0].start == date(2024, 3, 5)
    assert mws[0].end_inclusive == date(2024, 3, 20)


def test_iter_month_windows_spans_multiple_months():
    mws = mp.iter_month_windows(date(2024, 1, 2), date(2024, 3, 15))
    assert [m.label for m in mws] == ["2024-01", "2024-02", "2024-03"]
    assert mws[0].start == date(2024, 1, 2)
    assert mws[0].end_inclusive == date(2024, 1, 31)
    assert mws[1].start == date(2024, 2, 1)
    assert mws[1].end_inclusive == date(2024, 2, 29)  # leap year
    assert mws[2].start == date(2024, 3, 1)
    assert mws[2].end_inclusive == date(2024, 3, 15)


def test_iter_month_windows_in_sample_18_months():
    """Epic T002.0 in-sample: 2024-01-02 .. 2025-06-30 -> 18 monthly partitions."""
    mws = mp.iter_month_windows(date(2024, 1, 2), date(2025, 6, 30))
    assert len(mws) == 18
    labels = [m.label for m in mws]
    assert labels[0] == "2024-01"
    assert labels[-1] == "2025-06"


# ---------------------------------------------------------------------------
# Parquet schema (strict)
# ---------------------------------------------------------------------------

def test_parquet_schema_strict():
    import pyarrow as pa
    schema = mp._build_parquet_schema()

    names = [f.name for f in schema]
    assert names == [
        "timestamp", "ticker", "price", "qty",
        "aggressor", "buy_agent", "sell_agent",
    ]

    # timestamp must be naive (tz=None) with ns unit — R2 BRT-naive invariant
    ts_type = schema.field("timestamp").type
    assert pa.types.is_timestamp(ts_type)
    assert ts_type.unit == "ns"
    assert ts_type.tz is None

    assert pa.types.is_string(schema.field("ticker").type)
    assert schema.field("price").type == pa.float64()
    assert schema.field("qty").type == pa.int32()
    assert pa.types.is_string(schema.field("aggressor").type)

    # buy_agent / sell_agent nullable, string
    assert schema.field("buy_agent").nullable is True
    assert schema.field("sell_agent").nullable is True
    assert pa.types.is_string(schema.field("buy_agent").type)


# ---------------------------------------------------------------------------
# Manifest columns (fixed order)
# ---------------------------------------------------------------------------

def test_manifest_columns_fixed_order():
    """Riven Condition 3: 'phase' column inserted after 'ticker'."""
    assert mp.MANIFEST_COLUMNS == (
        "path",
        "rows",
        "sha256",
        "start_ts_brt",
        "end_ts_brt",
        "ticker",
        "phase",
        "generated_at_brt",
    )


# ---------------------------------------------------------------------------
# Phase classifier (Riven Condition 3)
# ---------------------------------------------------------------------------

def test_classify_phase_warmup():
    assert mp.classify_phase(date(2024, 1, 2), date(2024, 1, 31)) == "warmup"
    assert mp.classify_phase(date(2024, 6, 1), date(2024, 6, 30)) == "warmup"


def test_classify_phase_in_sample():
    assert mp.classify_phase(date(2024, 7, 1), date(2024, 7, 31)) == "in_sample"
    assert mp.classify_phase(date(2025, 6, 1), date(2025, 6, 30)) == "in_sample"


def test_classify_phase_hold_out():
    assert mp.classify_phase(date(2025, 7, 1), date(2025, 7, 31)) == "hold_out"
    assert mp.classify_phase(date(2026, 4, 1), date(2026, 4, 21)) == "hold_out"


def test_classify_phase_boundary_cross_rejected():
    """Cross warmup -> in_sample cut raises ValueError (partition bug)."""
    with pytest.raises(ValueError):
        mp.classify_phase(date(2024, 6, 25), date(2024, 7, 5))
    with pytest.raises(ValueError):
        mp.classify_phase(date(2025, 6, 25), date(2025, 7, 5))


def test_classify_phase_rejects_outside_known_bounds():
    """Windows before warmup or after hold-out fall outside known phases."""
    with pytest.raises(ValueError):
        mp.classify_phase(date(2023, 12, 1), date(2023, 12, 31))
    with pytest.raises(ValueError):
        mp.classify_phase(date(2026, 5, 1), date(2026, 5, 31))


# ---------------------------------------------------------------------------
# Month output path convention
# ---------------------------------------------------------------------------

def test_month_output_path_layout():
    mw = mp.MonthWindow(year=2024, month=3, start=date(2024, 3, 1),
                        end_inclusive=date(2024, 3, 31))
    p = mp._month_output_path(Path("data/in_sample"), "WDO", mw)
    assert p == Path("data/in_sample/year=2024/month=03/wdo-2024-03.parquet")


# ---------------------------------------------------------------------------
# Error sanitization (Riven Condition 2)
# ---------------------------------------------------------------------------

def test_sanitize_error_scrubs_password():
    """Any 'password=<secret>' fragment is replaced with 'password=***'."""
    raw = "could not connect: host=localhost port=5433 password=Sup3rSecret! user=x"
    out = mp._sanitize_error_message(raw)
    assert "Sup3rSecret!" not in out
    assert "password=***" in out


def test_sanitize_error_scrubs_password_with_quotes():
    raw = "psycopg2.OperationalError: FATAL: password=ABCxyz123 authentication failed"
    out = mp._sanitize_error_message(raw)
    assert "ABCxyz123" not in out
    assert "password=***" in out


def test_sanitize_error_scrubs_dsn_string():
    raw = "connection failure dsn='host=x password=foo user=y' returned null"
    out = mp._sanitize_error_message(raw)
    assert "password=foo" not in out
    assert "dsn=<redacted>" in out


def test_sanitize_error_leaves_benign_message_unchanged():
    raw = "connection timed out after 30s"
    assert mp._sanitize_error_message(raw) == raw
