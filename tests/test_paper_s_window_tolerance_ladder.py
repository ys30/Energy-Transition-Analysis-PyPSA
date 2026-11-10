import numpy as np
import pytest
from energy_transition.paper_s_window_tolerance_ladder import ABSOLUTE_BUDGETS, WINDOW, RELATIVE_BUDGET
from energy_transition.efs_cyclic_storage_lp import solve_zone

def test_selected_window_original_lp_at_two_absolute_caps():
    demand=[10.]*8
    supply=[1.]*4+[0.]*4
    orig,trace=solve_zone(demand,supply,4,renewable_peak_ratio=2.,
          battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,return_trace=True)
    cost=orig["objective_illustrative_variable_usd"]
    weights=np.array([1.,1.,0.,0.,0.,0.,0.,0.])
    for eps in ABSOLUTE_BUDGETS:
        vals=[]
        for direction in ("min","max"):
            res,dat=solve_zone(demand,supply,4,renewable_peak_ratio=2.,
                  battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,
                  return_trace=True,discharge_extremum=direction,
                  discharge_hour_weights=weights,original_cost_ceiling_usd=cost+eps)
            assert res["objective_illustrative_variable_usd"]<=cost+eps+.02
            vals.append(float(dat.storage_discharge_to_load_mwh.to_numpy()@weights))
        base=float(trace.storage_discharge_to_load_mwh.to_numpy()@weights)
        assert vals[0]<=base+.03 and base<=vals[1]+.03

def test_predeclared_midwindow_and_cost_ladder():
    assert WINDOW==(4001,4168)
    assert ABSOLUTE_BUDGETS==(.05,.2)
    assert RELATIVE_BUDGET==1e-9
