"""Search nearby, voltage-compatible real buses for documented facility leads.

Multiple geography/voltage candidates are for documentary research only.
Neither a coordinate match nor a voltage match establishes a physical POI.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pypsa

from .eia860_western_network_coverage import standardize


def haversine_km(latitude, longitude, latitudes, longitudes):
    p1=np.radians(float(latitude))
    p2=np.radians(np.asarray(latitudes,dtype=float))
    dphi=p2-p1
    dlambda=np.radians(np.asarray(longitudes,dtype=float)-float(longitude))
    a=np.sin(dphi/2)**2+np.cos(p1)*np.cos(p2)*np.sin(dlambda/2)**2
    return 6371.0088*2*np.arcsin(np.sqrt(np.clip(a,0,1)))


def audit(leads_path: Path, candidates_path: Path, network_path: Path,
          out: Path, radius_km: float=75.0, max_per_plant: int=10):
    if not np.isfinite(radius_km) or radius_km<=0 or max_per_plant<1:
        raise ValueError("Invalid search radius or maximum candidates")
    leads=pd.read_csv(leads_path,dtype={"plant_id":"string"})
    candidates=pd.read_csv(candidates_path,dtype={"plant_id":"string","nearest_candidate_bus":"string"})
    needed_l={"plant_id","documented_voltage_kv","network_bus_id","independent_electrical_bus_match_verified"}
    needed_c={"plant_id","state","plant_latitude","plant_longitude","nearest_candidate_bus"}
    if needed_l-set(leads) or needed_c-set(candidates):
        raise ValueError("Missing source documentary or geographic candidate columns")
    if leads.empty or leads.plant_id.isna().any() or leads.plant_id.duplicated().any():
        raise ValueError("Invalid facility leads")
    if candidates.plant_id.isna().any() or candidates.plant_id.duplicated().any():
        raise ValueError("Invalid geographic candidates")
    if leads.network_bus_id.notna().any() or not leads.independent_electrical_bus_match_verified.astype("string").str.lower().eq("false").all():
        raise ValueError("Unverified facility leads cannot claim original bus identity")
    joined=leads.merge(candidates.drop(columns=["plant_name"],errors="ignore"),on="plant_id",how="left",validate="one_to_one")
    if joined.nearest_candidate_bus.isna().any():
        raise ValueError("Unmatched facility geographic candidate")
    n=pypsa.Network(str(network_path))
    b=n.buses.copy()
    required_bus={"x","y","state","v_nom"}
    if required_bus-set(b):
        raise ValueError("Missing network bus location, state or voltage")
    b["state_code"]=standardize(b.state)
    b["latitude"]=pd.to_numeric(b.y,errors="coerce")
    b["longitude"]=pd.to_numeric(b.x,errors="coerce")
    b["voltage_kv"]=pd.to_numeric(b.v_nom,errors="coerce")
    b=b.loc[b.latitude.between(25,50)&b.longitude.between(-125,-102)&b.voltage_kv.gt(0)].copy()
    rows=[]
    summary=[]
    for r in joined.itertuples(index=False):
        try:
            voltages=[float(k.strip()) for k in str(r.documented_voltage_kv).split(";")]
        except ValueError as ex:
            raise ValueError("Invalid documented switchyard voltages") from ex
        if not voltages or not all(np.isfinite(v) and v>0 for v in voltages):
            raise ValueError("Invalid documented switchyard voltages")
        state=str(r.state)
        subset=b.loc[b.state_code.eq(state)].copy()
        if subset.empty:
            raise ValueError("No candidate network buses in plant state")
        lat=float(r.plant_latitude);lon=float(r.plant_longitude)
        if not 25<=lat<=50 or not -125<=lon<=-102:
            raise ValueError("Invalid plant coordinates")
        subset["distance_km"]=haversine_km(lat,lon,subset.latitude,subset.longitude)
        geographic_local=subset.loc[subset.distance_km.le(radius_km)]
        compatible_mask=subset.voltage_kv.apply(lambda x:any(abs(x-v)<0.01 for v in voltages))
        compatible_state=subset.loc[compatible_mask].copy()
        local=compatible_state.loc[compatible_state.distance_km.le(radius_km)]
        local=local.sort_values(["distance_km","voltage_kv"]).head(max_per_plant)
        for bus_id,bus in local.iterrows():
            line_count=int(((n.lines.bus0.astype(str)==str(bus_id))|(n.lines.bus1.astype(str)==str(bus_id))).sum())
            transformer_count=int(((n.transformers.bus0.astype(str)==str(bus_id))|(n.transformers.bus1.astype(str)==str(bus_id))).sum())
            rows.append({"plant_id":str(r.plant_id),"plant_name":str(r.plant_name),
                         "documented_facility_voltages_kv":r.documented_voltage_kv,
                         "candidate_bus_id":str(bus_id),"candidate_bus_voltage_kv":float(bus.voltage_kv),
                         "distance_km":round(float(bus.distance_km),4),
                         "connected_lines":line_count,"connected_transformers":transformer_count,
                         "is_original_geographic_nearest_bus":str(bus_id)==str(r.nearest_candidate_bus),
                         "electrical_connection_verified":False,
                         "approved_for_generator_injection":False,
                         "status":"voltage_geography_candidate_only"})
        summary.append({"plant_id":str(r.plant_id),"plant_name":str(r.plant_name),
                        "same_state_voltage_compatible_candidates_within_radius":int(len(local)),
                        "nearest_compatible_distance_km":float(local.distance_km.min()) if not local.empty else None,
                        "nearest_compatible_distance_anywhere_same_state_km":float(compatible_state.distance_km.min()) if not compatible_state.empty else None,
                        "geographic_buses_within_radius":int(len(geographic_local)),
                        "geographic_bus_voltage_counts_within_radius":{str(k):int(v) for k,v in geographic_local.voltage_kv.value_counts().sort_index().items()},
                        "documented_facility_bus_approved":False})
    out.parent.mkdir(parents=True,exist_ok=True)
    columns=["plant_id","plant_name","documented_facility_voltages_kv","candidate_bus_id",
             "candidate_bus_voltage_kv","distance_km","connected_lines","connected_transformers",
             "is_original_geographic_nearest_bus","electrical_connection_verified",
             "approved_for_generator_injection","status"]
    pd.DataFrame(rows,columns=columns).to_csv(out,index=False)
    report={"radius_km":radius_km,"max_candidates_per_plant":max_per_plant,
            "facility_leads":len(summary),"voltage_compatible_geographic_candidates":len(rows),
            "plant_summaries":summary,"independently_verified_electrical_connections":0,
            "generator_injections_approved":0,
            "warning":"Voltage-compatible local buses remain speculative geographical candidates and must not be used as POI crosswalks."}
    out.with_suffix(".json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    return report


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--leads",type=Path,required=True)
    a.add_argument("--candidates",type=Path,required=True)
    a.add_argument("--network",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    a.add_argument("--radius-km",type=float,default=75)
    a.add_argument("--max-per-plant",type=int,default=10)
    z=a.parse_args()
    audit(z.leads,z.candidates,z.network,z.out,z.radius_km,z.max_per_plant)


if __name__=="__main__":
    main()
