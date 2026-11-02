"""Prioritize EIA-860 plant/bus geographic candidates for independent tie evidence.

No proximity, BA label or grid-component membership certifies a connection.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def triage(candidates, material, out, year):
    c=pd.read_csv(candidates,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    m=pd.read_csv(material,dtype={"plant_id":"string","main_component_candidate_bus":"string"})
    required={"plant_id","nearest_candidate_bus","distance_km","assignment_status","electrical_connection_verified"}
    if required-set(c):raise ValueError("Missing EIA860 geographic candidate columns")
    if c.plant_id.isna().any() or c.plant_id.duplicated().any():raise ValueError("Invalid plant identities")
    if not c.assignment_status.eq("geographic_candidate_only").all() or not c.electrical_connection_verified.astype(str).str.lower().eq("false").all():
        raise ValueError("Candidate mistakenly certified as electrical")
    c["distance_km"]=pd.to_numeric(c.distance_km,errors="coerce")
    if c.distance_km.isna().any() or c.distance_km.lt(0).any() or not c.distance_km.map(__import__("math").isfinite).all():
        raise ValueError("Invalid geographic distance")
    if m.plant_id.isna().any() or m.plant_id.duplicated().any():raise ValueError("Invalid material change plant identities")
    if not set(m.plant_id).issubset(set(c.plant_id)):raise ValueError("Material changes not in original geographic universe")
    flagged=c.loc[c.distance_km.gt(50),["plant_id","nearest_candidate_bus","distance_km"]].copy()
    flagged["long_distance"]=True
    material_ids=set(m.plant_id)
    merged=c.loc[c.plant_id.isin(material_ids)|c.distance_km.gt(50)].copy()
    merged["long_distance"]=merged.distance_km.gt(50)
    merged["material_grid_candidate_change"]=merged.plant_id.isin(material_ids)
    merged["priority_reason"]=merged.apply(lambda r: "both" if r.long_distance and r.material_grid_candidate_change else ("main_grid_candidate_changed_over_1km" if r.material_grid_candidate_change else "nearest_bus_over_50km"),axis=1)
    merged["electrical_connection_verified"]=False
    merged["eligible_for_real_dispatch"]=False
    merged["required_next_evidence"]="Independent plant/substation interconnection or documented generator-to-bus tie; source and year"
    merged=merged.sort_values(["material_grid_candidate_change","distance_km"],ascending=[False,False])
    out.parent.mkdir(parents=True,exist_ok=True)
    merged.to_csv(out,index=False)
    report={"year":year,"candidate_plants":len(c),"over_50km_count":int(c.distance_km.gt(50).sum()),
            "material_candidate_change_count":len(material_ids),"unique_priority_plant_count":len(merged),
            "both_categories_count":int((merged.long_distance&merged.material_grid_candidate_change).sum()),
            "verified_electrical_connections":0,"real_dispatch_approved":False,
            "note":"Geographic triage only. Source EIA inventory and power-grid node IDs are different evidence types."}
    out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",required=True,type=Path)
    p.add_argument("--material",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--year",required=True,type=int)
    a=p.parse_args()
    triage(a.candidates,a.material,a.out,a.year)

if __name__=="__main__":main()
