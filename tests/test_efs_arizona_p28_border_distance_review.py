import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from energy_transition.efs_arizona_p28_border_distance_review import review

def test_az_p28_border_distance_and_all_state_matches():
    polygons=gpd.GeoDataFrame({
        "name":["Arizona","New Mexico"],"iso_a2":["US","US"]},
        geometry=[box(-113.,31.,-110.,36.),box(-110.,31.,-106.,36.)],
        crs="EPSG:4326")
    df=pd.DataFrame([{
        "Load_id":"EFS_2030_p28_Arizona",
        "original_bus_id":"2040000",
        "single_max_pd_candidate_bus_id":"2040003",
        "first_bus_lon":-109.8,"first_bus_lat":34.0,
        "max_pd_bus_lon":-111.,"max_pd_bus_lat":34.,
        "original_annual_mwh":71277837.59426476
    }])
    r=review(df,polygons)
    assert len(r["actual_source_geographic_review"])==2
    before,after=r["actual_source_geographic_review"]
    assert before["all_US_Natural_Earth_state_polygon_matches"]==["New Mexico"]
    assert not before["inside_Natural_Earth_Arizona_polygon"]
    assert before["minimum_EPSG5070_point_to_Arizona_polygon_km"]>0
    assert after["inside_Natural_Earth_Arizona_polygon"]
    assert after["minimum_EPSG5070_point_to_Arizona_polygon_km"]==0
    assert not r["candidate_load_reassignment_admitted"]
