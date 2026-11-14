"""Explicit month-day-hour map of native ReEDS source years to 2012 8760 support.

For NON-leap years: missing February 29 is *imputed*, per original source
same-hour February 28 and March 1 simple average; December 31 source
hours are intentionally excluded from the target. For leap weather years,
source itself may lack Dec31, yielding an exact observed MM-DD-HH map.
This is a numerical synthetic cross-weather-year demand alignment, NOT
observed Feb29 wind/PV, certified past-hour energy, nor a 2030 forecast.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

TARGET=pd.date_range("2012-01-01",periods=8760,freq="h")
TARGET_KEYS=tuple((t.month,t.day,t.hour) for t in TARGET)

def align_weather_year_to_reeds_2012_support(native_index,source_cf):
    t=pd.DatetimeIndex(pd.to_datetime(native_index,errors="raise"))
    v=np.asarray(source_cf,dtype=float)
    if v.ndim!=1 or len(v)!=len(t) or len(v)!=8760:
        raise ValueError("One 8760-reference source year required")
    if t.has_duplicates or t.isna().any() or len(set(t.year))!=1:
        raise ValueError("Native year clock must be unique and single-year")
    if not np.isfinite(v).all() or (v<0).any() or (v>1+1e-8).any():
        raise ValueError("Source weather CF must be finite and within [0,1]")
    if np.any(t.minute != 0) or np.any(t.second != 0) or np.any(t.microsecond != 0):
        raise ValueError("Native source timestamp is not on the exact whole hour")
    keys=[(x.month,x.day,x.hour) for x in t]
    if len(set(keys))!=8760:raise ValueError("Duplicated source month-day-hour")
    seen=dict(zip(keys,v))
    year=int(t.year[0])
    out=np.empty(8760,dtype=float)
    missing=[]
    for i,key in enumerate(TARGET_KEYS):
        if key in seen:out[i]=seen[key]
        elif key[0:2]==(2,29):
            before=(2,28,key[2])
            after=(3,1,key[2])
            if before not in seen or after not in seen:
                raise ValueError("Cannot interpolate absent leap day without adjacent authentic samples")
            out[i]=.5*(seen[before]+seen[after])
            missing.append(key)
        else:
            raise ValueError(f"Unsupported missing calendar key {key}")
    excluded=set(seen)-set(TARGET_KEYS)
    if excluded and excluded!={(12,31,h) for h in range(24)}:
        raise ValueError("Unexpected source-only calendar dates besides December 31")
    if len(missing) not in (0,24) or len(excluded) not in (0,24):
        raise ValueError("Unaccounted source calendar records")
    if not np.isfinite(out).all() or (out<-1e-8).any() or (out>1+1e-8).any():
        raise ValueError("Aligned source CF outside physical envelope")
    inserted_cf_sum=float(sum(out[i] for i,key in enumerate(TARGET_KEYS) if key in missing))
    excluded_cf_sum=float(sum(seen[key] for key in excluded))
    calendar_change=float(out.sum()-v.sum())
    if not np.isclose(calendar_change,inserted_cf_sum-excluded_cf_sum,rtol=0,atol=1e-7):
        raise ValueError("Source calendar CF energy-proxy substitution balance failed")
    info={
       "native_cf_hour_sum":float(v.sum()),
       "aligned_cf_hour_sum":float(out.sum()),
       "synthetic_feb29_cf_hour_sum":inserted_cf_sum,
       "excluded_dec31_cf_hour_sum":excluded_cf_sum,
       "calendar_substitution_cf_hour_sum_delta":calendar_change,
       "calendar_substitution_relative_to_native_CF_sum":(
           calendar_change/float(v.sum()) if v.sum()>0 else None),
       "native_weather_year":year,"target_reference_calendar":2012,
       "original_native_source_hours":len(t),"target_hours":len(TARGET),
       "interpolated_unobserved_feb29_hours":len(missing),
       "dropped_original_dec31_hours":len(excluded),
       "interpolation":"same_local_clock_hour_arithmetic_mean_Feb28_Mar1" if missing else "none",
       "hour_integrated_generation_certified":False,
       "calendar_imputation_is_source_observation":False,
       "2030_weather_and_demand_contemporaneous":False,
       "original_source_index_hourly_integration_verified":False}
    return out,info
