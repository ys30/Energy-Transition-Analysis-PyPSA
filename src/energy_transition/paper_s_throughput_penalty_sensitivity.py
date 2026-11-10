"""Source-archived 2030 Wave-A discharge throughput penalty sensitivity.

At each penalty p in USD/MWh discharged, C_p=C_original+p*sum(d).
Re-optimize C_p, then bound discharge in the fixed original source-hour
window 4001..4168 subject to C_p(x)<=C_p*+max(0.05,1e-9*C_p*).
This is an illustrative linear cycling cost, NOT battery degradation physics.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf

PENALTIES=(0.,1.,10.)
WINDOW=(4001,4168)
SHAPE="ordinal24_wave_A"
LIMIT_ABS_USD=.05
LIMIT_RELATIVE=1e-9
COST_TOLERANCE_USD=.02

def evaluate(hourly,original,accepted,group):
    if group not in (1,7):
        raise ValueError("Only preregistered source groups")
    src=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                    (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incomplete source-ordinal load")
    if src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(src.planning_year.iloc[0])!=2030:
        raise ValueError("Original EFS source identity changed")
    demand=src.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(demand).all() or (demand<0).any() or demand.max()<=0:
        raise ValueError("Invalid EFS source demand")
    factor=shape_cf(np.arange(1,8761),SHAPE)
    kw=dict(battery_power_peak_ratio=.25,storage_energy_peak_hours=1.)
    mask=np.zeros(8760);mask[WINDOW[0]-1:WINDOW[1]]=1.
    ref=original.loc[(original.synthetic_supply_shape==SHAPE)&
        (original.battery_duration_h==4)]
    historical=accepted.loc[(accepted.source_shape_group==group)&
                             (accepted.window=="middle_4001_4168")].set_index("solution")
    if len(ref)!=1 or set(historical.index)!={"baseline","min","max"}:
        raise ValueError("Missing previous primary objective/window archival source")
    cases=[]
    for penalty in PENALTIES:
        base,btrace=solve_zone(demand,factor,4,return_trace=True,
            discharge_throughput_cost_usd_per_mwh=penalty,**kw)
        original_cost=float(base["objective_illustrative_variable_usd"])
        total_cost=float(base["objective_with_throughput_penalty_usd"])
        if not np.isclose(total_cost,original_cost+penalty*base["storage_discharge_to_load_mwh"],atol=.02,rtol=1e-11):
            raise ValueError("Penalty-plus-original objective accounting failed")
        if penalty==0 and not np.isclose(original_cost,float(ref.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
            raise ValueError("Unpenalized baseline differs from original source archive")
        slack=max(LIMIT_ABS_USD,LIMIT_RELATIVE*total_cost)
        schedules={"baseline":(base,btrace)}
        for extrema in ("min","max"):
            schedules[extrema]=solve_zone(demand,factor,4,return_trace=True,
                discharge_throughput_cost_usd_per_mwh=penalty,
                discharge_extremum=extrema,discharge_hour_weights=mask,
                original_cost_ceiling_usd=total_cost+slack,**kw)
        for mode,(summary,trace) in schedules.items():
            window=float(trace.storage_discharge_to_load_mwh.to_numpy()@mask)
            penalized=float(summary["objective_with_throughput_penalty_usd"])
            orig=float(summary["objective_illustrative_variable_usd"])
            discharge=float(trace.storage_discharge_to_load_mwh.sum())
            if abs(penalized-(orig+penalty*discharge))>.03:
                raise ValueError("Re-scored source penalty mismatch")
            if penalized>total_cost+slack+COST_TOLERANCE_USD or penalized<total_cost-max(.03,1e-9*total_cost):
                raise ValueError("Candidate not in stated penalized cost sublevel set")
            if summary["max_equality_residual_mwh"]>1e-5 or abs(summary["storage_terminal_soc_mwh"])>1e-5:
                raise ValueError("Original source hourly constraints or cycle failed")
            if penalty==0:
                old=historical.loc[mode]
                if abs(window-float(old.window_discharge_mwh))>.1 or abs(orig-float(old.candidate_original_cost_usd))>.05:
                    raise ValueError("Unpenalized case does not reproduce accepted historical window LP")
            cases.append(dict(source_shape_group=group,state=str(src.state.iloc[0]),reeds_zone=str(src.reeds_zone.iloc[0]),
                synthetic_supply_shape=SHAPE,source_window_first=WINDOW[0],source_window_last=WINDOW[1],
                penalty_usd_per_discharge_mwh=penalty,solution=mode,
                optimal_penalized_cost_usd=total_cost,allowed_cost_increase_usd=slack,
                original_variable_cost_usd=orig,
                throughput_penalty_component_usd=penalty*discharge,
                penalized_objective_usd=penalized,
                annual_discharge_mwh=discharge,selected_window_discharge_mwh=window,
                simultaneous_charge_discharge_hours=int(((trace.storage_charge_input_mwh>1e-6)&
                      (trace.storage_discharge_to_load_mwh>1e-6)).sum())))
    out=pd.DataFrame(cases)
    if len(out)!=9 or out.duplicated(["penalty_usd_per_discharge_mwh","solution"]).any():
        raise ValueError("Expected 3 penalties x 3 solutions")
    envelopes=[]
    for penalty,a in out.groupby("penalty_usd_per_discharge_mwh"):
        m=a.set_index("solution")
        width=float(m.loc["max","selected_window_discharge_mwh"]-m.loc["min","selected_window_discharge_mwh"])
        if width<-.05 or m.loc["min","selected_window_discharge_mwh"]>m.loc["baseline","selected_window_discharge_mwh"]+.05 or m.loc["baseline","selected_window_discharge_mwh"]>m.loc["max","selected_window_discharge_mwh"]+.05:
            raise ValueError("Original schedule outside penalized discharge interval")
        envelopes.append(dict(source_shape_group=group,state=str(src.state.iloc[0]),
           reeds_zone=str(src.reeds_zone.iloc[0]),penalty_usd_per_discharge_mwh=penalty,
           baseline_window_discharge_mwh=float(m.loc["baseline","selected_window_discharge_mwh"]),
           lower_window_discharge_mwh=float(m.loc["min","selected_window_discharge_mwh"]),
           upper_window_discharge_mwh=float(m.loc["max","selected_window_discharge_mwh"]),
           window_interval_width_mwh=width,
           baseline_annual_discharge_mwh=float(m.loc["baseline","annual_discharge_mwh"]),
           optimal_penalized_cost_usd=float(m.loc["baseline","optimal_penalized_cost_usd"]),
           allowed_cost_increase_usd=float(m.loc["baseline","allowed_cost_increase_usd"])))
    return out,pd.DataFrame(envelopes)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--accepted-window",type=Path,required=True)
    p.add_argument("--group",type=int,choices=(1,7),required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    args=p.parse_args()
    rows,env=evaluate(pd.read_csv(args.hourly,compression="infer"),
        pd.read_csv(args.original),pd.read_csv(args.accepted_window),args.group)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    rows.to_csv(args.out_dir/"paper_s_penalty_nine_source_lp_solutions.csv",index=False,float_format="%.12g")
    env.to_csv(args.out_dir/"paper_s_penalty_three_window_envelopes.csv",index=False,float_format="%.12g")
    manifest={"status":"ORIGINAL_SOURCE_PENALIZED_DISPATCH_LP_RESCORING_PASS",
       "penalty_levels_usd_per_discharge_mwh":list(PENALTIES),
       "source_group":args.group,"window":[WINDOW[0],WINDOW[1]],
       "cost_sublevel_objective":"original variable cost + penalty * annual discharged MWh",
       "not_equivalent_to_measured_battery_degradation":True,
       "true_exclusive_MILP_computed":False,
       "actual_weather_or_Western_OPF":False,"physical_calendar_axis_verified":False}
    (args.out_dir/"paper_s_penalty_sensitivity_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(env.to_string(index=False))
if __name__=="__main__":main()
