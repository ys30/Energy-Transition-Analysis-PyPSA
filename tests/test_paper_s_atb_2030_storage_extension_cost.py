"""Synthetic cost numbers test the algebra ONLY, not official ATB 2030 values."""
import numpy as np
import pandas as pd
import pytest
from energy_transition.paper_s_atb_2030_storage_extension_cost import (
    compute_costs,compare_avoided_cost,crf,
)


def sample_atb():
    rows=[]
    for scenario in ("Advanced","Moderate","Conservative"):
        for h in (4,8):
            capex=500.+h*50.
            rows.append(dict(scenario=scenario,year=2030,duration_h=h,
                capex_usd_per_kw=capex,fom_usd_per_kw_year=.04*capex,
                source_url="https://atb.nlr.gov/electricity/2025/utility-scale_battery_storage",
                source_edition="ATB2025",cost_dollar_year="2023 USD",power_basis_kw=60000.))
    return pd.DataFrame(rows)


def test_energy_not_full_system_capex():
    a=compute_costs(sample_atb(),rates=(.07,))
    assert len(a)==3
    assert np.allclose(a.delta_capex_usd_kw,200.)
    assert np.allclose(a.delta_energy_kwh_per_kw,4.)
    assert np.allclose(a.capex_increment_usd_per_added_kwh,50.)
    assert np.allclose(a.annualized_extension_hurdle_usd_kwh_year,
        50.*crf(.07,15)+2.)


def test_incorrect_mix_or_source_rejected():
    bad=sample_atb()
    bad.loc[0,"year"]=2040
    with pytest.raises(ValueError):
        compute_costs(bad)
    bad=sample_atb()
    bad.loc[0,"power_basis_kw"]=100.
    with pytest.raises(ValueError,match="power basis"):
        compute_costs(bad)
    bad=sample_atb()
    bad.loc[0,"source_url"]="https://unverified.example"
    with pytest.raises(ValueError):
        compute_costs(bad)


def test_verified_lp_vs_cost_not_profit():
    costs=compute_costs(sample_atb(),rates=(.07,))
    vals=pd.DataFrame([dict(weather_year=2012,state="AZ",
        county_weight_scheme="source_potential_2012",
        load_mode="actual_historical_level",
        annualized_marginal_4_to_8_usd_kwh_year=12.)])
    out=compare_avoided_cost(costs,vals)
    assert len(out)==3
    assert not out.cash_flow_or_market_profit_established.any()
    assert out.operating_value_exceeds_annualized_extension_hurdle.dtype==bool
