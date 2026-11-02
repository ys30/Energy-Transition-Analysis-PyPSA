"""Review queue remains evidence-only, including overlapping priority groups."""
import pandas as pd
import pytest
from energy_transition.eia860_interconnection_priority_queue import triage


def test_queue_deduplicates_distance_and_material_priorities(tmp_path):
    a=tmp_path/"candidate.csv";b=tmp_path/"material.csv";out=tmp_path/"review.csv"
    pd.DataFrame([
      {"plant_id":"1","nearest_candidate_bus":"A","distance_km":51,
       "assignment_status":"geographic_candidate_only","electrical_connection_verified":False},
      {"plant_id":"2","nearest_candidate_bus":"B","distance_km":2,
       "assignment_status":"geographic_candidate_only","electrical_connection_verified":False},
      {"plant_id":"3","nearest_candidate_bus":"C","distance_km":53,
       "assignment_status":"geographic_candidate_only","electrical_connection_verified":False},
    ]).to_csv(a,index=False)
    pd.DataFrame([{"plant_id":"1","main_component_candidate_bus":"D"},
                  {"plant_id":"2","main_component_candidate_bus":"E"}]).to_csv(b,index=False)
    report=triage(a,b,out,2024)
    q=pd.read_csv(out,dtype={"plant_id":"string"})
    assert report["unique_priority_plant_count"]==3
    assert report["both_categories_count"]==1
    assert q.loc[q.plant_id.eq("1"),"priority_reason"].iloc[0]=="both"
    assert not q.eligible_for_real_dispatch.any()
    assert report["verified_electrical_connections"]==0


def test_queue_rejects_false_electrical_provenance(tmp_path):
    a=tmp_path/"candidate.csv";b=tmp_path/"material.csv"
    pd.DataFrame([{"plant_id":"1","nearest_candidate_bus":"A","distance_km":10,
      "assignment_status":"geographic_candidate_only","electrical_connection_verified":True}]).to_csv(a,index=False)
    pd.DataFrame(columns=["plant_id","main_component_candidate_bus"]).to_csv(b,index=False)
    with pytest.raises(ValueError,match="certified"):
        triage(a,b,tmp_path/"out.csv",2024)
