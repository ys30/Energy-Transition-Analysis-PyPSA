"""Unit tests for cross-panel pairing; synthetic matched inputs are NOT model evidence."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_load_weather_coupling_comparison import (
    compare,REF_MODE,SCHEMES,LOAD_MODES
)
from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
from energy_transition.reeds2022_four_weather_year_siting_lp import STATES,DURATIONS


def make_panels():
    fixed=[]
    matched=[]
    for year in WEATHER_YEARS:
        for state in STATES:
            for geo,scheme in enumerate(SCHEMES):
                for h in DURATIONS:
                    idx=dict(weather_year=year,state=state,
                             county_weight_scheme=scheme,battery_duration_h=h)
                    obj=1000000.-h*1000.+geo*h*15.
                    fixed.append({**idx,"hour_approximation":REF_MODE,
                        "objective_illustrative_variable_usd":obj,
                        "demand_mwh":500000.,"storage_power_mw":100. if h else 0.,
                        "storage_capacity_mwh":h*100.})
                    for mi,mode in enumerate(LOAD_MODES):
                        matched.append({**idx,"load_mode":mode,
                            "objective_illustrative_variable_usd":obj+mi*500.-h*(mi+1)*5.,
                            "demand_mwh":400000.+mi*100000.,
                            "storage_power_mw":(110.+10*mi) if h else 0.,
                            "storage_capacity_mwh":h*(110.+10*mi)})
    return pd.DataFrame(fixed),pd.DataFrame(matched)


def test_all_720_comparisons_and_geographic_pairs():
    a,b=make_panels()
    scenarios,durations,spatial=compare(a,b)
    assert (len(scenarios),len(durations),len(spatial))==(720,240,120)
    assert scenarios.battery_power_retained.sum()<len(scenarios)
    assert durations.same_total_demand.sum()==120
    assert set(spatial.load_mode)==set(LOAD_MODES)
    assert np.isfinite(spatial.change_in_siting_effect_usd_kwh_year).all()


def test_reject_missing_and_duplicate_pair():
    a,b=make_panels()
    with pytest.raises(ValueError,match="Expected 360"):
        compare(a.iloc[:-1],b)
    with pytest.raises(ValueError,match="duplication"):
        compare(a,pd.concat([b.iloc[:-1],b.iloc[[0]]],ignore_index=True))


def test_refuse_unmatched_required_field():
    a,b=make_panels()
    with pytest.raises(ValueError,match="Missing source LP fields"):
        compare(a.drop(columns=["demand_mwh"]),b)
