"""Audit geographic plant-to-bus candidates; do not claim actual connections."""
import argparse,json
from pathlib import Path
import pandas as pd

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--candidates",type=Path,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 p.add_argument("--year",type=int,required=True)
 a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 d=pd.read_csv(a.candidates,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
 required={"plant_id","state","nearest_candidate_bus","distance_km","assignment_status","electrical_connection_verified"}
 if required-set(d):raise ValueError("Missing candidate fields")
 if d.plant_id.duplicated().any():raise ValueError("Duplicate candidate plant IDs")
 # CSV boolean strings must not be interpreted by Python string truthiness.
 flags=d.electrical_connection_verified.astype("string").str.strip().str.lower()
 if flags.isna().any() or not flags.isin(["true","false"]).all():
  raise ValueError("Invalid electrical connection verification flags")
 if not d.assignment_status.eq("geographic_candidate_only").all() or flags.eq("true").any():
  raise ValueError("Proximity candidates incorrectly marked as electrical connections")
 if d.nearest_candidate_bus.isna().any() or d.plant_id.isna().any() or d.plant_id.duplicated().any():
  raise ValueError("Missing or duplicate candidate identifiers")
 d["distance_km"]=pd.to_numeric(d.distance_km,errors="coerce")
 if d.distance_km.isna().any() or not d.distance_km.map(__import__("math").isfinite).all() or d.distance_km.lt(0).any():
  raise ValueError("Invalid distances")
 d["distance_band"]=pd.cut(d.distance_km,[-0.001,1,5,10,25,50,float("inf")],labels=["0-1","1-5","5-10","10-25","25-50",">50"])
 flagged=d[d.distance_km>50].sort_values("distance_km",ascending=False)
 flagged.to_csv(a.out_dir/f"eia860_plant_bus_long_distance_review_{a.year}.csv",index=False)
 report={"year":a.year,"candidate_plants":len(d),"distance_quantiles_km":{str(q):float(d.distance_km.quantile(q)) for q in (0.5,0.9,0.95,0.99)},
   "distance_band_counts":{str(k):int(v) for k,v in d.distance_band.value_counts(dropna=False).items()},
   "over_50km_count":len(flagged),"over_50km_fraction":len(flagged)/len(d),
   "electrical_connections_verified":0,"plant_bus_assignment_approved":False,
   "warning":"Geography alone is not an electrical plant-bus crosswalk."}
 (a.out_dir/f"eia860_plant_bus_distance_qc_{a.year}.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
