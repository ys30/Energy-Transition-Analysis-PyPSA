import numpy as np
import pandas as pd
import pytest
from energy_transition.renewable_2012_resource_intake import evaluate

def metadata(product="wind_toolkit"):
    return {"product":product,"source_url":"https://developer.nlr.gov/docs/wind/wind-toolkit/wtk-download/",
            "source_year":2012,"requested_utc":True,"requested_leap_day":False,
            "requested_interval_minutes":60,"site_lat":35.,"site_lon":-106.,
            "source_time_interpretation":"interval_midpoint",
            "source_data_timezone_hours":0,
            "original_api_query_redacted":"names=2012&interval=60&utc=true&leap_day=false&api_key=[REDACTED]"}

def frame(product="wind_toolkit",minute=30):
    times=pd.date_range("2012-01-01","2013-01-01",freq="h",inclusive="left",tz="UTC")
    times=times[~((times.month==2)&(times.day==29))]
    times=times+pd.Timedelta(minutes=minute)
    d=pd.DataFrame({"Year":times.year,"Month":times.month,"Day":times.day,
                    "Hour":times.hour,"Minute":times.minute})
    if product=="wind_toolkit":
        d["windspeed_100m"]=np.full(len(d),8.)
    else:
        d["ghi"]=np.full(len(d),200.)
        d["dni"]=np.full(len(d),100.)
        d["dhi"]=np.full(len(d),100.)
    return d

def test_wind_2012_nonleap_utc_source_intake():
    r=evaluate(frame(),metadata())
    assert r["source_hourly_count"]==8760
    assert r["utc_time_keys_complete"]
    assert not r["EFS_load_resource_join_admitted"]
    assert not r["generator_capacity_factor_computed"]

def test_solar_2012_source_intake():
    r=evaluate(frame("nsrdb",0),metadata("nsrdb"))
    assert r["resource_statistics"]["ghi"]["mean"]==pytest.approx(200.)

def test_wrong_time_requires_hard_failure():
    bad=frame().copy()
    bad.loc[4000,"Hour"]=5
    with pytest.raises(ValueError,match="Source calendar"):
        evaluate(bad,metadata())

def test_missing_or_duplicate_hour_requires_failure():
    with pytest.raises(ValueError,match="8760"):
        evaluate(frame().iloc[:-1],metadata())
    d=frame()
    d.iloc[1]=d.iloc[0]
    with pytest.raises(ValueError,match="Duplicate"):
        evaluate(d,metadata())

def test_2012_resource_not_automatically_admitted_to_efs():
    with pytest.raises(ValueError,match="UTC request"):
        evaluate(frame(),{**metadata(),"requested_utc":False})
    with pytest.raises(ValueError,match="nonleap"):
        evaluate(frame(),{**metadata(),"requested_leap_day":True})
    with pytest.raises(ValueError,match="2012"):
        evaluate(frame(),{**metadata(),"source_year":2013})

def test_negative_wind_and_extreme_solar_rejected():
    d=frame()
    d.loc[0,"windspeed_100m"]=-1.
    with pytest.raises(ValueError,match="Invalid nonnegative"):
        evaluate(d,metadata())
    solar=frame("nsrdb",0)
    solar.loc[0,"ghi"]=1800.
    with pytest.raises(ValueError,match="Solar irradiance"):
        evaluate(solar,metadata("nsrdb"))
