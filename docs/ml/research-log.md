# Vespera Research Log — Cumulative Multiple-Testing Ledger

> **Owner:** Mira (@ml-researcher) — sole authority on append/edit of this ledger.
> **Purpose:** Single source of truth for `n_trials_cumulative` consumed by
> `vespera_metrics.dsr.deflated_sharpe_ratio` and any downstream multiple-testing
> correction (Bonferroni, Benjamini-Hochberg, Holm).
> **Reference:** Bailey & Lopez de Prado (2014), "The Deflated Sharpe Ratio:
> Correcting for Selection Bias, Backtest Overfitting, and Non-Normality",
> *Journal of Portfolio Management*, Vol. 40, No. 5, §3 — DSR penalises
> multiple-testing **GLOBAL** (cross-story / cross-experiment), not per-story.

---

## Authority statement

This file is the **append-only** ledger of every research trial that has touched
the Vespera modeling effort. Once an entry has been signed by Mira and committed,
its `n_trials` integer is immutable. Corrections happen by **adding a new entry**
that explicitly references and amends the prior one (R15-style discipline,
Article IV — No Invention). Editing an already-signed entry in place is forbidden
and treated as forgery by downstream contract tests.

---

## Schema (parse contract)

Every entry is a YAML frontmatter block delimited by `---` lines, immediately
followed by an optional free-form markdown body. Parsers MUST:

1. Walk the file, splitting on top-level `---` fences.
2. For each fenced block, parse as a flat YAML mapping.
3. Validate required keys (see below). On missing key → fail hard.
4. Sum the integer field `n_trials` across **all** valid entries to obtain
   `n_trials_cumulative`.
5. Treat the file as authoritative — no soft-fallback. If the file is missing or
   malformed, the consumer raises (Article IV — forbid invention of defaults).

### Required fields per entry

| Field              | Type         | Notes                                                                 |
|--------------------|--------------|-----------------------------------------------------------------------|
| `story_id`         | string       | AIOX story identifier (e.g. `T002.0d`).                               |
| `date_brt`         | YYYY-MM-DD   | Date the trials were enumerated, in BRT (MANIFEST R2).                |
| `n_trials`         | int >= 0     | Number of NEW model/parameter trials introduced by this story.        |
| `trials_enumerated`| list[string] | Trial IDs (matches spec `n_trials.variants[].id`). Empty if `n_trials==0`. |
| `description`      | string       | One-paragraph rationale linking trials to spec and toy benchmarks.    |
| `spec_ref`         | string       | Path (and ideally pinned hash) of the spec defining the trial set.    |
| `signed_by`        | string       | Always `Mira (@ml-researcher)` for this ledger.                       |

### Append-only discipline

- New trials → **new entry**, never edit prior entries.
- Retraction of a trial → new entry with `n_trials: 0` and a `description`
  explicitly naming the retracted trial(s) and rationale. The original trial
  count remains in the cumulative sum (the trial **was** run, the prior is
  still owed to the multiple-testing correction).
- File version bumps at the bottom (`## Version`) are append-only too.

---

## Entries

---
story_id: T002.0d
date_brt: "2026-04-25"
n_trials: 5
trials_enumerated: [T1, T2, T3, T4, T5]
description: "Vespera metrics module — DSR/PBO/IC/Sharpe/Drawdown/TradeStats implementação. 5 trial variants per spec T002 v0.2.0 §trading_rules (T1=baseline 4 janelas threshold P60 regime ATR [P20,P80] lookback 126d; T2=4 janelas threshold P50 regime ATR [P20,P80] lookback 126d; T3=4 janelas threshold P70 regime ATR [P20,P80] lookback 126d; T4=4 janelas threshold P60 regime ATR sem filtro lookback 126d; T5=1 janela 17:25 threshold P60 regime ATR [P20,P80] lookback 126d). Lookback 126d universal pós PRR-20260421-1. Toy benchmarks Mira §6 validados byte-exact."
spec_ref: "docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml@4b5624ad6ba151c57e263f1d160d7e802354c5e164f777198755b70c59bdc3fc"
signed_by: "Mira (@ml-researcher)"
---

T002.0d enumerou o trial set canônico que toda execução CPCV de Vespera vai
varrer. Os cinco trials varrem: (a) sensitivity ao threshold de magnitude
(T1/T2/T3 em P50/P60/P70), (b) ablation do filtro de regime ATR (T4), e
(c) ablation do número de janelas de entrada (T5, apenas 17:25). Bonferroni
calibrado em α/5 = 0.002 conforme spec §n_trials.bonferroni_adjusted_p_value.

---
story_id: T002.0f
date_brt: "2026-04-26"
n_trials: 0
trials_enumerated: []
description: "CPCV harness integration — orchestration only, no new trials introduced. Consumes T002.0d trial set unchanged."
spec_ref: "docs/stories/T002.0f.story.md"
signed_by: "Mira (@ml-researcher)"
---

T002.0f é puramente infra: integra o harness CPCV ao módulo `vespera_metrics`
de T002.0d. NENHUM trial novo é introduzido — a story consome o trial set
{T1..T5} já versionado em T002.0d. Por isso `n_trials: 0` e
`trials_enumerated: []`. Esta entrada existe explicitamente para deixar o
audit trail completo (story tocou pipeline → Mira assinou → Bailey-LdP §3
honrado mesmo com delta zero).

---

## Version

**v0.1** — 2026-04-26 BRT — Mira (@ml-researcher) — seed entries T002.0d + T002.0f

— Mira, mapeando o sinal
