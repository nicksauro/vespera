"""Tests for BacktestBroker — slippage model + hard stop + PnL formula."""

from __future__ import annotations

from datetime import datetime

import pytest

from packages.t002_eod_unwind.adapters.exec_backtest import (
    BacktestBroker,
    BacktestCosts,
    pnl_contracts,
    WDO_MULTIPLIER,
)
from packages.t002_eod_unwind.core.signal_rule import Direction


TS = datetime(2024, 3, 15, 17, 10, 0)
TS_EXIT = datetime(2024, 3, 15, 17, 55, 0)


def test_long_pays_mid_plus_slippage() -> None:
    broker = BacktestBroker()
    # defaults: roll_half=0.5, extra_ticks=1 × 0.5 = 0.5 → slip = 1.0
    fill = broker.execute(
        direction=Direction.LONG, n_contracts=2, ts=TS, mid_price=5200.0
    )
    assert fill.price == pytest.approx(5201.0)  # 5200 + 1.0
    assert fill.qty == 2
    assert fill.reason == "entry_market"
    # fees = 2 × (0.25 + 0.35) = 1.20
    assert fill.fees_rs == pytest.approx(1.2)


def test_short_receives_mid_minus_slippage() -> None:
    broker = BacktestBroker()
    fill = broker.execute(
        direction=Direction.SHORT, n_contracts=3, ts=TS, mid_price=5200.0
    )
    assert fill.price == pytest.approx(5199.0)  # 5200 - 1.0
    assert fill.qty == -3


def test_flat_direction_raises() -> None:
    broker = BacktestBroker()
    with pytest.raises(ValueError, match="FLAT"):
        broker.execute(direction=Direction.FLAT, n_contracts=1, ts=TS, mid_price=5200.0)


def test_zero_contracts_raises() -> None:
    broker = BacktestBroker()
    with pytest.raises(ValueError, match="must be > 0"):
        broker.execute(
            direction=Direction.LONG, n_contracts=0, ts=TS, mid_price=5200.0
        )


def test_force_exit_flattens_long() -> None:
    broker = BacktestBroker()
    # holding +2 LONG — force exit sells at mid - slip
    fill = broker.force_exit(open_qty=2, ts=TS_EXIT, mid_price=5210.0)
    assert fill.price == pytest.approx(5209.0)
    assert fill.qty == -2
    assert fill.reason == "exit_hard_stop"


def test_force_exit_flattens_short() -> None:
    broker = BacktestBroker()
    # holding -3 SHORT — force exit buys at mid + slip
    fill = broker.force_exit(open_qty=-3, ts=TS_EXIT, mid_price=5190.0)
    assert fill.price == pytest.approx(5191.0)
    assert fill.qty == 3


def test_force_exit_zero_raises() -> None:
    broker = BacktestBroker()
    with pytest.raises(ValueError, match="no open position"):
        broker.force_exit(open_qty=0, ts=TS_EXIT, mid_price=5200.0)


def test_pnl_long_profit() -> None:
    """LONG at 5200, exit 5210. Profit = 10 pts × 10 R$/pt × 2 contracts - fees."""
    broker = BacktestBroker()
    entry = broker.execute(
        direction=Direction.LONG, n_contracts=2, ts=TS, mid_price=5200.0
    )  # price=5201, qty=+2, fees=1.2
    exit_ = broker.force_exit(
        open_qty=2, ts=TS_EXIT, mid_price=5210.0
    )  # price=5209, qty=-2, fees=1.2
    # gross points = (5209 - 5201) × 2 = 16 → × 10 = 160 → - 2.4 = 157.6
    pnl = pnl_contracts(entry, exit_)
    assert pnl == pytest.approx(157.6)


def test_pnl_short_profit_on_price_drop() -> None:
    """SHORT at 5200, exit 5190. Profit = 10 pts × 10 R$/pt - fees."""
    broker = BacktestBroker()
    entry = broker.execute(
        direction=Direction.SHORT, n_contracts=1, ts=TS, mid_price=5200.0
    )  # price=5199, qty=-1, fees=0.6
    exit_ = broker.force_exit(
        open_qty=-1, ts=TS_EXIT, mid_price=5190.0
    )  # price=5191, qty=+1, fees=0.6
    # gross points = (5191 - 5199) × (-1) = 8 → × 10 = 80 → - 1.2 = 78.8
    pnl = pnl_contracts(entry, exit_)
    assert pnl == pytest.approx(78.8)


def test_determinism() -> None:
    broker = BacktestBroker()
    runs = [
        broker.execute(direction=Direction.LONG, n_contracts=2, ts=TS, mid_price=5200.0)
        for _ in range(3)
    ]
    assert all(r == runs[0] for r in runs)


def test_custom_costs_override() -> None:
    broker = BacktestBroker(
        costs=BacktestCosts(
            brokerage_per_contract_side_rs=1.0,
            exchange_fees_per_contract_side_rs=0.0,
            roll_spread_half_points=0.0,
            slippage_extra_ticks=0,
        )
    )
    fill = broker.execute(
        direction=Direction.LONG, n_contracts=1, ts=TS, mid_price=5200.0
    )
    assert fill.price == pytest.approx(5200.0)  # no slippage
    assert fill.fees_rs == pytest.approx(1.0)


def test_wdo_multiplier_constant() -> None:
    """Sanity check against DOMAIN_GLOSSARY — R$10/ponto."""
    assert WDO_MULTIPLIER == 10.0
