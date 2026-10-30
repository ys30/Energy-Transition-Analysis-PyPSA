"""Compare 2/4/6/8-hour batteries on one identical observed-demand week.

All cases use the same 1-GW battery power rating, 168 hourly EIA-930
observations, generation capacities and operating costs. Excludes battery capex.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from .chronological_storage_pilot import solve_window

DURATIONS=(2.,4.,6.,8.)

def run_sensitivity(hourly,output,durations=DURATIONS):
    if len(set(durations))!=len(durations) or any(d<=0 for d in durations):
        raise ValueError("Storage durations must be positive and unique")
    output=Path(output)
    rows=[]
    for duration in durations:
        path=output/f"duration_{int(duration)}h"
        result=solve_window(hourly,path,duration_h=duration,require_activity=False)
        rows.append({
            "duration_h":duration,
            "battery_power_mw":result["battery_mw_assumed"],
            "battery_energy_mwh":result["capacity_mwh_assumed"],
            "charge_mwh":result["battery_charge_mwh"],
            "discharge_mwh":result["battery_discharge_mwh"],
            "peaker_with_storage_mwh":result["peaker_generation_mwh"],
            "peaker_without_storage_mwh":result["peaker_generation_mwh_without_storage"],
            "operating_cost_with_storage_usd":result["objective_usd_with_storage_assumed"],
            "operating_cost_without_storage_usd":result["objective_usd_without_storage_assumed"],
            "operating_savings_usd":result["operating_savings_usd_assumed"],
            "unserved_mwh":result["unserved_mwh"],
            "max_soc_error_mwh":result["max_storage_conservation_error_mwh"]
        })
    df=pd.DataFrame(rows)
    if df.operating_cost_without_storage_usd.max()-df.operating_cost_without_storage_usd.min()>0.01:
        raise ValueError("No-storage baseline changed across sensitivity cases")
    if df.operating_savings_usd.diff().iloc[1:].lt(-.01).any():
        raise ValueError("Increasing optional battery energy capacity worsened minimized cost")
    output.mkdir(parents=True,exist_ok=True)
    df.to_csv(output/"storage_duration_sensitivity.csv",index=False)
    (output/"sensitivity_provenance.json").write_text(json.dumps({
        "study":"168-hour EIA-930 demand battery energy-duration sensitivity",
        "durations_h":list(durations),
        "battery_power_mw":1000,
        "battery_investment_cost_included":False,
        "note":"All supply and electricity costs are assumed. Savings are 168-hour modeled operating differences, not annual savings or lifecycle net benefit."
    },indent=2))
    return df

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--start",default="2024-01-08T00:00:00Z")
    p.add_argument("--output",type=Path,default=Path("outputs/storage_duration_sensitivity"))
    a=p.parse_args()
    frame=pd.read_csv(a.hourly)
    frame["period"]=pd.to_datetime(frame.period,utc=True)
    start=pd.Timestamp(a.start)
    if start.tzinfo is None:start=start.tz_localize("UTC")
    start=start.tz_convert("UTC")
    selected=frame[frame.period.ge(start)&frame.period.lt(start+pd.Timedelta(hours=168))]
    print(run_sensitivity(selected,a.output).to_string(index=False))
if __name__=="__main__":main()
