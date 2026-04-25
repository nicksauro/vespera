"""Hold-out lock — fail-closed guard on pre-registered CPCV hold-out window.

Story:  T002.0a (initial) — reused by T002.0b/0c.
Spec:   docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml L93-94
Epic:   EPIC-T002.0 §7.1
Rules:  R1 (hold-out virgin) + R15(d) (manifest append-only, non-retroactive)

Invariant
---------
Any read of a trades timestamp in ``[2025-07-01, 2026-04-21]`` requires
``VESPERA_UNLOCK_HOLDOUT=1`` in the environment. Absent that flag, the
materializer / adapter / CPCV loader MUST raise ``HoldoutLockError`` BEFORE
any database connection is opened (prevents accidental side-effects in case
of retry logic reconnecting past the guard).

The check happens in user-space (Python) because the DB role is read-only
anyway — the purpose here is to make preregistration-honoring explicit and
auditable via grep over the codebase (R15 append-only: every call-site is
visible).

BRT-naive datetime invariant (R2): all inputs and bounds are naive
``datetime.date`` / ``datetime.datetime`` objects. No ``tz_convert``, no
``pytz.UTC``, no ``datetime.utcnow()``. If you need "now", use
``datetime.now()`` (local system clock — assumed BRT on the materializer
host).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime


# Pre-registered hold-out bounds (spec v0.2.0 L93-94, PRR-20260421-1).
# These are HARDCODED — not read from spec.yaml — so that a spec edit cannot
# silently re-shape the gate. If the spec changes, this module MUST be
# updated via a reviewed PR (R15 append-only trail).
HOLDOUT_START: date = date(2025, 7, 1)
HOLDOUT_END_INCLUSIVE: date = date(2026, 4, 21)

UNLOCK_ENV_VAR: str = "VESPERA_UNLOCK_HOLDOUT"
UNLOCK_VALUE: str = "1"


class HoldoutLockError(RuntimeError):
    """Raised when a materialization window intersects the hold-out bounds.

    The default message is deliberately explicit about the remedy (set the
    env flag with a justification) so operators reading a traceback in CI
    understand immediately that this is a policy gate, not a bug.
    """


@dataclass(frozen=True)
class _Window:
    start: date
    end_inclusive: date


def _coerce_date(value: date | datetime | str) -> date:
    """Accept date, datetime (BRT-naive), or ISO-8601 string.

    Rejects anything timezone-aware (R2). ISO strings must be of the form
    ``YYYY-MM-DD`` or ``YYYY-MM-DDTHH:MM:SS`` (no offset suffix).
    """
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            raise ValueError(
                "Hold-out lock received a timezone-aware datetime; R2 "
                "requires BRT-naive (tzinfo=None)."
            )
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        # fromisoformat preserves naive-ness; any trailing offset makes it aware
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            raise ValueError(
                f"Hold-out lock received tz-aware ISO string '{value}'; "
                "R2 requires BRT-naive."
            )
        return parsed.date()
    raise TypeError(f"Unsupported date type: {type(value).__name__}")


def _intersects_holdout(start: date, end_inclusive: date) -> bool:
    """True iff [start, end_inclusive] overlaps the hold-out window."""
    # Two closed intervals [a,b] and [c,d] overlap iff a <= d AND c <= b.
    return start <= HOLDOUT_END_INCLUSIVE and HOLDOUT_START <= end_inclusive


def is_unlock_enabled(env: dict[str, str] | None = None) -> bool:
    """Return True iff ``VESPERA_UNLOCK_HOLDOUT=1`` is set.

    ``env`` is injectable for testability. Defaults to ``os.environ``.
    """
    source = env if env is not None else os.environ
    return source.get(UNLOCK_ENV_VAR, "0") == UNLOCK_VALUE


def assert_holdout_safe(
    start: date | datetime | str,
    end_inclusive: date | datetime | str,
    *,
    env: dict[str, str] | None = None,
) -> None:
    """Raise ``HoldoutLockError`` if window intersects hold-out and flag not set.

    Must be called BEFORE any DB connection is opened. Idempotent —
    returns ``None`` on success.

    Parameters
    ----------
    start, end_inclusive:
        Window bounds. ``end_inclusive`` means the window includes the last
        day — matches how ``--end-date`` is interpreted by operators.
    env:
        Optional environment override for testing. Defaults to ``os.environ``.
    """
    s = _coerce_date(start)
    e = _coerce_date(end_inclusive)
    if s > e:
        raise ValueError(f"Invalid window: start={s} > end_inclusive={e}")

    if not _intersects_holdout(s, e):
        return  # fully outside hold-out — always allowed

    if is_unlock_enabled(env=env):
        return  # explicit unlock with operator intent

    raise HoldoutLockError(
        f"window [{s.isoformat()}, {e.isoformat()}] intersects preregistered "
        f"hold-out [{HOLDOUT_START.isoformat()}, {HOLDOUT_END_INCLUSIVE.isoformat()}]; "
        f"set {UNLOCK_ENV_VAR}=1 and provide justification"
    )


__all__ = [
    "HOLDOUT_START",
    "HOLDOUT_END_INCLUSIVE",
    "UNLOCK_ENV_VAR",
    "HoldoutLockError",
    "assert_holdout_safe",
    "is_unlock_enabled",
]
