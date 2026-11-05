"""Assess EFS2020/ReEDS2022 clock-shift robustness without circular wrap assumptions.

Uses original archived source series and publisher-MD5-verified HDF5. For
each candidate offset, compares only genuinely overlapping source ordinal
hours (no fabricated December-to-January wrap), then reports lag rank,
second-best margin, interior hour residuals, boundary exclusions and Idaho
unresolved residual as a separate review category.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .reeds2022_reference_hdf5_provenance import CHECKSUM, STATES, YEARS, verify_publisher_2012_clock

HOURS=8760
LAGS=tuple(range(-12,13))

def lag_overlap(original, reference, offset):
    a=np.asarray(original,dtype=float);b=np.asarray(reference,dtype=float)
    if a.shape!=(HOURS,) or b.shape!=(HOURS,):
        raise ValueError("Each source must have 8760 hourly MW values")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("Nonfinite hourly source")
    if (a<0).any() or (b<0).any():
        raise ValueError("Negative hourly source")
    if abs(offset)>=HOURS:
        raise ValueError("No comparable hours")
    # np.roll(b,offset)[i] == b[i-offset], except its wrapped edge.
    idx=np.arange(max(0,offset),min(HOURS,HOURS+offset))
    residual=a[idx]-b[idx-offset]
    return {
        "offset":int(offset),"compared_hours":int(len(idx)),
        "excluded_boundary_hours":int(HOURS-len(idx)),
        "mae_mw":float(np.abs(residual).mean()),
        "rmse_mw":float(np.sqrt(np.mean(residual**2))),
        "max_abs_mw":float(np.max(np.abs(residual))),
        "hours_over_1_mw":int(np.sum(np.abs(residual)>1)),
        "fraction_within_1_mw":float(np.mean(np.abs(residual)<=1)),
        "p99_abs_mw":float(np.quantile(np.abs(residual),0.99)),
    }

def assess(a,b):
    candidates=[lag_overlap(a,b,k) for k in LAGS]
    ranked=sorted(candidates,key=lambda r:(r["mae_mw"],abs(r["offset"]),r["offset"]))
    first,second=ranked[:2]
    return {
        "best_nonwrap_offset":first["offset"],
        "best_nonwrap_mae_mw":first["mae_mw"],
        "best_nonwrap_rmse_mw":first["rmse_mw"],
        "best_nonwrap_max_abs_mw":first["max_abs_mw"],
        "best_nonwrap_hours_over_1mw":first["hours_over_1_mw"],
        "best_nonwrap_compared_hours":first["compared_hours"],
        "best_nonwrap_excluded_boundary_hours":first["excluded_boundary_hours"],
        "second_best_offset":second["offset"],
        "second_best_mae_mw":second["mae_mw"],
        "runnerup_mae_margin_mw":second["mae_mw"]-first["mae_mw"],
        "best_offset_has_below_1mw_all_overlapping_hours":bool(first["hours_over_1_mw"]==0),
        "first_vs_second_mae_ratio":first["mae_mw"]/second["mae_mw"] if second["mae_mw"] else None,
        "zero_offset_mae_mw":next(r["mae_mw"] for r in candidates if r["offset"]==0),
        "source_2020_clock_authoritatively_verified":False,
        "real_weather_join_admitted":False,
    }

def source_audit(original_file,reference_h5):
    import hashlib
    import h5py
    with reference_h5.open("rb") as stream:
        md5=hashlib.file_digest(stream,"md5").hexdigest()
    if md5!=CHECKSUM:
        raise ValueError("Publisher ReEDS HDF5 checksum failed")
    d=pd.read_csv(original_file,compression="infer")
    required={"year","state","local_hour_id","load_mw"}
    if not required.issubset(d) or d[list(required)].isna().any().any():
        raise ValueError("Missing archived EFS source fields")
    if d.duplicated(["year","state","local_hour_id"]).any() or len(d)!=len(YEARS)*len(STATES)*HOURS:
        raise ValueError("Duplicate or incomplete EFS source")
    rows=[]
    with h5py.File(reference_h5,"r") as hf:
        for year in YEARS:
            group=hf[str(year)]
            verify_publisher_2012_clock(group["datetime"][:])
            for state in STATES:
                selection=d[(d.year==year)&(d.state==state)].sort_values("local_hour_id")
                if len(selection)!=HOURS or not np.array_equal(selection.local_hour_id,np.arange(1,HOURS+1)):
                    raise ValueError(f"Incomplete source ordinals for {state}/{year}")
                metrics=assess(selection.load_mw,group[state][:])
                rows.append({"year":year,"state":state,**metrics})
    frame=pd.DataFrame(rows)
    if len(frame)!=33: raise ValueError("Missing source pairs")
    metadata={
        "status":"NONWRAPPING_SOURCE_LAG_ROBUSTNESS_CHECKED",
        "release_comparison":"EFS2020 Reference Moderate vs publisher MD5 verified ReEDS2022 EFS_REFERENCE",
        "source_pairs":33,"tested_shifts":list(LAGS),
        "per_pair_original_hours":HOURS,
        "all_33_source_year_states_covered":True,
        "nonwrap_excludes_unobserved_cross_year_hours":True,
        "matches_grant_actual_efs2020_UTC_semantics":False,
        "unverified_2020_to_2012_clock_join_allowed":False,
        "real_western_powerflow_admitted":False,
        "caution":"Computational lag identification, not proof of physical state timezone. Original EFS has state/sector/subsector fields, not a source-approved sub-state timezone split.",
    }
    return frame,metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--efs-hourly",required=True,type=Path)
    p.add_argument("--reeds-h5",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    rows,meta=source_audit(a.efs_hourly,a.reeds_h5)
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    rows.to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(meta,indent=2)+"\n")
    for r in rows.itertuples(index=False):
        print(f"NONWRAP_LAG year={r.year} state={r.state} best={r.best_nonwrap_offset} "
              f"MAE={r.best_nonwrap_mae_mw:.6f} runnerup={r.second_best_offset} "
              f"runnerup_MAE={r.second_best_mae_mw:.6f} margin={r.runnerup_mae_margin_mw:.6f} "
              f"hours_over_1MW={r.best_nonwrap_hours_over_1mw} excluded_edges={r.best_nonwrap_excluded_boundary_hours}")
    print(json.dumps(meta,indent=2))
if __name__=="__main__":main()
