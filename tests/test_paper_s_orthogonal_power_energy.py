import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_orthogonal_power_energy import POWERS, ENERGIES, increments

def test_baseline_explicit_capacity_reproduces_old_duration():
    load=np.array([10.,10.,10.,10.,10.,10.,10.,10.])
    cf=np.array([1.,1.,1.,1.,0.,0.,0.,0.])
    a=solve_zone(load,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=.25)
    b=solve_zone(load,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=.25,
                 storage_energy_peak_hours=1.)
    assert a==b

def test_can_change_energy_at_fixed_power():
    d=[10.]*8; cf=[1.]*4+[0.]*4
    lo=solve_zone(d,cf,4,renewable_peak_ratio=2.,
                  battery_power_peak_ratio=.5,storage_energy_peak_hours=.5)
    hi=solve_zone(d,cf,4,renewable_peak_ratio=2.,
                  battery_power_peak_ratio=.5,storage_energy_peak_hours=2.)
    assert hi["storage_power_mw"]==lo["storage_power_mw"]
    assert hi["storage_capacity_mwh"]>lo["storage_capacity_mwh"]
    assert hi["storage_discharge_to_load_mwh"]>=lo["storage_discharge_to_load_mwh"]-1e-7

def test_can_change_power_at_fixed_energy():
    d=[10.]*8;cf=[1.]*4+[0.]*4
    lo=solve_zone(d,cf,4,renewable_peak_ratio=2.,
                  battery_power_peak_ratio=.125,storage_energy_peak_hours=1.)
    hi=solve_zone(d,cf,4,renewable_peak_ratio=2.,
                  battery_power_peak_ratio=.50,storage_energy_peak_hours=1.)
    assert hi["storage_power_mw"]>lo["storage_power_mw"]
    assert hi["storage_capacity_mwh"]==lo["storage_capacity_mwh"]

def test_invalid_independent_energy_rejected():
    with pytest.raises(ValueError,match="independent battery"):
        solve_zone([1.,1.],[1.,0.],4,storage_energy_peak_hours=-1)
    with pytest.raises(ValueError,match="zero-duration"):
        solve_zone([1.,1.],[1.,0.],0,storage_energy_peak_hours=1.)

def test_factorial_grid_and_incomplete_contrast_rejected():
    assert len(POWERS)==3 and len(ENERGIES)==3
    with pytest.raises(ValueError,match="27 sized"):
        increments(pd.DataFrame())
