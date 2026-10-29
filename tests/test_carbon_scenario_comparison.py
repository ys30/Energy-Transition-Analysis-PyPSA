import pandas as pd
import pytest
from energy_transition.carbon_scenario_comparison import compare_scenarios

def valid_rows():
    return pd.DataFrame([
      {"planning_year":2040,"scenario":"reference","operational_emissions_tco2_assumed":100.,
       "objective_assumed_usd":1000.,"co2_cap_tco2":float("nan"),"load_mwh":400.,
       "unserved_mwh":0.,"new_solar_mw":20.,"new_wind_mw":30.,"new_gas_mw":0.,"solver_status":"optimal"},
      {"planning_year":2040,"scenario":"carbon_cap_50pct","operational_emissions_tco2_assumed":50.,
       "objective_assumed_usd":1200.,"co2_cap_tco2":50.,"load_mwh":400.,
       "unserved_mwh":0.,"new_solar_mw":35.,"new_wind_mw":45.,"new_gas_mw":0.,"solver_status":"optimal"}])

def test_compare_carbon_cost():
    out=compare_scenarios(valid_rows()).iloc[0]
    assert out.incremental_model_usd_per_tco2_avoided == 4.
    assert out.additional_new_solar_mw == 15.
    assert out.additional_new_wind_mw == 15.
    assert out.model_emissions_reduction_fraction == 0.5

def test_detect_violated_budget():
    df=valid_rows()
    df.loc[df.scenario.eq("carbon_cap_50pct"),"operational_emissions_tco2_assumed"]=65.
    with pytest.raises(ValueError,match="not satisfied"):
        compare_scenarios(df)
