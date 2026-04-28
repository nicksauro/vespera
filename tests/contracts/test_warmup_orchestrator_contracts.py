"""T6 — contract tests for the warmup orchestrator (Story T002.0g AC9 + AC12).

Coverage:
- AC12 — ``WarmUpGate.check(2025-05-31) == READY_TO_TRADE`` POST orchestrator
  (fixture orchestrator-driven per Beckett T0; NOT mocked JSON)
- AC9 — manifest pin presence check in ``.github/canonical-invariant.sums``
- AC12 amendment — 2024-06-30 ``@pytest.mark.skip(reason='BLOCK_GAP_UPSTREAM ...')``
- AC6 + AC9 — artifacts persisted under canonical ``state/T002/`` dir
"""

from __future__ import annotations

import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

import pytest

# Ensure repo root + scripts importable.
_REPO = Path(__file__).resolve().parents[2]
_SCRIPTS = _REPO / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from packages.t002_eod_unwind.warmup.atr_20d_builder import Trade  # noqa: E402
from packages.t002_eod_unwind.warmup.calendar_loader import CalendarData  # noqa: E402
from packages.t002_eod_unwind.warmup.gate import (  # noqa: E402
    WarmUpGate,
    WarmUpStatus,
)
from packages.t002_eod_unwind.warmup.orchestrator import (  # noqa: E402
    orchestrate_warmup_state,
)


# =====================================================================
# Fixtures (orchestrator-driven per Beckett T0)
# =====================================================================
def _permissive_calendar() -> CalendarData:
    return CalendarData(
        version="contract-test",
        copom_meetings=frozenset(),
        br_holidays=frozenset(),
        wdo_expirations=frozenset(),
        pre_long_weekends_br_with_us_open=frozenset(),
    )


def _gen_trades(start: date, end_inclusive: date) -> list[Trade]:
    trades: list[Trade] = []
    cur = start
    n = 0
    while cur <= end_inclusive:
        if cur.weekday() < 5:
            base_dt = datetime.combine(cur, time(9, 30, 0))
            base_price = 5000.0 + (n % 50)
            for offset_h, dp in (
                (0, 0.0),
                (2, (n % 7) * 0.5),
                (4, -(n % 5) * 0.5),
                (7, (n % 3) * 0.25),
            ):
                trades.append(
                    Trade(
                        ts=base_dt + timedelta(hours=offset_h, minutes=25 if offset_h == 7 else 0),
                        price=base_price + dp,
                        qty=1,
                    )
                )
            n += 1
        cur += timedelta(days=1)
    return trades


class _StubSource:
    def __init__(self, trades: list[Trade]) -> None:
        self.trades = trades

    def load_trades(
        self, start_brt: datetime, end_brt: datetime, ticker: str
    ) -> Iterable[Trade]:
        for tr in self.trades:
            if start_brt <= tr.ts < end_brt:
                yield tr


def _noop_holdout(start: date, end: date) -> None:
    return None


# =====================================================================
# AC12 — WarmUpGate ready-to-trade POST orchestrator (2025-05-31 only)
# =====================================================================
def test_warmup_gate_ready_to_trade_post_orchestrator(tmp_path):
    """AC12 (amended) — orchestrator output ⇒ WarmUpGate.check == READY_TO_TRADE.

    Fixture orchestrator-driven per Beckett T0 (NOT mocked JSON).
    Set restricted to ``{2025-05-31}`` per AC5 amendment (Dara
    BLOCK_GAP_UPSTREAM mini-council resolution APPROVE_OPTION_B).
    """
    out_dir = tmp_path / "state" / "T002"
    cal = _permissive_calendar()
    trades = _gen_trades(date(2023, 1, 1), date(2025, 12, 31))
    source = _StubSource(trades)

    as_of = date(2025, 5, 31)
    result = orchestrate_warmup_state(
        as_of_dates=[as_of],
        source=source,
        output_dir=out_dir,
        calendar=cal,
        calendar_sha="contract-test",
        holdout_assert=_noop_holdout,
    )

    # Use latest copies (the canonical paths WarmUpGate consumes).
    gate = WarmUpGate(result.latest_atr_path, result.latest_percentiles_path)
    verdict = gate.check(as_of)
    assert verdict.status == WarmUpStatus.READY_TO_TRADE, (
        f"expected READY_TO_TRADE, got {verdict.status} (reason={verdict.reason})"
    )
    assert verdict.atr_file_ok and verdict.percentiles_file_ok


@pytest.mark.skip(
    reason="BLOCK_GAP_UPSTREAM 2023 manifest gap; tracked USER-ESCALATION-QUEUE.md"
)
def test_2024_06_30_skipped_pending_data_coverage(tmp_path):  # pragma: no cover
    """AC12 amendment — 2024-06-30 SKIPPED until upstream data coverage resolved.

    Dara T0 BLOCK_GAP_UPSTREAM (resolved by 4/4 mini-council
    APPROVE_OPTION_B). Test left in-place as a TODO marker so a future
    coverage-resolution run can simply remove the skip.
    """
    raise NotImplementedError("placeholder — see USER-ESCALATION-QUEUE.md")


# =====================================================================
# AC9 — manifest pin presence in canonical-invariant.sums
# =====================================================================
def test_manifest_pin_in_canonical_invariants_sums():
    """AC9 — ``.github/canonical-invariant.sums`` references the warmup
    manifest schema OR contains an entry for ``state/T002/manifest.json``.

    Riven custodial cosign (T8) ratifies the explicit checksum; this test
    enforces the *presence* of the pin so it cannot regress silently.
    The pin entry is added below as part of T1 to satisfy this contract.
    """
    sums_path = _REPO / ".github" / "canonical-invariant.sums"
    assert sums_path.exists(), "canonical-invariant.sums missing"
    content = sums_path.read_text(encoding="utf-8")
    # Either a literal path entry or a marker comment honoring the schema.
    has_path_entry = "state/T002/manifest.json" in content
    has_schema_marker = "T002.0g-orchestrator" in content or "warmup-state-manifest" in content
    assert has_path_entry or has_schema_marker, (
        "canonical-invariant.sums missing T002.0g warmup manifest pin"
    )


# =====================================================================
# AC6 + AC9 — artifacts persisted under canonical state/T002/ dir
# =====================================================================
def test_artifacts_persisted_state_T002_dir(tmp_path):
    """AC6 + AC9 — orchestrator writes to ``state/T002/`` (caller-supplied)
    and creates: dated state files + latest copies + manifest + stamp.
    """
    out_dir = tmp_path / "state" / "T002"
    cal = _permissive_calendar()
    trades = _gen_trades(date(2023, 1, 1), date(2025, 12, 31))
    source = _StubSource(trades)

    orchestrate_warmup_state(
        as_of_dates=[date(2025, 5, 31)],
        source=source,
        output_dir=out_dir,
        calendar=cal,
        holdout_assert=_noop_holdout,
    )
    expected = {
        "atr_20d_2025-05-31.json",
        "percentiles_126d_2025-05-31.json",
        "atr_20d.json",
        "percentiles_126d.json",
        "manifest.json",
        "determinism_stamp.json",
    }
    actual = {p.name for p in out_dir.iterdir() if p.is_file()}
    missing = expected - actual
    assert not missing, f"missing artifacts: {missing}; have {actual}"


# =====================================================================
# Path lift regression (cross-story Aria sanity)
# =====================================================================
def test_consumers_default_lifted_to_state_T002():
    """T3 — verify ``cpcv_harness.py`` + ``run_cpcv_dry_run.py`` defaults
    were atomically lifted from ``data/warmup/`` ⇒ ``state/T002/``.
    """
    from packages.t002_eod_unwind import cpcv_harness as harn
    import run_cpcv_dry_run as runner  # noqa: PLC0415

    assert harn._DEFAULT_ATR_PATH == Path("state/T002/atr_20d.json")
    assert harn._DEFAULT_PERCENTILES_PATH == Path("state/T002/percentiles_126d.json")
    assert runner._DEFAULT_ATR_PATH == Path("state/T002/atr_20d.json")
    assert runner._DEFAULT_PERCENTILES_PATH == Path("state/T002/percentiles_126d.json")


# =====================================================================
# Guard #1 regression (silent fallback removal in run_cpcv_dry_run)
# =====================================================================
def test_run_cpcv_dry_run_load_warmup_state_fail_closed_on_missing(tmp_path):
    """Guard #1 — _load_warmup_state must raise (not return neutral state)
    when the warmup percentiles file is absent.
    """
    import run_cpcv_dry_run as runner  # noqa: PLC0415

    missing = tmp_path / "does-not-exist.json"
    with pytest.raises(FileNotFoundError):
        runner._load_warmup_state(missing)


def test_run_cpcv_dry_run_load_warmup_state_fail_closed_on_corrupt(tmp_path):
    """Guard #1 — _load_warmup_state must raise on corrupt JSON (no neutral fallback)."""
    import run_cpcv_dry_run as runner  # noqa: PLC0415

    bad = tmp_path / "corrupt.json"
    bad.write_text("{ this is not valid json", encoding="utf-8")
    with pytest.raises(ValueError):
        runner._load_warmup_state(bad)
