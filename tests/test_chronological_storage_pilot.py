import pandas as pd
import pytest
from energy_transition.chronological_storage_pilot import validate_window

def test_storage_window_requires_contiguous_true_hours():
    ts=pd.date_range("2024-01-01",periods=168,freq="h",tz="UTC")
    data=pd.DataFrame({"period":ts,"respondent":"CISO","value":100.})
    demand=validate_window(data)
    assert len(demand)==168
    assert demand.sum()==16800

def test_storage_window_rejects_missing_hour_instead_of_representative_weighting():
    ts=pd.date_range("2024-01-01",periods=168,freq="h",tz="UTC")
    ts=ts.delete(20)
    data=pd.DataFrame({"period":ts,"respondent":"CISO","value":100.})
    with pytest.raises(ValueError,match="contiguous"):
        validate_window(data)

def test_storage_window_rejects_ba_hour_duplication():
    ts=pd.date_range("2024-01-01",periods=168,freq="h",tz="UTC")
    data=pd.DataFrame({"period":ts,"respondent":"BPAT","value":100.})
    with pytest.raises(ValueError,match="Duplicate"):
        validate_window(pd.concat([data,data.iloc[[2]]]))
