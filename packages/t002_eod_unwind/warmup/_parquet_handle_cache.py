"""ParquetHandleCache — orchestrator-internal LRU cache for ``pyarrow.parquet.ParquetFile``.

Story: ``docs/stories/T002.0h.story.md`` (AC8 amendment 2026-04-26 BRT —
Option C cached file handles for wall-time mitigation).

Authority (mini-council 4-vote convergent — Aria + Mira + Riven + Beckett,
2026-04-26 BRT):

- **Aria (architecture)** — Orchestrator-internal sibling utility (NOT
  adapter modification — Guard #4 + R15 immutability of T002.0b adapter).
  Pure-compute LRU wrapper; no I/O policy changes; backward-compat with
  uncached path.
- **Mira (anti-leak)** — NEUTRAL. Cache does NOT alter iteration order,
  does NOT alter window predicate, does NOT change per-day `load_trades`
  semantics. Memory-only optimization; shifted-by-1 invariant preserved.
- **Riven (defense-in-depth)** — Cache size bounded by ``max_handles``
  (default 6 — covers a typical 6-month working set). Explicit ``clear()``
  for resource release. NO silent path divergence; sha256 integrity
  remains adapter-managed (``_INTEGRITY_CACHE`` in feed_parquet).
- **Beckett (R6 CPCV gate)** — Wall-time recovery. Per-day adapter
  pattern (T002.0h AC2) issued ~110 ParquetFile opens for one as_of
  warmup; each open re-reads parquet metadata (~3s on the local hardware).
  Cache amortizes opens 6:1 (110 calls → ~6 distinct monthly files for a
  146bd lookback) → projected wall-time < 60s (Beckett amended budget).

T002.0h Anti-Article-IV Guards (preserved):

1. NO timeout extend — fix is to amortize opens, NOT to widen the budget.
2. NO CAP_v3 raise — cache adds bounded ParquetFile metadata only
   (~MB-scale per handle, well within ADR-1 v3 8.4 GiB CAP_v3).
3. NO subsample dataset — cache is transparent; output bytes IDENTICAL.
4. NO builder API mutation — cache lives in ``warmup/`` (orchestrator
   sibling), NOT in the builder modules.
5. NO ascending-iteration skip — cache is order-agnostic; orchestrator
   still iterates D-1 strictly before D (preserved at orchestrator.py
   anti-leak runtime assertion).

Non-goals:

- NOT thread-safe (orchestrator is single-threaded by design).
- NOT a replacement for ``_INTEGRITY_CACHE`` in feed_parquet (sha256
  verification remains adapter-internal — Guard #4 immutability of
  T002.0b adapter contract).
"""

from __future__ import annotations

import logging
from collections import OrderedDict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ParquetHandleCache:
    """Bounded-size LRU cache for ``pyarrow.parquet.ParquetFile`` handles.

    Lifecycle:

      handle = cache.get(path)        # opens on miss, returns cached on hit
      ...                              # caller uses handle (read row groups, ...)
      cache.clear()                    # explicit release (best-effort GC)

    The cache key is the absolute resolved path; values are
    ``pyarrow.parquet.ParquetFile`` instances. On overflow the LEAST
    recently used handle is evicted (popped + dropped — Python GC
    finalizes the underlying file descriptor).

    Default ``max_handles=6`` covers the typical 6-month working set
    (one monthly parquet file per month of warmup lookback) — empirically
    a 146-business-day lookback spans 6-7 monthly partitions.

    Anti-Article-IV Guard #2 (T002.0h): bounded memory — at most
    ``max_handles`` ParquetFile metadata footprints (~MB-scale each).
    """

    def __init__(self, max_handles: int = 6) -> None:
        if max_handles < 1:
            raise ValueError(
                f"max_handles must be >= 1; got {max_handles}"
            )
        self._max_handles = int(max_handles)
        # OrderedDict preserves insertion order; ``move_to_end`` on access
        # turns it into a textbook LRU.
        self._handles: OrderedDict[Path, Any] = OrderedDict()
        self._hits = 0
        self._misses = 0
        # Companion manifest cache — single-slot memoization for the
        # adapter's ``_load_manifest_with_fallback`` result. Beckett
        # wall-time diagnostic step #1: 110 per-day adapter calls each
        # re-parse ``data/manifest.csv`` (+ PREVIEW). Memoizing here
        # collapses that to a single parse per orchestrator run while
        # remaining transparent to the adapter (the FeedParquetSource
        # wrapper installs a temporary cached loader during its yield
        # generator's lifetime).
        self._manifest_cached: Any | None = None
        # Real opener — captured at cache-construction time BEFORE the
        # adapter's ``pq.ParquetFile`` symbol is monkey-patched. Without
        # this capture, ``self._open_parquet`` would recurse into the
        # patched constructor (since the orchestrator patches
        # ``pyarrow.parquet.ParquetFile`` to a shim that calls
        # ``cache.get`` → ``cache._open_parquet`` → patched constructor →
        # infinite recursion). Tests override ``_open_parquet`` directly
        # via attribute assignment and never trigger this path.
        self._real_opener: Any | None = None

    @property
    def max_handles(self) -> int:
        return self._max_handles

    @property
    def hits(self) -> int:
        return self._hits

    @property
    def misses(self) -> int:
        return self._misses

    def __len__(self) -> int:
        return len(self._handles)

    def get(self, path: Path) -> Any:
        """Return a ``ParquetFile`` for ``path``; opens on miss.

        Idempotent w.r.t. path identity — repeated calls with the same
        ``path`` (same ``Path.resolve()`` value) return the same handle
        instance until evicted. Evicted handles are dropped (Python GC
        closes the underlying mmap).
        """
        key = Path(path).resolve()
        if key in self._handles:
            self._handles.move_to_end(key)
            self._hits += 1
            return self._handles[key]
        # Miss — open a fresh ParquetFile.
        # Lazy import keeps test fixtures free of pyarrow when the cache
        # is exercised with a mock factory (see _open_parquet override
        # hook below for unit tests).
        handle = self._open_parquet(key)
        self._handles[key] = handle
        self._misses += 1
        # Evict LRU if over capacity.
        while len(self._handles) > self._max_handles:
            evicted_key, evicted_handle = self._handles.popitem(last=False)
            # Best-effort close — pyarrow.ParquetFile holds a file
            # descriptor that benefits from prompt release on Windows.
            self._best_effort_close(evicted_handle)
            logger.debug(
                "ParquetHandleCache evicted LRU handle: %s", evicted_key
            )
        return handle

    def clear(self) -> None:
        """Drop all cached handles (best-effort close each).

        Also resets the companion manifest cache slot so a subsequent
        run picks up fresh manifest contents.
        """
        for _, handle in self._handles.items():
            self._best_effort_close(handle)
        self._handles.clear()
        self._manifest_cached = None

    # ------------------------------------------------------------------
    # Companion manifest memoization (single-slot, callsite-scoped)
    # ------------------------------------------------------------------
    def get_manifest(self, loader: Any) -> Any:
        """Return the cached manifest payload, calling ``loader()`` on miss.

        ``loader`` is the adapter's ``_load_manifest_with_fallback`` (a
        zero-arg callable returning ``(rows, used_preview)``). The result
        is memoized on the cache instance so a single orchestrator run
        parses ``data/manifest.csv`` exactly once even across ~110
        per-day ``load_trades`` calls.
        """
        if self._manifest_cached is None:
            self._manifest_cached = loader()
        return self._manifest_cached

    # ------------------------------------------------------------------
    # Hooks (testable)
    # ------------------------------------------------------------------
    def _open_parquet(self, path: Path) -> Any:
        """Default factory — opens a real ``pyarrow.parquet.ParquetFile``.

        Overridable for tests via ``ParquetHandleCache._open_parquet =
        ...`` monkey-patching, OR via subclass. If ``self._real_opener``
        was pre-captured by the orchestrator (BEFORE its module-scope
        monkey-patch of ``pq.ParquetFile``), use it to avoid recursing
        through the patched shim.
        """
        if self._real_opener is not None:
            return self._real_opener(str(path))
        import pyarrow.parquet as pq  # type: ignore[import-untyped]

        return pq.ParquetFile(str(path))

    @staticmethod
    def _best_effort_close(handle: Any) -> None:
        """Close a ``ParquetFile`` if the API exposes a closer; ignore otherwise."""
        # ``pyarrow.parquet.ParquetFile`` does not expose a public
        # ``close`` in every release; if absent, dropping the reference
        # lets Python GC finalize the underlying mmap. We try the common
        # patterns and swallow AttributeError to stay forward-compat.
        for closer_name in ("close", "_close"):
            closer = getattr(handle, closer_name, None)
            if callable(closer):
                try:
                    closer()
                except Exception:  # pragma: no cover - defensive
                    pass
                return


__all__ = ["ParquetHandleCache"]
