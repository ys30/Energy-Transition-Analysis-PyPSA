"""Verify derived EFS core-Western hourly loads and summarize annual metrics.

LocalHourID is *not* interpreted as UTC. For 8760 equal-duration local
hour slots, summing MW * 1 hour produces MWh; no spatial weights are used.
"""
import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

from energy_transition.nlr_efs_western_hourly import CORE_WEST, HOURS, YEARS


def summarize(path: Path) -> dict:
    totals = defaultdict(float)
    peaks = defaultdict(float)
    counts = defaultdict(int)
    seen = set()
    with gzip.open(path, "rt", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"year", "state", "local_hour_id", "load_mw"}
        if set(reader.fieldnames or ()) != required:
            raise ValueError("Unexpected EFS aggregate CSV fields")
        for row in reader:
            y, s, h = int(row["year"]), row["state"], int(row["local_hour_id"])
            mw = float(row["load_mw"])
            key = y, s, h
            if y not in YEARS or s not in CORE_WEST or not (1 <= h <= HOURS):
                raise ValueError(f"Unexpected year/state/hour: {key}")
            if key in seen:
                raise ValueError(f"Duplicate state-year-hour: {key}")
            if not math.isfinite(mw) or mw < 0:
                raise ValueError(f"Invalid load MW at {key}")
            seen.add(key)
            totals[y, s] += mw
            peaks[y, s] = max(peaks[y, s], mw)
            counts[y, s] += 1
    for y in YEARS:
        for s in CORE_WEST:
            if counts[y, s] != HOURS:
                raise ValueError(f"Incomplete {y} {s}: {counts[y,s]} hours")
    by_year = []
    for y in YEARS:
        annual_mwh = sum(totals[y, s] for s in CORE_WEST)
        by_year.append({
            "year": y,
            "core_11_state_annual_mwh": round(annual_mwh, 3),
            "core_11_state_mean_mw": round(annual_mwh / HOURS, 3),
            "state_annual_mwh": {s: round(totals[y,s], 3) for s in CORE_WEST},
            "state_peak_mw": {s: round(peaks[y,s], 3) for s in CORE_WEST},
        })
    return {
        "source": path.name,
        "years": list(YEARS),
        "states": list(CORE_WEST),
        "rows_verified": len(seen),
        "annual_energy_method": "sum of 8760 hourly load_mw values, each multiplied by 1 hour",
        "by_year": by_year,
        "utc_hourly_alignment_verified": False,
        "simultaneous_regional_peak_calculated": False,
        "reeds_zone_distribution_verified": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = summarize(a.csv)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
