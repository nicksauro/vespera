"""End-to-end backtest integration — 1 synthetic session.

Assembles: HistoricalTradesReplay → SessionState → FeatureComputer →
compute_signal (T1) → BacktestBroker → force_exit at 17:55 → PnL.

AC11: manual-calculation parity. AC12: determinism across 3 runs.

Event-driven pattern: snapshot_at fires AT the entry_ts, consuming only
trades with ts <= entry_ts. This mirrors the live loop contract.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import NamedTuple

import pytest

from packages.t002_eod_unwind.adapters.exec_backtest import (
    BacktestBroker,
    Fill,
    pnl_contracts,
)
from packages.t002_eod_unwind.adapters.feed_historical import HistoricalTradesReplay
from packages.t002_eod_unwind.core.feature_computer import (
    PercentileBands,
    compute_features,
)
from packages.t002_eod_unwind.core.session_state import (
    SessionState,
    Trade,
)
from packages.t002_eod_unwind.core.signal_rule import (
    Direction,
    Signal,
    TrialParams,
    compute_signal,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData


DEFAULT_BANDS = PercentileBands(p20=0.3, p60=0.6, p80=0.9)


def _empty_cal() -> CalendarData:
    return CalendarData(
        version="test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


class DayResult(NamedTuple):
    signal: Signal
    entry_fill: Fill | None
    exit_fill: Fill | None
    pnl_rs: float | None


def _run_day(
    trades: list[Trade],
    entry_ts: datetime,
    exit_ts: datetime,
    atr_20d: float = 20.0,
    bands: PercentileBands = DEFAULT_BANDS,
    trial: TrialParams | None = None,
) -> DayResult:
    """Event-driven backtest of a single day.

    Contract matches live loop:
      - on every TradeEvent, push into SessionState
      - when event.ts >= entry_ts AND signal not yet fired, snapshot at entry_ts
        and compute signal
      - at exit_ts, force-exit any open position using the last known price
    """
    trial = trial or TrialParams(trial_id="T1", magnitude_threshold=bands.p60)
    state = SessionState()
    broker = BacktestBroker()

    signal: Signal | None = None
    entry_fill: Fill | None = None
    mid_at_entry: float | None = None

    replay = HistoricalTradesReplay(trades, _empty_cal())

    for event in replay:
        # snapshot BEFORE pushing any trade whose ts > entry_ts
        if signal is None and event.ts > entry_ts and state.last_ts is not None:
            snap = state.snapshot_at(entry_ts)
            feats = compute_features(
                snap, atr_20d=atr_20d, magnitude_bands=bands, atr_ratio_bands=bands
            )
            signal = compute_signal(feats, bands, trial)
            mid_at_entry = state.last_price
            if signal.direction != Direction.FLAT and mid_at_entry is not None:
                entry_fill = broker.execute(
                    direction=signal.direction,
                    n_contracts=1,
                    ts=entry_ts,
                    mid_price=mid_at_entry,
                )
        state.on_trade(Trade(ts=event.ts, price=event.price, qty=event.qty))

    # end-of-stream: fire signal if we haven't yet (e.g. no trades after entry_ts)
    if signal is None and state.last_ts is not None and state.last_ts >= entry_ts:
        snap = state.snapshot_at(entry_ts) if state.last_ts == entry_ts else state.snapshot_at(state.last_ts)
        feats = compute_features(
            snap, atr_20d=atr_20d, magnitude_bands=bands, atr_ratio_bands=bands
        )
        signal = compute_signal(feats, bands, trial)

    assert signal is not None, "signal must have fired by end of day"

    exit_fill: Fill | None = None
    pnl: float | None = None
    if entry_fill is not None:
        assert state.last_price is not None
        exit_fill = broker.force_exit(
            open_qty=entry_fill.qty, ts=exit_ts, mid_price=state.last_price
        )
        pnl = pnl_contracts(entry_fill, exit_fill)

    return DayResult(signal=signal, entry_fill=entry_fill, exit_fill=exit_fill, pnl_rs=pnl)


# ---------- AC11: parity com cálculo manual ----------


def test_fade_short_within_regime_manual_pnl() -> None:
    """open=5200, close@17:10=5215 (flow +15, magnitude=15/20=0.75 > P60=0.6),
    ATR_day_so_far = 5215-5200 = 15, ratio=15/20=0.75 ∈ [0.3, 0.9] ⇒ SHORT entra.
    Mid-exit = 5205 ⇒ SHORT lucra.

    Manual PnL:
      entry_price = 5215 - 1.0 (slip) = 5214; qty=-1; fees=0.60
      exit_price  = 5205 + 1.0 (slip) = 5206; qty=+1; fees=0.60
      gross_points = (5206 - 5214) × (-1) = 8 pts
      gross_rs = 8 × 10 = R$80
      net = 80 - 1.20 = R$78.80
    """
    d = date(2024, 3, 15)
    trades = [
        Trade(ts=datetime(d.year, d.month, d.day, 9, 30), price=5200.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 10), price=5215.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 54), price=5205.0, qty=1),
    ]
    res = _run_day(
        trades,
        entry_ts=datetime(d.year, d.month, d.day, 17, 10),
        exit_ts=datetime(d.year, d.month, d.day, 17, 55),
    )
    assert res.signal.direction == Direction.SHORT
    assert res.signal.reason == "entered_fade_short"
    assert res.entry_fill is not None
    assert res.entry_fill.price == pytest.approx(5214.0)
    assert res.entry_fill.qty == -1
    assert res.exit_fill is not None
    assert res.exit_fill.price == pytest.approx(5206.0)
    assert res.pnl_rs == pytest.approx(78.8)


def test_fade_long_within_regime_manual_pnl() -> None:
    """Espelho do anterior: close<open ⇒ LONG fade."""
    d = date(2024, 3, 15)
    trades = [
        Trade(ts=datetime(d.year, d.month, d.day, 9, 30), price=5200.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 10), price=5185.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 54), price=5195.0, qty=1),
    ]
    res = _run_day(
        trades,
        entry_ts=datetime(d.year, d.month, d.day, 17, 10),
        exit_ts=datetime(d.year, d.month, d.day, 17, 55),
    )
    assert res.signal.direction == Direction.LONG
    # entry: 5185 + 1.0 = 5186, qty=+1
    # exit:  5195 - 1.0 = 5194, qty=-1
    # gross_points = (5194 - 5186) × (+1) = 8 → × 10 = 80 → - 1.20 = 78.80
    assert res.pnl_rs == pytest.approx(78.8)


# ---------- AC11: FLAT paths ----------


def test_no_entry_if_magnitude_below_threshold() -> None:
    d = date(2024, 3, 15)
    trades = [
        Trade(ts=datetime(d.year, d.month, d.day, 9, 30), price=5200.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 10), price=5202.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 54), price=5201.0, qty=1),
    ]
    res = _run_day(
        trades,
        entry_ts=datetime(d.year, d.month, d.day, 17, 10),
        exit_ts=datetime(d.year, d.month, d.day, 17, 55),
    )
    assert res.signal.direction == Direction.FLAT
    assert res.signal.reason == "magnitude_below_threshold"
    assert res.entry_fill is None
    assert res.pnl_rs is None


def test_no_entry_if_regime_filter_rejects() -> None:
    """ATR_day explode (high-low gigante) ⇒ atr_ratio > P80 ⇒ FLAT."""
    d = date(2024, 3, 15)
    trades = [
        Trade(ts=datetime(d.year, d.month, d.day, 9, 30), price=5200.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 10, 0), price=5250.0, qty=1),  # high
        Trade(ts=datetime(d.year, d.month, d.day, 12, 0), price=5160.0, qty=1),  # low
        Trade(ts=datetime(d.year, d.month, d.day, 17, 10), price=5215.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 54), price=5220.0, qty=1),
    ]
    res = _run_day(
        trades,
        entry_ts=datetime(d.year, d.month, d.day, 17, 10),
        exit_ts=datetime(d.year, d.month, d.day, 17, 55),
    )
    # ATR_day = 5250-5160 = 90, ratio = 90/20 = 4.5 > P80 (0.9) ⇒ FLAT
    assert res.signal.direction == Direction.FLAT
    assert res.signal.reason == "atr_ratio_outside_regime"


# ---------- AC12: determinism ----------


def test_determinism_three_runs() -> None:
    """Same synthetic input across 3 executions yields identical results."""
    d = date(2024, 3, 15)
    trades = [
        Trade(ts=datetime(d.year, d.month, d.day, 9, 30), price=5200.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 10), price=5215.0, qty=1),
        Trade(ts=datetime(d.year, d.month, d.day, 17, 54), price=5205.0, qty=1),
    ]
    runs = [
        _run_day(
            trades,
            entry_ts=datetime(d.year, d.month, d.day, 17, 10),
            exit_ts=datetime(d.year, d.month, d.day, 17, 55),
        )
        for _ in range(3)
    ]
    assert all(r == runs[0] for r in runs)
