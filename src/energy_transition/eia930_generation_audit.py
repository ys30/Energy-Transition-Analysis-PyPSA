"""Independent EIA-930 observed net-generation diagnostic for historical BA calibration.

EIA-930 'NG' is balancing-authority total net generation, not EIA-923
plant/fuel generation. Negative/missing records are preserved, never imputed.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request
import pandas as pd

API="https://api.eia.gov/v2/electricity/rto/region-data/data/"

def fetch_net_generation(year, bas, api_key=None):
    key=api_key or os.environ.get("EIA_API_KEY")
    if not key: raise ValueError("EIA_API_KEY is required")
    params=[("api_key",key),("frequency","hourly"),("data[0]","value"),
            ("facets[type][]","NG"),("start",f"{year}-01-01T00"),
            ("end",f"{year}-12-31T23"),("length","5000"),
            ("sort[0][column]","period"),("sort[0][direction]","asc")]
    params.extend(("facets[respondent][]",b) for b in bas)
    rows=[]; offset=0
    while True:
        url=API+"?"+urllib.parse.urlencode(params+[("offset",str(offset))])
        req=urllib.request.Request(url,headers={"User-Agent":"energy-transition-pypsa/0.4"})
        with urllib.request.urlopen(req,timeout=90) as f:
            obj=json.load(f)
        response=obj.get("response",{})
        page=response.get("data")
        if page is None: raise ValueError("EIA NG API response missing data")
        if not page: break
        rows.extend(page);offset+=len(page)
        if offset>=int(response.get("total",offset)):break
    if not rows:raise ValueError("No EIA-930 net generation data")
    frame=pd.DataFrame(rows)
    frame=frame[["period","respondent","value"]].copy()
    frame["period"]=pd.to_datetime(frame.period,utc=True)
    raw=frame["value"]
    parsed=pd.to_numeric(raw,errors="coerce")
    # Preserve explicit nulls, but reject malformed non-null numeric strings.
    malformed=raw.notna() & parsed.isna()
    if malformed.any():
        raise ValueError(f"EIA NG API returned {int(malformed.sum())} malformed non-null numeric values")
    frame["value"]=parsed
    if frame.duplicated(["period","respondent"]).any():
        raise ValueError("Duplicate BA-hour NG measurements")
    return frame

def summarize_net_generation(generation, year, bas):
    g=generation.copy()
    expected=8784 if pd.Timestamp(f"{year}-12-31").is_leap_year else 8760
    records=[]
    for ba in bas:
        subset=g[g.respondent.eq(ba)].copy()
        valid=subset.value.notna()
        expected_index=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")
        observed_index=pd.DatetimeIndex(subset.period)
        missing_times=expected_index.difference(observed_index)
        extra_times=observed_index.difference(expected_index)
        records.append({
          "year":year,"ba_code":ba,"received_hours":len(subset),
          "expected_hours":expected,"missing_value_hours":int((~valid).sum()),
          "missing_timestamp_hours":len(missing_times),
          "first_missing_timestamp_utc":missing_times.min().isoformat() if len(missing_times) else "",
          "last_missing_timestamp_utc":missing_times.max().isoformat() if len(missing_times) else "",
          "outside_year_hours":len(extra_times),
          "negative_value_hours":int((subset.value<0).sum()),
          "reported_net_generation_mwh_nonmissing_only":float(subset.loc[valid,"value"].sum()),
          "complete":bool(len(subset)==expected and valid.all() and not len(missing_times) and not len(extra_times))
        })
    return pd.DataFrame(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/ba_generation_audit"))
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    df=fetch_net_generation(args.year,args.bas)
    df.to_csv(args.output/"eia930_net_generation_hourly.csv",index=False)
    audit=summarize_net_generation(df,args.year,args.bas)
    audit.to_csv(args.output/"net_generation_audit.csv",index=False)
    # Preserve all missing timestamps for direct investigation of source coverage.
    missing=[]
    expected_index=pd.date_range(f"{args.year}-01-01",f"{args.year+1}-01-01",freq="h",inclusive="left",tz="UTC")
    for ba in args.bas:
        got=pd.DatetimeIndex(df.loc[df.respondent.eq(ba),"period"])
        for ts in expected_index.difference(got):
            missing.append({"ba_code":ba,"timestamp_utc":ts.isoformat()})
    pd.DataFrame(missing,columns=["ba_code","timestamp_utc"]).to_csv(args.output/"missing_timestamps.csv",index=False)
    manifest={
     "source":API,"source_type":"NG","units":"MW reported at hourly frequency",
     "boundary":"EIA-930 balancing authority total net generation, NOT plant/fuel-specific EIA-923 generation",
     "caution":"Negative readings and null values preserved. No fuel calibration; only hours with observed values are summed."
    }
    (args.output/"provenance.json").write_text(json.dumps(manifest,indent=2))
    print(audit.to_string(index=False))
if __name__=="__main__":
    main()
