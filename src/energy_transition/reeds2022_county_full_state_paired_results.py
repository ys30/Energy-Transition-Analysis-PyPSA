"""Exact paired summary of authenticated-source hypothetical installed-capacity LP.

Reads canonical 48-case source CSV, does no new solve and exports scoped
diagnostics. The implied dollars are *illustrative operating objective only*
without storage capex, network, resource build-out, or reliability.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

def evaluate(path,out):
    df=pd.read_csv(path)
    expected=4*3*2*2
    if len(df)!=expected or df.duplicated(
            ["state","demand_model_year","hour_approximation","battery_duration_h"]).any():
        raise ValueError("Expected exactly 48 distinct documented scenarios")
    keys=["state","demand_model_year","hour_approximation"]
    base=df[df.battery_duration_h.eq(0)].set_index(keys)
    storage=df[df.battery_duration_h.eq(4)].set_index(keys)
    if len(base)!=24 or len(storage)!=24 or not base.index.equals(storage.index):
        raise ValueError("Missing exact paired 0h/4h LP results")
    fields=["objective_illustrative_variable_usd","firm_generation_mwh",
            "unused_renewable_mwh","storage_discharge_to_load_mwh"]
    for field in fields:
        if not np.isfinite(df[field]).all():
            raise ValueError("Nonfinite underlying source LP summary")
    result=base[fields].add_suffix("_0h").join(storage[fields].add_suffix("_4h"))
    result["objective_savings_usd"]=(
        result["objective_illustrative_variable_usd_0h"]-
        result["objective_illustrative_variable_usd_4h"])
    result["objective_savings_pct"]=100*result.objective_savings_usd/result.objective_illustrative_variable_usd_0h
    result["avoided_firm_mwh"]=result.firm_generation_mwh_0h-result.firm_generation_mwh_4h
    result["avoided_curtailment_mwh"]=result.unused_renewable_mwh_0h-result.unused_renewable_mwh_4h
    if (result.objective_savings_usd < -.05).any() or (result.avoided_firm_mwh < -.05).any():
        raise ValueError("Unexpected storage-optimal-cost increase or increased firm generation")
    result=result.reset_index()
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    result.to_csv(out/"paper_s_reeds2022_county_full_state_0h_4h_exact_paired.csv",index=False)
    end=result[result.hour_approximation.eq("end_instant_hold")].set_index(["state","demand_model_year"])
    trap=result[result.hour_approximation.eq("trapezoid_with_first_endpoint")].set_index(["state","demand_model_year"])
    if len(end)!=12 or len(trap)!=12 or not end.index.equals(trap.index):
        raise ValueError("Incorrect matching physical-integration sensitivity")
    comparison=pd.DataFrame({
        "state":[x[0] for x in end.index],
        "demand_model_year":[x[1] for x in end.index],
        "endpoint_storage_savings_usd":end.objective_savings_usd.to_numpy(),
        "trapezoid_storage_savings_usd":trap.objective_savings_usd.to_numpy(),
        "trapezoid_minus_endpoint_savings_usd":
            trap.objective_savings_usd.to_numpy()-end.objective_savings_usd.to_numpy(),
        "endpoint_storage_savings_pct":end.objective_savings_pct.to_numpy(),
        "trapezoid_storage_savings_pct":trap.objective_savings_pct.to_numpy(),
    })
    comparison.to_csv(out/"paper_s_reeds2022_county_full_state_12_sensitivity_comparisons.csv",index=False)
    report={"status":"REEDS2022_COUNTY_SOURCE_HYPOTHETICAL_LP_PAIRED_RESULTS_VERIFIED",
            "source_original_LP_run_id":42965036275,
            "paired_0h_4h_cases":len(result),
            "hour_assumption_sensitivity_pairs":len(comparison),
            "claim_scope":"illustrative single-state copperplate objective, no build capex",
            "actual_buildout_known":False,"hourly_generation_integration_certified":False,
            "network_or_adequacy_certified":False,
            "fixed_hour_zero_boundary_mode":"endpoint_fallback_not_cyclic_wrap"}
    (out/"paper_s_reeds2022_county_full_state_exact_paired_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(comparison.to_string(index=False,float_format=lambda x:f"{x:.6f}"))
    print("REEDS2022_COUNTY_SOURCE_24_PAIRED_OPTIMAL_OBJECTIVE_RESULTS_PASS")
    return comparison

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    evaluate(a.source,a.out)

if __name__=="__main__":
    main()
