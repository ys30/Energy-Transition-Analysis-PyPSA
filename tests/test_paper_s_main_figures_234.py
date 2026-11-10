import pandas as pd
import pytest
from energy_transition.paper_s_main_figures_234 import certify,render

def original():
    annual=[];marg=[]
    for year in (2030,2040,2050):
      for shape in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B"):
        row={"planning_year":year,"synthetic_supply_shape":shape,
             "zones":20,"source_ordinal_hours_per_case":8760}
        for dur in (0,4,8):
          a={"planning_year":year,"synthetic_supply_shape":shape,"battery_duration_h":dur,
             "demand_mwh":10000.,"renewable_available_mwh":6000.,
             "unused_renewable_mwh":1000.-dur*40,
             "firm_generation_mwh":4000.-dur*100,
             "objective_illustrative_variable_usd":1e6-dur*5000}
          annual.append(a)
          for metric in ("unused_renewable_mwh","firm_generation_mwh","objective_illustrative_variable_usd"):
              row[f"{metric}_{dur}h"]=a[metric]
        for metric in ("unused_renewable_mwh","objective_illustrative_variable_usd"):
          for t,u,key in ((0,4,"0to4h"),(4,8,"4to8h")):
            row[f"{metric}_reduction_{key}"]=row[f"{metric}_{t}h"]-row[f"{metric}_{u}h"]
        marg.append(row)
    return pd.DataFrame(annual),pd.DataFrame(marg)

def test_source_cases_and_journal_figures(tmp_path):
    a,m=original()
    result=render(a,m,tmp_path)
    assert result["main_figures"]==[2,3,4]
    for no in (2,3,4):
        assert list(tmp_path.glob(f"Paper_S_proposed_main_Figure_{no}_*.png"))[0].stat().st_size>3000

def test_reject_missing_source_case():
    a,m=original()
    with pytest.raises(ValueError,match="27 original"):certify(a.iloc[:-1],m)

def test_reject_archive_disagreement():
    a,m=original()
    m.loc[0,"objective_illustrative_variable_usd_4h"]+=10
    with pytest.raises(ValueError,match="disagree"):certify(a,m)
