"""BacktestRunner — orchestrates adapter → CPCVEngine → backtest_fn → results.

Thin wrapper around ``CPCVEngine.run`` that injects the determinism
stamp computed once per run (R15 + Beckett §5).

Usage::

    runner = BacktestRunner(
        config=CPCVConfig.from_spec_yaml("docs/ml/specs/...yaml"),
        spec_path="docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml",
        spec_version="0.2.0",
        simulator_version="0.3.1",
    )
    results = runner.run(events_in_sample, backtest_fn=beckett_backtest_fn)
    assert len(results) == 45

The runner does NOT persist results — that is the caller's
responsibility (Beckett §3.2 contract). Persistence path convention:
``docs/backtest/runs/{run_id}/folds/path_{path_index:02d}.json``.
"""

from __future__ import annotations

import hashlib
import platform
import sys
import uuid
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from .config import CPCVConfig
from .engine import CPCVEngine, CPCVSplit
from .result import BacktestResult, DeterminismStamp


class BacktestRunner:
    """Orchestrator wrapping CPCVEngine with a per-run DeterminismStamp.

    The stamp is computed once in ``__init__`` (or first ``run`` call —
    after the dataset hash is known). Callers can pass a pre-computed
    ``DeterminismStamp`` to bypass automatic computation (useful in tests).
    """

    def __init__(
        self,
        config: CPCVConfig,
        *,
        spec_path: str | Path | None = None,
        spec_version: str = "0.0.0",
        simulator_version: str = "0.0.0",
        engine_config_path: str | Path | None = None,
        rollover_calendar_path: str | Path | None = None,
        cost_atlas_path: str | Path | None = None,
    ) -> None:
        self._engine = CPCVEngine(config)
        self._spec_path = Path(spec_path) if spec_path else None
        self._spec_version = spec_version
        self._simulator_version = simulator_version
        self._engine_config_path = Path(engine_config_path) if engine_config_path else None
        self._rollover_calendar_path = (
            Path(rollover_calendar_path) if rollover_calendar_path else None
        )
        self._cost_atlas_path = Path(cost_atlas_path) if cost_atlas_path else None

    @property
    def engine(self) -> CPCVEngine:
        return self._engine

    @property
    def config(self) -> CPCVConfig:
        return self._engine.config

    def build_determinism_stamp(
        self,
        events: pd.DataFrame,
        *,
        run_id: str | None = None,
        timestamp_brt: datetime | None = None,
    ) -> DeterminismStamp:
        """Compute the per-run DeterminismStamp (R15 + Beckett §5)."""
        return DeterminismStamp(
            seed=self.config.seed,
            simulator_version=self._simulator_version,
            dataset_sha256=_hash_events(events),
            spec_sha256=_hash_file(self._spec_path) if self._spec_path else "",
            spec_version=self._spec_version,
            engine_config_sha256=(
                _hash_file(self._engine_config_path) if self._engine_config_path else ""
            ),
            rollover_calendar_sha256=(
                _hash_file(self._rollover_calendar_path)
                if self._rollover_calendar_path
                else None
            ),
            cost_atlas_sha256=(
                _hash_file(self._cost_atlas_path) if self._cost_atlas_path else None
            ),
            cpcv_config_sha256=self.config.content_sha256(),
            python_version=platform.python_version(),
            numpy_version=np.__version__,
            pandas_version=pd.__version__,
            run_id=run_id or uuid.uuid4().hex,
            timestamp_brt=timestamp_brt or datetime.now(),  # BRT-naive (R2)
        )

    def run(
        self,
        events: pd.DataFrame,
        backtest_fn: Callable[[pd.DataFrame, pd.DataFrame, CPCVSplit], BacktestResult],
        *,
        determinism: DeterminismStamp | None = None,
        run_id: str | None = None,
    ) -> list[BacktestResult]:
        """Drive the engine over ``events``, returning ordered results.

        If ``determinism`` is None, a fresh stamp is built from
        ``build_determinism_stamp(events)`` and INJECTED into each result
        via ``dataclasses.replace`` so the per-run audit trail is uniform
        across folds.
        """
        if determinism is None:
            determinism = self.build_determinism_stamp(events, run_id=run_id)

        raw_results = self._engine.run(events, backtest_fn=backtest_fn)
        # Inject the per-run stamp uniformly (idempotent if backtest_fn already set it).
        stamped: list[BacktestResult] = []
        for r in raw_results:
            stamped.append(replace(r, determinism=determinism))
        return stamped


# ---------------------------------------------------------------
# Hashing utilities (private)
# ---------------------------------------------------------------
def _hash_file(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_events(events: pd.DataFrame) -> str:
    """Deterministic hash of an events DataFrame.

    Hashes (column names, dtypes, string-form of every value). Strict
    equality across re-runs requires the input DataFrame to be byte-stable
    — caller's responsibility.
    """
    h = hashlib.sha256()
    h.update("|".join(events.columns).encode("utf-8"))
    h.update(b"||")
    h.update("|".join(str(d) for d in events.dtypes).encode("utf-8"))
    h.update(b"||")
    # Use to_csv for stable string serialization (no float drift).
    h.update(events.to_csv(index=True).encode("utf-8"))
    return h.hexdigest()


__all__ = ["BacktestRunner"]


# Bind sys for build hash (placeholder for future use).
_ = sys  # noqa: F401
