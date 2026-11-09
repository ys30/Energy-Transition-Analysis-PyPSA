"""Orthogonal MW / MWh capacity screen on seven verified source-demand chronologies.

Power ratios {0.125, 0.25, 0.5} and energy capacities {0.5, 1, 2}
are *independent* fractions of source peak MW and peak-MWh, respectively.
Baseline points (power=.25, energy=1 or 2) must recover archived 4h/8h LPs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone, SHAPES
from .efs_ordinal_storage_sensitivity import shape_cf

POWERS=(.125,.25,.50)
ENERGIES=(.50,1.,2.)
COMPARED={"storage_discharge_to_load_mwh","firm_generation_mwh",
          "unused_renewable_mwh","storage_charge_input_mwh"}
def evaluate(hourly, original):
    ref=hourly[(hourly.synthetic_supply_shape=="flat_50pct")&
               (hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(ref)!=8760 or not np.array_equal(ref.local_hour_id,np.arange(1,8761)):
        raise ValueError("Original 8760 source-hour population is missing")
    if len(original)!=9 or len(ref[["planning_year","state","reeds_zone"]].drop_duplicates())!=1:
        raise ValueError("Missing unique archived source shape identity")
    state=str(ref.state.iloc[0]);zone=str(ref.reeds_zone.iloc[0])
    year=int(ref.planning_year.iloc[0]);d=ref.demand_mwh.to_numpy(dtype=float)
    if year!=2030 or not np.isfinite(d).all() or d.max()<=0 or (d<0).any():
        raise ValueError("Invalid preselected source demand")
    rows=[]
    for shape in SHAPES:
        cf=shape_cf(np.arange(1,8761),shape)
        for p in POWERS:
            for e in ENERGIES:
                result=solve_zone(d,cf,4,battery_power_peak_ratio=p,
                                  storage_energy_peak_hours=e)
                if p==.25 and e in (1.,2.):
                    duration=int(e/.25)
                    old=hourly[(hourly.synthetic_supply_shape==shape)&
                               (hourly.battery_duration_h==duration)]
                    oldmeta=original[(original.synthetic_supply_shape==shape)&
                                     (original.battery_duration_h==duration)]
                    if len(old)!=8760 or len(oldmeta)!=1:
                        raise ValueError("Archived baseline 4h/8h missing")
                    for col in COMPARED:
                        if not np.isclose(result[col],float(old[col].sum()),rtol=1e-9,atol=.03):
                            raise ValueError("Independent sizing differs from accepted LP: "+col)
                    if not np.isclose(result["objective_illustrative_variable_usd"],
                                      float(oldmeta.annual_toy_cost_usd.iloc[0]),rtol=1e-9,atol=.03):
                        raise ValueError("Baseline objective mismatch")
                rows.append({"planning_year":year,"state":state,"reeds_zone":zone,
                    "synthetic_supply_shape":shape,"battery_power_peak_ratio":p,
                    "battery_energy_peak_hours":e,
                    "implied_hours_at_rated_power":e/p,
                    "source_hours":result["source_hours"],
                    "solver_status":result["solver_status"],
                    "storage_power_mw":result["storage_power_mw"],
                    "storage_capacity_mwh":result["storage_capacity_mwh"],
                    "storage_charge_input_mwh":result["storage_charge_input_mwh"],
                    "storage_discharge_to_load_mwh":result["storage_discharge_to_load_mwh"],
                    "firm_generation_mwh":result["firm_generation_mwh"],
                    "unused_renewable_mwh":result["unused_renewable_mwh"],
                    "objective_illustrative_variable_usd":result["objective_illustrative_variable_usd"],
                    "storage_terminal_soc_mwh":result["storage_terminal_soc_mwh"],
                    "max_equality_residual_mwh":result["max_equality_residual_mwh"]})
    out=pd.DataFrame(rows)
    if len(out)!=27 or out.duplicated(["synthetic_supply_shape","battery_power_peak_ratio","battery_energy_peak_hours"]).any():
        raise ValueError("Expected 27 independently sized full-year LP cases")
    if not out.solver_status.eq("optimal").all() or out.max_equality_residual_mwh.max()>1e-5 or out.storage_terminal_soc_mwh.abs().max()>1e-5:
        raise ValueError("LP feasibility/cyclic terminal gate failed")
    return out

def increments(cases):
    if len(cases)!=27:raise ValueError("Expected 27 sized cases")
    records=[]
    for shape,g in cases.groupby("synthetic_supply_shape"):
        for power in POWERS:
            for low,high in ((.5,1.),(1.,2.)):
                a=g[(g.battery_power_peak_ratio==power)&(g.battery_energy_peak_hours==low)]
                b=g[(g.battery_power_peak_ratio==power)&(g.battery_energy_peak_hours==high)]
                if len(a)!=1 or len(b)!=1:raise ValueError("Missing energy increment")
                a=a.iloc[0];b=b.iloc[0]
                records.append({"synthetic_supply_shape":shape,"axis":"energy_at_fixed_power",
                    "held_constant":power,"from_level":low,"to_level":high,
                    "added_discharge_mwh":b.storage_discharge_to_load_mwh-a.storage_discharge_to_load_mwh,
                    "avoided_firm_mwh":a.firm_generation_mwh-b.firm_generation_mwh,
                    "avoided_unused_mwh":a.unused_renewable_mwh-b.unused_renewable_mwh,
                    "toy_objective_reduction_usd":a.objective_illustrative_variable_usd-b.objective_illustrative_variable_usd})
        for energy in ENERGIES:
            for low,high in ((.125,.25),(.25,.5)):
                a=g[(g.battery_energy_peak_hours==energy)&(g.battery_power_peak_ratio==low)]
                b=g[(g.battery_energy_peak_hours==energy)&(g.battery_power_peak_ratio==high)]
                if len(a)!=1 or len(b)!=1:raise ValueError("Missing power increment")
                a=a.iloc[0];b=b.iloc[0]
                records.append({"synthetic_supply_shape":shape,"axis":"power_at_fixed_energy",
                    "held_constant":energy,"from_level":low,"to_level":high,
                    "added_discharge_mwh":b.storage_discharge_to_load_mwh-a.storage_discharge_to_load_mwh,
                    "avoided_firm_mwh":a.firm_generation_mwh-b.firm_generation_mwh,
                    "avoided_unused_mwh":a.unused_renewable_mwh-b.unused_renewable_mwh,
                    "toy_objective_reduction_usd":a.objective_illustrative_variable_usd-b.objective_illustrative_variable_usd})
    result=pd.DataFrame(records)
    if len(result)!=36:raise ValueError("Expected 36 one-axis contrasts")
    expected=90*result.avoided_firm_mwh-5*result.avoided_unused_mwh
    if not np.allclose(result.toy_objective_reduction_usd,expected,rtol=1e-9,atol=.1):
        raise ValueError("Exact objective decomposition fails")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--original-hourly",required=True,type=Path)
    ap.add_argument("--original-metrics",required=True,type=Path)
    ap.add_argument("--out-dir",required=True,type=Path)
    a=ap.parse_args()
    d=evaluate(pd.read_csv(a.original_hourly,compression="infer"),pd.read_csv(a.original_metrics))
    contrasts=increments(d)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    d.to_csv(a.out_dir/"mw_mwh_27_lp.csv",index=False)
    contrasts.to_csv(a.out_dir/"mw_mwh_36_one_axis_contrasts.csv",index=False)
    manifest={"status":"ORIGINAL_SOURCE_ORTHOGONAL_MW_MWH_LP_VERIFIED",
        "source_zone":str(d.state.iloc[0])+" "+str(d.reeds_zone.iloc[0]),
        "lp_cases":len(d),"single_axis_contrasts":len(contrasts),
        "power_peak_ratios":list(POWERS),"energy_peak_hours":list(ENERGIES),
        "historical_baseline_comparisons_reproduced":6,"real_resource_data":False,
        "battery_capex_included":False,"physical_utc_certified":False}
    (a.out_dir/"mw_mwh_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()
