"""Conditional annual battery robustness tests, never a verified historical NPV."""
import argparse,json
from pathlib import Path
import pandas as pd
from .chronological_storage_pilot import solve_window

CASES=(
 ("reference",55000.,20000.,10000.,False),
 ("lower_voll",55000.,20000.,1000.,False),
 ("more_supply",65000.,30000.,10000.,False),
 ("cyclic_soc",55000.,20000.,10000.,True),
)

def check_grid(demand,scenario):
    d=demand.copy();d["period"]=pd.to_datetime(d.period,utc=True)
    s=scenario.copy();s["period"]=pd.to_datetime(s.period,utc=True)
    s=s[s.method.eq("linear")]
    expected=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    if s.duplicated(["period","respondent","fueltype"]).any():raise ValueError("Duplicate filled observations")
    if len(s)!=4*len(expected) or s.groupby("period").size().reindex(expected).ne(4).any():
        raise ValueError("Incomplete wind/solar input")
    if s.value_mwh.isna().any() or int(s.is_imputed.sum())!=55:
        raise ValueError("Unexpected imputed input count")
    return d,s.groupby("period").value_mwh.sum().reindex(expected)

def run(demand,scenario,output,solver=solve_window):
    output=Path(output)
    d,renewables=check_grid(demand,scenario)
    records=[]
    for name,firm,peaker,voll,cyclic in CASES:
        result=solver(d,output/name,renewable_net_mw=renewables,
            expected_hours=8784,require_activity=False,duration_h=4.,
            generation_mw=firm,peaker_mw=peaker,voll_usd_per_mwh=voll,cyclic_soc=cyclic)
        avoided=result["unserved_mwh_without_storage"]-result["unserved_mwh"]
        savings=result["operating_savings_usd_assumed"]
        records.append({"case":name,"firm_mw_assumed":firm,"peaker_mw_assumed":peaker,
          "voll_usd_per_mwh_assumed":voll,"cyclic_soc":cyclic,
          "unserved_with_storage_mwh":result["unserved_mwh"],
          "unserved_without_storage_mwh":result["unserved_mwh_without_storage"],
          "avoided_unserved_mwh":avoided,
          "shortage_penalty_component_usd":avoided*voll,
          "other_dispatch_component_usd":savings-avoided*voll,
          "operating_savings_usd":savings,
          "battery_discharge_mwh":result["battery_discharge_mwh"],
          "final_soc_mwh":result["final_soc_mwh"],
          "max_soc_conservation_residual_mwh":result["max_storage_conservation_error_mwh"]})
    output.mkdir(parents=True,exist_ok=True)
    frame=pd.DataFrame(records)
    frame.to_csv(output/"annual_robustness_comparison.csv",index=False)
    (output/"provenance.json").write_text(json.dumps({
      "source":"2024 EIA-930 demand and renewable signed net generation; 55 explicitly imputed records via linear interpolation",
      "type":"conditional_illustrative_annual_optimization_not_historical_calibration",
      "caution":"VOLL, supply and terminal SOC scenarios are hypothetical; no annual return or actual market revenue inference. Battery capex/degradation and transmission omitted."
    },indent=2))
    return frame

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",type=Path,required=True)
    p.add_argument("--scenarios",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(run(pd.read_csv(a.demand),pd.read_csv(a.scenarios),a.output).to_string(index=False))
if __name__=="__main__":main()
