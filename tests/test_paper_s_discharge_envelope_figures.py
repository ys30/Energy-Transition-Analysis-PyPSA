import pandas as pd
import pytest
from energy_transition.paper_s_discharge_envelope_figures import validate,render

def fixture():
    rows=[]
    for g,state in ((1,"Arizona"),(7,"Wyoming")):
        for shape,p,e in (("flat_50pct",.25,1.),("ordinal24_wave_A",.125,.5),
                           ("ordinal24_wave_A",.25,1.),("ordinal24_wave_B",.25,1.)):
            rows.append({"source_shape_group":g,"state":state,"reeds_zone":f"p{g}",
              "synthetic_supply_shape":shape,"battery_power_peak_ratio":p,
              "battery_energy_peak_hours":e,"baseline":1000.,"min":999.,
              "max":1001.,"width_mwh":2.})
    return pd.DataFrame(rows)

def test_original_eight_configurations_generate_both_figures(tmp_path):
    m=render(fixture(),tmp_path)
    assert m["intervals"]==8
    assert (tmp_path/"Figure_S17_discharge_envelope_relative_width.png").stat().st_size>1000

def test_reject_unreconciled_source_bounds():
    a=fixture();a.loc[0,"width_mwh"]+=20
    with pytest.raises(ValueError,match="reconcile"):validate(a)

def test_reject_wrong_case_population():
    with pytest.raises(ValueError,match="eight"):validate(fixture().iloc[:-1])
