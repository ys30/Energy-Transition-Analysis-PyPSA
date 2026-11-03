"""Ten-bus synthetic-source OPF validates hourly balance, congestion and source lineage."""
import json
import pandas as pd
import pypsa
import pytest

from energy_transition.source_topology_ten_bus_six_hour_opf import experiment,select_source_tree


def make_source(tmp_path,count=10):
    n=pypsa.Network()
    n.add("Bus","2040841",v_nom=500,sub_id="38478")
    for i in range(1,count):
        name=f"other_{i}"
        n.add("Bus",name,v_nom=500,sub_id=str(40000+i))
        # Network source tree: long chain, enabling real congestion constraints.
        previous="2040841" if i==1 else f"other_{i-1}"
        n.add("Line",f"original_{i:02d}",bus0=previous,bus1=name,r=0.1,x=0.5,s_nom=999)
    path=tmp_path/"original.nc"
    n.export_to_netcdf(path)
    return path


def test_ten_bus_six_hour_opf_and_provenance(tmp_path):
    source=make_source(tmp_path)
    report=experiment(source,tmp_path/"result.json")
    assert report["source_model_bus_count"]==10
    assert report["source_model_line_count"]==9
    assert report["hour_count"]==6
    assert report["real_western_opf_executed"] is False
    assert report["actual_facility_electrical_connectivity_verified"] is False
    assert len(report["hypothetical_scenarios"])==2
    lower,higher=report["hypothetical_scenarios"]
    assert higher["total_synthetic_cost_units"]<=lower["total_synthetic_cost_units"]+0.5
    for scenario in report["hypothetical_scenarios"]:
        assert len(scenario["snapshots"])==6
        assert all(abs(row["generator_load_balance_residual_mw"])<0.1 for row in scenario["snapshots"])
        assert all(row["maximum_nodal_balance_residual_mw"]<0.15 for row in scenario["snapshots"])
        assert all(row["line_max_abs_flow_mw"]<=scenario["hypothetical_line_rating_mw"]+0.1 for row in scenario["snapshots"])
        assert all(row["renewable_mw"]<=row["renewable_available_mw"]+0.1 for row in scenario["snapshots"])
    assert json.loads((tmp_path/"result.json").read_text())["experimental_input_status"].startswith("synthetic")


def test_cannot_claim_large_tree_from_small_component(tmp_path):
    source=make_source(tmp_path,count=3)
    with pytest.raises(ValueError,match="only supplied"):
        experiment(source,tmp_path/"result.json")


def test_anchor_must_exist(tmp_path):
    source=make_source(tmp_path)
    with pytest.raises(ValueError,match="anchor bus absent"):
        select_source_tree(pypsa.Network(source),anchor="nonexistent")
