import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box
from energy_transition.efs_2030_pinned_reeds_polygon_overlay import review

def fixtures():
    b_ids=[];states=[];zones=[];xs=[];ys=[]
    rows=[]
    polys=[]
    for i in range(20):
        zone=f"p{i+1}"
        state="New Mexico"
        polys.append(box(i*2,0,i*2+1.5,1))
        for suffix,x in [("a",i*2+.25),("b",i*2+1.0)]:
            b_ids.append(f"{zone}_{suffix}")
            states.append(state);zones.append(zone);xs.append(x);ys.append(.5)
        rows.append({"Load_id":f"EFS_2030_{zone}_{state}",
                     "original_first_bus_id":f"{zone}_a",
                     "single_largest_positive_pd_connected_bus_id":f"{zone}_b",
                     "original_zone_annual_mwh":274706987.114121/20})
    b=pd.DataFrame({"state":states,"reeds_zone":zones,"x":xs,"y":ys},index=b_ids)
    geo=gpd.GeoDataFrame({"rb":[f"p{i+1}" for i in range(20)]},geometry=polys,crs="EPSG:4326")
    return b,pd.DataFrame(rows),geo

def test_pinned_polygon_overlay_and_energy_identity():
    b,c,g=fixtures()
    d,r=review(b,c,g)
    assert len(d)==20
    assert r["original_firstbus_raw_polygon_mismatch_count"]==0
    assert r["max_pd_raw_polygon_mismatch_count"]==0
    assert r["source_pilot_ReEDS_zone_count"]==20
    assert not r["full_original_network_ReEDS_region_membership_certified"]
    assert not r["real_grid_OPF_solved"]

def test_raw_polygon_boundary_issue_is_detected_not_fixed():
    b,c,g=fixtures()
    b.loc["p1_a","x"]=-.2
    d,r=review(b,c,g)
    assert r["original_firstbus_raw_polygon_mismatch_count"]==1
    assert r["max_pd_raw_polygon_mismatch_count"]==0
    assert r["original_firstbus_raw_polygon_mismatch_Load_IDs"]==["EFS_2030_p1_New Mexico"]

def test_missing_source_reeds_shape_fails():
    b,c,g=fixtures()
    g=g.loc[g.rb.ne("p1")]
    with pytest.raises(ValueError,match="polygon missing"):
        review(b,c,g)
