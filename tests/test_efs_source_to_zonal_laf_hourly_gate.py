import pandas as pd
import pytest
from energy_transition.efs_source_to_zonal_laf_hourly_gate import audit


def case():
    source=pd.DataFrame([
        {"year":2030,"state":"AZ","local_hour_id":h,"load_mw":10.*h}
        for h in (1,2,3)])
    buses=pd.DataFrame([
        {"state":"Arizona","reeds_zone":"p1","LAF_state":0.2},
        {"state":"Arizona","reeds_zone":"p1","LAF_state":0.3},
        {"state":"Arizona","reeds_zone":"p2","LAF_state":0.5}])
    zonal=pd.DataFrame([
        {"year":2030,"state":"Arizona","reeds_zone":zone,
         "local_hour_id":h,"allocated_mw":10.*h*weight}
        for h in (1,2,3) for zone,weight in (("p1",0.5),("p2",0.5))])
    return source,zonal,buses


def check(s,z,b):
    return audit(s,z,b,years=(2030,),hours=3,expected_states={"Arizona"})


def test_exact_allocation_and_mass():
    s,z,b=case()
    r=check(s,z,b)
    assert r["zonal_hour_rows_compared"]==6
    assert r["state_year_hour_rows_compared"]==3
    assert r["state_laf_mass"]["Arizona"]==pytest.approx(1.)
    assert not r["joint_utc_dispatch_admitted"]


def test_reject_corrupt_single_zonal_hour():
    s,z,b=case()
    z.loc[0,"allocated_mw"]+=1
    with pytest.raises(ValueError,match="Zonal hourly allocation mismatch"):
        check(s,z,b)


def test_reject_missing_zone_hour():
    s,z,b=case()
    with pytest.raises(ValueError,match="Missing or extra"):
        check(s,z.iloc[:-1],b)


def test_reject_duplicate_source_hour():
    s,z,b=case()
    with pytest.raises(ValueError,match="Duplicate"):
        check(pd.concat([s,s.iloc[[0]]]),z,b)


def test_reject_overweight_state():
    s,z,b=case()
    b.loc[0,"LAF_state"]=1.
    with pytest.raises(ValueError,match="Invalid admitted LAF"):
        check(s,z,b)
