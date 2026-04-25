"""Arithmetic-invariant tests for `core.memory_budget` v3 constants.

Story: T002.0a (#103) — Dex v3 patch of ADR-1 v3 + Riven Co-sign v3.
Spec authority: docs/architecture/memory-budget.md §ADR-1 v3 (lines 982–1326).
QA gate: docs/qa/gates/ADR-1-v3-audit.md (Quinn PASS 7/7, 2026-04-23).
Empirical anchor: data/baseline-run/quiesce-mid.json (RA-20260424-1).
Literature anchor: Gregg, Systems Performance 2nd ed. §7.5.

Assertions enumerated by Aria v3 Handoff (memory-budget.md lines 1293–1300):
  1. CAP_ABSOLUTE == 8_400_052_224
  2. OS_HEADROOM == 1_073_741_824
  3. CAP_ABSOLUTE + OS_HEADROOM == 9_473_794_048
  4. OBSERVED_QUIESCE_FLOOR_AVAILABLE == 9_473_794_048

Plus v3-derived invariants: portability formula soundness, preserved v2 anchors,
and E7 drift-threshold arithmetic.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from core import memory_budget  # noqa: E402


# --- Aria v3 Handoff enumerated assertions ---------------------------------


def test_cap_absolute_v3_literal() -> None:
    """Aria v3 Handoff assertion #1: CAP_ABSOLUTE == 8_400_052_224."""
    assert memory_budget.CAP_ABSOLUTE == 8_400_052_224


def test_os_headroom_v3_literal() -> None:
    """Aria v3 Handoff assertion #2: OS_HEADROOM == 1_073_741_824 (1 GiB binary)."""
    assert memory_budget.OS_HEADROOM == 1_073_741_824
    assert memory_budget.OS_HEADROOM == 1 << 30  # 1 GiB binary cross-check


def test_cap_plus_headroom_equals_observed_floor() -> None:
    """Aria v3 Handoff assertion #3: CAP_ABSOLUTE + OS_HEADROOM == 9_473_794_048.

    This is the v3 R4 threshold — reachable on this host by construction since it
    equals the observed quiesce floor (see Check 5 "R4 reachability" in QA gate).
    """
    assert memory_budget.CAP_ABSOLUTE + memory_budget.OS_HEADROOM == 9_473_794_048


def test_observed_quiesce_floor_literal() -> None:
    """Aria v3 Handoff assertion #4: OBSERVED_QUIESCE_FLOOR_AVAILABLE == 9_473_794_048.

    Direct reading from data/baseline-run/quiesce-mid.json line 4 (Gage, RA-20260424-1,
    captured 2026-04-23T19:21:51-03:00).
    """
    assert memory_budget.OBSERVED_QUIESCE_FLOOR_AVAILABLE == 9_473_794_048


# --- Portability formula soundness (Aria v3 Derivation) --------------------


def test_portability_formula_selects_floor_anchor_on_this_host() -> None:
    """ADR-1 v3 portability formula: CAP = min(floor − headroom, 0.60 × RAM).

    On this 16 GiB host, the observed-floor anchor is tighter and dominates.
    Cross-check Quinn Check 6 table (16 GiB row): floor-dominated at 8.40 GiB.
    """
    floor_anchor = memory_budget.OBSERVED_QUIESCE_FLOOR_AVAILABLE - memory_budget.OS_HEADROOM
    ram_pct_anchor = math.floor(0.60 * memory_budget.PHYSICAL_RAM_BYTES)
    assert floor_anchor == 8_400_052_224
    assert ram_pct_anchor == 10_285_835_059  # v2 CAP preserved as RAM-pct anchor
    assert min(floor_anchor, ram_pct_anchor) == memory_budget.CAP_ABSOLUTE
    # Floor anchor dominates (tighter) on this host
    assert floor_anchor < ram_pct_anchor


def test_v3_cap_is_tighter_than_v2() -> None:
    """ADR-1 v3 tightens CAP_ABSOLUTE by 1.76 GiB (= 1_885_782_835 bytes)
    relative to v2 (`0.60 × PHYSICAL_RAM_BYTES = 10_285_835_059`).

    This is a deliberate strengthening per Quinn Check 5 (fail-closed preservation).
    """
    v2_cap = 10_285_835_059
    delta = v2_cap - memory_budget.CAP_ABSOLUTE
    assert delta == 1_885_782_835
    assert memory_budget.CAP_ABSOLUTE < v2_cap


# --- Preserved v2 constants (Aria v3 Handoff MUST-NOT list) ----------------


def test_headroom_factor_preserved_from_v2() -> None:
    """ADR-1 v3 preserves HEADROOM_FACTOR = 1.3 (Aria v3 Handoff MUST-NOT list)."""
    assert memory_budget.HEADROOM_FACTOR == 1.3


def test_warn_kill_fractions_preserved_from_v2() -> None:
    """ADR-1 v3 preserves WARN/KILL fractions unchanged — only applied to new CAP."""
    assert memory_budget.WARN_FRACTION == 0.85
    assert memory_budget.KILL_FRACTION == 0.95


def test_warn_threshold_v3_bytes() -> None:
    """WARN threshold v3 = 0.85 × CAP_ABSOLUTE = 7_140_044_390.4 (truncates to int).

    Cross-check Quinn Check 2 arithmetic: "0.85 × 8_400_052_224 = 7,140,044,390.4 bytes".
    """
    warn_bytes = memory_budget.WARN_FRACTION * memory_budget.CAP_ABSOLUTE
    assert int(warn_bytes) == 7_140_044_390


def test_kill_threshold_v3_bytes() -> None:
    """KILL threshold v3 = 0.95 × CAP_ABSOLUTE = 7_980_049_612.8 (truncates to int).

    Cross-check Quinn Check 2 arithmetic: "0.95 × 8_400_052_224 = 7,980,049,612.8 bytes".
    """
    kill_bytes = memory_budget.KILL_FRACTION * memory_budget.CAP_ABSOLUTE
    assert int(kill_bytes) == 7_980_049_612


def test_physical_ram_unchanged_from_v2() -> None:
    """PHYSICAL_RAM_BYTES is a host-preflight artifact, unchanged across v2 → v3."""
    assert memory_budget.PHYSICAL_RAM_BYTES == 17_143_058_432


# --- Measure-first compatibility (Check 4) ---------------------------------


def test_ceiling_bytes_populated_per_ra_28_1_decision_3() -> None:
    """ADR-1 v3 §Next-steps step-7: CEILING_BYTES populated per RA-20260428-1 Decision 3.

    RA-20260428-1 Decision 3 SUCCESS at 2026-04-24T18:45:45 BRT consumed the
    one-shot clock; Q6d disposition (RA-28-1 Decision 6) mandated derivation
    from child-self-reported `peak_pagefile_aug2024` (kernel-monotonic,
    authoritative) rather than parent-polled `peak_commit_bytes` (sub-Nyquist
    under 150s runtime).

    Derivation (ADR-1 v3 §Next-steps step 5):
        CEILING_BYTES = min(ceil(peak_pagefile_aug2024 × 1.3), CAP_ABSOLUTE)

    Values:
        peak_pagefile_aug2024 = 473_739_264 bytes (child self-reported exit)
        ceil(473_739_264 × 1.3) = 615_861_044
        min(615_861_044, 8_400_052_224) = 615_861_044  ← CEILING_BYTES
    """
    import math

    peak_pagefile_aug2024 = 473_739_264
    computed = min(
        math.ceil(peak_pagefile_aug2024 * 1.3),
        memory_budget.CAP_ABSOLUTE,
    )
    assert computed == 615_861_044
    assert memory_budget.CEILING_BYTES == 615_861_044
    assert memory_budget.CEILING_BYTES == computed
    assert memory_budget.CEILING_DERIVATION_REF is not None
    assert "RA-20260428-1 Decision 3" in memory_budget.CEILING_DERIVATION_REF
    assert "peak_pagefile=473739264" in memory_budget.CEILING_DERIVATION_REF
    assert "telemetry_commit=80805ac5" in memory_budget.CEILING_DERIVATION_REF


# --- E7 drift threshold (ADR-1 v3 new escalation) --------------------------


def test_e7_drift_threshold_is_ten_percent_of_observed_floor() -> None:
    """Riven v3 §Handoff 5 introduces E7: re-derivation trigger at >10% drift of
    OBSERVED_QUIESCE_FLOOR_AVAILABLE. 10% of 9_473_794_048 ≈ 947,379,404 bytes
    (≈ one OS_HEADROOM unit; cross-check Quinn Check 1 anchor-trace row E7).
    """
    ten_pct = int(0.10 * memory_budget.OBSERVED_QUIESCE_FLOOR_AVAILABLE)
    assert ten_pct == 947_379_404
    # Drift threshold is approximately one OS_HEADROOM unit (within 15%)
    assert abs(ten_pct - memory_budget.OS_HEADROOM) / memory_budget.OS_HEADROOM < 0.15


# --- Vestigial constant removal (Quinn Finding 2) --------------------------


def test_launch_available_multiplier_removed() -> None:
    """ADR-1 v3 additive formula has no role for the v2 multiplier constant.

    Per Quinn ADR-1-v3 audit Finding 2 default recommendation (delete), the
    vestigial `LAUNCH_AVAILABLE_MULTIPLIER` is removed in v3. This guards
    against accidental re-introduction.
    """
    assert not hasattr(memory_budget, "LAUNCH_AVAILABLE_MULTIPLIER")


# --- Audit-trail references ------------------------------------------------


def test_adr_ref_points_to_v3() -> None:
    """ADR_REF string must reference v3 (audit trail hygiene)."""
    assert "v3" in memory_budget.ADR_REF
    assert "memory-budget.md" in memory_budget.ADR_REF


def test_quiesce_floor_ref_points_to_empirical_anchor() -> None:
    """QUIESCE_FLOOR_REF string must reference the empirical source file."""
    assert memory_budget.QUIESCE_FLOOR_REF == "data/baseline-run/quiesce-mid.json"
