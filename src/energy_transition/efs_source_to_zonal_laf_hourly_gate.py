"""Source-state EFS -> original bus LAF -> archived zonal hourly MW audit.

Numerical reconstruction only: source LocalHourID is not certified UTC and
these are modeled zone weights, not certified load delivery locations.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

STATES = {"AZ":"Arizona","CO":"Colorado","ID":"Idaho",
          "MT":"Montana","NM":"New Mexico","UT":"Utah","WY":"Wyoming"}
YEARS = (2030,2040,2050)


def audit(source: pd.DataFrame, zonal: pd.DataFrame, buses: pd.DataFrame,
          *, years=YEARS, hours=8760, expected_states=None):
    sk = ["year","state","local_hour_id"]
    zk = sk + ["reeds_zone"]
    if not {"year","state","local_hour_id","load_mw"}.issubset(source.columns):
        raise ValueError("Missing EFS source columns")
    if not set(zk + ["allocated_mw"]).issubset(zonal.columns):
        raise ValueError("Missing EFS zonal columns")
    if not {"state","reeds_zone","LAF_state"}.issubset(buses.columns):
        raise ValueError("Missing original network bus weight columns")
    src = source.copy()
    src["state"] = src["state"].replace(STATES)
    z = zonal.copy()
    b = buses.copy()
    if expected_states is None:
        expected_states = set(STATES.values())
    else:
        expected_states = set(expected_states)
    src = src[src.state.isin(expected_states)]
    b = b[b.state.isin(expected_states)]
    if set(src.state) != expected_states or set(z.state) != expected_states:
        raise ValueError("Source or zonal state population mismatch")
    if set(src.year) != set(years) or set(z.year) != set(years):
        raise ValueError("Year population mismatch")
    if src.duplicated(sk).any() or z.duplicated(zk).any():
        raise ValueError("Duplicate source or zonal hour keys")
    for df, column in [(src,"load_mw"),(z,"allocated_mw"),(b,"LAF_state")]:
        x = pd.to_numeric(df[column], errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(x).all() or (x < 0).any():
            raise ValueError(f"Invalid/nonfinite {column}")
    counts = src.groupby(["year","state"]).local_hour_id.agg(["size","nunique","min","max"])
    if len(counts) != len(years)*len(expected_states):
        raise ValueError("Missing state-year")
    if not ((counts["size"]==hours)&(counts["nunique"]==hours)&
            (counts["min"]==1)&(counts["max"]==hours)).all():
        raise ValueError("Incomplete EFS source state-year hours")
    weights = b.groupby(["state","reeds_zone"],as_index=False,dropna=False)["LAF_state"].sum()
    weights = weights[weights.state.isin(expected_states)]
    if weights[["state","reeds_zone"]].isna().any().any():
        raise ValueError("Missing LAF geographic key")
    state_mass = weights.groupby("state").LAF_state.sum()
    if set(state_mass.index) != expected_states or (state_mass <= 0).any() or (state_mass > 1.0001).any():
        raise ValueError("Invalid admitted LAF state mass")
    expected = src.merge(weights, on="state", how="inner", validate="many_to_many")
    expected["expected_mw"] = expected["load_mw"] * expected["LAF_state"]
    expected = expected[zk+["expected_mw"]]
    merged = expected.merge(z, on=zk, how="outer", validate="one_to_one", indicator=True)
    if not (merged["_merge"]=="both").all():
        raise ValueError("Missing or extra source zonal hour keys")
    errors = (merged["expected_mw"]-merged["allocated_mw"]).abs()
    matches = np.isclose(merged["expected_mw"],merged["allocated_mw"],rtol=1e-9,atol=1e-5)
    if not matches.all():
        raise ValueError(f"Zonal hourly allocation mismatch: {int((~matches).sum())} rows; max error={errors.max()}")
    source_annual = src.groupby("year")["load_mw"].sum().to_dict()
    zonal_annual = z.groupby("year")["allocated_mw"].sum().to_dict()
    return {
        "status":"SOURCE_STATE_TO_LAF_ZONE_HOURLY_MATCH",
        "years":list(years),"states":sorted(expected_states),
        "state_year_hour_rows_compared":int(len(src)),
        "zonal_hour_rows_compared":int(len(merged)),
        "mismatched_zonal_hour_values":0,
        "maximum_absolute_hourly_zonal_error_mw":float(errors.max()),
        "state_laf_mass":{k:float(v) for k,v in state_mass.items()},
        "source_annual_mwh":{str(k):float(v) for k,v in source_annual.items()},
        "zonal_annual_mwh":{str(k):float(v) for k,v in zonal_annual.items()},
        "independent_source_hour_timezone_provenance_verified":False,
        "actual_electrical_load_location_certified":False,
        "joint_utc_dispatch_admitted":False,
        "note":"Uses archived original state-hour EFS aggregate, archived zone CSV and original network bus LAF; arithmetic only."
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    for name in ("source","zonal","network","out"):
        p.add_argument("--"+name,required=True,type=Path)
    args=p.parse_args()
    n=pypsa.Network(str(args.network))
    report=audit(pd.read_csv(args.source,compression="infer"),
                 pd.read_csv(args.zonal,compression="infer"),
                 n.buses.reset_index(drop=True))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
