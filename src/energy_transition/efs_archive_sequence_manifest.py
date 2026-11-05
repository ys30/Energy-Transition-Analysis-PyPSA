"""Create an audit-only ordinal manifest from verified archived EFS snapshot metadata.

Archive sequence ordinals are NOT independently sourced EFS LocalHourID and
naive snapshot labels are NOT UTC. This tool never alters the source NetCDF.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

YEARS = (2030, 2040, 2050)
HOURS = 8760


def build_rows(report):
    records = {int(x["model_year"]): x for x in report["archive_years"]}
    if len(records) != 3 or set(records) != set(YEARS):
        raise ValueError("Expected archived years 2030, 2040 and 2050 exactly")
    rows = []
    summary = []
    for year in YEARS:
        rec = records[year]
        if rec["stored_snapshot_count"] != HOURS:
            raise ValueError(f"{year}: expected exactly 8760 archived snapshots")
        if rec["stored_timestamp_timezone_name"] is not None:
            raise ValueError(f"{year}: this manifest expects the audited naive source index")
        start = datetime.fromisoformat(rec["stored_snapshot_first"])
        end = datetime.fromisoformat(rec["stored_snapshot_last"])
        if start != datetime(year, 1, 1) or end != start + timedelta(hours=HOURS-1):
            raise ValueError(f"{year}: unexpected archived snapshot boundaries")
        if end.year != year:
            raise ValueError(f"{year}: archived snapshots cross model year")
        for ordinal in range(1, HOURS + 1):
            stamp = start + timedelta(hours=ordinal-1)
            rows.append({
                "model_year": year,
                "archive_sequence_ordinal": ordinal,
                "stored_naive_snapshot": stamp.strftime("%Y-%m-%d %H:%M:%S"),
                "stored_month": stamp.month,
                "stored_day": stamp.day,
                "stored_hour": stamp.hour,
                "is_leap_day": int(stamp.month == 2 and stamp.day == 29),
                "verified_source_local_hour_id": "",
                "verified_utc_timestamp": "",
            })
        summary.append({
            "model_year": year,
            "archived_hours": HOURS,
            "archived_leap_day_hours": sum(r["is_leap_day"] for r in rows[-HOURS:]),
            "archived_dec31_hours": sum(
                r["stored_month"] == 12 and r["stored_day"] == 31
                for r in rows[-HOURS:]
            ),
        })
    return rows, {
        "status": "AUDIT_ONLY_NOT_ADMITTED_FOR_SYNCHRONOUS_OPF",
        "hours_total": len(rows),
        "years": summary,
        "source_LocalHourID_identity_verified": False,
        "UTC_alignment_verified": False,
        "weather_generator_join_admitted": False,
        "explanation": "Archive order is not evidence of original EFS LocalHourID, DST treatment, or synchronized UTC chronology.",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audit-json", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a = p.parse_args()
    rows, result = build_rows(json.loads(a.audit_json.read_text()))
    for path in (a.out_csv, a.out_json):
        path.parent.mkdir(parents=True, exist_ok=True)
    with a.out_csv.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    a.out_json.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
