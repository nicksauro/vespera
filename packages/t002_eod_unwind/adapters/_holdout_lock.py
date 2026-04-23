"""Hold-out lock — thin re-export of the canonical guard in ``scripts/_holdout_lock``.

Story:  T002.0b (T1)
Rule:   Constitution Article IV (No Invention) + DRY. The single source of
        truth for hold-out bounds and fail-closed logic lives in
        ``scripts/_holdout_lock.py``. This module is a re-export so that
        adapter callsites under ``packages.t002_eod_unwind.adapters`` can
        ``from ._holdout_lock import assert_holdout_safe, HoldoutLockError``
        without reaching into ``scripts/``.

Long-term refactor (Aria, 2026-04-22): canonical module should migrate
from ``scripts/`` into ``packages/t002_eod_unwind/`` and ``scripts/`` should
import from the package. Tracked as a future story (T002.Zx refactor). The
thin re-export below is the interim solution — zero logic duplicated.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the repo's ``scripts/`` directory is importable — this package is
# normally imported from an environment where the repo root is on sys.path
# (via conftest.py), but ``scripts/`` is not a package. We add it lazily so
# the import below resolves.
_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _REPO_ROOT / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from _holdout_lock import (  # noqa: E402  (sys.path munging must precede)
    HoldoutLockError,
    assert_holdout_safe,
    is_unlock_enabled,
)

__all__ = ["HoldoutLockError", "assert_holdout_safe", "is_unlock_enabled"]
