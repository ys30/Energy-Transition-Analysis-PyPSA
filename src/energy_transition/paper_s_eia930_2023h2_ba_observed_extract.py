"""Extract independently observed EIA-930 BA wind and solar from 2023 H2 raw ZIP.

Raw EIA flat-file labels are MW, not MWh. This script keeps reported MW
and optionally imputed/adjusted MW separate, and never confuses BA and state.
A one-hour average MW can be numerically converted to MWh only with explicit
measurement semantics; those are not established by the raw header alone.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from energy_transition.paper_s_eia930_2023half2_archive_inventory import EXPECTED_MD5

BAS=("PNM","PSCO","IPCO","WACM")
TECHS={"wind":"Wind","solar":"Solar"}
RAW_NAME="eia930-2023half2-balance.csv"
TIME_COL="UTC Time at End of Hour"
BA_COL="Balancing Authority"
START=pd.Timestamp("2023-07-01T00:00:00Z")
STOP=pd.Timestamp("2023-07-08T00:00:00Z")


def extract(src, start=START, stop=STOP):
    src=Path(src)
    digest=hashlib.md5()
    with src.open("rb") as handle:
        for block in iter(lambda:handle.read(1024*1024),b""):
            digest.update(block)
    if digest.hexdigest()!=EXPECTED_MD5:
        raise ValueError("Raw EIA-930 archive checksum does not match verified publisher mirror")
    if start.tzinfo is None or stop.tzinfo is None or stop<=start:
        raise ValueError("UTC half-open window required")
    expected=pd.date_range(start,stop,freq="h",inclusive="left")
    all_frames=[]
    with zipfile.ZipFile(src) as z:
        if RAW_NAME not in z.namelist():
            raise ValueError("Missing historical EIA-930 BA balance file")
        usecols=[BA_COL,TIME_COL]
        for fuel in TECHS.values():
            root=f"Net Generation (MW) from {fuel}"
            usecols.extend([root,root+" (Imputed)",root+" (Adjusted)"])
        with z.open(RAW_NAME) as raw:
            for chunk in pd.read_csv(raw,usecols=usecols,chunksize=30000,
                                     low_memory=False,encoding="utf-8-sig"):
                part=chunk.loc[chunk[BA_COL].isin(BAS)].copy()
                if part.empty:continue
                # Source timestamp has no zone designator, but is explicitly labeled UTC.
                part["utc_hour_end"]=pd.to_datetime(
                    part[TIME_COL],format="%m/%d/%Y %I:%M:%S %p",
                    errors="raise",utc=True)
                part=part.loc[(part.utc_hour_end>=start)&(part.utc_hour_end<stop)]
                if part.empty:continue
                for fuel,label in TECHS.items():
                    prefix=f"Net Generation (MW) from {label}"
                    temp=part[[BA_COL,"utc_hour_end",prefix,
                               prefix+" (Imputed)",prefix+" (Adjusted)"]].copy()
                    temp.columns=["ba_code","utc_hour_end","reported_mw",
                                  "imputed_mw","adjusted_mw"]
                    temp["fuel"]=fuel
                    for col in ("reported_mw","imputed_mw","adjusted_mw"):
                        temp[col]=pd.to_numeric(temp[col],errors="coerce")
                        if np.isinf(temp[col]).any():
                            raise ValueError("Non-finite EIA-930 source values")
                    all_frames.append(temp)
    if not all_frames:
        raise ValueError("No historical EIA930 BA records in requested period")
    result=pd.concat(all_frames,ignore_index=True)
    if result.duplicated(["ba_code","fuel","utc_hour_end"]).any():
        raise ValueError("Duplicate BA/fuel/UTC hour-ending record")
    if not result.utc_hour_end.isin(expected).all():
        raise ValueError("Out-of-window source record")
    coverage=[]
    for ba in BAS:
        for fuel in TECHS:
            group=result.loc[(result.ba_code==ba)&(result.fuel==fuel)]
            unique=pd.DatetimeIndex(group.utc_hour_end)
            missing=expected.difference(unique)
            coverage.append(dict(
                ba_code=ba,fuel=fuel,expected_hour_count=len(expected),
                source_row_count=len(group),missing_source_hours=len(missing),
                missing_reported_mw=int(group.reported_mw.isna().sum()),
                missing_adjusted_mw=int(group.adjusted_mw.isna().sum()),
                negative_reported_mw=int((group.reported_mw<0).sum()),
                example_missing_utc_hours=";".join(t.isoformat() for t in missing[:5]),
            ))
    return result.sort_values(["ba_code","fuel","utc_hour_end"]),pd.DataFrame(coverage)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    data,coverage=extract(a.archive)
    a.out.mkdir(parents=True,exist_ok=True)
    data.to_csv(a.out/"paper_s_eia930_2023_07_01_to_07_07_ba_wind_solar_reported_mw.csv",index=False)
    coverage.to_csv(a.out/"paper_s_eia930_2023_07_01_to_07_07_ba_coverage.csv",index=False)
    manifest={
        "status":"EIA930_RAW_OBSERVED_BA_SOURCE_EXTRACT_ONLY",
        "source_mirror_archive":"https://zenodo.org/records/22856870",
        "source_archive_md5":EXPECTED_MD5,
        "source_balance_csv":RAW_NAME,
        "UTC_hour_end_window_half_open":[START.isoformat(),STOP.isoformat()],
        "source_column_unit":"MW",
        "fuel_labels":TECHS,
        "BAs":list(BAS),
        "source_rows":len(data),
        "missing_source_hours_total":int(coverage.missing_source_hours.sum()),
        "missing_reported_mw_total":int(coverage.missing_reported_mw.sum()),
        "reported_mw_not_mwh":True,
        "reported_imputed_adjusted_not_silently_interchanged":True,
        "BA_equals_state_assumed":False,
        "EIA_to_ReEDS_weather_cf_comparison_completed":False,
        "historical_capacity_mw_verified":False,
        "source_observation_completeness_universally_claimed":False,
    }
    (a.out/"paper_s_eia930_2023_ba_observed_source_manifest.json").write_text(
        json.dumps(manifest,indent=2)+"\n")
    print("PAPER_S_EIA930_ACTUAL_BA_SOURCE_EXTRACT_COMPLETE",json.dumps(manifest))


if __name__=="__main__":
    main()
