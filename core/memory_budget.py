"""
Memory budget constants for T002.0a G09 materialization wrapper.

Derivation authority: docs/architecture/memory-budget.md ADR-1 v3 (observed-floor-anchored).
Custodial co-sign: docs/architecture/memory-budget.md Riven Co-sign v3 (R4 recalibration).
Empirical anchor: data/baseline-run/quiesce-mid.json (RA-20260424-1, Gage 2026-04-23T19:21:51-03:00).
Host-preflight evidence: data/baseline-run/host-preflight.txt (Gage, 2026-04-22T23:13:24-03:00).
Literature anchor (OS_HEADROOM): Gregg, Systems Performance 2nd ed. §7.5 "Methodology".

These literals are hardcoded per Aria Ratification Finding 4 (Option A):
static cap for reproducibility + custodial audit trail; runtime drift check
catches host changes (see `check_host_drift()`).

ADR-1 v3 supersedes narrowly:
- CAP_ABSOLUTE (v2 = 10_285_835_059 = 0.60 × PHYSICAL_RAM) → v3 = 8_400_052_224
  (= OBSERVED_QUIESCE_FLOOR_AVAILABLE − OS_HEADROOM; tighter by 1.76 GiB).
- R4 launch-time formula (v2 = `available ≥ 1.5 × CAP_ABSOLUTE` = 14.37 GiB, unreachable)
  → v3 = `available ≥ CAP_ABSOLUTE + OS_HEADROOM` = 9.47 GiB (= observed floor by construction).

HEADROOM_FACTOR (1.3), WARN_FRACTION (0.85), KILL_FRACTION (0.95) are unchanged.
The v2 `LAUNCH_AVAILABLE_MULTIPLIER` constant was removed by v3 (vestigial — additive
formula no longer uses a multiplier; see Quinn ADR-1-v3 audit Finding 2).

CEILING_BYTES populated at step 7 of remediation plan (RA-20260428-1 Decision 3
SUCCESS at 2026-04-24T18:45:45 BRT). Derivation: ceil(peak_pagefile_aug2024 × 1.3)
with peak_pagefile_aug2024 = 473_739_264 bytes (child self-reported, Q6d
authoritative per RA-28-1 Decision 6). See CEILING_DERIVATION_REF below.
"""
from __future__ import annotations

import psutil

# Host-specs-aware constants (from data/baseline-run/host-preflight.txt)
PHYSICAL_RAM_BYTES: int = 17_143_058_432     # 15.97 GiB, host-preflight §3 (unchanged from v2)

# ADR-1 v3 observed empirical anchor (data/baseline-run/quiesce-mid.json line 4)
# Direct psutil.virtual_memory().available reading under authorized quiesce per RA-20260424-1.
OBSERVED_QUIESCE_FLOOR_AVAILABLE: int = 9_473_794_048   # bytes (~8.82 GiB binary)

# ADR-1 v3 OS headroom above the cap — literature anchor (Gregg §7.5 bounded-workload
# buffer-pool slack upper bound; corroborated by Microsoft Win32 procthread docs
# "leave > 1 GiB for OS + file cache on 16 GiB systems"). Host-invariant.
OS_HEADROOM: int = 1_073_741_824                         # bytes (1.0 GiB)

# ADR-1 v3 CAP_ABSOLUTE derivation (portability formula):
#   CAP_ABSOLUTE_host = min(
#       OBSERVED_QUIESCE_FLOOR_AVAILABLE − OS_HEADROOM,   # observed-floor anchor
#       floor(0.60 × PHYSICAL_RAM_BYTES)                  # RAM-percentage anchor (v2 heritage)
#   )
# On this 16 GiB host: min(9_473_794_048 − 1_073_741_824, 0.60 × 17_143_058_432)
#                    = min(8_400_052_224, 10_285_835_059) = 8_400_052_224 (floor-dominated).
CAP_ABSOLUTE: int = 8_400_052_224            # bytes (~7.82 GiB binary), v3
HEADROOM_FACTOR: float = 1.3                 # ADR-1 v2 + Gregg + Sentinel Aug+45% (preserved v3)
WARN_FRACTION: float = 0.85                  # ADR-1 v2 early-trip WARN (preserved v3)
KILL_FRACTION: float = 0.95                  # ADR-1 v2 early-trip KILL (preserved v3)
DRIFT_TOLERANCE: float = 0.01                # 1% drift tolerance per Finding 4
POLL_SECONDS_DEFAULT: int = 30               # ADR-2
POLL_SECONDS_MIN: int = 10
POLL_SECONDS_MAX: int = 300

# CEILING_BYTES — step-7 populated per RA-20260428-1 Decision 3 SUCCESS at 2026-04-24T18:45:45 BRT.
# Formula (ADR-1 v3 §Next-steps step 5): CEILING_BYTES = min(ceil(peak_pagefile_aug2024 × 1.3), CAP_ABSOLUTE).
# peak_pagefile_aug2024 = 473_739_264 bytes (child self-reported exit telemetry, Q6d authoritative).
# ceil(473_739_264 × 1.3) = 615_861_044;  min(615_861_044, 8_400_052_224) = 615_861_044 (~587.3 MiB, ~0.5735 GiB).
CEILING_BYTES: int | None = 615_861_044
CEILING_DERIVATION_REF: str | None = (
    "RA-20260428-1 Decision 3 | Aug-2024 WDO sentinel-path | "
    "child_self_reported peak_pagefile=473739264 | telemetry_commit=80805ac5 | "
    "audit=data/baseline-run/ra-20260428-1-decision-3-audit.yaml"
)

# References for audit trail
HOST_PREFLIGHT_REF: str = "data/baseline-run/host-preflight.txt"
QUIESCE_FLOOR_REF: str = "data/baseline-run/quiesce-mid.json"
BASELINE_MONTH_REF: str = "Aug-2024"         # ADR-1 v2: worst-observed month (preserved v3)
ADR_REF: str = "docs/architecture/memory-budget.md ADR-1 v3"

# R4 whitelist — processes that cannot be closed by operator
# Riven Ratification Finding 6 (Option A + 2 amendments: registry, memory compression)
# Preserved verbatim by ADR-1 v3 (Aria v3 Handoff "MUST NOT modify _RETAINED_PROCESSES").
_RETAINED_PROCESSES: frozenset[str] = frozenset({
    "msmpeng",            # Windows Defender realtime AV
    "vmmem",              # Hyper-V / WSL2 guest memory
    "com.docker",         # Docker Desktop backend
    "docker desktop",     # Docker Desktop UI
    "claude",             # Dev shell (wrapper may be launched from claude)
    "explorer",           # Windows shell
    "services",           # Windows service controller
    "system",             # Windows system
    "svchost",            # Windows service host instances
    "csrss",              # Client/Server Runtime Subsystem
    "smss",               # Session Manager Subsystem
    "wininit",            # Windows init
    "winlogon",           # Windows logon manager
    "lsass",              # Local Security Authority
    "registry",           # Windows 10+ registry process
    "memory compression", # Windows 10+ memory compression process
})


def is_retained(process_name: str) -> bool:
    """Case-insensitive substring match against R4 whitelist.

    A process name 'counts as retained' if any whitelist token is a substring of
    the process name (lowercased). Used to exclude non-closable processes from
    the top-3 consumers message in launch-time check (R4, exit 1).
    """
    if not process_name:
        return False
    lowered = process_name.lower()
    return any(token in lowered for token in _RETAINED_PROCESSES)


def check_host_drift() -> tuple[bool, str]:
    """Compare live psutil host RAM to hardcoded PHYSICAL_RAM_BYTES.

    Returns (ok, detail). ok=True means drift <= DRIFT_TOLERANCE (1%).
    ok=False means the wrapper should exit 1 with this detail, citing E4
    re-derivation clause (Riven Co-sign v3 preserves v2 E4 verbatim).
    """
    live_total = psutil.virtual_memory().total
    drift = abs(live_total - PHYSICAL_RAM_BYTES) / PHYSICAL_RAM_BYTES
    if drift <= DRIFT_TOLERANCE:
        return True, f"host RAM drift ok: {drift:.4%} (live={live_total}, expected={PHYSICAL_RAM_BYTES})"
    return (
        False,
        f"host RAM drift {drift:.2%} exceeds {DRIFT_TOLERANCE:.0%} tolerance "
        f"(live={live_total}, expected={PHYSICAL_RAM_BYTES}). "
        f"CEILING_BYTES is invalid on this host. "
        f"See {ADR_REF} Riven Co-sign v3 (preserves v2 E4) for re-derivation procedure."
    )
