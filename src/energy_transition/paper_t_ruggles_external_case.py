"""Paper T external validation: archived EIA-930 original vs Ruggles 2019 cleaned.

This is an *original-to-derived* comparison for a common UTC timestamp grid.
It does NOT independently certify the EFS2020→ReEDS2022 physical-hour crosswalk.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,statistics,urllib.request
from datetime import datetime,timedelta,timezone
from pathlib import Path

SOURCE_REPO="truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data"
SOURCE_COMMIT="b80145df5f92aba56c52ed45281831b93543fb3b"
BAS=("IPCO","AZPS","BPAT")
LAGS=tuple(range(-12,13))
START="2015-07-02 00:00:00"
END="2019-07-01 23:00:00"
N=35064

def fetch_source(ba,kind):
    rel=f"data/release_2019_Oct/{kind}/{ba}.csv"
    url=f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{rel}"
    req=urllib.request.Request(url,headers={"User-Agent":"Paper-T-source-audit/1.0"})
    with urllib.request.urlopen(req,timeout=90) as response:
        body=response.read()
    return list(csv.DictReader(io.StringIO(body.decode("utf-8-sig")))),{
        "url":url,"sha256":hashlib.sha256(body).hexdigest(),"bytes":len(body)}
def value(x):
    if x is None or str(x).strip().upper() in ("MISSING","NAN",""):
        return None
    return float(x)
def validate_and_merge(raw,clean):
    orig={r["date_time"]:r for r in raw}
    if len(orig)!=len(raw):raise ValueError("Duplicate raw UTC timestamps")
    if len(clean)!=N:raise ValueError(f"Expected {N} cleaned UTC hours")
    t0=datetime.strptime(START,"%Y-%m-%d %H:%M:%S")
    result=[]
    for i,row in enumerate(clean):
        t=row["date_time"]
        if t!=(t0+timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"):
            raise ValueError(f"UTC grid gap or time disorder: {i}: {t}")
        if t not in orig:raise ValueError("Cleaned time lacks original UTC row: "+t)
        observed=value(orig[t]["demand (MW)"])
        reproduced=value(row["raw demand (MW)"])
        if observed!=reproduced:raise ValueError("Archived original does not equal cleaned raw column: "+t)
        result.append({"utc_hour":t,"raw":observed,
             "clean":value(row["cleaned demand (MW)"]),"category":row["category"]})
    if result[-1]["utc_hour"]!=END:raise ValueError("Unexpected end")
    return result
def lag_scan(rows):
    out=[]
    for lag in LAGS:
        # Compare original at index i with clean index i-lag; never wrap year edges.
        deviations=[]
        exact=0
        for i in range(len(rows)):
            j=i-lag
            if not 0<=j<len(rows):continue
            a,b=rows[i]["raw"],rows[j]["clean"]
            if a is None or b is None:continue
            err=abs(a-b)
            deviations.append(err)
            if err==0:exact+=1
        if not deviations:raise ValueError("No comparable measurements")
        out.append({"lag_h":lag,"compared_hours":len(deviations),
          "mae_mw":sum(deviations)/len(deviations),
          "median_abs_error_mw":statistics.median(deviations),
          "exact_fraction":exact/len(deviations)})
    return out
def summarize(ba,rows,scan):
    best=sorted(scan,key=lambda r:(r["mae_mw"],abs(r["lag_h"]),r["lag_h"]))
    if best[0]["lag_h"]!=0:raise ValueError(f"{ba} unexpectedly prefers a nonzero lag")
    raw_valid=[r for r in rows if r["raw"] is not None and r["clean"] is not None]
    changed=[r for r in raw_valid if r["raw"]!=r["clean"]]
    cats={}
    for r in rows:cats[r["category"]]=cats.get(r["category"],0)+1
    if cats.get("OKAY",0)>0 and any(r["raw"]!=r["clean"] for r in rows if r["category"]=="OKAY"):
        raise ValueError(f"{ba} OKAY class not exactly retained")
    return {"ba":ba,"hours":len(rows),"raw_numeric_hours":len(raw_valid),
      "missing_raw_hours":len(rows)-len(raw_valid),"changed_numeric_hours":len(changed),
      "unchanged_numeric_fraction":(len(raw_valid)-len(changed))/len(raw_valid),
      "best_lag_h":best[0]["lag_h"],"best_mae_mw":best[0]["mae_mw"],
      "best_exact_fraction":best[0]["exact_fraction"],
      "runnerup_lag_h":best[1]["lag_h"],"runnerup_mae_mw":best[1]["mae_mw"],
      "category_counts":cats}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--outdir",type=Path,required=True)
    args=p.parse_args()
    args.outdir.mkdir(parents=True,exist_ok=True)
    results=[];summary=[];source=[]
    for ba in BAS:
        orig,meta1=fetch_source(ba,"original_eia_files")
        clean,meta2=fetch_source(ba,"balancing_authorities")
        rows=validate_and_merge(orig,clean)
        scan=lag_scan(rows)
        summary.append(summarize(ba,rows,scan))
        for item in scan:results.append({"ba":ba,**item})
        source.extend([{**meta1,"ba":ba,"type":"EIA original archive"},
                       {**meta2,"ba":ba,"type":"Ruggles cleaned derivative"}])
    with (args.outdir/"three_ba_all_75_lag_points.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(results[0]));w.writeheader();w.writerows(results)
    with (args.outdir/"three_ba_summary.csv").open("w",newline="") as f:
        columns=[k for k in summary[0] if k!="category_counts"]
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
        for row in summary:w.writerow({k:row[k] for k in columns})
    (args.outdir/"source_hashes.json").write_text(json.dumps({"source_commit":SOURCE_COMMIT,
      "files":source,"data_meaning":"2019 raw EIA export and Ruggles cleaned edition; same-source lineage"},indent=2)+"\n")
    (args.outdir/"category_counts.json").write_text(json.dumps({x["ba"]:x["category_counts"] for x in summary},indent=2)+"\n")
    assert len(results)==len(BAS)*len(LAGS)
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
