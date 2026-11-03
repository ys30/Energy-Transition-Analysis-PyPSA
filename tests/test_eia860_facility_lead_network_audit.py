"""Official facility documents cannot automatically certify real network bus injections."""
import pandas as pd
import pypsa
import pytest
from energy_transition.eia860_facility_lead_network_audit import audit


def fixtures(tmp_path):
    n=pypsa.Network()
    n.add("Bus","a",v_nom=500)
    n.add("Bus","b",v_nom=230)
    n.add("Line","l",bus0="a",bus1="b",r=0.01,x=0.1,s_nom=100)
    network=tmp_path/"grid.nc"
    n.export_to_netcdf(network)
    leads=tmp_path/"leads.csv"
    pd.DataFrame([
        dict(plant_id="6163",plant_name="Grand Coulee",source_url="https://bpa.gov/official",
             documented_voltage_kv="115;230;500",network_bus_id=None,
             independent_electrical_bus_match_verified=False),
        dict(plant_id="6008",plant_name="Palo Verde",source_url="https://energy.gov/official",
             documented_voltage_kv="500",network_bus_id=None,
             independent_electrical_bus_match_verified=False),
    ]).to_csv(leads,index=False)
    candidates=tmp_path/"candidates.csv"
    pd.DataFrame([
        dict(plant_id="6163",nearest_candidate_bus="a",distance_km=2),
        dict(plant_id="6008",nearest_candidate_bus="b",distance_km=3),
    ]).to_csv(candidates,index=False)
    return leads,candidates,network


def test_voltage_screen_never_admits_electrical_connection(tmp_path):
    leads,candidates,network=fixtures(tmp_path)
    out=tmp_path/"result.csv"
    summary=audit(leads,candidates,network,out)
    d=pd.read_csv(out).set_index("plant_id")
    assert summary["candidate_voltage_compatible"]==1
    assert summary["candidate_voltage_incompatible"]==1
    assert d.loc[6163,"candidate_connected_line_count"]==1
    assert not d.source_facility_to_original_bus_verified.any()
    assert not d.generator_injection_approved.any()


def test_preapproved_lead_is_rejected(tmp_path):
    leads,candidates,network=fixtures(tmp_path)
    d=pd.read_csv(leads)
    d.loc[0,"independent_electrical_bus_match_verified"]=True
    d.to_csv(leads,index=False)
    with pytest.raises(ValueError,match="must not assert"):
        audit(leads,candidates,network,tmp_path/"out.csv")


def test_unknown_network_bus_fails_closed(tmp_path):
    leads,candidates,network=fixtures(tmp_path)
    d=pd.read_csv(candidates)
    d.loc[0,"nearest_candidate_bus"]="nonexistent"
    d.to_csv(candidates,index=False)
    with pytest.raises(ValueError,match="absent"):
        audit(leads,candidates,network,tmp_path/"out.csv")
