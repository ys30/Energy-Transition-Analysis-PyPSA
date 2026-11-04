"""Read-only topology scope audit for the pinned Western PyPSA-USA network.

Compares Line+Transformer and Line+Transformer+Link UNDIRECTED graph
connectivity, while making no claim that all Links are passive AC branches
or that graph connectivity proves electrical feasibility.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

TARGETS=("2053003","2053000","2077001")


def audit_link_scope(network)->dict:
    buses=network.buses
    names=set(buses.index.astype(str))
    if not names:raise ValueError("No source bus inventory")
    graph=nx.Graph()
    graph.add_nodes_from(names)
    per_component={}
    links=[]
    for family,table in (("Line",network.lines),("Transformer",network.transformers),("Link",network.links)):
        if not {"bus0","bus1"}.issubset(table):
            raise ValueError(f"{family} endpoints are not present")
        edges=[]
        for idx,row in table.iterrows():
            start,end=str(row.bus0),str(row.bus1)
            if start not in names or end not in names:raise ValueError(f"{family} references absent node")
            edges.append((start,end))
            if family=="Link":
                record={"link_id":str(idx),"bus0":start,"bus1":end}
                for col in ("carrier","p_nom","p_min_pu","p_max_pu","efficiency"):
                    if col in row.index:
                        value=row[col]
                        if pd.isna(value):record[col]=None
                        elif col=="carrier":record[col]=str(value)
                        else:
                            num=float(value)
                            record[col]=num if np.isfinite(num) else None
                links.append(record)
            else:graph.add_edge(start,end)
        per_component[family]=edges
    base_components=nx.number_connected_components(graph)
    base_isolates=sum(1 for node,degree in graph.degree if degree==0)
    base_sizes={node:len(comp) for comp in nx.connected_components(graph) for node in comp}
    base_target_degrees={node:int(graph.degree(node)) for node in TARGETS}
    before_isolates=set(nx.isolates(graph))
    graph.add_edges_from(per_component["Link"])
    link_components=nx.number_connected_components(graph)
    link_isolates=set(nx.isolates(graph))
    if not set(TARGETS).issubset(names):
        raise ValueError("Missing three high-priority source bus identities")
    link_endpoint_count=len({a for edge in per_component["Link"] for a in edge})
    result={
        "source_bus_count":len(names),
        "source_line_count":len(per_component["Line"]),
        "source_transformer_count":len(per_component["Transformer"]),
        "source_link_count":len(per_component["Link"]),
        "source_link_endpoints_unique_bus_count":link_endpoint_count,
        "source_links":links,
        "line_transformer_component_count":base_components,
        "line_transformer_degree_zero_bus_count":base_isolates,
        "undirected_all_branch_types_component_count":link_components,
        "undirected_all_branch_types_degree_zero_bus_count":len(link_isolates),
        "zero_degree_bus_reduction_after_link_edges":base_isolates-len(link_isolates),
        "number_of_originally_isolated_buses_touched_by_links":len(before_isolates & {a for edge in per_component["Link"] for a in edge}),
        "high_risk_candidates":[{
            "bus":target,
            "line_transformer_degree":base_target_degrees[target],
            "additional_incident_links":sum(target in edge for edge in per_component["Link"]),
            "undirected_all_branch_types_degree":int(graph.degree(target)),
            "line_transformer_component_size_buses":int(base_sizes[target]),
            "undirected_all_branch_types_component_size_buses":next(len(comp) for comp in nx.connected_components(graph) if target in comp),
            "real_electrical_poi_verified":False,
        } for target in TARGETS],
        "network_has_generator_components":len(network.generators)>0,
        "link_treated_as_undirected_edge_only_for_topological_sensitivity":True,
        "link_direction_and_operational_limits_analyzed":False,
        "full_electrical_network_islanding_certified":False,
        "empirical_2030_2050_generation_dispatch_admitted":False,
        "note":"Graph component counts are descriptive topology diagnostics, not actual grid islands or reliable electrical transfer. Link behavior may be directional or non-AC; no source POI is certified.",
    }
    if result["undirected_all_branch_types_component_count"]>base_components:
        raise ValueError("Adding link edges cannot increase component count")
    if result["undirected_all_branch_types_degree_zero_bus_count"]>base_isolates:
        raise ValueError("Adding link edges cannot increase isolate count")
    return result


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    report=audit_link_scope(pypsa.Network(str(a.network)))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))

if __name__=="__main__":
    main()
