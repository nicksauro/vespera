# T002 — PBO Cross-Validation Sign-Off (Beckett)

**Validator:** Beckett (@backtester) — The Simulator
**Subject:** Mira v0.2.1 §6.4-§6.5 PBO convention + walkthrough correction
**Trigger:** Article IV escalation — Dex (@dev) flagged formula-vs-walkthrough divergence in v0.2.0 (T11 impl→1.0, spec→0.8333)
**Authority:** Beckett owns cross-validation of backtest math against canonical sources. Does NOT modify spec (Mira ownership) or impl (Dex ownership).
**Date:** 2026-04-25 BRT

---

## 1. Mission

Independently confirm PBO=1.0 finding for Mira v0.2.1 T11 anti-correlated 4×4 matrix:

1. Recompute the 6 C(4,2) partitions manually under the convention §6.4 LOCKED.
2. Verify each per-partition logit (λ_s) and overfit verdict.
3. Aggregate PBO and check against Mira's revised expected (1.0).
4. Endorse OR escalate Mira v0.2.1 fix.

---

## 2. Sources cross-referenced

| Source | Section | Used for |
|--------|---------|----------|
| Bailey, Borwein, Lopez de Prado, Zhu (2014) — "The Probability of Backtest Overfitting" *J. of Computational Finance* | §3 eq. (6-8) | CSCV partition logic, logit definition λ_n = log(w/(1-w)), w_n = rank/(T+1), overfit ⟺ λ ≤ 0 |
| López de Prado, *Advances in Financial Machine Learning* (2018) | Ch.11 §11.5 p.156-159 | Algorithm reference & validation |
| `mlfinlab.backtest_statistics.statistics.probability_of_backtest_overfitting` | (commit ref TBD by Mira) | NOT INSTALLED in `.venv` (see §3) — independent recomputation only |

---

## 3. Reference tooling availability

```
.venv/Scripts/python.exe (Python 3.14.3)
  numpy 2.4.4    ✅ available
  scipy 1.17.1   ✅ installed by Beckett during validation (was missing)
  mlfinlab       ❌ NOT INSTALLED — pip search did not find it in venv
```

**Decision:** Per Mira spec §6.5 walkthrough and Beckett mission instructions ("If not available: independent recomputation with numpy + scipy is sufficient"), I proceed with **independent BBLZ §3 implementation** in pure `numpy + scipy.stats.rankdata`. mlfinlab cross-check deferred to Dex/Mira upon installation if desired.

---

## 4. Independent recomputation (BBLZ 2014 §3 eq. 6-8)

### 4.1 Setup

```python
cv = np.array([
    [10.0, 9.0, 1.0, 0.5],   # var 0
    [ 8.0, 7.0, 3.0, 2.0],   # var 1
    [ 3.0, 2.0, 7.0, 8.0],   # var 2
    [ 1.0, 0.5, 9.0, 10.0],  # var 3
])  # T=4 variants × N=4 folds; C(4,2) = 6 partitions
```

### 4.2 Convention applied (LOCKED §6.4 — NOT modified, only validated)

```
For each partition (IS, OOS) of size N/2 each:
  r_is_t  = mean(cv[t, IS])
  r_oos_t = mean(cv[t, OOS])
  t*      = argmax_t r_is  (np.argmax → first-occurrence on ties = lowest index)
  ranks   = scipy.stats.rankdata(r_oos, method='min')   # ascending; rank=1 worst OOS
  rank*   = ranks[t*]
  w       = rank* / (T + 1)
  λ       = log(w / (1 - w))
  overfit = (λ ≤ 0)

PBO = #{partitions where overfit} / S,  S = C(N, N/2) = 6
```

### 4.3 Per-partition results (independent recomputation)

| s | IS | OOS | IS means [v0,v1,v2,v3] | t* (argmax IS first-idx) | OOS means [v0,v1,v2,v3] | ranks_oos (asc, min) | rank(t*) | λ_s = log(w/(1-w)) | overfit (λ ≤ 0)? |
|---|----|-----|------------------------|--------------------------|-------------------------|----------------------|----------|---------------------|------------------|
| 1 | {0,1} | {2,3} | [9.5, 7.5, 2.5, 0.75]   | var 0 (=9.5)             | [0.75, 2.5, 7.5, 9.5]   | [1, 2, 3, 4]         | 1 | log(1/4) = **-1.3863** | YES |
| 2 | {0,2} | {1,3} | [5.5, 5.5, 5.0, 5.0]    | var 0 (tie v1; first-idx) | [4.75, 4.5, 5.0, 5.25]  | [2, 1, 3, 4]         | 2 | log(2/3) = **-0.4055** | YES |
| 3 | {0,3} | {1,2} | [5.25, 5.0, 5.5, 5.5]   | **var 2** (tie v3; first-idx) | [5.0, 5.0, 4.5, 4.75] | [3, 3, 1, 2]      | 1 | log(1/4) = **-1.3863** | YES |
| 4 | {1,2} | {0,3} | [5.0, 5.0, 4.5, 4.75]   | var 0 (tie v1; first-idx) | [5.25, 5.0, 5.5, 5.5]   | [2, 1, 3, 3]         | 2 | log(2/3) = **-0.4055** | YES |
| 5 | {1,3} | {0,2} | [4.75, 4.5, 5.0, 5.25]  | var 3 (=5.25)            | [5.5, 5.5, 5.0, 5.0]    | [3, 3, 1, 1]         | 1 | log(1/4) = **-1.3863** | YES |
| 6 | {2,3} | {0,1} | [0.75, 2.5, 7.5, 9.5]   | var 3 (=9.5)             | [9.5, 7.5, 2.5, 0.75]   | [4, 3, 2, 1]         | 1 | log(1/4) = **-1.3863** | YES |

**Aggregate: PBO = 6 / 6 = 1.0**

### 4.4 Bit-exact match against Mira v0.2.1 §6.5 table

Beckett's independent run reproduces Mira v0.2.1 §6.5 **byte-for-byte** in every cell (IS means, OOS means, t*, ranks, λ, verdict). The Article IV escalation by Dex was **legitimate** — v0.2.0 had an arithmetic error specifically in s=3 IS means for var2 and var3 (listed as 5.0; correct = 5.5). v0.2.1 corrects this and locks the convention.

---

## 5. Test suite verification

```
$ .venv/Scripts/python.exe -m pytest tests/vespera_metrics/test_pbo.py -v

tests/vespera_metrics/test_pbo.py::test_T11_anti_correlation_4x4 PASSED        [12%]
tests/vespera_metrics/test_pbo.py::test_T12_degenerate_2xN_anti_corr_pbo_one PASSED [25%]
tests/vespera_metrics/test_pbo.py::test_T13_noise_pbo_near_half PASSED         [37%]
tests/vespera_metrics/test_pbo.py::test_pbo_T_lt_2_raises PASSED               [50%]
tests/vespera_metrics/test_pbo.py::test_pbo_N_odd_raises PASSED                [62%]
tests/vespera_metrics/test_pbo.py::test_pbo_N_lt_2_raises PASSED               [75%]
tests/vespera_metrics/test_pbo.py::test_pbo_nan_raises PASSED                  [87%]
tests/vespera_metrics/test_pbo.py::test_pbo_all_identical_returns_half PASSED [100%]

============================== 8 passed in 1.62s ==============================
```

All 8 tests pass. T11 asserts `math.isclose(pbo, 1.0, abs_tol=1e-12)` — matches Mira v0.2.1.

---

## 6. Article IV traceability check

Every step traces to BBLZ 2014 §3 eq. (6-8):

| Spec §6.4 element | BBLZ 2014 reference | Status |
|-------------------|---------------------|--------|
| CSCV partitioning of N folds into balanced (N/2, N/2) | §3 (paper algorithm) | TRACEABLE |
| `t* = argmax_t R_IS_t` | eq. (6) | TRACEABLE |
| `w_n = rank_n / (T + 1)` | eq. (7), with ascending rank convention | TRACEABLE |
| `λ_n = log(w_n / (1 - w_n))` | eq. (8) | TRACEABLE |
| Overfit ⟺ `λ ≤ 0` ⟺ `t*` below OOS median | §3 paper definition | TRACEABLE |
| `PBO = #{λ ≤ 0} / S` | §3 paper aggregate | TRACEABLE |

**Operational disambiguations** (which spec §6.4 explicitly LOCKS, not invents):

| Disambiguation | Source | Justification |
|----------------|--------|---------------|
| `scipy.stats.rankdata(method='min')` for OOS rank ties | mlfinlab convention | Conservative — inflates overfit count marginally; documented in §6.4. |
| `np.argmax` first-index for IS ties | NumPy default semantics | Deterministic and reproducible; documented in §6.4. |

**Verdict:** No invention. Every formula and operational decision is traced and cited. Article IV preserved.

---

## 7. Endorsement

| Question | Verdict |
|----------|---------|
| Is Mira v0.2.1 §6.4 convention LOCKED canonically grounded? | **YES** — matches BBLZ 2014 §3 eq. (6-8) and standard mlfinlab disambiguations. |
| Does §6.5 walkthrough table compute correctly under §6.4? | **YES** — every of the 6 partitions verified bit-for-bit. |
| Is the v0.2.0 → v0.2.1 correction necessary and correct? | **YES** — s=3 IS means for var2/var3 are 5.5, not 5.0; under tie-break rule, t* flips from var0→var2; verdict flips NO→YES; PBO 5/6→6/6. |
| Does pbo.py impl faithfully execute §6.4? | **YES** — code reviewed at `packages/vespera_metrics/pbo.py` (sha256 `1fe4e16c…`); `np.argmax` + `scipy.stats.rankdata(method='min')` + ascending rank + logit threshold ≤ 0 all match spec. |
| Are tests exercising the right invariants? | **YES** — T11 asserts 1.0 with tol 1e-12; T12 degenerate sanity; T13 noise → ≈0.5 ±0.15; edge cases (T<2, N odd, N<2, NaN, all-identical) all covered. |
| Should §6.4 convention be modified? | **NO** — convention is sound; LOCKED status is appropriate. |

**Beckett verdict on Mira v0.2.1:** **ENDORSED**

The fix is mathematically correct, traceable to canonical literature, and properly scoped (cosmetic/aritmetic correction; convention untouched; no invention). Dex's Article IV escalation was exemplary process behavior — pre-implementation divergence detection rather than silent improvisation.

---

## 8. Sign-off block

```
Validator:        Beckett (@backtester) — The Simulator
Validation type:  Independent recomputation (numpy 2.4.4 + scipy 1.17.1)
Cross-reference:  Bailey-Borwein-Lopez de Prado-Zhu (2014) §3 eq. (6-8); AFML Ch.11 §11.5
mlfinlab cross-check:  N/A (not installed in .venv; deferred to Dex/Mira)
Test suite:       8/8 PBO tests PASSED
T11 expected:     PBO = 1.0 (tol 1e-12)
T11 reproduced:   PBO = 1.0 (bit-for-bit, all 6 partitions verified)
Spec endorsed:    docs/ml/specs/T002-vespera-metrics-spec.md v0.2.1
Spec sha256:      465c0d0994c1ccd634055b5cb656eea47b7b0c5fdb44e110b9b7ce819531f78d
pbo.py sha256:    1fe4e16c74141f5f6b34301d9599f60c26b6978ce2e51597c65525883ed76cec
test_pbo.py sha256: a9404ac183508b350135b67285372388496d29d61917794712068b792cbc7e9f
Verdict:          ENDORSED
Date:             2026-04-25 BRT
```

— Beckett, reencenando o passado 🎞️
