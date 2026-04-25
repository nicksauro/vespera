"""Unit tests for purge + embargo formulas in isolation.

Validates Mira spec §3 (purge eq. 7.1) and §4 (embargo per session).
Tests run on hand-crafted DataFrames that exercise the formula directly,
bypassing the engine.
"""

from __future__ import annotations

from datetime import date, datetime

import pandas as pd

from packages.vespera_cpcv.purge import (
    CPCVTestBlock,
    decompose_test_blocks,
    embargo_train,
    purge_train,
)

# Local alias so test code reads naturally without triggering pytest's
# "Test*" auto-collection.
_Block = CPCVTestBlock


def _ev(idx: int, day: int, hour: int = 16, minute: int = 55) -> dict:
    return {
        "t_start": datetime(2024, 1, day, hour, minute),
        "t_end": datetime(2024, 1, day, 17, 55),
        "session": date(2024, 1, day),
    }


# ---------------------------------------------------------------
# decompose_test_blocks
# ---------------------------------------------------------------
def test_decompose_adjacent_groups_into_one_block() -> None:
    events = pd.DataFrame([_ev(i, d) for i, d in enumerate([2, 3, 4, 5])])
    # All 4 events in groups 0..3; test groups (1,2) → 1 contiguous block.
    group_assignment = pd.Series([0, 1, 2, 3], index=events.index)
    test_events = events[group_assignment.isin((1, 2))]
    blocks = decompose_test_blocks(test_events, (1, 2), group_assignment)
    assert len(blocks) == 1
    assert blocks[0].group_ids == (1, 2)


def test_decompose_disjoint_groups_into_two_blocks() -> None:
    events = pd.DataFrame([_ev(i, d) for i, d in enumerate([2, 3, 4, 5, 8, 9])])
    group_assignment = pd.Series([0, 1, 2, 3, 4, 5], index=events.index)
    test_events = events[group_assignment.isin((1, 4))]
    blocks = decompose_test_blocks(test_events, (1, 4), group_assignment)
    assert len(blocks) == 2
    assert blocks[0].group_ids == (1,)
    assert blocks[1].group_ids == (4,)


# ---------------------------------------------------------------
# purge_train
# ---------------------------------------------------------------
def test_purge_drops_train_with_label_overlap() -> None:
    """A train event whose [t_start, t_end] overlaps a test window MUST be dropped."""
    # Train event at day 5 with t_end on day 6 (artificial overlap).
    train = pd.DataFrame(
        [
            {
                "t_start": datetime(2024, 1, 5, 16, 55),
                "t_end": datetime(2024, 1, 6, 17, 55),  # crosses into test day
                "session": date(2024, 1, 5),
            }
        ]
    )
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 6, 16, 55),
        window_end=datetime(2024, 1, 6, 17, 55),
        last_session=date(2024, 1, 6),
    )
    kept, purged = purge_train(train, [block])
    assert len(purged) == 1
    assert len(kept) == 0


def test_purge_keeps_train_strictly_before_test() -> None:
    train = pd.DataFrame(
        [
            {
                "t_start": datetime(2024, 1, 5, 16, 55),
                "t_end": datetime(2024, 1, 5, 17, 55),
                "session": date(2024, 1, 5),
            }
        ]
    )
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 6, 16, 55),
        window_end=datetime(2024, 1, 6, 17, 55),
        last_session=date(2024, 1, 6),
    )
    kept, purged = purge_train(train, [block])
    assert len(kept) == 1
    assert len(purged) == 0


def test_purge_keeps_train_strictly_after_test() -> None:
    train = pd.DataFrame(
        [
            {
                "t_start": datetime(2024, 1, 8, 16, 55),
                "t_end": datetime(2024, 1, 8, 17, 55),
                "session": date(2024, 1, 8),
            }
        ]
    )
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 6, 16, 55),
        window_end=datetime(2024, 1, 6, 17, 55),
        last_session=date(2024, 1, 6),
    )
    kept, purged = purge_train(train, [block])
    assert len(kept) == 1
    assert len(purged) == 0


def test_purge_empty_train_is_noop() -> None:
    train = pd.DataFrame(columns=["t_start", "t_end", "session"])
    block = _Block(
        group_ids=(0,),
        window_start=datetime(2024, 1, 1),
        window_end=datetime(2024, 1, 1),
        last_session=date(2024, 1, 1),
    )
    kept, purged = purge_train(train, [block])
    assert len(kept) == 0
    assert len(purged) == 0


# ---------------------------------------------------------------
# embargo_train
# ---------------------------------------------------------------
def test_embargo_drops_next_session_after_block() -> None:
    days = [2, 3, 4, 5, 8]
    train = pd.DataFrame([_ev(i, d) for i, d in enumerate(days)])
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 4, 16, 55),
        window_end=datetime(2024, 1, 4, 17, 55),
        last_session=date(2024, 1, 4),
    )
    all_sessions = sorted({date(2024, 1, d) for d in days})
    kept, embargoed = embargo_train(
        train, [block], embargo_sessions=1, all_sessions=all_sessions
    )
    # Next session after Jan 4 = Jan 5 → 1 event embargoed.
    assert len(embargoed) == 1
    assert embargoed.iloc[0]["session"] == date(2024, 1, 5)
    assert len(kept) == len(train) - 1


def test_embargo_at_dataset_end_is_noop() -> None:
    """Mira §5.2 — block at dataset end ⇒ embargo no-op."""
    days = [2, 3, 4, 5]
    train = pd.DataFrame([_ev(i, d) for i, d in enumerate(days[:-1])])  # 3 train events
    block = _Block(
        group_ids=(3,),
        window_start=datetime(2024, 1, 5, 16, 55),
        window_end=datetime(2024, 1, 5, 17, 55),
        last_session=date(2024, 1, 5),  # = dataset's max session
    )
    all_sessions = sorted({date(2024, 1, d) for d in days})  # last is jan-5
    kept, embargoed = embargo_train(
        train, [block], embargo_sessions=1, all_sessions=all_sessions
    )
    assert len(embargoed) == 0
    assert len(kept) == len(train)


def test_embargo_zero_is_noop() -> None:
    days = [2, 3, 4, 5]
    train = pd.DataFrame([_ev(i, d) for i, d in enumerate(days)])
    block = _Block(
        group_ids=(0,),
        window_start=datetime(2024, 1, 2, 16, 55),
        window_end=datetime(2024, 1, 2, 17, 55),
        last_session=date(2024, 1, 2),
    )
    all_sessions = sorted({date(2024, 1, d) for d in days})
    kept, embargoed = embargo_train(
        train, [block], embargo_sessions=0, all_sessions=all_sessions
    )
    assert len(embargoed) == 0
    assert len(kept) == len(train)


def test_embargo_uses_dataset_calendar_not_calendar_b3() -> None:
    """Mira §5.5 — sessions skipping (rollover, copom) must respect dataset
    calendar. With sparse sessions, embargo of 1 jumps to the next PRESENT session.
    """
    # Dataset has gap between Jan 4 and Jan 8 (e.g., Jan 5 was rollover).
    days = [2, 3, 4, 8, 9]
    train = pd.DataFrame([_ev(i, d) for i, d in enumerate(days)])
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 4, 16, 55),
        window_end=datetime(2024, 1, 4, 17, 55),
        last_session=date(2024, 1, 4),
    )
    all_sessions = sorted({date(2024, 1, d) for d in days})
    kept, embargoed = embargo_train(
        train, [block], embargo_sessions=1, all_sessions=all_sessions
    )
    # Next session AFTER Jan 4 in the dataset is Jan 8 (NOT Jan 5).
    assert len(embargoed) == 1
    assert embargoed.iloc[0]["session"] == date(2024, 1, 8)


def test_embargo_two_sessions_drops_two() -> None:
    days = [2, 3, 4, 5, 8]
    train = pd.DataFrame([_ev(i, d) for i, d in enumerate(days)])
    block = _Block(
        group_ids=(2,),
        window_start=datetime(2024, 1, 4, 16, 55),
        window_end=datetime(2024, 1, 4, 17, 55),
        last_session=date(2024, 1, 4),
    )
    all_sessions = sorted({date(2024, 1, d) for d in days})
    kept, embargoed = embargo_train(
        train, [block], embargo_sessions=2, all_sessions=all_sessions
    )
    # Next 2 sessions after Jan 4 = Jan 5, Jan 8.
    assert len(embargoed) == 2
    assert set(embargoed["session"]) == {date(2024, 1, 5), date(2024, 1, 8)}
