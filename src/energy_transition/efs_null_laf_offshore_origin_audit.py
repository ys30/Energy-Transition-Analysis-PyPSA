"""Trace null LAF buses to pinned upstream offshore-bus insertion.

The evidence checks explicit substation_off flags and source-defined bus IDs,
not just Pd==0. No source LAF is modified, zeroed or imputed.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np

PIN="338af9912addbaf038c6098fe27e1e6ef099d8aa"
OFFSHORE_ID_START=3008161


def audit_offshore_laf_origin(buses:pd.DataFrame, source:str)->dict:
    needed={"Pd","LAF_state","substation_off","state","reeds_state","reeds_zone"}
    if not needed.issubset(buses.columns):
        raise ValueError(f"Missing upstream bus attributes: {sorted(needed-set(buses.columns))}")
    anchors=[
        'gdf_bus["LAF_state"] = gdf_bus["Pd"] / group_sums',
        "n = add_offshore_buses(n, offshore_buses)",
        "offshore_buses.index = np.arange(3008161, 3008161 + len(offshore_buses))",
        "Pd=0,",
        "substation_off=True,",
    ]
    if not all(x in source for x in anchors):
        raise ValueError("Pinned offshore-bus LAF construction source anchors missing")
    if source.index(anchors[0])>=source.index(anchors[1]):
        raise ValueError("Upstream offshore construction does not follow LAF computation")
    laf=pd.to_numeric(buses["LAF_state"],errors="coerce")
    pdv=pd.to_numeric(buses["Pd"],errors="coerce")
    missing=~np.isfinite(laf.to_numpy(dtype=float))
    sub_off=buses["substation_off"].fillna(False).eq(True).to_numpy()
    idx=pd.to_numeric(pd.Index(buses.index).astype(str),errors="coerce").to_numpy()
    in_offshore_id_range=np.isfinite(idx)&(idx>=OFFSHORE_ID_START)
    nulls=buses.loc[missing].copy()
    nulls["_Pd"]=pdv.loc[missing]
    nulls["_offshore_flag"]=sub_off[missing]
    nulls["_offshore_id_range"]=in_offshore_id_range[missing]
    records=[]
    for bus,row in nulls.iterrows():
        records.append({
            "bus_id":str(bus),
            "state":str(row["state"]),
            "reeds_state":str(row["reeds_state"]),
            "reeds_zone":str(row["reeds_zone"]),
            "Pd":None if not np.isfinite(row["_Pd"]) else float(row["_Pd"]),
            "substation_off":bool(row["_offshore_flag"]),
            "in_pinned_generated_offshore_id_range":bool(row["_offshore_id_range"]),
        })
    return {
        "pinned_upstream_commit":PIN,
        "upstream_LAF_assigned_before_offshore_addition":True,
        "added_offshore_Pd_is_zero_in_source":True,
        "upstream_added_offshore_LAF_explicitly_assigned":False,
        "network_bus_count":int(len(buses)),
        "null_laf_bus_count":int(missing.sum()),
        "null_laf_offshore_flag_true":int((missing&sub_off).sum()),
        "null_laf_offshore_generated_id_range":int((missing&in_offshore_id_range).sum()),
        "null_laf_offshore_both_indicators":int((missing&sub_off&in_offshore_id_range).sum()),
        "null_laf_finite_zero_Pd":int((missing&np.isfinite(pdv.to_numpy(dtype=float))&pdv.eq(0).to_numpy()).sum()),
        "all_null_laf_buses_match_pinned_offshore_insertion_signature":bool(
            missing.any() and np.all(sub_off[missing]&in_offshore_id_range[missing])),
        "null_laf_buses":records,
        "missing_laf_values_zero_imputed":False,
        "original_full_state_geography_certified":False,
        "four_state_EFS_load_admitted":False,
        "interpretation":"ID/flag/zero-Pd and upstream insertion order establish source-compatible offshore origin if all flags match; no allocation coefficients are changed.",
    }


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--upstream-source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    n=pypsa.Network(str(a.network))
    r=audit_offshore_laf_origin(n.buses,a.upstream_source.read_text())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in r.items() if k!="null_laf_buses"},indent=2))
    print("First null LAF bus records:",json.dumps(r["null_laf_buses"][:5],indent=2))

if __name__=="__main__":
    main()
