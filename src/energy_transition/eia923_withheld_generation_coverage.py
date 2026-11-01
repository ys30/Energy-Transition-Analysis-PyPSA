"""Audit EIA-923 qualified versus withheld 2024 BA generation coverage before calibration."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
 p=argparse.ArgumentParser();p.add_argument("--qualified",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 x=pd.read_csv(a.qualified,dtype={"ba_code":"string"})
 need={"ba_code","source_rows","qualified_rows","qualified_annual_mwh","withheld_reported_annual_mwh"}
 if need-set(x):raise ValueError("Missing qualification fields")
 g=x.groupby("ba_code",as_index=False)[["source_rows","qualified_rows","qualified_annual_mwh","withheld_reported_annual_mwh"]].sum()
 g["qualified_row_fraction"]=g.qualified_rows/g.source_rows
 g["reported_annual_mwh_total"]=g.qualified_annual_mwh+g.withheld_reported_annual_mwh
 g["withheld_share_of_reported"]=g.withheld_reported_annual_mwh/g.reported_annual_mwh_total.where(g.reported_annual_mwh_total.ne(0))
 g["complete_annual_generation_verified"]=False
 a.out.parent.mkdir(parents=True,exist_ok=True);g.to_csv(a.out,index=False)
 report={"ba_coverage":{str(r.ba_code):{"source_rows":int(r.source_rows),"qualified_rows":int(r.qualified_rows),
   "qualified_row_fraction":float(r.qualified_row_fraction),
   "withheld_reported_mwh":float(r.withheld_reported_annual_mwh),
   "withheld_share_of_reported":None if pd.isna(r.withheld_share_of_reported) else float(r.withheld_share_of_reported)}
   for r in g.itertuples()},
  "calibrated_cf_ready":False,"warning":"Withheld reported annual generation may include negative numbers; coverage shares can be non-probabilistic."}
 a.out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
