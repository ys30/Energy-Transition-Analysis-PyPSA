"""Check EIA fuel-type API records for exact 2024 renewable gaps.

No overwrite or silent repair of the source dataset: keep an independent
response audit with source timestamps and status.
"""
import argparse,json,os,urllib.parse,urllib.request
from pathlib import Path
import pandas as pd
from .eia930_renewable_missing_inventory import missing_inventory
API="https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"

def refetch(frame,key,year=2024):
    gaps,_,_=missing_inventory(frame,year)
    windows=[("BPAT","SUN","2024-07-25T00","2024-07-25T23"),
             ("CISO","SUN","2024-11-02T00","2024-11-04T23"),
             ("CISO","WND","2024-11-02T00","2024-11-04T23"),
             ("BPAT","SUN","2024-11-08T00","2024-11-08T23")]
    recovered=[];responses=[]
    for ba,fuel,start,end in windows:
        query=[("api_key",key),("frequency","hourly"),("data[0]","value"),
               ("facets[respondent][]",ba),("facets[fueltype][]",fuel),
               ("start",start),("end",end),("length","5000")]
        url=API+"?"+urllib.parse.urlencode(query)
        with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"energy-transition-audit/0.7"}),timeout=90) as res:
            result=json.load(res)["response"]
        if "data" not in result:raise ValueError("EIA refetch lacks data")
        records=result["data"]
        responses.append({"ba":ba,"fueltype":fuel,"start":start,"end":end,
                          "returned_records":len(records),"api_total":result.get("total")})
        for record in records:
            recovered.append({"period":pd.to_datetime(record["period"],utc=True),
              "respondent":record["respondent"],"fueltype":record["fueltype"],
              "value":pd.to_numeric(record["value"],errors="coerce")})
    fetched=pd.DataFrame(recovered,columns=["period","respondent","fueltype","value"])
    if fetched.duplicated(["period","respondent","fueltype"]).any():
        raise ValueError("Duplicate refreshed fuel hour")
    matched=gaps.merge(fetched,on=["period","respondent","fueltype"],how="left",indicator=True)
    matched["verified_recovered"]=matched["value"].notna()
    return matched,responses

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args();key=os.environ.get("EIA_API_KEY")
    if not key:raise ValueError("EIA_API_KEY required")
    args.output.mkdir(parents=True,exist_ok=True)
    matched,responses=refetch(pd.read_csv(args.input),key)
    matched.to_csv(args.output/"official_gap_refetch_matches.csv",index=False)
    (args.output/"official_gap_refetch_provenance.json").write_text(json.dumps({
      "api":API,"source":"official EIA RTO fuel-type-data","request_windows":responses,
      "missing_pairs_before":len(matched),
      "recovered_valid_numeric_pairs":int(matched.verified_recovered.sum()),
      "remaining_pairs":int((~matched.verified_recovered).sum()),
      "policy":"Refetched official records are diagnostic only. No source overwrite or imputation."
    },indent=2))
    print(matched[["period","respondent","fueltype","value","verified_recovered"]].to_string(index=False))
if __name__=="__main__":main()
