"""Annual input-only optimization: nesting and paired annual LP source gates."""
import numpy as np,pandas as pd,pytest
from energy_transition.paper_s_input_only_annual_optimal import solve_annual,summarize
from energy_transition.paper_s_input_only_weekly_optimal import transport

def test_uneven_last_week_is_closed_at_year_end():
    surplus=np.zeros(24*15);deficit=np.zeros(24*15)
    surplus[24*12+20:24*13]=100.
    deficit[24*13:24*13+4]=100.
    daily=transport(surplus,deficit,25,8,reset_hours=24)
    weekly=transport(surplus,deficit,25,8,reset_hours=168)
    annual=transport(surplus,deficit,25,8,reset_hours=360)
    assert daily["delivered_mwh"]==pytest.approx(0,abs=1e-6)
    assert weekly["delivered_mwh"]==pytest.approx(90,abs=1e-6)
    assert annual["delivered_mwh"]==pytest.approx(90,abs=1e-6)

def test_three_horizon_nested_durations_and_residuals():
    load=np.full(8760,100.)
    cf=np.tile(np.r_[np.ones(12),np.zeros(12)],365)
    result=solve_annual(load,cf,2.)
    for duration in (4,8):
        assert result[f"annual_{duration}h_delivered_mwh"]+1e-4>=result[f"weekly_{duration}h_delivered_mwh"]
        assert result[f"weekly_{duration}h_delivered_mwh"]+1e-4>=result[f"daily_{duration}h_delivered_mwh"]
        assert result[f"annual_{duration}h_balance_residual_mwh"]<1e-5
    assert result["annual_incremental_4to8_mwh"]>=-1e-5

def test_bad_year_input_fails():
    with pytest.raises(ValueError):
        solve_annual(np.ones(8759),np.ones(8759),1.5)

def test_frozen_year_matching_does_not_multiply_siting_pairs():
    rows=[];lp=[]
    for state,ratio in [("CO",2.),("ID",1.5)]:
        for yr in (2012,2023):
            for scheme in ("source_potential_2012","eia_2025_operating_county_weight"):
                rows.append({"state":state,"renewable_peak_ratio":ratio,"weather_year":yr,
                    "county_weight_scheme":scheme,
                    **{f"{h}_incremental_4to8_mwh":3.+yr/1000. for h in ("daily","weekly","annual")}})
                for share in (.25,.5,.75):
                    lp.append({"state":state,"renewable_peak_ratio":ratio,"weather_year":yr,
                        "county_weight_scheme":scheme,"wind_share_ac":share,
                        "marginal_4to8_usd_added_kwh_year":4.+share})
    joined,pairs,summary=summarize(pd.DataFrame(rows),pd.DataFrame(lp))
    assert (len(joined),len(pairs),len(summary))==(8,4,2)
    assert summary.n_matched_weather_years.eq(2).all()
