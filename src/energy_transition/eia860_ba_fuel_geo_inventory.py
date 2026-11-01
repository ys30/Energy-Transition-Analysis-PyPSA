"""Produce official operating EIA-860 capacity by BA and fuel, with geographic evidence flags.

No BA-to-ReEDS mapping, hourly deliverability, or generator-bus connection is inferred.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def build(generators,plants,year,out):
 g=pd.read_csv(generators,dtype={"plant_id":"string","generator_id":"string","ba_code":"string"})
 p=pd.read_csv(plants,dtype={"plant_id":"string"})
 required={"plant_id","generator_id","ba_code","state","fuel","capacity_mw","status","crosswalk_status"}
 if required-set(g):raise ValueError("Missing official generator columns")
 op=g.loc[g.status.astype("string").str.strip().str.upper().eq("OP")&
          g.crosswalk_status.eq("matched")].copy()
 op.capacity_mw=pd.to_numeric(op.capacity_mw,errors="coerce")
 op=op[op.capacity_mw.ge(0)&op.capacity_mw.notna()]
 if op.duplicated(["plant_id","generator_id"]).any():raise ValueError("Duplicate operating gen IDs")
 if p.duplicated("plant_id").any():raise ValueError("Duplicate EIA location plant IDs")
 p=p[["plant_id","coordinate_qc"]]
 op=op.merge(p,on="plant_id",how="left",validate="many_to_one")
 op["verified_geographic_coordinate"]=op.coordinate_qc.eq("valid")
 out.parent.mkdir(parents=True,exist_ok=True)
 groups=op.groupby(["ba_code","fuel"],dropna=False).agg(
  official_nameplate_mw=("capacity_mw","sum"),
  operating_generators=("generator_id","size"),
  plants=("plant_id","nunique"),
  generators_with_coordinate=("verified_geographic_coordinate","sum")).reset_index()
 groups["year"]=year
 groups["actual_bus_assignment_verified"]=False
 groups["hourly_availability_verified"]=False
 groups["fuel_cost_verified"]=False
 groups.to_csv(out,index=False)
 report={"year":year,"ba_fuel_groups":len(groups),"operating_generators":len(op),
   "operating_nameplate_mw":float(op.capacity_mw.sum()),
   "generators_with_official_plant_coordinates":int(op.verified_geographic_coordinate.sum()),
   "generators_missing_plant_coordinates":int((~op.verified_geographic_coordinate).sum()),
   "ba_groups":int(op.ba_code.nunique()),
   "generator_bus_connections_verified":0,
   "note":"Official BA+fuel nameplate inventory only: cannot serve as calibrated dispatch capacity."}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 a=argparse.ArgumentParser();a.add_argument("--generators",required=True,type=Path)
 a.add_argument("--plants",required=True,type=Path);a.add_argument("--year",required=True,type=int)
 a.add_argument("--out",required=True,type=Path);v=a.parse_args()
 build(v.generators,v.plants,v.year,v.out)
