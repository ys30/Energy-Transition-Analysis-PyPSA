import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_cyclic_storage_lp import solve_zone,evaluate_zones

def example(hours=48):
    return pd.DataFrame([
        {"year":2030,"state":"Arizona","reeds_zone":"p1","local_hour_id":h,
         "allocated_mw":float(15+5*np.cos(2*np.pi*(h-1)/24))}
        for h in range(1,hours+1)])

def test_hiGHS_cyclic_soc_and_dispatch_conservation():
    demand=np.array([10.,10.,10.,10.])
    cf=np.array([1.,1.,0.,0.])
    no=solve_zone(demand,cf,0,renewable_peak_ratio=2.,battery_power_peak_ratio=1.)
    yes=solve_zone(demand,cf,4,renewable_peak_ratio=2.,battery_power_peak_ratio=1.)
    assert no["firm_generation_mwh"]==pytest.approx(20.)
    assert yes["firm_generation_mwh"]<20.
    assert yes["storage_terminal_soc_mwh"]==pytest.approx(0.,abs=1e-7)
    assert yes["cyclic_SOC_0_to_0_verified"]
    assert yes["objective_illustrative_variable_usd"]<no["objective_illustrative_variable_usd"]

def test_cannot_use_terminal_stored_energy_at_start():
    r=solve_zone([10.,10.,10.],[0.,0.,1.],8,
                 renewable_peak_ratio=2.,battery_power_peak_ratio=1.)
    assert r["storage_discharge_to_load_mwh"]==pytest.approx(0.,abs=1e-7)
    assert r["storage_terminal_soc_mwh"]==pytest.approx(0.,abs=1e-7)

def test_valid_sample_sixteen_cyclic_scenarios():
    rows,meta=evaluate_zones(example(),2030,48,max_zones=1)
    assert len(rows)==9
    assert all(abs(row["storage_terminal_soc_mwh"])<1e-7 for row in rows)
    assert all(row["cyclic_lp_vs_greedy_cost_directly_comparable"] for row in rows if row["battery_duration_h"]==0)
    assert not meta["real_Western_network_OPF_admitted"]
    assert not meta["physical_UTC_verified"]

def test_duplicate_source_hours_fail_closed():
    d=example()
    with pytest.raises(ValueError,match="duplicate"):
        evaluate_zones(pd.concat([d,d.iloc[[0]]]),2030,48,1)

def test_nonfinite_load_fails_closed():
    with pytest.raises(ValueError,match="Invalid"):
        solve_zone([10.,float("nan")],[0.5,0.5],0)

def test_misaligned_ordinal_input_rejected():
    with pytest.raises(ValueError,match="Incomplete"):
        evaluate_zones(example().iloc[:-1],2030,48,1)
