# R15 Canonical Invariant Hardening — Strategy

**Document type:** Architecture strategy / governance proposal
**Drafter:** Dara (@data-engineer) — data layer / canonical-producer surface custodian
**Tri-signature required (this strategy → implementation):** Dara (drafter, data layer authority) + Dex (@dev, implementation) + Riven (@risk-manager, R10 custodial sentinel)
**Spec authority chain (Article IV — No Invention):**
- RA-20260428-1 Decision 7 — story authority for git-tracking the two canonical files (anomaly discovery, baseline commit pins)
- MWF-20260422-1 — manifest write-flag contract (`VESPERA_MANIFEST_COSIGN` env var + flag regex `^MC-\d{8}-\d+$`); authoritative for ALL future manifest mutations
- MC-20260423-1 — precedent for retro custodial sign-off (manifest rows 1→16 retro APPROVED); template for "ex-ante MC" issuance
- MC-20260429-1 D9 — most recent application of cosign discipline (manifest 16→19 rows under Decisions 3 + 4)
- R15 story `docs/stories/R15-canonical-invariant-hardening.story.md` (PR #3 PASS at HEAD `ee786f80`) — baseline tracking commit; no content mutation

**Status:** DRAFT (Dara strafter sign-off pending Aria architectural decision; Dex + Riven cosign deferred to post-Aria)
**Story this strategy informs:** future story (R15.2 candidate per R15 §4 follow-up) — provisioning of pre-commit hooks + CI; this strategy is the architectural input
**Scope discipline:** strategy text only; **zero canonical mutation**, zero `git add`, zero hook installation in this document's lifecycle.

---

## 1. Problem statement (silent-failure mode)

### 1.1 Mechanism of the silent failure

Pre-PR-#3, both canonical-invariant files were untracked in git:

- `data/manifest.csv` — R15 append-only manifest (MWF-20260422-1 contract surface); pin `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`
- `core/memory_budget.py` — ADR-1 v3 constants home (R1-1 invariant); pin `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d`

Across dozens of stories (T002.x, MC-20260429-1 D3/D4/D9, RA-28-1 step-7, etc.) the squad enforced byte-equality with **`sha256sum` spot-checks at pre-step and post-step** of each canonical-touching dispatch. The agent discipline was rigorous; the **VCS layer was empty**.

**Silent-failure mechanism:** every "pre-state sha == post-state sha" check was structurally a comparison between two reads of the *same on-disk bytes minutes apart*. Without a baseline commit in git, neither side of the equality referenced an authoritative immutable record. The check was trivially true under any drift mode that mutated bytes uniformly between the two reads — which is exactly what most drift vectors produce:

| Drift vector                            | Pre/post sha relationship | Detected by old discipline? |
|-----------------------------------------|---------------------------|-----------------------------|
| Editor BOM insertion at file open       | Both reads see new BOM    | NO — sha matches itself     |
| `core.autocrlf=true` checkout normalize | Both reads see CRLF       | NO — sha matches itself     |
| OneDrive sync byte-rewrite              | Both reads see rewrite    | NO — sha matches itself     |
| Antivirus quarantine-and-restore        | Both reads see restore    | NO — sha matches itself     |
| Trailing-newline normalization on save  | Both reads see new newline | NO — sha matches itself    |
| Manual single-row mutation by mistake   | Both reads see mutation   | NO — sha matches itself     |

PR #3 closed the *first half* of the gap by establishing baseline commits (HEAD `ee786f80`, `.gitattributes` `-text` pinning). The remaining gap is **enforcement at the write boundary**: a future commit could still mutate the canonical files silently if no automated check fires before/at commit/push time.

### 1.2 Why this is custodial (not just hygiene)

R10 (custodial discipline, Riven scope) and R15 (append-only invariant, Riven sentinel) both depend on the canonical files representing the authoritative ground truth. If the canonical files drift undetected, every downstream artifact that pinned their sha (every audit YAML, every story File List, every gate sign-off block) becomes evidentially compromised — not because the audit was wrong, but because the artefact it referenced changed underneath it. **Custodial integrity collapses silently.**

The MWF-20260422-1 contract addresses this at the *write API* (via `VESPERA_MANIFEST_COSIGN` env var on `materialize_parquet.py`), but it has no purchase on git operations: `git add data/manifest.csv && git commit` doesn't go through `materialize_parquet.py`. R15 PR #3 closed the tracking gap; this strategy closes the **commit-time enforcement gap**.

---

## 2. Proposal — defense in depth at three layers

The proposal combines three enforcement loci, layered to match the existing tri-signature governance pattern (each layer mirrors one of Dara/Dex/Riven authority):

| Layer | Locus            | Authority owner | Role                                       |
|-------|------------------|-----------------|--------------------------------------------|
| L1    | Pre-commit hook  | Dex (impl)      | Local, fast, instant feedback (<100 ms)    |
| L2    | CI workflow      | Gage (R12)      | Server-side, authoritative, non-skippable  |
| L3    | Custodial review | Dara + Riven    | Human review on every PR touching canonicals |

L1 + L2 together replicate the MWF-20260422-1 cosign discipline at the VCS boundary. L3 is unchanged from current practice — this strategy formalizes it as load-bearing rather than incidental.

### 2.1 L1 — pre-commit hook (committer-local)

Per R15 story §3 / T4.1 sketch (already drafted by Dex), `.githooks/pre-commit-canonical-invariant`:

- Reads pinned shas for the two canonical files from a tracked `canonical-invariant.sums` file (single source of truth).
- For each staged path matching a pinned canonical, computes `git show ":${path}" | sha256sum` (the staged blob, not the disk file — avoids race with editor saves).
- If staged sha ≠ pin: searches `COMMIT_EDITMSG` for a co-sign flag matching `MWF-[0-9]{8}-[0-9]+|R1-1-WAIVER-[0-9]{8}-[0-9]+|MC-[0-9]{8}-[0-9]+` (the third disjunct is new — accepts MC ex-ante issuance per MC-20260423-1 precedent).
- Without the flag: exit 1 with explicit message citing the contract.
- With the flag: emit a NOTE to stderr and exit 0.

Activation requires `git config core.hooksPath .githooks` — opt-in per developer, but the activation is itself a one-line tracked change so it propagates via README onboarding.

### 2.2 L2 — CI workflow (server-side authoritative)

`.github/workflows/canonical-invariant-check.yml`:

- Triggers: `pull_request` to `main`, `push` to `main`.
- Step 1: `sha256sum -c .github/canonical-invariant.sums` — fails the job on any drift.
- Step 2 (PR only): if `.github/canonical-invariant.sums` itself was modified in the PR, require the PR title or body to contain the cosign flag regex above. Otherwise fail the check.
- Required check in branch protection for `main` (Gage R12 scope to toggle).

This is non-bypassable (`--no-verify` doesn't apply server-side; branch protection blocks the merge button if the check fails).

### 2.3 L3 — custodial review on every canonical-touching PR

Codified as a CODEOWNERS rule:

```
data/manifest.csv             @data-engineer @risk-manager
core/memory_budget.py         @data-engineer @risk-manager
.github/canonical-invariant.sums  @data-engineer @risk-manager
.githooks/pre-commit-canonical-invariant  @dev @risk-manager
```

Any PR diff touching the canonical files or the cosign infrastructure requires a Dara + Riven review per GitHub branch protection. This formalizes what Dara already does ad-hoc (T2 custodial diff review in R15 story).

---

## 3. Trade-offs — git-tracked vs off-tree

### 3.1 Option A: keep canonicals **off-tree** (status quo pre-R15)

- **Pro:** zero risk of git operations mutating bytes (no `core.autocrlf`, no LF-merge-driver, no `.gitattributes` complexity).
- **Pro:** R15 append-only is enforced *only* via the `materialize_parquet.py` cosign — single enforcement locus, no duplication.
- **Con (FATAL — already realized):** silent drift mode described in §1.1; no audit trail of who/when/why a row was added beyond agent self-discipline; baseline commit comparison impossible.
- **Con:** every story's "Files NOT touched" assertion is unverifiable by an automated tool — costs human review attention that scales linearly with story count.

### 3.2 Option B: track canonicals **in git** (R15 chosen path)

- **Pro:** baseline commit (`ee786f80`) provides the missing immutable reference for sha-equality checks.
- **Pro:** `.gitattributes -text` pinning (already in PR #3) freezes line-ending interpretation deterministically across Windows/Linux/macOS hosts.
- **Pro:** `git diff main...HEAD` becomes a free audit primitive — drift is visible in PR review without running custom tooling.
- **Pro:** the cosign discipline can be replicated at the VCS boundary (L1 + L2 above), giving a second enforcement locus that does not depend on developers running `materialize_parquet.py`.
- **Con (mitigated):** introduces git-side mutation vectors (CRLF, LF normalization). Mitigated by `.gitattributes -text` (already in PR #3).
- **Con (mitigated):** doubles the enforcement surface — both `materialize_parquet.py` cosign AND the L1/L2 hooks must agree on the contract. Mitigated by §4: a single regex literal sourced from a tracked spec file.
- **Con:** developers can still bypass the local hook with `--no-verify`. Mitigated by L2 (server-side, non-skippable).

**Decision recommendation (Dara):** Option B — already executed by PR #3 for tracking; this strategy completes it at the enforcement layer. **Option A is not survivable** given §1.1 silent failure.

### 3.3 Sub-option: hash-only tracking (`.sums` file) without tracking the canonicals themselves

- Track only `.github/canonical-invariant.sums` with the pins; keep `data/manifest.csv` and `core/memory_budget.py` off-tree.
- **Rejected** because: (a) the `.sums` file alone cannot bootstrap a fresh checkout — a new agent would have nothing to compare against; (b) loses the `git diff` audit primitive; (c) doesn't address the original anomaly Gage flagged (the canonicals being invisible to git history).

---

## 4. Phased implementation

### Phase 1 — Architectural decision (Aria sign-off, **BLOCKING** for Phase 2+)

**Single decision pending:** does the squad accept tracking canonical files in git as architecturally sound (Option B), with the L1/L2/L3 enforcement model as the authoritative defense-in-depth pattern?

This is Aria's call because:
- It commits the squad to maintaining `.gitattributes` correctness in perpetuity (any new canonical surface added in the future inherits this discipline).
- It expands MWF-20260422-1 contract scope from "API write" to "VCS write" — that is a contract amendment which only the architecture authority (Aria) can ratify, not the data-layer authority (Dara) alone.
- It creates the `.github/canonical-invariant.sums` file as a *new tracked governance surface* — Aria must declare whether this surface is itself subject to R10 custodial / R15 sentinel discipline (recommended: yes, with its own cosign requirement; see §4.2 step 4).

**Aria deliverable (this gap):** a decision record (RA-YYYYMMDD-N or ADR amendment) containing:
1. Accept Option B as the canonical-invariant tracking model — YES / NO.
2. Authorize the cosign flag regex extension `MC-[0-9]{8}-[0-9]+` (currently MWF + R1-1-WAIVER only) at the VCS boundary — YES / NO.
3. Declare `.github/canonical-invariant.sums` and `.githooks/pre-commit-canonical-invariant` as L2-protected canonical surfaces (NEVER modify) — YES / NO.

Until Aria signs off on these three points, **Phase 2 cannot start** — Dex would have no authority to extend MWF contract scope or to introduce the `.sums` file.

### Phase 2 — Initial git-add of governance files (post-Aria)

Already partially done: PR #3 added `data/manifest.csv` + `core/memory_budget.py` + `.gitattributes`. What remains for Phase 2 is the **infrastructure files** (the `.sums` file and the hook itself):

- Question: does adding `.github/canonical-invariant.sums` to git require a special MC issuance?
- **Answer (proposed):** YES — Riven issues `MC-YYYYMMDD-N` *ex-ante* per MC-20260423-1 precedent, before Dex's `git add`. The `.sums` file content is byte-determined by the canonical pins (already tracked); the MC formalizes the act of declaring `.sums` as itself a canonical surface from this commit forward. The MC is recorded in `docs/MANIFEST_CHANGES.md` (existing log) and in the commit message.

**Phase 2 deliverable:**
- New story (R15.2 candidate) with tri-signature Dara + Dex + Riven, AC: add `.github/canonical-invariant.sums` + `.githooks/pre-commit-canonical-invariant` + `.github/workflows/canonical-invariant-check.yml` + `CODEOWNERS` lines, all under one `MC-YYYYMMDD-N` ex-ante flag.

### Phase 3 — Pre-commit hooks validating R15 (manifest append-only, no row deletion, no row mutation)

Hook responsibilities (extension of the §2.1 sketch; manifest-specific R15 enforcement):

1. **Detect canonical staging:** scan `git diff --cached --name-only` for `data/manifest.csv`.
2. **Diff verb classification:** compute `git diff --cached --numstat data/manifest.csv` → `<added> <removed> data/manifest.csv`.
   - `removed > 0` → R15 **violation** (row deletion or mutation in place); exit 1 unconditionally with `BLOCK: data/manifest.csv has -${removed} rows; R15 forbids row deletion or mutation` regardless of cosign flag.
   - `removed == 0 && added == 0` → no-op staging artefact; pass.
   - `removed == 0 && added > 0` → pure append; require cosign flag in commit message (proceed to step 3).
3. **Cosign flag validation:** as in §2.1.
4. **Header invariance:** parse the first line of the staged blob (`git show ":data/manifest.csv" | head -n1`) and compare verbatim to the pinned header `path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt`. Mismatch → exit 1 with `BLOCK: manifest header mutated`.

For `core/memory_budget.py` the hook is simpler (R1-1 = full immutability): any staged sha mismatch requires `R1-1-WAIVER-YYYYMMDD-N` in the commit message; no diff-verb logic needed.

### Phase 4 — Pre-commit hooks validating R10 cosign (cosign env vars + ruling reference)

Phase 3 enforces the *content invariants*; Phase 4 enforces the *authority chain* on the cosign flag itself.

The L1 hook (and the L2 CI step) extends the regex check to **resolve the flag to a ruling document**:

1. Extract the matched flag (e.g. `MC-20260429-1`) from the commit message.
2. Verify a corresponding governance artefact exists: `docs/governance/${flag,,}*.md` OR `docs/qa/gates/${flag}-gate.md` OR a Decision Matrix entry in `docs/architecture/memory-budget.md` referencing the flag.
3. If no matching ruling artefact: exit 1 with `BLOCK: cosign flag ${flag} present but no ruling document found at expected paths`.
4. (CI only — server-side) verify that the ruling artefact's sha is itself stable (was not modified in the same PR — prevents same-PR self-justification attacks).

This step is what gives the strategy *authority traceability*: a commit isn't allowed to invoke `MC-20260429-1` unless `MC-20260429-1` exists as a documented ruling somewhere in the tree. It mirrors Article IV (No Invention) at the VCS boundary.

---

## 5. Cosign integration — how `VESPERA_MANIFEST_COSIGN` extends to git-tracked canonical

The MWF-20260422-1 spec at `docs/architecture/manifest-write-flag-spec.md` L213 defines:

| Env var                       | Used at                       | Format         | Regex              |
|-------------------------------|-------------------------------|----------------|--------------------|
| `VESPERA_MANIFEST_COSIGN`     | `materialize_parquet.py` write | `MC-YYYYMMDD-N` | `^MC-\d{8}-\d+$`   |

The strategy proposes parallel application at the VCS boundary, with the **same regex**:

| Locus                              | Trigger                                                      | Required flag in              |
|------------------------------------|--------------------------------------------------------------|-------------------------------|
| `materialize_parquet.py` (existing) | `os.environ["VESPERA_MANIFEST_COSIGN"]` set                  | env var                       |
| L1 pre-commit hook (new)           | Staged blob sha ≠ pin for `data/manifest.csv`                | commit message body           |
| L2 CI workflow (new)               | Diff vs base contains `data/manifest.csv` with sha drift     | PR title or PR body           |

**Single source of truth for the regex:** `docs/architecture/manifest-write-flag-spec.md` L213. The hook and CI both source the regex literal from this spec via a tracked extraction script (`.githooks/lib/cosign-regex.sh`) so a future regex change in the spec propagates without code-edit duplication.

**Acceptance of `R1-1-WAIVER-YYYYMMDD-N`** (currently undefined as an env var because `core/memory_budget.py` has no runtime write path that needs gating): the L1/L2 hooks accept it as a sibling regex disjunct because `core/memory_budget.py` is edited only through git, not through a Python writer. The waiver namespace is declared in this strategy and carried into Aria's Phase 1 decision record. Until then it is provisional.

---

## 6. Risks — what can go wrong if git-tracking introduces a bug that overwrites canonical

This section enumerates failure modes specific to *adding the L1/L2/L3 enforcement* on top of the already-tracked canonicals. The risks of tracking itself were addressed in §3.2.

### 6.1 R-1: Hook bug allows mutation through

Scenario: `.githooks/pre-commit-canonical-invariant` has a regex bug (e.g. anchors the cosign-tag check incorrectly) and lets a malformed flag through. Result: a real mutation lands in `main` with a corrupt audit trail.

**Mitigation:** L2 CI is a second independent implementation (sha256 -c against `.sums` file); a hook bug doesn't propagate to CI because the CI doesn't share code with the hook. Defense-in-depth.

### 6.2 R-2: `.gitattributes` regression silently re-enables CRLF normalization

Scenario: a future PR removes the `-text` lines from `.gitattributes`, Windows checkout re-renders the canonicals with CRLF, sha drifts on next read.

**Mitigation:** add `.gitattributes` to the L3 CODEOWNERS list under Dara + Riven review. Add a CI step (in the same workflow as §2.2) that asserts the two `-text` lines are present in `.gitattributes`. Drift fails the check.

### 6.3 R-3: `.sums` file desynchronizes from canonical content under valid cosign

Scenario: a legitimate `MC-YYYYMMDD-N` append updates `data/manifest.csv` but the developer forgets to update `.github/canonical-invariant.sums`. Next PR's CI fails for an unrelated reason — the original drift is masked.

**Mitigation:** the L1 hook auto-updates `.sums` when a cosigned mutation lands (computes the new sha, writes it, stages the `.sums` file alongside the canonical). The CI verifies `.sums` matches HEAD content (not a stale pin). Coupling kept via tooling, not human discipline.

### 6.4 R-4: Same-PR self-justification attack

Scenario: a malicious / careless PR adds both a fake ruling document `docs/governance/mc-99999999-1.md` AND mutates `data/manifest.csv` with that flag in the commit message. The Phase 4 ruling-existence check passes because the file does exist (in the same PR).

**Mitigation:** the CI step at §4 step 4 explicitly checks that the ruling file's sha is *stable across the PR* (i.e. existed at base, not introduced in HEAD). New rulings require a separate prior PR cosigned by Riven.

### 6.5 R-5: LF-only repo merged into a CRLF working copy bypasses `.gitattributes`

Scenario: a developer with `core.autocrlf=true` and a stale checkout (pre-PR-#3) does `git pull` and Git renormalizes locally; the disk file's sha drifts even though git's blob sha is fine.

**Mitigation:** L1 hook computes `git show ":${path}" | sha256sum` (the staged blob, not disk). This is invariant under disk-side renormalization. The check works correctly even on misconfigured hosts. (Already in the §2.1 sketch.)

### 6.6 R-6: Hook execution permission lost on Windows

Scenario: the hook file loses its executable bit (Windows filesystem); `git config core.hooksPath` is set but the hook silently doesn't run.

**Mitigation:** add a CI smoke test that runs the hook against a known-bad commit and asserts exit-code 1. Catches breakage at PR time. Hook script also self-checks: if invoked but `git --version` returns non-zero (e.g. because PATH is broken), it exits 1 (fail-closed) rather than 0.

---

## 7. Tri-sig handoff — what Dex and Riven review when this strategy is ready

This strategy is the **drafter sign-off (Dara)**. Dex and Riven cosign **after** Aria's Phase 1 decision lands, against this same document amended with Aria's RA reference. Their review scopes are non-overlapping:

### 7.1 Dex (@dev) review scope — implementation feasibility

- Validate the L1 hook sketch (§2.1, §4 Phase 3, §4 Phase 4) is implementable in portable bash with no GNU-specific extensions (Windows Git Bash compatibility).
- Validate the L2 CI workflow (§2.2) syntax against current `.github/workflows/` conventions (none yet exist in repo; Dex confirms whether `actions/checkout@v4` is the right pinned version per repo policy).
- Validate the `git show ":${path}" | sha256sum` invariant under the Windows `core.autocrlf=true` host that Dex used in PR #3 — test that the staged-blob path produces identical shas to the pin regardless of disk-side normalization.
- Validate the regex single-source-of-truth pattern (§5) is implementable — the `.githooks/lib/cosign-regex.sh` extraction script must work both in pre-commit context (git working directory available) and in CI context (post-checkout).
- Estimate effort for the R15.2 follow-up story (the implementation story this strategy authorizes).

### 7.2 Riven (@risk-manager) review scope — R10 custodial integrity

- Confirm the L1+L2+L3 layering matches the tri-signature governance pattern (Dara + Dex + Riven) and that no enforcement responsibility falls outside one of the three custodial loci.
- Ratify the cosign flag regex extension (`MC-[0-9]{8}-[0-9]+` accepted at VCS boundary alongside `MWF-...` and `R1-1-WAIVER-...`) — this is a contract scope expansion and Riven owns the contract integrity for R10/R15.
- Validate the §6 risk register: are R-1 through R-6 mitigated to "no silent failure mode remains"? If any risk has no mitigation that fails closed, Riven blocks the cosign.
- Confirm the R-3 (`.sums` desync) mitigation is sound: hook-driven `.sums` auto-update means the `.sums` file becomes a *derived* artefact; Riven must agree this is acceptable from a custodial standpoint or require manual cosign each time.
- Confirm that `MC-20260423-1` precedent (retro custodial sign-off) and `MC-20260429-1` D9 (recent ex-ante issuance) are correctly cited as the authority chain for the "ex-ante MC for `.sums` introduction" (§4 Phase 2). Article IV traceability check.
- Sentinel cosign on `.github/canonical-invariant.sums` itself becoming a canonical surface — does it inherit R15 append-only semantics, or is it a derived sha file that can be rewritten in place? **Recommended:** rewritten in place is correct (it's a sha mirror, not a log), but the rewrite requires the same MWF/MC cosign flag as the canonical it mirrors. Riven ratifies.

### 7.3 What this strategy does NOT decide (deferred to Aria + downstream stories)

- The exact R15.2 story AC list (drafted by Pax/Morgan once Aria signs off; this strategy is upstream).
- The CI workflow's exact GitHub Action versions (Dex pins at impl time per repo conventions).
- Whether to extend the cosign discipline to *other* canonical surfaces (e.g. `docs/architecture/memory-budget.md` itself, ADR documents, MWF spec) — out of scope per R15 story §4 ("pushes to R16 or later").
- The branch-protection rule wording on `main` (Gage R12 scope).
- The CODEOWNERS file's exact path-glob syntax (Dex impl detail).

---

## 8. Cross-references

| Reference                                                              | Purpose                                                                |
|------------------------------------------------------------------------|------------------------------------------------------------------------|
| `docs/stories/R15-canonical-invariant-hardening.story.md`              | Story this strategy informs (PR #3 baseline)                           |
| `docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md`           | Story-level QA gate (PASS, sha `8c4016b8...50bbe`)                     |
| `docs/qa/gates/R15-PR3-pre-merge-gate.md`                              | Pre-merge audit (PASS, 4/4 deterministic checks)                       |
| `docs/architecture/manifest-write-flag-spec.md`                        | MWF-20260422-1 contract — single source of truth for cosign regex      |
| `docs/qa/gates/MWF-20260422-1-gate.md`                                 | MWF contract gate                                                      |
| `docs/architecture/memory-budget.md` Decision Matrix                   | RA-20260428-1 Decision 7 (R15 authority); MC-20260423-1 / MC-20260429-1 D9 precedents |
| `docs/MANIFEST_CHANGES.md`                                             | Canonical log of manifest mutations (where ex-ante MC for `.sums` would land) |
| `docs/governance/mc-20260429-1-r4-halt-ruling-extension-retry2.md`     | Most recent applied ruling using cosign discipline                     |

---

## 9. Change log

- **2026-04-25** — Dara (@data-engineer) drafted strategy. Status: DRAFT (Dara drafter sign-off only; Aria Phase 1 decision pending; Dex + Riven cosign deferred to post-Aria). Zero canonical mutation in this draft. Zero `git add` performed. Authority chain cited per Article IV — RA-20260428-1 D7 + MWF-20260422-1 + MC-20260423-1 + MC-20260429-1 D9 + R15 story.
