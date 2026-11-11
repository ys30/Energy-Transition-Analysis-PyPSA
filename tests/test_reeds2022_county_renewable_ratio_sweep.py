import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_county_renewable_ratio_sweep import (
    RATIOS,POWER_PEAK_RATIO,RT_EFFICIENCY,paired_summary,
)
from energy_transition.reeds2022_county_full_state_lp import STATES,YEARS,MODES,DURATIONS


def fake_full_matrix():
    rows=[]
    for st in STATES:
        for year in YEARS:
            for mode in MODES:
                for ratio in RATIOS:
                    for duration in DURATIONS:
                        rows.append({
                            "state":st,"demand_model_year":year,
                            "hour_approximation":mode,
                            "renewable_peak_ratio":ratio,
                            "battery_duration_h":duration,
                            "objective_illustrative_variable_usd":1000-(10 if duration else 0),
                            "firm_generation_mwh":500-(2 if duration else 0),
                            "unused_renewable_mwh":100-(5 if duration else 0),
                            "storage_discharge_to_load_mwh":2 if duration else 0,
                            "renewable_available_mwh":200,
                        })
    return pd.DataFrame(rows)


def test_exact_prespecified_matrix_and_capacity_convention():
    assert len(STATES)*len(YEARS)*len(MODES)*len(RATIOS)*len(DURATIONS)==144
    assert RATIOS==(0.9,1.5,2.0)
    assert POWER_PEAK_RATIO==.25
    assert RT_EFFICIENCY==.9


def test_exact_pairing_and_units():
    d=paired_summary(fake_full_matrix())
    assert len(d)==72
    np.testing.assert_allclose(d.savings_variable_usd,10)
    np.testing.assert_allclose(d.savings_pct_0h_cost,1)
    np.testing.assert_allclose(d.firm_displacement_mwh,2)
    np.testing.assert_allclose(d.curtailment_rate_without_storage_pct,50)


def test_missing_pairs_or_unexpected_storage_cost_failure_are_rejected():
    f=fake_full_matrix()
    with pytest.raises(ValueError,match="Missing"):
        paired_summary(f.iloc[:-1])
    f.loc[f.battery_duration_h.eq(4),"objective_illustrative_variable_usd"]=2000
    with pytest.raises(ValueError,match="monotonicity"):
        paired_summary(f)
