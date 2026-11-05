import pandas as pd
import pytest
from energy_transition.eia930_observed_shape_boundary import audit

def sample():
    seasons=("winter","spring","summer","autumn")
    rows=[]
    for s in seasons:
        for b in ("CISO","BPAT"):
            for f in ("SUN","WND"):
                for i,t in enumerate(pd.date_range("2024-01-08",periods=168,freq="h",tz="UTC")):
                    rows.append({"season":s,"period":str(t),"respondent":b,"fueltype":f,
                                 "reported_signed_net_mwh":-5 if i==0 else (10 if i%2 else 0)})
    return pd.DataFrame(rows)

def test_accepts_complete_seasonal_signed_sources():
    s,m=audit(sample())
    assert len(s)==16
    assert len(set(s.n_observed_hours))==1
    assert (s.negative_hours==1).all()
    assert (s.negative_component_mwh==-5).all()
    assert m["expected_hourly_records"]==2688
    assert not m["renewable_capacity_factor_valid"]
    assert not m["efs_2030_2050_hour_alignment_admitted"]

def test_missing_hour_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        audit(sample().iloc[:-1])

def test_duplicate_hour_rejected():
    d=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        audit(pd.concat([d,d.iloc[[0]]]))

def test_negative_values_are_preserved():
    s,_=audit(sample())
    r=s.iloc[0]
    assert r.signed_reported_generation_mwh==pytest.approx(r.positive_component_mwh+r.negative_component_mwh)
