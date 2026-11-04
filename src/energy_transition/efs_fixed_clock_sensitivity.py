"""Read-only EFS fixed-offset chronology sensitivity using archived seven-state pilot.

The comparison applies the EXACT per-state circular 8760 shift implemented by
pinned PyPSA-USA, but intentionally emits UTC *ordinal* rather than a certified
calendar timestamp. No renewable or generation chronology is presumed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

STATE_SHIFTS={"Arizona":7,"Colorado":7,"Idaho":7,"Montana":7,
              "New Mexico":7,"Utah":7,"Wyoming":7}
YEARS=(2030,2040,2050)
HOURS=8760


def fixed_utc_ordinal(local_hour_id, shift):
    hour=np.asarray(local_hour_id,dtype=np.int64)
    if np.any((hour<1)|(hour>HOURS)):
        raise ValueError("LocalHourID must be within 1..8760")
    if shift not in (7,8):
        raise ValueError("Only the pinned 7/8 hour offsets are supported")
    return (hour+shift-1)%HOURS+1


def audit_fixed_clock(zonal:pd.DataFrame)->dict:
    required={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    if set(zonal.columns)!=required or zonal.empty or zonal.isna().any().any():
        raise ValueError("Unexpected or missing EFS zonal pilot columns")
    if set(zonal.year)!=set(YEARS) or set(zonal.state)!=set(STATE_SHIFTS):
        raise ValueError("Only the verified seven-state 2030/2040/2050 pilot is allowed")
    x=zonal.copy()
    x["allocated_mw"]=pd.to_numeric(x.allocated_mw,errors="raise")
    if not np.isfinite(x.allocated_mw.to_numpy()).all() or (x.allocated_mw<0).any():
        raise ValueError("Invalid MW")
    if x.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Duplicate source local hour")
    x["compat_utc_ordinal"]=np.empty(len(x),dtype=np.int64)
    for state,shift in STATE_SHIFTS.items():
        mask=x.state.eq(state)
        x.loc[mask,"compat_utc_ordinal"]=fixed_utc_ordinal(x.loc[mask,"local_hour_id"],shift)
    expected=np.arange(1,HOURS+1)
    groups=[]
    for (year,state,zone),g in x.groupby(["year","state","reeds_zone"],sort=True):
        if not np.array_equal(np.sort(g.local_hour_id.to_numpy()),expected):
            raise ValueError(f"Missing LocalHourID: {year}/{state}/{zone}")
        if not np.array_equal(np.sort(g.compat_utc_ordinal.to_numpy()),expected):
            raise ValueError(f"Shifted index incomplete: {year}/{state}/{zone}")
        local_sum=float(g.allocated_mw.sum())
        shifted_sum=float(g.groupby("compat_utc_ordinal").allocated_mw.sum().sum())
        if not np.isclose(local_sum,shifted_sum,rtol=0,atol=1e-6):
            raise ValueError("Energy changed under circular shift")
        groups.append({"year":int(year),"state":state,"reeds_zone":str(zone),
                       "fixed_shift_hours":STATE_SHIFTS[state],
                       "local_mwh":local_sum,"shifted_mwh":shifted_sum})
    summary=[]
    for year, g in x.groupby("year",sort=True):
        local=g.groupby("local_hour_id").allocated_mw.sum().reindex(expected)
        shifted=g.groupby("compat_utc_ordinal").allocated_mw.sum().reindex(expected)
        if local.isna().any() or shifted.isna().any():
            raise ValueError("Aggregate hourly coverage incomplete")
        local_max=float(local.max())
        shifted_max=float(shifted.max())
        summary.append({
            "year":int(year),
            "seven_state_local_ordinal_peak_mw":local_max,
            "seven_state_compat_shift_peak_mw":shifted_max,
            "peak_difference_mw":shifted_max-local_max,
            "local_ordinal_peak_hour":int(local.idxmax()),
            "compat_shift_peak_hour":int(shifted.idxmax()),
            "annual_mwh":float(local.sum()),
            "shifted_annual_mwh":float(shifted.sum()),
        })
    return {"source":"archived verified real EFS-LAF seven-state zonal pilot",
            "pinned_upstream_implementation":"338af9912addbaf038c6098fe27e1e6ef099d8aa",
            "algorithm":"(LocalHourID + fixed_state_offset - 1) % 8760 + 1",
            "hours_per_state_zone":HOURS,"state_year_zone_count":len(groups),
            "year_comparisons":summary,
            "per_state_year_zone_conservation":groups,
            "strict_per_zone_hour_permutation":True,
            "no_energy_added_by_clock_transform":True,
            "actual_utc_alignment_verified":False,
            "dst_and_split_timezone_adjusted":False,
            "renewable_generation_snapshot_synchronization_verified":False,
            "full_western_calibrated_opf_solved":False,
            "interpretation":"Only a fixed-offset upstream-compatibility sensitivity; both indices are ordinal, not physically certified simultaneous UTC timestamps."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zonal",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit_fixed_clock(pd.read_csv(a.zonal,compression="infer"))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items()
        if k!="per_state_year_zone_conservation"},indent=2))

if __name__=="__main__":
    main()
