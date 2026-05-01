---
council_id: QUANT-2026-05-01-alpha-discovery
council_topic: Alpha discovery direction post T002 retire (Round 4 — costed_out_edge_oos_confirmed_K3_passed)
ballot_authority: Mira (@ml-researcher)
ballot_role: ML/statistical authority — author of T002 spec yaml v0.2.x, Mira Gate 4b spec v1.2.0, F2-T5 / Round 3 / Round 3.1 verdicts, T002.6 IC pipeline deep audit
date_brt: 2026-05-01
branch: main (ballot independent — no other Round 4 votes read)
inputs_consumed:
  - "T002 retire memory (Round 3.1 GATE_4_FAIL_strategy_edge_costed_out_edge_oos_confirmed_K3_passed)"
  - "Round 3.1 verdict (Mira authorship — `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md`)"
  - "Riven 3-bucket post-mortem v2 (10 anti-patterns)"
  - "Cost atlas v1.0.0 (FIXED — slippage + costs reduction OFF the ballot per ESC-012 user reframe)"
  - "Mira deep audit T002.6 (`docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md`)"
inputs_explicitly_NOT_read:
  - "Other Round 4 ballots (Pax, Riven, Beckett, Aria, Kira, Sable) — Article IV §6 independence enforced"
core_question: "Given costed_out_edge OOS-confirmed (K3 PASS, K1 FAIL), what is the highest-information-per-Bonferroni-trial direction for H_next?"
verdict_summary: |
  Predictor IP REUSABLE under strict Bonferroni-budget hygiene (n_trials_carry_forward IS the asset).
  Top-3 strategies (statistical-rigor lens): (a) conviction-conditional sizing — magnitude P80 + bootstrap CI tightness;
  (b) different label horizon — `ret_to_close_BR` 17:55 swap-out; (c) asymmetric exit (R-multiple-shaped barriers).
  CV scheme: same CPCV N=10 k=2 45 paths embargo=1 (+ explicit re-Bonferroni penalty on the carry-forward base).
  Hold-out: NEW pre-registered 2026-05-01..2026-09-30 (5 forward-time months); old hold-out FORFEITED.
  Bonferroni budget: K=3 (one per strategy ranked). New anti-pattern Round 4: "DSR_OOS << DSR_IS reveals costed_out artifact".
  Personal preference disclosed; Article IV self-audit 7 anchors verified.
cosign: Mira @ml-researcher 2026-05-01 BRT
---

# Quant Council Round 4 — Alpha discovery post T002 retire — Mira (@ml-researcher)

> **Verdict (independent ballot — Article IV §6 enforced):** Predictor IP IS REUSABLE; preferred strategies are
> **(1) conviction-conditional sizing**, **(2) label-horizon swap to `ret_to_close_BR` 17:55**, **(3) asymmetric
> R-multiple exit**. CV scheme unchanged from T002 (CPCV N=10 k=2 embargo=1) BUT with explicit Bonferroni
> re-penalization on the carry-forward base. Hold-out is NEW (forward-time) — old hold-out 2025-07..2026-04
> is CONSUMED + FORFEITED. Bonferroni K=3 for H_next. New anti-pattern Round 4 added below.
>
> **Authority basis:** Author of T002 Mira spec yaml v0.2.3, Mira Gate 4b spec v1.2.0, F2-T5 / Round 3 / Round 3.1
> verdicts, T002.6 deep audit. ML/statistical voice on this council.
>
> **Constraint binding:** cost atlas v1.0.0 FIXED (Path A cost-reduction OFF). Predictor `−intraday_flow_direction`
> at entry windows {16:55, 17:10, 17:25, 17:40} BRT IS now treated as Squad IP under Round 3.1 K3 PASS evidence
> (rank-stability OOS confirmed, IC IS=0.866010 / OOS=0.865933, ratio 0.99991).

---

## §1 Predictor IP reuse — viable? Top-3 strategies ranked

### §1.1 Reuse viability (yes, with strict conditions)

The Round 3.1 verdict is the strongest possible diagnostic for predictor-level reuse:

- **K3 decay COMPUTED PASS (0.99991 ≫ 0.5):** rank-correlation between predictor and forward-return label IS
  stable across the 9-month in-sample window (2024-08-22..2025-06-30) AND the 10-month locked OOS holdout
  (2025-07-01..2026-04-21). This is exceptional cross-window stability per AFML §8.6 calibration —
  IC > 0.5 is "exceptional"; IC ~0.866 stable across windows is rarer still.
- **K1 OOS strict FAIL (DSR=0.206 « 0.95):** the realized PnL distribution under fixed cost atlas + DMA2
  latency profile + triple-barrier early-exit is materially negative OOS (sharpe_mean = -0.053,
  hit_rate = 0.472, profit_factor = 0.929). The PREDICTOR is intact; the STRATEGY-OVER-COSTS is not.

This decomposition is the canonical `costed_out_edge` signature confirmed OOS (Round 3.1 verdict
sub-classification `costed_out_edge_oos_confirmed_K3_passed`). The predictor IP is therefore reusable
**conditional on a NEW strategy layer that converts the rank-stable signal into PnL with a cost-friction
profile that materially exceeds the strict §1 bar (DSR > 0.95) on a NEW pre-registered OOS window**.

### §1.2 Top-3 ranked candidates (ML rigor lens)

I evaluate the 4 user-suggested strategies (a/b/c/d) on three statistical criteria:

| Criterion | Definition |
|---|---|
| **Bonferroni budget feasibility** | Strategy adds finite N new hypotheses to family-wise hypothesis space (per Bailey-LdP 2014 §3 multiple-testing penalty). Lower N is preferable under shared n_trials budget K=3. |
| **Sample-size feasibility** | Strategy preserves CPCV n_paths=45 × n_trials_used CPCV harness; filtered/conditional subsets do NOT collapse n_filtered below AC9 250 floor (spec §6 R9 binding). |
| **Falsifiability** | Strategy admits clean kill-criteria binary disambiguation per Mira Gate 4b spec §0 falsifiability mandate (analogous to K1+K2+K3 kill-tree). |

Scoring each user candidate:

| Candidate | Bonferroni | Sample-size | Falsifiability | **Composite** |
|---|---|---|---|---|
| **(a) Conviction-conditional sizing** (predictor magnitude P80 OR bootstrap CI tight) | **HIGH** (1 new hypothesis: threshold τ on magnitude; τ pre-registered as P80) | **MEDIUM-HIGH** (filtered subset n ≈ 0.2 × 3800 = 760 events; above 250 floor; R9 PASS) | **HIGH** (clean kill: DSR_OOS_filtered > 0.95 on new hold-out, OR FAIL) | **#1** |
| **(d) Different label** (replace `ret_forward_to_17:55` with `ret_to_close_BR`) | **HIGH** (1 new hypothesis: re-derive label semantics; same predictor) | **HIGH** (full 3800 events preserved; no filtering) | **HIGH** (clean kill: DSR_OOS > 0.95 with new label, OR FAIL) | **#2** |
| **(c) Asymmetric exit** (R-multiple shape: hold winners > 0.7×ATR longer; tight stop on losers) | **MEDIUM-HIGH** (2 new hypotheses: hold-extension trigger + tight-stop ratio) | **HIGH** (full 3800 events; barrier modification only) | **MEDIUM-HIGH** (kill DSR_OOS > 0.95; but barrier interaction with cost layer adds nuisance variance) | **#3** |
| **(b) Multi-timeframe conditioning** (predictor + secondary regime filter — IV spike, gap-from-open) | **LOW** (each regime filter = 1 new hypothesis; "IV spike + gap" = 2-4 hypotheses; family inflates rapidly) | **LOW-MEDIUM** (filtered subset risks dropping below 250 floor under tight regime conditions) | **MEDIUM** (regime definitions are themselves hyperparameters; hidden hypothesis multiplication) | **#4 (REJECTED for Round 4 H_next)** |

**Top-3 ranked recommendation:**

1. **(a) Conviction-conditional sizing.** Pre-register threshold `τ = P80(|predictor|)` measured on F2 in-sample
   distribution (2024-08-22..2025-06-30); on new OOS window, trade ONLY when `|predictor_t| ≥ τ`. Hypothesis is:
   the predictor's magnitude carries information about edge-vs-cost ratio (high-magnitude bets are more likely
   to overcome the cost layer). Falsifiable: DSR_OOS_filtered > 0.95 on new hold-out OR FAIL. n_filtered
   estimate ≈ 760 events (above R9 floor). Single new hypothesis added.

2. **(d) Label-horizon swap to `ret_to_close_BR` 17:55.** Pre-register new label as full session-close return
   (16:55 entry → 17:55 close BRT) replacing F2's intraday `ret_forward_to_17:55_pts`. Hypothesis is: the
   end-of-day fade has a different magnitude profile if measured to actual session close vs intermediate
   intraday window. Different time horizon = different cost-atlas-to-edge ratio (longer hold → cost layer
   amortizes; but slippage may also amplify). Falsifiable: DSR_OOS > 0.95 with new label OR FAIL. Full 3800
   events preserved. Single new hypothesis added.

3. **(c) Asymmetric exit (R-multiple barriers).** Pre-register triple-barrier with `tp_pts = 1.5 × ATR_5m` AND
   `sl_pts = 0.6 × ATR_5m` (currently F2 used symmetric 1×ATR per spec §15.3). Hypothesis is: the realized
   PnL distribution per-event has positive skew that the symmetric barrier truncates; asymmetric exits capture
   the tail. Falsifiable: DSR_OOS > 0.95 with asymmetric barriers OR FAIL. Full 3800 events preserved.
   Two new hypotheses added (tp ratio + sl ratio); justified per Bonferroni accounting in §5.

**Rejected: (b) Multi-timeframe conditioning.** The IV-spike and gap-from-open regimes are NOT pre-registered
in any prior T002 spec; introducing them would require fresh feature definitions, fresh Nova
microstructural audit, fresh Nelo live-availability check, AND fresh Bonferroni accounting against an
expanded hypothesis space. Family-wise error inflates rapidly under regime-conditioning (typical N-regime
filters expand search to N×base). Defer to a future epic; not a Round 4 H_next candidate.

### §1.3 Why these three (vs the alternative configurations I considered)

Three configurations I considered and rejected:

- **Meta-labeling layer over the predictor.** Lopez de Prado AFML §3 meta-labeling separates direction
  (primary) from size (secondary). On its face, this is conviction-conditional sizing (#1) plus a learned
  classifier. I rejected the learned classifier piece because: (i) it adds 1 model + ≥3 hyperparameters
  (n_estimators, depth, regularization) = 4+ new hypotheses, blowing the K=3 Bonferroni budget; (ii) the
  out-of-sample sample available for the meta-label classifier OOS validation is tiny under fresh hold-out
  preregistration (we cannot meta-train on the F2 in-sample window without re-using exhausted data per
  §2.1 of my ESC-012 vote — Bonferroni budget exhaustion argument). Defer to T003+ epic.
- **Stronger predictor (e.g., extend `−intraday_flow_direction` to a multi-window blend).** Predictor
  augmentation is itself a fresh hypothesis space. The Round 3.1 evidence already shows the predictor IS
  rank-stable OOS at IC=0.866; augmenting it risks regression to mean. Hold the IP fixed; vary the strategy
  layer.
- **Cost-modeling refinement.** Off the ballot per ESC-012 user reframe (cost atlas v1.0.0 FIXED).

### §1.4 What "predictor IP reuse" formally means under MANIFEST R15 + research-log invariant

To honor the n_trials carry-forward as squad IP:
- The predictor formula `−intraday_flow_direction(t)` at `t ∈ {16:55, 17:10, 17:25, 17:40} BRT` MUST be
  bit-frozen via `engine_config_sha256` AND `predictor_definition_sha256` from F2 N7-prime / N8.2 PROPER.
  Mira spec yaml v0.2.x line referencing predictor MUST be carried into the new spec yaml verbatim.
- The research-log invariant commit hash (`docs/ml/research-log.md@fadacf482633c4d23cdaf21edc986ca1f879752b`
  per N8.2 metrics) MUST remain CITABLE in the new spec; it documents the Bonferroni budget consumed to date.
- A NEW research-log entry MUST land BEFORE the new spec yaml hash-freezes — append-only chain preserved.

This is exactly the MANIFEST R15.2 spec versioning + research-log invariant that already binds T002. It
extends seamlessly to T003 / next-epic.

---

## §2 New CV scheme proposal

### §2.1 Recommendation: KEEP CPCV N=10 k=2 45 paths embargo=1, with explicit Bonferroni RE-penalization

Reasons to keep:
- **Statistical machinery is honest.** CPCV is the squad's canonical avoidance of single-path overfit
  (Lopez de Prado AFML §12). N=10 k=2 produces 45 distinct test combinations; PBO, DSR, and IC bootstrap
  CIs are all computed on the path distribution. Round 3.1 PBO=0.0595 demonstrates the harness is working.
- **Embargo=1 is the right value for end-of-day strategy.** End-of-day-fade (entry 16:55, exit 17:55)
  has implicit overnight = end-of-test-fold = beginning-of-next-fold contamination risk. 1-session embargo
  cleanly sterilizes that. Round 3.1 K3 PASS confirms the embargo is sufficient.
- **Sample-size headroom.** 3800 events × 45 paths = 171000 path-events; AC9 R9 250 floor is preserved
  74-127× over (per Round 3.1 §2 evidence). Conviction-conditional sizing (#1) drops n_filtered to ~760
  events but path-event count stays well above floor.

### §2.2 Modification: Bonferroni RE-penalization on the carry-forward base

Round 3.1 consumed Bonferroni budget = 5 trials (T1..T5 per ESC-011 R9). For H_next, the budget is
**carried forward NOT reset**. Per Bailey-LdP 2014 §3, the deflated Sharpe denominator inflates under
the cumulative trial count. For H_next:
- **n_trials_carry_forward = 5** (T002 IS-only trials consumed).
- **n_trials_new_for_H_next = 3** (one per top-3 candidate).
- **n_trials_total = 8** (Bonferroni penalty computed against this).

Note: the F2 N7-prime DSR=0.767 was deflated against n_trials=5; under n_trials=8 the same observation
would deflate further. This is precisely why running multiple new strategies on the same OOS window
without budget accounting WOULD be the canonical Round 3 anti-pattern — and is why I want the
Bonferroni budget MADE EXPLICIT in §5.

### §2.3 Optional addendum: tighter K3 decay floor

Round 3.1 K3 decay floor is `IC_holdout > 0.5 × IC_in_sample`. The 0.5 floor is conservative; observed
ratio was 0.99991. For H_next, I would propose **tighten K3 decay floor to 0.7** (i.e., `IC_holdout >
0.7 × IC_in_sample`) for robustness — but this is a SHOULD not a MUST, and only if Pax + Riven concur
in the T003 spec drafting. Original 0.5 floor remains acceptable as fallback.

### §2.4 Embargo unchanged (vs user prompt suggesting embargo=2)

User prompt suggested `embargo=2 if fewer events expected`. I reject this for H_next:
- The strategy is end-of-day, daily-bar event-clock; embargo=1 (one session) is structurally aligned
  with the event arrival rate.
- Embargo=2 would shrink usable train/test distinct samples without statistical rationale; it inflates
  variance estimates without reducing bias.
- "Fewer events" is NOT expected for H_next on the new OOS window (forward-time 5 months @ ~20
  sessions/month × 4 entry windows ≈ 400 events; conviction-conditional filtering reduces to ~80).

If conviction-filtering pushes n below R9 250 floor on the new OOS window, the PROPER response is
to extend the OOS window (e.g., 6-7 months instead of 5), NOT inflate embargo.

---

## §3 Hold-out window proposal

### §3.1 Old hold-out is CONSUMED + FORFEITED

Per Round 3.1 evidence + my ESC-012 §3.2 argument: once Phase G PROPER unlock fired (N8.2 run dir
`data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/`), the hold-out window 2025-07-01..2026-04-21
is **in-sample for any future T002.x or T003.x candidate**. Anti-Article-IV Guard #3 spirit forbids
re-using it as OOS for H_next.

### §3.2 Recommendation: forward-time 2026-05-01..2026-09-30 (5 months) — NEW pre-registered hold-out

**Why forward-time over walk-forward or last-30%-of-IS:**

| Option | Pros | Cons | Mira ranking |
|---|---|---|---|
| **(A) Forward-time 2026-05-01..2026-09-30** | Cleanest possible OOS (no chronological touch by any prior T002/T003 trial); pre-registration date can be hash-frozen; data does not yet exist as of council date 2026-05-01 → impossible to leak; matches Anti-Article-IV Guard #3 spirit | 5 months wall-clock wait before verdict | **#1 (PRIMARY RECOMMENDATION)** |
| **(B) Reserve last 30% of NEW IS data** | Faster verdict (no wall-clock wait beyond data extension) | Requires re-defining "in-sample" for predictor IP (was 2024-08-22..2025-06-30); creates ambiguity about which slice trained predictor vs which slice trained strategy layer; risks contamination of the carry-forward predictor IP | **#3 (REJECTED for H_next; reserve as fallback IFF user wall-clock constraint binding)** |
| **(C) Walk-forward (rolling)** | Generates multiple OOS observations; mitigates single-shot anxiety | Each rolling step consumes Bonferroni budget; 4 rolling windows × 3 candidates = 12 trials total → DSR floor inflates 240% from current 5; deflated significance becomes near-impossible to clear | **#4 (REJECTED on Bonferroni grounds)** |
| **(D) Hybrid: 30% reserved IS + forward-time 5mo** | Two OOS observations with composite kill criterion | Doubles preregistration complexity; harder to disambiguate signal vs regime drift; increases governance overhead | **#2 (defensible as conservative path)** |

**My recommendation: (A) forward-time 5-month hold-out 2026-05-01..2026-09-30.** Pre-registered today
(2026-05-01) at council ratification; data accumulates over wall-clock; no in-sample contamination
possible because data does not exist yet at preregistration time. Single-shot OOS observation per
candidate; verdict at council Q3 2026.

If user wall-clock constraint requires faster verdict than 5-month wait, fallback (D) hybrid: reserve
final 30% of an extended IS that runs 2024-08-22..2026-04-21 (current IS + old hold-out re-tagged as
extended IS for H_next purposes ONLY because old hold-out is now consumed = effectively in-sample).
The extended IS = ~21 months; reserved 30% = ~6.3 months ≈ 2025-12-15..2026-04-21. This window IS
already-existed-data, just NOT touched by H_next predictor refinement (predictor IP frozen). But this
introduces subtle epistemic risk because the same window WAS in-sample for the original Round 3.1
strategy-layer learning. I rate (D) as defensible-but-suboptimal vs (A).

### §3.3 Pre-registration discipline for new hold-out

Per MANIFEST R15.2 + my activation rule, the new spec yaml MUST emit:
```yaml
preregistration_revisions:
  - revision_id: PRR-20260501-1
    timestamp_brt: 2026-05-01T<HH:MM:SS>
    from_version: T002-end-of-day-inventory-unwind-wdo-v0.2.3
    to_version: T003-conviction-conditional-end-of-day-fade-v0.1.0  # or similar
    breaking_fields:
      - data_splits.in_sample (extended)
      - data_splits.hold_out_virgin (NEW: 2026-05-01..2026-09-30)
      - kill_criteria.K3_decay_floor (optional tighten 0.5 → 0.7)
      - n_trials.carry_forward (5 → 8)
      - strategy_layer.* (entirely new for conviction-conditional sizing)
    justification: "T002 retire under Round 3.1 costed_out_edge_oos_confirmed_K3_passed. Old hold-out window CONSUMED + FORFEITED per Anti-Article-IV Guard #3. New hold-out forward-time 2026-05-01..2026-09-30 pre-registered before any T003 trial executes."
    data_constraint_evidence: "T002 N8.2 holdout_locked=False propagation 2026-05-01T02:55:55 BRT confirmed by run_id 3da49a82343e4650abfd0d4921ee1897 — old hold-out unlocked + computed; cannot be re-used."
    pax_cosign_hash: "<computed via scripts/pax_cosign.py compute>"
```

This is append-only; preserves the T002 chain integrity.

---

## §4 New anti-pattern proposal Round 4 (NEW — addition to Riven 3-bucket post-mortem v3)

### §4.1 Anti-pattern #11: `costed_out_edge_signature` diagnostic chain

**Name:** `costed_out_edge_signature` — diagnostic anti-pattern for distinguishing costed-out-edge from
in-sample-fit-edge using the IC × DSR × Sharpe-sign cross-window diagnostic chain.

**Diagnostic chain (canonical signature):**
1. **IC stable IS=OOS** (Round 3.1: `IC_in_sample = 0.866010` vs `IC_holdout = 0.865933`; ratio 0.99991).
   This rules out predictor-level overfit. The PREDICTOR is real.
2. **DSR drops materially** (Round 3.1: `DSR_in_sample = 0.767` → `DSR_OOS = 0.206`). DSR is the
   deflated Sharpe of the realized PnL distribution under cost + barrier; it integrates the predictor
   AND the strategy AND the cost layer. The drop reveals the realized-PnL distribution carries less
   risk-adjusted edge than the predictor alone implies.
3. **Sharpe sign-flip** (Round 3.1: `sharpe_mean_IS = +0.046` → `sharpe_mean_OOS = -0.053`;
   `hit_rate_IS = ?` → `hit_rate_OOS = 0.472 < 0.5`; `profit_factor_OOS = 0.929 < 1.0`). The
   strategy is LOSING money OOS at the trade-event level. The sign-flip is the signature confirmation
   that cost layer eats the edge, leaving residual PnL distribution net-negative.

**When all three signals jointly fire** — IC stable + DSR drop + Sharpe sign-flip — the verdict is
CANONICALLY `costed_out_edge` (NOT `in_sample_artifact_overfit`, NOT `data_quality`, NOT `regime_change`).

**Why this matters:** without this diagnostic chain, council resolution risks misclassifying Round 3.1
as either (a) `predictor_overfit_artifact` (would reject IP reuse — wrong) or (b) `regime_change`
(would defer indefinitely waiting for stable regime — also wrong). The correct retrospective is the
predictor IS reusable, the strategy-over-costs is NOT. This drives the §1.2 top-3 candidates that
target the strategy layer (not the predictor).

### §4.2 Suggested addition to Riven 3-bucket post-mortem v3

Riven post-mortem `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` currently
maintains a 3-bucket taxonomy (Bucket A: data_quality, Bucket B: strategy_edge, Bucket C: regime
mismatch) plus 10 anti-patterns. I propose:

- **Anti-pattern #11 added:** `costed_out_edge_signature` diagnostic chain (above).
- **Bucket B sub-classification refined:** add `costed_out_edge_oos_confirmed_K3_passed` as a named
  Bucket B leaf (Round 3.1 signature). This sits adjacent to existing `strategy_edge` clean-negative
  (Round 2 sub-classification) but is empirically distinguishable per the diagnostic chain.

This refines Riven's taxonomy without modifying its existing buckets. Riven F2-T6 reclassification
authority is preserved; this is a Mira-authored proposal to be accepted/modified by Riven.

### §4.3 What the anti-pattern teaches future research-log entries

For all future H_next candidates: **always report IC × DSR × Sharpe-sign jointly across IS and
OOS**, not just one or two of them. The decomposition is what enables clean diagnostic. If a future
candidate shows IC drop + DSR drop + Sharpe-sign-flip, that is `predictor_overfit_artifact` (different
verdict). If IC stable + DSR drop + Sharpe stable-positive (small magnitude), that is `costed_out_marginal`
(different verdict — borderline). The full 2×2×2 truth table should be a standing fixture in every
H_next research-log entry.

---

## §5 Bonferroni budget recommendation

### §5.1 Defended K=3 for H_next

Hypothesis space size: top-3 strategy-layer variants ranked above (conviction-conditional sizing, label
horizon swap, asymmetric exit). Per Bailey-LdP 2014 §3:
- **n_trials_carry_forward = 5** (T002 IS T1..T5 consumed).
- **n_trials_new = 3** (Round 4 H_next candidates 1, 2, 3).
- **n_trials_total = 8**.

Justification for K=3 (not K=2, not K=5):
- **K=2 (top-2 only):** would force me to choose between (a) and (d) without clear superiority — (a) is
  more theoretically motivated by AFML meta-labeling tradition; (d) is more empirically motivated by
  cost-amortization-over-longer-horizon. Pre-registering only 1 of 2 would be arbitrary. K=3 includes
  both with discipline.
- **K=5 (Kira lead 1-3 candidates per concept × 5 concepts):** this would be an analyst-side widening of
  the hypothesis space. Per AFML §15.6 + §7, family-wise error inflates with N; under K=5 the deflated
  Sharpe denominator inflation makes 0.95 strict bar near-impossible. K=5 would be the canonical
  "analyst kitchen sink" anti-pattern (Riven 3-bucket anti-pattern catalog #2 or similar).
- **K=3 sweet spot:** preserves enough hypothesis diversity to learn from the council's directional
  intuitions while honoring the Bonferroni discipline.

### §5.2 Research-log invariant new commit

Per ESC-012 R6 reusability invariant + R15.2 hash-freeze:
- New research-log entry `docs/ml/research-log.md@<NEW_HASH>` MUST land BEFORE the new spec yaml
  hash-freezes.
- The entry MUST cite: (i) the carry-forward `n_trials = 5` from `@fadacf482633c4d23cdaf21edc986ca1f879752b`;
  (ii) the new `n_trials_new = 3` for top-3 candidates; (iii) the Bonferroni-adjusted DSR threshold
  derivation (the 0.95 strict bar is UNMOVABLE per Anti-Article-IV Guard #4, but the Bonferroni-adjusted
  significance-level penalty inflates the effective floor).
- The new spec yaml MUST cite `docs/ml/research-log.md@<NEW_HASH>` as the budget anchor.

### §5.3 What blocks K=3 from inflating to K=4+

Strict ML rigor discipline. Specifically:
- I (Mira) hold authority over K3 / K1 spec thresholds. Any 4th candidate would require a fresh
  research-log entry justifying it on independent statistical grounds AND a fresh PRR with full
  data_constraint_evidence + pax_cosign_hash.
- The H_next council resolution should cap n_trials_new at K=3 explicitly per ESC-011 R9 spirit.
- Multi-timeframe conditioning (#4 rejected) is explicitly OFF the H_next budget; deferred to T003+.

---

## §6 Personal preference disclosure (Article IV honesty)

### §6.1 What I believe (with epistemic uncertainty)

ML-research instinct given Round 3.1 evidence:
- **High confidence (≥80%):** Predictor IP is genuinely reusable. K3 PASS at decay ratio 0.99991 across
  9-month IS + 10-month OOS is the strongest possible cross-window stability signature at this sample
  size. Future candidates SHOULD reuse the predictor formula bit-frozen, NOT re-derive it.
- **Moderate-to-high confidence (65-75%):** Conviction-conditional sizing (#1) WILL improve realized
  Sharpe by 0.5-1.5σ on the new OOS window, BUT will likely STILL FAIL the strict §1 bar
  (DSR_OOS > 0.95). Why I expect this: cost atlas v1.0.0 is fixed and conservative; the magnitude-
  conditional improvement is real but bounded by the fundamental cost-to-edge ratio. I expect Round 4
  Q3 verdict to land at `DSR_OOS_filtered ∈ [0.4, 0.85]` — informative but below deployment threshold.
- **Moderate confidence (50-65%):** Label horizon swap (#2) MIGHT outperform sizing (#1) IF the end-of-day
  fade is genuinely a session-close-to-overnight-fade phenomenon (not an intraday-window phenomenon).
  Empirical question; 2025-07..2026-04 K3 PASS does not disambiguate the horizon question.
- **Low confidence (<35%):** Asymmetric exit (#3) materially outperforms #1 + #2. R-multiple barriers
  add nuisance variance through cost-layer interactions; theoretical motivation is weakest of the three.
- **Very low confidence (<15%):** Any single H_next candidate clears DSR_OOS > 0.95 strict on first
  pre-registered OOS observation. Most likely outcome is "all three FAIL but one is closest"; council
  Q3 2026 then adjudicates whether that closest gets a fresh extension or T003 retires too.

### §6.2 What I want NOT to bias the vote

I AUTHORED:
- T002 spec yaml v0.2.x (data_splits, kill_criteria, n_trials).
- Mira Gate 4b spec v1.2.0 (§1 strict thresholds, §15.13 PROPER unlock semantics).
- F2-T5 verdict, Round 3 verdict, Round 3.1 verdict, T002.6 IC pipeline deep audit.
- ESC-012 vote VOTE_PATH_B (which led to the current Round 3.1 outcome).

I have authorial investment in the predictor IP being genuinely reusable (it would validate my
Round 3.1 K3 PASS sub-classification). Disclosed for self-audit transparency.

To check it: I would still rank conviction-conditional sizing #1 if the predictor IP turned out to be
overfit (in that hypothetical, the recommendation would shift to "retire predictor; start fresh
with T003 hypothesis space"). The current ranking is explicitly grounded in K3 PASS evidence + AFML
calibration ranges; the ranking would invert under different evidence. The vote is not authorial.

### §6.3 What I would change my vote to

If the council surfaces evidence that:
- The predictor formula `−intraday_flow_direction(t)` has microstructural pathology Nova flags
  retrospectively (e.g., RLP or batched-trade contamination affecting flow direction in ways the
  Round 3.1 audit missed) — vote shifts to "retire predictor IP; defer H_next 1 epic".
- The cost atlas v1.0.0 is overstated in ways Riven flags (i.e., real costs are MATERIALLY less than
  modeled) — vote shifts to "rerun T002 N8.2 under reduced cost atlas BEFORE designing H_next; the
  costed_out_edge attribution may be cost-modeling artifact". (This is hypothetical only — user
  reframe in ESC-012 declared cost atlas FIXED.)
- A prior research literature finding shows end-of-day-fade phenomena on Brazilian futures has known
  regime-dependent decay that the F2 IS window happened to capture but H_next forward-time will not
  — vote shifts to mandatory regime-conditioning pre-test before H_next.

Otherwise, the vote is as written: top-3 candidates ranked, K=3 budget, forward-time hold-out, CPCV
unchanged + Bonferroni re-penalized.

---

## §7 Article IV self-audit (every clause traces; no invention)

| Claim category | Trace anchor |
|---|---|
| Round 3.1 K3 PASS COMPUTED at decay ratio 0.99991 | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1 + §2 (Mira authorship Round 3.1) + N8.2 `full_report.json:3-7,256` |
| Round 3.1 K1 OOS strict FAIL at DSR=0.205731 | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §2 + N8.2 `full_report.json:8` |
| `costed_out_edge_oos_confirmed_K3_passed` sub-classification | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md` §1.1 + ESC-013 §5(c) outcome decision tree |
| AFML §8.6 IC > 0.5 "exceptional" calibration | Lopez de Prado 2018 AFML §8.6 + ESC-012 Mira vote §4.1 |
| Bailey-LdP 2014 §3 multiple-testing penalty | Bailey-Lopez de Prado 2014 §3 + ESC-011 R9 NON-NEGOTIABLE Bonferroni binding |
| AFML §12 CPCV combinatorial purged cross-validation | Lopez de Prado 2018 AFML §12 + Mira spec yaml v0.2.3 §validation_scheme |
| Anti-Article-IV Guard #3 (hold-out untouched until preregistered unlock) | ESC-011 R3 + Mira spec yaml v0.2.3 §15.10 + Round 3.1 sign-off §6 |
| Anti-Article-IV Guard #4 (DSR > 0.95 thresholds UNMOVABLE) | ESC-011 R14 + ESC-012 R3 hash-frozen + Mira Gate 4b spec v1.2.0 §11.2 + Round 3.1 §1 |
| MANIFEST R15.2 spec versioning under major==0 | MANIFEST §15 + my activation rule (PRR schema 8 fields; pax_cosign_hash via scripts/pax_cosign.py compute) |
| Predictor formula `−intraday_flow_direction` at {16:55, 17:10, 17:25, 17:40} BRT | Mira spec yaml v0.2.3 §15.3 + F2-T5 Round 2 §3 + Round 3.1 §2 evidence table |
| n_trials carry-forward = 5 (T1..T5) | ESC-011 R9 + Mira spec yaml v0.2.3 §1.2 + N8.2 metrics `n_trials_source: docs/ml/research-log.md@fadacf482633c4d23cdaf21edc986ca1f879752b` |
| Cost atlas v1.0.0 FIXED (Path A OFF) | ESC-012 user reframe + ESC-012 resolution §1 binding constraint |
| Hold-out forfeited 2025-07-01..2026-04-21 (consumed by Phase G PROPER unlock 2026-05-01) | Round 3.1 sign-off §1 + N8.2 run_dir `data/baseline-run/cpcv-dryrun-auto-20260501-3fce65dab8f8/` + Anti-Article-IV Guard #3 |
| Riven 3-bucket post-mortem 10 anti-patterns | `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` (Riven authorship; this ballot proposes anti-pattern #11 as Mira-authored addition for Riven adoption) |
| Round 3.1 sharpe_mean / hit_rate / profit_factor OOS distribution | Round 3.1 sign-off §2 auxiliary table + N8.2 `full_report.json:237-242` |

### §7.1 Article IV self-audit verdict (7 anchor minimum honored)

7 named anchors traced explicitly above (rows 1-7). Every clause in §1-§6 maps to one of: T002 spec
yaml v0.2.3, Mira Gate 4b spec v1.2.0, Round 3.1 sign-off, ESC-011/012/013 resolutions, AFML / Bailey-LdP
literature canon, Riven 3-bucket post-mortem, MANIFEST §15 governance.

NO INVENTION:
- No new strategy formulas invented. Top-3 candidates are user-prompted (a/c/d); my scoring applies
  pre-existing Bonferroni / sample-size / falsifiability criteria.
- No threshold mutations. K1 strict 0.95 referenced AS-IS. K3 decay floor 0.5 referenced AS-IS;
  proposed tighten to 0.7 is SHOULD not MUST and explicitly conditional on Pax + Riven concurrence.
- No hold-out touch. This ballot does NOT read N8.2 raw artifacts beyond what is already in Round 3.1
  sign-off + ESC-013 resolution (council-ratified disclosures).
- No source code modification. No spec yaml mutation. No spec markdown mutation. No prior sign-off
  mutation.
- No reading of any other Round 4 ballot (Pax, Riven, Beckett, Aria, Kira, Sable) prior to authoring
  this ballot. Verified by ballot independence at branch main as of council date 2026-05-01.

NO PUSH performed (Article II — Gage @devops EXCLUSIVE authority preserved; this ballot is write-only
under MY authority, no `git add` / `git commit` / `git push` invoked per user prompt directive).

---

## §8 Mira cosign 2026-05-01 BRT — Quant Council Round 4 ballot

```
Author: Mira (@ml-researcher) — ML/statistical authority on this council per ESC-011 R8/R9/R11/R14 + Round 3.1 final-round authority
Council: Quant Council 2026-05-01 (alpha discovery direction post T002 retire)
Topic: Predictor IP reuse + H_next strategy candidates + new CV scheme + new hold-out + Bonferroni budget + new anti-pattern + personal preference disclosure
Constraint binding: cost atlas v1.0.0 FIXED (Path A cost-reduction OFF per ESC-012 user reframe)

§1 Predictor IP reuse:
  Top-3 candidates ranked (ML rigor lens):
    #1 (a) Conviction-conditional sizing (predictor magnitude P80; 1 hypothesis; n_filtered ~760 above R9 floor; clean kill via DSR_OOS_filtered > 0.95)
    #2 (d) Label-horizon swap to ret_to_close_BR 17:55 (1 hypothesis; full 3800 events; clean kill via DSR_OOS > 0.95 with new label)
    #3 (c) Asymmetric exit R-multiple (2 hypotheses; full 3800 events; clean kill via DSR_OOS > 0.95 with asymmetric barriers)
    REJECTED #4 (b) Multi-timeframe conditioning (regime filters expand family-wise; deferred to T003+ epic)

§2 New CV scheme:
  KEEP CPCV N=10 k=2 45 paths embargo=1 (unchanged from T002)
  ADD explicit Bonferroni RE-penalization on carry-forward base (n_trials_total = 5 + 3 = 8)
  OPTIONAL tighten K3 decay floor 0.5 → 0.7 (conditional on Pax + Riven concurrence)
  Embargo unchanged at 1 sessão (rejected user-prompted embargo=2 — structurally aligned; no rationale to inflate)

§3 Hold-out window:
  PRIMARY recommendation: forward-time 2026-05-01..2026-09-30 (5 months; data not yet exists at preregistration; impossible to leak)
  REJECTED reserve last 30% of new IS (creates ambiguity; risks predictor IP contamination)
  REJECTED walk-forward (rolling) (4 windows × 3 candidates = 12 trials; Bonferroni budget blow)
  FALLBACK if user wall-clock binding: hybrid 30% reserved IS + forward-time 5mo (defensible-suboptimal)

§4 New anti-pattern Round 4:
  Anti-pattern #11 (Riven post-mortem v3 candidate): "costed_out_edge_signature" diagnostic chain
    IC stable IS=OOS + DSR drops materially + Sharpe sign-flip = canonical costed_out_edge signature
    Sub-classification refinement to Riven Bucket B: costed_out_edge_oos_confirmed_K3_passed
    All future H_next candidates MUST report IC × DSR × Sharpe-sign jointly across IS and OOS

§5 Bonferroni budget K=3 for H_next:
  n_trials_carry_forward = 5 (T002 T1..T5 consumed)
  n_trials_new_for_H_next = 3 (top-3 candidates)
  n_trials_total = 8 (Bonferroni penalty re-computed against this)
  Research-log invariant: NEW commit hash `docs/ml/research-log.md@<NEW_HASH>` MUST land before new spec yaml hash-freezes
  K=3 sweet spot: K=2 arbitrary single-pick; K=5 family-wise-error blow; K=3 preserves diversity + discipline

§6 Personal preference disclosure: predictor reuse high-confidence (≥80%); top-3 ranking authorial-honest per AFML calibration; vote stable under counterfactual evidence

§7 Article IV self-audit: 7+ trace anchors (Round 3.1 sign-off + T002 spec yaml + Mira Gate 4b spec + ESC-011/012/013 resolutions + AFML/Bailey-LdP literature + Riven post-mortem + MANIFEST §15); NO invention; NO threshold mutation; NO hold-out touch by THIS ballot; NO push; NO source code modification; NO spec yaml/markdown mutation; NO prior sign-off mutation; NO reading of other Round 4 ballots prior to authoring

Independence: ballot authored without reading Pax, Riven, Beckett, Aria, Kira, or Sable Round 4 votes
Article II: NO push performed by Mira during this ballot. Gage @devops authority preserved for any subsequent commit/push (per user prompt: "NÃO commit. NÃO push.")
Article III (Story-Driven): this is a council ballot artifact, not a story implementation; lifecycle outside SDC scope per ESC-011/012/013 ratification format precedent
Anti-Article-IV Guards: #1-#8 ALL honored verbatim; new hold-out preregistration #3 (untouched until preregistered unlock) honored by forward-time data-not-yet-existing
Authority boundary: Mira issues this ballot; does NOT pre-empt Pax forward-research adjudication (story sequencing); does NOT pre-empt Riven F2-T6.1 reclassification authority (anti-pattern #11 is PROPOSED for Riven adoption); does NOT pre-empt Aria architecture review for new hold-out pipeline; does NOT pre-empt Kira hypothesis-generation lead for any expansion beyond top-3 K=3 budget

Cross-reference:
  Round 3.1 sign-off: docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md
  T002 retire ceremony: docs/qa/gates/T002.6-mira-gate-4b-signoff-round3-1.md §1 + ESC-013 §5(c)
  ESC-012 Mira vote: docs/councils/COUNCIL-2026-04-30-ESC-012-T002-strategy-fate-mira-vote.md
  T002.6 deep audit: docs/ml/audits/T002.6-mira-ic-pipeline-deep-audit.md
  Riven 3-bucket post-mortem (anti-pattern #11 candidate): docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md
  Cost atlas v1.0.0 FIXED: ESC-012 resolution
  MANIFEST R15.2 spec versioning: MANIFEST §15

Cosign: Mira @ml-researcher 2026-05-01 BRT — Quant Council Round 4 alpha discovery ballot — predictor IP reusable; top-3 H_next candidates ranked under K=3 Bonferroni budget; forward-time hold-out 2026-05-01..2026-09-30; CPCV unchanged + Bonferroni re-penalized; new anti-pattern #11 proposed for Riven adoption.
```

— Mira, mapeando o sinal 🗺️
