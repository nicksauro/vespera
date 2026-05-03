"""DLL control retest — 2023-12 with same 5-day window as 2024-01 control.

NOT a Council-binding probe. Symmetric A/B comparison tool only.
Same monkey-patch pattern as dll_control_check_2024_01.py:
  - _HARD_TIMEOUT_S = 60s (avoid 1800s drain hang on NL_ERROR)
  - _OUTPUT_DIR redirected to data/dll-probes/CONTROL-2023-12-5d/
Bypasses R1 hard-rule check (uses run_probe directly, R1 lives in main()).

Symmetry rationale
------------------
A1 official 2023-12 probe used 20-day window, returned NL_ERROR 3x.
2024-01 control used 5-day window, returned NL_OK + trades flow.
Window asymmetry could in principle skew the comparison (though NL_ERROR
is immediate at request time and not size-dependent). This retest closes
that gap with a symmetric 5-day window in 2023-12.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dll_probe_2023_12_wdofut as probe  # noqa: E402

CONTROL_DIR = Path(__file__).resolve().parents[1] / "data" / "dll-probes" / "CONTROL-2023-12-5d"
CONTROL_DIR.mkdir(parents=True, exist_ok=True)

probe._OUTPUT_DIR = CONTROL_DIR
probe._HARD_TIMEOUT_S = 300.0
probe._IDLE_WATCHDOG_S = 60.0


def main() -> int:
    for var in ("DLL_PATH", "DLL_ACTIVATION_KEY", "DLL_USER", "DLL_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: env var {var} not set", file=sys.stderr)
            return 3

    return probe.run_probe(
        start_date="2023-12-04",
        end_date="2023-12-08",
        ticker="WDOFUT",
        dll_path=os.environ["DLL_PATH"],
        activation_key=os.environ["DLL_ACTIVATION_KEY"],
        user=os.environ["DLL_USER"],
        password=os.environ["DLL_PASSWORD"],
    )


if __name__ == "__main__":
    sys.exit(main())
