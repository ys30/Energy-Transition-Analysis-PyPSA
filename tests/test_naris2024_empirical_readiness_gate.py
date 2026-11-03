"""Readiness gate cannot promote synthetic loads merely by passing HiGHS."""
import pytest
from energy_transition.naris2024_empirical_readiness_gate import evaluate


def inputs():
    optimization = {
        "solver_status": "ok", "solver_condition": "optimal",
        "zones": 35, "directional_links": 131,
        "isolated_zone_ids": ["p19"], "synthetic_fixture": True,
        "source_backed_load_report_flags_present": False,
    }
    membership = {"result_buses": 35, "directed_links": 131,
                  "invented_links": 0, "all_isolated_zones": ["p19"]}
    return optimization, membership


def test_synthetic_opf_is_not_empirical():
    op, members = inputs()
    result = evaluate(op, members)
    assert result["readiness_gates"]["synthetic_numerical_chain_passed"]
    assert not result["empirical_full_network_ready"]
    assert not result["paper_historical_grid_claim_allowed"]
    assert "real_source_loads_admitted" in result["blocked_gates"]
    assert result["isolated_zones"] == ["p19"]


def test_fake_source_flags_cannot_promote_synthetic_case():
    op, members = inputs()
    op.update(source_backed_load_report_flags_present=True,
              empirical_hourly_load_source_verified=True,
              hourly_load_source_conservation_verified=True)
    result = evaluate(op, members,
        allocation={"allocation_weights_validated": True,
                    "independent_source_verified": True},
        generation={"actual_generator_bus_mapping_verified": True,
                    "hourly_availability_verified": True,
                    "marginal_fuel_cost_verified": True,
                    "ready_for_full_real_generation_dispatch": True})
    assert not result["readiness_gates"]["real_source_loads_admitted"]
    assert not result["empirical_full_network_ready"]


@pytest.mark.parametrize("field,value,match", [
    ("zones", 34, "zone count"),
    ("directional_links", 130, "Link count"),
    ("isolated_zone_ids", [], "Isolated zone"),
    ("solver_condition", "infeasible", "optimal network"),
])
def test_mismatched_evidence_rejected(field, value, match):
    op, members = inputs()
    op[field] = value
    with pytest.raises(ValueError, match=match):
        evaluate(op, members)


def test_invented_link_rejected():
    op, members = inputs()
    members["invented_links"] = 1
    with pytest.raises(ValueError, match="Invented interface"):
        evaluate(op, members)
