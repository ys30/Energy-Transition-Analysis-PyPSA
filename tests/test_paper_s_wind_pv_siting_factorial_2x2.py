"""Unit-level gates for Paper S 2×2 siting attribution (not climate attribution)."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_wind_pv_siting_factorial_2x2 import (
    attribute,value_from_durations,shape_stats,BASE,WIND,SOLAR,JOINT,HOURS,
)

def test_shapley_and_interaction_exact():
    values=[]
    for year in (2007,):
        for state in ("ID",):
            for arm,v in [(BASE,2.),(WIND,4.),(SOLAR,5.),(JOINT,10.)]:
                values.append(dict(weather_year=year,state=state,factorial_arm=arm,
                                   marginal_4to8_usd_kwh_year=v))
    with pytest.raises(ValueError,match="Incomplete 60"):
        attribute(pd.DataFrame(values))
    values=[]
    for year in range(60):
        for arm,v in [(BASE,2.),(WIND,4.),(SOLAR,5.),(JOINT,10.)]:
            values.append(dict(weather_year=year,state="ID",factorial_arm=arm,
                               marginal_4to8_usd_kwh_year=v))
    o=attribute(pd.DataFrame(values))
    assert len(o)==60
    assert np.allclose(o.wind_alone,2)
    assert np.allclose(o.pv_alone,3)
    assert np.allclose(o.wind_pv_interaction,3)
    assert np.allclose(o.wind_shapley,3.5)
    assert np.allclose(o.pv_shapley,4.5)
    assert np.allclose(o.total_eia_minus_potential,8)

def test_4to8_value_exact_and_curtailment_change():
    source=[]
    for duration,cost,cap,curtail in [(0,1200,0,80),(4,1000,2,70),(8,920,4,65)]:
        source.append(dict(weather_year=2007,state="AZ",factorial_arm=WIND,
                           battery_duration_h=duration,solver_status="optimal",
                           objective_illustrative_variable_usd=cost,
                           storage_capacity_mwh=cap,unused_renewable_mwh=curtail))
    got=value_from_durations(pd.DataFrame(source))
    assert len(got)==1
    assert abs(got.iloc[0].marginal_4to8_usd_kwh_year-.04)<1e-12
    assert got.iloc[0].delta_curtailment_8minus4_mwh==-5

def test_hourly_shape_metrics_are_finite():
    load=np.ones(HOURS)*100
    hours=np.arange(HOURS)
    wind=0.3+0.1*np.sin(2*np.pi*hours/24)
    solar=np.maximum(0,np.sin(2*np.pi*(hours%24-6)/24))
    m=shape_stats(load,wind,solar)
    assert m["mean_daily_netload_peak_to_trough_mw"]>0
    assert np.isfinite(m["combined_cf_lag24_corr"])
    assert np.isfinite(m["netload_lag24_corr"])

def test_factorial_missing_arm_is_rejected():
    vals=[]
    for year in range(60):
        for arm in (BASE,WIND,JOINT):
            vals.append(dict(weather_year=year,state="WY",factorial_arm=arm,
                             marginal_4to8_usd_kwh_year=2.))
    with pytest.raises(ValueError):
        attribute(pd.DataFrame(vals))
