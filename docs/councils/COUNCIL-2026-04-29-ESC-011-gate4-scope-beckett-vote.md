## Beckett voto ESC-011 — 2026-04-29 BRT

> **Voter:** Beckett (@backtester) — The Simulator
> **Authority:** Backtest consumer + simulation realism + N6 evidence holder (sole empirical anchor)
> **Provenance:** N6 report `docs/backtest/T002-beckett-n6-2026-04-29.md` §11 caveat (Beckett-surfaced)
> **Vote independence:** Cast before reading any other voter ballot
> **No push:** Article II preserved (Gage exclusive)

### Verdict: APPROVE_OPTION_C

(Hybrid — Gate 4a synthetic clearance via T002.1.bis N6 + Gate 4b real-tape clearance via Phase F)

---

### Consumer authority reasoning

**On Option A (strict — real tape required, T002.1.bis closes Gate 2 only):**

Operationally tempting from the consumer purity stance — "no real PnL distribution, no statistical clearance" is the orthodox reading of ESC-009 condition #4. But it conflates two things the N6 evidence has **demonstrably separated**: (1) **harness-correctness** (does the strategy logic, cost wiring, factory pattern, per-fold P126 rebuild, Bonferroni preservation, anti-leak D-1 invariant, KillDecision verdict mechanics, sha256 reproducibility — all execute end-to-end?) and (2) **edge-existence** (does the WDO end-of-day fade strategy actually have positive economic IC against real tape?). The N6 distribution (σ=0.192, 222/225 unique values, K1 DSR measurably positive 1.52e-05 ≠ default 0.5, K2 PBO measurably 0.0 ≠ default 0.5, K3 IC=0 with strategy-logic-neutral synthetic walk by construction) is a **clean harness-correctness signal**. Forcing both to clear in a single Gate 4 verdict over real tape only delays the Gate 2 disarm without adding statistical information about the harness — and risks Phase F runs catching a *combined* failure (harness bug **or** real-edge absence) where root-cause attribution becomes harder. Beckett rejects Option A as **unnecessarily monolithic**.

**On Option B (lenient — synthetic walk DSR sufficient with caveat, N6 DSR=1.52e-05 → T002 dies):**

This option commits the inverse error: it would have me declare T002 economically dead based on a distribution that is **strategy-logic-neutral by construction**. From `cpcv_harness.py` `_SYNTH_*` constants (open=R$5000, daily_vol=25 points, bars=32, ticks=8) + per-event seed = SHA-256 of `(session, entry_window, trial_id, p126.as_of_date, split.path_id)` — the walk is a deterministic noise process. Zero economic edge is the **expected null**, not a measurement. Reporting DSR=1.52e-05 → "T002 dies" violates Article IV (no invention) at the interpretation layer: the empirical statement is "harness produces non-degenerate distribution with expected null edge over noise process", **not** "WDO end-of-day fade has 1.52e-05 deflated Sharpe". Beckett rejects Option B as **statistical malpractice via false-NO_GO**.

**On Option C (hybrid — Gate 4a synthetic + Gate 4b real tape):**

This is the **honest decomposition**. Gate 4a (synthetic) = harness-correctness clearance (DSR/PBO/IC mechanics work, distribution non-degenerate, K1/K2/K3 axes alive, toy benchmark Bailey-LdP 2014 §3+Table 2 demonstrates discriminator power mean Δ DSR > 0.10 across 5 seeds — separates edge from no-edge). Gate 4b (real tape, Phase F scope) = edge-existence clearance over real WDO end-of-day distribution (DSR > 0.95 ± 0.05 + PBO < 0.25 ± 0.05 + IC decay per Mira spec §7 + spec yaml v0.2.3 L207-209). T002.1.bis closes Gate 4a; Phase F closes Gate 4b. §9 HOLD #2 disarm chain is **explicit** about which gate disarms which barrier. Capital-ramp protocol RA-XXXXXXXX-X (Riven Gate 5) cannot fire without Gate 4b, so the real-tape requirement does NOT vanish — it just gets its own ledger entry instead of being conflated with harness-correctness.

**Why C is operationally superior for me as consumer:**
- N6 evidence is fully utilized (10 PASS / 1 CONCERN / 1 CAVEAT = 10/12 strict-literal; harness-correctness signal is unambiguously good)
- Phase F scope is **already explicit in Mira spec §0** and **already deferred** in T002.1.bis ACs — Option C just names what is already true in the spec
- Toy benchmark (Bailey-LdP 2014 §3+Table 2) is the **bridge artifact**: synthetic strategy A (no-edge DSR≈0.5) and synthetic strategy B (small-edge DSR>0.95) prove the harness *can* discriminate edge from no-edge → real-tape DSR > 0.95 will mean something when it lands
- Forward-visibility: Phase F failure modes are isolated (real-tape data quality, slippage realism, latency calibration, RLP policy, rollover transitions) and won't be mistaken for harness bugs
- Reproducibility ledger: Gate 4a artifact = N6 (run_id `ff40dd55d38645b2aab0cdef449a41e7`, 9 sha256-stamped artifacts, σ=0.192250); Gate 4b artifact = Phase F future N7+ (real-tape replay, distinct run_id, distinct dataset_sha256)

---

### Empirical anchor

| Dimension | N5 stub baseline | N6 (this council's anchor) | Comparison |
|---|---|---|---|
| `sharpe_std` | 0.0 (degenerate identity-zero) | **0.192250** | ∞ ratio improvement; non-degenerate proven |
| Unique sharpe values / 225 | 1 (all zero) | **222** (98.7%) | distribution actually exists |
| K1 DSR | 0.5 (default — never computed) | **1.5201186062197763e-05** | measured ≠ default |
| K2 PBO | 0.5 (default — never computed) | **0.0** (no overfit signal) | measured ≠ default |
| K3 IC | 0.0 default | **0.0 measured** (CI95 [0,0]) | matches synthetic-walk null expectation |
| KillDecision verdict | NO_GO (stub-degenerate F2 redef) | **NO_GO** (K3 reason `IC_in_sample=0.000000 non-positive — no edge`) | semantically meaningful, not stub artifact |
| Wall-time | ~21 s | 27.4 s | comparable, no regression |
| Peak RSS | 0.024 GiB Python | 0.158 GiB Python / 0.597 GiB OS-WS | comparable, well under 6 GiB cap |
| Bonferroni n_trials=5 | preserved | **preserved** (events_metadata.trials = ['T1'..'T5']) | invariant honored |
| Anti-leak D-1 invariant | preserved (warmup gate fail blocked it) | **preserved** (per-fold P126 factory pattern, 5 anti-leak tests + 7 factory tests + 6 toy tests in tree per Dex T1 commit `1b7d7d9`) | strengthened |

**Critical empirical claim:** N6 demonstrates **harness-correctness (Gate 4a) cleanly**, with the synthetic walk being the *deliberate isolation mechanism* (Mira spec §7 toy benchmark methodology). The N6 distribution carries the signal "harness alive" — it does NOT carry the signal "WDO strategy edge exists" because **the synthetic walk has no edge by construction**. Conflating these two signals is the failure mode Option C explicitly avoids.

**On DSR=1.52e-05 — does this say anything meaningful about real edge?**

**No.** And this is not a hedge — it is a structural truth. The synthetic walk:
- Open price = R$5000.0 (constant, not real WDO open)
- Daily vol = 25.0 points (constant, not real WDO ATR_hora)
- 32 × 15-min bars (synthetic OHLC structure)
- 8 ticks per bar (synthetic intra-bar walk)
- Per-event seed mixes session + entry_window + trial_id + p126.as_of + path_id → deterministic noise

The strategy logic (T1..T5 entry rule, triple-barrier with SL>PT>vertical precedence per AFML 2018 §3.4, P60/P20/P80 magnitude/ATR filter resolution, cost atlas wiring with R$1.23 exchange + Roll+1tick slippage + IR DARF post-hoc) executes **over this noise**. The expected DSR over noise is ≈ 0 (positive but trivially small, exactly as observed at 1.52e-05). This is the **Bailey-LdP 2014 §3+Table 2 toy strategy A pattern**: edge-neutral noise process produces DSR≈0.5 unfiltered or DSR ≈ 0 after deflation by the harness mechanics. The N6 measurement is **consistent with the null hypothesis "synthetic walk has no edge"** — which is **what we want at this stage** to prove harness mechanics work without contamination from real-tape signal.

Saying "DSR=1.52e-05 → T002 dies" is equivalent to saying "the noise process has no edge → therefore the WDO strategy has no edge". Non-sequitur. The strategy edge can only be measured against real WDO tape — that's Gate 4b (Phase F).

---

### Personal preference vs council vote

**Personal preference (Beckett-internal, before consumer authority constraints):** Option A (strict). My pessimistic-by-default temperament leans toward "no real tape, no statistical statement". I prefer to defer Gate 4 entirely until Phase F runs, then evaluate the combined Gate 4 over real PnL — cleaner provenance, no risk of operationally conflating "harness PASS" with "edge exists" in downstream readers.

**But I am voting Option C (hybrid), not Option A.** My personal preference is **subordinated to two structural findings**:

1. **Quinn QA gate (T002.1.bis-qa-gate.md §4) explicitly surfaces F2 to mini-council** with three options — Quinn's Option A maps to my Option B (synthetic suffices), Quinn's Option B maps to my Option A (real tape required), Quinn's Option C maps to my Option C (phased). Quinn's framing of F2 as a **MEDIUM severity** caveat with toy-benchmark discriminator power as the evidentiary bridge — this is structurally sound. The toy benchmark's mean Δ DSR > 0.10 across 5 seeds is the **harness-discriminator-power proof** that justifies treating Gate 4a as a real signal.

2. **Mira spec §0 already names Phase F as downstream scope** — it is *not invented* by this council; it is *pre-existing* in the canonical spec. Option C is therefore the **minimum-disruption path** that respects the spec author's authority while still using N6 evidence to clear what it can clear.

The honest delta between my personal preference (A) and my vote (C):
- A would force a single monolithic Gate 4 over real tape only — clean but operationally costly (delays §9 HOLD #2 Gate 2 + Gate 3 disarm by N7 cycle)
- C accepts the *philosophical* compromise of two-gate Gate 4 in exchange for the *empirical* clarity of harness vs edge separation

I disclose this divergence per Article IV — councils proceed on best evidence, and my N6 evidence is best-utilized by C even if A would be aesthetically purer.

---

### Conditions on Option C (mandatory if council adopts)

If ESC-011 ratifies Option C, Beckett conditions the vote on the following — non-negotiable for consumer-side acceptance:

1. **Gate 4a verdict text MUST carry verbatim caveat:** "Harness-correctness clearance over synthetic deterministic walk per Mira spec §7 toy benchmark methodology. Edge-existence clearance pending Gate 4b real-tape replay (Phase F scope). DSR=1.52e-05 is the noise-floor null measurement, NOT an economic statement about WDO end-of-day fade strategy edge." This caveat must appear in: (a) Mira Gate 4a sign-off artifact, (b) Riven §9 HOLD #2 Gate 2 + Gate 3 disarm ledger, (c) any downstream story or epic that consumes Gate 4a as input.

2. **Gate 4a CANNOT pre-disarm Gate 5 (capital ramp).** §9 HOLD #2 Gate 5 (Riven dual-sign for capital ramp protocol RA-XXXXXXXX-X) MUST require Gate 4b (real-tape) PASS as upstream pre-condition. No Gate 5 firing on Gate 4a alone.

3. **Phase F story scope must include Beckett N7+ real-tape replay** with: (a) WDO parquet tape consumption replacing `_walk_session_path` / `_walk_to_exit` synthetic walks, (b) preserved factory pattern + per-fold P126 rebuild + Bonferroni n_trials=5, (c) cost atlas wiring identical to N6, (d) latency_dma2_profile applied to slippage estimation per Beckett engine spec, (e) RLP policy + rollover calendar consumption per Nova authority, (f) re-run Bailey-LdP 2014 toy benchmark on real-tape harness to confirm discriminator power preserved.

4. **N6 housekeeping concerns C1-C3 must be resolved before Phase F:** C1 `cost_atlas_sha256: null` stamp persistence gap (atlas v1.0.0 source-imported per Dex commit body but not stamped — surface for next-run hardening); C2 `simulator_version` stamp string stale (`cpcv-dry-run-T002.0f-T3` while branch is T002.1.bis post-T1); C3 `determinism_stamp.spec_version = "0.2.0"` vs `full_report.metrics.spec_version = "T002-v0.2.3"` (two-source-of-truth on version string). NICE-TO-HAVE for Gate 4a; BLOCKING for Gate 4b reproducibility.

5. **Toy benchmark gate before Gate 4a verdict:** Quinn QA must confirm `tests/cpcv_harness/test_toy_benchmark_bailey_lopez_de_prado_2014.py` (6 tests per Dex T1 commit body) executed green with mean Δ DSR > 0.10 across 5 seeds. This is the structural evidentiary bridge that justifies treating synthetic-walk DSR/PBO as harness-correctness signals rather than just "we ran something".

6. **Article IV trace for Gate 4a verdict:** every clause in Mira Gate 4a sign-off must trace to (a) N6 report `docs/backtest/T002-beckett-n6-2026-04-29.md` §-anchor, (b) Mira spec §-anchor, (c) ESC-009 condition #4 + ESC-010 F2 ruling + ESC-011 ratification entry. No invention.

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
| Seed | 42 |
| Python / NumPy / Pandas | 3.14.3 / 2.4.2 / 2.3.3 |
| Bonferroni n_trials | 5 (T1..T5 verbatim) |
| n_trials_source | `docs/ml/research-log.md@2daedb6dfb553b9487927a29687583332eb68d25` |

---

### Anti-Article-IV self-audit

| Claim | Source / trace |
|---|---|
| "synthetic walk strategy-logic-neutral by construction" | `packages/t002_eod_unwind/cpcv_harness.py` module docstring §`_SYNTH_*` constants + Dex T1 commit body |
| "DSR=1.52e-05 is noise-floor null" | N6 §6 K1 row (DSR = 1.5201186062197763e-05) + cross-reference Bailey-LdP 2014 §3 Table 2 strategy A no-edge expectation |
| "σ(sharpe)=0.192250 vs N5 σ=0" | N6 §6 sharpe_std + N5 stub baseline (`docs/backtest/T002-beckett-t11-bis-smoke-report-N5-2026-04-28.md`) |
| "Phase F scope already in spec §0" | Mira spec `docs/ml/specs/T002.1.bis-make-backtest-fn-spec.md` §0 + L175 + L416 + L527 |
| "Quinn surfaced F2 to mini-council with 3 options" | `docs/qa/gates/T002.1.bis-qa-gate.md` §4 L246-249 |
| "Toy benchmark mean Δ DSR > 0.10 across 5 seeds" | Mira spec §7 + Quinn gate §4 description of discriminator power; runtime green confirmation = Quinn pre-condition #5 above |
| "Gate 5 must require Gate 4b" | `docs/councils/USER-ESCALATION-QUEUE.md` ESC-010 status block (5 disarm gates pending) + Mira spec L175+L416 (sizing scope deferred to Riven Gate 5) |
| "C1-C3 housekeeping concerns" | N6 §9 verbatim |
| "Bonferroni n_trials=5 preserved" | N6 §10 + events_metadata.json `trials = ['T1','T2','T3','T4','T5']` |
| "Per-fold P126 factory pattern (DEFERRED-T11 RESOLVED)" | N6 §10 + Aria T0b §I.1-§I.5 binding contract + Dex T1 commit `1b7d7d9` |

**Self-audit:** every claim above traces to N6 report, Mira spec, Quinn QA gate, ESC-010 council ledger, Aria T0b review, or Dex T1 commit. No invention. No code modification. No push (Gage authority preserved per Article II). Vote cast independent of other voters per council brief mandate.

---

### Beckett signature

Vote stands: **APPROVE_OPTION_C** with 6 mandatory conditions (above).

If 3+ voters converge on Option A or Option B, Beckett accepts council majority per autonomous-mode mini-council protocol (`feedback_always_delegate_governance.md`) but logs personal divergence above for governance ledger.

— Beckett, reencenando o passado 🎞️
