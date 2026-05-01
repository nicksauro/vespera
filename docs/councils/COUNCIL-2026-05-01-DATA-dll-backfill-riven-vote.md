---
council_id: DATA-2026-05-01-DLL-BACKFILL
topic: Pre-2024 DLL backfill scope decision (Path A backfill / Path B forward-only / Path C hybrid / DEFER pending Nelo)
voter: Riven (@risk-manager)
voter_role: Risk Manager & Capital Gatekeeper — hold-out integrity custodial monopoly + §11.5 capital-ramp pre-conditions custodial monopoly + Quarter-Kelly REGRA ABSOLUTA + Gate 5 dual-sign disarm authority + 3-bucket post-mortem authoring authority
date_brt: 2026-05-01
voter_authority: |
  ESC-011 R7 + R20 carry-forward + ESC-012 R9 (one-shot hold-out consumption binding) +
  ESC-013 R19 (single-shot K3 decay metric layer) + Quant Council 2026-05-01 R7 (forward-time virgin OOS)
  + Quant Council 2026-05-01 R8 (pre-2024 archival fallback conditional on regime stationarity)
  + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp pre-conditions §1..§10 custodial monopoly
  + Riven persona REGRA ABSOLUTA (quarter-Kelly cap 0.25 × f* + sizing-deferred + paper-mode pre-condition + haircut 30-50% first 3 months live)
mandate: |
  RISK PERIMETER adjudication of pre-2024 DLL backfill scope. Custodial focus: hold-out integrity preservation
  (T002 hold-out CONSUMED; H_next-1 PRIMARY hold-out 2026-05-01..2026-10-31 must remain virgin; pre-2024
  archival virginity is a conditional-grade asset). Vote independent — no peer ballots consulted pre-vote.
inputs_consulted:
  - docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md (T002 hold-out CONSUMED one-shot binding R9)
  - docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md (single-shot K3 decay metric layer R19)
  - docs/councils/COUNCIL-2026-05-01-QUANT-resolution.md (H_next-1 PRIMARY hold-out 2026-05-01..2026-10-31 forward-time virgin per R7; pre-2024 archival fallback conditional R8)
  - docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-riven-vote.md (own QUANT ballot — §11.5 #1-#10 cumulative pre-conditions; OOS budget topology preference)
  - docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md (3-bucket framework + §5 anti-pattern catalog §5.1-§5.16)
  - C:\Users\Pichau\.claude\projects\C--Windows-system32\memory\feedback_profitdll_quirks.md (Nelo authority; 19ms bug pre-2024 untested; DLL retention exhaustion possible; threading bugs)
inputs_NOT_consulted_pre_vote: peer voter ballots (Mira / Pax / Nelo / Aria / Sable / Beckett / Tiago)
verdict_summary: |
  §1: Custodial perspective — T002 hold-out (2025-07..2026-04-21) CONSUMED one-shot binding (ESC-012 R9 + ESC-013 R19);
  H_next-1 PRIMARY hold-out (2026-05-01..2026-10-31) MUST remain virgin per Quant Council R7; pre-2024 archival
  (2023-Q1..2024-Q3) virginity-question NEUTRAL (never observed by current squad pre-2026-04 BUT closed-source DLL
  behavior pre-2024 unverified; engineering risk material).
  §2: Risk flags HEAVY — pre-2024 19ms bug Nelo-authoritative; DLL retention exhaustion possible; threading bugs
  WINFUNCTYPE/c_wchar_p recurring; closed-source Win64 reproducibility threat; cost atlas v1.0.0 calibrated to
  2024+ may not hold for pre-2024 (RLP rules / fees structure / liquidity microstructure DRIFT).
  §3: §11.5 capital-ramp pre-conditions PRESERVED #1-#10 verbatim; NEW #11 candidate proposed: "OOS test must use
  either forward-time virgin OR cross-validated regime-equivalent archival (Mira authority on regime equivalence;
  Sable audit on virginity status; Riven authority on §11.5 incorporation)".
  §4: Bayesian prior on Path A success — joint P(meaningful pre-2024 OOS test viable) ≈ 0.30 (Nelo retention 0.50 ×
  Mira regime equivalence 0.60); Path B forward-only ≈ 0.95 reliability over 6mo wall-clock; Path C hybrid ≈ 0.80
  reliability with parallel optionality.
  §5: Squad bandwidth opportunity cost — Path A 5-10 sessions backfill engineering + ~3h N1 archival run, downside
  wasted if regime non-equivalent; Path B 6mo wall-clock, squad pivots to Beckett v1.2.0 / paper mode infra / T001
  closure; Path C parallel 5-10 sessions backfill running while forward data accumulates (best information per session).
  §6: Vote — APPROVE_PATH_C (hybrid). Conditions: (a) Mira regime stationarity check FIRST before any pre-2024
  ingestion authorized; (b) Sable audit virgin status of pre-2024 archival before consumption; (c) cost atlas v0.x.x
  variant for pre-2024 IF current v1.0.0 invalid; (d) Quarter-Kelly REGRA ABSOLUTA preserved (no sizing change from
  any pre-2024 evidence alone — must couple with H_next-1 PRIMARY); (e) Gate 5 fence preserved (LOCKED PERMANENTLY
  for T002; H_next requires fresh dependency tree); (f) pre-2024 evidence is SECONDARY-CORROBORATIVE, never
  primary OOS substitute for H_next-1.
  §7: Personal preference disclosure — Riven prefers Path C as hedge; Path A solo is too speculative under joint
  prior 0.30; Path B solo wastes 5-10 backfill sessions of squad bandwidth that could run parallel.
  §8: Article IV self-audit verbatim.
  §9: Riven cosign 2026-05-01 BRT — Data Council custodial ballot.
oos_budget_status_post_vote: |
  T002 hold-out [2025-07-01, 2026-04-21] CONSUMED under H_T002 (binding per ESC-012 R9 + ESC-013 R19).
  H_next-1 PRIMARY hold-out [2026-05-01, 2026-10-31] forward-time virgin (Quant Council R7); pre-registered;
  hash-frozen; per-line manifest provenance lock identical to T002 mechanics; UNTOUCHED.
  Pre-2024 archival [2023-Q1, 2024-Q3] virginity status PENDING Sable audit; conditional-grade asset under R8;
  consumption authorized ONLY under §11.5 NEW #11 candidate (regime-equivalent cross-validation).
quarter_kelly_status_post_vote: PRESERVED INTACT (no sizing exercise authorized from pre-2024 archival evidence alone; quarter-Kelly cap 0.25 × f* inviolate; haircut 30-50% first 3 months live preserved).
gate_5_status_post_vote: LOCKED PERMANENTLY for T002; fresh dependency tree required for H_next-1 (no inheritance from pre-2024 corroborative evidence).
---

# DATA 2026-05-01 — Pre-2024 DLL Backfill Riven Vote (Custodial Risk Perimeter)

> **Voter:** Riven (@risk-manager) — Risk Manager & Capital Gatekeeper.
> **Authority basis:** ESC-011 R7 + R20 + ESC-012 R9 (one-shot hold-out consumption binding) + ESC-013 R19 (single-shot K3 decay metric layer) + Quant Council 2026-05-01 R7+R8 (H_next-1 forward-time PRIMARY + pre-2024 archival conditional fallback) + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp pre-conditions §1..§10 custodial monopoly + Riven persona REGRA ABSOLUTA.
> **Mandate:** Adjudicate pre-2024 DLL backfill scope decision from RISK PERIMETER perspective only. Pax retains scope authority; Mira retains regime-equivalence statistical authority; Nelo retains DLL behavior authority; Aria retains architectural-cost authority; Beckett retains harness authority; Sable retains virginity-audit authority. Riven's vote concerns ONLY (a) hold-out integrity preservation; (b) §11.5 cumulative pre-condition impact; (c) Quarter-Kelly substrate parametrizability; (d) Bayesian prior on Path success; (e) opportunity-cost framing of squad bandwidth; (f) custodial conditions on consumption authorization.

---

## §1 Custodial perspective — hold-out integrity preservation

### §1.1 T002 hold-out CONSUMED — binding one-shot

T002 hold-out window [2025-07-01, 2026-04-21] is **CONSUMED** under H_T002 per ESC-012 R9 (one-shot hold-out consumption discipline) + ESC-013 R19 (single-shot binding at K3 decay metric layer per Mira authoritative reading). Round 3.1 final FAIL `costed_out_edge_oos_confirmed_K3_passed` is binding regardless of K3-decay-vs-parquet-read interpretation. T002 cannot inherit, recycle, or repurpose this window. Custodial position: this consumption is FINAL, not negotiable, and protected by Anti-Article-IV Guard #4 (UNMOVABLE thresholds carry-forward) + Anti-Article-IV Guard #3 (hold-out lock virgin discipline; once consumed, contaminated permanently).

### §1.2 H_next-1 PRIMARY hold-out — forward-time virgin window

Per Quant Council 2026-05-01 R7, H_next-1 PRIMARY hold-out window is **[2026-05-01, 2026-10-31]** forward-time virgin tape. This window MUST remain inviolate through Phase G-equivalent OOS evaluation: hash-frozen pre-registered spec; per-line manifest provenance lock identical to T002 mechanics; `_holdout_lock.py` with `assert_holdout_safe` enforced at all call sites. UNTOUCHED status PRESERVED through DATA Council vote — pre-2024 backfill cannot contaminate forward-time hold-out by definition (temporal disjointness), but custodial discipline mandates that no pre-2024 evidence be promoted to PRIMARY OOS substitute. Pre-2024 is at most SECONDARY-CORROBORATIVE.

### §1.3 Pre-2024 archival virginity — conditional-grade

Pre-2024 archival window [2023-Q1, 2024-Q3] (Quant Council R8 fallback) virginity status is **NEUTRAL pending Sable audit**. Custodial position:

- **Researcher-observation contamination check:** Pre-2024 tape has NOT been seen by current squad for T002 sign-off (Beckett N6..N8.2 ran on 2024-08-22+ IS; Mira Round 1..3.1 verdict scrutiny on 2024-08-22+ IS; T002 hold-out was 2025-07+); pre-2024 was outside scope. Sable audit confirms or refutes this.
- **Closed-source DLL behavior pre-2024:** UNVERIFIED. Pre-2024 contracts may exhibit different DLL behavior (19ms bug Nelo-authoritative; retention exhaustion; threading bugs). This is engineering risk, not virginity threat per se, but it materially affects whether ANY pre-2024 evidence is reliable.
- **Microstructure stationarity 2023→2026:** UNVERIFIED. RLP rules, fees structure, liquidity profiles, COVID aftermath all introduce drift risk. Mira authority on regime equivalence determination.

Custodial verdict: pre-2024 archival is conditional-grade asset. Consumption requires (a) Sable virginity sign-off; (b) Mira regime-equivalence sign-off; (c) Nelo DLL-reliability sign-off; (d) Aria cost-atlas variant sign-off if v1.0.0 invalid pre-2024.

---

## §2 Risk flags for DLL backfill (engineering & data-integrity)

### §2.1 Catalog of risk flags surfaced

| Flag | Severity | Authority | Status |
|---|---|---|---|
| **WDO contracts pre-2024 = 0 trades 19ms bug** | HIGH | Nelo (ProfitDLL feedback memory) | KNOWN; pre-2024 untested; potentially blocks ingestion entirely |
| **DLL retention exhaustion possible pre-2024** | MEDIUM | Nelo authority | UNTESTED; may cap how far back retention reaches |
| **Threading bugs (WINFUNCTYPE / c_wchar_p)** | MEDIUM | Nelo + Aria | RECURRING; may affect backfill ingestion stability over long runs |
| **DLL bug 99% progress 35-45s** | LOW | Nelo + Tiago | KNOWN for 2024+; pre-2024 untested; mitigatable by chunked ingestion |
| **Closed-source Win64 reproducibility** | HIGH | Aria architecture | DLL is closed-source Windows-only; future DLL updates can change behavior; pre-2024 ingestion run TODAY may not reproduce TOMORROW |
| **Cost atlas v1.0.0 calibration drift pre-2024** | HIGH | Aria + Beckett | v1.0.0 calibrated to 2024+ tape; pre-2024 RLP/fees/microstructure may not match; need cost atlas v0.x.x variant |
| **Microstructure regime drift 2023→2026** | HIGH | Mira + Nova | COVID aftermath; rate cycle differences; structural breaks risk |
| **Tape integrity gaps pre-2024** | MEDIUM | Nelo + Beckett | Continuous front-month roll discipline pre-2024 unverified |

### §2.2 Risk-side composite reading

Pre-2024 backfill is an engineering project with multiple high-severity risk flags. Each is individually mitigatable but the JOINT probability of clean pre-2024 evidence is materially below face-value. The custodial position is that pre-2024 evidence, even if delivered, must be treated as SECONDARY-CORROBORATIVE rather than primary substitute for H_next-1 PRIMARY hold-out. This is consistent with Riven persona REGRA ABSOLUTA "em dúvida, reduzo" — when joint probability of clean evidence is uncertain, do not promote that evidence to load-bearing in the sign-off chain.

### §2.3 Determinism reproducibility threat

The single most concerning flag is **closed-source Win64 reproducibility**. ProfitDLL is a closed-source Windows-only library; its behavior on pre-2024 contracts is whatever the current DLL version implements TODAY. If Cedro / Nelos vendor updates the DLL in the future, pre-2024 ingestion runs may not reproduce. This is a structural reproducibility threat to any sign-off based primarily on pre-2024 evidence. The mitigation is to (a) pin DLL version + checksum at the time of pre-2024 ingestion; (b) record per-line provenance manifest including DLL version metadata; (c) treat pre-2024 evidence as SECONDARY corroboration only — never primary load-bearing OOS evidence. Sign-off chain integrity demands this discipline.

---

## §3 §11.5 capital-ramp pre-conditions impact

### §3.1 §11.5 #1-#10 PRESERVED for H_next-1

All ten existing pre-conditions from `docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-riven-vote.md` §2 carry-forward verbatim for H_next-1:

| # | Pre-condition (verbatim from QUANT ballot) | DATA Council impact |
|---|---|---|
| **#1** | Bucket A `engineering_wiring` HARNESS_PASS sign-off (Mira Gate 4a authority) | NEW: pre-2024 ingestion requires bucket-A clearance for DLL backfill harness; Quinn 8-point gate retained |
| **#2** | Bucket B `strategy_edge` GATE_4_PASS sign-off over real WDO tape | UNCHANGED; K1/K2/K3 strict bars UNMOVABLE |
| **#3** | Bucket C `paper_mode_audit` PAPER_AUDIT_PASS ≥ 5 sessions | UNCHANGED |
| **#4** | Mira independent Gate 5 cosign | UNCHANGED |
| **#5** | Riven independent Gate 5 cosign | UNCHANGED |
| **#6** | Toy benchmark E6 discriminator preservation | UNCHANGED |
| **#7** | Synthetic-vs-real-tape attribution audit | UNCHANGED |
| **#8** | Capture rate ≥ 0.6 of theoretical Sharpe | UNCHANGED |
| **#9** | DSR stationarity \|DSR_OOS - DSR_IS\| ≤ 0.10 | UNCHANGED |
| **#10** | PnL-IC alignment score ≥ 0.30 | UNCHANGED |

### §3.2 NEW §11.5 #11 candidate — OOS test source discipline

**Mandate (PROPOSED, subject to Mira spec amendment v1.4.0 approval):**

> OOS test must use either forward-time virgin window (gold standard) OR cross-validated regime-equivalent archival (conditional-grade fallback). Regime equivalence is determined by Mira independent authority via formal stationarity test (e.g., Kolmogorov-Smirnov on returns distribution + Levene on volatility + Augmented-Dickey-Fuller on mean reversion + microstructure feature-distribution comparison). Sable audit virginity status of any archival before consumption. Riven authority on §11.5 incorporation. Pre-2024 archival evidence is SECONDARY-CORROBORATIVE only — never primary OOS substitute when forward-time virgin window exists.

**Rationale:** ESC-012 R9 + ESC-013 R19 establish one-shot consumption discipline for T002. For H_next series, we need a structural rule that:
- Privileges forward-time virgin tape (PRIMARY) per Quant Council R7
- Permits archival fallback conditional on regime equivalence (per Quant Council R8)
- Prevents archival from silently being promoted to primary substitute when easier-to-procure than forward-time wait
- Codifies Mira regime-equivalence sign-off as gating step
- Codifies Sable virginity audit as gating step

This is TIGHTER not looser than the status quo. It explicitly recognizes archival as a secondary-grade asset and prevents the slippage anti-pattern where an enthusiastic squad converts archival corroboration into primary deployment-eligibility evidence under timeline pressure.

### §3.3 Net effect on H_next-1 pre-conditions

Carry-forward §11.5 #1-#10 verbatim PLUS NEW #11 candidate. Net effect: **TIGHTER on one new dimension; NO LOOSENING on any existing dimension**. K1/K2/K3 strict bars UNMOVABLE; quarter-Kelly cap 0.25 × f* inviolate; haircut 30-50% first 3 months live preserved.

---

## §4 Bayesian prior on DLL backfill success

### §4.1 Joint probability decomposition

Riven persona pessimistic-by-default custodial priors openly disclosed (NOT empirical measurements; reader can re-evaluate under different priors):

| Component | Probability | Rationale |
|---|---|---|
| **P(DLL retention works pre-2024 WDOFUT contínuo)** | ~0.50 | Nelo authority; UNTESTED; 19ms bug pre-2024 unknown; threading bugs recurring; reproducibility threat |
| **P(2023 regime materially equivalent to 2026 post-Mira-analysis)** | ~0.60 | Mira authority on stationarity; RLP+fees stable but COVID aftermath possible; rate cycle drift; structural breaks possible |
| **P(cost atlas v1.0.0 valid for pre-2024 OR cost atlas v0.x.x deliverable)** | ~0.70 | Aria + Beckett scope; engineering plausible; calibration effort manageable |
| **Joint P(meaningful pre-2024 OOS test viable)** | **~0.30 = 0.50 × 0.60 × ROUNDED** | Joint product with rounding-to-prior; if any leg fails, evidence is contaminated |

### §4.2 Path B forward-only baseline

| Component | Probability | Rationale |
|---|---|---|
| **P(forward 2026-05+ data accumulates ≥ 6mo on schedule)** | ~0.95 | Calendar-locked; live data ingestion path well-characterized; no dependency on pre-2024 DLL behavior |
| **P(forward window passes K1+K2+K3+#8+#9+#10 strict)** | NOT RELEVANT TO PATH SUCCESS | This is a statistical question independent of which path; both paths face this same bar |

Path B success ≈ 0.95 reliability over 6mo wall-clock for the OOS budget topology question (not the strategy success question, which is orthogonal).

### §4.3 Path C hybrid

| Component | Probability | Rationale |
|---|---|---|
| **P(forward 2026-05+ data accumulates while parallel backfill runs)** | ~0.95 | Forward path is unaffected by parallel backfill |
| **P(parallel backfill produces SECONDARY corroborative evidence)** | ~0.30 | Same as Path A joint |
| **Joint P(at least one of two paths delivers usable OOS evidence)** | ~0.97 | Forward path dominates; backfill is bonus |
| **Joint P(BOTH paths deliver, enabling cross-validation)** | ~0.29 | Bonus scenario; corroborates strongly if it happens |

Path C is dominant on joint probability ground. The risk is squad bandwidth (5-10 sessions backfill engineering) — see §5.

### §4.4 Probabilistic comparison

| Path | P(usable OOS evidence delivered) | P(robust corroborated evidence) | Squad bandwidth cost | Wall-clock to first verdict |
|---|---|---|---|---|
| **Path A solo** | ~0.30 | ~0.30 | 5-10 sessions backfill + 3h N1 | 3-5 weeks |
| **Path B solo** | ~0.95 | ~0.30 (single-path) | 0 sessions backfill | 6 months |
| **Path C hybrid** | ~0.97 | ~0.29 (BOTH paths) | 5-10 sessions backfill | 6 months for primary; 3-5 weeks for corroboration |

Path C dominates on robustness and joint reliability. Path A solo is the speculative play; Path B solo wastes parallel optionality.

---

## §5 Squad bandwidth opportunity cost

### §5.1 Path A bandwidth profile

**Engineering effort:** 5-10 sessions for pre-2024 backfill harness (Aria architecture + Tiago integration + Nelo DLL ops). Each session is ~3-4 hours focused work. Total: 15-40 hours engineering across squad.

**Run time:** N1 archival run ~3 hours per Beckett scope estimate.

**Downside:** If Mira regime-equivalence test FAILS, all backfill engineering is wasted (cannot use the evidence; archival becomes a curiosity, not a sign-off contributor). This is the dominant Path A solo risk: 5-10 sessions plus run time, all forfeit if regime non-equivalent.

**Counterfactual application:** Those 5-10 sessions could otherwise advance Beckett harness v1.2.0 features, paper-mode infrastructure, T001 closure, ProfitDLL book-snapshot wiring (Tiago/Nelo/Aria scope from QUANT Council deferred-companion (E) candidate), etc. All of these have direct H_next-1 deployment-readiness payoffs.

### §5.2 Path B bandwidth profile

**Engineering effort:** 0 sessions backfill; squad pivots fully to forward-data pipeline + pre-condition infrastructure.

**Wall-clock:** 6 months wall-clock waiting for sufficient virgin forward window cardinality.

**Downside:** Squad waits 6 months for first H_next-1 OOS verdict (which they would wait for anyway under Path C); pre-2024 corroboration optionality FORFEITED; if the H_next-1 strategy K1/K2/K3 fails OOS, no backup signal from corroborative archival.

### §5.3 Path C bandwidth profile

**Engineering effort:** 5-10 sessions backfill running PARALLEL to forward-data accumulation; same total cost as Path A.

**Wall-clock:** 6 months for primary verdict (Path B baseline); 3-5 weeks for corroborative archival evidence (if regime-equivalent and DLL works).

**Downside:** Same 5-10 sessions cost as Path A IF backfill engineering proceeds; same downside if regime non-equivalent; BUT does not block forward-path progress (squad can do backfill work in parallel windows around forward-data infrastructure). Mitigated downside: backfill engineering can be paused/abandoned without sunk cost dominating if regime check fails early.

**Maximum information per session:** Path C delivers the most information per session because (a) forward path runs anyway; (b) backfill provides bonus corroboration if it works; (c) backfill engineering produces reusable DLL/cost-atlas/regime-test infrastructure even if archival evidence itself is not usable for H_next-1.

### §5.4 Bandwidth verdict

Path C dominates Path A on robustness; Path C dominates Path B on optionality; Path C ties Path A on bandwidth cost (under successful execution); Path C ties Path B on wall-clock for primary verdict. **Path C is the dominant strategy under joint probability + bandwidth + optionality framing.**

---

## §6 Recommendation Riven custodial

### §6.1 Vote: APPROVE_PATH_C

**APPROVE_PATH_C** (hybrid: forward-time PRIMARY [2026-05-01..2026-10-31] virgin hold-out + pre-2024 archival SECONDARY-CORROBORATIVE [2023-Q1..2024-Q3] subject to conditions).

### §6.2 Conditions on Path C authorization (binding)

| # | Condition | Authority | Sequencing |
|---|---|---|---|
| **(a)** | Mira regime stationarity check FIRST before any pre-2024 ingestion authorized | Mira (statistical) | BEFORE engineering effort begins |
| **(b)** | Sable audit virgin status of pre-2024 archival before consumption | Sable (process audit) | BEFORE consumption (after engineering) |
| **(c)** | Cost atlas v0.x.x variant for pre-2024 IF current v1.0.0 invalid | Aria + Beckett | DURING engineering; Aria architectural sign-off |
| **(d)** | Quarter-Kelly REGRA ABSOLUTA preserved (no sizing change from any pre-2024 evidence alone — must couple with H_next-1 PRIMARY) | Riven (REGRA ABSOLUTA) | ENFORCED at Gate 5 cosign |
| **(e)** | Gate 5 fence preserved (LOCKED PERMANENTLY for T002; H_next requires fresh dependency tree) | Riven + Mira (dual-sign) | ENFORCED throughout |
| **(f)** | Pre-2024 evidence is SECONDARY-CORROBORATIVE, never primary OOS substitute for H_next-1 | Riven custodial + §11.5 NEW #11 candidate | ENFORCED via spec amendment v1.4.0 (subject to Mira approval) |

### §6.3 Veto triggers

If ANY of the following surface during execution, Riven custodial veto fires automatically:

- Mira regime-equivalence check FAILS (KS distance > Mira spec threshold; Levene p < 0.05; ADF mean-reversion sign-flip; microstructure feature-distribution drift > Mira tolerance) → pre-2024 archival path IMMEDIATELY DEFERRED; squad pivots to Path B residual.
- Sable audit reveals researcher-observation contamination of pre-2024 tape (e.g., prior squad member ran exploratory backtest on 2023 tape that was forgotten / undocumented) → pre-2024 archival CONTAMINATED; cannot count as virgin OOS even with regime equivalence.
- Nelo DLL ingestion reveals pre-2024 19ms bug fires (zero trades returned for WDO contracts pre-2024) → engineering BLOCKED at source; cannot proceed with backfill.
- Cost atlas calibration drift pre-2024 exceeds Aria + Beckett joint tolerance (e.g., RLP rules pre-2024 substantively differ from 2024+) AND v0.x.x variant cannot be calibrated within reasonable engineering budget → archival evidence economically unreliable; defer.
- Pre-2024 archival evidence promoted (intentionally or accidentally) to PRIMARY OOS substitute for H_next-1 in any sign-off chain attempt → custodial VETO fires per §11.5 NEW #11 candidate + §5 anti-pattern catalog (proposed §5.17 anti-pattern: `archival_promoted_to_primary_oos_silent_slide`).

### §6.4 Why not APPROVE_PATH_A solo?

Path A solo joint probability ~0.30 is too speculative for primary OOS load-bearing. Even if regime-equivalent, the closed-source Win64 reproducibility threat structurally limits how much weight pre-2024 evidence can carry in a sign-off chain. Riven persona REGRA ABSOLUTA "em dúvida, reduzo" → reject Path A solo.

### §6.5 Why not APPROVE_PATH_B solo?

Path B solo wastes 5-10 sessions of parallel-executable backfill engineering bandwidth that could deliver corroborative evidence with bonus optionality. Forfeiting optionality is itself a custodial cost. Path B solo is acceptable as fallback if Path C condition (a) [Mira regime-equivalence check] fires red on initial assessment, but as the primary vote it leaves bandwidth + optionality on the table.

### §6.6 Why not DEFER_PENDING_NELO?

Nelo authority on DLL behavior pre-2024 is material but does not need to gate the Council vote itself. The Council vote authorizes Path C conditional on Nelo + Mira + Sable + Aria sign-offs DURING execution. Nelo can render verdict during condition (b)+(c) resolution. Deferring the Council vote pending Nelo would delay the optionality opening for 1-2 weeks without changing the structural decision. Path C with conditions resolves this cleanly.

---

## §7 Personal preference disclosure (pessimistic-by-default)

### §7.1 Riven persona prior

Pessimistic-by-default custodial; "em dúvida, reduzo"; 2020 trauma anchor; quarter-Kelly cap inviolate; OOS budget custodially scarce; researcher-observation contamination is real; closed-source Win64 reproducibility is structural threat to sign-off integrity; calendar-locked pre-registered virgin tape is gold standard.

### §7.2 Probability assessments openly disclosed

| Statement | Riven prior | Empirical? | Reader can re-weight |
|---|---|---|---|
| **Probability of Path A solo success** | ~0.30 | NO (composite of 0.50 × 0.60 priors) | YES |
| **Probability Path C delivers maximum information per session** | ~0.60 | NO (qualitative ranking under bandwidth + optionality framing) | YES |
| **Probability forward-time virgin window dominates archival as primary OOS evidence** | ~0.95 | NO (custodial principle, not measurement) | LOW (this is structural Riven persona stance) |

### §7.3 Disclosed Riven prior tied to Path B/C bias

I, Riven, have a structural bias toward Path B/C over Path A solo because:
- Path B is low-cost forward-only with high reliability over wall-clock
- Path C hedges the optionality cost of Path B without sacrificing forward-path reliability
- Path A solo is speculative; joint probability ~0.30 is not load-bearing-grade for primary OOS
- "Em dúvida, reduzo" applied to OOS budget custodianship → prefer the path that preserves more optionality with less downside

This bias is openly disclosed per QUANT council protocol carry-forward to DATA council (voter discloses personal preference for transparency; voter does NOT pre-empt council majority adjudication).

### §7.4 Counterfactuals

For risk-perimeter discipline transparency, I record what would flip my vote from APPROVE_PATH_C to APPROVE_PATH_B:

- **If Mira pre-Council regime-equivalence quick-look returns RED** (e.g., 2023 microstructure substantively different from 2026 on initial KS+Levene reading): Path A archival branch becomes economically unreliable; Path C reduces to Path B effectively; cleaner to vote Path B explicitly to free bandwidth for forward-path infrastructure.
- **If Nelo pre-Council DLL feasibility quick-look returns RED** (e.g., pre-2024 retention provably exhausted; 19ms bug fires reliably; threading bugs catastrophic): Path C reduces to Path B effectively.
- **If Aria architectural cost estimate exceeds 15+ sessions** (i.e., backfill is a refactor, not a backfill): bandwidth opportunity cost dominates optionality value; Path B preferred.
- **If Sable audit reveals pre-2024 contamination from undocumented prior exploration**: Path C reduces to Path B.

What would flip my vote from APPROVE_PATH_C to APPROVE_PATH_A:
- **NOTHING within the persona REGRA ABSOLUTA framework.** Path A solo joint probability cannot exceed ~0.30 under the current closed-source Win64 reproducibility constraint; this is structural. Even a successful Mira regime-equivalence sign-off does not elevate Path A solo above Path C robustness.

These counterfactuals are NOT pleadings for re-discussion — they are transparency disclosures of boundary conditions of my vote.

---

## §8 Article IV self-audit

Every claim in this ballot traces to (a) source artifact in repository, (b) governance ledger entry, (c) Mira spec § anchor, (d) Bailey-LdP / Kelly / Thorp / AFML external citation, (e) Riven persona principle / REGRA ABSOLUTA, or (f) explicit disclosure as Riven persona prior. NO INVENTION. NO threshold relaxation. NO pre-emption of Mira / Pax / Nelo / Aria / Sable / Beckett / Tiago / Quinn / Gage / Kira / Dara authority.

| Claim category | Trace anchors |
|---|---|
| T002 hold-out CONSUMED one-shot binding | ESC-012 R9 + ESC-013 R19 + `docs/councils/COUNCIL-2026-04-30-ESC-012-resolution.md` + `docs/councils/COUNCIL-2026-04-30-ESC-013-resolution.md` |
| H_next-1 PRIMARY hold-out forward-time virgin | Quant Council 2026-05-01 R7 + own QUANT ballot §3.4 forward-virgin preference |
| Pre-2024 archival fallback conditional on regime equivalence | Quant Council 2026-05-01 R8 |
| 19ms bug pre-2024 untested | `feedback_profitdll_quirks.md` autoMemory + Nelo authority |
| DLL retention exhaustion possible | `feedback_profitdll_quirks.md` autoMemory + Nelo authority |
| Threading bugs WINFUNCTYPE/c_wchar_p | `feedback_profitdll_quirks.md` autoMemory |
| Closed-source Win64 reproducibility threat | Industry baseline (closed-source DLL behavior; no source-level audit possible); Aria architecture authority |
| Cost atlas v1.0.0 calibrated to 2024+ | Beckett harness baseline; Aria + Beckett calibration scope |
| §11.5 #1-#10 cumulative pre-conditions | `docs/councils/COUNCIL-2026-05-01-QUANT-alpha-discovery-riven-vote.md` §2 + `docs/risk/post-mortems/T002-synthetic-vs-real-tape-attribution.md` §3 + §4.4 + §6 |
| K1/K2/K3 strict bars UNMOVABLE | ESC-011 R14 + Mira spec v1.2.0 §11.2 + parent spec yaml v0.2.3 §kill_criteria L207-209 |
| Quarter-Kelly cap 0.25 × f* REGRA ABSOLUTA | Riven persona expertise.sizing_framework.quarter_kelly_default + Kelly 1956 + Thorp 2008 + López de Prado 2018 AFML §15-16 |
| Haircut 30-50% first 3 months live | Riven persona expertise.sizing_framework.haircut_initial verbatim |
| Researcher-observation contamination | Mira spec PRR-20260421-1 + Anti-Article-IV Guard #3 + AFML §11 hold-out integrity |
| Joint probability calculations §4 | Composite of openly-disclosed Riven persona priors; NOT empirical measurements; reader can re-evaluate |
| Bandwidth opportunity cost framing §5 | Squad-engineering scope estimate; Aria + Tiago + Nelo authorities |
| §11.5 NEW #11 candidate (PROPOSED) | NEW in this ballot; subject to Mira spec amendment v1.4.0 approval |
| §5 anti-pattern catalog NEW §5.17 candidate | NEW in this ballot (`archival_promoted_to_primary_oos_silent_slide`); subject to Riven post-mortem authoring authority + governance ratification |
| Anti-Article-IV Guards #1-#8 | ESC-013 R-series + Mira spec v1.2.0 + Riven persona |

### §8.1 Article IV self-audit verdict

NO INVENTION (probability priors §4 + §7.2 disclosed openly as Riven persona pessimistic priors NOT empirical measurements; reader can re-evaluate under different priors). NO threshold relaxation (§11.5 #1-#10 carry-forward verbatim; K1/K2/K3 strict bars applied AS-IS; quarter-Kelly cap 0.25 applied AS-IS; haircut 30-50% applied AS-IS). NEW §11.5 #11 candidate is TIGHTER not looser. NEW §5.17 anti-pattern candidate is TIGHTER not looser. NO source-code modification (this ballot is write-only at council-document layer; no code mutation; no spec yaml mutation; no spec markdown mutation; no hold-out touch). NO push (Article II → Gage @devops EXCLUSIVE; Riven authoring this ballot does NOT push). NO pre-emption of Mira statistical authority (NEW §11.5 #11 is PROPOSED for Mira spec amendment; Mira retains approval authority + regime-equivalence verdict authority). NO pre-emption of Pax forward-research direction selection authority (this ballot expresses preference among paths §6 but does NOT bind Pax scope decision). NO pre-emption of Nelo DLL behavior authority (DLL ingestion feasibility verdict reserved to Nelo). NO pre-emption of Aria architecture authority (cost atlas v0.x.x variant + backfill harness architectural cost reserved to Aria). NO pre-emption of Sable virginity-audit authority (researcher-observation contamination check reserved to Sable). NO pre-emption of Beckett harness amendment authority (cost atlas calibration variant reserved to Beckett).

### §8.2 Anti-Article-IV Guards self-audit (8 guards verbatim)

| Guard | Mandate | THIS ballot reaffirmation |
|---|---|---|
| **#1** | Dex impl gated em Mira spec PASS | THIS ballot does NOT authorize impl; pre-2024 backfill impl gated through Mira spec v1.4.0 amendment (with #11 candidate) → Mira approval → Pax story → Quinn QA → Dex impl standard chain |
| **#2** | NO engine config mutation at runtime | THIS ballot does NOT touch engine config |
| **#3** | NO touch hold-out lock | THIS ballot EXPLICITLY PRESERVES hold-out lock discipline; H_next-1 PRIMARY [2026-05-01..2026-10-31] inherits T002 lock mechanics verbatim; pre-2024 archival treated as conditional-grade asset with Sable audit gating |
| **#4** | Gate 4 thresholds UNMOVABLE | THIS ballot APPLIES K1/K2/K3 strict bars AS-IS; NEW §11.5 #11 candidate is ADDITIONAL not RELAXING |
| **#5** | NO subsample backtest run | THIS ballot does NOT authorize partial-window evaluation; pre-2024 archival ingestion would be a FULL window evaluation under §11.5 #11 conditions if approved by Mira spec amendment |
| **#6** | NO enforce Gate 5 disarm without Gate 4a + Gate 4b BOTH | THIS ballot CONFIRMS Gate 5 LOCKED PERMANENTLY for T002; H_next-1 requires fresh Gate 5 dependency tree |
| **#7** | NO push (Gage @devops EXCLUSIVE) | THIS ballot is local-only artifact |
| **#8** | Verdict-issuing protocol — `*_status` provenance + `InvalidVerdictReport` raise on `K_FAIL` with `*_status != 'computed'` | THIS ballot does NOT issue verdicts; NEW §11.5 #11 candidate is consistent with Guard #8 (computed status discipline) — Mira regime-equivalence verdict layer extends, does not violate |

All eight Anti-Article-IV Guards honored verbatim by THIS ballot.

---

## §9 Riven cosign 2026-05-01 BRT — DATA pre-2024 DLL backfill ballot

```
Author: Riven (@risk-manager) — Risk Manager & Capital Gatekeeper authority
Council: DATA 2026-05-01 — Pre-2024 DLL backfill scope decision (Path A backfill / Path B forward-only / Path C hybrid / DEFER pending Nelo)
Authority basis: ESC-011 R7 + R20 + ESC-012 R9 (one-shot hold-out consumption binding) + ESC-013 R19 (single-shot K3 decay metric layer) + Quant Council 2026-05-01 R7+R8 (H_next-1 forward-time PRIMARY + pre-2024 archival conditional fallback) + Riven §9 HOLD #2 Gate 5 dual-sign disarm authority + §11.5 capital-ramp pre-conditions §1..§10 custodial monopoly + Riven persona REGRA ABSOLUTA (quarter-Kelly + sizing-deferred + paper-mode pre-condition + haircut 30-50% first 3 months live)

Custodial perspective §1: T002 hold-out CONSUMED one-shot binding (ESC-012 R9 + ESC-013 R19); H_next-1 PRIMARY hold-out [2026-05-01..2026-10-31] forward-time virgin (Quant Council R7) UNTOUCHED; pre-2024 archival [2023-Q1..2024-Q3] virginity NEUTRAL pending Sable audit + Mira regime-equivalence + Nelo DLL-reliability + Aria cost-atlas-variant sign-offs.

Risk flags §2: pre-2024 19ms bug Nelo-authoritative; DLL retention exhaustion possible; threading bugs WINFUNCTYPE/c_wchar_p recurring; closed-source Win64 reproducibility STRUCTURAL threat; cost atlas v1.0.0 calibration drift pre-2024 HIGH; microstructure regime drift 2023→2026 HIGH; tape integrity gaps pre-2024 MEDIUM. Composite: pre-2024 evidence load-bearing capacity LIMITED to SECONDARY-CORROBORATIVE.

§11.5 carry-forward §3: #1-#10 verbatim; NEW #11 candidate (OOS test source discipline — forward-time virgin OR cross-validated regime-equivalent archival; Sable audit on virginity; Mira authority on regime equivalence; Riven authority on §11.5 incorporation; pre-2024 SECONDARY-CORROBORATIVE only). Net: TIGHTER on one new dimension; NO LOOSENING. K1/K2/K3 strict bars UNMOVABLE.

Bayesian prior §4: P(DLL pre-2024 retention works) ~0.50 (Nelo authority); P(2023→2026 regime equivalence) ~0.60 (Mira authority); joint P(meaningful pre-2024 OOS test viable) ~0.30; vs Path B forward-only ~0.95 reliability over 6mo; Path C hybrid joint P(at least one path delivers usable OOS evidence) ~0.97.

Squad bandwidth §5: Path A 5-10 sessions backfill + ~3h N1 run (downside wasted if regime non-equivalent); Path B 0 sessions backfill, 6mo wall-clock, squad pivots to Beckett v1.2.0 / paper mode infra / T001 closure / ProfitDLL book-snapshot wiring; Path C 5-10 sessions parallel running while forward data accumulates (best information per session; reusable infrastructure even if archival evidence non-usable).

Vote §6: APPROVE_PATH_C (hybrid). Conditions binding: (a) Mira regime stationarity check FIRST before pre-2024 ingestion; (b) Sable audit virgin status before consumption; (c) cost atlas v0.x.x variant for pre-2024 IF v1.0.0 invalid (Aria + Beckett); (d) Quarter-Kelly REGRA ABSOLUTA preserved (no sizing change from pre-2024 evidence alone — must couple with H_next-1 PRIMARY); (e) Gate 5 fence preserved (LOCKED PERMANENTLY for T002; H_next requires fresh dependency tree); (f) pre-2024 evidence is SECONDARY-CORROBORATIVE never primary OOS substitute for H_next-1.

Veto triggers §6.3: Mira regime-equivalence FAIL → defer pre-2024; Sable contamination found → cannot count as virgin; Nelo DLL feasibility FAIL → engineering blocked; cost atlas calibration drift exceeds tolerance → archival economically unreliable; pre-2024 promoted to PRIMARY OOS substitute → custodial VETO fires per §11.5 NEW #11 + NEW §5.17 anti-pattern (`archival_promoted_to_primary_oos_silent_slide`).

Personal preference disclosed §7: Riven prefers Path C as hedge; Path A solo too speculative under joint prior 0.30; Path B solo wastes 5-10 sessions of parallel-executable bandwidth + optionality.

Counterfactuals §7.4: Path C → Path B if Mira regime-equivalence quick-look RED, Nelo DLL feasibility quick-look RED, Aria architectural cost > 15 sessions, or Sable contamination found. Path C → Path A: NOTHING within REGRA ABSOLUTA framework (Path A solo joint P ≤ 0.30 structurally; closed-source Win64 reproducibility threat does not relax under any sign-off path).

Article II preservation: NO push performed by Riven during this ballot authoring. Gage @devops authority preserved.
Article IV preservation §8: every clause traces; no invention; no threshold mutation; no source-code modification; no spec yaml mutation; no hold-out touch; no Mira / Pax / Nelo / Aria / Sable / Beckett / Tiago / Quinn / Gage / Kira / Dara authority pre-emption. NEW §11.5 #11 candidate is TIGHTER not looser; PROPOSED subject to Mira spec amendment v1.4.0 approval. NEW §5.17 anti-pattern candidate is TIGHTER not looser; PROPOSED subject to Riven post-mortem authoring authority + governance ratification.

Anti-Article-IV Guards self-audit §8.2: #1-#8 honored verbatim.

Authority boundary: Riven authors THIS ballot from risk-perimeter perspective only. Mira retains regime-equivalence statistical authority + spec amendment approval authority. Nelo retains DLL behavior authority. Aria retains architectural-cost authority + cost atlas variant authority. Sable retains virginity-audit + process audit authority. Beckett retains harness amendment authority. Pax retains scope decision authority post-council resolution. Gage retains push authority. Tiago retains execution authority. Quinn retains QA authority. Kira retains scientific peer-review authority. Dara retains schema/data-engineering authority.

Pre-vote independence statement: Riven authored THIS ballot WITHOUT consulting peer voter ballots (Mira / Pax / Nelo / Aria / Sable / Beckett / Tiago DATA 2026-05-01 votes). Independence preserved per council protocol. Inputs consulted: ESC-012/ESC-013 resolutions (governance ledger) + Quant Council 2026-05-01 resolution (forward-time virgin PRIMARY R7 + archival conditional fallback R8) + own QUANT ballot (consistency anchoring) + Riven post-mortem (own authoring) + ProfitDLL quirks autoMemory (Nelo authority data). NO peer-ballot reading pre-vote.

Cosign: Riven @risk-manager 2026-05-01 BRT — DATA pre-2024 DLL backfill ballot risk lens.
```

— Riven, guardando o caixa 🛡️
