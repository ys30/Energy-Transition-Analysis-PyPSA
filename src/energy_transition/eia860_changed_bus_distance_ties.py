"""Explain changed nearest-bus IDs where geographic distance does not change.
Candidates are never a verified generator-to-bus electrical crosswalk.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(path,out):
 d=pd.read_csv(path,dtype={"plant_id":"string","nearest_candidate_bus":"string","main_component_candidate_bus":"string"})
 needed={"plant_id","distance_km_all","distance_km_main","changed_candidate_bus"}
 if needed-set(d.columns):raise ValueError("Missing comparison columns")
 if d.plant_id.duplicated().any():raise ValueError("Duplicate plants")
 changed=d[d.changed_candidate_bus.astype(str).str.lower().eq("true")].copy()
 diff=changed.distance_km_main-changed.distance_km_all
 if diff.lt(-0.05).any():raise ValueError("Unexpected shorter restriction result")
 report={"plants_compared_in_change_list":len(d),"changed_candidate_bus_count":len(changed),
  "changed_within_10_metres":int(diff.abs().le(0.01).sum()),
  "changed_within_100_metres":int(diff.abs().le(0.1).sum()),
  "changed_over_1km":int(diff.gt(1).sum()),
  "changed_over_5km":int(diff.gt(5).sum()),
  "changed_distance_zero_median_km":float(diff.median()) if len(diff) else 0.0,
  "candidate_id_change_not_proof_of_new_electrical_connection":True,
  "verified_generator_bus_connections":0}
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--changed",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();audit(a.changed,a.out)
