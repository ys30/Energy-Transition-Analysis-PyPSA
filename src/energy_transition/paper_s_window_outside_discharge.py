"""Audit where cost-capped window discharge reallocates across source hours.

For each archived schedule, annual discharge equals selected-window discharge
plus discharge outside the 168-hour window. This is an accounting identity and
does not identify the exact offsetting hours or physical calendar times.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

GROUPS={1:("Arizona","p28"),7:("Wyoming","p24")}
WINDOWS={"early_1_168":(1,168),"middle_4001_4168":(4001,4168)}

def audit(data):
    required={"source_shape_group","state","reeds_zone","window",
      "first_source_hour","last_source_hour","solution","window_discharge_mwh",
      "annual_discharge_mwh","reference_optimal_cost_usd",
      "original_cost_budget_usd","candidate_original_cost_usd",
      "candidate_cost_gap_usd","max_hourly_balance_residual_mwh",
      "terminal_soc_mwh"}
    if not required.issubset(data):raise ValueError("Missing archived schedule certificate columns")
    if len(data)!=12 or data.duplicated(["source_shape_group","window","solution"]).any():
        raise ValueError("Require 12 original source-window candidate schedules")
    if set(data.source_shape_group)!=set(GROUPS) or set(data.window)!=set(WINDOWS):
        raise ValueError("Unexpected source group or precommitted window")
    values=data[["window_discharge_mwh","annual_discharge_mwh",
      "reference_optimal_cost_usd","original_cost_budget_usd",
      "candidate_original_cost_usd","candidate_cost_gap_usd",
      "max_hourly_balance_residual_mwh","terminal_soc_mwh"]].to_numpy(dtype=float)
    if not np.isfinite(values).all():raise ValueError("Nonfinite original source results")
    if (data.window_discharge_mwh<-.02).any() or (data.window_discharge_mwh>data.annual_discharge_mwh+.03).any():
        raise ValueError("Invalid discharge energy budget")
    if (data.max_hourly_balance_residual_mwh>1e-5).any() or (data.terminal_soc_mwh.abs()>1e-5).any():
        raise ValueError("Original source energy or cyclic feasibility failure")
    if not np.allclose(data.candidate_original_cost_usd-data.reference_optimal_cost_usd,
                       data.candidate_cost_gap_usd,rtol=0,atol=.011):
        raise ValueError("Original cost gap identity failure")
    if (data.candidate_cost_gap_usd>data.original_cost_budget_usd+.02).any():
        raise ValueError("Original cost allowance exceeded")
    records=[]
    for (group,window),rows in data.groupby(["source_shape_group","window"]):
        if len(rows)!=3 or set(rows.solution)!={"baseline","min","max"}:
            raise ValueError("Incomplete baseline/min/max source schedules")
        a=rows.set_index("solution")
        state,zone=GROUPS[group]
        if set(a.state)!={state} or set(a.reeds_zone)!={zone}:
            raise ValueError("Original EFS source representative mismatch")
        start,stop=WINDOWS[window]
        if not (a.first_source_hour.eq(start)&a.last_source_hour.eq(stop)).all():
            raise ValueError("Precommitted ordinal window modified")
        if a.reference_optimal_cost_usd.max()-a.reference_optimal_cost_usd.min()>.01:
            raise ValueError("Original baseline objective inconsistent")
        base=a.loc["baseline"]
        for mode in ("min","max"):
            x=a.loc[mode]
            inside=float(x.window_discharge_mwh-base.window_discharge_mwh)
            annual=float(x.annual_discharge_mwh-base.annual_discharge_mwh)
            outside=annual-inside
            if abs(inside+outside-annual)>1e-7:
                raise ValueError("Window/outside annual discharge reconciliation failed")
            records.append(dict(source_shape_group=int(group),state=state,reeds_zone=zone,
                  source_window=window,solution=mode,
                  baseline_window_discharge_mwh=float(base.window_discharge_mwh),
                  candidate_window_discharge_mwh=float(x.window_discharge_mwh),
                  delta_window_discharge_mwh=inside,
                  delta_discharge_outside_window_mwh=outside,
                  delta_annual_discharge_mwh=annual,
                  window_and_outside_residual_mwh=inside+outside-annual,
                  original_cost_gap_usd=float(x.candidate_cost_gap_usd),
                  allowed_cost_increase_usd=float(x.original_cost_budget_usd)))
    out=pd.DataFrame(records)
    if len(out)!=8 or out.duplicated(["source_shape_group","source_window","solution"]).any():
        raise ValueError("Incomplete eight candidate reallocations")
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--arizona",required=True,type=Path)
    ap.add_argument("--wyoming",required=True,type=Path)
    ap.add_argument("--out-dir",required=True,type=Path)
    a=ap.parse_args()
    original=pd.concat([pd.read_csv(a.arizona),pd.read_csv(a.wyoming)],ignore_index=True)
    result=audit(original)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.out_dir/"paper_s_eight_inside_outside_window_discharge_changes.csv",index=False,float_format="%.12g")
    meta={"status":"PAPER_S_ARCHIVED_SOURCE_WINDOW_OUTSIDE_BALANCE_PASS",
       "source_schedules":12,"compared_candidate_schedules":8,
       "windows":WINDOWS,"source_hour_count":8760,
       "window_outside_split_is_accounting_not_time_localization":True,
       "pointwise_hourly_redistribution_identified":False,
       "exact_optimal_face_certified":False}
    (a.out_dir/"paper_s_window_outside_discharge_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(result.to_string(index=False))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
