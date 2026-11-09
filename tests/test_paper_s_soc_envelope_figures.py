import pandas as pd
import pytest
from energy_transition.paper_s_soc_envelope_figures import validate,draw

def fixture():
    rows=[]
    for group,state in ((1,"Arizona"),(7,"Wyoming")):
        for shape,p,e in (("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
                          ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.)):
            for mode,fraction in (("baseline",.35),("min",.1),("max",.7)):
                rows.append({"source_shape_group":group,"state":state,
                  "reeds_zone":f"p{group}","synthetic_supply_shape":shape,
                  "battery_power_peak_ratio":p,"battery_energy_peak_hours":e,
                  "solution":mode,"total_soc_mwh_hours":fraction*8760*100,
                  "mean_soc_fraction":fraction,"original_cost_candidate_usd":1000.,
                  "reference_original_lp_cost_usd":1000.,
                  "allowed_cost_increase_usd":1.,"candidate_cost_gap_usd":0.})
    return pd.DataFrame(rows)

def test_figure_from_24_source_certified_candidates(tmp_path):
    m=draw(fixture(),tmp_path)
    assert m["intervals"]==8
    assert (tmp_path/"Figure_S16_SOC_occupancy_cost_cap_envelopes.png").stat().st_size>1000

def test_reject_bad_original_cost():
    a=fixture()
    a.loc[0,"candidate_cost_gap_usd"]=2
    with pytest.raises(ValueError,match="cap"):validate(a)

def test_reject_inverted_extrema():
    a=fixture()
    a.loc[1,"mean_soc_fraction"]=.8
    with pytest.raises(ValueError,match="outside optimized"):validate(a)
