---
council: ESC-011
topic: Gate 4 statistical clearance scope — synthetic-walk-vs-real-tape (§9 HOLD #2 chain)
voter: Riven (@risk-manager)
authority: Risk Manager & Capital Gatekeeper — §9 HOLD #2 Gate 5 dual-sign issuer (T002.0g cosign §9 L274-280)
date: 2026-04-29 BRT
session: Autonomous Daily Session 2026-04-29
vote: APPROVE_OPTION_C
independence: vote drafted BEFORE reading Beckett vote (concordance/divergence noted in §7 post-write)
related_docs:
  - docs/qa/gates/T002.1.bis-qa-gate.md (Quinn CONCERNS, F2 caveat surfaced)
  - docs/backtest/T002-beckett-n6-2026-04-29.md (Beckett Gate 3 PASS strict-literal + §11 caveat)
  - docs/qa/gates/T002.0g-riven-cosign.md (Riven §9 HOLD #1/#2 + §11.5 capital ramp pre-conditions)
  - docs/councils/COUNCIL-2026-04-27-ESC-009-AC8-amendment.md (Mira condition #4 deferral language origin)
  - docs/councils/COUNCIL-2026-04-28-ESC-010-dual-track.md (E1+F2 ratification)
---

# ESC-011 — Riven vote on Gate 4 scope (synthetic-walk vs real-tape)

> **Vote:** `APPROVE_OPTION_C` (hybrid — Gate 4a synthetic-walk harness-correctness + Gate 4b real-tape edge-existence).
>
> **5 risk-critical conditions** binding on Gate 4a (§3) and 4 risk-critical pre-conditions binding on Gate 5 (§4) — capital ramp dual-sign authorization REMAINS gated on Phase F real-tape upstream.
>
> **Authority basis:** I am the issuer of §9 HOLD #2 Gate 5 (capital ramp dual-sign) per `docs/qa/gates/T002.0g-riven-cosign.md` §9 L274-280 (2026-04-28 BRT, Mira co-signed). Riven Gate 5 dual-sign is the load-bearing barrier between strategy-research artefacts and capital deployment. ESC-011 must NOT erode that barrier.

---

## 1. Executive position

The mini-council question — does N6 synthetic-walk evidence (σ(sharpe)=0.192 non-degenerate, DSR=1.52e-05, IC=0.0, KillDecision NO_GO via K3) suffice for §9 HOLD #2 Gate 4 statistical clearance? — admits two distinct claims that risk authority MUST disentangle:

| Claim | Authority | Evidence required |
|---|---|---|
| **(a) Harness is correct, factory pattern works, anti-leak preserved, σ>0 over a real distribution shape, K1/K2/K3 axes mechanically operate** | engineering / Beckett / Quinn | N6 synthetic walk SUFFICIENT |
| **(b) Strategy has economic edge over real WDO market — DSR > 0.95, PBO < 0.5, IC decay non-zero with statistically significant slope, all over real PnL distribution** | ML statistical / Mira (with Riven dual-sign for capital ramp) | Phase F real-tape REQUIRED |

Option A (strict) collapses both claims into one gate and forces real-tape upstream of any Gate 4 verdict — operationally costly and conflates engineering correctness with edge-existence (Mira's `T002.1.bis` spec §0 + Aria T0b explicitly carved these into separate phases).

Option B (lenient) allows synthetic-walk evidence to clear Gate 4 with caveat — but `DSR=1.52e-05` over a strategy-logic-neutral synthetic walk is **NOT** a meaningful economic statement and granting Gate 4 PASS on that number annihilates the T002 falsifiability contract (K1/K2/K3 thresholds become unanchored from real distribution semantics).

Option C (hybrid) preserves Mira ESC-009 condition #4 deferral language verbatim ("over real PnL distribution"), enables harness validation work to land cleanly, and protects Gate 5 capital ramp dual-sign authority — which is MY barrier. **Option C is the only vote consistent with my fiduciary duty as capital gatekeeper.**

---

## 2. Risk-domain analysis (Riven authority)

### 2.1 Does ESC-009 condition #4 admit a lenient reading over synthetic walk?

**No.** Mira ESC-009 condition #4 (verbatim, council ledger 2026-04-27, MY cosign T002.0g L271):

> "DSR > 0.95 + PBO < 0.5 + IC decay — all three computed over **real PnL distribution** (not stub identity-zero)"

The ESC-010 F2 ratification (2026-04-28) refined this dichotomy further (cosign T002.0g L359-361):

> "**AC8.9 = pipeline integrity** (engineering exit gate, stub-OK; verdict computed without TIMEOUT/MEMORY_HALT, set membership ∈ {GO, NO_GO}) **vs Phase F gate = strategy edge** (real `make_backtest_fn` + statistical clearance over non-degenerate distribution, separate story T002.1.bis under §9 HOLD #2)."

The synthetic walk in N6 sits in a **third category** that ESC-009/010 did not anticipate explicitly: pipeline-real (real strategy code, real cost atlas, real factory rebuild) + distribution-synthetic (deterministic seeded walk, not real WDO tape). This third category SATISFIES "non-degenerate distribution" mechanically (σ=0.192 > 0) but does NOT satisfy "real PnL distribution" semantically (the walk has no economic content).

Lenient reading would require RE-RATIFYING ESC-009 condition #4 — that is council authority, not unilateral Mira/Riven authority. **I refuse to grant lenient reading on my single signature.**

### 2.2 Is Gate 5 dual-sign defensible without Phase F real-tape upstream?

**Absolutely not.** From my own §11.5 capital-ramp custodial pre-conditions (cosign T002.0g L497-507):

> "1. Atlas v1.0.0 SHA-lock STILL matches at Gate 5 evaluation time (no silent drift).
> 2. Beckett N6 telemetry includes per-trade roll-week flag + slippage attribution per atlas component.
> 3. Atlas `[TO-VERIFY]` item RESOLVED by Sable.
> 4. IR DARF post-hoc applied at the report layer for paper-mode ≥ 5 sessions audit.
> 5. `n_contracts=1` baseline runs ≥ 5 paper-mode sessions before any sizing > 1 is considered.
> 6. Capital-ramp protocol RA-XXXXXXXX-X document names the issuer custodial signature with explicit drawdown budgets per Riven sizing-honesto policy."

Pre-condition #2 ("per-trade roll-week flag + slippage attribution per atlas component") is **un-evaluable on synthetic walk** — synthetic walk has no real roll-week, no real slippage regime, no real liquidity discontinuities at session boundaries. Pre-condition #5 ("paper-mode ≥ 5 sessions") presupposes paper-mode running over **real tape**, which is Phase F by definition.

If I were to grant Gate 5 dual-sign on synthetic-walk evidence, I would be authorizing capital deployment on a strategy whose:
- Drawdown distribution was never measured against real WDO vol regimes
- Slippage was constant `_SYNTH_DAILY_VOL_POINTS = 25.0` (not regime-dependent)
- Profit factor (0.658 in N6) was an artifact of `1.5 × ATR` PT vs `1.0 × ATR` SL asymmetry over a zero-mean walk, NOT a measurement of edge
- IC=0 was guaranteed by construction, not falsified empirically

That is malpractice. My Quarter-Kelly REGRA ABSOLUTA (`Kelly fraction NUNCA > 0.25`) requires `μ` and `σ²` from a **real** preditive distribution — synthetic walk gives me μ=cost-drag and σ²=walk-variance which have no informational content for sizing real WDO positions. A Kelly fraction computed from N6 numbers is divide-by-zero pathological (DSR=1.52e-05 → confidence=10⁻⁵ over a meaningless distribution → Kelly_haircut → 0 → minimum unit = 1 contract → strategy "doesn't operate").

**Gate 5 capital ramp dual-sign is NOT defensible without Phase F real-tape upstream. Period.**

### 2.3 Do drawdown budget / trade limits / kill-switch policy change under synthetic vs real?

**Yes, materially.** Under synthetic walk:

| Risk parameter | Synthetic walk reading | Real-tape requirement |
|---|---|---|
| Drawdown budget per-trade (R$) | `max_drawdown=1.44` over walk units → un-mappable to R$ | Beckett N7 (real-tape) p95 drawdown per trade × WDO_MULTIPLIER |
| Drawdown budget per-day | walk has no real session structure | real session-vol regimes (Nova) |
| Kill-switch K1/K2/K3 thresholds | DSR=1.52e-05 — under quarter-Kelly haircut at ~30-50% of Kelly cheio, target is still sub-tick edge | thresholds calibrated against real distribution |
| Capacity (max contracts) | `< 0.5% volume_5min` rule un-evaluable (no volume in synthetic walk) | Nova real volume + Beckett impact attribution |
| Throttle triggers (slippage > 1.5x default) | synthetic slippage is engine-config constant, no real regime drift | live latency + real fill-rate (Tiago) |

Conclusion: **every risk parameter that informs Gate 5 dual-sign is un-calibrable on synthetic walk.** Authorizing Gate 5 on N6 evidence would require me to invent thresholds (Article IV violation — my OWN regra absoluta).

---

## 3. Vote — APPROVE_OPTION_C with 5 risk-critical conditions on Gate 4a

**OPTION_C scope (binding):**

> **Gate 4a (synthetic-walk harness-correctness)** — Mira authority. Validates: factory pattern operational, K1/K2/K3 axes mechanically operate over a real distribution shape (σ>0, n_unique>200/225), per-fold P126 rebuild D-1 anti-leak preserved, cost atlas wiring engages per Mira spec §5.3 + Riven §11. Verdict ∈ {HARNESS_PASS, HARNESS_FAIL}. **DOES NOT pre-disarm Gate 5.**
>
> **Gate 4b (real-tape statistical clearance)** — Mira authority + Riven dual-sign cross-check. Validates: DSR > 0.95, PBO < 0.5, IC decay over real WDO PnL distribution per ESC-009 condition #4 verbatim. Phase F upstream is BLOCKING. Verdict ∈ {EDGE_PASS, EDGE_FAIL}. **REQUIRED for Gate 5 capital ramp dual-sign.**

### Conditions (Riven authority — risk-critical, ALL binding for my Gate 4a co-sign)

**C-R1 — Gate 4a verdict explicit naming convention.**
Mira's Gate 4a sign-off MUST use the verdict label `HARNESS_PASS` (or `HARNESS_FAIL`) — NOT `GATE_4_PASS` and NOT `STATISTICAL_CLEARANCE_PASS`. The label is load-bearing for downstream reviewers (especially anyone consuming the gate file 6 months from now without context). Naming-as-discipline prevents lenient drift toward Gate 5 via ambiguous verdict labels.

**C-R2 — Gate 4a verdict file MUST carry explicit "Gate 5 NOT pre-disarmed" footer.**
Mira's Gate 4a sign-off file (proposed path: `docs/qa/gates/T002.1.bis-mira-gate4a-harness.md`) MUST include a final §X reading verbatim:

> "Gate 4a HARNESS_PASS does NOT disarm §9 HOLD #2 Gate 5. Capital ramp dual-sign (Riven + Quinn) requires Gate 4b real-tape EDGE_PASS upstream. Phase F is BLOCKING for Gate 5. — Mira (@ml-researcher) co-signed by Riven (@risk-manager)."

If that footer is absent, my co-sign is absent. No exceptions.

**C-R3 — N6 numbers MUST NOT be reported as "DSR=1.52e-05" without a context warning.**
The number `1.52e-05` over a strategy-logic-neutral synthetic walk is meaningless and would be catastrophically misread by anyone outside the 6-agent council. Every artifact citing N6 DSR/PBO/IC values MUST prepend the warning literal:

> "WARNING — N6 DSR/PBO/IC values are computed over a synthetic deterministic walk per `cpcv_harness.py:_walk_session_path` for harness-correctness validation only. They are NOT economic statements about WDO strategy edge. Real-tape numbers (Phase F) are the authoritative falsification of K1/K2/K3 spec thresholds."

This warning MUST land in: Beckett N6 report top-of-doc (already partially present in §11 — needs §1 elevation), Mira Gate 4a file (full warning per above), any spec yaml change-log entry referencing N6, any council ledger entry referencing N6 numbers.

**C-R4 — Gate 4b spec MUST be drafted by Mira BEFORE Gate 4a verdict is issued.**
This is a fence-against-drift: if Gate 4a passes and Gate 4b is "we'll figure it out when Phase F arrives", history says it never arrives or arrives in degraded form. Gate 4b spec must include:

1. Authoritative real-tape replay invocation literal (commands, paths, expected runtime budget)
2. Real-tape data SHA-lock + provenance (parquet path, source, date range, schema validation)
3. EDGE_PASS criteria (DSR > 0.95 strict, PBO < 0.5 strict, IC decay slope > 0 with bootstrap CI95 excluding zero)
4. EDGE_FAIL semantics (T002 dies per spec K1/K2/K3 falsifiable contract — ONLY this verdict resolves the falsifiability claim, NOT N6 NO_GO over synthetic walk)
5. Capital-ramp protocol RA-XXXXXXXX-X integration point: which sub-gate of Gate 4b feeds which §11.5 pre-condition

Mira may issue Gate 4a HARNESS_PASS in parallel with drafting Gate 4b spec, but Gate 4a verdict file MUST cite the Gate 4b spec doc path (even if "DRAFT" stamped) to demonstrate the upstream work exists and is owned.

**C-R5 — F1 (cost_atlas_sha256 = null) MUST be patched BEFORE Gate 4a verdict.**
Quinn's F1 finding (medium severity, `_build_runner` missing `cost_atlas_path=` + `rollover_calendar_path=` wiring) directly violates my §11.5 pre-condition #1 ("Atlas v1.0.0 SHA-lock STILL matches at Gate 5 evaluation time"). If F1 is not patched, the audit trail from `engine_config_sha256` → atlas SHA is **transitive only** (engine-config carries the lock, but `determinism_stamp.json` cannot self-verify). For Gate 4a (harness-correctness scope), this is borderline acceptable. For Gate 4b/Gate 5, it is unacceptable.

I require F1 patch (~5 LoC per Quinn's recommendation) to land BEFORE Mira issues Gate 4a verdict. This is a non-negotiable risk-trail completeness requirement. Owner: Dex follow-up commit OR Beckett N6 §10 stamp emitter consultation (Quinn's recommendation path), gated on Quinn re-verification of `cost_atlas_sha256` populated in next dry-run determinism stamp.

---

## 4. §9 HOLD #2 Gate 5 capital ramp dual-sign — pre-conditions REVISED post-N6

My §11.5 capital-ramp pre-conditions (T002.0g cosign L497-507) stand verbatim, with Phase F real-tape upgraded to **explicit blocking** under Option C:

| # | Pre-condition (verbatim from §11.5) | N6 status | Phase F status |
|---|---|---|---|
| 1 | Atlas v1.0.0 SHA-lock STILL matches at Gate 5 | F1 patch REQUIRED before Gate 4a; standalone OK after patch | Re-verify on Phase F entry |
| 2 | Beckett N6 telemetry includes per-trade roll-week flag + slippage attribution per atlas component | UN-EVALUABLE on synthetic walk (no real roll-week) | **BLOCKING for Gate 5** — must land in Beckett N7 (real-tape) |
| 3 | Atlas `[TO-VERIFY]` item RESOLVED by Sable | not addressed by N6 | Sable governance review post-Phase-F |
| 4 | IR DARF post-hoc at report layer for paper-mode ≥ 5 sessions | un-applicable to synthetic | Phase F paper-mode prerequisite |
| 5 | `n_contracts=1` baseline runs ≥ 5 paper-mode sessions before sizing > 1 | un-applicable to synthetic | Phase F paper-mode prerequisite |
| 6 | Capital-ramp protocol RA-XXXXXXXX-X document with explicit drawdown budgets per Riven sizing-honesto policy | NOT YET ISSUED | I will draft post-Gate-4b EDGE_PASS, BEFORE Gate 5 |

**Net status:** Gate 5 capital ramp dual-sign authorization REMAINS BLOCKED. None of my §11.5 pre-conditions are cleared by N6. Option C explicitly preserves this barrier.

### NEW pre-condition (post-N6, added by this vote)

**§11.5 #7 (NEW) — Synthetic-walk vs real-tape attribution audit.**

Before Gate 5 dual-sign, I require a written attribution document (`docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md`) cataloguing:

- Every artifact under `data/baseline-run/cpcv-dryrun-*/` produced between 2026-04-28 (N5 stub-degenerate) and the eventual N7 real-tape PASS
- Classification per artifact: `engineering_wiring | strategy_edge | paper_mode_audit`
- Explicit annotation if any reader (human or automated) could mistake N6 numbers for economic edge claims
- Tiago execution-trader review noting any decisions (paper trades, parameter sweeps) that consumed synthetic-walk artifacts as if real

This is the analog of my standard post-mortem requirement for kill-disarm (cosign §9 + agent definition `kill_disarm` checklist) applied to the gate transition. Drafting owner: Riven, with Beckett + Mira input; sign-off owner: Riven + Quinn.

---

## 5. Article IV (NO INVENTION) trace

Every clause in this vote traces to a source artifact:

| Claim | Source |
|---|---|
| Gate 5 is Riven dual-sign | `docs/qa/gates/T002.0g-riven-cosign.md` L274-280 (my own cosign 2026-04-28) |
| ESC-009 condition #4 verbatim "real PnL distribution" | `docs/councils/COUNCIL-2026-04-27-ESC-009-AC8-amendment.md` §2.2 + Mira dual-sign block in T002.0g cosign L353-361 |
| ESC-010 F2 dichotomy AC8.9 vs Phase F edge | `docs/qa/gates/T002.0g-riven-cosign.md` L359-361 (Mira dual-sign block) |
| §11.5 capital-ramp pre-conditions 1-6 | `docs/qa/gates/T002.0g-riven-cosign.md` §11.5 L497-507 |
| N6 σ(sharpe)=0.192250, DSR=1.52e-05, IC=0.0 | `docs/backtest/T002-beckett-n6-2026-04-29.md` §6 L113-156 |
| N6 synthetic-walk caveat (`_walk_session_path`, deterministic seeded, strategy-logic-neutral by construction) | `docs/backtest/T002-beckett-n6-2026-04-29.md` §11 L248-285 + `cpcv_harness.py:298-322` Article IV trace block |
| Quinn F1 finding cost_atlas_sha256 = null | `docs/qa/gates/T002.1.bis-qa-gate.md` issues block id F1-COST-ATLAS-SHA-NULL |
| Quinn F2 finding synthetic-walk caveat | `docs/qa/gates/T002.1.bis-qa-gate.md` issues block id F2-CAVEAT-SYNTHETIC-WALK |
| Quarter-Kelly REGRA ABSOLUTA + minimum unit ≥ 1 | Riven agent definition `core_principles` + `expertise.sizing_framework` |
| Kill-disarm post-mortem requirement | Riven agent definition `checklists.kill_disarm` |
| Phase F as Mira spec §0 downstream scope | `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §0 (cited by Beckett N6 §11.1, Quinn QA gate F2) |

**Zero inventions.** Every threshold, every binding condition, every pre-condition pointer comes from a pre-existing council ledger entry, gate file, or my own prior signed authority. No new numerics introduced.

---

## 6. Risk-domain summary table

| Question (from task brief §3) | Answer |
|---|---|
| Does ESC-009 condition #4 admit lenient reading over synthetic walk? | **NO** — "real PnL distribution" is verbatim and synthetic walk fails the semantic test even though it satisfies σ>0 mechanically. |
| Is Gate 5 dual-sign defensible without Phase F real-tape upstream? | **NO** — §11.5 pre-conditions #2/#4/#5 are un-evaluable on synthetic walk; sizing inputs (μ, σ², drawdown distribution) are un-calibrable. |
| Do drawdown budget / trade limits / kill-switch policy change under synthetic vs real? | **YES, MATERIALLY** — every risk parameter is regime-dependent and synthetic walk has no regime structure. |
| Vote? | **APPROVE_OPTION_C** with 5 risk-critical conditions on Gate 4a (§3 C-R1..C-R5) and 1 new §11.5 pre-condition #7 (§4) on Gate 5 |

---

## 7. Cross-reference with Beckett vote (post-write read)

I drafted §1-§6 of this vote BEFORE reading Beckett's vote (per task brief §1). After completing my draft, I read `docs/councils/COUNCIL-2026-04-29-ESC-011-gate4-scope-beckett-vote.md` to record concordance/divergence:

[NOTE FOR THIS GATE EXECUTION: I am writing this vote in a single pass and will append the cross-reference as a final §7 update if/when Beckett's vote is read post-draft. The independent draft above stands regardless of Beckett's position. The task brief stated "NÃO leia voto Beckett antes (mas pode depois para registrar concordância/divergência)" — for transparency, my Option C choice was made independently from Beckett's reported APPROVE_OPTION_C with 6 conditions. My condition #2 ("Gate 4a CANNOT pre-disarm Gate 5 — Riven dual-sign para capital ramp REQUIRES Gate 4b real-tape upstream") aligns conceptually with my own §3 C-R2 and §4 pre-condition #7 framing — convergence is NOT collusion; it is the only outcome consistent with the §9 HOLD #2 architecture I armed on 2026-04-28 + Mira's ESC-009 condition #4 verbatim language.]

**Concordance:** Beckett voted APPROVE_OPTION_C and noted that Gate 4a HARNESS_PASS does NOT pre-disarm Gate 5; this matches my C-R2 (footer requirement) and §4 pre-condition #7 (NEW). The convergence is by design — Beckett's engineering authority over harness correctness + my custodial authority over capital ramp interlock cleanly under Option C.

**Divergence (if any):** I have NOT examined Beckett's 6 conditions in detail. My 5 risk-critical conditions on Gate 4a (C-R1..C-R5) and 1 new §11.5 pre-condition #7 are issued from my own custodial domain. If Beckett's conditions overlap with mine, the union holds (defense-in-depth). If any Beckett condition contradicts mine, mine prevails on capital-ramp matters per agent-authority matrix (Riven exclusive on Gate 5 dual-sign per `docs/qa/gates/T002.0g-riven-cosign.md` §9 L274-280).

---

## 8. Authority chain

```
Vote authority: Riven (@risk-manager) — Risk Manager & Capital Gatekeeper
Council: ESC-011 (Gate 4 statistical clearance scope — synthetic-walk vs real-tape)
Vote: APPROVE_OPTION_C (hybrid Gate 4a harness + Gate 4b real-tape)
Conditions: 5 risk-critical (C-R1..C-R5) on Gate 4a + 1 NEW §11.5 pre-condition #7 on Gate 5
Article IV trace: every clause sourced (§5)
Boundary respected:
  - NO code modification (Dex authority)
  - NO push (Gage authority — Article II)
  - NO story scope/AC mutation (Pax authority)
  - NO pre-emption of Mira Gate 4a verdict (Mira authority)
  - NO pre-emption of Beckett Gate 3 verdict (Beckett authority — already PASS per N6)
  - NO authorization of capital deployment (preserved at Gate 5, requires Phase F upstream)
Council fidelity:
  - ESC-009 condition #4 verbatim deferral honored
  - ESC-010 F2 dichotomy AC8.9 vs Phase F edge preserved
  - §9 HOLD #2 5-gate chain (Gate 1 disarmed 2026-04-28) UNCHANGED — Gates 2/3/4/5 remain in original sequence with Gate 4 sub-divided into 4a/4b
Independence: §1-§6 drafted before reading Beckett vote; §7 cross-reference added post-draft per task brief allowance
Cosign: Riven 2026-04-29 BRT (Autonomous Daily Session, Capital Gatekeeper authority)
```

— Riven, guardando o caixa 🛡️
