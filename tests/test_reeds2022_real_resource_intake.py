import pandas as pd
import pytest
from energy_transition.reeds2022_real_resource_intake import inspect_weather_index,HOURS

def calendar():
 return [x.strftime("%Y-%m-%d %H:%M:%S") for x in pd.date_range("2007-01-01",periods=8760,freq="h")]+[x.strftime("%Y-%m-%d %H:%M:%S") for x in pd.date_range("2012-01-01",periods=HOURS,freq="h")]
def test_source_2012_leap_rule():
 x,c=inspect_weather_index(calendar())
 assert len(x)==8760 and c["2012_Feb29_included"]
 assert c["2012_Dec31_excluded"] and c["demand_hour_ending_join_certified"] is False
def test_missing_hour_rejected():
 s=calendar();s.pop(-1)
 with pytest.raises(ValueError):inspect_weather_index(s)
def test_wrong_date_rejected():
 s=calendar();s[-1]="2012-12-31 00:00:00"
 with pytest.raises(ValueError):inspect_weather_index(s)
def test_duplicate_2012_rejected():
 s=calendar();s[-1]=s[-2]
 with pytest.raises(ValueError):inspect_weather_index(s)
