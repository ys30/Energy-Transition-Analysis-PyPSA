"""Paper T WP1: 2019 Oct vs 2020 Oct Ruggles CLEANED data release-pair audit.

Two documented published editions of the same EIA-930 BA hourly-demand series.
Compare only overlapping *UTC-label* timestamps, 2015-07-02 to 2019-07-01.
This validates numerical identity under documented hour labels, not EFS/ReEDS clocks.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,statistics,urllib.request
from datetime import datetime,timedelta
from pathlib import Path

SOURCE_COMMIT="b80145df5f92aba56c52ed45281831b93543fb3b"
SOURCE_ROOT=f"https://raw.githubusercontent.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data/{SOURCE_COMMIT}/data"
BAS=("IPCO","AZPS","BPAT")
LAGS=range(-12,13)
N=35064
START=datetime(2015,7,2)

def download(ba,release):
    url=f"{SOURCE_ROOT}/{release}/balancing_authorities/{ba}.csv"
    request=urllib.request.Request(url,headers={"User-Agent":"Paper-T-source-forensics/1.0"})
    with urllib.request.urlopen(request,timeout=90) as response: raw=response.read()
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    records=list(reader)
    for field in ("date_time","cleaned demand (MW)","raw demand (MW)","category"):
        if field not in reader.fieldnames:raise ValueError("Missing documented field "+field)
    return records,{"ba":ba,"release":release,"url":url,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
def validate(base,next_release):
    if len(base)!=N or len(next_release)<N:raise ValueError("Incorrect release coverage")
    lookup={r["date_time"]:r for r in next_release}
    if len(lookup)!=len(next_release):raise ValueError("Duplicate newer timestamps")
    pair=[]
    for i,old in enumerate(base):
        t=(START+timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")
        if old["date_time"]!=t or t not in lookup:raise ValueError("UTC timestamp mismatch")
        new=lookup[t]
        a,b=float(old["cleaned demand (MW)"]),float(new["cleaned demand (MW)"])
        if not all(map(lambda z:float('-inf')<z<float('inf'),(a,b))):
            raise ValueError("Nonfinite cleaned demand")
        pair.append((t,a,b,old["category"],new["category"]))
    return pair
def compute(pair):
    lag_rows=[]
    for lag in LAGS:
        err=[]
        for i in range(N):
            j=i-lag
            if 0<=j<N:err.append(abs(pair[i][1]-pair[j][2]))
        lag_rows.append({"lag_h":lag,"compared_hours":len(err),
            "mae_mw":sum(err)/len(err),
            "median_abs_error_mw":statistics.median(err),
            "exact_fraction":sum(v==0 for v in err)/len(err)})
    return lag_rows
def summarize(ba,pair,lags):
    ranking=sorted(lags,key=lambda x:(x["mae_mw"],abs(x["lag_h"]),x["lag_h"]))
    if ranking[0]["lag_h"]!=0:raise ValueError(f"{ba} unexpected best lag")
    changed=[x for x in pair if x[1]!=x[2]]
    return {"ba":ba,"shared_hours":len(pair),"changed_hours":len(changed),
      "change_fraction":len(changed)/len(pair),
      "mean_annual_energy_2019_mwh":sum(x[1] for x in pair)/4,
      "mean_annual_energy_2020_mwh":sum(x[2] for x in pair)/4,
      "lag_best_h":ranking[0]["lag_h"],"best_mae_mw":ranking[0]["mae_mw"],
      "best_exact_fraction":ranking[0]["exact_fraction"],
      "runnerup_lag_h":ranking[1]["lag_h"],"runnerup_mae_mw":ranking[1]["mae_mw"],
      "change_categories_2019":dict(sorted({c:sum(x[3]==c for x in changed) for c in {x[3] for x in changed}}.items())),
      "change_categories_2020":dict(sorted({c:sum(x[4]==c for x in changed) for c in {x[4] for x in changed}}.items()))}
def main():
    p=argparse.ArgumentParser();p.add_argument("--outdir",required=True,type=Path)
    output=p.parse_args().outdir;output.mkdir(parents=True,exist_ok=True)
    scan=[];summaries=[];sources=[]
    for ba in BAS:
        old,m0=download(ba,"release_2019_Oct")
        new,m1=download(ba,"release_2020_Oct")
        pair=validate(old,new)
        result=compute(pair)
        scan.extend([{"ba":ba,**x} for x in result])
        summaries.append(summarize(ba,pair,result))
        sources.extend([m0,m1])
    def write_table(path,items,fields):
        with path.open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            writer.writerows({k:r[k] for k in fields} for r in items)
    write_table(output/"release_pair_75_lags.csv",scan,list(scan[0]))
    simple_cols=[x for x in summaries[0] if not x.startswith("change_categories")]
    write_table(output/"release_pair_summary.csv",summaries,simple_cols)
    (output/"source_manifest.json").write_text(json.dumps({"commit":SOURCE_COMMIT,
        "source_role":"2019-Oct and 2020-Oct independently issued cleansed data editions, common EIA source lineage",
        "raw_source_clock":"EIA UTC hour labels retained in archived release",
        "release_files":sources,"n_lags":len(scan),"screening_claim":"relative-hour correspondence, not physical join authorization"},indent=2)+"\n")
    (output/"changed_category_summary.json").write_text(json.dumps(
        {r["ba"]:{"old":r["change_categories_2019"],"new":r["change_categories_2020"]} for r in summaries},indent=2)+"\n")
    print(json.dumps(summaries,indent=2))
    assert len(scan)==75 and all(r["lag_best_h"]==0 for r in summaries)
if __name__=="__main__":main()
