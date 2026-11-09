import numpy as np
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone
from energy_transition.paper_s_soc_optimal_envelope import RELATIVE_BUDGET, MINIMUM_BUDGET_USD

def case():
    return [10.]*8,[1.]*4+[0.]*4

def test_soc_envelope_respects_original_objective_and_old_results():
    d,cf=case()
    baseline,trace=solve_zone(d,cf,4,renewable_peak_ratio=2.,
        battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,return_trace=True)
    cap=baseline["objective_illustrative_variable_usd"]+.05
    lo,lt=solve_zone(d,cf,4,renewable_peak_ratio=2.,
        battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,
        soc_extremum="min",original_cost_ceiling_usd=cap,return_trace=True)
    hi,ht=solve_zone(d,cf,4,renewable_peak_ratio=2.,
        battery_power_peak_ratio=.5,storage_energy_peak_hours=1.,
        soc_extremum="max",original_cost_ceiling_usd=cap,return_trace=True)
    assert lt.soc_end_mwh.sum()<=trace.soc_end_mwh.sum()+.01
    assert ht.soc_end_mwh.sum()+.01>=trace.soc_end_mwh.sum()
    assert lo["objective_illustrative_variable_usd"]<=cap+.02
    assert hi["objective_illustrative_variable_usd"]<=cap+.02
    assert "secondary_soc_extremum" not in baseline

def test_invalid_secondary_objective_or_missing_cost_cap_fails_closed():
    d,cf=case()
    with pytest.raises(ValueError,match="cost ceiling"):
        solve_zone(d,cf,4,soc_extremum="min")
    with pytest.raises(ValueError,match="secondary"):
        solve_zone(d,cf,4,soc_extremum="max",original_cost_ceiling_usd=100,
                   soc_tiebreak_usd_per_mwh=np.ones(8)*1e-5)
    with pytest.raises(ValueError,match="without secondary"):
        solve_zone(d,cf,4,original_cost_ceiling_usd=1e8)

def test_cost_budgets_are_explicit():
    assert RELATIVE_BUDGET==1e-9
    assert MINIMUM_BUDGET_USD==.05
