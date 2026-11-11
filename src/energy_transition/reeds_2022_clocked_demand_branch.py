"""ReEDS-2022 explicitly clocked state-demand source branch; never EFS2020 LocalHourID.
The source HDF5 is publisher MD5 authenticated, UTC-06, 2012 calendar, hour-ending.
Wind/PV have distinct instantaneous-on-hour semantics: no silent weather join.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np
import pandas as pd

RECORD="https://zenodo.org/records/18461543"
NAME="demand_EFS_REFERENCE.h5"
MD5="7b2055d43200744a16a8c4fed68b1a17"
STATES=("AZ","CO","ID","WY")
MODEL_YEARS=(2030,2040,2050)
HOURS=8760

def check_fixed_cst_native_labels(raw):
    decoded=[x.decode("utf8") if isinstance(x,bytes) else str(x) for x in raw]
    if len(decoded)!=HOURS or len(set(decoded))!=HOURS:
        raise ValueError("ReEDS 2022 source clock incomplete or duplicated")
    if not all(x.endswith("-06:00") for x in decoded):
        raise ValueError("ReEDS source offset is not the certified constant CST -06:00")
    idx=pd.to_datetime(decoded,utc=True)
    expected=pd.date_range("2012-01-01 00:00:00-06:00",periods=HOURS,freq="h").tz_convert("UTC")
    if not pd.DatetimeIndex(idx).equals(expected):
        raise ValueError("ReEDS 2022 native timestamp/calendar structure mismatch")
    return {"native_first":decoded[0],"native_last":decoded[-1],
        "2012_Feb29_included":True,"2012_Dec31_removed":True,
        "hours":HOURS,"source_timezone":"CST UTC-06:00",
        "demand_interval":"hour-ending (publisher)"}

def verify_official_file(path):
    dig=hashlib.md5()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):dig.update(b)
    if dig.hexdigest()!=MD5:raise ValueError("Publisher MD5 mismatch: "+dig.hexdigest())
    return dig.hexdigest()

def prepare(path,years=MODEL_YEARS,states=STATES):
    import h5py
    verify_official_file(path)
    records=[];clock={}
    with h5py.File(path) as f:
        for year in years:
            key=str(year)
            if key not in f:raise ValueError("Missing demand year "+key)
            group=f[key]
            clock[key]=check_fixed_cst_native_labels(group["datetime"][:])
            for state in states:
                if state not in group:raise ValueError("Missing state "+state)
                arr=np.asarray(group[state][:],dtype=float)
                if arr.shape!=(HOURS,) or not np.isfinite(arr).all() or np.any(arr<0):
                    raise ValueError("Invalid native demand values "+state)
                records.append({"source":"ReEDS2022_EFS_REFERENCE","model_year":year,
                    "weather_year":2012,"state":state,"hours":HOURS,
                    "annual_demand_mwh":float(arr.sum()),
                    "peak_hourly_demand_mw":float(arr.max()),
                    "zero_demand_hours":int((arr==0).sum())})
    return pd.DataFrame(records),{
        "status":"REEDS2022_PUBLISHER_CLOCKED_DEMAND_VERIFIED",
        "source":RECORD,"file":NAME,"official_md5_verified":MD5,
        "model_years":list(years),"states":list(states),
        "native_clock_by_model_year":clock,
        "demand_unit":"gross end-use MWh/h",
        "demand_interval":"hour-ending",
        "legacy_EFS2020_LocalHourID_used":False,
        "legacy_EFS2020_UTC_certified":False,
        "renewable_join_admitted":False,
        "wind_solar_cf_semantics":"instantaneous on hour, not automatically a load hour-ending interval",
        "state_to_ReEDS_BA_geography_validated":False,
        "real_wind_solar_LP_solved":False,
        "third_party_data_license_resolved":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    summary,meta=prepare(args.source)
    args.out.mkdir(parents=True,exist_ok=True)
    summary.to_csv(args.out/"reeds2022_replacement_four_states_three_years.csv",index=False)
    (args.out/"reeds2022_replacement_source_clock_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print(summary.to_string(index=False))
    print("REEDS2022_DEMAND_CLOCK_ACCEPTED_REAL_RENEWABLE_JOIN_NOT_YET_ADMITTED")
if __name__=="__main__":main()
