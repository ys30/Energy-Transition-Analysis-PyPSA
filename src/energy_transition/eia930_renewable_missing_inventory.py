"""Report exact BA/fuel/time gaps in EIA-930 annual renewable observations.

A missing value is not zero generation. Preserve signed valid observations.
"""
import argparse
from pathlib import Path
import pandas as pd

def missing_inventory(frame,year=2024,bas=("CISO","BPAT")):
    x=frame.copy()
    x["period"]=pd.to_datetime(x.period,utc=True)
    if x.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate BA-fuel-hour values")
    h=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    index=pd.MultiIndex.from_product([h,bas,("SUN","WND")],names=["period","respondent","fueltype"])
    data=x.set_index(["period","respondent","fueltype"])["value"].reindex(index)
    missing=data.isna().rename("missing").reset_index()
    gaps=missing[missing.missing].drop(columns=["missing"]).copy()
    gaps["issue"]="missing_or_null_reported_value"
    counts=gaps.groupby(["respondent","fueltype"]).size().rename("missing_hours").reset_index()
    overlap=gaps.groupby("period").size().rename("missing_ba_fuel_pairs").reset_index()
    return gaps,counts,overlap

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    gaps,counts,overlap=missing_inventory(pd.read_csv(a.input))
    gaps.to_csv(a.output/"missing_renewables_by_ba_fuel_hour.csv",index=False)
    counts.to_csv(a.output/"missing_renewables_by_ba_fuel_summary.csv",index=False)
    overlap.to_csv(a.output/"missing_renewables_hour_overlap.csv",index=False)
    print(counts.to_string(index=False))
    print("distinct missing UTC hours:",len(overlap))
    print(overlap.to_string(index=False))
if __name__=="__main__":main()
