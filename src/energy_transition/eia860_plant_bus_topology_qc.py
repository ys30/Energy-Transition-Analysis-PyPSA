"""Audit proximity candidates against actual Western network topology and ReEDS regions.

This is a geographic screening, not proof of a plant's electrical tie.
"""
import argparse,json
from pathlib import Path
import networkx as nx
import pandas as pd
import pypsa

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--candidates",type=Path,required=True)
 p.add_argument("--network",type=Path,required=True)
 p.add_argument("--out-dir",type=Path,required=True)
 p.add_argument("--year",type=int,required=True)
 a=p.parse_args();a.out_dir.mkdir(parents=True,exist_ok=True)
 d=pd.read_csv(a.candidates,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
 n=pypsa.Network(str(a.network))
 g=nx.Graph();g.add_nodes_from(n.buses.index.astype(str))
 for edges in (n.lines,n.transformers,n.links):
  g.add_edges_from(zip(edges.bus0.astype(str),edges.bus1.astype(str)))
 largest=max(nx.connected_components(g),key=len)
 b=n.buses
 busids=d.nearest_candidate_bus.astype(str)
 if not busids.isin(b.index.astype(str)).all():raise ValueError("Some candidate buses missing from actual grid")
 regions=b.reeds_zone.reindex(busids)
 d["candidate_reeds_zone"]=regions.to_numpy()
 d["candidate_in_largest_component"]=busids.isin(largest)
 d["needs_review"]=d.distance_km.gt(50)|(~d.candidate_in_largest_component)|d.candidate_reeds_zone.isna()
 d["electrical_connection_verified"]=False
 flagged=d[d.needs_review].copy()
 flagged.to_csv(a.out_dir/f"eia860_bus_topology_review_{a.year}.csv",index=False)
 result={"year":a.year,"candidate_plants":len(d),"largest_component_buses":len(largest),
   "candidate_buses_outside_largest_component":int((~d.candidate_in_largest_component).sum()),
   "candidate_regions_missing":int(d.candidate_reeds_zone.isna().sum()),
   "long_distance_candidates":int(d.distance_km.gt(50).sum()),
   "unique_review_plants":len(flagged),"review_csv":str(a.out_dir/f"eia860_bus_topology_review_{a.year}.csv"),
   "plant_ba_to_reeds_zone_verified":False,"electrical_connections_verified":0}
 (a.out_dir/f"eia860_bus_topology_review_{a.year}.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result,indent=2))
if __name__=="__main__":main()
