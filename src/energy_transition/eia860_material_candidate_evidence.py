"""Enrich materially shifted plant candidate rows with official BA and network ReEDS facts.

Evidence only: neither geographic nearest bus is a verified electrical tie.
"""
import argparse,json
from pathlib import Path
import pandas as pd,pypsa

def main():
 p=argparse.ArgumentParser()
 for name in ("material","plant-ba","network","out"):p.add_argument("--"+name,required=True,type=Path)
 p.add_argument("--year",required=True,type=int)
 a=p.parse_args()
 d=pd.read_csv(a.material,dtype={"plant_id":"string","nearest_candidate_bus":"string","main_component_candidate_bus":"string"})
 plants=pd.read_csv(a.plant_ba,dtype={"plant_id":"string","ba_code":"string"})
 valid=plants.loc[plants.crosswalk_qc.eq("valid"),["plant_id","ba_code","state"]].drop_duplicates()
 conflicts=valid.groupby("plant_id").ba_code.nunique()
 if (conflicts>1).any():raise ValueError("Conflicting valid plant BA codes")
 valid=valid.drop_duplicates("plant_id")
 out=d.merge(valid,on="plant_id",how="left",validate="one_to_one",suffixes=("","_official"))
 net=pypsa.Network(str(a.network))
 for tag,col in (("original","nearest_candidate_bus"),("main","main_component_candidate_bus")):
  for feature in ("reeds_zone","state","x","y"):
   out[f"{tag}_bus_{feature}"]=out[col].map(net.buses[feature])
 out["same_reeds_zone"]=out.original_bus_reeds_zone.eq(out.main_bus_reeds_zone)
 out["electrical_connection_verified"]=False
 a.out.parent.mkdir(parents=True,exist_ok=True)
 out.to_csv(a.out,index=False)
 report={"year":a.year,"material_plants":len(out),"plant_ids":out.plant_id.tolist(),
  "plant_ba_available":int(out.ba_code.notna().sum()),
  "original_and_main_same_reeds_zone":int(out.same_reeds_zone.sum()),
  "electrical_connections_verified":0,
  "note":"BA and ReEDS labels are descriptive; no unverified BA-to-ReEDS crosswalk is inferred."}
 a.out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
