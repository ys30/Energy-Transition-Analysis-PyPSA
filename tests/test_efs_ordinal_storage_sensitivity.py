import numpy as np
import pandas as pd
import pytest
from energy_transition.efs_ordinal_storage_sensitivity import dispatch_zone, evaluate


def demo(hours=48):
    return pd.DataFrame([
        {"year":2030,"state":"Arizona","reeds_zone":"p1",
         "local_hour_id":h,"allocated_mw":20.+10.*np.cos(2.*np.pi*(h-1)/24.)}
        for h in range(1,hours+1)
    ])


def test_battery_conservation_no_free_terminal_energy():
    demand=np.array([10.,10.,10.,10.])
    cf=np.array([1.,1.,0.,0.])
    r=dispatch_zone(demand,cf,4,nameplate_ratio=2.,storage_power_ratio=1.)
    assert r["storage_charge_mwh"]>0
    assert r["storage_discharge_to_load_mwh"]>0
    assert r["storage_terminal_soc_mwh"]>=0
    assert r["renewable_direct_mwh"]+r["storage_discharge_to_load_mwh"]+r["firm_generation_mwh"]==pytest.approx(40.)
    assert r["renewable_direct_mwh"]+r["storage_charge_mwh"]+r["unused_renewable_mwh"]==pytest.approx(r["available_renewable_mwh"])


def test_baseline_has_no_battery_energy_and_no_soc():
    demand=np.array([10.,5.,12.])
    cf=np.array([1.,0.,1.])
    r=dispatch_zone(demand,cf,0)
    assert r["storage_charge_mwh"]==0
    assert r["storage_discharge_to_load_mwh"]==0
    assert r["storage_terminal_soc_mwh"]==0


def test_equal_source_energy_across_storage_cases():
    rows,meta=evaluate(demo(),years=(2030,),hours=48)
    assert len(rows)==9
    for shape in meta["synthetic_supply_profiles"]:
        same=[r for r in rows if r["synthetic_supply_shape"]==shape]
        assert len({round(r["demand_mwh"],6) for r in same})==1
        assert len({round(r["available_renewable_mwh"],6) for r in same})==1
        assert same[0]["battery_duration_hours"]==0
        assert same[0]["storage_charge_mwh"]==0
        assert all(r["renewable_share_to_load"]<=1.000001 for r in same)
    assert meta["Western_OPF_admitted"] is False


def test_missing_source_hour_fails():
    with pytest.raises(ValueError,match="Missing or invalid hourly"):
        evaluate(demo().iloc[:-1],years=(2030,),hours=48)


def test_duplicate_source_key_fails():
    d=demo()
    with pytest.raises(ValueError,match="Duplicate source"):
        evaluate(pd.concat([d,d.iloc[[0]]]),years=(2030,),hours=48)


def test_invalid_storage_params_fail():
    with pytest.raises(ValueError,match="Invalid storage"):
        dispatch_zone([1.,1.],[.5,.5],4,rte=1.5)
