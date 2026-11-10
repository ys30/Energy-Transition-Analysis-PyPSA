"""Fixed-window discharge robustness to absolute original-cost allowances.

This test deliberately uses a strict absolute-dollar ladder and the previously
accepted 1e-9 relative budget. It never calls USD 0.05 an exact-optimal
certificate: HiGHS objective and feasibility tolerances still matter.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf

SHAPE="ordinal24_wave_A"
POWER=.25
ENERGY=1.
WINDOW=(4001,4168)
ABSOLUTE_BUDGETS=(.05,.2)
RELATIVE_BUDGET=1e-9
COST_SLACK=.02

def analyze(hourly, original, group):
    if group not in (1,7):raise ValueError("Only archived shape groups 1 and 7")
    a=hourly[(hourly.synthetic_supply_shape=="flat_50pct")&
             (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(a)!=8760 or not np.array_equal(a.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incomplete original source ordinal chronology")
    if a[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or int(a.planning_year.iloc[0])!=2030:
        raise ValueError("Unverified source identity")
    demand=a.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(demand).all() or (demand<0).any() or demand.max()<=0:
        raise ValueError("Invalid original demand")
    kw=dict(battery_power_peak_ratio=POWER,storage_energy_peak_hours=ENERGY)
    cf=shape_cf(np.arange(1,8761),SHAPE)
    base,baseline_trace=solve_zone(demand,cf,4,return_trace=True,**kw)
    c0=float(base["objective_illustrative_variable_usd"])
    previous=original[(original.synthetic_supply_shape==SHAPE)&(original.battery_duration_h==4)]
    if len(previous)!=1 or not np.isclose(c0,float(previous.annual_toy_cost_usd.iloc[0]),atol=.03,rtol=1e-9):
        raise ValueError("Original historical LP objective no longer matches")
    mask=np.zeros(8760);mask[WINDOW[0]-1:WINDOW[1]]=1
    assert int(mask.sum())==168
    baseline=float(baseline_trace.storage_discharge_to_load_mwh.to_numpy()@mask)
    budgets=[("absolute_0p05",.05),("absolute_0p20",.2),
             ("archived_1e-9",max(.05,RELATIVE_BUDGET*c0))]
    if budgets[-1][1] < .2:
        raise ValueError("Archived 1e-9 budget unexpectedly smaller than 0.2 USD")
    output=[]
    for label,allowance in budgets:
        records={}
        for direction in ("min","max"):
            result,trace=solve_zone(demand,cf,4,return_trace=True,
                discharge_extremum=direction,discharge_hour_weights=mask,
                original_cost_ceiling_usd=c0+allowance,**kw)
            cost=float(result["objective_illustrative_variable_usd"])
            if cost>c0+allowance+COST_SLACK or cost<c0-max(.03,1e-9*c0):
                raise ValueError("Cost-constrained optimum outside original objective cap")
            if result["max_equality_residual_mwh"]>1e-5 or abs(result["storage_terminal_soc_mwh"])>1e-5:
                raise ValueError("Hourly SOC/balance regression failed")
            records[direction]=(float(trace.storage_discharge_to_load_mwh.to_numpy()@mask),
                                cost-c0)
        low,low_gap=records["min"]
        high,high_gap=records["max"]
        if low>baseline+.05 or baseline>high+.05:
            raise ValueError("Original schedule outside near-optimal window interval")
        output.append(dict(source_shape_group=group,state=str(a.state.iloc[0]),
            reeds_zone=str(a.reeds_zone.iloc[0]),supply_shape=SHAPE,
            source_window_start=WINDOW[0],source_window_end=WINDOW[1],
            tolerance_label=label,allowed_extra_cost_usd=allowance,
            original_optimum_cost_usd=c0,
            baseline_window_discharge_mwh=baseline,
            minimum_window_discharge_mwh=low,
            maximum_window_discharge_mwh=high,
            window_discharge_span_mwh=high-low,
            minimum_schedule_cost_gap_usd=low_gap,
            maximum_schedule_cost_gap_usd=high_gap,
            positive_span_gt_1mwh=bool(high-low>1.)))
    out=pd.DataFrame(output)
    if len(out)!=3 or out.duplicated(["source_shape_group","tolerance_label"]).any():
        raise ValueError("Incomplete absolute/relative tolerance ladder")
    if (out.window_discharge_span_mwh<-.05).any():
        raise ValueError("Inverted source discharge envelope")
    # Relaxation of the allowance cannot mathematically reduce an attainable
    # range; allow small solver noise but fail on a materially inverted ladder.
    if np.any(np.diff(out.window_discharge_span_mwh.to_numpy()) < -1.):
        raise ValueError("Cost sublevel ladder produced nonnested discharge spans")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",required=True,type=Path)
    p.add_argument("--original",required=True,type=Path)
    p.add_argument("--group",required=True,type=int,choices=(1,7))
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    results=analyze(pd.read_csv(a.hourly,compression="infer"),
                    pd.read_csv(a.original),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    results.to_csv(a.out_dir/"paper_s_window_tolerance_ladder.csv",index=False,float_format="%.12g")
    note={"status":"COST_CAP_TOLERANCE_LADDER_ORIGINAL_SOURCE_VALIDATED",
          "group":a.group,"source_window":[WINDOW[0],WINDOW[1]],
          "absolute_usd_allowances":list(ABSOLUTE_BUDGETS),
          "archived_relative_allowance":RELATIVE_BUDGET,
          "extra_numerical_cost_slack_usd":COST_SLACK,
          "cost_tolerance_not_an_exact_optimal_face_certificate":True,
          "source_hour_axis_is_not_certified_UTC":True}
    (a.out_dir/"paper_s_window_tolerance_manifest.json").write_text(json.dumps(note,indent=2)+"\n")
    print(results.to_string(index=False))
    print(json.dumps(note,indent=2))
if __name__=="__main__":main()
