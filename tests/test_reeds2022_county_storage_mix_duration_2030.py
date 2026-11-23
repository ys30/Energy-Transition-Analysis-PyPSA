import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_county_storage_mix_duration_2030 import (
    RATIOS,WIND_MIX,POWER_RATIOS,DURATIONS,build_paired_table,
)


def fake_results():
    x=[]
    for st in ("AZ","CO","ID","WY"):
        for ratio in RATIOS:
            for w in WIND_MIX:
                for duration,power in [(0,0.)]+[
                    (d,p) for d in DURATIONS for p in POWER_RATIOS]:
                    x.append({
                        "state":st,"demand_model_year":2030,
                        "renewable_peak_ratio":ratio,
                        "wind_share_installed_mw":w,
                        "battery_duration_h":duration,
                        "battery_power_peak_ratio":power,
                        "objective_illustrative_variable_usd":1000 if not duration else 900,
                        "storage_power_mw":50 if duration else 0,
                        "storage_capacity_mwh":50*duration if duration else 0,
                    })
    return pd.DataFrame(x)


def test_prespecified_count_and_annuity_hurdle_units():
    a=fake_results()
    assert len(a)==180
    pairs=build_paired_table(a)
    assert len(pairs)==144
    np.testing.assert_allclose(pairs.operating_savings_usd_per_reference_year,100)
    np.testing.assert_allclose(pairs.break_even_power_only_usd_per_kw_year,100/(50*1000))
    np.testing.assert_allclose(pairs.break_even_energy_only_usd_per_kwh_year,
        100/(pairs.storage_capacity_mwh*1000))
    np.testing.assert_allclose(
        pairs.remaining_power_annuity_usd_per_kw_year_if_energy_10,
        (100-10*pairs.battery_energy_kwh)/pairs.battery_power_kw)


def test_duplicate_or_missing_battery_rejected():
    x=fake_results()
    with pytest.raises(ValueError,match="Incomplete"):
        build_paired_table(x.iloc[:-1])
    with pytest.raises(ValueError,match="Incomplete"):
        build_paired_table(pd.concat([x,x.iloc[:1]],ignore_index=True))


def test_storage_optimum_monotonicity():
    x=fake_results()
    x.loc[x.battery_duration_h.gt(0),"objective_illustrative_variable_usd"]=1100
    with pytest.raises(ValueError,match="worsened"):
        build_paired_table(x)
