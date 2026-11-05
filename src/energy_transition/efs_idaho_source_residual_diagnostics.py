"""Source-hour residual diagnostics, per-month and per-clock-hour, for Idaho.

Compare original EFS2020 state-hour ordinals against separately authenticated
ReEDS2022 HDF5 2012 CST clock, using nonwrapping source index shifts.
The 2012 source index is a *ReEDS2022 reference*, NOT an authenticated EFS
publisher timestamp. Seasonal bins are reference HDF5 calendar positions only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from .reeds2022_reference_hdf5_provenance import CHECKSUM, YEARS, verify_publisher_2012_clock

STATES=("ID","AZ","CA")
SHIFTS={"ID":-2,"AZ":-2,"CA":-3}
N=8760

def profile_metrics(original,reference,state,year,reference_datetime):
    if state not in SHIFTS: raise ValueError("Unsupported comparison state")
    a=np.asarray(original,dtype=float)
    b=np.asarray(reference,dtype=float)
    if a.shape!=(N,) or b.shape!=(N,):raise ValueError("Incomplete source hours")
    if not (np.isfinite(a).all() and np.isfinite(b).all()) or (a<0).any() or (b<0).any():
        raise ValueError("Invalid MW")
    shift=SHIFTS[state]
    i=np.arange(max(0,shift),min(N,N+shift))
    j=i-shift
    assert len(i)==N-abs(shift)
    source_time=pd.DatetimeIndex(pd.to_datetime(reference_datetime,utc=True))
    if len(source_time)!=N:raise ValueError("Missing published HDF5 chronology")
    residual=a[i]-b[j]
    abs_error=np.abs(residual)
    # Inherently descriptive: the published 2022 *reference* hour labels
    # are attached to b[j], NOT claimed to be 2020 EFS physical time.
    aligned_hour=source_time[j].tz_convert("Etc/GMT+6")
    frame=pd.DataFrame({
        "year":year,"state":state,"source_efs_ordinal":i+1,
        "published_reeds_2012_month":aligned_hour.month,
        "published_reeds_2012_hour":aligned_hour.hour,
        "residual_efs_minus_reeds_mw":residual,
        "absolute_error_mw":abs_error,
    })
    groups=[]
    for group_type,key in [("month","published_reeds_2012_month"),("hour","published_reeds_2012_hour")]:
        for value,g in frame.groupby(key):
            error=g.absolute_error_mw.to_numpy()
            groups.append({
                "year":int(year),"state":state,"group_type":group_type,
                "reference_index_label":int(value),"compared_hours":len(g),
                "mean_absolute_error_mw":float(error.mean()),
                "median_absolute_error_mw":float(np.median(error)),
                "p95_absolute_error_mw":float(np.quantile(error,.95)),
                "maximum_absolute_error_mw":float(error.max()),
                "hours_above_1mw":int((error>1).sum()),
                "signed_mean_residual_mw":float(g.residual_efs_minus_reeds_mw.mean()),
            })
    lag=np.abs(residual)>1.
    # Runs of residual >1 MW in chronological SOURCE ordinal order.
    segments=np.diff(np.r_[False,lag,False].astype(int))
    begin=np.where(segments==1)[0]
    end=np.where(segments==-1)[0]
    if len(begin)!=len(end):raise ValueError("Bad run-length accounting")
    overview={
        "year":int(year),"state":state,"source_2022_shift_applied_hours":shift,
        "compared_hours":int(len(i)),
        "source_year_MWh_difference_before_boundary_exclusion":float(a.sum()-b.sum()),
        "mae_mw":float(abs_error.mean()),
        "p95_abs_mw":float(np.quantile(abs_error,.95)),
        "hours_above_1mw":int(lag.sum()),
        "fraction_above_1mw":float(lag.mean()),
        "largest_consecutive_run_above_1mw_hours":int(max(end-begin,default=0)),
        "number_of_runs_above_1mw":int(len(begin)),
        "largest_24hour_mean_abs_error_mw":float(pd.Series(abs_error).rolling(24).mean().max()),
        "max_reference_month_mae_mw":float(max(g["mean_absolute_error_mw"] for g in groups if g["group_type"]=="month")),
        "min_reference_month_mae_mw":float(min(g["mean_absolute_error_mw"] for g in groups if g["group_type"]=="month")),
        "is_publisher_certified_original_EFS_local_clock":False,
    }
    return overview,groups

def inspect(efs_csv,hdf5):
    import h5py
    with hdf5.open("rb") as file:
        md5=hashlib.file_digest(file,"md5").hexdigest()
    if md5!=CHECKSUM:raise ValueError("Publisher HDF5 MD5 mismatch")
    source=pd.read_csv(efs_csv,compression="infer")
    keys={"year","state","local_hour_id","load_mw"}
    if not keys.issubset(source):raise ValueError("Invalid archived EFS columns")
    if source[list(keys)].isna().any().any() or source.duplicated(["year","state","local_hour_id"]).any():
        raise ValueError("Duplicate or empty archived EFS keys")
    overview=[];seasons=[]
    with h5py.File(hdf5,"r") as f:
        for year in YEARS:
            g=f[str(year)]
            verify_publisher_2012_clock(g["datetime"][:])
            for state in STATES:
                a=source[(source.year==year)&(source.state==state)].sort_values("local_hour_id")
                if not np.array_equal(a.local_hour_id.to_numpy(),np.arange(1,N+1)):
                    raise ValueError("Missing 2020 EFS source hour keys")
                result,grouped=profile_metrics(a.load_mw,g[state][:],state,year,g["datetime"][:])
                overview.append(result);seasons.extend(grouped)
    if len(overview)!=9 or len(seasons)!=9*(12+24):
        raise ValueError("Incorrect source/group coverage")
    meta={
        "status":"SOURCE_MISMATCH_RESIDUAL_DIAGNOSTIC_COMPLETED",
        "original_efs_input_sha256":hashlib.sha256(efs_csv.read_bytes()).hexdigest(),
        "publisher_reeds2022_md5":md5,
        "source_pairs":9,"states":list(STATES),"years":list(YEARS),
        "excluded_crossyear_wrapped_hours":True,
        "original_EFS2020_physical_clock_verified":False,
        "Idaho_timezone_weight_identified":False,
        "resource_join_or_real_OPF_admitted":False,
        "caution":"Month/hour grouping uses published 2022 HDF5 2012 CST source labels; original 2020 EFS time metadata is not certified."
    }
    return pd.DataFrame(overview),pd.DataFrame(seasons),meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-hourly",required=True,type=Path)
    p.add_argument("--reeds-h5",required=True,type=Path)
    p.add_argument("--out-dir",required=True,type=Path)
    args=p.parse_args()
    ov,groups,meta=inspect(args.efs_hourly,args.reeds_h5)
    args.out_dir.mkdir(parents=True,exist_ok=True)
    ov.to_csv(args.out_dir/"source_state_year_residual_overview.csv",index=False)
    groups.to_csv(args.out_dir/"source_month_hour_residual_groups.csv",index=False)
    (args.out_dir/"source_residual_diagnostic_provenance.json").write_text(json.dumps(meta,indent=2)+"\n")
    for row in ov.itertuples(index=False):
        print(f"SOURCE_RESIDUAL year={row.year} state={row.state} shift={row.source_2022_shift_applied_hours} "
              f"mae_MW={row.mae_mw:.5f} above1={row.hours_above_1mw} longest_run={row.largest_consecutive_run_above_1mw_hours} "
              f"monthly_MAE_min={row.min_reference_month_mae_mw:.5f} monthly_MAE_max={row.max_reference_month_mae_mw:.5f}")
    for row in groups[groups.state=="ID"].itertuples(index=False):
        print(f"ID_RESIDUAL_GROUP year={row.year} type={row.group_type} group={row.reference_index_label} "
              f"mae_MW={row.mean_absolute_error_mw:.5f} above1={row.hours_above_1mw}")
if __name__=="__main__":main()
