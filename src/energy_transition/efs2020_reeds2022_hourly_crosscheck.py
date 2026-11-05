"""Audit original EFS2020 vs independently published ReEDS2022 EFS_REFERENCE.

All 33 Western state-year hourly series are compared on their native source
ordinals, including shifts. Same-year totals alone cannot establish chronology.
Numerical matches are *not* independent authoritative EFS clock certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .reeds2022_reference_hdf5_provenance import CHECKSUM, STATES, YEARS, verify_publisher_2012_clock

HOURS=8760
OFFSETS=tuple(range(-12,13))

def compare_arrays(original, independent, *, abs_tolerance_mw=0.01):
    """Rolling independent values by k has EFS[h] compared to ReEDS[(h-k)%N]."""
    a=np.asarray(original,dtype=float)
    b=np.asarray(independent,dtype=float)
    if a.shape!=(HOURS,) or b.shape!=(HOURS,):
        raise ValueError("Expected 8760 values for both hourly sources")
    if not np.isfinite(a).all() or not np.isfinite(b).all() or (a<0).any() or (b<0).any():
        raise ValueError("Invalid original/published hourly MW")
    if not np.isclose(a.sum(),b.sum(),rtol=1e-9,atol=0.5):
        # Still evaluate hourly displacement; disagreement must be visible.
        annual_match=False
    else:
        annual_match=True
    comparisons=[]
    for offset in OFFSETS:
        shifted=np.roll(b,offset)
        diff=np.abs(a-shifted)
        comparisons.append({
            "offset_hours":offset,
            "mae_mw":float(diff.mean()),
            "rmse_mw":float(np.sqrt(np.mean(diff**2))),
            "maximum_absolute_error_mw":float(diff.max()),
            "all_8760_hour_values_equal_within_tolerance":bool((diff<=abs_tolerance_mw).all()),
            "matching_hours_within_tolerance":int((diff<=abs_tolerance_mw).sum()),
        })
    zero=next(v for v in comparisons if v["offset_hours"]==0)
    best=min(comparisons,key=lambda x:(x["mae_mw"],abs(x["offset_hours"]),x["offset_hours"]))
    valid=[x["offset_hours"] for x in comparisons if x["all_8760_hour_values_equal_within_tolerance"]]
    return {
        "source_2020_annual_mwh":float(a.sum()),
        "source_2022_annual_mwh":float(b.sum()),
        "annual_difference_mwh":float(a.sum()-b.sum()),
        "annual_energy_match_under_numeric_tolerance":annual_match,
        "direct_ordinal_mae_mw":zero["mae_mw"],
        "direct_ordinal_max_abs_error_mw":zero["maximum_absolute_error_mw"],
        "direct_ordinal_matching_hours":zero["matching_hours_within_tolerance"],
        "direct_ordinal_all_8760_match":zero["all_8760_hour_values_equal_within_tolerance"],
        "best_offset_hours":best["offset_hours"],
        "best_offset_mae_mw":best["mae_mw"],
        "best_offset_all_8760_match":best["all_8760_hour_values_equal_within_tolerance"],
        "all_exact_matching_offsets_in_tested_range":valid,
        "shift_uniquely_identified":len(valid)==1,
        "comparison_tolerance_mw":abs_tolerance_mw,
    }

def compare_files(efs_csv, reeds_h5):
    import h5py  # optional dependency only for the original publisher HDF5
    with reeds_h5.open("rb") as inp:
        md5=hashlib.file_digest(inp,"md5").hexdigest()
    if md5!=CHECKSUM:
        raise ValueError("ReEDS2022 publisher MD5 mismatch")
    efs=pd.read_csv(efs_csv,compression="infer")
    needed={"year","state","local_hour_id","load_mw"}
    if not needed.issubset(efs):
        raise ValueError("Missing original EFS2020 source-hour columns")
    if efs[list(needed)].isna().any().any() or efs.duplicated(["year","state","local_hour_id"]).any():
        raise ValueError("Invalid EFS source identity/hour uniqueness")
    expected_count=len(YEARS)*len(STATES)*HOURS
    if len(efs)!=expected_count or set(efs.year)!=set(YEARS) or set(efs.state)!=set(STATES):
        raise ValueError("Incomplete original EFS core-West state-year population")
    records=[]
    observed_time_keys={}
    with h5py.File(reeds_h5,"r") as h5:
        for year in YEARS:
            group=h5[str(year)]
            clock=verify_publisher_2012_clock(group["datetime"][:])
            observed_time_keys[str(year)]=clock
            for state in STATES:
                source=efs[(efs.year==year)&(efs.state==state)].sort_values("local_hour_id")
                if len(source)!=HOURS or not np.array_equal(source.local_hour_id.to_numpy(),np.arange(1,HOURS+1)):
                    raise ValueError(f"Incomplete original EFS hourly ordinals {state}/{year}")
                comparison=compare_arrays(source.load_mw.to_numpy(),group[state][:])
                records.append({"planning_year":year,"state":state,**comparison})
    results=pd.DataFrame(records).sort_values(["planning_year","state"]).reset_index(drop=True)
    if len(results)!=33 or results.duplicated(["planning_year","state"]).any():
        raise ValueError("Comparison did not cover 33 original state-year pairs")
    all_direct=bool(results.direct_ordinal_all_8760_match.all())
    all_any_shift=bool(results.best_offset_all_8760_match.all())
    meta={
        "status":"ORIGINAL_EFS2020_TO_INDEPENDENT_REEDS2022_FULL_HOURLY_COMPARISON_COMPLETED",
        "original_efs2020_input_sha256":hashlib.sha256(efs_csv.read_bytes()).hexdigest(),
        "original_reeds2022_h5_md5":md5,
        "publisher_reeds2022_md5_verified":True,
        "source_2020": "NLR EFSLoadProfile_Reference_Moderate original state-year LocalHourID CSV aggregation",
        "independent_source_2022":"ReEDS 2022 demand_EFS_REFERENCE.h5 official release",
        "state_year_pairs":33,
        "hour_pairs_per_state_year":HOURS,
        "total_direct_hour_pairs_compared":33*HOURS,
        "state_year_pairs_direct_all_hour_match":int(results.direct_ordinal_all_8760_match.sum()),
        "all_33_pairs_directly_match_under_0_01MW":all_direct,
        "all_33_pairs_have_exact_match_for_some_tested_shift":all_any_shift,
        "all_33_direct_hour_values_accepted_as_2020_EFS_UTC":False,
        "original_efs2020_source_time_convention_authoritatively_certified":False,
        "reeds2022_native_2012_CST_clock_verified":True,
        "source_2022_clock_samples":observed_time_keys,
        "real_renewable_generation_data_joined":False,
        "future_weather_year_resource_availability_join_approved":False,
        "real_western_network_OPF_admitted":False,
        "interpretation":"A full-hour numerical comparison, even if exact, proves state/year/source-ordinal numerical correspondence, not authoritative published 2020 source clock convention or identical scenario methodology."
    }
    return results,meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-hourly",required=True,type=Path)
    p.add_argument("--reeds-h5",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    result,metadata=compare_files(a.efs_hourly,a.reeds_h5)
    for output in (a.out_csv,a.out_json):output.parent.mkdir(parents=True,exist_ok=True)
    result.to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(metadata,indent=2)+"\n")
    print(json.dumps({k:v for k,v in metadata.items() if k!="source_2022_clock_samples"},indent=2))
    for x in result.itertuples(index=False):
        print(f"EFS_2020_2022_HOURLY year={x.planning_year} state={x.state} annual_diff_MWh={x.annual_difference_mwh:.6f} direct_MAE_MW={x.direct_ordinal_mae_mw:.6f} direct_equal={x.direct_ordinal_all_8760_match} best_shift_h={x.best_offset_hours} best_MAE_MW={x.best_offset_mae_mw:.6f} best_equal={x.best_offset_all_8760_match}")
if __name__=="__main__":
    main()
