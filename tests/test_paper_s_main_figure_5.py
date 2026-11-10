import pandas as pd
import pytest
from energy_transition.paper_s_main_figure_5 import certify,render

SHAPES=("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")

def source():
    contrasts=[];interactions=[]
    for g in range(1,8):
      for s in SHAPES:
        for p in (.125,.25,.5):
          for e1,e2 in ((.5,1.),(1.,2.)):
            contrasts.append(dict(source_shape_group=g,synthetic_supply_shape=s,
              axis="energy_at_fixed_power",held_constant=p,from_level=e1,to_level=e2,
              added_discharge_mwh=10.,toy_objective_reduction_usd=850.))
        for e in (.5,1.,2.):
          for p1,p2 in ((.125,.25),(.25,.5)):
            contrasts.append(dict(source_shape_group=g,synthetic_supply_shape=s,
              axis="power_at_fixed_energy",held_constant=e,from_level=p1,to_level=p2,
              added_discharge_mwh=20.,toy_objective_reduction_usd=1700.))
        for p1,p2 in ((.125,.25),(.25,.5)):
          for e1,e2 in ((.5,1.),(1.,2.)):
            interactions.append(dict(source_shape_group=g,synthetic_supply_shape=s,
              low_power_peak_ratio=p1,high_power_peak_ratio=p2,
              low_energy_peak_hours=e1,high_energy_peak_hours=e2,
              energy_benefit_low_power_usd=100.,energy_benefit_high_power_usd=150.,
              mw_mwh_objective_interaction_usd=50.,
              mw_mwh_interaction_pct_of_baseline_cost=.5))
    return pd.DataFrame(contrasts),pd.DataFrame(interactions)

def test_complete_original_factorial_and_figures(tmp_path):
    a,b=source()
    counts,signs=certify(a,b)
    assert len(counts)==12 and len(signs)==3
    assert signs.positive_interactions_of_28.eq(28).all()
    meta=render(a,b,tmp_path)
    assert meta["one_axis_contrasts_used"]==252
    assert (tmp_path/"Paper_S_proposed_main_Figure_5_independent_MW_MWh.svg").stat().st_size>3000

def test_no_incomplete_archived_contrasts():
    a,b=source()
    with pytest.raises(ValueError,match="252"):certify(a.iloc[:-1],b)

def test_tampered_four_corner_cost_identity_rejected():
    a,b=source()
    b.loc[0,"mw_mwh_objective_interaction_usd"]+=100
    with pytest.raises(ValueError,match="identity"):certify(a,b)
