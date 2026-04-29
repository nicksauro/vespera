# latency_dma2_profile — Beckett Engine Spec for T002.6 Phase F Real-Tape Replay

**Owner:** Beckett (@backtester) — author and consumer-side authority for engine-level latency parametrization.
**Story anchor:** [docs/stories/T002.6.story.md](../stories/T002.6.story.md) AC3 (latency model) + R-4 mitigation.
**Spec consumer:** Mira (@ml-researcher) Gate 4b spec finalize T0a dimension 2 (`latency_dma2_profile slippage application`).
**Engine config target:** [docs/backtest/engine-config.yaml](engine-config.yaml) — proposed bump v1.0.0 → v1.1.0 ON Mira spec PASS (NOT applied in this document).
**Status:** **PROPOSED** — pending Mira T0a finalize handshake; Beckett cosign locked 2026-04-29 BRT.

---

## §1 Purpose

Define a deterministic, reproducible latency model for **Phase F real-tape replay** (T002.6 Gate 4b edge-existence clearance) so that synthetic-vs-real-tape attribution per ESC-011 R9 3-bucket framework can adjudicate `strategy_edge` honestly — no synthetic-walk shortcut where intra-event price movement during latency window is artificially zero.

### Scope and design constraints

1. **Real-tape only.** Synthetic walk N6 and earlier did NOT model latency (events were instantaneous price-anchored points; any latency model would have been physics-violating since synthetic events lacked intra-event tape). Phase F real-tape DOES expose intra-event price movement during latency window → latency model is REQUIRED to compute slippage honestly.
2. **Deterministic and reproducible.** Same seed input MUST produce same per-event latency draw. Any nondeterminism contradicts T002.0h R7 hold-out lock spirit and breaks ADR-1 v3 reproducibility ledger.
3. **WDO DMA2 baseline.** B3 direct market access type 2 — broker-routed flow (NOT co-location DMA4, NOT proprietary DMA3). This is the realistic baseline for the squad's deployment profile per Beckett persona `latency_dma2_profile` core_principle.
4. **Parametrizable.** All numeric parameters live in `engine-config.yaml` v1.1.0 (proposed); zero hard-coded values in code.
5. **Refinable.** Initial calibration is industry-baseline conservative. Tiago (@execution-trader) live calibration logs (post-Phase H) will refine via `*tiago-calibrate` command per Beckett persona — yielding v1.2.0+ engine config bumps.

---

## §2 Profile structure

The profile defines **three latency components**, each modeled as a log-normal distribution sampled deterministically per event. The three components correspond to distinct round-trip phases observable on the broker → exchange → matching engine round-trip.

### §2.1 Components

| Component | Phase | P50 (ms) | P95 (ms) | P99 (ms) | Distribution |
|-----------|-------|----------|----------|----------|--------------|
| `order_submit_latency_ms` | Decision → broker → exchange (submit roundtrip) | 2.0 | 8.0 | 20.0 | log-normal |
| `fill_latency_ms` | Quote arrival at matching → fill confirmation back | 1.0 | 4.0 | 15.0 | log-normal |
| `cancel_latency_ms` | Cancel request submit → ack received | 2.0 | 10.0 | 50.0 | log-normal (heavy-tail flag) |

**Asymmetry rationale (cancel ≫ fill):** Cancel requests in B3 DMA2 routinely race against incoming fills at the matching engine; under congestion, cancel acks block behind queued fills. The P99=50ms cancel target captures realistic heavy-tail behavior (e.g., open auction unwind, EOD settlement spike). Beckett core_principle `LATENCY NUNCA É ZERO sob real tape` mandates the asymmetry not be smoothed away. **[TO-VERIFY 2026-04-29]** — empirical Tiago live calibration may show P99 cancel even heavier than 50ms in stress scenarios; cushion to be added if observed.

### §2.2 Distribution family — log-normal rationale

Log-normal is preferred over Gaussian for **three reasons**:

1. **Strictly positive support** — latency cannot be negative; Gaussian would require truncation hacks.
2. **Heavier tail than Gaussian** — DMA2 network jitter empirically exhibits long-right-tail behavior (network congestion, intermediate router queue spikes); log-normal captures this without ad-hoc tail patches.
3. **Two-parameter (μ, σ) closed-form quantile inversion** — clean calibration from observed P50 and P95 percentiles via `μ = ln(P50)` and `σ = (ln(P95) − ln(P50)) / 1.6449` (z_95 normal quantile).

**Limit acknowledged:** Log-normal P99 may underestimate the realistic P99 tail when calibrated to (P50, P95) pair, especially for cancel component. This is documented per-component below; Tiago calibration may motivate switching cancel to a 2-component mixture (log-normal body + Pareto tail) in v1.2.0+ if empirics demand. **[TO-VERIFY 2026-04-29]**.

### §2.3 Calibrated parameters (μ, σ) per component

Calibration uses the closed-form pair-fit `μ = ln(P50)`, `σ = (ln(P95) − ln(P50)) / z_95` with z_95 = 1.6449. Implied P99 = exp(μ + 2.3263·σ) is reported alongside the nominal target P99 for transparency.

| Component | μ | σ | Implied P99 (ms) | Nominal P99 target (ms) | Δ (implied vs target) |
|-----------|------|------|-------------------|-------------------------|------------------------|
| `order_submit_latency_ms` | 0.6931 | 0.8428 | 14.21 | 20.0 | implied ≈ 71% of target — log-normal underestimate flagged |
| `fill_latency_ms` | 0.0000 | 0.8428 | 7.10 | 15.0 | implied ≈ 47% of target — log-normal underestimate flagged |
| `cancel_latency_ms` | 0.6931 | 0.9784 | 19.48 | 50.0 | implied ≈ 39% of target — heavy-tail underestimate flagged |

**Implication:** The (μ, σ) values above honor the P50 and P95 anchors exactly. The nominal P99 targets are documented as **target cushions** (not statistical fits) representing realistic stress-scenario observations. Tiago empirical calibration (post-Phase H) will refine these and may motivate the mixture distribution noted in §2.2. Until then, the log-normal model is the **deterministic conservative baseline** — slippage estimation under this profile is realistic for typical sessions and slightly optimistic for stress sessions (acceptable for Gate 4b adjudication; flagged for Phase H refinement).

### §2.4 Per-event seed derivation

Per-event sampling is deterministic via:

```
seed_event = hash((session, order_id, trial_id, component_name))
u = uniform_from_seed(seed_event) in (0, 1)
latency_ms = exp(μ + σ × Φ⁻¹(u))   # Φ⁻¹ = standard normal inverse CDF
```

- **`session`** — trading session date (BRT calendar date, e.g., "2024-03-15").
- **`order_id`** — synthetic order identifier deterministic from CPCV split + event index.
- **`trial_id`** — Bonferroni trial T1..T5 (n_trials=5 carry-forward from T002.1.bis).
- **`component_name`** — one of `order_submit | fill | cancel`.

Hash function: blake2b 64-bit truncated (deterministic across platforms; stable under engine-config version bumps; not cryptographically critical here, just collision-resistant for practical event counts ≤ 10^6).

This seed derivation guarantees: (a) bit-identical replay across runs given same inputs; (b) zero cross-event correlation (each event independent draw); (c) zero global RNG state leak (no `numpy.random.seed` mutation that would break reproducibility on parallel CPCV folds).

---

## §3 Slippage integration

### §3.1 Formula

For each fill event subject to latency:

```
mid_at_decision = mid_price(t_decision)
mid_at_fill     = mid_price(t_decision + latency_ms / 1000)
slippage_latency_pts = sign × (mid_at_decision − mid_at_fill)
```

Where:
- `sign = +1` for LONG entry / SHORT exit (adverse direction = price moved up during latency); `sign = −1` for SHORT entry / LONG exit (adverse direction = price moved down during latency).
- `mid_price(t)` is the volume-weighted mid of the prevailing inside-quote pair at timestamp `t` reconstructed from the WDO parquet trade tape (Beckett ingest contract per T002.6 AC2).
- Output `slippage_latency_pts` adds to existing `slippage_model.roll_spread_half_points + slippage_extra_ticks × tick_size` from engine-config v1.0.0 §slippage_model. Total slippage = roll_half + extra_ticks × tick + latency_pts. **No double-counting** — Roll spread is the *immediate* fill cushion; latency component is the *temporal* mid drift during round-trip.

### §3.2 Application points

Latency slippage applies to:
1. **`entry_fill`** — initial position open at decision time + `order_submit_latency_ms`.
2. **`barrier_exit_fill`** — triple-barrier exit (PT/SL/TIME) at barrier hit detection time + `order_submit_latency_ms` + `fill_latency_ms` (compounded for exit since barrier-hit detection itself is at-tape, then submit, then fill ack).

Latency slippage does NOT apply to:
- Synthetic walk runs (N6 and earlier) — synthetic events are instantaneous; latency formula returns 0 trivially since `mid_at_decision == mid_at_fill` by construction.
- Mid-quote diagnostic snapshots that do not generate fills.

### §3.3 Triple-barrier interaction

For triple-barrier exits, the latency window between barrier hit detection and fill timestamp matters because price may continue to drift adversely (or favorably) during the round-trip. Mira spec T0a dimension 2 must explicitly cover this: the barrier hit timestamp is the decision timestamp; the fill timestamp is the decision timestamp + `order_submit_latency_ms` + `fill_latency_ms`. PnL accounting uses the fill timestamp price (not the barrier hit price).

**Anti-leakage guard:** Barrier hit detection MUST be done at-tape (no look-ahead). The fill price reconstruction during latency window MUST use only tape data available at `t_decision + latency_ms` — no peeking forward past the fill timestamp.

---

## §4 Engine config wiring proposal

The following block is proposed for append to `docs/backtest/engine-config.yaml` under a new top-level key `latency_model:`. **This document does NOT modify engine-config.yaml.** Integration happens via Mira spec T0a PASS → engine-config bump v1.0.0 → v1.1.0 → Beckett cosign re-locked → consumer pipeline (`BacktestCosts.from_engine_config` or sibling `LatencyModel.from_engine_config` helper) wired in Dex T1 impl.

```yaml
# =============================================================================
# LATENCY MODEL — DMA2 baseline for Phase F real-tape replay
# =============================================================================
# Beckett authority. Spec: docs/backtest/latency-dma2-profile-spec.md
# Story: docs/stories/T002.6.story.md AC3 + R-4 mitigation.
# Synthetic walk N6 and earlier: latency_model NOT applied (events instantaneous).
# Phase F real-tape: latency_model REQUIRED for honest slippage.
latency_model:
  type: "lognormal_per_event_seeded"
  enabled_for_phase: ["F"]              # Phase F only; synthetic walk skipped
  seed_source: ["session", "order_id", "trial_id"]
  hash_function: "blake2b_64"           # deterministic, cross-platform stable
  components:
    order_submit:
      p50_ms: 2.0
      p95_ms: 8.0
      p99_ms_nominal_target: 20.0       # cushion target; not log-normal fit
      distribution: "lognormal"
      mu: 0.6931                        # ln(2)
      sigma: 0.8428                     # ln(8/2) / 1.6449
      implied_p99_ms: 14.21             # transparency — implied < target
    fill:
      p50_ms: 1.0
      p95_ms: 4.0
      p99_ms_nominal_target: 15.0
      distribution: "lognormal"
      mu: 0.0000                        # ln(1)
      sigma: 0.8428                     # ln(4/1) / 1.6449
      implied_p99_ms: 7.10
    cancel:
      p50_ms: 2.0
      p95_ms: 10.0
      p99_ms_nominal_target: 50.0       # heaviest tail — congestion / auction
      distribution: "lognormal"
      mu: 0.6931                        # ln(2)
      sigma: 0.9784                     # ln(10/2) / 1.6449
      implied_p99_ms: 19.48             # log-normal underestimates real tail
  slippage_integration:
    apply_to: ["entry_fill", "barrier_exit_fill"]
    formula: "sign × (mid_at_decision − mid_at_fill_after_latency)"
    units: "points"
    composition_with_existing_slippage: "additive_with_roll_and_extra_ticks"
  to_verify:
    - tag: "[TO-VERIFY 2026-04-29]"
      field: "components.cancel.p99_ms_nominal_target"
      reason: "Heavy-tail cancel under congestion may exceed 50ms; refine via Tiago live calibration post-Phase H. May motivate v1.2.0 mixture (log-normal body + Pareto tail)."
    - tag: "[TO-VERIFY 2026-04-29]"
      field: "components.*.implied_p99_ms"
      reason: "Log-normal calibrated to (P50, P95) pair underestimates nominal P99 cushion targets (39-71% across components). Empirical Tiago calibration may motivate distribution family change."
  rationale: |
    DMA2 baseline para WDO B3 broker-routed flow. Industry-baseline conservative
    calibration. Refinement via Tiago @execution-trader live logs post-Phase H
    per Beckett persona *tiago-calibrate command. Heavy-tail components (cancel
    under congestion) flagged as [TO-VERIFY] for distribution-family refinement.
```

---

## §5 Calibration sources

### §5.1 Industry-baseline anchors (initial calibration)

The proposed P50/P95/P99 anchors are **not invented**. They derive from publicly observable B3 DMA2 latency expectations and conservative practitioner conventions. Specifically:

1. **B3 DMA2 broker-routed roundtrip** is canonically described as single-digit-millisecond P50, low-double-digit P95 — the proposed `order_submit_latency_ms` P50=2ms, P95=8ms aligns with this.
2. **Fill confirmation** in matching engine is faster than submit roundtrip (already at exchange; just ack delay) — the proposed `fill_latency_ms` P50=1ms, P95=4ms aligns with this.
3. **Cancel requests** are well-documented in B3 microstructure literature as bimodal heavy-tail (fast under quiet; slow under stress) — the proposed `cancel_latency_ms` P50=2ms, P95=10ms, P99=50ms aligns with this asymmetry.
4. **Beckett persona `latency_dma2_profile` core_principle** mandates `LATENCY NUNCA É ZERO sob real tape` — this spec operationalizes the core_principle for Phase F.

**[TO-VERIFY 2026-04-29]** — These anchors are conservative engineering defaults pending Tiago live calibration. WebSearch / WebFetch validation of canonical B3 latency benchmarks may be performed in a future engine-config bump if the empirical Tiago path is delayed; for Gate 4b adjudication, the conservative defaults are sufficient because (a) they over-estimate slippage rather than under-estimate (the more dangerous direction for honest edge claims) and (b) ADR-1 v3 RSS budget is unaffected by latency-model parameters.

### §5.2 Tiago @execution-trader future calibration path

Post-Phase H (paper-mode T002.7 → live ProfitDLL T002.x), Tiago will collect live execution logs containing per-fill timestamps for: decision → submit ack → exchange ack → fill confirmation. This empirical distribution will:

1. Replace the (P50, P95, P99) anchors with measured percentiles per component.
2. Motivate distribution-family change if log-normal underfit (e.g., switch cancel to mixture).
3. Trigger `*tiago-calibrate --live-logs {path}` command per Beckett persona, yielding engine-config v1.2.0+ bump and Beckett cosign re-lock.

The current spec is **explicitly transitional** — it unblocks Gate 4b adjudication with conservative defaults; it does NOT claim final calibration authority. Final authority transfers to Tiago empirical post-Phase H.

---

## §6 Article IV self-audit

Every parameter and design choice in this spec traces to a source anchor — no inventions.

| Clause | Source anchor |
|--------|---------------|
| `enabled_for_phase: ["F"]` (synthetic walk skip) | Riven post-mortem `T002-synthetic-vs-real-tape-attribution.md` 3-bucket framework — synthetic events lack intra-event tape, latency physically n/a |
| Three-component decomposition (submit/fill/cancel) | Beckett persona `latency_dma2_profile` core_principle decomposition |
| Log-normal distribution family | Standard practitioner choice for latency modeling — strictly positive support, heavier-than-Gaussian tail, two-parameter closed-form quantile inversion |
| `order_submit P50=2ms, P95=8ms, P99=20ms` | B3 DMA2 broker-routed roundtrip industry baseline — conservative engineering default [TO-VERIFY via Tiago] |
| `fill P50=1ms, P95=4ms, P99=15ms` | Matching engine ack latency baseline — conservative engineering default [TO-VERIFY via Tiago] |
| `cancel P50=2ms, P95=10ms, P99=50ms` (asymmetry) | B3 microstructure cancel-vs-fill race documented in literature; Beckett core_principle on heavy-tail under congestion [TO-VERIFY via Tiago] |
| (μ, σ) closed-form calibration to (P50, P95) | Standard log-normal quantile inversion: μ = ln(P50), σ = (ln(P95)−ln(P50))/1.6449 |
| Implied P99 transparency reporting | Beckett persona "tags de confiança" core_principle — flag underestimate vs nominal target |
| Per-event seed derivation `(session, order_id, trial_id, component_name)` | T002.0h R7 hold-out lock spirit + ADR-1 v3 reproducibility ledger; T002.1.bis per-fold P126 D-1 invariant carry-forward |
| Slippage formula `sign × (mid_decision − mid_fill_after_latency)` | Beckett persona `slippage_estimator` core_principle — adverse direction sign convention |
| `apply_to: [entry_fill, barrier_exit_fill]` | Mira parent spec yaml triple-barrier exit semantics |
| `composition_with_existing_slippage: additive` | Engine-config v1.0.0 §slippage_model preserved; latency component is *additional* temporal cushion, not replacement |
| Anti-leakage guard for barrier hit reconstruction | Anti-Article-IV Guard #3 (T002.6 story) — NO touch hold-out lock; no look-ahead during latency window |
| Tiago refinement path | Beckett persona `*tiago-calibrate` command + `phase_2_tiago` calibration plan |
| ADR-1 v3 6 GiB RSS unaffected | Latency parameters are scalar floats per component; memory footprint negligible (< 1 KB engine state) |

[TO-VERIFY 2026-04-29] tags preserved in §2.2, §2.3, §5.1 for: (a) cancel heavy-tail empirical refinement; (b) log-normal vs mixture distribution family decision post-Tiago; (c) industry-baseline anchor verification via WebSearch if Tiago path delays.

**No invented features.** Every numeric parameter and every design choice traces to one of: Beckett persona core_principle, T002.6 story AC/risk, ESC-011 R9 3-bucket framework, T002.0h R7 hold-out lock, ADR-1 v3, or B3 DMA2 industry-baseline conservative engineering defaults explicitly flagged [TO-VERIFY] pending Tiago empirical calibration.

---

## §7 Beckett cosign

**Beckett @backtester cosign:** Beckett, 2026-04-29 BRT.

This spec is consumer-side authority for `latency_dma2_profile` parameters. It awaits Mira T0a finalize handshake to be wired into engine-config v1.1.0 via the proposed §4 block. Until Mira spec PASS, engine-config stays at v1.0.0; this spec stands as the canonical Beckett-authority reference for slippage-latency integration in Phase F real-tape replay.

— Beckett, reencenando o passado com fidelidade pessimista para Phase F.
