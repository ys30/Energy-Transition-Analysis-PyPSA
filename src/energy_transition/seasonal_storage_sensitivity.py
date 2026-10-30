"""Multi-season 2024 observed-demand storage sensitivity, with no annual extrapolation."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
from .storage_duration_sensitivity import run_sensitivity

SEASON_WEEKS = {
    "winter": "2024-01-08T00:00:00Z",
    "spring": "2024-04-08T00:00:00Z",
    "summer": "2024-07-08T00:00:00Z",
    "autumn": "2024-10-07T00:00:00Z",
}

def compare_seasons(hourly, output, weeks=SEASON_WEEKS):
    output=Path(output)
    source=hourly.copy()
    source["period"]=pd.to_datetime(source["period"],utc=True)
    all_results=[]
    for season,start_string in weeks.items():
        start=pd.Timestamp(start_string)
        window=source[source.period.ge(start)&source.period.lt(start+pd.Timedelta(hours=168))]
        results=run_sensitivity(window,output/season)
        results.insert(0,"season",season)
        results.insert(1,"week_start_utc",start_string)
        all_results.append(results)
    combined=pd.concat(all_results,ignore_index=True)
    if combined.groupby("season").duration_h.nunique().ne(4).any():
        raise ValueError("Seasonal sensitivity incomplete")
    combined.to_csv(output/"seasonal_storage_sensitivity.csv",index=False)
    (output/"seasonal_provenance.json").write_text(json.dumps({
       "source":"2024 observed EIA-930 CAISO/BPAT hourly demand, 4 selected contiguous weeks",
       "weeks":weeks,
       "design":"Same assumed generation, battery power, costs, and battery round-trip efficiency for every season",
       "limitation":"Weeks are illustrative, not probabilistically representative; do not annualize savings or infer optimal investment duration."
    },indent=2))
    return combined

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hourly",type=Path,required=True)
    p.add_argument("--output",type=Path,default=Path("outputs/seasonal_storage"))
    a=p.parse_args()
    result=compare_seasons(pd.read_csv(a.hourly),a.output)
    print(result[["season","duration_h","operating_savings_usd","discharge_mwh","unserved_mwh"]].to_string(index=False))

if __name__=="__main__":main()
