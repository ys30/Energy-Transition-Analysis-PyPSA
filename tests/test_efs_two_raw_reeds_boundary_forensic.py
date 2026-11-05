from types import SimpleNamespace
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from energy_transition.efs_two_raw_reeds_boundary_forensic import audit

def test_raw_pinned_reeds_boundary_distance_two_original_fixtures():
    shapes=gpd.GeoDataFrame(
        {"rb":["p28","p18","p27"]},
        geometry=[box(-114.,32.,-112.,34.),box(-110.,44.,-108.,46.),box(-112.,32.,-110.,34.)],
        crs="EPSG:4326")
    buses=pd.DataFrame([
        {"x":-114.1,"y":33.,"reeds_zone":"p28","state":"Arizona"},
        {"x":-113.,"y":33.,"reeds_zone":"p28","state":"Arizona"},
        {"x":-110.1,"y":45.,"reeds_zone":"p18","state":"Montana"},
        {"x":-109.,"y":45.,"reeds_zone":"p18","state":"Montana"}],
        index=["2040000","2040003","2077004","2077101"])
    source=pd.DataFrame([
      {"Load_id":"EFS_2030_p28_Arizona","original_first_bus_id":"2040000",
       "single_largest_positive_pd_connected_bus_id":"2040003",
       "original_zone_annual_mwh":71277837.59426476},
      {"Load_id":"EFS_2030_p18_Montana","original_first_bus_id":"2077004",
       "single_largest_positive_pd_connected_bus_id":"2077101",
       "original_zone_annual_mwh":5720456.10302669}
    ])
    r=audit(SimpleNamespace(buses=buses),source,shapes)
    assert len(r["source_bus_results"])==4
    assert len([x for x in r["source_bus_results"] if x["inside_source_label_raw_polygon"]])==2
    assert r["source_bus_results"][0]["projected_distance_to_source_label_raw_polygon_km"]>0
    assert r["source_bus_results"][1]["projected_distance_to_source_label_raw_polygon_km"]==0
    assert not r["actual_Western_OPF_solved"]
