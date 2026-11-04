"""Evidence-only triage of EIA-860 generator rows into plant-level POI reviews.

Ranks the *same official 2024* generator-level archive without duplicating
plant capacity or implying geographic proximity is electrical connectivity.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
import pandas as pd

NEEDED={"plant_id","generator_id","state","ba_code","fuel","capacity_mw",
        "nearest_candidate_bus","distance_km","candidate_status",
        "has_geographic_candidate","electrical_connection_verified",
        "pypsa_generator_creation_approved"}

def triage(staging:pd.DataFrame):
    x=staging.copy()
    if NEEDED-set(x):raise ValueError("Generator staging schema incomplete")
    if x.empty or x[["plant_id","generator_id"]].isna().any().any():
        raise ValueError("Missing generator source IDs")
    for k in ["plant_id","generator_id","nearest_candidate_bus"]:
        x[k]=x[k].astype("string").str.strip()
    if x.duplicated(["plant_id","generator_id"]).any():
        raise ValueError("Duplicate plant-generator identifiers")
    if not x.has_geographic_candidate.astype("string").str.lower().eq("true").all():
        raise ValueError("Unmapped source generators require separate review")
    if not x.candidate_status.eq("candidate_only_no_approved_POI").all():
        raise ValueError("Staging source wrongly approved")
    for k in ["electrical_connection_verified","pypsa_generator_creation_approved"]:
        if not x[k].astype("string").str.lower().eq("false").all():
            raise ValueError("Unverified nearest bus promoted")
    for k in ["capacity_mw","distance_km"]:
        x[k]=pd.to_numeric(x[k],errors="coerce")
        if x[k].isna().any() or not np.isfinite(x[k].to_numpy(dtype=float)).all():
            raise ValueError("Invalid numeric source data")
    if x.capacity_mw.le(0).any() or x.distance_km.lt(0).any():
        raise ValueError("Bad capacity or distance")
    for k in ["state","ba_code"]:
        if x[k].isna().any() or x[k].astype("string").str.strip().eq("").any():
            raise ValueError("Missing plant source region")
        if x.groupby("plant_id")[k].nunique(dropna=False).gt(1).any():
            raise ValueError("Conflicting plant region among generators")
    if x.groupby("plant_id")["nearest_candidate_bus"].nunique(dropna=False).gt(1).any() or x.groupby("plant_id")["distance_km"].nunique(dropna=False).gt(1).any():
        raise ValueError("Inconsistent nearest bus across a plant's units")
    x["over50km"]=x.distance_km.gt(50)
    grouped=(x.groupby("plant_id",as_index=False)
             .agg(state=("state","first"),ba_code=("ba_code","first"),
                  nearest_candidate_bus=("nearest_candidate_bus","first"),
                  distance_km=("distance_km","first"),
                  generator_count=("generator_id","size"),
                  operating_nameplate_mw=("capacity_mw","sum"),
                  fuel_types=("fuel",lambda z:";".join(sorted(set(z.dropna().astype(str))))),
                  over50km=("over50km","first")))
    grouped["priority_rank"]=0
    grouped=grouped.sort_values(
        ["over50km","operating_nameplate_mw","distance_km","plant_id"],
        ascending=[False,False,False,True]).reset_index(drop=True)
    grouped["priority_rank"]=np.arange(1,len(grouped)+1)
    grouped["needs_independent_POI_documentation"]=True
    grouped["electrical_connection_verified"]=False
    grouped["empirical_generator_injection_approved"]=False
    far=grouped[grouped.over50km].copy()
    top=grouped.head(20)
    far20=far.head(20)
    by_ba=grouped.groupby(["ba_code","state"],as_index=False).agg(
        plants=("plant_id","size"),generators=("generator_count","sum"),
        nameplate_mw=("operating_nameplate_mw","sum"),
        over50km_plants=("over50km","sum"))
    total=float(x.capacity_mw.sum())
    if len(grouped)!=x.plant_id.nunique() or int(grouped.generator_count.sum())!=len(x) or not np.isclose(grouped.operating_nameplate_mw.sum(),total,atol=1e-6,rtol=0):
        raise ValueError("Plant-level rollup does not reconcile official generators")
    if not np.isclose(by_ba.nameplate_mw.sum(),total,atol=1e-6,rtol=0):
        raise ValueError("BA source rollup does not reconcile")
    report={
        "generator_rows":int(len(x)),"operating_plant_count":int(len(grouped)),
        "operating_nameplate_mw":total,
        "over50km_generator_rows":int(x.over50km.sum()),
        "over50km_plant_count":int(len(far)),
        "over50km_nameplate_mw":float(far.operating_nameplate_mw.sum()),
        "top20_over50km_nameplate_mw":float(far20.operating_nameplate_mw.sum()),
        "top20_all_priorities_nameplate_mw":float(top.operating_nameplate_mw.sum()),
        "over50km_plant_id_examples":far.head(10).plant_id.astype(str).tolist(),
        "ba_state_groups":int(len(by_ba)),
        "plant_and_ba_capacity_reconciled":True,
        "electrical_POIs_verified":0,"actual_network_generators_inserted":0,
        "2024_historical_nameplate_not_future_dispatch_capacity":True,
        "future_EFS_2030_2050_generation_admitted":False,
        "note":"Ranked source evidence collection only. The pinned grid is synthetic-topology-derived, so nearest bus cannot establish physical interconnection.",
    }
    return grouped,far,by_ba,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--staging",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    x=pd.read_csv(a.staging,dtype={"plant_id":"string","generator_id":"string","nearest_candidate_bus":"string"})
    plants,far,by_ba,r=triage(x)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    plants.to_csv(a.out_dir/"all_operating_plant_poi_triage.csv",index=False)
    far.to_csv(a.out_dir/"over50km_plant_poi_triage.csv",index=False)
    far.head(20).to_csv(a.out_dir/"top20_over50km_poi_document_queue.csv",index=False)
    by_ba.to_csv(a.out_dir/"poi_triage_by_ba_state.csv",index=False)
    (a.out_dir/"generator_plant_poi_triage_summary.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
    print("TOP TEN long-distance plants (not approved POIs):")
    print(far[["plant_id","state","ba_code","nearest_candidate_bus","distance_km","generator_count","operating_nameplate_mw"]].head(10).to_string(index=False))

if __name__=="__main__":main()
