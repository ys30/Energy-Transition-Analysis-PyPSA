import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box
from energy_transition.efs_cross_bus_pinned_natural_earth import audit_natural_earth

SOURCE='''shpreader.natural_earth(
    resolution="10m",
    category="cultural",
    name=state_shape,
)
if attr["iso_a2"] in countries: pass
'''

def fixture():
    points=pd.DataFrame([
        {"bus_id":"2030005","x":-120.003,"y":39.7699,"state":"Nevada","Pd":34.99,"LAF_state":34.99/67028.96},
        {"bus_id":"2013019","x":-123.962,"y":46.2056,"state":"Washington","Pd":17.49,"LAF_state":17.49/9281.36},
    ])
    states=gpd.GeoDataFrame(
        {"name":["California","Nevada","Oregon","Washington"],
         "iso_a2":["US"]*4},
        geometry=[box(-121,39,-120,40),box(-120,39,-118,41),
                  box(-125,45,-123,46.3),box(-125,46.3,-123,48)],
        crs="EPSG:4326")
    return points,states

def test_pinned_source_method_is_only_comparative_without_archived_shape_version():
    points,states=fixture()
    r=audit_natural_earth(points,states,archive_sha256="e"*64,source_code=SOURCE)
    assert r["all_matches_inferred_source"]
    assert not r["original_archived_build_full_state_labels_recovered"]
    assert not r["empirically_admitted_11_state_EFS"]

def test_wrong_source_method_is_rejected():
    points,states=fixture()
    with pytest.raises(ValueError,match="not verified"):
        audit_natural_earth(points,states,archive_sha256="e"*64,
                            source_code=SOURCE.replace('resolution="10m"','resolution="110m"'))

def test_missing_usa_natural_earth_state_fails_closed():
    points,states=fixture()
    states.loc[states.name=="Oregon","iso_a2"]="CA"
    with pytest.raises(ValueError,match="coverage is incomplete"):
        audit_natural_earth(points,states,archive_sha256="e"*64,source_code=SOURCE)
