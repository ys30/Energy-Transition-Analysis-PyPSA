"""Diagnose EIA plant-to-synthetic-network nearest-bus collision risk.

Independent EIA plants that collapse onto the SAME distant synthetic bus
form review CLUSTERS, not verified shared substations or physical POIs.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

import numpy as np
import pandas as pd

COLUMNS={"plant_id","state","ba_code","nearest_candidate_bus","distance_km",
         "generator_count","operating_nameplate_mw","over50km",
         "electrical_connection_verified","empirical_generator_injection_approved"}

def audit_collisions(plants:pd.DataFrame):
    d=plants.copy()
    if COLUMNS-set(d):raise ValueError("Missing plant-level verified staging fields")
    for k in ["plant_id","nearest_candidate_bus"]:
        d[k]=d[k].astype("string").str.strip()
    if d.plant_id.isna().any() or d.plant_id.eq("").any() or d.plant_id.duplicated().any():
        raise ValueError("Duplicate or absent plant identities")
    for k in ["distance_km","operating_nameplate_mw","generator_count"]:
        d[k]=pd.to_numeric(d[k],errors="coerce")
        if d[k].isna().any() or not np.isfinite(d[k].to_numpy(dtype=float)).all() or (d[k]<0).any():
            raise ValueError("Invalid geographic source data")
    flags=d.over50km.astype("string").str.lower()
    if not flags.isin(["true","false"]).all() or not flags.eq(d.distance_km.gt(50).astype(str).str.lower()).all():
        raise ValueError("Unverified long-distance classification")
    for k in ["electrical_connection_verified","empirical_generator_injection_approved"]:
        if not d[k].astype("string").str.lower().eq("false").all():
            raise ValueError("Unverified electrical POI was promoted")
    far=d[d.distance_km.gt(50)].copy()
    group=far.groupby("nearest_candidate_bus",as_index=False).agg(
        plant_count=("plant_id","size"),
        generator_count=("generator_count","sum"),
        historic_nameplate_mw=("operating_nameplate_mw","sum"),
        maximum_distance_km=("distance_km","max"),
        median_distance_km=("distance_km","median"),
        represented_states=("state",lambda x:";".join(sorted(set(x.astype(str))))),
        represented_bas=("ba_code",lambda x:";".join(sorted(set(x.astype(str))))),
        plant_ids=("plant_id",lambda x:";".join(sorted(set(x.astype(str))))),
    )
    group=group.sort_values(["historic_nameplate_mw","plant_count"],
        ascending=[False,False]).reset_index(drop=True)
    group["cluster_is_poi_verified"]=False
    group["independent_source_review_required"]=True
    total=float(d.operating_nameplate_mw.sum())
    far_mw=float(far.operating_nameplate_mw.sum())
    if not np.isclose(float(group.historic_nameplate_mw.sum()),far_mw,atol=1e-5,rtol=0):
        raise ValueError("Long-distance capacity source conservation failed")
    top=group.head(10)
    summary={
        "source_operating_plants":int(len(d)),
        "source_operating_nameplate_mw":total,
        "long_distance_plants":int(len(far)),
        "long_distance_nameplate_mw":far_mw,
        "distinct_long_distance_candidate_buses":int(len(group)),
        "candidate_buses_with_multiple_far_plants":int((group.plant_count>1).sum()),
        "long_distance_plants_in_repeated_candidate_bus_groups":int(
            group.loc[group.plant_count>1,"plant_count"].sum()),
        "nameplate_in_repeated_far_bus_groups_mw":float(
            group.loc[group.plant_count>1,"historic_nameplate_mw"].sum()),
        "top_ten_candidate_buses_nameplate_mw":float(top.historic_nameplate_mw.sum()),
        "highest_risk_candidate_bus":str(group.iloc[0].nearest_candidate_bus),
        "highest_risk_candidate_bus_nameplate_mw":float(group.iloc[0].historic_nameplate_mw),
        "highest_risk_candidate_bus_plant_count":int(group.iloc[0].plant_count),
        "capacity_conservation_verified":True,
        "electric_poi_connections_verified":0,
        "source_bus_ids_are_utility_verified":False,
        "future_generator_mapping_admitted":False,
        "note":"Bus collisions are nearest-neighbor artifacts over a synthetic source network, not proof that plants share a real electrical interconnection.",
    }
    return group,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plant-triage",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    d=pd.read_csv(a.plant_triage,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    clusters,summary=audit_collisions(d)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    clusters.to_csv(a.out_dir/"long_distance_plant_candidate_bus_collision_groups.csv",index=False)
    (a.out_dir/"long_distance_plant_candidate_bus_collision_summary.json").write_text(
        json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    print("Top candidate-bus collision clusters (NOT utility POIs):")
    print(clusters[["nearest_candidate_bus","plant_count","generator_count",
        "historic_nameplate_mw","maximum_distance_km","represented_states",
        "represented_bas"]].head(10).to_string(index=False))

if __name__=="__main__":main()
