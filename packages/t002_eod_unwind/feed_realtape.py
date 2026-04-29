"""feed_realtape — real WDO trade-tape loader + microstructure flag detector
+ replay walker for T002.6 Phase F real-tape replay.

Story: T002.6 (T1 Dex impl) — Mira Gate 4b spec v1.0.0 §3 (real-tape data
interface), §4 (RLP/microstructure verbatim from Nova spec), §5 (latency
model verbatim from Beckett spec).

Authority chain:
- Mira spec: docs/ml/specs/T002-gate-4b-real-tape-clearance.md v1.0.0
- Aria T0b conditions: C-A1 (replay helper INSIDE closure body), C-A2 (per-fill
  slippage at materialization, not aggregation), C-A4 (per-session flags BEFORE
  partition), C-A5 (cross_trade default False historic regime), C-A6 (toy
  benchmark structural sibling).
- Beckett T0c condition: C-B2 (lazy per-session parquet loading; no eager full
  window load).
- Nova spec: docs/backtest/T002.6-nova-rlp-rollover-spec.md §6 yaml verbatim.
- Beckett latency spec: docs/backtest/latency-dma2-profile-spec.md §4 yaml verbatim.

Module contract:
    load_session_trades(session_date, parquet_root) -> pd.DataFrame
        Lazy load single-session trades from monthly parquet (Beckett C-B2).
        Returns DataFrame with columns (ts, price, qty, aggressor) for the
        target session only — does NOT eager-load adjacent months.

    detect_session_microstructure_flags(trades, session_date, calendar) -> dict
        Detect Nova flags per Nova spec §4:
        - rollover_window: bool (D-3..D-1 from wdo_expirations + br_holidays)
        - circuit_breaker_fired: bool (continuous aggressor=NONE gap >30min)
        - cross_trade_pct: float (sentinel — historic gap, default 0.0)
        - rlp_active: tuple (start, end) BRT for the session

    latency_slippage_pts(seed, component, mid_at_decision, future_mid_lookup, config)
        Beckett spec §3.1 verbatim formula:
            slippage_latency_pts = sign × (mid_at_decision − mid_at_fill_after_latency)
        Per-fill API exposing seed-derived deterministic log-normal latency
        draw (Aria C-A2: per-fill API).

    replay_event_walk(...) -> ExitOutcome
        Real-tape barrier walk substituting cpcv_harness._walk_to_exit synthetic
        path. Triple-barrier precedence SL > PT > vertical (AFML 2018 §3.4),
        auction boundary 17:55 BRT (Nova §3.2-α).

Article IV provenance:
    Every numeric / behavior clause traces to:
    - Mira spec §3.3 (interface contract); §4.1 (Nova yaml verbatim);
      §5.1 (Beckett yaml verbatim); §2.1 (triple-barrier precedence).
    - Nova §1-§5 (RLP, rollover, auction, CB, cross_trade).
    - Beckett §3.1 (latency slippage formula); §2.4 (seed derivation).
    - parent spec yaml v0.2.3 (17:55 vertical exit; UNMOVABLE).

Anti-Article-IV Guards preserved:
    #2 NO subsample dataset — full session loaded lazily per session.
    #3 NO touch hold-out lock — caller responsible (cpcv_harness window guard).
    #5 NO subsample backtest — full triple-barrier walk per event.

Phase gate (engine-config v1.1.0 phase_gating.enabled_for_phase: ["F"]):
    Real-tape replay activates only under phase="F"; phase="E" routes to
    legacy synthetic walk (T002.1.bis carry-forward; back-compat).
"""

from __future__ import annotations

import hashlib
import math
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, Literal, Mapping

import numpy as np
import pandas as pd


# =====================================================================
# Constants — Nova / Beckett spec verbatim
# =====================================================================
# Auction boundary per Nova §3.2-α + parent spec yaml v0.2.3 17:55 vertical.
_AUCTION_BOUNDARY_BRT: time = time(17, 55, 0)

# RLP active hours per Nova §1.2 + §6 yaml block.
_RLP_ACTIVE_START_BRT: time = time(9, 0, 0)
_RLP_ACTIVE_END_BRT: time = time(17, 55, 0)

# Circuit breaker detection: continuous aggressor=NONE gap >30min within
# 09:30..17:55 BRT per Nova §4.2 historic detection signal.
_CB_DETECTION_GAP_MIN: int = 30
_CB_DETECTION_WINDOW_START_BRT: time = time(9, 30, 0)
_CB_DETECTION_WINDOW_END_BRT: time = time(17, 55, 0)

# WDO_TICK_SIZE imported lazily inside replay_event_walk to keep this module
# free of cpcv_harness circular imports.

# Component name enum (Beckett spec §2.1).
LatencyComponent = Literal["order_submit", "fill", "cancel"]


# =====================================================================
# §3 — Lazy per-session parquet loader (Beckett C-B2)
# =====================================================================
def _resolve_parquet_path(session_date: date, parquet_root: Path) -> Path:
    """Map session_date → monthly parquet path under repo's
    ``data/in_sample/year=YYYY/month=MM/wdo-YYYY-MM.parquet`` layout.

    Per project layout verified at T1 prep: 18 monthly files 2024-01..2025-06
    cover the in-sample window 2024-08-22..2025-06-30.
    """
    year = session_date.year
    month = session_date.month
    return (
        parquet_root
        / f"year={year:04d}"
        / f"month={month:02d}"
        / f"wdo-{year:04d}-{month:02d}.parquet"
    )


def load_session_trades(
    session_date: date,
    parquet_root: Path,
) -> pd.DataFrame:
    """Lazy-load a single session's trades from the monthly parquet (C-B2).

    Per Beckett T0c §1.3 Strategy A (lazy per-session): the engine MUST NOT
    eager-load the full in-sample window. This helper opens the monthly
    parquet covering ``session_date``, filters rows where
    ``timestamp.date() == session_date``, and returns a session-scoped
    DataFrame.

    Returns columns ``(ts, price, qty, aggressor)`` matching Mira §3.2 +
    Nova §1.3 trades-only schema. The historic ``trade_type`` enum is
    NOT available — Mira §4.3 explicit gap.

    Parameters
    ----------
    session_date:
        Target trading session date (BRT calendar date).
    parquet_root:
        Root directory holding ``year=YYYY/month=MM/wdo-YYYY-MM.parquet``
        layout. Typically ``Path("data/in_sample")``.

    Returns
    -------
    pd.DataFrame
        Columns ``(ts, price, qty, aggressor)``; rows sorted ascending by
        ``ts``. Empty DataFrame if the session has zero trades or the
        monthly parquet is missing (caller decides escalation).

    Raises
    ------
    FileNotFoundError
        Caller-facing escalation when the monthly parquet is expected but
        absent (verifiable session yet missing data → real upstream gap).
        Does NOT raise on empty filter result — empty session is signaled
        via empty DataFrame so the caller can mark FLAT per session policy.
    """
    path = _resolve_parquet_path(session_date, parquet_root)
    if not path.exists():
        raise FileNotFoundError(
            f"feed_realtape: parquet missing for session {session_date.isoformat()}: "
            f"expected at {path}. Anti-Article-IV: NO neutral fallback — "
            "operator must escalate (data ingest gap)."
        )

    # Lazy filtered load — pyarrow predicate pushdown via filters kwarg
    # avoids materializing the entire month into memory (Beckett C-B2).
    import pyarrow as pa  # noqa: F401  (pyarrow imported by parquet engine)
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(path)

    # We can't push down a date predicate generically (timestamp[ns] vs
    # date), so we filter in pandas after row-group skip via min/max stats.
    day_start = pd.Timestamp(datetime.combine(session_date, time(0, 0, 0)))
    day_end = pd.Timestamp(datetime.combine(session_date, time(23, 59, 59, 999999)))

    frames: list[pd.DataFrame] = []
    for rg_idx in range(pf.num_row_groups):
        rg_meta = pf.metadata.row_group(rg_idx)
        ts_field_idx = pf.schema_arrow.get_field_index("timestamp")
        col_stats = rg_meta.column(ts_field_idx).statistics
        if col_stats is not None and col_stats.has_min_max:
            rg_min = col_stats.min
            rg_max = col_stats.max
            # Skip row-groups entirely outside the session day.
            if rg_max < day_start.to_pydatetime() or rg_min > day_end.to_pydatetime():
                continue

        table = pf.read_row_group(
            rg_idx, columns=["timestamp", "price", "qty", "aggressor"]
        )
        df = table.to_pandas()
        # Filter to exact session day (BRT-naive).
        mask = df["timestamp"].dt.date == session_date
        if mask.any():
            frames.append(df.loc[mask].copy())

    if not frames:
        # Empty session — possible on holidays absent from calendar or
        # rollover gaps. Caller decides FLAT semantics.
        return pd.DataFrame(
            columns=["ts", "price", "qty", "aggressor"],
        )

    out = pd.concat(frames, ignore_index=True)
    out = out.rename(columns={"timestamp": "ts"})
    out = out[["ts", "price", "qty", "aggressor"]].sort_values("ts", kind="stable")
    out = out.reset_index(drop=True)
    return out


# =====================================================================
# §4 — Microstructure flag detection (Nova spec §1-§5 verbatim)
# =====================================================================
def detect_rollover_window(
    session_date: date,
    *,
    wdo_expirations: Iterable[date],
    br_holidays: Iterable[date],
) -> bool:
    """Return True iff session_date falls in D-3..D-1 of any wdo_expiration.

    Per Nova §2.3 pseudocode verbatim — walk back 3 trading days from each
    expiration, skipping br_holidays. Naive calendar arithmetic is wrong
    because BR holidays interject.

    Article IV: derivation traced to Nova spec §6 yaml block
    `rollover.derivation` field.
    """
    holidays_set = set(br_holidays)
    for expiry in wdo_expirations:
        d = expiry
        found = 0
        while found < 3:
            d = d - timedelta(days=1)
            if d.weekday() < 5 and d not in holidays_set:
                if d == session_date:
                    return True
                found += 1
    return False


def detect_circuit_breaker_fired(trades: pd.DataFrame) -> bool:
    """Return True iff session has continuous aggressor=NONE gap >30 min
    during 09:30..17:55 BRT.

    Per Nova §4.2 historic detection signal verbatim — pure timestamp gap
    analysis on the trade tape suffices (no explicit halt_flag column in
    historic parquet).

    Heuristic: walk through trades ordered by ts within the detection
    window, find max gap between adjacent timestamps where BOTH bracket
    trades have aggressor=NONE OR the gap itself exceeds the threshold
    irrespective of aggressor (Nova spec uses "continuous aggressor=NONE
    gap" which we operationalize as: gap is the time between any two
    consecutive trades during the window).
    """
    if trades.empty or "ts" not in trades.columns:
        return False
    # Filter to detection window 09:30..17:55 BRT.
    win_mask = trades["ts"].dt.time.between(
        _CB_DETECTION_WINDOW_START_BRT, _CB_DETECTION_WINDOW_END_BRT
    )
    sub = trades.loc[win_mask].sort_values("ts", kind="stable")
    if len(sub) < 2:
        # Sparse session — treat as suspect (likely trading suspension).
        return True
    deltas = sub["ts"].diff().dt.total_seconds().fillna(0)
    max_gap_min = float(deltas.max()) / 60.0
    return max_gap_min > _CB_DETECTION_GAP_MIN


def detect_session_microstructure_flags(
    trades: pd.DataFrame,
    session_date: date,
    *,
    wdo_expirations: Iterable[date] = (),
    br_holidays: Iterable[date] = (),
) -> dict[str, object]:
    """Return Nova microstructure flags for the session.

    Per Aria T0b C-A4 + C-A5 + Mira §4.3 + Nova §1-§5:
    - rollover_window: bool (D-3..D-1 detection)
    - circuit_breaker_fired: bool (continuous aggressor=NONE gap >30min)
    - cross_trade_pct: float (historic regime fixed at 0.0; Mira §4.3 gap;
      Aria C-A5 default False semantics — represented as 0.0 for the per-
      session aggregate flag; per-event cross_trade default False is set
      at event materialization site)
    - rlp_active_hours: tuple[time, time] (Nova §1.2 verbatim)
    - rlp_flag_available_historic: bool (False per Mira §4.3)
    """
    return {
        "rollover_window": detect_rollover_window(
            session_date,
            wdo_expirations=wdo_expirations,
            br_holidays=br_holidays,
        ),
        "circuit_breaker_fired": detect_circuit_breaker_fired(trades),
        "cross_trade_pct": 0.0,  # Aria C-A5: historic default; per-event False
        "rlp_active_hours": (_RLP_ACTIVE_START_BRT, _RLP_ACTIVE_END_BRT),
        "rlp_flag_available_historic": False,  # Mira §4.3 + Nova §1.3
    }


# =====================================================================
# §5 — Latency model (Beckett spec §2-§3 verbatim)
# =====================================================================
def _seed_event(
    session: date,
    order_id: str,
    trial_id: str,
    component: str,
) -> bytes:
    """Beckett spec §2.4 verbatim:
        seed_event = blake2b_64(session, order_id, trial_id, component_name)

    Returns 8-byte blake2b digest. Cross-platform stable.
    """
    h = hashlib.blake2b(digest_size=8)
    payload = f"{session.isoformat()}|{order_id}|{trial_id}|{component}".encode("utf-8")
    h.update(payload)
    return h.digest()


def _draw_lognormal_ms(
    seed: bytes,
    *,
    mu: float,
    sigma: float,
) -> float:
    """Deterministic log-normal draw via inverse CDF (Beckett spec §2.4).

    seed → uniform u in (0, 1) → latency_ms = exp(mu + sigma × Φ⁻¹(u)).

    Uses numpy.random.default_rng(int_from_seed) for reproducibility — same
    seed bytes → same uniform → same latency_ms across platforms.
    """
    seed_int = int.from_bytes(seed, byteorder="big") & 0xFFFFFFFFFFFFFFFF
    rng = np.random.default_rng(seed_int)
    u = float(rng.uniform(low=1e-9, high=1.0 - 1e-9))
    # Φ⁻¹(u) — standard normal inverse CDF via numpy (no scipy dep).
    # Inverse erf approximation per Acklam 2003 — sufficient for our regime.
    z = math.sqrt(2.0) * _ndtri(2.0 * u - 1.0)
    return math.exp(mu + sigma * z)


def _ndtri(x: float) -> float:
    """Inverse error function approximation (Acklam 2003, sufficient ε).

    Used to invert standard normal CDF. Acceptable accuracy for our
    latency-quantile sampling regime (P50..P99 anchors).
    """
    # Coefficients for Acklam's rational approximation of erf^{-1}.
    a = (
        -0.0000000005,
        0.000000003,
        -0.000000016,
        0.000000087,
        -0.000000470,
        0.000002576,
        -0.000014328,
        0.000080847,
        -0.000463002,
        0.002704315,
        -0.016198486,
        0.099792905,
        -0.633994725,
        4.999998881,
    )
    # Fallback to math.erf-based inversion via secant method for safety.
    # Bisection on z ∈ [-8, 8] with target erf(z/sqrt(2)) ≈ x.
    target = x
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if math.erf(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def latency_slippage_pts(
    *,
    seed: bytes,
    component: LatencyComponent,
    mid_at_decision: float,
    mid_at_fill_after_latency: float,
    sign: int,
    config: Mapping[str, object],
) -> float:
    """Beckett spec §3.1 verbatim formula (per-fill API per Aria C-A2):
        slippage_latency_pts = sign × (mid_at_decision − mid_at_fill_after_latency)

    Per Aria T0b C-A2 — slippage integration at fill-event materialization
    time, NOT PnL aggregation, so seed is anchored to the specific fill
    event. Returns a points value (WDO points; multiply by WDO_MULTIPLIER
    upstream for R$ if needed).

    The ``seed`` argument is NOT consumed by the formula itself (the
    seed-driven latency draw is the caller's concern, used to derive
    ``mid_at_fill_after_latency`` from the tape). Accepted here for
    determinism-stamp anchoring per Beckett §2.4.

    When ``config['enabled_for_phase']`` excludes the current phase or is
    empty, returns 0.0 deterministically (Aria C-A3 testable contract:
    F-disabled returns 0.0 deterministically).
    """
    # Aria C-A3: enabled_for_phase gate must be testable in both directions.
    enabled = config.get("enabled_for_phase", [])
    current_phase = config.get("current_phase", "F")  # caller injects
    if current_phase not in enabled:
        return 0.0
    # seed used for trace; component used to differentiate per-component
    # log-normal anchors (caller pre-computed mid_at_fill_after_latency
    # using the per-component (mu, sigma) from engine-config v1.1.0).
    _ = seed
    _ = component
    return float(sign) * (mid_at_decision - mid_at_fill_after_latency)


def draw_latency_ms(
    *,
    seed: bytes,
    component: LatencyComponent,
    config: Mapping[str, object],
) -> float:
    """Sample latency in ms via Beckett §2.4 lognormal_per_event_seeded.

    Returns 0.0 when the current phase is disabled (Aria C-A3 contract:
    F-disabled deterministic 0.0).

    Reads (mu, sigma) per-component from the engine-config v1.1.0
    latency_model.components.{component} block.
    """
    enabled = config.get("enabled_for_phase", [])
    current_phase = config.get("current_phase", "F")
    if current_phase not in enabled:
        return 0.0
    components = config.get("components", {})
    comp_block = components.get(component, {})
    mu = float(comp_block.get("mu", 0.0))
    sigma = float(comp_block.get("sigma", 0.0))
    if sigma <= 0.0:
        # Safety — degenerate distribution returns P50 anchor.
        return float(comp_block.get("p50_ms", 0.0))
    return _draw_lognormal_ms(seed, mu=mu, sigma=sigma)


# =====================================================================
# §3.3 — Real-tape barrier walk (replaces _walk_to_exit synthetic)
# =====================================================================
def replay_event_walk(
    *,
    trades: pd.DataFrame,
    entry_ts: datetime,
    entry_price: float,
    pt_offset: float,
    sl_offset: float,
    sign: int,
    auction_cutoff_ts: datetime,
    latency_config: Mapping[str, object],
    seed_inputs: tuple[date, str, str],  # (session, order_id, trial_id)
) -> tuple[float, str, int]:
    """Real-tape triple-barrier walk per Mira §3.3 + §2.1 + Nova §3.2-α.

    Per Aria T0b C-A1 — this helper is invoked from inside the closure
    body of `make_backtest_fn`, NOT from inside the factory builder.
    Per Aria C-A2 — slippage integration is per-fill (here, at exit
    materialization time). Per Nova §3.2-α — auction boundary at
    17:55:00 BRT excludes auction prints from forming the exit price.

    Triple-barrier precedence: SL > PT > vertical (AFML 2018 §3.4
    pessimist convention; same-tick ties resolve to SL).

    Parameters
    ----------
    trades:
        Session DataFrame from ``load_session_trades`` — columns
        ``(ts, price, qty, aggressor)`` ascending by ts.
    entry_ts:
        Decision timestamp (post-latency-applied entry not modeled here;
        caller prices entry separately).
    entry_price:
        Entry price (already includes broker_slip per cpcv_harness path).
    pt_offset, sl_offset:
        Triple-barrier offsets in WDO points (Mira §2.1 1.5×ATR_hora /
        1.0×ATR_hora).
    sign:
        +1 for LONG, -1 for SHORT.
    auction_cutoff_ts:
        Vertical barrier timestamp (17:55:00 BRT same-session per Nova
        §3.2-α — last non-auction trade < 17:55:00 BRT forms exit price).
    latency_config:
        engine-config v1.1.0 latency_model block (mapping). Used for
        per-fill latency draw on the exit fill (Aria C-A2 per-fill API).
    seed_inputs:
        Tuple ``(session, order_id, trial_id)`` for Beckett §2.4 seed
        derivation. ``component_name`` is appended internally per fill
        type (entry uses "order_submit", exit uses "fill").

    Returns
    -------
    tuple[float, str, int]
        ``(exit_price, exit_reason, ticks_held)`` matching the legacy
        ``_walk_to_exit`` interface (Aria §2 factory-pattern preservation
        contract — closure body upgrade is additive).
    """
    if trades.empty or "ts" not in trades.columns:
        # No tape data — degenerate FLAT exit at entry_price.
        return entry_price, "vertical", 0

    # Filter trades from entry_ts to auction_cutoff_ts; respect Nova §3.2-α
    # by excluding any trade at or after 17:55:00 BRT.
    walk_mask = (
        (trades["ts"] >= pd.Timestamp(entry_ts))
        & (trades["ts"] < pd.Timestamp(auction_cutoff_ts))
    )
    walk = trades.loc[walk_mask].sort_values("ts", kind="stable")
    if walk.empty:
        return entry_price, "vertical", 0

    session = seed_inputs[0]
    order_id = seed_inputs[1]
    trial_id = seed_inputs[2]

    # Per Mira §2.1 + AFML 2018 §3.4 precedence: SL > PT > vertical.
    # Walk forward; first barrier hit wins; same-tick (SL & PT both hit
    # by single trade price) → SL.
    ticks_held = 0
    last_price = entry_price
    for _, row in walk.iterrows():
        ticks_held += 1
        tick_price = float(row["price"])
        last_price = tick_price
        if sign == 1:  # LONG
            hit_sl = tick_price <= entry_price - sl_offset
            hit_pt = tick_price >= entry_price + pt_offset
            if hit_sl and hit_pt:
                exit_raw = entry_price - sl_offset
                exit_reason = "sl_hit"
                break
            if hit_sl:
                exit_raw = entry_price - sl_offset
                exit_reason = "sl_hit"
                break
            if hit_pt:
                exit_raw = entry_price + pt_offset
                exit_reason = "pt_hit"
                break
        else:  # SHORT
            hit_sl = tick_price >= entry_price + sl_offset
            hit_pt = tick_price <= entry_price - pt_offset
            if hit_sl and hit_pt:
                exit_raw = entry_price + sl_offset
                exit_reason = "sl_hit"
                break
            if hit_sl:
                exit_raw = entry_price + sl_offset
                exit_reason = "sl_hit"
                break
            if hit_pt:
                exit_raw = entry_price - pt_offset
                exit_reason = "pt_hit"
                break
    else:
        # No barrier hit — vertical exit at last non-auction trade
        # (Nova §3.2-α last trade with timestamp < 17:55:00 BRT).
        exit_raw = last_price
        exit_reason = "vertical"

    # Per Aria C-A2 + Beckett §3.1 — apply per-fill latency slippage at
    # exit materialization. Caller has already applied entry-side broker
    # slip; here we add the temporal mid-drift cushion via latency model.
    exit_seed = _seed_event(session, order_id, trial_id, "fill")
    # Conservative: latency formula returns sign × (mid_decision - mid_fill).
    # In real tape, the "mid_fill_after_latency" requires looking N ms past
    # the barrier hit. We approximate via the next available trade after
    # exit timestamp (latency_config-disabled path returns 0.0 by Aria C-A3).
    latency_pts = _approx_exit_latency_pts(
        walk=walk,
        exit_raw=exit_raw,
        exit_ticks=ticks_held,
        sign=sign,
        seed=exit_seed,
        component="fill",
        config=latency_config,
    )
    exit_price = exit_raw - sign * latency_pts  # adverse adds cost
    return float(exit_price), exit_reason, int(ticks_held)


def _approx_exit_latency_pts(
    *,
    walk: pd.DataFrame,
    exit_raw: float,
    exit_ticks: int,
    sign: int,
    seed: bytes,
    component: LatencyComponent,
    config: Mapping[str, object],
) -> float:
    """Approximate exit-side latency slippage by walking forward
    ``draw_latency_ms`` ms from the barrier-hit trade.

    Returns 0.0 when the latency model is phase-disabled (Aria C-A3).
    The mid_at_decision == exit_raw; mid_at_fill_after_latency = next
    available trade price ``latency_ms`` past the hit timestamp (clipped
    to walk frame). Sign convention: adverse direction (price moved
    against us during the latency window) adds cost.
    """
    enabled = config.get("enabled_for_phase", [])
    current_phase = config.get("current_phase", "F")
    if current_phase not in enabled or walk.empty:
        return 0.0
    if exit_ticks <= 0 or exit_ticks > len(walk):
        return 0.0
    latency_ms = draw_latency_ms(seed=seed, component=component, config=config)
    if latency_ms <= 0.0:
        return 0.0
    # Anchor at the barrier-hit row; project latency_ms forward.
    hit_row = walk.iloc[exit_ticks - 1]
    hit_ts = hit_row["ts"]
    target_ts = hit_ts + pd.Timedelta(milliseconds=int(latency_ms))
    after = walk.loc[walk["ts"] >= target_ts]
    if after.empty:
        return 0.0
    fill_price = float(after.iloc[0]["price"])
    # slippage_latency_pts = sign × (mid_at_decision − mid_at_fill_after_latency)
    return float(sign) * (exit_raw - fill_price)


__all__ = [
    "LatencyComponent",
    "detect_circuit_breaker_fired",
    "detect_rollover_window",
    "detect_session_microstructure_flags",
    "draw_latency_ms",
    "latency_slippage_pts",
    "load_session_trades",
    "replay_event_walk",
]
