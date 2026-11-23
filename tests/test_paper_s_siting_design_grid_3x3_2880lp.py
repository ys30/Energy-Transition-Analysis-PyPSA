"""Fast, source-independent coverage and objective checks for Paper S 3×3 sensitivity."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_siting_design_grid_3x3_2880lp import (
    RATIOS,WIND_SHARES,WEATHER_YEARS,STATES,DESIGNS,DURATIONS,
    validate_baseline,validate_and_summarize,EXPECTED_NEW,EXPECTED_ALL
)

def fake_all():
    rows=[]
    for y in WEATHER_YEARS:
        for st in STATES:
            for scheme in DESIGNS:
                eia=scheme==DESIGNS[1]
                for ratio in RATIOS:
                    for ws in WIND_SHARES:
                        base=1e8-1e6*ratio-1e5*ws
                        # Pairwise geography effect is conditional on design point.
                        v=2+ratio+ws+(0.4*ratio-0.2*ws if eia else 0)
                        for dur in DURATIONS:
                            obj=base-(dur//4)*(v*1000*4000)
                            rows.append(dict(weather_year=y,state=st,
                               county_weight_scheme=scheme,
                               renewable_peak_ratio=ratio,wind_share_ac=ws,
                               battery_duration_h=dur,
                               storage_capacity_mwh=(4000*dur/4 if dur else 0),
                               objective_illustrative_variable_usd=obj,
                               solver_status="optimal",max_equality_residual_mwh=0.,
                               unused_renewable_mwh=100,firm_generation_mwh=200))
    return pd.DataFrame(rows)

def test_exact_design_grid_coverage_and_siting_effect():
    x=fake_all()
    assert len(x)==EXPECTED_ALL==3240
    assert len(x)-360==EXPECTED_NEW==2880
    v,p,s=validate_and_summarize(x)
    assert len(v)==1080 and len(p)==540 and len(s)==36
    assert s.weather_years.eq(15).all()
    for _,row in s.iterrows():
        expected=0.4*row.renewable_peak_ratio-0.2*row.wind_share_ac
        assert abs(row.median_siting_effect-expected)<1e-9
    assert (s.positive_weather_years==15).all()

def test_missing_design_grid_case_is_fail_closed():
    x=fake_all().iloc[1:].copy()
    with pytest.raises(ValueError,match="3240"):
        validate_and_summarize(x)

def test_frozen_trapezoid_filter_and_anchor():
    x=fake_all()
    z=x[(x.renewable_peak_ratio==1.5)&(x.wind_share_ac==.5)].copy()
    z["hour_approximation"]="trapezoid_with_first_endpoint"
    assert len(validate_baseline(z))==360
    z.loc[z.index[0],"solver_status"]="failed"
    with pytest.raises(ValueError,match="360 optimal"):
        validate_baseline(z)

def test_monotonic_cost_gate():
    x=fake_all()
    mask=(x.weather_year==2007)&(x.state=="AZ")&(x.battery_duration_h==8)&(
        x.county_weight_scheme==DESIGNS[0])&(x.renewable_peak_ratio==1.0)&(
        x.wind_share_ac==0.25)
    x.loc[mask,"objective_illustrative_variable_usd"]=1e12
    with pytest.raises(ValueError,match="monotonicity"):
        validate_and_summarize(x)
