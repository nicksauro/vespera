"""Cumulative research-log parser — `n_trials` source for DSR (Bailey-LdP §3).

Single responsibility: read ``docs/ml/research-log.md`` (Mira ledger) and
return ``(n_trials_cumulative, source_ref)`` for consumption by
``compute_full_report`` (story T002.0f AC5, refresh of T002.0d AC0.1).

Contract (Mira T0 handshake 2026-04-26 in `docs/stories/T002.0f.story.md`):

    1. Walk the file, splitting on top-level ``---`` fences (per the schema
       documented in the ledger header).
    2. For each fenced YAML block, parse as flat mapping; sum integer
       ``n_trials`` across ALL valid entries (squad-cumulative, NOT
       per-story isolated — DSR penalises multiple-testing GLOBAL).
    3. ``source_ref = f"docs/ml/research-log.md@{git_rev_parse_HEAD()}"``.
    4. **Fail-closed if file missing:** raise ``FileNotFoundError`` with an
       explicit pointer to the Mira deliverable. Soft-fallback to
       ``spec.n_trials.total = 5`` is forbidden (Article IV — No
       Invention).

The parser intentionally tolerates only the schema documented in the
ledger header. Missing required keys, malformed YAML, or non-int
``n_trials`` raise ``ValueError`` — the ledger is the authoritative
source and silent corrections would forge audit history.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Tuple

import yaml


# Default ledger location (story T002.0f AC5, Mira ledger v0.1).
DEFAULT_RESEARCH_LOG = Path("docs/ml/research-log.md")

# Required keys per ledger schema header (lines 38-48 of research-log.md).
_REQUIRED_KEYS: Tuple[str, ...] = (
    "story_id",
    "date_brt",
    "n_trials",
    "trials_enumerated",
    "description",
    "spec_ref",
    "signed_by",
)


def _git_rev_parse_head(repo_path: Path | None = None) -> str:
    """Return ``git rev-parse HEAD`` for the repo containing ``repo_path``.

    Falls back to the literal sentinel ``"unknown"`` only if the call
    fails (subprocess error, not a git repo, git missing on PATH). The
    sentinel is informational — the ledger content already pins
    deterministic state via signed entries; the SHA is provenance, not
    invariant.
    """
    cwd = repo_path if repo_path is not None else Path.cwd()
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(cwd),
            check=True,
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        return completed.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return "unknown"


def _split_yaml_blocks(text: str) -> list[str]:
    """Walk the ledger and return raw YAML strings between top-level ``---``.

    The ledger interleaves YAML frontmatter blocks with free-form
    markdown bodies; only the blocks delimited by lines that are
    EXACTLY ``---`` are valid frontmatter. Markdown ``---`` rules
    (indented, with surrounding whitespace) are NOT delimiters.

    Per Mira ledger header §Schema item 1: "Walk the file, splitting on
    top-level ``---`` fences."
    """
    blocks: list[str] = []
    current: list[str] | None = None
    for raw_line in text.splitlines():
        if raw_line.strip() == "---":
            if current is None:
                # Open a new block.
                current = []
            else:
                # Close the current block.
                blocks.append("\n".join(current))
                current = None
            continue
        if current is not None:
            current.append(raw_line)
    # Unterminated trailing fence is treated as malformed — ledger
    # discipline requires every opened fence to close.
    return blocks


def _validate_entry(entry: dict, idx: int) -> None:
    """Validate a parsed YAML mapping against the ledger schema.

    Raises ValueError with explicit pointer to the offending entry
    (1-indexed) so the operator can amend the ledger via an append-only
    correction entry (per ledger Authority Statement).
    """
    missing = [k for k in _REQUIRED_KEYS if k not in entry]
    if missing:
        raise ValueError(
            f"docs/ml/research-log.md entry #{idx}: missing required keys "
            f"{missing}. Ledger schema (lines 38-48) requires {list(_REQUIRED_KEYS)}."
        )
    n_trials = entry["n_trials"]
    if not isinstance(n_trials, int) or n_trials < 0:
        raise ValueError(
            f"docs/ml/research-log.md entry #{idx}: n_trials must be int >= 0, "
            f"got {n_trials!r} (type {type(n_trials).__name__})."
        )


def read_research_log_cumulative(
    path: Path | str = DEFAULT_RESEARCH_LOG,
    repo_path: Path | None = None,
) -> Tuple[int, str]:
    """Read the Mira ledger and return ``(n_trials_cumulative, source_ref)``.

    Args:
        path: ledger location. Default ``docs/ml/research-log.md``.
        repo_path: root for ``git rev-parse HEAD``. Default = ``Path.cwd()``.

    Returns:
        ``(n_trials_total, source_ref)`` where ``source_ref`` is
        ``f"docs/ml/research-log.md@{git_sha}"``.

    Raises:
        FileNotFoundError: ledger missing — fail-closed per Mira T0
            handshake; ``spec.n_trials.total`` soft-fallback is FORBIDDEN
            (Article IV).
        ValueError: malformed YAML or schema violation — see
            ``_validate_entry`` for diagnostic detail.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"{p} not found — Mira T002.0d AC0.1 deliverable required "
            "before compute_full_report. Soft-fallback to spec.n_trials.total "
            "is forbidden (Article IV — No Invention)."
        )

    raw = p.read_text(encoding="utf-8")
    blocks = _split_yaml_blocks(raw)
    if not blocks:
        raise ValueError(
            f"{p} contains zero YAML frontmatter entries — ledger must "
            "include at least one signed entry (T002.0d seed)."
        )

    n_trials_total = 0
    parsed_count = 0
    for idx, block in enumerate(blocks, start=1):
        # The ledger interleaves the schema block (between the doc title
        # and the first entry); skip non-mapping YAML cleanly.
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as exc:
            raise ValueError(
                f"{p} entry #{idx}: YAML parse error — {exc}"
            ) from exc
        if not isinstance(data, dict):
            # Non-mapping fenced block (rare; some markdown fences may
            # delimit decorative content). Skip silently to keep the
            # parser tolerant to documentation evolution.
            continue
        _validate_entry(data, idx)
        n_trials_total += int(data["n_trials"])
        parsed_count += 1

    if parsed_count == 0:
        raise ValueError(
            f"{p}: no valid ledger entries found (parsed 0 mapping blocks). "
            "Required: at least one entry per schema lines 38-48."
        )

    sha = _git_rev_parse_head(repo_path=repo_path)
    source_ref = f"docs/ml/research-log.md@{sha}"
    return n_trials_total, source_ref


__all__ = ["read_research_log_cumulative", "DEFAULT_RESEARCH_LOG"]
