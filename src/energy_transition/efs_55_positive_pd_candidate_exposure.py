"""Screen whether 55 graph-isolated source Pd buses would receive EFS load.

Uses the *exported* bus.state with archived bus LAF_state as a what-if
allocation only. The dropped historical full_state denominator, receiving
ReEDS region and real UTC remain unverified: no empirical load admission.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import networkx as nx
import numpy as np
import pandas as pd

STATE_NAMES={"AZ":"Arizona","CA":"California","CO":"Colorado","ID":"Idaho",
             "MT":"Montana","NM":"New Mexico","NV":"Nevada","OR":"Oregon",
             "UT":"Utah","WA":"Washington","WY":"Wyoming"}
YEARS={2030,2040,2050}

def screening(network,efs:pd.DataFrame):
    if set(efs.columns)!={"year","state","local_hour_id","load_mw"}:
        raise ValueError("EFS expected year/state/local_hour_id/load_mw")
    demand=efs.copy()
    demand["year"]=pd.to_numeric(demand.year,errors="raise").astype(int)
    demand["local_hour_id"]=pd.to_numeric(demand.local_hour_id,errors="raise").astype(int)
    demand["load_mw"]=pd.to_numeric(demand.load_mw,errors="raise")
    if set(demand.year)!=YEARS or set(demand.state)!=set(STATE_NAMES):
        raise ValueError("EFS cohort or scenario years changed")
    if len(demand)!=11*3*8760 or demand.duplicated(["year","state","local_hour_id"]).any():
        raise ValueError("Missing or duplicate source-hour records")
    if not np.isfinite(demand.load_mw.to_numpy()).all() or demand.load_mw.lt(0).any():
        raise ValueError("Invalid EFS hourly load")
    totals=demand.groupby(["year","state"],as_index=False).load_mw.sum().rename(columns={"load_mw":"efs_state_annual_mwh"})
    graph=nx.Graph()
    graph.add_nodes_from(network.buses.index.astype(str))
    for frame in (network.lines,network.transformers):
        for _,r in frame.iterrows():
            a,b=str(r.bus0),str(r.bus1)
            if a not in graph or b not in graph:raise ValueError("Missing source graph endpoint")
            graph.add_edge(a,b)
    isolate=set(nx.isolates(graph))
    buses=network.buses
    if not {"Pd","LAF_state","state","v_nom","substation_off"}.issubset(buses):
        raise ValueError("Missing archived source bus attributes")
    p=buses.loc[buses.index.astype(str).isin(isolate)].copy()
    p["source_Pd"]=pd.to_numeric(p.Pd,errors="coerce")
    p["source_LAF_state"]=pd.to_numeric(p.LAF_state,errors="coerce")
    p["source_v_nom_kv"]=pd.to_numeric(p.v_nom,errors="coerce")
    p["is_offshore"]=p.substation_off.astype("string").str.lower().eq("true").fillna(False)
    c=p.loc[p.source_Pd.gt(0) & ~p.is_offshore].copy()
    if len(isolate)!=877 or len(c)!=55:raise ValueError("Pinned base-network cohort drift")
    if not np.isfinite(c[["source_Pd","source_LAF_state","source_v_nom_kv"]].to_numpy(dtype=float)).all():
        raise ValueError("Invalid isolated source Pd/LAF/voltage")
    if c.source_LAF_state.lt(0).any() or c.source_LAF_state.gt(1).any():
        raise ValueError("Source bus LAF outside 0-1")
    if c.source_v_nom_kv.gt(25).any():raise ValueError("Expected low voltage source cohort changed")
    c["bus_id"]=c.index.astype(str)
    inverse={value:key for key,value in STATE_NAMES.items()}
    c["exported_state_code"]=c.state.map(inverse)
    if c.exported_state_code.isna().any():raise ValueError("Missing EFS state for candidate bus")
    c=c.reset_index(drop=True)
    joined=c.merge(totals,left_on="exported_state_code",right_on="state",how="left",
                   validate="many_to_many")
    if len(joined)!=55*3 or joined.efs_state_annual_mwh.isna().any():
        raise ValueError("Source state-year coverage failed")
    joined["hypothetical_exported_state_laf_annual_mwh"]=(
        joined.source_LAF_state*joined.efs_state_annual_mwh)
    out=joined[["bus_id","year","exported_state_code","source_v_nom_kv","source_Pd",
                "source_LAF_state","efs_state_annual_mwh",
                "hypothetical_exported_state_laf_annual_mwh"]].copy()
    out.sort_values(["year","exported_state_code","bus_id"],inplace=True)
    yeartable=out.groupby("year",as_index=False).agg(
        positive_pd_source_bus_count=("bus_id","nunique"),
        raw_source_Pd_sum_mw=("source_Pd","sum"),
        hypothetical_exported_state_laf_annual_mwh=("hypothetical_exported_state_laf_annual_mwh","sum"),
    )
    results={
        "source_archive_bus_count":len(buses),
        "line_transformer_zero_degree_bus_count":len(isolate),
        "positive_source_pd_zero_degree_bus_count":len(c),
        "source_positive_pd_sum_mw":float(c.source_Pd.sum()),
        "source_laf_weight_sum_over_55_exported_buses":float(c.source_LAF_state.sum()),
        "candidate_bus_year_rows":len(out),
        "all_55_exported_states_present_in_11_EFS":True,
        "planning_year_rows":yeartable.to_dict(orient="records"),
        "direct_physically_validated_efs_load_attached_to_55_buses":False,
        "old_dropped_full_state_denominator_recovered":False,
        "reeds_receiving_zone_compatibility_confirmed":False,
        "actual_utc_time_alignment_confirmed":False,
        "operational_loss_of_load_demonstrated":False,
        "real_generator_poi_approved":False,
        "full_western_opf_solved":False,
        "note":"Hypothetical state-summed source load times original LAF, matched by exported state only; **not** a validated bus allocation, outage MWh or source full_state alignment.",
    }
    return out,results

def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--efs",type=Path,required=True)
    p.add_argument("--outdir",type=Path,required=True)
    a=p.parse_args()
    table,report=screening(pypsa.Network(str(a.network)),
         pd.read_csv(a.efs,compression="infer"))
    a.outdir.mkdir(parents=True,exist_ok=True)
    table.to_csv(a.outdir/"55_positive_pd_candidate_efs_state_annual_exposure.csv",index=False)
    (a.outdir/"55_positive_pd_candidate_efs_state_annual_exposure.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
