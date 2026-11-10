import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_throughput_penalty_sensitivity import PENALTIES,WINDOW

def test_penalty_decomposition_and_original_backward_compatibility():
    demand=np.array([10.]*12)
    cf=np.array([1.]*6+[0.]*6)
    original=solve_zone(demand,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.)
    explicit=solve_zone(demand,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
        discharge_throughput_cost_usd_per_mwh=0.)
    assert original==explicit
    for p in PENALTIES:
        x=solve_zone(demand,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
            discharge_throughput_cost_usd_per_mwh=p)
        assert np.isclose(x["objective_with_throughput_penalty_usd"],
            x["objective_illustrative_variable_usd"]+p*x["storage_discharge_to_load_mwh"])
        assert x["max_equality_residual_mwh"]<1e-5

def test_penalty_cost_cap_really_scored_on_augmented_objective():
    demand=[10.]*12; cf=[1.]*6+[0.]*6
    penalty=10.
    optimum=solve_zone(demand,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
        discharge_throughput_cost_usd_per_mwh=penalty)
    start=optimum["objective_with_throughput_penalty_usd"]
    weights=np.array([1]*4+[0]*8,dtype=float)
    for direction in ("min","max"):
        x=solve_zone(demand,cf,4,renewable_peak_ratio=2.,storage_energy_peak_hours=1.,
            discharge_throughput_cost_usd_per_mwh=penalty,discharge_extremum=direction,
            discharge_hour_weights=weights,original_cost_ceiling_usd=start+.1)
        assert x["objective_with_throughput_penalty_usd"]<=start+.12
        assert x["original_cost_ceiling_usd"]==start+.1

def test_invalid_penalty_and_zero_hour_mask():
    with pytest.raises(ValueError,match="throughput penalty"):
        solve_zone([10.]*8,[1.]*8,4,discharge_throughput_cost_usd_per_mwh=-1)
    assert WINDOW==(4001,4168)
