from energy_transition.planning_sensitivity import PERIODS, SCENARIOS

def test_reference_run_precedes_carbon_budget():
    keys=list(SCENARIOS)
    assert keys.index("reference") < keys.index("carbon_cap_50pct")
    assert SCENARIOS["carbon_cap_50pct"]["co2_cap_fraction"]==0.5
    assert all(y in PERIODS for y in (2025,2030,2035,2040))
