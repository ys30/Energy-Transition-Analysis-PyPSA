import pandas as pd
import pytest
from energy_transition.paper_s_window_tolerance_figures import validate,draw

def source():
    rows=[]
    for group,state,zone,wide in ((1,"Arizona","p28",29352.336139),
                                   (7,"Wyoming","p24",1616.753223)):
        for label,eps,diff in (("absolute_0p05",.05,3.0),
                               ("absolute_0p20",.2,2.7),
                               ("archived_1e-9",1.803783 if group==1 else .402599,0.)):
            width=wide-diff
            rows.append({"source_shape_group":group,"state":state,"reeds_zone":zone,
              "tolerance_label":label,"allowed_extra_cost_usd":eps,
              "original_optimum_cost_usd":1e9,"baseline_window_discharge_mwh":100000.,
              "minimum_window_discharge_mwh":100000.-width/2,
              "maximum_window_discharge_mwh":100000.+width/2,
              "window_discharge_span_mwh":width,
              "minimum_schedule_cost_gap_usd":eps-.0001,
              "maximum_schedule_cost_gap_usd":eps-.0001})
    return pd.DataFrame(rows)

def test_chart_and_source_provenance(tmp_path):
    meta=draw(source(),tmp_path)
    assert meta["exact_alternate_optimality_proven"] is False
    assert (tmp_path/"Figure_S19_window_discharge_cost_tolerance.png").stat().st_size>1000

def test_discordant_source_width_rejected():
    a=source();a.loc[0,"window_discharge_span_mwh"]+=10
    with pytest.raises(ValueError,match="identity"):validate(a)

def test_incomplete_original_source_rejected():
    with pytest.raises(ValueError,match="six"):validate(source().iloc[:-1])
