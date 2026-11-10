import pandas as pd
import pytest
from energy_transition.paper_s_window_outside_discharge import audit

def fixture():
    rows=[]
    for group,state,zone in ((1,"Arizona","p28"),(7,"Wyoming","p24")):
      for window,start,stop in (("early_1_168",1,168),("middle_4001_4168",4001,4168)):
        for solution,delta in (("baseline",0.),("min",-20.),("max",30.)):
          rows.append({"source_shape_group":group,"state":state,"reeds_zone":zone,
           "window":window,"first_source_hour":start,"last_source_hour":stop,
           "solution":solution,"window_discharge_mwh":100.+delta,
           "annual_discharge_mwh":10000.+delta*.01,
           "reference_optimal_cost_usd":1000000.,
           "original_cost_budget_usd":.2,"candidate_original_cost_usd":1000000.,
           "candidate_cost_gap_usd":0.,
           "max_hourly_balance_residual_mwh":0.,"terminal_soc_mwh":0.})
    return pd.DataFrame(rows)

def test_original_window_outside_identity_and_case_population():
    x=audit(fixture())
    assert len(x)==8
    assert x.window_and_outside_residual_mwh.abs().max()<1e-8
    assert (x.delta_annual_discharge_mwh.abs()<x.delta_window_discharge_mwh.abs()).all()

def test_missing_accepted_schedule_rejected():
    with pytest.raises(ValueError,match="12 original"):
        audit(fixture().iloc[:-1])

def test_original_cost_cap_violation_rejected():
    x=fixture()
    x.loc[0,"candidate_cost_gap_usd"]=3
    with pytest.raises(ValueError,match="allowance|identity"):
        audit(x)
