import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_soc_tiebreak import _weights,MODES,PROBES,EPS

def test_original_default_lp_unchanged_when_tiebreak_none():
    d=[10.]*8;cf=[1.]*4+[0.]*4
    a=solve_zone(d,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.)
    b=solve_zone(d,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
                 soc_tiebreak_usd_per_mwh=None)
    assert a==b

def test_perturbed_lp_is_revalued_under_unmodified_objective():
    d=[10.]*8;cf=[1.]*4+[0.]*4
    a=solve_zone(d,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.)
    b=solve_zone(d,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
                 soc_tiebreak_usd_per_mwh=_weights(8,'soc_penalty'))
    assert b["objective_illustrative_variable_usd"]>=a["objective_illustrative_variable_usd"]-.001
    assert abs(b["objective_illustrative_variable_usd"]-a["objective_illustrative_variable_usd"])<.1

def test_invalid_weight_rejected():
    with pytest.raises(ValueError,match="tiebreak"):
        solve_zone([10.,10.],[1.,0.],4,soc_tiebreak_usd_per_mwh=np.array([1e-2,1e-2]))
    with pytest.raises(ValueError,match="tiebreak"):
        solve_zone([10.,10.],[1.,0.],4,soc_tiebreak_usd_per_mwh=np.array([1e-6]))

def test_four_deterministic_probe_modes():
    assert len(PROBES)==4 and len(MODES)==4 and EPS==1e-5
