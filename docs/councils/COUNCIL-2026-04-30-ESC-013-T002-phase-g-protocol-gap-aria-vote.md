---
council: ESC-013
council_topic: T002 Phase G protocol-compliance gap (post-Mira F2-T9 sign-off-round3 INCONCLUSIVE_phase_g_protocol_compliance_gap)
voter: Aria @architect
voter_authority: System architecture; factory pattern + closure isolation + spec-yaml threshold guardianship; engineering-placement bindings; F2-T0b round 1 + F2-T0b' round 2 archi review precedence
date_brt: 2026-04-30
mode: autonomous
branch: t002-1-bis-make-backtest-fn (working tree)
verdict: APPROVE_PATH_iv (Protocol-corrected Phase G re-run — Beckett N8.1 ~3-3.5h with ~5-10 LoC Dex caller wiring fix)
verdict_secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback ONLY if Path (iv) blocked by independent governance (e.g., Riven 14-day Path C trigger fires per ESC-012 minority dissent)
verdict_relationship_to_esc012: REFINEMENT_OF_PATH_B — Path (iv) is Path B "completed under correct protocol"; not a new path, a procedural fix to the Phase G run that was attempted under Phase F protocol
inputs_consumed:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md (Mira F2-T9 sign-off-round3 INCONCLUSIVE verdict — F2-T9-OBS-1)
  - docs/ml/specs/T002-gate-4b-real-tape-clearance.md §15.13 (Phase G unlock protocol — pre-authored)
  - docs/governance/PRR-20260430-1-T002.7-phase-g-disposition.md (Phase G prep coherence audit anchor)
  - scripts/run_cpcv_dry_run.py (current caller — `:1093 holdout_locked=True` hardcoded)
  - packages/vespera_metrics/cpcv_aggregator.py:251-309 (`compute_ic_from_cpcv_results` — `holdout_locked` parameter exposed; `ic_holdout_status` flip authored)
  - scripts/_holdout_lock.py (UNLOCK_ENV_VAR + assert_holdout_safe contract)
  - docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md §1.3 + §6.1 C-G1..C-G6 (own prior vote — Path B conditions)
inputs_NOT_consumed_pre_cast:
  - docs/councils/COUNCIL-2026-04-30-ESC-013-* OTHER agents (independent ballot — task discipline)
constraint_acknowledged:
  - F2-T9-OBS-1: Beckett N8 attempted Phase G window but executed Phase F protocol (`holdout_locked=True` hardcoded + `--phase F` CLI flag) → IC_holdout_status='deferred' → K3 DEFERRED-sentinel; surprise PASS on K1 (DSR=0.965) + K2 (PBO=0.163) + K3 robust in-sample (IC=0.866) but K3 decay sub-clause NOT honored
  - Mira F2-T8-T1 spec §15.13.12 sign-off chain + §15.13.2 unlock mechanism wiring task surfaced AFTER Phase G run as protocol gap
  - Sable R5 audit scope did NOT explicitly flag F2-T8-T1 as PRE-condition for Beckett N8 launch (Sable surface excluded caller-wiring tasks pre-baseline-run)
  - ESC-012 R6/R7/R8/R9 reusability invariants DEMAND: same engine_config + spec yaml + cost atlas + rollover + Bonferroni n_trials=5 + latency + RLP + microstructure flags + predictor↔label IDENTICAL — i.e. one-shot OOS discipline preserved
spec_yaml_version_under_protection: T002-v0.2.3 (DSR>0.95 / PBO<0.5 / IC>0 — Anti-Article-IV Guard #4 UNMOVABLE)
factory_pattern_provenance: T002.1.bis APPROVE_OPTION_B (Aria 2026-04-28); preserved verbatim through T002.6 + Phase F2 + Phase G(Phase-F-protocol) N8
holdout_lock_provenance: Anti-Article-IV Guard #3 — hold-out window [2025-07-01, 2026-04-21] is structurally MATERIALIZED (data-engineering ingestion) per `materialize_holdout_parquet.py` + AUDIT-2026-04-30-T002.7 §6 — but STATISTICAL UNLOCK only happens at runtime via `compute_ic_from_cpcv_results(holdout_locked=False)` per spec §15.13.2; N8 ATTEMPTED but DID NOT execute the statistical unlock (left `holdout_locked=True` default flowing)
prior_vote_self_consistency_disclosure: Aria voted APPROVE_PATH_B (ESC-012); cosigned C-G1..C-G6 conditions; Path (iv) is the SAME ballot, just procedurally completed; consistency preserved
---

# ESC-013 Aria Architectural Vote — T002 Phase G protocol-compliance gap adjudication

> **Authority basis:** Aria @architect under AIOX agent-authority matrix (system architecture decisions, technology selection, integration patterns, factory pattern + closure isolation guardianship, spec yaml threshold guardianship). Per the ESC-013 council framing, Aria adjudicates **FROM SYSTEM DESIGN**: factory pattern preservation across the protocol-corrected re-run; closure body untouched; spec yaml v0.2.3 thresholds untouched; cost atlas/rollover/latency/RLP all reused; the only delta is **caller-side wiring** in `scripts/run_cpcv_dry_run.py` toggling pre-authored `holdout_locked=False` parameter path (Mira spec §15.13.2) under explicit `--phase G` CLI flag with `VESPERA_UNLOCK_HOLDOUT=1` env affordance.
>
> **Self-consistency disclosure:** Aria voted APPROVE_PATH_B in ESC-012 with conditions C-G1..C-G6 binding (`docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md` §6.1). Path (iv) IS Path B's procedural completion. C-G1 specifically mandated "Phase G hold-out unlock MUST be gated by an explicit `phase: G` parameter in `scripts/run_cpcv_dry_run.py` AND emit `holdout_unlocked: true` in `determinism_stamp.json`". F2-T9-OBS-1 surfaces that this exact condition was not satisfied at N8 launch; Path (iv) closes that condition.
>
> **Discipline:** Aria did NOT read other ESC-013 agent votes pre-cast (task mandate). Independent ballot.

---

## §1 Verdict + rationale (architectural)

### §1.1 Verdict

**APPROVE_PATH_iv** — Protocol-corrected Phase G re-run (Beckett N8.1) with Dex caller-wiring fix (`scripts/run_cpcv_dry_run.py` ~5-10 LoC + maybe 3-5 LoC `compute_ic_from_cpcv_results` phase-consistency assertion).

Secondary acceptable: **APPROVE_PATH_C** (Retire T002) — Pax fallback ONLY IF independent governance blocks Path (iv) within Riven's 14-calendar-day window from ESC-012 minority dissent (i.e., latest 2026-05-14 BRT). Aria does NOT see governance blockers in the Path (iv) trace; the cost is small + fully bounded.

### §1.2 Rationale (architectural — three lenses, ESC-012 carry-forward)

**Lens 1 — Spec yaml v0.2.3 threshold UNMOVABILITY (Anti-Article-IV Guard #4).**

- Path (iv): ZERO mutation. The thresholds DSR>0.95 / PBO<0.5 / IC>0 + CI95_lower>0 + decay (IC_holdout > 0.5 × IC_in_sample per spec §15.13.5) apply to the protocol-corrected re-run UNCHANGED. Bonferroni n_trials=5 carry-forward (ESC-012 R6/R7 + spec §15.13.3). NO new trial slots. NO threshold relaxation. K3 decay sub-clause activates honestly for the first time when `ic_holdout_status='computed'` propagates per §15.13.2.
- Path C: ZERO mutation. Spec yaml frozen as forensic record + institutional artifact bequest (ESC-012 §3.2 + §3.3 inventory).

**Verdict on Lens 1:** Path (iv) and Path C are equivalently safe under Guard #4. (Path A' was rejected in ESC-012; not in scope here.)

**Lens 2 — Factory pattern preservation (T002.1.bis APPROVE_OPTION_B).**

- Path (iv): ZERO closure body touch. The `make_backtest_fn` factory contract (R/O captures `enclosed_costs / enclosed_calendar / enclosed_percentiles`; per-fold P126 D-1 invariant `as_of_date == min(test_events.session)` at `cpcv_harness.py:~1009`; mutually-exclusive engine guard at `engine.py:~206-211`) is NOT modified. The fix is exclusively at the **post-fanout caller** site — `scripts/run_cpcv_dry_run.py:1088-1116` — flipping `holdout_locked=True → False` under the `phase=='G'` branch and adding the `--phase G` CLI choice. The Aria F2-T0b' Option D placement design specifically authored `compute_ic_from_cpcv_results` window-agnostic so this single-parameter flip suffices to switch IS/OOS semantics WITHOUT closure-body refactor.
- Path C: closure body preserved verbatim as forensic record.

**Verdict on Lens 2:** Path (iv) preserves the factory contract identically to Path C. The 8/8 PRESERVED cross-check table in F2-T0b' applies UNCHANGED to N8.1.

**Lens 3 — Hold-out lock contract (Anti-Article-IV Guard #3).**

- Path (iv): the hold-out lock is a TWO-LAYER contract:
  1. **Data-engineering layer** (file-level): `scripts/_holdout_lock.assert_holdout_safe` + `VESPERA_UNLOCK_HOLDOUT=1` env affordance — already authorized for parquet materialization per AUDIT-2026-04-30-T002.7 §6; this is "data ingestion completeness", NOT statistical unlock.
  2. **Statistical layer** (runtime aggregation): `compute_ic_from_cpcv_results(holdout_locked=False)` per Mira spec §15.13.2 — flips `ic_holdout_status: 'deferred' → 'computed'` so the K3 decay sub-clause activates honestly.
  N8 honored layer 1 (parquet was materialized; data was read; the heavy CPCV fan-out completed) but DID NOT honor layer 2 (caller hardcoded `holdout_locked=True` at `:1093` regardless of phase). Path (iv) closes the layer-2 gap. The unlock is **canonical** per ESC-012 R10 single-shot OOS discipline + Anti-Article-IV Guard #3 honored by intent.
- Path C: hold-out lock preserved, BUT the parquet has already been materialized (data-engineering layer consumed); statistical layer never consumed in Phase G context (Phase F protocol absorbed the run). The window is partially "spent" in the file-system sense and "unspent" in the statistical sense. Path C accepts this asymmetry as the cost of forensic-record-only retirement.

**Verdict on Lens 3:** Path (iv) is the canonical use of the locked window per ESC-012 §1.3. Path C is acceptable but leaves the statistical disambiguation forever unresolved despite the parquet already being materialized — strictly inferior information-per-effort.

### §1.3 Why Path (iv) is architecturally optimal

The terminal architectural question — surfaced by Mira F2-T5 round 2 (`costed_out_edge`) and partially answered by Mira F2-T9 round 3 (K1+K2 surprise PASS on the materialized hold-out window under Phase F protocol; K3 DEFERRED-sentinel) — remains: **does the K3 decay sub-clause hold under honest `ic_holdout_status='computed'` propagation?** That is the disambiguation the entire ESC-012 council voted to fund. N8 surprise PASS on K1+K2 RAISES the stakes (more material that the hold-out window may carry signal), making the K3 decay activation MORE essential, not less.

Path (iv) consumes ONE additional Beckett session (~3-3.5h wall N7-prime baseline; reproducibility receipts 8/9 IDENTICAL to N8 except `phase: G` + `holdout_unlocked: true` + `ic_holdout_status: 'computed'` — see §6 conditions C-iv1..C-iv6) + ONE small Dex commit (~5-10 LoC) + small Aria thin archi cross-check (this ballot's §3 baseline; no new review document needed beyond cosign on the post-N8.1 verdict chain). Net Architecture risk = ZERO.

### §1.4 Why Path (iv) is NOT a new vote

ESC-012 ratified APPROVE_PATH_B 5/6 supermajority. Path (iv) is the SAME path executed under SAME conditions C-G1..C-G6 with the protocol gap fixed. Not a new path, not a re-vote on strategy fate. ESC-013 is a **procedural** council, not a strategy-fate council. Aria's vote here is consistency with ESC-012 vote — recasting it would be inconsistent (would either rescind the original vote on procedural grounds, which is governance-opportunistic, or rubber-stamp the original vote, which is procedurally redundant).

What ESC-013 IS adjudicating: did the F2-T9-OBS-1 protocol gap warrant a Path-C retirement instead of a re-run? Aria position: NO — the gap is bounded, the fix is small, the architectural surface is unchanged, the information value of the protocol-corrected run is exactly what ESC-012 voted to fund.

### §1.5 Why Path C remains acceptable as fallback

Path C (Retire T002) preserves all impl artifacts as forensic record + institutional knowledge, zero new code. ESC-012 §6.2 conditions C-R1..C-R3 already authored. Architectural cost is zero. BUT: forfeits the OOS K3 decay measurement that the entire council voted to extract.

Path C IS the correct fallback IF:
- Riven's 14-calendar-day Path C trigger fires (i.e., Phase G N8.1 not executed by 2026-05-14 BRT due to independent governance blocker — Mira spec amendment delay, Quinn QA gate hold, Beckett wall-time conflict). This is the ESC-012 minority dissent compromise preserved intact.
- Independent governance (Mira spec authority, Pax forward-research bandwidth, Riven §9 HOLD #2 ledger authority) raises a NEW concern not visible in this F2-T9-OBS-1 trace.
- Aria architectural review of Mira G-spec amendment surfaces a previously-unseen factory contract risk requiring full re-design (not expected; Path (iv) is precisely the cheap-by-design case).

In the absence of those triggers, Path C is **strictly inferior** information-per-effort vs Path (iv). The bandwidth difference is ~3-3.5 hours Beckett wall + ~30 min Dex + ~30 min Quinn ≈ < 1 calendar day total.

---

## §2 Implementation cost per path (LoC + sessions)

### §2.1 Path (iv) implementation cost

**Code (LoC):**

| Surface | LoC delta | Session count | Authority |
|---|---|---|---|
| `scripts/run_cpcv_dry_run.py` — argparse `--phase` choice expansion `["E", "F"] → ["E", "F", "G"]`; `phase=='G'` branch toggles `holdout_locked=False` at `:1093` (existing call site, just replace literal `True` with `phase == 'G' ? False : True` semantic via local var); also gate the `assert_holdout_safe` env-var bypass with explicit operator banner | ~5-10 LoC | 1 Dex session (~30-45 min) | Dex (F2-T8-T1 — Mira spec §15.13.12 binding) |
| `scripts/run_cpcv_dry_run.py` — emit `holdout_unlocked: true` field on the `events_metadata.json` + ensure determinism stamp absorbs `phase: G` provenance (DeterminismStamp may already absorb it via Beckett T0 schema; verify; if not, additive 2-3 LoC in `_serialize_determinism_stamp` or upstream stamp construction) | ~3-5 LoC | merged into above session | Dex |
| `packages/vespera_metrics/cpcv_aggregator.py:compute_ic_from_cpcv_results` — OPTIONAL phase-consistency soft assertion (e.g., issue warning when `holdout_locked=False` AND no Phase G context flag passed; design choice; LOW priority — not strictly needed since the caller already routes the flag correctly under `--phase G`; OPTIONAL ~3-5 LoC defensive guard, NOT mandatory for N8.1 to run) | ~0-5 LoC | optional; same Dex session | Dex (Aria recommended NOT to add — keep cpcv_aggregator window-agnostic per F2-T0b' Option D design; phase-coupling at the aggregator level violates Lens 2 isolation) |
| `tests/cpcv_harness/test_run_cpcv_dry_run.py` (or analog) — assert `--phase G` + `VESPERA_UNLOCK_HOLDOUT=1` together flip `holdout_locked=False` AND `events_metadata.holdout_unlocked == True`; assert `--phase F/E` preserves `holdout_locked=True` (regression guard) | ~30-50 LoC (1-2 new test cases + parametrize) | 1 Quinn session (~30-45 min) merged with Dex | Quinn (F2-T8-T2/T3) |
| Beckett N8.1 baseline run (Phase G full, protocol-corrected) | 0 new code; Beckett executes against unlocked window with `--phase G` flag + `VESPERA_UNLOCK_HOLDOUT=1` + correct `holdout_locked=False` propagation | 1 Beckett session (~3-3.5 h wall — IDENTICAL to N7-prime/N8 wall per reusability invariants ESC-012 R6) | Beckett (F2-T8-T4) |
| Mira F2-T9 round 4 (or F2-T10) sign-off on N8.1 — IC_holdout PASS/FAIL determination + K3 decay sub-clause activation; verdict format identical to F2-T5 round 3 schema with `ic_holdout_status: 'computed'` cell flipped | 0 code; sign-off doc ~80-150 LoC | 1 Mira session (~1.5-2 h) | Mira (spec authority) |
| Aria thin archi cross-check on N8.1 (verify reproducibility 8/9 IDENTICAL except `phase: G` + `holdout_unlocked: true` + `ic_holdout_status: 'computed'`; verify factory contract preservation 8/8 PRESERVED — this very ballot already covers §3 baseline) | 0 code; thin archi cosign ~50-100 LoC if separate document, or absorbed into existing F2-T8-T0b ledger entry | 0.5 Aria session (~30-45 min) | Aria (per F2-T0b' protocol; condition C-G4 of ESC-012 §6.1) |
| Riven §9 HOLD #2 disarm-ledger update on Mira F2-T9-r4/F2-T10 verdict — atomic AND-conjunction format per Aria F2-T0b §6.1 condition C-A7 | ~50-100 LoC ledger entry | 0.5 Riven session | Riven |
| Pax F2-T9-r4 / F2-T10 / G-T6 close — story update + epic status | ~50-100 LoC | 0.5 Pax session | Pax |

**Total Path (iv):**
- **Net new code:** ~5-10 LoC strictly mandatory in `scripts/run_cpcv_dry_run.py` (argparse + branch + metadata field). Optional defensive ~3-5 LoC at `compute_ic_from_cpcv_results` NOT recommended (architectural noise; see §6 condition C-iv-NEG-1). Test surface ~30-50 LoC. Total mandatory: **~35-60 LoC across 2 source files.**
- **Sessions:** ~5-6 agent sessions across 5 agents (Dex F2-T8-T1 → Quinn F2-T8-T2/T3 → Beckett N8.1 → Aria thin cross-check → Mira F2-T9-r4/F2-T10 → Riven + Pax close).
- **Wall time:** ~0.75-1 calendar day (Dex+Quinn parallelizable ~1h; Beckett N8.1 serial ~3-3.5h; Aria+Mira post-baseline 1-2h; Riven+Pax close ~0.5h).
- **Risk surface:** ZERO structural — factory pattern UNCHANGED + closure isolation UNCHANGED + spec yaml UNCHANGED + cost atlas UNCHANGED + latency model UNCHANGED + RLP UNCHANGED + Bonferroni n_trials UNCHANGED + per-fold P126 D-1 UNCHANGED + mutually-exclusive engine guard UNCHANGED + DeterminismStamp 9-field receipt absorbs additive `phase: G` + `holdout_unlocked: true` cleanly. The only delta is a **single boolean flip + new CLI choice + audit-trail metadata field**.

### §2.2 Path C implementation cost (carry-forward from ESC-012 §2.3)

**Net new code: 0 LoC.**

| Surface | LoC delta | Session count |
|---|---|---|
| Pax T002 deprecation story / EPIC-T002.0 close | ~100-150 LoC story + epic status | 1 Pax session (~1 h) |
| Riven §9 HOLD #2 ledger entry — Gate 4b NEVER passes; T002 retired with `costed_out_edge` partial falsification + F2-T9 INCONCLUSIVE protocol-gap addendum (NEW: explicit acknowledgement that K1+K2 PASS observed under Phase F protocol but K3 decay sub-clause never tested due to gap-and-decline-to-rerun choice) | ~50-100 LoC ledger row + addendum | 0.5 Riven session |
| Aria architectural reusability inventory (`docs/architecture/T002-impl-artifacts-bequest.md` per ESC-012 C-R1) | ~150 LoC | 1 Aria session (~1-2 h) |
| Mira post-mortem closure (research-log update; thesis-falsification-depth notation + protocol-gap acknowledgement) | ~50-100 LoC | 0.5 Mira session |

**Total Path C:** 0 net new code; ~3 sessions; ~0.5-1 calendar day; ZERO risk; CONSUMED data-engineering layer of hold-out (parquet materialized) but UNCONSUMED statistical layer (forfeit by choice).

### §2.3 Cost-comparison table (Path iv vs Path C)

| Path | Net new LoC | Sessions | Wall time | Spec-yaml mutation risk | Hold-out budget — data layer | Hold-out budget — statistical layer | Information value (terminal disambiguation) |
|---|---|---|---|---|---|---|---|
| **(iv)** Phase G protocol-corrected re-run | ~35-60 (5-10 mandatory script + 30-50 tests) | ~5-6 | ~0.75-1 day | NONE | CONSUMED (parquet materialized; idempotent re-read) | CONSUMED canonically (single-shot per ESC-012 R9; `holdout_locked=False` propagated honestly) | HIGH — terminal K3 decay sub-clause activation; full disambiguation `costed_out_edge` vs partial-OOS-deployable; honors ESC-012 vote intent |
| **C** Retire T002 | 0 | ~3 | ~0.5-1 day | NONE | CONSUMED (already materialized; can't unspend) | UNCONSUMED (forfeit by choice — asymmetric loss) | LOW — preserves forensic record but FORFEITS the K3 decay measurement that ESC-012 voted to extract; surprise N8 K1+K2 PASS makes this forfeit MORE costly, not less |

**Architectural verdict on cost:** Path (iv) is the highest-information-per-effort option BY FAR given the F2-T9 trace (K1+K2 surprise PASS RAISES the stakes for K3 decay measurement). Path C accepts a forfeit of demonstrably-now-more-valuable disambiguation. Path A' was rejected at ESC-012 and not in scope.

---

## §3 Reusability assessment

### §3.1 Impl artifact inventory carry-forward (ESC-012 §3.1 verbatim)

All artifacts catalogued in ESC-012 §3.1 — `cpcv_aggregator + info_coef + bootstrap_ci + latency_dma2_profile + rollover_calendar + RLP detection + auction.exit_price_rule + microstructure flags (circuit_breaker_fired, cross_trade) + factory pattern + closure isolation R/O captures + per-fold P126 D-1 invariant + mutually-exclusive engine guard + BacktestResult.content_sha256 byte-stability + Determinism stamp 9-field receipt + Toy-benchmark Bailey-LdP harness` — apply IDENTICALLY here. None of these surfaces is touched by Path (iv).

### §3.2 Reusability scoring per path

**Path (iv) — MAXIMAL REUSE.**

The single delta is at the post-fanout caller in `scripts/run_cpcv_dry_run.py`. Specifically:
- `cpcv_aggregator.compute_ic_from_cpcv_results` REUSED verbatim — receives `holdout_locked=False` instead of `=True`; the same code path executes; `ic_holdout_status` flips `'deferred' → 'computed'` per the existing branch at `cpcv_aggregator.py:309`. Aria F2-T0b' Option D placement design is exactly the canonical use case here (window-agnostic by authorship).
- `info_coef.ic_spearman + bootstrap_ci` REUSED verbatim.
- `BacktestRunner` + `CPCVEngine` + `make_backtest_fn` factory + closure body REUSED verbatim — N8.1 fan-out is byte-identical to N8 (same window, same data, same seed, same engine_config, same atlas, same calendar, same n_trials).
- `latency_dma2_profile` + RLP detection + microstructure flags + auction rule REUSED verbatim per engine-config v1.1.0 carry-forward.
- Per-fold P126 D-1 invariant REUSED verbatim (same train slices for same `--in-sample-start/--in-sample-end` window).
- Mutually-exclusive engine guard REUSED verbatim.
- DeterminismStamp 9-field receipt: 8/9 fields IDENTICAL to N8 (engine_config_sha256, spec_sha256, cost_atlas_sha256, rollover_calendar_sha256, cpcv_config_sha256, python/numpy/pandas versions, seed=42, dataset_sha256 IDENTICAL since same window). The 1/9 difference is `phase: G` (was `phase: F` in N8) + `holdout_unlocked: true` (was `false` in N8) — both additive, both audit-trail.

**Reusability cost: ZERO refactor. Net surface change: single boolean flip + CLI choice expansion.**

**Path C — MAXIMAL PRESERVATION as institutional bequest.** Same as ESC-012 §3.2 Path C verbatim.

### §3.3 Cross-path reusability verdict

Path (iv) is the canonical Aria F2-T0b' Option D use case — the entire reason the orchestration helper was placed in `vespera_metrics` (separate from the harness) was precisely so that the `holdout_locked` flag flip suffices to switch IS/OOS semantics. The protocol-corrected re-run is THE design exercise. Path C preserves the inventory unconsumed but at the asymmetric cost of forfeiting the now-higher-value K3 disambiguation.

---

## §4 Spec yaml v0.2.3 mutation risk per path (Anti-Article-IV Guard #4)

### §4.1 Risk matrix

| Path | DSR/PBO/IC threshold mutation risk | n_trials=5 mutation risk | AC9 sample-size mutation risk | Other spec-yaml mutation risk | Mira spec amendment scope |
|---|---|---|---|---|---|
| **(iv)** | NONE — same thresholds apply to OOS evaluation per spec §15.13.5; K3 decay sub-clause activation is PRE-AUTHORED in spec §1 + parent §6 K3 row + §15.13.5 (no amendment needed for activation; only for honest `ic_holdout_status='computed'` propagation) | NONE — n_trials=5 carry-forward per ESC-012 R6 + spec §15.13.3 | NONE — Phase G window has its own session count; spec §6 + R9 floor applies UNCHANGED | NONE — protocol-corrected re-run preserves spec yaml v0.2.3 verbatim | ZERO new amendment needed; spec §15.13 IS the pre-authored amendment for Phase G unlock; F2-T8-T1 wiring is impl-side (Mira spec §15.13.12 sign-off chain); ESC-013 resolution language may add F2-T9-OBS-1 root-cause acknowledgement to research-log but NOT to spec yaml |
| **C** | NONE — spec yaml frozen as forensic record | NONE | NONE | NONE | NONE |

**Architectural verdict on Guard #4 risk:** Path (iv) and Path C are equivalently safe at ZERO mutation risk. The Phase G unlock semantics + K3 decay sub-clause activation are PRE-AUTHORED in spec §15.13 (per ESC-012 R2 ratification + spec amendment v1.2.0 §15.13 NEW); Path (iv) merely IMPLEMENTS what the spec already prescribes. This is the cleanest possible Guard #4 trace.

### §4.2 Why this is NOT a re-amendment

Spec §15.13.2 verbatim:

```python
ic_result = compute_ic_from_cpcv_results(
    results,
    seed_bootstrap=42,
    n_resample=10000,
    holdout_locked=False,  # Phase G unlock: holdout=AVAILABLE
)
```

Path (iv) implements EXACTLY this code at the caller site. The spec is authority-of-record; Path (iv) brings the impl into alignment. ESC-013 resolution can append a research-log note acknowledging F2-T9-OBS-1 as the protocol-compliance gap and Path (iv) as the closure, but no spec yaml v0.2.3 mutation is required.

---

## §5 Hold-out lock contract per path

### §5.1 Two-layer contract restated

The hold-out lock at the Algotrader system level is a TWO-LAYER contract per AUDIT-2026-04-30-T002.7 §6.4 + spec §15.13.1:

| Layer | Mechanism | Authority | Path (iv) state | Path C state |
|---|---|---|---|---|
| **Layer 1 — Data ingestion (file-level)** | `scripts/_holdout_lock.assert_holdout_safe` raises `HoldoutLockError` unless `VESPERA_UNLOCK_HOLDOUT=1` env set | R1 + R15(d) ratified at story T002.0a; carried to materialization per `scripts/materialize_holdout_parquet.py:32-40` | Layer 1 ALREADY honored — parquet was materialized for N8 with explicit `VESPERA_UNLOCK_HOLDOUT=1` operator action; idempotent re-read for N8.1 (no new env-var grant; no new operator authorization needed; data is on disk) | Layer 1 ALREADY honored (same parquet materialization); CONSUMED |
| **Layer 2 — Statistical aggregation (runtime)** | `compute_ic_from_cpcv_results(holdout_locked=False)` flips `ic_holdout_status: 'deferred' → 'computed'` per spec §15.13.2 | Mira spec §15.13.2 + Anti-Article-IV Guard #3 (canonical use of locked window) | Layer 2 NOT yet honored under Phase G context (N8 hardcoded `holdout_locked=True` regardless of phase); Path (iv) closes this gap explicitly via the `--phase G` branch in `scripts/run_cpcv_dry_run.py` | Layer 2 NEVER honored under Phase G context (forfeit by choice); spec §15.13.2 is pre-authored but never triggered |

### §5.2 Path (iv) authorized unlock protocol

Per Mira spec §15.13.2 PRE-AUTHORED (not new mutation; not Aria invention; cosigned at ESC-012 R2):

- **Layer 1 affordance:** existing `VESPERA_UNLOCK_HOLDOUT=1` env-var mechanism per `scripts/_holdout_lock.py:42-43` — re-used; no new env-var; no new bypass mechanism.
- **Layer 2 mechanism:** the new Python kwarg `holdout_locked: bool = True` on `compute_ic_from_cpcv_results` per `cpcv_aggregator.py:251-256`, FLIPPED to `False` under the `phase=='G'` branch by the Dex caller-wiring fix in `scripts/run_cpcv_dry_run.py`. Mira spec §15.13.2 is the authority; Aria F2-T0b' Option D cosigned the placement of the kwarg at the orchestration helper (not at the harness factory) precisely so this flip is window-agnostic.
- **Auditability:** `events_metadata.json` field `holdout_unlocked: true` + DeterminismStamp `phase: G` provenance ensure the unlock is post-hoc auditable. Operators reading the artifact dir IMMEDIATELY see the protocol-corrected status (cf. N8 artifact `events_metadata.holdout_unlocked: false` despite the Phase G window — that asymmetry was the F2-T9-OBS-1 surface symptom).

### §5.3 Path (iv) is NOT a new mutation

The hold-out lock contract is NOT being modified by Path (iv). Layer 1 mechanism unchanged. Layer 2 mechanism IS the pre-authored spec §15.13.2 path. The Dex commit BRINGS THE CALLER INTO COMPLIANCE WITH THE PRE-AUTHORED SPEC. This is implementation-pulling-up-to-spec, NOT spec-being-rewritten. Anti-Article-IV Guard #3 is honored by canonical use (single-shot OOS per ESC-012 R9; explicit phase=G + holdout_unlocked=true audit trail; identical predictor↔label per ESC-012 R7).

### §5.4 Path C hold-out lock state

Path C: hold-out window's data layer remains consumed (parquet materialized once for N8; idempotent on disk), and statistical layer remains UNCONSUMED forever for T002. The asymmetry persists — Riven §9 HOLD #2 ledger entry SHOULD note this asymmetry honestly per Aria condition C-R3 (ESC-012 §6.2). Future researchers inheriting the unconsumed statistical-layer hold-out budget for the SAME window will face Bonferroni-multiplicity question (the materialized data has already been observed once at K1+K2 level); Aria recommends Path C ledger entry surface this nuance for honest accounting.

---

## §6 Personal preference disclosure

**Aria personal preference (transparent for council):** APPROVE_PATH_iv.

**Rationale:** Aria architectural philosophy = minimum-disruption + maximum-information per-effort. Path (iv) is a 5-10 LoC fix that closes the F2-T9-OBS-1 protocol gap and unlocks the K3 decay sub-clause measurement that the entire ESC-012 council voted to extract. Path C forfeits a measurement that has been MORE costly to forfeit since N8 surprise-passed K1+K2.

**Bias disclosure (carry-forward + new):**

- **ESC-012 carry-forward bias:** Aria authored F2-T0b APPROVE_OPTION_D placement design specifically so `compute_ic_from_cpcv_results` is window-agnostic and consumes any `cpcv_results` (in-sample OR holdout) without refactor. Path (iv) is the canonical use case for that design (cosigned at ESC-012). Same bias from prior vote, unchanged.
- **Self-consistency bias (ESC-013-specific):** Aria voted APPROVE_PATH_B with conditions C-G1..C-G6; flipping to Path C now on procedural grounds would be inconsistent with that conditional commitment. Aria flags this as a potential bias toward Path (iv) and counter-checks: would Aria still vote (iv) if Path (iv) cost were higher? Counter-check: if the Dex fix were ~50-200 LoC OR if the architectural surface required factory-pattern modification OR if the spec yaml required a true v0.2.3 → v0.3.0 mutation, Aria would re-evaluate. The current cost is 5-10 LoC + a single boolean flip; this is well below the bias-trip threshold.
- **Authorship-history bias:** Aria F2-T0b'-style cross-check on N8.1 reproducibility receipt would be a 2nd Aria archi review document (or absorbed thin cosign on ledger). This is light-weight + canonical per F2-T0b' protocol. No new authorship ambition introduced.

**Counter-bias check passed.** Path (iv) preference holds independent of authorship history.

**Acknowledgement of council authority:** Aria votes Path (iv) but defers to:
- Pax @po forward-research authority on the bandwidth allocation question (Riven 14-day Path C trigger window per ESC-012 minority dissent);
- Mira @ml-researcher spec authority on F2-T9-OBS-1 closure language (Aria does NOT pre-empt Mira F2-T10 verdict scope);
- Riven @risk-manager ledger authority on Gate 4b OOS verdict format post-N8.1 (Aria conditions C-G6 ESC-012 carry-forward apply).

If Pax determines (per ESC-011 R10) that the squad's research bandwidth is better spent on a different epic AND Riven 14-day window expires AND Path (iv) is not executed by 2026-05-14 BRT, Path C becomes the right answer — and Aria would cosign Path C with conditions C-R1..C-R3 from ESC-012 §6.2 + a NEW C-R4 acknowledging the F2-T9-OBS-1 protocol-gap forfeit per §5.4 above.

---

## §7 Recommended conditions

If Path (iv) wins ESC-013, Aria binds the following architectural conditions on the Phase G N8.1 protocol-corrected re-run chain. These EXTEND ESC-012 C-G1..C-G6 (which remain in force) and add ESC-013-specific procedural conditions:

### §7.1 Aria conditions for Path (iv) (NEW C-iv1..C-iv6 — extend ESC-012 C-G1..C-G6)

| ID | Condition | Stage bound | Severity |
|---|---|---|---|
| **C-iv1** | `scripts/run_cpcv_dry_run.py` argparse `--phase` MUST extend `choices=["E", "F"] → ["E", "F", "G"]`. The `phase=='G'` branch MUST: (a) toggle `holdout_locked=False` at the existing `compute_ic_from_cpcv_results(...)` call site (`:1088-1102` insertion zone preserved); (b) require `VESPERA_UNLOCK_HOLDOUT=1` env affordance OR raise `HoldoutLockError` at the `assert_holdout_safe` guard (existing mechanism per `_holdout_lock.py:103-137` — no new env-var); (c) emit explicit operator banner "PHASE G HOLD-OUT UNLOCK ACTIVE — single-shot OOS per ESC-012 R9" to stderr at start; (d) emit `events_metadata.holdout_unlocked: true` field; (e) emit DeterminismStamp `phase: G` field if not already absorbed (verify via Beckett T0 schema). This DIRECTLY satisfies ESC-012 condition C-G1. | Dex F2-T8-T1 (impl) + Quinn F2-T8-T2/T3 (test) | **HIGH** |
| **C-iv2** | The Dex commit MUST NOT touch (a) `make_backtest_fn` factory contract, (b) closure body, (c) per-fold P126 D-1 invariant, (d) mutually-exclusive engine guard, (e) `BacktestResult.content_sha256` byte-stability, (f) `cpcv_aggregator.compute_ic_from_cpcv_results` body beyond strictly-defensive optional phase-consistency assertion. Specifically REJECT phase-coupling at the aggregator level — keep `compute_ic_from_cpcv_results` window-agnostic per Aria F2-T0b' Option D design. The single boolean-flip-at-caller pattern is the architectural intent; preserve it. | Dex F2-T8-T1 (impl) + Aria thin cross-check | **HIGH** |
| **C-iv3** | Beckett N8.1 baseline run MUST preserve 8/9 reproducibility receipt fields IDENTICAL to N8 (engine_config_sha256, spec_sha256, rollover_calendar_sha256, cost_atlas_sha256, cpcv_config_sha256, python/numpy/pandas versions, seed=42, dataset_sha256 — the latter MUST match because the underlying parquet is the same materialized hold-out; the per-event predictor/label arrays MUST match byte-for-byte modulo the `holdout_locked=False` propagation flipping `ic_holdout_status` and activating decay test). The 1/9 difference is `phase: G` + `holdout_unlocked: true` + `ic_holdout_status: 'computed'` + `K3_decay_passed` populated (was None / DEFERRED-sentinel under N8). Beckett N8.1 baseline report MUST include cross-check table analog to N7-prime §3.3 + N8 §3.3 with a NEW row "ic_holdout_status: deferred → computed" + "K3_decay sub-clause: SENTINEL → ACTIVATED". This DIRECTLY extends ESC-012 condition C-G5. | Beckett F2-T8-T4 (run + report) | **HIGH** |
| **C-iv4** | F2-T5-OBS-1 verdict-layer enforcement (decay-clause short-circuit on `ic_holdout_status='deferred'`) — verify that this fix WAS landed pre-N8 (Mira F2-T9 round 3 §4 + Beckett N7-prime §6.2 anchor). If not landed, Path (iv) is GATED on this fix landing first (Dex F2-postmerge follow-up per ESC-012 C-G2). If landed, verify it correctly handles the new `ic_holdout_status='computed'` propagation at N8.1 — i.e., `evaluate_kill_criteria` MUST evaluate the K3 decay sub-clause honestly (not short-circuit) when status is 'computed', and emit `K3_FAIL_decay` IF `IC_holdout < 0.5 × IC_in_sample` per spec §15.13.5. This DIRECTLY extends ESC-012 condition C-G2. | Dex (verify landed) + Quinn (regression test) | **HIGH** |
| **C-iv5** | Aria thin archi cross-check on N8.1 reproducibility receipt — MAY be absorbed into the F2-T8-T0b ledger entry per spec §15.13.12 (no new full archi review document required); OR authored as a thin standalone cosign ~50-100 LoC. Format MUST follow F2-T0b'-style 8/8 PRESERVED + 1/N delta-table convention. ESC-012 conditions C-G3 (Mira G-spec amendment) is NOT triggered for ESC-013 because spec §15.13 is already authored — only the F2-T9-OBS-1 protocol-gap acknowledgement may need a Mira F2-T10 sign-off addendum to the existing F2 sign-off-round3 document (Mira authority — Aria does NOT pre-empt). | Aria thin archi cross-check (~30-45 min) | MEDIUM |
| **C-iv6** | Riven §9 HOLD #2 disarm-ledger update on Mira F2-T10 verdict for N8.1 — atomic AND-conjunction format per Aria F2-T0b §6.1 condition C-A7 + ESC-012 C-G6. If N8.1 yields `GATE_4_PASS` (DSR > 0.95 AND PBO < 0.5 AND K3 in-sample PASS AND K3_decay_passed = True), Riven entry references Gate 4a HARNESS_PASS + Gate 4b N7-prime + Phase G N8.1 OOS confirmation; preserves R5/R6 fence to Gate 5; T002.7 paper-mode bandwidth opens. If N8.1 yields `GATE_4_FAIL_decay` (DSR + PBO PASS but K3_decay_passed = False — i.e., IC_holdout < 0.5 × IC_in_sample), Riven entry: Gate 4b confirmed FAIL on decay sub-clause; T002 retired with full institutional record; Anti-Article-IV Guard #3 honored by canonical use of single-shot OOS budget; the `costed_out_edge` thesis is empirically clarified — IS-only edge but OOS decay; future researchers inherit honest accounting. If N8.1 yields surprise `GATE_4_PASS` on K3 decay AND consensus K1+K2 carry-forward, ESC-014 council convenes for Gate 5 paper-mode T002.7 disposition. This DIRECTLY extends ESC-012 condition C-G6 with the F2-T9-OBS-1 trace closure language. | Riven F2-T10 (ledger authority) + Pax adjudication on T002.7 vs Path C terminal | **MEDIUM** |

### §7.2 Aria NEGATIVE conditions (DO-NOT for Path (iv))

| ID | Negative condition (DO-NOT) | Rationale |
|---|---|---|
| **C-iv-NEG-1** | DO NOT add phase-coupling at `compute_ic_from_cpcv_results` aggregator level (e.g., do NOT add a `phase` kwarg to the function signature). The function MUST remain window-agnostic per Aria F2-T0b' Option D design. The phase-coupling stays at the caller site (`scripts/run_cpcv_dry_run.py`); the aggregator merely receives the boolean `holdout_locked` flag. This preserves Lens 2 closure-isolation philosophy at the orchestration-helper level too. | Architectural philosophy preservation; F2-T0b' design intent |
| **C-iv-NEG-2** | DO NOT extend `--phase G` to also activate any new strategy-side surface (regime filter, conviction threshold change, signal ensemble). Phase G is single-shot OOS confirmation per ESC-012 R7 — predictor↔label IDENTICAL to F2 + Bonferroni n_trials=5 carry-forward. ESC-013 is procedural; do NOT smuggle Path A' refinement under cover of the protocol fix. | ESC-012 R7 + Anti-Article-IV Guard #4 |
| **C-iv-NEG-3** | DO NOT re-run additional sweeps after N8.1 (e.g., "if N8.1 fails K3 decay, try `phase=='G2'` with adjusted threshold"). Path (iv) is single-shot per ESC-012 R9; if it fails, Riven §9 HOLD #2 entry routes to Gate 4b confirmed-FAIL + T002 retired. Re-running would constitute IS-fit on hold-out and violate Anti-Article-IV Guard #3. | ESC-012 R9 + Anti-Article-IV Guard #3 |
| **C-iv-NEG-4** | DO NOT touch spec yaml v0.2.3. The protocol-corrected re-run honors PRE-AUTHORED spec §15.13. ESC-013 resolution language can append a research-log note acknowledging F2-T9-OBS-1 root cause (Sable R5 audit scope did not flag F2-T8-T1 as PRE-condition) without spec yaml mutation. | Anti-Article-IV Guard #4 |

### §7.3 Aria conditions for Path C (extend ESC-012 §6.2 C-R1..C-R3)

If Path C wins ESC-013 (Aria reject stance preserved; condition surface for completeness):

| ID | Condition | Stage bound | Severity |
|---|---|---|---|
| **C-R4 (NEW)** | Aria architectural reusability inventory document (ESC-012 C-R1) MUST EXTEND with explicit acknowledgement that the hold-out window data-engineering layer was CONSUMED via parquet materialization for N8 + N8.1-could-have-been but the statistical-layer was UNCONSUMED by retire-clean choice. Future researchers MUST be informed that the materialized parquet has been observed once at K1+K2 aggregate level (N8 surprise PASS) — i.e., a related-strategy researcher inheriting this artifact must consider Bonferroni-multiplicity nuance for any subsequent OOS measurement against the SAME window. | Aria | MEDIUM |
| **C-R5 (NEW)** | Mira post-mortem closure (ESC-012 C-R2) MUST surface F2-T9-OBS-1 protocol-gap as the PROXIMATE cause of T002 retire-clean (not the strategy thesis itself; the thesis remains in `costed_out_edge`-or-OOS-confirmable suspended state). Honest research-log accounting per Article IV. | Mira | MEDIUM |

---

## §8 Article IV self-audit

| Claim in this vote | Source anchor (verified in this session) |
|---|---|
| Mira F2-T9 sign-off-round3 INCONCLUSIVE_phase_g_protocol_compliance_gap verdict | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` frontmatter `verdict` + §1 + §3 trace; F2-T9-OBS-1 surfaced |
| K1 DSR=0.965 + K2 PBO=0.163 + K3 in-sample IC=0.866 (robust) but K3 DEFERRED-sentinel under Phase F protocol | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3.md` frontmatter `n8_holdout_locked_observed: True` + §1 narrative; cross-check spec §15.13.2 PRE-AUTHORED unlock mechanism |
| Caller hardcoded `holdout_locked=True` at `scripts/run_cpcv_dry_run.py:1093` | Direct file inspection in this session — line 1093 verbatim `holdout_locked=True,` inside `if phase == "F":` branch (no `phase == "G"` branch exists) |
| `compute_ic_from_cpcv_results(..., holdout_locked: bool = True)` signature with `ic_holdout_status: 'deferred' if holdout_locked else 'computed'` flip authored | Direct file inspection — `packages/vespera_metrics/cpcv_aggregator.py:251-309` verbatim |
| `_holdout_lock.assert_holdout_safe` + `VESPERA_UNLOCK_HOLDOUT=1` env affordance pre-existing | Direct file inspection — `scripts/_holdout_lock.py:103-137` verbatim |
| Spec §15.13.2 Phase G unlock mechanism PRE-AUTHORED with `holdout_locked=False` Python kwarg + ic_holdout_status='computed' propagation | Direct file inspection — `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:936-949` verbatim |
| Spec §15.13.5 K3 decay sub-clause `IC_holdout > 0.5 × IC_in_sample` activates under Phase G context | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:982-992` |
| Spec §15.13.7 single-shot OOS discipline (ESC-012 R9) | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:1005-1009` |
| Reusability invariants per ESC-012 R6 (engine_config + spec yaml + cost atlas + rollover + Bonferroni n_trials=5 + latency + RLP + microstructure flags IDENTICAL F2 N7-prime) | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:960-971` cross-check table |
| Predictor↔label IDENTICAL F2 per ESC-012 R7 | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:973-980` |
| ESC-012 5/6 SUPERMAJORITY APPROVE_PATH_B + Riven minority dissent 14-day Path C trigger | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:921-932` + `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` (referenced) |
| Aria APPROVE_PATH_B with C-G1..C-G6 conditions | `docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-aria-vote.md` §1 + §6.1 |
| F2-T8-T1 Dex caller-wiring task estimate (~10-20 LoC) | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:1070` verbatim |
| F2-T8-T0b Aria archi review small scope ("only `holdout_locked` flag flip + `--phase G` CLI flag") | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:597-598 + 704` verbatim |
| Aria F2-T0b' Option D design — `compute_ic_from_cpcv_results` window-agnostic | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md:949` "Aria Option D — `vespera_metrics` orchestration module"; cross-ref `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` §5.1 (per ESC-012 §1.4 + §3.1) |
| Anti-Article-IV Guard #3 (NO touch hold-out lock); Guard #4 (Gate 4 thresholds UNMOVABLE); Guard #8 (verdict-layer status provenance + InvalidVerdictReport) | ESC-012 §7 + spec §15.5 + Mira sign-off-round3 §9 cross-check |
| Two-layer hold-out lock contract (data-engineering layer + statistical layer) | `docs/audits/AUDIT-2026-04-30-T002.7-phase-g-prep-coherence.md:113 + 131 + 172` verbatim language ("Materialization is data-engineering preparation, NOT statistical unlock; runtime unlock acontece via `holdout_locked=False` in `compute_ic_from_cpcv_results` per spec §15.13.2") |

**Article IV self-audit verdict:** every architectural claim in this vote traces to (a) Mira F2-T9 sign-off-round3 §-anchor, (b) Mira spec v1.2.0 §15.13 §-anchor, (c) ESC-012 resolution + Aria own ballot §-anchor, (d) AUDIT-2026-04-30-T002.7 §-anchor, OR (e) direct repo file inspection in this session (`scripts/run_cpcv_dry_run.py:1088-1102` + `packages/vespera_metrics/cpcv_aggregator.py:251-309` + `scripts/_holdout_lock.py:103-137`). **NO INVENTION. NO threshold mutation. NO Mira spec body mutation. NO factory contract refactor. NO engine signature change. NO closure isolation break. NO new env-var. NO new bypass mechanism. NO Path A' refinement smuggling.**

The vote does NOT pre-empt:
- Pax @po forward-research authority (bandwidth allocation; Riven 14-day Path C trigger window).
- Mira @ml-researcher spec authority (F2-T9-OBS-1 closure language; F2-T10 verdict on N8.1; any spec §15.13 amendment if needed for ESC-013 trace acknowledgement — Aria does NOT think it is needed but defers).
- Riven @risk-manager ledger authority (Gate 4b OOS verdict reclassification per N8.1 outcome; §9 HOLD #2 disarm-ledger entry format).
- Beckett @backtester baseline-run authority (N8.1 execution; reproducibility receipt cross-check).
- Quinn @qa quality-gate authority (Phase G test surface; Phase F regression guard).
- Dex @dev implementation authority (engineering details of caller wiring fix; argparse choice extension; test additions).
- Gage @devops Article II push-exclusivity (no commit / push by this vote per task discipline).

---

## §9 Aria cosign 2026-04-30 BRT — ESC-013 Phase G protocol-gap ballot

```
Authority: Aria (@architect) — system architecture + factory pattern + closure isolation + spec yaml threshold guardianship
Council: ESC-013 — T002 Phase G protocol-compliance gap (post-Mira F2-T9 INCONCLUSIVE_phase_g_protocol_compliance_gap)
Vote: APPROVE_PATH_iv (Protocol-corrected Phase G re-run; Beckett N8.1 ~3-3.5h with Dex caller-wiring fix ~5-10 LoC)
Vote secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback IF Riven 14-day Path C trigger fires (latest 2026-05-14 BRT)
Vote relationship to ESC-012: REFINEMENT_OF_PATH_B — same ballot procedurally completed; not a new vote, not a re-vote
Mode: autonomous; voter did NOT consult other ESC-013 agent votes pre-cast (task discipline)

Architectural rationale (3 lenses; ESC-012 carry-forward):
  Lens 1 — Spec yaml v0.2.3 threshold UNMOVABILITY (Anti-Article-IV Guard #4):
           Path (iv) + Path C: ZERO mutation risk; thresholds preserved verbatim; spec §15.13 PRE-AUTHORED.
  Lens 2 — Factory pattern preservation (T002.1.bis APPROVE_OPTION_B):
           Path (iv): ZERO closure body touch; single boolean flip at caller per Aria F2-T0b' Option D design.
           Path C: closure body preserved as forensic record.
  Lens 3 — Hold-out lock contract (Anti-Article-IV Guard #3 — two-layer):
           Path (iv): Layer 1 already honored (parquet materialized via existing VESPERA_UNLOCK_HOLDOUT=1); Layer 2
           closed canonically by flipping holdout_locked=False per spec §15.13.2 PRE-AUTHORED mechanism.
           Path C: Layer 1 already consumed; Layer 2 forfeit by choice (asymmetric loss; surprise N8 K1+K2 PASS makes
           the forfeit more costly).

Implementation cost (per §2 detailed table):
  Path (iv): ~5-10 LoC mandatory (scripts/run_cpcv_dry_run.py argparse + branch + metadata field) + ~30-50 LoC tests;
             ~5-6 sessions; ~0.75-1 calendar day; ZERO factory refactor; ZERO closure body touch; ZERO spec yaml mutation;
             single boolean flip + new CLI choice.
  Path C: 0 net new LoC; ~3 sessions; ~0.5-1 calendar day; ZERO risk; CONSUMED data layer; UNCONSUMED statistical layer.

Reusability (per §3):
  Path (iv) MAXIMALLY REUSES — every artifact in ESC-012 §3.1 inventory consumed verbatim; cpcv_aggregator + info_coef +
  bootstrap_ci + latency_dma2 + rollover_calendar + RLP + microstructure flags + auction rule + factory pattern + closure
  isolation R/O captures + per-fold P126 D-1 + mutually-exclusive engine guard + BacktestResult.content_sha256 +
  DeterminismStamp 9-field receipt — all UNCHANGED. Single delta: caller-side phase=='G' branch.
  Path C MAXIMALLY PRESERVES as institutional bequest (ESC-012 §3.2 verbatim).

Spec yaml v0.2.3 mutation risk (Anti-Article-IV Guard #4):
  Path (iv): NONE — implements PRE-AUTHORED spec §15.13 verbatim; ESC-013 resolution may append research-log
             F2-T9-OBS-1 root-cause acknowledgement WITHOUT spec yaml mutation.
  Path C: NONE — spec yaml frozen as forensic record.

Hold-out lock contract per path:
  Path (iv): Layer 1 affordance VESPERA_UNLOCK_HOLDOUT=1 EXISTING mechanism — re-used; no new env-var; no new bypass.
             Layer 2 mechanism holdout_locked=False kwarg PRE-AUTHORED in Mira spec §15.13.2 — flipped at caller per
             Aria F2-T0b' Option D design. Anti-Article-IV Guard #3 honored by canonical use (single-shot OOS per
             ESC-012 R9; explicit phase=G + holdout_unlocked=true audit trail; identical predictor↔label per ESC-012 R7).
             NOT a new mutation; implementation-pulling-up-to-spec.
  Path C: Layer 1 already consumed; Layer 2 forfeit by choice; Riven §9 HOLD #2 ledger SHOULD note asymmetry honestly
          (NEW C-R4).

Conditions bound IF Path (iv) wins (C-iv1..C-iv6 EXTEND ESC-012 C-G1..C-G6):
  C-iv1 (HIGH) — argparse --phase choice ["E","F"] → ["E","F","G"]; phase=='G' branch toggles holdout_locked=False
                + requires VESPERA_UNLOCK_HOLDOUT=1 + emits operator banner + events_metadata.holdout_unlocked=true
                + DeterminismStamp phase=G provenance
  C-iv2 (HIGH) — Dex commit MUST NOT touch factory contract / closure body / per-fold P126 D-1 / engine guard /
                content_sha256 byte-stability / cpcv_aggregator body beyond optional defensive guard
  C-iv3 (HIGH) — Beckett N8.1 reproducibility 8/9 IDENTICAL to N8 except phase=G + holdout_unlocked=true +
                ic_holdout_status=computed + K3_decay_passed populated
  C-iv4 (HIGH) — F2-T5-OBS-1 verdict-layer fix (decay-clause short-circuit on deferred status) verified PRE-N8.1 +
                handles new computed status correctly at N8.1
  C-iv5 (MED) — Aria thin archi cross-check on N8.1 receipt (absorbed into F2-T8-T0b ledger or thin standalone cosign)
  C-iv6 (MED) — Riven §9 HOLD #2 disarm-ledger update on Mira F2-T10 verdict per Aria F2-T0b §6.1 + ESC-012 C-G6
                atomic AND-conjunction format with F2-T9-OBS-1 trace closure language

Conditions NEGATIVE (C-iv-NEG-1..C-iv-NEG-4):
  C-iv-NEG-1 — DO NOT couple phase to compute_ic_from_cpcv_results aggregator (preserve window-agnostic Option D design)
  C-iv-NEG-2 — DO NOT smuggle Path A' refinement under --phase G (predictor↔label IDENTICAL per ESC-012 R7)
  C-iv-NEG-3 — DO NOT re-run after N8.1 (single-shot per ESC-012 R9 + Anti-Article-IV Guard #3)
  C-iv-NEG-4 — DO NOT touch spec yaml v0.2.3 (Anti-Article-IV Guard #4)

Conditions bound IF Path C wins (C-R4..C-R5 EXTEND ESC-012 C-R1..C-R3):
  C-R4 (MED) — Aria reusability inventory MUST acknowledge two-layer hold-out lock asymmetry (data layer consumed +
              statistical layer forfeit; Bonferroni-multiplicity nuance for future researchers inheriting same window)
  C-R5 (MED) — Mira post-mortem MUST surface F2-T9-OBS-1 protocol-gap as PROXIMATE cause of retire-clean (vs strategy
              thesis itself remaining in suspended state)

Personal preference disclosure: APPROVE_PATH_iv; bias toward minimum-disruption + maximum-information per-effort
  preserved from ESC-012; self-consistency bias disclosed (ESC-012 cosigned C-G1 mandates phase=G CLI flag — Path (iv)
  closes this exact condition); counter-bias check passed at 5-10 LoC cost threshold.

Article II (Gage push exclusivity): preserved — vote document is write-only, no commit/push initiated by Aria.
Article IV (No Invention): preserved — every clause traces in §8 to repo file inspection or anchored doc; conditions
  bound to source anchors; no spec mutation; no threshold mutation; no factory contract refactor; no engine signature
  change; no closure isolation break; no new env-var; no new bypass mechanism; no Path A' smuggling.
Anti-Article-IV Guards (preserved unchanged):
  #1 (Dex impl gated em Mira spec PASS) — preserved through (iv) chain (Mira spec §15.13.12 sign-off chain → Aria
      F2-T8-T0b thin cross-check → Dex F2-T8-T1 caller wiring)
  #3 (NO touch hold-out lock contract) — preserved through Path (iv) canonical use (single explicit phase=G + Layer 1
      env-var existing + Layer 2 spec-pre-authored kwarg flip; audit trail via events_metadata + DeterminismStamp)
  #4 (Gate 4 thresholds UNMOVABLE) — preserved verbatim across both paths
  #5 (NO subsample backtest run) — preserved (Phase G N8.1 runs full hold-out window)
  #6 (NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH) — preserved (Path (iv) Gate 5 still requires paper-mode
      T002.7; Path C Gate 5 LOCKED forever for T002)
  #7 (NO push) — preserved (Aria authoring; no git operations)
  #8 (Verdict-layer *_status provenance + InvalidVerdictReport) — REINFORCED through C-iv4 (F2-T5-OBS-1 fix verified +
      computed-status path tested at N8.1)
Boundary respected:
  NÃO override Mira ML semantics (F2-T9-OBS-1 closure language + F2-T10 verdict on N8.1 delegated to Mira authority)
  NÃO mute Mira F2-T9 round 3 verdict (vote consumes verdict + nuance verbatim; F2-T9-OBS-1 root cause cited, not contested)
  NÃO pre-empt Pax forward-research authority (vote surfaces architectural recommendation; Riven 14-day Path C trigger
      window preserved per ESC-012 minority dissent)
  NÃO pre-empt Riven ledger authority (conditions C-iv6 + C-R4 bind format mandate per Aria F2-T0b §6.1; authoring is Riven)
  NÃO pre-empt Beckett baseline-run authority (Path (iv) requires Beckett N8.1; conditions bind reproducibility cross-check
      format only)
  NÃO commit / NÃO push (Gage @devops authority preserved for any future commit)
  NÃO read other ESC-013 agent votes pre-cast (task discipline; independent ballot)

Cosign: Aria @architect 2026-04-30 BRT — ESC-013 T002 Phase G protocol-compliance gap ballot
        Vote: APPROVE_PATH_iv (Protocol-corrected Phase G re-run — N8.1)
        Secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback IF Riven 14-day trigger fires
        Relationship: REFINEMENT_OF_PATH_B — ESC-012 conditions C-G1..C-G6 EXTENDED with C-iv1..C-iv6 + C-iv-NEG-1..-NEG-4
```

— Aria, escolhendo a conclusão procedural canônica do voto que já fizemos sobre adiar uma medição que ficou mais valiosa após o passe surpresa de K1+K2.
