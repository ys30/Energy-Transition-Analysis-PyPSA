"""Synthetic-only regression tests; official HDF5 MD5 tested in Actions."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_historical_weather_demand_audit import (
    validate_native_year,HOURS,WEATHER_YEARS,STATES,
)


def test_15_authentic_weather_years_and_no_missing_year_insertion():
    assert len(WEATHER_YEARS)==15
    assert WEATHER_YEARS==(2007,2008,2009,2010,2011,2012,2013,
                           2016,2017,2018,2019,2020,2021,2022,2023)
    assert len(STATES)==4


@pytest.mark.parametrize("year",[2007,2012,2016,2020,2023])
def test_native_year_clock_and_leap_cutoff(year):
    labels=pd.date_range(f"{year}-01-01",periods=HOURS,freq="h")
    got=validate_native_year(labels,year)
    assert got.equals(labels)
    assert len(got)==8760
    if year in (2008,2012,2016,2020):
        assert got[-1].month==12 and got[-1].day==30
    else:
        assert got[-1].month==12 and got[-1].day==31


def test_clock_fail_closed_missing_and_shifted_hours():
    labels=pd.date_range("2012-01-01",periods=HOURS,freq="h")
    with pytest.raises(ValueError):
        validate_native_year(labels[1:],2012)
    shifted=labels+pd.Timedelta(hours=1)
    with pytest.raises(ValueError,match="continuous"):
        validate_native_year(shifted,2012)
    with pytest.raises(ValueError,match="weather year"):
        validate_native_year(labels,2013)
