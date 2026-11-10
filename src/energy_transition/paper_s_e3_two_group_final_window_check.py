"""E3 finite closure: Colorado and Idaho distinct source demand groups.

Exactly the five previously frozen, disjoint 168 source-ordinal windows.
No search/extension after inspecting outputs. Source verification reuses the
accepted 2030 original hourly and case archives.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_five_window_robustness import WINDOWS,validate_windows
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET,MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

GROUP_STATES={2:"CO",3:"ID"}
SUPPLY="ordinal24_wave_A"
def evaluate(hourly,original,group):
    validate_windows()
    if group not in GROUP_STATES:raise ValueError("E3 is frozen to groups 2 and 3")
    src=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                   (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Original source hours are incomplete")
    if int(src.planning_year.iloc[0])!=2030 or src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1:
        raise ValueError("Invalid frozen source identity")
    state=str(src.state.iloc[0])
    if state.upper() not in (GROUP_STATES[group],{"CO":"Colorado","ID":"Idaho"}[GROUP_STATES[group]].upper()):
        raise ValueError(f"Source group {group} not its predeclared state: {state}")
    if len(original)!=9 or original[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1:
        raise ValueError("Original full case reconciliation missing")
    load=src.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(load).all() or (load<0).any() or load.max()<=0:
        raise ValueError("Invalid source load")
    cf=shape_cf(np.arange(1,8761),SUPPLY)
    kw=dict(battery_power_peak_ratio=.25,storage_energy_peak_hours=1.)
    base,tr=solve_zone(load,cf,4,return_trace=True,**kw)
    cost=float(base["objective_illustrative_variable_usd"])
    old=original.loc[(original.synthetic_supply_shape==SUPPLY)&(original.battery_duration_h==4)]
    if len(old)!=1 or not np.isclose(cost,float(old.annual_toy_cost_usd.iloc[0]),rtol=1e-9,atol=.03):
        raise ValueError("Original source 4-hour archived objective mismatch")
    tol=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*cost)
    schedules=[]
    for label,(first,last) in WINDOWS.items():
        mask=np.zeros(8760);mask[first-1:last]=1.
        solutions={"baseline":(base,tr)}
        for direction in ("min","max"):
            solutions[direction]=solve_zone(load,cf,4,return_trace=True,
               discharge_extremum=direction,discharge_hour_weights=mask,
               original_cost_ceiling_usd=cost+tol,**kw)
        for name,(res,trace) in solutions.items():
            c=float(res["objective_illustrative_variable_usd"])
            if c>cost+tol+COST_NUMERICAL_SLACK_USD or c<cost-max(.03,tol):
                raise ValueError("E3 candidate violates original near-optimal cost cap")
            if res["max_equality_residual_mwh"]>1e-5 or abs(res["storage_terminal_soc_mwh"])>1e-5:
                raise ValueError("E3 conservation/terminal SOC constraint failed")
            d=trace.storage_discharge_to_load_mwh.to_numpy(dtype=float)
            if len(d)!=8760 or not np.isfinite(d).all():
                raise ValueError("E3 trace missing original 8760 hours")
            schedules.append({"source_group":group,"state":state,
               "reeds_zone":str(src.reeds_zone.iloc[0]),"window":label,
               "start_source_ordinal":first,"end_source_ordinal":last,
               "solution":name,"window_discharge_mwh":float(d@mask),
               "annual_discharge_mwh":float(d.sum()),
               "optimal_cost_usd":cost,"cost_allowance_usd":tol,
               "candidate_cost_usd":c,
               "candidate_cost_gap_usd":c-cost,
               "max_hourly_equality_residual_mwh":res["max_equality_residual_mwh"],
               "terminal_soc_mwh":res["storage_terminal_soc_mwh"]})
    schedules=pd.DataFrame(schedules)
    if len(schedules)!=15 or schedules.duplicated(["window","solution"]).any():
        raise ValueError("Missing E3 frozen 5x3 solutions")
    env=schedules.pivot(index=["source_group","state","reeds_zone","window",
         "start_source_ordinal","end_source_ordinal"],columns="solution",
         values="window_discharge_mwh").reset_index()
    env["span_mwh"]=env["max"]-env["min"]
    env["span_pct_window_base"]=100*env.span_mwh/env.baseline.replace(0,np.nan)
    env["span_pct_annual_base"]=100*env.span_mwh/float(base["storage_discharge_to_load_mwh"])
    if len(env)!=5 or (env["min"]>env.baseline+.03).any() or (env.baseline>env["max"]+.03).any():
        raise ValueError("Baseline outside near-optimal E3 interval")
    return schedules,env

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--hourly",type=Path,required=True)
    a.add_argument("--original",type=Path,required=True)
    a.add_argument("--group",type=int,choices=(2,3),required=True)
    a.add_argument("--out-dir",type=Path,required=True)
    p=a.parse_args()
    detail,env=evaluate(pd.read_csv(p.hourly,compression="infer"),pd.read_csv(p.original),p.group)
    p.out_dir.mkdir(parents=True,exist_ok=True)
    detail.to_csv(p.out_dir/"paper_s_e3_fifteen_lp_window_rows.csv",index=False,float_format="%.12g")
    env.to_csv(p.out_dir/"paper_s_e3_five_window_intervals.csv",index=False,float_format="%.12g")
    (p.out_dir/"paper_s_e3_manifest.json").write_text(json.dumps({
       "status":"E3_FINITE_TWO_PREDECLARED_INDEPENDENT_SOURCE_SHAPES",
       "source_group":p.group,"windows":WINDOWS,"physical_utc_certified":False,
       "new_window_search_forbidden":True,"new_shape_groups_forbidden":True},indent=2)+"\n")
    print(env.to_string(index=False))
if __name__=="__main__":main()
