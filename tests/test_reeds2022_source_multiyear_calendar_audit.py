import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_source_multiyear_calendar_audit import (
    calendar_audit,compare_indexes
)

YEARS=tuple(list(range(2007,2014))+list(range(2016,2024)))

def synthetic_original_index():
    pieces=[]
    for year in YEARS:
        idx=pd.date_range(f"{year}-01-01",f"{year+1}-01-01",
            freq="h",inclusive="left")
        if len(idx)==8784:idx=idx[:-24]
        assert len(idx)==8760
        pieces.extend(idx.strftime("%Y-%m-%d %H:%M:%S").tolist())
    return np.asarray(pieces,dtype="S19")

def test_15_year_source_calendar_and_2012_boundary():
    raw=synthetic_original_index()
    w,p=compare_indexes(raw,raw)
    assert len(w)==15 and len(p)==15
    assert 2014 not in set(w.weather_year)
    assert 2023 in set(w.weather_year)
    leap=w[w.weather_year.eq(2012)].iloc[0]
    assert leap.missing_dec31_source_hours==24
    assert leap.missing_feb29_source_hours==0
    assert not bool(leap.is_exact_conventional_calendar)
    assert bool(w[w.weather_year.eq(2013)].iloc[0].is_exact_conventional_calendar)

def test_wind_pv_source_clock_mismatch_fails():
    a=synthetic_original_index()
    b=a.copy()
    b[6*8760-1]=b"2012-12-31 00:00:00"
    with pytest.raises(ValueError,match="Non-hourly gap|clocks disagree"):
        compare_indexes(a,b)

def test_duplicate_source_instants_rejected():
    a=synthetic_original_index()
    a[1]=a[0]
    with pytest.raises(ValueError,match="Duplicate"):
        calendar_audit(a,"wind")

def test_absent_reference_year_fails():
    a=synthetic_original_index()
    subset=a[~pd.DatetimeIndex(pd.to_datetime(a.astype(str))).year.isin([2012])]
    with pytest.raises(ValueError,match="Missing mandatory frozen 2012"):
        calendar_audit(subset,"wind")
