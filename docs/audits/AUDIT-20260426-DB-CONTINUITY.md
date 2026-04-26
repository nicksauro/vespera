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
