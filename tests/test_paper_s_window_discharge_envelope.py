import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_window_discharge_envelope import WINDOWS

def test_window_discharge_min_max_with_same_original_cost_cap():
    load=[10.]*8
    cf=[1.]*4+[0.]*4
    base,bt=solve_zone(load,cf,4,renewable_peak_ratio=2.,
            storage_energy_peak_hours=1.,return_trace=True)
    window=np.array([1.,1.,0.,0.,0.,0.,0.,0.])
    cap=base["objective_illustrative_variable_usd"]+.05
    smin,lo=solve_zone(load,cf,4,renewable_peak_ratio=2.,
          storage_energy_peak_hours=1.,return_trace=True,
          discharge_extremum="min",discharge_hour_weights=window,
          original_cost_ceiling_usd=cap)
    smax,hi=solve_zone(load,cf,4,renewable_peak_ratio=2.,
          storage_energy_peak_hours=1.,return_trace=True,
          discharge_extremum="max",discharge_hour_weights=window,
          original_cost_ceiling_usd=cap)
    assert (lo.storage_discharge_to_load_mwh@window<=bt.storage_discharge_to_load_mwh@window+.02)
    assert (bt.storage_discharge_to_load_mwh@window<=hi.storage_discharge_to_load_mwh@window+.02)
    assert max(smin["objective_illustrative_variable_usd"],smax["objective_illustrative_variable_usd"])<=cap+.02

def test_invalid_selected_hour_weights_rejected():
    with pytest.raises(ValueError,match="selected discharge-hour"):
        solve_zone([10.]*8,[1.]*4+[0.]*4,4,
            discharge_extremum="min",discharge_hour_weights=np.ones(7),
            original_cost_ceiling_usd=1e6)
    with pytest.raises(ValueError,match="selected discharge-hour"):
        solve_zone([10.]*8,[1.]*4+[0.]*4,4,
            discharge_extremum="max",discharge_hour_weights=np.zeros(8),
            original_cost_ceiling_usd=1e6)

def test_windows_predeclared_and_disjoint():
    assert WINDOWS=={"early_1_168":(1,168),"middle_4001_4168":(4001,4168)}
