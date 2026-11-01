"""Compare unrestricted versus main-connected nearest-bus candidates per actual EIA plant.

Both are geographic *candidates*, never verified electrical attachments.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def compare(old_path,new_path,out):
 a=pd.read_csv(old_path,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
 b=pd.read_csv(new_path,dtype={"plant_id":"string","main_component_candidate_bus":"string"})
 if a.plant_id.duplicated().any() or b.plant_id.duplicated().any():raise ValueError("Duplicate plant")
 joined=a[["plant_id","state","nearest_candidate_bus","distance_km"]].merge(
  b[["plant_id","main_component_candidate_bus","distance_km"]],on="plant_id",how="outer",
  validate="one_to_one",suffixes=("_all","_main"),indicator=True)
 if not joined._merge.eq("both").all():raise ValueError("Changed plant coverage between candidate procedures")
 joined["changed_candidate_bus"]=joined.nearest_candidate_bus.ne(joined.main_component_candidate_bus)
 joined["distance_increase_km"]=joined.distance_km_main-joined.distance_km_all
 if joined.distance_increase_km.lt(-0.05).any():raise ValueError("Connected-only candidate unexpectedly much closer")
 changed=joined[joined.changed_candidate_bus].sort_values("distance_increase_km",ascending=False)
 out.parent.mkdir(parents=True,exist_ok=True)
 changed.drop(columns="_merge").to_csv(out,index=False)
 report={"plants_compared":len(joined),"plants_with_changed_bus":len(changed),
  "changed_bus_fraction":len(changed)/len(joined),
  "changed_bus_distance_increase_median_km":float(changed.distance_increase_km.median()) if len(changed) else 0.0,
  "changed_bus_distance_increase_max_km":float(changed.distance_increase_km.max()) if len(changed) else 0.0,
  "changed_candidate_plant_ids_csv":str(out),"verified_electrical_connections":0,
  "warning":"Both mappings are geographical alternatives, not electrical plant-to-bus assignments."}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--original",required=True,type=Path)
 p.add_argument("--main",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();compare(a.original,a.main,a.out)
