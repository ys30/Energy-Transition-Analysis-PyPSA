"""Join official 2024 EIA-860 generator identities to GIS-only bus candidates.

This is a generator-level *staging* table, not a populated PyPSA network or
an approved powerplant-to-electrical-bus crosswalk.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

def stage_generator_candidates(candidates:pd.DataFrame, generators:pd.DataFrame):
    c=candidates.copy()
    g=generators.copy()
    req_c={"plant_id","nearest_candidate_bus","distance_km","state",
           "assignment_status","electrical_connection_verified"}
    req_g={"plant_id","generator_id","status","capacity_mw","fuel","state",
           "crosswalk_status","ba_code"}
    if req_c-set(c) or req_g-set(g):
        raise ValueError("Missing official candidate/generator fields")
    for frame,cols in ((c,["plant_id"]),(g,["plant_id","generator_id"])):
        for col in cols:
            frame[col]=frame[col].astype("string").str.strip()
        if frame[cols].isna().any().any() or frame[cols].eq("").any().any() or frame.duplicated(cols).any():
            raise ValueError("Duplicate or missing source identity")
    if c.nearest_candidate_bus.isna().any() or c.nearest_candidate_bus.astype(str).str.strip().eq("").any():
        raise ValueError("Candidate bus ID absent")
    if not c.assignment_status.eq("geographic_candidate_only").all():
        raise ValueError("Unexpected already-admitted geographic candidate")
    if not c.electrical_connection_verified.astype("string").str.lower().eq("false").all():
        raise ValueError("Geographic candidate cannot attest electrical connection")
    c["distance_km"]=pd.to_numeric(c.distance_km,errors="raise")
    if not np.isfinite(c.distance_km.to_numpy(dtype=float)).all() or (c.distance_km<0).any():
        raise ValueError("Invalid geographic distance")
    g["capacity_mw"]=pd.to_numeric(g.capacity_mw,errors="coerce")
    g["status"]=g.status.astype("string").str.strip().str.upper()
    g["crosswalk_status"]=g.crosswalk_status.astype("string").str.strip().str.lower()
    g["state"]=g.state.astype("string").str.strip().str.upper()
    c["state"]=c.state.astype("string").str.strip().str.upper()
    op=g.loc[g.status.eq("OP")&g.crosswalk_status.eq("matched") &
              g.capacity_mw.gt(0)&np.isfinite(g.capacity_mw.to_numpy(dtype=float))].copy()
    if op.empty:raise ValueError("No official operating, BA-matched generators")
    subset=op.merge(c[["plant_id","state","nearest_candidate_bus","distance_km"]],
                    on="plant_id",how="left",validate="many_to_one",
                    suffixes=("_eia","_candidate"),indicator=True)
    mismatched=subset.loc[subset["_merge"].eq("both") &
                          subset.state_eia.ne(subset.state_candidate)]
    if not mismatched.empty:
        raise ValueError("EIA generator state differs from coordinate candidate state")
    subset["has_geographic_candidate"]=subset["_merge"].eq("both")
    subset["electrical_connection_verified"]=False
    subset["pypsa_generator_creation_approved"]=False
    subset["candidate_status"]=subset.has_geographic_candidate.map({
        True:"candidate_only_no_approved_POI",
        False:"missing_geographic_candidate"})
    cols=["plant_id","generator_id","state_eia","ba_code","fuel","capacity_mw",
          "nearest_candidate_bus","distance_km","candidate_status",
          "has_geographic_candidate","electrical_connection_verified",
          "pypsa_generator_creation_approved"]
    out=subset[cols].copy().rename(columns={"state_eia":"state"})
    out["nearest_candidate_bus"]=out.nearest_candidate_bus.astype("string")
    with_candidate=out.has_geographic_candidate
    total_mw=float(out.capacity_mw.sum())
    mapped_mw=float(out.loc[with_candidate,"capacity_mw"].sum())
    report={
        "source":"official EIA-860 2024 operating and BA-matched generator records",
        "official_2024_operating_generator_rows":len(out),
        "candidate_generator_rows":int(with_candidate.sum()),
        "unmapped_generator_rows":int((~with_candidate).sum()),
        "candidate_generator_plant_count":int(out.loc[with_candidate,"plant_id"].nunique()),
        "all_operating_nameplate_mw":total_mw,
        "candidate_geographic_nameplate_mw":mapped_mw,
        "unmapped_nameplate_mw":float(out.loc[~with_candidate,"capacity_mw"].sum()),
        "candidate_nameplate_fraction":mapped_mw/total_mw,
        "candidate_over_50km_generator_rows":int((with_candidate & out.distance_km.gt(50)).sum()),
        "candidate_over_50km_nameplate_mw":float(out.loc[
            with_candidate & out.distance_km.gt(50),"capacity_mw"].sum()),
        "electrical_connections_verified":0,
        "source_bus_ids_utility_authenticated":False,
        "nameplate_as_hourly_generation_approved":False,
        "future_2030_2040_2050_generator_fleet_verified":False,
        "actual_network_generators_added":0,
        "empirical_western_opf_ready":False,
        "note":"BA labels, nearest geographic bus and historic EIA operating MW do not establish physical POI, dispatchable capacity or future fleet.",
    }
    if abs(mapped_mw+report["unmapped_nameplate_mw"]-total_mw)>1e-5:
        raise ValueError("Operating generator capacity coverage fails conservation")
    return out,report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidates",required=True,type=Path)
    p.add_argument("--generators",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    out,r=stage_generator_candidates(
        pd.read_csv(a.candidates,dtype={"plant_id":"string","nearest_candidate_bus":"string"}),
        pd.read_csv(a.generators,dtype={"plant_id":"string","generator_id":"string"}))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.out,index=False)
    a.out.with_suffix(".json").write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))

if __name__=="__main__":main()
