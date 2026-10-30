import pandas as pd
import pytest
from energy_transition.eia930_full_hour_pilot import validate_hourly_demand


def test_full_year_demand_is_accepted_without_hour_reconstruction():
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    source=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    demand=validate_hourly_demand(source,2024,["CISO"])
    assert demand.shape==(8784,1)
    assert demand.iloc[0,0]==100.0


def test_full_year_demand_rejects_missing_hour_and_unexpected_ba():
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    source=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    with pytest.raises(ValueError,match="Full chronological year"):
        validate_hourly_demand(source.iloc[:-1],2024,["CISO"])
    source.loc[0,"respondent"]="BPAT"
    with pytest.raises(ValueError,match="unexpected BA"):
        validate_hourly_demand(source,2024,["CISO"])


def test_full_year_demand_rejects_invalid_value():
    hours=pd.date_range("2024-01-01","2025-01-01",freq="h",inclusive="left",tz="UTC")
    source=pd.DataFrame({"respondent":"CISO","period":hours,"value":100.0})
    source.loc[0,"value"]=float("inf")
    with pytest.raises(ValueError,match="finite and positive"):
        validate_hourly_demand(source,2024,["CISO"])
