"""Gate EIA-860/EIA-923 BA screening interpretation without mislabeling partial data as calibration."""
import argparse,json
from pathlib import Path
import pandas as pd

def check(path,out):
 d=pd.read_csv(path,dtype={"ba_code":"string"})
 required={"ba_code","qualified_annual_mwh","official_nameplate_mw","qualified_generation_over_nameplate_hours","capacity_linked"}
 if required-set(d):raise ValueError("Missing cross-source screening columns")
 if d.ba_code.duplicated().any():raise ValueError("Duplicate BA")
 if not d.capacity_linked.astype(str).str.lower().eq("true").all():raise ValueError("Unmatched BA capacity")
 d["screen_ratio"]=pd.to_numeric(d.qualified_generation_over_nameplate_hours,errors="coerce")
 if d.screen_ratio.isna().any() or d.screen_ratio.lt(-0.01).any():
  raise ValueError("Invalid ratio; inspect negative EIA net generation or missing input")
 d["screen_gt_one"]=d.screen_ratio.gt(1.0)
 d["interpretation"]="partial_qualified_generation_vs_2024_nameplate_not_calibrated_cf"
 cols=["ba_code","qualified_annual_mwh","official_nameplate_mw","screen_ratio","screen_gt_one","interpretation"]
 out.parent.mkdir(parents=True,exist_ok=True);d[cols].to_csv(out,index=False)
 result={"year":2024,"ba_count":len(d),"observed_ba_ratios":{str(r.ba_code):float(r.screen_ratio) for r in d.itertuples()},
 "ratios_exceeding_one":d.loc[d.screen_gt_one,"ba_code"].astype(str).tolist(),
 "full_generation_coverage_verified":False,"hourly_dispatch_calibration_ready":False,
 "reason":"EIA923 qualification excludes incomplete rows, EIA860 nameplate is annual operating inventory; no complete BA denominator reconciliation."}
 out.with_suffix(".json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--input",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();check(a.input,a.out)
