# T002 — CPCV Purge & Embargo Formula Specification

**Owner:** Mira (@ml-researcher) — algoritmo + formalização matemática
**Consumers:** Dex (@dev) — implementa em `packages/vespera_cpcv/engine.py`; Beckett (@backtester) — consome via `CPCVEngine.run`
**Story:** [T002.0c — CPCV Engine](../../stories/T002.0c.story.md) (Tasks T0 handshake, T3, T7, T8)
**Spec parent:** [T002 v0.2.0](T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml) §cv_scheme L147-154
**Authority:** Article IV (No Invention) — toda fórmula traceável a Lopez de Prado, *Advances in Financial Machine Learning* (Wiley 2018) — doravante **AFML**.
**Created:** 2026-04-25 BRT
**Mira-signature:** PENDING (será SHA256 do conteúdo após sign-off cruzado com Beckett)

---

## 0. Escopo

Este documento especifica formalmente:

1. A função **purge** que descarta amostras de treino com sobreposição temporal de label vs janela de teste.
2. A função **embargo** que descarta amostras adicionais imediatamente após o teste para impedir leakage por autocorrelação.
3. Os edge cases relevantes (start/end of dataset, gaps em manifest, single-day groups).
4. Estimativa do tamanho purgado em função dos defaults da spec T002 v0.2.0 (N=10, k=2, embargo=1 sessão).

NÃO especifica: shape de `BacktestResult` (handshake paralelo Beckett), I/O do engine (Dex decide), métricas (T002-vespera-metrics-spec.md).

---

## 1. Notação

| Símbolo | Definição |
|---------|-----------|
| `E` | Conjunto ordenado de eventos `{e_0, e_1, …, e_{M-1}}`, ordenados por `t_start(e_i)` |
| `t_start(e)` | Timestamp BRT (naive) em que a feature do evento `e` é COMPUTADA — momento da decisão. |
| `t_end(e)` | Timestamp BRT em que o LABEL do evento `e` é OBSERVÁVEL (deadline de horizonte). Para T002: `t_end = 17:55:00 BRT do mesmo dia`. Para triple-barrier: `min(t_tp, t_sl, t_horizon)`. |
| `N` | Número de grupos contíguos (T002: `n_groups=10`). |
| `k` | Número de grupos de teste por split (T002: `k=2`). |
| `G_j` | j-ésimo grupo, `j ∈ [0, N-1]`, partição contígua de `E`. |
| `T = {G_{j_1}, …, G_{j_k}}` | Conjunto de teste do split (escolhido em `combinations(range(N), k)`). |
| `T_blocks` | Sub-conjuntos contíguos de `T` quando `j_2 - j_1 > 1` (intervalos disjuntos no eixo do tempo). |
| `[a, b]` | Intervalo temporal fechado. |
| `embargo_sessions` | Inteiro ≥ 0 (T002: `1`). Número de **sessões de pregão** (não de barras) descartadas pós-teste. |
| `\|S\|` | Cardinalidade do conjunto `S`. |

---

## 2. Particionamento contíguo (background — não é purge)

**AFML §12.3 (p. 163-164):** CPCV particiona `E` em `N` grupos **contíguos** (não aleatórios) preservando a ordem temporal:

```
G_j = {e_i ∈ E : j·M/N ≤ i < (j+1)·M/N}    para j ∈ [0, N-1]
```

Implementação canônica: `np.array_split(events.index, N)` (cobre o caso `M mod N != 0` distribuindo o resto pelos primeiros grupos).

**Invariante crítico:** `max(t_start(G_j)) < min(t_start(G_{j+1}))` ∀ j. Sem isso, purge fica indefinido.

---

## 3. Purge formula

### 3.1 Definição (formal)

Para um split com conjunto de teste `T`, decomposto em blocos temporalmente contíguos `T_blocks = {B_1, B_2, …, B_b}` (cada `B_l` é uma união de grupos `G_j` adjacentes, `b ≤ k`), define-se a **janela de cada bloco**:

```
window(B_l) = [ min_{e ∈ B_l} t_start(e),  max_{e ∈ B_l} t_end(e) ]
```

**A função purge** remove de `Train = E \ T` qualquer evento de treino cujo label sobreponha QUALQUER janela de teste:

```
Purge(Train, T) = { e ∈ Train : ∀ B_l ∈ T_blocks,  [t_start(e), t_end(e)] ∩ window(B_l) = ∅ }
```

Equivalente (forma operacional, AFML §7.4.1 p. 105-107, eq. 7.1):

```
e ∈ Train é PURGADO  ⟺  ∃ B_l ∈ T_blocks :
                          t_end(e)   ≥ window(B_l).start  ∧
                          t_start(e) ≤ window(B_l).end
```

Ou seja: **purgar todo evento de treino cuja barra de feature OU cujo deadline de label cai dentro da janela do teste**.

### 3.2 Justificativa AFML

**AFML §7.4.1 (Purging):** "If a training observation `Y_i` overlaps in time with a testing observation `Y_j`, then `Y_i` and `Y_j` will share information. […] To prevent this, all training observations whose labels overlap in time with the testing labels must be purged from the training set."

**AFML §12.4 (CPCV) p. 165:** o purging do CPCV é a **mesma função** de Ch.7 aplicada por bloco de teste (não pelo conjunto inteiro `T` se este for descontíguo). Razão: bloco descontíguo cria duas zonas de risco de leakage independentes.

### 3.3 Correctness invariant (AC13 da story)

Após purge + embargo, vale para todo evento de treino `e ∈ Train_purged`:

```
∀ B_l ∈ T_blocks:
   t_end(e)   < window(B_l).start  - embargo_offset   (treino strictly antes do teste)
   ∨
   t_start(e) > window(B_l).end    + embargo_offset   (treino strictly depois do teste + embargo)
```

Esta é a invariante que `tests/vespera_cpcv/test_cpcv_purge_embargo.py::test_no_lookahead` deve assertar.

---

## 4. Embargo formula

### 4.1 Definição (formal)

**AFML §7.4.2 (Embargo) p. 107-108:** mesmo após purge, autocorrelação serial entre features adjacentes faz com que treino imediatamente posterior ao teste vaze informação. Solução: descartar `h` observações **APÓS** cada bloco de teste:

```
Embargo(Train_purged, T_blocks, h) =
  { e ∈ Train_purged : ∀ B_l ∈ T_blocks,
      t_start(e) ∉ ( window(B_l).end,  window(B_l).end + h ] }
```

Onde `h = embargo_offset` é convertido de **sessões** para **timestamp delta**.

### 4.2 Conversão sessões → timestamp delta (T002 specific)

Para a tese T002 (event-driven com 4 entradas/dia em janela 16:55-17:55 BRT), uma "sessão" significa **um dia de pregão completo**. Operacionalmente, em vez de janela temporal de 24h literal:

```
embargo_offset(test_block, sessions=1) =
   primeiro evento de treino e' tal que
   sessao(e'.t_start) > sessao(B_l_end.t_end) + (sessions - 1)
```

Onde `sessao(t)` é a função que mapeia timestamp para o **dia de pregão** (data ISO YYYY-MM-DD em BRT, considerando o calendário B3 sem fins de semana, sem feriados, sem dias pós-Copom já excluídos via `post_copom_exclusion`).

**Consequência operacional:** com `embargo_sessions=1`, o embargo na T002 descarta **toda a sessão imediatamente seguinte** ao último dia do bloco de teste. Dado que cada sessão tem 4 eventos T002 (16:55, 17:10, 17:25, 17:40), cada bloco contribui com **4 eventos embargados** em média.

### 4.3 Por que somente pós-teste, não pré-teste

**AFML §7.4.2 (caveat):** o embargo é assimétrico — só pós-teste. Causa: autocorrelação positiva tipicamente decai em direção forward; o purge já cobriu o lado backward (label `t_end` do treino ≤ início do teste).

**Exceção que NÃO se aplica à T002:** se o label tivesse horizonte negativo (predizer passado) ou se features tivessem rolling-window que olha à frente (proibido por leakage-audit), embargo pré-teste seria necessário. Não é o caso.

---

## 5. Edge cases

### 5.1 Bloco de teste no início do dataset (`G_0 ∈ T`)

- Purge: nada a purgar à esquerda (não há treino antes).
- Embargo: aplicado normalmente à direita.
- **Tratamento:** OK, sem caso especial.

### 5.2 Bloco de teste no fim do dataset (`G_{N-1} ∈ T`)

- Purge: nada a purgar à direita.
- Embargo: tentaria descartar pós-teste, mas não há `Train` à direita. **Tratamento:** embargo é no-op (fail-safe via filter — nenhum evento corresponde, retorna conjunto vazio para descartar).
- **Não levantar erro** — situação é legítima em CPCV.

### 5.3 Test blocks descontíguos (`k=2`, grupos não-adjacentes)

Exemplo: split escolhe `T = {G_2, G_7}`. Então `T_blocks = [{G_2}, {G_7}]` (dois blocos disjuntos).

- Purge é aplicado **independentemente para cada bloco** (eq. §3.1).
- Embargo é aplicado **independentemente após cada bloco** (após `G_2.end + 1 sessão` E após `G_7.end + 1 sessão`).
- Treino entre `G_2` e `G_7` (i.e., parte do `G_3 ∪ G_4 ∪ G_5 ∪ G_6`) recebe ambos efeitos.

### 5.4 Test blocks adjacentes (`k=2`, grupos consecutivos)

Exemplo: `T = {G_3, G_4}`. Então `T_blocks = [{G_3, G_4}]` (1 bloco contíguo de 2 grupos).

- Purge é aplicado uma única vez sobre a janela combinada.
- Embargo é aplicado uma única vez após `G_4.end`.
- **Vantagem computacional:** menos eventos descartados que descontíguo (1 zona de embargo em vez de 2).

### 5.5 Gaps no manifest de eventos (dias faltantes — feriado, halt, etc.)

A tese T002 exclui `post_copom` e `rollover D-3 a D-1`. Portanto `events` já tem buracos.

- **Particionamento (§2):** `np.array_split` opera sobre `events.index`, não sobre o calendário; logo grupos têm aproximadamente o mesmo `|G_j|` mas diferentes `duracao(G_j)` em dias. **Aceitável.**
- **Purge:** baseia-se em timestamps, não em índice — funciona corretamente sobre dataset com buracos.
- **Embargo:** `sessao(t)` deve usar **calendário efetivo do dataset** (datas presentes em `events`), não calendário B3 puro. Se a sessão imediatamente seguinte estiver excluída, o embargo automaticamente "pula" para a próxima sessão presente.

**Implementação sugerida (Dex):** `embargo_offset` calculado como `embargo_sessions`-ésimo dia distinct posterior em `events.t_start.dt.date.unique()`.

### 5.6 Único evento por sessão (degenerate)

T002 tem 4 eventos/sessão, mas se cair `events` filtrado para apenas 1 entrada/dia (cenário stress-test ou variant T5 da spec):

- Purge: funciona.
- Embargo: descarta no máximo 1 evento por bloco (em vez de 4). **Aceitável** — a invariante de leakage é preservada.

### 5.7 `M < N` (menos eventos que grupos — DEFESA)

Se `len(events) < n_groups`, `np.array_split` produz grupos vazios. **Tratamento:** `CPCVEngine.generate_splits` deve **levantar `ValueError`** com mensagem explícita: `"Insufficient events: M=<M> < N=<n_groups>; need M ≥ N (ideally M ≥ 10×N for AFML CPCV)."`

### 5.8 Hold-out lock (R1 + AC12)

**Independente do purge/embargo:** se `events` contiver qualquer timestamp em `[2025-07-01, 2026-04-21]` E `VESPERA_UNLOCK_HOLDOUT != 1`, `generate_splits` deve levantar `HoldoutLockError` ANTES de chamar particionamento. Esta é a defesa de R1/R15(d) e é validada por T002.0c AC12.

---

## 6. Expected purged sample size (T002 defaults)

### 6.1 Premissas

- N = 10
- k = 2
- embargo_sessions = 1
- Janela in-sample: 2024-07-01 → 2025-06-30 = 12 meses úteis ≈ 250 sessões (B3, descontados feriados; antes de `post_copom_exclusion`).
- Eventos por sessão: 4 (entrada às 16:55/17:10/17:25/17:40).
- M ≈ 250 × 4 = **1000 eventos** (aproximação; valor real depende de exclusões pós-Copom — esperado ~10-15 sessões/ano).
- `|G_j| ≈ M/N = 100 eventos = ~25 sessões` por grupo.

### 6.2 Cálculo per split

Para um split `T = {G_a, G_b}` com a < b:

**Caso adjacente** (`b = a+1`, ocorre em N-1 = 9 dos 45 splits):

- `|T| = |G_a| + |G_b| ≈ 200` eventos.
- 1 zona de embargo após `G_b.end`: descarta ~4 eventos (1 sessão × 4 eventos).
- Purge: para T002, `t_end(e) ≤ fim_da_sessao(e)`, e como o particionamento é contíguo, **purge não descarta nada adicional além das fronteiras já cobertas pelo bloco de teste**, exceto eventos cujo `t_end` cruza fronteira de grupo. Como T002 fecha label às 17:55 do mesmo dia (sem cruzar fronteira de sessão), **purge ≈ 0 eventos** no caso típico.
- `Train ≈ M - |T| - embargo = 1000 - 200 - 4 = 796` eventos.

**Caso descontíguo** (`b > a+1`, ocorre em 36 dos 45 splits):

- `|T| ≈ 200` eventos.
- 2 zonas de embargo (após G_a e após G_b se G_b não for o último): descarta ~4 + ~4 = 8 eventos. Se G_b = G_9, só 4.
- Purge ≈ 0 eventos (mesma lógica).
- `Train ≈ M - |T| - embargo = 1000 - 200 - 8 = 792` eventos.

### 6.3 Tabela de referência (closed-form para Dex/Beckett)

| Cenário | # de splits | \|Train\| esperado | Purgados | Embargados |
|---------|-------------|--------------------|----------|------------|
| Adjacente (b=a+1) | 9 | ~796 | ~0 | ~4 |
| Descontíguo, b<N-1 | ~28 | ~792 | ~0 | ~8 |
| Descontíguo, b=N-1 | ~8 | ~796 | ~0 | ~4 |

**Total esperado:** todos os 45 splits têm `|Train| ∈ [790, 800]`, `|Test| ≈ 200`, `purgados ≈ 0`, `embargados ∈ {4, 8}`.

### 6.4 Sanity check para AC8 (toy benchmark)

**AFML Ch.12 §12.4 Figure 12.2/12.3 reference:** N=6, k=2, M=6 events (1 evento/grupo).

- C(6,2) = 15 splits.
- Cada split: |T|=2, |Train inicial|=4.
- Para event-driven simples (label horizon = 1 evento), sem labels sobrepostos, purge ≈ 0.
- Embargo `h=1` evento descarta 1 evento adjacente após cada bloco de teste:
  - Splits adjacentes (5 dos 15: `(0,1), (1,2), (2,3), (3,4), (4,5)`): embargo descarta 1 evento (próximo). |Train final| = 3.
  - Splits descontíguos não-final (8 dos 15): embargo após cada um dos 2 blocos descarta 2 eventos. |Train final| = 2.
  - Splits com b=5 descontíguos (2 dos 15: `(0,5), (1,5), (2,5), (3,5)` — corrigindo: 4 splits): só 1 embargo (após G_a; G_5 é último). |Train final| = 3.

**Tabela exata para AC8 (Mira fornece):**

| Split | T groups | Adj? | b=N-1? | Embargo events | \|Train\| |
|-------|----------|------|--------|----------------|-----------|
| 0 | (0,1) | sim | não | 1 (após G_1) | 3 |
| 1 | (0,2) | não | não | 2 (após G_0, após G_2) | 2 |
| 2 | (0,3) | não | não | 2 | 2 |
| 3 | (0,4) | não | não | 2 | 2 |
| 4 | (0,5) | não | sim | 1 (após G_0; G_5 último) | 3 |
| 5 | (1,2) | sim | não | 1 (após G_2) | 3 |
| 6 | (1,3) | não | não | 2 | 2 |
| 7 | (1,4) | não | não | 2 | 2 |
| 8 | (1,5) | não | sim | 1 | 3 |
| 9 | (2,3) | sim | não | 1 (após G_3) | 3 |
| 10 | (2,4) | não | não | 2 | 2 |
| 11 | (2,5) | não | sim | 1 | 3 |
| 12 | (3,4) | sim | não | 1 (após G_4) | 3 |
| 13 | (3,5) | não | sim | 1 | 3 |
| 14 | (4,5) | sim | sim | 0 (G_5 é último) | 4 |

**Soma de embargados:** 1+2+2+2+1+1+2+2+1+1+2+1+1+1+0 = **20 eventos descartados ao longo dos 15 splits**.

> Nota AC8: este é o benchmark **comparação exata** (tolerância 0) para `test_cpcv_against_afml_benchmark.py`. Dex deve reproduzir esta tabela byte-a-byte. Pequenas diferenças de definição de embargo (ex.: incluir ou excluir o evento na fronteira exata) devem ser resolvidas DURANTE handshake Dex/Beckett — esta tabela assume embargo strict (`<`, não `≤`) e sessão = 1 evento (toy).

---

## 7. Dependências e references cruzadas

- **Spec parent:** [T002 v0.2.0](T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml) §cv_scheme L147-154.
- **MANIFEST R6:** determinismo de seed em CPCV — fora do escopo deste documento (Dex implementa em `engine.py`), mas purge/embargo são **determinísticos por construção** (função pura de `events` e `T`).
- **MANIFEST R1 + R15(d):** hold-out intocado — defesa em §5.8.
- **AFML Ch.7 §7.4.1 (purging) p. 105-107**: equação 7.1.
- **AFML Ch.7 §7.4.2 (embargo) p. 107-108.**
- **AFML Ch.12 §12.3 (CPCV partition) p. 163-164.**
- **AFML Ch.12 §12.4 (CPCV combined) p. 164-167** + Figure 12.2/12.3 (AC8 reference).

---

## 8. Endorsement do tag `purge_formula_id` (handshake-Beckett)

**Pergunta de Beckett (T002-backtest-result-shape.md §7 item 1):**

> "Mira's CV scheme (spec L148-154) says `purging: true` but doesn't pin the formula. Default Lopez de Prado AFML §7.4.1: drop train samples whose label horizon `[t, t+H]` overlaps any `test_session_dates`. T002 horizon `H = entry_ts → 17:55` (intraday only) means purge is tight (same-day overlap only — minimal impact). **Beckett requests Mira confirm: same-day-only purge, formula tag `"AFML_7_4_1_intraday_H_eq_session"`.**"

**Resposta Mira: ENDOSSADO.**

| Decisão | Valor |
|---------|-------|
| `FoldMetadata.purge_formula_id` | `"AFML_7_4_1_intraday_H_eq_session"` |
| Algoritmo de purge | Definido formalmente em §3.1 deste documento (eq. 7.1 AFML) |
| Algoritmo de embargo | Definido formalmente em §4.1-4.2 deste documento |
| Conversão sessão→timestamp | `embargo_offset` = primeiro evento de treino cuja sessão excede a sessão de fim do bloco de teste em `embargo_sessions` dias do calendário efetivo do dataset (§4.2) |
| Impacto sobre purge size | ~0 eventos purgados por split (label intraday, mesmo dia → não cruza fronteira de grupo). Embargo sim, ~4-8 eventos por split. Ver §6.3 |
| Reasoning | Label T002 fecha `t_end = 17:55:00 BRT do mesmo dia`. Ordem temporal é `t_start_event ≤ t_end_event ≤ session_close_event`. Dois eventos da mesma sessão podem ter labels que se sobrepõem ENTRE SI, mas como o particionamento CPCV é contíguo por evento, todos os eventos da mesma sessão tendem a cair no mesmo grupo. Eventos cuja janela de label cruza fronteira de grupo são raríssimos (apenas se a fronteira do grupo cair entre 16:55 e 17:55 do dia `s = max(date(G_j)) = min(date(G_{j+1}))`). Tratamento: §3.1 cobre essa eventualidade — se houver overlap, o evento é purgado. |

**Tag canônico para o campo `purge_formula_id` em `FoldMetadata`:** `"AFML_7_4_1_intraday_H_eq_session"` — string literal, fixa, não-versionada (mudança de fórmula = nova spec ML major).

**Implicação para Dex (engine.py):** o purge implementado deve verificar overlap de `[t_start(e), t_end(e)] ∩ window(B_l)` com `t_end(e) = end_of_session(date(t_start(e)))` (i.e., 17:55 BRT do mesmo dia, sem timezone). NÃO usar timezone-aware datetime (conforme MANIFEST R2).

---

## 9. Sign-off

| Agente | Validação | Status |
|--------|-----------|--------|
| Mira | autoria + matemática + endorsement do purge_formula_id | ASSINADO (este doc) |
| Beckett | shape de `BacktestResult` consumível por `CPCVEngine.run` + cross-check do tag | PENDENTE — handshake separado (sign-off na story T002.0c) |
| Dex | implementação byte-exact contra §6.4 toy table (AC8) | PENDENTE — após T0 sign-off |
| Pax | `*validate-story-draft` T002.0c → GO | PENDENTE |

---

— Mira, mapeando o sinal 🗺️
