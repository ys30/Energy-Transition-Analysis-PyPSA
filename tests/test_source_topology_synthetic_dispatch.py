"""Synthetic OPF preserves source topology without claiming calibrated injections."""
import json
import pandas as pd
import pypsa
import pytest
from energy_transition.source_topology_synthetic_dispatch import experiment


def grid(tmp_path, include_valid=True):
    n=pypsa.Network()
    n.add("Bus","2040841",v_nom=500,sub_id="38478")
    n.add("Bus","next",v_nom=500,sub_id="38479")
    n.add("Bus","different_voltage",v_nom=115,sub_id="38480")
    n.add("Line","a_line",bus0="2040841",bus1="different_voltage",x=0.2,r=0.01,s_nom=100)
    if include_valid:
        n.add("Line","b_line",bus0="2040841",bus1="next",x=0.1,r=0.01,s_nom=100)
    path=tmp_path/"network.nc"
    n.export_to_netcdf(path)
    return path


def test_synthetic_source_branch_sweep_is_a_solve_not_real_dispatch(tmp_path):
    report=experiment(grid(tmp_path),tmp_path/"test.json")
    assert report["original_source_branch_id"]=="b_line"
    assert report["source_branch_x_ohm"]==pytest.approx(0.1)
    assert report["synthetic_two_bus_opf_executed"] is True
    assert report["source_facility_identity_verified"] is False
    assert report["real_western_opf_executed"] is False
    assert [round(x["backup_dispatch_mw"]) for x in report["capacity_sweep"]]==[75,50,0]
    assert [round(x["objective_synthetic_cost_units"]) for x in report["capacity_sweep"]]==[7525,5050,100]
    assert json.loads((tmp_path/"test.json").read_text())["experimental_line_ratings"].startswith("synthetic")


def test_missing_eligible_line_rejected(tmp_path):
    with pytest.raises(ValueError,match="No eligible"):
        experiment(grid(tmp_path,include_valid=False),tmp_path/"test.json")


def test_nonexistent_anchor_rejected(tmp_path):
    with pytest.raises(ValueError,match="absent"):
        experiment(grid(tmp_path),tmp_path/"test.json",anchor="missing")


def test_nonpositive_synthetic_capacity_rejected(tmp_path):
    with pytest.raises(ValueError,match="positive"):
        experiment(grid(tmp_path),tmp_path/"test.json",ratings=(0,50))
