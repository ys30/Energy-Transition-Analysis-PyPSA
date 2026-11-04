import pandas as pd
import pytest
from energy_transition.efs_source_zone_bus_spatial_dispersion import audit

def samples():
    bids=[];states=[];zones=[];xs=[];ys=[];pds=[]
    source=[]
    for i in range(20):
        for j in range(3):
            bids.append(f"{i}_{j}")
            states.append("New Mexico")
            zones.append(f"p{i}")
            xs.append(-105.+j*.05)
            ys.append(35.+i*.01)
            pds.append(float(j))
        source.append({
            "Load_id":f"EFS_2030_p{i}_New Mexico",
            "original_first_bus_id":f"{i}_0",
            "single_largest_positive_pd_connected_bus_id":f"{i}_2",
            "original_zone_annual_mwh":274706987.114121/20})
    b=pd.DataFrame({"state":states,"reeds_zone":zones,"x":xs,"y":ys,"Pd":pds},index=bids)
    s=pd.DataFrame(source)
    return b,s

def test_same_source_zone_pairs_and_geometry_reconcile():
    b,s=samples()
    d,r=audit(b,s)
    assert len(d)==20
    assert r["all_pairs_share_same_exported_state_and_reeds_zone_labels"]
    assert 8<r["source_candidate_pair_distance_km_median"]<10
    assert r["source_region_bus_coordinate_radius_p90_km_median_of_20_zones"]>0
    assert not r["independent_reeds_zone_polygon_available"]
    assert not r["full_western_OPF_solved"]

def test_mislabeled_cross_zone_candidate_fails():
    b,s=samples()
    s.loc[0,"single_largest_positive_pd_connected_bus_id"]="1_2"
    with pytest.raises(ValueError,match="zone keys disagree"):
        audit(b,s)

def test_source_annual_demand_mismatch_fails():
    b,s=samples()
    s.loc[0,"original_zone_annual_mwh"]+=200.
    with pytest.raises(ValueError,match="total mismatch"):
        audit(b,s)
