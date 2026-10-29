import calendar
import pandas as pd
from energy_transition.wind_availability import wind_sensitivity_profile

def test_wind_weighted_annual_mean_and_variability():
    ts=pd.DatetimeIndex([pd.Timestamp(2024,m,15,h) for m in range(1,13) for h in range(24)])
    weights=[calendar.monthrange(2024,m)[1] for m in range(1,13) for h in range(24)]
    profile=wind_sensitivity_profile(ts,weights)
    weighted=sum(profile.to_numpy()*weights)/sum(weights)
    assert abs(weighted-0.35)<1e-12
    assert 0<profile.min()<profile.max()<1
