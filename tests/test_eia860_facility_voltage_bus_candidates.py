"""Voltage-compatible local buses are research leads, not independently verified POIs."""
import pandas as pd
import pypsa
import pytest

from energy_transition.eia860_facility_voltage_bus_candidates import audit


def inputs(tmp_path):
    n=pypsa.Network()
    n.add("Bus","closest_wrong_voltage",x=-110.0,y=35.0,v_nom=69,state="AZ")
    n.add("Bus","compatible_nearby",x=-110.02,y=35.0,v_nom=500,state="AZ")
    n.add("Bus","wrong_state",x=-110.001,y=35.0,v_nom=500,state="NM")
    n.add("Bus","far",x=-112.5,y=35.0,v_nom=500,state="AZ")
    n.add("Line","line",bus0="closest_wrong_voltage",bus1="compatible_nearby",x=0.1,r=0.01,s_nom=100)
    network=tmp_path/"network.nc"
    n.export_to_netcdf(network)
    leads=tmp_path/"leads.csv"
    pd.DataFrame([{"plant_id":"100","plant_name":"Facility One",
      "documented_voltage_kv":"230;500","network_bus_id":None,
      "independent_electrical_bus_match_verified":False}]).to_csv(leads,index=False)
    candidates=tmp_path/"candidates.csv"
    pd.DataFrame([{"plant_id":"100","plant_name":"EIA Plant One","state":"AZ",
      "plant_latitude":35.0,"plant_longitude":-110.0,
      "nearest_candidate_bus":"closest_wrong_voltage"}]).to_csv(candidates,index=False)
    return leads,candidates,network


def test_nearby_voltage_compatible_bus_is_not_approved(tmp_path):
    leads,candidates,network=inputs(tmp_path)
    out=tmp_path/"screen.csv"
    report=audit(leads,candidates,network,out,radius_km=20,max_per_plant=5)
    df=pd.read_csv(out)
    assert report["voltage_compatible_geographic_candidates"]==1
    assert report["generator_injections_approved"]==0
    assert report["plant_summaries"][0]["same_state_voltage_compatible_candidates_within_radius"]==1
    assert df.iloc[0].candidate_bus_id=="compatible_nearby"
    assert df.iloc[0].plant_name=="Facility One"
    assert df.iloc[0].connected_lines==1
    assert not df.electrical_connection_verified.any()
    assert not df.approved_for_generator_injection.any()


def test_no_compatible_bus_is_valid_blocked_screen(tmp_path):
    leads,candidates,network=inputs(tmp_path)
    out=tmp_path/"none.csv"
    report=audit(leads,candidates,network,out,radius_km=0.1)
    assert report["voltage_compatible_geographic_candidates"]==0
    assert pd.read_csv(out).empty


def test_unverified_lead_claiming_bus_is_rejected(tmp_path):
    leads,candidates,network=inputs(tmp_path)
    d=pd.read_csv(leads)
    d.loc[0,"network_bus_id"]="compatible_nearby"
    d.to_csv(leads,index=False)
    with pytest.raises(ValueError,match="cannot claim"):
        audit(leads,candidates,network,tmp_path/"out.csv")
