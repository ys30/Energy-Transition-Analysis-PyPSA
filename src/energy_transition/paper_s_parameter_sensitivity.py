"""Seven source-hour demand-shape groups: LP power, efficiency and price stress tests.

Every job restores a source-archive-matched 8760-hour EFS demand chronology,
and baseline 4/8h cases must reproduce that group's accepted historical LP.
Variants affect one parameter at a time; no real weather or capex is modeled.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .efs_cyclic_storage_lp import solve_zone,SHAPES
from .efs_ordinal_storage_sensitivity import shape_cf

SCENARIOS={
    "baseline":(.25,.90,90.),
    "half_power":(.125,.90,90.),
    "double_power":(.50,.90,90.),
    "rte_80pct":(.25,.80,90.),
    "rte_95pct":(.25,.95,90.),
    "firm_60usd":(.25,.90,60.),
    "firm_150usd":(.25,.90,150.),
}
DURATIONS=(4,8)
ARCHIVED_COLUMNS={
    "storage_discharge_to_load_mwh":"storage_discharge_to_load_mwh",
    "storage_charge_input_mwh":"storage_charge_input_mwh",
    "firm_generation_mwh":"firm_generation_mwh",
    "unused_renewable_mwh":"unused_renewable_mwh",
    "objective_illustrative_variable_usd":"annual_toy_cost_usd",
}
def evaluate(source_hourly,original_cases):
    source=source_hourly.loc[(source_hourly.synthetic_supply_shape=="flat_50pct")&
                             (source_hourly.battery_duration_h==0)].sort_values("local_hour_id")
    if len(source)!=8760 or not np.array_equal(source.local_hour_id.to_numpy(),np.arange(1,8761)):
        raise ValueError("Incomplete original 8760 source hours")
    if len(original_cases)!=9 or source[["planning_year","state","reeds_zone"]].drop_duplicates().shape[0]!=1:
        raise ValueError("Bad original zone identity or baseline nine cases")
    if set(original_cases.synthetic_supply_shape)!=set(SHAPES):
        raise ValueError("Original supply shape mismatch")
    year=int(source.planning_year.iloc[0])
    state=str(source.state.iloc[0]);zone=str(source.reeds_zone.iloc[0])
    load=source.demand_mwh.to_numpy(dtype=float)
    if year!=2030 or not np.isfinite(load).all() or load.max()<=0 or (load<0).any():
        raise ValueError("Invalid pre-selected source demand")
    records=[]
    for shape in SHAPES:
        cf=shape_cf(np.arange(1,8761),shape)
        for label,(power,rte,firm_cost) in SCENARIOS.items():
            for duration in DURATIONS:
                result=solve_zone(load,cf,duration,battery_power_peak_ratio=power,
                                  roundtrip_efficiency=rte,firm_unit_cost=firm_cost)
                if label=="baseline":
                    original=original_cases[(original_cases.synthetic_supply_shape==shape)&
                                            (original_cases.battery_duration_h==duration)]
                    if len(original)!=1:raise ValueError("Missing original baseline case")
                    for key,source_key in ARCHIVED_COLUMNS.items():
                        if not np.isclose(result[key],float(original.iloc[0][source_key]),
                                          atol=.03,rtol=1e-9):
                            raise ValueError("Changed original LP baseline: "+key)
                records.append({"planning_year":year,"state":state,"reeds_zone":zone,
                    "synthetic_supply_shape":shape,"scenario":label,
                    "battery_duration_h":duration,"storage_power_peak_ratio":power,
                    "roundtrip_efficiency":rte,"renewable_unit_cost":5.,
                    "firm_unit_cost":firm_cost,
                    **{k:result[k] for k in ("source_hours","solver_status","demand_mwh",
                        "renewable_available_mwh","storage_charge_input_mwh",
                        "storage_discharge_to_load_mwh","firm_generation_mwh",
                        "unused_renewable_mwh","storage_terminal_soc_mwh",
                        "objective_illustrative_variable_usd","storage_capacity_mwh",
                        "storage_power_mw","max_equality_residual_mwh")}})
    df=pd.DataFrame(records)
    if len(df)!=42 or df.duplicated(["scenario","synthetic_supply_shape","battery_duration_h"]).any():
        raise ValueError("Incomplete sensitivity LP population")
    if not df.solver_status.eq("optimal").all() or not df.source_hours.eq(8760).all():
        raise ValueError("Non-optimal or incomplete LP")
    if df.storage_terminal_soc_mwh.abs().max()>1e-5 or df.max_equality_residual_mwh.max()>1e-5:
        raise ValueError("Source LP feasibility gate failed")
    return df

def summarize(cases):
    if len(cases)!=42:raise ValueError("Need complete 42 LP cases")
    rows=[]
    for (shape,scenario),frame in cases.groupby(["synthetic_supply_shape","scenario"]):
        if set(frame.battery_duration_h)!={4,8}:raise ValueError("Missing duration")
        g=frame.set_index("battery_duration_h")
        a=g.loc[4];b=g.loc[8]
        rows.append({"state":a.state,"reeds_zone":a.reeds_zone,
            "synthetic_supply_shape":shape,"scenario":scenario,
            "power_ratio":a.storage_power_peak_ratio,
            "roundtrip_efficiency":a.roundtrip_efficiency,
            "firm_unit_cost":a.firm_unit_cost,
            "additional_discharge_mwh":b.storage_discharge_to_load_mwh-a.storage_discharge_to_load_mwh,
            "avoided_firm_mwh":a.firm_generation_mwh-b.firm_generation_mwh,
            "avoided_unused_mwh":a.unused_renewable_mwh-b.unused_renewable_mwh,
            "toy_objective_reduction_usd":a.objective_illustrative_variable_usd-b.objective_illustrative_variable_usd})
    result=pd.DataFrame(rows)
    if len(result)!=21:raise ValueError("Expected 21 shape-scenario comparisons")
    predicted=result.firm_unit_cost*result.avoided_firm_mwh-5*result.avoided_unused_mwh
    if not np.allclose(predicted,result.toy_objective_reduction_usd,rtol=1e-9,atol=.1):
        raise ValueError("Cost identity fails in parameter stress test")
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--original-hourly",type=Path,required=True)
    p.add_argument("--original-metrics",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    cases=evaluate(pd.read_csv(a.original_hourly,compression="infer"),pd.read_csv(a.original_metrics))
    comparisons=summarize(cases)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    cases.to_csv(a.out_dir/"paper_s_parameter_sensitivity_42_lp.csv",index=False)
    comparisons.to_csv(a.out_dir/"paper_s_parameter_sensitivity_21_comparisons.csv",index=False)
    manifest={"status":"SOURCE_ARCHIVED_SEVEN_SHAPE_PARAMETER_LP_VALIDATED",
        "zone":cases.state.iloc[0]+" "+cases.reeds_zone.iloc[0],
        "source_ordinal_hours":8760,"full_year_lp_cases":42,
        "parameter_cases":list(SCENARIOS),
        "archive_baseline_all_shapes_verified":True,
        "source_utc_clock_certified":False,
        "real_renewable_profiles":False,"battery_capex_included":False}
    (a.out_dir/"paper_s_parameter_sensitivity_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    print(comparisons.to_string(index=False))
if __name__=="__main__":main()
