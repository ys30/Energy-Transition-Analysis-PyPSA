import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_county_ac_normalized_2030 import (
    ILR, normalized_pv_ac_cf,compare_source_basis,
)
from energy_transition.reeds2022_county_full_state_lp import HOURS
from energy_transition.reeds2022_county_storage_mix_duration_2030 import (
    RATIOS,WIND_MIX,DURATIONS,POWER_RATIOS,
)

def test_ac_pv_normalizes_once_and_only_tolerates_publisher_rounding():
    x=np.full(HOURS,.4)
    x[0]=.7463
    ac=normalized_pv_ac_cf(x)
    assert ac[1]==pytest.approx(.536)
    assert ac[0]==1.
    assert ILR==1.34
    assert ac.max()<=1.
    with pytest.raises(ValueError,match="rounding"):
        normalized_pv_ac_cf(np.full(HOURS,.9))
    with pytest.raises(ValueError,match="Invalid publisher"):
        normalized_pv_ac_cf(np.ones(HOURS-1))
    with pytest.raises(ValueError,match="Invalid PV"):
        normalized_pv_ac_cf(x,ilr=0)

def fake_matrix():
    rows=[]
    for state in ("AZ","CO","ID","WY"):
        for ratio in RATIOS:
            for share in WIND_MIX:
                for d,p in [(0,0.)]+[(d,p) for d in DURATIONS for p in POWER_RATIOS]:
                    rows.append({"state":state,"demand_model_year":2030,
                       "renewable_peak_ratio":ratio,"wind_share_installed_mw":share,
                       "battery_duration_h":d,"battery_power_peak_ratio":p,
                       "objective_illustrative_variable_usd":1000,
                       "unused_renewable_mwh":20,
                       "firm_generation_mwh":200})
    return pd.DataFrame(rows)

def test_compare_only_exact_180_cases():
    original=fake_matrix()
    new=original.copy()
    new["objective_illustrative_variable_usd"]-=100
    matched=compare_source_basis(new,original)
    assert len(matched)==180
    np.testing.assert_allclose(matched.ac_minus_legacy_variable_objective_usd,-100)
    with pytest.raises(ValueError,match="Missing"):
        compare_source_basis(new.iloc[:-1],original)
