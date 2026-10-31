from energy_transition.pypsa_usa_bundle_role import classify_inventory

def test_auxiliary_geospatial_bundle_is_not_network():
    data={"archive":"pypsa_usa_data.zip","files":[
        {"name":"gebco/dem.tif","extension":".tif"},
        {"name":"counties/regions.shp","extension":".shp"},
        {"name":"psh/sites.gpkg","extension":".gpkg"},
        {"name":"gebco/bathy.nc","extension":".nc"}]}
    r=classify_inventory(data)
    assert r["decision"]=="inspect_upstream_build_base_network"
    assert r["geospatial_member_count"]==4
    assert r["possible_network_model_members"]==[]
    assert not r["network_model_verified"]

def test_potential_grid_source_is_not_certified():
    r=classify_inventory({"files":[{"name":"raw/grid.raw","extension":".raw"}]})
    assert r["decision"]=="manual_schema_inspection_required"
    assert not r["network_model_verified"]
