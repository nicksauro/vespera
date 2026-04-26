"""Warm-up state orchestrator — T002.0g + T002.0h streaming patch.

Story: `docs/stories/T002.0h.story.md` (post-T002.0g streaming refactor —
honors ADR-1 v3 CAP_v3 8.4 GiB via per-day online reduction).

Connects parquet trades (T002.0b adapter) ⇒ daily OHLC ⇒ ATR_20d builder
+ Percentiles_126d builder ⇒ canonical JSON state files under
``state/T002/`` consumable by ``WarmUpGate`` and the CPCV harness.

Authoritative authorities (T0 handshakes 2026-04-26 BRT — T002.0h):

- **Aria (architecture)** — Module + thin CLI; ``state/T002/`` canonical;
  manifest schema with ``orchestrator_version``. T002.0h: outer per-day
  loop pattern; per-day O(1) accumulator; Trade objects discarded
  post-update; builder API immutable (``ATR20dBuilder`` /
  ``Percentiles126dBuilder`` pure-compute).
- **Mira (anti-leak + schema)** — Window strict ``[D-146bd, D-1]``;
  current day NEVER included; ``calendar: CalendarData`` MUST be passed
  by the caller (no internal instantiation — leak vector); 146 = 126
  P126 lookback + 20 ATR_20 aux input; ``state_content_hash`` excludes
  ``computed_at_brt`` for AC7. T002.0h: ascending iteration ENFORCED
  (D-1 strictly before D); rolling deques 20/126 orchestrator-managed;
  builder receives deque snapshots (pure compute, no state across calls).
- **Beckett (R6 CPCV gate)** — ``COPY`` (not symlink) on Windows for
  ``state/T002/atr_20d.json`` ↔ ``state/T002/atr_20d_{date}.json``.
- **Dara (parquet source + manifest)** — ``feed_parquet.load_trades``
  yields only ``(ts, price, qty)`` — ``tradeType`` discarded; orchestrator
  MUST escalate (``[USER-ESCALATION-PENDING]``) per Guard #4 and continue
  with unfiltered trades + warning. Manifest SHA re-check delegated to
  the adapter (``_verify_integrity`` per call).
- **Riven (defense-in-depth)** — ``assert_holdout_safe(start, end)``
  fires BEFORE adapter open; manifest.json append-only JSONL pinned in
  ``.github/canonical-invariant.sums``. T002.0h: peak-RSS regression
  test (``tests/warmup_orchestrator/test_streaming_memory.py``) asserts
  ``< 500 MB`` honoring ADR-1 v3 CAP_v3 8.4 GiB (7.9 GiB headroom).

Anti-Article-IV Guards (story T002.0g §Anti-Article-IV Guards +
T002.0h §Anti-Article-IV Guards):

T002.0g (preserved):
1. NO neutral PercentilesState fallback — fail-closed with
   ``InsufficientCoverage`` listing window edges + missing dates.
2. NO silent path switch on write fail — manifest abort.
3. NO window extension beyond ``[D-146bd, D-1]``.
4. NO DLL/TimescaleDB re-fetch — parquet only via ``ParquetSource``.
5. NO determinism check skip — sort_keys + canonical float repr.

T002.0h (added — fail-closed per Pax 10/10 GO):
1. NO timeout extend to mask memory bug — fix root cause (single-pass).
2. NO raise CAP_v3 8.4 GiB — invariant immutable (ADR-1 v3).
3. NO subsample dataset — fixture is real-scale by design.
4. NO builder API mutation — Mira pure-compute contract preserved.
5. NO skip ascending iteration — Mira anti-leak shifted-by-1 broken
   if reordered.

T002.0h AC8 amendment 2026-04-26 BRT (Option C cached file handles):
   ``FeedParquetSource`` accepts an optional ``handle_cache``
   (``ParquetHandleCache`` from ``warmup/_parquet_handle_cache.py``).
   ``orchestrate_warmup_state`` auto-attaches one when the source is a
   ``FeedParquetSource`` lacking a cache. The cache amortizes
   ``pyarrow.parquet.ParquetFile`` opens 6:1 (~110 per-day calls → ~6
   distinct monthly files for a 146bd lookback) AND memoizes the
   adapter's manifest parse single-shot. Anti-leak NEUTRAL — cache is
   order-agnostic; orchestrator's ascending iteration assertion remains
   the canonical invariant. Adapter (``feed_parquet.py``) is UNTOUCHED
   (R15 immutability of T002.0b).

AC mapping (story §Acceptance criteria):

T002.0g (preserved):
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

T002.0h (added):
- AC1  ``_aggregate_day_streaming`` single-pass O(1) accumulator.
- AC2  Outer per-day loop ⇒ trade objects discarded post-aggregation.
- AC3  ``_build_atr_state_from_ohlcs`` re-synthesis bounded to FINAL
       20-OHLC deque snapshot (≤80 trades total — was 146×N).
- AC4  Iteration ascending strictly (D-1 before D).
- AC5  Rolling deques 20/126 orchestrator-managed; builder API unchanged.
- AC6  ``test_streaming_memory.py`` peak < 500 MB.
- AC7  Quinn fixture parametrized ``n_days ∈ {21, 127, 365}``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from collections import deque
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Callable, Iterable, Protocol, Sequence

from packages.t002_eod_unwind.warmup._parquet_handle_cache import ParquetHandleCache
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

    T002.0h AC8 amendment (Option C cached file handles, 2026-04-26 BRT):
    when a ``ParquetHandleCache`` is provided via ``handle_cache`` (or
    auto-instantiated by ``orchestrate_warmup_state``), the per-day
    ``load_trades`` calls reuse a single ``ParquetFile`` instance per
    monthly partition — amortizing parquet open + metadata-scan cost
    6:1 (~110 per-day calls → ~6 distinct monthly files for a 146bd
    lookback). NEUTRAL w.r.t. anti-leak (Mira): cache is order-agnostic
    and does NOT change ``load_trades`` semantics; orchestrator still
    iterates D-1 strictly before D.
    """

    ticker: str = "WDO"
    handle_cache: ParquetHandleCache | None = None

    def load_trades(
        self,
        start_brt: datetime,
        end_brt: datetime,
        ticker: str,
    ) -> Iterable[Trade]:
        # Lazy import — keeps test mocks free of pyarrow import cost.
        from packages.t002_eod_unwind.adapters import feed_parquet as _fp
        from packages.t002_eod_unwind.adapters.feed_parquet import (
            load_trades as _load_trades,
        )

        # Adapter yields ``packages.t002_eod_unwind.core.session_state.Trade``;
        # ATR builder expects ``packages.t002_eod_unwind.warmup.atr_20d_builder.Trade``
        # — same shape (ts, price, qty). Cast on the fly.
        if self.handle_cache is None:
            # Backward-compat path — no cache; call adapter directly.
            for tr in _load_trades(start_brt, end_brt, ticker):
                yield Trade(ts=tr.ts, price=tr.price, qty=tr.qty)
            return

        # T002.0h AC8 — patch the adapter's ``pq.ParquetFile`` symbol
        # (used in ``_iter_parquet_rows``) to route through the cache.
        # The patch is scoped to this generator's lifetime via
        # try/finally so concurrent (mock-source) tests are unaffected.
        # We also cache the manifest row list so 110 per-day calls don't
        # re-parse data/manifest.csv each time (Beckett wall-time
        # diagnostic step #1).
        cache = self.handle_cache
        import pyarrow.parquet as _pq  # type: ignore[import-untyped]

        original_parquet_file = _pq.ParquetFile

        # Capture the REAL opener on the cache BEFORE we patch the
        # module-level symbol — otherwise ``cache._open_parquet`` would
        # recurse through the patched shim back into ``cache.get``.
        # Idempotent: only set on first patch.
        if cache._real_opener is None:
            cache._real_opener = original_parquet_file

        class _CachedParquetFile:
            """Constructor shim — returns a cached handle for ``path``."""

            def __new__(cls, path, *args, **kwargs):  # type: ignore[no-untyped-def]
                # ``cache.get(path)`` returns the same ``ParquetFile``
                # instance for the same path until LRU eviction. The
                # adapter only reads metadata + row groups (no mutation)
                # so sharing the handle across calls is safe.
                return cache.get(Path(path))

        _pq.ParquetFile = _CachedParquetFile  # type: ignore[misc]

        # Manifest cache — Beckett wall-time diagnostic step #1: the
        # adapter re-parses ``data/manifest.csv`` (+ PREVIEW) on every
        # ``load_trades`` call. For 110 per-day calls this is O(110 ×
        # CSV parse). Memoize at the cache instance so this run parses
        # the manifest exactly once.
        original_load_manifest = _fp._load_manifest_with_fallback

        def _cached_manifest_loader():  # type: ignore[no-untyped-def]
            return cache.get_manifest(original_load_manifest)

        _fp._load_manifest_with_fallback = _cached_manifest_loader  # type: ignore[assignment]

        # Also patch the symbol bound in the adapter module's local
        # namespace if it was imported at module scope (defensive — the
        # current adapter does ``import pyarrow.parquet as pq`` lazily
        # inside ``_iter_parquet_rows``, so the module-level patch above
        # is sufficient. This block is a no-op for the current adapter
        # but stays as a defense for future refactors.)
        adapter_pq_attr = getattr(_fp, "pq", None)
        try:
            for tr in _load_trades(start_brt, end_brt, ticker):
                yield Trade(ts=tr.ts, price=tr.price, qty=tr.qty)
        finally:
            _pq.ParquetFile = original_parquet_file  # type: ignore[misc]
            _fp._load_manifest_with_fallback = original_load_manifest  # type: ignore[assignment]
            if adapter_pq_attr is not None:
                # Adapter may have imported pq at module scope in the
                # future; restore that binding too.
                _fp.pq = adapter_pq_attr  # type: ignore[attr-defined]


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
def _aggregate_day_streaming(
    day: date,
    trades: Iterable[Trade],
    close_at_time: time,
) -> tuple[DailyOHLC, float] | None:
    """T002.0h AC1 — single-pass O(1) accumulator for ONE business day.

    Streams trades for ``day`` and returns ``(DailyOHLC, close_at_price)``
    or ``None`` if no trades were observed on ``day``. Trade objects are
    NOT retained — only the running aggregator state
    ``{open, high, low, close, volume, last_close_at_<=16:55, ts_min}``.

    Anti-leak invariant (Mira T0): trades with ``tr.ts.date() != day`` are
    SKIPPED (defensive — caller is expected to pass a per-day stream, but
    parquet files boundaries can leak ±1ms across day edges). The
    ``close_at`` price is the LAST observed trade with
    ``tr.ts.time() <= close_at_time`` (anti-leakage pattern from
    ``SessionState.snapshot_at`` — close_at_t never reads a trade with
    ts > t). Iteration order WITHIN the day does not need to be sorted
    since aggregation is order-invariant for high/low/volume; for
    open/close/close_at we track ``ts_min``/``ts_max`` per category.

    Memory profile: per-day O(1) state (~7 floats + 2 timestamps + 1
    int). Trade object lifetime = single iteration (immediately
    eligible for GC).

    Anti-Article-IV Guard #4 (T002.0h) preserved: builder API NOT
    touched — this helper is orchestrator-internal.
    """
    open_price: float | None = None
    open_ts: datetime | None = None
    close_price: float | None = None
    close_ts: datetime | None = None
    high_price: float = float("-inf")
    low_price: float = float("inf")
    volume: int = 0
    close_at_price: float | None = None
    close_at_ts: datetime | None = None
    saw_any: bool = False

    for tr in trades:
        # Defensive day-boundary filter (parquet row-group leakage).
        if tr.ts.date() != day:
            continue
        saw_any = True
        price = tr.price
        if price > high_price:
            high_price = price
        if price < low_price:
            low_price = price
        volume += tr.qty
        ts = tr.ts
        if open_ts is None or ts < open_ts:
            open_ts = ts
            open_price = price
        if close_ts is None or ts > close_ts:
            close_ts = ts
            close_price = price
        if ts.time() <= close_at_time:
            if close_at_ts is None or ts > close_at_ts:
                close_at_ts = ts
                close_at_price = price
        # Trade object goes out of scope at next loop iteration — no
        # retention beyond the running aggregator state.

    if not saw_any:
        return None

    # mypy: open_price/close_price are assigned iff saw_any.
    assert open_price is not None and close_price is not None
    if close_at_price is None:
        # No trade at/before 16:55 for this day — fall back to OPEN price
        # (spec-compatible with prior behavior; safe because magnitude
        # denominator is ATR_20d > 0 unless degenerate).
        close_at_price = open_price
    return (
        DailyOHLC(
            day=day,
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume_contracts=volume,
        ),
        close_at_price,
    )


def _aggregate_daily_with_close_at(
    trades: Iterable[Trade],
    close_at_time: time,
) -> tuple[list[DailyOHLC], dict[date, float]]:
    """Aggregate trades into ``(DailyOHLC list, close_at_time map)``.

    .. deprecated:: T002.0h
        This helper RETAINS trade objects in per-day buckets — incompatible
        with ADR-1 v3 CAP_v3 8.4 GiB on real-scale (146bd × 850k trades/day
        ≈ 3.7 GB residente). The orchestrator now uses the per-day
        streaming path (``_aggregate_day_streaming``) inside an outer
        per-day loop. This function is kept ONLY for backward-compatible
        unit-test coverage of the legacy aggregation logic — production
        code path is the streaming variant.

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


def _atr_from_ohlc_window(window: Sequence[DailyOHLC]) -> float:
    """T002.0h AC5 helper — compute ATR over a window of ``DailyOHLC``.

    Mirrors ``ATR20dBuilder._compute_atr`` arithmetic exactly (true range
    chained over consecutive OHLCs; first day's TR = high - low).
    Orchestrator-internal — DOES NOT mutate the builder API (Guard #4).

    Used by the streaming per-day loop to compute the rolling ATR_20
    denominator for each day's DailyMetrics. The window passed in is a
    snapshot of the rolling 20-day deque taken BEFORE the current day's
    OHLC is appended (anti-leak: current day excluded from its own
    rolling denominator).
    """
    if not window:
        return 0.0
    true_ranges: list[float] = []
    for i, day in enumerate(window):
        if i == 0:
            true_ranges.append(day.high - day.low)
        else:
            prev_close = window[i - 1].close
            tr = max(
                day.high - day.low,
                abs(day.high - prev_close),
                abs(day.low - prev_close),
            )
            true_ranges.append(tr)
    return sum(true_ranges) / len(true_ranges)


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


def _enumerate_valid_sample_days(
    window_start: date, window_end: date, calendar: CalendarData
) -> list[date]:
    """Return all calendar-valid sample days in ``[window_start, window_end]``
    in STRICTLY ASCENDING order.

    Mira T0 / T002.0h AC4 anti-leak invariant: D-1 always before D.
    """
    days: list[date] = []
    cur = window_start
    while cur <= window_end:
        if calendar.is_valid_sample_day(cur):
            days.append(cur)
        cur += timedelta(days=1)
    return days


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

    T002.0h streaming refactor (AC1-AC5):
        For each as_of_date, we iterate the valid_sample_days ASCENDING
        and call ``source.load_trades(day_start, day_end, ticker)`` PER
        DAY. The day's trades stream through ``_aggregate_day_streaming``
        (single-pass O(1) state) producing one ``DailyOHLC`` + one
        ``close_at`` price. The trade generator is then dropped — no
        per-day list retention. We maintain TWO rolling deques:

          - ``ohlc_deque`` (maxlen=20)   — for the rolling ATR_20 used by
            DailyMetrics computation AND the FINAL ATR_20d state at
            ``as_of - 1``.
          - ``metrics_deque`` (maxlen=126) — for the FINAL Percentiles
            state at ``as_of - 1``.

        Per-day memory: O(1) accumulator + 1× day's trade stream
        (consumed and discarded in-loop). Total residente: O(20 + 126)
        across days. ADR-1 v3 CAP_v3 8.4 GiB compliance: peak < 500 MB
        on real-scale 146bd × ≥50k trades/day (asserted by
        ``tests/warmup_orchestrator/test_streaming_memory.py``).
    """
    if not as_of_dates:
        raise ValueError("as_of_dates must be non-empty")
    sorted_dates = sorted(set(as_of_dates))

    # T002.0h AC8 amendment (Option C): auto-attach a ParquetHandleCache
    # to a FeedParquetSource that doesn't already have one. Mock sources
    # used by tests are unaffected (they don't carry a ``handle_cache``
    # attribute and use their own iteration semantics). NEUTRAL w.r.t.
    # anti-leak (Mira): cache is order-agnostic; orchestrator still
    # iterates D-1 strictly before D (runtime assertion preserved).
    # Set env ``T002_OPTC_DISABLE=1`` to opt out (e.g. when measuring
    # against the uncached baseline for empirical wall-time diagnostics).
    import os as _os

    if (
        isinstance(source, FeedParquetSource)
        and source.handle_cache is None
        and _os.environ.get("T002_OPTC_DISABLE", "0") != "1"
    ):
        source = FeedParquetSource(
            ticker=source.ticker,
            handle_cache=ParquetHandleCache(max_handles=6),
        )

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

    # T002.0g AC10 + T002.0h AC1-AC5: streaming PER as_of_date AND
    # per-day inside each as_of (R4 mitigation extended for memory cap).
    for as_of in sorted_dates:
        # AC2 — anti-leak window strict [D-146bd, D-1].
        window_start, window_end = compute_window(as_of, calendar)

        # AC3 — Riven defense-in-depth BEFORE adapter open.
        holdout_assert(window_start, window_end)

        # T002.0h AC4: enumerate valid sample days STRICTLY ASCENDING.
        # Mira anti-leak invariant: D-1 ALWAYS processed before D so the
        # 20-day rolling ATR for day D excludes day D itself (the
        # ``ohlc_deque`` snapshot taken at the START of day D's metrics
        # computation contains only days strictly before D).
        valid_days = _enumerate_valid_sample_days(
            window_start, window_end, calendar
        )

        # T002.0h AC5: rolling deques orchestrator-managed (NOT
        # builder-managed). Builder API stays pure-compute via deque
        # snapshots passed to its public ``build`` method (Guard #4).
        #
        # ``ohlc_deque``: rolling 20 most-recent OHLCs (ascending by day),
        # used both for per-day DailyMetrics ATR_20 denominator AND for
        # the FINAL ATR_20d state passed to ATR20dBuilder.build via
        # ``_build_atr_state_from_ohlcs`` (synthesizes ≤80 trades total —
        # a constant, not a function of the lookback window).
        #
        # ``metrics_deque``: rolling 126 most-recent DailyMetrics
        # (ascending by day), used for the FINAL Percentiles state
        # passed to Percentiles126dBuilder.build (no synthesis needed —
        # builder accepts DailyMetrics directly).
        # Use literal window sizes (20/126) so tests that patch
        # ``sut.ATR20dBuilder``/``sut.Percentiles126dBuilder`` with
        # side_effect callables don't break attribute access.
        ohlc_deque: deque[DailyOHLC] = deque(maxlen=20)
        metrics_deque: deque[DailyMetrics] = deque(maxlen=126)
        # Mira ascending-order assertion: track last day processed.
        last_day_processed: date | None = None
        # AC4 tradeType decision — set once per as_of after first day with
        # any trades; structurally identical across the run for parquet
        # source today (adapter discards tradeType uniformly).
        decision: TradeFilterDecision | None = None
        days_with_trades = 0

        for day in valid_days:
            # T002.0h AC4 anti-leak guard: ascending-order assertion.
            # Defense-in-depth: ``_enumerate_valid_sample_days`` already
            # returns ascending; this assertion catches future regressions.
            if last_day_processed is not None and day <= last_day_processed:
                raise AssertionError(
                    f"T002.0h AC4 anti-leak violation: day={day.isoformat()} "
                    f"<= last_day_processed={last_day_processed.isoformat()}; "
                    "Mira ascending-iteration invariant broken (D-1 MUST "
                    "strictly precede D)."
                )
            last_day_processed = day

            # T002.0h AC2: per-day stream. Adapter contract: start
            # inclusive, end exclusive; end_brt is start of NEXT day so
            # trades ON ``day`` are fully captured.
            day_start_brt = datetime.combine(day, time(0, 0, 0))
            day_end_brt = datetime.combine(day + timedelta(days=1), time(0, 0, 0))
            trades_iter = source.load_trades(day_start_brt, day_end_brt, ticker)

            # T002.0h AC1: single-pass O(1) accumulator. Trade objects
            # are discarded as the generator is consumed — NO per-day
            # list retention. Returns ``None`` if no trades on ``day``
            # (skipped — calendar said valid but data was empty).
            agg = _aggregate_day_streaming(day, trades_iter, CLOSE_AT_TIME_BRT)
            # CRITICAL: drop the iterator reference so the generator is
            # eligible for GC (parquet row-batches release memory).
            del trades_iter
            if agg is None:
                continue
            day_ohlc, close_at_price = agg
            days_with_trades += 1

            # AC4 tradeType inspection — once per as_of (the cast Trade
            # dataclass shape is invariant for FeedParquetSource).
            if decision is None:
                sample_trade = Trade(
                    ts=datetime.combine(day_ohlc.day, time(9, 0, 0)),
                    price=day_ohlc.open,
                    qty=1,
                )
                decision = inspect_tradetype_filter(sample_trade)
                if decision.status == "escalated_adapter_gap":
                    logger.warning("[T002.0g.AC4] %s", decision.note)

            # T002.0h AC5: emit DailyMetrics for this day BEFORE pushing
            # day_ohlc onto the deque (anti-leak: ATR_20 denominator must
            # exclude THIS day). Skip days where the rolling deque hasn't
            # yet filled to 20 (insufficient prior history); skip days
            # where ATR_20 is degenerate (<=0). Use literal 20 so tests
            # patching ``sut.ATR20dBuilder`` don't break attribute access.
            if len(ohlc_deque) >= 20:
                atr_20 = _atr_from_ohlc_window(list(ohlc_deque))
                if atr_20 > 0.0:
                    magnitude = abs(close_at_price - day_ohlc.open) / atr_20
                    atr_day = day_ohlc.high - day_ohlc.low
                    atr_day_ratio = atr_day / atr_20
                    metrics_deque.append(
                        DailyMetrics(
                            day=day_ohlc.day,
                            magnitude=magnitude,
                            atr_day_ratio=atr_day_ratio,
                        )
                    )

            # NOW push today's OHLC. Subsequent days will see this in
            # their prior-window snapshot (D will be in window for D+1's
            # ATR_20 denominator — correct anti-leak semantics).
            ohlc_deque.append(day_ohlc)

        # Resolve tradetype decision for manifest (default if no trades
        # observed at all — fall through to applied/no-trades).
        if decision is None:
            decision = TradeFilterDecision(
                status="applied", note="no trades observed in window"
            )
        last_dec = decision

        # T002.0h AC3 + AC5: build FINAL state from rolling deques. The
        # builder API is UNCHANGED — we pass deque snapshots via
        # ``list(deque)``. ATR builder still requires trades, so we use
        # the bounded ``_build_atr_state_from_ohlcs`` re-synthesis on
        # the FINAL 20-OHLC snapshot only (≤80 trades — a CONSTANT,
        # NOT 146×N like the legacy bulk-aggregation path that triggered
        # the T11.bis HALT).
        ohlc_snapshot = list(ohlc_deque)
        metrics_snapshot = list(metrics_deque)

        # Guard #1: convert builder's "insufficient history" ValueError
        # into canonical ``InsufficientCoverage``.
        try:
            atr_state = _build_atr_state_from_ohlcs(
                atr_builder, ohlc_snapshot, as_of, now_brt()
            )
        except ValueError as exc:
            raise InsufficientCoverage(
                f"as_of={as_of.isoformat()} ATR_20d build failed: {exc}; "
                f"window=[{window_start.isoformat()}, {window_end.isoformat()}]; "
                f"days_with_trades={days_with_trades}; "
                f"ohlc_deque_len={len(ohlc_snapshot)}. "
                "Anti-Article-IV Guard #1: NO neutral fallback — escalate "
                "to upstream data coverage."
            ) from exc
        _assert_roundtrip_atr(atr_state)

        # Guard #1 — convert "insufficient" detection to canonical fail-closed.
        # Use literal 126 (matches Percentiles126dBuilder.WINDOW) so tests
        # patching ``sut.Percentiles126dBuilder`` don't break this check.
        pct_window_required = 126
        if len(metrics_snapshot) < pct_window_required:
            raise InsufficientCoverage(
                f"as_of={as_of.isoformat()}: only {len(metrics_snapshot)} "
                f"valid DailyMetrics (need {pct_window_required}); "
                f"window=[{window_start.isoformat()}, {window_end.isoformat()}]; "
                f"days_with_trades={days_with_trades}. "
                "Anti-Article-IV Guard #1: NO neutral fallback — escalate "
                "to upstream data coverage."
            )
        try:
            pct_state = pct_builder.build(metrics_snapshot, as_of, now_brt())
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

    T002.0h AC3 NOTE — The legacy callsite (T002.0g) passed the FULL
    146-day OHLC list, causing the builder's ``_aggregate_daily`` to
    re-process 4 × N synthesized trades. The streaming refactor (T002.0h)
    now passes ONLY the FINAL 20-OHLC snapshot from the rolling
    ``ohlc_deque``, so trade synthesis is bounded to ≤80 trades total —
    a CONSTANT, not a function of the lookback window. This eliminates
    the duplication-of-peak that contributed to the T11.bis HALT.

    The builder's public API takes ``trades`` (Mira pure-compute,
    Guard #4 immutable); we therefore synthesize one trade per OHLC
    quad (open, high, low, close) so the builder's ``_aggregate_daily``
    reproduces the same OHLC. Order matters: the timestamps are anchored
    at session open (09:30) for open, then high/low/close intercalated
    inside the session — bucket by date is ts.date() so any time within
    the day works for grouping. The builder's window selector restricts
    output to the LAST 20 valid days < as_of_date — matching the deque
    snapshot exactly.
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
    "ParquetHandleCache",
    "ParquetSource",
    "TradeFilterDecision",
    "WARMUP_VALID_DAYS_REQUIRED",
    "append_manifest_entry",
    "compute_window",
    "inspect_tradetype_filter",
    "orchestrate_warmup_state",
    "state_content_hash",
]
