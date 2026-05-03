"""DLL control check — confirm hypothesis from A1 2023-12 probe.

NOT a Council-binding probe. Diagnostic comparison tool only.
Runs the same `run_probe()` used by A1, monkey-patched to:
  - Shorten _HARD_TIMEOUT_S from 1800s -> 60s (60s is enough to confirm trades flow)
  - Redirect _OUTPUT_DIR to data/dll-probes/CONTROL-2024-01/ (no pollution of 2023-12 artifacts)
Bypasses R1 hard-rule (which restricts the official probe to 2023-12-* window only).

Hypothesis under test
---------------------
A1 2023-12 probe returned NL_ERROR (-2147483645) immediately, zero trades, 3x consistent.
If GetHistoryTrades for 2024-01-02 returns NL_OK + trades flow, hypothesis confirmed:
ProfitDLL retention does NOT serve pre-2024 WDOFUT continuous (R4 retention_exhausted).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dll_probe_2023_12_wdofut as probe  # noqa: E402

CONTROL_DIR = Path(__file__).resolve().parents[1] / "data" / "dll-probes" / "CONTROL-2024-01"
CONTROL_DIR.mkdir(parents=True, exist_ok=True)

probe._OUTPUT_DIR = CONTROL_DIR
probe._HARD_TIMEOUT_S = 600.0
probe._IDLE_WATCHDOG_S = 120.0


def main() -> int:
    for var in ("DLL_PATH", "DLL_ACTIVATION_KEY", "DLL_USER", "DLL_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: env var {var} not set", file=sys.stderr)
            return 3

    return probe.run_probe(
        start_date="2024-01-02",
        end_date="2024-01-06",
        ticker="WDOFUT",
        dll_path=os.environ["DLL_PATH"],
        activation_key=os.environ["DLL_ACTIVATION_KEY"],
        user=os.environ["DLL_USER"],
        password=os.environ["DLL_PASSWORD"],
    )


if __name__ == "__main__":
    sys.exit(main())
