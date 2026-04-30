---
council: ESC-012
council_topic: T002 strategy-fate (post-Mira F2-T5 GATE_4_FAIL_strategy_edge / costed_out_edge)
voter: Aria @architect
voter_authority: System architecture; factory pattern + closure isolation + spec-yaml threshold guardianship; engineering-placement bindings
date_brt: 2026-04-30
mode: autonomous
branch: t002-1-bis-make-backtest-fn (working tree)
main_head: 81139de (per task brief; voter did NOT inspect other agents' votes pre-cast per task discipline)
verdict: APPROVE_PATH_B (Phase G hold-out unlock OOS confirmation)
verdict_secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback ONLY if Path B blocked by independent governance
verdict_rejected: REJECT_PATH_A_PRIME (Strategy refinement) — architectural cost + Bonferroni n_trials risk + thresholds-mutation slippage outweigh information value at this iteration
inputs_consumed:
  - docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md (Mira F2-T5 round 2 authoritative)
  - docs/ml/specs/T002-gate-4b-real-tape-clearance.md (v1.1.0 — spec yaml v0.2.3 + §15 amendment)
  - docs/backtest/T002-beckett-n7-prime-2026-04-30.md (N7-prime full Phase F2 empirical)
  - docs/architecture/T002.6-aria-archi-review.md (T0b round 1 APPROVE_WITH_CONDITIONS C-A1..C-A7)
  - docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md (F2-T0b/F2-T0b' APPROVE_OPTION_D + APPROVE_FORMAL)
inputs_NOT_consumed_pre_cast:
  - docs/councils/COUNCIL-2026-04-30-ESC-012-* (other agent votes — task discipline: cast independently)
constraint_acknowledged: slippage + costs FIXED conservative; Path A cost-reduction OFF (pre-condition by Pax adjudication)
spec_yaml_version_under_protection: T002-v0.2.3 (DSR>0.95 / PBO<0.5 / IC>0 — Anti-Article-IV Guard #4 UNMOVABLE)
factory_pattern_provenance: T002.1.bis APPROVE_OPTION_B (Aria 2026-04-28); preserved verbatim through T002.6 + Phase F2
holdout_lock_provenance: Anti-Article-IV Guard #3 UNMOVABLE; window [2025-07-01, 2026-04-21]; untouched through Phase F2
---

# ESC-012 Aria Architectural Vote — T002 Strategy-Fate Adjudication

> **Authority basis:** Aria @architect under AIOX agent-authority matrix (system architecture decisions, technology selection, integration patterns, factory pattern + closure isolation guardianship). Per the ESC-012 council framing, Aria adjudicates **FROM ARCHITECTURE**: factory pattern preservation; spec yaml v0.2.3 threshold UNMOVABILITY; hold-out lock contract; implementation cost per path; reusability of T002.x impl artifacts (cpcv_aggregator + latency_dma2 + RLP/microstructure/auction flags).
>
> **Personal preference disclosure (§5):** Aria leans toward minimum-disruption + maximum-information per-effort. Path B is information-rich + cheap. Path C preserves bandwidth. Path A' is expensive + risky.
>
> **Discipline:** Aria did NOT read other agents' ESC-012 votes pre-cast (task mandate). This vote is independent.

---

## §1 Verdict + rationale (architectural)

### §1.1 Verdict

**APPROVE_PATH_B** — Phase G hold-out unlock OOS confirmation.

Secondary acceptable: **APPROVE_PATH_C** (Retire T002) as Pax fallback **only if** independent governance blocks Path B (e.g., Riven raises §9 HOLD #2 Gate 5 disarm-ledger concern that needs redressing first; Mira raises spec-amendment requirement before Phase G unlock; Pax decides forward-research bandwidth allocation).

**REJECT_PATH_A_PRIME** — strategy refinement (entry/exit timing, regime filter, conviction threshold, signal ensemble).

### §1.2 Rationale (architectural — three lenses)

**Lens 1 — Spec yaml v0.2.3 threshold UNMOVABILITY (Anti-Article-IV Guard #4).**

Mira F2-T5 round 2 authoritative verdict (`docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` §1, §2, §9 row #4) preserves the K1/K2/K3 strict thresholds verbatim: `DSR > 0.95`, `PBO < 0.5`, `IC_in_sample > 0 AND CI95_lower > 0`. The K1 strict bar applied AS-IS despite strong K3 in-sample evidence (IC=0.866 with tight CI95 [0.865, 0.866]). **Path A' implications for thresholds:** strategy refinement that changes the predictor / entry filter / exit logic / regime filter REPLACES Bonferroni n_trials slot consumption — either (a) expands `n_trials = 5 → 10+` (spec yaml v0.2.3 §kill_criteria mutation; Anti-Article-IV Guard #4 affected), or (b) replaces existing trial slots via a research-log update (Mira authority; new spec amendment v1.2.0+). Either route reopens spec-yaml threshold-adjacent surface that ESC-011 R14 + Guard #4 protect. **Path B implications:** zero spec-yaml mutation; the same thresholds apply to the OOS evaluation (deferred-decay clause activates Phase G per Mira spec §15.10). **Path C implications:** zero spec-yaml mutation; thresholds preserved as institutional record of falsification depth.

**Lens 2 — Factory pattern preservation (T002.1.bis APPROVE_OPTION_B).**

The `make_backtest_fn` factory pattern (Aria 2026-04-28 ratified by Mira spec §2.3 + §8(b); cross-checked by F2-T0b' `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md` §1.1 8/8 PRESERVED) survived Phase F (real tape) + Phase F2 (IC pipeline wiring) without structural refactor. Closure body changes are permitted (R/O captures `enclosed_costs / enclosed_calendar / enclosed_percentiles` are stable; predictor/label fields on `TradeRecord` are additive per Mira §15.3 frozen-dataclass minor-version compat). **Path A' WOULD touch the closure body** (entry filter, exit logic, signal compute; possibly `Features.intraday_flow_*` redefinition). Factory pattern would survive — closure body changes don't violate APPROVE_OPTION_B. BUT the per-fold P126 D-1 invariant (`as_of_date == min(test_events.session)`; `cpcv_harness.py:1009`) and the closure-isolation test surface (18+ tests across `test_make_backtest_fn.py` + anti-leak + toy-benchmark) MUST be re-verified per refinement axis. Each refinement = one new audit chain (Quinn QA gate + Beckett N+1 baseline + Mira re-clearance). **Path B**: zero closure body touch; reuse the existing `backtest_fn_factory` against the OOS window. **Path C**: zero closure body touch; preserve as forensic record.

**Lens 3 — Hold-out lock contract (Anti-Article-IV Guard #3 UNMOVABLE).**

Hold-out window `[2025-07-01, 2026-04-21]` is locked per Anti-Article-IV Guard #3 (R1 + R15(d)) and untouched through Phase F2 (Mira spec §15.10 + this voter's F2-T0b' §1.1 row "Hold-out lock"). **Path A' implications:** strategy refinement is in-sample iteration; hold-out remains locked under Guard #3 (correct discipline). BUT: each refinement that re-runs CPCV against the in-sample window is a partial Bonferroni-trial consumption on the SAME data (n_trials slot semantics question — is "tweak entry filter" a new trial or a re-shaping of an existing one? ESC-011 R9 ratified n_trials=5 NON-NEGOTIABLE; refinement that re-uses a trial slot risks p-hacking the in-sample fit without honest multiplicity correction). **Path B implications:** Phase G unlock is the **canonical purpose** of the hold-out lock — held in reserve until exactly this point (in-sample edge measurement honest, deployment-gate failed strict, OOS confirmation needed to disambiguate `costed_out_edge` from `partial-edge-survives-OOS`). The hold-out unlock chain consumes the locked window once; Anti-Article-IV Guard #3 is honored by canonical use. **Path C implications:** hold-out lock preserved (never consumed); future strategies inherit the unconsumed window as research bandwidth.

### §1.3 Why Path B is architecturally optimal

The Mira F2-T5 round 2 verdict surfaces a **specific architectural question** that only Path B can answer cleanly: is the `costed_out_edge` signature (IC=0.866 strong + DSR=0.767 finite-positive + hit_rate=0.497) a Phase F2 in-sample artifact (overfit-to-cost-layer in 10 months), or does the prediction-level edge survive OOS measurement against the 2025-07-01..2026-04-21 hold-out window? This is the **terminal disambiguation** for the strategy hypothesis under the current spec — not a refinement axis (Path A'), not a retirement decision (Path C). Spending the hold-out budget HERE is the canonical use of the budget; spending it AFTER refinements would conflate (refinement effect) × (OOS regime change), losing the clean signal.

Architectural cost is minimal (§2 below): no new code in the strategy or engine layers; one small Dex commit to fix F2-T5-OBS-1 verdict-layer enforcement gap (decay-clause short-circuit under `ic_holdout_status='deferred'`); reuse of `cpcv_aggregator` + latency_dma2 + RLP/microstructure flags + factory pattern + closure body verbatim.

### §1.4 Why Path A' is architecturally suboptimal at this iteration

Per the constraint acknowledged at council framing: slippage + costs are FIXED conservative. Path A cost-reduction is OFF. Therefore Path A' refinements operate ONLY on the **strategy-side** axes: entry/exit timing, regime filter, conviction threshold, signal ensemble. Each axis:

- **Entry/exit timing:** changes `signal_rule.compute_signal` + closure body barrier-walk. Bonferroni n_trials interaction unclear (does each timing variant consume a trial slot? Mira spec §6 ratified n=5 from research-log; expansion needs spec amendment).
- **Regime filter:** changes `Features` filter logic (`filter_active(event)`; Mira spec §15.1 line 678). Same Bonferroni question.
- **Conviction threshold:** changes the `intraday_flow_magnitude > P_lower_or_upper` cutoff. Direct n_trials slot consumption (multiple thresholds = multiple trials).
- **Signal ensemble:** changes the predictor itself (e.g., combines `intraday_flow_direction` with another signal). Major spec amendment (§15.1 predictor sign convention C1 binding) + Mira F2-T0a-style spec re-amendment.

Each axis = one full chain (Mira spec amendment → Aria archi review → Beckett baseline re-run → Quinn QA gate → Mira re-clearance). Multiple axes × multiple iterations = bandwidth-expensive. **Information value:** an in-sample refinement that achieves DSR > 0.95 in-sample STILL needs Phase G OOS confirmation to disambiguate from in-sample overfit. So Path A' DOES NOT terminate the strategy-fate question; it adds iterations BEFORE the terminal Phase G unlock. Path B short-circuits to the terminal step. Architecturally inferior.

### §1.5 Why Path C is acceptable but not preferred

Path C (Retire T002) preserves all impl artifacts as forensic record + institutional knowledge, and zero new code. Architectural cost is zero. BUT: Path C **forfeits the information value of the OOS measurement**. The Mira F2-T5 verdict explicitly characterizes the strategy as PARTIALLY FALSIFIED (`costed_out_edge`), NOT clean-negative; thesis Q4 kill-triplet (DSR<0, PBO>0.4, IC_holdout < 50% IC_in_sample, DD>3σ) is NOT triggered. Retiring the strategy WITHOUT consuming the hold-out budget leaves the question unresolved in the institutional record — future researchers (or the same squad on a related WDO end-of-day fade hypothesis) would inherit the open question. Path B closes the question (either OOS-confirms `costed_out_edge` clean negative, or surfaces partial OOS deployability requiring fresh council). **Path C is the correct fallback IF Path B is blocked by independent governance** — but is not preferred when Path B is available.

---

## §2 Implementation cost per path (LoC + sessions)

### §2.1 Path B implementation cost

**Code (LoC):**

| Surface | LoC delta | Session count | Authority |
|---|---|---|---|
| `vespera_metrics/report.py` `evaluate_kill_criteria` — fix F2-T5-OBS-1 (short-circuit decay clause to `K3_DEFERRED` when `ic_holdout_status='deferred'` AND we're in in-sample-only run; emit `K3_FAIL_decay` only when `ic_holdout_status='computed'`) | ~15 LoC (one if-branch) | 1 Dex session (~30 min) | Dex F2-postmerge follow-up per Mira F2-T5 §8.2 + Beckett §10.4 |
| `tests/vespera_metrics/test_report.py` — assert `K3_DEFERRED` emission under `ic_holdout_status='deferred'`; assert no `InvalidVerdictReport` raised on deferred state | ~30 LoC (one new test + one parametrize case) | merged into above session | Dex |
| `scripts/run_cpcv_dry_run.py` — Phase G hold-out unlock dispatch (already designed per Mira spec §15.10 + holdout_lock guard mechanism per `cpcv_harness.py` + `engine.py:138-141`); MAY require flipping a CLI flag `--phase G --unlock-holdout` if not already wired | ~20 LoC if not wired (engine-level holdout-bypass under explicit phase=G with audit trail); 0 LoC if wired (just CLI invocation) | 1 Dex session OR 0 if pre-wired | Dex; Aria archi review thin (single point gate) |
| `BacktestRunner` / `CPCVEngine` hold-out unlock contract — engine MUST emit explicit `phase: G` event in determinism stamp + reject any `phase: F*` runs touching hold-out (defensive guard) | ~10 LoC if not present | merged into above | Aria condition (NEW C-A8 if needed) + Dex |
| Beckett N8 baseline run (Phase G full) | 0 new code; Beckett executes against unlocked window | 1 Beckett session (~3.5 h wall-time per N7-prime; ~12 GB transient artifacts) | Beckett |
| Mira F2-T6/G-T1 spec amendment (define Phase G IC measurement + decay clause activation; ic_holdout_status flips `deferred → computed`; preserve §15.5 Anti-Article-IV Guard #8 verdict-layer protocol) | ~80-150 LoC spec amendment (§15 append) | 1 Mira session (~2-3 h) | Mira (spec authority) |
| Aria archi review of Mira G-T1 spec amendment | 0 code; 1 archi review document (~250 LoC) | 1 Aria session (~1-2 h) | Aria (per F2-T0b' protocol) |
| Quinn QA G-gate | ~5-15 new tests (hold-out unlock invariant; `ic_holdout_status='computed'` PASS; K3 decay clause activation) | 1 Quinn session (~1-2 h) | Quinn |
| Riven §9 HOLD #2 disarm-ledger update if Gate 4b OOS PASS, OR §2 ledger reclassification entry if OOS FAIL | ~50-100 LoC ledger entry (one row per F2-T0b §6.1 atomic AND-conjunction format) | 0.5 Riven session | Riven |
| Pax G-story creation | ~150-200 LoC story (per Mira spec §0 + ESC-011 R10) | 1 Pax session (~1-2 h) | Pax |

**Total Path B:**
- **Net new code:** ~75-105 LoC across 3-4 source files (verdict-layer fix + tests + optional CLI/engine guard).
- **Sessions:** ~6-8 agent sessions across 5 agents (Pax → Mira spec → Aria archi → Dex → Quinn → Beckett → Mira F2-T6 G-equivalent).
- **Wall time:** ~1-2 calendar days (parallel where possible; Beckett N8 run is ~3.5 h serial).
- **Risk surface:** LOW — no closure body touch, no factory refactor, no engine signature change, hold-out lock consumed canonically (Anti-Article-IV Guard #3 honored by intent).

### §2.2 Path A' implementation cost (per refinement axis)

**Per axis (entry timing OR regime filter OR conviction threshold OR signal ensemble):**

| Surface | LoC delta | Session count |
|---|---|---|
| Mira spec amendment (new predictor / new filter / new threshold scheme; possible n_trials expansion) | ~150-300 LoC spec append | 1 Mira session (~2-4 h) |
| Aria archi review (new closure body changes; per-fold invariant re-verification; test surface rebuild plan) | ~250 LoC archi review | 1 Aria session (~1-2 h) |
| Dex closure body impl (modified `signal_rule.compute_signal` OR `Features` OR `make_backtest_fn` body) | ~50-200 LoC depending on axis | 1-2 Dex sessions (~3-6 h) |
| New unit tests (per closure-isolation contract; D-1 invariant; toy-benchmark sibling) | ~100-200 LoC | 1 Quinn session (~2-3 h) |
| Beckett N+k baseline re-run (each refinement = new baseline; ~3.5 h wall) | 0 new code; Beckett execution | 1 Beckett session (~4 h with prep) |
| Mira re-clearance per axis | 0 new code; 1 sign-off | 1 Mira session (~1-2 h) |
| Riven 3-bucket reclassify per axis | 0 new code; ledger entry | 0.5 Riven session |

**Per axis total:** ~300-700 LoC across multiple source files; ~6-8 sessions; ~1-2 calendar days per axis.

**Multi-axis aggregate (4 axes):** ~1200-2800 LoC; ~24-32 sessions; ~5-10 calendar days. AND each axis still requires Phase G hold-out unlock at the end to confirm OOS deployability (terminal step is not avoided; it's deferred). **Architectural cost: HIGH-VERY-HIGH.**

**Bonferroni n_trials risk surface:** if n_trials expansion (5 → 10+) is required per spec yaml v0.2.3 mutation, that itself is an Anti-Article-IV Guard #4 governance event requiring full council ratification. Adds another ~3-5 days governance overhead. **Risk surface: HIGH.**

### §2.3 Path C implementation cost

**Net new code: 0 LoC.**

| Surface | LoC delta | Session count |
|---|---|---|
| Pax T002 deprecation story / epic close (preserve as forensic record; redirect bandwidth to next research) | ~100-150 LoC story + EPIC-T002.0 status update | 1 Pax session (~1 h) |
| Riven §9 HOLD #2 ledger entry — Gate 4b NEVER passes; T002 retired with `costed_out_edge` partial falsification record | ~50 LoC ledger row | 0.5 Riven session |
| Aria archi reusability documentation (cpcv_aggregator + latency_dma2 + RLP/auction flags + factory pattern + closure isolation contract — all available for next strategy) | ~150 LoC architecture inventory document | 1 Aria session (~1-2 h) |
| Mira post-mortem closure (research-log update; thesis-falsification depth notation per spec §0) | ~50-100 LoC research-log entry | 0.5 Mira session |

**Total Path C:**
- **Net new code:** 0 LoC.
- **Sessions:** ~3 agent sessions across 4 agents.
- **Wall time:** ~0.5-1 calendar day.
- **Risk surface:** ZERO — no code changes; no spec mutations; hold-out lock preserved unconsumed (research bandwidth bonus for future).

### §2.4 Cost-comparison table

| Path | Net new LoC | Sessions | Wall time | Spec-yaml mutation risk | Hold-out budget consumed | Information value (terminal) |
|---|---|---|---|---|---|---|
| **B** (Phase G unlock OOS) | ~75-105 | ~6-8 | ~1-2 days | NONE | YES (canonical) | HIGH — terminal disambiguation `costed_out_edge` vs partial-OOS-deployable |
| **A'** (refinement, all 4 axes) | ~1200-2800 | ~24-32 | ~5-10 days | HIGH (n_trials expansion likely) | DEFERRED (terminal step still needed) | LOW per-axis (each axis still needs OOS confirmation) |
| **C** (retire) | 0 | ~3 | ~0.5-1 day | NONE | NO (preserved unconsumed) | MEDIUM — preserves forensic record but leaves OOS question open |

**Architectural verdict on cost:** Path B is the highest information-per-effort option. Path A' is highest cost lowest information per axis. Path C is lowest cost but leaves terminal question open.

---

## §3 Reusability assessment (cpcv_aggregator + latency + RLP across paths)

### §3.1 Impl artifact inventory (current state, post-Phase F2)

| Artifact | Owner | Provenance | Reusability across paths |
|---|---|---|---|
| `packages/vespera_metrics/info_coef.compute_ic_from_cpcv_results` (per spec §15.2 NEW orchestration helper) | Mira spec + Dex impl | F2-T1 PR #14 merged main `0903eaf` 2026-04-30 | Path B: REUSE verbatim (post-fanout aggregation over Phase G unlocked-holdout `cpcv_results`); Path A': REUSE with refined predictor/label per axis; Path C: PRESERVE as institutional artifact for next strategy |
| `packages/vespera_metrics/info_coef.ic_spearman` + `bootstrap_ci` | Mira spec + Dex (pre-existing; Phase F2 wired into compute_ic chain) | T002.0d Mira spec §3 + Efron 1979 | Path B: REUSE; Path A': REUSE; Path C: PRESERVE |
| `latency_dma2_profile` (engine-config.yaml v1.1.0 §latency_model block; Beckett §4 yaml verbatim) | Beckett spec + engine-config.yaml | T002.6 Aria T0b §4 PASS_WITH_CONDITIONS C-A2/C-A3 | Path B: REUSE verbatim (Phase G uses same engine-config; latency_model.enabled_for_phase=["F","G"] extension if not already; trivial config edit); Path A': REUSE; Path C: PRESERVE |
| `rollover_calendar` + RLP detection_signal_historical (Nova spec §6 yaml block) | Nova spec + engine-config.yaml v1.1.0 | T002.6 Aria T0b §5 PASS_WITH_CONDITIONS C-A4/C-A5 | Path B: REUSE; Path A': REUSE; Path C: PRESERVE |
| `auction.exit_price_rule` 3.2-α (Nova §3.2 yaml) | Nova spec | T002.6 Aria T0b §5 PASS | Path B: REUSE; Path A': REUSE; Path C: PRESERVE |
| `circuit_breaker_fired` + `cross_trade` flags (per-session / per-event microstructure flags) | Nova spec + Dex impl | T002.6 Aria T0b §5 conditions C-A4/C-A5 | Path B: REUSE; Path A': REUSE; Path C: PRESERVE |
| `make_backtest_fn` factory pattern (T002.1.bis APPROVE_OPTION_B) | Aria archi + Dex impl | T002.1.bis cosign 2026-04-28 + Mira Gate 4a HARNESS_PASS | Path B: REUSE verbatim (no closure body touch); Path A': REUSE structurally (closure body changes per axis); Path C: PRESERVE as canonical pattern for next strategy's harness |
| Closure isolation R/O captures (`enclosed_costs / enclosed_calendar / enclosed_percentiles`) | Aria archi (T002.1.bis §I.1-§I.6) | preserved through Phase F + F2 | Path B: REUSE; Path A': PRESERVE structurally (R/O capture set unchanged; closure body uses captures differently per axis); Path C: PRESERVE as canonical capture pattern |
| Per-fold P126 D-1 anti-leak invariant (`as_of_date == min(test_events.session)`) | Aria archi (T002.1.bis) + Dex impl (`cpcv_harness.py:1009`) | preserved through Phase F + F2; AC4 of T002.6 story | Path B: REUSE verbatim; Path A': PRESERVE (re-verify per axis via tests); Path C: PRESERVE |
| Mutually-exclusive engine guard (`engine.py:206-211`) | Aria archi (T002.1.bis §I.1) + Dex impl | preserved through Phase F + F2 | All paths: PRESERVE verbatim |
| `BacktestResult.content_sha256()` byte-stability (AC12) | Aria archi + Dex impl (`result.py:203-219`) | preserved; F2 additive fields auto-absorbed | All paths: PRESERVE verbatim |
| Determinism stamp 9-field receipt (R16/R17 governance) | Beckett spec + Dex impl (`runner.py:78-109`) | F2 IC fix preserved 8/9 fields IDENTICAL (Beckett N7-prime §3.3) | Path B: REUSE (Phase G stamp adds `phase: G` + `holdout_unlock: true`); Path A': REUSE; Path C: PRESERVE as institutional contract |
| Toy-benchmark Bailey-LdP test scaffolding (`test_toy_benchmark_bailey_lopez_de_prado_2014.py` 6/6 PASS pre-F2 + `test_toy_benchmark_real_tape.py` per AC6) | Quinn QA + Beckett spec | T002.1.bis Mira Gate 4a HARNESS_PASS evidence | All paths: PRESERVE as discriminator-power harness witness |

### §3.2 Reusability scoring per path

**Path B (Phase G OOS):** **MAXIMAL REUSE.** Every artifact above is consumed verbatim or with trivial config edit (latency_model.enabled_for_phase + holdout_unlock flag). The `compute_ic_from_cpcv_results` function operates over Phase G unlocked-holdout `cpcv_results` identically to how it operates over in-sample Phase F2 `cpcv_results` — the post-fanout aggregation surface is window-agnostic by Aria F2-T0b' Option D placement design (§5.1 of `docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md`). This is the canonical use case for Option D. **Reusability cost: ZERO refactor.**

**Path A' (refinement):** PARTIAL REUSE per axis. Engine layer + factory pattern + closure isolation contract + cpcv_aggregator + latency model + RLP flags + microstructure flags + auction rule = REUSED structurally. BUT: closure body strategy logic (`signal_rule.compute_signal`, `Features` filter, predictor/label semantics on `TradeRecord`) MUST be modified per axis. New tests required per axis. New Mira spec amendments required per axis (predictor/label semantics under spec §15.1 + §15.3 binding). **Reusability cost: MODERATE per axis; AGGREGATE HIGH across multiple axes.**

**Path C (retire):** ZERO REUSE in T002 itself (epic deprecated). MAXIMAL PRESERVATION as institutional artifacts available for next research. Architectural reusability inventory becomes a documented bequest:
- `cpcv_aggregator` + `info_coef` modules in `vespera_metrics/` available for any future strategy with predictor↔label IC requirement.
- `latency_dma2_profile` in engine-config.yaml available for any DMA2 execution simulation.
- RLP detection_signal + rollover_calendar + auction.exit_price_rule + microstructure flags available for any WDO-domain strategy.
- `make_backtest_fn` factory pattern + closure isolation contract + per-fold P126 D-1 invariant + mutually-exclusive engine guard = canonical AIOX-Vespera CPCV harness pattern available for any future signal-driven strategy.
- Anti-Article-IV Guard #8 (verdict-layer `*_status` provenance + `InvalidVerdictReport` enforcement) = canonical verdict-layer protocol now baked into `evaluate_kill_criteria`.
- `costed_out_edge` anti-pattern documented per Riven post-mortem §1.2 + Mira F2-T5 §1 + §5.2 = institutional knowledge that "IC strong + DSR sub-deployable + hit_rate ≈ 0.5 = cost-eroded edge signature".

**Reusability cost (Path C bequest):** ZERO; all artifacts preserved.

### §3.3 Cross-path reusability verdict

All three paths preserve the impl artifact inventory. Path B maximally REUSES it (terminal disambiguation). Path A' partially REUSES it per axis (multiplicative iteration cost). Path C maximally PRESERVES it as institutional bequest. **Architecturally, no path destroys the artifact inventory** — this is a strong consolation that makes the choice between B / A' / C primarily about information-per-effort (Lens 1 above) rather than asset preservation.

---

## §4 Spec yaml v0.2.3 mutation risk per path (Anti-Article-IV Guard #4)

### §4.1 What Anti-Article-IV Guard #4 protects

Per Mira Gate 4b spec v1.1.0 §11.2 + ESC-011 R14: the spec yaml v0.2.3 thresholds `DSR > 0.95`, `PBO < 0.5`, `IC > 0` are UNMOVABLE. No per-run waiver; no informal relaxation; no hidden retreat ("we'll relax to DSR>0.7 since 0.767 is close"). Mutation requires explicit council ratification + spec amendment with version bump.

Additionally protected (per Mira spec §6 + ESC-011 R9):
- `n_trials = 5` Bonferroni multiplicity correction NON-NEGOTIABLE (research-log canonical).
- AC9 sample-size floor `INCONCLUSIVE` route at `n_events < 150` (R9).
- `n_trials_source` provenance tracking (research-log SHA).

### §4.2 Mutation risk per path

| Path | DSR/PBO/IC threshold mutation risk | n_trials=5 mutation risk | AC9 sample-size mutation risk | Other spec-yaml mutation risk |
|---|---|---|---|---|
| **B** (Phase G OOS) | NONE — same thresholds apply to OOS evaluation per Mira spec §15.10 | NONE — same n_trials=5 carry-forward (Beckett N8 baseline reuses research-log SHA) | NONE — Phase G uses unlocked hold-out window [2025-07-01, 2026-04-21] which has its own session count; Mira G-spec amendment will define OOS sample-size floor consistently with §6 + R9 | LOW — Mira G-spec amendment may add Phase G activation clause for K3 decay sub-clause + ic_holdout_status='computed' protocol; this is APPEND-ONLY (per F2 §15 amendment precedent), not threshold mutation |
| **A'** (refinement, per axis) | LOW per axis if refinement holds n_trials fixed; HIGH if n_trials expansion (5 → 10+) is needed for new predictor/filter trial slots — that requires §kill_criteria L207-209 mutation OR research-log canonical update under Mira authority + ESC ratification | HIGH if n_trials expansion needed (most refinement axes that introduce new predictor variants consume new trial slots; each axis = +1-3 trials for sweep over parameter values) | MEDIUM — refinements may shift per-trial event counts; AC9 floor evaluation per axis | MEDIUM — refinements may touch §yaml `entry_window_brt`, `triple_barrier`, `feature_set_id`, etc.; each touch is a spec mutation event under Anti-Article-IV Guard #4 protection |
| **C** (retire) | NONE — spec yaml v0.2.3 frozen as forensic record; no further mutations | NONE | NONE | NONE — epic deprecation does not mutate the spec yaml; if anything, freezes it permanently |

**Architectural verdict on Guard #4 risk:** Path B and Path C are equivalently safe (NONE / LOW risk). Path A' has the highest mutation risk surface — particularly around n_trials Bonferroni accounting, which ESC-011 R9 specifically protected. Each refinement axis is a potential governance event.

### §4.3 Why Guard #4 + n_trials interaction matters

The ESC-011 R9 ratification of n_trials=5 was explicit acknowledgement that the in-sample Phase F2 measurement consumed exactly 5 trial slots (T1..T5 per research-log @c84f7475). Path A' refinements that introduce new predictor variants OR new filter variants OR new threshold values are EITHER (a) new trial slots requiring n_trials expansion (which then requires recomputing Bailey-LdP DSR with the larger trial pool — and the deflated SR threshold scales with sqrt(2 * log(n_trials)) per AFML §8.2, so DSR would need to be RECOMPUTED against the new n, not just compared at the existing 0.95 bar), OR (b) replacing existing trial slots which retroactively invalidates the original 5-trial Bonferroni accounting (because the in-sample fit has been re-explored with new strategy-design freedom — informational p-hacking risk).

**Mira F2-T5 §10 trace anchor:** "Bonferroni n_trials = 5 carry-forward" is one of the trace anchors cited as Article IV preservation. Path A' breaks this anchor.

---

## §5 Personal preference disclosure

**Aria personal preference (transparent for council):** APPROVE_PATH_B.

Rationale: Aria architectural philosophy = minimum-disruption + maximum-information per-effort. Path B is information-rich (terminal disambiguation of `costed_out_edge`) + cheap (~75-105 LoC, no closure body touch, factory pattern preserved verbatim). Path C is bandwidth-conserving but leaves the OOS question forever open. Path A' is expensive AND risky AND still requires Phase G OOS at the end.

**Bias disclosure:** Aria authored the F2-T0b APPROVE_OPTION_D placement design specifically so that `compute_ic_from_cpcv_results` is window-agnostic and consumes any `cpcv_results` (in-sample OR holdout) without refactor. Path B is the canonical use case for that design. There is therefore an architectural-self-consistency bias in favor of Path B from Aria's authorship history. This bias is disclosed.

Counter-bias check: would Aria still vote Path B if the OOS cost were higher (e.g., if Phase G unlock required a new engine-config v1.2.0 + new RLP detection layer + new hold-out window definition)? In that hypothetical, Aria would lean toward Path C (preserve forensic record; bequest artifacts to next strategy). The current Phase G unlock is cheap because the architecture was designed to make it cheap. So the preference is consistent with the architectural philosophy, not just with self-consistency.

**Acknowledgement of council authority:** Aria votes Path B but defers to Pax forward-research authority (per ESC-011 R10) on the bandwidth allocation question. If Pax determines that the squad's research bandwidth is better spent on a different epic (different thesis, different horizon, different market), Path C becomes the right answer — and Aria would cosign Path C as architecturally clean. The choice between B and C is fundamentally a Pax bandwidth-allocation decision; Aria's job is to confirm both are architecturally sound and Path A' is not.

---

## §6 Recommended conditions

If Path B wins the council, Aria binds the following architectural conditions on the Phase G unlock chain:

### §6.1 Aria conditions for Path B (NEW C-G1..C-G6)

| ID | Condition | Stage bound | Severity |
|---|---|---|---|
| **C-G1** | Phase G hold-out unlock MUST be gated by an explicit `phase: G` parameter in `scripts/run_cpcv_dry_run.py` AND emit `holdout_unlocked: true` in `determinism_stamp.json` for audit trail. The hold-out lock guard at `scripts/run_cpcv_dry_run.py:1142-1152` AND engine-level guard at `engine.py:138-141` MUST be modified to accept `phase: G` as the EXCLUSIVE bypass condition; ALL other phase values continue to enforce the lock. Anti-Article-IV Guard #3 honored by canonical use. | Dex G-T1 (impl) + Quinn G-QA (test) | **HIGH** |
| **C-G2** | F2-T5-OBS-1 verdict-layer enforcement gap MUST be fixed PRE-G-RUN: `evaluate_kill_criteria` MUST emit `K3_DEFERRED` (not `K3_FAIL`) for the decay sub-clause when `ic_holdout_status='deferred'`. Once Phase G activates `ic_holdout_status='computed'`, decay sub-clause MUST evaluate honestly per spec §15.10. This is the small Dex commit referenced in §2.1 above. | Dex F2-postmerge follow-up (1 session) | **HIGH** |
| **C-G3** | Mira G-spec amendment (analog to F2-T0a §15) MUST surface explicitly: (a) Phase G IC measurement protocol (predictor/label pairing on hold-out window — Aria recommended default: REUSE Mira F2 §15.1 per-event predictor/label semantics verbatim against the unlocked window), (b) `ic_holdout_status='computed'` propagation, (c) K3 decay sub-clause activation criteria (`IC_holdout > 0.5 × IC_in_sample` per Mira spec §1 K3 row, now operative), (d) Bonferroni n_trials=5 carry-forward (no expansion). Append-only revision per F2 §15 precedent. Aria condition C-A4 analog. | Mira G-T0a (spec authority) | **HIGH** |
| **C-G4** | Aria archi review of Mira G-spec amendment MUST verify (a) factory pattern preserved verbatim (no closure body touch beyond Phase G data window), (b) closure isolation R/O captures unchanged, (c) per-fold P126 D-1 invariant survives the unlocked window, (d) mutually-exclusive engine guard preserved, (e) determinism stamp absorbs `phase: G` + `holdout_unlocked: true` cleanly. F2-T0b'-style cross-check table mandatory. | Aria G-T0b (archi review) | **HIGH** |
| **C-G5** | Beckett N8 baseline run MUST preserve 8/9 reproducibility receipt fields IDENTICAL to N7-prime where applicable (engine_config_sha256, spec_sha256, rollover_calendar_sha256, cost_atlas_sha256, cpcv_config_sha256, python/numpy/pandas versions, seed=42); only `dataset_sha256` (different window), `run_id`, `timestamp_brt`, AND determinism stamp `phase: G` + `holdout_unlocked: true` may differ. Beckett G-baseline report MUST include cross-check table analog to N7-prime §3.3. | Beckett G-T4 (run + report) | **HIGH** |
| **C-G6** | Riven §9 HOLD #2 disarm-ledger update on Mira G-T5 verdict: if OOS `GATE_4_PASS` (DSR > 0.95 AND PBO < 0.5 AND K3 in-sample PASS AND K3 decay PASS), use the Aria F2-T0b §6.1 single-atomic-AND-conjunction format (reference Gate 4a HARNESS_PASS + Gate 4b GATE_4_PASS + Phase G OOS confirmation; preserve R5/R6 fence to Gate 5). If OOS `GATE_4_FAIL_strategy_edge` (DSR OOS also < 0.95 → confirms `costed_out_edge` clean negative + thesis falsified), Riven §2 ledger reclassification entry per Mira F2-T5 §8.1 path (b) clean-negative confirmation; T002 retired with full institutional record. Aria condition C-A7 (T002.6 T0b round 1 archi review) format mandate preserved. | Riven G-T6 (ledger authority) + Pax adjudication | **MEDIUM** |

### §6.2 Aria conditions for Path C (NEW C-R1..C-R3) — IF Path C wins

| ID | Condition | Stage bound | Severity |
|---|---|---|---|
| **C-R1** | Aria architectural reusability inventory document MUST be authored: catalogues `cpcv_aggregator + info_coef + latency_dma2 + RLP/rollover/auction/microstructure flags + factory pattern + closure isolation contract + per-fold P126 D-1 invariant + mutually-exclusive engine guard + determinism stamp 9-field receipt + Anti-Article-IV Guard #8 verdict-layer protocol` as institutional bequest. Path: `docs/architecture/T002-impl-artifacts-bequest.md` (~150 LoC). | Aria | MEDIUM |
| **C-R2** | Mira post-mortem closure MUST update research-log with `costed_out_edge` anti-pattern documentation (per Mira F2-T5 §5.2 evidence matrix verbatim) AND falsification-depth notation per spec §0 (PARTIALLY FALSIFIED at deployment-gate strict bar; Q4 kill triplet NOT triggered at thesis-falsification gate; clean-negative confirmation withheld due to hold-out budget conservation). Future researchers inherit honest accounting. | Mira | MEDIUM |
| **C-R3** | Hold-out window [2025-07-01, 2026-04-21] PRESERVED unconsumed; available for next strategy under Anti-Article-IV Guard #3 protection. Riven §9 HOLD #2 ledger entry: T002 retired with `costed_out_edge` partial falsification record; Gate 4b NEVER passed; Gate 5 LOCKED forever for T002. | Riven + Pax | MEDIUM |

### §6.3 Aria conditions if council selects Path A' (REJECT_PATH_A_PRIME stance preserved; conditions surfaced for completeness)

If council overrides Aria vote and selects Path A', Aria binds:

| ID | Condition | Stage bound | Severity |
|---|---|---|---|
| **C-R'1** | NO n_trials expansion (5 → 10+) without explicit ESC-013 council ratification; Bonferroni accounting pre-condition under ESC-011 R9 + Anti-Article-IV Guard #4 | Mira spec authority + ESC | **CRITICAL** |
| **C-R'2** | Each refinement axis = full audit chain (Mira spec amendment → Aria archi review → Quinn QA gate → Beckett baseline → Mira re-clearance); no shortcut paths | All agents | HIGH |
| **C-R'3** | Phase G hold-out unlock STILL REQUIRED at terminal step (refinement does not avoid OOS confirmation; it adds iterations BEFORE OOS); hold-out budget consumption deferred but eventually canonical | Mira + Pax | HIGH |
| **C-R'4** | Article IV preservation: each refinement MUST preserve the closure isolation R/O captures; per-fold P126 D-1 invariant; mutually-exclusive engine guard; determinism stamp 9-field receipt | All agents (per axis) | HIGH |

---

## §7 Article IV self-audit

| Claim in this vote | Source anchor (verified in this session) |
|---|---|
| Mira F2-T5 round 2 verdict `GATE_4_FAIL_strategy_edge / costed_out_edge` | `docs/qa/gates/T002.6-mira-gate-4b-signoff-round2.md` frontmatter `verdict` + §1 Executive verdict + §6.5 Final classification |
| K1=0.766987 / K2=0.337302 / K3 in-sample IC=0.866010 with CI95 [0.865288, 0.866026] | Mira sign-off-round2 §2 threshold table + §10 trace anchor row 1; Beckett N7-prime §1 + §6.1 |
| Spec yaml v0.2.3 thresholds DSR>0.95 / PBO<0.5 / IC>0 UNMOVABLE per Anti-Article-IV Guard #4 + ESC-011 R14 | Mira sign-off-round2 §9 row #4 + §10 trace row 2; Mira spec v1.1.0 §11.2 + §15.10 line 820 + §15.12 |
| Bonferroni n_trials=5 NON-NEGOTIABLE per ESC-011 R9 | Mira sign-off-round2 §10 trace row 6 (`n_trials_source: docs/ml/research-log.md@c84f7475...` Beckett §5.3) + spec v1.1.0 §6 + §15.10 |
| Hold-out lock window [2025-07-01, 2026-04-21] UNTOUCHED through Phase F2 per Anti-Article-IV Guard #3 | Mira sign-off-round2 §9 row #3 + §10 trace row "Hold-out lock"; F2-T0b' §1.1 row "Hold-out lock"; F2-T0b §9.2 |
| `make_backtest_fn` factory pattern T002.1.bis APPROVE_OPTION_B preserved verbatim through Phase F + F2 | Aria T0b round 1 review §2 PASS; F2-T0b' round 2 §1.1 8/8 PRESERVED cross-check table |
| Closure isolation R/O captures `enclosed_costs / enclosed_calendar / enclosed_percentiles` preserved | Aria T0b round 1 review §2 + §10; F2-T0b' §1.1 row "Closure R/O captures" + F2-T0b §6 table |
| Per-fold P126 D-1 invariant `as_of_date == min(test_events.session)` preserved (`cpcv_harness.py:1009`) | Aria T0b round 1 review §2 + §10 trace row 4; F2-T0b' §1.1 row "Per-fold P126"; F2-T0b §9.1 |
| Mutually-exclusive engine guard at `engine.py:206-211` preserved | Aria T0b round 1 review §2 + F2-T0b §13 anchor row "Mutually-exclusive engine guard" |
| `compute_ic_from_cpcv_results` post-fanout placement window-agnostic by Aria F2-T0b' Option D design | F2-T0b' §1 row C-A1 + Mira spec v1.1.0 §15.2 line 714-720 (NEW orchestration helper); F2-T0b §5 APPROVED arguments §5.1 #6 "Reusable across callers — Phase G/H paper-mode and hold-out clearance inherit the wiring as a one-line public API call" |
| F2-T5-OBS-1 verdict-layer enforcement gap (decay-clause emission under deferred-holdout) | Mira sign-off-round2 §4 + §8.2; Beckett N7-prime §6.2 |
| `IC=0.866 + hit_rate=0.497 + DSR=0.767` = costed_out_edge canonical signature (NOT leakage; NOT noise) | Mira sign-off-round2 §3.4 + §5.1 + §5.2 evidence matrix (4-cell rejection of leakage / noise / fully-realized hypotheses) |
| Phase G hold-out unlock authorized as OOS confirmation step (NOT salvage path) | Mira sign-off-round2 §1 disposition + §8.3 path (a)/(b)/(c) options |
| Anti-Article-IV Guard #8 (NEW §15.5) verdict-layer `*_status` provenance protocol | F2-T0b' §1 row C-A3 + Mira spec v1.1.0 §15.5 lines 749-761 |
| Engine config v1.1.0 + spec yaml v0.2.3 + rollover calendar + cost atlas + cpcv config 8/9 IDENTICAL N7 vs N7-prime | Beckett N7-prime §3.3 cross-check table + Mira sign-off-round2 §10 trace |
| Aria personal preference for minimum-disruption + maximum-information per-effort | Disclosed verbatim §5; consistent with Aria authorship history (T002.1.bis APPROVE_OPTION_B + T002.6 T0b APPROVE_WITH_CONDITIONS + F2-T0b APPROVE_OPTION_D) |
| ESC-011 5/5 UNANIMOUS APPROVE_OPTION_C ratification preserved | `docs/councils/COUNCIL-2026-04-29-ESC-011-resolution.md` §1; Mira sign-off-round2 §11 council fidelity |
| Pax forward-research authority (ESC-011 R10) for bandwidth allocation between paths | Mira sign-off-round2 §1 disposition + §8.3 |

**Article IV self-audit verdict:** every architectural claim in this vote traces to (a) Mira F2-T5 round 2 sign-off §-anchor, (b) Mira Gate 4b spec v1.1.0 §-anchor, (c) Beckett N7-prime report §-anchor, (d) Aria T0b round 1 archi review §-anchor, OR (e) F2-T0b/F2-T0b' archi review §-anchor. **NO INVENTION. NO threshold mutation. NO Mira spec body mutation. NO factory contract refactor. NO engine signature change. NO closure isolation break. NO hold-out lock touch in this vote.** Conditions C-G1..C-G6 (Path B win) and C-R1..C-R3 (Path C win) are engineering-placement / governance-format mandates strictly downstream of the spec — they refine implementation locus + audit trail + ledger format, NOT spec semantics.

The vote does NOT pre-empt:
- Pax @po forward-research authority (bandwidth allocation between paths B and C; story creation; epic deprecation if Path C).
- Mira @ml-researcher spec authority (Phase G IC measurement protocol; n_trials carry-forward; ic_holdout_status promotion to 'computed').
- Riven @risk-manager ledger authority (Gate 4b OOS verdict reclassification; §9 HOLD #2 disarm-ledger entry format).
- Beckett @backtester baseline-run authority (Phase G N8 execution; reproducibility receipt cross-check).
- Quinn @qa quality-gate authority (Phase G test surface; F2-T5-OBS-1 fix verification).
- Dex @dev implementation authority (engineering details of Phase G hold-out unlock dispatch + verdict-layer fix).
- Gage @devops Article II push-exclusivity (no commit / push by this vote per task discipline).

---

## §8 Aria cosign 2026-04-30 BRT — ESC-012 strategy-fate ballot

```
Authority: Aria (@architect) — system architecture + factory pattern + closure isolation + spec yaml threshold guardianship
Council: ESC-012 — T002 strategy-fate (post-Mira F2-T5 GATE_4_FAIL_strategy_edge / costed_out_edge)
Vote: APPROVE_PATH_B (Phase G hold-out unlock OOS confirmation)
Vote secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback ONLY if Path B blocked by independent governance
Vote rejected: REJECT_PATH_A_PRIME (Strategy refinement)
Mode: autonomous; voter did NOT consult other agents' votes pre-cast (task discipline)

Architectural rationale (3 lenses):
  Lens 1 — Spec yaml v0.2.3 threshold UNMOVABILITY (Anti-Article-IV Guard #4):
           Path B + Path C: ZERO mutation risk; thresholds preserved verbatim.
           Path A': HIGH mutation risk via n_trials Bonferroni expansion (refinement axes consume new trial slots).
  Lens 2 — Factory pattern preservation (T002.1.bis APPROVE_OPTION_B):
           Path B: ZERO closure body touch; reuse cpcv_aggregator window-agnostic per Aria F2-T0b' Option D design.
           Path A': closure body changes per axis (factory pattern survives but per-axis test surface rebuild).
           Path C: closure body preserved as forensic record.
  Lens 3 — Hold-out lock contract (Anti-Article-IV Guard #3 UNMOVABLE):
           Path B: canonical use of locked window — terminal disambiguation step.
           Path A': hold-out preserved during refinement (correct discipline) but terminal step deferred.
           Path C: hold-out preserved unconsumed (research bandwidth bequest for future strategies).

Implementation cost (per §2 detailed table):
  Path B: ~75-105 net new LoC; ~6-8 sessions; ~1-2 calendar days; ZERO factory refactor; LOW risk.
  Path A': ~1200-2800 net new LoC across 4 axes; ~24-32 sessions; ~5-10 calendar days; HIGH n_trials risk.
  Path C: 0 net new LoC; ~3 sessions; ~0.5-1 calendar day; ZERO risk.

Reusability (per §3 inventory):
  All paths preserve impl artifact inventory (cpcv_aggregator + info_coef + latency_dma2 + RLP/rollover/auction/microstructure flags + factory pattern + closure isolation contract + per-fold P126 D-1 invariant + mutually-exclusive engine guard + determinism stamp + Anti-Article-IV Guard #8).
  Path B MAXIMALLY REUSES (terminal disambiguation).
  Path A' partially reuses per axis (multiplicative cost).
  Path C MAXIMALLY PRESERVES as institutional bequest for next strategy.

Spec yaml v0.2.3 mutation risk (Anti-Article-IV Guard #4):
  Path B: NONE — same thresholds apply to OOS evaluation per Mira spec §15.10; Mira G-spec amendment is APPEND-ONLY.
  Path A': MEDIUM-HIGH — n_trials expansion likely; each refinement = potential governance event.
  Path C: NONE — spec yaml frozen as forensic record.

Conditions bound IF Path B wins (C-G1..C-G6):
  C-G1 (HIGH) — Phase G unlock gated by explicit phase=G + determinism stamp holdout_unlocked flag
  C-G2 (HIGH) — F2-T5-OBS-1 verdict-layer fix PRE-G-RUN (decay-clause short-circuit on ic_holdout_status='deferred')
  C-G3 (HIGH) — Mira G-spec amendment surface (predictor/label / ic_holdout_status='computed' / decay activation / n_trials carry-forward)
  C-G4 (HIGH) — Aria archi review of Mira G-spec amendment (factory + closure + invariants + engine guard + determinism stamp)
  C-G5 (HIGH) — Beckett N8 reproducibility cross-check 8/9 fields IDENTICAL to N7-prime
  C-G6 (MED) — Riven §9 HOLD #2 ledger entry per Aria F2-T0b §6.1 atomic AND-conjunction format

Conditions bound IF Path C wins (C-R1..C-R3):
  C-R1 (MED) — Aria architectural reusability inventory document
  C-R2 (MED) — Mira post-mortem research-log update with costed_out_edge anti-pattern + falsification-depth notation
  C-R3 (MED) — Hold-out window preserved unconsumed; Riven §9 HOLD #2 entry = T002 retired with costed_out_edge partial falsification record

Conditions bound IF council overrides to Path A' (C-R'1..C-R'4 surfaced for completeness despite Aria reject):
  C-R'1 (CRITICAL) — NO n_trials expansion without ESC-013 council ratification
  C-R'2 (HIGH) — Each refinement = full audit chain (no shortcut paths)
  C-R'3 (HIGH) — Phase G hold-out unlock STILL REQUIRED at terminal step
  C-R'4 (HIGH) — Article IV preservation per axis (closure isolation + P126 D-1 + engine guard + determinism stamp)

Personal preference disclosure: APPROVE_PATH_B; bias toward minimum-disruption + maximum-information per-effort; bias check passed (would still vote B given the cheap-by-design Phase G unlock; would lean C if OOS unlock cost were higher).

Article II (Gage push exclusivity): preserved — vote document is write-only, no commit/push initiated by Aria.
Article IV (No Invention): preserved — every clause traces in §7; conditions bound to source anchors; no spec mutation; no threshold mutation; no factory contract refactor; no engine signature change; no closure isolation break; no hold-out lock touch in this vote.
Anti-Article-IV Guards (preserved unchanged):
  #1 (Dex impl gated em Mira spec PASS) — preserved through G chain (Mira G-T0a → Aria G-T0b → Dex G-T1)
  #3 (NO touch hold-out lock) — preserved through Path B canonical use (single explicit phase=G unlock with audit trail)
  #4 (Gate 4 thresholds UNMOVABLE) — preserved verbatim across all paths; Path A' would risk this; Path B + Path C do not
  #5 (NO subsample backtest run) — preserved (Phase G runs full hold-out window; not subsample)
  #6 (NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH) — preserved (Path B → Gate 5 still requires paper-mode T002.7; Path C → Gate 5 LOCKED forever for T002)
  #7 (NO push) — preserved (Aria authoring; no git operations)
  #8 (Verdict-layer *_status provenance + InvalidVerdictReport) — preserved through F2-T5-OBS-1 fix (C-G2) which strengthens enforcement at decay-clause level
Boundary respected:
  NÃO override Mira ML semantics (Phase G IC measurement / n_trials carry-forward / ic_holdout_status promotion all delegated to Mira G-spec amendment under condition C-G3)
  NÃO mute Mira F2-T5 round 2 verdict (vote consumes verdict + nuance verbatim; does NOT challenge `costed_out_edge` sub-classification)
  NÃO pre-empt Pax forward-research authority (vote surfaces architectural recommendation; bandwidth allocation between B/C is Pax decision per ESC-011 R10)
  NÃO pre-empt Riven ledger authority (conditions C-G6 + C-R3 bind format mandate per Aria T0b §6.1; authoring is Riven)
  NÃO pre-empt Beckett baseline-run authority (Path B requires Beckett N8; conditions bind reproducibility cross-check format only)
  NÃO commit / NÃO push (Gage @devops authority preserved for any future commit)
Cosign: Aria @architect 2026-04-30 BRT — ESC-012 T002 strategy-fate ballot
        Vote: APPROVE_PATH_B (Phase G hold-out unlock OOS confirmation)
        Secondary: APPROVE_PATH_C (Retire T002) acceptable as Pax fallback
        Rejected: REJECT_PATH_A_PRIME (Strategy refinement)
```

— Aria, escolhendo a confirmação OOS canônica sobre refinamento iterativo ou aposentadoria prematura.
