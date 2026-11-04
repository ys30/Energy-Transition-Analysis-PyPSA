"""Enrich distant EIA plant POI review queue using original official 2024 coordinates.

No guessed plant names, substations, POIs or generator-to-bus authority.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

REQUIRED_PLANTS={"plant_id","state","ba_code","nearest_candidate_bus","distance_km",
                 "generator_count","operating_nameplate_mw","over50km",
                 "electrical_connection_verified","empirical_generator_injection_approved"}
REQUIRED_COORDS={"plant_id","state","nearest_candidate_bus","distance_km",
                 "plant_latitude","plant_longitude","bus_latitude","bus_longitude",
                 "assignment_status","electrical_connection_verified"}

def enrich(plants:pd.DataFrame, candidates:pd.DataFrame):
    p=plants.copy(); c=candidates.copy()
    if REQUIRED_PLANTS-set(p) or REQUIRED_COORDS-set(c):
        raise ValueError("Missing plant triage or official EIA coordinate candidate columns")
    for df in (p,c):
        df["plant_id"]=df.plant_id.astype("string").str.strip()
        df["nearest_candidate_bus"]=df.nearest_candidate_bus.astype("string").str.strip()
        df["state"]=df.state.astype("string").str.strip()
        if df.plant_id.isna().any() or df.plant_id.eq("").any() or df.plant_id.duplicated().any():
            raise ValueError("Unstable or duplicate official plant identities")
    if not p.electrical_connection_verified.astype("string").str.lower().eq("false").all() or not p.empirical_generator_injection_approved.astype("string").str.lower().eq("false").all():
        raise ValueError("Existing plant POIs improperly marked as approved")
    if not c.electrical_connection_verified.astype("string").str.lower().eq("false").all() or not c.assignment_status.eq("geographic_candidate_only").all():
        raise ValueError("Coordinate candidates wrongly promoted")
    if not p.over50km.astype("string").str.lower().isin(["true","false"]).all():
        raise ValueError("Invalid long-distance flags")
    far=p[p.over50km.astype("string").str.lower().eq("true")].copy()
    if far.empty:raise ValueError("No distant source plants")
    cols=sorted(REQUIRED_COORDS|({"plant_name"} if "plant_name" in c else set()))
    joined=far.merge(c[cols],on="plant_id",how="left",validate="one_to_one",
                     suffixes=("","_official"),indicator=True)
    if not joined["_merge"].eq("both").all():raise ValueError("Missing original official EIA plant-coordinate source")
    if not joined.state.eq(joined.state_official).all() or not joined.nearest_candidate_bus.eq(joined.nearest_candidate_bus_official).all():
        raise ValueError("Official generator and facility candidate IDs mismatch")
    for field in ["distance_km","distance_km_official","plant_latitude","plant_longitude","bus_latitude","bus_longitude"]:
        joined[field]=pd.to_numeric(joined[field],errors="coerce")
        if not np.isfinite(joined[field].to_numpy(dtype=float)).all():
            raise ValueError("Missing or invalid original coordinates")
    if not np.allclose(joined.distance_km,joined.distance_km_official,atol=0.0001,rtol=0):
        raise ValueError("Official source candidate distance changed")
    if not joined.plant_latitude.between(25,50).all() or not joined.plant_longitude.between(-125,-102).all():
        raise ValueError("Plant geography outside official source screen")
    if not joined.bus_latitude.between(25,50).all() or not joined.bus_longitude.between(-125,-102).all():
        raise ValueError("Candidate-bus geography outside source screen")
    if "plant_name" not in joined:
        joined["plant_name"]=pd.NA
    joined["plant_name"]=joined.plant_name.astype("string").str.strip()
    joined["review_queue_status"]="needs_authoritative_interconnection_document"
    joined["connection_document_url"]=pd.NA
    joined["electrical_connection_verified"]=False
    joined["empirical_generator_injection_approved"]=False
    joined=joined.sort_values(
        ["operating_nameplate_mw","distance_km","plant_id"],ascending=[False,False,True])
    named=int(joined.plant_name.notna().sum())
    summed=float(joined.operating_nameplate_mw.sum())
    grouped=joined.groupby("nearest_candidate_bus",as_index=False).agg(
        plant_count=("plant_id","size"),
        nameplate_mw=("operating_nameplate_mw","sum"),
        maximum_distance_km=("distance_km","max"),
        named_plants=("plant_name",lambda x:" | ".join(x.dropna().astype(str).head(12))),
        source_plant_ids=("plant_id",lambda x:";".join(x.astype(str))),
    ).sort_values("nameplate_mw",ascending=False)
    if not np.isclose(grouped.nameplate_mw.sum(),summed,atol=1e-6,rtol=0):
        raise ValueError("Cluster-nameplate energy provenance failed")
    report={
        "official_source_year":2024,
        "distant_plant_rows":len(joined),
        "official_names_available":named,
        "official_names_missing":len(joined)-named,
        "candidate_bus_count":len(grouped),
        "historic_distant_nameplate_mw":summed,
        "highest_nameplate_candidate_bus":str(grouped.iloc[0].nearest_candidate_bus),
        "highest_nameplate_bus_plant_count":int(grouped.iloc[0].plant_count),
        "highest_nameplate_bus_historic_mw":float(grouped.iloc[0].nameplate_mw),
        "official_coordinate_and_candidate_key_join_verified":True,
        "electrical_POI_documents_verified":0,
        "approved_generator_bus_connections":0,
        "source_network_is_utility_verified":False,
        "future_2030_2050_empirical_generator_mapping_admitted":False,
        "note":"Official facility names and reported coordinates are evidence for external document review; candidate buses are synthetic-topology IDs, not electrically certified interconnections.",
    }
    return joined,grouped,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--plants",required=True,type=Path)
    p.add_argument("--candidates",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    a=p.parse_args()
    plants=pd.read_csv(a.plants,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    candidates=pd.read_csv(a.candidates,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    full,groups,r=enrich(plants,candidates)
    a.out_dir.mkdir(parents=True,exist_ok=True)
    full.to_csv(a.out_dir/"official_named_63plant_poi_review_queue.csv",index=False)
    full.head(20).to_csv(a.out_dir/"official_named_top20plant_poi_review_queue.csv",index=False)
    groups.to_csv(a.out_dir/"named_candidate_bus_collision_clusters.csv",index=False)
    (a.out_dir/"official_plant_poi_source_enrichment.json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
    print(full[["plant_id","plant_name","state","ba_code","nearest_candidate_bus","distance_km","operating_nameplate_mw"]].head(12).to_string(index=False))

if __name__=="__main__":main()
