"""End-to-end executable synthetic dispatch report regression."""
import pytest

pypsa = pytest.importorskip("pypsa")
from energy_transition.three_zone_dispatch_report import solve_three_zone


def test_three_zone_report_numerical_acceptance():
    report = solve_three_zone()
    assert report["historically_calibrated"] is False
    assert report["solver_condition"] == "optimal"
    assert len(report["snapshots"]) == 2
    for hour in report["snapshots"]:
        assert hour["demand_mw"] == pytest.approx(70.)
        assert hour["generation_mw"]["cheap_A"] == pytest.approx(40.)
        assert hour["generation_mw"]["backup_B"] == pytest.approx(5.)
        assert hour["generation_mw"]["backup_C"] == pytest.approx(25.)
        assert hour["transfer_mw"]["A_B"] == pytest.approx(40.)
        assert hour["transfer_mw"]["B_C"] == pytest.approx(25.)
        assert hour["dispatch_cost_usd_per_hour"] == pytest.approx(2790.)
        assert max(abs(v) for v in hour["nodal_residual_mw"].values()) < 1e-5
