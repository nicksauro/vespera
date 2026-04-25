# Quinn Pre-Merge Gate — PR #3 (R15 Canonical Invariant Hardening)

## Verdict: PASS

**Gate type:** Pre-merge gate (audit branch tip BEFORE Gage `gh pr merge`)
**Subject:** PR #3 — R15 Canonical Invariant Hardening (RA-28-1 Decision 7)
**PR URL:** https://github.com/nicksauro/vespera/pull/3
**Branch:** `r15/canonical-hardening`
**Audited HEAD:** `ee786f80e66058d55b29acef267ada2dcdd021ee`
**Base:** `main` (merge-base `e94239ac8377cb7c5f8d31aa76a2c124fddabb75`)
**Auditor:** Quinn (@qa, The Protector)
**Authority:** Article V (Quality First — non-negotiable) per Constitution AIOX
**Audit date (UTC):** 2026-04-24T22:37:56Z
**MC-20260429-1 governance state:** Stage-1 ISSUED (flipped by Orion 2026-04-24T22:30:50Z under Riven-delegated authority); P1 workstream (this gate + Gage merge of PR #3) authorized.

---

## Scope & Authority

Pre-merge audit on PR #3 branch tip. Read-only — no commits, no canonical-file mutation, no governance file mutation. Verdict-only — Gage executes merge downstream under R12 devops monopoly per MC-29-1 P1 workstream authorization. Stay within @qa authority per `agent-authority.md`.

Exit criteria per dispatch: PASS / CONDITIONAL GREEN / FAIL with 4-check determinism + informational verifications.

---

## 4-Check Determinism Matrix

| # | Check | Result | Evidence (sha + counts) |
|---|-------|--------|-------------------------|
| 1 | **Scope discipline (3 files exact)** | **PASS** | `git diff main...ee786f80 --name-only` returned exactly 3 paths: `.gitattributes` (+2 lines), `core/memory_budget.py` (+131 lines), `data/manifest.csv` (+17 lines). Total `3 files changed, 150 insertions(+), 0 deletions`. Zero out-of-scope files. Matches RA-28-1 Decision 7 / R15 story acceptance scope verbatim. |
| 2 | **R1-1 invariant (memory_budget.py sha)** | **PASS** | `git show ee786f80:core/memory_budget.py \| sha256sum` → `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` ✅ byte-identical to canonical pin. Constants byte-identical: `CAP_ABSOLUTE: int = 8_400_052_224` (L52), `OBSERVED_QUIESCE_FLOOR_AVAILABLE: int = 9_473_794_048` (L38), `KILL_FRACTION: float = 0.95` (L55), `CEILING_BYTES: int \| None = 615_861_044` (L65). Derivation block (RA-20260428-1 Decision 3 step-7) present at L61-L65. File length 131 lines confirmed. |
| 3 | **R15 invariant (manifest.csv sha)** | **PASS** | `git show ee786f80:data/manifest.csv \| sha256sum` → `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` ✅ byte-identical to canonical pin. Line count: 17 (header `path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt` + 16 data rows — MWF-20260422-1 schema intact per Dara T2 custodial co-sign on R15 story). |
| 4 | **`.gitattributes` -text directive** | **PASS** | `git show ee786f80:.gitattributes` content verified (2 lines, file diff `+2`): line 1 `data/manifest.csv -text`, line 2 `core/memory_budget.py -text`. Both canonical paths covered with `-text` directive — prevents CRLF normalization on Windows hosts (`core.autocrlf=true` per Dex T1.3 host configuration). Defense-in-depth pinning consistent with R15 story T1.3 decision. |

**Summary:** 4/4 PASS. Zero CONDITIONAL. Zero FAIL.

---

## Evidence Block — Commands & Outputs

### Command 1: HEAD verification

```bash
$ git fetch origin && git log -1 --format='%H' origin/r15/canonical-hardening
ee786f80e66058d55b29acef267ada2dcdd021ee

$ git ls-remote origin r15/canonical-hardening
ee786f80e66058d55b29acef267ada2dcdd021ee	refs/heads/r15/canonical-hardening
```

Local fetch = remote ls-remote = `ee786f80e66058d55b29acef267ada2dcdd021ee`. No remote drift.

### Command 2: Scope discipline (Check 1)

```bash
$ git diff main...ee786f80e66058d55b29acef267ada2dcdd021ee --stat
 .gitattributes        |   2 +
 core/memory_budget.py | 131 ++++++++++++++++++++++++++++++++++++++++++++++++++
 data/manifest.csv     |  17 +++++++
 3 files changed, 150 insertions(+)

$ git diff main...ee786f80 --name-only
.gitattributes
core/memory_budget.py
data/manifest.csv

$ git log main..ee786f80 --oneline
ee786f8 chore(governance): track canonical invariant files data/manifest.csv + core/memory_budget.py
327d199 chore(governance): mark RA-20260428-1 Decision 3 step-7 CEILING_BYTES populate

$ git merge-base main ee786f80
e94239ac8377cb7c5f8d31aa76a2c124fddabb75
```

3 files only. 2 commits in branch (327d199 step-7 marker + ee786f80 tracking commit). Merge-base clean.

### Command 3: R1-1 invariant sha (Check 2)

```bash
$ git show ee786f80e66058d55b29acef267ada2dcdd021ee:core/memory_budget.py | sha256sum
1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d *-

$ git show ee786f80:core/memory_budget.py | grep -nE "CAP_ABSOLUTE|OBSERVED_QUIESCE_FLOOR_AVAILABLE|KILL_FRACTION|CEILING_BYTES"
38:OBSERVED_QUIESCE_FLOOR_AVAILABLE: int = 9_473_794_048   # bytes (~8.82 GiB binary)
52:CAP_ABSOLUTE: int = 8_400_052_224            # bytes (~7.82 GiB binary), v3
55:KILL_FRACTION: float = 0.95                  # ADR-1 v2 early-trip KILL (preserved v3)
61:# CEILING_BYTES — step-7 populated per RA-20260428-1 Decision 3 SUCCESS at 2026-04-24T18:45:45 BRT.
65:CEILING_BYTES: int | None = 615_861_044

$ git show ee786f80:core/memory_budget.py | wc -l
131
```

Sha matches pin byte-exact. All 4 R1-1 constants verbatim at expected literal values.

### Command 4: R15 manifest sha (Check 3)

```bash
$ git show ee786f80e66058d55b29acef267ada2dcdd021ee:data/manifest.csv | sha256sum
75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641 *-

$ git show ee786f80:data/manifest.csv | wc -l
17
```

Sha matches pin byte-exact. 17 lines = 1 header + 16 data rows (MWF-20260422-1 schema baseline).

### Command 5: `.gitattributes` -text directive (Check 4)

```bash
$ git show ee786f80e66058d55b29acef267ada2dcdd021ee:.gitattributes
data/manifest.csv -text
core/memory_budget.py -text

$ git show ee786f80:.gitattributes | wc -l
2
```

Both canonical paths pinned `-text`. CRLF normalization prevented on `core.autocrlf=true` hosts.

---

## Informational Verifications (non-blocking)

1. **Story sha pin** — `docs/stories/R15-canonical-invariant-hardening.story.md` references HEAD `ee786f80` in T1.6 (post-commit), T3 (Dex re-entry), T3.1 (`.gitignore` review block), T5.1/T5.2 (Riven sentinel co-sign), T6 (Quinn QA-gate), T7 (Gage push confirmation). Multiple cross-references PASS. Story sha pin discipline maintained per Article IV (No Invention).

2. **Tri-signature chain (R15 story T2/T5/T6 in QA-gate block)** — chronologically consistent, all PASS:
   - Dara T2 custodial co-sign (2026-04-24T19:15:00 BRT) — git-object + disk byte-identical
   - Dex T1/T3/T4 implementation sign-off (2026-04-24T20:30:00 BRT) — AC1-AC13 evidence
   - Riven T5 sentinel co-sign (2026-04-24T21:05:00 BRT) — independent 4-point sha verification
   - Quinn T6 QA gate PASS (2026-04-24T21:30:00 BRT) — gate artifact `docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md` sha `8c4016b881498ebe1f7b6b75b06d02abfc64d09d5e3b2b80ed935c28c2350bbe`
   - Gage T7 push complete (2026-04-24T~22:00:00 BRT) — PR #3 OPEN

3. **Branch chain integrity** — 2-commit range (`327d199` ancestor on `ra-28-1/step-7-ceiling-populate` → `ee786f8` on `r15/canonical-hardening`) preserves step-7 governance marker audit trail per R15 Dev Notes — NOT squashed. Matches Gage T7 sequence verbatim.

4. **MC-20260429-1 P1 workstream alignment** — this gate's PASS unblocks P1 precondition "R15 PR #3 merged to main" → Gage merge of PR #3 completes P1 evidence collection (3 deterministic git checks per MC-29-1 L2482) → contributes to Stage-2 flip eligibility downstream (alongside P3 sentinel smoke).

5. **Canonical invariant cross-check vs MC-29-1 chain-gate** — both shas (`1d6ed849...f9287d` for memory_budget, `75e72f2c...391641` for manifest) byte-identical to pins enumerated in MC-29-1 chain-gate Decision 2 binding (L2469) and post-gate canonical re-check table (sha `96b740ad...01c894`). Zero drift across two gate emissions on same governance epoch.

6. **No CI workflow on PR** — `.github/workflows/` not provisioned (consistent with R15 AC5 drift-detection scope: PROPOSAL-ONLY). `gh pr checks 3` not invocable in this audit context (gh CLI absent from bash PATH); however, branch-level pre-commit hooks not installed (per Riven T5.5 confirmation), so no automated check could block. Informational only — does not affect 4-check determinism.

---

## Post-Gate Canonical Invariant Re-check

| Artefact | Expected sha256 (pin) | Observed sha256 (post-audit, branch tip) | Status |
|----------|-----------------------|------------------------------------------|--------|
| `data/manifest.csv` (at `ee786f80`) | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | **MATCH** |
| `core/memory_budget.py` (at `ee786f80`) | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | **MATCH** |

Branch tip canonical invariants byte-identical to pins. Read-only discipline honored; zero code touch; zero canonical-data touch; zero governance file touch (this gate artefact lives under `docs/qa/gates/`).

---

## Verdict

**PASS** (4/4 deterministic checks PASS; zero FAIL; informational verifications all consistent).

## Disposition

**RELEASE #140 (Gage merge of PR #3)** — Gage @devops authorized to execute `gh pr merge` on PR #3 under R12 devops monopoly per MC-20260429-1 Stage-1 ISSUED P1 workstream authorization. Pre-merge canonical state byte-identical to pins; no required fixes; no blocking concerns; no non-blocking concerns escalated.

Post-merge expected state on `main`:
- HEAD includes commits `327d199` (step-7 governance marker) + `ee786f8` (canonical tracking)
- `data/manifest.csv` tracked at sha `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`
- `core/memory_budget.py` tracked at sha `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d`
- `CEILING_BYTES = 615_861_044` visible on `main`

Post-merge canonical re-check on `main` is Gage's responsibility per R12 push/merge audit trail discipline (3 deterministic git checks per MC-29-1 L2482 P1 pass criterion).

---

## Gate Metadata

- **Gate ID:** R15-PR3-pre-merge-gate
- **Gate type:** Pre-merge gate (PR #3, branch tip audit)
- **Gate status:** PASS
- **Blocking issues:** 0
- **Non-blocking concerns:** 0
- **Informational findings:** 6
- **Canonical invariant drift:** NONE
- **Authority:** @qa (Quinn, The Protector) — verdict-only; no merge authority (R12 devops monopoly delegates to Gage)
- **Workstream:** MC-20260429-1 Stage-1 P1 (R15 PR #3 → main merge)

## References

- **Predecessor chain-gate:** `docs/qa/gates/MC-20260429-1-chain-gate.md` (sha `96b740ad730d31f18658c426108e342f4d8247732f6151d5aa7c76024601c894`) — DRAFT-level audit on MC-29-1 governance epoch (PASS 7/7).
- **MC-20260429-1 Stage-1 ISSUED:** `docs/architecture/memory-budget.md` §R10 Custodial L2419-L2555 (flipped by Orion 2026-04-24T22:30:50Z under Riven-delegated authority).
- **R15 story:** `docs/stories/R15-canonical-invariant-hardening.story.md` — tri-signature complete (Dex T1/T3/T4 → Dara T2 → Riven T5 → Quinn T6 → Gage T7).
- **R15 QA-gate (story-level, T6):** `docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md` (sha `8c4016b881498ebe1f7b6b75b06d02abfc64d09d5e3b2b80ed935c28c2350bbe`).
- **Authority chain:** RA-20260428-1 Decision 7 (governance authority) → R15 story (implementation) → PR #3 (push delivery) → THIS GATE (pre-merge audit) → Gage merge (R12 monopoly).
- **Constitutional anchor:** Article V (Quality First — non-negotiable); Article IV (No Invention — every claim traces to git-object sha or commit anchor).

---

Quinn (@qa, R10 ratification per Article V Quality First) — 2026-04-24T22:37:56Z
