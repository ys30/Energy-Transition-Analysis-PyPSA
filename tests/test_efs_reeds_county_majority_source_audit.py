from types import SimpleNamespace
import geopandas as gpd
import pandas as pd
from shapely.geometry import box
from energy_transition.efs_reeds_county_majority_source_audit import audit

def test_county_majority_postprocessing_is_distinct_from_raw_polygon_membership():
    b=pd.DataFrame([
       {"x":-.1,"y":.5,"county":"A","reeds_zone":"p28","state":"Arizona"},
       {"x":.5,"y":.5,"county":"A","reeds_zone":"p28","state":"Arizona"},
       {"x":2.5,"y":.5,"county":"B","reeds_zone":"p18","state":"Montana"},
       {"x":2.7,"y":.5,"county":"B","reeds_zone":"p18","state":"Montana"},
       {"x":3.5,"y":.5,"county":"B","reeds_zone":"p18","state":"Montana"}],
       index=["2040000","x","2077004","y","z"])
    polys=gpd.GeoDataFrame(
       {"rb":["p28","p18","p19"]},
       geometry=[box(0,0,1,1),box(3,0,4,1),box(2,0,3,1)],
       crs="EPSG:4326")
    r=audit(b,polys)
    assert len(r["reviewed_source_load_cases"])==2
    assert r["all_target_archived_counties_finally_uniform"] is True
    mt=r["reviewed_source_load_cases"][1]
    assert mt["source_county_raw_polygon_single_cover_counts"]=={"p19":2,"p18":1}
    assert mt["source_county_final_reeds_zone_counts"]=={"p18":3}
    assert mt["archived_final_zone_is_raw_polygon_county_mode"] is False
    assert not r["historical_premajority_bus_labels_recovered"]
    assert not r["physically_validated_western_OPF"]
