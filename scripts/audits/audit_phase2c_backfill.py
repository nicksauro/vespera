"""
Phase 2C backfill audit — empirical verification of 50 parquets (2023-01-02..2023-12-29 WDOFUT).
Dara (@data-engineer) — read-only audit. Reports facts; council decides re-run.
"""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import date, datetime, time
from pathlib import Path

import pyarrow.parquet as pq
import pandas as pd

ROOT = Path(r"D:\Algotrader\dll-backfill")
MANIFEST_CSV = ROOT / "manifest.csv"

EXPECTED_COLUMNS = [
    "timestamp", "ts_raw", "ticker", "price", "qty",
    "aggressor", "buy_agent", "sell_agent", "vol_brl", "trade_number",
]

# B3 holidays 2023 (canonical list from spec)
B3_HOLIDAYS_2023 = {
    date(2023, 1, 1),    # New Year
    date(2023, 2, 20),   # Carnaval
    date(2023, 2, 21),   # Carnaval
    # Feb 22 is Ash Wed — half-session, NOT a holiday
    date(2023, 4, 7),    # Good Friday
    date(2023, 4, 21),   # Tiradentes
    date(2023, 5, 1),    # Labour
    date(2023, 6, 8),    # Corpus Christi
    date(2023, 9, 7),    # Independence
    date(2023, 10, 12),  # Nossa Senhora
    date(2023, 11, 2),   # Finados
    date(2023, 11, 15),  # Republica
    date(2023, 12, 25),  # Christmas
}
HALF_SESSIONS_2023 = {date(2023, 2, 22)}  # Ash Wed half-session


def read_manifest():
    rows = []
    with open(MANIFEST_CSV, "r", encoding="utf-8") as fh:
        # skip the comment line, then DictReader
        first = fh.readline()
        if not first.startswith("#"):
            fh.seek(0)
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def sha256_of_file(path, bufsize=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(bufsize)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def resolve_parquet_path(rel):
    # manifest writes "Algotrader\dll-backfill\<chunk>\<file>.parquet" — drive letter is D:
    rel = rel.replace("\\", "/")
    # strip leading drive-less prefix; we know root is D:\
    # Heuristic: the chunk dir is <chunk_id> under ROOT
    parts = rel.split("/")
    # find "dll-backfill" pivot
    if "dll-backfill" in parts:
        i = parts.index("dll-backfill")
        sub = parts[i + 1:]
        return ROOT.joinpath(*sub)
    return Path("D:/" + rel)


def audit():
    report = {
        "manifest_chunks": 0,
        "manifest_status_ok": 0,
        "manifest_attempt_max": 0,
        "manifest_trades_sum": 0,
        "manifest_qfd_sum": 0,
        "outcomes": defaultdict(int),
        "per_chunk": [],
        "monthly": defaultdict(int),
        "holiday_violations": [],
        "intraday_warnings": [],
        "cross_chunk_gaps": [],
        "sha256_status": {"empty_in_manifest": 0, "computed": 0},
        "errors": [],
    }

    rows = read_manifest()
    report["manifest_chunks"] = len(rows)

    # iterate chunks in manifest order (chronological)
    parquet_total_rows = 0
    last_chunk_max_ts = None
    last_chunk_id = None

    for r in rows:
        chunk_id = r["chunk_id"]
        status = r["status"]
        attempt = int(r.get("attempt", "0") or "0")
        trades_count = int(r.get("trades_count", "0") or "0")
        qfd = int(r.get("queue_full_drops", "0") or "0")
        outcome = r.get("outcome", "")
        sha_manifest = r.get("sha256_parquet", "") or ""
        rel = r.get("parquet_relative_path", "")
        start_date = datetime.strptime(r["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(r["end_date"], "%Y-%m-%d").date()

        if status == "ok":
            report["manifest_status_ok"] += 1
        report["manifest_attempt_max"] = max(report["manifest_attempt_max"], attempt)
        report["manifest_trades_sum"] += trades_count
        report["manifest_qfd_sum"] += qfd
        report["outcomes"][outcome] += 1

        if not sha_manifest.strip():
            report["sha256_status"]["empty_in_manifest"] += 1

        path = resolve_parquet_path(rel)
        chunk_entry = {
            "chunk_id": chunk_id,
            "path": str(path),
            "exists": path.exists(),
            "manifest_trades": trades_count,
            "parquet_rows": None,
            "min_ts": None,
            "max_ts": None,
            "in_window": None,
            "missing_cols": [],
            "extra_cols": [],
            "dtype_issues": [],
            "trade_number_monotonic_intraday": True,
            "outcome": outcome,
            "attempt": attempt,
            "sha256_computed": None,
        }

        if not path.exists():
            chunk_entry["error"] = "FILE_NOT_FOUND"
            report["per_chunk"].append(chunk_entry)
            report["errors"].append(f"{chunk_id}: parquet not found at {path}")
            continue

        try:
            tbl = pq.read_table(str(path))
            df = tbl.to_pandas()
        except Exception as e:
            chunk_entry["error"] = f"READ_FAIL: {e}"
            report["per_chunk"].append(chunk_entry)
            report["errors"].append(f"{chunk_id}: {e}")
            continue

        chunk_entry["parquet_rows"] = len(df)
        parquet_total_rows += len(df)

        # column check
        cols = list(df.columns)
        missing = [c for c in EXPECTED_COLUMNS if c not in cols]
        extra = [c for c in cols if c not in EXPECTED_COLUMNS]
        chunk_entry["missing_cols"] = missing
        chunk_entry["extra_cols"] = extra

        # dtype check (relaxed: int can be int32/int64; price float)
        dtype_expect = {
            "timestamp": "datetime64[ns",  # prefix allows tz/units variants
            "ts_raw": "object",
            "ticker": "object",
            "price": "float64",
            "qty": "int",
            "aggressor": "object",
            "buy_agent": "int",
            "sell_agent": "int",
            "vol_brl": "float64",
            "trade_number": "int",
        }
        for col, exp in dtype_expect.items():
            if col not in df.columns:
                continue
            dt = str(df[col].dtype)
            if not dt.startswith(exp):
                chunk_entry["dtype_issues"].append(f"{col}={dt} expected~{exp}")

        if len(df) == 0:
            chunk_entry["error"] = "ZERO_ROWS"
            report["per_chunk"].append(chunk_entry)
            report["errors"].append(f"{chunk_id}: zero rows")
            continue

        # window coverage
        ts_col = df["timestamp"]
        # ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(ts_col):
            try:
                ts_col = pd.to_datetime(ts_col)
            except Exception:
                pass
        min_ts = ts_col.min()
        max_ts = ts_col.max()
        chunk_entry["min_ts"] = str(min_ts)
        chunk_entry["max_ts"] = str(max_ts)
        in_window = (min_ts.date() >= start_date) and (max_ts.date() <= end_date)
        chunk_entry["in_window"] = bool(in_window)
        if not in_window:
            report["errors"].append(
                f"{chunk_id}: out-of-window min={min_ts} max={max_ts} window={start_date}..{end_date}"
            )

        # monthly aggregate
        month_key = ts_col.dt.strftime("%Y-%m")
        for k, v in month_key.value_counts().to_dict().items():
            report["monthly"][k] += int(v)

        # holiday sanity
        unique_dates = pd.unique(ts_col.dt.date)
        for d in unique_dates:
            if d in B3_HOLIDAYS_2023:
                cnt = int((ts_col.dt.date == d).sum())
                report["holiday_violations"].append({
                    "chunk_id": chunk_id, "holiday": str(d), "trades": cnt,
                })

        # intraday gap check (only weekdays, not holidays, not half-session)
        for d in unique_dates:
            if d.weekday() >= 5:
                continue
            if d in B3_HOLIDAYS_2023:
                continue
            day_ts = ts_col[ts_col.dt.date == d].sort_values()
            # only the regular session window 09:30-17:30
            day_reg = day_ts[(day_ts.dt.time >= time(9, 30)) & (day_ts.dt.time <= time(17, 30))]
            if len(day_reg) < 2:
                continue
            diffs = day_reg.diff().dt.total_seconds().dropna()
            max_gap = diffs.max() if len(diffs) else 0
            if max_gap > 60:
                report["intraday_warnings"].append({
                    "chunk_id": chunk_id, "date": str(d),
                    "max_gap_s": float(max_gap),
                    "first_ts": str(day_reg.iloc[0]),
                    "last_ts": str(day_reg.iloc[-1]),
                })

        # trade_number monotonic INTRA-DAY (Q-AMB acceptable: resets across days)
        if "trade_number" in df.columns:
            for d in unique_dates:
                mask = ts_col.dt.date == d
                tn = df.loc[mask, "trade_number"].to_numpy()
                if len(tn) > 1:
                    # allow non-strict monotonic (>=) since duplicates may occur but should never go down
                    diffs = tn[1:] - tn[:-1]
                    if (diffs < 0).any():
                        chunk_entry["trade_number_monotonic_intraday"] = False
                        # only record once per chunk
                        break

        # cross-chunk continuity (vs prior chunk's last day)
        if last_chunk_max_ts is not None:
            gap_days = (min_ts.date() - last_chunk_max_ts.date()).days
            # window boundaries: prior end_date and this start_date should differ by 0..3 (weekend)
            # If parquet's first day is > 4 business days after prior parquet's last day -> potential missing day
            if gap_days > 4:
                report["cross_chunk_gaps"].append({
                    "from_chunk": last_chunk_id, "to_chunk": chunk_id,
                    "from_max_ts": str(last_chunk_max_ts),
                    "to_min_ts": str(min_ts),
                    "gap_days": gap_days,
                })

        last_chunk_max_ts = max_ts
        last_chunk_id = chunk_id

        report["per_chunk"].append(chunk_entry)

    report["parquet_total_rows"] = parquet_total_rows
    report["delta_rows_vs_manifest"] = parquet_total_rows - report["manifest_trades_sum"]

    return report


if __name__ == "__main__":
    rpt = audit()
    out_path = ROOT / "audit-phase2c-2026-05-02.json"
    # convert defaultdicts to plain
    rpt["outcomes"] = dict(rpt["outcomes"])
    rpt["monthly"] = dict(sorted(rpt["monthly"].items()))
    out_path.write_text(json.dumps(rpt, indent=2, default=str), encoding="utf-8")
    print(f"WROTE: {out_path}")
    print(f"chunks={rpt['manifest_chunks']} ok={rpt['manifest_status_ok']}")
    print(f"manifest_trades_sum={rpt['manifest_trades_sum']:,}")
    print(f"parquet_total_rows={rpt['parquet_total_rows']:,}")
    print(f"delta={rpt['delta_rows_vs_manifest']}")
    print(f"qfd_sum={rpt['manifest_qfd_sum']}")
    print(f"errors={len(rpt['errors'])}")
    print(f"holiday_violations={len(rpt['holiday_violations'])}")
    print(f"intraday_warnings={len(rpt['intraday_warnings'])}")
    print(f"cross_chunk_gaps>4d={len(rpt['cross_chunk_gaps'])}")
    print(f"outcomes={rpt['outcomes']}")
    print("monthly:")
    for k, v in rpt["monthly"].items():
        print(f"  {k}: {v:,}")
