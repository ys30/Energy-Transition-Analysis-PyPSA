"""Strict historical 2024 hourly coverage gate before any annual storage optimization.

A 2024 leap year has 8,784 UTC hours. We do not silently interpolate
missing BA demand or fuel records. Report usable aligned runs separately.
"""
import argparse
import json
from pathlib import Path
import pandas as pd

def audit_annual_inputs(demand, renewables, year=2024, bas=("CISO","BPAT")):
    hours=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    d=demand.copy();r=renewables.copy()
    for frame in (d,r):
        frame["period"]=pd.to_datetime(frame["period"],utc=True)
    if d.duplicated(["period","respondent"]).any():
        raise ValueError("Duplicate demand BA-hour")
    if r.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate renewable BA-fuel-hour")
    d=d[d.respondent.isin(bas)].pivot(index="period",columns="respondent",values="value").reindex(hours)
    r=r[r.respondent.isin(bas)&r.fueltype.isin(("SUN","WND"))].pivot(
       index="period",columns=["respondent","fueltype"],values="value").reindex(hours)
    d=d.reindex(columns=list(bas))
    r=r.reindex(columns=pd.MultiIndex.from_product([bas,("SUN","WND")]))
    for frame in (d,r):
        frame[:]=frame.apply(pd.to_numeric,errors="coerce")
    demand_ok=d.notna().all(axis=1)&d.gt(0).all(axis=1)
    renewable_ok=r.notna().all(axis=1)
    aligned=demand_ok&renewable_ok
    groups=aligned.ne(aligned.shift(fill_value=False)).cumsum()
    segments=[]
    for _,sub in aligned.groupby(groups):
        if sub.iloc[0]:
            segments.append({"start_utc":sub.index[0].isoformat(),
                             "end_utc":sub.index[-1].isoformat(),
                             "hours":len(sub)})
    segments.sort(key=lambda x:x["hours"],reverse=True)
    return {
      "year":year,"expected_utc_hours":len(hours),
      "complete_demand_hours":int(demand_ok.sum()),
      "complete_renewable_hours":int(renewable_ok.sum()),
      "aligned_complete_hours":int(aligned.sum()),
      "missing_or_invalid_demand_hours":int((~demand_ok).sum()),
      "missing_renewable_hours":int((~renewable_ok).sum()),
      "full_year_optimization_permitted":bool(aligned.all()),
      "longest_aligned_contiguous_run":segments[0] if segments else None,
      "number_of_complete_runs":len(segments),
      "restriction":"No yearly optimization or economic claim with incomplete data; no automatic filling, clipping, or representative-hour substitution.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--demand",type=Path,required=True)
    p.add_argument("--renewables",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    result=audit_annual_inputs(pd.read_csv(a.demand),pd.read_csv(a.renewables))
    (a.output/"annual_hourly_coverage_gate.json").write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
