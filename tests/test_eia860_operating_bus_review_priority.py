"""Regression for operating MW-weighted bus candidate evidence review."""
import pandas as pd
import pytest
from energy_transition.eia860_operating_bus_review_priority import audit


def sample(tmp_path):
    source=tmp_path/"screen.csv"
    pd.DataFrame([
        dict(plant_id="1",state="AZ",nearest_candidate_bus="b1",distance_km=2,
             operating_generator_count=2,operating_nameplate_mw=100,
             has_qualified_operating_generator=True,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
        dict(plant_id="2",state="AZ",nearest_candidate_bus="b2",distance_km=62,
             operating_generator_count=1,operating_nameplate_mw=150,
             has_qualified_operating_generator=True,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
        dict(plant_id="3",state="NM",nearest_candidate_bus="b3",distance_km=80,
             operating_generator_count=0,operating_nameplate_mw=0,
             has_qualified_operating_generator=False,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
    ]).to_csv(source,index=False)
    return source


def test_operating_distance_priority_and_capacity(tmp_path):
    source=sample(tmp_path)
    out=tmp_path/"ranked.csv"
    result=audit(source,out)
    assert result["screened_operating_plants"]==2
    assert result["screened_operating_generators"]==3
    assert result["operating_nameplate_mw_over_50km"]==150
    assert result["operating_nameplate_fraction_over_50km"]==0.6
    assert result["electrical_connections_verified"]==0
    assert pd.read_csv(out).iloc[0].plant_id==2
    assert len(pd.read_csv(tmp_path/"ranked_over50km.csv"))==1
    assert sum(result["distance_band_counts"].values())==2


def test_refuse_candidate_self_approval(tmp_path):
    source=sample(tmp_path)
    frame=pd.read_csv(source)
    frame.loc[0,"ready_for_real_generator_injection"]=True
    frame.to_csv(source,index=False)
    with pytest.raises(ValueError,match="must not be approved"):
        audit(source,tmp_path/"out.csv")


def test_invalid_distance_is_rejected(tmp_path):
    source=sample(tmp_path)
    frame=pd.read_csv(source)
    frame.loc[0,"distance_km"]=-1
    frame.to_csv(source,index=False)
    with pytest.raises(ValueError,match="distance_km"):
        audit(source,tmp_path/"out.csv")
