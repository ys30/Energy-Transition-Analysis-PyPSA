import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from energy_transition.efs_2030_placement_state_polygon_audit import review

def test_polygon_matching_not_confused_with_verified_delivery():
    names=["Arizona","Colorado","Idaho","Montana","New Mexico","Utah","Wyoming"]
    g=gpd.GeoDataFrame({"name":names,"iso_a2":["US"]*7},
        geometry=[box(i*2,0,i*2+1,1) for i in range(7)],crs="EPSG:4326")
    rows=[]
    for i in range(20):
        state=names[i%7]
        x=(i%7)*2+.5
        rows.append({"Load_id":f"EFS_2030_p{i}_{state}","original_bus_id":str(i),
            "single_max_pd_candidate_bus_id":str(100+i),
            "first_bus_lat":.5,"first_bus_lon":x,
            "max_pd_bus_lat":.5,"max_pd_bus_lon":x if i else 12.5,
            "original_annual_mwh":100.})
    tab,r=review(pd.DataFrame(rows),g,"testhash")
    assert len(tab)==20
    assert r["original_exported_state_polygon_mismatch_count"]==0
    assert r["max_pd_exported_state_polygon_mismatch_count"]==1
    assert r["max_pd_mismatch_zonal_Load_IDs"]==["EFS_2030_p0_Arizona"]
    assert not r["official_utility_delivery_points_certified"]
