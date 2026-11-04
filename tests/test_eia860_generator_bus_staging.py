import pandas as pd
import pytest
from energy_transition.eia860_generator_bus_staging import stage_generator_candidates

def sample():
    c=pd.DataFrame({
        "plant_id":["100","200"],"nearest_candidate_bus":["b1","b2"],
        "distance_km":[2.0,55.0],"state":["CA","AZ"],
        "assignment_status":["geographic_candidate_only"]*2,
        "electrical_connection_verified":[False,False],
    })
    g=pd.DataFrame({
        "plant_id":["100","100","200","300","100"],
        "generator_id":["1","2","1","1","3"],
        "status":["OP","OP","OP","OP","RE"],
        "capacity_mw":[100.,50.,20.,30.,80.],
        "fuel":["NG","NG","WND","SOL","NG"],
        "state":["CA","CA","AZ","NM","CA"],
        "ba_code":["CISO","CISO","AZPS","PNM","CISO"],
        "crosswalk_status":["matched"]*5,
    })
    return c,g

def test_generator_level_staging_never_approves_physical_buses():
    rows,r=stage_generator_candidates(*sample())
    assert r["official_2024_operating_generator_rows"]==4
    assert r["candidate_generator_rows"]==3
    assert r["candidate_generator_plant_count"]==2
    assert r["candidate_geographic_nameplate_mw"]==pytest.approx(170.)
    assert r["unmapped_nameplate_mw"]==pytest.approx(30.)
    assert r["candidate_over_50km_generator_rows"]==1
    assert not rows.pypsa_generator_creation_approved.any()
    assert not rows.electrical_connection_verified.any()
    assert r["actual_network_generators_added"]==0
    assert not r["future_2030_2040_2050_generator_fleet_verified"]

def test_duplicate_generator_ids_rejected():
    c,g=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        stage_generator_candidates(c,pd.concat([g,g.iloc[[0]]],ignore_index=True))

def test_mismatched_plant_source_state_rejected():
    c,g=sample()
    c.loc[c.plant_id=="100","state"]="AZ"
    with pytest.raises(ValueError,match="differs"):
        stage_generator_candidates(c,g)

def test_false_electrical_claim_rejected():
    c,g=sample()
    c.loc[0,"electrical_connection_verified"]=True
    with pytest.raises(ValueError,match="cannot attest"):
        stage_generator_candidates(c,g)
