"""Joint source-voltage/Pd/offshore audit of archived Western degree-zero nodes.

Preserves original bus identities and publishes the positive-Pd cohort
for careful source-model QA, NOT as real unserved demand or network outages.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd

def audit(n):
    g=nx.Graph()
    g.add_nodes_from(n.buses.index.astype(str))
    for edges in (n.lines,n.transformers):
        for _,r in edges.iterrows():
            a,b=str(r.bus0),str(r.bus1)
            if a not in g or b not in g:raise ValueError("Unknown source branch bus")
            g.add_edge(a,b)
    isolate=set(nx.isolates(g))
    b=n.buses.loc[n.buses.index.astype(str).isin(isolate)].copy()
    if len(b)==0:raise ValueError("Missing source isolated-node cohort")
    required={"substation_off","Pd","LAF_state","v_nom","state","sub_id"}
    if required-set(b):raise ValueError("Source bus metadata incomplete")
    b["bus_id"]=b.index.astype(str)
    b["offshore_source_flag"]=b.substation_off.astype("string").str.lower().eq("true").fillna(False)
    b["pd_mw"]=pd.to_numeric(b.Pd,errors="coerce")
    b["nominal_kv"]=pd.to_numeric(b.v_nom,errors="coerce")
    b["sub_id_source"]=pd.to_numeric(b.sub_id,errors="coerce")
    if not np.isfinite(b[["pd_mw","nominal_kv"]].to_numpy(dtype=float)).all():raise ValueError("Invalid Pd/voltage")
    b["pd_class"]=np.where(b.pd_mw.gt(0),"positive_source_pd","zero_source_pd")
    b["laf_class"]=np.where(b.LAF_state.isna(),"missing_source_laf","present_source_laf")
    b["origin_class"]=np.where(b.offshore_source_flag,"offshore_auxiliary","nonoffshore_source_bus")
    b["source_substation_id_41012_or_higher"]=b.sub_id_source.ge(41012).fillna(False)
    # Explicitly describe observed source rather than equating an entire voltage bin with generation terminals.
    b["low_voltage_25kv_or_less"]=b.nominal_kv.le(25)
    group=b.groupby(["origin_class","nominal_kv","pd_class","laf_class"],dropna=False).agg(
        bus_count=("bus_id","size"),source_pd_mw=("pd_mw","sum"),
        sub_id_41012_plus_count=("source_substation_id_41012_or_higher","sum")
    ).reset_index().sort_values(["origin_class","nominal_kv","pd_class"])
    positive=b.loc[b.pd_mw.gt(0)].copy().sort_values("pd_mw",ascending=False)
    if len(group)==0 or group.bus_count.sum()!=len(b):raise ValueError("Joint source cross-tab not conserved")
    if abs(float(group.source_pd_mw.sum())-float(b.pd_mw.sum()))>1e-6:raise ValueError("Joint Pd not conserved")
    if len(positive)!=int(b.pd_mw.gt(0).sum()):raise ValueError("Positive source Pd cohort mismatch")
    report={
        "source_bus_total":len(n.buses),
        "line_transformer_zero_degree_count":len(b),
        "joint_source_category_rows":len(group),
        "offshore_source_zero_degree_nodes":int(b.offshore_source_flag.sum()),
        "nonoffshore_source_zero_degree_nodes":int((~b.offshore_source_flag).sum()),
        "nonoffshore_low_voltage_25kv_or_less":int(((~b.offshore_source_flag)&b.low_voltage_25kv_or_less).sum()),
        "nonoffshore_above_25kv":int(((~b.offshore_source_flag)&(~b.low_voltage_25kv_or_less)).sum()),
        "source_sub_id_41012_plus_zero_degree_count":int(b.source_substation_id_41012_or_higher.sum()),
        "zero_degree_positive_pd_count":len(positive),
        "zero_degree_positive_source_pd_mw":float(positive.pd_mw.sum()),
        "positive_pd_offshore_count":int(positive.offshore_source_flag.sum()),
        "positive_pd_by_voltage_kv":{str(k):{"bus_count":int(len(v)),"source_pd_mw":float(v.pd_mw.sum())}
            for k,v in positive.groupby("nominal_kv")},
        "positive_pd_top_ten_bus_ids":positive.head(10).bus_id.tolist(),
        "source_type_generator_terminal_verified":False,
        "real_grid_loss_of_load_verified":False,
        "bus_pruning_authorized":False,
        "full_empirical_opf_admitted":False,
        "note":"Raw bus Pd and nominal-voltage groupings are source engineering metadata; evidence of generator-terminal types or physical outages requires upstream bus-type/linkage provenance.",
    }
    return group,positive,report

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    grid,positive,r=audit(pypsa.Network(str(a.network)))
    a.outdir.mkdir(parents=True,exist_ok=True)
    grid.to_csv(a.outdir/"western_degree_zero_voltage_pd_origin_cross_tab.csv",index=False)
    cols=["bus_id","state","nominal_kv","pd_mw","LAF_state","sub_id_source","offshore_source_flag","origin_class","source_substation_id_41012_or_higher"]
    positive[cols].to_csv(a.outdir/"western_55_positive_pd_zero_degree_bus_review.csv",index=False)
    (a.outdir/"western_degree_zero_voltage_pd_source_summary.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))

if __name__=="__main__":main()
