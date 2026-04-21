"""Ensure project root is on sys.path for pytest so absolute imports
(`from packages.t002_eod_unwind...`) work without an installed package.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
