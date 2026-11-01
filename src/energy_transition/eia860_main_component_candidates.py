"""Measure availability of main-component nearest bus alternatives for plant candidates.

This is only geospatial candidate comparison, not electrical grid connection.
"""
import argparse,json
from pathlib import Path
import numpy as np,pandas as pd,pypsa,networkx as nx
from scipy.spatial import cKDTree
from .eia860_western_network_coverage import standardize

def xyz(lat,lon):
 phi=np.radians(np.asarray(lat,dtype=float));theta=np.radians(np.asarray(lon,dtype=float))
 return np.column_stack([np.cos(phi)*np.cos(theta),np.cos(phi)*np.sin(theta),np.sin(phi)])

def run(plants_path,network_path,out):
 plants=pd.read_csv(plants_path,dtype={"plant_id":"string"})
 n=pypsa.Network(str(network_path));g=nx.Graph();g.add_nodes_from(n.buses.index.astype(str))
 for e in (n.lines,n.transformers,n.links):g.add_edges_from(zip(e.bus0.astype(str),e.bus1.astype(str)))
 main=max(nx.connected_components(g),key=len)
 b=n.buses.copy();b["state_code"]=standardize(b.state)
 b["longitude"]=pd.to_numeric(b.x,errors="coerce");b["latitude"]=pd.to_numeric(b.y,errors="coerce")
 b=b.loc[b.index.astype(str).isin(main)&b.longitude.between(-125,-102)&b.latitude.between(25,50)]
 plants=plants.loc[plants.coordinate_qc.eq("valid")].copy()
 rows=[]
 for state,group in plants.groupby("state"):
  buses=b.loc[b.state_code.eq(state)]
  if buses.empty:continue
  tree=cKDTree(xyz(buses.latitude,buses.longitude))
  distances,indices=tree.query(xyz(group.latitude,group.longitude))
  for (_,r),d,i in zip(group.iterrows(),distances,indices):
   rows.append({"plant_id":str(r.plant_id),"state":state,"main_component_candidate_bus":str(buses.index[int(i)]),
    "distance_km":float(6371.0088*2*np.arcsin(np.clip(d/2,0,1))),
    "reeds_zone":str(buses.iloc[int(i)].reeds_zone),"electrical_connection_verified":False})
 df=pd.DataFrame(rows)
 if df.empty:raise ValueError("No main-component candidates")
 out.parent.mkdir(parents=True,exist_ok=True);df.to_csv(out,index=False)
 report={"candidate_plants":len(df),"main_component_candidate_fraction":len(df)/len(plants),
  "median_main_component_distance_km":float(df.distance_km.median()),
  "over_50km":int(df.distance_km.gt(50).sum()),
  "electrical_connections_verified":0,"actual_generator_assignment_done":False}
 out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--plants",type=Path,required=True)
 p.add_argument("--network",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.plants,a.network,a.out)
