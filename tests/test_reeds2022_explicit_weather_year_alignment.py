import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_explicit_weather_year_alignment import (
    TARGET,align_weather_year_to_reeds_2012_support
)

def test_nonleap_year_explicit_feb29_interpolation_and_dec31_discard():
    native=pd.date_range("2011-01-01","2012-01-01",freq="h",inclusive="left")
    x=np.full(len(native),.4)
    x[(native.month==2)&(native.day==28)]=.2
    x[(native.month==3)&(native.day==1)]=.6
    x[(native.month==12)&(native.day==31)]=.8
    y,m=align_weather_year_to_reeds_2012_support(native,x)
    assert len(y)==8760
    assert m["interpolated_unobserved_feb29_hours"]==24
    assert m["dropped_original_dec31_hours"]==24
    assert (y[(TARGET.month==2)&(TARGET.day==29)]==.4).all()
    assert m["calendar_imputation_is_source_observation"] is False

def test_exact_2012_native_reference_has_no_imputation():
    source=pd.date_range("2012-01-01",periods=8760,freq="h")
    x=np.linspace(0,1,8760)
    y,m=align_weather_year_to_reeds_2012_support(source,x)
    np.testing.assert_array_equal(y,x)
    assert m["interpolated_unobserved_feb29_hours"]==0
    assert m["dropped_original_dec31_hours"]==0

def test_wrong_hour_and_invalid_cf_fail_closed():
    source=pd.date_range("2011-01-01",periods=8760,freq="h")
    x=np.full(8760,.5)
    bad=source.delete(5).append(pd.DatetimeIndex([source[5]+pd.Timedelta(minutes=30)])).sort_values()
    with pytest.raises(ValueError,match="exact whole hour"):
        align_weather_year_to_reeds_2012_support(bad,x)
    x[5]=1.5
    with pytest.raises(ValueError,match="within"):
        align_weather_year_to_reeds_2012_support(source,x)
