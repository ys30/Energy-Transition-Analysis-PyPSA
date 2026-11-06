import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_lp_objective_certification import audit

def cases():
    data=[]
    for year in (2030,2040,2050):
        for zone in range(20):
            for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
                for duration in (0,4,8):
                    charge=100. if duration else 0.
                    discharge=.9*charge
                    direct=250.;firm=350.-discharge;unused=100.-charge
                    available=direct+charge+unused
                    demand=direct+discharge+firm
                    data.append({"planning_year":year,"state":"NM","reeds_zone":f"p{zone:02}",
                       "synthetic_supply_shape":shape,"battery_duration_h":duration,
                       "demand_mwh":demand,"renewable_available_mwh":available,
                       "renewable_direct_mwh":direct,"storage_charge_input_mwh":charge,
                       "storage_discharge_to_load_mwh":discharge,"firm_generation_mwh":firm,
                       "unused_renewable_mwh":unused,
                       "objective_illustrative_variable_usd":5*(direct+charge)+90*firm,
                       "storage_terminal_soc_mwh":0.,"max_equality_residual_mwh":0.,
                       "source_hours":8760,"solver_status":"optimal"})
    return pd.DataFrame(data)

def test_independent_objective_and_90pct_battery_audit():
    r=audit(cases())
    assert r["cases"]==540
    assert r["max_cyclic_battery_90pct_balance_mwh_error"]<1e-9
    assert r["max_absolute_objective_usd_recalculation_error"]<1e-6
    assert not r["real_western_grid_optimization"]

def test_objective_wrongly_excluding_charge_rejected():
    a=cases()
    a.loc[0,"objective_illustrative_variable_usd"]-=100.
    with pytest.raises(ValueError,match="Code-objective mismatch"):
        audit(a)

def test_terminal_storage_breaks_energy_rejected():
    a=cases()
    a.loc[0,"storage_discharge_to_load_mwh"]=4.
    with pytest.raises(ValueError,match="battery energy"):
        audit(a)

def test_dropped_case_rejected():
    with pytest.raises(ValueError,match="540-case"):
        audit(cases().iloc[:-1])
