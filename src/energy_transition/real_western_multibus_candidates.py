"""Inspect a real multi-bus, multi-line neighborhood around an EFS-loaded bus.

This is a topology and physical-parameter readiness audit, not an OPF result.
"""
import argparse,json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd
import pypsa

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--network",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 n=pypsa.Network(str(a.network))
 l=n.lines.copy()
 for key in ("r","x","s_nom"):
  l[key]=pd.to_numeric(l[key],errors="coerce")
 eligible=l.loc[np.isfinite(l.r)&(l.r>=0)&np.isfinite(l.x)&(l.x>0)&np.isfinite(l.s_nom)&(l.s_nom>=100)].copy()
 graph=nx.Graph()
 graph.add_edges_from(zip(eligible.bus0.astype(str),eligible.bus1.astype(str)))
 profiles=n.loads_t.p_set
 seen=[]
 for bus in n.loads.bus:
  bus=str(bus)
  if bus not in graph:continue
  adjacent=list(graph.neighbors(bus))
  local=set([bus]+adjacent)
  subset=eligible.loc[eligible.bus0.isin(local)&eligible.bus1.isin(local)]
  if len(local)<3 or len(subset)<2:continue
  ids=n.loads.index[n.loads.bus==bus]
  energy=float(profiles[ids].sum().sum())
  seen.append({"loaded_bus":bus,"buses":len(local),"real_lines":len(subset),"original_annual_load_mwh":energy,
               "line_ids":[str(i) for i in subset.index[:30]],"line_capacity_min_mva":float(subset.s_nom.min())})
 seen.sort(key=lambda x:(-x["real_lines"],-x["original_annual_load_mwh"]))
 result={"physical_candidate_neighborhoods":len(seen),"top_neighborhoods":seen[:10],
         "selection_minimum_line_rating_mva":100,
         "real_network_parameters":True,"generation_included":False,
         "multi_bus_opf_solved":False}
 a.out.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
