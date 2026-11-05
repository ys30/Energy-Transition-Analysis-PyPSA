"""Fail-closed cross-dataset temporal join audit: EFS future demand vs EIA-930 2024.

This verifies actual archived fields and coverage, and refuses hourly joins
when physical UTC, weather year, BA-to-zone and provenance are not authenticated.
It intentionally never generates an aligned dataset from undocumented ordinals.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

EXPECTED_YEARS={2030,2040,2050}
EXPECTED_OBSERVED_YEAR=2024

def audit(efs:pd.DataFrame,eia:pd.DataFrame,source_sha256:dict)->dict:
    ekeys={"year","state","reeds_zone","local_hour_id","allocated_mw"}
    okeys={"season","period","respondent","fueltype","reported_signed_net_mwh"}
    if not ekeys.issubset(efs):raise ValueError("Missing original EFS ordinal source fields")
    if not okeys.issubset(eia):raise ValueError("Missing original EIA-930 UTC-source fields")
    if efs[list(ekeys)].isna().any().any() or efs.duplicated(["year","state","reeds_zone","local_hour_id"]).any():
        raise ValueError("Invalid EFS hour uniqueness")
    if eia[list(okeys)].isna().any().any() or eia.duplicated(["season","period","respondent","fueltype"]).any():
        raise ValueError("Invalid EIA observed timestamp uniqueness")
    if set(efs.year)!=EXPECTED_YEARS:raise ValueError("Unexpected EFS projection years")
    if set(efs.local_hour_id)!=set(range(1,8761)):raise ValueError("EFS ordinal coverage invalid")
    zones=efs[["state","reeds_zone"]].drop_duplicates()
    if len(zones)!=20:raise ValueError("Expected exactly 20 EFS zones")
    ecounts=efs.groupby(["year","state","reeds_zone"]).size()
    if len(ecounts)!=60 or not ecounts.eq(8760).all():raise ValueError("EFS per-zone hour coverage invalid")
    periods=pd.to_datetime(eia.period,utc=True,errors="raise")
    if set(periods.dt.year)!={EXPECTED_OBSERVED_YEAR}:raise ValueError("Observed archive not 2024")
    if set(eia.respondent)!={"CISO","BPAT"} or set(eia.fueltype)!={"SUN","WND"}:
        raise ValueError("Unexpected BA/fuel data population")
    if set(eia.season)!={"winter","spring","summer","autumn"}:
        raise ValueError("Incomplete four-week season population")
    oc=eia.groupby(["season","respondent","fueltype"]).size()
    if len(oc)!=16 or not oc.eq(168).all():raise ValueError("Observed EIA 168h windows incomplete")
    for _,g in eia.groupby(["season","respondent","fueltype"]):
        p=pd.DatetimeIndex(pd.to_datetime(g.period,utc=True)).sort_values()
        if not (p[1:]-p[:-1]==pd.Timedelta(hours=1)).all():
            raise ValueError("EIA consecutive hour coverage incomplete")
    flags={
        "efs_source_LocalHourID_to_UTC_independently_verified":False,
        "efs_2040_calendar_leap_alignment_independently_verified":False,
        "efs_to_eia930_weather_year_identity_verified":False,
        "efs_reeds_zone_to_eia930_ba_mapping_certified":False,
        "observed_eia930_net_generation_is_uncurtailed_availability":False,
        "future_generation_capacity_normalization_certified":False
    }
    failed=[name for name,ok in flags.items() if not ok]
    return {
        "status":"FAIL_CLOSED_CROSS_SOURCE_JOIN_NOT_ADMITTED",
        "verified_source_EFS_projection_years":sorted(EXPECTED_YEARS),
        "verified_efs_zones":len(zones),
        "verified_efs_hours_per_zone_per_year":8760,
        "verified_source_eia930_observed_year":2024,
        "verified_eia930_complete_seasonal_panels":len(oc),
        "verified_eia930_hours_per_panel":168,
        "source_sha256":source_sha256,
        "join_admission_flags":flags,
        "refusal_reasons":failed,
        "joined_hourly_output_rows":0,
        "weather_synchronized_power_dispatch_admitted":False,
        "original_EFS_load_source_values_mutated":False,
        "warning":"2024 signed BA net generation is not time-synchronous weather potential for projected 2030/2040/2050 source ordinal EFS demand."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-zonal",type=Path,required=True)
    p.add_argument("--eia930-seasonal",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    hashes={"efs_zonal_source_sha256":hashlib.sha256(a.efs_zonal.read_bytes()).hexdigest(),
            "eia930_2024_observed_source_sha256":hashlib.sha256(a.eia930_seasonal.read_bytes()).hexdigest()}
    r=audit(pd.read_csv(a.efs_zonal,compression="infer"),pd.read_csv(a.eia930_seasonal),hashes)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
