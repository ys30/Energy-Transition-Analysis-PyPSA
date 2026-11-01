"""Screen EIA-923 qualified 2024 BA generation against EIA-860 operating BA nameplate.

BA-only; matched fuel codes are NOT assumed. Qualified EIA-923 is a subset,
so apparent capacity factors are lower-bound observations, not fleet CFs.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(capacity_path,generation_path,out):
 cap=pd.read_csv(capacity_path,dtype={"ba_code":"string"})
 gen=pd.read_csv(generation_path,dtype={"ba_code":"string"})
 if not {"ba_code","official_nameplate_mw"}<=set(cap):raise ValueError("Missing EIA860 capacity")
 if not {"ba_code","qualified_annual_mwh","withheld_reported_annual_mwh"}<=set(gen):raise ValueError("Missing qualified EIA923 generation")
 capacity=cap.groupby("ba_code",as_index=False).official_nameplate_mw.sum()
 gen_ba=gen.groupby("ba_code",as_index=False)[["qualified_annual_mwh","withheld_reported_annual_mwh"]].sum()
 result=gen_ba.merge(capacity,on="ba_code",how="left",validate="one_to_one")
 result["screen_hours"]=8784 # 2024 is a leap year; EIA-923 calendar year, not EFS 8760
 result["qualified_generation_over_nameplate_hours"]=result.qualified_annual_mwh/(result.official_nameplate_mw*8784)
 result["capacity_linked"]=result.official_nameplate_mw.gt(0)
 result["calibrated_capacity_factor"]=False
 result["full_ba_generation_coverage_verified"]=False
 out.parent.mkdir(parents=True,exist_ok=True);result.to_csv(out,index=False)
 report={"year":2024,"ba_groups_qualified_eia923":len(gen_ba),
  "ba_groups_with_nameplate":int(result.capacity_linked.sum()),
  "ba_groups_missing_nameplate":result.loc[~result.capacity_linked,"ba_code"].tolist(),
  "eia923_qualified_generation_mwh":float(gen_ba.qualified_annual_mwh.sum()),
  "hour_denominator":8784,"calendar":"2024 leap-year EIA historical only; not EFS scenario hour semantics",
  "fuel_code_crosswalk_verified":False,"full_ba_capacity_factor_verified":False,
  "warning":"Partial qualified Page1 generation and broader EIA860 capacity do not yield a calibrated fleet capacity factor."}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--eia860",type=Path,required=True);p.add_argument("--eia923",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();audit(a.eia860,a.eia923,a.out)
