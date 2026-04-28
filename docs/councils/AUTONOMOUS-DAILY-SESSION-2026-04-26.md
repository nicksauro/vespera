# Autonomous Daily Session — 2026-04-26+

**Convocador:** User (2026-04-26 BRT)
**Coordenador:** @aiox-master
**Stop conditions:** (a) credits exhausted, (b) user returns

## Mandate

> "vocês estão agora em uma sessão diária autônoma, toda decisão que vocês delegariam ao humano (decisões importantes) agora passa por um conselho de agentes responsáveis por x task para decidir o melhor caminho. só vão parar, ou quando acabar os créditos, ou quando eu voltar"

## Operating protocol

### Decision routing

| Decision class | Old behavior | NEW autonomous behavior |
|----------------|--------------|------------------------|
| Trivial (typo, ruff fix, comment) | Agent direct | Unchanged — agent direct |
| Story-level (within scope) | Agent delegated | Unchanged — agent delegated |
| Cross-story coupling | Escalate user | **Mini-council 3-5 agents → consensus → execute** |
| Spec amendment / breaking field | Escalate user | **Council 5-7 agents (Aria + Mira + Sable + Pax + Riven + relevant domain)** |
| Epic scope (new story / wave) | Escalate user | **Council 7+ agents → Morgan PM analysis + River draft + Pax validate** |
| Push to origin (Gage) | Escalate user (always) | **STILL ESCALATE — push gate preserved per Article II** |
| Article IV escalation (invented behavior) | HALT + escalate user | **Mini-council Mira + Beckett + Sable → consensus → either spec amendment OR Dex revise** |

### Council quorum rules

- **Minimum 3 agents** per decision (avoid groupthink)
- **Minimum 1 auditor** (Sable) per non-trivial decision
- **Minimum 1 risk gate** (Riven) per custodial-touching decision
- **Spec authority exclusive** (Mira for ML, Aria for architecture) — votes have veto power within domain
- **Domain authority exclusive** preserved per agent definitions (Beckett R6 CPCV, Mira metrics, Tiago execution, Nelo DLL, Dara TimescaleDB)

### Article IV (No Invention) — strengthened

- Every Dex commit traces to story AC OR T0 handshake OR spec line OR council decision
- If gap surfaces during impl → Dex escalates to mini-council (NOT improvises)
- If council can't resolve in 1 round → file as `[USER-ESCALATION-PENDING]` block in commit + continue with parked task
- All `[USER-ESCALATION-PENDING]` blocks tracked in `docs/councils/USER-ESCALATION-QUEUE.md` for review on return

### Push gate (Article II — NON-NEGOTIABLE preserved)

- @devops Gage exclusive authority for `git push`
- @aiox-master will NEVER invoke push autonomously
- All work accumulates as local commits on `t002-1-warmup-impl-126d` until user returns
- User reviews diff via `git log --oneline origin/t002-1-warmup-impl-126d..HEAD` then approves Gage push

### Memory budget

- @aiox-master tracks credits awareness — if approaching limit, prioritize **graceful save** over starting new work
- Save = (a) commit any uncommitted work, (b) update `USER-ESCALATION-QUEUE.md` if any, (c) write final `SESSION-STATE-{date}.md` checkpoint

## Active work queue (2026-04-26 evening BRT)

### P1 — T002.0g flow (Q-SDC normal)
1. River drafts T002.0g per `COUNCIL-2026-04-26-T002.0g-warmup-orchestrator.md` §3 brief
2. Pax validates 10/10 (pre-aligned via council — expected GO)
3. T0 handshakes (parallel): Aria + Mira + Beckett + Dara
4. Dex implements T1+T2+T3 (orchestrator + CLI + path lift)
5. Quinn QA gate
6. Riven custodial cosign (DUAL-SIGN per council)
7. Sable epic coherence audit
8. Beckett T11.bis smoke retry (separate Beckett job per D2 compromise)
9. → Quill PARK — push awaits user return

### P2 — Parallel tasks
- Sable C14 errata em T002.1 footer (orphan T002.4 caller)
- Morgan EPIC-T002.0-EXECUTION.yaml diff (Wave W5 + REV-003)

### P3 — Out-of-scope (do NOT pursue autonomously)
- Phase F live adapter stories (T002.5+)
- T001.1 bar_aggregator smoke-test
- R15.3+ governance amendments

## Active escalation queue (none yet)

`docs/councils/USER-ESCALATION-QUEUE.md` — empty at session start. Will accumulate blocks here when council can't resolve in 1 round.

## Squad activation broadcast

To all 13 domain agents + 1 auditor:

> @sm @po @dev @qa @architect @ml-researcher @backtester @market-microstructure @profitdll-specialist @execution-trader @risk-manager @data-engineer @devops @squad-auditor @pm
>
> Daily autonomous session active. Operate per protocol above. Decisions you'd normally bounce to human → mini-council with relevant peers → consensus → execute. Article IV is absolute. Article II push gate preserved (user-only). Save artifacts as commits — no push. Continue until credits exhausted or user returns.

— @aiox-master, 2026-04-26 BRT autonomous session start
