"""T002.6 T1 — Unit tests for feed_realtape (Phase F real-tape replay).

Per Aria T0b conditions C-A1..C-A6 + Beckett T0c C-B2 + Nova spec §1-§5:

C-A1 — replay helper INSIDE closure body (verified at integration; here we
       exercise the helper interface in isolation).
C-A2 — slippage at fill-event materialization (per-fill API).
C-A3 — `enabled_for_phase` gate testable for both F-enabled AND F-disabled
       deterministic paths.
C-A4 — per-session flags propagated through detector helper.
C-A5 — cross_trade default False historic regime + cross_trade_pct=0.0.
C-B2 — lazy per-session loading; no eager full-window load.

Article IV: every test cites the source spec section.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from pathlib import Path

import pandas as pd
import pytest

from packages.t002_eod_unwind.cpcv_harness import (
    augment_events_with_microstructure_flags,
)
from packages.t002_eod_unwind.feed_realtape import (
    detect_circuit_breaker_fired,
    detect_rollover_window,
    detect_session_microstructure_flags,
    draw_latency_ms,
    latency_slippage_pts,
    load_session_trades,
    replay_event_walk,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarLoader


_PARQUET_ROOT = Path("data/in_sample")
_SAMPLE_SESSION = date(2024, 1, 2)  # First WDO session in 2024 in-sample window.


# =====================================================================
# §3 — Lazy per-session loader (Beckett C-B2)
# =====================================================================
@pytest.mark.skipif(
    not _PARQUET_ROOT.exists(), reason="parquet root absent in this checkout"
)
def test_load_session_trades_returns_session_scoped_frame():
    """C-B2 — lazy load returns a single-session frame, NOT the full month."""
    df = load_session_trades(_SAMPLE_SESSION, _PARQUET_ROOT)
    assert not df.empty, "expected non-empty session"
    # All rows belong to the target session date.
    unique_dates = set(df["ts"].dt.date.unique())
    assert unique_dates == {_SAMPLE_SESSION}, (
        f"lazy load leaked rows from other dates: {unique_dates}"
    )
    # Required columns present (Mira §3.2).
    required = {"ts", "price", "qty", "aggressor"}
    assert required.issubset(df.columns), f"missing columns: {required - set(df.columns)}"


@pytest.mark.skipif(
    not _PARQUET_ROOT.exists(), reason="parquet root absent in this checkout"
)
def test_load_session_trades_empty_session_returns_empty_frame():
    """Empty/holiday session returns empty DataFrame, no exception."""
    # 2024-01-01 = New Year holiday; no trades.
    df = load_session_trades(date(2024, 1, 1), _PARQUET_ROOT)
    assert df.empty
    assert set(df.columns) == {"ts", "price", "qty", "aggressor"}


def test_load_session_trades_missing_parquet_raises():
    """Anti-Article-IV — missing parquet escalates, no neutral fallback."""
    with pytest.raises(FileNotFoundError):
        load_session_trades(date(1999, 1, 1), _PARQUET_ROOT)


# =====================================================================
# §4 — Microstructure flag detectors (Nova spec verbatim)
# =====================================================================
def test_detect_rollover_window_basic():
    """Nova §2.3 pseudocode — D-3..D-1 detection skipping holidays."""
    expirations = [date(2026, 4, 1)]  # Wednesday
    holidays: list[date] = []
    # D-1 = 2026-03-31 (Tuesday); D-2 = 2026-03-30 (Monday); D-3 = 2026-03-27 (Friday).
    assert detect_rollover_window(date(2026, 3, 31), wdo_expirations=expirations, br_holidays=holidays)
    assert detect_rollover_window(date(2026, 3, 30), wdo_expirations=expirations, br_holidays=holidays)
    assert detect_rollover_window(date(2026, 3, 27), wdo_expirations=expirations, br_holidays=holidays)
    # D-4 = 2026-03-26 (Thursday) — outside window.
    assert not detect_rollover_window(date(2026, 3, 26), wdo_expirations=expirations, br_holidays=holidays)
    # Unrelated date.
    assert not detect_rollover_window(date(2026, 5, 15), wdo_expirations=expirations, br_holidays=holidays)


def test_detect_rollover_window_skips_holidays():
    """Nova §2.3 — holidays skipped during D-3..D-1 walk-back."""
    # 2026-03-30 Monday treated as holiday → D-3 walks back further.
    expirations = [date(2026, 4, 1)]
    holidays = [date(2026, 3, 30)]
    # Walk back: 03-31 (D-1), 03-30 SKIP, 03-27 (D-2 effective), 03-26 (D-3 effective).
    assert detect_rollover_window(date(2026, 3, 31), wdo_expirations=expirations, br_holidays=holidays)
    assert detect_rollover_window(date(2026, 3, 27), wdo_expirations=expirations, br_holidays=holidays)
    assert detect_rollover_window(date(2026, 3, 26), wdo_expirations=expirations, br_holidays=holidays)
    # 03-30 itself is the holiday → skipped → not "in window" by detection
    # semantics (window walks only valid trading days).
    assert not detect_rollover_window(date(2026, 3, 30), wdo_expirations=expirations, br_holidays=holidays)


def test_detect_circuit_breaker_fired_no_gap_returns_false():
    """Nova §4.2 — clean continuous tape returns False."""
    # 1 trade per minute from 09:30 to 17:30 — no gap > 30 min.
    base = datetime(2024, 1, 2, 9, 30, 0)
    rows = []
    for i in range(8 * 60):  # 8 hours
        rows.append({
            "ts": pd.Timestamp(base + timedelta(minutes=i)),
            "price": 5000.0,
            "qty": 1,
            "aggressor": "BUY",
        })
    df = pd.DataFrame(rows)
    assert detect_circuit_breaker_fired(df) is False


def test_detect_circuit_breaker_fired_gap_returns_true():
    """Nova §4.2 — continuous gap >30 min within window triggers True."""
    base = datetime(2024, 1, 2, 9, 30, 0)
    rows = [
        {"ts": pd.Timestamp(base), "price": 5000.0, "qty": 1, "aggressor": "BUY"},
        # 45-min gap (no trades at all).
        {"ts": pd.Timestamp(base + timedelta(minutes=45)), "price": 5000.0, "qty": 1, "aggressor": "BUY"},
    ]
    df = pd.DataFrame(rows)
    assert detect_circuit_breaker_fired(df) is True


def test_detect_session_microstructure_flags_returns_full_dict():
    """C-A4/C-A5 — flag dict carries all 5 Nova fields."""
    df = pd.DataFrame({
        "ts": [pd.Timestamp(datetime(2024, 1, 2, 10, 0, 0))],
        "price": [5000.0],
        "qty": [1],
        "aggressor": ["BUY"],
    })
    flags = detect_session_microstructure_flags(df, date(2024, 1, 2))
    assert "rollover_window" in flags
    assert "circuit_breaker_fired" in flags
    assert "cross_trade_pct" in flags
    assert "rlp_active_hours" in flags
    assert "rlp_flag_available_historic" in flags
    # C-A5: cross_trade default False historic regime → cross_trade_pct=0.0.
    assert flags["cross_trade_pct"] == 0.0
    assert flags["rlp_flag_available_historic"] is False


# =====================================================================
# §5 — Latency model (Aria C-A3 deterministic both paths)
# =====================================================================
def test_draw_latency_ms_phase_F_enabled_returns_positive():
    """C-A3 — F-enabled triggers lognormal draw; deterministic > 0."""
    config = {
        "enabled_for_phase": ["F"],
        "current_phase": "F",
        "components": {
            "fill": {"mu": 0.0, "sigma": 0.84, "p50_ms": 1.0},
        },
    }
    seed = b"\x00" * 8
    latency_a = draw_latency_ms(seed=seed, component="fill", config=config)
    latency_b = draw_latency_ms(seed=seed, component="fill", config=config)
    assert latency_a > 0.0
    assert latency_a == latency_b, "deterministic across calls with same seed"


def test_draw_latency_ms_phase_F_disabled_returns_zero():
    """C-A3 — F-disabled returns 0.0 deterministically."""
    config = {
        "enabled_for_phase": [],  # nothing enabled
        "current_phase": "E",
        "components": {"fill": {"mu": 0.0, "sigma": 0.84}},
    }
    seed = b"\x01" * 8
    latency = draw_latency_ms(seed=seed, component="fill", config=config)
    assert latency == 0.0


def test_latency_slippage_pts_phase_disabled_returns_zero():
    """C-A3 — slippage formula returns 0.0 when phase disabled."""
    config = {"enabled_for_phase": ["F"], "current_phase": "E"}
    pts = latency_slippage_pts(
        seed=b"\x00" * 8,
        component="fill",
        mid_at_decision=5000.0,
        mid_at_fill_after_latency=5000.5,
        sign=1,
        config=config,
    )
    assert pts == 0.0


def test_latency_slippage_pts_formula_sign_convention():
    """Beckett §3.1 — sign × (mid_decision − mid_fill_after_latency)."""
    config = {"enabled_for_phase": ["F"], "current_phase": "F"}
    # LONG entry: price moved UP during latency → adverse → cost > 0.
    pts_long = latency_slippage_pts(
        seed=b"\x00" * 8,
        component="order_submit",
        mid_at_decision=5000.0,
        mid_at_fill_after_latency=5000.5,
        sign=1,
        config=config,
    )
    assert pts_long == pytest.approx(-0.5)
    # SHORT entry: price moved UP → favorable for short.
    pts_short = latency_slippage_pts(
        seed=b"\x00" * 8,
        component="order_submit",
        mid_at_decision=5000.0,
        mid_at_fill_after_latency=5000.5,
        sign=-1,
        config=config,
    )
    assert pts_short == pytest.approx(0.5)


# =====================================================================
# §3.3 — Real-tape replay (triple-barrier precedence + auction boundary)
# =====================================================================
def _build_synthetic_walk_frame(
    base_ts: datetime,
    n_ticks: int = 60,
    drift_per_tick: float = 0.0,
    base_price: float = 5000.0,
) -> pd.DataFrame:
    """Build a synthetic intra-test fixture (NOT real tape) — used only to
    exercise replay_event_walk semantics without parquet IO."""
    rows = []
    for i in range(n_ticks):
        rows.append({
            "ts": pd.Timestamp(base_ts + timedelta(seconds=i * 30)),
            "price": float(base_price + drift_per_tick * i),
            "qty": 1,
            "aggressor": "BUY",
        })
    return pd.DataFrame(rows)


def test_replay_event_walk_pt_hit_long():
    """Mira §2.1 — PT triggers on price >= entry + pt_offset (LONG)."""
    entry_ts = datetime(2024, 1, 2, 17, 0, 0)
    auction_cutoff = datetime(2024, 1, 2, 17, 55, 0)
    walk = _build_synthetic_walk_frame(entry_ts, n_ticks=20, drift_per_tick=0.5)
    config = {"enabled_for_phase": [], "current_phase": "E"}  # latency off
    exit_price, reason, ticks = replay_event_walk(
        trades=walk,
        entry_ts=entry_ts,
        entry_price=5000.0,
        pt_offset=2.0,
        sl_offset=2.0,
        sign=1,
        auction_cutoff_ts=auction_cutoff,
        latency_config=config,
        seed_inputs=(date(2024, 1, 2), "T1-17:00-0", "T1"),
    )
    assert reason == "pt_hit"
    assert exit_price == pytest.approx(5002.0, abs=1e-9)
    assert ticks > 0


def test_replay_event_walk_sl_hit_long():
    """Mira §2.1 — SL triggers on price <= entry - sl_offset (LONG)."""
    entry_ts = datetime(2024, 1, 2, 17, 0, 0)
    auction_cutoff = datetime(2024, 1, 2, 17, 55, 0)
    walk = _build_synthetic_walk_frame(entry_ts, n_ticks=20, drift_per_tick=-0.5)
    config = {"enabled_for_phase": [], "current_phase": "E"}
    exit_price, reason, ticks = replay_event_walk(
        trades=walk,
        entry_ts=entry_ts,
        entry_price=5000.0,
        pt_offset=2.0,
        sl_offset=2.0,
        sign=1,
        auction_cutoff_ts=auction_cutoff,
        latency_config=config,
        seed_inputs=(date(2024, 1, 2), "T1-17:00-0", "T1"),
    )
    assert reason == "sl_hit"
    assert exit_price == pytest.approx(4998.0, abs=1e-9)


def test_replay_event_walk_vertical_exit_at_auction_boundary():
    """Nova §3.2-α — vertical exit at last non-auction trade < 17:55:00 BRT."""
    entry_ts = datetime(2024, 1, 2, 17, 50, 0)
    auction_cutoff = datetime(2024, 1, 2, 17, 55, 0)
    # Tape spans 17:50..18:00 — only trades < 17:55 should be considered.
    rows = []
    base = entry_ts
    for i in range(20):  # 20 trades, 30s apart, runs from 17:50 → 17:59:30.
        rows.append({
            "ts": pd.Timestamp(base + timedelta(seconds=i * 30)),
            "price": 5000.0 + 0.1 * i,
            "qty": 1,
            "aggressor": "BUY",
        })
    walk = pd.DataFrame(rows)
    config = {"enabled_for_phase": [], "current_phase": "E"}
    exit_price, reason, ticks = replay_event_walk(
        trades=walk,
        entry_ts=entry_ts,
        entry_price=5000.0,
        pt_offset=10.0,  # too wide to hit
        sl_offset=10.0,
        sign=1,
        auction_cutoff_ts=auction_cutoff,
        latency_config=config,
        seed_inputs=(date(2024, 1, 2), "T1-17:50-0", "T1"),
    )
    assert reason == "vertical"
    # Last trade < 17:55:00 BRT — at most 9 trades visible (17:50, 17:50:30,
    # ..., 17:54:30); auction print 17:55:00 excluded.
    assert ticks <= 10
    # Exit price equals last visible trade price (drift +0.1 per tick).
    assert exit_price == pytest.approx(5000.0 + 0.1 * (ticks - 1), abs=1e-9)


# =====================================================================
# C-A4 — Per-session flag augmentation BEFORE engine partition
# =====================================================================
def test_augment_events_with_microstructure_flags_adds_three_columns():
    """C-A4 — adds rollover_window + circuit_breaker_fired + cross_trade
    columns, NOT mutating the originals."""
    calendar = CalendarLoader.load(Path("config/calendar/2024-2027.yaml"))
    events = pd.DataFrame({
        "t_start": [pd.Timestamp(datetime(2024, 9, 2, 17, 0, 0))],
        "t_end": [pd.Timestamp(datetime(2024, 9, 2, 17, 55, 0))],
        "session": [date(2024, 9, 2)],
        "trial_id": ["T1"],
        "entry_window": ["17:00"],
    })
    out = augment_events_with_microstructure_flags(events, calendar=calendar)
    assert "rollover_window" in out.columns
    assert "circuit_breaker_fired" in out.columns
    assert "cross_trade" in out.columns
    # Aria C-A5 — historic regime defaults False.
    assert out["cross_trade"].iloc[0] is False or out["cross_trade"].iloc[0] == False  # noqa: E712
    # Lazy default — CB stays False without eager scan.
    assert out["circuit_breaker_fired"].iloc[0] == False  # noqa: E712


def test_augment_events_with_microstructure_flags_empty_frame_preserves_schema():
    """Empty input — preserves schema with empty flag columns."""
    calendar = CalendarLoader.load(Path("config/calendar/2024-2027.yaml"))
    events = pd.DataFrame(columns=["t_start", "t_end", "session", "trial_id", "entry_window"])
    out = augment_events_with_microstructure_flags(events, calendar=calendar)
    assert "rollover_window" in out.columns
    assert "circuit_breaker_fired" in out.columns
    assert "cross_trade" in out.columns
    assert len(out) == 0


def test_replay_event_walk_empty_tape_returns_vertical_at_entry():
    """Empty session tape → degenerate vertical exit at entry_price."""
    walk = pd.DataFrame(columns=["ts", "price", "qty", "aggressor"])
    config = {"enabled_for_phase": [], "current_phase": "E"}
    exit_price, reason, ticks = replay_event_walk(
        trades=walk,
        entry_ts=datetime(2024, 1, 2, 17, 0, 0),
        entry_price=5000.0,
        pt_offset=2.0,
        sl_offset=2.0,
        sign=1,
        auction_cutoff_ts=datetime(2024, 1, 2, 17, 55, 0),
        latency_config=config,
        seed_inputs=(date(2024, 1, 2), "T1-17:00-0", "T1"),
    )
    assert reason == "vertical"
    assert exit_price == 5000.0
    assert ticks == 0
