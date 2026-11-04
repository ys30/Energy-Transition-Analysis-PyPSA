"""Classify line/transformer-isolated Western buses by archived source types.

A degree-zero bus is a graph property, not a real-life electrically isolated
substation. Disaggregate offshore auxiliaries, original zero Pd, LAF nulls,
nominal bus voltages, and whether source Link touches an isolate.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd

def inspect(network):
    buses=network.buses.copy()
    graph=nx.Graph()
    graph.add_nodes_from(buses.index.astype(str))
    for kind,frame in (("Line",network.lines),("Transformer",network.transformers)):
        for _,r in frame.iterrows():
            a,b=str(r.bus0),str(r.bus1)
            if a not in graph or b not in graph:
                raise ValueError("Unexpected archived network branch endpoint")
            graph.add_edge(a,b)
    isolated=set(nx.isolates(graph))
    if not isolated:raise ValueError("No degree-zero nodes to audit")
    b=buses.loc[buses.index.astype(str).isin(isolated)].copy()
    count=len(b)
    if "substation_off" not in b.columns or "Pd" not in b.columns or "LAF_state" not in b.columns:
        raise ValueError("Missing required upstream offshore and source LAF classification fields")
    offshore=b["substation_off"].astype("string").str.lower().eq("true").fillna(False)
    pdv=pd.to_numeric(b.Pd,errors="coerce")
    if pdv.isna().any() or not np.isfinite(pdv.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite source Pd in zero-degree cohort")
    if pdv.lt(0).any():raise ValueError("Unexpected negative bus source Pd")
    null_laf=b.LAF_state.isna()
    generation_count=len(network.generators)
    loads_count=len(network.loads)
    link_touched=set(map(str,network.links.bus0)).union(set(map(str,network.links.bus1)))
    offshore_and_null=int((offshore & null_laf).sum())
    offshore_nonnull=int((offshore & ~null_laf).sum())
    onshore_null=int((~offshore & null_laf).sum())
    onshore_nonnull=int((~offshore & ~null_laf).sum())
    result={
       "original_network_bus_count":len(buses),
       "line_transformer_zero_degree_bus_count":count,
       "offshore_flag_true_zero_degree_count":int(offshore.sum()),
       "offshore_and_null_laf_zero_degree_count":offshore_and_null,
       "offshore_and_nonnull_laf_zero_degree_count":offshore_nonnull,
       "nonoffshore_and_null_laf_zero_degree_count":onshore_null,
       "nonoffshore_and_nonnull_laf_zero_degree_count":onshore_nonnull,
       "zero_degree_zero_pd_count":int(pdv.eq(0).sum()),
       "zero_degree_positive_pd_count":int(pdv.gt(0).sum()),
       "zero_degree_positive_pd_total_mw":float(pdv.loc[pdv.gt(0)].sum()),
       "zero_degree_link_touched_count":int(len(isolated & link_touched)),
       "zero_degree_source_generation_components":sum(str(x) in isolated for x in network.generators.bus) if generation_count else 0,
       "zero_degree_source_load_components":sum(str(x) in isolated for x in network.loads.bus) if loads_count else 0,
       "zero_degree_by_source_state":{str(k):int(v) for k,v in b.state.fillna("MISSING").value_counts().items()} if "state" in b else {},
       "zero_degree_by_voltage_kv":{str(k):int(v) for k,v in b.v_nom.fillna("MISSING").value_counts().items()} if "v_nom" in b else {},
       "missing_laf_source_offshore_count_in_entire_network":int((buses.substation_off.astype("string").str.lower().eq("true").fillna(False) & buses.LAF_state.isna()).sum()),
       "offshore_auxiliaries_are_not_assumed_to_be_the_only_isolates":True,
       "zero_degree_buses_are_real_grid_outages":False,
       "source_utility_electrical_mapping_approved":False,
       "full_western_electric_dispatch_verified":False,
       "note":"Classification of source graph nodes; degree zero does not establish operational islanding or actual grid outages.",
    }
    if sum((offshore_and_null,offshore_nonnull,onshore_null,onshore_nonnull))!=count:
        raise ValueError("Zero-degree offshore/LAF partition not exhaustive")
    if result["zero_degree_zero_pd_count"]+result["zero_degree_positive_pd_count"]!=count:
        raise ValueError("Pd zero/positive count does not conserve source nodes")
    return result

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    report=inspect(pypsa.Network(str(a.network)))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))

if __name__=="__main__":main()
