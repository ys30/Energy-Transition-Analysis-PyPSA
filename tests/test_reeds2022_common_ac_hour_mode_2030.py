import pandas as pd
import numpy as np
import pytest
from energy_transition.reeds2022_common_ac_hour_mode_2030 import (
    summarize,STATES,RATIOS,WIND_MIX,MODES,DURATIONS
)

def matrix():
    r=[]
    for state in STATES:
        for ratio in RATIOS:
            for mix in WIND_MIX:
                for mode in MODES:
                    for duration in DURATIONS:
                        energy=duration*100 if duration else 0
                        r.append({"state":state,"renewable_peak_ratio":ratio,
                          "wind_share_installed_mw":mix,
                          "hour_approximation":mode,"battery_duration_h":duration,
                          "solver_status":"optimal","max_equality_residual_mwh":1e-10,
                          "objective_illustrative_variable_usd":10000-100*duration,
                          "storage_capacity_mwh":energy})
    return pd.DataFrame(r)

def test_exact_case_counts_and_36_hour_assumption_pairs():
    frame,pairs,diff=summarize(matrix())
    assert len(pairs)==72 and len(diff)==36
    assert len(frame)==216
    assert diff.conditional_10_hurdle_decision_changed.sum()==0
    np.testing.assert_allclose(pairs.incremental_energy_annuity_hurdle_usd_per_kwh_year,.001)

def test_missing_and_bad_monotonicity_rejected():
    with pytest.raises(ValueError,match="216"):
        summarize(matrix().iloc[:-1])
    x=matrix()
    x.loc[x.battery_duration_h.eq(8),"objective_illustrative_variable_usd"]+=100000
    with pytest.raises(ValueError,match="worsen"):
        summarize(x)

def test_nonoptimal_rejected():
    x=matrix()
    x.loc[x.index[0],"solver_status"]="failed"
    with pytest.raises(ValueError,match="convergence"):
        summarize(x)
