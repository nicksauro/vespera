# Story R15 — Canonical invariant git-tracking hardening (RA-20260428-1 Decision 7)

**Epic:** EPIC-T002 — Vespera end-of-day inventory unwind (WDO) / ADR-4 pre-cache layer §14 follow-up
**Story ID:** R15-canonical-invariant-hardening (governance/hardening story — descriptive slug in lieu of numeric epic.story.N)
**Status:** Draft
**Owner (Dev):** Dex (@dev)
**Canonical-producer custodian:** Dara (@data-engineer)
**R15 sentinel co-sign:** Riven (@risk-manager)
**QA gate:** Quinn (@qa)
**Push / merge authority (R12):** Gage (@devops)
**Story-level co-sign (mandatory, tri-signature):** `@data-engineer + @dev + @risk-manager-cosign`
**Spec ref / origin authority:** RA-20260428-1 Stage-2 (issued 2026-04-24T21:36:22Z), **Decision 7** in the Decision Matrix block of `docs/architecture/memory-budget.md` (RA-28-1) — text anchor: "data/manifest.csv + core/memory_budget.py untracked in git — flagged by Gage during T002.4 merge ... Morgan opens new story under standing authority ... story AC MUST include: add both files to git with a baseline commit establishing the current sha as the tracked state, verify pre/post sha equality, R15 co-sign at QA-gate."
**Anomaly discovery authority:** Gage (@devops) observation during T002.4 merge — main commit `5a52ddd6b1e710d830977b08be832850a6697842` (2026-04-24)
**Manifest write-semantics authority (unchanged by this story):** MWF-20260422-1 (append-only + flag + custodial co-sign contract; remains authoritative for ALL future manifest mutations)
**Canonical sha pins (verified byte-identical at story authorship):**
- `data/manifest.csv` → `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`
- `core/memory_budget.py` → `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d`

> **Pin reconciliation footnote (Morgan, @pm, Pax Rec 1):** the `core/memory_budget.py` pin `1d6ed849...f9287d` reflects the file state **post-RA-20260428-1 Decision 3 step-7 CEILING_BYTES populate** (Dex commit `327d1990` on branch `ra-28-1/step-7-ceiling-populate`, with `CEILING_BYTES = 615_861_044` populated). The story was originally authored against the pre-populate sha `51972c52...91a0ac` (where `CEILING_BYTES = None`); this pin update preserves Dex's step-7 work instead of undoing it. **If Dex picks up this story BEFORE step-7 populate lands on `main`, T1.1 HALT will fire** — in that case, re-issue the pin from `main` HEAD of `core/memory_budget.py` at T1 execution time and document the reconciliation in the Change log.

**Estimate:** 2–4 h wall clock (procedural; no new production code). Breakdown: Dex ~1–2 h (git add + hook sketch + `.gitignore` audit), Dara ~0.5 h (custodial diff review + co-sign), Riven ~0.5 h (R15 sentinel co-sign), Quinn ~0.5 h (gate).
**Blocking:** NONE — runs in parallel with RA-28-1 Decision 3 / step-7 populate work. No canonical content changes; no conflict with any in-flight feature story.

---

## Problem framing

Durante o merge da Story T002.4 (commit `5a52ddd6b1e710d830977b08be832850a6697842` em `main`, 2026-04-24), Gage (@devops) identificou uma **anomalia de governança silenciosa**: os dois arquivos declarados **canonical invariant** pelo squad — `data/manifest.csv` (R15 append-only manifesto) e `core/memory_budget.py` (ADR-1 v3 constants home; R1-1 invariant) — **não estão rastreados por git** e **não aparecem em `.gitignore`**.

**Consequência prática:** todos os checks "byte-identical" executados em dezenas de despachos anteriores (verified via `sha256sum` spot-check em pre/post steps de cada story) foram **trivialmente verdadeiros** porque o git jamais versionou os bytes originais — não havia um baseline commit contra o qual comparar. A invariância foi preservada **exclusivamente via disciplina de agente** (cada persona verifica o sha antes/depois, cada story lista os arquivos em "Files NOT touched"), **sem qualquer salvaguarda ao nível de VCS**.

**Modo de falha silenciosa (risco material):** qualquer artefato ambiental — conversão CRLF ↔ LF em checkout Windows, re-save por editor (BOM insertion, trailing newline normalization), reorder de fsync em crash de OS, sync de cloud-drive (OneDrive/Dropbox) rewriting bytes, antivirus scan quarantine-and-restore — poderia mutar os bytes e **só ser detectado pelo próximo agente que coincidentemente re-rodasse `sha256sum`**. Não há diff no `git status`, nenhum trip de CI, nenhum audit trail.

**RA-20260428-1 Decision 7 (origem formal desta story):** Morgan (@pm) recebe standing authority para abrir esta story de R15-hardening, com tri-signature mandatory (`@data-engineer + @dev + @risk-manager-cosign`) e AC explícitas: adicionar ambos os arquivos ao git com baseline commit estabelecendo o sha atual como tracked state, verificar igualdade pre/post, e co-sign R15 no QA-gate.

**Escopo da story:** puramente de rastreabilidade VCS. **Zero mudança de conteúdo** nos dois arquivos. **Zero re-architecting** do contrato MWF-20260422-1 (que continua authoritative para write-semantics do manifest). **Zero provisioning de CI** (apenas proposta documentada de hook/CI é deliverable; implementação fica para story futura).

---

## Acceptance criteria

### Core ACs (RA-28-1 Decision 7, verbatim mapping)

- [ ] **AC1** — `data/manifest.csv` é adicionado ao git com **baseline commit** estabelecendo o sha atual como tracked state. Pre-add sha verificado `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`; post-commit sha **byte-identical** (o `git add` não muta bytes; se `core.autocrlf=true` no ambiente de Dex causar qualquer conversão, a story FALHA e deve ser refeita com `--renormalize` ou configuração explícita de `.gitattributes` antes do add).
- [ ] **AC2** — `core/memory_budget.py` é adicionado ao git com **baseline commit** estabelecendo o sha atual como tracked state. Pre-add sha verificado `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d`; post-commit sha **byte-identical** (mesmo protocolo CRLF-safety de AC1).
- [ ] **AC3** — **sha verification pre/post byte-identical** para ambos os arquivos. Evidência obrigatória no File List: dois blocos `sha256sum` (pre-add + post-commit) por arquivo, totalizando 4 linhas; os 4 hashes devem colar com os canonical pins acima verbatim.
- [ ] **AC4** — `.gitignore` é revisado. Dex documenta no story: (a) **explicit allow** (nenhum pattern em `.gitignore` ou ancestor exclude ignora os paths), OU (b) **silent non-exclusion** (algum pattern poderia ter ignorado mas não casa). O findings deve incluir o comando `git check-ignore -v data/manifest.csv core/memory_budget.py` — se retornar exit-code 0 (ignored) é um **BLOCKER** e deve ser resolvido antes do commit de AC1/AC2.
- [ ] **AC5** — **Proposta** (não implementação) de mecanismo de drift-detection futuro é documentada em seção dedicada desta story (ver "Drift-detection proposal" abaixo). Deliverable mínimo: (i) pre-commit hook sketch (shell ou YAML) que bloqueia commits que mutem os dois arquivos sem uma tag explícita de co-sign; (ii) alternativa CI-level (GitHub Action ou equivalente) que compare o sha post-checkout contra os pins canônicos. Implementação de CI é **out-of-scope** desta story — é story futura; **a proposta textual é o AC**.
- [ ] **AC6** — **R15 append-only invariant** é documentado nesta story (seção "R15 contract restatement" abaixo): o conteúdo atual de `data/manifest.csv` é **baseline-immutable**; qualquer mutação futura segue o padrão MWF-20260422-1 em vigor (append-only + flag explícito `MWF-YYYYMMDD-N` + custodial co-sign de Dara + story/RA formal). Esta story NÃO altera o contrato — apenas o reafirma por escrito dentro do corpo da story como parte do audit trail do baseline commit.
- [ ] **AC7** — **Story-level tri-signature co-sign block** satisfeito no QA-gate, com todas as três assinaturas registradas:
  - (i) **@data-engineer (Dara)** — canonical-producer surface custodian: revisa o diff do baseline commit (deve ser **empty-content diff** — zero bytes alterados; apenas tracking status muda de untracked → tracked) e registra custodial co-sign.
  - (ii) **@dev (Dex)** — implementation: executa T1–T4 e registra evidência sha pre/post conforme AC1–AC3.
  - (iii) **@risk-manager (Riven)** — R15 sentinel: confirma que `data/manifest.csv` está sob rastreamento VCS com o baseline correto e que MWF-20260422-1 segue authoritative para write-semantics futuras. Riven co-sign é **mandatory at QA-gate boundary** (não RA-level).

### Scope-discipline ACs (hard constraints — gate rejects on violation)

- [ ] **AC8** — **Conteúdo dos dois arquivos canônicos permanece byte-identical ao longo de TODA a vida da story**. Verificação em 3 pontos: (a) story authorship (já feito — pins acima), (b) pre-add por Dex em T1, (c) post-commit por Dex em T1. Qualquer desvio = gate failure + rollback.
- [ ] **AC9** — **Nenhum outro arquivo é modificado** além de: (i) esta story `.md` (governance artifact), (ii) baseline commits de AC1/AC2 (que adicionam os dois canonical files ao tracking, sem mudar conteúdo), (iii) opcionalmente `.gitattributes` se AC1/AC2 exigir `binary` ou `-text` normalization para CRLF-safety (Dex decide em T1; se tocado, deve ser listado no File List).
- [ ] **AC10** — **Nenhum PR aberto por Dex/Dara/Riven/Quinn**. Gage (@devops) tem autoridade R12 exclusiva para push e merge (ver Agent Authority matrix). A story é concluída internamente até o QA-gate; o handoff para Gage é passo final.
- [ ] **AC11** — **MWF-20260422-1 contract untouched**. Esta story não emite novo flag de write, não altera o formato de manifest, não introduz nova coluna, não muta write-semantics. É exclusivamente uma mudança de **tracking status** (untracked → tracked) em VCS.
- [ ] **AC12** — **ADR-1 v3 constants em `core/memory_budget.py` untouched**. R1-1 invariant preservado.

### Regression budget

- [ ] **AC13** — Nenhum teste existente precisa ser modificado. Esta story não adiciona nem altera testes (mudança de tracking VCS é ortogonal à test suite). Se Quinn pedir teste de drift-detection no gate, o teste proposto vai para a story de implementação de CI (future, out-of-scope aqui).

---

## Tasks

- [ ] **T1 (Dex, @dev)** — **Baseline git-tracking commit**
  - T1.1 Pre-add sha verification: `sha256sum data/manifest.csv core/memory_budget.py`. Must print the two pins verbatim. If mismatch → HALT, escalate to Riven + Dara.
  - T1.2 Run `git check-ignore -v data/manifest.csv core/memory_budget.py`. Exit-code 1 (not-ignored) is expected. If exit-code 0 → HALT (AC4 BLOCKER); resolve `.gitignore` before proceeding.
  - T1.3 Optional CRLF-safety check: `git config --get core.autocrlf`. If `true` (Windows default), evaluate whether `.gitattributes` needs a `data/manifest.csv -text` + `core/memory_budget.py -text` block to freeze line-ending interpretation. Document decision in story File List.
  - T1.4 `git add data/manifest.csv core/memory_budget.py` (+ `.gitattributes` if T1.3 decided to add one).
  - T1.5 `git commit` with conventional message citing RA-28-1 Decision 7. Suggested message:
    ```
    chore(governance): track canonical invariant files data/manifest.csv + core/memory_budget.py

    Per RA-20260428-1 Decision 7 — both files were canonical invariant by
    agent discipline but untracked in git, creating a silent drift risk
    (flagged by Gage during T002.4 merge, commit 5a52ddd). Baseline commit
    establishes current sha as tracked state with byte-identical content:

      data/manifest.csv       75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641
      core/memory_budget.py   1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d

    MWF-20260422-1 remains authoritative for all future manifest
    write-semantics (append-only + flag + custodial co-sign).

    Story: R15-canonical-invariant-hardening
    Co-sign: @data-engineer + @dev + @risk-manager-cosign
    ```
  - T1.6 Post-commit sha verification: `sha256sum data/manifest.csv core/memory_budget.py` again. Hashes MUST match pins verbatim. If mismatch (CRLF conversion on re-read, editor artifact, etc.) → HALT, revert commit, diagnose, re-run T1.3.
  - T1.7 Record all four `sha256sum` outputs (pre + post × two files) in the "File list" section below as audit trail for AC3.

- [ ] **T2 (Dara, @data-engineer)** — **Custodial diff review + co-sign**
  - T2.1 `git show --stat HEAD` on Dex's commit. Expected: two files listed with additions = (line count of each file), deletions = 0. Since the files are being *introduced* to tracking, git reports them as "new files" and their line-count as additions — this is the canonical baseline, not a content mutation.
  - T2.2 `git show HEAD -- data/manifest.csv | sha256sum` (stream the blob through the hash) — must match pin `75e72f2c...391641`. Same for `core/memory_budget.py` matching `1d6ed849...f9287d`.
  - T2.3 Dara custodial co-sign registered in this story's QA-gate block (below) with timestamp BRT.

- [ ] **T3 (Dex, @dev)** — **`.gitignore` audit (AC4 evidence)**
  - T3.1 Read `.gitignore` at repo root and every nested `.gitignore` in ancestor directories of `data/` and `core/`. Paste any matching patterns into the "`.gitignore` findings" section below.
  - T3.2 Run `git check-ignore -v data/manifest.csv core/memory_budget.py` (exit-code 1 expected = not ignored). Paste output into "`.gitignore` findings".
  - T3.3 Classify as (a) explicit allow or (b) silent non-exclusion and document rationale.

- [ ] **T4 (Dex, @dev)** — **Drift-detection proposal (AC5 deliverable — text only, no implementation)**
  - T4.1 Draft pre-commit hook sketch. Suggested skeleton (shell-based, portable to `pre-commit` framework):
    ```bash
    #!/usr/bin/env bash
    # .git/hooks/pre-commit (sketch — NOT installed by this story)
    # Blocks commits that mutate canonical invariant files without co-sign tag.
    set -euo pipefail
    CANONICAL_FILES=(
      "data/manifest.csv:75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641"
      "core/memory_budget.py:1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d"
    )
    CO_SIGN_TAG_RE='MWF-[0-9]{8}-[0-9]+|R1-1-WAIVER-[0-9]{8}-[0-9]+'
    for entry in "${CANONICAL_FILES[@]}"; do
      path="${entry%%:*}"
      pin="${entry##*:}"
      if git diff --cached --name-only | grep -qFx "$path"; then
        actual=$(git show ":${path}" | sha256sum | awk '{print $1}')
        if [[ "$actual" != "$pin" ]]; then
          msg=$(git log -1 --format=%B 2>/dev/null || cat "$(git rev-parse --git-dir)/COMMIT_EDITMSG")
          if ! echo "$msg" | grep -Eq "$CO_SIGN_TAG_RE"; then
            echo "BLOCK: canonical invariant $path mutated without co-sign tag (expected one of: $CO_SIGN_TAG_RE)." >&2
            exit 1
          fi
        fi
      fi
    done
    ```
    Rationale: this enforces "write requires flag" at VCS boundary, matching MWF-20260422-1 semantics.
  - T4.2 Draft CI-level alternative (text-only). Sketch a GitHub Actions step that runs `sha256sum -c` against a committed `canonical-invariant.sums` file on every PR; any mismatch fails the check. Note that this requires the `.sums` file to be maintained (new story to provision).
  - T4.3 Document trade-offs: pre-commit runs only on committer's machine (skippable with `--no-verify`), CI is server-side enforceable but slower. Recommended combination: pre-commit for fast local feedback + CI for authoritative enforcement.

- [x] **T5 (Riven, @risk-manager)** — **R15 sentinel co-sign at QA-gate**
  - T5.1 Verify `git log --all -- data/manifest.csv` now returns a commit (should be Dex's baseline commit, not empty). Same for `core/memory_budget.py`.
  - T5.2 Verify `git show HEAD:data/manifest.csv | sha256sum` matches pin `75e72f2c...391641`. Same for `core/memory_budget.py` matching `1d6ed849...f9287d`.
  - T5.3 Confirm R15 append-only invariant is re-stated in the story body (AC6) and that MWF-20260422-1 contract remains unchanged (AC11).
  - T5.4 Register R15 sentinel co-sign in QA-gate block below with timestamp BRT.

- [x] **T6 (Quinn, @qa)** — **QA gate**
  - T6.1 7-quality-checks gate per `story-lifecycle.md`. Gate artifact: `docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md` sha256 `8c4016b881498ebe1f7b6b75b06d02abfc64d09d5e3b2b80ed935c28c2350bbe`.
  - T6.2 Tri-signature verification: Dara T2 (2026-04-24T19:15:00) → Dex T1/T3/T4 (2026-04-24T20:30:00) → Riven T5 (2026-04-24T21:05:00) → Quinn T6 (2026-04-24T21:30:00) — chronologically consistent, AC7 satisfied.
  - T6.3 Gate decision: **PASS** (all 7 checks PASS; zero findings; canonical invariants preserved byte-identical; tri-signature complete; zero test delta AC13).

- [x] **T7 (Gage, @devops)** — **Push + merge (R12 exclusive authority)**
  - T7.1 `git push` on the baseline commit (or push of a feature branch → PR → merge — Gage decides per repo conventions).
  - T7.2 Gage confirms main is updated with tracking baseline.
  - T7.3 [executed 2026-04-24T~22:00 BRT] Push-only disposition per R12 devops authority: (a) `git push origin ra-28-1/step-7-ceiling-populate` PASS — `--allow-empty` governance marker landed remote first (preserves step-7 CEILING_BYTES populate audit trail per Dev Notes); (b) `git push origin r15/canonical-hardening` PASS — remote sha confirmed `ee786f80e66058d55b29acef267ada2dcdd021ee` via `git ls-remote`; (c) PR #3 opened https://github.com/nicksauro/vespera/pull/3 (base=main, head=r15/canonical-hardening, OPEN); (d) `git log --oneline main..r15/canonical-hardening` confirms 2-commit range (327d199 + ee786f8) as expected per branch chain. Merge NOT executed — deferred to Nicolas per dispatch constraint. No force-push, no `--force-with-lease`, no merge, no close. Post-T7 canonical re-check: `core/memory_budget.py` = `1d6ed849...f9287d` ✅ byte-identical to pin; `data/manifest.csv` = `75e72f2c...391641` ✅ byte-identical to pin; local HEAD unchanged at `ee786f80`. Pre-push verification table: disk-sha memory_budget PASS, git-object-sha memory_budget PASS, disk-sha manifest PASS, git-object-sha manifest PASS, pytest 263/1 zero-delta PASS, git-status clean (untracked governance drafts only, tracked files clean) PASS. `gh auth status` PASS (nicksauro, scopes repo/gist/read:org). `git config user.email`/`user.name` set PASS.

---

## File list (previsto)

**Modified by this story (governance artifact only):**
- `docs/stories/R15-canonical-invariant-hardening.story.md` — this file. Created by Morgan (@pm) in Draft. Updated by Dex/Dara/Riven/Quinn across T1–T6 to record execution evidence + sha audit trail + co-signatures.

**Newly git-tracked by this story (zero content change — baseline commit only):**
- `data/manifest.csv` — **content byte-identical; only tracking status changes untracked → tracked**. Baseline sha: `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`.
- `core/memory_budget.py` — **content byte-identical; only tracking status changes untracked → tracked**. Baseline sha: `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d`.

**Conditionally modified (only if T1.3 requires CRLF-safety):**
- `.gitattributes` — **conditional: Dex decides at T1.3** (Pax Rec 3, pre-declared for Dara T2.1 diff-review unambiguity). New or appended file pinning `-text` for the two canonical paths. If added, expected content includes: `data/manifest.csv -text` and `core/memory_budget.py -text`. If Dex's T1.3 decision is "no change needed" (e.g. `core.autocrlf=false` on the execution environment), this line remains non-materialized and Dara's T2.1 diff should show exactly two files in `git show --stat HEAD` (no `.gitattributes`).

**Audit trail (filled by Dex during T1; re-verified at T3/T4 — canonical invariants byte-identical at every stage):**
```
# Pre-add (T1.1, BRT ~2026-04-24T18:40:00, ancestor commit 327d1990):
75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641 *data/manifest.csv
1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d *core/memory_budget.py

# Post-commit (T1.6, BRT ~2026-04-24T18:58:00, commit ee786f80e66058d55b29acef267ada2dcdd021ee):
75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641 *data/manifest.csv
1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d *core/memory_budget.py

# Re-verified at T3/T4 entry (Dex second-dispatch, BRT 2026-04-24T20:15:00, HEAD ee786f80):
# disk sha256sum:
75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641 *data/manifest.csv
1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d *core/memory_budget.py
# git-object (git hash-object — blob header included; shown for completeness, NOT a pin):
91142c4c709a20457d39ee86e0b6b125910d9875  data/manifest.csv
7295b05786203008af6de222cef0d1c1688d756d  core/memory_budget.py
# git show HEAD:<path> resolves to same blob shas — confirmed byte-identical in tree.

# AC3 / AC8 status: SATISFIED — 6 disk sha256 samples across three time points all equal to canonical pins verbatim.
```

**Files NOT touched (hard constraints — gate failure if violated):**
- `data/manifest.csv` — **content byte-identical** (AC8; pin `75e72f2c...391641`). The file is *added to git tracking* but its bytes MUST NOT change.
- `core/memory_budget.py` — **content byte-identical** (AC8, AC12; pin `1d6ed849...f9287d`). R1-1 invariant preserved.
- `docs/architecture/memory-budget.md` — Aria + Riven territory; RA-28-1 text is closed under governance.
- `docs/architecture/pre-cache-layer-spec.md` — Aria's territory.
- ADR-1 v3 clauses — untouched (AC12).
- MWF-20260422-1 contract artifacts — untouched (AC11).
- Any production code under `scripts/`, `core/`, `tests/` — this is a governance-only story.

---

## `.gitignore` findings (AC4 — filled by Dex in T3)

**T3.1 — Root `.gitignore` review (repo-tracked version at HEAD `ee786f80`):**

Full ignore patterns inventory (verbatim, as tracked in repo; working-tree `.gitignore` has unrelated uncommitted edits — `.venv/`, `data/cache/` — that are OUT OF SCOPE for this story and are NOT touched here):

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
*.egg-info/
build/
dist/

# Env / secrets
.env
.env.*
!.env.example
!.env.vespera.example
config_local.py
*.pem
*.key

# Vespera materialized data (parquet cache — regenerable from Sentinel DB)
# manifest.csv is committed separately (source of truth for hashes)
data/in_sample/
data/hold_out/

# IDE
.vscode/
.idea/
*.swp

# ProfitDLL local copies (too big for git)
*.dll

# Runtime state (ATR/percentile caches, logs)
state/
logs/

# OS
Thumbs.db
.DS_Store

# AIOX runtime
.aiox/handoffs/
```

Patterns potentially matching `data/manifest.csv`: none — no `data/manifest.csv` pattern; the existing `data/in_sample/` and `data/hold_out/` ignore sibling directories, not files under `data/` root. Lines 30–31 contain a pre-existing inline comment that explicitly declares `# manifest.csv is committed separately (source of truth for hashes)`, which aligns with AC1 intent.

Patterns potentially matching `core/memory_budget.py`: none — no `core/` pattern exists.

Ancillary pattern audit: `*.py[cod]`, `*.so`, `*.pem`, `*.key`, `*.dll`, `*.swp` — none of these extension globs match `manifest.csv` or `memory_budget.py`.

**T3.1 — Nested `.gitignore` files in ancestor directories of `data/` and `core/`:**

`find . -name ".gitignore" -not -path "./.git/*"` returns:
- `./.gitignore` (root — reviewed above)
- `./.mypy_cache/.gitignore`
- `./.pytest_cache/.gitignore`
- `./.ruff_cache/.gitignore`
- `./.venv/.gitignore`

None of these reside in ancestor directories of `data/` or `core/`. Confirmed: no nested `.gitignore` affects the canonical paths.

**T3.2 — `git check-ignore -v data/manifest.csv core/memory_budget.py` output:**

```
$ git check-ignore -v data/manifest.csv core/memory_budget.py
(no output)
$ echo "exit=$?"
exit=1
```

Exit code 1 = "not ignored" (expected per T1.2 / AC4). Both canonical paths pass the ignore gate.

**T3.3 — Classification:**

- [x] **(a) explicit allow** — no pattern in the root `.gitignore` (nor in any nested `.gitignore`) would ignore these paths. The root `.gitignore` line 31 (`# manifest.csv is committed separately (source of truth for hashes)`) is an inline declarative comment affirming explicit-allow intent for `data/manifest.csv`. `core/memory_budget.py` has no matching pattern at any level — also explicit allow.
- [ ] (b) silent non-exclusion

**Rationale:** The `.gitignore` was authored without any pattern that even approaches these paths; the manifest path carries an inline intent comment. This is a clean "explicit allow" — baseline tracking is unambiguous at VCS layer. AC4 satisfied.

---

## Drift-detection proposal (AC5 — Dex drafts in T4, text-only, no implementation)

**Scope reminder (AC5 + AC12):** this section is **proposal-only text**. No hook is installed, no CI workflow is provisioned, no `.git/hooks/` or `.githooks/` directory is materialized by this story. Any future activation is a separate story ("R15.2" recommended — see §4 below) and requires its own tri-signature.

### 1. Pre-commit hook skeleton (proposal — NOT activated)

Bash skeleton for `pre-commit` framework install path (`.githooks/pre-commit-canonical-invariant` suggested; `.git/hooks/` is intentionally avoided because it is not tracked). Skeleton pins the current R15 baseline canonical shas verbatim (post-step-7 populate values — NOT the pre-populate `51972c52...` sha):

```bash
#!/usr/bin/env bash
# .githooks/pre-commit-canonical-invariant (SKETCH — NOT installed by R15)
# Blocks commits that mutate canonical invariant files without an explicit
# co-sign write flag in the commit message. Enforces MWF-20260422-1 +
# R1-1-WAIVER-YYYYMMDD-N semantics at the VCS boundary.
#
# Install (future story — NOT this one):
#   git config core.hooksPath .githooks
#   chmod +x .githooks/pre-commit-canonical-invariant
#   ln -sf pre-commit-canonical-invariant .githooks/pre-commit

set -euo pipefail

# Pinned post-R15-baseline canonical shas (disk sha256, NOT git blob sha).
# If this list is updated, the update itself requires a co-sign flag.
CANONICAL_FILES=(
  "data/manifest.csv:75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641"
  "core/memory_budget.py:1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d"
)

# Accepted co-sign flag patterns (from MWF-20260422-1 + R1-1 waiver contracts):
#   - MWF-YYYYMMDD-N      → manifest append write flag (Dara custodial co-sign required)
#   - R1-1-WAIVER-YYYYMMDD-N → memory_budget.py ADR-1 v3 constants supersession flag
CO_SIGN_TAG_RE='MWF-[0-9]{8}-[0-9]+|R1-1-WAIVER-[0-9]{8}-[0-9]+'

staged_paths=$(git diff --cached --name-only)

for entry in "${CANONICAL_FILES[@]}"; do
  path="${entry%%:*}"
  pin="${entry##*:}"
  if echo "$staged_paths" | grep -qFx "$path"; then
    # Hash the staged working-tree version (what the commit will materialize)
    actual=$(git show ":${path}" | sha256sum | awk '{print $1}')
    if [[ "$actual" != "$pin" ]]; then
      msg_file="$(git rev-parse --git-dir)/COMMIT_EDITMSG"
      msg=$(cat "$msg_file" 2>/dev/null || echo "")
      if ! echo "$msg" | grep -Eq "$CO_SIGN_TAG_RE"; then
        echo "BLOCK: canonical invariant $path mutated (sha $actual != pin $pin) without co-sign tag." >&2
        echo "       Expected one of: $CO_SIGN_TAG_RE" >&2
        echo "       See docs/stories/R15-canonical-invariant-hardening.story.md for contract." >&2
        exit 1
      fi
      echo "NOTE: canonical invariant $path mutated with co-sign tag — permitted." >&2
    fi
  fi
done

exit 0
```

**Rationale:** enforces "write requires flag" at the VCS boundary, matching MWF-20260422-1 (manifest append) and R1-1-WAIVER (memory_budget.py constants) contracts. The hook is append-safe (a commit without canonical mutation passes through instantly).

### 2. CI-level alternative (proposal — NOT provisioned)

GitHub Actions workflow sketch for `/.github/workflows/canonical-invariant-check.yml` (NOT created by this story):

```yaml
# .github/workflows/canonical-invariant-check.yml (SKETCH — NOT provisioned by R15)
name: Canonical invariant drift check
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  check-canonical-shas:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 1
      - name: Verify canonical invariant shas
        run: |
          set -euo pipefail
          # A committed companion file — canonical-invariant.sums — holds
          # authoritative pins. Any drift fails the job.
          sha256sum -c .github/canonical-invariant.sums
```

Companion file `.github/canonical-invariant.sums` (also NOT created by R15 — proposal only):

```
75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641  data/manifest.csv
1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d  core/memory_budget.py
```

Updates to `canonical-invariant.sums` require the same co-sign flag gate as direct canonical file mutations — any PR touching it needs `MWF-YYYYMMDD-N` or `R1-1-WAIVER-YYYYMMDD-N` in the PR title/body.

### 3. Trade-off analysis

| Dimension | Pre-commit hook | GitHub Actions CI |
|-----------|----------------|-------------------|
| **Enforcement locus** | Committer's local machine | Server-side (authoritative) |
| **Speed** | Instant (<100ms on these two files) | ~20-60s per PR run (checkout + job spin-up) |
| **Skippability** | Yes — `git commit --no-verify` bypasses | No — branch protection + required checks can make it non-bypassable |
| **Coverage** | Only commits authored locally by developers who installed the hook | Every PR + every push to protected branches |
| **Maintenance cost** | Low — single shell file, pins embedded | Medium — workflow YAML + separate `.sums` file to maintain |
| **Failure mode** | Gives fast local feedback; prevents bad push | Catches drift even from collaborators who bypass local hook |
| **Pin update cost** | Edit hook file (requires co-sign flag itself) | Edit `.sums` file (requires co-sign flag itself) |
| **False-positive risk** | Low — staged-file filter + commit-msg regex | Very low — deterministic sha check |

**Recommended combination (future story):** deploy both. Pre-commit catches ~95% of mutations locally with instant feedback; CI provides authoritative server-side enforcement that cannot be skipped. Together they form a defense-in-depth matching the tri-signature story-level governance already in place.

### 4. Recommended follow-up story

**R15.2 — provision canonical-invariant drift-detection hook + CI**

- Install `.githooks/pre-commit-canonical-invariant` (above) with `core.hooksPath` config.
- Create `.github/workflows/canonical-invariant-check.yml` + `.github/canonical-invariant.sums`.
- Require the CI check in branch protection for `main` (R12 Gage scope).
- Update `docs/architecture/memory-budget.md` Decision Matrix with the new R15.2 reference.
- Tri-signature expected: `@data-engineer + @dev + @risk-manager-cosign` + Gage for branch-protection toggle.

**Out-of-scope for R15.2 (pushes to R16 or later):** fingerprinting additional canonical surfaces (e.g., `docs/architecture/memory-budget.md` itself, ADR-1 v3 artifacts, MWF contract docs). This story scope is exclusively the two files identified by Gage in T002.4 merge.

---

## R15 contract restatement (AC6)

The R15 append-only invariant for `data/manifest.csv` is hereby re-affirmed as follows (no new policy — this is the existing MWF-20260422-1 contract written out as part of this story's audit baseline):

1. **Baseline immutability**: the content of `data/manifest.csv` at the instant of this story's baseline commit (sha `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641`) is **append-only from here forward**. No row is ever modified in place; no row is ever deleted.
2. **Mutation protocol**: future appends require (a) explicit `MWF-YYYYMMDD-N` write flag registered in the commit message or accompanying RA/story, (b) custodial co-sign by Dara (@data-engineer) as canonical-producer surface custodian, (c) story or RA artifact declaring the appended row(s) and the justification, (d) R15 sentinel awareness at QA-gate for the story that performs the append.
3. **`core/memory_budget.py` invariance**: this file is **not append-only** — it is fully immutable with respect to ADR-1 v3 constants (R1-1 invariant). Any future change to its constants requires a new ADR supersession + R1-1 waiver (`R1-1-WAIVER-YYYYMMDD-N` flag).
4. **This story's own effect on the contract**: ZERO. This story only changes VCS tracking status. No content of either file is mutated; no new flag is emitted; no existing protocol is amended.

---

## Out-of-scope (explicit)

- **Mudar o conteúdo** de `data/manifest.csv` ou `core/memory_budget.py`. Qualquer mutação de byte = gate failure + rollback mandatory.
- **Re-arquitetar** o MWF-20260422-1 contract. Ele permanece authoritative verbatim.
- **Provisionar CI** ou instalar o pre-commit hook. Apenas a proposta textual é deliverable (AC5). Implementação é story futura.
- **Adicionar ou alterar testes** na suíte. T4.3 regression budget explícito (AC13).
- **Emitir um novo flag MWF-YYYYMMDD-N**. Esta story não faz append ao manifest — apenas rastreia o baseline em git.
- **Abrir PR ou fazer push**. Gage tem autoridade R12 exclusiva (AC10).

---

## Dev Notes

- **Origem da autoridade:** RA-20260428-1 (Stage-2, 2026-04-24T21:36:22Z), **Decision 7** no Decision Matrix de `docs/architecture/memory-budget.md`. Citar por RA-ID + Decision number (não line number — linhas drift; RA-ID é estável).
- **Commit de descoberta da anomalia:** `5a52ddd6b1e710d830977b08be832850a6697842` em `main` (merge de T002.4 por Gage, 2026-04-24). Gage notou no post-merge review que os dois arquivos passaram por dezenas de stories sem jamais aparecer em `git log --all`.
- **Contrato de write ainda vigente (untouched by this story):** MWF-20260422-1 — append-only + flag explícito + custodial co-sign de Dara. A presente story é ortogonal: endereça *tracking VCS*, não *write semantics*.
- **Por que a story é "empty-content diff":** adicionar um arquivo ao git via `git add` não muta seus bytes (assumindo `core.autocrlf=false` ou `-text` pinned em `.gitattributes`). Dara deve verificar no diff review (T2.1) que `git show --stat HEAD` lista os arquivos com adds = line-count e deletes = 0 (comportamento canônico de "new file"), e que `git show HEAD:<path> | sha256sum` retorna o pin byte-identical (T2.2).
- **CRLF risk em Windows:** se Dex rodar com `core.autocrlf=true` (Git for Windows default), o checkout subsequente poderia normalizar line-endings e mutar bytes. T1.3 é a mitigação: Dex decide se `.gitattributes` precisa de `-text` pinning ou se o ambiente já está `autocrlf=false`/`input`. Post-commit sha re-check em T1.6 captura qualquer surpresa.
- **Delegação:** esta story NÃO é executada por Morgan (@pm). Morgan apenas drafted. Execução segue o fluxo SDC: Dex implementa (T1, T3, T4) → Dara custodial review (T2) → Riven R15 sentinel co-sign (T5) → Quinn gate (T6) → Gage push/merge (T7).
- **RA-28-1 Decision 3 audit YAML (Pax Rec 2 — Riven T5 R15 sentinel co-sign context):** `data/baseline-run/ra-20260428-1-decision-3-audit.yaml` sha `c60ca42af2ff2a1c875dcf36645ccd05b7c5055ad6955e0d650196a405445126`. Purpose of citation: Decision 3 SUCCESS context for Riven's R15 sentinel co-sign at T5 — audit YAML confirms canonical invariants preserved byte-identical across Aug-2024 baseline execution.

---

## QA-gate co-sign block (to be filled by Dara, Riven, Quinn in T2, T5, T6)

**(Placeholder — tri-signature + QA gate verdict registered here at gate time.)**

```
Dara custodial co-sign (T2):   PASS  — timestamp BRT: 2026-04-24T19:15:00  — signature line: @data-engineer Dara — R10 custodian review of commit ee786f80: git-object + disk sha byte-identical to pins for data/manifest.csv (75e72f2c...391641) and core/memory_budget.py (1d6ed849...f9287d); .gitattributes materialized with both canonical paths -text (core.autocrlf=true host); 3 files / 150 insertions / 0 deletions confirmed; manifest 17 rows MWF-20260422-1 column order intact; memory_budget.py R1-1 constants + CEILING_BYTES=615_861_044 + CEILING_DERIVATION_REF(RA-20260428-1 Decision 3) byte-identical; no unrelated files in commit range. Canonical invariant preserved.
Dex implementation sign-off (post-T1/T3/T4): PASS  — timestamp BRT: 2026-04-24T20:30:00  — signature line: @dev Dex (The Defender) — R15 T1/T3/T4 execution complete. (a) T1 [deferred T1.7 sign-off, now recorded]: baseline commit ee786f80 established; disk sha256 for data/manifest.csv=75e72f2c...391641 and core/memory_budget.py=1d6ed849...f9287d verified byte-identical at pre-add, post-commit, and T3/T4 re-entry (6 samples; see File list audit-trail block). AC1/AC2/AC3/AC8/AC12 satisfied. (b) T3 [.gitignore audit, AC4]: root .gitignore reviewed verbatim (repo-tracked version); zero patterns match canonical paths (line 31 explicit-allow comment for manifest confirmed); no nested .gitignore in ancestor dirs of data/ or core/; `git check-ignore -v data/manifest.csv core/memory_budget.py` exit-code 1 (not ignored); classification (a) explicit allow. AC4 satisfied. (c) T4 [drift-detection proposal, AC5]: pre-commit hook skeleton drafted with canonical sha pins verbatim (post-step-7 populate values, NOT pre-populate 51972c52), CI-level GitHub Actions alternative drafted with companion .sums file, trade-off matrix enumerated, R15.2 follow-up story recommended. Proposal-only — NO hook installed, NO workflow provisioned, NO activation. AC5 satisfied. (d) Scope discipline (AC9/AC10/AC11): zero mutations outside this story file; no PR opened; MWF-20260422-1 untouched. (e) Post-T4 canonical re-verification: disk sha256 of both canonical files unchanged from pins; HEAD unchanged at ee786f80 (no new commits created by T3/T4 — they are pure story-text populations per AC5 proposal-only scope). Ready for @risk-manager Riven T5 sentinel co-sign.
Riven R15 sentinel co-sign (T5): PASS  — timestamp BRT: 2026-04-24T21:05:00  — signature line: @risk-manager Riven (The Sentinel) — R15 sentinel co-sign at QA-gate boundary. T5.1 [tracking]: `git log --all -- data/manifest.csv` and `git log --all -- core/memory_budget.py` both return commit ee786f8 ("chore(governance): track canonical invariant files...") — both canonical invariants are now under VCS tracking with baseline established. T5.2 [independent 4-point sha verification at HEAD ee786f80]: (a) `git show HEAD:data/manifest.csv | sha256sum` → `75e72f2c1185eb795a5db6c5a127706e1b90c30906216a72ea79c443d5391641` ✅ matches pin; (b) `git show HEAD:core/memory_budget.py | sha256sum` → `1d6ed8498630acab6946089d9d92f3a71b64cebbbc0cd8442193dc20fb9f287d` ✅ matches pin; (c) disk `sha256sum data/manifest.csv` → `75e72f2c...391641` ✅ byte-identical to git-object; (d) disk `sha256sum core/memory_budget.py` → `1d6ed849...f9287d` ✅ byte-identical to git-object. All 4 points PASS — canonical invariants are byte-identical across disk ↔ git-tree at tracking baseline. T5.3 [contract integrity]: R15 append-only invariant is re-stated verbatim in AC6 § "R15 contract restatement" (baseline immutability for manifest; R1-1 full immutability for memory_budget.py with R1-1-WAIVER-YYYYMMDD-N required for any future ADR-1 v3 constants supersession). MWF-20260422-1 contract remains authoritative for all future manifest write-semantics (append-only + explicit flag + Dara custodial co-sign) — AC11 scope discipline honored, no contract mutation by this story. T5.4 [upstream evidence chain]: (i) RA-20260428-1 Decision 7 authority cited in story frontmatter with text anchor — authority chain intact; (ii) Decision 3 audit YAML at `data/baseline-run/ra-20260428-1-decision-3-audit.yaml` re-verified at sha `c60ca42af2ff2a1c875dcf36645ccd05b7c5055ad6955e0d650196a405445126` ✅ matches Dev Notes pin — confirms canonical invariants preserved byte-identical across Aug-2024 baseline execution; (iii) Dex step-7 ancestor commit `327d1990` on branch `ra-28-1/step-7-ceiling-populate` populates CEILING_BYTES=615_861_044, upstream of ee786f80 — pin reconciliation footnote (Morgan Pax Rec 1) honored, post-populate canonical sha tracked not pre-populate sha. T5.5 [sentinel-specific drift-risk review]: drift-detection proposal (AC5 / T4) is correctly scoped PROPOSAL-ONLY — no `.githooks/` directory materialized, no `.github/workflows/` file created, no `core.hooksPath` config set, no `canonical-invariant.sums` file committed; R15.2 follow-up story path identified for future activation with its own tri-signature. Trade-off matrix (pre-commit vs CI) reviewed: defense-in-depth recommendation (both) is architecturally sound and matches tri-signature governance pattern; co-sign flag regex `MWF-[0-9]{8}-[0-9]+|R1-1-WAIVER-[0-9]{8}-[0-9]+` correctly enumerates existing contract flag families (MWF-20260422-1 for manifest appends, R1-1-WAIVER for ADR-1 v3 constants supersession). Pin values embedded in hook skeleton match post-step-7 canonical shas verbatim — no stale pre-populate `51972c52...` reference carried forward. AC5 scope discipline confirmed. T5.6 [co-sign chain verification]: Dara T2 custodial co-sign (PASS) and Dex T1/T3/T4 implementation sign-off (PASS) both present in QA-gate block above, chronologically consistent (T1→T2→T3→T4→T5). Tri-signature on track for AC7 upon Quinn T6 gate completion. R15 SENTINEL DISPOSITION: ✅ READY FOR QUINN T6 GATE — canonical invariants rastreados com baseline byte-identical, MWF-20260422-1 + R1-1 contracts preserved, drift-detection proposal scoped correctly, audit trail complete.
Quinn QA gate verdict (T6): PASS  — timestamp BRT: 2026-04-24T21:30:00  — signature line: @qa Quinn (The Protector) — R15 7-check QA gate PASS. (1) Requirements traceability: AC1–AC13 all map to verifiable evidence (see coverage matrix in docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md sha 8c4016b881498ebe1f7b6b75b06d02abfc64d09d5e3b2b80ed935c28c2350bbe). (2) Test execution: pytest tests/ → 263 passed / 1 skipped at HEAD ee786f80; identical count at ancestor 327d1990 → zero test delta (AC13 satisfied; dispatch-preamble "272" figure reconciled to actual 263 — informational only). (3) Security/correctness: .gitattributes -text pinning correctly freezes CRLF on Windows core.autocrlf=true hosts; drift-detection proposal embeds post-populate canonical shas verbatim (1d6ed849...f9287d), not stale pre-populate 51972c52. (4) Parity 4-point: disk sha + git-object sha byte-identical to pins for both canonical files. (5) Contract consistency: MWF-20260422-1 schema intact (17 rows, header `path,rows,sha256,start_ts_brt,end_ts_brt,ticker,phase,generated_at_brt` untouched); R1-1 constants verbatim (CAP_ABSOLUTE=8_400_052_224, OBSERVED_QUIESCE_FLOOR_AVAILABLE=9_473_794_048, KILL_FRACTION=0.95, CEILING_BYTES=615_861_044). (6) Performance: N/A governance-only; drift proposal is proposal-only, zero overhead. (7) Spec compliance (Article IV): every artifact traces to RA-28-1 Decision 7 / MWF-20260422-1 / ADR-1 v3 / RA-28-1 Decision 3 / T002.4 commit 5a52ddd — no invention. Tri-signature (Dara T2 → Dex T1/T3/T4 → Riven T5) chronologically consistent; AC7 satisfied. Post-T6 canonical re-check: disk + git-object shas unchanged from pins for both files. DISPOSITION: T6 PASS — ready for T7 (Gage @devops push, R12 exclusive).
Gage push/merge confirmation (T7): PUSH COMPLETE (merge pending Nicolas)  — PR #3 https://github.com/nicksauro/vespera/pull/3 (base=main, head=r15/canonical-hardening @ ee786f80e66058d55b29acef267ada2dcdd021ee, OPEN)  — timestamp BRT: 2026-04-24T~22:00:00  — signature line: @devops Gage (The Gatekeeper) — R12 exclusive push executed per T7 dispatch. Pre-push gates PASS: (a) 4-point sha verification — disk+git-object byte-identical to pins for both canonical files at HEAD ee786f80 (`core/memory_budget.py`=1d6ed849...f9287d ✅, `data/manifest.csv`=75e72f2c...391641 ✅); (b) pytest 263 passed / 1 skipped — zero delta vs ancestor 327d1990 (AC13 ✅); (c) `git status` clean on tracked files (untracked governance drafts present but not in scope); (d) `gh auth status` authenticated as nicksauro with scopes repo/gist/read:org; (e) `git config user.email/name` set. Push sequence: (1) `git push origin ra-28-1/step-7-ceiling-populate` → `[new branch]` OK (step-7 `--allow-empty` governance marker 327d1990 landed first — preserves audit trail per Dev Notes; NOT squashed out); (2) `git push origin r15/canonical-hardening` → `[new branch]` OK (tracking commit ee786f80 landed on top). PR #3 opened with title `chore(governance): R15 canonical invariant hardening [RA-28-1 Decision 7]`, body cites RA-28-1 D7 authority + AC1–AC13 coverage + QA gate sha 8c4016b8...50bbe + full tri-signature table (Dara→Dex→Riven→Quinn) + test plan. Post-push verification PASS: `gh pr view 3` returns state=OPEN, headRefOid=ee786f80, baseRefName=main; `git log --oneline main..r15/canonical-hardening` returns 2-commit range (327d199 + ee786f8) as expected per branch chain; `git ls-remote origin r15/canonical-hardening` returns `ee786f80e66058d55b29acef267ada2dcdd021ee` ✅ matches local HEAD byte-exact. Post-T7 canonical invariant re-check: `core/memory_budget.py` + `data/manifest.csv` disk shas unchanged ✅ byte-identical to pins. CONSTRAINTS HONORED: no `--force` / `--force-with-lease`, no PR merge, no PR close, no new commits, no canonical file mutation — pure push+PR disposition per R12 devops monopoly. DISPOSITION: **T7 PUSH COMPLETE** — R15 story **Done pending Nicolas merge review** on PR #3. Chain closed: @pm Morgan (draft+pin-reconciliation) → @po Pax (GO 10/10) → @dev Dex (T1/T3/T4 PASS) → @data-engineer Dara (T2 custodial PASS) → @risk-manager Riven (T5 sentinel PASS) → @qa Quinn (T6 gate PASS) → @devops Gage (T7 push COMPLETE).
```

---

## Change log

- **2026-04-24 — Morgan (@pm) drafted** this story per RA-20260428-1 Decision 7 standing authority. Status: Draft. Canonical sha pins verified byte-identical at authorship: `data/manifest.csv` → `75e72f2c...391641`, `core/memory_budget.py` → `1d6ed849...f9287d`. Zero canonical touch in this draft (governance artifact only).
- **2026-04-24 — Dex (@dev) T1** baseline git-tracking commit `ee786f80e66058d55b29acef267ada2dcdd021ee` on branch `r15/canonical-hardening`. `.gitattributes` materialized with `-text` pins for both canonical paths (T1.3 decision given `core.autocrlf=true` on host). Disk sha256 verified byte-identical pre-add + post-commit. AC1/AC2/AC3/AC8/AC12 evidence captured. T1.7 audit-trail originally deferred; recorded in the second dispatch alongside T3/T4 (see File list).
- **2026-04-24 — Dara (@data-engineer) T2** custodial co-sign registered in QA-gate block. Empty-content diff review confirmed: git-object shas (blob-level) + disk shas (sha256sum) byte-identical to canonical pins at commit ee786f80. 17-row manifest MWF-20260422-1 column order intact; memory_budget.py R1-1 constants preserved. Story sha drifted by addition of Dara's sign-off line (T2.3) — authorized story mutation.
- **2026-04-24 — Dex (@dev) T3** `.gitignore` audit populated (AC4). Classification: explicit allow (no nested ignores, no matching patterns, inline allow comment for manifest). `git check-ignore -v` exit-code 1. No new commits (pure story-text population).
- **2026-04-24 — Dex (@dev) T4** drift-detection proposal populated (AC5). Pre-commit hook skeleton + GitHub Actions CI alternative + trade-off matrix + R15.2 follow-up story draft — all text-only. Hook pins updated to post-step-7 values (`1d6ed849...f9287d` for `core/memory_budget.py`, NOT pre-populate `51972c52...`). No hook installed, no workflow provisioned. Canonical invariants re-verified byte-identical post-T4. No new commits (proposal-only scope, AC5 + AC12). HEAD remains `ee786f80`. Ready for Riven T5.
- **2026-04-24 — Riven (@risk-manager) T5** R15 sentinel co-sign registered in QA-gate block. Independent 4-point sha verification PASS: disk + git-object shas byte-identical to canonical pins for both files at HEAD `ee786f80`. Upstream authority chain re-verified: RA-20260428-1 Decision 7 frontmatter citation intact; Decision 3 audit YAML sha `c60ca42a...45126` matches Dev Notes pin; step-7 ancestor `327d1990` preserves CEILING_BYTES=615_861_044. Drift-detection proposal (AC5) confirmed proposal-only — no hook installed, no workflow provisioned, no .sums file committed, no `core.hooksPath` set. MWF-20260422-1 + R1-1 contracts preserved (AC11/AC12). Co-sign chain (Dex→Dara→Riven) chronologically consistent for AC7. Disposition: READY FOR QUINN T6 GATE. No new commits (sign-off is story-file paste only per T5 scope). HEAD remains `ee786f80`. Post-T5 canonical re-check: shas unchanged.
- **2026-04-24 — Quinn (@qa) T6** 7-check QA gate **PASS**. Gate artifact: `docs/qa/gates/R15-canonical-invariant-hardening-qa-gate.md` sha256 `8c4016b881498ebe1f7b6b75b06d02abfc64d09d5e3b2b80ed935c28c2350bbe`. All 7 checks PASS (requirements traceability, test execution, security/correctness, parity 4-point, contract consistency, performance N/A, spec compliance Article IV). AC coverage matrix: AC1–AC13 all satisfied. Tri-signature (Dara T2 → Dex T1/T3/T4 → Riven T5 → Quinn T6) chronologically consistent. pytest: 263 passed / 1 skipped at HEAD `ee786f80` and at ancestor `327d1990` → zero test delta (AC13). Dispatch-preamble expected "272 passed" reconciled to actual 263 (informational only; AC13 scope is "zero delta" which IS satisfied). Canonical invariants post-T6 re-check: disk + git-object shas byte-identical to pins for both files; HEAD unchanged at `ee786f80`. No new commits (gate sign-off is story-file + QA-gate-artifact paste only). Disposition: **T6 PASS — ready for T7 (Gage @devops push, R12 exclusive).**
