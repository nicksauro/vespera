"""BacktestBroker — layer 5 backtest execution adapter.

Deterministic slippage: Roll_spread_half + 1 tick worst-case (Beckett
default). Fees use conservative defaults (Nova atlas refinement is Fase E
scope, not D1).

LONG ⇒ caller pays mid + slippage; SHORT ⇒ receives mid - slippage.
Hard stop exit at exit_deadline_brt — broker forces fill regardless.

AC8: slippage model per spec `costs.slippage_model`.
AC9: 17:55 hard stop.
AC10: zero lookahead — broker never consults future ts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ..core.signal_rule import Direction

WDO_TICK_SIZE: float = 0.5  # R$/ponto × 10 = R$5 per tick
WDO_MULTIPLIER: float = 10.0  # R$ per point


@dataclass(frozen=True)
class Fill:
    ts: datetime
    price: float
    qty: int  # signed: +LONG, -SHORT
    fees_rs: float
    reason: str


@dataclass(frozen=True)
class BacktestCosts:
    """Conservative defaults. Overridden Fase E from Nova atlas."""

    brokerage_per_contract_side_rs: float = 0.25
    exchange_fees_per_contract_side_rs: float = 0.35  # emolumentos B3 placeholder
    roll_spread_half_points: float = 0.5  # half of 1-tick Roll spread
    slippage_extra_ticks: int = 1  # worst-case cushion


class BacktestBroker:
    """Simulates fills with deterministic slippage and fees.

    No position state — caller (backtest runner) tracks positions and
    calls `execute` or `force_exit` as needed.
    """

    def __init__(self, costs: BacktestCosts | None = None) -> None:
        self._costs = costs or BacktestCosts()

    def _slippage(self) -> float:
        return (
            self._costs.roll_spread_half_points
            + self._costs.slippage_extra_ticks * WDO_TICK_SIZE
        )

    def _fees(self, n_contracts: int) -> float:
        per_side = (
            self._costs.brokerage_per_contract_side_rs
            + self._costs.exchange_fees_per_contract_side_rs
        )
        return abs(n_contracts) * per_side

    def execute(
        self,
        *,
        direction: Direction,
        n_contracts: int,
        ts: datetime,
        mid_price: float,
    ) -> Fill:
        """Execute a market-style order.

        `n_contracts` is positive magnitude; sign encoded in `direction`.
        """
        if direction == Direction.FLAT:
            raise ValueError("cannot execute FLAT signal")
        if n_contracts <= 0:
            raise ValueError(f"n_contracts must be > 0, got {n_contracts}")

        slip = self._slippage()
        if direction == Direction.LONG:
            price = mid_price + slip
            signed_qty = n_contracts
        else:  # SHORT
            price = mid_price - slip
            signed_qty = -n_contracts

        return Fill(
            ts=ts,
            price=price,
            qty=signed_qty,
            fees_rs=self._fees(n_contracts),
            reason="entry_market",
        )

    def force_exit(
        self,
        *,
        open_qty: int,
        ts: datetime,
        mid_price: float,
    ) -> Fill:
        """AC9: hard stop at exit_deadline_brt — forces market fill."""
        if open_qty == 0:
            raise ValueError("force_exit called with no open position")
        # flatten the position: if LONG held, sell; if SHORT held, buy
        if open_qty > 0:
            # LONG → sell at mid - slip
            price = mid_price - self._slippage()
            signed_qty = -open_qty
        else:
            price = mid_price + self._slippage()
            signed_qty = -open_qty  # buy to cover
        return Fill(
            ts=ts,
            price=price,
            qty=signed_qty,
            fees_rs=self._fees(open_qty),
            reason="exit_hard_stop",
        )


def pnl_contracts(entry: Fill, exit_: Fill) -> float:
    """PnL in R$ for a round-trip: (exit_price - entry_price) × mult × signed_entry.

    entry.qty carries sign: +LONG (profit if price rises) / -SHORT (profit if falls).
    Fees summed both sides.
    """
    gross_points = (exit_.price - entry.price) * entry.qty  # sign handled by entry.qty
    gross_rs = gross_points * WDO_MULTIPLIER
    total_fees = entry.fees_rs + exit_.fees_rs
    return gross_rs - total_fees
