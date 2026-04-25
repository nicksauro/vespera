# T002 — `vespera_metrics` Module Specification (AC0 Gate)

**Owner:** Mira (@ml-researcher) — fórmulas + toy benchmarks + bibliografia
**Implementation owner:** Dex (@dev) — `packages/vespera_metrics/`
**Consumers:** Beckett (@backtester) — `compute_full_report` em `T002-cpcv-report.md`; Kira (@quant-researcher) — kill criteria K1/K2/K3
**Story:** [T002.0d — Metrics Module](../../stories/T002.0d.story.md) (AC0 gate)
**Spec parent:** [T002 v0.2.0](T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml) §metrics_required L159-172
**Authority:** Article IV (No Invention) — toda fórmula traceável a paper canônico citado.
**Created:** 2026-04-25 BRT
**Mira-signature:** PENDING

---

## 0. Como Dex deve usar este documento

1. Cada métrica abaixo tem: assinatura de função (entrada/saída), fórmula matemática, referência bibliográfica com página, **toy input + expected output** (números fechados que Dex roda em pytest).
2. **Tolerância padrão:** `1e-6` para float reduções (DSR, IC, Sharpe, Sortino, MAR, Ulcer); `1e-10` para identidades algébricas (bootstrap CI degenerate); **exata** (tolerância 0) para PBO toy 2×4.
3. Dex implementa o módulo, roda os testes, compara com os "Expected" desta spec. Se diverge, levanta para Mira ANTES de marcar AC verde.
4. Beckett cross-valida cada toy benchmark contra o paper original e assina sign-off na story T002.0d.

---

## 1. `MetricsResult` — schema do output integrado

### 1.1 Dataclass canônica

```python
# packages/vespera_metrics/report.py

from dataclasses import dataclass, field
from typing import Optional
import numpy as np

@dataclass(frozen=True)
class MetricsResult:
    # ---- Primary (spec L160-163) ----
    ic_spearman: float                       # média do IC sobre os 45 paths CPCV
    ic_spearman_ci95: tuple[float, float]    # bootstrap 10k 95% CI
    dsr: float                               # Deflated Sharpe Ratio (Bailey-LdP 2014)
    pbo: float                               # Probability of Backtest Overfitting (BBLZ 2014)

    # ---- Secondary (spec L164-172) ----
    sharpe_per_path: np.ndarray              # shape (45,), Sharpe anualizado por path
    sharpe_mean: float
    sharpe_median: float
    sharpe_std: float
    sortino: float                           # mediana sobre 45 paths
    mar: float                               # mediana sobre 45 paths
    ulcer_index: float                       # mediana sobre 45 paths
    max_drawdown: float                      # mediana sobre 45 paths (valor negativo)
    profit_factor: float                     # mediana
    hit_rate: float                          # mediana

    # ---- Provenance (auditoria, traceability) ----
    n_paths: int                             # 45 para CPCV(N=10, k=2)
    n_trials_used: int                       # source-of-truth de docs/ml/research-log.md (AC12.1)
    n_trials_source: str                     # "docs/ml/research-log.md@<git-sha>"
    seed_bootstrap: int                      # PCG64 seed
    spec_version: str                        # "T002-v0.2.0"
    computed_at_brt: str                     # ISO timestamp BRT
```

### 1.2 `FullReport` (super-set incluindo kill decision)

```python
@dataclass(frozen=True)
class FullReport:
    metrics: MetricsResult
    per_path_results: list  # list[BacktestResult] (T002.0c handshake)
    kill_decision: "KillDecision"  # GO/NO_GO + reason

    def to_markdown(self) -> str: ...
```

### 1.3 `KillDecision`

```python
@dataclass(frozen=True)
class KillDecision:
    verdict: str                # "GO" | "NO_GO"
    reasons: list[str]          # razões individuais ["K1: DSR=0.42 < 0", ...]
    k1_dsr_passed: bool         # DSR > 0
    k2_pbo_passed: bool         # PBO < 0.4
    k3_ic_decay_passed: bool    # IC_holdout >= 0.5 × IC_in_sample (avaliado em Fase E final)
```

---

## 2. Métrica 1 — Information Coefficient (Spearman)

### 2.1 Assinatura

```python
# packages/vespera_metrics/info_coef.py
def ic_spearman(predictions: np.ndarray, labels: np.ndarray) -> float: ...
```

### 2.2 Fórmula

`IC = ρ_Spearman(predictions, labels)` = correlação de Pearson dos ranks.

**Referência:** Lopez de Prado, *AFML* (2018) Ch.8 §8.4.1 p. 121; Hyndman-Athanasopoulos *Forecasting* (3rd ed) §3.4.

### 2.3 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `len(predictions) < 2` | `raise ValueError("IC undefined for n < 2")` |
| `np.std(predictions) == 0` ou `np.std(labels) == 0` | `return 0.0` (rank correlation degenerate, NÃO `nan`) |
| Predições com NaN | `raise ValueError("NaN in predictions/labels — clean upstream")` |
| Predições e labels com tamanhos diferentes | `raise ValueError` |

### 2.4 Toy benchmarks

**T1 (perfect rank, AC5):**
```
predictions = [1, 2, 3, 4, 5]
labels      = [1.1, 1.9, 3.2, 3.8, 5.5]
expected    = 1.0   (ranks idênticos)
tolerância  = 0     (exato)
```

**T2 (anti-correlation):**
```
predictions = [1, 2, 3, 4, 5]
labels      = [5, 4, 3, 2, 1]
expected    = -1.0
tolerância  = 0
```

**T3 (tied ranks):**
```
predictions = [1, 1, 2, 2, 3]
labels      = [10, 20, 30, 40, 50]
expected    ≈ 0.9486832980505138   (scipy.stats.spearmanr reference)
tolerância  = 1e-12
```

**T4 (zero variance):**
```
predictions = [3, 3, 3, 3, 3]
labels      = [1, 2, 3, 4, 5]
expected    = 0.0
tolerância  = 0
```

---

## 3. Métrica 2 — Bootstrap CI for IC

### 3.1 Assinatura

```python
def bootstrap_ci(
    sample: np.ndarray,
    statistic: callable = np.mean,
    n_resamples: int = 10_000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]: ...
```

### 3.2 Fórmula

Percentil bootstrap (Efron 1979): resample `sample` com reposição `n_resamples` vezes; aplica `statistic` em cada resample; retorna percentis `(α/2, 1-α/2)` da distribuição.

**Referência:** Efron, B. (1979) *Ann. Statist.* 7(1):1-26; AFML Ch.5 não-explicitamente mas é prática padrão.

### 3.3 Determinismo

- Usa `np.random.default_rng(seed)` (PCG64).
- Mesmo `seed` + mesmo `sample` → mesmo CI byte-a-byte (AC11 da story).

### 3.4 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `len(sample) < 2` | `raise ValueError` |
| `np.var(sample) == 0` | retorna `(sample[0], sample[0])` exato |
| `confidence ∉ (0, 1)` | `raise ValueError` |

### 3.5 Toy benchmarks

**T5 (zero variance, AC6):**
```
sample      = [0.1] * 1000
expected    = (0.1, 0.1)
tolerância  = 1e-10
```

**T6 (normal sample, sanity check):**
```
sample      = np.random.default_rng(0).normal(0, 1, size=1000)
seed        = 42
n_resamples = 10000
confidence  = 0.95
expected    ≈ (-0.0815, 0.0431)   # CI da média; valores são reference da execução determinística
tolerância  = 1e-4    (Dex computa com mesmo seed e bate)
```

> Beckett: cross-valide T6 rodando standalone com `numpy 1.26` ou `2.0` — discrepância entre versões é ACEITÁVEL desde que documentada na story; se Dex usar versão diferente, atualizar reference value.

---

## 4. Métrica 3 — Sharpe Ratio (e distribuição sobre paths)

### 4.1 Assinatura

```python
# packages/vespera_metrics/sharpe.py
def sharpe_ratio(returns: np.ndarray, freq: str = "daily", rf: float = 0.0) -> float: ...

def sharpe_distribution(paths_returns: list[np.ndarray]) -> np.ndarray: ...
# returns shape (len(paths_returns),)
```

### 4.2 Fórmula

```
SR = (mean(returns) - rf) / std(returns, ddof=1)   [non-annualized]
SR_annual = SR × sqrt(periods_per_year)
```

`periods_per_year`: `daily=252, hourly=252*8, minute=252*8*60`.

**Referência:** Sharpe, W.F. (1966) *J. of Business*; AFML Ch.14 §14.2.

### 4.3 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `len(returns) < 2` | `raise ValueError` |
| `np.std(returns, ddof=1) == 0` E `mean > rf` | `return float("inf")` |
| `np.std == 0` E `mean == rf` | `return 0.0` (não NaN) |
| `np.std == 0` E `mean < rf` | `return float("-inf")` |
| `freq` desconhecido | `raise ValueError` |

### 4.4 Toy benchmarks

**T7 (constant positive returns, AC7 part 1):**
```
returns       = [0.01] * 252
freq          = "daily"
expected      = float("inf")    # std=0, mean=0.01 > 0
tolerância    = exato (math.isinf)
```

**T8 (alternating, AC7 part 2):**
```
returns       = [0.01, -0.005] * 126   # length 252
freq          = "daily"
mean          = 0.0025
std (ddof=1)  = sqrt( ((0.01-0.0025)² + (-0.005-0.0025)²) × 126 / 251 )
              ≈ 0.007514...
SR_daily      = 0.0025 / 0.007514 ≈ 0.33270
SR_annual     = 0.33270 × sqrt(252) ≈ 5.281
expected      ≈ 5.281
tolerância    = 1e-3
```

> Dex: compute exato com `numpy.std(returns, ddof=1) * np.sqrt(252)` e compare; valor preciso pode variar 1e-4 dependendo de ordem de operações.

---

## 5. Métrica 4 — Deflated Sharpe Ratio (DSR)

### 5.1 Assinatura

```python
# packages/vespera_metrics/dsr.py
def deflated_sharpe_ratio(
    sr_observed: float,
    sr_distribution: np.ndarray,       # SRs dos N trials independentes
    n_trials: int,
    skew: float = 0.0,
    kurt: float = 3.0,
    sample_length: int = 252,
) -> float: ...
```

### 5.2 Fórmula

**Bailey & Lopez de Prado 2014** "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality" *J. of Portfolio Management* 40(5):94-107.

```
SR_0 = sqrt(Var(SR_dist)) × ( (1 - γ) × Φ⁻¹(1 - 1/N) + γ × Φ⁻¹(1 - 1/(N·e)) )
```
onde:
- `Var(SR_dist)` = variância dos SRs dos N trials
- `γ` ≈ 0.5772 (Euler-Mascheroni)
- `Φ⁻¹` = inversa da CDF normal padrão
- `e` = base do log natural
- `N = n_trials`

```
DSR = Φ( ( SR_observed - SR_0 ) × sqrt(T - 1) /
         sqrt( 1 - skew × SR_observed + ((kurt - 1)/4) × SR_observed² ) )
```
onde `T = sample_length` (número de períodos) e `Φ` = CDF normal padrão.

**Interpretação:** DSR ∈ [0, 1] = probabilidade de que o Sharpe observado seja > SR_0 (threshold de seleção).

### 5.3 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `n_trials <= 1` | `raise ValueError("DSR requires N ≥ 2 trials")` |
| `Var(sr_distribution) == 0` | `SR_0 = 0` por convenção; warn no log de Mira |
| `1 - skew·SR + ((kurt-1)/4)·SR² <= 0` | `raise ValueError` (denominador degenerate) |
| `kurt < 1` | `raise ValueError` (kurtosis física é ≥ 1) |
| `sample_length < 2` | `raise ValueError` |

### 5.4 Toy benchmark (AC3)

**T9 (Bailey-LdP 2014 Table 1 reproducible toy):**

Usar exemplo público cross-validado contra `hudson-and-thames/mlfinlab` `mlfinlab.backtest_statistics.statistics.deflated_sharpe_ratio`:

```
sr_observed       = 2.5         # observed annualized Sharpe
sr_distribution   = np.array([0.5, 0.7, 1.0, 1.3, 1.5, 1.8, 2.0, 2.3, 2.5, 2.8])  # 10 trials
n_trials          = 10
skew              = -0.5        # negative skew typical em equity
kurt              = 4.5         # excess kurtosis 1.5
sample_length     = 252         # 1 ano daily

# computações intermediárias (Dex deve reproduzir):
var_sr            = np.var(sr_distribution, ddof=1)         ≈ 0.6022
sigma_sr          = sqrt(var_sr)                            ≈ 0.7760
gamma             = 0.5772
phi_inv_1         = scipy.stats.norm.ppf(1 - 1/10)          ≈ 1.2816
phi_inv_2         = scipy.stats.norm.ppf(1 - 1/(10*e))      ≈ 1.7506
SR_0              = 0.7760 × ((1-0.5772)×1.2816 + 0.5772×1.7506)
                  ≈ 0.7760 × (0.5418 + 1.0107)
                  ≈ 0.7760 × 1.5525
                  ≈ 1.2047

denom_inside      = 1 - (-0.5)×2.5 + (4.5-1)/4 × 2.5²
                  = 1 + 1.25 + 0.875 × 6.25
                  = 1 + 1.25 + 5.4688
                  = 7.7188
denom             = sqrt(7.7188) ≈ 2.7783

z                 = (2.5 - 1.2047) × sqrt(251) / 2.7783
                  = 1.2953 × 15.8430 / 2.7783
                  ≈ 7.385

DSR               = scipy.stats.norm.cdf(7.385)  ≈ 1.0  (saturação numérica em float64)

expected          ≈ 1.0
tolerância        = 1e-6   (acima do threshold 0.95 do paper)
```

**T10 (DSR negativo — kill criterion):**

```
sr_observed       = 0.3
sr_distribution   = np.array([0.4, 0.5, 0.6, 0.5, 0.7, 0.4, 0.5, 0.6, 0.4, 0.5])
n_trials          = 10
skew              = 0.0
kurt              = 3.0
sample_length     = 252

# var_sr ≈ 0.0098 → sigma ≈ 0.099
# SR_0 ≈ 0.099 × 1.5525 ≈ 0.1537   (threshold)
# z ≈ (0.3 - 0.1537) × sqrt(251) / sqrt(1 - 0 + 0.5×0.09) ≈ 0.1463 × 15.84 / 1.0227 ≈ 2.266
# DSR ≈ scipy.stats.norm.cdf(2.266) ≈ 0.9883
expected          ≈ 0.9883
tolerância        = 1e-3
```

> **Beckett:** cross-valide T9 contra `mlfinlab.backtest_statistics.statistics.deflated_sharpe_ratio` (commit ref para reproducibility). T10 é caso limítrofe (DSR alto mas próximo do threshold) — útil para Dex pegar bug em sinal.
>
> **Mira anti-invenção note:** as fórmulas exatas de SR_0 com a constante γ (Euler-Mascheroni) seguem Bailey-LdP 2014 eq. (10) — Dex DEVE citar a equação no docstring da função.

---

## 6. Métrica 5 — Probability of Backtest Overfitting (PBO)

### 6.1 Assinatura

```python
# packages/vespera_metrics/pbo.py
def probability_backtest_overfitting(
    cv_results_matrix: np.ndarray,  # shape (T, N) — T variantes × N folds CPCV
    statistic: callable = np.mean,  # default: Sharpe-like → use SR
) -> float: ...
```

### 6.2 Fórmula

**Bailey, Borwein, Lopez de Prado, Zhu (2014)** "The Probability of Backtest Overfitting" *J. of Computational Finance*; AFML Ch.11 §11.5 p. 156-159.

Algoritmo CSCV (Combinatorially Symmetric Cross-Validation):

1. Particionar `N` folds em pares disjuntos `J_s = (J_s^IS, J_s^OOS)` para todas as `S = C(N, N/2)` combinações balanceadas.
2. Para cada `J_s`:
   - Computar `R_t^IS = statistic(cv_results_matrix[t, J_s^IS])` para cada variante t.
   - Selecionar `t* = argmax_t R_t^IS`.
   - Calcular rank de `t*` em `R_t^OOS = statistic(cv_results_matrix[t, J_s^OOS])`.
   - `λ_s = log( rank(t*, OOS) / (T + 1 - rank(t*, OOS)) )` (logit do rank relativo).
3. `PBO = P(λ_s ≤ 0) = Σ_s 𝟙[λ_s ≤ 0] / S`

**Interpretação:** PBO = probabilidade de que a melhor estratégia in-sample tenha rank OOS abaixo da mediana.

### 6.3 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `T < 2` | `raise ValueError("PBO requires ≥ 2 strategy variants")` |
| `N < 2` ou `N` ímpar | `raise ValueError` (CSCV requer N par para pares balanceados) |
| Todas variantes idênticas | `PBO = 0.5` por convenção (rank empatado) |
| Variante com NaN | `raise ValueError` |

### 6.4 Convenção de rank (LOCKED — Mira-decision)

A convenção segue **Bailey, Borwein, Lopez de Prado, Zhu (2014) §3 eq. (6-8)** com a desambiguação operacional usada por `mlfinlab.backtest_statistics.statistics.probability_of_backtest_overfitting`:

```
rank_n = posição em ordem ASCENDENTE de R_OOS_t*
         (rank=1 → t* foi o PIOR variante OOS; rank=T → t* foi o MELHOR variante OOS).

w_n    = rank_n / (T + 1)
λ_n    = log( w_n / (1 - w_n) )

OVERFITTING ⟺  λ_n ≤ 0  ⟺  rank_n ≤ (T+1)/2  ⟺  t* ficou abaixo da mediana OOS.
```

**Tie-breaking:** `scipy.stats.rankdata(method='min')` — empates recebem o menor rank disponível (decisão conservadora; infla a contagem de overfitting marginalmente; importa ≤ 1% em toy benchmarks). Dex DEVE citar esta decisão no docstring de `pbo.py`.

**Argmax IS tie-breaking:** se duas ou mais variantes empatam em `R_t^IS = mean(...)`, escolhe-se a de **menor índice** (`np.argmax` default — primeiro vencedor wins). Dex DEVE citar no docstring.

### 6.5 Toy benchmark T11 (anti-correlação perfeita IS↔OOS)

```python
# 4 variantes × 4 folds (T=4, N=4); CSCV particiona N em 2 IS + 2 OOS → S = C(4,2) = 6 partições.
cv_results_matrix = np.array([
    [10.0, 9.0, 1.0, 0.5],   # var 0: domina IS folds 0-1, péssimo OOS folds 2-3
    [ 8.0, 7.0, 3.0, 2.0],
    [ 3.0, 2.0, 7.0, 8.0],
    [ 1.0, 0.5, 9.0, 10.0],  # var 3: péssimo IS folds 0-1, domina OOS folds 2-3
])
```

**Computação manual (Dex deve reproduzir bit-a-bit):**

| s | J_s^IS | J_s^OOS | t* (argmax IS) | R^OOS rank de t* (asc, method='min') | λ_s | overfit (λ ≤ 0)? |
|---|--------|---------|----------------|---------------------------------------|-----|------------------|
| 1 | {0,1}  | {2,3}   | var 0 (mean=9.5) | rank 1 (var 0 OOS mean = 0.75, pior)   | log(1/4) ≈ -1.386 | YES |
| 2 | {0,2}  | {1,3}   | var 0 (mean=5.5, empate vs var1; argmin idx → var 0) | OOS means: var0=(9+0.5)/2=4.75, var1=(7+2)/2=4.5, var2=(2+8)/2=5.0, var3=(0.5+10)/2=5.25 → asc: [var1, var0, var2, var3] → rank(var0)=2 | log(2/3) ≈ -0.405 | YES |
| 3 | {0,3}  | {1,2}   | var 0 (IS mean=5.25 vs var1=5.0, var2=5.0, var3=5.0; argmax → var 0) | OOS means: var0=(9+1)/2=5.0, var1=(7+3)/2=5.0, var2=(2+7)/2=4.5, var3=(0.5+9)/2=4.75; asc: [var2, var3, var0, var1] → rank(var0)=3 | log(3/2) ≈ 0.405 | NO |
| 4 | {1,2}  | {0,3}   | var 0 (IS mean=5.0, empate; argmin idx → var 0) | OOS means: var0=(10+0.5)/2=5.25, var1=(8+2)/2=5.0, var2=(3+8)/2=5.5, var3=(1+10)/2=5.5; asc: [var1, var0, var2, var3 (empate var2 e var3 → rank-min=3 para ambos)] → rank(var0)=2 | log(2/3) ≈ -0.405 | YES |
| 5 | {1,3}  | {0,2}   | var 3 (IS mean=5.25; var0=4.75, var1=4.5, var2=5.0, var3=5.25 → argmax = var 3) | OOS means: var0=(10+1)/2=5.5, var1=(8+3)/2=5.5, var2=(3+7)/2=5.0, var3=(1+7)/2=4.0; asc: [var3, var2, var0, var1 (empate var0 e var1 → rank-min=3)] → rank(var3)=1 | log(1/4) ≈ -1.386 | YES |
| 6 | {2,3}  | {0,1}   | var 3 (IS mean=9.5) | OOS means: var0=(10+9)/2=9.5, var1=(8+7)/2=7.5, var2=(3+2)/2=2.5, var3=(1+0.5)/2=0.75; asc → rank(var3)=1 | log(1/4) ≈ -1.386 | YES |

**PBO = 5 / 6 ≈ 0.8333**

```python
expected   = 0.8333333333
tolerância = 1e-4   # tie-breaking determinístico → exato em scipy ≥ 1.10
```

> **Nota T11:** este toy substitui o "2×4 trivial PBO=1.0" originalmente no AC4 da story T002.0d. Proponho a Beckett/Pax que AC4 seja atualizado para refletir T11-FINAL `expected = 0.8333 ± 1e-4`. A construção 2×4 trivial só atinge PBO=1.0 com `T=2` variantes — caso degenerado onde o rank é binário (1 ou 2) e a fórmula λ = log(rank/(T+1-rank)) tem só 2 valores possíveis. Manter como T12 abaixo para sanity.

### 6.6 Toy benchmark T12 (matrix degenerate — PBO=1.0 trivial)

```python
# T=2 variantes × N=4 folds com anti-correlação total.
cv_results_matrix = np.array([
    [10.0, 9.0, 1.0, 0.5],   # var 0: alta IS (folds 0,1), baixa OOS (folds 2,3)
    [ 1.0, 0.5, 9.0, 10.0],  # var 1: opposite
])
# C(4,2) = 6 partições.
# Em TODA partição, o argmax IS é exatamente a pior variante OOS:
#   - rank(t*) = 1 sempre → λ = log(1/2) < 0 → overfit em todos.
expected = 1.0
tolerância = 1e-12
```

### 6.7 Toy benchmark T13 (controle ruído — PBO ≈ 0.5)

```python
cv_results_matrix = np.random.default_rng(42).normal(0, 1, size=(4, 8))
# 4 variantes × 8 folds, ruído gaussiano puro, sem estrutura.
# Em CSCV puramente aleatório, expected PBO converge a 0.5 (sem overfitting estrutural).
expected   ≈ 0.5
tolerância ≈ 0.15   # estocástico; n=8 folds → variância apreciável; Dex usa seed=42 para reproduzir
```

---

## 7. Métrica 6 — Sortino Ratio

### 7.1 Assinatura

```python
# packages/vespera_metrics/trade_stats.py
def sortino_ratio(returns: np.ndarray, freq: str = "daily", target: float = 0.0) -> float: ...
```

### 7.2 Fórmula

```
DD_t = min(returns_t - target, 0)
downside_dev = sqrt( mean(DD_t²) )
Sortino = (mean(returns) - target) / downside_dev × sqrt(periods_per_year)
```

**Referência:** Sortino & van der Meer (1991); AFML Ch.14 §14.2.

### 7.3 Edge cases

| Situação | Comportamento |
|----------|---------------|
| Todos `returns >= target` | `downside_dev = 0` → retorna `inf` se mean > target, `0.0` se mean == target |
| `len(returns) < 2` | `raise ValueError` |

### 7.4 Toy benchmarks

**T13 (no downside):**
```
returns = [0.01] * 252
expected = inf
```

**T14 (alternating, AC8):**
```
returns       = [0.01, -0.005] * 126
target        = 0.0
mean          = 0.0025
DD            = [0, -0.005] × 126 → sum_sq = 126 × 0.005² = 0.00315
downside_dev  = sqrt(0.00315 / 252) ≈ 0.003536
Sortino_d     = 0.0025 / 0.003536 ≈ 0.7071
Sortino_ann   ≈ 0.7071 × sqrt(252) ≈ 11.225
expected      ≈ 11.225
tolerância    = 1e-3
```

> Property test (AC implícito): `sortino >= sharpe` quando `skew(returns) > 0` (downside menor que volatility total).

---

## 8. Métrica 7 — Maximum Drawdown e MAR

### 8.1 Assinatura

```python
# packages/vespera_metrics/drawdown.py
def max_drawdown(equity: np.ndarray) -> float: ...   # retorna valor NEGATIVO ou 0
def mar_ratio(cagr: float, max_dd: float) -> float: ...
```

### 8.2 Fórmula

```
peak_t = max(equity[0..t])
dd_t = (equity_t - peak_t) / peak_t
max_dd = min_t(dd_t)        # mais negativo

MAR = CAGR / abs(max_dd)    # se max_dd < 0
    = inf                   # se max_dd == 0 e CAGR > 0
    = 0                     # se ambos == 0
    = -inf                  # se CAGR < 0 e max_dd == 0
```

**Referência:** Calmar/MAR — Young (1991), Schwager *Market Wizards* (1989).

### 8.3 Edge cases (AC9)

| Situação | Comportamento |
|----------|---------------|
| `equity` constante | `max_dd = 0.0` |
| `equity` strictly increasing | `max_dd = 0.0` |
| `equity[0] <= 0` | `raise ValueError("equity series must start positive")` |
| CAGR > 0, max_dd < 0 | MAR > 0 |
| CAGR < 0, max_dd < 0 | MAR < 0 (NÃO NaN) — **explicit sign**, AC9 |
| `max_dd == 0` E `CAGR == 0` | `MAR = 0.0` (NÃO NaN) |

### 8.4 Toy benchmarks

**T15 (simple drawdown):**
```
equity   = [100, 110, 120, 90, 100, 130]
peak     = [100, 110, 120, 120, 120, 130]
dd       = [0, 0, 0, -0.25, -0.1667, 0]
max_dd   = -0.25
expected = -0.25
tolerância = 1e-12
```

**T16 (MAR sinal negativo, AC9):**
```
cagr     = -0.10
max_dd   = -0.30
MAR      = -0.10 / 0.30 = -0.3333
expected = -0.3333
```

---

## 9. Métrica 8 — Ulcer Index

### 9.1 Assinatura

```python
def ulcer_index(equity: np.ndarray) -> float: ...
```

### 9.2 Fórmula (Martin 1989)

```
peak_t = max(equity[0..t])
ret_dd_t = 100 × (equity_t - peak_t) / peak_t   [percentual NEGATIVO ou 0]
UI = sqrt( mean(ret_dd_t²) )
```

**Referência:** Martin, P. (1989) — `tangotools.com/ui/ui.htm` (AC10).

### 9.3 Toy benchmark (AC10)

**T17 (Martin canonical example):**
```
equity   = [100, 95, 90, 100, 110]
peak     = [100, 100, 100, 100, 110]
ret_dd_pct = [0, -5, -10, 0, 0]   (em %)
sum_sq   = 0 + 25 + 100 + 0 + 0 = 125
UI       = sqrt(125 / 5) = sqrt(25) = 5.0
expected = 5.0
tolerância = 1e-12
```

---

## 10. Métricas de trade (hit rate, profit factor)

### 10.1 Assinaturas

```python
def hit_rate(trades_pnl: np.ndarray) -> float: ...  # fração de trades > 0
def profit_factor(trades_pnl: np.ndarray) -> float: ...  # sum(wins) / abs(sum(losses))
```

### 10.2 Edge cases

| Situação | Comportamento |
|----------|---------------|
| `len(trades) == 0` | `raise ValueError("no trades")` |
| Todos trades positivos | `profit_factor = inf`, `hit_rate = 1.0` |
| Todos trades zero | `hit_rate = 0.0`, `profit_factor = 1.0` (convenção: 0/0 → 1) |
| Todos trades negativos | `profit_factor = 0.0`, `hit_rate = 0.0` |

### 10.3 Toy benchmarks

**T18:**
```
trades_pnl = [10, -5, 20, -15, 8, -3, 12]
wins       = 10+20+8+12 = 50
losses     = abs(-5-15-3) = 23
profit_factor = 50 / 23 ≈ 2.1739
hit_rate   = 4/7 ≈ 0.5714
```

---

## 11. Determinismo global (AC11)

- Toda função estocástica (apenas `bootstrap_ci`) usa `np.random.default_rng(seed)`.
- Default `seed=42`.
- Não chamar `np.random.seed()` global (poluição).
- 2 runs com mesmo seed sobre o mesmo input → mesmo output byte-a-byte.

---

## 12. Edge cases globais que merecem destaque

| # | Edge case | Métricas afetadas | Tratamento |
|---|-----------|-------------------|------------|
| EC1 | Single-path / N=1 | DSR, PBO, sharpe_distribution | DSR raise; PBO raise; sharpe_distribution retorna shape (1,) |
| EC2 | All-zeros returns | Sharpe, Sortino, MAR | retornam 0.0 (não NaN); profit_factor=1.0 |
| EC3 | Equity strictly increasing | max_dd=0, MAR=inf, UI=0 | OK |
| EC4 | NaN em qualquer input | TODAS | `raise ValueError` (clean upstream — Beckett owns NaN handling) |
| EC5 | Inf em returns | Sharpe, Sortino | propaga inf; logged como warning |
| EC6 | n_trials < 2 | DSR | raise — desambígua |
| EC7 | T < 2 ou N < 2 ou N ímpar | PBO | raise |
| EC8 | Bootstrap com sample length 1 | bootstrap_ci | raise |

---

## 13. Sign-off

| Agente | Validação | Status |
|--------|-----------|--------|
| Mira | autoria + matemática + bibliografia | ASSINADO (este doc) |
| Beckett | toy numerics cross-validados contra Bailey-LdP 2014 + AFML Ch.11 + (mlfinlab onde aplicável) | PENDENTE — sign-off comment na story T002.0d |
| Kira | alignment kill criteria (K1: DSR>0; K2: PBO<0.4; K3: IC decay) | PENDENTE |
| Dex | implementação byte-exact contra toy benchmarks | PENDENTE — após AC0 gate |
| Pax | `*validate-story-draft` T002.0d → GO | PENDENTE |

---

## 14. Pendências e ações para Beckett/Kira

### Beckett (handshake)

- [ ] Cross-validar T9 (DSR) contra `mlfinlab.backtest_statistics.statistics.deflated_sharpe_ratio` em commit explícito; reportar discrepâncias.
- [ ] Validar convenção LOCKED de rank em PBO (§6.4): `scipy.stats.rankdata(method='min')` para tie-break em rank OOS; argmax IS por menor índice — se discordar, propor convenção alternativa em sign-off ANTES de Dex implementar.
- [ ] Validar T11 (PBO=0.8333) e T12 (PBO=1.0 trivial) — replicar manualmente conforme §6.5 e §6.6.
- [ ] Confirmar shape de `BacktestResult` (paralelo) — `MetricsResult` consome `pnl_series` (per-bar returns) e `trades` (per-trade pnl) de cada `BacktestResult`. Acordar em handshake.
- [ ] Validar `to_markdown()` schema em `T002-cpcv-report.md` template (Beckett owns).

### Kira (alignment)

- [ ] Confirmar K1: `DSR > 0` (não DSR > 0.95 absolute, que seria forte evidence; T002 thesis usa DSR > 0 como mínimo viável).
- [ ] Confirmar K2: `PBO < 0.4` está alinhado com thesis §5 kill criteria.
- [ ] Confirmar K3: `IC_holdout >= 0.5 × IC_in_sample` (não DSR-based em K3).

### Mira (próximas iterações)

- [ ] Após Beckett sign-off, recompute hash SHA256 deste arquivo e atualizar `Mira-signature` no header.
- [ ] Atualizar `docs/ml/research-log.md` com `n_trials_cumulative` (gap T0 da story T002.0d) — **separado deste documento**, não escopo aqui.

---

— Mira, mapeando o sinal 🗺️
