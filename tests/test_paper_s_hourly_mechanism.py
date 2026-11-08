import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone


def test_optional_hourly_trace_does_not_change_summary():
    demand=np.array([12.,12.,12.,12.,12.,12.,12.,12.])
    cf=np.array([1.,1.,1.,1.,0.,0.,0.,0.])
    baseline=solve_zone(demand,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=.8)
    summary,trace=solve_zone(demand,cf,4,renewable_peak_ratio=2.,
                             battery_power_peak_ratio=.8,return_trace=True)
    assert baseline==summary
    assert len(trace)==8
    assert abs(trace.soc_end_mwh.iloc[-1])<1e-6
    assert np.allclose(trace.soc_end_mwh-trace.soc_start_mwh,
                       np.sqrt(.9)*trace.storage_charge_input_mwh-
                       trace.storage_discharge_to_load_mwh/np.sqrt(.9),atol=1e-6)
    assert abs(trace.storage_charge_input_mwh.sum()-summary["storage_charge_input_mwh"])<1e-6


def test_zero_battery_has_no_false_active_constraints():
    summary,trace=solve_zone([10.,10.,10.],[1.,0.,1.],0,return_trace=True)
    assert not trace.charge_at_power_limit.any()
    assert not trace.discharge_at_power_limit.any()
    assert not trace.soc_at_energy_limit.any()
    assert trace.soc_end_mwh.eq(0).all()
    assert summary["storage_capacity_mwh"]==0
