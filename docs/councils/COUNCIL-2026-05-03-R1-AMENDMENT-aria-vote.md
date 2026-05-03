# Aria Ballot — Council 2026-05-03 R1 Amendment

**Voter:** Aria (@architect)
**Date BRT:** 2026-05-03
**Vote:** APPROVE_WITH_CONDITIONS
**Ballot self-audit (Article IV):** every claim source-anchored to commit/file/line below.

## §1 Verdict + reasoning

R1 expansion 2023-01..2024-01 within the Phase 2C orchestrator framework + R14 spike-completion gate + R15 token-rename audit-trail is **architecturally defensible** as a BOUNDED EXECUTION ENVELOPE. Option B (subprocess.Popen + in-process monkey-patch of probe module-globals) preserves Article IV: the canonical probe artifact `scripts/dll_probe_2023_12_wdofut.py` is untouched on disk; reassignment occurs only on the ephemeral child process's import object (chunk_runner.py L98-113). Sable MA-01 INFO independently corroborates. Riven blocking caps (max-attempts=3, max-consecutive-failures=3, max-wall-time=23400s, max_qfd_global_pct=0.001) provide hard kill switches matching the 17.8x scope expansion. Anti-Article-IV Guards 1-8 unaffected (resolution §3, 0/8 affected; H_next window 2026-05..10 disjoint from backfill 2023-01..2024-01).

I cannot grant unconditional APPROVE because MA-10 is real: the Story T003.A2 AC1-AC10 references infrastructure that is partially aspirational (ChunkPlanner/ManifestStore as named modules, ValidateGate, recover_parquet_from_jsonl.py, generate_backfill_report.py do not exist as separately extracted artifacts; orchestrator + lib are functional but monolithic-ish). The amendment ratifies a WINDOW EXPANSION grounded in the Phase-2C prototype — that is acceptable, but the story must be retro-fitted as design target, not treated as a satisfied AC contract.

## §2 Conditions

1. **C1 (R15 token rename — BLOCKING):** before any further bulk chunk dispatch, `chunk_runner.py:49,67-72` and orchestrator override emission MUST update token from `ack_dara_aria_council_2026_05_01` to `ratified_council_2026_05_03_R1_amendment_quorum_<sha>` per amendment §2.3. Old token retained as no-op for 24h grace then removed. Docstring source-anchor mandatory.
2. **C2 (R14 gate enforced pre-A2):** S1-retry-0915 + 2023-03-15 qfd root-cause MUST land before A2-Dara dispatch (already in resolution §2.2, restate).
3. **C3 (Story retro-fit — NEEDS_REVISION on T003.A2):** Pax must downgrade T003.A2 AC1-AC10 from "Phase-2 implementation contract" to "Phase-3 hardening target" OR explicitly mark Phase-2C prototype as an interim acceptance state with a follow-on story (T003.A3) covering lib extraction + recover/report scripts. MA-10 cannot be silently absorbed.
4. **C4 (Cross-drive defense documented):** `_REPO_ROOT` monkey-patch at chunk_runner.py:111-113 acceptable as a precedent IF added to `feedback_profitdll_quirks.md` as canonical pattern Q-PATH-14-V (cross-drive Path coercion). Otherwise refactor probe to take `repo_root` param post-bulk.
5. **C5 (data-completeness classifier visible):** orchestrator's "ok if qfd=0 + reached_100=True + trades>=1M regardless of schema_pass" rule MUST be added to amendment §1.4 footnote and surface in manifest column `dll_outcome_class` so downstream A2-Dara/A3-Nova can re-classify if schema drift later detected.

## §3 Concerns + mitigations (per 7 audit points)

1. **Option B integrity:** PASS. chunk_runner.py:101-113,123 — patches `_OUTPUT_DIR`, `_HARD_TIMEOUT_S`, `_IDLE_WATCHDOG_S`, `_REPO_ROOT` then calls `probe.run_probe()` directly bypassing `_validate_args()` which is bound to `main()`. Probe file canonical artifact byte-equal. Mitigation: C4 documents the pattern.
2. **MA-10 AC gap:** CONCERN. `dll_backfill_lib.py` exists (1402L) but is mostly DLL plumbing + IncrementalParquetSink (L580); no `ChunkPlanner` class, no `ManifestStore` class, no `ValidateGate`, no `recover_parquet_from_jsonl.py`, no `generate_backfill_report.py`. Mitigation: C3 (story status correction).
3. **Architectural debt curve (4 shifts in 2 days):** ELEVATED but not blocking. Phase 1→2A→2B→2C is reactive iteration driven by 4 critical probe bugs (resolution §1.3) + Q-FIN-12-E novel quirk discovery. Each pivot was empirically forced, not speculative. Mitigation: freeze architecture post-amendment; any further pivot requires Council re-quorum.
4. **Cross-drive defense:** acceptable precedent with C4.
5. **Data-completeness classifier:** architecturally sound for bulk acquisition (auction-window tolerance is correct per probe's 25% aggressor lowering); but DOES carry mask-risk. Mitigation C5 (classifier surfaced + downstream re-classifiable).
6. **R15 token authorization:** I did NOT pre-authorize the literal token string `ack_dara_aria_council_2026_05_01` — it was inferred-attribution by the orchestrator author. Amendment §2.3 rename to quorum-anchored token is the correct audit-trail correction. Endorsed.
7. **Aria Option D detached launcher:** appropriate for 6h30 wall-time bulk (parent shell decoupling, heartbeat-based external supervision). Not over-engineered given Riven max-wall-time=23400s.

## §4 Architectural debt analysis (Option A → B → C trajectory)

| Phase | Date | Pivot trigger | Architectural cost |
|---|---|---|---|
| 1 (single probe) | 2026-05-01 | R1 letter constraint | LOW — bounded |
| 2A streaming sink | 2026-05-02 early | Mira IC pipeline + scale projection | MED — built then deprecated commit `b6e3a5b` |
| 2B orchestrator | 2026-05-02 late | 2A complexity + Article IV (probe untouchable) | MED — Option B pivot commit `c7b1423` |
| 2C caps + heartbeat | 2026-05-03 | Riven + bulk wall-time risk | LOW — additive |

Net: 1 deprecation (2A streaming sink), 0 rewrites. **Healthy reactive iteration**, not scope-creep — provided we freeze post-amendment (per C3 follow-on story discipline). Empirical findings (4 critical probe bugs) justified each pivot; speculative architecture would have been worse.

## §5 Source anchors

- Resolution: `docs/councils/COUNCIL-2026-05-03-R1-AMENDMENT-resolution.md` §1-§5
- Option B impl: `scripts/dll_backfill_chunk_runner.py:47-131` (commit `c7b1423`)
- Cross-drive patch: `scripts/dll_backfill_chunk_runner.py:111-113`
- Probe canonical: `scripts/dll_probe_2023_12_wdofut.py` (Council A1 R1 untouchable)
- Lib current state: `scripts/dll_backfill_lib.py` 1402L — `IncrementalParquetSink` at L580; ChunkPlanner/ManifestStore/ValidateGate absent (MA-10 corroborated)
- Story aspirational AC: `docs/stories/t003.a2.dll-backfill-orchestrator.story.md:23,72-78`
- Quirks: `feedback_profitdll_quirks.md` (Q-FIN-12-E pending; proposed Q-PATH-14-V via C4)
- Anti-Article-IV Guards 1-8: project memory `project_t002_6_round2_closure.md` + T002 RETIRE FINAL
- HEAD `b1802ac` branch `t003-a1-dll-probe-2023-12`

— Aria, architectural authority, ballot self-audited 2026-05-03
