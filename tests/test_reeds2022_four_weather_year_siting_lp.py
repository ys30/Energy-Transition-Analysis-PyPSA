import pandas as pd
import numpy as np
import pytest
from energy_transition.reeds2022_four_weather_year_siting_lp import (
    YEARS,DESIGNS,DURATIONS,summarize
)

def fixture():
    rows=[]
    for year in YEARS:
        for state in ("AZ","CO","ID","WY"):
            for scheme in DESIGNS:
                for duration in DURATIONS:
                    obj=10000-(120 if scheme==DESIGNS[0] else 100)*duration
                    rows.append({
                       "weather_year":year,"state":state,"county_weight_scheme":scheme,
                       "battery_duration_h":duration,
                       "objective_illustrative_variable_usd":obj,
                       "storage_capacity_mwh":duration*100})
    return pd.DataFrame(rows)

def test_96_lp_grouping_into_32_duration_triplets_and_16_geography_pairs():
    data=fixture()
    p,g=summarize(data)
    assert len(data)==96 and len(p)==32 and len(g)==16
    assert set(g.weather_year)==set(YEARS)
    assert not g.spatial_weight_10usd_screen_flips.any()
    np.testing.assert_allclose(
      g.energy_annuity_hurdle_usd_kwh_year_EIA_minus_potential,-.0002)

def test_missing_duration_rejected():
    data=fixture().iloc[:-1]
    with pytest.raises(ValueError,match="Missing year/state"):
        summarize(data)

def test_monotonic_storage_cost_violation_rejected():
    data=fixture()
    data.loc[data.battery_duration_h.eq(8),"objective_illustrative_variable_usd"]+=2000
    with pytest.raises(ValueError,match="increases"):
        summarize(data)
