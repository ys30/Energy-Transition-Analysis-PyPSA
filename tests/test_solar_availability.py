import pandas as pd
from energy_transition.solar_availability import solar_daylight_profile

def test_pv_day_night():
    stamps=pd.date_range("2024-01-15",periods=24,freq="h",tz="UTC")
    p=solar_daylight_profile(stamps)
    local=stamps.tz_convert("America/Los_Angeles").hour
    assert (p[(local<6)|(local>=18)]==0).all()
    assert p.max()<=1
    assert p.max()>0.4

def test_full_year_month_hours():
    stamps=pd.DatetimeIndex([pd.Timestamp(year=2024,month=m,day=15,hour=h) for m in range(1,13) for h in range(24)])
    p=solar_daylight_profile(stamps)
    assert abs(p.mean()-0.26)<0.001
