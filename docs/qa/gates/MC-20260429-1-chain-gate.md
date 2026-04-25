# MC-20260429-1 DRAFT — Chain-Gate QA Audit

**Gate type:** Chain-gate (DRAFT-level, pre-Stage-1 flip)
**Subject:** MC-20260429-1 DRAFT — Gage G09 Mai+Jun 2025 Production Materialization Authorization
**DRAFT location:** `docs/architecture/memory-budget.md` L2419-L2555 (§R10 Custodial)
**Governance file sha256 (pre-audit, post-Riven draft write):** `9fb8eb1149c04d0c19e872fa21e7a2165b32469746b0108d803713ca15f635f7`
**Auditor:** Quinn (@qa, The Protector)
**Audit date (BRT):** 2026-04-24
**Precedent pattern:** RA-20260428-1 chain-gate (`docs/qa/gates/RA-20260428-1-chain-gate.md`)
**Sable mitigation applied:** `docs/governance/root-cause-audit-decision-1-propagation.md` mitigation #1 (fresh factual re-assertion) + #2 (inherited-decision factual re-verification)

---

## Scope & Authority

Chain-gate DRAFT-level audit on MC-29-1 only. Read-only on code. No commits, no manifest mutation, no `core/memory_budget.py` touch. Verdict-only — Orion/Riven handle Stage-1 flip downstream. Stay within @qa authority per `agent-authority.md`.

Exit criteria per dispatch: PASS / CONCERNS / FAIL with 7-check justifications + post-gate canonical invariant re-check.

---

## 7-Check Matrix

| # | Check | Result | 1-line justification |
|---|-------|--------|----------------------|
| 1 | Authorization chain integrity | **PASS** | Scope (L2436-L2442) + 9 Decisions (L2466-L2476) + 3 Preconditions P1-P3 (L2481-L2485) + 5 Invariants I1-I5 (L2489-L2494) + Consumption clause (Decision 8 L2475) + Rollback (Decision 7 L2474) all present, internally consistent, upstream-traceable (RA-28-1 D3 L2547, R15 PR #3 L2550, T002.4 L2549, MC-23-1 L2548). |
| 2 | Article IV (No Invention) | **PASS** | Every fact anchors to code-path or evidence: CEILING_BYTES=615_861_044 → RA-28-1 D3 SUCCESS + core sha `1d6ed849`; commits `327d199`+`ee786f8`; T002.4 merge `5a52ddd`; MC-23-1 schema L6-L87 for audit YAML. Constitutional refs §R10 custodial sign-off L2539 enumerate all anchors. Grep on MC-29-1 block (L2419-L2555) for "IDENTICAL to" → **zero matches**. No inheritance-idiom used; full factual re-assertion per Sable mitigation #1. MC-24-1 abandonment justified by 5 structural reasons L2450-L2462 — all cite code-path/commit/merge evidence. |
| 3 | Ceiling binding + R1-1 invariant consistency | **PASS** | Decision 2 (L2469) pins CEILING_BYTES=615_861_044 AND pins core sha `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` — matches live `core/memory_budget.py` on `r15/canonical-hardening` HEAD (verified via grep: `CEILING_BYTES: int \| None = 615_861_044`). WARN=0.85×=523_481_887, KILL=0.95×=584_568_091 — v3 fractions preserved. I3 invariant (L2492) binds runtime assert. CAP_ABSOLUTE + R4 + KILL constants upstream from R1-1 unchanged (this MC consumes, not derives). |
| 4 | Scope discipline | **PASS** | Scope clause L2436-L2441 lists exactly TWO runs: Mai-2025 + Jun-2025 WDO. I5 invariant (L2494) hardens hold-out boundary: "end-date ≤ 2025-06-30; post-run grep of manifest for any month > 2025-06 → HALT + rollback + MC CONSUMED + quarantine escalation (hold-out-leak class)". Explicit exclusions §Scope exclusion L2543: Jul-2025+, WIN, `--no-ceiling`, DB mutation, core constant change — all require new MC-YYYYMMDD-N amendment. No Jul-2025+ leakage pathway. |
| 5 | Branch/PR precondition clarity | **PASS** | P1 (L2482) is explicit: "R15 PR #3 merged to main. Canonical invariant hardening chain (commits `327d199`+`ee786f8`) on main branch; CEILING_BYTES=615_861_044 visible on main; `data/manifest.csv`+`core/memory_budget.py` tracked by git on main." Pass criterion enumerates 3 deterministic git checks (`git log --oneline` + `git cat-file -p main:core/memory_budget.py` + `git ls-tree main data/manifest.csv`). P1 consumed-by field lists "Decision 2, Decision 3" — Stage-2 execution cannot proceed without P1 evidence. No authorization-ahead-of-merge loophole; structural reason #3 L2456 explicitly rejects this pattern. |
| 6 | Telemetry contract binding | **PASS** | Decision 5 (L2472) binds T002.4 contract explicitly: "Both runs MUST emit `TELEMETRY_CHILD_PEAK_EXIT` at child exit per T002.4 contract (commit `80805ac5`)"; wrapper MUST persist CSV at `data/materialize-{may,jun}-2025-telemetry.csv`; pass criterion requires both `peak_pagefile_bytes`+`peak_wset_bytes` populated AND child-emitted values match wrapper-parsed values; fail criterion invokes "telemetry gap class — precedent: RA-26-1 retry #5 failure mode" HALT. T002.4 merge `5a52ddd6b1e710d830977b08be832850a6697842` cited in §References L2549. Format `commit=N wset=M pid=P timestamp_brt=T` is the post-T002.4-merge contract; no JSONL drift. |
| 7 | Two-stage flip pattern compliance | **PASS** | §DRAFT banner L2421-L2422 explicitly models RA-28-1 precedent (L2242-L2246 cited): "Stage-1 ISSUED flip requires Quinn chain-gate PASS on this DRAFT. Stage-2 ISSUED flip requires all P1-P3 preconditions landed under `data/canonical-relaunch/mc-20260429-1-evidence/` with sha256 manifest pinned. Decision 3 WITHHELD until Stage-2 flip." Next-links L2524-L2532 encode exact 8-step sequence: Quinn PASS → Orion Stage-1 flip → Gage P1+P3 → Quinn P-gates → Orion Stage-2 flip → Gage Decision 3 → Gage Decision 4 → Riven post-SUCCESS co-sign. No combined single-stage authorization. |

**Summary:** 7/7 PASS. Zero CONCERNS. Zero FAIL.

---

## Findings

### FAIL (blocking)
- None.

### CONCERNS (informational, non-blocking)
- None.

### Informational observations
1. **MC-24-1 abandonment documented thoroughly** (L2450-L2462) — 5 structural reasons each cite concrete code-path/commit anchors. Archaeological traceability preserved via MANIFEST_CHANGES.md L75-L81 reference. This exceeds the Sable mitigation #2 bar (Inherited-Decision factual re-verification) — Riven did not use inheritance idioms at all.
2. **Decision 6 invariant re-check mechanism is cell-level row comparison** (not file-level sha, since file sha MUST change on append) — correct choice; row-level hash comparison is the right mechanism for append-only mutation verification.
3. **Decision 9 post-SUCCESS co-sign** binds pattern parity with MC-23-1 schema L6-L87 — explicit schema inheritance is factual, not governance-clause inheritance (Sable mitigation #2 not triggered for schema parity).
4. **P2 precondition is self-referential** (L2483): "Quinn MC-29-1 chain-gate PASS" — this gate IS P2. Emitting this PASS verdict completes P2. Expected per two-stage pattern.
5. **Hold-out invariant I5** (L2494) is hardened beyond prior MC precedent — adds post-run grep sweep for month>2025-06, not just CLI boundary check. Defense-in-depth pattern.

---

## Post-Gate Canonical Invariant Re-check

| Artefact | Expected sha256 | Observed sha256 (post-audit) | Status |
|----------|-----------------|------------------------------|--------|
| `data/manifest.csv` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` | **UNCHANGED** |
| `core/memory_budget.py` | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` | **UNCHANGED** |

Both canonical invariants byte-identical pre/post audit. Read-only discipline honored; zero code touch; zero canonical-data touch.

Governance file `docs/architecture/memory-budget.md` sha pre-audit: `9fb8eb1149c04d0c19e872fa21e7a2165b32469746b0108d803713ca15f635f7` (this gate artefact lives under `docs/qa/gates/`, separate path — no governance-file mutation by this gate emission).

---

## Verdict

**PASS** (7/7 checks PASS; zero CONCERNS; zero FAIL).

## Disposition

**Ready for Stage-1 ISSUED flip** by Orion (aiox-master) post-Riven-authorization-delegation per flip_procedure L1835 pattern. P2 precondition satisfied by this gate emission. Downstream sequence per MC-29-1 §Next-links L2524-L2532 is unblocked; no amendments required to the DRAFT prior to flip.

---

## Gate metadata

- **Gate ID:** MC-20260429-1-chain-gate
- **Gate type:** DRAFT chain-gate (pre-Stage-1)
- **Gate status:** PASS
- **Blocking issues:** 0
- **Non-blocking concerns:** 0
- **Informational findings:** 5
- **Canonical invariant drift:** NONE
- **Authority:** @qa (Quinn, The Protector) — verdict-only; no flip authority
