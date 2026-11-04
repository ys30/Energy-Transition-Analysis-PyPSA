"""Independent integrity audit for archived EFS local-hour zonal pilot data.

No assumption that local_hour_id is UTC or that its length is a Gregorian
year. This is a source-to-output consistency audit, not empirical admission.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

STATE_NAMES={"AZ":"Arizona","CO":"Colorado","ID":"Idaho","MT":"Montana",
             "NM":"New Mexico","UT":"Utah","WY":"Wyoming"}
YEARS={2030,2040,2050}
NEEDED_SOURCE={"year","state","local_hour_id","load_mw"}
NEEDED_ZONAL={"year","state","local_hour_id","reeds_zone","allocated_mw"}


def audit_archived_pilot(source: pd.DataFrame, zonal: pd.DataFrame, *, tolerance_mw=1e-5):
    if set(source.columns)!=NEEDED_SOURCE or set(zonal.columns)!=NEEDED_ZONAL:
        raise ValueError("Unexpected input columns")
    if source.empty or zonal.empty or source.isna().any().any() or zonal.isna().any().any():
        raise ValueError("Empty/null archived EFS pilot input")
    src=source.copy()
    out=zonal.copy()
    src["state"]=src["state"].replace(STATE_NAMES)
    if set(src.year)!=YEARS or set(out.year)!=YEARS:
        raise ValueError("Must contain exactly EFS planning years 2030, 2040, 2050")
    admitted=set(STATE_NAMES.values())
    source_states=set(src.state)
    excluded=sorted(source_states-admitted)
    if not admitted.issubset(source_states) or set(out.state)!=admitted:
        raise ValueError("Seven admitted states missing from source or zonal archive")
    src=src[src.state.isin(admitted)].copy()
    for frame,col in [(src,"load_mw"),(out,"allocated_mw")]:
        values=pd.to_numeric(frame[col],errors="raise")
        if not np.isfinite(values.to_numpy(dtype=float)).all() or (values<0).any():
            raise ValueError("Invalid EFS hourly MW")
        frame[col]=values
    keys=["year","state","local_hour_id"]
    if src.duplicated(keys).any() or out.duplicated(keys+["reeds_zone"]).any():
        raise ValueError("Duplicate state-hour or state-hour-zone")
    source_keys=src.set_index(keys)["load_mw"].sort_index()
    allocated=out.groupby(keys)["allocated_mw"].sum().sort_index()
    if not source_keys.index.equals(allocated.index):
        raise ValueError("Source/allocated local-hour keys differ")
    hourly=src.groupby(["year","state"]).local_hour_id.nunique()
    if hourly.nunique()!=1:
        raise ValueError("Inconsistent LocalHourID counts across state/year groups")
    # Ordinal completeness is strictly testable even while timestamp semantics
    # remain unknown. No 2030/2040/2050 calendar, timezone or DST is inferred.
    expected_hours=np.arange(1,8761,dtype=np.int64)
    for (year,state),group in src.groupby(["year","state"],sort=True):
        hours=pd.to_numeric(group["local_hour_id"],errors="raise").to_numpy()
        if not np.array_equal(np.sort(hours),expected_hours):
            raise ValueError(f"Missing or invalid 1..8760 ordinal coverage for {year}/{state}")
    for (year,state,zone),group in out.groupby(["year","state","reeds_zone"],sort=True):
        hours=pd.to_numeric(group["local_hour_id"],errors="raise").to_numpy()
        if not np.array_equal(np.sort(hours),expected_hours):
            raise ValueError(f"Missing or invalid 1..8760 zone ordinal coverage for {year}/{state}/{zone}")
    zone_inventory=out.groupby(["year","state"])["reeds_zone"].apply(lambda x:tuple(sorted(x.unique())))
    for state,g in zone_inventory.groupby(level="state"):
        if len(set(g.tolist()))!=1:
            raise ValueError(f"Zone inventory changes between planning years for {state}")
    zone_counts=out.groupby(keys)["reeds_zone"].nunique()
    expected_zone_count=out.groupby(["year","state"])["reeds_zone"].nunique()
    expected=zone_counts.index.droplevel("local_hour_id").map(expected_zone_count)
    if not np.array_equal(zone_counts.to_numpy(),np.asarray(expected)):
        raise ValueError("Incomplete zone-by-hour coverage")
    report=[]
    for (year,state),source_group in src.groupby(["year","state"],sort=True):
        ss=source_group.set_index("local_hour_id")["load_mw"].sort_index()
        zz=allocated.loc[(year,state)].sort_index()
        if not ss.index.equals(zz.index):
            raise ValueError("State-level local-hour mismatch")
        nonzero=ss>0
        if not nonzero.any():
            raise ValueError(f"Zero-only EFS profile {year}/{state}")
        ratios=(zz.loc[nonzero]/ss.loc[nonzero]).to_numpy(dtype=float)
        factor=float(np.median(ratios))
        # A constant factor is not evidence that the original LAF is correct.
        deviation=np.max(np.abs(zz.to_numpy()-factor*ss.to_numpy()))
        if deviation>tolerance_mw+1e-9*np.max(np.abs(zz.to_numpy())):
            raise ValueError(f"Hourly demand allocation inconsistent in {year}/{state}")
        report.append({"year":int(year),"state":state,
                       "source_local_hour_count":int(len(ss)),
                       "zone_count":int(expected_zone_count.loc[(year,state)]),
                       "source_energy_local_hour_mwh":float(ss.sum()),
                       "allocated_energy_local_hour_mwh":float(zz.sum()),
                       "inferred_archived_allocation_factor":factor,
                       "max_hourly_factor_residual_mw":float(deviation)})
    return {
        "pilot_only":True,"source_state_hour_rows":int(len(src)),
        "zonal_state_hour_zone_rows":int(len(out)),
        "planning_years":sorted(YEARS),
        "scope_state_count":len(STATE_NAMES),
        "source_states_excluded_from_pilot":excluded,
        "source_state_count_before_admission_filter":len(source_states),
        "state_year_results":report,
        "duplicate_keys_rejected":True,
        "zone_hour_coverage_verified":True,
        "constant_factor_hourly_arithmetic_verified":True,
        "strict_1_to_8760_ordinals_verified_per_state_year_zone":True,
        "hour_end_or_hour_begin_convention_verified":False,
        "weather_year_calendar_verified":False,
        "dst_handling_verified":False,
        "utc_alignment_verified":False,
        "source_laf_provenance_verified":False,
        "full_western_demand_coverage_verified":False,
        "actual_western_opf_solved":False,
        "note":"LocalHourID does not establish UTC/DST/calendar. Inferred factors are arithmetic diagnostics, not newly sourced allocation shares."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=audit_archived_pilot(pd.read_csv(a.source,compression="infer"),
                                pd.read_csv(a.zonal,compression="infer"))
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="state_year_results"},indent=2))
    print("State-year rows:",len(result["state_year_results"]))


if __name__=="__main__":
    main()
