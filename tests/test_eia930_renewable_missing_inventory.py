import pandas as pd
import pytest
from energy_transition.eia930_renewable_missing_inventory import missing_inventory

def test_missing_inventory_tracks_ba_fuel_and_shared_hour():
    x=pd.DataFrame([{"period":"2024-01-01T00:00Z","respondent":"CISO","fueltype":"SUN","value":-2.},
                    {"period":"2024-01-01T00:00Z","respondent":"CISO","fueltype":"WND","value":3.}])
    gaps,counts,overlap=missing_inventory(x)
    assert len(overlap)==8784
    assert len(gaps)==8784*4-2
    assert gaps.loc[gaps.period.eq(pd.Timestamp("2024-01-01",tz="UTC"))].shape[0]==2
    assert counts.missing_hours.sum()==len(gaps)
def test_duplicates_rejected():
    row={"period":"2024-01-01T00:00Z","respondent":"CISO","fueltype":"SUN","value":0.}
    with pytest.raises(ValueError,match="Duplicate"):
        missing_inventory(pd.DataFrame([row,row]))
