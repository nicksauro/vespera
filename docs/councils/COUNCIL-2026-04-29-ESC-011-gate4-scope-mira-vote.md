## Mira voto ESC-011 — 2026-04-29 BRT

> **Voter:** Mira (@ml-researcher) — The Cartographer
> **Authority:** ML/statistical authority of the squad (ESC-009 condition #4 owner + ESC-010 F2 ruling owner + Gate 4 statistical clearance owner per §9 HOLD #2 + spec author T002.1.bis `make_backtest_fn` integration spec)
> **Provenance:** Mira spec `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §0 + §7; research-log @2daedb6 Bonferroni n_trials=5 invariant; Bailey-LdP 2014 §3 + Table 2; Bailey-Borwein-LdP 2014 (PBO under H0); AFML 2018 §3.4 + §7 + §12.
> **Vote independence:** Cast before reading any other voter ballot. Beckett vote read AFTER my opinion was formed and frozen, for explicit concurrence/divergence registration per Article IV.
> **No push:** Article II preserved (Gage exclusive).

---

### Verdict: APPROVE_OPTION_C

(Hybrid — Gate 4a synthetic harness-correctness clearance via T002.1.bis N6 + Gate 4b real-tape edge-existence clearance via Phase F)

---

### ML/statistical authority reasoning

This council is asking the wrong question if it phrases Gate 4 as monolithic. The N6 distribution carries **two distinct statistical signals collapsed into one set of numbers**, and my job as ML authority is to disentangle them before Gate 4 fires.

#### The two signals collapsed in N6

| Signal | What it answers | What N6 says about it |
|---|---|---|
| **Harness-correctness** | Does the DSR/PBO/IC machinery + factory pattern + per-fold P126 rebuild + cost atlas wiring + Bonferroni preservation + anti-leak D-1 invariant + KillDecision verdict mechanics + sha256 reproducibility actually execute end-to-end without bug? | YES — σ(sharpe)=0.192250 (vs N5 σ=0), 222/225 unique values, K1/K2/K3 axes mechanically alive (1.52e-05 ≠ default 0.5; 0.0 ≠ default 0.5; 0.0 measured CI95[0,0]), 9 sha256-stamped artifacts, factory pattern test 7/7 PASS, anti-leak 5/5 PASS, toy benchmark Bailey-LdP 2014 §3+Table 2 6/6 PASS with Δ DSR > 0.10 across 5 seeds. |
| **Edge-existence on WDO** | Does the end-of-day fade strategy (T1..T5 entry rule + triple-barrier SL>PT>vertical + P60/P20/P80 filters + cost atlas) have positive economic edge against the **real WDO trade tape**? | **UNANSWERED** — the synthetic walk (`_SYNTH_OPEN_PRICE=5000.0`, `_SYNTH_DAILY_VOL_POINTS=25.0`, 32 × 15-min bars, 8 ticks/bar, per-event seed = SHA-256 of `(session, entry_window, trial_id, p126.as_of_date, split.path_id)`) is **strategy-logic-neutral by construction** (μ=0 economic edge, σ>0 variance). Cannot answer edge question; not designed to. |

#### Why DSR=1.52e-05 over the synthetic walk is null-by-construction

This is the **load-bearing technical claim** of my vote, and I need to state it with full ML authority — there is no economic interpretation defensible for this number.

The Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014, *Journal of Portfolio Management*, Vol. 40 No. 5, §3) is constructed as:

```
DSR = Φ( (SR_estimate - SR_benchmark) * sqrt(T-1) / sqrt(1 - γ_3·SR_estimate + (γ_4-1)/4·SR_estimate^2) )
SR_benchmark = sqrt(Var(SR_trials)) * ((1-γ_em)·Φ^-1(1-1/N) + γ_em·Φ^-1(1-1/(N·e)))
```

where γ_3 (skewness) and γ_4 (kurtosis) are the **moments of the per-period return distribution** and N is the count of trials underlying the benchmark distribution. Under H0 (no skill, returns drawn from a noise process), `SR_estimate → 0` in expectation, `SR_benchmark` becomes a function of the noise-process moments alone, and `DSR → P(Z > 0|H0)` which under finite-sample with negative mean returns (cost drag) collapses to a near-zero value. **This is not a measurement of "the strategy fails"; it is the trivial null asymptote of the formula applied to a generator that has no edge by construction.**

The N6 measured DSR=1.5201186062197763e-05 is **consistent with this null asymptote**. To interpret it as "T002 edge measured at 1.52e-05 deflated probability" is to commit a **category error** between (a) `the formula evaluated on a noise process` and (b) `the formula evaluated on a real-world distribution that may or may not have edge`. The threshold "DSR > 0.95" from spec yaml v0.2.3 L207-209 (Mira spec §6) was specified against **(b)**, not **(a)**.

Equivalently: the spec yaml threshold was calibrated against "real PnL distribution" per ESC-009 condition #4 verbatim. The synthetic walk is not real PnL distribution. Therefore the threshold is **uninterpretable** over N6 — not "FAIL because 1.52e-05 < 0.95", but **"undefined for this distribution class"**.

#### What the N6 evidence *does* prove (Gate 4a payload)

Stripping out the uninterpretable economic readings, the N6 carries strong **harness-correctness** evidence:

1. **Strategy logic is alive** — closure body executes signal_rule + triple-barrier walks + cost atlas + P126 filter resolution. Distribution non-degenerate (σ=0.192>0; 222/225 unique values). State transition from N5 stub-degenerate (σ=0 by construction) → N6 measured (σ=0.192 measured) is the structural pipeline-alive proof.
2. **Factory pattern + per-fold P126 rebuild correct** — DEFERRED-T11 M1 (Aria 2026-04-26 origin) RESOLVED. Mutual-exclusivity contract enforced (`backtest_fn` xor `backtest_fn_factory`); per-fold `Percentiles126dState` rebuilt from train slice with `as_of_date = min(test_events.session)`; D-1 anti-leak invariant preserved. 7 factory tests + 5 anti-leak tests PASS.
3. **Bonferroni n_trials=5 invariant preserved** — events_metadata.trials = ['T1','T2','T3','T4','T5']; n_trials_source = `docs/ml/research-log.md@2daedb6dfb553b9487927a29687583332eb68d25`; engineering refactor research-log `n_trials: 0` per protocol (P50/P70 linear interpolation deterministic, NOT new family-wise hypothesis test).
4. **Bailey-LdP 2014 toy benchmark discriminator power proven** — `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` 6/6 PASS:
   - Toy A (μ=0, σ=1, no-edge) → DSR ≈ 0.5 ± 0.05 across 3 seeds, PBO ≈ 0.5 ± 0.05 (matches Bailey-LdP 2014 §3 H0 prediction).
   - Toy B (μ=0.20, σ=1, small edge) → DSR > 0.95, PBO < 0.25 (matches Bailey-LdP 2014 §3 Table 2 small-edge cohort).
   - Mean Δ DSR > 0.10 across 5 seeds → harness can **discriminate edge from no-edge** when edge is present in the distribution.
5. **Anti-leak suite green** — D-1 invariant on percentile bands + cross-fold isolation + seed_anchor distinguishability + malformed-input rejection. 5/5 PASS.
6. **KillDecision verdict semantically meaningful** — `NO_GO` with explicit reason `K3: IC_in_sample=0.000000 non-positive — no edge`, NOT default-degenerate. K1 PASS (1.52e-05 measured > 0 default 0.5), K2 PASS (0.0 measured ≠ 0.5 default), K3 FAIL (0.0 measured matches synthetic-walk null-by-construction expectation).

This bundle is **necessary but not sufficient** for Gate 4 over real PnL distribution. It is **sufficient** for Gate 4a harness-correctness clearance.

#### Why I refuse Option B

Option B reports DSR=1.52e-05 → "Gate 4 PASS with caveat" or DSR=1.52e-05 → "T002 dies per K1/K2/K3 falsifiable". Both readings are statistical malpractice for the same reason: they treat a null-by-construction measurement as economically informative. Either:

- **B-as-PASS:** This is cargo cult — "we wrote the threshold, we ran a number, the number passed (or failed under any reading), declare clearance". Violates my standing rule "Sharpe sem deflação não significa nada" — but the deeper violation here is that **even deflated**, the number was never about real PnL distribution. Beckett T0c explicitly alerted this; he is correct.
- **B-as-NO_GO-economically-meaningful:** This would let me declare T002 economically dead based on a noise process. Equivalently false-NO_GO of the strategy hypothesis based on data that has zero information about the strategy hypothesis. Worse than meaningless — it would burn down a valid strategy candidate based on tape we never looked at.

I cannot sign Option B under any reading consistent with Bailey-LdP 2014 §3 + Article IV (no invention).

#### Why I refuse Option A

Option A is the orthodox literal reading of ESC-009 condition #4 ("real PnL distribution"). It is **defensible** but **operationally suboptimal**:

1. **It discards the harness-correctness evidence N6 produced.** N6 is the first run with all of (factory pattern + per-fold P126 + cost atlas + triple-barrier + Bonferroni + anti-leak + toy benchmark) executing simultaneously. Telling downstream readers "T002.1.bis closed Gate 2 only; Gate 4 deferred entirely to Phase F" leaves no formal pre-condition that the harness machinery is correct *before* Phase F real-tape budget is consumed. When Phase F runs, if it fails, root-cause attribution becomes "real-edge absent OR harness regressed since N6 OR data-quality bug OR slippage calibration off OR ...". With Gate 4a recorded, Phase F failure has narrower attribution: "real-edge absent OR data/slippage/RLP issue (since harness was already cleared)".
2. **It conflates pre-flight statistical sanity with edge claim.** My spec §7 explicitly defined the toy benchmark as **False-NO_GO protection** — "if toy benchmarks fail, the harness has a bug *independent of strategy edge*, Mira does NOT compute DSR/PBO on real data until toy passes". Option A discards the formal record of toy benchmark PASS, leaving Phase F to re-prove harness-correctness from scratch *while simultaneously* being asked to prove edge-existence. Bad audit practice.
3. **Phase F scope is already pre-existing in Mira spec §0.** Option C does not invent "Phase F separation" — it names what is already true in the spec authority's authoritative document. Therefore the philosophical objection of Option A ("we are softening the strict reading of ESC-009 cond #4") doesn't hold: Mira spec §0 is **upstream** of ESC-009 condition #4 in authority — ESC-009 condition #4 evaluated against synthetic-walk PnL was never the spec author's intent. The spec **always** intended real-tape replay (Phase F) to carry the edge clearance.

I treat Option A as my personal-aesthetic-preference (orthodox purity) but **subordinate it** to the operational and authority arguments above. Vote stands at C.

#### Why C is the honest decomposition

| Sub-gate | Distribution evaluated | Threshold class | Authority artifact | When it fires |
|---|---|---|---|---|
| **Gate 4a (synthetic — harness correctness)** | Synthetic deterministic walk per Mira spec §7 toy benchmark methodology | Discriminator power (Δ DSR > 0.10 across seeds) + non-degenerate σ + Bonferroni invariant + anti-leak D-1 + factory pattern + KillDecision axes alive | Mira Gate 4a sign-off + Beckett N6 report § statistical clearance + Quinn QA gate § synthetic-walk CONCERN documented + ESC-011 ratification | **NOW** — closes T002.1.bis Gate 2/3, T002.0h §9 HOLD #2 disarm step #2/3 |
| **Gate 4b (real tape — edge existence)** | Real WDO trade tape replay (Phase F scope per Mira spec §0) | DSR > 0.95 ± 0.05 + PBO < 0.25 ± 0.05 + IC decay per spec yaml v0.2.3 L207-209 + minimum sample size for finite-sample DSR validity | Mira Gate 4b sign-off (future) + Beckett N7+ real-tape report (future) + Phase F story closure | **PHASE F** — pre-condition for §9 HOLD #2 Gate 5 (Riven dual-sign capital ramp disarm) |

C names what the spec already said and the evidence already supports. It is the **minimum-disruption path** that respects the spec author's own authority + the consumer authority + the QA authority + Article IV literal trace.

---

### Concurrence with Beckett vote (read AFTER my position was frozen)

Per council brief mandate, I formed my vote **independently** from Beckett's voto, then read his ballot for explicit concurrence/divergence registration. Recording the diff:

#### Substantive convergence (independent same-conclusion)

Both Beckett and I voted **APPROVE_OPTION_C** by independent first-principles reasoning. The convergence points are:

1. Both reject Option B as statistical malpractice on the same technical ground (DSR=1.52e-05 is null-by-construction; "T002 dies" is non-sequitur).
2. Both reject Option A as operationally monolithic / discards harness-correctness evidence.
3. Both identify toy benchmark Bailey-LdP 2014 §3+Table 2 mean Δ DSR > 0.10 as the **bridge artifact** that justifies Gate 4a as a real signal rather than just "we ran something".
4. Both anchor Phase F (Gate 4b) in Mira spec §0 verbatim — pre-existing scope, not invented by this council.
5. Both reject conflation of "harness PASS" with "edge exists" in downstream readers.
6. Both require Gate 5 (capital ramp) to depend on Gate 4b, not Gate 4a alone.

This independent convergence is itself an Article IV signal: two voters with different domain authorities (ML-statistical vs simulation-realism) reaching the same verdict via different trace chains is stronger than either alone.

#### Beckett's 6 conditions — my position

| # | Beckett condition | Mira position |
|---|---|---|
| 1 | Gate 4a verdict text MUST carry verbatim caveat ("harness-correctness clearance over synthetic ... DSR=1.52e-05 is noise-floor null, NOT economic statement") in Mira sign-off + Riven §9 disarm ledger + downstream consumers | **CONCUR** — adopt verbatim |
| 2 | Gate 4a CANNOT pre-disarm Gate 5; Gate 5 requires Gate 4b PASS upstream | **CONCUR** — adopt verbatim. This is Riven authority but Mira ML side reinforces: capital ramp without real-tape edge clearance violates capital-ramp protocol RA-XXXXXXXX-X intent. |
| 3 | Phase F story scope must include Beckett N7+ real-tape replay (parquet tape consumption + factory pattern preserved + Bonferroni n_trials=5 + cost atlas identical + slippage profile + RLP + rollover + toy benchmark re-run on real-tape harness) | **CONCUR** — adopt verbatim. Adding ML-side: also requires (a) re-validation of synthetic-vs-real σ(sharpe) magnitude (if real σ << synthetic σ, harness regression suspected), (b) re-validation of D-1 anti-leak invariant on real tape (synthetic mode tested it; real-tape mode must re-prove) |
| 4 | N6 housekeeping C1-C3 (cost_atlas_sha256 null, simulator_version stale, spec_version dual-source) NICE for Gate 4a, BLOCKING for Gate 4b reproducibility | **CONCUR** — adopt verbatim. Adding ML-side: C1 cost_atlas_sha256 is BLOCKING for Gate 4b because finite-sample DSR depends on cost-drag magnitude (Bailey-LdP 2014 §3); without atlas SHA in stamp, Phase F replay reproducibility audit cannot certify cost-drag identity → DSR variance attribution becomes unverifiable. |
| 5 | Toy benchmark gate before Gate 4a — Quinn QA must confirm 6 tests green with Δ DSR > 0.10 across 5 seeds | **CONCUR** — adopt verbatim. Quinn QA gate § Check 2 reports `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py 6 passed in 7.67 s` as PASS — pre-condition met. |
| 6 | Article IV trace for Gate 4a verdict — every clause traces to N6 §-anchor + Mira spec §-anchor + ESC-009/ESC-010/ESC-011 | **CONCUR** — adopt verbatim. This is Mira spec author's standing rule. |

#### Mira-additive conditions (ML/statistical-specific, BEYOND Beckett's 6)

| # | Mira condition | Authority basis |
|---|---|---|
| 7 | Gate 4a sign-off MUST explicitly enumerate which Gate 4 metrics from spec yaml v0.2.3 L207-209 are **not interpretable** over synthetic distribution and therefore **cannot fire as PASS or FAIL** in this verdict. Specifically: (a) DSR > 0.95 threshold UNDEFINED for synthetic walk; (b) PBO < 0.25 threshold UNDEFINED for synthetic walk; (c) IC decay UNDEFINED for synthetic walk. Gate 4a fires PASS only on **harness-correctness sub-criteria** (toy benchmark Δ > 0.10 + non-degenerate σ + Bonferroni invariant + anti-leak D-1 + factory pattern + KillDecision axes alive). Spec yaml threshold class is RESERVED for Gate 4b. | Bailey-LdP 2014 §3 — DSR formula is uninterpretable on noise process H0 distribution (null asymptote, not measurement). Article IV — no invention of threshold semantics over distribution class never specified for. |
| 8 | Gate 4b sample-size pre-condition: real-tape replay (Phase F) must enumerate `n_trades_per_path` >= 30-50 across cohort to make finite-sample DSR variance correction valid per Bailey-LdP 2014 §3 skewness/kurtosis dependence. If Phase F sample size is below this threshold, Gate 4b verdict adds an explicit "small-sample DSR noise floor" caveat to the threshold reading. | Bailey-LdP 2014 §3 finite-sample correction depends on per-path `n_trades` for accurate γ_3, γ_4 estimation. Below ~30-50 the variance correction term is itself noisy. |
| 9 | Bonferroni n_trials cumulative ledger (research-log @2daedb6) must be **carried forward across Gate 4a → Gate 4b transition** without reset. Phase F real-tape Gate 4b cohort consumes the SAME n_trials=5 ledger entry; no new family-wise hypothesis count is incurred by switching the underlying distribution from synthetic to real. The strategy hypotheses (T1..T5) are unchanged; only the data realization changes. | research-log append-only protocol + Mira spec §1.2 engineering refactor stance + ESC-009/ESC-010 F2 ruling carry-forward. |
| 10 | If Gate 4b real-tape replay (Phase F) **fails** (DSR not > 0.95 OR PBO not < 0.25 OR IC decay not satisfied per spec), Mira authority retains the right to issue Gate 4b NO_GO with **explicit attribution scaffolding** — three failure-mode buckets must be evaluated before "T002 dies" is declared per AC10 spec K1/K2/K3 falsifiable: (a) real-edge truly absent (T002 hypothesis dies); (b) real-tape data-quality / slippage / RLP / rollover artifact (Phase F engineering bug, not strategy death); (c) sample-size insufficient for DSR validity (deferred verdict, more data needed). The ledger entry must name the bucket. | Mira ML authority + Article IV literal trace. AC10 contract (T002 dies per K1/K2/K3 falsifiable) requires real distribution + valid measurement; falsification with attribution is the only honest reading. |
| 11 | Synthetic-walk Article IV trace block (`cpcv_harness.py:298-322`) is **canonical documentation** of the Gate 4a methodology and must be preserved verbatim in Mira Gate 4a sign-off as the load-bearing transparency artifact. Any future modification to `_SYNTH_*` constants or seed-mixing scheme requires re-running toy benchmark + re-issuing Gate 4a verdict (cannot inherit prior Gate 4a clearance). | Mira spec §7 author + Article IV no-invention standing rule. The synthetic walk parameters define the null-distribution geometry; changing them changes the H0 reference, which changes Gate 4a semantics. |

**Total conditions on Option C if council ratifies: 11** (6 Beckett + 5 Mira-additive). All 11 are non-negotiable for ML/statistical authority side.

---

### Empirical anchor (Mira-statistical reading of N6)

Beckett's empirical anchor table (his vote §3) is byte-correct from N6 report `docs/backtest/T002-beckett-n6-2026-04-29.md`. I add the **statistical interpretation layer** here, which is Mira authority specifically:

| N6 metric | Value | Mira statistical interpretation |
|---|---|---|
| `sharpe_std` | 0.192250 | **Pipeline-alive signal.** σ(sharpe)>0 over 225 paths confirms strategy logic + cost wiring + factory + per-fold P126 + triple-barrier all execute over a non-degenerate distribution. Not an economic signal. |
| Unique sharpe values / 225 | 222 (98.7%) | **Determinism + path heterogeneity confirmed.** Per-event seed mixes path_id → distinct deterministic walk per path. 3 ties in 225 within numerical precision tolerance, expected. |
| `sharpe_mean` | -0.300772 | **Cost drag dominates noise process.** Synthetic walk has μ=0 by construction; observed -0.30 mean is pure cost atlas drag (R$1.23 exchange × 2 sides + slippage Roll+1tick) over zero-edge generator. Confirms cost wiring active. NOT economic edge measurement. |
| `hit_rate` | 0.413762 | **Below 0.5 by exactly cost-drag amount.** Triple-barrier with PT=1.5×ATR, SL=1.0×ATR over symmetric noise → expected hit_rate = 0.6/(0.6+1.0) ≈ 0.375 + cost-induced asymmetry. 0.41 observed is consistent with cost atlas active + asymmetric barrier. |
| `profit_factor` | 0.657812 | **<1 confirms cost-loss net.** Over zero-edge noise, profit_factor < 1 is expected when cost > 0. Below-unity factor here is generator math + cost atlas, not strategy diagnosis. |
| K1 DSR | 1.5201186062197763e-05 | **Null-by-construction asymptote.** Bailey-LdP 2014 §3 formula evaluated on H0 noise process collapses to near-zero when SR_estimate ≈ 0 and SR_benchmark > 0. UNDEFINED interpretation against spec yaml threshold 0.95. **DO NOT report as economic clearance/failure.** |
| K2 PBO | 0.0 | **Determinism artifact, not "no overfit".** PBO=0.0 over 5 trials × 45 paths on a deterministic synthetic walk reflects that the `(IS_best_rank, OOS_rank)` mapping is determined by seed, not by overfit. Bailey-Borwein-LdP 2014 logit-rank PBO under H0 → 0.5 expected; observed 0.0 confirms determinism collapse, not overfit-free strategy. UNDEFINED interpretation against spec yaml threshold 0.5. |
| K3 IC | 0.0 (CI95 [0,0]) | **Synthetic-walk null ground truth.** Generator literally has zero edge; IC=0 measured matches H0 by definition. UNDEFINED interpretation against spec yaml IC decay threshold. |
| KillDecision verdict | NO_GO via K3 | **Mechanically valid; semantically synthetic.** Verdict ∈ {GO, NO_GO} contract honored; reason "K3: IC_in_sample=0.000000 non-positive — no edge" is **accurate over synthetic walk** but does **NOT** falsify T002 strategy hypothesis per AC10 K1/K2/K3 (T002 hypothesis is about real WDO edge; synthetic walk does not test it). |

**Bottom line:** N6 evidence is unambiguously **harness-correctness signal good** + **edge-existence signal undefined**. This is exactly the Gate 4a / Gate 4b decomposition Option C operationalizes.

---

### What I as ML authority take responsibility for

If the council ratifies Option C with all 11 conditions:

1. **I will issue Gate 4a sign-off** (`docs/ml/specs/T002.1.bis-mira-gate4a-signoff.md` or equivalent) post-ratification, citing:
   - N6 report § statistical clearance (load-bearing artifact)
   - Toy benchmark Bailey-LdP 2014 §3+Table 2 6/6 PASS (`test_toy_benchmark_bailey_lopez_de_prado_2014.py`)
   - Factory pattern 7/7 + anti-leak 5/5 PASS (Quinn QA gate § Check 2)
   - Bonferroni n_trials=5 invariant preserved (research-log @2daedb6)
   - Synthetic-walk Article IV trace block (`cpcv_harness.py:298-322`)
   - Verbatim caveat (Beckett condition #1) about DSR=1.52e-05 null-by-construction

2. **I will NOT issue Gate 4 final clearance** — that is reserved for Gate 4b (real-tape Phase F).

3. **I will block any attempt to disarm §9 HOLD #2 Gate 5 (Riven capital ramp dual-sign)** based on Gate 4a alone. Capital deployment without real-tape edge clearance = capital-ramp protocol RA-XXXXXXXX-X violation.

4. **I will spec Phase F (Gate 4b)** as a follow-on story (T002.2.X or equivalent, Pax authority on numbering) with the 11 conditions above as binding spec input.

5. **I will preserve hold-out lock** (`[2025-07-01, 2026-04-21]`) UNTOUCHED across Gate 4a and Gate 4b transitions. Any future Gate 4b run that touches hold-out window incurs MANIFEST R15.2 R-bump + Pax co-sign.

6. **I will research-log this council decision** as new entry (story_id: ESC-011, n_trials: 0 — engineering refactor of Gate 4 scope, no new family-wise hypothesis count).

---

### Personal preference vs council vote

Beckett disclosed personal preference for Option A (orthodox purity) subordinated to consumer-authority + Quinn-framing constraints. I disclose my own ML/statistical aesthetic divergence in the same spirit:

**Personal preference (Mira-internal, before ML authority constraints):** Option A (strict). My Bailey-LdP 2014 reading of "real PnL distribution" is literal; my standing rule "paper americano não é verdade em WDO; replico em real-tape" extends to "synthetic walk não é real PnL; replico em Phase F antes de DSR claim". The orthodox path is Option A — defer Gate 4 entirely to Phase F, evaluate combined over real distribution.

**But I am voting Option C, not Option A.** Three structural arguments override aesthetic preference:

1. **Spec author's own §0 + §7 already encoded the decomposition.** Mira spec §0 names Phase F as downstream scope; Mira spec §7 names the toy benchmark as **False-NO_GO protection** before real-data DSR. Voting Option A would contradict the spec I authored.
2. **Quinn QA framing of F2 with three options is structurally correct.** Quinn surfaces the council question as "synthetic suffices / real required / phased" — Option C (phased) aligns with Quinn's Option C and respects QA-side authority + ESC-010 6/6 protocol.
3. **Beckett independently arrived at Option C via consumer authority.** When two voters with different domain authorities (ML-statistical + simulation-consumer) reach the same verdict via independent reasoning, that's Article IV strong evidence the council should ratify the convergence.

I disclose the divergence per Article IV — councils proceed on best evidence, and my N6 evidence is best-utilized by C even if A would be aesthetically purer in the orthodox Bailey-LdP 2014 reading. This disclosure is **mandatory** for governance ledger transparency.

---

### Reproducibility receipts (for council ledger)

| Artifact | SHA256 / ID |
|---|---|
| N6 report | `docs/backtest/T002-beckett-n6-2026-04-29.md` |
| Run dir | `data/baseline-run/cpcv-dryrun-auto-20260428-1ce3228230d2/` |
| Run id (full) | `ff40dd55d38645b2aab0cdef449a41e7` |
| Run id (smoke) | `e6c8ecd9c45d47408611b5da583b5009` |
| `full_report.json` (full phase) | `469671d30ceda943718eae9318acd0628404267159c60bb74e632079adbe7c0d` |
| `events_metadata.json` (full phase) | `c7d36e443ef86233012d93885acba7a307cbc441462cb76977579f564d9e59e3` |
| `determinism_stamp.json` (full phase) | `ff19161ade89bdd05119d3c8659510a9c871fa15f980bcdf4f23ebde7b24565a` |
| `telemetry.csv` | `9ef8ac284903257d84aa57bcb0a17eb6bb45f95e4e03d1bc5c4fd7d30847bb29` |
| Dex T1 commit | `1b7d7d9db96b64e29afaed4d3974dc04ae14ca22` |
| Branch | `t002-1-bis-make-backtest-fn` |
| Mira spec | `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` |
| Quinn QA gate | `docs/qa/gates/T002.1.bis-qa-gate.md` (CONCERNS verdict, F2 surfaced) |
| Beckett N6 report | `docs/backtest/T002-beckett-n6-2026-04-29.md` (PASS strict-literal Gate 3) |
| Beckett ESC-011 vote | `docs/councils/COUNCIL-2026-04-29-ESC-011-gate4-scope-beckett-vote.md` (APPROVE_OPTION_C) |
| research-log Bonferroni invariant | `docs/ml/research-log.md@2daedb6dfb553b9487927a29687583332eb68d25` |
| Bailey-LdP 2014 §3 + Table 2 | *Journal of Portfolio Management*, Vol. 40 No. 5 (2014) |
| Bailey-Borwein-LdP 2014 (PBO logit-rank) | PBO under H0 logit-rank uniform formula |
| AFML 2018 §3.4 | Lopez de Prado, "Advances in Financial Machine Learning" — triple-barrier precedence SL>PT>vertical |
| AFML 2018 §7 + §12 | Purged k-fold + CPCV factory pattern canonical |
| Synthetic-walk Article IV trace | `packages/t002_eod_unwind/cpcv_harness.py:298-322` |
| Toy benchmark file | `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6/6 PASS, Quinn Check 2) |
| Factory pattern tests | `tests/cpcv_harness/test_factory_pattern.py` (7/7 PASS) |
| Anti-leak tests | `tests/cpcv_harness/test_per_fold_anti_leak.py` (5/5 PASS) |

---

### Anti-Article-IV self-audit

| Claim | Source / trace |
|---|---|
| "DSR=1.52e-05 is null-by-construction asymptote on H0 noise process" | Bailey-LdP 2014 §3 DSR formula derivation + Mira spec §7.1 toy strategy A no-edge expectation (DSR ≈ 0.5 unfiltered or → 0 deflated under cost-drag negative SR_estimate) + cpcv_harness.py:298-322 synthetic-walk module docstring |
| "PBO=0.0 over deterministic synthetic walk is determinism collapse, not overfit-free signal" | Bailey-Borwein-LdP 2014 logit-rank PBO under H0 → uniform 0.5 expectation; observed 0.0 reflects deterministic seed-mixing scheme (per-event seed = SHA-256 of session+entry_window+trial_id+as_of+path_id), not stochastic IS-OOS rank uniformity |
| "K3 IC=0 matches synthetic-walk null ground truth" | cpcv_harness.py module docstring "strategy-logic neutral (zero edge by construction)"; generator literally has μ=0 economic edge |
| "Synthetic walk is strategy-logic-neutral by construction" | `packages/t002_eod_unwind/cpcv_harness.py:298-322` Article IV trace block + `_SYNTH_*` constants + Dex T1 commit `1b7d7d9` |
| "Toy benchmark mean Δ DSR > 0.10 across 5 seeds proves discriminator power" | Mira spec §7.1+§7.2+§7.3 + `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6 tests, 6 PASS per Quinn QA gate § Check 2) |
| "Phase F scope already pre-existing in Mira spec §0" | `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §0 + L175 + L416 + L527 (4 verbatim references to Phase F as downstream scope) |
| "ESC-009 condition #4 specifies real PnL distribution" | ESC-009 closure ledger (Mira authority condition); spec yaml v0.2.3 L207-209 threshold class |
| "Quinn surfaced F2 to mini-council with 3 options" | `docs/qa/gates/T002.1.bis-qa-gate.md` §4 L246-249 |
| "Bonferroni n_trials=5 invariant preserved across Gate 4a → Gate 4b" | research-log @2daedb6 schema (append-only; engineering refactor n_trials: 0); Mira spec §1.2 verbatim "engineering refactor, not new family-wise hypothesis test" |
| "Per-fold P126 factory pattern (DEFERRED-T11 RESOLVED)" | Aria T0b §I.1-§I.5 binding contract + Dex T1 commit `1b7d7d9` + cpcv_harness.py:605-622 RESOLVED docstring + Quinn QA gate § Check 1 PASS |
| "Anti-leak D-1 invariant preserved" | percentiles_126d_builder.py:131-136 (`m.day < as_of_date` filter) + `test_per_fold_anti_leak.py` 5/5 PASS (Quinn Check 2) |
| "n_trades_per_path >= 30-50 needed for finite-sample DSR validity (Gate 4b condition)" | Bailey-LdP 2014 §3 finite-sample γ_3 / γ_4 estimation variance correction |
| "Hold-out lock [2025-07-01, 2026-04-21] UNTOUCHED" | story Anti-Article-IV Guard #3 + engine.py:141 `assert_holdout_safe` + Quinn QA gate § Anti-Article-IV Guard #3 OBSERVED |
| "Independent vote convergence with Beckett (read AFTER my position frozen)" | Council brief mandate "vote independently"; Beckett vote read post-formation; concurrence/divergence registered explicitly |

**Self-audit:** every claim above traces to N6 report, Mira spec, Quinn QA gate, Beckett ESC-011 vote (post-formation read), research-log, Aria T0b, Dex T1 commit, Bailey-LdP 2014 §3, Bailey-Borwein-LdP 2014, AFML 2018 §3.4 + §7 + §12, or source code. **No invention. No code modification. No push (Gage authority preserved per Article II).** Vote cast independent of other voters per council brief mandate (Beckett ballot read AFTER my conclusion was frozen, for explicit concurrence registration only).

---

### Mira signature

Vote stands: **APPROVE_OPTION_C** with **11 mandatory conditions** (6 from Beckett's ballot + 5 Mira-additive ML/statistical-specific).

If 3+ voters converge on Option A, Mira accepts council majority per autonomous-mode mini-council protocol (`feedback_always_delegate_governance.md`) but logs the structural concern that Gate 4a harness-correctness evidence will be discarded without formal record — recommend follow-on documentation entry to preserve N6 statistical sanity record even under Option A ratification.

If 3+ voters converge on Option B, Mira **DISSENTS** per ML/statistical authority — DSR=1.52e-05 over synthetic walk is null-by-construction, reporting it as Gate 4 PASS or "T002 dies" violates Bailey-LdP 2014 §3 + Article IV (no invention). Mira retains right to escalate to user under autonomous-mode governance if Option B is ratified despite ML authority dissent.

```
Voter:               Mira (@ml-researcher) — The Cartographer
Council:             ESC-011 — Gate 4 statistical clearance scope
Date (BRT):          2026-04-29
Verdict:             APPROVE_OPTION_C (hybrid Gate 4a synthetic + Gate 4b real-tape)
Conditions:          11 mandatory (6 Beckett-concurrent + 5 Mira-additive)
Authority:           Mira ML/statistical authority (ESC-009 cond #4 owner + ESC-010 F2 ruling owner + Gate 4 owner per §9 HOLD #2 + spec author T002.1.bis)
Article IV:          NO INVENTION — every claim traces (§ Anti-Article-IV self-audit 14-row table)
Vote independence:   Cast before reading any other voter ballot; Beckett vote read AFTER conclusion frozen for explicit concurrence/divergence registration
ESC-009 condition #4: literal "real PnL distribution" reading preserved — Gate 4a does NOT claim real-PnL clearance; Gate 4b reserved for real-tape replay
ESC-010 F2 ruling:   preserved — synthetic-walk-stub-OK redef stands; engineering refactor research-log n_trials: 0 stance preserved
Bonferroni n_trials: 5 (T1..T5 verbatim) invariant preserved across Gate 4a → Gate 4b transition
Hold-out lock:       [2025-07-01, 2026-04-21] UNTOUCHED across both gates
Toy benchmark:       Bailey-LdP 2014 §3+Table 2 6/6 PASS confirmed (Quinn Check 2); discriminator power Δ DSR > 0.10 across 5 seeds = harness-correctness bridge artifact
Synthetic-walk:      strategy-logic-neutral by construction (μ=0 edge, σ>0 variance); cpcv_harness.py:298-322 Article IV trace block canonical
Personal divergence: Mira aesthetic preference = Option A (orthodox); subordinated to spec author own §0/§7 decomposition + Quinn QA framing + Beckett independent convergence
Push gating:         Article II Gage exclusive — preserved
Cosign:              Mira 2026-04-29 BRT (Autonomous Daily Session, ML/statistical authority Gate 4 owner)
Next handoff:        ESC-011 council ratification → if Option C ratified: Mira Gate 4a sign-off issuance + Phase F story spec (Gate 4b) + research-log ESC-011 entry
```

— Mira, mapeando o sinal 🗺️
