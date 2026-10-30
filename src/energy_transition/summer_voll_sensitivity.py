"""Re-optimize a fixed observed 2024 summer week under alternative shortage penalties.

Value of lost load (VOLL) is an assumption. Savings are objective differences,
not market revenue, realized reliability benefits or battery investment returns.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
from .chronological_storage_pilot import solve_window

VOLLS=(1000.,5000.,10000.,20000.)

def run(hourly,output,volls=VOLLS):
    if len(set(volls))!=len(volls) or any(v<=250 for v in volls):
        raise ValueError("VOLL values must be unique and above assumed peaker marginal cost")
    out=Path(output);rows=[]
    for voll in volls:
        result=solve_window(hourly,out/f"voll_{int(voll)}",duration_h=4.,
                            require_activity=False,voll_usd_per_mwh=voll)
        avoided=result["unserved_mwh_without_storage"]-result["unserved_mwh"]
        penalty_benefit=avoided*voll
        savings=result["operating_savings_usd_assumed"]
        rows.append({"voll_usd_per_mwh":voll,
            "unserved_with_battery_mwh":result["unserved_mwh"],
            "unserved_without_battery_mwh":result["unserved_mwh_without_storage"],
            "avoided_unserved_mwh":avoided,
            "penalty_benefit_usd":penalty_benefit,
            "other_dispatch_savings_usd":savings-penalty_benefit,
            "total_operating_savings_usd":savings,
            "battery_discharge_mwh":result["battery_discharge_mwh"],
            "max_soc_error_mwh":result["max_storage_conservation_error_mwh"]})
    data=pd.DataFrame(rows)
    if (data.avoided_unserved_mwh < -1e-4).any():
        raise ValueError("Battery unexpectedly increased unserved load in this pilot")
    out.mkdir(parents=True,exist_ok=True)
    data.to_csv(out/"summer_voll_sensitivity.csv",index=False)
    (out/"voll_provenance.json").write_text(json.dumps({
        "scenario":"2024 summer 168-hour chronological observed-demand pilot",
        "battery":"1 GW, 4 GWh, assumed 95% charge and discharge efficiencies",
        "volls_usd_per_mwh":list(volls),
        "note":"Each case independently re-optimized. These are assumed shortage penalties, not observed prices or validated outage damage."
    },indent=2))
    return data

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/summer_voll"))
    a=p.parse_args()
    frame=pd.read_csv(a.hourly)
    frame["period"]=pd.to_datetime(frame.period,utc=True)
    start=pd.Timestamp("2024-07-08T00:00:00Z")
    sample=frame[frame.period.ge(start)&frame.period.lt(start+pd.Timedelta(hours=168))]
    print(run(sample,a.output).to_string(index=False))
if __name__=="__main__":main()
