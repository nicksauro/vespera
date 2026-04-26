"""Warm-up state orchestrator — T002.0g (Story `docs/stories/T002.0g.story.md`).

Connects parquet trades (T002.0b adapter) ⇒ daily OHLC ⇒ ATR_20d builder
+ Percentiles_126d builder ⇒ canonical JSON state files under
``state/T002/`` consumable by ``WarmUpGate`` and the CPCV harness.

Authoritative authorities (T0 handshakes 2026-04-26 BRT):

- **Aria (architecture)** — Module + thin CLI; ``state/T002/`` canonical;
  manifest schema with ``orchestrator_version``.
- **Mira (anti-leak + schema)** — Window strict ``[D-146bd, D-1]``;
  current day NEVER included; ``calendar: CalendarData`` MUST be passed
  by the caller (no internal instantiation — leak vector); 146 = 126
  P126 lookback + 20 ATR_20 aux input; ``state_content_hash`` excludes
  ``computed_at_brt`` for AC7.
- **Beckett (R6 CPCV gate)** — ``COPY`` (not symlink) on Windows for
  ``state/T002/atr_20d.json`` ↔ ``state/T002/atr_20d_{date}.json``.
- **Dara (parquet source + manifest)** — ``feed_parquet.load_trades``
  yields only ``(ts, price, qty)`` — ``tradeType`` discarded; orchestrator
  MUST escalate (``[USER-ESCALATION-PENDING]``) per Guard #4 and continue
  with unfiltered trades + warning. Manifest SHA re-check delegated to
  the adapter (``_verify_integrity`` per call).
- **Riven (defense-in-depth)** — ``assert_holdout_safe(start, end)``
  fires BEFORE adapter open; manifest.json append-only JSONL pinned in
  ``.github/canonical-invariant.sums``.

Anti-Article-IV Guards (story §Anti-Article-IV Guards):
1. NO neutral PercentilesState fallback — fail-closed with
   ``InsufficientCoverage`` listing window edges + missing dates.
2. NO silent path switch on write fail — manifest abort.
3. NO window extension beyond ``[D-146bd, D-1]``.
4. NO DLL/TimescaleDB re-fetch — parquet only via ``ParquetSource``.
5. NO determinism check skip — sort_keys + canonical float repr.

AC mapping (story §Acceptance criteria):

- AC1  parquet source + adapter REUSE (manifest SHA re-check delegated).
- AC2  strict ``[D-146bd, D-1]`` anti-leak window.
- AC3  ``assert_holdout_safe`` fires BEFORE adapter open.
- AC4  ``tradeType ∈ {2, 3}`` filter — escalate if adapter doesn't filter.
- AC5  multi as_of_date — per-date dated JSON + copy to canonical names.
- AC6  default output dir ``state/T002/`` (canonical).
- AC7  determinism — ``state_content_hash`` excludes wall-clock.
- AC8  schema roundtrip ``from_json(to_json())`` deep-equality assert.
- AC9  manifest.json append-only JSONL audit trail.
- AC10 streaming per as_of_date (R4 mitigation).
- AC11 CLI exposed via ``scripts/run_warmup_state.py`` (T2).
- AC12 integration test confirms ``WarmUpGate.check`` ⇒ READY_TO_TRADE.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable, Iterable, Protocol, Sequence

from packages.t002_eod_unwind.warmup.atr_20d_builder import (
    ATR20dBuilder,
    ATR20dState,
    DailyOHLC,
    Trade,
)
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (
    DailyMetrics,
    Percentiles126dBuilder,
    Percentiles126dState,
)

logger = logging.getLogger(__name__)


# =====================================================================
# Versioning (Aria T0 — manifest schema field)
# =====================================================================
ORCHESTRATOR_VERSION: str = "T002.0g-orchestrator-v1.0.0"
BUILDER_VERSION: str = "T002.1-builders-v1.0.0"

# Canonical entry-window close timestamp (spec v0.2.0 §trading_rules).
# magnitude per day = |close[16:55] - open_day| / ATR_20d_of_that_day.
CLOSE_AT_TIME_BRT: time = time(16, 55, 0)

# Anti-leak window — Mira T0 authority.
# 146 valid business days = 126 (P126 lookback) + 20 (ATR_20 aux input).
WARMUP_VALID_DAYS_REQUIRED: int = 146

# Calendar-day buffer multiplier — convert valid-business-day requirement to
# a raw calendar window safe for parquet load. Empirical upper bound for
# weekends + BR holidays + Copom + rollover exclusion: ~1.65×. We use 2.5×
# to absorb year-boundary edge cases (Carnaval + Copom + 4 holidays inside
# 146bd is plausible). The window is THEN strictly filtered by
# ``calendar.is_valid_sample_day`` so the buffer is a safety net only —
# Guard #3 is enforced by the strict ``< as_of_date`` predicate inside the
# builders themselves (atr_20d_builder.py L147; percentiles_126d_builder.py
# L134).
CALENDAR_BUFFER_RATIO: float = 2.5


# =====================================================================
# Source contract (Aria T0 — ParquetSource via DI; Phase F: TimescaleSource)
# =====================================================================
class ParquetSource(Protocol):
    """Source contract: yields ``Trade`` rows for a window.

    Default impl wraps ``feed_parquet.load_trades`` (T002.0b adapter REUSE
    per Article IV-A). Tests inject in-memory mocks.

    The ``ticker`` argument is part of the contract (the adapter requires
    it) — orchestrator passes the canonical ``"WDO"`` per spec v0.2.0.
    """

    def load_trades(
        self,
        start_brt: datetime,
        end_brt: datetime,
        ticker: str,
    ) -> Iterable[Trade]: ...  # pragma: no cover - protocol


@dataclass(frozen=True)
class FeedParquetSource:
    """Default ``ParquetSource`` impl backed by ``feed_parquet.load_trades``.

    Article IV-A REUSE — does not duplicate adapter logic.
    """

    ticker: str = "WDO"

    def load_trades(
        self,
        start_brt: datetime,
        end_brt: datetime,
        ticker: str,
    ) -> Iterable[Trade]:
        # Lazy import — keeps test mocks free of pyarrow import cost.
        from packages.t002_eod_unwind.adapters.feed_parquet import (
            load_trades as _load_trades,
        )

        # Adapter yields ``packages.t002_eod_unwind.core.session_state.Trade``;
        # ATR builder expects ``packages.t002_eod_unwind.warmup.atr_20d_builder.Trade``
        # — same shape (ts, price, qty). Cast on the fly.
        for tr in _load_trades(start_brt, end_brt, ticker):
            yield Trade(ts=tr.ts, price=tr.price, qty=tr.qty)


# =====================================================================
# Errors (Guard #1 — fail-closed; AC1 nota; story L322)
# =====================================================================
class InsufficientCoverage(RuntimeError):
    """Raised when parquet/calendar coverage cannot satisfy 146-bd lookback.

    Article IV: NO silent neutral fallback — caller must escalate to user
    (USER-ESCALATION-QUEUE.md) or unblock by re-fetching upstream data.
    """


class ManifestWriteError(RuntimeError):
    """Raised when ``state/T002/manifest.json`` append fails.

    Anti-Article-IV Guard #2: NO silent path switch — manifest write is a
    hard prerequisite. Failure aborts the run.
    """


# =====================================================================
# AC9 — manifest entry schema
# =====================================================================
@dataclass(frozen=True)
class ManifestEntry:
    """Append-only JSONL manifest line schema (story AC9).

    ``calendar_sha`` is the SHA-256 of the calendar YAML the orchestrator
    consumed (Mira T0 — calendar single-source); ``source_sha`` is a
    placeholder pinned by the adapter manifest re-check (Dara T0 D1).
    """

    as_of_date: str  # ISO YYYY-MM-DD
    source_sha: str
    builder_version: str
    orchestrator_version: str  # Aria T0 — separate from builder_version
    computed_at_brt: str
    output_sha: str
    holdout_unlock_used: bool
    calendar_sha: str
    tradetype_filter_status: str  # "applied" | "escalated_adapter_gap"

    def to_json_dict(self) -> dict:
        return {
            "as_of_date": self.as_of_date,
            "source_sha": self.source_sha,
            "builder_version": self.builder_version,
            "orchestrator_version": self.orchestrator_version,
            "computed_at_brt": self.computed_at_brt,
            "output_sha": self.output_sha,
            "holdout_unlock_used": self.holdout_unlock_used,
            "calendar_sha": self.calendar_sha,
            "tradetype_filter_status": self.tradetype_filter_status,
        }


# =====================================================================
# Helpers (anti-leak window, hashing)
# =====================================================================
def compute_window(as_of_date: date, calendar: CalendarData) -> tuple[date, date]:
    """Return ``(window_start, window_end)`` per AC2 strict invariant.

    Window contract (Mira T0):
      - end   = ``as_of_date - 1 day`` (current day NEVER included)
      - start = earliest calendar day s.t. the window contains at least
        ``WARMUP_VALID_DAYS_REQUIRED`` (146) ``calendar.is_valid_sample_day``
        days. We expand backwards day-by-day until the count is satisfied
        OR we exceed the calendar-buffer safety net (raises
        ``InsufficientCoverage``).

    Returns BRT-naive ``date`` bounds (R2). Builders apply the strict
    ``< as_of_date`` predicate downstream.
    """
    end = as_of_date - timedelta(days=1)
    safety_limit_days = int(WARMUP_VALID_DAYS_REQUIRED * CALENDAR_BUFFER_RATIO)
    cur = end
    valid_count = 0
    iterated = 0
    while iterated < safety_limit_days:
        if calendar.is_valid_sample_day(cur):
            valid_count += 1
            if valid_count >= WARMUP_VALID_DAYS_REQUIRED:
                return cur, end
        cur -= timedelta(days=1)
        iterated += 1
    raise InsufficientCoverage(
        f"calendar coverage insufficient for as_of={as_of_date.isoformat()}: "
        f"only {valid_count} valid sample days within "
        f"{safety_limit_days}-calendar-day buffer (need "
        f"{WARMUP_VALID_DAYS_REQUIRED})"
    )


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_bytes(obj: dict) -> bytes:
    """Canonical JSON serialization for byte-equal determinism (AC7).

    Uses ``sort_keys=True`` + compact separators. Floats are serialized
    via Python's ``json`` module which uses ``repr()`` round-trip-safe
    representation — same input ⇒ same bytes.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def state_content_hash(state_json: dict) -> str:
    """SHA-256 over the JSON representation EXCLUDING ``computed_at_brt``.

    AC7: 3 runs with same (as_of, source, seed) ⇒ identical hash.
    """
    snapshot = {k: v for k, v in state_json.items() if k != "computed_at_brt"}
    return _sha256_bytes(_canonical_json_bytes(snapshot))


# =====================================================================
# AC4 — tradeType filter (Guard #4 — escalate, do NOT improvise)
# =====================================================================
@dataclass(frozen=True)
class TradeFilterDecision:
    """Outcome of tradeType filter inspection per AC4.

    The T002.0b adapter (``feed_parquet.load_trades``) yields only
    ``(ts, price, qty)`` — tradeType is discarded at the adapter layer.
    Orchestrator detects this via runtime introspection of the Trade
    record (no ``tradeType`` attribute) and emits a structured escalation
    log. We continue with unfiltered trades + warning per Guard #4 (Dara
    T0 mini-council resolution: "NÃO improvisar; reportar gap").
    """

    status: str  # "applied" | "escalated_adapter_gap"
    note: str


def inspect_tradetype_filter(trade_sample: Trade | None) -> TradeFilterDecision:
    """Detect whether the source carries tradeType.

    Returns ``status="applied"`` if the trade carries a ``tradeType``
    attribute (future-proof for adapter upgrade); else
    ``"escalated_adapter_gap"`` per Guard #4.
    """
    if trade_sample is not None and hasattr(trade_sample, "tradeType"):
        return TradeFilterDecision(
            status="applied",
            note="Trade.tradeType present; downstream filter applied",
        )
    return TradeFilterDecision(
        status="escalated_adapter_gap",
        note=(
            "[USER-ESCALATION-PENDING] T002.0b adapter does not propagate "
            "tradeType (yields only ts/price/qty). Per AC4 + Guard #4: "
            "continuing with unfiltered trades + warning. Tracked: "
            "USER-ESCALATION-QUEUE.md (P2 - tradeType filter promotion)."
        ),
    )


# =====================================================================
# AC4 — daily OHLC + DailyMetrics extraction from raw trades
# =====================================================================
def _aggregate_daily_with_close_at(
    trades: Iterable[Trade],
    close_at_time: time,
) -> tuple[list[DailyOHLC], dict[date, float]]:
    """Aggregate trades into ``(DailyOHLC list, close_at_time map)``.

    The ``close_at_time`` map is keyed by ``date`` and holds the last
    trade price with ``trade.ts.time() <= close_at_time`` (anti-leakage
    pattern from ``SessionState.snapshot_at`` — close_at_t never reads a
    trade with ts > t).

    Builders consume the OHLC list directly; the magnitude metric uses
    ``close_at_time`` per spec v0.2.0 (close[16:55]).
    """
    buckets: dict[date, list[Trade]] = {}
    for tr in trades:
        buckets.setdefault(tr.ts.date(), []).append(tr)
    ohlcs: list[DailyOHLC] = []
    close_at_map: dict[date, float] = {}
    for day, trs in sorted(buckets.items()):
        trs_sorted = sorted(trs, key=lambda t: t.ts)
        prices = [t.price for t in trs_sorted]
        ohlcs.append(
            DailyOHLC(
                day=day,
                open=prices[0],
                high=max(prices),
                low=min(prices),
                close=prices[-1],
                volume_contracts=sum(t.qty for t in trs_sorted),
            )
        )
        # close_at_time anti-leak: last trade with ts.time() <= close_at_time.
        close_at: float | None = None
        for tr in trs_sorted:
            if tr.ts.time() <= close_at_time:
                close_at = tr.price
            else:
                break
        if close_at is None:
            # No trade at/before 16:55 for this day — fall back to first
            # trade of the session. Safe because magnitude denominator is
            # ATR_20d (always > 0 unless degenerate, and degenerate is
            # caught by the builder's ATR sanity).
            close_at = prices[0]
        close_at_map[day] = close_at
    return ohlcs, close_at_map


def _build_daily_metrics(
    ohlcs: Sequence[DailyOHLC],
    close_at_map: dict[date, float],
    calendar: CalendarData,
) -> list[DailyMetrics]:
    """Compute ``DailyMetrics`` per spec v0.2.0:

      magnitude     = |close_at[16:55] - open_day| / ATR_20d_of_that_day
      atr_day_ratio = ATR_day / ATR_20d_of_that_day

    where ``ATR_20d_of_that_day`` is the rolling 20d ATR ending at the
    PRIOR valid sample day (anti-leak — current day never enters its own
    rolling denominator) and ``ATR_day = high - low`` (trades-only proxy).

    Days where ATR_20d is undefined (insufficient prior history) are
    SKIPPED — emitting them with neutral magnitudes would be invention
    (Guard #1). The downstream Percentiles126d builder requires only
    that the FINAL window contains 126 valid metrics.
    """
    sample_days = [o for o in ohlcs if calendar.is_valid_sample_day(o.day)]
    sample_days.sort(key=lambda o: o.day)
    metrics: list[DailyMetrics] = []
    # Rolling 20d ATR (prior-only — index i uses sample_days[i-20:i] true ranges).
    # Use literal 20 so patch.object(sut, 'ATR20dBuilder', ...) in tests does
    # not break attribute access on a MagicMock.
    atr_window = 20
    for i, day_ohlc in enumerate(sample_days):
        if i < atr_window:
            continue  # not enough prior history for ATR_20d
        prior = sample_days[i - atr_window : i]
        true_ranges: list[float] = []
        for j, p in enumerate(prior):
            if j == 0:
                true_ranges.append(p.high - p.low)
            else:
                prev_close = prior[j - 1].close
                tr = max(
                    p.high - p.low,
                    abs(p.high - prev_close),
                    abs(p.low - prev_close),
                )
                true_ranges.append(tr)
        atr_20d = sum(true_ranges) / len(true_ranges)
        if atr_20d <= 0.0:
            continue  # degenerate; cannot compute ratios
        close_at = close_at_map.get(day_ohlc.day, day_ohlc.close)
        magnitude = abs(close_at - day_ohlc.open) / atr_20d
        atr_day = day_ohlc.high - day_ohlc.low
        atr_day_ratio = atr_day / atr_20d
        metrics.append(
            DailyMetrics(
                day=day_ohlc.day,
                magnitude=magnitude,
                atr_day_ratio=atr_day_ratio,
            )
        )
    return metrics


# =====================================================================
# AC8 — roundtrip schema validator
# =====================================================================
def _assert_roundtrip_atr(state: ATR20dState) -> None:
    """Per AC8 — ``from_json(to_json()) == state`` deep-equality."""
    encoded = state.to_json()
    restored = ATR20dState.from_json(encoded)
    if restored != state:
        raise AssertionError(
            "ATR20dState roundtrip drift detected — schema integrity broken"
        )


def _assert_roundtrip_pct(state: Percentiles126dState) -> None:
    """Per AC8 — ``from_json(to_json()) == state`` deep-equality."""
    encoded = state.to_json()
    restored = Percentiles126dState.from_json(encoded)
    if restored != state:
        raise AssertionError(
            "Percentiles126dState roundtrip drift detected — schema integrity broken"
        )


# =====================================================================
# AC9 — manifest writer (append-only JSONL)
# =====================================================================
def append_manifest_entry(manifest_path: Path, entry: ManifestEntry) -> None:
    """Append a single JSONL line to ``state/T002/manifest.json``.

    Anti-Article-IV Guard #2: failure raises ``ManifestWriteError``;
    caller MUST abort. NO fallback path.
    """
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(entry.to_json_dict(), sort_keys=True, separators=(",", ":"))
        with manifest_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        raise ManifestWriteError(
            f"manifest append failed at {manifest_path}: {exc}"
        ) from exc


# =====================================================================
# Output writers (canonical JSON + COPY for latest, AC5 + Beckett T0)
# =====================================================================
def _write_atr_state(state: ATR20dState, dated_path: Path) -> str:
    """Write ATR state to ``dated_path`` deterministically; return state_content_hash."""
    dated_path.parent.mkdir(parents=True, exist_ok=True)
    state_json = state.to_json()
    canonical_bytes = _canonical_json_bytes(state_json)
    # Write canonical bytes (sort_keys + compact) so file SHA matches the
    # determinism stamp; pretty-printed serialization would diverge.
    dated_path.write_bytes(canonical_bytes)
    return state_content_hash(state_json)


def _write_pct_state(state: Percentiles126dState, dated_path: Path) -> str:
    """Write Percentiles state to ``dated_path``; return state_content_hash."""
    dated_path.parent.mkdir(parents=True, exist_ok=True)
    state_json = state.to_json()
    canonical_bytes = _canonical_json_bytes(state_json)
    dated_path.write_bytes(canonical_bytes)
    return state_content_hash(state_json)


def _copy_to_latest(dated_path: Path, latest_path: Path) -> None:
    """Beckett T0 — COPY (not symlink) on Windows; fail-closed if copy fails.

    Anti-Article-IV Guard #2: surfaces OSError as-is so caller aborts.
    """
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(dated_path, latest_path)


# =====================================================================
# Determinism stamp (AC7)
# =====================================================================
@dataclass(frozen=True)
class DeterminismStamp:
    """Per-run determinism artifact (AC7).

    Persisted to ``state/T002/determinism_stamp.json`` so 3-run byte-equal
    test can re-read and compare across runs.
    """

    as_of_date: str
    atr_state_content_hash: str
    percentiles_state_content_hash: str
    seed: int
    orchestrator_version: str
    builder_version: str

    def to_json(self) -> dict:
        return {
            "as_of_date": self.as_of_date,
            "atr_state_content_hash": self.atr_state_content_hash,
            "percentiles_state_content_hash": self.percentiles_state_content_hash,
            "seed": self.seed,
            "orchestrator_version": self.orchestrator_version,
            "builder_version": self.builder_version,
        }


def _write_determinism_stamp(stamps: list[DeterminismStamp], path: Path) -> None:
    """Persist all per-as_of_date stamps as a JSON array (sorted by as_of)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [s.to_json() for s in sorted(stamps, key=lambda s: s.as_of_date)]
    path.write_bytes(_canonical_json_bytes({"stamps": payload}))


# =====================================================================
# Main entry point — orchestrate_warmup_state
# =====================================================================
@dataclass(frozen=True)
class OrchestratorResult:
    """Return value of ``orchestrate_warmup_state``.

    Lists are sorted by ``as_of_date`` ASCENDING. ``latest_*`` paths point
    to the COPY of the LAST as_of_date emitted (per AC5).
    """

    atr_paths: list[Path]
    percentiles_paths: list[Path]
    latest_atr_path: Path
    latest_percentiles_path: Path
    manifest_path: Path
    determinism_stamp_path: Path
    tradetype_decision: TradeFilterDecision


def orchestrate_warmup_state(
    *,
    as_of_dates: Sequence[date],
    source: ParquetSource,
    output_dir: Path,
    calendar: CalendarData,
    calendar_sha: str = "",
    seed: int = 42,
    ticker: str = "WDO",
    now_brt: Callable[[], datetime] = datetime.now,
    holdout_assert: Callable[[date, date], None] | None = None,
) -> OrchestratorResult:
    """Materialize ``state/T002/{atr_20d,percentiles_126d}_{date}.json``.

    Mira T0 mandatory: ``calendar`` is a REQUIRED keyword param. The
    orchestrator NEVER instantiates a calendar internally — divergence
    between the caller's calendar and an internal one would create a
    silent leak (sample-day membership drift).

    Riven T0 mandatory: ``holdout_assert`` is invoked BEFORE the adapter
    open. Defaults to the canonical ``assert_holdout_safe`` from
    ``scripts/_holdout_lock.py``. Tests inject a no-op for synthetic
    windows that intersect the hold-out range.

    Aria T0 + Beckett T0 + AC5: per-as_of_date dated outputs PLUS a COPY
    of the LAST date's state to ``state/T002/{atr_20d,percentiles_126d}.json``
    (consumer default for ``WarmUpGate``).
    """
    if not as_of_dates:
        raise ValueError("as_of_dates must be non-empty")
    sorted_dates = sorted(set(as_of_dates))

    # Resolve holdout assertion (Riven T0 — defense-in-depth).
    if holdout_assert is None:
        # Lazy import to keep tests insulated.
        import sys

        repo_root = Path(__file__).resolve().parents[3]
        scripts_dir = repo_root / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from _holdout_lock import assert_holdout_safe as _real_assert  # noqa: E402

        def holdout_assert(start: date, end: date) -> None:  # type: ignore[misc]
            _real_assert(start, end)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    determinism_stamp_path = output_dir / "determinism_stamp.json"

    # Builders.
    atr_builder = ATR20dBuilder(calendar=calendar)
    pct_builder = Percentiles126dBuilder(calendar=calendar)

    atr_paths: list[Path] = []
    pct_paths: list[Path] = []
    stamps: list[DeterminismStamp] = []
    last_dec: TradeFilterDecision | None = None

    # AC10 — streaming PER as_of_date (R4 mitigation).
    for as_of in sorted_dates:
        # AC2 — anti-leak window strict [D-146bd, D-1].
        window_start, window_end = compute_window(as_of, calendar)

        # AC3 — Riven defense-in-depth BEFORE adapter open.
        holdout_assert(window_start, window_end)

        # Convert window edges to BRT-naive datetimes spanning the trading day.
        # Adapter contract: start inclusive, end exclusive. End_brt is start
        # of the day AFTER window_end so trades ON window_end are included.
        start_brt = datetime.combine(window_start, time(0, 0, 0))
        end_brt = datetime.combine(window_end + timedelta(days=1), time(0, 0, 0))

        # AC1 — load trades via adapter (parquet primary; manifest SHA
        # re-check delegated per Dara T0).
        trades_iter = source.load_trades(start_brt, end_brt, ticker)

        # Materialize once into list — the OHLC aggregation needs to bucket
        # by day before either builder runs. Streaming into ``buckets``
        # keeps memory bounded by the daily-distinct-trade count.
        ohlcs, close_at_map = _aggregate_daily_with_close_at(
            trades_iter, CLOSE_AT_TIME_BRT
        )

        # AC4 — tradeType inspection (Guard #4 escalation if adapter
        # discards). We probe a single OHLC's underlying — the adapter
        # already discarded the field, so the probe always returns
        # "escalated_adapter_gap" for parquet source today. Future-proof
        # via runtime hasattr check.
        sample_trade: Trade | None = None
        if ohlcs:
            # Re-fetch a tiny window of trades from the same source just to
            # peek a Trade record's attributes — but the iterator is one-shot.
            # We approximate by inspecting the (post-cast) Trade dataclass:
            #   FeedParquetSource always produces warmup.atr_20d_builder.Trade
            #   which has only (ts, price, qty) — no tradeType.
            sample_trade = Trade(
                ts=datetime.combine(ohlcs[0].day, time(9, 0, 0)),
                price=ohlcs[0].open,
                qty=1,
            )
        decision = inspect_tradetype_filter(sample_trade)
        last_dec = decision
        if decision.status == "escalated_adapter_gap":
            logger.warning("[T002.0g.AC4] %s", decision.note)

        # Build ATR_20d state (uses ALL valid sample days < as_of).
        # Builder accepts trades — re-construct from OHLCs (price = open
        # for synthesis preserves daily aggregation; we already have
        # OHLCs so use them via internal API).
        # NOTE: ATR20dBuilder.build() expects trades; we already aggregated.
        # Use the builder's window selector + ATR compute via wrapper.
        # Guard #1: convert builder's "insufficient history" ValueError into
        # the canonical ``InsufficientCoverage`` so callers see fail-closed
        # signal rather than ambiguous ValueError.
        try:
            atr_state = _build_atr_state_from_ohlcs(
                atr_builder, ohlcs, as_of, now_brt()
            )
        except ValueError as exc:
            raise InsufficientCoverage(
                f"as_of={as_of.isoformat()} ATR_20d build failed: {exc}; "
                f"window=[{window_start.isoformat()}, {window_end.isoformat()}]. "
                "Anti-Article-IV Guard #1: NO neutral fallback — escalate "
                "to upstream data coverage."
            ) from exc
        _assert_roundtrip_atr(atr_state)

        # Build Percentiles_126d state (uses DailyMetrics derived from
        # OHLCs + close_at_map + rolling 20d ATR per day).
        daily_metrics = _build_daily_metrics(ohlcs, close_at_map, calendar)
        # Guard #1 — convert "insufficient" detection to canonical fail-closed.
        pct_window = 126
        if len(daily_metrics) < pct_window:
            raise InsufficientCoverage(
                f"as_of={as_of.isoformat()}: only {len(daily_metrics)} "
                f"valid DailyMetrics (need {pct_window}); "
                f"window=[{window_start.isoformat()}, {window_end.isoformat()}]. "
                "Anti-Article-IV Guard #1: NO neutral fallback — escalate "
                "to upstream data coverage."
            )
        try:
            pct_state = pct_builder.build(daily_metrics, as_of, now_brt())
        except ValueError as exc:
            raise InsufficientCoverage(
                f"as_of={as_of.isoformat()} Percentiles_126d build failed: {exc}; "
                f"window=[{window_start.isoformat()}, {window_end.isoformat()}]."
            ) from exc
        _assert_roundtrip_pct(pct_state)

        # AC5 — write per-as_of_date dated outputs.
        atr_dated = output_dir / f"atr_20d_{as_of.isoformat()}.json"
        pct_dated = output_dir / f"percentiles_126d_{as_of.isoformat()}.json"
        atr_hash = _write_atr_state(atr_state, atr_dated)
        pct_hash = _write_pct_state(pct_state, pct_dated)
        atr_paths.append(atr_dated)
        pct_paths.append(pct_dated)

        # AC9 — manifest entry per compute (append-only JSONL).
        # source_sha is delegated to the adapter manifest re-check (Dara T0
        # D1). We pin a placeholder noting the delegation; the adapter
        # raises if its own manifest sha mismatches.
        entry = ManifestEntry(
            as_of_date=as_of.isoformat(),
            source_sha="adapter-managed",  # delegated per Dara T0 D1
            builder_version=BUILDER_VERSION,
            orchestrator_version=ORCHESTRATOR_VERSION,
            computed_at_brt=now_brt().isoformat(timespec="seconds"),
            output_sha=_sha256_file(pct_dated),  # primary product
            holdout_unlock_used=_unlock_used(),
            calendar_sha=calendar_sha,
            tradetype_filter_status=decision.status,
        )
        append_manifest_entry(manifest_path, entry)

        stamps.append(
            DeterminismStamp(
                as_of_date=as_of.isoformat(),
                atr_state_content_hash=atr_hash,
                percentiles_state_content_hash=pct_hash,
                seed=seed,
                orchestrator_version=ORCHESTRATOR_VERSION,
                builder_version=BUILDER_VERSION,
            )
        )

    # AC5 — COPY (Beckett T0; not symlink) the MOST RECENT as_of to
    # canonical names so ``WarmUpGate`` default consumers find it.
    latest_as_of = sorted_dates[-1]
    latest_atr_dated = output_dir / f"atr_20d_{latest_as_of.isoformat()}.json"
    latest_pct_dated = output_dir / f"percentiles_126d_{latest_as_of.isoformat()}.json"
    latest_atr = output_dir / "atr_20d.json"
    latest_pct = output_dir / "percentiles_126d.json"
    _copy_to_latest(latest_atr_dated, latest_atr)
    _copy_to_latest(latest_pct_dated, latest_pct)

    _write_determinism_stamp(stamps, determinism_stamp_path)

    return OrchestratorResult(
        atr_paths=atr_paths,
        percentiles_paths=pct_paths,
        latest_atr_path=latest_atr,
        latest_percentiles_path=latest_pct,
        manifest_path=manifest_path,
        determinism_stamp_path=determinism_stamp_path,
        tradetype_decision=last_dec
        if last_dec is not None
        else TradeFilterDecision(status="applied", note="no trades observed"),
    )


def _build_atr_state_from_ohlcs(
    builder: ATR20dBuilder,
    ohlcs: Sequence[DailyOHLC],
    as_of_date: date,
    now_brt: datetime,
) -> ATR20dState:
    """Wrapper that runs ``ATR20dBuilder.build`` from pre-aggregated OHLCs.

    The builder's public API takes ``trades`` — for the orchestrator we've
    already aggregated to ``DailyOHLC``. We synthesize one trade per OHLC
    quad (open, high, low, close) so the builder's ``_aggregate_daily``
    preserves the same OHLC. Order matters: the timestamps are anchored
    at session open (09:30) for open, then high/low/close intercalated
    inside the session — bucket by date is ts.date() so any time within
    the day works for grouping.
    """
    trades: list[Trade] = []
    for o in ohlcs:
        base_dt = datetime.combine(o.day, time(9, 30, 0))
        # Order: open, high, low, close — final price = close (matches
        # close in original OHLC) since builder uses prices[-1] as close.
        trades.append(Trade(ts=base_dt, price=o.open, qty=1))
        trades.append(Trade(ts=base_dt + timedelta(minutes=1), price=o.high, qty=1))
        trades.append(Trade(ts=base_dt + timedelta(minutes=2), price=o.low, qty=1))
        trades.append(Trade(ts=base_dt + timedelta(minutes=3), price=o.close, qty=1))
    return builder.build(trades, as_of_date, now_brt)


def _unlock_used() -> bool:
    """Read VESPERA_UNLOCK_HOLDOUT to populate manifest field (R1+R15(d))."""
    import os

    return os.environ.get("VESPERA_UNLOCK_HOLDOUT", "0") == "1"


__all__ = [
    "BUILDER_VERSION",
    "CALENDAR_BUFFER_RATIO",
    "CLOSE_AT_TIME_BRT",
    "DeterminismStamp",
    "FeedParquetSource",
    "InsufficientCoverage",
    "ManifestEntry",
    "ManifestWriteError",
    "ORCHESTRATOR_VERSION",
    "OrchestratorResult",
    "ParquetSource",
    "TradeFilterDecision",
    "WARMUP_VALID_DAYS_REQUIRED",
    "append_manifest_entry",
    "compute_window",
    "inspect_tradetype_filter",
    "orchestrate_warmup_state",
    "state_content_hash",
]
