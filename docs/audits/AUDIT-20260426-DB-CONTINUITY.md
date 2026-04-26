---
date: 2026-04-26 BRT
author: Dara (@data-engineer)
trigger: User reported 2023 = ~3 random days; previous Dara claim "570 chunks 2023-2026" RETRACTED. Re-audit (second attempt) under Autonomous Daily Session post Docker engine restoration.
mode: Autonomous Daily Session — second attempt post Docker restoration
status: ABORTED — DOCKER_DAEMON_DOWN_500 (no SQL evidence collected)
related:
  - docs/audits/AUDIT-20260425-PRE-DRYRUN-CPCV.md
  - feedback_cpcv_dry_run_memory_protocol (global memory)
---

# DB Continuity Audit — sentinel-timescaledb trades hypertable

> **Outcome:** Audit aborted at Section 1 (connection probe). Docker Desktop Linux engine pipe is reachable but every API endpoint returns HTTP 500 Internal Server Error, and the backing Windows service `com.docker.service` is Stopped. No SQL queries against TimescaleDB were executed; therefore **no new continuity evidence is produced by this audit run**. Article IV (No Invention) requires this be recorded as-is — no extrapolation from prior (retracted) numbers, no inference about chunk distribution.

---

## 1. Connection status

**Verdict:** FAIL — Docker daemon unreachable; `docker exec` against `sentinel-timescaledb` impossible.

### 1.1 Probes executed (all from project cwd, Windows host)

| # | Command | Result | Notes |
|---|---------|--------|-------|
| 1 | `docker ps --format '...'` | exit 1 | `500 Internal Server Error` from `//./pipe/dockerDesktopLinuxEngine/v1.53/containers/json` |
| 2 | `docker exec sentinel-timescaledb pg_isready -U sentinel -d sentinel_db` | exit 1 | `500 Internal Server Error` from `.../containers/sentinel-timescaledb/json` (cannot inspect → cannot exec) |
| 3 | `docker version` | partial | Client section returned (29.2.1, API 1.53, Built 2026-02-02). Server section: `500 Internal Server Error` from `.../v1.53/version` |
| 4 | `docker info --format '{{.ServerVersion}} {{.OSType}}'` | exit 0 (text-only) | `500 Internal Server Error` from `.../v1.53/info` |
| 5 | `DOCKER_API_VERSION=1.47 docker ps` (downgrade probe) | exit 1 | `500 Internal Server Error` from `.../v1.47/containers/json` — not an API-version mismatch |
| 6 | `Get-Service *docker*` | exit 0 | `com.docker.service` → **Status: Stopped, StartType: Manual** |

### 1.2 Diagnosis

- The named pipe `\\.\pipe\dockerDesktopLinuxEngine` accepts connections (no "pipe not found" / "cannot connect to the Docker daemon" error), so Docker Desktop is partially up.
- Every HTTP method to that pipe returns a generic **500 Internal Server Error** regardless of API version negotiated (1.53 → 1.47 same behaviour). Failure is on the daemon side, not API-handshake mismatch.
- The Windows service that backs Docker Desktop's privileged operations (`com.docker.service`) is **Stopped**. Without it, the Linux VM / engine cannot service container API calls even though the front-door pipe responds.
- Therefore the user statement "Container `sentinel-timescaledb` UP" cannot currently be verified from this host, and `docker exec` is not possible. No SQL session can be opened against TimescaleDB through Docker.

### 1.3 Defensive stop rationale

Per task protocol ("queries with timeout 60s; abort if exceeded; do not drain resources"), this audit abort is triggered **before** any query was sent — the bottleneck is upstream of Postgres. Continuing would only re-issue the same 500-returning probes. No new information would emerge.

---

## 2. Chunk distribution per year (via timescaledb_information.chunks)

NOT EXECUTED — no DB session available (see §1).

| yr | chunk_count | first_day | last_day |
|----|-------------|-----------|----------|
| —  | —           | —         | —        |

---

## 3. 2023 chunks enumeration (user claim: ~3 random days)

NOT EXECUTED — no DB session available.

- **Verdict:** UNVERIFIED in this audit run. The user's empirical statement ("sim eu acho q temos 3 dias de 2023 aleatorios, n podemos usar isso pra nada") remains the only operative evidence about 2023, and it stands as the ground truth pending re-validation. The previous Dara claim of "570 chunks spanning 2023–2026" remains **RETRACTED** (mea culpa from prior session) and is **NOT reinstated** by this audit.

---

## 4. Hold-out window chunks (2025-07-01 → 2026-04-21)

NOT EXECUTED — no DB session available.

- **Verdict:** UNVERIFIED in this audit run. Density of the hold-out window in `trades` cannot be confirmed or refuted from host today.

---

## 5. Total estimate (no COUNT(*) — reltuples)

NOT EXECUTED — no DB session available.

- Estimated total rows: **UNKNOWN**
- Chunk count: **UNKNOWN**

---

## 6. Implications

### 6.1 ESC-001 (`as_of=2024-06-30`)
- **Status unchanged.** Audit produced no new evidence that would unblock or further confirm ESC-001. The prior closure rationale (user-confirmed 2023 ≈ 3 random days → no usable warm-up history before 2024-06-30) is **not contradicted** by anything observed today; it is simply not re-validated either.
- **Action:** Do NOT relax ESC-001 on the strength of this audit. Wait for Docker engine to recover and re-run §2–§5.

### 6.2 ESC-002 (hold-out window density)
- **Status unchanged.** No empirical confirmation that DB has hold-out data for 2025-07-01 → 2026-04-21. The LAYERED_SAFE rationale (defense-in-code at the caller boundary) remains correct as a code-level invariant regardless of DB state, but the operational claim "DB has hold-out data populated" is **NOT verified today**.
- **Action:** The user must continue to be told, in any decision artefact citing hold-out data, that DB density of that window has not been re-confirmed since 2026-04-25. No CPCV dry-run promotion should rely on a chunk-count assertion sourced from this audit.

### 6.3 Operational follow-up (out of scope for Dara — flagged for @devops / user)
- `com.docker.service` needs to be started (or Docker Desktop needs a clean restart) before any further DB-side audit is meaningful.
- Once the daemon is healthy (`docker info` returns server version cleanly), this audit should be re-run end-to-end and a new dated file produced (e.g. `AUDIT-20260426b-DB-CONTINUITY.md` or successor).

---

## 7. Article IV trace

| Claim in this document | Evidence cited |
|------------------------|----------------|
| Docker Desktop Linux engine pipe reachable | Probes 1–5 all returned an HTTP 500 from the named pipe (not "pipe not found"). |
| Failure is daemon-side, not API negotiation | Probe 5 (`DOCKER_API_VERSION=1.47`) reproduced the same 500 against a different API version — eliminates version-mismatch hypothesis. |
| `com.docker.service` is Stopped | Probe 6 (`Get-Service *docker*`) — Status column literally "Stopped". |
| `docker exec` against `sentinel-timescaledb` not possible | Probe 2 — container inspect failed before exec was attempted. |
| 2023 = ~3 random days | User statement (out-of-band, prior session). NOT independently re-verified by this audit. Carried forward as user testimony, flagged as such. |
| Previous "570 chunks 2023–2026" claim | Retracted in prior Dara mea-culpa. NOT reinstated and NOT used in any §6 conclusion. |
| §2–§5 numerical fields | Empty / "UNKNOWN" — explicitly **NOT** filled with extrapolation from prior runs. |
| ESC-001 / ESC-002 status "unchanged" | Direct consequence of "no new evidence collected today". No optimistic narrative grafted on top. |

**Lesson reinforced:** metadata range ≠ continuity — but absent metadata altogether, the correct posture is "unknown", not "previously asserted value".

---

## §3 — Attempt 3 (post 2nd Docker restart)

- **Date:** 2026-04-26 BRT
- **Container status:** UP (`sentinel-timescaledb` Up 3-4 minutes at audit start)
- **Postgres readiness:** READY (`pg_isready` exit 0, "accepting connections")
- **Audit strategy:** Defensive 3-query sequence via `timescaledb_information.chunks` metadata only (no COUNT(*), no cross-year scans). Each query wrapped in `timeout 30`.
- **Docker survival:** YES — container still UP after all 3 queries completed (Up 4 minutes post-audit).

### Q1 result (chunks per year) — empirical, no extrapolation

| yr | chunk_count | first_day | last_day |
|----|-------------|-----------|----------|
| 2023 | 6 | 2023-01-02 | 2023-01-10 |
| 2024 | 251 | 2024-01-02 | 2024-12-31 |
| 2025 | 250 | 2025-01-02 | 2025-12-31 |
| 2026 | 63 | 2026-01-02 | 2026-04-03 |

**Observation:** 2024 and 2025 show ~250 chunks each (consistent with daily-chunked trading days, ~252 sessions/year). 2026 has 63 chunks through 2026-04-03 (also consistent with YTD trading days). 2023 has only 6 chunks, all clustered in early January.

### Q2 result (2023 chunks explicit listing)

| day_start | day_end | size |
|-----------|---------|------|
| 2023-01-02 | 2023-01-03 | 80 MB |
| 2023-01-03 | 2023-01-04 | 140 MB |
| 2023-01-04 | 2023-01-05 | 130 MB |
| 2023-01-05 | 2023-01-06 | 121 MB |
| 2023-01-06 | 2023-01-07 | 122 MB |
| 2023-01-09 | 2023-01-10 | 126 MB |

**User claim re-validation:** User said "~3 dias de 2023 aleatórios". Empirical finding: **6 chunks, NOT random — consecutive trading days Jan 2-6 plus Jan 9, 2023** (Jan 7-8 = weekend). Total ~720 MB of trades data. The data is **clustered in a single week of January 2023**, then nothing for the rest of the year. User's intuition (unusable for warmup) **stands** — 1 week of January is insufficient as a warm-up baseline regardless of being non-random — but the precise count differs (6 days, not 3, all consecutive within Jan 2-9).

### Q3 result (hold-out window chunks 2025-07-01 → 2026-04-22)

- **Chunks returned:** 100 (limit reached — actual count likely higher; range only consumed 2025-07-01 → 2025-11-17 in the first 100 rows)
- **CRITICAL FINDING — chunk size:** Every single chunk in the listing reports `0 bytes` from `pg_relation_size`. All 100 chunks are **size-zero**.
- Sample: 2025-07-01 → 0 bytes, 2025-08-01 → 0 bytes, …, 2025-11-17 → 0 bytes (100 consecutive trading-day chunks, all empty).

**Interpretation (caveat — this is the one inference, flagged):**
- TimescaleDB created chunk metadata for these dates (likely from a schema-level seeding or an earlier ingestion attempt that wrote no rows), but the relations are physically empty.
- Alternative hypothesis: chunks may be compressed and `pg_relation_size` is reporting only the uncompressed heap (0 because everything migrated to compressed segments). **NOT VERIFIED in this audit** — would require a follow-up query against `chunk_compression_stats` or equivalent. Flagged for follow-up before any density claim is made.

### Verdict

- **2023 user claim:** PARTIALLY CONFIRMED — user said "~3 random days", actual is "6 consecutive days in week of Jan 2-9 2023". Operative conclusion (unusable for warm-up) **stands**. Numerical detail differs.
- **Hold-out density:** **AMBIGUOUS** — metadata says 100+ chunks exist, but `pg_relation_size = 0` for every one. Either truly empty (DENSE_BY_METADATA / EMPTY_BY_DATA) or compressed (needs verification). Cannot declare DENSE without compression check.
- **ESC-001 status:** **DEFINITIVELY BLOCKED** confirmed. With only 6 days of Jan 2023 + nothing until Jan 2024, no `as_of=2024-06-30` warm-up is feasible from history alone. No new path opened.
- **ESC-002 status:** **NEEDS_DB_GUARD** — LAYERED_SAFE at L3 remains correct as a code invariant, but the operational claim "DB has hold-out data populated" is **NOT confirmed empirically** (zero-size chunks raise a red flag). A DB-side guard (e.g., assert non-zero row count for any window the strategy reads from) is now justified before any CPCV dry-run promotion.

### Action items (ordered)

1. **[Dara, follow-up]** Run a single follow-up query against `timescaledb_information.compressed_chunk_stats` (or `chunk_compression_stats`) for the hold-out window to determine whether 0-byte chunks are compressed-with-data or genuinely empty. ONE query, timeout 30, defensive.
2. **[Dara → @architect]** If chunks confirmed empty: escalate ESC-002 from LAYERED_SAFE to **HARD_BLOCK** for any CPCV dry-run that depends on hold-out trades data. Strategy code must be guarded against zero-row windows.
3. **[Dara → @pm]** Update T002 state memory: 2023 chunk count corrected from "~3 random" to "6 consecutive Jan 2-9 days, ~720 MB"; user's operational conclusion ("can't use it") preserved.
4. **[@devops, out of scope for Dara]** Investigate Docker daemon instability — daemon crashed twice in a single session today. Likely WSL2 memory pressure on Windows host. Capture diagnostics before next crash.
5. **[Dara, governance]** Append this attempt's evidence to `feedback_cpcv_dry_run_memory_protocol` global memory so the empirical chunk distribution is durable across sessions (replaces the retracted "570 chunks" assertion definitively).

### Article IV trace (Attempt 3)

| Claim | Evidence |
|-------|----------|
| Container UP | `docker ps` returned `sentinel-timescaledb \| Up 3 minutes` (then Up 4 minutes post-audit). |
| Postgres READY | `pg_isready -U sentinel -d sentinel_db -t 5` exit 0, "accepting connections". |
| 2023 = 6 chunks Jan 2-9 | Q1 + Q2 raw output (chunk_count=6, range 2023-01-02 → 2023-01-10, sizes 80-140 MB). |
| 2024/2025 ~250 chunks each | Q1 raw output (251 / 250). |
| 2026 = 63 chunks through Apr 3 | Q1 raw output. |
| Hold-out 100+ chunks, 0 bytes each | Q3 raw output (100 rows, every `pg_relation_size` value = `0 bytes`). |
| Compression hypothesis NOT verified | Q3 used `pg_relation_size`, not `chunk_compression_stats`. Flagged in §3 Q3 interpretation. |
| Docker survived | `docker ps` post-audit shows `Up 4 minutes` (no crash during 3 queries). |

