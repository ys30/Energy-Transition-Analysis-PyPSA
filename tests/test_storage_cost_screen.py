import pandas as pd
import pytest
from energy_transition.storage_cost_screen import screen,capital_recovery_factor

def test_crf_and_week_threshold_not_annualized():
    assert capital_recovery_factor(0,10)==.1
    data=pd.DataFrame([{
      "season":"winter","scenario":"observed_wind_solar_plus_assumed_residual_supply",
      "assumed_operating_savings_usd":3558000.,
      "unserved_with_battery_mwh":0.,
      "unserved_without_battery_mwh":0.}])
    result=screen(data,capex=(250.,))
    row=result.iloc[0]
    assert row.investment_usd_assumed==1_000_000_000
    assert row.annual_fixed_cost_usd_assumed>0
    assert row.break_even_equivalent_weeks_at_observed_week_savings>0
    assert not bool(row.shortage_affected)

def test_shortage_case_flagged_and_zero_weekly_savings_undefined():
    frame=pd.DataFrame([{"season":"summer","scenario":"pilot",
      "assumed_operating_savings_usd":0.,
      "unserved_with_battery_mwh":1.,
      "unserved_without_battery_mwh":2.}])
    row=screen(frame).iloc[0]
    assert pd.isna(row.break_even_equivalent_weeks_at_observed_week_savings)
    assert row.classification=="shortage_penalty_dominated_not_arbitrage"
