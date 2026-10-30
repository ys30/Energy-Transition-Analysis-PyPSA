"""Compare existing illustrative supply against added observed EIA-930 solar/wind injections.

Observed BA fuel generation is signed net MWh per 1-hour interval. This
experiment does not claim a historical supply reconciliation: the illustrative
55-GW firm generator is explicitly treated as non-wind/non-solar residual supply.
"""
from pathlib import Path
import argparse
import json
import pandas as pd
from .chronological_storage_pilot import solve_window
from .seasonal_storage_sensitivity import SEASON_WEEKS

def prepare_injections(frame, bas=("CISO","BPAT")):
    required={"season","period","respondent","fueltype","reported_signed_net_mwh"}
    if required-set(frame):
        raise ValueError("Missing observed renewable fields: "+str(sorted(required-set(frame))))
    x=frame.copy()
    x["period"]=pd.to_datetime(x["period"],utc=True)
    x=x[x["respondent"].isin(bas)]
    if x.duplicated(["season","period","respondent","fueltype"]).any():
        raise ValueError("Duplicate season/BA/fuel/hour generation")
    if x["reported_signed_net_mwh"].isna().any():
        raise ValueError("Observed renewable values missing")
    expected={(ba,f) for ba in bas for f in ("SUN","WND")}
    series={}
    for season,start in SEASON_WEEKS.items():
        sub=x[x.season.eq(season)]
        counts=sub.groupby("period").apply(
            lambda part:set(zip(part.respondent,part.fueltype))==expected,
            include_groups=False)
        hours=pd.date_range(pd.Timestamp(start),periods=168,freq="h")
        if not counts.reindex(hours,fill_value=False).all() or len(counts)!=168:
            raise ValueError(f"Missing or unexpected renewable BA/fuel hourly records: {season}")
        series[season]=sub.groupby("period")["reported_signed_net_mwh"].sum().reindex(hours).astype(float)
    return series

def compare(hourly,renewables,output):
    output=Path(output);demand=hourly.copy()
    demand["period"]=pd.to_datetime(demand.period,utc=True)
    injections=prepare_injections(renewables)
    rows=[]
    for season,start in SEASON_WEEKS.items():
        begin=pd.Timestamp(start)
        window=demand[demand.period.ge(begin)&demand.period.lt(begin+pd.Timedelta(hours=168))]
        for scenario,injection in (("assumed_supply_only",None),
                                   ("observed_wind_solar_plus_assumed_residual_supply",injections[season])):
            result=solve_window(window,output/season/scenario,duration_h=4.,
                                require_activity=False,renewable_net_mw=injection)
            rows.append({
                "season":season,"scenario":scenario,
                "observed_signed_wind_solar_mwh":result["observed_signed_renewable_mwh"],
                "unserved_with_battery_mwh":result["unserved_mwh"],
                "unserved_without_battery_mwh":result["unserved_mwh_without_storage"],
                "battery_charge_mwh":result["battery_charge_mwh"],
                "battery_discharge_mwh":result["battery_discharge_mwh"],
                "assumed_operating_savings_usd":result["operating_savings_usd_assumed"],
                "max_soc_error_mwh":result["max_storage_conservation_error_mwh"],
            })
    out=pd.DataFrame(rows)
    output.mkdir(parents=True,exist_ok=True)
    out.to_csv(output/"observed_renewable_storage_comparison.csv",index=False)
    (output/"provenance.json").write_text(json.dumps({
       "data":"EIA-930 2024 hourly demand and signed wind/solar net generation for CISO/BPAT",
       "design":"Four matched seasonal weeks, storage 1GW/4GWh, identical firm and peaker assumptions in both variants",
       "renewable_handling":"fixed signed load offset, not weather-dependent renewable availability",
       "interpretation":"Scenario comparison, not validated historical generation balance. Assumed firm supply is defined as non-wind/non-solar residual capacity; actual composition and physical dispatch not established. No transmission.",
       "avoid":"Never add observed solar/wind generation to a historical dispatch that already includes those sources; this pilot supply only includes assumed firm/peaker generators."
    },indent=2))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",type=Path,required=True)
    p.add_argument("--renewables",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/observed_renewable_storage"))
    a=p.parse_args()
    print(compare(pd.read_csv(a.demand),pd.read_csv(a.renewables),a.output).to_string(index=False))
if __name__=="__main__":main()
