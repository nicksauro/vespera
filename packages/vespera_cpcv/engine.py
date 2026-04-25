"""CPCVEngine — Purged Combinatorial Cross-Validation engine.

Implements AFML Ch.12 §12.4 with §7.4.1 purging and §7.4.2 embargo, per
Mira spec ``docs/ml/specs/T002-cpcv-purge-formula.md``.

Public API:
    CPCVSplit         — frozen dataclass: one fold's train/test/diagnostics
    CPCVEngine        — engine with ``generate_splits`` + ``run`` entrypoints

Determinism (R6):
    Splits are emitted in canonical ``itertools.combinations`` order over
    ``range(n_groups)``. Partition is contiguous via the index. Purge
    formula and embargo formula are pure functions of (events,
    test_block_window). Seed is plumbed through to ``content_sha256`` of
    config but does not affect the partition itself.

Hold-out lock (R1 + R15(d) + AC12 of story):
    ``generate_splits`` calls ``assert_holdout_safe`` ONCE on the outer
    window ``[min(t_start).date(), max(t_end).date()]`` BEFORE iterating.
    Per-fold gates are not needed because the outer window covers all
    sub-windows (Beckett §3.2 contract).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from typing import Callable, Iterator

import numpy as np
import pandas as pd

from packages.t002_eod_unwind.adapters._holdout_lock import assert_holdout_safe

from .config import CPCVConfig
from .purge import TestBlock, decompose_test_blocks, embargo_train, purge_train
from .result import BacktestResult


# ---------------------------------------------------------------
# CPCVSplit — one fold's partition + diagnostics
# ---------------------------------------------------------------
@dataclass(frozen=True)
class CPCVSplit:
    """One CPCV fold.

    Attributes
    ----------
    path_id:
        Index into ``itertools.combinations(range(n_groups), k)`` (0..n_paths-1).
    group_ids_test:
        Sorted tuple of group indices in the test set.
    group_ids_train:
        Sorted tuple of group indices in the train set (complement).
    train_events:
        DataFrame of events in train, after purge + embargo.
    test_events:
        DataFrame of events in test (untouched).
    purged_events:
        DataFrame of train events removed by purge (diagnostics).
    embargoed_events:
        DataFrame of train events removed by embargo (diagnostics).
    test_blocks:
        List of contiguous test sub-blocks (Mira §3, §5.3-5.4).
    """

    path_id: int
    group_ids_test: tuple[int, ...]
    group_ids_train: tuple[int, ...]
    train_events: pd.DataFrame
    test_events: pd.DataFrame
    purged_events: pd.DataFrame
    embargoed_events: pd.DataFrame
    test_blocks: tuple[TestBlock, ...]

    def hash_split(self) -> str:
        """Deterministic hash of (path_id, group_ids_test, train_index_tuple,
        test_index_tuple). For AC6/AC9 (determinism + parallel safety).
        """
        train_idx = tuple(int(i) for i in self.train_events.index.tolist())
        test_idx = tuple(int(i) for i in self.test_events.index.tolist())
        payload = (
            f"path={self.path_id}|"
            f"test_groups={self.group_ids_test}|"
            f"train_idx={train_idx}|"
            f"test_idx={test_idx}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------
# CPCVEngine
# ---------------------------------------------------------------
class CPCVEngine:
    """Stateless-after-construction CPCV engine.

    Parameters
    ----------
    config:
        Validated ``CPCVConfig`` instance.

    Notes
    -----
    The engine does NOT mutate ``config`` or any global state; instances
    are safe to share across threads / processes (AC7).
    """

    REQUIRED_COLUMNS = ("t_start", "t_end", "session")

    def __init__(self, config: CPCVConfig) -> None:
        self._config = config
        # Seeded RNG — held for any future stochastic component (Mira
        # bootstrap CI). Splits themselves are deterministic by construction.
        self._rng = np.random.default_rng(config.seed)

    @property
    def config(self) -> CPCVConfig:
        return self._config

    # -----------------------------------------------------------
    # Public API
    # -----------------------------------------------------------
    def generate_splits(self, events: pd.DataFrame) -> Iterator[CPCVSplit]:
        """Yield ``n_paths`` CPCVSplit instances in canonical order.

        AC2: exactly C(N, k) splits.
        AC3: contiguous temporal partition via ``np.array_split``.
        AC4: purge applied per Mira §3 (eq. 7.1).
        AC5: embargo applied per Mira §4.
        AC6: deterministic — same events ⇒ same split sequence (byte-equal).
        AC12: hold-out lock fail-closed BEFORE any partition I/O.
        AC13: post-purge invariant validated by ``tests/cpcv/test_purge_formula.py``.
        """
        self._validate_events(events)

        # AC12: hold-out gate on outer window — once, before any work.
        outer_start = events["t_start"].min().date()
        outer_end = events["t_end"].max().date()
        assert_holdout_safe(outer_start, outer_end)

        # M < N defense (Mira §5.7)
        m = len(events)
        if m < self._config.n_groups:
            raise ValueError(
                f"Insufficient events: M={m} < N={self._config.n_groups}; "
                "need M >= N (ideally M >= 10*N for AFML CPCV)."
            )

        # Contiguous partition (Mira §2)
        group_assignment = self._assign_groups(events)
        all_sessions = sorted(events["session"].unique())

        # Canonical order: itertools.combinations(range(N), k)
        for path_id, test_groups in enumerate(
            combinations(range(self._config.n_groups), self._config.k)
        ):
            yield self._build_split(
                events=events,
                path_id=path_id,
                test_group_ids=test_groups,
                group_assignment=group_assignment,
                all_sessions=all_sessions,
            )

    def run(
        self,
        events: pd.DataFrame,
        backtest_fn: Callable[[pd.DataFrame, pd.DataFrame, "CPCVSplit"], BacktestResult],
        *,
        spec_snapshot: dict | None = None,  # noqa: ARG002 — reserved for Beckett §3.1
    ) -> list[BacktestResult]:
        """Consume ``generate_splits``, invoke ``backtest_fn`` per split.

        Returns a list of length ``config.n_paths`` ordered by
        ``fold.path_index`` ascending (Beckett §3.2).

        ``backtest_fn(train_events, test_events, split) -> BacktestResult``
        is called once per fold. The engine handles hold-out lock + purge
        + embargo; ``backtest_fn`` only sees post-purge train events.
        """
        results: list[BacktestResult] = []
        for split in self.generate_splits(events):
            result = backtest_fn(split.train_events, split.test_events, split)
            results.append(result)
        # Beckett §3.2 — sort by path_index ascending (already in order, but assert)
        results.sort(key=lambda r: r.fold.path_index)
        return results

    # -----------------------------------------------------------
    # Internals
    # -----------------------------------------------------------
    def _validate_events(self, events: pd.DataFrame) -> None:
        if not isinstance(events, pd.DataFrame):
            raise TypeError(
                f"events must be a pandas DataFrame, got {type(events).__name__}"
            )
        missing = [c for c in self.REQUIRED_COLUMNS if c not in events.columns]
        if missing:
            raise ValueError(
                f"events DataFrame missing required columns: {missing}. "
                f"Required: {self.REQUIRED_COLUMNS}"
            )
        if events.empty:
            raise ValueError("events DataFrame is empty.")
        # Reset index defense — engine relies on positional integer index.
        if not events.index.is_monotonic_increasing:
            raise ValueError(
                "events DataFrame index must be monotonic increasing "
                "(positional integer order by t_start)."
            )

    def _assign_groups(self, events: pd.DataFrame) -> pd.Series:
        """Contiguous partition via ``np.array_split`` (Mira §2).

        Returns a Series mapping global index → group id (0..N-1).
        """
        chunks = np.array_split(events.index.to_numpy(), self._config.n_groups)
        out = pd.Series(index=events.index, dtype="int64")
        for j, chunk in enumerate(chunks):
            out.loc[chunk] = j
        return out

    def _build_split(
        self,
        *,
        events: pd.DataFrame,
        path_id: int,
        test_group_ids: tuple[int, ...],
        group_assignment: pd.Series,
        all_sessions: list[date],
    ) -> CPCVSplit:
        # Test events
        test_mask = group_assignment.isin(test_group_ids)
        test_events = events[test_mask]

        # Train (raw) = complement
        train_raw = events[~test_mask]

        # Decompose test groups into contiguous blocks
        test_blocks = decompose_test_blocks(
            test_events=test_events,
            test_group_ids=test_group_ids,
            group_assignment=group_assignment,
        )

        # Purge (AFML §7.4.1)
        train_post_purge, purged = purge_train(train_raw, test_blocks)

        # Embargo (AFML §7.4.2)
        train_post_embargo, embargoed = embargo_train(
            train_events=train_post_purge,
            test_blocks=test_blocks,
            embargo_sessions=self._config.embargo_sessions,
            all_sessions=all_sessions,
        )

        train_group_ids = tuple(
            sorted(int(g) for g in range(self._config.n_groups) if g not in test_group_ids)
        )

        return CPCVSplit(
            path_id=path_id,
            group_ids_test=tuple(test_group_ids),
            group_ids_train=train_group_ids,
            train_events=train_post_embargo,
            test_events=test_events,
            purged_events=purged,
            embargoed_events=embargoed,
            test_blocks=tuple(test_blocks),
        )


__all__ = ["CPCVEngine", "CPCVSplit"]
