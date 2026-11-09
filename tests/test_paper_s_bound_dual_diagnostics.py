import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_bound_dual_diagnostics import CASES,STEP_RATIO

def test_upper_bound_dual_and_fd_on_small_nonzero_example():
    demand=np.array([10.]*4+[10.]*4)
    cf=np.array([1.]*4+[0.]*4)
    s,duals=solve_zone(demand,cf,4,renewable_peak_ratio=2.,
                       battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,
                       return_duals=True)
    assert len(duals)==8
    assert s["objective_derivative_installed_energy_usd_per_mwh"]<=1e-7
    assert s["objective_derivative_installed_power_usd_per_mw"]<=1e-7
    assert s["num_nonzero_soc_energy_duals"]<=int(duals.soc_upper_bound_active.sum())
    assert s["num_nonzero_charge_power_duals"]<=int(duals.charging_upper_bound_active.sum())
    assert s["num_nonzero_discharge_power_duals"]<=int(duals.discharging_upper_bound_active.sum())
    # Existing API is unchanged unless explicitly asking for duals.
    assert solve_zone(demand,cf,4,renewable_peak_ratio=2.,
        battery_power_peak_ratio=.5,storage_energy_peak_hours=1.)["objective_illustrative_variable_usd"]==s["objective_illustrative_variable_usd"]

def test_optional_trace_and_duals_returns_all_components():
    summary,trace,duals=solve_zone([10.]*8,[1.]*4+[0.]*4,4,
        renewable_peak_ratio=2.,battery_power_peak_ratio=.5,
        storage_energy_peak_hours=1.,return_trace=True,return_duals=True)
    assert len(trace)==len(duals)==8
    assert summary["cyclic_SOC_0_to_0_verified"]

def test_fixed_probe_set_and_step_are_explicit():
    assert len(CASES)==4
    assert STEP_RATIO==1e-4
