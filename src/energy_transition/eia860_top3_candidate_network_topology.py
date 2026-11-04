"""Read-only network topology audit for distant EIA-860 plant candidate buses.

Quantifies real archived network branch incidence, adjacent buses and component
sizes. This DOES NOT verify facility POIs, line voltages, or electrical loading.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

TARGETS=("2053003","2053000","2077001")


def topology_review(network, plants:pd.DataFrame)->dict:
    buses=network.buses.copy()
    bus_names=buses.index.astype(str)
    if len(bus_names)!=len(set(bus_names)):
        raise ValueError("Duplicate source bus identities")
    graph=nx.Graph()
    graph.add_nodes_from(bus_names)
    edges={}
    for kind,frame in (("lines",network.lines),("transformers",network.transformers)):
        if not {"bus0","bus1"}.issubset(frame.columns):
            raise ValueError("Network is missing archived branch endpoints")
        edges[kind]=[]
        for branch,row in frame.iterrows():
            a,b=str(row.bus0),str(row.bus1)
            if a not in graph or b not in graph:
                raise ValueError("Branch points to missing archived network bus")
            graph.add_edge(a,b)
            edges[kind].append((a,b,str(branch)))
    required={"plant_id","nearest_candidate_bus","distance_km","operating_nameplate_mw",
              "plant_latitude","plant_longitude","bus_latitude","bus_longitude"}
    if not required.issubset(plants.columns):
        raise ValueError("Official EIA plant coordinate evidence missing")
    p=plants.copy()
    p["nearest_candidate_bus"]=p.nearest_candidate_bus.astype("string").str.strip()
    p["plant_id"]=p.plant_id.astype("string").str.strip()
    if p.plant_id.duplicated().any() or p.plant_id.isna().any() or len(p)!=63:
        raise ValueError("Unexpected archived 63 EIA plant audit cohort")
    if not p.nearest_candidate_bus.isin(bus_names).all():
        raise ValueError("Candidate bus not present in source network")
    for v in ("distance_km","operating_nameplate_mw","plant_latitude",
              "plant_longitude","bus_latitude","bus_longitude"):
        p[v]=pd.to_numeric(p[v],errors="coerce")
        if not np.isfinite(p[v].to_numpy(dtype=float)).all():raise ValueError("Invalid source geographic data")
    if not p.distance_km.gt(50).all() or not p.operating_nameplate_mw.gt(0).all():
        raise ValueError("Must use screened >50 km 2024 operating plants")
    if set(TARGETS)-set(bus_names):
        raise ValueError("Three previously verified synthetic nodes not in source")
    if set(TARGETS)-set(p.nearest_candidate_bus):
        raise ValueError("Missing required high-priority plant collision group")
    components=list(nx.connected_components(graph))
    component_by_bus={bus:(i,len(c)) for i,c in enumerate(components) for bus in c}
    results=[]
    for target in TARGETS:
        row=buses.loc[bus_names==target].iloc[0]
        pts=p.loc[p.nearest_candidate_bus.eq(target)]
        if pts.empty:raise ValueError("Missing candidate-source plants")
        topological_neighbors=sorted(graph.neighbors(target))
        incidence={}
        branch_samples={}
        for kind,items in edges.items():
            connected=[{"branch_id":eid,"opposite_bus":b if a==target else a}
                       for a,b,eid in items if a==target or b==target]
            incidence[kind]=len(connected)
            branch_samples[kind]=connected[:15]
        fields={}
        for name in ("x","y","state","reeds_state","reeds_zone","v_nom","county"):
            if name in buses.columns:
                value=row[name]
                fields[name]=None if pd.isna(value) else (
                    float(value) if isinstance(value,(float,np.floating))
                    else str(value))
        if "x" in fields and "y" in fields:
            lat=float(fields["y"]);lon=float(fields["x"])
            if not np.allclose(pts.bus_latitude,lat,atol=1e-5,rtol=0) or not np.allclose(pts.bus_longitude,lon,atol=1e-5,rtol=0):
                raise ValueError(f"Archived GIS candidate bus coordinate drift: {target}")
        results.append({
            "synthetic_candidate_bus_id":target,
            "bus_attributes":fields,
            "candidate_2024_operating_plants":int(len(pts)),
            "candidate_2024_operating_units":int(pd.to_numeric(pts.generator_count).sum()) if "generator_count" in pts else None,
            "candidate_historical_nameplate_mw":float(pts.operating_nameplate_mw.sum()),
            "maximum_geographical_assignment_km":float(pts.distance_km.max()),
            "median_geographical_assignment_km":float(pts.distance_km.median()),
            "archived_line_count":incidence["lines"],
            "archived_transformer_count":incidence["transformers"],
            "distinct_topological_neighbors":len(topological_neighbors),
            "neighbor_bus_ids":topological_neighbors[:30],
            "branch_examples":branch_samples,
            "line_transformer_graph_component_size_buses":int(component_by_bus[target][1]),
            "all_2024_plants_source_region_labels":sorted(set(pts.state.astype(str))) if "state" in pts else [],
            "all_2024_plants_source_BA_labels":sorted(set(pts.ba_code.astype(str))) if "ba_code" in pts else [],
            "independent_electrical_POI_verification":False,
        })
    return {
        "archived_network_bus_count":len(buses),
        "archived_network_line_count":len(network.lines),
        "archived_network_transformer_count":len(network.transformers),
        "line_transformer_graph_connected_component_count":len(components),
        "line_transformer_graph_isolated_bus_count":sum(graph.degree(x)==0 for x in graph.nodes),
        "network_link_count_not_in_graph":len(network.links) if hasattr(network,"links") else 0,
        "connectivity_scope":"Line + Transformer graph only; PyPSA Link components are not included, so this is not an all-component electrical connectivity or islanding result.",
        "source_plant_cohort_count":len(p),
        "source_plant_historical_nameplate_mw":float(p.operating_nameplate_mw.sum()),
        "source_candidate_bus_count":int(p.nearest_candidate_bus.nunique()),
        "audited_top_candidate_buses":results,
        "real_utility_POI_connections_verified":0,
        "topology_used_for_electrical_admission":False,
        "future_2030_2050_generation_dispatch_admitted":False,
        "note":"Graph incidence is from a synthetic-topology-derived archive; links to nearest geographic source buses are NOT authenticated plant substation or POI connections.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",required=True,type=Path)
    p.add_argument("--named-plants",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    network=pypsa.Network(str(a.network))
    plants=pd.read_csv(a.named_plants,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    report=topology_review(network,plants)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="audited_top_candidate_buses"},indent=2))
    for d in report["audited_top_candidate_buses"]:
        print(json.dumps({k:v for k,v in d.items() if k!="branch_examples"},indent=2))

if __name__=="__main__":main()
