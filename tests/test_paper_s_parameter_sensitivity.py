import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_parameter_sensitivity import SCENARIOS, summarize

def test_default_solver_exactly_matches_explicit_baseline_parameters():
    d=np.array([5.,5.,5.,5.,5.,5.,5.,5.])
    cf=np.array([1.,1.,1.,1.,0.,0.,0.,0.])
    a=solve_zone(d,cf,4,renewable_peak_ratio=2.)
    b=solve_zone(d,cf,4,renewable_peak_ratio=2.,
                 battery_power_peak_ratio=.25,roundtrip_efficiency=.9,
                 renewable_unit_cost=5.,firm_unit_cost=90.)
    assert a==b

def test_eta_changes_optimal_delivered_energy_without_creating_energy():
    demand=np.array([10.,10.,10.,10.])
    cf=np.array([1.,1.,0.,0.])
    a=solve_zone(demand,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=1.,
                 roundtrip_efficiency=.8)
    b=solve_zone(demand,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=1.,
                 roundtrip_efficiency=.95)
    assert b["storage_discharge_to_load_mwh"]>a["storage_discharge_to_load_mwh"]
    assert abs(a["storage_terminal_soc_mwh"])<1e-7

def test_invalid_cost_or_efficiency_fails_closed():
    with pytest.raises(ValueError,match="roundtrip efficiency"):
        solve_zone([10.,10.],[1.,0.],4,roundtrip_efficiency=0)
    with pytest.raises(ValueError,match="objective coefficients"):
        solve_zone([10.,10.],[1.,0.],4,firm_unit_cost=1.)

def test_exactly_seven_predeclared_one_factor_scenarios():
    assert len(SCENARIOS)==7
    assert SCENARIOS["baseline"]==(.25,.9,90.)

def test_missing_cases_rejected():
    import pandas as pd
    with pytest.raises(ValueError,match="42 LP"):
        summarize(pd.DataFrame())
