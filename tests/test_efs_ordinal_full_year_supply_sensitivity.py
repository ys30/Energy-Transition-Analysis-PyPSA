import pandas as pd
import pytest
from energy_transition.efs_ordinal_full_year_supply_sensitivity import evaluate

def sample():
    return pd.DataFrame([
      {"year":2030,"state":"Arizona","reeds_zone":"p1","local_hour_id":h,"allocated_mw":mw}
      for h,mw in [(1,10.),(2,20.),(3,5.)]])

def test_ordinal_dispatch_conservation_and_costs():
    rows,summary=evaluate(sample(),years=(2030,),hours=3,multipliers=(0.,0.5))
    assert len(rows)==2
    assert rows[0]["illustrative_firm_dispatch_mwh"]==pytest.approx(35.)
    assert rows[0]["illustrative_variable_cost_usd"]==pytest.approx(35.*90)
    assert rows[1]["illustrative_renewable_available_mwh"]==pytest.approx(15.)
    assert rows[1]["illustrative_renewable_dispatch_mwh"]==pytest.approx(15.)
    assert rows[1]["illustrative_firm_dispatch_mwh"]==pytest.approx(20.)
    assert not summary["physical_western_opf_admitted"]
    assert not summary["utc_weather_alignment_verified"]

def test_high_renewable_availability_can_curtail():
    rows,_=evaluate(sample(),years=(2030,),hours=3,multipliers=(1.,))
    assert rows[0]["illustrative_renewable_curtailment_mwh"]==pytest.approx(5.)
    assert rows[0]["illustrative_renewable_dispatch_mwh"]==pytest.approx(25.)

def test_reject_missing_hour():
    with pytest.raises(ValueError,match="Missing or invalid"):
        evaluate(sample().iloc[:-1],years=(2030,),hours=3)

def test_reject_duplicate_hour():
    d=sample()
    with pytest.raises(ValueError,match="Duplicate"):
        evaluate(pd.concat([d,d.iloc[[0]]]),years=(2030,),hours=3)

def test_reject_negative_demand():
    d=sample()
    d.loc[0,"allocated_mw"]=-1.
    with pytest.raises(ValueError,match="Invalid source"):
        evaluate(d,years=(2030,),hours=3)
