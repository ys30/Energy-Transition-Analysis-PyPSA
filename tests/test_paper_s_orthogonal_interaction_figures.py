import pandas as pd
import pytest
from energy_transition.paper_s_orthogonal_interaction_figures import validate,figure

def fixture():
    rows=[]
    for group in range(1,8):
      for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
        for pl,ph,el,eh in ((.125,.25,.5,1.),(.125,.25,1.,2.),
                            (.25,.5,.5,1.),(.25,.5,1.,2.)):
          rows.append({"source_shape_group":group,"state":f"State{group}",
            "reeds_zone":f"p{group}","synthetic_supply_shape":shape,
            "low_power_peak_ratio":pl,"high_power_peak_ratio":ph,
            "low_energy_peak_hours":el,"high_energy_peak_hours":eh,
            "energy_benefit_low_power_usd":100,
            "energy_benefit_high_power_usd":150,
            "mw_mwh_objective_interaction_usd":50,
            "mw_mwh_interaction_pct_of_baseline_cost":.5,
            "interaction_avoided_firm_component_usd":60,
            "interaction_avoided_unused_component_usd":-10})
    return pd.DataFrame(rows)

def test_figures_from_84_valid_interactions(tmp_path):
    d=fixture()
    r=figure(d,tmp_path)
    assert r["factor_rectangles"]==84
    assert (tmp_path/"Figure_S13_orthogonal_MW_MWh_interaction_heatmap.png").stat().st_size>1000

def test_tampered_cost_identity_rejected():
    d=fixture();d.loc[0,"interaction_avoided_firm_component_usd"]+=100
    with pytest.raises(ValueError,match="decomposition"):validate(d)

def test_missing_interaction_rejected():
    with pytest.raises(ValueError,match="84 interactions"):validate(fixture().iloc[:-1])
