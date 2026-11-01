"""Produce focused plant ID review for materially changed main-grid candidates."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
 p=argparse.ArgumentParser();p.add_argument("--changed",type=Path,required=True)
 p.add_argument("--year",type=int,required=True);p.add_argument("--out-dir",type=Path,required=True)
 a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 d=pd.read_csv(a.changed,dtype={"plant_id":"string","nearest_candidate_bus":"string","main_component_candidate_bus":"string"})
 delta=pd.to_numeric(d.distance_increase_km,errors="coerce")
 if delta.isna().any():raise ValueError("Missing distance delta")
 material=d.loc[delta.gt(1)].sort_values("distance_increase_km",ascending=False)
 cols=["plant_id","state","nearest_candidate_bus","main_component_candidate_bus","distance_km_all","distance_km_main","distance_increase_km"]
 material[cols].to_csv(a.out_dir/f"eia860_material_bus_changes_{a.year}.csv",index=False)
 report={"year":a.year,"material_changes_over_1km":len(material),
   "affected_plant_ids":material.plant_id.astype(str).tolist(),
   "actual_electrical_connections_verified":0,
   "interpretation":"Candidate geographic change; requires independent interconnection evidence"}
 (a.out_dir/f"eia860_material_bus_changes_{a.year}.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
