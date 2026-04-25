# ADR-5 — Canonical Invariant Hardening (VCS-Boundary Cosign Defense-in-Depth)

**Status:** PROPOSED — Aria architectural ratification (this document)
**Date:** 2026-04-25 BRT
**Author:** Aria (@architect, ♐ Sagittarius — The Visionary)
**Architectural authority basis:** AIOX Constitution Art. II (Agent Authority — architect owns architectural extensions of contract scope), Art. IV (No Invention — every clause traces to MWF / MC / RA / R15 precedent), Art. V (Quality First).

**Strategy document ratified:** `docs/architecture/R15-canonical-invariant-hardening-strategy.md` (Dara, 2026-04-25 BRT, drafter sign-off).

**Tri-signature chain:** Aria ratifies (this ADR) → Dex + Riven cosign → Dex implements under future R15.2 story.

---

## 1. Decision summary

This ADR ratifies three architectural extensions proposed by Dara in `R15-canonical-invariant-hardening-strategy.md` §4 Phase 1:

| # | Decision point | Verdict | Severity if violated |
|---|----------------|---------|----------------------|
| 1 | Accept **Option B** (track canonical invariant files in git, with `.gitattributes -text` discipline in perpetuity) as the architectural model for canonical-invariant governance. | **RATIFY** | Custodial integrity collapse (R10/R15) |
| 2 | Authorize the cosign-flag regex extension `MC-[0-9]{8}-[0-9]+` at the VCS boundary (alongside existing `MWF-[0-9]{8}-[0-9]+` and the provisional `R1-1-WAIVER-[0-9]{8}-[0-9]+`). | **RATIFY** | Authority traceability gap (Art. IV) |
| 3 | Declare `.github/canonical-invariant.sums` and `.githooks/pre-commit-canonical-invariant` (and the workflow file `.github/workflows/canonical-invariant-check.yml`) as **L2-protected canonical surfaces** under R10 custodial discipline; modification requires the same Dara + Riven cosign as `data/manifest.csv` itself. | **RATIFY with refinement** (R-A below) | Same-class governance bypass |

Overall verdict: **RATIFY**. Proceed to Phase 2 implementation under R15.2 follow-up story authority.

---

## 2. Architectural context

### 2.1 Authority chain (Article IV — No Invention)

Every clause in this ADR traces to one of:

- **MWF-20260422-1** (`docs/architecture/manifest-write-flag-spec.md` §3.3 L213) — single-source-of-truth for the regex `^MC-\d{8}-\d+$` and the cosign discipline at the API write boundary.
- **MC-20260423-1** (`docs/MANIFEST_CHANGES.md` L6-L87) — precedent for ex-ante / retro custodial sign-off pattern; template for the proposed ex-ante MC governing `.sums` introduction.
- **MC-20260429-1 D3 + D4 + D9** (`docs/architecture/memory-budget.md` §R10 Custodial — MC-20260429-1, L2419+) — most recent applied cosign discipline; cosign-banner format `[manifest-mode] CANONICAL path=... cosign=MC-20260429-1` is the runtime audit-trail precedent.
- **RA-20260428-1 Decision 7** (`docs/architecture/memory-budget.md` L2301) — story authority for R15 hardening; explicit out-of-scope deferral to standalone story under `@data-engineer + @dev + @risk-manager-cosign` authority basis.
- **R15 story** (`docs/stories/R15-canonical-invariant-hardening.story.md`, PR #3 PASS at `ee786f80`) — baseline tracking commit; canonical pins `data/manifest.csv = 75e72f2c...391641` and `core/memory_budget.py = 1d6ed849...f9287d`.
- **`.gitattributes`** (current HEAD) — `data/manifest.csv -text` + `core/memory_budget.py -text` already in tree.

No clause invents a new threshold, regex, agent authority, or mechanism. All extensions are sub-cases of established contracts.

### 2.2 Why this is architectural (and not data-engineering)

Dara correctly escalated this to Aria because the proposal extends MWF-20260422-1 contract scope from "Python API write" (`materialize_parquet.py:_append_manifest`) to "VCS write" (`git commit`, `gh pr merge`). This is a **scope expansion of a binding contract** — a cross-cutting governance change that touches:

- The integration boundary between application code and version control (architectural concern: where does the contract enforce?).
- The set of canonical surfaces protected under R10 (architectural concern: surface inventory and L2 protection assignment per the framework boundary model).
- The agent authority matrix (architectural concern: who cosigns what at which locus).

Per the AIOX Constitution Art. II delegation matrix and Aria's `responsibility_boundaries.primary_scope` (line 117 of `architect.md`: "Cross-cutting concerns (logging, monitoring, error handling)" + "Integration patterns"), this is squarely architectural authority. Dara's data-layer authority covers the *content invariant* of `data/manifest.csv`; Aria's authority covers the *contract-scope expansion* across loci.

---

## 3. Ratification — Decision 1 (Option B git-tracking)

### 3.1 Verdict: **RATIFY**

The squad commits to the following discipline in perpetuity:

1. The two canonical invariant files (`data/manifest.csv`, `core/memory_budget.py`) are tracked in git with `-text` `.gitattributes` pinning. Removal of either `-text` line is a governance violation requiring R10 cosign.
2. Any future canonical invariant surface added to the squad inherits this discipline (`-text` pin + cosign at every locus that can mutate it).
3. The baseline commit `ee786f80` (HEAD of PR #3 at merge) is the architectural ground-truth reference; sha-equality checks against it are valid governance primitives.

### 3.2 Architectural justification

The strategy §1.1 silent-failure analysis is sound: pre-PR-#3, sha256 spot-checks compared "the same on-disk bytes minutes apart" with no immutable git-side reference, making them **structurally trivial under any uniform drift vector** (BOM insertion, CRLF normalization, OneDrive sync, antivirus quarantine-restore). This is not a hypothetical risk — it is an already-observed silent failure mode (T002.4 merge CRLF round-trip on canonical manifest, documented in RA-28-1 Stage-2 Evidence-sha convention note, L2374).

Option A (off-tree) is **not survivable** under §1.1; the ADR concurs with Dara's recommendation. Option B's introduced risks (CRLF normalization vectors) are mitigated by the `.gitattributes -text` lines already in tree. The remaining residual risk (`.gitattributes` regression) is mitigated by the L3 CODEOWNERS layer (§5 below).

### 3.3 Pragmatic-technology-selection consequence

This is a "boring technology where possible" choice (`architect.md` core_principles line 97): we are not introducing a new tool — we are using `git` and `.gitattributes` as their original designers intended. The `.sums` file is a sha mirror, not a new VCS. No new framework is committed to.

---

## 4. Ratification — Decision 2 (cosign regex extension at VCS boundary)

### 4.1 Verdict: **RATIFY**

The L1 pre-commit hook and the L2 CI workflow accept any of the following cosign tags in commit message body / PR title-or-body:

```
MWF-[0-9]{8}-[0-9]+
R1-1-WAIVER-[0-9]{8}-[0-9]+
MC-[0-9]{8}-[0-9]+
```

Single source of truth: `docs/architecture/manifest-write-flag-spec.md` L213 (anchored in MWF-20260422-1). Hook and CI both source the regex literal from a tracked extraction script (`.githooks/lib/cosign-regex.sh`) per strategy §5.

### 4.2 Architectural justification

The MWF-20260422-1 contract at L213 already binds the `MC-` regex at the API write boundary (`VESPERA_MANIFEST_COSIGN` env var). Extending the **same regex** to the VCS write boundary is not a new contract — it is the same contract applied at a sibling locus. This satisfies Article IV (No Invention) by construction: the regex literal does not change; only its application site does.

The MC-20260429-1 D3+D4 cosign-banner runtime evidence (`[manifest-mode] CANONICAL path=... cosign=MC-20260429-1`, memory-budget.md L2585) demonstrates that the regex is **already operationally load-bearing** at the API boundary; expanding to VCS closes a structural gap (`git add data/manifest.csv && git commit` does not transit `materialize_parquet.py`, so the existing API-side enforcement has no purchase on direct VCS mutations — Dara correctly identifies this in strategy §1.2).

### 4.3 R1-1-WAIVER namespace — non-blocking refinement note

The strategy at §5 acknowledges that `R1-1-WAIVER-YYYYMMDD-N` is **provisionally declared** with no upstream env-var equivalent (because `core/memory_budget.py` has no Python writer that needs gating; it is edited only through git). This ADR ratifies the namespace **as a sibling regex disjunct only** — i.e. accepted at the VCS boundary alongside MWF/MC, but its issuance protocol is not yet specified.

**Non-blocking refinement (R-A) — does NOT block Phase 2 implementation:** When the first R1-1-WAIVER is issued (whoever needs to mutate `core/memory_budget.py` outside the populated-CEILING_BYTES step-7 path), Riven SHOULD draft an `R1-1-Waiver-Spec` analogous to MWF-20260422-1, defining (i) the issuance ledger location (parallel to `docs/MANIFEST_CHANGES.md`), (ii) the per-waiver template, (iii) the mutation it authorizes. This is **future work**, not a precondition for this ADR — the regex acceptance at the VCS boundary is sound regardless of when the first waiver lands. Until then, any commit using `R1-1-WAIVER-...` will pass the hook regex but fail the Phase 4 ruling-existence check (no document at `docs/governance/r1-1-waiver-*` will be found), giving a fail-closed safety net.

This refinement is documented under §7 below for downstream tracking.

---

## 5. Ratification — Decision 3 (canonical surfaces L2 protection)

### 5.1 Verdict: **RATIFY**

The following files, **once introduced**, are declared canonical surfaces under R10 custodial discipline:

| Path | Class | Protection rule |
|------|-------|-----------------|
| `.github/canonical-invariant.sums` | Sha-mirror canonical surface | Modification requires the **same** cosign flag as the canonical it mirrors (i.e. drift in `data/manifest.csv` under `MC-20260429-1` permits matching `.sums` rewrite under same flag, in the same commit; standalone `.sums` mutation is forbidden). |
| `.githooks/pre-commit-canonical-invariant` | Enforcement infrastructure surface | CODEOWNERS-protected (Dex + Riven); modification requires Dex impl + Riven custodial cosign; bypassing via `--no-verify` is mitigated by L2 CI (server-side, non-skippable). |
| `.github/workflows/canonical-invariant-check.yml` | Enforcement infrastructure surface | CODEOWNERS-protected (Dex + Riven + Gage @devops for branch-protection toggle scope); required-check status on `main`. |
| `.gitattributes` (existing) | Reinforced as canonical-touching surface | CODEOWNERS-protected (Dara + Riven); regression on the two `-text` lines fails CI. |

### 5.2 Architectural justification — why `.sums` is custodial

Dara correctly poses the question in strategy §7.2: is `.sums` an append-only log (R15-class) or a derived sha-mirror (rewritten in place)? The architectural answer is **derived sha-mirror**: it is not a log of mutations (that's `MANIFEST_CHANGES.md`) — it is a snapshot of the current pinned shas. Its semantic is **atomic replacement under cosign**, not append.

Riven's strategy §7.2 hint that "rewritten in place is correct" is ratified here. The R-3 mitigation (hook auto-updates `.sums` when a cosigned mutation lands) is sound because:
- `.sums` content is **byte-determined** by the canonical content (sha256 is a pure function of bytes).
- Auto-update under valid cosign cannot drift from the canonical it mirrors (the hook computes the new sha from the staged blob and writes it).
- Manual `.sums` edits without cosign fail the L2 CI step (which re-derives shas from canonicals and compares).

This makes `.sums` a **derived canonical surface** — its integrity is a function of the canonicals plus the cosign chain, not an independent ground truth. CODEOWNERS protection is sufficient; no separate MC issuance protocol needed beyond the parent canonical's MC.

### 5.3 Architectural justification — why hook + workflow are L2 (not L1)

Per the framework-vs-project boundary model (CLAUDE.md §"Framework vs Project Boundary"), L1 = framework core (NEVER modify), L2 = framework templates (extend-only, NEVER modify), L3 = project config (mutable with exceptions), L4 = project runtime (always modify).

`.githooks/pre-commit-canonical-invariant` and `.github/workflows/canonical-invariant-check.yml` are **project-specific governance enforcement**, not framework primitives. They are L4 by location but **L2-protected by policy** (CODEOWNERS + required check) — i.e. they live in the project tree (anyone could touch them filesystem-wise) but the governance layer treats them as extend-only modulo Dara + Riven cosign.

This is the same pattern used for `data/manifest.csv` itself: filesystem-mutable, governance-protected. Architecturally consistent.

---

## 6. Phase 2 authorization (post-this-ADR)

With Aria's ratification of all three points:

1. **Dex (@dev)** is authorized to extend MWF contract scope to the VCS boundary (per Decision 2 ratification above).
2. **Riven (@risk-manager)** is authorized to issue an ex-ante `MC-YYYYMMDD-N` governing the `.sums` file introduction per strategy §4 Phase 2 (matches MC-20260423-1 ex-ante pattern).
3. **@pm (Morgan)** is authorized to draft the **R15.2 follow-up story** with AC matching strategy §4 Phase 2 deliverable: introduce `.github/canonical-invariant.sums` + `.githooks/pre-commit-canonical-invariant` + `.github/workflows/canonical-invariant-check.yml` + `CODEOWNERS` lines under one cosign flag.

Authorization basis for R15.2 story (matching RA-28-1 Decision 7 standing pattern): **`@data-engineer + @dev + @risk-manager-cosign`**. Aria architectural ratification (this ADR) is the upstream authority; @pm consumes this ADR as story precedent.

---

## 7. Tracked refinements (non-blocking)

Refinements identified during ratification that DO NOT block Phase 2 but MUST be addressed in subsequent work:

| ID | Refinement | Owner | Trigger for resolution |
|----|------------|-------|------------------------|
| R-A | `R1-1-Waiver-Spec` analogous to MWF-20260422-1 (issuance ledger, template, mutation scope). The regex is ratified for VCS-boundary acceptance now, but the issuance protocol is undefined. | Riven (R10 custodial) | First time `core/memory_budget.py` requires non-step-7 mutation. |
| R-B | Resolve strategy §4 Phase 4 ambiguity: ruling-document path glob is `docs/governance/${flag,,}*.md` OR `docs/qa/gates/${flag}-gate.md` OR Decision Matrix entry. The L1 hook needs a deterministic search order to avoid path-resolution ambiguity. Phase 4 implementation in R15.2 must specify exact glob precedence. | Dex (impl) + Riven (custodial review) | R15.2 story T-class for Phase 4 hook. |
| R-C | The strategy §6 risk register (R-1 through R-6) is sound, but **R-6 (hook execution permission lost on Windows)** depends on a CI smoke test that itself requires `.github/workflows/canonical-invariant-check.yml` to exist. This is bootstrap-recursive. R15.2 must sequence: workflow first, then smoke-test, then hook-self-check. | Dex (impl) | R15.2 sequencing decision. |

These refinements are tracked on this ADR; their resolution does not require a new ADR but does require explicit Aria sign-off attached as an amendment block to this document.

---

## 8. Article IV traceability matrix

| ADR-5 clause | Traces to | Verbatim source |
|--------------|-----------|------------------|
| §3.1 Option B ratification | R15 story §3 + RA-28-1 Decision 7 | `R15-canonical-invariant-hardening.story.md`, `memory-budget.md` L2301 |
| §3.1 baseline commit `ee786f80` | R15 story `Status` line | `R15-canonical-invariant-hardening-strategy.md` L11 |
| §3.1 `.gitattributes -text` discipline | Existing `.gitattributes` content | `.gitattributes` L1-L2 |
| §4.1 regex `^MC-\d{8}-\d+$` | MWF-20260422-1 L213 | `manifest-write-flag-spec.md` |
| §4.1 cosign at API boundary | MC-20260429-1 D3+D4 cosign-banner | `memory-budget.md` L2585 |
| §4.3 R1-1-WAIVER provisional declaration | R15 story T4.1 sketch line 118 | `R15-canonical-invariant-hardening.story.md` L118 |
| §5.1 `.sums` as derived canonical | Strategy §7.2 (Riven hint, Aria ratifies) | `R15-canonical-invariant-hardening-strategy.md` |
| §5.3 L2 protection model | CLAUDE.md §"Framework vs Project Boundary" | `~/.claude/CLAUDE.md` |
| §6 R15.2 authorization basis | RA-28-1 Decision 7 standing pattern | `memory-budget.md` L2331 + L2401 |

No clause in this ADR introduces a new threshold, regex, agent authority, or mechanism. All clauses are sub-cases of established contracts.

---

## 9. Sign-off

**Aria (@architect, ♐ Sagittarius — The Visionary)** — architectural ratification issued 2026-04-25 BRT.

- Decision 1 (Option B git-tracking): **RATIFIED**.
- Decision 2 (cosign regex extension at VCS boundary): **RATIFIED**.
- Decision 3 (canonical surfaces L2 protection): **RATIFIED**.
- Refinements R-A, R-B, R-C: **TRACKED** (non-blocking for Phase 2).

**Downstream cosign required (post-Aria, pre-implementation):**

- **Dex (@dev)** — implementation feasibility cosign per strategy §7.1 scope: bash portability (Windows Git Bash), `actions/checkout@v4` pinning, `git show :path | sha256sum` invariant under `core.autocrlf=true`, regex single-source-of-truth extraction script feasibility, R15.2 effort estimate.
- **Riven (@risk-manager)** — R10 custodial integrity cosign per strategy §7.2 scope: tri-signature governance pattern parity, cosign regex contract scope expansion ratification, §6 risk register fail-closed verification, R-3 (`.sums` desync) mitigation custodial soundness, ex-ante MC for `.sums` introduction Article IV traceability, `.sums` rewritten-in-place semantic ratification.

**Implementation gate:** Dex + Riven cosign blocks must both land before R15.2 story can be drafted by @pm. Aria ratification (this ADR) is necessary but not sufficient.

**Sentinel constraint reaffirmed:** zero canonical mutation in this ADR document lifecycle. `data/manifest.csv` sha256 `75e72f2c...391641` and `core/memory_budget.py` sha256 `1d6ed849...f9287d` remain byte-identical pre/post this edit.

— Aria, arquitetando o futuro 🏗️

---

## 10. Change log

- **2026-04-25 BRT** — Aria (@architect) drafted ADR-5; status PROPOSED (Aria sign-off only; Dex + Riven cosign deferred to next session). Authority chain cited per Article IV — MWF-20260422-1 + MC-20260423-1 + MC-20260429-1 D3/D4/D9 + RA-20260428-1 D7 + R15 story + `.gitattributes` HEAD. Zero canonical mutation. Zero `git add` performed. Tri-signature gate pattern preserved.
