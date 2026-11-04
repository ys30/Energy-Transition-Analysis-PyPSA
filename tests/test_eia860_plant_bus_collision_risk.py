import pandas as pd
import pytest
from energy_transition.eia860_plant_bus_collision_risk import audit_collisions

def sample():
    return pd.DataFrame({
      "plant_id":["1","2","3","4"],
      "state":["NM","NM","AZ","NM"],
      "ba_code":["PNM","SWPP","AZPS","PNM"],
      "nearest_candidate_bus":["b1","b1","b2","b1"],
      "distance_km":[150.,175.,60.,3.],
      "generator_count":[2,1,1,1],
      "operating_nameplate_mw":[200.,300.,400.,100.],
      "over50km":[True,True,True,False],
      "electrical_connection_verified":[False]*4,
      "empirical_generator_injection_approved":[False]*4,
    })

def test_far_plant_collision_capacity_preserved():
    clusters,r=audit_collisions(sample())
    assert r["long_distance_plants"]==3
    assert r["distinct_long_distance_candidate_buses"]==2
    assert r["candidate_buses_with_multiple_far_plants"]==1
    assert r["long_distance_plants_in_repeated_candidate_bus_groups"]==2
    assert r["nameplate_in_repeated_far_bus_groups_mw"]==pytest.approx(500)
    assert r["highest_risk_candidate_bus"]=="b1"
    assert r["electric_poi_connections_verified"]==0
    assert not r["future_generator_mapping_admitted"]

def test_false_poi_promotion_rejected():
    x=sample()
    x.loc[0,"electrical_connection_verified"]=True
    with pytest.raises(ValueError,match="promoted"):
        audit_collisions(x)

def test_invalid_distance_flag_rejected():
    x=sample()
    x.loc[0,"over50km"]=False
    with pytest.raises(ValueError,match="classification"):
        audit_collisions(x)

def test_duplicate_plant_rejected():
    x=sample()
    x.loc[1,"plant_id"]="1"
    with pytest.raises(ValueError,match="Duplicate"):
        audit_collisions(x)
