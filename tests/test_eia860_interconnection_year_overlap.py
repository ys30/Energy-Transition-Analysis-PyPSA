"""Contract tests for deduplicated EIA-860 plant review queues."""
import pandas as pd
import pytest
from energy_transition.eia860_interconnection_year_overlap import merge_queues


def make_queue(path, ids, flagged=None):
    flagged=set(flagged or [])
    pd.DataFrame([
        {"plant_id":str(i),"nearest_candidate_bus":f"B{i}","distance_km":60 if i in flagged else 2,
         "long_distance":i in flagged,"material_grid_candidate_change":i not in flagged,
         "priority_reason":"nearest_bus_over_50km" if i in flagged else "main_grid_candidate_changed_over_1km",
         "electrical_connection_verified":False,"eligible_for_real_dispatch":False}
        for i in ids
    ]).to_csv(path,index=False)


def test_plant_ids_are_deduplicated_across_years(tmp_path):
    a=tmp_path/"2023.csv";b=tmp_path/"2024.csv";out=tmp_path/"joined.csv"
    make_queue(a,[1,2,3],{1,2})
    make_queue(b,[2,3,4],{2,4})
    r=merge_queues(a,b,out)
    assert r["unique_priority_plant_ids"]==4
    assert r["review_both_years"]==2
    assert r["only_2023"]==1
    assert r["only_2024"]==1
    assert not pd.read_csv(out).eligible_for_real_dispatch.any()
    persistent=pd.read_csv(tmp_path/"joined_persistent.csv",dtype={"plant_id":"string"})
    single=pd.read_csv(tmp_path/"joined_year_specific.csv",dtype={"plant_id":"string"})
    assert len(persistent)==2
    assert len(single)==2
    assert set(persistent.plant_id).isdisjoint(set(single.plant_id))
    assert set(pd.read_csv(out,dtype={"plant_id":"string"}).plant_id)==set(persistent.plant_id)|set(single.plant_id)
    assert persistent.review_both_years.all()
    assert not single.review_both_years.any()



def test_duplicate_plant_id_rejected(tmp_path):
    a=tmp_path/"2023.csv";b=tmp_path/"2024.csv";out=tmp_path/"joined.csv"
    make_queue(a,[1,1],{1});make_queue(b,[2],{2})
    with pytest.raises(ValueError,match="duplicate or null"):
        merge_queues(a,b,out)


def test_unverified_connection_cannot_be_approved(tmp_path):
    a=tmp_path/"2023.csv";b=tmp_path/"2024.csv";out=tmp_path/"joined.csv"
    make_queue(a,[1],{1});make_queue(b,[2],{2})
    d=pd.read_csv(a);d.loc[0,"eligible_for_real_dispatch"]=True;d.to_csv(a,index=False)
    with pytest.raises(ValueError,match="unverified approved"):
        merge_queues(a,b,out)
