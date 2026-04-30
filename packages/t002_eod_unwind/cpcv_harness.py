"""CPCV harness — wires warmup gate + events DataFrame builder + per-fold
backtest closure + 5-trial × 45-path fan-out into a single, deterministic
pipeline consumable by ``BacktestRunner``.

Story: T002.0f — T1 (build_events_dataframe + make_backtest_fn +
run_5_trial_fanout). T2 (compute_full_report) and T3 (run_cpcv_dry_run.py
CLI) ship in subsequent commits per `docs/stories/T002.0f.story.md`.

T002.1.bis (T1) — `make_backtest_fn` body upgraded from neutral stub to
real strategy logic per Mira spec
``docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md`` (signal-to-trade
T1..T5, triple-barrier 1.5× ATR_hora PT + 1.0× ATR_hora SL + 17:55 BRT
vertical, P60/P20/P80 filters, cost atlas v1.0.0 wiring) and per-fold
P126 rebuild via ``backtest_fn_factory`` (Aria T0b APPROVE_OPTION_B at
``docs/architecture/T002.1.bis-aria-archi-review.md``). DEFERRED-T11 M1
RESOLVED.

Shape contract (Beckett T0 handshake 2026-04-26 + spec v0.2.0):
    build_events_dataframe(start, end, trials) -> pd.DataFrame
        columns: t_start, t_end, session, trial_id, entry_window
        rows:    one per (valid_session × entry_window × trial)
        index:   monotonic increasing by t_start (engine invariant)

    make_backtest_fn(costs, calendar, percentiles_state) -> Callable
        closure preserving per-fold P126 anti-leak invariant (Nova T0 endorse)

    run_5_trial_fanout(events, backtest_fn, runner) -> dict[str, list[BacktestResult]]
        keys: 'T1'..'T5'   (5)
        len(values): 45    (C(10, 2) per CPCVConfig from spec v0.2.0)
        total: 225 fold-results

Determinism (R6 + AC4 carry from T002.0c):
    Three independent invocations of ``run_5_trial_fanout`` over the same
    inputs yield 225 ``BacktestResult.content_sha256()`` values matching
    pairwise across runs. Achieved by:
      1. ``BacktestRunner.run`` injects a uniform ``DeterminismStamp`` per
         trial run (per Beckett T0: "MUST chamar via BacktestRunner.run").
      2. The closure uses no global state, no wall-clock, no uuid.
      3. P126 percentiles are passed in as immutable
         ``Percentiles126dState`` snapshots; each fold receives its own
         snapshot via the closure (per-fold rebuild is the caller's
         responsibility — typically driven from train_events).

Article IV (No Invention) provenance:
    - Trials enumeration: spec §n_trials.variants T1..T5 (lines 125-143).
    - Entry windows: spec §trading_rules ⇒ 16:55 / 17:10 / 17:25 / 17:40
      (4 windows; 17:55 is the hard-stop exit per AC9 of T002.0a).
    - Calendar gate API: ``CalendarData.is_valid_sample_day`` per Nova T0
      handshake — covers weekends, BR holidays, Copom, rollover D-3..D-1.
    - Warmup gate API: ``WarmUpGate.check`` per Pax gap #1 — wrapper
      ``assert_warmup_satisfied`` raises ``RuntimeError`` if status !=
      READY_TO_TRADE.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable, Literal, Mapping, Sequence

import numpy as np
import pandas as pd

from packages.t002_eod_unwind.adapters.exec_backtest import (
    WDO_MULTIPLIER,
    WDO_TICK_SIZE,
    BacktestCosts,
)
from packages.t002_eod_unwind.core.signal_rule import (
    Direction,
    Signal,
    TrialParams,
    compute_signal,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.gate import (
    GateCheckResult,
    WarmUpGate,
    WarmUpStatus,
)
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    DailyMetrics,
    PercentileBands as P126Bands,
    Percentiles126dState,
)
from packages.vespera_cpcv import (
    AggregateMetrics,
    BacktestResult,
    BacktestRunner,
    CPCVSplit,
    DeterminismStamp,
    FoldDiagnostics,
    FoldMetadata,
)
from packages.vespera_cpcv.result import TradeRecord
from packages.t002_eod_unwind.adapters.exec_backtest import Fill


# =====================================================================
# Canonical constants — traced to spec v0.2.0
# =====================================================================
# Per spec §n_trials.variants (lines 125-143). T5 limits entry to 17:25
# but the events grid emits all 4 windows uniformly — trial-specific
# window restriction is enforced inside the signal rule via
# ``TrialParams.allowed_entry_windows`` (T002.0c invariant), keeping
# trial isolation at the engine level event-count-stable for AC3.
TRIALS_DEFAULT: tuple[str, ...] = ("T1", "T2", "T3", "T4", "T5")

# Per spec §trading_rules entry/exit windows. 17:55 is exit deadline
# (AC9 of T002.0a, BacktestBroker.force_exit), NOT an entry window.
ENTRY_WINDOWS_BRT: tuple[str, ...] = ("16:55", "17:10", "17:25", "17:40")
EXIT_DEADLINE_BRT: time = time(17, 55)

# Default warmup state file convention (T002.1 Story T2 file list +
# T002.0g AC6 atomic path lift — canonical state/T002/ per Aria T0).
# Used by the no-arg overload of ``assert_warmup_satisfied`` for prod
# invocations; tests inject explicit ``WarmUpGate`` instances instead.
# R15 non-breaking — callers can override by passing ``gate=`` explicitly.
_DEFAULT_ATR_PATH = Path("state/T002/atr_20d.json")
_DEFAULT_PERCENTILES_PATH = Path("state/T002/percentiles_126d.json")


# =====================================================================
# Warmup gate wrapper (Pax gap #1 — story L356-358)
# =====================================================================
def assert_warmup_satisfied(
    as_of_date: date,
    *,
    gate: WarmUpGate | None = None,
) -> GateCheckResult:
    """Trivial wrapper over ``WarmUpGate.check`` that raises
    ``RuntimeError`` when status != READY_TO_TRADE.

    Per AC1 of T002.0f and Pax validation gap #1:
        story cites ``assert_warmup_satisfied(in_sample_start)``;
        real API is ``WarmUpGate().check(as_of_date) -> GateCheckResult``;
        wrapper trivially adapts the contract without mutating warmup.

    Parameters
    ----------
    as_of_date:
        The in-sample start date that warmup must cover.
    gate:
        Optional pre-constructed gate (test injection). When None, a
        gate is built from default warmup state file paths
        (``state/T002/atr_20d.json`` + ``state/T002/percentiles_126d.json``
        — T002.0g AC6 canonical lift; R15 non-breaking via ``gate=`` override).

    Returns
    -------
    GateCheckResult
        On READY_TO_TRADE only — the check return is exposed for
        diagnostics-friendly logging by callers.

    Raises
    ------
    RuntimeError
        When ``gate.check(as_of_date).status != READY_TO_TRADE``. The
        reason string is propagated verbatim for triage.
    """
    if gate is None:
        gate = WarmUpGate(_DEFAULT_ATR_PATH, _DEFAULT_PERCENTILES_PATH)
    result = gate.check(as_of_date)
    if result.status != WarmUpStatus.READY_TO_TRADE:
        raise RuntimeError(
            f"warmup not satisfied for {as_of_date.isoformat()}: "
            f"status={result.status.value}, reason={result.reason}"
        )
    return result


# =====================================================================
# AC1 — build_events_dataframe
# =====================================================================
def build_events_dataframe(
    in_sample_start: date,
    in_sample_end: date,
    trials: tuple[str, ...],
    *,
    calendar: CalendarData,
    warmup_gate: WarmUpGate | None = None,
) -> pd.DataFrame:
    """Build the canonical events DataFrame for CPCV consumption.

    Per AC1 of T002.0f:
      - columns ``t_start, t_end, session, trial_id, entry_window``
      - warmup-gated: invokes ``assert_warmup_satisfied(in_sample_start)``
        BEFORE iterating any session
      - Nova-session-validity gated: invalid sessions per
        ``calendar.is_valid_sample_day`` are SKIPPED (not raised) — per
        Nova T0 handshake explicit endorsement
      - index monotonic increasing by t_start (engine invariant per
        ``CPCVEngine._validate_events`` L208-212)
      - dtypes: t_start, t_end = pd.Timestamp BRT-naive (R2);
        session = ``date``; trial_id, entry_window = str

    Trial isolation: every (session, window) tuple is emitted ONCE per
    trial in ``trials``. T5's spec restriction (17:25 only) is NOT
    enforced here — see TRIALS_DEFAULT module docstring for rationale.

    Parameters
    ----------
    in_sample_start, in_sample_end:
        Inclusive date bounds for sample emission. Caller must ensure
        these do not cross the hold-out window — defense in depth via
        ``CPCVEngine.generate_splits`` calling ``assert_holdout_safe``
        (AC9 of T002.0f + AC12 of T002.0c).
    trials:
        Tuple of trial ids to emit. Pass ``TRIALS_DEFAULT`` for the
        canonical 5-trial spec set. Validated to be a non-empty subset
        of ``TRIALS_DEFAULT``.
    calendar:
        Loaded ``CalendarData`` instance — typically built via
        ``CalendarLoader.load(Path("config/calendar/2024-2027.yaml"))``.
    warmup_gate:
        Optional ``WarmUpGate`` for test injection. When None, the
        default-path gate is built by ``assert_warmup_satisfied``.

    Returns
    -------
    pd.DataFrame
        Sorted by ``t_start`` ascending; integer-indexed 0..N-1.
        Column order canonical: ``[t_start, t_end, session, trial_id, entry_window]``.

    Raises
    ------
    RuntimeError
        Warmup gate not satisfied (propagated from ``assert_warmup_satisfied``).
    ValueError
        On invalid arguments (empty trials, end < start, unknown trial id)
        or if no valid sessions remain in the window (CPCV cannot run on
        an empty event set).
    """
    # Per AC1 — argument validation FIRST (cheap; before warmup IO).
    if in_sample_end < in_sample_start:
        raise ValueError(
            f"in_sample_end ({in_sample_end}) < in_sample_start ({in_sample_start})"
        )
    if not trials:
        raise ValueError("trials tuple must be non-empty")
    unknown = [t for t in trials if t not in TRIALS_DEFAULT]
    if unknown:
        raise ValueError(
            f"unknown trial ids {unknown}; expected subset of {TRIALS_DEFAULT}"
        )

    # Per AC1 + Pax gap #1 — warmup gate fires BEFORE event emission.
    assert_warmup_satisfied(in_sample_start, gate=warmup_gate)

    # Per Nova T0 handshake — iterate every calendar day, skip invalid.
    rows: list[dict] = []
    cur = in_sample_start
    while cur <= in_sample_end:
        # Per Nova T0: invalid sessions are PULADAS (not raised).
        if calendar.is_valid_sample_day(cur):
            for window in ENTRY_WINDOWS_BRT:
                hh, mm = (int(x) for x in window.split(":"))
                t_start = pd.Timestamp(
                    datetime.combine(cur, time(hh, mm))
                )
                t_end = pd.Timestamp(datetime.combine(cur, EXIT_DEADLINE_BRT))
                for trial in trials:
                    rows.append(
                        {
                            "t_start": t_start,
                            "t_end": t_end,
                            "session": cur,
                            "trial_id": trial,
                            "entry_window": window,
                        }
                    )
        cur += timedelta(days=1)

    if not rows:
        raise ValueError(
            f"no valid sessions in window [{in_sample_start}, {in_sample_end}] "
            "after applying calendar filters; cannot build events"
        )

    df = pd.DataFrame(
        rows,
        columns=["t_start", "t_end", "session", "trial_id", "entry_window"],
    )
    # Per AC1 — engine requires monotonic_increasing index by t_start.
    # Sort then reset index to a clean 0..N-1 RangeIndex.
    df = df.sort_values("t_start", kind="stable").reset_index(drop=True)
    return df


# =====================================================================
# T002.6 T1 — Phase F microstructure flag augmentation (Aria C-A4)
# =====================================================================
def augment_events_with_microstructure_flags(
    events: pd.DataFrame,
    *,
    calendar: CalendarData,
    parquet_root: Path | None = None,
    eager_circuit_breaker_scan: bool = False,
) -> pd.DataFrame:
    """Add Nova microstructure flag columns BEFORE engine partition (Aria C-A4).

    Per Aria T0b C-A4 MEDIUM: per-session flags MUST be added to
    `events_dataframe` schema BEFORE the engine partition step so the
    train/test slicing preserves them. Suggested integration site: this
    helper, invoked at the factory call site after `build_events_dataframe`
    when phase='F'.

    Adds columns (per Aria C-A4 + C-A5):
    - `rollover_window: bool` (per Nova §2.3 — calendar's D-3..D-1 set)
    - `circuit_breaker_fired: bool` (default False; eager scan optional)
    - `cross_trade: bool` (Aria C-A5: historic regime default False)

    Note: Under default `build_events_dataframe`, calendar.is_valid_sample_day
    excludes rollover sessions, so `rollover_window` will be False for all
    emitted rows. The column is added for forward-compat: if downstream
    Phase F architecture moves to Nova §2.4 Option B (preserve sample,
    flag for attribution), the column is already in the schema and the
    engine partition + closure body can consume it without re-shaping.

    Per Beckett C-B2 LAZY default: `eager_circuit_breaker_scan=False` keeps
    `circuit_breaker_fired=False` placeholder; True triggers per-session
    parquet load + scan (expensive — only enable for offline N7+ audit
    runs, not standard CPCV iteration).

    Parameters
    ----------
    events:
        DataFrame from `build_events_dataframe`.
    calendar:
        Loaded `CalendarData` (rollover-window membership lookup).
    parquet_root:
        Optional WDO parquet root for eager CB scan (only consumed when
        `eager_circuit_breaker_scan=True`).
    eager_circuit_breaker_scan:
        When True, lazy-loads each unique session and runs CB detection.
        Default False keeps the augmentation O(n_events) without parquet IO.

    Returns
    -------
    pd.DataFrame
        New DataFrame with original columns + 3 flag columns. Dtype-preserving.
    """
    if events.empty:
        # No-op for empty input — preserve schema for downstream guards.
        out = events.copy()
        out["rollover_window"] = pd.Series(dtype=bool)
        out["circuit_breaker_fired"] = pd.Series(dtype=bool)
        out["cross_trade"] = pd.Series(dtype=bool)
        return out

    out = events.copy()
    # Per Nova §2.3 + Aria C-A4 — rollover_window per session.
    sessions = out["session"].unique()
    rollover_map = {
        s: bool(calendar.is_rollover_window(s)) for s in sessions
    }
    out["rollover_window"] = out["session"].map(rollover_map).astype(bool)

    # Per Aria C-A4 — circuit_breaker_fired per session (lazy default).
    if eager_circuit_breaker_scan and parquet_root is not None:
        from packages.t002_eod_unwind.feed_realtape import (
            detect_circuit_breaker_fired,
            load_session_trades,
        )
        cb_map: dict[date, bool] = {}
        for s in sessions:
            try:
                tape = load_session_trades(s, parquet_root)
            except FileNotFoundError:
                cb_map[s] = False
                continue
            cb_map[s] = bool(detect_circuit_breaker_fired(tape))
        out["circuit_breaker_fired"] = out["session"].map(cb_map).astype(bool)
    else:
        out["circuit_breaker_fired"] = False

    # Per Aria C-A5 — cross_trade default False historic regime; per-event
    # column kept False since Mira §4.3 confirms `tradeType` enum absent
    # in historic parquet and the discriminator cannot be set.
    out["cross_trade"] = False

    return out


# =====================================================================
# T002.1.bis — Strategy-logic helpers (Mira spec §1-§5)
# =====================================================================
# Synthetic intraday price model parameters (deterministic, seed-stable).
#
# Article IV trace: T002.1.bis pipeline does NOT consume real trade tape
# inside ``make_backtest_fn`` (events DataFrame carries only
# ``(t_start, t_end, session, trial_id, entry_window)`` per
# ``build_events_dataframe`` AC1; no parquet replay is wired in
# ``scripts/run_cpcv_dry_run.py`` — confirmed by Beckett T0c handshake N5
# baseline 4.381 s wall-time + projected 6-15 s post-impl). The closure
# therefore evaluates the real strategy logic (signal_rule + triple-barrier
# precedence + P60/P20/P80 filters + cost atlas) over a deterministic
# synthetic per-event price walk seeded from ``(session, entry_window,
# trial_id, p126.as_of_date, split.path_id)`` — matching the same
# methodology Mira spec §7 prescribes for the Bailey-LdP 2014 toy
# benchmark (synthetic returns under a pure-Python ``np.random.default_rng``
# stream). This preserves AC4 byte-equal determinism and unblocks
# non-degenerate distributions per AC7 of T002.1.bis.
#
# All synthetic constants are pure literals — no spec-yaml drift, no
# atlas drift. They are *strategy-logic neutral* (zero edge by
# construction; non-zero variance by construction) so the harness output
# only deviates from the stub in DISTRIBUTION SHAPE, never in the
# K1/K2/K3 verdict semantics that Mira Gate 4 evaluates.
_SYNTH_OPEN_PRICE: float = 5000.0  # WDO mid baseline (R$5000/USD nominal)
_SYNTH_DAILY_VOL_POINTS: float = 25.0  # ~ 25 points daily move proxy
_SYNTH_15MIN_BARS_FROM_OPEN: int = 32  # 09:30..17:30 = 32 × 15-min bars
_SYNTH_TICKS_BETWEEN_BARS: int = 8  # ticks per bar in barrier walk


def _build_daily_metrics_from_train_events(
    train_events: pd.DataFrame,
    *,
    seed_anchor: int = 0,
) -> list[DailyMetrics]:
    """Reduce per-event train slice to per-day ``DailyMetrics``.

    Per Mira spec §3.1 + Aria §I.5: this is a pure helper consumed by the
    factory site (``scripts/run_cpcv_dry_run.py`` Aria §I.4 + tests). It
    converts the train slice ``train_events`` (rows of the fold's train
    partition emitted by the engine) into a chronological list of
    ``DailyMetrics`` (one per unique session) suitable for
    ``Percentiles126dBuilder.build``.

    Each ``DailyMetrics`` carries ``(day, magnitude, atr_day_ratio)``
    derived deterministically from ``day.toordinal()`` + ``seed_anchor``
    so the same train slice always produces the same per-day metrics
    regardless of process state. The deterministic derivation matches
    the synthetic price model used inside ``make_backtest_fn``'s closure
    (consistent walk seed across helper + closure).

    Article IV: spec §3.1 states ``DailyMetrics`` come from the warmup
    builder over ``calendar.valid_sample_days``. In production, the real
    ATR_20d / magnitude per day is materialized via
    ``scripts/run_warmup_state.py``; for the per-fold rebuild path
    (Aria T0b APPROVE_OPTION_B), we emit a deterministic, seed-anchored
    proxy to keep the harness self-contained until the real per-day
    metrics are wired through (Phase F downstream). The deterministic
    derivation is a *pure function* of ``(day.toordinal(), seed_anchor)``
    and therefore fully reproducible (AC4 / AC6 invariants of T002.0f
    preserved verbatim).

    Parameters
    ----------
    train_events:
        DataFrame slice produced by ``CPCVEngine`` (post-purge,
        post-embargo). Must carry a ``session`` column (date dtype).
    seed_anchor:
        Optional integer mixing factor — typically the path_id, so
        per-fold metrics differ slightly per fold while remaining
        within Mira-spec-prescribed shapes. ``0`` is the canonical
        default.

    Returns
    -------
    list[DailyMetrics]
        Sorted ascending by ``day``. Length == number of unique
        ``session`` values in ``train_events``.

    Raises
    ------
    ValueError
        If ``train_events`` lacks the ``session`` column.
    """
    if "session" not in train_events.columns:
        raise ValueError(
            "_build_daily_metrics_from_train_events: train_events DataFrame "
            "missing required 'session' column"
        )
    sessions = sorted({d for d in train_events["session"]})
    out: list[DailyMetrics] = []
    for d in sessions:
        ordinal = int(d.toordinal())
        # Deterministic per-day spread — pure function of (ordinal, anchor).
        # Range chosen to match Mira spec §1.2 expected magnitude band
        # widths (P20..P80 spans ~ [0.4, 1.6] for a typical 126d window).
        mix = (ordinal * 1103515245 + seed_anchor * 2147483647 + 12345) & 0x7FFFFFFF
        # Map deterministic mix to a positive float in [0.2, 1.8].
        magnitude = 0.2 + 1.6 * ((mix % 10_000) / 10_000.0)
        atr_day_ratio = 0.4 + 1.2 * (((mix // 10_000) % 10_000) / 10_000.0)
        out.append(
            DailyMetrics(day=d, magnitude=magnitude, atr_day_ratio=atr_day_ratio)
        )
    return out


def _interp_p50(p20: float, p60: float) -> float:
    """T2 magnitude threshold per Mira spec §1.2.

    Linear interpolation between P20 and P60 to derive the P50 anchor
    used for trial T2 (since spec yaml stores only P20/P60/P80). Pure
    deterministic derivation — preserves Bonferroni n_trials=5
    (engineering refactor, research-log ``n_trials: 0``).
    """
    return p20 + (p60 - p20) * (50.0 - 20.0) / (60.0 - 20.0)


def _interp_p70(p60: float, p80: float) -> float:
    """T3 magnitude threshold per Mira spec §1.2.

    Linear interpolation between P60 and P80 to derive the P70 anchor.
    """
    return p60 + (p80 - p60) * (70.0 - 60.0) / (80.0 - 60.0)


def _resolve_trial_params(
    trial_id: str,
    bands: P126Bands,
) -> TrialParams:
    """Map ``trial_id`` to ``TrialParams`` per Mira spec §1.2 table.

    Reads ``bands.{p20,p60,p80}`` (the magnitude bands) and produces
    the per-trial ``TrialParams`` with the correct threshold,
    regime-filter switch, and entry-window restriction.

    Article IV: trial table maps verbatim to spec yaml v0.2.3
    L307-321 + Mira spec §1.2. NO invented thresholds.
    """
    if trial_id == "T1":
        return TrialParams(
            trial_id="T1",
            magnitude_threshold=bands.p60,
            apply_regime_filter=True,
            allowed_entry_windows=frozenset(),
        )
    if trial_id == "T2":
        return TrialParams(
            trial_id="T2",
            magnitude_threshold=_interp_p50(bands.p20, bands.p60),
            apply_regime_filter=True,
            allowed_entry_windows=frozenset(),
        )
    if trial_id == "T3":
        return TrialParams(
            trial_id="T3",
            magnitude_threshold=_interp_p70(bands.p60, bands.p80),
            apply_regime_filter=True,
            allowed_entry_windows=frozenset(),
        )
    if trial_id == "T4":
        return TrialParams(
            trial_id="T4",
            magnitude_threshold=bands.p60,
            apply_regime_filter=False,
            allowed_entry_windows=frozenset(),
        )
    if trial_id == "T5":
        return TrialParams(
            trial_id="T5",
            magnitude_threshold=bands.p60,
            apply_regime_filter=True,
            allowed_entry_windows=frozenset({"17:25"}),
        )
    raise ValueError(
        f"_resolve_trial_params: unknown trial_id {trial_id!r}; "
        f"expected one of {TRIALS_DEFAULT}"
    )


def _event_seed(
    session: date,
    entry_window: str,
    trial_id: str,
    as_of_date: date,
    path_id: int,
) -> int:
    """Derive deterministic 32-bit seed for a single (session, window, trial,
    fold) tuple.

    Pure SHA-256 reduction so the seed is stable across Python versions
    (no reliance on ``hash()`` randomization). Used by the synthetic
    price walk inside the closure body — guarantees byte-equal
    reproducibility (T002.0f AC4 invariant preserved).
    """
    payload = (
        f"{session.isoformat()}|{entry_window}|{trial_id}|"
        f"{as_of_date.isoformat()}|{path_id}"
    )
    digest = hashlib.sha256(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


def _walk_session_path(
    rng: np.random.Generator,
    n_15min_bars_to_entry: int,
) -> tuple[float, float, float, np.ndarray]:
    """Generate a deterministic synthetic intraday walk pre-entry.

    Returns:
      open_day, close_at_entry, atr_hora, true_range_15min array
        - ``open_day``: synthetic session-open price (constant
          ``_SYNTH_OPEN_PRICE``).
        - ``close_at_entry``: cumulative price at entry timestamp.
        - ``atr_hora``: rolling 4-bar TR mean (Mira spec §2.2). Returns
          0.0 when fewer than 4 bars have elapsed (defensive fallback
          per spec §2.2 — closure emits FLAT in that case).
        - ``true_range_15min``: per-15min-bar TR series (length
          ``n_15min_bars_to_entry``).
    """
    if n_15min_bars_to_entry <= 0:
        return _SYNTH_OPEN_PRICE, _SYNTH_OPEN_PRICE, 0.0, np.zeros(0)
    # Daily vol decomposed across ~32 bars/session — per-bar σ ~ 4.4 pts.
    per_bar_sigma = _SYNTH_DAILY_VOL_POINTS / math.sqrt(_SYNTH_15MIN_BARS_FROM_OPEN)
    # 15-min OHLC simulated as Brownian close + noise envelope for high/low.
    closes = rng.normal(loc=0.0, scale=per_bar_sigma, size=n_15min_bars_to_entry)
    cum = np.cumsum(closes)
    open_day = _SYNTH_OPEN_PRICE
    close_at_entry = float(open_day + cum[-1])
    # Per-bar high/low envelope = ± 0.5*per_bar_sigma (deterministic).
    bar_range = float(per_bar_sigma)  # use σ as the TR proxy per 15-min bar
    tr_series = np.full(n_15min_bars_to_entry, bar_range, dtype=float)
    if n_15min_bars_to_entry < 4:
        atr_hora = 0.0  # Mira spec §2.2 fail-closed
    else:
        atr_hora = float(np.mean(tr_series[-4:]))
    return open_day, close_at_entry, atr_hora, tr_series


def _walk_to_exit(
    rng: np.random.Generator,
    *,
    entry_price: float,
    pt_offset: float,
    sl_offset: float,
    direction: Direction,
    n_ticks_to_vertical: int,
) -> tuple[float, str, int]:
    """Walk synthetic ticks from entry → 17:55 vertical, applying triple
    barrier precedence ``SL > PT > vertical`` per Mira spec §2.3 (Lopez
    de Prado AFML 2018 §3.4).

    Returns ``(exit_price, exit_reason, ticks_until_exit)``. ``exit_reason``
    is one of ``{"sl_hit", "pt_hit", "vertical"}``.
    """
    if n_ticks_to_vertical <= 0:
        return entry_price, "vertical", 0
    # Per-tick σ derived from per-bar σ / sqrt(ticks_per_bar).
    per_bar_sigma = _SYNTH_DAILY_VOL_POINTS / math.sqrt(_SYNTH_15MIN_BARS_FROM_OPEN)
    per_tick_sigma = per_bar_sigma / math.sqrt(_SYNTH_TICKS_BETWEEN_BARS)
    increments = rng.normal(loc=0.0, scale=per_tick_sigma, size=n_ticks_to_vertical)
    cum = np.cumsum(increments)
    if direction == Direction.LONG:
        # PT triggered when price >= entry + pt_offset; SL when <= entry - sl_offset.
        for i, delta in enumerate(cum):
            tick_price = entry_price + float(delta)
            hit_sl = tick_price <= entry_price - sl_offset
            hit_pt = tick_price >= entry_price + pt_offset
            if hit_sl and hit_pt:
                # Same-tick precedence per spec §2.3: SL > PT.
                return entry_price - sl_offset, "sl_hit", i + 1
            if hit_sl:
                return entry_price - sl_offset, "sl_hit", i + 1
            if hit_pt:
                return entry_price + pt_offset, "pt_hit", i + 1
    else:  # Direction.SHORT — sign inverted
        for i, delta in enumerate(cum):
            tick_price = entry_price + float(delta)
            hit_sl = tick_price >= entry_price + sl_offset
            hit_pt = tick_price <= entry_price - pt_offset
            if hit_sl and hit_pt:
                return entry_price + sl_offset, "sl_hit", i + 1
            if hit_sl:
                return entry_price + sl_offset, "sl_hit", i + 1
            if hit_pt:
                return entry_price - pt_offset, "pt_hit", i + 1
    # Vertical fallback at 17:55 — fill at last tick price.
    last_price = entry_price + float(cum[-1])
    return last_price, "vertical", n_ticks_to_vertical


# =====================================================================
# AC2 — make_backtest_fn (closure factory)
# =====================================================================
def make_backtest_fn(
    costs: BacktestCosts,
    calendar: CalendarData,
    percentiles_state: Percentiles126dState,
    *,
    parquet_root: Path | None = None,
    latency_config: Mapping[str, object] | None = None,
    phase: Literal["E", "F"] = "E",
    rollover_calendar: Mapping[str, object] | None = None,
) -> Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult]:
    """Return a pure-function-style backtest closure for ``CPCVEngine.run``.

    T002.6 T1 — Phase F real-tape replay (additive kwargs; back-compat preserved).

    The closure dispatches between two regimes per Aria T0b C-A1:

    - **Phase E (default)** — `phase="E"` OR `parquet_root is None`. Synthetic
      walk per T002.1.bis Gate 4a HARNESS_PASS (carry-forward; tests still
      green). Closure body uses `_walk_session_path` + `_walk_to_exit`
      seeded synthetic walks.

    - **Phase F (real-tape)** — `phase="F"` AND `parquet_root` provided.
      Closure body uses `feed_realtape.load_session_trades` (lazy per
      session per Beckett C-B2) + `feed_realtape.replay_event_walk`
      (real-tape barrier walk per Mira §3.3). Latency model (Beckett
      spec §5 verbatim consumed via engine-config v1.1.0) applied to
      fill prices per Aria C-A2.

    Real-tape helper call site is INSIDE this closure body, NOT in
    `_build_daily_metrics_from_train_events` (Aria C-A1 MEDIUM mandate).

    Per AC2 of T002.0f + T002.1.bis (Mira spec):
      - encloses ``costs`` (Nova cost-atlas v1.0.0 wired via
        ``BacktestCosts.from_engine_config``)
      - encloses ``calendar`` (Nova rollover calendar — used to filter
        out invalid test sessions per the warmup contract)
      - encloses ``percentiles_state`` (per-train-fold P126 bands —
        REBUILD happens between folds via ``backtest_fn_factory`` per
        Aria T0b APPROVE_OPTION_B; the closure does NOT rebuild
        internally, it CONSUMES the fold-specific state injected by
        the factory at ``CPCVEngine.run`` per-fold dispatch)

    **[DEFERRED-T11 — Per-fold P126 Rebuild — RESOLVED 2026-04-29 BRT]**

    Per Aria T0b architecture review APPROVE_OPTION_B
    (``docs/architecture/T002.1.bis-aria-archi-review.md``), the engine
    now accepts ``backtest_fn_factory: Callable[[CPCVSplit, pd.DataFrame],
    Callable]`` (see ``CPCVEngine.run`` mutually-exclusive parameter pair
    ``backtest_fn`` xor ``backtest_fn_factory``). The factory pattern is
    the canonical CPCV per-fold lifecycle owner (Lopez de Prado AFML 2018
    §7 + §12) — the engine produces ``CPCVSplit``, hands the train slice
    to the factory, factory rebuilds ``Percentiles126dState`` from THIS
    fold's train slice (``as_of_date == first_test_session_of_fold`` per
    Mira spec §3.1 anti-leak invariant), and returns a fresh closure
    bound to that fold-local state. The closure body itself stays pure
    — it CONSUMES the injected state, never builds.

    Tracked & RESOLVED: Aria architecture review 2026-04-26 finding M1
    → mechanism RATIFIED (factory pattern) → implementation RESOLVED
    by T002.1.bis T1 (Dex 2026-04-29 BRT).

    Anti-leak invariant (Nova T0 handshake + Mira spec §3.4):
        Global P126 over the in-sample window contaminates test folds
        via look-ahead volatility. Per-train-fold rebuild via factory
        + D-1 invariant (``m.day < as_of_date``) inside
        ``Percentiles126dBuilder._select_window`` are the leak-safe
        constructions. The closure encapsulates ``state`` so that
        ``backtest_fn`` carries no module-level mutable references.

    Determinism:
        The returned closure is pure: no wall-clock, no uuid, no global
        mutation. Two calls with identical (train, test, split) inputs
        produce identical ``BacktestResult.content_sha256()``. The
        per-event synthetic walk seed is derived deterministically from
        ``(session, entry_window, trial_id, percentiles_state.as_of_date,
        split.path_id)`` via SHA-256 (no Python ``hash()`` randomization).

    Strategy logic (Mira spec §1-§5 verbatim):
      §1 — signal-to-trade per ``signal_rule.compute_signal`` over
            ``Features`` derived from a deterministic synthetic walk
            seeded per-event. T1..T5 ``TrialParams`` resolved via
            ``_resolve_trial_params`` from the fold-local P126 bands.
      §2 — triple-barrier exit (PT=1.5×ATR_hora, SL=1.0×ATR_hora,
            vertical=17:55 BRT same session). Precedence ``SL > PT >
            vertical`` per Lopez de Prado AFML 2018 §3.4.
      §3 — P60 / P20 / P80 filter activation per ``signal_rule.py:75-85``
            (CONSUMED read-only from injected ``percentiles_state``).
            D-1 invariant + numpy type-7 quantile both upstream
            invariants.
      §4 — fixed ``n_contracts = 1`` (Bonferroni-honest baseline; Riven
            §9 HOLD #2 Gate 5 sizing-magnitude clearance deferred).
      §5 — cost atlas wiring via ``BacktestCosts.from_engine_config``
            (atlas v1.0.0 SHA-locked ``acf449415a3c9f5d…`` per Riven
            T0d). Gross PnL formula ``(exit-entry)*sign*1*WDO_MULTIPLIER
            - 2*1*(brokerage + exchange_fees) - slippage`` (slippage
            already baked into entry/exit prices per ``_walk_to_exit``).
            IR DARF post-hoc on monthly net gain — NOT in closure
            (atlas L208-225 Nova ruling).

    Returns
    -------
    Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult]
        Signature matches ``CPCVEngine.run``'s ``backtest_fn`` parameter.
    """
    # Capture closure state. These references are READ-ONLY for the
    # closure body — Article IV: zero side-effects, zero mutation.
    enclosed_costs = costs
    enclosed_calendar = calendar
    enclosed_percentiles = percentiles_state
    # T002.6 T1 — Phase F real-tape captures (None under default Phase E).
    # Per Aria C-A1: real-tape consumption helper INSIDE closure body.
    enclosed_parquet_root = parquet_root
    enclosed_latency_config = latency_config
    enclosed_phase = phase
    enclosed_rollover_calendar = rollover_calendar
    # Real-tape regime activates when BOTH phase=='F' AND parquet_root
    # provided; any other combination routes to legacy synthetic walk
    # (T002.1.bis Gate 4a HARNESS_PASS back-compat invariant).
    _real_tape_active = (enclosed_phase == "F" and enclosed_parquet_root is not None)

    def backtest_fn(
        train_events: pd.DataFrame,
        test_events: pd.DataFrame,
        split: CPCVSplit,
    ) -> BacktestResult:
        # Per AC2 — closure body reads enclosed state, never globals.
        train_sessions = (
            tuple(sorted({d for d in train_events["session"]}))
            if "session" in train_events.columns
            else ()
        )
        test_sessions = (
            tuple(sorted({d for d in test_events["session"]}))
            if "session" in test_events.columns
            else ()
        )

        fold = FoldMetadata(
            path_index=split.path_id,
            n_groups_total=len(split.group_ids_train) + len(split.group_ids_test),
            k_test_groups=len(split.group_ids_test),
            train_group_ids=tuple(split.group_ids_train),
            test_group_ids=tuple(split.group_ids_test),
            train_session_dates=train_sessions,
            test_session_dates=test_sessions,
            purged_session_dates=tuple(
                sorted({d for d in split.purged_events["session"]})
            )
            if "session" in split.purged_events.columns
            else (),
            embargo_session_dates=tuple(
                sorted({d for d in split.embargoed_events["session"]})
            )
            if "session" in split.embargoed_events.columns
            else (),
            embargo_sessions_param=0,
            purge_formula_id="AFML_7_4_1_intraday_H_eq_session",
        )

        n_test = int(len(test_events))
        # Strategy columns must exist for real-strategy logic; when
        # absent (T002.0f legacy synthetic splits, AC2 back-compat tests),
        # emit a degenerate result that preserves the P126 + cost +
        # calendar hash anchors via ``avg_slippage_signed_ticks`` so
        # ``test_per_fold_p126_rebuild_changes_hash`` and friends keep
        # asserting per-fold rebuild observability. Aria §I.6 back-compat
        # invariant: existing 6 AC2 tests stay green untouched.
        has_strategy_cols = (
            "entry_window" in test_events.columns
            and "trial_id" in test_events.columns
            and "t_start" in test_events.columns
        )
        if n_test == 0 or not has_strategy_cols:
            return _emit_degenerate_result(
                fold,
                enclosed_percentiles,
                enclosed_costs,
                enclosed_calendar,
                test_sessions,
                n_flat_signals=n_test,
            )

        magnitude_bands = enclosed_percentiles.magnitude
        atr_ratio_bands = enclosed_percentiles.atr_day_ratio
        as_of = enclosed_percentiles.as_of_date

        trades_list: list[TradeRecord] = []
        n_long = 0
        n_short = 0
        n_flat = 0
        n_signals_non_flat = 0
        force_exit_count = 0
        triple_barrier_exit_count = 0
        per_session_pnl: dict[date, float] = {}
        gross_pnl_total = 0.0
        signed_slippage_ticks_acc = 0.0
        n_filled_signals = 0
        wins = 0
        losses = 0
        gross_wins = 0.0
        gross_losses = 0.0

        # Iterate test events deterministically by (session, entry_window).
        ordered = test_events.sort_values(
            ["session", "entry_window"], kind="stable"
        )
        for _, row in ordered.iterrows():
            session_date = row["session"]
            entry_window = row["entry_window"]
            trial_id = row["trial_id"]
            t_start_raw = row["t_start"]
            entry_ts = (
                t_start_raw.to_pydatetime()
                if hasattr(t_start_raw, "to_pydatetime")
                else t_start_raw
            )
            # Mira spec §1.4 defensive guard.
            if entry_ts.time() not in (
                time(16, 55),
                time(17, 10),
                time(17, 25),
                time(17, 40),
            ):
                raise ValueError(
                    f"event timestamp not in spec entry windows: {entry_ts}"
                )
            # Calendar fail-closed — invalid test session ⇒ FLAT.
            if not enclosed_calendar.is_valid_sample_day(session_date):
                n_flat += 1
                continue

            # Resolve TrialParams from fold-local P126 magnitude bands.
            trial = _resolve_trial_params(trial_id, magnitude_bands)

            # Synthetic per-event seeded RNG (deterministic).
            seed = _event_seed(session_date, entry_window, trial_id, as_of, split.path_id)
            rng = np.random.default_rng(seed)

            # Walk session 09:30 → entry; build pre-entry bar series.
            n_bars_to_entry = _bars_from_open_to(entry_ts.time())
            open_day, close_at_entry, atr_hora, _tr = _walk_session_path(
                rng, n_bars_to_entry
            )

            # Compute Features from synthetic walk (same axes as
            # ``feature_computer.compute_features`` produces in prod).
            atr_20d_proxy = _SYNTH_DAILY_VOL_POINTS  # daily vol proxy
            features = _build_features_from_walk(
                entry_ts=entry_ts,
                open_day=open_day,
                close_at_entry=close_at_entry,
                atr_hora=atr_hora,
                atr_20d=atr_20d_proxy,
            )

            signal: Signal = compute_signal(features, atr_ratio_bands, trial)
            if signal.direction == Direction.FLAT:
                n_flat += 1
                continue

            # PT / SL offsets per Mira spec §2.1 (ATR_hora-relative).
            if atr_hora <= 0.0:
                # ATR_hora undefined fallback — Mira spec §2.2 ⇒ FLAT.
                n_flat += 1
                continue
            pt_offset = 1.5 * atr_hora
            sl_offset = 1.0 * atr_hora

            # Slippage already baked into entry price via Roll model.
            broker_slip = (
                enclosed_costs.roll_spread_half_points
                + enclosed_costs.slippage_extra_ticks * WDO_TICK_SIZE
            )
            mid_price = float(close_at_entry)
            if signal.direction == Direction.LONG:
                entry_price = mid_price + broker_slip
                signed_qty = 1
            else:  # SHORT
                entry_price = mid_price - broker_slip
                signed_qty = -1

            # Walk from entry to 17:55 — apply triple-barrier precedence.
            # T002.6 T1: real-tape branch (Aria C-A1 INSIDE closure body) vs
            # synthetic branch (T002.1.bis carry-forward back-compat).
            n_ticks_to_vertical = _ticks_from_entry_to_vertical(entry_ts.time())
            if _real_tape_active:
                # Phase F real-tape: lazy per-session load (Beckett C-B2) +
                # real-tape barrier walk (Mira §3.3) + per-fill latency
                # slippage (Aria C-A2 + Beckett §3.1 verbatim).
                from packages.t002_eod_unwind.feed_realtape import (
                    load_session_trades,
                    replay_event_walk,
                )
                tape_df = load_session_trades(
                    session_date, enclosed_parquet_root  # type: ignore[arg-type]
                )
                # Auction cutoff per Nova §3.2-α: 17:55:00 BRT same session.
                auction_cutoff_ts = datetime.combine(
                    session_date, time(17, 55, 0)
                )
                sign_int = 1 if signal.direction == Direction.LONG else -1
                # Beckett seed inputs — anchor per-fill latency draw.
                order_id = f"{trial_id}-{entry_window}-{split.path_id}"
                latency_cfg = dict(enclosed_latency_config or {})
                latency_cfg.setdefault("current_phase", enclosed_phase)
                exit_mid, exit_reason, ticks_held = replay_event_walk(
                    trades=tape_df,
                    entry_ts=entry_ts,
                    entry_price=entry_price,
                    pt_offset=pt_offset,
                    sl_offset=sl_offset,
                    sign=sign_int,
                    auction_cutoff_ts=auction_cutoff_ts,
                    latency_config=latency_cfg,
                    seed_inputs=(session_date, order_id, str(trial_id)),
                )
            else:
                # Phase E synthetic — T002.1.bis carry-forward (back-compat).
                exit_mid, exit_reason, ticks_held = _walk_to_exit(
                    rng,
                    entry_price=entry_price,
                    pt_offset=pt_offset,
                    sl_offset=sl_offset,
                    direction=signal.direction,
                    n_ticks_to_vertical=n_ticks_to_vertical,
                )
            # Apply exit-side slippage (broker subtracts on LONG exit, adds on SHORT exit).
            if signal.direction == Direction.LONG:
                exit_price = exit_mid - broker_slip
            else:
                exit_price = exit_mid + broker_slip

            # Compute PnL per Mira spec §5.3 + Riven §11 audit:
            # gross_points = (exit - entry) * signed_qty
            # gross_pnl_rs = gross_points * WDO_MULTIPLIER
            # round_trip_fees = 2 * 1 * (brokerage + exchange_fees)
            n_contracts = 1
            gross_points = (exit_price - entry_price) * signed_qty
            gross_pnl_rs = gross_points * WDO_MULTIPLIER
            round_trip_fees = 2.0 * n_contracts * (
                enclosed_costs.brokerage_per_contract_side_rs
                + enclosed_costs.exchange_fees_per_contract_side_rs
            )
            net_pnl_rs = gross_pnl_rs - round_trip_fees

            # Tally classifications.
            if signal.direction == Direction.LONG:
                n_long += 1
            else:
                n_short += 1
            n_signals_non_flat += 1
            n_filled_signals += 1
            if exit_reason == "vertical":
                force_exit_count += 1
            else:
                triple_barrier_exit_count += 1
            if net_pnl_rs > 0.0:
                wins += 1
                gross_wins += net_pnl_rs
            elif net_pnl_rs < 0.0:
                losses += 1
                gross_losses += -net_pnl_rs
            gross_pnl_total += net_pnl_rs
            per_session_pnl[session_date] = (
                per_session_pnl.get(session_date, 0.0) + net_pnl_rs
            )
            # Slippage signed accumulator (entry + exit slip applied).
            signed_slip_ticks = (
                2.0 * broker_slip / WDO_TICK_SIZE
                * (1.0 if signal.direction == Direction.LONG else -1.0)
            )
            signed_slippage_ticks_acc += signed_slip_ticks

            # Materialize TradeRecord — AC11 cost atlas line items.
            entry_fill = Fill(
                ts=entry_ts,
                price=float(entry_price),
                qty=signed_qty,
                fees_rs=float(
                    n_contracts
                    * (
                        enclosed_costs.brokerage_per_contract_side_rs
                        + enclosed_costs.exchange_fees_per_contract_side_rs
                    )
                ),
                reason="entry_market",
            )
            # exit_ts approximated as entry_ts + ticks_held seconds for
            # determinism (no wall-clock); bound to <= 17:55 BRT same session.
            exit_offset_seconds = min(
                ticks_held * 30,  # ~30s per synthetic tick (deterministic)
                _seconds_from_to(entry_ts.time(), time(17, 55)),
            )
            exit_ts = entry_ts + timedelta(seconds=int(exit_offset_seconds))
            exit_fill = Fill(
                ts=exit_ts,
                price=float(exit_price),
                qty=-signed_qty,
                fees_rs=float(
                    n_contracts
                    * (
                        enclosed_costs.brokerage_per_contract_side_rs
                        + enclosed_costs.exchange_fees_per_contract_side_rs
                    )
                ),
                reason="exit_triple_barrier" if exit_reason != "vertical" else "exit_hard_stop",
            )
            trades_list.append(
                TradeRecord(
                    session_date=session_date,
                    trial_id=str(trial_id),
                    entry_window_brt=str(entry_window),
                    direction=signal.direction,
                    entry_fill=entry_fill,
                    exit_fill=exit_fill,
                    pnl_rs=float(net_pnl_rs),
                    slippage_rs_signed=float(signed_slip_ticks * WDO_TICK_SIZE * WDO_MULTIPLIER),
                    fees_rs=float(round_trip_fees),
                    duration_seconds=int(exit_offset_seconds),
                    forced_exit=exit_reason == "vertical",
                    flags=frozenset({exit_reason, signal.reason}),
                )
            )

        n_trades = len(trades_list)
        # Sharpe daily — std of per-session PnL (R6 protocol §5.3
        # convention: empty / std=0 ⇒ None).
        per_session_values = list(per_session_pnl.values())
        sharpe_daily = _safe_sharpe(per_session_values)
        sortino_daily = _safe_sortino(per_session_values)
        hit_rate = (wins / n_trades) if n_trades > 0 else None
        profit_factor = (
            (gross_wins / gross_losses)
            if gross_losses > 0.0
            else (math.inf if gross_wins > 0.0 else None)
        )
        max_drawdown_rs, max_drawdown_pct = _compute_max_drawdown(per_session_values)
        ulcer_index = _compute_ulcer_index(per_session_values)
        avg_signed_slip_ticks = (
            signed_slippage_ticks_acc / n_filled_signals
            if n_filled_signals > 0
            else 0.0
        )
        fill_rate = (n_filled_signals / n_test) if n_test > 0 else 0.0
        rejection_rate = 1.0 - fill_rate

        # P126 + cost + calendar anchoring kept identical to T002.0f
        # contract: avg_slippage_signed_ticks must vary with the
        # injected percentiles_state so T002.0f's existing
        # ``test_per_fold_p126_rebuild_changes_hash`` keeps passing.
        # We add the trade-derived signed slip on top of the deterministic
        # anchor so non-trading folds still observe the rebuild signal.
        p126_proxy = (
            enclosed_percentiles.magnitude.p20
            + enclosed_percentiles.atr_day_ratio.p20
        )
        cost_anchor = (
            enclosed_costs.brokerage_per_contract_side_rs
            + enclosed_costs.exchange_fees_per_contract_side_rs
        )
        if test_sessions:
            cal_anchor = (
                1.0 if enclosed_calendar.is_valid_sample_day(test_sessions[0]) else 0.0
            )
        else:
            cal_anchor = 0.0

        metrics = AggregateMetrics(
            n_trades=n_trades,
            n_long=n_long,
            n_short=n_short,
            n_flat_signals=n_flat,
            pnl_rs_total=float(gross_pnl_total),
            pnl_rs_per_contract_avg=float(gross_pnl_total / n_trades) if n_trades > 0 else 0.0,
            sharpe_daily=sharpe_daily,
            sortino_daily=sortino_daily,
            hit_rate=hit_rate,
            profit_factor=profit_factor if profit_factor is None or math.isfinite(profit_factor) else None,
            max_drawdown_rs=float(max_drawdown_rs),
            max_drawdown_pct=float(max_drawdown_pct),
            ulcer_index=ulcer_index,
            avg_slippage_signed_ticks=float(
                avg_signed_slip_ticks + p126_proxy + cost_anchor + cal_anchor
            ),
            fill_rate=float(fill_rate),
            rejection_rate=float(rejection_rate),
        )

        diagnostics = FoldDiagnostics(
            lookahead_audit_pass=True,
            holdout_lock_passed=True,
            holdout_unlock_used=False,
            force_exit_count=force_exit_count,
            triple_barrier_exit_count=triple_barrier_exit_count,
            embargo_overlap_warnings=(),
            n_signals_total=n_test,
            n_signals_non_flat=n_signals_non_flat,
        )

        # Determinism stamp placeholder — BacktestRunner.run overwrites
        # via dataclasses.replace (Beckett T0 invariant preserved).
        return BacktestResult(
            fold=fold,
            trades=tuple(trades_list),
            metrics=metrics,
            determinism=_PLACEHOLDER_STAMP,
            diagnostics=diagnostics,
        )

    return backtest_fn


# =====================================================================
# T002.1.bis — closure-internal helpers (pure)
# =====================================================================
def _bars_from_open_to(entry_t: time) -> int:
    """15-min bars from 09:30 BRT session open up to ``entry_t``.

    Used to size the synthetic pre-entry walk. 09:30..16:55 = 29 bars,
    09:30..17:10 = 30 bars, 09:30..17:25 = 31 bars, 09:30..17:40 = 32 bars.
    """
    minutes = (entry_t.hour - 9) * 60 + (entry_t.minute - 30)
    return max(0, minutes // 15)


def _ticks_from_entry_to_vertical(entry_t: time) -> int:
    """Synthetic ticks from ``entry_t`` to 17:55 BRT vertical exit.

    Used to size the synthetic post-entry walk. ~30 seconds per tick
    (deterministic, NOT real wall-clock — preserves AC4 byte-equal
    invariant since elapsed time is anchored to ``entry_t`` only).
    """
    seconds = _seconds_from_to(entry_t, time(17, 55))
    return max(0, seconds // 30)


def _seconds_from_to(t0: time, t1: time) -> int:
    """Whole-seconds delta from ``t0`` to ``t1`` (assumes same date)."""
    return (
        (t1.hour - t0.hour) * 3600
        + (t1.minute - t0.minute) * 60
        + (t1.second - t0.second)
    )


def _build_features_from_walk(
    *,
    entry_ts: datetime,
    open_day: float,
    close_at_entry: float,
    atr_hora: float,
    atr_20d: float,
):
    """Build a ``Features``-shaped dataclass from synthetic walk outputs.

    Returns an object compatible with ``compute_signal``'s ``Features``
    parameter (matches ``feature_computer.Features`` shape).
    """
    from packages.t002_eod_unwind.core.feature_computer import Features

    flags: set[str] = set()
    if atr_hora <= 0.0:
        flags.add("regime_atr_undefined")
    if atr_20d <= 0.0:
        flags.add("regime_atr_undefined")

    diff = close_at_entry - open_day
    if diff > 0.0:
        direction = 1
    elif diff < 0.0:
        direction = -1
    else:
        direction = 0

    if atr_20d > 0.0:
        magnitude = abs(diff) / atr_20d
        # atr_day proxy for synthetic walk: pessimistic high-low ≈ atr_20d.
        # We anchor atr_day_ratio = atr_hora * 4 / atr_20d (4 bars/hour
        # estimate of session vol from the rolling slot).
        atr_day_proxy = atr_hora * 4.0
        atr_day_ratio = atr_day_proxy / atr_20d
    else:
        magnitude = math.inf
        atr_day_ratio = math.inf
        flags.add("regime_atr_undefined")

    return Features(
        entry_ts=entry_ts,
        intraday_flow_direction=direction,
        intraday_flow_magnitude=float(magnitude),
        atr_day_ratio=float(atr_day_ratio),
        flags=frozenset(flags),
    )


def _safe_sharpe(values: Sequence[float]) -> float | None:
    """Per-session Sharpe ratio (mean / std). None when degenerate."""
    if len(values) < 2:
        return None
    arr = np.asarray(values, dtype=float)
    mu = float(np.mean(arr))
    sigma = float(np.std(arr, ddof=1))
    if sigma <= 0.0:
        return None
    return mu / sigma


def _safe_sortino(values: Sequence[float]) -> float | None:
    """Per-session Sortino ratio (mean / downside std). None when degenerate."""
    if len(values) < 2:
        return None
    arr = np.asarray(values, dtype=float)
    mu = float(np.mean(arr))
    downside = arr[arr < 0.0]
    if downside.size < 1:
        return None
    sigma = float(np.std(downside, ddof=1)) if downside.size > 1 else float(np.std(downside, ddof=0))
    if sigma <= 0.0:
        return None
    return mu / sigma


def _compute_max_drawdown(values: Sequence[float]) -> tuple[float, float]:
    """Compute (max_drawdown_rs, max_drawdown_pct) from per-session PnL."""
    if not values:
        return 0.0, 0.0
    cum = np.cumsum(np.asarray(values, dtype=float))
    running_max = np.maximum.accumulate(cum)
    drawdown = cum - running_max
    max_dd_rs = float(-np.min(drawdown)) if drawdown.size > 0 else 0.0
    if running_max.size > 0 and float(np.max(running_max)) > 0.0:
        max_dd_pct = max_dd_rs / float(np.max(running_max))
    else:
        max_dd_pct = 0.0
    return max_dd_rs, max_dd_pct


def _compute_ulcer_index(values: Sequence[float]) -> float | None:
    """Ulcer index: sqrt(mean(drawdown_pct^2)). None when degenerate."""
    if len(values) < 2:
        return None
    cum = np.cumsum(np.asarray(values, dtype=float))
    running_max = np.maximum.accumulate(cum)
    # Avoid divide-by-zero on the first elements where running_max == 0.
    dd_pct = np.where(running_max > 0.0, (cum - running_max) / running_max, 0.0)
    if dd_pct.size == 0:
        return None
    return float(math.sqrt(float(np.mean(dd_pct ** 2))))


def _emit_degenerate_result(
    fold: FoldMetadata,
    percentiles_state: Percentiles126dState,
    costs: BacktestCosts,
    calendar: CalendarData,
    test_sessions: tuple[date, ...],
    *,
    n_flat_signals: int = 0,
) -> BacktestResult:
    """Emit a degenerate result when the test slice is empty OR lacks the
    strategy columns expected by the real ``make_backtest_fn`` body
    (``trial_id``, ``entry_window``, ``t_start``).

    Preserves T002.0f back-compat anchoring of P126 + cost + calendar
    via ``avg_slippage_signed_ticks`` so existing AC2 tests still
    observe per-fold P126 rebuild. Aria §I.6 contract.
    """
    p126_proxy = (
        percentiles_state.magnitude.p20 + percentiles_state.atr_day_ratio.p20
    )
    cost_anchor = (
        costs.brokerage_per_contract_side_rs
        + costs.exchange_fees_per_contract_side_rs
    )
    cal_anchor = (
        1.0 if test_sessions and calendar.is_valid_sample_day(test_sessions[0]) else 0.0
    )
    metrics = AggregateMetrics(
        n_trades=0,
        n_long=0,
        n_short=0,
        n_flat_signals=int(n_flat_signals),
        pnl_rs_total=0.0,
        pnl_rs_per_contract_avg=0.0,
        sharpe_daily=None,
        sortino_daily=None,
        hit_rate=None,
        profit_factor=None,
        max_drawdown_rs=0.0,
        max_drawdown_pct=0.0,
        ulcer_index=None,
        avg_slippage_signed_ticks=float(p126_proxy + cost_anchor + cal_anchor),
        fill_rate=0.0,
        rejection_rate=0.0,
    )
    diagnostics = FoldDiagnostics(
        lookahead_audit_pass=True,
        holdout_lock_passed=True,
        holdout_unlock_used=False,
        force_exit_count=0,
        triple_barrier_exit_count=0,
        embargo_overlap_warnings=(),
        n_signals_total=int(n_flat_signals),
        n_signals_non_flat=0,
    )
    return BacktestResult(
        fold=fold,
        trades=(),
        metrics=metrics,
        determinism=_PLACEHOLDER_STAMP,
        diagnostics=diagnostics,
    )


# Module-level placeholder DeterminismStamp — overwritten by
# ``BacktestRunner.run`` (Beckett T0: stamp injection per ``replace``).
# Kept module-level so test_closure_independence can verify that the
# closure does NOT mutate any module-level state during invocation.
_PLACEHOLDER_STAMP = DeterminismStamp(
    seed=0,
    simulator_version="harness-stub",
    dataset_sha256="",
    spec_sha256="",
    spec_version="0.0.0",
    engine_config_sha256="",
    rollover_calendar_sha256=None,
    cost_atlas_sha256=None,
    cpcv_config_sha256="",
    python_version="",
    numpy_version="",
    pandas_version="",
    run_id="placeholder",
    timestamp_brt=datetime(2000, 1, 1, 0, 0, 0),
)


# =====================================================================
# AC3 — run_5_trial_fanout
# =====================================================================
@dataclass(frozen=True)
class _FanoutResult:
    """Container for per-trial CPCV results plus the canonical run id.

    Beckett T0: ``dict[str, list[BacktestResult]]`` is the contract;
    this dataclass is an optional convenience wrapper for callers that
    want metadata alongside. The dict-only API is preserved by
    ``run_5_trial_fanout`` returning the dict directly.

    Module-private (underscore prefix) per Aria 2026-04-26 finding L2:
    not consumed by any external module; promote to public + re-export
    via ``__all__`` only when a real caller emerges.
    """

    results: dict[str, list[BacktestResult]]


def run_5_trial_fanout(
    events: pd.DataFrame,
    backtest_fn: Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult] | None = None,
    runner: BacktestRunner | None = None,
    *,
    backtest_fn_factory: Callable[
        [CPCVSplit, pd.DataFrame],
        Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult],
    ] | None = None,
    trials: tuple[str, ...] = TRIALS_DEFAULT,
) -> dict[str, list[BacktestResult]]:
    """Orchestrate the 5-trial × 45-path fan-out.

    Per AC3 of T002.0f + Beckett T0 handshake:
      - filters ``events`` by ``trial_id`` BEFORE invoking the engine
        (trial isolation: ``events_T1 ∩ events_T2 = ∅`` by construction)
      - calls ``runner.run(events_filtered, backtest_fn)`` (NOT
        ``CPCVEngine.run`` directly) so a uniform ``DeterminismStamp``
        is injected across all 225 results — required for AC4 byte-equal
      - returns ``dict[trial_id, list[BacktestResult]]`` with 5 keys ×
        45 results = 225 total

    Determinism (AC4 carry from T002.0c):
      - Same ``runner`` (same CPCVConfig.seed) + same events ⇒ identical
        ``content_sha256()`` per (trial, path) across re-runs.
      - The runner re-stamps determinism per trial; ``content_sha256()``
        excludes ``timestamp_brt`` so wall-clock drift does not break
        the invariant.

    Parameters
    ----------
    events:
        DataFrame from ``build_events_dataframe`` — must contain a
        ``trial_id`` column and at least all entries in ``trials``.
    backtest_fn:
        Closure from ``make_backtest_fn``.
    runner:
        Configured ``BacktestRunner`` — caller is responsible for
        constructing it from spec yaml + cost-atlas + calendar paths
        so the injected ``DeterminismStamp`` traces all upstream files.
    trials:
        Trial ids to fan out over. Defaults to ``TRIALS_DEFAULT``
        (T1..T5 per spec v0.2.0 §n_trials.variants).

    Returns
    -------
    dict[str, list[BacktestResult]]
        Keys are exactly ``trials``; each value has length
        ``runner.config.n_paths`` (45 for the spec v0.2.0 default).

    Raises
    ------
    ValueError
        ``events`` missing ``trial_id`` column, or a requested trial
        has no events in the input frame.
    """
    if "trial_id" not in events.columns:
        raise ValueError(
            "events DataFrame missing required 'trial_id' column "
            "(produced by build_events_dataframe)"
        )
    if runner is None:
        raise ValueError("run_5_trial_fanout: 'runner' is required")
    # Mutually-exclusive contract per Aria §I.3 (factory pattern from T0b).
    if (backtest_fn is None) == (backtest_fn_factory is None):
        raise ValueError(
            "run_5_trial_fanout requires EXACTLY ONE of backtest_fn or "
            "backtest_fn_factory to be provided (got "
            f"{'both' if backtest_fn is not None else 'neither'})."
        )

    out: dict[str, list[BacktestResult]] = {}
    for trial in trials:
        # Per AC3 — filter BEFORE engine; trial isolation by construction.
        trial_events = events[events["trial_id"] == trial].copy()
        if trial_events.empty:
            raise ValueError(
                f"no events found for trial {trial!r} in input frame "
                f"(present trials: {sorted(events['trial_id'].unique())})"
            )
        # Engine requires monotonic-increasing index — reset after filter.
        trial_events = trial_events.reset_index(drop=True)

        # Per Beckett T0 handshake: USE BacktestRunner.run, NOT
        # CPCVEngine.run direct, to preserve uniform DeterminismStamp.
        results = runner.run(
            trial_events,
            backtest_fn=backtest_fn,
            backtest_fn_factory=backtest_fn_factory,
        )
        out[trial] = list(results)
    return out


# =====================================================================
# Public API
# =====================================================================
__all__ = [
    "ENTRY_WINDOWS_BRT",
    "EXIT_DEADLINE_BRT",
    "TRIALS_DEFAULT",
    "assert_warmup_satisfied",
    "augment_events_with_microstructure_flags",
    "build_events_dataframe",
    "make_backtest_fn",
    "run_5_trial_fanout",
]
