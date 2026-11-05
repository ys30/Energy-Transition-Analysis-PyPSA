"""Compare archived snapshot date labels against pinned nonleap template ordinal keys.

This is a calendar-label diagnostic only, NOT a repair, UTC conversion,
or proof that source EFS LocalHourID equals archived sequence order.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timedelta
from pathlib import Path


def analyze(rows):
    if not rows:
        raise ValueError("Missing archived sequence rows")
    years = {}
    for r in rows:
        year = int(r["model_year"])
        ordinal = int(r["archive_sequence_ordinal"])
        if year not in (2030, 2040, 2050):
            raise ValueError("Unexpected scenario year")
        if not (1 <= ordinal <= 8760):
            raise ValueError("Invalid ordinal")
        year_rows = years.setdefault(year, {})
        if ordinal in year_rows:
            raise ValueError(f"{year}: duplicate archive sequence ordinal {ordinal}")
        year_rows[ordinal] = r
    if set(years) != {2030, 2040, 2050}:
        raise ValueError("Missing model year")
    results = []
    for year in (2030, 2040, 2050):
        data = years[year]
        if len(data) != 8760:
            raise ValueError(f"{year}: invalid ordinal count")
        mismatches = 0
        first_mismatch = None
        for ordinal in range(1, 8761):
            r = data[ordinal]
            actual = datetime.fromisoformat(r["stored_naive_snapshot"])
            expected_source = datetime(year, 1, 1) + timedelta(hours=ordinal-1)
            if actual != expected_source:
                raise ValueError(f"{year}: source archive sequence mismatch")
            template = datetime(2018, 1, 1) + timedelta(hours=ordinal-1)
            candidate = (template.month, template.day, template.hour)
            actual_key = (actual.month, actual.day, actual.hour)
            if candidate != actual_key:
                mismatches += 1
                if first_mismatch is None:
                    first_mismatch = {
                        "archive_sequence_ordinal": ordinal,
                        "stored_naive_snapshot": str(actual),
                        "nonleap_template_month_day_hour": template.strftime("%m-%d %H"),
                    }
        results.append({
            "model_year": year,
            "hours_compared": 8760,
            "hours_with_different_month_day_hour_label": mismatches,
            "first_different_label": first_mismatch,
        })
    return {
        "status": "DIAGNOSTIC_ONLY_NO_TIME_REINTERPRETATION",
        "comparison": "stored-naive-calendar vs 2018 nonleap template by archived ordinal",
        "calendar_comparison": results,
        "source_EFS_LocalHourID_identity_verified": False,
        "utc_alignment_verified": False,
        "physical_dispatch_admitted": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    with args.manifest.open(newline="") as f:
        report = analyze(list(csv.DictReader(f)))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
