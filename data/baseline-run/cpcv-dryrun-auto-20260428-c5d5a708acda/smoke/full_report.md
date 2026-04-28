# T002 CPCV Metrics Report

- **Spec version:** `T002-v0.2.3`
- **Computed (BRT):** `2026-04-28T20:34:21`
- **n_paths:** 45
- **n_pbo_groups:** 10
- **n_trials_used:** 5
- **n_trials_source:** `docs/ml/research-log.md@69d97aeea2276370a797a5f32dabde6a6ad7261e`
- **bootstrap seed:** 42

## Primary metrics

- **IC Spearman (mean):** 0.000000
- **IC Spearman 95% CI:** [0.000000, 0.000000]
- **Deflated Sharpe Ratio:** 0.500000
- **PBO:** 0.500000

## Secondary metrics (median over paths unless noted)

- **Sharpe (mean over paths):** 0.000000
- **Sharpe (median):** 0.000000
- **Sharpe (std over paths):** 0.000000
- **Sortino:** 0.000000
- **MAR:** 0.000000
- **Ulcer Index:** 0.000000
- **Max Drawdown:** 0.000000
- **Profit Factor:** 0.000000
- **Hit Rate:** 0.000000

## Kill decision

- **Verdict:** **NO_GO**
- K1 (DSR>0): PASS
- K2 (PBO<0.4): FAIL
- K3 (IC decay): FAIL

### Reasons
- K2: PBO=0.500000 >= 0.4 (kill criterion)
- K3: IC_in_sample=0.000000 non-positive — no edge
