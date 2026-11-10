import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone

def test_original_lp_unchanged_with_no_discharge_secondary():
    d=[10.]*8; f=[1.]*4+[0.]*4
    a=solve_zone(d,f,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.)
    b=solve_zone(d,f,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
                 discharge_extremum=None)
    assert a==b

def test_discharge_extrema_with_original_cost_cap():
    d=[10.]*8;f=[1.]*4+[0.]*4
    original=solve_zone(d,f,4,renewable_peak_ratio=2.,
                        storage_energy_peak_hours=1.)
    c=original["objective_illustrative_variable_usd"]+.05
    lo=solve_zone(d,f,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
                  discharge_extremum="min",original_cost_ceiling_usd=c)
    hi=solve_zone(d,f,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
                  discharge_extremum="max",original_cost_ceiling_usd=c)
    assert lo["storage_discharge_to_load_mwh"]<=original["storage_discharge_to_load_mwh"]+.02
    assert hi["storage_discharge_to_load_mwh"]+.02>=original["storage_discharge_to_load_mwh"]
    assert lo["objective_illustrative_variable_usd"]<=c+.02
    assert hi["objective_illustrative_variable_usd"]<=c+.02

def test_invalid_secondary_combinations_are_rejected():
    with pytest.raises(ValueError,match="Only one secondary"):
        solve_zone([10.]*8,[1.]*4+[0.]*4,4,soc_extremum="min",
                   discharge_extremum="max",original_cost_ceiling_usd=1e8)
    with pytest.raises(ValueError,match="cost ceiling"):
        solve_zone([10.]*8,[1.]*4+[0.]*4,4,discharge_extremum="min")
