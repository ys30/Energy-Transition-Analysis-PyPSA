"""Sample actual EIA-930 hourly BA wind/solar MWh via official v2 API.

2023 UTC hour-ending observations; use as *BA diagnostics*, NEVER directly
as state-level validation of ReEDS county source CF. The API results may
include negative net-generation values; preserve them without clipping.
"""
from __future__ import annotations
import argparse, hashlib,json,urllib.parse,urllib.request,time
from pathlib import Path
import pandas as pd
import numpy as np

URL="https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"
CODES={"wind":"WND","solar":"SUN"}
BA_CODES=("PNM","PSCO","IPCO","WACM")
SOURCE="https://www.eia.gov/electricity/930-content/about.html"

def url_for(ba,fuel,start,end,key=None):
    if ba not in BA_CODES or fuel not in CODES:
        raise ValueError("Only pinned source-diagnostic BA codes and wind/solar permitted")
    if start>end or not start.startswith("2023-") or not end.startswith("2023-"):
        raise ValueError("Pilot period must be within 2023")
    params=[
        ("frequency","hourly"),("data[0]","value"),
        ("facets[respondent][]",ba),("facets[fueltype][]",CODES[fuel]),
        ("start",start),("end",end),
        ("sort[0][column]","period"),("sort[0][direction]","asc"),
        ("offset","0"),("length","5000")]
    if key:params.append(("api_key",key))
    return URL+"?"+urllib.parse.urlencode(params)

def parse_payload(body,ba,fuel):
    payload=json.loads(body)
    response=payload.get("response",{})
    if payload.get("error"):
        raise ValueError("EIA API error: "+str(payload["error"])[:300])
    rows=response.get("data",[])
    if not rows:raise ValueError(f"No official BA fuel source records for {ba} {fuel}")
    total=int(response.get("total",len(rows)))
    if total!=len(rows):raise ValueError("EIA API source query pagination incomplete")
    records=[]
    for x in rows:
        if x.get("respondent")!=ba or x.get("fueltype")!=CODES[fuel]:
            raise ValueError("EIA API facet mismatch")
        period=str(x.get("period",""))
        # EIA API period is UTC hour-ending YYYY-MM-DDTHH; require strict source token.
        if len(period)!=13 or period[10]!="T" or not period[:4]=="2023":
            raise ValueError(f"Unexpected EIA period token: {period!r}")
        ts=pd.to_datetime(period,utc=True,errors="raise")
        value=float(x["value"])
        if not np.isfinite(value):raise ValueError("Nonfinite EIA observed MWh")
        unit=str(x.get("value-units","")).strip()
        if unit and "MWh" not in unit and "megawatthour" not in unit.lower():
            raise ValueError("Unexpected EIA value unit "+unit)
        records.append({
            "utc_hour_end":ts.isoformat(),"ba_code":ba,
            "fuel":fuel,"net_generation_mwh":value,
            "source_url":SOURCE,"source_release":"EIA API v2 electricity/rto/fuel-type-data",
            "observation_year":2023,"original_period":period,
            "original_fueltype":CODES[fuel],"reported_unit":unit or "MWh (route metadata)",
        })
    f=pd.DataFrame(records)
    if f.duplicated(["utc_hour_end","ba_code","fuel"]).any():
        raise ValueError("Duplicate source hour")
    return f

def fetch(url,attempts=3):
    for i in range(attempts):
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"PaperS-Scientific-Data-Audit/1.0"})
            with urllib.request.urlopen(req,timeout=90) as r:
                return r.read()
        except Exception:
            if i==attempts-1:raise
            time.sleep(2*(i+1))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--start",default="2023-07-01T00")
    p.add_argument("--end",default="2023-07-07T23")
    p.add_argument("--api-key",default=None)
    a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    outputs=[];diagnostics=[]
    for ba in BA_CODES:
        for fuel in CODES:
            url=url_for(ba,fuel,a.start,a.end,a.api_key)
            raw=fetch(url)
            df=parse_payload(raw,ba,fuel)
            outputs.append(df)
            diagnostics.append({
                "ba_code":ba,"fuel":fuel,"records":len(df),
                "period_start":df.utc_hour_end.min(),"period_end":df.utc_hour_end.max(),
                "negative_hours":int((df.net_generation_mwh<0).sum()),
                "source_response_sha256":hashlib.sha256(raw).hexdigest(),
                "data_source_endpoint":URL,
            })
    frame=pd.concat(outputs,ignore_index=True)
    if frame.duplicated(["utc_hour_end","ba_code","fuel"]).any():
        raise ValueError("Duplicate BA/fuel/hour in combined source")
    frame.to_csv(a.out/"paper_s_EIA930_2023_BA_wind_solar_hourly_pilot.csv",index=False)
    pd.DataFrame(diagnostics).to_csv(a.out/"paper_s_EIA930_BA_pilot_coverage.csv",index=False)
    manifest={"status":"OBSERVED_EIA930_BA_SOURCE_PILOT_ONLY",
        "records":len(frame),"source_url":SOURCE,"source_endpoint":URL,
        "BA_codes":list(BA_CODES),"fuels":list(CODES),
        "source_period_start":a.start,"source_period_end":a.end,
        "BA_eq_state_assumed":False,
        "observed_to_ReEDS_state_hourly_validated":False,
        "source_clock":"UTC EIA API hour-end labels (must audit before joins)",
        "geographic_crosswalk_verified":False}
    (a.out/"paper_s_EIA930_BA_pilot_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_EIA930_OBSERVED_BA_PILOT_SUCCESS",json.dumps(manifest))

if __name__=="__main__":main()
