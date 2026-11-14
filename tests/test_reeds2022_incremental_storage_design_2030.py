import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_incremental_storage_design_2030 import (
    incremental_design_comparisons,RATIOS,WIND_SHARES,DURATIONS,POWERS
)

def synthetic_grid():
    rows=[]
    for state in ("AZ","CO","ID","WY"):
        for ratio in RATIOS:
            for wind in WIND_SHARES:
                for duration,power in [(0,0.)]+[(d,p) for d in DURATIONS for p in POWERS]:
                    mw=100*power if duration else 0.
                    energy=mw*duration
                    rows.append({
                        "state":state,"demand_model_year":2030,
                        "renewable_peak_ratio":ratio,"wind_share_installed_mw":wind,
                        "battery_duration_h":duration,"battery_power_peak_ratio":power,
                        "objective_illustrative_variable_usd":100000-(energy*20),
                        "storage_power_mw":mw,"storage_capacity_mwh":energy,
                        "storage_discharge_to_load_mwh":energy*.8,
                        "firm_generation_mwh":1000-energy*.5,
                        "unused_renewable_mwh":1000-energy*.6,
                        "solver_status":"optimal"})
    return pd.DataFrame(rows)

def test_exact_144_incremental_comparisons():
    duration,power=incremental_design_comparisons(synthetic_grid())
    assert len(duration)==72 and len(power)==72
    np.testing.assert_allclose(duration.max_incremental_energy_annuity_usd_per_kwh_year,.02)
    np.testing.assert_allclose(power.max_incremental_power_only_annuity_usd_per_kw_year,
                               power.battery_duration_h*.02)
    assert duration.incremental_power_kw.eq(0).all()

def test_missing_scenario_rejected():
    with pytest.raises(ValueError,match="180"):
        incremental_design_comparisons(synthetic_grid().iloc[:-1])

def test_bad_storage_monotonicity_rejected():
    x=synthetic_grid()
    x.loc[(x.battery_duration_h.eq(8))&(x.battery_power_peak_ratio.eq(.25)),
          "objective_illustrative_variable_usd"]=9999999
    with pytest.raises(ValueError,match="monotonicity"):
        incremental_design_comparisons(x)

def test_power_upgrade_also_increases_energy_not_power_only():
    _,power=incremental_design_comparisons(synthetic_grid())
    np.testing.assert_allclose(power.incremental_energy_kwh,
                               power.incremental_power_kw*power.battery_duration_h)
