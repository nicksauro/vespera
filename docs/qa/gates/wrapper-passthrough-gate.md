# Wrapper Passthrough Gate — `run_materialize_with_ceiling.py`

**Reviewer:** Quinn (@qa)
**Date:** 2026-04-23
**Binding specs:** MWF-20260422-1 (manifest-write-flag-spec.md) · ADR-1 v2 / ADR-3 / RA-20260423-1 (memory-budget.md)
**Artifacts reviewed:**
- `scripts/run_materialize_with_ceiling.py` (215 lines, +48 from 174 baseline)
- `tests/core/test_run_with_ceiling.py` (571 lines, 40 tests total, +5 wrapper tests)
- Child reference: `scripts/materialize_parquet.py` (--help introspected)

**Context chain:** MWF-20260422-1 → Dex impl → Gage halt #1 → Dex venv + materialize impl → Quinn gate PASS → Gage halt #2 (R4) → Riven RA-20260423-1 → Gage halt #3 (wrapper passthrough missing) → **Dex wrapper patch (THIS REVIEW)**.

---

## 7-Check Table

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Flag surface correctness | PASS | `scripts/run_materialize_with_ceiling.py` L101-110 (`--output-dir`, independent), L113-133 (`add_mutually_exclusive_group()` wraps `--no-manifest` L114-122 and `--manifest-path` L123-132) — true argparse-level mutex, not post-parse validation. Flag names exact-match child at `scripts/materialize_parquet.py --help` (`--output-dir`, `--no-manifest`, `--manifest-path`). |
| 2 | Command assembly correctness | PASS | L163-169 builds `command` as a `list[str]` (not a shell string). L172-177: each flag appended only when operator set it (`if ns.output_dir is not None`, `if ns.no_manifest`, `if ns.manifest_path is not None`); bare `--no-manifest` via `command.append(...)`; path-bearing flags via `command.extend([flag, str(path)])`. `run_with_ceiling(command, ...)` at L188 receives the list; no `shell=True` anywhere (Art. IV: no invented semantics — child defaults preserved when flags unset). |
| 3 | Test coverage (5 new tests) | PASS | `tests/core/test_run_with_ceiling.py` — `test_wrapper_forwards_output_dir` L504-514 asserts flag+value adjacency; `test_wrapper_forwards_no_manifest` L517-526 asserts bare flag and absence of `--manifest-path`; `test_wrapper_forwards_manifest_path` L529-540 asserts flag+value adjacency and absence of `--no-manifest`; `test_wrapper_mutex_no_manifest_and_manifest_path` L543-560 uses `pytest.raises(SystemExit)` and asserts `excinfo.value.code == 2`; `test_wrapper_omits_flags_when_not_set` L563-570 asserts all three absent. |
| 4 | No regression | PASS | `pytest tests/ -q` → **209 passed, 1 skipped** (matches Dex's number). `pytest tests/core/test_run_with_ceiling.py -v` → **40/40 PASS**. `pytest tests/unit/test_materialize_manifest_flag.py -v` → **19/19 PASS** (MWF-20260422-1 unaffected). |
| 5 | Ruff clean | PASS | `ruff check scripts/run_materialize_with_ceiling.py tests/core/test_run_with_ceiling.py` → `All checks passed!` |
| 6 | CLI surface end-to-end | PASS | `--help` renders `[--output-dir OUTPUT_DIR]` and `[--no-manifest \| --manifest-path MANIFEST_PATH]` (pipe denotes argparse mutex group). Live mutex: invoking `--no-manifest --manifest-path X ...` exits **2** with argparse error `argument --manifest-path: not allowed with argument --no-manifest`. Child `materialize_parquet.py --help` confirms same three flag names — exact byte-match for passthrough. |
| 7 | Canonical integrity | PASS | `data/manifest.csv` SHA256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` ✓ matches. `data/in_sample/year=2024/month=08/wdo-2024-08.parquet` SHA256 = `bf7d42f5122710571c7c7e8050dfde6482874dfb31734b05d54c79ba0bb83ce0` ✓ matches. No canonical artifact was touched by this patch. |

---

## Findings

### Blockers
None.

### Concerns
None.

### Informational

- **I-1 (positive):** The wrapper uses argparse's native `add_mutually_exclusive_group()` (L113) which raises the mutex error *during parse* (exit 2 with the canonical argparse message), rather than a hand-rolled post-parse `if a and b: sys.exit(...)`. This is the correct pattern and matches the child's implementation (MWF-20260422-1 §3.1).
- **I-2 (positive):** `--output-dir` is declared independently of the manifest mutex group (L101-110), correctly implementing MWF-20260422-1 §decision 3 ("independent, NOT auto-implied"). Operators can combine `--output-dir X --no-manifest`, `--output-dir X --manifest-path Y`, or `--output-dir X` alone.
- **I-3 (positive):** Passthrough is strictly conditional on operator intent (L172, L174, L176). When a flag is not supplied, the wrapper does NOT forward it, preserving the child's own defaults — this honors Art. IV (No Invention): the wrapper invents no semantics.
- **I-4 (positive):** `command` is assembled as a `list[str]` and passed as such through the call chain; no f-string shell concatenation, no `shell=True`. Injection-safe.
- **I-5 (positive):** The `--output-dir` argparse entry also registers `--out` as an alias (L102). This is backward-compatibility surface area; it is not required by MWF-20260422-1 but matches the child's alias and therefore does no harm.

---

## Verdict

**PASS**

All 7 gate checks pass with zero blockers and zero concerns. The patch correctly exposes `--output-dir`, `--no-manifest`, and `--manifest-path` at the wrapper layer with:
- argparse-native mutex on the manifest pair,
- independent `--output-dir`,
- conditional passthrough honoring child defaults,
- exact flag-name match against the child,
- list-based command assembly (no shell injection surface),
- 5 new targeted tests (all passing), plus 209/210 full-suite green,
- ruff clean,
- canonical artifacts (manifest + wdo-2024-08 parquet) byte-identical to locked hashes.

Gage is unblocked to proceed with G09a retry #3.

---

**Signature:** Quinn (@qa) · 2026-04-23
