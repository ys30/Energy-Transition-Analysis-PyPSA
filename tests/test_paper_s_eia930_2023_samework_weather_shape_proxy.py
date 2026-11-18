"""Source-free admission tests for Paper S 2023 same-weather BA-proxy diagnostic."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_eia930_2023_samework_weather_shape_proxy import (
    metric,compare,source_to_utc_clock,PAIRINGS,FUELS,SCHEMES,CLOCK_SHIFTS,
    OBS_WINDOW_HOURS,EXPECTED,COMMON_START,COMMON_END,HOURS
)

def test_original_2023_july_fixed_cst_clock_contract():
    july,utc=source_to_utc_clock()
    assert july.sum()==31*24
    assert utc[0]==pd.Timestamp("2023-07-01T06:00:00Z")
    assert utc[2]==COMMON_START
    assert len(utc)==744
    assert utc.is_unique

def test_metric_preserves_negative_observed_values_and_normalizes_shape():
    x=100+40*np.sin(np.arange(OBS_WINDOW_HOURS)*np.pi/12)
    y=x/1000.
    m=metric(x,y)
    assert abs(m["pearson_r"]-1)<1e-12
    assert m["normalized_mae"]<1e-12
    x[0]=-2
    assert metric(x,y)["negative_reported_mw_hours"]==1

def test_missing_or_duplicate_BA_fuel_hour_is_rejected():
    hours=pd.date_range(COMMON_START,COMMON_END,freq="h",tz="UTC")
    obs=[]
    for ba,state in PAIRINGS:
        for fuel in FUELS:
            for i,t in enumerate(hours):
                obs.append({"ba_code":ba,"fuel":fuel,"utc_hour_end":t,
                            "reported_mw":10+2*np.sin(i/7)})
    data=pd.DataFrame(obs)
    assert len(data)==4*OBS_WINDOW_HOURS
    # Source 2023 Jul profile can be indexed by 2012 calendar month/day/hour.
    source={}
    for ba,state in PAIRINGS:
        for fuel in FUELS:
            for scheme in SCHEMES:
                source[fuel,state,scheme]=np.clip(
                    .3+.2*np.sin(np.arange(HOURS)*2*np.pi/24),0,1)
    scores,hourly=compare(data,source)
    assert len(scores)==EXPECTED==24
    assert len(hourly)==EXPECTED*OBS_WINDOW_HOURS
    assert set(scores.source_clock_shift_hours)==set(CLOCK_SHIFTS)
    assert not scores.observational_validation.any()
    with pytest.raises(ValueError,match="Missing common BA"):
        compare(data.iloc[1:],source)

def test_metric_rejects_constant_or_missing_data():
    with pytest.raises(ValueError):
        metric(np.ones(OBS_WINDOW_HOURS),np.ones(OBS_WINDOW_HOURS))
    with pytest.raises(ValueError):
        metric(np.ones(OBS_WINDOW_HOURS-1),np.ones(OBS_WINDOW_HOURS-1))
