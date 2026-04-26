"""Ensure project root is on sys.path for pytest so absolute imports
(`from packages.t002_eod_unwind...`) work without an installed package.

Also registers project-wide pytest markers (so ``-W error::PytestUnknownMarkWarning``
configurations don't fail on first usage).
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def pytest_configure(config):
    """Register custom markers (T002.0h memory regression test uses ``slow``)."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (>10s wall time); deselect with `-m 'not slow'`",
    )
