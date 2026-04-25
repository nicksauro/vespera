"""BacktestBroker — layer 5 backtest execution adapter.

Deterministic slippage: Roll_spread_half + 1 tick worst-case (Beckett
default). Fees source-of-truth in `docs/backtest/nova-cost-atlas.yaml`
v1.0.0 (Nova compiled, Sable APPROVED_WITH_CONDITIONS), wired via
`docs/backtest/engine-config.yaml` (Beckett T002.0e).

LONG => caller pays mid + slippage; SHORT => receives mid - slippage.
Hard stop exit at exit_deadline_brt — broker forces fill regardless.

AC8: slippage model per spec `costs.slippage_model`.
AC9: 17:55 hard stop.
AC10: zero lookahead — broker never consults future ts.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..core.signal_rule import Direction

WDO_TICK_SIZE: float = 0.5  # R$/ponto x 10 = R$5 per tick
WDO_MULTIPLIER: float = 10.0  # R$ per point


class CostAtlasShaMismatch(RuntimeError):
    """Raised when atlas SHA256 differs from engine-config lock — fail_fast."""


class CostAtlasVersionMismatch(RuntimeError):
    """Raised when atlas_version differs from engine-config lock — fail_fast."""


class EngineConfigInvalid(ValueError):
    """Raised when engine-config.yaml is missing required fields."""


@dataclass(frozen=True)
class Fill:
    ts: datetime
    price: float
    qty: int  # signed: +LONG, -SHORT
    fees_rs: float
    reason: str


@dataclass(frozen=True)
class BacktestCosts:
    """Cost parameters for BacktestBroker.

    PREFERRED: load via :meth:`from_engine_config` so values trace to
    `docs/backtest/nova-cost-atlas.yaml` v1.0.0 (Nova compiled, Sable audited).

    Direct constructor with defaults remains for back-compat of existing tests
    and quick prototyping. **[DEPRECATED — use from_engine_config]** Defaults
    are conservative placeholders, NOT the canonical Nova atlas values.

    Cost source: docs/backtest/nova-cost-atlas.yaml v1.0.0
    Engine config: docs/backtest/engine-config.yaml v1.0.0 (Beckett T002.0e)
    """

    # DEFAULT — override via nova-cost-atlas.yaml v>=1.0.0; [TO-VERIFY] until wired in engine-config
    brokerage_per_contract_side_rs: float = 0.25
    exchange_fees_per_contract_side_rs: float = 0.35  # emolumentos B3 placeholder
    roll_spread_half_points: float = 0.5  # half of 1-tick Roll spread
    slippage_extra_ticks: int = 1  # worst-case cushion

    # =====================================================================
    # CANONICAL LOADER — engine-config.yaml + atlas Nova v1.0.0
    # =====================================================================
    @classmethod
    def from_engine_config(cls, path: str | Path) -> "BacktestCosts":
        """Load cost parameters from `docs/backtest/engine-config.yaml`.

        Resolves atlas reference, validates SHA256 + atlas_version locks
        (fail_fast on mismatch), maps cost_components/slippage_model to
        BacktestCosts fields. Preserves zero-invention discipline (Article IV).

        Raises:
            FileNotFoundError: engine-config or atlas path does not exist.
            EngineConfigInvalid: required fields missing in engine-config.
            CostAtlasShaMismatch: atlas content sha256 != engine-config lock.
            CostAtlasVersionMismatch: atlas_version != engine-config lock.
        """
        cfg_path = Path(path)
        if not cfg_path.is_file():
            raise FileNotFoundError(f"engine-config not found: {cfg_path}")

        cfg = _load_yaml(cfg_path)
        _require_keys(
            cfg,
            ["cost_atlas_ref", "cost_components", "slippage_model"],
            ctx=f"engine-config {cfg_path.name}",
        )

        atlas_ref = cfg["cost_atlas_ref"]
        _require_keys(
            atlas_ref,
            ["path", "atlas_version_lock", "atlas_sha256_lock"],
            ctx="cost_atlas_ref",
        )

        # Atlas path is relative to repo root (engine-config canonical layout)
        atlas_path = _resolve_atlas_path(cfg_path, atlas_ref["path"])
        if not atlas_path.is_file():
            raise FileNotFoundError(f"atlas not found: {atlas_path}")

        # SHA256 check — normalize CRLF -> LF to match canonical git blob hash
        actual_sha = _sha256_lf(atlas_path)
        expected_sha = atlas_ref["atlas_sha256_lock"]
        if actual_sha != expected_sha:
            raise CostAtlasShaMismatch(
                f"Atlas SHA256 mismatch — expected {expected_sha}, got {actual_sha}. "
                f"Atlas content has drifted from engine-config lock; refusing CPCV. "
                f"Re-audit atlas (Sable) and bump version before resuming."
            )

        atlas = _load_yaml(atlas_path)
        atlas_ver = atlas.get("atlas_version")
        expected_ver = atlas_ref["atlas_version_lock"]
        if atlas_ver != expected_ver:
            raise CostAtlasVersionMismatch(
                f"Atlas version mismatch — expected {expected_ver}, got {atlas_ver}."
            )

        # Resolve cost components -> atlas paths
        components = cfg["cost_components"]
        _require_keys(components, ["brokerage", "exchange_fees"], ctx="cost_components")

        brokerage = _resolve_atlas_path_lookup(atlas, components["brokerage"]["from"])
        exchange = _resolve_atlas_path_lookup(atlas, components["exchange_fees"]["from"])

        # Slippage params come from engine-config (deterministic Beckett defaults)
        slip = cfg["slippage_model"]
        _require_keys(
            slip,
            ["roll_spread_half_points", "slippage_extra_ticks"],
            ctx="slippage_model",
        )

        return cls(
            brokerage_per_contract_side_rs=float(brokerage),
            exchange_fees_per_contract_side_rs=float(exchange),
            roll_spread_half_points=float(slip["roll_spread_half_points"]),
            slippage_extra_ticks=int(slip["slippage_extra_ticks"]),
        )


# =====================================================================
# Module-private helpers (engine-config loader)
# =====================================================================
def _load_yaml(p: Path) -> dict[str, Any]:
    with p.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise EngineConfigInvalid(f"YAML root is not a mapping: {p}")
    return data


def _require_keys(d: dict[str, Any], keys: list[str], *, ctx: str) -> None:
    missing = [k for k in keys if k not in d]
    if missing:
        raise EngineConfigInvalid(f"{ctx} missing required field(s): {missing}")


def _resolve_atlas_path(cfg_path: Path, atlas_rel: str) -> Path:
    """Resolve atlas path. atlas_rel is relative to repo root.

    Engine-config lives in `docs/backtest/engine-config.yaml`; repo root is
    parent.parent. Allow absolute path override too.
    """
    p = Path(atlas_rel)
    if p.is_absolute():
        return p
    # cfg_path = .../docs/backtest/engine-config.yaml -> repo root is parents[2]
    repo_root = cfg_path.resolve().parents[2]
    return repo_root / p


def _resolve_atlas_path_lookup(atlas: dict[str, Any], dotted: str) -> Any:
    """Resolve dotted lookup like `costs.brokerage.per_contract_one_way`."""
    cur: Any = atlas
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise EngineConfigInvalid(f"atlas lookup failed at '{part}' in '{dotted}'")
        cur = cur[part]
    return cur


def _sha256_lf(path: Path) -> str:
    """Compute SHA256 of file with CRLF normalized to LF.

    Matches canonical git blob hash on Windows checkouts where atlas may render
    with CRLF line endings. Story T002.0e Beckett-consume-signoff committed
    SHA over LF canonical content.
    """
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n")
    return hashlib.sha256(normalized).hexdigest()


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
            # LONG -> sell at mid - slip
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
    """PnL in R$ for a round-trip: (exit_price - entry_price) x mult x signed_entry.

    entry.qty carries sign: +LONG (profit if price rises) / -SHORT (profit if falls).
    Fees summed both sides.
    """
    gross_points = (exit_.price - entry.price) * entry.qty  # sign handled by entry.qty
    gross_rs = gross_points * WDO_MULTIPLIER
    total_fees = entry.fees_rs + exit_.fees_rs
    return gross_rs - total_fees
