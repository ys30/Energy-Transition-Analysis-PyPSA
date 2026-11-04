import pytest
from energy_transition.efs_pinned_geography_order_audit import audit_geography_order

BASE='''
gdf_bus = map_bus_to_region(gdf_bus, na_shape, ["full_state"])
gdf_bus = map_bus_to_region(gdf_bus, state_shape, ["state"])
gdf_bus = map_bus_to_region(gdf_bus, reeds_shape, ["reeds_zone", "reeds_ba"])
gdf_bus = map_bus_to_region(gdf_bus, county_shape, ["county"])
gdf_bus = assign_missing_state_regions(gdf_bus)
group_sums = gdf_bus.groupby("full_state")["Pd"].transform("sum")
gdf_bus["LAF_state"] = gdf_bus["Pd"] / group_sums
gdf_bus = gdf_bus.drop(columns=["full_state"])
n = add_offshore_buses(n, offshore_buses)
assign_reeds_memberships(n, snakemake.input.reeds_memberships)
n.buses.groupby("county")["reeds_state"].transform(
    lambda x: x.mode()[0]
)
'''
SHAPES='''def load_na_shapes(
    state_shape="admin_1_states_provinces_lakes"
):
    resolution="10m"
    name=state_shape
gdf_states = trim_states_to_interconnect(gdf_states, gdf_nerc, interconnect)
state_boundaries = gdf_states[["name", "country", "geometry"]]
'''

def test_pinned_gis_assignment_is_three_distinct_keys():
    r=audit_geography_order(BASE,SHAPES)
    assert r["full_state_normalization_uses_Pd"] is True
    assert r["full_state_and_exported_state_same_semantics"] is False
    assert r["reeds_state_matches_export_state_guaranteed"] is False
    assert r["original_full_state_bus_labels_recovered"] is False
    assert r["independent_efs_geographic_admission"] is False

def test_source_assignment_order_change_fails():
    altered=BASE.replace('gdf_bus = map_bus_to_region(gdf_bus, na_shape, ["full_state"])',
        'SOURCE_REPLACED').replace(
        'gdf_bus = map_bus_to_region(gdf_bus, state_shape, ["state"])',
        'gdf_bus = map_bus_to_region(gdf_bus, na_shape, ["full_state"])').replace(
        'SOURCE_REPLACED',
        'gdf_bus = map_bus_to_region(gdf_bus, state_shape, ["state"])')
    with pytest.raises(ValueError,match="order changed"):
        audit_geography_order(altered,SHAPES)

def test_state_clipping_source_change_fails():
    with pytest.raises(ValueError,match="clipped-state"):
        audit_geography_order(BASE,SHAPES.replace("trim_states_to_interconnect","no_clip"))

def test_county_mode_omission_fails():
    with pytest.raises(ValueError,match="County majority"):
        audit_geography_order(BASE.replace('n.buses.groupby("county")["reeds_state"].transform(', 'n.buses.groupby("state")["reeds_state"].transform('),SHAPES)
