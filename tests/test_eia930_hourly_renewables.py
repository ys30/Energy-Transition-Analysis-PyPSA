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

def test_season_profiles_retain_signed_generation_and_reject_missing():
    from energy_transition.eia930_hourly_renewables import season_profiles
    dates=pd.date_range("2024-01-08",periods=168,freq="h",tz="UTC")
    frame=pd.DataFrame([{"period":date,"respondent":ba,"fueltype":fuel,"value":(-2. if fuel=="SUN" else 5.)}
         for date in dates for ba in ("CISO","BPAT") for fuel in ("SUN","WND")])
    weeks=season_profiles(frame,starts={"winter":"2024-01-08T00:00:00Z"})
    assert len(weeks)==672
    assert weeks.loc[weeks.fueltype.eq("SUN"),"reported_signed_net_mwh"].sum()==-672.
    with pytest.raises(ValueError,match="incomplete"):
        season_profiles(frame.iloc[:-1],starts={"winter":"2024-01-08T00:00:00Z"})
