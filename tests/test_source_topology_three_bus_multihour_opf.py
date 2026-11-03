"""Regression checks for a traceable three-bus, three-snapshot synthetic OPF."""
import pandas as pd
import pypsa
import pytest
from energy_transition.source_topology_three_bus_multihour_opf import experiment


def source_grid(tmp_path, two_neighbors=True):
    n=pypsa.Network()
    for bus in ("2040841","a","b"):
        n.add("Bus",bus,v_nom=500)
    n.add("Line","source_a",bus0="2040841",bus1="a",r=0.1,x=0.5,s_nom=900)
    if two_neighbors:
        n.add("Line","source_b",bus0="2040841",bus1="b",r=0.3,x=0.7,s_nom=900)
    out=tmp_path/"grid.nc"
    n.export_to_netcdf(out)
    return out


def test_three_node_three_snapshot_sweep_matches_economic_optimum(tmp_path):
    res=experiment(source_grid(tmp_path),tmp_path/"out.json")
    assert res["synthetic_multinode_multiperiod_opf_executed"] is True
    assert res["real_western_opf_executed"] is False
    assert res["physical_facility_mapping_verified"] is False
    assert res["snapshots"]==3
    assert len(res["selected_source_line_ids"])==2
    assert len(res["snapshot_results"])==9
    expected={25:33650,50:19790,125:485}
    for c,objective in expected.items():
        rows=[r for r in res["snapshot_results"] if r["hypothetical_rating_mw"]==c]
        assert all(r["scenario_objective_cost_units"]==pytest.approx(objective) for r in rows)
        assert all(r["max_absolute_branch_flow_mw"]<=c+0.1 for r in rows)
    assert res["snapshot_results"][0]["analytic_low_cost_mw"]==50


def test_fails_closed_if_source_cannot_provide_two_distinct_neighbors(tmp_path):
    with pytest.raises(ValueError,match="two distinct"):
        experiment(source_grid(tmp_path,two_neighbors=False),tmp_path/"out.json")


def test_no_source_anchor_rejected(tmp_path):
    with pytest.raises(ValueError,match="Anchor absent"):
        experiment(source_grid(tmp_path),tmp_path/"out.json",anchor="no-such-bus")
