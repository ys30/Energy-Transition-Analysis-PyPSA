"""Audit where verified EFS loads land in actual connected Western grid.

No generation or line physics is invented. This is a mandatory feasibility
screen before transmission-constrained optimization.
"""
import argparse,json
from pathlib import Path
from collections import Counter,defaultdict
import networkx as nx
import pypsa

def audit(path:Path):
 n=pypsa.Network(str(path))
 g=nx.Graph();g.add_nodes_from(n.buses.index)
 for frame in (n.lines,n.transformers,n.links):
  g.add_edges_from(zip(frame.bus0,frame.bus1))
 components=sorted(nx.connected_components(g),key=len,reverse=True)
 main=set(components[0]); loads=n.loads
 main_load=loads[loads.bus.isin(main)]
 other=loads[~loads.bus.isin(main)]
 per_state=Counter(n.buses.loc[other.bus,"state"]) if not other.empty else Counter()
 total=float(n.loads_t.p_set.sum().sum())
 excluded=float(n.loads_t.p_set[other.index].sum().sum()) if len(other) else 0.0
 return {"year":int(str(n.snapshots[0].year)),"total_load_components":len(loads),
         "main_component_buses":len(main),"outside_main_load_components":len(other),
         "outside_main_load_mwh":excluded,"total_load_mwh":total,
         "outside_main_share":excluded/total if total else None,
         "outside_main_load_states":dict(per_state),
         "transmission_solve_ready":len(other)==0,
         "network_topology_real":True,"generation_source_validated":False,
         "note":"No generation or dispatch inferred; main-component screening only."}
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--network",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();r=audit(a.network)
 a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r,indent=2))
