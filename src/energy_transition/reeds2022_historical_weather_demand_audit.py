"""Publisher-verified ReEDS historical-demand vs fixed 2030-demand audit.

This module does NOT infer 2030 climate-conditioned demand, join instantaneous
wind/PV as measured hour-ending energy, or solve an LP. Historical ReEDS state
gross end-use demand is independently published for 15 original weather years.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import h5py
import numpy as np
import pandas as pd
from energy_transition.reeds_2022_clocked_demand_branch import (
    verify_official_file,check_fixed_cst_native_labels,
)
from energy_transition.reeds2022_all_weather_year_720lp import (
    WEATHER_YEARS,STATES,HOURS,
)

HIST_MD5="06ca6b65088a870afafc25191dcfd6f3"
HIST_DOI="https://doi.org/10.5281/zenodo.18462671"
HIST_NAME="demand_historic.h5"
HIST_KEYS=("index_0","columns","data")
REF_YEAR=2012


def verify_historical_md5(path):
    sha=hashlib.md5()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            sha.update(chunk)
    got=sha.hexdigest()
    if got!=HIST_MD5:
        raise ValueError(f"Official historical demand MD5 mismatch: {got}")
    return got


def decode_values(values):
    return [v.decode("utf-8") if isinstance(v,bytes) else str(v) for v in values]


def validate_native_year(index,year):
    """The source's original 8760 hourly timestamps are not silently remapped."""
    t=pd.DatetimeIndex(pd.to_datetime(decode_values(index),errors="raise"))
    if t.tz is not None:raise ValueError("Historical source index must be naive fixed CST")
    if len(t)!=HOURS or t.has_duplicates or t.isna().any():
        raise ValueError("Historical year must have 8760 unique native labels")
    if not (t.year==year).all() or not (t.minute==0).all() or not (t.second==0).all():
        raise ValueError("Historical weather year or hourly clock mismatch")
    expected=pd.date_range(f"{year}-01-01",periods=HOURS,freq="h")
    if not t.equals(expected):
        raise ValueError("Historical source year is not continuous original 8760 CST hours")
    return t


def audit(historic,projection):
    """Verify exact source index, then report historical load level/shape, no LP."""
    rows=[]
    year_counts={}
    ref_load={}
    with h5py.File(historic,"r") as f:
        if not all(k in f for k in HIST_KEYS):
            raise ValueError("Historical HDF5 schema is not data/columns/index_0")
        state_cols=decode_values(f["columns"][:])
        if len(state_cols)!=len(set(state_cols)) or any(st not in state_cols for st in STATES):
            raise ValueError("Missing/duplicate official historical state columns")
        table=f["data"]
        native=pd.DatetimeIndex(pd.to_datetime(decode_values(f["index_0"][:]),errors="raise"))
        if table.ndim!=2 or table.shape!=(len(WEATHER_YEARS)*HOURS,len(state_cols)):
            raise ValueError("Unexpected historical demand dimensions")
        if len(native)!=len(WEATHER_YEARS)*HOURS or native.has_duplicates:
            raise ValueError("Historical demand labels invalid")
        for i,year in enumerate(WEATHER_YEARS):
            lo=i*HOURS
            hi=lo+HOURS
            clock=validate_native_year(native[lo:hi],year)
            year_counts[str(year)]=len(clock)
            indices=[state_cols.index(st) for st in STATES]
            panel=np.asarray(table[lo:hi,indices],dtype=float)
            if panel.shape!=(HOURS,len(STATES)) or not np.isfinite(panel).all() or (panel<0).any():
                raise ValueError(f"Invalid historical state demand: {year}")
            for j,state in enumerate(STATES):
                load=panel[:,j]
                if load.max()<=0:raise ValueError("Non-positive state demand peak")
                rows.append({"weather_year":year,"state":state,"demand_series":"historical",
                    "hour_count":HOURS,"annual_mwh":float(load.sum()),
                    "peak_mw":float(load.max()),"mean_mw":float(load.mean()),
                    "minimum_mw":float(load.min()),
                    "daily_cycle_amplitude_mw":float(np.ptp(load.reshape(-1,24).mean(axis=0)))})
                if year==REF_YEAR: ref_load[state]=(clock,load.copy())
    reference={}
    with h5py.File(projection,"r") as f:
        if "2030" not in f:raise ValueError("Projected source lacks 2030")
        group=f["2030"]
        check_fixed_cst_native_labels(group["datetime"][:])
        utc=pd.DatetimeIndex(pd.to_datetime(decode_values(group["datetime"][:]),utc=True))
        local=utc.tz_convert("Etc/GMT+6").tz_localize(None)
        for state in STATES:
            curve=np.asarray(group[state][:],dtype=float)
            if curve.shape!=(HOURS,) or not np.isfinite(curve).all() or (curve<0).any():
                raise ValueError("Invalid official 2030 projected demand")
            historical_clock,hist=ref_load[state]
            if not historical_clock.equals(local):
                raise ValueError("Historical 2012 CST and 2030 model reference clock differ")
            if np.std(hist)<=0 or np.std(curve)<=0:
                raise ValueError("Cannot correlate constant demand curve")
            reference[state]={
                "state":state,"weather_year":2012,"projection_model_year":2030,
                "historical_2012_mwh":float(hist.sum()),
                "projected_2030_mwh":float(curve.sum()),
                "historical_2012_peak_mw":float(hist.max()),
                "projected_2030_peak_mw":float(curve.max()),
                "projected_to_historical_energy_ratio":float(curve.sum()/hist.sum()),
                "projected_to_historical_peak_ratio":float(curve.max()/hist.max()),
                "hourly_pearson_r":float(np.corrcoef(hist,curve)[0,1]),
                "same_clock_not_same_weather_model":True,
            }
    df=pd.DataFrame(rows)
    if len(df)!=60 or set(df.weather_year)!=set(WEATHER_YEARS):
        raise ValueError("Expected all 15 years x four states")
    return df,pd.DataFrame(reference.values()),{
        "audit_status":"PUBLISHER_MD5_AND_HISTORICAL_DEMAND_SOURCE_CLOCK_VERIFIED",
        "history_source":HIST_DOI,
        "historic_md5":HIST_MD5,
        "historical_source_year_hours":year_counts,
        "reference_2030_weather_year":2012,
        "historic_demand_is_2030_projection":False,
        "original_reeds_2022_2030_model_has_15_weather_years":False,
        "frozen_720_LP_not_modified":True,
        "historical_weather_matched_generation_LP_performed":False,
        "2030_cross_release_load_compatibility_established":False,
    }


def run(historic,projection,out):
    verify_historical_md5(historic)
    verify_official_file(Path(projection))
    df,compare,manifest=audit(historic,projection)
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    df.to_csv(out/"paper_s_historical_load_15year_60_state_years.csv",index=False)
    compare.to_csv(out/"paper_s_historical_2012_vs_projected_2030_demand.csv",index=False)
    (out/"paper_s_historical_load_source_manifest.json").write_text(
        json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("PAPER_S_PUBLISHER_HISTORICAL_LOAD_15_YEAR_AUDIT_PASS")
    print(compare.to_string(index=False))
    return df,compare,manifest


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--historical-h5",type=Path,required=True)
    p.add_argument("--projected-h5",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    run(a.historical_h5,a.projected_h5,a.out)


if __name__=="__main__":
    main()
