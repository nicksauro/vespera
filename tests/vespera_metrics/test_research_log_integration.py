"""Integration test — production research-log.md ledger (ESC-007 canary).

Coverage gap context (Beckett report §11):

    Pre-ESC-007 ALL parser tests in ``test_compute_full_report.py`` consumed
    fixture STRINGS or ``_write_research_log``-emitted mock files. NONE
    exercised ``docs/ml/research-log.md`` (the production Mira ledger) loaded
    from disk via ``read_research_log_cumulative``. That coverage gap is what
    allowed the ``_split_yaml_blocks`` toggle-walker inversion (ESC-007) to
    ship undetected through Quinn T5 PASS — the bug only surfaced at Beckett
    T11.bis #2 exit gate (commit 243bcad), when the harness first attempted
    to read the real ledger end-to-end.

This module installs a single canary integration test that:

    1. Loads the REAL ``docs/ml/research-log.md`` from disk (path resolved
       robustly via ``__file__`` to survive worktree / CI checkout layouts).
    2. Invokes ``read_research_log_cumulative`` against that real file.
    3. Asserts ``n_trials_cumulative == 5`` (T002.0d=5 + T002.0f=0 per the
       Mira ledger v0.1 currently committed).
    4. Asserts ``source_ref`` follows the documented
       ``docs/ml/research-log.md@<sha>`` shape.

The assertion on the cumulative count acts as a canary: any future
incompatible change to the ledger format (e.g. a parser regression that
re-introduces the toggle-walker class of bug, or a Mira ledger schema
breaking change without contemporaneous parser update) trips this test
at unit-test CI time — no longer waiting for the Beckett T11.bis exit
gate to expose it.

References:

    - ESC-007 (USER-ESCALATION-QUEUE.md:267) — root-cause analysis of the
      ``_split_yaml_blocks`` toggle inversion.
    - Dex commit ea491f6 — parser fix (consecutive-fence-pair walker +
      content marker classifier).
    - Quinn T5 prior gate (commit 243bcad) — gap-revealing handoff.

Authority: QA-only; this test does NOT modify the ledger (Mira sole
authority) nor the parser (Dex authority). Article IV — No Invention.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from packages.vespera_metrics.research_log import read_research_log_cumulative


# Robust path resolution: this file is at
#   <repo>/tests/vespera_metrics/test_research_log_integration.py
# Production ledger lives at
#   <repo>/docs/ml/research-log.md
# Walking three parents from __file__ lands on the repo root regardless of
# CI checkout dir / worktree path / drive letter on Windows. Avoids any
# brittle CWD assumption.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PRODUCTION_LEDGER = _REPO_ROOT / "docs" / "ml" / "research-log.md"

# Current canonical squad-cumulative count per the v0.1 ledger:
#   - T002.0d entry: n_trials = 5
#   - T002.0f entry: n_trials = 0  (harness integration; no new trials)
#   Sum (Bailey-LdP §3 squad-wide): 5
# This constant is intentionally NOT pinned to a sha — the test contracts
# on the count + the source_ref shape only. If the ledger legitimately
# grows (Mira appends a new entry with n_trials > 0), THIS constant must
# be bumped in lockstep with the ledger update PR (intentional friction;
# any silent count drift is exactly the regression class this test
# guards against).
_EXPECTED_N_TRIALS_CUMULATIVE = 5


@pytest.mark.integration
def test_production_research_log_ledger_loads_and_sums_to_canonical_count() -> None:
    """ESC-007 canary — load real ``docs/ml/research-log.md`` from disk
    and assert ``n_trials_cumulative == 5``.

    This is the FIRST test in the suite that exercises the production
    ledger path end-to-end. All prior parser tests use fixture strings
    via ``_write_research_log`` — coverage gap that ESC-007 exploited.

    A failure here means EITHER:

        (a) ``_split_yaml_blocks`` (or any downstream parser code) has
            regressed against the production ledger format — most likely
            re-introducing the toggle-walker class of bug fixed by Dex
            commit ea491f6.
        (b) The Mira ledger has changed (new entry appended) WITHOUT a
            paired bump of ``_EXPECTED_N_TRIALS_CUMULATIVE`` here. In
            this case the failing diff is the canary signal that the
            governance contract (paired ledger + counter update) was
            skipped — investigate the most recent ledger PR.

    NEVER mock — the explicit purpose of this canary is to load the
    ledger production file from disk, byte-for-byte as committed.
    """
    # Sanity: production ledger MUST exist at the canonical path. If this
    # fails, the worktree is malformed (or someone deleted Mira's ledger).
    assert _PRODUCTION_LEDGER.exists(), (
        f"Production research-log.md missing at {_PRODUCTION_LEDGER}. "
        "This is a worktree integrity violation — the Mira ledger is "
        "tracked in git and MUST be present for the harness to run."
    )

    n_trials_cumulative, source_ref = read_research_log_cumulative(
        path=_PRODUCTION_LEDGER,
        repo_path=_REPO_ROOT,
    )

    # Primary canary assertion — squad-cumulative count.
    assert n_trials_cumulative == _EXPECTED_N_TRIALS_CUMULATIVE, (
        f"Production ledger n_trials_cumulative drift detected: "
        f"got {n_trials_cumulative}, expected {_EXPECTED_N_TRIALS_CUMULATIVE}. "
        "EITHER the parser has regressed against the ledger format (re-check "
        "_split_yaml_blocks vs ESC-007 fix commit ea491f6) OR the Mira "
        "ledger was appended without a paired bump of "
        "_EXPECTED_N_TRIALS_CUMULATIVE in this test (governance break)."
    )

    # Secondary canary — source_ref shape contract consumers depend on.
    assert source_ref.startswith("docs/ml/research-log.md@"), (
        f"source_ref shape contract broken: got {source_ref!r}; "
        "expected prefix 'docs/ml/research-log.md@<sha>' per Mira T0 "
        "handshake L301."
    )
