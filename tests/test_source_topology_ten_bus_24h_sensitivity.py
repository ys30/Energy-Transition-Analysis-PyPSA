"""Check 24-hour synthetic transmission and renewable sensitivity benchmark."""
import json

import pypsa
import pytest
from energy_transition.source_topology_ten_bus_24h_sensitivity import experiment


def source_tree(tmp_path,count=10):
    n=pypsa.Network()
    n.add("Bus","2040841",v_nom=500)
    for i in range(1,count):
        target=f"node{i}"
        parent="2040841" if i==1 else f"node{i-1}"
        n.add("Bus",target,v_nom=500)
        n.add("Line",f"line{i:02}",bus0=parent,bus1=target,r=0.2,x=1.1,s_nom=1000)
    path=tmp_path/"grid.nc"
    n.export_to_netcdf(path)
    return path


def test_24_hour_synthetic_cases_nodal_and_solar(tmp_path):
    path=source_tree(tmp_path)
    out=tmp_path/"result.json"
    r=experiment(path,out)
    assert r["hours"]==24
    assert r["scenarios"]==6
    assert len(r["source_bus_ids"])==10
    assert len(r["source_line_ids"])==9
    assert r["all_operational_inputs_synthetic"] is True
    assert r["source_facility_to_generator_bus_verified"] is False
    assert r["real_western_opf_executed"] is False
    assert json.loads(out.read_text())["scenarios"]==6
    for case in r["hourly_cases"]:
        assert len(case["hourly"])==24
        assert len(case["per_source_line_metrics"])==9
        assert {x["source_line_id"] for x in case["per_source_line_metrics"]}==set(r["source_line_ids"])
        assert sum(x["congested_hours"] for x in case["per_source_line_metrics"])==case["congested_line_hours"]
        assert all(0<=x["congested_hours"]<=24 for x in case["per_source_line_metrics"])
        assert all(x["sum_absolute_nodal_price_spread_units_per_mwh_hours"]>=0 for x in case["per_source_line_metrics"])
        assert case["max_nodal_residual_mw"]<0.15
        assert case["daily_solar_mwh"]>=0
        assert case["daily_solar_curtailment_mwh"]>=0
        assert all(x["max_line_abs_flow_mw"]<=case["hypothetical_line_capacity_mw"]+0.15 for x in case["hourly"])
        assert all(x["solar_mw"]<=x["solar_available_mw"]+0.15 for x in case["hourly"])


def test_not_enough_same_voltage_nodes(tmp_path):
    with pytest.raises(ValueError,match="only supplied"):
        experiment(source_tree(tmp_path,count=3),tmp_path/"result.json")


def test_invalid_scenario_input_fails_closed(tmp_path):
    with pytest.raises(ValueError,match="positive line capacity"):
        experiment(source_tree(tmp_path),tmp_path/"result.json",capacities=(0.0,75.0))
