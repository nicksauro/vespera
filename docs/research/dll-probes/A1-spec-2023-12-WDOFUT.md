# A1 Probe Spec — Pre-2024 WDOFUT Empirical Test (2023-12-01..2023-12-20)

> **Author:** Nelo (@profitdll-specialist) — DLL guardian, Manual-First Keeper
> **Date (BRT):** 2026-05-01
> **Branch:** `t003-a1-dll-probe-2023-12` (doc + script artifacts; no execution)
> **Authority basis:** Data Council 2026-05-01 R1-R4 binding conditions; Nelo §3.1 ballot probe spec
> **Execution authority:** Nelo specs the WHAT (this doc + companion script); Dara (@data-engineer) executes the script under Pax story authorization + Quinn QA gate. Nelo does NOT execute production DLL.
> **Article II preserved:** No git push; @devops Gage exclusive.
> **Article IV preserved:** Every clause traces to a source — manual section, canonical quirks entry, Sentinel empirical run, or Council resolution row.

---

## §1 Purpose + scope

### §1.1 Trigger

Path C HYBRID resolution from Data Acquisition Council 2026-05-01 (UNANIMOUS 5/5 APPROVE). Council §1 ratified:

- **PRIMARY:** Forward-time virgin hold-out 2026-05-01..2026-10-31 (Quant Council R7 carry-forward).
- **SECONDARY-CORROBORATIVE:** Pre-2024 archival window 2023-Q1..2024-Q3 via DLL backfill (Quant Council R8 fallback operationalized).

A1 is the FIRST gate of the implementation chain (Council §4):

```
A1 [THIS PROBE] → A2 schema parity → A3 cost atlas ruling → A4 regime check
   → A5 Sable virgin audit → A6 Pax + R10 user MWF → A7 bulk backfill → A8 Beckett N1+
```

### §1.2 Scope (what this probe answers)

**Single empirical question:** Does `GetHistoryTrades("WDOFUT", "F", "01/12/2023 09:00:00", "20/12/2023 18:00:00")` return non-trivial trade data with canonical 7-column schema fidelity, on the production ProfitDLL, today (2026-05-01)?

**Not in scope:**
- Bulk backfill (A7 territory).
- Schema parity audit byte-equal to current parquet (A2 — Dara authority).
- Regime equivalence statistical adjudication (A4 — Mira authority).
- Virgin status audit (A5 — Sable authority).
- Cost atlas ruling (A3 — Nova authority).
- Manifest mutation (A6 — requires user MWF cosign per R10).

Scope discipline is binding: this probe writes ONLY to `data/dll-probes/2023-12-WDOFUT/` (scratch dir, NOT touched by `data/in_sample/`, `data/holdout/`, `data/manifest.csv`).

### §1.3 Outcome consumes

- Council R4 outcome decision tree → ratify or abort A2-A8 chain.
- A2 input: schema parity audit needs first 1000 trades' actual column dtypes + value distributions.
- A3 input: confirms whether per-day mapping table for 2023 exists in Nelogica back-end (necessary precondition for archival).

---

## §2 Window: 2023-12-01..2023-12-20

### §2.1 Window choice rationale

| Constraint | Choice |
|---|---|
| Recent enough to minimize Q-PRE2024 schema-drift risk | December 2023 is the latest pre-2024 month available |
| Far enough back to validate retention claim concretely | 17 months pre-current (vs Sentinel manifest floor 2024-01-02) |
| Bounded by R1: "single month, 14 trading days max" | 2023-12-01..2023-12-20 = 20 calendar days; trading days breakdown below |
| Avoid year-end illiquidity confound | Cuts at 2023-12-20 (excludes Christmas week + New Year low-volume tape) |
| Avoid Carnaval / February holidays | Dec is post-Black Friday, pre-Christmas — typical Brazilian Q4 trading rhythm |

### §2.2 B3 trading days within 2023-12-01..2023-12-20

Per B3 official calendar 2023 (Nova authoritative; Nelo cites for completeness only):

| Date | Day-of-week | Trading? |
|---|---|---|
| 2023-12-01 (Fri) | Fri | YES |
| 2023-12-04..08 (Mon-Fri) | full week | YES (5d) |
| 2023-12-11..15 (Mon-Fri) | full week | YES (5d) |
| 2023-12-18..20 (Mon-Wed) | partial | YES (3d) |

**Total: ~14 trading days** (1 + 5 + 5 + 3). Fits R1 "14 trading days max" exactly.

**Holiday check:** No B3-closure holidays fall within 2023-12-01..2023-12-20 (Christmas 2023-12-25 is OUTSIDE the window; Imaculada Conceição 2023-12-08 is NOT a B3 holiday — confirmed by Nova authority defer).

### §2.3 Expected trade volume (informational, NOT a gate)

Per Sentinel empirical 2024-01..2025-06: ~9-14M trades/month for WDO. Pro-rata 14/21 trading days ≈ **~6-9M trades expected** for 2023-12-01..2023-12-20 IF the DLL serves this window normally.

**Sanity floor:** receiving fewer than 1M trades total → suspect partial-coverage outcome (R4 branch b).

**Sanity ceiling:** receiving more than 25M trades → likely DLL serving cross-session bleed; HOLD and inspect.

---

## §3 Ticker: WDOFUT (continuous proxy)

### §3.1 Ticker = WDOFUT (NEVER specific contracts pre-2024)

**Hard rule (R1 + Q09-E + canonical quirks §Tickers):**

- ✅ Use `"WDOFUT"` (synthetic continuous-contract alias resolved server-side).
- ❌ NEVER use `"WDOZ23"` (December 2023 specific contract — guaranteed 0 trades 19ms bug Q09-E).
- ❌ NEVER use `"WDOF24"`, `"WDOG24"`, etc. (specific expired contracts hit same Q09-E bug).
- ❌ NEVER use `"WINFUT"` for any historic (does NOT serve historic, see canonical quirks §Tickers — only contrato vigente works for WIN, but WIN out of A1 scope anyway).

### §3.2 Why WDOFUT specifically

Per Nelo §1.3 ballot:

> WDOFUT is the **synthetic continuous-contract alias** that the Nelogica back-end resolves at query time to the active rolling front-month contract for the date range requested. The DLL itself does NOT roll on the client side — the server stitches the historical sequence by mapping each date to its then-active front contract.

For 2023-12-01..2023-12-20 specifically, the back-end should map most days to **WDOZ23** (December 2023) up until rollover (3rd Wednesday = 2023-12-20) and then **WDOF24** (January 2024). Whether this mapping table is retained server-side for 2023 is precisely what A1 probes empirically.

### §3.3 Exchange code

Hard-coded `exchange = "F"` (Q03-V — manual §3.1 line 1673 literal example "Ticker: WINFUT, Bolsa: F"; NEVER `"BMF"` which returns NL_EXCHANGE_UNKNOWN).

---

## §4 DLL initialization sequence (canonical quirks compliance)

### §4.1 Function (NOT DLLInitialize)

```python
dll.DLLInitializeMarketLogin(
    activation_key,         # c_wchar_p — license key (env var DLL_ACTIVATION_KEY)
    user,                   # c_wchar_p — Nelogica login
    password,               # c_wchar_p — Nelogica password
    state_callback,         # WINFUNCTYPE — TStateCallback
    history_callback,       # WINFUNCTYPE — THistoryCallback (legacy order history) — placeholder
    order_change_callback,  # WINFUNCTYPE — TOrderChangeCallback — placeholder
    account_callback,       # WINFUNCTYPE — TAccountCallback — placeholder
    new_trade_callback,     # WINFUNCTYPE — TNewTradeCallback (real-time, NOT used in probe)
    new_daily_callback,     # WINFUNCTYPE — TNewDailyCallback — placeholder
    price_book_callback,    # WINFUNCTYPE — TPriceBookCallback — placeholder
    offer_book_callback,    # WINFUNCTYPE — TOfferBookCallback — placeholder
    history_trade_callback, # WINFUNCTYPE — THistoryTradeCallback (CRITICAL slot 9)
    progress_callback,      # WINFUNCTYPE — TProgressCallback (CRITICAL for telemetry)
    tiny_book_callback,     # WINFUNCTYPE — TTinyBookCallback — placeholder
)
```

**Hard rule per canonical quirks (Inicialização table):**
- ❌ `DLLInitialize` (does NOT exist for market-only mode)
- ✅ `DLLInitializeMarketLogin` (correct function for market-data-only mode without order routing)

### §4.2 Calling convention: WINFUNCTYPE (NOT CFUNCTYPE)

Per canonical quirks (Callbacks table) + Q01-V + manual §3.2 line 2735:

> "As funções de callbacks devem ser todas declaradas com a convenção de chamadas stdcall"

In Python ctypes: `WINFUNCTYPE` for stdcall (Windows 32-bit and 64-bit). Using `CFUNCTYPE` (cdecl) corrupts memory and aborts callbacks silently.

### §4.3 String type: c_wchar_p (NOT c_char_p)

Per canonical quirks + Q02-V + manual `PWideChar` convention:

- ✅ All string args declared as `c_wchar_p` (UTF-16 wide-char, Delphi PWideChar).
- ❌ `c_char_p` (UTF-8) corrupts strings — ticker / exchange / date strings will arrive as garbage.

### §4.4 Login readiness condition

Per canonical quirks (Inicialização table) — empirical from Whale Detector v2 live mode 2026-03-09:

```python
LOGIN_READY = (result == 2) and (conn_type in (1, 2))
```

⚠️ **Q-AMB-01 ambiguity acknowledged:** Manual §3.2 line 3317-3329 sugests `(conn_type=2, result=4)` (MARKET_CONNECTED). Empirical Whale Detector uses relaxed `(conn_type in (1,2), result=2)` (MARKET_WAITING) which has been observed sufficient to begin subscribe / GetHistoryTrades dispatch.

**Probe rule:** Wait up to 60 seconds for either condition. Log which condition fired first. If neither, abort with `LOGIN_TIMEOUT` outcome.

### §4.5 SetHistoryTradeCallback BEFORE init (NEVER after)

Per canonical quirks (Callbacks table) + Q11-E:

> SetHistoryTradeCallback após init → Nunca registrar após init — sobrescreve slot 9 silenciosamente

**Hard rule:** Pass `history_trade_callback` directly in slot 9 of `DLLInitializeMarketLogin`. Do NOT call `dll.SetHistoryTradeCallback(...)` after init — this silently overwrites slot 9 and causes the callback to fire into a stale function ptr.

### §4.6 _cb_refs global (prevent Python GC)

Per Q08-E (canonical quirks-extension; not in feedback_profitdll_quirks.md but in Nelo agent definition):

```python
_cb_refs = []  # Module-global list
_cb_refs.extend([on_state, on_trade, on_progress, on_history_trade, ...])
```

Without this list, Python GC may collect the WINFUNCTYPE wrappers after a few minutes, causing callbacks to silently stop firing. Universal rule (not specific to pre-2024).

---

## §5 Callback wiring

### §5.1 TStateCallback

```python
StateCB = WINFUNCTYPE(None, c_int, c_int)

@StateCB
def on_state(conn_type: int, result: int) -> None:
    """Tracks login state. Sets login_event when ready (§4.4)."""
    nonlocal_state["last_conn_type"] = conn_type
    nonlocal_state["last_result"] = result
    if result == 2 and conn_type in (1, 2):
        login_event.set()
    if result == 4 and conn_type == 2:
        login_event.set()  # Manual canonical condition
```

### §5.2 TProgressCallback (timeline log per minute)

```python
ProgressCB = WINFUNCTYPE(None, TAssetIDRec, c_int)

@ProgressCB
def on_progress(asset_id, progress: int) -> None:
    """Q10-E telemetry: log every 5% step + minute-level wall-clock delta."""
    now = time.time()
    last_progress = nonlocal_state["last_progress"]
    last_progress_ts = nonlocal_state["last_progress_ts"]
    nonlocal_state["last_progress"] = progress
    nonlocal_state["last_progress_ts"] = now
    progress_timeline.append({
        "ts_unix": now,
        "ts_brt": datetime.fromtimestamp(now).isoformat(),
        "progress": progress,
        "delta_s": (now - last_progress_ts) if last_progress_ts else 0.0,
    })
    if progress == 99:
        nonlocal_state["progress_99_started_ts"] = now
    if progress == 100 and nonlocal_state.get("progress_99_started_ts"):
        nonlocal_state["progress_99_dwell_s"] = (
            now - nonlocal_state["progress_99_started_ts"]
        )
```

**Q10-E expected behavior:** Progress sits at 99 for ~35-45s before jumping to 100. **Do NOT kill the process at this stall** (anti-pattern AP7).

### §5.3 THistoryTradeCallback → queue

```python
TradeCB = WINFUNCTYPE(
    None,
    TAssetIDRec,    # asset (.pwcTicker, .pwcBolsa)
    c_wchar_p,      # date string (raw — preserve verbatim per §6)
    c_uint,         # tradeNumber
    c_double,       # price
    c_double,       # vol (financial volume in BRL — Q07-V)
    c_int,          # qty (contracts)
    c_int,          # buy_agent_id
    c_int,          # sell_agent_id
    c_int,          # tradeType (2=BUY, 3=SELL — canonical quirks Callbacks)
)

@TradeCB
def on_history_trade(
    asset, date_raw, trade_num, price, vol, qty, buy_agent, sell_agent, trade_type
):
    """Enqueue raw tuple. NEVER call DLL inside callback (Q04-V)."""
    try:
        trade_queue.put_nowait((
            date_raw,           # raw string preserved (Q-AMB-02)
            asset.pwcTicker,    # normalized later
            float(price),
            int(qty),
            int(trade_type),
            int(buy_agent),
            int(sell_agent),
            float(vol),         # financial volume R$ — preserved (Q07-V)
        ))
    except queue.Full:
        nonlocal_state["queue_full_drops"] += 1
```

**Hard rule per Q04-V + manual §3.2 line 2730 + §4 line 4394:** Callbacks run on `ConnectorThread`; calling DLL functions or doing I/O inside them produces undefined behavior. Probe MUST use `queue.put_nowait()` exclusively.

### §5.4 Engine thread consumes queue + persists

```python
def engine_consumer(trade_queue, output_path, telemetry):
    """Run on the Python main thread (or dedicated worker).

    Drains trade_queue with a 100ms timeout. Persists to parquet in batches
    of 65_536 rows (matching feed_parquet AC8 row-batch sizing).
    Aggressor decoded HERE (not in callback): tradeType {2:'BUY', 3:'SELL'}
    else 'NONE' (canonical quirks Callbacks).
    """
```

The engine is the **only thread that writes to disk** and **resolves agent names** (if needed via `GetAgentName` — but A1 does NOT resolve agents during probe; raw `buy_agent_id` / `sell_agent_id` integers are persisted to parquet for A2 schema audit).

---

## §6 Timestamp handling

### §6.1 Raw timestamp string preserved (Q-AMB-02 ambiguity resolution)

Per Council R2: "raw timestamp string preserved (Q-AMB-02 ambiguity resolution)".

The DLL emits timestamp strings in one of two formats:

- **Manual canonical** (manual §3.2 line 3337): `"DD/MM/YYYY HH:mm:SS.ZZZ"` — separator before ms = `.`
- **Empirical Whale Detector**: `"DD/MM/YYYY HH:mm:SS:ZZZ"` — separator before ms = `:`

**Probe behavior:**

1. **Persist raw string** (column `ts_raw: STRING`) — exact bytes from DLL into parquet.
2. **Tolerant parse** to BRT-naive `datetime` (column `timestamp: TIMESTAMP[ns]`):
   ```python
   def parse_dll_ts(s: str) -> datetime:
       s_trim = s[:23]
       for fmt in ("%d/%m/%Y %H:%M:%S.%f", "%d/%m/%Y %H:%M:%S:%f"):
           try:
               return datetime.strptime(s_trim, fmt)
           except ValueError:
               continue
       raise ValueError(f"DLL ts unrecognized: {s!r}")
   ```
3. **Log first observed format** — telemetry tracks which separator the DLL emitted (helps adjudicate Q-AMB-02 across DLL versions).

### §6.2 BRT-naive convention (MANIFEST R2 + AP11)

Per MANIFEST R2 + AP11 (canonical quirks for consumers):

- ✅ Store as BRT-naive (no tzinfo, no UTC conversion).
- ❌ NEVER convert to UTC before storage — destroys session-phase semantics consumed by Nova / Beckett / Mira.

The DLL emits BRT (horário de Brasília) implicitly per empirical convention — manual is silent on timezone, but Sentinel + Whale Detector consistently confirm BRT.

---

## §7 Watchdogs

### §7.1 Idle watchdog (180s)

**Definition:** No `TProgressCallback` AND no `THistoryTradeCallback` fires for 180 consecutive seconds AFTER `GetHistoryTrades` is dispatched.

**Trigger:** Possible retention exhaustion (R4 branch c) OR DLL silent failure.

**Action:**
1. Log `watchdog_idle_triggered = True` to telemetry.
2. Continue waiting until hard timeout (§7.2) OR force shutdown — do NOT prematurely abort, because Q10-E means 99% can sit silently for 35-45s, and edge cases may extend that.
3. Mark outcome candidate as `retention_exhausted` for R4 classification.

**Implementation:** Python `threading.Timer` checking `time.time() - last_callback_ts > 180`.

### §7.2 Hard timeout (1800s = 30 min)

Per R2 + Q10-E + Nelo init guide: hard timeout 1800 seconds.

**Trigger:** Total wall-clock elapsed since `GetHistoryTrades` dispatched exceeds 1800s WITHOUT progress reaching 100.

**Action:**
1. Log `timeout_hit = True` to telemetry.
2. Force-stop callback consumption: drain remaining queue, persist what was received, classify outcome:
   - If trades > 0 received: `partial_coverage`.
   - If trades == 0 received: `retention_exhausted`.
3. Call `dll.UnsubscribeTicker` (defensive cleanup, even though we did not subscribe — DLL no-op safe per Q03-V semantics).
4. Call shutdown sequence per §10 (Finalize / DLLFinalize tolerant).

### §7.3 Why these thresholds

| Threshold | Rationale |
|---|---|
| 180s idle | Q10-E 99% pause is 35-45s (canonical); extreme tail observed up to ~120s; 180s gives 50% margin without false-positives |
| 1800s hard | Per Nelo §3.1 ballot + Q10-E protection envelope; pre-2024 may exhibit longer connection cycling than 2024+ Sentinel runs |

---

## §8 Schema validation (first 1000 trades)

### §8.1 Expected canonical 7-column schema

Per Sentinel canonical (current Sentinel manifest) + Council R5 schema parity baseline:

| Column | Dtype | Notes |
|---|---|---|
| `timestamp` | `TIMESTAMP[ns]` BRT-naive | Parsed from `ts_raw` per §6.1 |
| `ticker` | `STRING` | DLL emits "WDO" (normalized from "WDOFUT" continuous alias) — Sentinel convention |
| `price` | `DOUBLE` | Float64 |
| `qty` | `INT64` | Number of contracts (NOT financial volume) |
| `aggressor` | `STRING` | Decoded from tradeType: 2→"BUY", 3→"SELL", else→"NONE" |
| `buy_agent` | `INT64` | Numeric agent_id (NOT name); resolved later if needed |
| `sell_agent` | `INT64` | Numeric agent_id |

**Plus probe-only columns** (NOT in canonical 7 — these are A1-specific telemetry):
- `ts_raw` (STRING) — raw DLL timestamp string preserved per §6.1
- `vol_brl` (DOUBLE) — financial volume R$ from DLL `vol` arg (Q07-V; A2 will decide whether to keep in canonical or drop)

### §8.2 First 1000 trades validation harness

**On the 1000th trade received** (after engine consumer drains it from queue):

```python
def validate_first_1000(batch: list[dict]) -> dict:
    """Run schema + sanity checks on first 1000 trades."""
    checks = {}

    # Dtype validation
    checks["dtype_timestamp"] = all(
        isinstance(t["timestamp"], datetime) and t["timestamp"].tzinfo is None
        for t in batch
    )
    checks["dtype_price_double"] = all(isinstance(t["price"], float) for t in batch)
    checks["dtype_qty_int"] = all(isinstance(t["qty"], int) for t in batch)
    checks["dtype_aggressor_str"] = all(
        t["aggressor"] in ("BUY", "SELL", "NONE") for t in batch
    )

    # Sanity checks
    checks["sanity_price_positive"] = all(t["price"] > 0 for t in batch)
    checks["sanity_qty_positive"] = all(t["qty"] > 0 for t in batch)
    checks["sanity_ticker_normalized"] = all(t["ticker"] == "WDO" for t in batch)

    # Aggressor distribution sanity (BUY/SELL should be majority; NONE rare)
    n_buy = sum(1 for t in batch if t["aggressor"] == "BUY")
    n_sell = sum(1 for t in batch if t["aggressor"] == "SELL")
    n_none = sum(1 for t in batch if t["aggressor"] == "NONE")
    checks["sanity_aggressor_distribution"] = (
        n_buy + n_sell >= 0.80 * len(batch)  # ≥80% directional
    )

    # Timestamp monotonicity (within window — DLL is supposed to deliver
    # historical trades in temporal order, but allow ties)
    ts_list = [t["timestamp"] for t in batch]
    checks["sanity_ts_monotonic_nondec"] = all(
        ts_list[i] <= ts_list[i+1] for i in range(len(ts_list)-1)
    )

    # Window adherence
    target_start = datetime(2023, 12, 1, 9, 0)
    target_end = datetime(2023, 12, 20, 18, 0, 1)  # +1s slack
    checks["sanity_in_window"] = all(
        target_start <= t["timestamp"] <= target_end for t in batch
    )

    checks["pass_overall"] = all(checks.values())
    return checks
```

### §8.3 Failure handling

If `pass_overall == False`:

1. Log full check breakdown to telemetry.
2. **Continue receiving** trades (do NOT abort — gather full data for forensic analysis).
3. Mark outcome candidate as `partial_coverage` with `schema_validation_pass = False`.
4. Council Decision Tree (R4) routes this to "HOLD — escalate to council; do not proceed to bulk backfill until anomaly understood".

---

## §9 Outcome telemetry export

### §9.1 Telemetry fields (probe-telemetry-{run_id}.json)

```json
{
  "probe_run_id": "uuid4",
  "probe_spec_version": "A1-spec-2023-12-WDOFUT-v1.0",
  "council_resolution_ref": "COUNCIL-2026-05-01-DATA-resolution.md",

  "start_ts_brt": "ISO-8601 BRT-naive — when probe started",
  "end_ts_brt": "ISO-8601 BRT-naive — when probe ended (success or fail)",
  "wall_clock_duration_s": 0.0,

  "request": {
    "function": "GetHistoryTrades",
    "ticker": "WDOFUT",
    "exchange": "F",
    "start_str": "01/12/2023 09:00:00",
    "end_str": "20/12/2023 18:00:00"
  },

  "dll_response": {
    "return_code": 0,
    "return_code_name": "NL_OK",
    "login_ready": true,
    "login_ready_condition_observed": "result==2 and conn_type==2",
    "login_wait_s": 0.0
  },

  "trades": {
    "total_received": 0,
    "first_trade_ts_brt": null,
    "last_trade_ts_brt": null,
    "first_trade_ts_raw": null,
    "ts_separator_observed": ".",
    "queue_full_drops": 0
  },

  "progress": {
    "timeline": [
      {"ts_unix": 0, "ts_brt": "...", "progress": 1, "delta_s": 0}
    ],
    "progress_99_dwell_s": 0.0,
    "reached_100": true
  },

  "schema_validation": {
    "first_1000_complete": true,
    "checks": {
      "dtype_timestamp": true,
      "dtype_price_double": true,
      "dtype_qty_int": true,
      "dtype_aggressor_str": true,
      "sanity_price_positive": true,
      "sanity_qty_positive": true,
      "sanity_ticker_normalized": true,
      "sanity_aggressor_distribution": true,
      "sanity_ts_monotonic_nondec": true,
      "sanity_in_window": true,
      "pass_overall": true
    }
  },

  "watchdogs": {
    "watchdog_idle_triggered": false,
    "watchdog_idle_at_progress": null,
    "timeout_hit": false
  },

  "anti_patterns_audit": {
    "AP-D-01": "PASS",  "AP-D-02": "PASS",  "AP-D-03": "PASS",
    "AP-D-04": "PASS",  "AP-D-05": "CHECK", "AP-D-06": "CHECK",
    "AP-D-07": "N/A",   "AP-D-08": "N/A",   "AP-D-09": "N/A",
    "AP-D-10": "N/A",   "AP-D-11": "PASS",  "AP-D-12": "PASS",
    "AP-D-13": "N/A"
  },

  "outcome_classification": "full_month_works",
  "outcome_decision_tree_branch": "R4(a)",
  "outcome_rationale": "≥1M trades + schema validation pass + reached 100% + no watchdog trigger"
}
```

### §9.2 Outcome classification (R4 decision tree)

| Outcome | Trigger | R4 Branch |
|---|---|---|
| `full_month_works` | trades ≥ 1M AND schema_validation pass AND reached_100 AND NOT watchdog_idle_triggered AND NOT timeout_hit | R4(a) → ratify Path C extension |
| `partial_coverage` | trades > 0 AND (trades < 1M OR schema fail OR watchdog_idle OR timeout_hit but with data) | R4(b) → ratify with caveat (council escalation) |
| `retention_exhausted` | trades == 0 (regardless of return code, whether NL_SERIE_NO_HISTORY or 0-trades-19ms or watchdog) | R4(c) → confirm pre-2024 retention exhausted, abort Path A, fallback Path B |
| `error` | login_timeout OR DLL load failure OR uncaught exception | (out of R4 branches — escalate to Nelo + Dara joint debug) |

### §9.3 Trade data export (parquet)

`data/dll-probes/2023-12-WDOFUT/wdofut-2023-12-{run_id}.parquet` — full trade table received during probe (could be 0 rows or 9M rows depending on outcome). Columns per §8.1.

---

## §10 Anti-pattern monitoring (AP-D-01..AP-D-13)

| ID | Anti-pattern | Probe audit field | Default verdict logic |
|---|---|---|---|
| AP-D-01 | DLL retention exhaustion silent gaps | `outcome_classification != "retention_exhausted"` | Set during outcome classification |
| AP-D-02 | WDOFUT specific contracts pre-2024 → 0 trades | `request.ticker == "WDOFUT"` | Always PASS by spec design (we hard-code WDOFUT) |
| AP-D-03 | Threading WINFUNCTYPE/c_wchar_p violations | Static check on script (Quinn QA gate) | PASS if script uses WINFUNCTYPE + c_wchar_p exclusively |
| AP-D-04 | SetHistoryTradeCallback after init silent overwrite | Static check: callback passed in slot 9 of DLLInitializeMarketLogin only | PASS if no `dll.SetHistoryTradeCallback(...)` call appears post-init |
| AP-D-05 | 99% progress 35-45s pause WAIT not crash | `progress_99_dwell_s` recorded AND watchdog_idle threshold ≥ 180s | CHECK = informational, observed dwell logged |
| AP-D-06 | Sentinel ESC-009 pre-2024 failure precedent | Probe outcome distinct from Sentinel ESC-009 — Dara cross-references during A2 | CHECK = Dara reviews during A2 |
| AP-D-07 | Cost atlas v1.0.0 calibration drift pre-2024 | Out of probe scope (Nova authority A3) | N/A |
| AP-D-08 | Regime non-equivalence | Out of probe scope (Mira authority A4) | N/A |
| AP-D-09 | Engine-config v1.1.0 semantic mismatch pre-RLP | Out of probe scope (Beckett authority post-A4) | N/A |
| AP-D-10 | Virgin-by-availability ≠ virgin-by-discipline | Out of probe scope (Sable authority A5) | N/A |
| AP-D-11 | Closed-source Win64 reproducibility threat | Probe DLL version captured to telemetry | PASS if `dll_version` field populated |
| AP-D-12 | Manifest mutation without user MWF cosign | Probe writes to scratch only (`data/dll-probes/`) | PASS if no `data/manifest.csv` mutation occurs |
| AP-D-13 | Pre-2024 promotion to PRIMARY OOS | Out of probe scope (R12 governance binding) | N/A |

---

## §11 Execution authority

### §11.1 Specification vs. execution separation (MANIFEST R12-R14)

| Role | Authority | Action |
|---|---|---|
| Nelo (@profitdll-specialist) | DOMAIN — DLL correctness, manual fidelity, quirks compliance | Authors this spec + companion script; reviews script for AP-D-03/04/11 compliance |
| Dara (@data-engineer) | FRAMEWORK — execution, parquet persistence, DB layouts | Executes script; persists artifacts to `data/dll-probes/`; reports outcome to council |
| Quinn (@qa) | FRAMEWORK — quality gate | QA-reviews script before run (argtypes/restype, _cb_refs, exchange="F", timeout, schema-validation harness) |
| Pax (@po) | FRAMEWORK — story validation | Authorizes execution via story (10-point checklist) |
| Sable (@governance) | DOMAIN — virgin status custody | Audits scratch data handling (probe data NEVER moves to `data/in_sample/` or `data/holdout/` without A5 cosign) |
| Gage (@devops) | EXCLUSIVE — git push | Only agent who can push any A1 artifacts (this doc + script) (Article II) |

### §11.2 Nelo's only execution boundary

Nelo does NOT execute production DLL calls. Nelo authors the spec (this doc) + the companion script (`scripts/dll_probe_2023_12_wdofut.py`). Dara executes under Pax story authorization.

This separation prevents domain-specialist drift into operational execution and ensures every probe run has a governance audit trail (story → QA gate → execution → council report).

---

## §12 Output destination

### §12.1 Scratch directory (NOT in_sample, NOT holdout, NOT manifest)

All probe outputs land in:

```
data/dll-probes/2023-12-WDOFUT/
├── wdofut-2023-12-{run_id}.parquet         # trade data
├── probe-telemetry-{run_id}.json           # §9 telemetry
├── progress-timeline-{run_id}.csv          # §5.2 minute-level log
└── probe-stdout-stderr-{run_id}.log        # process log
```

### §12.2 Discipline rules

- ❌ **NEVER** write to `data/in_sample/year=*/` (T002 hot-path).
- ❌ **NEVER** write to `data/holdout/` (Sentinel hold-out lock).
- ❌ **NEVER** mutate `data/manifest.csv` (R10 absolute custodial — needs A6 user MWF cosign per Council R10).
- ❌ **NEVER** mutate `data/manifest_PREVIEW.csv` (dev fixture, also custodial).
- ✅ Write **only** to `data/dll-probes/2023-12-WDOFUT/` (this is a NEW scratch directory created by the probe).

### §12.3 Custodial transition path (NOT A1 scope)

If outcome is `full_month_works` and Council ratifies A2-A8, the path forward is:

1. A2: Dara byte-equal schema parity audit on probe parquet.
2. A3: Nova cost atlas pre-2024 ruling.
3. A4: Mira regime check.
4. A5: Sable virgin audit.
5. A6: Pax 10-point validate + **user MWF cosign** for manifest mutation.
6. A7: Bulk backfill 2023-Q1..2024-Q3 → `data/archive/year=2023/month=*/` + manifest extension with `phase=archive`.

**A6 user MWF cosign is the gate** that authorizes ANY movement out of scratch. Probe data NEVER promotes itself.

### §12.4 Cleanup policy

- Probe artifacts are RETAINED indefinitely (forensic value for future debugging + audit trail).
- `.gitignore` includes `data/dll-probes/*.parquet` (large binary; never committed). Telemetry JSON files MAY be committed if council requests — Dara decides.

---

## §13 Article IV self-audit (source anchors)

Every clause in this spec traces to one of:

1. **Council resolution** (`docs/councils/COUNCIL-2026-05-01-DATA-resolution.md`) — R1, R2, R3, R4, R10, R12, R13.
2. **Nelo ballot §3.1** (`docs/councils/COUNCIL-2026-05-01-DATA-dll-backfill-nelo-vote.md`) — probe spec authority, anti-patterns AP1-AP13.
3. **Canonical quirks** (`feedback_profitdll_quirks.md`, 2026-04-25) — Inicialização table, Callbacks table, Tickers e exchanges table, agent resolution rule.
4. **Manual oficial** (`manual_profitdll.txt`) — §3.1 GetHistoryTrades signature + line 1737-1745 date format + line 1673 exchange "F" example; §3.2 line 2730 callback-no-DLL rule + line 2735 stdcall + line 3730 THistoryTradeCallback + line 3750 TProgressCallback; §3 line 894-955 NL_* error codes.
5. **Existing adapters** (`packages/t002_eod_unwind/adapters/feed_parquet.py`, `feed_timescale.py`) — pattern reference for batching, BRT-naive convention, hold-out discipline (NOT consumed by probe; reference only).
6. **Sentinel empirical** (current `data/manifest.csv` — 2024-01..2025-06 WDOFUT proven viable) — empirical adjacency to retention floor question.
7. **Quirk registry** (Nelo agent definition embedded) — Q01-V, Q02-V, Q03-V, Q04-V, Q07-V, Q08-E, Q10-E, Q11-E, Q-AMB-01, Q-AMB-02.

**No invented retention claims. No invented vendor commitments. Where evidence is silent or absent, this spec defers to the empirical probe outcome (R4 decision tree branches a/b/c) for adjudication.**

---

## §14 Cosign

Cosign Nelo @profitdll-specialist 2026-05-01 BRT — A1 probe spec authored per Data Council R1-R4.

Branch: `t003-a1-dll-probe-2023-12`. Doc-only artifact (this spec + companion script). No source mutation outside scope. No DLL execution. No push. No manifest mutation.

— Nelo, guardião da DLL.
