"""Extract candidate full-state EFS demand for SD/TX; not Western allocation.

Uses actual source state/LocalHourID/LoadMW records, not invented shares.
"""
import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path
import pandas as pd

STATES = ("SD", "TX")
YEARS = (2030, 2040, 2050)
HOURS = 8760


def extract(source: Path, out: Path, report: Path):
    totals = defaultdict(float)
    records = 0
    for chunk in pd.read_csv(source, usecols=["Year", "State", "LocalHourID", "LoadMW"], chunksize=250000):
        part = chunk[chunk["Year"].isin(YEARS) & chunk["State"].isin(STATES)]
        records += len(part)
        if part.empty:
            continue
        if part["LoadMW"].isna().any() or (part["LoadMW"] < 0).any() or not part["LoadMW"].map(math.isfinite).all():
            raise ValueError("Invalid EFS load")
        if not part["LocalHourID"].between(1, HOURS).all():
            raise ValueError("Bad local hour ID")
        for key, val in part.groupby(["Year", "State", "LocalHourID"])["LoadMW"].sum().items():
            totals[(int(key[0]), str(key[1]), int(key[2]))] += float(val)
    expected = len(STATES) * len(YEARS) * HOURS
    if len(totals) != expected:
        raise ValueError(f"Incomplete SD/TX EFS input: {len(totals)}/{expected}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["year", "state", "local_hour_id", "load_mw"])
        for key in sorted(totals):
            writer.writerow([*key, format(totals[key], ".10f")])
    result = {
        "record_count": expected,
        "source_sector_subsector_rows": records,
        "states": list(STATES),
        "years": list(YEARS),
        "annual_full_state_twh": {
            str(y): {s: round(sum(totals[y,s,h] for h in range(1,HOURS+1))/1e6, 6) for s in STATES}
            for y in YEARS
        },
        "full_state_source_only": True,
        "western_partial_state_allocation_permitted": False,
        "reeds_laf_empirically_verified": False,
        "utc_time_alignment_verified": False
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--csv",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    extract(a.csv,a.out,a.report)


if __name__ == "__main__":
    main()
