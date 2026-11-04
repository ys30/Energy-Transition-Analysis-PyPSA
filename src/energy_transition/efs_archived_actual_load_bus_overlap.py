"""Audit *actual* 2030/2040/2050 PyPSA Load.bus attachments against 55 source-Pd isolated buses.

This examines saved load-bearing NetCDF networks; it does not infer actual
connections from hypothetical state×LAF exposures.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import networkx as nx
import pandas as pd
import numpy as np

def audit(base, networks):
    graph=nx.Graph()
    graph.add_nodes_from(base.buses.index.astype(str))
    for frame in (base.lines,base.transformers):
        for _,r in frame.iterrows():
            a,b=str(r.bus0),str(r.bus1)
            if a not in graph or b not in graph:raise ValueError("Bad source graph endpoint")
            graph.add_edge(a,b)
    isolated=set(nx.isolates(graph))
    buses=base.buses
    required={"Pd","LAF_state","state","v_nom","substation_off"}
    if required-set(buses):raise ValueError("Missing original source columns")
    p=buses.loc[buses.index.astype(str).isin(isolated)].copy()
    p["Pd"]=pd.to_numeric(p.Pd,errors="coerce")
    offshore=p.substation_off.astype("string").str.lower().eq("true").fillna(False)
    source=set(p.index[p.Pd.gt(0)&~offshore].astype(str))
    if len(isolated)!=877 or len(source)!=55:raise ValueError("Archived original source cohort drift")
    allowed_states={"Arizona","California","Colorado","Idaho","Montana","New Mexico",
                    "Nevada","Oregon","Utah","Washington","Wyoming"}
    in_scope=set(buses.loc[list(source)].index[buses.loc[list(source),"state"].isin(allowed_states)].astype(str))
    if len(in_scope)!=53:raise ValueError("Unexpected 53 in-scope source nodes")
    comps=sorted(nx.connected_components(graph),key=len,reverse=True)
    largest=comps[0]
    records=[]
    years=set()
    load_bus_sets=[]
    for year,net in networks:
        if year in years:raise ValueError("Repeated model year")
        years.add(year)
        if set(net.buses.index.astype(str))!=set(buses.index.astype(str)):
            raise ValueError("Load network has changed source bus identities")
        if len(net.snapshots)!=8760:raise ValueError("Load-bearing time axis missing hours")
        if len(net.generators)!=0:raise ValueError("Historical load-only network unexpectedly has generators")
        load_buses=net.loads.bus.astype(str)
        if not load_buses.isin(net.buses.index.astype(str)).all():raise ValueError("Load assigned to absent network bus")
        loads_on_55=net.loads.loc[load_buses.isin(source)]
        loads_on_53=net.loads.loc[load_buses.isin(in_scope)]
        if not net.loads_t.p_set.empty:
            dynamic=net.loads_t.p_set
            if len(dynamic)!=8760 or not set(dynamic.columns).issubset(set(net.loads.index)):
                raise ValueError("Unexpected incomplete or spurious dynamic Load.p_set columns")
            static_only=net.loads.index.difference(dynamic.columns)
            if not static_only.empty and net.loads.loc[static_only,"p_set"].isna().any():
                raise ValueError("Missing dynamic Load.p_set with no static fallback")
            if not static_only.empty and not np.isfinite(net.loads.loc[static_only,"p_set"].to_numpy(dtype=float)).all():
                raise ValueError("Nonfinite static Load.p_set")
            if dynamic.isna().any().any() or not np.isfinite(dynamic.to_numpy(dtype=float)).all():
                raise ValueError("Nonfinite dynamic Load.p_set")
            total=float(dynamic.to_numpy(dtype=float).sum())+8760*float(net.loads.loc[static_only,"p_set"].sum())
            active_dynamic=dynamic.columns.intersection(loads_on_53.index)
            affected=float(dynamic[active_dynamic].to_numpy(dtype=float).sum()) if len(active_dynamic) else 0.
            active_static=static_only.intersection(loads_on_53.index)
            affected+=8760*float(net.loads.loc[active_static,"p_set"].sum())
        else:
            raise ValueError("Archived load-bearing source missing p_set profiles")
        if not np.isfinite(total) or total<=0:raise ValueError("Invalid source demand")
        load_bus_sets.append(set(load_buses))
        records.append({
            "year":int(year),
            "source_Load_components":len(net.loads),
            "dynamic_Load_components":len(dynamic.columns),
            "static_only_Load_components":len(static_only),
            "distinct_Load_bus_count":int(load_buses.nunique()),
            "loads_attached_to_any_of_55_source_zero_degree_positive_pd_buses":int(len(loads_on_55)),
            "loads_attached_to_any_of_53_in_scope_source_zero_degree_positive_pd_buses":int(len(loads_on_53)),
            "annual_EFS_load_mwh_in_actual_archived_network":total,
            "annual_EFS_load_mwh_on_53_positive_pd_zero_degree_buses":affected,
            "load_components_on_line_transformer_graph_zero_degree_buses":int(load_buses.isin(isolated).sum()),
            "load_components_outside_largest_line_transformer_connected_component":int((~load_buses.isin(largest)).sum()),
            "distinct_load_bus_ids":sorted(set(load_buses)),
            "physical_UTC_harmonization_verified":False,
        })
    if years!={2030,2040,2050}:raise ValueError("All three archive years required")
    return {
       "source_base_bus_count":len(buses),
       "source_line_transformer_zero_degree_bus_count":len(isolated),
       "source_positive_pd_zero_degree_bus_count":len(source),
       "within_11_state_EFS_positive_pd_zero_degree_bus_count":len(in_scope),
       "pilot_allocation_rule":"first existing bus for each state and ReEDS zone; not every bus allocated by LAF",
       "actual_source_53_bus_ids_ever_used_as_Load_bus":sorted(set.union(*load_bus_sets)&in_scope),
       "actual_source_55_bus_ids_ever_used_as_Load_bus":sorted(set.union(*load_bus_sets)&source),
       "archived_load_bearing_network_years":records,
       "eleven_state_candidate_network_loads_attached":False,
       "empirical_53_bus_laf_exposure_is_real_served_demand":False,
       "source_full_state_denominator_verified":False,
       "generator_POI_and_dispatch_validated":False,
       "note":"This reads archived seven-state load-only PyPSA pilot nets. Zero direct attachment does not validate the 11-state candidate nor imply source bus removal is safe."
    }

def main():
    import pypsa
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    for year in (2030,2040,2050):
        ap.add_argument(f"--net{year}",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    base=pypsa.Network(str(a.base))
    nets=[(y,pypsa.Network(str(getattr(a,f"net{y}")))) for y in (2030,2040,2050)]
    r=audit(base,nets)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
