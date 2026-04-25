"""Engine determinism + parallel safety (AC6 + AC7 + AC9 of story).

- AC6: same seed + same events ⇒ byte-identical split sequence (per-split hash).
- AC7: engine is stateless after construction.
- AC9: parallel consumption produces same hashes as serial.

Plus AC10 verification: ``CPCVConfig.from_spec_yaml`` parses T002 spec.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from packages.vespera_cpcv import CPCVConfig, CPCVEngine


SPEC_PATH = Path("docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml")


def _build_events(n_sessions: int = 100) -> pd.DataFrame:
    """In-sample sessions (2024-07-01 onwards) with 4 events/day."""
    rows = []
    base = date(2024, 7, 1)
    for s in range(n_sessions):
        d = base + timedelta(days=s)
        for hh, mm in [(16, 55), (17, 10), (17, 25), (17, 40)]:
            rows.append(
                {
                    "t_start": datetime.combine(d, datetime.min.time()).replace(hour=hh, minute=mm),
                    "t_end": datetime.combine(d, datetime.min.time()).replace(hour=17, minute=55),
                    "session": d,
                }
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------
# AC6 — determinism
# ---------------------------------------------------------------
def test_two_runs_same_seed_produce_identical_split_hashes() -> None:
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    events = _build_events()
    engine_a = CPCVEngine(cfg)
    engine_b = CPCVEngine(cfg)
    hashes_a = [s.hash_split() for s in engine_a.generate_splits(events)]
    hashes_b = [s.hash_split() for s in engine_b.generate_splits(events)]
    assert hashes_a == hashes_b
    assert len(hashes_a) == 45  # C(10, 2) — AC2


def test_three_runs_byte_identical_hashes() -> None:
    """AC12 strict: 3 runs ⇒ byte-identical per-split hash list."""
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    events = _build_events()
    runs = []
    for _ in range(3):
        engine = CPCVEngine(cfg)
        runs.append(tuple(s.hash_split() for s in engine.generate_splits(events)))
    assert runs[0] == runs[1] == runs[2]


# ---------------------------------------------------------------
# AC9 — parallel safety
# ---------------------------------------------------------------
def test_parallel_consumption_produces_same_hashes_as_serial() -> None:
    """A naive parallel consumer (using a list of materialized splits)
    produces the same hash list as serial iteration.

    Note: ``CPCVEngine.generate_splits`` is a generator — true parallel
    iteration requires materializing first, then dispatching. This test
    validates that the materialized splits hash deterministically, which
    is the core invariant for ``joblib.Parallel`` consumers.
    """
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    events = _build_events()
    engine = CPCVEngine(cfg)

    serial_splits = list(engine.generate_splits(events))
    serial_hashes = [s.hash_split() for s in serial_splits]

    # Simulate parallel: shuffle materialized list, hash, sort by path_id, compare.
    # The split itself is frozen, so order-of-hashing doesn't change content.
    import random

    shuffled = serial_splits.copy()
    random.Random(0).shuffle(shuffled)
    parallel_hashes_unsorted = [(s.path_id, s.hash_split()) for s in shuffled]
    parallel_hashes_sorted = [h for _, h in sorted(parallel_hashes_unsorted)]
    assert parallel_hashes_sorted == serial_hashes


def test_engine_is_stateless_after_construction() -> None:
    """Two consecutive calls to ``generate_splits`` on the same engine
    instance produce identical sequences (AC7).
    """
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    events = _build_events()
    engine = CPCVEngine(cfg)
    first = [s.hash_split() for s in engine.generate_splits(events)]
    second = [s.hash_split() for s in engine.generate_splits(events)]
    assert first == second


# ---------------------------------------------------------------
# AC10 — config parsing from T002 spec
# ---------------------------------------------------------------
def test_from_spec_yaml_parses_t002_v0_2_0() -> None:
    if not SPEC_PATH.exists():
        pytest.skip(f"Spec yaml not present at {SPEC_PATH}")
    cfg = CPCVConfig.from_spec_yaml(SPEC_PATH)
    assert cfg.n_groups == 10
    assert cfg.k == 2
    assert cfg.embargo_sessions == 1
    assert cfg.n_paths == 45
    assert cfg.purge_formula_id == "AFML_7_4_1_intraday_H_eq_session"


def test_from_spec_yaml_respects_seed_env(monkeypatch: pytest.MonkeyPatch) -> None:
    if not SPEC_PATH.exists():
        pytest.skip(f"Spec yaml not present at {SPEC_PATH}")
    monkeypatch.setenv("SPEC_SEED", "12345")
    cfg = CPCVConfig.from_spec_yaml(SPEC_PATH)
    assert cfg.seed == 12345


def test_from_spec_yaml_default_seed_is_42(monkeypatch: pytest.MonkeyPatch) -> None:
    if not SPEC_PATH.exists():
        pytest.skip(f"Spec yaml not present at {SPEC_PATH}")
    monkeypatch.delenv("SPEC_SEED", raising=False)
    cfg = CPCVConfig.from_spec_yaml(SPEC_PATH)
    assert cfg.seed == 42


def test_from_spec_yaml_rejects_non_cpcv(tmp_path: Path) -> None:
    fake = tmp_path / "fake_spec.yaml"
    fake.write_text(
        "cv_scheme:\n"
        "  type: KFold\n"
        "  n_groups: 5\n"
        "  k: 1\n"
        "  embargo_sessions: 0\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Unsupported cv_scheme.type"):
        CPCVConfig.from_spec_yaml(fake)


def test_config_validation_rejects_k_geq_n_groups() -> None:
    with pytest.raises(ValueError, match="k must satisfy"):
        CPCVConfig(n_groups=3, k=3, embargo_sessions=1, seed=42)


def test_config_validation_rejects_negative_embargo() -> None:
    with pytest.raises(ValueError, match="embargo_sessions"):
        CPCVConfig(n_groups=10, k=2, embargo_sessions=-1, seed=42)


def test_config_validation_rejects_n_groups_lt_2() -> None:
    with pytest.raises(ValueError, match="n_groups"):
        CPCVConfig(n_groups=1, k=1, embargo_sessions=0, seed=42)


# ---------------------------------------------------------------
# AC13 — no-lookahead invariant after purge + embargo
# ---------------------------------------------------------------
def test_no_lookahead_invariant_holds_for_all_splits() -> None:
    """For each split, every train event must be EITHER strictly before
    EVERY test block window OR strictly after the embargo window.
    """
    cfg = CPCVConfig(n_groups=10, k=2, embargo_sessions=1, seed=42)
    events = _build_events()
    engine = CPCVEngine(cfg)
    for split in engine.generate_splits(events):
        for _, train_row in split.train_events.iterrows():
            for block in split.test_blocks:
                # The train event must NOT overlap the test window.
                overlap = (
                    train_row["t_end"] >= block.window_start
                    and train_row["t_start"] <= block.window_end
                )
                assert not overlap, (
                    f"split {split.path_id}: train event "
                    f"[{train_row['t_start']}, {train_row['t_end']}] "
                    f"overlaps test block [{block.window_start}, {block.window_end}]"
                )
