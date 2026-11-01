"""Audit real Western PyPSA AC/DC network connectivity before constrained optimization.

Topology diagnostics only; no fabricated line reactances or generation data.
"""
import argparse
import json
from pathlib import Path
import networkx as nx
import pypsa


def inspect(path: Path):
    n=pypsa.Network(str(path))
    graph=nx.Graph()
    graph.add_nodes_from(map(str,n.buses.index))
    edge_types={}
    for kind,df in (("Line",n.lines),("Transformer",n.transformers),("Link",n.links)):
        valid=df.loc[df.bus0.ne("") & df.bus1.ne("")]
        graph.add_edges_from((str(a),str(b)) for a,b in zip(valid.bus0,valid.bus1))
        edge_types[kind]=len(valid)
    components=sorted((len(x) for x in nx.connected_components(graph)),reverse=True)
    if sum(components)!=len(n.buses):raise ValueError("Topology accounting inconsistent")
    return {"buses":len(n.buses),"edges_by_type":edge_types,
            "connected_components":len(components),
            "largest_component_buses":components[0],
            "isolated_buses":sum(1 for size in components if size==1),
            "top_component_sizes":components[:25],
            "all_branch_endpoints_accounted":True,
            "observed_topology":True,
            "network_constrained_optimization_solved":False,
            "generation_assets_verified":False,
            "note":"Links included for connectivity audit; this does not establish electrical AC feasibility."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=inspect(a.network)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
