# Manifest Write Flag — Spec

**Spec ID:** MWF-20260422-1
**Author:** Riven (R10 — Risk Manager, Custodial Authority on `data/manifest.csv`)
**Date issued:** 2026-04-22 BRT
**Status:** ISSUED — pending Dex implementation, then Quinn QA gate
**Target file:** `scripts/materialize_parquet.py`
**Downstream implementer:** @dev (Dex)
**Downstream gate:** @qa (Quinn)

---

## 1. Context

### Why this spec exists

@devops (Gage) halted **G09a (baseline-run Aug-2024)** at pre-flight on 2026-04-22
because `scripts/materialize_parquet.py` **unconditionally appends to canonical
`data/manifest.csv`** on every non-empty month write.

Confirmed defect sites in `scripts/materialize_parquet.py`:
- Line 100: `MANIFEST_PATH = REPO_ROOT / "data" / "manifest.csv"` — hardcoded.
- Line 549: `_append_manifest([month_row])` — unconditional call inside main
  loop whenever `df` is non-empty.
- Argparse (lines 173-214): no `--no-manifest`, no `--manifest-path`, no
  env-var override. `--output-dir` redirects only parquet; manifest is
  independent.

This violates R10 custodial protocol: **every mutation of `data/manifest.csv`
requires ex-ante R10 sign-off** via an `MC-YYYYMMDD-N` entry in
`docs/MANIFEST_CHANGES.md`. See precedent **MC-20260423-1** (retro sign-off
issued to @dev after an unauthorized 1→16-row mutation).

### What this spec unblocks

The baseline-run must materialize Aug-2024 into a scratch directory
(`data/baseline-run/scratch/`) **without touching the 17-line canonical
manifest** (1 header + 16 rows; sha256
`75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` at spec
issuance).

### References

- Precedent entry: `docs/MANIFEST_CHANGES.md` → `MC-20260423-1`.
- Hold-out lock pattern (the design analogue used below):
  `scripts/_holdout_lock.py`, env var `VESPERA_UNLOCK_HOLDOUT`.
- Constitution Art. II (Agent Authority), Art. IV (No Invention), Art. V
  (Quality First). This spec is binding under R10.

---

## 2. Decisions

### Decision 1 — Flag shape: **BOTH** `--no-manifest` AND `--manifest-path PATH`

**Final answer.** Implement two mutually-exclusive flags:

| Flag | Semantics |
|------|-----------|
| `--no-manifest` | Skip all manifest append logic entirely. No file is created or mutated. |
| `--manifest-path PATH` | Redirect manifest writes to `PATH` (scratch manifest). Must NOT equal the canonical path. |

**Rationale.**
- `--no-manifest` alone is insufficient: a scratch/baseline run still benefits
  from a local manifest (rows, sha256, phase) for the consumer (Beckett's
  CPCV loader, Gage's reruns) — losing that chain-of-custody is a quality
  regression even in scratch. Cite Art. V.
- `--manifest-path` alone is insufficient: there are operator scenarios
  (e.g. a pure dry-fetch or a re-hash audit run) where **no manifest at all**
  is the correct choice; forcing the operator to pick a dummy path is clutter.
- Mutual exclusion is enforced in argparse (`argparse.ArgumentParser`'s
  `add_mutually_exclusive_group`) — setting both is a CLI error.

### Decision 2 — Fail-closed custodial guard: **(c) BOTH env-cosign AND hash-pin**

**Final answer.** The `_append_manifest` function must refuse to write to
the canonical path `data/manifest.csv` unless BOTH:

1. **Env cosign present:** `VESPERA_MANIFEST_COSIGN` is set to a value
   matching the regex `^MC-\d{8}-\d+$` (e.g. `MC-20260423-1`).
2. **Hash pin valid:** if the canonical file already exists, its current
   sha256 must match the value supplied by the operator via
   `VESPERA_MANIFEST_EXPECTED_SHA256`. If the file does not exist, the
   env var must be the literal string `CREATE` (bootstrap case — first
   manifest write ever).

**Rationale.**
- (a) alone (env cosign only): prevents accidental writes but does not
  detect a manifest that was concurrently mutated by another process or
  an out-of-date operator. Sentinel-variance argument: the canonical file
  is the governance artifact; we must prove we know its current state
  before appending.
- (b) alone (hash pin only): prevents stale-state bugs but does not prove
  operator intent or link the mutation to an `MC-` entry.
- Mirroring the `VESPERA_UNLOCK_HOLDOUT` pattern (cited: `_holdout_lock.py`
  lines 42-43, 94-100) keeps the codebase's policy-gate vocabulary
  consistent — operators reading a traceback recognize this as a policy
  gate, not a bug. Cite Art. V.
- The cosign value is not validated against `MANIFEST_CHANGES.md` at runtime
  (that would couple the materializer to a governance parser); instead it
  is recorded verbatim in the run log so a post-hoc audit can cross-check.

### Decision 3 — Interaction with `--output-dir`: **Independent, with a mandatory warning**

**Final answer.** `--output-dir` and `--no-manifest` / `--manifest-path`
are **independent** flags. No auto-implication.

However: when `--output-dir` resolves to any path under `data/baseline-run/`,
`data/_scratch/`, or `data/scratch/` (prefix match on resolved absolute path),
and the operator has **not** set one of `--no-manifest` / `--manifest-path`,
the script MUST print a stderr warning:

```
[warn] --output-dir points to a scratch location ({path}) but the manifest
       target is the CANONICAL path ({canonical}). This will require
       VESPERA_MANIFEST_COSIGN=MC-... to proceed. If this is a throwaway
       run, pass --no-manifest or --manifest-path <scratch>.
```

The script does **not** exit on this warning — the cosign gate (Decision 2)
is the hard stop.

**Rationale.** "Explicit is better than implicit" (PEP 20) — auto-implying
`--no-manifest` from a scratch output dir would silently hide manifest
suppression from the operator and from the logs. The warning flags the
inconsistency loudly but lets the cosign gate do the actual enforcement.
Cite Art. V.

### Decision 4 — Logging / audit trail: **YES, verbose stderr banners**

**Final answer.** The script prints **three** banners to **stderr**:

1. **At launch (after argparse, before DB connect).** One of:
   - `[manifest-mode] NO-MANIFEST (--no-manifest active; no manifest file will be written)`
   - `[manifest-mode] SCRATCH path={resolved_path} (--manifest-path active)`
   - `[manifest-mode] CANONICAL path={canonical} cosign={VESPERA_MANIFEST_COSIGN value or NOT_SET}`

2. **At each point a manifest append would have happened but was suppressed**
   (i.e. inside the per-month loop when `--no-manifest` is active):
   - `[manifest-suppressed] month={YYYY-MM} reason=--no-manifest`

3. **At end of run (in the summary block):**
   - If `--no-manifest`: `[manifest] run complete; 0 month(s) flushed (--no-manifest active)`
   - If `--manifest-path`: `[manifest] run complete; {N} month(s) flushed -> {scratch_path}`
   - If canonical: unchanged from current behavior.

**Rationale.** R10 custodial operations require grep-able audit trails. A
future operator or auditor must be able to answer "did this run touch the
canonical manifest?" from the log file alone, without rerunning. The
banners are the audit record. Cite Art. II and Art. V.

### Decision 5 — Test coverage Dex must add

See Section 5 (Test Cases) below — 11 test cases, all pytest.

---

## 3. Flag specification

### 3.1 Argparse additions

Add the following to `build_parser()` in `scripts/materialize_parquet.py`:

```python
manifest_group = parser.add_mutually_exclusive_group()
manifest_group.add_argument(
    "--no-manifest",
    action="store_true",
    help=(
        "Do not append to any manifest. No manifest file is created or mutated. "
        "Use for throwaway/scratch runs (e.g. baseline-run). Mutually exclusive "
        "with --manifest-path."
    ),
)
manifest_group.add_argument(
    "--manifest-path",
    dest="manifest_path",
    type=Path,
    default=None,
    help=(
        "Override manifest target to PATH (scratch manifest). PATH MUST NOT "
        "equal the canonical data/manifest.csv — that target requires "
        "VESPERA_MANIFEST_COSIGN. Mutually exclusive with --no-manifest."
    ),
)
```

### 3.2 `Args` dataclass extension

```python
@dataclass(frozen=True)
class Args:
    start_date: date
    end_date: date
    ticker: str
    output_dir: Path
    dry_run: bool
    no_manifest: bool           # NEW
    manifest_path: Path | None  # NEW (None = canonical, else scratch)
```

`parse_args` must:
- Populate `no_manifest` from `ns.no_manifest`.
- Populate `manifest_path` from `ns.manifest_path`.
- If `manifest_path` is not None, resolve it (`Path(x).resolve()`) and
  compare against `MANIFEST_PATH.resolve()`. If equal, call
  `parser.error("--manifest-path must not point at the canonical data/manifest.csv; use the cosign flow instead.")`.

### 3.3 Env vars (new)

| Name | Required when | Format | Validation |
|------|---------------|--------|------------|
| `VESPERA_MANIFEST_COSIGN` | Writing to canonical path | `MC-YYYYMMDD-N` | Regex `^MC-\d{8}-\d+$` |
| `VESPERA_MANIFEST_EXPECTED_SHA256` | Writing to canonical path | 64-hex-char sha256 OR literal `CREATE` | Regex `^([0-9a-f]{64}|CREATE)$` |

Both are read in the guard function (below), never logged verbatim except
the cosign value which IS logged (it's a governance reference, not a secret).

---

## 4. Pre-mutation guard (pseudo-code)

Replace the current `_append_manifest` (lines 475-483) with the following
semantics. Dex writes the actual Python; the spec below is binding on
behavior.

```
def _resolve_manifest_target(args) -> Optional[Path]:
    """Return the path to write to, or None if writes are suppressed."""
    if args.no_manifest:
        return None
    if args.manifest_path is not None:
        return args.manifest_path
    return MANIFEST_PATH  # canonical


def _guard_canonical_write(target: Path) -> None:
    """Raise RuntimeError if writing to the canonical path without cosign."""
    if target.resolve() != MANIFEST_PATH.resolve():
        return  # scratch writes have no gate

    cosign = os.environ.get("VESPERA_MANIFEST_COSIGN", "")
    if not re.match(r"^MC-\d{8}-\d+$", cosign):
        raise RuntimeError(
            "Refusing to write to canonical data/manifest.csv without "
            "VESPERA_MANIFEST_COSIGN=MC-YYYYMMDD-N. This write requires "
            "R10 ex-ante sign-off in docs/MANIFEST_CHANGES.md. See "
            "docs/architecture/manifest-write-flag-spec.md."
        )

    expected = os.environ.get("VESPERA_MANIFEST_EXPECTED_SHA256", "")
    if not re.match(r"^([0-9a-f]{64}|CREATE)$", expected):
        raise RuntimeError(
            "Refusing to write to canonical data/manifest.csv without "
            "VESPERA_MANIFEST_EXPECTED_SHA256=<64hex>|CREATE."
        )

    if expected == "CREATE":
        if MANIFEST_PATH.exists():
            raise RuntimeError(
                "VESPERA_MANIFEST_EXPECTED_SHA256=CREATE but "
                f"{MANIFEST_PATH} already exists. Pass the current sha256 "
                "or delete the file if re-bootstrapping."
            )
        return  # bootstrap: file will be newly created

    actual = _sha256_file(MANIFEST_PATH)
    if actual != expected:
        raise RuntimeError(
            f"Refusing canonical manifest write: expected sha256={expected} "
            f"but current file is sha256={actual}. The manifest has drifted "
            "since the R10 sign-off was recorded; re-run audit and update "
            "VESPERA_MANIFEST_EXPECTED_SHA256."
        )


def _append_manifest(rows: list[dict], *, target: Path) -> None:
    # Called only when target is not None AND guard has passed.
    target.parent.mkdir(parents=True, exist_ok=True)
    exists = target.exists()
    with target.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(MANIFEST_COLUMNS),
                                lineterminator="\n")
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in MANIFEST_COLUMNS})
```

### 4.1 `run()` integration

Before the main month loop:
1. Resolve `target = _resolve_manifest_target(args)`.
2. Print the launch banner (Decision 4, banner 1).
3. If `target is not None`, call `_guard_canonical_write(target)` once
   up-front (fail fast before any DB work).

Inside the main month loop, replace the unconditional `_append_manifest([month_row])`
(line 549) with:
```
if target is None:
    print(f"[manifest-suppressed] month={mw.label} reason=--no-manifest",
          file=sys.stderr)
else:
    _append_manifest([month_row], target=target)
```

### 4.2 Scratch-output warning (Decision 3)

After argparse, before the launch banner, if `target == MANIFEST_PATH`
AND `args.output_dir.resolve()` starts with any of
`(REPO_ROOT/"data"/"baseline-run").resolve()`,
`(REPO_ROOT/"data"/"_scratch").resolve()`,
`(REPO_ROOT/"data"/"scratch").resolve()` — print the warning from Decision 3
to stderr. Do not exit.

---

## 5. Test cases (Dex implements; name + assertion binding)

All tests live under `tests/unit/test_materialize_manifest_flag.py` unless
otherwise noted. Dex writes the pytest code; the names and assertions
below are binding.

| # | Test name | Assertion (plain English) |
|---|-----------|---------------------------|
| 1 | `test_parse_args_no_manifest_flag` | Parsing `--no-manifest` sets `args.no_manifest=True` and leaves `manifest_path=None`. |
| 2 | `test_parse_args_manifest_path_flag` | Parsing `--manifest-path /tmp/foo.csv` sets `manifest_path=Path("/tmp/foo.csv")` and leaves `no_manifest=False`. |
| 3 | `test_parse_args_flags_mutually_exclusive` | Passing BOTH `--no-manifest` and `--manifest-path X` exits with `SystemExit` (argparse error). |
| 4 | `test_parse_args_rejects_manifest_path_equal_to_canonical` | `--manifest-path data/manifest.csv` (any form that resolves to the canonical path) exits with `SystemExit` and a helpful message. |
| 5 | `test_resolve_manifest_target_no_manifest_returns_none` | `_resolve_manifest_target(args with no_manifest=True)` returns `None`. |
| 6 | `test_resolve_manifest_target_scratch_returns_given_path` | `_resolve_manifest_target(args with manifest_path=X)` returns `X`. |
| 7 | `test_resolve_manifest_target_default_returns_canonical` | With neither flag set, returns `MANIFEST_PATH`. |
| 8 | `test_guard_canonical_blocks_without_cosign` | Writing to canonical path with `VESPERA_MANIFEST_COSIGN` unset raises `RuntimeError` mentioning `MC-YYYYMMDD-N`. Use `monkeypatch.delenv`. |
| 9 | `test_guard_canonical_blocks_malformed_cosign` | Cosign value `bogus` or `MC-2026` (wrong format) raises `RuntimeError`. |
| 10 | `test_guard_canonical_blocks_on_sha_mismatch` | With cosign set and file existing but `VESPERA_MANIFEST_EXPECTED_SHA256` pointing at a different hash, raises `RuntimeError` mentioning `drifted`. Use `tmp_path` fixture with a patched `MANIFEST_PATH` — do NOT touch the real file. |
| 11 | `test_guard_canonical_allows_on_sha_match_and_cosign` | With correct cosign and matching sha256, `_guard_canonical_write` returns without raising. |
| 12 | `test_guard_canonical_bootstrap_create` | With cosign set and `VESPERA_MANIFEST_EXPECTED_SHA256=CREATE` and file not existing, guard returns without raising. |
| 13 | `test_guard_canonical_create_rejects_existing_file` | With `EXPECTED_SHA256=CREATE` but file exists, raises `RuntimeError`. |
| 14 | `test_scratch_path_has_no_guard` | `_guard_canonical_write(tmp_path / "scratch.csv")` returns immediately without checking env. Even with no cosign set, no exception. |
| 15 | `test_no_manifest_banner_printed_on_launch` | Using `capsys`, a dry-run with `--no-manifest` prints `[manifest-mode] NO-MANIFEST` to stderr. |
| 16 | `test_scratch_output_warning_when_canonical_target` | Using `capsys`, a dry-run with `--output-dir data/baseline-run/scratch` and no manifest flags prints the scratch-warning to stderr. |

**Hard rule for all tests:** NO test may read, write, or stat the real
`data/manifest.csv`. Use `monkeypatch.setattr(mp, "MANIFEST_PATH", tmp_path / "manifest.csv")`
in any test that exercises the guard. Quinn will reject any test that
touches the canonical file.

---

## 6. Out of scope

- Modifying `MANIFEST_PATH` constant itself — stays at `data/manifest.csv`.
- Validating cosign values against `docs/MANIFEST_CHANGES.md` at runtime
  (couples materializer to governance parser; deferred).
- Retroactively gating other scripts that may mutate the manifest
  (future cross-cutting epic — file separately).
- Changing `--dry-run` semantics — unchanged.

---

## 7. Riven R10 co-sign

```
Spec ID:        MWF-20260422-1
Signed by:      Riven (R10 — Risk Manager, Custodial)
Signed at:      2026-04-22 BRT
Rationale:      Unblocks G09a baseline-run without compromising canonical
                manifest custody. Fail-closed guard (env cosign + sha pin)
                prevents recurrence of MC-20260423-1-class violations.
Bound agents:   @dev (implement), @qa (gate), @devops (execute baseline-run
                with --no-manifest or --manifest-path <scratch>).
Implementation: Proceed. No further R10 sign-off needed for code; next R10
                gate is at any future canonical manifest write (which will
                require a new MC-YYYYMMDD-N entry).
```
