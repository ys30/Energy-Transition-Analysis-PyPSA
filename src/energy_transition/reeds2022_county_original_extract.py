"""Read authenticated original ReEDS county wind/PV 2012 CF in chunks.

Emits derived 4-state instantaneous CF only. Strict opt-in schema arguments
prevent guesses about CSV column names, CF encoding, and PV capacity basis.
Does not certify a demand-hour-ending energy join or solve any optimization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

from energy_transition.reeds2022_county_state_resources import (
    STATES, validate_capacity_key_match, state_cf_from_county_resource_matrix,
    WIND_COUNTY_MD5, PV_COUNTY_MD5, WIND_COUNTY_CAPACITY_MD5,
    PV_COUNTY_CAPACITY_MD5,
)
from energy_transition.reeds2022_real_resource_intake import (
    inspect_weather_index, require_md5, decode,
)

OFFICIAL = {
    "wind": (WIND_COUNTY_MD5, WIND_COUNTY_CAPACITY_MD5),
    "pv": (PV_COUNTY_MD5, PV_COUNTY_CAPACITY_MD5),
}
CHUNK = 168


def assemble_capacity_keys(frame, *, key_col=None, class_col=None, region_col=None):
    """Avoid inventing publisher CSV schema; explicit user-audited columns only."""
    if key_col:
        if key_col not in frame.columns:
            raise ValueError("Missing authenticated capacity key column")
        keys=frame[key_col].astype("string")
    else:
        if not class_col or not region_col or not {class_col,region_col}.issubset(frame.columns):
            raise ValueError("Explicit class_col and region_col are required")
        regions=frame[region_col].astype("string")
        regions=regions.where(regions.str.startswith("p"),"p"+regions)
        keys=frame[class_col].astype("string")+"|"+regions
    if keys.isna().any():
        raise ValueError("Null supply curve resource identifier")
    return keys.tolist()


def audit_and_extract(*, tech, h5_path, supply_path, capacity_key_col,
                      class_col, region_col, capacity_mw_col,
                      capacity_basis, cf_encoded_scale, out_dir, chunk_size=CHUNK):
    if tech not in OFFICIAL:
        raise ValueError("Unsupported technology")
    out_dir=Path(out_dir)
    out_dir.mkdir(parents=True,exist_ok=True)
    h5_digest,sc_digest=OFFICIAL[tech]
    require_md5(Path(h5_path),h5_digest)
    require_md5(Path(supply_path),sc_digest)

    supply=pd.read_csv(supply_path,dtype=str)
    if capacity_mw_col not in supply.columns:
        raise ValueError("Explicit capacity column absent from publisher source")
    supply_keys=assemble_capacity_keys(supply,key_col=capacity_key_col,
                                       class_col=class_col,region_col=region_col)
    capacity=pd.to_numeric(supply[capacity_mw_col],errors="raise")
    with h5py.File(h5_path,"r") as h:
        if not {"data","index_0","columns"}.issubset(h.keys()):
            raise ValueError("Publisher HDF5 required datasets absent")
        names=decode(h["columns"][:])
        rows,clock=inspect_weather_index(h["index_0"][:])
        data=h["data"]
        if data.ndim!=2 or data.shape!=(clock["index_rows_total"],len(names)):
            raise ValueError("Original HDF5 data matrix dimensions invalid")
        if not np.array_equal(rows,np.arange(rows[0],rows[-1]+1)):
            raise ValueError("Noncontiguous reference-year source index")
        table=validate_capacity_key_match(
            names,supply_keys,capacity,capacity_basis=capacity_basis,tech=tech)
        # Exact HDF5 order retained by merge(...,sort=False).
        if table.column.tolist()!=names:
            raise ValueError("Capacity key order did not preserve native HDF5 order")
        if np.issubdtype(data.dtype,np.integer) and cf_encoded_scale is None:
            raise ValueError("Integer encoded publisher CF has no verified scale")

        parts=[]
        minima=np.inf
        maxima=-np.inf
        for offset in range(0,len(rows),chunk_size):
            batch=np.asarray(data[rows[offset:offset+chunk_size],:])
            if not np.isfinite(batch).all():
                raise ValueError("Nonfinite original HDF5 resource values")
            minima=min(minima,float(batch.min()))
            maxima=max(maxima,float(batch.max()))
            parts.append(state_cf_from_county_resource_matrix(
                batch,table,tech=tech,native_cf_scale=cf_encoded_scale,
                pv_capacity_basis=capacity_basis if tech=="pv" else None))
    state_cf=pd.concat(parts,ignore_index=True)
    if len(state_cf)!=8760 or state_cf.isna().any().any():
        raise ValueError("State profile not complete")
    # Source native labels are timezone-naive, but publisher specifies fixed CST.
    # These are instantaneous CF, not hour-ending MWh.
    idx=pd.date_range("2012-01-01",periods=8760,freq="h",tz="Etc/GMT+6")
    state_cf.insert(0,"source_instantaneous_CST",idx.astype(str))
    state_cf.to_csv(out_dir/f"reeds2022_{tech}_2012_four_state_instantaneous_cf.csv",index=False)
    fips=table.state_fips.astype(str)
    state_capacity={state:float(table.loc[fips.eq(code),"capacity_mw"].sum())
                    for state,code in STATES.items()}
    info={
        "status":"ORIGINAL_COUNTY_SOURCE_TO_STATE_INSTANTANEOUS_CF",
        "empirical_hour_energy_join_admitted":False,
        "weather_adjusted_LP_completed":False,
        "source_h5_md5":h5_digest,
        "source_supply_curve_md5":sc_digest,
        "original_hdf5_dtype":str(data.dtype),
        "original_2012_native_raw_min":minima,
        "original_2012_native_raw_max":maxima,
        "capacity_csv_columns":list(supply.columns),
        "explicit_source_capacity_mw_column":capacity_mw_col,
        "explicit_source_capacity_basis":capacity_basis,
        "native_cf_encoding_scale":cf_encoded_scale,
        "region_class_column_count":len(names),
        "2012_source_clock":clock,
        "state_available_capacity_mw":state_capacity,
        "state_instantaneous_cf_stats":{
            state:{"min":float(state_cf[state].min()),
                   "max":float(state_cf[state].max()),
                   "mean":float(state_cf[state].mean())}
            for state in STATES},
        "output_is_2012_weather_not_2030_2050_forecast":True,
    }
    (out_dir/f"reeds2022_{tech}_2012_state_cf_source_manifest.json").write_text(
        json.dumps(info,indent=2)+"\n")
    return info


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--technology",choices=sorted(OFFICIAL),required=True)
    p.add_argument("--h5",type=Path,required=True)
    p.add_argument("--capacity-csv",type=Path,required=True)
    p.add_argument("--capacity-key-col")
    p.add_argument("--class-col")
    p.add_argument("--region-col")
    p.add_argument("--capacity-mw-col",required=True)
    p.add_argument("--capacity-basis",choices=["ac","dc"],required=True)
    p.add_argument("--cf-encoded-scale",type=float)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    if args.technology=="wind" and args.capacity_basis!="ac":
        p.error("Wind supply MW must use verified AC basis")
    info=audit_and_extract(
        tech=args.technology,h5_path=args.h5,supply_path=args.capacity_csv,
        capacity_key_col=args.capacity_key_col,
        class_col=args.class_col,region_col=args.region_col,
        capacity_mw_col=args.capacity_mw_col,
        capacity_basis=args.capacity_basis,cf_encoded_scale=args.cf_encoded_scale,
        out_dir=args.out)
    print(json.dumps(info,indent=2))


if __name__=="__main__":
    main()
