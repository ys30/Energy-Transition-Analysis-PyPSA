"""Independent publisher-file inspection: ReEDS 2022 EFS_REFERENCE HDF5.

Never equate this 2022 release with original 2020 EFS Reference/Moderate
source or silently copy its UTC/CST convention to original LocalHourID.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import h5py

CHECKSUM="7b2055d43200744a16a8c4fed68b1a17"
YEARS=(2030,2040,2050)
STATES=("AZ","CA","CO","ID","MT","NM","NV","OR","UT","WA","WY")

def verify_publisher_2012_clock(raw_datetimes):
    """Require exact 2012 CST UTC-06 sequence, Feb 29 kept and Dec 31 absent.

    This checks the *separate ReEDS2022 HDF5* native timeline, never EFS2020.
    """
    strings=[v.decode("utf-8") if isinstance(v,bytes) else str(v) for v in raw_datetimes]
    if len(strings)!=8760 or len(set(strings))!=8760:
        raise ValueError("Invalid ReEDS2022 native clock length or duplicate hours")
    if not all(s.endswith("-06:00") for s in strings):
        raise ValueError("ReEDS2022 source CST UTC-06 offset changed")
    times=pd.to_datetime(strings,utc=True,errors="raise")
    expected=pd.date_range(
        start="2012-01-01 00:00:00-06:00",
        end="2012-12-31 00:00:00-06:00",
        freq="h",inclusive="left",
    ).tz_convert("UTC")
    if len(expected)!=8760 or not pd.DatetimeIndex(times).equals(expected):
        raise ValueError("ReEDS2022 publisher 2012 CST leap/final-day chronology mismatch")
    return {
        "exact_2012_CST_UTC_minus_6_sequence_verified":True,
        "Feb_29_2012_included":True,
        "Dec_31_2012_omitted":True,
        "native_datetime_first":strings[0],
        "native_datetime_last":strings[-1],
        "native_time_index_hour_ending_semantics_only_from_publisher":True,
    }

def inspect(path):
    md5=hashlib.md5()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            md5.update(block)
    if md5.hexdigest()!=CHECKSUM:
        raise ValueError("Official Zenodo ReEDS2022 HDF5 MD5 mismatch")
    rows=[]
    samples={}
    with h5py.File(path,"r") as hf:
        keys=set(hf.keys())
        if not all(str(y) in keys for y in YEARS):
            raise ValueError("Requested ReEDS HDF5 model years unavailable")
        for year in YEARS:
            group=hf[str(year)]
            if "datetime" not in group:
                raise ValueError(f"Missing independently published datetime dataset in {year}")
            raw=group["datetime"][:]
            datetimes=[v.decode("utf-8") if isinstance(v,bytes) else str(v) for v in raw]
            clock_status=verify_publisher_2012_clock(raw)
            if not all(s in group for s in STATES):
                raise ValueError(f"Missing Western state profiles in {year}")
            samples[str(year)]={"first":datetimes[:3],"last":datetimes[-3:],
                                 "calendar_validation":clock_status,
                                 "unique_datetime_values":len(datetimes)}
            for state in STATES:
                values=np.asarray(group[state][:],dtype=float)
                if len(values)!=8760 or not np.isfinite(values).all() or (values<0).any():
                    raise ValueError(f"Invalid ReEDS projected demand {year}/{state}")
                rows.append({"release":"ReEDS 2022 EFS_REFERENCE (NOT original 2020 EFS)",
                             "model_year":year,"state":state,"source_8760_hours":8760,
                             "annual_state_profile_sum_mwh":float(values.sum()),
                             "hourly_source_peak_mw":float(values.max()),
                             "source_zero_hours":int((values==0).sum())})
    return rows,{
        "status":"OFFICIAL_REEDS_2022_HDF5_SOURCE_INSPECTED",
        "file":"demand_EFS_REFERENCE.h5","source_release":"ReEDS electricity demand profiles 2022",
        "publication_record":"https://zenodo.org/records/18461543",
        "original_publisher_md5":CHECKSUM,"verified_actual_md5":md5.hexdigest(),
        "sampled_model_years":list(YEARS),"western_state_profiles_inspected":len(STATES),
        "profiles_per_year_hours":8760,"source_datetime_samples":samples,
        "publisher_documented_timezone":"US Central Standard Time (UTC-06:00)",
        "publisher_documented_hour_format":"hour ending",
        "publisher_documented_weather_year":"2012 with final day removed",
        "legacy_EFS_2020_same_dataset_assertion":False,
        "legacy_EFS_2020_UTC_clock_certified":False,
        "synchronized_future_wind_solar_join_admitted":False,
        "Western_physical_OPF_admitted":False,
        "warning":"This is separate and later 2022 ReEDS input. Its source convention cannot certify original EFS2020 LocalHourID. The HDF5 datetime string should be independently interpreted before any join."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--h5",type=Path,required=True)
    p.add_argument("--out-csv",type=Path,required=True)
    p.add_argument("--out-json",type=Path,required=True)
    a=p.parse_args()
    rows,meta=inspect(a.h5)
    for target in (a.out_csv,a.out_json):target.parent.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(meta,indent=2)+"\n")
    print(json.dumps(meta,indent=2))
    print(pd.DataFrame(rows).to_string(index=False))
if __name__=="__main__":main()
