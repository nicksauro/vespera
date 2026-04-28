"""T002.0h AC8 amendment — ``ParquetHandleCache`` LRU semantics.

Story: ``docs/stories/T002.0h.story.md`` (AC8 amendment 2026-04-26 BRT —
Option C cached file handles for wall-time mitigation).

Coverage:

- ``test_cache_hit_reduces_open_calls`` — repeated ``get(path)`` for the
  SAME path opens the underlying ``ParquetFile`` exactly once. Memoization
  contract.
- ``test_lru_eviction_at_max`` — when the working set exceeds
  ``max_handles``, the LEAST recently used handle is evicted; a
  re-request for an evicted path triggers a fresh open.
- ``test_cache_clear_releases_handles`` — ``clear()`` drops all cached
  handles; subsequent ``get`` re-opens.
- ``test_max_handles_validation`` — constructor rejects ``max_handles < 1``.
- ``test_get_manifest_memoization`` — companion manifest cache calls the
  loader exactly once.
- ``test_get_manifest_cleared_by_clear`` — ``clear()`` also resets the
  manifest slot.

Anti-leak NEUTRAL: cache does NOT affect iteration order, window
predicates, or per-day ``load_trades`` semantics — purely memory/IO
optimization. Mira shifted-by-1 invariant preserved at the orchestrator
ascending-iteration assertion (covered by
``test_streaming_memory.py::test_iteration_strictly_ascending``).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure repo root importable.
_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from packages.t002_eod_unwind.warmup._parquet_handle_cache import (  # noqa: E402
    ParquetHandleCache,
)


class _StubParquetFile:
    """Minimal stand-in for ``pyarrow.parquet.ParquetFile``.

    Carries the path it was opened with so tests can assert identity
    (each open is a distinct instance).
    """

    instances_created = 0

    def __init__(self, path: Path) -> None:
        self.path = Path(path).resolve()
        self.closed = False
        type(self).instances_created += 1

    def close(self) -> None:
        self.closed = True


@pytest.fixture(autouse=True)
def _reset_stub_counter():
    _StubParquetFile.instances_created = 0
    yield


def _make_cache(max_handles: int = 6) -> ParquetHandleCache:
    """Construct a cache whose ``_open_parquet`` factory uses ``_StubParquetFile``.

    Avoids importing pyarrow in the unit-test path (parity with the
    orchestrator's lazy-import pattern).
    """
    cache = ParquetHandleCache(max_handles=max_handles)
    # Override the factory hook with the stub.
    cache._open_parquet = _StubParquetFile  # type: ignore[assignment, method-assign]
    return cache


def test_cache_hit_reduces_open_calls(tmp_path: Path) -> None:
    """Repeated ``get(path)`` opens the underlying ParquetFile exactly once."""
    cache = _make_cache(max_handles=6)
    parquet_a = tmp_path / "a.parquet"
    parquet_a.touch()

    h1 = cache.get(parquet_a)
    h2 = cache.get(parquet_a)
    h3 = cache.get(parquet_a)

    # Same instance returned on hits.
    assert h1 is h2 is h3
    # Exactly one open even though we requested 3 times.
    assert _StubParquetFile.instances_created == 1
    assert cache.hits == 2
    assert cache.misses == 1
    assert len(cache) == 1


def test_lru_eviction_at_max(tmp_path: Path) -> None:
    """When working set exceeds ``max_handles``, LRU is evicted."""
    cache = _make_cache(max_handles=2)
    pa = tmp_path / "a.parquet"
    pb = tmp_path / "b.parquet"
    pc = tmp_path / "c.parquet"
    for p in (pa, pb, pc):
        p.touch()

    h_a = cache.get(pa)         # cache: [a]
    h_b = cache.get(pb)         # cache: [a, b]
    assert _StubParquetFile.instances_created == 2
    assert len(cache) == 2

    # Touch ``a`` so ``b`` becomes LRU.
    h_a_again = cache.get(pa)
    assert h_a_again is h_a

    # Insert ``c`` — should evict ``b`` (LRU).
    h_c = cache.get(pc)         # cache: [a, c]
    assert _StubParquetFile.instances_created == 3
    assert len(cache) == 2
    assert h_a.closed is False
    assert h_b.closed is True   # evicted handle was closed (best-effort)
    assert h_c.closed is False

    # Re-requesting ``b`` triggers a fresh open (different instance).
    h_b_new = cache.get(pb)
    assert h_b_new is not h_b
    assert _StubParquetFile.instances_created == 4
    # Evicting ``a`` now (b's insertion pushes the cache to [c, b], so
    # the new ``b`` insert pushed ``a`` out).
    assert h_a.closed is True


def test_cache_clear_releases_handles(tmp_path: Path) -> None:
    """``clear()`` drops + closes all cached handles."""
    cache = _make_cache(max_handles=6)
    pa = tmp_path / "a.parquet"
    pb = tmp_path / "b.parquet"
    for p in (pa, pb):
        p.touch()

    h_a = cache.get(pa)
    h_b = cache.get(pb)
    assert len(cache) == 2

    cache.clear()
    assert len(cache) == 0
    assert h_a.closed is True
    assert h_b.closed is True

    # Subsequent ``get`` re-opens (fresh instance).
    h_a_new = cache.get(pa)
    assert h_a_new is not h_a
    assert _StubParquetFile.instances_created == 3


def test_max_handles_validation() -> None:
    """Constructor rejects ``max_handles < 1``."""
    with pytest.raises(ValueError, match="max_handles must be >= 1"):
        ParquetHandleCache(max_handles=0)
    with pytest.raises(ValueError, match="max_handles must be >= 1"):
        ParquetHandleCache(max_handles=-3)


def test_get_manifest_memoization() -> None:
    """``get_manifest`` calls the loader exactly once across repeated calls."""
    cache = _make_cache(max_handles=6)
    call_count = {"n": 0}

    def _loader():
        call_count["n"] += 1
        return ([{"row": 1}, {"row": 2}], False)

    r1 = cache.get_manifest(_loader)
    r2 = cache.get_manifest(_loader)
    r3 = cache.get_manifest(_loader)

    assert r1 is r2 is r3
    assert call_count["n"] == 1


def test_get_manifest_cleared_by_clear() -> None:
    """``clear()`` resets the manifest slot so a fresh load is triggered."""
    cache = _make_cache(max_handles=6)
    call_count = {"n": 0}

    def _loader():
        call_count["n"] += 1
        return ([{"row": 1}], False)

    cache.get_manifest(_loader)
    assert call_count["n"] == 1

    cache.clear()
    cache.get_manifest(_loader)
    assert call_count["n"] == 2


def test_path_normalization(tmp_path: Path) -> None:
    """Different path representations (relative/absolute/symlinks) of the
    same underlying file resolve to the SAME cache key.
    """
    cache = _make_cache(max_handles=6)
    parquet = tmp_path / "x.parquet"
    parquet.touch()

    h1 = cache.get(parquet)
    h2 = cache.get(Path(str(parquet)))    # equivalent path repr
    assert h1 is h2
    assert _StubParquetFile.instances_created == 1


def test_default_max_handles_is_six() -> None:
    """Default ``max_handles=6`` matches Aria's spec for the 6-month working set."""
    cache = ParquetHandleCache()
    assert cache.max_handles == 6
