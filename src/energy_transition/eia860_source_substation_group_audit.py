"""Reconcile original substation IDs among Palo Verde geographic bus leads.

Original sub_id may correspond to several electrical bus records. Grouping is
source-model identity inspection only; no official utility substation name or
generator POI is inferred.
"""
import argparse
import json
from pathlib import Path
import pandas as pd


def canonical_sub_id(value):
    if pd.isna(value):
        return None
    text=str(value).strip()
    if not text:
        return None
    try:
        number=float(text)
        if number.is_integer() and number>=0:
            return str(int(number))
    except ValueError:
        pass
    return text


def audit(bus_path: Path, edges_path: Path, out_dir: Path):
    b=pd.read_csv(bus_path,dtype={"plant_id":"string","bus_id":"string","sub_id":"string"})
    e=pd.read_csv(edges_path,dtype={"plant_id":"string","bus_id":"string","other_bus_id":"string",
                                    "other_bus_sub_id":"string","edge_id":"string"})
    required_b={"plant_id","bus_id","sub_id","candidate_voltage_kv","x","y",
                "line_count","transformer_count","geographic_distance_km"}
    required_e={"plant_id","bus_id","edge_type","edge_id","other_bus_id","other_bus_sub_id"}
    if required_b-set(b) or required_e-set(e):
        raise ValueError("Missing source-bus or endpoint topology fields")
    if b.empty or b.bus_id.isna().any() or b.bus_id.duplicated().any():
        raise ValueError("Invalid original bus inventory")
    if not b.plant_id.eq(b.plant_id.iloc[0]).all():
        raise ValueError("Mixed plant IDs")
    b["source_sub_id"]=b.sub_id.map(canonical_sub_id)
    if b.source_sub_id.isna().any():
        raise ValueError("Source substation identifiers missing")
    e["source_neighbor_sub_id"]=e.other_bus_sub_id.map(canonical_sub_id)
    if not set(e.bus_id.astype(str)).issubset(set(b.bus_id.astype(str))):
        raise ValueError("Endpoint not from selected bus inventory")
    for col in ("x","y","candidate_voltage_kv","geographic_distance_km","line_count","transformer_count"):
        b[col]=pd.to_numeric(b[col],errors="coerce")
        if b[col].isna().any():
            raise ValueError(f"Invalid source-bus {col}")
    incident=e.groupby(["bus_id","edge_type"]).size().unstack(fill_value=0)
    for kind,col in (("line","line_count"),("transformer","transformer_count")):
        counts=b.bus_id.map(incident[kind] if kind in incident else {}).fillna(0).astype(int)
        if not counts.eq(b[col]).all():
            raise ValueError(f"Source {kind} incidence count mismatch")
    e=e.merge(b[["bus_id","source_sub_id"]],on="bus_id",how="left",validate="many_to_one")
    e["same_source_substation_edge"]=e.source_sub_id.eq(e.source_neighbor_sub_id)
    groups=[]
    for sub_id,part in b.groupby("source_sub_id",sort=True):
        own=e.loc[e.source_sub_id.eq(sub_id)]
        unique_xy=part[["x","y"]].drop_duplicates().shape[0]
        groups.append({"plant_id":str(b.plant_id.iloc[0]),"source_sub_id":str(sub_id),
                       "bus_count":int(len(part)),"bus_ids":";".join(part.bus_id.astype(str).sort_values()),
                       "voltage_kv":";".join(map(str,sorted(part.candidate_voltage_kv.unique()))),
                       "unique_coordinate_pairs":int(unique_xy),
                       "incident_line_and_transformer_records":int(len(own)),
                       "same_source_substation_edge_records":int(own.same_source_substation_edge.sum()),
                       "minimum_plant_distance_km":float(part.geographic_distance_km.min()),
                       "independently_verified_facility_identity":False})
    summary={"plant_id":str(b.plant_id.iloc[0]),"candidate_bus_count":int(len(b)),
             "unique_source_substation_ids":len(groups),
             "source_substations_with_multiple_bus_records":sum(x["bus_count"]>1 for x in groups),
             "source_substations_with_multiple_coordinate_pairs":sum(x["unique_coordinate_pairs"]>1 for x in groups),
             "total_incident_records":int(len(e)),
             "same_substation_incident_records":int(e.same_source_substation_edge.sum()),
             "independently_verified_palo_verde_substation_identity":False,
             "generator_injections_approved":0,
             "note":"Source numeric sub_id is not an independently verified Palo Verde facility identifier."}
    out_dir.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(groups).to_csv(out_dir/"palo_verde_source_substation_groups.csv",index=False)
    e.to_csv(out_dir/"palo_verde_source_substation_edges.csv",index=False)
    (out_dir/"palo_verde_source_substation_groups.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    print(pd.DataFrame(groups).to_string(index=False))
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--buses",type=Path,required=True)
    p.add_argument("--edges",type=Path,required=True)
    p.add_argument("--out-dir",type=Path,required=True)
    a=p.parse_args()
    audit(a.buses,a.edges,a.out_dir)


if __name__=="__main__":
    main()
