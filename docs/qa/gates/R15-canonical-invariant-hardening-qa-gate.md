# QA Gate — R15 Canonical invariant git-tracking hardening

**Story:** `docs/stories/R15-canonical-invariant-hardening.story.md`
**Story sha at gate entry:** `ec73a2b19a3037668fb10850560706ff4996e6cd` (drifted from authorship `066310656d...` via authorized Morgan pin-reconciliation + Dara T2 + Dex T1/T3/T4 + Riven T5 sign-off updates — expected)
**Branch:** `r15/canonical-hardening` @ HEAD `ee786f80e66058d55b29acef267ada2dcdd021ee`
**Ancestor:** `ra-28-1/step-7-ceiling-populate` @ `327d1990`
**Gate executor:** Quinn (@qa)
**Gate timestamp (BRT):** 2026-04-24T21:30:00
**Spec authority:** RA-20260428-1 Decision 7 (`docs/architecture/memory-budget.md`)

---

## Verdict: **PASS**

All 7 quality checks PASS. Tri-signature (Dara + Dex + Riven) present and chronologically consistent. Canonical invariants byte-identical across disk and git-tree. No contract mutation, no test delta, no scope violation. **Ready for T7 (Gage devops push).**

---

## 7-check summary

| # | Check | Result | Justification |
|---|-------|--------|---------------|
| 1 | Requirements traceability | PASS | AC1–AC13 all map to verifiable evidence in commit ee786f80, story body sections, or QA-gate sign-off block (see AC coverage matrix below) |
| 2 | Test execution | PASS | `pytest tests/` → 263 passed, 1 skipped at HEAD `ee786f80`; same count at ancestor `327d1990` → zero test delta (AC13 satisfied). Note: expected baseline "272 passed" in dispatch preamble does not match repo reality — actual pre-R15 baseline is 263 passed / 1 skipped. AC13 scope is "zero delta" which IS satisfied. |
| 3 | Security / correctness review | PASS | `.gitattributes` `-text` directive correctly freezes line-ending interpretation for both canonical paths on Windows `core.autocrlf=true` hosts; drift-detection proposal embeds post-populate canonical shas (`1d6ed849...f9287d`), not stale pre-populate `51972c52...`; commit message cites RA-28-1 Decision 7 and MWF-20260422-1 explicitly |
| 4 | Parity audit (4-point sha check) | PASS | (a) disk `data/manifest.csv` = `75e72f2c...391641` ✅ pin; (b) disk `core/memory_budget.py` = `1d6ed849...f9287d` ✅ pin; (c) `git cat-file -p HEAD:data/manifest.csv \| sha256sum` = `75e72f2c...391641` ✅; (d) `git cat-file -p HEAD:core/memory_budget.py \| sha256sum` = `1d6ed849...f9287d` ✅. All 4 points byte-identical to pins. |
| 5 | Contract consistency | PASS | (a) MWF-20260422-1 manifest schema preserved (header `path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt` intact; 17 data rows); (b) R1-1 constants preserved verbatim in `core/memory_budget.py`: CAP_ABSOLUTE=8_400_052_224, OBSERVED_QUIESCE_FLOOR_AVAILABLE=9_473_794_048, KILL_FRACTION=0.95, CEILING_BYTES=615_861_044; (c) RA-28-1 Decision 7 scope honored (tracking-status-only change, zero content mutation). |
| 6 | Performance budget | N/A | Governance-only story, no performance surface. Drift-detection proposal (T4) is proposal-only — no hook installed, no execution overhead introduced. |
| 7 | Spec compliance (Article IV — No Invention) | PASS | Every story artifact traces to explicit authority: RA-20260428-1 Decision 7 (story authority), MWF-20260422-1 (manifest write contract), ADR-1 v3 (R1-1 constants home), RA-20260428-1 Decision 3 (step-7 CEILING_BYTES populate pin reconciliation), T002.4 merge commit `5a52ddd` (Gage anomaly discovery). Drift-detection proposal sha pins + co-sign flag regex match existing contract families verbatim. No invented features. |

---

## AC coverage matrix (AC1–AC13)

| AC | Requirement | Evidence pointer | Result |
|----|-------------|------------------|--------|
| AC1 | `data/manifest.csv` added to git with baseline commit; pre-add sha = post-commit sha = `75e72f2c...391641` | Commit `ee786f80`; story File list audit-trail block (3 sha samples across 3 time points); independent Quinn re-verification at gate (disk + git-object) | PASS |
| AC2 | `core/memory_budget.py` added to git with baseline commit; pre-add sha = post-commit sha = `1d6ed849...f9287d` | Commit `ee786f80`; story File list audit-trail; independent Quinn re-verification | PASS |
| AC3 | sha verification pre/post byte-identical — 4 sha256sum lines in File List | Story File list audit-trail block (6 samples: pre-add, post-commit, T3/T4 re-entry × 2 files); Dara T2.2 git-object verification; Riven T5.2 4-point check; Quinn gate 4-point re-verification | PASS |
| AC4 | `.gitignore` review with `git check-ignore -v` evidence + classification | Story "`.gitignore` findings" section (T3 by Dex); `git check-ignore -v` exit-code 1 (confirmed at gate: exit=1); classification (a) explicit allow (inline intent comment line 31 for manifest, zero matching patterns for memory_budget.py) | PASS |
| AC5 | Drift-detection proposal (pre-commit hook sketch + CI alternative) — text only, no implementation | Story "Drift-detection proposal" section (T4 by Dex); hook skeleton embeds post-populate canonical shas verbatim; GitHub Actions workflow sketch + `.sums` file sketch + trade-off matrix + R15.2 follow-up story draft. **Confirmed proposal-only at gate:** no `.githooks/` directory, no `.github/workflows/canonical-invariant-check.yml`, no `canonical-invariant.sums`, no `core.hooksPath` set. | PASS |
| AC6 | R15 append-only invariant re-stated in story body | Story "R15 contract restatement" section (4 numbered clauses: baseline immutability, mutation protocol, memory_budget.py invariance, zero-effect on contract) | PASS |
| AC7 | Tri-signature co-sign block (Dara + Dex + Riven) at QA-gate | Story QA-gate block contains: Dara T2 PASS (2026-04-24T19:15:00 BRT), Dex implementation PASS (2026-04-24T20:30:00 BRT), Riven T5 PASS (2026-04-24T21:05:00 BRT); chronologically consistent (T1→T2→T3→T4→T5); Quinn T6 sign-off pending at gate entry, added by this gate | PASS |
| AC8 | Content byte-identical across entire story lifetime (3 verification points) | 3 pre-authorship/pre-add/post-commit samples in File list + Dara T2 + Riven T5 4-point + Quinn gate 4-point = 10+ independent byte-identical verifications across 4 agents | PASS |
| AC9 | No other files modified besides story.md + baseline commit + conditional `.gitattributes` | `git show --stat ee786f80` lists exactly 3 files: `.gitattributes` (+2), `core/memory_budget.py` (+131), `data/manifest.csv` (+17), deletions=0. Story file modifications are governance-artifact (allowed). | PASS |
| AC10 | No PR opened by Dex/Dara/Riven/Quinn | Confirmed at gate: branch `r15/canonical-hardening` has no PR associated; handoff to Gage for T7 per R12 exclusive authority | PASS |
| AC11 | MWF-20260422-1 contract untouched | No new flag emitted; manifest schema header unchanged; 17 rows preserved; write-semantics documented as untouched in R15 contract restatement clause 4 | PASS |
| AC12 | ADR-1 v3 constants in `core/memory_budget.py` untouched | R1-1 invariant constants verified verbatim at HEAD: CAP_ABSOLUTE=8_400_052_224, OBSERVED_QUIESCE_FLOOR_AVAILABLE=9_473_794_048, KILL_FRACTION=0.95 (all v3); CEILING_BYTES=615_861_044 (post-step-7 populate, ancestor-provided, not introduced by R15) | PASS |
| AC13 | Zero test delta | pytest at HEAD = 263 passed / 1 skipped; pytest at ancestor `327d1990` (stashed check) = 263 passed / 1 skipped. Zero delta. No tests added, modified, or removed by R15. | PASS |

---

## Canonical invariant post-T6 re-check

| File | Expected pin | Disk sha256 at gate | Git HEAD object sha256 | Result |
|------|--------------|---------------------|------------------------|--------|
| `core/memory_budget.py` | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | `1d6ed849...f9287d` | `1d6ed849...f9287d` | PASS |
| `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c...391641` | `75e72f2c...391641` | PASS |

Both canonical invariants unchanged. Byte-identical across disk ↔ git-tree.

---

## Upstream evidence chain verification

| Artifact | Expected sha / value | Verified at gate | Result |
|----------|---------------------|------------------|--------|
| RA-20260428-1 Decision 3 audit YAML | `c60ca42af2ff2a1c875dcf36645ccd05b7c5055ad6955e0d650196a405445126` | `c60ca42a...45126` | PASS |
| Ancestor commit (step-7 populate) | `327d1990` | Confirmed on branch | PASS |
| Anomaly discovery commit | `5a52ddd6b1e710d830977b08be832850a6697842` | Confirmed in `git log main` | PASS |
| Baseline commit | `ee786f80e66058d55b29acef267ada2dcdd021ee` | Confirmed HEAD | PASS |

---

## Findings

**No FAIL findings. No CONCERNS findings.**

### Informational (non-blocking)

1. **Test-count preamble mismatch (informational only):** the T6 dispatch preamble stated expected baseline "272 passed / 1 skipped (Dex step-7 baseline)". Actual repo reality at ancestor `327d1990` is **263 passed / 1 skipped**. AC13 scope is "zero test delta" — satisfied (263/1 at both ancestor and HEAD). The 272 figure in the dispatch preamble appears to predate an earlier test-count adjustment and does not reflect the actual pre-R15 baseline. Not a gate issue; noted for dispatch-writer calibration.

2. **Story-file T5 checkbox state:** story line 138 shows `- [x] **T5 (Riven, @risk-manager)**` marked complete. T1–T4 and T6 remain `- [ ]` at gate entry. This gate fills T6.

---

## Disposition

**T6 PASS — ready for T7 (Gage devops push).**

Tri-signature complete (Dara + Dex + Riven); Quinn QA gate PASS; canonical invariants preserved byte-identical; no contract mutation; no scope violation; zero test delta. Gage @devops holds R12 exclusive authority for T7 push/merge.

---

## Quinn QA gate signature line (paste to story QA-gate block)

```
Quinn QA gate verdict (T6): PASS  — timestamp BRT: 2026-04-24T21:30:00  — signature line: @qa Quinn (The Protector) — R15 7-check QA gate PASS. (1) Requirements traceability: AC1–AC13 all map to verifiable evidence (see coverage matrix in docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md). (2) Test execution: pytest tests/ → 263 passed / 1 skipped at HEAD ee786f80; identical count at ancestor 327d1990 → zero test delta (AC13 satisfied; dispatch-preamble "272" figure reconciled to actual 263 — informational). (3) Security/correctness: .gitattributes -text pinning + drift-proposal shas post-populate verbatim. (4) Parity 4-point: disk sha + git-object sha byte-identical to pins for both canonical files. (5) Contract consistency: MWF-20260422-1 schema intact (17 rows, header untouched); R1-1 constants verbatim (CAP_ABSOLUTE=8_400_052_224, OBSERVED_QUIESCE_FLOOR_AVAILABLE=9_473_794_048, KILL_FRACTION=0.95, CEILING_BYTES=615_861_044). (6) Performance: N/A governance-only; drift proposal is proposal-only, zero overhead. (7) Spec compliance (Article IV): every artifact traces to RA-28-1 Decision 7 / MWF-20260422-1 / ADR-1 v3 / RA-28-1 Decision 3 / T002.4 commit 5a52ddd — no invention. Tri-signature (Dara T2 → Dex T1/T3/T4 → Riven T5) chronologically consistent; AC7 satisfied. Post-T6 canonical re-check: disk + git-object shas unchanged from pins for both files. DISPOSITION: T6 PASS — ready for T7 (Gage @devops push, R12 exclusive).
```

---

## References

- Story: `docs/stories/R15-canonical-invariant-hardening.story.md`
- Spec authority: RA-20260428-1 Decision 7 (`docs/architecture/memory-budget.md` Decision Matrix)
- Write contract (untouched): MWF-20260422-1 gate — `docs/qa/gates/MWF-20260422-1-gate.md`
- Anomaly discovery: commit `5a52ddd6b1e710d830977b08be832850a6697842` (T002.4 merge by Gage)
- Decision 3 audit YAML: `data/baseline-run/ra-20260428-1-decision-3-audit.yaml` sha `c60ca42a...45126`
- Baseline commit: `ee786f80e66058d55b29acef267ada2dcdd021ee`
