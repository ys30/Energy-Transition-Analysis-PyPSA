"""Download and audit observed EIA-930 hourly solar/wind BA generation.

This is generation in MWh over each hour, NOT a weather-derived capacity
factor or a forecast of renewable resource potential.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
import pandas as pd

API = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
FUEL = ("SUN", "WND")

def fetch(year, bas=("CISO", "BPAT"), key=None):
    key = key or os.environ.get("EIA_API_KEY")
    if not key: raise ValueError("EIA_API_KEY required")
    params=[("api_key",key),("frequency","hourly"),("data[0]","value"),
            ("start",f"{year}-01-01T00"),("end",f"{year}-12-31T23"),
            ("length","5000"),("sort[0][column]","period"),
            ("sort[0][direction]","asc")]
    params += [("facets[respondent][]",x) for x in bas]
    params += [("facets[fueltype][]",x) for x in FUEL]
    rows=[];offset=0
    while True:
        url=API+"?"+urllib.parse.urlencode(params+[("offset",str(offset))])
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"energy-transition-research/0.6"}),timeout=90) as response:
            obj=json.load(response)["response"]
        page=obj.get("data")
        if page is None:raise ValueError("EIA fuel-type API returned no data field")
        if not page:break
        rows.extend(page);offset+=len(page)
        if offset>=int(obj.get("total",offset)):break
    if not rows:raise ValueError("No EIA renewable hourly generation records")
    frame=pd.DataFrame(rows)[["period","respondent","fueltype","value"]].copy()
    frame["period"]=pd.to_datetime(frame.period,utc=True)
    frame["value"]=pd.to_numeric(frame.value,errors="coerce")
    if frame.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate BA-fuel-hour observations")
    return frame

def audit(frame, year, bas=("CISO","BPAT")):
    expected=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    x=frame.copy()
    x["period"]=pd.to_datetime(x.period,utc=True)
    x["value"]=pd.to_numeric(x.value,errors="coerce")
    if x.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate renewable BA/fuel/hour")
    rows=[]
    for ba in bas:
        for fuel in FUEL:
            part=x[x.respondent.eq(ba)&x.fueltype.eq(fuel)]
            within=part[part.period.isin(expected)]
            missing=expected.difference(pd.DatetimeIndex(within.period))
            nulls=int(within.value.isna().sum())
            negatives=int(within.value.lt(0).sum())
            rows.append({"year":year,"ba_code":ba,"fueltype":fuel,
              "expected_hours":len(expected),"received_hours":len(within),
              "missing_timestamp_hours":len(missing),"missing_value_hours":nulls,
              "negative_generation_hours":negatives,
              "reported_generation_mwh_valid_nonnegative_only":float(within.loc[within.value.ge(0),"value"].sum()),
              "reported_signed_net_generation_mwh":float(within.value.sum()),
              "negative_net_generation_mwh":float(within.loc[within.value.lt(0),"value"].sum()),
              "minimum_hourly_net_generation_mwh":float(within.value.min()) if not within.empty else None,
              "coverage_fraction":float((len(expected)-len(missing)-nulls)/len(expected)),
              "complete_nonnegative":bool(not len(missing) and not nulls and not negatives)})
    return pd.DataFrame(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/eia930_renewables"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    frame=fetch(a.year,a.bas)
    frame.to_csv(a.output/"renewable_hourly_observed.csv",index=False)
    results=audit(frame,a.year,a.bas)
    results.to_csv(a.output/"renewable_hourly_coverage.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "api":API,"year":a.year,"bas":a.bas,"fueltypes":FUEL,
      "units":"EIA reported megawatthours per hour; numerically equivalent to average MW during each hourly interval",
      "warning":"Missing and negative hours are retained, not interpolated or clipped. The signed net generation sum is the relevant net-energy statistic; nonnegative-only sums overstate net generation. Reported actual BA generation must not be confused with meteorological availability or future resource potential.",
      "policy":"Never convert this to a model-wide p_max_pu without audited matching nameplate and geography."
    },indent=2))
    print(results.to_string(index=False))
if __name__=="__main__":main()
