import pandas as pd
import pytest
from energy_transition.eia860_generator_poi_triage import triage

def fixture():
    return pd.DataFrame({
        "plant_id":["10","10","20","30"],
        "generator_id":["1","2","A","3"],
        "state":["CA","CA","NV","AZ"],
        "ba_code":["CISO","CISO","NEVP","AZPS"],
        "fuel":["NG","NG","SUN","WND"],
        "capacity_mw":[40.0,60.0,30.0,50.0],
        "nearest_candidate_bus":["b1","b1","b2","b3"],
        "distance_km":[61.,61.,3.,80.],
        "candidate_status":["candidate_only_no_approved_POI"]*4,
        "has_geographic_candidate":[True]*4,
        "electrical_connection_verified":[False]*4,
        "pypsa_generator_creation_approved":[False]*4,
    })

def test_generator_rows_aggregate_without_double_counting_plants():
    p,far,ba,r=triage(fixture())
    assert r["generator_rows"]==4
    assert r["operating_plant_count"]==3
    assert r["operating_nameplate_mw"]==pytest.approx(180)
    assert r["over50km_generator_rows"]==3
    assert r["over50km_plant_count"]==2
    assert r["over50km_nameplate_mw"]==pytest.approx(150)
    assert p.iloc[0]["plant_id"]=="10"
    assert len(ba)==3
    assert not p.electrical_connection_verified.any()
    assert not r["future_EFS_2030_2050_generation_admitted"]

def test_conflicting_bus_for_one_plant_fails():
    x=fixture()
    x.loc[1,"nearest_candidate_bus"]="b4"
    with pytest.raises(ValueError,match="Inconsistent nearest bus"):
        triage(x)

def test_duplicate_plant_generator_fails():
    x=fixture()
    x.loc[1,"generator_id"]="1"
    with pytest.raises(ValueError,match="Duplicate"):
        triage(x)

def test_claimed_poi_is_rejected():
    x=fixture()
    x.loc[0,"electrical_connection_verified"]=True
    with pytest.raises(ValueError,match="promoted"):
        triage(x)
