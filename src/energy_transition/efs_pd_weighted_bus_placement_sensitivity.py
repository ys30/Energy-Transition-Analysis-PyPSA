"""Read-only comparison of two source-based EFS zonal Load placement rules.

Original archive: one Load at first indexed state x ReEDS-zone bus.
Counterfactual: distribute that zone's same hourly time series across
MAIN LINE/TRANSFORMER graph buses with positive original Pd, proportionally
to original Pd. No extra electricity, no source files rewritten, and no OPF.
One zero-candidate zone stays at original representative bus and is flagged.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd

def compare(base,loaded):
    buses=base.buses
    required={"state","reeds_zone","Pd","v_nom","substation_off"}
    if required-set(buses):
        raise ValueError("Missing original source bus columns")
    if set(buses.index.astype(str))!=set(loaded.buses.index.astype(str)):
        raise ValueError("Original bus identity changed")
    graph=nx.Graph()
    graph.add_nodes_from(buses.index.astype(str))
    for frame in (base.lines,base.transformers):
        for _,r in frame.iterrows():
            a,z=str(r.bus0),str(r.bus1)
            if a not in graph or z not in graph: raise ValueError("Unknown source branch endpoint")
            graph.add_edge(a,z)
    main=max(nx.connected_components(graph),key=len)
    if len(loaded.snapshots)!=8760 or len(loaded.loads)!=20 or len(loaded.generators):
        raise ValueError("Expected original 2030 EFS load-only pilot")
    dynamic=loaded.loads_t.p_set
    if len(dynamic)!=8760 or not set(dynamic.columns).issubset(set(loaded.loads.index)):
        raise ValueError("Incomplete archived dynamic load source")
    static=loaded.loads.index.difference(dynamic.columns)
    if not set(static).issubset(set(loaded.loads.index)):raise ValueError("Invalid static load IDs")
    if dynamic.isna().any().any() or not np.isfinite(dynamic.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite real archived hourly EFS loads")
    if not np.isfinite(pd.to_numeric(loaded.loads.p_set,errors="coerce").to_numpy()).all():
        raise ValueError("Missing non-dynamic static Load.p_set")
    if (dynamic.to_numpy(dtype=float)<0).any() or (pd.to_numeric(loaded.loads.p_set)<0).any():
        raise ValueError("Negative load incompatible with positive-Pd distribution")
    row_outputs=[]
    full_original=np.zeros(8760,dtype=float)
    full_candidate=np.zeros(8760,dtype=float)
    for load,record in loaded.loads.iterrows():
        target=str(record.bus)
        if target not in buses.index:raise ValueError("Non-source load bus")
        source=buses.loc[target]
        candidates=buses.loc[buses.state.eq(source.state)&buses.reeds_zone.eq(source.reeds_zone)].copy()
        if str(candidates.index[0])!=target:raise ValueError("Pilot selection rule drift")
        p=pd.to_numeric(candidates.Pd,errors="coerce")
        if (p.dropna()<0).any() or not np.isfinite(p.dropna().to_numpy()).all():
            raise ValueError("Invalid original candidate Pd")
        good=(p.gt(0)&p.notna()&pd.Index(candidates.index.astype(str)).isin(main))
        positive=candidates.loc[good].copy()
        original_hour=(dynamic[load].to_numpy(dtype=float) if load in dynamic else
                       np.full(8760,float(loaded.loads.loc[load,"p_set"]),dtype=float))
        if not np.isfinite(original_hour).all() or (original_hour<0).any():
            raise ValueError("Invalid source hour time series")
        weight=pd.to_numeric(positive.Pd).to_numpy(dtype=float)
        if len(weight) and weight.sum()>0:
            shares=weight/weight.sum()
            chosen=list(positive.index.astype(str))
            fallback=False
        else:
            shares=np.array([1.0]);chosen=[target];fallback=True
        if not np.isclose(shares.sum(),1.,atol=1e-12,rtol=0):
            raise ValueError("Counterfactual zone weights do not conserve load")
        reconstructed=original_hour*float(shares.sum())
        if not np.allclose(original_hour,reconstructed,atol=1e-8,rtol=1e-13):
            raise ValueError("Hourly EFS source conservation failed")
        full_original+=original_hour
        full_candidate+=reconstructed
        candidate_at_old=float(shares[chosen.index(target)]) if target in chosen else 0.0
        shifted_share=1.0-candidate_at_old
        row_outputs.append({
           "Load_id":str(load),
           "source_zone_state":str(source.state),
           "source_zone":str(source.reeds_zone),
           "original_bus_id":target,
           "original_bus_Pd":float(source.Pd),
           "original_bus_voltage_kv":float(source.v_nom),
           "original_bus_in_main_graph":target in main,
           "positive_pd_main_component_candidate_count":int(len(positive)),
           "candidate_bus_count_after_fallback":int(len(chosen)),
           "candidate_pd_source_weight_sum":float(weight.sum()) if not fallback else 0.0,
           "fallback_original_bus_no_positive_pd_candidate":fallback,
           "candidate_buses_source_ids":";".join(chosen),
           "candidate_bus_pd_shares":";".join(f"{z:.12g}" for z in shares),
           "candidate_share_remaining_at_original_bus":candidate_at_old,
           "share_of_zone_load_relocated_from_original_bus":shifted_share,
           "original_zone_annual_mwh":float(original_hour.sum()),
           "candidate_zone_annual_mwh":float(reconstructed.sum()),
           "candidate_zone_synthetic_relocation_mwh":float(original_hour.sum()*shifted_share),
           "utility_certified_load_location":False,
        })
    if not np.allclose(full_original,full_candidate,rtol=1e-12,atol=1e-6):
        raise ValueError("Full system hourly total load not conserved")
    d=pd.DataFrame(row_outputs)
    if not d.original_bus_in_main_graph.all():raise ValueError("Source Load target is not on main graph")
    total=float(d.original_zone_annual_mwh.sum())
    moved=float(d.candidate_zone_synthetic_relocation_mwh.sum())
    result={
       "source_original_network_buses":int(len(buses)),
       "source_original_2030_loads":int(len(loaded.loads)),
       "original_loads_with_zero_pd_source_bus":int(d.original_bus_Pd.eq(0).sum()),
       "zones_with_pd_weighted_connected_alternative":int(d.positive_pd_main_component_candidate_count.gt(0).sum()),
       "zones_falling_back_to_first_bus":int(d.fallback_original_bus_no_positive_pd_candidate.sum()),
       "zones_with_any_load_relocation":int(d.share_of_zone_load_relocated_from_original_bus.gt(1e-12).sum()),
       "original_annual_load_mwh":total,
       "candidate_annual_load_mwh":float(d.candidate_zone_annual_mwh.sum()),
       "hypothetical_spatially_reassigned_mwh":moved,
       "hypothetical_reassigned_fraction_of_original_annual_load":moved/total if total else 0.,
       "original_and_candidate_each_hour_demand_equal":True,
       "hourly_zonal_demand_preserved":True,
       "network_original_load_attachments_modified":False,
       "candidate_bus_source_grid_connection_certified":False,
       "future_11_state_EFS_geometry_admitted":False,
       "generation_supply_admitted":False,
       "OPF_solved":False,
       "note":"Synthetic source-Pd weighted relocation is a model placement sensitivity, not actual load shift, congestion, supply loss, validated interconnection or physical dispatch.",
    }
    return d,result

def main():
    import pypsa
    ap=argparse.ArgumentParser()
    ap.add_argument("--base",type=Path,required=True)
    ap.add_argument("--load-net",type=Path,required=True)
    ap.add_argument("--outdir",type=Path,required=True)
    a=ap.parse_args()
    d,r=compare(pypsa.Network(str(a.base)),pypsa.Network(str(a.load_net)))
    a.outdir.mkdir(parents=True,exist_ok=True)
    d.to_csv(a.outdir/"efs_2030_zone_firstbus_vs_source_pd_candidates.csv",index=False)
    (a.outdir/"efs_2030_zone_firstbus_vs_source_pd_summary.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
    print(d[["Load_id","original_bus_id","original_bus_Pd","positive_pd_main_component_candidate_count","fallback_original_bus_no_positive_pd_candidate","share_of_zone_load_relocated_from_original_bus","original_zone_annual_mwh"]].to_string(index=False))
if __name__=="__main__":main()
