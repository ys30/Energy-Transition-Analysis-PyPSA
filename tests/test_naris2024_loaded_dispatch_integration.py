"""Regression checks for load-to-OPF integration; all generation is hypothetical."""
import json

import pandas as pd
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.naris2024_loaded_dispatch_integration import solve_loaded_network


def fixture_case(tmp_path):
    n = pypsa.Network()
    n.set_snapshots(pd.date_range("2024-01-01", periods=3, freq="h"))
    for bus in ("p8", "p9"):
        n.add("Bus", bus)
    n.add("Link", "p8_to_p9", bus0="p8", bus1="p9",
          p_nom=50, p_min_pu=0, p_max_pu=1, efficiency=1)
    n.add("Load", "demand_p8", bus="p8", p_set=[10, 20, 10])
    n.add("Load", "demand_p9", bus="p9", p_set=[100, 100, 100])
    net = tmp_path / "loads.nc"
    n.export_to_netcdf(net)
    report = {
        "source_provenance_required": False,
        "western_membership_verified": False,
        "netcdf_load_roundtrip_verified": True,
        "netcdf_topology_roundtrip_verified": True,
        "optimization_solved": False,
        "historically_calibrated": False,
        "snapshots": 3,
        "zones": 2,
        "total_load_mwh": 340.0,
    }
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report))
    return net, path, report


def test_load_solve_is_explicitly_hypothetical(tmp_path):
    net, report_path, _ = fixture_case(tmp_path)
    result = solve_loaded_network(net, report_path, synthetic_fixture=True)
    assert result["snapshots"] == 3
    assert result["zones"] == 2
    assert result["input_load_mwh"] == pytest.approx(340.0)
    assert result["optimized_generation_mwh"] == pytest.approx(340.0)
    assert result["hypothetical_backup_mwh"] > 0
    assert result["max_nodal_balance_residual_mw"] < 1e-3
    assert result["historical_calibration"] is False
    assert result["generation_costs_and_capacity_hypothetical"] is True


def test_fail_closed_on_missing_source_admission(tmp_path):
    net, report_path, _ = fixture_case(tmp_path)
    with pytest.raises(ValueError, match="Source-backed load admission"):
        solve_loaded_network(net, report_path)


def test_fail_closed_on_load_total_mismatch(tmp_path):
    net, report_path, report = fixture_case(tmp_path)
    report["total_load_mwh"] += 10.0
    report_path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match="conservation check"):
        solve_loaded_network(net, report_path, synthetic_fixture=True)


def test_fail_closed_on_existing_generators(tmp_path):
    net, report_path, _ = fixture_case(tmp_path)
    n = pypsa.Network(net)
    n.add("Generator", "existing", bus="p8", p_nom=10)
    n.export_to_netcdf(net)
    with pytest.raises(ValueError, match="preexisting supply"):
        solve_loaded_network(net, report_path, synthetic_fixture=True)
