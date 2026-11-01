"""Stream official EFS into a reproducible *core western states* hourly load artifact.

The core 11-state scope is explicitly not asserted to equal PyPSA-USA's
interconnection or ReEDS zonal footprint. Uses source LocalHourID as an
ordinal; does not invent UTC time stamps or resolve daylight saving shifts.
"""
import argparse
import csv
import gzip
import json
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd

CORE_WEST = ("AZ", "CA", "CO", "ID", "MT", "NM", "NV", "OR", "UT", "WA", "WY")
YEARS = (2030, 2040, 2050)
HOURS = 8760


def aggregate(path: Path, out: Path, report: Path, chunksize: int = 250_000):
    totals = defaultdict(float)
    observed = set()
    source_rows = 0
    for chunk in pd.read_csv(path, usecols=["Year", "LocalHourID", "State", "LoadMW"],
                             chunksize=chunksize):
        filtered = chunk.loc[chunk["Year"].isin(YEARS) & chunk["State"].isin(CORE_WEST)]
        if filtered.empty:
            continue
        source_rows += len(filtered)
        if filtered["LoadMW"].isna().any() or not filtered["LoadMW"].map(math.isfinite).all():
            raise ValueError("Non-finite MW in selected source records")
        if (filtered["LoadMW"] < 0).any():
            raise ValueError("Negative MW in selected source records")
        if not filtered["LocalHourID"].between(1, HOURS).all():
            raise ValueError("Invalid EFS LocalHourID")
        grouped = filtered.groupby(["Year", "State", "LocalHourID"], sort=False)["LoadMW"].sum()
        for (year, state, hour), mw in grouped.items():
            key = (int(year), str(state), int(hour))
            totals[key] += float(mw)
            observed.add(key)
    expected_count = len(CORE_WEST) * len(YEARS) * HOURS
    if len(observed) != expected_count:
        missing = [(y,s,h) for y in YEARS for s in CORE_WEST for h in range(1,HOURS+1) if (y,s,h) not in observed]
        raise ValueError(f"Missing core Western state-year-hour combinations: {len(missing)}; example={missing[:10]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(out, "wt", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(("year", "state", "local_hour_id", "load_mw"))
        for key in sorted(totals):
            writer.writerow((*key, format(totals[key], ".10f")))
    results = {
        "input_filename": path.name,
        "scope": "core 11 Western states pilot; not full ReEDS interconnect",
        "years": list(YEARS),
        "states": list(CORE_WEST),
        "expected_state_year_hours": expected_count,
        "actual_state_year_hours": len(totals),
        "source_sector_subsector_rows_selected": source_rows,
        "nonnegative_finite_load_mw": True,
        "each_state_year_has_8760_local_hour_ids": True,
        "timezone_alignment_verified": False,
        "reeds_laf_weights_verified": False,
        "full_western_pypsa_network_admitted": False,
    }
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    aggregate(a.csv, a.out, a.report)


if __name__ == "__main__":
    main()
