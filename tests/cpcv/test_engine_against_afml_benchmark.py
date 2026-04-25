"""AC8 — CPCVEngine reproduces Mira's toy benchmark (N=6, k=2, M=6) byte-exact.

Reference: ``docs/ml/specs/T002-cpcv-purge-formula.md`` §6.4.

Per Mira §6.4 the expected per-split (n_test, n_embargoed, n_train_final)
table is:

    Split | T groups | Adj? | b=N-1? | Embargo events | |Train|
    -----------------------------------------------------------
    0     | (0,1)    | sim  | no     | 1              | 3
    1     | (0,2)    | no   | no     | 2              | 2
    2     | (0,3)    | no   | no     | 2              | 2
    3     | (0,4)    | no   | no     | 2              | 2
    4     | (0,5)    | no   | yes    | 1              | 3
    5     | (1,2)    | sim  | no     | 1              | 3
    6     | (1,3)    | no   | no     | 2              | 2
    7     | (1,4)    | no   | no     | 2              | 2
    8     | (1,5)    | no   | yes    | 1              | 3
    9     | (2,3)    | sim  | no     | 1              | 3
    10    | (2,4)    | no   | no     | 2              | 2
    11    | (2,5)    | no   | yes    | 1              | 3
    12    | (3,4)    | sim  | no     | 1              | 3
    13    | (3,5)    | no   | yes    | 1              | 3
    14    | (4,5)    | sim  | yes    | 0              | 4
    -----------------------------------------------------------
    Total embargoed events:                                20
    Total purged events:                                    0  (intraday label)

This is the AC8 byte-exact comparison (tolerance 0).
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pandas as pd
import pytest

from packages.vespera_cpcv import CPCVConfig, CPCVEngine


# ---------------------------------------------------------------
# Fixture: 6 events × 6 groups × k=2 toy dataset
# ---------------------------------------------------------------
def _build_toy_events() -> pd.DataFrame:
    """6 events on 6 distinct sessions (one event per group).

    Sessions chosen far enough into 2024 to NOT intersect the
    pre-registered hold-out window [2025-07-01, 2026-04-21].
    """
    base = date(2024, 1, 2)
    rows = []
    for i in range(6):
        d = base + timedelta(days=i * 7)  # weekly to avoid weekends/holidays
        # T002-style: t_start at 16:55, t_end at 17:55 same day.
        rows.append(
            {
                "t_start": datetime.combine(d, datetime.min.time()).replace(hour=16, minute=55),
                "t_end": datetime.combine(d, datetime.min.time()).replace(hour=17, minute=55),
                "session": d,
                "ev_id": i,
            }
        )
    df = pd.DataFrame(rows)
    return df


# Expected (n_embargoed, n_train_final) per Mira §6.4 table.
# Splits in canonical itertools.combinations(range(6), 2) order.
_EXPECTED = [
    # (path_id, test_groups, n_embargoed, n_train_final)
    (0, (0, 1), 1, 3),
    (1, (0, 2), 2, 2),
    (2, (0, 3), 2, 2),
    (3, (0, 4), 2, 2),
    (4, (0, 5), 1, 3),
    (5, (1, 2), 1, 3),
    (6, (1, 3), 2, 2),
    (7, (1, 4), 2, 2),
    (8, (1, 5), 1, 3),
    (9, (2, 3), 1, 3),
    (10, (2, 4), 2, 2),
    (11, (2, 5), 1, 3),
    (12, (3, 4), 1, 3),
    (13, (3, 5), 1, 3),
    (14, (4, 5), 0, 4),
]


# ---------------------------------------------------------------
# Tests
# ---------------------------------------------------------------
def test_total_split_count() -> None:
    """C(6, 2) = 15 splits."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(_build_toy_events()))
    assert len(splits) == 15


def test_canonical_combinations_order() -> None:
    """Splits emitted in itertools.combinations(range(6), 2) order."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(_build_toy_events()))
    for split, (path_id, expected_groups, _, _) in zip(splits, _EXPECTED):
        assert split.path_id == path_id
        assert split.group_ids_test == expected_groups


@pytest.mark.parametrize(
    "path_id,test_groups,n_embargoed_expected,n_train_expected",
    _EXPECTED,
    ids=[f"split_{p}_{tg}" for p, tg, _, _ in _EXPECTED],
)
def test_per_split_purge_embargo_match_afml_benchmark(
    path_id: int,
    test_groups: tuple[int, ...],
    n_embargoed_expected: int,
    n_train_expected: int,
) -> None:
    """Byte-exact match to Mira §6.4 table — per-split."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(_build_toy_events()))
    split = splits[path_id]

    # Test set: always 2 events
    assert len(split.test_events) == 2, f"path {path_id}: expected 2 test events"

    # Purge: 0 events for intraday-label toy (Mira §6.4)
    assert len(split.purged_events) == 0, (
        f"path {path_id}: expected 0 purged (intraday label, toy 1ev/group), "
        f"got {len(split.purged_events)}"
    )

    # Embargo: must match Mira table
    assert len(split.embargoed_events) == n_embargoed_expected, (
        f"path {path_id} test={test_groups}: "
        f"expected {n_embargoed_expected} embargoed, got {len(split.embargoed_events)}"
    )

    # Final train size
    assert len(split.train_events) == n_train_expected, (
        f"path {path_id} test={test_groups}: "
        f"expected |Train|={n_train_expected}, got {len(split.train_events)}"
    )


def test_total_embargoed_sum_matches_mira() -> None:
    """Sum across all 15 splits = 20 events embargoed (Mira §6.4)."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(_build_toy_events()))
    total = sum(len(s.embargoed_events) for s in splits)
    assert total == 20, f"Mira §6.4 says 20 total embargoed events; got {total}"


def test_total_purged_sum_zero() -> None:
    """Sum across all 15 splits = 0 events purged (intraday label, Mira §6.4)."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    splits = list(engine.generate_splits(_build_toy_events()))
    total = sum(len(s.purged_events) for s in splits)
    assert total == 0


def test_train_test_disjoint() -> None:
    """Sanity: train ∩ test = ∅ for all 15 splits."""
    cfg = CPCVConfig(n_groups=6, k=2, embargo_sessions=1, seed=42)
    engine = CPCVEngine(cfg)
    for split in engine.generate_splits(_build_toy_events()):
        train_idx = set(split.train_events.index)
        test_idx = set(split.test_events.index)
        assert not (train_idx & test_idx), (
            f"path {split.path_id}: train and test overlap"
        )
