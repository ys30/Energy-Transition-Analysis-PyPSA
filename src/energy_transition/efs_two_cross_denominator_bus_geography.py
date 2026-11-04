"""Inventory exact identity/geography of two cross-denominator LAF source buses.

No inferred original full_state, no geographic reassignment or imputation.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd
import numpy as np

TARGETS={"2030005":{"expected_native":"Nevada","expected_source_denominator":67028.96},
         "2013019":{"expected_native":"Washington","expected_source_denominator":9281.36}}


def inspect_bus_crossings(buses:pd.DataFrame)->dict:
    required={"Pd","LAF_state","state","reeds_state","reeds_zone"}
    if not required.issubset(buses.columns):
        raise ValueError("Required pinned network geography missing")
    names=buses.index.astype(str)
    reports=[]
    for bus_id,expected in TARGETS.items():
        ids=np.flatnonzero(names==bus_id)
        if len(ids)!=1:
            raise ValueError(f"Target bus missing or duplicate: {bus_id}")
        row=buses.iloc[int(ids[0])]
        if str(row["state"])!=expected["expected_native"]:
            raise ValueError(f"Unexpected current native state for {bus_id}")
        pdv=float(row["Pd"]); laf=float(row["LAF_state"])
        if pdv<=0 or laf<=0 or not np.isfinite(pdv+laf):
            raise ValueError("Expected strictly positive target Pd and LAF")
        denominator=pdv/laf
        if abs(denominator-expected["expected_source_denominator"])>1e-3:
            raise ValueError(f"Source denominator changed for bus {bus_id}")
        fields={}
        for f in ["state","reeds_state","reeds_zone","reeds_ba","county","balancing_area",
                  "interconnect","sub_id","substation_off","poi_bus","poi_sub","x","y","v_nom"]:
            if f in buses.columns:
                x=row[f]
                fields[f]=None if pd.isna(x) else (
                    bool(x) if isinstance(x,(bool,np.bool_)) else
                    float(x) if isinstance(x,(float,np.floating)) else str(x))
        reports.append({"bus_id":bus_id,"Pd":pdv,"LAF_state":laf,
                        "inferred_source_denominator_Pd":denominator,
                        "exported_geography":fields,
                        "original_full_state_verified":False})
    return {"target_bus_count":len(reports),"buses":reports,
            "source_full_state_recovered":False,
            "any_bus_geography_modified":False,
            "source_to_current_state_reassignment_certified":False,
            "empirical_EFS_admitted":False}


def main():
    import pypsa
    p=argparse.ArgumentParser()
    p.add_argument("--network",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=inspect_bus_crossings(pypsa.Network(str(a.network)).buses)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
