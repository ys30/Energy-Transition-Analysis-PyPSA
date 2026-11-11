import numpy as np
import pandas as pd
import pytest
from energy_transition.reeds2022_ac_cost_efficiency_2030 import (
    STATES,ROUNDTRIP_EFFICIENCIES,FIRM_COST_USD_PER_MWH,DURATIONS,pairs
)

def matrix():
    rows=[]
    for state in STATES:
        for eta in ROUNDTRIP_EFFICIENCIES:
            for cost in FIRM_COST_USD_PER_MWH:
                for duration in DURATIONS:
                    rows.append({
                       "state":state,"demand_model_year":2030,
                       "roundtrip_efficiency":eta,"firm_cost_usd_per_mwh":cost,
                       "battery_duration_h":duration,
                       "objective_illustrative_variable_usd":10000+cost*5-duration*100,
                       "storage_power_mw":10. if duration else 0.,
                       "storage_capacity_mwh":10.*duration,
                    })
    return pd.DataFrame(rows)

def test_prespecified_108_solver_scenarios_and_36_matches():
    m=matrix()
    assert len(m)==108
    x=pairs(m)
    assert len(x)==36
    np.testing.assert_allclose(x.incremental_4_to_8_hour_savings_usd,400)
    np.testing.assert_allclose(x.extra_4_to_8_hour_energy_kwh,40000)
    np.testing.assert_allclose(x.incremental_energy_annuity_hurdle_usd_per_kwh_year,.01)

def test_missing_scenario_rejected():
    with pytest.raises(ValueError,match="108"):
        pairs(matrix().iloc[:-1])

def test_duration_dominance_rejected():
    x=matrix()
    x.loc[x.battery_duration_h.eq(8),"objective_illustrative_variable_usd"]+=1000
    with pytest.raises(ValueError,match="weakly dominate"):
        pairs(x)

def test_zero_storage_cannot_depend_on_battery_efficiency():
    x=matrix()
    sel=(x.battery_duration_h.eq(0))&(x.state.eq("AZ"))&(x.roundtrip_efficiency.eq(.8))
    x.loc[sel,"objective_illustrative_variable_usd"]+=10
    with pytest.raises(ValueError,match="Zero-storage"):
        pairs(x)
