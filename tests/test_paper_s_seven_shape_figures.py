import pandas as pd
import pytest
from energy_transition.paper_s_seven_shape_figures import validate,plot

def data():
    return pd.DataFrame([
       {"source_shape_group":i,"state":f"State{i}","reeds_zone":f"p{i}",
        "synthetic_supply_shape":s,"discharged_4h_gwh":100.,
        "discharged_8h_gwh":110.,"incremental_discharge_4to8h_gwh":10.}
       for i in range(1,8)
       for s in ("flat_50pct","ordinal24_wave_A","ordinal24_wave_B")])

def test_source_21_rows_and_figure_binary(tmp_path):
    r=plot(data(),tmp_path)
    assert r["shape_groups"]==7
    assert (tmp_path/"Figure_S9_2030_seven_shape_relative_increment.png").stat().st_size>1000

def test_nonreconciled_marginal_rejected():
    a=data();a.loc[0,"incremental_discharge_4to8h_gwh"]+=1
    with pytest.raises(ValueError,match="Marginal discharge"):validate(a)

def test_population_missing_rejected():
    with pytest.raises(ValueError,match="21 distinct"):validate(data().iloc[:-1])
