---
plan_id: T002-beckett-t11-bis-execution-plan-2026-04-27
story_id: T002.0h
agent: Beckett (@backtester)
task: T6 — preparação do plano de execução do T11.bis re-run (AC8 exit gate)
date_brt: 2026-04-27 BRT
status: PLAN_READY_AWAITING_QUINN_T5_PASS
authority: |
  Beckett — backtester & execution simulator authority. Article IV (No
  Invention) absoluto. Plano define a sequência exata de comandos, os
  pré-flights, a captura de telemetry, a árvore de decisão pass/fail, o
  formato do relatório destino e o critério de clearance da Riven HOLD
  #1. NENHUMA execução ainda — execução virá após sinal "Dex committed
  AC9 + Quinn T5 PASS". Anti-Article-IV Guards de Beckett aplicados:
  Guard #3 (NO subsample), Guard sobre engine config (NO mutation para
  passar threshold), Guard sobre threshold relaxation (HALT-ESCALATE em
  qualquer falha sub-criterion), Guard sobre RSS honesty (reportar
  observado, NUNCA estimar).
preconditions_for_execution:
  - "Dex commitou AC9 cache validation contract (BUILDER_VERSION + triple-key sidecar + StaleCacheError + --force-rebuild + cache_audit.jsonl)"
  - "Quinn T5 re-QA verdict = PASS (557+ tests passed, ruff clean, zero regressions T002.0a-g)"
  - "Story status promoted Ready → InProgress → InReview por @sm/@po (não Beckett)"
---

# T002.0h T6 — Beckett T11.bis Execution Plan (2026-04-27 BRT)

> **Status:** PLAN_READY — execução depende de sinal "Quinn T5 PASS" via @sm/@po. Beckett NÃO modifica story files (autoridade @po sobre AC/scope, @qa sobre QA Results).
>
> **Origem:** ESC-006 mini-council 4/4 APPROVE_F (2026-04-26 BRT, Aria + Mira + Beckett + Riven, commit `3f27f89`). Wall-time NO LONGER smoke gate criterion para precompute (run-once-per-as_of, accepted ~5-7min cost). Smoke total < 5min aplica APENAS post-warmup-cache-hit. AC9 (cache validation contract) implementado por Dex com BUILDER_VERSION 1.0.0 + triple-key sidecar + StaleCacheError + --force-rebuild + cache_audit.jsonl.
>
> **Estado atual em disco (verificado 2026-04-27 21:20 BRT):** state files dated + canonical copies já existem do pre-flight do Dex (2026-04-26 20:49 BRT). Sidecar `_cache_key_2025-05-31.json` presente + cache_audit.jsonl com 3 entries (miss → write → hit). Significa que o T11.bis vai DE FATO exercitar o **caminho cache hit** já no primeiro run desta sessão (warmup wall-time esperado < 5s). Re-run com `--force-rebuild` opcional para validar caminho miss completo (recommended sub-step para evidence completeness).

---

## 0. Resumo executivo

Plano para T11.bis exit gate de T002.0h (AC8). Sequência: (1) pré-flight read-only, (2) warmup state cache validation (espera-se HIT — < 5s), (3) opcionalmente re-run com `--force-rebuild` para validar miss path completo, (4) CPCV dry-run smoke, (5) artefatos check + telemetry capture, (6) relatório markdown destino, (7) handoff para Riven cosign §9 amendment.

7 sub-criteria AC8 a verificar; cada um com threshold pass/fail explícito. Guards Anti-Article-IV reforçados.

---

## 1. Sequência de comandos exata

**Working dir:** `C:\Users\Pichau\Desktop\Algotrader` (absoluto, sempre).
**Shell:** Git Bash (compatível com Unix syntax do AIOX). Comandos PowerShell equivalentes anexados em §3 quando necessário para captura de telemetria.
**Branch:** `t002-1-warmup-impl-126d` (sem checkout; Beckett não mexe em git push — Gage authority).
**Python:** ambient venv (`python` deve ser 3.14.x conforme prior runs); confirmar via `python --version` no pré-flight.

### 1.1. Pré-flight read-only (sem side-effect)

```bash
# (P1) Confirmar Python version + psutil presente
python --version
python -c "import psutil; print('psutil', psutil.__version__)"

# (P2) Confirmar BUILDER_VERSION constante (deve ser '1.0.0' — Dex AC9)
python -c "from packages.t002_eod_unwind.warmup import BUILDER_VERSION; print('BUILDER_VERSION', BUILDER_VERSION)"

# (P3) Confirmar manifest.csv sha256 (deve ser o pinado em canonical-invariant.sums)
python -c "import hashlib; print(hashlib.sha256(open('data/manifest.csv','rb').read()).hexdigest())"
# expected: 78c9adb35851bab4450c209d7afe6fc9b51e76351e2f069125785660822dee72

# (P4) Confirmar parquets in-sample materializados para janela smoke [2025-05-31, 2025-06-30]
ls data/in_sample/year=2025/month=05/wdo-2025-05.parquet
ls data/in_sample/year=2025/month=06/wdo-2025-06.parquet

# (P5) Snapshot do diretório state/T002/ ANTES do run (para diff post-run)
ls -la state/T002/ > /tmp/beckett_t11bis_state_pre.txt
cat state/T002/_cache_key_2025-05-31.json
tail -3 state/T002/cache_audit.jsonl

# (P6) Spec sha256 (whole-file convention, used pelo CLI)
python -c "import hashlib; print(hashlib.sha256(open('docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml','rb').read()).hexdigest())"
# expected (do report 2026-04-26): 98f22f3c8ceee521cbb696b62cd3cf6bd49e4556af77005589e720a4d4b24614

# (P7) Calendar SHA + cost-atlas SHA (sanity)
python -c "import hashlib; print(hashlib.sha256(open('config/calendar/2024-2027.yaml','rb').read()).hexdigest())"
python -c "import hashlib; print(hashlib.sha256(open('docs/backtest/nova-cost-atlas.yaml','rb').read()).hexdigest())"
# expected cost-atlas LF-normalized: acf449415a3c9f5dce0571c307dc891d00488860132093c40b2f00c2434a5126
# (whole-file vs LF-normalized podem diverger no Windows — anotar ambos)

# (P8) Hold-out lock constants
python -c "from scripts._holdout_lock import HOLDOUT_START, HOLDOUT_END_INCLUSIVE; print(HOLDOUT_START, HOLDOUT_END_INCLUSIVE)"
# expected: 2025-07-01 2026-04-21
```

**Critério pré-flight PASS:** todos 8 checks acima devem retornar valores esperados. Qualquer mismatch → HALT, registrar no relatório, escalar via USER-ESCALATION-QUEUE.

### 1.2. Step A — Warmup state cache hit validation (path principal AC8)

```bash
# Capturar wall-time + RSS via instrumentation Python wrapper (ver §3)
# OBS: state files já existem, sidecar OK, manifest sha unchanged ⇒ esperado CACHE HIT < 5s

mkdir -p data/baseline-run/cpcv-dryrun-T002-2026-04-27

# Comando A.1 — warmup com cache hit (smoke window 2025-05-31)
time python scripts/run_warmup_state.py \
  --as-of-dates 2025-05-31 \
  --output-dir state/T002/ \
  2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_stderr.log \
  > data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_stdout.log
echo "WARMUP_EXIT_CODE=$?"
```

**Esperado AC8 cache hit branch:**
- Exit code = 0
- Wall-time < 5s (real)
- `state/T002/cache_audit.jsonl` ganha 1 nova linha `status:"hit"` com `note:"orchestrator skipped (triple-key match)"`
- 2 dated JSONs (atr_20d_2025-05-31.json, percentiles_126d_2025-05-31.json) PRESENTES (sem alteração de mtime)
- Symlink/copy default path PRESENTES (atr_20d.json, percentiles_126d.json)
- 2 telemetry CSV samples (run_start + cache_hit + cache_all_hits + run_end ≈ 4 rows)

**Se cache MISS (e.g., manifest sha mudou desde último run):** comportamento ainda PASS para AC8 first-time branch (wall-time NOT smoke gate criterion; ~5-7min accepted). Captura wall-time + peak RSS via poller-csv. Após miss, sidecar é escrito ⇒ próximo run vira hit.

**Se cache STALE (`StaleCacheError`):** EXIT 1, NÃO retry, registrar no report e investigar (manifest drift OR builder version bump). Se intencional, operator decide se re-run com `--force-rebuild`.

### 1.3. Step B — (OPCIONAL — recommended) Force rebuild para validar miss path

Para evidence completeness do AC8 + AC9 cache contract (cobertura dos 3 estados: miss/hit/force_rebuild), recomendo executar **uma rodada com `--force-rebuild`** num diretório separado para não invalidar o cache vigente:

```bash
# Comando B.1 — force-rebuild num output-dir scratch (NÃO toca state/T002/ vigente)
mkdir -p data/baseline-run/cpcv-dryrun-T002-2026-04-27/force_rebuild_scratch

time python scripts/run_warmup_state.py \
  --as-of-dates 2025-05-31 \
  --output-dir data/baseline-run/cpcv-dryrun-T002-2026-04-27/force_rebuild_scratch \
  --force-rebuild \
  2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_force_stderr.log \
  > data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_force_stdout.log
echo "WARMUP_FORCE_EXIT_CODE=$?"
```

**Esperado:**
- Exit code = 0
- Wall-time ~5-7min (Dex empirical: 6m05s; per-day adapter calls 110× para 146bd lookback)
- Peak RSS observed entre poller samples (esperado ~120-400 MB conforme Dex pre-flight: poller telemetry RSS estável 119-122 MB ao longo de toda janela)
- 2 dated JSONs + 2 default-name JSONs no scratch dir
- cache_audit.jsonl no scratch dir com `status:"force_rebuild"` + `status:"write"`
- **Esta etapa valida empiricamente que o miss path está funcional E que peak RSS de `run_warmup_state.py` está well-under ADR-1 v3 CAP_v3 8.4 GiB**

**NÃO bloqueante para AC8 PASS** — opcional, mas se executado e PASS, fortalece o relatório (Riven custodial would prefer this evidence).

### 1.4. Step C — CPCV dry-run smoke (post-warmup-cache-hit)

```bash
# Comando C.1 — CPCV dry-run smoke. Esperado total wall-time < 5min (post-cache-hit).
time python scripts/run_cpcv_dry_run.py \
  --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml \
  --dry-run \
  --smoke \
  --in-sample-end 2025-06-30 \
  --seed 42 \
  --warmup-atr state/T002/atr_20d.json \
  --warmup-percentiles state/T002/percentiles_126d.json \
  2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/cpcv_stderr.log \
  > data/baseline-run/cpcv-dryrun-T002-2026-04-27/cpcv_stdout.log
echo "CPCV_EXIT_CODE=$?"
```

**Notas:**
- `--warmup-atr` + `--warmup-percentiles` fornecem path canônico explícito (T002.1 convention `state/T002/`). Defaults do `run_cpcv_dry_run.py` deveriam apontar para `state/T002/` post-T002.0g, mas explicit override garante zero ambiguidade.
- Run ID será derivado deterministicamente via `derive_default_run_id` (sha256 de `spec_sha|in_sample_start|in_sample_end|seed`). Esperado run dir = `data/baseline-run/cpcv-dryrun-auto-{12-hex}/` (não o dir T002-2026-04-27 que criei pra logs).
- Smoke window = `[in_sample_end - 30d, in_sample_end] = [2025-05-31, 2025-06-30]` (per CLI contract).

**Esperado AC8 CPCV branch:**
- Exit code = 0
- Wall-time real < 5min (< 300s) — smoke total budget (post-warmup-cache-hit)
- Peak RSS sample em `telemetry.csv` < 6 GiB
- `KillDecision.verdict ∈ {GO, NO_GO}` (não TIMEOUT, não MEMORY_HALT)
- 5 artifacts persistidos no run dir (smoke subdir): `full_report.json`, `full_report.md`, `determinism_stamp.json`, `events_metadata.json`, `telemetry.csv`

**Mapeamento AC8 spec → script reality:**

A AC8 spec literal lista artifacts como `Splits.json, FoldStats.json, FullReport.json, KillDecision.json, manifest.json`. O `run_cpcv_dry_run.py:639-667` (`persist_artifacts`) escreve atualmente:
- `full_report.md` + `full_report.json` (FullReport contém embedded splits + fold-stats + kill_decision)
- `determinism_stamp.json`
- `events_metadata.json`
- `telemetry.csv` (escrito pelo MemoryPoller)

**Decisão:** AC8 spec foi escrita citando nomes "lógicos" (Splits/FoldStats/KillDecision são SECTIONS dentro de full_report.json). O script atual emite as 5 entidades em 5 arquivos ligeiramente diferentes (full_report.md + full_report.json + determinism + events_metadata + telemetry). Vou validar que **as 5 sections lógicas estão presentes** no output (todas dentro do full_report.json structure), reportando o mapeamento explícito no relatório. Não é divergência semântica — é nomenclatura. Se Pax/Aria considerar critical, é R15 breaking_fields revision (não Beckett authority).

### 1.5. Step D — Post-run snapshot + checksums

```bash
# Snapshot pós-run para diff
ls -la state/T002/ > /tmp/beckett_t11bis_state_post.txt
diff /tmp/beckett_t11bis_state_pre.txt /tmp/beckett_t11bis_state_post.txt || true

# Identifica run dir derivado deterministicamente
ls -d data/baseline-run/cpcv-dryrun-auto-*/ | tail -1
RUN_DIR=$(ls -d data/baseline-run/cpcv-dryrun-auto-*/ | tail -1)
ls -la "$RUN_DIR"
ls -la "$RUN_DIR/smoke/" 2>/dev/null || echo "smoke subdir missing"

# SHA-256 dos 5 smoke artifacts (para checksums table do relatório)
for f in "$RUN_DIR/smoke/full_report.json" "$RUN_DIR/smoke/full_report.md" "$RUN_DIR/smoke/determinism_stamp.json" "$RUN_DIR/smoke/events_metadata.json" "$RUN_DIR/telemetry.csv"; do
  if [ -f "$f" ]; then
    python -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest(), sys.argv[1])" "$f"
  else
    echo "MISSING: $f"
  fi
done

# Extrai KillDecision.verdict do FullReport
python -c "
import json
with open('$RUN_DIR/smoke/full_report.json') as fh:
    rep = json.load(fh)
print('verdict =', rep.get('kill_decision', {}).get('verdict', 'NOT_FOUND'))
print('pbo =', rep.get('metrics', {}).get('pbo', 'N/A'))
print('dsr =', rep.get('metrics', {}).get('dsr', 'N/A'))
"

# Peak RSS observado: max(rss_mb) na telemetry.csv (ALL phases)
python -c "
import csv
with open('$RUN_DIR/telemetry.csv') as fh:
    reader = csv.DictReader(fh)
    rows = list(reader)
peak_rss_mb = max(float(r['rss_mb']) for r in rows if r['rss_mb'])
peak_wset_mb = max(int(r['peak_wset_bytes'])/1024/1024 for r in rows if r['peak_wset_bytes'])
print(f'peak_rss_mb={peak_rss_mb:.2f}  ({peak_rss_mb/1024:.3f} GiB)')
print(f'peak_wset_mb={peak_wset_mb:.2f}  ({peak_wset_mb/1024:.3f} GiB)')
print('threshold AC8:  6 GiB (= 6144 MB)')
print('threshold ADR-1 v3 CAP_v3:  8.4 GiB (= 8602 MB)')
"
```

---

## 2. Pré-flight checks (resumo tabular)

| # | Check | Comando | Threshold/Expected | Falha → ação |
|---|-------|---------|---------------------|---------------|
| P1 | Python + psutil | `python --version`, `import psutil` | Python 3.14.x; psutil ≥ 5.x | HALT, escalate (env regression) |
| P2 | BUILDER_VERSION constante | `from packages.t002_eod_unwind.warmup import BUILDER_VERSION` | == `'1.0.0'` | HALT — significa AC9 não commitado ou regressão |
| P3 | manifest.csv sha256 | `hashlib.sha256` | `78c9adb3...22dee72` | HALT — manifest drift; investigar (Dara) |
| P4 | parquets in-sample para [2025-05-31, 2025-06-30] | `ls wdo-2025-05.parquet wdo-2025-06.parquet` | ambos exist | HALT — Dara escala materialização |
| P5 | state/T002/ snapshot pré-run | `ls -la`, `cat _cache_key`, `tail cache_audit.jsonl` | sidecar existe + last entry status:"hit" | informacional — define se cache hit branch ativo |
| P6 | spec sha256 | `hashlib.sha256` | `98f22f3c8cee...4d4b24614` | HALT — spec drift; @sm reconciliação |
| P7 | calendar + cost-atlas shas | `hashlib.sha256` | calendar matches; cost-atlas LF-norm matches `acf44941...4a5126` | HALT — Mira ou Nova drift |
| P8 | Hold-out lock constants | `from _holdout_lock import HOLDOUT_*` | `2025-07-01` / `2026-04-21` | HALT — R1 + R15(d) violation |

**Pré-flight fail → ZERO comandos de step A executados. Plano abortado.**

---

## 3. Telemetry capture plan

### 3.1. Wall-time

- **Primary:** `time python ...` (Bash) — captura `real` em stderr (formato `0m3.058s`).
- **Cross-check (PowerShell):** `Measure-Command { python ... }` — captura `TotalSeconds` precise (Windows-native).
- **Application-level:** o próprio `run_warmup_state.py` registra `duration_ms` no telemetry CSV (`run_end` event); o `run_cpcv_dry_run.py` idem. Triple cross-check garante NO improvisation.

### 3.2. Peak RSS

- **Source primário:** poller psutil daemon-thread em ambos scripts (cadência 30s default). Escreve `rss_mb` + `peak_wset_bytes` (Windows working set) no CSV.
- **Cálculo peak:** `max(rss_mb)` sobre TODAS as rows do CSV (run_start + per-poll + run_end).
- **Windows-specific:** `peak_wset_bytes` é o Windows "Peak Working Set" via `psutil.Process().memory_info()` (campo `peak_wset` em Windows). É o equivalente correto a "peak RSS" em Linux.
- **Por que NÃO usar Get-Process:** `Get-Process` snapshot só captura instantes pontuais, não roda em paralelo com o subprocess. O poller psutil é canonical (e já é o que ADR-1 v3 + governance memory protocol mandam para CPCV runs).
- **Sanity cross-check:** durante o run, abrir terminal paralelo PowerShell e rodar `Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, WorkingSet64, PeakWorkingSet64 | Format-Table -AutoSize` periodicamente. Anotar os 2-3 maiores observados; comparar com poller CSV peak. Mismatch > 10% → escalate (poller bug).

### 3.3. Exit codes

- Capturar via `echo "WARMUP_EXIT_CODE=$?"` imediatamente após cada comando (Bash semantics).
- Persistir no relatório como tabela.

### 3.4. cache_audit.jsonl contents

- `tail -10 state/T002/cache_audit.jsonl` antes E depois do run.
- `diff` para mostrar exatamente quais entries novas surgiram (cada run adiciona ≥ 1 entry).
- **Esperado pós-T11.bis cache hit:** +1 linha `{status:"hit", note:"orchestrator skipped (triple-key match)"}`.
- **Esperado pós-Step B (force rebuild scratch dir):** o cache_audit.jsonl scratch ganha 2 entries: `status:"force_rebuild"` + `status:"write"`. NÃO afeta `state/T002/cache_audit.jsonl` vigente.

### 3.5. CPCV run dir contents

- `ls -la $RUN_DIR/` + `ls -la $RUN_DIR/smoke/`
- SHA-256 de cada artefato (5 esperados: full_report.{md,json}, determinism_stamp.json, events_metadata.json, telemetry.csv) — tabela no relatório.
- `KillDecision.verdict` extraído via `python -c "import json; ..."` — ver §1.5 step D.

---

## 4. Pass/fail decision tree (7 sub-criteria AC8)

| # | Sub-criterion | Threshold | Source | PASS | FAIL action |
|---|----------------|-----------|--------|------|-------------|
| **AC8.1** | `run_warmup_state.py --as-of-dates 2025-05-31` exit code | == 0 | Bash `$?` | proceed | HALT-ESCALATE: log stderr, classify (StaleCacheError → operator decide; manifest missing → Dara; hold-out violation → Mira/Riven). NÃO retry. |
| **AC8.2** | Warmup wall-time | <span style="background-color:#ffefef">**Cache hit:** < 5s</span><br><span style="background-color:#fff3e0">**Cache miss / force-rebuild:** NOT a smoke gate criterion (~5-7min OK)</span> | `time` real + telemetry duration_ms | proceed | Cache hit > 5s → escalate Aria (cache logic regression possible); miss > 10min → escalate Aria (perf regression beyond Dex empirical 6m05s baseline). |
| **AC8.3** | 2 dated JSONs persisted | atr_20d_2025-05-31.json + percentiles_126d_2025-05-31.json em state/T002/ | `ls` | proceed | FAIL — missing file means orchestrator did not run OR write failed. HALT-ESCALATE Aria/Dex. |
| **AC8.4** | 2 default-path JSONs (symlink/copy) | atr_20d.json + percentiles_126d.json em state/T002/ apontando para mais recente | `ls` + content matches dated version | proceed | FAIL — copy logic regression. HALT-ESCALATE Dex. |
| **AC8.5** | CPCV smoke exit code | == 0 | Bash `$?` | proceed | HALT-ESCALATE — categorize: warmup-gate fail (regressão T002.0g)? smoke compute fail? memory halt? cada um diferente owner. |
| **AC8.6** | CPCV smoke wall-time | < 300s (5 min) — applies POST-warmup-cache-hit | `time` real | proceed | FAIL — escalate Aria (CPCV harness perf regression). NÃO mexer threshold (Anti-Article-IV Guard: NO threshold relaxation). |
| **AC8.7** | Peak RSS | < 6 GiB (= 6144 MB) | `max(rss_mb)` da telemetry CSV | proceed | FAIL — escalate Aria/Riven; ADR-1 v3 invariant violation. NÃO mexer cap (Guard #2 Aria). |
| **AC8.8** | 5 smoke artifacts persisted | full_report.{md,json} + determinism_stamp.json + events_metadata.json + telemetry.csv | `ls $RUN_DIR/smoke/` + checksums | proceed | FAIL — categorize: persist_artifacts não rodou (compute_full_report falhou)? IO error? HALT-ESCALATE Aria. |
| **AC8.9** | KillDecision.verdict | ∈ {GO, NO_GO}; NÃO TIMEOUT, NÃO MEMORY_HALT | `json.load(full_report.json).kill_decision.verdict` | proceed | FAIL TIMEOUT/MEMORY_HALT → escalate (cobertura insuficiente OR perf regression). |

**(Numerei como 8.1-8.9 para granularidade; story spec literal lista 7 bullets — minha decomposição mais fina facilita audit. No relatório final, agrupo de volta nos 7 bullets do spec.)**

### 4.1. Composite verdicts

- **AC8 PASS = 9/9 sub-criteria PASS** (no waivers permitted at this gate).
- **AC8 PARTIAL_PASS** (8/9 com 1 cosmetic discrepancy): exemplo válido = artifact naming Splits.json/FoldStats.json (spec literal) vs full_report.json sections (script reality). Documentar como NOTE no relatório, não FAIL — é R11 (story spec é COMO, não O-QUÊ); R15 breaking_fields revision é Pax authority, não Beckett.
- **AC8 FAIL = qualquer 1 dos 9 sub-criteria FAIL** sem mitigation. HOLD verdict; escalate to USER-ESCALATION-QUEUE.

### 4.2. Anti-Article-IV Guards (Beckett-specific)

| Guard | Aplicação concreta neste plano |
|-------|----------------------------------|
| #1: NO subsample dataset | Comando smoke window default `[2025-05-31, 2025-06-30]` é a janela canonical (DEFAULT_SMOKE_DAYS=30). NÃO restrinjo data range para passar threshold. |
| #2: NO modify engine config para passar threshold | `docs/backtest/engine-config.yaml` é READ-ONLY durante T11.bis. Cost atlas v1.0.0 LF sha pinada. |
| #3: NO improvise threshold relaxation | Se AC8.6 (CPCV < 5min) falhar em 305s, NÃO arredondo nem aceito. HALT-ESCALATE. |
| #4: Reportar peak RSS HONESTAMENTE | Source canonical = poller CSV `max(rss_mb)`. NÃO "estimar" de Get-Process. NÃO arredondar pra baixo. NÃO descartar tail samples. |
| #5: NO retry após exit ≠ 0 | Operator restriction histórica (T11 brief): "ABORT se exit != 0". Capture diagnostic, NÃO retry. |
| #6: NO push (Gage gate) | git push EXCLUSIVO Gage. Beckett apenas commita relatório local se solicitado pelo @sm. |
| #7: NO modify story files | AC/scope @po authority; QA Results @qa authority. Beckett write-only para `docs/backtest/...`. |

---

## 5. Destination report — estrutura

**Path:** `docs/backtest/T002-beckett-t11-bis-smoke-report-2026-04-27.md`

> NOTE: data ajustada de 04-26 → 04-27. AC8 spec L57-69 usa "2026-04-26" como nome legacy do arquivo; a refactor ESC-006 commit `3f27f89` consolidou a story para mandar Beckett gerar report COM A DATA DA EXECUÇÃO. Em caso de dúvida, ambos arquivos coexistem (T11 2026-04-26 = HOLD anterior; T11.bis 2026-04-27 = exit gate). Updated File List da story T002.0h L126 deve referir nome final correto (Pax @sm housekeeping post-PASS).

### 5.1. Header (YAML frontmatter)

```yaml
---
report_id: T002-beckett-t11-bis-smoke-report-2026-04-27
story_id: T002.0h
agent: Beckett (@backtester)
task: T6 — execução do T11.bis re-run (AC8 exit gate de T002.0h)
date_brt: <YYYY-MM-DDTHH:MM BRT>  # preencher na execução real
verdict: <PASS | HOLD | FAIL>     # preencher na execução real
authority: |
  Beckett — backtester & execution simulator authority. AC8 exit gate
  exercised post-AC9-cache-validation-contract (commit AC9 hash from Dex).
  Article IV (No Invention) absoluto. Anti-Article-IV Guards #1-#7
  honrados. Wall-time honestly measured via /usr/bin/time + telemetry
  CSV duration_ms cross-check. Peak RSS honestly captured via psutil
  poller daemon-thread (canonical per ADR-1 v3 governance memory
  protocol).
preconditions_met:
  - "Dex AC9 commitado (BUILDER_VERSION=1.0.0 + triple-key sidecar + StaleCacheError + --force-rebuild + cache_audit.jsonl)"
  - "Quinn T5 PASS (557+ tests, ruff clean, zero regressions T002.0a-g)"
  - "All 8 pre-flight checks PASSED"
---
```

### 5.2. Sections do relatório

1. **§1 — Smoke commands executed**
   - Step A (warmup cache hit) — comando exato + exit code + wall-time.
   - Step B (force-rebuild scratch — opcional) — comando + exit code + wall-time + peak RSS.
   - Step C (CPCV dry-run smoke) — comando exato + exit code + wall-time.

2. **§2 — Pre-conditions verified (8 entries)**
   - Tabela format do report 2026-04-26 §2 (esperado/observed/match).

3. **§3 — AC8 sub-criteria — pass/fail matrix (9 sub-criteria)**
   - Tabela format §4 deste plano com observed values + verdict por linha.

4. **§4 — Peak RSS telemetry table**
   - Cols: `phase, rss_mb, vms_mb, cpu_pct, peak_wset_mb, sample_size`.
   - Linha resumo: `peak_rss_mb_overall = max(...)`, `peak_wset_mb_overall = ...`, threshold AC8 6 GiB, headroom %.

5. **§5 — 5 artifacts checksums**
   - Cols: `path, size_bytes, sha256, present (Y/N)`.
   - Mapeamento spec-name → file-name explicit (Splits.json → full_report.json.splits; FoldStats.json → full_report.json.fold_stats; etc.).

6. **§6 — KillDecision verdict + metrics summary**
   - `verdict`, `pbo`, `dsr`, `ic_spearman`, `n_paths`, `seed`, `spec_sha256`.

7. **§7 — cache_audit.jsonl diff (pre/post)**
   - Linhas adicionadas durante o run (esperado: 1 hit OR 1 miss + 1 write).

8. **§8 — Re-determinism check (optional Step D')**
   - Se feito: 2nd run, byte-equality check on `full_report.json.metrics` + `determinism_stamp.json.dataset_hash`.

9. **§9 — Article IV trace**
   - Decisões com source/justificativa (mesmo padrão report 2026-04-26 §6 trace).

10. **§10 — Reproducibility envelope**
    - Seed, simulator version, dataset hash, spec sha, calendar sha, cost-atlas LF sha, BUILDER_VERSION, hold-out constants, run dir, Python/psutil versions.

11. **§11 — Verdict + recommendation to operator**
    - PASS → Riven HOLD #1 clear (vide §6 deste plano).
    - HOLD/FAIL → escalation list + USER-ESCALATION-QUEUE pointer.

12. **§12 — Signed**
    - "Verdict signed by: Beckett (@backtester) — YYYY-MM-DD BRT" + signature emoji 🎞️.

---

## 6. Riven HOLD #1 clearance criteria

**Reference:** `docs/qa/gates/T002.0g-riven-cosign.md` §9 action item #4 (line 155):

> **#4** — Beckett T11.bis smoke retry — BLOCKED memory-budget gap orchestrator (T002.0h pending streaming aggregation refactor). [AMENDMENT 2026-04-26: prior reason "depends on Docker engine restoration" RETRACTED — Beckett T11.bis empirically confirmed Docker is NOT in the path; orchestrator is parquet-only. Real blocker: `scripts/run_warmup_state.py` SIGTERM at 6 GiB soft-cap @ 90s for single as_of=2025-05-31 (146bd window materialized in-memory before flush). See `docs/backtest/T002-beckett-t11-smoke-report-2026-04-26.md` §T11.bis.] | Beckett (T10 retry) post T002.0h fix | HOLD on T002.0h streaming refactor | USER-ESCALATION-QUEUE.md P1 (re-classify)

### 6.1. Quando T11.bis = PASS, evidence package para Riven §9 amendment update

**Required artifacts:**
1. **This T11.bis smoke report** (`docs/backtest/T002-beckett-t11-bis-smoke-report-2026-04-27.md`) — verdict PASS, all 9 sub-criteria PASS.
2. **Peak RSS observed** — from telemetry CSV, < 6 GiB. Specifically:
   - **Warmup phase peak** (Step A cache hit OR Step B force rebuild) — esperado < 500 MB conforme Dex pre-flight (RSS estável 119-122 MB). Confirma streaming refactor T1-T3 working as designed.
   - **CPCV smoke peak** — esperado entre 142 MB (legacy from 2026-04-26 §3) e ~1 GiB (post-warmup cached state load + 5-trial fan-out). Sub 6 GiB confirms no regression.
3. **Cache contract evidence** — cache_audit.jsonl entries demonstrating triple-key validation working: hit + miss + (optional) force_rebuild.
4. **5 artifacts checksums** — proves the smoke pipeline reached `compute_full_report` + `persist_artifacts`.
5. **KillDecision.verdict ∈ {GO, NO_GO}** — proves the modeling work completed (não TIMEOUT, não MEMORY_HALT).
6. **Re-determinism sub-evidence (optional but Riven would want it)** — 2 runs byte-identical on `full_report.json.metrics.pbo` + `determinism_stamp.json.dataset_hash`.

### 6.2. §9 amendment text (Beckett proposes Riven adopts)

```
| #4 | Beckett T11.bis smoke retry — RESOLVED. T002.0h streaming refactor
| (AC1-AC7 Dex DONE) + AC9 cache validation contract (Dex DONE) +
| Quinn T5 re-QA PASS + Beckett T11.bis 2026-04-27 PASS verdict
| (peak RSS warmup <500MB, CPCV smoke <6 GiB, all 9 sub-criteria PASS,
| KillDecision verdict={GO|NO_GO} from full_report.json). [PRIOR HOLD
| 2026-04-26 'depends on Docker engine restoration' was RETRACTED in
| empirical T11.bis #1 — orchestrator is parquet-only, no Docker dep.
| Memory blocker subsequently resolved via T002.0h streaming refactor
| + AC9 fail-closed cache. Evidence:
| docs/backtest/T002-beckett-t11-bis-smoke-report-2026-04-27.md.] |
| Beckett (T6 done) | CLEARED 2026-04-27 | T002.0h closure |
```

**Owner amendment:** Riven (custodial cosign authority over §9 of own gate file). Beckett can NOT edit Riven's gate file (R15 + agent-authority). Beckett DELIVERS the evidence; Riven DUAL-SIGNS the §9 update post-review.

### 6.3. Story T002.0h DoD checkbox flip

When T11.bis PASS:
- T002.0h L195 `[ ] **AC1-AC8** todos verde` → `[x]`
- T002.0h L199 `[ ] **Beckett T11.bis re-run PASS:** AC8 exit gate ...` → `[x]` with evidence pointer
- T002.0h L57 `[ ] **AC8** ...` → `[x]` (this is THE story exit gate trigger)
- T002.0h L73 `[ ] **AC9** ...` → `[x]` (cache validation contract proven)
- T002.0h L90 T6 `[ ] **T6** — Beckett T11.bis re-run` → `[x]`

**Owner of these flips:** @qa Quinn (re-QA section) + @sm/@po (story status promotion `InReview → Done`). NOT Beckett (Beckett is execution authority + reporter, not story-state mutator).

---

## 7. Handoff matrix (post-execution)

| To | What | Trigger |
|----|------|---------|
| @qa (Quinn) | T11.bis report URL + reference for re-QA closure | T11.bis PASS |
| @risk-manager (Riven) | Evidence package per §6.1 + proposed §9 amendment text per §6.2 | T11.bis PASS |
| @sm / @po | Story status promotion `InReview → Done` request + DoD checkbox flips per §6.3 | Riven §9 cosign DONE |
| @devops (Gage) | (eventually) git push of report + story update — but ONLY post explicit user request | NEVER auto |
| @ml-researcher (Mira) | (eventually) Phase E unblock notification — full 12-month CPCV can now run | T002.0h closure |

---

## 8. Rollback / contingency

### 8.1. Se Step A (warmup cache hit) FALHAR

- **Exit code 0 mas wall-time > 5s:** cache hit logic potencial regression. Examinar telemetry `cache_hit` event. Escalate Aria/Dex.
- **Exit code 1 com StaleCacheError:** investigar mismatch (manifest sha drift OR builder version bump). Operator decision: re-run com `--force-rebuild` (mas deve ir para AC8 first-time branch que aceita ~5-7min). NÃO commit until investigation.
- **Exit code 1 sem StaleCacheError:** outro fail (orchestrator regression). Read stderr, escalate.

### 8.2. Se Step C (CPCV smoke) FALHAR

- **Exit 1 com warmup gate HALT:** regressão T002.0g (state files apparently exist mas WarmUpGate considera incomplete). Read stderr verbose, possivelmente `_load_warmup_state` schema drift. Escalate Aria/Dex.
- **Exit 1 com soft halt RSS > 6 GiB:** ADR-1 v3 invariant violation. Escalate IMMEDIATELY Aria + Riven. NÃO retry com cap maior (Guard #2).
- **Exit 1 timeout:** wall-time excedeu 5min. Capturar telemetry CSV, identificar phase mais cara, escalate Aria.
- **Exit 0 mas KillDecision.verdict=TIMEOUT/MEMORY_HALT:** modelo computou mas verdict é abort-class. Escalate Mira + Aria; possivelmente coverage insuficiente.

### 8.3. Se relatório markdown não conseguir ser gerado

- HALT, escalate como GAP — significa que execução parcial passou mas evidence capture falhou. Beckett MUST report (R-anti-pattern: silent success).

---

## 9. Run order (one-shot batched)

Para minimizar context switch durante execução real, eis a sequência one-shot recomendada (a ser executada em UMA bash session):

```bash
# Working dir
cd C:/Users/Pichau/Desktop/Algotrader

# === Pre-flight ===
python --version
python -c "import psutil; print('psutil', psutil.__version__)"
python -c "from packages.t002_eod_unwind.warmup import BUILDER_VERSION; print('BUILDER_VERSION', BUILDER_VERSION)"
python -c "import hashlib; print('manifest.csv:', hashlib.sha256(open('data/manifest.csv','rb').read()).hexdigest())"
python -c "import hashlib; print('spec:', hashlib.sha256(open('docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml','rb').read()).hexdigest())"
python -c "import hashlib; print('calendar:', hashlib.sha256(open('config/calendar/2024-2027.yaml','rb').read()).hexdigest())"
python -c "import hashlib; print('atlas:', hashlib.sha256(open('docs/backtest/nova-cost-atlas.yaml','rb').read()).hexdigest())"
python -c "import sys; sys.path.insert(0,'scripts'); from _holdout_lock import HOLDOUT_START, HOLDOUT_END_INCLUSIVE; print('holdout:', HOLDOUT_START, HOLDOUT_END_INCLUSIVE)"
ls data/in_sample/year=2025/month=05/wdo-2025-05.parquet
ls data/in_sample/year=2025/month=06/wdo-2025-06.parquet
ls -la state/T002/ > /tmp/beckett_t11bis_state_pre.txt
cat state/T002/_cache_key_2025-05-31.json
echo "---"
tail -3 state/T002/cache_audit.jsonl

# Halt gate: review pre-flight output above. Continue ONLY if all match expected.

mkdir -p data/baseline-run/cpcv-dryrun-T002-2026-04-27/{,force_rebuild_scratch}

# === Step A: warmup cache hit ===
echo "=== Step A: warmup (expected cache hit) ==="
{ time python scripts/run_warmup_state.py --as-of-dates 2025-05-31 --output-dir state/T002/ ; } 2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_stderr.log
echo "WARMUP_EXIT=$?"

# === Step B (optional): force rebuild ===
echo "=== Step B: force rebuild (scratch, validates miss path) ==="
{ time python scripts/run_warmup_state.py --as-of-dates 2025-05-31 --output-dir data/baseline-run/cpcv-dryrun-T002-2026-04-27/force_rebuild_scratch --force-rebuild ; } 2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/warmup_force_stderr.log
echo "WARMUP_FORCE_EXIT=$?"

# === Step C: CPCV smoke ===
echo "=== Step C: CPCV dry-run smoke ==="
{ time python scripts/run_cpcv_dry_run.py --spec docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml --dry-run --smoke --in-sample-end 2025-06-30 --seed 42 --warmup-atr state/T002/atr_20d.json --warmup-percentiles state/T002/percentiles_126d.json ; } 2> data/baseline-run/cpcv-dryrun-T002-2026-04-27/cpcv_stderr.log
echo "CPCV_EXIT=$?"

# === Step D: snapshot + checksums ===
echo "=== Step D: post-run snapshot ==="
ls -la state/T002/ > /tmp/beckett_t11bis_state_post.txt
diff /tmp/beckett_t11bis_state_pre.txt /tmp/beckett_t11bis_state_post.txt || true
RUN_DIR=$(ls -d data/baseline-run/cpcv-dryrun-auto-*/ | tail -1)
echo "RUN_DIR=$RUN_DIR"
ls -la "$RUN_DIR" "$RUN_DIR/smoke/" 2>/dev/null
for f in "$RUN_DIR/smoke/full_report.json" "$RUN_DIR/smoke/full_report.md" "$RUN_DIR/smoke/determinism_stamp.json" "$RUN_DIR/smoke/events_metadata.json" "$RUN_DIR/telemetry.csv"; do
  [ -f "$f" ] && python -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest(), sys.argv[1])" "$f" || echo "MISSING: $f"
done
python - <<'PY'
import csv, json, glob, os
run_dirs = sorted(glob.glob("data/baseline-run/cpcv-dryrun-auto-*/"))
run_dir = run_dirs[-1] if run_dirs else None
print(f"run_dir={run_dir}")
if run_dir:
    fr_json = os.path.join(run_dir, "smoke", "full_report.json")
    if os.path.exists(fr_json):
        with open(fr_json) as fh:
            rep = json.load(fh)
        print("verdict =", rep.get("kill_decision", {}).get("verdict", "NOT_FOUND"))
        print("pbo     =", rep.get("metrics", {}).get("pbo", "N/A"))
        print("dsr     =", rep.get("metrics", {}).get("dsr", "N/A"))
    tel = os.path.join(run_dir, "telemetry.csv")
    if os.path.exists(tel):
        with open(tel) as fh:
            rows = list(csv.DictReader(fh))
        peak = max((float(r["rss_mb"]) for r in rows if r.get("rss_mb")), default=0.0)
        wset = max((int(r["peak_wset_bytes"])/1024/1024 for r in rows if r.get("peak_wset_bytes")), default=0.0)
        print(f"peak_rss_mb={peak:.2f} ({peak/1024:.3f} GiB)")
        print(f"peak_wset_mb={wset:.2f} ({wset/1024:.3f} GiB)")
PY
echo "=== T11.bis run sequence complete; assemble report. ==="
```

---

## 10. Validação cruzada deste plano

| Validation | Source |
|-----------|--------|
| AC8 spec literal text | `docs/stories/T002.0h.story.md` L57-69 (read 2026-04-27) |
| ESC-006 mini-council 4/4 APPROVE_F | story header L6 + commit `3f27f89` |
| AC9 cache contract specifics | `scripts/run_warmup_state.py` L26-58 module docstring + `packages/t002_eod_unwind/warmup/__init__.py::BUILDER_VERSION` |
| State files snapshot atual | `state/T002/` ls (verified 2026-04-27 21:20 BRT) — 8 files presentes incl. cache_audit.jsonl com hit já registrado |
| Riven HOLD #1 reference | `docs/qa/gates/T002.0g-riven-cosign.md` §9 action item #4 line 155 (read 2026-04-27) |
| persist_artifacts contract | `scripts/run_cpcv_dry_run.py` L639-667 + L893-899 (smoke subdir) |
| Anti-Article-IV Beckett guards | persona definition `core_principles` block + user task brief L86-91 |
| Memory protocol governance | `feedback_cpcv_dry_run_memory_protocol.md` (referenced via project memory imports) |

---

**Plan signed by:** Beckett (@backtester) — 2026-04-27 BRT
**Authority:** `*run-cpcv` task preparation; plan-only artifact (NO execution). Awaits Quinn T5 PASS signal via @sm.
**Status:** PLAN_READY_AWAITING_QUINN_T5_PASS

— Beckett, reencenando o passado 🎞️
