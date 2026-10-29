"""Compare solved PyPSA scenarios with independent post-solve QA checks.

Do not confuse modeled dispatch emissions and objective differences with
observed emissions or policy welfare/cost estimates.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

TOL=1e-5

def compare_scenarios(frame: pd.DataFrame) -> pd.DataFrame:
    required={"planning_year","scenario","operational_emissions_tco2_assumed",
              "objective_assumed_usd","co2_cap_tco2","load_mwh","unserved_mwh",
              "new_solar_mw","solver_status"}
    missing=required-set(frame.columns)
    if missing: raise ValueError(f"Missing planning results: {sorted(missing)}")
    if frame.duplicated(["scenario","planning_year"]).any():
        raise ValueError("Duplicate scenario/year results")
    if not frame.solver_status.eq("optimal").all():
        raise ValueError("All compared scenarios must be optimal")
    rows=[]
    for year, subset in frame.groupby("planning_year"):
        ref=subset[subset.scenario.eq("reference")]
        cap=subset[subset.scenario.eq("carbon_cap_50pct")]
        if len(ref)!=1 or len(cap)!=1:
            raise ValueError(f"Missing or duplicate reference/carbon case in {year}")
        ref,cap=ref.iloc[0],cap.iloc[0]
        if not abs(float(ref.load_mwh)-float(cap.load_mwh))<=max(1e-4,float(ref.load_mwh)*TOL):
            raise ValueError(f"Demand differs between reference and carbon cap in {year}")
        budget=float(cap.co2_cap_tco2)
        achieved=float(cap.operational_emissions_tco2_assumed)
        if not budget>=0 or achieved>budget+max(0.01,budget*TOL):
            raise ValueError(f"CO2 cap is not satisfied for {year}")
        removed=float(ref.operational_emissions_tco2_assumed)-achieved
        extra=float(cap.objective_assumed_usd)-float(ref.objective_assumed_usd)
        if removed<=0:
            raise ValueError(f"Carbon cap did not reduce modeled emissions in {year}")
        rows.append({
            "planning_year":int(year),
            "reference_emissions_tco2":float(ref.operational_emissions_tco2_assumed),
            "capped_emissions_tco2":achieved,
            "co2_cap_tco2":budget,
            "model_emissions_reduction_fraction":removed/float(ref.operational_emissions_tco2_assumed),
            "extra_model_objective_usd":extra,
            "model_objective_premium_fraction":extra/float(ref.objective_assumed_usd),
            "incremental_model_usd_per_tco2_avoided":extra/removed,
            "additional_new_solar_mw":float(cap.new_solar_mw)-float(ref.new_solar_mw),
            "reference_unserved_mwh":float(ref.unserved_mwh),
            "capped_unserved_mwh":float(cap.unserved_mwh),
        })
    return pd.DataFrame(rows).sort_values("planning_year")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--summary",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/planning_sensitivity"))
    a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True)
    comparison=compare_scenarios(pd.read_csv(a.summary))
    comparison.to_csv(a.output/"carbon_cap_vs_reference.csv",index=False)
    (a.output/"carbon_comparison_provenance.json").write_text(json.dumps({
        "interpretation":"Model incremental objective cost per modeled operational tonne avoided; NOT social cost of carbon, market carbon price, or real-world abatement cost",
        "model_limits":"Independent representative-year optimization; constant solar/wind availability; no storage, transmission or retirement dynamics"
    },indent=2))
    print(comparison.to_string(index=False))
if __name__=="__main__":main()
