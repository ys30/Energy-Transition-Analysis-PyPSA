import pandas as pd
import pytest
from energy_transition.eia930_hourly_renewables import audit

def test_hourly_wind_solar_audit_retains_missing_and_negative_values():
    frame=pd.DataFrame([
      {"period":"2024-01-01T00:00Z","respondent":"CISO","fueltype":"SUN","value":0.},
      {"period":"2024-01-01T01:00Z","respondent":"CISO","fueltype":"SUN","value":-5.},
      {"period":"2024-01-01T00:00Z","respondent":"CISO","fueltype":"WND","value":10.},
    ])
    result=audit(frame,2024,bas=("CISO",))
    sun=result[result.fueltype.eq("SUN")].iloc[0]
    assert sun.expected_hours==8784
    assert sun.missing_timestamp_hours==8782
    assert sun.negative_generation_hours==1
    assert sun.reported_generation_mwh_valid_nonnegative_only==0
    assert sun.reported_signed_net_generation_mwh==-5
    assert sun.negative_net_generation_mwh==-5
    assert sun.minimum_hourly_net_generation_mwh==-5
    assert not bool(sun.complete_nonnegative)

def test_renewables_reject_duplicate_hourly_fuel():
    row={"period":"2024-01-01T00:00Z","respondent":"BPAT","fueltype":"WND","value":10.}
    with pytest.raises(ValueError,match="Duplicate"):
        audit(pd.DataFrame([row,row]),2024,bas=("BPAT",))
