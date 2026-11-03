"""Trace original PyPSA-USA bus source fields and first-hop electrical topology.

This is an evidence inventory: a bus's numeric ID, sub_id, voltage or nearby
coordinates cannot alone establish which EIA-860 plant injects at that bus.
"""
import argparse
import json
from pathlib import Path

import pandas as pd
import pypsa


FIELDS=("sub_id","substation_off","state","country","carrier","v_nom","x","y")


def trace(network_path: Path, candidate_path: Path, out: Path, plant_id: str="6008",
          max_buses: int=10):
    if max_buses<1:
        raise ValueError("max_buses must be positive")
    source=pd.read_csv(candidate_path,dtype={"plant_id":"string","candidate_bus_id":"string"})
    required={"plant_id","candidate_bus_id","candidate_bus_voltage_kv","distance_km",
              "electrical_connection_verified"}
    if required-set(source):
        raise ValueError(f"Missing voltage candidate fields: {sorted(required-set(source))}")
    selected=source.loc[source.plant_id.eq(str(plant_id))].head(max_buses)
    if selected.empty or selected.candidate_bus_id.isna().any() or selected.candidate_bus_id.duplicated().any():
        raise ValueError("No valid unique candidate bus IDs for plant")
    if not selected.electrical_connection_verified.astype("string").str.lower().eq("false").all():
        raise ValueError("Candidate cannot self-certify electrical connection")
    n=pypsa.Network(str(network_path))
    if "sub_id" not in n.buses.columns:
        raise ValueError("Source network missing sub_id; source identity investigation required")
    bus_ids=set(n.buses.index.astype(str))
    line_rows=[]
    bus_rows=[]
    for r in selected.itertuples(index=False):
        bus=str(r.candidate_bus_id)
        if bus not in bus_ids:
            raise ValueError(f"Missing source bus {bus}")
        record=n.buses.loc[bus]
        row={"plant_id":str(plant_id),"bus_id":bus,
             "geographic_distance_km":float(r.distance_km),
             "candidate_voltage_kv":float(r.candidate_bus_voltage_kv)}
        for field in FIELDS:
            row[field]=None if field not in record or pd.isna(record[field]) else str(record[field])
        if abs(float(record.v_nom)-float(r.candidate_bus_voltage_kv))>0.01:
            raise ValueError(f"Candidate voltage inconsistent with source network for {bus}")
        for kind,frame in (("line",n.lines),("transformer",n.transformers)):
            adj=frame.loc[frame.bus0.astype(str).eq(bus)|frame.bus1.astype(str).eq(bus)]
            for eid,edge in adj.iterrows():
                neighbor=str(edge.bus1) if str(edge.bus0)==bus else str(edge.bus0)
                if neighbor not in bus_ids:
                    raise ValueError(f"Missing {kind} endpoint {neighbor}")
                neighbor_rec=n.buses.loc[neighbor]
                line_rows.append({"plant_id":str(plant_id),"bus_id":bus,"edge_type":kind,
                                  "edge_id":str(eid),"other_bus_id":neighbor,
                                  "other_bus_voltage_kv":float(neighbor_rec.v_nom),
                                  "other_bus_sub_id":None if pd.isna(neighbor_rec.sub_id) else str(neighbor_rec.sub_id)})
            row[f"{kind}_count"]=len(adj)
        bus_rows.append(row)
    out.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(bus_rows).to_csv(out,index=False)
    edges=out.with_name(out.stem+"_edges.csv")
    pd.DataFrame(line_rows,columns=["plant_id","bus_id","edge_type","edge_id",
                                   "other_bus_id","other_bus_voltage_kv","other_bus_sub_id"]).to_csv(edges,index=False)
    summary={"plant_id":str(plant_id),"source_bus_records":len(bus_rows),
             "source_line_and_transformer_incidents":len(line_rows),
             "with_substation_identifier":sum(x["sub_id"] is not None for x in bus_rows),
             "facility_to_original_bus_identity_verified":False,
             "generator_injection_approved":False,
             "note":"Trace retains source substation IDs and real first-hop topology for independent crosswalk research only."}
    out.with_suffix(".json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    print(pd.DataFrame(bus_rows).to_string(index=False))
    return summary


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--network",type=Path,required=True)
    a.add_argument("--candidates",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--plant-id",default="6008")
    a.add_argument("--max-buses",type=int,default=10)
    v=a.parse_args()
    trace(v.network,v.candidates,v.out,v.plant_id,v.max_buses)


if __name__=="__main__":
    main()
