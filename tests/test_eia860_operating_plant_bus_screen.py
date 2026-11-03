"""Operating plant screening must exclude non-OP and unqualified generator capacity."""
import pandas as pd
import pytest
from energy_transition.eia860_operating_plant_bus_screen import audit


def _tables(tmp_path):
    candidates = tmp_path/"candidates.csv"
    generators = tmp_path/"generators.csv"
    pd.DataFrame([
        dict(plant_id="1",state="AZ",nearest_candidate_bus="busA",distance_km=4.0,
             assignment_status="geographic_candidate_only",electrical_connection_verified=False),
        dict(plant_id="2",state="AZ",nearest_candidate_bus="busB",distance_km=70.0,
             assignment_status="geographic_candidate_only",electrical_connection_verified=False),
        dict(plant_id="3",state="AZ",nearest_candidate_bus="busC",distance_km=3.0,
             assignment_status="geographic_candidate_only",electrical_connection_verified=False),
    ]).to_csv(candidates,index=False)
    pd.DataFrame([
        dict(plant_id="1",generator_id="A",state="AZ",status="OP",capacity_mw=50,ba_code="TEST",crosswalk_status="matched"),
        dict(plant_id="1",generator_id="B",state="AZ",status="SB",capacity_mw=90,ba_code="TEST",crosswalk_status="matched"),
        dict(plant_id="2",generator_id="C",state="AZ",status="OP",capacity_mw=75,ba_code="TEST",crosswalk_status="matched"),
        dict(plant_id="3",generator_id="D",state="AZ",status="OP",capacity_mw=20,ba_code="TEST",crosswalk_status="unmatched"),
        dict(plant_id="4",generator_id="E",state="AZ",status="OP",capacity_mw=10,ba_code="TEST",crosswalk_status="matched"),
    ]).to_csv(generators,index=False)
    return candidates,generators


def test_only_ba_matched_operating_nameplate_is_screened(tmp_path):
    c,g=_tables(tmp_path)
    output=tmp_path/"screen.csv"
    report=audit(c,g,output)
    result=pd.read_csv(output).set_index("plant_id")
    assert report["candidate_plants_with_qualified_op_generator"]==2
    assert report["qualified_operating_generator_rows_on_candidate_plants"]==2
    assert report["qualified_operating_nameplate_mw_on_candidate_plants"]==125
    assert report["qualified_operating_nameplate_mw_without_candidate"]==10
    assert report["candidate_op_plants_over_50km"]==1
    assert result.loc[1,"operating_nameplate_mw"]==50
    assert result.loc[3,"operating_nameplate_mw"]==0
    assert not result.ready_for_real_generator_injection.any()


def test_reject_state_conflict(tmp_path):
    c,g=_tables(tmp_path)
    d=pd.read_csv(g)
    d.loc[d.plant_id==1,"state"]="NM"
    d.to_csv(g,index=False)
    with pytest.raises(ValueError,match="state disagrees"):
        audit(c,g,tmp_path/"out.csv")


def test_reject_geographic_self_approval(tmp_path):
    c,g=_tables(tmp_path)
    d=pd.read_csv(c)
    d.loc[0,"electrical_connection_verified"]=True
    d.to_csv(c,index=False)
    with pytest.raises(ValueError,match="cannot be treated"):
        audit(c,g,tmp_path/"out.csv")
