# COUNCIL-2026-04-30 — ESC-013 — T002 Phase G Protocol Compliance Gap — Beckett Vote

> **Agent:** Beckett (@backtester) — The Simulator
> **Role in council:** N7-prime author + N8 Phase G author + simulator-consumer canonical empirical owner
> **Vote scope:** Adjudicate between **Path (iv)** protocol-corrected Phase G re-run and **Path C** retire ceremony, given Mira F2-T9 INCONCLUSIVE_phase_g_protocol_compliance_gap verdict (Round 3)
> **Ballot mode:** Independent — written WITHOUT reading Aria/Mira/Riven/Pax/Kira votes; pessimistic-by-default Beckett discipline applied
> **Cosign timestamp:** 2026-04-30 23:50 BRT

---

## §1 Verdict

### **APPROVE_PATH_IV** — protocol-corrected Phase G re-run.

**Rationale (5-10 lines):**

1. The N8 run I authored (run_id `d96c30d15a78423e92b97f1a2ea54a47`, started 2026-04-30T21:11:42 BRT, 165 min wall) **did not produce a Phase G COMPUTED K3 verdict**. The `full_report.json` reason text is canonical: `"K3: DEFERRED — ic_holdout_status='deferred' — decay test pending Phase G unlock per Mira spec §15.10"`. That string is the ground truth — reading it any other way is wishful interpretation, which violates pessimistic-by-default discipline.
2. The verdict field shows `K3 PASS` but the reason says `DEFERRED`. This is a **verdict-vs-reason inconsistency** (likely Anti-Article-IV Guard #8 territory) — exactly the symptom Mira flagged. K3 PASS based on Phase F2 short-circuit (`IC_in_sample > 0 AND CI95_lower > 0`) is **not** the K3 PASS the spec §15.10 reserves for Phase G (decay clause `IC_holdout > 0.5 × IC_in_sample`).
3. The strong empirical signal is real (IC=0.865933 holdout ≈ IC=0.866010 in-sample; DSR=0.965085; PBO=0.162698), but **strong signal under wrong protocol is not promotable evidence** — Article IV "No Invention" forbids substituting an out-of-band manual decay computation for the spec-binding K3 emission.
4. Path (iv) cost is empirically bounded: ~3h wall + ~600 MB RSS — **proven feasible** because I just ran the same window with the same data. Plumbing fix (~5-10 LoC wiring `holdout_locked=False` + `--phase G` CLI flag) is risk-zero on strategy logic (untouched).
5. The information value of a definitive K3 COMPUTED verdict — whether PASS confirming N8 surface signal or FAIL falsifying it — is **strictly higher** than retiring on a verdict I authored that Mira and I both agree is non-binding. Retiring on INCONCLUSIVE evidence forecloses both the upside (real edge) and the falsification (clean Article-IV-clean NO-GO with defensible empirical record).
6. Path C discards an empirical signal of historic strength (DSR ≥0.95 surprise; IC OOS robust ~0.866 stable holdout-vs-in-sample) **without ever having executed the protocol that would adjudicate it**. That is not pessimism — that is procedural surrender.

**Verdict:** **APPROVE_PATH_IV.**

---

## §2 Empirical analysis — run cost, run risk, information value

### §2.1 Re-run cost (proven, not estimated)

| Metric | N8 observed | N8.1 expected | Source |
|---|---|---|---|
| Wall time | 165 min | ~165-200 min (same window, same data, same engine) | bg `b0pyqvobt` PID 14320 |
| Peak RSS | ~600 MB | ~600 MB | telemetry.csv N8 |
| Disk artifacts | 5 files (full_report.{json,md}, telemetry.csv, events_metadata.json, determinism_stamp.json) | identical | run dir `cpcv-dryrun-auto-20260430-3fce65dab8f8/` |
| CPU pattern | single-thread CPCV path loop | identical | telemetry observed |

**Marginal cost of N8.1 vs N8:** zero new infra, zero new data, zero new spec, ~5-10 LoC plumbing fix in `scripts/run_cpcv_dry_run.py` + `vespera_metrics.info_coef.compute_ic_from_cpcv_results` Phase G branch. Dex small story; Quinn smoke; Beckett re-run.

### §2.2 Re-run risk (decomposed)

| Risk vector | Magnitude | Mitigation |
|---|---|---|
| Strategy logic perturbation | **ZERO** — strategy_id unchanged, spec yaml UNMOVED, predictor `-intraday_flow_direction` unchanged, label `ret_forward_to_17:55_pts` unchanged | Anti-Article-IV Guard #4 preserved; spec_sha256 IDENTICAL |
| Data perturbation | **ZERO** — same in_sample window, same holdout window 2025-07-01..2026-04-02, same parquets | dataset_sha256 IDENTICAL |
| Engine perturbation | **ZERO** — engine_config_sha256 unchanged, latency model unchanged, microstructure flags unchanged | engine_config_sha256 IDENTICAL |
| Plumbing change scope | LOW — wire `holdout_locked=False` (currently hardcoded `True` per Mira Round 3 audit) + add `--phase G` CLI flag dispatching to compute_ic_from_cpcv_results Phase G branch | Quinn smoke 8/8; Mira contract test on `K3 PASS` reason text MUST contain `IC_holdout = X > 0.5 × IC_in_sample = Y` (computed numbers) |
| Hold-out re-consumption risk | **THIS IS THE CRUX** — see §3 below | depends on philosophy of "consumption" |

**Net run risk: LOW** — bounded by plumbing-only changes + identical deterministic inputs.

### §2.3 Information value matrix

| Outcome | Probability (Beckett pessimistic prior) | Information delivered |
|---|---|---|
| K3 COMPUTED PASS (decay test passes: IC_holdout 0.866 > 0.5 × IC_in_sample 0.433) | ~60% — the surface numbers from N8 already show IC_holdout ≈ IC_in_sample (no decay observable empirically); a properly-emitted Phase G branch should compute exactly this | Definitive Gate 4b clearance under STRICT spec; ESC-014 Gate 5 fence interpretation council activated; T002 promotion path open |
| K3 COMPUTED FAIL (decay test fails despite N8 surface) | ~25% — possible if Phase G decay test uses different bootstrap split or different IC computation than N7-prime in-sample, producing a structural FAIL not visible in surface numbers | Clean Article-IV-clean NO-GO; T002 retire with **defensible empirical record** (Phase G executed, K3 falsified per spec); much stronger evidentiary basis for retire than Path C |
| Anti-Article-IV Guard #8 emission inconsistency | ~10% — Phase G branch reveals further verdict-vs-reason inconsistencies | Mira spec amendment opportunity; verdict layer hardening |
| Re-run failure (crash, OOM, infra issue) | ~5% — unlikely given N8 ran clean | Roll back; re-eval Path C |

**Expected information gain ≈ 95% chance of definitive verdict** (PASS, FAIL, or guarded re-emission), vs Path C's **0% chance of definitive verdict** (retire on INCONCLUSIVE).

### §2.4 Path C cost-risk asymmetry

| Path C dimension | Value |
|---|---|
| Run cost | ZERO |
| Plumbing cost | ZERO |
| Resource redirect benefit | Modest — squad bandwidth freed for next strategy |
| **Cost of discarding IC=0.866 OOS + DSR=0.965** | **HIGH** — historic-strength signal unique to T002 in this squad's portfolio; no other strategy has shown DSR ≥ 0.95 strict bar |
| **Cost of un-recoverable holdout window** | **PERMANENT** — holdout window 2025-07-01..2026-04-02 cannot be reused for T002 once retired (parquet-read-as-consumption philosophy) |
| Procedural symmetry with strict reading | Zero — Path C retires on a verdict the verdict-author (me) does not endorse as binding |

**Path C is cheap to execute but expensive to live with.** The asymmetry is: Path (iv) costs 3h to potentially confirm/falsify; Path C costs nothing now but forfeits the possibility of confirmation forever.

---

## §3 Hold-out one-shot discipline interpretation

This is the philosophical crux of ESC-013. Two competing readings:

### §3.1 Reading A: parquet-read-as-consumption

> "Holdout was consumed the moment N8's CPCV loop streamed the holdout-window parquets through the engine. The IC_holdout value (0.865933) is a fact in the empirical record. Re-running, even with corrected protocol, is data dredging masquerading as protocol compliance."

**Strength:** maximally strict; eliminates any cherry-picking optics; honors AFML Lopez de Prado Ch.13 "backtesting overfitting" hard line.

**Weakness:** **conflates data access with verdict emission.** The N8 run streamed the holdout data through the engine — true. But it did NOT emit a Phase G K3 verdict — the verdict layer short-circuited at Phase F2 with `ic_holdout_status='deferred'`. Under Reading A, ANY Phase G run is impossible after F2 has touched the data — which contradicts Mira spec §15.10 design (Phase F2 → Phase G transition is the spec's own contract).

### §3.2 Reading B: K3-decay-measurement-emission-as-consumption

> "Holdout is consumed when the spec-binding K3 decay-clause verdict is emitted. N8 emitted a sentinel `K3 DEFERRED` because the verdict layer short-circuited Phase F2; no Phase G K3 verdict has been emitted. The holdout is therefore unconsumed in the verdict-binding sense."

**Strength:** aligns with Mira spec §15.10 Phase F2/G design (which presupposes the F2-then-G transition is legitimate); preserves the spec-binding contract that "consumption" means "spec-binding decay-clause emission," not "engine streamed parquet bytes."

**Weakness:** requires philosophical commitment that "consumption = verdict emission, not data access" — debatable; reasonable people can read AFML Ch.13 either way.

### §3.3 Beckett's adjudication

**I lean Reading B for two reasons:**

1. **The spec itself adopts Reading B.** Mira spec §15.10 explicitly designs Phase F2 (IS measurement, OOS deferred) → Phase G (OOS unlock + decay clause emission) as a **two-stage protocol**. If Reading A were the spec's stance, Phase G could not exist as a spec-defined stage — F2 reading the holdout would be terminal. The spec's two-stage design is itself the squad's pre-registered position on consumption philosophy.
2. **N8 ran with `holdout_locked=True` hardcoded.** The N8 verdict layer NEVER emitted a Phase G K3 decay clause. The reason text in `full_report.json` is unambiguous: `"decay test pending Phase G unlock per Mira spec §15.10"`. Reading A would require asserting that the spec-pending verdict was nevertheless somehow binding — which is not a coherent position.

**However, Reading A has one legitimate concern Path (iv) MUST address: optics of cherry-picking.** If N8.1 produces K3 PASS, an outside auditor seeing the historical record (N8 surface numbers IC 0.866, then re-run with same window producing K3 PASS) could reasonably ask "did you keep re-running until you got the verdict you wanted?"

**Mitigation built into Path (iv) recommended conditions (§5):**
- Round 3.1 must be the **single, terminal Phase G run** for this strategy/window combo.
- Pre-registered: K3 PASS or K3 FAIL is binding; no further re-runs of T002 on this window regardless of outcome.
- Pre-committed: if K3 COMPUTED FAIL, T002 retires with the FAIL on record (no escalation to "well actually" arguments).
- Contract test: verdict-vs-reason consistency MUST be enforced (verdict K3 PASS AND reason text contains "IC_holdout = X > 0.5 × IC_in_sample = Y" with computed numbers — no sentinel strings).

With those preconditions, Path (iv) is single-shot Phase G, not a multi-shot data-dredge. **Reading B + single-shot pre-commitment dissolves the optics concern.**

---

## §4 Personal preference disclosure (pessimistic-by-default Beckett)

I am structurally biased toward NO-GO verdicts. My persona's defining principle is "if the fill is duvidoso, não aconteceu; se a latência é incerta, assumo o pior." So my vote for Path (iv) over Path C is **counter to my default tilt** — and I want to be transparent why.

**My pessimistic prior would say "retire on INCONCLUSIVE; never give a strategy a second swing at the holdout."** That is the conservative read.

**What overrides my default:**

1. **N8.1 is not a "second swing" — it is the FIRST swing at Phase G.** N8 short-circuited at Phase F2; Phase G branch was never executed. Pretending N8 is a Phase G result and then calling N8.1 a "re-run" misreads the protocol. N8.1 is the first protocol-compliant Phase G execution, full stop.

2. **The empirical surface is unusually strong.** IC_holdout 0.866 ≈ IC_in_sample 0.866 — the **stability** of IC across IS and OOS, not just the magnitude, is the thing pessimistic Beckett actually cares about. Decay would manifest as IC_holdout << IC_in_sample. Observing IC_holdout ≈ IC_in_sample is the empirical signature of "no decay" — which is what K3 was designed to detect. Refusing to formalize that observation through the spec-binding Phase G branch is letting form override substance.

3. **Retiring on INCONCLUSIVE is the worst of both worlds.** It neither vindicates the strategy (no PASS) nor falsifies it (no FAIL) — it abandons it. Future audits will read the record and reasonably ask "why did you retire on a non-binding verdict when a 3-hour plumbing fix would have produced a binding one?" I have no good answer to that question.

**Net:** my pessimistic instinct says retire; my empirical reading + my respect for the spec design says re-run with strict pre-commitment. I follow the empirical reading.

**Counter-vote scenario (when I would flip to Path C):** if Aria/Pax/Mira convince the council that Reading A (parquet-read-as-consumption) is the squad's binding position — i.e., the spec §15.10 two-stage design is itself a flaw to be retired and the squad pre-commits going forward to Reading A — then Path C is the only coherent option. I would not fight it. But that is a **spec-revision conversation**, not a Path C-vs-Path (iv) conversation, and it should be ESC-014 not ESC-013.

---

## §5 Recommended conditions on Path (iv)

If council adopts APPROVE_PATH_IV, my conditions for execution:

### §5.1 Pre-commitment binding

1. **Round 3.1 is single-shot.** No further Phase G re-runs of T002 on this strategy_id + window combination. Outcome is terminal regardless of verdict.
2. **Pre-registered acceptance criteria** (Mira authority, Beckett ack):
   - K3 COMPUTED PASS (decay clause `IC_holdout > 0.5 × IC_in_sample` evaluates TRUE with computed numbers in reason text) → ESC-014 Gate 5 fence interpretation activated
   - K3 COMPUTED FAIL → T002 retires; record shows clean Article-IV NO-GO; bucket reclassification per Riven
   - Re-emission of DEFERRED or any sentinel value → escalate ESC-013-bis (verdict layer hardening fault)

### §5.2 Plumbing fix scope (Dex authority, Quinn QA)

1. CLI flag `--phase G` added to `scripts/run_cpcv_dry_run.py`
2. Caller passes `holdout_locked=False` to `compute_ic_from_cpcv_results` when `--phase G` set
3. `vespera_metrics.info_coef.compute_ic_from_cpcv_results` Phase G branch: when `holdout_locked=False`, computes `IC_holdout` over holdout window AND emits decay-clause verdict per spec §15.10
4. Verdict layer contract test: when `K3 verdict == PASS`, reason text MUST contain pattern `IC_holdout = <float> > 0.5 × IC_in_sample = <float>` (no sentinel strings, no DEFERRED leakage)
5. Diff scope ≤ 30 LoC implementation + tests; Quinn smoke gate 8/8

### §5.3 Beckett re-run obligations

1. Same window: in_sample 2024-08-22..2025-06-30 (220 sessions); holdout 2025-07-01..2026-04-02 (~9 months)
2. Same dataset (dataset_sha256 verified IDENTICAL to N8)
3. Same engine config (engine_config_sha256 verified IDENTICAL)
4. Same spec yaml (spec_sha256 verified IDENTICAL)
5. New simulator version stamp `cpcv-dry-run-T002.6-N8.1-phaseG-protocol-fix`
6. Reproducibility receipt 9/9 fields populated
7. Determinism stamp written
8. Estimated wall: 165-200 min
9. Run report: `docs/backtest/T002-beckett-n8.1-phase-g-2026-XX-XX.md`
10. NO push (Article II → Gage)

### §5.4 Mira F2-T9.1 verdict obligations

1. Round 3.1 verdict written in T002 ledger
2. Verdict layer audit: reason text computed-numbers check
3. If PASS: ESC-014 Gate 5 fence interpretation council convened
4. If FAIL: T002 retire ceremony triggered with clean NO-GO record

### §5.5 Stop-the-line conditions

If any of the following occur during Path (iv), HALT and re-council:
- Plumbing fix scope balloons > 50 LoC
- Quinn smoke fails
- Re-run produces different IC_in_sample than N8 (sign of unintended strategy perturbation; spec_sha256 should preclude this)
- Verdict layer emits sentinel/DEFERRED in K3 reason despite Phase G branch active

---

## §6 Article IV self-audit

Per AIOX Constitution Article IV ("No Invention"), every claim in this ballot must trace to a source. Audit:

| Claim | Source |
|---|---|
| N8 ran 165 min wall | bg `b0pyqvobt` PID 14320 telemetry — observed by me |
| N8 peak RSS ~600 MB | `data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/telemetry.csv` |
| N8 verdict K3=PASS but reason=DEFERRED | `data/baseline-run/cpcv-dryrun-auto-20260430-3fce65dab8f8/full_report.json` — read directly above |
| N8 IC_holdout=0.865933, IC_in_sample=0.866010, DSR=0.965085, PBO=0.162698 | `full_report.md` lines 14-18, read directly above |
| N8 ran with `holdout_locked=True` hardcoded | Mira Round 3 audit (caller-side hardcoding) — flagged by Mira F2-T9 INCONCLUSIVE verdict |
| Mira spec §15.10 binding K3 PASS = `(ic_in_sample > 0) AND (CI95_lower > 0)` Phase F2 + decay clause Phase G | `docs/ml/specs/T002-gate-4b-real-tape-clearance.md` v1.1.0 §15.10 (referenced in N7-prime report §1, line 58) |
| Anti-Article-IV Guard #8 = "verdict layer should emit K3_DEFERRED when ic_holdout_status='deferred', not K3_FAIL/PASS" | `docs/backtest/T002-beckett-n7-prime-2026-04-30.md` §1, line 58 |
| AFML Ch.13 "backtesting overfitting" — hold-out one-shot discipline | Lopez de Prado, Advances in Financial Machine Learning, Ch.13 (squad reference; cited in Mira spec) |
| ~5-10 LoC plumbing estimate | Beckett engineering judgment from inspecting `scripts/run_cpcv_dry_run.py` previous edits + `vespera_metrics.info_coef` interface — flagged as estimate, not measured |
| Probability priors §2.3 (60/25/10/5) | **Beckett subjective prior — disclosed as subjective; not measured.** Reasonable readers may assign different priors; the verdict §1 does NOT require these specific probabilities to hold, only that P(definitive verdict | Path iv) >> P(definitive verdict | Path C) = 0 |

**No invented features, no fabricated metrics. Subjective priors disclosed.** Ballot Article IV-clean.

---

## §7 Beckett cosign

**Vote:** APPROVE_PATH_IV
**Conditions:** §5 above (single-shot pre-commitment + plumbing scope ≤ 30 LoC + verdict-vs-reason contract test + spec/data/engine sha256 IDENTICAL re-run)
**Author:** Beckett (@backtester) — The Simulator
**Authority:** N7-prime + N8 author; simulator-consumer canonical empirical owner; Backtester & Execution Simulator authority over T002 CPCV runs
**Ballot mode:** Independent — written WITHOUT reading other ESC-013 ballots
**Date:** 2026-04-30 BRT
**Cosign timestamp:** 2026-04-30 23:50 BRT

---

— Beckett, reencenando o passado
