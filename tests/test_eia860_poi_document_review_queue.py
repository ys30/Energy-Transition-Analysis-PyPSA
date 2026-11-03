"""POI research queues prioritize capacity without mistaking map proximity for proof."""
import pandas as pd
import pytest
from energy_transition.eia860_poi_document_review_queue import audit


def _screen(tmp_path):
    src=tmp_path/"screen.csv"
    pd.DataFrame([
        dict(plant_id="1",plant_name="Official Plant One",ba_code="BA1",state="AZ",nearest_candidate_bus="b1",distance_km=3,
             operating_generator_count=2,operating_nameplate_mw=500,
             has_qualified_operating_generator=True,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
        dict(plant_id="2",ba_code="BA1",state="AZ",nearest_candidate_bus="b2",distance_km=80,
             operating_generator_count=1,operating_nameplate_mw=120,
             has_qualified_operating_generator=True,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
        dict(plant_id="3",ba_code="BA2",state="NM",nearest_candidate_bus="b3",distance_km=60,
             operating_generator_count=1,operating_nameplate_mw=300,
             has_qualified_operating_generator=True,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
        dict(plant_id="4",ba_code=None,state="NM",nearest_candidate_bus="b4",distance_km=1,
             operating_generator_count=0,operating_nameplate_mw=0,
             has_qualified_operating_generator=False,electrical_connection_verified=False,
             ready_for_real_generator_injection=False),
    ]).to_csv(src,index=False)
    return src


def test_review_queue_reconciles_source_and_preserves_unverified_status(tmp_path):
    src=_screen(tmp_path)
    out=tmp_path/"queue"
    result=audit(src,out,top_n=2)
    assert result["source_operating_plants"]==3
    assert result["source_operating_generator_count"]==4
    assert result["source_operating_nameplate_mw"]==920
    assert result["long_distance_plants"]==2
    assert result["long_distance_nameplate_mw"]==420
    assert result["top_capacity_review_nameplate_mw"]==800
    assert result["source_capacity_reconciles_with_ba_state_groups"] is True
    assert result["electrical_connections_verified"]==0
    priority=pd.read_csv(out/"top_operating_plant_poi_review.csv")
    far=pd.read_csv(out/"top_long_distance_operating_plant_poi_review.csv")
    assert priority.plant_id.tolist()==[1,3]
    assert priority.loc[0,"plant_name"]=="Official Plant One"
    assert pd.isna(priority.loc[1,"plant_name"])
    assert far.plant_id.tolist()==[3,2]
    assert not priority.eligible_for_empirical_dispatch.any()
    assert not far.electrical_connection_verified.any()
    assert pd.read_csv(out/"operating_poi_review_by_ba_state.csv").operating_nameplate_mw.sum()==920


def test_reject_approval_from_geographic_candidate(tmp_path):
    src=_screen(tmp_path)
    d=pd.read_csv(src)
    d.loc[0,"electrical_connection_verified"]=True
    d.to_csv(src,index=False)
    with pytest.raises(ValueError,match="approved connection"):
        audit(src,tmp_path/"queue")


def test_bad_operating_capacity_blocks_rank(tmp_path):
    src=_screen(tmp_path)
    d=pd.read_csv(src)
    d.loc[0,"operating_nameplate_mw"]=-10
    d.to_csv(src,index=False)
    with pytest.raises(ValueError,match="operating_nameplate_mw"):
        audit(src,tmp_path/"queue")
