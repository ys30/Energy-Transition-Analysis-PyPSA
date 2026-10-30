"""Full 8784-hour storage scenarios with explicitly imputed EIA wind/solar gaps.

Runs three separate scenarios and matched no-battery counterfactuals.
The official-data annual completeness gate remains blocked.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .chronological_storage_pilot import solve_window

def compare_annual(demand,scenario_frame,output):
    out=Path(output);d=demand.copy();d["period"]=pd.to_datetime(d.period,utc=True)
    expected=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    if len(expected)!=8784:raise RuntimeError("2024 leap year hour count mismatch")
    summaries=[]
    for method,part in scenario_frame.groupby("method",sort=True):
        x=part.copy();x["period"]=pd.to_datetime(x.period,utc=True)
        if x.duplicated(["period","respondent","fueltype"]).any():
            raise ValueError("Duplicate BA fuel hour")
        required={"CISO","BPAT"}
        if set(x.respondent)!=required or set(x.fueltype)!={"SUN","WND"}:
            raise ValueError("Missing expected BA/fuel")
        counts=x.groupby("period").size().reindex(expected)
        if counts.isna().any() or not counts.eq(4).all() or len(x)!=4*8784:
            raise ValueError("Incomplete annual filled renewable grid")
        if x.value_mwh.isna().any():raise ValueError("Unfilled renewable observations")
        injection=x.groupby("period").value_mwh.sum().reindex(expected)
        result=solve_window(d,out/method,renewable_net_mw=injection,
            expected_hours=8784,require_activity=False,duration_h=4.)
        saved=result["operating_savings_usd_assumed"]
        avoided=result["unserved_mwh_without_storage"]-result["unserved_mwh"]
        summaries.append({
          "scenario":method,"input_classification":"scenario_imputed_not_complete_official",
          "imputed_ba_fuel_hours":int(x.is_imputed.sum()),
          "annual_signed_wind_solar_mwh":float(injection.sum()),
          "battery_charge_mwh":result["battery_charge_mwh"],
          "battery_discharge_mwh":result["battery_discharge_mwh"],
          "unserved_with_battery_mwh":result["unserved_mwh"],
          "unserved_without_battery_mwh":result["unserved_mwh_without_storage"],
          "avoided_unserved_mwh":avoided,
          "avoided_unserved_penalty_usd":avoided*result["assumed_voll_usd_per_mwh"],
          "other_dispatch_savings_usd":saved-avoided*result["assumed_voll_usd_per_mwh"],
          "operating_savings_usd_assumed":saved,
          "peaker_avoided_mwh":result["peaker_generation_mwh_without_storage"]-result["peaker_generation_mwh"],
          "firm_extra_mwh":result["firm_generation_mwh_with_storage"]-result["firm_generation_mwh_without_storage"],
          "max_soc_error_mwh":result["max_storage_conservation_error_mwh"],
        })
    if set(t["scenario"] for t in summaries)!={"linear","same_hour_nearby","zero_bound"}:
        raise ValueError("Not all three missing-value scenarios solved")
    table=pd.DataFrame(summaries)
    out.mkdir(parents=True,exist_ok=True)
    table.to_csv(out/"annual_2024_storage_fill_sensitivity.csv",index=False)
    (out/"annual_sensitivity_provenance.json").write_text(json.dumps({
      "classification":"hypothetical_missing_value_sensitivity_not_full_observed_2024",
      "run_hours":8784,"battery":"1GW/4GWh assumed","generation":"55GW firm plus 20GW peaker assumed",
      "voll_usd_per_mwh":10000,
      "caveat":"Not a calibrated annual value or investment NPV. 55GW supply assumptions, no transmission, battery cost or degradation. Official observed full-year QC remains blocked."
    },indent=2))
    return table

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",type=Path,required=True)
    p.add_argument("--scenarios",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    print(compare_annual(pd.read_csv(a.demand),pd.read_csv(a.scenarios),a.output).to_string(index=False))
if __name__=="__main__":main()
