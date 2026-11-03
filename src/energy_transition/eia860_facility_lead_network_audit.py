"""Inspect real model-bus topology near officially documented plant facilities.

Nearest geographic bus and voltage compatibility are *screening* checks only.
No documented facility or generator is claimed to connect electrically to a bus.
"""
import argparse
import json
from pathlib import Path
import pandas as pd
import pypsa


def audit(leads_path: Path, candidates_path: Path, network_path: Path, out: Path):
    leads=pd.read_csv(leads_path,dtype={"plant_id":"string","network_bus_id":"string"})
    c=pd.read_csv(candidates_path,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    required_leads={"plant_id","plant_name","source_url","documented_voltage_kv",
                    "network_bus_id","independent_electrical_bus_match_verified"}
    required_c={"plant_id","nearest_candidate_bus","distance_km"}
    if required_leads-set(leads) or required_c-set(c):
        raise ValueError("Missing documentary lead or candidate fields")
    if leads.empty or leads.plant_id.isna().any() or leads.plant_id.duplicated().any():
        raise ValueError("Missing or duplicate lead plant IDs")
    if c.plant_id.isna().any() or c.plant_id.duplicated().any():
        raise ValueError("Missing or duplicate geographic candidate IDs")
    flags=leads.independent_electrical_bus_match_verified.astype("string").str.strip().str.lower()
    if not flags.eq("false").all() or leads.network_bus_id.notna().any():
        raise ValueError("Unreviewed facility leads must not assert verified electrical bus IDs")
    if not leads.source_url.astype("string").str.startswith("https://",na=False).all():
        raise ValueError("Facility leads must include original HTTPS source URLs")
    n=pypsa.Network(str(network_path))
    merged=leads.merge(c[["plant_id","nearest_candidate_bus","distance_km"]],
                       on="plant_id",how="left",validate="one_to_one")
    if merged.nearest_candidate_bus.isna().any():
        raise ValueError("Official facility lead missing geographic plant candidate")
    b=n.buses
    rows=[]
    for r in merged.itertuples(index=False):
        bus=str(r.nearest_candidate_bus)
        if bus not in b.index.astype(str):
            raise ValueError(f"Candidate bus absent from source network: {bus}")
        v=float(pd.to_numeric(pd.Series([b.loc[bus,"v_nom"]]),errors="coerce").iloc[0])
        doc=[]
        for part in str(r.documented_voltage_kv).split(";"):
            try:
                doc.append(float(part.strip()))
            except ValueError as exc:
                raise ValueError("Non-numeric documented switchyard voltage") from exc
        if not doc or any(x<=0 for x in doc):
            raise ValueError("Invalid documented facility voltage")
        connected_lines=n.lines[(n.lines.bus0.astype(str)==bus)|(n.lines.bus1.astype(str)==bus)]
        connected_transformers=n.transformers[(n.transformers.bus0.astype(str)==bus)|(n.transformers.bus1.astype(str)==bus)]
        rows.append({
            "plant_id":r.plant_id,"plant_name":r.plant_name,
            "source_url":r.source_url,"geographic_candidate_bus":bus,
            "distance_km":float(r.distance_km),"candidate_bus_v_nom_kv":v,
            "documented_facility_voltages_kv":";".join(str(x) for x in doc),
            "candidate_voltage_in_documented_facility_set":bool(pd.notna(v) and any(abs(v-x)<0.01 for x in doc)),
            "candidate_connected_line_count":int(len(connected_lines)),
            "candidate_connected_transformer_count":int(len(connected_transformers)),
            "candidate_line_ids":";".join(map(str,connected_lines.index[:15])),
            "candidate_transformer_ids":";".join(map(str,connected_transformers.index[:15])),
            "source_facility_to_original_bus_verified":False,
            "generator_injection_approved":False,
            "review_status":"topology_and_voltage_screen_only",
        })
    frame=pd.DataFrame(rows)
    out.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out,index=False)
    report={"facility_leads":len(frame),
            "candidate_voltage_compatible":int(frame.candidate_voltage_in_documented_facility_set.sum()),
            "candidate_voltage_incompatible":int((~frame.candidate_voltage_in_documented_facility_set).sum()),
            "independently_verified_source_facility_to_original_bus":0,
            "generator_injections_approved":0,
            "warning":"Geographic coincidence, topology, and voltage compatibility do not prove facility-to-model-bus identity."}
    out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--leads",type=Path,required=True)
    a.add_argument("--candidates",type=Path,required=True)
    a.add_argument("--network",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    x=a.parse_args();audit(x.leads,x.candidates,x.network,x.out)
