"""Explicit, independently labeled sensitivity fills for missing EIA-930 renewable hours.

Never overwrite official observations, including signed negative values.
These are hypothetical fill strategies, NOT recovered official data.
"""
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd
from .eia930_renewable_missing_inventory import missing_inventory

METHODS=("linear","same_hour_nearby","zero_bound")
def scenarios(frame,year=2024,bas=("CISO","BPAT")):
    data=frame.copy()
    data["period"]=pd.to_datetime(data.period,utc=True)
    if data.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate original BA fuel-hour")
    hours=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    idx=pd.MultiIndex.from_product([hours,bas,("SUN","WND")],names=["period","respondent","fueltype"])
    observed=pd.to_numeric(data.set_index(["period","respondent","fueltype"])["value"].reindex(idx),errors="coerce")
    gap_count=int(observed.isna().sum())
    if gap_count==0:raise ValueError("No missing source records to scenario-fill")
    rows=[];metadata=[]
    for method in METHODS:
        pieces=[]
        for ba in bas:
            for fuel in ("SUN","WND"):
                series=observed.xs((ba,fuel),level=("respondent","fueltype"))
                if method=="linear":
                    fill=series.interpolate(method="time",limit_area="inside")
                elif method=="same_hour_nearby":
                    # ±7-day same UTC clock-hour reference only, excluding absent observations.
                    fill=series.copy()
                    for hour in series.index[series.isna()]:
                        samples=[series.get(hour+pd.Timedelta(days=d),np.nan) for d in (-7,7)]
                        valid=[float(z) for z in samples if pd.notna(z)]
                        if valid:fill.loc[hour]=sum(valid)/len(valid)
                else:
                    fill=series.fillna(0.)
                if fill.isna().any():
                    raise ValueError(f"Unfillable gap: {method}, {ba}, {fuel}")
                for hour in series.index:
                    old=series.loc[hour];new=float(fill.loc[hour])
                    if pd.notna(old) and new!=float(old):
                        raise ValueError("Original observation changed")
                    pieces.append({"period":hour,"respondent":ba,"fueltype":fuel,
                       "value_mwh":new,"is_imputed":bool(pd.isna(old)),
                       "method":method,"source":"official_eia930" if pd.notna(old) else "hypothetical_sensitivity"})
        result=pd.DataFrame(pieces)
        if len(result)!=len(idx) or int(result.is_imputed.sum())!=gap_count:
            raise ValueError("Scenario missing count inconsistent")
        metadata.append({"method":method,"imputed_ba_fuel_hours":gap_count,
           "imputed_sum_mwh":float(result.loc[result.is_imputed,"value_mwh"].sum())})
        rows.append(result)
    return pd.concat(rows,ignore_index=True),pd.DataFrame(metadata)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    scenarios_df,summary=scenarios(pd.read_csv(args.input))
    scenarios_df.to_csv(args.output/"renewable_missing_scenarios.csv",index=False)
    summary.to_csv(args.output/"fill_sensitivity_summary.csv",index=False)
    (args.output/"provenance.json").write_text(json.dumps({
      "classification":"hypothetical_missing_value_sensitivity_not_observed_eia",
      "methods":METHODS,
      "note":"Every source value is unchanged; 0 is a deliberately conservative zero-generation scenario, not an observed value. ±7 day matching uses the same UTC hour, not local DST.",
      "restriction":"Never relabel scenario-filled data as complete official historical observations."
    },indent=2))
    print(summary.to_string(index=False))
if __name__=="__main__":main()
