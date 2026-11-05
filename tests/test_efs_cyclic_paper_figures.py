import pandas as pd
import pytest

from energy_transition.efs_cyclic_paper_figures import validate,make_figures

def data():
    return pd.DataFrame([
      {"planning_year":year,"synthetic_supply_shape":shape,"battery_duration_h":duration,
       "demand_mwh":1000.,"renewable_available_mwh":900.,
       "unused_renewable_mwh":max(0,90-duration*10),
       "firm_generation_mwh":500-duration*10,
       "storage_discharge_to_load_mwh":duration*10,
       "objective_illustrative_variable_usd":12000-duration*100}
      for year in (2030,2040,2050)
      for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")
      for duration in (0,4,8)
    ])

def test_exact_27_population_and_svg_png_manifest(tmp_path):
    r=make_figures(data(),tmp_path)
    assert r["source_scenario_rows"]==27
    assert not r["real_Western_OPF_admitted"]
    assert len(r["files"])==6
    assert all((tmp_path/f).stat().st_size>1000 for f in r["files"])

def test_duplicate_scenario_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        validate(pd.concat([data(),data().iloc[[0]]]))

def test_mismatched_supply_rejected():
    a=data()
    a.loc[0,"renewable_available_mwh"]=100.
    with pytest.raises(ValueError,match="Renewable available"):
        validate(a)

def test_increasing_firm_rejected():
    a=data()
    a.loc[1,"firm_generation_mwh"]=600.
    with pytest.raises(ValueError,match="increases firm"):
        validate(a)
