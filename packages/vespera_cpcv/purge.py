"""Purge + embargo functions per Mira spec T002-cpcv-purge-formula.md.

Pure, deterministic, no I/O. Operates on pandas DataFrames with the
canonical event schema:

    - index: positional integer (0..M-1)
    - column 't_start' (datetime BRT-naive): when feature is computed
    - column 't_end'   (datetime BRT-naive): when label deadline is reached
    - column 'session' (date BRT-naive):     calendar session (date of t_start)

Authority:
    AFML Ch.7 §7.4.1 (purging) eq. 7.1
    AFML Ch.7 §7.4.2 (embargo)
    Mira spec §3 (purge), §4 (embargo), §5 (edge cases)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import NamedTuple

import pandas as pd


class CPCVTestBlock(NamedTuple):
    """One contiguous test block: a maximal run of adjacent test groups.

    Named ``CPCVTestBlock`` (not ``TestBlock``) to avoid pytest's
    auto-collection of any class starting with ``Test``.

    ``window_start`` = min(t_start) over all events in the block.
    ``window_end``   = max(t_end)   over all events in the block.
    ``last_session`` = max(session) over all events in the block (used by
    embargo to step forward in the calendar of the dataset).
    """

    group_ids: tuple[int, ...]
    window_start: datetime
    window_end: datetime
    last_session: date


# Backwards-compatible alias for older imports.
TestBlock = CPCVTestBlock


def decompose_test_blocks(
    test_events: pd.DataFrame,
    test_group_ids: tuple[int, ...],
    group_assignment: pd.Series,
) -> list[TestBlock]:
    """Split the chosen test groups into contiguous blocks.

    ``test_group_ids`` is sorted ascending. Adjacent group ids (j and j+1)
    are merged into a single block; gaps create new blocks.

    Parameters
    ----------
    test_events:
        DataFrame of all events in the chosen test groups (subset of full
        events, indexed positionally over the GLOBAL event order).
    test_group_ids:
        Sorted tuple of group indices selected for test (e.g. ``(2, 7)``).
    group_assignment:
        Series mapping global event index → group id. Used to locate
        which events belong to which group.
    """
    if not test_group_ids:
        return []

    # Walk through sorted group ids, merging contiguous runs.
    blocks: list[tuple[int, ...]] = []
    current: list[int] = [test_group_ids[0]]
    for j in test_group_ids[1:]:
        if j == current[-1] + 1:
            current.append(j)
        else:
            blocks.append(tuple(current))
            current = [j]
    blocks.append(tuple(current))

    out: list[TestBlock] = []
    for block_groups in blocks:
        # All events whose group is in block_groups.
        mask = group_assignment.isin(block_groups)
        evs = test_events.loc[test_events.index.intersection(group_assignment[mask].index)]
        if evs.empty:
            continue
        window_start = evs["t_start"].min()
        window_end = evs["t_end"].max()
        last_session = evs["session"].max()
        out.append(
            TestBlock(
                group_ids=block_groups,
                window_start=window_start,
                window_end=window_end,
                last_session=last_session,
            )
        )
    return out


def purge_train(
    train_events: pd.DataFrame,
    test_blocks: list[TestBlock],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """AFML §7.4.1 eq. 7.1 — drop train rows whose label horizon overlaps
    any test block window.

    A train event ``e`` is purged iff there exists a test block ``B`` such
    that::

        t_end(e)   >= window(B).start  AND
        t_start(e) <= window(B).end

    Returns
    -------
    (kept, purged):
        Two DataFrames; ``kept`` is the post-purge train; ``purged`` carries
        the dropped rows for diagnostics.
    """
    if train_events.empty or not test_blocks:
        return train_events, train_events.iloc[0:0]

    drop_mask = pd.Series(False, index=train_events.index)
    for block in test_blocks:
        overlaps = (
            (train_events["t_end"] >= block.window_start)
            & (train_events["t_start"] <= block.window_end)
        )
        drop_mask = drop_mask | overlaps

    purged = train_events[drop_mask]
    kept = train_events[~drop_mask]
    return kept, purged


def embargo_train(
    train_events: pd.DataFrame,
    test_blocks: list[TestBlock],
    embargo_sessions: int,
    all_sessions: list[date],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """AFML §7.4.2 — drop the next ``embargo_sessions`` calendar sessions
    after each test block.

    Per Mira spec §4.2: "session" means a unique date present in the
    dataset (``all_sessions`` is the sorted unique session dates of
    ``events``). With ``embargo_sessions=1``, all events whose session
    equals the FIRST distinct session strictly after ``block.last_session``
    are dropped. With ``embargo_sessions=2``, the first TWO distinct
    sessions strictly after are dropped, and so on.

    If the test block's last session is at or beyond the dataset's last
    session, embargo is a no-op (Mira §5.2).

    Returns
    -------
    (kept, embargoed):
        Two DataFrames; ``kept`` is post-embargo; ``embargoed`` is dropped.
    """
    if train_events.empty or embargo_sessions <= 0 or not test_blocks:
        return train_events, train_events.iloc[0:0]

    sessions_to_drop: set[date] = set()
    for block in test_blocks:
        # Find the index of block.last_session in all_sessions, then take
        # the next ``embargo_sessions`` sessions strictly after.
        # Bisect-style lookup: first session > block.last_session.
        # (all_sessions is sorted ascending.)
        cutoff = block.last_session
        idx_after = next(
            (i for i, s in enumerate(all_sessions) if s > cutoff),
            None,
        )
        if idx_after is None:
            continue  # cutoff is at/after dataset end — no embargo
        end_idx = min(idx_after + embargo_sessions, len(all_sessions))
        for s in all_sessions[idx_after:end_idx]:
            sessions_to_drop.add(s)

    if not sessions_to_drop:
        return train_events, train_events.iloc[0:0]

    drop_mask = train_events["session"].isin(sessions_to_drop)
    embargoed = train_events[drop_mask]
    kept = train_events[~drop_mask]
    return kept, embargoed


__all__ = [
    "CPCVTestBlock",
    "TestBlock",
    "decompose_test_blocks",
    "embargo_train",
    "purge_train",
]
