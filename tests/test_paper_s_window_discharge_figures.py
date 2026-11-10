import pandas as pd
import pytest
from energy_transition.paper_s_window_discharge_figures import validate,render

def source():
    return pd.DataFrame([{"source_shape_group":g,"state":st,"reeds_zone":zone,
         "window":window,"baseline":1000.,"min":900.,"max":1100.,
         "span_mwh":200.,"relative_span_pct_of_baseline":20.}
        for g,st,zone in ((1,"Arizona","p28"),(7,"Wyoming","p24"))
        for window in ("early_1_168","middle_4001_4168")])

def test_source_four_interval_plot(tmp_path):
    m=render(source(),tmp_path)
    assert m["physical_UTC_certified"] is False
    assert (tmp_path/"Figure_S18_window_discharge_redistribution.png").stat().st_size>1000

def test_reject_tampered_interval():
    df=source();df.loc[0,"max"]+=100
    with pytest.raises(ValueError,match="reconcile"):validate(df)

def test_reject_missing_group_window():
    with pytest.raises(ValueError,match="four"):validate(source().iloc[:-1])
