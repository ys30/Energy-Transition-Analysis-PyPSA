"""Inspect exact archived 2030/2040/2050 PyPSA Load network clock semantics.

Do not infer timezone, daylight saving or simultaneity with power-supply
profiles from naive local ordinal hour snapshots.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
import pandas as pd
import numpy as np

YEARS=(2030,2040,2050)

def audit(networks):
    if set(networks)!=set(YEARS):raise ValueError("Three source years required")
    records=[]
    normalized_shapes=[]
    for year in YEARS:
        n=networks[year]
        snapshots=n.snapshots
        if len(snapshots)!=8760 or snapshots.has_duplicates:
            raise ValueError(f"{year}: 8760 unique snapshots required")
        idx=pd.DatetimeIndex(snapshots)
        if idx.isna().any() or not idx.is_monotonic_increasing:
            raise ValueError("Source snapshot timestamps invalid/nonmonotone")
        delta=idx[1:]-idx[:-1]
        is_hourly=all(x==pd.Timedelta(hours=1) for x in delta)
        if not is_hourly:raise ValueError(f"Non-hourly or discontinuous archived snapshots: {year}")
        if idx.year.nunique()!=1 or int(idx.year[0])!=year:
            raise ValueError(f"Unexpected stored source snapshot calendar year for {year}")
        dyn=n.loads_t.p_set
        if dyn.shape[0]!=8760 or len(n.loads)!=20:
            raise ValueError("Actual source Load time series incomplete")
        if not np.isfinite(dyn.to_numpy(dtype=float)).all():
            raise ValueError("Nonfinite archived EFS source Load")
        static=n.loads.index.difference(dyn.columns)
        if n.loads.loc[static,"p_set"].isna().any():
            raise ValueError("Missing static EFS p_set")
        annual=float(dyn.to_numpy(dtype=float).sum()+8760*n.loads.loc[static,"p_set"].sum())
        records.append({
            "model_year":year,
            "stored_snapshot_first":str(idx[0]),
            "stored_snapshot_last":str(idx[-1]),
            "stored_snapshot_count":len(idx),
            "stored_timestamp_timezone_name":str(idx.tz) if idx.tz is not None else None,
            "stored_snapshots_explicit_UTC_aware":bool(idx.tz is not None and str(idx.tz) in ("UTC","UTC+00:00")),
            "naive_calendar_hours_contiguous":is_hourly,
            "stored_annual_efs_load_mwh":annual,
            "source_dynamic_Load_count":len(dyn.columns),
            "source_static_only_Load_count":len(static),
            "source_calendar_semantics_independently_certified":False,
            "simultaneous_supply_profiles_aligned":False,
        })
        normalized_shapes.append([(int(x.month),int(x.day),int(x.hour)) for x in idx])
    same_calendar=normalized_shapes[0]==normalized_shapes[1]==normalized_shapes[2]
    # Do NOT state this proves a real same-UTC electricity chronology.
    return {
        "archive_year_count":len(records),
        "archive_years":records,
        "all_three_years_have_same_naive_month_day_hour_order":same_calendar,
        "archived_model_snapshots_timezone_aware_UTC":all(x["stored_snapshots_explicit_UTC_aware"] for x in records),
        "independent_source_EFS_clock_DST_convention_verified":False,
        "weather_and_generator_hourly_profiles_verified":False,
        "joint_synchronous_2030_2050_OPF_admitted":False,
        "note":"Stored model calendar continuity is not independent proof of EFS local-hour convention or synchronized generator/weather UTC chronology."
    }

def main():
    import pypsa
    p=argparse.ArgumentParser()
    for year in YEARS:p.add_argument(f"--net{year}",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    nets={year:pypsa.Network(str(getattr(a,f"net{year}"))) for year in YEARS}
    report=audit(nets)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
