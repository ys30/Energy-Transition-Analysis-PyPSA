"""Bounded deterministic SOC-objective perturbations on accepted EFS source-hour LPs.

This is a *near-optimal schedule sensitivity*, not an exact LP alternative-optima
certificate. Every perturbed solution is scored with the original objective.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone
from .efs_ordinal_storage_sensitivity import shape_cf

PROBES=(("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
        ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.))
MODES=("baseline","soc_penalty","soc_reward","ordinal_wiggle")
EPS=1e-5

def _weights(n,mode):
    if mode=="baseline": return None
    if mode=="soc_penalty":return np.full(n,EPS)
    if mode=="soc_reward":return np.full(n,-EPS)
    if mode=="ordinal_wiggle":
        t=np.arange(n,dtype=float)
        return EPS*np.sin(2*np.pi*t/47)
    raise ValueError("Unsupported perturbation")

def evaluate(hourly,original,group):
    if group not in (1,7):raise ValueError("Precommitted source groups are 1 and 7")
    source=hourly.loc[(hourly.synthetic_supply_shape=="flat_50pct")&
                      (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(source)!=8760 or not np.array_equal(source.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Missing original source-ordinal demand population")
    d=source.demand_mwh.to_numpy(dtype=float)
    if not np.isfinite(d).all() or d.max()<=0 or (d<0).any() or int(source.planning_year.iloc[0])!=2030:
        raise ValueError("Invalid source chronology")
    if source[["state","reeds_zone","planning_year"]].drop_duplicates().shape[0]!=1:
        raise ValueError("Invalid source-zone identity")
    if len(original)!=9:raise ValueError("Missing archived nine case annual baseline")
    rows=[]
    for shape,power,energy in PROBES:
        cf=shape_cf(np.arange(1,8761),shape)
        base,base_trace=solve_zone(d,cf,4,battery_power_peak_ratio=power,
                                   storage_energy_peak_hours=energy,return_trace=True)
        if power==.25 and energy==1.:
            prior=original.loc[(original.synthetic_supply_shape==shape)&
                                (original.battery_duration_h==4)]
            if len(prior)!=1 or not np.isclose(base["objective_illustrative_variable_usd"],
                                            float(prior.annual_toy_cost_usd.iloc[0]),rtol=1e-9,atol=.03):
                raise ValueError("Unmodified objective does not match accepted source LP")
        basis={
            "charged_mwh":float(base_trace.storage_charge_input_mwh.sum()),
            "discharged_mwh":float(base_trace.storage_discharge_to_load_mwh.sum()),
            "soc_bound_hours":int(base_trace.soc_at_energy_limit.sum()),
            "charge_bound_hours":int(base_trace.charge_at_power_limit.sum()),
            "discharge_bound_hours":int(base_trace.discharge_at_power_limit.sum()),
        }
        for mode in MODES:
            if mode=="baseline":
                result,trace=base,base_trace
            else:
                result,trace=solve_zone(d,cf,4,battery_power_peak_ratio=power,
                    storage_energy_peak_hours=energy,return_trace=True,
                    soc_tiebreak_usd_per_mwh=_weights(8760,mode))
            cost=float(result["objective_illustrative_variable_usd"])
            reference=float(base["objective_illustrative_variable_usd"])
            gap=cost-reference
            # Small perturbations cannot be reported as exactly equal objective
            # solutions unless they actually satisfy an independent strict gate.
            near_tol=max(.01,1e-6*max(1.,abs(reference)))
            if gap < -max(.03,1e-9*abs(reference)):
                raise ValueError("Perturbed solution improved certified original optimum")
            if gap>near_tol:
                raise ValueError("Perturbed solution outside precommitted near-optimal cost tolerance")
            charge=float(trace.storage_charge_input_mwh.sum())
            discharge=float(trace.storage_discharge_to_load_mwh.sum())
            soc=np.asarray(trace.soc_end_mwh,dtype=float)
            original_soc=np.asarray(base_trace.soc_end_mwh,dtype=float)
            rows.append({"source_shape_group":group,"state":str(source.state.iloc[0]),
                "reeds_zone":str(source.reeds_zone.iloc[0]),
                "synthetic_supply_shape":shape,"battery_power_peak_ratio":power,
                "battery_energy_peak_hours":energy,"perturbation_mode":mode,
                "tiebreak_eps_usd_per_soc_mwh":EPS if mode!="baseline" else 0.,
                "reference_unperturbed_objective_usd":reference,
                "unperturbed_cost_of_candidate_usd":cost,
                "original_objective_gap_usd":gap,
                "original_objective_gap_relative":gap/max(1.,abs(reference)),
                "near_optimal_within_1ppm":bool(gap<=near_tol),
                "strict_original_objective_match_0_03usd":bool(abs(gap)<=.03),
                "charged_mwh":charge,"discharged_mwh":discharge,
                "soc_bound_hours":int(trace.soc_at_energy_limit.sum()),
                "charge_bound_hours":int(trace.charge_at_power_limit.sum()),
                "discharge_bound_hours":int(trace.discharge_at_power_limit.sum()),
                "mean_soc_mwh":float(soc.mean()),
                "max_abs_hourly_soc_change_mwh":float(np.max(np.abs(soc-original_soc))),
                "sum_abs_hourly_soc_change_mwh":float(np.sum(np.abs(soc-original_soc))),
                "soc_bound_hours_delta":int(trace.soc_at_energy_limit.sum())-basis["soc_bound_hours"],
                "charge_bound_hours_delta":int(trace.charge_at_power_limit.sum())-basis["charge_bound_hours"],
                "discharge_bound_hours_delta":int(trace.discharge_at_power_limit.sum())-basis["discharge_bound_hours"],
                "charged_mwh_delta":charge-basis["charged_mwh"],
                "discharged_mwh_delta":discharge-basis["discharged_mwh"],
                "cyclic_soc_verified":bool(result["cyclic_SOC_0_to_0_verified"])})
    out=pd.DataFrame(rows)
    if len(out)!=16 or out.duplicated(["synthetic_supply_shape","battery_power_peak_ratio",
                                       "battery_energy_peak_hours","perturbation_mode"]).any():
        raise ValueError("Expected four probes times four modes")
    if not out.near_optimal_within_1ppm.all() or not out.cyclic_soc_verified.all():
        raise ValueError("Near-optimal or cycle certificate missing")
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--group",type=int,choices=(1,7),required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    out=evaluate(pd.read_csv(a.hourly,compression="infer"),pd.read_csv(a.original),a.group)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.out_dir/"paper_s_soc_tiebreak_schedule_sensitivity.csv",index=False,float_format="%.12g")
    manifest={"status":"PAPER_S_NEAR_OPTIMAL_SCHEDULE_PERTURBATION_CHECK_PASS",
        "source_shape_group":a.group,"probes":4,"objective_modes":len(MODES),
        "source_hour_axis":"8760 original LocalHourID; not certified UTC",
        "epsilon_usd_per_soc_mwh":EPS,
        "within_one_part_per_million_original_lp_objective":True,
        "exact_alternative_optima_proven":False,
        "not_western_grid_or_storage_capex":True}
    (a.out_dir/"paper_s_soc_tiebreak_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(out[["synthetic_supply_shape","battery_power_peak_ratio","battery_energy_peak_hours",
               "perturbation_mode","original_objective_gap_usd",
               "sum_abs_hourly_soc_change_mwh","soc_bound_hours_delta",
               "charge_bound_hours_delta","discharge_bound_hours_delta"]].to_string(index=False))
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":main()
