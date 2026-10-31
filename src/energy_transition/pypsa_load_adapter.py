"""Validate audited zonal demand against explicit network bus mapping.

This is a pre-solve input adapter, not an inferred WECC topology or a solved
PyPSA model. All zones must have a uniquely declared existing network bus.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def build_load_matrix(zonal_csv, zone_bus_csv):
    zonal = pd.read_csv(zonal_csv)
    mapping = pd.read_csv(zone_bus_csv)
    if not {"timestamp_utc", "zone", "load_mw"}.issubset(zonal.columns):
        raise ValueError("zonal input requires timestamp_utc,zone,load_mw")
    if not {"zone", "bus"}.issubset(mapping.columns):
        raise ValueError("mapping requires zone,bus")
    if zonal.empty or mapping.empty or zonal[["timestamp_utc", "zone", "load_mw"]].isna().any().any():
        raise ValueError("missing zonal load")
    if mapping[["zone", "bus"]].isna().any().any() or mapping["zone"].duplicated().any():
        raise ValueError("missing or duplicate zone-to-bus mapping")
    if set(zonal["zone"]) != set(mapping["zone"]):
        raise ValueError("zone coverage mismatch")
    if mapping["bus"].duplicated().any():
        raise ValueError("multiple zones map to the same bus; aggregation requires explicit policy")
    stamp = zonal["timestamp_utc"].astype(str)
    if not stamp.str.contains(r"(?:Z|[+]00:00)$", case=False, regex=True).all():
        raise ValueError("explicit UTC timestamps required")
    zonal["timestamp_utc"] = pd.to_datetime(stamp, utc=True, errors="raise")
    if zonal.duplicated(["timestamp_utc", "zone"]).any():
        raise ValueError("duplicate zone-hour")
    zonal["load_mw"] = pd.to_numeric(zonal["load_mw"], errors="raise")
    if not np.isfinite(zonal["load_mw"].to_numpy()).all() or (zonal["load_mw"] < 0).any():
        raise ValueError("invalid load")
    result = zonal.pivot(index="timestamp_utc", columns="zone", values="load_mw").sort_index()
    if result.isna().any().any():
        raise ValueError("missing zone-hour")
    if result.index.has_duplicates:
        raise ValueError("duplicate hours")
    result.columns = [mapping.set_index("zone").loc[z, "bus"] for z in result.columns]
    result.columns.name = "bus"
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--zonal", required=True)
    parser.add_argument("--zone-bus", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    matrix = build_load_matrix(args.zonal, args.zone_bus)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(out, index_label="timestamp_utc")
    print(f"Validated {len(matrix)} hours across {len(matrix.columns)} mapped buses")


if __name__ == "__main__":
    main()
