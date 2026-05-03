# Pax (@po) ballot — Council 2026-05-03 Schema Resolution + R16

**Voter:** Pax (@po) — story-locus / AC traceability authority
**Date (BRT):** 2026-05-03
**Lens:** Where does the work live? What is the cleanest audit trail?

---

## Vote: **Option A** — Defensive minimum (preserve storage 10-col + project + naive cast at consumption)

## R16: **CONCUR** (ratify)

---

## §1 Story-locus adjudication (per option)

| Option | Story locus | Rationale |
|---|---|---|
| **A** | **NEW T003.A4** (projection layer) — distinct from T003.A3 | Projection + cast is a NEW concern not covered by T003.A3 ACs (which are pure structural extraction of existing prototype primitives). Mixing projection logic into A3 contaminates AC7 (zero-regression refactor) — projection is *additive behaviour*, not refactor. New story = clean audit. |
| B | T003.A4 (Dara remap) **+ T003.A5** (Nelo translate-map probe) — two stories | Two distinct authority domains (DLL probing vs storage join); separating preserves owner-clarity and parallelism. |
| C | T003.A2 **re-execution** (NOT a new story) under R1' bound amendment | Re-download IS the original A2 acquisition envelope — same story, expanded amendment §0.6. |
| D | T003.A4 minimal-cast (lightweight, ~2h) | Same locus as A but smaller AC scope (cast only, no projection layer). |

**A is cleanest** because: storage stays untouched (custodial preserved), projection is a single new module with bounded ACs, no entanglement with A3 lib-extraction (which is already gated on A2 bulk closure + Quinn verdict).

## §2 AC traceability — does T003.A3 absorb projection?

**No.** T003.A3 has 7 ACs, all binary-verifiable, all scoped to **extracting existing prototype primitives** (ChunkPlanner, ManifestStore, ValidateGate, recovery, report, schema bump, no-regression). AC7 explicitly mandates *"no semantic mutation"* — adding a projection+cast layer IS semantic addition. Forcing projection into A3 would:

1. Violate AC7 zero-regression invariant.
2. Mix two concerns (refactor vs new feature) — AIOX Constitution Article III (story-driven) prefers atomic stories.
3. Inflate A3 estimate beyond the named 3-5 sessions.

Projection layer deserves **separate AC scope** in a new T003.A4 story authored by Dara (storage owner) with consumer-side projection ACs.

## §3 R16 implication on story shape

**Inline reference, NOT a new principle-story.** R16 is a governance principle (like R5/R6/R10), not a deliverable. Pattern precedent: R1-R15 live in council ledger and are referenced inline by stories that touch their domain. T003.A4 should cite R16 in its **Source / Authority basis** header (one line) and in any AC that codifies preservation behaviour. No standalone "principle story" needed; that would be over-engineering and dilute the principle.

## §4 Pax 10-point checklist applied to Option A → T003.A4

| # | Point | Status | Note |
|---|---|---|---|
| 1 | Clear title | CLEAR | "Schema projection + naive cast at consumption (T003.A2 → A3 boundary)" |
| 2 | Complete description | CLEAR | F1-F5 mapping table from Dara A2 audit is the spec |
| 3 | Testable AC | CLEAR | parity tests vs Sentinel canonical 7-col + cast invariants |
| 4 | Scope IN/OUT | CLEAR | IN: projection module + casts. OUT: re-download, broker remap |
| 5 | Dependencies | CLEAR | A2 bulk completion + R16 ratified |
| 6 | Complexity | CLEAR | ~4-6h Dara per council |
| 7 | Business value | CLEAR | unblocks A3/A4-Mira/A5-Sable chain |
| 8 | Risks | **CONCERN** | Risk: zero-pad agent encoding misleads downstream — must be documented + Sable [DIVERGENCE] register entry if H_next-1 later flips flow-based |
| 9 | DoD | CLEAR | 7-check Quinn gate + Sable audit |
| 10 | PRD/Epic alignment | CLEAR | T003 epic preserved |

**Score: 9/10 CLEAR + 1 CONCERN (documented, not blocking).** GO verdict.

---

## §5 Final position

- **Option A** — minimum-regret, fastest unblock, preserves optionality via R16 custodial storage.
- **R16 CONCUR** — codifies the principle user already enacted; future councils will benefit.
- **Story:** open T003.A4 (Dara) post-council; cite R16 inline. T003.A3 unchanged.
- **If A4-Mira later thesis demands brokers:** convene mini-council to escalate to Option B/C — storage is preserved, no re-download wasted.

— Pax (@po), 2026-05-03 BRT
