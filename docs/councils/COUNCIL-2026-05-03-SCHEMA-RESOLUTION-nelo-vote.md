# Council 2026-05-03 Schema Resolution — Nelo (DLL Specialist) Ballot

> **Date (BRT):** 2026-05-03
> **Authority lens:** ProfitDLL `TranslateTrade` mechanics + `GetAgentName*` map availability + canonical quirks
> **Manual citations:** §3 line 750 (TConnectorTrade), §3.1 lines 1707-1729 (GetAgentName), §3.1 lines 1696-1705 (deprecated GetAgentNameByID), §3.2 line 3331 (TNewTradeCallback), §3.2 line 3597 (book agent IDs), §3.2 line 1907 (TranslateTrade usage)

## §1 Vote

**OPTION: D** — Defer broker question; cast int64→int32 now; technical-pure path proceeds.
**R16: CONCUR** — fully aligned with Q-AMB-02 raw-preservation discipline and §3.2 timestamp-format ambiguity handling.

## §2 Critical correction to council premise (manual-grounded)

**The premise that `TranslateTrade` ON/OFF causes int64-vs-string agent typing is FACTUALLY INCORRECT.**

Per manual §3 line 764-766, `TConnectorTrade.BuyAgent` and `SellAgent` are declared **`Integer`** (NOT string). Per §3.2 line 3348-3350, V1 `TNewTradeCallback` also declares `nBuyAgent Integer` / `nSellAgent Integer`. Per §3.1 line 1337-1338, `TranslateTrade(pTrade, var TConnectorTrade)` only unpacks an opaque V2 pointer into the struct — it **does not translate IDs to broker names**.

**The DLL ALWAYS returns integers for agents, in every callback, in every version.** String broker names exist only via separate post-hoc lookup with `GetAgentNameLength` + `GetAgentName(length, id, buf, shortFlag)` (§3.1 lines 1707-1729 — manual-canonical; `GetAgentNameByID` is DEPRECIATED per line 1705).

**Therefore F2 root cause is NOT `TranslateTrade` ON/OFF asymmetry.** It's that Sentinel 2024 ingestion ran `GetAgentName` post-hoc resolution (likely engine-thread cached lookup) and the backfill A1 probe deliberately **deferred** that resolution to A2 (per `t003.a2.story.md` line 286: *"A1 does NOT resolve agents during probe; raw integers persisted for A2 schema audit"*). This is **resolution-pipeline asymmetry**, not DLL-mode asymmetry.

## §3 Specific concerns

1. **Root cause:** corrected above. F2 is `GetAgentName` post-hoc lookup ON (Sentinel) vs OFF (backfill).
2. **Translate-map availability (Option B):** YES, feasible. Build via `GetAgentName` loop over observed IDs. Effort: **~2h Nelo** (probe script + cache JSON). Completeness: high for active agents during call-time, but see §4.
3. **Re-download (Option C):** unjustified. Re-running 50 chunks would reproduce the SAME integer agent IDs (DLL returns Integer regardless). Only `GetAgentName` post-hoc lookup adds strings — and that can be done WITHOUT re-download. **Strong NO on C** as currently scoped.
4. **Q-PRE2024 mapping drift:** Speculative-but-plausible. `GetAgentName` queries Nelogica's CURRENT agent registry — 2023 IDs that map to merged/renamed brokers (XP/Rico merger, Modal acquisition era) may resolve to today's name, not historical name. Manual is silent on registry stability. **This is a Sable-D-class divergence and supports Option D's deferral logic.**
5. **R16 coherence:** R16 is the storage-layer formalization of Q-AMB-02's tolerant-parser philosophy. Concur strongly.

## §4 Why D over B

Option B preserves optionality but commits us to a possibly-non-stationary mapping (concern #4). Option D preserves the int64 storage (R16-compliant, projects to int32 at consumption), parks the broker-name question until Mira's H_next-1 thesis declares need, and avoids registry-drift risk. If thesis later requires names, Option B becomes a 2h task — no information lost.

— Nelo, guardian of the DLL
