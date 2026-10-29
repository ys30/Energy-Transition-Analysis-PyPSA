"""Audit observed EIA-930 BA interchange and accounting balance (2024).

Official EIA-930 series D=reported demand, NG=net generation, TI=total interchange.
Sign convention is not imposed: report both accounting residual alternatives
and observed correlations until independently verified.
"""
import argparse,json
from pathlib import Path
import pandas as pd
from .eia930_generation_audit import fetch_net_generation,API
from .eia930_west import fetch_eia_demand
import urllib.parse,urllib.request,os

def fetch_ti(year,bas):
    key=os.environ["EIA_API_KEY"]
    params=[("api_key",key),("frequency","hourly"),("data[0]","value"),
            ("facets[type][]","TI"),("start",f"{year}-01-01T00"),
            ("end",f"{year}-12-31T23"),("length","5000"),
            ("sort[0][column]","period"),("sort[0][direction]","asc")]
    params.extend(("facets[respondent][]",b) for b in bas)
    rows=[];offset=0
    while True:
        url=API+"?"+urllib.parse.urlencode(params+[("offset",str(offset))])
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"pypsa-west-balance-audit/0.1"}),timeout=90) as f:
            response=json.load(f)["response"]
        page=response["data"]
        if not page:break
        rows.extend(page);offset+=len(page)
        if offset>=int(response.get("total",offset)):break
    if not rows:raise ValueError("No EIA-930 TI observations")
    df=pd.DataFrame(rows)[["period","respondent","value"]]
    df["period"]=pd.to_datetime(df.period,utc=True)
    df["value"]=pd.to_numeric(df.value,errors="coerce")
    if df.duplicated(["respondent","period"]).any():raise ValueError("Duplicate interchange observations")
    return df

def balance_audit(demand,generation,interchange,bas,year):
    idx=pd.MultiIndex.from_product([bas,pd.date_range(f"{year}-01-01",f"{year+1}-01-01",freq="h",inclusive="left",tz="UTC")],names=["respondent","period"])
    outputs={}
    for label,df in [("demand",demand),("generation",generation),("interchange",interchange)]:
        outputs[label]=df.set_index(["respondent","period"])["value"].reindex(idx)
    merged=pd.DataFrame(outputs).reset_index()
    merged["residual_d_minus_ng_minus_ti"]=merged.demand-merged.generation-merged.interchange
    merged["residual_d_minus_ng_plus_ti"]=merged.demand-merged.generation+merged.interchange
    audit=merged.groupby("respondent").agg(
      expected_hours=("period","size"),
      complete_triples=("residual_d_minus_ng_minus_ti","count"),
      missing_demand=("demand",lambda v:int(v.isna().sum())),
      missing_generation=("generation",lambda v:int(v.isna().sum())),
      missing_interchange=("interchange",lambda v:int(v.isna().sum())),
      sum_observed_demand_mwh=("demand","sum"),
      sum_observed_generation_mwh=("generation","sum"),
      sum_observed_interchange_mwh=("interchange","sum"),
      mae_d_minus_ng_minus_ti=("residual_d_minus_ng_minus_ti",lambda v:float(v.abs().mean())),
      mae_d_minus_ng_plus_ti=("residual_d_minus_ng_plus_ti",lambda v:float(v.abs().mean()))
    ).reset_index()
    return merged,audit

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=2024)
    p.add_argument("--bas",nargs="+",default=["CISO","BPAT"])
    p.add_argument("--output",type=Path,default=Path("outputs/eia930_balance"))
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    d=fetch_eia_demand(a.year,a.bas)
    ng=fetch_net_generation(a.year,a.bas)
    ti=fetch_ti(a.year,a.bas)
    frame,audit=balance_audit(d,ng,ti,a.bas,a.year)
    frame.to_csv(a.output/"hourly_balance_audit.csv",index=False)
    audit.to_csv(a.output/"ba_balance_summary.csv",index=False)
    (a.output/"provenance.json").write_text(json.dumps({
      "source":API,"types":["D","NG","TI"],
      "warning":"Demand may include audited imputations; NG/TI incomplete hours retained. Interchange sign convention NOT assumed; neither accounting residual is independently validated.",
      "interpretation":"D - NG +/- TI is a screening diagnostic, not a full energy accounting identity; storage, BA net interchange conventions and losses require validation."
    },indent=2))
    print(audit.to_string(index=False))
if __name__=="__main__":main()
