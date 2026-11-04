"""Audit actual EFS 2030 seven-state representative Load bus selection against zone alternatives.

The original pilot picks the first source bus per exported state/ReEDS zone.
This audits that choice, without changing the attached demand or treating
topology/source Pd as proof of utility-certified delivery points.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx

def audit(base,load_net):
    b=base.buses.copy()
    n=load_net
    required={"state","reeds_zone","Pd","LAF_state","v_nom","substation_off"}
    if required-set(b):raise ValueError("Missing source bus attributes")
    if set(b.index.astype(str))!=set(n.buses.index.astype(str)):raise ValueError("Original bus cohort changed")
    graph=nx.Graph()
    graph.add_nodes_from(b.index.astype(str))
    for table in (base.lines,base.transformers):
        for _,r in table.iterrows():
            graph.add_edge(str(r.bus0),str(r.bus1))
    if not all(node in graph for node in b.index.astype(str)):raise ValueError("Network source mismatch")
    main=max(nx.connected_components(graph),key=len)
    entries=[]
    for load,row in n.loads.iterrows():
        target=str(row.bus)
        if target not in b.index:raise ValueError("Unknown Load target")
        source=b.loc[target]
        match=b.loc[b.state.eq(source.state)&b.reeds_zone.eq(source.reeds_zone)].copy()
        if len(match)==0:raise ValueError("Missing source zone")
        first_id=str(match.index[0])
        pd_values=pd.to_numeric(match.Pd,errors="coerce")
        laf_values=pd.to_numeric(match.LAF_state,errors="coerce")
        positive=pd_values.gt(0)&np.isfinite(pd_values.to_numpy(dtype=float))
        connected=pd.Index(match.index.astype(str)).isin(main)
        admissible=positive.to_numpy()&connected
        v_nom=float(source.v_nom)
        target_pd=float(source.Pd)
        target_laf=float(source.LAF_state) if pd.notna(source.LAF_state) else None
        entries.append({
          "Load_id":str(load),"selected_bus_id":target,
          "exported_state":str(source.state),"reeds_zone":str(source.reeds_zone),
          "selected_bus_matches_pilot_first_bus":target==first_id,
          "zone_source_bus_count":len(match),
          "zone_connected_positive_pd_candidate_count":int(admissible.sum()),
          "zone_total_positive_pd_count":int(positive.sum()),
          "selected_source_nominal_voltage_kv":v_nom,
          "selected_source_pd_mw":target_pd,
          "selected_source_laf_state":target_laf,
          "selected_positive_source_pd":target_pd>0,
          "selected_line_transformer_degree":int(graph.degree(target)),
          "selected_in_main_line_transformer_component":target in main,
          "selected_substation_off_source_flag":str(source.substation_off).lower()=="true",
          "selected_source_is_utility_certified_load_delivery_point":False,
        })
    if not entries:raise ValueError("No saved EFS loads to audit")
    df=pd.DataFrame(entries)
    report={
      "archived_original_buses":len(b),
      "archived_EFS_loads":len(n.loads),
      "all_Load_targets_match_first_source_bus_per_zone":bool(df.selected_bus_matches_pilot_first_bus.all()),
      "selected_zero_original_pd_Load_count":int((~df.selected_positive_source_pd).sum()),
      "selected_zero_line_transformer_degree_Load_count":int((df.selected_line_transformer_degree==0).sum()),
      "selected_outside_main_line_transformer_component_Load_count":int((~df.selected_in_main_line_transformer_component).sum()),
      "selected_offshore_flagged_Load_count":int(df.selected_substation_off_source_flag.sum()),
      "zones_with_connected_positive_pd_alternatives":int(df.zone_connected_positive_pd_candidate_count.gt(0).sum()),
      "zone_representation_is_utility_certified":False,
      "pilot_uses_source_pd_weighted_bus_allocation":False,
      "full_11_state_efs_network_validated":False,
      "actual_UTC_compatibility_verified":False,
      "no_generator_dispatch_solved":True,
      "note":"Actual source first-bus representative Load placement. Positive Pd, connectivity or voltage is not sufficient to validate electrical delivery location.",
    }
    return df,report

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--base",type=Path,required=True)
    p.add_argument("--load-network",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    df,report=audit(pypsa.Network(str(a.base)),pypsa.Network(str(a.load_network)))
    a.out_dir.mkdir(parents=True,exist_ok=True)
    df.to_csv(a.out_dir/"efs_2030_actual_representative_load_bus_selection.csv",index=False)
    (a.out_dir/"efs_2030_actual_representative_load_bus_summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    print(df[["Load_id","selected_bus_id","selected_source_nominal_voltage_kv",
              "selected_source_pd_mw","selected_line_transformer_degree",
              "zone_connected_positive_pd_candidate_count"]].to_string(index=False))
if __name__=="__main__":main()
