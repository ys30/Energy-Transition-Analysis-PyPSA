"""Source-independent physical invariants for 168h renewable-only mechanism."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_input_only_weekly_optimal import transport,one_week,report

def test_cross_midnight_only_week_can_transfer():
    surplus=np.zeros(168);deficit=np.zeros(168)
    surplus[20:24]=100
    deficit[24:28]=100
    daily=transport(surplus,deficit,25,8,daily=True)
    weekly=transport(surplus,deficit,25,8,daily=False)
    assert daily["delivered_mwh"]==pytest.approx(0,abs=1e-8)
    assert weekly["delivered_mwh"]==pytest.approx(90,abs=1e-6)
    assert weekly["equality_residual_mwh"]<1e-5

def test_4h_and_8h_with_identical_source_and_horizon():
    load=np.full(168,100.)
    cf=np.tile(np.r_[np.ones(12),np.zeros(12)],7)
    r=one_week(load,cf,2.0,100.)
    assert r["daily_incremental_4to8_mwh"]>0
    assert r["weekly_incremental_4to8_mwh"]>0
    for d in (4,8):
        assert r[f"weekly_{d}h_delivered_mwh"]+1e-5>=r[f"daily_{d}h_delivered_mwh"]
    assert r["weekly_equality_residual_mwh"]<1e-5

def test_surplus_after_deficit_no_false_cross_day_terminal_delivery():
    load=np.full(168,100.)
    cf=np.tile(np.r_[np.zeros(12),np.ones(12)],7)
    r=one_week(load,cf,2.0,100.)
    assert r["weekly_4h_delivered_mwh"]>=0
    assert r["weekly_8h_delivered_mwh"]>=r["weekly_4h_delivered_mwh"]-1e-5
    assert r["weekly_8h_delivered_mwh"]>=r["daily_8h_delivered_mwh"]-1e-5

def test_bad_168h_inputs_fail_closed():
    with pytest.raises(ValueError):
        one_week(np.ones(167),np.ones(167),1.5,100.)
    with pytest.raises(ValueError):
        transport(np.array([-1.]*24),np.zeros(24),25,4)
    with pytest.raises(ValueError):
        transport(np.ones(24),np.ones(24),25,4)
    with pytest.raises(ValueError):
        report(pd.DataFrame(),pd.DataFrame())

def test_report_selects_120_from_1080_frozen_grid():
    from energy_transition.reeds2022_all_weather_year_720lp import WEATHER_YEARS
    from energy_transition.reeds2022_four_weather_year_siting_lp import DESIGNS
    from energy_transition.paper_s_input_only_weekly_optimal import STUDIES
    frozen=[]
    for year in WEATHER_YEARS:
        for state in ("AZ","CO","ID","WY"):
            for scheme in DESIGNS:
                for ratio in (1.0,1.5,2.0):
                    for wind_share in (.25,.5,.75):
                        frozen.append(dict(state=state,renewable_peak_ratio=ratio,
                            weather_year=year,county_weight_scheme=scheme,
                            wind_share_ac=wind_share,
                            marginal_4to8_usd_added_kwh_year=4.+year/1000.+
                                (0.2 if scheme==DESIGNS[1] else 0)))
    prior=pd.DataFrame(frozen)
    assert len(prior)==1080
    cases=[]
    for state,ratio in STUDIES:
        for year in WEATHER_YEARS:
            for scheme in DESIGNS:
                cases.append(dict(state=state,renewable_peak_ratio=ratio,
                    weather_year=year,county_weight_scheme=scheme,
                    daily_incremental_4to8_mwh=100.+year/1000.,
                    weekly_incremental_4to8_mwh=130.+year/1000.))
    assert len(cases)==120
    # The original grid has nine wind-share/ratio design points per state/year/weight.
    # Restrict to wind 50% to match this experiment's source population.
    prior=prior[prior.wind_share_ac.eq(.5)].copy()
    joined, paired, summary=report(pd.DataFrame(cases),prior)
    assert (len(joined),len(paired),len(summary))==(120,120,4)
    assert set(summary.state)=={"AZ","CO","ID","WY"}
    assert summary.weather_years.eq(15).all()
