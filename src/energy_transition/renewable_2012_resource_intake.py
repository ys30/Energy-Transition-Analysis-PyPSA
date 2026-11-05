"""Fail-closed intake audit for site-level 2012 NLR renewable resource CSVs.

Supports WIND Toolkit wind speed and NSRDB solar irradiance source outputs.
No automatic conversion to generation capacity factors or joins with EFS.
The source file must be separately downloaded with an authenticated API query.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

SOURCE_COLUMN_MAP = {
    "wind_toolkit": ("windspeed_100m",),
    "nsrdb": ("ghi", "dni", "dhi"),
}
REQUIRED_METADATA = {
    "product","source_url","source_year","requested_utc","requested_leap_day",
    "requested_interval_minutes","site_lat","site_lon",
    "source_time_interpretation","source_data_timezone_hours",
    "original_api_query_redacted",
}
REQUIRED_TIME = ("Year","Month","Day","Hour","Minute")

def evaluate(frame:pd.DataFrame, metadata:dict)->dict:
    missing=REQUIRED_METADATA-set(metadata)
    if missing: raise ValueError("Missing product metadata: "+", ".join(sorted(missing)))
    product=metadata["product"]
    if product not in SOURCE_COLUMN_MAP:
        raise ValueError("Unknown renewable resource source family")
    if not isinstance(metadata["requested_utc"],bool) or metadata["requested_utc"] is not True:
        raise ValueError("Explicit UTC request required")
    if not isinstance(metadata["requested_leap_day"],bool) or metadata["requested_leap_day"] is not False:
        raise ValueError("Explicit nonleap 8760-hour request required")
    if metadata["requested_interval_minutes"]!=60 or metadata["source_year"]!=2012:
        raise ValueError("Only explicit candidate 2012 hourly resource series are accepted")
    if metadata["source_data_timezone_hours"]!=0:
        raise ValueError("Source header must identify UTC data timezone")
    if metadata["source_time_interpretation"] not in ("interval_start","interval_midpoint","interval_end"):
        raise ValueError("Unknown sample-time meaning: manual source review required")
    if not str(metadata["source_url"]).startswith("https://"):
        raise ValueError("Source URL must be HTTPS")
    if not str(metadata["original_api_query_redacted"]).strip():
        raise ValueError("Missing redacted original API request")
    lat=float(metadata["site_lat"]);lon=float(metadata["site_lon"])
    if not (np.isfinite(lat) and np.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
        raise ValueError("Invalid site location")
    needed=set(REQUIRED_TIME)|set(SOURCE_COLUMN_MAP[product])
    if not needed.issubset(frame):
        raise ValueError("Missing source time/resource columns: "+", ".join(sorted(needed-set(frame))))
    if frame[list(needed)].isna().any().any():
        raise ValueError("Incomplete time or renewable resource values")
    if len(frame)!=8760:
        raise ValueError("Expected exactly 8760 source hours after explicit leap exclusion")
    components=frame[list(REQUIRED_TIME)].apply(pd.to_numeric,errors="raise")
    if not np.isfinite(components.to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite time components")
    if not np.array_equal(components.to_numpy(),components.to_numpy(dtype=int)):
        raise ValueError("Fractional source time component")
    minutes=set(components["Minute"].astype(int))
    if len(minutes)!=1:raise ValueError("Inconsistent source minute convention")
    stamps=pd.to_datetime(
        pd.DataFrame({
            "year":components["Year"].astype(int),
            "month":components["Month"].astype(int),
            "day":components["Day"].astype(int),
            "hour":components["Hour"].astype(int),
            "minute":components["Minute"].astype(int),
        }),utc=True,errors="raise")
    expected=pd.date_range("2012-01-01", "2013-01-01",freq="h",inclusive="left",tz="UTC")
    expected=expected[~((expected.month==2)&(expected.day==29))]
    expected=expected+pd.Timedelta(minutes=next(iter(minutes)))
    actual=pd.DatetimeIndex(stamps)
    if actual.has_duplicates or not actual.is_monotonic_increasing:
        raise ValueError("Duplicate or nonmonotonic resource timestamps")
    if not actual.equals(expected):
        raise ValueError("Source calendar/UTC hours do not match explicit 2012 nonleap template")
    statistics={}
    for column in SOURCE_COLUMN_MAP[product]:
        values=pd.to_numeric(frame[column],errors="raise").to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values<0).any():
            raise ValueError(f"Invalid nonnegative resource measurement: {column}")
        if column in ("ghi","dni","dhi") and (values>1600).any():
            raise ValueError("Solar irradiance over conservative intake screen")
        if column=="windspeed_100m" and (values>100).any():
            raise ValueError("Wind speed over conservative intake screen")
        statistics[column]={"minimum":float(values.min()),"maximum":float(values.max()),
                            "mean":float(values.mean()),"zero_hours":int((values==0).sum())}
    return {
        "status":"RESOURCE_SOURCE_TIME_AND_VALUES_INTAKE_VALIDATED",
        "product":product,"source_year":2012,
        "source_hourly_count":len(actual),"utc_time_keys_complete":True,
        "source_time_interpretation_reviewed":metadata["source_time_interpretation"],
        "source_utc_minute_component":next(iter(minutes)),
        "site_lat":lat,"site_lon":lon,
        "resource_statistics":statistics,
        "is_meteorological_resource_not_generator_dispatch":True,
        "generator_capacity_factor_computed":False,
        "source_representativeness_of_reeds_zone_verified":False,
        "original_EFS_LocalHourID_utc_mapping_verified":False,
        "EFS_load_resource_join_admitted":False,
        "physical_Western_OPF_admitted":False,
        "warning":"Intake verification checks one source-site's nonleap UTC resource hours only. It cannot certify temporal or geographic alignment to future EFS projections."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-csv",required=True,type=Path)
    p.add_argument("--metadata",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    meta=json.loads(a.metadata.read_text())
    r=evaluate(pd.read_csv(a.source_csv),meta)
    r["source_csv_sha256"]=hashlib.sha256(a.source_csv.read_bytes()).hexdigest()
    r["source_metadata_sha256"]=hashlib.sha256(a.metadata.read_bytes()).hexdigest()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps(r,indent=2))
if __name__=="__main__":main()
