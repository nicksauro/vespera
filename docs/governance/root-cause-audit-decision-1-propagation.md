# Root-Cause Audit — Decision 1 False-Rationale Propagation Across Consecutive RAs

**Audit ID:** task #106
**Author:** Sable (@squad-auditor, The Investigator)
**Date authored:** 2026-04-24 BRT
**Class:** Retrospective, read-only, blame-free, structural root-cause audit
**Scope trigger:** @pm directive — reconstruct how the false Decision 1 rationale survived multiple RA cycles before being empirically falsified by Gage retry #4 (2026-04-23 BRT).
**Canonical-data guard:** This audit writes ONE file under `docs/governance/`. Zero touch to `core/memory_budget.py`. Zero touch to `data/manifest.csv`. Zero touch to any RA text in `docs/architecture/memory-budget.md`. Governance-only artifact.

---

## 1. Executive Summary

The false rationale was the sentence attached to Decision 1's `sentinel-timescaledb` stop row: **"Container is idle for baseline-run (baseline uses canonical parquets, not Sentinel DB)."** It was introduced at **RA-20260423-1** (first baseline-run quiesce RA under ADR-1 v2), then **reproduced verbatim** in **RA-20260424-1** and **RA-20260425-1** via explicit "IDENTICAL to [prior RA]" inheritance markers, surviving three successive R10 sign-offs, one Quinn v3 audit, and one Dex v3 patch cycle. It was empirically **falsified by Gage (@devops) retry #4 on 2026-04-23 BRT** under RA-20260425-1 when the authorized quiesce ran to completion, the R4 and E7 gates both PASSED, and the baseline-run child immediately exited 11 on `psycopg.OperationalError: connection refused at localhost:5433` — proving `materialize_parquet._fetch_month_dataframe` reads trades FROM the stopped sentinel container rather than from canonical parquets. The canonical Aug-2024 parquet (`wdo-2024-08.parquet`) was the OUTPUT of the baseline-run, not an input. **RA-20260426-1 corrected the rationale** (explicitly labeled "CORRECTED RATIONALE") by routing via Option B cache (`--source=cache`) rather than sentinel. **RA-20260428-1 does not re-propagate the false rationale** — it inverts it (requires sentinel UP because its workload is the sentinel-path streaming refactor measurement).

**Scope correction vs. task prompt:** The prompt specified RA-25-1/26-1/28-1 as the three propagation targets. Evidence shows the actual propagation chain was **RA-23-1 → RA-24-1 → RA-25-1** (three consecutive RAs inheriting the false rationale verbatim via "IDENTICAL to" markers). RA-26-1 is the **correction** RA. RA-28-1 is downstream governance that consumes the corrected chain. This audit follows the evidence, not the prompt's enumeration.

---

## 2. Timeline

| Date (BRT) | RA ID | Decision 1 `sentinel-timescaledb` rationale | Source of rationale | Accurate (Y/N) |
|---|---|---|---|---|
| 2026-04-23 (early) | **RA-20260423-1** | "Container is idle for baseline-run (baseline uses canonical parquets, not Sentinel DB)." | **ORIGIN** — self-authored by Riven at first draft (L659 of `memory-budget.md`). Anchor cited to "observed deficit in halt report + ADR-1 v2 §215 shared-resident analysis." Aria/Dex/Quinn chain had not yet observed an empirical baseline-run child execution. | **N** (latent — unused; wrapper passthrough missing halted at Step 1d) |
| 2026-04-23 (mid) | **RA-20260424-1** | VERBATIM copy. Table cell identical; anchor text reads *"Identical trace chain to RA-20260423-1"*. Marker: "**IDENTICAL to RA-20260423-1.** Reproduced for executability" (L822). | Inheritance marker — NO re-derivation. | **N** (latent — quiesce halted at Step 1e R4 gate; floor 9,473,794,048 bytes unreachable under v2 14.37 GiB threshold) |
| 2026-04-23 (late) | **RA-20260425-1** | VERBATIM copy. Marker: "**IDENTICAL to RA-20260424-1.** Reproduced for executability" (L1599). Anchor reads *"Identical trace chain to RA-20260424-1."* | Second inheritance hop — still no re-derivation. | **N** (this is where it **falsified** — R4+E7 both PASSED, child launched, `psycopg connect refused`, exit 11 at t+30.6s; `peak_commit=401,408 B` = startup only) |
| 2026-04-23 (late evening) | — | Falsification observed by Gage retry #4. `data/baseline-run/baseline-aug-2024-halt-report.md §Retry #4` authored. Recommendation §1: "Revise Decision 1 of the next RA to NOT stop `sentinel-timescaledb`. The assertion that baseline uses only canonical parquets is empirically false — materialize reads from PG-5433." | Empirical evidence from the authorized quiesce execution itself. | — (detection event) |
| 2026-04-26 (drafted) / 2026-04-24 UTC (ISSUED) | **RA-20260426-1** | "Under `--source=cache` routing … baseline-run reads raw trades from `data/cache/raw_trades/` via `feed_cache.py` — NO live sentinel dependency during the R4-governed window." Explicitly labeled **"— CORRECTED RATIONALE"** in the section header (L1894). | Aria ADR-4 Amendment §13 (Option B pre-cache layer) + T12b empirical proof (sentinel DOWN + cache-only → PASSED). Re-anchored to two empirical sources (halt report retry #4 + T12b verdict). | **Y** (correction) |
| 2026-04-28 (drafted) / 2026-04-24 UTC (ISSUED Stage-2) | **RA-20260428-1** | Decision 3 precondition inverts: *"sentinel-timescaledb container UP & healthy at invocation (inverse of RA-26-1 Decision 1 which stopped it under cache-path routing)"* (L2297). No quiesce under this RA — it's a sentinel-path workload measurement, not a quiesce. | New workload class; RA-26-1's correction preserved and deliberately inverted per workload need. | **Y** (orthogonal; no quiesce Decision 1 at all) |

---

## 3. Root Cause Analysis (3 Whys)

### Why 1 — Why did the false rationale appear at origin (RA-20260423-1)?

Riven authored Decision 1 under **argument-by-construction** (no empirical baseline-run child execution available yet). The rationale "baseline uses canonical parquets, not Sentinel DB" is a plausible-but-untested inference from surface semantics: baseline-run's OUTPUT artifact is `data/in_sample/year=2024/month=08/wdo-2024-08.parquet`, a canonical parquet, and prior ADR-1 v2 analysis discussed canonical parquet I/O. The actual INPUT pathway (`scripts/materialize_parquet.py:_fetch_month_dataframe` executing a PG query against `localhost:5433`) was not traced at Decision 1 drafting time. Article IV "No Invention" was satisfied at a bibliographic level (every sentence cited a prior doc) but NOT at a call-graph level (no cited doc proved the build path was PG-free).

### Why 2 — Why did it propagate verbatim across RA-24-1 and RA-25-1 without re-derivation?

The RA template established **"IDENTICAL to [prior RA]"** as a first-class inheritance idiom to minimize drafting surface area for the **changing** piece of each one-shot (RA-24-1 changed Decision 5 wrapper flags; RA-25-1 changed Decision 4 gate formula from v2 to v3). Decision 1 was presumed **invariant** across gate-formula and wrapper evolutions — structurally correct in governance terms (the services to stop did not depend on the R4 threshold or the wrapper flags), but this **invariance-by-structure compiled to invariance-of-scrutiny**. None of the three chain gates (wrapper-passthrough-gate for RA-24-1 precondition; ADR-1 v3 audit for RA-25-1 precondition) scoped a re-read of Decision 1 because Decision 1 was not on their diff. The "IDENTICAL to" marker explicitly invited reviewers to skip.

### Why 3 — Why was the false rationale not caught by any pre-execution gate?

The chain-gate protocol verifies **what changed** against invariants and citations, not **what was reproduced**. Quinn's ADR-1 v3 audit (`docs/qa/gates/ADR-1-v3-audit.md`) gated the v3 constants and the R4 formula change; Decision 1 text was not in scope. Quinn's wrapper-passthrough-gate addressed flag surface, not Decision 1 rationale. No agent held **call-graph validation** authority for RA Decision-text accuracy: @architect owned design, @dev owned code, @qa owned test/regression verification, @risk-manager owned R10 operational policy, @devops owned execution — but none owned "cross-check that each RA Decision's factual claim about system behavior matches the actual system call graph". The gap was a **responsibility seam**, not a skills gap. Gage's retry #4 was the first execution that could reach the point where the false claim became operationally load-bearing, and it failed-closed instantly (exit 11 at t+30.6s) — which is itself a testament to the canonical-state protections holding: no damage, clean detection, full rollback via Decision 6 restore (17/17 byte-identical sha256 match post-restore).

---

## 4. Detection Gap Analysis

### Gates that *should* have plausibly caught Decision 1 earlier

| Gate / Reviewer | Opportunity | Why it didn't fire |
|---|---|---|
| Riven R10 self-review at RA-23-1 drafting | Trace "uses canonical parquets" claim to the actual build-path source file | Drafting-time Article IV check operated on citation-presence, not call-graph truth. `scripts/materialize_parquet.py` was not required reading to draft Decision 1. |
| Aria @architect pre-RA-23-1 review | Could have flagged that the CANONICAL parquet is baseline's OUTPUT, not INPUT | Aria was not in the RA-23-1 drafting loop at the Decision 1 text level — Aria's architectural surface was ADR-1 v2 gate/threshold correctness, not RA Decision-rationale wording. |
| Dex @dev pre-execution review (owner of `materialize_parquet.py`) | Single grep for `psycopg` / `connect(` in the build path would have immediately refuted Decision 1 | Dex's review scope at each RA was the wrapper patch (passthrough, mutex) and v3 code constants. No protocol required Dex to cross-read RA Decision text against code the RA authorized to be run. |
| Quinn @qa ADR-1 v3 audit | 7-check matrix | Checks were scoped to v3 threshold correctness, smoke-verification of runtime constants, and regression suite cleanliness. Decision 1 rationale accuracy was not a check item. |
| Gage @devops Phase 1 pre-quiesce verification (RA-25-1 Decision 3) | sha256-gates on manifest + Aug-2024 parquet | The verifications gated **canonical state integrity**, not **Decision 1 factual soundness**. A clean pre-state does not falsify a faulty Decision 1 rationale. |

**Where the defense-in-depth actually held:** the canonical-state guards (hard bound 1-2: canonical manifest + parquets untouched) AND Decision 6's unconditional restore AND sha256 re-verification. When the false rationale finally bit (RA-25-1 retry #4), damage was strictly limited to 30.6 seconds of wasted child-process startup and one test-failure log line. **No canonical-data loss; no irrecoverable state change.** The architecture contained the defect even while the governance layer let it through.

---

## 5. Recommended Structural Mitigations

1. **[@risk-manager — Riven, R10 template owner]** Amend RA template (see RA-28-1 Decision 7 / §RISK-DISPOSITION-20260423-1 Q6d pattern for precedent) to add a pre-issuance **Decision-text call-graph check block**. Each Decision that makes a factual claim about system behavior (e.g., "X is idle", "Y uses Z", "A does not read from B") MUST cite a **code-path anchor** (file:line range or test name) that proves the claim by construction. Anchors from prior RAs are NOT automatically inherited — each fresh RA re-asserts the anchor, even when the Decision text is "IDENTICAL". This closes the responsibility seam without adding a new agent authority.

2. **[@qa — Quinn, chain-gate owner]** Extend the chain-gate 7-check matrix with a new check **"Inherited-Decision factual re-verification"**: for every Decision carried via "IDENTICAL to [prior RA]" marker, Quinn runs one grep or trace against the referenced code-path anchor and attaches the stdout/exit-code as evidence. A missing anchor OR a failed trace blocks DRAFT → ISSUED. This is strictly additive to the existing matrix; no existing check is relaxed.

3. **[@squad-auditor — Sable, this role]** Schedule a quarterly retrospective audit pass over all ISSUED RAs of the last quarter, specifically targeting "IDENTICAL" inheritance edges. Single pass = single markdown artifact under `docs/governance/`. No agent invocation, no code change, no RA mutation. Cadence catches any future class-of-defect analogous to this one before it accumulates to three hops.

4. **[@pm — Morgan, task orchestration]** Convert the 30.6-second empirical containment demonstrated by retry #4 into a **named governance asset**: "Canonical-state defense-in-depth held under a governance-level false rationale." This supports future scope-discipline decisions (Q6b narrow-scope, Q5 DEFER, Decision 7 scope-exclusion) by concretely showing the architectural containment works — governance corrections do not require emergency scope expansion.

---

## 6. Scope Boundary

**This audit does NOT cover:**

- **Individual agent blame.** Every agent acted in good faith with the information available at drafting time. Riven's RA-23-1 Decision 1 was cited, self-consistent, and structurally reasonable under Article IV at bibliographic level. Propagation was protocol-compliant. The defect is structural (responsibility seam + invariance-by-structure compiling to invariance-of-scrutiny), not personal.
- **Other Decision fields beyond Decision 1.** Decisions 2 (duration cap), 3 (pre-quiesce verifications), 4/4b (gate/drift check), 5 (invocation), 6 (restore), 7 (audit), 8 (hard bounds), 9 (constants) were not within this audit's scope. A follow-on audit may sample them if similar propagation patterns are suspected.
- **RA template editorial changes.** Recommended mitigations 1-2 propose behavioral/procedural changes; actual template-edit authority rests with Riven (R10, per RA-28-1 §RISK-DISPOSITION-20260423-1 Q6d). Any template edit MUST land via a separate sprint under that authority.
- **Validation of RA-28-1 sentinel-path workload correctness.** RA-28-1's Decision 3 inverts the RA-25-1 failure mode (sentinel UP required). Whether its call-graph claims hold empirically is Gage's responsibility at Stage-2 execution, not this audit's.
- **Code mutation.** Per constraints: zero touch to `core/memory_budget.py`, `data/manifest.csv`, any RA text, any test. Read-only audit.
- **Cross-agent invocation.** Per @squad-auditor authority: this audit produces one governance doc; downstream action is up to @pm / Riven / Quinn per their standing authority.

---

## Signature

Sable (@squad-auditor, The Investigator ♐) — 2026-04-24 BRT.

**Canonical invariant re-check at audit close (sha256sum at audit-write completion):**
- `data/manifest.csv` → `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` — **byte-identical to the RA-chain pinned value** (this audit did not touch it; confirmed).
- `core/memory_budget.py` → `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` — **byte-identical to the pre-audit observation**. Differs from the RA-28-1 Stage-2 flip-time value `51972c522c79d42718bb2037b7efd36cb2ec6a195b9f34eb2ce42bead391a0ac` (2026-04-24T18:36:22-03:00); this drift is **out of scope for this audit** (Sable does not mutate Python) and reflects legitimate downstream activity between Stage-2 flip and this audit's write time. Noted transparently for next reader.
- Hold-out lock `VESPERA_UNLOCK_HOLDOUT` — unset throughout this audit session (no data-layer code path exercised).

**Artifact-level sha256 commitment:** This file's sha256 will be computed by the next reader at consumption time. Governance file, not canonical data; sha will drift if any downstream consumer appends commentary.
