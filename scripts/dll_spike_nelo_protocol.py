"""DLL spike protocol — Nelo audit pre-backfill (S1 + S2 + S3).

NOT a Council-binding probe. Diagnostic spikes only. Outputs go to
data/dll-probes/SPIKE-NELO/ for audit consumption.

Spike S1 — Retention floor (6 probes, 1d each, WDOFUT continuous)
    Map oldest date where DLL serves trades. Probe schedule:
    2023-11-15, 2023-09-15, 2023-07-15, 2023-05-15, 2023-03-15, 2023-01-16
    Outcomes per probe: trades > 0 (OK), trades == 0 (retention_exhausted),
    NL_INVALID_ARGS (arg fail), other.

Spike S2 — Range limit binary search (3 probes)
    5d=OK, 20d=NL_INVALID_ARGS confirmed empirically. Map exact boundary.
    Probes: 7d (2023-12-04..10), 10d (2023-12-04..13), 15d (2023-12-04..18).
    First NL_OK ceiling tells us optimal chunk size for backfill.

Spike S3 — Roll boundary (1 probe, cross-month)
    Test if WDOFUT continuous in DLL handles month-roll cleanly.
    Probe: 2023-03-29..2023-04-03 (5d) — crosses WDOH23→WDOJ23 vencimento.
    Audit: trade_number monotonic across the roll? Volume bate por dia?

All spikes use Phase-1-fixed run_probe() with monkey-patched _OUTPUT_DIR
and short _HARD_TIMEOUT_S (90s — confirmed sufficient for ~5M trades).
Sequential execution (DLL single-instance).
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import dll_probe_2023_12_wdofut as probe  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
SPIKE_DIR = REPO_ROOT / "data" / "dll-probes" / "SPIKE-NELO"
SPIKE_DIR.mkdir(parents=True, exist_ok=True)

probe._HARD_TIMEOUT_S = 90.0
probe._IDLE_WATCHDOG_S = 30.0


def run_one_spike(label: str, start_date: str, end_date: str, ticker: str = "WDOFUT") -> dict:
    """Run a single spike with isolated output dir. Returns summary dict."""
    spike_subdir = SPIKE_DIR / label
    spike_subdir.mkdir(parents=True, exist_ok=True)
    probe._OUTPUT_DIR = spike_subdir

    print(f"\n{'='*70}\n[SPIKE {label}] {start_date}..{end_date} ticker={ticker}\n{'='*70}", flush=True)
    t0 = time.time()
    try:
        exit_code = probe.run_probe(
            start_date=start_date,
            end_date=end_date,
            ticker=ticker,
            dll_path=os.environ["DLL_PATH"],
            activation_key=os.environ["DLL_ACTIVATION_KEY"],
            user=os.environ["DLL_USER"],
            password=os.environ["DLL_PASSWORD"],
        )
    except SystemExit as e:
        exit_code = int(e.code) if e.code is not None else 3
    except Exception as e:
        print(f"[SPIKE {label}] EXCEPTION: {type(e).__name__}: {e}", flush=True)
        exit_code = 3

    elapsed = time.time() - t0

    summary = {
        "label": label,
        "start_date": start_date,
        "end_date": end_date,
        "ticker": ticker,
        "exit_code": exit_code,
        "wall_clock_s": round(elapsed, 1),
    }

    telemetries = sorted(spike_subdir.glob("probe-telemetry-*.json"))
    if telemetries:
        latest = telemetries[-1]
        try:
            with latest.open(encoding="utf-8") as fh:
                tele = json.load(fh)
            summary["return_code"] = tele.get("dll_response", {}).get("return_code")
            summary["return_code_name"] = tele.get("dll_response", {}).get("return_code_name")
            summary["trades_total"] = tele.get("trades", {}).get("total_received")
            summary["trades_persisted"] = tele.get("trades", {}).get("persisted_rows")
            summary["queue_full_drops"] = tele.get("trades", {}).get("queue_full_drops")
            summary["reached_100"] = tele.get("progress", {}).get("reached_100")
            summary["outcome"] = tele.get("outcome_classification")
            summary["telemetry_path"] = str(latest.relative_to(REPO_ROOT))
        except Exception as e:
            summary["telemetry_parse_error"] = str(e)
    else:
        summary["telemetry_missing"] = True

    print(f"[SPIKE {label}] DONE — exit={exit_code}, elapsed={elapsed:.1f}s", flush=True)
    return summary


def main() -> int:
    for var in ("DLL_PATH", "DLL_ACTIVATION_KEY", "DLL_USER", "DLL_PASSWORD"):
        if not os.environ.get(var):
            print(f"ERROR: env var {var} not set", file=sys.stderr)
            return 3

    all_spikes = {
        "S1a": [
            ("S1-2023-01-16", "2023-01-16", "2023-01-16"),
            ("S1-2023-03-15", "2023-03-15", "2023-03-15"),
            ("S1-2023-05-15", "2023-05-15", "2023-05-15"),
        ],
        "S1b": [
            ("S1-2023-07-17", "2023-07-17", "2023-07-17"),
            ("S1-2023-09-15", "2023-09-15", "2023-09-15"),
            ("S1-2023-11-16", "2023-11-16", "2023-11-16"),
        ],
        "S2": [
            ("S2-7d-2023-12-04_10", "2023-12-04", "2023-12-10"),
            ("S2-10d-2023-12-04_13", "2023-12-04", "2023-12-13"),
            ("S2-15d-2023-12-04_18", "2023-12-04", "2023-12-18"),
        ],
        "S3": [
            ("S3-roll-2023-03-29_04-03", "2023-03-29", "2023-04-03"),
        ],
        "S1-retry-0315": [
            ("S1-2023-03-15-retry", "2023-03-15", "2023-03-15"),
        ],
        "S1-retry-0915": [
            ("S1-2023-09-15-retry", "2023-09-15", "2023-09-15"),
        ],
        "S1-retry2-0315": [
            ("S1-2023-03-15-retry2", "2023-03-15", "2023-03-15"),
        ],
        "parity-test-2023-12-26_29": [
            ("PARITY-2023-12-26_29", "2023-12-26", "2023-12-29"),
        ],
    }

    batch = sys.argv[1] if len(sys.argv) > 1 else "S1a"
    if batch not in all_spikes:
        print(f"ERROR: batch must be one of {list(all_spikes.keys())}, got {batch!r}", file=sys.stderr)
        return 3

    spikes = all_spikes[batch]
    print(f"=== Running batch {batch}: {len(spikes)} spike(s) ===", flush=True)

    results = []
    for label, sd, ed in spikes:
        results.append(run_one_spike(label, sd, ed))
        time.sleep(90)

    consolidated = SPIKE_DIR / f"spike-summary-{batch}.json"
    with consolidated.open("w", encoding="utf-8") as fh:
        json.dump({"batch": batch, "spikes": results}, fh, indent=2, default=str, ensure_ascii=False)

    print(f"\n{'='*70}\nSPIKE PROTOCOL COMPLETE — summary at {consolidated}\n{'='*70}", flush=True)
    print(json.dumps(results, indent=2, default=str, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    sys.exit(main())
