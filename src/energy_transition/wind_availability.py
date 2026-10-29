"""Documented illustrative wind variability for representative month-hour models.

Not observed wind speed or EIA reported wind availability. This is a
sensitivity envelope with seasonal and UTC-hour variability, intended only
to expose dependence on the flat 0.35 wind assumption. Weighted annual mean
is normalized to 0.35 under month-day snapshot weights.
"""
import numpy as np
import pandas as pd

def wind_sensitivity_profile(snapshots, weights, annual_mean=0.35):
    stamps=pd.DatetimeIndex(snapshots)
    w=np.asarray(weights,dtype=float)
    if len(stamps)!=len(w) or np.any(w<=0):
        raise ValueError("Wind profile snapshots and positive weights must align")
    if not 0<annual_mean<1:
        raise ValueError("Wind mean must lie between zero and one")
    # Illustrative winter-high and intra-day shape (NOT meteorological data).
    month=stamps.month.to_numpy(dtype=float)
    hour=stamps.hour.to_numpy(dtype=float)
    raw=(1+0.25*np.cos(2*np.pi*(month-1)/12))*(1+0.2*np.cos(2*np.pi*(hour-3)/24))
    profile=raw*annual_mean/np.average(raw,weights=w)
    if np.any(profile>1) or np.any(profile<0):
        raise ValueError("Assumed wind availability escaped [0, 1]")
    return pd.Series(profile,index=stamps,name="assumed_wind_p_max_pu")
