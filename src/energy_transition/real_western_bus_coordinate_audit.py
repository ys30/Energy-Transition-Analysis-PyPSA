"""Check real Western bus coordinates needed for auditable power-plant proximity matching.

No assignments are generated: nearest-bus alone does not prove electrical interconnection.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pypsa

def audit(network):
 n=pypsa.Network(str(network)); b=n.buses
 for col in ("x","y","state"):
  if col not in b.columns:raise ValueError(f"Bus field absent: {col}")
 lon=pd.to_numeric(b.x,errors="coerce");lat=pd.to_numeric(b.y,errors="coerce")
 valid=lon.between(-125,-102)&lat.between(25,50)
 labeled=b.state.notna()&b.state.astype(str).str.strip().ne("")
 rows=[]
 for state,group in b.groupby("state",dropna=False):
  ix=group.index
  rows.append({"state":str(state),"buses":len(ix),
    "valid_coordinate_buses":int(valid.loc[ix].sum()),
    "missing_or_invalid_coordinates":int((~valid.loc[ix]).sum())})
 result={"network_buses":len(b),"valid_geographic_coordinates":int(valid.sum()),
  "missing_invalid_geographic_coordinates":int((~valid).sum()),
  "state_labeled_buses":int(labeled.sum()),"state_counts":rows,
  "coordinate_units":"assumed longitude/latitude degrees, not yet independently CRS-verified",
  "real_generator_coordinates_available_in_this_network":False,
  "plant_to_bus_assignment_verified":False,
  "warning":"Geographic proximity alone cannot establish electrical bus connection."}
 if not valid.any():raise ValueError("No geographically plausible bus coordinates")
 return result

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--network",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();r=audit(a.network);a.out.write_text(json.dumps(r,indent=2)+"\n")
 print(json.dumps({"network_buses":r["network_buses"],"valid_geographic_coordinates":r["valid_geographic_coordinates"],"plant_to_bus_assignment_verified":False},indent=2))
