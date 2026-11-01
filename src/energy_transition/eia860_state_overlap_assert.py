"""Validate geographic overlap without mistaking state coincidence for generator-bus assignment."""
import argparse,json
from pathlib import Path
import pandas as pd

def audit(path):
 r=json.loads(Path(path).read_text())
 overlap=r["states_in_both"]
 if len(overlap)<10:raise ValueError(f"Unexpected EIA-Western network state overlap: {overlap}")
 rows=r["state_comparison"]
 checked=[x for x in rows if x["network_and_generator_state_overlap"]]
 if any(x["actual_network_buses"]<=0 or x["operating_generators"]<=0 for x in checked):
  raise ValueError("Reported overlap includes absent generators or buses")
 return {"overlap_states":overlap,"count":len(overlap),
         "operating_generator_rows_in_overlap":sum(x["operating_generators"] for x in checked),
         "nameplate_mw_in_overlap":sum(x["operating_nameplate_mw"] for x in checked),
         "real_network_buses_in_overlap":sum(x["actual_network_buses"] for x in checked),
         "generator_bus_assignment_done":False,
         "plant_coordinates_required":True,
         "verified_feasibility":"State-level coverage only"}
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--coverage-json",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path);a=p.parse_args()
 result=audit(a.coverage_json);a.out.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
