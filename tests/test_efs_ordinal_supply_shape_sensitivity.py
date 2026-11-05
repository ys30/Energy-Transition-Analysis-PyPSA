import numpy as np
import pandas as pd
import pytest

from energy_transition.efs_ordinal_supply_shape_sensitivity import evaluate, profile


def demo():
    return pd.DataFrame([
        {"year":2030,"state":"Arizona","reeds_zone":"p1",
         "local_hour_id":h,"allocated_mw":float(20+10*np.cos(2*np.pi*(h-1)/24))}
        for h in range(1,49)
    ])


def test_each_profile_has_identical_energy_and_different_dispatch():
    rows,shapes,meta=evaluate(demo(),years=(2030,),hours=48,multipliers=(0.9,))
    assert len(rows)==3
    assert len(shapes)==3
    assert len({round(x["available_renewable_mwh"],8) for x in rows})==1
    assert len({round(x["model_unused_renewable_mwh"],4) for x in rows})>1
    assert all(abs(x["delivered_renewable_mwh"]+x["assumed_firm_generation_mwh"]-
                   x["source_demand_mwh"])<1e-8 for x in rows)
    assert not meta["source_LocalHourID_is_physical_UTC_verified"]
    assert not meta["physical_Western_OPF_admitted"]


def test_synthetic_shapes_are_bounded_and_equal_mean():
    h=np.arange(1,8761)
    for kind in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
        f=profile(h,kind)
        assert f.min()>=0. and f.max()<=1.
        assert np.mean(f)==pytest.approx(0.5,abs=1e-12)
    assert profile(h,"ordinal24_wave_A")[0]==pytest.approx(0.85)
    assert profile(h,"ordinal24_wave_B")[0]==pytest.approx(0.15)


def test_missing_hour_fails():
    with pytest.raises(ValueError,match="Incomplete ordinal"):
        evaluate(demo().iloc[:-1],years=(2030,),hours=48)


def test_duplicate_hour_fails():
    d=demo()
    with pytest.raises(ValueError,match="Duplicate source"):
        evaluate(pd.concat([d,d.iloc[[0]]]),years=(2030,),hours=48)


def test_bad_demand_fails():
    d=demo()
    d.loc[0,"allocated_mw"]=-2.
    with pytest.raises(ValueError,match="Invalid EFS"):
        evaluate(d,years=(2030,),hours=48)


def test_profile_requires_complete_cycles():
    with pytest.raises(ValueError,match="not equal mean"):
        evaluate(demo().iloc[:25],years=(2030,),hours=25,multipliers=(.5,))
