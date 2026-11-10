"""Min and max annual battery discharge over explicitly cost-capped LP feasible set.

Distinct from SOC-occupancy envelope. We do NOT optimize bound-hour counts or
assert every hourly dispatch is bounded by these annual discharge extrema.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_soc_tiebreak import PROBES
from .paper_s_soc_optimal_envelope import RELATIVE_BUDGET,MINIMUM_BUDGET_USD,COST_NUMERICAL_SLACK_USD

def evaluate(hourly, original, group):
    if group not in (1,7):raise ValueError("Only preregistered groups 1 and 7")
    src=hourly[(hourly.synthetic_supply_shape=="flat_50pct")&
        (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(src)!=8760 or not np.array_equal(src.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incomplete original source-hour sequence")
    if src[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1 or src.planning_year.iloc[0]!=2030:
        raise ValueError("Invalid original source zone and year")
    demand=src.demand_mwh.to_numpy(dtype=float)
    if (not np.isfinite(demand).all()) or np.min(demand)<0 or demand.max()<=0:
        raise ValueError("Invalid source demand")
    if len(original)!=9:raise ValueError("Missing original annual archival data")
    results=[]
    for shape,power,energy in PROBES:
        cf=shape_cf(np.arange(1,8761),shape)
        kwargs=dict(battery_power_peak_ratio=power,storage_energy_peak_hours=energy)
        baseline,base_trace=solve_zone(demand,cf,4,return_trace=True,**kwargs)
        optimal=float(baseline["objective_illustrative_variable_usd"])
        if power==.25 and energy==1.:
            ref=original[(original.synthetic_supply_shape==shape)&(original.battery_duration_h==4)]
            if len(ref)!=1 or not np.isclose(optimal,float(ref.annual_toy_cost_usd.iloc[0]),rtol=1e-9,atol=.03):
                raise ValueError("Original LP archival baseline mismatch")
        epsilon=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*optimal)
        candidates={"baseline":(baseline,base_trace)}
        for extremum in ("min","max"):
            candidates[extremum]=solve_zone(
                demand,cf,4,return_trace=True,discharge_extremum=extremum,
                original_cost_ceiling_usd=optimal+epsilon,**kwargs)
        low=float(candidates["min"][1].storage_discharge_to_load_mwh.sum())
        mid=float(base_trace.storage_discharge_to_load_mwh.sum())
        high=float(candidates["max"][1].storage_discharge_to_load_mwh.sum())
        if low>mid+0.02 or mid>high+0.02:
            raise ValueError("Original discharge is outside optimized envelope")
        for mode,(summary,trace) in candidates.items():
            cost=float(summary["objective_illustrative_variable_usd"])
            if (cost>optimal+epsilon+COST_NUMERICAL_SLACK_USD or
                cost<optimal-max(.03,1e-9*optimal)):
                raise ValueError("Original cost of candidate violates tight optimality gate")
            if summary["max_equality_residual_mwh"]>1e-5 or abs(summary["storage_terminal_soc_mwh"])>1e-5:
                raise ValueError("Original energy/SOC mass balance gate failed")
            results.append(dict(
                source_shape_group=group,state=str(src.state.iloc[0]),
                reeds_zone=str(src.reeds_zone.iloc[0]),
                synthetic_supply_shape=shape,battery_power_peak_ratio=power,
                battery_energy_peak_hours=energy,solution=mode,
                original_optimum_usd=optimal,allowed_cost_increase_usd=epsilon,
                original_cost_candidate_usd=cost,original_cost_gap_usd=cost-optimal,
                annual_discharge_mwh=float(trace.storage_discharge_to_load_mwh.sum()),
                annual_charge_mwh=float(trace.storage_charge_input_mwh.sum()),
                annual_firm_mwh=float(trace.firm_generation_mwh.sum()),
                annual_unused_mwh=float(trace.unused_renewable_mwh.sum()),
                mean_soc_fraction=float(trace.soc_end_mwh.mean()/summary["storage_capacity_mwh"]),
                soc_at_capacity_hours=int(trace.soc_at_energy_limit.sum()),
                charge_power_limit_hours=int(trace.charge_at_power_limit.sum()),
                discharge_power_limit_hours=int(trace.discharge_at_power_limit.sum())))
    frame=pd.DataFrame(results)
    if len(frame)!=12 or frame.duplicated(["synthetic_supply_shape",
            "battery_power_peak_ratio","battery_energy_peak_hours","solution"]).any():
        raise ValueError("Expected 12 accepted LP cases")
    return frame

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--hourly",required=True,type=Path)
    ap.add_argument("--original",required=True,type=Path)
    ap.add_argument("--group",required=True,type=int,choices=(1,7))
    ap.add_argument("--out-dir",required=True,type=Path)
    x=ap.parse_args()
    a=evaluate(pd.read_csv(x.hourly,compression="infer"),pd.read_csv(x.original),x.group)
    x.out_dir.mkdir(parents=True,exist_ok=True)
    a.to_csv(x.out_dir/"paper_s_discharge_envelope_12_solutions.csv",index=False,float_format="%.12g")
    meta={"status":"COST_CAPPED_ANNUAL_DISCHARGE_ENVELOPE_VALIDATED",
          "group":x.group,"solution_rows":len(a),"case_probes":4,
          "original_cost_budget_relative":RELATIVE_BUDGET,
          "original_cost_budget_minimum_usd":MINIMUM_BUDGET_USD,
          "strict_exact_optimal_face":False,"bounds_on_annual_discharge_only":True,
          "real_solar_wind_or_western_opf":False}
    (x.out_dir/"paper_s_discharge_envelope_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(a.to_string(index=False))
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
