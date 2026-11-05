import pandas as pd
import pytest
from energy_transition.reeds2022_reference_hdf5_provenance import verify_publisher_2012_clock

def original():
    return pd.date_range(
      "2012-01-01 00:00:00-06:00","2012-12-31 00:00:00-06:00",
      freq="h",inclusive="left").strftime("%Y-%m-%d %H:%M:%S%z").tolist()

def data():
    a=pd.date_range(
      "2012-01-01 00:00:00-06:00","2012-12-31 00:00:00-06:00",
      freq="h",inclusive="left")
    return [v.isoformat(sep=" ") for v in a]

def test_full_2012_leap_day_and_dec31_omission():
    d=verify_publisher_2012_clock(data())
    assert d["Feb_29_2012_included"]
    assert d["Dec_31_2012_omitted"]
    assert d["native_datetime_first"].startswith("2012-01-01 00:00:00")
    assert d["native_datetime_last"].startswith("2012-12-30 23:00:00")

def test_wrong_dst_offset_refused():
    d=data()
    d[100]="2012-01-05 04:00:00-07:00"
    with pytest.raises(ValueError,match="UTC-06 offset"):
        verify_publisher_2012_clock(d)

def test_missing_hour_refused():
    with pytest.raises(ValueError,match="length"):
        verify_publisher_2012_clock(data()[:-1])

def test_shifted_hour_refused_even_if_8760():
    d=data()
    d[200]="2012-01-09 09:00:00-06:00"
    with pytest.raises(ValueError,match="chronology mismatch"):
        verify_publisher_2012_clock(d)
