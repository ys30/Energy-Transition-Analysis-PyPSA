import pandas as pd
import pytest
from energy_transition.reeds_2022_clocked_demand_branch import check_fixed_cst_native_labels,HOURS

def sample():
    return [x.isoformat(sep=" ") for x in pd.date_range("2012-01-01 00:00:00-06:00",periods=HOURS,freq="h")]

def test_exact_publisher_calendar():
    a=check_fixed_cst_native_labels(sample())
    assert a["2012_Feb29_included"] and a["2012_Dec31_removed"]

def test_missing_hour_fails():
    with pytest.raises(ValueError,match="incomplete"):
        check_fixed_cst_native_labels(sample()[:-1])

def test_duplicate_hour_fails():
    a=sample();a[-1]=a[-2]
    with pytest.raises(ValueError,match="duplicated"):
        check_fixed_cst_native_labels(a)

def test_dst_shift_fails():
    a=sample();a[2000]=a[2000].replace("-06:00","-05:00")
    with pytest.raises(ValueError,match="offset"):
        check_fixed_cst_native_labels(a)

def test_leap_index_fails():
    a=sample();a[1416]="2012-03-01 00:00:00-06:00"
    with pytest.raises(ValueError):
        check_fixed_cst_native_labels(a)
