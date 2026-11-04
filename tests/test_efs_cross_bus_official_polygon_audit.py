"""Census polygon overlay stays separate from source full_state provenance."""
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import box
from energy_transition.efs_cross_bus_official_polygon_audit import audit


def fixture():
    points=pd.DataFrame([
        {"bus_id":"2030005","x":-120.003,"y":39.7699,"state":"Nevada","Pd":34.99,"LAF_state":34.99/67028.96},
        {"bus_id":"2013019","x":-123.962,"y":46.2056,"state":"Washington","Pd":17.49,"LAF_state":17.49/9281.36},
    ])
    states=gpd.GeoDataFrame(
        {"NAME":["California","Nevada","Oregon","Washington"]},
        geometry=[
            box(-121,39,-120,40),
            box(-120,39,-118,41),
            box(-125,45,-123,46.3),
            box(-125,46.3,-123,48),
        ],
        crs="EPSG:4326")
    return points,states


def test_official_polygon_comparison_is_not_upstream_full_state_certification():
    points,states=fixture()
    result=audit(points,states,source_archive_sha256="a"*64)
    assert len(result["bus_audits"])==2
    assert all("independent_polygon_supports_inferred_denominator_state"==r["classification"]
               for r in result["bus_audits"])
    assert result["independent_state_polygon_point_overlay_performed"]
    assert result["candidate_4_state_EFS_weights_empirically_admitted"] is False
    assert result["original_pinned_full_state_polygon_recovered"] is False


def test_unrecognized_geographic_layer_is_rejected():
    points,states=fixture()
    states=states.loc[states.NAME!="Oregon"]
    with pytest.raises(ValueError,match="Incomplete authoritative"):
        audit(points,states,source_archive_sha256="b"*64)


def test_unexpected_bus_state_is_rejected():
    points,states=fixture()
    points.loc[0,"state"]="California"
    with pytest.raises(ValueError,match="Exported bus state has changed"):
        audit(points,states,source_archive_sha256="c"*64)
