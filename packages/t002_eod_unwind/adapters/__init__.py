"""T002 adapters — layer 1 (feed) + layer 5 (execution), pluggable.

Feed adapters (identical load_trades contract):
  - feed_timescale  — live Sentinel TimescaleDB (slow path)
  - feed_parquet    — canonical parquet manifest (data/manifest.csv)
  - feed_cache      — pre-cache layer (ADR-4, data/cache/cache-manifest.csv)
"""

from . import feed_cache, feed_parquet, feed_timescale  # noqa: F401

