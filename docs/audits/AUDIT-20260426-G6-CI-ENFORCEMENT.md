---
date: 2026-04-26 BRT
auditor: Sable (@squad-auditor)
trigger: Riven recommendation #3 post Dara empirical audit (council T002.0g §ESC-002)
mode: Autonomous Daily Session
scope: READ-ONLY — G6 CI gate enforcement of `.github/canonical-invariant.sums`
status: open
severity: ⚠️ moderate (with one ⚠️/[GAP] sub-finding on bash semantics)
tag: [DIVERGENCE] + [GAP]
---

# G6 CI Gate Enforcement Audit

## 1. Workflows enumerated

- `.github/workflows/canonical-invariant-protection.yml` — L2 server-side enforcement (per ADR-5 §3.2). Hosts the `sums-consistency` job that runs `sha256sum -c .github/canonical-invariant.sums`. Triggers: `pull_request: branches: [main]` + `push: branches: [main]`.
- `.github/workflows/canonical-invariant-smoke-test.yml` — `workflow_dispatch` only. Validates fail-closed semantics of `sha256sum -c` (known-bad mutation). NOT a gate; diagnostic only.

No other workflows in `.github/workflows/`.

## 2. canonical-invariant.sums verify step

- Found in: `.github/workflows/canonical-invariant-protection.yml` lines 57–77 (job `sums-consistency`).
- Command: `sha256sum -c .github/canonical-invariant.sums` (line 76).
- Trigger: `pull_request` to `main` AND `push` to `main` (lines 17–20).
- Required for merge: **UNVERIFIABLE FROM REPO** — branch protection lives in GitHub admin layer (see §4).

Additional G6-adjacent jobs in same workflow:
- `gitattributes-discipline` (R-2) — confirms `data/manifest.csv -text` + `core/memory_budget.py -text` lines intact.
- `sums-mutation-cosign` (R-4) — when PR diff touches `.sums`, requires cosign flag in PR title/body matching `MWF|R1-1-WAIVER|MC-YYYYMMDD-N` regex AND ruling artefact present at BASE_SHA (R-4 closure).
- `glob-precedence-verifier` (Riven C-1 R-B) — guards hook precedence ordering.

## 3. Pin enforcement verdict

**ACTIVE_BLOCKING — at workflow level. Branch protection layer UNVERIFIABLE from repo (admin-layer config).**

Rationale:
- Workflow runs on every PR + push to `main`. `set -euo pipefail` (line 69) + `sha256sum -c` exit non-zero on drift → job fails red.
- Cosign-validation logic is genuinely fail-closed: missing flag, malformed flag, missing ruling artefact, OR ruling-artefact-introduced-in-same-PR-HEAD all cause `exit 1`.
- HOWEVER: a failing GitHub Actions check only **blocks merge** if the check is registered as a **required status check** under branch protection rules. That toggle is GitHub admin-side (R12 Gage exclusive), NOT visible in the repository tree.

⚠️ Sub-finding `[GAP]` (M5 / glossary G2): line 73 emits `::warning::` text but then calls `exit 1`. The "advisory mode" comment in the workflow (lines 71–73) is misleading — the job still fails red. If branch-protection treats the workflow name as required, missing `.sums` blocks merge regardless of intent. This is functionally fine TODAY (`.sums` exists with a real pin for `data/manifest.csv` + `core/memory_budget.py`), but the line-9 comment claiming "non-skippable when wired into branch protection at T6" implies T6 has happened. **No evidence in repo confirms T6 was executed.**

## 4. R15.2 compliance

- Per R15.2 story (lines 199–203, T6) and ADR-5 §3.2, G6 SHOULD be a **required check on `main` branch protection**, configured by Gage @devops in T6 (R12 exclusive).
- Story file shows `T6 (Gage, @devops)` is `[ ]` (UNCHECKED) at line 199. Tasks T1–T5 marked `[x]` for T1; rest `[ ]` per visible state.
- Current state aligns? **NO — strong divergence.**
  - Workflow exists ✓
  - `.sums` baseline exists ✓ (lines 1–2 = pin for both canonical surfaces; line 9 = `PENDING_RIVEN_T8_DUAL_SIGN  state/T002/manifest.json` placeholder, NOT an active enforced sha)
  - Branch protection toggle (T6) — **NO IN-REPO EVIDENCE**. Story T6 unchecked. No QA-gate cosign block visible at lines 199–220.
  - `CODEOWNERS` (T5.3) — not checked here; outside G6 scope but related.

## 5. Bypass risks

- Force-push to `main`: **UNVERIFIABLE from repo** (admin setting). If branch protection has `enforce_admins: false` or push-restrictions absent, force-push bypasses required checks entirely.
- `[skip ci]` merge: GitHub Actions does NOT honor `[skip ci]` on `pull_request` events for required status checks — workflow runs regardless. SAFE on this axis.
- `enforce_admins`: **UNVERIFIABLE from repo**. If false, repo admins (Gage) can merge through failing required checks. This is the standard release-manager escape hatch but should be documented.
- `--no-verify` at commit time: bypasses L1 hook only. L2 (this workflow) catches mutation regardless. Mitigation chain holds for L2 IF required-check is wired.

## 6. Recommendations

Priority list for incoming story (River to draft):

1. **HIGH — Verify T6 actually executed.** Need empirical confirmation via `gh api repos/{owner}/{repo}/branches/main/protection` showing `canonical-invariant-protection` (or its job names — GitHub uses job-name-level required checks) in `required_status_checks.contexts`. If absent → G6 is **DECORATIVE** in production, Riven LAYERED_SAFE rationale collapses.
2. **HIGH — Update R15.2 story file** to reflect T6 status. Either mark `[x]` with evidence link OR mark explicitly `[blocked — pending Gage R12 execution]`.
3. **MEDIUM — Clarify advisory-mode comment** on workflow lines 71–73. Either remove the comment (now stale, `.sums` baseline exists) or change `exit 1` to `exit 0` with `::notice::` if advisory semantics are still desired (NOT recommended — fail-closed is correct posture).
4. **MEDIUM — Document `enforce_admins` policy** in ADR-5 or governance ledger. If admins can bypass, explicit ruling required.

## 7. Cross-stories impact

- **T002.0g — pinning `state/T002/manifest.json`:** Line 9 of `.sums` already declares `PENDING_RIVEN_T8_DUAL_SIGN  state/T002/manifest.json` as placeholder. Once Riven T8 dual-sign happens with real sha, `sums-consistency` job will start enforcing it on every PR/push. Feasible under current G6 setup ✓ — same `sha256sum -c` path covers it transparently. NO CI extension needed.
- **ESC-002 mitigation (DB guard view, story T002.0h):** If the DB guard view artefact is intended as a canonical surface (i.e. mutations require cosign), it must be added as a new line in `.sums` AND the canonical surface must be added to `.gitattributes -text` (R-2 mitigation). Same workflow covers it without modification IF artifact is a static file. If it's a runtime view (DB DDL), G6 is the wrong layer — that's Dara/Riven's runtime invariant pipeline, NOT this CI gate.

## 8. Verdict for queue

**`[USER-ESCALATION-PENDING]`** — G6 CI workflow exists and is fail-closed at the workflow level, BUT branch-protection enforcement (R15.2 T6) cannot be verified from repository state. T6 is the toggle that converts a green/red workflow into a merge-blocking required check. Without empirical confirmation, Riven LAYERED_SAFE assessment rests on an unverified assumption.

**Owner for fix:** @devops (Gage) — R12 exclusive for branch-protection inspection + execution. @sm (River) — to draft companion story documenting empirical verification.

**Re-audit trigger:** post `gh api ...protection` evidence captured + R15.2 T6 marked `[x]`.

— Sable, o cético do squad 🔍
