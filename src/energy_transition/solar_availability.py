"""Illustrative solar daylight envelope for representative UTC month-hour snapshots.

This is a physically motivated ASSUMPTION (not measured solar irradiance).
Sunlight is zero at local night; normalized mean availability is approximately
0.26 with an explicit cap at 1. CAISO and BPAT use Pacific time here.
"""
import numpy as np
import pandas as pd

def solar_daylight_profile(snapshots, timezone="America/Los_Angeles", annual_mean=0.26):
    if not 0 < annual_mean < 0.5:
        raise ValueError("Annual mean must be within (0, 0.5) for this daylight model")
    stamps=pd.DatetimeIndex(snapshots)
    if stamps.tz is None:
        stamps=stamps.tz_localize("UTC")
    local=stamps.tz_convert(timezone)
    hour=local.hour.to_numpy()+local.minute.to_numpy()/60
    # Solar envelope: sunrise approximately 06:00, sunset approximately 18:00
    # local clock. Latitude, season, weather, and DST offsets are NOT calibrated.
    daylight=np.maximum(0.0,np.sin(np.pi*(hour-6.0)/12.0))
    daylight[(hour<6)|(hour>=18)]=0.0
    if not daylight.any():raise ValueError("No daylight hours in snapshots")
    # Normalize on unweighted representative snapshots. In the current 12*24
    # representation every month has 24 hourly samples.
    profile=np.clip(daylight*(annual_mean/daylight.mean()),0,1)
    if (profile[(hour<6)|(hour>=18)]!=0).any():
        raise AssertionError("Nighttime PV generation availability must be zero")
    return pd.Series(profile,index=pd.DatetimeIndex(snapshots),name="solar_p_max_pu")
