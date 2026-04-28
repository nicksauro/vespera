# Council 2026-04-27 — ESC-009 AC8 Amendment (D1-original empirical refutation → D2-narrow as_of=2024-08-22)

**Date (BRT):** 2026-04-27
**Trigger:** D1-original (`as_of=2024-07-01`) HALT empirical 2026-04-27 BRT (Operator precompute attempt, ESC-008 D1 path) — `InsufficientCoverage: only 91 valid DailyMetrics (need 126); window=[2023-11-13, 2024-06-30]; days_with_trades=111`
**Source diagnostics:**
- Operator precompute log 2026-04-27 BRT (`scripts/run_warmup_state.py --as-of-dates 2024-07-01`)
- Dara coverage audit: [docs/architecture/T002-data-coverage-audit-2026-04-27.md](../architecture/T002-data-coverage-audit-2026-04-27.md)
- Dara D1-shifted candidates walk: `state/T002/_dara_d1_candidates.txt`
- User briefing 2026-04-27 BRT: "garanto que NÃO tem 2023, tem tipo uns 2 dias quebrados"
**Council convener:** Orion (@aiox-master) under autonomous-mode mandate
**Council size:** 6 voters (Aria + Mira + Beckett + Riven + Pax + Dara)
**Protocol:** Independent vote, no cross-visibility before consolidation
**Outcome:** **6/6 functional convergence APPROVE_D2-NARROW `as_of=2024-08-22`**
**User authorization:** Autonomous mode mandate 2026-04-27 BRT (mini-council decides)

---

## 1. Context

ESC-008 mini-council 4/5 MAJORITY APPROVE_D1 (2026-04-27 BRT) directed Operator precompute of warmup state for `as_of=2024-07-01` per AC9 cache contract + ESC-006 run-once-per-as_of principle (~5–7min cost). Operator executed accordingly. Empirical result:

```
HALT: as_of=2024-07-01: only 91 valid DailyMetrics (need 126); window=[2023-11-13, 2024-06-30]; days_with_trades=111
```

The precompute was REFUTED upstream — there is no continuous 2023-Q4 data in the manifest. Dara coverage audit confirmed that the manifest starts at `2024-01-02` (continuous), and `data/in_sample/year=2023/` has no parquets; user briefing additionally confirmed "garanto que NÃO tem 2023, tem tipo uns 2 dias quebrados". Backfill is not viable per the user's canonical constraint ("não baixar de novo" applied to TimescaleDB-derived data).

This empirically REFUTES PRR-20260421-1's `data_constraint_evidence` — the original SQL aggregation (`6 chunks Jan 2023, zero Feb-Dec 2023; continuous from 2024-01-02`) did NOT account for `is_valid_sample_day` exclusions (weekends/holidays/Copom/rollover D-3..D-1). The actual count of valid sample days in `[2023-11-13, 2024-06-30]` is 91 of the 126 required — short by 35 valid sample days even granting that the entire 2024-01-02..2024-06-30 segment is "continuous".

**3 mitigation paths surfaced (post-D1 HALT):**
- **(D1-shifted)** Re-issue D1 path with shifted `as_of` such that the 146bd lookback is fully within manifest coverage (Dara walk identifies `as_of=2024-08-22` as earliest viable; or later, e.g. `2025-05-31`).
- **(D2-narrow)** Narrow AC8 invocation literal to use `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30` so the warmup gate's `as_of` aligns with viable lookback, while keeping spec-level `data_splits.in_sample` unchanged for downstream Phase F empirical anchor.
- **(D5)** Halt T002.0h closure indefinitely, defer to upstream backfill negotiation with user.

**Critical architectural finding (Aria + Mira + Pax independent discovery):**
- `scripts/run_cpcv_dry_run.py:761`: `warmup_gate_as_of = in_sample_start.isoformat()` — hardcoded binding.
- AC8 invocation literal does NOT carry `--in-sample-start` flag (defaults to spec's `2024-07-01`).
- Spec default `data_splits.in_sample.start = 2024-07-01`.
- Cache lookup with `as_of != 2024-07-01` would fail `assert_warmup_satisfied` strict-equality check.
- **D1-shifted (any as_of) is functionally identical to D2-narrow under another name** — both paths require the AC8 invocation literal to carry `--in-sample-start <viable_as_of>`. The only difference is the framing/labeling. Aria mandated honest relabeling: the path is D2-narrow; calling it "D1-shifted" hides the AC8 amendment that is structurally required.

---

## 2. Votes (condensed for ledger; full verbatim transcripts retained in council session log)

### 2.1 Aria voto (@architect — APPROVE_D2_NARROW as_of=2024-08-22)

**Verdict:** APPROVE_D2_NARROW with `--in-sample-start 2024-08-22` (1 architectural condition + honest-label mandate)
**Personal preference declared:** D2-narrow `as_of=2024-08-22`

**Top rationale (3 points):**
1. **Architectural binding discovery:** `run_cpcv_dry_run.py:761` hardcodes `warmup_gate_as_of = in_sample_start.isoformat()`. There is no decoupling of `as_of` from `in_sample_start`. Therefore D1-shifted (re-precompute with shifted as_of) and D2-narrow (amend AC8 invocation with `--in-sample-start`) are functionally the SAME amendment — a different `--in-sample-start` flag at the CLI surface. Honest labeling: the path is **D2-narrow**.
2. **Earliest viable `as_of` per Dara walk = 2024-08-22.** Lookback window `[2024-01-02, 2024-08-21]` fully within manifest. Preserves ~10 months of in-sample CPCV (`[2024-08-22, 2025-06-30]`) ≈ 225 valid sample days — non-degenerate for Bonferroni n_trials=5 + DSR distribution (Mira authority).
3. **Spec yaml UNTOUCHED.** This is a story-level R15 amendment: AC8 invocation literal (CLI flag append) + `preregistration_revisions[]` PRR append documenting empirical refutation of PRR-20260421-1's data_constraint_evidence. `data_splits.in_sample` field UNCHANGED at spec level (Phase F downstream anchor preserved).

**1 architectural condition:**
- **AC8 invocation amendment** — story T002.0h L65 adds `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30 --smoke` to the literal command. The `--in-sample-start` flag already exists on the CLI surface (per `argparse` registration in `run_cpcv_dry_run.py`). NO script change required, NO spec yaml change required.

**Anti-Article-IV Guard #5 (extended):** D1 empirical refutation = authorization basis for D2-narrow. NOT a "retry until green" — the upstream data is empirically infeasible at as_of=2024-07-01, and shifting as_of is the response to a falsifiable upstream finding (Operator precompute log + Dara audit). This is structurally distinct from "retry the same thing hoping for a different result".

**Boundary preserved:** spec `T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` data_splits UNTOUCHED; only `preregistration_revisions[]` PRR append (story-level path notation in `breaking_fields`); story T002.0h AC8 invocation literal narrowed via existing CLI flag.

**Signature:** Aria 2026-04-27 BRT.

---

### 2.2 Mira voto (@ml-researcher — APPROVE_D2_NARROW with 4 conditions)

**Verdict:** APPROVE_D2_NARROW with 4 conditions
**Personal preference declared:** D2-narrow `as_of=2024-08-22`

**Top rationale (3 points):**
1. **Statistical power preservation at as_of=2024-08-22.** ~10mo in-sample (`[2024-08-22, 2025-06-30]`, ~225 valid sample days) preserves a non-degenerate distribution over CPCV folds — Bonferroni n_trials=5 + DSR distribution remain mathematically meaningful. Compared to ESC-008 D1 (12mo, ~252d), the ~10mo D2-narrow loses ~10% sample but stays well above the degeneracy floor.
2. **n_trials=5 PRESERVED — no recount.** PRR-20260421-1 fixed n_trials=5 with Bonferroni-adjusted p-value 0.002 (= 0.01 / 5). Sample reduction from 12mo to 10mo does NOT trigger a new family-wise error rate — the testing structure (5 distinct trials over a CPCV K-fold) is invariant under the specific in-sample window choice provided the distribution remains non-degenerate. Recount of n_trials would create a false-precision signal that the underlying model architecture changed; it has not. Bonferroni 0.002 stands.
3. **Anti-leak invariants preserved.** Shifted-by-1 + ascending iteration are properties of the orchestrator over the lookback window; both hold equally for `as_of=2024-08-22` as for any other `as_of`. AC4 and AC5 of T002.0h preserve these regardless of in-sample start.

**4 conditional approvals:**
1. **Spec yaml UNTOUCHED.** `data_splits.in_sample` remains `2024-07-01..2025-06-30` at the spec level (Phase F downstream anchor preserved). Story-level AC8 narrowing only.
2. **PRR-20260427-1 append** to `preregistration_revisions[]` — empirical refutation of PRR-20260421-1's data_constraint_evidence. Justification must trace to (a) Operator precompute log, (b) Dara coverage audit, (c) user briefing, (d) Dara D1-shifted candidates walk.
3. **Hold-out lock UNTOUCHED.** `[2025-07-01, 2026-04-21]` remains R10-pinned; no exposure.
4. **§9 deferral language for capital ramp clearance** — Riven §9 amendment must EXPLICITLY DEFER any statistical clearance for capital ramp to a future story when upstream coverage fixed (or when independent walk-forward window permits). The current N4 with as_of=2024-08-22 clears AC8 (engineering exit gate), NOT §9-level Phase F unblock; that requires a separate decision once a longer in-sample is available.

**Signature:** Mira 2026-04-27 BRT.

---

### 2.3 Beckett voto (@backtester — APPROVE_D1_SHIFTED_2024-08-22)

**Verdict:** APPROVE_D1_SHIFTED with `as_of=2024-08-22`
**Personal preference declared:** D1-shifted `as_of=2024-08-22` (functionally equivalent to D2-narrow under Aria's relabel)

**Top rationale (3 points):**
1. **Operator-initiated precompute discipline preserved.** D1's principle was "precompute is run-once-per-as_of, accepted ~5-7min cost; that's the contract" (ESC-006 mini-council 4/4 APPROVE_F + ESC-008 4/5 MAJORITY). Shifting `as_of` from 2024-07-01 to 2024-08-22 honors that principle; the precompute still runs once, the cache contract still applies, the smoke gate criterion (post-cache-hit < 5min) is unchanged. Beckett canonical operational threshold preserved.
2. **N4 is straightforwardly executable.** Once Operator precomputes at `as_of=2024-08-22`, Beckett's N4 invocation (with `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30`) hits the cache, runs the full CPCV smoke phase, captures the full RSS profile (peak < 6 GiB target per Riven condition #2). Empirical wall-time captured for Aria condition #3.
3. **No statistical-power objection from consumer authority.** Beckett consumes the CPCV harness output for kill-decision verdicts; the harness operates over whatever in-sample window the spec declares. As long as the smoke phase exits 0 and produces 5 artifacts + valid KillDecision, the consumer-side AC8 gate is satisfied. Mira owns the statistical power assessment; Beckett's role is to verify the engineering exit gate.

**Aria-honest relabel acknowledged:** Beckett accepts Aria's mandate that "D1-shifted" and "D2-narrow" name the same architectural amendment (CLI flag append). Vote registered as D1-shifted-2024-08-22 to preserve continuity with Beckett's N3 escalation report wording, but Beckett confirms the path is functionally D2-narrow under Aria's labeling. **No dissent.**

**Signature:** Beckett 2026-04-27 BRT.

---

### 2.4 Riven voto (@risk-manager — APPROVE_D1_SHIFTED_2025-05-31 PRIMARY → 2024-08-22 ACCEPTABLE_SECONDARY)

**Verdict:** APPROVE_D1_SHIFTED `as_of=2025-05-31` PRIMARY (architecturally refuted by Aria/Mira/Pax discovery); APPROVE_D1_SHIFTED `as_of=2024-08-22` ACCEPTABLE_SECONDARY (effective vote post-finding)
**Personal preference declared (pre-finding):** as_of=2025-05-31 (already cached, zero precompute cost)
**Effective vote post-finding:** as_of=2024-08-22 (per architectural binding discovery)

**Top rationale (3 points, pre-architectural-finding):**
1. **Custodial discipline favors the already-cached `as_of=2025-05-31`** — Operator precompute of 2024-07-01 having empirically failed, the cleanest path is to lean on the existing cache (2025-05-31) rather than introduce yet another `as_of` requiring a new precompute pass. ZERO additional precompute cost; cache contract already satisfied.
2. **§9 HOLD #1 strict literal exit 0 retained** — full pipeline exit 0 with the existing 2025-05-31 cache satisfies the §9 amendment language preview ("HOLD #1 cleared post-N4 PASS, full CPCV exit 0").
3. **Phase F custodial readiness:** capital ramp gate requires empirical full-pipeline exit; that is achievable with as_of=2025-05-31 today.

**Architectural finding — secondary effective vote 2024-08-22:**
- Aria/Mira/Pax independent discovery: `run_cpcv_dry_run.py:761` hardcodes `warmup_gate_as_of = in_sample_start.isoformat()`. Therefore using as_of=2025-05-31 with the SPEC default `in_sample_start=2024-07-01` would FAIL the warmup-satisfied check (cache key `2025-05-31` does not match expected `2024-07-01`). Architecturally refuted as primary.
- **Riven concedes:** as_of=2025-05-31 path requires the SAME `--in-sample-start 2025-05-31 ... --in-sample-end 2026-04-21` amendment, which exposes the in_sample window to ~10mo (similar to 2024-08-22 case) AND straddles the hold-out start at 2025-07-01 — a §9 violation candidate (custodially UNACCEPTABLE).
- **Effective vote: as_of=2024-08-22 ACCEPTABLE_SECONDARY** — the only path that (a) satisfies the architectural binding, (b) preserves the hold-out lock at 2025-07-01, (c) provides ~10mo in-sample for non-degenerate CPCV.

**3 conditional approvals (D2-narrow as_of=2024-08-22 path):**
1. Operator precomputes at `as_of=2024-08-22` (NEW cache entry, explicit ESC-006 contract authorization — NOT a retry).
2. Beckett N4 captures full-pipeline RSS profile (peak RSS < 6 GiB target).
3. **§9 deferral language (Mira condition #4 reinforced):** statistical clearance for capital ramp DEFERRED to future story when upstream coverage fixed. N4 PASS at as_of=2024-08-22 clears AC8 engineering exit gate, NOT §9-level Phase F unblock.

**Signature:** Riven 2026-04-27 BRT.

---

### 2.5 Pax voto (@po — APPROVE_D2_NARROW unconditional + 3 cosign + R15 ledger + PRR)

**Verdict:** APPROVE_D2_NARROW unconditional
**Personal preference declared:** D2-narrow `as_of=2024-08-22`

**Top rationale (3 points):**
1. **Architectural finding mandates honest relabel — D2-narrow is the truthful name.** The `warmup_gate_as_of` hardcoded binding at `run_cpcv_dry_run.py:761` was independently surfaced by Aria, Mira, and Pax during vote-formation (no cross-visibility before consolidation). All three converged on the same conclusion: any `as_of` shift requires an `--in-sample-start` CLI flag amendment to AC8, which is structurally a D2-narrow regardless of label.
2. **R15 + PRR + spec preregistration_revisions append** — story T002.0h's AC8 invocation literal is mutable (story-level `[ ]` checklist with explicit `[ ]` AC8 still open per L57). This is NOT a Done story file edit; it's an in-flight AC refinement. Spec yaml `data_splits` UNTOUCHED. Therefore: story-level R15 amendment (AC8 line + new AC8 amendment section + Change Log entry) + PRR-20260427-1 to spec preregistration_revisions[] documenting empirical refutation of PRR-20260421-1's data_constraint_evidence.
3. **Article IV trace:** all clauses traceable to (a) Operator precompute log 2026-04-27 BRT, (b) Dara coverage audit (`docs/architecture/T002-data-coverage-audit-2026-04-27.md`), (c) user briefing 2026-04-27 BRT, (d) Dara D1-shifted candidates walk (`state/T002/_dara_d1_candidates.txt`), (e) ESC-006 run-once-per-as_of principle, (f) ESC-008 D1 path empirical refutation, (g) 5 verbatim votes recorded above (this ledger).

**3 cosign acknowledgments + R15 ledger commitment:**
1. Aria architectural finding accepted as authoritative (`run_cpcv_dry_run.py:761` binding).
2. Mira statistical preservation accepted (Bonferroni n_trials=5 + DSR remain non-degenerate at ~10mo in-sample).
3. Riven custodial deferral accepted (§9 deferral language for capital ramp).
4. **R15 breaking_field commitment:** `acceptance_criteria.AC8.invocation_literal` is the affected field at the story level. Spec yaml `data_splits.in_sample` is NOT a breaking_field — it remains v0.2.0-pinned for downstream Phase F.

**Signature:** Pax 2026-04-27 BRT (Autonomous Daily Session, council steward authority).

---

### 2.6 Dara voto (@data-engineer — APPROVE_D1_SHIFTED — pre-architectural-finding)

**Verdict (as cast):** APPROVE_D1_SHIFTED with EITHER `as_of=2025-05-31` OR `as_of=2024-08-22` (Dara expressed indifference between the two, framed as a data-coverage walk decision rather than a custodial/architectural one)
**Personal preference declared:** indifferent, defers to Mira/Riven on statistical/custodial criteria
**Effective vote post-architectural-finding:** APPROVE_D2_NARROW `as_of=2024-08-22` (per architectural binding refuting 2025-05-31 path)

**Top rationale (Dara's voted position):**
1. **Coverage walk authoritative:** earliest viable `as_of` post-2024-07-01 HALT is `2024-08-22` (manifest window `[2024-01-02, 2024-08-21]` fully covered). Latest already-cached `as_of` is `2025-05-31` (precompute already completed in prior session, mtime 2026-04-26 20:49). Both are data-coverage-valid.
2. **TimescaleDB chunks 2023-01-02..2026-04-02 (570 chunks across full range), but 2023-Q4 effectively absent** — confirmed via prior audit doc and corroborated by user briefing. Backfill 2023-Q4 NOT viable per user constraint.
3. **PRR-20260421-1 data_constraint_evidence empirically refuted** — original SQL aggregation didn't model `is_valid_sample_day` filter (weekends/holidays/Copom/rollover D-3..D-1). 91 valid DailyMetrics in `[2023-11-13, 2024-06-30]` is the empirical truth; "continuous from 2024-01-02" claim was true at calendar-day granularity but FALSE at valid-sample-day granularity for warmup gate purposes.

**Documentation produced:**
- `docs/architecture/T002-data-coverage-audit-2026-04-27.md` — full coverage audit
- `state/T002/_dara_d1_candidates.txt` — D1-shifted candidates walk; first viable as_of = 2024-08-22

**Effective vote post-architectural-finding:** Dara's vote was cast pre-architectural-finding (Dara's role was data-coverage authority, not architectural binding analysis). When Aria/Mira/Pax surfaced the `warmup_gate_as_of` binding, the 2025-05-31 path becomes architecturally refuted (as Riven also conceded post-finding). Dara's effective vote consolidates on 2024-08-22 by elimination.

**Signature:** Dara 2026-04-27 BRT.

---

## 3. Vote consolidation

| Voter | Verdict (as cast) | Hard/Conditional | Effective post-finding | Personal-preference (declared) |
|---|---|---|---|---|
| Aria | D2-NARROW with `--in-sample-start 2024-08-22` | conditional (1 architectural condition + honest-label mandate) | D2-narrow `as_of=2024-08-22` ✅ | D2-narrow `as_of=2024-08-22` |
| Mira | D2-NARROW (4 conditions, n_trials=5 stays) | conditional (4 conditions) | D2-narrow `as_of=2024-08-22` ✅ | D2-narrow `as_of=2024-08-22` |
| Beckett | D1-SHIFTED-2024-08-22 | unconditional (Aria relabel honest accepted) | D2-narrow `as_of=2024-08-22` ✅ | D1-shifted-2024-08-22 = D2-narrow under Aria relabel |
| Riven | D1-SHIFTED-2025-05-31 PRIMARY → 2024-08-22 SECONDARY ACCEPTABLE | conditional (3 conditions on secondary) | D2-narrow `as_of=2024-08-22` ✅ (primary architecturally refuted) | as_of=2025-05-31 (pre-finding); 2024-08-22 (post-finding) |
| Pax | D2-NARROW unconditional + 3 cosign + R15 ledger + PRR | unconditional + 4 cosign acknowledgments | D2-narrow `as_of=2024-08-22` ✅ | D2-narrow `as_of=2024-08-22` |
| Dara | D1-SHIFTED with EITHER `as_of=2025-05-31` OR `as_of=2024-08-22` | unconditional (data-coverage walk) | D2-narrow `as_of=2024-08-22` ✅ (by elimination post-finding) | indifferent (defers to Mira/Riven) |

**Effective verdict tally (post-architectural-finding):**
- **D2-narrow `as_of=2024-08-22` hard support:** 6/6 functional convergence
- **D1-shifted-2025-05-31 hard support:** 0/6 (architecturally refuted by Aria/Mira/Pax discovery; conceded by Riven; eliminated for Dara by binding)
- **D5 (defer indefinitely):** 0/6

**Conditions consolidated (8 unique):**
1. **AC8 invocation amendment (Aria #1, Mira #3 implicit, Pax):** story T002.0h L65 — add `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30 --smoke` to the literal command.
2. **Operator precompute as_of=2024-08-22 (~6min cache miss per ESC-006 contract).**
3. **PRR-20260427-1 append** to `preregistration_revisions[]` in `docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml` — empirical refutation of PRR-20260421-1's data_constraint_evidence (Mira authority, Pax cosign).
4. **Bonferroni n_trials=5 PRESERVED** — sem recount (Mira ruling).
5. **Spec yaml UNTOUCHED** at `data_splits.in_sample` level. Only `preregistration_revisions[]` append.
6. **Hold-out lock UNTOUCHED.** `[2025-07-01, 2026-04-21]` remains R10-pinned.
7. **Anti-Article-IV Guard #5 (extended):** D1 empirical refutation = authorization basis for D2-narrow, NOT retry (Aria).
8. **Riven §9 deferral language (Mira condition #4):** statistical clearance for capital ramp DEFERRED to future story when upstream coverage fixed. Resolved as task-#21-separate-post-N4 (out of this council scope; reconciliation between Riven §9 amendment language and Mira deferral handled in dedicated cosign session post-Beckett N4 PASS).

---

## 4. Convergence analysis

**3 detail-investigators discovery (independent, no cross-visibility before consolidation):**

1. **`warmup_gate_as_of` hardcoded binding at `run_cpcv_dry_run.py:761`** — Aria + Mira + Pax independently surfaced this during vote-formation. The line `warmup_gate_as_of = in_sample_start.isoformat()` couples the warmup gate's `as_of` to the in-sample start. AC8's invocation literal does NOT carry `--in-sample-start`, so it defaults to the spec's `2024-07-01`. Cache lookup at any other `as_of` would fail `assert_warmup_satisfied`. **Implication:** D1-shifted (any non-default as_of) is architecturally identical to D2-narrow under another label.

2. **Earliest viable `as_of` per Dara walk = 2024-08-22.** All 4 architectural/statistical/custodial voters (Aria, Mira, Riven post-finding, Pax) converged on this specific date. Dara's data-coverage walk is the single source of truth (`state/T002/_dara_d1_candidates.txt`).

3. **PRR-20260421-1 empirical refutation is the proper R15 trail** (Mira + Pax). The original PRR's data_constraint_evidence was based on chunk-metadata SQL that did not model `is_valid_sample_day`. Empirical truth is 91 valid DailyMetrics, not the chunk-count claim implied. PRR-20260427-1 append is the canonical R15 trail for this finding.

**6/6 functional convergence on D2-narrow `as_of=2024-08-22`** with all hard conditions met:
- Aria's architectural condition (AC8 invocation amendment): SATISFIED
- Mira's 4 conditions (spec untouched, PRR append, hold-out untouched, §9 deferral): SATISFIED in this ledger + downstream cosign chain
- Beckett's no-dissent: REGISTERED
- Riven's 3 conditions (Operator precompute, RSS profile, fallback ack): SATISFIED in action items
- Pax's 4 cosign acknowledgments + R15 commitment: SATISFIED in this ledger + Pax cosign at §9
- Dara's effective consolidation (post-finding): SATISFIED by elimination

---

## 5. Outcome

**APPROVE_D2_NARROW `as_of=2024-08-22`** — 6/6 functional convergence per autonomous-mode council standard (5/5 CONVERGENT preferred, ≥4/5 MAJORITY acceptable; 6/6 exceeds threshold).

**User authorization:** Autonomous mode mandate 2026-04-27 BRT — user explicitly delegated mini-council decision authority for this round. No additional user authorization required for D2-narrow execution.

---

## 6. Action items (post-decision)

1. **Operator** authorizes precompute via:
   ```
   python scripts/run_warmup_state.py --as-of-dates 2024-08-22 --output-dir state/T002/
   ```
   Estimated cost ~6min (cache miss per ESC-006 contract). `cache_audit.jsonl` will record `status:"miss"` then `status:"write"` markers per AC9 invariant.
2. **Beckett** executes T11.bis N4 re-run with amended invocation:
   ```
   python scripts/run_cpcv_dry_run.py --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run --smoke --in-sample-start 2024-08-22 --in-sample-end 2025-06-30
   ```
   Report path: `docs/backtest/T002-beckett-t11-bis-smoke-report-N4-{date}.md`. Full pipeline RSS profile captured per Riven condition #2.
3. **Riven + Mira §9 deferral reconciliation** — separate task post-N4 PASS. Riven's §9 amendment language (HOLD #1 clearance) and Mira's §9 deferral language (capital ramp clearance) reconciled in dedicated cosign session. Documented in `docs/qa/gates/T002.0g-riven-cosign.md` §9 (or successor doc).
4. **Pax** updates T002.0h story Change Log + adds AC8 amendment section + 10-point re-validation post-amendment. Updates USER-ESCALATION-QUEUE with ESC-009 entry. Appends PRR-20260427-1 to spec `preregistration_revisions[]` with computed pax_cosign_hash.
5. **Sable (squad-auditor)** audits coherence post-N4 (workflow Q-SDC Phase G — cosign chain integrity + Article IV traceability + R15 trail completeness).
6. **Gage push** R12 user-gated post-cosign chain complete.

---

## 7. Conditional ledger commitments (per voter approvals)

### 7.1 Aria conditions (D2-narrow as_of=2024-08-22)
1. AC8 invocation amendment: `--in-sample-start 2024-08-22 --in-sample-end 2025-06-30 --smoke` (existing CLI flag, no script change).
2. Honest-label mandate: this is D2-narrow regardless of pre-finding labeling.
3. Anti-Article-IV Guard #5 (extended): D1 empirical refutation = authorization basis, NOT retry.

### 7.2 Mira conditions (D2-narrow as_of=2024-08-22)
1. Spec yaml `data_splits.in_sample` UNTOUCHED.
2. PRR-20260427-1 append to `preregistration_revisions[]` (empirical refutation of PRR-20260421-1).
3. Hold-out lock UNTOUCHED.
4. §9 deferral language for capital ramp clearance (resolved as task-#21-separate-post-N4).

### 7.3 Beckett conditions (D2-narrow as_of=2024-08-22)
- No additional conditions; Aria relabel accepted.

### 7.4 Riven conditions (D2-narrow as_of=2024-08-22, secondary acceptable post-finding)
1. Operator authorizes precompute as ESC-006-contract-completion (NOT retry).
2. Beckett N4 captures full-pipeline RSS profile (peak RSS < 6 GiB target).
3. §9 deferral language reconciled with Mira condition #4 in dedicated post-N4 cosign session.

### 7.5 Pax conditions (D2-narrow as_of=2024-08-22)
1. Aria architectural finding accepted as authoritative.
2. Mira statistical preservation (Bonferroni n_trials=5 stays) accepted.
3. Riven custodial deferral accepted.
4. R15 breaking_field commitment: `acceptance_criteria.AC8.invocation_literal` (story-level).

### 7.6 Dara conditions (D2-narrow as_of=2024-08-22, by elimination post-finding)
- Coverage walk authoritative: 2024-08-22 = earliest viable.

---

## 8. Authority chain

- **Council convener:** Orion (@aiox-master) under autonomous-mode mandate
- **Voters:** Aria + Mira + Beckett + Riven + Pax + Dara (independent, no cross-visibility)
- **Outcome ratification:** Pax cosign 2026-04-27 BRT (council steward)
- **User authorization:** Autonomous mode mandate 2026-04-27 BRT (mini-council decides)
- **Execution authority:** D2-narrow path → Operator (precompute as_of=2024-08-22) → Beckett (N4 amended invocation) → Riven+Mira §9 deferral reconciliation → Pax close → Sable audit → Gage push (R12 user-gated)

---

## 9. Pax cosign

```
Validator: Pax (@po) — Product Owner / Story Balancer / Council Steward
Council: ESC-009 AC8 Amendment (D1-original empirical refutation → D2-narrow as_of=2024-08-22)
Date: 2026-04-27 BRT
Outcome: 6/6 functional convergence APPROVE_D2_NARROW as_of=2024-08-22
User authorization: Autonomous mode mandate 2026-04-27 BRT (mini-council decides)
Article IV: NO INVENTION — every clause traceable to (a) Operator precompute log 2026-04-27 BRT,
            (b) Dara coverage audit (docs/architecture/T002-data-coverage-audit-2026-04-27.md),
            (c) user briefing 2026-04-27 BRT, (d) Dara D1-shifted candidates walk
            (state/T002/_dara_d1_candidates.txt), (e) ESC-006 + ESC-008 council ledgers,
            (f) 6 verbatim votes recorded above (condensed for ledger;
            full transcripts retained in council session log).
R15 compliance: STORY-LEVEL breaking_field — acceptance_criteria.AC8.invocation_literal.
                Spec yaml v0.2.0 schema UNTOUCHED. PRR-20260427-1 appended to
                preregistration_revisions[] documenting empirical refutation of
                PRR-20260421-1's data_constraint_evidence.
Spec compliance: T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml data_splits.in_sample
                 UNTOUCHED (downstream Phase F empirical anchor preserved).
Statistical preservation: Bonferroni n_trials=5 PRESERVED (Mira ruling).
                          ~10mo in-sample (~225 valid sample days) preserves
                          non-degenerate distribution for CPCV K-fold + DSR.
Custodial preservation: hold-out lock [2025-07-01, 2026-04-21] UNTOUCHED.
                        §9 deferral for capital ramp clearance honored.
Next gate: Operator precompute as_of=2024-08-22 (~6min) → Beckett N4 amended invocation.
Cosign: Pax 2026-04-27 BRT (Autonomous Daily Session, council steward).
```

— Pax, balanceando ✨
