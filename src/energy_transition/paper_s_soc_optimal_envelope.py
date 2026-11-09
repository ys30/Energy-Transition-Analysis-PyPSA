"""Lexicographic-like SOC envelopes with an explicit bound on ORIGINAL LP cost.

For each archived source LP probe, compute min and max annual sum of end-hour
SOC over C(x) <= C* + epsilon. This is a near-optimal *energy occupancy* envelope,
NOT a mathematical bound on every individual hourly SOC or on bound-hour counts.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf
from .paper_s_soc_tiebreak import PROBES

RELATIVE_BUDGET=1e-9
MINIMUM_BUDGET_USD=.05
COST_NUMERICAL_SLACK_USD=.02

def evaluate(hourly, original, group):
    if group not in (1,7):raise ValueError("Only preregistered EFS source groups 1,7")
    source=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                      (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(source)!=8760 or not np.array_equal(source.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Source ordinal hour population incomplete")
    if source[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1:
        raise ValueError("Ambiguous demand source identity")
    d=source.demand_mwh.to_numpy(dtype=float)
    if source.planning_year.iloc[0]!=2030 or not np.isfinite(d).all() or d.max()<=0 or (d<0).any():
        raise ValueError("Invalid original 2030 demand")
    if len(original)!=9:raise ValueError("Missing original nine source archival outcomes")
    summaries=[];hourlies=[]
    for shape,power,energy in PROBES:
        cf=shape_cf(np.arange(1,8761),shape)
        base,baseline_trace=solve_zone(d,cf,4,battery_power_peak_ratio=power,
                      storage_energy_peak_hours=energy,return_trace=True)
        reference=float(base["objective_illustrative_variable_usd"])
        if power==.25 and energy==1.:
            prior=original[(original.synthetic_supply_shape==shape)&
                           (original.battery_duration_h==4)]
            if len(prior)!=1 or not np.isclose(reference,float(prior.iloc[0].annual_toy_cost_usd),rtol=1e-9,atol=.03):
                raise ValueError("Unmodified LP fails archived original-cost validation")
        budget=max(MINIMUM_BUDGET_USD,RELATIVE_BUDGET*reference)
        ceiling=reference+budget
        solutions={"baseline":(base,baseline_trace)}
        for mode in ("min","max"):
            solutions[mode]=solve_zone(d,cf,4,battery_power_peak_ratio=power,
                          storage_energy_peak_hours=energy,return_trace=True,
                          soc_extremum=mode,original_cost_ceiling_usd=ceiling)
        min_tot=float(solutions["min"][1].soc_end_mwh.sum())
        max_tot=float(solutions["max"][1].soc_end_mwh.sum())
        baseline_tot=float(baseline_trace.soc_end_mwh.sum())
        if min_tot>max_tot+max(.01,1e-7*max_tot) or baseline_tot<min_tot-max(.01,1e-7*max_tot) or baseline_tot>max_tot+max(.01,1e-7*max_tot):
            raise ValueError("Baseline SOC occupancy is not inside computed envelope")
        for mode,(res,trace) in solutions.items():
            cost=float(res["objective_illustrative_variable_usd"])
            gap=cost-reference
            if gap>budget+COST_NUMERICAL_SLACK_USD:
                raise ValueError("Near-optimal solution violates original objective cap")
            if gap< -max(.03,1e-9*reference):
                raise ValueError("Secondary solution spuriously beats original LP optimum")
            soc=np.asarray(trace.soc_end_mwh,dtype=float)
            if len(soc)!=8760 or not np.isfinite(soc).all():
                raise ValueError("Incomplete secondary source trace")
            summaries.append({"source_shape_group":group,
                "state":str(source.state.iloc[0]),"reeds_zone":str(source.reeds_zone.iloc[0]),
                "synthetic_supply_shape":shape,"battery_power_peak_ratio":power,
                "battery_energy_peak_hours":energy,"solution":mode,
                "reference_original_lp_cost_usd":reference,
                "original_lp_cost_ceiling_usd":ceiling,
                "allowed_cost_increase_usd":budget,
                "original_cost_candidate_usd":cost,
                "candidate_cost_gap_usd":gap,
                "total_soc_mwh_hours":float(soc.sum()),
                "mean_soc_fraction":float(soc.mean()/res["storage_capacity_mwh"]),
                "soc_capacity_bound_hours":int(trace.soc_at_energy_limit.sum()),
                "charge_power_bound_hours":int(trace.charge_at_power_limit.sum()),
                "discharge_power_bound_hours":int(trace.discharge_at_power_limit.sum()),
                "charged_mwh":float(trace.storage_charge_input_mwh.sum()),
                "discharged_mwh":float(trace.storage_discharge_to_load_mwh.sum()),
                "max_equality_residual_mwh":res["max_equality_residual_mwh"],
                "terminal_soc_mwh":res["storage_terminal_soc_mwh"]})
            row=pd.DataFrame({"local_hour_id":trace.local_hour_id,
                 "soc_end_mwh":trace.soc_end_mwh,
                 "battery_capacity_mwh":res["storage_capacity_mwh"]})
            for name,value in (("source_shape_group",group),
                  ("synthetic_supply_shape",shape),("battery_power_peak_ratio",power),
                  ("battery_energy_peak_hours",energy),("solution",mode)):
                row.insert(0,name,value)
            hourlies.append(row)
    frame=pd.DataFrame(summaries)
    traces=pd.concat(hourlies,ignore_index=True)
    if len(frame)!=12 or len(traces)!=12*8760:
        raise ValueError("Incomplete four-probe three-solution SOC envelope")
    return frame,traces

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-hourly",required=True,type=Path)
    p.add_argument("--original-metrics",required=True,type=Path)
    p.add_argument("--group",required=True,type=int,choices=(1,7))
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    summary,traces=evaluate(pd.read_csv(a.original_hourly,compression="infer"),
                   pd.read_csv(a.original_metrics),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    summary.to_csv(a.out_dir/"paper_s_soc_optimal_envelope_summary.csv",index=False)
    traces.to_csv(a.out_dir/"paper_s_soc_optimal_envelope_hourly.csv.gz",index=False,compression="gzip")
    metadata={"status":"SOC_MIN_MAX_OVER_EXPLICIT_ORIGINAL_COST_SUBLEVEL_SET",
        "source_group":a.group,"probes":4,"solutions":12,
        "hourly_rows":int(len(traces)),
        "relative_cost_tolerance":RELATIVE_BUDGET,
        "minimum_cost_tolerance_usd":MINIMUM_BUDGET_USD,
        "not_bounds_on_individual_hours_or_active_bound_counts":True,
        "not_strict_exact_alternative_optimum_proof":True,
        "real_solar_wind_data":False,"certified_utc":False}
    (a.out_dir/"paper_s_soc_optimal_envelope_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n")
    print(summary.to_string(index=False))
    print(json.dumps(metadata,indent=2))

if __name__=="__main__":main()
