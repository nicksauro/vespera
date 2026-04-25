# RA-20260428-1 Precondition Chain QA Gate — CONDITIONAL GREEN

**Reviewer:** Quinn (@qa, The Sentinel ♍)
**Date:** 2026-04-24 BRT
**Story / Spec:** RA-20260428-1 DRAFT issuance-precondition chain (`docs/architecture/memory-budget.md` L2240-2339) + ADR-1 v3 §Next-steps step 5/7 + ADR-4 Amendment 20260424-1 §14 + §RISK-DISPOSITION-20260423-1 Q6a/Q6d + RA-20260426-1 Q5 disposition + T002.4 merge commit `5a52ddd6b1e710d830977b08be832850a6697842`.
**Deliverables gated (DRAFT-level — governance text only, no code):**
1. §R10 Amendment block L2240-2339 (99 lines) — banner, metadata, authority, scope, ratification chain, 4 latent invariants, 7-row decision matrix, 4-row P-class precondition table, Next links, R10 custodial sign-off.
2. DRAFT → ISSUED flip preconditions P1-P4 structure + consumer-binding semantics.
3. Decision 6 Q6d Nyquist disposition (this-RA-scoped, child-telemetry-authoritative-by-construction).
4. Decision 7 scope-exclusion of canonical invariant anomaly (narrow-scope policy compliance).

**Verdict:** **CONDITIONAL GREEN** — 5 validation scopes all pass (structural soundness verified), 7 functional checks 7/7 PASS, canonical invariants intact, no scope leak from the Decision 7 excluded option (b) untrack-CRT path, P4 circularity resolved by Riven's Decision 6 self-disposition (child-telemetry-authoritative-by-construction) which structurally decouples P4 authorship from P1 numeric ratios. **Two minor CONCERNS** (R2-2 §R15 citation missing; R3-1 ADR-2 citation missing) are wording-tightening only and do not block DRAFT → ISSUED flip if Orion elects to proceed; Riven MAY elect to patch the two citations before flip for completeness. Single surgical wording pass optional.

---

## 5-Scope Validation Summary

| # | Scope | Result | Evidence |
|---|-------|--------|----------|
| 1 | Decision matrix completeness + rationale quality | **PASS** | All 7 rows (Defer-source / Streaming-refactor / Authorized-sentinel-invocation / No-ceiling-routing / Audit-extension / Q6d-disposition / Canonical-anomaly-exclusion) trace verbatim to prior artifacts: Decision 1 → Q6a §1 L2170; Decision 2 → RA-26-1 Q5 L2085-L2101 + agent-authority.md L59-L73 R10 split; Decision 3 → Q6a §1 + T002.4 `80805ac5`; Decision 4 → RA-26-1 Decision 5 precedent + ADR-1 v3 R5; Decision 5 → R3-1 additive rule; Decision 6 → Q6d L2204-L2214; Decision 7 → Q6b §3 rationale L2188. Each row has explicit precondition + rationale + pass-criterion + fail-criterion columns populated with testable criteria. No ungrounded rows. No invented agent authorities or thresholds. |
| 2 | P1-P4 executability + evidence plan | **PASS** | P1 evidence is dual-artifact (`p1-streaming-refactor-commit.txt` + `p1-dara-cosign.md`) with explicit R10 co-sign verdict wording mandated ("R10 custodial co-sign: APPROVED" citing parity to `build_raw_trades_cache.py:_stream_month_to_parquet`). P2 is a standard Quinn gate file path with green-all-signals criteria (pytest ≥ baseline, ruff + mypy clean, zero blockers). P3 is a measurable round-trip smoke test (30s cache-path, non-null non-zero `peak_pagefile_bytes` + `peak_wset_bytes`, wrapper CSV/JSON passthrough byte-identity). **P4 circularity disposition:** accepted per Riven's Decision 6 — since child-side telemetry is authoritative-by-construction for this RA (kernel monotonic counters), P4 is a **documentation** precondition not a computational gate; post-P1 authorship is therefore structurally acceptable because the Q6d ratio is advisory here, not gating. |
| 3 | Latent risks R1-1/R2-1/R2-2/R3-1 wording + downstream traceability | **PASS with minor CONCERNS** | R1-1 enumerates 3 byte-identical constants explicitly (`CAP_ABSOLUTE_v3 = 8_400_052_224`, `R4_threshold_v3 = 9_473_794_048`, `emergency_kill_threshold_v3 = 7_980_049_613`) with sha256 pre/post validation on every step-7 commit. R2-1 cites kernel-maintained `PROCESS_MEMORY_COUNTERS_EX.PeakPagefileUsage` / `.PeakWorkingSetSize` via T002.4 commit `80805ac5` — kernel monotonic max counters are structurally the input, not poll-derived. R2-2 BRT-naive contract cites L1838 issuance-metadata pattern + Whale/Sentinel DB contract but does **NOT** cite §R15 explicitly — see CONCERNS-01. R3-1 additive-only cites SUMMARY_JSON_FIELDS immutability + frozen `peak_wset_bytes` / `peak_pagefile_bytes` names — but does **NOT** reference ADR-2 schema — see CONCERNS-02. Substantive enforcement content is sound in both cases; only citation wording is imprecise. |
| 4 | Q6d Nyquist precondition application | **PASS** | Decision 6 L2286 text binds Q6d application **to this RA's Aug-2024 sentinel-path invocation only** ("child runtime is expected to be multi-hour … this RA MUST cite child-side peak telemetry as the primary peak-measurement source"). Parent polling `--poll-seconds=30` is **retained for reactive R5 WARN/KILL gating only**; `peak_commit_aug2024` for step-7 is sourced from `TELEMETRY_CHILD_PEAK_EXIT.peak_pagefile_bytes`. Not a standing policy change — no template-artifact amendment required; binds this RA. Future baselines under future RAs each re-apply Q6d independently. Scoping is correct. |
| 5 | R10 dual-agent custodial co-sign mechanic (Decision 2) | **PASS — clear** | Mechanic is structurally self-contained: Dex authors commit on main (visible in git), Dara reviews the committed diff (symmetric visibility — both see same bytes), Dara produces explicit markdown file `p1-dara-cosign.md` with mandated "R10 custodial co-sign: APPROVED" verdict citing streaming-pattern parity. Decision 2 fail-criterion explicitly authorizes Dara to block: "if Dara DOES NOT co-sign → R10 violation, halt, escalate". Rejection authority is symmetric with approval authority. Diff visibility is post-commit (Dara reviews landed code, not a draft), which matches the `build_raw_trades_cache.py` §13.1 precedent where Dara co-signs the committed streaming helper. No ambiguity. |

---

## 7-Check Functional Summary (standard pattern)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Requirements traceability | PASS | Every decision, precondition, and invariant cites a prior governance artifact with file + line reference (ADR-1 v3 step 5/7; ADR-4 §14; §RISK-DISPOSITION Q6a/Q6b/Q6c/Q6d L2156-L2236; RA-26-1 Q5 L2085-L2101; T002.4 merge `5a52ddd6` + telemetry commit `80805ac5`; agent-authority.md L59-L73 for R10 territorial split). Full traceability matrix is the Decision Matrix itself + Latent Invariants block. No orphaned element. |
| 2 | Test execution (DRAFT-level) | PASS | N/A for governance-only DRAFT text; P2 evidence plan explicitly requires "pytest PASS count ≥ current baseline; ruff + mypy clean" at refactor-time — sensible, matches RA-26-1 A5 acceptance pattern. T002.4 already merged on main carries the telemetry mechanism under its own QA gate — dependency satisfied upstream. |
| 3 | Security / correctness review | PASS | DRAFT text contains zero code; zero `eval`/`exec`; zero hardcoded secrets; zero path-traversal surfaces; all proposed refactor scope (Decision 2) is to canonical `scripts/materialize_parquet.py:_fetch_month_dataframe` with streaming pattern already security-reviewed under RA-26-1 §13.1 gate (parameterized SQL, holdout guard, `_reject_canonical_aliases`). |
| 4 | Parity considerations | PASS | Decision 2 fail-criterion explicitly enumerates parity invariants: "Refactor regresses any existing sentinel-path invariant (schema, ordering, row count, BRT-naive timestamps) → halt". Pattern-source `build_raw_trades_cache.py:_stream_month_to_parquet` has verbatim coercion-mirroring precedent (RA-26-1 INFO-02 cited 21,058,318-row pilot byte-identical at 210.89 MiB). Parity is mandated at P2 gate. |
| 5 | Contract consistency | PASS | Refactored output parquet MUST be schema-identical to current `_fetch_month_dataframe` output (implicit in parity fail-criterion, Decision 2). R2-2 BRT-naive timestamp contract is latent invariant. R3-1 additive-only JSON key contract is latent invariant. No contract mutation authorized. |
| 6 | Performance impact | PASS | Refactor goal is memory reduction (accumulating Python list → streaming `pq.ParquetWriter.write_table` per-batch), not speed. Decision 2 rationale explicitly identifies "Python-list accumulation that produces the 11.8 GiB WS workload (ADR-4 §13 trigger)" as root-cause target. RA-26-1 §13.1 pilot evidence (210.89 MiB peak WS at 21M rows, ~3.4 min elapsed) establishes the streaming pattern is memory-thrift without speed regression — refactor inherits that profile. |
| 7 | Article IV (No Invention) | PASS | R10 custodial sign-off block L2323 explicitly claims Article IV compliance: "every decision traces to one of: ADR-1 v3 §Next-steps … ADR-4 §14 … §RISK-DISPOSITION-20260423-1 Q6a/Q6b/Q6c/Q6d … RA-20260426-1 Q5 disposition … or T002.4 merge commit". Independent audit of all 7 decisions + 4 invariants + 4 preconditions confirms every clause traces. No invented thresholds (all constants quoted byte-literal from prior artifacts). No invented agent authorities (R10 territorial split cites agent-authority.md L59-L73). |

---

## Findings

### Blockers
**None.** (Canonical `data/manifest.csv` sha256 unchanged; Decision 7 scope-exclusion is hermetic — no leak of the disposed-out option (b) CRT untracking into RA-28-1 text; R10 custodial mechanic self-contained; Q6d disposition internally coherent.)

### Concerns
- **CONCERNS-01 — [R2-2] BRT-naive contract does not cite §R15 or equivalent enforcement mechanism.** L2274 text establishes the contract ("any step-7 artifact … MUST emit BRT-naive timestamps") and cites L1838 issuance-metadata pattern + Whale/Sentinel DB contract as precedent, but does not cite a specific R-series enforcement rule. Remediation: one-line addition pointing to the actual BRT-naive enforcement locus (either §R15 if it exists, or the `feed_timescale.load_trades` tz-naive assert, or the R2-2 invariant declaration itself as self-binding). Not blocking — substantive enforcement content is sound. Informational quality improvement.

- **CONCERNS-02 — [R3-1] Additive-only JSON keys does not reference ADR-2 schema.** L2275 text establishes frozen names `peak_wset_bytes`/`peak_pagefile_bytes` and the additive-only rule but does not cite ADR-2 (referenced in the gate brief as the canonical schema authority). Remediation: one-line citation "per ADR-2 schema additive-only discipline" or equivalent. Not blocking — R3-1 is self-binding even without upstream citation (SUMMARY_JSON_FIELDS immutability is stated directly).

### Informational
- **INFO-01 (positive).** P4 circularity is resolved *by construction* in Decision 6: because child-side telemetry is authoritative (kernel monotonic counters), the Q6d ratio check is advisory not gating for this RA. Riven's Decision 6 disposition ("child-peak telemetry is authoritative by construction") structurally decouples P4 evidence authorship from P1 refactor numerics — P4 becomes a **documentation** precondition, not a computational gate. This is architecturally clean and Quinn accepts it without requiring a deferred P4 synthesis step.
- **INFO-02 (positive).** Decision 7 scope-exclusion is hermetic: 5-point rationale (core deliverable focus, cross-cutting orthogonality, narrow-scope policy, R1-1 sha256 validation independent of git, no `core/memory_budget.py` or `data/manifest.csv` mutation in this RA's execution) + explicit escalation requirement ("RA amendment required, not permitted unilaterally") closes the disposed-out option (b) CRT untracking path completely. No leak.
- **INFO-03 (positive).** Canonical invariant `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at gate session start; Riven's drafting session preserved canonical discipline (edit scoped to `memory-budget.md` only).
- **INFO-04 (positive).** P1 dual-artifact evidence pattern (`p1-streaming-refactor-commit.txt` + `p1-dara-cosign.md`) with explicit R10 verdict wording mandated is a stronger precondition shape than RA-26-1 single-artifact P1-P5 — raises the R10 territorial-split bar and codifies Dara's veto authority in evidence form. Good precedent for future canonical-producer-surface RAs.
- **INFO-05 (positive).** Format precedent compliance: DRAFT banner structure, decision-matrix columns, evidence P-class table, R10 custodial sign-off, References block — all match RA-20260426-1 ISSUED block (L1832-L2151) structurally. Orion's flip mechanic will be pattern-identical.
- **INFO-06.** memory-budget.md post-DRAFT sha256 = `b3e004b344deb1b2b78981c695b0eb99382be19bed54848ccfae173847de44ad` matches Riven's authored expected value — zero drift between drafting commit and gate session.

---

## Decision Rationale

Riven's RA-28-1 DRAFT is structurally sound at the governance level. All 7 decisions trace to prior artifacts; all 4 latent invariants enumerate concrete enforcement mechanisms; all 4 P-class preconditions have testable evidence shapes with named owners and consumers. The R10 dual-agent custodial co-sign mechanic (first of its kind per Riven's flag) is unambiguous: Dex authors, Dara co-signs via explicit markdown verdict file, rejection authority is symmetric, diff visibility is post-commit symmetric. The P4 circularity that Riven flagged is resolved by Decision 6's "child-telemetry-authoritative-by-construction" disposition — which structurally decouples P4 evidence authorship from any post-P1 numeric dependency, because the Q6d ratio becomes advisory once child telemetry is the authoritative peak source. The Decision 7 scope-exclusion of the canonical invariant anomaly is hermetic: the 5-point rationale, the narrow-scope policy citation (Q6b §3 L2188), and the explicit escalation clause ("RA amendment required, not permitted unilaterally") prevent any leak of the disposed-out option (b) untrack-CRT path into this RA's authority envelope. The two CONCERNS (R2-2 §R15 citation, R3-1 ADR-2 citation) are wording-tightening only — substantive enforcement content is self-binding even without the upstream citations. Gate: **CONDITIONAL GREEN**. Orion may flip DRAFT → ISSUED without remediation; Riven MAY elect to patch the two minor citations pre-flip for completeness. Canonical sha guard unbroken.

---

## Recommendation for Orion (DRAFT → ISSUED)

**CONDITIONAL GREEN.** Orion may flip DRAFT → ISSUED immediately per the flip_procedure pattern (L1835) with Riven-delegated authority citation, subject to:
1. P1-P4 evidence packet completion (structural DRAFT gate passes regardless; P1-P4 satisfaction is a separate executable gate on ISSUED-state consumption, not on the DRAFT text itself).
2. Optional: Riven patches CONCERNS-01 + CONCERNS-02 citation tightening (single-line edits to L2274 + L2275). Not blocking.

**Downstream ordering confirmed:** Orion flips → Dex+Dara land P1 refactor + co-sign → Quinn P2 gate on refactor → Gage P3 smoke test → Riven P4 Nyquist documentation → Orion re-flip ISSUED with evidence packet attached → Gage executes Decision 3 (one-shot sentinel-path baseline) → Dex populates `core/memory_budget.py` step-7 CEILING_BYTES.

**Latent risks for Orion to carry:**
- P1 refactor MUST preserve Aug-2024 pilot parity (schema, ordering, row count 21,058,318, BRT-naive) — if P2 gate exposes regression, revert + new drafting session.
- P3 smoke test wrapper CSV/JSON passthrough byte-identity is the single binding proof that telemetry survives end-to-end — brittle surface; any wrapper change between now and P3 invalidates.
- Decision 3 requires `sentinel-timescaledb` container UP (inverse of RA-26-1 Decision 1 which required DOWN). Gage MUST confirm container health at invocation time.
- Decision 6 mandates step-7 commit cites `TELEMETRY_CHILD_PEAK_EXIT.peak_pagefile_bytes` as derivation source — any step-7 commit citing parent-polled `commit_bytes` instead is a Q6d violation requiring revert.
- Decision 7 separate R15 hardening story is @pm parallel action — NOT downstream-blocking from Quinn PASS — Orion does not gate on it.

---

**Signature:** Quinn (@qa, The Sentinel ♍), 2026-04-24 BRT.
**Canonical sha guard:** `data/manifest.csv` sha256 = `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` verified byte-identical at gate session open (pre-edit only — this gate does not modify canonical data).
**Governance file sha:** `docs/architecture/memory-budget.md` sha256 = `b3e004b344deb1b2b78981c695b0eb99382be19bed54848ccfae173847de44ad` at gate session open — matches Riven's authored post-edit expected value (zero drift).
**Hold-out lock:** `VESPERA_UNLOCK_HOLDOUT` unset throughout session.
**Next gate:** on ISSUED-state, P2 gate on canonical streaming refactor diff (Quinn @qa), per Decision 2 pass-criterion.
**Next agent:** **Orion (aiox-master)** for DRAFT → ISSUED flip per flip_procedure pattern L1835 — CONDITIONAL GREEN clears Orion to proceed. (Riven optionally patches CONCERNS-01 + CONCERNS-02 citation tightening pre-flip.)
