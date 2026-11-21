import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_96lp_hour_approximation_192lp import (
    MODES,YEARS,STATES,DESIGNS,DURATIONS,summarize_modes
)
def example():
    rows=[]
    for st in STATES:
        for yr in YEARS:
            for geo in DESIGNS:
                for mode in MODES:
                    for dur in DURATIONS:
                        base=120 if geo==DESIGNS[0] else 100
                        penalty=10 if mode==MODES[0] else 0
                        rows.append(dict(
                            state=st,weather_year=yr,county_weight_scheme=geo,
                            hour_approximation=mode,battery_duration_h=dur,
                            objective_illustrative_variable_usd=10000+penalty-base*dur,
                            storage_capacity_mwh=dur*100))
    return pd.DataFrame(rows)

def test_192_scenario_matching_and_no_artificial_hour_effect():
    x=example()
    p,g,obj,annual,geo=summarize_modes(x.sample(frac=1,random_state=8))
    assert len(x)==192 and len(p)==64 and len(g)==32
    assert len(obj)==96 and len(annual)==32 and len(geo)==16
    np.testing.assert_allclose(annual.annuity_hold_minus_trapezoid,0,atol=1e-12)
    assert not annual["10usd_screen_hour_approximation_flip"].any()
    assert geo.siting_delta_sign_preserved.all()
    assert geo.siting_10usd_screen_status_agrees.all()

def test_missing_one_original_hour_mode_rejected():
    with pytest.raises(ValueError,match="2 original-source 96-LP modes"):
        summarize_modes(example().iloc[:-1])

def test_mismatched_source_duration_rejected():
    x=example()
    x.loc[0,"battery_duration_h"]=8
    with pytest.raises(ValueError,match="Missing year/state|Unpaired|duration"):
        summarize_modes(x)
