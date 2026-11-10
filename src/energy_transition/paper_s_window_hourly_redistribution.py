"""Reconstruct full-hour LP dispatch alternatives for predeclared Wave-A window.

The reported outside-window offset is localized into 24-source-hour blocks.
All candidates are re-scored under the original objective and reconciled to
previously archived window min/max and annual results.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_window_discharge_envelope import SHAPE,POWER,ENERGY,WINDOWS
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET, MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

WINDOW="middle_4001_4168"
DAY_BLOCK=24
TRACE_COLUMNS=["storage_charge_input_mwh","storage_discharge_to_load_mwh",
               "soc_end_mwh","firm_generation_mwh","unused_renewable_mwh"]
ARCHIVE_ATOL_MWH=.1

def reconstruct(hourly,original,accepted,group):
    if group not in (1,7):raise ValueError("Only original preregistered groups 1 and 7")
    src=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                   (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Original EFS source-hour chronology missing or reordered")
    if src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(src.planning_year.iloc[0])!=2030:
        raise ValueError("Original 2030 source identity invalid")
    demand=src.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(demand).all() or (demand<0).any() or demand.max()<=0:
        raise ValueError("Invalid original hourly demand")
    if len(original)!=9:raise ValueError("Missing previously accepted nine-case summary")
    window_start,window_end=WINDOWS[WINDOW]
    mask=np.zeros(8760,dtype=float);mask[window_start-1:window_end]=1.
    prior=accepted.loc[(accepted.source_shape_group==group)&(accepted.window==WINDOW)]
    if len(prior)!=3 or set(prior.solution)!={"baseline","min","max"}:
        raise ValueError("Missing certified original middle-window candidate triple")
    previous_baseline=original.loc[(original.synthetic_supply_shape==SHAPE)&
                                   (original.battery_duration_h==4)]
    if len(previous_baseline)!=1:raise ValueError("Missing original four-hour LP")
    factor=shape_cf(np.arange(1,8761),SHAPE)
    kwargs={"battery_power_peak_ratio":POWER,"storage_energy_peak_hours":ENERGY}
    baseline,btrace=solve_zone(demand,factor,4,return_trace=True,**kwargs)
    original_cost=float(baseline["objective_illustrative_variable_usd"])
    if not np.isclose(original_cost,float(previous_baseline.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
        raise ValueError("New baseline differs from original full-year archive")
    allowance=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*original_cost)
    if not np.isclose(allowance,float(prior.original_cost_budget_usd.iloc[0]),atol=.02,rtol=1e-9):
        raise ValueError("Cost allowance differs from accepted source archive")
    solutions={"baseline":(baseline,btrace)}
    for ext in ("min","max"):
        solutions[ext]=solve_zone(demand,factor,4,return_trace=True,
            discharge_extremum=ext,discharge_hour_weights=mask,
            original_cost_ceiling_usd=original_cost+allowance,**kwargs)
    summaries=[];traces=[]
    for mode,(result,trace) in solutions.items():
        old=prior.loc[prior.solution==mode].iloc[0]
        window=float(trace.storage_discharge_to_load_mwh.to_numpy()@mask)
        annual=float(trace.storage_discharge_to_load_mwh.sum())
        cost=float(result["objective_illustrative_variable_usd"])
        if (abs(window-float(old.window_discharge_mwh))>ARCHIVE_ATOL_MWH or
            abs(annual-float(old.annual_discharge_mwh))>ARCHIVE_ATOL_MWH or
            abs(cost-float(old.candidate_original_cost_usd))>.05):
            raise ValueError("Reconstructed hourly case does not match original accepted LP outcome")
        if cost>original_cost+allowance+COST_NUMERICAL_SLACK_USD or cost<original_cost-max(.03,RELATIVE_BUDGET*original_cost):
            raise ValueError("Reconstructed candidate violates original optimal-cost cap")
        if result["max_equality_residual_mwh"]>1e-5 or abs(result["storage_terminal_soc_mwh"])>1e-5:
            raise ValueError("Hourly mass balance / cyclic SOC check failed")
        summaries.append({"source_shape_group":group,"state":str(src.state.iloc[0]),
            "reeds_zone":str(src.reeds_zone.iloc[0]),"solution":mode,
            "window":WINDOW,"original_cost_usd":cost,"allowed_extra_cost_usd":allowance,
            "window_discharge_mwh":window,"annual_discharge_mwh":annual,
            "outside_discharge_mwh":annual-window,
            "annual_charge_mwh":float(trace.storage_charge_input_mwh.sum()),
            "mean_soc_mwh":float(trace.soc_end_mwh.mean())})
        t=trace[["local_hour_id"]+TRACE_COLUMNS].copy()
        t.insert(0,"solution",mode)
        t.insert(0,"source_shape_group",group)
        t["in_predeclared_window"]=mask.astype(bool)
        t["source_day_block"]=((t.local_hour_id-1)//DAY_BLOCK+1).astype(int)
        traces.append(t)
    summary=pd.DataFrame(summaries)
    detailed=pd.concat(traces,ignore_index=True)
    wide={mode:detailed[detailed.solution==mode].set_index("local_hour_id") for mode in ("baseline","min","max")}
    recon=[]
    for mode in ("min","max"):
        change=wide[mode][TRACE_COLUMNS]-wide["baseline"][TRACE_COLUMNS]
        if not np.array_equal(change.index.to_numpy(),np.arange(1,8761)):
            raise ValueError("Mismatch in original ordered hours")
        delta_discharge=change.storage_discharge_to_load_mwh
        x=change.copy()
        x["source_day_block"]=((x.index.to_numpy()-1)//DAY_BLOCK+1).astype(int)
        x["in_predeclared_window"]=mask.astype(bool)
        grouped=x.groupby(["source_day_block","in_predeclared_window"],sort=True)[TRACE_COLUMNS].sum().reset_index()
        grouped.insert(0,"candidate_solution",mode)
        grouped.insert(0,"source_shape_group",group)
        recon.append(grouped)
        delta_inside=float(delta_discharge.to_numpy()@mask)
        delta_outside=float(delta_discharge.sum()-delta_inside)
        row=summary.set_index("solution")
        check_in=float(row.loc[mode,"window_discharge_mwh"]-row.loc["baseline","window_discharge_mwh"])
        check_out=float(row.loc[mode,"outside_discharge_mwh"]-row.loc["baseline","outside_discharge_mwh"])
        if not np.isclose(delta_inside,check_in,atol=1e-5,rtol=1e-10) or not np.isclose(delta_outside,check_out,atol=1e-5,rtol=1e-10):
            raise ValueError("Actual hourly deltas do not reconcile with archive-derived outside-window accounting")
        if not np.isclose(grouped.storage_discharge_to_load_mwh.sum(),delta_discharge.sum(),atol=1e-5,rtol=1e-10):
            raise ValueError("24-hour grouped redistribution fails original full-year identity")
    days=pd.concat(recon,ignore_index=True)
    if len(summary)!=3 or len(detailed)!=3*8760 or len(days)!=2*365:
        raise ValueError("Incomplete source trace or daily-block candidate population")
    return summary,detailed,days

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hourly",required=True,type=Path)
    ap.add_argument("--original",required=True,type=Path)
    ap.add_argument("--accepted-window",required=True,type=Path)
    ap.add_argument("--group",type=int,choices=(1,7),required=True)
    ap.add_argument("--out-dir",required=True,type=Path)
    a=ap.parse_args()
    summary,hourly,blocks=reconstruct(pd.read_csv(a.hourly,compression="infer"),
         pd.read_csv(a.original),pd.read_csv(a.accepted_window),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(a.out_dir/"paper_s_reconstructed_three_original_window_schedules.csv",index=False)
    hourly.to_csv(a.out_dir/"paper_s_three_full_hour_window_dispatch_traces.csv.gz",index=False,compression="gzip")
    blocks.to_csv(a.out_dir/"paper_s_two_candidate_24source_hour_redistribution.csv",index=False)
    meta={"status":"RECONSTRUCTED_THREE_SOURCE_HOUR_FULL_LP_TRACES_RECONCILED",
          "group":a.group,"full_year_hourly_rows":len(hourly),"delta_24hour_rows":len(blocks),
          "source_day_blocks_are_not_calendar_dates":True,
          "selected_window":WINDOW,"original_cost_ceiling_verified":True,
          "archive_hourly_outputs_reconciled":True,
          "source_resource_profiles_are_synthetic":True}
    (a.out_dir/"paper_s_window_hourly_redistribution_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))
    for mode in ("min","max"):
        subset=blocks[(blocks.candidate_solution==mode)&(~blocks.in_predeclared_window)]
        top=subset.reindex(subset.storage_discharge_to_load_mwh.abs().sort_values(ascending=False).index).head(8)
        print("GROUP",a.group,"MODE",mode,"TOP_OUTSIDE_24H_BLOCKS")
        print(top[["source_day_block","storage_discharge_to_load_mwh",
                   "storage_charge_input_mwh","soc_end_mwh"]].to_string(index=False))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
