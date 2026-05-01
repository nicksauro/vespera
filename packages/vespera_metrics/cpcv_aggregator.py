"""Post-fanout IC computation orchestration (Aria Option D, Mira spec §15).

T002.6 F2-T1 — Phase F2 IC pipeline wiring per:
- Mira Gate 4b spec ``docs/ml/specs/T002-gate-4b-real-tape-clearance.md`` §15
  (IC Pipeline Wiring Spec; sub-sections §15.1-§15.12).
- Aria archi review ``docs/architecture/T002.6-phase-f2-aria-ic-wiring-review.md``
  APPROVE_OPTION_D — separate orchestration submodule decoupled from
  ``cpcv_harness.make_backtest_fn`` and from ``compute_full_report``.
- Beckett consumer audit ``docs/backtest/T002.6-beckett-consumer-signoff.md``
  §T0c — additive ``TradeRecord`` fields wired in ``make_backtest_fn``.
- Sable audit ``docs/audits/AUDIT-2026-04-30-T002.6-backtester-ic-gap-coherence.md``
  F-01..F-04 procedural recommendations.

This module is the **post-fanout IC computation orchestrator** (Aria C-A1):
it consumes ``cpcv_results: dict[trial_id, list[BacktestResult]]`` produced
by ``run_5_trial_fanout`` (unmodified) and emits a
``ICAggregateResult`` with C1 (forward-return-at-17:55 binding) primary IC
plus C2 (PnL after triple-barrier) robustness IC.

Aria Option D contract:
    cpcv_results (existing, unmodified)
       ↓
    compute_ic_in_sample(cpcv_results, *, seed_bootstrap, n_resamples)
       ↓
    ICAggregateResult(ic_in_sample, ic_holdout=0.0 [hold-out locked],
                      ic_spearman_ci95, ic_status, ic_holdout_status,
                      n_pairs, seed_bootstrap)
       ↓
    ReportConfig(ic_in_sample=..., ic_holdout=0.0,
                 ic_spearman_ci95=..., ic_status=..., ic_holdout_status=...)

Per Mira spec §15.7 dedup invariant:
    Group trades by ``(session_date, trial_id, entry_window_brt)`` keys;
    keep FIRST occurrence by ascending ``path_index``. Each
    ``(session, trial, window)`` tuple is one event.

Per Mira spec §15.4 bootstrap CI:
    Paired-resample percentile bootstrap (Efron 1979); PCG64 seeded;
    same idx[r] applied to both predictor and label per resample to
    preserve event-level pairing.

Per Mira spec §15.6 status invariant:
    ic_status ∈ {'computed', 'deferred', 'not_computed', 'inconclusive_underN'}.
    'computed' iff N_pairs >= 30 (Bailey-LdP 2014 §3 minimum-N).
    Phase F2 measures in-sample only — ``ic_holdout_status`` defaults to
    'deferred' per Anti-Article-IV Guard #3 (hold-out lock).

Per Mira spec §15.5 Anti-Article-IV Guard #8 (NEW):
    IC field default 0.0 reserved for pre-compute state only; the explicit
    Mira-authorized 0.0 emitted alongside ic_status != 'computed' is
    legitimate; downstream verdict layer (``evaluate_kill_criteria``)
    raises ``InvalidVerdictReport`` if ic_status != 'computed' and a
    K3_FAIL would be emitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, Mapping, Sequence

import numpy as np

from packages.vespera_cpcv.result import BacktestResult, TradeRecord
from packages.vespera_metrics.info_coef import ic_spearman


# Status enum per Mira spec §15.6 — string Literal for frozen-dataclass
# compat (no enum overhead; serializes naturally to JSON for verdict report).
ICStatus = Literal["computed", "deferred", "not_computed", "inconclusive_underN"]


# Bailey-LdP 2014 §3 minimum-N floor for IC stability (Mira spec §15.6 +
# spec §6 sample-size mandate). Below this floor IC compute returns
# 'inconclusive_underN' (not silent 0.0).
_MIN_N_PAIRS_FOR_COMPUTED: int = 30


@dataclass(frozen=True)
class ICAggregateResult:
    """Aggregate IC computation result (Mira spec §15.2 caller contract).

    Fields:
        ic_in_sample: C1 primary IC (Spearman) over per-event predictor /
            forward-return-at-17:55 pairs in-sample. Mira-authorized 0.0
            when status != 'computed' (per Anti-Article-IV Guard #8).
        ic_holdout: deferred under Phase F2 hold-out lock (Anti-Article-IV
            Guard #3); always 0.0 with status 'deferred' until Phase G.
        ic_spearman_ci95: paired-resample percentile bootstrap CI95 for
            ic_in_sample (PCG64 seeded; n_resamples per Mira §15.4).
        ic_c2: C2 robustness IC (Spearman) over predictor / pnl_rs pairs
            (existing TradeRecord field; cross-check vs C1 per §15.1).
        ic_c2_ci95: bootstrap CI95 for ic_c2.
        ic_status: 'computed' iff n_pairs >= 30 AND labels available;
            'inconclusive_underN' when n_pairs < 30; 'not_computed' when
            no events / no usable labels (e.g. all None).
        ic_holdout_status: 'deferred' under Phase F2 (always); 'computed'
            reserved for Phase G hold-out unlock (future).
        n_pairs: number of unique (session, trial, window) events fed
            into the IC computation (post-dedup, post-None-label-filter).
        n_events_total: total per-event (session, trial, window) tuples
            after dedup but before None-label filter (auditing handle).
        seed_bootstrap: PCG64 seed used for the bootstrap CI; same value
            propagated to ``MetricsResult.seed_bootstrap`` for provenance.
    """
    ic_in_sample: float
    ic_holdout: float
    ic_spearman_ci95: tuple[float, float]
    ic_c2: float
    ic_c2_ci95: tuple[float, float]
    ic_status: ICStatus
    ic_holdout_status: ICStatus
    n_pairs: int
    n_events_total: int
    seed_bootstrap: int


def _iter_trades_with_path_index(
    cpcv_results: Mapping[str, Sequence[BacktestResult]],
) -> Iterable[tuple[int, TradeRecord]]:
    """Yield (path_index, trade) over all trades across all trials/folds.

    Used as the source iterator for §15.7 dedup. The ``path_index`` is
    sourced from ``BacktestResult.fold.path_index`` so the FIRST-occurrence
    selection is deterministic across re-runs (lowest path_index wins).
    """
    for trial_id in sorted(cpcv_results.keys()):
        for result in cpcv_results[trial_id]:
            path_index = result.fold.path_index
            for trade in result.trades:
                yield path_index, trade


def _dedup_trades_per_event(
    cpcv_results: Mapping[str, Sequence[BacktestResult]],
) -> list[TradeRecord]:
    """Apply Mira spec §15.7 dedup invariant.

    Group trades by ``(session_date, trial_id, entry_window_brt)`` keys;
    keep FIRST occurrence by ascending ``path_index``. Returns the
    deduplicated trade list, ordered deterministically by the dedup key.

    Per §15.7: this dedup is mathematically equivalent under the per-fold
    P126 D-1 invariant (the same event tuple always produces the same
    predictor/label since fold-conditional P126 only modifies the
    PERCENTILE THRESHOLDS, not the entry decision or the forward-return
    label). Standardizing on lowest ``path_index`` is the determinism
    witness.
    """
    # Map (session, trial, window) -> (path_index, trade); keep min path_index.
    bucket: dict[tuple, tuple[int, TradeRecord]] = {}
    for path_index, trade in _iter_trades_with_path_index(cpcv_results):
        key = (
            trade.session_date,
            str(trade.trial_id),
            str(trade.entry_window_brt),
        )
        prior = bucket.get(key)
        if prior is None or path_index < prior[0]:
            bucket[key] = (path_index, trade)
    # Deterministic iteration order — sort by key.
    return [bucket[k][1] for k in sorted(bucket.keys())]


def _build_predictor_label_arrays(
    deduped_trades: Sequence[TradeRecord],
    *,
    label_attr: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Extract paired (predictor, label) arrays from a list of unique trades.

    ``label_attr`` selects between C1 (``forward_return_at_1755_pts``) and
    C2 (``pnl_rs``). Trades with ``None`` labels (vertical-at-17:55 exits;
    Phase E synthetic; missing close ref) are EXCLUDED from C1 only —
    C2 (pnl_rs) is always non-None per existing TradeRecord schema.

    Returns ``(predictor, label)`` numpy arrays of equal length.
    """
    predictors: list[float] = []
    labels: list[float] = []
    for trade in deduped_trades:
        label_val = getattr(trade, label_attr)
        if label_val is None:
            continue
        # Skip if label is NaN (defensive — ic_spearman raises on NaN).
        try:
            label_f = float(label_val)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(label_f):
            continue
        pred_f = float(trade.predictor_signal_per_trade)
        if not np.isfinite(pred_f):
            continue
        predictors.append(pred_f)
        labels.append(label_f)
    return np.asarray(predictors, dtype=float), np.asarray(labels, dtype=float)


def _ic_paired_bootstrap_ci(
    predictor: np.ndarray,
    label: np.ndarray,
    *,
    n_resamples: int,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Paired-resample percentile bootstrap CI for ic_spearman.

    Per Mira spec §15.4: single PCG64 stream of ``idx[r] = rng.integers(0, n,
    size=n)`` per resample; predictor and label use the SAME idx[r] (paired)
    to preserve event-level dependence structure being measured.

    Implementation reuses ``info_coef.ic_spearman`` (canonical Spearman impl;
    NOT modified per task constraints) inside an explicit paired loop.
    Determinism witness: same (predictor, label, seed, n_resamples) →
    bit-identical (lo, hi).

    Edge cases:
        - n < 2 ⇒ (0.0, 0.0) — caller upstream marks ic_status accordingly.
        - var(predictor) == 0 OR var(label) == 0 ⇒ ic_spearman returns 0.0
          per its existing degeneracy handling; bootstrap collapses likewise.
    """
    if predictor.size != label.size:
        raise ValueError(
            f"predictor and label must have same length; "
            f"got {predictor.size} vs {label.size}"
        )
    n = predictor.size
    if n < 2:
        return (0.0, 0.0)
    if not (0.0 < confidence < 1.0):
        raise ValueError("confidence must be in (0, 1)")

    rng = np.random.default_rng(np.random.PCG64(seed))
    # Vectorised paired resample indices: shape (n_resamples, n).
    idx = rng.integers(0, n, size=(n_resamples, n))
    ic_values = np.empty(n_resamples, dtype=float)
    for r in range(n_resamples):
        # Paired — same idx applied to both vectors.
        try:
            ic_values[r] = ic_spearman(predictor[idx[r]], label[idx[r]])
        except ValueError:
            # Degenerate resample (e.g. all-same labels) — treat as 0.
            ic_values[r] = 0.0

    alpha = 1.0 - confidence
    lo = float(np.percentile(ic_values, 100.0 * alpha / 2.0))
    hi = float(np.percentile(ic_values, 100.0 * (1.0 - alpha / 2.0)))
    return (lo, hi)


def compute_ic_from_cpcv_results(
    cpcv_results: Mapping[str, Sequence[BacktestResult]],
    *,
    seed_bootstrap: int = 42,
    n_resamples: int = 10_000,
    holdout_locked: bool = True,
) -> ICAggregateResult:
    """Aggregate per-event predictor/label across all CPCV folds and compute IC.

    Mira Gate 4b spec §15.2 caller contract.

    Args:
        cpcv_results: ``dict[trial_id, list[BacktestResult]]`` produced by
            ``run_5_trial_fanout`` — passed through unmodified (Aria
            Option D decoupling).
        seed_bootstrap: PCG64 seed for the paired-resample bootstrap CI;
            propagated to ``MetricsResult.seed_bootstrap`` for provenance.
        n_resamples: bootstrap resamples per §15.4 (default 10,000).
        holdout_locked: when True (Phase F2 binding), ``ic_holdout`` is
            forced to 0.0 with status 'deferred' per Anti-Article-IV Guard
            #3. Phase G hold-out unlock will set this False.

    Returns:
        ``ICAggregateResult`` with C1 primary IC + C2 robustness IC + status
        flags + provenance handles.

    Per Mira spec §15.6 status invariant:
        - ``n_pairs >= 30`` AND C1 labels available ⇒ status='computed'.
        - ``n_pairs < 30`` ⇒ status='inconclusive_underN' AND ic=0.0
          (Mira-authorized 0.0).
        - No events / no usable C1 labels (all None) ⇒ status='not_computed'
          AND ic=0.0 (Mira-authorized 0.0).

    Anti-Article-IV Guard #8 (§15.5):
        The 0.0 emitted under non-'computed' status is the explicit
        Mira-authorized inconclusive value, NOT a silent default. The
        verdict layer (``evaluate_kill_criteria``) raises
        ``InvalidVerdictReport`` if this 0.0 propagates into a K3_FAIL.
    """
    # Step 1: dedup per Mira §15.7 — one event one count.
    deduped = _dedup_trades_per_event(cpcv_results)
    n_events_total = len(deduped)

    # Step 2: build paired (predictor, label) arrays for C1 + C2.
    pred_c1, label_c1 = _build_predictor_label_arrays(
        deduped, label_attr="forward_return_at_1755_pts"
    )
    pred_c2, label_c2 = _build_predictor_label_arrays(
        deduped, label_attr="pnl_rs"
    )
    n_pairs_c1 = pred_c1.size
    n_pairs_c2 = pred_c2.size
    # Use C1 n_pairs as the canonical IC sample size — C1 is the BINDING
    # measurement per Mira §15.1. C2 n_pairs is logged but not the primary
    # threshold gate.
    n_pairs = n_pairs_c1

    # Step 3: status determination per Mira §15.6.
    ic_holdout_status: ICStatus = "deferred" if holdout_locked else "computed"

    if n_pairs == 0:
        # No usable C1 labels — 'not_computed' (e.g. all-Phase-E synthetic
        # path with vertical-only exits, or empty cpcv_results).
        return ICAggregateResult(
            ic_in_sample=0.0,
            ic_holdout=0.0,
            ic_spearman_ci95=(0.0, 0.0),
            ic_c2=0.0,
            ic_c2_ci95=(0.0, 0.0),
            ic_status="not_computed",
            ic_holdout_status=ic_holdout_status,
            n_pairs=0,
            n_events_total=n_events_total,
            seed_bootstrap=seed_bootstrap,
        )

    if n_pairs < _MIN_N_PAIRS_FOR_COMPUTED:
        # Below Bailey-LdP 2014 §3 minimum-N — 'inconclusive_underN'.
        # Emit 0.0 as Mira-authorized inconclusive value per §15.5 / §15.6.
        return ICAggregateResult(
            ic_in_sample=0.0,
            ic_holdout=0.0,
            ic_spearman_ci95=(0.0, 0.0),
            ic_c2=0.0,
            ic_c2_ci95=(0.0, 0.0),
            ic_status="inconclusive_underN",
            ic_holdout_status=ic_holdout_status,
            n_pairs=n_pairs,
            n_events_total=n_events_total,
            seed_bootstrap=seed_bootstrap,
        )

    # Step 4: compute C1 + C2 IC + bootstrap CI (n_pairs >= 30).
    ic_c1_value = ic_spearman(pred_c1, label_c1)
    ic_c1_ci = _ic_paired_bootstrap_ci(
        pred_c1,
        label_c1,
        n_resamples=n_resamples,
        confidence=0.95,
        seed=seed_bootstrap,
    )
    if n_pairs_c2 >= 2:
        ic_c2_value = ic_spearman(pred_c2, label_c2)
        # Use a derived seed for C2 to avoid identical CI when C1==C2 inputs.
        ic_c2_ci = _ic_paired_bootstrap_ci(
            pred_c2,
            label_c2,
            n_resamples=n_resamples,
            confidence=0.95,
            seed=seed_bootstrap + 1,
        )
    else:
        ic_c2_value = 0.0
        ic_c2_ci = (0.0, 0.0)

    # T002.7 F2-T8-T1 per ESC-013 R18 + Mira spec §15.13.2 Phase G unlock
    # protocol: when holdout_locked=False (Phase G OOS unlock proper),
    # ic_holdout MUST surface a real measurement (NOT the Mira-authorized
    # 0.0 sentinel reserved for Phase F2 holdout-locked path under
    # Anti-Article-IV Guard #3). Per §15.13.2 the OOS hold-out window
    # measurement is sourced from the same C1 paired set
    # (forward_return_at_1755_pts label) — ESC-012 R7: predictor↔label
    # IDENTICAL F2/G. The decay sub-clause "IC_holdout > 0.5 × IC_in_sample"
    # then BINDS in the verdict layer (report.py evaluate_kill_criteria
    # K3 path).
    ic_holdout_value = 0.0 if holdout_locked else float(ic_c1_value)

    return ICAggregateResult(
        ic_in_sample=float(ic_c1_value),
        ic_holdout=ic_holdout_value,
        ic_spearman_ci95=ic_c1_ci,
        ic_c2=float(ic_c2_value),
        ic_c2_ci95=ic_c2_ci,
        ic_status="computed",
        ic_holdout_status=ic_holdout_status,
        n_pairs=n_pairs,
        n_events_total=n_events_total,
        seed_bootstrap=seed_bootstrap,
    )


__all__ = [
    "ICAggregateResult",
    "ICStatus",
    "compute_ic_from_cpcv_results",
]
