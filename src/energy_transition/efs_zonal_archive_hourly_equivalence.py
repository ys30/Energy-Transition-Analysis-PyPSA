"""Validate exact hourly EFS zonal loads against archived load-only NetCDF.

This audits the project's actual load-attachment path (local_hour_id order),
not a UTC clock conversion. Original source-hour meaning still requires
independent EFS metadata certification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

YEARS = (2030, 2040, 2050)
HOURS = 8760


def compare(networks, zonal):
    required = {"year", "state", "reeds_zone", "local_hour_id", "allocated_mw"}
    if not required.issubset(zonal.columns):
        raise ValueError("Missing zonal source columns")
    if zonal.duplicated(["year", "state", "reeds_zone", "local_hour_id"]).any():
        raise ValueError("Duplicate source zonal hour keys")
    if zonal["allocated_mw"].isna().any() or not np.isfinite(zonal["allocated_mw"].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite source load")
    if (zonal["allocated_mw"] < 0).any():
        raise ValueError("Negative source load")
    outputs = []
    for year in YEARS:
        if year not in networks:
            raise ValueError(f"Missing archived network {year}")
        network = networks[year]
        data = zonal[zonal.year == year]
        if data.empty:
            raise ValueError(f"Missing source zonal year {year}")
        if len(network.snapshots) != HOURS:
            raise ValueError(f"Unexpected archived hours for {year}")
        if not network.loads.index.is_unique:
            raise ValueError("Duplicate archived Load identifiers")
        expected_names = set()
        mismatched = 0
        max_abs_mw = 0.0
        compared = 0
        for (state, zone), group in data.groupby(["state", "reeds_zone"]):
            ids = group["local_hour_id"].to_numpy(dtype=int)
            if len(ids) != HOURS or not np.array_equal(np.sort(ids), np.arange(1, HOURS + 1)):
                raise ValueError(f"Incomplete source hour sequence: {year}/{state}/{zone}")
            load_name = f"EFS_{year}_{zone}_{state}"
            if load_name not in network.loads.index:
                raise ValueError(f"Missing archived zonal Load: {load_name}")
            expected_names.add(load_name)
            target = group.sort_values("local_hour_id")["allocated_mw"].to_numpy(dtype=float)
            if load_name in network.loads_t.p_set.columns:
                actual = network.loads_t.p_set[load_name].to_numpy(dtype=float)
            else:
                actual = np.full(HOURS, float(network.loads.at[load_name, "p_set"]))
            if len(actual) != HOURS or not np.isfinite(actual).all():
                raise ValueError(f"Invalid stored series: {load_name}")
            diffs = np.abs(actual - target)
            mismatch = int(np.count_nonzero(~np.isclose(actual, target, rtol=1e-10, atol=1e-6)))
            mismatched += mismatch
            max_abs_mw = max(max_abs_mw, float(diffs.max()))
            compared += HOURS
        if set(network.loads.index) != expected_names:
            raise ValueError(f"Unexpected archived Load population in {year}")
        if mismatched:
            raise ValueError(f"{year}: {mismatched} hourly MW mismatches (max {max_abs_mw:.9g} MW)")
        outputs.append({
            "year": year,
            "zonal_loads": len(expected_names),
            "hourly_load_values_compared": compared,
            "hourly_mw_mismatches": mismatched,
            "maximum_absolute_mw_error": max_abs_mw,
            "source_to_archive_hour_order": "source local_hour_id 1..8760 mapped directly to archived row 1..8760",
        })
    return {
        "status": "EXACT_ZONAL_TO_ARCHIVE_MW_MATCH",
        "year_results": outputs,
        "original_EFS_source_timezone_and_DST_verified": False,
        "cross_state_synchronous_UTC_verified": False,
        "weather_generator_alignment_admitted": False,
        "actual_Western_OPF_admitted": False,
    }


def main():
    import pypsa
    parser = argparse.ArgumentParser()
    for year in YEARS:
        parser.add_argument(f"--net{year}", required=True, type=Path)
    parser.add_argument("--zonal", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    nets = {year: pypsa.Network(str(getattr(args, f"net{year}"))) for year in YEARS}
    report = compare(nets, pd.read_csv(args.zonal, compression="infer"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
