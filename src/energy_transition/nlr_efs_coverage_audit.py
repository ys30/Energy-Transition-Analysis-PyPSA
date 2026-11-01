"""Chunked empirical coverage audit of the official NLR EFS Reference/Moderate CSV."""
import argparse
import json
from pathlib import Path

import pandas as pd

FIELDS = ["Electrification", "TechnologyAdvancement", "Year", "LocalHourID", "State", "Sector", "Subsector", "LoadMW"]
TARGET_YEARS = {2030, 2040, 2050}


def audit(path: Path, chunksize: int = 200_000) -> dict:
    years = {}
    states = {}
    sector_names = set()
    hours = {}
    total = 0
    bad_load = 0
    negative = 0
    wrong_scenario = 0
    for chunk in pd.read_csv(path, usecols=FIELDS, chunksize=chunksize,
                             dtype={"State": str, "Sector": str, "Subsector": str}):
        total += len(chunk)
        yr = pd.to_numeric(chunk["Year"], errors="coerce")
        h = pd.to_numeric(chunk["LocalHourID"], errors="coerce")
        mw = pd.to_numeric(chunk["LoadMW"], errors="coerce")
        bad_load += int(mw.isna().sum())
        negative += int((mw < 0).sum())
        wrong_scenario += int(((chunk["Electrification"] != "Reference") |
                               (chunk["TechnologyAdvancement"] != "Moderate")).sum())
        for y, n in yr.value_counts(dropna=False).items():
            key = str(int(y)) if pd.notna(y) else "missing"
            years[key] = years.get(key, 0) + int(n)
        for state, n in chunk["State"].value_counts(dropna=False).items():
            key = str(state)
            states[key] = states.get(key, 0) + int(n)
        sector_names.update(chunk["Sector"].dropna().unique().tolist())
        for y in TARGET_YEARS:
            selected = h[yr == y].dropna()
            if not selected.empty:
                item = hours.setdefault(str(y), {"min_hour": None, "max_hour": None})
                lo, hi = int(selected.min()), int(selected.max())
                item["min_hour"] = lo if item["min_hour"] is None else min(item["min_hour"], lo)
                item["max_hour"] = hi if item["max_hour"] is None else max(item["max_hour"], hi)
    result = {
        "source_filename": path.name,
        "rows": total,
        "years_row_counts": dict(sorted(years.items())),
        "state_row_counts": dict(sorted(states.items())),
        "sector_values": sorted(sector_names),
        "target_year_hour_extrema": hours,
        "bad_load_mw_rows": bad_load,
        "negative_load_mw_rows": negative,
        "scenario_mismatch_rows": wrong_scenario,
        "years_2030_2040_2050_present": all(str(y) in years for y in TARGET_YEARS),
        "note": "Observed row coverage only; hour completeness, geospatial alignment and dispatch suitability remain separate checks.",
    }
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    result = audit(args.csv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
