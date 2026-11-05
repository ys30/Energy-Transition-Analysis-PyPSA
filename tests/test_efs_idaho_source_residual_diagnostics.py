import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_idaho_source_residual_diagnostics import profile_metrics

def source_clock():
    ts=pd.date_range("2012-01-01 00:00:00-06:00","2012-12-31 00:00:00-06:00",freq="h",inclusive="left")
    assert len(ts)==8760
    return [x.isoformat(sep=" ") for x in ts]

def series():
    h=np.arange(8760)
    return 500+100*np.sin(2*np.pi*h/24)+.02*h

def test_nonwrap_year_full_group_coverage():
    b=series();a=np.roll(b,-2)
    overview,groups=profile_metrics(a,b,"ID",2030,source_clock())
    assert overview["compared_hours"]==8758
    assert overview["mae_mw"]==pytest.approx(0)
    assert overview["hours_above_1mw"]==0
    assert len(groups)==36
    assert not overview["is_publisher_certified_original_EFS_local_clock"]

def test_monthly_residual_localized_and_contiguous_runs():
    b=series();a=np.roll(b,-2);a[100:150]+=10
    overview,groups=profile_metrics(a,b,"ID",2030,source_clock())
    assert overview["largest_consecutive_run_above_1mw_hours"]==50
    assert overview["number_of_runs_above_1mw"]==1
    assert overview["hours_above_1mw"]==50
    january=next(x for x in groups if x["group_type"]=="month" and x["reference_index_label"]==1)
    assert january["hours_above_1mw"]==50

def test_wrong_array_length_and_nan_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        profile_metrics(series()[:-1],series(),"ID",2030,source_clock())
    x=series();x[42]=float("nan")
    with pytest.raises(ValueError,match="Invalid"):
        profile_metrics(x,series(),"ID",2030,source_clock())

def test_only_explicit_control_states():
    with pytest.raises(ValueError,match="Unsupported"):
        profile_metrics(series(),series(),"WA",2030,source_clock())

def test_official_hdf5_bytestring_timestamp_supported():
    b=series()
    clock=[s.encode("utf-8") for s in source_clock()]
    result,_=profile_metrics(np.roll(b,-2),b,"ID",2030,clock)
    assert result["mae_mw"]==pytest.approx(0)
