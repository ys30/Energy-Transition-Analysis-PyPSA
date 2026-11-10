"""Source-backed near-optimal discharge timing: independent predefined 168-hour windows.

The annual delivered MWh can remain nearly invariant while the allocation of
MWh among source-hour windows changes. This LP bounds selected-window service,
NOT real UTC weeks, pointwise hourly discharge, or reliability.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET, MINIMUM_BUDGET_USD, COST_NUMERICAL_SLACK_USD

SHAPE="ordinal24_wave_A"
POWER=.25
ENERGY=1.
# Windows selected based on source ordinals, before viewing any discharge results.
WINDOWS={"early_1_168":(1,168),"middle_4001_4168":(4001,4168)}

def evaluate(hourly,original,group):
    if group not in (1,7):raise ValueError("Only preregistered source groups 1 and 7")
    src=hourly[(hourly.synthetic_supply_shape=="flat_50pct")&
               (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incorrect original source LocalHourID population")
    if src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(src.planning_year.iloc[0])!=2030:
        raise ValueError("Unexpected source identity")
    load=src.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(load).all() or np.min(load)<0 or load.max()<=0:
        raise ValueError("Invalid original load")
    if len(original)!=9:raise ValueError("Incomplete original archived cases")
    cf=shape_cf(np.arange(1,8761),SHAPE)
    kw={"battery_power_peak_ratio":POWER,"storage_energy_peak_hours":ENERGY}
    baseline,bt=solve_zone(load,cf,4,return_trace=True,**kw)
    old=original[(original.synthetic_supply_shape==SHAPE)&(original.battery_duration_h==4)]
    if len(old)!=1 or not np.isclose(baseline["objective_illustrative_variable_usd"],
                                     float(old.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
        raise ValueError("Archived original annual objective mismatch")
    original_cost=float(baseline["objective_illustrative_variable_usd"])
    budget=max(MINIMUM_BUDGET_USD, RELATIVE_BUDGET*original_cost)
    rows=[]
    for name,(start,stop) in WINDOWS.items():
        mask=np.zeros(8760,dtype=float)
        mask[start-1:stop]=1.
        if int(mask.sum())!=168:raise ValueError("Window length mismatch")
        group_results={"baseline":(baseline,bt)}
        for extremum in ("min","max"):
            group_results[extremum]=solve_zone(load,cf,4,
                return_trace=True,discharge_extremum=extremum,
                discharge_hour_weights=mask,
                original_cost_ceiling_usd=original_cost+budget,**kw)
        min_discharge=float(group_results["min"][1].storage_discharge_to_load_mwh.to_numpy()@mask)
        max_discharge=float(group_results["max"][1].storage_discharge_to_load_mwh.to_numpy()@mask)
        base_discharge=float(bt.storage_discharge_to_load_mwh.to_numpy()@mask)
        if not min_discharge<=base_discharge+.03 or not base_discharge<=max_discharge+.03:
            raise ValueError("Archived original baseline is outside window-discharge envelope")
        for mode,(result,trace) in group_results.items():
            original_scored=float(result["objective_illustrative_variable_usd"])
            if original_scored>original_cost+budget+COST_NUMERICAL_SLACK_USD or original_scored<original_cost-max(.03,RELATIVE_BUDGET*original_cost):
                raise ValueError("Selected-hour LP violates original objective certificate")
            discharge=trace.storage_discharge_to_load_mwh.to_numpy(dtype=float)
            if len(discharge)!=8760 or not np.isfinite(discharge).all():
                raise ValueError("Missing or invalid hourly discharge")
            rows.append({"source_shape_group":group,"state":str(src.state.iloc[0]),
                "reeds_zone":str(src.reeds_zone.iloc[0]),"synthetic_supply_shape":SHAPE,
                "power_peak_ratio":POWER,"energy_peak_hours":ENERGY,
                "window":name,"first_source_hour":start,"last_source_hour":stop,
                "solution":mode,"window_discharge_mwh":float(discharge@mask),
                "annual_discharge_mwh":float(discharge.sum()),
                "reference_optimal_cost_usd":original_cost,
                "original_cost_budget_usd":budget,
                "candidate_original_cost_usd":original_scored,
                "candidate_cost_gap_usd":original_scored-original_cost,
                "max_hourly_balance_residual_mwh":result["max_equality_residual_mwh"],
                "terminal_soc_mwh":result["storage_terminal_soc_mwh"]})
    out=pd.DataFrame(rows)
    if len(out)!=6 or out.duplicated(["window","solution"]).any():
        raise ValueError("Two windows and three solutions required")
    if out.max_hourly_balance_residual_mwh.max()>1e-5 or out.terminal_soc_mwh.abs().max()>1e-5:
        raise ValueError("Original hourly conservation/cyclic terminal gate failed")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--group",type=int,choices=(1,7),required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    result=evaluate(pd.read_csv(a.hourly,compression="infer"),pd.read_csv(a.original),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.out_dir/"paper_s_6_source_window_discharge_lp.csv",index=False,float_format="%.12g")
    meta={"status":"TWO_PREDECLARED_ORDINAL_WINDOW_DISCHARGE_COST_CAP_PASS",
          "source_group":a.group,"windows":WINDOWS,"solutions":6,
          "original_relative_cost_budget":RELATIVE_BUDGET,
          "not_certified_calendar_weeks":True,
          "hourly_discharge_bands_computed":False,
          "real_weather_or_grid_inferred":False}
    (a.out_dir/"paper_s_source_window_discharge_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(result.to_string(index=False))
if __name__=="__main__":main()
