"""Generate auditable same-state proximity CANDIDATES from official plant and real bus coordinates.

Nearest geographical bus is NOT verified generator electrical connectivity.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pypsa
from scipy.spatial import cKDTree
from .eia860_western_network_coverage import standardize

def match(plants_path,network_path,out):
 plants=pd.read_csv(plants_path,dtype={"plant_id":"string"})
 n=pypsa.Network(str(network_path))
 b=n.buses.copy();b["state_code"]=standardize(b.state)
 b["latitude"]=pd.to_numeric(b.y,errors="coerce")
 b["longitude"]=pd.to_numeric(b.x,errors="coerce")
 b=b[b.latitude.between(25,50)&b.longitude.between(-125,-102)]
 p=plants.copy()
 p=p[p.coordinate_qc.eq("valid")&p.latitude.between(25,50)&p.longitude.between(-125,-102)]
 rows=[]
 for state,group in p.groupby("state"):
  buses=b[b.state_code.eq(state)]
  if buses.empty:continue
  # Great-circle nearest neighbor on unit sphere; no planar degree distance assumption.
  def xyz(lat,lon):
   phi=np.radians(np.asarray(lat,dtype=float));theta=np.radians(np.asarray(lon,dtype=float))
   return np.column_stack((np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)))
  tree=cKDTree(xyz(buses.latitude,buses.longitude))
  chord,ii=tree.query(xyz(group.latitude,group.longitude),k=1)
  distances=6371.0088*2*np.arcsin(np.clip(chord/2,0,1))
  for (idx,row),i,d in zip(group.iterrows(),ii,distances):
   bus=buses.iloc[int(i)]
   rows.append({"plant_id":str(row.plant_id),"plant_name":str(row.plant_name) if "plant_name" in row and pd.notna(row.plant_name) else None,"state":state,"nearest_candidate_bus":str(buses.index[int(i)]),
    "distance_km":round(float(d),4),"plant_latitude":float(row.latitude),"plant_longitude":float(row.longitude),
    "bus_latitude":float(bus.latitude),"bus_longitude":float(bus.longitude),
    "assignment_status":"geographic_candidate_only","electrical_connection_verified":False})
 output=pd.DataFrame(rows)
 if output.empty:raise ValueError("No plant/bus same-state coordinate candidate pairs")
 out.parent.mkdir(parents=True,exist_ok=True)
 output.to_csv(out,index=False)
 report={"candidate_pairs":len(output),"states":sorted(output.state.unique().tolist()),
  "median_distance_km":float(output.distance_km.median()),
  "more_than_50km":int((output.distance_km>50).sum()),
  "verified_electrical_connections":0,
  "warning":"Do not inject these candidate buses into empirical dispatch without plant interconnection evidence."}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--plants",type=Path,required=True)
 parser.add_argument("--network",type=Path,required=True)
 parser.add_argument("--out",type=Path,required=True)
 a=parser.parse_args();match(a.plants,a.network,a.out)
