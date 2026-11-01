"""Compare official annual EIA-860 BA × fuel capacity, preserving vintage changes.

Observed changes are descriptive, not future capacity projections or dispatch.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def compare(a,b,out):
 old=pd.read_csv(a,dtype={"ba_code":"string","fuel":"string"})
 new=pd.read_csv(b,dtype={"ba_code":"string","fuel":"string"})
 for d in (old,new):
  if d.duplicated(["ba_code","fuel"]).any():raise ValueError("Repeated BA-fuel key")
  if d.official_nameplate_mw.isna().any():raise ValueError("Missing capacity")
 x=old[["ba_code","fuel","official_nameplate_mw","operating_generators"]].merge(
  new[["ba_code","fuel","official_nameplate_mw","operating_generators"]],
  on=["ba_code","fuel"],how="outer",suffixes=("_2023","_2024"),indicator=True,validate="one_to_one")
 for col in ("official_nameplate_mw_2023","official_nameplate_mw_2024","operating_generators_2023","operating_generators_2024"):
  x[col]=x[col].fillna(0)
 x["nameplate_delta_mw"]=x.official_nameplate_mw_2024-x.official_nameplate_mw_2023
 x["generator_count_delta"]=x.operating_generators_2024-x.operating_generators_2023
 x=x.sort_values("nameplate_delta_mw",key=lambda s:s.abs(),ascending=False)
 out.parent.mkdir(parents=True,exist_ok=True);x.to_csv(out,index=False)
 summary={"base_year":2023,"comparison_year":2024,
  "total_nameplate_mw_2023":float(old.official_nameplate_mw.sum()),
  "total_nameplate_mw_2024":float(new.official_nameplate_mw.sum()),
  "net_nameplate_delta_mw":float(x.nameplate_delta_mw.sum()),
  "ba_fuel_groups_2023":len(old),"ba_fuel_groups_2024":len(new),
  "new_ba_fuel_groups":int(x._merge.eq("right_only").sum()),
  "retired_or_removed_ba_fuel_groups":int(x._merge.eq("left_only").sum()),
  "note":"Annual vintage comparison does not establish individual builds/retirements, hourly dispatch, or future capacity."}
 if abs(summary["net_nameplate_delta_mw"]-(summary["total_nameplate_mw_2024"]-summary["total_nameplate_mw_2023"]))>1e-5:
  raise ValueError("Capacity conservation failed")
 out.with_suffix(".json").write_text(json.dumps(summary,indent=2)+"\n")
 print(json.dumps(summary,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--year-2023",type=Path,required=True);p.add_argument("--year-2024",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True);a=p.parse_args()
 compare(a.year_2023,a.year_2024,a.out)
