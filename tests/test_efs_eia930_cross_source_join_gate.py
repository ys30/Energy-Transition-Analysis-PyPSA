import pandas as pd
import pytest
from energy_transition.efs_eia930_cross_source_join_gate import audit

def sources():
    efs=pd.DataFrame([
        {"year":y,"state":"California","reeds_zone":f"p{z}","local_hour_id":h,"allocated_mw":float(h)}
        for y in (2030,2040,2050) for z in range(1,21) for h in range(1,8761)
    ])
    eia=pd.DataFrame([
      {"season":s,"period":t,"respondent":ba,"fueltype":fuel,"reported_signed_net_mwh":-1. if i==0 else 5.}
      for s in ("winter","spring","summer","autumn")
      for ba in ("CISO","BPAT") for fuel in ("SUN","WND")
      for i,t in enumerate(pd.date_range("2024-01-08",periods=168,freq="h",tz="UTC"))
    ])
    return efs,eia

def test_original_cross_source_join_must_fail_closed():
    a,b=sources()
    r=audit(a,b,{"efs_zonal_source_sha256":"placeholder","eia930_2024_observed_source_sha256":"placeholder"})
    assert r["status"]=="FAIL_CLOSED_CROSS_SOURCE_JOIN_NOT_ADMITTED"
    assert r["verified_efs_zones"]==20
    assert r["joined_hourly_output_rows"]==0
    assert not r["weather_synchronized_power_dispatch_admitted"]
    assert len(r["refusal_reasons"])==6

def test_duplicate_eia_hour_rejected():
    a,b=sources()
    with pytest.raises(ValueError,match="Invalid EIA"):
        audit(a,pd.concat([b,b.iloc[[0]]]),{})

def test_missing_efs_hour_rejected():
    a,b=sources()
    with pytest.raises(ValueError,match="coverage invalid"):
        audit(a.iloc[:-1],b,{})

def test_observed_year_swap_rejected():
    a,b=sources()
    b["period"]=pd.to_datetime(b.period)+pd.DateOffset(years=1)
    with pytest.raises(ValueError,match="not 2024"):
        audit(a,b,{})
