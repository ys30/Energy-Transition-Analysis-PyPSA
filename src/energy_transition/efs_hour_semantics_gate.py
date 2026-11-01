"""Audit EFS LocalHourID temporal semantics before interpreting local hours as UTC.

Critical: ordinal 1..8760 by state does NOT establish a synchronized Western
dispatch snapshot. Do not infer time zones or DST from state abbreviations.
"""
import argparse,json
from pathlib import Path
import pandas as pd

def inspect(input_path):
 df=pd.read_csv(input_path,compression="gzip")
 required={"year","state","reeds_zone","local_hour_id","allocated_mw"}
 if not required.issubset(df.columns):raise ValueError("Missing EFS zonal fields")
 years=sorted(df.year.unique().tolist())
 states=sorted(df.state.unique().tolist())
 issues=[]
 per_year={}
 for year in years:
  subset=df[df.year==year]
  hours=sorted(subset.local_hour_id.unique().tolist())
  if len(hours)!=8760 or hours[0]!=1 or hours[-1]!=8760:
   issues.append(f"{year} has incorrect local hour ordinals")
  duplicate=int(subset.duplicated(["state","reeds_zone","local_hour_id"]).sum())
  if duplicate:issues.append(f"{year} duplicates {duplicate}")
  per_year[str(year)]={"rows":int(len(subset)),"hour_ordinals":len(hours),"duplicates":duplicate}
 if issues:raise ValueError("; ".join(issues))
 return {"years":years,"states":states,"per_year":per_year,
  "local_hour_semantics":"EFS source LocalHourID = ordinal index only",
  "utc_time_aligned":False,"dst_transition_verified":False,
  "state_zone_timezone_crosswalk_verified":False,
  "required_before_grid_congestion_claims":[
   "Document EFS source hour convention and treatment of daylight saving time",
   "Obtain geolocated zone-to-timezone mapping for split-timezone states",
   "Construct and independently validate a simultaneous UTC profile across zones"],
  "time_alignment_gate":"BLOCKED"}

if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--zonal",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();r=inspect(a.zonal);a.out.parent.mkdir(parents=True,exist_ok=True)
 a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
