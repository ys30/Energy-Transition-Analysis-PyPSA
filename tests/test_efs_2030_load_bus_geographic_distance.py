import pandas as pd
import pytest
from energy_transition.efs_2030_load_bus_geographic_distance import geographic_sensitivity

def fixture():
    buses=pd.DataFrame({"x":[-105.,-106.,-107.],"y":[35.,35.,35.]},index=["a","b","c"])
    rows=[{"Load_id":f"L{i}","original_first_bus_id":"a",
        "single_largest_positive_pd_connected_bus_id":"a" if i==0 else "b",
        "candidate_eligible_bus_count":0 if i==0 else 1,
        "original_zone_annual_mwh":0. if i==0 else 100.,
        "single_bus_source_candidate_changed":i!=0,
        "multibus_share_changed":0. if i==0 else 1.} for i in range(20)]
    return buses,pd.DataFrame(rows)

def test_geodesic_baseline_and_candidate_summary():
    b,r=fixture()
    output,summary=geographic_sensitivity(b,r)
    assert len(output)==20
    assert summary["zones_changing_single_max_pd_bus_id"]==19
    assert summary["nonzero_load_zones_changing_bus_id"]==19
    assert summary["original_source_annual_load_mwh"]==1900.
    assert 90<summary["single_max_pd_geodesic_distance_km_load_weighted_mean"]<92
    assert not summary["future_Western_OPF_solved"]

def test_unavailable_bus_rejected():
    b,r=fixture()
    r.loc[3,"single_largest_positive_pd_connected_bus_id"]="missing"
    with pytest.raises(ValueError,match="source ID"):
        geographic_sensitivity(b,r)

def test_falsely_marked_bus_change_rejected():
    b,r=fixture()
    r.loc[1,"single_bus_source_candidate_changed"]=False
    with pytest.raises(ValueError,match="flag mismatch"):
        geographic_sensitivity(b,r)
