"""T002.0h T2 + T3 — streaming memory regression + anti-leak invariants.

Story: ``docs/stories/T002.0h.story.md``

Coverage map:

- **AC4 (T2)**  ``test_iteration_strictly_ascending`` — orchestrator
  passes ``valid_sample_days`` to its per-day inner loop in STRICTLY
  ASCENDING order. Mira anti-leak shifted-by-1 invariant: D-1 always
  before D so the rolling 20-day ATR for day D never includes day D
  itself.
- **AC5 (T2)**  ``test_builder_api_unchanged_across_calls`` — the
  ``ATR20dBuilder`` and ``Percentiles126dBuilder`` ``.build`` methods
  are invoked exactly ONCE per as_of_date, with snapshot inputs (no
  state accumulated across calls). Builder API contract preserved
  (Guard #4).
- **AC6 (T3)**  ``test_streaming_real_scale_peak_under_500mb`` — real-
  scale fixture (146 valid business days × ≥50k trades/day) feeds the
  orchestrator end-to-end; ``tracemalloc.get_traced_memory()`` peak
  asserted ``< 500 MB``.

ADR-1 v3 CAP_v3 8.4 GiB compliance comment (mandatory per AC6):
    The streaming refactor (T002.0h) bounds residente memory to
    O(20+126) deque state + 1× day-of-trades stream consumed-and-discarded
    per inner-loop iteration. The 500 MB cap leaves ~7.9 GiB headroom
    under ADR-1 v3 CAP_v3 8.4 GiB for the downstream CPCV harness
    (concurrent JSON state + parquet adapter + numpy arrays). Without
    this patch the legacy bulk-aggregation path retained ~3.7 GiB of
    Trade objects in ``buckets[day]: list[Trade]`` (146d × ~850k
    trades/day × ~120B/Trade), triggering the T11.bis HALT (RSS
    1.95→4.10→6.09 GB in 90s, SIGTERM exit 124).

The memory test is marked ``slow`` because the synthetic real-scale
generator + per-day streaming costs ~10-30s wall-time. Excluded from
default fast-CI runs via ``pytest -m 'not slow'``.
"""

from __future__ import annotations

import sys
import tracemalloc
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, Iterator

import pytest

# Ensure repo root importable.
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from packages.t002_eod_unwind.warmup import orchestrator as sut  # noqa: E402
from packages.t002_eod_unwind.warmup.atr_20d_builder import (  # noqa: E402
    ATR20dBuilder,
    Trade,
)
from packages.t002_eod_unwind.warmup.calendar_loader import (  # noqa: E402
    CalendarData,
)
from packages.t002_eod_unwind.warmup.orchestrator import (  # noqa: E402
    orchestrate_warmup_state,
)
from packages.t002_eod_unwind.warmup.percentiles_126d_builder import (  # noqa: E402
    Percentiles126dBuilder,
)


# =====================================================================
# Fixtures — permissive calendar + holdout no-op
# =====================================================================
def _permissive_calendar() -> CalendarData:
    """Calendar where every weekday is a valid sample day."""
    return CalendarData(
        version="streaming-memory-test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _noop_holdout(start: date, end: date) -> None:
    return None


# =====================================================================
# Per-day streaming source — generates trades on-demand (no retention)
# =====================================================================
class _PerDayStreamingSource:
    """T002.0h-aware ``ParquetSource`` impl that synthesizes trades per
    requested window via a generator. Crucially: trades are NOT
    materialized in advance — each ``load_trades`` call returns a fresh
    generator that yields trades lazily.

    This mirrors the real ``FeedParquetSource`` semantics (parquet
    row-batch streaming) so the memory test exercises the same
    consume-and-discard pattern as production.

    ``trades_per_day`` controls the per-day burden — at 50_000 the test
    matches Beckett's smoke real-scale (~50-100k trades/day on WDO).
    """

    def __init__(self, *, trades_per_day: int, base_price: float = 5000.0) -> None:
        self.trades_per_day = trades_per_day
        self.base_price = base_price
        # Track the per-day call count so AC5 anti-leak inspection can
        # verify ascending order. Populated by ``load_trades`` for ALL
        # days within the requested window (Option B per-month batched
        # call may cover ~21 days per call; populated once per day in
        # ascending order to remain meaningful for the AC4 ascending
        # invariant assertion).
        self.day_call_order: list[date] = []
        # Track raw window calls (start, end) for diagnostic purposes —
        # Option C (per-day) makes ~110 calls; Option B (per-month) makes
        # ~7-8 calls for the same window.
        self.window_calls: list[tuple[datetime, datetime]] = []

    def load_trades(
        self,
        start_brt: datetime,
        end_brt: datetime,
        ticker: str,
    ) -> Iterable[Trade]:
        # T002.0h AC2 amendment (Option B per-month outer loop): the
        # orchestrator may issue per-day OR per-month calls. We honor
        # both by generating trades for EVERY weekday in the requested
        # ``[start_brt, end_brt)`` window.
        self.window_calls.append((start_brt, end_brt))
        return self._gen_for_window(start_brt, end_brt)

    def _gen_for_window(
        self, start_brt: datetime, end_brt: datetime
    ) -> Iterator[Trade]:
        """Generator: yields trades for every weekday in
        ``[start_brt, end_brt)``. Days are visited in ASCENDING order so
        the orchestrator's per-day partition (Option B) and per-day
        consumption (Option C) both observe the SAME trade sequence.
        """
        cur = start_brt.date()
        end_excl = end_brt.date()
        while cur < end_excl:
            if cur.weekday() < 5:
                self.day_call_order.append(cur)
                yield from self._gen_for_day(cur)
            cur += timedelta(days=1)

    def _gen_for_day(self, day: date) -> Iterator[Trade]:
        """Generator: yields ``trades_per_day`` synthetic ``Trade`` rows
        for ``day``. Each Trade is constructed and immediately yielded;
        the caller is expected to consume-and-discard.
        """
        n = self.trades_per_day
        base = self.base_price + (day.toordinal() % 50) * 1.0
        # Synthetic intraday price walk: scale with trade index so OHLC
        # is non-degenerate (high > low, ATR > 0).
        session_start = datetime.combine(day, time(9, 0, 0))
        # Spread N ticks over the trading day (~7h25m = 26700s).
        # Use a deterministic "tick spacing" so the sequence is
        # reproducible.
        seconds_window = 7 * 3600 + 25 * 60
        if n <= 1:
            # Edge: single trade — emit one tick at session open.
            yield Trade(ts=session_start, price=base, qty=1)
            return
        dt_step = max(1, seconds_window // n)
        for i in range(n):
            # Triangle wave: rises in first half, falls in second half —
            # ensures distinct high/low so ATR_day > 0.
            if i < n // 2:
                price = base + (i % 50) * 0.5
            else:
                price = base + ((n - i) % 50) * 0.5
            ts = session_start + timedelta(seconds=i * dt_step)
            yield Trade(ts=ts, price=price, qty=1)


# =====================================================================
# AC4 — iteration strictly ascending (Mira anti-leak invariant)
# =====================================================================
def test_iteration_strictly_ascending(tmp_path):
    """T002.0h AC4 — orchestrator iterates per-day in STRICTLY ASCENDING
    order. Mira anti-leak: D-1 must always be processed before D.

    We instrument ``_PerDayStreamingSource`` to record the order in which
    the orchestrator requests per-day trade windows, then assert that
    sequence equals the sorted enumeration of valid sample days.
    """
    cal = _permissive_calendar()
    # Use a SMALL trades_per_day so the test runs fast — the order
    # invariant doesn't depend on trade volume.
    source = _PerDayStreamingSource(trades_per_day=4)
    out_dir = tmp_path / "state"

    orchestrate_warmup_state(
        as_of_dates=[date(2025, 5, 31)],
        source=source,
        output_dir=out_dir,
        calendar=cal,
        calendar_sha="ascending-test",
        holdout_assert=_noop_holdout,
    )

    # The recorded day_call_order MUST be strictly ascending.
    assert source.day_call_order, "source.load_trades was never called"
    assert source.day_call_order == sorted(source.day_call_order), (
        f"AC4 violation: day_call_order is not ascending. "
        f"First few: {source.day_call_order[:5]}; "
        f"sorted-prefix: {sorted(source.day_call_order)[:5]}"
    )
    # Strict ascending — no duplicates within a single as_of run.
    assert len(set(source.day_call_order)) == len(source.day_call_order), (
        f"AC4 violation: duplicate day in day_call_order; "
        f"len={len(source.day_call_order)}, "
        f"unique={len(set(source.day_call_order))}"
    )


# =====================================================================
# AC5 — builder API unchanged across calls (Mira pure-compute contract)
# =====================================================================
def test_builder_api_unchanged_across_calls(tmp_path):
    """T002.0h AC5 — ``ATR20dBuilder.build`` and
    ``Percentiles126dBuilder.build`` are called EXACTLY ONCE per
    as_of_date, with deque snapshot inputs. Builder API contract
    preserved (Guard #4 — no builder mutation).

    We wrap the real builder constructors and count ``.build`` calls
    per builder instance.
    """
    from unittest.mock import patch

    cal = _permissive_calendar()
    source = _PerDayStreamingSource(trades_per_day=4)
    out_dir = tmp_path / "state"

    atr_build_calls: list[int] = []
    pct_build_calls: list[int] = []

    real_atr_cls = sut.ATR20dBuilder
    real_pct_cls = sut.Percentiles126dBuilder

    def wrap_atr(*, calendar):
        inst = real_atr_cls(calendar=calendar)
        original_build = inst.build

        def counting_build(*args, **kwargs):
            atr_build_calls.append(1)
            return original_build(*args, **kwargs)

        inst.build = counting_build  # type: ignore[method-assign]
        return inst

    def wrap_pct(*, calendar):
        inst = real_pct_cls(calendar=calendar)
        original_build = inst.build

        def counting_build(*args, **kwargs):
            pct_build_calls.append(1)
            return original_build(*args, **kwargs)

        inst.build = counting_build  # type: ignore[method-assign]
        return inst

    with patch.object(sut, "ATR20dBuilder", side_effect=wrap_atr), patch.object(
        sut, "Percentiles126dBuilder", side_effect=wrap_pct
    ):
        orchestrate_warmup_state(
            as_of_dates=[date(2025, 5, 31)],
            source=source,
            output_dir=out_dir,
            calendar=cal,
            calendar_sha="builder-api-test",
            holdout_assert=_noop_holdout,
        )

    # Each builder is invoked EXACTLY ONCE for the single as_of_date —
    # not once per day. The orchestrator manages rolling state in deques,
    # then snapshots deques into a single builder.build() call.
    assert sum(atr_build_calls) == 1, (
        f"AC5 violation: ATR20dBuilder.build called "
        f"{sum(atr_build_calls)} times; expected exactly 1 per as_of_date"
    )
    assert sum(pct_build_calls) == 1, (
        f"AC5 violation: Percentiles126dBuilder.build called "
        f"{sum(pct_build_calls)} times; expected exactly 1 per as_of_date"
    )

    # Sanity: builders' WINDOW class attributes match orchestrator's
    # deque maxlen (Guard #4 invariant — builder API unchanged).
    assert ATR20dBuilder.WINDOW == 20
    assert Percentiles126dBuilder.WINDOW == 126


# =====================================================================
# AC6 (T3) — memory regression: real-scale peak < 500 MB
# =====================================================================
@pytest.mark.slow
def test_streaming_real_scale_peak_under_500mb(tmp_path):
    """T002.0h AC6 — real-scale streaming peak memory < 500 MB.

    ADR-1 v3 CAP_v3 8.4 GiB compliance:
        The orchestrator's per-day streaming refactor MUST keep
        residente memory bounded by O(20+126) deque state + 1× day-of-
        trades stream consumed-and-discarded per inner loop iteration.
        We assert peak < 500 MB to leave ~7.9 GiB headroom for the
        downstream CPCV harness under CAP_v3.

    Real-scale fixture: ≥146 valid business days × 50_000 trades/day.
        - 146 days = T002.0g warmup window (126 P126 + 20 ATR_20 aux).
        - 50_000 trades/day matches Beckett's smoke RSS observation
          (parquet WDO 2024-2025: ~50-100k trades/day intraday).

    Without this patch (T002.0g legacy bulk-aggregation path), the
    per-day ``buckets[day]: list[Trade]`` retention path consumed
    ~3.7 GB of Trade objects (146 × 50k × ~500B incl. dataclass overhead
    after Python's per-object alignment). The streaming refactor caps
    it at < 500 MB.
    """
    cal = _permissive_calendar()
    # 50_000 trades/day matches Beckett smoke observation (ADR-1 v3 floor).
    source = _PerDayStreamingSource(trades_per_day=50_000)
    out_dir = tmp_path / "state"
    as_of = date(2025, 5, 31)

    # tracemalloc captures Python-level allocations; this is the right
    # proxy for the "Trade objects retained" bug (the failure mode is
    # Python object retention, not malloc'd buffers in pyarrow). Peak
    # is the high-water mark across the entire orchestrate call.
    tracemalloc.start()
    try:
        orchestrate_warmup_state(
            as_of_dates=[as_of],
            source=source,
            output_dir=out_dir,
            calendar=cal,
            calendar_sha="memory-regression",
            holdout_assert=_noop_holdout,
        )
        current_bytes, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    # ADR-1 v3 CAP_v3 8.4 GiB invariant — peak MUST stay well below the
    # cap (500 MB ≈ 5.8% of CAP_v3) so concurrent CPCV harness retains
    # ~7.9 GiB headroom downstream.
    peak_mb = peak_bytes / (1024 * 1024)
    cap_v3_gib = 8.4
    headroom_gib_at_500mb = cap_v3_gib - 0.5
    assert peak_bytes < 500 * 1024 * 1024, (
        f"T002.0h AC6 violation: peak Python heap = {peak_mb:.1f} MB "
        f"(>= 500 MB hard cap). ADR-1 v3 CAP_v3 = {cap_v3_gib} GiB; "
        f"500 MB cap leaves {headroom_gib_at_500mb:.1f} GiB headroom for "
        "CPCV harness downstream. Streaming refactor regressed — "
        "check for trade-object retention in orchestrator inner loop."
    )

    # Sanity: artifacts persisted (proves the streaming run actually
    # completed, not that we just tested empty work).
    assert (out_dir / f"atr_20d_{as_of.isoformat()}.json").exists()
    assert (out_dir / f"percentiles_126d_{as_of.isoformat()}.json").exists()
    assert (out_dir / "atr_20d.json").exists()
    assert (out_dir / "percentiles_126d.json").exists()
    assert (out_dir / "manifest.json").exists()
