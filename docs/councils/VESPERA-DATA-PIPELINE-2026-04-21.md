# Council — Vespera Data Pipeline (T002.0)

**Convocado por:** Orion (@aiox-master)
**Data:** 2026-04-21 BRT
**Motivação:** Omissão descoberta na Fase C/D1 — Fase E (CPCV) depende de dataset histórico real e não existe story para pipeline Sentinel→Vespera.
**Participantes:** Nelo (@profitdll-specialist), Nova (@market-microstructure), Dara (@data-engineer), Mira (@ml-researcher), Beckett (@backtester), Riven (@risk-manager), Aria (@architect), Quinn (@qa), Sable (@squad-auditor), Pax (@po)
**Decisão esperada:** escopo T002.0 (o que exportar, como armazenar, como versionar, quem faz o quê)

---

## ⚠️ ADDENDUM 2026-04-21 (pós-inspeção do usuário)

O usuário corrigiu duas premissas erradas que contaminaram Turnos 2, 5 e 11:

1. **Sentinel NÃO está rodando backfill.** Sentinel é projeto morto — nenhum processo ativo, zero ingestão nova. O que existe são **dados congelados** no container docker + cópia local CSV recente.
2. **Squad deve inspecionar antes de decidir.** Feito. Resultados consolidados aqui.

### Inspeção realizada (2026-04-21 BRT)

| Item | Achado |
|---|---|
| Container `sentinel-timescaledb` | UP (porta 5433) — preservado mas frozen |
| Tabela `trades` | 56.5 GB, 570 chunks TimescaleDB hypertable |
| Schema `trades.timestamp` | `TIMESTAMP WITHOUT TIME ZONE` ✅ BRT naive (match MANIFEST R2) |
| Ticker literal WDO no DB | `'WDO'` (string curta, NÃO `WDOFUT`) |
| Cobertura WDO | Jan 2-9 2023 (6d isolados, descartar) + **2024-01-02 → 2026-04-02 contínuo** (~500 dias úteis) |
| Volume WDO | 500K-850K trades/dia |
| `trades_backup.csv` local | 1.2 GB, começa 2025-12-26 majoritariamente WIN — **backup incremental, NÃO fonte primária** |
| `sentinel/backtest/engine_v2.py` | Estratégia TFI+SmartScore+XGBoost sobre `features_1s` — **não reutilizável** para Vespera trades-only |

### Implicações que revisam decisões do council

**[REVISADO] Turno 2 (Nelo):** Fonte autoritativa NÃO é ProfitDLL diretamente — é a tabela `trades` do Sentinel TimescaleDB (snapshot congelado). Schema real disponível tem colunas extras (`vol`, `buy_agent`, `sell_agent`, `aggressor`, `trade_type`, `trade_number`) mas o slim 3-col (`timestamp, price, qty`) continua sendo o export correto por R7.

**[REVISADO] Turno 5 (Mira) — CRÍTICO:** Warm-up P252 (252 dias úteis ≈ 12 meses) a partir de 2024-01-02 exige ~12 meses de histórico ANTERIORES a 2024. **Esses dados NÃO existem** (apenas 6 dias isolados em jan/2023). Três alternativas a decidir em T002.0:

  - **(a) Reduzir percentile lookback** de 252d para N dias ajustado ao disponível (ex: 126d = 6 meses)
  - **(b) Escalar incremental** (cresce de 60d até 252d conforme dias acumulam — in-sample start efetivo fica em ~2024-04)
  - **(c) Empurrar in-sample start para 2025-01** (com 12 meses P252 prontos; reduz in-sample a ~6 meses, **ruim para CPCV N=10/k=2**)

  **Mira decide e re-assina spec.** Opção (a) parece preferível — P126 ainda é robusto estatisticamente e preserva in-sample 18 meses.

**[REVISADO] Turno 11 (Pax):** Pré-requisito "Sentinel backfill em curso" **não se aplica** — dataset está congelado e completo para 2024-01 → 2026-04. Gate muda para "snapshot docker existe e é legível read-only".

**[REVISADO] Decisão "2 parquets físicos separados" (Mira/Turno 5):** ainda válida, mas com **alternativa de implementação**: pode ser `WHERE timestamp < '2025-07-01'` no SQL loader + `VESPERA_UNLOCK_HOLDOUT=true` para destravar, **sem exportar parquet de antemão** se ficarmos com leitura direta do DB. Decisão final depende de Beckett (perf 225 replays).

**[REVISADO] Beckett perf (Turno 6):** continua válida — parquet + pyarrow memory-map = ~4.5min p/ 225 replays. DB direct = 60-110min. **Parquet segue como hot-path**, mas agora a materialização pode ser **on-demand dia-ticker** em vez de export antecipado de 56GB. Fase E decide se exporta tudo upfront ou materializa sob demanda.

**[REVISADO] Pipeline architecture:** passa a ter **dois adapters**:

  - `feed_timescale.py` — lê direto do DB (útil para EDA, materializador, e spot checks)
  - `feed_parquet.py` — lê parquet materializado (hot-path CPCV)

  + `scripts/materialize_parquet.py` que converte DB → parquet sob demanda (trigger: primeira run CPCV se cache não existe).

### Decisões originais que permanecem válidas

- Parquet + zstd3 + Hive partition (mensal)
- Schema slim 3 colunas + dtypes estritos
- Hash sha256 por parquet + calendar.yaml
- `data/` gitignored (Opção A de Sable)
- Role read-only `sentinel_ro` (Riven)
- Manifest CSV (Mira)
- `scripts/` vs `packages/` separation (Aria)
- Docker Vespera ❌ agora, ✅ Fase H live (Aria)

---

> **Turnos 1-11 abaixo são mantidos como audit trail da deliberação original.**
> Para a decisão final revisada, leia o ADDENDUM acima + "Decisões finais (revisadas)" no fim do documento.

---

## Turno 1 — Orion abre o chão

> "Plano original: Fase E CPCV roda sobre 2024-01 → 2025-06 in-sample, hold-out 2025-07 → 2026-04 virgem. Engine D1 está pronta, mas ninguém definiu como os trades chegam no Vespera. Sentinel TimescaleDB tem os dados — é a fonte autoritativa. Quero decisão sobre: (a) export parquet vs live DB read; (b) granularidade; (c) partitioning; (d) hash/versioning; (e) git-LFS ou só local; (f) docker ou não. Começa Nelo — de onde vêm os dados?"

---

## Turno 2 — Nelo (@profitdll-specialist) — fonte autoritativa

> "Fonte única: `ProfitDLL.GetHistoryTrades` ingerido pelo Sentinel entre 2024-01-02 e 2026-03-20 (backfill ativo). Cada trade tem: `ts_brt_naive`, `price`, `qty`, `agent_buy_id`, `agent_sell_id`, `aggressor_side` (quando resolvível via GetAgentName), `session`, `ticker_contract` (WDOFUT + código do vencimento vigente).
>
> Campos que o Vespera precisa (mínimo, R7 trades-only): `ts`, `price`, `qty`. O resto é overhead para CPCV — não entra nos feature computers. **Recomendo export slim: 3 colunas + dtype estrito**.
>
> Quanto à granularidade: Sentinel guarda **trade-by-trade** (não barrado). Vespera precisa trade-by-trade — engine consome T&S event-driven. Preserve.
>
> Aviso: dados pré-Jan/2024 indisponíveis na DLL (limite de 27 meses). Para o split da spec isso é OK — in_sample 2024-01 → 2025-06 cabe. Hold-out 2025-07 → 2026-04 também. Mas isso **congela** a profundidade histórica — rebuild futuro do modelo precisa aceitar mesma janela."

---

## Turno 3 — Dara (@data-engineer) — storage & partition

> "Três decisões técnicas:
>
> **(1) Format**: Parquet com compressão `zstd` nível 3. pyarrow memory-map habilita sequential replay sem carregar tudo em RAM.
>
> **(2) Partition**: `year=YYYY/month=MM/` — padrão Hive. Slice temporal (CPCV N=10 groups sobre janelas contíguas) vira filtro de partition push-down, zero deserialization de meses irrelevantes. Granularidade mensal bate com rollover WDO (vencimento é 1º dia útil do mês) — D-3..D-1 de rollover cai sempre no último arquivo do mês.
>
> **(3) Schema estrito pyarrow**:
> ```
> ts:     timestamp[us] (BRT naive — SEM timezone metadata, R2)
> price:  float64
> qty:    int32
> ```
> Nada de strings. Nada de nullable. Nada de index — ordem temporal é garantida por sort dentro de cada partition.
>
> Tamanho estimado: ~5M trades/mês × 24 bytes ≈ 120MB/mês raw → ~15MB/mês comprimido zstd. 28 meses ≈ **420MB total**. Cabe fácil em disco. **NÃO cabe em git direto** — passa do limite de 100MB/file do GitHub mesmo sem LFS, e a árvore inteira passa de 1GB após rollovers. **Git-LFS obrigatório** se entrar no repo. Minha recomendação: **não entrar no repo**."

---

## Turno 4 — Sable (@squad-auditor) — reprodutibilidade

> "Dara toca na ferida. Reproducibility Popperiana exige que qualquer terceiro possa **reproduzir byte-a-byte** o CPCV. Três opções escalares:
>
> **A. Parquet fora do git, hash no spec.** Dataset vive em `data/` (gitignored). `scripts/export_wdo_parquet.py` é determinístico — dado mesmo Sentinel commit, mesmo YAML export, mesmo parquet. Spec YAML carrega `dataset_sha256` pré-registrado. Qualquer auditor re-roda o script, compara hash. Simples. Problema: depende do Sentinel estar rodando e com o dump correto.
>
> **B. Parquet no git-LFS.** `data/wdo_trades_...parquet` em LFS. Reproducibility total (clone + pull LFS). Problema: custo LFS storage ($0.05/GB/mês stored, $0.88/GB bandwidth no plan gratuito da GitHub limit 1GB), plus governance — quem pode commitar updates do dataset? E 2026-05 em diante vai exigir rebuild do parquet mensalmente.
>
> **C. Parquet em object store (S3 / R2 / MinIO local).** Uploaded com versionamento. Spec carrega `dataset_uri` + `dataset_sha256`. Neutro entre reprodutibilidade externa e custos. Problema: infra adicional — conta S3/R2, credenciais.
>
> **Minha recomendação: A agora, migrar pra C se o algoritmo for ao ar.** Custo zero, reprodutibilidade local, hash congelado no spec. Se Vespera virar produção e precisarmos rebuild em CI/CD ou compartilhar com outros quants, aí C."

---

## Turno 5 — Mira (@ml-researcher) — integridade estatística

> "Três exigências da minha parte:
>
> **(1) Dataset imutável para CPCV** — uma vez hasheado no spec, qualquer mutação invalida a assinatura. Sable cobre isso com hash.
>
> **(2) Separação in-sample / hold-out precisa ser física** — prefiro dois parquets separados: `wdo_in_sample_2024-01_to_2025-06.parquet` e `wdo_hold_out_2025-07_to_2026-04.parquet`. Risco de leakage acidental por glob errado é real — já vi gente `ls data/*.parquet | load_all()` e detonar o pre-registro. Arquivos separados + código que recusa carregar o hold-out salvo flag `--unlock-holdout` explícito.
>
> **(3) Hash de CADA parquet no spec** — não um hash agregado. `dataset_in_sample_sha256` + `dataset_hold_out_sha256`. Dois campos. Assinatura Mira só é válida se ambos batem.
>
> Bônus: quero um CSV sumário (`data/manifest.csv`) com `n_trades_por_mes`, `n_dias_validos`, `n_dias_excluidos_copom`, `n_dias_excluidos_rollover` — me dá visão rápida de sample balance sem precisar reabrir o parquet."

---

## Turno 6 — Beckett (@backtester) — performance CPCV

> "Números pra aterrar o debate:
>
> CPCV com N=10 grupos k=2 = 45 paths. × 5 trials (T1..T5) = **225 full replays** do dataset in-sample (~18 meses × ~5M trades/mês = 90M trades). Cada replay precisa consumir a série ordenada por ts. Três modos:
>
> - **Parquet + pyarrow memory-map**: ~1.2s/replay (90M trades, i/o limitado). Total 225 × 1.2s = **4.5min**. Limpo.
> - **TimescaleDB direct query**: ~15-30s/replay (JOIN + network roundtrip + deserialize). Total **60-110min**. Não aceitável pra iteração.
> - **DuckDB sobre parquet**: ~0.8s/replay se for só filter + project. Interessante se Mira quiser queries ad-hoc no dataset.
>
> Sou simpático a **parquet direto** — memory-map + zero DB dependency no path hot. DuckDB pode ser tool auxiliar pra Mira no EDA, não pro CPCV runner.
>
> Exigência minha: **parquet particionado por mês E dentro do mês ordenado por ts**. Preciso ler `2024-01`, `2024-02`, ... em ordem sequencial sem resort."

---

## Turno 7 — Aria (@architect) — contrato de interface

> "Beckett fechou o hot-path. Duas decisões de design que me tocam:
>
> **(1) Adapter pattern**: já temos `HistoricalTradesReplay` (toma iterável de `Trade`). Basta **novo adapter** `ParquetTradesReplay` que implementa o mesmo contrato. Zero mudança no engine layers 2-5. Layer 1 é exatamente isso — pluggable por design.
>
> **(2) Separação `scripts/` vs `packages/`**: o export do Sentinel é **one-shot tooling**, não vai pra produção live. Vive em `scripts/export_wdo_parquet.py`. O reader (`ParquetTradesReplay`) vive em `packages/t002_eod_unwind/adapters/feed_parquet.py` porque é código de produção (rodando em CPCV, possivelmente em CI). Boundary Constitution Article VI — scripts são throwaway, packages são absolute imports.
>
> **(3) Docker, sim — mas escopo certo**: docker-compose do **Sentinel** fica onde está (é infra de dados). O Vespera **não precisa** docker pra rodar o CPCV — Python venv + parquet local basta. Docker no Vespera fica pra quando formos live (Fase H), aí sim quero container reproduzível com ProfitDLL dependency e systemd-style restart. **NÃO docker Vespera agora** — adiciona fricção sem ganho imediato."

---

## Turno 8 — Riven (@risk-manager) — integridade custodial

> "Uma coisa só, mas crítica:
>
> **Read-only do Sentinel.** O script de export conecta com credencial read-only. **Jamais** credencial write. Sentinel é fonte de verdade operacional — qualquer bug no export que crie um `UPDATE` ou `DELETE` é catastrófico.
>
> Dara pode criar o role `sentinel_ro` com `GRANT SELECT ON trades TO sentinel_ro` e **nada mais**. Password vai em `.env.vespera` gitignored.
>
> Também: hash do parquet exportado assinado cryptographicamente no spec + autor + timestamp. Se alguém regenerar o dataset fora desse fluxo e tentar usar, a assinatura não bate e o CPCV runner recusa. R10-style fail-closed."

---

## Turno 9 — Nova (@market-microstructure) — alinhamento com tese

> "Concordo com o slim de 3 colunas pro export **se** aggressor_side não entrar no feature set. Reverificando spec YAML feature_set:
>
> ```
> intraday_flow_direction = sign(close[t] - open_day)
> intraday_flow_magnitude = |close - open_day| / ATR_20d
> atr_day_ratio           = ATR_day / ATR_20d
> ```
>
> Zero dependência de aggressor, book, ou agent id. Slim 3 colunas é suficiente. Mas **registro ressalva**: se uma tese futura (T003?) quiser `aggressor_imbalance` ou `smart_money_participation`, vai precisar re-export com mais colunas. Isso está OK — parquet é por-estratégia, não tenta ser single-source universal. Vespera = T002 + suas futuras iterações; outras teses geram outros parquets.
>
> Uma adição: **calendário precisa estar congelado junto**. Se `config/calendar/2024-2027.yaml` mudar depois da assinatura do spec, filtros pós-Copom/rollover mudam, features mudam, backtest muda. Hash do calendar YAML também entra na assinatura Mira."

---

## Turno 10 — Quinn (@qa) — contract tests

> "Três acceptance criteria que quero na story T002.0:
>
> 1. **Hash determinismo**: rodar `export_wdo_parquet.py` duas vezes consecutivas deve produzir hash sha256 idêntico. Senão o pipeline não é determinístico (timestamps sort stability, float precision, etc).
> 2. **Schema contract**: `ParquetTradesReplay` valida dtype exato no abrir do arquivo — se alguém recomprimiu ou reconverteu o parquet e mudou `qty` de int32 pra int64, recusa com erro claro.
> 3. **Hold-out lock**: `ParquetTradesReplay` carregado com path do hold-out dispara RuntimeError sólido salvo ambiente variable `VESPERA_UNLOCK_HOLDOUT=true`. Mira pediu, eu implemento o teste que valida."

---

## Turno 11 — Pax (@po) — escopo da story

> "Compilando as decisões: T002.0 é uma story só, não um epic. Escopo:
>
> - `scripts/export_wdo_parquet.py` (Nelo + Dara implementam — Nelo conhece Sentinel, Dara conhece pyarrow)
> - `packages/t002_eod_unwind/adapters/feed_parquet.py` (Dex implementa, contrato idêntico a HistoricalTradesReplay)
> - `data/` no .gitignore (já está? conferir)
> - Atualização spec YAML: adicionar `dataset_in_sample_sha256`, `dataset_hold_out_sha256`, `calendar_sha256` — INVALIDA a assinatura atual de Mira. Mira re-assina.
> - `data/manifest.csv` produzido junto pelo script de export (pedido Mira)
> - Contract tests de Quinn
>
> **Estimativa:** 1-2 sessões de trabalho (humano↔squad).
>
> **Bloqueia:** Fase E (CPCV).
>
> **Depende:** Sentinel ter o backfill em curso suficientemente avançado — se ainda falta gap 2024-01 → 2024-06, bloqueia. Verificar antes.
>
> **Kill criteria:** não aplicável (plumbing). Se export estourar RAM ou demorar >30min, refactor pra streaming write."

---

## Decisões finais

| Decisão | Escolha | Justificativa |
|---|---|---|
| Storage format | Parquet + zstd nível 3 | Beckett perf, Dara tooling |
| Schema | `ts:timestamp[us]`, `price:float64`, `qty:int32` — slim 3 colunas | Nova confirmou feature set não depende do resto; R7 |
| Partition | `year=YYYY/month=MM/` | Dara: rollover alinha com month boundary; CPCV slice é push-down |
| Versioning | sha256 hash por parquet + hash do calendar, anotados no spec YAML | Mira + Sable Popperian reprodutibilidade |
| Onde viver | `data/` gitignored **(Opção A de Sable)** | Custo zero; migrar pra S3/R2 se for produção |
| Separação treino/holdout | **2 parquets físicos distintos**, unlock hold-out via env var | Mira: leakage prevention |
| Export tool | `scripts/export_wdo_parquet.py` (throwaway) | Aria: scripts vs packages boundary |
| Reader | `packages/t002_eod_unwind/adapters/feed_parquet.py` (produção) | Aria: contrato layer 1 |
| Docker Vespera | **NÃO** agora; só quando for live (Fase H) | Aria: fricção sem ganho |
| Credencial Sentinel | role `sentinel_ro` SELECT-only; password em `.env.vespera` gitignored | Riven: fail-closed custodial |
| Manifest CSV | `data/manifest.csv` produzido junto | Mira: sample balance visibility |
| DuckDB | opcional, Mira EDA | Beckett: parquet puro é hot-path |

---

## Owners T002.0 (REVISADO)

| Sub-tarefa | Owner | Consultor |
|---|---|---|
| Role `sentinel_ro` no TimescaleDB | Dara | Riven (custodial) |
| `packages/.../adapters/feed_timescale.py` | Dex | Dara (SQL), Nova (schema alignment) |
| `packages/.../adapters/feed_parquet.py` | Dex | Aria (contract), Beckett (perf) |
| `scripts/materialize_parquet.py` | Dara | Nelo (schema knowledge), Sable (hash protocol) |
| **Warm-up decision (P252 → P_N)** | **Mira** | Beckett (CPCV impact), Sable (spec re-sign) |
| Spec YAML update (+3 hash fields + P_N, re-assinar) | Mira | Sable |
| Contract tests | Quinn | Dex |
| Pré-requisito: docker up + role criada (substitui "backfill check") | Dara | Riven |

---

## Gate (REVISADO)

**Entrada Fase E depende de:**

- [ ] Snapshot `sentinel-timescaledb` legível via role `sentinel_ro` (substitui "backfill cobre 2024-01→2026-04" — dataset já existe congelado)
- [ ] `packages/t002_eod_unwind/adapters/feed_timescale.py` existe + testado (carrega WDO slim 3-col BRT naive)
- [ ] `packages/t002_eod_unwind/adapters/feed_parquet.py` existe + testado (memory-map, schema estrito)
- [ ] `scripts/materialize_parquet.py` existe (DB→parquet on-demand, determinístico)
- [ ] Parquet in-sample materializado + hash anotado (materializável via script; export antecipado opcional)
- [ ] Parquet hold-out materializado + hash anotado + lock `VESPERA_UNLOCK_HOLDOUT`
- [ ] Calendar YAML hash anotado
- [ ] **Warm-up decision Mira:** P252 → P_N ajustado (decisão entre opção a/b/c acima) + re-assinatura spec
- [ ] Mira re-assina spec com hashes (in_sample + hold_out + calendar)
- [ ] Pax valida story T002.0 (10-point)
- [ ] Quinn contract tests passam (determinismo, schema, hold-out lock)

**Assinatura council:**
Orion (@aiox-master), Nelo, Nova, Dara, Mira, Beckett, Riven, Aria, Quinn, Sable, Pax — 2026-04-21 BRT.
**Addendum + Gate revisão:** Orion — 2026-04-21 BRT pós-inspeção docker+data.
