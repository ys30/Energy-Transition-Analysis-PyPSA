"""Five preregistered, mutually disjoint 168-source-hour near-optimal discharge envelopes.

No calendar/UTC inference: original EFS local_hour_id is an ordinal. All
five windows are fixed without reading dispatch; the original 4001..4168
interval is deliberately retained to cross-audit previously accepted LPs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET,MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

WINDOWS={"ordinal_0001":(1,168),"ordinal_2001":(2001,2168),
         "ordinal_4001_reference":(4001,4168),"ordinal_6001":(6001,6168),
         "ordinal_8001":(8001,8168)}
SHAPE="ordinal24_wave_A"

def validate_windows(windows=WINDOWS):
    hour_sets=[]
    for label,(first,last) in windows.items():
        if first<1 or last>8760 or last-first+1!=168:
            raise ValueError(f"Invalid preregistered source window {label}")
        hour_sets.append(set(range(first,last+1)))
    for i,a in enumerate(hour_sets):
        for b in hour_sets[i+1:]:
            if a&b: raise ValueError("Overlapping prespecified source windows")
    if len(windows)!=5 or windows.get("ordinal_4001_reference")!=(4001,4168):
        raise ValueError("Expected all five predeclared source windows")
    return True

def evaluate(hourly,original,accepted,group):
    validate_windows()
    if group not in (1,7):raise ValueError("Only original archived source groups 1 and 7")
    src=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                   (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Missing source ordinal population")
    if src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(src.planning_year.iloc[0])!=2030:
        raise ValueError("Original source identity changed")
    demand=src.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(demand).all() or (demand<0).any() or demand.max()<=0:
        raise ValueError("Invalid original demand source")
    ref=original.loc[(original.synthetic_supply_shape==SHAPE)&(original.battery_duration_h==4)]
    if len(original)!=9 or len(ref)!=1:raise ValueError("Missing complete historic source controls")
    cf=shape_cf(np.arange(1,8761),SHAPE)
    kw=dict(battery_power_peak_ratio=.25,storage_energy_peak_hours=1.)
    base,bt=solve_zone(demand,cf,4,return_trace=True,**kw)
    cstar=float(base["objective_illustrative_variable_usd"])
    if not np.isclose(cstar,float(ref.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
        raise ValueError("Historical optimal source objective mismatch")
    epsilon=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*cstar)
    archive=accepted.loc[(accepted.source_shape_group==group)&
             (accepted.window=="middle_4001_4168")].set_index("solution")
    if set(archive.index)!={"baseline","min","max"}:
        raise ValueError("Missing original accepted fixed-window source results")
    results=[]
    for label,(first,last) in WINDOWS.items():
        mask=np.zeros(8760);mask[first-1:last]=1.
        sols={"baseline":(base,bt)}
        for direction in ("min","max"):
            sols[direction]=solve_zone(demand,cf,4,return_trace=True,
                discharge_extremum=direction,discharge_hour_weights=mask,
                original_cost_ceiling_usd=cstar+epsilon,**kw)
        for mode,(m,tr) in sols.items():
            window=float(tr.storage_discharge_to_load_mwh.to_numpy()@mask)
            annual=float(tr.storage_discharge_to_load_mwh.sum())
            original_cost=float(m["objective_illustrative_variable_usd"])
            if original_cost>cstar+epsilon+COST_NUMERICAL_SLACK_USD or original_cost<cstar-max(.03,RELATIVE_BUDGET*cstar):
                raise ValueError("Cost sublevel set failed original objective audit")
            if m["max_equality_residual_mwh"]>1e-5 or abs(m["storage_terminal_soc_mwh"])>1e-5:
                raise ValueError("Hourly original source model feasibility failed")
            if label=="ordinal_4001_reference":
                row=archive.loc[mode]
                if abs(window-float(row.window_discharge_mwh))>.1 or abs(annual-float(row.annual_discharge_mwh))>.1:
                    raise ValueError("Archived 4001–4168 window mismatch")
            results.append(dict(source_group=group,state=str(src.state.iloc[0]),
                reeds_zone=str(src.reeds_zone.iloc[0]),window=label,
                start_source_ordinal=first,end_source_ordinal=last,
                solution=mode,window_discharge_mwh=window,annual_discharge_mwh=annual,
                optimal_cost_usd=cstar,cost_allowance_usd=epsilon,
                candidate_cost_usd=original_cost,
                candidate_cost_gap_usd=original_cost-cstar,
                max_hourly_equality_residual_mwh=m["max_equality_residual_mwh"],
                terminal_soc_mwh=m["storage_terminal_soc_mwh"]))
    full=pd.DataFrame(results)
    if len(full)!=15 or full.duplicated(["window","solution"]).any():
        raise ValueError("Incomplete 5-window × 3-solution matrix")
    envelope=full.pivot(index=["source_group","state","reeds_zone","window",
       "start_source_ordinal","end_source_ordinal"],columns="solution",
       values="window_discharge_mwh").reset_index()
    envelope["span_mwh"]=envelope["max"]-envelope["min"]
    envelope["span_pct_annual_base"]=100*envelope.span_mwh/float(base["storage_discharge_to_load_mwh"])
    envelope["span_pct_window_base"]=100*envelope.span_mwh/envelope.baseline.replace(0,np.nan)
    if len(envelope)!=5 or (envelope["min"]>envelope.baseline+.03).any() or (envelope.baseline>envelope["max"]+.03).any():
        raise ValueError("Baseline outside source window extrema")
    return full,envelope

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--accepted-window",type=Path,required=True)
    p.add_argument("--group",type=int,choices=(1,7),required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    detail,env=evaluate(pd.read_csv(a.hourly,compression="infer"),
        pd.read_csv(a.original),pd.read_csv(a.accepted_window),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    detail.to_csv(a.out_dir/"paper_s_fifteen_source_window_schedules.csv",index=False,float_format="%.12g")
    env.to_csv(a.out_dir/"paper_s_five_source_window_intervals.csv",index=False,float_format="%.12g")
    (a.out_dir/"paper_s_five_window_manifest.json").write_text(json.dumps({
      "status":"FIVE_FIXED_168_ORDINAL_WINDOWS_HIGHS_SOURCE_ARCHIVE_RECONCILED",
      "windows":WINDOWS,"source_group":a.group,"solutions":len(detail),
      "old_reference_window_reconciled":True,"physical_utc_verified":False,
      "source_data_representative_only":True,"not_iid_calendar_weeks":True},indent=2)+"\n")
    print(env.to_string(index=False))
if __name__=="__main__":main()
