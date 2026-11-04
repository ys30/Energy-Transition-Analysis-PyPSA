import pandas as pd
import pytest
from energy_transition.eia860_named_poi_review import enrich

def inputs():
    p=pd.DataFrame({
        "plant_id":["1","2","3"],"state":["NM","NM","CA"],"ba_code":["SWPP","PNM","CISO"],
        "nearest_candidate_bus":["b1","b1","b3"],"distance_km":[210.,170.,8.],
        "generator_count":[2,1,1],"operating_nameplate_mw":[200.,300.,100.],
        "over50km":[True,True,False],
        "electrical_connection_verified":[False]*3,
        "empirical_generator_injection_approved":[False]*3,
    })
    c=pd.DataFrame({
        "plant_id":["1","2","3"],"plant_name":["Plant A","Plant B","Plant C"],
        "state":["NM","NM","CA"],"nearest_candidate_bus":["b1","b1","b3"],
        "distance_km":[210.,170.,8.],
        "plant_latitude":[35.,36.,38.],"plant_longitude":[-107.,-108.,-120.],
        "bus_latitude":[35.2,35.2,38.2],"bus_longitude":[-106.,-106.,-120.2],
        "assignment_status":["geographic_candidate_only"]*3,
        "electrical_connection_verified":[False]*3,
    })
    return p,c

def test_official_named_plants_and_capacity_stay_unapproved():
    p,c=inputs()
    rows,clusters,r=enrich(p,c)
    assert r["distant_plant_rows"]==2
    assert r["official_names_available"]==2
    assert r["historic_distant_nameplate_mw"]==pytest.approx(500)
    assert r["highest_nameplate_bus_plant_count"]==2
    assert r["electrical_POI_documents_verified"]==0
    assert not rows.electrical_connection_verified.any()
    assert set(rows.plant_name)=={"Plant A","Plant B"}

def test_source_candidate_mismatch_fails_closed():
    p,c=inputs()
    c.loc[0,"nearest_candidate_bus"]="b55"
    with pytest.raises(ValueError,match="mismatch"):
        enrich(p,c)

def test_wrong_distance_rejected():
    p,c=inputs()
    c.loc[0,"distance_km"]=205.
    with pytest.raises(ValueError,match="distance changed"):
        enrich(p,c)

def test_promoted_real_poi_claim_rejected():
    p,c=inputs()
    c.loc[0,"electrical_connection_verified"]=True
    with pytest.raises(ValueError,match="promoted"):
        enrich(p,c)
