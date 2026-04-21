"""SessionState — layer 2 of T002.

Pure, O(1) per trade. Tracks open_day, last_price, session high/low
(for ATR_day), plus a registry of close prices at configured snapshot
timestamps (anti-leakage — snapshot_at(t) never returns a price from t' > t).

BRT naive throughout (MANIFEST R2). Trades-only (R7): no book, no LTP
stream — just T&S.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time

SESSION_OPEN_BRT: time = time(9, 30, 0)


@dataclass(frozen=True)
class Trade:
    """Single trade print from T&S."""

    ts: datetime  # BRT naive
    price: float
    qty: int


@dataclass(frozen=True)
class SessionSnapshot:
    """Immutable read of session state as-of a given timestamp.

    `close_at_ts` is the last trade price with `trade.ts <= ts` (strictly
    anti-leakage — see AC2).
    """

    as_of_ts: datetime
    open_day: float
    close_at_ts: float
    session_high: float
    session_low: float


class SessionState:
    """Online aggregator for one trading session (WDO).

    Call `on_trade(trade)` for every T&S print in ascending ts order.
    Call `snapshot_at(ts)` at the 4 deterministic entry windows to obtain
    an immutable snapshot for the feature computer.

    Invariants:
      - `open_day` is fixed on the FIRST trade whose ts >= 09:30:00 BRT.
        Trades before session open are ignored for open_day but still
        update high/low/last (they shouldn't exist — defensive).
      - `session_high`, `session_low`, `last_price`, `last_ts` update
        monotonically in the order trades arrive.
      - Out-of-order trades (ts < last_ts) raise ValueError — backtest
        feed must emit in order.
    """

    __slots__ = (
        "_open_day",
        "_last_price",
        "_last_ts",
        "_session_high",
        "_session_low",
    )

    def __init__(self) -> None:
        self._open_day: float | None = None
        self._last_price: float | None = None
        self._last_ts: datetime | None = None
        self._session_high: float | None = None
        self._session_low: float | None = None

    # -------- mutation --------

    def on_trade(self, trade: Trade) -> None:
        if self._last_ts is not None and trade.ts < self._last_ts:
            raise ValueError(
                f"out-of-order trade: {trade.ts} < last_ts {self._last_ts}"
            )

        if self._open_day is None and trade.ts.time() >= SESSION_OPEN_BRT:
            self._open_day = trade.price

        self._last_price = trade.price
        self._last_ts = trade.ts
        if self._session_high is None or trade.price > self._session_high:
            self._session_high = trade.price
        if self._session_low is None or trade.price < self._session_low:
            self._session_low = trade.price

    # -------- read --------

    @property
    def is_open(self) -> bool:
        return self._open_day is not None

    @property
    def open_day(self) -> float | None:
        return self._open_day

    @property
    def last_price(self) -> float | None:
        return self._last_price

    @property
    def last_ts(self) -> datetime | None:
        return self._last_ts

    @property
    def session_high(self) -> float | None:
        return self._session_high

    @property
    def session_low(self) -> float | None:
        return self._session_low

    def snapshot_at(self, ts: datetime) -> SessionSnapshot:
        """Return snapshot as-of `ts`.

        Contract: `close_at_ts` is `last_price` if `last_ts <= ts`. If
        `last_ts > ts` (caller misused the API), raises. If no trade yet
        arrived at all, raises.

        NOTE: in normal usage the backtest/live loop calls snapshot_at
        at the exact entry timestamp and only AFTER having pushed all
        trades with ts <= entry into the state. We trust that contract
        here rather than scanning a trade buffer (layer responsibility
        boundary — buffering is layer 1).
        """
        if self._last_ts is None:
            raise ValueError("snapshot_at called before any trade arrived")
        if self._last_ts > ts:
            raise ValueError(
                f"anti-leakage violation: snapshot_at({ts}) called but "
                f"state has last_ts={self._last_ts} > ts"
            )
        if self._open_day is None:
            raise ValueError(
                f"snapshot_at({ts}) called before session open at "
                f"{SESSION_OPEN_BRT} BRT"
            )
        assert self._last_price is not None
        assert self._session_high is not None
        assert self._session_low is not None
        return SessionSnapshot(
            as_of_ts=ts,
            open_day=self._open_day,
            close_at_ts=self._last_price,
            session_high=self._session_high,
            session_low=self._session_low,
        )
